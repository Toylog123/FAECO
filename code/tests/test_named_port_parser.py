"""Parser regression: named-port gate instances (Yosys SKY130 style)."""

from __future__ import annotations

import pytest

from rseco.netlist import parse_verilog_netlist


def _parse(text: str):
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "n.v"
        p.write_text(text, encoding="utf-8")
        return parse_verilog_netlist(p)


def test_parses_named_port_multi_line_instance() -> None:
    v = """module top(A, B, C, Y);
  input A, B, C;
  output Y;
  wire n1, n2;
  sky130_fd_sc_hd__nand2_1 u1 (
    .A(A),
    .B(B),
    .Y(n1)
  );
  sky130_fd_sc_hd__inv_1 u2 (
    .A(n1),
    .Y(Y)
  );
endmodule
"""
    net = _parse(v)
    assert net.module_name == "top"
    assert net.inputs == ["A", "B", "C"]
    assert net.outputs == ["Y"]
    assert net.gate_count == 2
    u1 = net.gates[0]
    assert u1.gate_type == "sky130_fd_sc_hd__nand2_1"
    assert u1.name == "u1"
    assert u1.output == "n1"
    assert u1.inputs == ("A", "B")
    u2 = net.gates[1]
    assert u2.output == "Y"
    assert u2.inputs == ("n1",)


def test_parses_named_port_x_output() -> None:
    v = """module top(A1, A2, B1, X);
  input A1, A2, B1;
  output X;
  sky130_fd_sc_hd__o21a_1 u1 (
    .A1(A1),
    .A2(A2),
    .B1(B1),
    .X(X)
  );
endmodule
"""
    net = _parse(v)
    assert net.gate_count == 1
    g = net.gates[0]
    assert g.gate_type == "sky130_fd_sc_hd__o21a_1"
    assert g.output == "X"
    assert g.inputs == ("A1", "A2", "B1")


def test_parses_positional_and_named_mixed() -> None:
    v = """module top(A, B, Y);
  input A, B;
  output Y;
  nand u1 (n1, A, B);
  sky130_fd_sc_hd__inv_1 u2 (.A(n1), .Y(Y));
endmodule
"""
    net = _parse(v)
    assert net.gate_count == 2
    assert net.gates[1].output == "Y"
    assert net.gates[1].inputs == ("n1",)


def test_parses_openroad_style_instance_whose_header_holds_first_connection() -> None:
    """OpenROAD's write_verilog puts the first named connection on the same
    line as the instance header (``... DFF_14  (.D(net),``), so the "line ends
    with (" heuristic does not fire.  Without an explicit multi-line instance
    start the whole netlist parses to zero gates and downstream logic-level
    analysis raises ``KeyError`` for the connected net.
    """
    v = """module top(CK, D, Q, Y);
  input CK;
  input D;
  output Q;
  output Y;
  wire n1;
  sky130_fd_sc_hd__dfxtp_1 DFF_0  (.D(n1),
    .CLK(CK),
    .Q(Q));
  sky130_fd_sc_hd__inv_1 _000_ (.A(D),
    .Y(n1));
  sky130_fd_sc_hd__inv_1 _001_ (.A(n1),
    .Y(Y));
endmodule
"""
    net = _parse(v)
    assert net.gate_count == 3
    by_name = {gate.name: gate for gate in net.gates}
    assert by_name["DFF_0"].gate_type == "sky130_fd_sc_hd__dfxtp_1"
    assert by_name["DFF_0"].inputs == ("n1", "CK")
    assert by_name["_000_"].output == "n1"
    # logic_levels must resolve the net driven by _000_, which is what the
    # analysis netlist path needs.
    assert net.logic_level("n1") == 1
