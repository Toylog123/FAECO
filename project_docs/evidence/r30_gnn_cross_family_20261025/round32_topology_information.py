"""Round 32, component G: is the topology information ABSENT, or was the
learner just not tuned?

Why this question exists
------------------------
Round 32's oracle comparison showed that the candidate-level physical signal
is NOT small: FAECO's own ideal-netlist delta predicts the post-route label at
a within-pool AUC of 0.85..0.88 (and the cheap placed tier at 0.91..0.93),
while the trivial baseline sits at 0.52..0.56.  So the candidate-level problem
is solvable -- but the solution is a *measurement*, not a *description of the
topology*.

That leaves the sharp version of LOG-29's negative result: is
"no candidate-level signal in the GRAPH" a statement about the graph, or an
artefact of (a) a binary label that throws away the magnitude, (b) a fixed
hyper-parameter setting, or (c) an architecture too small to carry the
information?

The information test
--------------------
Instead of predicting the thresholded label, predict the CONTINUOUS physical
quantity itself (the marginal placed delta and the marginal routed delta) by
regression.  A continuous target has no thresholding noise, so a null result
cannot be blamed on the label.  If a trained GNN encoder plus a linear readout
cannot explain the within-pool variance of the physical delta, while the
oracle (the ideal delta) explains a large share of it, then the information
that determines the physical outcome is NOT in the topology -- that is an
information limit, not a tuning artefact.

Controls
  C1  numeric gradient check of the REGRESSION path (a wrong backprop makes
      every number below meaningless)
  C2  random-init encoder + ridge on the same embedding (structure without
      target fitting)
  C3  the trivial baseline (kind_only) and LOG-24's scalar summaries, under
      the same folds and the same metric
  C4  the ideal/placed oracle under the same metric, as the scale reference

Everything is reused from the project's own tools: the rows and the graphs
come from the GNN tool, the features and the ridge come from
resolvable_positive_classifier, the fold protocol is the project's.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
SCR = REPO / 'scratch'
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))

import resolvable_positive_classifier as rpc  # noqa: E402
from surrogate_prototype import num  # noqa: E402
import gnn_candidate_signal as G  # noqa: E402

TARGETS = {'placed': 'placed_delta_wns', 'routed': 'routed_delta_wns'}


# --------------------------------------------------------------- regression
def loss_and_grad_reg(items, y, params, readout, use_A=True, use_types=True):
    """MSE on a linear readout (the GNN's forward pass is reused unchanged)."""
    pred, cache = G.forward(items, params['E'], params['W1'], params['b1'],
                            params['W2'], params['b2'], params['w_out'],
                            params['b_out'], readout, use_A, use_types)
    cache['E_used'] = params['E']
    d = pred - y
    # The project's gradient_check assumes the convention of the classification
    # path: the returned loss is the SUM and the returned gradient is the
    # MEAN-loss gradient (it divides the finite difference of the sum by n).
    # The regression path must follow the SAME convention, otherwise the check
    # compares a sum-difference against a mean-gradient and misses by a factor
    # of n -- which is exactly what the first real check reported
    # (max_rel_err 0.71 for n = 6).
    loss = float(np.sum(d ** 2))
    grad_logit = 2.0 * d / len(y)
    grads = G.backward(cache, grad_logit, params['W1'], params['W2'],
                       params['w_out'], readout)
    if not use_types:
        grads['E'] = np.zeros_like(grads['E'])
    return loss, grads, pred


# ------------------------------------------------------------------ metrics
def pool_index(rows):
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    return pool_idx


def _rankdata(v):
    """Average ranks (ties handled), so Spearman is a Pearson on the ranks."""
    order = np.argsort(v, kind='mergesort')
    s = v[order]
    uniq, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    starts = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    avg = starts + (cnt + 1) / 2.0
    r = np.empty(len(v), dtype=float)
    r[order] = avg[inv]
    return r


def within_pool_stats(rows, y, pred, pool_idx, min_rows=3):
    """Within-pool Pearson r and Spearman rho of a prediction against a target.

    Both are scale-free and offset-free, which is what a candidate generator
    needs (it must ORDER the candidates of one pool).  An R^2 is NOT used: the
    target's within-pool spread is tiny compared with any predictor's global
    offset, and a centred R^2 even rewards a scale mismatch (first smoke run:
    the oracle scored Pearson 0.667 with a centred R^2 of -2.86).
    """
    pears, spears, sizes = [], [], []
    for key, idx in sorted(pool_idx.items()):
        if len(idx) < min_rows:
            continue
        yy = np.asarray(y, dtype=float)[idx]
        pp = np.asarray(pred, dtype=float)[idx]
        if yy.std() <= 1e-12 or pp.std() <= 1e-12:
            continue
        pears.append(float(np.corrcoef(yy, pp)[0, 1]))
        spears.append(float(np.corrcoef(_rankdata(yy), _rankdata(pp))[0, 1]))
        sizes.append(len(idx))
    arr = np.asarray(pears, dtype=float) if pears else np.array([])
    return {
        'mean_within_pool_pearson': float(arr.mean()) if len(arr) else None,
        'median_within_pool_pearson': float(np.median(arr)) if len(arr) else None,
        'mean_within_pool_spearman': float(np.mean(spears)) if len(spears) else None,
        'median_within_pool_spearman': float(np.median(spears)) if len(spears) else None,
        'n_pools_used': int(len(arr)),
        'n_pools_total': int(len(pool_idx)),
        'pool_sizes': sizes,
        'per_pool_pearson': [float(v) for v in arr],
    }


def oof_ridge(rows, kinds, circuits, y, feature_set):
    """Leave-one-circuit-out ridge on the project's own feature sets.

    Same folds as rpc.oof_predict, but for a CONTINUOUS target (rpc's version
    maps the target to +-1 for the binary label).
    """
    ckt_of = [r.get('circuit') for r in rows]
    preds = np.zeros(len(rows))
    for held in circuits:
        tr = [i for i in range(len(rows)) if ckt_of[i] != held]
        te = [i for i in range(len(rows)) if ckt_of[i] == held]
        if not te:
            continue
        Xtr, _ = rpc.build_matrix([rows[i] for i in tr], feature_set, kinds)
        Xte, _ = rpc.build_matrix([rows[i] for i in te], feature_set, kinds)
        Ztr, Zte, _ = rpc.standardise(Xtr, Xte)
        w, _ = rpc.ridge_loocv_select(Ztr, np.asarray(y, dtype=float)[tr])
        preds[te] = Zte @ w
    return preds


def paired_r2_test(rows, y, pred_a, pred_b, name_a, name_b, pool_idx,
                   min_rows=3):
    """Per-pool paired comparison of two predictors on the within-pool Pearson r."""
    diffs, wins, losses = [], 0, 0
    for key, idx in sorted(pool_idx.items()):
        if len(idx) < min_rows:
            continue
        yy = np.asarray(y, dtype=float)[idx]
        pa = np.asarray(pred_a, dtype=float)[idx]
        pb = np.asarray(pred_b, dtype=float)[idx]
        if yy.std() <= 1e-12 or pa.std() <= 1e-12 or pb.std() <= 1e-12:
            continue
        ra = float(np.corrcoef(yy, pa)[0, 1])
        rb = float(np.corrcoef(yy, pb)[0, 1])
        diffs.append(rb - ra)
        if rb > ra:
            wins += 1
        elif rb < ra:
            losses += 1
    p, pos, neg = rpc.sign_test_p(diffs)
    return {'name_a': name_a, 'name_b': name_b, 'n_pools': len(diffs),
            'mean_diff': float(np.mean(diffs)) if diffs else None,
            'b_wins': wins, 'b_losses': losses,
            'b_ties': len(diffs) - wins - losses, 'sign_test_p': p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='itc99')
    ap.add_argument('--epochs', type=int, default=120)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rows, kinds, circuits, fam_dir = G.load_rows(args.family)
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    rows = [r for r in rows if num(r.get('routed_delta_wns'), None) is not None]
    gs = G.GraphSet(rows, fam_dir)
    keep = [i for i, r in enumerate(rows) if r['key'] in gs.by_key]
    rows = [rows[i] for i in keep]
    items = [gs.by_key[r['key']] for r in rows]
    pool_idx = pool_index(rows)

    out = {
        'family': args.family, 'band_ns': band,
        'n_rows': len(rows), 'n_circuits': len(circuits),
        'epochs': args.epochs,
        'question': ('is the candidate-level physical signal absent from the '
                     'TOPOLOGY, or was the learner not tuned?  the continuous '
                     'physical delta is regressed instead of its thresholded '
                     'label, so a null result cannot be blamed on the label'),
        'metric': ('mean within-pool R^2 (the pool mean is the baseline, so a '
                   'pool-level-only predictor scores exactly 0) and the mean '
                   'within-pool Pearson r'),
        'protocol': 'leave-one-circuit-out, identical to the project tool',
    }

    # ---- the regression path replaces the classification loss
    G.loss_and_grad = loss_and_grad_reg

    for tname, tcol in TARGETS.items():
        y = np.array([num(r.get(tcol), None) for r in rows], dtype=float)
        valid = np.isfinite(y)
        if valid.sum() < len(y):
            # keep the rows that carry the target
            rows_t = [r for r, v in zip(rows, valid) if v]
            items_t = [it for it, v in zip(items, valid) if v]
            y = y[valid]
            pool_idx_t = pool_index(rows_t)
        else:
            rows_t, items_t, pool_idx_t = rows, items, pool_idx

        # ---- C1: gradient check of the regression path, on the REAL target
        #      and aligned with the graph list (the project's gradient_check
        #      reads gs.items[:6] and y[:6], so the two must correspond).
        shim = type('Shim', (), {})()
        shim.items = items_t
        shim.n_types = gs.n_types
        gc = G.gradient_check(shim, y, 'mod')
        blk = {'n_rows': len(rows_t), 'n_pools': len(pool_idx_t),
               'C1_gradient_check_regression': gc,
               'target_column': tcol,
               'target_mean_ns': float(y.mean()), 'target_sd_ns': float(y.std()),
               'predictors': {}, 'paired_pool_tests': []}

        # ---- C3 baselines and C4 oracles (no training)
        base_preds = {}
        for fs in ('kind_only', 'structural'):
            p = oof_ridge(rows_t, kinds, circuits, y, fs)
            base_preds[fs] = p
            blk['predictors'][fs] = within_pool_stats(rows_t, y, p, pool_idx_t)
            print('  [%s] %-24s within_pool_r2=%s pearson=%s'
                  % (tname, fs, blk['predictors'][fs]['mean_within_pool_pearson'],
                     blk['predictors'][fs]['mean_within_pool_pearson']), flush=True)
        for tier in ('ideal', 'placed'):
            col = rpc.TARGET_COL[tier]
            if not all(num(r.get(col), None) is not None for r in rows_t):
                continue
            p = np.array([num(r.get(col), 0.0) for r in rows_t])
            blk['predictors']['oracle_' + tier] = within_pool_stats(
                rows_t, y, p, pool_idx_t)
            print('  [%s] oracle_%-14s within_pool_r2=%s pearson=%s'
                  % (tname, tier, blk['predictors']['oracle_' + tier]['mean_within_pool_pearson'],
                     blk['predictors']['oracle_' + tier]['mean_within_pool_pearson']),
                  flush=True)

        # ---- the GNN, trained by regression on the continuous target
        ckt_of = [r.get('circuit') for r in rows_t]
        gnn_pred = np.zeros(len(rows_t))
        for held in circuits:
            tr = [i for i in range(len(rows_t)) if ckt_of[i] != held]
            te = [i for i in range(len(rows_t)) if ckt_of[i] == held]
            if not te:
                continue
            mu = float(y[tr].mean())
            sd = float(y[tr].std()) or 1.0
            ytr = (y[tr] - mu) / sd
            params = G.train([items_t[i] for i in tr], ytr, 'mod', gs.n_types,
                              seed=G.SEED, epochs=args.epochs)
            p = G.predict([items_t[i] for i in te], params, 'mod')
            gnn_pred[te] = p * sd + mu
        blk['predictors']['gnn_regr_mod'] = within_pool_stats(
            rows_t, y, gnn_pred, pool_idx_t)
        print('  [%s] gnn_regr_mod            within_pool_r2=%s pearson=%s'
              % (tname, blk['predictors']['gnn_regr_mod']['mean_within_pool_pearson'],
                 blk['predictors']['gnn_regr_mod']['mean_within_pool_pearson']),
              flush=True)

        # ---- C2 random-init encoder + ridge on the same embedding
        rng2 = np.random.default_rng(G.SEED + 9)
        params0 = G.init_params(gs.n_types, 'mod', rng2)
        for k in ('W1', 'W2'):
            params0[k] = params0[k] + rng2.normal(0, 0.1, size=params0[k].shape)
        emb = []
        for s in range(0, len(items_t), 64):
            chunk = items_t[s:s + 64]
            _, cache = G.forward(chunk, params0['E'], params0['W1'], params0['b1'],
                                 params0['W2'], params0['b2'], np.ones(2 * G.D_H + 1),
                                 0.0, 'mod', True)
            emb.append(cache['R'])
        R = np.vstack(emb)
        rp = np.zeros(len(rows_t))
        for held in circuits:
            tr = [i for i in range(len(rows_t)) if ckt_of[i] != held]
            te = [i for i in range(len(rows_t)) if ckt_of[i] == held]
            if not te:
                continue
            Xtr = np.hstack([np.ones((len(tr), 1)), R[tr]])
            Xte = np.hstack([np.ones((len(te), 1)), R[te]])
            w, _ = rpc.ridge_loocv_select(Xtr, y[tr])
            rp[te] = Xte @ w
        blk['predictors']['C2_random_init_encoder_probe'] = within_pool_stats(
            rows_t, y, rp, pool_idx_t)
        print('  [%s] C2_random_init_probe    within_pool_r2=%s pearson=%s'
              % (tname,
                 blk['predictors']['C2_random_init_encoder_probe']['mean_within_pool_pearson'],
                 blk['predictors']['C2_random_init_encoder_probe']['mean_within_pool_pearson']),
              flush=True)

        # ---- paired per-pool tests against the trivial baseline
        for pname, ppred in (('gnn_regr_mod', gnn_pred),
                             ('C2_random_init_encoder_probe', rp),
                             ('oracle_ideal', np.array(
                                 [num(r.get(rpc.TARGET_COL['ideal']), 0.0) for r in rows_t])
                              if all(num(r.get(rpc.TARGET_COL['ideal']), None) is not None
                                     for r in rows_t) else None)):
            if ppred is None:
                continue
            for bname in ('kind_only', 'structural'):
                t = paired_r2_test(rows_t, y, base_preds[bname], ppred,
                                   bname, pname, pool_idx_t)
                blk['paired_pool_tests'].append(t)
                print('  [%s] paired %-10s vs %-28s diff=%s wins %s losses %s p=%s'
                      % (tname, bname, pname, t['mean_diff'], t['b_wins'],
                         t['b_losses'], t['sign_test_p']), flush=True)

        out.setdefault('C1_gradient_check_regression', {})[tname] = gc
        print('  [%s] C1 gradient check: max_abs_err=%.3e max_rel_err=%.3e (%d checks)'
              % (tname, gc['max_abs_err'], gc['max_rel_err'], gc['n_checks']), flush=True)
        out['target_' + tname] = blk

    dest = Path(args.out) if args.out else SCR / ('round32_topology_info_%s.json' % args.family)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', dest)


if __name__ == '__main__':
    main()
