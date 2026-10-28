"""Bounded serial execution of the root-approved r24 paired SPEF design."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
DESIGN = BASE / 'PAIRED_SPEF_DESIGN.json'
EXPECTED_DESIGN = 'f212e78473fc99dcca843aa9ce009b433eb557a8af2f60c858867763b8591465'
RUN = BASE / 'paired_spef_runs'
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.opensta import _sta_failure_reason

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def utc():
    return datetime.now(timezone.utc).isoformat()

assert sha(DESIGN) == EXPECTED_DESIGN
d = json.loads(DESIGN.read_text(encoding='utf-8'))
review = json.loads((BASE / 'PAIRED_SPEF_ROOT_DESIGN_REVIEW.json').read_text(encoding='utf-8'))
assert review['decision'] == 'approve_execution' and review['design_sha256'] == EXPECTED_DESIGN
RUN.mkdir(exist_ok=False)
started = time.perf_counter()
deadline = started + d['experiment_global_timeout_s']
progress = RUN / 'PROGRESS.jsonl'
results = []

def event(name, **data):
    row = {'event': name, 'UTC': utc(), 'elapsed_s': time.perf_counter() - started, **data}
    with progress.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps(row, ensure_ascii=False), flush=True)

def left():
    remaining = deadline - time.perf_counter()
    if remaining <= 0:
        raise TimeoutError('Global 1800 second deadline reached')
    return remaining

def guard():
    p = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
    assert p.returncode == 0 and p.stdout.decode().strip() == d['head']
    for row in d['sources'] + [d['model_scope'], d['static_precheck']]:
        assert sha(row['path']) == row['sha256'], row['path']
    for job in d['jobs_in_order']:
        for side in ['baseline', 'repaired']:
            assert sha(job[side]['path']) == job[side]['sha256']

def native(argv, out, timeout):
    out.mkdir(exist_ok=False)
    save(out / 'launch.json', {'argv': argv, 'started_UTC': utc(), 'timeout_s': timeout})
    t = time.perf_counter()
    env = dict(os.environ)
    env['PATH'] = r'C:\Windows\System32;C:\Windows'
    try:
        p = subprocess.run(argv, capture_output=True, timeout=min(timeout, left()), env=env)
    except subprocess.TimeoutExpired as exc:
        (out / 'stdout.bin').write_bytes(exc.stdout or b'')
        (out / 'stderr.bin').write_bytes(exc.stderr or b'')
        save(out / 'return.json', {'timeout': True, 'elapsed_s': time.perf_counter() - t})
        raise
    (out / 'stdout.bin').write_bytes(p.stdout)
    (out / 'stderr.bin').write_bytes(p.stderr)
    save(out / 'return.json', {'returncode': p.returncode, 'elapsed_s': time.perf_counter() - t,
         'stdout_sha256': sha(out / 'stdout.bin'), 'stderr_sha256': sha(out / 'stderr.bin')})
    return p

def check_text(text):
    reason = _sta_failure_reason(text, 0)
    if reason or re.search(r'(?im)^\s*(?:fatal|error)\b|(?:not found|failed to read|unknown instance)', text):
        raise ValueError(reason or 'Unexpected native tool diagnostic')

try:
    guard()
    save(RUN / 'EXECUTION_PIN.json', {'design': EXPECTED_DESIGN,
        'driver_sha256': sha(__file__), 'worker_sha256': sha(BASE / 'paired_spef_api_worker.py'),
        'root_review_sha256': sha(BASE / 'PAIRED_SPEF_ROOT_DESIGN_REVIEW.json'),
        'started_UTC': utc(), 'head': d['head']})
    pin = d['runtime_tool_pin']['expected_from_accepted_tiny_pilot']
    version = native(['wsl.exe', '-d', 'Ubuntu', '--', pin['binary'], '-version'], RUN / '_version', 30)
    binary = native(['wsl.exe', '-d', 'Ubuntu', '--', 'sha256sum', pin['binary']], RUN / '_binary', 30)
    assert version.returncode == 0 and pin['version'] in version.stdout.decode('utf-8', 'replace')
    assert binary.returncode == 0 and binary.stdout.decode().split()[0] == pin['sha256']
    event('tool_pin_verified', version=pin['version'], sha256=pin['sha256'])
    for job in d['jobs_in_order']:
        guard()
        left()
        event('case_start', case=job['name'])
        cap = RUN / '_workers' / job['name']
        cap.mkdir(parents=True, exist_ok=False)
        argv = [d['python_executable'], '-u', '-X', 'utf8', str(BASE / 'paired_spef_api_worker.py'),
                '--design', str(DESIGN), '--job', job['name']]
        save(cap / 'launch.json', {'argv': argv, 'scientific_cli_argv': job['argv'],
             'case_timeout_s': job['outer_case_timeout_s'], 'started_UTC': utc()})
        t = time.perf_counter()
        with (cap / 'stdout.bin').open('xb') as so, (cap / 'stderr.bin').open('xb') as se:
            p = subprocess.Popen(argv, cwd=ROOT, stdout=so, stderr=se)
            case_deadline = min(deadline, t + job['outer_case_timeout_s'])
            while p.poll() is None:
                if time.perf_counter() >= case_deadline:
                    subprocess.run(['taskkill.exe', '/PID', str(p.pid), '/T', '/F'], capture_output=True, timeout=30)
                    raise TimeoutError('Outer case/global deadline: ' + job['name'])
                time.sleep(1)
        save(cap / 'return.json', {'returncode': p.returncode, 'elapsed_s': time.perf_counter() - t})
        if p.returncode:
            raise RuntimeError('Scientific CLI failed: ' + job['name'])
        output = Path(job['output_dir'])
        summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
        assert summary['valid']
        api_capture = RUN / '_api_capture' / job['name']
        launches = sorted(api_capture.glob('launch_*/return.json'))
        assert len(launches) == 4
        annotations = []
        for side in ['baseline', 'repaired']:
            for mode in ['ideal', 'spef']:
                m = output / (side + '_' + mode)
                receipt = json.loads((m / 'measurement_receipt.json').read_text(encoding='utf-8'))
                assert receipt['valid'] and receipt['returncode'] == 0
                for row in [receipt['netlist'], receipt['liberty'], receipt['spef'], receipt['tcl'], receipt['log']]:
                    if row:
                        assert sha(row['path']) == row['sha256']
                for label in ['stdout.bin', 'stderr.bin']:
                    check_text((api_capture / ('launch_%02d' % (1 + (2 if side == 'repaired' else 0) + (1 if mode == 'spef' else 0))) / label).read_bytes().decode('utf-8', 'replace'))
                tcl = (m / 'sta.tcl').read_text(encoding='utf-8')
                if mode == 'spef':
                    assert tcl.index('read_spef ') < tcl.index('report_checks ')
                    assert math.isfinite(summary['rows'][side + '_spef']['wns'])
        for replay in job['annotation_replay_after_API']:
            tcl = Path(replay['base_tcl']).read_text(encoding='utf-8')
            Path(replay['annotation_tcl']).write_text(tcl + '\n' + replay['append_only_tcl_command'] + '\n', encoding='utf-8')
            p = native(replay['argv'], Path(replay['annotation_tcl']).parent / 'annotation_replay', replay['timeout_s'])
            raw = p.stdout.decode('utf-8', 'replace') + '\n' + p.stderr.decode('utf-8', 'replace')
            assert p.returncode == 0
            check_text(raw)
            assert re.search(r'Found 0 unannotated drivers\.', raw)
            assert re.search(r'Found 0 partially unannotated drivers\.', raw)
            vals = re.findall(r'worst slack max\s+(-?\d+\.\d+)', raw)
            assert vals
            api_wns = summary['rows'][replay['side'] + '_spef']['wns']
            assert float(vals[-1]) == api_wns
            annotations.append({'side': replay['side'], 'wns': float(vals[-1]),
                'unannotated': 0, 'partially_unannotated': 0,
                'stdout_sha256': sha(Path(replay['annotation_tcl']).parent / 'annotation_replay/stdout.bin'),
                'stderr_sha256': sha(Path(replay['annotation_tcl']).parent / 'annotation_replay/stderr.bin')})
        if job['name'].startswith('control'):
            assert summary['ideal_delta'] == 0 and summary['spef_delta'] == 0
            assert (output / 'baseline.spef').read_bytes() == (output / 'repaired.spef').read_bytes()
        guard()
        row = {'case': job['name'], 'length_um': job['length_um'],
            'summary_path': str(output / 'summary.json'), 'summary_sha256': sha(output / 'summary.json'),
            'ideal_delta': summary['ideal_delta'], 'spef_delta': summary['spef_delta'],
            'rows': summary['rows'], 'annotations': annotations, 'accepted_data': True}
        results.append(row)
        save(output / 'CASE_ACCEPTANCE.json', row)
        event('case_pass', **row)
    guard()
    physical = [r for r in results if not r['case'].startswith('control')]
    sensitivity = any(r['rows'][side + '_ideal']['wns'] != r['rows'][side + '_spef']['wns'] for r in physical for side in ['baseline', 'repaired'])
    save(RUN / 'RESULT.json', {'status': 'complete', 'head': d['head'], 'design_sha256': EXPECTED_DESIGN,
        'source_stable': True, 'input_stable': True, 'results': results, 'injection_sensitivity_observed': sensitivity,
        'elapsed_s': time.perf_counter() - started,
        'actual_API_launches': len(list((RUN / '_api_capture').glob('*/launch_*/return.json'))),
        'actual_annotation_launches': len(list(RUN.glob('*/**/annotation_replay/return.json'))),
        'scope': d['claim_scope']})
    event('complete', cases=len(results), injection_sensitivity_observed=sensitivity)
except Exception as exc:
    save(RUN / 'FAILURE.json', {'status': 'stopped', 'error_type': type(exc).__name__, 'error': str(exc),
        'elapsed_s': time.perf_counter() - started, 'completed_cases': results,
        'actual_API_launches': len(list((RUN / '_api_capture').glob('*/launch_*/return.json'))),
        'actual_annotation_launches': len(list(RUN.glob('*/**/annotation_replay/return.json')))})
    event('stopped', error_type=type(exc).__name__, error=str(exc))
    raise
