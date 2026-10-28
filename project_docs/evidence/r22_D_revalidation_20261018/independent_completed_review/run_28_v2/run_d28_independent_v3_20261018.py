"""Execute root-reviewed v3 only against immutable ROOT28, never producer extras."""
from pathlib import Path
import subprocess,os,json,hashlib,datetime,time
ROOT=Path.cwd().resolve();BASE=ROOT/'project_docs/evidence/r22_D_revalidation_20261018'
PREP=BASE/'ledger_duplicate_diagnosis_20261018';OUT=BASE/'independent_completed_review/run_28_v2';OUT.mkdir(exist_ok=False)
script=PREP/'checker_v3.py';audit=BASE/'ROOT_COMPLETION_AUDIT_28.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(script)=='f6b053dfa6552aca43817f0dc1c1bdefca295c32bdf7ddc4b01cf1b12ab71daf'
assert sha(audit)=='1db9b0fb778c2dfdb411d2095519479f59c6ef2cfb35ba34416f89eb8c47ab4d'
argv=['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','900',str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-u',str(script),'--audit',str(audit),'--output',str(OUT/'review')]
env=os.environ.copy();env['PYTHONUTF8']='1'
record={'argv':argv,'cwd':str(ROOT),'checker_sha256':sha(script),'parent_root_audit_sha256':sha(audit),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root_preexecution_review':{'design_sha256':sha(PREP/'V3_DESIGN.md'),'minimal_diff_sha256':sha(PREP/'checker_v2_to_v3.diff'),'diagnosis_sha256':sha(PREP/'DIAGNOSIS.json'),'approved_contract':'Frozen ROOT28 subset only; all extra completed keys excluded. Original raw STA/SEC/source checks retained; strict actual cache / identity dedup / cached rejection separation. Legacy broad cache field preserved as compatibility sum.'},'checker_independently_authored':True,'scope':'Read-only independent raw review of ROOT28; no new EDA/source/HEAD or original record changes.'}
(OUT/'INVOCATION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
started=time.monotonic()
with (OUT/'WRAPPER.log').open('xb') as log:
    p=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=930)
receipt={**record,'returncode':p.returncode,'runtime_s':time.monotonic()-started,'log_sha256':sha(OUT/'WRAPPER.log'),'checker_unchanged':sha(script)==record['checker_sha256']}
if (OUT/'review/RESULT.json').exists():receipt['result_sha256']=sha(OUT/'review/RESULT.json')
(OUT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert p.returncode==0 and receipt['checker_unchanged']
print(json.dumps(receipt))
