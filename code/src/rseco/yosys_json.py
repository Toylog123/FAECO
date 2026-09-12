"""Import Yosys JSON netlists into the internal FAECO netlist model."""

from pathlib import Path
from dataclasses import dataclass
from typing import Any
import json
import subprocess

from .netlist import Gate, Netlist
from .toolchain import resolve_tool_command


_OUTPUT_PORTS = {"Y", "Q"}


@dataclass(frozen=True)
class YosysJsonNormalizationResult:
    status: str
    json_path: Path
    command: str
    returncode: int | None
    log: str
    sanitized_input_path: Path | None = None


def normalize_verilog_to_yosys_json(
    verilog_path: str | Path,
    json_path: str | Path,
    *,
    yosys_command: str = "yosys",
    log_path: str | Path | None = None,
    timeout_s: float = 120.0,
) -> YosysJsonNormalizationResult:
    """Run Yosys simplemap normalization and write a JSON netlist."""
    output_path = Path(json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tool = resolve_tool_command("yosys", [yosys_command], env_var="FAECO_YOSYS" if yosys_command == "yosys" else None)
    if tool is None:
        return YosysJsonNormalizationResult(
            status="unavailable",
            json_path=output_path,
            command=yosys_command,
            returncode=None,
            log=f"Yosys command not found: {yosys_command}",
        )

    input_path, sanitized_path = _prepare_yosys_json_input(Path(verilog_path), output_path)
    script = "; ".join(
        [
            f"read_verilog {_yosys_path(input_path)}",
            "proc",
            "flatten",
            "opt",
            "simplemap",
            "clean",
            f"write_json {_yosys_path(output_path)}",
        ]
    )
    command = [*tool.argv, "-q", "-p", script]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        log = (completed.stdout or "") + (completed.stderr or "")
        status = "success" if completed.returncode == 0 and output_path.exists() else "error"
        returncode: int | None = completed.returncode
    except subprocess.TimeoutExpired as exc:
        log = (exc.stdout or "") + (exc.stderr or "")
        status = "timeout"
        returncode = 124

    if log_path is not None:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(log_path).write_text(log, encoding="utf-8")

    return YosysJsonNormalizationResult(
        status=status,
        json_path=output_path,
        command=" ".join(command),
        returncode=returncode,
        log=log,
        sanitized_input_path=sanitized_path,
    )


def parse_yosys_json_netlist(path: str | Path, module_name: str | None = None) -> Netlist:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    modules = data.get("modules")
    if not isinstance(modules, dict) or not modules:
        raise ValueError(f"missing Yosys JSON modules: {path}")

    raw_module_name = module_name or _select_module_name(modules)
    if raw_module_name not in modules:
        raise ValueError(f"module not found in Yosys JSON: {raw_module_name}")
    module = modules[raw_module_name]

    ports = module.get("ports", {})
    netnames = module.get("netnames", {})
    bit_names = _build_bit_name_map(ports, netnames)

    inputs = _port_names_by_direction(ports, "input")
    outputs = _port_names_by_direction(ports, "output")
    port_name_set = set(inputs) | set(outputs)
    wires = _wire_names(netnames, port_name_set)
    gates = _parse_cells(module.get("cells", {}), bit_names)
    gates.extend(_constant_output_gates(ports, bit_names, gates))

    return Netlist(
        module_name=_normalize_identifier(raw_module_name),
        inputs=inputs,
        outputs=outputs,
        wires=wires,
        gates=gates,
    )


def _select_module_name(modules: dict[str, Any]) -> str:
    top_modules = [name for name, module in modules.items() if module.get("attributes", {}).get("top")]
    if len(top_modules) == 1:
        return top_modules[0]
    if len(modules) == 1:
        return next(iter(modules))
    raise ValueError("multiple modules found; pass module_name explicitly")


def _port_names_by_direction(ports: dict[str, Any], direction: str) -> list[str]:
    return [_normalize_identifier(name) for name, port in ports.items() if port.get("direction") == direction]


def _wire_names(netnames: dict[str, Any], port_name_set: set[str]) -> list[str]:
    wires: list[str] = []
    seen: set[str] = set()
    for raw_name in netnames:
        name = _normalize_identifier(raw_name)
        if name in port_name_set or name in seen:
            continue
        wires.append(name)
        seen.add(name)
    return wires


def _build_bit_name_map(ports: dict[str, Any], netnames: dict[str, Any]) -> dict[str, str]:
    bit_names: dict[str, str] = {}
    for raw_name, port in ports.items():
        _record_bits(bit_names, raw_name, port.get("bits", []), overwrite=True)
    for raw_name, netname in netnames.items():
        _record_bits(bit_names, raw_name, netname.get("bits", []), overwrite=False)
    return bit_names


def _record_bits(bit_names: dict[str, str], raw_name: str, bits: list[Any], overwrite: bool) -> None:
    if not isinstance(bits, list):
        return
    base_name = _normalize_identifier(raw_name)
    for index, bit in enumerate(bits):
        key = _bit_key(bit) or _constant_name(bit)
        if key is None:
            continue
        name = base_name if len(bits) == 1 else f"{base_name}[{index}]"
        if overwrite or key not in bit_names:
            bit_names[key] = name


def _parse_cells(cells: dict[str, Any], bit_names: dict[str, str]) -> list[Gate]:
    gates: list[Gate] = []
    for raw_name, cell in cells.items():
        connections = cell.get("connections", {})
        output_port = _select_output_port(connections)
        output_bits = connections.get(output_port, [])
        if not output_bits:
            continue

        gate_type = _normalize_gate_type(str(cell.get("type", "UNKNOWN")))
        input_ports = [port for port in connections if port != output_port]
        for output_index, output_bit in enumerate(output_bits):
            output = _signal_name(output_bit, bit_names)
            inputs = tuple(
                _signal_name(bits[min(output_index, len(bits) - 1)], bit_names)
                for port in input_ports
                for bits in [connections.get(port, [])]
                if bits
            )
            gate_name = _normalize_identifier(raw_name)
            if len(output_bits) > 1:
                gate_name = f"{gate_name}[{output_index}]"
            gates.append(Gate(gate_type=gate_type, name=gate_name, output=output, inputs=inputs))
    return gates


def _constant_output_gates(ports: dict[str, Any], bit_names: dict[str, str], gates: list[Gate]) -> list[Gate]:
    driven_outputs = {gate.output for gate in gates}
    extra_gates: list[Gate] = []
    for raw_name, port in ports.items():
        if port.get("direction") != "output":
            continue
        bits = port.get("bits", [])
        if not isinstance(bits, list):
            continue
        for index, bit in enumerate(bits):
            constant = _constant_name(bit)
            if constant is None:
                continue
            output = _normalize_identifier(raw_name) if len(bits) == 1 else f"{_normalize_identifier(raw_name)}[{index}]"
            if output in driven_outputs:
                continue
            extra_gates.append(
                Gate(
                    gate_type="BUF",
                    name=f"$const${output}",
                    output=output,
                    inputs=(constant,),
                )
            )
    return extra_gates


def _select_output_port(connections: dict[str, Any]) -> str:
    for port in ("Y", "Q"):
        if port in connections:
            return port
    for port in connections:
        if port.upper() in _OUTPUT_PORTS:
            return port
    raise ValueError(f"cell has no recognized output port: {sorted(connections)}")


def _normalize_gate_type(raw_type: str) -> str:
    gate_type = raw_type
    if gate_type.startswith("$_") and gate_type.endswith("_"):
        gate_type = gate_type[2:-1]
    elif gate_type.startswith("$"):
        gate_type = gate_type[1:]
    return gate_type.upper()


def _signal_name(bit: Any, bit_names: dict[str, str]) -> str:
    constant = _constant_name(bit)
    if constant is not None:
        return constant
    key = _bit_key(bit)
    if key is None:
        return str(bit)
    return bit_names.get(key, _constant_name(bit) or f"$bit${key}")


def _bit_key(bit: Any) -> str | None:
    if isinstance(bit, int):
        return str(bit)
    if isinstance(bit, str) and bit.isdecimal():
        return bit
    return None


def _constant_name(bit: Any) -> str | None:
    if bit == "0":
        return "$false"
    if bit == "1":
        return "$true"
    if bit in {"x", "z"}:
        return "$undef"
    return None


def _normalize_identifier(raw_name: str) -> str:
    name = raw_name.strip()
    if name.startswith("\\"):
        name = name[1:].rstrip()
    return name


def _prepare_yosys_json_input(verilog_path: Path, json_path: Path) -> tuple[Path, Path | None]:
    try:
        data = verilog_path.read_bytes()
    except OSError:
        return verilog_path, None
    if not data.startswith(b"\xef\xbb\xbf"):
        return verilog_path, None
    sanitized_path = json_path.with_suffix(".sanitized.v")
    sanitized_path.write_bytes(data[3:])
    return sanitized_path, sanitized_path


def _yosys_path(path: Path) -> str:
    return str(path).replace("\\", "/")
