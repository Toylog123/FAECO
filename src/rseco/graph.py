"""Graph helpers for cone extraction."""

from dataclasses import dataclass

from .netlist import Netlist


@dataclass(frozen=True)
class FaninCone:
    roots: list[str]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    internal_nets: list[str]
    gates: list[str]
    gate_outputs: dict[str, str]
    gate_inputs: dict[str, list[str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "roots": self.roots,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "internal_nets": self.internal_nets,
            "gates": self.gates,
            "gate_outputs": self.gate_outputs,
            "gate_inputs": self.gate_inputs,
        }


def _is_sequential_gate(gate_type: str) -> bool:
    """True for flip-flop / latch gate types.

    Sequential outputs are timing boundaries: the combinational fanin cone
    stops there (reg-to-reg logic), which keeps the cone acyclic even when
    the sequential netlist contains feedback loops through flops.

    Recognizes the ISCAS89 ``dff`` wrapper plus direct SKY130 standard-cell
    flops (``sky130_fd_sc_hd__dfxtp_1`` etc.).  Without this, Yosys-mapped
    netlists with direct cells (e.g. PicoRV32) treat flops as combinational
    gates, pull the whole datapath into the cone and create combinational
    cycles through the register feedback (Q -> logic -> D), which hangs the
    logic-depth DP.
    """
    t = gate_type.lower()
    if "dff" in t or "latch" in t:
        return True
    # sky130 flop families: dfx* / dfr* / dfs* / dlx* / dlr* / dfb*
    return t.startswith("sky130_fd_sc_hd__") and any(
        tok in t for tok in ("dfx", "dfr", "dfs", "dlx", "dlr", "dfb")
    )


def extract_fanin_cone(netlist: Netlist, roots: list[str]) -> FaninCone:
    output_to_gate = {gate.output: gate for gate in netlist.gates}
    visited_gates: set[str] = set()
    reached_inputs: set[str] = set()

    def visit(signal: str) -> None:
        if signal in netlist.inputs:
            reached_inputs.add(signal)
            return
        gate = output_to_gate.get(signal)
        if gate is None:
            return
        if _is_sequential_gate(gate.gate_type):
            # a flip-flop output behaves like a primary input for the
            # combinational cone that feeds the timing endpoint
            reached_inputs.add(signal)
            return
        if gate.name in visited_gates:
            return
        visited_gates.add(gate.name)
        for input_signal in gate.inputs:
            visit(input_signal)

    for root in roots:
        visit(root)

    gates = [gate.name for gate in netlist.gates if gate.name in visited_gates]
    boundary_inputs = [signal for signal in netlist.inputs if signal in reached_inputs]
    internal_nets = [
        gate.output
        for gate in netlist.gates
        if gate.name in visited_gates and gate.output not in roots
    ]

    return FaninCone(
        roots=list(roots),
        boundary_inputs=boundary_inputs,
        boundary_outputs=list(roots),
        internal_nets=internal_nets,
        gates=gates,
        gate_outputs={gate.name: gate.output for gate in netlist.gates if gate.name in visited_gates},
        gate_inputs={gate.name: list(gate.inputs) for gate in netlist.gates if gate.name in visited_gates},
    )
