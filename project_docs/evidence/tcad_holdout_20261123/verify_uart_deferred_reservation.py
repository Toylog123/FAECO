#!/usr/bin/env python3
"""Audit the UART reservation matrix and reconstruct actual physical dispatches."""

from argparse import ArgumentParser
from pathlib import Path

from run_uart_deferred_reservation import ORDER, RULE, comparison, enable_reservation, read, verify
from verify_uart_rejection_dedup import candidate_identity, replay_variant
import verify_aes_cold_online as cold
from verify_aes_factorial import accepted_checkpoints
from verify_aes_greedy_matched import verify_opening
from verify_aes_protected_online import audit_logical, check


def replay_reserved(cell, inputs, protocol, requests):
    original = comparison.adaptive_batch_recovery
    reserved = enable_reservation(original)
    replayed = []

    def search(*args, **kwargs):
        result = reserved(*args, **kwargs)
        for index, row in enumerate(result["trace"], 1):
            if "reserved_deferred_singleton" in row:
                replayed.append({"physical_request": index, "action": row["reserved_deferred_singleton"],
                                 "actions": row["actions"]})
        return result

    comparison.adaptive_batch_recovery = search
    try:
        audited, skipped = replay_variant(cell, inputs, protocol, requests)
    finally:
        comparison.adaptive_batch_recovery = original
    check(replayed == read(cell / "reservation.json"), "reservation did not replay from prior measurements")
    check(all(item["physical_request"] == protocol["logical_dispatch_cap"] for item in replayed),
          "reservation consumed a slot before the last physical evaluation")
    return audited, skipped, replayed


def audit(root):
    protocol_path = root / "protocol.json"
    protocol = read(protocol_path)
    source = verify(protocol["source_protocol"])
    previous = read(source)
    earlier = read(verify(protocol["source_verification"]))
    check(verify(earlier["protocol"]) == source and len(earlier["arms"]) == 4, "wrong source experiment")
    shared = ("seed", "reference", "ordered_pool", "screen_input", "charged_screening_seconds_per_arm", "gate",
              "wall_window_seconds_including_screen", "logical_dispatch_cap", "batch_size", "area_target_pct",
              "clock", "affinity", "route_threads", "single_pin_access", "hold_tolerance_ps", "absolute_hold_ps")
    for key in shared:
        check(protocol[key] == previous[key], f"changed comparison condition: {key}")
    check(tuple(protocol["order"]) == ORDER and protocol["reservation_rule"] == RULE
          and protocol["fixed_area_reference_um2"] == 0.23328, "invalid preregistered comparison")
    for source_ref in protocol["sources"].values():
        verify(source_ref)
    check(verify(protocol["sources"]["physical_budget_adapter.py"]) ==
          Path(comparison.adaptive_batch_recovery.__code__.co_filename).resolve(), "auditor did not load the measured scheduler")
    protocol.update(relative_hold_tolerance_ps=protocol["hold_tolerance_ps"], timeout_classifier=True)
    assets = read(verify(protocol["seed"]))["bindings"]
    frozen = assets["control"]
    screen_ref = protocol["screen_input"]
    screen = read(verify(screen_ref["receipt"]))
    check(screen["clock"] == protocol["clock"] and screen["pool_sha256"] == screen_ref["pool"]["sha256"]
          and screen["wall_seconds"] == protocol["charged_screening_seconds_per_arm"]
          and read(verify(screen_ref["pool"])) == protocol["ordered_pool"]
          and all(frozen[ext]["sha256"] == digest for ext, digest in screen["control_sha256"].items()),
          "screening did not bind the frozen physical input and ordered pool")
    views = read(verify(protocol["reference"]))["views"]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    pool = [comparison.PhysicalAction(**row) for row in protocol["ordered_pool"]]
    zero, reference = audit_logical(root / "preflight/zero", nets, frozen, views, protocol["gate"])
    check(reference.valid and not zero["actions"], "shared zero failed")
    inputs = (frozen, views, nets, pool, reference)
    rows = read(root / "results.json")
    check(tuple(row["variant"] for row in rows) == ORDER, "incomplete or reordered matrix")
    outcome = []
    preceding_stop = 0.0
    for index, row in enumerate(rows, 1):
        variant = row["variant"]
        method = "fixed_online" if variant == "fixed_online" else "faeco"
        cell = root / f"cell_{index:02d}"
        arm = cell / method
        summary = read(arm / "summary.json")
        progress = read(arm / "progress.json")
        check(index == row["cell"] and row["method"] == method and row["result"] == summary, "arm summary mismatch")
        check(preceding_stop <= progress["start_raw"] < summary["stop_raw"], "arm timings overlap")
        preceding_stop = summary["stop_raw"]
        verify_opening(method, progress["logical_requests"], pool, protocol["batch_size"])
        requests = cold.audit_requests(arm, assets, pool, nets)
        reservation, skipped = [], []
        if variant == "reserved":
            assessed, skipped, reservation = replay_reserved(cell, inputs, protocol, requests)
        elif variant == "dedup":
            assessed, skipped = replay_variant(cell, inputs, protocol, requests)
        else:
            assessed = cold.replay_arm(cell, method, protocol, inputs, requests)
        check(len(skipped) == row["reused_rejections"], "physical rejection reuse did not replay")
        operations = cold.verify_operations(cell, method, assessed)
        accepted, first, best = accepted_checkpoints(arm, assessed, reference, requests)
        outcome.append({"cell": index, "variant": variant, "window": assessed["window"], "operations": operations,
                        "first_target": first, "best": best, "accepted": accepted, "reservation": reservation,
                        "skips": skipped, "requests": requests,
                        "physical_identities": [candidate_identity(arm, req) for req in requests
                                                if req["logical_finished"]]})
    return {"protocol": comparison.bind(protocol_path), "arms": outcome,
            "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    report = audit(root)
    comparison.save(root / "independent_verification.json", report)
    print(f"Verified {len(report['arms'])} UART last-slot comparison cells", flush=True)


if __name__ == "__main__":
    main()
