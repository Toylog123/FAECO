from pathlib import Path
import os,json,dataclasses
os.environ['PATH']=';'.join([r'C:\Program Files\Git\bin',r'C:\oss-cad-suite-build\oss-cad-suite\bin',r'C:\oss-cad-suite-build\oss-cad-suite\lib',os.environ.get('PATH','')])
from rseco.yosys_abc import check_yosys_abc_equivalence
case=Path('data/cases/minimal/iscas85_c17_case01')
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/native_cec_reproduction_v2')
result=check_yosys_abc_equivalence(case/'original/original.v',case/'resynthesized/resynthesized.v',
    outputs=['N22','N23'],artifact_dir=out,
    liberty_cells_v=Path('data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v'))
(out/'RESULT.json').write_text(json.dumps(dataclasses.asdict(result),ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps(dataclasses.asdict(result),ensure_ascii=False,indent=2,default=str))
