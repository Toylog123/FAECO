#!/usr/bin/env python3
"""Audit a same-candidate AES marker-guidance component experiment."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import re

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
import verify_aes_incident_priority_matched as matched
from probe_aes_selective_repair import normalize_net, read, verify
from run_aes_protected_online import PROTECT_PA, drc_neighbor_evidence
from verify_aes_marker_repair import incident_signal_nets, verify_operations
from verify_aes_protected_online import check


METHODS = ("retry_1", "guided_1", "guided_2", "retry_2")


def verify_protocol(root, manifest):
    check(manifest["methods"] == list(METHODS) and manifest["wall_window_seconds_including_screen"] == 720.0
          and manifest["logical_dispatch_cap"] in (1, 6) and manifest["logical_requests_per_arm"] == 1
          and "timeout_classifier" in manifest
          and "defer_marker_retry_reason" not in manifest, "unexpected repeated schedule or wall policy")
    preflight = verify(read(root / "transferred_preflight.json")["preflight_result"])
    original = read(preflight.parent.parent / "config.json")
    shared = original.keys() - {"driver_pid", "driver_sources", "methods", "logical_dispatch_cap"}
    check(all(manifest[key] == original[key] for key in shared), "original frozen gates or timing charges changed")
    check(all(manifest["driver_sources"][name] == binding for name, binding in original["driver_sources"].items()),
          "a frozen physical dependency changed")
    check(manifest["maximum_neighbor_retries"] == 1 and manifest["single_internal_pin_access"] is True
          and manifest["relative_hold_tolerance_ps"] == comparison.PS_TOLERANCE
          and manifest["absolute_hold_ps"] == 0 and manifest["gate"]["budget_ps"] == 36.0,
          "original acceptance, pin access or retry policy changed")


def compare_routes(left, right, allowed, message):
    check(left.keys() == right.keys() and all(
        normalize_net(left[name]) == normalize_net(right[name]) for name in left.keys() - allowed
    ), message)


def reconstruct_hint(manifest, frozen, pool, nets):
    sources = manifest["diagnostic_sources"]
    request, physical, inputs, summary = (
        read(verify(sources[key])) for key in ("request", "physical", "audit_inputs", "audit_summary")
    )
    actions = tuple(manifest["case_actions"])
    check(actions and tuple(sorted(set(actions))) == actions and set(actions) <= {row.action_id for row in pool}
          and request["actions"] == physical["actions"] == list(actions), "diagnostic edited a different candidate")
    edited, incident = incident_signal_nets(actions, nets)
    check(request["direct_signal_nets"] == sorted(incident) and physical["control_sdc"] == frozen["sdc"]
          and physical["routed_to_completion"] and physical["extracted_to_completion"],
          "diagnostic topology, SDC or physical completion differs")
    check(inputs["matrix_config"] == manifest["matrix"] and inputs["input_odb"] == physical["artifacts"]["odb"]
          and inputs["input_def"] == physical["artifacts"]["def"], "independent audit read a different physical input")
    verify(inputs["input_odb"])
    verify(inputs["producer"])
    routed = comparison.def_section(verify(inputs["input_def"]), "NETS")
    restored = comparison.def_section(verify(summary["normalized_geometry"]), "NETS")
    compare_routes(nets, routed, incident, "historical diagnostic changed an original protected net")
    compare_routes(routed, restored, set(), "historical restore changed a route or pin connection")
    fixed_wires = sum("+ FIXED " in entry for entry in routed.values())
    check(fixed_wires > 0 and fixed_wires == inputs["original_fixed_wire_count"]
          and not any("+ FIXED " in entry for entry in restored.values()), "historical check did not restore ROUTED wires")
    report = verify(summary["report"])
    markers = re.findall(r"(?m)^violation type:\s*(.+)$", report.read_text(encoding="utf-8"))
    check(len(markers) == summary["drc_markers"] and sorted(set(markers)) == summary["marker_types"],
          "historical independent marker count differs from its report")
    neighbors, evidence = drc_neighbor_evidence((report,), incident, edited, nets)
    complete = bool(neighbors) and len(evidence) == len(markers)
    hint = {"actions": list(actions), "incident_nets": sorted(incident),
            "released_neighbors": sorted(neighbors) if complete else [], "marker_evidence": evidence,
            "marker_count": len(markers), "status": "guided" if complete else "no_complete_guidance"}
    return actions, edited, incident, hint


def audit_guided_retry(directory, frozen, views, gate):
    """Check ordinary physical delivery gates when the shared reader's zero-hint premise no longer holds."""
    record = read(directory / "result.json")
    expected = directory / "retry/receipt.json"
    physical = verify(record["physical_receipt"])
    check(physical == expected and record["passes"] == ["initial", "retry"], "guided retry did not bind its actual output")
    for name in record["passes"]:
        trial = directory / name
        receipt = read(trial / "receipt.json")
        check(receipt["actions"] == record["actions"] and receipt["control_sdc"] == frozen["sdc"],
              "guided retry changed actions or source SDC")
        if receipt["routed_to_completion"]:
            log = (trial / "route.log").read_text(encoding="utf-8", errors="replace")
            check(len(re.findall(PROTECT_PA, log)) == 1, "guided physical pass had extra pin access")
        if "artifacts" in receipt:
            for artifact in receipt["artifacts"].values():
                verify(artifact)
            verify(read(trial / "unlocked_drc/audit.json")["report"])
    endpoint = comparison.Endpoint(**record["endpoint"])
    check(endpoint.valid == endpoint.sec_pass == (not record["failures"]), "guided delivery and gate observations disagree")
    if endpoint.valid:
        trial = expected.parent
        proof = read(trial / "sec/receipt.json")
        check(proof["passed"] and proof["proven"] > 0 and proof["unproven"] == 0 and proof["gold"] == frozen["v"]
              and proof["gate"] == read(physical)["artifacts"]["v"], "guided SEC did not bind the exact candidate endpoints")
        verify(proof["gate"])
        check(read(trial / "unlocked_drc/audit.json")["drc_markers"] == 0
              and (trial / "antenna.rpt").stat().st_size == 0, "guided retry left physical violations")
        measured = read(physical)["views"]
        check(not comparison.joint_failures(views, measured, check_setup=False), "guided retry failed original hold or electrical gate")
        for corner in comparison.CORNERS:
            base, result = views[corner], measured[corner]
            failed = sweep.policy.setup_gate_failures(
                corner, base["setup_wns_ps"], result["setup_wns_ps"], gate["budget_ps"],
                comparison.PS_TOLERANCE, protect_clean=gate["protect_clean_setup_views"],
            ) + sweep.policy.tns_gate_failures(
                corner, base["setup_tns_ps"], result["setup_tns_ps"], gate["setup_tns_budget_ps_by_view"][corner],
                comparison.PS_TOLERANCE,
            )
            check(not failed, "guided retry failed original setup envelope")
    return record, endpoint


def verify_pass_scope(trial, incident, released, nets, completed):
    config = trial / "routing_scope.json"
    scope = read(config)
    active = incident | released
    check(scope["mode"] == "fixed-untouched" and scope["released_neighbors"] == sorted(released)
          and scope["expected_touched_nets"] == sorted(active), "actual routing scope differs from independently justified release")
    verify(scope["fixed_wire_patch"])
    if completed:
        receipt = read(trial / "receipt.json")
        if "artifacts" in receipt:
            routed = comparison.def_section(verify(receipt["artifacts"]["def"]), "NETS")
            compare_routes(nets, routed, active, "fresh physical pass changed a protected net")
    return {"scope": comparison.bind(config), "released": sorted(released)}


def verify_arm_scopes(arm, actions, edited, incident, hint, nets):
    plan = arm / "hint.json"
    progress = read(arm / "progress.json")
    requests = progress["logical_requests"]
    check(len(requests) == 1 and requests[0]["actions"] == list(actions), "arm did not dispatch exactly the common edit tuple")
    guided = arm.name.startswith("guided_")
    released = set()
    if guided:
        source = read(plan)
        check({key: source[key] for key in hint} == hint, "fresh hint differs from source report and frozen topology")
        time = source["preparation"]
        check(progress["start_raw"] <= time["start_raw"] < time["stop_raw"] <= requests[0]["admitted_raw"]
              and time["seconds"] == time["stop_raw"] - time["start_raw"], "guidance prepared outside its timed arm")
        released = set(hint["released_neighbors"])
    else:
        check(not plan.exists(), "ordinary retry arm has a guidance artifact")
    directory = arm / "01"
    request = read(directory / "request.json")
    check(request["actions"] == list(actions) and request["direct_signal_nets"] == sorted(incident),
          "physical request differed from the common logical request")
    tools = read(arm / "subprocesses.json")
    check(all(Path(tool["log"]).is_relative_to(directory) for tool in tools), "arm routed a different request")
    initial = directory / "initial"
    completed = "finished_raw" in requests[0]
    scopes = {"initial": verify_pass_scope(initial, incident, released, nets, completed)}
    retry = directory / "retry"
    if retry.exists():
        assessment = read(initial / "assessment.json")
        drc = {"drc", "full_drc", "unlocked_drc"}
        failures = set(assessment["failures"])
        check(failures & drc and all(name.startswith(("FF:", "TT:", "SS:")) for name in failures - drc),
              "performed neighbor retry after an unrelated failure")
        reports = (initial / "drc.rpt", initial / "full_drc.rpt", initial / "unlocked_drc/full_drc.rpt")
        added, evidence = drc_neighbor_evidence(reports, incident | released, edited, nets)
        decision = read(directory / "retry_decision.json")
        check(added and not (incident | released) & added and decision["released_neighbors"] == sorted(added)
              and decision["drc_marker_evidence"] == evidence, "retry did not exclusively release real new marker neighbors")
        scopes["retry"] = verify_pass_scope(retry, incident, released | added, nets, completed)
    for pass_name in ("initial", "retry"):
        routes = [row for row in tools if Path(row["log"]) == directory / pass_name / "route.log"]
        check(len(routes) <= int(pass_name in scopes), "arm started extra detailed routing")
    if completed:
        record = read(directory / "result.json")
        final = verify(record["physical_receipt"])
        check(record["passes"] == list(scopes) and final == directory / record["passes"][-1] / "receipt.json",
              "completed endpoint did not come from this arm's last physical pass")
        measured = read(final)["endpoint"]
        recorded = record["endpoint"]
        check(Path(recorded["evidence_id"]) == final.parent
              and all(value == recorded[key] for key, value in measured.items() if key not in ("valid", "sec_pass")),
              "measured endpoint identity or metrics differ from the selected logical record")
    return scopes


def replay_arm(root, method, inputs, manifest, actions, scopes):
    def replay(name, reference, _pool, evaluate, _cap, _batch_size, *, policy, defer_split_for, priority_after_defer):
        check(name == method and defer_split_for is None and priority_after_defer is None, "unexpected scheduler replay")
        outcome = evaluate(actions)
        good = comparison.assess(reference, outcome, policy).feasible and outcome.area < reference.area - 1e-9
        return {"selected": outcome if good else reference, "trace": [actions]}

    frozen, views, nets, pool, reference = inputs
    original_schedule, original_audit = comparison.run_method, matched.audit_logical
    try:
        comparison.run_method = replay
        if method.startswith("guided_") and scopes["initial"]["released"] and "retry" in scopes:
            def replay_guided(directory, _nets, frozen, views, gate):
                return audit_guided_retry(directory, frozen, views, gate)

            matched.audit_logical = replay_guided
        return matched.audit_arm(root, method, manifest, pool, reference, views, frozen, nets)
    finally:
        comparison.run_method, matched.audit_logical = original_schedule, original_audit


def endpoint_identity(window):
    if not window["selected"]["valid"] or not window["area_saved"]:
        return None
    endpoint = Path(window["selected"]["evidence_id"])
    receipt = read(endpoint / "receipt.json")
    files = {kind: receipt["artifacts"][kind]["sha256"] for kind in ("odb", "def", "v")}
    spef = verify(receipt["artifacts"]["spef"])
    normalized = sha256()
    with spef.open("rb") as lines:
        for line in lines:
            if not line.startswith(b"*DATE "):
                normalized.update(line)
    views = receipt["views"]
    view_bytes = json.dumps(views, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    metrics = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
    return {"receipt": comparison.bind(endpoint / "receipt.json"), "files": files,
            "spef_except_date_sha256": normalized.hexdigest(), "views_sha256": sha256(view_bytes).hexdigest(),
            "views": {corner: {key: values[key] for key in metrics} for corner, values in views.items()}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    root = parser.parse_args().run.resolve(strict=True)
    manifest = read(root / "config.json")
    verify_protocol(root, manifest)
    inputs = matched.verify_pair_inputs(root, manifest)
    frozen, _, nets, pool, _ = inputs
    actions, edited, incident, hint = reconstruct_hint(manifest, frozen, pool, nets)
    results = read(root / "results.json")
    check(list(results) == list(METHODS), "top-level results omit a serial method")
    verified = {}
    for method in METHODS:
        arm = root / method
        check(results[method] == read(arm / "summary.json"), "arm result differs from its published summary")
        scopes = verify_arm_scopes(arm, actions, edited, incident, hint, nets)
        audited = replay_arm(root, method, inputs, manifest, actions, scopes)
        if verified:
            check(next(reversed(verified.values()))["raw_stop"] <= audited["raw_start"], "arm clocks overlapped or order changed")
        audited.update(operation_counts=verify_operations(root, method, audited), routing_scopes=scopes,
                       endpoint_identity=endpoint_identity(audited["window"]))
        verified[method] = audited
        print(method, audited["window"]["time_to_target_seconds"], audited["window"]["area_saved"], flush=True)
    comparison.save(root / "independent_verification.json", {
        "audit_source": comparison.bind(Path(__file__).resolve()), "configuration": comparison.bind(root / "config.json"),
        "candidate": list(actions), "reconstructed_hint": hint, "arms": verified,
    })


if __name__ == "__main__":
    main()
