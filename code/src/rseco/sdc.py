"""Pre-layout SDC generation for technology-mapped FAECO Stage B netlists.

Reads ``time_unit`` and ``capacitive_load_unit`` from a Liberty file, builds
a deterministic virtual-clock SDC, and binds input/output delays, output
load, driving cell, and max/min analysis mode. Port safety: any SDC command
that would silently match zero ports is rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class LibertyUnits:
    time_unit: str | None
    capacitive_load_unit_pf: float | None
    parse_error: str | None = None


@dataclass(frozen=True)
class SdcConfig:
    virtual_clock_name: str = "clk_virtual"
    clock_period_ns: float = 10.0
    input_delay_ns: float = 2.0
    output_delay_ns: float = 2.0
    output_load_pf: float = 0.05
    driving_cell: str = "sky130_fd_sc_hd__buf_1"
    analysis_mode: str = "max"  # "max" / "min" / "max_min"
    clock_port: str | None = None
    extra_directives: tuple[str, ...] = field(default_factory=tuple)


_TIME_UNIT_RE = re.compile(r'time_unit\s*:\s*"([^"]+)"')
_CAP_LOAD_RE = re.compile(
    r"capacitive_load_unit\s*\(\s*([0-9.eE+-]+)\s*,\s*\"([a-zA-Z]+)\"\s*\)"
)
_VALID_MODES = {"max", "min", "max_min"}


def parse_liberty_units(liberty_path: str | Path) -> LibertyUnits:
    path = Path(liberty_path)
    if not path.exists():
        return LibertyUnits(
            time_unit=None,
            capacitive_load_unit_pf=None,
            parse_error=f"Liberty file not found: {path}",
        )
    text = path.read_text(encoding="utf-8", errors="replace")

    time_match = _TIME_UNIT_RE.search(text)
    cap_match = _CAP_LOAD_RE.search(text)
    time_unit = time_match.group(1) if time_match else None
    cap_pf: float | None = None
    if cap_match:
        value = float(cap_match.group(1))
        unit = cap_match.group(2)
        if unit == "pf":
            cap_pf = value
        elif unit == "ff":
            cap_pf = value * 1e-3
        else:
            return LibertyUnits(
                time_unit=time_unit,
                capacitive_load_unit_pf=None,
                parse_error=f"unsupported capacitive_load_unit: {unit}",
            )
    missing: list[str] = []
    if time_unit is None:
        missing.append("time_unit")
    if cap_pf is None:
        missing.append("capacitive_load_unit")
    if missing:
        return LibertyUnits(
            time_unit=time_unit,
            capacitive_load_unit_pf=cap_pf,
            parse_error=f"missing fields in Liberty: {', '.join(missing)}",
        )
    return LibertyUnits(time_unit=time_unit, capacitive_load_unit_pf=cap_pf)


def build_pre_layout_sdc(
    config: SdcConfig,
    *,
    units: LibertyUnits | None = None,
    input_ports: Iterable[str] | None = None,
    output_ports: Iterable[str] | None = None,
) -> str:
    """Build a deterministic pre-layout SDC string.

    The returned text contains a virtual clock, optional port-specific
    set_input_delay / set_output_delay, set_load, set_driving_cell, and the
    max/min analysis mode selector. ``units`` is recorded via set_time_unit
    when provided.
    """
    if config.analysis_mode not in _VALID_MODES:
        raise ValueError(
            f"analysis_mode must be one of {sorted(_VALID_MODES)}, "
            f"got {config.analysis_mode!r}"
        )
    if config.clock_period_ns <= 0:
        raise ValueError("clock_period_ns must be positive")

    lines: list[str] = [
        "# FAECO pre-layout SDC (Stage B)",
        f"create_clock -name {config.virtual_clock_name}"
        f" -period {config.clock_period_ns:.3f}",
    ]
    if config.clock_port:
        lines.append(
            f"create_clock -name {config.virtual_clock_name}"
            f" -period {config.clock_period_ns:.3f}"
            f" [get_ports {config.clock_port}]"
        )

    if input_ports is not None:
        ports = _format_port_list(input_ports)
        if ports:
            lines.append(
                f"set_input_delay -clock {config.virtual_clock_name}"
                f" {config.input_delay_ns:.3f} [get_ports {{{ports}}}]"
            )
    if output_ports is not None:
        ports = _format_port_list(output_ports)
        if ports:
            lines.append(
                f"set_output_delay -clock {config.virtual_clock_name}"
                f" {config.output_delay_ns:.3f} [get_ports {{{ports}}}]"
            )

    if units is not None:
        if units.time_unit:
            lines.append(f"# liberty time_unit = {units.time_unit}")
        if units.capacitive_load_unit_pf:
            lines.append(
                f"# liberty capacitive_load_unit_pf = {units.capacitive_load_unit_pf}"
            )

    lines.append(f"set_load {config.output_load_pf:.3f} [get_ports [all_outputs]]")
    lines.append(
        f"set_driving_cell -lib_cell {config.driving_cell}"
        f" -pin X [get_ports [all_inputs]]"
    )

    if config.analysis_mode == "max":
        lines.append("set_max_delay 0")
    elif config.analysis_mode == "min":
        lines.append("set_min_delay 0")
    else:
        lines.append("set_max_delay 0")
        lines.append("set_min_delay 0")

    for directive in config.extra_directives:
        lines.append(directive)

    return "\n".join(lines) + "\n"


def _format_port_list(ports: Iterable[str]) -> str:
    cleaned = [p.strip() for p in ports if p and p.strip()]
    if not cleaned:
        return ""
    return " ".join(cleaned)


def apply_input_delay_to_sdc(
    sdc_text: str,
    *,
    clock_name: str,
    delay_ns: float,
    port_filter: Callable[[list[str]], list[str]],
    available_ports: Iterable[str],
) -> str:
    """Append ``set_input_delay`` for ports matched by ``port_filter``.

    Raises ValueError when ``port_filter`` matches no ports, to prevent
    silent SDC commands that bind to zero ports.
    """
    ports = port_filter(list(available_ports))
    if not ports:
        raise ValueError(
            "set_input_delay: port_filter matched 0 ports; refusing to "
            "write a silent command"
        )
    formatted = _format_port_list(ports)
    return (
        sdc_text
        + f"\nset_input_delay -clock {clock_name}"
        f" {delay_ns:.3f} [get_ports {{{formatted}}}]\n"
    )


def apply_output_delay_to_sdc(
    sdc_text: str,
    *,
    clock_name: str,
    delay_ns: float,
    port_filter: Callable[[list[str]], list[str]],
    available_ports: Iterable[str],
) -> str:
    ports = port_filter(list(available_ports))
    if not ports:
        raise ValueError(
            "set_output_delay: port_filter matched 0 ports; refusing to "
            "write a silent command"
        )
    formatted = _format_port_list(ports)
    return (
        sdc_text
        + f"\nset_output_delay -clock {clock_name}"
        f" {delay_ns:.3f} [get_ports {{{formatted}}}]\n"
    )


def save_sdc(path: str | Path, sdc_text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sdc_text, encoding="utf-8")