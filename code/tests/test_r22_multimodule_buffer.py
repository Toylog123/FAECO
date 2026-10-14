"""Buffer repair respects Verilog module namespaces; no EDA is executed."""
import re
from pathlib import Path

import pytest

from rseco.buffer_insertion import insert_buffer
from rseco.gate_sizing import parse_mapped_netlist
from rseco.real_wns import build_boundary_closure_checker


HELPER = '''module dff(CK, Q, D);
input CK, D;
output Q;
wire CK;
wire Q;
wire D;
sky130_fd_sc_hd__dfxtp_1 _0_ (.CLK(CK), .D(D), .Q(Q));
endmodule
'''
TOP = '''module top(A, B, Y);
input A, B;
output Y;
wire n;
sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(n));
sky130_fd_sc_hd__and2_1 g2 (.A(n), .B(B), .Y(Y));
endmodule
'''
TRAILER = '''module trailing(I, O);
input I;
output O;
wire I, O;
sky130_fd_sc_hd__buf_1 t1 (.A(I), .X(O));
endmodule
'''


def _modules(text):
    return {name:block for block,name in re.findall(
        r'\b(module\s+(\w+)\b.*?\bendmodule)', text, re.S)}


@pytest.mark.parametrize('parts', [(HELPER, TOP), (TOP, HELPER),
                                    (HELPER, TOP, TRAILER)])
def test_unique_instance_infers_own_module_and_preserves_other_modules(parts):
    original = '\n'.join(parts)
    result = insert_buffer(original, 'g2', 'B', 'sky130_fd_sc_hd__buf_1', 'new_B')
    before, after = _modules(original), _modules(result)
    assert set(before) == set(after)
    assert all(before[name] == after[name] for name in before if name != 'top')
    top = after['top']
    assert 'wire new_B;' in top
    cells = {c.instance:c for c in parse_mapped_netlist(top)}
    assert cells['g2'].pins['B'] == 'new_B'
    assert cells['_bufb_g2_B'].pins == {'A':'B', 'X':'new_B'}
    assert build_boundary_closure_checker()(before['top'], top).status == 'pass'


def test_explicit_top_module_disambiguates_identical_instance_names():
    sibling = TOP.replace('module top', 'module sibling')
    original = HELPER + sibling + TOP
    result = insert_buffer(original, 'g2', 'B', 'sky130_fd_sc_hd__buf_1', 'new_B',
                           top_module='top')
    before, after = _modules(original), _modules(result)
    assert after['dff'] == before['dff'] and after['sibling'] == before['sibling']
    assert '.B(new_B)' in after['top'] and '_bufb_g2_B' in after['top']


def test_repeated_instance_without_target_module_fails_closed():
    sibling = TOP.replace('module top', 'module sibling')
    with pytest.raises(ValueError, match='ambiguous|multiple'):
        insert_buffer(HELPER + TOP + sibling, 'g2', 'B', 'sky130_fd_sc_hd__buf_1', 'new_B')


@pytest.mark.parametrize('top', ['absent', 'dff'])
def test_explicit_top_never_falls_back_to_instance_in_another_module(top):
    with pytest.raises(ValueError):
        insert_buffer(HELPER + TOP, 'g2', 'B', 'sky130_fd_sc_hd__buf_1', 'new_B',
                      top_module=top)


def test_duplicate_target_module_fails_closed():
    with pytest.raises(ValueError):
        insert_buffer(TOP + TOP, 'g2', 'B', 'sky130_fd_sc_hd__buf_1', 'new_B',
                      top_module='top')


@pytest.mark.parametrize('circuit,instance,pin', [('s27','_11_','A2'),
                                                ('s382','_073_','B1_N')])
def test_real_failed_pilot_input_preserves_dff_helper_and_closes_target(
    circuit, instance, pin,
):
    root = Path(__file__).resolve().parents[2]
    path = root/'experiments/20261014_r22_cut_ablation/inputs'/circuit/'mapped.v'
    if not path.is_file():
        pytest.skip('Archived pilot input absent; portable module namespace probes still run')
    original = path.read_text(encoding='utf-8')
    before = _modules(original)
    result = insert_buffer(original, instance, pin, 'sky130_fd_sc_hd__buf_1',
                           'pilot_buf_probe', top_module=circuit)
    after = _modules(result)
    assert after['dff'] == before['dff']
    cells = {c.instance:c for c in parse_mapped_netlist(after[circuit])}
    assert cells[instance].pins[pin] == 'pilot_buf_probe'
    assert cells['_bufb_' + instance + '_' + pin].pins['X'] == 'pilot_buf_probe'
    assert build_boundary_closure_checker()(before[circuit], after[circuit]).status == 'pass'
