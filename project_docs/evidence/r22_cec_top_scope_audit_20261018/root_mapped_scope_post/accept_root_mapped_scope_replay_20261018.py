from pathlib import Path
import json,hashlib

base=Path('project_docs/evidence/r22_cec_top_scope_audit_20261018')
old=base/'fix_independent_review_v2';out=base/'root_mapped_scope_post'
r=json.loads((out/'PROBE_RESULT.json').read_text())
assert r['source_stable'] and r['source_before']==r['source_after']
for path,sha in r['source_after'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha
files=['original.v','single_inverter.blif','dummy_first_then_inverter.blif']
same={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in files}
for name in files:assert (old/name).read_bytes()==(out/name).read_bytes()
statuses={x['case']:x['result']['status'] for x in r['native_cases']}
assert statuses=={'single_inverter':'fail','dummy_first_then_inverter':'error'}
assert 'NOT EQUIVALENT' in (out/'single_inverter/abc_cec.log').read_text(encoding='utf-8')
assert 'unique BLIF root' in (out/'dummy_first_then_inverter/abc_cec.log').read_text(encoding='utf-8')
script=Path('scratch/root_mapped_scope_replay_20261018.py')
original_script=(old/'probe_source.py').read_text(encoding='utf-8')
assert script.read_text(encoding='utf-8')==original_script.replace("fix_independent_review_v2';OUT.mkdir","root_mapped_scope_post';OUT.mkdir")
(out/'probe_source.py').write_bytes(script.read_bytes())
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
receipt={'scope':'Root independent re-execution of original mapped-boundary falsifier; only output directory changed',
 'same_inputs_sha256':same,'statuses':statuses,'source_current_matches_probe_before_after':True,
 'original_probe_sha256':hashlib.sha256((old/'probe_source.py').read_bytes()).hexdigest(),
 'replay_script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
 'artifacts':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}}
(out/'ROOT_ACCEPTANCE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='artifacts'}))
