from pathlib import Path
import json,hashlib,subprocess

root=Path.cwd().resolve();base=root/'data/cases/minimal/iscas85_c17_case01/results'
out=root/'project_docs/evidence/r22_s_spef_integrated_20261018/final_test_fixture_cleanup'
pre=json.loads((out/'PRE_CLEANUP.json').read_text(encoding='utf-8'))
plan=pre['untracked_move_plan']
for row in pre['tracked_restored']:
    assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['head_sha256']
moved={}
for row in plan:
    src=Path(row['source']);dest=Path(row['destination'])
    assert not src.exists() and dest.exists()
    files=[dest] if dest.is_file() else sorted(p for p in dest.rglob('*') if p.is_file())
    for p in files:
        relative=Path(row['relative']) if dest.is_file() else Path(row['relative'])/p.relative_to(dest)
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        assert sha==pre['archived_files'][str(relative)]
        moved[str(relative)]=sha
dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',str(base)],text=True)
assert not dirty.strip(),dirty
receipt={'scope':'Reversible native QA byproduct cleanup only','archived_before_cleanup_files':len(pre['archived_files']),
 'tracked_head_bytes_restored':len(pre['tracked_restored']),'moved_untracked_items':len(plan),'moved_files_verified':len(moved),
 'original_test_output_git_status_clean':True,'moved_files':moved,
 'archive_sha256':hashlib.sha256((out/'all_test_results_before_cleanup.zip').read_bytes()).hexdigest()}
(out/'CLEANUP_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in receipt.items() if k!='moved_files'}))
