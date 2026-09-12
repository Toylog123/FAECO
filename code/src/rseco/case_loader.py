"""Load FAECO case metadata from the project data directory."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EcoCase:
    root: Path
    metadata: dict[str, Any]

    @property
    def case_id(self) -> str:
        return str(self.metadata["case_id"])

    @property
    def target_output(self) -> str:
        return str(self.metadata["target"]["output"])

    @property
    def original_netlist_path(self) -> Path:
        return self.root / "original" / "original.v"

    @property
    def resynthesized_netlist_path(self) -> Path:
        return self.root / "resynthesized" / "resynthesized.v"

    @property
    def original_analysis_netlist_path(self) -> Path:
        return self._analysis_netlist_path("original", self.original_netlist_path)

    @property
    def resynthesized_analysis_netlist_path(self) -> Path:
        return self._analysis_netlist_path("resynthesized", self.resynthesized_netlist_path)

    def _analysis_netlist_path(self, role: str, fallback: Path) -> Path:
        netlists = self.metadata.get("netlists", {})
        analysis = netlists.get("analysis", {}) if isinstance(netlists, dict) else {}
        relative_path = analysis.get(role) if isinstance(analysis, dict) else None
        return self.root / str(relative_path) if relative_path else fallback

    def json_path(self, relative_path: str) -> Path:
        return self.root / relative_path


def load_case(case_dir: str | Path) -> EcoCase:
    root = Path(case_dir)
    metadata = _parse_simple_yaml(root / "case.yaml")
    return EcoCase(root=root, metadata=metadata)


def _parse_simple_yaml(path: Path) -> dict[str, Any]:
    lines = [
        line.rstrip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    parsed, index = _parse_block(lines, 0, 0)
    if index != len(lines):
        raise ValueError(f"could not parse all YAML lines in {path}")
    if not isinstance(parsed, dict):
        raise ValueError(f"top-level YAML value must be a mapping: {path}")
    return parsed


def _parse_block(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index

    current_indent = _indent_of(lines[index])
    if current_indent < indent:
        return {}, index

    if lines[index].lstrip().startswith("- "):
        items: list[Any] = []
        while index < len(lines) and _indent_of(lines[index]) == indent and lines[index].lstrip().startswith("- "):
            items.append(_parse_scalar(lines[index].strip()[2:].strip()))
            index += 1
        return items, index

    result: dict[str, Any] = {}
    while index < len(lines):
        line_indent = _indent_of(lines[index])
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ValueError(f"unexpected indentation: {lines[index]}")

        stripped = lines[index].strip()
        if ":" not in stripped:
            raise ValueError(f"expected key-value line: {lines[index]}")
        key, raw_value = stripped.split(":", 1)
        raw_value = raw_value.strip()
        if raw_value:
            result[key] = _parse_scalar(raw_value)
            index += 1
        else:
            value, index = _parse_block(lines, index + 1, indent + 2)
            result[key] = value
    return result, index


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_scalar(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value.strip('"').strip("'")
