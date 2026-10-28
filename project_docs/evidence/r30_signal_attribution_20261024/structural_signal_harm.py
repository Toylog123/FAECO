"""THIRD ATTRIBUTION TEST: the harm label on ITC-99.

WHY THIS TEST IS THE DECISIVE ONE
---------------------------------
LOG-23/LOG-24 found a weak, cross-family-consistent signal in the GLOBAL size
features (depth / n_cells / n_ff / max_fanout / n_primary_*) for the
`resolvable` label (|delta| > band).  In ISCAS89 the same feature set predicts
the `harm` label (delta < -band) even STRONGER than it predicts `resolvable`
(0.684 vs 0.553 pooled).  That is the signature of a MAGNITUDE effect: the
feature set predicts how far the WNS will move, not which way it moves.

If the same asymmetry shows up on ITC-99, the honest reading of the whole
attribution series is:

    the graph-feature signal is a SCALE effect (how big is this design /
    how much will it move), not a TOPOLOGY effect (which candidate is good).

A topology effect would predict `gain` above 0.5 and `harm` below 0.5.
A magnitude effect predicts BOTH above 0.5.

This script reuses the previous harness unchanged (importing it also installs
its build_matrix monkey-patch, so the split and single-feature sets are
identical) and only adds the `harm` label mode on ITC-99, plus the
circuit-level ceiling for the harm label.

Everything else -- leave-one-circuit-out, ridge with the analytic LOO lambda
search, the pool bootstrap CI -- is the classifier tool's own code.
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
import structural_signal_attribution2 as attr2  # noqa: E402

OUT = REPO / 'scratch/structural_signal_harm.json'


def circuit_level_ceiling_harm(rows, band):
    """Same ceiling as attr2.circuit_level_ceiling, but for the harm label."""
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    y = np.array([1.0 if rpc.num(r.get(rpc.TARGET_COL['routed']), 0.0) < -band else 0.0
                  for r in sub])
    by_c = defaultdict(list)
    for i, r in enumerate(sub):
        by_c[r.get('circuit')].append(i)
    means = {c: float(y[idx].mean()) for c, idx in by_c.items()}
    preds = np.array([(sum(v for cc, v in means.items() if cc != r.get('circuit'))
                       / max(1, len(means) - 1)) for r in sub])
    a = rpc.auc(y, preds)
    return {
        'n': len(sub), 'n_positive': int(y.sum()),
        'n_circuits': len(by_c),
        'circuit_mean_label_spread': round(max(means.values()) - min(means.values()), 6),
        'pooled_auc_of_circuit_id': round(a, 6) if a is not None else None,
        'global_positive_rate': round(float(y.mean()), 6),
        'per_circuit_positive_rate': {c: round(float(y[idx].mean()), 6)
                                      for c, idx in sorted(by_c.items())},
    }


def main():
    rows, kinds, circuits = attr2.rows_joined()
    tpc = json.loads((attr2.FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    band_now = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    out = {
        'question': ('does the global-size feature set predict the harm label '
                     '(delta < -band) as strongly as it predicts resolvable '
                     '(|delta| > band)?  A magnitude effect predicts both; a '
                     'topology effect predicts gain up and harm down.'),
        'method': ('the previous harness is imported unchanged (which also '
                   'installs its build_matrix monkey-patch, so the feature sets '
                   'are identical); only the harm label mode is added'),
        'family': 'itc99',
        'classifier': {},
        'circuit_level_ceiling': {},
    }
    for tag, band in (('control', band_now), ('preview', attr2.BAND_PREVIEW)):
        res = attr2.run(rows, kinds, circuits, band, 'harm')
        cells = {}
        for fs, c in res['cells'].items():
            cells[fs] = {
                'pooled_auc': c.get('pooled_auc'),
                'ci95': c.get('ci95'),
                'mean_per_circuit_auc': c.get('mean_per_circuit_auc'),
                'mean_per_circuit_auc_ci95': c.get('mean_per_circuit_auc_ci95'),
                'per_circuit_auc': c.get('per_circuit_auc'),
            }
        out['classifier'][tag] = {'band_ns': band, 'n_positive': res['n_positive'],
                                  'powered': res['powered'], 'cells': cells}
        out['circuit_level_ceiling'][tag] = circuit_level_ceiling_harm(rows, band)

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

    lines = []
    lines.append('=== label harm  (band control %.6f -> preview %.6f) ==='
                 % (band_now, attr2.BAND_PREVIEW))
    ctl = out['classifier']['control']
    prv = out['classifier']['preview']
    lines.append('  positives: control %d (powered %s) / preview %d (powered %s)'
                 % (ctl['n_positive'], ctl['powered'], prv['n_positive'], prv['powered']))
    lines.append('  feature set            control pooled [CI]           preview pooled [CI]           preview per-circuit [CI]')
    for fs in ctl['cells']:
        a = ctl['cells'][fs]
        b = prv['cells'][fs]
        lines.append('  %-22s %s [%s, %s]  %s [%s, %s]  %s [%s, %s]'
                     % (fs, a['pooled_auc'], a['ci95'][0], a['ci95'][1],
                        b['pooled_auc'], b['ci95'][0], b['ci95'][1],
                        b['mean_per_circuit_auc'], b['mean_per_circuit_auc_ci95'][0],
                        b['mean_per_circuit_auc_ci95'][1]))
    for tag in ('control', 'preview'):
        cc = out['circuit_level_ceiling'][tag]
        lines.append('  CIRCUIT-LEVEL CEILING (%s): pooled AUC = %s ; spread %s'
                     % (tag, cc['pooled_auc_of_circuit_id'],
                        cc['circuit_mean_label_spread']))
    (REPO / 'scratch/structural_signal_harm.txt').write_text(
        '\n'.join(lines) + '\n', encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()
