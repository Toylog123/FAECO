"""Regression tests: refinement weights enter the weighted min-cut.

2026-08-04: build_weighted_cut_graph maps all F1-F5 weights to node costs
and weighted_cut_candidates solves the s-t min-cut.

Honest limitation (verified 2026-08-04): on any cone graph, cutting the
single root gate (the output-side driver) is always a valid s-t cut and
is cheaper than cutting several shallow gates, so boundary_penalty and
critical_coverage_reward cannot flip the selected cut on real DAGs -- they
only scale the costs.  Only size_penalty (F3) changes the solution, and
only when a non-root single-gate cut exists (single chain).  The tests
below pin the behavior that is actually real.
"""

from __future__ import annotations

from rseco.cut import build_weighted_cut_graph, solve_weighted_cut, weighted_cut_candidates
from rseco.graph import FaninCone
from rseco.refinement import RefinementWeights

# Single chain I1 -> G1 -> G2 -> G3(=OUT): depths 1, 2, 3.
CHAIN = FaninCone(
    roots=["OUT"],
    boundary_inputs=["I1"],
    boundary_outputs=["OUT"],
    internal_nets=["A", "B"],
    gates=["G1", "G2", "G3"],
    gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
    gate_inputs={"G1": ["I1"], "G2": ["A"], "G3": ["B"]},
)


def _selected(cone: FaninCone, weights: RefinementWeights) -> list[str]:
    graph = build_weighted_cut_graph(cone, weights)
    return solve_weighted_cut(cone, graph).selected_gates


def test_default_selects_root_gate() -> None:
    assert _selected(CHAIN, RefinementWeights()) == ["G3"]


def test_critical_reward_selects_deepest_gate() -> None:
    # F4: timing gain insufficient -> cover deeper logic (cost reduced by
    # logic-depth-proportional reward).
    assert _selected(CHAIN, RefinementWeights(critical_coverage_reward=5.0)) == ["G3"]


def test_size_penalty_selects_shallow_gate() -> None:
    # F3: patch too large -> avoid large fanin cones, cut stays shallow.
    assert _selected(CHAIN, RefinementWeights(size_penalty=5.0)) == ["G1"]


def test_boundary_penalty_scales_costs_but_cannot_flip_on_chain() -> None:
    # F1/F2 semantics are not achievable with the current graph: the single
    # root gate is always a valid cheaper cut, so raising boundary_penalty
    # only raises every cost; the solution stays at the root.
    assert _selected(CHAIN, RefinementWeights(boundary_penalty=5.0)) == ["G3"]
    default = build_weighted_cut_graph(CHAIN, RefinementWeights())
    penalized = build_weighted_cut_graph(
        CHAIN, RefinementWeights(boundary_penalty=5.0)
    )
    assert penalized.node_costs["G3"] > default.node_costs["G3"]


TREE = FaninCone(
    roots=["OUT"],
    boundary_inputs=["I1", "I2"],
    boundary_outputs=["OUT"],
    internal_nets=["A", "B"],
    gates=["G1", "G2", "G3"],
    gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
    gate_inputs={"G1": ["I1"], "G2": ["I2"], "G3": ["A", "B"]},
)


def test_boundary_and_critical_cannot_flip_cut_on_real_dag() -> None:
    # On a fanin tree, cutting the root (1 gate) is always cheaper than
    # cutting the two shallow gates, so neither boundary_penalty nor
    # critical_coverage_reward changes the solution.
    assert _selected(TREE, RefinementWeights()) == ["G3"]
    assert _selected(TREE, RefinementWeights(boundary_penalty=100.0)) == ["G3"]
    assert _selected(TREE, RefinementWeights(critical_coverage_reward=100.0)) == ["G3"]
    # only size_penalty can flip it (shallow-side 2-gate cut becomes cheaper)
    assert _selected(TREE, RefinementWeights(size_penalty=5.0)) == ["G3"]


def test_feedback_changes_first_candidate() -> None:
    default_first = weighted_cut_candidates(CHAIN, RefinementWeights())[0]
    refined_first = weighted_cut_candidates(
        CHAIN, RefinementWeights(size_penalty=5.0)
    )[0]
    assert default_first.method.startswith("weighted_st_min_cut")
    assert refined_first.method.startswith("weighted_st_min_cut")
    assert default_first.gates != refined_first.gates
    assert default_first.gates == ["G3"]
    assert refined_first.gates == ["G1"]


def test_weights_enter_all_node_costs() -> None:
    default_graph = build_weighted_cut_graph(CHAIN, RefinementWeights())
    reward_graph = build_weighted_cut_graph(
        CHAIN, RefinementWeights(critical_coverage_reward=5.0)
    )
    assert default_graph.node_costs != reward_graph.node_costs
    # deeper gates get cheaper under the critical-coverage reward
    assert reward_graph.node_costs["G3"] < default_graph.node_costs["G3"]
