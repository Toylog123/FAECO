from pathlib import Path
import subprocess,json,time,datetime,hashlib
r=Path('paper/zh/review_rounds/r23_20261018');out=r/'qa/record_checks';out.mkdir(exist_ok=False)
commands=[('git_diff_check_default',['git','diff','--check']),('git_diff_check_crlf',['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--check']),('record_check',['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','30','bash','code/scripts/check_record.sh'])]
receipts=[]
for name,argv in commands:
 start=time.monotonic();p=subprocess.run(argv,capture_output=True,timeout=45)
 (out/f'{name}.stdout.log').write_bytes(p.stdout);(out/f'{name}.stderr.log').write_bytes(p.stderr)
 row={'name':name,'argv':argv,'returncode':p.returncode,'runtime_s':time.monotonic()-start};receipts.append(row)
 print(json.dumps({**row,'stdout':p.stdout.decode('utf-8',errors='replace')[:500],'stderr':p.stderr.decode('utf-8',errors='replace')[:300]},ensure_ascii=False))
authored=[]
for p in [r/'REVIEW_REPORT.md',r/'REVISION_ROADMAP.md']:
 bad=[n for n,l in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if l.rstrip(' \t')!=l]
 authored.append({'path':p.name,'trailing_space_lines':bad,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':receipts,'authored_reports':authored,'scope':'Default diff --check retains existing CRLF-as-whitespace warnings in pre-review source/English diagnostics; no source changes to erase them. cr-at-eol-aware check evaluates actual whitespace without mutating files. Record checker is daily-entry presence only, not semantic audit.'}
(out/'RECEIPT.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
