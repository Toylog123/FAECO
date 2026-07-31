"""Run the Stage B pre-layout STA pipeline (mapping -> SDC -> OpenSTA).

For each requested EPFL benchmark:
  1. Map Verilog -> SKY130 Liberty cells (Yosys).
  2. Build a pre-layout SDC from the Liberty units + config.
  3. Run OpenSTA pre-layout STA via the configured ``sta`` command.
  4. Write a per-case structured JSON report and a batch summary.
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

from rseco.opensta import run_opensta_pre_layout  # noqa: E402
from rseco.sdc import (  # noqa: E402
    SdcConfig,
    build_pre_layout_sdc,
    parse_liberty_units,
    save_sdc,
)
from rseco.technology_mapping import map_verilog_to_liberty  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "experiments" / "configs" / "stage_b_pre_layout.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write per-case mapping / STA artifacts and reports.",
    )
    parser.add_argument(
        "--benchmark-ids",
        nargs="+",
        default=None,
        help="Override benchmark ids from config.",
    )
    parser.add_argument(
        "--sta-command",
        default="sta",
        help="OpenSTA command. Production runs use WSL2 path.",
    )
    parser.add_argument(
        "--mapping-timeout-s",
        type=float,
        default=180.0,
    )
    parser.add_argument(
        "--sta-timeout-s",
        type=float,
        default=180.0,
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


def _run_case(
    *,
    benchmark_id: str,
    config: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    epfl_source = ROOT / config["epfl_source"]
    liberty_path = ROOT / config["liberty"]["path"]
    sdc_cfg_dict = config["sdc"]
    sdc_cfg = SdcConfig(
        virtual_clock_name=sdc_cfg_dict.get("virtual_clock_name", "clk_virtual"),
        clock_period_ns=sdc_cfg_dict.get("clock_period_ns", 10.0),
        input_delay_ns=sdc_cfg_dict.get("input_delay_ns", 2.0),
        output_delay_ns=sdc_cfg_dict.get("output_delay_ns", 2.0),
        output_load_pf=sdc_cfg_dict.get("output_load_pf", 0.05),
        driving_cell=sdc_cfg_dict.get("driving_cell", "sky130_fd_sc_hd__buf_1"),
        analysis_mode=sdc_cfg_dict.get("analysis_mode", "max"),
    )
    case_dir = args.output_dir / benchmark_id
    mapping_dir = case_dir / "mapping"
    sta_dir = case_dir / "sta"
    sdc_path = case_dir / f"{benchmark_id}.sdc"

    source_path = _source_for(benchmark_id, epfl_source)
    top_module = _top_module_for(benchmark_id)

    mapping_result = map_verilog_to_liberty(
        source_path,
        liberty_path,
        top_module=top_module,
        output_dir=mapping_dir,
        yosys_command=config.get("yosys_command", "yosys"),
        timeout_s=args.mapping_timeout_s,
    )
    units = parse_liberty_units(liberty_path)
    sdc_text = build_pre_layout_sdc(sdc_cfg, units=units)
    save_sdc(sdc_path, sdc_text)

    mapped_v = mapping_dir / "mapped.v"
    if mapping_result.status == "success" and mapped_v.exists():
        sta_result = run_opensta_pre_layout(
            netlist_path=mapped_v,
            liberty_path=liberty_path,
            sdc_path=sdc_path,
            output_dir=sta_dir,
            sta_command=args.sta_command,
            top_module=top_module,
            timeout_s=args.sta_timeout_s,
        )
    else:
        class _SkippedSta:
            def to_dict(self) -> dict[str, object]:
                return {"status": "skipped"}

        sta_result = _SkippedSta()

    return {
        "benchmark_id": benchmark_id,
        "source_path": str(source_path),
        "top_module": top_module,
        "liberty_path": str(liberty_path),
        "sdc_path": str(sdc_path),
        "mapping": mapping_result.to_dict(),
        "sta": sta_result.to_dict(),
    }


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    benchmark_ids = args.benchmark_ids or [
        entry["id"] for entry in config["epfl_benchmarks"]
    ]
    per_case: list[dict[str, Any]] = []
    for benchmark_id in benchmark_ids:
        try:
            case_report = _run_case(
                benchmark_id=benchmark_id, config=config, args=args
            )
        except Exception as exc:
            print(f"{benchmark_id}: {exc}", file=sys.stderr)
            continue
        per_case.append(case_report)
        mapping_status = case_report["mapping"]["status"]
        sta_status = case_report["sta"].get("status", "skipped")
        slack = case_report["sta"].get("slack")
        slack_str = f"{slack:.3f}" if isinstance(slack, (int, float)) else "n/a"
        print(
            f"{benchmark_id}: mapping={mapping_status} sta={sta_status}"
            f" slack={slack_str}"
        )

    summary = {
        "config_path": str(args.config),
        "sta_command": args.sta_command,
        "case_count": len(per_case),
        "per_case": per_case,
    }
    summary_path = args.output_dir / "stage_b_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())