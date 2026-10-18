from pathlib import Path
import json,hashlib,subprocess

out=Path('project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding')
r=json.loads((out/'RESULT.json').read_text(encoding='utf-8'))
assert r['source_stable']
for name,sha in r['source_after'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
for name,sha in r['artifacts'].items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==sha
positives=[x for x in r['cases'] if 'length_um' in x]
negatives=[x for x in r['cases'] if 'missing_pin' in x['case']]
assert len(positives)==4 and len(negatives)==2
for row in positives:
    assert row['annotation_returncode']==0 and row['annotation_error'] is None
    log=(out/row['case']/str(row['length_um'])/'annotation.log').read_text(encoding='utf-8')
    assert 'Found 0 unannotated drivers.' in log
    assert 'Found 0 partially unannotated drivers.' in log
    assert row['result']['slack'] is not None
for length in [40,4000]:
    pair=[x for x in positives if x['length_um']==length]
    assert pair[0]['result']==pair[1]['result']
for name in ['ordinary','escaped']:
    pair=[x for x in positives if x['case']==name]
    assert pair[0]['result']['slack']>pair[1]['result']['slack']
for row in negatives:
    assert 'pin b0:ABSENT not found' in row['result']['error']
    assert all(row['result'][field] is None for field in ['wns','tns','slack','min_slack'])
identities=[]
for args in [['/usr/local/bin/sta','-version'],['sha256sum','/usr/local/bin/sta']]:
    argv=['wsl.exe','-d','Ubuntu','--',*args]
    p=subprocess.run(argv,capture_output=True,timeout=15)
    identities.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
    assert p.returncode==0
receipt={'scope':'Root postcheck of actual OpenSTA micro controls, not independent review or benchmark evidence','positive_api_attempts':4,'annotation_replay_attempts':4,'missing_pin_negative_attempts':2,
 'all_sources_and_artifacts_match':True,'all_four_annotation_replays_zero_unannotated_and_zero_partial_drivers':True,
 'escaped_and_ordinary_results_identical_at_each_rc':True,'rc_increase_degrades_both_controls':True,'both_bad_pin_cases_rejected_without_numeric_results':True,
 'actual_tool_identities':identities,'result_sha256':hashlib.sha256((out/'RESULT.json').read_bytes()).hexdigest()}
(out/'ROOT_ACCEPTANCE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(receipt,ensure_ascii=False))
