"""Build per-case and runtime summary tables from a Stage B summary JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="stage_b_summary.json produced by run_stage_b_pre_layout_sta.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write tables/.",
    )
    return parser.parse_args()


def _per_case_row(entry: dict) -> dict:
    mapping = entry.get("mapping", {}) if isinstance(entry, dict) else {}
    sta = entry.get("sta", {}) if isinstance(entry, dict) else {}
    return {
        "benchmark_id": entry.get("benchmark_id"),
        "mapping_status": mapping.get("status") if isinstance(mapping, dict) else None,
        "mapping_runtime_s": mapping.get("runtime_s") if isinstance(mapping, dict) else None,
        "sta_status": sta.get("status") if isinstance(sta, dict) else None,
        "sta_runtime_s": sta.get("runtime_s") if isinstance(sta, dict) else None,
        "wns": sta.get("wns") if isinstance(sta, dict) else None,
        "tns": sta.get("tns") if isinstance(sta, dict) else None,
        "slack": sta.get("slack") if isinstance(sta, dict) else None,
        "slack_status": sta.get("slack_status") if isinstance(sta, dict) else None,
    }


def _runtime_row(entry: dict) -> dict:
    mapping = entry.get("mapping", {}) if isinstance(entry, dict) else {}
    sta = entry.get("sta", {}) if isinstance(entry, dict) else {}
    mapping_rt = mapping.get("runtime_s") if isinstance(mapping, dict) else 0
    sta_rt = sta.get("runtime_s") if isinstance(sta, dict) else 0
    return {
        "benchmark_id": entry.get("benchmark_id"),
        "mapping_runtime_s": mapping_rt,
        "sta_runtime_s": sta_rt,
        "total_runtime_s": (mapping_rt or 0) + (sta_rt or 0),
    }


def main() -> int:
    args = parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    per_case = summary.get("per_case", [])
    args.output_dir.mkdir(parents=True, exist_ok=True)

    case_rows = [_per_case_row(e) for e in per_case]
    runtime_rows = [_runtime_row(e) for e in per_case]

    case_json = args.output_dir / "stage_b_case_summary.json"
    case_md = args.output_dir / "stage_b_case_summary.md"
    runtime_json = args.output_dir / "stage_b_runtime.json"
    runtime_md = args.output_dir / "stage_b_runtime.md"

    case_payload = {
        "schema_version": 1,
        "source_summary": str(args.summary),
        "case_count": len(case_rows),
        "rows": case_rows,
    }
    case_json.write_text(
        json.dumps(case_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    case_md_lines = [
        "# Stage B Case Summary",
        "",
        "| benchmark | mapping | mapping_runtime_s | sta | sta_runtime_s | wns | tns | slack | slack_status |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in case_rows:
        wns = r["wns"] if r["wns"] is not None else "n/a"
        tns = r["tns"] if r["tns"] is not None else "n/a"
        slack = r["slack"] if r["slack"] is not None else "n/a"
        mapping_rt = r["mapping_runtime_s"] if r["mapping_runtime_s"] is not None else 0.0
        sta_rt = r["sta_runtime_s"] if r["sta_runtime_s"] is not None else 0.0
        case_md_lines.append(
            f"| {r['benchmark_id']} | {r['mapping_status']} | {mapping_rt:.3f}"
            f" | {r['sta_status']} | {sta_rt:.3f}"
            f" | {wns} | {tns} | {slack} | {r['slack_status']} |"
        )
    case_md.write_text("\n".join(case_md_lines) + "\n", encoding="utf-8")

    runtime_payload = {
        "schema_version": 1,
        "source_summary": str(args.summary),
        "case_count": len(runtime_rows),
        "rows": runtime_rows,
    }
    runtime_json.write_text(
        json.dumps(runtime_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    runtime_md_lines = [
        "# Stage B Runtime Breakdown",
        "",
        "| benchmark | mapping_s | sta_s | total_s |",
        "|---|---|---|---|",
    ]
    for r in runtime_rows:
        runtime_md_lines.append(
            f"| {r['benchmark_id']} | {r['mapping_runtime_s']:.3f}"
            f" | {r['sta_runtime_s']:.3f} | {r['total_runtime_s']:.3f} |"
        )
    runtime_md.write_text("\n".join(runtime_md_lines) + "\n", encoding="utf-8")

    print(f"case summary: {case_json}")
    print(f"runtime table: {runtime_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())