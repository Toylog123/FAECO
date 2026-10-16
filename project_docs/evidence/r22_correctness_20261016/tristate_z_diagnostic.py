"""Adversarial Z-vs-zero and Z-vs-one tool controls, no timing runs."""
from pathlib import Path
import importlib.util
import subprocess

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tri_controls',HERE/'sec_model_controls.py')
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
b=c.batch

def main():
    out=HERE/'tristate_z_diagnostic'
    if out.exists():
        raise RuntimeError('Do not overwrite evidence')
    out.mkdir()
    cases=[]
    for value in (0,1):
        gold=f"module top(EN,Y); input EN; output Y; sky130_fd_sc_hd__einvn_1 g(.A(1'b{1-value}),.TE_B(EN),.Z(Y)); endmodule\n"
        gate=f"module top(EN,Y); input EN; output Y; assign Y=1'b{value}; endmodule\n"
        cases.append((f'z_vs_constant_{value}',gold,gate,'fail'))
    source=b.source_manifest()
    lib=b.sha(b.LIB)
    record={'diagnostic_only':True,'timing_runs':0,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=b.ROOT,text=True).strip(),
            'source_manifest':source,'liberty_sha256':lib,'script_sha256':b.sha(Path(__file__)),
            'configuration':[dict(name=n,gold=g,gate=t,expected=e) for n,g,t,e in cases],
            'status':'registered','results':[]}
    target=out/'diagnostic.json'
    b.save(target,record)
    for name,gold,gate,expected in cases:
        result=b.final_sec(gold,gate,'top',out/name)
        record['results'].append(dict(name=name,expected=expected,result=result,matches=result['status']==expected))
        b.save(target,record)
        print(name,expected,result['status'],flush=True)
    record.update(status='completed',source_stable=b.source_manifest()==source and b.sha(b.LIB)==lib)
    record['passed']=record['source_stable'] and all(r['matches'] for r in record['results'])
    b.save(target,record)
    return 0 if record['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
