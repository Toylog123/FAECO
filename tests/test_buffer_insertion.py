"""Tests for buffer insertion (strategy B of failure-aware hybrid repair)."""

from rseco.buffer_insertion import (
    build_net_fanout,
    buffer_candidates,
    insert_buffer,
)
from rseco.gate_sizing import parse_mapped_netlist


NETLIST = """
module s382(CK, Q);
  input CK;
  output Q;
  wire _00_;
  wire _01_;
  sky130_fd_sc_hd__dfxtp_1 _0_ (
    .CLK(CK),
    .D(_01_),
    .Q(Q)
  );
  sky130_fd_sc_hd__o21a_1 _070_ (
    .A1(_00_),
    .A2(_00_),
    .B1(_01_),
    .X(_01_)
  );
  sky130_fd_sc_hd__buf_1 _buf_ (
    .A(_00_),
    .X(_01_)
  );
endmodule
"""


def test_fanout_map_counts_sinks():
    cells = parse_mapped_netlist(NETLIST)
    fanout = build_net_fanout(cells, output_pins={"X", "Q"})
    # _00_ sinks: _070_.A1, _070_.A2, _buf_.A (no outputs on this net)
    assert len(fanout["_00_"]) == 3
    # _01_ sinks: _0_.D, _070_.B1 (X outputs excluded)
    assert len(fanout["_01_"]) == 2
    assert "_070_.A1" in fanout["_00_"]


def test_buffer_candidates_skips_outputs_and_low_fanout():
    cells = parse_mapped_netlist(NETLIST)
    fanout = build_net_fanout(cells, output_pins={"X", "Q"})
    cands = buffer_candidates(cells, "_070_", fanout, output_pins={"X"})
    pins = {(c[0], c[2]) for c in cands}
    assert ("A1", "sky130_fd_sc_hd__buf_1") in pins
    assert ("A2", "sky130_fd_sc_hd__buf_1") in pins
    # B1 is an input on a fanout-2 net -> candidate
    assert ("B1", "sky130_fd_sc_hd__buf_1") in pins
    # X is the output pin -> skipped
    assert all(c[0] != "X" for c in cands)


def test_buffer_candidates_respect_min_fanout():
    cells = parse_mapped_netlist(NETLIST)
    fanout = build_net_fanout(cells, output_pins={"X", "Q"})
    cands = buffer_candidates(cells, "_070_", fanout, min_fanout=4)
    assert cands == []


def test_insert_buffer_reconnects_pin_and_adds_instance():
    out = insert_buffer(NETLIST, "_070_", "A1", "sky130_fd_sc_hd__buf_1", "_00___buf")
    cells = parse_mapped_netlist(out)
    u070 = next(c for c in cells if c.instance == "_070_")
    assert u070.pins["A1"] == "_00___buf"
    buf = next(c for c in cells if c.instance == "_bufb__070__A1")
    assert buf.cell_type == "sky130_fd_sc_hd__buf_1"
    assert buf.pins == {"A": "_00_", "X": "_00___buf"}
    assert "wire _00___buf;" in out


def test_insert_buffer_unknown_instance_noop():
    out = insert_buffer(NETLIST, "_nope_", "A1", "sky130_fd_sc_hd__buf_1", "x")
    assert out == NETLIST

