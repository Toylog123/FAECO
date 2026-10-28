"""Run only the 42 remaining preregistered D jobs after two pilot acceptance gates."""
from pathlib import Path
import sys,subprocess,json,hashlib,os,time
sys.path.insert(0,str(Path('code/scripts').resolve()))
import run_r22_d_revalidation as d

out=Path('project_docs/evidence/r22_D_revalidation_20261018')
experiment=Path('experiments/20261018_r22_D_revalidate_v1')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path=experiment/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
assert digest(manifest_path)=='fd336745fd6bbb3039eaf5c043f67206a5567e74116b7787e093f89592a3ff4d'
pilot=json.loads((out/'PILOT_RUN_RECEIPT.json').read_text(encoding='utf-8'))
audit_path=out/'ROOT_COMPLETION_AUDIT_14.json'
audit=json.loads(audit_path.read_text(encoding='utf-8'))
assert pilot['returncode']==0 and pilot['selected_jobs']==14
assert audit['verified_completed']==14 and audit['all_frozen_completed_verified'] is True
pilot_jobs={j['key'] for j in manifest['jobs'] if j['circuit'] in {'s27','s382'}}
assert set(audit['completion_set_frozen_at_start'])==pilot_jobs
for job in manifest['jobs']:
    if job['key'] in pilot_jobs:
        assert digest(Path(job['output_dir'])/'completion.json')==audit['completion_set_frozen_at_start'][job['key']]
# The independent review is passed as its immutable final receipt plus a root
# acceptance note containing the independently reviewed completion set.
independent_path=out/'INDEPENDENT_PILOT_ROOT_ACCEPTANCE.json'
independent=json.loads(independent_path.read_text(encoding='utf-8'))
assert independent['accepted'] is True
assert independent['completion_set']==audit['completion_set_frozen_at_start']
for name,expected in independent['review_artifacts'].items():assert digest(Path(name))==expected
d.validate_manifest(manifest,experiment)
circuits=['s420','s641','s713','s820','s832','s953']
assert len([j for j in manifest['jobs'] if j['circuit'] in circuits])==42
argv=[str(d.BASH),'code/scripts/run_with_timeout.sh','90000',sys.executable,'-u','-X','utf8','code/scripts/run_r22_d_revalidation.py','--output-dir',str(experiment),'--circuits',','.join(circuits)]
env=os.environ.copy();env['PYTHONUTF8']='1'
pre={'argv':argv,'source_head':manifest['source_pin']['head'],'manifest_sha256':digest(manifest_path),
 'selected_circuits':circuits,'selected_jobs':42,'parallel_circuits':2,'per_run_timeout_s':3900,'runner_subprocess_timeout_s':3930,
 'remaining_wrapper_timeout_s':90000,'remaining_parent_timeout_s':90100,'status':'starting',
 'pilot_run_receipt_sha256':digest(out/'PILOT_RUN_RECEIPT.json'),'pilot_root_audit_sha256':digest(audit_path),
 'independent_pilot_root_acceptance_sha256':digest(independent_path),'no_head_or_source_changes_until_full_D56_acceptance':True}
with (out/'REMAINING_INVOCATION.json').open('x',encoding='utf-8') as f:json.dump(pre,f,indent=2)
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
with (out/'PILOT_BATCH_SUMMARY_ORIGINAL.json').open('xb') as f:f.write((experiment/'batch_summary.json').read_bytes())
print(json.dumps(pre),flush=True)
started=time.monotonic()
with (out/'remaining.stdout.log').open('xb') as stdout,(out/'remaining.stderr.log').open('xb') as stderr:
    try:rc=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr,timeout=90100).returncode
    except subprocess.TimeoutExpired:rc=124
receipt={**pre,'status':'finished','returncode':rc,'runtime_s':time.monotonic()-started,
 'head_after':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'stdout_sha256':digest(out/'remaining.stdout.log'),'stderr_sha256':digest(out/'remaining.stderr.log')}
with (out/'REMAINING_RUN_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt),flush=True)
assert rc==0
d.validate_manifest(manifest,experiment)
