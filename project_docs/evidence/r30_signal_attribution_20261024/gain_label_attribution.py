"""ATTRIBUTION TEST: where does the GAIN-label signal of the graph features
come from?

LOG-20261024-23 found that, with the narrower full-family band, the
`structural` feature set reaches AUC 0.661449 on the `gain` label (it was
0.226244 with the pilot band).  Before that is read as "the graph features CAN
predict a real physical gain -- the GNN route is not dead", it has to be
attributed, because the `structural` set is a mixture of three different things:

  * STRUCT_LOCAL   the local topology of the candidate (module cone, depth ...)
  * STRUCT_GLOBAL  the global size of the candidate's netlist
  * STRUCT_DELTA   d_depth / d_n_cells / d_max_fanout -- HOW MUCH the candidate
                   changed relative to its iteration base

STRUCT_DELTA is not graph structure and it is not obviously causal: FAECO
accepts the candidate with the best ideal-net delta, and a bigger structural
change tends to produce a bigger ideal-net delta, so the change magnitude is a
**proxy for "this candidate was the accepted one"** -- and the accepted ones are
the ones with a real gain.  If the signal lives in STRUCT_DELTA, then the
0.661 is a magnitude/selection artefact, not "graph structure predicts gain".

The test therefore splits `structural` into its parts and re-runs the tool's own
evaluation on each part, with the tool's own feature builder monkey-patched to
support the split sets (nothing else in the tool changes, and no statistic is
re-implemented).

Bands: the pilot band (in force) and the full-family preview band, both from
the same training table.
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))

import resolvable_positive_classifier as rpc  # noqa: E402

FAM = 'itc99'
FAM_DIR = rpc.FAM_DIRS[FAM]
OUT = REPO / 'scratch/gain_label_attribution.json'
def _band_from_artefact():
    """The routed candidate-level band, read back from the stored artefact."""
    tpc = json.loads((FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    return (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')


BAND_PREVIEW = _band_from_artefact()
BAND_PREVIEW_BEFORE_FINALISATION = 0.050419  # the value the LOG-23 preview used

SPLITS = {
    'struct_local_only': rpc.STRUCT_LOCAL,
    'struct_global_only': rpc.STRUCT_GLOBAL,
    'struct_delta_only': rpc.STRUCT_DELTA,
    'struct_topo_no_delta': rpc.STRUCT_LOCAL + rpc.STRUCT_GLOBAL,
}
CUSTOM_SETS = ('kind_only', 'structural',) + tuple(SPLITS.keys())

_orig_build = rpc.build_matrix


def patched_build(rows, feature_set, kinds):
    """The tool's own builder, plus the split sets."""
    if feature_set not in SPLITS:
        return _orig_build(rows, feature_set, kinds)
    cols, names = [], []
    for k in SPLITS[feature_set]:
        cols.append([rpc.num(r.get('sf_%s' % k)) for r in rows])
        names.append(k)
    for k in kinds:
        cols.append([1.0 if r.get('kind') == k else 0.0 for r in rows])
        names.append('kind_%s' % k)
    cols.append([float(rpc.num(r.get('iteration'))) for r in rows])
    names.append('iteration')
    return np.array(cols, dtype=float).T, names


rpc.build_matrix = patched_build


def rows_joined():
    tt = FAM_DIR / 'training_table.jsonl'
    rows_all = [json.loads(l) for l in tt.read_text(encoding='utf-8').splitlines() if l.strip()]
    feats = rpc.load_ledger(rpc.LEDGERS[FAM])
    struct = rpc.load_structural(FAM_DIR)
    out = []
    for r0 in rows_all:
        ckt = r0.get('circuit')
        f = feats.get((ckt, r0.get('trial_index')))
        if f is None:
            continue
        s = struct.get((ckt, r0.get('key')))
        if s is None:
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


def run(rows, kinds, circuits, band, label_mode):
    rng = np.random.default_rng(rpc.SEED)
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    res = rpc.evaluate('routed', sub, kinds, circuits, band, rng,
                       feature_sets=CUSTOM_SETS, label_mode=label_mode)
    cells = {}
    for fs, c in res['cells'].items():
        b = (c.get('budget_recall') or {}).get('0.25') or {}
        cells[fs] = {
            'pooled_auc': c.get('pooled_auc'),
            'ci95': c.get('pooled_auc_ci95'),
            'n_features': len(c.get('dropped_columns') or {}) or None,
            'recall_at_25pct': b.get('mean_recall_model'),
        }
    return {'band_ns': band, 'n_positive': res['n_positive'],
            'powered': res['powered'], 'cells': cells}


def mechanism(rows, band, label_mode):
    """Direct evidence for the proxy mechanism: how do the change magnitude and
    the acceptance flag relate to the label?"""
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    thr = band
    y = np.array([1.0 if (rpc.num(r.get(rpc.TARGET_COL['routed']), 0.0) > thr
                          if label_mode == 'gain'
                          else abs(rpc.num(r.get(rpc.TARGET_COL['routed']), 0.0)) > thr)
                  else 0.0 for r in sub])
    out = {'n': len(sub), 'n_positive': int(y.sum())}
    for feat in ('d_depth', 'd_n_cells', 'd_max_fanout'):
        v = np.array([rpc.num(r.get('sf_%s' % feat)) for r in sub], dtype=float)
        if v.std() == 0:
            continue
        # point-biserial correlation between the feature and the label
        r_pb = float(np.corrcoef(v, y)[0, 1])
        pos, neg = v[y == 1], v[y == 0]
        out[feat] = {
            'corr_with_label': round(r_pb, 6),
            'mean_when_positive': round(float(pos.mean()), 6) if pos.size else None,
            'mean_when_negative': round(float(neg.mean()), 6) if neg.size else None,
        }
    acc = np.array([1.0 if r.get('accepted_ideal') else 0.0 for r in sub])
    if acc.std() > 0:
        out['accepted_ideal_corr_with_label'] = round(float(np.corrcoef(acc, y)[0, 1]), 6)
        out['accepted_ideal_share_among_positives'] = round(
            float(acc[y == 1].mean()), 6) if (y == 1).sum() else None
        out['accepted_ideal_share_among_negatives'] = round(
            float(acc[y == 0].mean()), 6) if (y == 0).sum() else None
    return out


def main():
    rows, kinds, circuits = rows_joined()
    tpc = json.loads((FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    band_now = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    out = {
        'question': ('LOG-23 found structural AUC 0.661449 on the GAIN label with the '
                     'narrower band. Is that graph STRUCTURE, or the change magnitude '
                     '(d_depth / d_n_cells / d_max_fanout) proxying for "this candidate '
                     'was the accepted one"?'),
        'method': ('the tool\'s own build_matrix is monkey-patched to support the split '
                   'feature sets; every other part of the tool (leave-one-circuit-out, '
                   'ridge with the analytic LOO lambda search, the pool bootstrap CI) is '
                   'reused unchanged'),
        'splits': {k: list(v) for k, v in SPLITS.items()},
        'classifier': {},
        'mechanism': {},
    }

    for lm in ('gain', 'resolvable'):
        out['classifier'][lm] = {
            'control': run(rows, kinds, circuits, band_now, lm),
            'preview': run(rows, kinds, circuits, BAND_PREVIEW, lm),
        }
    out['mechanism']['gain_preview'] = mechanism(rows, BAND_PREVIEW, 'gain')
    out['mechanism']['gain_control'] = mechanism(rows, band_now, 'gain')
    out['mechanism']['resolvable_preview'] = mechanism(rows, BAND_PREVIEW, 'resolvable')

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()
