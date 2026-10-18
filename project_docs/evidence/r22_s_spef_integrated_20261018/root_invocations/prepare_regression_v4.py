from pathlib import Path
import shutil

base=Path('project_docs/evidence/r22_s_spef_integrated_20261018')
v3=Path('scratch/run_r22_integrated_regression_v3_20261018.py')
shutil.copyfile(v3,base/'v3'/v3.name)
v4=Path('scratch/run_r22_integrated_regression_v4_20261018.py')
v4.write_text(v3.read_text(encoding='utf-8').replace('20261018/v3','20261018/v4'),encoding='utf-8')
print(v4)
