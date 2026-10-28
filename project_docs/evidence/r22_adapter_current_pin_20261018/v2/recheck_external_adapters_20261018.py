"""Bounded current-pin adapter QA; scientific STA/SEC boundaries are mocked."""
from pathlib import Path
import sys, subprocess, os, json, hashlib, time

ROOT=Path.cwd()
OUT=ROOT/'project_docs/evidence/r22_adapter_current_pin_20261018/v2'
OUT.mkdir(exist_ok=False)
B3=ROOT/'project_docs/evidence/r22_b_model_audit_20261016/B3_RECONSTRUCTION_ADAPTER'
C=ROOT/'project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER'
BASH='C:/Program Files/Git/bin/bash.exe'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    paths=set((ROOT/'code').rglob('*.py'))
    paths.update(p for base in (B3,C) for p in base.rglob('*') if p.is_file() and p.suffix in {'.py','.json','.md'} and '__pycache__' not in p.parts)
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)

head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert head=='f761ee1996a83fc4f0f3de0999b74d85a8237858'
assert not subprocess.check_output(['git','status','--porcelain','--','code'],text=True).strip()
before=snapshot();save('SOURCE_BEFORE.json',before)
env=os.environ.copy();env['PYTHONUTF8']='1'
cases=[('B3',[str(B3/'test_adapter.py')]),('C',[str(C/'test_adapter.py'),str(C/'test_register_run.py')])]
calls=[]
for name,files in cases:
    argv=[BASH,'code/scripts/run_with_timeout.sh','300',sys.executable,'-X','utf8','-m','pytest','-q',*files,'--basetemp',str(OUT/('pytest_tmp_'+name))]
    calls.append({'name':name,'argv':argv,'timeout_s':330})
save('INVOCATION.json',{'head':head,'PYTHONUTF8':'1','calls':calls,'scope':'Current-source bounded mocked adapter QA, not scientific EDA or historical identity recovery'})
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
receipts=[]
for call in calls:
    start=time.monotonic()
    with (OUT/(call['name']+'.stdout.log')).open('xb') as out,(OUT/(call['name']+'.stderr.log')).open('xb') as err:
        try:rc=subprocess.run(call['argv'],env=env,stdout=out,stderr=err,timeout=call['timeout_s']).returncode
        except subprocess.TimeoutExpired:rc=124
    receipts.append({**call,'returncode':rc,'runtime_s':time.monotonic()-start,'stdout_sha256':digest(OUT/(call['name']+'.stdout.log')),'stderr_sha256':digest(OUT/(call['name']+'.stderr.log'))})
after=snapshot();save('SOURCE_AFTER.json',after)
head_after=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
clean=not subprocess.check_output(['git','status','--porcelain','--','code'],text=True).strip()
result={'head':head,'head_after':head_after,'sources_stable':before==after,'source_count':len(before),'code_clean_after':clean,'cases':receipts,'all_returncodes_zero':all(x['returncode']==0 for x in receipts)}
save('RUN_RECEIPT.json',result);print(json.dumps(result),flush=True)
assert before==after and head==head_after and clean and result['all_returncodes_zero']
