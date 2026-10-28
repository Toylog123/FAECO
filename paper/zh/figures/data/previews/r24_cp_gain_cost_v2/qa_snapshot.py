from pathlib import Path
import csv, hashlib, json, subprocess, sys
from decimal import Decimal
import fitz

root = Path(__file__).resolve().parents[1]
out = root/'paper/zh/figures/data/previews/r24_cp_gain_cost_v2'
skill = Path('C:/Users/16225/.codex/skills/nature-figure/scripts')
script = root/'paper/zh/figures/data/scripts/review_r24_cp_gain_cost.py'
pdf = out/'r24_cp_gain_cost.pdf'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name, x): (out/name).write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
def csvread(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
for name, tool, target in [('SOURCE_PREFLIGHT.json', 'validate_figure.py', script),
                           ('PDF_GLYPH_AUDIT.json', 'audit_pdf_text.py', pdf)]:
    result = subprocess.run([sys.executable, str(skill/tool), str(target), '--json'], capture_output=True, text=True, timeout=45)
    (out/name).write_text(result.stdout, encoding='utf-8')
    assert result.returncode == 0, result.stderr
result = subprocess.run([sys.executable, str(skill/'audit_figure_collisions.py'), str(pdf),
    '--json-out', str(out/'COLLISION_AUDIT.json'), '--overlay-pdf', str(out/'COLLISION_AUDIT.pdf')],
    capture_output=True, text=True, timeout=45)
assert result.returncode == 0, result.stdout+result.stderr
rows = csvread(out/'r24_cp_gain_cost_source.csv')
audit_path = root/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json'
audit = json.loads(audit_path.read_text())
by = {(r['circuit'], r['arm']): r for r in rows}
old = csvread(root/'paper/zh/figures/data/previews/r22_matrix_gain_cost_v3/r22_matrix_gain_cost_raw.csv')
for r in audit['jobs']:
    d = by[r['circuit'], r['arm']]
    assert Decimal(d['wns_gain_ns']) == Decimal(str(r['final_wns']))-Decimal(str(r['baseline_wns']))
    for dest, src in [('candidate_ideal_sta','candidate_ideal_sta_launches'),
                      ('candidate_evaluation_records','candidate_evaluation_records'),
                      ('baseline_sta','baseline_sta_process_attempts'), ('total_sta','total_sta_process_attempts'),
                      ('retained_commits','retained_commits'), ('sec_proven_points','sec_proven_points'),
                      ('sec_unproven_points','sec_unproven_points')]:
        assert int(d[dest]) == r[src]
    assert sha(root/d['completion_path']) == d['completion_sha256'] == r['completion_sha256']
for r in old:
    d = by[r['circuit'], r['arm']]
    for field in ['wns_gain_ps','candidate_ideal_sta','baseline_sta','total_sta','retained_commits']:
        assert Decimal(d[field]) == Decimal(r[field])
    assert d['completion_sha256'] == r['completion_sha256']
alignment = json.loads((out/'PANEL_ALIGNMENT.json').read_text())
assert alignment['verdict'] == 'PASS'
assert alignment['summary']['fail'] == alignment['summary']['warn'] == 0
guardout = root/'scratch/r24_cp_rejected_guard'
assert not guardout.exists()
rejected = subprocess.run([sys.executable, str(script), '--audit',
    str(root/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_51.json'), '--output-dir', str(guardout),
    '--alignment-auditor', str(skill/'audit_panel_alignment.py')], capture_output=True, text=True, timeout=45)
assert rejected.returncode != 0 and not guardout.exists()
with fitz.open(pdf) as doc:
    page = doc[0]
    assert len(doc) == 1
    spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    assert min(s['size'] for s in spans) >= 7
    text = page.get_text()
    assert '改善' in text and '候选' in text
    fonts = page.get_fonts(full=True)
    physical_mm = [page.rect.width/72*25.4, page.rect.height/72*25.4]
    assert all(doc.extract_font(f[0])[3] for f in fonts)
    for name, x0, x1 in [('a', 0, page.rect.width/2), ('b', page.rect.width/2, page.rect.width)]:
        page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(x0,0,x1,page.rect.height)).save(out/f'QA_panel_{name}.png')
    page.get_pixmap(matrix=fitz.Matrix(2,2)).save(out/'QA_pdf_render.png')
dump('DATA_AND_RENDER_CHECK.json', {'status': 'PASS', 'data_rows': len(rows),
    'audit_rows_checked':72,'previous_accepted_csv_rows_checked':72,
    'incomplete51_rejected_before_output':True, 'guard_rc':rejected.returncode,
    'guard_stderr': rejected.stderr, 'alignment_verdict':alignment['verdict'],
    'pdf_font_min_actual_pt':min(s['size'] for s in spans), 'all_pdf_fonts_embedded':True,
    'pdf_chinese_text_extractable':True, 'pdf_fonts':[f[3] for f in fonts],
    'pdf_size_mm':physical_mm,
    'candidate_sta_total':sum(int(r['candidate_ideal_sta']) for r in rows),
    'records_total':sum(int(r['candidate_evaluation_records']) for r in rows),
    'baseline_sta_separate':sum(int(r['baseline_sta']) for r in rows),
    'visual_review':'pending actual PNG and panel inspection'})
print('PASS all72 audit/previousCSV/currentcompletion binding; font/embedding/alignment/collision; incomplete guard')
