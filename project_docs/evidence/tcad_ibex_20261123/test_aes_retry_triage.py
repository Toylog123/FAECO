"""Check when the proposed scheduler keeps or defers an otherwise eligible DRC retry."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import os
import sys
import unittest


EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(EVIDENCE))
from run_aes_incident_priority_matched_v2 import CorrectedComparison

LEGACY = bool(os.environ.get("FAECO_AES_LEGACY_RETRY"))
if not LEGACY:
    import run_aes_retry_triage as triage


class RetryTriageTest(unittest.TestCase):
    def exercise(self, failures, neighbors, *, stage="initial"):
        klass = CorrectedComparison if LEGACY else triage.RetryTriageComparison
        runner = object.__new__(klass)
        runner.eval = SimpleNamespace(actions={"edit": SimpleNamespace(instance="cell")})
        runner.nets = {}
        with TemporaryDirectory() as work:
            directory = Path(work) / stage
            directory.mkdir()
            assessment = directory / "assessment.json"
            assessment.write_text("{}", encoding="utf-8")
            reports = [directory / "full_drc.rpt"]
            reports[0].write_text("fixture marker", encoding="utf-8")
            with patch.object(CorrectedComparison, "physical", return_value=(None, {}, failures, reports)):
                if LEGACY:
                    _, _, returned, active = runner.physical(("edit",), directory, {"edited_net"}, set())
                else:
                    with patch.object(triage, "drc_neighbor_evidence", return_value=(neighbors, [])):
                        _, _, returned, active = runner.physical(("edit",), directory, {"edited_net"}, set())
            decision = directory.parent / "deferred_retry.json"
            return returned, [path.name for path in active], decision.read_text(encoding="utf-8") if decision.exists() else None

    def test_legal_neighbor_retry_is_deferred_with_relative_hold_failure(self):
        for corner in ("FF", "TT", "SS"):
            with self.subTest(corner=corner):
                reason = f"{corner}:hold_regression"
                failures, active, decision = self.exercise(["unlocked_drc", reason], {"neighbor"})
                self.assertEqual(active, [])
                self.assertIn("preliminary_hold_retry_deferred", failures)
                self.assertIn(reason, decision)
                self.assertIn("neighbor", decision)

    def test_hold_pass_keeps_marker_retry_available(self):
        raw = ["full_drc", "unlocked_drc"]
        self.assertEqual(self.exercise(raw, {"neighbor"}), (raw, ["full_drc.rpt"], None))

    def test_missing_marker_keeps_original_outcome(self):
        raw = ["unlocked_drc", "FF:hold_regression"]
        self.assertEqual(self.exercise(raw, set()), (raw, ["full_drc.rpt"], None))

    def test_no_drc_and_unrelated_rejections_keep_original_outcomes(self):
        for raw in (["FF:hold_regression"], ["full_drc", "FF:hold_regression", "pin_access_count"]):
            self.assertEqual(self.exercise(raw, {"neighbor"}), (raw, ["full_drc.rpt"], None))

    def test_drc_retry_itself_is_still_assessed(self):
        raw = ["unlocked_drc", "TT:hold_regression"]
        self.assertEqual(self.exercise(raw, {"neighbor"}, stage="retry"), (raw, ["full_drc.rpt"], None))

    @unittest.skipIf(LEGACY, "the old arm does not define the extra deferral reason")
    def test_scheduler_defers_bisection_only_inside_the_opt_in_arm(self):
        runner = object.__new__(triage.RetryTriageComparison)
        original = triage.matched.RELATIVE_HOLD_REASONS

        def run(_method, _reference):
            self.assertEqual(triage.matched.RELATIVE_HOLD_REASONS, original | {triage.DEFERRED_RETRY})
            return "arm result"

        with patch.object(CorrectedComparison, "arm", side_effect=run):
            self.assertEqual(runner.arm("faeco", None), "arm result")
            self.assertEqual(triage.matched.RELATIVE_HOLD_REASONS, original)


if __name__ == "__main__":
    unittest.main()
