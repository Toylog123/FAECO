"""Regression for protected AES subprocess timeouts at the strict RAW wall cap."""

import importlib
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(EVIDENCE))
MODULE = ("run_aes_protected_online" if os.environ.get("FAECO_AES_LEGACY_LEDGER")
          else "run_aes_incident_priority_matched_v2")
ledger = importlib.import_module(MODULE)
from compare_ibex import ProcessResult, TrialFailure, checked_output


class WallTransportTest(unittest.TestCase):
    def exercise(self, stage_timeout, returncode):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "test.log"
            output.write_text("partial stage output\n", encoding="utf-8")

            def run_process(argv, logfile, effective, **kwargs):
                self.assertEqual(effective, min(stage_timeout, 10.0))
                return ProcessResult(returncode, effective - 0.02, effective, str(logfile))

            with patch.object(ledger, "raw_seconds", side_effect=(100.0, 109.98, 109.98)), \
                    patch.object(ledger.comparison, "run_process", side_effect=run_process):
                with ledger.process_ledger(Path(directory) / "ledger.json", 110.0):
                    row = ledger.comparison.run_process(["openroad"], output, stage_timeout)
                    checked_output(row, "AES_UNLOCKED_DRC_COMPLETE")

    def test_wall_clipped_timeout_before_raw_deadline(self):
        with self.assertRaises(ledger.WallWindowEnded):
            self.exercise(stage_timeout=120.0, returncode=None)

    def test_shorter_stage_timeout_still_raises_normal_trial_failure(self):
        with self.assertRaises(TrialFailure):
            self.exercise(stage_timeout=2.0, returncode=None)

    def test_nonzero_tool_error_is_not_reclassified_as_timeout(self):
        with self.assertRaises(TrialFailure):
            self.exercise(stage_timeout=120.0, returncode=1)


if __name__ == "__main__":
    unittest.main()
