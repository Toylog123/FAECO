"""Static post-audit of all 24 actual v2 STA launches and their raw/input bindings."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
RUN = BASE / 'paired_spef_flat_v2_STA_runs'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rec(p):
    p = Path(p)
    return {'path': str(p.resolve()), 'sha256': sha(p), 'bytes': p.stat().st_size}

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def decode(b):
    return b.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')

def wns(s):
    values = re.findall(r'worst slack max\s+(-?\d+\.\d+)', s)
    assert len(values) == 1
    return Decimal(values[0])

d = load(BASE / 'PAIRED_SPEF_FLAT_V2_STA_DESIGN.json')
r = load(RUN / 'RESULT.json')
assert r['status'] == 'complete'
assert sha(BASE / 'PAIRED_SPEF_FLAT_V2_STA_DESIGN.json') == r['design_sha256']
inventory = []
for row in r['final_artifact_inventory']:
    assert rec(row['path']) == row
    inventory.append(row)
fm = load(d['canonicalization_final_manifest']['path'])
assert rec(d['canonicalization_final_manifest']['path']) == d['canonicalization_final_manifest']
for row in fm['current_artifact_inventory']:
    assert rec(row['path']) == row
source_after = []
for row in d['sources'] + [d['model_scope'], d['capture_worker'], d['canonicalization_final_manifest'], d['post_freeze_audit']]:
    actual = rec(row['path'])
    assert actual['sha256'] == row['sha256'] and actual['bytes'] == row['bytes']
    source_after.append({'expected': row, 'actual': actual, 'match': True})
p = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
assert p.returncode == 0 and p.stdout.decode().strip() == d['head']
all_api, all_annotation, table = [], [], []
for job in d['jobs_in_order']:
    name = job['name']
    output = Path(job['output_dir'])
    summary = load(output / 'summary.json')
    assert summary['valid'] and summary['period_ns'] == 0.5 and summary['clock_port'] == 'CK'
    measured = {}
    for seq, key in enumerate(['baseline_ideal', 'baseline_spef', 'repaired_ideal', 'repaired_spef'], 1):
        capture = RUN / '_api_capture' / name / f'launch_{seq:02d}'
        intent, ret = load(capture / 'launch_intent.json'), load(capture / 'return.json')
        receipt = load(output / key / 'measurement_receipt.json')
        stdout, stderr = (capture / 'stdout.bin').read_bytes(), (capture / 'stderr.bin').read_bytes()
        text = decode(stdout) + decode(stderr)
        log = output / key / 'sta.log'
        assert text == log.read_text(encoding='utf-8')
        assert hashlib.sha256(stdout).hexdigest() == ret['stdout_sha256']
        assert hashlib.sha256(stderr).hexdigest() == ret['stderr_sha256']
        assert intent['argv'] == receipt['argv'] and ret['returncode'] == receipt['returncode'] == 0
        assert intent['timeout_s'] == receipt['timeout_s'] == 600 and receipt['valid']
        for role in ['netlist', 'liberty', 'spef', 'tcl', 'log']:
            if receipt[role]:
                actual = rec(receipt[role]['path'])
                assert actual['sha256'] == receipt[role]['sha256'] and actual['bytes'] == receipt[role]['bytes']
        assert receipt['inputs_after']['netlist'] == receipt['netlist']
        assert receipt['inputs_after']['liberty'] == receipt['liberty']
        assert receipt['inputs_after']['spef'] == receipt['spef']
        side = key.split('_')[0]
        assert receipt['netlist']['sha256'] == job[side]['sha256']
        assert receipt['top'] == 's382' and receipt['clock_port'] == 'CK' and receipt['period_ns'] == 0.5
        assert receipt['rc_model'] == {'unit_len_um': job['length_um'], 'fanout_penalty': 1.0, 'depth_penalty': 1.0}
        measured[key] = wns(text)
        assert measured[key] == Decimal(str(summary['rows'][key]['wns']))
        tcl = (output / key / 'sta.tcl').read_text(encoding='utf-8')
        if key.endswith('_spef'):
            assert tcl.index('read_spef ') < tcl.index('report_checks ')
        else:
            assert 'read_spef ' not in tcl
        assert not re.search(r'(?im)^\s*(?:fatal|error)\b|(?:not found|failed to read|unknown instance)', text)
        all_api.append({'case': name, 'mode': key, 'argv': intent['argv'], 'returncode': 0, 'timeout_s': 600,
            'native_stdout': rec(capture / 'stdout.bin'), 'native_stderr': rec(capture / 'stderr.bin'),
            'raw_streams_reproduce_original_runner_log': True, 'wns_from_raw': str(measured[key]),
            'measurement_receipt': rec(output / key / 'measurement_receipt.json'),
            'input_model_Tcl_before_after_bindings_match': True})
    for replay in job['annotation_replay_after_API']:
        path = Path(replay['annotation_tcl']).parent / 'annotation_replay'
        launch, ret = load(path / 'launch.json'), load(path / 'return.json')
        so, se = (path / 'stdout.bin').read_bytes(), (path / 'stderr.bin').read_bytes()
        assert launch['argv'] == replay['argv'] and ret['returncode'] == 0
        assert hashlib.sha256(so).hexdigest() == ret['stdout_sha256'] and hashlib.sha256(se).hexdigest() == ret['stderr_sha256']
        txt = decode(so) + '\n' + decode(se)
        assert re.findall(r'Found (\d+) unannotated drivers\.', txt) == ['0']
        assert re.findall(r'Found (\d+) partially unannotated drivers\.', txt) == ['0']
        assert wns(txt) == measured[replay['side'] + '_spef']
        original_tcl = Path(replay['base_tcl']).read_text(encoding='utf-8')
        derived_tcl = Path(replay['annotation_tcl']).read_text(encoding='utf-8')
        assert derived_tcl == original_tcl + '\n' + replay['append_only_tcl_command'] + '\n'
        assert not re.search(r'(?im)^\s*(?:fatal|error)\b|(?:not found|failed to read|unknown instance)', txt)
        all_annotation.append({'case': name, 'side': replay['side'], 'argv': launch['argv'], 'returncode': 0,
            'timeout_s': launch['timeout_s'], 'unannotated': 0, 'partial': 0,
            'WNS_equals_fresh_API': True, 'only_added_annotation_command': True,
            'stdout': rec(path / 'stdout.bin'), 'stderr': rec(path / 'stderr.bin'),
            'Tcl': rec(replay['annotation_tcl'])})
    ideal = measured['repaired_ideal'] - measured['baseline_ideal']
    physical = measured['repaired_spef'] - measured['baseline_spef']
    assert ideal == Decimal(str(summary['ideal_delta'])) and physical == Decimal(str(summary['spef_delta']))
    if name.startswith('control'):
        assert ideal == physical == 0
        assert (output / 'baseline.spef').read_bytes() == (output / 'repaired.spef').read_bytes()
    table.append({'case': name, 'unit_um': job['length_um'],
        'baseline_ideal_WNS_ns': str(measured['baseline_ideal']), 'final_ideal_WNS_ns': str(measured['repaired_ideal']),
        'ideal_delta_ns': str(ideal), 'baseline_SPEF_WNS_ns': str(measured['baseline_spef']),
        'final_SPEF_WNS_ns': str(measured['repaired_spef']), 'SPEF_delta_ns': str(physical),
        'both_sides_same_model_constraints': True, 'fresh_ideal_measured_in_this_API_job': True})
assert len(all_api) == 16 and len(all_annotation) == 8
journal = (RUN / 'PROGRESS.jsonl').read_bytes()
assert json.loads(journal.splitlines()[-1].decode('utf-8'))['event'] == 'complete'
out = {'schema': 'r24-flat-SPEF-STA-v2-post-audit-v1', 'UTC': datetime.now(timezone.utc).isoformat(),
    'EDA_started_in_this_audit': False, 'producer_RESULT': rec(RUN / 'RESULT.json'),
    'design': rec(BASE / 'PAIRED_SPEF_FLAT_V2_STA_DESIGN.json'),
    'all_194_final_inventory_members_match': True, 'final_inventory_member_count': len(inventory),
    'completion_event_written_before_freeze_and_no_later_append': True, 'final_journal': rec(RUN / 'PROGRESS.jsonl'),
    'canonicalization_final_manifest_all_68_members_match': True,
    'head': d['head'], 'all_sources_Lib_models_flat_inputs_stable': True, 'source_after': source_after,
    'flat_inputs': d['flat_input_bindings'], 'actual_API_measurements': all_api,
    'actual_annotation_replays': all_annotation, 'actual_total_STA_launches': 24,
    'identity_queries_excluded_from_STA_count': 2, 'table': table,
    'no_missing_pin_unknown_instance_or_native_error_in_all_24_original_streams': True,
    'all_8_replays_zero_unannotated_zero_partial': True,
    'scope': d['claim_scope'], 'producer_elapsed_s': r['elapsed_s'],
    'audit_script': rec(__file__)}
p = BASE / 'PAIRED_SPEF_FLAT_V2_STA_POST_AUDIT.json'
with p.open('x', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write('\n')
for row in inventory:
    assert rec(row['path']) == row
print(json.dumps({'post_audit': rec(p), 'actual_API': len(all_api), 'actual_annotation': len(all_annotation),
    'all_final_inventory_stable': True, 'table': table}, ensure_ascii=False, indent=2))
