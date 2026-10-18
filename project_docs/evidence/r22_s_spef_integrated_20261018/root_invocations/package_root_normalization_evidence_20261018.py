"""Retain exact invoked root probes and failed/green logs without replacing them."""
from pathlib import Path
import hashlib, json, shutil

root=Path('project_docs/evidence/r22_s_spef_integrated_20261018')
out=root/'root_invocations'
out.mkdir(exist_ok=False)
names=[
 'capture_native_tool_identity_20261018.py',
 'probe_native_wrong_top_20261018.py','probe_native_wrong_top_post_20261018.py',
 'reproduce_native_cec_20261018.py','reproduce_native_cec_v2_20261018.py',
 'run_r22_optional_tool_checks_20261018.py','run_r22_optional_tool_checks_v2_20261018.py',
 'run_r22_optional_tool_checks_v3_20261018.py',
 'normalization_selection_red_20261018.log','normalization_selection_green_20261018.log',
 'normalization_top_red_20261018.log','normalization_top_red_v2_20261018.log',
 'normalization_top_green_20261018.log','normalization_top_green_v2_20261018.log',
 'prepare_regression_v2.py','prepare_regression_v3.py','prepare_regression_v4.py',
 'run_r22_integrated_regression_v4_20261018.py',
]
manifest=[]
for name in names:
    src=Path('scratch')/name
    dest=out/name
    shutil.copyfile(src,dest)
    assert src.read_bytes()==dest.read_bytes()
    manifest.append({'source':str(src),'snapshot':str(dest),
                     'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
shutil.copyfile(__file__,out/Path(__file__).name)
(out/'MANIFEST.json').write_text(json.dumps({'scope':'Exact root invocation scripts and intermediate logs; failed attempts retained; not scientific measurements', 'files':manifest},indent=2),encoding='utf-8')
print(f'Preserved {len(manifest)} exact invoked scripts/logs')
