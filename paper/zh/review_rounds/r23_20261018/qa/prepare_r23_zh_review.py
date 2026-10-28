from pathlib import Path
import json,hashlib,subprocess,datetime,re,shutil
import pymupdf
ROOT=Path.cwd().resolve();OUT=ROOT/'paper/zh/review_rounds/r23_20261018'
OUT.mkdir(exist_ok=False);(OUT/'inputs').mkdir();(OUT/'seats').mkdir();(OUT/'qa').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex'
pdf=ROOT/'paper/zh/build/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.pdf'
assert sha(source)=='c750ff9cad382ff3fdf3c067980016a0ebcc7be7c2fff2a198c5f5396767918b'
assert sha(pdf)=='173ae809eb7b2d3d142880681cdac31e4fc35f7bccc40de9bab19f384d38070b'
shutil.copyfile(source,OUT/'inputs/manuscript.tex');shutil.copyfile(pdf,OUT/'inputs/manuscript.pdf')
with pymupdf.open(pdf) as doc:
    texts=[page.get_text() for page in doc];assert len(texts)==12
plain='\n\n'.join(f'=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(texts))
(OUT/'inputs/manuscript_pdf_text.txt').write_text(plain,encoding='utf-8')
tex=source.read_text(encoding='utf-8')
(OUT/'inputs/manuscript_numbered.txt').write_text('\n'.join(f'{i+1:04d}: {line}' for i,line in enumerate(tex.splitlines())),encoding='utf-8')
contract_path=Path('C:/Users/16225/.codex/skills/academic-research-skills/shared/contracts/reviewer/full.json')
contract=json.loads(contract_path.read_text(encoding='utf-8'));contract['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
metadata={'title':'FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画','field':'电子设计自动化；预布局门级时序ECO；候选搜索与形式验证','word_count':len(re.findall(r'[\u4e00-\u9fff]|[A-Za-z0-9_]+',plain))}
(OUT/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=ROOT/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/independent_final_review/attempt1/zh_renders'
render=OUT/'inputs/rendered';render.mkdir()
for p in prior.glob('*.png'):shutil.copyfile(p,render/p.name)
attribute=ROOT/'.gitattributes';before=attribute.read_bytes();(OUT/'qa/GITATTRIBUTES_BEFORE.txt').write_bytes(before)
rule=b'paper/zh/review_rounds/r23_20261018/** -text'
assert rule not in before
newline=b'\r\n' if b'\r\n' in before else b'\n';attribute.write_bytes(before+(b'' if before.endswith(b'\n') else newline)+rule+newline)
receipt={'utc':contract['generated_at'],'scope':'New read-only Chinese full review; no manuscript/figure/source edits or EDA','source_path':str(source.relative_to(ROOT)),'source_sha256':sha(source),'pdf_path':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),'pages':12,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'contract_template_path':str(contract_path),'contract_template_sha256':sha(contract_path),'metadata':metadata,'inputs':{p.relative_to(OUT).as_posix():sha(p) for p in (OUT/'inputs').rglob('*') if p.is_file()},'render_reuse':'Exact prior independently rendered PNGs for the same SHA-bound PDF; current review visual observations still required.','no_confirmed_target_criteria':'criteria_binding_unavailable','review_topology':'Five same-family role-separated reviewer seats, fresh fork-none contexts, two-call commitment. Not calibrated; no claim of independent error processes.'}
(OUT/'INPUT_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'qa'/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'review_dir':str(OUT),'source_sha':sha(source),'pdf_sha':sha(pdf),'pages':12,'metadata':metadata},ensure_ascii=False))
