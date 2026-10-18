"""Bounded read-only review; no solver, pytest, or Git invocation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,ast
R=Path.cwd();B=R/'project_docs/evidence/r22_s_spef_integrated_20261018/mapped_scope_repair'
O=B/'independent_final_review';O.mkdir(exist_ok=False)
ROOTPOST=R/'project_docs/evidence/r22_cec_top_scope_audit_20261018/root_mapped_scope_post'
OLD=R/'project_docs/evidence/r22_cec_top_scope_audit_20261018/fix_independent_review_v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ident(p):return {'sha256':sha(p),'bytes':Path(p).stat().st_size}
final=read(B/'FINAL_RECEIPT.json')
assert sha(B/'FINAL_RECEIPT.json')=='cd5361e2b378a5760b0accf20b2d61df3bb65d406abaafbd8c9f3402970fd5cf'
paths={B/n for n in final['artifacts']}
paths|={B/'FINAL_RECEIPT.json'}
paths|={p for d in [ROOTPOST,OLD] for p in d.rglob('*') if p.is_file()}
paths|={R/n for n in final['source_frozen']}
before={p.relative_to(R).as_posix():ident(p) for p in paths}
for name,digest in final['artifacts'].items():assert sha(B/name)==digest,name
for name,digest in final['source_frozen'].items():
 assert sha(R/name)==digest,name
 assert sha(B/('frozen_'+Path(name).name))==digest,name
native=read(B/'native_post/RESULT.json')
assert native['source_before']==native['source_after']==final['source_frozen']
assert native['source_stable']
expected={'single_identity':'pass','single_inverter':'fail','dummy_then_inverter':'error',
          'inverter_then_dummy':'error','explicit_ztop':'fail','explicit_missing':'error','reachable_helper_first':'pass'}
assert len(native['cases'])==7
def models(p):return re.findall(r'^\.model\s+(\S+)',Path(p).read_text(),re.M)
def normalizations(folder):
 checked=[]
 for p in sorted(folder.rglob('receipt.json')):
  x=read(p)
  if x.get('schema')!='normalization-input-binding-v1':continue
  for phase in ['inputs_before','inputs_after']:
   for role,row in x[phase].items():
    q=p.parent/row['snapshot'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
  for name,row in x['artifacts'].items():
   q=p.parent/name;assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
  assert 'original_source' in x['inputs_before'],str(p)
  assert (p.parent/'normalize.log').read_text().startswith('command: '+' '.join(x['command'])+'\n')
  if x['returned_returncode']==0:
   assert x['input_drift']==[] and x['process_launched'] is True
   top=x['selected_top_module'];assert 'hierarchy -check -top '+top in x['command'][-1]
   assert models(p.parent/'normalized_output.blif')==[top]
   assert sha(Path(x['canonical_output']))==sha(p.parent/'normalized_output.blif')
  checked.append({'path':p.relative_to(R).as_posix(),'sha256':sha(p),'input_format':x['input_format'],
      'selected_top':x['selected_top_module'],'returncode':x['returned_returncode'],
      'process_launched':x['process_launched'],'original_source_sha256':x['inputs_before']['original_source']['sha256'],
      'all_snapshot_and_artifact_sha_match':True})
 return checked
norms=normalizations(B/'native_post')+normalizations(ROOTPOST)
cases=[]
for row in native['cases']:
 name=row['case'];want=expected[name];out=row['result'];assert row['expected']==want and out['status']==want
 assert sha(B/'native_post'/(name+'.blif'))==row['input_sha256']
 log=Path(out['log_path']).read_text()
 if want in ['pass','fail']:
  assert out['returncode']==0 and 'cec ' in log
  assert ('Networks are equivalent' in log) if want=='pass' else ('Networks are NOT EQUIVALENT' in log)
  assert not re.search(r'[2-9]\s+root-level modules',log)
  assert models(out['normalized_original'])==['ztop'] and models(out['normalized_revised'])==['ztop']
 else:
  assert out['returncode']!=0 and 'ValueError' in log
  assert 'unique BLIF root' in log or 'not a BLIF model' in log
 cases.append({'case':name,'expected_status':want,'actual_status':out['status'],'input_sha256':row['input_sha256'],
               'actual_result_log_correspondence':True,'log_sha256':sha(out['log_path'])})
base=native['baseline'];assert base['status']=='success' and base['verification_status']=='pass'
assert 'Networks are equivalent' in Path(base['verification_log_path']).read_text()
assert Path(base['output_netlist']).is_file()
backcheck=B/'native_post/baseline/abc_rewrite_refactor_resyn.normalized.blif'
assert models(backcheck)==['ztop']
zero=(B/'native_post/native_input_error.stdout.log').read_text()
assert 'Cannot open input file' in zero and native['native_zero_rc_input_error']['returncode']==0
assert native['native_zero_rc_input_error']['with_appended_success_status']=='error'
old=read(OLD/'PROBE_RESULT.json');post=read(ROOTPOST/'PROBE_RESULT.json')
assert post['source_before']==post['source_after'] and post['source_stable']
for name,digest in post['source_before'].items():assert sha(R/name)==digest
assert (OLD/'original.v').read_bytes()==(ROOTPOST/'original.v').read_bytes()
comparisons=[]
for a,z in zip(old['native_cases'],post['native_cases']):
 name=a['case'];assert name==z['case']
 assert (OLD/(name+'.blif')).read_bytes()==(ROOTPOST/(name+'.blif')).read_bytes()
 assert sha(ROOTPOST/(name+'.blif'))==z['mapped_file_sha256']
 if name=='single_inverter':
  assert a['result']['status']==z['result']['status']=='fail'
  assert 'Networks are NOT EQUIVALENT' in Path(z['result']['log_path']).read_text()
 else:
  assert a['result']['status']=='pass' and z['result']['status']=='error'
  assert 'root-level modules' in Path(a['result']['log_path']).read_text()
  assert 'unique BLIF root' in Path(z['result']['log_path']).read_text()
 comparisons.append({'case':name,'source_and_mapped_bytes_equal_old_new':True,'old_status':a['result']['status'],
  'new_status':z['result']['status'],'old_log_sha256':sha(a['result']['log_path']),'new_log_sha256':sha(z['result']['log_path'])})
red=(B/'RED_SOURCE_WINDOW.log').read_text();green=(B/'GREEN_V3.log').read_text()
assert 'before_top_selection[False]' in red and 'before_top_selection[True]' in red and '2 failed, 19 deselected' in red
assert '47 passed, 1 skipped in 4.64s' in green and 'code/tests/test_cec_blif_scope.py' in green.splitlines()[0]
source=(R/'code/src/rseco/yosys_abc.py').read_text();tree=ast.parse(source)
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
normal=ast.get_source_segment(source,functions['_normalize_to_blif'])
assert normal.index('snapshot_before("original_source", netlist_path)')<normal.index('_prepare_yosys_input(netlist_path')
assert normal.index('_prepare_yosys_input(netlist_path')<normal.index('select_blif_top_module(source_text')
mapped=ast.get_source_segment(source,functions['check_mapped_blif_equivalence'])
assert 'top_module=mapped_top_module' in mapped and 'mapped_blif, revised_blif' in mapped
baseline=ast.get_source_segment(source,functions['run_yosys_abc_resynthesis_baseline'])
assert '_normalize_to_blif(' in baseline and 'optimized_blif,' in baseline and 'normalized_optimized' in baseline
after={p.relative_to(R).as_posix():ident(p) for p in paths};assert before==after
v={'schema':'oi048-final-independent-code-evidence-review-v1','client_date':'2026-10-18','created_actual_utc':datetime.now(timezone.utc).isoformat(),
 'decision':'Reproduced mapped-root/status/source-selection defects accepted as repaired within reviewed scope; full v5 pending',
 'no_new_source_test_git_or_eda_operations':True,'producer_final_receipt_sha256':sha(B/'FINAL_RECEIPT.json'),
 'producer_artifacts_independently_rehashed':len(final['artifacts']),'producer_artifacts_all_match':True,
 'source_frozen_and_current_match':final['source_frozen'],'source_stability':True,
 'native_seven_cases':cases,'baseline_backcheck':{'status':base['status'],'verification_status':base['verification_status'],
  'raw_output_preserved':True,'normalized_backcheck_top':'ztop','cec_log_sha256':sha(base['verification_log_path'])},
 'zero_rc_native_input_error_log_sha256':sha(B/'native_post/native_input_error.stdout.log'),
 'normalization_receipts':norms,'root_independent_replay_comparisons':comparisons,
 'source_window_controls':{'ordinary_and_BOM_red_observed':True,'red_log_sha256':sha(B/'RED_SOURCE_WINDOW.log'),
  'final_adjacent_log_sha256':sha(B/'GREEN_V3.log'),'green_summary':'47 passed, 1 skipped in 4.64s',
  'final_test_source_contains_both_cases':True,'static_original_source_binding_precedes_prepare_and_top_inference':True,
  'note':'This reviewer checked retained test source/logs and code order, not a new execution or separately retained window-test runtime directories.'},
 'reviewed_before':before,'reviewed_after':after,'original_evidence_stable':True,
 'coverage_limits':['No new native solver or pytest execution by this reviewer.','v5 currently running and is not declared passed here.',
  'No historical full-host proof, four-state/inout/physical scientific effect established.',
  'Explicit mapped_top_module is an explicit caller proof scope; it is not an inferred correspondence to another model.'],
 'nonblocking_out_of_scope_static_observation':{'file':'code/src/rseco/yosys_abc.py','function':'_tail',
  'detail':'Direct string join of bytes splitlines may TypeError when mapped CEC timeout output is bytes. This is fail-closed presentation behavior, predates the mapped-scope repair, and was reported to main without adding probe or changing scope.'},
 'review_script_sha256':sha(Path(__file__))}
p=O/'INDEPENDENT_REVIEW.json'
with p.open('x',encoding='utf-8') as stream:json.dump(v,stream,indent=2);stream.write('\n')
with (O/'review_script.py').open('xb') as stream:stream.write(Path(__file__).read_bytes())
print(json.dumps({'receipt_sha256':sha(p),'producer_artifact_count':len(final['artifacts']),'checked_normalization_receipts':len(norms),
 'reviewed_files':len(before),'source_and_original_evidence_stable':True,'v5':'pending'},indent=2))
