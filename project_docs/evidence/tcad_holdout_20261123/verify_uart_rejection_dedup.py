#!/usr/bin/env python3
"""Audit UART's fresh dedup and unchanged FAECO arms and replay each skip."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path

from run_uart_rejection_dedup import ORDER, SETUP_REASONS, comparison, read, verify
import verify_aes_cold_online as cold
from verify_aes_factorial import accepted_checkpoints
from verify_aes_greedy_matched import verify_opening
from verify_aes_protected_online import audit_logical, check


def replay_variant(cell, inputs, manifest, requests):
    arm = cell / "faeco"
    expected = read(cell / "reused_rejections.json")
    evidence = []
    rejected = {}
    native = comparison.run_method

    def dispatch(name, base, pool, dry_evaluate, cap, width, **kwargs):
        check(name == "faeco", "unexpected variant scheduler")
        index = 0

        def evaluate(ids):
            nonlocal index
            endpoint = dry_evaluate(ids)
            index += 1
            physical = arm / f"{index:02d}" / "result.json"
            record = read(physical)
            reasons = set(record["failures"])
            if reasons and reasons <= SETUP_REASONS:
                final = verify(record["physical_receipt"])
                check(set(read(final)["views"]) == set(comparison.CORNERS), "memoized trial lacks full STA")
                rejected[ids] = comparison.bind(physical)
            return endpoint

        def known(ids):
            if ids not in rejected:
                return False
            evidence.append({"actions": list(ids), "rejected_receipt": rejected[ids], "after_physical_id": index})
            return True

        return comparison.adaptive_batch_recovery(
            base, pool, evaluate, kwargs["policy"], max_evaluations=cap, batch_size=width,
            defer_split_for=kwargs["defer_split_for"], priority_after_defer=kwargs["priority_after_defer"],
            known_split_rejection=known,
        )

    comparison.run_method = dispatch
    try:
        audited = cold.replay_arm(cell, "faeco", manifest, inputs, requests)
    finally:
        comparison.run_method = native
    check(len(evidence) == len(expected), "the skip count did not replay")
    logical = read(arm / "progress.json")["logical_requests"]
    audited_skips = []
    for row, replay in zip(expected, evidence, strict=True):
        check({k: row[k] for k in ("actions", "rejected_receipt")} ==
              {k: replay[k] for k in ("actions", "rejected_receipt")}, "the skip did not replay the observed rejection")
        origin = verify(row["rejected_receipt"])
        after = replay["after_physical_id"]
        check(origin.is_relative_to(arm) and 0 < int(origin.parent.name) <= after <= len(logical),
              "skip refers to an uncompleted or cross-arm measurement")
        next_admit = logical[after]["admitted_raw"] if after < len(logical) else audited["raw_stop"]
        check(logical[after - 1]["finished_raw"] <= row["skipped_raw"] <= next_admit,
              "skip time is outside the expected physical dispatch gap")
        audited_skips.append({**row, "after_physical_id": after})
    return audited, audited_skips


def candidate_identity(arm, request):
    record = read(arm / f"{request['id']:02d}" / "result.json")
    result = read(verify(record["physical_receipt"]))
    fingerprint = {"actions": record["actions"], "failures": record["failures"],
                   "area": record["endpoint"]["area"], "timing": result.get("views")}
    artifacts = result.get("artifacts")
    if artifacts:
        spef = verify(artifacts["spef"])
        with spef.open("rb") as stream:
            normalized = sha256(b"".join(line for line in stream if not line.startswith(b"*DATE "))).hexdigest()
        fingerprint["artifacts"] = {key: artifacts[key]["sha256"] for key in ("odb", "def", "v")}
        fingerprint["artifacts"]["spef_except_date"] = normalized
    return fingerprint


def audit(root):
    protocol_path = root / "protocol.json"
    manifest = read(protocol_path)
    original = read(verify(manifest["source_protocol"]))
    for key in ("seed", "reference", "ordered_pool", "screen_input", "charged_screening_seconds_per_arm", "gate",
                "wall_window_seconds_including_screen", "logical_dispatch_cap", "batch_size", "area_target_pct",
                "clock", "affinity", "route_threads", "single_pin_access", "hold_tolerance_ps", "absolute_hold_ps"):
        check(manifest[key] == original[key], f"variant did not preserve {key}")
    check(tuple(manifest["order"]) == ORDER, "wrong paired order")
    for item in manifest["sources"].values():
        verify(item)
    check(verify(manifest["sources"]["physical_budget_adapter.py"]) ==
          Path(comparison.adaptive_batch_recovery.__code__.co_filename).resolve(), "auditor loaded a different scheduler")
    manifest.update(relative_hold_tolerance_ps=manifest["hold_tolerance_ps"], timeout_classifier=True)
    assets = read(verify(manifest["seed"]))["bindings"]
    frozen = assets["control"]
    screen = read(verify(manifest["screen_input"]["receipt"]))
    screen_pool = manifest["screen_input"]["pool"]
    check(screen["clock"] == manifest["clock"] and screen["pool_sha256"] == screen_pool["sha256"]
          and screen["wall_seconds"] == manifest["charged_screening_seconds_per_arm"]
          and read(verify(screen_pool)) == manifest["ordered_pool"]
          and all(frozen[ext]["sha256"] == digest for ext, digest in screen["control_sha256"].items()),
          "the charged screen does not bind this pool and physical reference")
    views = read(verify(manifest["reference"]))["views"]
    nets = comparison.def_section(verify(frozen["def"]), "NETS")
    pool = [comparison.PhysicalAction(**item) for item in manifest["ordered_pool"]]
    zero, reference = audit_logical(root / "preflight/zero", nets, frozen, views, manifest["gate"])
    check(reference.valid and not zero["actions"], "unqualified reference")
    rows = read(root / "results.json")
    check(tuple(row["variant"] for row in rows) == ORDER, "wrong or incomplete paired result")
    audited_rows = []
    stop = 0.0
    for index, row in enumerate(rows, 1):
        cell = root / f"cell_{index:02d}"
        arm = cell / "faeco"
        summary = read(arm / "summary.json")
        check(row["cell"] == index and row["method"] == "faeco" and row["result"] == summary,
              "summary does not bind the expected arm")
        progress = read(arm / "progress.json")
        check(stop <= progress["start_raw"] < summary["stop_raw"], "overlapping arms")
        stop = summary["stop_raw"]
        verify_opening("faeco", progress["logical_requests"], pool, manifest["batch_size"])
        requests = cold.audit_requests(arm, assets, pool, nets)
        inputs = (frozen, views, nets, pool, reference)
        if row["variant"] == "dedup":
            audited, skipped = replay_variant(cell, inputs, manifest, requests)
        else:
            audited, skipped = cold.replay_arm(cell, "faeco", manifest, inputs, requests), []
        check(len(skipped) == row["reused_rejections"], "skip count differs from the result")
        counts = cold.verify_operations(cell, "faeco", audited)
        accepted, first, best = accepted_checkpoints(arm, audited, reference, requests)
        audited_rows.append({"cell": index, "variant": row["variant"], "window": audited["window"],
                             "requests": requests, "operations": counts, "skips": skipped,
                             "accepted": accepted, "first": first, "best": best,
                             "physical_identities": [candidate_identity(arm, req) for req in requests
                                                     if req["logical_finished"]]})
    return {"protocol": comparison.bind(protocol_path), "arms": audited_rows,
            "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    ns = parser.parse_args()
    root = ns.run.resolve(strict=True)
    report = audit(root)
    comparison.save(root / "independent_verification.json", report)
    print(f"Verified {len(report['arms'])} UART rejection reuse cells", flush=True)


if __name__ == "__main__":
    main()
