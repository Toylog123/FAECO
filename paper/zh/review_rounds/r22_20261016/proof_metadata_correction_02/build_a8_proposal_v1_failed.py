"""Prepare source/input identities only; no prover import or execution."""
from pathlib import Path
import hashlib, io, json, re

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
reads={}
def identity(path):
    path=ROOT/path
    b=path.read_bytes()
    item={'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    reads[item['path']]=item
    return item
def read(path):
    identity(path)
    return (ROOT/path).read_text(encoding='utf-8-sig')
def load(path):return json.loads(read(path))
def modules(text):
    return {m.group(1):m.group() for m in re.finditer(r'\bmodule\s+(\w+)\b[\s\S]*?\bendmodule',text)}
old=load('project_docs/evidence/r22_historical_correctness_20261014/correctness_audit.json')
dmanifest=load('experiments/20261018_r22_D_revalidate_v1/manifest.json')
assert dmanifest['source_pin']['head']=='f761ee1996a83fc4f0f3de0999b74d85a8237858'
for path,expected in dmanifest['source_pin']['files'].items():assert identity(path)['sha256']==expected,path
common=read('code/scripts/run_r22_cut_ablation.py')
assert 'def final_sec(initial, final, circuit, out):' in common
assert 'timeout=180' in common and 'equiv_induct -seq 10' in common and 'equiv_status -assert' in common
lib=identity('data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')
oldrows=load(OUT.relative_to(ROOT)/'actual_verification/VERIFIED_A_METADATA.json')['rows']
cases=[]
for circuit in ['s27','s382','s420','s641','s713','s820','s832','s953']:
    row=next(r for r in old['runs'] if r['family']=='A' and r['circuit']==circuit)
    initial_path=Path(row['run'].replace('\\','/'))/'mapped.v'
    final_path=Path(row['final_source'].replace('\\','/'))
    initial=read(initial_path);final=read(final_path)
    left,right=modules(initial),modules(final)
    assert circuit in left and circuit in right
    assert {n:t for n,t in left.items() if n!=circuit}=={n:t for n,t in right.items() if n!=circuit}
    result=load(Path(row['run'].replace('\\','/'))/'outerloop_result.json')
    ledger=load(Path(row['run'].replace('\\','/'))/'eval_trials.json')
    accepted=[r for r in ledger['trials'] if r.get('accepted')]
    keys=('instance','kind','to_type')
    assert [{k:r.get(k) for k in keys} for r in accepted]==[{k:r.get(k) for k in keys} for r in row['accepted_actions']]
    assert result['success'] and result['circuit']==circuit
    previous=next(r for r in oldrows if r['circuit']==circuit)
    if previous['batch']=='P1':
        assert reads[str(initial_path).replace('\\','/')]['sha256']==previous['gold_input']['sha256']
        # s713's counterpart bytes differ only by universal-newline decoding.
        proofraw=f'project_docs/evidence/r22_a_sec_20261016_frozen/proofs/{circuit}/final_raw.v'
        assert read(proofraw)==final
    cases.append({'circuit':circuit,'baseline':identity(initial_path),'accepted_final':identity(final_path),
        'baseline_decoded_utf8_sha256':hashlib.sha256(initial.encode()).hexdigest(),
        'final_decoded_utf8_sha256':hashlib.sha256(final.encode()).hexdigest(),
        'shared_helpers_equal_after_utf8_bom_and_universal_newline_decode':True,
        'declared_modules':sorted(left),'used_sky_models':sorted(set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+\w+\s*\(',initial+'\n'+final))),
        'accepted_actions':[{k:r.get(k) for k in keys} for r in accepted],
        'historical_proof_batch':previous['batch'],'historical_proven_unproven':[previous['proven'],previous['unproven']],
        'new_output_proposal':f'project_docs/evidence/r22_a_sec_unified_20261018/proofs/{circuit}',
        'status':'proposed; not registered or executed'})
for path,record in reads.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==record['sha256'],path
plan={'schema':'A8-unified-sec-input-proposal-v1','status':'proposal only; root confirmation and fresh registration required before any SEC',
    'external_prover_started':False,'new_sta_runs':0,
    'source_pin_from_locked_D_manifest':dmanifest['source_pin'],
    'source_sha_matches_pin_now':True,'current_head_not_independently_queried':True,
    'liberty':lib,'cases':cases,'execution':{'reuse':'code/scripts/run_r22_cut_ablation.py:final_sec',
    'parallelism':1,'per_check_timeout_s':180,'whole_wrapper_timeout_s':1800,
    'prover':'wsl.exe -d Ubuntu -- /usr/bin/yosys <sec.ys>',
    'proof_method':'explicit gold/gate circuit; shared equal helpers; model/port/two-state preflight; hierarchy -top equiv; flatten; equiv_simple; equiv_induct -seq 10; equiv_status -assert',
    'timing':'One uniform batch, runtime_s reported by shared final_sec; wall interval around external prover and log emission, excluding model/input preparation. No CPU/wall conversion.',
    'preserve_original_bytes':'Before final_sec decode, copy exact original baseline/final bytes into separate exclusive source_snapshots with SHA. Common initial_raw/final_raw may have newline serialization differences; bind both byte identity and decoded-text identity.',
    'pass_gate':'Every registered input/source/lib SHA stable before and after; exact expected circuit top; returncode0, statuspass, actual log nonzero proven and zero unproven, equivalence success; complete per-proof artifacts/receipts; independent root review.',
    'point_count_policy':'11/90/79/124/126/137/146/228 are prior-proof observations only. Read actual new log counts; never require equality to old counts when model/flatten changes number of equiv cells.',
    'failure':'Any unsupported/timeout/mismatch/drift/nonzero/unproven stops further launch and preserves attempted evidence; no fallback to old proof/time.',
    'D_protection':'No change to D manifest/config/source/HEAD; no remapping/STA/OpenROAD/candidate search. Separate output root; sequential SEC, D two-circuit STA ownership unchanged.'},
    'read_sources_sha_before_after_stable':True,'read_artifacts':reads}
with (OUT/'A8_INPUT_PROPOSAL.json').open('x',encoding='utf-8') as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'cases':len(cases),'source_pin':dmanifest['source_pin']['head'],'read_files':len(reads),'external_prover_started':False,
                  'inputs':[(c['circuit'],c['baseline']['sha256'],c['accepted_final']['sha256']) for c in cases]},indent=2))
