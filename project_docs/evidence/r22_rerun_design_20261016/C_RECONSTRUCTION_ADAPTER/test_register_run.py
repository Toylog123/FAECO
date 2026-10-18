"""Transaction QA only; no EDA or formal registration outside pytest tmp paths."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent

def module():
    spec = importlib.util.spec_from_file_location('c_register_run_qa', HERE/'register_run.py')
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m

@pytest.fixture
def env(tmp_path, monkeypatch):
    m = module()
    monkeypatch.setattr(m, 'RUNS_BASE', tmp_path/'C_RECONSTRUCTION_RUNS')
    monkeypatch.setattr(m, '_git_identity', lambda: {'head':'qa-head', 'source_tree_clean':True})
    monkeypatch.setattr(m, '_tool_pin', lambda: {'qa_stub': {'sha256':'a'*64, 'version':'QA only'}})
    out = m.RUNS_BASE/'fresh'
    return m, out

def registered(env):
    m, out = env
    plan = m.build_preview(out)
    m.register(plan, out)
    return m, out, out/'manifest.json'

def test_preview_exact_48_and_no_external_tools(env, monkeypatch):
    m, out = env
    monkeypatch.setattr(m, '_tool_pin', lambda: pytest.fail('preview invoked tool'))
    p = m.build_preview(out)
    assert len(p['jobs']) == 48 and not out.exists() and not p['execution_ready']
    assert {j['arm'] for j in p['jobs']} == {'hybrid','pureG','pureB','random1','random2','random3'}
    for j in p['jobs']:
        assert j['recipe']['historical_runtime_argv'] is None
        assert j['recipe']['historical_runtime_source_pin'] is None
        assert '--skip-mapping' not in j['command']  # Native frozen C runner consumes retained mapped bytes.
        assert 'guarded-run' in j['command'] and 'run_outerloop' not in ' '.join(j['command'])
        assert j['expected_config'] == j['recipe']['new_reconstruction_values']
    assert next(j for j in p['jobs'] if j['arm']=='hybrid')['expected_config']['joint_pairs']==3
    assert next(j for j in p['jobs'] if j['arm']=='random1')['expected_config']['joint_pairs']==0

@pytest.mark.parametrize('bad', ['old_v1', '.', '../outside'])
def test_old_directory_is_rejected(env, bad):
    m, out=env
    target = out.parent.parent/bad
    with pytest.raises(RuntimeError): m.build_preview(target)

def test_unknown_cannot_be_relabelled_historical(env):
    m,out=env;p=m.build_preview(out)
    p['jobs'][0]['recipe']['historical_runtime_argv']=['invented']
    with pytest.raises(RuntimeError):m.register(p,out)
    assert not out.exists()

def test_dirty_source_cannot_register(env,monkeypatch):
    m,out=env;monkeypatch.setattr(m,'_git_identity',lambda:{'head':'qa-head','source_tree_clean':False})
    with pytest.raises(RuntimeError):m.register(m.build_preview(out),out)
    assert not out.exists()

def test_register_exclusive_and_no_automatic_resume(env):
    m,out,path=registered(env)
    before=path.read_bytes()
    with pytest.raises(RuntimeError):m.register(m.build_preview(out),out)
    assert path.read_bytes()==before
    job=out/'jobs'/'hybrid'/'s27';job.mkdir(parents=True)
    with pytest.raises(RuntimeError):m.execute(path,'hybrid','s27')
    assert not (job/'preregistered.json').exists()

@pytest.mark.parametrize('kind',['source','input','liberty','head','tools'])
def test_live_pin_drift_rejected_before_job(env,monkeypatch,kind):
    m,out,path=registered(env)
    if kind=='head':monkeypatch.setattr(m,'_git_identity',lambda:{'head':'other','source_tree_clean':True})
    elif kind=='tools':monkeypatch.setattr(m,'_tool_pin',lambda:{'different':{}})
    else:
        original=m.build_preview
        def changed(p):
            data=original(p)
            if kind=='source':data['source_manifest']['fake.py']='0'*64
            elif kind=='input':data['mapped_inputs']['s27']['sha256']='0'*64
            else:data['lib_sha256']='0'*64
            return data
        monkeypatch.setattr(m,'build_preview',changed)
    with pytest.raises(RuntimeError):m.execute(path,'hybrid','s27')
    assert not (out/'jobs').exists()

def test_manifest_bytes_guard_not_just_json(env):
    m,out,path=registered(env);guard=m.ManifestGuard(path,m.sha(path));guard()
    path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(RuntimeError):guard()

def test_internal_guard_is_injected_without_mutating_frozen_global(env,monkeypatch):
    m,out,path=registered(env);original=m.adapter.PinGuard;observed=[]
    def frozen(pin,arm,circuit,output):
        guard=PinGuard({})
        guard();observed.append(True)
        path.write_bytes(path.read_bytes()+b' ')
        guard()
        pytest.fail('guard failed to stop drift')
    monkeypatch.setattr(m.adapter,'run_frozen',frozen)
    with pytest.raises(RuntimeError):m._guarded_frozen(path,m.sha(path),'hybrid','s27',out/'unused')
    assert observed and m.adapter.PinGuard is original

def test_child_failure_keeps_receipt_no_overwrite(env,monkeypatch):
    m,out,path=registered(env);calls=[]
    def child(*args,**kwargs):calls.append(args);return SimpleNamespace(returncode=17,stdout=b'partial',stderr=b'broken')
    monkeypatch.setattr(m.subprocess,'run',child)
    with pytest.raises(RuntimeError):m.execute(path,'hybrid','s27')
    job=out/'jobs'/'hybrid'/'s27'
    assert len(calls)==1 and m.read(job/'failure.json')['returncode']==17
    assert (job/'stdout.log').read_bytes()==b'partial'
    first=(job/'failure.json').read_bytes()
    with pytest.raises(RuntimeError):m.execute(path,'hybrid','s27')
    assert len(calls)==1 and (job/'failure.json').read_bytes()==first

def test_timeout_partial_output_preserved(env,monkeypatch):
    m,out,path=registered(env)
    def child(*a,**k):raise m.subprocess.TimeoutExpired(a[0],3,output=b'partial stdout',stderr=b'partial stderr')
    monkeypatch.setattr(m.subprocess,'run',child)
    with pytest.raises(m.subprocess.TimeoutExpired):m.execute(path,'hybrid','s27')
    job=out/'jobs'/'hybrid'/'s27'
    assert (job/'stdout.log').read_bytes()==b'partial stdout'
    assert (job/'stderr.log').read_bytes()==b'partial stderr'
    assert (job/'failure.json').exists() and not (job/'completion.json').exists()

def test_zero_exit_without_artifacts_is_not_complete(env,monkeypatch):
    m,out,path=registered(env)
    monkeypatch.setattr(m.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=b'fake success',stderr=b''))
    with pytest.raises((RuntimeError,FileNotFoundError)):m.execute(path,'hybrid','s27')
    assert (out/'jobs'/'hybrid'/'s27'/'failure.json').exists()
    assert not (out/'jobs'/'hybrid'/'s27'/'completion.json').exists()

def test_manifest_drift_during_job_is_failure(env,monkeypatch):
    m,out,path=registered(env)
    def child(*a,**k):path.write_bytes(path.read_bytes()+b' ');return SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
    monkeypatch.setattr(m.subprocess,'run',child)
    with pytest.raises(RuntimeError):m.execute(path,'hybrid','s27')
    assert (out/'jobs'/'hybrid'/'s27'/'failure.json').exists()

def test_recipe_and_wrong_pin_rejected(env):
    m,out,path=registered(env);data=m.read(path)
    data['plan']['jobs'][0]['expected_config']['rounds']=1
    data['plan_fingerprint']=m.fingerprint(data['plan'])
    path.write_text(json.dumps(data))
    with pytest.raises(RuntimeError):m.validate_manifest(path)

def test_qa_and_fake_scientific_status_never_complete(env):
    m,out=env;job=m.build_preview(out)['jobs'][0];run=out/'native';run.mkdir(parents=True)
    for simulated,status in [(True,'qa_complete'),(True,'complete'),(False,'complete')]:
        (run/'completion.json').write_text(json.dumps({'status':status,'simulated':simulated}))
        with pytest.raises((RuntimeError,KeyError,FileNotFoundError)):m._verify_run(job,run)

@pytest.mark.parametrize('name',['empty','nosat','unproven'])
def test_nonempty_proof_guard(env,name):
    m,_=env
    log={'empty':'Equivalence successfully proven!', 'nosat':'No SAT model available\nOf those cells 3 are proven and 0 are unproven.\nEquivalence successfully proven!', 'unproven':'Of those cells 2 are proven and 1 are unproven.\nEquivalence successfully proven!'}[name]
    with pytest.raises(RuntimeError):m._proof_points(log)

def test_correct_nonempty_proof_positive(env):
    m,_=env;assert m._proof_points('Of those cells 9 are proven and 0 are unproven.\nEquivalence successfully proven!')

def test_manifest_drift_between_jobs_is_rejected(env):
    m,out,path=registered(env)
    path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(RuntimeError):m.validate_manifest(path)

def test_registration_anchor_is_exclusive(env):
    m,out,path=registered(env)
    anchor=out/'registration.json'
    assert m.read(anchor)['manifest_sha256']==m.sha(path)

@pytest.mark.parametrize('kind',['source','staged_input'])
def test_internal_extra_file_drift_blocks_next_boundary(env,monkeypatch,tmp_path,kind):
    m,out,path=registered(env);p=tmp_path/kind;p.write_bytes(b'initial')
    def frozen(pin,arm,circuit,output):
        guard=PinGuard({});guard();p.write_bytes(b'changed');guard()
    monkeypatch.setattr(m.adapter,'run_frozen',frozen)
    with pytest.raises(RuntimeError):m._guarded_frozen(path,m.sha(path),'hybrid','s27',out/'unused',{p:m.sha(p)})

@pytest.fixture
def synthetic_native(env,monkeypatch,tmp_path):
    """Deliberately forged scientific flags over QA output to attack later bindings.
    No transaction completes, no tool/mapper runs; the real model check remains on.
    """
    m,out=env
    spec=importlib.util.spec_from_file_location('c_native_qa_fixture',HERE/'test_adapter.py')
    q=importlib.util.module_from_spec(spec);sys.modules[spec.name]=q;spec.loader.exec_module(q)
    a=q.module();initial=tmp_path/'input.v';initial.write_text(q.INITIAL,encoding='utf-8')
    backend=q.FakeBackend(a,{'x':[1,3],'y':[2]})
    config=a.Config(rounds=1)
    run=tmp_path/'native'
    result=a.run_schedule(q.INITIAL,config,backend,run,process_runner=q.fake_process,retained_input=initial)
    result['status']='complete';result['simulated']=False
    monkeypatch.setattr(m,'ROOT',tmp_path)
    job={'circuit':'s27','expected_config':m.canonical(__import__('dataclasses').asdict(config)),
         'baseline':{'path':'input.v','sha256':m.sha(initial)}}
    def reseal():
        result.pop('evidence_receipt',None)
        (run/'run_result.json').write_text(json.dumps(result),encoding='utf-8')
        result['evidence_receipt']=m._receipt(run,('completion.json',))
        (run/'completion.json').write_text(json.dumps(result),encoding='utf-8')
    reseal()
    return m,job,run,result,reseal

def test_actual_config_mismatch_even_with_fresh_artifact_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    config=m.read(run/'config.json');config['rounds']=2;(run/'config.json').write_text(json.dumps(config));seal()
    with pytest.raises(RuntimeError,match='configuration'):m._verify_run(job,run)

def test_wrong_retained_bytes_even_with_fresh_artifact_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    (run/'retained_mapped.v').write_text('other');seal()
    with pytest.raises(RuntimeError,match='retained raw'):m._verify_run(job,run)

def test_commit_chain_tamper_even_with_fresh_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    result['commits'][0]['base_sha256']='0'*64;seal()
    with pytest.raises(RuntimeError,match='commit chain'):m._verify_run(job,run)

def test_committed_candidate_changed_even_with_fresh_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    trial=next(t for t in result['trials'] if t['trial_id']==result['commits'][0]['trial_id'])
    (Path(trial['directory'])/'candidate.v').write_text('different');seal()
    with pytest.raises(RuntimeError,match='candidate/base'):m._verify_run(job,run)

def test_proof_empty_even_with_fresh_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    (run/'final_sec'/'sec.log').write_text('Equivalence successfully proven!');seal()
    with pytest.raises(RuntimeError,match='nonempty'):m._verify_run(job,run)

def test_raw_proof_binding_even_with_fresh_receipt(synthetic_native):
    m,job,run,result,seal=synthetic_native
    (run/'final_sec'/'final_raw.v').write_text('other')
    proof=m.read(run/'final_sec'/'result.json');proof['final_sha256']=m.sha(run/'final_sec'/'final_raw.v')
    (run/'final_sec'/'result.json').write_text(json.dumps(proof));seal()
    with pytest.raises(RuntimeError,match='different raw'):m._verify_run(job,run)

def test_unreceipted_extra_artifact_rejected(synthetic_native):
    m,job,run,result,seal=synthetic_native
    (run/'unexpected.txt').write_text('not in receipt')
    with pytest.raises(RuntimeError,match='artifact receipt'):m._verify_run(job,run)

def test_simulation_cannot_upgrade_to_scientific_complete(synthetic_native):
    m,job,run,result,seal=synthetic_native
    result['simulated']=True;seal()
    with pytest.raises(RuntimeError,match='QA/incomplete'):m._verify_run(job,run)

def test_native_run_never_remaps(env,monkeypatch):
    m,out,path=registered(env)
    import backend
    monkeypatch.setattr(m.common,'run_yosys_mapping',lambda *a,**k:pytest.fail('remapping invoked'))
    monkeypatch.setattr(m.adapter.subprocess,'check_output',lambda argv,**kw:'qa-head' if argv[1]=='rev-parse' else '')
    def schedule(initial,config,actual_backend,output,**kwargs):
        assert isinstance(actual_backend,backend.ActualBackend)
        assert initial==(m.ROOT/m.read(path)['plan']['mapped_inputs']['s27']['path']).read_text(encoding='utf-8')
        kwargs['guard']()
        return {'status':'qa_complete','simulated':True}
    monkeypatch.setattr(m.adapter,'run_schedule',schedule)
    r=m._guarded_frozen(path,m.sha(path),'hybrid','s27',out/'notcreated')
    assert r['status']=='qa_complete' and not (out/'notcreated').exists()

def test_staging_failure_also_retains_failed_transaction(env,monkeypatch):
    m,out,path=registered(env);original=m.adapter.write_bytes
    def write(path,data):
        if Path(path).name=='retained_mapped.v':raise OSError('staging unavailable')
        return original(path,data)
    monkeypatch.setattr(m.adapter,'write_bytes',write)
    with pytest.raises(OSError):m.execute(path,'hybrid','s27')
    assert (out/'jobs'/'hybrid'/'s27'/'failure.json').exists()
