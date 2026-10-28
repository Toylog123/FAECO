from pathlib import Path
import sys,subprocess,shutil,os,time,json,hashlib,datetime
root=Path.cwd();r=root/'paper/zh/review_rounds/r27_20261019';name=sys.argv[1];out=r/name;out.mkdir(exist_ok=False)
src=root/'paper/zh/manuscript'/sys.argv[2];build=root/'paper/zh/build';pdf=build/(src.stem+'.pdf');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=sha(src)
engine=shutil.which('lualatex');assert engine
env={**os.environ,'PYTHONUTF8':'1','OSFONTDIR':str(root/'paper/zh/fonts')};passes=[]
for n in (1,2):
 argv=['C:/Program Files/Git/bin/bash.exe',str(root/'code/scripts/run_with_timeout.sh'),'150',engine,'-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),src.name]
 start=time.monotonic();p=subprocess.run(argv,cwd=src.parent,env=env,capture_output=True,timeout=180)
 (out/f'pass{n}.stdout.log').write_bytes(p.stdout);(out/f'pass{n}.stderr.log').write_bytes(p.stderr)
 row={'pass':n,'argv':argv,'returncode':p.returncode,'runtime_s':time.monotonic()-start};passes.append(row);print(json.dumps(row),flush=True)
 if p.returncode:break
if pdf.with_suffix('.log').exists():(out/'compile.log').write_bytes(pdf.with_suffix('.log').read_bytes())
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':pin,'source_unchanged':sha(src)==pin,'passes':passes,'passed':len(passes)==2 and all(x['returncode']==0 for x in passes),'pdf_sha256':sha(pdf) if pdf.exists() else None}
(out/'BUILD_RECEIPT.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(receipt),flush=True);sys.exit(0 if receipt['passed'] else 1)
