"""Read-only attribution: archived paths, full structure, SPEF and Liberty tables."""
import copy,hashlib,json,pathlib,re,sys
R=pathlib.Path.cwd();H=R/'project_docs/evidence/recovery_repair_20261113';O=H/'pathdiag'
sys.path[:0]=[str(H),str(R/'code/src'),str(R/'code/scripts')]
import analyze_repair as audit
from structure_reader import Reader
from rseco.logic_rewrite import _pin_blocks,_LIBERTY_BRACE_RE
from run_sequential_timing_check import LIB
BASE='COMBO_054_074_093_098_111'; arms=[BASE,'JOINT_057','JOINT_083','JOINT_REBUFFER1']
extras={'JOINT_057':'_057_','JOINT_083':'_083_','JOINT_REBUFFER1':'rebuffer1'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def paths(arm):
 text=(H/'runs'/arm/'propagated.log').read_text(errors='replace'); result=[]
 for b in re.split(r'(?=Startpoint:)',text)[1:]:
  if 'Path Type: max' not in b:continue
  start=re.search(r'Startpoint: (\S+)',b)[1];end=re.search(r'Endpoint: (\S+)',b)[1]
  nodes=[dict(pin=m[3],cell=m[4],delay_ns=float(m[1]),time_ns=float(m[2])) for m in re.finditer(r'^\s*([-\d.]+)\s+([-\d.]+)\s+[\^v]\s+(\S+) \(([^)]+)\)',b,re.M)]
  result.append(dict(startpoint=start,endpoint=end,slack_ns=float(re.search(r'^\s*([-\d.]+)\s+slack',b,re.M)[1]),arrival_ns=float(re.search(r'^\s*([-\d.]+)\s+data arrival time',b,re.M)[1]),required_ns=float(re.search(r'^\s*([-\d.]+)\s+data required time',b,re.M)[1]),launch_clock_ns=next(n['time_ns'] for n in nodes if n['pin']==start+'/CLK'),capture_clock_ns=[n['time_ns'] for n in nodes if n['pin']==end+'/CLK'][-1],nodes=nodes))
 return result
parsed={a:Reader((H/'runs'/a/'routed.v').read_text()).parse()[0] for a in arms}
result={'inputs_sha256':{str(p.relative_to(R)):sha(p) for a in arms for p in [H/'runs'/a/'routed.v',H/'runs'/a/'routed.spef',H/'runs'/a/'propagated.log',H/'runs'/a/'propagated.tcl',H/'runs'/a/'manifest.json']},'structure_checks':{},'paths':{a:paths(a) for a in arms},'paired_endpoints':{},'spef_caps':{},'arc_tables':{}}
for p in [LIB,H/'JOINT_SUMMARY.json',H/'JOINT_PLAN.json',H/'JOINT_RECIPE.json',H/'physical_probe_joint.py',H/'analyze_repair.py',H/'structure_reader.py']:
 result['inputs_sha256'][str(p.relative_to(R))]=sha(p)
result['input_checks']={}
for arm in arms:
 manifest=json.loads((H/'runs'/arm/'manifest.json').read_text())
 assert all(sha(R/path)==digest for path,digest in manifest['input_sha256'].items())
 script=(H/'runs'/arm/'propagated.tcl').read_text()
 assert all(audit._to_sta_path(H/'runs'/arm/name) in script for name in ['routed.v','routed.spef'])
 assert 'set_propagated_clock [all_clocks]' in script
 result['input_checks'][arm]={'manifest_input_hashes_unchanged':True,'STA_uses_own_final_netlist_and_SPEF':True,'propagated_clock':True}
base=parsed[BASE]
for arm,instance in extras.items():
 expected=copy.deepcopy(base);expected['instances'][instance]['cell']=parsed[arm]['instances'][instance]['cell']
 assert expected==parsed[arm]
 result['structure_checks'][arm]={'exactly_one_cell_type_changed_vs_base':True,'instance':instance,'before':base['instances'][instance]['cell'],'after':parsed[arm]['instances'][instance]['cell'],'other_complete_structure_equal':True}
 bpaths={p['endpoint']:p for p in result['paths'][BASE]};rows=[]
 for p in result['paths'][arm]:
  if p['endpoint'] not in bpaths:continue
  b=bpaths[p['endpoint']];row={'endpoint':p['endpoint'],'same_start':p['startpoint']==b['startpoint'],'changes_ns':{k:round(p[k]-b[k],12) for k in ['slack_ns','arrival_ns','required_ns','launch_clock_ns','capture_clock_ns']},'stage_delay_changes_ns':{}}
  for pin in ['DFF_20/_0_/Q','_057_/X','_083_/X','rebuffer1/X','_067_/Y','_059_/Y']:
   old=next((n for n in b['nodes'] if n['pin']==pin),None);new=next((n for n in p['nodes'] if n['pin']==pin),None)
   if old and new:row['stage_delay_changes_ns'][pin]={'base':old['delay_ns'],'joint':new['delay_ns'],'delta':round(new['delay_ns']-old['delay_ns'],12)}
  rows.append(row)
 result['paired_endpoints'][arm]=rows
for arm in arms:
 s=(H/'runs'/arm/'routed.spef').read_text();names=dict(re.findall(r'^(\*\d+) ([^\n]+)$',s.split('*NAME_MAP',1)[1].split('*PORTS',1)[0],re.M));caps={names.get(n,n):float(c) for n,c in re.findall(r'^\*D_NET (\S+) ([\d.eE+-]+)',s,re.M)}
 result['spef_caps'][arm]={net:caps[net] for net in ['C1VCO0','_015_','_035_','net1']}
def body(text,start):
 depth=1
 for token in _LIBERTY_BRACE_RE.finditer(text,start):
  if token[0]=='{':depth+=1
  elif token[0]=='}':
   depth-=1
   if not depth:return text[start:token.start()]
 raise ValueError('Unclosed block')
libtext=LIB.read_text()
for cell in ['sky130_fd_sc_hd__o31a_1','sky130_fd_sc_hd__o31a_2']:
 m=re.search(r'cell\s*\("'+cell+r'"\)\s*\{',libtext);block=body(libtext,m.end());pins=dict(_pin_blocks(block));arcs=[]
 for t in re.finditer(r'timing\s*\([^)]*\)\s*\{',pins['X']):
  b=body(pins['X'],t.end())
  if re.search(r'related_pin\s*:\s*"A3"',b):arcs.append(b)
 assert len(arcs)==1
 b=arcs[0];m=re.search(r'cell_fall\s*\([^)]*\)\s*\{',b);table=body(b,m.end())
 indices={key:[float(x) for x in re.search(key+r'\("([^\"]+)"\)',table)[1].split(',')] for key in ['index_1','index_2']}
 raw_values=re.search(r'values\((.*?)\);',table,re.S)[1];values=[[float(v) for v in row.split(',')] for row in re.findall(r'"([^\"]+)"',raw_values)]
 result['arc_tables'][cell]=dict(input_pin='A3',output_pin='X',sense='positive_unate',transition='fall',**indices,values_ns=values,A3_input_cap_pf=float(re.search(r'\bcapacitance\s*:\s*([\d.eE+-]+)',pins['A3'])[1]))
 mt=re.search(r'fall_transition\s*\([^)]*\)\s*\{',b);tr=body(b,mt.end())
 result['arc_tables'][cell]['fall_transition_ns']=[[float(v) for v in row.split(',')] for row in re.findall(r'"([^\"]+)"',re.search(r'values\((.*?)\);',tr,re.S)[1])]
# Explicit arithmetic comparison at common input slew and output capacitance;
# this is not an actual STA operating-point reconstruction.
x=.0531329;y=.0223314;example={}
for cell,t in result['arc_tables'].items():
 i=t['index_1'].index(x);ys=t['index_2'];j=next(j for j in range(len(ys)-1) if ys[j]<=y<=ys[j+1]);v=t['values_ns'][i]
 example[cell]={'cell_fall_ns':v[j]+(v[j+1]-v[j])*(y-ys[j])/(ys[j+1]-ys[j]), 'fall_transition_ns':t['fall_transition_ns'][i][j]+(t['fall_transition_ns'][i][j+1]-t['fall_transition_ns'][i][j])*(y-ys[j])/(ys[j+1]-ys[j])}
result['illustrative_equal_slew_load_arc_comparison']={'input_slew_ns':x,'load_pf':y,'delay_ns':example,'method':'one-dimensional linear interpolation on exact common slew row; not measured operating point'}
(O/'JOINT_ATTRIBUTION_EVIDENCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['paired_endpoints'],indent=2));print('CAPS',result['spef_caps']);print('COMMON_LIB',example)
