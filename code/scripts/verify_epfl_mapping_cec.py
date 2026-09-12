"""Run ABC CEC between the Yosys-normalized reference BLIF and the Liberty-mapped BLIF.

Stage B batch 3: formal back-verification of tech mapping results. Verifies
that the mapped netlist is functionally equivalent to the reference netlist
at the gate-level full-netlist / all-primary-outputs scope.
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

from rseco.yosys_abc import check_mapped_blif_equivalence  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--epfl-source",
        type=Path,
        default=ROOT / "benchmarks" / "raw" / "epfl_v2025_1_full",
        help="Root of the pinned EPFL v2025.1 source tree.",
    )
    parser.add_argument(
        "--mapping-dir",
        type=Path,
        required=True,
        help="Output dir produced by map_epfl_to_sky130.py.",
    )
    parser.add_argument(
        "--benchmark-ids",
        nargs="+",
        default=["ctrl", "int2float", "router"],
        help="EPFL benchmark ids to verify (default: wave 1).",
    )
    parser.add_argument(
        "--yosys-command",
        default="yosys",
        help="Yosys command line. Honours FAECO_YOSYS env var when default.",
    )
    parser.add_argument(
        "--abc-command",
        default="yosys-abc",
        help="ABC command line. Honours FAECO_ABC env var when default.",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=180.0,
        help="Per-verification ABC CEC timeout in seconds.",
    )
    return parser.parse_args()


def _source_for(benchmark_id: str, epfl_source: Path) -> Path:
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


def _outputs_for(benchmark_id: str) -> list[str]:
    """Return primary output port names per EPFL benchmark."""
    return {
        "ctrl": [
            "sel_reg_dst[0]", "sel_reg_dst[1]", "sel_alu_opB[0]", "sel_alu_opB[1]",
            "alu_op[0]", "alu_op[1]", "alu_op[2]", "alu_op_ext[0]",
            "alu_op_ext[1]", "alu_op_ext[2]", "alu_op_ext[3]", "halt",
            "reg_write", "sel_pc_opA", "sel_pc_opB", "beqz", "bnez",
            "bgez", "bltz", "jump", "Cin", "invA", "invB", "sign",
            "mem_write", "sel_wb",
        ],
        "int2float": ["z0", "z1", "z2", "z3", "z4", "z5", "z6", "z7"],
        "router": [
            "out_data[0]", "out_data[1]", "out_data[2]", "out_data[3]",
            "out_data[4]", "out_data[5]", "out_data[6]", "out_data[7]",
            "out_data[8]", "out_data[9]", "out_data[10]", "out_data[11]",
            "out_data[12]", "out_data[13]", "out_data[14]", "out_data[15]",
            "out_valid", "out_request", "out_op[0]", "out_op[1]",
            "out_op[2]", "out_op[3]", "out_ch[0]", "out_ch[1]",
            "out_ch[2]", "out_ch[3]", "out_ch[4]", "out_ch[5]",
        ],
        "cavlc": ["code[0]", "code[1]", "code[2]", "code[3]", "code[4]", "code[5]",
                  "code[6]", "code[7]", "code[8]", "code[9]", "code[10]", "code[11]"],
        "dec": ["Z[0]", "Z[1]", "Z[2]", "Z[3]"],
        "priority": ["out[0]", "out[1]", "out[2]", "out[3]", "out[4]", "out[5]", "out[6]", "out[7]"],
        "adder": ["out[0]", "out[1]", "out[2]", "out[3]", "out[4]", "out[5]", "out[6]", "out[7]", "out[8]"],
        "max": ["out[0]", "out[1]", "out[2]", "out[3]", "out[4]", "out[5]", "out[6]", "out[7]", "out[8]"],
    }.get(benchmark_id, [])


def verify_case(
    *,
    benchmark_id: str,
    epfl_source: Path,
    mapping_dir: Path,
    yosys_command: str,
    abc_command: str,
    timeout_s: float,
) -> dict[str, Any]:
    case_dir = mapping_dir / benchmark_id
    mapping_case_dir = case_dir / "mapping"
    mapped_blif = mapping_case_dir / "mapped.blif"
    if not mapped_blif.exists():
        raise FileNotFoundError(
            f"mapped BLIF missing for {benchmark_id!r}: {mapped_blif}"
        )
    cec_artifact_dir = case_dir / "cec"
    cec_artifact_dir.mkdir(parents=True, exist_ok=True)

    original_verilog = _source_for(benchmark_id, epfl_source)
    outputs = _outputs_for(benchmark_id)

    result = check_mapped_blif_equivalence(
        original_verilog,
        mapped_blif,
        artifact_dir=cec_artifact_dir,
        yosys_command=yosys_command,
        abc_command=abc_command,
        timeout_s=timeout_s,
    )
    return {
        "benchmark_id": benchmark_id,
        "original_verilog": str(original_verilog),
        "mapped_blif": str(mapped_blif),
        "outputs": outputs,
        "scope": "gate_level_full_netlist_all_primary_outputs",
        "result": result.to_dict(),
    }


def main() -> int:
    args = parse_args()
    args.mapping_dir.mkdir(parents=True, exist_ok=True)

    per_case: list[dict[str, Any]] = []
    for benchmark_id in args.benchmark_ids:
        try:
            case_report = verify_case(
                benchmark_id=benchmark_id,
                epfl_source=args.epfl_source,
                mapping_dir=args.mapping_dir,
                yosys_command=args.yosys_command,
                abc_command=args.abc_command,
                timeout_s=args.timeout_s,
            )
        except Exception as exc:
            print(f"{benchmark_id}: {exc}", file=sys.stderr)
            continue
        per_case.append(case_report)
        status = case_report["result"]["status"]
        runtime = case_report["result"]["runtime_s"]
        print(f"{benchmark_id}: status={status} runtime={runtime:.3f}s")

    summary = {
        "mapping_dir": str(args.mapping_dir),
        "yosys_command": args.yosys_command,
        "abc_command": args.abc_command,
        "case_count": len(per_case),
        "per_case": per_case,
    }
    summary_path = args.mapping_dir / "cec_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())