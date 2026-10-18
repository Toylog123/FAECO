"""B3 same-family reconstruction transactions; no search or batch scheduler.

Preview is read-only. Register/run require explicit operator invocation after
review and a clean, frozen source pin. This adapter always reuses raw mapped
inputs and calls the existing outerloop; it never substitutes C's greedy loop.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ADAPTER=Path(__file__).resolve()
ROOT=ADAPTER.parents[4]
BASE=ADAPTER.parent.parent
sys.path[:0]=[str(ROOT/'code/src'),str(ROOT/'code/scripts')]
import run_r22_cut_ablation as common
import run_outerloop_real_wns as runner
from rseco.feedback import LEGACY_CONFIG
from rseco.gate_sizing import parse_mapped_netlist
from rseco.logic_rewrite import parse_liberty_cells
from rseco.real_wns import (RealWnsEvaluator, validate_cell_input_connections,
                           two_state_sec_unsupported_reason, write_liberty_cell_models)
from rseco.sta_ledger import summarize_sta_ledger

LIB=common.LIB
CHECKER=BASE/'x_identity_certificate.py'
TABLE=ROOT/'code/src/rseco/strategy_priority_table.json'
DESIGN=BASE/'B3_RERUN_DESIGN.json'
final_sec=common.final_sec
SCHEMA='r22-B3-reconstruction-transaction-v1'
INPUTS={
 'b09':{'path':'experiments/20260826_itc99_main/b09/b09/mapped.v','sha256':'7f80e3b9c97d70a4af8a5ca3ab67adc87ed5046bea3f92b018c871d4f8b14337','rtl':'data/raw/benchmarks/raw/itc99/v/b09.v'},
 'b20':{'path':'experiments/20260826_itc99_main/b20/b20/mapped.v','sha256':'4a800657a0f64f997fb8d440b5fcc125721b58dd16842524ee9957644a64f377','rtl':'data/raw/benchmarks/raw/itc99/v/b20.v'},
 'b21':{'path':'experiments/20260826_itc99_main/b21/b21/mapped.v','sha256':'5067fd16ecc1af7a3187479817fe4bc918495a4a02b6c2302f4d436f809b9563','rtl':'data/raw/benchmarks/raw/itc99/v/b21.v'},
}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def text_sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def fingerprint(value):return text_sha(json.dumps(value,sort_keys=True,ensure_ascii=False))
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save_new(path,value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2);handle.write('\n')


def _rel(path):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise RuntimeError('Path outside repository')
    return path.relative_to(ROOT.resolve()).as_posix()


def _output(path):
    path=Path(path).resolve();container=(BASE/'B3_RECONSTRUCTION_RUNS').resolve()
    if path==container or not path.is_relative_to(container):
        raise RuntimeError('New B3 output must be a new child of B3_RECONSTRUCTION_RUNS')
    return path


def _git_identity():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=15).strip()
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','code',_rel(ADAPTER),_rel(CHECKER)],cwd=ROOT,text=True,timeout=15)
    return {'head':head,'source_tree_clean':not bool(status.strip())}


def _production_manifest():return common.source_manifest()


def source_pin():
    files=dict(_production_manifest())
    files.update({_rel(path):sha(path) for path in (ADAPTER,CHECKER,TABLE)})
    return {**_git_identity(),'files':files}


def _tool_pin():
    """Read-only binary/version identities; only formal registration/run calls this."""
    pin={}
    for name,binary,flag in [('sta','/usr/local/bin/sta','-version'),('sec_yosys','/usr/bin/yosys','-V'),('topology_abc','/usr/bin/yosys-abc','-h')]:
        digest=subprocess.run(['wsl.exe','-d','Ubuntu','--','sha256sum',binary],capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=30,check=True)
        version=subprocess.run(['wsl.exe','-d','Ubuntu','--',binary,flag],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
        match=re.match(r'([0-9a-f]{64})\s',digest.stdout)
        if not match:raise RuntimeError('Unavailable binary hash: '+binary)
        pin[name]={'binary':binary,'sha256':match.group(1),'version':(version.stdout+version.stderr).strip(),'version_returncode':version.returncode}
    return pin


def _resolved(command):
    previous=sys.argv
    try:
        sys.argv=command[4:]
        return {k:str(v) if isinstance(v,Path) else v for k,v in vars(runner.parse_args()).items()}
    finally:sys.argv=previous


def build_plan(output):
    output=_output(output);pin=source_pin();design=read_json(DESIGN)
    if set(INPUTS)!={'b09','b20','b21'}:raise RuntimeError('B3 membership changed')
    jobs=[];provenance={_rel(DESIGN):sha(DESIGN),_rel(LIB):sha(LIB),_rel(TABLE):sha(TABLE)}
    for circuit,baseline in INPUTS.items():
        if not any(row['circuit']==circuit and row['raw_input_path']==baseline['path'] for row in design['runs']):
            raise RuntimeError('Recovered B3 input identity differs from design')
        if sha(ROOT/baseline['path'])!=baseline['sha256']:raise RuntimeError('Frozen B3 input changed: '+circuit)
        for name in (baseline['path'],baseline['rtl']):provenance[name]=sha(ROOT/name)
        command=[sys.executable,'-u','-X','utf8',str(ROOT/'code/scripts/run_outerloop_real_wns.py'),
            '--circuit',circuit,'--source-file',str(ROOT/baseline['rtl']),
            '--iscas89-dir',str(ROOT/'data/raw/benchmarks/raw/itc99/v'),'--output-dir',str(output),
            '--period','0.5','--clock-port','CK','--max-iterations','8','--max-patches','8',
            '--candidates-per-iteration','1','--workers','1','--max-instances','8',
            '--joint-k','0','--joint-enumerate-depth','3','--strategies','R,G,B',
            '--enable-buffer','--tns-aware','--early-stop','--feedback-legacy','--no-proxy-ranking',
            '--skip-mapping','--cut-search-policy','legacy','--cut-sources','full','--node-cost-mode','configured',
            '--priority-table',str(TABLE),'--epsilon','0','--required-metrics','setup_wns,setup_tns']
        for flag in ['boundary-penalty','size-penalty','critical-coverage-reward','verification-cost-penalty','equivalence-stability-reward']:
            command+=['--init-'+flag,'1']
        expected={'argv':command[4:],'resolved_args':_resolved(command),'enable_feedback':True,
            'feedback_config_name':'legacy','feedback_config':asdict(LEGACY_CONFIG),'random_order':False,
            'seed':None,'adaptive_ucb_decision_layer':False,'structure_resynth':False}
        jobs.append({'circuit':circuit,'baseline':dict(baseline),'output_dir':str(output/circuit),
                     'command':command,'expected_run_config':expected})
    signature=inspect.signature(RealWnsEvaluator)
    if source_pin()!=pin:raise RuntimeError('Source changed while building preview')
    return {'schema':SCHEMA,'family':'B3-same-family-explicit-reconstruction','status':'review_preview',
        'execution_ready':False,'historical_argv':None,'historical_runtime_revision':None,
        'output_dir':str(output),'source_pin':pin,'provenance':provenance,'liberty':_rel(LIB),
        'jobs':jobs,'historical_parallel_circuits':2,'external_parallel_limit':2,
        'scheduler':'none added; one explicit registered circuit transaction per invocation',
        'runner_watchdog_s':14400,'outer_watchdog_s':14430,'scientific_sta_formal_wall_budgets':None,
        'reconstruction_choices':{'priority_table':{'path':_rel(TABLE),'sha256':sha(TABLE),'reason':'Freeze the existing canonical table as a new reconstruction choice; original runtime table is unknown.'},
            'max_instances':8,'joint_k':0,'topology_enabled':True,'UCB_adaptive':False,'EMA_feedback':False,
            'reason':'Nearby historical defaults are reconstruction choices, not recovered runtime argv. Legacy cut/feedback and documented beam1/B/TNS/inner-first-improvement are retained.',
            'max_patch_ratio':signature.parameters['max_patch_ratio'].default,
            'max_verification_time_s':signature.parameters['max_verification_time_s'].default,
            'watchdog_reason':'External hang monitor only; timeout is an explicit incomplete failure, never a smaller scientific wall budget.'},
        'eda_executed_at_preview':False}


def validate_plan(plan,output,*,require_clean=False):
    if require_clean and not plan.get('source_pin',{}).get('source_tree_clean'):
        raise RuntimeError('Formal registration requires clean source/adapter/checker')
    if build_plan(output)!=plan:raise RuntimeError('Source/input/library/configuration changed from reviewed plan')


def register_plan(plan,output):
    output=_output(output)
    validate_plan(plan,output,require_clean=True)
    if output.exists():raise RuntimeError('Output already exists; refuse overwrite')
    tools=_tool_pin()
    for job in plan['jobs']:
        initial=(ROOT/job['baseline']['path']).read_text(encoding='utf-8')
        _domain(initial,initial)
    validate_plan(plan,output,require_clean=True)
    manifest={'schema':SCHEMA,'registered':True,'plan':plan,'plan_fingerprint':fingerprint(plan),'tools':tools}
    output.mkdir(parents=True,exist_ok=False)
    save_new(output/'manifest.json',manifest)
    return manifest


def validate_manifest(manifest):
    if manifest.get('schema')!=SCHEMA or manifest.get('registered') is not True:
        raise RuntimeError('Formal registered B3 manifest required')
    plan=manifest['plan'];validate_plan(plan,plan['output_dir'],require_clean=True)
    if manifest.get('plan_fingerprint')!=fingerprint(plan):raise RuntimeError('Manifest fingerprint changed')
    path=Path(plan['output_dir'])/'manifest.json'
    if read_json(path)!=manifest:raise RuntimeError('Registered manifest changed on disk/in memory')
    if _tool_pin()!=manifest['tools']:raise RuntimeError('Tool binary/version pin changed')


def _job(manifest,circuit):
    found=[job for job in manifest['plan']['jobs'] if job['circuit']==circuit]
    if len(found)!=1:raise RuntimeError('Unknown B3 circuit')
    return found[0]


def _domain(initial,final):
    cells=parse_liberty_cells(LIB.read_text(encoding='utf-8'))
    for text in (initial,final):
        validate_cell_input_connections(text,cells)
        unsupported=two_state_sec_unsupported_reason(text,cells)
        if unsupported:raise RuntimeError('Independent SEC unsupported: '+unsupported)
    spec=importlib.util.spec_from_file_location('_b3_x_certificate',CHECKER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    certificate=module.certify_pair(initial,final)
    if not certificate['certified']:raise RuntimeError('X isolation certificate rejected: '+certificate['reason'])
    return certificate


def _used_types(initial,final):return {cell.cell_type for cell in parse_mapped_netlist(initial+'\n'+final)}


def _sec_script(out,circuit=None):
    circuit=circuit or out.parent.name
    return '\n'.join([f'read_verilog "{common._to_wsl(out/"cells.v")}"',f'read_verilog "{common._to_wsl(out/"helpers.v")}"',
        f'read_verilog "{common._to_wsl(out/"gold.v")}"','rename '+circuit+' gold',
        f'read_verilog "{common._to_wsl(out/"gate.v")}"','rename '+circuit+' gate',
        'proc','memory','equiv_make gold gate equiv','hierarchy -top equiv','flatten','opt_clean',
        'equiv_simple','equiv_induct -seq 10','equiv_status -assert',''])


def _artifacts(out):
    return {p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*'))
            if p.is_file() and not (p.parent==out and p.name in {'completion.json','failure.json'})}


def _write_bytes_new(path,data):
    with Path(path).open('xb') as handle:handle.write(data)


def _sta_local_path(value):
    """Resolve only the absolute WSL paths emitted by the frozen generators."""
    if not re.fullmatch(r'[^\s{}\[\]$;\\"#]+',value):raise RuntimeError('Unsupported dynamic/quoted STA path')
    prefix=common._to_wsl(ROOT).rstrip('/')+'/'
    if not value.startswith(prefix):raise RuntimeError('STA input path is outside the pinned repository')
    path=(ROOT/value[len(prefix):]).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise RuntimeError('STA input escapes pinned repository')
    return path


def _sta_tcl_inputs(raw,out,circuit):
    text=raw.decode('utf-8');files={};links=[];clocks=[]
    patterns=[r'report_checks -path_delay (?:max|min)(?: -slack_max 0 -endpoint_count 100000)?',
              r'report_worst_slack -(?:max|min)',r'report_tns',r'puts "TNS_(?:BEGIN|END)"',
              r'set_clock_uncertainty -hold [0-9.eE+-]+ \[get_clocks clk\]']
    for line in text.splitlines():
        if not line:continue
        match=re.fullmatch(r'(read_liberty|read_verilog) (\S+)',line)
        if match:
            kind=match.group(1)
            if kind in files:raise RuntimeError('Multiple STA '+kind+' commands are unsupported')
            files[kind]=_sta_local_path(match.group(2));continue
        if line.startswith('link_design '):links.append(line);continue
        if line.startswith('create_clock '):clocks.append(line);continue
        if not any(re.fullmatch(pattern,line) for pattern in patterns):
            raise RuntimeError('Unsupported generated STA TCL syntax: '+line)
    if set(files)!={'read_liberty','read_verilog'} or links!=['link_design '+circuit] or clocks!=['create_clock -name clk -period 0.5 [get_ports CK]']:
        raise RuntimeError('STA TCL input/top/clock binding differs from registered B3 grammar')
    if files['read_liberty']!=LIB.resolve():raise RuntimeError('STA TCL Liberty differs from pinned library')
    if not files['read_verilog'].is_relative_to(Path(out).resolve()):raise RuntimeError('STA netlist is outside this job')
    return {'netlist':files['read_verilog'],'liberty':files['read_liberty']}


def _current_input_hashes(inputs):
    observed={}
    for key in ('script','netlist','liberty'):
        try:observed[key]=sha(inputs[key]['path'])
        except OSError as error:observed[key]={'error_type':type(error).__name__,'error':str(error)}
    return observed


def _begin_sta_attempt(attempt,script,out,circuit,manifest,command):
    raw=Path(script).read_bytes();_write_bytes_new(attempt/'sta.tcl',raw)
    paths=_sta_tcl_inputs(raw,out,circuit)
    netlist=paths['netlist'].read_bytes();_write_bytes_new(attempt/'netlist.v',netlist)
    inputs={'command':list(command),'script':{'path':str(Path(script).resolve()),'sha256':sha(attempt/'sta.tcl'),'snapshot':'sta.tcl','bytes':len(raw)},
            'netlist':{'path':str(paths['netlist']),'sha256':sha(attempt/'netlist.v'),'snapshot':'netlist.v','bytes':len(netlist)},
            'liberty':{'path':str(paths['liberty']),'sha256':sha(paths['liberty'])}}
    save_new(attempt/'inputs.json',inputs)
    if inputs['liberty']['sha256']!=manifest['plan']['provenance'][_rel(LIB)]:raise RuntimeError('STA Liberty input drift before launch')
    if _current_input_hashes(inputs)!={key:inputs[key]['sha256'] for key in ('script','netlist','liberty')}:
        raise RuntimeError('STA input drift while staging before launch')
    return inputs


def _output_bytes(attempt,name,value):
    if value is None:kind='none';raw=b''
    elif isinstance(value,bytes):kind='bytes';raw=value
    elif isinstance(value,str):kind='utf8_text';raw=value.encode('utf-8')
    else:raise RuntimeError('Unsupported subprocess output type: '+type(value).__name__)
    path=attempt/(name+'.bin');_write_bytes_new(path,raw)
    return {'path':path.name,'sha256':sha(path),'bytes':len(raw),'kind':kind}


def _finish_sta_attempt(attempt,inputs,*,answer=None,error=None):
    current=_current_input_hashes(inputs)
    if error is None:launched=True;confirmation='run_api_completed'
    elif isinstance(error,subprocess.TimeoutExpired):launched=True;confirmation='run_api_timeout'
    elif isinstance(error,subprocess.CalledProcessError):launched=True;confirmation='run_api_completed_nonzero'
    elif isinstance(error,(FileNotFoundError,PermissionError)):launched=False;confirmation='known_prelaunch_os_error'
    else:launched=None;confirmation='unconfirmed_exception'
    result={'process_launched':launched,'launch_confirmation':confirmation,'status':'returned' if error is None else 'exception',
            'returncode':getattr(answer if error is None else error,'returncode',None),
            'inputs_sha256':sha(attempt/'inputs.json'),'inputs_after':current,
            'input_drift':current!={key:inputs[key]['sha256'] for key in ('script','netlist','liberty')},
            'output_scope':'subprocess API values; timeout output may be partial, text values encoded as UTF-8',
            'stdout':_output_bytes(attempt,'stdout',getattr(answer if error is None else error,'stdout',None)),
            'stderr':_output_bytes(attempt,'stderr',getattr(answer if error is None else error,'stderr',None))}
    if error is not None:
        result.update(error_type=type(error).__name__,error=str(error))
        if isinstance(error,subprocess.TimeoutExpired):result['timeout_s']=error.timeout
    save_new(attempt/'result.json',result)
    return result


def _verify_sta_attempt(out,launch,returned,manifest,circuit):
    attempt=out/'sta_attempts'/f'{launch["id"]:06d}'
    if launch.get('attempt_dir')!=str(attempt) or returned.get('attempt_dir')!=str(attempt):raise RuntimeError('STA attempt directory binding changed')
    inputs=read_json(attempt/'inputs.json');result=read_json(attempt/'result.json')
    if launch.get('inputs_sha256')!=sha(attempt/'inputs.json') or returned.get('result_sha256')!=sha(attempt/'result.json') or result.get('inputs_sha256')!=launch['inputs_sha256']:
        raise RuntimeError('STA attempt receipt hash changed')
    if launch.get('script')!=inputs['script']['path'] or launch.get('script_sha256')!=inputs['script']['sha256'] or launch.get('command')!=inputs['command']:
        raise RuntimeError('STA launch input binding changed')
    if inputs['liberty']!={'path':str(LIB.resolve()),'sha256':manifest['plan']['provenance'][_rel(LIB)]}:
        raise RuntimeError('STA attempt Liberty pin changed')
    paths=_sta_tcl_inputs((attempt/'sta.tcl').read_bytes(),out,circuit)
    if str(paths['netlist'])!=inputs['netlist']['path']:raise RuntimeError('STA snapshot TCL/netlist binding changed')
    for key,name in [('script','sta.tcl'),('netlist','netlist.v')]:
        path=attempt/name
        if inputs[key].get('snapshot')!=name or inputs[key].get('sha256')!=sha(path) or inputs[key].get('bytes')!=path.stat().st_size:
            raise RuntimeError('STA exact input snapshot changed')
    if result.get('process_launched') is not True or result.get('status') not in {'returned','exception'} or result.get('input_drift') is not False or result.get('inputs_after')!={key:inputs[key]['sha256'] for key in ('script','netlist','liberty')}:
        raise RuntimeError('STA attempt has unconfirmed launch, input drift or incomplete result')
    for key in ('stdout','stderr'):
        item=result[key];path=attempt/(key+'.bin')
        if item.get('path')!=path.name or item.get('kind') not in {'none','bytes','utf8_text'} or item.get('sha256')!=sha(path) or item.get('bytes')!=path.stat().st_size:
            raise RuntimeError('STA complete output artifact changed/truncated')
    if returned.get('returncode')!=result['returncode'] or returned.get('error')!=result.get('error'):
        raise RuntimeError('STA return trace differs from result artifact')
    return attempt/'netlist.v'


def _run_outputs(job,manifest):
    out=Path(job['output_dir']);result=read_json(out/'outerloop_result.json');config=read_json(out/'run_config.json')
    for key,value in job['expected_run_config'].items():
        if config.get(key)!=value:raise RuntimeError('Actual run configuration changed: '+key)
    if config.get('git_head')!=manifest['plan']['source_pin']['head']:raise RuntimeError('Runner source HEAD changed')
    if result.get('cut_search_policy')!='legacy' or result.get('enable_topology') is not True:
        raise RuntimeError('B3 method changed')
    initial=(out/'mapped.v').read_text(encoding='utf-8');state=result['state'];current=initial
    for patch in state['accepted_patches']:
        if patch['base_netlist_hash']!=text_sha(current):raise RuntimeError('Accepted state chain has wrong base')
        current=patch['netlist_text']
        if patch['candidate_hash']!=text_sha(current) or patch['netlist_hash']!=text_sha(current):raise RuntimeError('Accepted candidate hash mismatch')
    if current!=state['current_netlist_text'] or state['current_netlist_hash']!=text_sha(current):
        raise RuntimeError('Actual final state text/hash does not match committed chain')
    budget=state['budget']
    for key,value in {'max_iterations':8,'max_patches':8,'epsilon':0.0,'sta_budget':None,'formal_budget':None,'wall_timeout_s':None}.items():
        if budget.get(key)!=value:raise RuntimeError('Scientific budget differs: '+key)
    if len(state['accepted_patches'])>8:raise RuntimeError('Too many commits')
    ledger=read_json(out/'eval_trials.json')
    if 'sta_launch_events' not in ledger:raise RuntimeError('Missing STA launch events')
    events=ledger['sta_launch_events'];counts=summarize_sta_ledger(ledger['trials'],result['baseline_wns'],events)
    n=counts['n_new_sta_runs']
    if n!=result['n_new_sta_runs'] or n!=budget.get('sta_used'):raise RuntimeError('STA launch/reservation count mismatch')
    if counts['n_candidate_evaluation_records']!=result['n_candidate_sta_runs'] or counts['n_candidate_evaluation_records']!=result['n_candidate_evaluation_records']:
        raise RuntimeError('Candidate evaluation count mismatch')
    candidate_events=[event for event in events if event.get('kind')=='candidate_ideal']
    if sorted(e['seq'] for e in candidate_events)!=list(range(1,n+1)):raise RuntimeError('Incomplete launch sequence')
    by_seq={event['seq']:event for event in candidate_events}
    for trial in ledger['trials']:
        if trial.get('sta_executed') is True:
            event=by_seq.get(trial.get('sta_launch_seq'))
            if event is None or any(trial.get(key)!=event.get(key) for key in ('candidate_hash','base_netlist_hash')):
                raise RuntimeError('Candidate trial does not match its actual launch identity')
    committed={trial.get('candidate_hash') for trial in ledger['trials'] if trial.get('committed') is True}
    patch_hashes={patch['candidate_hash'] for patch in state['accepted_patches']}
    if committed!=patch_hashes:raise RuntimeError('Committed candidate identities differ from accepted state chain')
    for event in candidate_events:
        path=Path(event['report_dir'])/'mapped.v'
        if not path.resolve().is_relative_to(out.resolve()) or text_sha(path.read_text(encoding='utf-8'))!=event['candidate_hash']:
            raise RuntimeError('Launched candidate file does not match event identity')
    trace=[json.loads(line) for line in (out/'tool_launches.jsonl').read_text(encoding='utf-8').splitlines() if line]
    launches=[e for e in trace if e.get('event')=='launch'];returns=[e for e in trace if e.get('event')=='return']
    if sorted(e['id'] for e in launches)!=list(range(1,len(launches)+1)) or sorted(e['id'] for e in returns)!=list(range(1,len(launches)+1)):
        raise RuntimeError('Incomplete actual STA process-attempt trace')
    if len(trace)!=len(launches)+len(returns) or any(trace[2*i].get('event')!='launch' or trace[2*i+1].get('event')!='return' or trace[2*i]['id']!=i+1 or trace[2*i+1]['id']!=i+1 for i in range(len(launches))):
        raise RuntimeError('Rejected, reordered or unclassified STA attempt trace')
    snapshots={event['id']:_verify_sta_attempt(out,event,returns[index],manifest,job['circuit']) for index,event in enumerate(launches)}
    if {p.name for p in (out/'sta_attempts').iterdir()}!={f'{e["id"]:06d}' for e in launches}:
        raise RuntimeError('Untraced extra STA attempt artifact directory')
    expected=Counter(str((Path(e['report_dir'])/'sta.tcl').resolve()) for e in candidate_events)
    actual=Counter(str(Path(e['script']).resolve()) for e in launches if str(Path(e['script']).resolve()) in expected)
    if expected!=actual:raise RuntimeError('STA ledger does not match actual candidate process attempts')
    by_script={str((Path(e['report_dir'])/'sta.tcl').resolve()):e for e in candidate_events}
    for launch in launches:
        event=by_script.get(str(Path(launch['script']).resolve()))
        if event is not None and text_sha(snapshots[launch['id']].read_text(encoding='utf-8'))!=event['candidate_hash']:
            raise RuntimeError('Actual STA snapshot differs from ledger candidate identity')
    baseline=0;refresh=0
    for event in launches:
        script=Path(event['script']).resolve()
        if str(script) in expected:continue
        if script==(out/'sta.tcl').resolve():
            inputs=read_json(out/'sta_attempts'/f'{event["id"]:06d}'/'inputs.json')
            if inputs['netlist']['path']!=str((out/'mapped.v').resolve()) or sha(snapshots[event['id']])!=job['baseline']['sha256']:
                raise RuntimeError('Actual baseline STA input differs from frozen mapped input')
            baseline+=1
        elif script.is_relative_to((out/'eval').resolve()) and 'baseline' in str(script.relative_to(out)):
            refresh+=1
        else:raise RuntimeError('Unclassified extra STA process attempt')
    if baseline<1:raise RuntimeError('Missing baseline STA process attempt')
    counts.update(accepted_commits=len(state['accepted_patches']),baseline_sta_launch_attempts=baseline,
                  refresh_sta_launch_attempts=refresh,total_sta_process_attempts=len(launches))
    return result,counts


def _verify_sec(job,result):
    out=Path(job['output_dir']);secdir=out/'final_sec';sec=read_json(secdir/'result.json')
    initial=(out/'mapped.v').read_text(encoding='utf-8');final=result['state']['current_netlist_text']
    if sec.get('status')!='pass' or sec.get('returncode')!=0:raise RuntimeError('Independent final SEC not pass')
    if (secdir/'initial_raw.v').read_text(encoding='utf-8')!=initial or (secdir/'final_raw.v').read_text(encoding='utf-8')!=final:
        raise RuntimeError('Independent SEC does not bind actual final state/raw initial')
    gold,gate,helpers=common.sec_designs(initial,final,job['circuit'])
    for name,text in [('gold.v',gold),('gate.v',gate),('helpers.v',helpers)]:
        if (secdir/name).read_text(encoding='utf-8')!=text:raise RuntimeError('SEC split/helper binding mismatch')
    for key,name in [('initial_sha256','initial_raw.v'),('final_sha256','final_raw.v'),('shared_helpers_sha256','helpers.v')]:
        if sec.get(key)!=sha(secdir/name):raise RuntimeError('SEC receipt input hash mismatch')
    if (secdir/'sec.ys').read_text(encoding='utf-8')!=_sec_script(secdir,job['circuit']):raise RuntimeError('SEC script/proof method changed')
    if sha(secdir/'cells.v')!=sha(out/'model_preflight.v'):raise RuntimeError('Actual model differs from preflight')
    log=(secdir/'sec.log').read_text(encoding='utf-8')
    counts=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)
    if not counts or any(int(p)<=0 or int(u)!=0 for p,u in counts) or 'Equivalence successfully proven!' not in log or 'No SAT model available' in log:
        raise RuntimeError('SEC empty/unproven/unsupported despite reported success')
    return sec


def _run_process(job,manifest):
    out=Path(job['output_dir'])
    command=[sys.executable,'-u','-X','utf8',str(ADAPTER),'guarded-run','--manifest',str(Path(manifest['plan']['output_dir'])/'manifest.json'),'--circuit',job['circuit']]
    env={**os.environ,'PYTHONUTF8':'1'}
    with (out/'runner.log').open('x',encoding='utf-8') as log:
        return subprocess.run([str(common.BASH),str(ROOT/'code/scripts/run_with_timeout.sh'),str(manifest['plan']['runner_watchdog_s']),*command],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=manifest['plan']['outer_watchdog_s'],env=env)


def execute_job(manifest,circuit):
    validate_manifest(manifest);job=_job(manifest,circuit);out=Path(job['output_dir'])
    if out.exists():raise RuntimeError('Job output exists; refuse overwrite or automatic resume')
    initial_path=ROOT/job['baseline']['path'];initial=initial_path.read_text(encoding='utf-8')
    _domain(initial,initial)
    out.mkdir(parents=True,exist_ok=False)
    save_new(out/'preregistered.json',{'manifest_fingerprint':fingerprint(manifest),'job':job})
    try:
        with (out/'mapped.v').open('xb') as handle:handle.write(initial_path.read_bytes())
        if sha(out/'mapped.v')!=job['baseline']['sha256']:raise RuntimeError('Frozen mapped staging changed')
        validate_manifest(manifest)
        process=_run_process(job,manifest)
        if process.returncode!=0:raise RuntimeError('Outerloop process failed: '+str(process.returncode))
        validate_manifest(manifest)
        if sha(out/'mapped.v')!=job['baseline']['sha256']:raise RuntimeError('Runner changed staged mapped input')
        result,counts=_run_outputs(job,manifest)
        certificate=_domain(initial,result['state']['current_netlist_text'])
        save_new(out/'x_identity_certificate.json',certificate)
        write_liberty_cell_models(LIB.read_text(encoding='utf-8'),out/'model_preflight.v',used_cells=_used_types(initial,result['state']['current_netlist_text']))
        sec=final_sec(initial,result['state']['current_netlist_text'],circuit,out/'final_sec')
        if sec.get('status')!='pass' or sec.get('returncode')!=0:raise RuntimeError('Independent final SEC failed or unsupported')
        _verify_sec(job,result);validate_manifest(manifest)
        done={'status':'complete','circuit':circuit,'family':manifest['plan']['family'],'manifest_fingerprint':fingerprint(manifest),
            'accounting':counts,'initial_byte_sha256':job['baseline']['sha256'],'actual_final_text_sha256':result['state']['current_netlist_hash'],
            'sec_status':sec['status'],'sec_returncode':sec['returncode'],'evidence_receipt':common.evidence_receipt(out),'artifacts':_artifacts(out)}
        save_new(out/'completion.json',done)
        verify_job(manifest,circuit)
        return done
    except Exception as error:
        save_new(out/'failure.json',{'status':'failed','error':str(error),'manifest_fingerprint':fingerprint(manifest),'artifacts':_artifacts(out)})
        raise


def verify_job(manifest,circuit):
    validate_manifest(manifest);job=_job(manifest,circuit);out=Path(job['output_dir'])
    if (out/'failure.json').exists():raise RuntimeError('Job has a failure receipt; completion cannot be accepted')
    done=read_json(out/'completion.json')
    if done.get('status')!='complete' or done.get('manifest_fingerprint')!=fingerprint(manifest):raise RuntimeError('Completion identity changed')
    if sha(out/'mapped.v')!=job['baseline']['sha256']:raise RuntimeError('Frozen mapped changed after completion')
    result,counts=_run_outputs(job,manifest);_verify_sec(job,result)
    certificate=_domain((out/'mapped.v').read_text(encoding='utf-8'),result['state']['current_netlist_text'])
    if read_json(out/'x_identity_certificate.json')!=certificate:raise RuntimeError('X certificate not bound to current objects')
    if done.get('accounting')!=counts or done.get('actual_final_text_sha256')!=result['state']['current_netlist_hash'] or done.get('initial_byte_sha256')!=job['baseline']['sha256']:
        raise RuntimeError('Completion state/accounting changed')
    if done.get('evidence_receipt')!=common.evidence_receipt(out) or done.get('artifacts')!=_artifacts(out):raise RuntimeError('Completion artifact hashes changed')
    return done


def guarded_runner(manifest,circuit):
    validate_manifest(manifest);job=_job(manifest,circuit);out=Path(job['output_dir'])
    if read_json(out/'preregistered.json')!={'manifest_fingerprint':fingerprint(manifest),'job':job}:
        raise RuntimeError('Missing or changed job preregistration')
    if not (out/'mapped.v').is_file() or sha(out/'mapped.v')!=job['baseline']['sha256']:raise RuntimeError('Missing/changed staged mapped input')
    original_mapping=runner.run_yosys_mapping;original_run=subprocess.run;original_argv=sys.argv
    lock=threading.Lock();seq=0;invalid=[];trace=out/'tool_launches.jsonl'
    with trace.open('x',encoding='utf-8') as trace_handle:
        def emit(event):
            with lock:trace_handle.write(json.dumps(event,ensure_ascii=False)+'\n');trace_handle.flush()
        def forbid_mapping(*args,**kwargs):raise RuntimeError('Automatic mapping/remap is forbidden for B3 frozen mapped input')
        def observed_run(command,*args,**kwargs):
            nonlocal seq
            argv=list(command) if isinstance(command,(tuple,list)) else []
            is_sta=any(re.search(r'(?:^|[/\\])sta(?:\.exe)?$',str(token)) for token in argv)
            if not is_sta:return original_run(command,*args,**kwargs)
            with lock:seq+=1;identity=seq
            attempt=out/'sta_attempts'/f'{identity:06d}';owned=False
            try:
                attempt.mkdir(parents=True,exist_ok=False);owned=True
                if argv[:7]!=['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit'] or len(argv)!=8:
                    raise RuntimeError('Unsupported STA invocation grammar')
                script=str(_sta_local_path(str(argv[-1])))
                inputs=_begin_sta_attempt(attempt,script,out,circuit,manifest,argv)
            except Exception as error:
                # Never write into an existing attempt directory on collision.
                if owned:
                    save_new(attempt/'rejected.json',{'status':'rejected_before_launch','error_type':type(error).__name__,'error':str(error)})
                emit({'event':'rejected_before_launch','id':identity,'attempt_dir':str(attempt),'error':str(error)})
                raise
            emit({'event':'launch','id':identity,'command':argv,'script':script,'script_sha256':inputs['script']['sha256'],
                  'attempt_dir':str(attempt),'inputs_sha256':sha(attempt/'inputs.json')})
            try:
                answer=original_run(command,*args,**kwargs)
            except BaseException as error:
                try:
                    result=_finish_sta_attempt(attempt,inputs,error=error)
                    emit({'event':'return','id':identity,'returncode':result['returncode'],'error':str(error),
                          'attempt_dir':str(attempt),'result_sha256':sha(attempt/'result.json')})
                    if result['input_drift']:invalid.append('STA input drift')
                except Exception as observation_error:
                    invalid.append('STA exception observation failed: '+str(observation_error))
                    emit({'event':'observation_error','id':identity,'error':str(observation_error)})
                raise
            try:
                result=_finish_sta_attempt(attempt,inputs,answer=answer)
                emit({'event':'return','id':identity,'returncode':answer.returncode,'attempt_dir':str(attempt),'result_sha256':sha(attempt/'result.json')})
                if result['input_drift']:invalid.append('STA input drift')
            except Exception as error:
                invalid.append('STA return observation failed: '+str(error))
                emit({'event':'observation_error','id':identity,'error':str(error)})
            return answer
        try:
            runner.run_yosys_mapping=forbid_mapping;subprocess.run=observed_run
            sys.argv=job['command'][4:]
            answer=runner.main()
            if invalid:raise RuntimeError('; '.join(invalid))
            return answer
        finally:
            runner.run_yosys_mapping=original_mapping;subprocess.run=original_run;sys.argv=original_argv


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    preview=sub.add_parser('preview');preview.add_argument('--output-dir',type=Path,required=True);preview.add_argument('--save',type=Path,required=True)
    registration=sub.add_parser('register');registration.add_argument('--review-plan',type=Path,required=True)
    for name in ['run','verify','guarded-run']:
        p=sub.add_parser(name);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--circuit',choices=tuple(INPUTS),required=True)
    args=parser.parse_args(argv)
    if args.mode=='preview':
        plan=build_plan(args.output_dir);save_new(args.save,plan);print('Review preview only; no formal registration or EDA');return 0
    if args.mode=='register':
        plan=read_json(args.review_plan);register_plan(plan,plan['output_dir']);return 0
    manifest=read_json(args.manifest)
    if args.mode=='guarded-run':return guarded_runner(manifest,args.circuit)
    done=execute_job(manifest,args.circuit) if args.mode=='run' else verify_job(manifest,args.circuit)
    print(json.dumps({'status':done['status'],'circuit':args.circuit,'accounting':done['accounting']}));return 0


if __name__=='__main__':raise SystemExit(main())
