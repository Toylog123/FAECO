"""Re-audit all four separately registered stages, without running EDA."""
import csv
import json
from pathlib import Path

import analyze_repair as audit

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def main():
    areas = audit.load_liberty_areas(audit.LIB)
    control, recovery = audit.baseline('CONTROL', areas), audit.baseline('RECOVERY_V2', areas)
    original = read('inputs/recipe.json')['applied']
    specifications = [
        ('A', 'PLAN.json', 'BATCH_RECEIPT.json', 'SUMMARY.json', 13, original),
        ('B', 'COMBINATION_PLAN.json', 'COMBINATION_RECEIPT.json', 'COMBINATION_SUMMARY.json', 12, original),
        ('C', 'FORWARD_PLAN.json', 'FORWARD_RECEIPT.json', 'FORWARD_SUMMARY.json', 13, original),
        ('D', 'JOINT_PLAN.json', 'JOINT_RECEIPT.json', 'JOINT_SUMMARY.json', 3, read('JOINT_RECIPE.json')['applied']),
    ]
    rows, stages, bindings = [], [], {}
    for stage, plan_file, receipt_file, summary_file, count, recipe in specifications:
        plan, receipt, summary = read(plan_file), read(receipt_file), read(summary_file)
        for name in (plan_file, receipt_file, summary_file):
            bindings[name] = audit.sha(HERE / name)
        audit.require(receipt['plan_sha256'] == bindings[plan_file], 'Receipt plan drift')
        jobs = {j['arm']: j for j in receipt['jobs']}
        audit.require(len(jobs) == count == len(receipt['jobs']) == len(summary['rows']), 'Stage coverage differs')
        registered = dict(plan.get('singletons', {}), **plan.get('combinations', {}))
        audited = []
        for old in summary['rows']:
            arm = old['arm']
            audit.require(arm in jobs and arm in registered, 'Unregistered endpoint')
            row = audit.audit_arm(arm, registered[arm], control, recovery, recipe, areas, 1e-6, jobs)
            audit.require(row == old, 'Fresh full audit differs from frozen row: ' + arm)
            audit.require(row['status'].startswith('validated_'), 'Invalid endpoint')
            manifest = read('runs/' + arm + '/manifest.json')
            audit.require(manifest['input_sha256'][str((HERE / ('physical_probe.py' if stage == 'A' else 'physical_probe_' + {'B': 'combination', 'C': 'forward', 'D': 'joint'}[stage] + '.py')).relative_to(audit.ROOT))] == receipt['driver_sha256'], 'Stage driver binding differs')
            audited.append(row)
            rows.append(dict(stage=stage, **row))
        stages.append(dict(stage=stage, physical_runs=count, standalone_sta_runs=2*count,
                           valid=count, strict_numeric_pass=sum(r['primary_numeric_pass'] for r in audited),
                           observed_job_seconds=sum(j['elapsed_s'] for j in jobs.values())))
    accepted = read('FORWARD_ACCEPTANCE.json')
    sec_path = 'sec/CONTROL_vs_FORWARD__096__models_v2/receipt.json'
    proof = read(sec_path)
    audit.require(accepted['status'] == 'accepted_local_conservative_baseline', 'Independent acceptance missing')
    audit.require(audit.sha(HERE / sec_path) == accepted['sec_receipt_sha256'], 'SEC receipt drift')
    audit.require(audit.sha(HERE / accepted['sec_driver_path']) == accepted['sec_driver_sha256'] == proof['driver_sha256'], 'Proof driver drift')
    audit.require(proof['status'] == 'pass' and proof['sources_unchanged'], 'SEC not passed')
    for name, digest in proof['proof_sha256'].items():
        audit.require(audit.sha(HERE / 'sec/CONTROL_vs_FORWARD__096__models_v2/proof' / name) == digest, 'Proof artifact drift')
    successful = [r['arm'] for r in rows if r['primary_numeric_pass']]
    audit.require(successful == ['FORWARD__096_'], 'Accepted set differs from independent review')
    bindings.update({name: audit.sha(HERE/name) for name in ['FORWARD_ACCEPTANCE.json', sec_path, 'summarize_study.py', 'analyze_repair.py']})
    result = dict(scope='s382 exploratory study; four sequentially registered budgets, not one prospective algorithm benchmark',
                  stages=stages, physical_runs=41, standalone_sta_runs=82, extra_readonly_pathdiagnostic_sta_runs=2,
                  sec_runs=1, accepted=accepted, rows=rows, source_sha256=bindings,
                  limitations=['One design/implementation and TT library only.',
                               'Relative nondegradation at measured constraints is not absolute timing closure or signoff.',
                               'Independent mechanism superiority remains unproven; the accepted point is a conservative baseline.',
                               'Shared-host elapsed time is not an exclusive performance benchmark.'])
    (HERE/'FINAL_RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    columns = ['stage', 'arm', 'area', 'area_saved', 'area_saved_pct', 'setup_delta_ns', 'tns_delta_ns', 'hold_delta_ns', 'primary_numeric_pass', 'sec_status']
    with (HERE/'RESULTS.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(stage=r['stage'], arm=r['arm'], area=r['area'], area_saved=r['area_saved'],
                area_saved_pct=r['area_saved_pct'], setup_delta_ns=r['deltas_ns']['setup_ns'],
                tns_delta_ns=r['deltas_ns']['tns_ns'], hold_delta_ns=r['deltas_ns']['hold_ns'],
                primary_numeric_pass=r['primary_numeric_pass'], sec_status='pass' if r['arm'] in successful else 'not_run'))
    print(json.dumps(dict(stages=stages, accepted=successful, all41_fresh_audits=True)), flush=True)


if __name__ == '__main__':
    main()
