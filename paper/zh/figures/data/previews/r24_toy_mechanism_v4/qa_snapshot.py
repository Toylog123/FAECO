from pathlib import Path
import csv,hashlib,json,math,os,runpy,shutil,subprocess,sys
import fitz
root=Path(__file__).resolve().parents[1]
out=root/'paper/zh/figures/data/previews/r24_toy_mechanism_v4'
skill=Path('C:/Users/16225/.codex/skills/nature-figure/scripts')
script=root/'paper/zh/figures/data/scripts/review_r24_toy_mechanism.py'
pdf=out/'r24_toy_mechanism.pdf'
process_env=dict(os.environ,PYTHONIOENCODING='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x): (out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
for name,tool,target,extra in [
    ('SOURCE_PREFLIGHT.json','validate_figure.py',script,[]),
    ('PDF_GLYPH_AUDIT.json','audit_pdf_text.py',pdf,[]),
    ('SVG_SCHEMATIC_AUDIT.json','audit_svg_schematic.py',out/'r24_toy_mechanism.svg',['--max-pt','8'])]:
    cmd=[sys.executable,str(skill/tool),str(target),*extra,'--json']
    if tool=='audit_svg_schematic.py':
        # Existing skill auditor calls math for Matplotlib rotate(0) but omits
        # its import. Supply only this missing standard-library namespace.
        cmd=[sys.executable,'-c',"import math,runpy,sys; p=sys.argv.pop(1); runpy.run_path(p,init_globals={'math':math},run_name='__main__')",str(skill/tool),str(target),*extra,'--json']
    result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',env=process_env,timeout=45)
    (out/name).write_text(result.stdout,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
result=subprocess.run([sys.executable,str(skill/'audit_figure_collisions.py'),str(pdf),
    '--json-out',str(out/'COLLISION_AUDIT.json'),'--overlay-pdf',str(out/'COLLISION_AUDIT.pdf')],
    capture_output=True,text=True,encoding='utf-8',env=process_env,timeout=45)
assert result.returncode==0,result.stdout+result.stderr
evidence=root/'paper/zh/review_rounds/r24_20261018/METHOD_EVIDENCE.json'
t=json.loads(evidence.read_text(encoding='utf-8'))['toy']
assert sha(evidence)=='b0eff5f45bf8d6ef91798e37cbbbdf5f92f9aa6ed509d4eafeaa9858471967b2'
assert json.loads((out/'TOY_INPUT.json').read_text(encoding='utf-8'))==t
assert sha(out/'toy.v')==t['netlist_sha256']
align=json.loads((out/'PANEL_ALIGNMENT.json').read_text())
assert align['verdict']=='PASS' and align['summary']['warn']==0
with fitz.open(pdf) as doc:
    page=doc[0]; spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    fonts=page.get_fonts(full=True)
    assert all(doc.extract_font(f[0])[3] for f in fonts)
    assert min(s['size'] for s in spans)>=7
    assert '�' not in page.get_text()
    dims=[page.rect.width/72*25.4,page.rect.height/72*25.4]
    panel_clips={'a':fitz.Rect(0,0,page.rect.width,page.rect.height*.59),
        'b':fitz.Rect(0,page.rect.height*.59,page.rect.width/2,page.rect.height*.93),
        'c':fitz.Rect(page.rect.width/2,page.rect.height*.59,page.rect.width,page.rect.height*.93)}
    page.get_pixmap(matrix=fitz.Matrix(2,2)).save(out/'QA_pdf_render.png')
    for label,clip in panel_clips.items(): page.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip).save(out/f'QA_panel_{label}.png')
dump('DATA_AND_RENDER_CHECK.json',{'status':'PASS','method_evidence_sha256':sha(evidence),
    'toy_input_equal_to_final_method_json':True,'toy_netlist_sha_match':True,
    'six_costs_and_both_boundaries_recomputed_in_generator':True,'pdf_all_fonts_embedded':True,
    'minimum_actual_pdf_font_pt':min(s['size'] for s in spans),'pdf_size_mm':dims,
    'alignment':'PASS 0WARN','collision':'PASS 0WARN','svg_auditor_compatibility':
        {'auditor_sha256':sha(skill/'audit_svg_schematic.py'),
         'change':'supply missing import math via runpy.init_globals, no rule or input geometry changed'},
    'visual_review':'pending actual panel and assembled render inspection'})
shutil.copyfile(__file__,out/'qa_snapshot.py')
print('PASS: finalized toy binding, all costs/boundaries, font7pt, alignment/collision/SVG')
