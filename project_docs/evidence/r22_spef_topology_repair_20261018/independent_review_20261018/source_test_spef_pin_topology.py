"""Counterexamples for actual pin roles and complete parasitic connectivity."""
from pathlib import Path
import re
import pytest
from rseco.spef import parse_mapped_verilog, build_spef

LIB='''library (tiny) {
cell ("sky130_fd_sc_hd__ha_1") {
 pin ("A") { direction : input; } pin ("B") { direction : input; }
 pin ("SUM") { direction : output; function : "A^B"; }
 pin ("COUT") { direction : output; function : "A&B"; }
}
cell ("sky130_fd_sc_hd__buf_1") {
 pin ("A") { direction : input; } pin ("X") { direction : output; function : "A"; }
}
cell ("sky130_fd_sc_hd__custom_1") {
 pin ("Y") { direction : input; } pin ("Q_N") { direction : output; function : "!Y"; }
}
}'''

def parsed(tmp_path, text, **kw):
    p=tmp_path/'mapped.v';p.write_text(text,encoding='utf-8')
    return parse_mapped_verilog(p, liberty_text=LIB, **kw)

def test_existing_port_api_must_not_replace_cell_pins_with_repeated_ports(tmp_path):
    p=tmp_path/'port.v'
    p.write_text('module top(A,Z);\ninput A; output Z;\n'
        'sky130_fd_sc_hd__buf_1 b1 (.A(A),.X(n));\n'
        'sky130_fd_sc_hd__buf_1 b2 (.A(A),.X(Z));\nendmodule',encoding='utf-8')
    spef=build_spef(parse_mapped_verilog(p))
    section=spef.split('*D_NET A ',1)[1].split('*END',1)[0]
    assert section.count('*P A I')==1
    assert '*I b1:A I' in section and '*I b2:A I' in section

def test_actual_multioutput_roles_and_input_named_y(tmp_path):
    nl=parsed(tmp_path,'''module top(input A, input B, output Z);
    wire s,c,n;
    sky130_fd_sc_hd__ha_1 h (.A(A),.B(B),.SUM(s),.COUT(c));
    sky130_fd_sc_hd__custom_1 f (.Y(s),.Q_N(n));
    sky130_fd_sc_hd__buf_1 b (.A(n),.X(Z)); endmodule''')
    assert nl.nets['s'].driver()==('h','SUM')
    assert nl.nets['c'].driver()==('h','COUT')
    assert nl.nets['n'].driver()==('f','Q_N')
    spef=build_spef(nl)
    assert '*I h:SUM O' in spef and '*I f:Y I' in spef
    assert re.search(r'^\d+ h:SUM f:Y ',spef,re.M)

def test_port_net_keeps_one_port_and_all_instance_connections(tmp_path):
    nl=parsed(tmp_path,'''module top(A,Z); input A; output Z; wire t;
    sky130_fd_sc_hd__buf_1 b1 (.A(A),.X(t));
    sky130_fd_sc_hd__buf_1 b2 (.A(A),.X(Z)); endmodule''')
    spef=build_spef(nl)
    section=spef.split('*D_NET A ',1)[1].split('*END',1)[0]
    assert section.count('*P A I')==1
    assert '*I b1:A I' in section and '*I b2:A I' in section
    assert re.search(r'^\d+ A b1:A ',section,re.M)
    assert re.search(r'^\d+ A b2:A ',section,re.M)

def test_vectors_and_aliases_preserve_port_endpoints(tmp_path):
    nl=parsed(tmp_path,'''module top(A,Z); input [1:0] A; output Z;
    wire a2; assign a2 = A[1];
    sky130_fd_sc_hd__buf_1 b (.A(a2),.X(Z)); endmodule''')
    spef=build_spef(nl)
    assert nl.ports==['A[0]','A[1]','Z']
    assert '*P A[1] I' in spef and '*I b:A I' in spef
    assert re.search(r'^\d+ A\[1\] b:A ',spef,re.M)
    assert '*D_NET a2 ' not in spef

def test_top_and_wrapper_roles_come_from_module_declarations(tmp_path):
    nl=parsed(tmp_path,'''module helper(D,Q_N); input D; output Q_N;
    sky130_fd_sc_hd__custom_1 ff (.Y(D),.Q_N(Q_N)); endmodule
    module top(input A, output Z); wire n;
    helper h (.D(A),.Q_N(n)); sky130_fd_sc_hd__buf_1 b (.A(n),.X(Z)); endmodule''',top_module='top')
    assert nl.module_name=='top'
    assert nl.nets['n'].driver()==('h','Q_N')
    assert '*I h:Q_N O' in build_spef(nl)

@pytest.mark.parametrize('body',[
    'sky130_fd_sc_hd__unknown_1 u (.A(A),.X(Z));',
    'sky130_fd_sc_hd__buf_1 u (.A(A),.BOGUS(Z));',
    'sky130_fd_sc_hd__buf_1 u (.A(A),.A(A),.X(Z));',
    'sky130_fd_sc_hd__buf_1 u (A,Z);',
    'sky130_fd_sc_hd__buf_1 u (.A(A&1\'b1),.X(Z));',
    'sky130_fd_sc_hd__buf_1 u (.A(A),.X(Z)); sky130_fd_sc_hd__buf_1 v (.A(A),.X(Z));',
])
def test_unsupported_or_ambiguous_connectivity_rejected(tmp_path,body):
    with pytest.raises(ValueError):
        nl=parsed(tmp_path,'module top(input A, output Z); '+body+' endmodule')
        build_spef(nl)

def test_ambiguous_top_requires_explicit_selection(tmp_path):
    text='module a(input X); endmodule module b(input Y); endmodule'
    with pytest.raises(ValueError,match='top|Top'):
        parsed(tmp_path,text)
    assert parsed(tmp_path,text,top_module='b').module_name=='b'

def test_unused_constant_alias_does_not_block_real_mapped_inputs(tmp_path):
    nl=parsed(tmp_path,"module top(input A,output Z); wire unused; assign unused=1'h1; "
        'sky130_fd_sc_hd__buf_1 b (.A(A),.X(Z)); endmodule')
    assert '*D_NET unused' not in build_spef(nl)

def test_connected_constant_alias_requires_a_physical_source(tmp_path):
    with pytest.raises(ValueError,match='constant|Constant'):
        build_spef(parsed(tmp_path,"module top(output Z); wire t; assign t=1'b1; "
            'sky130_fd_sc_hd__buf_1 b (.A(t),.X(Z)); endmodule'))

@pytest.mark.parametrize('text',[
    'module top(A,Z); input A; sky130_fd_sc_hd__buf_1 b (.A(A),.X(Z)); endmodule',
    'module top(input A,output Z); sky130_fd_sc_hd__buf_1 b (.A(A).X(Z)); endmodule',
])
def test_incomplete_ports_and_malformed_named_pin_separators_rejected(tmp_path,text):
    with pytest.raises(ValueError):
        parsed(tmp_path,text)
