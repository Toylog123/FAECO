import pathlib,sys,json,re
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'project_docs/evidence/recovery_qualification_20261112'))
from check_phase0_structure import Reader
out=root/'scratch/recovery_repair_pathdiag';result={}
for arm in ['CONTROL','RECOVERY_V2']:
 base=root/'project_docs/evidence/recovery_repair_20261113/inputs'/arm
 parsed=Reader((base/'routed.v').read_text()).parse()[0]
 spef=(base/'routed.spef').read_text();names=dict(re.findall(r'^(\*\d+) ([^\n]+)$',spef.split('*NAME_MAP',1)[1].split('*PORTS',1)[0],re.M));caps={names.get(n,n):float(c) for n,c in re.findall(r'^\*D_NET (\S+) ([\d.eE+-]+)',spef,re.M)}
 rows=[]
 for name,pin in [('_057_','X'),('_059_','Y'),('_060_','Y'),('_084_','Y')]:
  item=parsed['instances'][name]; expr=item['pins'][pin];assert len(expr)==1 and expr[0][0]=='id';net=expr[0][1]
  endpoints={n:{'cell':i['cell'],'pins':[p for p,v in i['pins'].items() if v==expr]} for n,i in parsed['instances'].items() if expr in i['pins'].values()}
  rows.append({'driver':name+'/'+pin,'cell':item['cell'],'net':net,'spef_wire_cap_pf':caps[net],'all_net_pin_connections':endpoints})
 result[arm]=rows
(out/'spef_pathnets.json').write_text(json.dumps(result,indent=2)+'\n')
for before,after in zip(result['CONTROL'],result['RECOVERY_V2']):print(before['driver'],before['net'],'wirecap',before['spef_wire_cap_pf'],after['spef_wire_cap_pf'],'same_pin_cell_topology',before['all_net_pin_connections']==after['all_net_pin_connections'])
