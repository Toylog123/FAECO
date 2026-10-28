"""One-fold smoke test of the numpy GNN: does it train, and does the held-out
circuit get a non-degenerate ranking?  Also measures the per-epoch cost on the
FULL training set, so the full run can be budgeted instead of guessed."""
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scratch'))
import gnn_candidate_signal as g  # noqa: E402
import resolvable_positive_classifier as rpc  # noqa: E402

rows, kinds, circuits, fam_dir = g.load_rows('itc99')
tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
rows = [r for r in rows if g.num(r.get('routed_delta_wns'), None) is not None]
y = g.label_vector(rows, band, 'resolvable')
gs = g.GraphSet(rows, fam_dir)
keep = [i for i, r in enumerate(rows) if r['key'] in gs.by_key]
rows = [rows[i] for i in keep]
y = y[keep]
items = [gs.by_key[r['key']] for r in rows]

HELD = 'b01'
tr = [i for i in range(len(rows)) if rows[i].get('circuit') != HELD]
te = [i for i in range(len(rows)) if rows[i].get('circuit') == HELD]
print('rows %d (pos %d)  train %d (pos %d)  test %d (pos %d)'
      % (len(rows), int(y.sum()), len(tr), int(y[tr].sum()), len(te), int(y[te].sum())),
      flush=True)

# per-epoch cost on the FULL training set
t0 = time.time()
g.train([items[i] for i in tr], y[tr], 'mod', gs.n_types, epochs=2)
per_epoch = (time.time() - t0) / 2
print('per-epoch on %d graphs: %.3f s -> 200 epochs = %.1f s/fold, 7 folds = %.1f min'
      % (len(tr), per_epoch, per_epoch * 200, per_epoch * 200 * 7 / 60), flush=True)

for ro in ('mod', 'global'):
    t0 = time.time()
    params = g.train([items[i] for i in tr], y[tr], ro, gs.n_types, epochs=60)
    p = g.predict([items[i] for i in te], params, ro)
    a = rpc.auc(y[te], p)
    a_base = rpc.auc(y[te], np.array([rows[i].get('kind') == 'B' for i in te], dtype=float))
    print('readout=%-7s train_s=%.1f  test_auc=%.4f  (kind_B_only_auc=%.4f)  '
          'pred_std=%.4f  nan=%s'
          % (ro, time.time() - t0, a if a is not None else float('nan'), a_base,
             float(np.std(p)), bool(np.isnan(p).any())), flush=True)

# loss trajectory (does it actually fit the training data?)
for ep in (1, 10, 50, 100):
    pr = g.train(items[:400], y[:400], 'mod', gs.n_types, epochs=ep)
    loss, _, _ = g.loss_and_grad(items[:400], y[:400], pr, 'mod')
    print('epochs=%3d  mean_loss=%.4f' % (ep, loss / len(items[:400])), flush=True)
