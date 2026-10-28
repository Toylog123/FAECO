"""POOL-LEVEL vs CANDIDATE-LEVEL decomposition of the structural signal.

WHY THIS IS THE DECISIVE TEST
-----------------------------
The attribution series (LOG-20261024-24) found a weak but repeatable signal in
a single gate-level scalar (`depth`) for the `resolvable` label: per-circuit
AUC ~0.60 on ITC-99 and ~0.58 on ISCAS89.  Before that can be reported as
"graph structure carries a usable physical signal", one question has to be
answered:

    is the signal WITHIN a candidate pool (one circuit, one ECO iteration), or
    BETWEEN pools / between circuits?

The reason it matters: the use case is a candidate generator that has to decide
*which candidate of the pool it is currently looking at* deserves an expensive
post-route STA run.  A signal that separates POOL A from POOL B is useless for
that decision -- it says "this iteration is worth measuring", not "this
candidate is worth measuring".  And the depth of a candidate netlist is almost
a per-circuit constant (the candidate is the iteration base plus a few cells),
so the between-pool reading is the plausible one.

THE DECOMPOSITION
-----------------
Using the SAME out-of-fold predictions as the classifier tool (leave-one-
circuit-out, so the held-out circuit is never seen in training):

  pooled AUC                 all rows at once (the headline number everywhere)
  pool-mean-only pooled AUC  every candidate of a pool gets the pool's mean
                             prediction -> only the BETWEEN-pool component
                             survives
  mean within-pool AUC       the average of the per-pool AUCs (pools with a
                             single class are skipped) -> the WITHIN-pool
                             component a candidate generator can use
  mean within-pool AUC of    the same, but ranking by the RAW feature instead
  the raw feature             of the model

If the headline pooled AUC is carried by the between-pool component, then
"the graph features predict the physical outcome" is true only in the weak
sense "some iterations move more than others", and the candidate-level claim
must not be made.

Everything here is the classifier tool's own code (oof_predict, auc) plus a
bootstrap over pools, the same unit of independence the tool uses.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / 'scratch'))

import resolvable_positive_classifier as rpc  # noqa: E402
import structural_signal_crossfamily as xfam  # noqa: E402

OUT = REPO / 'scratch/pool_level_decomposition.json'
RAW_FEATURE = {'one_depth': 'depth', 'one_n_cells': 'n_cells',
               'one_max_fanout': 'max_fanout', 'one_n_ff': 'n_ff'}
FEATURE_SETS = ('one_depth', 'one_n_cells', 'one_max_fanout', 'one_n_ff',
                 'struct_global_only', 'struct_local_only', 'struct_delta_only',
                 'structural', 'kind_only')


def label_vector(rows, band, label_mode):
    col = rpc.TARGET_COL['routed']
    if label_mode == 'gain':
        return np.array([1.0 if rpc.num(r.get(col), -1e18) > band else 0.0 for r in rows])
    if label_mode == 'harm':
        return np.array([1.0 if rpc.num(r.get(col), 1e18) < -band else 0.0 for r in rows])
    return np.array([1.0 if abs(rpc.num(r.get(col), -1e18)) > band else 0.0 for r in rows])


def boot_mean_ci(values, reps=2000, seed=rpc.SEED + 11):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return (float(np.mean(vals)) if vals else None), None, None, len(vals)
    arr = np.asarray(vals, dtype=float)
    rng = np.random.default_rng(seed)
    out = np.empty(reps, dtype=float)
    n = len(arr)
    for b in range(reps):
        out[b] = arr[rng.integers(0, n, size=n)].mean()
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(arr.mean()), float(lo), float(hi), n


def decompose(rows, kinds, circuits, band, label_mode):
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    y = label_vector(sub, band, label_mode)
    pool_idx = defaultdict(list)
    for i, r in enumerate(sub):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    pools = list(pool_idx.values())
    out = {
        'band_ns': band, 'label_mode': label_mode, 'n_rows': len(sub),
        'n_positive': int(y.sum()),
        'n_pools': len(pools),
        'n_pools_with_both_classes': 0,
        'cells': {},
    }
    for fs in FEATURE_SETS:
        preds, _ = rpc.oof_predict(sub, kinds, circuits, y, fs, model='ridge')
        pooled = rpc.auc(y, preds)
        # the between-pool component: every candidate gets its pool's mean score
        pm = np.zeros(len(sub))
        for idx in pools:
            pm[idx] = float(preds[idx].mean())
        pooled_poolmean = rpc.auc(y, pm)
        # the within-pool component
        per_pool = []
        for idx in pools:
            a = rpc.auc(y[idx], preds[idx])
            if a is not None:
                per_pool.append(a)
        wp_mean, wp_lo, wp_hi, wp_n = boot_mean_ci(per_pool)
        # the same, ranking by the raw feature
        raw = None
        if fs in RAW_FEATURE:
            key = 'sf_%s' % RAW_FEATURE[fs]
            raw_vals = np.array([rpc.num(r.get(key)) for r in sub], dtype=float)
            per_pool_raw = []
            for idx in pools:
                a = rpc.auc(y[idx], raw_vals[idx])
                if a is not None:
                    per_pool_raw.append(a)
            rw_mean, rw_lo, rw_hi, rw_n = boot_mean_ci(per_pool_raw)
            raw = {'mean_within_pool_auc': rw_mean, 'ci95': [rw_lo, rw_hi],
                   'n_pools_used': rw_n}
        out['n_pools_with_both_classes'] = max(out['n_pools_with_both_classes'], wp_n)
        out['cells'][fs] = {
            'pooled_auc': pooled,
            'pooled_auc_pool_mean_only': pooled_poolmean,
            'mean_within_pool_auc': wp_mean,
            'mean_within_pool_auc_ci95': [wp_lo, wp_hi],
            'n_pools_used': wp_n,
            'raw_feature': raw,
        }
    return out


def main():
    out = {
        'question': ('is the structural signal within a candidate POOL (usable by a '
                     'candidate generator) or between pools / circuits (not usable)?'),
        'method': ('the classifier tool\'s own out-of-fold predictions (leave-one-'
                   'circuit-out) are decomposed into the between-pool component (the '
                   'pool-mean predictor) and the within-pool component (the mean of the '
                   'per-pool AUCs, bootstrap over pools)'),
        'families': {},
    }
    for fam in ('itc99', 'iscas89'):
        fam_dir = rpc.FAM_DIRS[fam]
        tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
        band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
        rows, kinds, circuits = xfam.rows_joined(fam)
        out['families'][fam] = {
            'band_ns': band,
            'labels': {lm: decompose(rows, kinds, circuits, band, lm)
                       for lm in ('resolvable', 'harm', 'gain')},
        }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

    lines = []
    for fam, fd in out['families'].items():
        lines.append('########## %s (band %.6f ns) ##########' % (fam, fd['band_ns']))
        for lm, ld in fd['labels'].items():
            lines.append('=== %s (positives %d, pools %d, pools with both classes %d) ==='
                         % (lm, ld['n_positive'], ld['n_pools'],
                            ld['n_pools_with_both_classes']))
            lines.append('  feature set            pooled      pool-mean-only   '
                         'mean within-pool [CI]')
            for fs, c in ld['cells'].items():
                ci = c['mean_within_pool_auc_ci95']
                lines.append('  %-22s %-11s %-16s %s [%s, %s] (n=%s)'
                             % (fs, ('%.6f' % c['pooled_auc']) if c['pooled_auc'] is not None else '-',
                                ('%.6f' % c['pooled_auc_pool_mean_only'])
                                if c['pooled_auc_pool_mean_only'] is not None else '-',
                                ('%.6f' % c['mean_within_pool_auc'])
                                if c['mean_within_pool_auc'] is not None else '-',
                                ('%.4f' % ci[0]) if ci else '-', ('%.4f' % ci[1]) if ci else '-',
                                c['n_pools_used']))
            lines.append('')
    (REPO / 'scratch/pool_level_decomposition.txt').write_text(
        '\n'.join(lines) + '\n', encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()
