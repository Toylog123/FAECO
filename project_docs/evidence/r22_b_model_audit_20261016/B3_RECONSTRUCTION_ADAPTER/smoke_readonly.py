"""Actual B3 bytes and domain gates only; never register or launch tools."""
from pathlib import Path
import json
import subprocess
import adapter as a

HERE=Path(__file__).resolve().parent
output=a.BASE/'B3_RECONSTRUCTION_RUNS/review_20261016'
assert not output.exists(),'Unexpected formal output already exists'
pin=a.source_pin()
plan=a.build_plan(output)
a.save_new(HERE/'review_preview_20261016.json',plan)
design=a.read_json(a.DESIGN)
rows=[]
for job in plan['jobs']:
    circuit=job['circuit'];initial=(a.ROOT/job['baseline']['path']).read_text(encoding='utf-8')
    cert=a._domain(initial,initial)
    old=next(row for row in design['runs'] if row['circuit']==circuit)
    candidate=a.ROOT/old['actual_final_path']
    assert a.sha(candidate)==design['sources'][old['actual_final_path']]['sha256']
    try:a._domain(initial,candidate.read_text(encoding='utf-8'))
    except (RuntimeError,ValueError) as error:rejection=str(error)
    else:raise AssertionError('Historical missing TE_B final unexpectedly accepted')
    assert 'TE_B' in rejection
    rows.append({'circuit':circuit,'input_sha256':a.sha(a.ROOT/job['baseline']['path']),
        'initial_domain':'valid','initial_x_sources':len(cert['sources']),
        'old_final_path':old['actual_final_path'],'old_final_sha256':a.sha(candidate),
        'old_final_rejection':rejection})
report={'schema':'B3-adapter-readonly-live-input-QA-v1','eda_executed':False,'formal_registration_executed':False,
    'preview_sha256':a.sha(HERE/'review_preview_20261016.json'),'source_pin':pin,
    'source_stable':a.source_pin()==pin,'formal_output_exists':output.exists(),'actual_inputs':rows,
    'production_git_clean':not bool(subprocess.check_output(['git','status','--porcelain','--','code'],cwd=a.ROOT,text=True).strip()),
    'historical_design_hashes':{name:a.sha(a.BASE/name) for name in ['B3_RERUN_DESIGN.md','B3_RERUN_DESIGN.json']}}
assert report['source_stable'] and not report['formal_output_exists']
a.save_new(HERE/'LIVE_INPUT_QA.json',report)
print(json.dumps({'head':pin['head'],'source_stable':report['source_stable'],'inputs':rows,'formal_output_exists':output.exists()},indent=2))
