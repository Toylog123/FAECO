#!/usr/bin/env python3
"""Reconstruct the matched AES online single-gate and FAECO comparisons."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import math
from pathlib import Path

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
import verify_aes_cold_online as cold
from verify_aes_factorial import accepted_checkpoints, compare_cells
from verify_aes_incident_priority_matched import verify_pair_inputs
from verify_aes_protected_online import check


ORDERS = {"forward": ["single", "faeco"], "reverse": ["faeco", "single"]}
SCHEDULE = [(order, method) for order, methods in ORDERS.items() for method in methods]
CELL_FIELDS = {"methods", "diagnostic_methods", "matched_order", "scheduler"}
PLAN_SETTINGS = {
    "orders": ORDERS, "area_target_pct": 0.01, "wall_limit_seconds_including_screen": 720.0,
    "maximum_requests_per_cell": 6,
    "execution": "serial, fresh physical work per cell; both schedulers use current-candidate pre-DRT diagnosis",
}
STAGES = {"route.log": "route", "audit.log": "unlocked_drc", "sec.log": "sec", "preview.log": "diagnosis",
          **{f"sta_{view}.log": "sta" for view in comparison.CORNERS}}


def verify_protocol(root):
    path = root / "matched_protocol.json"
    plan = read(path)
    check(plan.keys() == PLAN_SETTINGS.keys() | {"driver", "matrix", "preflight"}
          and all(plan[key] == value for key, value in PLAN_SETTINGS.items()),
          "matched schedule or preregistered settings changed")
    producer = Path(__file__).with_name("run_aes_greedy_matched.py").resolve()
    check(verify(plan["driver"]) == producer, "unexpected matched producer")
    verify(plan["matrix"])
    verify(plan["preflight"])
    return plan, comparison.bind(path)


def verify_manifest(cell, order, method, plan, binding):
    manifest = read(cell / "config.json")
    check(manifest["methods"] == manifest["diagnostic_methods"] == [method]
          and manifest["matched_order"] == order and manifest["scheduler"] == method,
          f"incorrect scheduler or diagnostic backend for {order}/{method}")
    check(manifest["matrix"] == plan["matrix"] and manifest["matched_protocol"] == binding
          and manifest["driver_sources"]["run_aes_greedy_matched.py"] == plan["driver"]
          and read(cell / "transferred_preflight.json")["preflight_result"] == plan["preflight"],
          f"matrix, driver, or common physical preflight changed for {order}/{method}")
    check(manifest["measurement_clock"] == "CLOCK_MONOTONIC_RAW"
          and manifest["batch_size"] == 3
          and manifest["diagnostic_strategy"] == "fresh pre-DRT local swap and erase on frozen ROUTED control",
          f"unexpected clock, batch size, or diagnostic strategy in {order}/{method}")
    # The cold auditor's common settings and source checks were defined for a
    # three-method producer. The matched method lists were checked just above.
    cold.verify_protocol(cell, {**manifest, "methods": list(cold.METHODS), "diagnostic_methods": list(cold.ONLINE)})
    return manifest


def verify_opening(method, requests, pool, batch_size):
    width = 1 if method == "single" else batch_size
    expected = sorted(action.action_id for action in pool[:width])
    check(requests and requests[0]["actions"] == expected, f"wrong opening proposal for {method}")


def audit_cell(cell, method, manifest, entry, assets):
    arm = cell / method
    summary = read(verify(entry["summary"]))
    check(entry["summary"]["path"] == str(arm / "summary.json")
          and entry["manifest"] == comparison.bind(cell / "config.json")
          and summary["method"] == read(arm / "progress.json")["method"] == method
          and summary == read(cell / "result.json") == entry["result"],
          f"published result does not match the physical summary in {cell}")
    inputs = verify_pair_inputs(cell, manifest)
    _, control_views, nets, pool, reference = inputs
    original_online = cold.ONLINE
    try:
        cold.ONLINE = (method,)
        requests = cold.audit_requests(arm, assets, pool, nets)
    finally:
        cold.ONLINE = original_online
    verify_opening(method, requests, pool, manifest["batch_size"])
    audited = cold.replay_arm(cell, method, manifest, inputs, requests)
    counts = cold.verify_operations(cell, method, audited)
    diagnostics = [request["diagnosis"] for request in requests]
    counts.update({"diagnostics_started": sum(row["preview_tool_started"] for row in diagnostics),
                   "diagnoses_completed": sum(row["completed"] for row in diagnostics),
                   "diagnoses_guided": sum(row["status"] == "guided" for row in diagnostics),
                   "diagnoses_unavailable": sum(row["status"] == "unavailable" for row in diagnostics)})
    stage_times = {stage: [] for stage in STAGES.values()}
    for tool in read(verify(audited["source_subprocesses"])):
        stage_times[STAGES[Path(tool["log"]).name]].append(tool["wall_seconds"])
    check(len(stage_times["diagnosis"]) == counts["diagnostics_started"], "diagnostic start count differs from ledger")
    accepted, first, best = accepted_checkpoints(arm, audited, reference, requests)
    progress = read(verify(audited["source_progress"]))
    for request, measured in zip(requests, progress["logical_requests"], strict=True):
        request["failures"] = measured["failures"] if request["logical_finished"] else None
    audited.update(requests=requests, operation_counts=counts, accepted_checkpoints=accepted,
                   first_target=first, best_checkpoint=best)
    window = audited["window"]
    check(abs(window["target_area_saved"] - reference.area * 0.0001) < 1e-9,
          "target area does not represent 0.01 percent of the frozen reference")
    metrics = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
    selected_views = best["identity"]["views"] if best else control_views
    timing_delta = {view: {key: selected_views[view][key] - control_views[view][key] for key in metrics}
                    for view in comparison.CORNERS}
    folded = {
        **{key: audited[key] for key in ("logical_admitted", "logical_finished", "completed_retries", "stop_reason")},
        **{key: window[key] for key in ("time_to_target_seconds", "target_reached_in_window", "target_area_saved",
                                       "area_saved", "area_saved_pct")},
        "screen_seconds": manifest["charged_screening_seconds_per_arm"],
        "search_raw_seconds": audited["raw_stop"] - audited["raw_start"],
        "tool_seconds": summary["tool_seconds"],
        "tool_seconds_by_stage": {stage: math.fsum(seconds) for stage, seconds in stage_times.items()},
        "completed_diagnosis_seconds": math.fsum(row["seconds"] for row in diagnostics if row["completed"]),
        "priority_seconds": audited["priority_preparation"]["seconds"] if audited["priority_preparation"] else 0.0,
        "selected_area": window["selected"]["area"], "selected_timing_delta_ps": timing_delta,
        "first_target_actions": first["actions"] if first else None,
        "best_checkpoint_actions": best["actions"] if best else None, **counts,
    }
    return audited, folded


def available_comparisons(arms, folded):
    return {
        "within_order": [compare_cells(arms, folded, (order, "single"), (order, "faeco"))
                         for order in ORDERS if all(method in arms[order] for method in ORDERS[order])],
        "order_repeats": [compare_cells(arms, folded, ("forward", method), ("reverse", method))
                          for method in ORDERS["forward"] if all(method in arms[order] for order in ORDERS)],
    }


def audit(root, prefix):
    plan, binding = verify_protocol(root)
    published = root / "results.json"
    check(published.is_file(), "the producer has not yet published its first completed cell")
    snapshot = published.read_bytes()
    entries = json.loads(snapshot)
    limit = len(SCHEDULE) if prefix is None else prefix
    check(limit <= len(entries) <= len(SCHEDULE), f"only {len(entries)} cells are published; audit requires {limit}")
    check([(row["order"], row["cell"], row["method"]) for row in entries]
          == [(order, method, method) for order, method in SCHEDULE[:len(entries)]],
          "published cell labels or order differ from the matched schedule")
    assets = read(verify(plan["matrix"]))["bindings"]
    arms = {order: {} for order in ORDERS}
    folded = {order: {} for order in ORDERS}
    shared = None
    previous_stop = -math.inf
    for entry, (order, method) in zip(entries[:limit], SCHEDULE[:limit], strict=True):
        cell = root / order / method
        manifest = verify_manifest(cell, order, method, plan, binding)
        common = {key: value for key, value in manifest.items() if key not in CELL_FIELDS}
        if shared is None:
            shared = common
        check(common == shared, f"common matched configuration changed in {order}/{method}")
        row, metrics = audit_cell(cell, method, manifest, entry, assets)
        start, stop = entry["outer_start_raw"], entry["outer_stop_raw"]
        check(all(math.isfinite(value) for value in (start, row["raw_start"], row["raw_stop"], stop))
              and previous_stop <= start <= row["raw_start"] <= row["raw_stop"] <= stop,
              f"raw clock windows overlap or disagree in {order}/{method}")
        previous_stop = stop
        arms[order][method], folded[order][method] = row, metrics
        print(f"{order}/{method}: {row['logical_finished']}/{row['logical_admitted']} requests; "
              f"first={metrics['time_to_target_seconds']}; area={metrics['area_saved_pct']:.6g}%", flush=True)
    return {"audit_source": comparison.bind(Path(__file__).resolve()), "matched_protocol": binding,
            "producer_results_snapshot": {"path": str(published), "sha256": sha256(snapshot).hexdigest(),
                                          "bytes": len(snapshot), "published_cells": len(entries)},
            "audited_cells": limit, "full_audit": prefix is None, "folded": folded,
            "comparisons": available_comparisons(arms, folded), "arms": arms}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--prefix", type=int, choices=range(1, len(SCHEDULE) + 1))
    args = parser.parse_args()
    root = args.run.resolve(strict=True)
    result = audit(root, args.prefix)
    stem = f"independent_verification_prefix_{args.prefix}" if args.prefix else "independent_verification"
    comparison.save(root / f"{stem}.json", result)


if __name__ == "__main__":
    main()
