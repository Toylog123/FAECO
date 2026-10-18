"""Independent read-only checks of retained regression/proof artifacts."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse,hashlib,json,re,zipfile

R=Path.cwd();B=R/'project_docs/evidence/r22_s_spef_integrated_20261018'
p=argparse.ArgumentParser();p.add_argument('--stages',required=True);p.add_argument('--output',required=True);args=p.parse_args()
O=B/'independent_final_review';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def norm(name):return name.replace('\\','/')
stages=args.stages.split(',')
native=[B/'native_top_counterexample',B/'native_top_counterexample_post']
sources={q for s in stages for q in (B/s).iterdir() if q.is_file()}
sources|={q for d in native for q in d.rglob('*') if q.is_file()}
sources.add(B/'NATIVE_TOOL_IDENTITIES.json')
before={q.relative_to(R).as_posix():{'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(sources)}
audits=[];source_versions={}
for stage in stages:
 d=B/stage
 assert (d/'RUN_RECEIPT.json').is_file(),stage+' still running / no final receipt'
 a={norm(n):h for n,h in read(d/'SOURCE_BEFORE.json').items()}
 z={norm(n):h for n,h in read(d/'SOURCE_AFTER.json').items()}
 assert a==z,stage+' source before/after drift'
 run=read(d/'RUN_RECEIPT.json');log=(d/'pytest.log').read_text(encoding='utf-8',errors='replace')
 assert sha(d/'pytest.log')==run['log_sha256'],stage+' log binding'
 assert run['source_stable'] is True and run['python_sources']==len(a)
 with zipfile.ZipFile(d/'source_snapshot.zip') as archive:
  names=archive.namelist()
  assert len(names)==len(set(names)) and set(names)==set(a),stage+' ZIP member set'
  assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
  members=[{'path':n,'sha256':hashlib.sha256(archive.read(n)).hexdigest(),'bytes':archive.getinfo(n).file_size} for n in names]
  assert all(x['sha256']==a[x['path']] for x in members),stage+' ZIP member bytes'
 source_versions[stage]=a
 summaries=[line for line in log.splitlines() if re.search(r'\d+ passed',line)]
 failures=[line for line in log.splitlines() if line.startswith('FAILED ')]
 assert (run['returncode']==0)==(not failures),stage+' returncode/failure list relation'
 audits.append({'stage':stage,'run_receipt_sha256':sha(d/'RUN_RECEIPT.json'),
  'source_before_sha256':sha(d/'SOURCE_BEFORE.json'),'source_after_sha256':sha(d/'SOURCE_AFTER.json'),
  'source_count':len(a),'source_before_after_equal':True,'snapshot_zip_sha256':sha(d/'source_snapshot.zip'),
  'snapshot_member_set_and_all_sha_match':True,'snapshot_members':members,
  'log_sha256':sha(d/'pytest.log'),'log_hash_matches_run_receipt':True,'returncode':run['returncode'],
  'runtime_s':run['runtime_s'],'pytest_summary':summaries[-1],'failed_tests':failures,
  'classification':'passed regression at its own frozen source' if run['returncode']==0 else 'preserved failed regression at its own frozen source',
  'all_artifacts_retained_unchanged':True})
native_rows=[]
for index,d in enumerate(native):
 result=read(d/'RESULT.json');proof=result['result'];log=R/proof['log_path'];raw=log.read_text(encoding='utf-8')
 assert raw.startswith('command: '+proof['command']+'\n')
 for n,h in result['source_sha256'].items():
  if n.endswith('yosys_abc.py'):continue
  assert sha(R/n)==h,n
 normalization=[]
 for q in sorted(d.rglob('receipt.json')):
  rec=read(q)
  if rec.get('schema')!='normalization-input-binding-v1':continue
  assert not rec['input_drift'] and rec['process_launched'] and rec['returned_returncode']==0
  for phase in ['inputs_before','inputs_after']:
   for role,row in rec[phase].items():
    snap=q.parent/row['snapshot'];assert sha(snap)==row['sha256'] and snap.stat().st_size==row['bytes']
  for name,row in rec['artifacts'].items():
   artifact=q.parent/name;assert sha(artifact)==row['sha256'] and artifact.stat().st_size==row['bytes']
  normalized=Path(rec['canonical_output']);assert sha(normalized)==sha(q.parent/'normalized_output.blif')
  normalization.append({'receipt_path':q.relative_to(R).as_posix(),'sha256':sha(q),'selected_top':rec.get('selected_top_module'),
                        'input_and_artifact_hashes_match':True,'command':rec['command']})
 models={}
 for side in ['original','revised']:
  t=(d/'proof'/f'{side}.normalized.blif').read_text(encoding='utf-8')
  models[side]=re.findall(r'^\.model\s+(\S+)',t,re.M)
 source_sha=next(h for n,h in result['source_sha256'].items() if n.endswith('yosys_abc.py'))
 locations=[s for s,m in source_versions.items() if m.get('code/src/rseco/yosys_abc.py')==source_sha]
 if not locations:
  for q in (B/'top_scope_repair').glob('*.py'):
   if sha(q)==source_sha:locations.append(q.relative_to(R).as_posix())
 assert locations,'Native source SHA lacks inspected source snapshot'
 native_rows.append({'folder':d.name,'result_json_sha256':sha(d/'RESULT.json'),'status':proof['status'],
  'solver_returncode':proof['returncode'],'abc_log_sha256':sha(log),'command_matches_abc_log':True,
  'original_sha256':sha(d/'original.v'),'revised_sha256':sha(d/'revised.v'),
  'normalization_receipts':normalization,'normalized_models':models,
  'source_yosys_abc_sha256':source_sha,'matching_source_snapshot_locations':locations,
  'actual_log_root_module_warning':'design has 2 root-level modules' in raw,
  'actual_log_equivalent':'Networks are equivalent' in raw,'actual_log_not_equivalent':'Networks are NOT EQUIVALENT' in raw,
  'actual_log_solver_witness':re.findall(r'^INPUT:.*|^Verification failed.*|^Output Y:.*',raw,re.M),
  'manual_semantic_witness_in_result':result['semantic_counterexample']})
assert native_rows[0]['original_sha256']==native_rows[1]['original_sha256']
assert native_rows[0]['revised_sha256']==native_rows[1]['revised_sha256']
assert native_rows[0]['status']=='pass' and native_rows[0]['actual_log_equivalent'] and native_rows[0]['actual_log_root_module_warning']
assert native_rows[1]['status']=='fail' and native_rows[1]['actual_log_not_equivalent'] and not native_rows[1]['actual_log_root_module_warning']
assert native_rows[0]['normalized_models']['original']==['sky130_fd_sc_hd__buf_1','ztop']
assert native_rows[1]['normalized_models']['original']==['ztop']
assert len(native_rows[1]['normalization_receipts'])==2 and all(x['selected_top']=='ztop' for x in native_rows[1]['normalization_receipts'])
tool_rows=[]
for row in read(B/'NATIVE_TOOL_IDENTITIES.json')['tools']:
 q=Path(row['argv'][0]);assert q.is_file() and sha(q)==row['binary_sha256']
 tool_rows.append({'path':str(q),'sha256':sha(q),'matches_recorded_identity':True,'new_process_executed':False})
after={q.relative_to(R).as_posix():{'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(sources)}
assert before==after,'Read-only evidence source drift'
v={'schema':'r22-s-spef-integrated-independent-evidence-review-v1','client_date':'2026-10-18','created_actual_utc':datetime.now(timezone.utc).isoformat(),
 'reviewer_did_not_modify_source_or_original_evidence':True,'new_eda_or_test_or_git_commands_executed':False,
 'inspected_stages':stages,'stage_audits':audits,'native_counterexample':native_rows,
 'native_input_pairs_exactly_identical':True,'current_tool_binaries_hash_match_identity_receipt':tool_rows,
 'source_before':before,'source_after':after,'evidence_bytes_stable_during_review':True,
 'v4_status_at_review':'not included; no completion claim' if 'v4' not in stages else next(x['classification'] for x in audits if x['stage']=='v4'),
 'coverage_limits':['Only retained evidence and snapshot integrity were independently checked; no solver/test execution was repeated.',
  'Failed v1/v3 are preserved as failed; a pass at a different source does not retroactively validate them.',
  'Native counterexample is a tiny combinational top-scope falsification control, not paper evidence or a general sequential/XZ proof.',
  'RESULT manual witness A=0/B=1 is distinct from the actual ABC log witness A=1/B=0; both distinguish Y=A from Y=B.',
  'OI046 b18 inout support, scientific S/SPEF campaign, manuscript/figure results and frozen-source registration are not validated by this artifact QA.'],
 'review_script_sha256':sha(Path(__file__))}
target=O/args.output
with target.open('x',encoding='utf-8') as stream:json.dump(v,stream,indent=2);stream.write('\n')
print(json.dumps({'receipt_path':target.relative_to(R).as_posix(),'receipt_sha256':sha(target),
 'stages':[{'stage':x['stage'],'source_count':x['source_count'],'returncode':x['returncode'],'summary':x['pytest_summary']} for x in audits],
 'native_input_pairs_exactly_identical':True,'native_old_pass_new_fail_logs_match':True,'reviewed_files':len(before),'source_stable':True},indent=2))
