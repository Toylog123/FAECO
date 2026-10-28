"""Independent data recomputation and root visual acceptance of D pilot figure."""
from pathlib import Path
import csv,json,hashlib
BASE=Path('paper/zh/figures/data/previews/r22_D_feedback_mechanism_v1')
FINAL=BASE/'iteration02'
EXP=Path('experiments/20261018_r22_D_revalidate_v1/D')
READ={}
def raw(p):
    p=Path(p);b=p.read_bytes();k=p.as_posix();v=hashlib.sha256(b).hexdigest()
    if k in READ:assert READ[k]==v
    READ[k]=v;return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
def csvrows(p):return list(csv.DictReader(raw(p).decode('utf-8-sig').splitlines()))
receipt=load(BASE/'FINAL_RECEIPT.json')
assert receipt['selected_iteration']=='iteration02' and receipt['source_bindings_stable_at_finish']
for name,record in receipt['artifacts'].items():assert hashlib.sha256(raw(BASE/name)).hexdigest()==record['sha256']
for name,expected in load(FINAL/'INPUT_BINDINGS.json').items():assert hashlib.sha256(raw(Path(name))).hexdigest()==expected
root=load('project_docs/evidence/r22_D_revalidation_20261018/ROOT_COMPLETION_AUDIT_14.json')
weight_rows=csvrows(FINAL/'weights_all_80.csv');diag_rows=csvrows(FINAL/'matched_rounds_40.csv');summary=csvrows(FINAL/'evaluation_sequences_2.csv')
assert (len(weight_rows),len(diag_rows),len(summary))==(80,40,2)
checks=[]
for circuit in ['s27','s382']:
    results={};ledgers={}
    for arm in ['fixed','adaptive']:
        run=EXP/arm/circuit
        assert hashlib.sha256(raw(run/'completion.json')).hexdigest()==root['completion_set_frozen_at_start'][f'D/{arm}/{circuit}']
        results[arm]=load(run/'outerloop_result.json');ledgers[arm]=load(run/'eval_trials.json')
        expected=results[arm]['weights_trace']
        rows=[r for r in weight_rows if r['circuit']==circuit and r['arm']==arm]
        assert len(rows)==len(expected)==20
        for r,w in zip(rows,expected):
            assert int(r['round'])==w['round_id']
            for field in ['boundary_penalty','size_penalty','critical_coverage_reward']:assert float(r[field])==w[field]
    rounds={arm:results[arm]['candidate_pool_trace'] for arm in ['fixed','adaptive']}
    seen={};changed=[]
    for idx,row in enumerate([r for r in diag_rows if r['circuit']==circuit]):
        f,a=[rounds[arm][idx] for arm in ['fixed','adaptive']]
        assert f['round']==a['round']==int(row['round']) and f['base_netlist_hash']==a['base_netlist_hash']
        order=f['dispatch_hashes']!=a['dispatch_hashes'];sets=set(f['dispatch_hashes'])!=set(a['dispatch_hashes'])
        previous=seen.setdefault(a['base_netlist_hash'],set());new=bool(set(a['dispatch_hashes'])-previous)
        assert int(row['order_differs_from_fixed'])==int(order) and int(row['set_differs_from_fixed'])==int(sets)
        assert int(row['unseen_dispatch_at_same_base'])==int(new)
        previous.update(a['dispatch_hashes'])
        if order:changed.append(a['round'])
    s=next(r for r in summary if r['circuit']==circuit)
    for arm in ['fixed','adaptive']:
        assert int(s[arm+'_candidate_records'])==len(ledgers[arm]['trials'])
        assert int(s[arm+'_new_candidate_sta'])==len(ledgers[arm]['sta_launch_events'])==results[arm]['n_new_sta_runs']
    trial_fields=['candidate_hash','base_netlist_hash','kind','instance','patch_id','accepted','committed','sta_executed']
    event_fields=['seq','kind','candidate_hash','base_netlist_hash','wns','tns','error','timeout','status']
    for array,fields in [('trials',trial_fields),('sta_launch_events',event_fields)]:
        values={arm:[[r.get(k) for k in fields] for r in ledgers[arm][array]] for arm in ['fixed','adaptive']}
        assert values['fixed']==values['adaptive']
    first=next(w['round_id'] for w in results['adaptive']['weights_trace'] if any(w[k]!=1 for k in ['boundary_penalty','size_penalty','critical_coverage_reward']))
    assert first==int(s['first_weight_change_round'])
    assert not any(int(r['unseen_dispatch_at_same_base']) for r in diag_rows if r['circuit']==circuit and int(r['round'])>=first)
    checks.append({'circuit':circuit,'weight_change_round':first,'dispatch_order_changed_rounds':changed,'raw_counts_and_sequences_match':True})
assert load(FINAL/'PANEL_ALIGNMENT.json')['verdict']=='PASS'
assert load(FINAL/'COLLISION_AUDIT.json')['summary']=={'fail':0,'warn':0,'contained_fill_overlays':0,'contained_image_overlays':0}
glyph=load(FINAL/'PDF_GLYPH_AUDIT.json');assert glyph['minimum_found_pt']==7 and glyph['below_minimum_count']==0
for name,value in READ.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==value
out={'accepted':True,'scope':'Two-case D/beam8 diagnostic preview only; no manuscript integration or full-D56 efficacy inference',
 'independent_raw_data_checks':checks,'csv_rows':[80,40,2],'all_read_artifacts_stable':True,'read_sha256':READ,
 'visual_review':{'root_inspected':['iteration02/r22_D_feedback_mechanism.png','iteration02/PDF_RENDER_200dpi.png'],
 'whole_figure_and_four_panels':'Readable aligned axes, no clipping/overlap, coincident weights distinguishable by alternating markers; caption defines new dispatch at same base and excludes new STA interpretation',
 'minimum_pt':7,'alignment_and_collision_pass':True},'caption_scope_and_record_vs_new_STA_labels_accepted':True}
with (BASE/'ROOT_FIGURE_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'accepted':True,'checks':checks,'read_artifacts':len(READ)}))
