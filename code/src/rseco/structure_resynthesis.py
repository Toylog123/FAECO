"""L3: S — window-local structure resynthesis candidates (r2 tech design §4-§5).

The dangerous failure mode this module is built around is *not* ABC itself but
window grafting: a window that passes local CEC can still be grafted onto the
wrong host net.  Every interface below is therefore pure text-in / text-out
(except explicit IO paths), deterministic, and validated by

  * invariant checks at extraction (no sequential / clock / gating cell …),
  * a forced full-host-netlist ``structure_check`` AFTER graft and BEFORE STA,
  * a strict graft contract (boundary host nets byte-identical, internal names
    namespaced, no collisions with the host, idempotency enforced).

The state machine is r2 §5.3:

    EXTRACT → EMIT → RESYNTH(S0/S1/S2) → CEC_PRE → TECHMAP → CEC_POST
            → RATIO → DEDUP → GRAFT → STRUCT → EMIT_CANDIDATE

Tool steps (ABC variants, techmap, CEC) are injectable via :class:`ResynthTools`
so the whole machine is unit-testable without Yosys/ABC on the host.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .cut import CutBoundary
from .gate_sizing import Cell, parse_mapped_netlist
from .netlist_audit import find_multi_driver_nets
from .yosys_abc import RESYN2_BUILTIN_SEQUENCE

# --------------------------------------------------------------------------
# r2 §4.3 — the three frozen variants.  No other ABC recipe is added.
# --------------------------------------------------------------------------
VARIANTS: dict[str, tuple[str, ...]] = {
    "S0": tuple(RESYN2_BUILTIN_SEQUENCE),
    "S1": (*RESYN2_BUILTIN_SEQUENCE, "resub"),
    "S2": (*RESYN2_BUILTIN_SEQUENCE, "resub -z"),
}

# r2 §4.4
R_SOFT = 1.20
R_HARD = 1.50

# r2 §4.7 rejection attribution labels (only CEC-1 failure and F3-S count
# into F1/F3 respectively; everything else is a window-level rejection).
LABEL_EXTRACT_INVARIANT = "W_EXTRACT_INVARIANT"
LABEL_ABC_ERR = "W_ABC_ERR"
LABEL_ABC_TIMEOUT = "W_ABC_TIMEOUT"
LABEL_F1_CEC_PRE = "F1"
LABEL_LIB_OUT_OF_SET = "W_LIB_OUT_OF_SET"
LABEL_CEC_POST = "S_TECHMAP_MISMATCH"
LABEL_F3S = "F3-S"
LABEL_GRAFT_ERROR = "W_GRAFT_ERROR"
LABEL_STRUCT_ERROR = "W_STRUCT_ERROR"
LABEL_DEDUP = "DROPPED"
LABEL_OK = "ok"

# Cells that must never enter a window (r2 §4.2): sequential, clock/reset/
# gating, and non-logic physical cells.
_FORBIDDEN_FUNCTION_PREFIXES = (
    "df", "sdf", "edfx", "dlx", "dlclkp",       # sequential
    "clkbuf", "clkinv", "clkdlybuf", "clkgat",  # clock
    "einvp", "ebufn", "einvn", "ebufp",         # tri-state enable / gating
    "tap", "conb", "decap", "fill", "diode", "antenna",
)
_CONSTANT_NETS = {"1'b0", "1'b1", "0", "1", "VPWR", "VGND", "VDD", "VSS"}


def _is_forbidden(function: str) -> bool:
    return function.startswith(_FORBIDDEN_FUNCTION_PREFIXES)


# --------------------------------------------------------------------------
# r2 §5.1 — data structures
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class WindowPort:
    host_net: str        # host net name — byte-identical before/after graft
    module_name: str     # deterministic port name inside the window module
    direction: str       # "in" | "out"
    known_constant: bool = False


@dataclass(frozen=True)
class WindowCell:
    instance: str
    cell_type: str
    connections: dict[str, str]   # pin -> net (host side names)
    is_sequential: bool = False   # invariant: always False inside a window


@dataclass(frozen=True)
class WindowSpec:
    window_id: str
    root: str
    ports_in: list[WindowPort]
    ports_out: list[WindowPort]
    cells: list[WindowCell]
    host_to_module: dict[str, str]
    module_to_host: dict[str, str]
    n_window_combo_cells: int
    source_cut_method: str
    source_cone: str
    extraction_report: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "window_id": self.window_id,
            "root": self.root,
            "ports_in": [p.__dict__ for p in self.ports_in],
            "ports_out": [p.__dict__ for p in self.ports_out],
            "cells": [{"instance": c.instance, "cell_type": c.cell_type,
                       "connections": dict(c.connections),
                       "is_sequential": c.is_sequential} for c in self.cells],
            "host_to_module": dict(self.host_to_module),
            "module_to_host": dict(self.module_to_host),
            "n_window_combo_cells": self.n_window_combo_cells,
            "source_cut_method": self.source_cut_method,
            "source_cone": self.source_cone,
            "extraction_report": dict(self.extraction_report),
        }


@dataclass(frozen=True)
class GraftPlan:
    window_id: str
    remove_instances: list[str]
    insert_cells: list[WindowCell]
    namespace_prefix: str
    keep_host_nets: list[str]

    def to_dict(self) -> dict:
        return {
            "window_id": self.window_id,
            "remove_instances": list(self.remove_instances),
            "insert_cells": [c.instance for c in self.insert_cells],
            "namespace_prefix": self.namespace_prefix,
            "keep_host_nets": list(self.keep_host_nets),
        }


@dataclass(frozen=True)
class VariantResult:
    variant: str
    status: str                  # "ok" | "error" | "timeout"
    reason: str = ""
    window_blif: str | None = None
    abc_sequence: str = ""
    aig_nodes_before: int = 0
    aig_nodes_after: int = 0
    depth_before: int = 0
    depth_after: int = 0
    depth_before_sky130: int | None = None   # window depth in the SKY130 layer
    window_gates_after: int = 0

    @property
    def ok(self) -> bool:
        return self.status == "ok"


@dataclass(frozen=True)
class CecResult:
    status: str          # "pass" | "fail" | "unavailable" | "timeout"
    reason: str = ""
    log_path: str | None = None


@dataclass(frozen=True)
class RatioVerdict:
    ratio: float | None
    verdict: str         # "ok" | "soft" | "f3s"
    n_window: int
    n_patch: int
    label: str


@dataclass(frozen=True)
class StructureReport:
    ok: bool
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"ok": self.ok, "issues": list(self.issues)}


@dataclass(frozen=True)
class ResynthCandidate:
    """One accepted window resynthesis candidate (pre-STA)."""

    spec: WindowSpec
    variant: VariantResult
    verdict: RatioVerdict
    grafted_text: str
    resynth_stats: dict
    canonical_hash: str
    soft_penalty: bool


# --------------------------------------------------------------------------
# deterministic identity helpers (r2 §5.2)
# --------------------------------------------------------------------------
_WINDOW_ID_RE = re.compile(r"^[0-9a-f]{16}$")


def window_id(root: str, gates: list[str]) -> str:
    seed = root + "|" + "|".join(sorted(gates))
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def canonical_netlist_hash(text: str) -> str:
    """Whitespace/comment-insensitive hash used for cross-variant dedup."""
    stripped = re.sub(r"//[^\n]*", "", text)
    tokens = re.findall(r"[\w.$'\[\]]+", stripped)
    return hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# EXTRACT (r2 §5.4) — invariants per r2 §4.2
# --------------------------------------------------------------------------
# ``gate_sizing.parse_mapped_netlist`` only matches ``sky130_fd_sc_hd__*``
# instances.  The FAECO host netlists additionally instantiate flops through a
# local ``dff`` wrapper module (``module dff(CK, Q, D)`` wrapping a single
# ``sky130_fd_sc_hd__dfxtp_1``).  Skipping those instances would (a) drop a
# window output that feeds a flop and (b) report every flop-driven net as
# dangling.  The permissive parser below recovers them.
_HOST_INSTANCE_RE = re.compile(
    r"(?m)^[ \t]*([A-Za-z_][\w$]*)[ \t]+([A-Za-z_][\w$]*)[ \t]*\((.*?)\)[ \t]*;",
    re.S,
)
_HOST_PIN_RE = re.compile(r"\.\s*([A-Za-z_]\w*)\s*\(\s*([^)]*?)\s*\)")
_HOST_NON_CELL_KEYWORDS = frozenset({
    "module", "endmodule", "input", "output", "inout", "wire", "reg", "logic",
    "assign", "always", "always_ff", "always_comb", "initial", "function",
    "endfunction", "task", "endtask", "generate", "endgenerate", "parameter",
    "localparam", "defparam", "genvar", "integer", "real", "time", "tri",
    "supply0", "supply1", "if", "else", "case", "endcase", "for", "while",
    "begin", "end", "specify", "endspecify", "primitive", "endprimitive",
})
# Wrapper modules mapped to the primitive they wrap, so purity checks
# (``_is_forbidden``) and ``Cell.is_dff`` see through the wrapper.
_WRAPPER_FUNCTION = {"dff": "dfxtp", "dffn": "dfxtp"}


def _parse_wrapper_cells(netlist_text: str,
                         known: set[str]) -> list[Cell]:
    """Parse cell instances the SKY130-only parser skipped (e.g. ``dff``)."""
    extras: list[Cell] = []
    for match in _HOST_INSTANCE_RE.finditer(netlist_text):
        cell_type, instance, body = match.group(1), match.group(2), match.group(3)
        if cell_type in _HOST_NON_CELL_KEYWORDS:
            continue
        if instance in known:
            continue
        pins = {pin: net for pin, net in _HOST_PIN_RE.findall(body) if net}
        if not pins:
            continue
        function = _WRAPPER_FUNCTION.get(cell_type.lower(), cell_type.lower())
        extras.append(Cell(instance=instance, cell_type=cell_type,
                           function=function, size=1, pins=pins))
    return extras


def host_cells(netlist_text: str) -> dict[str, Cell]:
    """All host cell instances, SKY130-mapped and wrapper cells alike."""
    cells = {c.instance: c for c in parse_mapped_netlist(netlist_text)}
    for extra in _parse_wrapper_cells(netlist_text, set(cells)):
        cells[extra.instance] = extra
    return cells


def extract_window(netlist_text: str, boundary: CutBoundary) -> WindowSpec | None:
    """Build a :class:`WindowSpec` from the mapped host netlist + cut boundary.

    Returns ``None`` when any extraction invariant is violated (no partial
    window is ever produced — r2 §4.2 "任一违反 → 拒绝").
    """
    cells = host_cells(netlist_text)
    gate_names = sorted(dict.fromkeys(boundary.gates))
    if not gate_names:
        return None
    missing = [name for name in gate_names if name not in cells]
    if missing:
        return None
    window_cells = [cells[name] for name in gate_names]
    if any(_is_forbidden(c.function) for c in window_cells):
        return None

    driven_by_window = {pin_net for c in window_cells
                        for pin_net in _output_nets(c)}
    # Nets consumed by host cells outside the window.  A window-driven net that
    # is consumed outside MUST become a window output, otherwise grafting would
    # delete the only driver of a live host net (r2 §4.2 — the failure this
    # whole module exists to prevent).
    gate_name_set = set(gate_names)
    outside_sinks: set[str] = set()
    for inst, cell in cells.items():
        if inst in gate_name_set:
            continue
        outside_sinks |= _sink_nets(cell)
    # Host module ports (needed to decide if a window output leaves the window).
    host_ports = _module_ports(netlist_text)

    # boundary output nets must all be produced inside the window
    if not set(boundary.boundary_outputs) <= driven_by_window:
        return None

    port_in_nets: list[str] = []
    for cell in window_cells:
        for pin, net in sorted(cell.pins.items()):
            if net in _CONSTANT_NETS:
                continue
            if net in driven_by_window:
                continue
            if net in port_in_nets:
                continue
            port_in_nets.append(net)
    port_out_nets: list[str] = []
    for net in sorted(driven_by_window):
        if net in outside_sinks or net in host_ports:
            port_out_nets.append(net)
    # every boundary output must be a window output port
    for net in boundary.boundary_outputs:
        if net not in port_out_nets:
            port_out_nets.append(net)
    port_out_nets = sorted(dict.fromkeys(port_out_nets))
    if not port_out_nets:
        return None
    # Caller-contract audit: a window-driven net that leaves the window but was
    # not declared as a boundary output means the supplied cut boundary was
    # incomplete.  It is repaired here (so no host net loses its driver) and
    # recorded, rather than silently inherited.
    leaving = {net for net in driven_by_window
               if net in outside_sinks or net in host_ports}
    boundary_outputs_extended = sorted(leaving - set(boundary.boundary_outputs))

    # deterministic module names: w_<increasing index>, no reuse of host names
    host_to_module: dict[str, str] = {}
    module_to_host: dict[str, str] = {}
    ports_in: list[WindowPort] = []
    ports_out: list[WindowPort] = []
    index = 0
    for net in port_in_nets:
        index += 1
        name = f"w_{index}"
        host_to_module[net] = name
        module_to_host[name] = net
        ports_in.append(WindowPort(host_net=net, module_name=name,
                                   direction="in",
                                   known_constant=False))
    for net in port_out_nets:
        index += 1
        name = f"w_{index}"
        host_to_module[net] = name
        module_to_host[name] = net
        ports_out.append(WindowPort(host_net=net, module_name=name,
                                    direction="out",
                                    known_constant=False))
    # constant nets feeding the window become explicit constant input ports
    constants = sorted({net for c in window_cells
                        for net in c.pins.values() if net in _CONSTANT_NETS})
    for net in constants:
        index += 1
        name = f"w_{index}"
        host_to_module[net] = name
        module_to_host[name] = net
        ports_in.append(WindowPort(host_net=net, module_name=name,
                                   direction="in", known_constant=True))

    spec_cells = [
        WindowCell(instance=c.instance, cell_type=c.cell_type,
                   connections=dict(sorted(c.pins.items())),
                   is_sequential=bool(c.is_dff))
        for c in window_cells
    ]
    root = boundary.boundary_outputs[0]
    spec = WindowSpec(
        window_id=window_id(root, gate_names),
        root=root,
        ports_in=ports_in,
        ports_out=ports_out,
        cells=spec_cells,
        host_to_module=host_to_module,
        module_to_host=module_to_host,
        n_window_combo_cells=len(spec_cells),  # r2 §4.4: combo std cells only
        source_cut_method=boundary.method,
        source_cone=str(getattr(boundary, "source_cone", "") or ""),
        extraction_report={
            "no_sequential_cell": not any(c.is_sequential for c in spec_cells),
            "no_forbidden_cell": not any(_is_forbidden(c.function)
                                         for c in window_cells),
            "no_dangling_output": bool(port_out_nets),
            "boundary_outputs_covered":
                set(boundary.boundary_outputs) <= set(port_out_nets),
            "boundary_outputs_extended": boundary_outputs_extended,
            "n_ports_in": len(ports_in),
            "n_ports_out": len(ports_out),
        },
    )
    return spec


def _output_nets(cell: Cell) -> set[str]:
    """Nets driven by a mapped cell (all pins that are not inputs)."""
    return {net for pin, net in cell.pins.items() if _is_driver_pin(pin)}


def _sink_nets(cell: Cell) -> set[str]:
    """Nets consumed by a mapped cell (all pins that are not drivers)."""
    return {net for pin, net in cell.pins.items() if not _is_driver_pin(pin)}


def _is_driver_pin(pin: str) -> bool:
    from .netlist_audit import OUTPUT_PINS
    return pin in OUTPUT_PINS or pin in _DRIVER_PINS


def _module_ports(netlist_text: str) -> set[str]:
    ports: set[str] = set()
    for match in re.finditer(r"\b(?:input|output|inout)\b([^;]*);", netlist_text):
        for token in re.split(r"[,\s]+", match.group(1)):
            token = token.strip()
            if token:
                ports.add(token)
    return ports


# --------------------------------------------------------------------------
# EMIT (r2 §5.4) — window.v
# --------------------------------------------------------------------------
def render_window_verilog(spec: WindowSpec, *, module_name: str | None = None) -> str:
    module = module_name or f"win_{spec.window_id}"
    inputs = [p.module_name for p in spec.ports_in]
    outputs = [p.module_name for p in spec.ports_out]
    lines = [f"module {module}({', '.join(inputs + outputs)});"]
    if inputs:
        lines.append("  input " + ", ".join(inputs) + ";")
    if outputs:
        lines.append("  output " + ", ".join(outputs) + ";")
    for cell in spec.cells:
        conns = []
        for pin, net in sorted(cell.connections.items()):
            conns.append(f".{pin}({spec.host_to_module.get(net, net)})")
        lines.append(f"  {cell.cell_type} {cell.instance} ({', '.join(conns)});")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def emit_window_verilog(spec: WindowSpec, out_dir: str | Path,
                        *, module_name: str | None = None) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "window.v"
    path.write_text(render_window_verilog(spec, module_name=module_name),
                    encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# RATIO (r2 §4.4) — window-local double threshold
# --------------------------------------------------------------------------
def ratio_check(spec: WindowSpec, n_patch: int) -> RatioVerdict:
    n_window = int(spec.n_window_combo_cells)
    if n_window <= 0:
        return RatioVerdict(ratio=None, verdict="f3s", n_window=n_window,
                            n_patch=int(n_patch), label=LABEL_F3S)
    ratio = n_patch / n_window
    if ratio <= R_SOFT:
        verdict, label = "ok", LABEL_OK
    elif ratio <= R_HARD:
        verdict, label = "soft", LABEL_OK
    else:
        verdict, label = "f3s", LABEL_F3S
    return RatioVerdict(ratio=ratio, verdict=verdict, n_window=n_window,
                        n_patch=int(n_patch), label=label)


# --------------------------------------------------------------------------
# GRAFT (r2 §5.2/§5.4) — the step that must never silently mis-wire
# --------------------------------------------------------------------------
_INSTANCE_LINE_RE = re.compile(
    r"(?ms)^[ \t]*sky130_fd_sc_hd__\w+[ \t]+(?P<inst>\w+)[ \t]*\([^;]*\)[ \t]*;")


def graft(netlist_text: str, spec: WindowSpec, plan: GraftPlan,
          *, mapped_window_text: str | None = None) -> str:
    """Stitch the resynthesized window back into the host netlist.

    ``mapped_window_text`` is the mapped (SKY130) window netlist; when it is
    ``None`` the plan's own ``insert_cells`` are used (used by tests and by the
    degenerate "identity" case).  Raises ``ValueError`` on any violation —
    never best-effort.
    """
    if plan.window_id != spec.window_id:
        raise ValueError("graft plan / window spec id mismatch")
    if plan.namespace_prefix and plan.namespace_prefix in netlist_text:
        # r2 §5.5: a pre-existing prefix means a collision would silently
        # overwrite — fail closed instead.
        raise ValueError("namespace prefix already present in host netlist")
    host_cells = {c.instance for c in parse_mapped_netlist(netlist_text)}
    for inst in plan.remove_instances:
        if inst not in host_cells:
            raise ValueError(f"cannot remove missing instance: {inst}")

    insert_cells: list[WindowCell]
    if mapped_window_text is not None:
        insert_cells = _mapped_cells_to_host(spec, plan, mapped_window_text)
    else:
        insert_cells = list(plan.insert_cells)

    out = netlist_text
    for inst in plan.remove_instances:
        pattern = re.compile(
            r"(?ms)^[ \t]*sky130_fd_sc_hd__\w+[ \t]+" + re.escape(inst)
            + r"[ \t]*\([^;]*\)[ \t]*;([ \t]*\n)?")
        out, count = pattern.subn("", out, count=1)
        if count != 1:
            raise ValueError(f"could not remove instance {inst}")
    rendered = "\n".join(_render_host_cell(c) for c in insert_cells) + "\n"
    # insert before the host module's endmodule (deterministic anchor)
    anchor = out.rfind("endmodule")
    if anchor < 0:
        raise ValueError("host netlist has no endmodule")
    out = out[:anchor] + rendered + out[anchor:]
    return out


def _render_host_cell(cell: WindowCell) -> str:
    conns = ", ".join(f".{pin}({net})"
                      for pin, net in sorted(cell.connections.items()))
    return f"  {cell.cell_type} {cell.instance} ({conns});"


def _mapped_cells_to_host(spec: WindowSpec, plan: GraftPlan,
                          mapped_window_text: str) -> list[WindowCell]:
    """Rename mapped window cells into host namespace (r2 §5.2 rules)."""
    module_ports = set(spec.module_to_host)
    cells = parse_mapped_netlist(mapped_window_text)
    if not cells:
        raise ValueError("mapped window has no cells")
    seen_instances: set[str] = set()
    out: list[WindowCell] = []
    for cell in cells:
        # window top-level module name appears as the instance of nothing;
        # yosys emits the top module's cells directly, ports are module IO
        instance = plan.namespace_prefix + cell.instance
        if instance in seen_instances:
            raise ValueError(f"duplicate inserted instance: {instance}")
        seen_instances.add(instance)
        conns: dict[str, str] = {}
        for pin, net in sorted(cell.pins.items()):
            if net in module_ports:
                conns[pin] = spec.module_to_host[net]      # boundary: host net
            elif net in _CONSTANT_NETS:
                conns[pin] = net
            else:
                conns[pin] = plan.namespace_prefix + net   # internal: namespaced
        out.append(WindowCell(instance=instance, cell_type=cell.cell_type,
                              connections=conns, is_sequential=bool(cell.is_dff)))
    return out


def build_graft_plan(spec: WindowSpec, mapped_window_text: str) -> GraftPlan:
    """Deterministic graft plan for a resynthesized window (r2 §5.2)."""
    mapped_cells = parse_mapped_netlist(mapped_window_text)
    return GraftPlan(
        window_id=spec.window_id,
        remove_instances=sorted(c.instance for c in spec.cells),
        insert_cells=[],
        namespace_prefix=f"rs_{spec.window_id}_",
        keep_host_nets=sorted({p.host_net for p in spec.ports_in + spec.ports_out}),
    )


# --------------------------------------------------------------------------
# STRUCT CHECK (r2 §5.3 hard constraint #2) — on the FULL host netlist
# --------------------------------------------------------------------------
def structure_check(grafted_text: str, *,
                    baseline_text: str | None = None) -> StructureReport:
    """Full-netlist structural self-check run after graft, before STA.

    Catches exactly the "local CEC passes but the graft lands on the wrong
    net" failure: dangling inputs (a net that no cell/PI/constant drives) and
    undriven module outputs, plus multi-driver nets from the shared audit.

    ``baseline_text`` (the pre-graft host netlist) is subtracted: the gate is
    about defects the GRAFT introduced, so pre-existing host properties
    (hierarchical clock nets, tie nets, …) must not produce false positives.
    """
    issues = _structure_issues(grafted_text)
    if baseline_text is not None:
        issues -= _structure_issues(baseline_text)
    return StructureReport(ok=not issues, issues=sorted(issues))


def _structure_issues(text: str) -> set[str]:
    issues: set[str] = set()
    for net, drivers in find_multi_driver_nets(text).items():
        issues.add(f"multi_driver:{net}:{len(drivers)}")
    cells = host_cells(text)
    driven: set[str] = set()
    for cell in cells.values():
        for pin, net in cell.pins.items():
            if pin in _DRIVER_PINS:
                driven.add(net)
    ports = _module_ports(text)
    for cell in cells.values():
        for pin, net in cell.pins.items():
            if pin in _DRIVER_PINS or net in _CONSTANT_NETS:
                continue
            if net in ports or net in driven:
                continue
            issues.add(f"dangling_input:{cell.instance}.{pin}:{net}")
    return issues


_DRIVER_PINS = {"X", "Y", "Z", "Q", "Q_N", "COUT", "SUM", "HI", "LO", "GCLK"}


# --------------------------------------------------------------------------
# STATE MACHINE (r2 §5.3) with injectable tool steps
# --------------------------------------------------------------------------
@dataclass
class ResynthTools:
    """Injectable tool steps; the defaults bind the real Yosys/ABC wrappers.

    ``run_variant(spec, variant, out_dir) -> VariantResult``
    ``techmap(window_v, out_dir) -> Path | None``
    ``cec(reference, candidate, out_dir) -> CecResult``
    """

    run_variant: "object"
    techmap: "object"
    cec: "object"
    # optional: (mapped_window_v) -> max SKY130 level (r2 §4.8 second layer)
    sky130_level: "object" = None


@dataclass
class ResynthOutcome:
    candidates: list[ResynthCandidate] = field(default_factory=list)
    rejections: list[dict] = field(default_factory=list)      # label + variant
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "n_candidates": len(self.candidates),
            "rejections": list(self.rejections),
            "stats": dict(self.stats),
            "candidates": [
                {
                    "window_id": c.spec.window_id,
                    "variant": c.variant.variant,
                    "canonical_hash": c.canonical_hash,
                    "soft_penalty": c.soft_penalty,
                    "resynth_stats": dict(c.resynth_stats),
                }
                for c in self.candidates
            ],
        }


def run_structure_resynthesis(
    netlist_text: str,
    boundary: CutBoundary,
    out_dir: str | Path,
    *,
    tools: ResynthTools,
    variants: tuple[str, ...] = ("S0", "S1", "S2"),
    dedup_seen: set[str] | None = None,
    soft_penalty_hook: bool = True,
) -> ResynthOutcome:
    """Run the r2 §5.3 state machine for one cut boundary.

    The returned candidates carry the grafted host text; STA is the caller's
    job (this module stops at EMIT_CANDIDATE, exactly as the state machine
    specifies — ``STRUCT`` must pass first).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seen = dedup_seen if dedup_seen is not None else set()
    outcome = ResynthOutcome()

    # EXTRACT
    spec = extract_window(netlist_text, boundary)
    if spec is None:
        outcome.rejections.append({"label": LABEL_EXTRACT_INVARIANT,
                                   "variant": None})
        return outcome
    # EMIT
    window_v = emit_window_verilog(spec, out_dir)

    for variant in variants:
        if variant not in VARIANTS:
            raise ValueError(f"unknown variant: {variant}")
        label, candidate = _run_one_variant(
            spec=spec, variant=variant, netlist_text=netlist_text,
            window_v=window_v, out_dir=out_dir, tools=tools, seen=seen,
            soft_penalty_hook=soft_penalty_hook, outcome=outcome)
        if candidate is not None:
            outcome.candidates.append(candidate)
            seen.add(candidate.canonical_hash)
        elif label is not None:
            outcome.rejections.append({"label": label, "variant": variant})

    outcome.stats = {
        "window_id": spec.window_id,
        "n_window_combo_cells": spec.n_window_combo_cells,
        "variants_run": list(variants),
        "n_candidates": len(outcome.candidates),
    }
    return outcome


def _run_one_variant(*, spec: WindowSpec, variant: str, netlist_text: str,
                     window_v: Path, out_dir: Path, tools: ResynthTools,
                     seen: set[str], soft_penalty_hook: bool,
                     outcome: ResynthOutcome) -> tuple[str | None, object | None]:
    variant_dir = out_dir / variant
    variant_dir.mkdir(parents=True, exist_ok=True)

    # RESYNTH
    result = tools.run_variant(spec, variant, variant_dir)
    if result is None:
        return LABEL_ABC_ERR, None
    if result.status == "timeout":
        return LABEL_ABC_TIMEOUT, None
    if not result.ok or not result.window_blif:
        return LABEL_ABC_ERR, None

    # CEC_PRE (must precede TECHMAP so pre-pass/post-fail is cleanly
    # attributable to S_TECHMAP_MISMATCH — r2 §5.3 hard constraint #1)
    pre = tools.cec(window_v, Path(result.window_blif), variant_dir)
    if pre.status != "pass":
        return LABEL_F1_CEC_PRE, None

    # TECHMAP
    mapped_v = tools.techmap(Path(result.window_blif), variant_dir)
    if mapped_v is None or not Path(mapped_v).exists():
        return LABEL_LIB_OUT_OF_SET, None
    mapped_text = Path(mapped_v).read_text(encoding="utf-8")

    # CEC_POST — original ≡ mapped (whole resynthesis+mapping chain)
    post = tools.cec(window_v, Path(mapped_v), variant_dir)
    if post.status != "pass":
        return LABEL_CEC_POST, None

    # RATIO
    n_patch = len(parse_mapped_netlist(mapped_text))
    verdict = ratio_check(spec, n_patch)
    if verdict.verdict == "f3s":
        return LABEL_F3S, None

    # DEDUP (before graft — avoids useless graft+STA on duplicates)
    canonical = canonical_netlist_hash(mapped_text)
    if canonical in seen:
        return None, None  # dropped, not a failure (r2 §4.7)
    if not canonical_netlist_hash(mapped_text):
        return LABEL_ABC_ERR, None

    # GRAFT
    try:
        plan = build_graft_plan(spec, mapped_text)
        grafted = graft(netlist_text, spec, plan,
                        mapped_window_text=mapped_text)
    except ValueError:
        return LABEL_GRAFT_ERROR, None

    # STRUCT (full host netlist, mandatory before STA); baseline-subtracted so
    # only graft-introduced defects (e.g. a mis-wired boundary) can reject
    report = structure_check(grafted, baseline_text=netlist_text)
    if not report.ok:
        return LABEL_STRUCT_ERROR, None

    depth_after_sky130 = None
    if getattr(tools, "sky130_level", None) is not None:
        try:
            depth_after_sky130 = tools.sky130_level(Path(mapped_v))
        except Exception:
            depth_after_sky130 = None
    stats = {
        "variant": variant,
        "window_gates_before": spec.n_window_combo_cells,
        "window_gates_after": n_patch,
        "aig_nodes_before": result.aig_nodes_before,
        "aig_nodes_after": result.aig_nodes_after,
        "depth_before": result.depth_before,
        "depth_after": result.depth_after,
        # r2 §4.8: both layers kept; SKY130 is authoritative when they differ
        "depth_before_sky130": result.depth_before_sky130,
        "depth_after_sky130": depth_after_sky130,
        "depth_layer": ("sky130" if depth_after_sky130 is not None
                        else "blif"),
        "abc_sequence": result.abc_sequence or " ; ".join(VARIANTS[variant]),
        "cec_pre_map": "pass",
        "cec_post_map": "pass",
        "area_before_um2": None,
        "area_after_um2": None,
        "canonical_hash": canonical,
        "r_s": verdict.ratio,
        "r_s_verdict": verdict.verdict,
    }
    return None, ResynthCandidate(
        spec=spec, variant=result, verdict=verdict, grafted_text=grafted,
        resynth_stats=stats, canonical_hash=canonical,
        soft_penalty=bool(soft_penalty_hook and verdict.verdict == "soft"),
    )


# --------------------------------------------------------------------------
# Real tool binding (r2 §5.4) — Yosys normalisation + ABC variants + techmap
# --------------------------------------------------------------------------
_BLIF_TOP_RE = re.compile(r"^\s*\.model\s+(\S+)", re.M)
_VERILOG_MODULE_RE = re.compile(r"^\s*module\s+([A-Za-z_]\w*)", re.M)
_LTP_LEN_RE = re.compile(r"length\s*=\s*(\d+)")
# ABC ``print_stats`` rows.  A freshly read BLIF reports ``nd = N`` (nodes)
# while a strashed network reports ``and = N``; both carry ``lev = N``.
_ABC_LEV_RE = re.compile(r"\blev\s*=\s*(\d+)")
_ABC_NODES_RE = re.compile(r"\b(?:and|nd)\s*=\s*(\d+)")


def blif_or_verilog_top(src: Path) -> str | None:
    """Best-effort top-module name for a window Verilog or gate-level BLIF."""
    src = Path(src)
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    pattern = _BLIF_TOP_RE if src.suffix.lower() == ".blif" else _VERILOG_MODULE_RE
    match = pattern.search(text)
    return match.group(1) if match else None


def abc_stats_rows(stdout: str) -> list[dict[str, int]]:
    """Ordered ``{nodes, lev}`` rows from ABC ``print_stats`` output.

    ``yosys_abc._parse_abc_stats`` only recognises the strashed ``and =`` form,
    so the pre-optimisation row of a BLIF read (``nd =``) is silently dropped
    and the "before" depth is lost.  This variant accepts both.
    """
    rows: list[dict[str, int]] = []
    for line in stdout.splitlines():
        if "i/o" not in line:
            continue
        lev = _ABC_LEV_RE.search(line)
        if not lev:
            continue
        nodes = _ABC_NODES_RE.search(line)
        rows.append({"nodes": int(nodes.group(1)) if nodes else 0,
                     "lev": int(lev.group(1))})
    return rows


def _blif_top_model(blif_path: Path) -> str | None:
    match = _BLIF_TOP_RE.search(blif_path.read_text(encoding="utf-8",
                                                    errors="replace"))
    return match.group(1) if match else None


def _yosys_ltp_max_level(verilog_path: Path, *, yosys_argv: list[str],
                         timeout_s: float, out_dir: Path,
                         cells_v: Path | None = None,
                         top: str | None = None) -> int | None:
    """SKY130-layer window depth via ``ltp -noff`` (r2 §4.8 second layer).

    The extracted SKY130 cell models are behavioural ``assign`` bodies, so they
    must be read alongside the netlist and flattened: only then does ``ltp``
    measure depth *through* the cells (gate/arc level) rather than counting each
    cell as one level.  ``-q`` is deliberately not passed — it suppresses the
    ``length=N`` log line this function parses.

    ``top`` overrides the module-name heuristic; pass it for multi-module files
    (e.g. a netlist that still carries the ``dff`` wrapper definition).
    """
    import subprocess
    from .yosys_abc import _yosys_path, _is_wsl_argv
    wsl = _is_wsl_argv(yosys_argv)
    top = top or blif_or_verilog_top(verilog_path)
    commands = []
    if cells_v is not None:
        commands.append(f"read_verilog {_yosys_path(cells_v, wsl=wsl)}")
    commands += [
        f"read_verilog {_yosys_path(verilog_path, wsl=wsl)}",
        (f"hierarchy -check -top {top}" if top else "hierarchy -auto-top"),
        "proc", "flatten", "opt_clean", "ltp -noff",
    ]
    script = " ; ".join(commands)
    log = out_dir / "ltp.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run([*yosys_argv, "-p", script],
                                   check=False, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace",
                                   timeout=timeout_s)
    except Exception:
        return None
    text = f"{completed.stdout}\n{completed.stderr}"
    log.write_text(text, encoding="utf-8")
    levels = [int(m) for m in _LTP_LEN_RE.findall(text)]
    return max(levels) if levels else None


def default_resynth_tools(
    lib_path: str | Path,
    *,
    yosys_command: str = "yosys",
    abc_command: str = "yosys-abc",
    timeout_s: float = 60.0,
    cells_v: str | Path | None = None,
) -> ResynthTools:
    """Bind the r2 §5.4 interfaces to the real Yosys/ABC tool chain.

    ``cells_v`` is the extracted SKY130 cells model (assign-style) used to
    expand named-port Liberty-mapped netlists so ABC can read them; it
    defaults to ``data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v``
    (same model the CEC stages use).
    """
    import subprocess
    from . import yosys_abc as ya
    from .technology_mapping import _extract_liberty_cells

    lib_path = Path(lib_path)
    if cells_v is None:
        candidate = (Path(__file__).resolve().parents[3] / "data" / "raw"
                     / "benchmarks" / "raw" / "skywater_cells_models"
                     / "sky130_cells_v2.v")
        cells_v = candidate if candidate.exists() else None
    cells_v = Path(cells_v) if cells_v else None
    tools = ya._resolve_yosys_and_abc(yosys_command=yosys_command,
                                      abc_command=abc_command)
    if isinstance(tools, ya._UnavailableTools):
        reason = tools.reason

        def _unavailable(*_args, **_kwargs):
            return VariantResult(variant="?", status="error", reason=reason)

        return ResynthTools(run_variant=_unavailable,
                            techmap=lambda *_a, **_k: None,
                            cec=lambda *_a, **_k: CecResult(
                                status="unavailable", reason=reason))
    yosys_argv = tools.yosys_argv
    abc_argv = tools.abc_argv
    # ``_extract_liberty_cells`` returns the raw Liberty token, which for
    # ``cell ("NAME") {`` retains the double quotes.  Strip them locally so the
    # §4.7 library-membership check compares against real instance names; the
    # shared helper is left untouched to keep the validated mapping path
    # bit-identical.
    liberty_cells = {c.strip('"\'') for c in _extract_liberty_cells(lib_path)}

    def _normalize(src: Path, dst: Path, *, top: str | None = None) -> bool:
        result = ya._normalize_to_blif(src, dst, yosys_argv=yosys_argv,
                                       timeout_s=timeout_s, top_module=top,
                                       liberty_cells_v=cells_v)
        return result.returncode == 0 and dst.exists()

    def _normalize_any(src: Path, dst: Path) -> bool:
        """Normalize a Verilog OR an already-gate-level BLIF to BLIF.

        The CEC reference is always the window Verilog; the candidate is a
        BLIF pre-techmap (ABC output) and Verilog post-techmap (Yosys output),
        so both branches are needed.  The top module MUST be supplied: without
        ``hierarchy -check -top`` the ``flatten`` below is a no-op and the
        expanded SKY130 cell-model modules survive as extra BLIF roots, which
        makes ABC's miter computation fail ("different number of primary
        inputs") and the CEC spuriously report failure.
        """
        src = Path(src)
        top = blif_or_verilog_top(src)
        if src.suffix.lower() == ".blif":
            from .yosys_abc import _yosys_path, _is_wsl_argv
            hierarchy = (f"hierarchy -check -top {top}" if top
                         else "hierarchy -auto-top")
            script = " ; ".join([
                f"read_blif {_yosys_path(src, wsl=_is_wsl_argv(yosys_argv))}",
                hierarchy,
                "flatten",
                "write_blif " f"{_yosys_path(dst, wsl=_is_wsl_argv(yosys_argv))}",
            ])
            try:
                completed = subprocess.run([*yosys_argv, "-q", "-p", script],
                                           check=False, capture_output=True,
                                           text=True, encoding="utf-8",
                                           errors="replace", timeout=timeout_s)
            except Exception:
                return False
            return completed.returncode == 0 and dst.exists()
        return _normalize(src, dst, top=top)

    def run_variant(spec: WindowSpec, variant: str, out_dir) -> VariantResult:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        module = f"win_{spec.window_id}"
        window_v = emit_window_verilog(spec, out_dir, module_name=module)
        blif = out_dir / "window.blif"
        if not _normalize(window_v, blif, top=module):
            return VariantResult(variant=variant, status="error",
                                 reason="yosys failed to normalize window")
        depth_before_sky130 = _yosys_ltp_max_level(window_v, yosys_argv=yosys_argv,
                                                   timeout_s=timeout_s,
                                                   out_dir=out_dir,
                                                   cells_v=cells_v)
        out_blif = out_dir / "win_abc.blif"
        sequence = " ; ".join(VARIANTS[variant])
        script = " ; ".join([
            f"read_blif {ya._abc_path(blif, wsl=ya._is_wsl_argv(abc_argv))}",
            "print_stats",
            "strash",
            *VARIANTS[variant],
            "print_stats",
            f"write_blif {ya._abc_path(out_blif, wsl=ya._is_wsl_argv(abc_argv))}",
        ])
        log_path = out_dir / "abc.log"
        try:
            completed = subprocess.run([*abc_argv, "-s", "-c", script],
                                       check=False, capture_output=True,
                                       text=True, encoding="utf-8",
                                       errors="replace", timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            ya._write_text_log(log_path, [*abc_argv, "-s", "-c", script],
                               exc.stdout or "", exc.stderr or "")
            return VariantResult(variant=variant, status="timeout",
                                 reason=f"ABC timed out after {timeout_s}s")
        ya._write_log(log_path, completed)
        if completed.returncode != 0 or not out_blif.exists():
            return VariantResult(variant=variant, status="error",
                                 reason=f"ABC failed rc={completed.returncode}")
        rows = abc_stats_rows(completed.stdout)
        before = rows[0] if rows else {"nodes": 0, "lev": 0}
        after = rows[-1] if rows else {"nodes": 0, "lev": 0}
        return VariantResult(
            variant=variant, status="ok", window_blif=str(out_blif),
            abc_sequence=sequence,
            aig_nodes_before=int(before["nodes"]),
            aig_nodes_after=int(after["nodes"]),
            depth_before=int(before["lev"]),
            depth_after=int(after["lev"]),
            depth_before_sky130=depth_before_sky130,
            window_gates_after=int(after.get("and", 0)),
        )

    def techmap(blif: Path, out_dir) -> Path | None:
        out_dir = Path(out_dir)
        blif = Path(blif)
        top = _blif_top_model(blif)
        if top is None:
            return None
        mapped_v = out_dir / "win_mapped.v"
        mapped_blif = out_dir / "win_mapped.blif"
        from .yosys_abc import _yosys_path, _is_wsl_argv
        script = " ; ".join([
            f"read_blif {_yosys_path(blif, wsl=_is_wsl_argv(yosys_argv))}",
            "hierarchy -auto-top",
            "proc",
            # ``read_blif`` yields ``$lut`` cells (BLIF ``.names`` is a LUT);
            # without ``techmap`` the ``abc`` extractor reports "0 gates /
            # nothing to map" and the design never reaches the cell library.
            "techmap",
            f"abc -liberty {_yosys_path(lib_path, wsl=_is_wsl_argv(yosys_argv))}",
            "clean",
            f"write_verilog -noattr {_yosys_path(mapped_v, wsl=_is_wsl_argv(yosys_argv))}",
            f"write_blif {_yosys_path(mapped_blif, wsl=_is_wsl_argv(yosys_argv))}",
        ])
        log_path = out_dir / "techmap.log"
        try:
            completed = subprocess.run([*yosys_argv, "-q", "-p", script],
                                       check=False, capture_output=True,
                                       text=True, encoding="utf-8",
                                       errors="replace", timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return None
        log_path.write_text(f"{completed.stdout}\n{completed.stderr}",
                            encoding="utf-8")
        if completed.returncode != 0 or not mapped_v.exists():
            return None
        # library membership check (r2 §4.7 W_LIB_OUT_OF_SET)
        mapped_text = mapped_v.read_text(encoding="utf-8", errors="replace")
        for cell_type in set(re.findall(r"(sky130_fd_sc_hd__\w+)", mapped_text)):
            if liberty_cells and cell_type not in liberty_cells:
                return None
        return mapped_v

    def cec(reference: Path, candidate: Path, out_dir) -> CecResult:
        out_dir = Path(out_dir)
        reference = Path(reference)
        candidate = Path(candidate)
        left = out_dir / "cec_left.blif"
        right = out_dir / "cec_right.blif"
        if not _normalize_any(reference, left) or not _normalize_any(candidate, right):
            return CecResult(status="unavailable",
                             reason="yosys failed to normalize a CEC side")
        output = ya._run_abc_cec(left, right, abc_argv=abc_argv,
                                 log_path=out_dir / "abc_cec.log",
                                 timeout_s=timeout_s)
        return CecResult(status=output.status,
                         reason="" if output.status == "pass"
                         else (output.stderr or "")[-200:],
                         log_path=str(out_dir / "abc_cec.log"))

    return ResynthTools(run_variant=run_variant, techmap=techmap, cec=cec,
                        sky130_level=lambda mapped_v: _yosys_ltp_max_level(
                            Path(mapped_v), yosys_argv=yosys_argv,
                            timeout_s=timeout_s,
                            out_dir=Path(mapped_v).parent,
                            cells_v=cells_v))
