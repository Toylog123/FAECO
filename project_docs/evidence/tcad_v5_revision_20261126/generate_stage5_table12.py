#!/usr/bin/env python3
"""Generate the 40 ns processor table from the SEC-fixed replay ZIPs."""

import argparse
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path, PurePosixPath
import sys
from zipfile import ZipFile

import verify_stage5_sec_fixed_replay as fixed


EVIDENCE = Path(__file__).resolve().parent
REBUILT = "V5_STAGE5_ISOLATED_REBUILD_ORIGINALS.zip"
REBUILT_SHA = "8941e1fde843880a3c701f1114a0b4ac48633080e4c42ead49e74e0ff656891e"
COMMON_AREA = 23.7728
ADAPTIVE_AREA = 31.2800
AREA_TOLERANCE = 1e-8
POWER_KEYS = (("total", "Total", "total"), ("combinational", "Combinational", "total"),
              ("leakage", "Total", "leakage"))
WARNING = "[WARNING STA-2402] power activity propagation through registers did not converge after 50 passes."


def fingerprint(path, content):
    return {"path": str(path), "bytes": len(content), "sha256": sha256(content).hexdigest()}


def power_report(read, path, odb, spef, sdc, libs):
    script_path = path.with_suffix(".tcl")
    script = read(str(script_path))
    expected = [*(f"read_liberty {json.dumps(item)}" for item in libs),
                f"read_db {json.dumps(odb)}", f"read_sdc {json.dumps(sdc)}", f"read_spef {json.dumps(spef)}",
                f"report_power -digits 9 -format json > {json.dumps(str(path))}", "puts PWR_OK", "exit"]
    if script.decode().splitlines() != expected:
        raise ValueError(f"Unexpected TT power inputs or activities in {script_path}")
    raw = read(str(path))
    prefix, data = raw.decode().split("{", 1)
    power = json.loads("{" + data)
    warnings = [line for line in prefix.splitlines() if line]
    watts = {name: power[group][item] for name, group, item in POWER_KEYS}
    if warnings != [WARNING] or not all(math.isfinite(value) and value > 0 for value in watts.values()):
        raise ValueError(f"Unexpected TT power values or propagation status in {path}")
    return power, {"values_w": watts, "activity_warning": warnings[0],
                   "raw_report": fingerprint(path, raw), "tcl": fingerprint(script_path, script)}


def threshold_endpoint(accepted, threshold):
    return next(row for row in accepted if row["area_saved_um2"] + AREA_TOLERANCE >= threshold)


def accepted_trace(audit, read, arm, audited, base_area, window):
    progress = fixed.bound_json(audit, read, arm["progress"])
    accepted = []
    for request_id, item in zip(audited["accepted"], arm["accepted_checkpoints"], strict=True):
        request = progress["logical_requests"][request_id - 1]
        point = progress["checkpoints"][request_id - 1]
        physical = fixed.bound_json(audit, read, item["physical"])
        sec = fixed.bound_json(audit, read, item["sec"])
        area = base_area - point["endpoint"]["area"]
        audit.require(point["accepted"] and point["endpoint"]["valid"] and point["endpoint"]["sec_pass"]
                      and len(request["actions"]) == item["gates"] and request["actions"] == item["actions"]
                      and point["elapsed_seconds"] == item["elapsed_s"] <= window
                      and math.isclose(area, item["area_saved_um2"], rel_tol=0, abs_tol=AREA_TOLERANCE)
                      and sec["command"][1] == "--foreground", (request_id, "invalid delivered checkpoint"))
        files = physical["artifacts"]
        accepted.append({
            "request_id": request_id,
            "actions": request["actions"],
            "action_count": len(request["actions"]),
            "charged_elapsed_s": point["elapsed_seconds"],
            "area_saved_um2": area,
            "endpoint_area_um2": point["endpoint"]["area"],
            "receipt": item["receipt"],
            "physical_receipt": item["physical"],
            "physical_hashes": {key: files[key]["sha256"] for key in ("odb", "def", "v")}
            | {"spef_without_date": audit.spef_without_date(read, files["spef"])},
        })
    times = [row["charged_elapsed_s"] for row in accepted]
    gains = [row["area_saved_um2"] for row in accepted]
    widths = [right - left for left, right in zip(times, [*times[1:], window], strict=True)]
    auc = math.fsum(gain * width for gain, width in zip(gains, widths, strict=True)) / window
    audit.require(times == sorted(set(times)) and gains == sorted(set(gains))
                  and math.isclose(auc, arm["anytime_auc_um2"], rel_tol=0, abs_tol=1e-9)
                  and math.isclose(auc, audited["auc"], rel_tol=0, abs_tol=1e-9), "AUC accounting")
    return progress, accepted, auc


def check_reference_bytes(audit, evidence, control):
    path = evidence / REBUILT
    with path.open("rb") as raw:
        audit.require(file_digest(raw, "sha256").hexdigest() == REBUILT_SHA, "rebuilt reference archive changed")
    with ZipFile(path) as archive:
        for kind in ("odb", "spef", "sdc"):
            item = control[kind]
            content = archive.read(f"rebuild/physical/6_final.{kind}")
            audit.require(fingerprint(item["path"], content) == item,
                          (kind, "reference power artifact does not match rebuilt bytes"))


def table_data(evidence):
    audit = fixed.published_verifier(evidence)
    with ExitStack() as stack:
        archives = [fixed.pinned_bundle(audit, stack, evidence / name, digest)
                    for name, digest in fixed.FIXED_ARCHIVES.items()]
        # Earlier bundles are the content store for byte-identical physical aliases.
        alias_store = {name: fixed.pinned_bundle(audit, stack, evidence / name, digest)
                       for name, digest in audit.ONLINE_ARCHIVES.items()}
        read = fixed.fixed_reader(audit, fixed.V2_ROOT, archives, alias_store)
        state_path = fixed.V2_ROOT / fixed.STATE
        state_raw = read(str(state_path))
        state = json.loads(state_raw)
        audit.require(state["status"] == "finished" and tuple(state["arms"]) == fixed.ARMS,
                      "expected all three finished SEC-fixed arms")
        protocol, audited = audit.checks(state, read, live_trials=True, verify_accept_artifacts=True)
        fixed.strict_zero(audit, read, state, foreground=True)
        qualification = fixed.bound_json(audit, read, state["qualification"])
        reference = qualification["control_output_paths"]
        check_reference_bytes(audit, evidence, reference)
        seed = fixed.bound_json(audit, read, protocol["seed"])
        libs = [item["path"] for item in seed["bindings"]["used_libraries"]["TT"]]
        sdc = reference["sdc"]["path"]
        audit.require(seed["bindings"]["used_libraries"]["TT"] == qualification["view_liberty_groups"]["TT"]
                      and libs == qualification["library_paths"]["TT"], "reference TT Liberty changed")
        reference_report = fixed.V2_ROOT / "reference_power/attempt_01/reference_power.json"
        ref_power, measured_reference = power_report(read, reference_report, reference["odb"]["path"],
                                                     reference["spef"]["path"], sdc, libs)
        audit.require(ref_power == fixed.bound_json(audit, read, state["reference_power"]), "reference power mismatch")
        screening = fixed.bound_json(audit, read, protocol["screen_input"]["receipt"])
        screen_s = protocol["charged_screening_seconds_per_arm"]
        audit.require(screening["wall_seconds"] == screen_s, "screening charge differs from raw receipt")

        base = state["reference"]["area"]
        window = protocol["wall_window_seconds_including_screen"]
        output = {}
        for label, arm in state["arms"].items():
            progress, trace, auc = accepted_trace(audit, read, arm, audited[label], base, window)
            requests = progress["logical_requests"]
            final = trace[-1]
            method_path = PurePosixPath(arm["progress"]["path"]).parent
            physical = fixed.bound_json(audit, read, final["physical_receipt"])
            files = physical["artifacts"]
            _, measured = power_report(read, method_path.parent / "best_pwr_power.json", files["odb"]["path"],
                                       files["spef"]["path"], sdc, libs)
            ref_watts = measured_reference["values_w"]
            deltas = {kind: 100.0 * (watts - ref_watts[kind]) / ref_watts[kind]
                      for kind, watts in measured["values_w"].items()}
            audit.require(all(math.isclose(value, arm["power_delta_pct"][f"{key}_pct"], rel_tol=0, abs_tol=1e-12)
                              for key, value in deltas.items()), (label, "TT power deltas disagree with raw reports"))
            tools = fixed.bound_json(audit, read, arm["tool_ledger"])
            rank_path = method_path / "sensitivity/ranking.json"
            rank_raw = read(str(rank_path))
            rank = json.loads(rank_raw)
            prep = rank["preparation"]
            audit.require(rank["ordered_action_ids"] == state["rank_order"] and rank["view"] == "TT"
                          and progress["start_raw"] <= prep["start_raw"] <= tools[0]["start_raw"]
                          <= tools[0]["stop_raw"] <= prep["stop_raw"] <= requests[0]["admitted_raw"]
                          and prep["seconds"] == prep["stop_raw"] - prep["start_raw"]
                          and tools[0]["log"] == rank["log"]["path"], (label, "rank not charged before dispatch"))
            audit.bound(read, rank["log"])
            terminal = fixed.end_of_arm(audit, read, state, label, audited[label])
            routes = [tool for tool in tools if PurePosixPath(tool["log"]).name == "route.log"]
            output[label] = {
                "dispatched": len(requests),
                "finished": audited[label]["completed"],
                "accepted": len(trace),
                "terminal_action_count": final["action_count"],
                "terminal_area_saved_um2": final["area_saved_um2"],
                "functional_area_reduction_pct": final["area_saved_um2"] * 100.0 / base,
                "time_normalized_auc_um2": auc,
                "first_terminal_attainment_s": threshold_endpoint(trace, final["area_saved_um2"])["charged_elapsed_s"],
                "first_common_attainment_s": threshold_endpoint(trace, COMMON_AREA)["charged_elapsed_s"],
                "first_adaptive_terminal_area_attainment_s": threshold_endpoint(trace, ADAPTIVE_AREA)["charged_elapsed_s"],
                "tt_power_change_pct": deltas,
                "tt_power_measurement": measured,
                "completed_drt_rcx_tool_s": math.fsum(tool["wall_seconds"] for tool in routes if tool["returncode"] == 0),
                "all_drt_rcx_tool_s_including_wall_cutoff": math.fsum(tool["wall_seconds"] for tool in routes),
                "stop_reason": terminal["stop"],
                "raw_search_s_available_after_screening": terminal["time_for_rank_and_search_s"],
                "tool_timeouts": terminal["tool_timeouts"],
                "rank_preparation_s": prep["seconds"],
                "rank_receipt": fingerprint(rank_path, rank_raw),
                "progress": arm["progress"],
                "tool_ledger": arm["tool_ledger"],
                "accepted_trace": trace,
            }
        common = [threshold_endpoint(row["accepted_trace"], COMMON_AREA) for row in output.values()]
        adaptive = [threshold_endpoint(output[label]["accepted_trace"], ADAPTIVE_AREA)
                    for label in ("single_boxed", "faeco_boxed")]
        audit.require(all(row["physical_hashes"] == common[0]["physical_hashes"] for row in common)
                      and adaptive[0]["physical_hashes"] == adaptive[1]["physical_hashes"],
                      "reported same-area first attainment is a different physical endpoint")
        return {
            "run": str(fixed.V2_ROOT),
            "fixed_archives": fixed.FIXED_ARCHIVES,
            "rebuilt_reference_archive": {"name": REBUILT, "sha256": REBUILT_SHA},
            "stage_progress": fingerprint(state_path, state_raw),
            "protocol": state["protocol"],
            "reference_qualification": state["qualification"],
            "screening_receipt": protocol["screen_input"]["receipt"],
            "charged_screening_s": screen_s,
            "window_s_including_screening": window,
            "clock_period_ps": protocol["period_basis"]["period_ps"],
            "setup_wns_budget_ps": protocol["gate"]["budget_ps"],
            "reference_functional_area_um2": base,
            "common_threshold_um2": COMMON_AREA,
            "adaptive_terminal_comparison_threshold_um2": ADAPTIVE_AREA,
            "common_threshold_matches_same_physical_endpoint": True,
            "adaptive_terminal_matches_single_physical_endpoint": True,
            "reference_tt_power": measured_reference,
            "tt_power_policy": {"liberty": qualification["view_liberty_groups"]["TT"], "sdc": reference["sdc"],
                                "activity": "tool defaults", "included_in_search_budget": False},
            "arms": output,
        }


def latex_rows(data):
    rows = data["arms"].values()
    functions = [
        ("派发/完成/接受", lambda r: f"{r['dispatched']}/{r['finished']}/{r['accepted']}"),
        (r"终态回收（\textmu m$^2$）", lambda r: f"{r['terminal_area_saved_um2']:.4f}"),
        ("终态动作数", lambda r: str(r["terminal_action_count"])),
        (r"功能面积降幅（\%）", lambda r: f"{r['functional_area_reduction_pct']:.4f}"),
        (r"时间平均收益（\textmu m$^2$）", lambda r: f"{r['time_normalized_auc_um2']:.4f}"),
        ("各自终态首达（s）", lambda r: f"{r['first_terminal_attainment_s']:.2f}"),
        (rf"共达{data['common_threshold_um2']:.4f}\,\textmu m$^2$（s）",
         lambda r: f"{r['first_common_attainment_s']:.2f}"),
    ]
    power_rows = [(r"TT总功耗变化（\%）", "total"), (r"TT组合功耗变化（\%）", "combinational"),
                  (r"TT漏电变化（\%）", "leakage")]
    lines = [" & ".join([label, *(render(row) for row in rows)]) + r" \\" for label, render in functions]
    lines.extend(" & ".join([label, *("$" + format(row["tt_power_change_pct"][metric], ".4f") + "$"
                                     for row in rows)]) + r" \\" for label, metric in power_rows)
    return "\n".join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--format", choices=("json", "latex", "latex-source"), default="json")
    args = parser.parse_args()
    data = table_data(args.evidence)
    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.format == "latex":
        print(latex_rows(data))
    else:
        print(r"\newcommand{\StageFiveResultRows}{%")
        print(latex_rows(data))
        print("}")


if __name__ == "__main__":
    main()
