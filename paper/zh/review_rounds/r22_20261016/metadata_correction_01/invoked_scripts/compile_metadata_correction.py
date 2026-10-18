import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--language',choices=['zh','en'],required=True);a=p.parse_args()
lang=a.language
base=R/'paper/zh/review_rounds/r22_20261016/metadata_correction_01'
source=R/('paper/en/manuscript/FAECO.tex' if lang=='en' else 'paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex')
build=R/'paper'/lang/'build'
pdf=build/(source.stem+'.pdf')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source)
if pdf.is_file():
    target=base/(lang+'_before.pdf')
    if target.exists():raise RuntimeError('Previous PDF backup already exists')
    shutil.copyfile(pdf,target)
logs=base/(lang+'_build_logs');logs.mkdir(exist_ok=False)
engine=shutil.which('lualatex');assert engine
env={**os.environ,'PYTHONUTF8':'1','OSFONTDIR':str(R/'paper/zh/fonts')}
results=[]
for index in (1,2):
    command=['C:/Program Files/Git/bin/bash.exe',str(R/'code/scripts/run_with_timeout.sh'),'120',engine,
             '-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),source.name]
    t=time.monotonic()
    process=subprocess.run(command,cwd=source.parent,env=env,capture_output=True,timeout=150)
    (logs/('pass%d.stdout.bin'%index)).write_bytes(process.stdout)
    (logs/('pass%d.stderr.bin'%index)).write_bytes(process.stderr)
    results.append({'pass':index,'command':command,'returncode':process.returncode,'runtime_s':time.monotonic()-t})
    if process.returncode:break
assert sha(source)==source_sha
report={'language':lang,'source_sha256':source_sha,'source_stable':True,'passes':results,
        'passed':len(results)==2 and all(x['returncode']==0 for x in results),
        'pdf':str(pdf.relative_to(R)),'pdf_sha256':sha(pdf) if pdf.exists() else None}
with (base/(lang+'_build_receipt.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
raise SystemExit(0 if report['passed'] else 1)
