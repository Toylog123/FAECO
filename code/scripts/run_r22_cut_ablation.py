"""Pinned C-prime matrix: cold runs, common mapped inputs, bounded jobs.

Prepare with --dry-run. Execute a two-circuit pilot, inspect it, then execute
remaining circuits with the same manifest. Completed runs are only reused
after checking their input/config/source fingerprints and final SEC receipt.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'code/scripts'))
sys.path.insert(0, str(ROOT/'code/src'))
from run_sequential_timing_check import run_yosys_mapping, LIB, _to_wsl, _yosys_env, _find_oss_cad_root
from rseco.real_wns import write_liberty_cell_models

ARMS = ('W0','W1','U0','U1','C','UR1','UR2','UR3','L')
CIRCUITS = ('s27','s382','s420','s641','s713','s820','s832','s953')
POLICIES = {'W0': ('weighted','configured'), 'W1': ('full','configured'),
            'U0': ('weighted','uniform'), 'U1': ('full','uniform'),
            'C': ('cover','configured')}
RUNNER = ROOT/'code/scripts/run_outerloop_real_wns.py'
BASH = Path('C:/Program Files/Git/bin/bash.exe')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def job_command(arm, circuit, out):
    if arm not in ARMS or circuit not in CIRCUITS:
        raise ValueError('Unregistered matrix member')
    base = 'W1' if arm.startswith('UR') else arm
    source, cost = POLICIES.get(base, ('full','configured'))
    cmd = [sys.executable,'-u','-X','utf8',str(RUNNER),'--circuit',circuit,
           '--output-dir',str(out.parent),'--period','0.5','--max-iterations','20',
           '--max-patches','20','--sta-budget','500','--wall-timeout-s','3600',
           '--candidates-per-iteration','8','--max-instances','8',
           '--workers','1','--joint-k','2','--joint-enumerate-depth','0',
           '--strategies','R,G,B','--enable-buffer','--early-stop',
           '--no-feedback','--no-proxy-ranking','--disable-topology','--skip-mapping',
           '--cut-search-policy','legacy' if arm=='L' else 'weighted_st',
           '--cut-sources',source,'--node-cost-mode',cost]
    for flag in ('boundary-penalty','size-penalty','critical-coverage-reward',
                 'verification-cost-penalty','equivalence-stability-reward'):
        cmd += ['--init-'+flag, '0' if cost=='uniform' else '1']
    if arm.startswith('UR'):
        cmd += ['--random-order','--seed',arm[-1]]
    return cmd


def source_manifest():
    files = sorted((ROOT/'code/src/rseco').glob('*.py')) + [RUNNER,Path(__file__).resolve(),
        ROOT/'code/scripts/run_sequential_timing_check.py',ROOT/'code/scripts/run_with_timeout.sh']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in files}


def tool_versions():
    cad = _find_oss_cad_root()
    if cad is None:
        raise RuntimeError('Pinned native Yosys unavailable')
    queries = {'mapping_yosys':[str(cad/'bin/yosys.exe'),'-V'],
               'sta':['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-version'],
               'sec_yosys':['wsl.exe','-d','Ubuntu','--','/usr/bin/yosys','-V']}
    answer = {}
    for name, cmd in queries.items():
        p = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',
            errors='replace',timeout=30,env=_yosys_env() if name=='mapping_yosys' else None)
        if p.returncode:
            raise RuntimeError(f'{name} unavailable: {p.stderr}')
        answer[name] = {'command':cmd,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
    return answer


def sec_designs(initial, final, circuit):
    """Share only byte-identical helper definitions, prove both distinct tops."""
    import re
    def modules(text):
        pairs = re.findall(r'\b(module\s+([A-Za-z_][A-Za-z0-9_$]*)\b.*?\bendmodule)',text,re.S)
        found = {name:block for block,name in pairs}
        if len(found)!=len(pairs) or circuit not in found:
            raise ValueError('Missing/duplicate SEC top or module')
        return found
    left, right = modules(initial), modules(final)
    names = (set(left)|set(right))-{circuit}
    if any(left.get(name)!=right.get(name) for name in names):
        raise ValueError('SEC helper definitions differ; shared semantics cannot be assumed')
    return left[circuit],right[circuit],'\n'.join(left[n] for n in sorted(names))


def final_sec(initial, final, circuit, out):
    """Independent full-netlist sequential induction, not the local RGB gate."""
    import re
    out.mkdir(parents=True,exist_ok=True)
    (out/'initial_raw.v').write_text(initial,encoding='utf-8')
    (out/'final_raw.v').write_text(final,encoding='utf-8')
    gold, gate, helpers = sec_designs(initial,final,circuit)
    (out/'gold.v').write_text(gold,encoding='utf-8')
    (out/'gate.v').write_text(gate,encoding='utf-8')
    (out/'helpers.v').write_text(helpers,encoding='utf-8')
    used = set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+\w+\s*\(',initial+'\n'+final))
    write_liberty_cell_models(LIB.read_text(encoding='utf-8'),out/'cells.v',used_cells=used)
    script = '\n'.join([
        f'read_verilog "{_to_wsl(out/"cells.v")}"',
        f'read_verilog "{_to_wsl(out/"helpers.v")}"',
        f'read_verilog "{_to_wsl(out/"gold.v")}"',f'rename {circuit} gold',
        f'read_verilog "{_to_wsl(out/"gate.v")}"',f'rename {circuit} gate',
        'proc','memory','equiv_make gold gate equiv','hierarchy -top equiv',
        'flatten','opt_clean','equiv_simple','equiv_induct -seq 10',
        'equiv_status -assert',''])
    (out/'sec.ys').write_text(script,encoding='utf-8')
    started = time.monotonic()
    cmd = ['wsl.exe','-d','Ubuntu','--','/usr/bin/yosys',_to_wsl(out/'sec.ys')]
    try:
        p = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        log = p.stdout+p.stderr
        status = 'pass' if p.returncode==0 and 'Equivalence successfully proven!' in log else 'fail'
        rc = p.returncode
    except subprocess.TimeoutExpired:
        log, status, rc = 'SEC timed out after 180s', 'timeout', None
    (out/'sec.log').write_text(log,encoding='utf-8')
    result = {'status':status,'returncode':rc,'command':cmd,'runtime_s':time.monotonic()-started,
        'initial_sha256':sha(out/'initial_raw.v'),'final_sha256':sha(out/'final_raw.v'),
        'shared_helpers_sha256':sha(out/'helpers.v'),
        'method':'Yosys equiv_simple + equiv_induct seq10, full-netlist'}
    save(out/'result.json',result)
    return result


def evidence_receipt(out):
    names = ('outerloop_result.json','eval_trials.json','run_config.json',
             'mapped.v','final_sec/result.json','final_sec/sec.log','final_sec/sec.ys',
             'final_sec/initial_raw.v','final_sec/final_raw.v',
             'final_sec/helpers.v','final_sec/cells.v')
    if any(not (out/name).is_file() for name in names):
        raise RuntimeError('Incomplete experiment/SEC receipt')
    return {name:sha(out/name) for name in names}


def validate_completion(out, done, initial):
    if done.get('evidence_receipt') != evidence_receipt(out):
        raise RuntimeError('Experiment/SEC receipt hash mismatch')
    sec=json.loads((out/'final_sec/result.json').read_text(encoding='utf-8'))
    result=json.loads((out/'outerloop_result.json').read_text(encoding='utf-8'))
    if (sec.get('status')!='pass' or done.get('sec_status')!='pass'
            or sec.get('initial_sha256')!=sha(out/'final_sec/initial_raw.v')
            or sec.get('final_sha256')!=sha(out/'final_sec/final_raw.v')
            or (out/'final_sec/initial_raw.v').read_text(encoding='utf-8')!=initial
            or (out/'final_sec/final_raw.v').read_text(encoding='utf-8')!=result['state']['current_netlist_text']):
        raise RuntimeError('Independent SEC receipt does not bind the actual netlists')
    return True


def execute_circuit(circuit, output, manifest, stop=None):
    def check_stop():
        if stop is not None and stop.is_set():
            raise RuntimeError('Batch stopped after another circuit failed; no new job launched')
    check_stop()
    baseline = output/'inputs'/circuit
    baseline.mkdir(parents=True,exist_ok=True)
    source = ROOT/'data/raw/benchmarks/raw/iscas89'/f'{circuit}.v'
    if sha(source)!=manifest['inputs'][circuit]:
        raise RuntimeError('Input changed after registration')
    input_receipt = baseline/'input.json'
    if input_receipt.exists():
        receipt=json.loads(input_receipt.read_text(encoding='utf-8'))
        if receipt['source_manifest']!=manifest['source_manifest'] or receipt['mapped_sha256']!=sha(baseline/'mapped.v'):
            raise RuntimeError('Mapped input/source receipt mismatch')
    else:
        if (baseline/'mapped.v').exists():
            raise RuntimeError('Unregistered mapped input; do not overwrite')
        errors=run_yosys_mapping(source,baseline)
        if errors or not (baseline/'mapped.v').exists():
            raise RuntimeError(f'Mapping failed: {errors}')
        save(input_receipt,{'source_manifest':manifest['source_manifest'],
            'source_sha256':sha(source),'mapped_sha256':sha(baseline/'mapped.v')})
    expected_mapped_sha=sha(baseline/'mapped.v')
    completed=[]
    for arm in ARMS:
        check_stop()
        if (sha(baseline/'mapped.v')!=expected_mapped_sha
                or sha(LIB)!=manifest['lib_sha256']):
            raise RuntimeError('Shared mapped input/library changed during experiment')
        if source_manifest()!=manifest['source_manifest']:
            raise RuntimeError('Executable source changed during experiment')
        out=output/arm/circuit
        out.mkdir(parents=True,exist_ok=True)
        cmd=job_command(arm,circuit,out)
        receipt={'command':cmd,'source_manifest':manifest['source_manifest'],
                 'mapped_sha256':sha(baseline/'mapped.v'),'lib_sha256':manifest['lib_sha256']}
        pre=out/'preregistered.json'
        if pre.exists():
            if json.loads(pre.read_text(encoding='utf-8'))!=receipt:
                raise RuntimeError('Existing run has different registered configuration')
            if (out/'completion.json').exists():
                done=json.loads((out/'completion.json').read_text(encoding='utf-8'))
                if done['returncode']==0 and validate_completion(
                        out,done,(baseline/'mapped.v').read_text(encoding='utf-8')):
                    completed.append(done)
                    continue
            raise RuntimeError(f'Incomplete prior run requires attribution before retry: {out}')
        save(pre,receipt)
        shutil.copyfile(baseline/'mapped.v',out/'mapped.v')
        if sha(out/'mapped.v')!=expected_mapped_sha:
            raise RuntimeError('Copied mapped input does not match frozen baseline')
        started=time.monotonic()
        print(f'LAUNCH {circuit}/{arm}',flush=True)
        try:
            with (out/'runner.log').open('w',encoding='utf-8') as log:
                proc=subprocess.run([str(BASH),str(ROOT/'code/scripts/run_with_timeout.sh'),'3900',*cmd],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=3930)
        except subprocess.TimeoutExpired:
            save(out/'completion.json',{'returncode':124,'sec_status':'not_run',
                'runtime_s':time.monotonic()-started,'failure':'outer process timeout 3930s'})
            if stop is not None:
                stop.set()
            raise RuntimeError(f'Outer process timeout {circuit}/{arm}: inspect runner.log')
        if proc.returncode!=0 or not (out/'outerloop_result.json').exists():
            save(out/'completion.json',{'returncode':proc.returncode,'sec_status':'not_run',
                'runtime_s':time.monotonic()-started})
            raise RuntimeError(f'Run failed {circuit}/{arm}: inspect runner.log')
        result=json.loads((out/'outerloop_result.json').read_text(encoding='utf-8'))
        state=result['state']
        if result['n_new_sta_runs']!=state['budget'].get('sta_used',0):
            raise RuntimeError('Launch/reservation mismatch')
        sec=final_sec(state['initial_netlist_text'] if 'initial_netlist_text' in state else
            (baseline/'mapped.v').read_text(encoding='utf-8'),state['current_netlist_text'],circuit,out/'final_sec')
        done={'arm':arm,'circuit':circuit,'returncode':proc.returncode,'sec_status':sec['status'],
            'runtime_s':time.monotonic()-started,'n_new_sta_runs':result['n_new_sta_runs'],
            'baseline_wns':result['baseline_wns'],'final_wns':result['wns'],
            'stop_reason':result['stop_reason'],'result_sha256':sha(out/'outerloop_result.json'),
            'evidence_receipt':evidence_receipt(out)}
        save(out/'completion.json',done)
        completed.append(done)
        print(f'DONE {circuit}/{arm} {json.dumps(done)}',flush=True)
        if sec['status']!='pass':
            raise RuntimeError(f'Final SEC did not pass: {circuit}/{arm}')
    return completed


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--circuits',default='s27,s382')
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args()
    circuits=args.circuits.split(',')
    if not circuits or any(c not in CIRCUITS for c in circuits) or len(set(circuits))!=len(circuits):
        p.error('Use distinct registered circuits')
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=True)
    manifest_path=output/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['source_manifest']!=source_manifest() or manifest['lib_sha256']!=sha(LIB):
            raise RuntimeError('Pinned source/library changed; use a separately registered revision')
    else:
        manifest={'family':'C-prime-r22','arms':list(ARMS),'circuits':list(CIRCUITS),
            'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_manifest':source_manifest(),'lib_sha256':sha(LIB),'tools':tool_versions(),
            'inputs':{c:sha(ROOT/'data/raw/benchmarks/raw/iscas89'/f'{c}.v') for c in CIRCUITS},
            'commands':{a:{c:job_command(a,c,output/a/c) for c in CIRCUITS} for a in ARMS}}
        save(manifest_path,manifest)
    if args.dry_run:
        print(f'Registered {len(ARMS)*len(CIRCUITS)} jobs; no mapping or STA executed',flush=True)
        return 0
    summary_path=output/'batch_summary.json'
    summaries=json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.exists() else []
    stop=threading.Event()
    failures=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(execute_circuit,c,output,manifest,stop):c for c in circuits}
        for f in as_completed(futures):
            try:
                incoming=f.result()
                by_key={(r['arm'],r['circuit']):r for r in summaries+incoming}
                summaries=list(by_key.values())
                save(summary_path,summaries)
            except Exception as exc:
                stop.set()
                failure={'circuit':futures[f],'error':str(exc),'status':'failed_or_stopped'}
                failures.append(failure)
                save(output/'batch_failures.json',failures)
                for pending in futures:
                    if pending is not f:
                        pending.cancel()
                print(f'FAIL {json.dumps(failure)}',flush=True)
    return 1 if failures else 0


if __name__=='__main__':
    raise SystemExit(main())
