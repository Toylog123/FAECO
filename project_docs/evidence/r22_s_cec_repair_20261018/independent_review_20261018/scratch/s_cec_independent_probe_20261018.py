"""Independent receipt-binding probes. Fake process boundary only; no EDA."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, subprocess, sys
import pytest

R=Path.cwd()
sys.path.insert(0,str(R/'code/src'))
from rseco import structure_resynthesis as sr, yosys_abc as ya

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=[R/'code/src/rseco/structure_resynthesis.py',R/'code/src/rseco/yosys_abc.py',R/'code/tests/test_s_cec_evidence.py']
before={p.relative_to(R).as_posix():sha(p) for p in scope}
out=R/'scratch/s_cec_independent_probe_20261018'
out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('s_cec_existing_control',R/'code/tests/test_s_cec_evidence.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
rows=[]
for mode in ['unchanged_control','derived_model_drift','normalize_launch_error']:
 d=out/mode;d.mkdir();mp=pytest.MonkeyPatch()
 try:
  tools,commands,model=fixture.factory(d,mp,statuses=('pass',))
  reference=d/'ref.v';reference.write_text('module win(a,y); input a; output y;\nsky130_fd_sc_hd__inv_1 g (.A(a),.Y(y));\nendmodule\n')
  candidate=d/'gate.blif';candidate.write_text('.model win\n.end\n')
  boundary=subprocess.run;mutations=[]
  def process(argv,**kwargs):
   if mode=='normalize_launch_error' and argv[0]=='fake-yosys':
    raise FileNotFoundError('controlled missing normalization executable')
   result=boundary(argv,**kwargs)
   if mode=='derived_model_drift' and argv[0]=='fake-yosys':
    match=re.search(r'read_verilog\s+(?:"([^"]+)"|([^;\s]+))',argv[-1])
    if match:
     model_path=Path(match.group(1) or match.group(2))
     if model_path.name.endswith('_cells.v'):
      old=sha(model_path);model_path.write_bytes(model_path.read_bytes()+b'\n// derived model changed after tool invocation\n')
      mutations.append({'path':str(model_path),'before_sha256':old,'after_sha256':sha(model_path)})
   return result
  mp.setattr(subprocess,'run',process)
  folder=d/'proof';result=tools.cec(reference,candidate,folder)
  receipt=json.loads((folder/'receipt.json').read_text())
  rows.append({'mode':mode,'result_status':result.status,'result_reason':result.reason,'receipt_status':receipt['status'],
    'input_drift':receipt['input_drift'],'mutations':mutations,'receipt_path':(folder/'receipt.json').relative_to(R).as_posix(),
    'receipt_sha256':sha(folder/'receipt.json'),'actual_derived_artifact_sha256':receipt['artifacts'].get('cec_left_cells.v'),
    'normalize_log_exists':(folder/'cec_left.normalize.log').exists(),'command_count':len(commands)})
 finally:mp.undo()
after={p.relative_to(R).as_posix():sha(p) for p in scope};assert before==after
v={'client_date':'2026-10-18','created_actual_utc':datetime.now(timezone.utc).isoformat(),'probe_sha256':sha(Path(__file__)),
 'actual_eda_executed':False,'actual_yosys_or_abc_executed':False,'boundary_control':'existing default factory and normalization/artifact code, only subprocess mocked',
 'source_before':before,'source_after':after,'source_stable':True,'cases':rows}
with (out/'PROBE_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps(v,indent=2));print('probe_receipt_sha256',sha(out/'PROBE_RECEIPT.json'))
