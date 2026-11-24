#!/usr/bin/env python3
"""Independently replay and verify the timed AES marker-guided development pair."""

from argparse import ArgumentParser
from pathlib import Path
import math
import re

import compare_ibex as comparison
from probe_aes_selective_repair import normalize_net, read, verify
from run_aes_protected_online import drc_neighbor_evidence
from verify_aes_incident_priority_matched import audit_arm, verify_pair_inputs
from verify_aes_protected_online import check


METHODS = ("fixed", "repair")
RANKS = {"three": (4, 5, 6), "six": (4, 6, 12, 13, 16, 17)}
EXPECTED_NEIGHBORS = {
    "three": {"net4840", "net8407"},
    "six": {"_08784_", "net4840", "net8148", "net8407"},
}


def verify_protocol(root, manifest):
    check(manifest["methods"] == list(METHODS), "unexpected timed methods or serial order")
    check(manifest["batch_size"] == 3 and manifest["logical_dispatch_cap"] == 6
          and manifest["wall_window_seconds_including_screen"] == 720.0 and manifest["area_target_pct"] == 0.01,
          "changed original batch, logical cap, wall cap or area target")
    check(manifest["absolute_hold_ps"] == 0 and manifest["relative_hold_tolerance_ps"] == comparison.PS_TOLERANCE
          and manifest["gate"]["budget_ps"] == 36.0 and manifest["route_threads"] == 4
          and manifest["measurement_clock"] == "CLOCK_MONOTONIC_RAW" and manifest["maximum_neighbor_retries"] == 1
          and manifest["single_internal_pin_access"] is True and manifest["direct_data_nets_only_initially"] is True
          and "timeout_classifier" in manifest and "defer_marker_retry_reason" not in manifest,
          "changed original acceptance, pin access or strict clock protocol")
    preflight = verify(read(root / "transferred_preflight.json")["preflight_result"])
    zero_config = read(preflight.parent.parent / "config.json")
    shared = zero_config.keys() - {"driver_pid", "driver_sources", "methods"}
    check(all(manifest[key] == zero_config[key] for key in shared), "timed pair differs from its original preflight protocol")
    check(all(manifest["driver_sources"][name] == binding for name, binding in zero_config["driver_sources"].items()),
          "timed pair changed a frozen physical or timing dependency")


def incident_signal_nets(actions, nets):
    edited = {comparison.canonical_odb_name(action.partition("=")[0]) for action in actions}
    connected = {
        name for name, entry in nets.items()
        if edited.intersection(re.findall(r"\( (\S+) \S+ \)", entry.partition(" + ")[0]))
    }
    check(connected and all("+ USE SIGNAL" in nets[name] for name in connected), "invalid hint incident net topology")
    return edited, connected


def verify_marker_plan(root, manifest, pool, nets):
    check(len(pool) == 18 and set(manifest["hint_sources"]) == set(RANKS), "unexpected development hint sources or pool")
    arm = root / "repair"
    progress = read(arm / "progress.json")
    plan = read(arm / "marker_plan.json")
    timing = plan["preparation"]
    requests = progress["logical_requests"]
    check(requests and progress["start_raw"] <= timing["start_raw"] < timing["stop_raw"] <= requests[0]["admitted_raw"]
          and timing["seconds"] == timing["stop_raw"] - timing["start_raw"], "marker preparation escaped the repair window")
    proposals = [tuple(sorted(item.action_id for item in pool[:3]))]
    releases = [set()]
    expected_hints = {}
    for label, ranks in RANKS.items():
        inputs = manifest["hint_sources"][label]
        request, report = (verify(inputs[key]) for key in ("request", "marker_report"))
        actions = tuple(sorted(pool[rank - 1].action_id for rank in ranks))
        edited, incident = incident_signal_nets(actions, nets)
        history = read(request)
        check(tuple(history["actions"]) == actions and history["direct_signal_nets"] == sorted(incident),
              f"{label} hint refers to different actions or incident nets")
        neighbors, evidence = drc_neighbor_evidence((report,), incident, edited, nets)
        check(neighbors == EXPECTED_NEIGHBORS[label] and not neighbors & incident,
              f"{label} hint has unexpected original neighbors")
        expected_hints[label] = {"actions": list(actions), "incident_nets": sorted(incident),
                                 "released_neighbors": sorted(neighbors), "marker_evidence": evidence}
        proposals.append(actions)
        releases.append(neighbors)
    check(plan["hints"] == expected_hints and plan["actions"] == [list(item) for item in proposals],
          "the recorded repair plan differs from the historical markers or preregistered actions")
    check(1 <= len(requests) <= len(proposals) and [tuple(row["actions"]) for row in requests] == proposals[:len(requests)],
          "repair dispatched a request outside the three-proposal plan")
    return proposals, releases, expected_hints, timing


def verify_repair_scopes(arm, proposals, releases, nets):
    progress = read(arm / "progress.json")
    tools = read(arm / "subprocesses.json")
    scopes = []
    for row, actions, neighbors in zip(progress["logical_requests"], proposals, releases):
        directory = arm / f"{row['id']:02d}"
        initial = directory / "initial"
        scope = initial / "routing_scope.json"
        started = [tool for tool in tools if Path(tool["log"]).is_relative_to(directory)]
        finished = "finished_raw" in row
        check(not (directory / "retry").exists() and not (directory / "retry_decision.json").exists()
              and len([tool for tool in started if Path(tool["log"]).name == "route.log"]) <= 1
              and all(Path(tool["log"]).is_relative_to(initial) for tool in started),
              "repair invoked extra work outside its single planned physical pass")
        if not scope.exists():
            check(not (started or finished), "physical invocation has no frozen routing scope")
            continue
        _, incident = incident_signal_nets(actions, nets)
        allowed = incident | neighbors
        request = read(directory / "request.json")
        pinned = read(scope)
        check(request["actions"] == list(actions) and request["direct_signal_nets"] == sorted(incident)
              and pinned["mode"] == "fixed-untouched" and pinned["released_neighbors"] == sorted(neighbors)
              and pinned["expected_touched_nets"] == sorted(allowed), "physical route used a different marker release scope")
        verify(pinned["fixed_wire_patch"])
        if finished:
            record = read(directory / "result.json")
            final = verify(record["physical_receipt"])
            check(record["passes"] == ["initial"] and final == initial / "receipt.json", "logical result reused a physical output")
            receipt = read(final)
            if "artifacts" in receipt:
                routed = comparison.def_section(verify(receipt["artifacts"]["def"]), "NETS")
                check(routed.keys() == nets.keys() and all(
                    normalize_net(nets[name]) == normalize_net(routed[name]) for name in nets.keys() - allowed
                ), "an out-of-scope wire changed in the actual routed DEF")
        scopes.append({"request_id": row["id"], "scope": comparison.bind(scope),
                       "incident": sorted(incident), "released": sorted(neighbors)})
    return scopes


def audit_repair(root, manifest, pool, reference, views, frozen, nets, proposals):
    def replay(method, reference, _pool, evaluate, budget, batch_size, *, policy,
               defer_split_for, priority_after_defer):
        check(method == "repair" and budget >= len(proposals) and batch_size == 3
              and defer_split_for is None and priority_after_defer is None, "unexpected repair replay contract")
        trace = []
        best = reference
        for actions in proposals:
            endpoint = evaluate(actions)
            if comparison.assess(reference, endpoint, policy).feasible and endpoint.area < best.area - 1e-9:
                best = endpoint
            trace.append(actions)
        return {"selected": best, "trace": trace}

    original = comparison.run_method
    try:
        comparison.run_method = replay
        return audit_arm(root, "repair", manifest, pool, reference, views, frozen, nets)
    finally:
        comparison.run_method = original


def verify_operations(root, method, audited):
    directory = root / method
    summary = read(directory / "summary.json")
    tools = read(directory / "subprocesses.json")
    names = [Path(row["log"]).name for row in tools]
    counts = {"route_tools": names.count("route.log"), "unlocked_drc_tools": names.count("audit.log"),
              "sta_tools": sum(name.startswith("sta_") for name in names), "sec_tools": names.count("sec.log")}
    check(all(count == summary[key] for key, count in counts.items())
          and summary["logical_admitted"] == audited["logical_admitted"]
          and summary["logical_finished"] == audited["logical_finished"]
          and summary["tool_seconds"] == math.fsum(row.get("wall_seconds", 0) for row in tools)
          and summary["search_raw_seconds"] == audited["raw_stop"] - audited["raw_start"],
          "producer operation counts or time differ from the original ledger")
    return counts


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    root = parser.parse_args().run.resolve(strict=True)
    manifest = read(root / "config.json")
    verify_protocol(root, manifest)
    frozen, views, nets, pool, reference = verify_pair_inputs(root, manifest)
    proposals, releases, hints, planning = verify_marker_plan(root, manifest, pool, nets)
    fixed = audit_arm(root, "fixed", manifest, pool, reference, views, frozen, nets)
    repair = audit_repair(root, manifest, pool, reference, views, frozen, nets, proposals)
    scopes = verify_repair_scopes(root / "repair", proposals, releases, nets)
    check(fixed["raw_stop"] <= repair["raw_start"], "timed arms overlapped or ran in the wrong order")
    first = read(root / "fixed/progress.json")["logical_requests"][0]["actions"]
    check(first == list(proposals[0]), "timed arms began with different actions")
    results = read(root / "results.json")
    check(list(results) == list(METHODS) and all(results[method] == read(root / method / "summary.json")
                                                for method in METHODS), "top-level results and exact arm summaries differ")
    arms = {"fixed": fixed, "repair": repair}
    for method, checked in arms.items():
        checked["operation_counts"] = verify_operations(root, method, checked)
    comparison.save(root / "independent_verification.json", {
        "audit_source": comparison.bind(Path(__file__).resolve()), "configuration": comparison.bind(root / "config.json"),
        "arms": arms, "marker_plan": comparison.bind(root / "repair/marker_plan.json"),
        "recovered_hints": hints, "marker_preparation": planning, "routed_scopes": scopes,
    })
    for method, row in arms.items():
        print(method, row["logical_finished"], row["logical_admitted"], row["window"]["area_saved_pct"], flush=True)


if __name__ == "__main__":
    main()
