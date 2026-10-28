"""Preserve the invalidated initial inventory and freeze actual final v2 bytes; no EDA."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
V2 = BASE / 'paired_spef_flat_v2'
OLD = V2 / 'FROZEN_DERIVED_INPUTS.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def rec(p):
    raw = p.read_bytes()
    return {'path': str(p.resolve()), 'sha256': sha(raw), 'bytes': len(raw)}

def save_new(p, v):
    with p.open('x', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return rec(p)

old_bytes = OLD.read_bytes()
assert sha(old_bytes) == '2a9c6ef58e9fb1588b042f7116b9f9148c1a939511014ca3292346ad8c8e87bd'
old = json.loads(old_bytes.decode('utf-8'))
design = json.loads((BASE / 'PAIRED_SPEF_FLAT_V2_DESIGN.json').read_text(encoding='utf-8'))
rows, differences = [], []
for expected in old['artifacts']:
    path = Path(expected['path'])
    raw = path.read_bytes()
    actual = rec(path)
    row = {'expected_initial': expected, 'actual_final': actual, 'match': actual['sha256'] == expected['sha256'] and actual['bytes'] == expected['bytes']}
    rows.append(row)
    if not row['match']:
        prefix, suffix = raw[:expected['bytes']], raw[expected['bytes']:]
        event = json.loads(suffix.decode('utf-8'))
        assert path.name == 'PROGRESS.jsonl' and sha(prefix) == expected['sha256']
        assert len(suffix.splitlines()) == 1
        assert event['event'] == 'complete_pending_root_review' and event['flatten'] == event['SEC'] == 2 and event['STA'] == 0
        differences.append({**row, 'initial_byte_prefix_exact_sha_match': True,
            'prefix_sha256': sha(prefix), 'appended_bytes': len(suffix), 'appended_sha256': sha(suffix),
            'appended_utf8': suffix.decode('utf-8'), 'appended_event': event})
assert len(differences) == 1
head_proc = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
head = head_proc.stdout.decode().strip()
assert head_proc.returncode == 0 and head == design['head']
pins = []
for expected in design['sources'] + [design['model_scope']] + [j['raw'] for j in design['jobs']]:
    actual = rec(Path(expected['path']))
    assert actual['sha256'] == expected['sha256'] and actual['bytes'] == expected['bytes']
    pins.append({'expected': expected, 'actual': actual, 'match': True})
audit = {'schema': 'r24-flat-v2-post-freeze-audit-v1', 'UTC': datetime.now(timezone.utc).isoformat(),
    'EDA_started_in_this_audit': False, 'initial_manifest_preserved': rec(OLD),
    'initial_manifest_current_inventory_valid': False,
    'cause': 'Executor wrote initial inventory, then appended final complete_pending_root_review event to PROGRESS.jsonl. This was a freeze-order implementation mistake, not input/source/proof byte drift.',
    'initial_inventory_items': len(rows), 'unchanged_items': len(rows) - 1,
    'differences': differences, 'all_initial_inventory_comparisons': rows,
    'head': head, 'pinned_sources_Lib_models_raw_inputs_match': pins,
    'scientific_flat_and_SEC_artifacts_unchanged': True, 'new_STA_processes': 0,
    'future_protocol': 'Write final progress event first; close logs; snapshot final inventory; perform no later writes to registered members. Never rewrite initial manifest to hide the discrepancy.'}
audit_record = save_new(BASE / 'PAIRED_SPEF_FLAT_V2_POST_FREEZE_AUDIT.json', audit)
members = sorted(p for p in V2.rglob('*') if p.is_file())
additional = [BASE / n for n in ['PAIRED_SPEF_FLAT_V2_DESIGN.json', 'PAIRED_SPEF_FLAT_V2_DESIGN.md',
    'PAIRED_SPEF_FLAT_V2_ROOT_REVIEW.json', 'PAIRED_SPEF_FLAT_V2_REPORT.md', 'run_flatten_sec_v2.py',
    'audit_flat_v2_final_freeze.py', 'PAIRED_SPEF_FLAT_V2_POST_FREEZE_AUDIT.json']]
inventory = [rec(p) for p in [*members, *additional]]
for r in inventory:
    assert rec(Path(r['path'])) == r
final = {'schema': 'r24-flat-v2-final-byte-manifest-v1', 'UTC': datetime.now(timezone.utc).isoformat(),
    'status': 'final_static_flat_and_two_SEC_bytes_frozen_pending_root_STA_review',
    'head': head, 'initial_manifest': rec(OLD), 'post_freeze_audit': audit_record,
    'initial_manifest_inventory_was_invalidated': True, 'reason': 'One final progress event appended after initial inventory; original and full mismatch retained.',
    'flat_inputs_and_SEC_bindings': old['flat_inputs'], 'current_artifact_inventory': inventory,
    'member_count': len(inventory), 'all_members_rechecked_after_inventory': True,
    'sources_Lib_models_raw_inputs_match': True, 'actual_flatten_launches': 2, 'actual_SEC_launches': 2,
    'STA_launches': 0, 'logs_closed_no_more_member_appends': True,
    'future_STA_outputs_must_be_in_separate_directory': True,
    'scope': old['scope']}
final_record = save_new(BASE / 'PAIRED_SPEF_FLAT_V2_FINAL_MANIFEST.json', final)
for r in inventory:
    assert rec(Path(r['path'])) == r
assert OLD.read_bytes() == old_bytes
print(json.dumps({'audit': audit_record, 'final_manifest': final_record,
    'initial_manifest_untouched': True, 'only_difference': '153 appended bytes: one final completion event',
    'new_EDA': 0}, ensure_ascii=False, indent=2))
