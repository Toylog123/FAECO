"""Regression tests: F1-F5 refinement weights really change the min-cut.

2026-08-04 fix: build_weighted_cut_graph previously ignored every weight
except size_penalty and added a flat penalty to non-root gates, so the
root gate was always the cheapest and feedback never changed the selected
cut.  The cost function now maps all F1-F5 weights to node costs, and
weighted_cut_candidates solves the weighted s-t min-cut instead of only
ranking fixed candidates.
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


def test_boundary_penalty_moves_cut_away_from_boundary() -> None:
    # F1/F2: equivalence/boundary failure -> move the boundary toward the
    # stable deep region, away from the input boundary.
    assert _selected(CHAIN, RefinementWeights(boundary_penalty=5.0)) == ["G3"]


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
