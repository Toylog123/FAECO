"""Logic-rewrite repair (strategy R of failure-aware hybrid repair).

In the pre-layout (ideal-net) regime there is no wire load, so gate sizing
(strategy G) has little to exploit: a larger cell mainly raises its input
capacitance, which slows down the driving stage (observed on ISCAS89 s382,
where up-sizing made WNS *worse*).  Strategy R instead replaces a
critical-path cell with a *functionally equivalent* library cell of lower
intrinsic delay.

The canonical motivating case is ``sky130_fd_sc_hd__lpflow_inputiso1p_1``
(``X = A | SLEEP``).  It is functionally identical to ``or2`` but carries a
larger delay, so swapping it for ``or2`` recovers timing.

Equivalence is decided by canonicalising the Liberty ``function`` expression:
variable names are renamed to ``v0, v1, ...`` in order of first appearance,
and two cells whose canonical forms match are interchangeable.  The same
canonical form yields the pin map (``SLEEP -> B`` for the example above).

The hybrid repair loop tries, for every critical-path cell, its
functionally-equivalent candidates *and* its larger drive sizes, and keeps
only changes that improve the OpenSTA-measured WNS; candidates that make
timing worse (like over-sized cells in the ideal-net regime) are naturally
rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class LibCell:
    """A single SKY130 cell from the Liberty library."""

    name: str                 # e.g. "sky130_fd_sc_hd__or2_1"
    family: str               # e.g. "or2"
    size: int                 # e.g. 1
    output_pin: str           # e.g. "X"
    function: str             # raw Liberty function, "" if sequential cell
    input_pins: list[str] = field(default_factory=list)


_CELL_RE = re.compile(r'cell \("sky130_fd_sc_hd__([^"]+)"\) \{')
# pin definition: a bare `pin ("A")` or `pin(A)` (not `pg_pin (...)`),
# body up to the first closing brace
_PIN_DEF_RE = re.compile(
    r'(?<!\w)pin\s*\(\s*"?([A-Za-z0-9_]+)"?\s*\)\s*\{(.*?)\}', re.S
)


def _split_family_size(cell_name: str) -> tuple[str, int]:
    m = re.search(r"(.+)_(\d+)$", cell_name)
    if m:
        return m.group(1), int(m.group(2))
    return cell_name, 0


def parse_liberty_cells(liberty_text: str) -> dict[str, LibCell]:
    """Parse all combinational SKY130 cells from a Liberty file.

    Returns a mapping ``cell name -> LibCell``.  Cells without an output
    ``function`` (DFFs, power cells) are kept with ``function == ""``.
    """
    cells: dict[str, LibCell] = {}
    for m in _CELL_RE.finditer(liberty_text):
        cell_name = m.group(1)
        start = m.end()
        nxt = _CELL_RE.search(liberty_text, start)
        block = liberty_text[start: nxt.start() if nxt else len(liberty_text)]
        family, size = _split_family_size(cell_name)
        input_pins: list[str] = []
        output_pin = ""
        function = ""
        for pm in _PIN_DEF_RE.finditer(block):
            pin, pblock = pm.group(1), pm.group(2)
            if "direction" not in pblock:
                continue
            if '"input"' in pblock:
                input_pins.append(pin)
                continue
            if '"output"' in pblock:
                output_pin = pin
                f = re.search(r'function\s*:\s*"([^"]+)"', pblock)
                if f and "VPWR" not in f.group(1) and "VGND" not in f.group(1):
                    function = f.group(1)
        cells[f"sky130_fd_sc_hd__{cell_name}"] = LibCell(
            name=f"sky130_fd_sc_hd__{cell_name}",
            family=family,
            size=size,
            output_pin=output_pin,
            function=function,
            input_pins=input_pins,
        )
    return cells


def function_vars(function: str) -> list[str]:
    """Variables of a Liberty function in order of first appearance."""
    seen: list[str] = []
    for v in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", function):
        if v not in seen:
            seen.append(v)
    return seen


def canonical_function(function: str) -> str:
    """Rename variables to ``v0, v1, ...`` by first-appearance order."""
    out = function
    for i, v in enumerate(function_vars(function)):
        out = re.sub(r"\b" + re.escape(v) + r"\b", f"v{i}", out)
    return out


def equivalence_candidates(
    cell: LibCell, lib: dict[str, LibCell]
) -> list[tuple[str, dict[str, str]]]:
    """Return ``(new_type, pin_map)`` for every functionally-equivalent cell.

    ``pin_map`` maps the *source* cell's pin names to the candidate's pin
    names (e.g. ``{"A": "A", "SLEEP": "B"}`` for inputiso1p -> or2).  The
    source cell itself is excluded.  Cells with no function (DFFs) have no
    candidates.
    """
    if not cell.function:
        return []
    src_canon = canonical_function(cell.function)
    src_vars = function_vars(cell.function)
    out: list[tuple[str, dict[str, str]]] = []
    for other in lib.values():
        if other.name == cell.name or not other.function:
            continue
        if canonical_function(other.function) != src_canon:
            continue
        other_vars = function_vars(other.function)
        pin_map = {sv: ov for sv, ov in zip(src_vars, other_vars)}
        # map the output pin too when names differ
        if cell.output_pin and other.output_pin and cell.output_pin != other.output_pin:
            pin_map[cell.output_pin] = other.output_pin
        out.append((other.name, pin_map))
    return out


def apply_rewrite(
    mapped_text: str,
    inst: str,
    new_type: str,
    pin_map: dict[str, str],
) -> str:
    """Replace instance ``inst`` with ``new_type``, renaming pins per ``pin_map``.

    Pins not present in ``pin_map`` keep their original names.  Only the first
    matching instance is replaced.
    """
    pat = re.compile(
        r"(sky130_fd_sc_hd__\w+)\s+(" + re.escape(inst) + r")\s*\((.*?)\)\s*;",
        re.S,
    )

    def repl(m: re.Match) -> str:
        pin_body = m.group(3)
        new_pins = []
        for p, net in re.findall(r"\.(\w+)\(\s*([^)]+?)\s*\)", pin_body):
            new_pins.append(f".{pin_map.get(p, p)}({net.strip()})")
        body = ",\n    ".join(new_pins)
        return f"{new_type} {inst} (\n    {body}\n  );"

    out, n = pat.subn(repl, mapped_text, count=1)
    return out
