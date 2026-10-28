"""GNN-level adjudication of "graph structure carries no candidate-level physical
signal" (LOG-20261024-24), on the FINAL routed band.

WHY
---
LOG-24 showed, with the project's own classifier tool, that the gate-level
graph's SCALAR SUMMARIES carry no candidate-level signal beyond the trivial
baseline (within-pool AUC: kind_only 0.555062 vs best graph-feature set
0.561297), and stated its own boundary: "the features are scalar summaries of
the gate-level graph, NOT a GNN".  A negative result about summaries does not
transfer to a message-passing encoder.  This tool performs the transfer.

No deep-learning framework exists in this environment (torch / dgl / sklearn /
scipy absent), so the GNN is written directly in numpy.  The graphs are tiny
(14..188 nodes; 87 441 nodes in total), so a dense numpy implementation is both
exact and fast: graphs are padded to the batch maximum and the propagation is a
single batched einsum.

THE DESIGN POINT THAT DECIDES THE EXPERIMENT
---------------------------------------------
A candidate netlist is the iteration base plus ONE modified cell, so the whole
graph is nearly constant inside a candidate pool.  A global mean-pool readout is
therefore almost constant within a pool and cannot rank the candidates of one
pool -- exactly what a candidate generator must do.  The informative readout is
the MODIFIED CELL's embedding and how it differs from the graph average.  Both
are reported:

    readout 'global'   mean over all nodes                (the naive choice)
    readout 'mod'      concat[ h_mod , h_mod - mean_all ]  (the headline)

CONTROLS (an instrument that cannot fail is not an instrument)
-------------------------------------------------------------
  C1  numeric gradient check against finite differences
  C2  null labels permuted inside the pools -> AUC must land at ~0.5
  C3  no-propagation variant (A = I)        -> isolates the message passing
  C4  random-init encoder + ridge probe     -> structure without label fitting
  C5  kind_only / structural baselines from the project's own tool

Every number is produced under the SAME leave-one-circuit-out protocol and the
SAME AUC / pool-bootstrap code as the tool that produced the baselines.
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))
import resolvable_positive_classifier as rpc  # noqa: E402
from surrogate_prototype import num  # noqa: E402

SEED = 20261025
D_E = 8
D_H = 16
EPOCHS = 200
LR = 0.01
WD = 1e-3
BATCH = 64
READOUTS = ('mod', 'global')
N_NODE_NUM = 6
N_CONST = 2
D0 = D_E + N_NODE_NUM + N_CONST


# ===================================================================== data

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
    return out, kinds, circuits, fam_dir


def label_vector(rows, band, label_mode):
    col = rpc.TARGET_COL['routed']
    if label_mode == 'gain':
        return np.array([1.0 if num(r.get(col), -1e18) > band else 0.0 for r in rows])
    if label_mode == 'harm':
        return np.array([1.0 if num(r.get(col), 1e18) < -band else 0.0 for r in rows])
    return np.array([1.0 if abs(num(r.get(col), -1e18)) > band else 0.0 for r in rows])


# ================================================================== features

class GraphSet:
    """Every candidate's graph: adjacency, node features, modified-cell index."""

    def __init__(self, rows, fam_dir):
        gdir = fam_dir / 'graphs'
        self.type_vocab = {}
        self.items = []
        self.by_key = {}
        for r in rows:
            p = gdir / r.get('circuit') / f'{r.get("key")}.json'
            if not p.exists():
                continue
            d = json.loads(p.read_text(encoding='utf-8'))
            nodes = d['nodes']
            n = len(nodes)
            idx = {nd['id']: i for i, nd in enumerate(nodes)}
            A = np.zeros((n, n), dtype=np.float64)
            for e in d['edges']:
                i, j = idx.get(e['src']), idx.get(e['dst'])
                if i is not None and j is not None:
                    A[i, j] = 1.0
            A = A + np.eye(n)
            Ahat = A / np.maximum(A.sum(axis=1, keepdims=True), 1e-12)

            types = []
            for nd in nodes:
                t = nd['type']
                if t not in self.type_vocab:
                    self.type_vocab[t] = len(self.type_vocab)
                types.append(self.type_vocab[t])
            types = np.array(types, dtype=np.int64)

            depth = max(1, d.get('depth') or 1)
            ncells = max(1, n)
            numf = np.zeros((n, N_NODE_NUM), dtype=np.float64)
            for i, nd in enumerate(nodes):
                numf[i, 0] = min(nd.get('fanin', 0) / 8.0, 1.0)
                numf[i, 1] = min(nd.get('fanout', 0) / 16.0, 1.0)
                numf[i, 2] = (nd.get('level', 0) or 0) / depth
                numf[i, 3] = (nd.get('cone_down', 0) or 0) / ncells
                numf[i, 4] = 1.0 if nd.get('is_ff') else 0.0
                numf[i, 5] = 1.0 if nd.get('id') == r.get('instance') else 0.0
            const = np.repeat(np.array([n / 200.0, depth / 10.0])[None, :], n, axis=0)

            it = {'key': r.get('key'), 'circuit': r.get('circuit'),
                  'Ahat': Ahat, 'types': types, 'numf': numf, 'const': const,
                  'mod_idx': idx.get(r.get('instance'), -1), 'n': n}
            self.items.append(it)
            self.by_key[it['key']] = it
        self.n_types = max(1, len(self.type_vocab))


# ===================================================================== model

def _pack(items, E, use_A, use_types=True):
    B = len(items)
    n_max = max(it['n'] for it in items)
    X = np.zeros((B, n_max, D0))
    A = np.zeros((B, n_max, n_max))
    mask = np.zeros((B, n_max))
    midx = np.full(B, -1, dtype=np.int64)
    for bi, it in enumerate(items):
        n = it['n']
        if use_types:
            X[bi, :n, :D_E] = E[it['types']]
        X[bi, :n, D_E:D_E + N_NODE_NUM] = it['numf']
        X[bi, :n, D_E + N_NODE_NUM:] = it['const']
        A[bi, :n, :n] = it['Ahat'] if use_A else np.eye(n)
        mask[bi, :n] = 1.0
        midx[bi] = it['mod_idx']
    return X, A, mask, midx


def forward(items, E, W1, b1, W2, b2, w_out, b_out, readout, use_A=True,
            use_types=True):
    X, A, mask, midx = _pack(items, E, use_A, use_types)
    m3 = mask[:, :, None]
    # np.matmul on a stacked (B, n, n) array dispatches to BLAS; np.einsum does
    # not (measured 8-14x slower for these shapes, numerically identical).
    Z1 = np.matmul(A, X) @ W1 + b1
    H1 = np.maximum(Z1, 0.0) * m3
    Z2 = np.matmul(A, H1) @ W2 + b2
    H2 = np.maximum(Z2, 0.0) * m3
    cnt = np.maximum(mask.sum(axis=1), 1.0)[:, None]
    mean_all = (H2 * m3).sum(axis=1) / cnt
    h_mod = np.zeros((H2.shape[0], H2.shape[2]))
    for bi in range(H2.shape[0]):
        if midx[bi] >= 0:
            h_mod[bi] = H2[bi, midx[bi]]
    has = (midx >= 0).astype(np.float64)[:, None]
    if readout == 'global':
        R = mean_all
    else:
        R = np.concatenate([h_mod, h_mod - mean_all, has], axis=1)
    logit = R @ w_out + b_out
    cache = {'X': X, 'A': A, 'mask': mask, 'm3': m3, 'midx': midx, 'Z1': Z1,
             'H1': H1, 'Z2': Z2, 'H2': H2, 'mean_all': mean_all, 'h_mod': h_mod,
             'has': has, 'R': R, 'items': items}
    return logit, cache


def backward(cache, grad_logit, W1, W2, w_out, readout):
    X = cache['X']; A = cache['A']; m3 = cache['m3']; midx = cache['midx']
    Z1 = cache['Z1']; H1 = cache['H1']; Z2 = cache['Z2']; H2 = cache['H2']
    dH2 = np.zeros_like(H2)
    if readout == 'global':
        cnt = np.maximum(cache['mask'].sum(axis=1), 1.0)[:, None]
        dmean = (grad_logit[:, None] * w_out[None, :]) / cnt
        dH2 = np.repeat(dmean[:, None, :], H2.shape[1], axis=1) * m3
    else:
        dR = grad_logit[:, None] * w_out[None, :]
        d_h_mod = dR[:, :D_H]
        d_diff = dR[:, D_H:2 * D_H]
        for bi in range(H2.shape[0]):
            if midx[bi] >= 0:
                dH2[bi, midx[bi]] += d_h_mod[bi] + d_diff[bi]
        cnt = np.maximum(cache['mask'].sum(axis=1), 1.0)[:, None]
        dmean = -d_diff / cnt
        dH2 += np.repeat(dmean[:, None, :], H2.shape[1], axis=1) * m3

    dZ2 = (dH2 * (Z2 > 0)) * m3
    dZ2x = np.matmul(np.swapaxes(A, 1, 2), dZ2)
    dW2 = np.matmul(np.swapaxes(H1, 1, 2), dZ2x).sum(axis=0)
    db2 = dZ2x.sum(axis=(0, 1))
    dH1 = dZ2x @ W2.T
    dZ1 = (dH1 * (Z1 > 0)) * m3
    dZ1x = np.matmul(np.swapaxes(A, 1, 2), dZ1)
    dW1 = np.matmul(np.swapaxes(X, 1, 2), dZ1x).sum(axis=0)
    db1 = dZ1x.sum(axis=(0, 1))
    dX = dZ1x @ W1.T

    dE = np.zeros_like(cache['E_used'])
    for bi, it in enumerate(cache['items']):
        n = int(cache['mask'][bi].sum())
        if n:
            np.add.at(dE, it['types'], dX[bi, :n, :D_E])

    dw_out = (grad_logit[:, None] * cache['R']).sum(axis=0)
    db_out = float(grad_logit.sum())
    return {'E': dE, 'W1': dW1, 'b1': db1, 'W2': dW2, 'b2': db2,
            'w_out': dw_out, 'b_out': db_out}


def loss_and_grad(items, y, params, readout, use_A=True, use_types=True):
    logit, cache = forward(items, params['E'], params['W1'], params['b1'],
                            params['W2'], params['b2'], params['w_out'],
                            params['b_out'], readout, use_A, use_types)
    cache['E_used'] = params['E']
    p = 1.0 / (1.0 + np.exp(-np.clip(logit, -30, 30)))
    eps = 1e-12
    loss = float(-np.sum(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)))
    grad_logit = (p - y) / len(y)
    grads = backward(cache, grad_logit, params['W1'], params['W2'],
                     params['w_out'], readout)
    if not use_types:
        grads['E'] = np.zeros_like(grads['E'])
    return loss, grads, logit


def init_params(n_types, readout, rng):
    R_DIM = D_H if readout == 'global' else 2 * D_H + 1
    return {
        'E': rng.normal(0, 0.1, size=(n_types, D_E)),
        'W1': rng.normal(0, 0.1, size=(D0, D_H)),
        'b1': np.zeros(D_H),
        'W2': rng.normal(0, 0.1, size=(D_H, D_H)),
        'b2': np.zeros(D_H),
        'w_out': np.zeros(R_DIM),
        'b_out': np.zeros(()),
    }


def train(items, y, readout, n_types, seed=SEED, epochs=EPOCHS, lr=LR, wd=WD,
          use_A=True, batch=BATCH, use_types=True):
    rng = np.random.default_rng(seed)
    params = init_params(n_types, readout, rng)
    if not use_types:
        params['E'] = np.zeros_like(params['E'])
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(v) for k, v in params.items()}
    b1t, b2t, eps = 0.9, 0.999, 1e-8
    order = np.arange(len(items))
    step = 0
    for ep in range(epochs):
        rng.shuffle(order)
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            bitems = [items[i] for i in idx]
            by = y[idx]
            _loss, grads, _ = loss_and_grad(bitems, by, params, readout, use_A,
                                            use_types)
            step += 1
            for k in params:
                g = grads[k]
                if k in ('W1', 'W2', 'w_out', 'E'):
                    g = g + wd * params[k]
                m[k] = b1t * m[k] + (1 - b1t) * g
                v[k] = b2t * v[k] + (1 - b2t) * (g * g)
                mh = m[k] / (1 - b1t ** step)
                vh = v[k] / (1 - b2t ** step)
                params[k] = params[k] - lr * mh / (np.sqrt(vh) + eps)
            if not use_types:
                params['E'] = np.zeros_like(params['E'])
    return params


def predict(items, params, readout, use_A=True, use_types=True):
    logit, _ = forward(items, params['E'], params['W1'], params['b1'],
                        params['W2'], params['b2'], params['w_out'],
                        params['b_out'], readout, use_A, use_types)
    return logit


# ============================================================ gradient check

def gradient_check(gs, y, readout, rng_seed=7):
    rng = np.random.default_rng(rng_seed)
    items = gs.items[:6]
    yy = np.asarray(y[:6], dtype=float)
    params = init_params(gs.n_types, readout, rng)
    _l0, grads, _ = loss_and_grad(items, yy, params, readout)
    eps = 1e-6
    checks = []
    for name in ('W1', 'W2', 'w_out', 'E', 'b1', 'b2'):
        arr = params[name]
        flat = arr.reshape(-1)
        picks = rng.choice(flat.size, size=min(flat.size, 5), replace=False)
        for p in picks:
            old = float(flat[p])
            flat[p] = old + eps
            lp, _, _ = loss_and_grad(items, yy, params, readout)
            flat[p] = old - eps
            lm, _, _ = loss_and_grad(items, yy, params, readout)
            flat[p] = old
            num_g = (lp - lm) / (2 * eps)
            # loss_and_grad returns the SUM loss and the MEAN-loss gradient, so
            # the finite difference of the sum has to be scaled by 1/n to be
            # compared like for like.
            num_g = num_g / len(yy)
            ana_g = float(grads[name].reshape(-1)[p])
            checks.append({'param': name, 'index': int(p),
                           'numeric': float(num_g), 'analytic': ana_g,
                           'abs_err': float(abs(num_g - ana_g)),
                           'rel_err': float(abs(num_g - ana_g) /
                                            max(1e-9, abs(num_g) + abs(ana_g)))})
    return {'max_abs_err': max(c['abs_err'] for c in checks),
            'max_rel_err': max(c['rel_err'] for c in checks),
            'n_checks': len(checks), 'checks': checks}


# ================================================================ reporting

def pool_metrics(rows, y, preds):
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    pooled = rpc.auc(y, preds)
    pm = np.zeros(len(rows))
    for idx in pool_idx.values():
        pm[idx] = float(preds[idx].mean())
    pooled_pm = rpc.auc(y, pm)
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
    return {'pooled_auc': pooled, 'pooled_auc_pool_mean_only': pooled_pm,
            'mean_within_pool_auc': wp, 'mean_within_pool_auc_ci95': [wlo, whi],
            'n_pools_used': wn, 'per_pool_auc': per_pool}


def paired_pool_test(rows, y, preds_a, preds_b, name_a, name_b):
    """Per-pool paired comparison of two predictors (same pools)."""
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    diffs, wins, losses = [], 0, 0
    for key, idx in sorted(pool_idx.items()):
        aa = rpc.auc(y[idx], preds_a[idx])
        bb = rpc.auc(y[idx], preds_b[idx])
        if aa is None or bb is None:
            continue
        diffs.append(bb - aa)
        if bb > aa:
            wins += 1
        elif bb < aa:
            losses += 1
    p, pos, neg = rpc.sign_test_p(diffs)
    return {'name_a': name_a, 'name_b': name_b, 'n_pools': len(diffs),
            'mean_diff': float(np.mean(diffs)) if diffs else None,
            'b_wins': wins, 'b_losses': losses, 'b_ties': len(diffs) - wins - losses,
            'sign_test_p': p}


# ==================================================================== main

def run_loco(rows, y, items, circuits, readout, use_A, n_types, seed=SEED,
             epochs=EPOCHS, wd=WD, use_types=True):
    preds = np.zeros(len(rows))
    for held in circuits:
        tr = [i for i in range(len(rows)) if rows[i].get('circuit') != held]
        te = [i for i in range(len(rows)) if rows[i].get('circuit') == held]
        if len(set(y[tr])) < 2 or not te:
            continue
        params = train([items[i] for i in tr], y[tr], readout, n_types,
                       seed=seed, epochs=epochs, wd=wd, use_A=use_A,
                       use_types=use_types)
        preds[te] = predict([items[i] for i in te], params, readout, use_A=use_A,
                            use_types=use_types)
    return preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='itc99')
    ap.add_argument('--label', default='resolvable')
    ap.add_argument('--epochs', type=int, default=EPOCHS)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rows, kinds, circuits, fam_dir = load_rows(args.family)
    tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
    band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    rows = [r for r in rows if num(r.get('routed_delta_wns'), None) is not None]
    y = label_vector(rows, band, args.label)

    gs = GraphSet(rows, fam_dir)
    items = [gs.by_key[r['key']] for r in rows if r['key'] in gs.by_key]
    keep = [i for i, r in enumerate(rows) if r['key'] in gs.by_key]
    rows = [rows[i] for i in keep]
    y = y[keep]
    items = [gs.by_key[r['key']] for r in rows]

    out = {
        'family': args.family, 'label_mode': args.label, 'band_ns': band,
        'n_rows': len(rows), 'n_positive': int(y.sum()),
        'n_graph_nodes': sum(it['n'] for it in items),
        'n_graphs_without_modified_cell': sum(1 for it in items if it['mod_idx'] < 0),
        'hyperparams': {'D_E': D_E, 'D_H': D_H, 'epochs': args.epochs, 'lr': LR,
                        'wd': WD, 'batch': BATCH, 'seed': SEED,
                        'protocol': 'leave-one-circuit-out (same as the project tool)'},
        'note': ('the GNN is numpy (no torch/dgl/sklearn in this environment); '
                 'graphs are padded to the batch maximum, the propagation is one '
                 'batched einsum; no hyperparameter was selected on the held-out '
                 'circuit (the setting is fixed in advance)'),
    }

    # ---- C1 gradient check
    out['C1_gradient_check'] = {ro: gradient_check(gs, y, ro) for ro in READOUTS}

    # ---- C5 baselines from the project's own tool
    base = {}
    base_preds = {}
    for fs in ('kind_only', 'structural'):
        p, _ = rpc.oof_predict(rows, kinds, circuits, y, fs, model='ridge')
        base_preds[fs] = p
        base[fs] = pool_metrics(rows, y, p)
    out['C5_baselines_from_project_tool'] = base
    for fs, m in base.items():
        print('  %-20s pooled=%.6f  within_pool=%s  [CI %s]'
              % (fs, m['pooled_auc'] if m['pooled_auc'] is not None else float('nan'),
                 ('%.6f' % m['mean_within_pool_auc'])
                 if m['mean_within_pool_auc'] is not None else '-',
                 m['mean_within_pool_auc_ci95']), flush=True)

    # ---- the GNN and its variants
    gnn = {}
    gnn_preds = {}
    variants = (
        ('gnn_mod', 'mod', True, True),
        ('gnn_global', 'global', True, True),
        ('gnn_no_prop_mod', 'mod', False, True),
        ('gnn_no_types_mod', 'mod', True, False),
    )
    for name, ro, use_A, use_types in variants:
        t0 = time.time()
        p = run_loco(rows, y, items, circuits, ro, use_A, gs.n_types,
                     epochs=args.epochs, use_types=use_types)
        gnn_preds[name] = p
        m = pool_metrics(rows, y, p)
        m['train_seconds'] = round(time.time() - t0, 1)
        m['readout'] = ro
        m['propagation'] = use_A
        m['cell_type_embedding'] = use_types
        gnn[name] = m
        print('  %-20s pooled=%.6f  within_pool=%s  (%.0f s)'
              % (name, m['pooled_auc'] if m['pooled_auc'] is not None else float('nan'),
                 ('%.6f' % m['mean_within_pool_auc'])
                 if m['mean_within_pool_auc'] is not None else '-',
                 m['train_seconds']), flush=True)
    out['gnn'] = gnn

    # ---- C2 null labels (permuted inside the pools)
    rng = np.random.default_rng(SEED + 5)
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    y_null = y.copy()
    for _idx in pool_idx.values():
        perm = rng.permutation(len(_idx))
        y_null[_idx] = y[_idx][perm]
    null_p = run_loco(rows, y_null, items, circuits, 'mod', True, gs.n_types,
                      epochs=args.epochs)
    out['C2_null_labels'] = pool_metrics(rows, y, null_p)
    print('  %-20s pooled=%.6f  within_pool=%s'
          % ('C2_null_labels', out['C2_null_labels']['pooled_auc'],
             ('%.6f' % out['C2_null_labels']['mean_within_pool_auc'])
             if out['C2_null_labels']['mean_within_pool_auc'] is not None else '-'),
          flush=True)

    # ---- C4 random-init encoder + ridge probe
    rng2 = np.random.default_rng(SEED + 9)
    params0 = init_params(gs.n_types, 'mod', rng2)
    for k in ('W1', 'W2'):
        params0[k] = params0[k] + rng2.normal(0, 0.1, size=params0[k].shape)
    emb = []
    for s in range(0, len(items), 64):
        chunk = items[s:s + 64]
        _, cache = forward(chunk, params0['E'], params0['W1'], params0['b1'],
                           params0['W2'], params0['b2'], np.ones(2 * D_H + 1),
                           0.0, 'mod', True)
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
    out['C4_random_init_encoder_probe'] = pool_metrics(rows, y, rp)

    # ---- paired pool test: GNN vs the scalar-summary baseline
    out['paired_pool_tests'] = []
    for key in ('gnn_mod', 'gnn_global', 'gnn_no_prop_mod', 'gnn_no_types_mod'):
        if key in gnn_preds:
            out['paired_pool_tests'].append(
                paired_pool_test(rows, y, base_preds['structural'], gnn_preds[key],
                                 'structural', key))
            out['paired_pool_tests'].append(
                paired_pool_test(rows, y, base_preds['kind_only'], gnn_preds[key],
                                 'kind_only', key))
    for t in out['paired_pool_tests']:
        print('  paired %-10s vs %-20s mean_diff=%s  wins %s / losses %s  p=%s'
              % (t['name_a'], t['name_b'],
                 ('%.6f' % t['mean_diff']) if t['mean_diff'] is not None else '-',
                 t['b_wins'], t['b_losses'], t['sign_test_p']), flush=True)

    dest = Path(args.out) if args.out else REPO / 'scratch/gnn_candidate_signal.json'
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', dest)


if __name__ == '__main__':
    main()
