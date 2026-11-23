#!/usr/bin/env python3
"""Diagnose hold against bound zero-edit DRT without modifying strict results."""

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

import compare_ibex as comparison
from run_screened_matrix import bind_runtime
from verify_screened_matrix import MatrixAudit
from verify_setup_protocol import check_bindings, complete, digest, equal, need, process, read


CORNERS = comparison.CORNERS
CLOCK = "CLOCK_MONOTONIC_RAW"
RELATIVE_HOLD = {f"{view}:hold_regression" for view in CORNERS}
HOLD_TOLERANCE_PS = 0.001


def verify_zero_edit(root, config):
    path = root / "noop" / "receipt.json"
    history = Path(__file__).with_name("SKY130_NOOP_AUDIT.json")
    known, = (row for row in read(history) if row["mode"] == "embedded guide DRT")
    equal((str(path), digest(path)), (known["raw_receipt"], known["receipt_sha256"]), "pinned embedded zero-edit")
    prior = read(root / "config.json")
    expected = config["bindings"]
    old = prior["bindings"]
    for key in ("control", "original_sdc", "control_drc", "qualification_receipt", "source_libraries", "flow", "used_libraries"):
        equal(old[key], expected[key], f"same original freeze {key}")
    for key in ("openroad", "opensta"):
        equal(old["tools"][key], expected["tools"][key], f"same tool {key}")
    for key in ("pdk", "top", "route_guide_source", "route_mode", "route_drt_iters", "methods_route_threads",
                "numerical_tolerance_ps", "hold_threshold_ps", "hold_nonregression_per_view"):
        equal(prior[key], config[key], f"same physical setup {key}")
    equal((prior["route_guide_source"], prior["route_mode"]), ("embedded in frozen CONTROL ODB", "local"),
          "embedded local DRT comparator")
    equal((prior["hold_threshold_ps"], prior["numerical_tolerance_ps"]), (0.0, HOLD_TOLERANCE_PS),
          "same absolute hold zero and relative loss tolerance")
    bindings = {key: old[key] for key in ("control", "original_sdc", "source_libraries", "flow", "used_libraries")}
    check_bindings(bindings)
    row = read(path)
    equal(row["control_sdc"], old["control"]["sdc"], "original exported SDC binding")
    equal((row["actions"], row["area_saved"], row["drc_violations"]), ([], 0.0, 0), "unchanged zero-edit netlist area")
    equal((row["routed_to_completion"], row["extracted_to_completion"]), (True, True), "real fresh DRT/RCX")
    gold = old["control"]["v"]
    arts = row["artifacts"]
    check_bindings(arts)
    equal(arts["v"]["sha256"], gold["sha256"], "zero-edit routed Verilog byte identity")
    need(not Path(arts["drc"]["path"]).read_text().strip(), "zero-edit DRC report")
    phase = row["operations"]["DRT_RCX"]
    route = process(phase, path.parent / "route.log", prior["route_timeout_seconds"])
    need(complete(phase, route, "IBEX_ROUTE_COMPLETE"), "zero-edit raw DRT/RCX completion")
    for mark in ("IBEX_DRT_COMPLETE", "IBEX_RCX_COMPLETE", "IBEX_DRT_VIOLATIONS 0", "IBEX_CLEARED_SIGNAL_WIRES 0"):
        need(mark in route.splitlines(), f"zero-edit raw marker {mark}")
    need("IBEX_TOUCHED_NET " not in route and "IBEX_REUSED_FROZEN_DRT" not in route, "actual zero-edit route scope")
    route_tcl = (path.parent / "route.tcl").read_text().splitlines()
    need(any("grt::have_routes" in line for line in route_tcl)
         and not any("swapMaster" in line for line in route_tcl), "embedded zero-edit route Tcl")
    for command, key in (("read_db", "odb"), ("read_sdc", "sdc")):
        equal([line for line in route_tcl if line.startswith(command + " ")],
              [f"{command} {comparison.tcl(old['control'][key]['path'])}"], f"zero-edit DRT input {key}")
    layout = comparison.changed_geometry(Path(old["control"]["def"]["path"]), Path(arts["def"]["path"]), set())
    equal(layout, read(path.parent / "layout_changes.json"), "zero-edit placement and routing geometry")
    equal(layout["changed_component_placement"], [], "zero-edit DRT did not move components")
    for view in CORNERS:
        op = row["operations"][f"STA_{view}"]
        text = process(op, path.parent / f"sta_{view}.log", prior["sta_timeout_seconds_per_view"])
        need(complete(op, text, "IBEX_STA_COMPLETE"), f"zero-edit measured {view} STA")
        equal(text.splitlines()[0], f"IBEX_STA_ROUTED_ODB {arts['odb']['path']}", f"zero-edit actual {view} ODB")
        tcl = (path.parent / f"sta_{view}.odb.tcl").read_text().splitlines()
        for command, binding in (("read_db", arts["odb"]), ("read_sdc", old["control"]["sdc"]),
                                 ("read_spef", arts["spef"])):
            q = comparison.tcl(binding["path"])
            equal([line for line in tcl if line.startswith(command + " ")],
                  [f"{command} {{{binding['path']}}}" if command == "read_db" else f"{command} {q}"],
                  f"zero-edit actual STA deck {view} {command}")
        equal([line for line in tcl if line.startswith("read_liberty ")],
              [f"read_liberty {comparison.tcl(item['path'])}" for item in old["used_libraries"][view]],
              f"zero-edit STA views {view}")
        equal(comparison.parse_sta(text), row["views"][view], f"zero-edit raw {view} timing")
        need(row["views"][view]["hold_wns_ps"] >= 0, f"zero-edit absolute hold {view}")
    return row, {"receipt": comparison.bind(path), "config": comparison.bind(root / "config.json"),
                 "control_hold_deltas_ps": {view: known["setup_hold_deltas"][view]["hold_wns_ps"] for view in CORNERS},
                 "changed_nets": len(layout["changed_nets"])}


def classify(check, physical, zero, source):
    comparison_by_view = {}
    failures = [reason for reason in check["failures"] if reason not in RELATIVE_HOLD]
    for view in CORNERS:
        base = source["views"][view]["hold_wns_ps"]
        ref = zero["views"][view]["hold_wns_ps"]
        candidate = physical["views"][view]["hold_wns_ps"]
        held = candidate >= ref - HOLD_TOLERANCE_PS
        absolute = candidate >= 0
        if not absolute and f"{view}:negative_hold" not in failures:
            failures.append(f"{view}:negative_hold")
        if not held:
            failures.append(f"{view}:hold_vs_rerouted_zero_edit")
        comparison_by_view[view] = {
            "source_hold_ps": base, "zero_edit_hold_ps": ref, "candidate_hold_ps": candidate,
            "delta_vs_source_ps": candidate - base, "delta_vs_zero_edit_ps": candidate - ref,
            "absolute_nonnegative": absolute, "hold_within_zero_edit_tolerance": held,
        }
    return {"hold_comparisons": comparison_by_view, "strict_failures": check["failures"],
            "diagnostic_failures": failures, "diagnostic_qualifies_for_sec": not failures}


def audit_pilot(pilot_root, verification, zero, config):
    final = read(pilot_root / "results.json")
    equal(final["status"], "matched", "pilot four cases complete")
    verified = read(verification)["physical_pilot"]
    equal((digest(pilot_root / "results.json"), digest(pilot_root / "config.json")),
          (verified["results_sha256"], verified["config_sha256"]), "independently verified pilot")
    output = []
    for idx, (case, checked) in enumerate(zip(final["cases"], verified["cases"], strict=True), 1):
        check = case["physical"]
        physical = read(Path(check["physical_receipt"]))
        equal(physical["actions"], [checked["action"]["action_id"]], f"independently verified edit {idx}")
        equal(physical["control_sdc"], config["bindings"]["control"]["sdc"], f"unchanged candidate SDC {idx}")
        equal(check["failures"], checked["failures"], f"independently verified gates {idx}")
        for view in CORNERS:
            equal(physical["views"][view]["hold_wns_ps"], checked["physical_delta_by_view"][view]["hold_wns_ps"],
                  f"independently verified physical hold {idx}/{view}")
        decision = classify(check, physical, zero, final["control"])
        output.append({**decision, "case": idx, "action": checked["action"],
                       "area_saved": physical["area_saved"], "strict_accepted": case["endpoint"]["sec_pass"],
                       "routed_verilog": physical["artifacts"]["v"]})
    return output


def project_matrix(root, config, zero):
    final = read(root / "results.json")
    matrix = read(root / "config.json")
    equal(final["status"], "matched", "complete matrix for projection")
    for key in ("control", "original_sdc", "flow", "used_libraries"):
        equal(matrix["bindings"][key], config["bindings"][key], f"same Ibex projection freeze {key}")
    results = {}
    for pool, methods in final["arms"].items():
        order = results[pool] = {}
        for method, arm in methods.items():
            passed = []
            for index, (path, checkpoint) in enumerate(zip(
                    arm["attempt_receipts"], arm["end_to_end_checkpoints"], strict=True), 1):
                check = read(Path(path))
                physical = read(Path(check["physical_receipt"]))
                equal(physical["control_sdc"], config["bindings"]["control"]["sdc"], "identical matrix candidate SDC")
                if set(physical["views"]) != set(CORNERS):
                    continue
                row = classify(check, physical, zero, final["control"])
                if row["diagnostic_qualifies_for_sec"]:
                    passed.append({
                        "attempt": index, "actions": check["actions"], "area_saved": physical["area_saved"],
                        "end_to_end_seconds": checkpoint["elapsed_seconds"],
                        "strict_sec_passed": check["endpoint"]["sec_pass"],
                    })
            limit = arm["wall_window"]["wall_limit_seconds"]
            order[method] = {
                "observed_candidates_passing_shifted_hold": passed,
                "max_observed_physical_delta": max((p["area_saved"] for p in passed), default=0.0),
                "max_observed_delta_within_original_window": max(
                    (p["area_saved"] for p in passed if p["end_to_end_seconds"] <= limit), default=0.0),
                "strict_validated_gain": arm["area_saved"],
            }
    return {"interpretation": "projection of observed action tuples only; no rescheduling, estimated proof time, or new SEC",
            "results": results}


def prove_diagnostics(out, config, pilot_root, cases):
    """Run a fresh bounded SEC only, independently of the unchanged strict pilot."""
    need(not out.is_relative_to(pilot_root), "diagnostic SEC output must be outside the strict physical pilot")
    out.mkdir(parents=True)
    frozen = config["bindings"]
    gold = frozen["control"]["v"]
    tool = frozen["tools"]["sec"]
    libraries = frozen["used_libraries"]["TT"]
    verify = MatrixAudit(pilot_root)
    timeout_seconds = config["sec_timeout_seconds"]
    env = os.environ.copy()
    env["FAECO_SEC_LIBRARIES"] = json.dumps([item["path"] for item in libraries])
    env["FAECO_SEC_PDK"] = config["pdk"]
    env["FAECO_DESIGN_TOP"] = config["top"]
    command = [sys.executable, tool["path"]] if Path(tool["path"]).suffix == ".py" else [tool["path"]]
    results = []
    with bind_runtime(config["top"], None):
        for case in cases:
            if not case["diagnostic_qualifies_for_sec"]:
                continue
            gate = case["routed_verilog"]
            bindings = (gold, gate, tool, *libraries)
            for asset in bindings:
                equal(comparison.bind(Path(asset["path"])), asset, f"pre-SEC diagnostic input {asset['path']}")
            directory = out / f"case_{case['case']:02d}"
            directory.mkdir()
            op = asdict(comparison.run_process([*command, gold["path"], gate["path"], directory / "sec"],
                                               directory / "sec.log", timeout_seconds, env=env))
            passed = op["returncode"] == 0
            proven = verify.proof(directory, {"SEC": op}, gate, passed=passed)
            for asset in bindings:
                equal(comparison.bind(Path(asset["path"])), asset, f"post-SEC diagnostic input {asset['path']}")
            row = {"case": case["case"], "gold": gold, "gate": gate, "clock": CLOCK,
                   "operation": op, "passed": passed, "confirmed_proofs": proven,
                   "diagnostic_only": True}
            comparison.save(directory / "diagnostic_sec.json", row)
            results.append(row)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pilot", type=Path)
    parser.add_argument("zero_edit", type=Path)
    parser.add_argument("--pilot-audit", type=Path, required=True)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--run-sec", action="store_true", help="after main timings, prove only the diagnostic qualifiers")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if bool(args.out) != args.run_sec:
        parser.error("--run-sec and a fresh --out directory must be specified together")
    pilot = args.pilot.resolve(strict=True)
    cfg = read(pilot / "config.json")
    zero, source = verify_zero_edit(args.zero_edit.resolve(strict=True), cfg)
    cases = audit_pilot(pilot, args.pilot_audit.resolve(strict=True), zero, cfg)
    output = {"interpretation": "separate hold diagnostic using historical embedded zero-edit DRT; strict outcomes unchanged",
              "pilot_results_sha256": digest(pilot / "results.json"), "zero_edit_binding": source, "cases": cases,
              "diagnostic_sec_executed": args.run_sec, "diagnostic_sec": []}
    if args.matrix is not None:
        output["read_only_matrix_projection"] = project_matrix(args.matrix.resolve(strict=True), cfg, zero)
    if args.run_sec:
        directory = args.out.resolve()
        output["diagnostic_sec"] = prove_diagnostics(directory, cfg, pilot, cases)
        comparison.save(directory / "DIAGNOSTIC_RESULTS.json", output)
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
