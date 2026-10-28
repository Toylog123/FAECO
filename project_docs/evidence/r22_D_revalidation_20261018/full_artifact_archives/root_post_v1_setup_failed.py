"""Independent postcheck of producer archive parts, sidecars and all restored bytes."""
from pathlib import Path
import json,hashlib,time,sys
BASE=Path('project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives')
ROOT=Path.cwd().resolve()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
checks=[]
for circuit in sys.argv[1:]:
    start=time.monotonic();base=BASE/circuit;r=load(base/'receipt.json')
    assert r['status']=='verified' and r['circuit']==circuit and not r['eda_executed']
    assert r['source_stable'] and r['member_set_and_sizes_match'] and r['seven_zip_t_passed'] and r['restore_all_file_sha_size_match']
    before=load(base/'source_before.json');after=load(base/'source_after.json');restored=load(base/'restore_check.json')
    members=load(base/'archive_members.json')
    assert before==after==restored['files'] and set(members)==set(before)
    assert len(before)==r['source_file_count']==restored['restored_file_count']
    assert sum(v['bytes'] for v in before.values())==r['source_bytes']
    assert sha(base/'source_before.json')==r['source_before_sha256'] and sha(base/'source_after.json')==r['source_after_sha256']
    for name,expected in r['sidecar_hashes'].items():assert sha(base/name)==expected
    for cmd in r['commands']:
        assert cmd['returncode']==0 and sha(Path(cmd['log']))==cmd['log_sha256']
    for root_name in r['source_roots']:
        actual={p.relative_to(ROOT).as_posix() for p in Path(root_name).rglob('*') if p.is_file()}
        assert actual <= set(before)
    restore_root=(ROOT/r['restore_check_root']).resolve();assert restore_root.is_relative_to(ROOT/'scratch')
    for name,entry in before.items():
        p=ROOT/name;q=restore_root/name
        assert p.stat().st_size==q.stat().st_size==entry['bytes']==members[name]
        assert sha(p)==sha(q)==entry['sha256']
    whole=hashlib.sha256()
    for volume in r['volumes']:
        p=base/volume['path'];assert p.stat().st_size==volume['bytes'] and sha(p)==volume['sha256']
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):whole.update(b)
    assert whole.hexdigest()==r['archive_whole_sha256']
    result={'accepted':True,'scope':'Root independently rehashed every current source and restored file, all archive volumes and recorded command logs; producer performed 7z t/list/restore',
       'circuit':circuit,'source_file_count':len(before),'original_and_restored_all_match':True,
       'all_volume_and_sidecar_hashes_match':True,'producer_receipt_sha256':sha(base/'receipt.json'),
       'archive_sha256':r['archive_whole_sha256'],'archive_bytes':r['archive_bytes'],'runtime_s':time.monotonic()-start,
       'checker_sha256':sha(Path(__file__))}
    with (base/'ROOT_POST_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result),flush=True);checks.append(result)
target=BASE/'root_post_d_archives_20261018.py'
if target.exists():assert target.read_bytes()==Path(__file__).read_bytes()
else:target.write_bytes(Path(__file__).read_bytes())
