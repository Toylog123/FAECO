# -*- coding: utf-8 -*-
"""TDD tests for the parasitic-aware SPEF generator (shortboard-1 landing)."""

from pathlib import Path

from rseco.spef import (
    MappedNet,
    build_spef,
    estimate_net_rc,
    parse_mapped_verilog,
    write_spef,
)

MAPPED = """module top(A, Y);
  input A;
  output Y;
  wire n1;
  sky130_fd_sc_hd__inv_1 u0 (.A(A), .Y(n1));
  sky130_fd_sc_hd__buf_2 u1 (.A(n1), .X(Y));
endmodule
"""


def test_parse_mapped_verilog_nets(tmp_path):
    p = tmp_path / "m.v"
    p.write_text(MAPPED, encoding="utf-8")
    nl = parse_mapped_verilog(p)
    assert nl.module_name == "top"
    assert nl.ports == ["A", "Y"]
    assert "n1" in nl.nets
    assert len(nl.instances) == 2


def test_estimate_net_rc_grows_with_fanout():
    net = MappedNet(name="n1", pins=(("u0", "Y"), ("u1", "A")), is_port=False)
    r, c = estimate_net_rc(net, unit_len_um=40.0)
    assert r > 0
    assert c > 0
    heavy = MappedNet(name="n1", pins=(("u0", "Y"), ("u1", "A"), ("u2", "A"), ("u3", "A")))
    r2, c2 = estimate_net_rc(heavy, unit_len_um=40.0)
    assert r2 > r
    assert c2 > c


def test_build_spef_contains_header_and_net(tmp_path):
    p = tmp_path / "m.v"
    p.write_text(MAPPED, encoding="utf-8")
    nl = parse_mapped_verilog(p)
    spef = build_spef(nl, unit_len_um=40.0)
    assert "*SPEF" in spef
    assert "*D_NET" in spef
    assert "*CONN" in spef
    assert "*CAP" in spef
    assert "*RES" in spef


def test_write_spef_roundtrip(tmp_path):
    p = tmp_path / "m.v"
    p.write_text(MAPPED, encoding="utf-8")
    nl = parse_mapped_verilog(p)
    out = write_spef(tmp_path / "m.spef", nl, unit_len_um=40.0)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "*SPEF" in text
