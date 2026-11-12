"""Frozen bounded beam of compensation subsets; defaults to dry-check, no EDA.

Requires all13 valid failed singletons. --execute performs at most12 serial
physical evaluations. Predictions order proposals only; audit decides feasibility.
"""
import argparse
import copy
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import analyze_repair as audit

HERE = Path(__file__).resolve().parent
NORMS = {'setup_ns': .010, 'tns_ns': .312647, 'hold_ns': .001}
TOL = 1e-6


def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def rank(row, control):
    metrics = row['metrics']
    deficits = [max(0.0, control['metrics'][key]-metrics[key]-TOL)/scale
                for key, scale in NORMS.items()]
    invalid = not row.get('valid', True) or not all(math.isfinite(v) for v in metrics.values())
    return (int(invalid), max(deficits), sum(deficits), -row['area_saved'], tuple(row['restored']))


def main(execute=False):
    plan_path = HERE/'COMBINATION_PLAN.json'
    plan = json.loads(plan_path.read_text())
    singleton_plan = json.loads((HERE/'PLAN.json').read_text())
    summary = json.loads((HERE/'SUMMARY.json').read_text())
    audit.require(summary['all13_finished'] and len(summary['rows']) == 13, 'All13 final singleton summary required')
    audit.require(summary['analyzer_sha256'] == audit.sha(HERE/'analyze_repair.py'), 'Analyzer drift')
    audit.require(summary['plan_sha256'] == audit.sha(HERE/'PLAN.json'), 'Singleton plan drift')
    audit.require(summary['batch_receipt_sha256'] == audit.sha(HERE/'BATCH_RECEIPT.json'), 'Singleton batch drift')
    audit.require(plan['preregistration_sha256'] == audit.sha(HERE/'PREREGISTRATION.md'), 'Preregistration drift')
    driver = HERE/'physical_probe_combination.py'
    original = (HERE/'physical_probe.py').read_text()
    audit.require(plan['source_driver_sha256'] == audit.sha(HERE/'physical_probe.py'), 'Original driver drift')
    audit.require(driver.read_text() == original.replace("HERE / 'PLAN.json'", "HERE / 'COMBINATION_PLAN.json'"), 'Combination driver differs beyond plan filename')
    audit.require(plan['normalizers_ns'] == NORMS and plan['tolerance_ns'] == TOL and plan['max_new_runs'] == 12 and plan['beam_width'] == 3 and plan['cardinalities'] == [2,3,4,5], 'Frozen search rule mismatch')
    for name, info in json.loads((HERE/'inputs/MANIFEST.json').read_text()).items():
        audit.require(audit.sha(HERE/'inputs'/name) == info['sha256'], 'Frozen input drift')
    areas = audit.load_liberty_areas(audit.LIB)
    control, recovery = audit.baseline('CONTROL', areas), audit.baseline('RECOVERY_V2', areas)
    recipe = json.loads((HERE/'inputs/recipe.json').read_text())['applied']
    names = sorted(x['instance'] for x in recipe)
    audit.require(len(names) == 13 and len(set(names)) == 13, 'Expected13 unique actions')
    all_sets = {tuple(v): arm for arm, v in plan['combinations'].items()}
    expected = {s for size in range(2,6) for s in itertools.combinations(names,size)}
    audit.require(len(all_sets) == 2366 and set(all_sets) == expected, 'Combination coverage mismatch')
    batch = {j['arm']: j for j in json.loads((HERE/'BATCH_RECEIPT.json').read_text())['jobs']}
    singles = [audit.audit_arm(arm, restored, control, recovery, recipe, areas, TOL, batch)
               for arm, restored in singleton_plan['singletons'].items()]
    audit.require(len(singles) == 13 and all(r['status'] == 'validated_primary_fail' for r in singles),
                  'All13 valid strictly failing singletons required; invalid/success cases block expansion')
    singleton_by_action = {r['restored'][0]: r for r in singles}
    audit.require(set(singleton_by_action) == set(names), 'Singleton coverage mismatch')

    def actual(row):
        return dict(restored=sorted(row['restored']), metrics=row['metrics']['propagated'],
                    area_saved=row['area_saved'], valid=row['status'].startswith('validated_'))

    def proposal(subset):
        metrics = {key: recovery['metrics'][key] + sum(
            singleton_by_action[x]['metrics']['propagated'][key]-recovery['metrics'][key] for x in subset)
                   for key in NORMS}
        design = copy.deepcopy(control['structure'])
        for change in recipe:
            if change['instance'] not in subset:
                design['instances'][change['instance']]['cell'] = change['old_cell']
        total, _ = audit.area(design, areas)
        return dict(arm=all_sets[subset], restored=list(subset), metrics=metrics,
                    area_saved=control['area']-total, valid=True,
                    predicted_only=True, physical_validity='unknown until actual audit')

    beam = [tuple(r['restored']) for r in sorted(singles, key=lambda r: rank(actual(r), control))[:3]]
    state = dict(status='prepared', runner_sha256=audit.sha(Path(__file__)),
                 driver_sha256=audit.sha(driver), plan_sha256=audit.sha(plan_path),
                 analyzer_sha256=audit.sha(HERE/'analyze_repair.py'), singleton_summary_sha256=audit.sha(HERE/'SUMMARY.json'),
                 initial_beam=[list(s) for s in beam], jobs=[], layers=[], max_new_runs=12)
    first = sorted({tuple(sorted(set(b)|{x})) for b in beam for x in names if x not in b})
    preview = sorted((proposal(s) for s in first), key=lambda r: rank(r,control))[:3]
    print(json.dumps({'mode':'execute' if execute else 'dry-check', 'initial_beam':state['initial_beam'], 'first_proposals':preview}), flush=True)
    if not execute:
        return 0
    audit.require(not (HERE/'COMBINATION_RECEIPT.json').exists() and not (HERE/'COMBINATION_SUMMARY.json').exists(), 'Existing combination results require manual attribution; no implicit resume')
    state['status']='running'
    save('COMBINATION_RECEIPT.json',state)
    measured = []
    seen = set()

    def finish(reason):
        state['status']=reason
        save('COMBINATION_RECEIPT.json',state)
        valid = singles+[r for r in measured if r['status'].startswith('validated_')]
        curves = {}
        for budget in (0,.002,.005,.010):
            feasible=[r for r in valid if r['diagnostic_budget_pass'][str(budget)]]
            curves[str(budget)]=max(feasible,key=lambda r:r['area_saved']) if feasible else None
        save('COMBINATION_SUMMARY.json',dict(scope='s382 bounded evaluated search; no global optimality or mechanism superiority claim; SEC pending',
             status=reason, primary_goal='zero-budget WNS/TNS/hold nonworsening plus physical gates and positive savings',
             physical_runs_attempted=len(state['jobs']), layers=state['layers'], rows=measured,
             same_evaluated_set_budget_best=curves, primary_candidates_pending_SEC=[r['arm'] for r in measured if r.get('primary_numeric_pass')],
             source_sha256={k:state[k] for k in ('runner_sha256','driver_sha256','plan_sha256','analyzer_sha256','singleton_summary_sha256')},
             control_fallback='all-restored CONTROL has zero saving; not a useful recovery solution',
             limitations=['Predictions only order proposals; no predicted result is accepted.', 'Configured DRV and supported-rule DRC only; no complete constraint coverage claim.', 'Failure consumes budget and halts for attribution; no automatic retries.']))

    for size in (2,3,4,5):
        proposals = {tuple(sorted(set(b)|{x})) for b in beam for x in names if x not in b}
        proposals = {s for s in proposals if len(s)==size and s not in seen}
        chosen = sorted((proposal(s) for s in proposals), key=lambda r: rank(r,control))[:3]
        layer = dict(cardinality=size, parent_beam=[list(s) for s in beam], proposal_count=len(proposals),
                     chosen=[dict(p,ranking=list(rank(p,control))) for p in chosen], actual=[])
        state['layers'].append(layer)
        save('COMBINATION_RECEIPT.json',state)
        current=[]
        for p in chosen:
            audit.require(len(state['jobs'])<12, 'Physical run budget exceeded')
            subset=tuple(p['restored']); arm=p['arm']; seen.add(subset)
            if (HERE/'runs'/arm).exists() or (HERE/(arm+'.monitor.log')).exists():
                finish('halted_existing_artifact_requires_attribution')
                return 1
            job=dict(arm=arm,restored=p['restored'],status='running')
            state['jobs'].append(job);save('COMBINATION_RECEIPT.json',state)
            start=time.monotonic()
            print('START',arm,flush=True)
            with (HERE/(arm+'.monitor.log')).open('xb') as log:
                try:
                    proc=subprocess.run([sys.executable,str(driver),arm],stdout=log,stderr=subprocess.STDOUT,timeout=1530)
                    rc=proc.returncode
                except subprocess.TimeoutExpired:
                    rc=124
                except OSError as error:
                    rc=127
                    job['launch_error']=str(error)
            job.update(returncode=rc,elapsed_s=time.monotonic()-start,status='complete')
            row=audit.audit_arm(arm,p['restored'],control,recovery,recipe,areas,TOL,{arm:job})
            measured.append(row);current.append(row);layer['actual'].append(row)
            save('COMBINATION_RECEIPT.json',state)
            print('END',arm,'rc',rc,'audit',row['status'],flush=True)
            if rc or not row['status'].startswith('validated_'):
                finish('halted_failure_requires_attribution')
                return 1
        if any(r.get('primary_numeric_pass') for r in current):
            finish('strict_numeric_candidate_found_pending_SEC')
            return 0
        beam=[tuple(r['restored']) for r in sorted(current,key=lambda r:rank(actual(r),control))]
    finish('budget_exhausted_no_strict_candidate')
    return 0


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',help='Run physical evaluations; omit for read-only dry-check')
    args=parser.parse_args()
    raise SystemExit(main(args.execute))
