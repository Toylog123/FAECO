"""Root acceptance of independent v3's immutable D28 subset, not full D56."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path.cwd().resolve();BASE=ROOT/'project_docs/evidence/r22_D_revalidation_20261018'
RUN=BASE/'independent_completed_review/run_28_v2';PREP=BASE/'ledger_duplicate_diagnosis_20261018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
audit_path=BASE/'ROOT_COMPLETION_AUDIT_28.json';audit=read(audit_path)
assert sha(audit_path)=='1db9b0fb778c2dfdb411d2095519479f59c6ef2cfb35ba34416f89eb8c47ab4d'
final=read(RUN/'FINAL_RECEIPT.json');inv=read(RUN/'INVOCATION.json');result=read(RUN/'review/RESULT.json')
assert final['returncode']==0 and final['checker_unchanged']
assert final['result_sha256']==sha(RUN/'review/RESULT.json')
assert final['log_sha256']==sha(RUN/'WRAPPER.log')
assert result['checker_sha256']==inv['checker_sha256']==sha(PREP/'checker_v3.py')=='f6b053dfa6552aca43817f0dc1c1bdefca295c32bdf7ddc4b01cf1b12ab71daf'
assert result['schema']=='r22-D-frozen-subset-independent-raw-review-v3'
assert result['audit_sha256']==sha(audit_path) and result['all_read_artifacts_stable']
assert not result['full_56_registered_keys_reviewed']
assert result['completion_set_frozen_at_start']==audit['completion_set_frozen_at_start'] and len(result['rows'])==28
assert {row['key'] for row in result['rows']}==set(audit['completion_set_frozen_at_start'])
assert (RUN/'review/SOURCE_BEFORE.json').read_bytes()==(RUN/'review/SOURCE_AFTER.json').read_bytes()
assert len(read(RUN/'review/SOURCE_AFTER.json'))==result['read_artifact_count']
expected={'jobs':28,'candidate_evaluation_records':11169,'candidate_ideal_STA_launches':5243,'baseline_STA_runs':28,'cache_replays':5850,'pre_STA_rejected_trial_records':76,'SEC_passes':28,'actual_STA_cache_reuse_from_launch':5821,'tested_hash_dedup_without_replay':29,'cached_pre_STA_rejection':0,'uncached_pre_STA_rejection':76}
assert result['totals']==expected,(result['totals'],expected)
manifest=read(ROOT/'experiments/20261018_r22_D_revalidate_v1/manifest.json')
jobs={job['key']:job for job in manifest['jobs']}
for key,digest in audit['completion_set_frozen_at_start'].items():assert sha(ROOT/Path(jobs[key]['output_dir'])/'completion.json')==digest
for row in result['rows']:assert row['sec_proven']>0 and row['sec_unproven']==0
for name,digest in manifest['source_pin']['files'].items():assert sha(ROOT/name)==digest
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==manifest['source_pin']['head']
paths=[audit_path,PREP/'checker_v3.py',PREP/'V3_DESIGN.md',PREP/'DIAGNOSIS.json',RUN/'INVOCATION.json',RUN/'FINAL_RECEIPT.json',RUN/'WRAPPER.log',RUN/'review/RESULT.json',RUN/'review/SOURCE_BEFORE.json',RUN/'review/SOURCE_AFTER.json']
receipt={'accepted':True,'scope':'Only immutable ROOT28 registered completion subset; all other completed or active jobs excluded. Not D56, physical RC, four-state or global scientific closure.','parent_root_audit_sha256':sha(audit_path),'completion_set':audit['completion_set_frozen_at_start'],'review_artifacts':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},'source_head':manifest['source_pin']['head'],'all45_runtime_source_current_match':True,'independent_read_artifact_count':result['read_artifact_count'],'independent_read_sources_before_after_stable':True,'root_current_completion_sha_verified':28,'root_reviewed_preexecution_checker_source_diff_and_design':True,'canonical_counts':expected,'legacy_cache_field_is_compatibility_sum_not_pure_STA_reuse':True,'full56_accepted':False,'extra_completed_at_review_start_not_accepted':result['extra_completed_at_start_not_reviewed'],'extra_completed_at_review_end_not_accepted':result['extra_completed_at_end_not_reviewed']}
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
with (BASE/'INDEPENDENT_28_ROOT_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'accepted':True,'completed_accepted':28,'counts':expected,'root_receipt_sha256':sha(BASE/'INDEPENDENT_28_ROOT_ACCEPTANCE.json')}))
