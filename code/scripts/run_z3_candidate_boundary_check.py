"""Run Z3 candidate/boundary formal equivalence check on EPFL case pairs.

N31-06 Z3 wrapper runner.  For each EPFL case, builds a SMT2 problem
that asks whether the original Verilog differs from the mapped Verilog
on any boundary input.  Writes a structured JSON report and a markdown
summary table.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.z3_formal import check_z3_candidate_boundary_equivalence  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--epfl-source",
        type=Path,
        default=ROOT / "benchmarks" / "raw" / "epfl_v2025_1_full",
        help="Root of the pinned EPFL v2025.1 source tree.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write per-case Z3 artifacts and report.",
    )
    parser.add_argument(
        "--benchmark-ids",
        nargs="+",
        default=["ctrl", "int2float", "router", "cavlc", "dec", "priority", "adder", "max"],
        help="EPFL benchmark ids to check (default: wave 1+2).",
    )
    parser.add_argument(
        "--stage-b-mapping-dir",
        type=Path,
        default=ROOT / "experiments" / "20260731_epfl_8case_stage_b",
        help="Stage B output dir with <case>/mapping/mapped.v files.",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=10.0,
        help="Per-case Z3 timeout in seconds.",
    )
    return parser.parse_args()


def _top_module_for(benchmark_id: str) -> str:
    return {
        "ctrl": "top",
        "int2float": "top",
        "router": "top",
        "cavlc": "top",
        "dec": "dec",
        "priority": "top",
        "adder": "top",
        "max": "top",
    }.get(benchmark_id, "top")


def _boundary_ports_for(benchmark_id: str) -> list[str]:
    """Return a reasonable boundary-port set per EPFL case.

    We use a small canonical set: the top module inputs that drive
    most combinational logic.  For the test runner we use the same
    names that appear in the module port list (e.g. ``opcode``).
    """
    common = {
        "ctrl": ["opcode[0]", "halt", "reg_write", "mem_write"],
        "int2float": ["z0", "z1", "z2", "z3"],
        "router": ["out_data[0]", "out_data[1]", "out_valid"],
        "cavlc": ["code[0]", "code[1]"],
        "dec": ["Z[0]", "Z[1]"],
        "priority": ["out[0]", "out[1]"],
        "adder": ["out[0]", "out[1]"],
        "max": ["out[0]", "out[1]"],
    }
    return common.get(benchmark_id, ["a", "b"])


def _source_for(benchmark_id: str, epfl_source: Path) -> Path:
    # EPFL v2025.1 distributes all combinational benchmarks under
    # random_control/ regardless of family label; the original file
    # lookup is exhaustive across all known subdirs.
    candidates = [
        epfl_source / "random_control" / f"{benchmark_id}.v",
        epfl_source / "arithmetic" / f"{benchmark_id}.v",
        epfl_source / "memory" / f"{benchmark_id}.v",
        epfl_source / f"{benchmark_id}.v",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"no EPFL source for benchmark {benchmark_id!r} under {epfl_source}"
    )


def _mapped_for(benchmark_id: str, stage_b_dir: Path) -> Path:
    mapped = stage_b_dir / benchmark_id / "mapping" / "mapped.v"
    if not mapped.exists():
        raise FileNotFoundError(f"Stage B mapped Verilog missing: {mapped}")
    return mapped


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    per_case: list[dict[str, Any]] = []
    for benchmark_id in args.benchmark_ids:
        try:
            original_path = _source_for(benchmark_id, args.epfl_source)
            mapped_path = _mapped_for(benchmark_id, args.stage_b_mapping_dir)
            boundary_ports = _boundary_ports_for(benchmark_id)
            case_dir = args.output_dir / benchmark_id
            result = check_z3_candidate_boundary_equivalence(
                original_path,
                mapped_path,
                boundary_ports=boundary_ports,
                output_dir=case_dir,
                timeout_s=args.timeout_s,
            )
        except Exception as exc:
            print(f"{benchmark_id}: {exc}", file=sys.stderr)
            continue
        per_case.append(
            {
                "benchmark_id": benchmark_id,
                "original_path": str(original_path),
                "mapped_path": str(mapped_path),
                "boundary_ports": boundary_ports,
                "result": result.to_dict(),
            }
        )
        print(
            f"{benchmark_id}: status={result.status}"
            f" runtime={result.runtime_s:.3f}s"
            f" boundary={len(result.boundary_ports)}"
        )

    summary = {
        "source_summary": str(args.stage_b_mapping_dir),
        "epfl_source": str(args.epfl_source),
        "case_count": len(per_case),
        "per_case": per_case,
    }
    summary_path = args.output_dir / "z3_candidate_boundary_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())