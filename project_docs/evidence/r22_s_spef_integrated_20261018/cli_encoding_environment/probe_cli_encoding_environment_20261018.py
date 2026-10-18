from pathlib import Path
import os,json,runpy,subprocess,sys,hashlib

out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/cli_encoding_environment')
out.mkdir(exist_ok=False)
test=Path('code/tests/test_compare_0a_equivalence.py')
script=Path('code/scripts/compare_0a_equivalence.py')
product=runpy.run_path(str(test))['_product']()
fixture=out/'路径包含中文.json'
fixture.write_text(json.dumps(product),encoding='utf-8')
rows=[]
for setting in [None,'1']:
    env=os.environ.copy()
    env.pop('PYTHONUTF8',None)
    env.pop('PYTHONIOENCODING',None)
    if setting is not None:env['PYTHONUTF8']=setting
    argv=[sys.executable,str(script),'--reference',str(fixture),'--candidate',str(fixture)]
    p=subprocess.run(argv,env=env,capture_output=True,timeout=30)
    name='default' if setting is None else 'utf8'
    (out/(name+'.stdout.bin')).write_bytes(p.stdout)
    (out/(name+'.stderr.bin')).write_bytes(p.stderr)
    try:
        text=p.stdout.decode('utf-8')
        decoded=True
    except UnicodeDecodeError:
        decoded=False
        text=None
    rows.append({'pythonutf8':setting,'argv':argv,'returncode':p.returncode,
                 'stdout_utf8_decodable':decoded,'pass_marker':None if text is None else 'full gate (E1-E6)     : PASS' in text,
                 'stdout_sha256':hashlib.sha256(p.stdout).hexdigest()})
assert rows[0]['returncode']==rows[1]['returncode']==0
assert not rows[0]['stdout_utf8_decodable'] and rows[1]['stdout_utf8_decodable'] and rows[1]['pass_marker']
env=os.environ.copy();env['PYTHONUTF8']='1'
with (out/'targeted_pytest.log').open('wb') as log:
    p=subprocess.run([sys.executable,'-X','utf8','-m','pytest','code/tests/test_compare_0a_equivalence.py','code/tests/test_compare_equivalence_sweep.py','-q','-ra'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
receipt={'scope':'Execution environment attribution only; no production change','probes':rows,'targeted_returncode':p.returncode,
         'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [test,script,Path('code/tests/test_compare_equivalence_sweep.py'),Path('code/scripts/compare_equivalence_sweep.py')]}}
(out/'RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(rows));print((out/'targeted_pytest.log').read_text(encoding='utf-8'))
assert p.returncode==0
