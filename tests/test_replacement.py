import unittest
from pathlib import Path

from rseco.cut import fixed_min_cut, weighted_cut_candidates
from rseco.equivalence import EquivalenceResult
from rseco.graph import extract_fanin_cone
from rseco.netlist import parse_verilog_netlist
from rseco.patch import make_patch_candidate
from rseco.ranking import rank_patch_candidates
from rseco.refinement import RefinementWeights
from rseco.replacement import apply_patch_replacement


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class PatchReplacementTest(unittest.TestCase):
    def test_applies_selected_patch_to_cone_internal_representation(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])
        equivalence = EquivalenceResult(
            status="pass",
            method="structural_signature",
            reason="signatures match",
        )
        patches = [
            make_patch_candidate(
                case_id="iscas85_c17_case01",
                boundary=boundary,
                equivalence=equivalence,
            )
            for boundary in weighted_cut_candidates(cone, RefinementWeights(size_penalty=2.0))
        ]
        patch = rank_patch_candidates(patches)[0].patch

        replacement = apply_patch_replacement(
            case_id="iscas85_c17_case01",
            cone=cone,
            patch=patch,
        )

        self.assertEqual(replacement.method, "internal_cone_replacement_v0")
        self.assertEqual(replacement.status, "applied")
        self.assertEqual(replacement.patch_id, "patch_N22_size_refined_cut")
        self.assertEqual(replacement.source_cone, "cone_N22")
        self.assertEqual(replacement.replaced_gates, ["NAND2_5"])
        self.assertEqual(replacement.preserved_gates, ["NAND2_1", "NAND2_2", "NAND2_3"])
        self.assertEqual(replacement.boundary_inputs, ["N10", "N16"])
        self.assertEqual(replacement.boundary_outputs, ["N22"])
        self.assertEqual(replacement.patched_outputs, ["N22"])
        self.assertEqual(
            replacement.to_dict(),
            {
                "case_id": "iscas85_c17_case01",
                "method": "internal_cone_replacement_v0",
                "status": "applied",
                "patch_id": "patch_N22_size_refined_cut",
                "source_cone": "cone_N22",
                "original_roots": ["N22"],
                "replaced_gates": ["NAND2_5"],
                "preserved_gates": ["NAND2_1", "NAND2_2", "NAND2_3"],
                "boundary_inputs": ["N10", "N16"],
                "boundary_outputs": ["N22"],
                "patched_outputs": ["N22"],
                "patch_size": 1,
            },
        )

    def test_rejects_patch_gates_outside_the_source_cone(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")
        cone = extract_fanin_cone(netlist, roots=["N22"])
        equivalence = EquivalenceResult(
            status="pass",
            method="structural_signature",
            reason="signatures match",
        )
        patch = make_patch_candidate(
            case_id="iscas85_c17_case01",
            boundary=fixed_min_cut(cone),
            equivalence=equivalence,
        )
        invalid_patch = patch.__class__(
            **{
                **patch.to_dict(),
                "gates": ["NAND2_5", "MISSING_GATE"],
                "patch_size": 2,
            }
        )

        with self.assertRaisesRegex(ValueError, "patch gates are outside source cone: MISSING_GATE"):
            apply_patch_replacement(
                case_id="iscas85_c17_case01",
                cone=cone,
                patch=invalid_patch,
            )


if __name__ == "__main__":
    unittest.main()
