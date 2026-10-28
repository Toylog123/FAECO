from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd().resolve();out=root/'project_docs/evidence/r22_oi049_timeout_bytes_20261018'
p=root/'.gitattributes';before=p.read_bytes();rule=b'project_docs/evidence/r22_oi049_timeout_bytes_20261018/** -text'
assert rule not in before
(out/'GITATTRIBUTES_BEFORE.txt').write_bytes(before)
newline=b'\r\n' if b'\r\n' in before else b'\n'
after=before+(b'' if before.endswith(b'\n') else newline)+rule+newline
p.write_bytes(after)
command=['git','check-attr','text','--','project_docs/evidence/r22_oi049_timeout_bytes_20261018/red_v3/RESULT.json']
check=subprocess.check_output(command,text=True).strip();assert check.endswith('text: unset')
sha=lambda b:hashlib.sha256(b).hexdigest()
record={'before_sha256':sha(before),'after_sha256':sha(after),'exact_before_prefix_retained':after.startswith(before),'appended_rule':rule.decode(),'argv':command,'actual_check_attr':check,'scope':'Preserve exact raw proof/failure-injection evidence bytes in future Git staging; no current staging/commit/HEAD change.'}
(out/'GITATTRIBUTES_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(record))
