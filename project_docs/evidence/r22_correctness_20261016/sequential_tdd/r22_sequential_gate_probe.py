from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code/scripts'),str(ROOT/'code/src')]
import run_r22_cut_ablation as batch
from rseco.logic_rewrite import parse_liberty_cells,equivalence_candidates
from rseco.real_wns import build_real_equivalence_checker
from rseco.graph import _is_sequential_gate
libtext=batch.LIB.read_text(encoding='utf-8')
cells=parse_liberty_cells(libtext)
gold='module top(CLK,D,RESET_B,Q); input CLK,D,RESET_B; output Q; sky130_fd_sc_hd__dfrtp_1 g(.CLK(CLK),.D(D),.RESET_B(RESET_B),.Q(Q)); endmodule'
gate=gold.replace('dfrtp_1','dfstp_1').replace('.RESET_B(RESET_B)','.SET_B(RESET_B)')
result=build_real_equivalence_checker(libtext)(gold,gate)
rows=[dict(type=n,kind=c.sequential_kind,recognized=_is_sequential_gate(n)) for n,c in cells.items() if c.sequential_kind]
record=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 source_manifest=batch.source_manifest(),liberty_sha256=batch.sha(batch.LIB),
 gold=gold,gate=gate,expected_status='fail',actual_status=result.status,
 actual_reason=result.reason,eda_executed=False,
 sequential_r_candidates=equivalence_candidates(cells['sky130_fd_sc_hd__dfrtp_1'],cells),
 graph_sequential_inventory=rows)
out=ROOT/'project_docs/evidence/r22_correctness_20261016/SEQUENTIAL_GATE_COUNTEREXAMPLE.json'
with out.open('x',encoding='utf-8') as stream:json.dump(record,stream,indent=2)
print('reset-to-set F1:',result.status)
print('sequence families missed by graph:',[r['type'] for r in rows if not r['recognized']])
