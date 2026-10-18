"""Stage only this reviewed implementation/evidence phase, preserving raw logs."""
from pathlib import Path
import subprocess,json

evidence=[f'project_docs/evidence/{name}' for name in [
 'r22_b18_domain_20261018','r22_cec_top_scope_audit_20261018','r22_parasitic_repair_20261018',
 'r22_s_cec_repair_20261018','r22_s_spef_integrated_20261018','r22_spef_topology_repair_20261018']]
tracked=[p.decode('utf-8') for p in subprocess.check_output(['git','diff','--name-only','-z']).split(b'\0') if p]
roots={'.codex-handoff.json','.gitattributes','AGENTS.md','README.md','docs/EXPERIENCE.md'}
assert all(p in roots or p.startswith(('code/','project_docs/')) for p in tracked),tracked
subprocess.run(['git','add','-A','--',*tracked,'code/tests/test_cec_blif_scope.py','code/tests/test_r22_parasitic_measurement.py','code/tests/test_s_cec_evidence.py','code/tests/test_spef_pin_topology.py',*evidence],check=True,capture_output=True)
logs=[str(p) for name in evidence for p in sorted(Path(name).rglob('*.log')) if p.is_file()]
for start in range(0,len(logs),40):
    subprocess.run(['git','add','-f','--',*logs[start:start+40]],check=True,capture_output=True)
# Re-apply byte attributes after all additions; do not normalize pinned raw data.
subprocess.run(['git','add','--renormalize','--','code',*evidence],check=True,capture_output=True)
staged=[p.decode('utf-8') for p in subprocess.check_output(['git','diff','--cached','--name-only','-z']).split(b'\0') if p]
assert not any(p.startswith('data/') for p in staged)
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/source_stage_qa')
receipt={'tracked_modified_paths':tracked,'forced_raw_logs':logs,'staged_paths':staged,'staged_count':len(staged),'scope':'Reviewed source/evidence/records only; no scientific result files in data/ staged'}
(out/'STAGING_SCOPE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
subprocess.run(['git','add','--',str(out/'STAGING_SCOPE.json'),str(out/Path(__file__).name)],check=True,capture_output=True)
print(json.dumps({'staged_count_before_own_receipt':len(staged),'forced_raw_logs':len(logs),'data_results_staged':False}))
