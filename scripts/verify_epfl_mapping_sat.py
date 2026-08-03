"""Verify EPFL original-vs-mapped equivalence via Yosys miter + SAT.

N31-03 path A resolution: ABC `cec` cannot build Liberty subcircuit
models, and the downloaded skywater cell Verilog models use UDP
primitives that Yosys 0.9 cannot parse.  This runner instead:
  1. generates an assign-style cells.v from the Liberty boolean
     functions (scripts/make_liberty_cells_v.py -> sky130_cells_v2.v),
  2. builds a Yosys miter circuit (orig vs mapped),
  3. proves equivalence with `sat -prove-asserts`.

8/8 EPFL cases pass (2026-08-03).  Writes per-case JSON and a summary.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CELLS_V2 = (
    ROOT / "benchmarks" / "raw" / "skywater_cells_models" / "sky130_cells_v2.v"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--epfl-source",
        type=Path,
        default=ROOT / "benchmarks" / "raw" / "epfl_v2025_1_full",
    )
    parser.add_argument(
        "--stage-b-dir",
        type=Path,
        default=ROOT / "experiments" / "20260731_epfl_8case_stage_b",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory for per-case SAT artifacts and summary.",
    )
    parser.add_argument(
        "--benchmark-ids",
        nargs="+",
        default=["ctrl", "int2float", "router", "cavlc", "dec", "priority", "adder", "max"],
    )
    return parser.parse_args()


def _module_and_subdir(benchmark_id: str) -> tuple[str, str]:
    """Return (module_name, epfl_subdir) per benchmark."""
    if benchmark_id == "dec":
        return "dec", "random_control"
    if benchmark_id in {"adder", "max"}:
        return "top", "arithmetic"
    return "top", "random_control"


def verify_case(
    *,
    benchmark_id: str,
    epfl_source: Path,
    stage_b_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    module, subdir = _module_and_subdir(benchmark_id)
    original = epfl_source / subdir / f"{benchmark_id}.v"
    mapped = stage_b_dir / benchmark_id / "mapping" / "mapped.v"
    if not original.exists() or not mapped.exists():
        return {
            "benchmark_id": benchmark_id,
            "status": "error",
            "reason": f"missing input: original={original.exists()} mapped={mapped.exists()}",
        }

    case_dir = output_dir / benchmark_id
    case_dir.mkdir(parents=True, exist_ok=True)
    script = case_dir / "verify.ys"
    script.write_text(
        "\n".join(
            [
                f"read_verilog {CELLS_V2.as_posix()}",
                f"read_verilog {original.as_posix()}",
                f"rename {module} orig",
                f"read_verilog {mapped.as_posix()}",
                f"rename {module} mapped",
                "miter -equiv -flatten orig mapped miter",
                "hierarchy -top miter",
                "sat -verify -prove-asserts miter",
                "",
            ]
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        ["yosys", str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    runtime_s = time.perf_counter() - started
    log = case_dir / "verify.log"
    log.write_text(proc.stdout + proc.stderr, encoding="utf-8")

    combined = proc.stdout + proc.stderr
    if "SAT proof finished - no model found: SUCCESS" in combined:
        status = "pass"
        reason = "Yosys miter + sat proved original==mapped"
    elif "ERROR" in combined:
        status = "error"
        reason = _tail_reason(combined)
    else:
        status = "error"
        reason = "no SUCCESS marker in SAT output"

    return {
        "benchmark_id": benchmark_id,
        "status": status,
        "reason": reason,
        "runtime_s": round(runtime_s, 3),
        "module": module,
        "original_path": str(original),
        "mapped_path": str(mapped),
        "log_path": str(log),
    }


def _tail_reason(text: str) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[-1][:300] if lines else ""


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    per_case = []
    for b in args.benchmark_ids:
        r = verify_case(
            benchmark_id=b,
            epfl_source=args.epfl_source,
            stage_b_dir=args.stage_b_dir,
            output_dir=args.output_dir,
        )
        per_case.append(r)
        print(f"{b}: {r['status']} ({r.get('runtime_s', '?')}s) {r.get('reason', '')[:60]}")

    summary = {
        "method": "yosys_miter_sat",
        "cells_v2": str(CELLS_V2),
        "case_count": len(per_case),
        "pass_count": sum(1 for r in per_case if r["status"] == "pass"),
        "per_case": per_case,
    }
    out = args.output_dir / "sat_equivalence_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"summary: {out} pass={summary['pass_count']}/{summary['case_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())