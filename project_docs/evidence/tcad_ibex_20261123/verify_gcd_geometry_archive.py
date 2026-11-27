#!/usr/bin/env python3
"""Audit the one-net GCD geometry intervention and its matched reference archive."""

from argparse import ArgumentParser
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_gcd_window_archive import STA_MARKERS, archive_audit as window_audit, check_binding, digest, require, spef_digest


def audit(archive, previous):
    def read(name):
        return json.loads(archive.read(name))

    index = read("ORIGINALS.json")
    require(sorted(archive.namelist()) == sorted([*index, "ORIGINALS.json"]), "manifest member mismatch")
    for name, binding in index.items():
        data = archive.read(name)
        require(binding == {"bytes": len(data), "sha256": digest(data)}, name)
    old = window_audit(previous)
    protocol = read("run/protocol.json")
    baseline = json.loads(previous.read("run/protocol.json"))
    common = ("seed", "reference", "original_sdc", "pool", "screen_inputs", "charged_screening_seconds",
              "fixed_actions", "fixed_ranks", "clock", "gate", "affinity", "route_threads",
              "single_pin_access", "diagnostic_threads", "maximum_logical_requests_per_cell",
              "wall_budget_seconds_including_screen")
    require(protocol == read("launcher/gate.json") and all(protocol[k] == baseline[k] for k in common)
            and protocol["protocol_order"] == ["geometry"] and protocol["initial_release_cap"] == 1,
            "matched treatment protocol")
    for name, binding in protocol["sources"].items():
        if name != "contextlib.py":
            check_binding(binding, f"producer_sources/{name}", index)

    geo_dir = "run/cell_01/online/diagnosis/01"
    geometry = read(f"{geo_dir}/geometry.json")
    log = archive.read(f"{geo_dir}/geo_bbox.log").decode()
    boxes = {row[0]: [int(coordinate) for coordinate in row[1:]] for row in
             re.findall(r"(?m)^INST (\S+) (\d+) (\d+) (\d+) (\d+)$", log)}
    require(boxes == geometry["instance_boxes_dbu"] and set(boxes) == set(protocol["static_check"]["edited_instances"])
            and "FAECO_GEO_BBOX_DONE" in log, "geometry obtained from frozen OpenDB placement")
    recorded_control = json.loads(previous.read("seed/config.json"))["bindings"]["control"]
    require(geometry["placement_source"] == recorded_control["odb"]
            and geometry["wire_source"] == recorded_control["def"], "geometry input changed")
    ranking = geometry["ranked_distance_dbu_and_net"]
    granted, = geometry["released_neighbors"]
    require(ranking == sorted(ranking) and len({net for _, net in ranking}) == len(ranking)
            and ranking[0][1] == granted and all(net not in geometry["incident_nets"] for _, net in ranking)
            and geometry["minimum_distance_ties"] == [net for distance, net in ranking if distance == ranking[0][0]],
            "geometry eligibility, ties or first release")

    row, = read("run/results.json")
    arm = "run/cell_01/online"
    summary, progress = (read(f"{arm}/{name}.json") for name in ("summary", "progress"))
    require(summary == row["result"] and row["diagnosis_mode"] == "geometry"
            and abs(progress["deadline_raw"] - progress["start_raw"] + protocol["charged_screening_seconds"]
                    - protocol["wall_budget_seconds_including_screen"]) < 1e-6, "matched wall account")
    request, = progress["logical_requests"]
    require(request["actions"] == geometry["actions"] == protocol["fixed_actions"]
            and request["admitted_raw"] <= geometry["start_raw"] < geometry["stop_raw"] <= row["outer_stop_raw"],
            "single request and charged diagnostic work")
    ledger = read(f"{arm}/subprocesses.json")
    require(sum(PurePosixPath(item["log"]).name == "geo_bbox.log" and item["returncode"] == 0 for item in ledger) == 1,
            "successful charged OpenDB bbox query")
    zero = archive.read("run/preflight/zero/initial/sec.log").decode()
    require(re.search(r"(?m)^SEC proven=262 unproven=0 rc=0$", zero), "strict zero SEC")
    zero_views = read("run/preflight/zero/initial/receipt.json")["views"]
    initial = read(f"{arm}/01/initial/routing_scope.json")
    require(initial["released_neighbors"] == [granted] and len(initial["fixed_nets"]) == 475
            and set(initial["expected_touched_nets"]) == {granted, *geometry["incident_nets"]}, "initial release scope")

    control_initial = old["arms"][0]["phases"][0]
    historical_repair = old["arms"][0]["phases"][1]
    phases = {}
    for phase in ("initial", "retry"):
        where = f"{arm}/01/{phase}"
        receipt_file = f"{where}/receipt.json"
        if receipt_file not in index:
            continue
        receipt = read(receipt_file)
        if not (receipt.get("routed_to_completion") and receipt.get("extracted_to_completion")):
            continue
        for binding in receipt["artifacts"].values():
            check_binding(binding, f"{where}/{PurePosixPath(binding['path']).name}", index)
        spef_name = f"{where}/routed.spef"
        hashes = {key: receipt["artifacts"][key]["sha256"] for key in ("odb", "def", "v")}
        hashes["spef_without_date"] = spef_digest(archive.read(spef_name), spef_name)
        metrics = {}
        for view, values in receipt["views"].items():
            log = archive.read(f"{where}/sta_{view}.log").decode()
            for key, marker in STA_MARKERS.items():
                entries = re.findall(rf"(?m)^IBEX_{marker} ([^\n]+)$", log)
                require(len(entries) == 1 and float(entries[0]) == values[key], f"{phase} {view} {key}")
            metrics[view] = values["hold_wns_ps"] - zero_views[view]["hold_wns_ps"]
        audit_file = f"{where}/unlocked_drc/audit.json"
        drc = None
        if audit_file in index:
            audit_receipt = read(audit_file)
            report = f"{where}/unlocked_drc/full_drc.rpt"
            check_binding(audit_receipt["report"], report, index)
            drc = re.findall(r"(?m)^violation type: (.+)\n\s+srcs: (.+)\n\s+bbox = (.+)$", archive.read(report).decode())
            require(len(drc) == audit_receipt["drc_markers"], f"{phase} DRC raw count")
        released = read(f"{where}/routing_scope.json")["released_neighbors"]
        require(granted in released, f"{phase} initial choice was lost")
        phases[phase] = {"released_neighbors": released, "markers": drc, "physical_hashes": hashes,
                         "matches_control_initial": hashes == control_initial["physical_hashes"],
                         "matches_historical_repair": hashes == historical_repair["physical_hashes"],
                         "hold_delta_ps": metrics, "route_rcx_seconds": receipt["operations"]["DRT_RCX"]["wall_seconds"]}

    if summary["logical_finished"]:
        require(request["finished_raw"] < progress["deadline_raw"], "finished outside the charged window")
        result = read(f"{arm}/01/result.json")
        require(request["failures"] == result["failures"], "terminal gate result differs from ledger")
    else:
        require(summary["stop_reason"] == "end_to_end_wall_cap" and not progress["checkpoints"], "censoring status")
    require(phases["initial"]["markers"] == [tuple(marker) for marker in control_initial["markers"]]
            and phases["retry"]["markers"] == [] and summary["logical_finished"] == 1
            and summary["route_tools"] == summary["unlocked_drc_tools"] == 2
            and summary["sta_tools"] == 6 and summary["sec_tools"] == 0
            and request["failures"] == ["TT:hold_regression"] and summary["window"]["area_saved"] == 0.0,
            "geometry result and matched first-pass markers")
    known_protocol = read("known_run/protocol.json")
    require(all(known_protocol[k] == baseline[k] for k in common)
            and known_protocol["protocol_order"] == ["known_neighbor"] and known_protocol["initial_release_cap"] == 1,
            "matched known-neighbor protocol")
    for name, binding in known_protocol["sources"].items():
        if name != "contextlib.py":
            check_binding(binding, f"producer_sources/{name}", index)
    check_binding(known_protocol["release_source"], "historical_release/retry_decision.json", index)
    old_choice, = read("historical_release/retry_decision.json")["released_neighbors"]
    known_arm = "known_run/cell_01/online"
    known_choice = read(f"{known_arm}/diagnosis/01/known_neighbor.json")
    known_row, = read("known_run/results.json")
    known_summary = read(f"{known_arm}/summary.json")
    known_result = read(f"{known_arm}/01/result.json")
    require(known_choice["actions"] == protocol["fixed_actions"] and known_choice["released_neighbors"] == [old_choice]
            and known_row["result"] == known_summary and known_summary["logical_finished"] == 1
            and known_summary["route_tools"] == known_summary["unlocked_drc_tools"] == 1
            and known_summary["sta_tools"] == 3 and known_summary["sec_tools"] == 0
            and known_result["passes"] == ["initial"] and known_result["failures"] == ["TT:hold_regression"],
            "known-neighbor result and absence of retry")
    physical_dir = f"{known_arm}/01/initial"
    physical = read(f"{physical_dir}/receipt.json")
    scope = read(f"{physical_dir}/routing_scope.json")
    require(scope["released_neighbors"] == [old_choice] and len(scope["fixed_nets"]) == 475,
            "one known neighbor released")
    for binding in physical["artifacts"].values():
        check_binding(binding, f"{physical_dir}/{PurePosixPath(binding['path']).name}", index)
    known_geo = {key: physical["artifacts"][key]["sha256"] for key in ("odb", "def", "v")}
    spef_name = f"{physical_dir}/routed.spef"
    known_geo["spef_without_date"] = spef_digest(archive.read(spef_name), spef_name)
    old_path = "run/cell_01/ordinary/01/retry"
    old_receipt = json.loads(previous.read(f"{old_path}/receipt.json"))
    new_dir_key = str(PurePosixPath(physical["artifacts"]["odb"]["path"]).parent)
    old_dir_key = str(PurePosixPath(old_receipt["artifacts"]["odb"]["path"]).parent)
    require(known_geo == historical_repair["physical_hashes"] and physical["views"] == old_receipt["views"]
            and archive.read(f"{physical_dir}/route.tcl").replace(new_dir_key.encode(), old_dir_key.encode())
            == previous.read(f"{old_path}/route.tcl")
            and archive.read(f"{physical_dir}/unlocked_drc/full_drc.rpt") == b""
            and known_summary["window"]["area_saved"] == 0.0, "known initial endpoint must match the historical retry")
    known_zero = read("known_run/preflight/zero/initial/receipt.json")
    known_sec = archive.read("known_run/preflight/zero/initial/sec.log")
    known_progress = read(f"{known_arm}/progress.json")
    known_request, = known_progress["logical_requests"]
    require(known_zero["views"] == zero_views and b"SEC proven=262 unproven=0 rc=0" in known_sec
            and known_request["finished_raw"] < known_progress["deadline_raw"]
            and known_request["failures"] == known_result["failures"], "known-neighbor reference and RAW gate")
    for view, metrics in physical["views"].items():
        log = archive.read(f"{physical_dir}/sta_{view}.log").decode()
        for key, marker in STA_MARKERS.items():
            entries = re.findall(rf"(?m)^IBEX_{marker} ([^\n]+)$", log)
            require(len(entries) == 1 and float(entries[0]) == metrics[key], f"known-neighbor {view} {key}")
    known_hold = physical["views"]["TT"]["hold_wns_ps"] - known_zero["views"]["TT"]["hold_wns_ps"]
    require(known_hold == phases["retry"]["hold_delta_ps"]["TT"] < 0, "matched relative TT Hold loss")
    historical_choice = next(i for i, (_, net) in enumerate(ranking, 1) if net == old_choice)
    return {"originals": len(index), "eligible_nets": len(ranking), "initial_release": granted,
            "minimum_distance_ties": geometry["minimum_distance_ties"], "historical_release_rank": historical_choice,
            "qualified_area_saved_um2": summary["window"]["area_saved"], "stop_reason": summary["stop_reason"],
            "request": request, "phases": phases,
            "known_neighbor": {"released_neighbors": [old_choice], "initial_markers": 0, "initial_physical_passes": 1,
                               "tt_hold_delta_ps": known_hold, "qualified_area_saved_um2": 0.0,
                               "route_rcx_seconds": physical["operations"]["DRT_RCX"]["wall_seconds"]}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", type=Path, default=HERE / "GCD_GEOMETRY_RELEASE_ORIGINALS.zip")
    parser.add_argument("baseline", nargs="?", type=Path, default=HERE / "GCD_WINDOW_DIAGNOSIS_ORIGINALS.zip")
    args = parser.parse_args()
    with ZipFile(args.archive) as archive, ZipFile(args.baseline) as previous:
        print(json.dumps(audit(archive, previous), indent=2))


if __name__ == "__main__":
    main()
