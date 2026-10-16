"""Reprove the two explicitly bound accepted Pico netlists with current models."""
from pathlib import Path
import importlib.util
import json,hashlib,subprocess,sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'code/src'))
spec=importlib.util.spec_from_file_location('pico_prover',ROOT/'code/scripts/run_r22_cut_ablation.py')
batch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

def main():
    folder=Path(__file__).resolve().parent
    audit_path=folder/'audit.json'
    audit=json.loads(audit_path.read_text(encoding='utf-8'))
    output=folder/'new_model_proofs'
    if output.exists():
        raise RuntimeError('Do not overwrite existing proof evidence')
    if subprocess.check_output(['git','status','--porcelain','--','code'],cwd=ROOT,text=True).strip():
        raise RuntimeError('Freeze/commit production and tests before execution')
    source=batch.source_manifest()
    audit_sha=batch.sha(audit_path)
    lib_sha=batch.sha(batch.LIB)
    pairs=[]
    for pair in audit['proof_pairs']:
        item=dict(pair)
        for role in ['gold','gate']:
            path=Path(pair[role+'_path']).resolve()
            if not path.is_relative_to(ROOT):
                raise RuntimeError('Proof input outside project')
            if batch.sha(path)!=pair[role+'_sha256']:
                raise RuntimeError('Registered raw '+role+' changed')
        state_path=Path(pair['actual_final_state_source'])
        state=json.loads(state_path.read_text(encoding='utf-8'))['state']
        actual=state['current_netlist_text']
        text=Path(pair['gate_path']).read_text(encoding='utf-8-sig')
        if text!=actual:
            raise RuntimeError('Candidate no longer equals actual committed state')
        text_hash=hashlib.sha256(actual.encode('utf-8')).hexdigest()
        if any(text_hash!=pair[name] for name in ['actual_final_state_utf8_lf_sha256',
                   'accepted_patch_candidate_hash','accepted_patch_netlist_hash','current_netlist_hash']):
            raise RuntimeError('Accepted patch and actual state hash mismatch')
        item['state_file_sha256']=batch.sha(state_path)
        pairs.append(item)
    output.mkdir()
    receipt={'status':'registered','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'source_manifest':source,'script_sha256':batch.sha(Path(__file__)),
             'audit_sha256':audit_sha,'liberty_sha256':lib_sha,'pairs':pairs,'results':[]}
    target=output/'manifest_and_results.json'
    batch.save(target,receipt)
    for pair in pairs:
        if batch.source_manifest()!=source or batch.sha(audit_path)!=audit_sha or batch.sha(batch.LIB)!=lib_sha:
            raise RuntimeError('Proof source or audit drift')
        for role in ['gold','gate']:
            if batch.sha(Path(pair[role+'_path']))!=pair[role+'_sha256']:
                raise RuntimeError('Raw proof object drift')
        if batch.sha(Path(pair['actual_final_state_source']))!=pair['state_file_sha256']:
            raise RuntimeError('Accepted state receipt drift')
        initial=Path(pair['gold_path']).read_text(encoding='utf-8-sig')
        final=Path(pair['gate_path']).read_text(encoding='utf-8-sig')
        result=batch.final_sec(initial,final,pair['top_module'],output/pair['top_module'])
        if (batch.source_manifest()!=source or batch.sha(audit_path)!=audit_sha
                or batch.sha(batch.LIB)!=lib_sha
                or any(batch.sha(Path(pair[role+'_path']))!=pair[role+'_sha256'] for role in ['gold','gate'])
                or batch.sha(Path(pair['actual_final_state_source']))!=pair['state_file_sha256']):
            raise RuntimeError('Proof source/input drift after tool execution')
        row={'top':pair['top_module'],'result':result,
             'raw_decoded_text_equal':(output/pair['top_module']/'final_raw.v').read_text(encoding='utf-8-sig')==final,
             'artifacts':{p.name:batch.sha(p) for p in sorted((output/pair['top_module']).iterdir()) if p.is_file()}}
        receipt['results'].append(row)
        batch.save(target,receipt)
        print(pair['top_module'],result['status'],flush=True)
        if result['status']!='pass' or not row['raw_decoded_text_equal']:
            return 1
    receipt['source_stable']=batch.source_manifest()==source and batch.sha(batch.LIB)==lib_sha and batch.sha(audit_path)==audit_sha
    receipt['status']='completed'
    batch.save(target,receipt)
    return 0 if receipt['source_stable'] else 1

if __name__=='__main__':
    raise SystemExit(main())
