"""Two-pass bounded build; adapted from the prior metadata correction."""
import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--language',choices=['zh','en'],required=True);args=p.parse_args()
lang=args.language
source=ROOT/('paper/en/manuscript/FAECO.tex' if lang=='en' else 'paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex')
build=OUT/'build';build.mkdir(exist_ok=False);pdf=build/(source.stem+'.pdf')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=sha(source);logs=OUT/(lang+'_build_logs');logs.mkdir(exist_ok=False)
engine=shutil.which('lualatex');assert engine
env={**os.environ,'PYTHONUTF8':'1','OSFONTDIR':str(ROOT/'paper/zh/fonts')}
passes=[]
for number in (1,2):
    command=['C:/Program Files/Git/bin/bash.exe',str(ROOT/'code/scripts/run_with_timeout.sh'),'120',engine,
             '-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),source.name]
    started=time.monotonic()
    process=subprocess.run(command,cwd=source.parent,env=env,capture_output=True,timeout=150)
    (logs/f'pass{number}.stdout.bin').write_bytes(process.stdout)
    (logs/f'pass{number}.stderr.bin').write_bytes(process.stderr)
    passes.append({'pass':number,'command':command,'returncode':process.returncode,'runtime_s':time.monotonic()-started})
    print(json.dumps(passes[-1]),flush=True)
    if process.returncode:break
assert sha(source)==pin
result={'language':lang,'source_sha256':pin,'source_stable':True,'passes':passes,
        'passed':len(passes)==2 and all(p['returncode']==0 for p in passes),
        'pdf':pdf.relative_to(ROOT).as_posix(),'pdf_sha256':sha(pdf) if pdf.exists() else None}
with (OUT/(lang+'_build_receipt.json')).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False),flush=True)
raise SystemExit(0 if result['passed'] else 1)
