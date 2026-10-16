import hashlib,json,subprocess,time,sys,os
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
evidence=root/'project_docs/evidence/r22_correctness_20261016'
evidence.mkdir(parents=True,exist_ok=True)
label=sys.argv[1] if len(sys.argv)>1 else 'full_regression'
def hashes():
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root/'code').rglob('*.py')) if '__pycache__' not in p.parts}
before=hashes()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
cmd=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','300',
     '.venv/Scripts/python.exe','-X','utf8','-m','pytest','code/tests','-q',
     '--junitxml=project_docs/evidence/r22_correctness_20261016/'+label+'.xml']
record={'start_utc':datetime.now(timezone.utc).isoformat(),'head_before_commit':head,
        'command':cmd,'before_sha256':before,'status':'running','environment_overrides':{'PYTHONUTF8':'1'}}
receipt=evidence/(label+'.json')
if receipt.exists():
    raise RuntimeError('Refusing to overwrite an existing regression evidence bundle')
receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
start=time.monotonic()
with (evidence/(label+'.log')).open('w',encoding='utf-8') as log:
    try:
        result=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=330,env={**os.environ,'PYTHONUTF8':'1'})
        rc=result.returncode
    except subprocess.TimeoutExpired:
        rc=124
after=hashes()
record.update(returncode=rc,runtime_s=time.monotonic()-start,after_sha256=after,
              source_stable=before==after,status='completed',end_utc=datetime.now(timezone.utc).isoformat())
receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['returncode','runtime_s','source_stable']},indent=2),flush=True)
print((evidence/(label+'.log')).read_text(encoding='utf-8')[-2500:],flush=True)
raise SystemExit(rc if before==after else 125)
