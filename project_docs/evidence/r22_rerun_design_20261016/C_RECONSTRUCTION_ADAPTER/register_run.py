"""Explicit C greedy reconstruction transactions, without a new search scheduler.

Preview performs no EDA/tool probes. Registration and each run are separate,
explicit operations after review, commit and completion of the current C-prime
matrix. Retained C mapped inputs are never remapped. Existing runs never resume.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import FunctionType

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=HERE.parent
RUNS_BASE=BASE/'C_RECONSTRUCTION_RUNS'
SCHEMA='r22-C-reconstruction-transaction-v1'
sys.path[:0]=[str(HERE),str(ROOT/'code/src'),str(ROOT/'code/scripts')]
spec=importlib.util.spec_from_file_location('r22_c_frozen_adapter',HERE/'adapter.py')
adapter=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=adapter
spec.loader.exec_module(adapter)
import run_r22_cut_ablation as common

sha=adapter.sha
save=adapter.save

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def canonical(value):return json.loads(json.dumps(value,ensure_ascii=False,sort_keys=True))
def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
def _require(condition,message):
    if not condition:raise RuntimeError(message)
def _rel(path):return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
def _output(path):
    path=Path(path).resolve();base=RUNS_BASE.resolve()
    _require(path!=base and path.is_relative_to(base),'Use a fresh child of C_RECONSTRUCTION_RUNS')
    return path

def _git_identity():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=15).strip()
    # Clean every pinned source/input; generated plans and run receipts live
    # outside this scope and cannot make their own execution dirty.
    paths=set(adapter.source_manifest())|{'code',_rel(HERE),_rel(common.LIB)}
    paths.update(row['path'] for row in read(HERE/'recipe_preview.json')['mapped_inputs'].values())
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*sorted(paths)],cwd=ROOT,text=True,timeout=15)
    return {'head':head,'source_tree_clean':not bool(status.strip())}

def _tool_pin():
    """Read-only identity probes; never called by build-preview."""
    pin={'python':{'path':sys.executable,'sha256':sha(sys.executable),'version':sys.version}}
    for name in ('bash','wsl.exe'):
        path=shutil.which(name)
        _require(path is not None,'Missing tool launcher '+name)
        pin[name]={'path':str(Path(path).resolve()),'sha256':sha(path)}
    for name,binary,flag in [('sta','/usr/local/bin/sta','-version'),('sec_yosys','/usr/bin/yosys','-V')]:
        digest=subprocess.run(['wsl.exe','-d','Ubuntu','--','sha256sum',binary],capture_output=True,text=True,timeout=30,check=True)
        version=subprocess.run(['wsl.exe','-d','Ubuntu','--',binary,flag],capture_output=True,text=True,timeout=30)
        match=re.match(r'([0-9a-f]{64})\s',digest.stdout)
        _require(match is not None and bool((version.stdout+version.stderr).strip()) and version.returncode==0,'Unavailable tool identity '+binary)
        pin[name]={'binary':binary,'sha256':match.group(1),'version':(version.stdout+version.stderr).strip(),'version_returncode':version.returncode,'distribution':'Ubuntu'}
    return pin

def build_preview(output):
    output=_output(output);git=_git_identity();sources=adapter.source_manifest()
    sources[_rel(ROOT/'code/scripts/run_with_timeout.sh')]=sha(ROOT/'code/scripts/run_with_timeout.sh')
    preview=read(HERE/'recipe_preview.json')
    _require(preview['family']=='C-reconstruction-r22' and preview['not_Cprime'] is True,'Wrong reconstruction family')
    _require(len(preview['runs'])==48 and len(preview['mapped_inputs'])==8,'Unexpected C matrix')
    jobs=[]
    for circuit,baseline in preview['mapped_inputs'].items():
        _require(sha(ROOT/baseline['path'])==baseline['sha256'],'Retained input drift: '+circuit)
    for recipe in preview['runs']:
        _require(recipe['historical_runtime_argv'] is None and recipe['historical_runtime_source_pin'] is None,'Unknown historical fields must remain unknown')
        config=canonical(asdict(adapter.Config(**recipe['new_reconstruction_values'])))
        _require(config==recipe['new_reconstruction_values'],'Unexpected implicit configuration')
        arm,circuit=recipe['arm'],recipe['circuit']
        _require(arm in {'hybrid','pureG','pureB','random1','random2','random3'} and circuit in preview['mapped_inputs'],'Wrong C membership')
        command=['bash',str(ROOT/'code/scripts/run_with_timeout.sh'),'3900',sys.executable,'-u','-X','utf8',str(HERE/'register_run.py'),'guarded-run','--manifest',str(output/'manifest.json'),'--arm',arm,'--circuit',circuit]
        jobs.append({'arm':arm,'circuit':circuit,'recipe':recipe,'expected_config':config,
            'baseline':preview['mapped_inputs'][circuit],'job_dir':str(output/'jobs'/arm/circuit),
            'command':command,'outer_timeout_s':3930})
    _require(len({(j['arm'],j['circuit']) for j in jobs})==48,'Duplicate C jobs')
    current=adapter.source_manifest();current[_rel(ROOT/'code/scripts/run_with_timeout.sh')]=sha(ROOT/'code/scripts/run_with_timeout.sh')
    _require(current==sources and _git_identity()==git,'Source changed during preview')
    return {'schema':SCHEMA,'family':'C-reconstruction-r22','status':'review_preview','execution_ready':False,
        'output_dir':str(output),'git':git,'source_manifest':sources,'lib_path':_rel(common.LIB),
        'lib_sha256':sha(common.LIB),'mapped_inputs':preview['mapped_inputs'],'jobs':jobs,
        'recipe_preview_sha256':sha(HERE/'recipe_preview.json'),'scheduler':'Frozen C pass/instance evaluate-all/select-best, then JOINT; no new scheduler',
        'historical_runtime_argv':None,'historical_runtime_source_pin':None,'remapping':False,
        'scientific_budget':'Per-recipe budget retained; external 3900/3930s watchdog yields failure on timeout',
        'eda_executed':False}

def _validate_plan(plan,output):
    _require(plan.get('git',{}).get('source_tree_clean') is True,'Formal execution requires a fresh clean HEAD')
    _require(plan==build_preview(output),'Source/input/library/recipe/HEAD differs from reviewed plan')

def register(plan,output):
    output=_output(output)
    _validate_plan(plan,output)
    _require(not output.exists(),'Output already exists; no overwrite or resume')
    tools=_tool_pin()
    _validate_plan(plan,output)
    manifest={'schema':SCHEMA,'registered':True,'execution_ready':True,'plan':plan,'plan_fingerprint':fingerprint(plan),'tools':tools}
    output.mkdir(parents=True,exist_ok=False)
    save(output/'manifest.json',manifest)
    save(output/'registration.json',{'schema':SCHEMA,'manifest_sha256':sha(output/'manifest.json'),
        'plan_fingerprint':manifest['plan_fingerprint']})
    return manifest

def validate_manifest(path,*,tools=True):
    path=Path(path).resolve();manifest=read(path)
    _require(manifest.get('schema')==SCHEMA and manifest.get('registered') is True and manifest.get('execution_ready') is True,'Not a registered execution manifest')
    plan=manifest['plan'];out=_output(plan['output_dir'])
    _require(path==out/'manifest.json' and manifest['plan_fingerprint']==fingerprint(plan),'Manifest path/fingerprint mismatch')
    anchor=read(out/'registration.json')
    _require(anchor=={'schema':SCHEMA,'manifest_sha256':sha(path),
        'plan_fingerprint':manifest['plan_fingerprint']},'Registered manifest byte drift')
    _validate_plan(plan,out)
    if tools:_require(manifest['tools']==_tool_pin(),'Tool identity drift')
    return manifest

class ManifestGuard:
    def __init__(self,path,expected,files=None):
        self.path=Path(path);self.expected=expected;self.files=adapter.PinGuard(files or {})
    def __call__(self):
        _require(self.path.is_file() and sha(self.path)==self.expected,'Manifest byte drift')
        self.files()

def _job(manifest,arm,circuit):
    jobs=[j for j in manifest['plan']['jobs'] if (j['arm'],j['circuit'])==(arm,circuit)]
    _require(len(jobs)==1,'Unregistered arm/circuit')
    return jobs[0]

def _frozen_pin(manifest):
    p=manifest['plan']
    # Adapter checks its source manifest exactly; wrapper also pins watchdog separately.
    sources=dict(p['source_manifest']);sources.pop(_rel(ROOT/'code/scripts/run_with_timeout.sh'),None)
    actual=adapter.source_manifest()
    if _rel(ROOT/'code/scripts/run_with_timeout.sh') in actual:
        sources[_rel(ROOT/'code/scripts/run_with_timeout.sh')]=p['source_manifest'][_rel(ROOT/'code/scripts/run_with_timeout.sh')]
    _require(sources==actual,'Frozen adapter source pin mismatch')
    return {'execution_ready':True,'family':p['family'],'git_head':p['git']['head'],
        'source_manifest':sources,'lib_sha256':p['lib_sha256'],'mapped_inputs':p['mapped_inputs']}

def _guarded_frozen(path,digest,arm,circuit,output,extra_files=None):
    manifest=read(path);native_guard=adapter.PinGuard
    extra_files=dict(extra_files or {})
    anchor=Path(path).parent/'registration.json'
    extra_files[anchor]=sha(anchor)
    class GuardedPin:
        def __init__(self,files):
            merged={**files,**(extra_files or {}),Path(path):digest}
            self.guard=ManifestGuard(path,digest,merged)
        def __call__(self):self.guard()
    function=adapter.run_frozen
    clone=FunctionType(function.__code__,{**function.__globals__,'PinGuard':GuardedPin},function.__name__,function.__defaults__,function.__closure__)
    clone.__kwdefaults__=function.__kwdefaults__
    ManifestGuard(path,digest,extra_files)()
    result=clone(_frozen_pin(manifest),arm,circuit,Path(output))
    ManifestGuard(path,digest,extra_files)()
    return result

def _receipt(directory,exclude=()):
    directory=Path(directory)
    _require(not any(p.is_symlink() for p in directory.rglob('*')),'Symlink artifact refused')
    return {p.relative_to(directory).as_posix():sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.relative_to(directory).as_posix() not in exclude}

def _proof_points(log):
    points=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)
    _require(bool(points) and all(int(p)>0 and int(u)==0 for p,u in points)
        and 'Equivalence successfully proven!' in log and re.search(r'No\s+SAT\s+model\s+available',log,re.I) is None,'SEC has no nonempty supported proof')
    return points

def _verify_models(initial,final,circuit,run):
    from backend import ActualBackend
    with tempfile.TemporaryDirectory(prefix='r22_C_static_verify_') as folder:
        expected=ActualBackend(circuit).prepare_sec(initial,final,Path(folder)/'preflight')
        for name,text in expected['splits'].items():
            _require((run/'final_sec'/name).read_text(encoding='utf-8')==text,'SEC split/helper mismatch '+name)
        _require(sha(run/'final_sec'/'cells.v')==expected['model_sha256'],'Actual Liberty model mismatch')
        binding=read(run/'sec_preflight'/'binding.json')
        _require(binding['splits']==expected['splits'] and binding['model_sha256']==expected['model_sha256'],'Independent model preflight binding mismatch')
        _require(sha(Path(binding['model_path']))==binding['model_sha256'],'Preflight model changed')

def _verify_run(job,run):
    run=Path(run);result=read(run/'completion.json')
    _require(result.get('status')=='complete' and result.get('simulated') is False,'QA/incomplete result is not scientific completion')
    _require(result['evidence_receipt']==_receipt(run,('completion.json',)),'Native complete artifact receipt mismatch')
    raw=read(run/'run_result.json')
    _require(raw=={k:v for k,v in result.items() if k!='evidence_receipt'},'Native completion/result differ')
    _require(read(run/'config.json')==job['expected_config'],'Actual configuration differs from registered recipe')
    _require(sha(run/'retained_mapped.v')==job['baseline']['sha256'],'Wrong retained raw input')
    initial=(ROOT/job['baseline']['path']).read_text(encoding='utf-8');final=(run/'final.v').read_text(encoding='utf-8')
    _require((run/'initial.v').read_text(encoding='utf-8')==initial,'Actual initial design mismatch')
    _require(result['initial_sha256']==adapter.text_sha(initial) and result['final_sha256']==adapter.text_sha(final) and result['final_text']==final,'Initial/final text identity mismatch')
    counts=result['counts']
    _require(counts['commits']==len(result['commits']) and counts['failed_launch_attempts']==0 and counts['sta_launches']==counts['sta_reservations'],'STA/commit accounting mismatch')
    wns=result['final_metrics']['wns']
    _require(isinstance(wns,(int,float)) and math.isfinite(wns),'Missing finite final STA')
    current=adapter.text_sha(initial)
    trials={row['trial_id']:row for row in result['trials']}
    for number,commit in enumerate(result['commits']):
        _require(commit['commit_id']==number and commit['base_sha256']==current,'Broken commit chain')
        _require(read(run/('commit_%06d.json'%number))==commit,'Commit receipt mismatch')
        trial=trials[commit['trial_id']];directory=Path(trial['directory']).resolve()
        _require(directory.is_relative_to(run.resolve()),'Trial outside registered run')
        _require(read(directory/'decision.json')==trial and trial['status']=='measured','Commit not bound to measured trial')
        _require(commit['action']==trial['action'] and commit['base_sha256']==trial['base_sha256'] and commit['candidate_sha256']==trial['candidate_sha256'],'Wrong trial/commit association')
        _require(sha(directory/'base.v')==current and sha(directory/'candidate.v')==commit['candidate_sha256'],'Commit candidate/base bytes differ')
        current=commit['candidate_sha256']
    _require(current==result['final_sha256'],'Final design not end of commit chain')
    sec=run/'final_sec';proof=read(sec/'result.json')
    _require(proof['status']=='pass' and proof['returncode']==0 and result['sec_status']=='pass' and result['sec_bound'] is True and result['sec_nonempty_supported_proof'] is True,'SEC failed or unbound')
    _require(proof['initial_sha256']==sha(sec/'initial_raw.v') and proof['final_sha256']==sha(sec/'final_raw.v') and proof['shared_helpers_sha256']==sha(sec/'helpers.v'),'SEC raw receipt mismatch')
    _require((sec/'initial_raw.v').read_text(encoding='utf-8')==initial and (sec/'final_raw.v').read_text(encoding='utf-8')==final,'SEC proved different raw designs')
    _proof_points((sec/'sec.log').read_text(encoding='utf-8'))
    _verify_models(initial,final,job['circuit'],run)
    return result

def _association(manifest,path,digest,job):
    return {'schema':SCHEMA,'manifest_path':str(Path(path).resolve()),'manifest_sha256':digest,
        'registration_sha256':sha(Path(path).parent/'registration.json'),
        'plan_fingerprint':manifest['plan_fingerprint'],'job':job,'frozen_pin':_frozen_pin(manifest),'tools':manifest['tools']}

def guarded_run(path,arm,circuit):
    path=Path(path).resolve();digest=sha(path);manifest=validate_manifest(path);job=_job(manifest,arm,circuit)
    directory=Path(job['job_dir']);preregistered=directory/'preregistered.json'
    _require(read(preregistered)==_association(manifest,path,digest,job),'Preregistration differs from complete registered pin')
    extra={preregistered:sha(preregistered),directory/'retained_mapped.v':job['baseline']['sha256']}
    save(directory/'actual_run.json',_association(manifest,path,digest,job))
    extra[directory/'actual_run.json']=sha(directory/'actual_run.json')
    _guarded_frozen(path,digest,arm,circuit,directory/'run',extra)
    ManifestGuard(path,digest,extra)();validate_manifest(path)
    _verify_run(job,directory/'run')

def execute(path,arm,circuit):
    path=Path(path).resolve();digest=sha(path);manifest=validate_manifest(path);job=_job(manifest,arm,circuit)
    guard=ManifestGuard(path,digest);guard();directory=Path(job['job_dir'])
    _require(not directory.exists(),'Job already exists; no automatic resume/overwrite')
    directory.mkdir(parents=True,exist_ok=False)
    code=None
    try:
        save(directory/'preregistered.json',_association(manifest,path,digest,job))
        adapter.write_bytes(directory/'retained_mapped.v',(ROOT/job['baseline']['path']).read_bytes())
        guard();validate_manifest(path)
        process=subprocess.run(job['command'],cwd=ROOT,capture_output=True,timeout=job['outer_timeout_s'])
        code=process.returncode
        adapter.write_bytes(directory/'stdout.log',process.stdout);adapter.write_bytes(directory/'stderr.log',process.stderr)
        guard();validate_manifest(path)
        _require(code==0,'Native C child failed: '+str(code))
        expected=_association(manifest,path,digest,job)
        _require(read(directory/'actual_run.json')==expected and read(directory/'preregistered.json')==expected,'Actual/preregistered pin differs')
        _require(sha(directory/'retained_mapped.v')==job['baseline']['sha256'],'Staged input changed')
        result=_verify_run(job,directory/'run')
        guard();validate_manifest(path)
        save(directory/'completion.json',{'schema':SCHEMA,'status':'complete','simulated':False,
            'association':expected,'native_completion_sha256':sha(directory/'run'/'completion.json'),
            'evidence_receipt':_receipt(directory,('completion.json',))})
        return result
    except Exception as error:
        if isinstance(error,subprocess.TimeoutExpired):
            for name,data in [('stdout.log',error.stdout),('stderr.log',error.stderr)]:
                if not (directory/name).exists():adapter.write_bytes(directory/name,data)
        save(directory/'failure.json',{'schema':SCHEMA,'status':'failed','manifest_sha256':digest,
            'returncode':code,'error_type':type(error).__name__,'error':str(error),
            'evidence_receipt':_receipt(directory,('failure.json',))})
        raise

def verify(path,arm,circuit):
    path=Path(path).resolve();digest=sha(path);manifest=validate_manifest(path);job=_job(manifest,arm,circuit)
    directory=Path(job['job_dir']);_require(not (directory/'failure.json').exists(),'Failed job never complete')
    complete=read(directory/'completion.json');association=_association(manifest,path,digest,job)
    _require(complete['status']=='complete' and complete['simulated'] is False and complete['association']==association,'Wrong completion pin')
    _require(complete['evidence_receipt']==_receipt(directory,('completion.json',)),'Transaction artifact drift')
    _require(read(directory/'preregistered.json')==association and read(directory/'actual_run.json')==association,'Actual/preregistered association mismatch')
    _require(sha(directory/'run'/'completion.json')==complete['native_completion_sha256'],'Native completion drift')
    result=_verify_run(job,directory/'run')
    ManifestGuard(path,digest)();validate_manifest(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('build-preview');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--plan',type=Path,required=True)
    p=sub.add_parser('register');p.add_argument('--plan',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    for name in ('run','guarded-run','verify'):
        p=sub.add_parser(name);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--arm',required=True);p.add_argument('--circuit',required=True)
    args=parser.parse_args()
    if args.mode=='build-preview':
        _require(not args.plan.resolve().is_relative_to(HERE.resolve()),'Review plan must live outside source_manifest adapter directory')
        args.plan.parent.mkdir(parents=True,exist_ok=True);save(args.plan,build_preview(args.output_dir))
        print('Preview only: 48 recipes, retained C inputs, no EDA; execution_ready=false');return 0
    if args.mode=='register':register(read(args.plan),args.output_dir);print('Registered 48 explicit C jobs; no experiment launched');return 0
    if args.mode=='guarded-run':guarded_run(args.manifest,args.arm,args.circuit)
    else:
        result=(execute if args.mode=='run' else verify)(args.manifest,args.arm,args.circuit)
        print(json.dumps({key:result[key] for key in ('status','counts','sec_status')}))
    return 0

if __name__=='__main__':raise SystemExit(main())
