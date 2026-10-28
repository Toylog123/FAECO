"""Bounded progress observation only; completion observations are not acceptance."""
from pathlib import Path
import sys,json,datetime,hashlib
sys.path.insert(0,str(Path('code/scripts').resolve()))
import run_r22_d_revalidation as d

experiment=Path('experiments/20261018_r22_D_revalidate_v1')
manifest=json.loads((experiment/'manifest.json').read_text(encoding='utf-8'))
d.validate_manifest(manifest,experiment)
complete=[];active=[];failed=[];writing=[]
for j in manifest['jobs']:
    p=Path(j['output_dir'])
    if (p/'failure.json').exists():
        failed.append(j['key']);continue
    if (p/'completion.json').exists():
        try:done=json.loads((p/'completion.json').read_text(encoding='utf-8'))
        except (OSError,json.JSONDecodeError):writing.append(j['key']);continue
        if done.get('status')=='complete':complete.append(j['key'])
        continue
    if (p/'preregistered.json').exists():
        recent=max((x for x in p.rglob('*') if x.is_file()),key=lambda x:x.stat().st_mtime,default=None)
        active.append({'key':j['key'],'latest_file':None if recent is None else str(recent.relative_to(p)),
                       'latest_file_actual_utc':None if recent is None else datetime.datetime.fromtimestamp(recent.stat().st_mtime,datetime.timezone.utc).isoformat()})
now=datetime.datetime.now(datetime.timezone.utc)
out=Path('project_docs/evidence/r22_D_revalidation_20261018/monitoring');out.mkdir(exist_ok=True)
receipt={'scope':'Observed progress, not a fresh independent scientific acceptance','actual_utc':now.isoformat(),
 'source_pin_unchanged':True,'source_head':manifest['source_pin']['head'],
 'manifest_sha256':hashlib.sha256((experiment/'manifest.json').read_bytes()).hexdigest(),
 'registered_total':56,'pilot_total':14,'produced_complete':complete,'active':active,'failed':failed,'completion_writing':writing}
target=out/(now.strftime('%Y%m%dT%H%M%S_%f')+'.json')
with target.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
script=out.parent/Path(__file__).name
if not script.exists():script.write_bytes(Path(__file__).read_bytes())
else:assert script.read_bytes()==Path(__file__).read_bytes()
print(json.dumps({'receipt':str(target),'produced_complete':len(complete),'active':active,'failed':failed,'source_pin_unchanged':True}))
