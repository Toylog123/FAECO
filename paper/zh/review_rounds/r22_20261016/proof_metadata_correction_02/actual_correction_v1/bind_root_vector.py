from pathlib import Path
import json,hashlib
r=Path.cwd();out=r/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1';source=out/'FINAL_QA.json';v=json.loads(source.read_text(encoding='utf-8'));root=r/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/root_vector_head_binding/VECTOR_HEAD_BINDING.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(root)=='c4ff6ad9429a692e9a12937f869de6d72fd3987df7093ae4534c9d1838f3bf8b'
v['prior_QA_sha256']=sha(source);v['figure_artwork_binding']={'receipt':root.relative_to(r).as_posix(),'sha256':sha(root),'scope':'Root independently compared all 7 ZH and 7 EN vector PDFs to fixed f761 HEAD blobs; exact equality. This is not a before-filesystem capture by this child.','this_child_before_vector_SHA_capture':False}
with (out/'FINAL_QA_v2.json').open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print('FINAL_QA_v2',sha(out/'FINAL_QA_v2.json'))
