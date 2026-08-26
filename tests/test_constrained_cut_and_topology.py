from types import SimpleNamespace

from rseco.cut import FaninCone, constrained_weighted_cut_candidates, canonical_cut_hash
from rseco.netlist import parse_verilog_netlist
from rseco.replacement import (
    extract_combinational_window, generate_topology_replacement,
    stitch_topology_replacement, check_local_functional_equivalence,
    parse_verilog_netlist_from_text,
    apply_joint_region_rewrite,
)


def test_flow_cone_candidates_ignores_critical_instances_outside_cone():
    """Regression: a critical-path hard anchor outside the target cone must
    not suppress every constrained cut candidate (s27 target cone G10 lacks
    the deepest critical instance)."""
    from rseco.flow import _cone_candidates

    cone = _diamond()
    weights = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                              critical_coverage_reward=1,
                              verification_cost_penalty=1,
                              equivalence_stability_reward=1,
                              max_cone_gates=1000, physical_penalty=1)
    cands = _cone_candidates(cone, weights, ["g99", "g50"], None,
                             constrained=True, k=2, allow_singleton=False)
    assert cands, "critical instances outside the cone must not yield zero candidates"


def _diamond():
    return FaninCone(
        roots=["OUT"], boundary_inputs=["A", "B", "C"],
        boundary_outputs=["OUT"], internal_nets=["N1", "N2", "N3", "N4"],
        gates=["g1", "g2", "g3", "g4", "g5"],
        gate_outputs={"g1":"N1", "g2":"N2", "g3":"N3", "g4":"N4", "g5":"OUT"},
        gate_inputs={"g1":["A"], "g2":["A"], "g3":["N1"], "g4":["N2"], "g5":["N3", "N4", "C"]},
    )


def test_constrained_kbest_has_distinct_regions_and_anchor_coverage():
    cone = _diamond()
    weights = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                              critical_coverage_reward=1,
                              verification_cost_penalty=1,
                              physical_penalty=1)
    rows = constrained_weighted_cut_candidates(
        cone, weights, k=4, critical_instances=["g3", "g4", "g5"],
        min_critical_coverage=2, hard_anchors=["g5"], window_size=4,
    )
    assert len(rows) == 4
    assert len({canonical_cut_hash(r) for r in rows}) == 4
    assert all("g5" in r.gates for r in rows)
    assert all(len(set(r.gates) & {"g3", "g4", "g5"}) >= 2 for r in rows)
    assert all(not (len(r.gates) == 1 and r.gates == ["g5"]) for r in rows)


def test_constrained_kbest_weight_feedback_changes_order_not_only_cost():
    cone = _diamond()
    base = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                           critical_coverage_reward=1,
                           verification_cost_penalty=1, physical_penalty=1)
    physical = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                               critical_coverage_reward=1,
                               verification_cost_penalty=1, physical_penalty=20)
    a = constrained_weighted_cut_candidates(cone, base, k=3,
                                             critical_instances=["g3", "g4", "g5"],
                                             min_critical_coverage=1)
    b = constrained_weighted_cut_candidates(cone, physical, k=3,
                                             critical_instances=["g3", "g4", "g5"],
                                             min_critical_coverage=1)
    assert [canonical_cut_hash(x) for x in a] != [canonical_cut_hash(x) for x in b]


def test_each_cut_feedback_dimension_can_change_topk_order():
    cone = _diamond()
    base = dict(boundary_penalty=1, size_penalty=1,
                critical_coverage_reward=1, verification_cost_penalty=1,
                physical_penalty=1)
    baseline = [canonical_cut_hash(x) for x in constrained_weighted_cut_candidates(
        cone, SimpleNamespace(**base), k=5,
        critical_instances=["g3", "g4", "g5"], min_critical_coverage=1)]
    for dimension in base:
        changed = dict(base)
        changed[dimension] = 30
        candidate = [canonical_cut_hash(x) for x in constrained_weighted_cut_candidates(
            cone, SimpleNamespace(**changed), k=5,
            critical_instances=["g3", "g4", "g5"], min_critical_coverage=1)]
        assert candidate != baseline, dimension


def test_constrained_kbest_supports_multi_output_cone():
    cone = FaninCone(
        roots=["Y1", "Y2"], boundary_inputs=["A", "B"],
        boundary_outputs=["Y1", "Y2"], internal_nets=["N1"],
        gates=["g1", "g2", "g3"],
        gate_outputs={"g1":"N1", "g2":"Y1", "g3":"Y2"},
        gate_inputs={"g1":["A"], "g2":["N1", "B"], "g3":["N1", "A"]},
    )
    rows, diagnostics = constrained_weighted_cut_candidates(
        cone, SimpleNamespace(boundary_penalty=1, size_penalty=1,
                              critical_coverage_reward=1,
                              verification_cost_penalty=1, physical_penalty=1),
        k=3, critical_instances=["g2", "g3"], min_critical_coverage=1,
        return_diagnostics=True)
    assert rows and all(set(r.boundary_outputs) for r in rows)
    assert diagnostics["returned_k"] == len(rows)


def test_topology_window_rewrite_changes_gates_edges_and_levels_and_is_equivalent():
    text = """module top(A, B, Y);
input A, B;
output Y;
wire N1, N2;
and g1 (N1, A, B);
and g2 (N2, A, B);
or g3 (Y, N1, N2);
endmodule
"""
    netlist = parse_verilog_netlist_from_text(text)
    window = extract_combinational_window(netlist, ["g1", "g2", "g3"])
    replacement = generate_topology_replacement(window)
    revised_joint = apply_joint_region_rewrite(text, replacement, window=window)
    assert "and g1 (Y, A, B);" in revised_joint
    revised = stitch_topology_replacement(text, replacement)
    assert replacement.before.gates == 3
    assert replacement.after.gates == 1
    assert replacement.before.edges != replacement.after.edges
    assert replacement.before.levels > replacement.after.levels
    check = check_local_functional_equivalence(window, revised)
    assert check.status == "pass"


def test_local_checker_fail_closes_when_topology_changes_function():
    text = """module top(A, B, Y);
input A, B;
output Y;
and g1 (Y, A, B);
endmodule
"""
    netlist = parse_verilog_netlist_from_text(text)
    window = extract_combinational_window(netlist, ["g1"])
    bad = text.replace("and g1", "or g1")
    check = check_local_functional_equivalence(window, bad)
    assert check.status == "fail"


def test_joint_region_rewrite_rejects_action_outside_window():
    text = """module top(A, B, Y);
input A, B;
output Y;
wire N1, N2;
and g1 (N1, A, B);
and g2 (N2, A, B);
or g3 (Y, N1, N2);
endmodule
"""
    netlist = parse_verilog_netlist_from_text(text)
    window = extract_combinational_window(netlist, ["g1", "g2", "g3"])
    replacement = generate_topology_replacement(window)
    try:
        apply_joint_region_rewrite(text, replacement, window=window, sizing={"outside": "and2"})
    except ValueError as exc:
        assert "outside" in str(exc)
    else:
        raise AssertionError("joint action outside cut region must be rejected")


def test_constrained_beam_seed_reaches_late_anchor_in_bounded_chain():
    n = 600
    gates = [f"g{i}" for i in range(n)]
    outputs = {f"g{i}": (f"N{i}" if i < n - 1 else "OUT") for i in range(n)}
    inputs = {"g0": ["A"]}
    inputs.update({f"g{i}": [f"N{i-1}"] for i in range(1, n)})
    cone = FaninCone(
        roots=["OUT"], boundary_inputs=["A"], boundary_outputs=["OUT"],
        internal_nets=[f"N{i}" for i in range(n - 1)], gates=gates,
        gate_outputs=outputs, gate_inputs=inputs,
    )
    weights = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                              critical_coverage_reward=1,
                              verification_cost_penalty=1, physical_penalty=1,
                              max_cone_gates=n)
    rows = constrained_weighted_cut_candidates(
        cone, weights, k=1, critical_instances=[f"g{n-1}"],
        min_critical_coverage=1, hard_anchors=[f"g{n-1}"],
        window_size=n, wall_timeout_s=1.0,
    )
    assert rows and f"g{n-1}" in rows[0].gates
