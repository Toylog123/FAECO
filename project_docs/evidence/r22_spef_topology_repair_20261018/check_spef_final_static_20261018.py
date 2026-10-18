from pathlib import Path
import hashlib,json,time
from rseco.spef import parse_mapped_verilog,build_spef
from rseco.opensta import LIB_SEQ
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_paths=['code/src/rseco/spef.py','code/src/rseco/real_wns.py']
before={p:sha(p) for p in source_paths}
lib=Path(LIB_SEQ).read_text(encoding='utf-8')
inputs=[(p,p.parent.name) for p in Path('experiments/20261016_r22_cut_ablation_v3/inputs').glob('*/mapped.v')]
inputs += [(Path('experiments/20260805_phys_closure/b18_light/b18')/p,'b18') for p in ['mapped.v','eval/iter009_cand009/029__649725__R/mapped.v']]
rows=[];started=time.perf_counter()
for path,top in inputs:
    row={'path':str(path),'sha256':sha(path)}
    try:
        nl=parse_mapped_verilog(path,liberty_text=lib,top_module=top)
        text=build_spef(nl)
        row.update(status='parsed',instances=len(nl.instances),nets=len(nl.nets),spef_sha256=hashlib.sha256(text.encode()).hexdigest(),
            omitted_unused_constant_aliases=nl.omitted_unused_constant_aliases,
            target_outputs=[{'net':n.name,'pin':n.driver()} for n in nl.nets.values() if n.driver() and n.driver()[0]=='_649725_'])
    except ValueError as exc:row.update(status='unsupported',reason=str(exc))
    assert sha(path)==row['sha256']
    rows.append(row)
    print(json.dumps({k:v for k,v in row.items() if k not in ['omitted_unused_constant_aliases']}),flush=True)
receipt={'scope':'static actual inputs only, no STA/SEC and no independent full-host legality claim','lib_sha256':sha(LIB_SEQ),
         'source_before':before,'source_after':{p:sha(p) for p in source_paths},'records':rows,'elapsed_s':time.perf_counter()-started}
with Path('project_docs/evidence/r22_spef_topology_repair_20261018/FINAL_ACTUAL_INPUT_STATIC_CHECK.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
assert before==receipt['source_after']
