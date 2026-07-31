import unittest
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
    def test_identical_original_and_resynthesized_c17_cones_pass(self):
        original = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        resynthesized = parse_verilog_netlist(CASE_DIR / "resynthesized" / "resynthesized.v")

        result = check_structural_equivalence(original, resynthesized, outputs=["N22"])

        self.assertEqual(result.status, "pass")
        self.assertEqual(result.method, "structural_signature")

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
