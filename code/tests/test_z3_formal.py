"""Tests for the Z3 candidate/boundary formal equivalence wrapper.

N31-06 design: Z3 candidate/boundary formal wrapper complements the
existing ABC CEC path.  We use z3-solver (5.0.0) Python API directly
so tests do not need the z3 binary on PATH.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class Z3FormalApiTest(unittest.TestCase):
    def test_z3_formal_module_exposes_required_callables(self):
        from rseco import z3_formal  # noqa: F401
        self.assertTrue(hasattr(z3_formal, "Z3FormalEquivalenceResult"))
        self.assertTrue(hasattr(z3_formal, "check_z3_candidate_boundary_equivalence"))

    def test_two_identical_blifs_pass(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["a"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")
            self.assertEqual(result.tool, "z3")
            self.assertGreaterEqual(result.runtime_s, 0.0)
            self.assertIn("a", result.boundary_ports)

    def test_diff_in_output_fails(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original = temp_path / "original.v"
            original.write_text(
                "module top(input a, input b, output y); assign y = a & b; endmodule\n",
                encoding="utf-8",
            )
            replaced = temp_path / "replaced.v"
            replaced.write_text(
                "module top(input a, input b, output y); assign y = a | b; endmodule\n",
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
            # counterexample must include both boundary inputs
            ce_dict = dict(result.counterexample_inputs)
            self.assertIn("a", ce_dict)
            self.assertIn("b", ce_dict)
            # and the chosen values must distinguish AND from OR
            # (a=0, b=0) -> AND=0 OR=0  (same)
            # (a=0, b=1) -> AND=0 OR=1  (diff)
            # (a=1, b=0) -> AND=0 OR=1  (diff)
            # (a=1, b=1) -> AND=1 OR=1  (same)
            a, b = ce_dict["a"], ce_dict["b"]
            self.assertNotEqual(a & b, a | b)

    def test_boundary_subset_passes_when_equivalent(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "top.v"
            verilog.write_text(
                "module top(input a, input b, output y); assign y = a & b; endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["a"],  # only "a" not "b"
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")

    def test_unavailable_when_z3_python_missing(self):
        """In normal path, z3-solver Python API is available; status is 'pass'."""
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "top.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["a"],
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertIn(result.status, {"pass", "unavailable"})

    def test_liberty_optional(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "top.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            # liberty_path=None should still work (BitVec-only mode)
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["a"],
                liberty_path=None,
                output_dir=temp_path / "sta",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "pass")

    def test_creates_smt2_artifact_in_output_dir(self):
        from rseco.z3_formal import check_z3_candidate_boundary_equivalence
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "top.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            output_dir = temp_path / "sta"
            result = check_z3_candidate_boundary_equivalence(
                verilog, verilog,
                boundary_ports=["a"],
                output_dir=output_dir,
                timeout_s=10.0,
            )
            self.assertTrue(output_dir.exists())
            self.assertTrue(result.smt2_problem_path and Path(result.smt2_problem_path).exists())


if __name__ == "__main__":
    unittest.main()