"""Generate a simplified assign-style cells.v from the SKY130 HD Liberty.

N31-03 path A (user-selected): provide cell function models so Yosys can
read the Liberty-mapped netlist (mapped.v) for equivalence checking.

Why this file: Yosys `read_liberty` imports Liberty cells as *blackbox*
(ports only, no logic), so Yosys equiv/SAT cannot expand them; ABC
`read_blif` also fails to build models for Liberty subcircuits; and the
downloaded skywater cell Verilog models use UDP primitives that Yosys 0.9
cannot parse.  This script instead extracts each cell's boolean
`function` from the Liberty file and emits a plain assign-style Verilog
module that Yosys CAN read.

Output: ``benchmarks/raw/skywater_cells_models/sky130_cells_v2.v``
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIB = (
    ROOT
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)
OUT = (
    ROOT
    / "benchmarks"
    / "raw"
    / "skywater_cells_models"
    / "sky130_cells_v2.v"
)


def parse_cells(lib_text: str) -> dict[str, dict]:
    """Return {cell_name: {'pins': [(pin, dir)], 'functions': [...]}}."""
    cell_starts = [m.start() for m in re.finditer(r"^\s*cell \(", lib_text, re.M)]
    cell_ends = cell_starts[1:] + [len(lib_text)]
    cells: dict[str, dict] = {}
    for i, s in enumerate(cell_starts):
        name_m = re.search(r'cell \(\"([^\"]+)\"\)', lib_text[s:])
        if not name_m:
            continue
        name = name_m.group(1)
        block = lib_text[s : cell_ends[i]]
        # Only plain signal pins (exclude pg_pin like VGND/VNB/VPB/VPWR).
        pin_starts = [
            m.start() for m in re.finditer(r"^\s{8}pin \(", block, re.M)
        ]
        pin_ends = pin_starts[1:] + [len(block)]
        pins: list[tuple[str, str]] = []
        for j, ps in enumerate(pin_starts):
            pin_block = block[ps : pin_ends[j]]
            name_m = re.search(r'pin \(\"(\w+)\"\)', pin_block)
            dir_m = re.search(r'direction : \"(\w+)\"', pin_block)
            if name_m and dir_m:
                pins.append((name_m.group(1), dir_m.group(1)))
        funcs = re.findall(r'function : \"([^\"]+)\"', block)
        cells[name] = {"pins": pins, "functions": funcs}
    return cells


def liberty_fn_to_verilog(expr: str) -> str:
    """Convert a Liberty boolean function to a Verilog assign RHS.

    Liberty uses ``!`` for NOT and ``& | ^`` for AND/OR/XOR with
    parentheses; Verilog is the same except NOT is ``~``.  ``0``/``1``
    constants are mapped to ``1'b0``/``1'b1``.
    """
    expr = expr.replace("!", "~")
    expr = re.sub(r"\b1\b", "1'b1", expr)
    expr = re.sub(r"\b0\b", "1'b0", expr)
    return expr


def to_verilog_module(cell: str, info: dict) -> str | None:
    pins = info["pins"]
    funcs = info["functions"]
    if not funcs:
        return None
    # first function is the real boolean function; a second is usually
    # the power_down_function (!VPWR + VGND) — skip it.
    fn = funcs[0]
    candidates = [
        f for f in funcs
        if not any(s in f for s in ("VPWR", "VGND", "VNB", "VPB"))
    ]
    if not candidates:
        return None
    fn = candidates[0]
    outputs = [p for p, d in pins if d == "output"]
    inputs = [p for p, d in pins if d == "input"]
    if len(outputs) != 1 or not inputs:
        # skip multi-output / no-input cells (not needed for mapped.v)
        return None
    out = outputs[0]
    rhs = liberty_fn_to_verilog(fn)
    lines = [
        f"module {cell} ({', '.join(inputs)}, {out});",
        *[f"  input {p};" for p in inputs],
        f"  output {out};",
        f"  assign {out} = {rhs};",
        "endmodule",
    ]
    return "\n".join(lines)


def main() -> int:
    lib_text = LIB.read_text(encoding="utf-8")
    cells = parse_cells(lib_text)
    mods: list[str] = []
    for cell in sorted(cells):
        mod = to_verilog_module(cell, cells[cell])
        if mod:
            mods.append(mod)
    OUT.write_text("\n\n".join(mods) + "\n", encoding="utf-8")
    print(f"wrote {OUT} with {len(mods)} modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())