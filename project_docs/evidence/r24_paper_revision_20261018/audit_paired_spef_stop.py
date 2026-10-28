"""Static postfailure accounting of the first r24 paired-SPEF control; no EDA."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
RUN = BASE / 'paired_spef_runs'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def record(p):
    return {'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size}

def decode(b):
    return b.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')

d = load(BASE / 'PAIRED_SPEF_DESIGN.json')
head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
head_current = head.stdout.decode().strip()
source_after = [{**row, 'actual_sha256': sha(Path(row['path'])),
    'match': sha(Path(row['path'])) == row['sha256']} for row in d['sources']]
input_after = [{**row, 'actual_sha256': sha(Path(row['path'])),
    'match': sha(Path(row['path'])) == row['sha256']}
    for row in d['jobs_in_order'][0:2] for row in [row['baseline'], row['repaired']]]
capture = RUN / '_api_capture/control_same_u40'
control = RUN / 'control_same_u40'
api = []
for index, key in enumerate(['baseline_ideal', 'baseline_spef', 'repaired_ideal', 'repaired_spef'], 1):
    launch = capture / f'launch_{index:02d}'
    intent, ret = load(launch / 'launch_intent.json'), load(launch / 'return.json')
    receipt = load(control / key / 'measurement_receipt.json')
    stdout, stderr = (launch / 'stdout.bin').read_bytes(), (launch / 'stderr.bin').read_bytes()
    expected_log = decode(stdout) + decode(stderr)
    actual_log = (control / key / 'sta.log').read_text(encoding='utf-8')
    api.append({'mode': key, 'intent': record(launch / 'launch_intent.json'),
        'return': record(launch / 'return.json'), 'receipt': record(control / key / 'measurement_receipt.json'),
        'argv_matches_receipt': intent['argv'] == receipt['argv'], 'timeout_unchanged_600': intent['timeout_s'] == receipt['timeout_s'] == 600,
        'returncode': ret['returncode'], 'receipt_valid': receipt['valid'],
        'raw_streams_reproduce_original_runner_log_after_original_newline_decode': expected_log == actual_log,
        'stdout': record(launch / 'stdout.bin'), 'stderr': record(launch / 'stderr.bin')})
annot = control / 'baseline_spef/annotation_replay'
raw = (annot / 'stdout.bin').read_bytes().decode('utf-8', 'replace')
rawlines = raw.splitlines()
driver_groups = []
for line in rawlines:
    if re.fullmatch(r' [^\s].*', line):
        driver_groups.append({'driver': line.strip(), 'unannotated_sinks': []})
    elif line.startswith('  ') and driver_groups:
        driver_groups[-1]['unannotated_sinks'].append(line.strip())
counts = {'clock': sum(g['driver'] == 'CK' for g in driver_groups),
          'helper_Q_drivers': sum(bool(re.fullmatch(r'DFF_\d+/_0_/Q', g['driver'])) for g in driver_groups),
          'combinational_drivers_to_helper_D': sum(any(re.fullmatch(r'DFF_\d+/_0_/D', s) for s in g['unannotated_sinks']) for g in driver_groups)}
assert len(driver_groups) == 43 and counts == {'clock': 1, 'helper_Q_drivers': 21, 'combinational_drivers_to_helper_D': 21}
summary = load(control / 'summary.json')
output = {
    'schema': 'r24-paired-spef-stopped-control-audit-v1', 'UTC': datetime.now(timezone.utc).isoformat(),
    'decision': 'stop_no_scientific_pair_WNS_admitted', 'EDA_started_in_this_audit': False,
    'head_current': head_current, 'head_matches': head_current == d['head'],
    'source_after': source_after, 'all_sources_match': all(r['match'] for r in source_after),
    'inputs_after': input_after, 'all_inputs_match': all(r['match'] for r in input_after),
    'API_launches': api, 'API_launch_count': len(api), 'annotation_launch_count': 1,
    'annotation_returncode': load(annot / 'return.json')['returncode'],
    'annotation_stdout': record(annot / 'stdout.bin'), 'annotation_stderr': record(annot / 'stderr.bin'),
    'annotation_counts': {'unannotated_drivers': 0, 'partially_unannotated_drivers': 43},
    'partial_driver_groups': driver_groups, 'partial_driver_categories': counts,
    'control_numeric_observations_not_accepted_science': {k: v['wns'] for k, v in summary['rows'].items()},
    'control_delta_ideal': summary['ideal_delta'], 'control_delta_spef': summary['spef_delta'],
    'baseline_repaired_SPEF_bytes_equal': (control / 'baseline.spef').read_bytes() == (control / 'repaired.spef').read_bytes(),
    'attribution': 'Static SPEF module-interface endpoints DFF_N:{CK,D,Q} do not close actual OpenSTA leaf endpoints DFF_N/_0_/{CLK,D,Q}; source parser uses helper module port directions without recursive leaf expansion.',
    'scope': 'Current hierarchical-helper SPEF injection coverage failure, not evidence that FAECO ideal timing gain or underlying candidate equivalence is false.',
    'implementation_sources': [record(BASE / n) for n in ['run_paired_spef_registered.py', 'paired_spef_api_worker.py', 'prepare_paired_spef_design.py']],
    'unstarted_jobs': [j['name'] for j in d['jobs_in_order'] if not Path(j['output_dir']).exists()],
    'new_artifact_inventory': [record(p) for p in sorted(RUN.rglob('*')) if p.is_file()],
}
assert output['head_matches'] and output['all_sources_match'] and output['all_inputs_match']
assert all(r['argv_matches_receipt'] and r['timeout_unchanged_600'] and r['raw_streams_reproduce_original_runner_log_after_original_newline_decode'] for r in api)
p = BASE / 'PAIRED_SPEF_STOP_AUDIT.json'
with p.open('x', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'output': record(p), 'actual_API': len(api), 'actual_annotation': 1,
    'partial': counts, 'source_input_HEAD_stable': True, 'raw_stream_decode_reproduction': True}, ensure_ascii=False, indent=2))
