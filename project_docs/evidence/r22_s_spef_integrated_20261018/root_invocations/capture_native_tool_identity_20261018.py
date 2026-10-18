from pathlib import Path
import os,subprocess,json,hashlib
env=os.environ.copy()
prefix=[r'C:\Program Files\Git\bin',r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib']
env['PATH']=';'.join(prefix+[env.get('PATH','')])
commands=[[r'C:\oss-cad-suite-build\oss-cad-suite\bin\yosys.exe','-V'],[r'C:\oss-cad-suite-build\oss-cad-suite\bin\yosys-abc.exe','-c','version'],[r'C:\Program Files\Git\bin\bash.exe','--version']]
rows=[]
for argv in commands:
    proc=subprocess.run(argv,env=env,capture_output=True,timeout=30)
    rows.append({'argv':argv,'returncode':proc.returncode,'stdout':proc.stdout.decode('utf-8',errors='replace'),
                 'stderr':proc.stderr.decode('utf-8',errors='replace'),'binary_sha256':hashlib.sha256(Path(argv[0]).read_bytes()).hexdigest()})
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/NATIVE_TOOL_IDENTITIES.json')
with out.open('x',encoding='utf-8') as f:json.dump({'path_prefix':prefix,'tools':rows},f,indent=2)
print(json.dumps(rows))
assert all(r['returncode']==0 for r in rows)
