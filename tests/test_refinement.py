import unittest

from rseco.failures import FailureType
from rseco.refinement import RefinementWeights, refine_weights


class FailureAwareRefinementTest(unittest.TestCase):
    def test_f3_and_f4_increase_size_penalty_and_critical_reward(self):
        decision = refine_weights(
            RefinementWeights(),
            {FailureType.PATCH_TOO_LARGE, FailureType.TIMING_GAIN_INSUFFICIENT},
        )

        self.assertEqual(decision.weights.size_penalty, 2.0)
        self.assertEqual(decision.weights.critical_coverage_reward, 2.0)
        self.assertEqual(
            decision.actions,
            ["increase_size_penalty", "increase_critical_coverage_reward"],
        )

    def test_f1_f2_and_f5_prioritize_stable_and_bounded_search(self):
        decision = refine_weights(
            RefinementWeights(max_cone_gates=200),
            {
                FailureType.EQUIVALENCE,
                FailureType.BOUNDARY_INVALID,
                FailureType.VERIFICATION_TOO_EXPENSIVE,
            },
        )

        self.assertEqual(decision.weights.boundary_penalty, 3.0)
        self.assertEqual(decision.weights.equivalence_stability_reward, 2.0)
        self.assertEqual(decision.weights.verification_cost_penalty, 2.0)
        self.assertEqual(decision.weights.max_cone_gates, 100)
        self.assertEqual(
            decision.actions,
            [
                "increase_boundary_penalty",
                "increase_equivalence_stability_reward",
                "increase_boundary_penalty",
                "increase_verification_cost_penalty",
                "reduce_max_cone_gates",
            ],
        )


if __name__ == "__main__":
    unittest.main()
