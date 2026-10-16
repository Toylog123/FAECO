from pathlib import Path
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
checker=ROOT/'project_docs/evidence/r22_b_model_audit_20261016/x_identity_certificate.py'
spec=importlib.util.spec_from_file_location('certificate',checker)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
pairs=json.loads((ROOT/'project_docs/evidence/r22_b_model_audit_20261016/audit.json').read_text(encoding='utf-8'))['proof_pairs']
result={'checker_sha256':hashlib.sha256(checker.read_bytes()).hexdigest(),'eda_executed':False,'pairs':[]}
for pair in pairs:
    raw={side:Path(pair[side+'_path']).read_bytes() for side in ('gold','gate')}
    cert=mod.certify_pair(raw['gold'].decode('utf-8'),raw['gate'].decode('utf-8'))
    entry={'top_module':pair['top_module'],'inputs':{side:{'path':pair[side+'_path'],'sha256':hashlib.sha256(raw[side]).hexdigest()} for side in raw},'certificate':cert}
    result['pairs'].append(entry)
    print(pair['top_module'],cert['certified'],cert['reason'],len(cert['sources']))
(ROOT/'scratch/r22_tristate_20261016/x_certificate_actual.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert all(row['certificate']['certified'] for row in result['pairs'])
