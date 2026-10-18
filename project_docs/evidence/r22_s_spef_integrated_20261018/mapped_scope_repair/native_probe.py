"""Small native correctness controls only; no scientific campaign."""
from pathlib import Path
import sys,json,hashlib,os,subprocess
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'code/src'))
os.environ['PATH']=';'.join([r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib',os.environ.get('PATH','')])
from rseco.yosys_abc import check_mapped_blif_equivalence,run_yosys_abc_resynthesis_baseline,_abc_status_from_output
OUT=ROOT/'project_docs/evidence/r22_s_spef_integrated_20261018/mapped_scope_repair/native_post';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['code/src/rseco/yosys_abc.py','code/src/rseco/verilog_modules.py','code/tests/test_cec_blif_scope.py','code/tests/test_yosys_abc_flow.py']
before={n:sha(ROOT/n) for n in paths}
for n in paths:(OUT/('source_'+Path(n).name)).write_bytes((ROOT/n).read_bytes())
original=OUT/'original.v';original.write_text('module ztop(input A,output Y); assign Y=A; endmodule\n')
identity='.model ztop\n.inputs A\n.outputs Y\n.names A Y\n1 1\n.end\n';inverter=identity.replace('1 1','0 1');dummy=identity.replace('ztop','dummy')
hierarchy='.model helper\n.inputs A\n.outputs Y\n.names A Y\n1 1\n.end\n.model ztop\n.inputs A\n.outputs Y\n.subckt helper A=A Y=Y\n.end\n'
args={'yosys_command':'C:/oss-cad-suite-build/oss-cad-suite/bin/yosys.exe','abc_command':'C:/oss-cad-suite-build/oss-cad-suite/bin/yosys-abc.exe','timeout_s':15}
rows=[]
for name,text,top,expected in [('single_identity',identity,None,'pass'),('single_inverter',inverter,None,'fail'),('dummy_then_inverter',dummy+inverter,None,'error'),('inverter_then_dummy',inverter+dummy,None,'error'),('explicit_ztop',dummy+inverter,'ztop','fail'),('explicit_missing',identity,'missing','error'),('reachable_helper_first',hierarchy,None,'pass')]:
 p=OUT/(name+'.blif');p.write_text(text)
 r=check_mapped_blif_equivalence(original,p,artifact_dir=OUT/name,mapped_top_module=top,**args)
 rows.append({'case':name,'input_sha256':sha(p),'expected':expected,'result':r.to_dict()});assert r.status==expected,(name,r.to_dict())
 print(name,r.status,flush=True)
r=run_yosys_abc_resynthesis_baseline(original,output_dir=OUT/'baseline',**args);assert r.status=='success',r.to_dict()
command=[args['abc_command'],'-c','cec definitely_missing_left.blif definitely_missing_right.blif']
p=subprocess.run(command,capture_output=True,text=True,timeout=15)
(OUT/'native_input_error.stdout.log').write_text(p.stdout);(OUT/'native_input_error.stderr.log').write_text(p.stderr)
assert p.returncode==0 and _abc_status_from_output(p.stdout+'\nNetworks are equivalent',0)=='error'
after={n:sha(ROOT/n) for n in paths};assert before==after
report={'scope':'native tiny correctness controls, not scientific EDA','source_before':before,'source_after':after,'source_stable':True,'cases':rows,'baseline':r.to_dict(),'native_zero_rc_input_error':{'command':command,'returncode':p.returncode,'with_appended_success_status':'error'}}
(OUT/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print('all native controls pass; source stable',flush=True)
