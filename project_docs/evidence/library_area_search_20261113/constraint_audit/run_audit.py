"""Two bounded read-only STA diagnostics, preserving every original output."""
import json
from pathlib import Path
import subprocess
import time
import hashlib

HERE = Path(__file__).resolve().parent
path = HERE/'MANIFEST.json'
data = json.loads(path.read_text())
if data['status'] != 'registered_before_STA':
    raise SystemExit('Refusing duplicate execution')
data['driver_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
for job in data['jobs']:
    out = HERE/job['label']
    assert hashlib.sha256((out/'coverage.tcl').read_bytes()).hexdigest() == job['tcl_sha256']
    script = '/mnt/d/'+(out/'coverage.tcl').resolve().as_posix()[3:]
    argv = ['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',script]
    start = time.monotonic()
    with (out/'stdout.log').open('xb') as stdout, (out/'stderr.log').open('xb') as stderr:
        try:
            rc = subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=job['timeout_s']).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    job.update(argv=argv,returncode=rc,elapsed_s=time.monotonic()-start)
    data['status']='running'
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    if rc or 'COVERAGE_END' not in (out/'stdout.log').read_text(errors='replace'):
        data['status']='halted_for_attribution'
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        raise SystemExit('Inspect failed diagnostic')
data['status']='two_STA_complete'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Two read-only constraint diagnostics complete')
