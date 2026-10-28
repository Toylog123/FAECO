from pathlib import Path
import json,hashlib,datetime
r=Path('paper/zh/review_rounds/r23_20261018'); s=Path('C:/Users/16225/.codex/skills/academic-research-skills')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roster=[('EIC','eic','/root/r23_fit'),('R1','methodology','/root/r23_method'),('R2','domain','/root/r23_domain'),('R3','perspective','/root/r23_perspective'),('DA','da','/root/r23_da')]
seats=[]; artifacts=[]
for seat,role,context in roster:
    for phase in ['phase1','phase2']:
        p=r/f'seats/{role}_{phase}.md'; artifacts.append({'seat':seat,'phase':phase,'path':str(p.relative_to(r)).replace('\\','/'),'sha256':sha(p)})
        assert json.loads((r/f'qa/{role}_{phase}/RECEIPT.json').read_text(encoding='utf-8'))['returncode']==0
    seats.append({'seat_id':seat,'role_id':role,'context_id':context,'peer_outputs_visible':False,'actor_type':'model','model_family':None,'provider':None,'human_reviewer_id':None})
data={'schema_version':'review-panel-provenance-input/1.0','panel_id':'r23-20261018-zh','mode':'reviewer_full','contract_id':'reviewer/reviewer_full/v2','contract_sha256':sha(s/'shared/contracts/reviewer/full.json'),'seats':seats}
with (r/'PANEL_PROVENANCE_INPUT.json').open('x',encoding='utf-8') as f:f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifacts':artifacts,'freshness_scope':'within_panel_attempt_only','visibility_basis':'Five explicit fork-none contexts, restricted per-seat paths, no peer outputs transmitted before commitments, seat read receipts. Prompt-level boundary; no filesystem access guard was installed.','identity_basis':'Canonical task context paths returned by collaboration tools; no actual runtime family/provider identifiers returned. Intended inherited route is not observed model diversity.','calibration_status':'NOT_CALIBRATED'}
(r/'PANEL_COMMIT_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'seats_committed':5,'phase_gates_passed':10,'contract_sha256':data['contract_sha256']}))
