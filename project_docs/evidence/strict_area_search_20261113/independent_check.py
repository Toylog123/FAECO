from pathlib import Path
from decimal import Decimal
import copy, hashlib, importlib.util, json, math, re, sys
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'project_docs/evidence/strict_area_search_20261113'
sys.path.insert(0,str(P))
from structure_reader import Reader
sys.path.insert(0,str(P/'space_audit'))
from audit_space import parse_cells, LIB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
plan=load(P/'PLAN.json'); receipt=load(P/'SEARCH_RECEIPT.json')
assert sha(P/'PLAN.json')==receipt['plan_sha256']=='2efbac2bfaf603fd2814e1e1ba00e0c6254dc7e5aeaf1c314f3fe169b5fcf45e'
for name,h in plan['source_sha256'].items():assert sha(P/name)==h,name
control=Reader((P/'inputs/CONTROL/routed.v').read_text()).parse()[0]
recipe=load(P/'inputs/recipe.json')['applied']
families={re.sub(r'_\d+$','',x['cell']) for x in control['instances'].values()}
cells,_=parse_cells(LIB.read_text(),families)
ERR=re.compile(r'(?im)^.*(?:Error:|\[ERROR|invalid command name|wrong # args|failed to).*$')
def metrics(path,marker):
 raw=path.read_text(encoding='utf-8',errors='replace').replace('\x00','')
 assert marker in raw and not ERR.search(raw),path
 out={}
 for k,token in [('setup_ns','ROUTED_WNS_MAX'),('hold_ns','ROUTED_WNS_MIN')]:
  v=re.findall(token+r'\s+([-+\d.eE]+)',raw);assert len(v)==1,(path,token);out[k]=float(v[0])*1e9
 t=re.findall(r'^tns max\s+([-+\d.eE]+)',raw,re.M);assert t and len(t[-1].split('.')[-1])>=9
 out['tns_ns']=float(t[-1]);assert all(math.isfinite(x) for x in out.values())
 return out,raw
ref,_=metrics(P/'pathdiag/CONTROL.log','PATHDIAG_TNS9_END');assert ref==plan['control']['metrics']
seed=plan['seed']; measured={}; result=[]
for row in receipt['rows']:
 arm=row['arm']; folder=P/'runs'/arm; manifest=load(folder/'manifest.json')
 assert row['status'].startswith('validated_'),row
 job=next(x for x in receipt['jobs'] if x['arm']==arm); assert job['returncode']==0
 extra=arm.split('_')[-1]; wanted={'_096_',f'_{extra}_'}
 expected=copy.deepcopy(control)
 for r in recipe:
  assert expected['instances'][r['instance']]['cell']==r['new_cell']
  if r['instance'] in wanted:expected['instances'][r['instance']]['cell']=r['old_cell']
 actual=Reader((folder/'routed.v').read_text()).parse()[0];assert expected==actual,arm
 for name,h in row['output_sha256'].items():assert sha(folder/name)==h,(arm,name)
 for name,h in manifest['input_sha256'].items():assert sha(ROOT/name)==h,(arm,name)
 flow=(folder/'flow.tcl').read_text(); log=(folder/'flow.log').read_text(errors='replace')
 assert 'PHYSICAL_PROBE_OK' in log and not ERR.search(log) and manifest['flow']['returncode']==0
 assert sha(folder/'flow.tcl')==manifest['tcl_sha256']
 assert re.findall(r'^replace_cell (\S+) (\S+)',flow,re.M)==[(r['instance'],r['old_cell']) for r in recipe if r['instance'] in wanted]
 assert 'odb::dbWire_destroy $wire' in flow and 'extract_parasitics -ext_model_file' in flow
 assert not (folder/'drc.rpt').read_text().strip() and manifest['drc_count']==0
 assert 'write_spef' in flow and str(folder/'routed.spef').replace('\\','/').replace('D:','/mnt/d') in flow
 spef=(folder/'routed.spef').read_text();assert '*DESIGN "s382"' in spef and '*D_NET' in spef and '*CAP' in spef
 total=Decimal(0)
 for name,entry in actual['instances'].items():
  if entry['cell']=='sky130_fd_sc_hd__tapvpwrvgnd_1':assert not entry['pins']
  else:total+=cells[entry['cell']]['area']
 assert float(total)==row['area']==next(c['area'] for c in plan['candidates'] if c['candidate_id']==arm)
 for clock in ['ideal','propagated']:
  m,raw=metrics(folder/(clock+'.log'),'ROUTED_STA_OK');assert m==row['metrics'][clock]
  assert manifest[clock]['returncode']==0
  tcl=(folder/(clock+'.tcl')).read_text()
  for name in ['routed.v','routed.spef']:
   assert str(folder/name).replace('\\','/').replace('D:','/mnt/d') in tcl
  assert ('set_propagated_clock [all_clocks]' in tcl)==(clock=='propagated')
  assert 'report_check_types -max_slew -max_capacitance -violators -digits 9' in tcl
  drv=re.search(r'ROUTED_STA_OK([\s\S]*?)worst slack min',raw);assert drv and 'VIOLATED' not in drv.group(1)
  assert 'Startpoint:' in raw and 'Endpoint:' in raw
 delta={k:m[k]-ref[k] for k in ref}; saved=Decimal(str(plan['control']['area']))-total
 feasible=all(v>=-1e-6 for v in delta.values()) and m['hold_ns']>=0 and saved>0
 assert feasible==row['primary_numeric_pass']
 info={'arm':arm,'area':str(total),'area_saved':str(saved),'delta_ns':delta,'strict':feasible,
       'deficits_ns':{k:max(0,-v-1e-6) for k,v in delta.items()},'netlist_sha256':sha(folder/'routed.v'),'spef_sha256':sha(folder/'routed.spef')}
 result.append(info); measured[arm]=info
out={'receipt_status':receipt['status'],'completed_independently_checked':len(result),'rows':result,
     'independent_checker_sha256':sha(Path(__file__)), 'plan_sha256':sha(P/'PLAN.json'),
     'receipt_sha256':sha(P/'SEARCH_RECEIPT.json'), 'all_frozen_sources_match':True,
     'author_selection_imported':False, 'scope':'complete structural and raw endpoint evidence audit, independent strict gate and prefix replay; no new EDA or SEC'}
if receipt['status']=='all9_finished':
 assert len(measured)==9 and receipt['actual_new_cost']=={'charged_verifications':9,'completed_routes':9,'completed_sta':18}
 traces={}
 for name,order in plan['orders'].items():
  best=seed['candidate_id'];best_save=Decimal(str(plan['control']['area']))-Decimal(str(seed['area']));trace=[]
  for k,arm in enumerate(order,1):
   r=measured[arm];saved=Decimal(r['area_saved'])
   if r['strict'] and (saved>best_save or (saved==best_save and arm<best)):best,best_save=arm,saved
   author=receipt['traces'][name][k-1]
   assert author['visited']==arm and author['charged_verifications']==k
   assert author['selected']['candidate_id']==best and Decimal(str(author['best_area_saved']))==best_save
   expected_point=seed if best==seed['candidate_id'] else receipt['points'][best]
   assert author['selected']==expected_point
   for endpoint in expected_point['endpoint'].values():assert sha(P/endpoint['path'])==endpoint['sha256']
   if k in (1,3,6,9):trace.append({'k':k,'best':best,'saving':str(best_save)})
  traces[name]=trace
 assert traces['area_first'][-1]==traces['timing_risk'][-1]
 assert receipt['selected']['candidate_id']==traces['area_first'][-1]['best']
 out['independent_checkpoints']=traces
 out['routes_sta']='9 routes / 18 STA; both orderings replay shared actual endpoints'
print(json.dumps(out,indent=2))

