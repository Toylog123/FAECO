#!/usr/bin/env python3
"""Run rank-aligned 6-arm (fixed_online, single_sensitivity, faeco_dedup, forward/reverse) wall-clock holdout on asap7/aes."""

from contextlib import ExitStack, contextmanager
from pathlib import Path
import sys

SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(SCRIPT.parents[1] / "tcad_wallclock_schedule_20261125"))
import run_qualified_wallclock as qualified

matrix, comparison, read, verify = qualified.matrix, qualified.comparison, qualified.read, qualified.verify


@contextmanager
def install(owner, name, handler):
    original = getattr(owner, name)
    setattr(owner, name, handler)
    try:
        yield
    finally:
        setattr(owner, name, original)


def run_aligned_strategy(runner, strategy, reference, expected_box, native_strategy):
    native_score = matrix.sensitivity.score_control
    native_fixed = comparison.run_method
    native_adaptive = comparison.adaptive_batch_recovery
    count = 0

    def fresh_score(active_runner, pool, out):
        nonlocal count
        row = native_score(active_runner, pool, out)
        order = row["ordered_action_ids"]
        if len(order) != len(pool):
            raise ValueError("fresh sensitivity rank size mismatch")
        if expected_box["order"] is None:
            expected_box["order"] = list(order)
        elif order != expected_box["order"]:
            raise ValueError("fresh rank order drifted between arms")
        count += 1
        return row

    def aligned_pool(pool, method):
        ranking = fresh_score(runner, pool, runner.output / method / "sensitivity")
        by_id = {item.action_id: item for item in pool}
        return [by_id[key] for key in ranking["ordered_action_ids"]]

    def aligned_fixed(name, ref, pool, evaluate, cap, width, **kwargs):
        return native_fixed(name, ref, aligned_pool(pool, "fixed"), evaluate, cap, width, **kwargs)

    def aligned_adaptive(ref, pool, evaluate, policy, **kwargs):
        return native_adaptive(ref, aligned_pool(pool, "faeco"), evaluate, policy, **kwargs)

    with ExitStack() as scope:
        if strategy == "fixed_online":
            scope.enter_context(install(comparison, "run_method", aligned_fixed))
        elif strategy == "single_sensitivity":
            scope.enter_context(install(matrix.sensitivity, "score_control", fresh_score))
        elif strategy == "faeco_dedup":
            scope.enter_context(install(comparison, "adaptive_batch_recovery", aligned_adaptive))
        else:
            raise ValueError(f"unexpected strategy {strategy}")
        outcome = native_strategy(runner, strategy, reference)
    if count != 1:
        raise ValueError(f"expected exactly 1 fresh timed sensitivity rank in {strategy}, got {count}")
    return outcome


def main():
    expected_box = {"order": None}
    native_register = matrix.preregister
    native_strategy = matrix.run_strategy

    def register(runner, source, output):
        runner.config["rank_alignment_rule"] = (
            "Independent holdout rank-aligned comparison: every arm executes a fresh timed TT sensitivity rank "
            "inside its 720 RAW s window and verifies identical ordering across all 6 arms."
        )
        runner.config["sources"][SCRIPT.name] = comparison.bind(SCRIPT)
        native_register(runner, source, output)

    def strategy(runner, method, reference):
        return run_aligned_strategy(runner, method, reference, expected_box, native_strategy)

    if "--confirmed-only" not in sys.argv:
        sys.argv.append("--confirmed-only")
    with install(matrix, "preregister", register), install(matrix, "run_strategy", strategy):
        return qualified.main()


if __name__ == "__main__":
    raise SystemExit(main())
