"""Prepare reversible cleanup after all native QA has stopped (do not run early)."""
from pathlib import Path
import json,hashlib,subprocess,zipfile

root=Path.cwd().resolve()
prefix='data/cases/minimal/iscas85_c17_case01/results/'
base=root/prefix
out=root/'project_docs/evidence/r22_s_spef_integrated_20261018/final_test_fixture_cleanup'
out.mkdir(exist_ok=False)
files=sorted(p for p in base.rglob('*') if p.is_file())
before={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(out/'all_test_results_before_cleanup.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(base).as_posix())
after={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert before==after
with zipfile.ZipFile(out/'all_test_results_before_cleanup.zip') as z:
    for p in files:assert hashlib.sha256(z.read(p.relative_to(base).as_posix())).hexdigest()==before[str(p.relative_to(base))]
changed=[p.decode('utf-8') for p in subprocess.check_output(['git','diff','--name-only','-z','--',prefix]).split(b'\0') if p]
restored=[]
for name in changed:
    assert name.startswith(prefix)
    data=subprocess.check_output(['git','show','HEAD:'+name])
    target=out/'head'/Path(name).relative_to(prefix)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    Path(name).write_bytes(data)
    assert Path(name).read_bytes()==data
    restored.append({'path':name,'head_sha256':hashlib.sha256(data).hexdigest()})
extras=[p.decode('utf-8').rstrip('/') for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','--directory','-z','--',prefix]).split(b'\0') if p]
plan=[]
for name in extras:
    src=(root/name).resolve()
    assert src.is_relative_to(base) and src!=base
    assert not subprocess.check_output(['git','ls-files','-z','--',name])
    dest=out/'generated_extras'/src.relative_to(base)
    assert dest.is_relative_to(out)
    plan.append({'source':str(src),'destination':str(dest),'relative':str(src.relative_to(base))})
(out/'MOVE_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'PRE_CLEANUP.json').write_text(json.dumps({'scope':'Native QA generated outputs; not scientific results','archived_files':before,'tracked_restored':restored,'untracked_move_plan':plan},ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'archived_files':len(files),'tracked_restored':len(restored),'untracked_move_items':len(plan)}))
