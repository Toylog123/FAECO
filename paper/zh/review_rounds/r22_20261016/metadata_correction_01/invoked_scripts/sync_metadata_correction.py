from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
base=R/'paper/zh/review_rounds/r22_20261016/metadata_correction_01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((base/'FINAL_QA.json').read_text())['layout_passed']
assert not (base/'SYNC_RECEIPT.json').exists()
zh=json.loads((base/'zh_build_receipt.json').read_text());en=json.loads((base/'en_build_receipt.json').read_text())
pdf=R/zh['pdf'];assert sha(pdf)==zh['pdf_sha256'];copies=[]
for label,folder in [('root',R/'paper/zh'),('manuscript',R/'paper/zh/manuscript')]:
    target=folder/pdf.name;old=sha(target) if target.is_file() else None
    if old and old!=sha(base/'zh_before.pdf'):
        backup=base/('zh_'+label+'_precopy.pdf');assert not backup.exists();shutil.copyfile(target,backup)
    shutil.copyfile(pdf,target);assert sha(target)==zh['pdf_sha256']
    copies.append({'path':target.relative_to(R).as_posix(),'before_sha256':old,'after_sha256':sha(target)})
for name in ['source_binding.json','build_metrics.json','BUILD_DIAGNOSTICS.md']:
    backup=base/('en_'+name+'_before');assert not backup.exists();shutil.copyfile(R/'paper/en/submission'/name,backup)
bindpath=R/'paper/en/submission/source_binding.json';b=json.loads(bindpath.read_text())
b.update(date='2026-10-16',translation_source_current_sha256=zh['source_sha256'],english_manuscript_sha256=en['source_sha256'],
         results_cutoff='r21 numerical results; archived B-count provenance and actual clock-period metadata corrected; no r22 EDA result inserted')
b['r22_clock_period_metadata_correction']={'scope':'ISCAS89/ITC-99 .5ns; Pico core5ns/multiplier2ns/registers.5ns; per-circuit baseline and repair share constraints',
    'receipt':(base/'FINAL_QA.json').relative_to(R).as_posix(),'receipt_sha256':sha(base/'FINAL_QA.json'),
    'supporting_audits':[(base.parent/name).relative_to(R).as_posix() for name in ['TIMING_CONSTRAINT_CHECK.json','TIMING_CONSTRAINT_MAIN27.json']]}
bindpath.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
metrics=R/'paper/en/submission/build_metrics.json';m=json.loads(metrics.read_text())
m.update(latest_compile_exit_code=0,pdf_sha256=en['pdf_sha256'],english_source_sha256=en['source_sha256'],
    pdf_bytes=(R/en['pdf']).stat().st_size,pages=26,rendered_pages=26,
    scope='Metadata-corrected working draft; scientific evidence repair and author inputs pending',
    r22_metadata_qa=(base/'FINAL_QA.json').relative_to(R).as_posix())
metrics.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'paper/en/submission/BUILD_DIAGNOSTICS.md';s=p.read_text(encoding='utf-8')
changes=[('Checked on 14 October 2026.','Rebuilt and checked on 16 October 2026 after correcting clock-period metadata.'),
    ('The sole later factual correction is the explicitly authorized distinction between','Later factual corrections include the actual PicoRV32 periods (core 5 ns, multiplier 2 ns, register bank 0.5 ns) and the distinction between'),
    ('produces 27 pages','produces 26 pages'),('All 27 pages','All 26 pages'),
    ('This package has not been submitted, uploaded, committed or pushed by the English-preparation agent.','The manuscript has not been submitted. Current scientific evidence repair follows the r22 claim-to-evidence map.')]
for old,new in changes:
    assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
s+='\nThe 16 October metadata correction preserves all 14 numerical table bodies and seven figure references. All 38 pages across the Chinese and English drafts were rendered, with detailed inspection of the changed setting and figure-4 caption pages. Exact receipts, prior PDFs and edit snapshots are retained in the r22 metadata-correction evidence package.\n'
p.write_text(s,encoding='utf-8')
receipt={'chinese_pdf_copies':copies,'english_pdf_sha256':sha(R/en['pdf']),
    'english_metadata_updated':['source_binding.json','build_metrics.json','BUILD_DIAGNOSTICS.md','draft_checks.json'],
    'final_qa_sha256':sha(base/'FINAL_QA.json'),'scientific_status':'Working drafts; remaining historical evidence not yet repaired'}
with (base/'SYNC_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps(receipt,ensure_ascii=False))
