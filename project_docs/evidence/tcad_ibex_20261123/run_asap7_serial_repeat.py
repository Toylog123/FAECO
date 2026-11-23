#!/usr/bin/env python3
"""Repeat both ASAP7 method orders with fresh physical work to the same area target."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from setup_budget import original_period_ps


ORDERS = {"reverse": ("faeco", "single"), "original": ("single", "faeco")}
TARGET_PCT = 0.01
BUDGET_PCT = 1.0
CPU_SET = list(range(6))


class MetTarget(Exception):
    """Stop the existing scheduler before dispatching any work after the target."""


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def check_previous(args):
    old, current = (read(root / "config.json") for root in (args.previous_run, args.out))
    for key in ("pdk", "top", "budget_attempts_per_arm", "batch_size", "methods_route_threads",
                "route_mode", "route_drt_iters", "route_guide_source", "route_timeout_seconds",
                "sta_timeout_seconds_per_view", "sec_timeout_seconds", "numerical_tolerance_ps",
                "report_setup_endpoints", "original_clock_period_ps", "primary_budget_pct", "primary_mode",
                "primary_target_area_pct", "setup_tns_loss_budget"):
        if old[key] != current[key]:
            raise comparison.TrialFailure(f"serial run differs from previous configuration at {key}")
    for key in ("control", "original_sdc", "control_drc", "route_guide", "qualification_receipt",
                "source_libraries", "flow", "tools"):
        if old["bindings"][key] != current["bindings"][key]:
            raise comparison.TrialFailure(f"serial run changes a previous binding at {key}")
    for key, binding in old["bindings"]["driver_source"].items():
        if current["bindings"]["driver_source"][key] != binding:
            raise comparison.TrialFailure(f"serial run changes a previous driver source at {key}")
    if comparison.bind(args.previous_run / "pool.json")["sha256"] != comparison.bind(args.out / "pool.json")["sha256"]:
        raise comparison.TrialFailure("serial run changes the ordered candidate pool")
    prior = read(args.previous_run / "results.json")
    if prior["status"] != "matched":
        raise comparison.TrialFailure("previous run lacks a complete matched receipt")
    return prior


def measure_arm(args, cache, reference, pool, method, gate, directory):
    directory.mkdir()
    target = reference.area * TARGET_PCT / 100
    scheduler_policy = comparison.BudgetPolicy.from_ps(
        gate.wns_ps, tolerance_ns=comparison.PS_TOLERANCE / 1000,
    )
    attempts = []
    selected = reference
    first_hit = None
    begin = time.monotonic()
    begin_utc = iso_now()

    def evaluate(actions):
        nonlocal selected, first_hit
        if first_hit is not None:
            raise MetTarget
        seq = len(attempts) + 1
        print(f"{directory.parent.name} {method} {seq}/{args.max_evals} start", flush=True)
        endpoint, receipt = cache.request(actions, gate, fresh_directory=directory / f"{seq:02d}_physical")
        accepted = (comparison.assess(reference, endpoint, scheduler_policy).feasible
                    and endpoint.area < selected.area - 1e-9)
        if accepted:
            selected = endpoint
        comparison.save(directory / f"{seq:02d}.json", receipt)
        print(f"{directory.parent.name} {method} {seq} {receipt['failures'] or 'passed gates'}", flush=True)
        elapsed = time.monotonic() - begin
        attempts.append({"elapsed_seconds": elapsed, "accepted": accepted, **receipt})
        if accepted and reference.area - selected.area >= target - 1e-9:
            first_hit = elapsed
        return endpoint

    try:
        scheduled = comparison.run_method(method, reference, pool, evaluate, args.max_evals,
                                          args.batch_size, policy=scheduler_policy)
    except MetTarget:
        pass
    else:
        if scheduled["selected"] != selected or scheduled["evaluations_used"] != len(attempts):
            raise comparison.TrialFailure("measured checkpoints disagree with scheduler")
    end = time.monotonic()
    result = {
        "start_monotonic": begin, "end_monotonic": end,
        "start_utc": begin_utc, "end_utc": iso_now(), "elapsed_seconds": end - begin,
        "target_reached_seconds": first_hit, "target_area_saved": target,
        "evaluations": len(attempts), "selected": asdict(selected), "area_saved": reference.area - selected.area,
        "checkpoints": attempts,
    }
    comparison.save(directory / "summary.json", result)
    return result


def run_serial(args, evaluator, reference, pool, baseline_record, noop):
    previous = check_previous(args)
    if any(baseline_record["views"][corner] != previous["control"]["views"][corner]
           for corner in comparison.CORNERS):
        raise comparison.TrialFailure("live CONTROL views changed from the previous run")
    gate = sweep.budget_gate(evaluator, BUDGET_PCT, False)
    cache = sweep.TrialCache(evaluator)
    pairs = {}
    for label, order in ORDERS.items():
        directory = args.out / label
        directory.mkdir()
        arms = pairs[label] = {}
        for method in order:
            arms[method] = measure_arm(args, cache, reference, pool, method, gate, directory / method)
            comparison.save(args.out / "serial_progress.json", pairs)
    totals = cache.totals()
    count = sum(arm["evaluations"] for pair in pairs.values() for arm in pair.values())
    complete = (totals["drt_completions"] == totals["rcx_completions"] == count
                and totals["view_sta_attempts"] == count * len(comparison.CORNERS)
                and all(set(trial.receipt["views"]) == set(comparison.CORNERS) for trial in cache.measurements))
    return complete, {
        "orders": ORDERS, "pairs": pairs, "gate": sweep.gate_summary(gate, evaluator.ref_views),
        "physical_operations": totals, "target_area_pct": TARGET_PCT,
        "shared_noop_operations": sweep.operation_counts(noop),
    }


def main():
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--previous-run", required=True, type=Path)
    args = comparison.prepare_args(parser, parser.parse_args())
    if args.pdk != "asap7" or args.probe_only or args.prepare_only:
        parser.error("the repeat requires a full ASAP7 run")
    affinity = sorted(os.sched_getaffinity(0))
    if affinity != CPU_SET:
        parser.error(f"use CPU affinity {CPU_SET}, observed {affinity}")
    try:
        args.previous_run = args.previous_run.resolve(strict=True)
        args.clock_period_ps = original_period_ps(read(args.views_json), args.original_sdc)
        return comparison.run(args, matched_runner=run_serial, config_overrides={
            "previous_run": comparison.bind(args.previous_run / "results.json"),
            "cpu_affinity": affinity, "orders": ORDERS,
            "methods_in_run_order": [method for order in ORDERS.values() for method in order],
            "tns_gate": True, "setup_budget_ps_per_view": 10.0,
            "original_clock_period_ps": args.clock_period_ps, "primary_budget_pct": BUDGET_PCT,
            "primary_mode": "tradeoff", "primary_target_area_pct": TARGET_PCT,
            "setup_tns_loss_budget": "max(10 * B_WNS, clock ratio * abs(reference TNS)) per view",
            "final_budget_slot": "terminal top-level dispatch is a singleton; an in-flight bisection can use two edits",
            "termination": "first accepted SEC-verified target or six calls; no cross-arm reuse",
        }, extra_sources=(Path(__file__), Path(sweep.__file__), Path(sweep.policy.__file__)))
    except (comparison.TrialFailure, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
