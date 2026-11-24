"""Check that the development schedule can replace, and can retain, the incumbent."""

import os
import unittest

import compare_ibex as comparison

if not os.environ.get("FAECO_AES_BEFORE_MARKER_PLAN"):
    from run_aes_marker_repair import run_planned_repair


class MarkerRepairPlanTest(unittest.TestCase):
    def check_plan(self, six_valid, expected):
        keys = "abcdefghijkl"
        pool = [comparison.PhysicalAction(k, k, "large", "small", 1) for k in keys]
        proposed = [tuple("abc"), tuple("def"), tuple("dfijkl")]
        ref = comparison.Endpoint("control", 100, 0, 0, 0.3, "s", "r", True, True)
        policy = comparison.BudgetPolicy.from_ps(36)
        visited = []

        def evaluate(actions):
            visited.append(actions)
            valid = actions != proposed[0] and (actions != proposed[2] or six_valid)
            return comparison.Endpoint("".join(actions), 100 - len(actions), 0, 0, 0.3, "s", "r", valid, valid)

        if os.environ.get("FAECO_AES_BEFORE_MARKER_PLAN"):
            result = comparison.run_method("fixed", ref, pool, evaluate, 3, 3, policy=policy)
        else:
            result = run_planned_repair(ref, proposed, evaluate, policy)

        self.assertEqual(visited, proposed)
        self.assertEqual(result["selected"].endpoint_id, expected)
        self.assertEqual([row["accepted"] for row in result["trace"]], [False, True, six_valid])

    def test_six_can_replace_the_incumbent(self):
        self.check_plan(True, "dfijkl")

    def test_rejected_six_leaves_the_verified_three(self):
        self.check_plan(False, "def")


if __name__ == "__main__":
    unittest.main()
