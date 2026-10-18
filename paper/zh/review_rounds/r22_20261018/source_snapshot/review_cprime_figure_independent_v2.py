from pathlib import Path
import csv,json,hashlib
from decimal import Decimal as D
root=Path.cwd();folder=root/'paper/zh/figures/data/previews/r22_matrix_gain_cost_v1';out=root/'paper/zh/review_rounds/r22_20261018';out.mkdir(exist_ok=True,parents=True);seen={}
def read(p):
 seen[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text(encoding='utf-8-sig')
def load(p):return json.loads(read(p))
a=load(root/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json');qa=load(folder/'QA.json');assert seen['project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json']==qa['audit_sha256']
for name,d in qa['exports_sha256'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==d;seen[(folder/name).relative_to(root).as_posix()]=d
raw=list(csv.DictReader(read(folder/'r22_matrix_gain_cost_raw.csv').splitlines()));paired=list(csv.DictReader(read(folder/'r22_matrix_gain_cost_paired.csv').splitlines()));assert len(raw)==72 and len(paired)==64
idx={(x['circuit'],x['arm']):x for x in raw};jobs={(x['circuit'],x['arm']):x for x in a['jobs']};assert len(idx)==72 and set(idx)==set(jobs)
for key,r in idx.items():
 j=jobs[key];assert D(r['baseline_wns_ns'])==D(str(j['baseline_wns']));assert D(r['final_wns_ns'])==D(str(j['final_wns']));assert D(r['wns_gain_ps'])==(D(str(j['final_wns']))-D(str(j['baseline_wns'])))*1000
 for x,y in [('candidate_ideal_sta','candidate_ideal_sta_launches'),('baseline_sta','baseline_sta_process_attempts'),('total_sta','total_sta_process_attempts'),('retained_commits','retained_commits')]:assert int(r[x])==j[y]
 assert r['completion_sha256']==j['completion_sha256'] and r['source_head']==a['head'];assert int(r['total_sta'])==int(r['candidate_ideal_sta'])+int(r['baseline_sta']);assert j['other_sta_process_attempts']==0
 p=root/'experiments/20261016_r22_cut_ablation_v3'/key[1]/key[0]/'completion.json';read(p);assert seen[p.relative_to(root).as_posix()]==r['completion_sha256']
assert len({(x['circuit'],x['contrast']) for x in paired})==64
for r in paired:
 left,right=r['contrast'].split('-');l,h=idx[r['circuit'],left],idx[r['circuit'],right];assert D(r['gain_difference_ps'])==D(l['wns_gain_ps'])-D(h['wns_gain_ps']);assert int(r['sta_difference'])==int(l['total_sta'])-int(h['total_sta']);assert r['left_completion_sha256']==l['completion_sha256'] and r['right_completion_sha256']==h['completion_sha256']
pidx={(r['circuit'],r['contrast']):r for r in paired};assert int(pidx['s27','W1-UR3']['sta_difference'])==5;assert int(pidx['s641','W1-C']['sta_difference'])==8
load(root/'project_docs/evidence/r22_cprime_v3_20261016/mechanism_audits/MATCHED_STATE_PAIRS_16.json');pairs=[]
for c in ['s27','s382','s420','s641','s713','s820','s832','s953']:
 for w,u in [('W0','U0'),('W1','U1')]:
  wr=load(root/'experiments/20261016_r22_cut_ablation_v3'/w/c/'outerloop_result.json');ur=load(root/'experiments/20261016_r22_cut_ablation_v3'/u/c/'outerloop_result.json');W=wr['candidate_pool_trace'];U=ur['candidate_pool_trace'];n=0
  for x in W:
   peers=[y for y in U if y['base_netlist_hash']==x['base_netlist_hash']];assert peers
   for y in peers:
    def cuts(z):return [[i['cut_hash'] for i in sc['candidates']] for sc in z['subcones']]
    n+=1;assert cuts(x)==cuts(y) and x['pool_hashes']==y['pool_hashes'] and x['dispatch_hashes']==y['dispatch_hashes']
  assert wr['state']['current_netlist_text']==ur['state']['current_netlist_text']
  pairs.append({'circuit':c,'weighted':w,'uniform':u,'weighted_rounds':len(W),'uniform_rounds':len(U),'all_same_base_cross_comparisons':n,'differences':0,'endpoint_text_equal':True})
read(folder/'README.md');read(folder/'VISUAL_REVIEW.json');glyph=load(folder/'PDF_GLYPH_AUDIT.json');sizes=[glyph['minimum_found_pt']];assert glyph['minimum_found_pt']>=5 and glyph['below_minimum_count']==0
assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in seen.items())
report={'date':'2026-10-18','status':'data and interpretation pass; PNG visually inspected; separate PDF render pending inspection','scope':'read-only independent review; no EDA/Git/plot modification','audit_all72_verified':a['all_matrix_verified'],'raw_rows_verified':72,'paired_rows_verified':64,'completion_hashes_verified':72,'pair_formula':'left minus right; Decimal ns * 1000; actual candidate + baseline STA','excluded':0,'adverse_comparisons':{'s27 W1-UR3 STA':5,'s641 W1-C STA':8},'matched_states_all_duplicate_uniform_rounds':pairs,'total_cross_comparisons':sum(x['all_same_base_cross_comparisons'] for x in pairs),'matched_report_limitation':'original report selects last uniform round per state; independently checked every matching uniform round here','PDF_pages':1,'PDF_min_font_pt_reused_glyph_audit':min(sizes),'PDF_font_below_5pt':sum(x<5 for x in sizes),'source_before':seen,'source_after_stable':True,'findings':[]}
with (out/'FIGURE_CPRIME_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({k:report[k] for k in ['raw_rows_verified','paired_rows_verified','total_cross_comparisons','PDF_min_font_pt_reused_glyph_audit','source_after_stable']}))
