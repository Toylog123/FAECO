"""Tests for Z3 wrapper multi-output / escaped-identifier support.

N31-06 extension: EPFL v2025.1 Verilog uses internal wire assigns
(`assign n19 = ~\\B[1] & \\B[4];`) and escaped identifiers (`\\B[0]`),
which the original single-assign `assign y = ...` wrapper cannot
parse.  This file drives the multi-output / escaped-identifier path.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class Z3MultiOutputTest(unittest.TestCase):
    def test_epfl_style_internal_wire_assigns_pass_when_identical(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "epfl.v"
            verilog.write_text(
                "module top ( \\B[0] , \\B[1] , M[0] , M[1] );\n"
                "  input \\B[0] , \\B[1] ;\n"
                "  output M[0] , M[1] ;\n"
                "  wire n19, n20;\n"
                "  assign n19 = ~\\B[1]  & \\B[0] ;\n"
                "  assign n20 = \\B[0]  | \\B[1] ;\n"
                "  assign M[0] = n19 ;\n"
                "  assign M[1] = n20 ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["B[0]", "B[1]"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")

    def test_epfl_style_multi_output_diff_fails(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            original.write_text(
                "module top ( a , b , M[0] );\n"
                "  input a , b ;\n"
                "  output M[0] ;\n"
                "  assign M[0] = a & b ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            replaced = temp_path / "replaced.v"
            replaced.write_text(
                "module top ( a , b , M[0] );\n"
                "  input a , b ;\n"
                "  output M[0] ;\n"
                "  assign M[0] = a | b ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                original, replaced,
                boundary_ports=["a", "b"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "fail")
            self.assertGreater(len(result.counterexample_inputs), 0)

    def test_escaped_identifier_input_normalized(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "esc.v"
            verilog.write_text(
                "module top ( \\B[0] , M[0] );\n"
                "  input \\B[0] ;\n"
                "  output M[0] ;\n"
                "  assign M[0] = \\B[0] ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            # boundary_ports must accept the normalized form "B[0]"
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["B[0]"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")

    def test_xor_operator_supported(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            original.write_text(
                "module top ( a , b , y );\n"
                "  input a , b ; output y ;\n"
                "  assign y = a ^ b ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            replaced = temp_path / "replaced.v"
            replaced.write_text(
                "module top ( a , b , y );\n"
                "  input a , b ; output y ;\n"
                "  assign y = a & b ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                original, replaced,
                boundary_ports=["a", "b"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "fail")

    def test_constant_zero_and_one_literals(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            original.write_text(
                "module top ( a , y );\n"
                "  input a ; output y ;\n"
                "  assign y = a & 1'b1 ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            replaced = temp_path / "replaced.v"
            replaced.write_text(
                "module top ( a , y );\n"
                "  input a ; output y ;\n"
                "  assign y = a ;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                original, replaced,
                boundary_ports=["a"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")


if __name__ == "__main__":
    unittest.main()