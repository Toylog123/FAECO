from pathlib import Path
import json,hashlib,subprocess,sys,time,os

expected='f761ee1996a83fc4f0f3de0999b74d85a8237858'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==expected
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','code']).strip()
out=Path('project_docs/evidence/r22_D_revalidation_20261018')
out.mkdir(exist_ok=False)
experiment=Path('experiments/20261018_r22_D_revalidate_v1')
assert not experiment.exists()
argv=[sys.executable,'-X','utf8','code/scripts/run_r22_d_revalidation.py','--output-dir',str(experiment),'--circuits','s27,s382','--dry-run']
env=os.environ.copy();env['PYTHONUTF8']='1'
start=time.monotonic();p=subprocess.run(argv,capture_output=True,env=env,timeout=120)
(out/'registration.stdout.log').write_bytes(p.stdout);(out/'registration.stderr.log').write_bytes(p.stderr)
assert p.returncode==0,p.stderr.decode('utf-8',errors='replace')
manifest=experiment/'manifest.json';m=json.loads(manifest.read_text(encoding='utf-8'))
assert m['source_pin']['head']==expected and m['source_pin']['source_tree_clean']
assert len(m['jobs'])==56 and m['parallel_circuits']==2
selected=[x['key'] for x in m['jobs'] if x['circuit'] in ['s27','s382']]
assert len(selected)==14
assert m['eda_executed_at_registration'] is False
for name,sha in m['source_pin']['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
receipt={'argv':argv,'returncode':p.returncode,'runtime_s':time.monotonic()-start,'source_commit':expected,
 'source_tree_clean':True,'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'manifest':str(manifest),
 'registered_jobs':len(m['jobs']),'pilot_jobs':selected,'parallel_circuits':2,'eda_executed':False,
 'scope':'Fresh same-family D56 registration at clean corrected source pin; D14 pilot selected before remaining D42'}
(out/'REGISTRATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(receipt))
