"""Three fixed independent joint-compensation probes; dry-check by default."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

import analyze_repair as audit
from rseco.logic_rewrite import parse_liberty_cells

HERE = Path(__file__).resolve().parent
BASE = 'COMBO_054_074_093_098_111'
BASE_RESTORED = ['_054_', '_074_', '_093_', '_098_', '_111_']
EXTRAS = {'JOINT_057': ('_057_', 'sky130_fd_sc_hd__o31a_1', 'sky130_fd_sc_hd__o31a_2'),
          'JOINT_083': ('_083_', 'sky130_fd_sc_hd__o21a_1', 'sky130_fd_sc_hd__o21a_2'),
          'JOINT_REBUFFER1': ('rebuffer1', 'sky130_fd_sc_hd__buf_6', 'sky130_fd_sc_hd__buf_8')}
TOL = 1e-6


def main(execute=False):
    plan_path = HERE/'JOINT_PLAN.json'
    plan = json.loads(plan_path.read_text())
    for name, digest in plan['source_sha256'].items():
        audit.require(audit.sha(HERE/name) == digest, 'Pinned source drift: '+name)
    audit.require(audit.sha(audit.LIB) == plan['liberty_sha256'], 'Liberty drift')
    audit.require(plan['max_new_runs'] == 3 and plan['tolerance_ns'] == TOL and plan['base_arm'] == BASE, 'Protocol drift')
    driver = HERE/'physical_probe_joint.py'
    expected_driver = (HERE/'physical_probe.py').read_text().replace("HERE / 'PLAN.json'", "HERE / 'JOINT_PLAN.json'").replace("HERE / 'inputs/recipe.json'", "HERE / 'JOINT_RECIPE.json'")
    audit.require(driver.read_text() == expected_driver, 'Driver differs beyond plan/recipe paths')
    for name, info in json.loads((HERE/'inputs/MANIFEST.json').read_text()).items():
        audit.require(audit.sha(HERE/'inputs'/name) == info['sha256'], 'Copied input drift')
    original = json.loads((HERE/'inputs/recipe.json').read_text())['applied']
    recipe_document = json.loads((HERE/'JOINT_RECIPE.json').read_text())
    recipe = recipe_document['applied']
    audit.require(len(original) == 13 and recipe[:13] == original and len(recipe) == 16, 'Original13/extra3 recipe drift')
    audit.require(recipe_document['original_recipe_sha256'] == audit.sha(HERE/'inputs/recipe.json'), 'Original recipe pin drift')
    expected_extra = [dict(instance=i, new_cell=before, old_cell=after) for i,before,after in EXTRAS.values()]
    audit.require(recipe[13:] == expected_extra and recipe_document['extra_target_edits'] == expected_extra, 'Extra edits differ from preregistration')
    original_names = {r['instance'] for r in original}
    extra_names = {v[0] for v in EXTRAS.values()}
    audit.require(len(original_names) == 13 and not (original_names & extra_names), 'Extra actions overlap original13')
    expected = {arm: sorted(BASE_RESTORED+[other for other in extra_names if other != edit[0]]) for arm,edit in EXTRAS.items()}
    audit.require(plan['singletons'] == expected, 'Each arm must contain base5 restorations plus unused2 extras')
    areas = audit.load_liberty_areas(audit.LIB)
    cells = parse_liberty_cells(audit.LIB.read_text())
    control,recovery = audit.baseline('CONTROL',areas),audit.baseline('RECOVERY_V2',areas)
    for instance,before,after in EXTRAS.values():
        audit.require(control['structure']['instances'][instance]['cell'] == before, 'Extra CONTROL cell mismatch')
        a,b=cells[before],cells[after]
        audit.require(a.output_functions == b.output_functions and a.input_pins == b.input_pins and not a.sequential_kind and not b.sequential_kind and not a.three_state_functions and not b.three_state_functions, 'Extra cell function/ports/state mismatch')
    combo = json.loads((HERE/'COMBINATION_SUMMARY.json').read_text())
    audit.require(combo['status'] == 'budget_exhausted_no_strict_candidate' and combo['physical_runs_attempted'] == 12, 'StageB is not complete')
    combo_batch = {j['arm']:j for j in json.loads((HERE/'COMBINATION_RECEIPT.json').read_text())['jobs']}
    base = audit.audit_arm(BASE,BASE_RESTORED,control,recovery,original,areas,TOL,combo_batch)
    audit.require(base['status'].startswith('validated_'), 'Selected physical base fails audit')
    predictions = {}
    for arm,restored in expected.items():
        target = copy.deepcopy(control['structure'])
        for change in recipe:
            if change['instance'] not in restored:
                target['instances'][change['instance']]['cell'] = change['old_cell']
        total,_ = audit.area(target,areas)
        predictions[arm] = dict(area=total,area_increment_over_base=total-base['area'],area_saved=control['area']-total,
                                timing='unknown; no predicted timing acceptance')

    forward_summary = HERE/'FORWARD_SUMMARY.json'
    forward_rows = []
    stage_c = 'pending_final_summary'
    forward_sha = None
    if forward_summary.exists():
        f = json.loads(forward_summary.read_text())
        audit.require(f['status'] == 'all13_finished' and len(f['rows']) == 13, 'StageC incomplete')
        audit.require(f['plan_sha256'] == audit.sha(HERE/'FORWARD_PLAN.json') and f['driver_sha256'] == audit.sha(HERE/'physical_probe_forward.py') and f['runner_sha256'] == audit.sha(HERE/'run_forward.py'), 'StageC provenance drift')
        forward_plan = json.loads((HERE/'FORWARD_PLAN.json').read_text())
        forward_batch = {j['arm']:j for j in f['jobs']}
        audit.require(len(forward_batch) == 13, 'StageC batch coverage incomplete')
        forward_rows = [audit.audit_arm(arm,restored,control,recovery,original,areas,TOL,forward_batch)
                        for arm,restored in forward_plan['singletons'].items()]
        audit.require(len(forward_rows)==13 and all(row['status'].startswith('validated_') for row in forward_rows), 'StageC has invalid evidence; no expansion')
        stage_c = 'all13_valid'
        forward_sha = audit.sha(forward_summary)
    print(json.dumps(dict(mode='execute' if execute else 'dry-check',stage_c=stage_c,arms=list(expected),exact_area_targets=predictions)),flush=True)
    if not execute:
        return 0
    audit.require(stage_c == 'all13_valid', 'StageC must finish13 valid cases before StageD')
    receipt,summary = HERE/'JOINT_RECEIPT.json',HERE/'JOINT_SUMMARY.json'
    audit.require(not receipt.exists() and not summary.exists(), 'Existing StageD results; no overwrite/resume')
    for arm in expected:
        audit.require(not (HERE/'runs'/arm).exists() and not (HERE/(arm+'.monitor.log')).exists(), 'Existing StageD endpoint/log')
    state = dict(status='running',runner_sha256=audit.sha(Path(__file__)),driver_sha256=audit.sha(driver),
                 plan_sha256=audit.sha(plan_path),recipe_sha256=audit.sha(HERE/'JOINT_RECIPE.json'),
                 forward_summary_sha256=forward_sha,source_sha256=plan['source_sha256'],
                 fixed_base=base,exact_area_targets=predictions,jobs=[],rows=[])
    def save():
        receipt.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    def finish(status):
        state['status']=status
        candidates=sorted((r for r in state['rows'] if r.get('primary_numeric_pass')),key=lambda r:(-r['area_saved'],r['arm']))
        forward_candidates=sorted((r for r in forward_rows if r.get('primary_numeric_pass')),key=lambda r:(-r['area_saved'],r['arm']))
        state['primary_candidates_pending_SEC']=[r['arm'] for r in candidates]
        state['selected_pending_SEC']=candidates[0]['arm'] if candidates else None
        state['forward_best_numeric_pending_SEC']=forward_candidates[0] if forward_candidates else None
        state['scope']='s3823 fixed independent compensation arms; numerical results only, SEC and independent review pending'
        state['limitations']=['Negative setup slack remains; relative nondegradation is not timing closure.',
                             'Supported-rule DRC/configured DRV only; no complete signoff claim.',
                             'Three additional runs informed by StagesA-C; not equal-budget superiority evidence.',
                             'No global optimality, transferability, independent-mechanism or novelty claim.']
        save()
        summary.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    save()
    for arm,restored in expected.items():
        for name,digest in plan['source_sha256'].items():
            if audit.sha(HERE/name)!=digest:
                finish('halted_source_drift_requires_attribution')
                return 1
        job=dict(arm=arm,restored=restored,status='running')
        state['jobs'].append(job);save()
        print('START',arm,flush=True);start=time.monotonic()
        with (HERE/(arm+'.monitor.log')).open('xb') as log:
            try:
                rc=subprocess.run([sys.executable,str(driver),arm],stdout=log,stderr=subprocess.STDOUT,timeout=1530).returncode
            except subprocess.TimeoutExpired:
                rc=124
            except OSError as exc:
                job['launch_error']=str(exc);rc=127
        job.update(returncode=rc,elapsed_s=time.monotonic()-start,status='complete')
        row=audit.audit_arm(arm,restored,control,recovery,recipe,areas,TOL,{arm:job})
        state['rows'].append(row);save()
        print('END',arm,rc,row['status'],flush=True)
        if rc or not row['status'].startswith('validated_'):
            finish('halted_failure_requires_attribution')
            return 1
        audit.require(abs(row['area']-predictions[arm]['area']) < 1e-9, 'Measured full-cell area differs from exact target')
    finish('all3_finished')
    return 0


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',help='Run3 physical arms; default only validates preparation')
    raise SystemExit(main(parser.parse_args().execute))
