# -*- coding: utf-8 -*-
"""Extend parasitic SPEF scan to 200um (reviewer Q4).
s382: 120/160/200 (existing 0-80); b18: 80/120/160/200 (existing 0-40)."""
import subprocess, json, time, os
from pathlib import Path

ROOT = Path(r'D:\BaiduSyncdisk\03_FAECO')
VENV = ROOT / '.venv' / 'Scripts' / 'python.exe'
CHECK = ROOT / 'scripts' / 'run_parasitic_aware_check.py'

CASES = {
    's382': {
        'baseline': ROOT / 'experiments' / '20260804_outerloop_decision' / 's382_beam1_early' / 's382' / 'mapped.v',
        'repaired': ROOT / 'experiments' / '20260804_outerloop_decision' / 's382_beam1_early' / 's382' / 'eval' / 'iter002_cand002' / '005__071__R' / 'mapped.v',
        'period': 0.5,
        'lengths': [120.0, 160.0, 200.0],
        'outdir': ROOT / 'experiments' / '20260805_parasitic_s382_scan',
    },
    'b18': {
        'baseline': ROOT / 'experiments' / '20260804_itc99_joint' / 'b18' / 'mapped.v',
        'repaired': ROOT / 'experiments' / '20260804_itc99_joint' / 'b18' / 'eval' / 'iter004_cand004' / '018_JOINT_JOINT' / 'mapped.v',
        'period': 13.15,
        'lengths': [80.0, 120.0, 160.0, 200.0],
        'outdir': ROOT / 'experiments' / '20260805_parasitic_b18_scan',
    },
}
logf = open(ROOT / 'experiments' / '20260806_spef_extend.log', 'w', encoding='utf-8')
def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(msg, flush=True)
    logf.write(msg + '\n'); logf.flush()

env = dict(os.environ); env['PYTHONPATH'] = 'src'
for cname, c in CASES.items():
    for L in c['lengths']:
        outd = c['outdir'] / ('u%d' % int(L))
        if (outd / 'summary.json').exists():
            log(cname, L, 'SKIP existing')
            continue
        cmd = [str(VENV), str(CHECK), '--baseline', str(c['baseline']), '--repaired', str(c['repaired']),
               '--period', str(c['period']), '--output-dir', str(outd), '--unit-len-um', str(L)]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=1800)
        ok = 'SKIP' if r.returncode == 0 and (outd / 'summary.json').exists() else r.returncode
        log(cname, L, 'rc', r.returncode, f"{time.time()-t0:.1f}s")
        if r.returncode != 0:
            log('  ERR', (r.stderr or '')[-400:])
log('SPEF_EXTEND_DONE')
logf.close()
