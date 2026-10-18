"""Read-only OI048 proof-route audit; no tools or Git are started."""
from pathlib import Path
import ast,hashlib,json,re,time,zipfile
ROOT=Path.cwd();OUT=ROOT/'project_docs/evidence/r22_cec_top_scope_audit_20261018';OUT.mkdir(exist_ok=False)
SEEN={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 p=p.resolve();key=p.relative_to(ROOT).as_posix();data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if key in SEEN:assert SEEN[key]['sha256']==digest,key
 SEEN[key]={'sha256':digest,'bytes':len(data)}
 return data.decode('utf-8-sig')
def load(p):return json.loads(read(p))
def check(folder,circuit,family,expected=None):
 ys=read(folder/'sec.ys');log=read(folder/'sec.log');result=load(folder/'result.json')
 required=[f'rename {circuit} gold',f'rename {circuit} gate','equiv_make gold gate equiv','hierarchy -top equiv','flatten','equiv_simple','equiv_induct -seq 10','equiv_status -assert']
 lines=[x.strip() for x in ys.splitlines() if x.strip()];assert all(x in lines for x in required),(folder,'missing explicit proof command')
 assert lines.index('equiv_make gold gate equiv')<lines.index('hierarchy -top equiv')<lines.index('flatten')
 assert 'abc' not in str(result['command']).lower() and 'yosys' in str(result['command']).lower()
 assert result['status']=='pass' and result['returncode']==0
 matches=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log);assert matches,(folder,'no nonempty proof summary');proven,unproven=map(int,matches[-1]);assert proven>0 and unproven==0 and 'Equivalence successfully proven!' in log
 assert 'No SAT model available' not in log
 read(folder/'initial_raw.v');read(folder/'final_raw.v');read(folder/'helpers.v');assert sha(folder/'initial_raw.v')==result['initial_sha256'] and sha(folder/'final_raw.v')==result['final_sha256'] and sha(folder/'helpers.v')==result['shared_helpers_sha256']
 matched=0
 for name,d in (expected or {}).items():
  p=folder/name;read(p);assert sha(p)==(d.get('sha256') if isinstance(d,dict) else d),(folder,name);matched+=1
 return {'family':family,'circuit':circuit,'folder':folder.relative_to(ROOT).as_posix(),'classification':'not affected by OI048 default-top ABC counterexample','route':'explicit renamed gold/gate Yosys equiv; not shared ABC wrapper','method':result['method'],'command':result['command'],'proven':proven,'unproven':unproven,'bound_artifacts_checked':matched,'sec_ys_sha256':sha(folder/'sec.ys'),'sec_log_sha256':sha(folder/'sec.log'),'result_sha256':sha(folder/'result.json')}
start=time.monotonic();read(Path(__file__));native=load(ROOT/'project_docs/evidence/r22_s_spef_integrated_20261018/native_top_counterexample/RESULT.json');matrix=load(ROOT/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json');proofs=[]
for job in matrix['jobs']:
 folder=ROOT/'experiments/20261016_r22_cut_ablation_v3'/job['arm']/job['circuit']/'final_sec';expected={k[len('final_sec/'):]:v for k,v in job['evidence_receipt'].items() if k.startswith('final_sec/')};proofs.append({**check(folder,job['circuit'],'Cprime72',expected),'arm':job['arm']})
print('Cprime checked',len(proofs),flush=True)
a=ROOT/'project_docs/evidence/r22_a_sec_20261016_frozen/proofs'
for folder in sorted(a.iterdir()):
 if folder.is_dir():receipt=load(folder/'receipt.json');proofs.append(check(folder,folder.name,'A6',receipt['artifacts']))
b=ROOT/'project_docs/evidence/r22_b_model_audit_20261016';b2=load(b/'new_model_proofs/manifest_and_results.json')
for row in b2['results']:proofs.append(check(b/'new_model_proofs'/row['top'],row['top'],'B2',row['artifacts']))
b17=load(b/'B17_PROOF_RECOVERY_DESIGN.json');proofs.append(check(b/'B17_new_model_proofs/final_sec','b17','B17',b17['stability']['output_hashes']))
# Read exact archived runtime sources rather than infer historical behavior from
# today's in-flight implementation edits.
zip_path=ROOT/'project_docs/evidence/r22_cprime_v3_20261016/source_snapshot/runtime_inputs.zip';read(zip_path) if False else None
SEEN[zip_path.relative_to(ROOT).as_posix()]={'sha256':sha(zip_path),'bytes':zip_path.stat().st_size}
snapshot=load(zip_path.parent/'snapshot.json');z=zipfile.ZipFile(zip_path);historical={}
for name in ['code/src/rseco/real_wns.py','code/src/rseco/yosys_abc.py','code/src/rseco/structure_resynthesis.py','code/src/rseco/flow.py','code/scripts/run_r22_cut_ablation.py']:
 data=z.read(name);s=data.decode('utf-8-sig');(OUT/('pinned_'+Path(name).name)).write_bytes(data)
 rows=[];tree=ast.parse(s)
 for node in ast.walk(tree):
  if isinstance(node,ast.Call):
   fn=ast.unparse(node.func)
   if fn.rsplit('.',1)[-1] in ['_normalize_to_blif','check_yosys_abc_equivalence','check_mapped_blif_equivalence','final_sec']:
    rows.append({'line':node.lineno,'function':fn,'keywords':{k.arg:ast.unparse(k.value) for k in node.keywords if k.arg},'call':ast.get_source_segment(s,node)})
 historical[name]={'sha256':hashlib.sha256(data).hexdigest(),'calls':rows}
call_sites=[]
for name in ['code/src/rseco/flow.py','code/src/rseco/real_wns.py','code/src/rseco/structure_resynthesis.py','code/src/rseco/yosys_abc.py','code/scripts/verify_epfl_mapping_cec.py']:
 text=read(ROOT/name);tree=ast.parse(text);rows=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Call) and ast.unparse(node.func).rsplit('.',1)[-1] in ['_normalize_to_blif','check_yosys_abc_equivalence','check_mapped_blif_equivalence']:
   rows.append({'line':node.lineno,'function':ast.unparse(node.func),'keywords':{k.arg:ast.unparse(k.value) for k in node.keywords if k.arg},'call':ast.get_source_segment(text,node)})
 call_sites.append({'source':name,'source_sha256':sha(ROOT/name),'calls':rows})
after={k:{'sha256':sha(ROOT/k),'bytes':(ROOT/k).stat().st_size} for k in SEEN};changed=[k for k,v in SEEN.items() if v!=after[k]]
report={'date':'2026-10-18','EDA_executed':False,'Git_executed':False,'scope':'OI048 routing audit, not broad re-certification','proof_counts':{f:sum(x['family']==f for x in proofs) for f in ['Cprime72','A6','B2','B17']},'proofs':proofs,'native_counterexample':{'result_sha256':sha(ROOT/'project_docs/evidence/r22_s_spef_integrated_20261018/native_top_counterexample/RESULT.json'),'status':native['result']['status'],'semantic_counterexample':native['semantic_counterexample'],'classification':'affected: known false pass with ABC selecting first library root'},'pinned_3ea_call_sites':historical,'current_call_sites':call_sites,'source_before':SEEN,'source_after':after,'source_changed_during_read':changed,'old_evidence_stable':not any(not k.startswith('code/') for k in changed),'runtime_seconds':time.monotonic()-start,'limitations':['not affected by this counterexample is not an unrestricted proof validity claim','A reused legacy two proofs and other historical ABC results are not globally certified by this audit','generic topNone call sites show risk, not proof every legacy endpoint is false','current root code may be changing; archived 3ea bytes are the historical authority']}
(OUT/'REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'counts':report['proof_counts'],'changed':changed,'runtime_s':report['runtime_seconds']}),flush=True)
