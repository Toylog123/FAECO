from pathlib import Path
import hashlib,json,shutil,subprocess

out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/source_stage_qa')
out.mkdir(exist_ok=False)
v5=out.parent/'v5'
before=json.loads((v5/'SOURCE_BEFORE.json').read_text())
after=json.loads((v5/'SOURCE_AFTER.json').read_text())
current={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('code').rglob('*.py'))}
assert before==after==current
r=json.loads((v5/'RUN_RECEIPT.json').read_text())
assert r['returncode']==0 and r['pythonutf8']=='1' and r['python_sources']==174
assert hashlib.sha256((v5/'pytest.log').read_bytes()).hexdigest()==r['log_sha256']
assert '1056 passed, 156 subtests passed in 208.27s' in (v5/'pytest.log').read_text()
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','data/cases/minimal/iscas85_c17_case01/results']).strip()
argv=['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--ignore-space-at-eol','--check','--','.',' :(exclude)project_docs/evidence/**'.strip(),':(exclude)data/**']
p=subprocess.run(argv,capture_output=True)
(out/'semantic_whitespace.stdout.log').write_bytes(p.stdout)
(out/'semantic_whitespace.stderr.log').write_bytes(p.stderr)
assert p.returncode==0
receipt={'scope':'Root integration and source-stage QA, not scientific validation',
 'source_before_after_current_identical':True,'python_sources':174,'pytest_passed':1056,'subtests_passed':156,'skipped':0,
 'pytest_log_sha256':r['log_sha256'],'run_receipt_sha256':hashlib.sha256((v5/'RUN_RECEIPT.json').read_bytes()).hexdigest(),
 'native_fixture_git_clean':True,'whitespace_argv':argv,'whitespace_returncode':p.returncode,
 'whitespace_note':'Byte-pinned CRLF sources retained. Initial default check treated CR as trailing whitespace; semantic check explicitly recognizes CR-at-EOL; raw evidence excluded.',
 'known_open_boundaries':['Historical top-omitted proof objects require individual impact audit','b18 inout passive RC design not implemented','Four-state proof support unsupported','OI049 timeout bytes tail rendering is a static pending issue'],
 'current_sources':current}
(out/'ROOT_SOURCE_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['write_r22_source_stage_qa_20261018.py','prepare_regression_v5.py']:
    shutil.copyfile(Path('scratch')/name,out/name)
print(json.dumps({k:v for k,v in receipt.items() if k not in ['current_sources','whitespace_argv']}))
