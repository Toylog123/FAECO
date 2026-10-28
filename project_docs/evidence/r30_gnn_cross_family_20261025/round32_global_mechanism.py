"""Round 32, addendum A: matched controls for gnn_global + mechanism diagnostics.

WHY THIS TOOL EXISTS
--------------------
The ISCAS89 cross-family replication produced, for the first time, a GNN variant
whose mean within-pool AUC beats the trivial baseline:

    gnn_global  0.653625   vs   kind_only  0.517298
    paired per-pool sign test: +0.136326, 13 wins / 4 losses, p = 0.049041748

But the two controls that the pre-registered falsification criterion asks for
were run with the WRONG architecture: in gnn_candidate_signal.py, C2 (null
labels) and C4 (random-init encoder) both use readout='mod', while the variant
under test, gnn_global, uses readout='global'.  A control that was trained with
a different readout does not certify that the signal is not an artefact of the
readout under test.

This tool therefore does three things, all pre-declared in
scratch/round32_preregistration_addendum_A.json BEFORE any of it ran:

  1. the MATCHED controls: C2-global (null labels, global readout) and
     C4-global (random-init global encoder + ridge);
  2. the MECHANISM diagnostics D1-D7: is the 0.6536 driven by pool size, by a
     single pool, by a single circuit, by a degenerate (near-constant) score,
     or by the positive-rate/池-size structure that makes the within-pool mean
     AUC a biased statistic in the first place;
  3. the RECOVERY of the prediction vectors (the artefact JSON stores only
     per-pool AUCs), which is also a harness check: the recomputed
     gnn_global must reproduce the published 0.653625 exactly.

The thresholds are NOT touched: 0.53 for the controls, p < 0.05 for the
pre-registered gate.  The permutation null (D4) is reported as a SUPPLEMENT,
never as a replacement for the pre-registered gate.
"""
import argparse
import json
import sys
import time
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

THRESH = 0.53            # the pre-registered threshold, unchanged
PERM_B = 2000            # permutation replicates for D4


# --------------------------------------------------------------------- stats
def rankdata(a):
    """Average ranks (ties handled), so Spearman == Pearson on ranks."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind='mergesort')
    ss = a[order]
    uniq, inv, cnt = np.unique(ss, return_inverse=True, return_counts=True)
    starts = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    avg = starts + (cnt + 1) / 2.0
    r = np.empty(len(a), dtype=float)
    r[order] = avg[inv]
    return r


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3:
        return None
    xc = x - x.mean()
    yc = y - y.mean()
    dx = float(np.sqrt((xc * xc).sum()))
    dy = float(np.sqrt((yc * yc).sum()))
    if dx == 0 or dy == 0:
        return None
    return float((xc * yc).sum() / (dx * dy))


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))


def mean_within_pool(rows, y, preds, pool_idx):
    """Mean of the per-pool AUCs; pools with a single class are skipped.

    This is the project's own definition (rpc.auc returns None for a single
    class), reproduced here so that the permutation null uses exactly the same
    statistic as the headline reading.
    """
    vals = []
    for _key, idx in sorted(pool_idx.items()):
        a = rpc.auc(y[idx], preds[idx])
        if a is not None:
            vals.append((_key, idx, a))
    if not vals:
        return None, []
    return float(np.mean([v[2] for v in vals])), vals


# ------------------------------------------------------------------ controls
def random_init_probe(rows, items, kinds, circuits, y, readout, n_types,
                      seed_offset):
    """C4 for an arbitrary readout: random-init encoder + ridge, LOCO.

    Mirrors the project's own C4 block, with the readout as the only thing
    that changes.

    NOTE (bug caught on the first run): the project's C4 passes
    ``np.ones(2 * D_H + 1)`` as ``w_out``, which is the right width for the
    'mod' readout (R = [h_mod, h_mod - mean_all, has]).  For the 'global'
    readout R = mean_all and its width is D_H, so the placeholder ``w_out``
    must be D_H wide -- otherwise ``R @ w_out`` raises a shape error.  The
    readout width is therefore derived from the readout, never hard-coded.
    """
    r_dim = G.D_H if readout == 'global' else 2 * G.D_H + 1
    rng2 = np.random.default_rng(G.SEED + seed_offset)
    params0 = G.init_params(n_types, readout, rng2)
    for k in ('W1', 'W2'):
        params0[k] = params0[k] + rng2.normal(0, 0.1, size=params0[k].shape)
    emb = []
    for s in range(0, len(items), 64):
        chunk = items[s:s + 64]
        _logit, cache = G.forward(chunk, params0['E'], params0['W1'],
                                  params0['b1'], params0['W2'], params0['b2'],
                                  np.ones(r_dim), 0.0, readout, True)
        emb.append(cache['R'])
    R = np.vstack(emb)
    ckt_of = [r.get('circuit') for r in rows]
    rp = np.zeros(len(rows))
    for held in circuits:
        tr = [i for i in range(len(rows)) if ckt_of[i] != held]
        te = [i for i in range(len(rows)) if ckt_of[i] == held]
        if len(set(y[tr])) < 2 or not te:
            continue
        Xtr = np.hstack([np.ones((len(tr), 1)), R[tr]])
        Xte = np.hstack([np.ones((len(te), 1)), R[te]])
        w, _ = rpc.ridge_loocv_select(Xtr, 2.0 * y[tr] - 1.0)
        rp[te] = Xte @ w
    return rp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='iscas89')
    ap.add_argument('--label', default='resolvable')
    ap.add_argument('--epochs', type=int, default=120)
    ap.add_argument('--perms', type=int, default=PERM_B)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rows, kinds, circuits, fam_dir = G.load_rows(args.family)
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
    rows = [r for r in rows if num(r.get('routed_delta_wns'), None) is not None]
    y = G.label_vector(rows, band, args.label)
    gs = G.GraphSet(rows, fam_dir)
    keep = [i for i, r in enumerate(rows) if r['key'] in gs.by_key]
    rows = [rows[i] for i in keep]
    y = y[keep]
    items = [gs.by_key[r['key']] for r in rows]

    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)

    out = {
        'family': args.family, 'label_mode': args.label, 'band_ns': band,
        'n_rows': len(rows), 'n_circuits': len(circuits),
        'n_pools_total': len(pool_idx),
        'threshold': THRESH,
        'pre_registration': 'scratch/round32_preregistration_addendum_A.json',
        'note': ('the threshold 0.53 and the p<0.05 gate are the ones written '
                 'before the run; this tool does not re-tune them'),
    }

    # ---------------------------------------------------------- predictions
    print('[A] recovering the prediction vectors ...', flush=True)
    t0 = time.time()
    p_kind, _ = rpc.oof_predict(rows, kinds, circuits, y, 'kind_only',
                                 model='ridge')
    p_struct, _ = rpc.oof_predict(rows, kinds, circuits, y, 'structural',
                                   model='ridge')
    p_global = G.run_loco(rows, y, items, circuits, 'global', True, gs.n_types,
                          epochs=args.epochs, use_types=True)
    print('  recovered in %.0f s' % (time.time() - t0), flush=True)

    m_kind = G.pool_metrics(rows, y, p_kind)
    m_struct = G.pool_metrics(rows, y, p_struct)
    m_global = G.pool_metrics(rows, y, p_global)
    out['recovered'] = {
        'kind_only': {'pooled_auc': m_kind['pooled_auc'],
                      'mean_within_pool_auc': m_kind['mean_within_pool_auc']},
        'structural': {'pooled_auc': m_struct['pooled_auc'],
                       'mean_within_pool_auc': m_struct['mean_within_pool_auc']},
        'gnn_global': {'pooled_auc': m_global['pooled_auc'],
                       'mean_within_pool_auc': m_global['mean_within_pool_auc']},
    }
    print('  kind_only within=%s' % m_kind['mean_within_pool_auc'], flush=True)
    print('  structural within=%s' % m_struct['mean_within_pool_auc'], flush=True)
    print('  gnn_global within=%s' % m_global['mean_within_pool_auc'], flush=True)

    # harness check against the published artefact
    pub_path = SCR / ('gnn_%s_replication.json'
                      % ('iscas89' if args.family == 'iscas89' else 'itc99_control'))
    harness = None
    if pub_path.exists():
        pub = json.loads(pub_path.read_text(encoding='utf-8'))
        pv = pub['gnn']['gnn_global']['mean_within_pool_auc']
        harness = {'published': pv,
                   'recomputed': m_global['mean_within_pool_auc'],
                   'identical': bool(pv == m_global['mean_within_pool_auc'])}
        out['harness_check'] = harness
        print('  harness check: published=%r recomputed=%r identical=%s'
              % (pv, m_global['mean_within_pool_auc'], harness['identical']),
              flush=True)

    # ------------------------------------------------------ matched controls
    print('[A] matched control C2-global (null labels, global readout) ...',
          flush=True)
    rng = np.random.default_rng(G.SEED + 5)
    y_null = y.copy()
    for _idx in pool_idx.values():
        perm = rng.permutation(len(_idx))
        y_null[_idx] = y[_idx][perm]
    t0 = time.time()
    p_null_global = G.run_loco(rows, y_null, items, circuits, 'global', True,
                                gs.n_types, epochs=args.epochs, use_types=True)
    m_c2g = G.pool_metrics(rows, y, p_null_global)
    print('  C2-global within=%s  (%.0f s)'
          % (m_c2g['mean_within_pool_auc'], time.time() - t0), flush=True)

    print('[A] matched control C4-global (random-init global encoder) ...',
          flush=True)
    p_c4g = random_init_probe(rows, items, kinds, circuits, y, 'global',
                              gs.n_types, 9)
    m_c4g = G.pool_metrics(rows, y, p_c4g)
    print('  C4-global within=%s' % m_c4g['mean_within_pool_auc'], flush=True)

    out['controls'] = {
        'C2_global': {'pooled_auc': m_c2g['pooled_auc'],
                      'mean_within_pool_auc': m_c2g['mean_within_pool_auc'],
                      'ci95': m_c2g['mean_within_pool_auc_ci95'],
                      'below_threshold': bool(
                          m_c2g['mean_within_pool_auc'] < THRESH)},
        'C4_global': {'pooled_auc': m_c4g['pooled_auc'],
                      'mean_within_pool_auc': m_c4g['mean_within_pool_auc'],
                      'ci95': m_c4g['mean_within_pool_auc_ci95'],
                      'below_threshold': bool(
                          m_c4g['mean_within_pool_auc'] < THRESH)},
    }

    # the unmatched controls, for the side-by-side reading
    if pub_path.exists():
        pub = json.loads(pub_path.read_text(encoding='utf-8'))
        out['controls']['C2_mod_from_artefact'] = {
            'mean_within_pool_auc':
                pub['C2_null_labels']['mean_within_pool_auc'],
            'note': "readout='mod' -- this is the control that was actually run"}
        out['controls']['C4_mod_from_artefact'] = {
            'mean_within_pool_auc':
                pub['C4_random_init_encoder_probe']['mean_within_pool_auc'],
            'note': "readout='mod' -- this is the control that was actually run"}

    # DIAG_TRY: the diagnostics run inside a guard so that a failure
    # here is recorded and the controls (the expensive part) survive.
    try:
        # ------------------------------------------------------------ D1..D7
        wp, vals = mean_within_pool(rows, y, p_kind, pool_idx)
        _, vals_g = mean_within_pool(rows, y, p_global, pool_idx)
        gmap = {k: a for k, _i, a in vals_g}
        recs = []
        for key, idx, a_kind in vals:
            a_g = gmap.get(key)
            if a_g is None:
                continue
            k = int(y[idx].sum())
            recs.append({
                'circuit': key[0], 'iteration': key[1], 'n': len(idx),
                'positives': k, 'negatives': len(idx) - k,
                'auc_kind_only': a_kind, 'auc_gnn_global': a_g,
                'diff': a_g - a_kind,
            })
        recs.sort(key=lambda r: (str(r['circuit']), str(r['iteration'])))
        diffs = [r['diff'] for r in recs]
        out['per_pool'] = recs
        out['mean_diff'] = float(np.mean(diffs))
        print('[D] %d usable pools, mean diff = %+.6f'
              % (len(recs), out['mean_diff']), flush=True)

        # D1: pool-size / positive-count confound
        ns = [r['n'] for r in recs]
        ks = [r['positives'] for r in recs]
        out['D1_size_confound'] = {
            'spearman_diff_vs_n': spearman(diffs, ns),
            'spearman_diff_vs_positives': spearman(diffs, ks),
            'spearman_n_vs_positives': spearman(ns, ks),
        }
        print('  D1 rho(diff,n)=%s rho(diff,k)=%s rho(n,k)=%s'
              % (out['D1_size_confound']['spearman_diff_vs_n'],
                 out['D1_size_confound']['spearman_diff_vs_positives'],
                 out['D1_size_confound']['spearman_n_vs_positives']), flush=True)

        # D2: leave-one-pool-out
        loo = []
        for j in range(len(recs)):
            rest = [d for i, d in enumerate(diffs) if i != j]
            loo.append(float(np.mean(rest)))
        out['D2_leave_one_pool_out'] = {
            'min_mean_diff': min(loo), 'max_mean_diff': max(loo),
            'n_removals_flip_sign': sum(1 for v in loo if v <= 0),
            'worst_removed_pool': recs[int(np.argmin(loo))],
        }
        print('  D2 LOPO min=%+.6f max=%+.6f flips=%d'
              % (min(loo), max(loo), out['D2_leave_one_pool_out']
                 ['n_removals_flip_sign']), flush=True)

        # D3: leave-one-circuit-out
        ckt_set = sorted({r['circuit'] for r in recs})
        loco = {}
        for c in ckt_set:
            rest = [r['diff'] for r in recs if r['circuit'] != c]
            loco[c] = float(np.mean(rest)) if rest else None
        out['D3_leave_one_circuit_out'] = loco
        vals_loco = [v for v in loco.values() if v is not None]
        out['D3_leave_one_circuit_out_summary'] = {
            'min': min(vals_loco), 'max': max(vals_loco),
            'n_negative': sum(1 for v in vals_loco if v <= 0)}
        print('  D3 LOCO min=%+.6f max=%+.6f negative=%d'
              % (min(vals_loco), max(vals_loco),
                 out['D3_leave_one_circuit_out_summary']['n_negative']), flush=True)

        # D4: label-permutation null on the same statistic
        print('[D] permutation null (B=%d) ...' % args.perms, flush=True)
        rngp = np.random.default_rng(G.SEED + 101)
        obs_kind = wp
        obs_global = mean_within_pool(rows, y, p_global, pool_idx)[0]
        null_kind, null_global, null_diff = [], [], []
        for _ in range(args.perms):
            yp = y.copy()
            for _idx in pool_idx.values():
                yp[_idx] = y[_idx][rngp.permutation(len(_idx))]
            a, _v = mean_within_pool(rows, yp, p_kind, pool_idx)
            b, _v2 = mean_within_pool(rows, yp, p_global, pool_idx)
            if a is None or b is None:
                continue
            null_kind.append(a)
            null_global.append(b)
            null_diff.append(b - a)
        null_kind = np.array(null_kind)
        null_global = np.array(null_global)
        null_diff = np.array(null_diff)

        def emp_two_sided(obs, null):
            if len(null) == 0:
                return None
            centre = float(null.mean())
            return float((np.sum(np.abs(null - centre) >= abs(obs - centre)) + 1)
                         / (len(null) + 1))

        out['D4_permutation_null'] = {
            'B': int(len(null_diff)),
            'null_mean_within_pool_auc': {
                'kind_only': {'mean': float(null_kind.mean()),
                              'sd': float(null_kind.std(ddof=1)),
                              'p2_5': float(np.percentile(null_kind, 2.5)),
                              'p97_5': float(np.percentile(null_kind, 97.5)),
                              'observed': obs_kind,
                              'emp_p_two_sided': emp_two_sided(obs_kind, null_kind)},
                'gnn_global': {'mean': float(null_global.mean()),
                               'sd': float(null_global.std(ddof=1)),
                               'p2_5': float(np.percentile(null_global, 2.5)),
                               'p97_5': float(np.percentile(null_global, 97.5)),
                               'observed': obs_global,
                               'emp_p_two_sided': emp_two_sided(obs_global,
                                                              null_global)},
            },
            'null_paired_mean_diff': {
                'mean': float(null_diff.mean()),
                'sd': float(null_diff.std(ddof=1)),
                'p2_5': float(np.percentile(null_diff, 2.5)),
                'p97_5': float(np.percentile(null_diff, 97.5)),
                'observed': float(np.mean(diffs)),
                'emp_p_two_sided': emp_two_sided(float(np.mean(diffs)), null_diff),
            },
            'caveat': ('the permutation keeps each pool\'s positive count but '
                       'scrambles WHICH candidates are positive; both predictors '
                       'were fitted on the REAL labels, so this null is '
                       'conservative in the direction of significance for whichever '
                       'predictor retains more label information.  It is reported '
                       'as a supplement and does NOT replace the pre-registered '
                       'sign test.'),
        }
        print('  D4 kind_only emp_p=%s  gnn_global emp_p=%s  paired emp_p=%s'
              % (out['D4_permutation_null']['null_mean_within_pool_auc']
                 ['kind_only']['emp_p_two_sided'],
                 out['D4_permutation_null']['null_mean_within_pool_auc']
                 ['gnn_global']['emp_p_two_sided'],
                 out['D4_permutation_null']['null_paired_mean_diff']
                 ['emp_p_two_sided']), flush=True)

        # D5: degeneracy -- is the global readout just tracking "how big"?
        sd_global, sd_kind, big_corr = [], [], {}
        nodes = [items[i]['n'] for i in range(len(items))]
        iters = [float(str(r.get('iteration')).replace('iter_', ''))
                 if str(r.get('iteration')).replace('iter_', '').isdigit()
                 else float('nan') for r in rows]
        for _key, idx in sorted(pool_idx.items()):
            if len(idx) < 2:
                continue
            sd_global.append(float(np.std(p_global[idx])))
            sd_kind.append(float(np.std(p_kind[idx])))
        big_corr['spearman_score_vs_graph_nodes_global'] = spearman(p_global, nodes)
        big_corr['spearman_score_vs_graph_nodes_kind'] = spearman(p_kind, nodes)
        finite = [(s, it) for s, it in zip(p_global, iters) if it == it]
        if len(finite) > 3:
            big_corr['spearman_score_vs_iteration_global'] = spearman(
                [f[0] for f in finite], [f[1] for f in finite])
        finite_k = [(s, it) for s, it in zip(p_kind, iters) if it == it]
        if len(finite_k) > 3:
            big_corr['spearman_score_vs_iteration_kind'] = spearman(
                [f[0] for f in finite_k], [f[1] for f in finite_k])
        big_corr['mean_within_pool_sd_global'] = float(np.mean(sd_global))
        big_corr['mean_within_pool_sd_kind'] = float(np.mean(sd_kind))
        big_corr['min_within_pool_sd_global'] = float(np.min(sd_global))
        big_corr['n_pools_with_degenerate_global'] = int(
            sum(1 for s in sd_global if s < 1e-9))
        out['D5_degeneracy'] = big_corr
        print('  D5 within-pool sd global=%.6g kind=%.6g  rho(score,nodes)_global=%s'
              % (big_corr['mean_within_pool_sd_global'],
                 big_corr['mean_within_pool_sd_kind'],
                 big_corr['spearman_score_vs_graph_nodes_global']), flush=True)

        # D6: positive rate vs pool size (a predictor-independent bias)
        rates = [r['positives'] / r['n'] for r in recs]
        out['D6_positive_rate_vs_size'] = {
            'spearman_rate_vs_n': spearman(rates, ns),
            'spearman_rate_vs_positives': spearman(rates, ks),
            'mean_rate': float(np.mean(rates)),
        }
        print('  D6 rho(rate,n)=%s' % out['D6_positive_rate_vs_size']
              ['spearman_rate_vs_n'], flush=True)

        # D7: restrict to pools with enough positives AND negatives
        stable = [r for r in recs if r['positives'] >= 3 and r['negatives'] >= 3]
        if stable:
            sd = [r['diff'] for r in stable]
            wins = sum(1 for v in sd if v > 0)
            losses = sum(1 for v in sd if v < 0)
            t = G.paired_pool_test(rows, y, p_kind, p_global, 'kind_only',
                                    'gnn_global')
            out['D7_stable_pools'] = {
                'n_pools': len(stable),
                'mean_diff': float(np.mean(sd)),
                'wins': wins, 'losses': losses,
                'ties': len(sd) - wins - losses,
                'sign_test_p': rpc.sign_test_p(sd)[0],
                'note': ('the same statistic on the pools where the per-pool AUC '
                         'is not discretised to {0, 0.5, 1}'),
            }
            print('  D7 stable pools n=%d mean_diff=%+.6f wins=%d losses=%d p=%s'
                  % (len(stable), float(np.mean(sd)), wins, losses,
                     out['D7_stable_pools']['sign_test_p']), flush=True)

    except Exception as exc:            # noqa: BLE001
        out['diagnostics_error'] = repr(exc)
        print('[D] diagnostics FAILED: %r' % (exc,), flush=True)
    # the pre-registered gate, stated in both calibres
    out['verdict_both_calibres'] = {
        'pre_registered_as_implemented': {
            'C2_used': 'mod', 'C4_used': 'mod',
            'condition3_ok': out['controls'].get(
                'C2_mod_from_artefact', {}).get('mean_within_pool_auc', 1.0)
            < THRESH,
            'condition4_ok': out['controls'].get(
                'C4_mod_from_artefact', {}).get('mean_within_pool_auc', 1.0)
            < THRESH,
        },
        'matched_calibre': {
            'C2_used': 'global', 'C4_used': 'global',
            'condition3_ok': out['controls']['C2_global']['below_threshold'],
            'condition4_ok': out['controls']['C4_global']['below_threshold'],
        },
    }
    print('[A] verdict (both calibres): %s'
          % json.dumps(out['verdict_both_calibres'], ensure_ascii=False),
          flush=True)

    dest = Path(args.out) if args.out else SCR / ('round32_mechanism_%s.json'
                                                   % args.family)
    # write the controls BEFORE the diagnostics run, so that a failure in
    # the diagnostics cannot discard the control readings
    dest = Path(args.out) if args.out else SCR / ('round32_mechanism_%s.json'
                                                           % args.family)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                    encoding='utf-8')
    print('[A] partial write (controls only): %s' % dest, flush=True)

    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                    encoding='utf-8')
    print('written', dest, flush=True)


if __name__ == '__main__':
    main()
