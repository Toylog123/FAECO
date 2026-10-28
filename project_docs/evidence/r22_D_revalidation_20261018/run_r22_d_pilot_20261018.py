"""Run the registered D14 pilot; preserve invocation and bounded wrapper output."""
from pathlib import Path
import sys,subprocess,json,hashlib,os,time
sys.path.insert(0,str(Path('code/scripts').resolve()))
import run_r22_d_revalidation as d

out=Path('project_docs/evidence/r22_D_revalidation_20261018')
experiment=Path('experiments/20261018_r22_D_revalidate_v1')
manifest_path=experiment/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
sha=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
assert sha=='fd336745fd6bbb3039eaf5c043f67206a5567e74116b7787e093f89592a3ff4d'
d.validate_manifest(manifest,experiment)
argv=[str(d.BASH),'code/scripts/run_with_timeout.sh','27800',sys.executable,'-u','-X','utf8','code/scripts/run_r22_d_revalidation.py','--output-dir',str(experiment),'--circuits','s27,s382']
env=os.environ.copy();env['PYTHONUTF8']='1'
pre={'argv':argv,'source_head':manifest['source_pin']['head'],'manifest_sha256':sha,'selected_circuits':['s27','s382'],
 'selected_jobs':14,'parallel_circuits':2,'per_run_timeout_s':3900,'runner_subprocess_timeout_s':3930,
 'pilot_wrapper_timeout_s':27800,'pilot_parent_timeout_s':27900,'status':'starting','no_head_or_source_changes_until_full_D56_acceptance':True}
with (out/'PILOT_INVOCATION.json').open('x',encoding='utf-8') as f:json.dump(pre,f,indent=2)
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(pre),flush=True)
started=time.monotonic()
with (out/'pilot.stdout.log').open('xb') as stdout,(out/'pilot.stderr.log').open('xb') as stderr:
    try:
        p=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr,timeout=27900)
        rc=p.returncode
    except subprocess.TimeoutExpired:rc=124
receipt={**pre,'status':'finished','returncode':rc,'runtime_s':time.monotonic()-started,
 'head_after':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'stdout_sha256':hashlib.sha256((out/'pilot.stdout.log').read_bytes()).hexdigest(),
 'stderr_sha256':hashlib.sha256((out/'pilot.stderr.log').read_bytes()).hexdigest()}
(out/'PILOT_RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt),flush=True)
assert rc==0
d.validate_manifest(manifest,experiment)
