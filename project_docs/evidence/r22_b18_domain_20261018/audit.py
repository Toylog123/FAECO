"""Read-only b18 LOGIC0 source/interface audit. No EDA or source rewriting."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re,sys,difflib,subprocess

R=Path.cwd();D=R/'project_docs/evidence/r22_b18_domain_20261018'
D.mkdir(exist_ok=False)
sys.path.insert(0,str(R/'code/src'))
from rseco.logic_rewrite import _pin_blocks
paths={
 'bench':R/'data/raw/benchmarks/raw/itc99/bench/b18.bench',
 'root_blif':R/'data/raw/benchmarks/raw/itc99/b18.blif',
 'bench_blif':R/'data/raw/benchmarks/raw/itc99/bench/b18.blif',
 'preconverted_verilog':R/'data/raw/benchmarks/raw/itc99/v/b18.v',
 'base':R/'experiments/20260805_phys_closure/b18_light/b18/mapped.v',
 'candidate':R/'experiments/20260805_phys_closure/b18_light/b18/eval/iter009_cand009/029__649725__R/mapped.v',
 'map_script':R/'experiments/20260805_phys_closure/b18_light/b18/map.ys',
 'map_log':R/'experiments/20260805_phys_closure/b18_light/b18/map.log',
 'sta_tcl':R/'experiments/20260805_phys_closure/b18_light/b18/sta.tcl',
 'raw_source_manifest':R/'data/raw/benchmarks/source_manifests/itc99.json',
 'bench_converter':R/'code/scripts/convert_itc99_bench_to_blif.py',
 'verilog_converter':R/'code/scripts/convert_itc99_blif_to_v.py',
 'historical_family_review':R/'project_docs/evidence/r22_spef_audit_20261016/review_20261018/REVIEW.json',
 'static_report':R/'project_docs/evidence/r22_spef_topology_repair_20261018/FINAL_ACTUAL_INPUT_STATIC_CHECK.json',
 'lib':R/'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
before={name:{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for name,p in paths.items()}
text={name:p.read_text(encoding='utf-8-sig',errors='replace') for name,p in paths.items()}
assert before['base']['sha256']=='c5c89e3a218557797b9c6868a95b1ffea22f0cf324a7d188bf4d5f669bb5ed33'
assert before['candidate']['sha256']=='42db3970ed14ba9d99689f5489a1db4cc3074b209c5374b55749fd0a3367e10c'
excerpts={}
for name,value in text.items():
 if name=='lib':continue
 lines=value.splitlines()
 numbers={i for i,line in enumerate(lines) if re.search(r'\bLOGIC0\b',line)}
 if name in {'map_script','sta_tcl'}:numbers=set(range(len(lines)))
 excerpts[name]=[{'line':i+1,'text':lines[i]} for i in sorted(numbers)]
bench_rows=[line for line in text['bench'].splitlines() if 'LOGIC0' in line]
blif=text['root_blif']
blif_inputs=next(line.split()[1:] for line in blif.splitlines() if line.startswith('.inputs '))
blif_outputs=next(line.split()[1:] for line in blif.splitlines() if line.startswith('.outputs '))
blif_drivers=[line for line in blif.splitlines() if (line.startswith('.names ') and line.split()[-1]=='LOGIC0') or
             (line.startswith('.latch') and len(line.split())>2 and line.split()[2]=='LOGIC0')]
lib=text['lib']
def cell_block(cell):
 match=re.search(r'\bcell\s*\(\s*"'+re.escape(cell)+r'"\s*\)\s*\{',lib)
 assert match,cell
 pos=match.end();depth=1
 while depth:
  if lib[pos]=='{':depth+=1
  elif lib[pos]=='}':depth-=1
  pos+=1
 return lib[match.end():pos-1]
def connectivity(key):
 s=text[key];rows=[]
 for m in re.finditer(r'(?ms)^\s*(sky130_fd_sc_hd__[\w$]+)\s+([\w$]+)\s*\((.*?)\)\s*;',s):
  for pin,net in re.findall(r'\.([\w$]+)\s*\(\s*([^()]+?)\s*\)',m.group(3)):
   if net!='LOGIC0':continue
   blocks=dict(_pin_blocks(cell_block(m.group(1))));body=blocks[pin]
   direction=re.search(r'\bdirection\s*:\s*"?(\w+)"?\s*;',body).group(1)
   rows.append({'cell_type':m.group(1),'instance':m.group(2),'pin':pin,'direction':direction,
                'instance_start_line':s.count('\n',0,m.start())+1,'pin_body':body.strip()})
 return {'top_declared_direction':'inout' if re.search(r'\binout\s+LOGIC0\s*;',s) else 'unknown',
  'occurrence_lines':excerpts[key],'connections':rows,'internal_output_or_inout_connections':[x for x in rows if x['direction']!='input'],
  'direct_assign_driver_count':len(re.findall(r'\bassign\s+LOGIC0\s*=',s)),
  'contains_tran_or_bidirectional_primitive':bool(re.search(r'\b(?:tran|rtran|tranif[01]|rtranif[01])\b',s))}
base=connectivity('base');candidate=connectivity('candidate')
assert len(base['connections'])==len(candidate['connections'])==4
assert not base['internal_output_or_inout_connections'] and not candidate['internal_output_or_inout_connections']
assert not blif_drivers
diff=list(difflib.unified_diff(text['base'].splitlines(),text['candidate'].splitlines(),fromfile='baseline',tofile='unique_R_candidate',n=2))
manifest=json.loads(text['raw_source_manifest']);declared=next(x['sha256'] for x in manifest['circuits'] if x['id']=='b18')
family=next(x for x in json.loads(text['historical_family_review'])['physical_ledger_summary'] if 'b18_light' in x['folder'])
after={name:{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for name,p in paths.items()}
assert before==after
result={'schema':'b18-logic0-readonly-domain-audit-v1','client_date':'2026-10-18','created_actual_utc':datetime.now(timezone.utc).isoformat(),
 'EDA_executed':False,'source_or_input_modified':False,'source_before':before,'source_after':after,'source_stable':True,
 'bench':{'pseudo_input_note':bench_rows[0],'input':bool(re.search(r'^INPUT\(LOGIC0\)',text['bench'],re.M)),
          'output':bool(re.search(r'^OUTPUT\(LOGIC0\)',text['bench'],re.M)),
          'driver_definition_count':len(re.findall(r'^LOGIC0\s*=',text['bench'],re.M)),
          'consumer_gate_count':len([line for line in bench_rows if not line.startswith(('#','INPUT','OUTPUT'))])},
 'blif':{'logic0_is_input':'LOGIC0' in blif_inputs,'logic0_is_output':'LOGIC0' in blif_outputs,
         'logic0_internal_drivers':blif_drivers,'root_and_bench_blif_bytes_equal':before['root_blif']['sha256']==before['bench_blif']['sha256'],
         'current_root_blif_sha256':before['root_blif']['sha256'],'acquisition_manifest_b18_sha256':declared,
         'current_matches_acquisition_manifest':before['root_blif']['sha256']==declared},
 'preconverted_verilog':{'inout_declaration':bool(re.search(r'\binout\s+LOGIC0\s*;',text['preconverted_verilog'])),
   'direct_assign_logic0_driver_count':len(re.findall(r'\bassign\s+LOGIC0\s*=',text['preconverted_verilog']))},
 'baseline':base,'unique_candidate':candidate,'net_connectivity_identical':base['connections']==candidate['connections'],
 'mapper_script':text['map_script'],'mapping_has_logic0_setundef_tieoff_or_direction_rewrite':bool(re.search(r'LOGIC0|setundef|hilomap|setattr.*port',text['map_script'])),
 'pair_diff':diff,'historical_family':family,
 'bounded_conclusion':'The retained benchmark interface exposes LOGIC0 as an external pseudo-input and simultaneously a same-named output. Both actual mapped objects preserve that inout interface, with four Liberty-input loads and no observed internal driver/assign/switch. Existing evidence does not justify a constant-0 tie or interface rewrite.',
 'unknowns':['Original EDIF source is not present in inspected local raw tree; any physical ground/constant intent before edf2bench remains unknown.',
  'The acquisition BLIF SHA may differ from current reconstructed complete BLIF; explicit equality field above bounds provenance. No converter run receipt ties current BLIF to current Verilog byte-for-byte, so conversion path is reconstructed from content/scripts, not claimed newly proved.',
  'Passive *P B support and actual OpenSTA annotation acceptance are proposed but untested; external excitation/load assumptions must be explicit before valid timing comparison.'],
 'excerpts':excerpts,'audit_script_sha256':sha(Path(__file__))}
with (D/'AUDIT.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
with (D/'pair.diff').open('x',encoding='utf-8') as f:f.write('\n'.join(diff)+'\n')
with (D/'audit.py').open('xb') as f:f.write(Path(__file__).read_bytes())
print(json.dumps({'source_stable':True,'bench':result['bench'],'blif':result['blif'],'baseline_connections':base['connections'],
 'net_connectivity_identical':result['net_connectivity_identical'],'diff_line_count':len(diff),'AUDIT_sha256':sha(D/'AUDIT.json')},ensure_ascii=False,indent=2))
