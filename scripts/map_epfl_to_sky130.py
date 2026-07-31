"""Map pinned EPFL Verilog to SKY130 HD Liberty cells via Yosys tech mapping.

Runs ``rseco.technology_mapping.map_verilog_to_liberty`` against one EPFL
benchmark at a time and writes a structured JSON report under ``--output-dir``.
The original EPFL Verilog is never modified; mapped Verilog, BLIF and the
full Yosys log land inside ``--output-dir/<benchmark_id>/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.technology_mapping import map_verilog_to_liberty  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--epfl-source",
        type=Path,
        default=ROOT / "benchmarks" / "raw" / "epfl_v2025_1_full",
        help="Root of the pinned EPFL v2025.1 source tree.",
    )
    parser.add_argument(
        "--liberty",
        type=Path,
        default=(
            ROOT
            / "benchmarks"
            / "raw"
            / "openroad_flow_scripts_sky130hd"
            / "da8f092a02a8e75658cc3100691aabff05f35629"
            / "lib"
            / "sky130_fd_sc_hd__tt_025C_1v80.lib"
        ),
        help="Path to the pinned SKY130 HD Liberty timing model.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write per-case mapping artifacts and report.",
    )
    parser.add_argument(
        "--benchmark-ids",
        nargs="+",
        default=["ctrl", "int2float", "router"],
        help="EPFL benchmark ids to map (default: wave 1).",
    )
    parser.add_argument(
        "--yosys-command",
        default="yosys",
        help="Yosys command line. Honours FAECO_YOSYS env var when default.",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=180.0,
        help="Per-mapping Yosys timeout in seconds.",
    )
    return parser.parse_args()


def _top_module_for(benchmark_id: str) -> str:
    return {
        "ctrl": "top",
        "int2float": "top",
        "router": "top",
        "cavlc": "top",
        "dec": "top",
        "priority": "top",
        "adder": "top",
        "max": "top",
    }.get(benchmark_id, "top")


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


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _mapping_sha(mapping_dir: Path) -> dict[str, str | None]:
    sha: dict[str, str | None] = {}
    for name in ("mapped.v", "mapped.blif", "tech_mapping.log"):
        path = mapping_dir / name
        sha[name] = _sha256(path) if path.exists() else None
    return sha


def map_epfl_case(
    *,
    benchmark_id: str,
    epfl_source: Path,
    liberty: Path,
    output_dir: Path,
    yosys_command: str,
    timeout_s: float,
) -> dict[str, Any]:
    source_path = _source_for(benchmark_id, epfl_source)
    case_dir = output_dir / benchmark_id
    mapping_dir = case_dir / "mapping"
    mapping_dir.mkdir(parents=True, exist_ok=True)

    result = map_verilog_to_liberty(
        source_path,
        liberty,
        top_module=_top_module_for(benchmark_id),
        output_dir=mapping_dir,
        yosys_command=yosys_command,
        timeout_s=timeout_s,
    )

    report: dict[str, Any] = {
        "benchmark_id": benchmark_id,
        "source_path": str(source_path),
        "source_sha256": _sha256(source_path),
        "top_module": _top_module_for(benchmark_id),
        "liberty_path": str(liberty),
        "liberty_sha256": _sha256(liberty) if liberty.exists() else None,
        "mapping_dir": str(mapping_dir),
        "result": result.to_dict(),
        "mapped_artifacts_sha256": _mapping_sha(mapping_dir),
    }

    case_report_path = case_dir / "mapping_report.json"
    case_report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    report["report_path"] = str(case_report_path)
    return report


def main() -> int:
    args = parse_args()
    if not args.liberty.exists():
        print(f"Liberty not found: {args.liberty}", file=sys.stderr)
        return 1
    args.output_dir.mkdir(parents=True, exist_ok=True)

    per_case: list[dict[str, Any]] = []
    for benchmark_id in args.benchmark_ids:
        try:
            case_report = map_epfl_case(
                benchmark_id=benchmark_id,
                epfl_source=args.epfl_source,
                liberty=args.liberty,
                output_dir=args.output_dir,
                yosys_command=args.yosys_command,
                timeout_s=args.timeout_s,
            )
        except Exception as exc:
            print(f"{benchmark_id}: {exc}", file=sys.stderr)
            continue
        per_case.append(case_report)
        print(
            f"{benchmark_id}: status={case_report['result']['status']}"
            f" runtime={case_report['result']['runtime_s']:.3f}s"
            f" reason={case_report['result']['reason'][:80]}"
        )

    summary = {
        "yosys_command": args.yosys_command,
        "liberty_path": str(args.liberty),
        "liberty_sha256": _sha256(args.liberty),
        "epfl_source": str(args.epfl_source),
        "case_count": len(per_case),
        "per_case": per_case,
    }
    summary_path = args.output_dir / "mapping_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())