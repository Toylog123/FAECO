"""Tests for netlist sanity checks (multi-driver nets, output-pin coverage)."""

from rseco.netlist_audit import audit_netlist, find_multi_driver_nets


GOOD = """
module s382(CK, Q);
  input CK;
  output Q;
  wire _00_;
  sky130_fd_sc_hd__dfxtp_1 _0_ (
    .CLK(CK),
    .D(_00_),
    .Q(Q)
  );
  sky130_fd_sc_hd__buf_1 _buf_ (
    .A(CK),
    .X(_00_)
  );
endmodule
"""


BAD = """
module s382(CK, Q);
  input CK;
  output Q;
  wire _00_;
  wire _00___buf;
  sky130_fd_sc_hd__dfxtp_1 _0_ (
    .CLK(CK),
    .D(_00___buf),
    .Q(Q)
  );
  sky130_fd_sc_hd__buf_1 _b1_ (
    .A(_00_),
    .X(_00___buf)
  );
  sky130_fd_sc_hd__buf_1 _b2_ (
    .A(_00_),
    .X(_00___buf)
  );
endmodule
"""


def test_find_multi_driver_nets_detects_parallel_buffers():
    multi = find_multi_driver_nets(BAD)
    assert "_00___buf" in multi
    assert len(multi["_00___buf"]) == 2


def test_good_netlist_no_multi_driver():
    assert find_multi_driver_nets(GOOD) == {}


def test_audit_ok_flag():
    assert audit_netlist(GOOD, report=False)["ok"] is True
    assert audit_netlist(BAD, report=False)["ok"] is False
    a = audit_netlist(BAD, report=False)
    assert a["multi_driver_nets"]["_00___buf"] == [("_b1_", "X"), ("_b2_", "X")]


def test_audit_reports_cell_without_output():
    txt = GOOD.replace("    .Q(Q)\n", "")
    a = audit_netlist(txt, report=False)
    assert not a["ok"]
    assert any(inst == "_0_" for inst, _ in a["cells_no_output_pin"])


BUFINV = "'''\nmodule s820(CK, Q);\n  input CK;\n  output Q;\n  wire _00_;\n  sky130_fd_sc_hd__dfxtp_1 _0_ (\n    .CLK(CK),\n    .D(_00_),\n    .Q(Q)\n  );\n  sky130_fd_sc_hd__bufinv_16 _116_ (\n    .A(CK),\n    .Y(_00_)\n  );\nendmodule\n'''"

def test_audit_accepts_bufinv_with_y_output():
    a = audit_netlist(BUFINV, report=False)
    assert a[chr(111)+chr(107)] is True
    assert a[chr(98)+chr(117)+chr(102)+chr(102)+chr(101)+chr(114)+chr(115)+chr(95)+chr(119)+chr(105)+chr(116)+chr(104)+chr(111)+chr(117)+chr(116)+chr(95)+chr(88)] == []
