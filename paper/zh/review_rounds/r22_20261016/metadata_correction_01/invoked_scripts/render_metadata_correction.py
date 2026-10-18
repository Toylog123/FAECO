import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--language',choices=['zh','en'],required=True);a=p.parse_args()
lang=a.language;base=R/'paper/zh/review_rounds/r22_20261016/metadata_correction_01'
receipt=json.loads((base/(lang+'_build_receipt.json')).read_text())
pdf=R/receipt['pdf'];assert hashlib.sha256(pdf.read_bytes()).hexdigest()==receipt['pdf_sha256']
out=R/'scratch/r22_metadata_01_render'/lang;out.mkdir(parents=True,exist_ok=False)
command=[shutil.which('pdftoppm'),'-r','100','-png',str(pdf),str(out/'page')]
t=time.monotonic();proc=subprocess.run(command,capture_output=True,timeout=150)
(out/'render.stdout.bin').write_bytes(proc.stdout);(out/'render.stderr.bin').write_bytes(proc.stderr)
assert proc.returncode==0
pages=sorted(out.glob('page-*.png'))
expected=json.loads((base/(lang+'_static_build_qa.json')).read_text())['pages'];assert len(pages)==expected
for offset in range(0,len(pages),16):
    selected=pages[offset:offset+16];sheet=Image.new('RGB',(1440,535*((len(selected)+3)//4)),'#E9ECEF');draw=ImageDraw.Draw(sheet)
    for i,file in enumerate(selected):
        image=Image.open(file).convert('RGB');image.thumbnail((352,502))
        x=(i%4)*360+(360-image.width)//2;y=(i//4)*535+22
        sheet.paste(image,(x,y));draw.text(((i%4)*360+8,(i//4)*535+5),lang+' page '+str(offset+i+1),fill='black')
    sheet.save(out/('contact_%02d.png'%(offset//16+1)))
textproc=subprocess.run([shutil.which('pdftotext'),'-layout',str(pdf),'-'],capture_output=True,timeout=30)
assert textproc.returncode==0
(out/'pdf_text_layout.txt').write_bytes(textproc.stdout)
text=textproc.stdout.decode('utf-8');sections=text.split('\f');matches=[]
for i,part in enumerate(sections):
    if ('PicoRV32' in part and ('clock period' in part or '分别为 5' in part or '分别为5' in part or 'use periods of 5' in part)):
        matches.append(i+1)
report={'language':lang,'pdf_sha256':receipt['pdf_sha256'],'render_returncode':proc.returncode,
        'pages_rendered':len(pages),'runtime_s':time.monotonic()-t,'metadata_page_candidates':matches,
        'visual_review':'pending','output_dir':str(out.relative_to(R)),
        'page_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in pages}}
with (base/(lang+'_render_receipt.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='page_sha256'}))
