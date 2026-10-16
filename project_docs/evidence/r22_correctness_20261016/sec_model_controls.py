"""Real SEC positive/negative controls for tie outputs and full-adder carry.

Uses the same frozen independent prover as the experiments. No timing runs.
"""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'code/src'))
path=ROOT/'code/scripts/run_r22_cut_ablation.py'
spec=importlib.util.spec_from_file_location('controls_prover',path)
batch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

tie_gold="""module top(H,L);
output H,L;
assign H=1'b1;
assign L=1'b0;
endmodule
"""
tie_good="""module top(H,L);
output H,L;
sky130_fd_sc_hd__conb_1 g(.HI(H),.LO(L));
endmodule
"""
fa_gold="""module top(A,B,CIN,SUM,COUT);
input A,B,CIN;
output SUM,COUT;
assign SUM=A^B^CIN;
assign COUT=(A&B)|(A&CIN)|(B&CIN);
endmodule
"""
fa_good="""module top(A,B,CIN,SUM,COUT);
input A,B,CIN;
output SUM,COUT;
sky130_fd_sc_hd__fa_1 g(.A(A),.B(B),.CIN(CIN),.SUM(SUM),.COUT(COUT));
endmodule
"""
fa_bad=fa_good.replace('output SUM,COUT;', 'output SUM,COUT;\nwire unused_carry;\nassign COUT=1\'b0;').replace('.COUT(COUT)', '.COUT(unused_carry)')
enable_gold="""module top(CLK,D,DE,Q);
input CLK,D,DE;
output reg Q;
always @(posedge CLK) if (DE) Q<=D;
endmodule
"""
enable_good="""module top(CLK,D,DE,Q);
input CLK,D,DE;
output Q;
sky130_fd_sc_hd__edfxtp_1 g(.CLK(CLK),.D(D),.DE(DE),.Q(Q));
endmodule
"""
enable_bad=enable_good.replace('output Q;','output Q;\nwire wrong_enable;\nassign wrong_enable=~DE;').replace('.DE(DE)','.DE(wrong_enable)')
CASES=[('tie_both_outputs',tie_gold,tie_good,'pass'),
       ('tie_swapped_outputs',tie_gold,tie_good.replace('.HI(H),.LO(L)','.HI(L),.LO(H)'),'fail'),
       ('fa_all_outputs',fa_gold,fa_good,'pass'),
       ('fa_same_sum_wrong_carry',fa_gold,fa_bad,'fail'),
       ('enable_ff_hold_semantics',enable_gold,enable_good,'pass'),
       ('enable_ff_inverted_enable',enable_gold,enable_bad,'fail')]


def main():
    out=Path(__file__).resolve().parent/'sec_controls'
    if out.exists():
        raise RuntimeError('Never overwrite prior controls')
    if subprocess.check_output(['git','status','--porcelain','--','code'],cwd=ROOT,text=True).strip():
        raise RuntimeError('Commit source and tests before formal controls')
    out.mkdir()
    frozen=batch.source_manifest()
    record={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'liberty_sha256':batch.sha(batch.LIB),'source_manifest':frozen,
            'script_sha256':batch.sha(Path(__file__)),
            'configuration':[{'name':name,'gold':gold,'gate':gate,'expected':expected}
                             for name,gold,gate,expected in CASES], 'status':'registered', 'results':[]}
    receipt=out/'controls.json'
    batch.save(receipt,record)
    for name,gold,gate,expected in CASES:
        if batch.source_manifest()!=frozen:
            raise RuntimeError('Source drift before control')
        result=batch.final_sec(gold,gate,'top',out/name)
        record['results'].append({'name':name,'expected':expected,'actual':result['status'],
                                  'returncode':result['returncode'],
                                  'matches':result['status']==expected,
                                  'artifacts':{p.name:batch.sha(p) for p in sorted((out/name).iterdir()) if p.is_file()}})
        batch.save(receipt,record)
        print(name,expected,result['status'],flush=True)
    record['source_stable']=batch.source_manifest()==frozen
    record['passed']=record['source_stable'] and all(row['matches'] for row in record['results'])
    record['status']='completed'
    batch.save(receipt,record)
    return 0 if record['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
