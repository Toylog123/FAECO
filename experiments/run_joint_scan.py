# -*- coding: utf-8 -*-
"""Run JOINT depth 1..5 scan for s382 (and later b15)."""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(r'D:\BaiduSyncdisk\03_FAECO')
VENV = ROOT / '.venv' / 'Scripts' / 'python.exe'
SCRIPT = ROOT / 'scripts' / 'run_outerloop_real_wns.py'
MAPPED_SRC = ROOT / 'experiments' / '20260805_tcad_sprint1_iscas89' / 's382' / 's382' / 'mapped.v'

OUT = ROOT / 'experiments' / '20260806_joint_depth_scan_s382'
OUT.mkdir(parents=True, exist_ok=True)

results = []
for depth in range(1, 6):
    d = OUT / ('depth%d' % depth)
    d.mkdir(parents=True, exist_ok=True)
    mapped = d / 'mapped.v'
    if not mapped.exists():
        mapped.write_bytes(MAPPED_SRC.read_bytes())
    t0 = time.time()
    cmd = [str(VENV), str(SCRIPT), '--circuit', 's382', '--period', '0.5',
           '--output-dir', str(d), '--skip-mapping', '--workers', '1',
           '--joint-enumerate-depth', str(depth), '--early-stop',
           '--max-iterations', '3']
    env = {'PYTHONPATH': 'src'}
    import os
    e = dict(os.environ); e['PYTHONPATH'] = 'src'
    r = subprocess.run(cmd, cwd=str(ROOT), env=e, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=3600)
    res = {'depth': depth, 'rc': r.returncode, 'elapsed_s': round(time.time()-t0, 1)}
    # 找结果 json
    for jf in d.rglob('*result*.json'):
        try:
            import json
            j = json.loads(jf.read_text(encoding='utf-8'))
            res['json'] = jf.name
            res['final_wns'] = j.get('final_wns') or j.get('final_worst_negative_slack')
            res['n_sta'] = j.get('n_candidate_sta_runs') or j.get('candidate_sta_count')
            break
        except Exception:
            pass
    if not res.get('final_wns'):
        res['tail'] = (r.stdout or '')[-300:] + (r.stderr or '')[-300:]
    results.append(res)
    print('depth', depth, 'rc', r.returncode, 'final_wns', res.get('final_wns'),
          'n_sta', res.get('n_sta'), f"{res['elapsed_s']}s", flush=True)

import json
(OUT / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print('SCAN_DONE')
