"""Read-only fixed-HEAD vector comparison, not a reconstructed pre-edit snapshot."""
from pathlib import Path
import subprocess, hashlib, json, re, datetime
ROOT=Path.cwd().resolve()
OUT=ROOT/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/root_vector_head_binding'
OUT.mkdir(exist_ok=False)
HEAD='f761ee1996a83fc4f0f3de0999b74d85a8237858'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
rows=[]
for lang in ['zh','en']:
    files=list((ROOT/f'paper/{lang}/manuscript').glob('*.tex'))
    assert len(files)==1
    tex=files[0].read_text(encoding='utf-8')
    refs=re.findall(r'\\includegraphics[^\{]*\{([^}]+)\}',tex)
    assert len(refs)==7
    for ref in refs:
        candidates=list((ROOT/f'paper/{lang}/figures').rglob(Path(ref).name))
        assert len(candidates)==1,(lang,ref,candidates)
        p=candidates[0];rel=p.relative_to(ROOT).as_posix()
        argv=['git','show',f'{HEAD}:{rel}']
        proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=20)
        assert proc.returncode==0,proc.stderr
        original=p.read_bytes()
        assert original==proc.stdout,rel
        rows.append({'language':lang,'reference':ref,'path':rel,'current_sha256':sha(original),'fixed_head_blob_sha256':sha(proc.stdout),'exact_bytes_equal':True,'argv':argv})
receipt={'scope':'Current 14 included vector PDFs equal immutable f761 Git blobs; not a claim that current hashes are a pre-edit filesystem capture.','head':HEAD,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'all_equal':True}
(OUT/'VECTOR_HEAD_BINDING.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'all_equal':True,'vectors':len(rows),'receipt_sha256':sha((OUT/'VECTOR_HEAD_BINDING.json').read_bytes())}))
