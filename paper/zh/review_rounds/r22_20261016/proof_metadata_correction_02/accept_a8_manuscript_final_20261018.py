"""Root acceptance of frozen independent manuscript review and current copies."""
from pathlib import Path
import json,hashlib,subprocess,re
import pymupdf
ROOT=Path.cwd().resolve();BASE=ROOT/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02'
REVIEW=BASE/'independent_final_review';AUTHOR=BASE/'actual_correction_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
final=read(REVIEW/'FINAL_RECEIPT.json')
assert sha(REVIEW/'FINAL_RECEIPT.json')=='334a893b1a561c51486b4d90e4f781e7b962bcd8f0e0fc8cefae362778bc4953'
assert final['wrapper_returncode']==0 and final['all_read_sources_stable'] and final['actual_visual_pages']==38
for item in final['artifacts']:
    p=REVIEW/item['path'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
sources=read(REVIEW/'attempt1/READ_AFTER.json')
assert len(sources)==562
for name,item in sources.items():
    p=Path(name);assert p.is_relative_to(ROOT) and sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
author=read(AUTHOR/'FINAL_RECEIPT.json')
assert sha(AUTHOR/'FINAL_RECEIPT.json')=='bc95133872e4365ebf8b6b20e379345f54e74df4ad5e065c816bdd5b36c34c23'
for name,digest in author['final_paths_sha256'].items():assert sha(ROOT/name)==digest
qa=read(AUTHOR/'FINAL_QA_v2.json');proof=read(ROOT/'project_docs/evidence/r22_a_sec_unified_20261018/RUN_RECEIPT.json')
results={}
for lang,page_no in [('zh',8),('en',15)]:
    entry=qa['languages'][lang];pdf=ROOT/('paper/en/build/FAECO.pdf' if lang=='en' else entry['pdf'])
    assert sha(ROOT/entry['source'])==entry['source_sha256'] and sha(pdf)==entry['pdf_sha256']
    with pymupdf.open(pdf) as doc:
        assert len(doc)==(26 if lang=='en' else 12)
        page=doc[page_no-1];text=page.get_text()
        for row in proof['rows']:
            pattern=rf"{row['circuit']}\s+{row['proven']}\s*/\s*0\s+(?:Proven|通过)\s+{row['runtime_s']:.3f}"
            assert re.search(pattern,text), (lang,row['circuit'])
        results[lang]={'pdf_sha256':sha(pdf),'pages':len(doc),'table_page':page_no,'eight_rows_read_back_by_root':True}
        if lang=='en':
            spans=[s for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for s in line['spans'] if 'Arial' in s['font']]
            assert len(spans)==29 and min(s['size'] for s in spans)>=6.8
            assert 'Cross-dataset evaluation' not in page.get_text() and 'Cross-dataset evaluation' in doc[15].get_text()
            results[lang]['actual_plot_min_pt']=min(s['size'] for s in spans)
manifest=read(ROOT/'experiments/20261018_r22_D_revalidate_v1/manifest.json')
for name,digest in manifest['source_pin']['files'].items():assert sha(ROOT/name)==digest
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==manifest['source_pin']['head']
record={'accepted':True,'scope':'A8 SEC sentence/table, measured EN Figure3 placement, compiled PDF copies and associated metadata only. Other scientific gates and submission readiness remain open.','author_final_sha256':sha(AUTHOR/'FINAL_RECEIPT.json'),'independent_final_sha256':sha(REVIEW/'FINAL_RECEIPT.json'),'independent_artifacts_current_verified':len(final['artifacts']),'independent_read_sources_current_verified':len(sources),'root_actual_PDF_readback':results,'root_visual_images_actually_viewed':['actual_correction_v1/en_float_refinement_v5/en_renders/A_SEC_full_page_180dpi.png','actual_correction_v1/en_float_refinement_v5/en_renders/contact_04.png'],'bilingual_all_38_pages_visual_review_by_independent_owner':True,'source_HEAD':manifest['source_pin']['head'],'all45_runtime_source_unchanged':True,'OI050_may_close_only_this_scope':True}
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
with (BASE/'ROOT_MANUSCRIPT_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'accepted':True,'receipt_sha256':sha(BASE/'ROOT_MANUSCRIPT_ACCEPTANCE.json'),'root_PDF_checks':results}))
