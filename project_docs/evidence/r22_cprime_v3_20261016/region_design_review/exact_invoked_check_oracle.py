from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'code/src'),str(R/'code/scripts')]
from rseco.logic_rewrite import parse_liberty_cells
from rseco.replacement import parse_verilog_netlist_from_text
from rseco.graph import extract_fanin_cone
from rseco.cut import _cut_for_selected_gates
import run_r22_cut_ablation as common
cells=parse_liberty_cells(common.LIB.read_text(encoding='utf-8'))
metadata={n:dict(c.output_functions) for n,c in cells.items() if c.output_functions}
text='''module top(ZERO,ONE);\noutput ZERO,ONE;\nsky130_fd_sc_hd__conb_1 c(.LO(ZERO),.HI(ONE));\nendmodule\n'''
netlist=parse_verilog_netlist_from_text(text,cell_output_functions=metadata)
cone=extract_fanin_cone(netlist,['ZERO']);cut=_cut_for_selected_gates(cone,cone.gates,method='control')
drivers={n:g.name for g in netlist.gates for n in g.all_outputs}
old={netlist.resolve_alias(n) for n in netlist.outputs}
new={n if n in drivers else netlist.resolve_alias(n) for n in netlist.outputs}
assert old=={"1'b0","1'b1"} and new=={'ZERO','ONE'} and set(cut.boundary_outputs)==new
report={'old_oracle_module_outputs':sorted(old),'correct_physical_module_outputs':sorted(new),
 'production_cut_boundary_outputs':cut.boundary_outputs,'oracle_defect_confirmed':True,
 'production_defect':False,'eda_executed':False}
out=R/'project_docs/evidence/r22_cprime_v3_20261016/region_design_review/ORACLE_ATTRIBUTION.json'
with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
