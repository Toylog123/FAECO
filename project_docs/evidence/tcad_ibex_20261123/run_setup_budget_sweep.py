#!/usr/bin/env python3
"""Run independent primary Ibex searches and cached diagnostics over timing budgets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import json
import math
from pathlib import Path
import sys
import time

import compare_ibex as comparison
import setup_budget as policy


DEFAULT_BUDGET_PCTS = (0.0, 0.5, 1.0)
WALL_LIMIT_SECONDS = {"asap7": 1200.0, "sky130hd": 720.0}
MODES = {"protect": True, "tradeoff": False}


@dataclass(frozen=True)
class BudgetGate:
    wns_ps: float
    tns_ps_by_view: dict[str, float]
    protect_clean: bool


def budget_gate(evaluator, pct: float, protect_clean: bool) -> BudgetGate:
    period = evaluator.args.clock_period_ps
    return BudgetGate(
        policy.setup_budget_ps(period, pct),
        {
            corner: policy.setup_tns_budget_ps(period, pct, view["setup_tns_ps"])
            for corner, view in evaluator.ref_views.items()
        },
        protect_clean,
    )


@dataclass
class PhysicalTrial:
    actions: tuple[str, ...]
    endpoint: comparison.Endpoint
    receipt: dict
    directory: Path
    proof_passed: bool | None = None
    proof_failures: list[str] = field(default_factory=list)
    proof_operations: dict = field(default_factory=dict)
    proof_seconds: float = 0.0


def operation_counts(receipt: dict) -> dict[str, int]:
    operations = receipt["operations"]
    return {
        "route_attempts": int("DRT_RCX" in operations),
        "drt_completions": int(receipt.get("routed_to_completion", False)),
        "rcx_completions": int(receipt.get("extracted_to_completion", False)),
        "view_sta_attempts": sum(f"STA_{corner}" in operations for corner in comparison.CORNERS),
        "sec_attempts": int("SEC" in operations),
    }


class TrialCache:
    """Run fresh primary evaluations and share exact measurements during diagnostic replay."""

    def __init__(self, evaluator: comparison.Evaluator):
        self.evaluator = evaluator
        self.directory = evaluator.args.out / "physical"
        self.directory.mkdir()
        self.trials: dict[tuple[str, ...], PhysicalTrial] = {}
        self.measurements: list[PhysicalTrial] = []
        self.requests = 0
        self.cache_hits = 0

    def _prove(self, trial: PhysicalTrial) -> None:
        start = time.monotonic()
        bound_artifacts = trial.receipt["artifacts"]
        candidate = Path(bound_artifacts["v"]["path"])
        try:
            if any(comparison.bind(Path(item["path"])) != item for item in bound_artifacts.values()):
                raise comparison.TrialFailure("cached physical artifact changed before SEC")
            trial.proof_passed = self.evaluator.proof(candidate, trial.directory, trial.proof_operations)
            if not trial.proof_passed:
                trial.proof_failures.append("sec")
        except (comparison.TrialFailure, OSError, ValueError) as error:
            trial.proof_passed = False
            trial.proof_failures.extend(("sec", str(error)))
        proof_time = trial.proof_operations.get("SEC", {}).get("wall_seconds")
        trial.proof_seconds = time.monotonic() - start if proof_time is None else proof_time
        comparison.save(trial.directory / "deferred_proof.json", {
            "endpoint_id": trial.receipt["endpoint_id"],
            "candidate": bound_artifacts["v"],
            "sec_pass": trial.proof_passed,
            "failures": trial.proof_failures,
            "operations": trial.proof_operations,
            "wall_seconds": trial.proof_seconds,
        })

    def request(
        self, actions: tuple[str, ...], gate: BudgetGate, *, fresh_directory: Path | None = None,
    ) -> tuple[comparison.Endpoint, dict]:
        self.requests += 1
        cached = fresh_directory is None and actions in self.trials
        if cached:
            self.cache_hits += 1
            trial = self.trials[actions]
        else:
            directory = fresh_directory or self.directory / f"{len(self.measurements) + 1:04d}"
            endpoint, receipt = self.evaluator.evaluate(actions, directory, envelope_only=True)
            trial = PhysicalTrial(actions, endpoint, receipt, directory)
            self.measurements.append(trial)
            # Primary duplicates are measured independently. Diagnostics start from the
            # first complete receipt for the tuple, never the best of later repeats.
            if fresh_directory is None or (
                receipt.get("routed_to_completion", False)
                and receipt.get("extracted_to_completion", False)
                and set(receipt["views"]) == set(comparison.CORNERS)
            ):
                self.trials.setdefault(actions, trial)
        failures = list(trial.receipt["failures"])
        views = trial.receipt["views"]
        if set(views) == set(comparison.CORNERS):
            for corner in comparison.CORNERS:
                failures.extend(policy.setup_gate_failures(
                    corner, self.evaluator.ref_views[corner]["setup_wns_ps"],
                    views[corner]["setup_wns_ps"], gate.wns_ps, comparison.PS_TOLERANCE,
                    protect_clean=gate.protect_clean,
                ))
                failures.extend(policy.tns_gate_failures(
                    corner, self.evaluator.ref_views[corner]["setup_tns_ps"],
                    views[corner]["setup_tns_ps"], gate.tns_ps_by_view[corner], comparison.PS_TOLERANCE,
                ))
        elif not failures:
            failures.append("incomplete_sta_views")
        if not trial.endpoint.valid and not failures:
            failures.append("invalid_physical_endpoint")

        proof_required = not failures
        if proof_required:
            if trial.proof_passed is None:
                self._prove(trial)
            failures.extend(trial.proof_failures)
        passed = proof_required and trial.proof_passed is True
        endpoint = replace(trial.endpoint, valid=passed, sec_pass=passed)
        seconds = trial.receipt["wall_seconds"] + (trial.proof_seconds if proof_required else 0.0)
        return endpoint, {
            "endpoint": asdict(endpoint),
            "actions": list(actions),
            "physical_receipt": str(trial.directory / "receipt.json"),
            "from_physical_cache": cached,
            "failures": failures,
            "wall_seconds": seconds,
            "wall_seconds_basis": "charged physical evaluation plus SEC when required",
            "setup_wns_ps": {corner: values["setup_wns_ps"] for corner, values in views.items()},
            "setup_tns_ps": {corner: values["setup_tns_ps"] for corner, values in views.items()},
            "deferred_proof_receipt": str(trial.directory / "deferred_proof.json") if proof_required else None,
        }

    def totals(self) -> dict:
        return {
            **trial_totals(self.measurements),
            "logical_requests": self.requests,
            "physical_cache_hits": self.cache_hits,
        }


def trial_totals(trials: list[PhysicalTrial]) -> dict:
    totals = dict.fromkeys(
        ("route_attempts", "drt_completions", "rcx_completions", "view_sta_attempts"), 0,
    )
    for trial in trials:
        counts = operation_counts(trial.receipt)
        for name in totals:
            totals[name] += counts[name]
    return {
        **totals,
        "measured_endpoints": len(trials),
        "distinct_action_tuples": len({trial.actions for trial in trials}),
        "sec_attempts": sum("SEC" in trial.proof_operations for trial in trials),
        "actual_evaluation_seconds": sum(
            trial.receipt["wall_seconds"] + trial.proof_seconds for trial in trials
        ),
    }


def summarize_wall_window(reference, checkpoints, *, wall_limit_seconds: float, target_area_pct: float) -> dict:
    target_area = reference.area * (target_area_pct / 100)
    selected = asdict(reference)
    hit = None
    completed = 0
    for checkpoint in checkpoints:
        elapsed = checkpoint["elapsed_seconds"]
        if elapsed > wall_limit_seconds:
            break
        completed += 1
        if checkpoint["accepted"]:
            selected = checkpoint["endpoint"]
            if hit is None and reference.area - selected["area"] >= target_area - 1e-9:
                hit = elapsed
    return {
        "wall_limit_seconds": wall_limit_seconds,
        "completed_attempts": completed,
        "selected": selected,
        "area_saved": reference.area - selected["area"],
        "area_saved_pct": 100 * (reference.area - selected["area"]) / reference.area,
        "target_area_pct": target_area_pct,
        "target_area_saved": target_area,
        "time_to_target_seconds": hit,
        "target_reached_in_window": hit is not None,
    }


def run_arm(
    args, cache, reference, pool, method, gate, arm, *, primary: bool,
    defer_split_reasons: frozenset[str] = frozenset(),
):
    arm.mkdir()
    attempts = []
    elapsed = []
    before = len(cache.measurements)
    scheduler_policy = comparison.BudgetPolicy.from_ps(
        gate.wns_ps, tolerance_ns=comparison.PS_TOLERANCE / 1000,
    )

    def evaluate(actions):
        seq = len(attempts) + 1
        print(f"{arm.parent.name} {method} attempt {seq}/{args.max_evals} edits={len(actions)}", flush=True)
        fresh = arm / f"{seq:02d}_physical" if primary else None
        endpoint, receipt = cache.request(actions, gate, fresh_directory=fresh)
        attempts.append(receipt)
        comparison.save(arm / f"{seq:02d}.json", receipt)
        print(f"{arm.parent.name} {method} {seq:02d} {receipt['failures'] or 'passed gates'}", flush=True)
        if primary:
            elapsed.append(time.monotonic() - start)
        return endpoint

    def defer_split_for(actions):
        last = attempts[-1]
        if tuple(last["actions"]) != actions:
            raise comparison.TrialFailure("split decision does not match the latest physical receipt")
        return not defer_split_reasons.isdisjoint(last["failures"])

    start = time.monotonic()
    result = comparison.run_method(
        method, reference, pool, evaluate, args.max_evals, args.batch_size, policy=scheduler_policy,
        defer_split_for=defer_split_for if defer_split_reasons else None,
    )
    total_wall = time.monotonic() - start
    result["selected"] = asdict(result["selected"])
    result["area_saved"] = reference.area - result["selected"]["area"]
    result["attempt_receipts"] = [str(arm / f"{seq:02d}.json") for seq in range(1, len(attempts) + 1)]
    result["operations"] = trial_totals(cache.measurements[before:])
    if primary:
        checkpoints = [
            {"elapsed_seconds": end, "accepted": decision["accepted"], "endpoint": attempt["endpoint"]}
            for end, decision, attempt in zip(elapsed, result["trace"], attempts, strict=True)
        ]
        result["wall_seconds"] = total_wall
        result["checkpoints"] = checkpoints
        result["wall_window"] = summarize_wall_window(
            reference, checkpoints, wall_limit_seconds=args.wall_limit_seconds, target_area_pct=args.target_area_pct,
        )
    else:
        result["charged_evaluation_seconds"] = sum(item["wall_seconds"] for item in attempts)
    comparison.save(arm / "summary.json", result)
    return result, attempts


def gate_summary(gate, ref_views):
    return {
        "budget_ps": gate.wns_ps,
        "protect_clean_setup_views": gate.protect_clean,
        "setup_floor_ps_by_view": {
            corner: policy.setup_threshold_ps(
                view["setup_wns_ps"], gate.wns_ps, protect_clean=gate.protect_clean,
            )
            for corner, view in ref_views.items()
        },
        "setup_tns_budget_ps_by_view": gate.tns_ps_by_view,
    }


def run_sweep(args, evaluator, reference, pool, baseline_record, noop):
    cache = TrialCache(evaluator)
    budgets = {}
    progress = args.out / "sweep_progress.json"
    complete = True
    primary_gate = budget_gate(evaluator, args.primary_budget_pct, False)
    primary_directory = args.out / f"primary_tradeoff_{args.primary_budget_pct:g}pct"
    primary_directory.mkdir()
    primary = {
        **gate_summary(primary_gate, evaluator.ref_views),
        "budget_pct": args.primary_budget_pct,
        "mode": "tradeoff",
        "wall_limit_seconds": args.wall_limit_seconds,
        "target_area_pct": args.target_area_pct,
        "results": {},
    }

    def snapshot():
        comparison.save(progress, {
            "primary": primary, "budgets": budgets, "physical_operations": cache.totals(),
        })

    for method in comparison.METHODS:
        result, attempts = run_arm(
            args, cache, reference, pool, method, primary_gate, primary_directory / method, primary=True,
        )
        primary["results"][method] = result
        complete &= result["evaluations_used"] == len(attempts) == args.max_evals
        snapshot()

    for pct in args.budget_pcts:
        key = format(pct, "g")
        directory = args.out / f"budget_{key}pct"
        directory.mkdir()
        budgets[key] = {"budget_pct": pct, "modes": {}}
        for mode, protect_clean in MODES.items():
            gate = budget_gate(evaluator, pct, protect_clean)
            mode_dir = directory / mode
            mode_dir.mkdir()
            results, receipts = {}, {}
            budget = {**gate_summary(gate, evaluator.ref_views), "results": results}
            budgets[key]["modes"][mode] = budget
            for method in comparison.METHODS:
                result, attempts = run_arm(
                    args, cache, reference, pool, method, gate, mode_dir / method, primary=False,
                )
                results[method] = result
                receipts[method] = attempts
                complete &= result["evaluations_used"] == len(attempts) == args.max_evals
                snapshot()
            limit = min(result["charged_evaluation_seconds"] for result in results.values())
            budget["equal_charged_prefix_limit_seconds"] = limit
            budget["equal_charged_prefixes"] = {
                method: comparison.accepted_prefix(reference, result, receipts[method], limit)
                for method, result in results.items()
            }
            snapshot()
    return complete, {
        "clock_period_ps": args.clock_period_ps,
        "primary_budget_pct": args.primary_budget_pct,
        "primary": primary,
        "control": baseline_record,
        "shared_noop": noop,
        "physical_operations": cache.totals(),
        "control_operations": operation_counts(baseline_record),
        "shared_noop_operations": operation_counts(noop),
        "budgets": budgets,
    }


def main() -> int:
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--budget-pct", type=float, action="append", help="repeat to override the default grid; include 0")
    parser.add_argument("--primary-budget-pct", type=float, default=1.0)
    parser.add_argument("--wall-limit-seconds", type=float)
    parser.add_argument("--target-area-pct", type=float, default=0.01)
    args = comparison.prepare_args(parser, parser.parse_args())
    values = tuple(args.budget_pct) if args.budget_pct is not None else DEFAULT_BUDGET_PCTS
    if 0.0 not in values or args.primary_budget_pct not in values or len(set(values)) != len(values):
        parser.error("budget percentages must be unique and include 0 and the primary budget")
    if args.wall_limit_seconds is None:
        args.wall_limit_seconds = WALL_LIMIT_SECONDS[args.pdk]
    if any(not math.isfinite(x) or x <= 0 for x in (args.wall_limit_seconds, args.target_area_pct)):
        parser.error("wall limit and target area percentage must be finite and positive")
    args.budget_pcts = tuple(sorted(values))
    try:
        qualification = json.loads(args.views_json.read_text(encoding="utf-8"))
        args.clock_period_ps = policy.original_period_ps(qualification, args.original_sdc)
        for pct in args.budget_pcts:
            policy.setup_budget_ps(args.clock_period_ps, pct)
        return comparison.run(args, matched_runner=run_sweep, config_overrides={
            "setup_budget_ps_per_view": None,
            "setup_budget_percent_of_clock": args.budget_pcts,
            "original_clock_period_ps": args.clock_period_ps,
            "protect_clean_setup_views": "diagnostic protect arm",
            "setup_tns_loss_budget": "max(10 * B_WNS, clock ratio * abs(reference TNS)) per view",
            "primary_budget_pct": args.primary_budget_pct,
            "primary_mode": "tradeoff",
            "primary_wall_limit_seconds": args.wall_limit_seconds,
            "primary_target_area_pct": args.target_area_pct,
            "no_op_setup_budget_ps": comparison.POLICY.wns_budget_ns * 1000,
            "cached_physical_trials": "diagnostics only; run-local first complete primary or diagnostic exact tuple",
            "time_comparison": "independent monotonic wall time in primary; charged evaluation-equivalent seconds in diagnostics",
        }, extra_sources=(Path(__file__), Path(policy.__file__)))
    except (comparison.TrialFailure, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
