"""0a gate (step 2): ``update_feedback`` must be bit-identical to the legacy rule.

The whole point of the 0a migration is "new SearchState architecture == old FAECO
behaviour".  ``LEGACY_CONFIG`` is the only configuration that may be used in 0a,
so these tests pin down r2 §3.3 property 2 (bit-identical degradation) and the
adaptive-only properties (release total, F5 continuity, clip) that must *not*
leak into the legacy arm.
"""

import itertools
import unittest

from rseco.failures import FailureType
from rseco.feedback import (
    ADAPTIVE_CONFIG,
    LEGACY_CONFIG,
    FailureFeedbackState,
    describe_actions,
    update_feedback,
)
from rseco.refinement import RefinementWeights, refine_weights

ALL_FAILURES = tuple(FailureType)

# Weight fields compared bit-for-bit against refine_weights().
_COMPARED_FIELDS = (
    "boundary_penalty",
    "size_penalty",
    "critical_coverage_reward",
    "verification_cost_penalty",
    "equivalence_stability_reward",
    "max_cone_gates",
)


def _step_legacy(weights, cone_limit, failures, feedback, round_id):
    feedback, weights, cone_limit = update_feedback(
        feedback, weights, failures, cone_limit, LEGACY_CONFIG, round_id
    )
    return weights, cone_limit, feedback


class LegacyEquivalenceTest(unittest.TestCase):
    def assert_weights_equal(self, left, right):
        for name in _COMPARED_FIELDS:
            self.assertEqual(
                getattr(left, name),
                getattr(right, name),
                f"{name}: {getattr(left, name)!r} != {getattr(right, name)!r}",
            )

    def test_all_64_failure_subsets_match_legacy(self):
        """Exhaustive: every subset of F1-F6, from a fresh state."""
        for size in range(len(ALL_FAILURES) + 1):
            for combination in itertools.combinations(ALL_FAILURES, size):
                failures = set(combination)
                with self.subTest(failures=sorted(f.value for f in failures)):
                    legacy = refine_weights(RefinementWeights(), failures)
                    _, weights, _ = update_feedback(
                        FailureFeedbackState(),
                        RefinementWeights(),
                        failures,
                        1000,
                        LEGACY_CONFIG,
                        1,
                    )
                    self.assert_weights_equal(weights, legacy.weights)

    def test_action_sequence_matches_legacy_for_all_subsets(self):
        """The recorded action list must match, in order — it lands in the artifacts."""
        for size in range(len(ALL_FAILURES) + 1):
            for combination in itertools.combinations(ALL_FAILURES, size):
                failures = set(combination)
                with self.subTest(failures=sorted(f.value for f in failures)):
                    expected = refine_weights(RefinementWeights(), failures).actions
                    actual = describe_actions(failures, LEGACY_CONFIG, FailureFeedbackState(), 1)
                    self.assertEqual(actual, expected)

    def test_multi_round_accumulation_matches_legacy(self):
        """Cumulative rounds: weights drift identically over 20 rounds."""
        sequence = [
            {FailureType.TIMING_GAIN_INSUFFICIENT},
            {FailureType.PATCH_TOO_LARGE, FailureType.TIMING_GAIN_INSUFFICIENT},
            set(),
            {FailureType.EQUIVALENCE, FailureType.BOUNDARY_INVALID},
            {FailureType.VERIFICATION_TOO_EXPENSIVE},
            {FailureType.PHYSICAL_LOAD_FAILURE},
            {FailureType.TIMING_GAIN_INSUFFICIENT},
        ] * 3

        legacy_weights = RefinementWeights()
        legacy_cone = 1000
        weights = RefinementWeights()
        cone_limit = 1000
        feedback = FailureFeedbackState()

        for round_id, failures in enumerate(sequence, start=1):
            legacy = refine_weights(
                RefinementWeights(**{**legacy_weights.__dict__, "max_cone_gates": legacy_cone}),
                failures,
            )
            legacy_weights = legacy.weights
            legacy_cone = legacy.weights.max_cone_gates

            weights, cone_limit, feedback = _step_legacy(
                weights, cone_limit, failures, feedback, round_id
            )

            with self.subTest(round_id=round_id):
                self.assert_weights_equal(weights, legacy_weights)
                self.assertEqual(cone_limit, legacy_cone)

    def test_cone_limit_mirror_and_floor(self):
        """max_cone_gates stays mirrored, and the legacy floor is preserved."""
        for start in (1000, 201, 200, 3, 2, 1):
            with self.subTest(start=start):
                legacy = refine_weights(
                    RefinementWeights(max_cone_gates=start),
                    {FailureType.VERIFICATION_TOO_EXPENSIVE},
                )
                _, weights, cone_limit = update_feedback(
                    FailureFeedbackState(),
                    RefinementWeights(max_cone_gates=start),
                    {FailureType.VERIFICATION_TOO_EXPENSIVE},
                    start,
                    LEGACY_CONFIG,
                    1,
                )
                self.assertEqual(cone_limit, legacy.weights.max_cone_gates)
                self.assertEqual(weights.max_cone_gates, legacy.weights.max_cone_gates)

    def test_empty_failures_is_a_no_op(self):
        feedback, weights, cone_limit = update_feedback(
            FailureFeedbackState(),
            RefinementWeights(),
            set(),
            1000,
            LEGACY_CONFIG,
            7,
        )
        self.assert_weights_equal(weights, RefinementWeights())
        self.assertEqual(cone_limit, 1000)
        # The EMA advances every round (release semantics), so all six channels
        # exist and stay at zero; counts only move on observation.
        self.assertEqual(set(feedback.ema), set(ALL_FAILURES))
        self.assertTrue(all(value == 0.0 for value in feedback.ema.values()))
        self.assertEqual(feedback.count, {})
        self.assertEqual(feedback.last_failure_round, {})

    def test_inputs_are_not_mutated(self):
        """Purity: SearchState owns the state, this function owns nothing."""
        weights_before = RefinementWeights()
        feedback_before = FailureFeedbackState()
        update_feedback(
            feedback_before,
            weights_before,
            {FailureType.EQUIVALENCE, FailureType.VERIFICATION_TOO_EXPENSIVE},
            1000,
            LEGACY_CONFIG,
            1,
        )
        self.assertEqual(weights_before, RefinementWeights())
        self.assertEqual(feedback_before, FailureFeedbackState())

    def test_feedback_state_observability_is_populated_in_legacy_too(self):
        """Legacy still records counts/rounds — behaviour-free observability."""
        feedback, _, _ = update_feedback(
            FailureFeedbackState(),
            RefinementWeights(),
            {FailureType.EQUIVALENCE},
            1000,
            LEGACY_CONFIG,
            4,
        )
        self.assertEqual(feedback.count[FailureType.EQUIVALENCE], 1)
        self.assertEqual(feedback.last_failure_round[FailureType.EQUIVALENCE], 4)
        self.assertEqual(feedback.rate(FailureType.EQUIVALENCE), 1.0)


class AdaptivePropertiesTest(unittest.TestCase):
    def test_isolated_failure_releases_exactly_eta(self):
        """rho controls how many rounds a penalty is spread over, not its total."""
        feedback = FailureFeedbackState()
        weights = RefinementWeights()
        cone_limit = 1000
        start = weights.critical_coverage_reward

        feedback, weights, cone_limit = update_feedback(
            feedback, weights, {FailureType.TIMING_GAIN_INSUFFICIENT}, cone_limit, ADAPTIVE_CONFIG, 1
        )
        for round_id in range(2, 60):
            feedback, weights, cone_limit = update_feedback(
                feedback, weights, set(), cone_limit, ADAPTIVE_CONFIG, round_id
            )

        total = weights.critical_coverage_reward - start
        self.assertAlmostEqual(total, ADAPTIVE_CONFIG.eta_c, places=9)

    def test_release_sequence_is_geometric(self):
        """r2 §3.3 property 1: rho=0.5 releases 0.5, 0.25, 0.125, ... over rounds.

        This is the assertion that pins the "advance the EMA every round"
        semantics: a single failure must keep decaying even on rounds where it
        is not observed again.
        """
        feedback = FailureFeedbackState()
        rates = []
        for round_id in range(1, 5):
            failures = {FailureType.TIMING_GAIN_INSUFFICIENT} if round_id == 1 else set()
            feedback, _, _ = update_feedback(
                feedback, RefinementWeights(), failures, 1000, ADAPTIVE_CONFIG, round_id
            )
            rates.append(feedback.rate(FailureType.TIMING_GAIN_INSUFFICIENT))
        self.assertEqual([round(rate, 6) for rate in rates], [0.5, 0.25, 0.125, 0.0625])

    def test_first_round_step_is_rho_scaled(self):
        feedback = FailureFeedbackState()
        feedback, weights, _ = update_feedback(
            feedback, RefinementWeights(), {FailureType.TIMING_GAIN_INSUFFICIENT}, 1000, ADAPTIVE_CONFIG, 1
        )
        # rate = rho*0 + (1-rho)*1 = 0.5 ; step = eta_c * rate = 0.25*0.5
        self.assertAlmostEqual(weights.critical_coverage_reward, 1.0 + 0.25 * 0.5, places=12)

    def test_f5_continuity_condition_suppresses_single_timeout(self):
        """One isolated F5 must not shrink the cone (b17-style single timeout)."""
        feedback, weights, cone_limit = update_feedback(
            FailureFeedbackState(), RefinementWeights(), {FailureType.VERIFICATION_TOO_EXPENSIVE}, 1000, ADAPTIVE_CONFIG, 1
        )
        self.assertEqual(cone_limit, 1000, "single F5 must not shrink the cone")
        self.assertGreater(weights.verification_cost_penalty, 1.0, "lambda_v still moves")

    def test_f5_continuity_condition_shrinks_on_second_trigger(self):
        feedback = FailureFeedbackState()
        cone_limit = 1000
        weights = RefinementWeights()
        for round_id in (1, 2):
            feedback, weights, cone_limit = update_feedback(
                feedback, weights, {FailureType.VERIFICATION_TOO_EXPENSIVE}, cone_limit, ADAPTIVE_CONFIG, round_id
            )
        self.assertEqual(cone_limit, 500)

    def test_f5_window_forgets_old_triggers(self):
        feedback = FailureFeedbackState()
        cone_limit = 1000
        weights = RefinementWeights()
        # trigger at round 1, then nothing for > window, then trigger at round 6
        feedback, weights, cone_limit = update_feedback(
            feedback, weights, {FailureType.VERIFICATION_TOO_EXPENSIVE}, cone_limit, ADAPTIVE_CONFIG, 1
        )
        for round_id in range(2, 6):
            feedback, weights, cone_limit = update_feedback(
                feedback, weights, set(), cone_limit, ADAPTIVE_CONFIG, round_id
            )
        self.assertEqual(feedback.recent_f5_rounds, (1,))
        feedback, weights, cone_limit = update_feedback(
            feedback, weights, {FailureType.VERIFICATION_TOO_EXPENSIVE}, cone_limit, ADAPTIVE_CONFIG, 6
        )
        self.assertEqual(feedback.recent_f5_rounds, (6,))
        self.assertEqual(cone_limit, 1000, "stale trigger must be forgotten")

    def test_clip_keeps_weights_in_range(self):
        feedback = FailureFeedbackState()
        weights = RefinementWeights()
        cone_limit = 1000
        for round_id in range(1, 200):
            feedback, weights, cone_limit = update_feedback(
                feedback,
                weights,
                {FailureType.PATCH_TOO_LARGE, FailureType.TIMING_GAIN_INSUFFICIENT},
                cone_limit,
                ADAPTIVE_CONFIG,
                round_id,
            )
        self.assertLessEqual(weights.size_penalty, ADAPTIVE_CONFIG.additive_max)
        self.assertLessEqual(weights.critical_coverage_reward, ADAPTIVE_CONFIG.divisor_max)
        self.assertGreaterEqual(weights.size_penalty, ADAPTIVE_CONFIG.additive_min)

    def test_legacy_config_has_no_clip_and_no_f5_continuity(self):
        self.assertFalse(LEGACY_CONFIG.clip)
        self.assertEqual(LEGACY_CONFIG.rho, 0.0)
        self.assertEqual(LEGACY_CONFIG.eta_add, 1.0)
        self.assertEqual(LEGACY_CONFIG.eta_c, 1.0)
        self.assertEqual(LEGACY_CONFIG.f5_min_recent_triggers, 1)
        self.assertEqual(ADAPTIVE_CONFIG.f5_min_recent_triggers, 2)


class FeedbackStateSerialisationTest(unittest.TestCase):
    def test_round_trip(self):
        feedback, _, _ = update_feedback(
            FailureFeedbackState(),
            RefinementWeights(),
            {FailureType.EQUIVALENCE, FailureType.VERIFICATION_TOO_EXPENSIVE},
            1000,
            ADAPTIVE_CONFIG,
            3,
        )
        restored = FailureFeedbackState.from_dict(feedback.to_dict())
        self.assertEqual(restored, feedback)

    def test_to_dict_is_json_safe_and_deterministic(self):
        import json

        feedback, _, _ = update_feedback(
            FailureFeedbackState(),
            RefinementWeights(),
            {FailureType.PATCH_TOO_LARGE, FailureType.EQUIVALENCE},
            1000,
            ADAPTIVE_CONFIG,
            1,
        )
        first = json.dumps(feedback.to_dict(), sort_keys=True)
        second = json.dumps(feedback.to_dict(), sort_keys=True)
        self.assertEqual(first, second)
        self.assertIn("F1_equivalence_failure", first)


if __name__ == "__main__":
    unittest.main()
