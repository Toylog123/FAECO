#!/usr/bin/env python3
"""Compare three riscv32i schedulers from one freshly checked sensitivity rank."""

from argparse import ArgumentParser
from contextlib import ExitStack, contextmanager
from pathlib import Path
import os
import sys


SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(SCRIPT.parents[1] / "tcad_wallclock_schedule_20261125"))
import run_qualified_wallclock as qualified


matrix, comparison, read, verify = qualified.matrix, qualified.comparison, qualified.read, qualified.verify
TARGETS_UM2 = (26.2752, 45.0432, 52.5504, 57.5552)
V2_PROTOCOL_SHA = "a768316f012f7386c2c1d31e43829b9490c0da82174ab884dc3b6634ea5f2dae"
V2_VERIFICATION_SHA = "ef949a66f62d5645ddbef1876e338484ecededbe0896b2efba467ca09814ed04"
V2_RANK_SHA = (
    "200b402d5af592a794c05984524d6429a8ef8f61397bd2cfac8d4aa9f5a58bf0",
    "81aadfe74626094efd2ba7fa32a2797d6ff509804df19d63917df05305a4c4a3",
)


@contextmanager
def install(owner, name, handler):
    original = getattr(owner, name)
    setattr(owner, name, handler)
    try:
        yield
    finally:
        setattr(owner, name, original)


def load_rank_source(root):
    protocol_ref = comparison.bind(root / "protocol.json")
    verification_ref = comparison.bind(root / "independent_verification.json")
    if protocol_ref["sha256"] != V2_PROTOCOL_SHA or verification_ref["sha256"] != V2_VERIFICATION_SHA:
        raise ValueError("rank source does not match the verified original riscv32i v2 matrix")
    assurance = read(verify(verification_ref))
    protocol = read(verify(protocol_ref))
    seed = read(verify(protocol["seed"]))
    if assurance["protocol"] != protocol_ref or assurance["verified_prefix"] != 6 or seed["top"] != "riscv":
        raise ValueError("source is not the independently verified six-arm riscv matrix")
    ranks = [
        comparison.bind(root / f"cell_{cell:02d}" / "single/sensitivity/ranking.json")
        for cell in (2, 5)
    ]
    if tuple(item["sha256"] for item in ranks) != V2_RANK_SHA:
        raise ValueError("reference ranking receipts changed")
    forward, reverse = (read(verify(item)) for item in ranks)
    expected = forward["ordered_action_ids"]
    pool_ids = {item["action_id"] for item in protocol["ordered_pool"]}
    if (expected != reverse["ordered_action_ids"] or len(expected) != 18 or set(expected) != pool_ids
            or forward["unconstrained_tail_action_ids"] != reverse["unconstrained_tail_action_ids"]
            or len(forward["unconstrained_tail_action_ids"]) != 3):
        raise ValueError("reference orders do not bind the same 18 actions and three +Inf tail actions")
    return protocol, seed, {
        "rank_alignment_source": ranks[0], "rank_alignment_source_reverse": ranks[1],
        "rank_alignment_source_run": protocol_ref, "rank_alignment_source_verification": verification_ref,
        "rank_aligned_action_ids": expected, "rank_aligned_plus_inf_tail": forward["unconstrained_tail_action_ids"],
        "rank_alignment_rule": "fresh timed TT ranking in every arm; exact frozen order match before dispatch",
        "rank_alignment_absolute_targets_um2": TARGETS_UM2,
    }


def require_same_inputs(args, prepared, protocol, seed):
    _, assets, clock = prepared
    old = seed["bindings"]
    if any(assets[key] != old[key] for key in (
        "control", "control_drc", "original_sdc", "qualification_receipt", "source_libraries", "tools",
    )) or assets["routing_config"] != old["flow"]["fastroute.tcl"]:
        raise ValueError("phase 2 changed qualified physical, timing or tool inputs")
    same_resources = (
        args.top == seed["top"] and args.pdk == seed["pdk"] and args.confirmed_only
        and args.embedded_guides and args.single_pin_access and args.route_mode == seed["route_mode"]
        and args.threads == seed["methods_route_threads"] == 4
        and args.droute_iters == seed["route_drt_iters"] == 64
        and args.route_timeout == seed["route_timeout_seconds"] == 240
        and args.sta_timeout == seed["sta_timeout_seconds_per_view"] == 180
        and args.sec_timeout == seed["sec_timeout_seconds"] == 210
        and args.batch_size == seed["batch_size"] == 3
        and sorted(os.sched_getaffinity(0)) == protocol["cpu_affinity"] == list(range(6))
        and clock == protocol["period_basis"]
    )
    if not same_resources:
        raise ValueError("phase 2 changed scope, hardware or physical stage limits")
    bindings, cost = qualified.bind_screen_inputs(args)
    if bindings != protocol["screen_input"] or cost != protocol["charged_screening_seconds_per_arm"]:
        raise ValueError("phase 2 changed screening results or cost")


def run_aligned_strategy(runner, strategy, reference, expected, native_strategy):
    native_score = matrix.sensitivity.score_control
    native_fixed = comparison.run_method
    native_adaptive = comparison.adaptive_batch_recovery
    count = 0

    def fresh_score(active_runner, pool, out):
        nonlocal count
        row = native_score(active_runner, pool, out)
        if row["ordered_action_ids"] != expected or len(pool) != len(expected):
            raise ValueError("fresh rank disagrees with the frozen v2 order")
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
            raise ValueError(f"unexpected rank-aligned strategy {strategy}")
        outcome = native_strategy(runner, strategy, reference)
    if count != 1:
        raise ValueError("each arm must complete exactly one fresh timed rank")
    return outcome


@contextmanager
def rank_alignment(protocol, seed, alignment):
    native_prepare = qualified.prepare_binding
    native_register = matrix.preregister
    native_strategy = matrix.run_strategy

    def prepare(args):
        prepared = native_prepare(args)
        require_same_inputs(args, prepared, protocol, seed)
        comparison.save(args.out / "rank_alignment_inputs.json", {**alignment, "driver": comparison.bind(SCRIPT)})
        return prepared

    def register(runner, source, output):
        if (runner.config["ordered_pool"] != protocol["ordered_pool"] or runner.config["gate"] != protocol["gate"]
                or matrix.ordering() != {key: tuple(items) for key, items in protocol["order"].items()}
                or matrix.LIMIT_SECONDS != protocol["wall_window_seconds_including_screen"]):
            raise ValueError("phase 2 changed the action identities, acceptance gate or wall window")
        runner.config.update(alignment)
        runner.config["sources"][SCRIPT.name] = comparison.bind(SCRIPT)
        native_register(runner, source, output)

    def strategy(runner, method, reference):
        return run_aligned_strategy(runner, method, reference, alignment["rank_aligned_action_ids"], native_strategy)

    with install(qualified, "prepare_binding", prepare), install(
        matrix, "preregister", register,
    ), install(matrix, "run_strategy", strategy):
        yield


def main():
    parser = ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--rank-source-run", type=Path, required=True, help="independently verified original riscv v2 run")
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        parser.print_help()
        comparison.create_parser("Original qualified matrix inputs").print_help()
        return 0
    args, remaining = parser.parse_known_args()
    if any(option in remaining for option in ("--screen-only", "--prepare-only", "--probe-only")):
        parser.error("this wrapper accepts only the matrix and its no-tool validation")
    protocol, seed, alignment = load_rank_source(args.rank_source_run.resolve(strict=True))
    original_argv = sys.argv
    try:
        sys.argv = [*original_argv[:1], *remaining]
        if "--confirmed-only" not in remaining:
            sys.argv.append("--confirmed-only")
        with rank_alignment(protocol, seed, alignment):
            return qualified.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
