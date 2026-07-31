"""Cut boundary generation for early FAECO baselines."""

import random
from collections import deque
from dataclasses import dataclass

from .graph import FaninCone


@dataclass(frozen=True)
class CutBoundary:
    method: str
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    internal_nets: list[str]
    gates: list[str]

    @property
    def patch_size(self) -> int:
        return len(self.gates)

    def to_dict(self) -> dict[str, object]:
        return {
            "method": self.method,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "internal_nets": self.internal_nets,
            "gates": self.gates,
            "patch_size": self.patch_size,
        }


@dataclass(frozen=True)
class WeightedCutGraph:
    nodes: list[str]
    node_costs: dict[str, float]
    source: str
    sink: str
    infinite_capacity: float
    split_edges: list[tuple[str, str, float]]
    dependency_edges: list[tuple[str, str, float]]

    def lowest_cost_gate(self) -> str:
        return min(self.nodes, key=lambda gate: (self.node_costs[gate], gate))


@dataclass(frozen=True)
class WeightedCutResult:
    method: str
    source: str
    sink: str
    selected_gate: str
    selected_gates: list[str]
    cut_cost: float
    cut_edges: list[tuple[str, str]]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    gates: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "method": self.method,
            "source": self.source,
            "sink": self.sink,
            "selected_gate": self.selected_gate,
            "selected_gates": self.selected_gates,
            "cut_cost": self.cut_cost,
            "cut_edges": self.cut_edges,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "gates": self.gates,
        }


def fixed_min_cut(cone: FaninCone) -> CutBoundary:
    """Use the current cone boundary as a deterministic fixed-cut baseline."""
    return CutBoundary(
        method="fixed_min_cut",
        boundary_inputs=cone.boundary_inputs,
        boundary_outputs=cone.boundary_outputs,
        internal_nets=cone.internal_nets,
        gates=cone.gates,
    )


def size_only_cut(cone: FaninCone) -> CutBoundary:
    """Select the smallest deterministic patch around the target output driver."""
    return _single_output_driver_cut(cone, method="size_only_cut")


def critical_path_only_cut(cone: FaninCone) -> CutBoundary:
    """Select the deepest available target-output driver as a Stage A critical-path proxy."""
    return _single_output_driver_cut(cone, method="critical_path_only_cut")


def random_cut(cone: FaninCone, *, seed: int = 20260714, trials: int = 5) -> CutBoundary:
    """Return the best deterministic random-cut trial as the aggregate random baseline."""
    candidates = random_cut_candidates(cone, seed=seed, trials=trials)
    best = min(candidates, key=lambda candidate: (candidate.patch_size, candidate.method))
    return CutBoundary(
        method="random_cut",
        boundary_inputs=best.boundary_inputs,
        boundary_outputs=best.boundary_outputs,
        internal_nets=best.internal_nets,
        gates=best.gates,
    )


def random_cut_candidates(cone: FaninCone, *, seed: int = 20260714, trials: int = 5) -> list[CutBoundary]:
    """Generate reproducible random cut trials over the target-output driver cone."""
    if trials <= 0:
        raise ValueError("trials must be positive")

    root_gate = _gate_driving_output(cone, cone.boundary_outputs[0])
    expandable_gates = [gate for gate in cone.gates if gate != root_gate]
    rng = random.Random(seed)
    candidates: list[CutBoundary] = []
    for trial_index in range(1, trials + 1):
        selected_gate_set = {root_gate}
        for gate in expandable_gates:
            if rng.random() < 0.5:
                selected_gate_set.add(gate)
        selected_gates = [gate for gate in cone.gates if gate in selected_gate_set]
        candidates.append(
            _cut_for_selected_gates(
                cone,
                selected_gates,
                method=f"random_cut_trial_{trial_index:03d}",
            )
        )
    return candidates


def build_weighted_cut_graph(cone: FaninCone, weights: object) -> WeightedCutGraph:
    """Build the first auditable weighted cut graph over cone gates."""
    size_penalty = float(getattr(weights, "size_penalty", 1.0))
    infinite_capacity = 1_000_000_000.0
    costs = {
        gate: 1.0 + size_penalty
        for gate in cone.gates
    }

    non_root_gates = [gate for gate in cone.gates if cone.gate_outputs[gate] not in cone.boundary_outputs]
    for gate in non_root_gates:
        costs[gate] += float(len(non_root_gates))

    split_edges = [
        (f"{gate}:in", f"{gate}:out", costs[gate])
        for gate in cone.gates
    ]
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}
    dependency_edges: list[tuple[str, str, float]] = []
    for gate in cone.gates:
        for input_signal in cone.gate_inputs[gate]:
            input_gate = output_to_gate.get(input_signal)
            if input_gate is not None:
                dependency_edges.append(
                    (f"{input_gate}:out", f"{gate}:in", infinite_capacity)
                )

    return WeightedCutGraph(
        nodes=list(cone.gates),
        node_costs=costs,
        source="source",
        sink=cone.boundary_outputs[0],
        infinite_capacity=infinite_capacity,
        split_edges=split_edges,
        dependency_edges=dependency_edges,
    )


def solve_weighted_cut(cone: FaninCone, cut_graph: WeightedCutGraph) -> WeightedCutResult:
    """Solve the weighted s-t node cut over the cone split graph."""
    capacities = _build_st_capacities(cone, cut_graph)
    residual = _edmonds_karp(capacities, cut_graph.source, cut_graph.sink)
    reachable = _reachable_nodes(residual, cut_graph.source)
    cut_edges = _minimum_cut_edges(cut_graph, capacities, reachable)
    selected_gates = _selected_gates_from_cut_edges(cone, cut_edges)
    selected_gate = selected_gates[0] if selected_gates else ""
    boundary_inputs = _boundary_inputs_for_gates(cone, selected_gates)
    boundary_outputs = _boundary_outputs_for_gates(cone, selected_gates)

    return WeightedCutResult(
        method="weighted_st_min_cut_v1",
        source=cut_graph.source,
        sink=cut_graph.sink,
        selected_gate=selected_gate,
        selected_gates=selected_gates,
        cut_cost=sum(_edge_capacity(capacities, from_node, to_node) for from_node, to_node in cut_edges),
        cut_edges=cut_edges,
        boundary_inputs=boundary_inputs,
        boundary_outputs=boundary_outputs,
        gates=selected_gates,
    )


def weighted_cut_candidates(cone: FaninCone, weights: object) -> list[CutBoundary]:
    """Generate deterministic first-version cut candidates from weighted graph costs."""
    cut_graph = build_weighted_cut_graph(cone, weights)
    candidates = [fixed_min_cut(cone), random_cut(cone), size_only_cut(cone), critical_path_only_cut(cone)]
    size_penalty = float(getattr(weights, "size_penalty", 1.0))
    if size_penalty > 1.0:
        size_refined = _size_refined_cut(cone)
        if size_refined.patch_size < fixed_min_cut(cone).patch_size:
            candidates.append(size_refined)
    return sorted(_deduplicate_candidates(candidates), key=lambda candidate: (_cut_cost(candidate, cut_graph), candidate.method))


def _size_refined_cut(cone: FaninCone) -> CutBoundary:
    return _single_output_driver_cut(cone, method="size_refined_cut")


def _single_output_driver_cut(cone: FaninCone, *, method: str) -> CutBoundary:
    root = cone.boundary_outputs[0]
    root_gate = _gate_driving_output(cone, root)
    return _cut_for_selected_gates(cone, [root_gate], method=method)


def _cut_for_selected_gates(
    cone: FaninCone,
    selected_gates: list[str],
    *,
    method: str,
) -> CutBoundary:
    return CutBoundary(
        method=method,
        boundary_inputs=_boundary_inputs_for_gates(cone, selected_gates),
        boundary_outputs=_boundary_outputs_for_gates(cone, selected_gates),
        internal_nets=_internal_nets_for_gates(cone, selected_gates),
        gates=selected_gates,
    )


def _deduplicate_candidates(candidates: list[CutBoundary]) -> list[CutBoundary]:
    seen: set[str] = set()
    unique: list[CutBoundary] = []
    for candidate in candidates:
        if candidate.method in seen:
            continue
        seen.add(candidate.method)
        unique.append(candidate)
    return unique


def _gate_driving_output(cone: FaninCone, output: str) -> str:
    return next(gate for gate, gate_output in cone.gate_outputs.items() if gate_output == output)


def _cut_cost(candidate: CutBoundary, cut_graph: WeightedCutGraph) -> float:
    return sum(cut_graph.node_costs[gate] for gate in candidate.gates)


def _build_st_capacities(
    cone: FaninCone,
    cut_graph: WeightedCutGraph,
) -> dict[str, dict[str, float]]:
    capacities: dict[str, dict[str, float]] = {}
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}

    for gate in cone.gates:
        if any(input_signal not in output_to_gate for input_signal in cone.gate_inputs[gate]):
            _add_capacity(capacities, cut_graph.source, f"{gate}:in", cut_graph.infinite_capacity)

    for from_node, to_node, capacity in cut_graph.split_edges:
        _add_capacity(capacities, from_node, to_node, capacity)
    for from_node, to_node, capacity in cut_graph.dependency_edges:
        _add_capacity(capacities, from_node, to_node, capacity)

    for gate in cone.gates:
        if cone.gate_outputs[gate] in cone.boundary_outputs:
            _add_capacity(capacities, f"{gate}:out", cut_graph.sink, cut_graph.infinite_capacity)

    return capacities


def _add_capacity(
    capacities: dict[str, dict[str, float]],
    from_node: str,
    to_node: str,
    capacity: float,
) -> None:
    capacities.setdefault(from_node, {})
    capacities.setdefault(to_node, {})
    capacities[from_node][to_node] = capacities[from_node].get(to_node, 0.0) + capacity


def _edmonds_karp(
    capacities: dict[str, dict[str, float]],
    source: str,
    sink: str,
) -> dict[str, dict[str, float]]:
    residual = {node: dict(edges) for node, edges in capacities.items()}
    for from_node, edges in capacities.items():
        for to_node in edges:
            residual.setdefault(to_node, {})
            residual[to_node].setdefault(from_node, 0.0)
        residual.setdefault(from_node, residual.get(from_node, {}))

    while True:
        parent = _augmenting_path(residual, source, sink)
        if sink not in parent:
            return residual

        path_capacity = float("inf")
        node = sink
        while node != source:
            previous = parent[node]
            path_capacity = min(path_capacity, residual[previous][node])
            node = previous

        node = sink
        while node != source:
            previous = parent[node]
            residual[previous][node] -= path_capacity
            residual[node][previous] = residual[node].get(previous, 0.0) + path_capacity
            node = previous


def _augmenting_path(
    residual: dict[str, dict[str, float]],
    source: str,
    sink: str,
) -> dict[str, str]:
    parent: dict[str, str] = {source: source}
    queue: deque[str] = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor, capacity in sorted(residual[node].items()):
            if capacity <= 1e-9 or neighbor in parent:
                continue
            parent[neighbor] = node
            if neighbor == sink:
                return parent
            queue.append(neighbor)
    return parent


def _reachable_nodes(
    residual: dict[str, dict[str, float]],
    source: str,
) -> set[str]:
    reachable = {source}
    queue: deque[str] = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor, capacity in residual[node].items():
            if capacity <= 1e-9 or neighbor in reachable:
                continue
            reachable.add(neighbor)
            queue.append(neighbor)
    return reachable


def _minimum_cut_edges(
    cut_graph: WeightedCutGraph,
    capacities: dict[str, dict[str, float]],
    reachable: set[str],
) -> list[tuple[str, str]]:
    split_edge_order = [(from_node, to_node) for from_node, to_node, _ in cut_graph.split_edges]
    return [
        (from_node, to_node)
        for from_node, to_node in split_edge_order
        if from_node in reachable
        and to_node not in reachable
        and _edge_capacity(capacities, from_node, to_node) < cut_graph.infinite_capacity
    ]


def _selected_gates_from_cut_edges(
    cone: FaninCone,
    cut_edges: list[tuple[str, str]],
) -> list[str]:
    cut_edge_set = set(cut_edges)
    return [
        gate
        for gate in cone.gates
        if (f"{gate}:in", f"{gate}:out") in cut_edge_set
    ]


def _boundary_inputs_for_gates(cone: FaninCone, selected_gates: list[str]) -> list[str]:
    selected_gate_set = set(selected_gates)
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}
    boundary_inputs: list[str] = []

    for gate in selected_gates:
        for input_signal in cone.gate_inputs[gate]:
            driver_gate = output_to_gate.get(input_signal)
            if driver_gate in selected_gate_set or input_signal in boundary_inputs:
                continue
            boundary_inputs.append(input_signal)
    return boundary_inputs


def _boundary_outputs_for_gates(cone: FaninCone, selected_gates: list[str]) -> list[str]:
    selected_gate_set = set(selected_gates)
    consumers_by_signal: dict[str, list[str]] = {}
    for gate in cone.gates:
        for input_signal in cone.gate_inputs[gate]:
            consumers_by_signal.setdefault(input_signal, []).append(gate)

    boundary_outputs: list[str] = []
    selected_outputs = {
        cone.gate_outputs[gate]
        for gate in selected_gates
    }
    for root_output in cone.boundary_outputs:
        if root_output in selected_outputs:
            boundary_outputs.append(root_output)

    for gate in selected_gates:
        output_signal = cone.gate_outputs[gate]
        if output_signal in boundary_outputs:
            continue
        consumers = consumers_by_signal.get(output_signal, [])
        if output_signal in cone.boundary_outputs or any(consumer not in selected_gate_set for consumer in consumers):
            boundary_outputs.append(output_signal)
    return boundary_outputs


def _internal_nets_for_gates(cone: FaninCone, selected_gates: list[str]) -> list[str]:
    boundary_outputs = set(_boundary_outputs_for_gates(cone, selected_gates))
    return [
        cone.gate_outputs[gate]
        for gate in selected_gates
        if cone.gate_outputs[gate] not in boundary_outputs
    ]


def _edge_capacity(
    capacities: dict[str, dict[str, float]],
    from_node: str,
    to_node: str,
) -> float:
    return capacities[from_node][to_node]
