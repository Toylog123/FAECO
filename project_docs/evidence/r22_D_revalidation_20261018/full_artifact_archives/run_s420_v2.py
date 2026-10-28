"""Single authorized s420 archive; no EDA, tests, source mutation or Git."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,time

ROOT=Path.cwd().resolve()
OUT=ROOT/'project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

if __name__=='__main__':
    script=OUT/'archive_d_cases_v2.py';acceptance=OUT.parent/'INDEPENDENT_28_ROOT_ACCEPTANCE.json';audit=OUT.parent/'ROOT_COMPLETION_AUDIT_28.json'
    assert sha(script)=='b60cc3f1f4e7dfbb0db884b21b4b0faa55b7909260d70b9aa28ecbda42c40b3f'
    assert sha(acceptance)=='f14c33061c3824deaa6d6018779d1d53cf6a24aba2b33d0a23d2162b6bfd00dd'
    assert not (OUT/'s420').exists()
    argv=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','900',sys.executable,'-X','utf8','-u',str(script),'--circuit','s420','--output-dir',str(OUT/'s420'),'--audit',str(audit),'--acceptance',str(acceptance)]
    pre={'argv':argv,'cwd':str(ROOT),'client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),'archiver_sha256':sha(script),'acceptance_sha256':sha(acceptance),'root_audit_sha256':sha(audit),'runner_sha256':sha(Path(__file__)),'wrapper_timeout_s':900,'parent_timeout_s':930,'authorized_case_only':'s420','raw_log':str(OUT/'s420_V2_WRAPPER.log')}
    save(OUT/'s420_V2_INVOCATION.json',pre)
    started=time.monotonic()
    with (OUT/'s420_V2_WRAPPER.log').open('xb')as log:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        while process.poll() is None:
            if time.monotonic()-started>=930:
                process.kill();process.wait(timeout=15);raise TimeoutError('archive parent timeout; preserve all original outputs')
            log_path=OUT/'s420_V2_WRAPPER.log'
            lines=log_path.read_text(encoding='utf-8-sig',errors='replace').splitlines()
            print('[monitor]',round(time.monotonic()-started,1),'s',log_path.stat().st_size,'bytes',lines[-1]if lines else '',flush=True)
            time.sleep(10)
    result={**pre,'returncode':process.returncode,'runtime_s':time.monotonic()-started,'wrapper_log_sha256':sha(OUT/'s420_V2_WRAPPER.log')}
    if (OUT/'s420/receipt.json').is_file():result['producer_receipt_sha256']=sha(OUT/'s420/receipt.json')
    save(OUT/'s420_V2_RUN_RECEIPT.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    assert process.returncode==0
