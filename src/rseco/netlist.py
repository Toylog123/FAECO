"""Minimal gate-level Verilog parsing for early FAECO experiments."""

from dataclasses import dataclass
import re
from pathlib import Path


@dataclass(frozen=True)
class Gate:
    gate_type: str
    name: str
    output: str
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class Netlist:
    module_name: str
    inputs: list[str]
    outputs: list[str]
    wires: list[str]
    gates: list[Gate]

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    def logic_levels(self) -> dict[str, int]:
        levels = {name: 0 for name in self.inputs}
        levels.update({"$false": 0, "$true": 0, "$undef": 0})
        remaining = list(self.gates)

        while remaining:
            progressed = False
            next_remaining: list[Gate] = []
            for gate in remaining:
                if all(signal in levels for signal in gate.inputs):
                    levels[gate.output] = max(levels[signal] for signal in gate.inputs) + 1
                    progressed = True
                else:
                    next_remaining.append(gate)
            if not progressed:
                unresolved = ", ".join(gate.name for gate in next_remaining)
                raise ValueError(f"cannot resolve logic levels for gates: {unresolved}")
            remaining = next_remaining

        return levels

    def logic_level(self, signal: str) -> int:
        return self.logic_levels()[signal]

    def max_logic_level(self) -> int:
        levels = self.logic_levels()
        return max(levels[output] for output in self.outputs)


def parse_verilog_netlist(path: str | Path) -> Netlist:
    text = Path(path).read_text(encoding="utf-8")
    module_match = re.search(r"\bmodule\s+(\w+)\s*\(", text)
    if not module_match:
        raise ValueError(f"missing module declaration: {path}")

    inputs: list[str] = []
    outputs: list[str] = []
    wires: list[str] = []
    gates: list[Gate] = []

    for line in _verilog_statements(text):
        if not line or line.startswith("//"):
            continue
        _collect_declaration(line, "input", inputs)
        _collect_declaration(line, "output", outputs)
        _collect_declaration(line, "wire", wires)

        instance = re.match(r"^(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;", line)
        if instance and instance.group(1) not in {"module", "input", "output", "wire"}:
            pins = [pin.strip() for pin in instance.group(3).split(",") if pin.strip()]
            if len(pins) < 2:
                raise ValueError(f"gate instance must have output and inputs: {line}")
            gates.append(
                Gate(
                    gate_type=instance.group(1),
                    name=instance.group(2),
                    output=pins[0],
                    inputs=tuple(pins[1:]),
                )
            )

    return Netlist(
        module_name=module_match.group(1),
        inputs=inputs,
        outputs=outputs,
        wires=wires,
        gates=gates,
    )


def _collect_declaration(line: str, keyword: str, target: list[str]) -> None:
    match = re.match(rf"^{keyword}\s+(.+?)[,;]?$", line)
    if not match:
        return
    for name in match.group(1).replace(";", "").split(","):
        cleaned = name.strip()
        if cleaned:
            target.append(cleaned)


def _verilog_statements(text: str) -> list[str]:
    statements: list[str] = []
    declaration: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        while True:
            if declaration:
                if re.match(r"^(input|output|wire)\b", line):
                    statements.append(" ".join(declaration))
                    declaration = []
                    continue
                declaration.append(line)
                if line.endswith(";"):
                    statements.append(" ".join(declaration))
                    declaration = []
                break

            if re.match(r"^(input|output|wire)\b", line) and line.endswith(","):
                declaration.append(line)
                break

            statements.append(line)
            break

    if declaration:
        statements.append(" ".join(declaration))
    return statements
