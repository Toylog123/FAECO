import unittest

from rseco.patch import PatchCandidate
from rseco.ranking import RankingWeights, rank_patch_candidates, score_patch_candidate


def make_patch(
    patch_id: str,
    *,
    patch_size: int,
    boundary_inputs: list[str],
    boundary_outputs: list[str],
    equivalence_result: str = "pass",
    cut_method: str = "test_cut",
) -> PatchCandidate:
    return PatchCandidate(
        case_id="case01",
        patch_id=patch_id,
        source_cone="cone_N22",
        cut_method=cut_method,
        boundary_inputs=boundary_inputs,
        boundary_outputs=boundary_outputs,
        gates=[f"g{i}" for i in range(patch_size)],
        patch_size=patch_size,
        equivalence_result=equivalence_result,
        equivalence_method="structural_signature",
        status="structural_checked" if equivalence_result == "pass" else "equivalence_failed",
    )


class PatchRankingTest(unittest.TestCase):
    def test_scores_patch_with_interpretable_first_version_features(self):
        patch = make_patch(
            "patch_small",
            patch_size=2,
            boundary_inputs=["N1", "N2"],
            boundary_outputs=["N22"],
        )

        ranked = score_patch_candidate(
            patch,
            timing_gain=3.0,
            verification_cost=0.5,
            weights=RankingWeights(),
        )

        self.assertEqual(ranked.patch_id, "patch_small")
        self.assertEqual(ranked.features["timing_gain"], 3.0)
        self.assertEqual(ranked.features["patch_size"], 2.0)
        self.assertEqual(ranked.features["boundary_complexity"], 3.0)
        self.assertEqual(ranked.features["verification_cost"], 0.5)
        self.assertEqual(ranked.features["equivalence_confidence"], 1.0)
        self.assertAlmostEqual(ranked.score, -1.5)

    def test_ranks_candidates_by_score_then_stable_patch_id(self):
        smaller = make_patch(
            "patch_b",
            patch_size=2,
            boundary_inputs=["N1", "N2"],
            boundary_outputs=["N22"],
        )
        larger = make_patch(
            "patch_a",
            patch_size=5,
            boundary_inputs=["N1", "N2", "N3", "N6"],
            boundary_outputs=["N22"],
        )
        failed = make_patch(
            "patch_failed",
            patch_size=1,
            boundary_inputs=["N1"],
            boundary_outputs=["N22"],
            equivalence_result="fail",
        )

        ranked = rank_patch_candidates(
            [larger, failed, smaller],
            timing_gains={"patch_a": 3.0, "patch_b": 3.0, "patch_failed": 8.0},
            verification_costs={"patch_a": 0.0, "patch_b": 0.0, "patch_failed": 0.0},
        )

        self.assertEqual([entry.patch_id for entry in ranked], ["patch_b", "patch_a", "patch_failed"])
        self.assertEqual(ranked[0].rank, 1)
        self.assertEqual(ranked[1].rank, 2)
        self.assertEqual(ranked[2].rank, 3)
        self.assertEqual(ranked[2].features["equivalence_confidence"], 0.0)

    def test_prefers_faeco_refined_cut_over_equal_scoring_baselines(self):
        size_refined = make_patch(
            "patch_N22_size_refined_cut",
            patch_size=1,
            boundary_inputs=["N10", "N16"],
            boundary_outputs=["N22"],
            cut_method="size_refined_cut",
        )
        size_only = make_patch(
            "patch_N22_size_only_cut",
            patch_size=1,
            boundary_inputs=["N10", "N16"],
            boundary_outputs=["N22"],
            cut_method="size_only_cut",
        )
        critical_path = make_patch(
            "patch_N22_critical_path_only_cut",
            patch_size=1,
            boundary_inputs=["N10", "N16"],
            boundary_outputs=["N22"],
            cut_method="critical_path_only_cut",
        )

        ranked = rank_patch_candidates([critical_path, size_only, size_refined])

        self.assertEqual(ranked[0].patch_id, "patch_N22_size_refined_cut")
        self.assertEqual(ranked[0].patch.cut_method, "size_refined_cut")


if __name__ == "__main__":
    unittest.main()
