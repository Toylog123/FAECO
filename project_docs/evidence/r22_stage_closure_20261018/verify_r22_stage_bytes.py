"""Verify index bytes for all byte-pinned staged changes before committing."""
import hashlib, json, subprocess
from pathlib import Path
root=Path.cwd()
run=lambda a,**kw:subprocess.run(['git',*a],check=True,capture_output=True,**kw).stdout
paths=[p.decode('utf-8') for p in run(['diff','--cached','--name-only','-z']).split(b'\0') if p]
attrs=run(['check-attr','-z','--stdin','text'],input=b''.join(p.encode()+b'\0' for p in paths)).split(b'\0')
pinned=[attrs[i].decode() for i in range(0,len(attrs)-1,3) if attrs[i+2]==b'unset']
index={r.split(b'\t',1)[1].decode():r.split()[1].decode() for r in run(['ls-files','--stage','-z']).split(b'\0') if r}
payload=''.join(index[p]+'\n' for p in pinned).encode()
data=run(['cat-file','--batch'],input=payload)
pos=0; failures=[]; checked=[]
for p in pinned:
    end=data.index(b'\n',pos); header=data[pos:end].split(); size=int(header[2]); pos=end+1
    blob=data[pos:pos+size];pos+=size+1
    disk=(root/p).read_bytes()
    same=blob==disk
    if not same:failures.append(p)
    checked.append({'path':p,'sha256':hashlib.sha256(disk).hexdigest(),'bytes':len(disk),'index_identical':same})
receipt={'staged_changed_paths':len(paths),'byte_pinned_files_verified':len(pinned),'mismatches':failures,'files':checked}
Path('scratch/STAGED_BYTES_VERIFICATION_20261018.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
assert not failures
