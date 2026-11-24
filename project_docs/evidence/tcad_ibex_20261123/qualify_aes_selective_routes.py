#!/usr/bin/env python3
"""Qualify completed selective AES routes against the unchanged matrix reference."""

from argparse import ArgumentParser
from pathlib import Path
from types import SimpleNamespace
import re

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from audit_aes_unlocked_drc import audit
from probe_aes_selective_repair import audit_routing, audit_timing, read, verify
from run_screened_matrix import bind_runtime


def qualify(matrix_path, raw, out, labels):
    matrix = read(matrix_path)
    cfg = matrix["bindings"]
    inputs = read(raw / "inputs.json")
    if inputs["matrix_config"] != comparison.bind(matrix_path):
        raise ValueError("physical producer used a different matrix reference")
    control = {key: verify(item) for key, item in cfg["control"].items()}
    flow = {key: verify(item) for key, item in cfg["flow"].items()}
    libs = {corner: [verify(item) for item in items] for corner, items in cfg["used_libraries"].items()}
    control_receipt = verify(inputs["reference_view_receipt"])
    baseline = comparison.def_section(control["def"], "NETS")
    raw_results = read(raw / "results.json")
    out.mkdir(parents=True)
    comparison.save(out / "inputs.json", {
        "matrix": comparison.bind(matrix_path), "physical_inputs": comparison.bind(raw / "inputs.json"),
        "qualification_source": comparison.bind(Path(__file__).resolve()),
        "geometry_source": comparison.bind(Path(audit_routing.__code__.co_filename).resolve()),
        "unlocked_drc_source": comparison.bind(Path(audit.__code__.co_filename).resolve()),
        "cases": labels,
    })
    settings = SimpleNamespace(
        clock_period_ps=matrix["original_clock_period_ps"], sec=verify(cfg["tools"]["sec"]),
        sec_timeout=matrix["sec_timeout_seconds"], pdk=matrix["pdk"],
    )
    results = {}
    with bind_runtime(matrix["top"], flow["fastroute.tcl"]):
        evaluator = comparison.Evaluator(
            settings, control, libs, comparison.logical_masters(control["v"], comparison.liberty_areas(libs["TT"])),
            read(control_receipt)["views"], (), matrix["scope"],
        )
        gate = sweep.budget_gate(evaluator, matrix["primary_budget_pct"], False)
        for label in labels:
            case = out / label
            case.mkdir()
            receipt_path = verify(raw_results[label]["receipt"])
            receipt = read(receipt_path)
            if not (receipt["routed_to_completion"] and receipt["extracted_to_completion"]):
                raise ValueError(f"{label} missing completed DRT and RCX")
            if receipt["control_sdc"] != cfg["control"]["sdc"]:
                raise ValueError(f"{label} was measured under different constraints")
            for artifact in receipt["artifacts"].values():
                verify(artifact)
            failures = list(receipt["failures"])
            failures.extend(audit_timing(evaluator, receipt, gate, label == "zero"))
            area_pct = 100 * receipt["area_saved"] / evaluator.ref_area
            if label != "zero" and area_pct < matrix["primary_target_area_pct"]:
                failures.append("area_target")
            physical_dir = receipt_path.parent
            route_audit = case / "routing_audit.json"
            failures.extend(audit_routing(physical_dir, baseline, route_audit))
            drc = audit(matrix_path, case / "unlocked_drc", receipt_path)
            if drc["drc_markers"]:
                failures.append("unlocked_drc")
            operations = {}
            proof = None
            if not failures:
                if label == "zero":
                    if not receipt["endpoint"]["sec_pass"]:
                        failures.append("sec")
                    sec_log = physical_dir / "sec.log"
                else:
                    candidate = verify(receipt["artifacts"]["v"])
                    if not evaluator.proof(candidate, case, operations):
                        failures.append("sec")
                    sec_log = case / "sec.log"
                match = re.search(r"(?m)^SEC proven=([1-9]\d*) unproven=0 rc=0\s*$",
                                  sec_log.read_text(encoding="utf-8"))
                if not match:
                    failures.append("nonempty_sec_evidence")
                elif not failures:
                    proof = {"proven": int(match[1]), "unproven": 0, "log": comparison.bind(sec_log)}
            results[label] = {
                "physical_receipt": comparison.bind(receipt_path),
                "physical_route_preflight": comparison.bind(route_audit), "unlocked_drc": drc,
                "area_saved_pct": area_pct, "failures": failures, "sec": proof, "sec_operations": operations,
            }
            comparison.save(out / "results.json", results)
            print(f"AES qualification {label}: {failures or 'passed'}", flush=True)
    return results


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("matrix", type=Path)
    p.add_argument("physical_run", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--cases", nargs="+", choices=("zero", "02", "05"), default=["zero", "02", "05"])
    ns = p.parse_args()
    qualify(ns.matrix.resolve(strict=True), ns.physical_run.resolve(strict=True), ns.out.resolve(), ns.cases)


if __name__ == "__main__":
    main()
