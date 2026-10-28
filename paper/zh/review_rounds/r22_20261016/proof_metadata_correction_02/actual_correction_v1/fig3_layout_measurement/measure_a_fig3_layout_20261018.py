"""Read the rendered figure text before choosing a modest inclusion scale."""
from pathlib import Path
import pymupdf,json,hashlib
ROOT=Path.cwd().resolve();BASE=ROOT/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1'
pdf=BASE/'en_float_refinement_v4/build/FAECO.pdf'
out=BASE/'fig3_layout_measurement';out.mkdir(exist_ok=False)
before=hashlib.sha256(pdf.read_bytes()).hexdigest()
with pymupdf.open(pdf) as doc:
    spans=[s for b in doc[14].get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
    graph=[s for s in spans if 170<s['bbox'][0] and s['bbox'][2]<450 and 170<s['bbox'][1] and s['bbox'][3]<415 and s['text'].strip()]
    assert {'Baseline','FAECO','WNS (ns)','s27','s953'}<=set(s['text'] for s in graph)
    minimum=min(s['size'] for s in graph);projected=minimum*.70/.78
    assert minimum>8 and projected>=6.8
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==before
value={'source_pdf':pdf.relative_to(ROOT).as_posix(),'source_pdf_sha256':before,'page_1based':15,
 'current_inclusion_width':'.78 linewidth','proposed_inclusion_width':'.70 linewidth',
 'actual_current_minimum_figure_text_pt':minimum,'projected_minimum_pt':projected,'required_minimum_pt':6.8,
 'scope':'Layout-only inclusion scaling of the unchanged vector Figure3; measured minimum concerns all visible plot labels/ticks/legend in the stated region',
 'observed_figure_text_spans':[{'text':s['text'],'pt':s['size'],'bbox':s['bbox']} for s in graph],
 'source_pdf_unchanged':True,'new_export_actual_font_and_layout_check_still_required':True}
with (out/'MEASUREMENT.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in value.items() if k!='observed_figure_text_spans'}))
