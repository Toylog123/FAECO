"""Read-only audit of completed C-prime v3 jobs; preserve each count snapshot."""
import hashlib,json,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code/scripts'),str(ROOT/'code/src')]
import run_r22_cut_ablation as b
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def text_sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
out=ROOT/'experiments/20261016_r22_cut_ablation_v3'
manifest=load(out/'manifest.json')
assert manifest['source_manifest']==b.source_manifest()
assert manifest['git_head']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
assert manifest['lib_sha256']==b.sha(b.LIB)
rows=[]
for circuit in b.CIRCUITS:
    initial=(out/'inputs'/circuit/'mapped.v').read_text(encoding='utf-8')
    for arm in b.ARMS:
        job=out/arm/circuit
        if not (job/'completion.json').is_file():continue
        done=load(job/'completion.json')
        assert done['returncode']==0 and done['sec_status']=='pass',(arm,circuit,done)
        assert b.validate_completion(job,done,initial)
        result=load(job/'outerloop_result.json');ledger=load(job/'eval_trials.json')
        config=load(job/'run_config.json')
        assert config['git_head']==manifest['git_head']
        assert config['argv']==manifest['commands'][arm][circuit][4:]
        assert not any(config['resolved_args'][key] for key in
                       ('physical_gate','capture_electrical','structure_resynth'))
        state=result['state'];launches=ledger['sta_launch_events'];trials=ledger['trials']
        count=len(launches)
        assert result['n_new_sta_runs']==done['n_new_sta_runs']==state['budget']['sta_used']==count
        assert result['n_candidate_evaluation_records']==len(trials)
        assert [e['seq'] for e in launches]==list(range(1,count+1))
        launch_artifacts=[]
        for event in launches:
            report=Path(event['report_dir'])
            assert event['kind']=='candidate_ideal'
            assert text_sha((report/'mapped.v').read_text(encoding='utf-8'))==event['candidate_hash']
            assert (report/'sta.log').is_file() and (report/'sta.tcl').is_file()
            matches=[t for t in trials if t.get('sta_executed') and t.get('sta_launch_seq')==event['seq']]
            assert len(matches)==1 and matches[0]['candidate_hash']==event['candidate_hash']
            launch_artifacts.append({'seq':event['seq'], 'report_dir':report.relative_to(job).as_posix(),
                'sha256':{name:b.sha(report/name) for name in ('mapped.v','sta.tcl','sta.log')}})
        expected_reports={Path(e['report_dir']).resolve()/'sta.log' for e in launches}
        expected_reports.add((job/'sta.log').resolve())
        assert {p.resolve() for p in job.rglob('sta.log')}==expected_reports
        runner_log=(job/'runner.log').read_text(encoding='utf-8')
        retries=len(re.findall(r'STA attempt [123] truncated wns=None, retrying',runner_log))
        baseline_attempts=1+retries
        assert baseline_attempts<=3
        previous=text_sha(initial)
        for commit in state['accepted_patches']:
            assert commit['base_netlist_hash']==previous
            assert commit['netlist_hash']==commit['candidate_hash']==text_sha(commit['netlist_text'])
            assert any(t['candidate_hash']==commit['candidate_hash'] and t['base_netlist_hash']==previous for t in trials)
            previous=commit['netlist_hash']
        assert previous==state['current_netlist_hash']==text_sha(state['current_netlist_text'])
        log=(job/'final_sec/sec.log').read_text(encoding='utf-8')
        points=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)
        assert points and int(points[-1][0])>0 and int(points[-1][1])==0
        assert 'Equivalence successfully proven!' in log and 'No SAT model' not in log
        rows.append({'circuit':circuit,'arm':arm,'candidate_ideal_sta_launches':count,
                     'candidate_evaluation_records':len(trials),'retained_commits':len(state['accepted_patches']),
                     'baseline_sta_process_attempts':baseline_attempts,
                     'total_sta_process_attempts':count+baseline_attempts,
                     'other_sta_process_attempts':0,'launch_artifacts':launch_artifacts,
                     'baseline_artifacts':{name:b.sha(job/name) for name in ('mapped.v','sta.tcl','sta.log','runner.log')},
                     'baseline_wns':done['baseline_wns'],'final_wns':done['final_wns'],
                     'sec_proven_points':int(points[-1][0]),'sec_unproven_points':0,
                     'completion_sha256':b.sha(job/'completion.json'),
                     'evidence_receipt':done['evidence_receipt']})
assert manifest['source_manifest']==b.source_manifest()
result={'head':manifest['git_head'],'manifest_sha256':b.sha(out/'manifest.json'),
        'completed_and_verified':len(rows),'expected_matrix_jobs':72,'all_matrix_verified':len(rows)==72,
        'source_stable':True,'jobs':rows,
        'count_scope':'candidate_ideal event count excludes baseline. Total adds baseline attempts from the pinned one-call runner and retry messages; complete STA report paths checked. Physical/electrical/S are disabled.',
        'audit_invoked_path':'scratch/audit_matrix_cprime_v3.py','audit_sha256':b.sha(Path(__file__))}
target=ROOT/f'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_{len(rows):02d}.json'
with target.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'completed_and_verified':len(rows),'all_matrix_verified':len(rows)==72,
                  'jobs':[{k:r[k] for k in ('circuit','arm','candidate_ideal_sta_launches','retained_commits','final_wns')} for r in rows]},ensure_ascii=False))
