from pathlib import Path
import hashlib,json,subprocess,os,sys,time
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/tool_checks_v3')
out.mkdir(exist_ok=False)
paths=['code/tests/test_convert_itc99_blif_to_v.py','code/tests/test_run_equivalence_sweep_sh.py','code/tests/test_yosys_abc_flow.py']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('code').rglob('*.py')}
env=os.environ.copy()
extra=[r'C:\Program Files\Git\bin',r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib']
env['PATH']=';'.join(extra+[env.get('PATH','')])
argv=[sys.executable,'-X','utf8','-m','pytest',*paths,'-q','-ra']
started=time.perf_counter()
with (out/'pytest.log').open('wb') as log:
    try:
        code=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
    except subprocess.TimeoutExpired:code=124
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('code').rglob('*.py')}
receipt={'scope':'Supplementary checks with existing native tools exposed only to child PATH; not a new scientific campaign',
    'argv':argv,'path_prefix':extra,'returncode':code,'runtime_s':time.perf_counter()-started,
    'timeout_s':300,'source_stable':before==after,'sources':before,
    'log_sha256':hashlib.sha256((out/'pytest.log').read_bytes()).hexdigest()}
(out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='sources'}))
print((out/'pytest.log').read_text(encoding='utf-8',errors='replace')[-7000:])
assert code==0 and before==after
