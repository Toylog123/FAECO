import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'project_docs/evidence/r22_correctness_20261016'
receipt=json.loads((out/'full_regression_v8.json').read_text(encoding='utf-8'))
exact=json.loads((out/'SEQUENTIAL_GATE_VERIFICATION_V3.json').read_text(encoding='utf-8'))
current={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted((root/'code').rglob('*.py')) if '__pycache__' not in p.parts}
assert receipt['returncode']==0 and receipt['source_stable']
assert receipt['before_sha256']==receipt['after_sha256']==current
assert exact['passed'] and exact['source_stable'] and exact['parsed_cell_counts']==[1,1]
assert all(current.get(p)==h for p,h in exact['source_manifest'].items() if p.endswith('.py'))
assert exact['reset_to_set_status']=='fail' and exact['legal_same_family_G_status']=='pass'
assert not exact['sequential_R_candidates']
suites=ET.parse(out/'full_regression_v8.xml').getroot()
assert sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in suites)==0
result={'full_regression_source_files':len(current),'current_sources_match_v8':True,
        'exact_v3_source_binding':True,'xml_failures_and_errors':0,
        'skipped':sum(int(s.get('skipped',0)) for s in suites),
        'regression_sha256':hashlib.sha256((out/'full_regression_v8.json').read_bytes()).hexdigest(),
        'exact_sha256':hashlib.sha256((out/'SEQUENTIAL_GATE_VERIFICATION_V3.json').read_bytes()).hexdigest(),
        'scope':'Current code hashes and original counterexample binding; no EDA or performance claim'}
with (out/'V8_POST_RUN_VERIFICATION.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
