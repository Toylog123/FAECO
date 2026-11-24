#!/usr/bin/env python3
"""Check equivalent complete search arms before comparing their observed runtime."""

import argparse
import json
from pathlib import Path
import re

import compare_ibex as comparison
from probe_duplicate_pin_access import spef_without_date
from run_holdout_screened import expected_holdout_sdc
import verify_setup_protocol as protocol
from verify_screened_matrix import MatrixAudit


ARMS = {"a1": False, "b1": True, "b2": True, "a2": False}
PIN_ACCESS_START = re.compile(r"^\[INFO DRT-0165\] Start pin access\.$", re.M)


def fingerprint(root, arm, optimized):
    directory = root / "screened/faeco"
    rows = []
    for number, decision in enumerate(arm["trace"], start=1):
        trial = directory / f"{number:02d}_physical"
        attempt = protocol.read(directory / f"{number:02d}.json")
        receipt = protocol.read(trial / "receipt.json")
        deck = (trial / "route.tcl").read_text().replace(str(root), "<arm>")
        if not optimized:
            protocol.equal(deck.count("\npin_access\n"), 1, f"baseline Tcl {trial}")
            deck = deck.replace("\npin_access\n", "\n", 1)
        pin_access = len(PIN_ACCESS_START.findall((trial / "route.log").read_text()))
        protocol.equal(pin_access, 1 if optimized else 2, f"actual PA count {trial}")
        proof_dir = trial / "sec/receipt.json"
        proof = protocol.read(proof_dir) if proof_dir.exists() else {}
        rows.append({
            "deck": deck,
            "actions": attempt["actions"],
            "failures": attempt["failures"],
            "accepted": decision["accepted"],
            "split_deferred": decision.get("split_deferred", False),
            "area": receipt["endpoint"]["area"],
            "views": receipt["views"],
            "digests": {tag: receipt["artifacts"][tag]["sha256"] for tag in ("def", "v", "drc")},
            "spef": spef_without_date(receipt["artifacts"]["spef"]["path"]),
            "layout_changes": protocol.read(trial / "layout_changes.json"),
            "sec_points": [proof.get(field) for field in ("proven", "unproven")],
        })
    return rows


def audit(root):
    protocol.expected_sdc = expected_holdout_sdc
    original = None
    entries = {}
    for name, optimized in ARMS.items():
        directory = root / name
        config = protocol.read(directory / "config.json")
        comparison.TOP = config["top"]
        protocol.equal(config["top"], "gcd", f"same design {name}")
        protocol.equal(config["single_pin_access"], optimized, f"assigned treatment {name}")
        protocol.equal(config["cpu_affinity"], list(range(6, 12)), f"CPU set {name}")
        protocol.equal(config["methods_route_threads"], 4, f"threads {name}")
        report = MatrixAudit(directory).run_matrix()
        summary = protocol.read(directory / "results.json")["arms"]["screened"]["faeco"]
        outcome = report["arms"]["screened"]["faeco"]
        assets = config["bindings"]
        rows = fingerprint(directory, summary, optimized)
        input_fingerprint = (
            {key: assets[key] for key in ("control", "tools", "flow", "source_libraries", "original_sdc")},
            config["screen_inputs"], tuple(config["split_deferral_reasons"]), config["primary_wall_limit_seconds"],
            config["primary_target_area_pct"], config["budget_attempts_per_arm"], config["batch_size"],
            report["control"], report["noop_sec_proven"],
        )
        if original is None:
            original = (rows, input_fingerprint)
        protocol.equal((rows, input_fingerprint), original, f"same six complete endpoints {name}")
        entries[name] = {
            "single_pin_access": optimized,
            "config_sha256": report["config_sha256"], "results_sha256": report["results_sha256"],
            "total_operations": report["total_operations"],
            "end_to_end_first_target_raw_seconds": outcome["time_to_target_seconds"],
            "search_first_target_raw_seconds": outcome["search_time_to_target_seconds"],
            "search_six_raw_seconds": outcome["search_wall_seconds"],
            "screen_charge_raw_seconds": outcome["charged_screening_seconds"],
            "area_saved_six": outcome["within_cap"]["area_saved"],
            "area_saved_within_720": outcome["within_wall_window"]["area_saved"],
            "stage_raw_seconds": outcome["stage_seconds"],
        }
    return {
        "arms": entries,
        "same_actions_physical_geometry_timing_and_proofs": True,
        "ablated_Tcl_line_only": True,
        "pair_saved_first_target_raw_seconds": [
            entries[a]["end_to_end_first_target_raw_seconds"] - entries[b]["end_to_end_first_target_raw_seconds"]
            for a, b in (("a1", "b1"), ("a2", "b2"))
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    print(json.dumps(audit(parser.parse_args().root.resolve(strict=True)), indent=2, allow_nan=False))
