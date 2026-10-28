"""Static/readback/layout evidence; render all pages, no scientific EDA."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,time
import pymupdf
from PIL import Image,ImageDraw

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file());OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BASE=next(p for p in Path(__file__).resolve().parents if (p/'EDIT_RECEIPT.json').is_file())
edits=json.loads((BASE/'EDIT_RECEIPT.json').read_text(encoding='utf-8'))
snapshots=json.loads((BASE/'BEFORE_SNAPSHOT.json').read_text(encoding='utf-8'))
a8=json.loads((ROOT/'project_docs/evidence/r22_a_sec_unified_20261018/RUN_RECEIPT.json').read_text(encoding='utf-8'))
def table(text,label):
    pos=text.index(r'\label{'+label+'}');start=text.rfind(r'\begin{table}',0,pos)
    end=text.index(r'\end{table}',pos)+len(r'\end{table}');return text[start:end]
all_report=[]
for entry in [item for item in edits['edits'] if item['language']=='en']:
    lang=entry['language'];source=ROOT/entry['path'];after=source.read_text(encoding='utf-8')
    old=next(s for s in snapshots if s['path']==entry['path']);before=(BASE/old['backup']).read_text(encoding='utf-8')
    labels=re.findall(r'\\label\{([^}]+)\}',after);assert len(labels)==len(set(labels))
    labels_before=re.findall(r'\\label\{([^}]+)\}',before);assert labels==labels_before
    cite=lambda text:re.findall(r'\\(?:cite|ref|eqref)\{([^}]+)\}',text)
    assert cite(before)==cite(after)
    blocks=re.findall(r'\\begin\{table\}[\s\S]*?\\end\{table\}',before)
    preserved=0
    for block in blocks:
        if r'\label{tab:sec_iscas8}' not in block:
            assert block in after;preserved+=1
    assert preserved==13
    assert re.findall(r'\\includegraphics[^{]*\{([^}]+)\}',before)==re.findall(r'\\includegraphics[^{]*\{([^}]+)\}',after)
    actual_table=table(after,'tab:sec_iscas8')
    actual_rows=re.findall(r'^(s\d+)\s*&\s*(\d+)/(\d+)\s*&\s*(?:通过|Proven)\s*&\s*([\d.]+)',actual_table,re.M)
    assert actual_rows==[(r['circuit'],str(r['proven']),str(r['unproven']),f"{r['runtime_s']:.3f}") for r in a8['rows']]
    assert 'Yosys 0.33' in actual_table
    build=json.loads((OUT/(lang+'_build_receipt.json')).read_text(encoding='utf-8'))
    assert build['passed'] and sha(source)==build['source_sha256']
    pdf=ROOT/build['pdf'];assert sha(pdf)==build['pdf_sha256']
    log=pdf.with_suffix('.log').read_text(encoding='utf-8',errors='replace')
    (OUT/(lang+'_final_compile.log')).write_bytes(pdf.with_suffix('.log').read_bytes())
    diagnostics={'overfull_boxes':len(re.findall(r'Overfull \\[hv]box',log)),
                 'underfull_boxes':len(re.findall(r'Underfull \\[hv]box',log)),
                 'missing_character':bool(re.search('Missing character',log)),
                 'undefined_refs_or_citations':bool(re.search(r'(?:Reference|Citation).*undefined|There were undefined',log)),
                 'rerun_warning':bool(re.search(r'Rerun to get cross-references right|Label\(s\) may have changed',log)),
                 'latex_warnings':re.findall(r'(?:LaTeX|Package [^\n]+) Warning:[^\n]*',log)}
    assert not any(diagnostics[k] for k in ('overfull_boxes','missing_character','undefined_refs_or_citations','rerun_warning'))
    doc=pymupdf.open(pdf);texts=[page.get_text() for page in doc]
    matching=[i for i,text in enumerate(texts) if re.search(r'139\s*/\s*0',text) and re.search(r'146\s*/\s*0',text)]
    assert len(matching)==1,(lang,matching)
    table_page=matching[0]
    rendering=OUT/(lang+'_renders');rendering.mkdir(exist_ok=False)
    command=[shutil.which('pdftoppm'),'-r','100','-png',str(pdf),str(rendering/'page')]
    started=time.monotonic();process=subprocess.run(command,capture_output=True,timeout=150)
    (rendering/'render.stdout.bin').write_bytes(process.stdout);(rendering/'render.stderr.bin').write_bytes(process.stderr)
    assert process.returncode==0
    pages=sorted(rendering.glob('page-*.png'));assert len(pages)==len(doc)
    # Four-page sheets allow each individual page's layout to be inspected.
    for offset in range(0,len(pages),4):
        selected=pages[offset:offset+4];sheet=Image.new('RGB',(1680,2420),'#E9ECEF');draw=ImageDraw.Draw(sheet)
        for index,path in enumerate(selected):
            image=Image.open(path).convert('RGB');image.thumbnail((820,1175))
            x=(index%2)*840+(840-image.width)//2;y=(index//2)*1210+25
            sheet.paste(image,(x,y));draw.text(((index%2)*840+8,(index//2)*1210+6),f'{lang} page {offset+index+1}',fill='black')
        sheet.save(rendering/f'contact_{offset//4+1:02d}.png')
    page=doc[table_page];page.get_pixmap(dpi=180).save(rendering/'A_SEC_full_page_180dpi.png')
    # Table may occupy one Chinese column or the English text width.
    wordrects=[]
    for needle in ('139/0','146/0','0.281','0.407'):
        wordrects.extend(page.search_for(needle))
    x0=min(r.x0 for r in wordrects)-90;x1=max(r.x1 for r in wordrects)+24
    y0=min(r.y0 for r in wordrects)-70;y1=max(r.y1 for r in wordrects)+140
    clip=pymupdf.Rect(max(0,x0),max(0,y0),min(page.rect.width,x1),min(page.rect.height,y1))
    page.get_pixmap(dpi=250,clip=clip).save(rendering/'A_SEC_table_detail_250dpi.png')
    (rendering/'pdf_text_all.txt').write_text('\n\f\n'.join(texts),encoding='utf-8')
    (rendering/'A_SEC_page_text.txt').write_text(texts[table_page],encoding='utf-8')
    report={'language':lang,'source_sha256':sha(source),'pdf_sha256':sha(pdf),'pages':len(doc),
            'render_command':command,'render_exitcode':process.returncode,'render_runtime_s':time.monotonic()-started,
            'table_page':table_page+1,'table_rows_match_accepted_A8':True,'other_13_table_blocks_byte_text_preserved':True,
            'source_labels_cites_refs_unchanged':True,'seven_graphics_references_unchanged':True,'diagnostics':diagnostics,
            'visual_review':'pending','page_renders_sha256':{p.name:sha(p) for p in pages}}
    with (OUT/(lang+'_STATIC_RENDER_QA.json')).open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    all_report.append({k:v for k,v in report.items() if k!='page_renders_sha256'})
print(json.dumps(all_report,ensure_ascii=False,indent=2))
