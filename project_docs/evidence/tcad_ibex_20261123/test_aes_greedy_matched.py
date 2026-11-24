"""Guard the fresh single-gate comparison against disabling its online backend."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from run_aes_greedy_matched import CorrectedComparison, ordered_methods, run_online_arm


class GreedyComparisonTest(unittest.TestCase):
    def test_uses_the_same_diagnostic_backend_in_both_orderings(self):
        self.assertEqual(ordered_methods(), {"forward": ("single", "faeco"), "reverse": ("faeco", "single")})
        runner = SimpleNamespace(use_preview=False)
        reference = object()

        def run(candidate, method, initial):
            self.assertIs(candidate, runner)
            self.assertIs(initial, reference)
            self.assertTrue(candidate.use_preview)
            return method

        with patch.object(CorrectedComparison, "arm", side_effect=run):
            for methods in ordered_methods().values():
                for method in methods:
                    self.assertEqual(run_online_arm(runner, method, reference), method)
                    self.assertFalse(runner.use_preview)


if __name__ == "__main__":
    unittest.main()
