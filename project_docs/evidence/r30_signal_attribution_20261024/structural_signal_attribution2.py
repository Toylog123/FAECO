"""SECOND ATTRIBUTION TEST for the structural-feature signal.

The first test (scratch/gain_label_attribution.py) split the `structural` set
into its three kinds and found the signal in the GLOBAL size features
(depth / n_cells / n_ff / max_fanout / n_primary_inputs / n_primary_outputs),
not in the local topology and not in the change magnitude.

But "the candidate netlist is big" is close to "the circuit is big" -- the
candidate is the iteration base plus a few cells, so n_cells is very nearly a
constant per circuit.  If the signal is a CIRCUIT-LEVEL effect, it does not
support the claim that graph structure can pick the candidate worth verifying;
it only says "some circuits have bigger gains than others".

Two decisive checks:
  1. WITHIN-CIRCUIT vs BETWEEN-CIRCUIT.  The pooled AUC mixes both.  The tool
     already computes the per-circuit AUC; if the per-circuit values are near
     0.5 while the pooled value is high, the signal is between circuits.
  2. SINGLE-FEATURE CONTROL.  If `n_cells` alone reproduces most of the
     six-feature AUC, the "graph structure" claim collapses to "circuit size".
  3. A CIRCUIT-LEVEL PREDICTOR.  A constant-per-circuit predictor (the circuit
     mean of the label) scores how much of the signal is explained by the
     circuit alone -- the upper bound for any circuit-size proxy.

Everything else (leave-one-circuit-out, ridge with the analytic LOO lambda
search, the pool bootstrap CI) is the tool's own code.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))

import resolvable_positive_classifier as rpc  # noqa: E402

FAM = 'itc99'
FAM_DIR = rpc.FAM_DIRS[FAM]
OUT = REPO / 'scratch/structural_signal_attribution2.json'
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
    'one_n_cells': ('n_cells',),
    'one_depth': ('depth',),
    'one_max_fanout': ('max_fanout',),
    'one_n_ff': ('n_ff',),
}
CUSTOM_SETS = ('kind_only', 'structural',) + tuple(SPLITS.keys())

_orig_build = rpc.build_matrix


def patched_build(rows, feature_set, kinds):
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


def circuit_level_ceiling(rows, band, label_mode):
    """How much of the label does the CIRCUIT alone explain?

    The predictor is the leave-one-circuit-out estimate of the circuit's own
    mean label -- i.e. for a candidate of circuit C, predict the mean label of
    every OTHER circuit.  This is the upper bound of any predictor that only
    knows WHICH circuit it is in (a circuit-size proxy included).
    """
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    thr = band
    if label_mode == 'gain':
        y = np.array([1.0 if rpc.num(r.get(rpc.TARGET_COL['routed']), 0.0) > thr else 0.0
                      for r in sub])
    else:
        y = np.array([1.0 if abs(rpc.num(r.get(rpc.TARGET_COL['routed']), 0.0)) > thr else 0.0
                      for r in sub])
    by_c = defaultdict(list)
    for i, r in enumerate(sub):
        by_c[r.get('circuit')].append(i)
    means = {c: float(y[idx].mean()) for c, idx in by_c.items()}
    glob = float(y.mean())
    preds = np.array([(sum(v for cc, v in means.items() if cc != r.get('circuit'))
                       / max(1, len(means) - 1)) for r in sub])
    a = rpc.auc(y, preds)
    # the same quantity computed INSIDE each circuit is impossible (a constant
    # carries no information), so the between-circuit ceiling IS the pooled one
    return {
        'n': len(sub), 'n_positive': int(y.sum()),
        'n_circuits': len(by_c),
        'circuit_mean_label_spread': round(max(means.values()) - min(means.values()), 6),
        'pooled_auc_of_circuit_id': round(a, 6) if a is not None else None,
        'global_positive_rate': round(glob, 6),
        'per_circuit_positive_rate': {c: round(float(y[idx].mean()), 6)
                                      for c, idx in sorted(by_c.items())},
        'note': ('the predictor knows only WHICH circuit a candidate belongs to; a '
                 'circuit-size proxy cannot beat this ceiling'),
    }


def run(rows, kinds, circuits, band, label_mode):
    rng = np.random.default_rng(rpc.SEED)
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    res = rpc.evaluate('routed', sub, kinds, circuits, band, rng,
                       feature_sets=CUSTOM_SETS, label_mode=label_mode)
    cells = {}
    for fs, c in res['cells'].items():
        cells[fs] = {
            'pooled_auc': c.get('pooled_auc'),
            'ci95': c.get('pooled_auc_ci95'),
            'mean_per_circuit_auc': c.get('mean_per_circuit_auc'),
            'mean_per_circuit_auc_ci95': c.get('mean_per_circuit_auc_ci95'),
            'per_circuit_auc': c.get('per_circuit_auc'),
        }
    return {'band_ns': band, 'n_positive': res['n_positive'],
            'powered': res['powered'], 'cells': cells}


def main():
    rows, kinds, circuits = rows_joined()
    tpc = json.loads((FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    band_now = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    out = {
        'question': ('is the global-size signal in the structural features a '
                     'GRAPH-STRUCTURE effect (within a pool) or a CIRCUIT-LEVEL effect '
                     '(between circuits, e.g. circuit size)?'),
        'method': ('the tool\'s own build_matrix is monkey-patched for the split and '
                   'single-feature sets; every statistic is the tool\'s own code; the '
                   'circuit-level ceiling is a leave-one-circuit-out predictor that '
                   'knows only the circuit identity'),
        'classifier': {},
        'circuit_level_ceiling': {},
    }
    for lm in ('gain', 'resolvable'):
        out['classifier'][lm] = {
            'control': run(rows, kinds, circuits, band_now, lm),
            'preview': run(rows, kinds, circuits, BAND_PREVIEW, lm),
        }
        out['circuit_level_ceiling'][lm] = {
            'control': circuit_level_ceiling(rows, band_now, lm),
            'preview': circuit_level_ceiling(rows, BAND_PREVIEW, lm),
        }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()
