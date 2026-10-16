from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'project_docs/evidence/r22_b_model_audit_20261016'
sys.path.insert(0,str(folder))
import x_identity_certificate as xc
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=folder/'new_model_proofs/manifest_and_results.json'
d=json.loads(receipt.read_text(encoding='utf-8'))
assert d['status']=='completed' and d['source_stable']
assert all(sha(ROOT/n)==h for n,h in d['source_manifest'].items())
assert sha(folder/'x_identity_certificate.py')==d['x_identity_checker_sha256']
assert sha(folder/'prove_actual_pico_pairs.py')==d['script_sha256']
assert sha(folder/'audit.json')==d['audit_sha256']
rows=[]
for pair,result in zip(d['pairs'],d['results'],strict=True):
    assert pair['top_module']==result['top'] and result['result']['status']=='pass'
    case=folder/'new_model_proofs'/pair['top_module']
    raw_texts=[]
    for role,raw_name in [('gold','initial_raw.v'),('gate','final_raw.v')]:
        original=Path(pair[role+'_path'])
        assert sha(original)==pair[role+'_sha256']
        original_text=original.read_text(encoding='utf-8-sig')
        assert (case/raw_name).read_text(encoding='utf-8-sig')==original_text
        raw_texts.append(original_text)
    assert all(sha(case/name)==h for name,h in result['artifacts'].items())
    cert=xc.certify_pair(*raw_texts)
    assert cert==json.loads((case/'x_identity_certificate.json').read_text(encoding='utf-8'))
    assert cert['certified']
    rows.append(dict(top=pair['top_module'],status='pass',raw_byte_hashes_match=True,
                     full_decoded_gold_and_gate_equal=True,all_artifacts_match=True,
                     x_identity_recomputed=True,x_sources=len(cert['sources'])))
out=folder/'new_model_proofs/POST_RUN_VERIFICATION.json'
with out.open('x',encoding='utf-8') as f:
    json.dump(dict(manifest_sha256=sha(receipt),verification=rows,
        rule='Original byte hashes plus exact decoded UTF8/BOM/newline equality; no token or whitespace normalization',
        verifier_sha256=sha(Path(__file__))),f,indent=2)
print(json.dumps(rows,indent=2))
