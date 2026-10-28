"""THIRD TEST: cross-family replication of the single-feature structural signal.

The second test found that on the RESOLVABLE label a SINGLE structural scalar --
`depth` (the candidate netlist's logic depth) -- carries a consistent signal
(pooled AUC 0.653 at the pilot band and 0.637 at the full-family preview band,
mean per-circuit AUC 0.605 with a CI excluding 0.5), while the 23-feature
`structural` bundle shows none (0.444 / 0.445).

That set was CHOSEN BY LOOKING AT THE DATA (nine sets were tried), so it is a
post-hoc finding and cannot be believed on one family.  The decisive check is
an INDEPENDENT FAMILY: ISCAS89, whose routed band (2 sigma = 0.055543 ns) is
already its final full-family value -- no pending band change, no shared
threshold, a different benchmark.

The same split sets and the same per-circuit breakdown are computed there with
the same tool code.  A signal that does not replicate is a multiple-comparison
artefact and must be reported as such.
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))

import resolvable_positive_classifier as rpc  # noqa: E402

OUT = REPO / 'scratch/structural_signal_crossfamily.json'

SPLITS = {
    'struct_local_only': rpc.STRUCT_LOCAL,
    'struct_global_only': rpc.STRUCT_GLOBAL,
    'struct_delta_only': rpc.STRUCT_DELTA,
    'struct_topo_no_delta': rpc.STRUCT_LOCAL + rpc.STRUCT_GLOBAL,
    'one_n_cells': ('n_cells',),
    'one_depth': ('depth',),
    'one_max_fanout': ('max_fanout',),
    'one_n_ff': ('n_ff',),
    'one_n_primary_inputs': ('n_primary_inputs',),
}
CUSTOM_SETS = ('kind_only', 'structural',) + tuple(SPLITS.keys())

def _itc99_band():
    """The ITC-99 routed candidate-level band, read back from the artefact."""
    tpc = json.loads((rpc.FAM_DIRS['itc99'] / 'three_point_curve.json')
                     .read_text(encoding='utf-8'))
    return (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')


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


def rows_joined(fam):
    fam_dir = rpc.FAM_DIRS[fam]
    tt = fam_dir / 'training_table.jsonl'
    rows_all = [json.loads(l) for l in tt.read_text(encoding='utf-8').splitlines() if l.strip()]
    feats = rpc.load_ledger(rpc.LEDGERS[fam])
    struct = rpc.load_structural(fam_dir)
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


def run(fam, band, label_mode):
    rows, kinds, circuits = rows_joined(fam)
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
    return {'band_ns': band, 'n_rows': res['n_rows'], 'n_positive': res['n_positive'],
            'powered': res['powered'], 'cells': cells}


def main():
    out = {'method': ('the same split and single-feature sets, the same tool code, on '
                      'the INDEPENDENT ISCAS89 family, whose routed band is already its '
                      'final full-family value'),
           'families': {}}

    # ---- ISCAS89: its own band, already final
    fam = 'iscas89'
    fam_dir = rpc.FAM_DIRS[fam]
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
    out['families']['iscas89'] = {
        'band_ns': band,
        'classifier': {lm: run(fam, band, lm) for lm in ('resolvable', 'gain', 'harm')},
    }

    # ---- ITC-99: both bands, for the side-by-side
    fam = 'itc99'
    fam_dir = rpc.FAM_DIRS[fam]
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band_now = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
    out['families']['itc99'] = {
        'band_in_force_ns': band_now,
        'band_preview_ns': _itc99_band(),
        'classifier': {
            lm: {'control': run(fam, band_now, lm),
                 'preview': run(fam, _itc99_band(), lm)}
            for lm in ('resolvable', 'gain', 'harm')
        },
    }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()
