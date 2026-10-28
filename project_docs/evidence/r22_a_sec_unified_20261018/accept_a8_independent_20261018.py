"""Root acceptance of independently verified exact-object A8 SEC metadata."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path.cwd().resolve();sys.path.insert(0,str(ROOT/'code/scripts'))
import run_r22_d_revalidation as d
BASE=ROOT/'project_docs/evidence/r22_a_sec_unified_20261018';REVIEW=BASE/'independent_review'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
manifest=load(BASE/'manifest.json');batch=load(BASE/'RUN_RECEIPT.json')
r=load(REVIEW/'attempt1/RESULT.json');receipt=load(REVIEW/'FINAL_RECEIPT.json')
assert sha(REVIEW/'FINAL_RECEIPT.json')=='87b3b721f1c5d229b929b1cf43d70c3c097d105ba932358421c4e3df6bed184b'
assert sha(REVIEW/'attempt1/RESULT.json')=='eae2ae8201087fddcdeddc44d0f32e95c7a820e7be795d651de9b16cbdc2ec73'
for entry in receipt['artifacts']:
    p=REVIEW/entry['path'];assert sha(p)==entry['sha256']
d.validate_manifest(load(ROOT/'experiments/20261018_r22_D_revalidate_v1/manifest.json'),ROOT/'experiments/20261018_r22_D_revalidate_v1')
assert manifest['source_pin']==d.executable_pin() and r['source_HEAD']==manifest['source_pin']['head']
assert r['proof_count']==8 and r['current_runtime_sources']==45 and r['all_read_sources_stable']
assert r['manifest_sha256']==batch['manifest_sha256']==sha(BASE/'manifest.json')
assert r['actual_tool_binary_sha256']=='88c0a12bb814a1a8716b1ae10b482e35d3005ed558e1f5f626b3dc983ea3abd0'
assert batch['source_and_inputs_stable'] and batch['tool_identity_stable'] and batch['STA_runs']==0
for row,job in zip(batch['rows'],manifest['cases']):
    c=row['circuit'];assert c==job['circuit'] and row['proven']>0 and row['unproven']==0 and row['status']=='pass' and row['returncode']==0
    for role in ['baseline','accepted_final']:
        assert sha(ROOT/job[role]['path'])==job[role]['sha256']==sha(BASE/'source_snapshots'/c/(role+'.v'))
    for name,digest in row['artifact_sha256'].items():assert sha(BASE/'proofs'/c/name)==digest
out={'accepted':True,'scope':'Eight exact original A baseline/final pairs, uniform fresh Boolean SEC metadata only; no new STA/WNS or four-state result',
 'manifest_sha256':sha(BASE/'manifest.json'),'batch_receipt_sha256':sha(BASE/'RUN_RECEIPT.json'),
 'independent_final_sha256':sha(REVIEW/'FINAL_RECEIPT.json'),'independent_result_sha256':sha(REVIEW/'attempt1/RESULT.json'),
 'source_head':manifest['source_pin']['head'],'rows':[{k:row[k] for k in ['circuit','proven','unproven','runtime_s']} for row in batch['rows']],
 'paper_table_may_use_actual_current_batch_values':True,'s820_139_is_new_actual_count_not_old_137_or_paper_138':True,
 'old_A6_A2_records_preserved':True}
with (BASE/'ROOT_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(out))
