from pathlib import Path
import sys,subprocess,os,json,hashlib,time,datetime
ROOT=Path.cwd().resolve();R=ROOT/'paper/zh/review_rounds/r23_20261018';S=Path('C:/Users/16225/.codex/skills/academic-research-skills/scripts')
kind=sys.argv[1];role=sys.argv[2] if len(sys.argv)>2 else None
if kind=='contract':
    script=S/'check_sprint_contract.py';args=[str(R/'contract.json')];name='contract'
else:
    script=S/'check_phase_conformance.py'
    args=['--contract',str(R/'contract.json'),'--role',role,'--phase1',str(R/f'seats/{role}_phase1.md'),'--manuscript',str(R/'inputs/manuscript.tex'),'--metadata',str(R/'metadata.json')]
    args+=['--phase1-only'] if kind=='phase1' else ['--phase2',str(R/f'seats/{role}_phase2.md')]
    name=f'{role}_{kind}'
out=R/'qa'/name;out.mkdir(exist_ok=False)
argv=[str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8',str(script),*args]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'argv':argv,'script_sha256':sha(script),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cwd':str(ROOT),'timeout_s':60,'review_dependencies_only':str(ROOT/'scratch/r23_review_deps')}
(out/'INVOCATION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONPATH']=str(ROOT/'scratch/r23_review_deps')
started=time.monotonic()
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
    result=subprocess.run(argv,stdout=stdout,stderr=stderr,env=env,timeout=60)
receipt={**record,'returncode':result.returncode,'runtime_s':time.monotonic()-started,'stdout_sha256':sha(out/'stdout.log'),'stderr_sha256':sha(out/'stderr.log')}
(out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'gate':name,'returncode':result.returncode,'stdout':(out/'stdout.log').read_text(encoding='utf-8'),'stderr':(out/'stderr.log').read_text(encoding='utf-8')}))
sys.exit(result.returncode)
