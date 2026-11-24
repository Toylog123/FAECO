#!/usr/bin/env python3
"""Independently audit the AES comparison with fresh, metered pre-DRT diagnostics."""

from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
import math
import re

import compare_ibex as comparison
import verify_aes_incident_priority_matched as matched
from probe_aes_selective_repair import read, verify
from run_aes_protected_online import drc_neighbor_evidence
from verify_aes_diagnostic_repair import audit_guided_retry, endpoint_identity, verify_pass_scope
from verify_aes_marker_repair import incident_signal_nets, verify_operations
from verify_aes_protected_online import check


METHODS = ("fixed", "fixed_online", "faeco")
ONLINE = METHODS[1:]
PREVIEW_COMPLETE = "FAECO_PRE_DRT_DRC_COMPLETE"


def verify_protocol(root, manifest):
    check(manifest["methods"] == list(METHODS) and manifest["diagnostic_methods"] == list(ONLINE)
          and "timeout_classifier" in manifest and manifest["diagnostic_threads"] == 1
          and manifest["diagnostic_timeout_seconds"] == 60.0 and manifest["logical_dispatch_cap"] == 6
          and manifest["wall_window_seconds_including_screen"] == 720.0,
          "unexpected arm order, timeout policy or common work budget")
    check(not {"hint_sources", "diagnostic_sources", "case_actions", "defer_marker_retry_reason"} & manifest.keys()
          and manifest["physical_cache"] == "disabled, no candidate-specific diagnostic input",
          "live experiment declares a historical packet or a different scheduling mechanism")
    preflight = verify(read(root / "transferred_preflight.json")["preflight_result"])
    source = read(preflight.parent.parent / "config.json")
    shared = source.keys() - {"driver_pid", "driver_sources", "methods"}
    check(all(source[key] == manifest[key] for key in shared), "the original frozen physics or constraints changed")
    check(all(manifest["driver_sources"][name] == binding for name, binding in source["driver_sources"].items()),
          "the original route or timing source changed")
    check(manifest["absolute_hold_ps"] == 0 and manifest["relative_hold_tolerance_ps"] == comparison.PS_TOLERANCE
          and manifest["gate"]["budget_ps"] == 36.0 and manifest["area_target_pct"] == 0.01,
          "original acceptance protocol changed")


def verify_preview_script(directory, assets, actions):
    script = directory / "preview.tcl"
    text = script.read_text(encoding="utf-8")
    reads = re.findall(r"(?m)^\s*(read_\w+|source) (.+)$", text)
    expected = [("read_liberty", comparison.tcl(verify(asset))) for asset in assets["used_libraries"]["TT"]]
    expected.extend((
        ("read_db", comparison.tcl(verify(assets["control"]["odb"]))),
        ("read_sdc", comparison.tcl(verify(assets["control"]["sdc"]))),
        ("source", comparison.tcl(verify(assets["flow"]["setRC.tcl"]))),
        ("source", comparison.tcl(verify(assets["flow"]["fastroute.tcl"]))),
    ))
    check(reads == expected, "preview read a non-frozen file or a diagnostic packet")
    names = re.findall(r"(?m)^set inst \[\[ord::get_db_block\] findInst (.+)\]$", text)
    targets = re.findall(r"(?m)^set target \[\[ord::get_db\] findMaster (.+)\]$", text)
    check(names == [comparison.tcl(action.instance) for action in actions for _ in (0, 1)]
          and targets == [comparison.tcl(action.target_cell) for action in actions],
          "preview Tcl applied a different edit tuple")
    end = f'drt::check_drc -output_file {comparison.tcl(directory / "full_drc.rpt")}\nputs {PREVIEW_COMPLETE}\nexit'
    check(text.rstrip().endswith(end) and text.count("drt::check_drc ") == 1
          and "odb::dbWire_destroy $wire" in text
          and not re.search(r"(?m)^\s*(?:detailed_route|global_route|extract_parasitics|write_\w+|read_guides)\s", text),
          "preview did work other than the swap, erase and fresh DRC check")
    return script


def reconstruct_diagnosis(tool, report, edited, incident, nets):
    status = comparison.ProcessResult(**{key: tool[key] for key in ("returncode", "wall_seconds", "timeout_seconds", "log")})
    count, failure, evidence, neighbors = None, None, [], set()
    try:
        text = comparison.checked_output(status, PREVIEW_COMPLETE)
        touched = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", text))
        clears = re.findall(r"(?m)^IBEX_CLEARED_SIGNAL_WIRES (\d+)$", text)
        expected_clears = sum("+ ROUTED " in nets[net] or "+ FIXED " in nets[net] for net in incident)
        if touched != incident or clears != [str(expected_clears)] or not report.is_file():
            raise comparison.TrialFailure("preview did not clear the expected direct wires or report DRC")
        contents = report.read_text(encoding="utf-8")
        count = len(re.findall(r"(?m)^violation type: ", contents))
        if not count and contents.strip():
            raise comparison.TrialFailure("unrecognized preview DRC report")
        neighbors, evidence = drc_neighbor_evidence((report,), incident, edited, nets)
        if len(evidence) != count:
            neighbors = set()
    except comparison.TrialFailure as error:
        failure = str(error)
    flags = {"marker_count": count, "marker_evidence": evidence, "failure": failure,
             "released_neighbors": sorted(neighbors),
             "status": "unavailable" if failure else "guided" if neighbors else "no_complete_guidance"}
    return neighbors, flags


def audit_diagnosis(directory, request, tools, physical_tools, assets, pool, edited, incident, nets, deadline):
    check(len(tools) <= 1, "requested multiple fresh diagnostics for one edit tuple")
    receipt_path = directory / "diagnosis.json"
    preview_log = directory / "preview.log"
    if tools:
        tool, = tools
        script = verify_preview_script(directory, assets, [pool[key] for key in request["actions"]])
        expected_command = [str(verify(assets["tools"]["openroad"])), "-no_init", "-no_splash",
                            "-threads", "1", "-exit", str(script)]
        check(Path(tool["log"]) == preview_log and tool["command"] == expected_command
              and tool["configured_timeout_seconds"] == 60.0 and request["admitted_raw"] <= tool["start_raw"],
              "preview command, thread count or time did not match the admitted cold request")
    if not receipt_path.exists():
        check(not physical_tools and "finished_raw" not in request, "physical work began without a fresh diagnosis")
        if tools:
            check((tool["returncode"] is None and tool["timeout_bound"] == "wall") or tool["stop_raw"] >= deadline,
                  "preview ended before the wall without a diagnosis receipt")
        return set(), {"status": "window_censored" if tools else "not_started", "completed": False,
                       "preview_tool_started": bool(tools)}
    check(len(tools) == 1, "diagnosis receipt has no timed diagnostic process")
    receipt = read(receipt_path)
    check(receipt["actions"] == request["actions"] and receipt["incident_nets"] == sorted(incident)
          and verify(receipt["script"]) == script, "diagnosis record did not come from this edit tuple and script")
    check(request["admitted_raw"] <= receipt["start_raw"] <= tool["start_raw"] <= tool["stop_raw"] <= receipt["stop_raw"]
          and receipt["seconds"] == receipt["stop_raw"] - receipt["start_raw"]
          and (not physical_tools or receipt["stop_raw"] <= physical_tools[0]["start_raw"]),
          "diagnosis and physical work were not sequenced or charged correctly")
    check("finished_raw" not in request or receipt["stop_raw"] <= request["finished_raw"],
          "request finished before its preview")
    report = directory / "full_drc.rpt"
    if receipt["report"] is not None:
        check(verify(receipt["report"]) == report, "diagnosis reused an external report")
    else:
        check(not report.exists(), "missing binding for a diagnostic report")
    neighbors, flags = reconstruct_diagnosis(tool, report, edited, incident, nets)
    check(all(receipt[key] == value for key, value in flags.items()), "released neighbors do not reconstruct from live markers")
    return neighbors, {"receipt": comparison.bind(receipt_path), "log": comparison.bind(preview_log), "report": receipt["report"],
                       "status": flags["status"], "markers": flags["marker_count"], "released": sorted(neighbors),
                       "completed": True, "preview_tool_started": True, "seconds": receipt["seconds"]}


def audit_physical(directory, request, tools, edited, incident, initial_neighbors, nets):
    initial = directory / "initial"
    completed = "finished_raw" in request
    if not (initial / "routing_scope.json").exists():
        check(not tools and not completed, "physical request or completed result has no routing scope")
        return {}
    original = read(directory / "request.json")
    check(original["actions"] == request["actions"] and original["direct_signal_nets"] == sorted(incident),
          "physical route used a different logical request")
    scopes = {"initial": verify_pass_scope(initial, incident, initial_neighbors, nets, (initial / "receipt.json").exists())}
    retry = directory / "retry"
    if retry.exists():
        reports = (initial / "drc.rpt", initial / "full_drc.rpt", initial / "unlocked_drc/full_drc.rpt")
        failures = set(read(initial / "assessment.json")["failures"])
        drc_failures = {"drc", "full_drc", "unlocked_drc"}
        check(failures & drc_failures and all(reason.startswith(("FF:", "TT:", "SS:")) for reason in failures - drc_failures),
              "retry followed a nonrepairable or non-DRC failure")
        added, evidence = drc_neighbor_evidence(reports, incident | initial_neighbors, edited, nets)
        recorded = read(directory / "retry_decision.json")
        check(added and not added & (incident | initial_neighbors) and recorded["released_neighbors"] == sorted(added)
              and recorded["drc_marker_evidence"] == evidence, "follow-up did not exclusively add newly marked neighbors")
        scopes["retry"] = verify_pass_scope(retry, incident, initial_neighbors | added, nets, (retry / "receipt.json").exists())
    for name in scopes:
        stages = [row for row in tools if Path(row["log"]).is_relative_to(directory / name)]
        route_stages = [row for row in stages if Path(row["log"]).name == "route.log"]
        check(not stages or stages[0] in route_stages and len(route_stages) == 1, "physical pass ran extra DRT or omitted its DRT")
        audit = directory / name / "routing_audit.json"
        if completed and "artifacts" in read(directory / name / "receipt.json"):
            check(audit.is_file(), "completed extracted layout has no protected geometry audit")
        if audit.exists():
            route = read(audit)
            check(not route["changed_protected_nets"] and not route["changed_untouched_nets"],
                  "prior physical audit found changes outside its permitted scope")
            scopes[name]["routing_audit"] = comparison.bind(audit)
    check(all(any(Path(tool["log"]).is_relative_to(directory / name) for name in scopes) for tool in tools),
          "tool ran outside an authorized physical pass")
    if completed:
        result = read(directory / "result.json")
        receipt = verify(result["physical_receipt"])
        check(result["passes"] == list(scopes) and receipt == directory / result["passes"][-1] / "receipt.json"
              and Path(result["endpoint"]["evidence_id"]) == receipt.parent, "completed endpoint came from elsewhere")
        measured = read(receipt)["endpoint"]
        check(all(result["endpoint"][key] == value for key, value in measured.items() if key not in ("valid", "sec_pass")),
              "physical and logical endpoint metrics disagree")
    return scopes


def audit_requests(arm, assets, pool, nets):
    progress = read(arm / "progress.json")
    requests = progress["logical_requests"]
    preview_tools, physical_tools = defaultdict(list), defaultdict(list)
    previous_end = progress["start_raw"]
    previous_seq = 1
    for row in read(arm / "subprocesses.json"):
        path = Path(row["log"]).relative_to(arm)
        is_preview = path.parts[0] == "diagnosis"
        seq = int(path.parts[1] if is_preview else path.parts[0])
        check(previous_seq <= seq <= len(requests) and previous_end <= row["start_raw"] <= row["stop_raw"]
              and requests[seq - 1]["admitted_raw"] <= row["start_raw"], "tool work was out of request order")
        check("finished_raw" not in requests[seq - 1] or row["stop_raw"] <= requests[seq - 1]["finished_raw"],
              "request finished while its tool was still running")
        previous_end, previous_seq = row["stop_raw"], seq
        (preview_tools if is_preview else physical_tools)[seq].append(row)
    index = {action.action_id: action for action in pool}
    outcomes = []
    for request in requests:
        seq = request["id"]
        edited, incident = incident_signal_nets(request["actions"], nets)
        preview = arm / "diagnosis" / f"{seq:02d}"
        if arm.name in ONLINE:
            neighbors, diag = audit_diagnosis(preview, request, preview_tools[seq], physical_tools[seq], assets,
                                              index, edited, incident, nets, progress["deadline_raw"])
        else:
            check(not preview_tools[seq] and not preview.exists(), "ordinary fixed arm used preview guidance")
            neighbors, diag = set(), None
        stages = audit_physical(arm / f"{seq:02d}", request, physical_tools[seq], edited, incident, neighbors, nets)
        outcomes.append({"id": seq, "actions": request["actions"], "diagnosis": diag, "physical": stages,
                         "logical_finished": "finished_raw" in request})
    return outcomes


def replay_arm(root, method, manifest, inputs, requests):
    frozen, views, nets, pool, reference = inputs
    original_schedule = comparison.run_method
    original_audit = matched.audit_logical
    guided_retries = {f"{row['id']:02d}" for row in requests if "retry" in row["physical"]
                      and row["physical"]["initial"]["released"]}

    def schedule(name, *args, **kwargs):
        return original_schedule("fixed" if name == "fixed_online" else name, *args, **kwargs)

    def logical(directory, baseline_nets, frozen, views, gate):
        if directory.name in guided_retries:
            return audit_guided_retry(directory, frozen, views, gate)
        return original_audit(directory, baseline_nets, frozen, views, gate)

    try:
        comparison.run_method, matched.audit_logical = schedule, logical
        return matched.audit_arm(root, method, manifest, pool, reference, views, frozen, nets)
    finally:
        comparison.run_method, matched.audit_logical = original_schedule, original_audit


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    root = parser.parse_args().run.resolve(strict=True)
    manifest = read(root / "config.json")
    verify_protocol(root, manifest)
    inputs = matched.verify_pair_inputs(root, manifest)
    assets = read(verify(manifest["matrix"]))["bindings"]
    _, _, nets, pool, _ = inputs
    strategies = read(root / "results.json")
    check(list(strategies) == list(METHODS), "run is missing a method or changed execution order")
    audited = {}
    common_first = sorted(action.action_id for action in pool[:manifest["batch_size"]])
    for method in METHODS:
        arm = root / method
        check(strategies[method] == read(arm / "summary.json"), "published result disagrees with its physical arm")
        requests = audit_requests(arm, assets, pool, nets)
        check(requests and requests[0]["actions"] == common_first, "methods differ before the first physical proposal")
        result = replay_arm(root, method, manifest, inputs, requests)
        if audited:
            check(next(reversed(audited.values()))["raw_stop"] <= result["raw_start"], "methods overlapped in time")
        diagnostics = [item["diagnosis"] for item in requests if item["diagnosis"] is not None]
        counts = verify_operations(root, method, result)
        counts.update({"diagnostics_started": sum(row["preview_tool_started"] for row in diagnostics),
                       "diagnoses_completed": sum(row["completed"] for row in diagnostics),
                       "diagnoses_guided": sum(row["status"] == "guided" for row in diagnostics),
                       "diagnoses_unavailable": sum(row["status"] == "unavailable" for row in diagnostics),
                       "completed_diagnosis_seconds": math.fsum(row["seconds"] for row in diagnostics if row["completed"])})
        result.update(requests=requests, operation_counts=counts, selected_identity=endpoint_identity(result["window"]))
        audited[method] = result
        print(method, result["logical_finished"], result["logical_admitted"], result["window"]["area_saved_pct"], flush=True)
    comparison.save(root / "independent_verification.json", {
        "audit_source": comparison.bind(Path(__file__).resolve()), "configuration": comparison.bind(root / "config.json"),
        "arms": audited,
    })


if __name__ == "__main__":
    main()
