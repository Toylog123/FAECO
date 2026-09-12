import unittest

from rseco.failures import FailureThresholds, FailureType, classify_failures
from rseco.metrics import change_ratio, logic_level_reduction


class MetricsTest(unittest.TestCase):
    def test_change_ratio_uses_original_gate_count(self):
        self.assertEqual(change_ratio(patch_size=15, original_gate_count=100), 0.15)

    def test_change_ratio_rejects_empty_original_netlist(self):
        with self.assertRaises(ValueError):
            change_ratio(patch_size=1, original_gate_count=0)

    def test_logic_level_reduction_is_before_minus_after(self):
        self.assertEqual(logic_level_reduction(before=12, after=9), 3)


class FailureClassificationTest(unittest.TestCase):
    def test_classifies_equivalence_failure_before_other_quality_checks(self):
        thresholds = FailureThresholds(max_patch_ratio=0.15, min_logic_level_reduction=1)

        failures = classify_failures(
            equivalence_passed=False,
            boundary_closed=True,
            patch_size=10,
            original_gate_count=100,
            logic_level_before=12,
            logic_level_after=9,
            verification_runtime_s=1.0,
            thresholds=thresholds,
        )

        self.assertIn(FailureType.EQUIVALENCE, failures)

    def test_classifies_patch_size_and_timing_failures(self):
        thresholds = FailureThresholds(max_patch_ratio=0.15, min_logic_level_reduction=2)

        failures = classify_failures(
            equivalence_passed=True,
            boundary_closed=True,
            patch_size=20,
            original_gate_count=100,
            logic_level_before=12,
            logic_level_after=11,
            verification_runtime_s=1.0,
            thresholds=thresholds,
        )

        self.assertIn(FailureType.PATCH_TOO_LARGE, failures)
        self.assertIn(FailureType.TIMING_GAIN_INSUFFICIENT, failures)


if __name__ == "__main__":
    unittest.main()
