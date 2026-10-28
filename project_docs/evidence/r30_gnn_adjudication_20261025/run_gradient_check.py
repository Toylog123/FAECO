"""Run ONLY the numeric gradient check of the numpy GNN (fast).

The backprop has to be right before any AUC it produces means anything, so this
runs the finite-difference check alone and prints the worst errors.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scratch'))
import gnn_candidate_signal as g  # noqa: E402

rows, kinds, circuits, fam_dir = g.load_rows('itc99')
tpc = json.loads((fam_dir / 'three_point_curve.json').read_text(encoding='utf-8'))
band = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')
rows = [r for r in rows if g.num(r.get('routed_delta_wns'), None) is not None]
y = g.label_vector(rows, band, 'resolvable')
gs = g.GraphSet(rows, fam_dir)
items = [gs.by_key[r['key']] for r in rows if r['key'] in gs.by_key]

report = {}
for ro in g.READOUTS:
    gc = g.gradient_check(gs, y, ro)
    report[ro] = {'max_abs_err': gc['max_abs_err'], 'max_rel_err': gc['max_rel_err'],
                  'n_checks': gc['n_checks'],
                  'worst': sorted(gc['checks'], key=lambda c: -c['abs_err'])[:6]}
    print(ro, 'max_abs_err=%.3e' % gc['max_abs_err'],
          'max_rel_err=%.3e' % gc['max_rel_err'], 'n=%d' % gc['n_checks'])

# also a timing probe: how long does one epoch of training cost?
import time
t0 = time.time()
p = g.train(items[:256], y[:256], 'mod', gs.n_types, epochs=5)
t1 = time.time()
print('5 epochs on 256 graphs: %.2f s -> per-epoch %.3f s'
      % (t1 - t0, (t1 - t0) / 5))
report['timing'] = {'five_epochs_256_graphs_s': round(t1 - t0, 2)}

(REPO / 'scratch/gnn_gradient_check.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print('written scratch/gnn_gradient_check.json')
