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
plan=load(P/'PLAN.json'); variant=load(P/'VARIANT_PLAN.json'); receipt=load(P/'VARIANT_RECEIPT.json')
assert sha(P/'VARIANT_PLAN.json')==receipt['plan_sha256']=='e600cd53f9899d179152d6c84c0cc84476a96998f7e4f117d7f1b4fc4772c7f7'
for name,h in variant['source_sha256'].items():assert sha(P/name)==h,name
assert sha(P/'SEARCH_SUMMARY.json')==receipt['original_search_summary_sha256']
for name,h in plan['source_sha256'].items():assert sha(P/name)==h,name
control=Reader((P/'inputs/CONTROL/routed.v').read_text()).parse()[0]
recipe=load(P/'VARIANT_RECIPE.json')['applied']
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
 wanted=set(variant['targets'][arm])
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
 assert float(total)==row['area']==variant['exact_area'][arm]['area']
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
     'receipt_sha256':sha(P/'VARIANT_RECEIPT.json'), 'variant_plan_sha256':sha(P/'VARIANT_PLAN.json'), 'all_frozen_sources_match':True,
     'author_selection_imported':False, 'scope':'complete structural and raw endpoint evidence audit, independent strict gate and prefix replay; no new EDA or SEC'}

if receipt['status']=='all2_finished':
 assert len(measured)==2 and receipt['actual_new_cost']=={'charged_verifications':2,'completed_routes':2,'completed_sta':4}
 prior=load(P/'labels/provenance/FORWARD_SUMMARY.json')
 pair=load(P/'SEARCH_SUMMARY.json')
 comparisons=[]
 for arm,previous_arm,previous_dir,source in [('VARIANT_054_2','FORWARD__054_','labels/singletons/FORWARD__054_',prior),('VARIANT_096_054_2','PAIR_096_054','runs/PAIR_096_054',pair)]:
  row=next(r for r in source['rows'] if r['arm']==previous_arm)
  for name,h in row['output_sha256'].items():assert sha(P/previous_dir/name)==h,(previous_arm,name)
  old_m,_=metrics(P/previous_dir/'propagated.log','ROUTED_STA_OK')
  new_m,_=metrics(P/'runs'/arm/'propagated.log','ROUTED_STA_OK')
  assert old_m==row['metrics']['propagated']
  assert Decimal(str(row['area']))==Decimal(measured[arm]['area'])
  comparisons.append({'variant':arm,'historical_equal_area_comparator':previous_arm,'area':measured[arm]['area'],
                      'variant_minus_comparator_ns':{k:new_m[k]-old_m[k] for k in old_m},
                      'variant_strict':measured[arm]['strict'], 'comparator_strict':row['primary_numeric_pass']})
 best=seed['candidate_id']; saving=Decimal(str(plan['control']['area']))-Decimal(str(seed['area']))
 for arm in variant['measurement_order']:
  row=measured[arm];candidate_saving=Decimal(row['area_saved'])
  if row['strict'] and (candidate_saving>saving or (candidate_saving==saving and arm<best)):
   best,saving=arm,candidate_saving
 assert receipt['selected']['candidate_id']==best
 expected_point=seed if best==seed['candidate_id'] else receipt['points'][best]
 assert receipt['selected']==expected_point
 for endpoint in expected_point['endpoint'].values():assert sha(P/endpoint['path'])==endpoint['sha256']
 out['paired_comparisons']=comparisons
 out['independent_selected']={'candidate_id':best,'saving':str(saving)}
 out['routes_sta']='2 routes / 4 STA; separate from nine-pair study'
print(json.dumps(out,indent=2))
