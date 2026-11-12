import json,pathlib,re,hashlib
out=pathlib.Path(__file__).resolve().parent;m=json.loads((out/'manifest.json').read_text()); swaps={x['instance'] for x in m['swaps']}
def read(arm):
 text=(out/(arm+'.log')).read_text(errors='replace'); result={}
 for mode,count in [('SETUP',10),('HOLD',5)]:
  section=text.split(f'PATHDIAG_{mode}_TOP{count}_BEGIN',1)[1].split(f'PATHDIAG_{mode}_TOP{count}_END',1)[0]
  paths=[]
  for block in re.split(r'(?=Startpoint:)',section)[1:]:
   p={k:re.search(label+r': (\S+)',block)[1] for k,label in [('startpoint','Startpoint'),('endpoint','Endpoint')]}
   for key,label in [('arrival_ns','data arrival time'),('required_ns','data required time'),('slack_ns','slack')]:
    p[key]=float(re.search(r'^\s*([-\d.]+)\s+'+label,block,re.M)[1])
   rows=[]
   for line in block.splitlines():
    match=re.match(r'^\s*([\d.\s-]+)\s+([\^v])\s+(\S+) \(([^)]+)\)',line)
    if not match:continue
    numbers=[float(x) for x in match[1].split()]
    if len(numbers) not in [3,5]:raise ValueError(line)
    row={'pin':match[3],'cell':match[4],'edge':match[2], 'slew_ns':numbers[-3],'delay_ns':numbers[-2],'time_ns':numbers[-1]}
    if len(numbers)==5:row.update(fanout=int(numbers[0]),cap_pf=numbers[1])
    rows.append(row)
   p['rows']=rows;p['swapped_instances_on_reported_path']=sorted({x['pin'].rsplit('/',1)[0] for x in rows}&swaps)
   launch=[x for x in rows if x['pin']==p['startpoint']+'/CLK'];capture=[x for x in rows if x['pin']==p['endpoint']+'/CLK']
   p['launch_clock_arrival_ns']=launch[0]['time_ns'];p['capture_clock_arrival_ns']=capture[-1]['time_ns']
   p['data_after_launch_clock_ns']=p['arrival_ns']-p['launch_clock_arrival_ns']
   paths.append(p)
  result[mode.lower()]=paths
 result['tns_ns']=float(re.search(r'PATHDIAG_TNS9_BEGIN\s+tns max ([-\d.]+)',text)[1])
 result['setup_wns_ns']=float(re.search(r'ROUTED_WNS_MAX ([^\s]+)',text)[1])*1e9
 result['hold_wns_ns']=float(re.search(r'ROUTED_WNS_MIN ([^\s]+)',text)[1])*1e9
 return result
result={arm:read(arm) for arm in m['arms']}
comparison=[]
before={p['endpoint']:p for p in result['CONTROL']['setup']}
for after in result['RECOVERY_V2']['setup']:
 if after['endpoint'] not in before:continue
 b=before[after['endpoint']];r={'endpoint':after['endpoint'],'same_startpoint':b['startpoint']==after['startpoint'],'before_swaps':b['swapped_instances_on_reported_path'],'after_swaps':after['swapped_instances_on_reported_path']}
 for k in ['arrival_ns','required_ns','slack_ns','launch_clock_arrival_ns','capture_clock_arrival_ns','data_after_launch_clock_ns']:r['delta_'+k]=round(after[k]-b[k],9)
 r['before_slack_ns']=b['slack_ns'];r['after_slack_ns']=after['slack_ns'];comparison.append(r)
result['matched_endpoint_setup_changes']=comparison
(out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
for arm in m['arms']:
 print(arm,'WNS',result[arm]['setup_wns_ns'],'TNS',result[arm]['tns_ns'])
 print([(p['endpoint'],p['slack_ns'],p['swapped_instances_on_reported_path']) for p in result[arm]['setup']])
print(json.dumps(comparison,indent=2))
