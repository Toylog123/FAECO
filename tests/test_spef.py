"""Unit tests for parasitic-aware SPEF generation (src/rseco/spef.py)."""

import re
from pathlib import Path

import pytest

from rseco.spef import (
    MappedNet,
    build_spef,
    estimate_net_rc,
    parse_mapped_verilog,
    write_spef,
)


@pytest.fixture
def small_netlist(tmp_path: Path) -> Path:
    v = tmp_path / "top.v"
    v.write_text(
        "module top(CK, A, Y);\n"
        "  input CK; input A; output Y;\n"
        "  sky130_fd_sc_hd__buf_1 u1 (.A(A), .X(n1));\n"
        "  sky130_fd_sc_hd__inv_1 u2 (.A(n1), .Y(Y));\n"
        "  sky130_fd_sc_hd__dfxtp_1 u3 (.CLK(CK), .D(n1), .Q(q1));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    return v


def test_parse_top_module_and_nets(small_netlist: Path):
    nl = parse_mapped_verilog(small_netlist)
    assert nl.module_name == "top"
    assert ("sky130_fd_sc_hd__buf_1", "u1") in nl.instances
    assert "n1" in nl.nets
    assert nl.nets["n1"].driver() == ("u1", "X")
    assert nl.nets["n1"].fanout == 2
    assert nl.ports == ["A", "CK", "Y"]
    assert nl.port_dirs["A"] == "I"
    assert nl.port_dirs["Y"] == "O"


def test_parse_selects_top_when_wrapper_exists(tmp_path: Path):
    v = tmp_path / "multi.v"
    v.write_text(
        "module dff(CK, D, Q);\n"
        "  input CK; input D; output Q;\n"
        "  sky130_fd_sc_hd__dfxtp_1 _0_ (.CLK(CK), .D(D), .Q(Q));\n"
        "endmodule\n"
        "module top(CK, A, Y);\n"
        "  input CK; input A; output Y;\n"
        "  dff f1 (.CK(CK), .D(A), .Q(Y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    nl = parse_mapped_verilog(v)
    assert nl.module_name == "top"
    assert len(nl.instances) == 1
    assert nl.instances[0] == ("dff", "f1")


def test_estimate_rc_scales_with_fanout():
    r0, c0 = estimate_net_rc(MappedNet("n", pins=(("d", "Y"), ("s1", "A"))))
    r1, c1 = estimate_net_rc(MappedNet("n", pins=(("d", "Y"), ("s1", "A"), ("s2", "A"), ("s3", "A"))))
    assert r1 > r0
    assert c1 > c0


def test_build_spef_structure(small_netlist: Path):
    nl = parse_mapped_verilog(small_netlist)
    spef = build_spef(nl)
    assert "*SPEF" in spef
    assert '*DESIGN "top"' in spef
    assert "*PORTS" in spef
    assert "*D_NET n1" in spef
    assert "*I u1:X O" in spef
    assert "*I u2:A I" in spef
    assert "*END" in spef
    assert re.search(r"^A I$", spef, re.M)
    assert re.search(r"^Y O$", spef, re.M)


def test_write_spef_roundtrip(small_netlist: Path, tmp_path: Path):
    nl = parse_mapped_verilog(small_netlist)
    out = write_spef(tmp_path / "top.spef", nl)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "*D_NET n1" in text


def test_skips_pinless_nets(tmp_path: Path):
    v = tmp_path / "top.v"
    v.write_text(
        "module top(A, Y);\n"
        "  input A; output Y;\n"
        "  wire unused;\n"
        "  wire a2;\n"
        "  assign a2 = A;\n"
        "  sky130_fd_sc_hd__buf_1 u1 (.A(a2), .X(Y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    nl = parse_mapped_verilog(v)
    spef = build_spef(nl)
    assert "*D_NET unused" not in spef
