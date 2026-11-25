#!/usr/bin/env python3
"""Verify charged endpoints and reproduce dispatch from the measured prefix."""

from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import asdict
from math import inf, isclose
from pathlib import Path

from run_wallclock_matrix import comparison, read, verify
import verify_aes_cold_online as cold
from verify_aes_factorial import accepted_checkpoints
from verify_aes_protected_online import audit_logical, check
from verify_aes_sensitivity_greedy import RANK_LOG, validate_ranking
from verify_uart_rejection_dedup import replay_variant


METHODS = {"fixed_online": "fixed", "single_sensitivity": "single",
           "faeco_dedup": "faeco", "faeco_interleave_dedup": "faeco"}
FORWARD = list(METHODS)
TARGETS_PCT = [0.01, 0.15, 0.25]


@contextmanager
def replay_resources(arm, strategy, assets, views, pool):
    previous_read, previous_online = cold.read, cold.ONLINE
    adaptive = comparison.adaptive_batch_recovery
    ledger = arm / "subprocesses.json"
    tools = read(ledger)
    rank = [tool for tool in tools if Path(tool["log"]) == arm / RANK_LOG]
    check(len(rank) == int(strategy == "single_sensitivity"), "wrong number of ranking invocations")
    ranking = None
    if rank:
        check(rank[0] == tools[0], "ranking did not precede physical requests")
        pool, ranking = validate_ranking(arm, assets, views, pool, rank[0])

    def uncapped(*args, max_evaluations, **kwargs):
        check(max_evaluations == inf, "unexpected replay evaluation limit")
        return adaptive(*args, max_evaluations=None, **kwargs,
                        interleave_failed_splits=strategy == "faeco_interleave_dedup")

    def candidate_ledger(path):
        return tools[1:] if rank and Path(path) == ledger else previous_read(path)

    cold.read = candidate_ledger
    cold.ONLINE = tuple(set(METHODS.values()))
    comparison.adaptive_batch_recovery = uncapped
    try:
        yield pool, tools, ranking
    finally:
        cold.read, cold.ONLINE = previous_read, previous_online
        comparison.adaptive_batch_recovery = adaptive


def audit(root, prefix, confirmed_only=False):
    protocol_path = root / "protocol.json"
    protocol = read(protocol_path)
    forward = FORWARD[:-1] if confirmed_only else FORWARD
    orders = {"forward": forward, "reverse": forward[::-1]}
    check(protocol["order"] == orders and protocol["logical_dispatch_cap"] is None and protocol["batch_size"] == 3
          and protocol["wall_window_seconds_including_screen"] == 720.0
          and protocol["area_targets_pct"] == TARGETS_PCT and protocol["area_target_pct"] == TARGETS_PCT[0],
          "unexpected wall-clock protocol")
    previous = read(verify(protocol["source_protocol"]))
    seed = read(verify(protocol["seed"]))
    assets = seed["bindings"]
    if "qualified_start" in protocol:
        check(protocol["qualified_start"] == protocol["source_protocol"] == assets["qualification_receipt"]
              and (protocol["top"], protocol["pdk"]) == (seed["top"], seed["pdk"])
              and seed["setup_budget_ps_per_view"] == protocol["gate"]["budget_ps"]
              and seed["original_clock_period_ps"] == protocol["period_basis"]["period_ps"],
              "independent holdout qualification or timing budget changed")
        comparison.qualify_binding(previous, assets)
    else:
        for key in ("seed", "reference", "ordered_pool", "screen_input", "charged_screening_seconds_per_arm", "gate",
                    "absolute_hold_ps", "hold_tolerance_ps", "route_threads", "single_pin_access"):
            check(protocol[key] == previous[key], f"physical inputs or gate changed: {key}")
    for source in protocol["sources"].values():
        verify(source)
    for copy in (root / "producer_sources").iterdir():
        check(comparison.bind(copy)["sha256"] == protocol["sources"][copy.name]["sha256"], "source copy differs")
    frozen, views = assets["control"], read(verify(protocol["reference"]))["views"]
    screen = read(verify(protocol["screen_input"]["receipt"]))
    pool_binding = protocol["screen_input"]["pool"]
    check(screen["clock"] == protocol["clock"] == "CLOCK_MONOTONIC_RAW"
          and screen["pool_sha256"] == pool_binding["sha256"] and read(verify(pool_binding)) == protocol["ordered_pool"]
          and screen["wall_seconds"] == protocol["charged_screening_seconds_per_arm"]
          and all(frozen[key]["sha256"] == value for key, value in screen["control_sha256"].items()),
          "screening does not bind the charged cost, input and pool")
    pool = [comparison.PhysicalAction(**row) for row in protocol["ordered_pool"]]
    check(protocol["legacy_baseline_exhaustion_sentinel"] == len(pool) + 1, "finite search cap may bind")
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    zero, reference = audit_logical(root / "preflight/zero", nets, frozen, views, protocol["gate"])
    check(reference.valid and reference.sec_pass and not zero["actions"]
          and asdict(reference) == read(root / "reference.json"), "wrong or unqualified zero endpoint")
    manifest = dict(protocol, logical_dispatch_cap=inf, relative_hold_tolerance_ps=protocol["hold_tolerance_ps"],
                    timeout_classifier=True)
    entries = read(root / "results.json")
    schedule = [(direction, name) for direction, names in orders.items() for name in names]
    prefix = len(schedule) if prefix is None else prefix
    check(1 <= prefix <= len(entries) <= len(schedule), "requested serial arms are missing")
    outcomes, preceding_stop = [], 0.0
    for index, (direction, strategy) in enumerate(schedule[:prefix], 1):
        method = METHODS[strategy]
        cell = root / f"cell_{index:02d}"
        arm, entry = cell / method, entries[index - 1]
        check(entry == read(cell / "arm.json") and (index, direction, strategy) ==
              (entry["cell"], entry["direction"], entry["strategy"]), "arm order or result changed")
        check(verify(entry["binding"]) == protocol_path and verify(entry["progress"]) == arm / "progress.json"
              and verify(entry["tool_ledger"]) == arm / "subprocesses.json"
              and verify(entry["summary"]) == arm / "summary.json" and read(verify(entry["summary"])) == entry["result"],
              "cross-arm result or ledger")
        check(entry["charged_screening_seconds"] == screen["wall_seconds"], "screening charge differs")
        with replay_resources(arm, strategy, assets, views, pool) as (ordered, tools, ranking):
            requests = cold.audit_requests(arm, assets, ordered, nets)
            inputs = (frozen, views, nets, ordered, reference)
            if method == "faeco":
                audited, skips = replay_variant(cell, inputs, manifest, requests)
            else:
                audited, skips = cold.replay_arm(cell, method, manifest, inputs, requests), []
        operations = cold.verify_operations(cell, method, audited)
        accepted, first, best = accepted_checkpoints(arm, audited, reference, requests)
        check(preceding_stop <= audited["raw_start"] < audited["raw_stop"], "timed cells were not serial")
        preceding_stop = audited["raw_stop"]
        check(len(skips) == entry["reused_setup_only_rejections"], "rejection reuse did not reconstruct")
        check(sum(row["started"] for row in entry["stage_costs"].values()) == len(tools)
              and isclose(sum(row["tool_wall_seconds"] for row in entry["stage_costs"].values()),
                          sum(row["wall_seconds"] for row in tools), rel_tol=0, abs_tol=1e-6), "tool totals differ")
        for pct in TARGETS_PCT:
            threshold = reference.area * pct / 100
            hit = next((row for row in accepted if row["area_saved"] >= threshold - 1e-9), None)
            target = entry["window_targets_pct"][str(pct)]
            check(target["required_area"] == threshold and target["time_raw_seconds"] ==
                  (hit["elapsed_seconds"] if hit else None) and target["first_realized_area"] ==
                  (hit["area_saved"] if hit else None), f"{pct}% target hit differs")
        outcomes.append({"cell": index, "direction": direction, "strategy": strategy,
                         "window": audited["window"], "stop_reason": audited["stop_reason"],
                         "targets": entry["window_targets_pct"], "accepted": accepted, "first": first, "best": best,
                         "operations": operations, "requests": requests, "reused_setup_rejections": skips,
                         "sensitivity_seconds": ranking["preparation"]["seconds"] if ranking else None})
        print(f"Verified {direction} cell {index} {strategy}: {audited['window']['area_saved']:.6f}", flush=True)
    return {"protocol": comparison.bind(protocol_path), "arms": outcomes,
            "verified_prefix": prefix, "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", type=int, choices=range(1, 9))
    parser.add_argument("--confirmed-only", action="store_true", help="audit only the three strategies frozen for holdout")
    args = parser.parse_args()
    comparison.save(args.output, audit(args.run.resolve(strict=True), args.prefix, args.confirmed_only))


if __name__ == "__main__":
    main()
