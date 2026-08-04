"""Regression tests for minimal SKY130 cells extraction (N31-03/N31-05).

2026-08-04: _extract_cells_for_netlist must not silently fall back to the
full cells library when the netlist instantiates SKY130 cells that are
missing from the provided model.  That fallback reintroduces $mul / DFF
models that ABC cannot read and hides the real coverage gap.  It now
raises ValueError listing the missing cells.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rseco.yosys_abc import _extract_cells_for_netlist


class CellsExtractTest(unittest.TestCase):
    @staticmethod
    def _write(tmp: Path, name: str, text: str) -> Path:
        p = tmp / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_assign_only_netlist_returns_library_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            net = self._write(
                tmp,
                "top.v",
                "module top(input a, output y); assign y = a; endmodule\n",
            )
            lib = self._write(
                tmp,
                "cells.v",
                "module sky130_fd_sc_hd__buf_1(input A, output X); assign X = A; endmodule\n",
            )
            out = tmp / "extracted.v"
            result = _extract_cells_for_netlist(net, lib, out)
            self.assertIs(result, lib)
            self.assertFalse(out.exists())

    def test_missing_cell_raises_with_cell_name(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            net = self._write(
                tmp,
                "top.v",
                "module top(input a, output y);\n  sky130_fd_sc_hd__nand2_1 u1 (.A(a), .B(a), .X(y));\nendmodule\n",
            )
            lib = self._write(
                tmp,
                "cells.v",
                "module sky130_fd_sc_hd__buf_1(input A, output X); assign X = A; endmodule\n",
            )
            out = tmp / "extracted.v"
            with self.assertRaises(ValueError) as ctx:
                _extract_cells_for_netlist(net, lib, out)
            self.assertIn("sky130_fd_sc_hd__nand2_1", str(ctx.exception))

    def test_extracts_only_instantiated_modules(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            net = self._write(
                tmp,
                "top.v",
                (
                    "module top(input a, input b, output y);\n"
                    "  sky130_fd_sc_hd__nand2_1 u1 (.A(a), .B(b), .X(n));\n"
                    "  sky130_fd_sc_hd__inv_1 u2 (.A(n), .Y(y));\n"
                    "endmodule\n"
                ),
            )
            lib = self._write(
                tmp,
                "cells.v",
                (
                    "module sky130_fd_sc_hd__nand2_1(input A, input B, output X); assign X = ~(A & B); endmodule\n"
                    "module sky130_fd_sc_hd__inv_1(input A, output Y); assign Y = ~A; endmodule\n"
                    "module sky130_fd_sc_hd__buf_1(input A, output X); assign X = A; endmodule\n"
                ),
            )
            out = tmp / "extracted.v"
            result = _extract_cells_for_netlist(net, lib, out)
            self.assertIs(result, out)
            text = out.read_text(encoding="utf-8")
            self.assertIn("module sky130_fd_sc_hd__nand2_1", text)
            self.assertIn("module sky130_fd_sc_hd__inv_1", text)
            self.assertNotIn("module sky130_fd_sc_hd__buf_1", text)


if __name__ == "__main__":
    unittest.main()
