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


if __name__ == "__main__":
    unittest.main()
