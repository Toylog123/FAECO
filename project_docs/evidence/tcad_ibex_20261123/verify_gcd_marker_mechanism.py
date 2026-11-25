#!/usr/bin/env python3
"""Reconcile GCD's fixed proposal and independently audit its physical scopes."""

from argparse import ArgumentParser
from pathlib import Path

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
from run_gcd_marker_mechanism import PROTOCOL_ORDER
import verify_aes_cold_online as cold
from verify_aes_diagnostic_repair import endpoint_identity
from verify_aes_protected_online import audit_logical, check


def audit(root):
    protocol_path = root / "protocol.json"
    protocol = read(protocol_path)
    published = read(root / "results.json")
    check(tuple(row["method"] for row in published) == PROTOCOL_ORDER, "incomplete or reordered arm results")
    seed = read(verify(protocol["seed"]))
    assets = seed["bindings"]
    for source in protocol["sources"].values():
        verify(source)
    pool = [comparison.PhysicalAction(**row) for row in read(verify(protocol["pool"]))]
    frozen = assets["control"]
    views = read(verify(protocol["reference"]))["views"]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    policy = comparison.BudgetPolicy.from_ps(protocol["gate"]["budget_ps"],
                                              tolerance_ns=comparison.PS_TOLERANCE / 1000)
    zero, reference = audit_logical(root / "preflight/zero", nets, frozen, views, protocol["gate"])
    check(reference.valid and not zero["actions"], "shared zero failed")
    cold.ONLINE = ("online",)
    checked = []
    last = None
    for row in published:
        method, index = row["method"], row["cell"]
        arm = root / f"cell_{index:02d}" / method
        summary = read(arm / "summary.json")
        progress = read(arm / "progress.json")
        start, deadline = progress["start_raw"], progress["deadline_raw"]
        check(last is None or last <= row["outer_start_raw"], "timed arms overlapped")
        check(row["outer_start_raw"] <= start <= summary["stop_raw"] <= row["outer_stop_raw"], "invalid arm boundary")
        check(abs(deadline - start + protocol["charged_screening_seconds"]
                  - protocol["wall_budget_seconds_including_screen"]) < 1e-6,
              "the deadline does not charge shared screening")
        last = row["outer_stop_raw"]
        check(summary == row["result"], "summary differs from the published record")
        requests = cold.audit_requests(arm, assets, pool, nets)
        request, = requests
        check(request["actions"] == protocol["fixed_actions"], "request changed the fixed proposal")
        stopped = progress["logical_requests"][0]
        evidence = {"cell": index, "method": method, "window": summary["window"], "request": request,
                    "subprocesses": comparison.bind(arm / "subprocesses.json"), "failure_reasons": None}
        if request["logical_finished"]:
            check(start <= stopped["admitted_raw"] <= stopped["finished_raw"] < deadline, "late acceptance")
            record, measured = audit_logical(arm / "01", nets, frozen, views, protocol["gate"])
            accepted = comparison.assess(reference, measured, policy).feasible and measured.area < reference.area - 1e-9
            checkpoint, = progress["checkpoints"]
            gain = reference.area - measured.area if accepted else 0.0
            check(checkpoint["accepted"] == accepted and summary["window"]["area_saved"] == gain,
                  "fixed-proposal acceptance cannot be reproduced")
            evidence.update(failure_reasons=record["failures"], final_physical=record["physical_receipt"],
                            endpoint=endpoint_identity(summary["window"]))
        else:
            check(not progress["checkpoints"] and summary["stop_reason"] == "end_to_end_wall_cap",
                  "unfinished request did not meet a wall stop")
        checked.append(evidence)
    return {"protocol": comparison.bind(protocol_path), "shared_zero": zero, "checked": checked,
            "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    report = audit(root)
    comparison.save(root / "independent_verification.json", report)
    print(f"Verified {len(report['checked'])} GCD cells", flush=True)


if __name__ == "__main__":
    main()
