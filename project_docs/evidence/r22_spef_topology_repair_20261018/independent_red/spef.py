"""Parasitic-aware SPEF generation for pre-layout ECO verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from functools import lru_cache
from .gate_sizing import _mapped_code
from .logic_rewrite import _CELL_RE, _pin_blocks
from .verilog_modules import module_spans


_NAME = r'(?:\\[^\s]+|[A-Za-z_$][\w$]*(?:\[\d+\])?)'


@dataclass(frozen=True)
class MappedNet:
    name: str
    pins: tuple[tuple[str, str], ...] = ()
    is_port: bool = False
    pin_directions: tuple[str, ...] = ()
    port_connections: tuple[tuple[str, str], ...] = ()

    @property
    def fanout(self) -> int:
        return max(0, len(self.pins) + len(self.port_connections) - 1)

    def driver(self) -> tuple[str, str] | None:
        if len(self.pin_directions) != len(self.pins):
            raise ValueError(f'Actual pin directions unavailable for net {self.name}')
        drivers = [p for p, d in zip(self.pins, self.pin_directions) if d == 'O']
        external = [p for p, d in self.port_connections if d == 'I']
        if len(drivers) + len(external) > 1:
            raise ValueError(f'Ambiguous multiple drivers for net {self.name}')
        return drivers[0] if drivers else None


@dataclass
class MappedNetlist:
    module_name: str
    ports: list[str] = field(default_factory=list)
    port_dirs: dict[str, str] = field(default_factory=dict)
    nets: dict[str, MappedNet] = field(default_factory=dict)
    instances: list[tuple[str, str]] = field(default_factory=list)
    omitted_unused_constant_aliases: list[str] = field(default_factory=list)


def _declared_names(declaration: str) -> dict[str, list[str]]:
    """Expand constant packed ranges; reject expressions and unpacked arrays."""
    declaration = re.sub(r'\b(?:wire|reg|logic|signed|unsigned)\b', '', declaration).strip()
    packed = re.match(r'\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\]', declaration)
    indices = None
    if packed:
        left, right = map(int, packed.groups())
        indices = range(left, right + (1 if right >= left else -1), 1 if right >= left else -1)
        declaration = declaration[packed.end():].strip()
    result = {}
    for entry in declaration.split(','):
        name = entry.strip()
        if not re.fullmatch(r'\\[^\s]+|[A-Za-z_$][\w$]*', name):
            raise ValueError(f'Unsupported net declaration: {declaration}')
        name = name.removeprefix('\\')
        result[name] = [f'{name}[{i}]' for i in indices] if indices is not None else [name]
    return result


def _module_interface(text: str):
    header = re.match(r'\s*module\s+\S+?\s*\((.*?)\)\s*;', text, re.S)
    if header is None:
        raise ValueError('Unsupported module header for SPEF')
    ports, widths = {}, {}
    def declare(direction, declaration):
        if direction == 'inout':
            raise ValueError('Bidirectional SPEF nets are unsupported')
        entries = _declared_names(declaration)
        widths.update(entries)
        for bits in entries.values():
            for bit in bits:
                role = {'input': 'I', 'output': 'O'}[direction]
                if bit in ports and ports[bit] != role:
                    raise ValueError(f'Conflicting port directions for {bit}')
                ports[bit] = role
    ansi = bool(re.search(r'\b(?:input|output|inout)\b', header.group(1)))
    if ansi:
        direction, packed = None, ''
        for item in header.group(1).split(','):
            match = re.match(r'\s*(input|output|inout)\b(.*)', item, re.S)
            if match:
                direction, item = match.groups()
                item = re.sub(r'\b(?:wire|reg|logic|signed|unsigned)\b', '', item).strip()
                span = re.match(r'\[[^\]]+\]', item)
                packed = span.group() if span else ''
                item = item[span.end():] if span else item
            if direction is None:
                raise ValueError('Incomplete ANSI port declaration')
            declare(direction, packed + ' ' + item)
    body = text[header.end():]
    for direction, declaration in re.findall(r'\b(input|output|inout)\s+([^;]+);', body):
        declare(direction, declaration)
    for declaration in re.findall(r'\bwire\s+([^;]+);', body):
        for name, bits in _declared_names(declaration).items():
            if name in widths and widths[name] != bits:
                raise ValueError(f'Conflicting ranges for {name}')
            widths[name] = bits
    if not ansi:
        declared_port_names = {name.strip().removeprefix('\\') for name in header.group(1).split(',') if name.strip()}
        expected_bits = {bit for name in declared_port_names for bit in widths.get(name, [name])}
        if expected_bits != set(ports):
            raise ValueError('Incomplete or conflicting non-ANSI port declarations')
    return ports, widths, body


@lru_cache(maxsize=4)
def _liberty_pin_directions(text: str):
    """Reuse complete Liberty pin blocks, including outputs without functions."""
    result = {}
    headers = list(_CELL_RE.finditer(text))
    for index, header in enumerate(headers):
        end = headers[index+1].start() if index+1 < len(headers) else len(text)
        roles = {}
        for name, body in _pin_blocks(text[header.end():end]):
            direction = re.search(r'\bdirection\s*:\s*"?(\w+)"?\s*;', body)
            if direction:
                roles[name] = {'input':'I', 'output':'O', 'inout':'B'}.get(direction.group(1))
        result['sky130_fd_sc_hd__'+header.group(1)] = roles
    return result


def parse_mapped_verilog(path: str | Path, *, liberty_text: str | None = None,
                         top_module: str | None = None) -> MappedNetlist:
    """Parse mapped named-port connectivity with actual library/module roles.

    The no-library convenience API reads the configured actual Liberty. Production
    callers pass their frozen Liberty and explicit top. Unknown syntax/roles are
    rejected; output names never determine direction.
    """
    from .real_wns import _PHYSICAL_INSTANCE_RE
    if liberty_text is None:
        from .opensta import LIB_SEQ
        liberty_text = Path(LIB_SEQ).read_text(encoding='utf-8')
    roles = _liberty_pin_directions(liberty_text)
    spans = module_spans(Path(path).read_text(encoding='utf-8'))
    modules = {span.name: _mapped_code(span.text) for span in spans}
    interfaces = {name: _module_interface(text) for name, text in modules.items()}
    instantiated = {m.group(1) for text in modules.values() for m in _PHYSICAL_INSTANCE_RE.finditer(text)
                    if m.group(1) in modules and m.group(1) != 'module'}
    tops = set(modules) - instantiated
    if top_module is None:
        if len(tops) != 1:
            raise ValueError('SPEF requires an unambiguous top module')
        top_module = next(iter(tops))
    if top_module not in modules:
        raise ValueError(f'SPEF top module unavailable: {top_module}')
    ports, widths, body = interfaces[top_module]
    parent = {}
    def canonical(name):
        parent.setdefault(name, name)
        current, trail = name, []
        while parent[current] != current:
            trail.append(current)
            current = parent[current]
        for item in trail:
            parent[item] = current
        return current
    def signals(expression):
        expr = expression.strip()
        if re.fullmatch(r"(?:\d+)?'[sS]?[bBdDhHoO][0-9a-fA-F_xXzZ]+|'[01]", expr):
            if re.search('[xXzZ]', expr):
                raise ValueError('Unknown/high-impedance SPEF literal is unsupported')
            return []  # Literal ties have no named wire in OpenSTA.
        if not re.fullmatch(_NAME, expr):
            raise ValueError(f'Unsupported SPEF connection expression: {expr}')
        expr = expr.removeprefix('\\')
        return widths.get(expr, [expr])
    constant_aliases = set()
    for lhs, rhs in re.findall(r'\bassign\s+([^;=]+)=([^;]+);', body):
        left, right = signals(lhs), signals(rhs)
        if left and not right:
            constant_aliases.update(left)
            continue
        if len(left) != len(right):
            raise ValueError('Unsupported constant or width-changing SPEF alias')
        for a, b in zip(left, right):
            parent[canonical(a)] = canonical(b)
    pins = []
    instances = []
    seen_instances = set()
    for match in _PHYSICAL_INSTANCE_RE.finditer(body):
        cell_type, instance, pin_body = match.groups()
        instance = instance.removeprefix('\\')
        if instance in seen_instances:
            raise ValueError(f'Duplicate SPEF instance: {instance}')
        seen_instances.add(instance)
        direction_map = roles.get(cell_type)
        if cell_type in interfaces:
            direction_map = interfaces[cell_type][0]
        if direction_map is None:
            raise ValueError(f'Unknown SPEF cell/module: {cell_type}')
        instances.append((cell_type, instance))
        pin_matches = list(re.finditer(r'\.\s*([A-Za-z_$][\w$]*)\s*\(([^()]*)\)', pin_body))
        remainder = re.sub(r'\.\s*([A-Za-z_$][\w$]*)\s*\(([^()]*)\)', '', pin_body)
        if re.sub(r'[,\s]', '', remainder):
            raise ValueError(f'Unsupported SPEF named pins at {instance}')
        seen_pins = set()
        offset = 0
        for pin_match in pin_matches:
            if not re.fullmatch(r'\s*' if not seen_pins else r'\s*,\s*', pin_body[offset:pin_match.start()]):
                raise ValueError(f'Unsupported SPEF pin separator at {instance}')
            offset = pin_match.end()
            pin, expression = pin_match.groups()
            if pin in seen_pins or direction_map.get(pin) not in {'I', 'O'}:
                raise ValueError(f'Unknown, duplicate or bidirectional SPEF pin: {instance}:{pin}')
            seen_pins.add(pin)
            if not expression.strip():
                if direction_map[pin] == 'I':
                    raise ValueError(f'Empty input pin: {instance}:{pin}')
                continue
            nets = signals(expression)
            if len(nets) > 1:
                raise ValueError(f'Unresolved vector cell pin: {instance}:{pin}')
            for net in nets:
                pins.append((canonical(net), (instance, pin), direction_map[pin]))
        if pin_body[offset:].strip():
            raise ValueError(f'Unsupported SPEF pin tail at {instance}')
        missing = [pin for pin, direction in direction_map.items() if direction == 'I' and pin not in seen_pins]
        if missing:
            raise ValueError(f'Missing SPEF input pins at {instance}: {missing}')
    remainder = _PHYSICAL_INSTANCE_RE.sub('', body)
    remainder = re.sub(r'\b(?:input|output|inout|wire)\s+[^;]+;', '', remainder)
    remainder = re.sub(r'\bassign\s+[^;]+;', '', remainder)
    remainder = re.sub(r'\bendmodule\b', '', remainder).strip()
    if remainder:
        raise ValueError(f'Unsupported or unparsed SPEF syntax: {remainder[:100]}')
    all_names = set(ports) | {net for bits in widths.values() for net in bits} | {p[0] for p in pins}
    groups = {}
    for name in sorted(all_names):
        groups.setdefault(canonical(name), []).append(name)
    netlist = MappedNetlist(top_module, sorted(ports), dict(ports), instances=instances)
    grouped_pins = {}
    for net, pin, direction in pins:
        grouped_pins.setdefault(canonical(net), []).append((pin, direction))
    grouped_constants = {}
    for item in constant_aliases:
        grouped_constants.setdefault(canonical(item), []).append(item)
    for key, names in groups.items():
        external = tuple((name, ports[name]) for name in names if name in ports)
        name = external[0][0] if external else names[0]
        endpoints = grouped_pins.get(key, [])
        constants = grouped_constants.get(key, [])
        if constants:
            if endpoints or external:
                raise ValueError(f'Connected constant alias requires an explicit physical tie source: {name}')
            netlist.omitted_unused_constant_aliases.extend(sorted(constants))
            continue
        net = MappedNet(name, tuple(p for p, _ in endpoints), bool(external),
                        tuple(d for _, d in endpoints), external)
        net.driver()  # Reject driver ambiguity before writing a partial SPEF.
        netlist.nets[name] = net
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
        external_drivers = [name for name, direction in net.port_connections if direction == 'I']
        driver_node = f'{driver[0]}:{driver[1]}' if driver else (external_drivers[0] if external_drivers else None)
        if driver_node is None:
            raise ValueError(f'Undriven SPEF net: {net.name}')
        for name, direction in net.port_connections:
            lines.append(f'*P {name} {direction}')
        for (inst, pin), direction in zip(net.pins, net.pin_directions):
            lines.append(f"*I {inst}:{pin} {direction}")
        lines.append("*CAP")
        lines.append(f"1 {driver_node} {c_pf:.6f}")
        lines.append("*RES")
        nodes = [f'{inst}:{pin}' for inst, pin in net.pins] + [name for name, _ in net.port_connections]
        sinks = [node for node in nodes if node != driver_node]
        r_piece = r_ohm / max(1, len(sinks))
        for res_index, node in enumerate(sinks, 1):
            lines.append(f"{res_index} {driver_node} {node} {r_piece:.4f}")
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
