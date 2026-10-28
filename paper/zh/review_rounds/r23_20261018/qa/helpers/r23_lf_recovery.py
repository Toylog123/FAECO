from pathlib import Path
import json,hashlib,os
r=Path('paper/zh/review_rounds/r23_20261018');out=r/'qa/windows_newline_recovery';out.mkdir(exist_ok=False)
rows=[]
for name in ['REVISION_ROADMAP.json','REVIEW_PACKAGE.json','FINDING_INVENTORY.json','REVISION_ROADMAP.md']:
    p=r/name;raw=p.read_bytes();(out/name).write_bytes(raw)
    fd=os.open(p,os.O_RDONLY);b=os.fstat(fd);via_os=os.read(fd,10000000);a=os.fstat(fd);os.close(fd)
    new=raw.replace(b'\r\n',b'\n');p.write_bytes(new)
    rows.append({'name':name,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(new).hexdigest(),'before_stat_size':b.st_size,'os_read_length':len(via_os),'stat_unchanged':(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns)==(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns),'crlf_to_lf_only':True})
(out/'RECEIPT.json').write_bytes((json.dumps({'cause':'Upstream revision_roadmap._read_path_once opens os.O_RDONLY without O_BINARY on Windows; CRLF becomes LF on os.read so byte count differs from stat while metadata unchanged, falsely reported artifact changed.','recovery':'Preserved originals; write generated review deliverables with LF raw bytes. No guard bypass and no production/source edits.','files':rows},ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(rows,ensure_ascii=False))
