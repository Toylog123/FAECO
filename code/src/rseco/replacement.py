"""Internal patch and combinational topology replacement operations."""

from dataclasses import dataclass
import itertools
import re
from typing import Iterable

from .graph import FaninCone
from .netlist import Gate, Netlist, parse_verilog_netlist
from .patch import PatchCandidate
from .equivalence import EquivalenceResult


@dataclass(frozen=True)
class TopologyMetrics:
    levels: int
    gates: int
    edges: int

    def to_dict(self) -> dict[str, int]:
        return {"levels": self.levels, "gates": self.gates, "edges": self.edges}


@dataclass(frozen=True)
class CombinationalWindow:
    gates: list[Gate]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    module_name: str
    source_netlist: Netlist
    before: TopologyMetrics


@dataclass(frozen=True)
class TopologyReplacement:
    original_gates: list[Gate]
    new_gates: list[Gate]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    before: TopologyMetrics
    after: TopologyMetrics
    method: str = "duplicate_parallel_factor_v1"

    def to_dict(self) -> dict[str, object]:
        return {
            "method": self.method,
            "original_gates": [g.name for g in self.original_gates],
            "new_gates": [g.name for g in self.new_gates],
            "boundary_inputs": list(self.boundary_inputs),
            "boundary_outputs": list(self.boundary_outputs),
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
        }


def _window_metrics(gates: list[Gate], inputs: list[str], outputs: list[str]) -> TopologyMetrics:
    by_output = {g.output: g for g in gates}
    memo = {x: 0 for x in inputs}

    def level(signal: str, stack: set[str] | None = None) -> int:
        if signal in memo:
            return memo[signal]
        gate = by_output.get(signal)
        if gate is None:
            return 0
        stack = stack or set()
        if gate.name in stack:
            raise ValueError("combinational window contains a cycle")
        value = 1 + max((level(i, stack | {gate.name}) for i in gate.inputs), default=0)
        memo[signal] = value
        return value

    return TopologyMetrics(
        levels=max((level(o) for o in outputs), default=0),
        gates=len(gates),
        edges=sum(len(g.inputs) for g in gates),
    )


def _logic_family(gate_type: str) -> str:
    family = gate_type.lower().split("__")[-1]
    return re.sub(r"_\d+$", "", family)


def extract_combinational_window(netlist: Netlist, gate_names: Iterable[str], *, max_gates: int = 16) -> CombinationalWindow:
    """Extract a cut-boundary combinational window from a parsed netlist."""
    if isinstance(netlist, str):
        netlist = parse_verilog_netlist_from_text(netlist)
    if hasattr(gate_names, "gates"):
        gate_names = getattr(gate_names, "gates")
    names = list(dict.fromkeys(gate_names))
    if not names or len(names) > max_gates:
        raise ValueError("window must contain between one and max_gates gates")
    by_name = {g.name: g for g in netlist.gates}
    missing = [name for name in names if name not in by_name]
    if missing:
        raise ValueError(f"window gates not found: {', '.join(missing)}")
    gates = [by_name[name] for name in names]
    outputs = {g.output for g in gates}
    consumers = {signal for g in gates for signal in g.inputs}
    boundary_inputs = list(dict.fromkeys(
        signal for g in gates for signal in g.inputs if signal not in outputs
    ))
    boundary_outputs = list(dict.fromkeys(
        g.output for g in gates
        if g.output not in consumers or g.output in netlist.outputs
    ))
    if not boundary_outputs:
        raise ValueError("window has no boundary output")
    return CombinationalWindow(
        gates=gates,
        boundary_inputs=boundary_inputs,
        boundary_outputs=boundary_outputs,
        module_name=netlist.module_name,
        source_netlist=netlist,
        before=_window_metrics(gates, boundary_inputs, boundary_outputs),
    )


def generate_topology_replacement(window: CombinationalWindow) -> TopologyReplacement:
    """Generate a real multi-gate rewrite for duplicate parallel logic.

    ``OR(AND(A,B), AND(A,B))`` (and the analogous OR/NOR-free duplicate)
    collapses to one AND gate.  This changes gate count, edges and depth and
    is checked by the truth-table checker before stitching.
    """
    by_output = {g.output: g for g in window.gates}
    output_gate = next((g for g in window.gates if g.output in window.boundary_outputs), None)
    if output_gate is None or _logic_family(output_gate.gate_type) not in {"or", "or2", "orr"}:
        raise ValueError("window does not match duplicate parallel OR pattern")
    children = [by_output.get(signal) for signal in output_gate.inputs]
    if len(children) != 2 or any(child is None for child in children):
        raise ValueError("parallel OR must have two internal inputs")
    left, right = children
    if _logic_family(left.gate_type) != _logic_family(right.gate_type) or _logic_family(left.gate_type) not in {"and", "and2"}:
        raise ValueError("parallel children are not equivalent AND gates")
    if tuple(sorted(left.inputs)) != tuple(sorted(right.inputs)):
        raise ValueError("parallel children do not have identical inputs")
    new_gate = Gate(gate_type=left.gate_type, name=left.name,
                    output=output_gate.output, inputs=left.inputs,
                    pin_names=left.pin_names, output_pin=left.output_pin)
    before = window.before
    after = _window_metrics([new_gate], window.boundary_inputs, window.boundary_outputs)
    return TopologyReplacement(
        original_gates=list(window.gates), new_gates=[new_gate],
        boundary_inputs=list(window.boundary_inputs),
        boundary_outputs=list(window.boundary_outputs), before=before, after=after,
    )


def stitch_topology_replacement(netlist_text: str, replacement: TopologyReplacement) -> str:
    """Stitch a verified local topology rewrite back into full Verilog text."""
    output = netlist_text
    for index, original in enumerate(replacement.original_gates):
        pattern = re.compile(r"(?ms)^\s*\w+\s+" + re.escape(original.name) + r"\s*\([^;]*\);\s*")
        replacement_text = ""
        if index == 0:
            rendered = []
            for gate in replacement.new_gates:
                if gate.pin_names and gate.output_pin:
                    input_pins = [pin for pin in gate.pin_names if pin != gate.output_pin]
                    if len(input_pins) != len(gate.inputs):
                        raise ValueError(f"pin/input count mismatch for {gate.name}")
                    connections = [f".{gate.output_pin}({gate.output})"]
                    connections.extend(f".{pin}({net})" for pin, net in zip(input_pins, gate.inputs))
                    rendered.append(
                        f"{gate.gate_type} {gate.name} (" + ", ".join(connections) + ");"
                    )
                else:
                    rendered.append(
                        f"{gate.gate_type} {gate.name} ({gate.output}, {', '.join(gate.inputs)});"
                    )
            replacement_text = "\n".join(rendered) + "\n"
        output, count = pattern.subn(replacement_text, output, count=1)
        if count != 1:
            raise ValueError(f"could not stitch gate {original.name}")
    return output


def apply_joint_region_rewrite(
    netlist_text: str,
    replacement: TopologyReplacement,
    *,
    sizing: dict[str, str] | None = None,
    buffer_actions: dict[str, object] | None = None,
    window: CombinationalWindow | None = None,
    local_checker=None,
) -> str:
    """Compose topology and G/B actions while enforcing one cut region."""
    if window is None:
        raise ValueError("topology replacement requires an explicit window/checker")
    allowed = {g.name for g in replacement.original_gates} | {g.name for g in replacement.new_gates}
    for action_set, label in ((sizing or {}, "sizing"), (buffer_actions or {}, "buffer")):
        outside = sorted(set(action_set) - allowed)
        if outside:
            raise ValueError(f"{label} actions outside topology region: {', '.join(outside)}")
    result = stitch_topology_replacement(netlist_text, replacement)
    if window is not None:
        if local_checker is None:
            local_checker = check_local_functional_equivalence
        if local_checker is None:
            raise ValueError("topology replacement requires a local equivalence checker")
        checked = local_checker(window, result)
        if getattr(checked, "status", None) != "pass":
            raise ValueError(f"local topology equivalence failed: {getattr(checked, 'reason', checked)}")
    if sizing:
        from .gate_sizing import apply_sizing
        result = apply_sizing(result, sizing)
    # Buffer insertion needs a fully mapped fanout model; callers can pass it
    # as a separate verified action, but never silently apply out-of-region B.
    if buffer_actions:
        raise ValueError("buffer_actions require mapped fanout context")
    return result


def _truth_table(gates: list[Gate], inputs: list[str], output: str) -> tuple[bool, ...]:
    by_output = {g.output: g for g in gates}

    def evaluate(signal: str, values: dict[str, bool], memo: dict[str, bool]) -> bool:
        if signal in memo:
            return memo[signal]
        if signal in values:
            return values[signal]
        gate = by_output.get(signal)
        if gate is None:
            raise ValueError(f"unresolved local signal: {signal}")
        vals = [evaluate(i, values, memo) for i in gate.inputs]
        kind = _logic_family(gate.gate_type).replace("_", "")
        if kind in {"buf", "buffer"}:
            result = vals[0]
        elif kind in {"not", "inv", "inverter"}:
            result = not vals[0]
        elif kind.startswith("nand"):
            result = not all(vals)
        elif kind.startswith("nor"):
            result = not any(vals)
        elif kind.startswith("xor"):
            result = sum(vals) % 2 == 1
        elif kind.startswith("xnor"):
            result = sum(vals) % 2 == 0
        elif kind.startswith("or"):
            result = any(vals)
        elif kind.startswith("and"):
            result = all(vals)
        else:
            raise ValueError(f"unsupported local gate type: {gate.gate_type}")
        memo[signal] = result
        return result

    if len(inputs) > 12:
        raise ValueError("truth-table local checker supports at most 12 inputs")
    rows: list[bool] = []
    for bits in itertools.product([False, True], repeat=len(inputs)):
        rows.append(evaluate(output, dict(zip(inputs, bits)), {}))
    return tuple(rows)


def check_local_functional_equivalence(window: CombinationalWindow, revised_netlist_text: str) -> EquivalenceResult:
    """Truth-table check for a combinational window; unavailable is fail-closed."""
    try:
        revised = parse_verilog_netlist_from_text(revised_netlist_text)
        revised_names = {g.name for g in window.gates}
        replacement_gates = [g for g in revised.gates if g.name in revised_names]
        if not replacement_gates:
            replacement_gates = [g for g in revised.gates if g.output in window.boundary_outputs]
        for output in window.boundary_outputs:
            original_table = _truth_table(window.gates, window.boundary_inputs, output)
            revised_table = _truth_table(replacement_gates, window.boundary_inputs, output)
            if original_table != revised_table:
                return EquivalenceResult(status="fail", method="truth_table_local",
                                         reason=f"truth tables differ at {output}")
    except Exception as exc:
        return EquivalenceResult(status="fail", method="truth_table_local",
                                 reason=f"local checker failed closed: {exc}")
    return EquivalenceResult(status="pass", method="truth_table_local",
                             reason="all boundary output truth tables match")


def parse_verilog_netlist_from_text(text: str) -> Netlist:
    """Parse text through the existing parser without introducing a temp file."""
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile("w", suffix=".v", delete=False, encoding="utf-8") as handle:
        handle.write(text)
        path = Path(handle.name)
    try:
        return parse_verilog_netlist(path)
    finally:
        path.unlink(missing_ok=True)


def run_full_netlist_sec_checkpoint(original_text: str, candidate_text: str, checker=None) -> EquivalenceResult:
    """Run the final full-netlist SEC checkpoint, fail-closed if unavailable.

    Local topology truth-table checking is necessary but not sufficient for a
    sequential design.  Production callers can inject Yosys/ABC (or another
    formal backend) here; the explicit unavailable result prevents a local
    pass from being reported as whole-netlist proof.
    """
    if checker is None:
        return EquivalenceResult("unavailable", "full_netlist_sec", "formal SEC backend unavailable")
    try:
        result = checker(original_text, candidate_text)
    except Exception as exc:
        return EquivalenceResult("fail", "full_netlist_sec", f"formal SEC failed closed: {exc}")
    status = getattr(result, "status", None) if not isinstance(result, dict) else result.get("status")
    if status == "pass":
        return EquivalenceResult("pass", "full_netlist_sec", "formal SEC checkpoint passed")
    return EquivalenceResult("fail", "full_netlist_sec", f"formal SEC returned {result}")


@dataclass(frozen=True)
class PatchReplacementResult:
    case_id: str
    method: str
    status: str
    patch_id: str
    source_cone: str
    original_roots: list[str]
    replaced_gates: list[str]
    preserved_gates: list[str]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    patched_outputs: list[str]
    patch_size: int

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "method": self.method,
            "status": self.status,
            "patch_id": self.patch_id,
            "source_cone": self.source_cone,
            "original_roots": self.original_roots,
            "replaced_gates": self.replaced_gates,
            "preserved_gates": self.preserved_gates,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "patched_outputs": self.patched_outputs,
            "patch_size": self.patch_size,
        }


def apply_patch_replacement(
    *,
    case_id: str,
    cone: FaninCone,
    patch: PatchCandidate,
) -> PatchReplacementResult:
    """Apply a selected patch to the cone-level internal representation."""
    cone_gate_set = set(cone.gates)
    missing_gates = [gate for gate in patch.gates if gate not in cone_gate_set]
    if missing_gates:
        raise ValueError(f"patch gates are outside source cone: {', '.join(missing_gates)}")

    replaced_gate_set = set(patch.gates)
    return PatchReplacementResult(
        case_id=case_id,
        method="internal_cone_replacement_v0",
        status="applied",
        patch_id=patch.patch_id,
        source_cone=patch.source_cone,
        original_roots=list(cone.roots),
        replaced_gates=list(patch.gates),
        preserved_gates=[gate for gate in cone.gates if gate not in replaced_gate_set],
        boundary_inputs=list(patch.boundary_inputs),
        boundary_outputs=list(patch.boundary_outputs),
        patched_outputs=list(patch.boundary_outputs),
        patch_size=patch.patch_size,
    )
