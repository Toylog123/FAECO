from pathlib import Path
import json,hashlib,datetime,subprocess,shutil
root=Path.cwd();r=root/'paper/zh/review_rounds/r23_20261018';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((r/'qa/panel_synthesis_final/RECEIPT.json').read_text())['returncode']==0
assert json.loads((r/'qa/roadmap_validate_projection_lf/RECEIPT.json').read_text())['returncode']==0
assert json.loads((r/'qa/schema6_provenance_validate/RECEIPT.json').read_text())['returncode']==0
report=r/'REVIEW_REPORT.md';before=sha(report);raw=(r/'qa/acronym_advisory/stdout.log').read_bytes()
assert b'## Attachment: Acronym Check' not in report.read_bytes()
with report.open('ab') as f:f.write(b'\n## Attachment: Acronym Check (advisory, #849)\n\n'+raw)
qa=r/'qa';saved=[]
for p in sorted((root/'scratch').glob('r23_*.py')):
    dest=qa/'helpers'/p.name;dest.parent.mkdir(exist_ok=True);assert not dest.exists();dest.write_bytes(p.read_bytes());saved.append({'path':str(dest.relative_to(r)).replace('\\','/'),'sha256':sha(dest)})
src=root/'scratch/r23_canonical_skill';dst=qa/'canonical_skill_snapshot';shutil.copytree(src,dst)
frozen=json.loads((r/'INPUT_RECEIPT.json').read_text(encoding='utf-8'));checks={}
for rel,expected in frozen['inputs'].items(): checks[rel]=sha(r/rel)==expected
checks['live_tex']=sha(root/frozen['source_path'])==frozen['source_sha256'];checks['live_pdf']=sha(root/frozen['pdf_path'])==frozen['pdf_sha256']
head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True,timeout=20).stdout.strip();checks['head']=head==frozen['source_head']
code_status=subprocess.run(['git','status','--porcelain','--','code'],capture_output=True,text=True,check=True,timeout=20).stdout;checks['code_status_clean']=not code_status.strip()
commits=json.loads((r/'PANEL_COMMIT_RECEIPT.json').read_text(encoding='utf-8'))['artifacts'];checks['all_seat_commits_unchanged']=all(sha(r/x['path'])==x['sha256'] for x in commits)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_pass':all(checks.values()),'source_head':head,'code_status':code_status,'review_verdict':'major_revision','findings':20,'roadmap_items':22,'must_fix':8,'should_fix':14,'report_before_advisory_sha256':before,'report_final_sha256':sha(report),'advisory_status':'did_not_run_unsupported_tex_input; exact printed advisory appended unchanged after decision and roadmap validation; excluded from findings and decision','decision_gate':json.loads((qa/'panel_synthesis_final/RECEIPT.json').read_text()),'saved_helpers':saved,'output_hashes':{n:sha(r/n) for n in ['REVISION_ROADMAP.json','REVISION_ROADMAP.md','REVIEW_PACKAGE.json','FINDING_INVENTORY.json','ROOT_EVIDENCE_CROSSCHECK.json','PANEL_PROVENANCE.json','PANEL_CARRIER.json']},'no_eda_or_source_mutation':True,'commit_push_performed':False}
(qa/'FINAL_REVIEW_RECEIPT.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps({'all_pass':receipt['all_pass'],'checks':checks,'report_final_sha256':receipt['report_final_sha256']},ensure_ascii=False))
assert receipt['all_pass']
