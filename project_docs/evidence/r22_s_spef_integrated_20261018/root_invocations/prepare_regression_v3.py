from pathlib import Path
import shutil
v2=Path('scratch/run_r22_integrated_regression_v2_20261018.py')
shutil.copyfile(v2,Path('project_docs/evidence/r22_s_spef_integrated_20261018/v2')/v2.name)
text=v2.read_text(encoding='utf-8').replace('20261018/v2','20261018/v3')
text=text.replace('import hashlib,json,subprocess,sys,time,zipfile','import hashlib,json,subprocess,sys,time,zipfile,os')
text=text.replace('started=time.perf_counter()',"env=os.environ.copy()\nextra=[r'C:\\Program Files\\Git\\bin',r'C:\\oss-cad-suite-build\\oss-cad-suite\\bin',r'C:\\oss-cad-suite-build\\oss-cad-suite\\lib']\nenv['PATH']=';'.join(extra+[env.get('PATH','')])\nstarted=time.perf_counter()")
text=text.replace('subprocess.run(argv,stdout=log','subprocess.run(argv,env=env,stdout=log')
text=text.replace("'runtime_s':time.perf_counter()-started", "'path_prefix':extra,'runtime_s':time.perf_counter()-started")
Path('scratch/run_r22_integrated_regression_v3_20261018.py').write_text(text,encoding='utf-8')
print('v3 all-test native-tool environment harness ready')
