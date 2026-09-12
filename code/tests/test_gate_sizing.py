"""Tests for gate sizing core logic (strategy G of failure-aware hybrid repair)."""

from __future__ import annotations

import unittest


from rseco.gate_sizing import (
    apply_sizing,
    build_available_sizes,
    critical_gates,
    larger_size_candidates,
    parse_mapped_netlist,
)


SAMPLE = """\
module s27(CK, G0, G1, G17, G2, G3);
  sky130_fd_sc_hd__dfxtp_1 _0_ (.CLK(CK), .D(G11), .Q(G5));
  sky130_fd_sc_hd__nor2_1 _04_ (.A(G0), .B(G1), .Y(G6));
  sky130_fd_sc_hd__nor2_1 _05_ (.A(G5), .B(G6), .Y(G17));
endmodule
"""

LIBERTY_SAMPLE = """\
library(min) {
  cell ("sky130_fd_sc_hd__nor2_1") { pin(Y) { direction: "output"; } }
  cell ("sky130_fd_sc_hd__nor2_2") { pin(Y) { direction: "output"; } }
  cell ("sky130_fd_sc_hd__nor2_4") { pin(Y) { direction: "output"; } }
  cell ("sky130_fd_sc_hd__dfxtp_1") { pin(Q) { direction: "output"; } }
}
"""


class ParseNetlistTest(unittest.TestCase):
    def test_parse_mapped_netlist(self):
        cells = parse_mapped_netlist(SAMPLE)
        self.assertEqual(len(cells), 3)
        dff = cells[0]
        self.assertTrue(dff.is_dff)
        self.assertEqual(dff.function, "dfxtp")
        nor = cells[1]
        self.assertEqual(nor.function, "nor2")
        self.assertEqual(nor.size, 1)
        self.assertEqual(nor.pins["A"], "G0")

    def test_critical_gates_finds_deepest(self):
        cells = parse_mapped_netlist(SAMPLE)
        dff_q = {c.pins.get("Q", "") for c in cells if c.is_dff}
        critical = critical_gates(cells, output_ports={"G17"}, dff_q_nets=dff_q)
        # _05_ (drives output G17) is deepest
        self.assertIn("_05_", critical)


class SizingCandidatesTest(unittest.TestCase):
    def test_build_available_sizes(self):
        avail = build_available_sizes(LIBERTY_SAMPLE)
        self.assertEqual(avail["nor2"], {1, 2, 4})

    def test_larger_size_candidates(self):
        avail = {"nor2": {1, 2, 4, 8}}
        cands = larger_size_candidates("sky130_fd_sc_hd__nor2_1", avail)
        self.assertEqual(
            cands,
            ["sky130_fd_sc_hd__nor2_2", "sky130_fd_sc_hd__nor2_4", "sky130_fd_sc_hd__nor2_8"],
        )

    def test_no_larger_size_for_max(self):
        avail = {"nor2": {1, 2, 4, 8}}
        cands = larger_size_candidates("sky130_fd_sc_hd__nor2_8", avail)
        self.assertEqual(cands, [])


class ApplySizingTest(unittest.TestCase):
    def test_apply_sizing_replaces_cell_type(self):
        new = apply_sizing(SAMPLE, {"_05_": "sky130_fd_sc_hd__nor2_4"})
        self.assertIn("sky130_fd_sc_hd__nor2_4 _05_", new)
        self.assertNotIn("sky130_fd_sc_hd__nor2_1 _05_", new)
        # other cells untouched
        self.assertIn("sky130_fd_sc_hd__nor2_1 _04_", new)


if __name__ == "__main__":
    unittest.main()