"""Tests for the hybrid-repair runner audit trail (scripts/run_hybrid_repair.py).

The runner records one accepted change per instance in ``applied_changes`` and
marks the matching trial as accepted.  When the same instance is accepted again
in a later round (a later change supersedes the earlier one), the earlier
trial must be reset so ``accepted`` always equals the final applied changes.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_hybrid_repair.py"


def _load_runner():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("run_hybrid_repair", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HybridRunnerAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _load_runner()

    def test_mark_accepted_sets_applied_and_trial(self):
        trials = [
            {"instance": "_08_", "kind": "B", "to_type": "buf:x", "trial_id": 0, "accepted": False},
            {"instance": "_08_", "kind": "B", "to_type": "buf:y", "trial_id": 1, "accepted": False},
        ]
        applied: dict = {}
        self.runner._mark_accepted(trials, applied, "_08_", "B", "buf:y", 1)
        self.assertEqual(applied["_08_"]["trial_id"], 1)
        self.assertTrue(trials[1]["accepted"])
        self.assertFalse(trials[0]["accepted"])

    def test_later_accept_supersedes_earlier_for_same_instance(self):
        # round 1 accepts _08_ -> buf:x (trial 2); round 3 later accepts
        # _08_ -> buf:y (trial 5).  Only trial 5 stays accepted.
        trials = [
            {"instance": "_08_", "kind": "B", "to_type": "buf:x", "trial_id": 2, "accepted": True},
            {"instance": "_09_", "kind": "R", "to_type": "inv", "trial_id": 3, "accepted": False},
            {"instance": "_08_", "kind": "B", "to_type": "buf:y", "trial_id": 5, "accepted": False},
        ]
        applied: dict = {"_08_": {"kind": "B", "new_type": "buf:x", "trial_id": 2}}
        self.runner._mark_accepted(trials, applied, "_08_", "B", "buf:y", 5)
        self.assertEqual(applied["_08_"]["trial_id"], 5)
        self.assertTrue(trials[2]["accepted"])
        self.assertFalse(trials[0]["accepted"])
        # other instance untouched
        self.assertFalse(trials[1]["accepted"])

    def test_applied_trial_count_matches_accepted_entries(self):
        trials = [
            {"instance": "_08_", "kind": "B", "to_type": "buf:x", "trial_id": 0, "accepted": False},
            {"instance": "_08_", "kind": "B", "to_type": "buf:y", "trial_id": 1, "accepted": False},
            {"instance": "_09_", "kind": "G", "to_type": "nor2_2", "trial_id": 2, "accepted": False},
        ]
        applied: dict = {}
        self.runner._mark_accepted(trials, applied, "_08_", "B", "buf:x", 0)
        self.runner._mark_accepted(trials, applied, "_09_", "G", "nor2_2", 2)
        accepted = [t for t in trials if t["accepted"]]
        self.assertEqual(len(accepted), len(applied))

    def test_accepts_strict_wns_default(self):
        a = self.runner._accepts
        # strictly better WNS accepted regardless of tns flag
        self.assertTrue(a(-0.5, -5.0, -0.4, -4.0, False))
        # same WNS but better TNS rejected when not tns-aware
        self.assertFalse(a(-0.5, -5.0, -0.5, -4.0, False))
        # worse WNS rejected even if TNS better
        self.assertFalse(a(-0.5, -5.0, -0.6, -4.0, False))
        # None wns never accepted
        self.assertFalse(a(-0.5, -5.0, None, None, True))
        # None previous treated as always accept (first candidate)
        self.assertTrue(a(None, None, -0.5, -5.0, True))

    def test_accepts_tns_aware_breaks_wns_plateau(self):
        a = self.runner._accepts
        # same WNS but TNS improved -> accepted with --tns-aware
        self.assertTrue(a(-0.5, -5.0, -0.5, -4.0, True))
        # same WNS and same TNS -> rejected
        self.assertFalse(a(-0.5, -5.0, -0.5, -5.0, True))
        # same WNS but TNS worse -> rejected
        self.assertFalse(a(-0.5, -5.0, -0.5, -6.0, True))
        # WNS strictly better still accepted (TNS irrelevant)
        self.assertTrue(a(-0.5, -5.0, -0.4, -6.0, True))



if __name__ == "__main__":
    unittest.main()
