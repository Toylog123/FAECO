import hashlib,json,subprocess,sys,time,zipfile,os
from pathlib import Path
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/v5')
out.mkdir(parents=True,exist_ok=False)
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
def sources():
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('code').rglob('*.py'))}
before=sources()
(out/'SOURCE_BEFORE.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'source_snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:
    for path in before: archive.write(path,path.replace(chr(92),'/'))
argv=[sys.executable,'-X','utf8','-m','pytest','code/tests','-q','-ra']
env=os.environ.copy()
env['PYTHONUTF8']='1'
extra=[r'C:\Program Files\Git\bin',r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib']
env['PATH']=';'.join(extra+[env.get('PATH','')])
started=time.perf_counter()
with (out/'pytest.log').open('wb') as log:
    try:
        proc=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        code=proc.returncode
    except subprocess.TimeoutExpired:
        code=124
after=sources()
(out/'SOURCE_AFTER.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
receipt={'argv':argv,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'path_prefix':extra,'pythonutf8':env['PYTHONUTF8'],'runtime_s':time.perf_counter()-started,'timeout_s':600,'returncode':code,
         'source_stable':before==after,'python_sources':len(before),
         'log_sha256':hashlib.sha256((out/'pytest.log').read_bytes()).hexdigest()}
(out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
print((out/'pytest.log').read_text(encoding='utf-8',errors='replace')[-5500:])
assert code==0 and before==after
