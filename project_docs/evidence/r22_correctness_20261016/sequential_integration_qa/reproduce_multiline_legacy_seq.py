from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'code/src'))
import rseco.real_wns as current
from rseco.logic_rewrite import parse_liberty_cells
revision='44d20bb'
def old_module(relative,name):
    source=subprocess.check_output(['git','show',revision+':'+relative],cwd=R)
    spec=importlib.util.spec_from_loader(name,loader=None)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    exec(compile(source.decode('utf-8'),revision+':'+relative,'exec'),module.__dict__)
    return module,{'git_revision':revision,'git_path':relative,'sha256':hashlib.sha256(source).hexdigest()}
old,old_pin=old_module('code/src/rseco/real_wns.py','rseco._r22_legacy_rw')
old_gs,gs_pin=old_module('code/src/rseco/gate_sizing.py','rseco._r22_legacy_gs')
libpath=R/'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
text=libpath.read_text(encoding='utf-8')
gold='''module top(CLK,D,RESET_B,Q);
input CLK,D,RESET_B;
output Q;
sky130_fd_sc_hd__dfrtp_1 g (.CLK(CLK),.D(D),.RESET_B(RESET_B),.Q(Q));
endmodule
'''
gate=gold.replace('dfrtp_1','dfstp_1').replace('.RESET_B(RESET_B)','.SET_B(RESET_B)')
records=[]
for mode in ['multiline','singleline']:
    g=gold if mode=='multiline' else ' '.join(gold.splitlines())
    t=gate if mode=='multiline' else ' '.join(gate.splitlines())
    for parser_name,parser in [('historical_gs',old_gs.parse_mapped_netlist),('current_gs',current.parse_mapped_netlist)]:
        old.parse_mapped_netlist=parser
        result=old.build_real_equivalence_checker(text,top_module='top')(g,t)
        records.append({'source_format':mode,'checker':'historical_RW','parser':parser_name,'gold_parsed_count':len(parser(g)),'gate_parsed_count':len(parser(t)),'status':result.status,'reason':result.reason})
    result=current.build_real_equivalence_checker(text,top_module='top')(g,t)
    records.append({'source_format':mode,'checker':'current_RW','parser':'current_gs','gold_parsed_count':len(current.parse_mapped_netlist(g)),'gate_parsed_count':len(current.parse_mapped_netlist(t)),'status':result.status,'reason':result.reason})
assert next(x for x in records if x['source_format']=='multiline' and x['parser']=='historical_gs')['status']=='pass'
assert all(x['status']=='fail' and x['gold_parsed_count']==1 and x['gate_parsed_count']==1 for x in records if x['checker']=='current_RW')
result={'schema':'r22-sequential-F1-independent-multiline-legacy-reproduction-v1','eda_executed':False,'old_RW':old_pin,'old_gatesizing':gs_pin,'current_source_sha256':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['code/src/rseco/real_wns.py','code/src/rseco/gate_sizing.py','code/src/rseco/logic_rewrite.py']},'liberty_path':libpath.relative_to(R).as_posix(),'liberty_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),'gold_multiline':gold,'gate_multiline':gate,'records':records,'conclusion':'Multiline historical parser sees both physical FFs and old F1 still incorrectly passes reset-to-set. Sequential semantic defect is independent from historical single-line parser omission. Current RW rejects both complete-parser formats.'}
out=R/'project_docs/evidence/r22_correctness_20261016/SEQUENTIAL_MULTILINE_LEGACY_REPRO.json'
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,indent=2))
