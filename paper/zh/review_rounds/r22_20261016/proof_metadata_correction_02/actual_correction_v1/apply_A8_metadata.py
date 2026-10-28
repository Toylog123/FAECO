"""Authorized local A SEC metadata-only correction, bound to accepted A8."""
from pathlib import Path
import csv, difflib, hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parents[6]
OUT=Path(__file__).resolve().parent
BEFORE=OUT/'before';BEFORE.mkdir(exist_ok=False)
A8=ROOT/'project_docs/evidence/r22_a_sec_unified_20261018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
accept=json.loads((A8/'ROOT_ACCEPTANCE.json').read_text(encoding='utf-8'))
receipt=json.loads((A8/'RUN_RECEIPT.json').read_text(encoding='utf-8'))
assert accept['accepted'] and sha(A8/'RUN_RECEIPT.json')==accept['batch_receipt_sha256']
assert sha(A8/'independent_review/FINAL_RECEIPT.json')==accept['independent_final_sha256']
rows=receipt['rows'];assert len(rows)==8
for row, accepted in zip(rows,accept['rows']):
    assert all(row[k]==accepted[k] for k in ('circuit','proven','unproven','runtime_s'))
    assert row['proven']>0 and row['unproven']==0 and row['returncode']==0 and row['status']=='pass'
    folder=A8/'proofs'/row['circuit']
    for name,value in row['artifact_sha256'].items():assert sha(folder/name)==value,(row['circuit'],name)
    log=(folder/'sec.log').read_text(encoding='utf-8')
    counts=re.findall(r'Of those cells\s+(\d+) are proven and\s+(\d+) are unproven',log)
    assert tuple(map(int,counts[-1]))==(row['proven'],0)
    assert 'Yosys 0.33' in log
assert next(r for r in rows if r['circuit']=='s820')['proven']==139
targets={'zh':ROOT/'paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex',
         'en':ROOT/'paper/en/manuscript/FAECO.tex'}
snapshot_paths=list(targets.values())+[
    ROOT/'paper/zh/build'/targets['zh'].with_suffix('.pdf').name,
    ROOT/'paper/en/build/FAECO.pdf',
    ROOT/'paper/zh'/targets['zh'].with_suffix('.pdf').name,
    targets['zh'].with_suffix('.pdf')]
snapshot_paths += [ROOT/'paper/en/submission'/name for name in
                   ('source_binding.json','build_metrics.json','BUILD_DIAGNOSTICS.md','draft_checks.json')]
snapshots=[]
for index,path in enumerate(snapshot_paths):
    assert path.is_file(),path
    backup=BEFORE/f'{index:02d}_{path.name}'
    backup.write_bytes(path.read_bytes())
    snapshots.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'backup':backup.relative_to(OUT).as_posix()})
status=subprocess.run(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,capture_output=True,check=True)
(OUT/'GIT_STATUS_BEFORE.stdout.bin').write_bytes(status.stdout)
(OUT/'GIT_STATUS_BEFORE.stderr.bin').write_bytes(status.stderr)
with (OUT/'BEFORE_SNAPSHOT.json').open('x',encoding='utf-8') as f:json.dump(snapshots,f,ensure_ascii=False,indent=2);f.write('\n')
binding={'RUN_RECEIPT.json':sha(A8/'RUN_RECEIPT.json'),'ROOT_ACCEPTANCE.json':sha(A8/'ROOT_ACCEPTANCE.json'),
         'independent_review/FINAL_RECEIPT.json':sha(A8/'independent_review/FINAL_RECEIPT.json')}
draft=OUT.parent/'manuscript_draft_pending_A8'
sentences=json.loads((draft/'SENTENCE_REPLACEMENTS.json').read_text(encoding='utf-8'))
edits=[];diffs=[]
for lang,path in targets.items():
    original=path.read_bytes().decode('utf-8')
    newline='\r\n' if '\r\n' in original else '\n'
    old_sentence=sentences[lang]['before'];new_sentence=sentences[lang]['after']
    assert original.count(old_sentence)==1
    table=(draft/f'{lang}_SEC_table.tex.in').read_text(encoding='utf-8')
    for row in rows:
        key=row['circuit'].upper()
        for name,value in [('PROVEN',str(row['proven'])),('UNPROVEN',str(row['unproven'])),('WALLTIME_3DP',f"{row['runtime_s']:.3f}")]:
            token=f'@{key}_{name}@';assert table.count(token)==1;table=table.replace(token,value)
    assert '@' not in table
    if lang=='zh':
        table=table.replace('八对网表采用同一验证批次和SKY130行为单元模型，','八对网表在同一验证批次中使用Yosys 0.33和SKY130行为单元模型，')
    else:
        table=table.replace('All eight pairs are checked in one verification batch under SKY130 behavioral cell models using',
                            'All eight pairs are checked in one verification batch with Yosys 0.33 under SKY130 behavioral cell models using')
    table=table.rstrip('\n').replace('\n',newline)
    pos=original.index(r'\label{tab:sec_iscas8}')
    start=original.rfind(r'\begin{table}',0,pos)
    end=original.index(r'\end{table}',pos)+len(r'\end{table}')
    old_table=original[start:end]
    after=original[:start]+table+original[end:]
    after=after.replace(old_sentence,new_sentence)
    # A strict inverse establishes that no other source bytes changed.
    assert after.replace(table,old_table).replace(new_sentence,old_sentence)==original
    before_counts={x:original.count(x) for x in (r'\begin{table}',r'\begin{figure}',r'\includegraphics')}
    after_counts={x:after.count(x) for x in before_counts};assert before_counts==after_counts
    path.write_bytes(after.encode('utf-8'))
    (OUT/f'{lang}_after.tex').write_bytes(path.read_bytes())
    (OUT/f'{lang}_applied_table.tex').write_text(table,encoding='utf-8')
    edits.append({'language':lang,'path':path.relative_to(ROOT).as_posix(),'before_sha256':hashlib.sha256(original.encode()).hexdigest(),
                  'after_sha256':sha(path),'only_one_sentence_and_SEC_table_changed':True,'counts':after_counts})
    diffs.extend(difflib.unified_diff(original.splitlines(keepends=True),after.splitlines(keepends=True),
                                    fromfile=lang+'_before.tex',tofile=lang+'_after.tex'))
(OUT/'edits.diff').write_text(''.join(diffs),encoding='utf-8')
with (OUT/'A8_TABLE_FILL.csv').open('x',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['circuit','proven','unproven','runtime_s_full','runtime_s_display']);writer.writeheader()
    writer.writerows({'circuit':r['circuit'],'proven':r['proven'],'unproven':r['unproven'],
                     'runtime_s_full':r['runtime_s'],'runtime_s_display':f"{r['runtime_s']:.3f}"} for r in rows)
with (OUT/'EDIT_RECEIPT.json').open('x',encoding='utf-8') as f:
    json.dump({'scope':'A functionality sentence and SEC table only; no new WNS, other results or figure edits',
               'A8_sources_sha256':binding,'edits':edits},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(edits,ensure_ascii=False,indent=2))
