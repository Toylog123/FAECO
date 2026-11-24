"""Check the fresh timing order and separation of scheduler from backend."""

import os
import unittest

from run_aes_cold_online import METHODS

if not os.environ.get("FAECO_AES_BEFORE_FACTORIAL"):
    from run_aes_factorial import ordered_cells


class FactorialOrderTest(unittest.TestCase):
    def test_runs_all_cells_and_then_their_reverse_without_changing_settings(self):
        if os.environ.get("FAECO_AES_BEFORE_FACTORIAL"):
            prior = [(name, name.split("_")[0], name != "fixed") for name in METHODS]
            forward, reverse = prior, list(reversed(prior))
        else:
            forward, reverse = ordered_cells().values()
        self.assertEqual(forward, [
            ("fixed_legacy", "fixed", False), ("fixed_online", "fixed", True),
            ("faeco_legacy", "faeco", False), ("faeco_online", "faeco", True),
        ])
        self.assertEqual(reverse, list(reversed(forward)))


if __name__ == "__main__":
    unittest.main()
