#!/usr/bin/env python3
"""Reconcile the online AES scheduler, physical admissions and wall windows."""

from argparse import ArgumentParser
from pathlib import Path
import re

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from probe_aes_selective_repair import read, verify
from run_aes_protected_online import METHODS, PROTECT_PA, def_name, drc_neighbor_evidence
from run_screened_matrix import RELATIVE_HOLD_REASONS


class EndOfMeasuredTrace(Exception):
    pass


def check(value, message):
    if not value:
        raise ValueError(message)


def audit_logical(directory, baseline_nets, frozen, reference, gate):
    record = read(directory / "result.json")
    physical_path = verify(record["physical_receipt"])
    final = read(physical_path)
    check(record["actions"] == final["actions"], "logical/physical action disagreement")
    passes = record["passes"]
    check(passes in (["initial"], ["initial", "retry"]), "invalid retry count")
    for name in passes:
        trial = directory / name
        receipt = read(trial / "receipt.json")
        check(receipt["actions"] == record["actions"], "retry changed edit identities")
        check(receipt["control_sdc"] == frozen["sdc"], "SDC mismatch")
        log = (trial / "route.log").read_text(encoding="utf-8", errors="replace")
        if receipt.get("routed_to_completion"):
            check(len(re.findall(PROTECT_PA, log)) == 1, "pin access repeated or absent")
        if "artifacts" in receipt:
            for artifact in receipt["artifacts"].values():
                verify(artifact)
            route = read(trial / "routing_audit.json")
            check(not route["changed_protected_nets"] and not route["changed_untouched_nets"],
                  "changed out-of-scope nets")
            independent = read(trial / "unlocked_drc/audit.json")
            verify(independent["report"])
    if passes == ["initial", "retry"]:
        scope = read(directory / "initial/routing_scope.json")
        request = read(directory / "request.json")
        edited = {comparison.canonical_odb_name(key.partition("=")[0]) for key in record["actions"]}
        init = directory / "initial"
        neighbors, matches = drc_neighbor_evidence(
            (init / "drc.rpt", init / "full_drc.rpt", init / "unlocked_drc/full_drc.rpt"),
            set(request["direct_signal_nets"]), edited, baseline_nets,
        )
        decision = read(directory / "retry_decision.json")
        retry = read(directory / "retry/routing_scope.json")
        check(scope["released_neighbors"] == [], "first route pre-released neighbors")
        check(neighbors and sorted(neighbors) == retry["released_neighbors"]
              == decision["released_neighbors"] and matches == decision["drc_marker_evidence"],
              "retry does not match actual DRC marker neighborhoods")
        check(all("+ USE CLOCK" not in baseline_nets[key] for key in neighbors), "released a clock net")
    endpoint = comparison.Endpoint(**record["endpoint"])
    check(endpoint.valid == endpoint.sec_pass == (not record["failures"]), "delivery-gate disagreement")
    if endpoint.valid:
        where = physical_path.parent
        prove = read(where / "sec/receipt.json")
        check(prove["passed"] and prove["proven"] > 0 and prove["unproven"] == 0
              and prove["gold"] == frozen["v"] and prove["gate"] == final["artifacts"]["v"],
              "delivered SEC proof is empty or bound to a different design")
        verify(prove["gate"])
        check(read(where / "unlocked_drc/audit.json")["drc_markers"] == 0
              and (where / "antenna.rpt").stat().st_size == 0, "delivered physical design is not clean")
        views = final["views"]
        check(not comparison.joint_failures(reference, views, check_setup=False), "hold or electrical violation")
        for corner in comparison.CORNERS:
            base, trial = reference[corner], views[corner]
            failures = sweep.policy.setup_gate_failures(
                corner, base["setup_wns_ps"], trial["setup_wns_ps"], gate["budget_ps"],
                comparison.PS_TOLERANCE, protect_clean=gate["protect_clean_setup_views"],
            ) + sweep.policy.tns_gate_failures(
                corner, base["setup_tns_ps"], trial["setup_tns_ps"],
                gate["setup_tns_budget_ps_by_view"][corner], comparison.PS_TOLERANCE,
            )
            check(not failures, "setup envelope violated")
    return record, endpoint


def audit_arm(root, method, manifest, pool, reference, views, frozen, nets):
    arm = root / method
    progress = read(arm / "progress.json")
    checkpoints = progress["checkpoints"]
    requests = progress["logical_requests"]
    summary = read(arm / "summary.json")
    start, deadline = progress["start_raw"], progress["deadline_raw"]
    cap, screen = manifest["wall_window_seconds_including_screen"], manifest["charged_screening_seconds_per_arm"]
    check(abs(deadline - start + screen - cap) < 1e-6, "wall config mismatch")
    check(len(checkpoints) <= len(requests) <= manifest["logical_dispatch_cap"], "logical cap violated")
    check(sum("failures" not in row for row in requests) <= 1, "multiple unfinished logical trials")
    check(not any(c["elapsed_seconds"] > cap for c in checkpoints), "post-window acceptance")
    for tool in read(arm / "subprocesses.json"):
        check(tool["start_raw"] < deadline, "tool launched out of window")
        check(tool["effective_timeout_seconds"] <= deadline - tool["start_raw"] + 1e-6, "tool timeout bypassed window")
    recorded = [audit_logical(arm / f"{seq:02d}", nets, frozen, views, manifest["gate"])
                for seq in range(1, len(checkpoints) + 1)]
    policy = comparison.BudgetPolicy.from_ps(manifest["gate"]["budget_ps"],
                                             tolerance_ns=manifest["relative_hold_tolerance_ps"] / 1000)
    idx = 0
    last = None
    best = reference

    def evaluate(action_ids):
        nonlocal idx, last, best
        if idx < len(requests):
            check(tuple(requests[idx]["actions"]) == action_ids, "scheduler next proposal disagrees with recorded order")
        if idx == len(recorded):
            raise EndOfMeasuredTrace()
        row, endpoint = recorded[idx]
        check(tuple(row["actions"]) == action_ids, "completed scheduler batch differs")
        check(checkpoints[idx]["endpoint"] == row["endpoint"], "checkpoint points to other physical result")
        accepted = comparison.assess(reference, endpoint, policy).feasible and endpoint.area < best.area - 1e-9
        check(checkpoints[idx]["accepted"] == accepted, "accepted physical prefix does not reconstruct")
        if accepted:
            best = endpoint
        idx += 1
        last = row
        return endpoint

    def defer(actions):
        check(tuple(last["actions"]) == actions, "hold-aware event differs from latest proposal")
        return not RELATIVE_HOLD_REASONS.isdisjoint(last["failures"])

    try:
        replay = comparison.run_method(
            method, reference, pool, evaluate, manifest["logical_dispatch_cap"], manifest["batch_size"],
            policy=policy, defer_split_for=defer if method == "faeco" else None,
        )
        check(len(replay["trace"]) == idx, "scheduler replay has a different completed count")
        check([item["accepted"] for item in replay["trace"]] == [item["accepted"] for item in checkpoints],
              "checkpoint and scheduler acceptances differ")
    except EndOfMeasuredTrace:
        check(progress["stop_reason"] == "end_to_end_wall_cap", "incomplete arm missing wall attribution")
    check(idx == len(recorded), "unused completed evaluations")
    r = sweep.summarize_wall_window(reference, checkpoints, wall_limit_seconds=cap,
                                    target_area_pct=manifest["area_target_pct"])
    check(r == summary["window"], "wall result does not reconstruct")
    return {"logical_admitted": len(requests), "logical_finished": len(checkpoints),
            "retries_completed": sum(row["passes"] == ["initial", "retry"] for row, _ in recorded),
            "route_tools": summary["route_tools"], "stop_reason": summary["stop_reason"],
            "wall_target_reached": r["target_reached_in_window"], "area_saved_pct": r["area_saved_pct"]}


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("run", type=Path)
    args = p.parse_args()
    root = args.run.resolve(strict=True)
    manifest = read(root / "config.json")
    for name, original in manifest["driver_sources"].items():
        snapshot = comparison.bind(root / "producer_sources" / name)
        check(snapshot["sha256"] == original["sha256"] and snapshot["bytes"] == original["bytes"],
              f"archived runtime differs for {name}")
        verify(original)
    frozen = read(verify(manifest["matrix"]))["bindings"]["control"]
    views = read(verify(manifest["control_sta"]))["views"]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    pool = [comparison.PhysicalAction(**row) for row in read(root / "ordered_pool.json")]
    reference = comparison.Endpoint(**read(root / "transferred_preflight.json")["strict_zero"]["endpoint"])
    audited = {method: audit_arm(root, method, manifest, pool, reference, views, frozen, nets) for method in METHODS}
    comparison.save(root / "independent_verification.json", audited)
    for method, row in audited.items():
        print(method, row, flush=True)


if __name__ == "__main__":
    main()
