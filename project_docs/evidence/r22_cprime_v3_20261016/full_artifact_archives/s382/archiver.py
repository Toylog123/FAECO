"""Read-only case evidence archive, with relative restore and independent checks.

This invocation is authorized for s382 and s641 only. No EDA, Git, source rewriting,
archive update, overwrite, or deletion is performed.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
from datetime import datetime, timezone
import argparse, hashlib, json, re, shutil, subprocess, sys, time

ROOT=Path.cwd().resolve()
BASE=ROOT/'experiments/20261016_r22_cut_ablation_v3'
EVIDENCE=ROOT/'project_docs/evidence/r22_cprime_v3_20261016'
LIB=ROOT/'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
VOLUME_BYTES=80*1024*1024
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def write(path,value):
    with Path(path).open('x',encoding='utf-8',newline='') as f:f.write(value)
def require(value,message):
    if not value:raise RuntimeError(message)
def relative(path):
    path=Path(path).absolute()
    require(path==path.resolve() and path.is_relative_to(ROOT),'Alias/outside repository: '+str(path))
    name=path.relative_to(ROOT).as_posix();p=PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and ':' not in name and '\n' not in name and '\r' not in name,'Unsafe restore path')
    return name
def inventory(paths):
    records={}
    for i,p in enumerate(sorted(paths),1):
        require(p.is_file() and not p.is_symlink(),'Not a regular source file: '+str(p))
        stat=p.stat();digest=sha(p);again=p.stat()
        require((stat.st_size,stat.st_mtime_ns)==(again.st_size,again.st_mtime_ns),'File changed while hashing')
        records[relative(p)]={'sha256':digest,'bytes':stat.st_size}
        if i%200==0:print(f'[hash] {i}/{len(paths)}',flush=True)
    return records
def run_tool(argv,out,timeout,phase,receipt):
    started=time.monotonic();entry={'phase':phase,'argv':argv,'cwd':str(ROOT),'timeout_s':timeout,
        'started_utc':datetime.now(timezone.utc).isoformat()};receipt['commands'].append(entry)
    with out.open('xb',buffering=0) as log:
        proc=subprocess.Popen(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        entry['pid']=proc.pid;last=0
        while proc.poll() is None:
            elapsed=time.monotonic()-started
            if elapsed>=timeout:
                proc.kill();proc.wait(timeout=15);entry.update(returncode=proc.returncode,timed_out=True,runtime_s=elapsed)
                raise TimeoutError(phase+' exceeded '+str(timeout)+'s')
            if elapsed-last>=10:
                print(f'[{phase}] {elapsed:.1f}s log_bytes={out.stat().st_size}',flush=True);last=elapsed
            time.sleep(.2)
    entry.update(returncode=proc.returncode,runtime_s=time.monotonic()-started,log=relative(out),log_sha256=sha(out))
    require(proc.returncode==0,f'{phase} failed rc={proc.returncode}; see {out}')
    print(f'[{phase}] finished rc=0 in {entry["runtime_s"]:.2f}s',flush=True)
def listing_files(path):
    blocks=[];block={}
    for line in path.read_text(encoding='utf-8-sig').splitlines()+['']:
        if ' = ' in line:
            k,v=line.split(' = ',1);block[k]=v
        elif not line.strip():
            if block:blocks.append(block);block={}
    files={}
    for b in blocks:
        if 'Path' not in b or 'Size' not in b or 'Type' in b:continue
        if b.get('Folder')=='+' or b.get('Attributes','').startswith('D'):continue
        name=b['Path'].replace('\\','/');p=PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and ':' not in name,'Absolute/traversal archive member')
        require(name not in files,'Duplicate archive member: '+name)
        files[name]=int(b['Size'])
    require(bool(files),'No archive members parsed')
    return files

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--circuit',choices=['s382','s641'],required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--audit',type=Path,default=EVIDENCE/'MATRIX_AUDIT_36.json')
    args=parser.parse_args();c=args.circuit;out=args.output_dir.resolve()
    require(out==EVIDENCE/'full_artifact_archives'/c,'Use the new dedicated case directory')
    require(not out.exists(),'Output exists; no update/overwrite/resume')
    tool=shutil.which('7z');require(tool is not None,'7z unavailable')
    manifest=read(BASE/'manifest.json');audit=read(args.audit);arms=manifest['arms']
    rows=[j for j in audit['jobs'] if j['circuit']==c]
    require(len(rows)==9 and {j['arm'] for j in rows}==set(arms),'Case is not independently accepted in all nine arms')
    require(sha(BASE/'manifest.json')==audit['manifest_sha256'],'Audit/manifest mismatch')
    for row in rows:require(sha(BASE/row['arm']/c/'completion.json')==row['completion_sha256'],'Completion drift: '+row['arm'])
    for name,digest in manifest['source_manifest'].items():require(sha(ROOT/name)==digest,'Registered production drift: '+name)
    require(sha(LIB)==manifest['lib_sha256'],'Registered Liberty changed')
    rtl=ROOT/'data/raw/benchmarks/raw/iscas89'/f'{c}.v'
    require(sha(rtl)==manifest['inputs'][c],'Registered RTL changed')
    roots=[BASE/arm/c for arm in arms]+[BASE/'inputs'/c]
    extras={BASE/'manifest.json',BASE/'preflight.json',args.audit.resolve(),LIB,rtl}
    extras.update(ROOT/p for p in manifest['source_manifest'])
    def collect():
        return extras|{p for directory in roots for p in directory.rglob('*') if p.is_file()}
    paths=collect();before=inventory(paths)
    out.mkdir(parents=True,exist_ok=False)
    # Capture the exact archiver used, without changing any original source.
    with (out/'archiver.py').open('xb') as f:f.write(Path(__file__).read_bytes())
    receipt={'schema':'r22-Cprime-case-solid7z-archive-v1','status':'in_progress','circuit':c,
        'created_utc':datetime.now(timezone.utc).isoformat(),'eda_executed':False,'source_modified':False,
        'authorized_case_scope':[c],'git_head_from_registered_manifest':manifest['git_head'],
        'matrix_audit_path':relative(args.audit),'matrix_audit_sha256':sha(args.audit),
        'actual_audit_case_counts':dict(Counter(j['circuit'] for j in audit['jobs'])),
        'case_arms':arms,'source_roots':[relative(p) for p in roots],
        'extra_source_paths':[relative(p) for p in sorted(extras)],'source_file_count':len(before),
        'source_bytes':sum(r['bytes'] for r in before.values()),'volume_limit_bytes':VOLUME_BYTES,
        'compression':{'container':'7z','method':'LZMA2','level':5,'solid':True,'dictionary':'32m','threads':2},
        'tool':{'path':tool,'launcher_sha256':sha(tool)},'archiver_sha256':sha(out/'archiver.py'),
        'adapted_from':{'path':'project_docs/evidence/r22_cprime_v3_20261016/full_artifact_archives/s27/archiver.py',
            'sha256':'528711d95d1779752aff4dc54f0c378e3bb17964baea985a76f42f02f8ab678e'},
        'commands':[],'outer_wrapper_timeout_s':900,'no_automatic_resume':True}
    shim=Path(tool).with_suffix('.shim')
    if shim.exists():
        body=shim.read_text(encoding='utf-8');target=re.search(r'^path = "(.+)"',body,re.M)
        receipt['tool'].update(shim_path=str(shim),shim_sha256=sha(shim))
        if target:
            receipt['tool'].update(binary_path=target.group(1),binary_sha256=sha(target.group(1)))
    save(out/'source_before.json',before)
    write(out/'files.list',''.join(name+'\n' for name in before))
    save(out/'preregistered_archive.json',receipt)
    try:
        run_tool([tool,'-h','-sccUTF-8'],out/'7z_help.log',30,'help-version',receipt)
        header=(out/'7z_help.log').read_text(encoding='utf-8-sig').splitlines()
        receipt['tool']['version']=next(line for line in header if line.startswith('7-Zip '))
        first=out/f'{c}_full_evidence.7z.001'
        command=[tool,'a','-t7z','-m0=LZMA2','-mx=5','-md=32m','-ms=on','-mmt=2','-v80m',
            '-sse','-ssp','-spd','-scsUTF-8','-sccUTF-8','-bb1','-bsp1',str(out/f'{c}_full_evidence.7z'),'@'+str(out/'files.list')]
        run_tool(command,out/'7z_create.log',600,'create-solid-80MiB-volumes',receipt)
        require(first.is_file(),'Expected first volume .001 missing')
        run_tool([tool,'l','-slt','-sccUTF-8',str(first)],out/'7z_listing.log',60,'list-members',receipt)
        members=listing_files(out/'7z_listing.log')
        require(members=={p:r['bytes'] for p,r in before.items()},'Archive member set/size differs')
        require('Solid = +' in (out/'7z_listing.log').read_text(encoding='utf-8-sig'),'Archive is not solid')
        save(out/'archive_members.json',members)
        run_tool([tool,'t','-sccUTF-8','-bsp1',str(first)],out/'7z_test.log',120,'test-integrity',receipt)
        require('Everything is Ok' in (out/'7z_test.log').read_text(encoding='utf-8-sig'),'7z t missing success assertion')
        restore=ROOT/'scratch'/(f'r22_cprime_restorecheck_{c}_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))
        restore.mkdir(exist_ok=False)
        run_tool([tool,'x','-sccUTF-8','-bsp1',str(first),'-o'+str(restore)],out/'7z_restore_check.log',120,'restore-new-scratch',receipt)
        restored={p.relative_to(restore).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in restore.rglob('*') if p.is_file()}
        require(restored==before,'Restored file set/SHA/size differs')
        save(out/'restore_check.json',{'restored_file_count':len(restored),'all_bytes_match':True,
             'scratch_root':relative(restore),'files':restored,'not_added_to_evidence_archive':True})
        after=inventory(collect());save(out/'source_after.json',after)
        require(after==before,'Original source set/SHA/size drift')
        require(sha(tool)==receipt['tool']['launcher_sha256'],'7z launcher drift')
        if 'binary_path' in receipt['tool']:require(sha(receipt['tool']['binary_path'])==receipt['tool']['binary_sha256'],'7z binary drift')
        volumes=sorted(out.glob(f'{c}_full_evidence.7z.*'),key=lambda p:int(p.suffix[1:]))
        require([int(p.suffix[1:]) for p in volumes]==list(range(1,len(volumes)+1)),'Missing archive volume')
        whole=hashlib.sha256();volume_records=[]
        for p in volumes:
            require(p.stat().st_size<=VOLUME_BYTES,'Volume exceeds 80MiB')
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):whole.update(chunk)
            volume_records.append({'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
        receipt.update(status='verified',source_stable=True,member_set_and_sizes_match=True,
            seven_zip_t_passed=True,restore_all_file_sha_size_match=True,restore_check_root=relative(restore),
            volumes=volume_records,archive_bytes=sum(p.stat().st_size for p in volumes),
            archive_whole_sha256=whole.hexdigest(),archive_whole_hash_definition='SHA256 of volume bytes concatenated in numeric suffix order; one volume equals its SHA',
            source_before_sha256=sha(out/'source_before.json'),source_after_sha256=sha(out/'source_after.json'),
            files_list_sha256=sha(out/'files.list'),archive_members_sha256=sha(out/'archive_members.json'),
            restored_manifest_sha256=sha(out/'restore_check.json'),completed_utc=datetime.now(timezone.utc).isoformat())
        write(out/'RESTORE.md',f'''# {c} full evidence solid 7z archive

This archive contains all files under the nine completed {c} jobs and inputs/{c},
the fixed manifest/preflight/frozen audit, the registered 44 runtime source files,
actual Liberty and {c} RTL. It is not an archive of the full 72-job matrix.
MATRIX_AUDIT_36 has actual distribution 9/9/8/9/1, not four complete circuits.

Keep every .7z.NNN volume together. Verify each size/SHA against receipt.json.
The whole-archive SHA is the SHA256 of concatenated volume bytes in numeric order.
Each volume is at most 80 MiB. Solid LZMA2 is deliberate; do not substitute ZIP.

Use a NEW empty restore directory, never an existing experiment checkout:

    7z t {c}_full_evidence.7z.001
    7z x {c}_full_evidence.7z.001 -o<NEW_RESTORE_REPOSITORY_ROOT>

Archive entries begin with repository-relative code/, data/, experiments/ or
project_docs/. No absolute drive prefix or traversal member is used. Restoration
does not require the original D: drive. Compare each extracted file SHA/size with
source_before.json; archive_members.json records exact member sizes. A full
independent scratch extraction was already compared byte-for-byte by SHA/size.

Historical Tcl/JSON argv may contain original absolute runtime paths. Those bytes
are evidence and were not rewritten; the archive is a portable byte restoration,
not permission or a claim that old EDA commands rerun without explicit rebinding.
Tool executables, WSL environment and external tool installation are not bundled.
No new STA/SEC/mapping was run. The original experiments were read only. Existing
outputs and archives are never overwritten/resumed. All creation/test/list/restore
commands, versions, bounded timeouts, logs and hashes are in receipt.json.
''')
        receipt['sidecar_hashes']={p.name:sha(p) for p in out.iterdir() if p.is_file() and not p.name.startswith(f'{c}_full_evidence.7z.')}
        save(out/'receipt.json',receipt)
        print(json.dumps({k:receipt[k] for k in ['status','source_file_count','source_bytes','archive_bytes','archive_whole_sha256','volumes','source_stable']},ensure_ascii=False,indent=2),flush=True)
    except Exception as error:
        receipt.update(status='failed',error_type=type(error).__name__,error=str(error))
        save(out/'failure.json',receipt)
        raise
if __name__=='__main__':main()
