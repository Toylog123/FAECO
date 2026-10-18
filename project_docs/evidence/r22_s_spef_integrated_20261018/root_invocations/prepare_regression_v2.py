from pathlib import Path
import shutil
p=Path('scratch/run_r22_integrated_regression_20261018.py')
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/v1')
shutil.copyfile(p,out/p.name)
text=p.read_text(encoding='utf-8')
text=text.replace('import hashlib,json,subprocess,sys,time','import hashlib,json,subprocess,sys,time,zipfile')
text=text.replace('20261018/v1','20261018/v2').replace("'code/tests','-q'","'code/tests','-q','-ra'")
text=text.replace('argv=[sys.executable', "with zipfile.ZipFile(out/'source_snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:\n    for path in before: archive.write(path,path.replace(chr(92),'/'))\nargv=[sys.executable")
Path('scratch/run_r22_integrated_regression_v2_20261018.py').write_text(text,encoding='utf-8')
print('v2 harness prepared, not executed')
