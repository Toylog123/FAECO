import sys
import tempfile
import unittest
from pathlib import Path

from rseco.yosys_abc import check_yosys_abc_equivalence, run_yosys_abc_resynthesis_baseline


class YosysAbcFlowTest(unittest.TestCase):
    def test_formal_equivalence_normalizes_to_blif_before_abc_cec(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            revised = temp_path / "revised.v"
            original.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            revised.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            fake_yosys, fake_abc = _write_fake_tools(temp_path)

            result = check_yosys_abc_equivalence(
                original,
                revised,
                outputs=["y", "z"],
                artifact_dir=temp_path / "formal",
                yosys_command=f"{sys.executable} {fake_yosys}",
                abc_command=f"{sys.executable} {fake_abc}",
            )

            self.assertEqual(result.status, "pass")
            self.assertEqual(result.method, "yosys_blif_abc_cec")
            self.assertEqual(result.outputs, ["y", "z"])
            self.assertEqual(result.scope, "gate_level_full_netlist_all_primary_outputs")
            self.assertTrue((temp_path / "formal" / "original.normalized.blif").exists())
            self.assertTrue((temp_path / "formal" / "revised.normalized.blif").exists())
            self.assertTrue((temp_path / "formal" / "abc_cec.log").exists())
            self.assertIn("original.normalized.blif", result.command)
            self.assertIn("revised.normalized.blif", result.command)
            self.assertIn("Networks are equivalent", result.stdout_tail)

    def test_resynthesis_baseline_writes_optimized_blif_stats_and_verification(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            original.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            fake_yosys, fake_abc = _write_fake_tools(temp_path)

            result = run_yosys_abc_resynthesis_baseline(
                original,
                output_dir=temp_path / "baseline",
                yosys_command=f"{sys.executable} {fake_yosys}",
                abc_command=f"{sys.executable} {fake_abc}",
            )

            self.assertEqual(result.status, "success")
            self.assertEqual(result.method, "yosys_blif_abc_rewrite_refactor_resyn")
            self.assertTrue((temp_path / "baseline" / "original.normalized.blif").exists())
            self.assertTrue((temp_path / "baseline" / "abc_rewrite_refactor_resyn.blif").exists())
            self.assertTrue((temp_path / "baseline" / "abc_baseline.log").exists())
            self.assertTrue((temp_path / "baseline" / "abc_baseline_cec.log").exists())
            self.assertEqual(result.output_netlist, str(temp_path / "baseline" / "abc_rewrite_refactor_resyn.blif"))
            self.assertEqual(result.stats["before"]["and"], 6)
            self.assertEqual(result.stats["after"]["and"], 4)
            self.assertEqual(result.verification_status, "pass")

    def test_normalization_strips_utf8_bom_before_invoking_yosys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            revised = temp_path / "revised.v"
            original.write_bytes(b"\xef\xbb\xbfmodule top(input a, output y); assign y = a; endmodule\n")
            revised.write_bytes(b"\xef\xbb\xbfmodule top(input a, output y); assign y = a; endmodule\n")
            fake_yosys, fake_abc = _write_fake_tools(temp_path, reject_bom=True)

            formal = check_yosys_abc_equivalence(
                original,
                revised,
                outputs=["y"],
                artifact_dir=temp_path / "formal",
                yosys_command=f"{sys.executable} {fake_yosys}",
                abc_command=f"{sys.executable} {fake_abc}",
            )
            baseline = run_yosys_abc_resynthesis_baseline(
                original,
                output_dir=temp_path / "baseline",
                yosys_command=f"{sys.executable} {fake_yosys}",
                abc_command=f"{sys.executable} {fake_abc}",
            )

            self.assertEqual(formal.status, "pass")
            self.assertEqual(baseline.status, "success")
            self.assertTrue((temp_path / "formal" / "original.sanitized.v").exists())
            self.assertFalse((temp_path / "formal" / "original.sanitized.v").read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertTrue((temp_path / "formal" / "revised.sanitized.v").exists())
            self.assertFalse((temp_path / "baseline" / "original.sanitized.v").read_bytes().startswith(b"\xef\xbb\xbf"))


class LibertyCellsCecTest(unittest.TestCase):
    """CEC on Liberty-mapped netlists using extracted assign-style cells."""

    ROOT = Path(__file__).resolve().parents[1]
    CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"
    CELLS_V = ROOT / "_tmp_c17_cells.v"

    def _cells(self, temp_path: Path) -> Path:
        # fall back to full extracted model if the minimal probe file is
        # absent (it is written by an earlier probe run; keep test robust)
        if self.CELLS_V.exists():
            return self.CELLS_V
        full = self.ROOT / "benchmarks" / "raw" / "skywater_cells_models" / "sky130_cells_v2.v"
        if not full.exists():
            self.skipTest("SKY130 cells model not available")
        return full

    def test_cec_passes_with_liberty_cells_on_real_resynthesized_c17(self):
        import shutil
        if shutil.which("yosys") is None or shutil.which("yosys-abc") is None:
            self.skipTest("real yosys/abc not available")
        with tempfile.TemporaryDirectory() as temp_dir:
            result = check_yosys_abc_equivalence(
                self.CASE_DIR / "original" / "original.v",
                self.CASE_DIR / "resynthesized" / "resynthesized.v",
                outputs=["N22", "N23"],
                artifact_dir=Path(temp_dir) / "formal",
                liberty_cells_v=self._cells(Path(temp_dir)),
            )
            self.assertEqual(result.status, "pass")
            self.assertIn("equivalent", result.stdout_tail.lower())

    def test_fake_tools_receive_cells_read_in_normalize_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cells = temp_path / "cells.v"
            cells.write_text("module dummy(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            (temp_path / "a.v").write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            (temp_path / "b.v").write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")

            log = temp_path / "yosys_cmds.log"
            fake_yosys = temp_path / "fy.py"
            fake_yosys.write_text(
                "import sys, re, pathlib\n"
                "script = sys.argv[sys.argv.index('-p') + 1]\n"
                "with open(r'" + str(log).replace("\\", "/") + "', 'a', encoding='utf-8') as f: f.write(script + '\\n')\n"
                "m = re.search(r'write_blif\\s+([^;]+)', script)\n"
                "path = pathlib.Path(m.group(1).strip().strip('\"'))\n"
                "path.parent.mkdir(parents=True, exist_ok=True)\n"
                "path.write_text('.model fake\\n.inputs a\\n.outputs y\\n.names a y\\n1 1\\n.end\\n', encoding='utf-8')\n",
                encoding="utf-8",
            )
            fake_abc = temp_path / "fa.py"
            fake_abc.write_text(
                "import sys, re\n"
                "script = sys.argv[sys.argv.index('-c') + 1]\n"
                "print('ABC: ' + script)\n"
                "if 'cec ' in script: print('Networks are equivalent after structural hashing.')\n",
                encoding="utf-8",
            )
            result = check_yosys_abc_equivalence(
                temp_path / "a.v",
                temp_path / "b.v",
                outputs=["y"],
                artifact_dir=temp_path / "formal2",
                yosys_command=f"{sys.executable} {fake_yosys}",
                abc_command=f"{sys.executable} {fake_abc}",
                liberty_cells_v=cells,
            )
            self.assertEqual(result.status, "pass")
            recorded = log.read_text(encoding="utf-8")
            self.assertIn("read_verilog", recorded)
            self.assertGreaterEqual(recorded.count("read_verilog"), 2)



def _write_fake_tools(temp_path: Path, *, reject_bom: bool = False) -> tuple[Path, Path]:
    fake_yosys = temp_path / "fake_yosys.py"
    reject_bom_code = (
        "input_match = re.search(r'read_verilog\\s+([^;]+)', script)\n"
        "if input_match:\n"
        "    input_path = pathlib.Path(input_match.group(1).strip().strip('\\\"'))\n"
        "    if input_path.read_bytes().startswith(b'\\xef\\xbb\\xbf'):\n"
        "        print('BOM was not stripped before Yosys', file=sys.stderr)\n"
        "        sys.exit(3)\n"
        if reject_bom
        else ""
    )
    fake_yosys.write_text(
        "import pathlib\n"
        "import re\n"
        "import sys\n"
        "script = sys.argv[sys.argv.index('-p') + 1]\n"
        f"{reject_bom_code}"
        "match = re.search(r'write_blif\\s+([^;]+)', script)\n"
        "if not match:\n"
        "    sys.exit(2)\n"
        "path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
        "path.parent.mkdir(parents=True, exist_ok=True)\n"
        "path.write_text('.model fake\\n.inputs a\\n.outputs y\\n.names a y\\n1 1\\n.end\\n', encoding='utf-8')\n"
        "print('fake yosys wrote', path)\n",
        encoding="utf-8",
    )
    fake_abc = temp_path / "fake_abc.py"
    fake_abc.write_text(
        "import pathlib\n"
        "import re\n"
        "import sys\n"
        "script = sys.argv[sys.argv.index('-c') + 1]\n"
        "print('ABC command line: ' + script)\n"
        "if 'cec ' in script:\n"
        "    print('Networks are equivalent after structural hashing.')\n"
        "if 'print_stats' in script:\n"
        "    print('top : i/o =    5/    2  lat =    0  and =      6  lev =  3')\n"
        "    print('top : i/o =    5/    2  lat =    0  and =      4  lev =  2')\n"
        "match = re.search(r'write_blif\\s+([^;]+)', script)\n"
        "if match:\n"
        "    path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    path.write_text('.model optimized\\n.end\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    return fake_yosys, fake_abc


if __name__ == "__main__":
    unittest.main()
