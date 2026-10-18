"""Bounded QA: all STA/SEC boundaries are stubs; real F1/F2 are used below."""
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import threading
from types import SimpleNamespace

import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'code/src'))
sys.path.insert(0,str(ROOT/'code/scripts'))

def module():
    spec=importlib.util.spec_from_file_location('C_adapter',HERE/'adapter.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m

def fake_process(argv,**kwargs):
    return SimpleNamespace(returncode=0,stdout='mock STA only',stderr='')

def stub_tcl(directory):
    (directory/'sta.tcl').write_text('read_verilog '+(directory/'mapped.v').resolve().as_posix()+'\n# mock only\n',encoding='utf-8',newline='')

class FakeBackend:
    simulated=True
    def __init__(self,api,candidates):self.api=api;self.pool=candidates;self.measured=[];self.proofs=0
    def snapshot(self,text):return ['x','y']
    def candidates(self,snapshot,inst,config):return [self.api.Action(inst,'G',str(x)) for x in self.pool.get(inst,[])]
    def apply(self,text,action):
        j=json.loads(text);j[action.instance]=action.target;return json.dumps(j,sort_keys=True)
    def validate(self,base,candidate):return {'status':'fail' if 'bad' in candidate else 'pass'}
    def score(self,text):return sum(float(v) for v in json.loads(text).values())
    def measure(self,text,directory,role,invoke,config):
        stub_tcl(directory)
        self.measured.append((role,text));invoke(['mock-sta',text],capture_output=True,text=True,timeout=5)
        return {'wns':self.score(text),'tns':-1,'critical':['x','y']}
    def prepare_sec(self,initial,final,directory):
        directory.mkdir()
        (directory/'model_preflight.v').write_text('mock',encoding='utf-8',newline='')
        return {'splits':{'gold.v':initial,'gate.v':final,'helpers.v':'mock'},
                'model_path':str(directory/'model_preflight.v'),
                'model_sha256':self.api.sha(directory/'model_preflight.v')}
    def sec(self,initial,final,directory):
        self.proofs+=1;directory.mkdir()
        for name,text in [('initial_raw.v',initial),('final_raw.v',final),('gold.v',initial),('gate.v',final),('cells.v','mock'),('helpers.v','mock'),('sec.ys','mock'),('sec.log','Of those cells 1 are proven and 0 are unproven.\nEquivalence successfully proven!')]: (directory/name).write_text(text,encoding='utf-8',newline='')
        result={'status':'pass','returncode':0,'initial_sha256':self.api.sha(directory/'initial_raw.v'),'final_sha256':self.api.sha(directory/'final_raw.v'),'shared_helpers_sha256':self.api.sha(directory/'helpers.v')}
        (directory/'result.json').write_text(json.dumps(result));return result

INITIAL=json.dumps({'x':'0','y':'0'},sort_keys=True)
def run(tmp_path,api,backend,**changes):
    config=api.Config(rounds=1,**changes)
    return api.run_schedule(INITIAL,config,backend,tmp_path/'run',process_runner=fake_process)

def test_evaluate_all_same_base_then_best_and_multiple_commits(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1,3],'y':[2]});r=run(tmp_path,a,b,workers=2)
    assert r['status']=='qa_complete' and [c['action']['target'] for c in r['commits']]==['3','2']
    first=[j for role,j in b.measured if role=='candidate'][:2]
    assert all(json.loads(t)['y']=='0' for t in first)
    assert json.loads(r['final_text'])=={'x':'3','y':'2'} and r['counts']['candidate_sta_launches']==3 and b.proofs==1
    assert len({t['directory'] for t in r['trials']})==3

def test_parallel_completion_does_not_change_submission_order_tie(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1,2]});b.score=lambda text: 0 if text==INITIAL else 1
    second=threading.Event();completion=[]
    def runner(argv,**kw):
        v=json.loads(argv[1])['x']
        if v=='1':assert second.wait(3)
        if v=='2':second.set()
        completion.append(v);return fake_process(argv,**kw)
    r=a.run_schedule(INITIAL,a.Config(rounds=1,workers=2),b,tmp_path/'run',process_runner=runner)
    assert r['commits'][0]['action']['target']=='1' and completion.index('2')<completion.index('1')

def test_one_shared_rng_shuffles_candidates_not_critical_instances(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1,2,3,4],'y':[1,2,3,4]});b.score=lambda text: 0
    r=run(tmp_path,a,b,random_order=True,seed=3)
    rng=random.Random(3);expected=[]
    for inst in ['x','y']:
        values=['1','2','3','4'];rng.shuffle(values);expected.extend((inst,v) for v in values)
    assert [(t['action']['instance'],t['action']['target']) for t in r['trials']]==expected

def test_unimproved_pass_stops_before_round_cap(tmp_path):
    a=module();b=FakeBackend(a,{'x':[0]});r=a.run_schedule(INITIAL,a.Config(rounds=20),b,tmp_path/'run',process_runner=fake_process)
    assert len(r['passes'])==1 and r['stop_reason']=='no_improvement'

def test_illegal_candidate_and_budget_never_launch_sta(tmp_path):
    a=module();b=FakeBackend(a,{'x':['bad',1,2]});r=run(tmp_path,a,b,sta_budget=1,workers=2)
    assert r['counts']['candidate_sta_launches']==1 and len(r['commits'])==1
    assert any(t['status']=='precheck_reject' for t in r['trials'])
    assert any(t['status']=='budget_reject' for t in r['trials'])

def test_source_input_drift_stops_before_completion(tmp_path):
    a=module();p=tmp_path/'source';p.write_text('initial');guard=a.PinGuard({p:a.sha(p)})
    b=FakeBackend(a,{'x':[1]})
    def runner(argv,**kw):
        if json.loads(argv[1])['x']=='1':p.write_text('changed')
        return fake_process(argv,**kw)
    with pytest.raises(a.PinDrift):a.run_schedule(INITIAL,a.Config(rounds=1),b,tmp_path/'run',guard=guard,process_runner=runner)
    assert not (tmp_path/'run/completion.json').exists()

def test_no_overwrite_or_resume_incomplete_output(tmp_path):
    a=module();b=FakeBackend(a,{});p=tmp_path/'run';p.mkdir();(p/'sentinel').write_text('keep')
    with pytest.raises((RuntimeError,FileExistsError)):run(tmp_path,a,b)
    assert (p/'sentinel').read_text()=='keep' and not b.measured

def test_sec_failure_never_becomes_complete(tmp_path):
    a=module();b=FakeBackend(a,{});old=b.sec
    def sec(*args):
        result=old(*args);result.update(status='fail',returncode=1);(args[-1]/'result.json').write_text(json.dumps(result));return result
    b.sec=sec;r=run(tmp_path,a,b)
    assert r['status']=='failed' and r['sec_status']=='fail'

def test_false_gate_result_is_not_treated_as_success(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1]});original=b.validate
    b.validate=lambda base,candidate: {'status':'pass'} if base==candidate else {'status':'fail','reason':'F2 false'}
    r=run(tmp_path,a,b);assert r['counts']['candidate_sta_launches']==0 and not r['commits']

LIB='''library(test) {
 cell ("sky130_fd_sc_hd__buf_1") { pin("A") { direction: input; } pin("X") { direction: output; function: "A"; } }
 cell ("sky130_fd_sc_hd__buf_2") { pin("A") { direction: input; } pin("X") { direction: output; function: "A"; } }
 cell ("sky130_fd_sc_hd__clkbuf_1") { pin("A") { direction: input; } pin("X") { direction: output; function: "A"; } }
}'''
TEXT='''module helper(A,Y); input A; output Y; sky130_fd_sc_hd__buf_1 x(.A(A),.X(Y)); endmodule
module top(A,Y,Z); input A; output Y,Z; sky130_fd_sc_hd__buf_1 x(.A(A),.X(Y)); sky130_fd_sc_hd__buf_1 y(.A(A),.X(Z)); endmodule'''

@pytest.mark.parametrize('kind,target',[('G','sky130_fd_sc_hd__buf_2'),('R','sky130_fd_sc_hd__clkbuf_1'),('B','sky130_fd_sc_hd__buf_1')])
def test_real_edit_and_F1_F2_preserve_same_named_helper(kind,target):
    a=module();from backend import ActualBackend
    from rseco.verilog_modules import target_module_text
    b=ActualBackend('top',liberty_text=LIB);action=a.Action('x',kind,target,pin='A',new_net='n_x')
    changed=b.apply(TEXT,action)
    assert target_module_text(changed,'helper')==target_module_text(TEXT,'helper')
    assert b.validate(TEXT,changed)['status']=='pass'

def test_real_gate_rejects_helper_change():
    module();from backend import ActualBackend
    b=ActualBackend('top',liberty_text=LIB)
    assert b.validate(TEXT,TEXT.replace('buf_1 x','buf_2 x',1))['status']=='fail'

def test_repeated_B_in_post_single_JOINT_is_rejected_without_STA(tmp_path):
    a=module();from backend import ActualBackend
    b=ActualBackend('top',liberty_text=LIB);b.simulated=True
    b.candidates=lambda snapshot,inst,config:[a.Action(inst,'B','sky130_fd_sc_hd__buf_1',pin='A',new_net='n_'+inst)]
    def measure(text,directory,role,invoke,config):
        stub_tcl(directory)
        invoke(['mock-sta'],capture_output=True,text=True,timeout=5)
        return {'wns':text.count('_bufb_'),'tns':-1,'critical':['x','y']}
    fake_proof=FakeBackend(a,{})
    b.measure=measure;b.sec=fake_proof.sec;b.prepare_sec=fake_proof.prepare_sec
    # Archived C inputs have standalone Yosys declarations/cell statements.
    # Compact mixed statement lines are a separate current F2 limitation.
    initial=TEXT.replace('; ', ';\n ')
    r=a.run_schedule(initial,a.Config(rounds=1,joint_pairs=3),b,tmp_path/'run',process_runner=fake_process)
    joint=[t for t in r['trials'] if t['stage']=='JOINT']
    assert len(r['commits'])==2 and len(joint)==1 and joint[0]['status']=='precheck_reject'
    assert r['counts']['joint_sta_launches']==0

def test_cloned_legacy_STA_records_each_retry_without_global_patch(tmp_path):
    a=module();from backend import ActualBackend
    b=ActualBackend('top',liberty_text=LIB);observed=[]
    def old_sta(mapped,period,output,*,top_module,multi_path,clock_port):
        subprocess.run(['mock-sta','attempt1'],capture_output=True,text=True,timeout=5)
        subprocess.run(['mock-sta','attempt2'],capture_output=True,text=True,timeout=5)
        return {'wns':0,'tns':0}
    b.legacy=SimpleNamespace(run_opensta=old_sta,_critical_instances_from_sta=lambda text:[])
    original=subprocess.run
    def invoke(argv,**kw):observed.append(argv);return fake_process(argv,**kw)
    p=tmp_path/'sta';p.mkdir();(p/'mapped.v').write_text(TEXT);(p/'sta.log').write_text('mock')
    b.measure(TEXT,p,'candidate',invoke,a.Config())
    assert len(observed)==2 and subprocess.run is original

def test_preview_manifest_cannot_execute_before_registration(tmp_path,monkeypatch):
    a=module();monkeypatch.setattr(subprocess,'run',lambda *a,**k:pytest.fail('unexpected process'))
    with pytest.raises(RuntimeError,match='preview|registered'):
        a.run_frozen({'execution_ready':False},'hybrid','s27',tmp_path/'run')


def test_candidate_tamper_after_STA_cannot_be_committed(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1]});old=b.measure
    def measure(text,directory,role,invoke,config):
        result=old(text,directory,role,invoke,config)
        if role=='candidate':(directory.parent/'candidate.v').write_text('changed')
        return result
    b.measure=measure
    with pytest.raises(a.PinDrift):run(tmp_path,a,b)
    assert not (tmp_path/'run/completion.json').exists()


def test_retry_is_another_actual_launch_and_cannot_exceed_budget(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1]});old=b.measure;invoked=[]
    def measure(text,directory,role,invoke,config):
        result=old(text,directory,role,invoke,config)
        if role=='candidate':invoke(['mock-sta','retry'],capture_output=True,text=True,timeout=5)
        return result
    b.measure=measure
    def runner(argv,**kw):invoked.append(argv);return fake_process(argv,**kw)
    r=a.run_schedule(INITIAL,a.Config(rounds=1,sta_budget=1),b,tmp_path/'run',process_runner=runner)
    assert r['counts']['candidate_sta_launches']==1
    assert not any('retry' in argv for argv in invoked) and not r['commits']


def test_missing_required_input_is_rejected_by_actual_F1_F2():
    module();from backend import ActualBackend
    b=ActualBackend('top',liberty_text=LIB)
    assert b.validate(TEXT,TEXT.replace('.A(A),.X(Y)', '.X(Y)', 1))['status']=='fail'


def test_all_eight_retained_C_inputs_have_actual_static_model_support():
    module();from backend import ActualBackend
    from adapter import PinGuard
    preview=json.loads((HERE/'recipe_preview.json').read_text(encoding='utf-8'))
    pins={ROOT/row['path']:row['sha256'] for row in preview['mapped_inputs'].values()}
    guard=PinGuard(pins);guard()
    for circuit,row in preview['mapped_inputs'].items():
        b=ActualBackend(circuit);text=(ROOT/row['path']).read_text(encoding='utf-8')
        assert b.validate(text,text)['status']=='pass', circuit
    guard()


def test_recipe_preview_preserves_unknowns_and_mixed_random_asymmetry():
    preview=json.loads((HERE/'recipe_preview.json').read_text(encoding='utf-8'))
    assert not preview['execution_ready'] and preview['formal_source_pin'] is None
    assert len(preview['runs'])==48
    for row in preview['runs']:
        values=row['new_reconstruction_values']
        assert row['historical_runtime_argv'] is None and row['historical_runtime_source_pin'] is None
        assert values['joint_pairs']==(3 if row['arm']=='hybrid' else 0)
        assert values['sta_budget']==0 and values['rounds']==20

@pytest.mark.parametrize('artifact',['candidate.v','base.v','sta/mapped.v'])
def test_later_candidate_cannot_change_previous_trial_input(tmp_path,artifact):
    a=module();b=FakeBackend(a,{'x':[1],'y':[2]});old=b.measure
    def measure(text,directory,role,invoke,config):
        result=old(text,directory,role,invoke,config)
        if role=='candidate' and json.loads(text)['y']=='2':
            (tmp_path/'run/trial_000000'/artifact).write_text('changed after earlier evaluation')
        return result
    b.measure=measure
    with pytest.raises(a.PinDrift):run(tmp_path,a,b)
    assert not (tmp_path/'run/completion.json').exists()


def test_legacy_STA_receives_declared_clock_port(tmp_path):
    a=module();from backend import ActualBackend
    b=ActualBackend('top',liberty_text=LIB);seen=[]
    def old_sta(mapped,period,output,*,top_module,multi_path,clock_port='CK'):
        seen.append(clock_port);return {'wns':0,'tns':0}
    b.legacy=SimpleNamespace(run_opensta=old_sta,_critical_instances_from_sta=lambda text:[])
    p=tmp_path/'sta';p.mkdir();(p/'mapped.v').write_text(TEXT)
    b.measure(TEXT,p,'candidate',lambda *a,**k:fake_process(*a,**k),a.Config(clock_port='clk'))
    assert seen==['clk']


@pytest.mark.parametrize('changed',['mapped.v','sta.tcl'])
def test_retry_input_or_TCL_drift_is_rejected_before_another_runner_call(tmp_path,changed):
    a=module();b=FakeBackend(a,{'x':[1]});old=b.measure;calls=[]
    def measure(text,directory,role,invoke,config):
        result=old(text,directory,role,invoke,config)
        if role=='candidate':
            (directory/changed).write_text('changed between attempts')
            invoke(['mock-sta','retry'],capture_output=True,text=True,timeout=5)
        return result
    b.measure=measure
    def runner(argv,**kw):calls.append(argv);return fake_process(argv,**kw)
    with pytest.raises(a.PinDrift):a.run_schedule(INITIAL,a.Config(rounds=1),b,tmp_path/'run',process_runner=runner)
    assert not any('retry' in command for command in calls)


def test_every_attempt_binds_exact_TCL_and_complete_Verilog_bytes(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1]});run(tmp_path,a,b)
    parent=tmp_path/'run/trial_000000/sta';attempt=parent/'attempt_001'
    assert (attempt/'sta.tcl').read_bytes()==(parent/'sta.tcl').read_bytes()
    assert (attempt/'read_verilog_input.v').read_bytes()==(parent/'mapped.v').read_bytes()
    receipt=json.loads((attempt/'input_snapshot.json').read_text(encoding='utf-8'))
    assert receipt['read_verilog_sha256']==a.sha(attempt/'read_verilog_input.v')
    assert receipt['tcl_sha256']==a.sha(attempt/'sta.tcl')


def test_timeout_partial_stdout_stderr_are_retained_exactly(tmp_path):
    a=module();b=FakeBackend(a,{'x':[1]})
    def runner(argv,**kw):
        if json.loads(argv[1])['x']=='1':raise subprocess.TimeoutExpired(argv,1,output=b'partial stdout\n',stderr=b'partial stderr\n')
        return fake_process(argv,**kw)
    a.run_schedule(INITIAL,a.Config(rounds=1),b,tmp_path/'run',process_runner=runner)
    attempt=tmp_path/'run/trial_000000/sta/attempt_001'
    assert (attempt/'stdout.log').read_bytes()==b'partial stdout\n'
    assert (attempt/'stderr.log').read_bytes()==b'partial stderr\n'


@pytest.mark.parametrize('log',[
    'Of those cells 0 are proven and 0 are unproven.\nEquivalence successfully proven!',
    'Of those cells 1 are proven and 0 are unproven.\nEquivalence successfully proven!\nNo SAT model available',
    'Of those cells 1 are proven and 1 are unproven.\nEquivalence successfully proven!',
    'Equivalence successfully proven!',
])
def test_pseudo_pass_empty_unsupported_or_unproven_is_not_complete(tmp_path,log):
    a=module();b=FakeBackend(a,{});old=b.sec
    def sec(*args):
        result=old(*args);(args[-1]/'sec.log').write_text(log,encoding='utf-8');return result
    b.sec=sec
    assert run(tmp_path,a,b)['status']=='failed'


@pytest.mark.parametrize('artifact',['gold.v','gate.v','helpers.v','cells.v'])
def test_proof_split_or_actual_model_mismatch_is_not_complete(tmp_path,artifact):
    a=module();b=FakeBackend(a,{});old=b.sec
    def sec(*args):
        result=old(*args);(args[-1]/artifact).write_text('different object',encoding='utf-8');return result
    b.sec=sec
    assert run(tmp_path,a,b)['status']=='failed'


def test_actual_preflight_uses_current_writer_and_independent_helper_split(tmp_path):
    a=module();from backend import ActualBackend
    from rseco.real_wns import write_liberty_cell_models
    import run_r22_cut_ablation as common
    b=ActualBackend('top',liberty_text=LIB)
    changed=b.apply(TEXT,a.Action('x','G','sky130_fd_sc_hd__buf_2'))
    expected=b.prepare_sec(TEXT,changed,tmp_path/'preflight')
    gold,gate,helpers=common.sec_designs(TEXT,changed,'top')
    assert expected['splits']=={'gold.v':gold,'gate.v':gate,'helpers.v':helpers}
    assert expected['used_types']==['sky130_fd_sc_hd__buf_1','sky130_fd_sc_hd__buf_2']
    write_liberty_cell_models(LIB,tmp_path/'independent_model.v',used_cells=set(expected['used_types']))
    assert a.sha(tmp_path/'independent_model.v')==expected['model_sha256']
