#!/usr/bin/env python3
"""Complete one identically censored AES retry outside the timed comparison."""

from argparse import ArgumentParser
from pathlib import Path

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
from run_aes_protected_online import OnlineProtection, drc_neighbor_evidence, process_ledger
from run_screened_matrix import bind_runtime, raw_seconds


def pending_retry(matrix, run, method, baseline_nets):
    d = run / method
    progress_path = d / "progress.json"
    summary_path = d / "summary.json"
    tools_path = d / "subprocesses.json"
    progress = read(progress_path)
    summary = read(summary_path)
    if (progress["stop_reason"] != "end_to_end_wall_cap" or summary["logical_admitted"] != 3
            or summary["logical_finished"] != 2 or len(progress["logical_requests"]) != 3):
        raise ValueError(f"{method} did not censor logical request 3")
    request_dir = d / "03"
    request_path = request_dir / "request.json"
    request = read(request_path)
    if request["actions"] != progress["logical_requests"][2]["actions"]:
        raise ValueError(f"{method} timed action tuple differs from physical request")
    initial = request_dir / "initial"
    unlocked = initial / "unlocked_drc/audit.json"
    if read(unlocked)["drc_markers"] <= 0:
        raise ValueError(f"{method} has no unlocked DRC failure to replay")
    decision_path = request_dir / "retry_decision.json"
    decision = read(decision_path)
    incident = set(request["direct_signal_nets"])
    edited = {comparison.canonical_odb_name(a.partition("=")[0]) for a in request["actions"]}
    reports = [initial / "drc.rpt", initial / "full_drc.rpt", initial / "unlocked_drc/full_drc.rpt"]
    neighbors, markers = drc_neighbor_evidence(reports, incident, edited, baseline_nets)
    if not neighbors or sorted(neighbors) != decision["released_neighbors"] or markers != decision["drc_marker_evidence"]:
        raise ValueError(f"{method} retry does not reconstruct from actual DRC markers")
    attempts = read(tools_path)
    route_log = request_dir / "retry/route.log"
    replay, = [x for x in attempts if Path(x["log"]) == route_log]
    if ("returncode" not in replay or replay["returncode"] is not None
            or replay["effective_timeout_seconds"] >= replay["configured_timeout_seconds"]):
        raise ValueError(f"{method} retry is not an observed window-interrupted DRT")
    if read(initial / "receipt.json")["control_sdc"] != read(matrix / "config.json")["bindings"]["control"]["sdc"]:
        raise ValueError(f"{method} retry uses another SDC")
    bindings = [progress_path, summary_path, tools_path, request_path, decision_path, unlocked,
                initial / "receipt.json", *reports, route_log]
    return tuple(request["actions"]), incident, neighbors, [comparison.bind(path) for path in bindings]


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("old_matrix", type=Path)
    p.add_argument("formal_run", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    matrix = args.old_matrix.resolve(strict=True)
    run = args.formal_run.resolve(strict=True)
    out = args.output.resolve()
    manifest = read(run / "config.json")
    if manifest["matrix"] != comparison.bind(matrix / "config.json"):
        raise ValueError("formal run does not use requested matrix")
    for source in manifest["driver_sources"].values():
        verify(source)
    frozen_def = read(matrix / "config.json")["bindings"]["control"]["def"]
    nets = comparison.def_section(verify(frozen_def), "NETS")
    a, b = (pending_retry(matrix, run, method, nets) for method in ("fixed", "faeco"))
    if a[:3] != b[:3]:
        raise ValueError("timed fixed and FAECO censored different retries")
    actions, incident, neighbors, _ = a
    runner = OnlineProtection(matrix, out)
    comparison.save(out / "diagnostic_scope.json", {
        "physical_recipe": "same original frozen control and exactly the observed timed retry",
        "timed_results_unchanged": True, "actions": actions, "incident": sorted(incident),
        "neighbors": sorted(neighbors), "source_fixed": a[3], "source_faeco": b[3],
        "diagnostic_source": comparison.bind(Path(__file__).resolve()),
    })
    print(f"{len(actions)} fixed edit identities; releasing {', '.join(sorted(neighbors))}", flush=True)
    begin = raw_seconds()
    target = out / "retry"
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]), process_ledger(out / "subprocesses.json", begin + 430):
        _, receipt, failures, _ = runner.physical(actions, target, incident, neighbors)
        proof = {}
        if not failures and not runner.eval.proof(verify(receipt["artifacts"]["v"]), target, proof):
            failures.append("sec")
    comparison.save(out / "result.json", {
        "actions": actions, "failures": failures, "sec_pass": not failures, "proof_operations": proof,
        "elapsed_raw_seconds": raw_seconds() - begin, "formal_window_inclusion": False,
        "receipt": comparison.bind(target / "receipt.json"),
    })
    print(f"censored retry completed: {failures or 'passed gates'}", flush=True)


if __name__ == "__main__":
    main()
