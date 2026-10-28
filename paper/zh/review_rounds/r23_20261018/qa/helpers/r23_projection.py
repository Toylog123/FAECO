from pathlib import Path
import sys,json,hashlib,re
root=Path.cwd();r=root/'paper/zh/review_rounds/r23_20261018'
sys.path.insert(0,'C:/Users/16225/.codex/skills/academic-research-skills/scripts')
from ars_anchorize_draft import anchorize_file
raw=(r/'inputs/manuscript.tex').read_bytes(); text=raw.decode('utf-8')
lines=text.splitlines(keepends=True); chunks=[]; start=1; acc=[]
for n,line in enumerate(lines,1):
    acc.append(line)
    if not line.strip():
        chunks.append((start,n,''.join(acc)));acc=[];start=n+1
if acc: chunks.append((start,len(lines),''.join(acc)))
assert ''.join(x[2] for x in chunks).encode('utf-8')==raw
assert all('~~~~' not in x[2] for x in chunks)
surrogate=''.join('~~~~latex\n'+x[2]+('' if x[2].endswith('\n') else '\n')+'~~~~\n\n' for x in chunks)
p=r/'inputs/review_projection.md'; assert not p.exists()
p.write_bytes(surrogate.encode('utf-8'))
manifest=r/'inputs/review_projection.block-manifest.json'
summary=anchorize_file(p,manifest)
m=json.loads(manifest.read_text(encoding='utf-8')); assert len(m['blocks'])==len(chunks)
mapping=[{'block_id':b['block_id'],'tex_first_line':c[0],'tex_last_line':c[1],'tex_fragment_sha256':hashlib.sha256(c[2].encode('utf-8')).hexdigest()} for b,c in zip(m['blocks'],chunks)]
receipt={'scope':'Read-only fenced paragraph projection for roadmap binding; NOT a patchable LaTeX draft and NOT write authority. Later LaTeX changes require exact source mapping and author adjudication. All source bytes round-trip from original chunks; original manuscript unchanged.','source_sha256':hashlib.sha256(raw).hexdigest(),'projection_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'mapping':mapping}
(r/'inputs/PROJECTION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary));print(json.dumps({'paragraphs':len(chunks),'source_bytes_round_trip':True}))
