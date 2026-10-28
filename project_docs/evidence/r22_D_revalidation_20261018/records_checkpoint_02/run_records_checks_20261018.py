from pathlib import Path
import concurrent.futures,subprocess,json,time,hashlib,datetime
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
BASH='C:/Program Files/Git/bin/bash.exe'
commands={
 'check_record':[BASH,'code/scripts/run_with_timeout.sh','30',BASH,'code/scripts/check_record.sh'],
 'semantic_whitespace':[BASH,'code/scripts/run_with_timeout.sh','30','git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--ignore-space-at-eol','--check','--','.',':(exclude)project_docs/evidence/**',':(exclude)data/**']}
head_before=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
def run(item):
 name,argv=item;start=time.monotonic();r=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40)
 (OUT/(name+'.stdout.bin')).write_bytes(r.stdout);(OUT/(name+'.stderr.bin')).write_bytes(r.stderr)
 return name,{'argv':argv,'returncode':r.returncode,'runtime_s':time.monotonic()-start,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'stdout_text':r.stdout.decode('utf-8',errors='replace'),'stderr_text':r.stderr.decode('utf-8',errors='replace')}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:rows=dict(ex.map(run,commands.items()))
head_after=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
j={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Records and semantic whitespace QA only; no EDA/tests, no stage/commit/source or HEAD mutation','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cwd':str(ROOT),'HEAD_before':head_before,'HEAD_after':head_after,'HEAD_stable':head_before==head_after,'commands':rows,'all_returncodes_zero':all(x['returncode']==0 for x in rows.values())}
(OUT/'RECEIPT.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
print(json.dumps({'all_returncodes_zero':j['all_returncodes_zero'],'HEAD_stable':j['HEAD_stable'],'checks':{k:{'returncode':v['returncode'],'runtime_s':v['runtime_s'],'stdout_text':v['stdout_text'],'stderr_text':v['stderr_text']} for k,v in rows.items()}},ensure_ascii=False))
