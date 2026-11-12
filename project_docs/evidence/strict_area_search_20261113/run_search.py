"""Default read-only preflight; --execute measures all nine once, then replays."""
import argparse
import json
import subprocess
import sys
import time

import analyze_repair as audit
import local_data as data
import selection

HERE = data.HERE
RECEIPT = HERE / 'SEARCH_RECEIPT.json'
SUMMARY = HERE / 'SEARCH_SUMMARY.json'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def preflight():
    plan = data.read('PLAN.json')
    for name, digest in plan['source_sha256'].items():
        data.check_hash(name, digest)
    for name, digest in plan['shared_dependency_sha256'].items():
        path = (audit.ROOT / name).resolve()
        audit.require(path.is_relative_to(audit.ROOT) and not name.startswith(('experiments/', 'project_docs/evidence/')),
                      'External experiment dependency prohibited')
        audit.require(audit.sha(path) == digest, 'Shared dependency SHA drift: ' + name)
    dataset = data.history()
    frozen = data.proposal(dataset)
    for key in frozen:
        audit.require(plan[key] == frozen[key], 'Frozen proposal mismatch: ' + key)
    audit.require(plan['tolerance_ns'] == selection.TOL and plan['norms_ns'] == selection.NORMS,
                  'Acceptance/ranking constants drift')
    audit.require(plan['seed'] == dataset[4] and plan['control'] == {k:dataset[1][k] for k in ('area','metrics','hashes')},
                  'Seed/reference identity drift')
    audit.require(plan['measurement_order'] == sorted(plan['singletons']) and len(plan['singletons']) == 9,
                  'Not the complete lexical nine-pair neighborhood')
    audit.require(plan['timeouts_s'] == {'route':900,'sta':300,'child':1530,'batch':1800}, 'Timeout configuration changed')
    tools = data.read('TOOLCHAIN_PRECHECK.json')
    result = subprocess.run(['wsl.exe','-d','Ubuntu','--','sha256sum',*[t['path'] for t in tools['tools']]],
                            capture_output=True, timeout=45)
    # WSL may emit a UTF-16LE host warning on stderr alongside ASCII Linux stdout.
    audit.require(result.returncode == 0, 'Toolchain SHA query failed: ' + repr(result.stderr))
    actual = {line.split(None,1)[1].strip():line.split()[0] for line in result.stdout.decode('ascii').splitlines()}
    audit.require(actual == {t['path']:t['sha256'] for t in tools['tools']}, 'WSL toolchain drift')
    for name, digest in tools['rcx_and_setRC'].items():
        audit.require(audit.sha(audit.ROOT / name) == digest, 'RC configuration drift')
    return plan, dataset


def execute(plan, dataset):
    audit.require(not RECEIPT.exists() and not SUMMARY.exists(), 'Existing receipt/summary; refuse overwrite/restart')
    for arm in plan['measurement_order']:
        audit.require(not (HERE/'runs'/arm).exists() and not (HERE/(arm+'.runner.log')).exists(), 'Existing arm output: ' + arm)
    areas, control, recovered, recipe, seed, _ = dataset
    state = {'status':'running', 'plan_sha256':audit.sha(HERE/'PLAN.json'),
             'driver_sha256':audit.sha(HERE/'physical_probe.py'), 'runner_sha256':audit.sha(HERE/'run_search.py'),
             'jobs':[], 'rows':[], 'actual_new_cost':{'charged_verifications':0,'completed_routes':0,'completed_sta':0},
             'reused_history_cost':plan['reused_history_cost']}
    write(RECEIPT,state)
    start = time.monotonic()
    points = {}
    for arm in plan['measurement_order']:
        remaining = plan['timeouts_s']['batch'] - (time.monotonic()-start)
        audit.require(remaining > 0, 'Batch timeout before next arm; preserve receipt for attribution')
        job = {'arm':arm, 'restored':plan['singletons'][arm], 'status':'reserved', 'returncode':None}
        state['jobs'].append(job)
        state['actual_new_cost']['charged_verifications'] += 1
        write(RECEIPT,state)
        began = time.monotonic()
        try:
            with (HERE/(arm+'.runner.log')).open('xb') as log:
                p = subprocess.run([sys.executable,str(HERE/'physical_probe.py'),arm], stdout=log, stderr=subprocess.STDOUT,
                                   timeout=min(plan['timeouts_s']['child'],remaining), cwd=audit.ROOT)
            job.update(returncode=p.returncode,status='complete')
        except subprocess.TimeoutExpired:
            job.update(returncode=124,status='timeout')
        except OSError as exc:
            job.update(returncode=125,status='launch_failed',reason=str(exc))
        job['elapsed_s'] = time.monotonic()-began
        row = audit.audit_arm(arm,job['restored'],control,recovered,recipe,areas,selection.TOL,{arm:job})
        state['rows'].append(row)
        manifest_path = HERE/'runs'/arm/'manifest.json'
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            state['actual_new_cost']['completed_routes'] += int(manifest.get('flow',{}).get('returncode') == 0)
            state['actual_new_cost']['completed_sta'] += sum(manifest.get(k,{}).get('returncode') == 0 for k in ('ideal','propagated'))
        if row['status'] == 'invalid_or_missing_evidence':
            state.update(status='halted_for_attribution',elapsed_s=time.monotonic()-start)
            write(RECEIPT,state)
            raise RuntimeError('Invalid/timeout consumes budget; no retry: ' + arm + ': ' + row.get('reason',''))
        point = data.point(row,'runs/'+arm)
        gate = selection.judge_actual(point,control)
        audit.require(gate['feasible'] == row['primary_numeric_pass'], 'Independent strict gate disagreement')
        points[arm] = point
        state['points'] = points
        write(RECEIPT,state)
        print(json.dumps({'finished':len(state['jobs']),'arm':arm,'status':row['status'],'strict_gate':gate}),flush=True)
    traces = selection.replay(plan['orders'],points,control,seed)
    selected = traces['area_first'][-1]['selected']
    state.update(status='all9_finished',elapsed_s=time.monotonic()-start,traces=traces,
                 checkpoints={name:{str(k):trace[k-1] for k in (1,3,6,9)} for name,trace in traces.items()},
                 selected=selected, next_sec=('reuse_seed_proof' if selected == seed else 'selected_exact_endpoint_pending_SEC'),
                 interpretation='k3 primary; k1/k6/k9 secondary. Shared-history conditional comparison; no global optimum claim.')
    audit.require(state['actual_new_cost'] == {'charged_verifications':9,'completed_routes':9,'completed_sta':18}, 'Actual call accounting mismatch')
    write(RECEIPT,state)
    write(SUMMARY,state)
    print(json.dumps({'status':state['status'],'selected':selected['candidate_id'],'next_sec':state['next_sec']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',help='Run all nine serial physical jobs after preflight; never retry or overwrite.')
    args = parser.parse_args()
    plan,dataset = preflight()
    print(json.dumps({'preflight':'pass','orders':plan['orders'],'seed':dataset[4]['candidate_id'],'execute':args.execute}),flush=True)
    if args.execute:
        execute(plan,dataset)


if __name__ == '__main__':
    main()
