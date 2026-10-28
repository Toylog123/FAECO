from pathlib import Path
import json,hashlib,sys
r=Path('paper/zh/review_rounds/r23_20261018');out=r/'qa/windows_projection_recovery';out.mkdir(exist_ok=False)
sys.path.insert(0,'C:/Users/16225/.codex/skills/academic-research-skills/scripts')
from ars_anchorize_draft import anchorize_file
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['inputs/review_projection.md','inputs/review_projection.block-manifest.json','inputs/PROJECTION_RECEIPT.json','REVISION_ROADMAP.json','REVIEW_PACKAGE.json','REVISION_ROADMAP.md']
for name in names:
    p=r/name;b=out/name;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes())
p=r/'inputs/review_projection.md';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
anchorize_file(p,r/'inputs/review_projection.block-manifest.json')
pr=json.loads((r/'inputs/PROJECTION_RECEIPT.json').read_text(encoding='utf-8'));pr['projection_sha256']=sha(p);pr['manifest_sha256']=sha(r/'inputs/review_projection.block-manifest.json');pr['line_endings']='Projection code spans normalized CRLF->LF only; exact original source bytes preserved in inputs/manuscript.tex and mapping fragment hashes. All original chunk bytes reconstructed before normalization. No semantic edits.'
(r/'inputs/PROJECTION_RECEIPT.json').write_bytes((json.dumps(pr,ensure_ascii=False,indent=2)+'\n').encode())
roadmap=json.loads((r/'REVISION_ROADMAP.json').read_text(encoding='utf-8'));roadmap['base_draft_sha256']=pr['projection_sha256'];roadmap['block_manifest_sha256']=pr['manifest_sha256']
(r/'REVISION_ROADMAP.json').write_bytes((json.dumps(roadmap,ensure_ascii=False,indent=2)+'\n').encode())
package=json.loads((r/'REVIEW_PACKAGE.json').read_text(encoding='utf-8'));package['revision_roadmap']=roadmap
(r/'REVIEW_PACKAGE.json').write_bytes((json.dumps(package,ensure_ascii=False,indent=2)+'\n').encode())
md=(r/'REVISION_ROADMAP.md').read_text(encoding='utf-8').replace('原文逐字节映射见','投影仅规范化行尾，原文逐字节片段映射见');(r/'REVISION_ROADMAP.md').write_bytes(md.encode())
(out/'RECEIPT.json').write_bytes((json.dumps({'cause':'Same Windows os.O_RDONLY text translation affected mixed-newline fenced TeX projection.','recovery':'Original failed artifacts preserved; projection only CRLF->LF, official anchorizer regenerated raw manifest digest; roadmap/package binding hashes updated before acceptance, no findings/actions changed.','source_unchanged':sha(r/'inputs/manuscript.tex')=='c750ff9cad382ff3fdf3c067980016a0ebcc7be7c2fff2a198c5f5396767918b','projection_sha256':pr['projection_sha256'],'roadmap_sha256':sha(r/'REVISION_ROADMAP.json')},ensure_ascii=False,indent=2)+'\n').encode())
print('projection LF-only recovery complete; original review source and findings unchanged')
