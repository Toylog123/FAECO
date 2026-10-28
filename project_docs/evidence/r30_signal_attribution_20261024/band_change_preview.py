"""FALSIFICATION PREVIEW: will the LOG-20261024-21 conclusions survive the band
change?

The routed candidate-level band moves from the pilot scope (2 sigma = 0.087496
ns) to the full-family scope (preview 2 sigma = 0.050419 ns, about 42% narrower)
when the I1 batch completes.  Every band-thresholded number in LOG-21 therefore
has to be recomputed, and the honest question is: WHICH conclusions flip, and
which do not?

METHOD
------
The two tools are IMPORTED and their own functions are called with a band
override; nothing is re-implemented.  Two passes over the SAME training table:

  CONTROL  the band in force now (pilot) -- must reproduce the stored
           LOG-20261024-21 artefacts exactly.  If it does not, the harness is
           unfaithful and the preview pass is discarded;
  PREVIEW  the band the full-family scope is expected to give.

Holding the data fixed and changing only the threshold isolates the band
effect.  The final recomputation will additionally have more labelled rows, so
this is the dominant-but-not-only factor.

NOTE ON THE TWO ROW SETS: the classifier works on the JOINED rows (the ledger
and the graph features must exist), while the acceptance tool works on the RAW
training table.  Passing the wrong one to either tool silently changes the
denominators -- the first version of this harness did exactly that and the
control pass caught it.

Output: scratch/band_change_preview.json
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
import acceptance_physical_selectivity as aps  # noqa: E402

FAM = 'itc99'
FAM_DIR = rpc.FAM_DIRS[FAM]
OUT = REPO / 'scratch/band_change_preview.json'
def _band_from_artefact():
    """The routed candidate-level band, read back from the stored artefact."""
    tpc = json.loads((FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    return (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')


BAND_PREVIEW = _band_from_artefact()
BAND_PREVIEW_BEFORE_FINALISATION = 0.050419  # the value the LOG-23 preview used


def raw_rows():
    tt = FAM_DIR / 'training_table.jsonl'
    return [json.loads(l) for l in tt.read_text(encoding='utf-8').splitlines() if l.strip()]


def joined_rows(rows_all):
    feats = rpc.load_ledger(rpc.LEDGERS[FAM])
    struct = rpc.load_structural(FAM_DIR)
    rows = []
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
        rows.append(r)
    kinds = sorted({r.get('kind') for r in rows if r.get('kind')})
    circuits = sorted({r.get('circuit') for r in rows})
    return rows, kinds, circuits


def classifier_pass(rows, kinds, circuits, band, label_mode, sweep=False):
    rng = np.random.default_rng(rpc.SEED)
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    res = rpc.evaluate('routed', sub, kinds, circuits, band, rng, label_mode=label_mode)
    cells = {}
    for fs, c in res['cells'].items():
        b = (c.get('budget_recall') or {}).get('0.25') or {}
        cells[fs] = {
            'pooled_auc': c.get('pooled_auc'),
            'ci95': c.get('pooled_auc_ci95'),
            'mean_per_circuit_auc': c.get('mean_per_circuit_auc'),
            'recall_at_25pct': b.get('mean_recall_model'),
            'recall_gain_over_random': b.get('recall_gain_over_random'),
            'sign_test_p': b.get('sign_test_p'),
        }
    out = {
        'band_ns': band,
        'label_mode': label_mode,
        'n_rows': res['n_rows'],
        'n_positive': res['n_positive'],
        'powered': res['powered'],
        'cells': cells,
    }
    if sweep:
        sw = {}
        for m in rpc.THRESHOLD_SWEEP:
            if m == 1.0:
                continue
            rm = rpc.evaluate('routed', sub, kinds, circuits, band, rng,
                               band_mult=m, label_mode=label_mode)
            sw[str(m)] = {fs: {'pooled_auc': c.get('pooled_auc'),
                               'ci95': c.get('pooled_auc_ci95')}
                          for fs, c in rm['cells'].items()}
        out['threshold_sweep'] = sw
    # the four gates
    base = cells.get('kind_only', {}).get('pooled_auc')
    gates = {}
    for fs, c in cells.items():
        ci = c.get('ci95')
        g = {
            'G1_auc_ci_excludes_0.5': bool(ci and ci[0] > 0.5),
            'G2_auc_above_kind_only_baseline': bool(c.get('pooled_auc') is not None
                                                    and base is not None
                                                    and c['pooled_auc'] > base),
            'G3_threshold_sweep_ci_excludes_0.5_everywhere': None,
            'G4_budget_recall_above_random': None,
        }
        b25 = None
        for fs2, c2 in res['cells'].items():
            if fs2 == fs:
                b25 = (c2.get('budget_recall') or {}).get('0.25')
        if b25:
            g['G4_budget_recall_above_random'] = bool(
                (b25.get('recall_gain_over_random') or 0) > 0
                and b25.get('sign_test_p') is not None and b25['sign_test_p'] < 0.05)
        if sweep:
            cis = [ci] + [sw[str(m)][fs]['ci95'] for m in rpc.THRESHOLD_SWEEP
                          if m != 1.0 and fs in sw.get(str(m), {})]
            cis = [c for c in cis if c]
            g['G3_threshold_sweep_ci_excludes_0.5_everywhere'] = bool(cis) and all(
                c[0] > 0.5 for c in cis)
        gates[fs] = g
    out['gates'] = gates
    return out


def ablation_pass(rows, kinds, circuits, band):
    sub = [r for r in rows if r.get(rpc.TARGET_COL['routed']) is not None]
    thr = band
    y = np.array([1.0 if abs(rpc.num(r.get(rpc.TARGET_COL['routed']), -1e18)) > thr else 0.0
                  for r in sub])
    if int(y.sum()) < rpc.MIN_POSITIVES_FOR_AUC:
        return {'n_positive': int(y.sum()), 'powered': False, 'cells': {}}
    pool_idx = defaultdict(list)
    for i, r in enumerate(sub):
        pool_idx[(r.get('circuit'), str(r.get('iteration')))].append(i)
    idx_by_pool = [np.array(v) for v in pool_idx.values()]
    abl = {}
    for fs in rpc.ABLATION_SETS:
        preds, _ = rpc.oof_predict(sub, kinds, circuits, y, fs, model='ridge')
        a = rpc.auc(y, preds)
        rng5 = np.random.default_rng(rpc.SEED + 5)
        point, lo, hi = rpc.boot_pool_auc(y, preds, idx_by_pool, rpc.BOOTSTRAP_POOLS, rng5)
        abl[fs] = {'pooled_auc': round(a, 6) if a is not None else None,
                   'pooled_auc_ci95': [lo, hi] if lo is not None else None,
                   'n_features': rpc.build_matrix(sub, fs, kinds)[1]}
    return {'label_mode': 'resolvable', 'threshold_ns': thr,
            'n_positive': int(y.sum()), 'cells': abl}


def acceptance_pass(rows_raw, band, stage='routed'):
    col = aps.TARGET_COL[stage]
    acc = [r for r in rows_raw if aps.is_accepted(r) and r.get(col) is not None]
    rej = [r for r in rows_raw if not aps.is_accepted(r) and r.get(col) is not None]
    if not acc:
        return None
    acc_by, rej_by = defaultdict(list), defaultdict(list)
    for r in acc:
        acc_by[r.get('circuit')].append(r)
    for r in rej:
        rej_by[r.get('circuit')].append(r)
    rng = np.random.default_rng(aps.SEED)
    obs_g, obs_h, null_g, null_h = aps.circuit_matched_null(
        acc_by, rej_by, col, band, aps.PERMUTATIONS, rng)
    pool_rows = defaultdict(list)
    for r in rows_raw:
        if r.get(col) is not None:
            pool_rows[(r.get('circuit'), str(r.get('iteration')))].append(r)
    pg, ph = aps.pool_matched_null(acc, pool_rows, col, band, aps.PERMUTATIONS, rng)

    def paired(rate):
        diffs = []
        for ckt in sorted(acc_by):
            a, b = acc_by[ckt], rej_by.get(ckt, [])
            if not a or not b:
                continue
            ra = sum(1 for r in a if aps.classify(r.get(col), band) == rate) / len(a)
            rb = sum(1 for r in b if aps.classify(r.get(col), band) == rate) / len(b)
            diffs.append(ra - rb)
        return diffs

    dg, dh = paired('real_gain'), paired('real_harm')
    pg_p, gw, gl, gt = aps.sign_test(dg)
    ph_p, hw, hl, ht = aps.sign_test(dh)
    am, rm = aps.mix(acc, col, band), aps.mix(rej, col, band)
    return {
        'band_ns': band,
        'n_accepted': len(acc), 'n_rejected': len(rej),
        'accepted': am, 'rejected': rm,
        'gain_enrichment': (round(am['real_gain_rate'] / rm['real_gain_rate'], 4)
                            if rm['real_gain_rate'] else None),
        'harm_ratio': (round(am['real_harm_rate'] / rm['real_harm_rate'], 4)
                       if rm['real_harm_rate'] else None),
        'p_gain_circuit_matched': aps.permutation_p(am['real_gain_rate'], null_g, 'greater'),
        'p_harm_circuit_matched': aps.permutation_p(am['real_harm_rate'], null_h, 'lower'),
        'p_gain_pool_matched': aps.permutation_p(am['real_gain_rate'], pg, 'greater'),
        'p_harm_pool_matched': aps.permutation_p(am['real_harm_rate'], ph, 'lower'),
        'per_circuit_gain': '%dW/%dL/%dT p=%s' % (gw, gl, gt, pg_p),
        'per_circuit_harm': '%dW/%dL/%dT p=%s' % (hw, hl, ht, ph_p),
    }


def main():
    rows_raw = raw_rows()
    rows, kinds, circuits = joined_rows(rows_raw)
    tpc = json.loads((FAM_DIR / 'three_point_curve.json').read_text(encoding='utf-8'))
    band_now = (tpc.get('bands') or {}).get('routed_candidate_level_two_sigma_ns')

    out = {
        'family': FAM,
        'n_rows_in_training_table': len(rows_raw),
        'n_rows_usable_after_join': len(rows),
        'circuits': circuits,
        'band_in_force_now': band_now,
        'band_preview_full_family': BAND_PREVIEW,
        'note': ('the training table is held FIXED between the two passes, so this '
                 'isolates the effect of the threshold; the final recomputation will '
                 'also have more labelled rows'),
        'classifier': {}, 'ablation': {}, 'acceptance': {},
    }

    for lm in ('resolvable', 'gain', 'harm'):
        out['classifier'][lm] = {
            'control': classifier_pass(rows, kinds, circuits, band_now, lm),
            'preview': classifier_pass(rows, kinds, circuits, BAND_PREVIEW, lm,
                                       sweep=True),
        }
    out['ablation']['routed'] = {
        'control': ablation_pass(rows, kinds, circuits, band_now),
        'preview': ablation_pass(rows, kinds, circuits, BAND_PREVIEW),
    }
    out['acceptance']['routed'] = {
        'control': acceptance_pass(rows_raw, band_now),
        'preview': acceptance_pass(rows_raw, BAND_PREVIEW),
    }

    # ---------------- faithfulness against the STORED LOG-21 artefacts
    stored_rpc = json.loads((FAM_DIR / 'resolvable_positive.json').read_text(encoding='utf-8'))
    stored_acc = json.loads((FAM_DIR / 'acceptance_selectivity.json').read_text(encoding='utf-8'))
    checks = []
    for lm in ('resolvable', 'gain', 'harm'):
        s = (stored_rpc.get('results') or {}).get('routed', {}).get(lm) or {}
        c = out['classifier'][lm]['control']
        checks.append(('n_positive[%s]' % lm, s.get('n_positive'), c['n_positive']))
        for fs in ('structural', 'proxy_plus_ideal', 'kind_only', 'proxy_only'):
            sv = ((s.get('cells') or {}).get(fs) or {}).get('pooled_auc')
            cv = (c['cells'].get(fs) or {}).get('pooled_auc')
            checks.append(('auc[%s/%s]' % (lm, fs), sv, cv))
    sa = (stored_acc.get('stages') or {}).get('routed') or {}
    ca = out['acceptance']['routed']['control']
    checks.append(('accepted.n', (sa.get('accepted') or {}).get('n'), ca['accepted']['n']))
    checks.append(('rejected.n', (sa.get('rejected') or {}).get('n'), ca['rejected']['n']))
    checks.append(('accepted.real_gain', (sa.get('accepted') or {}).get('real_gain'),
                    ca['accepted']['real_gain']))
    checks.append(('rejected.real_harm', (sa.get('rejected') or {}).get('real_harm'),
                    ca['rejected']['real_harm']))
    checks.append(('gain_enrichment',
                    (sa.get('enrichment') or {}).get('real_gain_ratio_accepted_over_rejected'),
                    ca['gain_enrichment']))
    devs = []
    for name, sv, cv in checks:
        if isinstance(sv, (int, float)) and isinstance(cv, (int, float)):
            devs.append(abs(float(sv) - float(cv)))
        elif sv != cv:
            devs.append(999.0)
    out['control_faithfulness'] = {
        'n_checks': len(checks),
        'max_absolute_deviation': max(devs) if devs else None,
        'mismatches': [{'name': n, 'stored': s, 'control': c}
                       for n, s, c in checks
                       if not (isinstance(s, (int, float)) and isinstance(c, (int, float))
                               and abs(float(s) - float(c)) < 1e-6)
                       and s != c],
        'faithful': bool(devs and max(devs) < 1e-6),
    }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    cf = out['control_faithfulness']
    print('written', OUT)
    print('control faithful: %s  max dev %s  (%d checks, %d mismatches)'
          % (cf['faithful'], cf['max_absolute_deviation'], cf['n_checks'],
             len(cf['mismatches'])))
    for m in cf['mismatches'][:10]:
        print('   MISMATCH', m)


if __name__ == '__main__':
    main()
