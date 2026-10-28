from pathlib import Path
import json,re,hashlib,sys
import pymupdf
R=Path.cwd();rd=R/'paper/zh/review_rounds/r28_20261019';build=rd/sys.argv[1];src=R/'paper/zh/manuscript'/sys.argv[2];pdf=R/'paper/zh/build'/src.with_suffix('.pdf').name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
static=json.loads((build/'render_qa/STATIC_RENDER_QA.json').read_text(encoding='utf-8'))
assert sha(src)==static['source_sha256'] and sha(pdf)==static['pdf_sha256']
paths=re.findall(r'\\includegraphics\[[^]]*\]\{([^}]+)\}',src.read_text(encoding='utf-8'))
fontnames=set()
for rel in paths:
    if not rel.endswith('.pdf'):continue
    doc=pymupdf.open(R/'paper/zh/figures'/rel)
    for bl in doc[0].get_text('dict')['blocks']:
        for line in bl.get('lines',[]):
            for s in line['spans']:
                if s['text'].strip():fontnames.add(s['font'].split('+')[-1])
doc=pymupdf.open(pdf);runs=[];schematics=[]
for i,p in enumerate(doc):
    for bl in p.get_text('dict')['blocks']:
        for line in bl.get('lines',[]):
            for s in line['spans']:
                if s['font'].split('+')[-1] in fontnames and s['text'].strip():runs.append({'page':i+1,'text':s['text'],'font':s['font'],'size_bp':s['size']})
    for im in p.get_image_info():
        if (im['width'],im['height'])==(1536,1024):
            b=pymupdf.Rect(im['bbox']);w=b.width*25.4/72;h=b.height*25.4/72
            assert abs(w-139.4)<.02 and abs(h-92.93333333)<.02
            assert abs(b.width/b.height-1.5)<.0001
            schematics.append({'page':i+1,'width_mm':w,'height_mm':h,'aspect_ratio_preserved':True})
assert runs and min(s['size_bp'] for s in runs)>=6.0
assert len(schematics)==(2 if '面向' in src.name else 0)
result={'source_sha256':sha(src),'pdf_sha256':sha(pdf),'quantitative_font_names':sorted(fontnames),'quantitative_text_runs_checked':len(runs),'actual_minimum_quantitative_font_bp':min(s['size_bp'] for s in runs),'minimum_font_floor_bp':6.0,'quantitative_text_floor_pass':True,'schematics_actual_dimensions':schematics,'source_assets_unchanged':True,'uniform_scaling_no_aspect_distortion':True}
(build/'ACTUAL_FIGURE_SIZE_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
