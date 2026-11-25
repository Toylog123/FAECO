#!/usr/bin/env python3
"""Audit the fixed-SPEF screening pool and cost for a qualified holdout."""

from argparse import ArgumentParser
import gzip
from hashlib import file_digest
from math import fsum, isfinite
from pathlib import Path
from types import SimpleNamespace

from run_wallclock_matrix import comparison, read, verify
from screen_sky130_candidates import MIN_MATRIX_POOL, SCREEN_TARGET
from verify_screened_pilot import load_probe
from verify_setup_protocol import check_bindings, need


def audit(root):
    binding = read(root / "qualified_inputs.json")
    source = binding["source"]
    qualify = read(verify(source["qualification_receipt"]))
    check_bindings(source)
    screen = root / "screen"
    receipt_path, pool_path = screen / "screen_receipt.json", screen / "screen_pool.json"
    receipt, pool = read(receipt_path), read(pool_path)
    check_bindings(receipt)
    need(receipt["top"] == binding["top"] and receipt["period_ps"] == binding["period_basis"]["period_ps"]
         and receipt["control"] == source["control"] and receipt["clock"] == "CLOCK_MONOTONIC_RAW"
         and receipt["screen_workers"] == receipt["threads_per_probe"] == 1,
         "screen period, timing clock, physical reference or workers differ")
    recorded_inputs = {Path(item["path"]): item for item in receipt["input_bindings"]}
    libraries = []
    for item in source["source_libraries"]["TT"]:
        original = verify(item)
        materialized = screen / "libraries/TT" / original.stem if original.suffix == ".gz" else original.resolve()
        library = recorded_inputs[materialized]
        if original.suffix == ".gz":
            with gzip.open(original, "rb") as stream:
                need(file_digest(stream, "sha256").hexdigest() == library["sha256"], "materialized TT library differs")
        else:
            need(library["sha256"] == item["sha256"], "uncompressed TT library differs")
        libraries.append(library)
    need(libraries, "screen records do not identify the actual TT libraries")
    args = SimpleNamespace(libs={"TT": libraries},
                           config={"sta_timeout_seconds_per_view": receipt["baseline"]["timeout_seconds"]})
    control = receipt["control"]
    baseline, annotation = load_probe(args, screen / "control_TT", control, receipt["baseline"])
    tolerance = comparison.PS_TOLERANCE
    for k in ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps"):
        need(abs(baseline[k] - qualify["views"]["TT"][k]) <= tolerance, f"screen and qualified TT differ: {k}")
    wns = receipt["period_ps"] * 0.01
    tns = max(10 * wns, 0.01 * abs(baseline["setup_tns_ps"]))
    need(receipt["budgets_ps"] == {"wns": wns, "tns": tns}, "incorrect TT budget")
    rows = receipt["rows"]
    need(0 < len(rows) == receipt["screened"] <= 32, "wrong screening prefix")
    fanouts = {parts[1]: int(parts[2]) for line in (screen / "fanout.log").read_text().splitlines()
               if line.startswith("SCREEN_FANOUT\t") for parts in [line.split("\t")]}
    for i, row in enumerate(rows, 1):
        directory = screen / f"screen_{i:02d}"
        need(row["label"] == directory.name and row == read(directory / "receipt.json"), "screen row changed")
        action = row["action"]
        need(row["fanout"] == fanouts[action["instance"]] > 0, "incorrect raw fanout")
        metrics, marks = load_probe(args, directory, control, row["operation"], action)
        need(metrics == row["metrics"], "screen metrics differ from the raw TT report")
        base = dict.fromkeys(comparison.CORNERS, baseline)
        candidate = dict.fromkeys(comparison.CORNERS, metrics)
        failures = [reason for reason in comparison.joint_failures(base, candidate, check_setup=False)
                    if reason.startswith("TT:") and reason != "TT:hold_regression"]
        if metrics["setup_wns_ps"] < baseline["setup_wns_ps"] - wns - tolerance:
            failures.append("TT:setup_budget")
        if metrics["setup_tns_ps"] < baseline["setup_tns_ps"] - tns - tolerance:
            failures.append("TT:setup_tns_budget")
        if annotation != marks:
            failures.append("changed_annotation")
        need(row["failures"] == failures, "screen decision does not reconstruct")
    need(pool == [row["action"] for row in rows if not row["failures"]]
         and MIN_MATRIX_POOL <= len(pool) == receipt["passed"] <= SCREEN_TARGET,
         "published candidate pool differs from the accepted prefix")
    need(len(pool) != SCREEN_TARGET or not rows[-1]["failures"], "screen ran beyond its accepted-candidate limit")
    pool_binding = comparison.bind(pool_path)
    need(pool_binding["sha256"] == receipt["pool_sha256"], "screen pool hash differs")
    wall = receipt["wall_seconds"]
    tt_cost = receipt["baseline"]["wall_seconds"] + fsum(row["operation"]["wall_seconds"] for row in rows)
    need(isfinite(wall) and 0 < tt_cost <= wall < 720, "RAW charge excludes TT work or exhausts the experiment")
    return {"screen_input": comparison.bind(root / "qualified_inputs.json"), "screen_receipt": comparison.bind(receipt_path),
            "pool": pool_binding, "screened": len(rows), "passed": len(pool), "tt_cost_raw_s": tt_cost,
            "total_charged_raw_s": wall, "verifier": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = audit(args.root.resolve(strict=True))
    comparison.save(args.output, report)
    print(f"Verified {report['passed']}/{report['screened']} screened candidates, {report['total_charged_raw_s']:.6f} RAW s")


if __name__ == "__main__":
    main()
