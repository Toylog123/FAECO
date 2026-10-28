from pathlib import Path
import pymupdf,json,hashlib
r=Path.cwd();o=r/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1/en_float_refinement_v5';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((o/'en_build_receipt.json').read_text());pdf=r/build['pdf'];d=pymupdf.open(pdf);p=d[14];ss=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']];graph=[s for s in ss if s['font'] in ('ArialMT','Arial-BoldMT') and s['text'].strip()]
assert len(graph)==29 and {'Baseline','FAECO','WNS (ns)','s27','s953'}<=set(s['text'] for s in graph)
minimum=min(s['size'] for s in graph);assert minimum>=6.8
rect=pymupdf.Rect(min(s['bbox'][0] for s in graph)-15,min(s['bbox'][1] for s in graph)-12,max(s['bbox'][2] for s in graph)+15,max(s['bbox'][3] for s in graph)+12);p.get_pixmap(dpi=250,clip=rect).save(o/'en_renders/Fig3_detail_250dpi.png');p.get_pixmap(dpi=250,clip=pymupdf.Rect(80,455,540,660)).save(o/'en_renders/A_SEC_table_fullwidth_250dpi.png')
texts=[p.get_text() for p in d];table=[i+1 for i,t in enumerate(texts) if '139/0' in t and '146/0' in t];cross=[i+1 for i,t in enumerate(texts) if '4.3. Cross-dataset evaluation' in t];assert table==[15] and cross==[16]
v={'source_sha256':build['source_sha256'],'pdf_sha256':sha(pdf),'pages':len(d),'figure_page':15,'A_SEC_table_page':15,'cross_dataset_first_heading_page':16,'actual_plot_labels_min_pt':minimum,'required_min_pt':6.8,'graph_text_spans':[{'text':s['text'],'size_pt':s['size'],'bbox':s['bbox']} for s in graph],'graph_fonts_identification':'All 29 embedded ArialMT/Arial-BoldMT spans on page15; body/table use other fonts','plot_and_table_before_next_experiment':True}
with (o/'FIG3_LAYOUT_ACTUAL_QA.json').open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in v.items() if k!='graph_text_spans'}))
