"""Tests for logic-rewrite core logic (strategy R of failure-aware hybrid repair).

Strategy R replaces a critical-path cell with a functionally-equivalent
library cell that has a lower intrinsic delay in the pre-layout (ideal-net)
regime, where gate sizing has no wire load to exploit.  The motivating
example: ``sky130_fd_sc_hd__lpflow_inputiso1p_1`` implements ``X = A | SLEEP``
(identical to ``or2``) but its delay is larger, so swapping it for ``or2``
recovers timing.
"""

from __future__ import annotations

import unittest

from rseco.logic_rewrite import (
    apply_rewrite,
    equivalence_candidates,
    parse_liberty_cells,
)

LIBERTY_SAMPLE = """\
library(min) {
  cell ("sky130_fd_sc_hd__or2_1") {
    pin(A) { direction: "input"; }
    pin(B) { direction: "input"; }
    pin(X) { direction: "output"; function : "(A) | (B)"; }
  }
  cell ("sky130_fd_sc_hd__or2_4") {
    pin(A) { direction: "input"; }
    pin(B) { direction: "input"; }
    pin(X) { direction: "output"; function : "(A) | (B)"; }
  }
  cell ("sky130_fd_sc_hd__lpflow_inputiso1p_1") {
    pin(A) { direction: "input"; }
    pin(SLEEP) { direction: "input"; }
    pin(X) { direction: "output"; function : "(A) | (SLEEP)"; }
  }
  cell ("sky130_fd_sc_hd__o21a_1") {
    pin(A1) { direction: "input"; }
    pin(A2) { direction: "input"; }
    pin(B1) { direction: "input"; }
    pin(X) { direction: "output"; function : "(A1&B1) | (A2&B1)"; }
  }
  cell ("sky130_fd_sc_hd__o21a_4") {
    pin(A1) { direction: "input"; }
    pin(A2) { direction: "input"; }
    pin(B1) { direction: "input"; }
    pin(X) { direction: "output"; function : "(A1&B1) | (A2&B1)"; }
  }
  cell ("sky130_fd_sc_hd__dfxtp_1") {
    pin(CLK) { direction: "input"; }
    pin(D) { direction: "input"; }
    pin(Q) { direction: "output"; }
  }
}
"""

MAPPED_SAMPLE = """\
module s382(CK, CLR, UC_8, UC_9, UC_10, UC_16, UC_17, UC_18);
  sky130_fd_sc_hd__dfxtp_1 DFF_20/_0_ (.CLK(CK), .D(G11), .Q(TCOMB));
  sky130_fd_sc_hd__o21a_1 _070_ (.A1(TESTL), .A2(_011_), .B1(_022_), .X(_023_));
  sky130_fd_sc_hd__lpflow_inputiso1p_1 _071_ (.A(CLR), .SLEEP(_023_), .X(_024_));
  sky130_fd_sc_hd__o21a_1 _075_ (.A1(UC_16), .A2(_026_), .B1(_024_), .X(UC_16VD));
endmodule
"""


class ParseLibertyTest(unittest.TestCase):
    def test_parse_or2(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        cell = lib["sky130_fd_sc_hd__or2_1"]
        self.assertEqual(cell.family, "or2")
        self.assertEqual(cell.size, 1)
        self.assertEqual(cell.output_pin, "X")
        self.assertEqual(set(cell.input_pins), {"A", "B"})

    def test_parse_lpflow(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        cell = lib["sky130_fd_sc_hd__lpflow_inputiso1p_1"]
        self.assertEqual(cell.output_pin, "X")
        self.assertEqual(set(cell.input_pins), {"A", "SLEEP"})

    def test_parse_skips_dff_without_function(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        cell = lib["sky130_fd_sc_hd__dfxtp_1"]
        self.assertEqual(cell.function, "")
        self.assertEqual(cell.output_pin, "Q")


class EquivalenceCandidatesTest(unittest.TestCase):
    def test_inputiso_to_or2_pin_map(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        src = lib["sky130_fd_sc_hd__lpflow_inputiso1p_1"]
        cands = equivalence_candidates(src, lib)
        by_type = {t: pm for t, pm in cands}
        self.assertIn("sky130_fd_sc_hd__or2_1", by_type)
        # SLEEP maps onto or2's B pin (same variable slot)
        self.assertEqual(by_type["sky130_fd_sc_hd__or2_1"]["SLEEP"], "B")
        self.assertEqual(by_type["sky130_fd_sc_hd__or2_1"]["A"], "A")

    def test_same_family_other_sizes_are_candidates(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        src = lib["sky130_fd_sc_hd__o21a_1"]
        cands = equivalence_candidates(src, lib)
        types = {t for t, _ in cands}
        self.assertIn("sky130_fd_sc_hd__o21a_4", types)

    def test_excludes_self(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        src = lib["sky130_fd_sc_hd__or2_1"]
        cands = equivalence_candidates(src, lib)
        types = {t for t, _ in cands}
        self.assertNotIn("sky130_fd_sc_hd__or2_1", types)

    def test_no_candidates_for_unmatched(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        # dfxtp has no function -> no equivalence candidates
        src = lib["sky130_fd_sc_hd__dfxtp_1"]
        self.assertEqual(equivalence_candidates(src, lib), [])


class ApplyRewriteTest(unittest.TestCase):
    def test_rewrite_replaces_type_and_remaps_pins(self):
        lib = parse_liberty_cells(LIBERTY_SAMPLE)
        cands = equivalence_candidates(
            lib["sky130_fd_sc_hd__lpflow_inputiso1p_1"], lib
        )
        by_type = {t: pm for t, pm in cands}
        new = apply_rewrite(
            MAPPED_SAMPLE,
            "_071_",
            "sky130_fd_sc_hd__or2_1",
            by_type["sky130_fd_sc_hd__or2_1"],
        )
        # type replaced
        self.assertIn("sky130_fd_sc_hd__or2_1 _071_", new)
        self.assertNotIn("lpflow_inputiso1p_1 _071_", new)
        # SLEEP connection moved onto B
        self.assertIn(".B(_023_)", new)
        self.assertNotIn(".SLEEP(_023_)", new)
        # other cells untouched
        self.assertIn("sky130_fd_sc_hd__o21a_1 _070_", new)

    def test_rewrite_unknown_instance_noop(self):
        new = apply_rewrite(MAPPED_SAMPLE, "_999_", "sky130_fd_sc_hd__or2_1", {})
        self.assertEqual(new, MAPPED_SAMPLE)


if __name__ == "__main__":
    unittest.main()
