#!/usr/bin/env python
"""Multi-circuit equivalence sweep (E1-E6) — aggregate a ``compare`` over N circuits.

``compare_0a_equivalence.py`` decides one reference/candidate product pair.  A
phase gate such as the legacy regression asks the same question across a whole
benchmark set (e.g. all eight ISCAS89 circuits) and needs one verdict:

    N/N circuits  whose six equivalence items all match

This script walks ``<root>/<left>/<circuit>/outerloop_result.json`` and
``<root>/<right>/<circuit>/outerloop_result.json`` for the requested circuits,
reuses :func:`compare` so the item definitions stay in exactly one place, and
prints both a per-circuit table and the aggregate verdict.  Decision-core and
bookkeeping verdicts are reported separately, matching the single-pair report.

Usage::

    python compare_equivalence_sweep.py \
        --root experiments/20260923_legacy_reg/E1 \
        --left codex --right main \
        --circuits s27,s382,s420,s641,s713,s820,s832,s953 \
        --json-out experiments/20260923_legacy_reg/E1/gate_legacy_8circ.json

Exit code is 0 only when every requested circuit passes the *decision core*;
pass ``--require-full`` to also demand bookkeeping (E1.candidate_order,
E1.current_cone_gates, E6) agreement.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_0a_equivalence import compare  # noqa: E402

PRODUCT = "outerloop_result.json"


def _load(root: Path, side: str, circuit: str) -> Path | None:
    path = root / side / circuit / PRODUCT
    return path if path.exists() else None


def run_sweep(root: Path, left: str, right: str, circuits: list[str]) -> dict:
    per_circuit: list[dict] = []
    for circuit in circuits:
        ref = _load(root, left, circuit)
        cand = _load(root, right, circuit)
        if ref is None or cand is None:
            missing = [
                f"{s}/{circuit}" for s, p in ((left, ref), (right, cand))
                if p is None
            ]
            per_circuit.append({
                "circuit": circuit,
                "status": "MISSING",
                "missing": missing,
            })
            continue
        result = compare(ref, cand)
        per_circuit.append({
            "circuit": circuit,
            "status": "OK" if result["full_match"] else (
                "DECISION_DIFF" if not result["decision_match"]
                else "BOOKKEEPING_DIFF"
            ),
            "n_items": result["n_items"],
            "n_match": result["n_match"],
            "decision_match": result["decision_match"],
            "full_match": result["full_match"],
            "core_mismatches": result["core_mismatches"],
            "bookkeeping_mismatches": result["bookkeeping_mismatches"],
            "reference": result["reference"],
            "candidate": result["candidate"],
        })

    runnable = [c for c in per_circuit if c["status"] != "MISSING"]
    return {
        "root": str(root),
        "left": left,
        "right": right,
        "circuits": circuits,
        "per_circuit": per_circuit,
        "n_circuits": len(circuits),
        "n_runnable": len(runnable),
        "n_decision_pass": sum(1 for c in runnable if c["decision_match"]),
        "n_full_pass": sum(1 for c in runnable if c["full_match"]),
        "all_decision_pass": (
            len(runnable) == len(circuits)
            and all(c["decision_match"] for c in runnable)
        ),
        "all_full_pass": (
            len(runnable) == len(circuits)
            and all(c["full_match"] for c in runnable)
        ),
    }


def print_sweep(report: dict, require_full: bool) -> None:
    print(f"root  : {report['root']}")
    print(f"sides : {report['left']} (reference)  vs  {report['right']} (candidate)")
    print()
    width = max((len(c["circuit"]) for c in report["per_circuit"]), default=8)
    print(f"{'circuit':<{width}}  {'items':>7}  {'decision':>9}  {'full':>9}  status")
    print("-" * (width + 42))
    for c in report["per_circuit"]:
        if c["status"] == "MISSING":
            print(f"{c['circuit']:<{width}}  {'-':>7}  {'-':>9}  {'-':>9}  "
                  f"MISSING {c['missing']}")
            continue
        items = f"{c['n_match']}/{c['n_items']}"
        dec = "PASS" if c["decision_match"] else "FAIL"
        full = "PASS" if c["full_match"] else "FAIL"
        detail = ""
        if c["core_mismatches"]:
            detail = "  core: " + ", ".join(c["core_mismatches"])
        elif c["bookkeeping_mismatches"]:
            detail = "  book: " + ", ".join(c["bookkeeping_mismatches"])
        print(f"{c['circuit']:<{width}}  {items:>7}  {dec:>9}  {full:>9}  "
              f"{c['status']}{detail}")
    print("-" * (width + 42))
    print(f"decision core : {report['n_decision_pass']}/{report['n_circuits']} circuits")
    print(f"full gate     : {report['n_full_pass']}/{report['n_circuits']} circuits")
    verdict = report["all_full_pass"] if require_full else report["all_decision_pass"]
    print(f"SWEEP GATE    : {'PASS' if verdict else 'FAIL'}"
          f"  ({'full E1-E6' if require_full else 'decision core E1-E5'})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, required=True,
                        help="Directory holding <left>/ and <right>/ subdirs")
    parser.add_argument("--left", default="codex", help="Reference side subdir")
    parser.add_argument("--right", default="main", help="Candidate side subdir")
    parser.add_argument("--circuits", required=True,
                        help="Comma-separated circuit ids")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--require-full", action="store_true",
                        help="Also require bookkeeping/E6 agreement")
    args = parser.parse_args(argv)

    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    report = run_sweep(args.root, args.left, args.right, circuits)
    print_sweep(report, args.require_full)

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nmachine-readable report -> {args.json_out}")

    if args.require_full:
        return 0 if report["all_full_pass"] else 1
    return 0 if report["all_decision_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
