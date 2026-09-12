"""Create a minimal FAECO case from a local raw Verilog netlist."""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.graph import extract_fanin_cone  # noqa: E402
from rseco.netlist import parse_verilog_netlist  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-verilog", type=Path, required=True)
    parser.add_argument("--output-case-dir", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--circuit", required=True)
    parser.add_argument("--target-output", required=True)
    parser.add_argument("--critical-path-id", default="TBD")
    parser.add_argument("--original-source", default="TBD")
    parser.add_argument("--license-note", default="public benchmark")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        make_case_from_raw(
            raw_verilog=args.raw_verilog.resolve(),
            output_case_dir=args.output_case_dir.resolve(),
            case_id=args.case_id,
            suite=args.suite,
            circuit=args.circuit,
            target_output=args.target_output,
            critical_path_id=args.critical_path_id,
            original_source=args.original_source,
            license_note=args.license_note,
            force=args.force,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(args.output_case_dir)
    return 0


def make_case_from_raw(
    *,
    raw_verilog: Path,
    output_case_dir: Path,
    case_id: str,
    suite: str,
    circuit: str,
    target_output: str,
    critical_path_id: str,
    original_source: str,
    license_note: str,
    force: bool = False,
) -> None:
    if output_case_dir.exists():
        if not force:
            raise FileExistsError(f"output case already exists: {output_case_dir}")
        shutil.rmtree(output_case_dir)

    netlist = parse_verilog_netlist(raw_verilog)
    if target_output not in netlist.outputs:
        raise ValueError(f"target output is not in raw netlist outputs: {target_output}")
    cone = extract_fanin_cone(netlist, roots=[target_output])

    for subdir in ["original", "resynthesized", "cones", "patches", "results"]:
        (output_case_dir / subdir).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(raw_verilog, output_case_dir / "original" / "original.v")
    shutil.copyfile(raw_verilog, output_case_dir / "resynthesized" / "resynthesized.v")
    (output_case_dir / "cones" / "candidate_cones.json").write_text("{}\n", encoding="utf-8")

    metadata = {
        "case_id": case_id,
        "benchmark": {
            "suite": suite,
            "circuit": circuit,
            "type": "combinational",
        },
        "source": {
            "original_source": original_source,
            "license_note": license_note,
        },
        "toolchain": {
            "yosys_version": "TBD",
            "abc_version": "TBD",
            "opensta_version": "optional",
        },
        "generation": {
            "original_script": "local_raw_copy",
            "resynthesized_script": "local_raw_copy",
            "target_constraint": {
                "type": "logic_level",
                "value": netlist.logic_level(target_output),
            },
        },
        "target": {
            "output": target_output,
            "critical_path_id": critical_path_id,
            "cone_roots": [target_output],
            "cone_boundary_inputs": cone.boundary_inputs,
            "cone_boundary_outputs": [target_output],
        },
        "patch": {
            "initial_cut_method": "fixed_min_cut",
            "refinement_method": "failure_aware",
            "ranking_method": "deterministic_score",
        },
        "metrics": {
            "required": [
                "gate_count",
                "logic_level",
                "patch_size",
                "change_ratio",
                "equivalence_result",
                "runtime_total",
            ],
            "optional": ["WNS", "TNS", "violating_paths"],
        },
        "status": {
            "stage": "generated_from_raw",
            "verified": False,
        },
    }
    (output_case_dir / "case.yaml").write_text(_format_yaml(metadata), encoding="utf-8")


def _format_yaml(value: Any, indent: int = 0) -> str:
    return "\n".join(_format_yaml_lines(value, indent)) + "\n"


def _format_yaml_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(_format_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_format_scalar(item)}")
        return lines
    if isinstance(value, list):
        return [f"{prefix}- {_format_scalar(item)}" for item in value]
    return [f"{prefix}{_format_scalar(value)}"]


def _format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
