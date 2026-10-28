"""Lifetime-bound monitor for the already running D42 batch; never launches EDA."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,json,time,hashlib,os
ROOT=Path.cwd().resolve()
BASE=ROOT/'project_docs/evidence/r22_D_revalidation_20261018'
invocation=BASE/'REMAINING_INVOCATION.json';ending=BASE/'REMAINING_RUN_RECEIPT.json'
assert invocation.exists()
out=BASE/'remaining_lifetime_monitor';out.mkdir(exist_ok=False)
argv=[sys.executable,'-X','utf8',str(ROOT/'scratch/monitor_r22_d_20261018.py')]
env=os.environ.copy();env['PYTHONUTF8']='1'
def save(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
save(out/'INVOCATION.json',{'actual_utc':datetime.now(timezone.utc).isoformat(),'monitor_argv':argv,'interval_s':60,
 'monitor_process_timeout_s':30,'batch_receipt':str(ending.relative_to(ROOT)),'watcher_max_duration_s':90300,
 'scope':'Monitor this already-running batch only; not a recurring automation, not a scientific acceptance, no EDA'})
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
started=time.monotonic();checks=[];status='monitoring'
with (out/'PROGRESS.jsonl').open('x',encoding='utf-8',buffering=1) as log:
    while time.monotonic()-started<90300:
        begin=time.monotonic();p=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,timeout=30)
        row={'actual_utc':datetime.now(timezone.utc).isoformat(),'returncode':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
        log.write(json.dumps(row)+'\n');checks.append(row)
        print(json.dumps(row),flush=True)
        if p.returncode:
            status='monitor_validation_failed';break
        if ending.exists():
            receipt=json.loads(ending.read_text(encoding='utf-8'));status='batch_receipt_observed';break
        if json.loads(p.stdout.decode('utf-8'))['failed']:
            status='batch_failure_observed';break
        time.sleep(max(0,60-(time.monotonic()-begin)))
    else:status='watcher_deadline_reached'
save(out/'FINAL_MONITOR_RECEIPT.json',{'status':status,'actual_utc':datetime.now(timezone.utc).isoformat(),
 'runtime_s':time.monotonic()-started,'checks':len(checks),'batch_receipt_present':ending.exists(),
 'batch_receipt_sha256':hashlib.sha256(ending.read_bytes()).hexdigest() if ending.exists() else None,
 'scope':'Process/source/progress monitor only, no independent scientific acceptance'})
