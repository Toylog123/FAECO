from pathlib import Path
import json,re,hashlib,time,collections
ROOT=Path.cwd();OUT=ROOT/'project_docs/evidence/r22_cec_top_scope_audit_20261018/historical_objects_followup';OUT.mkdir(exist_ok=False)
readmap={};started=time.time()
def read(p):
 p=Path(p);b=p.read_bytes();readmap[str(p.relative_to(ROOT)).replace('\\','/')]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return b.decode('utf-8-sig',errors='replace')
def remap(s):
 s=s.replace('\\','/');m=re.search(r'(?:^|/)(experiments|data|project_docs)/',s)
 return ROOT/s[m.start():].lstrip('/') if m else ROOT/s

def blif(p):
 t=read(p);models={};active=None;order=[]
 for line in re.sub(r'\\\r?\n',' ',t).splitlines():
  q=line.split('#')[0].split()
  if not q:continue
  if q[0]=='.model':active=q[1];order.append(active);models[active]={'refs':set(),'inputs':[],'outputs':[]}
  elif q[0]=='.end':active=None
  elif active:
   if q[0] in ['.subckt','.gate']:models[active]['refs'].add(q[1])
   elif q[0] in ['.inputs','.outputs']:models[active][q[0][1:]].extend(q[1:])
 refs=set().union(*(v['refs'] for v in models.values())) if models else set()
 return {'path':str(p.relative_to(ROOT)).replace('\\','/'),'models_in_order':order,'roots':sorted(set(models)-refs),'unresolved_referenced_models':sorted(refs-set(models)),'models':{n:{**v,'refs':sorted(v['refs'])} for n,v in models.items()}}

inventory=read(ROOT/'scratch/historical_cec_log_inventory_1018.txt').splitlines();(OUT/'LOG_PATH_DISCOVERY.txt').write_text('\n'.join(inventory)+'\n')
rows=[]
for lp in inventory:
 p=ROOT/lp;log=read(p)
 if p.name=='abc_baseline.log':continue
 matches=re.findall(r'\bcec\s+(\S+\.blif)\s+(\S+\.blif)',log)
 row={'log':str(p.relative_to(ROOT)).replace('\\','/'),'log_has_equivalence':bool(re.search(r'(?:networks|circuits) are equivalent',log,re.I)),'multiroot_diagnostics':re.findall(r'[^\n]*root-level modules[^\n]*',log,re.I),'read_failure_diagnostics':re.findall(r'[^\n]*(?:Cannot find the model|Reading network.*failed|Cannot open input)[^\n]*',log,re.I)}
 if matches:
  paths=[remap(x) for x in matches[0]];row['command_objects']=matches[0];row['retained_sides']=[blif(x) if x.exists() else {'path':str(x),'missing':True} for x in paths]
  sides=row['retained_sides'];single=all(len(x.get('models_in_order',[]))==1 and len(x.get('roots',[]))==1 for x in sides)
  row['verdict']='single-root retained objects; no wrong-first-root condition' if single else ('recorded error, not a pass' if not row['log_has_equivalence'] and row['read_failure_diagnostics'] else 'unknown: multi-model or missing object, needs binding')
 else:row['verdict']='unknown: no CEC command parsed'
 metrics=p.parent.parent/'metrics.json'
 if metrics.exists():
  obj=json.loads(read(metrics));key='formal_equivalence' if p.name=='abc_cec.log' else 'abc_baseline';row['metrics_record']=obj.get(key);row['metrics_path']=str(metrics.relative_to(ROOT)).replace('\\','/')
  if key=='abc_baseline':row['metrics_output_path_matches_cec_rhs']=remap(obj[key].get('output_netlist',''))==paths[1]
 rows.append(row)
# Read original/candidate source attachments for the six retained demo cases;
# only exact BOM sanitation comparisons are treated as byte bindings.
source_bindings=[]
configs=['experiments/20260717_minimal_combinational_demo/config.json','experiments/20260718_minimal_combinational_batch_demo/config.json']
for cfg in configs:
 o=json.loads(read(ROOT/cfg));cases=o.get('cases',[o])
 for c in cases:
  case=remap(c['case_dir']);read(case/'case.yaml');rr=remap(c['raw_results']).parent
  record={'config':cfg,'run_id':c.get('run_id',o['experiment_id']),'case_dir':str(case.relative_to(ROOT)).replace('\\','/'),'sources':[]}
  for kind in ['original','resynthesized']:
   for p in sorted((case/kind).glob('*.v')):
    text=read(p);side='original' if kind=='original' else 'revised';san=rr/'formal_equivalence'/f'{side}.sanitized.v'
    entry={'path':str(p.relative_to(ROOT)).replace('\\','/'),'modules':re.findall(r'\bmodule\s+(\w+)',re.sub(r'//[^\n]*|/\*[\s\S]*?\*/','',text))}
    if san.exists():entry['exact_sanitized_text_match']=read(san)==text
    record['sources'].append(entry)
  source_bindings.append(record)
# EPFL exact mapped artifact receipt.
ep=json.loads(read(ROOT/'experiments/20260731_epfl_ctrl_sky130_mapping/cec_summary.json'));mapping=json.loads(read(ROOT/'experiments/20260731_epfl_ctrl_sky130_mapping/ctrl/mapping_report.json'))
ep_mapped=ROOT/'experiments/20260731_epfl_ctrl_sky130_mapping/ctrl/mapping/mapped.blif'
assert readmap[str(ep_mapped.relative_to(ROOT)).replace('\\','/')]['sha256']==mapping['mapped_artifacts_sha256']['mapped.blif']
# Old A reused pair proofs: actual B script/log/source objects, not the 81 new proofs.
old=json.loads(read(ROOT/'project_docs/evidence/r22_historical_correctness_20261014/correctness_audit.json'));arows=[]
def module_text(text,name):
 m=re.search(r'\bmodule\s+'+re.escape(name)+r'\b[\s\S]*?\bendmodule',text);assert m;return '\n'.join(x.strip() for x in m.group().splitlines() if x.strip())
for circuit in ['s27','s820']:
 a=next(x for x in old['runs'] if x['family']=='A' and x['circuit']==circuit);b=next(x for x in old['runs'] if x['family']=='B' and x['circuit']==circuit)
 sec=b['sec'];script=read(ROOT/sec['script']);log=read(ROOT/sec['log']);gold=read(ROOT/sec['gold_file']);gate=read(ROOT/sec['gate_file']);afinal=read(remap(a['final_source']));initial=read(remap(a['run'])/'mapped.v')
 exact_gate=module_text(gate,circuit)==module_text(afinal,circuit);exact_gold=module_text(gold,circuit)==module_text(initial,circuit)
 script_tokens={x:(x in script) for x in [f'rename {circuit} gold',f'rename {circuit} gate','equiv_make gold gate equiv','hierarchy -top equiv','equiv_status -assert']}
 counts=re.findall(r'Of\s+(\d+)\s+\$equiv cells.*?(\d+) are proven and\s+(\d+) are unproven',log)
 arows.append({'circuit':circuit,'script':sec['script'],'log':sec['log'],'script_scope_tokens':script_tokens,'log_equiv_counts':counts,'success_assert':('Equivalence successfully proven!' in log),'gold_matches_A_initial_top_ignoring_blank_lines':exact_gold,'gate_matches_A_final_top_ignoring_blank_lines':exact_gate,'verdict':'not affected by ABC omitted-top counterexample' if all(script_tokens.values()) and exact_gold and exact_gate else 'unknown: inspect raw facts'})
# Read caller contracts as current context only, never infer historical source provenance.
for p in ['code/src/rseco/flow.py','code/src/rseco/abc_baseline.py','code/scripts/verify_epfl_mapping_cec.py','project_docs/evidence/r22_cec_top_scope_audit_20261018/REPORT.md','project_docs/evidence/r22_cec_top_scope_audit_20261018/SCOPE_MATRIX.json']:read(ROOT/p)
summary={'scope':'bounded read-only historical object followup; excludes 81 already-reviewed new proofs and S local proofs; no EDA/source/Git changes','elapsed_s':time.time()-started,'discovered_old_nons_cec_and_baseline_logs':len(inventory),'actual_cec_pairs_reviewed':len(rows),'verdict_counts':dict(collections.Counter(x['verdict'] for x in rows)),'rows':rows,'demo_source_attachments':source_bindings,'epfl':{'cec_status':ep['per_case'][0]['result']['status'],'mapped_blif_sha_matches_original_mapping_receipt':True},'A_reused_old_proofs':arows,'limits':['No contemporaneous per-proof source/BLIF SHA receipt exists for demo files; present bytes and historical command-path bindings do not exclude later overwrite.','No full historical source commit was recovered; current caller source is only context, not retrospective source provenance.','Other old logs under different names/versions, missing artifacts, and S pre/post overwrite gaps remain unknown.','Not a four-state/model/initialization/candidate-correctness revalidation.'],'read_artifacts':readmap}
for name,item in [('OBJECT_AUDIT.json',summary),('READ_SHA_MANIFEST.json',readmap)]: (OUT/name).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pairs':len(rows),'verdict_counts':summary['verdict_counts'],'A':arows,'read_files':len(readmap)},ensure_ascii=False,indent=2))
