"""Reuse the accepted root archive postchecker; only the new s420 case."""
from pathlib import Path
import json,hashlib,subprocess,os,time,datetime
ROOT=Path.cwd().resolve();BASE=ROOT/'project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives'
CHECKER=BASE/'root_post_d_archives_20261018.py';CASE=BASE/'s420'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert read(CASE/'receipt.json')['status']=='verified'
assert sha(CHECKER)==read(BASE/'s27/ROOT_POST_VERIFICATION.json')['checker_sha256']
assert read(BASE.parent/'INDEPENDENT_28_ROOT_ACCEPTANCE.json')['accepted'] is True
argv=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','300',str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-u',str(CHECKER),'s420']
record={'argv':argv,'cwd':str(ROOT),'checker_sha256':sha(CHECKER),'producer_receipt_sha256':sha(CASE/'receipt.json'),'root28_acceptance_sha256':sha(BASE.parent/'INDEPENDENT_28_ROOT_ACCEPTANCE.json'),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wrapper_timeout_s':300,'parent_timeout_s':330,'no_new_EDA':True}
with (BASE/'ROOT_POST_S420_INVOCATION.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
env=os.environ.copy();env['PYTHONUTF8']='1';started=time.monotonic()
with (BASE/'ROOT_POST_S420.log').open('xb') as log:
    p=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=330)
result={**record,'returncode':p.returncode,'runtime_s':time.monotonic()-started,'log_sha256':sha(BASE/'ROOT_POST_S420.log')}
assert sha(CASE/'receipt.json')==record['producer_receipt_sha256']
if (CASE/'ROOT_POST_VERIFICATION.json').exists():result['post_result_sha256']=sha(CASE/'ROOT_POST_VERIFICATION.json')
with (BASE/'ROOT_POST_S420_RUN_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
assert p.returncode==0
print(json.dumps(result))
