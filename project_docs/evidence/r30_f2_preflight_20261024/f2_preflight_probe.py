"""PRE-FLIGHT (v2) for the three-implementation comparison.

WHAT v1 GOT WRONG (and why this file exists)
---------------------------------------------
The first fixture built the synthetic F2 as "the real I1 rows plus noise".  That
makes F2 SHARE the I1 realisation's noise (F2 = I1 + eps), so the three
realisations are NOT exchangeable: Var(d_F1F2) = sigma_r^2 instead of
2 sigma_r^2, and Var(d_F0F2) = 3 sigma_r^2.  The fixture duly reported a
max/min band ratio of 1.70 -- a correct consequence of a badly built mock, not
a property of the measurement.  Interpreting the real F2 with that expectation
would have been wrong.

The fact that the three pairwise differences are algebraically dependent
(d_F0F2 = d_F0F1 + d_F1F2) is exactly why a mock built from two realisations
cannot be exchangeable: you cannot synthesise a third exchangeable realisation
from two.

SO: the fixture is now built from scratch on all three sides.

THE THREE CASES
---------------
A. real F0/F1, no F2 file
   -> the guard must refuse the three-way path, and the F0-F1 band must
      reproduce the FINALISED band (0.049752 ns stored).
B. FULLY SYNTHETIC exchangeable triple (common signal + iid realisation noise)
   -> the three pairwise bands must AGREE (max/min near 1.0), because every
      pairwise difference has the same variance; and the three-way comparison
      must show the averaged-label picker beating the single-measurement picker
      (averaging two realisations halves the noise), which is the ground truth
      the real run is tested against.
C. real F0/F1 + a CORRELATED mock F2 (F2 = F1 + noise)
   -> kept as the contrast case: a non-exchangeable third side shows up as a
      max/min ratio far from 1.0, so the real result can be classified as
      "exchangeable" or "one pair is special" with a criterion, not a vibe.

Nothing here touches the repository's artefacts: the probe is pointed at
sandbox directories and writes there.
"""
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
FAM = REPO / 'experiments/20261024_physical_labels_itc99'
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
ROOT = REPO / 'scratch/f2_probe_fixture'
SEED = 20261024

LINES = []


def A(s=''):
    LINES.append(s)


def dataset_rows():
    return [json.loads(l) for l
            in (FAM / 'physical_dataset.jsonl').read_text(encoding='utf-8').splitlines()
            if l.strip()]


def measured():
    cln = json.loads((FAM / 'candidate_level_noise.json').read_text(encoding='utf-8'))
    sd = cln.get('pooled_within_circuit_sd_ns')
    per = cln.get('per_circuit') or {}
    offsets = {c: d.get('systematic_offset_ns') or 0.0 for c, d in per.items()}
    return sd, offsets


def fresh_dir(name):
    d = ROOT / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for t in ('jobs_itc99.tsv', 'jobs_itc99_f1.tsv', 'jobs_itc99_f2.tsv'):
        shutil.copy2(FAM / t, d / t)
    return d


def write_jsonl(path, recs):
    with path.open('w', encoding='utf-8', newline='\n') as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')


def run_probe(sandbox):
    sys.modules.pop('impl_stability_probe', None)
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    import impl_stability_probe as p  # noqa: E402
    p.FAM_DIRS = dict(p.FAM_DIRS)
    p.FAM_DIRS['itc99'] = sandbox
    old = sys.argv
    sys.argv = ['impl_stability_probe.py', '--family', 'itc99']
    try:
        p.main()
    finally:
        sys.argv = old
    return json.loads((sandbox / 'impl_stability.json').read_text(encoding='utf-8'))


def summarise(tag, res):
    A('--- %s ---' % tag)
    meta = res.get('meta') or {}
    A('  third present=%s complete=%s f2 rows=%s'
      % (meta.get('has_third_realisation'), meta.get('third_realisation_complete'),
         meta.get('n_f2_rows')))
    for k, v in (res.get('bands_by_pair') or {}).items():
        A('    %-10s scope=%-8s 2sigma=%-10s df=%-6s pairs=%-6s circuits=%s'
          % (k, v.get('scope'), v.get('two_sigma_ns'), v.get('df'),
             v.get('n_candidate_netlists'), v.get('n_circuits')))
    bs = res.get('band_stability') or {}
    A('    band stability max/min = %s' % bs.get('max_over_min_ratio'))
    tw = res.get('three_way_choice') or {}
    if 'per_direction' in tw:
        for h, e in tw['per_direction'].items():
            A('    hold out %-4s: %d pools | regret single %.5f | regret avg %.5f'
              ' | avg better %d / ties %d / single better %d | p=%s'
              % (h, e.get('n_pools'), e.get('regret_single_measurement_ns'),
                 e.get('regret_averaged_label_ns'), e.get('averaged_better_pools'),
                 e.get('ties'), e.get('single_better_pools'), e.get('exact_binomial_p')))
        o = tw.get('overall') or {}
        A('    OVERALL: %d pool-direction pairs | avg better %d / ties %d / single better %d'
          ' | p=%s' % (o.get('n_pool_direction_pairs'), o.get('averaged_better'),
                       o.get('ties'), o.get('single_better'), o.get('exact_binomial_p')))
    else:
        A('    THREE-WAY: %s' % tw.get('note'))


def case_a(rows, sd):
    d = fresh_dir('A_no_f2')
    write_jsonl(d / 'physical_dataset.jsonl', rows)
    res = run_probe(d)
    A('CASE A -- real F0/F1, no F2 file (the guard)')
    summarise('A', res)
    A('')
    return res


def case_b(rows, sd, offsets):
    """Fully synthetic exchangeable triple."""
    d = fresh_dir('B_exchangeable')
    rng = np.random.default_rng(SEED)
    sigma_r = sd / math.sqrt(2.0)
    by_key = {}
    for r in rows:
        if r.get('batch') == 'I1' and r.get('post_status') == 'ok':
            by_key[r.get('key')] = r
    noise = {}
    for name in ('I0', 'I1', 'I2'):
        noise[name] = {k: float(rng.normal(0.0, sigma_r)) for k in by_key}
    # the common signal: the real I1 WNS, minus the realisation noise it carries
    out_rows = []
    for r in rows:
        if r.get('batch') not in ('I0', 'I1'):
            continue
        b = r.get('batch')
        k = r.get('key')
        if k not in by_key:
            continue
        sig = by_key[k]['post_wns']
        out_rows.append({
            'batch': b, 'key': k, 'circuit': r.get('circuit'),
            'kind': r.get('kind'), 'iteration': r.get('iteration'),
            'trial_index': r.get('trial_index'),
            'post_status': 'ok',
            'post_wns': round(sig + noise[b][k] - noise['I1'][k], 2),
            'MOCK': True,
        })
    f2 = []
    for k, r in by_key.items():
        sig = r['post_wns']
        f2.append({
            'batch': 'I2', 'key': k, 'circuit': r.get('circuit'),
            'kind': r.get('kind'), 'iteration': r.get('iteration'),
            'trial_index': r.get('trial_index'),
            'post_status': 'ok',
            'post_wns': round(sig + noise['I2'][k] - noise['I1'][k], 2),
            'MOCK': True,
        })
    write_jsonl(d / 'physical_dataset.jsonl', out_rows)
    write_jsonl(d / 'f2_labels.jsonl', f2)
    res = run_probe(d)
    A('CASE B -- FULLY SYNTHETIC exchangeable triple (sigma_r = %.6f ns)' % sigma_r)
    A('  ground truth: the three pairwise bands must AGREE, and the averaged-label')
    A('  picker must beat the single-measurement picker (averaging halves the noise)')
    summarise('B', res)
    A('')
    return res


def case_c(rows, sd, offsets):
    """Real F0/F1 + a CORRELATED mock F2 (F2 = I1 + noise) -- the contrast case."""
    d = fresh_dir('C_correlated')
    rng = np.random.default_rng(SEED + 1)
    sigma_r = sd / math.sqrt(2.0)
    write_jsonl(d / 'physical_dataset.jsonl', rows)
    i1 = [r for r in rows if r.get('batch') == 'I1' and r.get('post_status') == 'ok']
    f2 = []
    for r in i1:
        f2.append({
            'batch': 'I2', 'key': r.get('key'), 'circuit': r.get('circuit'),
            'kind': r.get('kind'), 'iteration': r.get('iteration'),
            'trial_index': r.get('trial_index'),
            'post_status': 'ok',
            'post_wns': round(r['post_wns'] + float(rng.normal(0.0, sigma_r)), 2),
            'MOCK': True,
        })
    write_jsonl(d / 'f2_labels.jsonl', f2)
    res = run_probe(d)
    A('CASE C -- real F0/F1 + CORRELATED mock F2 (F2 = I1 + noise; NOT exchangeable)')
    A('  expected: the F1-F2 band comes out too tight and the F0-F2 band too wide,')
    A('  so the max/min ratio is far from 1 -- the machinery can SEE a special pair')
    summarise('C', res)
    A('')
    return res


def main():
    rows = dataset_rows()
    sd, offsets = measured()
    A('F2 pre-flight v2 -- three-implementation code path on fixtures')
    A('measured F0-F1 pooled within-circuit sd = %s ns' % sd)
    A('per-realisation sigma_r = %s ns' % (sd / math.sqrt(2.0)))
    A('')

    a = case_a(rows, sd)
    b = case_b(rows, sd, offsets)
    c = case_c(rows, sd, offsets)

    A('VERDICT')
    band_a = ((a.get('bands_by_pair') or {}).get('F0_vs_F1') or {}).get('two_sigma_ns')
    A('  A: F0-F1 band from the probe = %s ns (the finalised band stores 0.049752 ns;'
      % band_a)
    A('     the 1e-6 difference is the tool\'s documented rounding convention)')
    ratio_b = (b.get('band_stability') or {}).get('max_over_min_ratio')
    ratio_c = (c.get('band_stability') or {}).get('max_over_min_ratio')
    tw_b = b.get('three_way_choice') or {}
    pools_b = sum(e.get('n_pools', 0) for e in (tw_b.get('per_direction') or {}).values())
    ov_b = tw_b.get('overall') or {}
    A('  B: exchangeable fixture -> max/min = %s (expected ~1.0), pools = %d,'
      % (ratio_b, pools_b))
    A('     averaged better %s / ties %s / single better %s, p=%s'
      % (ov_b.get('averaged_better'), ov_b.get('ties'), ov_b.get('single_better'),
         ov_b.get('exact_binomial_p')))
    A('  C: correlated fixture -> max/min = %s (expected far from 1.0)' % ratio_c)
    checks = {
        'A reproduces the finalised band': band_a is not None and abs(band_a - 0.049752) < 2e-6,
        'A refuses the three-way path without F2': 'per_direction' not in (a.get('three_way_choice') or {}),
        'B three-way path runs (pools > 0)': pools_b > 0,
        'B exchangeable bands agree (max/min < 1.15)': ratio_b is not None and ratio_b < 1.15,
        'B averaging beats single measurement': (ov_b.get('averaged_better') or 0) > (ov_b.get('single_better') or 0),
        'C a correlated third side is visible (max/min > 1.3)': ratio_c is not None and ratio_c > 1.3,
    }
    A('')
    for k, v in checks.items():
        A('  [%s] %s' % ('PASS' if v else 'FAIL', k))
    A('')
    A('  PRE-FLIGHT %s' % ('PASSED' if all(checks.values()) else 'NEEDS ATTENTION'))
    (REPO / 'scratch/f2_preflight_probe.txt').write_text('\n'.join(LINES) + '\n',
                                                        encoding='utf-8')


if __name__ == '__main__':
    main()
