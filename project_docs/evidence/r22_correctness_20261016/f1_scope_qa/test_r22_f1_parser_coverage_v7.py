"""F1 must account for every source SKY instance and every named connection."""
from dataclasses import replace

import pytest

import rseco.real_wns as rw
from rseco.gate_sizing import Cell

LIB = '\n'.join(
    f'cell ("sky130_fd_sc_hd__buf_{size}") {{ '
    'pin ("A") { direction : "input"; } '
    'pin ("X") { direction : "output"; function : "A"; } }'
    for size in (1,2))
MULTI = '''module top(A,Y);
input A;
output Y;
wire N;
sky130_fd_sc_hd__buf_1 first (.A(A),.X(N));
sky130_fd_sc_hd__buf_1 second (.A(N),.X(Y));
endmodule
'''


def _candidate():
    return MULTI.replace('buf_1 first','buf_2 first')


@pytest.mark.parametrize('corrupt', ['empty','missing','extra','type','pin','net','duplicate'])
def test_parser_coverage_corruption_fails_closed(monkeypatch, corrupt):
    real_parser = rw.parse_mapped_netlist
    def broken(text):
        cells = real_parser(text)
        if corrupt=='empty':
            return []
        if corrupt=='missing':
            return cells[1:]
        if corrupt=='extra':
            return cells+[Cell('ghost','sky130_fd_sc_hd__buf_1','buf',1,{'A':'A','X':'Y'})]
        if corrupt=='type':
            return [replace(cell,cell_type='sky130_fd_sc_hd__buf_99') for cell in cells]
        if corrupt=='duplicate':
            return cells+[cells[0]]
        if corrupt=='pin':
            return [replace(cell,pins={key:net for key,net in cell.pins.items() if key!='A'}) for cell in cells]
        return [replace(cell,pins={key:('WRONG' if key=='A' else net) for key,net in cell.pins.items()}) for cell in cells]
    monkeypatch.setattr(rw,'parse_mapped_netlist',broken)
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(MULTI,_candidate())
    assert result.status=='fail',result
    assert 'coverage' in result.reason.lower(),result


def test_original_single_line_legal_G_has_real_parser_coverage():
    original=' '.join(MULTI.splitlines())
    candidate=original.replace('buf_1 first','buf_2 first')
    assert len(rw.parse_mapped_netlist(original))==2
    assert len(rw.parse_mapped_netlist(candidate))==2
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(original,candidate)
    assert result.status=='pass',result


def test_comments_fake_instances_and_dollar_names_do_not_lose_coverage():
    original=MULTI.replace(' first ', ' $first ').replace(' second ', ' mid$second ')
    original=original.replace('input A;', 'input A; // sky130_fd_sc_hd__buf_1 fake(.A(A),.X(Y));\n')
    original=original.replace('wire N;', 'wire N; /* another fake sky130_fd_sc_hd__buf_1 fake(.A(A),.X(Y)); */')
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(original,original.replace('buf_1 $first','buf_2 $first'))
    assert result.status=='pass',result


def test_empty_output_connection_is_preserved_by_coverage():
    original=MULTI.replace('.X(Y)', '.X()')
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(original,original.replace('buf_1 first','buf_2 first'))
    assert result.status=='pass',result


def test_escaped_scalar_cannot_be_confused_with_bus_bitselect():
    original=r'''module top(A,Y);
input [1:0] A;
output Y;
wire \A[0] ;
sky130_fd_sc_hd__buf_1 first (.A(\A[0] ),.X(Y));
endmodule
'''
    candidate=original.replace('buf_1 first','buf_2 first').replace('.A(\\A[0] )','.A(A[0])')
    assert rw.build_real_equivalence_checker(LIB,top_module='top')(original,candidate).status=='fail'


def test_escaped_instance_and_net_are_legal_for_same_G():
    original=MULTI.replace(' first ',r' \first[0] ').replace('wire N;',r'wire \N\ ;')
    original=original.replace('.X(N)',r'.X(\N\ )').replace('.A(N)',r'.A(\N\ )')
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(original,original.replace('buf_1 \\first[0]','buf_2 \\first[0]'))
    assert result.status=='pass',result


def test_comment_like_text_in_escaped_net_is_an_atom():
    original=MULTI.replace('wire N;',r'wire \N//tail ;')
    original=original.replace('.X(N)',r'.X(\N//tail )').replace('.A(N)',r'.A(\N//tail )')
    result=rw.build_real_equivalence_checker(LIB,top_module='top')(original,original.replace('buf_1 first','buf_2 first'))
    assert result.status=='pass',result
