"""Parasitic-aware SPEF generation for pre-layout ECO verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


_OUTPUT_PINS = {"Y", "X", "Q", "Z", "SN", "RN"}


@dataclass(frozen=True)
class MappedNet:
    name: str
    pins: tuple[tuple[str, str], ...] = ()
    is_port: bool = False

    @property
    def fanout(self) -> int:
        return max(0, len(self.pins) - 1)

    def driver(self) -> tuple[str, str] | None:
        for inst, pin in self.pins:
            if pin in _OUTPUT_PINS:
                return (inst, pin)
        return None


@dataclass
class MappedNetlist:
    module_name: str
    ports: list[str] = field(default_factory=list)
    port_dirs: dict[str, str] = field(default_factory=dict)
    nets: dict[str, MappedNet] = field(default_factory=dict)
    instances: list[tuple[str, str]] = field(default_factory=list)


def parse_mapped_verilog(path: str | Path) -> MappedNetlist:
    """Parse a Yosys-generated SKY130 mapped netlist into nets (top module)."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    module_matches = list(re.finditer(r"\bmodule\s+(\w+)\s*\(", text))
    if not module_matches:
        raise ValueError(f"no module declaration found: {path}")
    module_names = [m.group(1) for m in module_matches]
    # Choose the top module: the one never instantiated by another module.
    instantiated: set[str] = set()
    inst_re = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_$]*)\s+"
        r"([A-Za-z_][A-Za-z0-9_$]*)\s*\(",
        re.MULTILINE,
    )
    for m in inst_re.finditer(text):
        cell_type = m.group(1)
        if cell_type in module_names:
            instantiated.add(cell_type)
    top = next((n for n in module_names if n not in instantiated), module_names[-1])

    top_match = next(m for m in module_matches if m.group(1) == top)
    starts = [m.start() for m in module_matches]
    end = min((s for s in starts if s > top_match.start()), default=len(text))
    body = text[top_match.start():end]

    netlist = MappedNetlist(module_name=top)
    nets: dict[str, list[tuple[str, str]]] = {}
    ports: set[str] = set()
    port_dirs: dict[str, str] = {}

    for m in re.finditer(r"\b(input|output|inout)\s+[^;]*?(\w+)\s*[;,\n]", body):
        direction, name = m.group(1), m.group(2)
        ports.add(name)
        port_dirs[name] = {"input": "I", "output": "O", "inout": "B"}[direction]

    for m in re.finditer(r"\bwire\s+([^;]+);", body):
        for name in re.split(r"[,\s]+", m.group(1).strip()):
            if name:
                nets.setdefault(name, [])

    inst_re2 = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_$]*)\s+"
        r"([A-Za-z_][A-Za-z0-9_$]*)\s*\(([^;]*?)\)\s*;",
        re.MULTILINE,
    )
    for m in inst_re2.finditer(body):
        cell_type, inst_name = m.group(1), m.group(2)
        if cell_type.startswith(("module", "input", "output", "wire", "assign")):
            continue
        netlist.instances.append((cell_type, inst_name))
        pin_body = m.group(3)
        for pin_m in re.finditer(r"\.\s*([A-Za-z_][A-Za-z0-9_$]*)\s*\(\s*([^)]*?)\s*\)", pin_body):
            pin, net = pin_m.group(1), pin_m.group(2).strip()
            if not net:
                continue
            nets.setdefault(net, []).append((inst_name, pin))

    for name, pins in nets.items():
        netlist.nets[name] = MappedNet(name=name, pins=tuple(pins), is_port=name in ports)
    netlist.ports = sorted(ports)
    netlist.port_dirs = port_dirs
    return netlist


def estimate_net_rc(
    net: MappedNet,
    *,
    unit_len_um: float = 40.0,
    fanout_penalty: float = 1.0,
    depth_penalty: float = 1.0,
) -> tuple[float, float]:
    """Estimate net R/C with tunable physical penalties.

    ``fanout_penalty`` > 1.0 lengthens high-fanout nets (the physical-load
    feedback signal: a high-fanout driver is where post-layout wire delay
    concentrates); ``depth_penalty`` lengthens deep paths.  Both default to
    1.0, preserving the legacy lumped estimate.
    """
    length = (
        unit_len_um
        * max(1.0, (net.fanout ** 0.5))
        * fanout_penalty
        * depth_penalty
    )
    r = 0.09 * length
    # wire-only capacitance (fF/um), converted to pF for SPEF; pin caps
    # come from the Liberty via OpenSTA (PIN_CAP NONE avoids double count)
    c = 0.21 * length / 1000.0
    return r, c


def build_spef(
    netlist: MappedNetlist,
    *,
    unit_len_um: float = 40.0,
    fanout_penalty: float = 1.0,
    depth_penalty: float = 1.0,
) -> str:
    lines: list[str] = []
    lines.append('*SPEF "IEEE 1481-1998"')
    lines.append(f'*DESIGN "{netlist.module_name}"')
    lines.append('*DATE "2026-08-05"')
    lines.append('*VENDOR "FAECO"')
    lines.append('*PROGRAM "src/rseco/spef.py"')
    lines.append('*VERSION "1.0"')
    lines.append('*DESIGN_FLOW "PIN_CAP NONE"')
    lines.append("*DIVIDER /")
    lines.append("*DELIMITER :")
    lines.append("*BUS_DELIMITER [ ]")
    lines.append("*T_UNIT 1 NS")
    lines.append("*C_UNIT 1 PF")
    lines.append("*R_UNIT 1 OHM")
    lines.append("*L_UNIT 1 HENRY")
    lines.append("*PORTS")
    for port in netlist.ports:
        lines.append(f"{port} {netlist.port_dirs.get(port, 'I')}")
    lines.append("")

    idx = 1
    for net in netlist.nets.values():
        if not net.pins:
            continue
        r_ohm, c_pf = estimate_net_rc(
            net,
            unit_len_um=unit_len_um,
            fanout_penalty=fanout_penalty,
            depth_penalty=depth_penalty,
        )
        lines.append(f"*D_NET {net.name} {c_pf:.6f}")
        lines.append("*CONN")
        driver = net.driver()
        for inst, pin in net.pins:
            if net.is_port:
                lines.append(f"*P {net.name} {netlist.port_dirs.get(net.name, 'I')}")
            else:
                direction = "O" if driver and (inst, pin) == driver else "I"
                lines.append(f"*I {inst}:{pin} {direction}")
        lines.append("*CAP")
        if driver:
            lines.append(f"{idx} {driver[0]}:{driver[1]} {c_pf:.6f}")
        elif net.pins:
            first = net.pins[0]
            if net.is_port:
                lines.append(f"{idx} {net.name} {c_pf:.6f}")
            else:
                lines.append(f"{idx} {first[0]}:{first[1]} {c_pf:.6f}")
        lines.append("*RES")
        if driver and len(net.pins) > 1:
            r_piece = r_ohm / max(1, net.fanout)
            for inst, pin in net.pins:
                if (inst, pin) == driver:
                    continue
                lines.append(f"{idx} {driver[0]}:{driver[1]} {inst}:{pin} {r_piece:.4f}")
        lines.append("*END")
        lines.append("")
        idx += 1

    return "\n".join(lines)


def write_spef(
    path: str | Path,
    netlist: MappedNetlist,
    *,
    unit_len_um: float = 40.0,
    fanout_penalty: float = 1.0,
    depth_penalty: float = 1.0,
) -> Path:
    out = Path(path)
    out.write_text(
        build_spef(
            netlist,
            unit_len_um=unit_len_um,
            fanout_penalty=fanout_penalty,
            depth_penalty=depth_penalty,
        ),
        encoding="utf-8",
    )
    return out
