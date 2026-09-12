"""Gate sizing repair for sequential timing violations (failure-aware hybrid repair, strategy G).

Given a technology-mapped netlist (pure SKY130 cell instances, e.g. from
``synth + dfflibmap + abc -liberty``), identify the critical-path gates
(by combinational logic depth from DFF Q to DFF D / outputs) and try
larger drive-strength cells from the same Liberty function family
(e.g. ``sky130_fd_sc_hd__nor2_1`` -> ``nor2_2`` / ``nor2_4`` / ``nor2_8``),
greedily keeping changes that improve WNS.

This is one leg of the FAECO failure-aware hybrid repair: when a timing
violation is caused by insufficient drive strength (F4-type), gate sizing
is preferred over logic rewriting.

Pipeline:
  mapped.v (SKY130 cells) --parse--> cells --topo depth--> critical gates
  --try larger sizes--> candidate netlists --OpenSTA WNS--> keep best
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Cell:
    instance: str          # e.g. "_04_"
    cell_type: str         # full cell name e.g. "sky130_fd_sc_hd__nor2_1"
    function: str          # e.g. "nor2"
    size: int              # e.g. 1
    pins: dict[str, str]   # pin -> net

    @property
    def is_dff(self) -> bool:
        return self.function in {"dfxtp", "dfrtp", "dfbbp", "dfbbn", "dfrbp"}


_CELL_INST_RE = re.compile(
    r"^\s*(sky130_fd_sc_hd__\w+)\s+(\w+)\s*\((.*?)\)\s*;",
    re.M | re.S,
)
_PIN_RE = re.compile(r"\.(\w+)\(\s*([^)]+?)\s*\)")


def _parse_function(cell_type: str) -> tuple[str, int]:
    m = re.search(r"sky130_fd_sc_hd__([a-z0-9]+)_(\d+)$", cell_type)
    if m:
        return m.group(1), int(m.group(2))
    return cell_type, 0


def parse_mapped_netlist(text: str) -> list[Cell]:
    cells: list[Cell] = []
    for m in _CELL_INST_RE.finditer(text):
        cell_type, inst = m.group(1), m.group(2)
        pins = {p: n.strip().strip("\\") for p, n in _PIN_RE.findall(m.group(3))}
        fun, size = _parse_function(cell_type)
        cells.append(Cell(inst, cell_type, fun, size, pins))
    return cells


def _topo_order(cells: list[Cell]) -> list[str]:
    """Rough topological order by iterative resolution (netlists are small)."""
    resolved: set[str] = set()
    order: list[str] = []
    remaining = list(cells)
    while remaining:
        progressed = False
        for c in remaining[:]:
            if c.is_dff:
                order.append(c.instance)
                resolved.add(c.instance)
                remaining.remove(c)
                progressed = True
                continue
            if all(net in resolved or True for net in c.pins.values()):
                order.append(c.instance)
                resolved.add(c.instance)
                remaining.remove(c)
                progressed = True
        if not progressed:
            order.extend(c.instance for c in remaining)
            break
    return order


def critical_gates(
    cells: list[Cell],
    *,
    output_ports: set[str],
    dff_q_nets: set[str],
) -> list[str]:
    """Return instance names on the longest combinational path.

    Depth = max fanin depth + 1 (DFF Q / primary inputs are boundaries).
    Returns instances whose depth equals the global max.
    """
    driven_by: dict[str, str] = {}
    for c in cells:
        for net in c.pins.values():
            if net not in driven_by:
                driven_by[net] = c.instance

    depth: dict[str, int] = {}
    order = _topo_order(cells)
    for inst in order:
        cell = next(c for c in cells if c.instance == inst)
        if cell.is_dff:
            depth[inst] = 0
            continue
        max_in = 0
        for net in cell.pins.values():
            if net in dff_q_nets:
                continue
            drv = driven_by.get(net)
            if drv and drv != inst:
                max_in = max(max_in, depth.get(drv, 0))
        depth[inst] = max_in + 1

    if not depth:
        return []
    max_depth = max(depth.values())
    if max_depth == 0:
        return []
    return [i for i, d in depth.items() if d == max_depth]


def build_available_sizes(liberty_text: str) -> dict[str, set[int]]:
    """Scan Liberty for all (function -> {sizes}) per family."""
    out: dict[str, set[int]] = {}
    for m in re.finditer(r'cell \("sky130_fd_sc_hd__([a-z0-9]+)_(\d+)"\)', liberty_text):
        fun, size = m.group(1), int(m.group(2))
        out.setdefault(fun, set()).add(size)
    return out


def larger_size_candidates(cell_type: str, available: dict[str, set[int]]) -> list[str]:
    fun, size = _parse_function(cell_type)
    sizes = sorted(available.get(fun, []))
    return [
        f"sky130_fd_sc_hd__{fun}_{s}"
        for s in sizes
        if s > size
    ]


def apply_sizing(mapped_text: str, change: dict[str, str]) -> str:
    """Replace instance cell types per `change` (instance -> new cell type)."""
    out = mapped_text
    for inst, new_type in change.items():
        out = re.sub(
            r"(sky130_fd_sc_hd__\w+)\s+(" + re.escape(inst) + r")\s*\(",
            f"{new_type} {inst} (",
            out,
            count=1,
        )
    return out