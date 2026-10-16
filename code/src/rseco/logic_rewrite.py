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

Combinational equivalence conservatively matches every Liberty output ``function`` and
``three_state`` condition.  One shared variable-role map preserves data and
output-enable relationships, including ``SLEEP -> B`` for the example above.
Cells carrying sequential state metadata are outside strategy R: an output
function such as ``IQ`` refers to state, not a combinational input function.

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
    next_state: str = ""
    clocked_on: str = ""
    latch_enable: str = ""
    clear: str = ""
    preset: str = ""
    state_var: str = ""
    state_inv_var: str = ""
    output_functions: dict[str, str] = field(default_factory=dict)
    sequential_kind: str = ""
    three_state_functions: dict[str, str] = field(default_factory=dict)


_CELL_RE = re.compile(r'cell \("sky130_fd_sc_hd__([^"]+)"\) \{')
# Pin headers only: output metadata can follow nested timing/power groups.
_PIN_DEF_RE = re.compile(
    r'(?<!\w)pin\s*\(\s*"?([A-Za-z0-9_]+)"?\s*\)\s*\{'
)
_LIBERTY_BRACE_RE = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/|[{}]', re.S)


def _pin_blocks(block: str):
    """Yield complete pin bodies, ignoring braces in strings and comments."""
    for header in _PIN_DEF_RE.finditer(block):
        depth = 1
        for token in _LIBERTY_BRACE_RE.finditer(block, header.end()):
            if token.group() == "{":
                depth += 1
            elif token.group() == "}":
                depth -= 1
                if depth == 0:
                    yield header.group(1), block[header.end():token.start()]
                    break
        else:
            raise ValueError(f"Unterminated Liberty pin block: {header.group(1)}")


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
        next_state = ""
        clocked_on = ""
        latch_enable = ""
        clear = ""
        preset = ""
        state_var = ""
        state_inv_var = ""
        output_functions: dict[str, str] = {}
        three_state_functions: dict[str, str] = {}
        sequential_kind = ""
        for pin, pblock in _pin_blocks(block):
            direction = re.search(r'\bdirection\s*:\s*"?(\w+)"?\s*;', pblock)
            if not direction:
                continue
            if direction.group(1) == "input":
                input_pins.append(pin)
                continue
            if direction.group(1) == "output":
                output_pin = pin
                f = re.search(r'\bfunction\s*:\s*"([^"]+)"', pblock)
                if f and "VPWR" not in f.group(1) and "VGND" not in f.group(1):
                    function = f.group(1)
                    output_functions[pin] = f.group(1).strip()
                three_state = re.search(r'\bthree_state\s*:\s*"([^"]+)"', pblock)
                if three_state:
                    three_state_functions[pin] = three_state.group(1).strip()
        ff = re.search(r"\bff\s*\([^)]*\)\s*\{(.*?)\}", block, re.S)
        if ff:
            sequential_kind = "ff"
            ff_body = ff.group(1)
            ff_header = re.search(r"\bff\s*\(([^)]*)\)", block, re.S)
            ff_vars = [v.strip().strip('"') for v in (ff_header.group(1) if ff_header else "").split(",") if v.strip()]
            state_var = ff_vars[0] if ff_vars else ""
            state_inv_var = ff_vars[1] if len(ff_vars) > 1 else ""
            next_match = re.search(r"next_state\s*:\s*\"([^\"]+)\"", ff_body)
            clock_match = re.search(r"clocked_on\s*:\s*\"([^\"]+)\"", ff_body)
            clear_match = re.search(r"clear\s*:\s*\"([^\"]+)\"", ff_body)
            preset_match = re.search(r"preset\s*:\s*\"([^\"]+)\"", ff_body)
            next_state = next_match.group(1).strip() if next_match else ""
            clocked_on = clock_match.group(1).strip() if clock_match else ""
            clear = clear_match.group(1).strip() if clear_match else ""
            preset = preset_match.group(1).strip() if preset_match else ""
        latch = re.search(r"\blatch\s*\([^)]*\)\s*\{(.*?)\}", block, re.S)
        if latch:
            sequential_kind = "latch"
            latch_body = latch.group(1)
            latch_header = re.search(r"\blatch\s*\(([^)]*)\)", block, re.S)
            latch_vars = [v.strip().strip('"') for v in (
                latch_header.group(1) if latch_header else ""
            ).split(",") if v.strip()]
            state_var = latch_vars[0] if latch_vars else ""
            state_inv_var = latch_vars[1] if len(latch_vars) > 1 else ""
            next_match = re.search(r"next_state\s*:\s*\"([^\"]+)\"", latch_body)
            enable_match = re.search(r"enable\s*:\s*\"([^\"]+)\"", latch_body)
            next_state = next_match.group(1).strip() if next_match else ""
            latch_enable = enable_match.group(1).strip() if enable_match else ""
        cells[f"sky130_fd_sc_hd__{cell_name}"] = LibCell(
            name=f"sky130_fd_sc_hd__{cell_name}",
            family=family,
            size=size,
            output_pin=output_pin,
            function=function,
            input_pins=input_pins,
            next_state=next_state,
            clocked_on=clocked_on,
            latch_enable=latch_enable,
            clear=clear,
            preset=preset,
            state_var=state_var,
            state_inv_var=state_inv_var,
            output_functions=output_functions,
            sequential_kind=sequential_kind,
            three_state_functions=three_state_functions,
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


def _output_semantics(cell: LibCell):
    """Canonicalise data and Z conditions using one shared input-role map.

    Matching is syntactic and conservative.  In particular, data and enable
    expressions must share the same variable mapping across every output.
    """
    functions = cell.output_functions or {cell.output_pin: cell.function}
    if cell.output_pin not in functions or not set(cell.three_state_functions) <= set(functions):
        return None
    outputs = [cell.output_pin, *sorted(pin for pin in functions if pin != cell.output_pin)]
    variables: list[str] = []

    def expression(text):
        for variable in function_vars(text):
            if variable not in variables:
                variables.append(variable)
        roles = {variable: f"v{index}" for index, variable in enumerate(variables)}
        return re.sub(r"[A-Za-z_][A-Za-z0-9_]*", lambda match: roles[match.group()], text)

    signature = tuple(
        (expression(functions[pin]),
         expression(cell.three_state_functions[pin]) if pin in cell.three_state_functions else None)
        for pin in outputs
    )
    if cell.three_state_functions and (
        set(variables) != set(cell.input_pins)
        or len(cell.input_pins) != len(set(cell.input_pins))
        or set(outputs) & set(cell.input_pins)
    ):
        # Every enable/data role must be a real input and every required input
        # must survive the rewrite.  Missing enable metadata is not a tie-off.
        return None
    return signature, variables, outputs


def _has_state_semantics(cell: LibCell) -> bool:
    """Recognize parsed state groups and older/partial sequential metadata."""
    return any((cell.sequential_kind, cell.next_state, cell.clocked_on,
                cell.latch_enable, cell.clear, cell.preset,
                cell.state_var, cell.state_inv_var))


def equivalence_candidates(
    cell: LibCell, lib: dict[str, LibCell]
) -> list[tuple[str, dict[str, str]]]:
    """Return ``(new_type, pin_map)`` for equivalent combinational cells.

    ``pin_map`` maps the *source* cell's pin names to the candidate's pin
    names (e.g. ``{"A": "A", "SLEEP": "B"}`` for inputiso1p -> or2).  The
    Data and high-impedance conditions share one pin map; all enable inputs
    must survive a tristate rewrite.  The source cell itself and cells with
    no function are excluded. Sequential sources and targets are excluded;
    same-family sequential sizing belongs to strategy G, not this matcher.
    """
    if _has_state_semantics(cell) or not cell.function:
        return []
    source = _output_semantics(cell)
    if source is None:
        return []
    src_canon, src_vars, src_outputs = source
    out: list[tuple[str, dict[str, str]]] = []
    for other in lib.values():
        if other.name == cell.name or _has_state_semantics(other) or not other.function:
            continue
        target = _output_semantics(other)
        if target is None:
            continue
        other_canon, other_vars, other_outputs = target
        if other_canon != src_canon:
            continue
        pin_map = {sv: ov for sv, ov in zip(src_vars, other_vars)}
        for source_pin, target_pin in zip(src_outputs, other_outputs):
            if source_pin and target_pin and source_pin != target_pin:
                pin_map[source_pin] = target_pin
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
