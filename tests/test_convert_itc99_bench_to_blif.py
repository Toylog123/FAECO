# -*- coding: utf-8 -*-
"""TDD tests for the ITC-99 .bench -> .blif converter."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "convert_itc99_bench_to_blif.py"


def _load():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("convert_itc99_bench_to_blif", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BenchToBlifTest(unittest.TestCase):
    def test_simple_gates_and_dff(self):
        mod = _load()
        bench = (
            "# comment\n"
            "INPUT(A)\n"
            "INPUT(B)\n"
            "OUTPUT(Y)\n"
            "OUTPUT(Q)\n"
            "N1 = NAND(A, B)\n"
            "Y = AND(A, B)\n"
            "Q = DFF(N1)\n"
        )
        blif = mod.bench_to_blif(bench, model="b18")
        self.assertIn(".model b18", blif)
        self.assertIn(".inputs A B", blif)
        self.assertIn(".outputs Y Q", blif)
        self.assertIn(".names A B N1", blif)
        self.assertIn("11 0", blif)  # NAND
        self.assertIn(".names A B Y", blif)
        self.assertIn("11 1", blif)  # AND
        self.assertIn(".latch\tN1\tQ\t0", blif)

    def test_or_nor_not(self):
        mod = _load()
        blif = mod.bench_to_blif(
            "INPUT(A)\nINPUT(B)\nOUTPUT(O)\nOUTPUT(N)\nOUTPUT(I)\n"
            "O = OR(A, B)\nN = NOR(A, B)\nI = NOT(A)\n",
            model="m",
        )
        # OR: any input high -> output 1
        self.assertIn(".names A B O", blif)
        self.assertIn("1- 1", blif)
        self.assertIn("-1 1", blif)
        # NOR: any input high -> output 0
        self.assertIn("1- 0", blif)
        # NOT
        self.assertIn(".names A I", blif)
        self.assertIn("1 0", blif)

    def test_unsupported_gate_raises(self):
        mod = _load()
        with self.assertRaises(ValueError):
            mod.bench_to_blif("INPUT(A)\nOUTPUT(Y)\nY = MAGIC(A)\n", model="m")

    def test_wire_collection(self):
        mod = _load()
        blif = mod.bench_to_blif(
            "INPUT(A)\nOUTPUT(Y)\nM1 = NOT(A)\nY = NOT(M1)\n",
            model="m",
        )
        self.assertIn(".names A M1", blif)
        self.assertIn(".names M1 Y", blif)

    def test_convert_bench_writes_file(self):
        mod = _load()
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "b18.bench"
        src.write_text("INPUT(A)\nOUTPUT(Q)\nQ = DFF(A)\n", encoding="utf-8")
        out = tmp / "b18.blif"
        mod.convert_bench(src, out)
        text = out.read_text(encoding="utf-8")
        self.assertIn(".latch\tA\tQ\t0", text)
        self.assertTrue(text.rstrip().endswith(".end"))


if __name__ == "__main__":
    unittest.main()
