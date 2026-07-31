import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rseco.case_loader import load_case
from rseco.flow import build_case_metrics


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_minimal_case_variant.py"
SOURCE_CASE = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class MinimalCaseGenerationScriptTest(unittest.TestCase):
    def test_generates_case_variant_for_another_target_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "iscas85_c17_case02"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source-case-dir",
                    str(SOURCE_CASE),
                    "--output-case-dir",
                    str(case_dir),
                    "--case-id",
                    "iscas85_c17_case02",
                    "--target-output",
                    "N23",
                    "--critical-path-id",
                    "c17_path_N7_N23",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((case_dir / "case.yaml").exists())
            self.assertTrue((case_dir / "original" / "original.v").exists())
            self.assertTrue((case_dir / "resynthesized" / "resynthesized.v").exists())

            case = load_case(case_dir)
            self.assertEqual(case.case_id, "iscas85_c17_case02")
            self.assertEqual(case.target_output, "N23")
            self.assertEqual(case.metadata["target"]["critical_path_id"], "c17_path_N7_N23")
            self.assertEqual(case.metadata["target"]["cone_roots"], ["N23"])
            self.assertEqual(case.metadata["target"]["cone_boundary_outputs"], ["N23"])

            report = build_case_metrics(case_dir)
            self.assertEqual(report["case_id"], "iscas85_c17_case02")
            self.assertEqual(report["cone"]["roots"], ["N23"])
            self.assertEqual(report["selected_patch"]["patch_id"], "patch_N23_size_refined_cut")
            self.assertEqual(report["patch_replacement"]["status"], "applied")

    def test_refuses_to_overwrite_existing_case_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "existing_case"
            shutil.copytree(SOURCE_CASE, case_dir)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source-case-dir",
                    str(SOURCE_CASE),
                    "--output-case-dir",
                    str(case_dir),
                    "--case-id",
                    "iscas85_c17_case02",
                    "--target-output",
                    "N23",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)


if __name__ == "__main__":
    unittest.main()
