"""Preserve test-generated tracked c17 outputs before restoring fixture bytes."""
from pathlib import Path
import subprocess, hashlib, json

prefix='data/cases/minimal/iscas85_c17_case01/results/'
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/test_output_restore')
out.mkdir(exist_ok=False)
paths=[p.decode('utf-8') for p in subprocess.check_output(
    ['git','diff','--name-only','-z','--',prefix]).split(b'\0') if p]
rows=[]
for name in paths:
    assert name.startswith(prefix)
    rel=Path(name).relative_to(prefix)
    current=Path(name).read_bytes()
    head=subprocess.check_output(['git','show','HEAD:'+name])
    for folder,data in [('generated',current),('head',head)]:
        target=out/folder/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    rows.append({'path':name,'generated_sha256':hashlib.sha256(current).hexdigest(),
                 'head_sha256':hashlib.sha256(head).hexdigest()})
(out/'BEFORE.json').write_text(json.dumps({'scope':'Native QA-generated fixture outputs, not scientific results','files':rows},indent=2),encoding='utf-8')
if paths:
    subprocess.run(['git','restore','--source=HEAD','--worktree','--',*paths],check=True)
for row in rows:
    assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['head_sha256']
(out/'RESTORE_RECEIPT.json').write_text(json.dumps({'restored_count':len(rows),'all_head_bytes_restored':True,'files':rows},indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(f'Preserved and restored {len(rows)} generated tracked fixture outputs')
