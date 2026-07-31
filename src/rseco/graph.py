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
