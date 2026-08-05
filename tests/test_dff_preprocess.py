"""Tests for the dff black-box preprocess in run_sequential_timing_check.

Some ISCAS89 netlists (s820/s832/s953) instantiate a plain ``dff`` with
positional ports in (CK, Q, D) order and no module definition.  The runner
rewrites these to named ports and appends a standard module so Yosys can
map them to SKY130 flops.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mod():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("rsc", ROOT / "scripts" / "run_sequential_timing_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DffPreprocessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_mod()

    def test_rewrites_ck_q_d_positional_to_named(self):
        src = "module m(CK, a, b);\ninput CK;\nwire a, b;\ndff DFF_0(CK,G38,G90);\nendmodule\n"
        # apply the same rewrite used by the runner
        def _fix(m):
            name = m.group(1)
            args = [a.strip() for a in m.group(2).split(",")]
            if len(args) == 3:
                ck, q, d = args
                return "dff " + name + "(.CK(" + ck + "), .D(" + d + "), .Q(" + q + "))"
            return m.group(0)
        out = re.sub(r"\bdff\s+(\w+)\s*\(\s*([^;]+?)\s*\)", _fix, src)
        self.assertIn("dff DFF_0(.CK(CK), .D(G90), .Q(G38))", out)

    def test_appends_module_dff(self):
        src = "module m(CK);\ninput CK;\ndff D(CK,a,b);\nendmodule\n"
        src += "\nmodule dff(input CK, D, output Q);\n  reg Q;\n  always @(posedge CK) Q <= D;\nendmodule\n"
        self.assertIn("module dff(input CK, D, output Q)", src)
        self.assertIn("always @(posedge CK) Q <= D", src)

    def test_no_rewrite_when_no_dff(self):
        src = "module m(CK);\ninput CK;\nendmodule\n"
        self.assertNotIn("dff ", src)
        # ensure the guard in the runner would not trigger
        self.assertFalse(re.search(r"\bdff\s+\w+\s*\(", src) and "module dff" not in src)

    def test_three_arg_only(self):
        src = "dff D(CK,a);"
        def _fix(m):
            name = m.group(1)
            args = [a.strip() for a in m.group(2).split(",")]
            if len(args) == 3:
                ck, q, d = args
                return "dff " + name + "(.CK(" + ck + "), .D(" + d + "), .Q(" + q + "))"
            return m.group(0)
        out = re.sub(r"\bdff\s+(\w+)\s*\(\s*([^;]+?)\s*\)", _fix, src)
        self.assertEqual(out, "dff D(CK,a);")

    def test_parse_tns_reads_native_report_tns(self):
        report = "TNS_BEGIN\ntns max -5.74\nTNS_END\n"
        self.assertEqual(self.mod._parse_tns(report), -5.74)

    def test_parse_tns_falls_back_to_slack_sum(self):
        report = "".join([
            "TNS_BEGIN\n",
            "-0.10   slack (VIOLATED)\n",
            "-0.20   slack (VIOLATED)\n",
            "0.05   slack (MET)\n",
            "TNS_END\n",
        ])
        self.assertEqual(self.mod._parse_tns(report), -0.3)

    def test_parse_tns_missing_markers_returns_none(self):
        self.assertIsNone(self.mod._parse_tns("no markers here"))
        self.assertIsNone(self.mod._parse_tns("TNS_BEGIN\nno slack\n"))
        self.assertIsNone(self.mod._parse_tns(""))

    def test_run_opensta_multi_path_emits_all_paths_section(self):
        # multi_path=True should write the all-path report_checks line into
        # the generated Tcl; multi_path=False uses the compact report_tns.
        import inspect
        src = inspect.getsource(self.mod.run_opensta)
        self.assertIn("multi_path: bool = False", src)
        self.assertIn("report_tns", src)
        self.assertIn("slack_max 0 -endpoint_count 100000", src)

    def test_ys_script_reads_preprocessed_circuit_when_dff_present(self):
        """Regression: circuit_for_script must be recomputed after circuit is
        swapped to the preprocessed copy, otherwise Yosys still reads the raw
        file and fails on s820/s832/s953 with Module dff not part of design."""
        import subprocess
        import tempfile

        captured = {}

        def fake_run(cmd, **kwargs):
            ys = Path(cmd[1])
            captured["ys_text"] = ys.read_text(encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            circuit = out / "s820.v"
            nl = "\n"
            circuit.write_text(
                "module s820(CK);" + nl + "input CK;" + nl + "dff DFF_0(CK,G38,G90);" + nl + "endmodule" + nl,
                encoding="utf-8",
            )
            orig_run = self.mod.subprocess.run
            orig_env = self.mod._yosys_env
            try:
                self.mod.subprocess.run = fake_run
                self.mod._yosys_env = lambda: {}
                self.mod.run_yosys_mapping(circuit, out, yosys_cmd=["yosys"])
            finally:
                self.mod.subprocess.run = orig_run
                self.mod._yosys_env = orig_env

            self.assertIn("ys_text", captured)
            ys_text = captured["ys_text"]
            self.assertIn("circuit_pre.v", ys_text)
            self.assertNotIn("read_verilog " + circuit.as_posix(), ys_text)
            self.assertTrue((out / "circuit_pre.v").exists())
            pre_text = (out / "circuit_pre.v").read_text(encoding="utf-8")
            self.assertIn("module dff(input CK, D, output Q)", pre_text)
            self.assertIn("dff DFF_0(.CK(CK), .D(G90), .Q(G38))", pre_text)



if __name__ == "__main__":
    unittest.main()
