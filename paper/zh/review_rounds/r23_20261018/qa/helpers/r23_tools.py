from pathlib import Path
import os, sys, json, subprocess, time, hashlib, datetime
root=Path.cwd().resolve(); review=root/'paper/zh/review_rounds/r23_20261018'
skills=Path('C:/Users/16225/.codex/skills/academic-research-skills')
name,script,*args=sys.argv[1:]
out=review/'qa'/name;out.mkdir(exist_ok=False)
argv=[str(root/'.venv/Scripts/python.exe'),'-X','utf8',str(skills/'scripts'/script),*args]
env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONPATH']=str(root/'scratch/r23_review_deps')
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'cwd':str(root),'timeout_s':60,'script_sha256':hashlib.sha256(Path(argv[3]).read_bytes()).hexdigest()}
(out/'INVOCATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
started=time.monotonic()
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
    p=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr,timeout=60)
record.update(returncode=p.returncode,runtime_s=time.monotonic()-started)
(out/'RECEIPT.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'name':name,'returncode':p.returncode,'stdout':(out/'stdout.log').read_text(encoding='utf-8'),'stderr':(out/'stderr.log').read_text(encoding='utf-8')},ensure_ascii=False))
sys.exit(p.returncode)
