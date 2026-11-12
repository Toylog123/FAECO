"""Run every preregistered single compensation once, serially and bounded."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
plan=json.loads((HERE/'PLAN.json').read_text())
receipt=HERE/'BATCH_RECEIPT.json'
if receipt.exists():
    raise SystemExit('Existing batch receipt: inspect before resuming')
state={'driver_sha256':hashlib.sha256((HERE/'physical_probe.py').read_bytes()).hexdigest(),
       'plan_sha256':hashlib.sha256((HERE/'PLAN.json').read_bytes()).hexdigest(),'jobs':[]}
for arm in plan['singletons']:
    print('START',arm,flush=True)
    start=time.monotonic()
    logfile=HERE/f'{arm}.monitor.log'
    with logfile.open('xb') as log:
        try:
            p=subprocess.run([sys.executable,str(HERE/'physical_probe.py'),arm],stdout=log,stderr=subprocess.STDOUT,timeout=1530)
            rc=p.returncode
        except subprocess.TimeoutExpired:
            rc=124
    state['jobs'].append({'arm':arm,'returncode':rc,'elapsed_s':time.monotonic()-start})
    receipt.write_text(json.dumps(state,indent=2),encoding='utf-8')
    print('END',arm,'rc',rc,'seconds',state['jobs'][-1]['elapsed_s'],flush=True)
    if rc:
        raise SystemExit('Stopped for attribution; no blind retry')
