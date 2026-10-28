"""BAND-PAIR SENSITIVITY: do the published band-thresholded verdicts survive
the fact that the three routing realisations give DIFFERENT bands?

WHY
---
LOG-28 measured three pairwise implementation bands on the same candidate
netlists:
    F0 vs F1  0.049753 ns   (the band every published verdict uses)
    F1 vs F2  0.045540 ns
    F0 vs F2  0.033706 ns   (max/min = 1.476087 -> NOT exchangeable)
So the "resolution band" is not one number: it depends on WHICH PAIR of
realisations is compared.  Every band-thresholded statement inherits that
choice.  The F0/F1 value -- the one used everywhere -- is the LARGEST of the
three, which makes the published thresholds the most CONSERVATIVE available.

This tool recomputes, for each of the three bands, the band-thresholded
quantities that the published conclusions rest on, and states explicitly which
of them flip:

  A  candidate-level label counts (resolvable / gain / harm)
  B  the classifier readouts: pooled AUC and mean within-pool AUC of the
     trivial baseline (kind_only) and of the scalar graph summaries
     (structural) -- both from the project's own tool, no re-implementation
  C  the acceptance selectivity: real gain / harm / inert rates of the
     accepted and the rejected set, and the enrichment ratios

Nothing here changes the main dataset or the family band definition: the
family band STAYS F0 vs F1 (the probe's own caveat).  This is a robustness
check of the published verdicts against the arbitrariness F2 exposed.

Usage:
  python tools/band_pair_sensitivity.py --family itc99
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve()
REPO = _HERE.parents[3] if _HERE.parent.name == 'tools' else _HERE.parents[1]
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))
import resolvable_positive_classifier as rpc  # noqa: E402
import acceptance_physical_selectivity as aps  # noqa: E402

BANDS = {
    'F0_vs_F1': 0.049753,
    'F1_vs_F2': 0.045540,
    'F0_vs_F2': 0.033706,
}
FAMILY_BAND_PAIR = 'F0_vs_F1'


def load_rows(fam):
    fam_dir = rpc.FAM_DIRS[fam]
    tt = [json.loads(l) for l in (fam_dir / 'training_table.jsonl')
          .read_text(encoding='utf-8').splitlines() if l.strip()]
    feats = rpc.load_ledger(rpc.LEDGERS[fam])
    struct = rpc.load_structural(fam_dir)
    out = []
    for r0 in tt:
        ckt = r0.get('circuit')
        f = feats.get((ckt, r0.get('trial_index')))
        s = struct.get((ckt, r0.get('key')))
        if f is None or s is None:
            continue
        if r0.get('ideal_delta_wns') is None:
            continue
        r = dict(r0)
        r.update(f)
        r.update({'sf_%s' % k: s.get(k) for k in rpc.STRUCT_ALL})
        out.append(r)
    kinds = sorted({r.get('kind') for r in out if r.get('kind')})
    circuits = sorted({r.get('circuit') for r in out})
    return out, kinds, circuits


def pool_metrics(rows, y, preds):
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    pooled = rpc.auc(y, preds)
    per_pool = []
    for idx in pool_idx.values():
        a = rpc.auc(y[idx], preds[idx])
        if a is not None:
            per_pool.append(a)
    rng = np.random.default_rng(rpc.SEED + 11)
    if len(per_pool) >= 2:
        arr = np.asarray(per_pool, dtype=float)
        out = np.empty(2000)
        for b in range(2000):
            out[b] = arr[rng.integers(0, len(arr), size=len(arr))].mean()
        lo, hi = np.percentile(out, [2.5, 97.5])
        wp, wlo, whi, wn = float(arr.mean()), float(lo), float(hi), len(arr)
    else:
        wp, wlo, whi, wn = None, None, None, len(per_pool)
    return {'pooled_auc': pooled, 'mean_within_pool_auc': wp,
            'mean_within_pool_auc_ci95': [wlo, whi], 'n_pools_used': wn}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='itc99')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    fam = args.family
    rows, kinds, circuits = load_rows(fam)
    col = rpc.TARGET_COL['routed']
    rows_full = [json.loads(l) for l in
                 (rpc.FAM_DIRS[fam] / 'training_table.jsonl')
                 .read_text(encoding='utf-8').splitlines() if l.strip()]

    out = {
        'family': fam,
        'bands_ns': BANDS,
        'family_band_pair': FAMILY_BAND_PAIR,
        'note': ('the family band DEFINITION stays F0 vs F1 -- the other pairs are '
                 'diagnostics and do not change any published verdict; this tool '
                 'only asks whether the published verdicts would SURVIVE the '
                 'other two bands'),
        'n_rows': len(rows),
        'cells': {},
    }

    for pair, band in BANDS.items():
        cell = {'band_ns': band, 'labels': {}, 'classifier': {}, 'acceptance': {}}
        # ---- A label counts
        for lm in ('resolvable', 'gain', 'harm'):
            y = rpc.evaluate('routed', rows, kinds, circuits, band,
                             np.random.default_rng(rpc.SEED), feature_sets=(),
                             label_mode=lm)
            cell['labels'][lm] = {'n_positive': y['n_positive'],
                                  'positive_rate': y['positive_rate'],
                                  'powered': y['powered']}
        # ---- B classifier readouts (project's own tool, LOCO ridge)
        for fs in ('kind_only', 'structural'):
            for lm in ('resolvable', 'gain', 'harm'):
                if lm == 'gain':
                    y = np.array([1.0 if rpc.num(r.get(col), -1e18) > band else 0.0
                                  for r in rows])
                elif lm == 'harm':
                    y = np.array([1.0 if rpc.num(r.get(col), 1e18) < -band else 0.0
                                  for r in rows])
                else:
                    y = np.array([1.0 if abs(rpc.num(r.get(col), -1e18)) > band else 0.0
                                  for r in rows])
                preds, _ = rpc.oof_predict(rows, kinds, circuits, y, fs, model='ridge')
                m = pool_metrics(rows, y, preds)
                m['n_positive'] = int(y.sum())
                cell['classifier'].setdefault(fs, {})[lm] = m
        # ---- C acceptance selectivity
        # The published acceptance numbers were computed on the FULL training
        # table (1207 rows), NOT on the 1117-row joined subset: the classifier
        # needs the ledger proxy features and the structural features, but the
        # acceptance criterion only needs `accepted_ideal` and the routed delta.
        # Using the joined subset here would shrink the rejected set and shift
        # the enrichment ratios, so the reference band pair has to reproduce the
        # published numbers exactly.
        acc = [r for r in rows_full if aps.is_accepted(r) and r.get(col) is not None]
        rej = [r for r in rows_full if not aps.is_accepted(r) and r.get(col) is not None]
        am = aps.mix(acc, col, band)
        rm = aps.mix(rej, col, band)
        cell['acceptance'] = {
            'n_accepted': len(acc), 'n_rejected': len(rej),
            'accepted': {k: am.get(k) for k in
                         ('real_gain_rate', 'real_harm_rate', 'inert_rate',
                          'real_gain', 'real_harm', 'inert')},
            'rejected': {k: rm.get(k) for k in
                         ('real_gain_rate', 'real_harm_rate', 'inert_rate',
                          'real_gain', 'real_harm', 'inert')},
            'gain_enrichment': (round(am['real_gain_rate'] / rm['real_gain_rate'], 4)
                                if rm['real_gain_rate'] else None),
            'harm_ratio': (round(am['real_harm_rate'] / rm['real_harm_rate'], 4)
                           if rm['real_harm_rate'] else None),
        }
        out['cells'][pair] = cell

    # ---- which published statements flip?
    ref = out['cells'][FAMILY_BAND_PAIR]
    flips = []

    def note(kind, name, ref_v, other_v, tol=0.0, higher_is_stronger=True):
        if ref_v is None or other_v is None:
            flips.append({'kind': kind, 'name': name, 'reference': ref_v,
                          'other': other_v, 'flips': None})
            return
        f = (other_v > ref_v) if higher_is_stronger else (other_v < ref_v)
        flips.append({'kind': kind, 'name': name, 'reference': ref_v,
                      'other': other_v, 'flips': bool(f and abs(other_v - ref_v) > tol)})

    for pair in BANDS:
        if pair == FAMILY_BAND_PAIR:
            continue
        c = out['cells'][pair]
        note('label_count', 'resolvable_positives',
             ref['labels']['resolvable']['n_positive'],
             c['labels']['resolvable']['n_positive'])
        note('classifier', 'kind_only_pooled_auc(resolvable)',
             ref['classifier']['kind_only']['resolvable']['pooled_auc'],
             c['classifier']['kind_only']['resolvable']['pooled_auc'])
        note('classifier', 'structural_within_pool_auc(resolvable)',
             ref['classifier']['structural']['resolvable']['mean_within_pool_auc'],
             c['classifier']['structural']['resolvable']['mean_within_pool_auc'])
        note('classifier', 'structural_pooled_auc(resolvable)',
             ref['classifier']['structural']['resolvable']['pooled_auc'],
             c['classifier']['structural']['resolvable']['pooled_auc'])
        note('acceptance', 'accepted_real_gain_rate',
             ref['acceptance']['accepted']['real_gain_rate'],
             c['acceptance']['accepted']['real_gain_rate'])
        note('acceptance', 'accepted_inert_rate',
             ref['acceptance']['accepted']['inert_rate'],
             c['acceptance']['accepted']['inert_rate'],
             higher_is_stronger=False)
        note('acceptance', 'gain_enrichment',
             ref['acceptance']['gain_enrichment'],
             c['acceptance']['gain_enrichment'])
        note('acceptance', 'harm_ratio',
             ref['acceptance']['harm_ratio'],
             c['acceptance']['harm_ratio'], higher_is_stronger=False)
    out['flip_table'] = flips

    dest = Path(args.out) if args.out else REPO / 'scratch/band_pair_sensitivity.json'
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

    L = []
    L.append('band-pair sensitivity (family %s, %d rows)' % (fam, len(rows)))
    L.append('reference pair (the family band definition): %s = %.6f ns'
             % (FAMILY_BAND_PAIR, BANDS[FAMILY_BAND_PAIR]))
    L.append('')
    L.append('%-8s %-10s | %-28s | %-28s | %-28s'
             % ('pair', 'band', 'labels(res/gain/harm)',
                'classifier(kind_only/struct)', 'acceptance(acc gain/inert)'))
    for pair, band in BANDS.items():
        c = out['cells'][pair]
        lab = '%d/%d/%d' % (c['labels']['resolvable']['n_positive'],
                            c['labels']['gain']['n_positive'],
                            c['labels']['harm']['n_positive'])
        cl = '%.4f/%.4f' % (c['classifier']['kind_only']['resolvable']['pooled_auc'],
                            c['classifier']['structural']['resolvable']['pooled_auc'])
        wp = c['classifier']['structural']['resolvable']['mean_within_pool_auc']
        ac = '%.4f/%.4f' % (c['acceptance']['accepted']['real_gain_rate'],
                            c['acceptance']['accepted']['inert_rate'])
        L.append('%-8s %.6f | %-28s | %-28s | %-28s  within-pool(struct)=%s'
                 % (pair, band, lab, cl, ac,
                    ('%.6f' % wp) if wp is not None else '-'))
    L.append('')
    L.append('flip table (vs the family band pair):')
    for f in flips:
        L.append('  %-14s %-42s ref=%s other=%s flips=%s'
                 % (f['kind'], f['name'], f['reference'], f['other'], f['flips']))
    (REPO / 'scratch/band_pair_sensitivity.txt').write_text('\n'.join(L) + '\n',
                                                               encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
