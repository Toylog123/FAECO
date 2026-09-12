"""Minimal gate-level Verilog parsing for early FAECO experiments."""

from dataclasses import dataclass, field
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
    signal_aliases: dict[str, str] = field(default_factory=dict)

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    def resolve_alias(self, signal: str) -> str:
        seen: set[str] = set()
        current = signal
        while current in self.signal_aliases and current not in seen:
            seen.add(current)
            current = self.signal_aliases[current]
        return current

    def logic_levels(self) -> dict[str, int]:
        levels = {name: 0 for name in self.inputs}
        levels.update({"$false": 0, "$true": 0, "$undef": 0})
        remaining = list(self.gates)

        while remaining:
            progressed = False
            next_remaining: list[Gate] = []
            for gate in remaining:
                resolved_inputs = [self.resolve_alias(signal) for signal in gate.inputs]
                if all(signal in levels for signal in resolved_inputs):
                    levels[gate.output] = max(levels[signal] for signal in resolved_inputs) + 1
                    progressed = True
                else:
                    next_remaining.append(gate)
            if not progressed:
                unresolved = ", ".join(gate.name for gate in next_remaining)
                raise ValueError(f"cannot resolve logic levels for gates: {unresolved}")
            remaining = next_remaining

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.signal_aliases.items():
                resolved = self.resolve_alias(rhs)
                if resolved in levels and levels.get(lhs) != levels[resolved]:
                    levels[lhs] = levels[resolved]
                    changed = True

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
    aliases: dict[str, str] = {}

    # first pass: declarations and single-identifier assign aliases
    for line in _verilog_statements(text):
        if not line or line.startswith("//"):
            continue
        assign_match = re.match(r"^assign\s+(\S+)\s*=\s*([^;]+);", line)
        if assign_match:
            lhs = assign_match.group(1).strip()
            rhs = assign_match.group(2).strip()
            if re.fullmatch(r"\w+", rhs):
                aliases[lhs] = rhs
            continue
        _collect_declaration(line, "input", inputs)
        _collect_declaration(line, "output", outputs)
        _collect_declaration(line, "wire", wires)

    # second pass: instances (aliases are complete by now)
    for line in _verilog_statements(text):
        if not line or line.startswith("//") or line.startswith("assign"):
            continue
        instance = re.match(r"^(\w+)\s+(\w+)\s*\((.*)\)\s*;", line)
        if instance and instance.group(1) not in {"module", "input", "output", "wire"}:
            pins = [pin.strip() for pin in instance.group(3).split(",") if pin.strip()]
            if pins and pins[0].startswith("."):
                connections = [
                    re.match(r"\.(\w+)\s*\(([^()]*)\)", pin) for pin in pins
                ]
                if not all(connections):
                    raise ValueError(f"malformed named-port instance: {line}")
                named = [
                    (match.group(1), match.group(2).strip()) for match in connections
                ]
                output_pin = next(
                    (pin for pin, _ in named if pin in {"Y", "X", "Z", "Q", "Q_N"}),
                    None,
                )
                if output_pin is None:
                    raise ValueError(
                        f"cannot determine output pin for named-port instance: {line}"
                    )
                signal_map = dict(named)
                raw_output = signal_map[output_pin]
                raw_inputs = tuple(signal for pin, signal in named if pin != output_pin)
                gates.append(
                    Gate(
                        gate_type=instance.group(1),
                        name=instance.group(2),
                        output=_follow_alias(raw_output, aliases),
                        inputs=tuple(_follow_alias(signal, aliases) for signal in raw_inputs),
                    )
                )
            else:
                if len(pins) < 2:
                    raise ValueError(f"gate instance must have output and inputs: {line}")
                gates.append(
                    Gate(
                        gate_type=instance.group(1),
                        name=instance.group(2),
                        output=_follow_alias(pins[0], aliases),
                        inputs=tuple(_follow_alias(signal, aliases) for signal in pins[1:]),
                    )
                )

    return Netlist(
        module_name=module_match.group(1),
        inputs=inputs,
        outputs=outputs,
        wires=wires,
        gates=gates,
        signal_aliases=aliases,
    )


def _follow_alias(signal: str, aliases: dict[str, str]) -> str:
    seen: set[str] = set()
    current = signal
    while current in aliases and current not in seen:
        seen.add(current)
        current = aliases[current]
    return current


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
    instance_buffer: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        while True:
            if instance_buffer:
                instance_buffer.append(line)
                if ");" in line or line.endswith(";"):
                    statements.append(" ".join(instance_buffer))
                    instance_buffer = []
                break

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

            if (line.endswith("(") or line.endswith(" (")) and not re.match(
                r"^(module|endmodule)\b", line
            ):
                instance_buffer.append(line)
                break

            statements.append(line)
            break

    if declaration:
        statements.append(" ".join(declaration))
    if instance_buffer:
        statements.append(" ".join(instance_buffer))
    return statements
