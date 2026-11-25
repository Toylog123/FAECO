#!/usr/bin/env python3
"""Replay all rank-aligned arms and compare their verified area curves to v2."""

from argparse import ArgumentParser
from contextlib import contextmanager
from itertools import combinations
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tcad_wallclock_schedule_20261125"))
import verify_wallclock_matrix as independent
from verify_wallclock_matrix import check, comparison, read, verify


BUDGET_SECONDS = 720.0
AREA_TARGETS = (26.2752, 45.0432, 52.5504, 57.5552)
EPSILON_AREA = 1e-8


def first_area_hit(accepted, target, *, exact):
    for point in accepted:
        delta = point["area_saved"] - target
        hit = abs(delta) <= EPSILON_AREA if exact else delta >= -EPSILON_AREA
        if point["elapsed_seconds"] <= BUDGET_SECONDS and hit:
            return {key: point[key] for key in ("request_id", "elapsed_seconds", "area_saved")}
    return None


def same_realized_areas(first, second):
    matches = []
    for point in first:
        area = point["area_saved"]
        a = first_area_hit(first, area, exact=True)
        b = first_area_hit(second, area, exact=True)
        if a and b and a["request_id"] == point["request_id"]:
            matches.append({"area_um2": area, "first": a, "second": b,
                            "first_minus_second_raw_s": a["elapsed_seconds"] - b["elapsed_seconds"]})
    return matches


def compare_endpoints(previous, measured):
    prior_arms = {(row["direction"], row["strategy"]): row for row in previous["arms"]}
    pairs = []
    for arm in measured["arms"]:
        key = (arm["direction"], arm["strategy"])
        baseline = prior_arms[key]
        targets = []
        for area in AREA_TARGETS:
            row = {"target_um2": area}
            for exact, label in ((False, "at_least"), (True, "same_realized_area")):
                before = first_area_hit(baseline["accepted"], area, exact=exact)
                after = first_area_hit(arm["accepted"], area, exact=exact)
                gain = before["elapsed_seconds"] - after["elapsed_seconds"] if before and after else None
                row[label] = {"v2": before, "aligned": after, "seconds_saved": gain}
            targets.append(row)
        old_area, new_area = baseline["window"]["area_saved"], arm["window"]["area_saved"]
        pairs.append({"direction": key[0], "strategy": key[1], "v2_area_saved_um2": old_area,
                      "aligned_area_saved_um2": new_area, "area_improvement_um2": new_area - old_area,
                      "targets": targets})
    return pairs


def check_same_conditions(current, baseline):
    for key in ("top", "pdk", "qualified_start", "gate", "absolute_hold_ps", "hold_tolerance_ps", "ordered_pool",
                "screen_input", "charged_screening_seconds_per_arm", "period_basis", "batch_size", "route_threads",
                "single_pin_access", "clock", "cpu_affinity", "timed_process_clock", "timed_process_poll_seconds",
                "order", "wall_window_seconds_including_screen", "logical_dispatch_cap", "single_sensitivity_rule",
                "faeco_reuse_rule"):
        check(current[key] == baseline[key], f"comparison differs in {key}")
    new_seed, old_seed = [read(verify(config["seed"])) for config in (current, baseline)]
    for key in ("route_drt_iters", "route_guide_source", "route_mode", "route_timeout_seconds",
                "sta_timeout_seconds_per_view", "sec_timeout_seconds", "original_clock_period_ps", "physical_area",
                "hold_nonregression_per_view", "hold_threshold_ps", "setup_budget_ps_per_view", "tns_gate"):
        check(new_seed[key] == old_seed[key], f"physical seed setting differs: {key}")
    for key in ("control", "control_drc", "flow", "tools", "used_libraries", "original_sdc", "qualification_receipt"):
        check(new_seed["bindings"][key] == old_seed["bindings"][key], f"physical binding differs: {key}")


def audit(root, source, prefix):
    protocol = read(root / "protocol.json")
    baseline_path = source / "protocol.json"
    verification_path = source / "independent_verification.json"
    check(verify(protocol["rank_alignment_source_verification"]) == verification_path, "wrong original audit receipt")
    previous = read(verification_path)
    check(verify(previous["protocol"]) == baseline_path and previous["verified_prefix"] == 6,
          "expected a fully audited six-arm v2")
    check_same_conditions(protocol, read(baseline_path))
    check(verify(protocol["rank_alignment_source_run"]) == baseline_path
          and tuple(protocol["rank_alignment_absolute_targets_um2"]) == AREA_TARGETS,
          "unexpected comparison source or matched-area targets")
    rank_path = verify(protocol["rank_alignment_source"])
    reverse_path = verify(protocol["rank_alignment_source_reverse"])
    check(rank_path == source / "cell_02/single/sensitivity/ranking.json"
          and reverse_path == source / "cell_05/single/sensitivity/ranking.json", "wrong frozen TT rank sources")
    expected = read(rank_path)["ordered_action_ids"]
    reverse = read(reverse_path)["ordered_action_ids"]
    check(expected == reverse == protocol["rank_aligned_action_ids"] and len(expected) == len(protocol["ordered_pool"])
          and set(expected) == {item["action_id"] for item in protocol["ordered_pool"]}, "rank identity or pool differs")

    native = independent.replay_resources

    @contextmanager
    def aligned_resources(arm, strategy, assets, views, pool, config):
        check(strategy in ("fixed_online", "single_sensitivity", "faeco_dedup"), "unexpected aligned strategy")
        # All arms use the audited single-strategy rank protocol. The historical
        # resource scope still replays the caller's actual batch or single scheduler.
        with native(arm, "single_sensitivity", assets, views, pool, config) as (ordered, tools, ranking):
            check([item.action_id for item in ordered] == expected and ranking["ordered_action_ids"] == expected,
                  "fresh ranked order differs from the frozen source")
            yield ordered, tools, ranking

    independent.replay_resources = aligned_resources
    try:
        measured = independent.audit(root, prefix, confirmed_only=True)
    finally:
        independent.replay_resources = native
    matched = [
        {"direction": a["direction"], "first_strategy": a["strategy"], "second_strategy": b["strategy"],
         "same_realized_areas": same_realized_areas(a["accepted"], b["accepted"])}
        for a, b in combinations(measured["arms"], 2) if a["direction"] == b["direction"]
    ]
    measured.update({"v2_verification": comparison.bind(source / "independent_verification.json"),
                     "aligned_rank_source": comparison.bind(rank_path), "comparison": compare_endpoints(previous, measured),
                     "within_aligned_exact_matches": matched,
                     "verifier": comparison.bind(Path(__file__).resolve())})
    return measured


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("v2", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", type=int, choices=range(1, 7))
    args = parser.parse_args()
    result = audit(args.run.resolve(strict=True), args.v2.resolve(strict=True), args.prefix)
    comparison.save(args.output, result)


if __name__ == "__main__":
    main()
