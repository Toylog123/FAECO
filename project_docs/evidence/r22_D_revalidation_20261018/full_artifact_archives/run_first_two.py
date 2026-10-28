"""Bounded archive orchestration only; no EDA or Git commands."""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, subprocess, sys, time

ROOT=Path.cwd().resolve()
OUT=ROOT/'project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

def archive(c):
    argv=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','900',sys.executable,'-X','utf8','-u',str(OUT/'archive_d_cases.py'),'--circuit',c,'--output-dir',str(OUT/c),'--audit',str(OUT.parent/'ROOT_COMPLETION_AUDIT_14.json')]
    pre={'argv':argv,'cwd':str(ROOT),'actual_utc':datetime.now(timezone.utc).isoformat(),'client_date':'2026-10-18','archiver_sha256':sha(OUT/'archive_d_cases.py'),'stdout_stderr_log':str(OUT/(c+'_WRAPPER.log')),'parent_timeout_s':930}
    save(OUT/(c+'_INVOCATION.json'),pre)
    started=time.monotonic()
    with (OUT/(c+'_WRAPPER.log')).open('xb') as log:
        proc=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,timeout=930)
    result={**pre,'returncode':proc.returncode,'runtime_s':time.monotonic()-started,'wrapper_log_sha256':sha(OUT/(c+'_WRAPPER.log'))}
    if (OUT/c/'receipt.json').is_file():result['producer_receipt_sha256']=sha(OUT/c/'receipt.json')
    save(OUT/(c+'_RUN_RECEIPT.json'),result)
    print(c,'archive wrapper rc',proc.returncode,'seconds',result['runtime_s'],flush=True)
    assert proc.returncode==0,c
    return result

if __name__=='__main__':
    save(OUT/'BATCH_INVOCATION.json',{'argv':sys.argv,'cwd':str(ROOT),'script_sha256':sha(Path(__file__)),'max_parallel_archives':2,'each_7z_threads':2,'no_EDA':True,'client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat()})
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(archive,c) for c in ['s27','s382']]
        while any(not f.done() for f in futures):
            for c in ['s27','s382']:
                p=OUT/(c+'_WRAPPER.log')
                if p.exists():
                    lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines()
                    print('[monitor]',c,p.stat().st_size,'bytes',lines[-1] if lines else '',flush=True)
            time.sleep(10)
        results=[f.result() for f in futures]
    save(OUT/'FIRST_TWO_RUN_RECEIPT.json',{'client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),'archive_count':2,'results':results,'no_EDA':True})
