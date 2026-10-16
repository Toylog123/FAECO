"""Bind prior exact proofs to unchanged generated models after gate-only fixes."""
from pathlib import Path
import importlib.util
import json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'code/scripts'),str(ROOT/'code/src')]
import run_r22_cut_ablation as b
from rseco.real_wns import write_liberty_cell_models

def main():
    output=ROOT/'project_docs/evidence/r22_correctness_20261016/proof_model_preservation'
    if output.exists():
        raise RuntimeError('Never overwrite previous model witnesses')
    output.mkdir()
    source=b.source_manifest()
    liberty=b.LIB.read_text(encoding='utf-8')
    library_sha=b.sha(b.LIB)
    cases=[('A_'+c,ROOT/'project_docs/evidence/r22_a_sec_20261016_frozen/proofs'/c)
           for c in ['s382','s420','s641','s713','s832','s953']]
    cases += [('B_'+c,ROOT/'project_docs/evidence/r22_b_model_audit_20261016/new_model_proofs'/c)
              for c in ['picorv32','picorv32_pcpi_mul']]
    cases += [('B17',ROOT/'project_docs/evidence/r22_b_model_audit_20261016/B17_new_model_proofs/final_sec')]
    record=dict(status='registered',source_manifest=source,liberty_sha256=library_sha,
                verifier_sha256=b.sha(Path(__file__)),eda_executed=False,cases=[])
    receipt=output/'verification.json'
    b.save(receipt,record)
    for name,old in cases:
        proof=json.loads((old/'result.json').read_text(encoding='utf-8'))
        assert proof['status']=='pass'
        initial=(old/'initial_raw.v').read_text(encoding='utf-8')
        final=(old/'final_raw.v').read_text(encoding='utf-8')
        assert b.sha(old/'initial_raw.v')==proof['initial_sha256']
        assert b.sha(old/'final_raw.v')==proof['final_sha256']
        used=set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+\w+\s*\(',initial+'\n'+final))
        fresh=output/(name+'_cells.v')
        write_liberty_cell_models(liberty,fresh,used_cells=used)
        same=fresh.read_bytes()==(old/'cells.v').read_bytes()
        record['cases'].append(dict(name=name,proof_directory=old.relative_to(ROOT).as_posix(),
            proof_result_sha256=b.sha(old/'result.json'),old_model_sha256=b.sha(old/'cells.v'),
            new_model_sha256=b.sha(fresh),byte_identical=same))
        b.save(receipt,record)
        print(name,'model byte-identical:',same,flush=True)
    record.update(status='completed',source_stable=source==b.source_manifest() and library_sha==b.sha(b.LIB))
    record['passed']=record['source_stable'] and all(c['byte_identical'] for c in record['cases'])
    b.save(receipt,record)
    return 0 if record['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
