"""Read-only diagnosis of frozen ROOT28 ledger duplicate schema; no EDA/imports from production."""
from pathlib import Path
import collections,hashlib,json,re,time

R=Path.cwd();O=R/'project_docs/evidence/r22_D_revalidation_20261018/ledger_duplicate_diagnosis_20261018';O.mkdir(exist_ok=False)
READ={};sha=lambda b:hashlib.sha256(b).hexdigest()
def raw(p):
    p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();name=p.relative_to(R).as_posix();v={'bytes':len(b),'sha256':sha(b)}
    assert name not in READ or READ[name]==v;READ[name]=v;return b
def txt(p):return raw(p).decode('utf-8-sig').replace('\r\n','\n')
def load(p):return json.loads(txt(p))
def save(name,v):
    with (O/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
started=time.monotonic();audit=load('project_docs/evidence/r22_D_revalidation_20261018/ROOT_COMPLETION_AUDIT_28.json');m=load('experiments/20261018_r22_D_revalidate_v1/manifest.json');selected=set(audit['completion_set_frozen_at_start']);assert len(selected)==28
for p in ['code/src/rseco/real_wns.py','code/src/rseco/sta_ledger.py','code/src/rseco/flow.py','project_docs/evidence/r22_D_revalidation_20261018/independent_completed_review/checker_v2.py','project_docs/evidence/r22_D_revalidation_20261018/independent_completed_review/run_28_v1/WRAPPER.log']:
    b=raw(p);(O/('source_'+Path(p).name)).write_bytes(b)
for p,d in m['source_pin']['files'].items():assert sha(raw(p))==d
rootrows={x['key']:x for x in audit['jobs']};rows=[];details=[];total=collections.Counter()
for job in m['jobs']:
    if job['key'] not in selected:continue
    p=Path(job['output_dir']);done=load(p/'completion.json');assert sha(raw(p/'completion.json'))==audit['completion_set_frozen_at_start'][job['key']]
    ledger=load(p/'eval_trials.json');result=load(p/'outerloop_result.json');config=load(p/'run_config.json')
    for name,digest in {**done['evidence_receipt'],**done['extra_receipt']}.items():assert sha(raw(p/name))==digest
    ts=ledger['trials'];events={e['seq']:e for e in ledger['sta_launch_events']};assert len(events)==len(ledger['sta_launch_events'])
    measured={t['sta_launch_seq']:(i,t) for i,t in enumerate(ts) if t.get('sta_executed') is True}
    assert set(events)==set(measured)
    byiteration=collections.OrderedDict()
    for i,t in enumerate(ts):byiteration.setdefault(t['iteration'],[]).append((i,t))
    current=sha(txt(p/'mapped.v').encode());inferred={}
    for iteration,group in byiteration.items():
        for i,t in group:
            if 'base_netlist_hash' in t:assert t['base_netlist_hash']==current,(job['key'],i,'base chain')
            inferred[i]=current
        commits=[t for i,t in group if t.get('committed') is True];assert len(commits)<=1
        if commits:current=commits[0]['candidate_hash']
    assert current==result['state']['current_netlist_hash']
    categories=collections.Counter();prior_bykey={}
    for i,t in enumerate(ts):
        skipped=t.get('skipped_duplicate') is True;seq=t.get('cached_from_seq')
        if skipped:
            assert t.get('sta_executed') is False and t.get('sta_launch_seq') is None
            assert sha(t['candidate_netlist_text'].encode())==t['candidate_hash']
            base=inferred[i];assert sha((base+t['candidate_hash']+t['config_hash']).encode())==t['cache_key']
            if seq is not None:
                origin=events[seq];oi,ot=measured[seq]
                assert origin['candidate_hash']==t['candidate_hash'] and origin['base_netlist_hash']==t['base_netlist_hash']==base
                assert ot['cache_key']==t['cache_key'] and ot['config_hash']==t['config_hash'] and oi<i
                category='STA_cache_reuse_from_launch'
            elif 'cached_from_seq' in t:
                candidates=[(pi,pt) for pi,pt in prior_bykey.get(t['cache_key'],[]) if pt.get('sta_executed') is False and not pt.get('skipped_duplicate') and pt.get('failure_events')]
                assert candidates,(job['key'],i,'cached preSTA missing original failure')
                category='cached_pre_STA_rejection';oi,ot=candidates[0]
                details.append({'job':job['key'],'trial_index_0based':i,'category':category,'origin_trial_index_0based':oi,'failure_events':ot['failure_events'],'cache_key':t['cache_key'],'base_hash':base})
            else:
                assert 'base_netlist_hash' not in t and t['runtime_s']==0 and not t.get('failure_events') and not t.get('trial_failure_events') and t.get('accepted') is False and t.get('committed') is False
                origins=[(oi,ot,events[s]) for s,(oi,ot) in measured.items() if oi<i and ot['candidate_hash']==t['candidate_hash'] and ot['config_hash']==t['config_hash']]
                assert origins,(job['key'],i,'missing identity origin')
                origin_details=[]
                for oi,ot,e in origins:
                    mapped=Path(e['report_dir'])/'mapped.v';log=Path(e['report_dir'])/'sta.log';tcl=Path(e['report_dir'])/'sta.tcl'
                    assert sha(txt(mapped).encode())==t['candidate_hash'];sl=txt(log);txt(tcl)
                    w=re.findall(r'(?m)^worst slack max\s+([-+0-9.eE]+)\s*$',sl);assert len(w)==1 and abs(float(w[0])-e['wns'])<1e-9
                    assert e['status']=='completed' and not e['error'] and not e['timeout']
                    origin_details.append({'trial_index_0based':oi,'launch_seq':e['seq'],'base_hash':e['base_netlist_hash'],'cache_key':ot['cache_key'],'config_hash':ot['config_hash'],'wns':e['wns'],'report_dir':str(Path(e['report_dir']).relative_to(R)),'actual_mapped_and_STA_log_read':True})
                category='tested_hash_dedup_without_replay'
                details.append({'job':job['key'],'trial_index_0based':i,'category':category,'iteration':t['iteration'],'candidate_hash':t['candidate_hash'],'config_hash':t['config_hash'],'cache_key':t['cache_key'],'base_hash_missing_in_raw_trial':True,'inferred_base_hash':base,'base_inference_evidence':'Exact initial mapped SHA plus ordered explicitly committed trial chain; independently matches cache_key=SHA256(base+candidate+config). No raw field filled.','origin_measured_trials':origin_details,'placeholder_wns':t['wns'],'actual_STA_executed_by_this_record':False,'accepted':t['accepted'],'committed':t['committed'],'workers':config['resolved_args']['workers']})
            categories[category]+=1
        elif t.get('sta_executed') is True:categories['new_candidate_STA_launch']+=1
        else:categories['uncached_pre_STA_rejection']+=1
        if t.get('cache_key'):prior_bykey.setdefault(t['cache_key'],[]).append((i,t))
    legacy=sum(v for k,v in categories.items() if k in ('STA_cache_reuse_from_launch','cached_pre_STA_rejection','tested_hash_dedup_without_replay'))
    assert legacy==done['accounting']['n_cache_replays']==result['n_cache_replays']==rootrows[job['key']]['n_cache_replays']
    assert categories['new_candidate_STA_launch']==len(events)==done['accounting']['n_new_sta_runs']
    assert sum(categories.values())==len(ts)
    row={'key':job['key'],'trials':len(ts),'actual_STA_launches':len(events),'reported_legacy_n_cache_replays':legacy,**dict(categories)};rows.append(row);total.update(categories)
    print(json.dumps(row),flush=True)
before=dict(READ)
for name,v in before.items():assert {'bytes':len(raw(name)),'sha256':sha(raw(name))}==v
save('READ_SHA_MANIFEST.json',before);save('DUPLICATE_DETAILS.json',details)
save('DIAGNOSIS.json',{'scope':'ROOT28 immutable frozen subset only; new completions not reviewed','root28_sha256':READ['project_docs/evidence/r22_D_revalidation_20261018/ROOT_COMPLETION_AUDIT_28.json']['sha256'],'rows':rows,'totals':dict(total),'all_read_sources_stable':True,'read_files':len(before),'runtime_s':time.monotonic()-started,'cause':'checker_v2 assumes every skipped_duplicate record has an originating STA launch; production also records tested-candidate identity dedup and can cache pre-STA rejection','new_EDA_runs':0,'production_changed':False,'extra_completed_not_covered':[j['key'] for j in m['jobs'] if j['key'] not in selected and (Path(j['output_dir'])/'completion.json').is_file()]})
(O/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
save('INVOCATION.json',{'command':['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','180','.venv/Scripts/python.exe','scratch/diagnose_D_duplicate_1018.py'],'actual_scope':'Read-only ledger/source/artifact diagnosis; writes only this exclusive diagnosis directory.'})
print('TOTAL',json.dumps(dict(total)),flush=True)
