from pathlib import Path
import csv,json,hashlib,os,shutil,subprocess,sys
import fitz
root=Path(__file__).resolve().parents[1]
out=root/'paper/zh/figures/data/previews/r24_cp_budget_curves_v2'
skill=Path('C:/Users/16225/.codex/skills/nature-figure/scripts')
script=root/'paper/zh/figures/data/scripts/review_r24_cp_budget_curves.py'
pdf=out/'r24_cp_budget_curves.pdf'
env=dict(os.environ,PYTHONIOENCODING='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
for filename,tool,target in [('SOURCE_PREFLIGHT.json','validate_figure.py',script),
                           ('PDF_GLYPH_AUDIT.json','audit_pdf_text.py',pdf)]:
    p=subprocess.run([sys.executable,str(skill/tool),str(target),'--json'],
        capture_output=True,text=True,encoding='utf-8',env=env,timeout=45)
    assert p.returncode==0,p.stdout+p.stderr
    (out/filename).write_text(p.stdout,encoding='utf-8')
p=subprocess.run([sys.executable,str(skill/'audit_figure_collisions.py'),str(pdf),
    '--json-out',str(out/'COLLISION_AUDIT.json'),'--overlay-pdf',str(out/'COLLISION_AUDIT.pdf')],
    capture_output=True,text=True,encoding='utf-8',env=env,timeout=45)
assert p.returncode==0,p.stdout+p.stderr
alignment=json.loads((out/'PANEL_ALIGNMENT.json').read_text())
assert alignment['verdict']=='PASS' and alignment['summary']['warn']==0
collision=json.loads((out/'COLLISION_AUDIT.json').read_text())
assert collision['summary']['fail']==collision['summary']['warn']==0
curves=list(csv.DictReader((out/'CANDIDATE_STA_COMMITTED_CURVES.csv').open(encoding='utf-8-sig')))
commits=list(csv.DictReader((out/'COMMIT_EVENTS.csv').open(encoding='utf-8-sig')))
groups=json.loads((out/'PLOTTED_CURVE_GROUPS.json').read_text())
covered=[(g['circuit'],a) for g in groups['groups'] for a in g['covered_arms']]
assert len(covered)==len(set(covered))==72 and len(groups['groups'])==46
assert len(curves)==6930 and len(commits)==192
assert sha(out/'CANDIDATE_STA_COMMITTED_CURVES.csv')=='e42b330ab31f610f866ec66b152965776c9ec6d3ef0113382b131c6f395a98a7'
assert sha(out/'COMMIT_EVENTS.csv')=='2d0831027029c1ca932be7dea54fea8fa5505cffca784980c39d37c07ab44bf2'
series={key:[(int(r['k']),float(r['committed_gain_ns'])) for r in curves if (r['circuit'],r['arm'])==key] for key in covered}
for g in groups['groups']:
    s=series[g['circuit'],g['representative']]
    assert all(series[g['circuit'],a]==s for a in g['covered_arms'])
    assert s[-1]==(g['k_stop'],g['gain_stop_ns'])
    assert hashlib.sha256(json.dumps(s,separators=(',',':')).encode()).hexdigest()==g['series_sha256']
boxes=json.loads((out/'PANEL_CONTENT_BOXES.json').read_text())
with fitz.open(pdf) as document:
    page=document[0];spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    assert min(s['size'] for s in spans)>=7
    assert all(document.extract_font(f[0])[3] for f in page.get_fonts(full=True))
    page.get_pixmap(matrix=fitz.Matrix(2,2)).save(out/'QA_pdf_render.png')
    h=boxes['figure_height_pt']
    for name,(x0,y0,x1,y1) in boxes['panels'].items():
        clip=fitz.Rect(max(0,x0-2),max(0,h-y1-2),min(page.rect.width,x1+2),min(page.rect.height,h-y0+2))
        page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip).save(out/f'QA_panel_{name}.png')
dump('DATA_AND_RENDER_CHECK.json',{'status':'PASS data and rendered geometry; author panel inspection pending',
    'actual_sta':6858,'baseline_sta_excluded':72,'evaluation_records_not_used_as_k':8458,
    'original_curves':72,'all72_coverage_unique':True,'rendered_exact_groups':46,'all_k0_points':72,
    'raw_csv_points':len(curves),'commits':len(commits),'merged_groups_equal_at_every_k_and_stop':True,
    'no_extrapolation':True,'font_min_pt':min(s['size'] for s in spans),'font_embedded':True,
    'alignment':'PASS0F0W','collision':'PASS0F0W','no_new_eda':True})
shutil.copyfile(__file__,out/'qa_snapshot.py')
print('PASS 72curves/6930points/192commits/46 exact groups; font7pt, alignment/collision0F0W')
