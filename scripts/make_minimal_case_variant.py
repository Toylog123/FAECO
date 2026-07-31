"""Create a minimal FAECO case variant with a different target output."""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.case_loader import load_case  # noqa: E402
from rseco.graph import extract_fanin_cone  # noqa: E402
from rseco.netlist import parse_verilog_netlist  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-case-dir", type=Path, required=True)
    parser.add_argument("--output-case-dir", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--target-output", required=True)
    parser.add_argument("--critical-path-id", default="TBD")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        make_case_variant(
            source_case_dir=args.source_case_dir.resolve(),
            output_case_dir=args.output_case_dir.resolve(),
            case_id=args.case_id,
            target_output=args.target_output,
            critical_path_id=args.critical_path_id,
            force=args.force,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(args.output_case_dir)
    return 0


def make_case_variant(
    *,
    source_case_dir: Path,
    output_case_dir: Path,
    case_id: str,
    target_output: str,
    critical_path_id: str,
    force: bool = False,
) -> None:
    if output_case_dir.exists():
        if not force:
            raise FileExistsError(f"output case already exists: {output_case_dir}")
        shutil.rmtree(output_case_dir)

    source_case = load_case(source_case_dir)
    original = parse_verilog_netlist(source_case.original_netlist_path)
    if target_output not in original.outputs:
        raise ValueError(f"target output is not in source netlist outputs: {target_output}")

    cone = extract_fanin_cone(original, roots=[target_output])
    shutil.copytree(source_case_dir, output_case_dir)

    for relative_path in [
        "cones/target_cone.json",
        "patches/candidates.json",
        "patches/replacement.json",
        "patches/selected_patch.json",
        "results/metrics.json",
    ]:
        path = output_case_dir / relative_path
        if path.exists():
            path.unlink()

    metadata = dict(source_case.metadata)
    metadata["case_id"] = case_id
    metadata["target"] = {
        **metadata["target"],
        "output": target_output,
        "critical_path_id": critical_path_id,
        "cone_roots": [target_output],
        "cone_boundary_inputs": cone.boundary_inputs,
        "cone_boundary_outputs": [target_output],
    }
    metadata["status"] = {
        **metadata.get("status", {}),
        "stage": "generated_variant",
        "verified": False,
    }
    (output_case_dir / "case.yaml").write_text(_format_yaml(metadata), encoding="utf-8")


def _format_yaml(value: Any, indent: int = 0) -> str:
    lines = _format_yaml_lines(value, indent)
    return "\n".join(lines) + "\n"


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
