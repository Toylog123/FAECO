#!/usr/bin/env python3
"""Validate the alternate one-pass DRT recipe on the same qualified GCD tuple."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from probe_duplicate_pin_access import spef_without_date
from run_screened_matrix import CLOCK_NAME, bind_runtime, raw_seconds, read
from verify_setup_protocol import check_bindings, need


def run(reference_root, out):
    config_path = reference_root / "config.json"
    results_path = reference_root / "results.json"
    config, previous = read(config_path), read(results_path)
    need(config["top"] == "gcd" and previous["status"] == "matched", "expected completed GCD A/B")
    assets = config["bindings"]
    check_bindings(assets)
    check_bindings(config["reference_bindings"])
    qualified = previous["trials"][0]
    need(qualified["accepted"] and all(qualified["matches_historical"].values()), "reference GCD tuple unqualified")
    original = read(Path(qualified["physical_receipt"]["path"]))
    old_directory = Path(qualified["physical_receipt"]["path"]).parent
    old_artifacts = original["artifacts"]
    old_proof = read(old_directory / "sec" / "receipt.json")
    controls = {name: Path(item["path"]) for name, item in assets["control"].items()}
    libs = {corner: [Path(item["path"]) for item in items] for corner, items in assets["used_libraries"].items()}
    pool = [comparison.PhysicalAction(**row) for row in read(Path(config["reference_bindings"][-1]["path"]))]
    actions = tuple(original["actions"])
    need(actions == tuple(sorted(row.action_id for row in pool[12:15])), "unexpected GCD rank tuple")
    policy_inputs = {
        "clock": CLOCK_NAME, "cpu_affinity": sorted(os.sched_getaffinity(0)),
        "prior": [comparison.bind(path) for path in (config_path, results_path)],
        "driver": comparison.bind(Path(__file__).resolve()), "actions": actions,
        "setup_hold_gate": previous["gate"], "order": ("reference", "explicit_only", "explicit_only", "reference"),
    }
    scope = hashlib.sha256(json.dumps(policy_inputs, sort_keys=True).encode()).hexdigest()
    routing = Path(assets["flow"]["fastroute.tcl"]["path"])
    settings = SimpleNamespace(
        out=out, pdk=config["pdk"], orfs=routing.parents[2], clock_period_ps=config["original_clock_period_ps"],
        openroad=Path(assets["tools"]["openroad"]["path"]), sta=Path(assets["tools"]["opensta"]["path"]),
        sec=Path(assets["tools"]["sec"]["path"]), threads=config["methods_route_threads"],
        embedded_guides=True, zero_reextract=True, route_mode=config["route_mode"], route_guide=None,
        droute_iters=config["route_drt_iters"], route_timeout=config["route_timeout_seconds"],
        sta_timeout=config["sta_timeout_seconds_per_view"], sec_timeout=config["sec_timeout_seconds"],
        report_setup_endpoints=config["report_setup_endpoints"], control_drc=Path(assets["control_drc"]["path"]),
    )
    area_table = comparison.liberty_areas(libs["TT"])
    with bind_runtime("gcd", routing):
        masters = comparison.logical_masters(controls["v"], area_table)
    evaluator = comparison.Evaluator(settings, controls, libs, masters, previous["control"]["views"], pool, scope)
    gate = sweep.budget_gate(evaluator, config["primary_budget_pct"], False)
    need(sweep.gate_summary(gate, evaluator.ref_views) == previous["gate"], "gate drift")
    out.mkdir()
    comparison.save(out / "config.json", policy_inputs)
    cache = sweep.TrialCache(evaluator)
    renderer = comparison.render_route
    rows = []
    expected_spef = spef_without_date(old_artifacts["spef"]["path"])
    expected_layout = read(old_directory / "layout_changes.json")
    with bind_runtime("gcd", routing):
        for seq, mode in enumerate(policy_inputs["order"], 1):
            destination = out / f"{seq:02d}_{mode}"
            print(f"START {destination}", flush=True)

            def render(*values):
                script = renderer(*values)
                need("\npin_access\n" in script, "expected explicit pin_access")
                marker = " -verbose 1 -droute_end_iter "
                need(script.count(marker) == 1, "expected single detailed_route")
                return script.replace(marker, " -no_pin_access" + marker, 1) if mode == "explicit_only" else script

            start = raw_seconds()
            with patch.object(comparison, "render_route", render):
                endpoint, logical = cache.request(actions, gate, fresh_directory=destination)
            elapsed = raw_seconds() - start
            comparison.save(destination / "logical.json", logical)
            physical = read(destination / "receipt.json")
            proof_path = destination / "sec" / "receipt.json"
            proof = read(proof_path) if proof_path.exists() else {}
            artifacts = physical.get("artifacts", {})
            match = {kind: artifacts.get(kind, {}).get("sha256") == old_artifacts[kind]["sha256"]
                     for kind in ("odb", "def", "v", "drc")}
            match["spef_without_date"] = bool(artifacts) and spef_without_date(artifacts["spef"]["path"]) == expected_spef
            match["sta_views"] = physical["views"] == original["views"]
            match["layout_changes"] = bool(artifacts) and read(destination / "layout_changes.json") == expected_layout
            match["sec"] = (proof.get("proven") == old_proof["proven"] > 0 and proof.get("unproven") == 0
                            and proof.get("gold") == old_proof["gold"] and proof.get("gate") == artifacts["v"])
            count = (destination / "route.log").read_text().count("Start pin access.")
            rows.append({"mode": mode, "matches_reference": match, "pin_access_passes": count,
                         "accepted": endpoint.valid and endpoint.sec_pass,
                         "elapsed_raw_seconds": elapsed, "area_saved": evaluator.ref_area - endpoint.area})
            comparison.save(out / "progress.json", rows)
            print(f"FINISH {destination} {elapsed:.3f}s {match}", flush=True)
    comparison.save(out / "results.json", {"trials": rows, "operations": cache.totals()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    run(args.reference.resolve(strict=True), args.out.resolve())


if __name__ == "__main__":
    main()
