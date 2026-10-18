"""Read-only matched-state diagnostic; no EDA or campaign mutations."""
import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/'experiments/20261016_r22_cut_ablation_v3'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=load(D/'manifest.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
assert head==m['git_head']
rows=[];files={}
for c in m['circuits']:
 for w,u in [('W0','U0'),('W1','U1')]:
  paths=[D/a/c/'outerloop_result.json' for a in (w,u)]
  if not all((p.parent/'completion.json').is_file() for p in paths):continue
  a,b=map(load,paths)
  for p in paths:files[str(p.relative_to(R))]=sha(p)
  for r in (a,b):assert r['state']['current_wns']==r['wns']
  by={r['base_netlist_hash']:r for r in b['candidate_pool_trace']}
  # Retain each weighted round, even repeated states; do not call these independent samples.
  matches=[]
  for t in a['candidate_pool_trace']:
   v=by.get(t['base_netlist_hash'])
   if v is None:continue
   wc=[s['node_costs'] for s in t['subcones']]
   uc=[s['node_costs'] for s in v['subcones']]
   assert all(all(abs(z-1)<1e-12 for z in s.values()) for s in uc)
   nonuniform=any(len({round(z,12) for z in s.values()})>1 for s in wc)
   def cuts(t):return [[x['cut_hash'] for x in s['candidates']] for s in t['subcones']]
   matches.append({'weighted_round':t['round'],'uniform_round_at_same_state':v['round'],
    'base_netlist_hash':t['base_netlist_hash'],'weighted_nonuniform_node_costs':nonuniform,
    'same_subcone_cut_hash_lists':cuts(t)==cuts(v),
    'same_ordered_pool':t['pool_hashes']==v['pool_hashes'],
    'same_dispatch_order':t['dispatch_hashes']==v['dispatch_hashes']})
  rows.append({'circuit':c,'pair':[w,u],'weighted_rounds':len(a['candidate_pool_trace']),
    'uniform_rounds':len(b['candidate_pool_trace']),'matched_state_rounds':matches,
    'same_endpoint_hash':a['state']['current_netlist_hash']==b['state']['current_netlist_hash'],
    'weighted_final_wns':a['wns'],'uniform_final_wns':b['wns'],
    'weighted_candidate_sta':a['n_new_sta_runs'],'uniform_candidate_sta':b['n_new_sta_runs']})
assert all(sha(R/k)==v for k,v in files.items())
report={'head':head,'manifest_sha256':sha(D/'manifest.json'),'status':'partial diagnostic; not final matrix acceptance',
 'eda_executed':False,'pairs':rows,'input_sha256':files,'auditor_sha256':sha(Path(__file__)),
 'interpretation_limits':['Comparisons are only at byte-hash-identical base states.',
 'Repeated rounds at one state are not independent observations.',
 'Same endpoint does not establish identical trajectories; candidate and dispatch hashes are checked separately.',
 'No causal weighting benefit follows from equal endpoints; unfinished circuits are excluded.']}
out=R/'project_docs/evidence/r22_cprime_v3_20261016/mechanism_audits'
out.mkdir(exist_ok=True)
target=out/('MATCHED_STATE_PAIRS_%02d.json'%len(rows))
with target.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(target),'pairs':len(rows),'details':[
 {'circuit':r['circuit'],'pair':r['pair'],'matched_rounds':len(r['matched_state_rounds']),
 'nonuniform_rounds':sum(t['weighted_nonuniform_node_costs'] for t in r['matched_state_rounds']),
 'cut_differences':sum(not t['same_subcone_cut_hash_lists'] for t in r['matched_state_rounds']),
 'pool_differences':sum(not t['same_ordered_pool'] for t in r['matched_state_rounds']),
 'dispatch_differences':sum(not t['same_dispatch_order'] for t in r['matched_state_rounds']),
 'same_endpoint_hash':r['same_endpoint_hash']} for r in rows]},ensure_ascii=False))
