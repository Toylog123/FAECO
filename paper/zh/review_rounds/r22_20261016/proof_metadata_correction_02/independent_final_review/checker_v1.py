"""Independent read-only A8 metadata manuscript/PDF review; no compilation/EDA/Git.

Run only after author final receipt and synchronization. --output is exclusive.
The checker renders PDFs for visual review; its result is pending human/model
visual inspection until a separate visual review receipt has been added.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,difflib,hashlib,json,math,re,sys,time
import pymupdf
from PIL import Image,ImageDraw

BASE=Path('paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02')
EDIT=BASE/'actual_correction_v1'
ENFINAL=EDIT/'en_float_refinement_v5'
A8=Path('project_docs/evidence/r22_a_sec_unified_20261018')
ZH=Path('paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex')
EN=Path('paper/en/manuscript/FAECO.tex')
READ={}
def sha(data):return hashlib.sha256(data).hexdigest()
def raw(path):
    p=Path(path);data=p.read_bytes();name=str(p.resolve());entry={'sha256':sha(data),'bytes':len(data)}
    if name in READ:assert READ[name]==entry,('source drift during read',name)
    READ[name]=entry;return data
def text(path):return raw(path).decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')
def load(path):return json.loads(text(path))
def save(path,obj):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def table(source,label='tab:sec_iscas8'):
    pos=source.index(r'\label{'+label+'}');a=source.rfind(r'\begin{table}',0,pos);b=source.index(r'\end{table}',pos)+len(r'\end{table}')
    return source[a:b]
def head():
    value=text('.git/HEAD').strip()
    if not value.startswith('ref: '):return value
    ref=value[5:];p=Path('.git')/ref
    if p.exists():return text(p).strip()
    return next(line.split()[0] for line in text('.git/packed-refs').splitlines() if line.endswith(' '+ref))
def resolve_graphics(source,path):
    sourcepaths=[]
    for line in source.splitlines():
        if r'\graphicspath' in line:sourcepaths.extend(re.findall(r'\{([^{}]+)\}',line))
    references=re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',source)
    assert len(references)==7
    resolved=[]
    for reference in references:
        possibilities=[path.parent/reference]+[path.parent/p/reference for p in sourcepaths]
        available=[p.resolve() for p in possibilities if p.is_file()]
        assert len(set(available))==1,(reference,available)
        resolved.append(available[0])
    return resolved
def vector_records(obj):
    """Accept explicit root file→SHA map or records with path and sha256."""
    result={}
    def visit(value):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:result[str(Path(value['path']).resolve())]=value['sha256']
            if 'path' in value and 'fixed_head_blob_sha256' in value:
                assert value['exact_bytes_equal'] and value['current_sha256']==value['fixed_head_blob_sha256']
                result[str(Path(value['path']).resolve())]=value['fixed_head_blob_sha256']
            for k,v in value.items():
                if isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) and ('.pdf' in k or '.svg' in k):result[str(Path(k).resolve())]=v
                elif isinstance(v,dict) and 'sha256' in v and ('.pdf' in k or '.svg' in k):result[str(Path(k).resolve())]=v['sha256']
                visit(v)
        elif isinstance(value,list):
            for v in value:visit(v)
    visit(obj);return result
def compile_check(lang,build_dir,source,pdf):
    receipt=load(build_dir/f'{lang}_build_receipt.json')
    assert receipt['passed'] and receipt['source_stable'] and receipt['source_sha256']==sha(raw(source))
    assert Path(receipt['pdf']).resolve()==pdf.resolve() and receipt['pdf_sha256']==sha(raw(pdf))
    assert [p['pass'] for p in receipt['passes']]==[1,2]
    pass_logs=[]
    for p in receipt['passes']:
        assert p['returncode']==0 and 0<p['runtime_s']<=120
        assert any('lualatex' in token.lower() for token in p['command'])
        stdout=raw(build_dir/f'{lang}_build_logs'/f"pass{p['pass']}.stdout.bin")
        stderr=raw(build_dir/f'{lang}_build_logs'/f"pass{p['pass']}.stderr.bin")
        decoded=stdout.decode('utf-8',errors='replace')
        assert 'Output written on' in decoded and 'Fatal error' not in decoded
        pass_logs.append({'pass':p['pass'],'runtime_s':p['runtime_s'],'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)})
    logfile=build_dir/f'{lang}_final_compile.log';log=text(logfile)
    assert raw(logfile)==raw(pdf.with_suffix('.log'))
    diagnostics={name:bool(re.search(pattern,log,re.I)) for name,pattern in {
        'overfull':r'Overfull \\[hv]box','missing_character':r'Missing character',
        'undefined_ref_or_cite':r'(?:Reference|Citation).*undefined|There were undefined',
        'rerun':r'Rerun to get cross-references right|Label\(s\) may have changed',
        'fatal_error':r'Fatal error|^! '}.items()}
    assert not any(diagnostics.values()),(lang,diagnostics)
    return {'passes':pass_logs,'diagnostics':diagnostics,'underfull_boxes':len(re.findall(r'Underfull \\[hv]box',log)),
            'warnings':re.findall(r'(?:LaTeX|Package [^\n]+) Warning:[^\n]*',log)}

def main():
    started=time.monotonic();parser=argparse.ArgumentParser(description=__doc__)
    for option in ['output','author-final','vector-baseline']:parser.add_argument('--'+option,required=True)
    args=parser.parse_args();author=load(args.author_final)
    assert author['selected_english_iteration']=='v5'
    frozen=load(EDIT/'FINAL_RECEIPT.json')
    assert sha(raw(EDIT/'FINAL_RECEIPT.json'))=='bc95133872e4365ebf8b6b20e379345f54e74df4ad5e065c816bdd5b36c34c23'
    assert frozen['all_source_and_PDF_work_frozen'] and frozen['all_builds_and_tests_stopped']
    assert frozen['final_QA_sha256']==sha(raw(args.author_final))
    assert frozen['sync_receipt_sha256']==sha(raw(EDIT/'SYNC_RECEIPT.json'))
    assert frozen['post_sync_validation_sha256']==sha(raw(EDIT/'POST_SYNC_VALIDATION.json'))
    assert frozen['artifact_manifest_sha256']==sha(raw(EDIT/'FINAL_FILE_SHA_MANIFEST.json'))
    artifact_manifest=load(EDIT/'FINAL_FILE_SHA_MANIFEST.json');assert len(artifact_manifest)==frozen['artifact_files_count']==397
    for index,(name,identity) in enumerate(artifact_manifest.items(),1):
        data=raw(EDIT/name);assert len(data)==identity['bytes'] and sha(data)==identity['sha256'],name
        if index%100==0:print('Bound author artifacts',index,'/397',flush=True)
    for name,digest in frozen['final_paths_sha256'].items():assert sha(raw(name))==digest
    sync=load(EDIT/'SYNC_RECEIPT.json')
    assert sync['all_three_PDF_copies_synchronized']
    assert sync['FINAL_QA_sha256']==sha(raw(args.author_final))
    assert author['prior_QA_sha256']==sha(raw(EDIT/'FINAL_QA.json'))
    for row in sync['copies']:
        assert row['synchronized'] and row['actual_sha256']==row['expected_sha256']
        assert sha(raw(row['source']))==sha(raw(row['target']))==row['actual_sha256']
    for row in sync['english_build_ancillary']:assert row['synchronized'] and sha(raw(row['path']))==row['sha256']
    for name,digest in sync['metadata'].items():assert sha(raw(name))==digest
    out=Path(args.output);out.mkdir(exist_ok=False)
    snapshots=load(EDIT/'BEFORE_SNAPSHOT.json')
    for entry in snapshots:assert sha(raw(EDIT/entry['backup']))==entry['sha256'],entry['backup']
    snapshot_by_path={entry['path']:entry for entry in snapshots}
    acceptance=load(A8/'ROOT_ACCEPTANCE.json');batch=load(A8/'RUN_RECEIPT.json')
    assert acceptance['accepted'] and sha(raw(A8/'RUN_RECEIPT.json'))==acceptance['batch_receipt_sha256']
    assert sha(raw(A8/'independent_review/FINAL_RECEIPT.json'))==acceptance['independent_final_sha256']
    pin=load(A8/'manifest.json')['source_pin'];assert head()==pin['head'] and len(pin['files'])==45
    for name,digest in pin['files'].items():assert sha(raw(name))==digest,name
    rows=batch['rows'];assert len(rows)==8
    for row,accepted in zip(rows,acceptance['rows']):
        for name in ['circuit','proven','unproven','runtime_s']:assert row[name]==accepted[name]
        folder=A8/'proofs'/row['circuit'];completion=load(folder/'completion.json');assert completion==row
        for name,digest in row['artifact_sha256'].items():assert sha(raw(folder/name))==digest
        result=load(folder/'result.json');log=text(folder/'sec.log')
        found=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)
        assert found==[(str(row['proven']),'0')] and row['proven']>0
        assert result['runtime_s']==row['runtime_s'] and result['status']=='pass' and result['returncode']==0
    sentences=load(BASE/'manuscript_draft_pending_A8/SENTENCE_REPLACEMENTS.json')
    vector_document=load(args.vector_baseline)
    assert sha(raw(args.vector_baseline))=='c4ff6ad9429a692e9a12937f869de6d72fd3987df7093ae4534c9d1838f3bf8b'
    raw(Path(args.vector_baseline).parent/'pin_manuscript_vectors_head_20261018.py')
    assert vector_document['head']==pin['head'] and vector_document['all_equal'] and len(vector_document['rows'])==14
    vector_baseline=vector_records(vector_document);assert len(vector_baseline)==14,'Missing fixed HEAD vector identities'
    reports={};vectors={};pdfs={}
    for lang,source,build_dir,snapshot_source in [('zh',ZH,EDIT,EDIT/'zh_after.tex'),('en',EN,ENFINAL,ENFINAL/'en_after.tex')]:
        current=text(source);before=text(EDIT/snapshot_by_path[source.as_posix()]['backup'])
        assert raw(source)==raw(snapshot_source)
        old_sentence=sentences[lang]['before'];new_sentence=sentences[lang]['after']
        assert before.count(old_sentence)==current.count(new_sentence)==1
        old_table=table(before);new_table=table(current)
        assert 'Yosys 0.33' in new_table and r'equiv\_status -assert' in new_table and r'equiv\_induct -seq 10' in new_table
        extracted=re.findall(r'^(s\d+)\s*&\s*(\d+)/(\d+)\s*&\s*(?:通过|Proven)\s*&\s*([\d.]+)',new_table,re.M)
        expected=[(r['circuit'],str(r['proven']),'0',f"{r['runtime_s']:.3f}")for r in rows]
        assert extracted==expected,(lang,extracted)
        reconstructed=current.replace(new_table,old_table).replace(new_sentence,old_sentence)
        if lang=='en':
            old=r'\includegraphics[width=0.78\linewidth]{fig3_single_round_r21.pdf}'
            new=r'\includegraphics[width=0.70\linewidth]{fig3_single_round_r21.pdf}'
            assert before.count(old)==current.count(new)==1
            reconstructed=reconstructed.replace(new,old)
            position=r'\FloatBarrier'+'\n'+r'\subsection{Cross-dataset evaluation}'
            assert current.count(position)==1 and before.count(position)==0
            reconstructed=reconstructed.replace(position,r'\subsection{Cross-dataset evaluation}')
            assert new_table.startswith(r'\begin{table}[!htbp]')
        assert reconstructed==before,('Change outside authorized A metadata/local layout',lang)
        # Also preserve raw source newline convention; the logical inverse above does not conceal full-source line-ending changes.
        assert raw(source).count(b'\r\n')==raw(EDIT/snapshot_by_path[source.as_posix()]['backup']).count(b'\r\n') or not raw(source).count(b'\r\n')
        other_tables=[b for b in re.findall(r'\\begin\{table\}[\s\S]*?\\end\{table\}',before)if r'\label{tab:sec_iscas8}'not in b]
        assert len(other_tables)==13 and all(b in current for b in other_tables)
        for pattern in [r'\\label\{([^}]+)\}',r'\\(?:cite|ref|eqref)\{([^}]+)\}',r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}']:
            assert re.findall(pattern,before)==re.findall(pattern,current)
        refs=lambda s:s[s.index(r'\begin{thebibliography}'):] if r'\begin{thebibliography}'in s else ''
        assert refs(before)==refs(current)
        graphics=resolve_graphics(current,source)
        for figure in graphics:
            digest=sha(raw(figure));assert vector_baseline[str(figure.resolve())]==digest,figure
            vectors[str(figure)]={'sha256':digest,'bytes':len(raw(figure))}
        pdf=Path('paper/zh/build')/ZH.with_suffix('.pdf').name if lang=='zh' else ENFINAL/'build/FAECO.pdf'
        pdfs[lang]=pdf
        diagnostics=compile_check(lang,build_dir,source,pdf)
        doc=pymupdf.open(stream=raw(pdf),filetype='pdf');assert len(doc)==(12 if lang=='zh' else 26)
        page_text=[p.get_text() for p in doc]
        matches=[i for i,t in enumerate(page_text)if '139/0'in t and '146/0'in t];assert len(matches)==1
        table_index=matches[0];table_text=page_text[table_index]
        for row in rows:
            assert row['circuit']in table_text and f"{row['proven']}/0"in table_text and f"{row['runtime_s']:.3f}"in table_text
        fonts={}
        for page in doc:
            for font in page.get_fonts(full=True):
                xref=font[0]
                if xref in fonts:continue
                name,ext,kind,data=doc.extract_font(xref);assert data,(lang,'font not embedded',name)
                fonts[xref]={'name':name,'type':kind,'extension':ext,'bytes':len(data),'sha256':sha(data)}
        figure3=None
        if lang=='en':
            candidates=[i for i,t in enumerate(page_text)if 'ISCAS89: paired ideal-net WNS'in t];assert len(candidates)==1
            fp=candidates[0];spans=[s for block in doc[fp].get_text('dict')['blocks']if block['type']==0 for line in block['lines']for s in line['spans']]
            graph=[s for s in spans if s['font']in ('ArialMT','Arial-BoldMT')and s['text'].strip()]
            assert {'WNS (ns)','Baseline','FAECO','s27','s953'}<=set(s['text']for s in graph)
            minimum=min(s['size']for s in graph);assert minimum>=6.8
            cross=[i for i,t in enumerate(page_text)if '4.3. Cross-dataset evaluation'in t];assert len(cross)==1 and cross[0]>table_index
            figure3={'page':fp+1,'actual_min_plot_font_pt':minimum,'required_min_pt':6.8,'table_page':table_index+1,'next_experiment_heading_page':cross[0]+1,'span_count':len(graph)}
        render=out/(lang+'_renders');render.mkdir()
        page_files=[]
        for index,page in enumerate(doc):
            file=render/f'page-{index+1:02d}.png';page.get_pixmap(dpi=100).save(file);page_files.append(file)
        for offset in range(0,len(page_files),4):
            sheet=Image.new('RGB',(1680,2420),'#e9ecef');draw=ImageDraw.Draw(sheet)
            for k,file in enumerate(page_files[offset:offset+4]):
                image=Image.open(file).convert('RGB');image.thumbnail((820,1175));x=(k%2)*840+(840-image.width)//2;y=(k//2)*1210+25
                sheet.paste(image,(x,y));draw.text(((k%2)*840+8,(k//2)*1210+6),f'{lang} page {offset+k+1}',fill='black')
            sheet.save(render/f'contact_{offset//4+1:02d}.png')
        doc[table_index].get_pixmap(dpi=250).save(render/'A_SEC_full_page_250dpi.png')
        if figure3:doc[figure3['page']-1].get_pixmap(dpi=250).save(render/'Fig3_and_A_SEC_actual_250dpi.png')
        (render/'pdf_text_all.txt').write_text('\n\f\n'.join(page_text),encoding='utf-8')
        reports[lang]={'source_sha256':sha(raw(source)),'pdf_sha256':sha(raw(pdf)),'pages':len(doc),'A_table_page':table_index+1,
                       'rows_match_actual_A8':True,'only_authorized_logical_edits':True,'other_13_tables_unchanged':True,
                       'labels_cites_refs_bibliography_clock_metadata_unchanged':True,'fonts':fonts,'compile':diagnostics,'Figure3_actual':figure3}
        (out/f'{lang}_independent_minimal.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),current.splitlines(True))),encoding='utf-8')
        print('VERIFIED source/proof/compile/PDF metadata',lang,len(doc),'pages; visual review pending',flush=True)
        assert author['languages'][lang]['source_sha256']==reports[lang]['source_sha256']
        assert author['languages'][lang]['pdf_sha256']==reports[lang]['pdf_sha256']
    zhpdfs=[Path('paper/zh/build')/ZH.with_suffix('.pdf').name,Path('paper/zh')/ZH.with_suffix('.pdf').name,ZH.with_suffix('.pdf')]
    assert len({sha(raw(p))for p in zhpdfs})==1
    assert raw('paper/en/build/FAECO.pdf')==raw(pdfs['en'])
    bindings=load('paper/en/submission/source_binding.json');metrics=load('paper/en/submission/build_metrics.json');draft=load('paper/en/submission/draft_checks.json')
    assert bindings['english_manuscript_sha256']==metrics['english_source_sha256']==draft['english_source_sha256']==sha(raw(EN))
    assert bindings['translation_source_current_sha256']==draft['current_chinese_source_sha256']==sha(raw(ZH))
    assert metrics['pdf_sha256']==sha(raw('paper/en/build/FAECO.pdf')) and metrics['pages']==26 and metrics['latest_compile_exit_code']==0
    oldbindings=load(EDIT/'before/06_source_binding.json')
    assert bindings['r22_clock_period_metadata_correction']==oldbindings['r22_clock_period_metadata_correction']
    assert draft['passed'] and all(draft['numeric_table_rows_match'].values()) and all(draft['numeric_figure_csv_rows_match'].values())
    assert draft['reference_keys']==load(EDIT/'before/09_draft_checks.json')['reference_keys']
    # Author's frozen final receipt must actually bind the accepted current sources and PDFs.
    final_serialized=json.dumps(author,ensure_ascii=False)
    for digest in [sha(raw(ZH)),sha(raw(EN)),sha(raw(zhpdfs[0])),sha(raw(pdfs['en']))]:assert digest in final_serialized
    assert head()==pin['head']
    before=dict(READ);after={}
    for name,value in before.items():
        b=Path(name).read_bytes();after[name]={'sha256':sha(b),'bytes':len(b)};assert after[name]==value,('read-only drift',name)
    save(out/'READ_BEFORE.json',before);save(out/'READ_AFTER.json',after)
    result={'schema':'A8-manuscript-independent-static-and-render-review-v1','client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,'checker_sha256':sha(Path(__file__).read_bytes()),'runtime_s':time.monotonic()-started,'source_HEAD':pin['head'],'current_source_files':45,'all_read_sources_stable':True,'read_source_count':len(before),'reports':reports,'vector_sources':vectors,'zh_three_PDF_copies_equal':True,'en_selected_and_current_PDF_equal':True,'source_binding_and_build_metrics_and_draft_checks_match':True,'new_compilation_EDA_or_Git_commands':False,'visual_review':'pending independent actual image inspection','decision':'Static/proof/source/build/readback bindings verified; visual acceptance pending'}
    save(out/'RESULT.json',result);print('RESULT_SHA256',sha((out/'RESULT.json').read_bytes()),'visual pending',flush=True)

if __name__=='__main__':main()
