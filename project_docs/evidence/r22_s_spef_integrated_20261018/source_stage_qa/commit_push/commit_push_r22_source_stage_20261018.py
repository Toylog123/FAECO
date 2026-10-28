from pathlib import Path
import subprocess,json,time,hashlib

out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/source_stage_qa/commit_push')
out.mkdir(exist_ok=False)
before=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert before=='7231e0296da357df435414f75b0a41fe78265837'
assert not subprocess.check_output(['git','diff','--name-only']).strip()
staged=subprocess.check_output(['git','diff','--cached','--name-only','-z']).split(b'\0')
assert len([x for x in staged if x])==1278
receipts=[]
for name,argv in [
 ('commit',['git','commit','-m','Fix CEC proof-object binding and paired parasitic evidence']),
 ('push',['git','push','origin','main'])]:
    start=time.monotonic()
    p=subprocess.run(argv,capture_output=True,timeout=180)
    (out/(name+'.stdout.log')).write_bytes(p.stdout)
    (out/(name+'.stderr.log')).write_bytes(p.stderr)
    receipts.append({'argv':argv,'returncode':p.returncode,'runtime_s':time.monotonic()-start})
    (out/'PROGRESS.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
    assert p.returncode==0,(name,p.stderr.decode('utf-8',errors='replace')[-1500:])
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True,timeout=60).split()[0]
assert head==remote and head!=before
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','code']).strip()
receipt={'previous_head':before,'new_source_commit':head,'remote_main':remote,
 'staged_files_committed':1278,'source_tree_clean':True,'operations':receipts,
 'scope':'Implementation/evidence stage checkpoint; no scientific baseline tag or EDA',
 'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
(out/'COMMIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(receipt))
