"""Round 32, component E: how much candidate-level signal is there at all?

The GNN adjudication (LOG-29) compares the GNN against the trivial baseline
`kind_only`.  That answers "is the GNN better than a one-hot?" but not "is
there anything left to learn?".  This tool adds the reference point the
project never measured: the IDEAL-NETLIST DELTA as a predictor of the
post-route label.

FAECO already computes the ideal-netlist WNS of every candidate it proposes,
so this is not an oracle in the cheating sense -- it is the project's own
strongest netlist-derived signal, used as a competitor.  If even it cannot
beat `kind_only` inside a pool, then the candidate-level ceiling is low and
the GNN's null result is a property of the signal/label, not of the GNN.

Everything is read from the project's own tools:
  * the rows and the labels come from the GNN tool (the same loader, the same
    label construction, the family's OWN band);
  * the baselines come from rpc.oof_predict (the project's classifier tool);
  * the AUC / pool-bootstrap / paired-pool code is the GNN tool's.

The marginal columns are used throughout (rpc.TARGET_COL): LOG-27 established
that the ledger's 'cumulative' quantity is in fact a marginal quantity, and
the project's own tools read `*_delta_wns`.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
SCR = REPO / 'scratch'
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))

import resolvable_positive_classifier as rpc  # noqa: E402
from surrogate_prototype import num  # noqa: E402
import gnn_candidate_signal as G  # noqa: E402  (the project's own tool, reused)

ORACLE_SRC = {
    'ideal': 'ideal_delta_wns',
    'placed': 'placed_delta_wns',
}


def score_for(rows, col, label_mode):
    """A continuous score whose LARGER value means 'more likely positive'.

    resolvable: |delta| -- the label asks whether the magnitude beats the band
    harm:      -delta -- the label asks whether the delta went below -band
    gain:       delta -- the label asks whether the delta went above +band
    """
    if label_mode == 'resolvable':
        return np.array([abs(num(r.get(col), 0.0)) for r in rows])
    if label_mode == 'harm':
        return np.array([-num(r.get(col), 0.0) for r in rows])
    return np.array([num(r.get(col), 0.0) for r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='itc99')
    ap.add_argument('--label', default='resolvable')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rows, kinds, circuits, fam_dir = G.load_rows(args.family)
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    rows = [r for r in rows if num(r.get('routed_delta_wns'), None) is not None]
    y = G.label_vector(rows, band, args.label)

    out = {
        'family': args.family, 'label_mode': args.label, 'band_ns': band,
        'n_rows': len(rows), 'n_positive': int(y.sum()),
        'n_circuits': len(circuits),
        'marginal_columns_used': ORACLE_SRC,
        'question': ('how much candidate-level signal is there at all?  the '
                     'ideal-netlist delta is FAECO\'s own strongest '
                     'netlist-derived signal, so it is the reference point for '
                     '"is there room left for any learner?"'),
    }

    # ---- the project's own baselines -------------------------------------
    base_preds = {}
    out['baselines_from_project_tool'] = {}
    for fs in ('kind_only', 'structural'):
        p, _ = rpc.oof_predict(rows, kinds, circuits, y, fs, model='ridge')
        base_preds[fs] = p
        m = G.pool_metrics(rows, y, p)
        out['baselines_from_project_tool'][fs] = m
        print('  %-28s pooled=%s within=%s' % (fs, m['pooled_auc'], m['mean_within_pool_auc']))

    # ---- the oracles ------------------------------------------------------
    oracles = {}
    for tier, col in ORACLE_SRC.items():
        vals = [r.get(col) for r in rows]
        have = [v for v in vals if num(v, None) is not None]
        if len(have) < len(rows):
            print('  %-28s SKIPPED (only %d/%d rows carry the column)'
                  % ('oracle_' + tier, len(have), len(rows)))
            continue
        s = score_for(rows, col, args.label)
        m = G.pool_metrics(rows, y, s)
        oracles['oracle_' + tier] = s
        m['source_column'] = col
        m['n_rows_with_column'] = len(have)
        oracles_res = oracles
        print('  %-28s pooled=%s within=%s CI=%s'
              % ('oracle_' + tier, m['pooled_auc'], m['mean_within_pool_auc'],
                 m['mean_within_pool_auc_ci95']))
    out['oracles'] = {k: G.pool_metrics(rows, y, v) for k, v in oracles.items()}

    # ---- paired per-pool tests: oracle vs the trivial baseline -----------
    out['paired_pool_tests'] = []
    for oname, spred in oracles.items():
        for bname in ('kind_only', 'structural'):
            t = G.paired_pool_test(rows, y, base_preds[bname], spred, bname, oname)
            out['paired_pool_tests'].append(t)
            print('  paired %-12s vs %-16s diff=%s wins %s losses %s p=%s'
                  % (bname, oname, t['mean_diff'], t['b_wins'], t['b_losses'],
                     t['sign_test_p']))

    # ---- how much of the pooled AUC is pool-level? -----------------------
    out['pool_vs_candidate_decomposition'] = {
        'note': ('pooled_auc_pool_mean_only is the AUC of a predictor that '
                 'knows each pool\'s MEAN score and nothing about the '
                 'individual candidates; the difference between it and the '
                 'pooled AUC is the pool-level component (LOG-24)'),
        'kind_only': out['baselines_from_project_tool']['kind_only'].get(
            'pooled_auc_pool_mean_only'),
        'structural': out['baselines_from_project_tool']['structural'].get(
            'pooled_auc_pool_mean_only'),
        'oracles': {k: v.get('pooled_auc_pool_mean_only')
                    for k, v in out['oracles'].items()},
    }

    dest = Path(args.out) if args.out else SCR / ('round32_oracle_%s.json' % args.family)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', dest)


if __name__ == '__main__':
    main()
