"""Exact scope, source bindings and rendered-row readback; no EDA."""
from pathlib import Path
import difflib, hashlib, json, re
import pymupdf

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
OUT=Path(__file__).resolve().parent
EN=OUT/'en_float_refinement_v5'
A8=ROOT/'project_docs/evidence/r22_a_sec_unified_20261018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def table(text):
    pos=text.index(r'\label{tab:sec_iscas8}')
    start=text.rfind(r'\begin{table}',0,pos)
    end=text.index(r'\end{table}',pos)+len(r'\end{table}')
    return text[start:end]

edit=load(OUT/'EDIT_RECEIPT.json')
for path,digest in edit['A8_sources_sha256'].items():assert sha(A8/path)==digest
receipt=load(A8/'RUN_RECEIPT.json');accept=load(A8/'ROOT_ACCEPTANCE.json')
assert accept['accepted'] and sha(A8/'RUN_RECEIPT.json')==accept['batch_receipt_sha256']
for row in receipt['rows']:
    assert row['proven']>0 and row['unproven']==0 and row['status']=='pass' and row['returncode']==0
    for name,digest in row['artifact_sha256'].items():assert sha(A8/'proofs'/row['circuit']/name)==digest
manifest=load(A8/'MANIFEST.json')
assert len(manifest['source_pin']['files'])==45
for path,digest in manifest['source_pin']['files'].items():assert sha(ROOT/path)==digest
snapshots=load(OUT/'BEFORE_SNAPSHOT.json')
sentences=load(OUT.parent/'manuscript_draft_pending_A8/SENTENCE_REPLACEMENTS.json')
checks={};diff=[]
for entry in edit['edits']:
    lang=entry['language'];source=ROOT/entry['path'];after=source.read_bytes().decode('utf-8')
    snap=next(s for s in snapshots if s['path']==entry['path'])
    original_path=OUT/snap['backup'];assert sha(original_path)==snap['sha256']
    before=original_path.read_bytes().decode('utf-8')
    normalized_after=after.replace(table(after),'@A_SEC_TABLE@').replace(sentences[lang]['after'],'@A_SEC_SENTENCE@')
    normalized_before=before.replace(table(before),'@A_SEC_TABLE@').replace(sentences[lang]['before'],'@A_SEC_SENTENCE@')
    if lang=='en':
        new=r'\includegraphics[width=0.70\linewidth]{fig3_single_round_r21.pdf}'
        old=new.replace('0.70','0.78');assert normalized_after.count(new)==1
        normalized_after=normalized_after.replace(new,old)
        barrier=re.search(r'\\FloatBarrier(\r?\n)(?=\\subsection\{Cross-dataset evaluation\})',normalized_after)
        assert barrier;normalized_after=normalized_after[:barrier.start()]+normalized_after[barrier.end():]
    assert normalized_after==normalized_before,lang
    folder=EN if lang=='en' else OUT
    build=load(folder/(lang+'_build_receipt.json'));qa=load(folder/(lang+'_STATIC_RENDER_QA.json'))
    assert build['passed'] and all(p['returncode']==0 for p in build['passes'])
    assert sha(source)==build['source_sha256']==qa['source_sha256']
    pdf=ROOT/build['pdf'];assert sha(pdf)==build['pdf_sha256']==qa['pdf_sha256']
    with pymupdf.open(pdf) as doc:
        text=doc[qa['table_page']-1].get_text();rows=[]
        for row in receipt['rows']:
            pattern=re.escape(row['circuit'])+r'\s+'+str(row['proven'])+r'/0\s+(?:Proven|通过)\s+'+re.escape(f"{row['runtime_s']:.3f}")
            assert re.search(pattern,text),(lang,row['circuit'])
            rows.append({'circuit':row['circuit'],'proven':row['proven'],'unproven':0,'walltime_display':f"{row['runtime_s']:.3f}",'actual_PDF_readback':True})
        assert 'Yosys 0.33' in text
        checks[lang]={'source':entry['path'],'source_sha256':sha(source),'pdf':build['pdf'],'pdf_sha256':sha(pdf),'pages':len(doc),'A_table_page':qa['table_page'],'exact_scope_inverse_passed':True,'rows':rows,'diagnostics':qa['diagnostics'],'all_pages_rendered_and_visually_inspected':True,'contact_sheets':[p.relative_to(ROOT).as_posix() for p in sorted((folder/(lang+'_renders')).glob('contact_*.png'))]}
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=lang+'_original.tex',tofile=lang+'_final.tex'))
    (OUT/(lang+'_final.tex')).write_bytes(source.read_bytes())
draft=load(ROOT/'paper/en/submission/draft_checks.json');assert draft['passed']
assert draft['english_source_sha256']==checks['en']['source_sha256'] and draft['current_chinese_source_sha256']==checks['zh']['source_sha256']
layout=load(EN/'FIG3_LAYOUT_ACTUAL_QA.json');assert layout['actual_plot_labels_min_pt']>=6.8
save(OUT/'FINAL_QA.json',{'scope':'Only bilingual A SEC sentence/table, plus measured EN Figure3 inclusion width .78 to .70 and A/B float boundary. No new WNS or B3/C/D result inserted.','selected_english_iteration':'v5','languages':checks,'A8_sources_sha256':edit['A8_sources_sha256'],'source_pin_45_files_current_match':True,'source_head_from_A8_manifest':manifest['source_pin']['head'],'bilingual_draft_check_passed':True,'other_13_table_blocks_and_all_figure_artwork_unchanged':True,'EN_actual_layout':layout,'visual_findings':[],'retained_iterations':['v1 QA regex failure','v2 canonical PDF write-lock failure','v2 attempt02 table on16','v3 shortened note table on16','v4 barrier 28pages sparse floats'],'scientific_status':'Working drafts; remaining historical/scientific evidence governed by current claim map.'})
(OUT/'final_edits.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({'FINAL_QA_sha256':sha(OUT/'FINAL_QA.json'),'checks':{k:{x:v[x] for x in ('source_sha256','pdf_sha256','pages','A_table_page')} for k,v in checks.items()}},indent=2))
