"""Physical cell discovery cannot depend on Verilog line wrapping."""
import pytest

from rseco.gate_sizing import parse_mapped_netlist


INV = "sky130_fd_sc_hd__inv_1"
BUF = "sky130_fd_sc_hd__buf_1"


def test_single_line_inv_to_buf_counterexample_is_visible():
    gold = "module top(A,Y); input A; output Y; " + INV + " u(.A(A),.Y(Y)); endmodule"
    gate = gold.replace(INV, BUF).replace(".Y(Y)", ".X(Y)")
    assert [(c.instance, c.cell_type, c.pins) for c in parse_mapped_netlist(gold)] == [
        ("u", INV, {"A": "A", "Y": "Y"})]
    assert [(c.instance, c.cell_type, c.pins) for c in parse_mapped_netlist(gate)] == [
        ("u", BUF, {"A": "A", "X": "Y"})]


@pytest.mark.parametrize("separator", [" ", "\n", "\r\n", "/* next */", "\n//next\n"])
def test_multiple_physical_statements_after_semicolon(separator):
    text = "module top(A,Y); " + INV + " first(.A(A),.Y(n));" + separator + BUF + " second(.A(n),.X(Y)); endmodule"
    assert [c.instance for c in parse_mapped_netlist(text)] == ["first", "second"]


@pytest.mark.parametrize("name", ["$inst", "u$inst", "_u$2", r"\u$[0]"])
def test_dollar_and_escaped_instance_names(name):
    text = f"module top(A,Y); {INV} {name} (.A(A),.Y(Y)); endmodule"
    assert [c.instance for c in parse_mapped_netlist(text)] == [name]


@pytest.mark.parametrize("noise", [
    "// " + INV + " fake(.A(a),.Y(b));\n",
    "/* before\n" + INV + " fake(.A(a),.Y(b));\n*/",
    'initial $display("' + INV + ' fake(.A(a),.Y(b));");',
    'initial $display("escaped \\\" ' + INV + ' fake(.A(a),.Y(b));");',
    "(* " + INV + " fake(.A(a),.Y(b)); *)",
    '(* note="*)", payload="' + INV + ' fake(.A(a),.Y(b));" *)',
    '(* note="/* *) */", /* embedded *) comment */ payload="safe" *)',
])
def test_comments_strings_attributes_never_create_fake_cells(noise):
    text = "module top(A,Y);\n" + noise + "\n" + BUF + " real(.A(A),.X(Y)); endmodule"
    assert [c.instance for c in parse_mapped_netlist(text)] == ["real"]


@pytest.mark.parametrize("raw, expected", [
    (r"\plain ", "plain"),
    ("\\tail\\ ", "tail\\"),
    ("\\middle\\name ", "middle\\name"),
    ("\\\\two ", "\\two"),
    (r"\net//comment ", "net//comment"),
    (r'\net"quote ', 'net"quote'),
    (r"\net);punct ", "net);punct"),
])
def test_escaped_net_removes_only_one_syntax_backslash(raw, expected):
    text = f"module top(Y); {BUF} u (.A({raw}), .X(Y)); endmodule"
    cells = parse_mapped_netlist(text)
    assert len(cells) == 1
    assert cells[0].pins == {"A": expected, "X": "Y"}


def test_multiline_pin_spacing_and_empty_output_are_preserved():
    text = f"""module top(A);
    {BUF} u (
      .A ( /* note */ A ),
      .X ()
    );
    endmodule"""
    assert parse_mapped_netlist(text)[0].pins == {"A": "A", "X": ""}


def test_duplicate_physical_instances_remain_visible_as_duplicate_records():
    text = f"module top(A,Y); {INV} u(.A(A),.Y(n)); {BUF} u(.A(n),.X(Y)); endmodule"
    cells = parse_mapped_netlist(text)
    assert [c.instance for c in cells] == ["u", "u"]
    assert [c.cell_type for c in cells] == [INV, BUF]


def test_comments_between_type_and_instance_or_inside_pins_are_whitespace():
    text = f"module top(A,Y); {BUF} /* instance */ u(.A(/* net */ A),.X(Y /* end */)); endmodule"
    assert parse_mapped_netlist(text)[0].pins == {"A": "A", "X": "Y"}
