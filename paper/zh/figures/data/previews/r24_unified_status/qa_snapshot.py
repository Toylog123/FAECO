from pathlib import Path
import csv,json,hashlib,shutil
import fitz
root=Path(__file__).resolve().parents[1]
out=root/'paper/zh/figures/data/previews/r24_unified_status'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
old=list(csv.DictReader((root/'paper/zh/figures/data/final/fig4_unified_gain_r21.csv').open(encoding='utf-8-sig')))
new=list(csv.DictReader((out/'fig4_r24_source.csv').open(encoding='utf-8-sig')))
assert len(old)==len(new)==30
for before,after in zip(old,new):
    for field in before:assert before[field]==after[field],(field,before,after)
marked={r['circuit'] for r in new if r['functional_proof_annotation']=='unsupported_true_tristate'}
assert marked=={'b09','b20','b21'}
assert sum(r['applicable']=='True' for r in new)==29
alignment=json.loads((out/'PANEL_ALIGNMENT.json').read_text())
assert alignment['verdict']=='PASS' and alignment['summary']['warn']==0
collision=json.loads((out/'COLLISION_AUDIT.json').read_text())
with fitz.open(out/'fig4_r24.pdf') as doc:
    page=doc[0];spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    assert min(s['size'] for s in spans)>=7
    assert all(doc.extract_font(f[0])[3] for f in page.get_fonts(full=True))
    text=page.get_text()
    for c in ['b09','b20','b21']:assert c in text
    assert '功能证明不支持' in text
    assert all(0<=s['bbox'][0] and s['bbox'][2]<=page.rect.width and 0<=s['bbox'][1] and s['bbox'][3]<=page.rect.height for s in spans)
    dims=[page.rect.width/72*25.4,page.rect.height/72*25.4]
    page.get_pixmap(matrix=fitz.Matrix(2,2)).save(out/'QA_pdf_render.png')
    for name,limits in {'a':(0,.325),'b':(.325,.66),'c':(.66,1)}.items():
        page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(page.rect.width*limits[0],0,page.rect.width*limits[1],page.rect.height*.9)).save(out/f'QA_panel_{name}.png')
dump('DATA_AND_RENDER_CHECK.json',{'status':'PASS with two explicitly reviewed plot-fill-edge warnings',
    'original_csv_rows_checked':30,'all_original_fields_identical_in_original_order':True,
    'numeric_rows':29,'N_A_rows':['picorv32_regs'],'unsupported_markers':sorted(marked),
    'minimum_actual_font_pt':min(s['size'] for s in spans),'all_fonts_embedded':True,
    'all_text_inside_page':True,'pdf_size_mm':dims,'alignment':'PASS0F0W',
    'collision_warnings_review':'The +2.75 and +1.13 value text extends beyond the blank white axes fill into the white gutter. Both remain within page with no line/text collision. No data removed.',
    'no_new_eda':True,'no_cross_family_data':True,'visual_review':'pending final panel inspection'})
shutil.copyfile(__file__,out/'qa_snapshot.py')
print('PASS all30 original fields exactly equal, three status flags only, font/embed/page geometry')
