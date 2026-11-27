#!/usr/bin/env python3
"""Read the GCD three-arm original records without the WSL machine or EDA tools."""

from argparse import ArgumentParser
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile


ARM_ORDER = ("ordinary", "boxed", "online")
PHASES = ("initial", "retry")
STA_MARKERS = {"setup_wns_ps": "SETUP_PS", "hold_wns_ps": "HOLD_PS",
               "setup_tns_ps": "TNS_PS", "hold_tns_ps": "HOLD_TNS_PS"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def check_binding(binding, archived_name, index):
    require(index[archived_name] == {key: binding[key] for key in ("bytes", "sha256")}, archived_name)


def spef_digest(data, name):
    normalized, date_lines = re.subn(rb"(?m)^\*DATE [^\r\n]*$", b"*DATE", data)
    require(date_lines == 1, f"missing or repeated SPEF date in {name}")
    return digest(normalized)


def archive_audit(archive):
    def read(name):
        return json.loads(archive.read(name))

    index = read("ORIGINALS.json")
    require(sorted(archive.namelist()) == sorted([*index, "ORIGINALS.json"]), "manifest member mismatch")
    for name, record in index.items():
        data = archive.read(name)
        require(record == {"bytes": len(data), "sha256": digest(data)}, name)

    protocol = read("run/protocol.json")
    previous = read("historical/protocol.json")
    require(protocol == read("launcher/gate.json"), "offline and live protocols differ")
    for name, binding in protocol["historical"].items():
        check_binding(binding, f"historical/{name}", index)
    for name, binding in protocol["sources"].items():
        if name != "contextlib.py":
            check_binding(binding, f"producer_sources/{name}", index)
    require(all(protocol["sources"][name]["sha256"] == binding["sha256"]
                for name, binding in previous["sources"].items()), "shared historical source fingerprint changed")
    for key in ("seed", "reference", "pool"):
        member = {"seed": "config.json", "reference": "control/receipt.json", "pool": "screened_pool_used.json"}[key]
        check_binding(protocol[key], f"seed/{member}", index)
    seed = read("seed/config.json")
    bindings = seed["bindings"]
    for group, files in (("control/files", bindings["control"]), ("screen_inputs", seed["screen_inputs"]),
                         ("tool_wrappers", {name: bindings["tools"][name] for name in ("opensta", "sec")})):
        for key, binding in files.items():
            check_binding(binding, f"seed/{group}/{key}/{PurePosixPath(binding['path']).name}", index)
    for key in ("original_sdc", "qualification_receipt"):
        binding = bindings[key]
        check_binding(binding, f"seed/{key}/{PurePosixPath(binding['path']).name}", index)
    require(all(previous[key] == protocol[key]
                for key in previous if key not in {"protocol_order", "sources", "static_check"}),
            "frozen arm conditions differ from the original ABBA")

    def physical(directory):
        receipt = read(f"{directory}/receipt.json")
        require(receipt["routed_to_completion"] and receipt["extracted_to_completion"], directory)
        for binding in receipt["artifacts"].values():
            name = PurePosixPath(binding["path"]).name
            check_binding(binding, f"{directory}/{name}", index)
        for view in ("FF", "TT", "SS"):
            log = archive.read(f"{directory}/sta_{view}.log").decode()
            for metric, marker in STA_MARKERS.items():
                values = re.findall(rf"(?m)^IBEX_{marker} ([^\n]+)$", log)
                require(len(values) == 1 and float(values[0]) == receipt["views"][view][metric],
                        f"{directory} {view} {metric}")
        drc_member = f"{directory}/unlocked_drc/full_drc.rpt"
        drc = read(f"{directory}/unlocked_drc/audit.json")
        check_binding(drc["report"], drc_member, index)
        report = archive.read(drc_member).decode()
        markers = re.findall(r"(?m)^violation type: (.+)\n\s+srcs: (.+)\n\s+bbox = (.+)$", report)
        require(len(markers) == drc["drc_markers"] and bool(markers) == bool(report.strip()), directory)
        spef_name = f"{directory}/routed.spef"
        hashes = {key: receipt["artifacts"][key]["sha256"] for key in ("odb", "def", "v")}
        hashes["spef_without_date"] = spef_digest(archive.read(spef_name), spef_name)
        return receipt, markers, hashes

    zero = read("run/preflight/zero/result.json")
    reference, zero_markers, _ = physical("run/preflight/zero/initial")
    sec = archive.read("run/preflight/zero/initial/sec.log").decode()
    require(not zero["actions"] and not zero["failures"] and not zero_markers
            and zero["endpoint"]["valid"] and zero["endpoint"]["sec_pass"]
            and re.search(r"(?m)^SEC proven=262 unproven=0 rc=0$", sec), "strict zero qualification")
    ref_hold_ps = read("seed/control/receipt.json")["views"]["TT"]["hold_wns_ps"]
    require(reference["views"]["TT"]["hold_wns_ps"] == ref_hold_ps, "zero TT hold differs from frozen TT hold")

    results = read("run/results.json")
    require(tuple(row["diagnosis_mode"] for row in results) == ARM_ORDER, "three complete cells required")
    arms = []
    last_end = float("-inf")
    for row in results:
        method, mode = row["method"], row["diagnosis_mode"]
        require(method == protocol["execution_methods"][mode], mode)
        arm = f"run/cell_{row['cell']:02d}/{method}"
        summary = read(f"{arm}/summary.json")
        progress = read(f"{arm}/progress.json")
        request, = progress["logical_requests"]
        result = read(f"{arm}/01/result.json")
        deadline = progress["deadline_raw"]
        charged = protocol["charged_screening_seconds"]
        require(summary == row["result"] and last_end <= row["outer_start_raw"]
                <= progress["start_raw"] <= request["admitted_raw"] <= request["finished_raw"]
                <= summary["stop_raw"] <= row["outer_stop_raw"] and request["finished_raw"] < deadline
                and abs(deadline - progress["start_raw"] + charged - 720) < 1e-6, f"{mode} RAW account")
        require(protocol["fixed_actions"] == result["actions"] == request["actions"], f"{mode} proposal")
        last_end = row["outer_stop_raw"]
        ledger = read(f"{arm}/subprocesses.json")
        require(all(entry["returncode"] == 0 for entry in ledger) and len(ledger) == 10 + (mode != "ordinary"),
                f"{mode} physical and diagnostic stage counts")
        preview_seconds = None
        if mode != "ordinary":
            preview = f"{arm}/diagnosis/01"
            diagnosis = read(f"{preview}/diagnosis.json")
            script = archive.read(f"{preview}/preview.tcl").decode()
            report = f"{preview}/{PurePosixPath(diagnosis['report']['path']).name}"
            check_binding(diagnosis["report"], report, index)
            require(archive.read(report) == b"" and diagnosis["marker_count"] == 0 and not diagnosis["failure"]
                    and not diagnosis["released_neighbors"] and "detailed_route " not in script
                    and ("drt::check_drc -box " in script) == (mode == "boxed"), f"{mode} empty pre-DRT report")
            preview_seconds = diagnosis["seconds"]

        phases = []
        for phase in PHASES:
            where = f"{arm}/01/{phase}"
            receipt, markers, hashes = physical(where)
            scope = read(f"{where}/routing_scope.json")
            expected_neighbors = [] if phase == "initial" else ["net242"]
            require(scope["released_neighbors"] == expected_neighbors, f"{mode} {phase} route scope")
            phases.append({"markers": markers, "physical_hashes": hashes, "area_saved_um2": receipt["area_saved"],
                           "route_rcx_seconds": receipt["operations"]["DRT_RCX"]["wall_seconds"]})
        hold_delta = receipt["views"]["TT"]["hold_wns_ps"] - ref_hold_ps
        checkpoint, = progress["checkpoints"]
        require(hold_delta < -0.001 and result["failures"] == ["TT:hold_regression"]
                and list(PHASES) == result["passes"] and not result["proof_operations"] and not checkpoint["accepted"]
                and summary["window"]["selected"] == zero["endpoint"] and summary["window"]["area_saved"] == 0.0,
                f"{mode} final gate")
        arms.append({"mode": mode, "preview_seconds": preview_seconds, "phases": phases,
                     "tt_hold_delta_ps": hold_delta, "qualified_area_saved_um2": summary["window"]["area_saved"]})

    for index_phase, phase in enumerate(PHASES):
        first = arms[0]["phases"][index_phase]
        markers, hashes = first["markers"], first["physical_hashes"]
        require(all(arm["phases"][index_phase]["physical_hashes"] == hashes
                    and arm["phases"][index_phase]["markers"] == markers for arm in arms),
                f"{phase} physical files or DRC markers differ across arms")
        require(len(markers) == (3 if phase == "initial" else 0) and
                all(marker_type == "Short" and nets == "net:net242 net:net266" and box.endswith("on Layer met1")
                    for marker_type, nets, box in markers), f"{phase} DRC marker identities")
        for cell, method in enumerate(previous["protocol_order"], 1):
            where = f"historical/cell_{cell:02d}/{method}/01/{phase}"
            old = read(f"{where}/receipt.json")
            spef_name = f"{where}/routed.spef"
            check_binding(old["artifacts"]["spef"], spef_name, index)
            require(all(old["artifacts"][key]["sha256"] == hashes[key] for key in ("odb", "def", "v"))
                    and spef_digest(archive.read(spef_name), spef_name) == hashes["spef_without_date"]
                    and archive.read(f"{where}/unlocked_drc/full_drc.rpt")
                    == archive.read(f"run/cell_01/ordinary/01/{phase}/unlocked_drc/full_drc.rpt"),
                    f"{phase} differs from historical cell {cell}")

    receipt = read("independent/v6_gcd_window_geometry.json")
    check_binding(receipt["producer"], "independent/v6_verify_gcd_same_proposal.py", index)
    geometry = receipt["window_geometry_from_def_lef"]
    check_binding(geometry["sources"]["control_def"], "seed/control/files/def/6_final.def", index)
    require(len(receipt["cells"]) == len(arms) and geometry["dbu_per_um"] == 1000, "geometry scope")
    window = geometry["inferred_windows_dbu"]["_093_"]
    for cell, arm in zip(receipt["cells"], arms):
        require(cell["mode"] == arm["mode"], "geometry arm order")
        location = cell["physical"]["initial"]
        report_path = PurePosixPath(location["geometry_sources"]["whole_block_report"]["path"])
        check_binding(location["geometry_sources"]["whole_block_report"],
                      f"run/{'/'.join(report_path.parts[-6:])}", index)
        for _, _, box in arm["phases"][0]["markers"]:
            x0, y0, x1, y1 = (int(Decimal(n) * geometry["dbu_per_um"]) for n in re.findall(r"\d+\.\d+", box))
            require(window[0] <= x0 <= x1 <= window[2] and window[1] <= y0 <= y1 <= window[3],
                    "post-route short outside the reconstructed _093_ window")
    return {"originals": len(index), "zero_sec": [262, 0], "arms": arms, "_093_window_dbu": window}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", type=Path,
                        default=Path(__file__).with_name("GCD_WINDOW_DIAGNOSIS_ORIGINALS.zip"))
    args = parser.parse_args()
    with ZipFile(args.archive) as archive:
        report = archive_audit(archive)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
