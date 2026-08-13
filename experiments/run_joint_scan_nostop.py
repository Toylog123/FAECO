# -*- coding: utf-8 -*-
"""JOINT depth 1..5 scan for s382 (single full-enumeration iteration, no early-stop)."""
import subprocess, time, json, os
from pathlib import Path

ROOT = Path(r'D:\BaiduSyncdisk\03_FAECO')
VENV = ROOT / '.venv' / 'Scripts' / 'python.exe'
SCRIPT = ROOT / 'scripts' / 'run_outerloop_real_wns.py'
MAPPED_SRC = ROOT / 'experiments' / '20260805_tcad_sprint1_iscas89' / 's382' / 's382' / 'mapped.v'
OUT = ROOT / 'experiments' / '20260806_joint_depth_scan_s382_nostop'
OUT.mkdir(parents=True, exist_ok=True)
logf = open(ROOT / 'experiments' / '20260806_joint_scan_nostop.log', 'w', encoding='utf-8')

def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(msg, flush=True)
    logf.write(msg + '\n'); logf.flush()

def load_json(p):
    try:
        return json.loads(p.read_text(encoding='utf-8').rstrip())
    except Exception:
        return None

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
           '--joint-enumerate-depth', str(depth), '--max-iterations', '1',
           '--candidates-per-iteration', '8']
    env = dict(os.environ); env['PYTHONPATH'] = 'src'
    r = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=7200)
    res = {'depth': depth, 'rc': r.returncode, 'elapsed_s': round(time.time()-t0, 1)}
    rj = OUT / ('depth%d' % depth) / 's382' / 'outerloop_result.json'
    tj = OUT / ('depth%d' % depth) / 's382' / 'eval_trials.json'
    j = load_json(rj)
    if j is not None:
        res['baseline_wns'] = j.get('baseline_wns')
        wh = j.get('wns_history') or []
        res['best_wns'] = max(wh) if wh else None
        res['n_candidate_sta_runs'] = j.get('n_candidate_sta_runs')
        res['n_iterations'] = j.get('iterations')
    t = load_json(tj)
    if t is not None:
        trials = t.get('trials', [])
        res['n_joint_trials'] = sum(1 for x in trials if x.get('kind') == 'JOINT')
        res['n_r_trials'] = sum(1 for x in trials if x.get('kind') == 'R')
        res['n_g_trials'] = sum(1 for x in trials if x.get('kind') == 'G')
        res['n_b_trials'] = sum(1 for x in trials if x.get('kind') == 'B')
        acc = [x for x in trials if x.get('accepted')]
        res['accepted'] = [(a.get('instance'), a.get('kind'), a.get('wns')) for a in acc]
    results.append(res)
    log('depth', depth, 'rc', r.returncode, 'best', res.get('best_wns'),
        'n_sta', res.get('n_candidate_sta_runs'), 'joint', res.get('n_joint_trials'),
        'acc', res.get('accepted'), f"{res['elapsed_s']}s")
    if r.returncode != 0:
        log('  STDERR:', (r.stderr or '')[-800:])
log('SCAN_DONE')
(OUT / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
logf.close()
