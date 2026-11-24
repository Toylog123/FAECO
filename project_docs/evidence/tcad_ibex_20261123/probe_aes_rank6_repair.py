#!/usr/bin/env python3
"""Test one equal-area launch-clock donor substitution in rejected AES ranks 4–9."""

from argparse import ArgumentParser
from pathlib import Path
import math

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
from run_aes_protected_online import OnlineProtection, drc_neighbor_evidence, process_ledger
from run_screened_matrix import bind_runtime, raw_seconds


RANKS_4_TO_9 = ("_11178_", "_11724_", "_12777_", "_12929_", "_13098_", "_13122_")
DONOR = "_21033_"


def instance(action):
    return comparison.canonical_odb_name(action.partition("=")[0])


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("matrix", type=Path)
    p.add_argument("formal_run", type=Path)
    p.add_argument("rejected_result", type=Path)
    p.add_argument("donor_direction", type=Path)
    p.add_argument("donor_qualified", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--omit", choices=RANKS_4_TO_9[3:], required=True)
    ns = p.parse_args()
    matrix = ns.matrix.resolve(strict=True)
    formal = ns.formal_run.resolve(strict=True)
    cut = ns.rejected_result.resolve(strict=True)
    donor_direction = ns.donor_direction.resolve(strict=True)
    donor_qualified = ns.donor_qualified.resolve(strict=True)
    out = ns.out.resolve()
    old = read(cut)
    old_path = verify(old["receipt"])
    old_physical = read(old_path)
    if (old["formal_window_inclusion"] is not False or set(map(instance, old["actions"])) != set(RANKS_4_TO_9)
            or tuple(old["actions"]) != tuple(old_physical["actions"])
            or set(old["failures"]) != {"FF:hold_regression", "TT:hold_regression"}):
        raise ValueError("expected the rejected six original rank4–9 edits")
    for item in old_physical["artifacts"].values():
        verify(item)
    matrix_cfg = comparison.bind(matrix / "config.json")
    if read(formal / "config.json")["matrix"] != matrix_cfg:
        raise ValueError("formal experiment used a different frozen matrix")
    donor = read(donor_direction)
    if donor["matrix_config"] != matrix_cfg:
        raise ValueError("donor timing paired against a different frozen matrix")
    verify(donor["ordinary_zero"])
    verify(donor["donor_receipt"])
    action, = donor["donor_actions"]
    if instance(action) != DONOR or donor["changed_clock_nets_relative_to_ordinary_zero"]:
        raise ValueError("invalid donor comparison")
    proof_row, = read(donor_qualified).values()
    proof_physical = read(verify(proof_row["physical_receipt"]))
    sec = proof_row.get("sec")
    if proof_row["failures"] or not sec or action not in proof_physical["actions"]:
        raise ValueError("expected previously qualified physical donor batch")
    proof = read(verify(sec["log"]).parent / "sec/receipt.json")
    if not proof["passed"] or proof["unproven"] or proof["gate"] != proof_physical["artifacts"]["v"]:
        raise ValueError("donor SEC identity mismatch")
    verify(proof["gate"])

    runner = OnlineProtection(matrix, out)
    actions = tuple(sorted([key for key in old["actions"] if instance(key) != ns.omit] + [action]))
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        edited, incident = runner.direct_nets(actions)
        _, donor_incident = runner.direct_nets((action,))
        prior = formal / "fixed/03/initial"
        reports = [prior / "drc.rpt", prior / "full_drc.rpt", prior / "unlocked_drc/full_drc.rpt"]
        retained_neighbors, evidence = drc_neighbor_evidence(reports, incident, edited, runner.nets)
        old_neighbors = set(read(old_path.with_name("routing_scope.json"))["released_neighbors"])
        donor_extra = set(donor["changed_nets_relative_to_ordinary_zero"]) - donor_incident
        if not retained_neighbors <= old_neighbors or donor_extra != {"net8148"}:
            raise ValueError("unexpected neighbor sites in the preserved DRC evidence")
        released = retained_neighbors | donor_extra
        if released & incident or any("+ USE SIGNAL" not in runner.nets[net] for net in released):
            raise ValueError("repair must release only non-clock, non-incident neighbors")
        comparison.save(out / "repair_plan.json", {
            "driver": comparison.bind(Path(__file__).resolve()), "rejected_result": comparison.bind(cut),
            "rejected_route_receipt": comparison.bind(old_path), "donor_direction": comparison.bind(donor_direction),
            "donor_qualification": comparison.bind(donor_qualified),
            "original_formal_marker_reports": [comparison.bind(path) for path in reports],
            "marker_evidence_for_preserved_edit_nets": evidence, "donor_neighbor_nets": sorted(donor_extra),
            "actions": actions, "omitted_instance": ns.omit,
            "incident_nets": sorted(incident), "initial_released_nets": sorted(released),
            "protected_net_count": len(runner.nets) - len(incident | released),
            "target_area_equal_to_rejected_proposal": old_physical["area_saved"],
            "formal_window_inclusion": False, "maximum_drt_attempts": 2,
        })
        print(f"replace {ns.omit} with {DONOR}: {len(incident)} incident + {len(released)} released", flush=True)
        begin = raw_seconds()
        deadline = begin + 714.0
        with process_ledger(out / "subprocesses.json", deadline):
            used = ["candidate"]
            ep, row, failures, active_reports = runner.physical(actions, out / used[-1], incident, released)
            drc_errors = {"drc", "full_drc", "unlocked_drc"}
            if active_reports and set(failures).intersection(drc_errors):
                unsafe = {x for x in set(failures) - drc_errors if not x.startswith(("FF:", "TT:", "SS:"))}
                if not unsafe:
                    new_neighbors, sources = drc_neighbor_evidence(active_reports, incident | released, edited,
                                                                  runner.nets)
                    comparison.save(out / "retry_decision.json", {
                        "additional_nonclock_nets": sorted(new_neighbors), "sources": sources,
                    })
                    if new_neighbors:
                        used.append("drc_retry")
                        ep, row, failures, _ = runner.physical(actions, out / used[-1], incident,
                                                               released | new_neighbors)
            measured_area = row.get("area_saved")
            if measured_area is None or not math.isclose(
                measured_area, old_physical["area_saved"], rel_tol=0, abs_tol=1e-6,
            ):
                failures.append("equal_area_target")
            proof_operations = {}
            if not failures and not runner.eval.proof(verify(row["artifacts"]["v"]), out / used[-1],
                                                       proof_operations):
                failures.append("sec")
        comparison.save(out / "result.json", {
            "actions": actions, "physical_attempts": used, "failures": failures,
            "receipt": comparison.bind(out / used[-1] / "receipt.json"),
            "scope": comparison.bind(out / used[-1] / "routing_audit.json") if "artifacts" in row else None,
            "proof_operations": proof_operations, "sec_pass": not failures,
            "area_saved": measured_area, "elapsed_raw_seconds": raw_seconds() - begin,
        })
        print(f"repair {ns.omit}: {failures or 'passed gates'}", flush=True)


if __name__ == "__main__":
    main()
