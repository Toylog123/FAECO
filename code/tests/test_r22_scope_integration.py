"""Counterexamples for scope and multi-output integration, without EDA."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from rseco.graph import extract_fanin_cone
from rseco.netlist import Netlist
from rseco.cut import (build_weighted_cut_graph, _cut_for_selected_gates,
                       _gate_driving_output, split_cone_by_depth, solve_weighted_cut)
from rseco.refinement import RefinementWeights


def _adder_cone(root='Y'):
    add = SimpleNamespace(gate_type='fa', name='add', output='S', inputs=('A','B'),
                          all_outputs=('S','CO'), additional_outputs=('CO',))
    sink = SimpleNamespace(gate_type='buf', name='sink', output='Y', inputs=('CO',),
                           all_outputs=('Y',), additional_outputs=())
    return extract_fanin_cone(Netlist('top',['A','B'],['Y'],['S','CO'],[add,sink]), [root])


def test_secondary_output_is_a_real_fanin_dependency():
    cone = _adder_cone()
    assert cone.gates == ['add','sink']
    graph = build_weighted_cut_graph(cone, RefinementWeights())
    assert ('add:out','sink:in',graph.infinite_capacity) in graph.dependency_edges
    cut = _cut_for_selected_gates(cone, ['add'], method='counterexample')
    assert 'CO' in cut.boundary_outputs


def test_secondary_root_and_split_keep_one_physical_node():
    cone = _adder_cone('CO')
    assert cone.gates == ['add']
    assert _gate_driving_output(cone,'CO') == 'add'
    parts = split_cone_by_depth(_adder_cone(),1)
    assert sum(len(part.gates) for part in parts) == 2
    add_part = next(part for part in parts if 'add' in part.gates)
    assert 'CO' in add_part.boundary_outputs


def _runner():
    path=Path(__file__).resolve().parents[1]/'scripts/run_outerloop_real_wns.py'
    spec=importlib.util.spec_from_file_location('scope_cli_runner',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_initial_endpoint_ignores_same_named_helper_instance(tmp_path,monkeypatch):
    runner=_runner()
    helper='module helper(A,Y);\ninput A;\noutput Y;\ndff shared (.CK(A), .D(helper_d), .Q(Y));\nendmodule\n'
    top='module top(A,Y);\ninput A;\noutput Y;\nwire top_d;\nbuf g1(top_d,A);\ndff shared (.CK(A), .D(top_d), .Q(Y));\nendmodule\n'
    source=tmp_path/'top.v'
    source.write_text(helper+top,encoding='utf-8')
    output=tmp_path/'run'
    (output/'top').mkdir(parents=True)
    (output/'top/mapped.v').write_text(helper+top,encoding='utf-8')
    def baseline(*args,**kwargs):
        (output/'top/sta.log').write_text('',encoding='utf-8')
        return {'wns':-0.1}
    class ReachedEvaluator(Exception):
        pass
    def evaluator(**kwargs):
        config=(output/'top/case/case.yaml').read_text(encoding='utf-8')
        assert 'output: top_d' in config
        raise ReachedEvaluator
    monkeypatch.setattr(runner,'run_opensta',baseline)
    monkeypatch.setattr(runner,'parse_critical_instances',lambda _: ['shared'])
    monkeypatch.setattr(runner,'parse_worst_endpoint',lambda _: 'shared')
    monkeypatch.setattr(runner,'RealWnsEvaluator',evaluator)
    monkeypatch.setattr('sys.argv',['runner','--circuit','top','--source-file',str(source),
                                  '--output-dir',str(output),'--skip-mapping'])
    with pytest.raises(ReachedEvaluator):
        runner.main()


def test_s_refresh_failure_cannot_commit_candidate(tmp_path,monkeypatch):
    from test_flow_structure_resynth import (_make_case, _SOnlyEvaluator,
        _install_s_stubs, _fake_candidate, _functional_ok)
    from rseco.flow import run_multi_iteration_case
    candidate=_fake_candidate()
    candidate.grafted_text='module wrong(A,Y);\ninput A;\noutput Y;\nbuf g(Y,A);\nendmodule\n'
    tools=_install_s_stubs(monkeypatch,candidates=[candidate])
    evaluator=_SOnlyEvaluator([{'improved':True,'wns':-1.2}])
    evaluator.top_module='top'
    evaluator.refresh_cone=True
    result=run_multi_iteration_case(_make_case(tmp_path),max_iterations=2,max_patches=1,
        equivalence_checker=_functional_ok,wns_evaluator=evaluator,structure_resynth=True,
        resynth_tools=tools,structure_out_dir=tmp_path/'s_out')
    assert result['structure_resynth']['accepted'] == 0
    assert result['state']['accepted_patches'] == []
    assert result['state']['current_wns'] == -1.5
    assert any(event['type']=='F2_boundary_invalid'
               for event in result['state']['failure_history'])


def test_independent_sec_ignores_fake_modules_in_comments():
    from test_r22_batch import module
    batch=module()
    top='module top(A,Y);\ninput A;\noutput Y;\nbuf g(Y,A);\nendmodule\n'
    text='// module fake; endmodule\n'+top
    gold,gate,helpers=batch.sec_designs(text,text,'top')
    assert gold == gate
    assert helpers == ''


def test_cone_refresh_uses_real_evaluator_liberty_attribute():
    from rseco.flow import _refreshed_candidate_cone
    evaluator=SimpleNamespace(top_module='top',lib={
        'dual':SimpleNamespace(output_functions={'P':'A','R':'A'})})
    text='module top(A,Y,Z);\ninput A;\noutput Y,Z;\ndual g(.A(A),.P(Y),.R(Z));\nendmodule\n'
    cone=_refreshed_candidate_cone(text,evaluator,'Z')
    assert cone.gates == ['g']
    assert cone.signal_drivers()['Z'] == 'g'


def test_zero_input_cell_is_a_source_node():
    from rseco.netlist import Gate
    netlist=Netlist('top',[],['Y'],['T'],[
        Gate('tie','tie','T',()),Gate('buf','sink','Y',('T',))])
    cone=extract_fanin_cone(netlist,['Y'])
    result=solve_weighted_cut(cone,build_weighted_cut_graph(cone,RefinementWeights()))
    assert result.selected_gates


def test_alias_root_retains_its_physical_driver():
    from rseco.flow import _refreshed_candidate_cone
    evaluator=SimpleNamespace(top_module='top')
    text='module top(A,Y);\ninput A;\noutput Y;\nwire n;\nbuf g(n,A);\nassign Y=n;\nendmodule\n'
    cone=_refreshed_candidate_cone(text,evaluator,'Y')
    assert cone.gates == ['g']
    assert _gate_driving_output(cone,cone.boundary_outputs[0]) == 'g'


def test_cut_preserves_secondary_output_consumed_outside_target_cone():
    from rseco.netlist import Gate
    add=Gate('fa','add','S',('A','B'),additional_outputs=('CO',))
    netlist=Netlist('top',['A','B'],['Y','Z'],['S','CO'],[
        add,Gate('buf','sink','Y',('CO',)),Gate('buf','other','Z',('S',))])
    cone=extract_fanin_cone(netlist,['Y'])
    cut=_cut_for_selected_gates(cone,['add'],method='counterexample')
    assert set(cut.boundary_outputs) == {'CO','S'}
    assert 'S' not in cut.internal_nets


def test_split_external_outputs_cannot_also_be_internal():
    from rseco.netlist import Gate
    from rseco.cut import fixed_min_cut
    netlist=Netlist('top',['A','B'],['Y','Z'],['I','S','CO'],[
        Gate('buf','src','I',('A',)),
        Gate('fa','add','S',('I','B'),additional_outputs=('CO',)),
        Gate('buf','sink','Y',('CO',)),Gate('buf','other','Z',('S',))])
    parts=split_cone_by_depth(extract_fanin_cone(netlist,['Y']),2)
    part=next(part for part in parts if 'add' in part.gates)
    cut=fixed_min_cut(part)
    assert 'S' in cut.boundary_outputs
    assert not (set(cut.boundary_outputs)&set(cut.internal_nets))
