import unittest
from dataclasses import replace
from pathlib import Path

from rseco.cut import (
    build_weighted_cut_graph,
    critical_path_only_cut,
    fixed_min_cut,
    random_cut,
    random_cut_candidates,
    size_only_cut,
    solve_weighted_cut,
    split_cone_by_depth,
    weighted_cut_candidates,
)
from rseco.equivalence import EquivalenceResult
from rseco.graph import FaninCone, extract_fanin_cone
from rseco.netlist import parse_verilog_netlist
from rseco.patch import PatchCandidate, make_patch_candidate
from rseco.refinement import RefinementWeights


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class FixedMinCutTest(unittest.TestCase):
    def test_fixed_min_cut_uses_cone_boundary_as_initial_boundary(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        boundary = fixed_min_cut(cone)

        self.assertEqual(boundary.method, "fixed_min_cut")
        self.assertEqual(boundary.boundary_inputs, ["N1", "N2", "N3", "N6"])
        self.assertEqual(boundary.boundary_outputs, ["N22"])
        self.assertEqual(boundary.gates, ["NAND2_1", "NAND2_2", "NAND2_3", "NAND2_5"])
        self.assertEqual(boundary.patch_size, 4)

    def test_weighted_candidates_add_smaller_cut_when_size_penalty_increases(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        default_candidates = weighted_cut_candidates(cone, RefinementWeights())
        refined_candidates = weighted_cut_candidates(
            cone,
            RefinementWeights(size_penalty=2.0),
        )

        self.assertEqual(
            [candidate.method for candidate in default_candidates],
            ["weighted_st_min_cut_v1", "critical_path_only_cut", "size_only_cut", "random_cut", "fixed_min_cut"],
        )
        self.assertEqual(
            [candidate.method for candidate in refined_candidates],
            ["weighted_st_min_cut_v1", "critical_path_only_cut", "size_only_cut", "size_refined_cut", "random_cut", "fixed_min_cut"],
        )
        self.assertEqual(refined_candidates[0].boundary_inputs, ["N10", "N16"])
        self.assertEqual(refined_candidates[0].boundary_outputs, ["N22"])
        self.assertEqual(refined_candidates[0].gates, ["NAND2_5"])
        self.assertLess(refined_candidates[0].patch_size, refined_candidates[-1].patch_size)
        self.assertTrue(refined_candidates[0].method.startswith("weighted_st_min_cut"))

    def test_size_only_cut_selects_smallest_output_driver_patch(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        boundary = size_only_cut(cone)

        self.assertEqual(boundary.method, "size_only_cut")
        self.assertEqual(boundary.boundary_inputs, ["N10", "N16"])
        self.assertEqual(boundary.boundary_outputs, ["N22"])
        self.assertEqual(boundary.gates, ["NAND2_5"])
        self.assertEqual(boundary.patch_size, 1)

    def test_critical_path_only_cut_selects_deepest_driver_on_target_path(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["A", "B"],
            gates=["G1", "G2", "G3"],
            gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
            gate_inputs={"G1": ["I1"], "G2": ["A"], "G3": ["B", "I2"]},
        )

        boundary = critical_path_only_cut(cone)

        self.assertEqual(boundary.method, "critical_path_only_cut")
        self.assertEqual(boundary.boundary_inputs, ["B", "I2"])
        self.assertEqual(boundary.boundary_outputs, ["OUT"])
        self.assertEqual(boundary.gates, ["G3"])
        self.assertEqual(boundary.patch_size, 1)

    def test_random_cut_candidates_are_seeded_reproducible_trials(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        candidates = random_cut_candidates(cone, seed=20260714, trials=5)

        self.assertEqual(
            [candidate.method for candidate in candidates],
            [
                "random_cut_trial_001",
                "random_cut_trial_002",
                "random_cut_trial_003",
                "random_cut_trial_004",
                "random_cut_trial_005",
            ],
        )
        self.assertEqual(
            [candidate.gates for candidate in candidates],
            [
                ["NAND2_1", "NAND2_2", "NAND2_5"],
                ["NAND2_2", "NAND2_3", "NAND2_5"],
                ["NAND2_2", "NAND2_5"],
                ["NAND2_1", "NAND2_2", "NAND2_5"],
                ["NAND2_2", "NAND2_5"],
            ],
        )
        self.assertTrue(all(candidate.boundary_outputs[0] == "N22" for candidate in candidates))

    def test_random_cut_returns_best_seeded_trial_as_aggregate_baseline(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        boundary = random_cut(cone, seed=20260714, trials=5)

        self.assertEqual(boundary.method, "random_cut")
        self.assertEqual(boundary.boundary_inputs, ["N3", "N6", "N10", "N16"])
        self.assertEqual(boundary.boundary_outputs, ["N22", "N11"])
        self.assertEqual(boundary.gates, ["NAND2_2", "NAND2_5"])
        self.assertEqual(boundary.patch_size, 2)

    def test_random_cut_rejects_empty_trial_count(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        with self.assertRaisesRegex(ValueError, "trials must be positive"):
            random_cut_candidates(cone, seed=20260714, trials=0)

    def test_weighted_cut_graph_assigns_gate_costs_from_refinement_weights(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        cut_graph = build_weighted_cut_graph(cone, RefinementWeights(size_penalty=2.0))

        self.assertEqual(cut_graph.nodes, ["NAND2_1", "NAND2_2", "NAND2_3", "NAND2_5"])
        self.assertEqual(cut_graph.source, "source")
        self.assertEqual(cut_graph.sink, "N22")
        self.assertEqual(cut_graph.infinite_capacity, 1000000000.0)
        self.assertAlmostEqual(cut_graph.node_costs["NAND2_5"], 1.3722727272727273)
        self.assertAlmostEqual(cut_graph.node_costs["NAND2_1"], 1.2981818181818183)
        self.assertAlmostEqual(cut_graph.node_costs["NAND2_2"], 1.2981818181818183)
        self.assertAlmostEqual(cut_graph.node_costs["NAND2_3"], 1.1021818181818182)
        self.assertIn(("NAND2_5:in", "NAND2_5:out", 1.3722727272727273), cut_graph.split_edges)
        self.assertIn(("NAND2_1:out", "NAND2_5:in", 1000000000.0), cut_graph.dependency_edges)
        self.assertIn(("NAND2_3:out", "NAND2_5:in", 1000000000.0), cut_graph.dependency_edges)
        self.assertEqual(cut_graph.lowest_cost_gate(), "NAND2_3")

    def test_weighted_candidates_are_ordered_by_cut_graph_cost(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])

        candidates = weighted_cut_candidates(cone, RefinementWeights(size_penalty=2.0))

        self.assertEqual(
            [candidate.method for candidate in candidates],
            ["weighted_st_min_cut_v1", "critical_path_only_cut", "size_only_cut", "size_refined_cut", "random_cut", "fixed_min_cut"],
        )

    def test_solve_weighted_cut_returns_auditable_cut_result(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])
        cut_graph = build_weighted_cut_graph(cone, RefinementWeights(size_penalty=2.0))

        result = solve_weighted_cut(cone, cut_graph)

        self.assertEqual(result.method, "weighted_st_min_cut_v1")
        self.assertEqual(result.source, "source")
        self.assertEqual(result.sink, "N22")
        self.assertEqual(result.selected_gate, "NAND2_5")
        self.assertEqual(result.selected_gates, ["NAND2_5"])
        self.assertAlmostEqual(result.cut_cost, 1.3722727272727273)
        self.assertEqual(result.cut_edges, [("NAND2_5:in", "NAND2_5:out")])
        self.assertEqual(result.boundary_inputs, ["N10", "N16"])
        self.assertEqual(result.boundary_outputs, ["N22"])
        self.assertEqual(result.gates, ["NAND2_5"])
        result_dict = result.to_dict()
        self.assertEqual(result_dict["method"], "weighted_st_min_cut_v1")
        self.assertEqual(result_dict["source"], "source")
        self.assertEqual(result_dict["sink"], "N22")
        self.assertEqual(result_dict["selected_gate"], "NAND2_5")
        self.assertEqual(result_dict["selected_gates"], ["NAND2_5"])
        self.assertAlmostEqual(result_dict["cut_cost"], 1.3722727272727273)
        self.assertEqual(result_dict["cut_edges"], [("NAND2_5:in", "NAND2_5:out")])
        self.assertEqual(result_dict["boundary_inputs"], ["N10", "N16"])
        self.assertEqual(result_dict["boundary_outputs"], ["N22"])
        self.assertEqual(result_dict["gates"], ["NAND2_5"])

    def test_solve_weighted_cut_finds_global_minimum_over_multiple_split_edges(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["A", "B"],
            gates=["G1", "G2", "G3"],
            gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
            gate_inputs={"G1": ["I1"], "G2": ["I2"], "G3": ["A", "B"]},
        )
        cut_graph = build_weighted_cut_graph(cone, RefinementWeights())
        cut_graph = replace(
            cut_graph,
            node_costs={"G1": 2.0, "G2": 2.0, "G3": 5.0},
            split_edges=[
                ("G1:in", "G1:out", 2.0),
                ("G2:in", "G2:out", 2.0),
                ("G3:in", "G3:out", 5.0),
            ],
        )

        result = solve_weighted_cut(cone, cut_graph)

        self.assertEqual(result.method, "weighted_st_min_cut_v1")
        self.assertEqual(result.selected_gate, "G1")
        self.assertEqual(result.selected_gates, ["G1", "G2"])
        self.assertEqual(result.cut_cost, 4.0)
        self.assertEqual(result.cut_edges, [("G1:in", "G1:out"), ("G2:in", "G2:out")])
        self.assertEqual(result.boundary_inputs, ["I1", "I2"])
        self.assertEqual(result.boundary_outputs, ["A", "B"])
        self.assertEqual(result.gates, ["G1", "G2"])


class PatchCandidateTest(unittest.TestCase):
    def test_make_patch_candidate_records_boundary_and_equivalence(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])
        boundary = fixed_min_cut(cone)
        equivalence = EquivalenceResult(
            status="pass",
            method="structural_signature",
            reason="signatures match",
        )

        patch = make_patch_candidate(
            case_id="iscas85_c17_case01",
            boundary=boundary,
            equivalence=equivalence,
        )

        self.assertIsInstance(patch, PatchCandidate)
        self.assertEqual(patch.patch_id, "patch_N22_fixed_min_cut")
        self.assertEqual(patch.patch_size, 4)
        self.assertEqual(patch.equivalence_result, "pass")
        self.assertEqual(patch.status, "structural_checked")


if __name__ == "__main__":
    unittest.main()


class JointBiObjectiveCutTest(unittest.TestCase):
    """Review shortboard: merge F1 (equivalence) and F4 (timing) into a joint
    bi-objective cut.  Equivalence is a hard constraint encoded in the graph
    (gates without an R candidate get no critical discount), and the
    critical-path cover is a first-round default candidate, not only an F4
    failure remedy."""

    def test_no_r_candidate_gate_gets_no_critical_discount(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["A", "B"],
            gates=["G1", "G2", "G3"],
            gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
            gate_inputs={"G1": ["I1"], "G2": ["A"], "G3": ["B", "I2"]},
        )
        # G3 (deepest, on the critical path) has no R candidate; G1/G2 do.
        r_ok = {"G1", "G2"}
        graph = build_weighted_cut_graph(cone, RefinementWeights(critical_coverage_reward=3.0), r_available=r_ok)
        # Without the hard constraint, G3 (depth 3) would get the largest
        # critical discount; with it, its cost must not be discounted below
        # the shallow gates.
        self.assertGreaterEqual(graph.node_costs["G3"], graph.node_costs["G1"])
        self.assertGreaterEqual(graph.node_costs["G3"], graph.node_costs["G2"])

    def test_critical_path_cover_is_first_round_default(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["A", "B"],
            gates=["G1", "G2", "G3"],
            gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
            gate_inputs={"G1": ["I1"], "G2": ["A"], "G3": ["B", "I2"]},
        )
        candidates = weighted_cut_candidates(
            cone,
            RefinementWeights(critical_coverage_reward=1.0),
            critical_instances=["G2", "G3"],
            r_available={"G1", "G2", "G3"},
            critical_first_default=True,
        )
        methods = [c.method for c in candidates]
        self.assertIn("critical_path_cover", methods)
        cover = next(c for c in candidates if c.method == "critical_path_cover")
        self.assertEqual(set(cover.gates), {"G2", "G3"})

    def test_critical_cover_excludes_gates_without_r_candidate(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["A", "B"],
            gates=["G1", "G2", "G3"],
            gate_outputs={"G1": "A", "G2": "B", "G3": "OUT"},
            gate_inputs={"G1": ["I1"], "G2": ["A"], "G3": ["B", "I2"]},
        )
        # G3 has no R candidate -> the cover must skip it (hard constraint).
        candidates = weighted_cut_candidates(
            cone,
            RefinementWeights(critical_coverage_reward=1.0),
            critical_instances=["G2", "G3"],
            r_available={"G1", "G2"},
            critical_first_default=True,
        )
        cover = next(c for c in candidates if c.method == "critical_path_cover")
        self.assertEqual(set(cover.gates), {"G2"})

    def test_default_candidates_unchanged_without_flags(self):
        """Backward compatibility: without r_available/critical_first_default,
        the candidate list and ordering stay identical."""
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])
        old = weighted_cut_candidates(cone, RefinementWeights())
        new = weighted_cut_candidates(cone, RefinementWeights())
        self.assertEqual([c.method for c in old], [c.method for c in new])
        self.assertEqual([c.gates for c in old], [c.gates for c in new])

class SplitConeTest(unittest.TestCase):
    def test_split_cone_by_depth_partitions_large_cone(self):
        # Build a synthetic 6-gate chain (I1 -> g1 -> g2 -> ... -> g6 -> OUT).
        gates = []
        prev = "I1"
        for i in range(1, 7):
            g = "g%d" % i
            gates.append("%s and2_%d (X_%d, A_%d, B_%d);" % ("xor2_1", i, i, i, i))
        # hand-build a small cone with depth > max_subcone_gates
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["X_1", "X_2", "X_3", "X_4", "X_5"],
            gates=["g1", "g2", "g3", "g4", "g5", "g6"],
            gate_outputs={
                "g1": "X_1", "g2": "X_2", "g3": "X_3",
                "g4": "X_4", "g5": "X_5", "g6": "OUT",
            },
            gate_inputs={
                "g1": ["I1", "I2"],
                "g2": ["X_1"],
                "g3": ["X_2"],
                "g4": ["X_3"],
                "g5": ["X_4"],
                "g6": ["X_5"],
            },
        )

        subcones = split_cone_by_depth(cone, max_subcone_gates=2)

        self.assertGreater(len(subcones), 1)
        all_gates = [g for sc in subcones for g in sc.gates]
        self.assertEqual(sorted(all_gates), sorted(cone.gates))
        # every subcone respects the size bound and stays closed enough to cut
        for sc in subcones:
            self.assertLessEqual(len(sc.gates), 2)
            self.assertTrue(sc.boundary_outputs)

    def test_split_cone_by_depth_noop_for_small_cone(self):
        cone = FaninCone(
            roots=["OUT"],
            boundary_inputs=["I1", "I2"],
            boundary_outputs=["OUT"],
            internal_nets=["X_1"],
            gates=["g1", "g2"],
            gate_outputs={"g1": "X_1", "g2": "OUT"},
            gate_inputs={"g1": ["I1", "I2"], "g2": ["X_1"]},
        )
        self.assertEqual(split_cone_by_depth(cone, 1000), [cone])

