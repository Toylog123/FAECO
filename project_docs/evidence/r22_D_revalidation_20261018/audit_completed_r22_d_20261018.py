"""Read-only replay of completion validation, frozen at audit start; no EDA."""
from pathlib import Path
import sys,json,hashlib,time
sys.path.insert(0,str(Path('code/scripts').resolve()))
import run_r22_d_revalidation as d

experiment=Path('experiments/20261018_r22_D_revalidate_v1')
manifest=json.loads((experiment/'manifest.json').read_text(encoding='utf-8'))
d.validate_manifest(manifest,experiment)
jobs=[j for j in manifest['jobs'] if (Path(j['output_dir'])/'completion.json').exists()]
assert jobs
out=Path('project_docs/evidence/r22_D_revalidation_20261018')/f'ROOT_COMPLETION_AUDIT_{len(jobs):02d}.json'
assert not out.exists()
frozen={j['key']:hashlib.sha256((Path(j['output_dir'])/'completion.json').read_bytes()).hexdigest() for j in jobs}
started=time.monotonic();rows=[]
for job in jobs:
    done=d.execute_run(job,experiment,manifest)  # Existing complete branch only.
    p=Path(job['output_dir'])/'completion.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==frozen[job['key']]
    a=done['accounting']
    rows.append({'key':job['key'],'baseline_wns':done['baseline_wns'],'final_wns':done['final_wns'],
                 'sec_status':done['sec_status'],'sec_returncode':done['sec_returncode'],
                 'n_candidate_evaluation_records':a['n_candidate_evaluation_records'],
                 'n_new_candidate_sta_runs':a['n_new_sta_runs'],'n_cache_replays':a['n_cache_replays'],
                 'completion_sha256':frozen[job['key']]})
d.validate_manifest(manifest,experiment)
receipt={'scope':'Root read-only completion replay; not independent from implementation author; no new STA/SEC',
 'manifest_sha256':hashlib.sha256((experiment/'manifest.json').read_bytes()).hexdigest(),
 'source_pin':manifest['source_pin'],'completion_set_frozen_at_start':frozen,
 'verified_completed':len(jobs),'matrix_registered':56,'all_frozen_completed_verified':True,
 'runtime_s':time.monotonic()-started,'jobs':rows,
 'running_or_not_started_jobs_not_counted_as_complete':True}
with out.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
target=out.parent/Path(__file__).name
if target.exists():assert target.read_bytes()==Path(__file__).read_bytes()
else:target.write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in receipt.items() if k not in ['source_pin','completion_set_frozen_at_start']}))
