"""Netlist sanity checks for post-ECO mapped Verilog.

The hybrid repair loop rewrites a mapped netlist (gate sizing, logic rewrite
and buffer insertion).  Several rewrite bugs surface as *illegal* netlists
that a timing tool may still happily evaluate (e.g. two buffers driving one
net reads as a parallel driver and inflates WNS).  This module provides
cheap checks that every experiment's final netlist must pass.
"""

from __future__ import annotations

from rseco.gate_sizing import parse_mapped_netlist

# SKY130 combinational/sequential output pins (single-driver).
OUTPUT_PINS = {"X", "Y", "Q", "Z"}


def find_multi_driver_nets(mapped_text: str, output_pins: set[str] | None = None) -> dict[str, list[tuple[str, str]]]:
    """Return {net: [(instance, pin), ...]} for nets driven by >1 output pin.

    A legal structural netlist has exactly one driver per net; multiple
    drivers (e.g. several buffers tied to the same net name) is a rewrite
    bug.  Module output ports are driven by a cell, so they show up here
    only when more than one cell drives them.
    """
    pins = output_pins or OUTPUT_PINS
    drivers: dict[str, list[tuple[str, str]]] = {}
    for cell in parse_mapped_netlist(mapped_text):
        for pin, net in cell.pins.items():
            if pin in pins:
                drivers.setdefault(net, []).append((cell.instance, pin))
    return {net: drv for net, drv in drivers.items() if len(drv) > 1}


def audit_netlist(mapped_text: str, *, report: bool = True) -> dict:
    """Run all netlist sanity checks; return a JSON-serialisable audit dict.

    Checks:
      * single-driver nets (no multi-driver)
      * every cell instance has at least one output pin connection
      * every buffer instance has an output (X) connection
    """
    multi = find_multi_driver_nets(mapped_text)
    cells = parse_mapped_netlist(mapped_text)
    no_output = [
        (c.instance, c.cell_type)
        for c in cells
        if not any(p in (OUTPUT_PINS | {"Z"}) for p in c.pins)
    ]
    buf_no_output = [
        (c.instance, c.cell_type)
        for c in cells
        if "buf" in c.cell_type and "X" not in c.pins
    ]
    result = {
        "multi_driver_nets": multi,
        "cells_no_output_pin": no_output,
        "buffers_without_X": buf_no_output,
        "ok": not multi and not no_output and not buf_no_output,
    }
    if report and not result["ok"]:
        print(
            f"[netlist_audit] INVALID: {len(multi)} multi-driver nets, "
            f"{len(no_output)} cells w/o output pin, {len(buf_no_output)} buffers w/o X"
        )
    return result

