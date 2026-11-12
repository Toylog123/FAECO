"""Bounded isolated forward baseline. Default is read-only preflight."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import analyze_repair as audit

HERE = Path(__file__).resolve().parent


def main(execute=False):
    plan_path = HERE / 'FORWARD_PLAN.json'
    plan = json.loads(plan_path.read_text())
    for name, digest in plan['source_sha256'].items():
        audit.require(audit.sha(HERE / name) == digest, 'Pinned source drift: ' + name)
    previous = json.loads((HERE / 'COMBINATION_SUMMARY.json').read_text())
    audit.require(previous['status'] == 'budget_exhausted_no_strict_candidate' and previous['physical_runs_attempted'] == 12, 'Stage B must be finished')
    driver = HERE / 'physical_probe_forward.py'
    audit.require(driver.read_text() == (HERE / 'physical_probe.py').read_text().replace("HERE / 'PLAN.json'", "HERE / 'FORWARD_PLAN.json'"), 'Driver changed beyond plan')
    for name, info in json.loads((HERE / 'inputs/MANIFEST.json').read_text()).items():
        audit.require(audit.sha(HERE / 'inputs' / name) == info['sha256'], 'Input drift')
    areas = audit.load_liberty_areas(audit.LIB)
    control, recovery = audit.baseline('CONTROL', areas), audit.baseline('RECOVERY_V2', areas)
    recipe = json.loads((HERE / 'inputs/recipe.json').read_text())['applied']
    names = sorted(r['instance'] for r in recipe)
    expected = {'FORWARD_' + n: [other for other in names if other != n] for n in names}
    audit.require(plan['singletons'] == expected and len(expected) == 13, 'Forward coverage mismatch')
    audit.require(plan['tolerance_ns'] == 1e-6 and plan['max_new_runs'] == 13, 'Gate or budget drift')
    state = dict(status='preflight', plan_sha256=audit.sha(plan_path), driver_sha256=audit.sha(driver),
                 runner_sha256=audit.sha(Path(__file__)), analyzer_sha256=audit.sha(HERE/'analyze_repair.py'),
                 source_sha256=plan['source_sha256'], jobs=[], rows=[])
    print(json.dumps({'mode': 'execute' if execute else 'preflight', 'arms': list(expected)}), flush=True)
    if not execute:
        return 0
    receipt = HERE / 'FORWARD_RECEIPT.json'
    summary = HERE / 'FORWARD_SUMMARY.json'
    audit.require(not receipt.exists() and not summary.exists(), 'No implicit overwrite or resume')

    def save():
        receipt.write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')

    state['status'] = 'running'
    save()
    for arm, restored in expected.items():
        audit.require(not (HERE/'runs'/arm).exists(), 'Existing endpoint')
        job = dict(arm=arm, restored=restored, status='running')
        state['jobs'].append(job)
        save()
        print('START', arm, flush=True)
        start = time.monotonic()
        with (HERE/(arm+'.monitor.log')).open('xb') as log:
            try:
                rc = subprocess.run([sys.executable, str(driver), arm], stdout=log, stderr=subprocess.STDOUT, timeout=1530).returncode
            except subprocess.TimeoutExpired:
                rc = 124
            except OSError as exc:
                job['launch_error'] = str(exc)
                rc = 127
        job.update(returncode=rc, elapsed_s=time.monotonic()-start, status='complete')
        row = audit.audit_arm(arm, restored, control, recovery, recipe, areas, 1e-6, {arm: job})
        state['rows'].append(row)
        save()
        print('END', arm, rc, row['status'], flush=True)
        if rc or not row['status'].startswith('validated_'):
            state['status'] = 'halted_failure_requires_attribution'
            save()
            return 1
    candidates = sorted((r for r in state['rows'] if r.get('primary_numeric_pass')), key=lambda r: (-r['area_saved'], r['arm']))
    state['status'] = 'all13_finished'
    state['primary_candidates_pending_SEC'] = [r['arm'] for r in candidates]
    state['selected_pending_SEC'] = candidates[0]['arm'] if candidates else None
    save()
    summary.write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    raise SystemExit(main(parser.parse_args().execute))
