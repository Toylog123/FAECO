import hashlib,json,subprocess,sys,time
from pathlib import Path
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/v1')
out.mkdir(parents=True,exist_ok=False)
def sources():
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('code').rglob('*.py'))}
before=sources()
(out/'SOURCE_BEFORE.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
argv=[sys.executable,'-X','utf8','-m','pytest','code/tests','-q']
started=time.perf_counter()
with (out/'pytest.log').open('wb') as log:
    try:
        proc=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        code=proc.returncode
    except subprocess.TimeoutExpired:
        code=124
after=sources()
(out/'SOURCE_AFTER.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
receipt={'argv':argv,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'runtime_s':time.perf_counter()-started,'timeout_s':600,'returncode':code,
         'source_stable':before==after,'python_sources':len(before),
         'log_sha256':hashlib.sha256((out/'pytest.log').read_bytes()).hexdigest()}
(out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
print((out/'pytest.log').read_text(encoding='utf-8',errors='replace')[-5500:])
assert code==0 and before==after
