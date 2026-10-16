"""Sequential G preserves state, event/control, output and named-pin roles."""
from pathlib import Path

import pytest

from rseco.logic_rewrite import parse_liberty_cells
from rseco.real_wns import build_real_equivalence_checker

LIB = (Path(__file__).resolve().parents[2] / 'data/raw/benchmarks/raw/'
       'openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/'
       'lib/sky130_fd_sc_hd__tt_025C_1v80.lib')


def _top(cell, bindings=None):
    bindings = bindings or {}
    ins = sorted({bindings.get(pin, pin) for pin in cell.input_pins})
    outs = sorted(cell.output_functions)
    pins = ', '.join(f'.{pin}({bindings.get(pin,pin)})'
                     for pin in dict.fromkeys(cell.input_pins + outs))
    return ('module top(' + ','.join(ins+outs) + ');\n'
            + 'input ' + ','.join(ins) + ';\noutput ' + ','.join(outs)
            + ';\n' + cell.name + ' g (' + pins + ');\nendmodule\n')


@pytest.fixture(scope='module')
def actual():
    text = LIB.read_text(encoding='utf-8')
    return text, parse_liberty_cells(text)


def test_actual_reset_to_set_rejected_despite_same_IQ_output(actual):
    text, cells = actual
    original = _top(cells['sky130_fd_sc_hd__dfrtp_1'])
    candidate = _top(cells['sky130_fd_sc_hd__dfstp_1'], {'SET_B':'RESET_B'})
    for gold, gate in ((original,candidate),(candidate,original)):
        result = build_real_equivalence_checker(text, top_module='top')(gold,gate)
        assert result.status == 'fail', result


def test_all_actual_sequential_same_family_sizes_remain_legal(actual):
    text, cells = actual
    checker = build_real_equivalence_checker(text, top_module='top')
    groups = {}
    for cell in cells.values():
        if cell.sequential_kind:
            groups.setdefault(cell.family,[]).append(cell)
    pairs = 0
    for group in groups.values():
        group.sort(key=lambda cell:cell.size)
        for target in group[1:]:
            result = checker(_top(group[0]),_top(target))
            assert result.status == 'pass', (group[0].name,target.name,result)
            pairs += 1
    assert pairs >= 20


def _cell(size, *, body=None, group='ff', output='IQ', inputs=('CLK','D','EN')):
    if body is None:
        body = 'next_state : "D"; clocked_on : "CLK";'
    pins = ''.join(f'pin ("{pin}") {{ direction : "input"; }}' for pin in inputs)
    return (f'cell ("sky130_fd_sc_hd__testseq_{size}") {{ {pins}'
            f'pin ("Q") {{ direction : "output"; function : "{output}"; }}'
            + (f'{group} ("IQ", "IQ_N") {{ {body} }}' if group else '') + '}')


@pytest.mark.parametrize('changed', [
    {'body':'next_state : "D"; clocked_on : "!CLK";'},
    {'body':'next_state : "D&EN"; clocked_on : "CLK";'},
    {'body':'next_state : "!D"; clocked_on : "CLK";'},
    {'body':'next_state : "D"; clocked_on : "CLK"; clear : "!EN";'},
    {'body':'next_state : "D"; clocked_on : "CLK"; preset : "!EN";'},
    {'group':'latch','body':'next_state : "D"; enable : "CLK";'},
    {'output':'IQ_N'},
    {'body':'next_state : "D"; clocked_on : "CLK"; clear_preset_var1 : "H";'},
])
def test_same_family_different_sequential_semantics_rejected(changed):
    text = _cell(1) + _cell(2,**changed)
    cells = parse_liberty_cells(text)
    original,candidate = [_top(cells[f'sky130_fd_sc_hd__testseq_{i}']) for i in (1,2)]
    for gold,gate in ((original,candidate),(candidate,original)):
        assert build_real_equivalence_checker(text,top_module='top')(gold,gate).status == 'fail'


def test_sequential_and_combinational_cells_cannot_share_only_output_function():
    text = _cell(1,output='D') + _cell(2,group='',output='D')
    cells=parse_liberty_cells(text)
    pair=[_top(cells[f'sky130_fd_sc_hd__testseq_{i}']) for i in (1,2)]
    for gold,gate in (pair,pair[::-1]):
        assert build_real_equivalence_checker(text,top_module='top')(gold,gate).status=='fail'


@pytest.mark.parametrize('bindings', [{'CLK':'D','D':'CLK'}, {'EN':'D','D':'EN'}])
def test_same_family_sequential_size_cannot_swap_input_roles(bindings):
    text = _cell(1) + _cell(2)
    cells=parse_liberty_cells(text)
    original=_top(cells['sky130_fd_sc_hd__testseq_1'])
    candidate=_top(cells['sky130_fd_sc_hd__testseq_2'],bindings)
    assert build_real_equivalence_checker(text,top_module='top')(original,candidate).status=='fail'


def test_identical_unknown_extra_state_control_is_preserved_by_legal_G():
    body='next_state : "D"; clocked_on : "CLK"; clear_preset_var1 : "H";'
    text = _cell(1,body=body)+_cell(2,body=body)
    cells=parse_liberty_cells(text)
    result=build_real_equivalence_checker(text,top_module='top')(
        _top(cells['sky130_fd_sc_hd__testseq_1']),_top(cells['sky130_fd_sc_hd__testseq_2']))
    assert result.status=='pass',result
