"""Parser regression: assign aliases (Yosys wire renaming)."""

from __future__ import annotations

from rseco.netlist import parse_verilog_netlist


def _parse(text: str):
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "n.v"
        p.write_text(text, encoding="utf-8")
        return parse_verilog_netlist(p)


def test_assign_aliases_resolve_logic_levels() -> None:
    v = """module top(A, B, Y);
  input A, B;
  output Y;
  wire n1, x1;
  nand u1 (n1, A, B);
  assign x1 = n1;
  assign Y = x1;
endmodule
"""
    net = _parse(v)
    assert net.gate_count == 1
    assert net.logic_level("Y") == 1
    assert net.logic_level("n1") == 1


def test_yosys_sky130_assign_chain() -> None:
    """Real Yosys liberty output: cells plus alias assignments."""
    v = """module top(N1, N2, N3, N22, N23);
  input N1, N2, N3;
  output N22, N23;
  wire _00_, _01_, _02_, _05_, _06_, _07_, _18_, _19_;
  sky130_fd_sc_hd__nand2_1 _20_ (.A(_02_), .B(_03_), .Y(_05_));
  sky130_fd_sc_hd__o21a_1 _21_ (.A(_04_), .B(_01_), .C(_05_), .X(_07_));
  sky130_fd_sc_hd__a22o_1 _22_ (.A(_02_), .B(_00_), .C(_05_), .D(_01_), .X(_06_));
  assign _03_ = N3;
  assign _01_ = N2;
  assign _02_ = N3;
  assign _00_ = N1;
  assign _04_ = N3;
  assign _19_ = _07_;
  assign _18_ = _06_;
  assign N23 = _19_;
  assign N22 = _18_;
endmodule
"""
    net = _parse(v)
    assert net.gate_count == 3
    # gate inputs normalized through aliases: _02_ -> N3
    nand = next(g for g in net.gates if g.gate_type.endswith("nand2_1"))
    assert set(nand.inputs) == {"N3"}
    # alias chain N22 -> _18_ -> _06_ resolves
    assert net.logic_level("N22") == net.logic_level("_06_")
