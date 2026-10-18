from pathlib import Path
from dataclasses import replace
import ast,hashlib,json,subprocess,sys
import networkx as nx
R=Path(__file__).resolve().parents[2]
OUT=R/'project_docs/evidence/r22_cprime_v3_20261016/region_design_review'
sys.path[:0]=[str(R/'code/src'),str(R/'code/scripts'),str(R/'project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER')]
from backend import ActualBackend
from rseco.replacement import parse_verilog_netlist_from_text
from rseco.graph import extract_fanin_cone
from rseco.cut import _cut_for_selected_gates
native_run=subprocess.run
def no_process(*args,**kwargs):raise AssertionError('No external process permitted')
subprocess.run=no_process
try:
 b=ActualBackend('top');metadata={n:dict(c.output_functions) for n,c in b.cells.items() if c.output_functions}
 text='''module top(A,B,CIN,S,C);\ninput A,B,CIN;\noutput S,C;\nwire co;\nsky130_fd_sc_hd__fa_1 f(.A(A),.B(B),.CIN(CIN),.COUT(co),.SUM(S));\nsky130_fd_sc_hd__buf_1 consume(.A(co),.X(C));\nendmodule\n'''
 netlist=parse_verilog_netlist_from_text(text,cell_output_functions=metadata)
 cone=extract_fanin_cone(netlist,['S']);cut=_cut_for_selected_gates(cone,cone.gates,method='control')
 # Execute only the standalone independent oracle function; no census rerun.
 tree=ast.parse((Path(__file__).parent/'census.py').read_text(encoding='utf-8'))
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='region_info')
 namespace={'nx':nx};exec(compile(ast.Module(body=[node],type_ignores=[]),'region_oracle_only','exec'),namespace)
 region_info=namespace['region_info']
 good=region_info(netlist,cone,cut,[])
 bad=region_info(netlist,cone,replace(cut,boundary_outputs=['S']),[])
 positive=b.validate(text,text);negative=b.validate(text,text.replace('.COUT(co)','.COUT()'))
 assert positive['status']=='pass' and negative['status']=='fail'
 assert good['boundary_closed'] and not bad['boundary_closed'] and 'co' in cut.boundary_outputs
 census=json.loads((OUT/'census_v2/CENSUS.json').read_text(encoding='utf-8'))
 summaries=[]
 for circuit in census['circuits']:
  eligible=[r for r in circuit['regions'] if r['eligibility']]
  ties={m:sum(abs(r['node_scores'][m]-min(v['node_scores'][m] for v in eligible))<1e-12 for r in eligible) for m in ['configured','uniform']}
  assert set(circuit['rankings']['configured'])==set(circuit['rankings']['uniform'])
  assert any('singleton_control' in r['origins'] for r in circuit['regions'])
  assert any('full_critical_cover_control' in r['origins'] for r in circuit['regions'])
  summaries.append({'circuit':circuit['circuit'],'top_score_tie_counts':ties,
   'eligible_multigate_regions':sum(r['patch_size']>=2 for r in eligible),
   'checks':sum(len(i['checks']) for i in circuit['instance_witness_checks']),
   'static_pass_checks':sum(c['static_validation']['status']=='pass' for i in circuit['instance_witness_checks'] for c in i['checks']),
   'unexamined_proposals':sum(sum(i['untested_by_kind'].values()) for i in circuit['instance_witness_checks']),
   'bounded_generator_exhausted':{m:v['diagnostics']['rejected']['budget']>0 for m,v in circuit['generator_results'].items()}})
 report={'eda_executed':False,'external_process_calls':0,'multioutput_actualLib_fixture_valid_static':positive['status'],
  'secondary_output_closed_positive':good,'secondary_output_omission_rejected_by_oracle':not bad['boundary_closed'],
  'secondary_output_disconnect_rejected_by_F1_F2':negative['status'],
  'same_union_singleton_fullcover_controls_passed':True,'scope':'Fixtures only geometry/function static controls; no timing benefit',
  'circuit_audit':summaries}
 with (OUT/'STATIC_CONTROLS.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(report,indent=2))
finally:subprocess.run=native_run
