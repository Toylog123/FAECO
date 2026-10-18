"""Independent root post-verification; does not modify archived receipt or inputs."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,time
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--circuits',required=True);a=p.parse_args()
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
for circuit in a.circuits.split(','):
    t=time.monotonic();d=R/'project_docs/evidence/r22_cprime_v3_20261016/full_artifact_archives'/circuit
    assert not (d/'ROOT_POST_VERIFICATION.json').exists()
    rec=json.loads((d/'receipt.json').read_text());before=json.loads((d/'source_before.json').read_text())
    assert rec['status']=='verified' and rec['circuit']==circuit and rec['source_stable'] and rec['restore_all_file_sha_size_match']
    assert before==json.loads((d/'source_after.json').read_text())
    assert json.loads((d/'archive_members.json').read_text())=={k:v['bytes'] for k,v in before.items()}
    assert json.loads((d/'restore_check.json').read_text())['files']==before
    for rel,row in before.items():assert (R/rel).stat().st_size==row['bytes'] and sha(R/rel)==row['sha256'],rel
    for rel,h in rec['sidecar_hashes'].items():assert sha(d/rel)==h,rel
    whole=hashlib.sha256()
    for index,v in enumerate(rec['volumes'],1):
        file=d/v['path'];assert int(file.suffix[1:])==index
        assert file.stat().st_size==v['bytes'] and v['bytes']<=80*1024*1024 and sha(file)==v['sha256']
        whole.update(file.read_bytes())
    assert whole.hexdigest()==rec['archive_whole_sha256']
    proc=subprocess.run([shutil.which('7z'),'t',str(d/rec['volumes'][0]['path']),'-sccUTF-8'],capture_output=True,timeout=120)
    assert proc.returncode==0 and b'Everything is Ok' in proc.stdout
    (d/'root_test.log').write_bytes(proc.stdout+proc.stderr)
    result={'receipt_sha256':sha(d/'receipt.json'),'source_files_rechecked':len(before),'source_bytes_stable':True,
        'sidecar_sha256_rechecked':True,'member_and_restore_manifests_rechecked':True,'volume_sha256_rechecked':True,
        'whole_archive_sha256_rechecked':True,'independent_7z_t_returncode':proc.returncode,
        'independent_7z_t_log_sha256':sha(d/'root_test.log'),'runtime_s':time.monotonic()-t,
        'verifier_invoked_path':'scratch/verify_cprime_case_archive.py','verifier_sha256':sha(Path(__file__)),
        'decision':'accepted within '+circuit+' archive scope; not full matrix'}
    with (d/'ROOT_POST_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result),flush=True)
