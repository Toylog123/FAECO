#!/usr/bin/env python3
"""Reconstruct completed AES factorial cells from their raw physical evidence."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import math
from pathlib import Path

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
import verify_aes_cold_online as cold
import verify_aes_incident_priority_matched as matched
from verify_aes_protected_online import check


FORWARD = [
    ["fixed_legacy", "fixed", False],
    ["fixed_online", "fixed", True],
    ["faeco_legacy", "faeco", False],
    ["faeco_online", "faeco", True],
]
ORDERS = {"forward": FORWARD, "reverse": list(reversed(FORWARD))}
SCHEDULE = [(order, *cell) for order, cells in ORDERS.items() for cell in cells]
CELL_FIELDS = {"methods", "diagnostic_methods", "factorial_cell", "factorial_order", "scheduler", "online_diagnostics"}


def method_for(scheduler, online):
    return "fixed_online" if scheduler == "fixed" and online else scheduler


def verify_protocol(root):
    path = root / "factorial_protocol.json"
    plan = read(path)
    expected = {"orders": ORDERS, "wall_limit_seconds_including_screen": 720.0,
                "maximum_requests_per_cell": 6, "area_target_pct": 0.01,
                "execution": "serial, fresh physical work per cell"}
    check(plan.keys() == expected.keys() | {"driver", "matrix", "preflight"}
          and all(plan[key] == value for key, value in expected.items()),
          "factorial schedule or preregistered settings changed")
    check(verify(plan["driver"]) == Path(__file__).with_name("run_aes_factorial.py").resolve(),
          "unexpected factorial producer")
    verify(plan["matrix"])
    verify(plan["preflight"])
    return plan, comparison.bind(path)


def verify_manifest(cell, order, label, scheduler, online, plan, plan_binding):
    manifest = read(cell / "config.json")
    method = method_for(scheduler, online)
    check(manifest["methods"] == [method] and manifest["diagnostic_methods"] == ([method] if online else [])
          and manifest["factorial_cell"] == label and manifest["factorial_order"] == order
          and manifest["scheduler"] == scheduler and manifest["online_diagnostics"] is online,
          f"incorrect scheduler or diagnostic backend for {order}/{label}")
    check(manifest["matrix"] == plan["matrix"] and manifest["factorial_protocol"] == plan_binding
          and manifest["driver_sources"]["run_aes_factorial.py"] == plan["driver"]
          and read(cell / "transferred_preflight.json")["preflight_result"] == plan["preflight"],
          f"matrix, driver, or common physical preflight changed for {order}/{label}")
    check(manifest["measurement_clock"] == "CLOCK_MONOTONIC_RAW"
          and manifest["diagnostic_strategy"] == "fresh pre-DRT local swap and erase on frozen ROUTED control",
          f"unexpected clock or diagnostic strategy in {order}/{label}")
    # The earlier protocol describes a three-method producer. Its common gates and
    # preflight checks still apply after checking this cell's singleton lists above.
    cold.verify_protocol(cell, {**manifest, "methods": list(cold.METHODS), "diagnostic_methods": list(cold.ONLINE)})
    return manifest


def accepted_checkpoints(arm, audited, reference, requests):
    window = audited["window"]
    progress = read(verify(audited["source_progress"]))
    check(audited["source_progress"]["path"] == str(arm / "progress.json"), "checkpoint came from another arm")
    accepted = []
    for row, request in zip(progress["checkpoints"], requests[:audited["logical_finished"]], strict=True):
        if row["accepted"]:
            endpoint = row["endpoint"]
            saved = reference.area - endpoint["area"]
            identity = cold.endpoint_identity({"selected": endpoint, "area_saved": saved})
            check(identity is not None and Path(identity["receipt"]["path"]).is_relative_to(arm / f"{request['id']:02d}"),
                  "accepted checkpoint endpoint did not originate in the matching request")
            accepted.append({"request_id": request["id"], "actions": request["actions"], "area": endpoint["area"],
                             "area_saved": saved, "elapsed_seconds": row["elapsed_seconds"], "identity": identity})
    first = next((row for row in accepted if row["area_saved"] >= window["target_area_saved"] - 1e-9), None)
    best = accepted[-1] if accepted else None
    check((first["elapsed_seconds"] if first else None) == window["time_to_target_seconds"]
          and (first is not None) == window["target_reached_in_window"], "the first target checkpoint differs")
    check((best["identity"] if best else None) == cold.endpoint_identity(window)
          and (best["area"] if best else reference.area) == window["selected"]["area"],
          "selected endpoint differs from the last accepted checkpoint")
    return accepted, first, best


def audit_cell(cell, method, online, manifest, entry, assets):
    arm = cell / method
    summary = read(verify(entry["summary"]))
    check(entry["summary"]["path"] == str(arm / "summary.json")
          and entry["manifest"] == comparison.bind(cell / "config.json")
          and summary["method"] == read(arm / "progress.json")["method"] == method
          and summary == read(cell / "result.json") == entry["result"],
          f"top-level or cell result differs from its physical summary in {cell}")
    inputs = matched.verify_pair_inputs(cell, manifest)
    _, control_views, nets, pool, reference = inputs
    prior_online = cold.ONLINE
    try:
        cold.ONLINE = (method,) if online else ()
        requests = cold.audit_requests(arm, assets, pool, nets)
    finally:
        cold.ONLINE = prior_online
    first_proposal = sorted(action.action_id for action in pool[:manifest["batch_size"]])
    check(requests and requests[0]["actions"] == first_proposal, "the opening physical proposal changed")
    audited = cold.replay_arm(cell, method, manifest, inputs, requests)
    counts = cold.verify_operations(cell, method, audited)
    diagnostics = [row["diagnosis"] for row in requests if row["diagnosis"] is not None]
    counts.update({"diagnostics_started": sum(row["preview_tool_started"] for row in diagnostics),
                   "diagnoses_completed": sum(row["completed"] for row in diagnostics),
                   "diagnoses_guided": sum(row["status"] == "guided" for row in diagnostics),
                   "diagnoses_unavailable": sum(row["status"] == "unavailable" for row in diagnostics)})
    stages = {"route.log": "route", "audit.log": "unlocked_drc", "sec.log": "sec", "preview.log": "diagnosis",
              **{f"sta_{view}.log": "sta" for view in comparison.CORNERS}}
    times = {stage: [] for stage in stages.values()}
    for tool in read(verify(audited["source_subprocesses"])):
        stage = stages[Path(tool["log"]).name]
        times[stage].append(tool["wall_seconds"])
    check(len(times["diagnosis"]) == counts["diagnostics_started"], "diagnostic count differs from the tool ledger")
    stage_seconds = {stage: math.fsum(values) for stage, values in times.items()}
    checkpoint_rows, first, best = accepted_checkpoints(arm, audited, reference, requests)
    window = audited["window"]
    audited.update(requests=requests, operation_counts=counts, accepted_checkpoints=checkpoint_rows,
                   first_target=first, best_checkpoint=best)
    timing_metrics = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
    selected_views = best["identity"]["views"] if best else control_views
    timing_delta = {view: {key: selected_views[view][key] - control_views[view][key] for key in timing_metrics}
                    for view in comparison.CORNERS}
    folded = {"logical_admitted": audited["logical_admitted"], "logical_finished": audited["logical_finished"],
              "completed_retries": audited["completed_retries"], "stop_reason": audited["stop_reason"],
              "screen_seconds": manifest["charged_screening_seconds_per_arm"],
              "search_raw_seconds": audited["raw_stop"] - audited["raw_start"], "tool_seconds": summary["tool_seconds"],
              "tool_seconds_by_stage": stage_seconds,
              "priority_seconds": audited["priority_preparation"]["seconds"] if audited["priority_preparation"] else 0.0,
              "completed_diagnosis_seconds": math.fsum(row["seconds"] for row in diagnostics if row["completed"]),
              "time_to_target_seconds": window["time_to_target_seconds"], "area_saved": window["area_saved"],
              "area_saved_pct": window["area_saved_pct"], "selected_area": window["selected"]["area"],
              "selected_timing_delta_ps": timing_delta,
              "first_target_actions": first["actions"] if first else None,
              "best_checkpoint_actions": best["actions"] if best else None, **counts}
    return audited, folded


def compare_checkpoints(left, right):
    if left is None or right is None:
        return None
    keys = ("files", "spef_except_date_sha256", "views_sha256")
    return {"same_actions": left["actions"] == right["actions"],
            "same_physical_endpoint": all(left["identity"][key] == right["identity"][key] for key in keys),
            "elapsed_seconds_right_minus_left": right["elapsed_seconds"] - left["elapsed_seconds"],
            "area_saved_right_minus_left": right["area_saved"] - left["area_saved"]}


def compare_cells(arms, folded, left, right):
    left_arm, right_arm = (arms[order][label] for order, label in (left, right))
    left_fold, right_fold = (folded[order][label] for order, label in (left, right))
    fields = ("area_saved_pct", "search_raw_seconds", "tool_seconds", "logical_admitted", "logical_finished",
              "completed_retries", "route_tools", "unlocked_drc_tools", "sta_tools", "sec_tools", "diagnostics_started")
    return {"left": "/".join(left), "right": "/".join(right),
            "first_targets": compare_checkpoints(left_arm["first_target"], right_arm["first_target"]),
            "best_checkpoints": compare_checkpoints(left_arm["best_checkpoint"], right_arm["best_checkpoint"]),
            "right_minus_left": {key: right_fold[key] - left_fold[key] for key in fields}}


def available_comparisons(arms, folded):
    within_order = [(order, a, b) for order in ORDERS for a, b in (
        ("fixed_legacy", "fixed_online"), ("faeco_legacy", "faeco_online"),
        ("fixed_legacy", "faeco_legacy"), ("fixed_online", "faeco_online"))]
    return {"within_order": [compare_cells(arms, folded, (order, a), (order, b))
                             for order, a, b in within_order if a in arms[order] and b in arms[order]],
            "order_repeats": [compare_cells(arms, folded, ("forward", label), ("reverse", label))
                              for label, _, _ in FORWARD if label in arms["forward"] and label in arms["reverse"]]}


def audit(root, prefix):
    plan, binding = verify_protocol(root)
    published = root / "results.json"
    check(published.is_file(), "the producer has not yet published its first completed cell")
    snapshot = published.read_bytes()
    entries = json.loads(snapshot)
    limit = len(SCHEDULE) if prefix is None else prefix
    check(limit <= len(entries) <= len(SCHEDULE), f"only {len(entries)} cells are published; audit requires {limit}")
    expected = [(order, label, method_for(scheduler, online)) for order, label, scheduler, online in SCHEDULE]
    check([(row["order"], row["cell"], row["method"]) for row in entries] == expected[:len(entries)],
          "published order, cell labels, or methods differ from the frozen schedule")
    assets = read(verify(plan["matrix"]))["bindings"]
    arms = {order: {} for order in ORDERS}
    folded = {order: {} for order in ORDERS}
    shared = None
    previous_end = -math.inf
    for entry, (order, label, scheduler, online) in zip(entries[:limit], SCHEDULE[:limit], strict=True):
        cell = root / order / label
        manifest = verify_manifest(cell, order, label, scheduler, online, plan, binding)
        common = {key: value for key, value in manifest.items() if key not in CELL_FIELDS}
        if shared is None:
            shared = common
        check(shared == common, f"common factorial configuration changed in {order}/{label}")
        row, metrics = audit_cell(cell, entry["method"], online, manifest, entry, assets)
        start, stop = entry["outer_start_raw"], entry["outer_stop_raw"]
        check(all(math.isfinite(value) for value in (start, row["raw_start"], row["raw_stop"], stop))
              and previous_end <= start <= row["raw_start"] <= row["raw_stop"] <= stop,
              f"raw clock windows overlap or disagree in {order}/{label}")
        previous_end = stop
        arms[order][label] = row
        folded[order][label] = metrics
        print(f"{order}/{label}: {row['logical_finished']}/{row['logical_admitted']} requests; "
              f"first={metrics['time_to_target_seconds']}; area={metrics['area_saved_pct']:.6g}%", flush=True)
    return {"audit_source": comparison.bind(Path(__file__)), "factorial_protocol": binding,
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
