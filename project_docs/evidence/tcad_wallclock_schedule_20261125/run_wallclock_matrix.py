#!/usr/bin/env python3
"""Run four schedulers in a paired forward/reverse RAW wall-clock matrix."""

from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import asdict
from inspect import signature
import math
import os
from pathlib import Path
import socket
import sys
from types import SimpleNamespace


EVIDENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVIDENCE / "tcad_holdout_20261123"))
sys.path.insert(0, str(EVIDENCE / "tcad_ibex_20261123"))

import run_aes_incident_priority_matched as matched
import run_aes_sensitivity_greedy as sensitivity
from run_aes_greedy_matched import run_online_arm
from run_aes_protected_online import LIMIT_SECONDS
from run_screened_matrix import assert_screen_inputs, bind_runtime, bind_screen_inputs, raw_seconds
from run_uart_online import UartComparison, comparison, read, verify
from run_uart_rejection_dedup import run_variant, seed_args


FORWARD = ("fixed_online", "single_sensitivity", "faeco_dedup", "faeco_interleave_dedup")
TARGETS_PCT = (0.01, 0.15, 0.25)


def ordering():
    return {"forward": FORWARD, "reverse": FORWARD[::-1]}


def exhaustion_sentinel(pool):
    """Legacy single/fixed always consume an unvisited action per request."""
    return len(pool) + 1


@contextmanager
def wall_dispatch(runner, variant):
    original_cap = matched.MAX_REQUESTS
    original_method = comparison.run_method
    original_adaptive = comparison.adaptive_batch_recovery

    def baselines(name, reference, pool, evaluate, budget, width, **kwargs):
        if budget is not None or name not in ("fixed", "single"):
            raise ValueError("expected one uncapped fixed or single-gate baseline")
        if name == "single":
            ranking = sensitivity.score_control(runner, pool, runner.output / name / "sensitivity")
            indexed = {action.action_id: action for action in pool}
            pool = [indexed[action_id] for action_id in ranking["ordered_action_ids"]]
        return original_method(name, reference, pool, evaluate, exhaustion_sentinel(pool), width, **kwargs)

    def adaptive(*args, **kwargs):
        if kwargs["max_evaluations"] is not None:
            raise ValueError("expected an uncapped adaptive scheduler")
        return original_adaptive(
            *args, **kwargs, interleave_failed_splits=variant == "faeco_interleave_dedup",
        )

    try:
        # The reused arm owns the deadline and subprocess ledger. Only replace
        # dispatch here, leaving diagnosis, physical acceptance, and costs shared.
        matched.MAX_REQUESTS = None
        comparison.run_method = baselines
        comparison.adaptive_batch_recovery = adaptive
        yield
    finally:
        comparison.adaptive_batch_recovery = original_adaptive
        comparison.run_method = original_method
        matched.MAX_REQUESTS = original_cap


def run_strategy(runner, strategy, reference):
    with wall_dispatch(runner, strategy):
        if strategy == "fixed_online":
            return run_online_arm(runner, "fixed", reference), 0
        if strategy == "single_sensitivity":
            return run_online_arm(runner, "single", reference), 0
        if strategy in ("faeco_dedup", "faeco_interleave_dedup"):
            return run_variant(runner, reference)
    raise ValueError(f"unknown strategy {strategy}")


def target_hits(reference, checkpoints):
    accepted = [
        (row["elapsed_seconds"], reference.area - row["endpoint"]["area"], row["endpoint"]["evidence_id"])
        for row in checkpoints
        if row["accepted"] and row["elapsed_seconds"] <= LIMIT_SECONDS
    ]
    targets = {}
    for pct in TARGETS_PCT:
        need = reference.area * pct / 100
        first = next(((wall, area, evidence) for wall, area, evidence in accepted if area >= need - 1e-9), None)
        targets[str(pct)] = {
            "required_area": need,
            "time_raw_seconds": first[0] if first else None,
            "first_realized_area": first[1] if first else None,
            "endpoint": first[2] if first else None,
        }
    return targets


def audit_tools(ledger):
    names = {
        "sta_rank.log": "ranking_sta", "preview.log": "preview_drc", "route.log": "drt_rcx",
        "sta_FF.log": "candidate_sta", "sta_TT.log": "candidate_sta", "sta_SS.log": "candidate_sta",
        "audit.log": "independent_drc", "sec.log": "sec",
    }
    tools = {stage: {"started": 0, "completed_zero_rc": 0, "wall_timeout": 0, "stage_timeout": 0,
                     "other_nonzero_rc": 0, "tool_wall_seconds": 0.0} for stage in (*sorted(set(names.values())), "other")}
    for entry in ledger:
        stage = tools[names.get(Path(entry["log"]).name, "other")]
        stage["started"] += 1
        stage["tool_wall_seconds"] += entry.get("wall_seconds", 0.0)
        code = entry.get("returncode")
        if code == 0:
            stage["completed_zero_rc"] += 1
        elif code is not None:
            stage["other_nonzero_rc"] += 1
        elif "returncode" in entry:
            stage[f'{entry["timeout_bound"]}_timeout'] += 1
    return tools


def run_matrix(runner, reference, output, config):
    results = []
    state = output / "status.json"
    config_ref = comparison.bind(output / "protocol.json")
    comparison.save(output / "reference.json", asdict(reference))
    for direction, methods in ordering().items():
        for strategy in methods:
            cell = len(results) + 1
            runner.output = output / f"cell_{cell:02d}"
            runner.output.mkdir()
            comparison.save(state, {"status": "running", "cell": cell, "direction": direction, "strategy": strategy,
                                    "completed_arms": len(results), "start_raw": raw_seconds()})
            print(f"{direction} cell {cell} {strategy}", flush=True)
            summary, reused = run_strategy(runner, strategy, reference)
            arm = runner.output / summary["method"]
            progress_path = arm / "progress.json"
            progress = read(progress_path)
            targets = target_hits(reference, progress["checkpoints"])
            reported = summary["window"]["time_to_target_seconds"]
            if targets["0.01"]["time_raw_seconds"] != reported:
                raise ValueError("recomputed 0.01% first hit differs from the original window ledger")
            if summary["stop_reason"] == "logical_cap_or_pool_exhausted":
                stop = "natural_scheduler_exhaustion"
            else:
                stop = summary["stop_reason"]
            ledger_path = arm / "subprocesses.json"
            assert_screen_inputs(config["screen_input"])
            for source in config["sources"].values():
                verify(source)
            row = {
                "cell": cell, "direction": direction, "strategy": strategy,
                "status": stop, "binding": config_ref, "summary": comparison.bind(arm / "summary.json"),
                "progress": comparison.bind(progress_path),
                "tool_ledger": comparison.bind(ledger_path) if ledger_path.exists() else None,
                "window_targets_pct": targets, "reused_setup_only_rejections": reused,
                "stage_costs": audit_tools(read(ledger_path) if ledger_path.exists() else []),
                "charged_screening_seconds": runner.screen, "result": summary,
            }
            comparison.save(runner.output / "arm.json", row)
            results.append(row)
            comparison.save(output / "results.json", results)
            print(f"{direction} cell {cell} area={summary['window']['area_saved']:.6f} stop={stop}", flush=True)
    comparison.save(state, {"status": "complete", "completed_arms": len(results), "stop_raw": raw_seconds()})


def prepare_uart(source_run, output):
    source = source_run / "protocol.json"
    previous = read(source)
    seed_path = verify(previous["seed"])
    seed = read(seed_path)
    args = seed_args(seed, previous)
    screen_receipt = verify(previous["screen_input"]["receipt"])
    bindings, seconds = bind_screen_inputs(SimpleNamespace(**vars(args), top="uart", screen_receipt=screen_receipt))
    if bindings != previous["screen_input"] or not math.isclose(
        seconds, previous["charged_screening_seconds_per_arm"], rel_tol=0, abs_tol=1e-12,
    ):
        raise ValueError("shared screen results or their measured cost disagree with the original experiment")
    with bind_runtime("uart", verify(seed["bindings"]["flow"]["fastroute.tcl"])):
        runner = UartComparison(args, seed_path.parent, output, bindings, seconds)
    if [asdict(action) for action in runner.pool] != previous["ordered_pool"]:
        raise ValueError("reconstructed pool differs from the frozen ordered actions")
    # Validate name grammar and inventory inputs before running timed ranking.
    sensitivity.render_rank_tcl(runner.eval.libraries["TT"], runner.eval.control, runner.pool)
    return runner, source


def preregister(runner, source, output):
    sources = {
        Path(__file__),
        *(verify(entry) for entry in runner.config["sources"].values()),
        *(Path(func.__code__.co_filename) for func in (
            run_online_arm, sensitivity.score_control, matched.IncidentPriorityComparison.arm,
            comparison.run_method, comparison.adaptive_batch_recovery, run_variant, seed_args,
            bind_screen_inputs, verify,
        )),
    }
    frozen = output / "producer_sources"
    frozen.mkdir()
    for path in sorted(sources):
        reference = comparison.bind(path)
        runner.config["sources"][path.name] = reference
        (frozen / path.name).write_bytes(verify(reference).read_bytes())
    runner.config.update({
        "source_protocol": comparison.bind(source), "order": ordering(),
        "logical_dispatch_cap": None, "wall_window_seconds_including_screen": LIMIT_SECONDS,
        "legacy_baseline_exhaustion_sentinel": exhaustion_sentinel(runner.pool),
        "charged_screening_method": "reuse one frozen screened pool and charge its measured RAW cost equally per arm",
        "single_sensitivity_rule": sensitivity.RANK_RULE,
        "single_sensitivity_cost": "fresh TT CONTROL ranking STA in each single-gate arm window",
        "faeco_order_rule": "reuse existing relative-hold defer and incident-cap priority; charge live preparation",
        "faeco_reuse_rule": "same-arm completed, three-view, independent-DRC-clean setup-only rejection",
        "interleave_rule": "one immediate left split before trying the next fresh batch; queue remaining subgroups",
        "area_targets_pct": TARGETS_PCT, "host": socket.gethostname(),
        "cpu_affinity": sorted(os.sched_getaffinity(0)), "sequential_same_process": True,
        "shared_zero": "fresh precondition outside the strategy windows; retain separate ledger",
    })
    comparison.save(output / "protocol.json", runner.config)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path, help="qualified UART online run root containing protocol.json")
    parser.add_argument("output", type=Path, help="fresh output directory")
    parser.add_argument("--validate-only", action="store_true", help="validate frozen inputs without tools or timing")
    ns = parser.parse_args()
    if "interleave_failed_splits" not in signature(comparison.adaptive_batch_recovery).parameters:
        parser.error("the opt-in wall-clock scheduler is unavailable on this checkout")
    source_run, output = ns.source_run.resolve(strict=True), ns.output.resolve()
    output.mkdir(parents=True)
    try:
        runner, source = prepare_uart(source_run, output)
        preregister(runner, source, output)
        print(f"Bound {len(runner.pool)} candidates; charge {runner.screen:.9f} RAW s shared screening", flush=True)
        if ns.validate_only:
            comparison.save(output / "status.json", {"status": "protocol_and_inputs_validated", "completed_arms": 0})
            return
        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            reference = runner.qualify_zero()
            run_matrix(runner, reference, output, runner.config)
    except Exception as error:
        status_path = output / "status.json"
        prior = read(status_path) if status_path.exists() else {}
        comparison.save(status_path, {**prior, "status": "failed", "error": str(error), "stop_raw": raw_seconds()})
        raise


if __name__ == "__main__":
    main()
