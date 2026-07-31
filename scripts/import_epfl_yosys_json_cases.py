"""Import pinned EPFL Verilog sources into Yosys JSON gate-level artifacts."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.yosys_json import normalize_verilog_to_yosys_json, parse_yosys_json_netlist  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "benchmarks" / "source_manifests" / "epfl_v2025.1.json")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--wave", type=int, default=1)
    parser.add_argument("--yosys-command", default="yosys")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = import_epfl_yosys_json_cases(
            manifest_path=args.manifest.resolve(),
            source_root=args.source_root.resolve(),
            output_dir=args.output_dir.resolve(),
            wave=args.wave,
            yosys_command=args.yosys_command,
            force=args.force,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(report["report_path"])
    return 0


def import_epfl_yosys_json_cases(
    *,
    manifest_path: Path,
    source_root: Path,
    output_dir: Path,
    wave: int,
    yosys_command: str,
    force: bool = False,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if output_dir.exists() and not force and any(output_dir.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = [case for case in manifest.get("candidate_files", []) if case.get("import_wave") == wave]
    cases: list[dict[str, Any]] = []
    for entry in selected:
        benchmark_id = str(entry["benchmark_id"])
        source_path = source_root / str(entry["path"])
        if not source_path.exists():
            raise FileNotFoundError(f"missing EPFL source file: {source_path}")

        case_dir = output_dir / benchmark_id
        case_dir.mkdir(parents=True, exist_ok=True)
        json_path = case_dir / f"{benchmark_id}.yosys.json"
        log_path = case_dir / "yosys_json.log"
        result = normalize_verilog_to_yosys_json(
            source_path,
            json_path,
            yosys_command=yosys_command,
            log_path=log_path,
        )
        case_report: dict[str, Any] = {
            "benchmark_id": benchmark_id,
            "group": entry.get("group"),
            "source_path": _relative_or_absolute(source_path, source_root),
            "source_blob_sha1": entry.get("blob_sha1"),
            "reference_blif_path": entry.get("reference_blif_path"),
            "reference_blif_blob_sha1": entry.get("reference_blif_blob_sha1"),
            "status": result.status,
            "yosys_json": _relative_or_absolute(json_path, output_dir),
            "yosys_log": _relative_or_absolute(log_path, output_dir),
            "yosys_returncode": result.returncode,
            "sanitized_input": str(result.sanitized_input_path) if result.sanitized_input_path else None,
        }
        if result.status == "success":
            netlist = parse_yosys_json_netlist(json_path)
            case_report.update(
                {
                    "module_name": netlist.module_name,
                    "inputs": netlist.inputs,
                    "outputs": netlist.outputs,
                    "gate_count": netlist.gate_count,
                    "max_logic_level": netlist.max_logic_level(),
                }
            )
        cases.append(case_report)

    report_path = output_dir / "import_report.json"
    report = {
        "schema_version": 1,
        "suite_id": manifest.get("suite_id"),
        "repository": manifest.get("repository"),
        "tag": manifest.get("tag"),
        "source_commit": manifest.get("commit"),
        "license": manifest.get("license"),
        "wave": wave,
        "case_count": len(cases),
        "cases": cases,
        "report_path": str(report_path),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
