"""Root accepts independently audited pilot artifacts; no scientific execution."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path('code/scripts').resolve()))
import run_r22_d_revalidation as d
base=Path('project_docs/evidence/r22_D_revalidation_20261018')
review=base/'independent_pilot_review'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
receipt=load(review/'FINAL_RECEIPT.json')
result=load(review/'attempt1/RESULT.json')
root=load(base/'ROOT_COMPLETION_AUDIT_14.json')
manifest=load('experiments/20261018_r22_D_revalidate_v1/manifest.json')
d.validate_manifest(manifest,Path('experiments/20261018_r22_D_revalidate_v1'))
assert digest(review/'FINAL_RECEIPT.json')=='b3c6c8d55dde787cf6bf3d76429576636f90aa36b75654b43f5d4cfcd0f3d50b'
assert digest(review/'attempt1/RESULT.json')=='27efaf79ed685fbf02d752d093538c47bd9322381d7fd3c1759bcd6ea2079497'
assert result['completion_set_frozen_at_start']==root['completion_set_frozen_at_start']
assert result['all_read_artifacts_stable'] is True and result['source_files_current_matched']==45
assert result['source_HEAD']==manifest['source_pin']['head'] and result['manifest_sha256']==digest('experiments/20261018_r22_D_revalidate_v1/manifest.json')
assert result['totals']=={'jobs':14,'candidate_evaluation_records':2471,'candidate_ideal_STA_launches':1369,'baseline_STA_runs':14,'cache_replays':1102,'pre_STA_rejected_trial_records':0,'SEC_passes':14}
assert len(result['rows'])==14 and all(row['sec_proven']>0 and row['sec_unproven']==0 for row in result['rows'])
for job in manifest['jobs']:
    if job['key'] in root['completion_set_frozen_at_start']:
        assert digest(Path(job['output_dir'])/'completion.json')==root['completion_set_frozen_at_start'][job['key']]
artifacts={p.as_posix():digest(p) for p in [review/'FINAL_RECEIPT.json',review/'REPORT.md',review/'checker_v1.py',review/'INVOCATION_V1.json',review/'RUN_V1.log',review/'attempt1/RESULT.json',review/'attempt1/SOURCE_BEFORE.json',review/'attempt1/SOURCE_AFTER.json']}
out={'accepted':True,'scope':'Root acceptance of independent D14 raw-artifact audit only; no extrapolation to D56 or new STA/SEC',
 'completion_set':root['completion_set_frozen_at_start'],'review_artifacts':artifacts,'totals':result['totals'],
 'source_pin_current_matches':True,'parent_root_audit_sha256':digest(base/'ROOT_COMPLETION_AUDIT_14.json')}
with (base/'INDEPENDENT_PILOT_ROOT_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
(base/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'accepted':True,'jobs':14,'receipt':str(base/'INDEPENDENT_PILOT_ROOT_ACCEPTANCE.json'),'totals':result['totals']}))
