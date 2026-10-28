"""Reconstruct committed C-prime B(k) from accepted raw process/commit ledgers."""
import argparse,csv,hashlib,json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
AUDIT='project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json'
AUDIT_SHA='a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def textsha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def csvout(p,rows):
    with p.open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def reconstruct(job,accepted_job):
    completion=load(job/'completion.json')
    assert sha(job/'completion.json')==accepted_job['completion_sha256']
    for name in ['outerloop_result.json','eval_trials.json','run_config.json']:
        assert sha(job/name)==completion['evidence_receipt'][name]==accepted_job['evidence_receipt'][name]
    result=load(job/'outerloop_result.json');ledger=load(job/'eval_trials.json')
    launches=ledger['sta_launch_events'];trials=ledger['trials'];commits=result['state']['accepted_patches']
    n=accepted_job['candidate_ideal_sta_launches']
    assert len(launches)==n==result['n_new_sta_runs']==completion['n_new_sta_runs']
    assert len(trials)==accepted_job['candidate_evaluation_records']
    assert len(commits)==accepted_job['retained_commits']
    assert [e['seq'] for e in launches]==list(range(1,n+1))
    launchmap={e['seq']:e for e in launches}
    artifacts={a['seq']:a for a in accepted_job['launch_artifacts']}
    measured=[(i,t) for i,t in enumerate(trials,1) if t.get('sta_executed')]
    assert [t['sta_launch_seq'] for _,t in measured]==list(range(1,n+1))
    for index,t in measured:
        e=launchmap[t['sta_launch_seq']]
        assert e['kind']=='candidate_ideal'
        assert e['candidate_hash']==t['candidate_hash'] and e['base_netlist_hash']==t['base_netlist_hash']
        assert Path(e['report_dir']).relative_to(job).as_posix()==artifacts[e['seq']]['report_dir']
        assert not t.get('skipped_duplicate',False)
    baseline=Decimal(str(accepted_job['baseline_wns']))
    initial=(job/'final_sec/initial_raw.v').read_text(encoding='utf-8')
    current_hash=textsha(initial);best=Decimal(0);k=0;ci=0;cached_commits=0
    points=[{'circuit':accepted_job['circuit'],'arm':accepted_job['arm'],'k':0,'trial_record_index':0,
        'committed_gain_ns':0.0,'committed_this_record':False,'candidate_hash':'','base_netlist_hash':current_hash}]
    commit_rows=[]
    for trial_index,t in enumerate(trials,1):
        executed=bool(t.get('sta_executed'))
        if executed:
            k+=1;assert t['sta_launch_seq']==k
        if t.get('committed'):
            assert t.get('accepted') is True
            c=commits[ci];ci+=1
            assert c['candidate_hash']==t['candidate_hash']==c['netlist_hash']==textsha(c['netlist_text'])
            assert c['base_netlist_hash']==t['base_netlist_hash']==current_hash
            assert Decimal(str(c['wns']))==Decimal(str(t['wns']))
            gain=Decimal(str(c['wns']))-baseline
            assert gain>best
            best=gain;current_hash=c['netlist_hash']
            if not executed:cached_commits+=1
            commit_rows.append({'circuit':accepted_job['circuit'],'arm':accepted_job['arm'],
                'commit_index':ci,'k_at_commit':k,'trial_record_index':trial_index,
                'fresh_sta_in_this_trial':executed,'wns_ns':float(c['wns']),
                'gain_ns':float(best),'base_netlist_hash':c['base_netlist_hash'],
                'committed_candidate_hash':c['candidate_hash'],'patch_id':c['patch_id']})
        if executed:
            points.append({'circuit':accepted_job['circuit'],'arm':accepted_job['arm'],'k':k,
                'trial_record_index':trial_index,'committed_gain_ns':float(best),
                'committed_this_record':bool(t.get('committed')),
                'candidate_hash':t['candidate_hash'],'base_netlist_hash':t['base_netlist_hash']})
        elif t.get('committed'):
            # Cost-free committed cache replay: B(k) updates only at its actual
            # outer commit, never when the old measurement was merely observed.
            points[-1]['committed_gain_ns']=float(best)
            points[-1]['committed_this_record']=True
            points[-1]['trial_record_index']=trial_index
    assert ci==len(commits) and k==n and len(points)==n+1
    assert current_hash==result['state']['current_netlist_hash']==textsha(result['state']['current_netlist_text'])
    assert best==Decimal(str(accepted_job['final_wns']))-baseline
    assert Decimal(str(completion['final_wns']))==Decimal(str(accepted_job['final_wns']))
    assert all(a['committed_gain_ns']<=b['committed_gain_ns'] for a,b in zip(points,points[1:]))
    return points,commit_rows,{'circuit':accepted_job['circuit'],'arm':accepted_job['arm'],
        'candidate_sta':n,'trial_records':len(trials),'excluded_nonlaunch_records':len(trials)-n,
        'retained_commits':len(commits),'cached_commits':cached_commits,
        'baseline_sta_separate':accepted_job['baseline_sta_process_attempts'],
        'endpoint_gain_ns':float(best),'final_netlist_hash':current_hash,
        'failed_launches_still_counted':sum(e.get('error') is not None or e.get('timeout',False) for e in launches),
        'accepted_but_not_committed':sum(bool(t.get('accepted')) and not bool(t.get('committed')) for t in trials),
        'input_sha256':{name:sha(job/name) for name in ['completion.json','outerloop_result.json','eval_trials.json','run_config.json']}}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args();audit_path=ROOT/AUDIT
    assert sha(audit_path)==AUDIT_SHA
    audit=load(audit_path);assert audit['all_matrix_verified'] and audit['completed_and_verified']==72
    allpoints=[];allcommits=[];checks=[]
    for j in audit['jobs']:
        job=ROOT/'experiments/20261016_r22_cut_ablation_v3'/j['arm']/j['circuit']
        points,commits,check=reconstruct(job,j)
        allpoints+=points;allcommits+=commits;checks.append(check)
    assert len(checks)==72 and sum(c['candidate_sta'] for c in checks)==6858 and len(allcommits)==192
    by=defaultdict(dict)
    for c in checks:
        series=[(r['k'],r['committed_gain_ns']) for r in allpoints if r['circuit']==c['circuit'] and r['arm']==c['arm']]
        by[c['circuit']][c['arm']]=series
    equal=[]
    for c,arms in by.items():
        remaining=list(arms)
        while remaining:
            a=remaining.pop(0);group=[a]+[b for b in remaining if arms[a]==arms[b]]
            remaining=[b for b in remaining if b not in group]
            equal.append({'circuit':c,'identical_complete_curve_arms':group,'k_end':arms[a][-1][0],
                'gain_end_ns':arms[a][-1][1],
                'series_sha256':textsha(json.dumps(arms[a],separators=(',',':')))})
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    csvout(out/'CANDIDATE_STA_COMMITTED_CURVES.csv',allpoints)
    csvout(out/'COMMIT_EVENTS.csv',allcommits)
    dump(out/'CURVE_RECONSTRUCTION_AUDIT.json',{'status':'PASS all72 actualSTA/commit-bound curves reconstructable',
        'audit_path':AUDIT,'audit_sha256':AUDIT_SHA,'runtime_head':audit['head'],
        'policy':'k counts every candidate_ideal launch (failed too), excludes baseline/cache/pre-reject; B(k) changes only on explicit outer committed trial bound in the accepted state commit chain',
        'total_candidate_sta':6858,'total_points_including72_k0':len(allpoints),
        'total_evaluation_records':sum(c['trial_records'] for c in checks),'total_retained_commits':len(allcommits),
        'cached_commits':sum(c['cached_commits'] for c in checks),
        'accepted_but_not_committed':sum(c['accepted_but_not_committed'] for c in checks),
        'failed_launches':sum(c['failed_launches_still_counted'] for c in checks),
        'checks':checks,'complete_curve_equality_groups':equal,'new_eda':False})
    dump(out/'SOURCE_BINDING.json',{'audit':AUDIT_SHA,'plot_data':{p.name:sha(p) for p in out.iterdir() if p.is_file()},
        'reconstructor_sha256':sha(__file__),'source_inputs':[{c['circuit']+'/'+c['arm']:c['input_sha256']} for c in checks]})
    print(json.dumps({'curves':72,'actual_sta':6858,'points':len(allpoints),'commits':len(allcommits),
        'cached_commits':sum(c['cached_commits'] for c in checks),
        'accepted_not_committed':sum(c['accepted_but_not_committed'] for c in checks),
        'output':str(out)}))


if __name__=='__main__':main()
