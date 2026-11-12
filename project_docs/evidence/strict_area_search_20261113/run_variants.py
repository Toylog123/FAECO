"""Independent fixed two-arm family-target probe; default preflight only."""
import argparse
import copy
import json
import subprocess
import sys
import time
from decimal import Decimal

import analyze_repair as audit
import local_data as data
import run_search
import selection

HERE = data.HERE
BASE_PLAN_SHA256 = '2efbac2bfaf603fd2814e1e1ba00e0c6254dc7e5aeaf1c314f3fe169b5fcf45e'
TARGETS = {'VARIANT_054_2':['_054_'], 'VARIANT_096_054_2':['_054_','_096_']}


def variant_recipe(original):
    result = copy.deepcopy(original)
    hits = [r for r in result['applied'] if r['instance'] == '_054_']
    audit.require(len(hits) == 1 and hits[0]['new_cell'] == 'sky130_fd_sc_hd__or3b_4' and
                  hits[0]['old_cell'] == 'sky130_fd_sc_hd__or3b_1', 'Unexpected _054_ historical recipe')
    hits[0]['old_cell'] = 'sky130_fd_sc_hd__or3b_2'
    return result


def completed_search(base_plan, dataset):
    summary = data.read('SEARCH_SUMMARY.json')
    audit.require(summary['status'] == 'all9_finished' and summary['plan_sha256'] == BASE_PLAN_SHA256,
                  'All nine valid original pairs must finish before variant execution')
    audit.require(summary['driver_sha256'] == audit.sha(HERE/'physical_probe.py') and
                  summary['runner_sha256'] == audit.sha(HERE/'run_search.py'), 'Original search execution identity drift')
    audit.require(summary['actual_new_cost'] == {'charged_verifications':9,'completed_routes':9,'completed_sta':18}, 'Incomplete original measurement costs')
    audit.require(audit.sha(HERE/'SEARCH_RECEIPT.json') == audit.sha(HERE/'SEARCH_SUMMARY.json'), 'Original summary/receipt mismatch')
    audit.require([j['arm'] for j in summary['jobs']] == base_plan['measurement_order'] and
                  all(j['status'] == 'complete' and j['returncode'] == 0 for j in summary['jobs']), 'Original jobs incomplete')
    areas, control, recovered, recipe, seed, _ = dataset
    batch = {j['arm']:j for j in summary['jobs']}
    rows = []; points = {}
    for arm in base_plan['measurement_order']:
        row = audit.audit_arm(arm,base_plan['singletons'][arm],control,recovered,recipe,areas,selection.TOL,batch)
        audit.require(row['status'].startswith('validated_'), 'Original raw audit failed: '+arm)
        rows.append(row); points[arm] = data.point(row,'runs/'+arm)
    audit.require(rows == summary['rows'] and points == summary['points'], 'Original raw results disagree with summary')
    trace = selection.replay(base_plan['orders'],points,control,seed)
    audit.require(trace == summary['traces'] and trace['area_first'][-1]['selected'] == summary['selected'], 'Original policy replay mismatch')
    return audit.sha(HERE/'SEARCH_SUMMARY.json')


def preflight(execute=False):
    audit.require(audit.sha(HERE/'PLAN.json') == BASE_PLAN_SHA256, 'Original frozen plan drift')
    base_plan, dataset = run_search.preflight()
    plan = data.read('VARIANT_PLAN.json')
    for name, digest in plan['source_sha256'].items():
        data.check_hash(name,digest)
    audit.require(plan['base_plan_sha256'] == BASE_PLAN_SHA256 and plan['targets'] == TARGETS, 'Variant plan target drift')
    audit.require(plan['measurement_order'] == list(TARGETS) and plan['tolerance_ns'] == selection.TOL and
                  plan['timeouts_s'] == {'route':900,'sta':300,'child':1530,'batch':1800}, 'Variant protocol drift')
    original = data.read('inputs/recipe.json')
    recipe = data.read('VARIANT_RECIPE.json')
    audit.require(recipe == variant_recipe(original), 'Variant recipe changed more than _054_ target')
    actions = {r['instance'] for r in original['applied']}
    expected = {arm:sorted(actions-set(target)) for arm,target in TARGETS.items()}
    audit.require(plan['singletons'] == expected, 'Variant restored sets mismatch')
    areas,control,_,_,_,_ = dataset
    for arm,targets in TARGETS.items():
        design = copy.deepcopy(control['structure'])
        for change in recipe['applied']:
            if change['instance'] in targets:
                design['instances'][change['instance']]['cell'] = change['old_cell']
        total,_ = audit.area(design,areas)
        saving = float(Decimal(str(control['area']))-Decimal(str(total)))
        audit.require(plan['exact_area'][arm] == {'area':total,'area_saved':saving}, 'Variant complete area mismatch')
    summary_sha = completed_search(base_plan,dataset) if execute or (HERE/'SEARCH_SUMMARY.json').exists() else None
    return plan,dataset,summary_sha


def execute(plan,dataset,summary_sha):
    receipt = HERE/'VARIANT_RECEIPT.json'; summary = HERE/'VARIANT_SUMMARY.json'
    audit.require(summary_sha is not None, 'Original search completion not audited')
    audit.require(not receipt.exists() and not summary.exists(), 'Existing variant receipts; no overwrite/restart')
    for arm in plan['measurement_order']:
        audit.require(not (HERE/'runs'/arm).exists() and not (HERE/(arm+'.runner.log')).exists(), 'Existing variant output')
    areas,control,recovered,_,seed,_ = dataset
    recipe = data.read('VARIANT_RECIPE.json')['applied']
    state = {'status':'running','plan_sha256':audit.sha(HERE/'VARIANT_PLAN.json'),
             'recipe_sha256':audit.sha(HERE/'VARIANT_RECIPE.json'),'driver_sha256':audit.sha(HERE/'physical_probe_variant.py'),
             'runner_sha256':audit.sha(HERE/'run_variants.py'),'original_search_summary_sha256':summary_sha,
             'jobs':[],'rows':[],'points':{},'actual_new_cost':{'charged_verifications':0,'completed_routes':0,'completed_sta':0},
             'budget_scope':'Separate two-route/four-STA probe; excluded from original nine-pair ranking pool.'}
    run_search.write(receipt,state)
    began = time.monotonic()
    for arm in plan['measurement_order']:
        remaining = 1800-(time.monotonic()-began)
        audit.require(remaining>0,'Variant batch timeout; stop for attribution')
        audit.require(audit.sha(HERE/'SEARCH_SUMMARY.json') == summary_sha,'Original search summary drift')
        job = {'arm':arm,'restored':plan['singletons'][arm],'status':'reserved','returncode':None}
        state['jobs'].append(job); state['actual_new_cost']['charged_verifications'] += 1
        run_search.write(receipt,state)
        start = time.monotonic()
        try:
            with (HERE/(arm+'.runner.log')).open('xb') as log:
                result = subprocess.run([sys.executable,str(HERE/'physical_probe_variant.py'),arm],cwd=audit.ROOT,
                                        stdout=log,stderr=subprocess.STDOUT,timeout=min(1530,remaining))
            job.update(status='complete',returncode=result.returncode)
        except subprocess.TimeoutExpired:
            job.update(status='timeout',returncode=124)
        except OSError as exc:
            job.update(status='launch_failed',returncode=125,reason=str(exc))
        job['elapsed_s'] = time.monotonic()-start
        row = audit.audit_arm(arm,job['restored'],control,recovered,recipe,areas,selection.TOL,{arm:job})
        state['rows'].append(row)
        path = HERE/'runs'/arm/'manifest.json'
        if path.exists():
            manifest = json.loads(path.read_text())
            state['actual_new_cost']['completed_routes'] += int(manifest.get('flow',{}).get('returncode')==0)
            state['actual_new_cost']['completed_sta'] += sum(manifest.get(k,{}).get('returncode')==0 for k in ('ideal','propagated'))
        if not row['status'].startswith('validated_'):
            state.update(status='halted_for_attribution',elapsed_s=time.monotonic()-began)
            run_search.write(receipt,state)
            raise RuntimeError('Variant failure consumes budget; no retries: '+arm+': '+row.get('reason',''))
        point = data.point(row,'runs/'+arm)
        audit.require(selection.judge_actual(point,control)['feasible'] == row['primary_numeric_pass'], 'Strict gate disagreement')
        state['points'][arm] = point
        run_search.write(receipt,state)
        print(json.dumps({'arm':arm,'status':row['status']}),flush=True)
    trace = selection.replay({'fixed_two':plan['measurement_order']},state['points'],control,seed)['fixed_two']
    selected = trace[-1]['selected']
    state.update(status='all2_finished',elapsed_s=time.monotonic()-began,trace=trace,selected=selected,
                 next_sec='reuse_seed_proof' if selected==seed else 'selected_exact_endpoint_pending_SEC')
    audit.require(state['actual_new_cost'] == {'charged_verifications':2,'completed_routes':2,'completed_sta':4}, 'Variant cost mismatch')
    run_search.write(receipt,state);run_search.write(summary,state)
    print(json.dumps({'status':state['status'],'selected':selected['candidate_id'],'next_sec':state['next_sec']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',help='Requires all nine original measurements valid; execute both variants once.')
    args = parser.parse_args()
    plan,dataset,summary_sha = preflight(args.execute)
    print(json.dumps({'preflight':'pass','original_search':'all9_valid' if summary_sha else 'pending_allowed_for_drycheck',
                      'arms':plan['measurement_order'],'execute':args.execute}),flush=True)
    if args.execute:execute(plan,dataset,summary_sha)
