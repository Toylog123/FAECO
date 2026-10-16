import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / 'project_docs/evidence/r22_b_model_audit_20261016/x_identity_certificate.py'
if CHECKER.exists():
    spec = importlib.util.spec_from_file_location('x_identity_certificate', CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    certify = module.certify_pair
else:
    def certify(*args):
        return {'certified': False, 'reason': 'checker not implemented'}

BASE = "module top(Y); output [3:0] Y; wire [3:0] Y; assign Y = 4'bxxxx; endmodule"
DEAD = "module top(A,Y); input A; output Y; wire [3:0] n; assign n = 4'hx; assign Y = A; endmodule"

@pytest.mark.parametrize('text', [BASE, DEAD, "module top(Y); output Y; assign Y = 'x; endmodule", r"module top(Y); output Y; wire [31:0] \cpuregs[0] ; assign \cpuregs[0] = 32'hxxxxxxxx; assign Y = 1'b0; endmodule"])
def test_isolated_all_x_sources(text):
    result = certify(text, text)
    assert result['certified'], result
    assert len(result['sources']) == 1

@pytest.mark.parametrize('suffix', [
    'assign Y = n[0];', 'assign Y = {n[0]};', 'assign other = n;',
    'sky130_fd_sc_hd__buf_1 g(.A(n),.X(Y));',
    'always @(*) Y = n[0];', 'initial Y = n[0];',
    'assign n[0] = 1\'b0;', 'buf g(Y,n[0]);',
    'assign Y = \\n ;',
])
def test_consumers_and_extra_drivers_rejected(suffix):
    text = DEAD.replace('assign Y = A;', suffix)
    assert not certify(text,text)['certified']

@pytest.mark.parametrize('gate', [
    BASE.replace('[3:0]', '[7:0]'), BASE.replace("4'bxxxx", "4'b0000"),
    BASE.replace("4'bxxxx", "4'bxxx0"), BASE.replace('output [3:0]', 'input [3:0]'),
    BASE.replace('wire [3:0]', 'wire signed [3:0]'),
    BASE.replace('assign Y', 'assign {Y}'), BASE.replace('assign Y', 'assign Y[3:0]'),
])
def test_changed_source_declaration_or_rhs_rejected(gate):
    assert not certify(BASE,gate)['certified']

@pytest.mark.parametrize('text', [
    "module top(Y); output Y; wire n; assign n = 1'bx; assign Y = n; endmodule",
    "module top(Y); output reg Y; initial Y = 1'bx; endmodule",
    "module top(Y); output Y; buf g(Y,1'bx); endmodule",
    "module top(Y); output Y; parameter P=1'bx; assign Y=P; endmodule",
    "module top(Y); output Y; assign Y=4'bxx01; endmodule",
    "module top(Y); output Y; assign Y=1'bz; endmodule",
    '`include "hidden.v"\n'+BASE,
    BASE.replace('endmodule', 'garbage; endmodule'),
    BASE.replace('wire [3:0] Y;', 'tri [3:0] Y;'),
    BASE.replace('assign Y', 'assign #1 Y'),
])
def test_unsupported_or_nonassign_x_rejected(text):
    assert not certify(text,text)['certified']

def test_escaped_x_consumer_rejected():
    text = r"module top(Y); output Y; wire [31:0] \cpuregs[0] ; assign \cpuregs[0] = 32'hxxxxxxxx; assign Y = \cpuregs[0] [0]; endmodule"
    assert not certify(text,text)['certified']

def test_namespace_isolation_and_escaped_plain_name_equivalence():
    text = DEAD + ' module helper(n,Y); input n; output Y; assign Y=n; endmodule'
    assert certify(text,text)['certified']
    text = DEAD.replace('assign Y = A;', r'assign Y = \n ;')
    assert not certify(text,text)['certified']

def test_no_x_certificate_is_explicitly_empty():
    text = "module top(A,Y); input A; output Y; assign Y=A; endmodule"
    result=certify(text,text)
    assert result['certified'], result
    assert result['sources'] == []

@pytest.mark.parametrize('extra', ["assign 1'b0 = A;", 'assign A+Y = A;', "assign A=1'b2;", "assign A=0'bx;", "assign A=4'dxx;"])
def test_unknown_or_invalid_syntax_never_certifies(extra):
    text=DEAD.replace('assign Y = A;',extra)
    assert not certify(text,text)['certified']

def test_helper_x_output_escapes_module_boundary():
    text="module top(Y); output Y; helper g(.Y(Y)); endmodule module helper(Y); output Y; assign Y=1'bx; endmodule"
    assert not certify(text,text)['certified']

def test_escaped_brackets_are_identifier_not_select():
    text=r"module top(Y); output Y; wire [31:0] \cpuregs[0] ; wire [31:0] \cpuregs[1] ; assign \cpuregs[0] = 32'hxxxxxxxx; assign Y = \cpuregs[1] [0]; endmodule"
    result=certify(text,text)
    assert result['certified'], result
    assert result['sources'][0]['lhs']=='cpuregs[0]'
