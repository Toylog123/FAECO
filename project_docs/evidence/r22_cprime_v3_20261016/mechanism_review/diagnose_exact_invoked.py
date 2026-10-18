"""Read-only partial4 Cprime node-cut attribution. No EDA or parameter edits."""
from pathlib import Path
import hashlib,json,subprocess,sys
from dataclasses import replace
from types import SimpleNamespace
import networkx as nx

R=Path(__file__).resolve().parents[2];D=R/'experiments/20261016_r22_cut_ablation_v3'
OUT=R/'project_docs/evidence/r22_cprime_v3_20261016/mechanism_review'
sys.path[:0]=[str(R/'code/src'),str(R/'code/scripts')]
from rseco.logic_rewrite import parse_liberty_cells
from rseco.replacement import parse_verilog_netlist_from_text
from rseco.verilog_modules import target_module_text
from rseco.graph import extract_fanin_cone
from rseco.cut import (build_weighted_cut_graph,solve_weighted_cut,_build_st_capacities,
                      _cut_for_selected_gates,canonical_cut_hash)
import run_r22_cut_ablation as common

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def textsha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def bind(p):
 p=Path(p);key=p.relative_to(R).as_posix();value=sha(p)
 if key in inputs:assert inputs[key]==value,key
 inputs[key]=value
 return p

inputs={};report_path=bind(R/'project_docs/evidence/r22_cprime_v3_20261016/mechanism_audits/MATCHED_STATE_PAIRS_08.json')
prior=load(report_path);manifest=load(bind(D/'manifest.json'))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
assert head==prior['head']==manifest['git_head']
assert sha(D/'manifest.json')==prior['manifest_sha256']
for p,h in prior['input_sha256'].items():assert sha(bind(R/p))==h
sources={p:sha(R/p) for p in ['code/src/rseco/cut.py','code/src/rseco/graph.py',
 'code/src/rseco/candidate_policy.py','code/src/rseco/flow.py','code/src/rseco/netlist.py',
 'code/src/rseco/replacement.py','code/src/rseco/logic_rewrite.py','code/src/rseco/verilog_modules.py']}
bind(common.LIB);cells=parse_liberty_cells(common.LIB.read_text(encoding='utf-8'))
metadata={name:dict(cell.output_functions) for name,cell in cells.items() if cell.output_functions}
rows=[];pairs=[];cone_cache={}

def independent_cut(cone,graph,*,exclude=()):
 costs={**graph.node_costs,**{g:graph.infinite_capacity for g in exclude}}
 modified=replace(graph,node_costs=costs,split_edges=[(a,b,costs[a[:-3]]) for a,b,_ in graph.split_edges])
 capacities=_build_st_capacities(cone,modified);G=nx.DiGraph()
 for u,edges in capacities.items():
  for v,value in edges.items():G.add_edge(u,v,capacity=value)
 value,(reachable,unreachable)=nx.minimum_cut(G,graph.source,graph.sink)
 selected=[g for g in cone.gates if g+':in' in reachable and g+':out' in unreachable]
 finite=value<graph.infinite_capacity*.5
 cut=_cut_for_selected_gates(cone,selected,method='independent_root_excluded') if finite else None
 return {'finite':finite,'value':value,'gates':selected,
         'boundary_inputs':cut.boundary_inputs if cut else None,
         'boundary_outputs':cut.boundary_outputs if cut else None,
         'cut_hash':canonical_cut_hash(cut) if cut else None}

for c in ['s27','s382','s420','s641']:
 for w,u in [('W0','U0'),('W1','U1')]:
  a=load(D/w/c/'outerloop_result.json');b=load(D/u/c/'outerloop_result.json')
  assert (D/w/c/'completion.json').is_file() and (D/u/c/'completion.json').is_file()
  initial_path=bind(D/w/c/'mapped.v');initial=initial_path.read_text(encoding='utf-8')
  texts={textsha(initial):initial}
  for patch in a['state']['accepted_patches']:
   assert patch['candidate_hash']==patch['netlist_hash']==textsha(patch['netlist_text'])
   texts[patch['candidate_hash']]=patch['netlist_text']
  matching=[]
  for t in a['candidate_pool_trace']:
   matches=[v for v in b['candidate_pool_trace'] if v['base_netlist_hash']==t['base_netlist_hash']]
   assert matches
   checks=[]
   for v in matches:
    checks.append({'uniform_round':v['round'],'cut_hash_lists_equal':[[x['cut_hash'] for x in s['candidates']] for s in t['subcones']]==[[x['cut_hash'] for x in s['candidates']] for s in v['subcones']],
      'ordered_pool_equal':t['pool_hashes']==v['pool_hashes'],'dispatch_equal':t['dispatch_hashes']==v['dispatch_hashes'],
      'uniform_costs_one':all(abs(x-1)<1e-12 for s in v['subcones'] for x in s['node_costs'].values())})
   assert all(all(x[k] for k in ('cut_hash_lists_equal','ordered_pool_equal','dispatch_equal','uniform_costs_one')) for x in checks)
   matching.append({'weighted_round':t['round'],'base_sha256':t['base_netlist_hash'],'all_same_state_uniform_rounds':checks})
   key=(c,t['base_netlist_hash'])
   if key not in cone_cache:
    text=texts[t['base_netlist_hash']]
    netlist=parse_verilog_netlist_from_text(target_module_text(text,c),cell_output_functions=metadata)
    cone_cache[key]=extract_fanin_cone(netlist,[a['target_net']])
   cone=cone_cache[key]
   # These four circuits have one unsplit cone. Refuse unsupported inference.
   assert len(t['subcones'])==1
   st=t['subcones'][0]
   assert set(st['node_costs'])==set(cone.gates),(c,w,t['round'],'unexpected split/missing cone')
   graph=build_weighted_cut_graph(cone,SimpleNamespace(**st['effective_weights']),set(t['r_available']) if t['r_available'] is not None else None)
   assert all(abs(graph.node_costs[g]-st['node_costs'][g])<1e-10 for g in cone.gates)
   solved=solve_weighted_cut(cone,graph);independent=independent_cut(cone,graph)
   weighted=[x for x in st['candidates'] if 'weighted' in x['origins']]
   assert len(weighted)==1
   observed=weighted[0]
   assert solved.selected_gates==observed['gates']
   assert abs(solved.cut_cost-st['weighted_cut_cost'])<1e-10
   assert abs(independent['value']-solved.cut_cost)<1e-9
   root_drivers=list(dict.fromkeys(cone.signal_drivers()[n] for n in cone.boundary_outputs))
   assert len(root_drivers)==1
   root=root_drivers[0];drivers=cone.signal_drivers()
   external=[n for n in cone.gate_inputs[root] if n not in drivers]
   root_is_source=not cone.gate_inputs[root] or bool(external)
   alternative=independent_cut(cone,graph,exclude=[root])
   uniform_graph=build_weighted_cut_graph(cone,SimpleNamespace(**{k:0. for k in st['effective_weights']}),set(t['r_available']) if t['r_available'] is not None else None)
   uniform_alt=independent_cut(cone,uniform_graph,exclude=[root])
   if root_is_source:assert not alternative['finite']
   rows.append({'circuit':c,'arm':w,'round':t['round'],'base_sha256':t['base_netlist_hash'],
    'target_net':a['target_net'],'root_gate':root,'cone_gates':len(cone.gates),
    'cone_outputs':cone.boundary_outputs,'external_exposed_not_timing_roots':cone.external_boundary_outputs,
    'weighted_selected':solved.selected_gates,'selected_is_root_singleton':solved.selected_gates==[root],
    'weighted_cost':solved.cut_cost,'node_cost_range':[min(graph.node_costs.values()),max(graph.node_costs.values())],
    'nonuniform':len({round(x,12) for x in graph.node_costs.values()})>1,
    'root_gate_inputs':cone.gate_inputs[root],'root_external_inputs':external,'root_source_anchor':root_is_source,
    'mandatory_root_by_direct_path':root_is_source,'independent_min_cut':independent,
    'best_root_excluded_cut':alternative,'uniform_root_excluded_cut':uniform_alt,
    'root_exclusion_margin':alternative['value']-solved.cut_cost if alternative['finite'] else None})
  pairs.append({'circuit':c,'pair':[w,u],'weighted_rounds':len(a['candidate_pool_trace']),
   'uniform_rounds':len(b['candidate_pool_trace']),'weighted_unique_base_states':len({x['base_netlist_hash'] for x in a['candidate_pool_trace']}),
   'same_endpoint_text':a['state']['current_netlist_text']==b['state']['current_netlist_text'],
   'same_endpoint_hash':a['state']['current_netlist_hash']==b['state']['current_netlist_hash'],
   'weighted_commits':len(a['state']['accepted_patches']),'uniform_commits':len(b['state']['accepted_patches']),
   'matching':matching})

assert all(sha(R/k)==v for k,v in inputs.items())
assert all(sha(R/k)==v for k,v in sources.items())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==head
OUT.mkdir(exist_ok=False)
report={'schema':'r22-cprime-partial4-mechanism-independent-diagnostic-v1','status':'partial4, no new EDA',
 'head_before':head,'head_after':head,'eda_executed':False,'registered_parameters_changed':False,
 'input_sha256':inputs,'source_before':sources,'source_after':sources,'auditor_sha256':sha(Path(__file__)),
 'independent_solver':{'package':'networkx','version':nx.__version__,'method':'minimum_cut default preflow_push',
  'constraint_diagnostic':'Root exclusion sets only its split edge to existing INF; not an experiment-arm parameter change.'},
 'pairs':pairs,'rows':rows,'summary':{'circuits':4,'pairs':len(pairs),'weighted_trace_rows':len(rows),
  'root_singletons':sum(x['selected_is_root_singleton'] for x in rows),
  'mandatory_root_rows':sum(x['mandatory_root_by_direct_path'] for x in rows),
  'finite_nonroot_alternatives':sum(x['best_root_excluded_cut']['finite'] for x in rows),
  'unique_circuit_base_states':len(cone_cache)}}
with (OUT/'DIAGNOSTIC.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report['summary'],indent=2))
for c in ['s27','s382','s420','s641']:
 rr=[r for r in rows if r['circuit']==c]
 print(json.dumps({'circuit':c,'rows':len(rr),'unique_states':len({r['base_sha256'] for r in rr}),
  'mandatory_rows':sum(r['mandatory_root_by_direct_path'] for r in rr),
  'cost_range':[min(r['weighted_cost'] for r in rr),max(r['weighted_cost'] for r in rr)],
  'first':rr[0]},indent=2))
