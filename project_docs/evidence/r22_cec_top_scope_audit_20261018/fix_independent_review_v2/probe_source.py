"""Bounded independent native correctness probes; no scientific experiments."""
from pathlib import Path
import sys,json,hashlib,os
os.environ['PATH']=';'.join([r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib',os.environ.get('PATH','')])
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'code/src'))
from rseco.yosys_abc import check_mapped_blif_equivalence,_extract_cells_for_netlist
from rseco.verilog_modules import select_top_module,module_spans
OUT=ROOT/'project_docs/evidence/r22_cec_top_scope_audit_20261018/fix_independent_review_v2';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['code/src/rseco/yosys_abc.py','code/src/rseco/verilog_modules.py','code/src/rseco/structure_resynthesis.py'];before={n:sha(ROOT/n) for n in paths}
for n in paths:(OUT/('source_'+Path(n).name)).write_bytes((ROOT/n).read_bytes())
original=OUT/'original.v';original.write_text('module ztop(input A,output Y); assign Y=A; endmodule\n',encoding='utf-8')
rows=[]
for name,prefix in [('single_inverter',''),('dummy_first_then_inverter','.model dummy\n.inputs A\n.outputs Y\n.names A Y\n1 1\n.end\n\n')]:
 mapped=OUT/(name+'.blif');mapped.write_text(prefix+'.model ztop\n.inputs A\n.outputs Y\n.names A Y\n0 1\n.end\n',encoding='utf-8')
 r=check_mapped_blif_equivalence(original,mapped,artifact_dir=OUT/name,yosys_command='C:/oss-cad-suite-build/oss-cad-suite/bin/yosys.exe',abc_command='C:/oss-cad-suite-build/oss-cad-suite/bin/yosys-abc.exe',timeout_s=15)
 rows.append({'case':name,'result':r.to_dict(),'expected':'fail: source Y=A versus mapped ztop Y=!A','counterexample':{'A':0,'source_Y':0,'intended_mapped_top_Y':1},'mapped_file_sha256':sha(mapped)})
top_controls=[]
for name,text,wanted in [('helper_before_top','module helper(input A,output Y);assign Y=A;endmodule\nmodule ztop(input A,output Y);helper h(.A(A),.Y(Y));endmodule','ztop'),('ambiguous','module a(input A);endmodule module b(input B);endmodule',None)]:
 try:
  top=select_top_module(text);assert top==wanted;top_controls.append({'name':name,'selected':top})
 except ValueError as exc:assert wanted is None;top_controls.append({'name':name,'rejected':str(exc)})
model=OUT/'models.v';model.write_text('module sky130_fd_sc_hd__buf_1(input A,output X);assign X=A;endmodule\nmodule sky130_fd_sc_hd__unused_1(input A,output X);assign X=~A;endmodule\n')
extract_rows=[]
for name,text,expected in [('assign_only',original.read_text(),set()),('inline_used','module ztop(input A,output Y);sky130_fd_sc_hd__buf_1 u(.A(A),.X(Y));endmodule',{'sky130_fd_sc_hd__buf_1'})]:
 p=OUT/(name+'.v');p.write_text(text);dst=OUT/(name+'_cells.v');_extract_cells_for_netlist(p,model,dst);found={x.name for x in module_spans(dst.read_text())};assert found==expected;extract_rows.append({'case':name,'actual_models':sorted(found),'sha256':sha(dst)})
after={n:sha(ROOT/n) for n in paths};assert before==after
report={'scope':'independent bounded native correctness and static probes, not scientific EDA','source_before':before,'source_after':after,'source_stable':True,'native_cases':rows,'top_controls':top_controls,'model_controls':extract_rows}
(OUT/'PROBE_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'native':[(r['case'],r['result']['status']) for r in rows],'source_stable':True}))
