from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
R=Path.cwd();B=R/'project_docs/evidence/r22_s_spef_integrated_20261018';O=B/'independent_final_review'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
before=read(B/'v5/SOURCE_BEFORE.json');after=read(B/'v5/SOURCE_AFTER.json')
assert before==after and len(before)==174
current={n:sha(R/n) for n in before}
assert current==before
assert {str(p.relative_to(R)):sha(p) for p in (R/'code').rglob('*.py')}==before
run=read(B/'v5/RUN_RECEIPT.json')
assert run['pythonutf8']=='1' and run['returncode']==0 and run['source_stable']
assert sha(B/'v5/pytest.log')==run['log_sha256']=='3f5f39fa113c8e0f0b7a15d0e63de9f0427532450f4f8cd0b0ac75b65f74bb26'
log=(B/'v5/pytest.log').read_text()
assert '1056 passed, 156 subtests passed in 208.27s' in log
assert 'warnings summary' not in log and 'SKIPPED' not in log
with zipfile.ZipFile(B/'v5/source_snapshot.zip') as z:
 assert set(z.namelist())=={n.replace('\\','/') for n in before}
 assert all(hashlib.sha256(z.read(n.replace('\\','/'))).hexdigest()==h for n,h in before.items())
C=B/'final_test_fixture_cleanup';pre=read(C/'PRE_CLEANUP.json');verification=read(C/'CLEANUP_VERIFICATION.json')
index=read(C/'INDEX_REFRESH_RECEIPT.json');moves=read(C/'MOVE_PLAN.json')
assert sha(C/'all_test_results_before_cleanup.zip')==verification['archive_sha256']
with zipfile.ZipFile(C/'all_test_results_before_cleanup.zip') as z:
 assert set(z.namelist())=={n.replace('\\','/') for n in pre['archived_files']}
 assert all(hashlib.sha256(z.read(n.replace('\\','/'))).hexdigest()==h for n,h in pre['archived_files'].items())
assert len(pre['archived_files'])==verification['archived_before_cleanup_files']==85
restored=[];prefix=Path('data/cases/minimal/iscas85_c17_case01/results')
for row in pre['tracked_restored']:
 actual=R/row['path'];head=C/'head'/Path(row['path']).relative_to(prefix);raw=actual.read_bytes()
 digest=hashlib.sha256(raw).hexdigest()
 assert digest==row['head_sha256']==sha(head) and raw==head.read_bytes()
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert blob==index['index_before'][row['path']]==index['index_after'][row['path']]
 restored.append({'path':row['path'],'raw_sha256':digest,'computed_git_blob_sha1':blob,
                  'current_bytes_match_saved_HEAD_copy':True})
assert len(restored)==verification['tracked_head_bytes_restored']==5
assert index['index_before']==index['index_after'] and index['index_refresh_only_no_blob_changes']
assert len(moves)==verification['moved_untracked_items']==6
for row in moves:assert not Path(row['source']).exists() and Path(row['destination']).exists()
for n,h in verification['moved_files'].items():assert sha(C/'generated_extras'/n)==h==pre['archived_files'][n]
assert len(verification['moved_files'])==verification['moved_files_verified']==72
paths={B/'v5'/n for n in ['SOURCE_BEFORE.json','SOURCE_AFTER.json','source_snapshot.zip','RUN_RECEIPT.json','pytest.log']}
paths|={C/n for n in ['PRE_CLEANUP.json','MOVE_PLAN.json','CLEANUP_VERIFICATION.json','INDEX_REFRESH_RECEIPT.json','all_test_results_before_cleanup.zip']}
v={'schema':'r22-stage-current-implementation-independent-acceptance-v1','client_date':'2026-10-18',
 'created_actual_utc':datetime.now(timezone.utc).isoformat(),
 'decision':'Accept current reviewed implementation and full v5 regression; historical/scientific domain gates remain open',
 'new_eda_tests_or_git_executed':False,
 'current_all_174_code_python_sources_equal_v5_before_after_zip':True,'current_python_source_sha256':current,
 'v5_actual_pytest_summary':'1056 passed, 156 subtests passed in 208.27s','v5_recorded_run':run,
 'v5_no_skip_or_warning_summary':True,'v1_v3_v4_remain_failed_history':True,
 'scope_review_sha256':sha(B/'mapped_scope_repair/independent_final_review/INDEPENDENT_REVIEW.json'),
 'all_versions_snapshot_review_sha256':sha(O/'REVIEW_V1_V5.json'),
 'cleanup_independent_checks':{'archived_zip_files_all_sha_verified':85,'tracked_restored':restored,
  'moved_items_destinations_exist_and_originals_absent':6,'moved_files_all_sha_verified':72,
  'recorded_index_before_after_equal_and_raw_blob_sha1_recomputed':True,
  'git_status_or_index_not_queried_by_this_reviewer':True,
  'producer_recorded_original_test_output_git_status_clean':verification['original_test_output_git_status_clean']},
 'accepted_implementation_scope':['S pre/post evidence separation and shared-normalizer actual input binding as exercised by current tests',
 'Mapped/source top selection and ABC status precedence in reproduced controls',
 'SPEF topology/report provenance and paired comparison within supported static/tiny-tool domain'],
 'still_open_or_not_validated':['OI048 historical affected top/proof objects still require per-object audit.',
 'OI046 b18 inout remains unsupported; proposed passive boundary support is unimplemented.',
 'OI049 partial-timeout bytes tail presentation remains a static residual and fail-closed.',
 'Four-state capability, historical B3/C/D/S/SPEF scientific restoration, RC calibration and paper/figure result replacement remain separate.',
 'A new clean committed source pin and registration are required before formal scientific EDA.'],
 'reviewed_evidence_hashes':{p.relative_to(R).as_posix():sha(p) for p in paths},
 'code_sources_rechecked_at_end':{n:sha(R/n) for n in before},'review_script_sha256':sha(Path(__file__))}
assert v['code_sources_rechecked_at_end']==current
p=O/'STAGE_CURRENT_IMPLEMENTATION_ACCEPTANCE.json'
with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
with (O/'accept_current_stage.py').open('xb') as f:f.write(Path(__file__).read_bytes())
print('acceptance_sha',sha(p),'v1_v5_review_sha',sha(O/'REVIEW_V1_V5.json'),'cleanup_verified85_5_6_72',True)
