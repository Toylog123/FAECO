"""Execute existing independently authored raw checker; no EDA or source edits."""
from pathlib import Path
import subprocess,os,json,hashlib,datetime,time
ROOT=Path.cwd().resolve();BASE=ROOT/'project_docs/evidence/r22_D_revalidation_20261018'
OUT=BASE/'independent_completed_review/run_28_v1';OUT.mkdir(exist_ok=False)
script=BASE/'independent_completed_review/checker_v2.py';audit=BASE/'ROOT_COMPLETION_AUDIT_28.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(script)=='59e51ed56d72fafc3b2dd611bf62028e4491991d6d07ca8bebc4b31ddd9e4250'
argv=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','900',str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-u',str(script),'--audit',str(audit),'--output',str(OUT/'review')]
env=os.environ.copy();env['PYTHONUTF8']='1'
record={'argv':argv,'cwd':str(ROOT),'checker_sha256':sha(script),'parent_root_audit_sha256':sha(audit),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker_independently_authored':True,'scope':'Only frozen D28; existing checker rejects any stale completion set at start; no new EDA.'}
(OUT/'INVOCATION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
started=time.monotonic()
with (OUT/'WRAPPER.log').open('xb') as log:
    p=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=930)
receipt={**record,'returncode':p.returncode,'runtime_s':time.monotonic()-started,'log_sha256':sha(OUT/'WRAPPER.log')}
if (OUT/'review/RESULT.json').exists():receipt['result_sha256']=sha(OUT/'review/RESULT.json')
(OUT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert p.returncode==0
print(json.dumps(receipt))
