"""Graph helpers for cone extraction."""

from dataclasses import dataclass, field

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
    gate_additional_outputs: dict[str, list[str]] = field(default_factory=dict)
    external_boundary_outputs: list[str] = field(default_factory=list)

    def outputs_for_gate(self, gate: str) -> list[str]:
        return [signal for signal in [self.gate_outputs[gate],
                *self.gate_additional_outputs.get(gate, [])] if signal]

    def signal_drivers(self) -> dict[str, str]:
        return {signal: gate for gate in self.gates for signal in self.outputs_for_gate(gate)}

    def interface_outputs(self) -> list[str]:
        """All exposed nets; external consumers do not become timing roots."""
        return list(dict.fromkeys([*self.boundary_outputs, *self.external_boundary_outputs]))

    def to_dict(self) -> dict[str, object]:
        result = {
            "roots": self.roots,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "internal_nets": self.internal_nets,
            "gates": self.gates,
            "gate_outputs": self.gate_outputs,
            "gate_inputs": self.gate_inputs,
        }
        if self.gate_additional_outputs:
            result["gate_additional_outputs"] = self.gate_additional_outputs
        if self.external_boundary_outputs:
            result["external_boundary_outputs"] = self.external_boundary_outputs
        return result


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
    output_to_gate = {signal: gate for gate in netlist.gates for signal in gate.all_outputs}
    visited_gates: set[str] = set()
    reached_inputs: set[str] = set()

    def physical_signal(signal):
        # Preserve tie-cell physical identities while resolving ordinary assigns.
        return signal if signal in output_to_gate else netlist.resolve_alias(signal)

    def visit(signal: str) -> None:
        signal = physical_signal(signal)
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
    root_signals = list(dict.fromkeys(physical_signal(root) for root in roots))
    outside_inputs = {signal for gate in netlist.gates if gate.name not in visited_gates
                      for signal in gate.inputs}
    module_outputs = {physical_signal(output) for output in netlist.outputs}
    external_outputs = list(dict.fromkeys(
        signal for gate in netlist.gates if gate.name in visited_gates
        for signal in gate.all_outputs
        if signal not in root_signals and (signal in outside_inputs or signal in module_outputs)))
    internal_nets = [
        signal
        for gate in netlist.gates
        if gate.name in visited_gates
        for signal in gate.all_outputs if signal not in root_signals and signal not in external_outputs
    ]

    return FaninCone(
        roots=list(roots),
        boundary_inputs=boundary_inputs,
        boundary_outputs=root_signals,
        internal_nets=internal_nets,
        gates=gates,
        gate_outputs={gate.name: gate.output for gate in netlist.gates if gate.name in visited_gates},
        gate_inputs={gate.name: list(gate.inputs) for gate in netlist.gates if gate.name in visited_gates},
        gate_additional_outputs={gate.name: list(gate.additional_outputs)
                                 for gate in netlist.gates
                                 if gate.name in visited_gates and gate.additional_outputs},
        external_boundary_outputs=external_outputs,
    )
