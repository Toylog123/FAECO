import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rseco.case_loader import load_case
from rseco.flow import build_case_metrics
from rseco.netlist import parse_verilog_netlist


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_minimal_case_from_bench.py"


BENCH_TEXT = """# Tiny ISCAS-style BENCH file
INPUT(N1)
INPUT(N2)
INPUT(N3)
INPUT(N4)
OUTPUT(N10)

N5 = NAND(N1, N2)
N6 = AND(N3, N4)
N7 = OR(N5, N6)
N8 = NOT(N7)
N10 = BUF(N8)
"""


EXTENDED_BENCH_TEXT = """# Common BENCH gates used by larger ISCAS-style files
INPUT(N1)
INPUT(N2)
INPUT(N3)
OUTPUT(N11)

N4 = NOR(N1, N2)
N5 = XOR(N2, N3)
N6 = XNOR(N4, N5)
N11 = NAND(N4, N5, N6)
"""


class BenchCaseGenerationScriptTest(unittest.TestCase):
    def test_generates_minimal_case_from_local_bench_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bench_path = temp_path / "tiny432.bench"
            bench_path.write_text(BENCH_TEXT, encoding="utf-8")
            case_dir = temp_path / "iscas85_tiny432_bench_case01"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--bench",
                    str(bench_path),
                    "--output-case-dir",
                    str(case_dir),
                    "--case-id",
                    "iscas85_tiny432_bench_case01",
                    "--suite",
                    "ISCAS85",
                    "--circuit",
                    "tiny432_bench",
                    "--target-output",
                    "N10",
                    "--critical-path-id",
                    "tiny432_bench_path_N1_N10",
                    "--original-source",
                    "benchmarks/raw/iscas85/tiny432.bench",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            netlist = parse_verilog_netlist(case_dir / "original" / "original.v")
            self.assertEqual(netlist.inputs, ["N1", "N2", "N3", "N4"])
            self.assertEqual(netlist.outputs, ["N10"])
            self.assertEqual(netlist.gate_count, 5)
            self.assertEqual([gate.gate_type for gate in netlist.gates], ["nand", "and", "or", "not", "buf"])

            case = load_case(case_dir)
            self.assertEqual(case.case_id, "iscas85_tiny432_bench_case01")
            self.assertEqual(case.target_output, "N10")
            self.assertEqual(case.metadata["target"]["cone_boundary_inputs"], ["N1", "N2", "N3", "N4"])

            report = build_case_metrics(case_dir)
            self.assertEqual(report["metrics"]["original_gate_count"], 5)
            self.assertEqual(report["selected_patch"]["patch_id"], "patch_N10_size_refined_cut")
            self.assertEqual(report["patch_replacement"]["status"], "applied")

    def test_generates_case_from_common_extended_bench_gate_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bench_path = temp_path / "extended.bench"
            bench_path.write_text(EXTENDED_BENCH_TEXT, encoding="utf-8")
            case_dir = temp_path / "iscas85_extended_case01"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--bench",
                    str(bench_path),
                    "--output-case-dir",
                    str(case_dir),
                    "--case-id",
                    "iscas85_extended_case01",
                    "--suite",
                    "ISCAS85",
                    "--circuit",
                    "extended",
                    "--target-output",
                    "N11",
                    "--critical-path-id",
                    "extended_path_N1_N11",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            netlist = parse_verilog_netlist(case_dir / "original" / "original.v")
            self.assertEqual([gate.gate_type for gate in netlist.gates], ["nor", "xor", "xnor", "nand"])
            self.assertEqual(netlist.gates[-1].inputs, ("N4", "N5", "N6"))

            report = build_case_metrics(case_dir)
            self.assertEqual(report["case_id"], "iscas85_extended_case01")
            self.assertEqual(report["metrics"]["original_gate_count"], 4)
            self.assertEqual(report["cone"]["roots"], ["N11"])
            self.assertEqual(report["patch_replacement"]["status"], "applied")

    def test_rejects_unsupported_bench_gate_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bench_path = temp_path / "bad.bench"
            bench_path.write_text(
                "INPUT(N1)\nINPUT(N2)\nOUTPUT(N3)\nN3 = MUX(N1, N2, N1)\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--bench",
                    str(bench_path),
                    "--output-case-dir",
                    str(temp_path / "bad_case"),
                    "--case-id",
                    "bad_case",
                    "--suite",
                    "ISCAS85",
                    "--circuit",
                    "bad",
                    "--target-output",
                    "N3",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported BENCH gate type: MUX", result.stderr)


if __name__ == "__main__":
    unittest.main()
