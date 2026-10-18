from pathlib import Path
import subprocess,json
out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/final_test_fixture_cleanup')
pre=json.loads((out/'PRE_CLEANUP.json').read_text(encoding='utf-8'))
paths=[r['path'] for r in pre['tracked_restored']]
def oid(spec):return subprocess.check_output(['git','rev-parse',spec],text=True).strip()
before={p:oid(':'+p) for p in paths}
for p in paths:
    assert before[p]==oid('HEAD:'+p)
    assert subprocess.check_output(['git','hash-object',p],text=True).strip()==before[p]
    assert subprocess.check_output(['git','hash-object','--no-filters',p],text=True).strip()==before[p]
p=subprocess.run(['git','add','--',*paths],capture_output=True)
assert p.returncode==0
after={p:oid(':'+p) for p in paths}
assert before==after
assert not subprocess.check_output(['git','diff','--cached','--name-only','--',*paths]).strip()
assert not subprocess.check_output(['git','status','--porcelain','--',*paths]).strip()
receipt={'initial_cleanup_verification':'failed at git-status cleanliness despite exact HEAD/worktree/raw+filtered hash identity; original verification script retained',
 'index_refresh_only_no_blob_changes':True,'index_before':before,'index_after':after,
 'git_add_stderr':p.stderr.decode('utf-8',errors='replace')}
(out/'INDEX_REFRESH_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print('Refreshed five fixture index stat records; all blob IDs unchanged')
