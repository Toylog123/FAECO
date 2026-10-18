from pathlib import Path
import json,hashlib,subprocess

out=Path('project_docs/evidence/r22_s_spef_integrated_20261018/test_output_restore')
before=json.loads((out/'BEFORE.json').read_text(encoding='utf-8'))
rows=[]
prefix='data/cases/minimal/iscas85_c17_case01/results/'
for row in before['files']:
    p=Path(row['path'])
    initial=p.read_bytes()
    head=(out/'head'/p.relative_to(prefix)).read_bytes()
    assert hashlib.sha256(head).hexdigest()==row['head_sha256']
    # git restore applied text checkout conversion. Preserve that observation,
    # then restore the already-snapshotted HEAD bytes exactly.
    row={**row,'git_restore_checkout_sha256':hashlib.sha256(initial).hexdigest(),
         'checkout_matches_head_with_crlf_normalized':initial.replace(b'\r\n',b'\n')==head.replace(b'\r\n',b'\n')}
    assert row['checkout_matches_head_with_crlf_normalized']
    p.write_bytes(head)
    assert p.read_bytes()==head
    rows.append(row)
receipt={'scope':'test fixture outputs only; no scientific result restoration',
 'initial_restore_exact_byte_assertion':'failed because git text checkout applied CRLF conversion; original script and snapshots retained',
 'git_core_autocrlf':subprocess.check_output(['git','config','--get','core.autocrlf'],text=True).strip(),
 'restored_count':len(rows),'all_head_bytes_restored':True,'files':rows}
(out/'RESTORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
for name in ['preserve_restore_native_test_outputs_20261018.py',Path(__file__).name]:
    (out/name).write_bytes((Path('scratch')/name).read_bytes())
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
