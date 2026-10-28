"""Preserve complete current-run QA fixtures in a verified archive; no deletion."""
from pathlib import Path
import hashlib,json,time,zipfile
BASE=Path('project_docs/evidence/r22_adapter_current_pin_20261018/v2')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
receipt=load(BASE/'RUN_RECEIPT.json')
before=load(BASE/'SOURCE_BEFORE.json');after=load(BASE/'SOURCE_AFTER.json')
assert before==after and receipt['sources_stable'] and receipt['all_returncodes_zero'] and receipt['code_clean_after']
assert receipt['head']==receipt['head_after']=='f761ee1996a83fc4f0f3de0999b74d85a8237858'
assert len([p for p in before if p.startswith('code/')])==174
for case,expected in [('B3','51 passed in 19.72s'),('C','84 passed in 98.30s')]:
    assert expected in (BASE/(case+'.stdout.log')).read_text(encoding='utf-8')
    row=next(r for r in receipt['cases'] if r['name']==case)
    for stream in ['stdout','stderr']:assert sha(BASE/(case+'.'+stream+'.log'))==row[stream+'_sha256']
paths=sorted(p for folder in ['pytest_tmp_B3','pytest_tmp_C'] for p in (BASE/folder).rglob('*') if p.is_file())
inventory={p.relative_to(BASE).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}
with (BASE/'QA_FIXTURE_MEMBERS.json').open('x',encoding='utf-8') as f:json.dump(inventory,f,indent=2)
started=time.monotonic();archive=BASE/'QA_FIXTURES_FULL.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in paths:z.write(p,p.relative_to(BASE).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None and set(z.namelist())==set(inventory)
    for name,record in inventory.items():
        raw=z.read(name);assert len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256']
for p in paths:assert sha(p)==inventory[p.relative_to(BASE).as_posix()]['sha256']
out={'accepted':True,'scope':'Current f761 pin mocked adapter QA only; no scientific EDA or historical recovery',
     'B3_pass':51,'C_adapter_and_registration_pass':84,'production_source_count':174,'production_sources_stable':True,
     'all_snapshot_entries':len(before),'B3_tree_entries_including_old_sandbox':5628,'C_tree_entries':8,
     'fixture_file_count':len(paths),'fixture_total_bytes':sum(r['bytes'] for r in inventory.values()),
     'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'zip_crc_and_all_member_bytes_verified':True,
     'original_fixtures_retained':True,'runtime_s':time.monotonic()-started,
     'run_receipt_sha256':sha(BASE/'RUN_RECEIPT.json'),'manifest_sha256':sha(BASE/'QA_FIXTURE_MEMBERS.json')}
(BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
with (BASE/'ROOT_QA_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
print(json.dumps(out))
