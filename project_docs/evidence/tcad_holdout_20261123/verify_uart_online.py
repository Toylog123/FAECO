#!/usr/bin/env python3
"""Reconstruct UART diagnostic scopes, scheduler traces and charged endpoints."""

from argparse import ArgumentParser
from pathlib import Path
import sys


IBEX = Path(__file__).resolve().parents[1] / "tcad_ibex_20261123"
sys.path.insert(0, str(IBEX))

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify
from verify_aes_cold_online import verify_operations
import verify_aes_cold_online as cold
from verify_aes_factorial import accepted_checkpoints
from verify_aes_greedy_matched import verify_opening
from verify_aes_protected_online import audit_logical, check


ORDER = ("single", "fixed_online", "faeco", "faeco", "fixed_online", "single")


def audit(root, count):
    protocol_path = root / "protocol.json"
    protocol = read(protocol_path)
    check(tuple(protocol["order"]) == ORDER and protocol["area_target_pct"] == 0.01
          and protocol["wall_window_seconds_including_screen"] == 720.0
          and protocol["logical_dispatch_cap"] == 6 and protocol["batch_size"] == 3,
          "unexpected registered comparison settings")
    for source in protocol["sources"].values():
        verify(source)
    seed = read(verify(protocol["seed"]))
    check((seed["top"], seed["pdk"], seed["route_guide_source"]) ==
          ("uart", "asap7", "embedded in frozen CONTROL ODB"), "wrong physical reference")
    assets = seed["bindings"]
    frozen = assets["control"]
    qualification = read(verify(assets["qualification_receipt"]))
    verify(qualification["adapted_qualification"]["source"])
    for path in frozen.values():
        verify(path)
    comparison.qualify_binding(qualification, assets)
    views = read(verify(protocol["reference"]))["views"]
    screen = read(verify(protocol["screen_input"]["receipt"]))
    pool_rows = read(verify(protocol["screen_input"]["pool"]))
    check(screen["wall_seconds"] == protocol["charged_screening_seconds_per_arm"]
          and screen["pool_sha256"] == protocol["screen_input"]["pool"]["sha256"]
          and pool_rows == protocol["ordered_pool"] and len(pool_rows) == screen["passed"] == 18,
          "common screen identity or cost differs")
    pool = [comparison.PhysicalAction(**row) for row in pool_rows]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    zero_row, reference = audit_logical(root / "preflight/zero", nets, frozen, views, protocol["gate"])
    check(reference.valid and not zero_row["actions"], "strict zero reference did not qualify")
    zero_path = verify(zero_row["physical_receipt"])
    check(read(zero_path)["artifacts"]["v"]["sha256"] == frozen["v"]["sha256"], "strict zero changed the netlist")
    results_path = root / "results.json"
    published = read(results_path)
    check(count <= len(published) <= len(ORDER), "required serial results are missing")
    manifest = dict(protocol, relative_hold_tolerance_ps=protocol["hold_tolerance_ps"], timeout_classifier=True)
    cold.ONLINE = tuple(set(ORDER))
    cells = []
    previous_stop = 0.0
    for index, method in enumerate(ORDER[:count], 1):
        cell = root / f"cell_{index:02d}"
        arm = cell / method
        summary = read(arm / "summary.json")
        check(published[index - 1] == {"cell": index, "method": method, "result": summary}, "wrong serial outcome")
        progress = read(arm / "progress.json")
        check(previous_stop <= progress["start_raw"] < summary["stop_raw"], "timed arms overlapped")
        previous_stop = summary["stop_raw"]
        verify_opening(method, progress["logical_requests"], pool, protocol["batch_size"])
        requests = cold.audit_requests(arm, assets, pool, nets)
        audited = cold.replay_arm(cell, method, manifest, (frozen, views, nets, pool, reference), requests)
        operations = verify_operations(cell, method, audited)
        accepted, first, best = accepted_checkpoints(arm, audited, reference, requests)
        cells.append({"cell": index, "summary": comparison.bind(arm / "summary.json"), "method": method,
                      "window": audited["window"], "operations": operations,
                      "accepted": accepted, "first_target": first, "best": best,
                      "requests": requests})
    return {"producer_protocol": comparison.bind(protocol_path), "verified_cells": cells,
            "reference": {"endpoint": zero_row["endpoint"], "views": views},
            "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--prefix", type=int, choices=range(1, 7), default=6)
    args = parser.parse_args()
    report = audit(args.root.resolve(strict=True), args.prefix)
    comparison.save(args.out, report)
    print(f"Verified {len(report['verified_cells'])} UART cells", flush=True)


if __name__ == "__main__":
    main()
