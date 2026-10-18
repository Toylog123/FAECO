from pathlib import Path
import os,json,dataclasses,hashlib
os.environ['PATH']=';'.join([r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib',os.environ.get('PATH','')])
from rseco.yosys_abc import check_yosys_abc_equivalence
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/native_top_counterexample_post')
out.mkdir(exist_ok=False)
template='''module ztop(input A,B,output Y); wire n;
sky130_fd_sc_hd__buf_1 g1 (.A(INPUT),.X(Y));
sky130_fd_sc_hd__buf_1 g2 (.A(OTHER),.X(n)); endmodule
'''
a=out/'original.v'; b=out/'revised.v'
a.write_text(template.replace('INPUT','A').replace('OTHER','B'),encoding='utf-8')
b.write_text(template.replace('INPUT','B').replace('OTHER','A'),encoding='utf-8')
result=check_yosys_abc_equivalence(a,b,outputs=['Y'],artifact_dir=out/'proof',
    liberty_cells_v=Path('data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v'))
receipt={'result':dataclasses.asdict(result),'semantic_counterexample':{'A':0,'B':1,'original_Y':0,'revised_Y':1},
    'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('code/src/rseco/yosys_abc.py'),a,b]},
    'scope':'native tool falsification probe only; not a paper result'}
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2,default=str),encoding='utf-8')
print(json.dumps(receipt,indent=2,default=str))
