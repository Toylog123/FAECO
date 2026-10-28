"""Post-sync readback and immutable file inventory. No builds, EDA or Git mutations."""
from pathlib import Path
import hashlib,json,subprocess,pymupdf

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
qa=load(OUT/'FINAL_QA_v2.json');sync=load(OUT/'SYNC_RECEIPT.json')
assert sync['all_three_PDF_copies_synchronized']
assert sha(OUT/'FINAL_QA_v2.json')==sync['FINAL_QA_sha256']
for path,digest in sync['metadata'].items():assert sha(ROOT/path)==digest
paths={}
for lang,row in qa['languages'].items():
    for kind in ('source','pdf'):
        path=ROOT/row[kind];assert sha(path)==row[kind+'_sha256'];paths[rel(path)]=sha(path)
    with pymupdf.open(ROOT/row['pdf']) as doc:assert len(doc)==row['pages']
for row in sync['copies']:
    assert sha(ROOT/row['target'])==row['expected_sha256'];paths[row['target']]=row['expected_sha256']
for row in sync['english_build_ancillary']:
    assert row['synchronized'] and sha(ROOT/row['path'])==row['sha256'];paths[row['path']]=row['sha256']
manifest=load(ROOT/'project_docs/evidence/r22_a_sec_unified_20261018/MANIFEST.json')
for path,digest in manifest['source_pin']['files'].items():assert sha(ROOT/path)==digest
vector=ROOT/qa['figure_artwork_binding']['receipt'];assert sha(vector)==qa['figure_artwork_binding']['sha256']
metrics=load(ROOT/'paper/en/submission/build_metrics.json');binding=load(ROOT/'paper/en/submission/source_binding.json');draft=load(ROOT/'paper/en/submission/draft_checks.json')
assert metrics['pdf_sha256']==sha(ROOT/metrics['pdf_path'])==qa['languages']['en']['pdf_sha256']
assert metrics['english_source_sha256']==binding['english_manuscript_sha256']==draft['english_source_sha256']==qa['languages']['en']['source_sha256']
assert metrics['pages']==26 and draft['passed']
assert binding['translation_source_current_sha256']==qa['languages']['zh']['source_sha256']
status=subprocess.run(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,capture_output=True,check=True,timeout=30)
(OUT/'GIT_STATUS_AFTER.stdout.bin').write_bytes(status.stdout);(OUT/'GIT_STATUS_AFTER.stderr.bin').write_bytes(status.stderr)
post={'all_current_source_PDF_and_metadata_bindings_match':True,'ZH_three_PDF_copies_same_SHA':all(d==qa['languages']['zh']['pdf_sha256'] for p,d in paths.items() if p.startswith('paper/zh/') and p.endswith('.pdf') and '/review_rounds/' not in p),'source_pin_45_files_match_A8_f761':True,'no_EDA_by_this_correction':True,'final_paths_sha256':paths,'metadata_sha256':sync['metadata'],'vector_binding_scope':'All14 vector PDFs equal fixed f761 HEAD blobs per root independent receipt, not child before-filesystem capture','git_status_scope':'Read-only shared-workspace snapshot; not all concurrent changes are attributable to this correction.'}
assert post['ZH_three_PDF_copies_same_SHA'];save(OUT/'POST_SYNC_VALIDATION.json',post)
(OUT/'README.md').write_text('''# A SEC metadata correction — selected final build

The selected Chinese source/build is the original correction v1 (12 pages, Table 8 on page 8). The selected English source/build is `en_float_refinement_v5/` (26 pages, Figure 3 and Table 8 on page 15, next experiment on page 16). Both languages contain the eight accepted A8 proof counts and same-batch prover wall times. No WNS, B3/C/D result, algorithm or scientific run was changed here.

`FINAL_QA_v2.json` binds exact source/PDF bytes, actual PDF row readback, two-pass compiler results, all-page rendered visual review and the root's 14-vector comparison against fixed f761 HEAD. The vector comparison is not a before-filesystem snapshot by this child. `SYNC_RECEIPT.json` and `POST_SYNC_VALIDATION.json` bind the synchronized three Chinese PDF locations, English canonical PDF and current English submission metadata.

The final English layout keeps the accepted short proof note and a single A/B FloatBarrier; only the unchanged Figure 3 inclusion width changes from 0.78 to 0.70 linewidth. All 29 actual embedded plot text spans have minimum size 7.34552 pt, above the 6.8 pt requirement. The other 13 table blocks, references and figure artwork are preserved.

History is retained: initial QA regex failure; canonical PDF write-lock failure; v2/v3 table placement on page 16; v4 28-page sparse layout; all source/PDF snapshots, execution scripts and bounded compile/render logs. The selected v5 resolves the observed layout regression. The earlier FINAL_QA remains an original record; v2 adds precise vector provenance.

This closes only the A proof metadata and its layout/synchronization task. Other historical scientific evidence, author declarations and full-paper finalization remain governed by the current claim map and shared project records.
''',encoding='utf-8')
save(OUT/'ARCHIVE_INVOCATION.json',{'command':['C:/Program Files/Git/bin/bash.exe','code/scripts/run_with_timeout.sh','120','.venv/Scripts/python.exe',rel(Path(__file__))],'scope':'Post-sync read-only binding checks, QA packaging, shared Git status only; no Git mutation or EDA.'})
(OUT/'ARCHIVE_VALIDATION.log').write_text('PASS: source/PDF/current metadata bytes and actual page counts\nPASS: all synchronized PDF copies\nPASS: 45 current source files match fixed A8 f761 pin\nPASS: root vector receipt SHA binding\nPASS: bounded read-only shared Git status snapshot\nNo build or scientific EDA started by archive step.\n',encoding='utf-8')
files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ('FINAL_RECEIPT.json','FINAL_FILE_SHA_MANIFEST.json')]
inventory={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
save(OUT/'FINAL_FILE_SHA_MANIFEST.json',inventory)
final={'status':'A SEC metadata/layout/copy synchronization completed; root independent acceptance separate','selected_EN':'en_float_refinement_v5','final_QA_sha256':sha(OUT/'FINAL_QA_v2.json'),'sync_receipt_sha256':sha(OUT/'SYNC_RECEIPT.json'),'post_sync_validation_sha256':sha(OUT/'POST_SYNC_VALIDATION.json'),'artifact_manifest_sha256':sha(OUT/'FINAL_FILE_SHA_MANIFEST.json'),'artifact_files_count':len(inventory),'final_paths_sha256':paths,'scope':qa['scope'],'all_source_and_PDF_work_frozen':True,'all_builds_and_tests_stopped':True,'source_head_changed_by_this_task':False,'shared_records_owner':'records_1018','remaining_scope':'Other scientific/author/submission work remains open in shared project records.'}
save(OUT/'FINAL_RECEIPT.json',final)
print(json.dumps({'final_receipt_sha256':sha(OUT/'FINAL_RECEIPT.json'),'artifact_files_count':len(inventory),'sources':{k:v['source_sha256'] for k,v in qa['languages'].items()},'PDFs':{k:v['pdf_sha256'] for k,v in qa['languages'].items()}},indent=2))
