from pathlib import Path
import json, hashlib, re, sys
import pymupdf
from PIL import Image,ImageDraw
root=Path.cwd(); rd=root/'paper/zh/review_rounds/r28_20261019'; build=rd/sys.argv[1]
out=build/'render_qa';out.mkdir(exist_ok=True)
src=root/'paper/zh/manuscript'/sys.argv[2];pdf=root/'paper/zh/build'/src.with_suffix('.pdf').name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((build/'BUILD_RECEIPT.json').read_text(encoding='utf-8'))
assert receipt['passed'] and receipt['source_unchanged'] and sha(src)==receipt['source_sha256'] and sha(pdf)==receipt['pdf_sha256']
text=src.read_text(encoding='utf-8');log=(build/'compile.log').read_text(encoding='utf-8',errors='replace')
labels=re.findall(r'\\label\{([^}]+)\}',text);refs=[s for s in re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text) if not re.fullmatch(r'#\d+',s)]
cites=[s.strip() for group in re.findall(r'\\cite\{([^}]+)\}',text) for s in group.split(',')];bib=re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',text)
graphics=re.findall(r'\\includegraphics[^\{]*\{([^}]+)\}',text)
assert len(labels)==len(set(labels)) and set(refs)<=set(labels) and set(cites)==set(bib) and (not bib or len(bib)==14)
assert list(dict.fromkeys(cites))==bib
paths=[(root/'paper/zh/figures'/p).resolve() for p in graphics];assert all(p.is_file() for p in paths)
diag={'overfull':len(re.findall(r'Overfull \\[hv]box',log)),'underfull':len(re.findall(r'Underfull \\[hv]box',log)),
 'missing_characters':len(re.findall('Missing character',log)),'undefined':len(re.findall(r'(?:Reference|Citation).*undefined|There were undefined',log)),
 'rerun':len(re.findall(r'Rerun to get cross-references right|Label\(s\) may have changed',log)),
 'warnings':re.findall(r'(?:LaTeX(?: Font)?|Package [^\n]+|Class [^\n]+) Warning:[^\n]*',log)}
assert not any(diag[k] for k in ('overfull','missing_characters','undefined','rerun')),diag
doc=pymupdf.open(pdf); pages=[];texts=[]
for i,page in enumerate(doc):
 p=out/f'page_{i+1:02d}.png';page.get_pixmap(dpi=120).save(p);pages.append(p);texts.append(page.get_text())
for start in range(0,len(pages),4):
 sheet=Image.new('RGB',(1680,2420),'#EEEEEE');draw=ImageDraw.Draw(sheet)
 for j,p in enumerate(pages[start:start+4]):
  im=Image.open(p).convert('RGB');im.thumbnail((820,1175));x=j%2*840+(840-im.width)//2;y=j//2*1210+25;sheet.paste(im,(x,y));draw.text((j%2*840+8,j//2*1210+6),f'page {start+j+1}',fill='black')
 sheet.save(out/f'contact_{start//4+1:02d}.png')
(out/'pdf_text_all.txt').write_bytes(('\n\f\n'.join(texts)).encode('utf-8'))
result={'source_sha256':sha(src),'pdf_sha256':sha(pdf),'pages':len(doc),'figures':len(graphics),'tables':len(re.findall(r'\\begin\{table\*?\}',text)),'bibitems':len(bib),'citations_first_order_equals_bib':True,'all_labels_refs_unique_resolved':True,'diagnostics':diag,'graphics':{str(p.relative_to(root)):sha(p) for p in paths},'render_sha256':{p.name:sha(p) for p in pages},'visual_review':'pending root inspection'}
(out/'STATIC_RENDER_QA.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps({k:v for k,v in result.items() if k not in ('render_sha256','graphics')},ensure_ascii=False,indent=2))
