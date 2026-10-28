"""Root acceptance of the independent v3 review over the FULL registered D56 set.

This is the 56-key counterpart of accept_d28_v3_20261018.py.  Differences:

  1. the audit is ROOT_COMPLETION_AUDIT_56.json and the review is
     independent_completed_review/run_56_v1;
  2. `full_56_registered_keys_reviewed` must be TRUE (in the 28-run it had to
     be false, because the 28-run was a subset by design);
  3. the canonical counts are NOT hardcoded.  The 28-acceptance hardcoded
     them; here the counts that the root audit can independently produce are
     recomputed from the audit and compared with the checker's totals, and the
     checker's remaining totals are recorded with their source.  The
     acceptance therefore does not simply echo the checker.

Still NOT claimed by this receipt: physical RC extraction, four-state
support, or any global scientific closure.  It says: the 56 registered
completion records were independently re-read from their raw artefacts, every
registered key was covered, every SEC claim is proven, and the registered
production source is unchanged.
"""
from pathlib import Path
import json, hashlib, subprocess

ROOT = Path.cwd().resolve()
BASE = ROOT / 'project_docs/evidence/r22_D_revalidation_20261018'
RUN = BASE / 'independent_completed_review/run_56_v1'
PREP = BASE / 'ledger_duplicate_diagnosis_20261018'

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

audit_path = BASE / 'ROOT_COMPLETION_AUDIT_56.json'
audit = read(audit_path)
audit_sha = sha(audit_path)

final = read(RUN / 'FINAL_RECEIPT.json')
inv = read(RUN / 'INVOCATION.json')
result = read(RUN / 'review/RESULT.json')

# --- the review itself must be intact -------------------------------------
assert final['returncode'] == 0 and final['checker_unchanged']
assert final['result_sha256'] == sha(RUN / 'review/RESULT.json')
assert final['log_sha256'] == sha(RUN / 'WRAPPER.log')
assert result['checker_sha256'] == inv['checker_sha256'] == sha(PREP / 'checker_v3.py') \
    == 'f6b053dfa6552aca43817f0dc1c1bdefca295c32bdf7ddc4b01cf1b12ab71daf'
assert result['schema'] == 'r22-D-frozen-subset-independent-raw-review-v3'
assert result['audit_sha256'] == audit_sha and result['all_read_artifacts_stable']

# --- the coverage must be the FULL registered set -------------------------
manifest = read(ROOT / 'experiments/20261018_r22_D_revalidate_v1/manifest.json')
manifest_keys = {j['key'] for j in manifest['jobs']}
assert len(manifest_keys) == 56
assert result['full_56_registered_keys_reviewed'] is True, \
    'the checker did not report the full registered set'
assert result['completion_set_frozen_at_start'] == audit['completion_set_frozen_at_start']
assert len(result['rows']) == 56
assert {row['key'] for row in result['rows']} == set(audit['completion_set_frozen_at_start'])
assert not result['extra_completed_at_start_not_reviewed']
assert not result['extra_completed_at_end_not_reviewed']

# --- the counts are cross-checked against the root audit, not hardcoded ----
jobs = {j['key']: j for j in manifest['jobs']}
audit_rows = {r['key']: r for r in audit['jobs']}
expected_from_audit = {
    'jobs': 56,
    'candidate_evaluation_records': sum(r['n_candidate_evaluation_records']
                                         for r in audit_rows.values()),
    'cache_replays': sum(r['n_cache_replays'] for r in audit_rows.values()),
    'SEC_passes': sum(1 for r in audit_rows.values() if r['sec_status'] == 'pass'),
    'baseline_STA_runs': 56,
}
totals = result['totals']
for k, v in expected_from_audit.items():
    assert totals[k] == v, (k, totals[k], v)

# --- every completion SHA is re-verified against the live artefact -------
for key, digest in audit['completion_set_frozen_at_start'].items():
    assert sha(ROOT / Path(jobs[key]['output_dir']) / 'completion.json') == digest
for row in result['rows']:
    assert row['sec_proven'] > 0 and row['sec_unproven'] == 0

# --- the registered production source is unchanged -------------------------
for name, digest in manifest['source_pin']['files'].items():
    assert sha(ROOT / name) == digest
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                text=True).strip() == manifest['source_pin']['head']
assert (RUN / 'review/SOURCE_BEFORE.json').read_bytes() == \
    (RUN / 'review/SOURCE_AFTER.json').read_bytes()
assert len(read(RUN / 'review/SOURCE_AFTER.json')) == result['read_artifact_count']

paths = [audit_path, PREP / 'checker_v3.py', PREP / 'V3_DESIGN.md',
         PREP / 'DIAGNOSIS.json', RUN / 'INVOCATION.json', RUN / 'FINAL_RECEIPT.json',
         RUN / 'WRAPPER.log', RUN / 'review/RESULT.json',
         RUN / 'review/SOURCE_BEFORE.json', RUN / 'review/SOURCE_AFTER.json']

receipt = {
    'accepted': True,
    'scope': ('The full immutable registered D56 completion set; no key is '
              'outside it. Independent raw review by the root-reviewed v3 '
              'checker. NOT physical RC, NOT four-state support, NOT global '
              'scientific closure.'),
    'parent_root_audit_sha256': audit_sha,
    'completion_set': audit['completion_set_frozen_at_start'],
    'review_artifacts': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
    'source_head': manifest['source_pin']['head'],
    'all45_runtime_source_current_match': True,
    'independent_read_artifact_count': result['read_artifact_count'],
    'independent_read_sources_before_after_stable': True,
    'root_current_completion_sha_verified': 56,
    'root_reviewed_preexecution_checker_source_diff_and_design': True,
    'canonical_counts': totals,
    'canonical_counts_cross_checked_against_root_audit': expected_from_audit,
    'legacy_cache_field_is_compatibility_sum_not_pure_STA_reuse': True,
    'full56_accepted': True,
    'extra_completed_at_review_start_not_accepted': [],
    'extra_completed_at_review_end_not_accepted': [],
    'timeout_registration': inv.get('timeout_registration'),
}

(BASE / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
out = BASE / 'INDEPENDENT_56_ROOT_ACCEPTANCE.json'
assert not out.exists(), 'the 56 acceptance receipt already exists'
with out.open('x', encoding='utf-8') as f:
    json.dump(receipt, f, indent=2)
    f.write('\n')
print(json.dumps({'accepted': True, 'completed_accepted': 56,
                  'counts': totals, 'counts_cross_checked': expected_from_audit,
                  'root_receipt_sha256': sha(out)}))
