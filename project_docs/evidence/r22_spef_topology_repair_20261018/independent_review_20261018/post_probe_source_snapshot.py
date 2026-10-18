from pathlib import Path
import json,sys,hashlib,time
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'code/src'))
from rseco.spef import parse_mapped_verilog,build_spef
OUT=ROOT/'scratch/spef_independent_1018_post';OUT.mkdir(exist_ok=False)
LIB='''library(tiny) {
cell ("sky130_fd_sc_hd__buf_1") { pin ("A") { direction: input; } pin ("X") { direction: output; function: "A"; } }
}'''
cases={
 'escaped_scalar_vs_bitselect':r'''module top(a, \a[0] , z1, z2);
input [1:0] a; input \a[0] ; output z1,z2;
sky130_fd_sc_hd__buf_1 b1 (.A(a[0]),.X(z1));
sky130_fd_sc_hd__buf_1 b2 (.A(\a[0] ),.X(z2));
endmodule''',
 'port_only_feedthrough':'''module top(input A,output Z); assign Z=A; endmodule''',
 'unparsed_outside_modules':'''garbage invalid xyz
module top(input A,output Z); sky130_fd_sc_hd__buf_1 b (.A(A),.X(Z)); endmodule
garbage illegal''',
 'missing_header_port_direction':'''module top(A,Z,forgot); input A; output Z;
sky130_fd_sc_hd__buf_1 b (.A(A),.X(Z)); endmodule''',
 'alias_scalar_width_mismatch':'''module top(input [1:0] A,output Z); wire t; assign t=A[2]; sky130_fd_sc_hd__buf_1 b (.A(t),.X(Z)); endmodule''',
 'constant_output_connection':'''module top(input A,output Z); sky130_fd_sc_hd__buf_1 b (.A(A),.X(1'b0)); assign Z=A; endmodule''',
}
sources=['code/src/rseco/spef.py','code/src/rseco/real_wns.py','code/tests/test_spef_pin_topology.py','code/tests/test_real_wns.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={s:sha(ROOT/s) for s in sources};rows=[]
for name,text in cases.items():
 p=OUT/(name+'.v');p.write_text(text,encoding='utf-8')
 try:
  nl=parse_mapped_verilog(p,liberty_text=LIB,top_module='top');spef=build_spef(nl);(OUT/(name+'.spef')).write_text(spef,encoding='utf-8')
  rows.append({'case':name,'status':'accepted','ports':nl.ports,'nets':{k:{'pins':n.pins,'ports':n.port_connections,'driver':n.driver()} for k,n in nl.nets.items()},'spef':spef})
 except Exception as exc:rows.append({'case':name,'status':'rejected','error':repr(exc)})
after={s:sha(ROOT/s) for s in sources};assert before==after
(OUT/'RESULT.json').write_text(json.dumps({'sources_before':before,'sources_after':after,'cases':rows,'EDA_executed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'case':r['case'],'status':r['status'],'error':r.get('error'),'nets':r.get('nets')} for r in rows],ensure_ascii=False,indent=2))
