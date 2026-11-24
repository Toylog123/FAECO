#!/usr/bin/env python3
"""Replay the measured protected AES pair and independently audit gate and wall admission."""

from argparse import ArgumentParser
from pathlib import Path

import compare_ibex as comparison
from incident_cap_priority import build_incident_priority
from probe_aes_selective_repair import read, verify
from run_aes_incident_priority_matched import METHODS
from run_aes_protected_online import drc_neighbor_evidence
from run_aes_retry_triage import DEFERRED_RETRY, DRC_REASONS
from run_screened_matrix import RELATIVE_HOLD_REASONS
import run_setup_budget_sweep as sweep
from verify_aes_protected_online import EndOfMeasuredTrace, audit_logical, check


def verify_pair_inputs(root, manifest):
    for name, original in manifest["driver_sources"].items():
        verify(original)
        snapshot = comparison.bind(root / "producer_sources" / name)
        check({key: snapshot[key] for key in ("bytes", "sha256")} ==
              {key: original[key] for key in ("bytes", "sha256")}, f"archived runtime differs for {name}")
    matrix = read(verify(manifest["matrix"]))
    frozen = matrix["bindings"]["control"]
    views = read(verify(manifest["control_sta"]))["views"]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    rows = read(root / "ordered_pool.json")
    check(rows == read(verify(manifest["screened_pool"])) == read(verify(matrix["screen_inputs"]["pool"])),
          "screen pool differs from the original")
    check(read(verify(manifest["historical_screen_receipt"]))["wall_seconds"] ==
          manifest["charged_screening_seconds_per_arm"], "historical screening charge differs")
    pool = [comparison.PhysicalAction(**row) for row in rows]
    transferred = read(root / "transferred_preflight.json")
    preflight = verify(transferred["preflight_result"])
    check(transferred["strict_zero"] == read(preflight)["zero"], "different zero transferred")
    zero_row, reference = audit_logical(preflight.parent / "zero", nets, frozen, views, manifest["gate"])
    challenge_row, challenge = audit_logical(preflight.parent / "rank1_batch", nets, frozen, views, manifest["gate"])
    check(reference == comparison.Endpoint(**transferred["strict_zero"]["endpoint"]), "wrong zero checkpoint")
    check(reference.valid and reference.sec_pass and not challenge.valid, "expected fresh strict zero and rejected rank1")
    zero_views = read(verify(zero_row["physical_receipt"]))["views"]
    metrics = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
    check(all(zero_views[view][metric] == views[view][metric] for view in comparison.CORNERS for metric in metrics),
          "strict zero timing differs from frozen reference")
    expected = sorted(action.action_id for action in pool[:manifest["batch_size"]])
    check(challenge_row["actions"] == expected and challenge_row["failures"] == ["SS:hold_regression"],
          "fresh rank1 differs from the recorded challenge")
    return frozen, views, nets, pool, reference


def audit_retry_deferral(directory, record, nets):
    initial = directory / "initial"
    assessment = initial / "assessment.json"
    decision = directory / "deferred_retry.json"
    if not assessment.exists():
        check(not decision.exists(), "retry was deferred without an initial physical assessment")
        return False
    failures = set(read(assessment)["failures"])
    hold = sorted(RELATIVE_HOLD_REASONS & failures)
    unrelated = {reason for reason in failures - DRC_REASONS if not reason.startswith(("FF:", "TT:", "SS:"))}
    neighbors, markers = set(), []
    if hold and failures & DRC_REASONS and not unrelated:
        request = read(directory / "request.json")
        edited = {comparison.canonical_odb_name(action.partition("=")[0]) for action in record["actions"]}
        neighbors, markers = drc_neighbor_evidence(
            (initial / "drc.rpt", initial / "full_drc.rpt", initial / "unlocked_drc/full_drc.rpt"),
            set(request["direct_signal_nets"]), edited, nets,
        )
    check(decision.exists() == bool(neighbors) == (DEFERRED_RETRY in record["failures"]),
          "preliminary hold and genuine DRC neighbors do not reconstruct the retry deferral")
    if decision.exists():
        details = read(decision)
        check(record["passes"] == ["initial"] and not record["endpoint"]["sec_pass"] and not (directory / "retry").exists(),
              "deferred candidate incurred a physical retry or was admitted")
        check(details["actions"] == record["actions"] and details["reason"] == DEFERRED_RETRY
              and details["preliminary_relative_hold_reasons"] == hold and details["reported_retry_neighbors"] == sorted(neighbors)
              and details["marker_evidence"] == markers and verify(details["preliminary_assessment"]) == assessment,
              "deferred marker or preliminary hold details differ from original")
    return decision.exists()


def audit_arm(root, method, manifest, pool, reference, views, frozen, nets, *, reconcile_exit=False):
    arm = root / method
    progress = read(arm / "progress.json")
    producer_summary = arm / "summary.json"
    summary = read(producer_summary) if producer_summary.exists() else None
    requests, checkpoints = progress["logical_requests"], progress["checkpoints"]
    start, deadline = progress["start_raw"], progress["deadline_raw"]
    cap = manifest["wall_window_seconds_including_screen"]
    screen = manifest["charged_screening_seconds_per_arm"]
    max_requests = manifest["logical_dispatch_cap"]
    check(abs(deadline - start + screen - cap) < 1e-6, "arm window differs")
    check(len(checkpoints) <= len(requests) <= max_requests and len(requests) - len(checkpoints) <= 1,
          "logical cap or unfinished count differs")
    check([row["id"] for row in requests] == list(range(1, len(requests) + 1)), "invalid dispatch numbering")
    check(all(start <= row["admitted_raw"] < deadline for row in requests), "late dispatch")
    for request, checkpoint in zip(requests, checkpoints):
        elapsed = checkpoint["elapsed_seconds"]
        check(request["admitted_raw"] <= request["finished_raw"] < deadline and elapsed <= cap
              and elapsed == screen + (request["finished_raw"] - start), "late or mis-metered checkpoint")
    raw_tools = read(arm / "subprocesses.json")
    for tool in raw_tools:
        check(start <= tool["start_raw"] < deadline and tool["effective_timeout_seconds"] <=
              deadline - tool["start_raw"] + 1e-6, "subprocess exceeded its admissible cap")
        if "timeout_classifier" in manifest:
            bound = "wall" if deadline - tool["start_raw"] <= tool["configured_timeout_seconds"] else "stage"
            check(tool["timeout_bound"] == bound, "wrong subprocess timeout source")
        check(Path(tool["log"]).is_relative_to(arm), "cross-arm physical reuse")
    last = raw_tools[-1]
    expired_wall_child = (last["returncode"] is None and last["configured_timeout_seconds"] >
                          last["effective_timeout_seconds"] and abs(last["start_raw"] +
                          last["effective_timeout_seconds"] - deadline) < 1e-6)
    if summary is None:
        check(reconcile_exit and method == "faeco" and "timeout_classifier" not in manifest and
              progress["stop_reason"] is None and expired_wall_child and len(requests) == len(checkpoints) + 1
              and deadline - 1 < last["stop_raw"] < deadline and Path(last["log"]).name == "audit.log",
              "missing producer outcome without a matching V1 cap-clipped independent DRC exit")
        check(not (arm / f"{len(requests):02d}/result.json").exists(), "censored request has a terminal admission record")
        stop_reason = "clipped_child_timeout_driver_exit"
        stop_raw = last["stop_raw"]
    else:
        stop_reason = progress["stop_reason"]
        stop_raw = summary["stop_raw"]
        check(stop_reason == summary["stop_reason"], "producer stop records disagree")
    priorities = None
    preparation = progress["priority_preparation"]
    if method == "faeco":
        binding = read(arm / "incident_priority.json")
        check(binding["control_def"] == frozen["def"] and binding["control_spef"] == frozen["spef"],
              "active priority uses a different reference")
        ranking = build_incident_priority(verify(frozen["def"]), verify(frozen["spef"]), pool)
        check(all(binding[key] == value for key, value in ranking.items()), "priority does not reconstruct")
        priorities = {key: row["priority"] for key, row in ranking["actions"].items()}
        check(preparation == binding["preparation"]
              and start <= preparation["start_raw"] < preparation["stop_raw"] <= requests[0]["admitted_raw"]
              and preparation["seconds"] == preparation["stop_raw"] - preparation["start_raw"],
              "priority preparation did not fall inside the FAECO charged window")
        if summary is not None:
            check(preparation == summary["priority_preparation"], "producer priority time differs")
    else:
        check(preparation is None and not (arm / "incident_priority.json").exists(), "fixed paid priority cost")

    recorded = [audit_logical(arm / f"{seq:02d}", nets, frozen, views, manifest["gate"])
                for seq in range(1, len(checkpoints) + 1)]
    triage = manifest.get("defer_marker_retry_reason") == DEFERRED_RETRY
    triaged_retries = sum(audit_retry_deferral(arm / f"{index:02d}", record, nets)
                          for index, (record, _) in enumerate(recorded, 1)) if triage else 0
    defer_reasons = RELATIVE_HOLD_REASONS | {DEFERRED_RETRY} if triage else RELATIVE_HOLD_REASONS
    policy = comparison.BudgetPolicy.from_ps(manifest["gate"]["budget_ps"],
                                             tolerance_ns=manifest["relative_hold_tolerance_ps"] / 1000)
    idx = 0
    deferrals = []
    best = reference

    def evaluate(action_ids):
        nonlocal idx, best
        if idx < len(requests):
            check(tuple(requests[idx]["actions"]) == action_ids, "measured dispatch differs from method replay")
        if idx == len(recorded):
            raise EndOfMeasuredTrace()
        record, endpoint = recorded[idx]
        check(tuple(record["actions"]) == action_ids and checkpoints[idx]["endpoint"] == record["endpoint"]
              and requests[idx]["failures"] == record["failures"],
              "checkpoint differs from physical receipt")
        accepted = comparison.assess(reference, endpoint, policy).feasible and endpoint.area < best.area - 1e-9
        check(checkpoints[idx]["accepted"] == accepted, "accepted physical prefix does not replay")
        if accepted:
            best = endpoint
        idx += 1
        return endpoint

    def defer(actions):
        record, _ = recorded[idx - 1]
        check(tuple(record["actions"]) == actions, "relative-hold event uses a different request")
        reasons = sorted(defer_reasons.intersection(record["failures"]))
        if reasons:
            deferrals.append({"request_id": idx, "actions": list(actions), "reasons": reasons})
        return bool(reasons)

    try:
        replay = comparison.run_method(
            method, reference, pool, evaluate, max_requests, manifest["batch_size"], policy=policy,
            defer_split_for=defer if method == "faeco" else None, priority_after_defer=priorities,
        )
        check(replay["selected"] == best and len(replay["trace"]) == idx, "method completion differs in replay")
        check(stop_reason == "logical_cap_or_pool_exhausted", "completed arm marked as censored")
    except EndOfMeasuredTrace:
        waited_to_cap = stop_reason == "end_to_end_wall_cap" and stop_raw >= deadline
        timed_out_in_cap = stop_reason == "end_to_end_wall_cap" and expired_wall_child and "timeout_classifier" in manifest
        clipped_legacy_exit = summary is None and stop_reason == "clipped_child_timeout_driver_exit"
        check(waited_to_cap or timed_out_in_cap or clipped_legacy_exit, "censored arm did not reach a wall-bound timeout")
    check(idx == len(recorded), "unused completed evaluations")
    trigger = deferrals[0] if deferrals else None
    check(trigger == progress["first_relative_hold_defer"], "first deferral differs from measured history")
    area = sweep.summarize_wall_window(reference, checkpoints, wall_limit_seconds=cap,
                                      target_area_pct=manifest["area_target_pct"])
    if summary is not None:
        check(trigger == summary["first_relative_hold_defer"] and area == summary["window"],
              "producer deferral or wall result does not reconstruct")
    return {"logical_admitted": len(requests), "logical_finished": idx,
            "completed_retries": sum(len(row["passes"]) == 2 for row, _ in recorded),
            "triaged_retries": triaged_retries,
            "first_relative_hold_defer": trigger, "priority_preparation": preparation,
            "raw_start": start, "raw_stop": stop_raw, "stop_reason": stop_reason,
            "source_progress": comparison.bind(arm / "progress.json"),
            "source_subprocesses": comparison.bind(arm / "subprocesses.json"), "window": area}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--reconcile-clipped-legacy-exit", action="store_true")
    args = parser.parse_args()
    root = args.run.resolve(strict=True)
    manifest = read(root / "config.json")
    development = manifest.get("defer_marker_retry_reason") == DEFERRED_RETRY
    methods = ("faeco",) if development else METHODS
    check(manifest["methods"] == list(methods), "wrong arm order")
    frozen, views, nets, pool, reference = verify_pair_inputs(root, manifest)
    audited = {method: audit_arm(root, method, manifest, pool, reference, views, frozen, nets,
                                 reconcile_exit=args.reconcile_clipped_legacy_exit) for method in methods}
    if development:
        baseline = {name: read(verify(item)) for name, item in manifest["baseline_v2"].items()}
        v2 = baseline["config.json"]
        checked = v2.keys() - {"methods", "driver_pid", "driver_sources"}
        check(all(v2[key] == manifest[key] for key in checked), "V3 changed a V2 physical or budget condition")
        check(baseline["independent_verification.json"]["arms"]["faeco"]["raw_stop"] <= audited["faeco"]["raw_start"],
              "V3 overlaps the V2 baseline")
    else:
        check(audited["fixed"]["raw_stop"] <= audited["faeco"]["raw_start"], "overlapping methods")
    dispatches = {method: read(root / method / "progress.json")["logical_requests"] for method in methods}
    first = {method: rows[0]["actions"] for method, rows in dispatches.items()}
    size = manifest["batch_size"]
    expected = sorted(action.action_id for action in pool[:size])
    check(all(actions == expected for actions in first.values()), "the first batch changed before hold deferral")
    trigger = audited["faeco"]["first_relative_hold_defer"]
    if trigger and trigger["request_id"] == 1 and len(dispatches["faeco"]) > 1:
        ranking = read(root / "faeco/incident_priority.json")["actions"]
        ordered_suffix = sorted(pool[size:], key=lambda action: -ranking[action.action_id]["priority"])
        expected_second = sorted(action.action_id for action in ordered_suffix[:size])
        check(dispatches["faeco"][1]["actions"] == expected_second, "first reorder did not keep the top unvisited batch")
    name = "independent_reconciliation.json" if args.reconcile_clipped_legacy_exit else "independent_verification.json"
    comparison.save(root / name, {"audit_source": comparison.bind(Path(__file__).resolve()), "arms": audited})
    for method, row in audited.items():
        print(method, row["logical_finished"], row["logical_admitted"], row["window"]["area_saved_pct"], flush=True)


if __name__ == "__main__":
    main()
