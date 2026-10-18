"""Read-only independent QA of actual retained micro OpenSTA artifacts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re
R=Path.cwd();B=R/'project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding'
O=B/'independent_review';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def identity(p):return {'sha256':sha(p),'bytes':Path(p).stat().st_size}
def wsl(p):
 s=str(Path(p).resolve());return '/mnt/'+s[0].lower()+'/'+s[3:].replace('\\','/')
files=[p for p in B.rglob('*') if p.is_file() and not p.is_relative_to(O)]
before={p.relative_to(R).as_posix():identity(p) for p in files}
result=read(B/'RESULT.json');accept=read(B/'ROOT_ACCEPTANCE.json');prereg=read(B/'PRE_REGISTER.json')
assert sha(B/'RESULT.json')==accept['result_sha256']
assert prereg['sources']==result['source_before']==result['source_after'] and result['source_stable']
source_current={n:sha(R/n) for n in result['source_before']}
assert source_current==result['source_before']
for name,h in result['artifacts'].items():assert sha(B/name)==h,name
positive=[x for x in result['cases'] if 'length_um' in x]
negative=[x for x in result['cases'] if x['case'].endswith('_missing_pin')]
assert len(positive)==4 and len(negative)==2
expected={(case,length) for case in ['ordinary','escaped'] for length in [40,4000]}
assert {(x['case'],x['length_um']) for x in positive}==expected
lib=next(Path(n) for n in source_current if n.endswith('.lib'))
def metrics(raw):
 patterns={'slack':r'(-?\d+\.\d+)\s+slack \(([A-Z]+)\)',
  'wns':r'worst slack max\s+(-?\d+\.\d+)',
  'tns':r'tns\s+max\s+(-?\d+\.\d+)',
  'min_slack':r'worst slack min\s+(-?\d+\.\d+)'}
 out={}
 for key,pattern in patterns.items():
  m=re.search(pattern,raw);assert m,key
  out[key]=float(m.group(1))
  if key=='slack':out['slack_status']=m.group(2)
 out['min_slack_status']='MET' if out['min_slack']>=0 else 'VIOLATED'
 return out
def command_check(tcl,mapped,spef,*,annotation=False):
 lines=tcl.splitlines()
 assert lines.count('read_liberty '+wsl(lib))==1
 assert lines.count('read_verilog '+wsl(mapped))==1
 assert lines.count('read_spef '+wsl(spef))==1
 assert 'link_design top' in lines
 assert 'create_clock -name clk -period 5 [get_ports CK]' in lines
 read_pos=lines.index('read_spef '+wsl(spef))
 assert all(i>read_pos for i,line in enumerate(lines) if line.startswith('report_'))
 if annotation:assert lines.count('report_parasitic_annotation -report_unannotated')==1
 return {'liberty_netlist_spef_exact_paths_match':True,'clock_top_period_match':True,'all_reports_after_read_spef':True}
def nets(spef):
 return {m.group(1):set(re.findall(r'^\*I\s+(\S+)\s+([IOB])$',m.group(2),re.M))
  for m in re.finditer(r'^\*D_NET\s+(\S+)\s+[^\n]+\n(.*?)(?=^\*END)',spef,re.M|re.S)}
rows=[]
for row in positive:
 name,length=row['case'],row['length_um'];d=B/name/str(length);mapped=B/name/'mapped.v';spef=d/'net.spef'
 api_log=(d/'measurement/sta.log').read_text();api_tcl=(d/'measurement/sta.tcl').read_text()
 rawout=(d/'annotation.stdout.bin').read_bytes();rawerr=(d/'annotation.stderr.bin').read_bytes()
 annotation_log=(d/'annotation.log').read_text()
 assert annotation_log==rawout.decode('utf-8',errors='replace')+'\n'+rawerr.decode('utf-8',errors='replace')
 annotation_tcl=(d/'annotation.tcl').read_text()
 assert annotation_tcl==api_tcl.replace('report_checks -path_delay max\n','report_parasitic_annotation -report_unannotated\nreport_checks -path_delay max\n',1)
 assert row['annotation_returncode']==0 and row['annotation_error'] is None
 assert 'Found 0 unannotated drivers.' in annotation_log and 'Found 0 partially unannotated drivers.' in annotation_log
 assert not re.search(r'^\s*(?:Error(?:\s+\d+)?(?:\s*:|\s+)|Warning\s+(?:1647|1652):)',annotation_log,re.M)
 observed=metrics(api_log);assert observed==row['result'] and metrics(annotation_log)==observed
 links=nets(spef.read_text())
 bus,literal=('q[0]',r'q\[0\]') if name=='escaped' else ('qvec','qlit')
 assert set(links)=={'A','CK','Z',bus,literal}
 assert links[bus]=={('f0:Q','O'),('b0:A','I')}
 assert links[literal]=={('b0:X','O'),('f1:D','I')}
 rows.append({'case':name,'length_um':length,'observed_metrics':observed,
  'api_tcl':command_check(api_tcl,mapped,spef),
  'annotation_tcl':command_check(annotation_tcl,mapped,spef,annotation=True),
  'annotation_argv_matches_tcl':row['annotation_argv']==['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',wsl(d/'annotation.tcl')],
  'annotation_log_matches_raw_streams':True,'zero_unannotated_drivers':True,'zero_partially_unannotated_drivers':True,
  'distinct_internal_net_endpoint_sets':{bus:sorted(links[bus]),literal:sorted(links[literal])},
  'raw_stderr_has_wsl_path_translation_messages':b'Failed to translate' in rawerr,
  'artifact_bindings':{p.relative_to(B).as_posix():identity(p) for p in [mapped,spef,d/'measurement/sta.tcl',d/'measurement/sta.log',d/'annotation.tcl',d/'annotation.stdout.bin',d/'annotation.stderr.bin',d/'annotation.log']}})
 assert rows[-1]['annotation_argv_matches_tcl']
negatives=[]
for row in negative:
 name=row['case'].removesuffix('_missing_pin');d=B/name/'missing_pin_measurement';bad=B/name/'missing_pin.spef'
 assert bad.read_text()==(B/name/'40/net.spef').read_text().replace('b0:A','b0:ABSENT')
 outcome=row['result'];assert all(outcome[k] is None for k in ['wns','tns','slack','min_slack'])
 raw=(d/'sta.log').read_text();assert 'pin b0:ABSENT not found' in raw and 'pin b0:ABSENT not found' in outcome['error']
 receipt=read(R/outcome['failure_receipt_path']);assert receipt['valid'] is False and receipt['returncode']==0
 for field,expected in [('netlist',B/name/'mapped.v'),('liberty',lib),('spef',bad)]:
  assert receipt[field]['sha256']==sha(expected) and receipt[field]['bytes']==expected.stat().st_size
 for field in ['tcl','log']:
  p=Path(receipt[field]['path']);assert sha(p)==receipt[field]['sha256'] and p.stat().st_size==receipt[field]['bytes']
  assert p.read_bytes()==(d/('sta.tcl' if field=='tcl' else 'sta.log')).read_bytes()
 command_check((d/'sta.tcl').read_text(),B/name/'mapped.v',bad)
 negatives.append({'case':name,'raw_missing_pin_diagnostic_matches_api_error':True,'api_all_numeric_metrics_null':True,
  'failure_receipt_input_and_saved_tcl_log_hashes_match':True,'receipt_sha256':sha(R/outcome['failure_receipt_path']),
  'tool_returncode_recorded_in_failure_receipt':receipt['returncode']})
for length in [40,4000]:
 pair=[x['observed_metrics'] for x in rows if x['length_um']==length];assert pair[0]==pair[1]
for name in ['ordinary','escaped']:
 a,b=[x for x in rows if x['case']==name];assert a['length_um']==40 and b['length_um']==4000 and a['observed_metrics']['wns']>b['observed_metrics']['wns']
assert accept['positive_api_attempts']==4 and accept['annotation_replay_attempts']==4 and accept['missing_pin_negative_attempts']==2
for key in ['all_sources_and_artifacts_match','all_four_annotation_replays_zero_unannotated_and_zero_partial_drivers',
 'escaped_and_ordinary_results_identical_at_each_rc','rc_increase_degrades_both_controls','both_bad_pin_cases_rejected_without_numeric_results']:
 assert accept[key] is True
tool=accept['actual_tool_identities'];assert len(tool)==2 and all(x['returncode']==0 for x in tool)
assert tool[0]['argv']==['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-version'] and tool[0]['stdout'].strip()=='3.1.0'
assert tool[1]['argv']==['wsl.exe','-d','Ubuntu','--','sha256sum','/usr/local/bin/sta']
assert re.fullmatch(r'[0-9a-f]{64}\s+/usr/local/bin/sta\s*',tool[1]['stdout'])
assert tool[1]['stdout'].split()[0]=='96833cf69282803fc44fc8cc343bfe03ad8279bab9fb276d84a6d4532e15b468'
after={p.relative_to(R).as_posix():identity(p) for p in files};assert before==after
assert source_current=={n:sha(R/n) for n in source_current}
v={'schema':'actual-spef-tiny-binding-independent-review-v1','client_date':'2026-10-18','created_actual_utc':datetime.now(timezone.utc).isoformat(),
 'decision':'accepted only within retained tiny ordinary/escaped binding controls','new_sta_or_eda_or_test_or_git_executed':False,
 'producer_evidence_modified':False,'result_sha256':sha(B/'RESULT.json'),'root_acceptance_sha256':sha(B/'ROOT_ACCEPTANCE.json'),
 'pre_register_sha256':sha(B/'PRE_REGISTER.json'),'manifest_artifact_count':len(result['artifacts']),'all_manifest_artifact_sha_match':True,
 'source_before_after_current_all_match':source_current,'positive_api_attempts_rechecked':4,'annotation_replay_attempts_rechecked':4,
 'missing_pin_negative_attempts_rechecked':2,'positive_rows':rows,'negative_rows':negatives,
 'root_acceptance_claims_independently_correspond_to_raw_artifacts':True,'tool_identity_receipts':tool,
 'tool_identity_coverage':'Recorded successful version/hash queries validated; reviewer did not relaunch WSL or re-read Linux executable bytes.',
 'reviewed_artifact_before':before,'reviewed_artifact_after':after,'all_reviewed_bytes_stable':True,
 'coverage_limits':['This verifies actual retained tiny OpenSTA binding controls, not benchmark gain or sign-off physical accuracy.',
 'RC40/4000 is a sensitivity/falsification control, not calibrated geometry or an improvement target.',
 'No s382/b18 scientific timing result, inout/tri-state support, sequential proof, scientific campaign or full regression is established here.',
 'Nonfatal WSL PATH translation stderr is present in retained replays/identity queries; it is preserved and not described as empty stderr.'],
 'review_script_sha256':sha(Path(__file__))}
p=O/'INDEPENDENT_REVIEW.json'
with p.open('x',encoding='utf-8') as stream:json.dump(v,stream,indent=2);stream.write('\n')
with (O/'review_script.py').open('xb') as stream:stream.write(Path(__file__).read_bytes())
print(json.dumps({'receipt_path':p.relative_to(R).as_posix(),'receipt_sha256':sha(p),'manifest_artifact_count':len(result['artifacts']),
 'reviewed_files':len(before),'positive_api':4,'annotation_replay':4,'negative_missing_pin':2,'source_current_and_evidence_stable':True},indent=2))
