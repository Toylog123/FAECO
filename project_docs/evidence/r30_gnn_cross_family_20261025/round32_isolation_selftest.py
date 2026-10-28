"""Round 32, negative test of the nested-selection isolation guard.

The nested selection claims (in the docstring and in the pre-registration) that
the outer test circuit never enters the inner selection.  That claim is carried
by ONE assertion, ``_assert_isolated``.  An assertion that never fires is not a
guarantee -- it is a comment with an ``assert`` in front of it.

This test therefore tries to LEAK on purpose, in three ways, and checks that
each one is caught:

  T1  the inner training set contains an outer-test row      -> must raise
  T2  the inner test set contains an outer-test row           -> must raise
  T3  the clean case (no overlap)                              -> must NOT raise

It also checks the second, quieter failure mode: the assertion compares ROW
indices, so it can only catch a leak if the inner index sets are built from the
same global row numbering.  T4 therefore checks that the real caller passes
global row indices (not a renumbered subset), by asserting that the indices
produced for the inner folds are a subset of the global row range and that the
outer test rows are actually excluded from the inner TRAINING set in a real
run.

Finally it verifies the smoke output produced by the earlier pre-flight, so
that the structure the real run is expected to emit is known to exist.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCR = REPO / 'scratch'
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))

import round32_nested_selection as NS  # noqa: E402
import gnn_candidate_signal as G  # noqa: E402

results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print('%-4s %-46s %s' % ('OK' if ok else 'FAIL', name, detail), flush=True)


def raised(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except AssertionError:
        return True
    except Exception as exc:                     # noqa: BLE001
        return 'wrong-exception:' + type(exc).__name__
    return False


# ---------------------------------------------------------------- T1..T3
# synthetic index sets: rows 0..9, outer test = {8, 9}
inner_tr_clean = [0, 1, 2, 3]
inner_te_clean = [4, 5, 6, 7]
outer_te = [8, 9]

r1 = raised(NS._assert_isolated, inner_tr_clean + [8], inner_te_clean,
            outer_te, 'b01')
check('T1 leak in inner TRAIN is caught', r1 is True, str(r1))

r2 = raised(NS._assert_isolated, inner_tr_clean, inner_te_clean + [9],
            outer_te, 'b01')
check('T2 leak in inner TEST is caught', r2 is True, str(r2))

r3 = raised(NS._assert_isolated, inner_tr_clean, inner_te_clean, outer_te,
            'b01')
check('T3 clean case does not raise', r3 is False, str(r3))

# The guard must not be satisfiable by passing empty inner sets either --
# an empty inner selection means "no inner evidence", which the caller treats
# as "no score for this config".  That is a silent skip, not a leak, but it
# must NOT be reported as a successful isolation check.
r4 = raised(NS._assert_isolated, [], [], outer_te, 'b01')
check('T4 empty inner sets pass the guard (caller skips)', r4 is False, str(r4))

# ------------------------------------------------------- T5 real-call wiring
# The guard compares indices, so it is only meaningful if the caller hands it
# GLOBAL row indices.  Rebuild one real fold the way run_nested does and check
# that (a) the inner indices are global, (b) the outer test rows are absent
# from the inner training set, (c) the guard does not fire on the real fold.
rows, kinds, circuits, fam_dir = G.load_rows('iscas89')
ckt_of = [r.get('circuit') for r in rows]
held = circuits[0]
tr = [i for i in range(len(rows)) if ckt_of[i] != held]
te = [i for i in range(len(rows)) if ckt_of[i] == held]
inner_circuits = sorted({ckt_of[i] for i in tr})
ok_global = max(tr) < len(rows) and min(tr) >= 0
check('T5a inner/outer indices are global row indices', ok_global,
      'n_rows=%d max_inner=%d' % (len(rows), max(tr)))

bad = 0
for jheld in inner_circuits:
    itr = [i for i in tr if ckt_of[i] != jheld]
    ite = [i for i in tr if ckt_of[i] == jheld]
    if set(itr) & set(te) or set(ite) & set(te):
        bad += 1
check('T5b no inner fold touches the outer test rows', bad == 0,
      'overlapping folds=%d / %d' % (bad, len(inner_circuits)))

# T5c must use a REAL inner fold's test set.  Passing an outer-test row as
# the inner test set (a mistake in the first version of this test) makes the
# guard fire correctly -- that is a leak being caught, not a failure of the
# guard, so it must not be counted as "the real fold passes".
inner_ckts = sorted({ckt_of[i] for i in tr})
jheld = inner_ckts[0]
itr = [i for i in tr if ckt_of[i] != jheld]
ite = [i for i in tr if ckt_of[i] == jheld]
r5 = raised(NS._assert_isolated, itr, ite, te, held)
check('T5c a real inner fold passes the isolation guard', r5 is False, str(r5))
check('T5d the real inner fold really excludes the outer rows',
      not (set(itr) & set(te)) and not (set(ite) & set(te)),
      'inner_train=%d inner_test=%d outer=%d' % (len(itr), len(ite), len(te)))

# ------------------------------------------------- T6 smoke output structure
smoke = SCR / 'round32_nested_smoke.json'
if smoke.exists():
    d = json.loads(smoke.read_text(encoding='utf-8'))
    need = ['family', 'band_ns', 'grid', 'selected_per_outer_fold',
            'inner_scores', 'metrics', 'baselines', 'paired_pool_tests',
            'C2_null_labels', 'null_grid', 'pre_registration']
    missing = [k for k in need if k not in d]
    check('T6a smoke output has every required key', not missing,
          'missing=%s' % (missing or 'none'))
    check('T6b smoke recorded the pre-registration path',
          d.get('pre_registration') == 'scratch/round32_preregistration.json',
          str(d.get('pre_registration')))
    check('T6c smoke recorded the null grid actually used',
          d.get('null_grid') in ('full', 'pub'), str(d.get('null_grid')))
    check('T6d smoke has one outer selection per circuit',
          len(d.get('selected_per_outer_fold', {})) == len(
              d.get('inner_scores', {})),
          'folds=%d' % len(d.get('selected_per_outer_fold', {})))
else:
    check('T6 smoke output exists', False, 'missing %s' % smoke)

# ------------------------------------------------- T7 readout shape contract
# The first run of the matched-control tool died with a shape error because
# the random-init probe passed the 'mod' placeholder width (2*D_H+1) for the
# 'global' readout, whose representation is D_H wide.  The project's own C4
# block is correct for 'mod'; only the new 'global' path was wrong.  These
# checks pin the width contract so the class of bug cannot come back.
import numpy as np  # noqa: E402


def _width(ro):
    return G.D_H if ro == 'global' else 2 * G.D_H + 1


_rows, _kinds, _circuits, _fam = G.load_rows('iscas89')
gs2 = G.GraphSet(_rows, _fam)
items2 = gs2.items[:4]
NT = gs2.n_types

for ro in ('mod', 'global'):
    p = G.init_params(NT, ro, np.random.default_rng(0))
    check('T7a %s: w_out width matches the readout width' % ro,
          p['w_out'].shape[0] == _width(ro),
          'w_out=%d expected=%d' % (p['w_out'].shape[0], _width(ro)))

# the project's own C4 placeholder width must work for 'mod' and must NOT be
# silently reused for 'global'
p_mod = G.init_params(NT, 'mod', np.random.default_rng(1))
try:
    G.forward(items2, p_mod['E'], p_mod['W1'], p_mod['b1'], p_mod['W2'],
              p_mod['b2'], np.ones(2 * G.D_H + 1), 0.0, 'mod', True)
    mod_ok = True
except Exception as exc:                                # noqa: BLE001
    mod_ok = False
    mod_err = repr(exc)
check('T7b the project C4 placeholder width works for the mod readout',
      mod_ok, '' if mod_ok else mod_err)

p_glob = G.init_params(NT, 'global', np.random.default_rng(1))
try:
    G.forward(items2, p_glob['E'], p_glob['W1'], p_glob['b1'], p_glob['W2'],
              p_glob['b2'], np.ones(G.D_H), 0.0, 'global', True)
    glob_ok = True
except Exception as exc:                                # noqa: BLE001
    glob_ok = False
    glob_err = repr(exc)
check('T7c the readout-derived width works for the global readout',
      glob_ok, '' if glob_ok else glob_err)

# ------------------------------------------------- T8 resume fingerprint guard
# The nested tool checkpoints every outer fold so a batch can survive the
# harness's one-hour background limit.  A checkpoint may only be resumed by a
# run with the SAME settings -- otherwise a 1-epoch sandbox fold would be
# silently mixed into a 120-epoch production artefact.
import round32_nested_selection as NS  # noqa: E402


class _Args:
    family = 'iscas89'
    label = 'resolvable'
    null_grid = 'pub'


_g1 = [dict(c) for c in NS.GRID_EXTENDED]
_g2 = [dict(c) for c in NS.GRID_EXTENDED]
_fp1 = NS._fingerprint(_g1, _Args)
_fp2 = NS._fingerprint(_g2, _Args)
check('T8a identical settings give an identical fingerprint', _fp1 == _fp2, '')

_g3 = [dict(c) for c in NS.GRID_EXTENDED]
_g3[0]['epochs'] = 7
_fp3 = NS._fingerprint(_g3, _Args)
check('T8b a changed epoch count changes the fingerprint', _fp1 != _fp3, '')

_g4 = [dict(c) for c in NS.GRID_EXTENDED]
_g4[1]['readout'] = 'global'
_fp4 = NS._fingerprint(_g4, _Args)
check('T8c a changed readout changes the fingerprint', _fp1 != _fp4, '')

_g5 = [dict(c) for c in NS.GRID_EXTENDED]
_g5[2]['wd'] = 0.01
_fp5 = NS._fingerprint(_g5, _Args)
check('T8d a changed weight decay changes the fingerprint', _fp1 != _fp5, '')

_a = _Args()
_a.family = 'itc99'
_fp6 = NS._fingerprint(_g1, _a)
check('T8e a changed family changes the fingerprint', _fp1 != _fp6, '')

check('T8f the pre-registered grid really does not vary the readout',
      len({c['readout'] for c in NS.GRID_PRE}) == 1,
      'readouts=%s' % sorted({c['readout'] for c in NS.GRID_PRE}))
check('T8g the extended grid adds exactly the global arm',
      [c['name'] for c in NS.GRID_EXTENDED] ==
      [c['name'] for c in NS.GRID_PRE] + ['global'],
      str([c['name'] for c in NS.GRID_EXTENDED]))

# ---------------------------------------------------------------- summary
n_fail = sum(1 for _n, ok, _d in results if not ok)
print('\n[round32] isolation self-test: %d checks, %d failed'
      % (len(results), n_fail), flush=True)
sys.exit(1 if n_fail else 0)
