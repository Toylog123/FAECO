from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_aes_sensitivity_greedy as experiment
from run_aes_sensitivity_greedy import rank_actions


def action(name, area=1.0):
    return SimpleNamespace(action_id=name, instance=name, estimated_area_saving=area)


class SensitivityRankingTest(unittest.TestCase):
    def test_uncapped_rank_separates_candidates_tied_by_historical_weight(self):
        pool = [action("large_critical", 100), action("medium", 1.5), action("small", 1), action("far", 1)]
        log = "RANK_WNS_PS -100\nRANK_PIN small X 100\nRANK_PIN far X 900\n"
        log += "RANK_PIN large_critical X -95\nRANK_PIN medium X 50\nRANK_PIN medium Y -90\n"
        ranked = rank_actions(pool, log, -100.0)
        self.assertEqual(ranked["ordered_action_ids"], ["far", "small", "medium", "large_critical"])
        self.assertNotEqual(ranked["rows"]["far"]["score"], ranked["rows"]["small"]["score"])
        self.assertEqual(ranked["rows"]["far"]["historical_score"], ranked["rows"]["small"]["historical_score"])
        self.assertAlmostEqual(ranked["rows"]["medium"]["margin_ps"], 10.0)

    def test_requires_exact_instance_coverage_and_control_wns(self):
        pool = [action("expected")]
        for log in ("RANK_WNS_PS -100\n", "RANK_WNS_PS -90\nRANK_PIN expected X 100\n",
                    "RANK_WNS_PS -100\nRANK_PIN expected X Inf\n", "RANK_WNS_PS -100\nRANK_PIN wrong X 100\n"):
            with self.subTest(log=log), self.assertRaises(ValueError):
                rank_actions(pool, log, -100.0)

    def test_single_run_changes_the_order_without_changing_the_pool_or_faeco(self):
        runner = SimpleNamespace(output=Path("arm_root"))
        pool = [action("one"), action("two")]

        def dispatch(_runner, method, reference):
            return experiment.comparison.run_method(method, reference, pool)

        with patch.object(experiment, "run_online_arm", dispatch), \
                patch.object(experiment.comparison, "run_method", side_effect=lambda _, ref, order: (ref, order)), \
                patch.object(experiment, "score_control", return_value={"ordered_action_ids": ["two", "one"]}) as score:
            self.assertEqual(experiment.SensitivityComparison.run_arm(runner, "single", "control"),
                             ("control", pool[::-1]))
            self.assertEqual(experiment.SensitivityComparison.run_arm(runner, "faeco", "control"), ("control", pool))
            score.assert_called_once_with(runner, pool, runner.output / "single/sensitivity")
