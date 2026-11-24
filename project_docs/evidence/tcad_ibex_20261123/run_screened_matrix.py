#!/usr/bin/env python3
"""Compare fresh post-route search arms from a common legacy or screened pool."""

from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace

import compare_ibex as comparison
from incident_cap_priority import build_incident_priority
import run_setup_budget_sweep as sweep


CLOCK_NAME = "CLOCK_MONOTONIC_RAW"
BUDGET_PCT = 1.0
RELATIVE_HOLD_REASONS = {f"{corner}:hold_regression" for corner in comparison.CORNERS}


def read(path):
    return json.loads(path.read_bytes())


def raw_seconds():
    return time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW) / 1e9


@contextmanager
def bind_runtime(top, routing_config):
    """Use the selected top and measurement clock in this isolated driver process."""
    prior = comparison.TOP, comparison.time, sweep.time, comparison.fastroute
    old_top_env = os.environ.get("FAECO_DESIGN_TOP")
    try:
        comparison.TOP = top
        comparison.time = sweep.time = SimpleNamespace(monotonic=raw_seconds)
        if routing_config is not None:
            comparison.fastroute = lambda _: routing_config
        os.environ["FAECO_DESIGN_TOP"] = top
        yield
    finally:
        comparison.TOP, comparison.time, sweep.time, comparison.fastroute = prior
        if old_top_env is None:
            os.environ.pop("FAECO_DESIGN_TOP", None)
        else:
            os.environ["FAECO_DESIGN_TOP"] = old_top_env


def bind_screen_inputs(args):
    config = {"pool": comparison.bind(args.screen_pool), "receipt": comparison.bind(args.screen_receipt)}
    receipt = read(args.screen_receipt)
    duration = receipt["wall_seconds"]
    if (receipt.get("clock") != CLOCK_NAME or isinstance(duration, bool)
            or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0):
        raise ValueError("screening receipt lacks a valid raw-clock duration")
    if receipt.get("pool_sha256") != config["pool"]["sha256"] or receipt.get("top") != args.top:
        raise ValueError("screening receipt does not bind the ordered pool and requested top")
    for ext in ("odb", "spef", "sdc"):
        if receipt["control_sha256"][ext] != comparison.sha(args.control_dir / f"6_final.{ext}"):
            raise ValueError(f"screening receipt and matrix disagree on CONTROL {ext}")
    return config, duration


def assert_screen_inputs(bindings):
    for entry in bindings.values():
        if comparison.bind(Path(entry["path"])) != entry:
            raise comparison.TrialFailure(f"frozen screening input changed: {entry['path']}")


def screened_actions(args, evaluator):
    inventory = args.out / "control" / "inventory.log"
    masters, instances = comparison.parse_inventory(inventory.read_text(encoding="utf-8"))
    allowed = set()
    for action in comparison.generate_compatible_candidates(
            args.out / "control" / "flattened_instance_index.txt", evaluator.libraries["TT"]):
        allowed.add((action.instance.removeprefix("\\"), action.source_cell, action.target_cell))
    view_cells = set.intersection(*(set(comparison.liberty_areas(libs)) for libs in evaluator.libraries.values()))
    rows = read(args.screen_pool)
    if not isinstance(rows, list):
        raise ValueError("screened pool must be an ordered JSON list")
    actions = [comparison.PhysicalAction(**row) for row in rows]
    ids, names = set(), set()
    for act in actions:
        key = comparison.canonical_odb_name(act.instance)
        pair = (key, act.source_cell, act.target_cell)
        source, target = masters.get(act.source_cell), masters.get(act.target_cell)
        tags = instances.get(act.instance)
        if not act.action_id or act.action_id in ids or key in names:
            raise ValueError(f"duplicate or empty screened edit identity: {act.action_id}")
        if (pair not in allowed or evaluator.ref_masters.get(key) != act.source_cell
                or tags != [act.source_cell, "PLACED", "0", "0"]
                or not {act.source_cell, act.target_cell} <= view_cells
                or source is None or target is None or source[:4] != target[:4] or not source[2]
                or int(target[4]) >= int(source[4])):
            raise ValueError(f"screened edit does not meet physical compatibility: {act.action_id}")
        area_gain = evaluator.areas[act.source_cell] - evaluator.areas[act.target_cell]
        if not math.isclose(act.estimated_area_saving, area_gain, rel_tol=0, abs_tol=1e-6):
            raise ValueError(f"screened edit area does not match TT Liberty: {act.action_id}")
        ids.add(act.action_id)
        names.add(key)
    required = (args.max_evals - 1) * args.batch_size + 1
    if len(actions) < required:
        raise ValueError(f"screened pool has {len(actions)} unique edits, need {required}")
    return actions


def summarize_arm_times(args, reference, checkpoints, search_seconds, screen_seconds, ranking_seconds=0.0):
    front_end = screen_seconds + ranking_seconds
    e2e = [{**row, "elapsed_seconds": row["elapsed_seconds"] + front_end} for row in checkpoints]
    opts = {"target_area_pct": args.target_area_pct}
    first_hit = sweep.summarize_wall_window(reference, checkpoints, wall_limit_seconds=search_seconds, **opts)
    first_hit = first_hit["time_to_target_seconds"]
    return {
        "clock": CLOCK_NAME,
        "search_wall_seconds": search_seconds,
        "charged_screening_seconds": screen_seconds,
        "charged_ranking_seconds": ranking_seconds,
        "end_to_end_wall_seconds": search_seconds + front_end,
        "search_time_to_target_seconds": first_hit,
        "end_to_end_time_to_target_seconds": first_hit + front_end if first_hit is not None else None,
        "search_only_wall_window": sweep.summarize_wall_window(
            reference, checkpoints, wall_limit_seconds=args.wall_limit_seconds, **opts,
        ),
        "wall_window": sweep.summarize_wall_window(
            reference, e2e, wall_limit_seconds=args.wall_limit_seconds, **opts,
        ),
        "end_to_end_checkpoints": e2e,
    }


def stage_report(trials, attempts):
    spent = dict.fromkeys(("DRT_RCX", "STA_FF", "STA_TT", "STA_SS", "SEC"), 0.0)
    for trial in trials:
        for operation, data in (trial.receipt["operations"] | trial.proof_operations).items():
            spent[operation] += data["wall_seconds"]
    failures = Counter(failure for attempt in attempts for failure in attempt["failures"])
    relative_hold_only = sum(bool(row["failures"]) and set(row["failures"]) <= RELATIVE_HOLD_REASONS for row in attempts)
    return {"tool_stage_seconds": spent, "failures_by_exact_reason": dict(failures),
            "relative_hold_only_rejections": relative_hold_only}


def comparison_arms(args):
    if getattr(args, "screened_risk_pair", False):
        return ("screened",), ("fixed", "faeco"), RELATIVE_HOLD_REASONS
    if args.hold_aware_only:
        return ("screened",), ("faeco",), RELATIVE_HOLD_REASONS
    if args.screened_hold_aware:
        return ("screened",), comparison.METHODS, RELATIVE_HOLD_REASONS
    pools = ("legacy", "screened") if args.pool_order == "legacy-first" else ("screened", "legacy")
    return pools, comparison.METHODS, frozenset()


def run_matrix(args, evaluator, reference, pool, baseline_record, noop):
    assert_screen_inputs(args.screen_bindings)
    screened = screened_actions(args, evaluator)
    comparison.save(args.out / "screened_pool_used.json", [asdict(act) for act in screened])
    gate = sweep.budget_gate(evaluator, BUDGET_PCT, False)
    cache = sweep.TrialCache(evaluator)
    results = {}
    arm_order = []
    for kind in args.pool_order:
        active = pool if kind == "legacy" else screened
        evaluator.actions = {action.action_id: action for action in active}
        directory = args.out / kind
        directory.mkdir()
        results[kind] = {}
        for method in args.methods:
            ranking = args.incident_ranking if method == "faeco" else None
            priorities = {key: row["priority"] for key, row in ranking["actions"].items()} if ranking else None
            before = len(cache.measurements)
            start = raw_seconds()
            result, attempts = sweep.run_arm(
                args, cache, reference, active, method, gate, directory / method, primary=True,
                defer_split_reasons=args.defer_split_reasons if method == "faeco" else frozenset(),
                priority_after_defer=priorities,
            )
            end = raw_seconds()
            arm_order.append({"pool": kind, "method": method, "raw_start": start, "raw_end": end})
            screened_seconds = args.screen_seconds if kind == "screened" else 0.0
            result.update(summarize_arm_times(args, reference, result["checkpoints"],
                                              result["wall_seconds"], screened_seconds,
                                              ranking["raw_seconds"] if ranking else 0.0))
            result.update(stage_report(cache.measurements[before:], attempts))
            comparison.save(directory / method / "summary.json", result)
            results[kind][method] = result
            comparison.save(args.out / "matrix_progress.json", {"arms": results, "serial_arm_order": arm_order})
    assert_screen_inputs(args.screen_bindings)
    counts = cache.totals()
    expected = len(arm_order) * args.max_evals
    complete = (
        all(arm["evaluations_used"] == args.max_evals for methods in results.values() for arm in methods.values())
        and counts["logical_requests"] == counts["route_attempts"] == counts["drt_completions"]
        == counts["rcx_completions"] == expected
        and counts["view_sta_attempts"] == expected * len(comparison.CORNERS)
        and all(set(trial.receipt["views"]) == set(comparison.CORNERS) for trial in cache.measurements)
        and counts["physical_cache_hits"] == 0
    )
    return complete, {
        "arms": results, "serial_arm_order": arm_order, "gate": sweep.gate_summary(gate, evaluator.ref_views),
        "physical_operations": counts, "screen_inputs": args.screen_bindings,
        "qualified_legacy_instances": len(pool), "screened_instances": len(screened),
        "shared_control_operations": baseline_record["operations"],
        "shared_noop_operations": noop["operations"],
    }


def main():
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--screen-pool", required=True, type=Path)
    parser.add_argument("--screen-receipt", required=True, type=Path)
    parser.add_argument("--top", default=comparison.TOP)
    parser.add_argument("--routing-config", type=Path, help="native design or platform FastRoute Tcl")
    parser.add_argument("--helper-source", type=Path, action="append", default=[],
                        help="extra source dependency to bind for a generic STA or SEC wrapper")
    parser.add_argument("--pool-order", choices=("legacy-first", "screened-first"), default="legacy-first")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--hold-aware-only", action="store_true",
                       help="run only screened FAECO with per-view relative hold split deferral")
    scope.add_argument("--screened-hold-aware", action="store_true",
                       help="compare single, fixed and hold-aware FAECO on the same screened pool")
    scope.add_argument("--screened-risk-pair", action="store_true",
                       help="compare fixed and FAECO with one incident-capacitance reorder after hold rejection")
    parser.add_argument("--wall-limit-seconds", type=float, default=720.0)
    parser.add_argument("--target-area-pct", type=float, default=0.01)
    args = comparison.prepare_args(parser, parser.parse_args())
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.top):
        parser.error("top must be a Verilog identifier")
    if args.prepare_only or args.probe_only:
        parser.error("the comparison must evaluate candidate arms")
    if not all(math.isfinite(x) and x > 0 for x in (args.wall_limit_seconds, args.target_area_pct)):
        parser.error("wall window and area target must be finite and positive")
    if not hasattr(time, CLOCK_NAME):
        parser.error("this matrix requires CLOCK_MONOTONIC_RAW")
    args.pool_order, args.methods, args.defer_split_reasons = comparison_arms(args)
    try:
        args.screen_pool, args.screen_receipt = (p.resolve(strict=True) for p in (args.screen_pool, args.screen_receipt))
        if args.routing_config is not None:
            args.routing_config = args.routing_config.resolve(strict=True)
        args.screen_bindings, args.screen_seconds = bind_screen_inputs(args)
        args.incident_ranking = None
        if args.screened_risk_pair:
            start = raw_seconds()
            candidate_actions = [comparison.PhysicalAction(**row) for row in read(args.screen_pool)]
            args.incident_ranking = build_incident_priority(
                args.control_dir / "6_final.def", args.control_dir / "6_final.spef", candidate_actions,
            )
            args.incident_ranking["raw_seconds"] = raw_seconds() - start
        args.clock_period_ps = sweep.policy.original_period_ps(read(args.views_json), args.original_sdc)
        setup_budget = sweep.policy.setup_budget_ps(args.clock_period_ps, BUDGET_PCT)
        added_sources = (Path(__file__), Path(sweep.__file__), Path(sweep.policy.__file__),
                         *((Path(build_incident_priority.__code__.co_filename),) if args.incident_ranking else ()),
                         *(path.resolve(strict=True) for path in args.helper_source))
        if len({path.name for path in added_sources}) != len(added_sources):
            raise ValueError("driver dependencies must have distinct basenames")
        with bind_runtime(args.top, args.routing_config):
            return comparison.run(args, matched_runner=run_matrix, config_overrides={
                "pool_order": args.pool_order, "clock": CLOCK_NAME,
                "methods_in_run_order": args.methods,
                "split_deferral_reasons": sorted(args.defer_split_reasons),
                "cpu_affinity": sorted(os.sched_getaffinity(0)),
                "clock_resolution_seconds": time.clock_getres(time.CLOCK_MONOTONIC_RAW),
                "setup_budget_ps_per_view": setup_budget, "primary_budget_pct": BUDGET_PCT,
                "original_clock_period_ps": args.clock_period_ps, "primary_mode": "tradeoff",
                "primary_wall_limit_seconds": args.wall_limit_seconds, "primary_target_area_pct": args.target_area_pct,
                "tns_gate": True, "setup_tns_loss_budget": "max(10 * B_WNS, clock ratio * abs(reference TNS)) per view",
                "final_budget_slot": "terminal top-level dispatch is a singleton; an in-flight bisection can use two edits",
                "screen_inputs": args.screen_bindings, "charged_screening_seconds": args.screen_seconds,
                "screening_cost_model": "one measured full scan charged to each screened arm",
                **({"incident_ranking": args.incident_ranking} if args.incident_ranking else {}),
                "shared_preflight_cost_in_arms": False,
            }, extra_sources=added_sources)
    except (comparison.TrialFailure, OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
