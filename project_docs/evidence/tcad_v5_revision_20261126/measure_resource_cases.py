#!/usr/bin/env python3
"""Measure three previously qualified physical requests in separate Linux scopes."""

import argparse
from contextlib import contextmanager
from dataclasses import asdict
import os
from pathlib import Path
import re

from measure_stage5_resources import scope_snapshot
from probe_aes_selective_repair import audit_timing
from run_v5_step3_multibudget_online import (
    WallWindowEnded, apply_search_budget, bind_runtime, cmp, lr_mod, process_ledger,
    qualified, raw_seconds,
)
from verify_review_evidence import NAMES, SHA256


CASES = {
    "asap7_uart": (3, "asap7_uart::1.0pct", "trials", "16",
                  "a8590c1e962c52f70829990231986ecb0136014cdb8429eec65723e2bb81ef6c", 567),
    "sky130hd_aes": (4, "sky130hd_aes::0s", "phase2_fallback", "03",
                    "50f64ef0d3b2e2fef1120af5f2d2e9ef59f71d90779a61e46fdf71cc91fab4d1", 11089),
    "asap7_aes": (4, "asap7_aes::0s", "phase2_fallback", "01",
                 "6c30e0bee61811ae3d52fbe67ebdf8b694f0db862b1bbcf6f82c9028c8d83b7c", 10027),
}
TOOLS = {
    "preview.log": "boxed_drc_preview", "route.log": "detailed_route_and_rcx",
    "sta_FF.log": "sta_ff", "sta_TT.log": "sta_tt", "sta_SS.log": "sta_ss",
    "audit.log": "independent_unlocked_drc", "sec.log": "sec",
}
VIEWS = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps", "electrical")
ARTIFACTS = ("odb", "def", "v", "spef")
read, verify = qualified.read, qualified.verify


def check_endpoint(result, directory, control, evaluator, timing_gate, proved):
    """Collect the actual gates and bind only artifacts produced by this candidate."""
    endpoint = result["endpoint"]
    physical_path = verify(result["physical_receipt"])
    target = physical_path.parent
    if target != Path(endpoint["evidence_id"]) or target.parent != directory:
        raise ValueError("physical receipt is outside the candidate directory")
    physical = read(physical_path)
    artifacts = physical.get("artifacts", {})
    for ext in ARTIFACTS:
        if ext in artifacts and verify(artifacts[ext]) != target / f"routed.{ext}":
            raise ValueError(f"candidate {ext} binding names a different output")
    audit, sec = target / "unlocked_drc/audit.json", target / "sec/receipt.json"
    assessment_path = target / "assessment.json"
    assessment = read(assessment_path) if assessment_path.is_file() else {}
    proof = read(sec) if sec.is_file() else {}
    antenna = [int(n) for n in re.findall(r"(?m)^AES_SELECTIVE_ANTENNA (\d+)(?:\.0)?\s*$",
                                          (target / "route.log").read_text(errors="replace"))]
    views = {corner: {metric: view[metric] for metric in VIEWS}
             for corner, view in physical.get("views", {}).items()}
    envelope = (cmp.joint_failures(evaluator.ref_views, physical["views"], check_setup=False)
                if set(views) == set(cmp.CORNERS) else ["incomplete_sta_views"])
    setup = audit_timing(evaluator, physical, timing_gate, False) if views else ["incomplete_sta_views"]
    gate = {
        "backend_failures": result["failures"], "physical_failures": physical["failures"],
        "hold_port_and_drv_recheck": envelope, "setup_recheck": setup,
        "protected_assessment_failures": assessment.get("failures"),
        "complete_routing": physical.get("routed_to_completion", False),
        "complete_extraction": physical.get("extracted_to_completion", False),
        "initial_drt_violations": physical.get("drc_violations"),
        "unlocked_drc_markers": read(audit)["drc_markers"] if audit.is_file() else None,
        "antenna_counts": antenna, "sec_passed": proof.get("passed", False),
        "sec_proven": proof.get("proven"), "sec_unproven": proof.get("unproven"),
    }
    accepted = (
        physical["actions"] == result["actions"] and endpoint["valid"] and endpoint["sec_pass"]
        and not (gate["backend_failures"] or gate["physical_failures"] or envelope or setup)
        and gate["protected_assessment_failures"] == [] and gate["complete_routing"]
        and gate["complete_extraction"] and gate["initial_drt_violations"] == 0
        and gate["unlocked_drc_markers"] == 0 and antenna == [0] and set(views) == set(cmp.CORNERS)
        and gate["sec_passed"] and gate["sec_proven"] == proved and gate["sec_unproven"] == 0
        and all(ext in artifacts for ext in ARTIFACTS)
        and proof.get("gate") == artifacts["v"] and proof.get("gold") == control["v"]
        and physical.get("control_sdc") == control["sdc"]
    )
    if proof:
        verify(proof["gold"])
        verify(proof["gate"])
    return {"qualified": accepted, "gates": gate, "views": views, "artifacts": artifacts,
            "area_saved_um2": physical.get("area_saved"), "elapsed_attempt_s": result["elapsed_seconds"],
            "physical": result["physical_receipt"],
            "assessment": cmp.bind(assessment_path) if assessment else None,
            "drc": cmp.bind(audit) if audit.is_file() else None,
            "sec": cmp.bind(sec) if sec.is_file() else None}


def prepare(case, output):
    step, key, phase, task, result_hash, proved = CASES[case]
    review = Path(__file__).resolve().parent / NAMES[step]
    if cmp.sha(review) != SHA256[step]:
        raise ValueError("published V5 comparison changed")
    row = read(review)["runs"][key]
    source_run = Path(row["raw_directory"] if step == 3 else row["run_dir"])
    source = source_run / phase / task
    result_path = source / "result.json"
    if cmp.sha(result_path) != result_hash:
        raise ValueError("frozen accepted candidate receipt changed")
    result = read(result_path)
    actions = tuple(result["actions"])
    protocol = read(verify(row["protocol"] if step == 3 else row["run_config"]))
    old_ledger = (source_run if step == 3 else source.parent) / "subprocesses.json"
    ledger = read(verify(row["subprocess_ledger"]) if step == 3 else old_ledger)
    old_tools = [item for item in ledger if Path(item["log"]).is_relative_to(source)
                 or Path(item["log"]).is_relative_to(source.parent / "diagnosis" / task)]
    if [Path(item["log"]).name for item in old_tools] != list(TOOLS) or any(
        item["returncode"] != 0 for item in old_tools
    ):
        raise ValueError("frozen candidate lacks its seven successful tool stages")
    deadline = next(item["start_raw"] + item["effective_timeout_seconds"] for item in ledger
                    if item["timeout_bound"] == "wall")
    original_remaining_s = deadline - old_tools[0]["start_raw"]
    if not old_tools[0]["start_raw"] < old_tools[-1]["stop_raw"] < deadline:
        raise ValueError("frozen candidate did not complete inside the original deadline")

    output.mkdir()
    runner, _, _, _, _ = lr_mod.make_boxed_runner(case, output / "runner")
    runner.initial_hint = set()
    runner.use_preview = True
    if step == 3:
        apply_search_budget(runner, row["clock_period_ps"], row["setup_budget_pct"])
    control = {name: cmp.bind(path) for name, path in runner.eval.control.items()}
    frozen = check_endpoint(result, source, control, runner.eval, runner.gate, proved)
    matrix = read(runner.matrix / "config.json")
    for corner, libraries in matrix["bindings"]["used_libraries"].items():
        if runner.eval.libraries[corner] != [verify(binding) for binding in libraries]:
            raise ValueError(f"libraries drifted for {corner}")
    if step == 3:
        expected = [item["action_id"] for item in protocol["ordered_pool"]]
        pool_ok = [item.action_id for item in runner.pool] == expected
        for name in ("driver", "boxed_backend", "preflight"):
            verify(protocol[name])
        if (control != protocol["control"] or runner.eval.ref_views != protocol["base_views"]
                or qualified.sweep.gate_summary(runner.gate, runner.eval.ref_views) != protocol["gate"]):
            raise ValueError("UART reference, timing or electrical gate changed")
    else:
        pool_ok = sorted(item.action_id for item in runner.pool) == protocol["pool_actions"]
        for name in ("source", "runner_source", "boxed_backend"):
            verify(protocol[name])
        if (runner.gate.wns_ps != protocol["setup_wns_budget_ps"]
                or runner.batch != protocol["batch_size"]
                or not protocol["nominal_tau_probe_s"] == 0):
            raise ValueError("AES budget, batch width or source arm changed")
    if (not pool_ok or len(runner.pool) != 18 or not set(actions) <= runner.eval.actions.keys()
            or runner.eval.scope != result["scope_id"] or not frozen["qualified"]):
        raise ValueError("frozen candidate, timing scope or source pool changed")
    sources = {"candidate": cmp.bind(result_path), "comparison": cmp.bind(review),
               "tool_ledger": cmp.bind(old_ledger), "matrix": cmp.bind(runner.matrix / "config.json"),
               "reference": control, "frozen_result": frozen}
    screen_key = "charged_screening_seconds" if step == 3 else "charged_screening_s"
    cfg = {"case": case, "actions": actions, "original_remaining_s": original_remaining_s,
           "expected_sec_proven": proved, "source_screen_charge_s": protocol[screen_key],
           "route_threads": runner.eval.args.threads, "affinity": sorted(os.sched_getaffinity(0)),
           "gate": qualified.sweep.gate_summary(runner.gate, runner.eval.ref_views),
           "driver": cmp.bind(Path(__file__)), "sources": sources, "source_tools": old_tools}
    cmp.save(output / "protocol.json", cfg)
    return runner, cfg


def cpu_delta(before, after):
    return {key: after["cpu_usec"][key] - value for key, value in before["cpu_usec"].items()}


@contextmanager
def measure_tools(scope, stages):
    source = cmp.run_process

    def invoke(argv, logfile, timeout, *, env=None):
        before = scope_snapshot(scope)
        result = source(argv, logfile, timeout, env=env)
        after = scope_snapshot(scope)
        stages.append({"stage": TOOLS.get(logfile.name, logfile.name), **asdict(result),
                       "before": before, "after": after, "cpu_usec_delta": cpu_delta(before, after)})
        return result

    cmp.run_process = invoke
    try:
        yield
    finally:
        cmp.run_process = source


def measure(case, output, scope):
    runner, cfg = prepare(case, output)
    target = runner.output / "candidate"
    stages = []
    result, error = None, None
    with (bind_runtime(runner.top, runner.flow["fastroute.tcl"]), qualified.qualified_ranking(),
          qualified.qualified_process_clock(), measure_tools(scope, stages)):
        before = scope_snapshot(scope)
        begun = raw_seconds()
        deadline = begun + cfg["original_remaining_s"]
        ledger = output / "subprocesses.json"
        try:
            with process_ledger(ledger, deadline):
                _, result = runner.attempt(cfg["actions"], target)
        except (WallWindowEnded, cmp.TrialFailure) as exc:
            error = {"type": type(exc).__name__, "detail": str(exc)}
        after = scope_snapshot(scope)
    actual = (check_endpoint(result, target, cfg["sources"]["reference"], runner.eval, runner.gate,
                             cfg["expected_sec_proven"]) if result else None)
    def comparable_command(row, root, candidate, diag):
        return [arg.replace(str(candidate), "<candidate>").replace(str(diag), "<diagnosis>")
                .replace(str(root), "<runner>") for arg in row["command"]]

    old_source = Path(cfg["sources"]["candidate"]["path"]).parent
    old_root = old_source.parent.parent
    old_diagnosis = old_source.parent / "diagnosis" / old_source.name
    new_diagnosis = runner.output / "diagnosis" / target.name
    old_tools, new_tools = cfg["source_tools"], read(ledger) if ledger.is_file() else []
    commands_match = len(old_tools) == len(new_tools) and all(
        comparable_command(old, old_root, old_source, old_diagnosis)
        == comparable_command(new, runner.output, target, new_diagnosis)
        and old["configured_timeout_seconds"] == new["configured_timeout_seconds"]
        for old, new in zip(old_tools, new_tools)
    )
    frozen = cfg["sources"]["frozen_result"]
    differences = {
        "tool_commands_match_after_output_relocation": commands_match,
        "gates_equal": bool(actual and actual["gates"] == frozen["gates"]),
        "area_saved_equal": bool(actual and actual["area_saved_um2"] == frozen["area_saved_um2"]),
        "timing_and_electrical_equal": bool(actual and actual["views"] == frozen["views"]),
        "artifact_bytes_equal": {ext: bool(actual and ext in actual["artifacts"] and
                                           actual["artifacts"][ext]["sha256"] == frozen["artifacts"][ext]["sha256"])
                                 for ext in ARTIFACTS},
    }
    cmp.save(output / "MEASUREMENT.json", {
        "protocol": cmp.bind(output / "protocol.json"), "scope": str(scope),
        "tool_ledger": cmp.bind(ledger) if ledger.is_file() else None,
        "before": before, "after": after, "candidate_deadline_raw": deadline,
        "candidate_wall_seconds": after["raw"] - begun, "candidate_cpu_usec": cpu_delta(before, after),
        "scope_peak_memory_bytes": after["memory_peak_bytes"], "stages": stages,
        "result": actual, "comparison": differences, "error": error,
    })
    print(f"{case}: {len(stages)} tool stages, qualified={bool(actual and actual['qualified'])}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preflight", action="store_true", help="bind frozen inputs without launching EDA")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.preflight:
        _, cfg = prepare(args.case, output)
        print(f"{args.case}: {len(cfg['actions'])} frozen actions, {cfg['original_remaining_s']:.2f} s remaining")
        return
    scope_name = Path("/proc/self/cgroup").read_text().strip().removeprefix("0::/")
    scope = Path("/sys/fs/cgroup") / scope_name
    if (not scope.name.startswith("faeco-v4-") or not scope.name.endswith(".scope")
            or (scope / "cgroup.procs").read_text().split() != [str(os.getpid())]
            or os.sched_getaffinity(0) != set(range(6))):
        parser.error("run alone in a fresh faeco-v4-*.scope with taskset -c 0-5")
    measure(args.case, output, scope)


if __name__ == "__main__":
    main()
