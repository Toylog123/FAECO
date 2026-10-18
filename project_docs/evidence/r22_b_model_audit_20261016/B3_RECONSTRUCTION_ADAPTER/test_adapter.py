"""Bounded adapter QA. All processes/SEC are fakes; no EDA is launched."""
from pathlib import Path
from types import ModuleType, SimpleNamespace
import importlib.util
import json
import sys

import pytest

HERE=Path(__file__).resolve().parent
if (HERE/'adapter.py').exists():
    spec=importlib.util.spec_from_file_location('b3_adapter_under_test',HERE/'adapter.py')
    a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
else:
    a=ModuleType('missing_adapter')
    def missing(*args,**kwargs):raise RuntimeError('B3 adapter not implemented')
    for name in ['build_plan','register_plan','validate_manifest','execute_job','verify_job','guarded_runner']:
        setattr(a,name,missing)

LIB=''.join(f'cell ("sky130_fd_sc_hd__buf_{i}") {{ pin ("A") {{ direction : "input"; }} pin ("X") {{ direction : "output"; function : "A"; }} }}' for i in (1,2))


@pytest.fixture
def env(tmp_path,monkeypatch):
    root=tmp_path; evidence=root/'evidence';evidence.mkdir()
    code=root/'code';code.mkdir();(code/'source.py').write_text('frozen production')
    adapter=evidence/'adapter.py';adapter.write_text('frozen adapter')
    table=code/'table.json';table.write_text('{}')
    lib=root/'cells.lib';lib.write_text(LIB)
    original_checker=HERE.parent/'x_identity_certificate.py'
    checker=evidence/'x_identity_certificate.py';checker.write_bytes(original_checker.read_bytes())
    inputs={}
    for circuit in ('b09','b20','b21'):
        path=root/f'{circuit}.v'
        path.write_text(f'module {circuit}(A,Y);\ninput A;\noutput Y;\nsky130_fd_sc_hd__buf_1 g (.A(A),.X(Y));\nendmodule\n')
        inputs[circuit]={'path':path.name,'sha256':__import__('hashlib').sha256(path.read_bytes()).hexdigest(),'rtl':path.name}
    design=evidence/'B3_RERUN_DESIGN.json';design.write_text(json.dumps({'runs':[{'circuit':c,'raw_input_path':v['path']} for c,v in inputs.items()]}))
    patches={'ROOT':root,'BASE':evidence,'ADAPTER':adapter,'CHECKER':checker,'LIB':lib,'TABLE':table,'DESIGN':design,'INPUTS':inputs}
    for k,v in patches.items():monkeypatch.setattr(a,k,v,raising=False)
    monkeypatch.setattr(a,'_git_identity',lambda:{'head':'abc123','source_tree_clean':True},raising=False)
    monkeypatch.setattr(a,'_production_manifest',lambda:{'code/source.py':a.sha(code/'source.py')},raising=False)
    monkeypatch.setattr(a,'_tool_pin',lambda:{'fixture':'no tools executed'},raising=False)
    output=evidence/'B3_RECONSTRUCTION_RUNS'/'new_run'
    return SimpleNamespace(root=root,evidence=evidence,output=output,code=code,inputs=inputs)


def registered(env):
    plan=a.build_plan(env.output)
    return a.register_plan(plan,env.output)


def test_preview_is_explicit_reconstruction_not_registration(env):
    plan=a.build_plan(env.output)
    assert plan['status']=='review_preview'
    assert not plan['execution_ready']
    assert not env.output.exists()
    assert plan['historical_argv'] is None
    assert plan['source_pin']['head']=='abc123'
    assert len(plan['jobs'])==3
    for job in plan['jobs']:
        argv=job['command']
        for flag in ['--skip-mapping','--early-stop','--enable-buffer','--tns-aware','--feedback-legacy','--no-proxy-ranking']:
            assert flag in argv
        assert '--disable-topology' not in argv and '--sta-budget' not in argv and '--wall-timeout-s' not in argv
        for flag,value in [('--max-iterations','8'),('--max-patches','8'),('--period','0.5'),('--strategies','R,G,B'),('--cut-search-policy','legacy')]:
            assert argv[argv.index(flag)+1]==value
        assert 'run_outerloop_real_wns.py' in ' '.join(argv)
        assert 'hybrid_repair' not in ' '.join(argv)


def test_registration_refuses_dirty_source_or_existing_directory(env,monkeypatch):
    plan=a.build_plan(env.output)
    monkeypatch.setattr(a,'_git_identity',lambda:{'head':'abc123','source_tree_clean':False})
    with pytest.raises(RuntimeError,match='clean|Source|source'):
        a.register_plan(plan,env.output)
    assert not env.output.exists()
    monkeypatch.setattr(a,'_git_identity',lambda:{'head':'abc123','source_tree_clean':True})
    env.output.mkdir(parents=True)
    with pytest.raises(RuntimeError,match='exist|overwrite'):
        a.register_plan(plan,env.output)


@pytest.mark.parametrize('change',['input','source','library','head','table','command'])
def test_registered_manifest_drift_rejected_before_launch(env,monkeypatch,change):
    manifest=registered(env)
    if change=='input':(env.root/env.inputs['b09']['path']).write_text('changed input')
    elif change=='source':(env.code/'source.py').write_text('changed code')
    elif change=='library':a.LIB.write_text('changed library')
    elif change=='table':a.TABLE.write_text('{"changed":true}')
    elif change=='head':monkeypatch.setattr(a,'_git_identity',lambda:{'head':'other','source_tree_clean':True})
    else:manifest['plan']['jobs'][0]['command'].append('--disable-topology')
    calls=[]
    monkeypatch.setattr(a,'_run_process',lambda *args: calls.append(args),raising=False)
    with pytest.raises(RuntimeError):a.execute_job(manifest,'b09')
    assert not calls


def _fake_attempt(out,script,netlist,manifest,identity,stdout='WNS -1',returncode=0,error=None):
    script.write_text('\n'.join([f'read_liberty {a.common._to_wsl(a.LIB)}',
        f'read_verilog {a.common._to_wsl(netlist)}','link_design '+out.name,
        'create_clock -name clk -period 0.5 [get_ports CK]','report_worst_slack -max','']))
    command=['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',a.common._to_wsl(script)]
    attempt=out/'sta_attempts'/f'{identity:06d}';attempt.mkdir(parents=True)
    inputs=a._begin_sta_attempt(attempt,str(script),out,out.name,manifest,command)
    result=a._finish_sta_attempt(attempt,inputs,answer=SimpleNamespace(returncode=returncode,stdout=stdout,stderr='') if error is None else None,error=error)
    returned={'event':'return','id':identity,'returncode':result['returncode'],'attempt_dir':str(attempt),'result_sha256':a.sha(attempt/'result.json')}
    if error is not None:returned['error']=str(error)
    return [{'event':'launch','id':identity,'script':str(script.resolve()),'command':command,'script_sha256':a.sha(script),
             'attempt_dir':str(attempt),'inputs_sha256':a.sha(attempt/'inputs.json')},
            returned]


def _fake_outputs(job,manifest,final=None,candidate_error=None):
    out=Path(job['output_dir']);initial=(out/'mapped.v').read_text();final=final or initial.replace('buf_1','buf_2')
    fingerprint=a.text_sha
    patch={'candidate_hash':fingerprint(final),'base_netlist_hash':fingerprint(initial),'netlist_hash':fingerprint(final),'netlist_text':final}
    state={'current_netlist_text':final,'current_netlist_hash':fingerprint(final),'accepted_patches':[patch],'budget':{'epsilon':0.0,'sta_used':1,'max_iterations':8,'max_patches':8,'sta_budget':None,'formal_budget':None,'wall_timeout_s':None}}
    result={'state':state,'wns':-0.5,'baseline_wns':-1.0,'n_new_sta_runs':1,'n_candidate_sta_runs':2,'n_candidate_evaluation_records':2,'enable_topology':True,'cut_search_policy':'legacy'}
    report=out/'eval/iter001_cand001/000_g_G';report.mkdir(parents=True);(report/'mapped.v').write_text(final)
    trial={'sta_launch_seq':1,'sta_executed':True,'accepted':True,'committed':True,'candidate_hash':fingerprint(final),'base_netlist_hash':fingerprint(initial),'sta_provenance':{'output_dir':str(report)}}
    replay={**trial,'sta_executed':False,'cached_from_seq':1,'accepted':False,'committed':False}
    events=[{'kind':'candidate_ideal','seq':1,'wns':-0.5,'report_dir':str(report),'candidate_hash':fingerprint(final),'base_netlist_hash':fingerprint(initial)}]
    for name,data in [('outerloop_result.json',result),('run_config.json',{**job['expected_run_config'],'git_head':manifest['plan']['source_pin']['head']}),('eval_trials.json',{'trials':[trial,replay],'sta_launch_events':events})]:
        (out/name).write_text(json.dumps(data))
    trace=_fake_attempt(out,out/'sta.tcl',out/'mapped.v',manifest,1)+_fake_attempt(out,report/'sta.tcl',report/'mapped.v',manifest,2,error=candidate_error)
    (out/'tool_launches.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in trace))
    return SimpleNamespace(returncode=0)


def _fake_sec(initial,final,circuit,out):
    out.mkdir();gold,gate,helpers=a.common.sec_designs(initial,final,circuit)
    for name,text in [('initial_raw.v',initial),('final_raw.v',final),('gold.v',gold),('gate.v',gate),('helpers.v',helpers),('sec.ys',a._sec_script(out))]:
        (out/name).write_text(text,encoding='utf-8')
    a.write_liberty_cell_models(a.LIB.read_text(),out/'cells.v',used_cells=a._used_types(initial,final))
    (out/'sec.log').write_text('Of those cells 2 are proven and 0 are unproven.\nEquivalence successfully proven!\n')
    result={'status':'pass','returncode':0,'initial_sha256':a.sha(out/'initial_raw.v'),'final_sha256':a.sha(out/'final_raw.v'),'shared_helpers_sha256':a.sha(out/'helpers.v')}
    (out/'result.json').write_text(json.dumps(result))
    return result


def test_full_mock_transaction_binds_state_counts_and_SEC(env,monkeypatch):
    manifest=registered(env)
    monkeypatch.setattr(a,'_run_process',lambda job,m:_fake_outputs(job,m))
    monkeypatch.setattr(a,'final_sec',_fake_sec)
    done=a.execute_job(manifest,'b09')
    assert done['status']=='complete'
    assert done['accounting']['n_candidate_evaluation_records']==2
    assert done['accounting']['n_new_sta_runs']==1
    assert done['accounting']['n_cache_replays']==1
    assert done['accounting']['accepted_commits']==1
    assert done['accounting']['baseline_sta_launch_attempts']==1
    assert a.verify_job(manifest,'b09')==done
    with pytest.raises(RuntimeError,match='exist|overwrite'):a.execute_job(manifest,'b09')


@pytest.mark.parametrize('artifact',['final_raw','state','unproven','model','config','launch'])
def test_completed_transaction_tampering_rejected(env,monkeypatch,artifact):
    manifest=registered(env)
    monkeypatch.setattr(a,'_run_process',lambda job,m:_fake_outputs(job,m))
    monkeypatch.setattr(a,'final_sec',_fake_sec)
    a.execute_job(manifest,'b09');out=Path(manifest['plan']['jobs'][0]['output_dir'])
    if artifact=='final_raw':(out/'final_sec/final_raw.v').write_text('wrong final')
    elif artifact=='model':(out/'final_sec/cells.v').write_text('wrong model')
    elif artifact=='unproven':(out/'final_sec/sec.log').write_text('Of those cells 2 are proven and 1 are unproven.\nEquivalence successfully proven!')
    elif artifact=='launch':(out/'tool_launches.jsonl').write_text('')
    else:
        name='outerloop_result.json' if artifact=='state' else 'run_config.json'
        data=json.loads((out/name).read_text())
        if artifact=='state':data['state']['current_netlist_hash']='wrong'
        else:data['resolved_args']['tns_aware']=False
        (out/name).write_text(json.dumps(data))
    with pytest.raises(RuntimeError):a.verify_job(manifest,'b09')


def test_mapping_fallback_is_forbidden_even_inside_runner(env,monkeypatch):
    manifest=registered(env);job=manifest['plan']['jobs'][0];out=Path(job['output_dir']);out.mkdir();(out/'mapped.v').write_bytes((env.root/job['baseline']['path']).read_bytes())
    a.save_new(out/'preregistered.json',{'manifest_fingerprint':a.fingerprint(manifest),'job':job})
    monkeypatch.setattr(a.runner,'main',lambda:a.runner.run_yosys_mapping('unexpected','unexpected'))
    calls=[];monkeypatch.setattr(a.runner,'run_yosys_mapping',lambda *args:calls.append(args))
    with pytest.raises(RuntimeError,match='mapping|remap'):a.guarded_runner(manifest,'b09')
    assert not calls


def test_failure_receipt_retains_failed_SEC_and_never_completes(env,monkeypatch):
    manifest=registered(env)
    monkeypatch.setattr(a,'_run_process',lambda job,m:_fake_outputs(job,m))
    monkeypatch.setattr(a,'final_sec',lambda *args:{'status':'unsupported','returncode':None})
    with pytest.raises(RuntimeError,match='SEC'):a.execute_job(manifest,'b09')
    out=Path(manifest['plan']['jobs'][0]['output_dir'])
    assert (out/'failure.json').is_file() and not (out/'completion.json').exists()


def test_failure_receipt_cannot_be_ignored_next_to_completion(env,monkeypatch):
    manifest=registered(env)
    monkeypatch.setattr(a,'_run_process',lambda job,m:_fake_outputs(job,m))
    monkeypatch.setattr(a,'final_sec',_fake_sec)
    a.execute_job(manifest,'b09');out=Path(manifest['plan']['jobs'][0]['output_dir'])
    a.save_new(out/'failure.json',{'status':'failed'})
    with pytest.raises(RuntimeError,match='failure'):a.verify_job(manifest,'b09')


def test_missing_staged_input_rejected_without_fallback(env,monkeypatch):
    manifest=registered(env);job=manifest['plan']['jobs'][0];out=Path(job['output_dir']);out.mkdir()
    a.save_new(out/'preregistered.json',{'manifest_fingerprint':a.fingerprint(manifest),'job':job})
    calls=[];monkeypatch.setattr(a.runner,'main',lambda:calls.append('runner'))
    with pytest.raises(RuntimeError,match='staged'):a.guarded_runner(manifest,'b09')
    assert not calls


def test_illegal_tristate_actual_final_rejected_before_SEC(env,monkeypatch):
    a.LIB.write_text(LIB+'cell ("sky130_fd_sc_hd__einvn_1") { pin ("A") { direction : "input"; } pin ("TE_B") { direction : "input"; } pin ("Z") { direction : "output"; function : "!A"; three_state : "TE_B"; } }')
    manifest=registered(env)
    def bad_process(job,m):
        initial=(Path(job['output_dir'])/'mapped.v').read_text()
        final=initial.replace('buf_1','einvn_1').replace('.X(Y)','.Z(Y)')
        return _fake_outputs(job,m,final=final)
    monkeypatch.setattr(a,'_run_process',bad_process)
    calls=[];monkeypatch.setattr(a,'final_sec',lambda *args:calls.append(args))
    with pytest.raises((RuntimeError,ValueError),match='required input'):a.execute_job(manifest,'b09')
    assert not calls


@pytest.mark.parametrize('corrupt',['trial_identity','commit_identity','epsilon'])
def test_candidate_launch_commit_and_scientific_epsilon_must_agree(env,monkeypatch,corrupt):
    manifest=registered(env)
    def broken(job,m):
        answer=_fake_outputs(job,m);out=Path(job['output_dir'])
        name='outerloop_result.json' if corrupt=='epsilon' else 'eval_trials.json'
        data=json.loads((out/name).read_text())
        if corrupt=='epsilon':data['state']['budget']['epsilon']=0.5
        elif corrupt=='trial_identity':data['trials'][0]['candidate_hash']='wrong candidate'
        else:data['trials'][0]['committed']=False
        (out/name).write_text(json.dumps(data));return answer
    monkeypatch.setattr(a,'_run_process',broken)
    calls=[]
    def fake_proof(*args):calls.append(args);return _fake_sec(*args)
    monkeypatch.setattr(a,'final_sec',fake_proof)
    with pytest.raises(RuntimeError):a.execute_job(manifest,'b09')
    assert not calls


def test_guarded_child_observes_exact_STA_process_boundary_without_running_it(env,monkeypatch):
    manifest=registered(env);job=manifest['plan']['jobs'][0];out=Path(job['output_dir']);out.mkdir()
    (out/'mapped.v').write_bytes((env.root/job['baseline']['path']).read_bytes())
    a.save_new(out/'preregistered.json',{'manifest_fingerprint':a.fingerprint(manifest),'job':job})
    script=out/'sta.tcl';script.write_text('\n'.join([f'read_liberty {a.common._to_wsl(a.LIB)}',
        f'read_verilog {a.common._to_wsl(out/"mapped.v")}','link_design b09',
        'create_clock -name clk -period 0.5 [get_ports CK]','report_worst_slack -max','']))
    calls=[]
    monkeypatch.setattr(a.subprocess,'run',lambda cmd,*args,**kwargs:(calls.append(cmd) or SimpleNamespace(returncode=0,stdout='',stderr='')))
    def fake_runner():
        a.subprocess.run(['ignored','-version'])
        a.subprocess.run(['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',a.common._to_wsl(script)])
        return 0
    monkeypatch.setattr(a.runner,'main',fake_runner)
    assert a.guarded_runner(manifest,'b09')==0
    events=[json.loads(line) for line in (out/'tool_launches.jsonl').read_text().splitlines()]
    assert len(calls)==2 and len(events)==2
    assert events[0]['event']=='launch' and events[0]['id']==1
    assert events[0]['script']==str(script) and events[0]['script_sha256']==a.sha(script)
    assert events[1]['event']=='return' and events[1]['returncode']==0
    assert events[1]['result_sha256']==a.sha(out/'sta_attempts/000001/result.json')


def _sta_setup(env):
    manifest=registered(env);job=manifest['plan']['jobs'][0];out=Path(job['output_dir']);out.mkdir()
    (out/'mapped.v').write_bytes((env.root/job['baseline']['path']).read_bytes())
    a.save_new(out/'preregistered.json',{'manifest_fingerprint':a.fingerprint(manifest),'job':job})
    script=out/'sta.tcl'
    script.write_text('\n'.join([f'read_liberty {a.common._to_wsl(a.LIB)}',
        f'read_verilog {a.common._to_wsl(out/"mapped.v")}', 'link_design b09',
        'create_clock -name clk -period 0.5 [get_ports CK]', 'report_checks -path_delay max',
        'puts "TNS_BEGIN"','report_tns','puts "TNS_END"','report_worst_slack -max','']))
    command=['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',a.common._to_wsl(script)]
    return manifest,out,script,command


def _trace(out):
    return [json.loads(line) for line in (out/'tool_launches.jsonl').read_text().splitlines()]


def test_STA_retry_keeps_exact_prelaunch_bytes_and_full_outputs(env,monkeypatch):
    manifest,out,script,command=_sta_setup(env);raw=(out/'mapped.v').read_bytes();tcl=script.read_bytes()
    answers=[SimpleNamespace(returncode=1,stdout='truncated first\n',stderr='first error\n'),
             SimpleNamespace(returncode=0,stdout='second WNS -1\n'+'x'*100000,stderr='second warning\n')]
    calls=[]
    def process(cmd,*args,**kwargs):
        assert cmd is command and kwargs=={'capture_output':True,'text':True,'timeout':900}
        calls.append(cmd);return answers[len(calls)-1]
    monkeypatch.setattr(a.subprocess,'run',process)
    def run():
        for answer in answers:
            observed=a.subprocess.run(command,capture_output=True,text=True,timeout=900)
            assert observed is answer
            (out/'sta.log').write_text(answer.stdout+answer.stderr)
        return 0
    monkeypatch.setattr(a.runner,'main',run)
    assert a.guarded_runner(manifest,'b09')==0
    events=_trace(out);assert len(events)==4 and len(calls)==2
    for index,answer in enumerate(answers,1):
        attempt=out/'sta_attempts'/f'{index:06d}'
        assert (attempt/'sta.tcl').read_bytes()==tcl
        assert (attempt/'netlist.v').read_bytes()==raw
        inputs=a.read_json(attempt/'inputs.json');result=a.read_json(attempt/'result.json')
        assert inputs['liberty']['sha256']==a.sha(a.LIB)
        assert result['returncode']==answer.returncode and not result['input_drift']
        assert (attempt/'stdout.bin').read_bytes()==answer.stdout.encode()
        assert (attempt/'stderr.bin').read_bytes()==answer.stderr.encode()
        assert events[(index-1)*2]['inputs_sha256']==a.sha(attempt/'inputs.json')
        assert events[(index-1)*2+1]['result_sha256']==a.sha(attempt/'result.json')
    assert (out/'sta.log').read_text()==answers[1].stdout+answers[1].stderr


@pytest.mark.parametrize('changed',['netlist','script','library'])
def test_STA_input_drift_is_recorded_and_rejects_guard_after_preserving_return(env,monkeypatch,changed):
    manifest,out,script,command=_sta_setup(env);answer=SimpleNamespace(returncode=0,stdout='WNS -1',stderr='')
    original={'netlist':out/'mapped.v','script':script,'library':a.LIB}[changed]
    before=original.read_bytes();seen=[]
    def process(*args,**kwargs):original.write_bytes(before+b'\nchanged');return answer
    monkeypatch.setattr(a.subprocess,'run',process)
    def run():seen.append(a.subprocess.run(command) is answer);return 0
    monkeypatch.setattr(a.runner,'main',run)
    with pytest.raises(RuntimeError,match='drift'):a.guarded_runner(manifest,'b09')
    assert seen==[True]
    attempt=out/'sta_attempts/000001';result=a.read_json(attempt/'result.json')
    assert result['input_drift'] and result['returncode']==0
    assert (attempt/('sta.tcl' if changed=='script' else 'netlist.v')).is_file()


@pytest.mark.parametrize('kind',['timeout','oserror','missing','permission','unknown'])
def test_STA_exception_identity_and_partial_output_are_preserved(env,monkeypatch,kind):
    manifest,out,script,command=_sta_setup(env)
    error={'timeout':a.subprocess.TimeoutExpired(command,900,output=b'partial\x00\xff',stderr=b'error\xfe'),
           'oserror':OSError('unconfirmed OS failure'),'missing':FileNotFoundError('missing executable'),
           'permission':PermissionError('launch denied'),'unknown':RuntimeError('unconfirmed failure')}[kind]
    def process(*args,**kwargs):raise error
    monkeypatch.setattr(a.subprocess,'run',process)
    def run():a.subprocess.run(command)
    monkeypatch.setattr(a.runner,'main',run)
    with pytest.raises(type(error)) as raised:a.guarded_runner(manifest,'b09')
    assert raised.value is error
    attempt=out/'sta_attempts/000001';result=a.read_json(attempt/'result.json')
    assert result['status']=='exception' and result['error_type']==type(error).__name__
    assert result['process_launched'] is (True if kind=='timeout' else False if kind in {'missing','permission'} else None)
    assert not result['input_drift']
    assert (attempt/'stdout.bin').read_bytes()==(error.output if kind=='timeout' else b'')
    assert _trace(out)[1]['result_sha256']==a.sha(attempt/'result.json')


def test_STA_existing_attempt_directory_never_overwritten_or_launched(env,monkeypatch):
    manifest,out,script,command=_sta_setup(env);attempt=out/'sta_attempts/000001';attempt.mkdir(parents=True)
    sentinel=attempt/'netlist.v';sentinel.write_bytes(b'old immutable evidence');calls=[]
    monkeypatch.setattr(a.subprocess,'run',lambda *args,**kwargs:(calls.append(args) or SimpleNamespace(returncode=0,stdout='',stderr='')))
    monkeypatch.setattr(a.runner,'main',lambda:a.subprocess.run(command))
    with pytest.raises((RuntimeError,FileExistsError)):a.guarded_runner(manifest,'b09')
    assert not calls and sentinel.read_bytes()==b'old immutable evidence'


@pytest.mark.parametrize('suffix',['source /tmp/extra.tcl\n','read_verilog /tmp/other.v\n','read_liberty $LIB\n'])
def test_STA_unknown_or_dynamic_TCL_rejected_without_guessing(env,monkeypatch,suffix):
    manifest,out,script,command=_sta_setup(env);script.write_text(script.read_text()+suffix);calls=[]
    monkeypatch.setattr(a.subprocess,'run',lambda *args,**kwargs:(calls.append(args) or SimpleNamespace(returncode=0,stdout='',stderr='')))
    monkeypatch.setattr(a.runner,'main',lambda:a.subprocess.run(command))
    with pytest.raises((RuntimeError,ValueError)):a.guarded_runner(manifest,'b09')
    assert not calls


def test_STA_baseline_cannot_read_another_valid_netlist(env,monkeypatch):
    manifest=registered(env)
    def wrong_baseline(job,m):
        answer=_fake_outputs(job,m);out=Path(job['output_dir']);trace=_trace(out)
        # Internally consistent bytes and hashes, but baseline TCL read the candidate.
        for path in [out/'sta_attempts/000001/sta.tcl',out/'sta_attempts/000001/netlist.v',out/'sta_attempts/000001/inputs.json',out/'sta_attempts/000001/result.json',out/'sta_attempts/000001/stdout.bin',out/'sta_attempts/000001/stderr.bin']:
            path.unlink()
        (out/'sta_attempts/000001').rmdir()
        report=out/'eval/iter001_cand001/000_g_G'
        trace[:2]=_fake_attempt(out,out/'sta.tcl',report/'mapped.v',m,1)
        (out/'tool_launches.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in trace))
        return answer
    monkeypatch.setattr(a,'_run_process',wrong_baseline);calls=[]
    def proof(*args):calls.append(args);return _fake_sec(*args)
    monkeypatch.setattr(a,'final_sec',proof)
    with pytest.raises(RuntimeError,match='baseline'):a.execute_job(manifest,'b09')
    assert not calls


@pytest.mark.parametrize('artifact',['stdout','snapshot','receipt','liberty','extra_attempt'])
def test_STA_attempt_tampering_is_rejected_before_SEC(env,monkeypatch,artifact):
    manifest=registered(env)
    def changed(job,m):
        answer=_fake_outputs(job,m);out=Path(job['output_dir']);attempt=out/'sta_attempts/000002'
        if artifact=='stdout':(attempt/'stdout.bin').write_bytes(b'')
        elif artifact=='snapshot':(attempt/'netlist.v').write_text('truncated')
        elif artifact=='receipt':
            result=a.read_json(attempt/'result.json');result['input_drift']=True;a.save_new(attempt/'changed.json',result)
            (attempt/'result.json').write_text(json.dumps(result))
        elif artifact=='liberty':
            inputs=a.read_json(attempt/'inputs.json');inputs['liberty']['sha256']='wrong';(attempt/'inputs.json').write_text(json.dumps(inputs))
        else:(out/'sta_attempts/000003').mkdir()
        return answer
    monkeypatch.setattr(a,'_run_process',changed);calls=[];monkeypatch.setattr(a,'final_sec',lambda *args:calls.append(args))
    with pytest.raises(RuntimeError):a.execute_job(manifest,'b09')
    assert not calls


def test_STA_truncated_baseline_and_refresh_retries_count_separately(env,monkeypatch):
    manifest=registered(env)
    def retry_process(job,m):
        answer=_fake_outputs(job,m);out=Path(job['output_dir']);trace=_trace(out)
        refresh=out/'eval/baseline_001';refresh.mkdir();(refresh/'mapped.v').write_bytes((out/'mapped.v').read_bytes())
        trace+=_fake_attempt(out,out/'sta.tcl',out/'mapped.v',m,3,stdout='truncated',returncode=1)
        trace+=_fake_attempt(out,refresh/'sta.tcl',refresh/'mapped.v',m,4,stdout='truncated refresh')
        trace+=_fake_attempt(out,refresh/'sta.tcl',refresh/'mapped.v',m,5,stdout='valid refresh WNS -1')
        (out/'tool_launches.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in trace))
        return answer
    monkeypatch.setattr(a,'_run_process',retry_process);monkeypatch.setattr(a,'final_sec',_fake_sec)
    counts=a.execute_job(manifest,'b09')['accounting']
    assert counts['n_new_sta_runs']==1 and counts['n_candidate_evaluation_records']==2
    assert counts['baseline_sta_launch_attempts']==2 and counts['refresh_sta_launch_attempts']==2
    assert counts['total_sta_process_attempts']==5


def test_STA_liberty_changed_inside_runner_is_rejected_and_recorded_before_launch(env,monkeypatch):
    manifest,out,script,command=_sta_setup(env);calls=[]
    monkeypatch.setattr(a.subprocess,'run',lambda *args,**kwargs:(calls.append(args) or SimpleNamespace(returncode=0,stdout='',stderr='')))
    def run():
        a.LIB.write_text(a.LIB.read_text()+'\nchanged')
        a.subprocess.run(command)
    monkeypatch.setattr(a.runner,'main',run)
    with pytest.raises(RuntimeError,match='drift'):a.guarded_runner(manifest,'b09')
    assert not calls
    rejection=a.read_json(out/'sta_attempts/000001/rejected.json')
    assert rejection['status']=='rejected_before_launch'
    assert _trace(out)[0]['event']=='rejected_before_launch'


def test_STA_reused_path_between_attempts_keeps_both_complete_netlists(env,monkeypatch):
    manifest,out,script,command=_sta_setup(env);candidate=out/'current_candidate.v'
    first=(out/'mapped.v').read_bytes();second=first.replace(b'buf_1',b'buf_2')
    candidate.write_bytes(first)
    script.write_text(script.read_text().replace(a.common._to_wsl(out/'mapped.v'),a.common._to_wsl(candidate)))
    answer=SimpleNamespace(returncode=0,stdout='WNS -1',stderr='')
    monkeypatch.setattr(a.subprocess,'run',lambda *args,**kwargs:answer)
    def run():
        assert a.subprocess.run(command) is answer
        candidate.write_bytes(second)
        assert a.subprocess.run(command) is answer
        return 0
    monkeypatch.setattr(a.runner,'main',run)
    assert a.guarded_runner(manifest,'b09')==0
    assert (out/'sta_attempts/000001/netlist.v').read_bytes()==first
    assert (out/'sta_attempts/000002/netlist.v').read_bytes()==second


def test_STA_timeout_retry_keeps_exception_and_success_in_separate_attempts(env,monkeypatch):
    manifest,out,script,command=_sta_setup(env);error=a.subprocess.TimeoutExpired(command,900,output=b'truncated',stderr=b'first error')
    answer=SimpleNamespace(returncode=0,stdout='WNS -1',stderr='');calls=[]
    def process(*args,**kwargs):
        calls.append(args)
        if len(calls)==1:raise error
        return answer
    monkeypatch.setattr(a.subprocess,'run',process)
    def run():
        try:a.subprocess.run(command)
        except a.subprocess.TimeoutExpired as seen:assert seen is error
        assert a.subprocess.run(command) is answer
        return 0
    monkeypatch.setattr(a.runner,'main',run)
    assert a.guarded_runner(manifest,'b09')==0
    assert a.read_json(out/'sta_attempts/000001/result.json')['status']=='exception'
    assert a.read_json(out/'sta_attempts/000002/result.json')['status']=='returned'
    assert (out/'sta_attempts/000001/stdout.bin').read_bytes()==b'truncated'
    assert len(_trace(out))==4


@pytest.mark.parametrize('error',[FileNotFoundError('missing executable'),PermissionError('permission denied'),OSError('unconfirmed OS failure'),RuntimeError('unconfirmed run failure')])
def test_unconfirmed_STA_start_cannot_be_scientific_complete_even_if_runner_continues(env,monkeypatch,error):
    manifest=registered(env);calls=[]
    monkeypatch.setattr(a,'_run_process',lambda job,m:_fake_outputs(job,m,candidate_error=error))
    def proof(*args):calls.append(args);return _fake_sec(*args)
    monkeypatch.setattr(a,'final_sec',proof)
    with pytest.raises(RuntimeError,match='launch|unconfirmed|incomplete'):a.execute_job(manifest,'b09')
    assert not calls
    out=Path(manifest['plan']['jobs'][0]['output_dir'])
    assert (out/'failure.json').is_file() and not (out/'completion.json').exists()
    assert len(_trace(out))==4
    result=a.read_json(out/'sta_attempts/000002/result.json')
    assert result['process_launched'] is not True
    assert result['error_type']==type(error).__name__
