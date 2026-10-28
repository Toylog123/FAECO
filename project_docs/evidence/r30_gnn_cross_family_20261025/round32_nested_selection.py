"""Round 32, component F: nested hyper-parameter selection for the GNN.

LOG-20261025-29 fixed every hyper-parameter in advance and said so: "no
hyperparameter was selected on the held-out circuit (the setting is fixed in
advance)".  That leaves the honest objection open -- maybe a tuned GNN does
have room.  This tool closes it the only way that counts:

  outer fold  : leave-one-circuit-out (the project's protocol)
  inner folds : leave-one-circuit-out over the TRAINING circuits only
  inner score : the same headline readout as the outer one
                (mean within-pool AUC), so the selection optimises exactly
                what the verdict is read on
  selected    : the config with the best inner score (ties -> the earlier one
                in the grid order), retrained on ALL training circuits and
                applied to the outer test circuit

The outer test circuit never enters the inner selection.  That is asserted in
code (see ``_assert_isolated``), not merely intended.

TWO SELECTIONS FROM ONE RUN
----------------------------
The pre-registered grid (scratch/round32_preregistration.json) lists four
configurations and its scope sentence claims that the nested selection covers
four dimensions: readout, propagation, cell-type embedding and weight decay.
The four listed configurations all fix the readout at 'mod', so the grid as
written does NOT vary the readout -- the scope sentence and the grid disagree.
That disagreement is a defect in the pre-registration's description, not a
licence to re-tune anything, and it is recorded as an open issue.

The replication meanwhile found that the strongest variant is ``gnn_global``
(readout='global').  A grid that structurally cannot reach the best-known
architecture cannot answer "does tuning open space", so this tool runs the
five-configuration grid (the four pre-registered ones plus 'global' appended
LAST, so the pre-registered tie-break order is untouched) and reports TWO
selections:

  'pre'      : the best of the FOUR pre-registered configurations only.
               This is the pre-registered verdict, unchanged.
  'extended' : the best of all five.

Both share the same inner scores, so the extra cost is one extra training per
outer fold, not a whole extra run.

The 'extended' arm is informed by the replication's readout, i.e. it is
post-hoc.  Its bias direction is therefore FIXED AND STATED: adding an arm
that can only make the negative conclusion harder to sustain cannot be
"fishing" for a positive result -- it is an adversarial arm.  A positive
verdict from the extended arm therefore still has to survive the same
significance gate and the same controls as the pre-registered one.

The null-label control (labels permuted inside the pools) runs under the same
outer protocol; the grid used for it is recorded in the output.
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
import gnn_candidate_signal as G  # noqa: E402

# The pre-registered grid, exactly as written before any round-32 run.
GRID_PRE = [
    {'name': 'pub', 'readout': 'mod', 'propagation': True, 'types': True,
     'epochs': 120, 'wd': 0.001},
    {'name': 'reg', 'readout': 'mod', 'propagation': True, 'types': True,
     'epochs': 120, 'wd': 0.01},
    {'name': 'noprop', 'readout': 'mod', 'propagation': False, 'types': True,
     'epochs': 120, 'wd': 0.001},
    {'name': 'notypes', 'readout': 'mod', 'propagation': True, 'types': False,
     'epochs': 120, 'wd': 0.001},
]

# The adversarial arm, appended LAST so the pre-registered tie-break order is
# preserved for the four configurations above.
GRID_EXTENDED = GRID_PRE + [
    {'name': 'global', 'readout': 'global', 'propagation': True, 'types': True,
     'epochs': 120, 'wd': 0.001},
]

PRE_NAMES = [c['name'] for c in GRID_PRE]
ALL_NAMES = [c['name'] for c in GRID_EXTENDED]


def _flush_print(*args, **kwargs):
    """FLUSHED_LOG: progress must reach the log file immediately.

    stdout is redirected to a file in every batch run, and Python block-
    buffers that stream; without an explicit flush the log stays empty for
    tens of minutes even though the process is working, which silently breaks
    the "watch the log to confirm progress" discipline.
    """
    kwargs['flush'] = True
    print(*args, **kwargs)


FINGERPRINT = {}          # FINGERPRINT_MARK: the settings a run was made with


def _fingerprint(grid, args):
    """FINGERPRINT_MARK: identify the settings a checkpoint belongs to.

    A checkpoint may only be resumed by a run with the SAME grid (names,
    readout, propagation, types, weight decay, epochs).  Without this, a
    sandbox checkpoint (1 epoch) could be resumed by the production run
    (120 epochs) and the two would be silently mixed.
    """
    return {'grid': [{'name': c['name'], 'readout': c['readout'],
                      'propagation': c['propagation'], 'types': c['types'],
                      'wd': c['wd'], 'epochs': c['epochs']} for c in grid],
            'family': args.family, 'label': args.label,
            'null_grid': args.null_grid}


def _checkpoint(path, selected, inner_log, preds, note, folds_done):
    """RESUME_MARK: write the per-fold state to disk so a crash keeps the work.

    The out-of-fold prediction vectors are stored next to the JSON as a .npy,
    because they are what the final metrics are computed from and they cannot
    be recomputed without redoing every fold.
    """
    import json as _json
    try:
        blob = {'note': note,
                'fingerprint': FINGERPRINT,
                'selected_per_outer_fold': selected,
                'inner_scores': inner_log,
                'folds_done': sorted(folds_done)}
        Path(path).write_text(_json.dumps(blob, indent=2, ensure_ascii=False),
                              encoding='utf-8')
        np.savez(str(path) + '.preds.npz',
                 **{k: np.asarray(v) for k, v in preds.items()})
    except Exception:                                   # noqa: BLE001
        pass


def _load_checkpoint(path):
    """RESUME_MARK: read a checkpoint back; returns None if there is none."""
    import json as _json
    p = Path(path)
    if not p.exists():
        return None
    try:
        blob = _json.loads(p.read_text(encoding='utf-8'))
    except Exception:                                   # noqa: BLE001
        return None
    preds = {}
    npz = Path(str(path) + '.preds.npz')
    if npz.exists():
        try:
            with np.load(npz) as z:
                preds = {k: z[k] for k in z.files}
        except Exception:                               # noqa: BLE001
            preds = {}
    blob['preds'] = preds
    return blob


def _assert_isolated(inner_train_idx, inner_test_idx, outer_test_idx, outer_held):
    """The outer test circuit must not appear in the inner selection at all."""
    outer_rows = set(outer_test_idx)
    inner_rows = set(inner_train_idx) | set(inner_test_idx)
    bad = outer_rows & inner_rows
    assert not bad, 'the outer held-out circuit %s leaked into the inner ' \
                    'selection (%d rows)' % (outer_held, len(bad))


def _train_predict(cfg, tr, te, y, items, n_types, seed, epochs=None):
    params = G.train([items[i] for i in tr], y[tr], cfg['readout'], n_types,
                      seed=seed, epochs=epochs or cfg['epochs'], wd=cfg['wd'],
                      use_A=cfg['propagation'], use_types=cfg['types'])
    return G.predict([items[i] for i in te], params, cfg['readout'],
                      use_A=cfg['propagation'], use_types=cfg['types'])


def _n_eligible(rows, y, circuits):
    """COMPLETENESS_MARK: how many outer folds this data set can actually
    produce.  It mirrors run_nested's skip rule exactly (no test rows, or a
    single-class training set), so a run is 'complete' when it has processed
    one fold per ELIGIBLE circuit -- not per circuit in the raw list."""
    ckt_of = [r.get('circuit') for r in rows]
    n = 0
    for held in circuits:
        tr = [i for i in range(len(rows)) if ckt_of[i] != held]
        te = [i for i in range(len(rows)) if ckt_of[i] == held]
        if not te or len(set(y[tr])) < 2:
            continue
        n += 1
    return n


def run_nested(rows, y, items, circuits, n_types, grid, selections,
               seed=G.SEED, log=_flush_print, tag='', checkpoint_path=None,
               resume_state=None, max_new_folds=None):
    """Nested selection + out-of-fold predictions for each selection rule.

    ``selections`` is a list of (name, allowed_config_names).  The inner
    scores are computed ONCE for the whole grid and then reused by every
    selection rule, so a second rule costs one extra training per outer fold.
    """
    ckt_of = [r.get('circuit') for r in rows]
    preds = {sel_name: np.zeros(len(rows)) for sel_name, _ in selections}
    selected = {sel_name: {} for sel_name, _ in selections}
    inner_log = {}
    done = set()
    if resume_state:
        for sel_name, folds in (resume_state.get('selected_per_outer_fold')
                                or {}).items():
            if sel_name in selected:
                selected[sel_name] = dict(folds)
        inner_log = dict(resume_state.get('inner_scores') or {})
        done = set(resume_state.get('folds_done') or [])
        for sel_name, arr in (resume_state.get('preds') or {}).items():
            if sel_name in preds and len(arr) == len(rows):
                preds[sel_name][:] = arr
        log('  %sresume: %d fold(s) already done' % (tag, len(done)))
    new_folds = 0
    for held in circuits:
        if held in done:
            log('  %souter %-5s [resume] already done -- skipped' % (tag, held))
            continue
        if max_new_folds is not None and new_folds >= max_new_folds:
            log('  %sstopping after %d new fold(s); %d fold(s) done in total'
                % (tag, new_folds, len(done) + new_folds))
            break
        tr = [i for i in range(len(rows)) if ckt_of[i] != held]
        te = [i for i in range(len(rows)) if ckt_of[i] == held]
        if not te or len(set(y[tr])) < 2:
            continue
        inner_circuits = sorted({ckt_of[i] for i in tr})
        scores = {}
        for cfg in grid:
            vals = []
            for jheld in inner_circuits:
                itr = [i for i in tr if ckt_of[i] != jheld]
                ite = [i for i in tr if ckt_of[i] == jheld]
                if not ite or len(set(y[itr])) < 2:
                    continue
                _assert_isolated(itr, ite, te, held)
                p = _train_predict(cfg, itr, ite, y, items, n_types, seed)
                m = G.pool_metrics([rows[i] for i in ite], y[ite], p)
                v = m.get('mean_within_pool_auc')
                if v is not None:
                    vals.append(v)
            scores[cfg['name']] = float(np.mean(vals)) if vals else None
        inner_log[held] = scores
        for sel_name, allowed in selections:
            best = None
            for cfg in grid:                  # grid order is the tie-break
                if cfg['name'] not in allowed:
                    continue
                v = scores.get(cfg['name'])
                if v is None:
                    continue
                if best is None or v > best[0]:
                    best = (v, cfg)
            if best is None:
                continue
            cfg = best[1]
            selected[sel_name][held] = {'config': cfg['name'],
                                        'inner_score': best[0],
                                        'inner_scores': scores}
            preds[sel_name][te] = _train_predict(cfg, tr, te, y, items,
                                                 n_types, seed)
            log('  %souter %-5s [%s] selected=%-8s inner=%s'
                % (tag, held, sel_name, cfg['name'],
                   {k: (round(v, 6) if v is not None else None)
                    for k, v in scores.items()}))
        new_folds += 1
        done.add(held)
        if checkpoint_path:
            _checkpoint(checkpoint_path, selected, inner_log, preds,
                        tag.strip() or 'main', done)
    return preds, selected, inner_log


def _grid_for(kind):
    if kind == 'pub':
        return [dict(c) for c in GRID_PRE if c['name'] == 'pub']
    if kind == 'pre':
        return [dict(c) for c in GRID_PRE]
    return [dict(c) for c in GRID_EXTENDED]


def _selections_for(kind):
    if kind == 'pub':
        return [('pub', ['pub'])]
    if kind == 'pre':
        return [('pre', PRE_NAMES)]
    return [('pre', PRE_NAMES), ('extended', ALL_NAMES)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='itc99')
    ap.add_argument('--label', default='resolvable')
    ap.add_argument('--epochs', type=int, default=120)
    ap.add_argument('--grid', choices=['pre', 'extended'], default='extended',
                    help="'pre' = the four pre-registered configurations only; "
                         "'extended' = plus the adversarial 'global' arm")
    ap.add_argument('--null-grid', choices=['full', 'pre', 'pub'], default='pub',
                    help="the grid used for the null-label control")
    ap.add_argument('--grid-epochs', type=int, default=None,
                    help="override every grid config's epoch count (sandbox "
                         "pre-flight only; the pre-registered grid keeps its own)")
    ap.add_argument('--out', default=None)
    ap.add_argument('--resume', action='store_true',
                    help='continue from the checkpoint of a previous chunk')
    ap.add_argument('--max-folds', type=int, default=None,
                    help='process at most N NEW outer folds, then checkpoint '
                         'and stop (to fit inside a job time limit)')
    ap.add_argument('--require-complete', action='store_true',
                    help='do not write the output file unless EVERY outer fold '
                         'of both the main run and the null-label control was '
                         'computed -- a truncated chunk must never look like a '
                         'complete readout to the landing script')
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

    grid = _grid_for(args.grid)
    if args.grid_epochs is not None:
        for c in grid:
            c['epochs'] = args.grid_epochs
    names = [c['name'] for c in grid]
    selections = _selections_for(args.grid)

    out = {
        'family': args.family, 'label_mode': args.label, 'band_ns': band,
        'n_rows': len(rows), 'n_circuits': len(circuits),
        'grid': grid,
        'grid_kind': args.grid,
        'selection_rules': {n: a for n, a in selections},
        'protocol': ('outer = leave-one-circuit-out; inner = leave-one-circuit-out '
                     'over the TRAINING circuits only; inner score = mean '
                     'within-pool AUC (the headline readout); the outer test '
                     'circuit is asserted to be absent from the inner selection; '
                     'the inner scores are computed once and shared by every '
                     'selection rule'),
        'null_grid': args.null_grid,
        'pre_registration': 'scratch/round32_preregistration.json',
        'pre_registration_note': (
            "the pre-registered grid's scope sentence claims coverage of the "
            "readout dimension, but its four configurations all fix readout='mod'; "
            "the 'pre' selection below is the pre-registered verdict unchanged, "
            "and the 'extended' selection adds the 'global' arm as an ADVERSARIAL "
            "arm (post-hoc informed, bias fixed: it can only make the negative "
            "conclusion harder to sustain)"),
    }

    # ---- the nested run
    print('[F] nested selection, family=%s grid=%s' % (args.family, args.grid),
          flush=True)
    ckpt_main = str(SCR / ('round32_nested_%s_checkpoint.json' % args.family))
    resume_main = _load_checkpoint(ckpt_main) if args.resume else None
    global FINGERPRINT
    FINGERPRINT = _fingerprint(grid, args)
    if resume_main is not None:
        stored = resume_main.get('fingerprint')
        if stored is not None and stored != FINGERPRINT:
            raise SystemExit(
                'REFUSING TO RESUME: the checkpoint was written with a '
                'different configuration.\n  stored:   %s\n  current:  %s'
                % (json.dumps(stored, sort_keys=True),
                   json.dumps(FINGERPRINT, sort_keys=True)))
    preds, selected, inner_log = run_nested(rows, y, items, circuits,
                                            gs.n_types, grid, selections,
                                            log=_flush_print,
                                            checkpoint_path=ckpt_main,
                                            resume_state=resume_main,
                                            max_new_folds=args.max_folds)
    out['selected_per_outer_fold'] = selected
    out['inner_scores'] = inner_log
    out['metrics'] = {}
    for name, p in preds.items():
        m = G.pool_metrics(rows, y, p)
        out['metrics'][name] = m
        print('  %-10s pooled=%s within=%s'
              % (name, m['pooled_auc'], m['mean_within_pool_auc']), flush=True)

    # ---- baselines from the project's own tool
    base_preds = {}
    out['baselines'] = {}
    for fs in ('kind_only', 'structural'):
        p, _ = rpc.oof_predict(rows, kinds, circuits, y, fs, model='ridge')
        base_preds[fs] = p
        out['baselines'][fs] = G.pool_metrics(rows, y, p)
        print('  %-10s pooled=%s within=%s'
              % (fs, out['baselines'][fs]['pooled_auc'],
                 out['baselines'][fs]['mean_within_pool_auc']), flush=True)

    # ---- paired per-pool tests
    out['paired_pool_tests'] = []
    for name, p in preds.items():
        for bname in ('kind_only', 'structural'):
            t = G.paired_pool_test(rows, y, base_preds[bname], p, bname, name)
            out['paired_pool_tests'].append(t)
            print('  paired %-10s vs %-10s diff=%s wins %s losses %s p=%s'
                  % (t['name_a'], t['name_b'], t['mean_diff'], t['b_wins'],
                     t['b_losses'], t['sign_test_p']), flush=True)

    # ---- the null-label control under the same outer protocol
    rng = np.random.default_rng(G.SEED + 5)
    from collections import defaultdict
    pool_idx = defaultdict(list)
    for i, r in enumerate(rows):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    y_null = y.copy()
    for _idx in pool_idx.values():
        perm = rng.permutation(len(_idx))
        y_null[_idx] = y[_idx][perm]
    null_grid = _grid_for(args.null_grid if args.null_grid != 'full' else 'extended')
    if args.grid_epochs is not None:
        for c in null_grid:
            c['epochs'] = args.grid_epochs
    null_sels = _selections_for(args.null_grid)
    print('[F] null-label control, grid=%s' % args.null_grid, flush=True)
    ckpt_null = str(SCR / ('round32_nested_%s_null_checkpoint.json' % args.family))
    resume_null = _load_checkpoint(ckpt_null) if args.resume else None
    FINGERPRINT = _fingerprint(null_grid, args)
    if resume_null is not None:
        stored_n = resume_null.get('fingerprint')
        if stored_n is not None and stored_n != FINGERPRINT:
            raise SystemExit(
                'REFUSING TO RESUME the null control: the checkpoint was '
                'written with a different configuration.\n  stored:   %s\n'
                '  current:  %s'
                % (json.dumps(stored_n, sort_keys=True),
                   json.dumps(FINGERPRINT, sort_keys=True)))
    npreds, nsel, ninner = run_nested(rows, y_null, items, circuits, gs.n_types,
                                      null_grid, null_sels, log=_flush_print,
                                      tag='NULL ', checkpoint_path=ckpt_null,
                                      resume_state=resume_null,
                                      max_new_folds=args.max_folds)
    out['C2_null_labels'] = {k: G.pool_metrics(rows, y_null, v)
                              for k, v in npreds.items()}
    out['C2_null_selected_per_outer_fold'] = nsel
    print('  C2 null:', {k: (v['pooled_auc'], v['mean_within_pool_auc'])
                         for k, v in out['C2_null_labels'].items()}, flush=True)

    # COMPLETENESS_MARK: a truncated chunk must never be readable as a
    # complete readout -- the landing script reads this file, and a file that
    # exists with only some folds would silently under-sample every nested
    # number.
    n_main_expect = _n_eligible(rows, y, circuits)
    n_null_expect = _n_eligible(rows, y_null, circuits)
    n_main_done = len(inner_log)
    n_null_done = len(ninner)
    complete = ((n_main_done >= n_main_expect)
                and (n_null_done >= n_null_expect))
    out['n_outer_folds_main'] = n_main_expect
    out['n_outer_folds_null'] = n_null_expect
    out['folds_done_main'] = n_main_done
    out['folds_done_null'] = n_null_done
    out['complete'] = complete

    dest = Path(args.out) if args.out else SCR / ('round32_nested_%s.json' % args.family)
    if args.require_complete and not complete:
        print('[F] INCOMPLETE: main %d/%d folds, null %d/%d folds -- the output '
              'file is NOT written; the checkpoint is kept for --resume'
              % (n_main_done, n_main_expect, n_null_done, n_null_expect),
              flush=True)
        raise SystemExit(3)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', dest, flush=True)


if __name__ == '__main__':
    main()
