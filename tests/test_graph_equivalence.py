import unittest
import tempfile
from pathlib import Path

from rseco.equivalence import check_abc_equivalence, check_structural_equivalence
from rseco.graph import extract_fanin_cone
from rseco.netlist import parse_verilog_netlist


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class VerilogParserTest(unittest.TestCase):
    def test_parses_multiline_genus_style_declarations(self):
        with self.subTest("Cadence Genus style declarations span continuation lines"):
            temp_path = ROOT / "experiments" / "tmp_multiline_parser_test.v"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(
                """module tiny(N1, N2, N3, N4, N10, N11);
  input N1, N2,
       N3, N4;
  output N10,
       N11;
  wire N5, N6,
       N7;
  nand NAND2_1 (N5, N1, N2);
  and AND2_1 (N6, N3, N4);
  or OR2_1 (N7, N5, N6);
  buf BUF_1 (N10, N7);
  not NOT_1 (N11, N7);
endmodule
""",
                encoding="utf-8",
            )
            try:
                netlist = parse_verilog_netlist(temp_path)
            finally:
                temp_path.unlink(missing_ok=True)

        self.assertEqual(netlist.inputs, ["N1", "N2", "N3", "N4"])
        self.assertEqual(netlist.outputs, ["N10", "N11"])
        self.assertEqual(netlist.wires, ["N5", "N6", "N7"])
        self.assertEqual(netlist.gate_count, 5)
        self.assertEqual(netlist.logic_level("N10"), 3)


class FaninConeTest(unittest.TestCase):
    def test_extracts_n22_fanin_cone_from_c17(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")

        cone = extract_fanin_cone(netlist, roots=["N22"])

        self.assertEqual(cone.roots, ["N22"])
        self.assertEqual(cone.boundary_inputs, ["N1", "N2", "N3", "N6"])
        self.assertEqual(cone.boundary_outputs, ["N22"])
        self.assertEqual(cone.internal_nets, ["N10", "N11", "N16"])
        self.assertEqual(cone.gates, ["NAND2_1", "NAND2_2", "NAND2_3", "NAND2_5"])


class StructuralEquivalenceTest(unittest.TestCase):
    def test_dff_feedback_signature_is_cycle_safe(self):
        """A sequential feedback loop must not recurse forever."""
        netlist_text = """module loop(D, Q);
  input D;
  output Q;
  dfxtp DFF_0(.D(Q), .CLK(D), .Q(Q));
endmodule
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "loop.v"
            path.write_text(netlist_text, encoding="utf-8")
            left = parse_verilog_netlist(path)
            right = parse_verilog_netlist(path)

        result = check_structural_equivalence(left, right, outputs=["Q"])

        self.assertEqual(result.status, "pass")

    def test_feedback_signature_ignores_internal_net_names(self):
        def parse(text: str, filename: str):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                return parse_verilog_netlist(path)

        left = parse(
            """module loop(D, Q1);
  input D;
  output Q1;
  dfxtp DFF_0(.D(Q1), .CLK(D), .Q(Q1));
endmodule
""",
            "left.v",
        )
        right = parse(
            """module loop(D, Q2);
  input D;
  output Q2;
  dfxtp DFF_0(.D(Q2), .CLK(D), .Q(Q2));
endmodule
""",
            "right.v",
        )

        result = check_structural_equivalence(
            left, right, outputs=["Q1"], other_outputs=["Q2"]
        )

        self.assertEqual(result.status, "pass")

    def test_feedback_signature_detects_gate_and_connection_changes(self):
        def parse(text: str, filename: str):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                return parse_verilog_netlist(path)

        baseline = parse(
            """module loop(D, Q);
  input D;
  output Q;
  dfxtp DFF_0(.D(Q), .CLK(D), .Q(Q));
endmodule
""",
            "baseline.v",
        )
        changed_gate = parse(
            """module loop(D, Q);
  input D;
  output Q;
  dfrtp DFF_0(.D(Q), .CLK(D), .Q(Q));
endmodule
""",
            "changed_gate.v",
        )
        changed_connection = parse(
            """module loop(D, Q);
  input D;
  output Q;
  dfxtp DFF_0(.D(D), .CLK(D), .Q(Q));
endmodule
""",
            "changed_connection.v",
        )

        self.assertEqual(
            check_structural_equivalence(baseline, changed_gate, outputs=["Q"]).status,
            "fail",
        )
        self.assertEqual(
            check_structural_equivalence(baseline, changed_connection, outputs=["Q"]).status,
            "fail",
        )

    def test_feedback_signature_distinguishes_shared_and_split_sccs(self):
        def parse(text: str, filename: str):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                return parse_verilog_netlist(path)

        shared = parse(
            """module shared(ROOT);
  output ROOT;
  wire A, B, X;
  and GROOT(ROOT, A, B);
  buf GA(A, X);
  buf GB(B, X);
  buf GX(X, A);
endmodule
""",
            "shared.v",
        )
        split = parse(
            """module split(ROOT);
  output ROOT;
  wire A, B, X, Y;
  and GROOT(ROOT, A, B);
  buf GA(A, X);
  buf GX(X, A);
  buf GB(B, Y);
  buf GY(Y, B);
endmodule
""",
            "split.v",
        )

        result = check_structural_equivalence(shared, split, outputs=["ROOT"])

        self.assertEqual(result.status, "fail")

    def test_signature_distinguishes_combinational_sharing_from_copy(self):
        def parse(text: str, filename: str):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                return parse_verilog_netlist(path)

        shared = parse(
            """module shared(D, ROOT);
  input D;
  output ROOT;
  wire X;
  buf GX(X, D);
  and GROOT(ROOT, X, X);
endmodule
""",
            "shared_dag.v",
        )
        copied = parse(
            """module copied(D, ROOT);
  input D;
  output ROOT;
  wire A, B;
  buf GA(A, D);
  buf GB(B, D);
  and GROOT(ROOT, A, B);
endmodule
""",
            "copied_dag.v",
        )

        result = check_structural_equivalence(shared, copied, outputs=["ROOT"])

        self.assertEqual(result.status, "fail")

    def test_deep_combinational_chain_signature_is_iterative(self):
        """A >1000-level cone must not hit Python recursion limits (ITC-99 b15)."""
        def deep_chain(gate_type: str, depth: int = 2500) -> str:
            wires = ", ".join(f"N{i}" for i in range(1, depth + 1))
            lines = [
                "module deep(D, ROOT);",
                "  input D;",
                "  output ROOT;",
                f"  wire {wires};",
            ]
            prev = "D"
            for i in range(1, depth + 1):
                lines.append(f"  {gate_type} G{i}(N{i}, {prev});")
                prev = f"N{i}"
                lines.append(f"  buf GROOT(ROOT, N{depth});")
            lines.append("endmodule")
            return "\n".join(lines)

        def parse(text: str, filename: str):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                return parse_verilog_netlist(path)

        identical = parse(deep_chain("buf"), "deep_a.v")
        same = parse(deep_chain("buf"), "deep_b.v")
        different_tail = parse(deep_chain("not"), "deep_c.v")

        self.assertEqual(
            check_structural_equivalence(identical, same, outputs=["ROOT"]).status,
            "pass",
        )
        self.assertEqual(
            check_structural_equivalence(identical, different_tail, outputs=["ROOT"]).status,
            "fail",
        )

    def test_resynthesized_c17_is_functionally_restructured_not_identical(self):
        # Since 2026-08-04 the resynthesized netlists are real SKY130-liberty
        # mappings (3 cells vs 6 nands), so structural signatures differ even
        # though the function is preserved.  This is the whole point: the old
        # data were byte-identical copies, which made F4 unreachable.
        original = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        resynthesized = parse_verilog_netlist(CASE_DIR / "resynthesized" / "resynthesized.v")

        result = check_structural_equivalence(original, resynthesized, outputs=["N22"])

        self.assertEqual(result.status, "fail")
        self.assertEqual(result.method, "structural_signature")
        self.assertNotEqual(original.gate_count, resynthesized.gate_count)

    def test_different_c17_outputs_fail_structural_equivalence(self):
        original = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        resynthesized = parse_verilog_netlist(CASE_DIR / "resynthesized" / "resynthesized.v")

        result = check_structural_equivalence(original, resynthesized, outputs=["N22"], other_outputs=["N23"])

        self.assertEqual(result.status, "fail")

    def test_abc_equivalence_reports_unavailable_when_tool_is_missing(self):
        result = check_abc_equivalence(
            CASE_DIR / "original" / "original.v",
            CASE_DIR / "resynthesized" / "resynthesized.v",
            outputs=["N22"],
            abc_command="definitely_missing_abc_for_test",
        )

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.method, "abc_cec")
        self.assertEqual(result.tool, "abc")
        self.assertEqual(result.command, "definitely_missing_abc_for_test")
        self.assertIn("not found", result.reason)
        self.assertEqual(result.outputs, ["N22"])
        self.assertGreaterEqual(result.runtime_s, 0.0)
        self.assertEqual(
            result.to_dict()["status"],
            "unavailable",
        )


if __name__ == "__main__":
    unittest.main()



