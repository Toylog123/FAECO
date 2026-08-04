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


def test_buffer_candidates_new_net_unique_per_instance_pin():
    cells = parse_mapped_netlist(NETLIST)
    fanout = build_net_fanout(cells, output_pins={"X", "Q"})
    cands = buffer_candidates(cells, "_070_", fanout, output_pins={"X"})
    nets_by_pin = {pin: {c[3] for c in cands if c[0] == pin} for pin in ("A1", "A2", "B1")}
    # different sink pins on the same net get different new nets (no collision)
    assert len(nets_by_pin["A1"]) == 1 and len(nets_by_pin["A2"]) == 1
    assert nets_by_pin["A1"] != nets_by_pin["A2"] != nets_by_pin["B1"]
    a1 = next(iter(nets_by_pin["A1"]))
    assert a1.endswith("__A1")


def test_two_buffers_same_net_keep_single_driver():
    cells = parse_mapped_netlist(NETLIST)
    fanout = build_net_fanout(cells, output_pins={"X", "Q"})
    cands = buffer_candidates(cells, "_070_", fanout, output_pins={"X"})
    a1 = next(c for c in cands if c[0] == "A1")
    a2 = next(c for c in cands if c[0] == "A2")
    out = insert_buffer(NETLIST, "_070_", "A1", a1[2], a1[3])
    out = insert_buffer(out, "_070_", "A2", a2[2], a2[3])
    cells2 = parse_mapped_netlist(out)
    drivers: dict[str, list[str]] = {}
    for c in cells2:
        for pin, net in c.pins.items():
            if pin in ("X", "Y", "Q"):
                drivers.setdefault(net, []).append(c.instance)
    # only the nets created by buffer insertion must be single-driver
    # (the test fixture itself contains a pre-existing multi-driver _01_)
    new_nets = [n for n in drivers if "__buf_" in n]
    assert all(len(drivers[n]) == 1 for n in new_nets)
    assert "_00___buf__070__A1" in new_nets and "_00___buf__070__A2" in new_nets
