import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rseco.case_loader import load_case
from rseco.flow import build_case_metrics


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_minimal_case_from_raw.py"


RAW_VERILOG = """module tiny432 (
    input N1,
    input N2,
    input N3,
    input N4,
    output N10
);
    wire N5;
    wire N6;
    wire N7;

    nand NAND2_1 (N5, N1, N2);
    nand NAND2_2 (N6, N3, N4);
    nand NAND2_3 (N7, N5, N6);
    nand NAND2_4 (N10, N7, N2);
endmodule
"""


class RawCaseGenerationScriptTest(unittest.TestCase):
    def test_generates_minimal_case_from_local_raw_verilog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            raw_path = temp_path / "tiny432.v"
            raw_path.write_text(RAW_VERILOG, encoding="utf-8")
            case_dir = temp_path / "iscas85_tiny432_case01"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-verilog",
                    str(raw_path),
                    "--output-case-dir",
                    str(case_dir),
                    "--case-id",
                    "iscas85_tiny432_case01",
                    "--suite",
                    "ISCAS85",
                    "--circuit",
                    "tiny432",
                    "--target-output",
                    "N10",
                    "--critical-path-id",
                    "tiny432_path_N1_N10",
                    "--original-source",
                    "benchmarks/raw/iscas85/tiny432.v",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((case_dir / "original" / "original.v").exists())
            self.assertTrue((case_dir / "resynthesized" / "resynthesized.v").exists())
            self.assertTrue((case_dir / "case.yaml").exists())

            case = load_case(case_dir)
            self.assertEqual(case.case_id, "iscas85_tiny432_case01")
            self.assertEqual(case.metadata["benchmark"]["circuit"], "tiny432")
            self.assertEqual(case.target_output, "N10")
            self.assertEqual(case.metadata["target"]["cone_roots"], ["N10"])
            self.assertEqual(case.metadata["target"]["cone_boundary_outputs"], ["N10"])
            self.assertEqual(case.metadata["target"]["cone_boundary_inputs"], ["N1", "N2", "N3", "N4"])

            report = build_case_metrics(case_dir)
            self.assertEqual(report["case_id"], "iscas85_tiny432_case01")
            self.assertEqual(report["metrics"]["original_gate_count"], 4)
            self.assertEqual(report["cone"]["roots"], ["N10"])
            self.assertEqual(report["selected_patch"]["patch_id"], "patch_N10_size_refined_cut")
            self.assertEqual(report["patch_replacement"]["status"], "applied")

    def test_rejects_unknown_target_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            raw_path = temp_path / "tiny432.v"
            raw_path.write_text(RAW_VERILOG, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-verilog",
                    str(raw_path),
                    "--output-case-dir",
                    str(temp_path / "bad_case"),
                    "--case-id",
                    "bad_case",
                    "--suite",
                    "ISCAS85",
                    "--circuit",
                    "tiny432",
                    "--target-output",
                    "MISSING_OUTPUT",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("target output is not in raw netlist outputs", result.stderr)


if __name__ == "__main__":
    unittest.main()
