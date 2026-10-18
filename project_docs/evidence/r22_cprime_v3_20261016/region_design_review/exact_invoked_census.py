"""One predeclared static census; subprocess boundaries disabled during checks."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,time
from types import SimpleNamespace
from datetime import datetime,timezone
import networkx as nx

R=Path(__file__).resolve().parents[2]
OUT=R/'project_docs/evidence/r22_cprime_v3_20261016/region_design_review'
CONTRACT=OUT/'CONTRACT.json'
RUN=OUT/'census_v2'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def textsha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def save(p,data):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
contract=load(CONTRACT);contract_sha=sha(CONTRACT)
RUN.mkdir(exist_ok=False)
for p,h in {**contract['source_sha256'],**contract['input_sha256']}.items():assert sha(R/p)==h,p
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==contract['head']
started=time.perf_counter();start_utc=datetime.now(timezone.utc).isoformat()
sys.path[:0]=[str(R/'code/src'),str(R/'code/scripts'),str(R/'project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER')]
from rseco.cut import (constrained_weighted_cut_candidates,_cut_for_selected_gates,
 _critical_path_cover_cut,canonical_cut_hash,build_weighted_cut_graph,_build_st_capacities)
from rseco.graph import extract_fanin_cone
from rseco.replacement import parse_verilog_netlist_from_text
from rseco.verilog_modules import target_module_text
from rseco.real_wns import parse_critical_instances
from backend import ActualBackend

native_run=subprocess.run;external_calls=[]
def no_process(*args,**kwargs):
 external_calls.append(str(args));raise RuntimeError('Static census must not launch any external process')
subprocess.run=no_process
results=[];controls=[];candidate_files={}

def region_info(netlist,cone,cut,critical):
 selected=set(cut.gates);drivers={signal:g.name for g in netlist.gates for signal in g.all_outputs}
 expected_in=list(dict.fromkeys(n for g in netlist.gates if g.name in selected for n in g.inputs if drivers.get(n) not in selected))
 # Physical source outputs keep their identity even when also const aliases.
 module_outputs={n if n in drivers else netlist.resolve_alias(n) for n in netlist.outputs}
 expected_out=list(dict.fromkeys(n for g in netlist.gates if g.name in selected for n in g.all_outputs if n in cone.boundary_outputs or n in module_outputs or any(n in other.inputs for other in netlist.gates if other.name not in selected)))
 G=nx.Graph();G.add_nodes_from(selected)
 for g in netlist.gates:
  if g.name in selected:
   for n in g.inputs:
    if drivers.get(n) in selected:G.add_edge(g.name,drivers[n])
 return {'connected':bool(selected) and nx.is_connected(G),
  'boundary_closed':set(cut.boundary_inputs)==set(expected_in) and set(cut.boundary_outputs)==set(expected_out),
  'expected_boundary_inputs':expected_in,'expected_boundary_outputs':expected_out,
  'critical_coverage':len(selected&set(critical)),
  'multioutput_gate_count':sum(len(g.all_outputs)>1 for g in netlist.gates if g.name in selected)}

try:
 for circuit in contract['scope']:
  directory=R/'experiments/20261016_r22_cut_ablation_v3/W0'/circuit
  initial=(directory/'mapped.v').read_text(encoding='utf-8');actual=load(directory/'outerloop_result.json')
  critical=parse_critical_instances((directory/'sta.log').read_text(encoding='utf-8'))
  assert critical==actual['critical_instances']==actual['candidate_pool_trace'][0]['critical_instances']
  b=ActualBackend(circuit);assert b.validate(initial,initial)['status']=='pass'
  metadata={n:dict(c.output_functions) for n,c in b.cells.items() if c.output_functions}
  netlist=parse_verilog_netlist_from_text(target_module_text(initial,circuit),cell_output_functions=metadata)
  cone=extract_fanin_cone(netlist,[actual['target_net']]);snapshot=b.snapshot(initial)
  scoped_critical=[g for g in critical if g in cone.gates]
  configurations=[('configured',SimpleNamespace(**contract['configured_weights'])),('uniform',SimpleNamespace(**contract['uniform_weights']))]
  union={};generation={}
  def append(cut,origin):
   key=canonical_cut_hash(cut)
   if key not in union:union[key]={'cut':cut,'origins':[]}
   if origin not in union[key]['origins']:union[key]['origins'].append(origin)
  for name,weights in configurations:
   cuts,diagnostics=constrained_weighted_cut_candidates(cone,weights,k=5,
    critical_instances=scoped_critical,min_critical_coverage=1,hard_anchors=[],
    window_size=len(cone.gates),allow_singleton=False,beam_width=40,
    max_region_evaluations=320,wall_timeout_s=None,return_diagnostics=True)
   generation[name]={'cut_hashes':[canonical_cut_hash(c) for c in cuts],'diagnostics':diagnostics}
   for cut in cuts:append(cut,'generated_'+name)
  root=cone.signal_drivers()[cone.boundary_outputs[0]]
  append(_cut_for_selected_gates(cone,[root],method='retained_singleton'),'singleton_control')
  cover=_critical_path_cover_cut(cone,critical,r_available=None)
  if cover is not None:append(cover,'full_critical_cover_control')
  action_config=SimpleNamespace(only_strategy=None,enable_buffer=True,buf_types=tuple(contract['actions']['buf_types']))
  instance_cache={};candidate_cache={}
  def witnesses(instance):
   if instance in instance_cache:return instance_cache[instance]
   proposals=b.candidates(snapshot,instance,action_config)
   by_kind={kind:[a for a in proposals if a.kind==kind] for kind in ['R','G','B']}
   checks=[]
   for kind,actions in by_kind.items():
    for action in actions[:3]:
     descriptor={k:getattr(action,k) for k in ['instance','kind','target','pin_map','pin','new_net']}
     try:
      candidate=b.apply(initial,action);digest=textsha(candidate)
      if candidate==initial:validation={'status':'not_changed'}
      elif digest in candidate_cache:validation=candidate_cache[digest]
      else:
       validation=b.validate(initial,candidate);candidate_cache[digest]=validation
       if validation['status']=='pass':
        path=RUN/(circuit+'_witnesses');path.mkdir(exist_ok=True)
        file=path/(digest+'.v')
        if not file.exists():
         with file.open('x',encoding='utf-8',newline='') as f:f.write(candidate)
        assert sha(file)==digest
        candidate_files[file.relative_to(R).as_posix()]=digest
      checks.append({'action':descriptor,'candidate_sha256':digest,'static_validation':validation})
     except (ValueError,RuntimeError) as error:
      checks.append({'action':descriptor,'static_validation':{'status':'error','reason':str(error)}})
   result={'instance':instance,'cell_type':next(c.cell_type for c in snapshot if c.instance==instance),
    'proposals_by_kind':{k:len(v) for k,v in by_kind.items()},
    'untested_by_kind':{k:max(0,len(v)-3) for k,v in by_kind.items()},'checks':checks,
    'passed_candidates':sorted({c['candidate_sha256'] for c in checks if c['static_validation']['status']=='pass'})}
   instance_cache[instance]=result;return result
  region_rows=[]
  for key,item in union.items():
   cut=item['cut'];geometry=region_info(netlist,cone,cut,critical)
   ordered=[g for g in critical if g in cut.gates]+[g for g in cone.gates if g in cut.gates and g not in critical]
   actions=[witnesses(g) for g in ordered[:8]]
   passed=sorted({h for info in actions for h in info['passed_candidates']})
   eligible=geometry['connected'] and geometry['boundary_closed'] and geometry['critical_coverage']>=1 and bool(passed)
   region_rows.append({'cut_hash':key,**cut.to_dict(),'origins':item['origins'],**geometry,
    'tested_instances':[g['instance'] for g in actions],'witness_candidates':passed,
    'eligibility':eligible,'eligibility_scope':'domain/F1/F2 static witness; not independent SEC/STA/strict full acceptance',
    'unknown_if_no_witness':not bool(passed)})
  r_available={g for g in cone.gates if any(a.kind=='R' for a in b.candidates(snapshot,g,action_config))}
  graphs={name:build_weighted_cut_graph(cone,weights,r_available) for name,weights in configurations}
  rankings={}
  for name,graph in graphs.items():
   for row in region_rows:row.setdefault('node_scores',{})[name]=sum(graph.node_costs[g] for g in row['gates'])
   eligible=[row for row in region_rows if row['eligibility']]
   rankings[name]=[r['cut_hash'] for r in sorted(eligible,key=lambda r:(r['node_scores'][name],r['cut_hash']))]
  assert set(rankings['configured'])==set(rankings['uniform'])
  by_hash={r['cut_hash']:r for r in region_rows}
  first={name:order[0] if order else None for name,order in rankings.items()}
  witness_changed=(bool(first['configured']) and bool(first['uniform']) and by_hash[first['configured']]['witness_candidates']!=by_hash[first['uniform']]['witness_candidates'])
  no_r_gb=[info['instance'] for info in instance_cache.values() if info['proposals_by_kind']['R']==0 and any(c['action']['kind'] in ['G','B'] and c['static_validation']['status']=='pass' for c in info['checks'])]
  capacities=_build_st_capacities(cone,graphs['configured'])
  controls.append({'circuit':circuit,'root_source_dependency_kept':root+':in' in capacities.get(graphs['configured'].source,{}),
   'singleton_retained':any('singleton_control' in r['origins'] for r in region_rows),
   'full_cover_retained':cover is None or any('full_critical_cover_control' in r['origins'] for r in region_rows),
   'no_R_but_GB_static_witness_instances':no_r_gb,
   'actual_multioutput_region_count':sum(r['multioutput_gate_count']>0 for r in region_rows),
   'same_eligible_union':set(rankings['configured'])==set(rankings['uniform'])})
  results.append({'circuit':circuit,'initial_text_sha256':textsha(initial),'baseline_critical':critical,
   'scoped_critical':scoped_critical,'target_net':actual['target_net'],'cone':cone.to_dict(),
   'generator_results':generation,'regions':region_rows,'instance_witness_checks':list(instance_cache.values()),
   'r_available':sorted(r_available),'rankings':rankings,'top1':first,
   'summary':{'union_regions':len(region_rows),'eligible_regions':len(rankings['configured']),
    'multiple_static_witness_regions':len(rankings['configured'])>=2,
    'distinct_witness_sets':len({tuple(row['witness_candidates']) for row in region_rows if row['eligibility']}),
    'same_top1':first['configured']==first['uniform'],'same_order':rankings['configured']==rankings['uniform'],
    'top1_witness_candidates_differ':witness_changed,'no_R_GB_instances':no_r_gb}})
  print(json.dumps({'circuit':circuit,**results[-1]['summary']},ensure_ascii=False),flush=True)
 # Static geometry controls using actual Liberty outputs; not timing evidence.
 metadata={n:dict(c.output_functions) for n,c in b.cells.items() if c.output_functions}
 examples={
 'multioutput_secondary_consumer':('''module top(A,B,CIN,S,C);\ninput A,B,CIN;\noutput S,C;\nwire co;\nsky130_fd_sc_hd__fa_1 f(.A(A),.B(B),.CIN(CIN),.COUT(co),.SUM(S));\nsky130_fd_sc_hd__buf_1 consume(.A(co),.X(C));\nendmodule\n''','S','co'),
 'zero_input_source':('''module top(ZERO,ONE);\noutput ZERO,ONE;\nsky130_fd_sc_hd__conb_1 c(.LO(ZERO),.HI(ONE));\nendmodule\n''','ZERO','ONE')}
 for name,(text,target,secondary) in examples.items():
  netlist=parse_verilog_netlist_from_text(text,cell_output_functions=metadata);cone=extract_fanin_cone(netlist,[target])
  cut=_cut_for_selected_gates(cone,cone.gates,method='static_control')
  geometry=region_info(netlist,cone,cut,[])
  assert geometry['boundary_closed'] and secondary in cut.boundary_outputs
  graph=build_weighted_cut_graph(cone,SimpleNamespace(**contract['configured_weights']))
  source=_build_st_capacities(cone,graph).get(graph.source,{})
  if name=='zero_input_source':assert cone.gate_inputs['c']==[] and 'c:in' in source
  controls.append({'fixture':name,**cut.to_dict(),**geometry,'secondary_boundary_preserved':True,
    'source_anchored':bool(source),'scope':'implementation geometry control only, no actual timing/SEC claim'})
finally:
 subprocess.run=native_run

elapsed=time.perf_counter()-started
for p,h in {**contract['source_sha256'],**contract['input_sha256']}.items():assert sha(R/p)==h,p
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==contract['head']
assert sha(CONTRACT)==contract_sha and not external_calls
report={'schema':'r22-region-static-census-v1','declared_contract_sha256':contract_sha,
 'started_utc':start_utc,'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_s':elapsed,
 'scope':'partial4 initial states only','eda_executed':False,'external_process_calls_during_census':external_calls,
 'parameters_scanned_or_tuned':False,'source_input_stable':True,'head':contract['head'],
 'source_sha256':contract['source_sha256'],'input_sha256':contract['input_sha256'],
 'auditor_sha256':sha(Path(__file__)),'candidate_witness_files':candidate_files,'circuits':results,'controls':controls,
 'limitations':['Bounded proposal union, not exhaustive feasible-region universe.',
 'Witness search bounded first3 eachRGB/instance; untested not invalid.',
 'Static F1/F2 only: no independent SEC/F3/F5/STA/acceptance or timing benefit.',
 'Node sum ranking differs from internal full constrained region_score; common-union isolates only declared node-cost ranking.']}
save(RUN/'CENSUS.json',report)
print(json.dumps({'elapsed_s':elapsed,'candidate_witness_files':len(candidate_files),'source_input_stable':True,'eda':False},indent=2),flush=True)
