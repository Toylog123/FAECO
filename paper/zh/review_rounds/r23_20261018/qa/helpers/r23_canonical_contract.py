from pathlib import Path
import hashlib,json,datetime
root=Path.cwd().resolve();r=root/'paper/zh/review_rounds/r23_20261018';s=Path('C:/Users/16225/.codex/skills/academic-research-skills');out=root/'scratch/r23_canonical_skill'
sha=lambda b:hashlib.sha256(b).hexdigest()
full=s/'shared/contracts/reviewer/full.json';before=full.read_bytes();canonical=before.replace(b'\r\n',b'\n')
assert sha(canonical)=='e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af'
assert json.loads(before)==json.loads(canonical)
files=['scripts/review_panel_provenance.py', 'shared/contracts/reviewer/full.json',*[f'shared/contracts/reviewer/{name}' for name in ['review_panel_provenance_input.schema.json','review_panel_provenance.schema.json','review_panel_provenance_carrier.schema.json']]]
copies=[]
for rel in files:
    src=s/rel;dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    assert not dest.exists();raw=src.read_bytes();new=canonical if src==full else raw;dest.write_bytes(new)
    copies.append({'source':str(src),'copy':str(dest),'source_sha256':sha(raw),'copy_sha256':sha(new),'only_crlf_to_lf':src==full})
input1=json.loads((r/'PANEL_PROVENANCE_INPUT.json').read_text(encoding='utf-8'));input1['contract_sha256']=sha(canonical)
(r/'PANEL_PROVENANCE_INPUT_CANONICAL.json').write_text(json.dumps(input1,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'qa/CANONICAL_CONTRACT_RECOVERY.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cause':'Windows installed full.json CRLF differs from raw LF pin; first build/validation failures preserved.','recovery':'Isolated copy of unmodified validator and schemas, full.json ONLY CRLF->LF; exact pinned digest and JSON semantic equality checked; installed skills, project source and runtime contract not edited.','files':copies},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'qa/full.canonical.json').write_bytes(canonical)
print(json.dumps({'original_sha256':sha(before),'canonical_sha256':sha(canonical),'semantic_equality':True,'validator_bytes_unchanged':True}))
