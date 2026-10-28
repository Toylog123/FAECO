"""Bounded PDF synchronization and current submission metadata, preserving prior bytes."""
from pathlib import Path
import hashlib,json,shutil,time

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(path,value,exclusive=False):
    with path.open('x' if exclusive else 'w',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
qa_path=OUT/'FINAL_QA_v2.json';qa=load(qa_path);before=OUT/'sync_before';before.mkdir(exist_ok=False)
for row in qa['languages'].values():assert sha(ROOT/row['source'])==row['source_sha256'] and sha(ROOT/row['pdf'])==row['pdf_sha256']
submission=ROOT/'paper/en/submission'
for name in ('source_binding.json','build_metrics.json','BUILD_DIAGNOSTICS.md','draft_checks.json'):
    shutil.copy2(submission/name,before/name)
zhpdf=ROOT/qa['languages']['zh']['pdf'];enpdf=ROOT/qa['languages']['en']['pdf'];canon=ROOT/'paper/en/build/FAECO.pdf'
copies=[]
targets=[(zhpdf,ROOT/'paper/zh'/zhpdf.name),(zhpdf,ROOT/'paper/zh/manuscript'/zhpdf.name),(enpdf,canon)]
for index,(source,target) in enumerate(targets):
    old=sha(target) if target.exists() else None
    if target.exists():shutil.copy2(target,before/f'pdf{index}_{target.name}')
    attempts=[];success=False
    for attempt in range(1,4):
        try:
            shutil.copy2(source,target);assert sha(target)==sha(source);success=True
            attempts.append({'attempt':attempt,'success':True});break
        except PermissionError as exc:
            attempts.append({'attempt':attempt,'success':False,'error':str(exc)})
            if attempt<3:time.sleep(2)
    copies.append({'source':rel(source),'target':rel(target),'before_sha256':old,'expected_sha256':sha(source),'actual_sha256':sha(target) if target.exists() else None,'synchronized':success,'attempts':attempts})
    print(json.dumps(copies[-1],ensure_ascii=False),flush=True)
# Preserve and synchronize ancillary logs only when the canonical PDF is current.
ancillary=[]
if copies[-1]['synchronized']:
    for source in sorted(enpdf.parent.glob('FAECO.*')):
        if source.suffix=='.pdf':continue
        target=canon.parent/source.name
        if target.exists():shutil.copy2(target,before/('en_build_'+source.name))
        try:
            shutil.copy2(source,target);ancillary.append({'path':rel(target),'sha256':sha(target),'synchronized':True})
        except PermissionError as exc:ancillary.append({'path':rel(target),'synchronized':False,'error':str(exc)})
effective=canon if copies[-1]['synchronized'] else enpdf
binding=load(submission/'source_binding.json')
binding.update(date='2026-10-18',translation_source_current_sha256=qa['languages']['zh']['source_sha256'],english_manuscript_sha256=qa['languages']['en']['source_sha256'],results_cutoff='r21 timing/result set with archived B provenance and actual clock metadata; A SEC points and prover wall time replaced by one accepted 2026-10-18 exact-object batch. No new WNS or B3/C/D result inserted.')
binding['r22_A_SEC_metadata_correction']={'scope':qa['scope'],'qa':rel(qa_path),'qa_sha256':sha(qa_path),'proof_sources_sha256':qa['A8_sources_sha256'],'pdf':rel(effective),'pdf_sha256':sha(effective),'canonical_english_pdf_synchronized':copies[-1]['synchronized']}
write(submission/'source_binding.json',binding)
metrics=load(submission/'build_metrics.json');diag=qa['languages']['en']['diagnostics']
metrics.update(date='2026-10-18',latest_compile_exit_code=0,pdf_path=rel(effective),pdf_sha256=sha(effective),pdf_bytes=effective.stat().st_size,pages=qa['languages']['en']['pages'],english_source_sha256=qa['languages']['en']['source_sha256'],rendered_pages=qa['languages']['en']['pages'],scope='Working draft; accepted unified A8 SEC metadata and measured A figure/table layout; remaining scientific evidence and author inputs pending',r22_A_SEC_metadata_qa=rel(qa_path),r22_A_SEC_metadata_qa_sha256=sha(qa_path),canonical_pdf_synchronized=copies[-1]['synchronized'])
metrics.update(overfull_boxes=diag['overfull_boxes'],underfull_boxes=diag['underfull_boxes'],missing_character=diag['missing_character'],undefined_references_or_citations=diag['undefined_refs_or_citations'],rerun_warning=diag['rerun_warning'],latex_or_package_warnings=len(diag['latex_warnings']))
write(submission/'build_metrics.json',metrics)
path=submission/'BUILD_DIAGNOSTICS.md';text=path.read_text(encoding='utf-8')
text=text.replace('Rebuilt and checked on 16 October 2026 after correcting clock-period metadata.','Rebuilt and checked on 18 October 2026 after updating the A-family sequential-equivalence metadata from one accepted batch.')
text=text.replace('The numerical result set is r21.','Timing gains and candidate counts retain the r21 result set; the A SEC table uses the accepted unified eight-pair proof batch of 18 October 2026.')
text+='\nThe 18 October A SEC correction changes the functionality sentence and proof table in each language. All eight exact baseline/final pairs have nonzero proven points and zero unproven points with Yosys 0.33. The same-batch prover wall times exclude mapping, candidate STA and model preparation. The other 13 tables and all figure artwork remain unchanged. The English inclusion width of Figure 3 is 0.70 linewidth, with an actual minimum plot-label size of 7.34552 pt; Figure 3 and Table 8 share page 15 and the next experiment starts on page 16. The final 12 Chinese and 26 English pages were rendered and visually inspected, including high-resolution proof-table checks. Failed and intermediate QA/build/layout attempts are preserved in `../../zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1/`; `FINAL_QA.json` binds the selected source/PDF bytes. No new timing experiment or B3/C/D result is inserted.\n'
if not copies[-1]['synchronized']:text+='\nThe canonical English build PDF remains write-locked. The validated current PDF is `'+rel(enpdf)+'`; build metrics bind this separate current output, not the old canonical file.\n'
path.write_text(text,encoding='utf-8')
receipt={'copies':copies,'english_build_ancillary':ancillary,'effective_english_pdf':rel(effective),'effective_english_pdf_sha256':sha(effective),'metadata':{rel(submission/name):sha(submission/name) for name in ('source_binding.json','build_metrics.json','BUILD_DIAGNOSTICS.md','draft_checks.json')},'FINAL_QA_sha256':sha(qa_path),'all_three_PDF_copies_synchronized':all(r['synchronized'] for r in copies)}
write(OUT/'SYNC_RECEIPT.json',receipt,exclusive=True)
print(json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
