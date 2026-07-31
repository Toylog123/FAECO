import unittest
from pathlib import Path

from rseco.abc_baseline import run_abc_resynthesis_baseline


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class AbcBaselineTest(unittest.TestCase):
    def test_reports_unavailable_when_abc_command_is_missing(self):
        result = run_abc_resynthesis_baseline(
            CASE_DIR / "original" / "original.v",
            output_dir=ROOT / "experiments" / "tmp_missing_abc_baseline_test",
            abc_command="definitely_missing_abc_for_baseline_test",
        )

        self.assertEqual(result.method, "abc_rewrite_refactor_resyn")
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.tool, "abc")
        self.assertEqual(result.command, "definitely_missing_abc_for_baseline_test")
        self.assertIn("not found", result.reason)
        self.assertIsNone(result.output_netlist)
        self.assertGreaterEqual(result.runtime_s, 0.0)
        self.assertEqual(result.to_dict()["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
