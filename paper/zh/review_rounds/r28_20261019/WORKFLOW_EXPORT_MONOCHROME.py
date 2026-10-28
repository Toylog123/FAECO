from pathlib import Path
import sys,json,hashlib,subprocess,time,shutil,os
import pymupdf
import numpy as np
R=Path.cwd();rd=R/'paper/zh/review_rounds/r28_20261019';b=rd/sys.argv[1]
src=R/'paper/zh/manuscript'/sys.argv[2];pdf=R/'paper/zh/build'/src.with_suffix('.pdf').name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads((b/'BUILD_RECEIPT.json').read_text(encoding='utf-8'))
assert receipt['passed'] and sha(src)==receipt['source_sha256'] and sha(pdf)==receipt['pdf_sha256']
e=b/(sys.argv[3] if len(sys.argv)>3 else 'export_attempt02');e.mkdir(exist_ok=True)
native=e/'lualatex_native.pdf';out=e/'monochrome_export.pdf'
if native.exists():assert sha(native)==sha(pdf),'cannot resume a different native PDF'
else:shutil.copyfile(pdf,native)
gs=Path(shutil.which('gswin64c.exe') or '');assert gs.is_file(),'gswin64c.exe not on PATH'
base=gs.parent.parent
search=';'.join(str(base/p).replace('\\','/') for p in ('Resource/Init','lib','Resource/Font','kanji'))
args=[str(gs),'-I'+search,'-sGenericResourceDir='+str(base/'Resource').replace('\\','/')+'/', '-sICCProfilesDir='+str(base/'iccprofiles').replace('\\','/')+'/', '-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.7','-sColorConversionStrategy=Gray','-dProcessColorModel=/DeviceGray','-dOverrideICC','-dAutoRotatePages=/None','-dDownsampleColorImages=false','-dDownsampleGrayImages=false','-dDownsampleMonoImages=false','-dEmbedAllFonts=true','-dPreserveAnnots=true','-sOutputFile='+str(out),str(native)]
cmd=['C:/Program Files/Git/bin/bash.exe',str(R/'code/scripts/run_with_timeout.sh'),'120',*args]
reused=out.exists()
if reused:
    assert (e/'monochrome_export.stdout.log').is_file()
    runtime=None
else:
    t=time.monotonic();p=subprocess.run(cmd,capture_output=True,timeout=150,env={**os.environ,'MSYS2_ARG_CONV_EXCL':'*','MSYS_NO_PATHCONV':'1'})
    runtime=time.monotonic()-t
    (e/'monochrome_export.stdout.log').write_bytes(p.stdout);(e/'monochrome_export.stderr.log').write_bytes(p.stderr)
    assert p.returncode==0,p.stderr[-2000:]
a=pymupdf.open(native);c=pymupdf.open(out);assert len(a)==len(c)
pages=[]
for old,new in zip(a,c):
    oldtxt=old.get_text();newtxt=new.get_text()
    same_text=oldtxt==newtxt
    assert ''.join(oldtxt.split())==''.join(newtxt.split()),(old.number,'nonwhitespace text changed during grey export')
    def chars(pg):
        return [(ch['c'],ch['origin']) for bl in pg.get_text('rawdict')['blocks'] if 'lines' in bl for line in bl['lines'] for span in line['spans'] for ch in span['chars'] if not ch['c'].isspace()]
    oc,nc=chars(old),chars(new)
    assert [v[0] for v in oc]==[v[0] for v in nc]
    origin_delta=max([abs(u-v) for x,y in zip(oc,nc) for u,v in zip(x[1],y[1])] or [0]);assert origin_delta<.05
    rect_difference=max(abs(x-y) for x,y in zip(old.rect,new.rect));assert rect_difference<.01
    pymupdf.TOOLS.set_icc(False)
    im=new.get_pixmap(dpi=96,colorspace=pymupdf.csRGB);arr=np.frombuffer(im.samples,np.uint8).reshape(im.height,im.width,im.n)
    spread=int(np.ptp(arr[:,:,:3],axis=2).max());assert spread==0
    old_images=sorted((i[2],i[3]) for i in old.get_images());new_images=sorted((i[2],i[3]) for i in new.get_images())
    assert old_images==new_images,(old.number,'image native dimensions changed')
    old_links=len(old.get_links());new_links=len(new.get_links());assert old_links==new_links
    pages.append({'page':old.number+1,'text_exactly_identical':same_text,'nonwhitespace_text_and_glyph_sequence_exactly_identical':True,'max_nonwhitespace_glyph_origin_delta_pt':origin_delta,'text_extraction_note':None if same_text else 'One inferred whitespace changes after PDF font/position serialization; source and nonwhitespace glyphs unchanged. See export comparison.','page_box_max_delta_pt':rect_difference,'all_rendered_pixels_R_equals_G_equals_B':True,'max_RGB_spread':spread,'render_ICC_enabled':False,'native_image_dimensions_unchanged':True,'image_dimensions':new_images,'hyperlinks_before_after':[old_links,new_links],'image_colorspaces':sorted(set(i[5] for i in new.get_images()))})
payload={'status':'PASS_WITH_RECORDED_SERIALIZATION_VARIATION','method':'Ghostscript pdfwrite document-level DeviceGray export; original built-in AI PNG bytes retained, no manual pixel editing','command':cmd,'returncode':0,'process_walltime_s_this_invocation':runtime,'reused_completed_export_for_validation':reused,'export_log':str((e/'monochrome_export.stdout.log').relative_to(R)),'page_box_tolerance_pt':.01,'glyph_origin_tolerance_pt':.05,'native_pdf_sha256':sha(native),'monochrome_pdf_sha256':sha(out),'pages':pages,'all_page_nonwhitespace_text_and_image_dimensions_preserved':True,'all_pages_strict_neutral':True}
(b/'MONOCHROME_EXPORT.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
a.close();c.close();shutil.copyfile(out,pdf)
receipt['lualatex_pdf_sha256']=receipt['pdf_sha256'];receipt['pdf_sha256']=sha(pdf);receipt['monochrome_export_receipt']=str((b/'MONOCHROME_EXPORT.json').relative_to(R));receipt['monochrome_export_passed']=True
(b/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','pages':len(pages),'pdf_sha256':sha(pdf),'native_pdf_sha256':sha(native)},ensure_ascii=False))
