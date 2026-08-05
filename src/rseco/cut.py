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


def build_weighted_cut_graph(
    cone: FaninCone,
    weights: object,
    r_available: set[str] | None = None,
) -> WeightedCutGraph:
    """Build the auditable weighted cut graph over cone gates.

    All F1-F5 refinement weights enter the node costs (2026-08-04 fix).

    ``r_available``: set of gates that have at least one logic-rewrite (R)
    equivalence candidate in the Liberty library.  Gates *without* an R
    candidate get the critical-coverage discount zeroed (hard equivalence
    constraint: a timing-critical gate that cannot be rewritten must not be
    selected by the F4 critical reward, which would only lead to an F1
    equivalence failure later) and their stability term is minimized.  This
    is the joint bi-objective cut: equivalence is a hard constraint encoded
    directly in the graph, not a post-hoc functional check.
      * boundary_penalty (F1/F2): gates close to the boundary inputs are
        more expensive, pushing the cut toward stable deep regions.
      * equivalence_stability_reward (F1): high-fanout gates (unstable
        equivalence points) get a small extra cost.
      * size_penalty (F3): gates with a large fanin cone (expensive to
        rewrite) get a quadratic cost term, steering the cut away from
        large cones (patch compression).
      * critical_coverage_reward (F4): deep gates (logic-depth proxy for
        the critical path in pre-layout Stage A) become cheaper, so the
        cut can cover deeper logic when timing gain is insufficient.
      * verification_cost_penalty (F5): scales every gate with the cone
        size, shrinking the search space when verification is expensive.
    The costs are normalized by the max depth and the sum of squared
    fanin-cone sizes so the relative ordering is stable.
    """
    infinite_capacity = 1_000_000_000.0
    boundary_penalty = float(getattr(weights, "boundary_penalty", 1.0))
    size_penalty = float(getattr(weights, "size_penalty", 1.0))
    critical_coverage_reward = float(getattr(weights, "critical_coverage_reward", 1.0))
    verification_cost_penalty = float(getattr(weights, "verification_cost_penalty", 1.0))
    equivalence_stability_reward = float(getattr(weights, "equivalence_stability_reward", 1.0))

    depths = _logic_depths(cone)
    max_depth = max(depths.values(), default=1)
    cone_sizes = {gate: _fanin_cone_size(cone, gate) for gate in cone.gates}
    sum_squares = max(1.0, sum(size * size for size in cone_sizes.values()))
    n_gates = max(1, len(cone.gates))
    fanouts = _fanout_counts(cone)

    costs: dict[str, float] = {}
    for gate in cone.gates:
        depth = max(1, depths[gate])
        base = 1.0
        boundary_term = boundary_penalty / (1.0 + depth)
        stability_term = equivalence_stability_reward * 0.1 * fanouts[gate]
        size_term = size_penalty * (cone_sizes[gate] ** 2) / sum_squares
        verification_term = verification_cost_penalty * 0.01 * n_gates
        r_ok = r_available is None or gate in r_available
        # Hard equivalence constraint: without an R candidate, the F4
        # critical reward must not discount this gate (it cannot be
        # rewritten, so covering it with the critical reward only invites an
        # F1 failure).  Stability reward likewise cannot help it.
        critical_divisor = 1.0 + (critical_coverage_reward * depth / max_depth if r_ok else 0.0)
        effective_stability = stability_term if r_ok else 0.0
        costs[gate] = max(
            0.05,
            (base + boundary_term + effective_stability + size_term + verification_term)
            / critical_divisor,
        )

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


def weighted_cut_candidates(
    cone: FaninCone,
    weights: object,
    critical_instances: list[str] | None = None,
    r_available: set[str] | None = None,
    critical_first_default: bool = False,
) -> list[CutBoundary]:
    """Generate deterministic cut candidates from weighted graph costs.

    The weighted s-t min-cut solution (which uses every F1-F5 weight) is
    solved and included as the first candidate; the legacy fixed candidates
    remain as baselines.  Ordering is by total node cost.

    ``critical_instances``: real critical-path instance names (e.g. parsed
    from OpenSTA report_checks).  When provided, a ``critical_path_cover``
    candidate is generated whose gate set is the *intersection* of the cone
    with the critical instances, ordered so the deepest cone gate comes
    last; this lets an F4 (timing gain insufficient) failure turn into a
    candidate that actually covers the timing-critical gates.  As
    critical_coverage_reward grows, that candidate is ranked first.
    """
    cut_graph = build_weighted_cut_graph(cone, weights, r_available=r_available)
    solved = solve_weighted_cut(cone, cut_graph)
    min_cut = _cut_for_selected_gates(
        cone, solved.selected_gates, method=solved.method
    )
    candidates = [min_cut, fixed_min_cut(cone), random_cut(cone), size_only_cut(cone), critical_path_only_cut(cone)]
    # Joint bi-objective cut: the critical-path cover is a *first-round*
    # default candidate (not only an F4 failure remedy).  Both the weighted
    # min-cut and the critical-path cover enter the same STA-measured
    # candidate list; whichever improves WNS first is accepted.
    if critical_instances and critical_first_default:
        cover = _critical_path_cover_cut(cone, critical_instances, r_available=r_available)
        if cover is not None and cover.patch_size > 0:
            candidates.append(cover)
    size_penalty = float(getattr(weights, "size_penalty", 1.0))
    if size_penalty > 1.0:
        size_refined = _size_refined_cut(cone)
        if size_refined.patch_size < fixed_min_cut(cone).patch_size:
            candidates.append(size_refined)
    critical_reward = float(getattr(weights, "critical_coverage_reward", 1.0))
    if critical_instances and critical_reward > 1.0:
        cover = _critical_path_cover_cut(cone, critical_instances, r_available=r_available)
        if cover is not None and cover.patch_size > 0:
            candidates.append(cover)
    # F4 feedback ranks the critical-path-cover cut first so beam-1 loops
    # actually try the timing-targeted candidate after a timing failure
    # (previously the 4-gate cover lost to every 1-gate cut by cost).
    critical_first = (critical_reward > 1.0 or critical_first_default) and bool(critical_instances)
    return sorted(
        _deduplicate_candidates(candidates),
        key=lambda candidate: (
            0 if (critical_first and candidate.method == "critical_path_cover") else 1,
            _cut_cost(candidate, cut_graph),
            0 if candidate.method.startswith("weighted_st_min_cut") else 1,
            candidate.method,
        ),
    )


def _logic_depths(cone: FaninCone) -> dict[str, int]:
    """Longest path length from the cone boundary inputs to each gate.

    Iterative post-order DP: deep combinational cones (e.g. PicoRV32) can
    exceed the Python recursion limit, so depth is computed with an
    explicit stack instead of recursive DFS.
    """
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}
    memo: dict[str, int] = {}
    stack: list[tuple[str, bool]] = []
    for gate in cone.gates:
        stack.append((gate, False))
    while stack:
        gate, expanded = stack.pop()
        if gate in memo:
            continue
        internal_inputs = [
            signal for signal in cone.gate_inputs[gate] if signal in output_to_gate
        ]
        if not internal_inputs:
            memo[gate] = 1
            continue
        if not expanded:
            stack.append((gate, True))
            for signal in internal_inputs:
                driver = output_to_gate[signal]
                if driver not in memo:
                    stack.append((driver, False))
        else:
            # cycle guard: if any input driver is not memoized yet (a
            # combinational loop slipped through cone extraction), fall back
            # to the available depths so the DP always terminates.
            vals = [
                memo[output_to_gate[s]]
                for s in internal_inputs
                if output_to_gate[s] in memo
            ]
            if not vals:
                memo[gate] = 2
            else:
                memo[gate] = 1 + max(vals)
    return memo


def _fanin_cone_size(cone: FaninCone, root_gate: str) -> int:
    """Number of cone gates in the fanin cone of root_gate (inclusive)."""
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}
    seen: set[str] = set()
    stack = [root_gate]
    while stack:
        gate = stack.pop()
        if gate in seen:
            continue
        seen.add(gate)
        for signal in cone.gate_inputs[gate]:
            driver = output_to_gate.get(signal)
            if driver is not None:
                stack.append(driver)
    return len(seen)


def _fanout_counts(cone: FaninCone) -> dict[str, int]:
    """Number of cone-internal consumers of each gate output."""
    counts = {gate: 0 for gate in cone.gates}
    for gate in cone.gates:
        for signal in cone.gate_inputs[gate]:
            driver = next(
                (g for g, out in cone.gate_outputs.items() if out == signal),
                None,
            )
            if driver is not None:
                counts[driver] += 1
    return counts




def split_cone_by_depth(cone: FaninCone, max_subcone_gates: int) -> list[FaninCone]:
    """Divide a large fanin cone into depth-bounded subcones.

    Divide-and-conquer cut (review shortboard defect 4): for designs whose
    full cone exceeds ``max_subcone_gates`` (b18/b19, PicoRV32-scale
    datapaths), solving one global s-t cut graph can be intractable.  The
    cone is split along logic-depth bands so every subcone is small enough
    to cut independently; each subcone keeps only its own gates, treats
    signals driven outside the band as boundary inputs, and marks gates
    whose outputs are consumed by later (shallower) bands as boundary
    outputs so the subcone cut targets the timing-critical portion.
    Returns a list of subcones, or [cone] unchanged when it already fits.
    """
    if len(cone.gates) <= max_subcone_gates:
        return [cone]
    depths = _logic_depths(cone)
    # band gates by depth, deepest first (closest to the timing endpoint)
    by_depth: dict[int, list[str]] = {}
    for gate in cone.gates:
        by_depth.setdefault(depths[gate], []).append(gate)
    levels = sorted(by_depth, reverse=True)
    output_to_gate = {output: gate for gate, output in cone.gate_outputs.items()}
    # downstream (shallower-band / final) consumers for boundary-output detection
    consumer_of: dict[str, set[str]] = {g: set() for g in cone.gates}
    for gate in cone.gates:
        for signal in cone.gate_inputs[gate]:
            driver = output_to_gate.get(signal)
            if driver is not None and driver != gate:
                consumer_of[driver].add(gate)
    subcones: list[FaninCone] = []
    band: list[str] = []
    for level in levels:
        band.extend(by_depth[level])
        if len(band) >= max_subcone_gates or level == levels[-1]:
            subcones.append(_subcone_from_gates(cone, band, consumer_of, output_to_gate, depths))
            band = []
    return subcones


def _subcone_from_gates(cone, band, consumer_of, output_to_gate, depths) -> FaninCone:
    gate_set = set(band)
    gate_outputs = {g: cone.gate_outputs[g] for g in band}
    gate_inputs = {g: list(cone.gate_inputs[g]) for g in band}
    # boundary inputs: signals not driven inside the band
    boundary_inputs: list[str] = []
    seen_bi: set[str] = set()
    for g in band:
        for signal in cone.gate_inputs[g]:
            if signal in gate_outputs.values() or signal in seen_bi:
                continue
            seen_bi.add(signal)
            boundary_inputs.append(signal)
    # boundary outputs: band gates consumed outside the band, or the
    # original cone root when it belongs to this (deepest) band
    boundary_outputs: list[str] = []
    seen_bo: set[str] = set()
    for g in band:
        outside = [c for c in consumer_of[g] if c not in gate_set]
        if outside or (g in output_to_gate.values() and cone.gate_outputs[g] in cone.boundary_outputs):
            out = cone.gate_outputs[g]
            if out not in seen_bo:
                seen_bo.add(out)
                boundary_outputs.append(out)
    # internal nets: band outputs that are not a boundary output
    internal_nets = [
        gate_outputs[g] for g in band
        if gate_outputs[g] not in boundary_outputs and gate_outputs[g] not in cone.boundary_outputs
    ]
    return FaninCone(
        roots=boundary_outputs or [cone.gate_outputs[band[0]]],
        boundary_inputs=boundary_inputs,
        boundary_outputs=boundary_outputs or [cone.gate_outputs[band[0]]],
        internal_nets=internal_nets,
        gates=band,
        gate_outputs=gate_outputs,
        gate_inputs=gate_inputs,
    )


def _critical_path_cover_cut(
    cone: FaninCone,
    critical_instances: list[str],
    r_available: set[str] | None = None,
) -> CutBoundary | None:
    """Cut over the cone gates that lie on the real critical path.

    Only gates present in both the cone and the critical instances are
    included, in critical-path order (deepest first) so the candidate
    targets the timing bottleneck.  When ``r_available`` is given, gates
    without an R equivalence candidate are excluded (hard equivalence
    constraint: the cover only includes gates the repair strategies can
    actually change without an F1 failure).  Returns None when no overlap.
    """
    cone_gate_set = set(cone.gates)
    covered = [g for g in critical_instances if g in cone_gate_set]
    if r_available is not None:
        covered = [g for g in covered if g in r_available]
    if not covered:
        return None
    return _cut_for_selected_gates(cone, covered, method="critical_path_cover")


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
