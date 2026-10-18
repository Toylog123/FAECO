from pathlib import Path
import shutil

base=Path('project_docs/evidence/r22_s_spef_integrated_20261018')
v4=Path('scratch/run_r22_integrated_regression_v4_20261018.py')
shutil.copyfile(v4,base/'v4'/v4.name)
text=v4.read_text(encoding='utf-8').replace('20261018/v4','20261018/v5')
text=text.replace('env=os.environ.copy()',"env=os.environ.copy()\nenv['PYTHONUTF8']='1'")
text=text.replace("'path_prefix':extra,", "'path_prefix':extra,'pythonutf8':env['PYTHONUTF8'],")
text=text.replace("out.mkdir(parents=True,exist_ok=False)","out.mkdir(parents=True,exist_ok=False)\n(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())")
Path('scratch/run_r22_integrated_regression_v5_20261018.py').write_text(text,encoding='utf-8')
print('Prepared v5, not yet executed; explicit inherited UTF8 and exact harness snapshot')
