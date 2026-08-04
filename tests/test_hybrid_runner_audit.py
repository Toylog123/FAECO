"""Tests for the hybrid-repair runner audit trail (scripts/run_hybrid_repair.py).

The runner records one accepted change per instance in applied_changes and
marks the matching trial as accepted.  When the same instance is accepted again
in a later round (a later change supersedes the earlier one), the earlier
trial must be reset so accepted always equals the final applied changes.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import pathlib
import unittest
import unittest.mock as mock
from pathlib import Path


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
        self.assertTrue(a(-0.5, -5.0, -0.4, -4.0, False))
        self.assertFalse(a(-0.5, -5.0, -0.5, -4.0, False))
        self.assertFalse(a(-0.5, -5.0, -0.6, -4.0, False))
        self.assertFalse(a(-0.5, -5.0, None, None, True))
        self.assertTrue(a(None, None, -0.5, -5.0, True))

    def test_accepts_tns_aware_breaks_wns_plateau(self):
        a = self.runner._accepts
        self.assertTrue(a(-0.5, -5.0, -0.5, -4.0, True))
        self.assertFalse(a(-0.5, -5.0, -0.5, -5.0, True))
        self.assertFalse(a(-0.5, -5.0, -0.5, -6.0, True))
        self.assertTrue(a(-0.5, -5.0, -0.4, -6.0, True))

    def test_eval_candidate_returns_pin_map_for_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td)
            with mock.patch.object(self.runner, "run_opensta", return_value={"wns": -0.4, "tns": -3.0}):
                res = self.runner._eval_candidate(
                    "_05_", "sky130_fd_sc_hd__lpflow_inputiso1p_1",
                    "sky130_fd_sc_hd__or2_1", {"A": "SLEEP", "B": "A", "X": "X"},
                    "R", "module s382;", out, 0.5, "s382",
                )
                self.assertEqual(res[3], {"A": "SLEEP", "B": "A", "X": "X"})
                self.assertEqual(res[4]["wns"], -0.4)



    def test_apply_single_r_and_g(self):
        r = self.runner._apply_single("module m; sky130_fd_sc_hd__inv_1 _a_ (.A(x), .Y(y)); endmodule", "_a_", "G", "sky130_fd_sc_hd__inv_2", {})
        self.assertIn("sky130_fd_sc_hd__inv_2 _a_", r)

    def test_eval_joint_returns_both_and_sta(self):
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td)
            with mock.patch.object(self.runner, "run_opensta", return_value={"wns": -0.3, "tns": -2.0}):
                a = ("_a_", "G", "sky130_fd_sc_hd__inv_2", {})
                b = ("_b_", "G", "sky130_fd_sc_hd__nand2_2", {})
                key, kind, res = self.runner._eval_joint("module m; sky130_fd_sc_hd__inv_1 _a_ (.A(x), .Y(y)); sky130_fd_sc_hd__nand2_1 _b_ (.A(a), .B(b), .Y(z)); endmodule", out, 0.5, "m", a, b)
                self.assertEqual(kind, "JOINT")
                self.assertIn("_a_+_b_", key)
                self.assertEqual(res["wns"], -0.3)

if __name__ == "__main__":
    unittest.main()

