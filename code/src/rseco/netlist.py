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
    pin_names: tuple[str, ...] = ()
    output_pin: str | None = None
    additional_outputs: tuple[str, ...] = ()

    @property
    def all_outputs(self) -> tuple[str, ...]:
        """Connected output nets belonging to this one physical instance."""
        return tuple(signal for signal in (self.output, *self.additional_outputs) if signal)


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
        levels.update({"$false": 0, "$true": 0, "$undef": 0, "1'b0": 0, "1'b1": 0})
        remaining = list(self.gates)

        while remaining:
            progressed = False
            next_remaining: list[Gate] = []
            for gate in remaining:
                resolved_inputs = [
                    _constant_signal(self.resolve_alias(signal)) or self.resolve_alias(signal)
                    for signal in gate.inputs
                ]
                if all(signal in levels for signal in resolved_inputs):
                    level = max((levels[signal] for signal in resolved_inputs), default=0) + 1
                    for output in gate.all_outputs:
                        constant = _constant_signal(self.resolve_alias(output))
                        levels[output] = 0 if constant else level
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


def parse_verilog_netlist(
    path: str | Path,
    *,
    cell_output_functions: dict[str, dict[str, str]] | None = None,
) -> Netlist:
    text = Path(path).read_text(encoding="utf-8")
    module_match = re.search(r"\bmodule\s+(\w+)\s*\(", text)
    if not module_match:
        raise ValueError(f"missing module declaration: {path}")

    inputs: list[str] = []
    outputs: list[str] = []
    wires: list[str] = []
    gates: list[Gate] = []
    aliases: dict[str, str] = {}
    constant_aliases: dict[str, str] = {}
    instance_names: set[str] = set()

    # first pass: declarations and single-identifier assign aliases
    for line in _verilog_statements(text):
        if not line or line.startswith("//"):
            continue
        assign_match = re.match(r"^assign\s+(\S+)\s*=\s*([^;]+);", line)
        if assign_match:
            lhs = assign_match.group(1).strip()
            rhs = assign_match.group(2).strip()
            constant = _constant_signal(rhs)
            if re.fullmatch(r"\w+", rhs) or constant:
                aliases[lhs] = constant or rhs
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
            cell_type, instance_name = instance.group(1), instance.group(2)
            if instance_name in instance_names:
                raise ValueError(f"Duplicate instance in parsed netlist: {instance_name}")
            instance_names.add(instance_name)
            output_functions = (cell_output_functions or {}).get(cell_type)
            if output_functions is None and cell_type == "sky130_fd_sc_hd__conb_1":
                # Exact known cell semantics, retained for historical callers
                # without Liberty metadata.  Both outputs remain represented.
                output_functions = {"HI": "1", "LO": "0"}
            pins = [pin.strip() for pin in instance.group(3).split(",") if pin.strip()]
            if (pins and pins[0].startswith(".")) or (not pins and output_functions):
                connections = [
                    re.match(r"\.(\w+)\s*\(([^()]*)\)", pin) for pin in pins
                ]
                if not all(connections):
                    raise ValueError(f"malformed named-port instance: {line}")
                named = [
                    (match.group(1), match.group(2).strip()) for match in connections
                ]
                signal_map = dict(named)
                if output_functions:
                    output_pins = tuple(output_functions)
                else:
                    legacy_output = next(
                        (pin for pin, _ in named if pin in {"Y", "X", "Z", "Q", "Q_N"}),
                        None,
                    )
                    if legacy_output is None:
                        raise ValueError(
                            f"cannot determine output pin for named-port instance: {line}"
                        )
                    output_pins = (legacy_output,)
                connected_pins = tuple(pin for pin in output_pins if signal_map.get(pin))
                connected_outputs = tuple(_follow_alias(signal_map[pin], aliases) for pin in connected_pins)
                output_pin = connected_pins[0] if connected_pins else None
                raw_inputs = tuple(signal for pin, signal in named if pin not in output_pins and signal)
                for pin, output in zip(connected_pins, connected_outputs):
                    constant = _constant_signal((output_functions or {}).get(pin, ""))
                    if constant:
                        constant_aliases[output] = constant
                gates.append(
                    Gate(
                        gate_type=instance.group(1),
                        name=instance.group(2),
                        output=connected_outputs[0] if connected_outputs else "",
                        inputs=tuple(_follow_alias(signal, aliases) for signal in raw_inputs),
                        pin_names=tuple(pin for pin, _ in named),
                        output_pin=output_pin,
                        additional_outputs=connected_outputs[1:],
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

    # Add constant semantics after constructing physical output net identities.
    aliases.update(constant_aliases)
    return Netlist(
        module_name=module_match.group(1),
        inputs=inputs,
        outputs=outputs,
        wires=wires,
        gates=gates,
        signal_aliases=aliases,
    )


def _constant_signal(signal: str) -> str | None:
    """Recognise single-bit constants used by Liberty and mapped Verilog."""
    match = re.fullmatch(r"(?:1'[bBdDhH]|')?([01])", signal.strip())
    return f"1'b{match.group(1)}" if match else None


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
        if not cleaned:
            continue
        vec = re.match(r"^\[(\d+):(\d+)\]\s*(.+)$", cleaned)
        if vec:
            # Bit-blast vector declarations (e.g. "output [31:0] mem_addr;"
            # -> mem_addr[0]..mem_addr[31]) so netlist closure checks can
            # match the bit-level nets used by gate instances.
            msb, lsb = int(vec.group(1)), int(vec.group(2))
            base = vec.group(3).strip()
            lo, hi = min(msb, lsb), max(msb, lsb)
            if base.startswith("\\"):
                # Escaped identifier: Yosys writes bit nets as `\name [i]`.
                target.extend(f"{base} [{i}]" for i in range(lo, hi + 1))
            else:
                target.extend(f"{base}[{i}]" for i in range(lo, hi + 1))
        else:
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
