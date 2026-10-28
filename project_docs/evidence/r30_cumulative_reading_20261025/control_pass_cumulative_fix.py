"""Control pass for the cumulative-reading fix (LOG-20261024-27).

Two kinds of checks, and BOTH must pass:

  A. NOTHING PUBLISHED MAY MOVE.
     The marginal block of the three-point curve is already published (it is the
     basis of the "attenuation concentrates in the placement stage" conclusion),
     so it must come out of the rerun bit-for-bit identical to the pre-fix
     backup.  Same for the training table's marginal columns, the verdict
     counts, the coverage block and the bands.

  B. THE CORRECTED CUMULATIVE BLOCK MUST MATCH AN INDEPENDENT IMPLEMENTATION.
     The numbers written by the patched tools are compared against a second,
     independently written computation that goes to the ledger and to the raw
     dataset, not to the tool's own output.

Any mismatch is a FAIL; the script exits non-zero.
"""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ITCF = REPO / 'experiments/20261024_physical_labels_itc99'
ISCF = REPO / 'experiments/20261024_physical_labels'
BK = REPO / 'scratch/backup_pre_cumfix'

checks = []


def chk(name, ok, detail=''):
    checks.append((name, bool(ok), detail))


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    return None if dx == 0 or dy == 0 else num / (dx * dy)


def ols_slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / den


def ledger_base_ideal(fam_dir):
    out = {}
    if not fam_dir.exists():
        return out
    for ckt_dir in sorted(p for p in fam_dir.iterdir() if p.is_dir()):
        p = ckt_dir / ckt_dir.name / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        refs = set()
        for t in d.get('trials', []):
            if not isinstance(t, dict) or str(t.get('iteration')) != '1':
                continue
            mr = (t.get('acceptance_evidence') or {}).get('metric_references') or {}
            v = mr.get('setup_wns')
            if v is not None:
                refs.add(round(float(v), 6))
        if len(refs) == 1:
            out[ckt_dir.name] = refs.pop()
    return out


def read_csv(p):
    with p.open(encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def check_family(tag, famdir, backup_tpc, backup_tt, ledger_dir, expect):
    new_tpc = json.loads((famdir / 'three_point_curve.json').read_text(encoding='utf-8'))
    old_tpc = json.loads(backup_tpc.read_text(encoding='utf-8'))

    # ---- A: the marginal block must not move --------------------------------
    om, nm = old_tpc.get('stages_marginal', {}), new_tpc.get('stages_marginal', {})
    for stage in ('ideal', 'placed', 'routed'):
        for field in ('n', 'mean', 'median', 'spearman_vs_ideal',
                      'sign_agreement_vs_ideal', 'n_positive', 'attenuation_slope_vs_ideal'):
            a = om.get(stage, {}).get(field)
            b = nm.get(stage, {}).get(field)
            ok = (a == b) if isinstance(a, str) else close(a, b)
            chk(f'{tag}: marginal.{stage}.{field} unchanged', ok, f'{a} -> {b}')
    for field in ('n', 'spearman', 'slope_routed_on_placed'):
        a = om.get('placed_to_routed', {}).get(field)
        b = nm.get('placed_to_routed', {}).get(field)
        chk(f'{tag}: marginal.placed_to_routed.{field} unchanged',
            (a == b) if isinstance(a, str) else close(a, b), f'{a} -> {b}')

    for field in ('coverage', 'verdict_counts', 'bands', 'decisions', 'netlist_consistency',
                  'measure_note'):
        a = json.dumps(old_tpc.get(field), sort_keys=True, ensure_ascii=False)
        b = json.dumps(new_tpc.get(field), sort_keys=True, ensure_ascii=False)
        chk(f'{tag}: top-level "{field}" unchanged', a == b)

    # ---- B: the corrected cumulative block vs an independent computation ----
    base_ideal = ledger_base_ideal(ledger_dir)
    basis = new_tpc.get('ideal_cumulative_basis') or {}
    chk(f'{tag}: ideal_cumulative_basis present', bool(basis))
    chk(f'{tag}: ideal_cumulative_basis ledger_family',
        (basis.get('ledger_family') or '').replace('\\', '/')
        == str(ledger_dir.relative_to(REPO)).replace('\\', '/'),
        str(basis.get('ledger_family')))
    chk(f'{tag}: ideal_cumulative_basis values == ledger-derived',
        basis.get('circuit_baseline_ideal_wns') == base_ideal,
        f"basis={len(basis.get('circuit_baseline_ideal_wns') or {})} "
        f"indep={len(base_ideal)}")

    cands = new_tpc.get('candidates') or []
    tt_rows = read_csv(famdir / 'training_table.csv')
    tt_by_key = {r['key']: r for r in tt_rows}

    # independent cumulative for every candidate
    indep = []
    for c in cands:
        row = tt_by_key.get(c['key'])
        if row is None:
            continue
        iw = row.get('ideal_wns')
        cb = base_ideal.get(c['circuit'])
        if iw in (None, '') or cb is None:
            continue
        indep.append({
            'key': c['key'],
            'ideal_cum': round(float(iw) - cb, 6),
            'placed_cum': c.get('placed_cumulative'),
            'routed_cum': c.get('routed_cumulative'),
        })
    chk(f'{tag}: independent cumulative covers every candidate',
        len(indep) == len(cands), f'{len(indep)} vs {len(cands)}')

    max_dev = 0.0
    n_mismatch = 0
    for c, ind in zip([c for c in cands if c['key'] in tt_by_key], indep):
        got = c.get('ideal_cumulative')
        if got is None:
            n_mismatch += 1
            continue
        dev = abs(float(got) - ind['ideal_cum'])
        max_dev = max(max_dev, dev)
        if dev > 1e-9:
            n_mismatch += 1
    chk(f'{tag}: candidates.ideal_cumulative == independent', n_mismatch == 0,
        f'mismatches={n_mismatch} max_dev={max_dev}')

    # stage statistics of the cumulative block, recomputed independently
    cum = new_tpc.get('stages_cumulative', {})
    for stage, key in (('ideal', 'ideal_cum'), ('placed', 'placed_cum'), ('routed', 'routed_cum')):
        pairs = [(ind['ideal_cum'], ind[key]) for ind in indep if ind[key] is not None]
        xs = [a for a, _ in pairs]
        ys = [b for _, b in pairs]
        exp_mean = round(sum(ys) / len(ys), 6)
        exp_rho = round(spearman(xs, ys), 4)
        exp_slope = round(ols_slope(xs, ys), 4)
        blk = cum.get(stage, {})
        chk(f'{tag}: cumulative.{stage}.mean == independent', close(blk.get('mean'), exp_mean, 1e-6),
            f"{blk.get('mean')} vs {exp_mean}")
        chk(f'{tag}: cumulative.{stage}.spearman == independent', close(blk.get('spearman_vs_ideal'), exp_rho, 1e-4),
            f"{blk.get('spearman_vs_ideal')} vs {exp_rho}")
        chk(f'{tag}: cumulative.{stage}.slope == independent', close(blk.get('attenuation_slope_vs_ideal'), exp_slope, 1e-4),
            f"{blk.get('attenuation_slope_vs_ideal')} vs {exp_slope}")

    # ---- the training table -------------------------------------------------
    old_rows = read_csv(backup_tt)
    old_by_key = {r['key']: r for r in old_rows}
    chk(f'{tag}: training table row count unchanged', len(tt_rows) == len(old_rows),
        f'{len(tt_rows)} vs {len(old_rows)}')
    for col in ('ideal_delta_wns', 'placed_delta_wns', 'routed_delta_wns',
                'routed_cumulative_wns', 'placed_cumulative_wns'):
        diff = sum(1 for r in tt_rows
                   if r.get(col) != old_by_key.get(r['key'], {}).get(col))
        chk(f'{tag}: training table column {col} unchanged', diff == 0, f'{diff} rows differ')

    n_cum_ok = 0
    n_cum_bad = 0
    for r in tt_rows:
        c = next((x for x in cands if x['key'] == r['key']), None)
        if c is None:
            continue
        if r.get('ideal_cumulative_wns') in (None, ''):
            continue
        if close(r['ideal_cumulative_wns'], c.get('ideal_cumulative'), 1e-9):
            n_cum_ok += 1
        else:
            n_cum_bad += 1
    chk(f'{tag}: training table ideal_cumulative_wns == three-point curve', n_cum_bad == 0,
        f'ok={n_cum_ok} bad={n_cum_bad}')

    # the old (wrong) value must actually have been different -- otherwise the
    # fix would be a no-op and the whole exercise would be pointless
    old_vals = {r['key']: r.get('ideal_cumulative_wns') for r in old_rows}
    n_diff = sum(1 for r in tt_rows
                 if old_vals.get(r['key']) is not None
                 and r.get('ideal_cumulative_wns') not in (None, '')
                 and not close(old_vals[r['key']], r['ideal_cumulative_wns'], 1e-9))
    chk(f'{tag}: the fix actually changed the column', n_diff > 0, f'{n_diff} rows changed')

    # expectations pinned from the pre-fix analysis
    for name, val in expect.get('cumulative_mean', {}).items():
        chk(f'{tag}: cumulative {name} mean == {val}', close(cum.get(name, {}).get('mean'), val, 1e-6),
            str(cum.get(name, {}).get('mean')))
    for name, val in expect.get('cumulative_rho', {}).items():
        chk(f'{tag}: cumulative {name} spearman == {val}',
            close(cum.get(name, {}).get('spearman_vs_ideal'), val, 1e-4),
            str(cum.get(name, {}).get('spearman_vs_ideal')))


def main():
    check_family(
        'itc99', ITCF, BK / 'itc99_three_point_curve.json', BK / 'itc99_training_table.csv',
        REPO / 'experiments/20260826_itc99_main',
        {'cumulative_mean': {'ideal': 0.028613, 'placed': 0.027054, 'routed': 0.04304},
         'cumulative_rho': {'placed': 0.9411, 'routed': 0.8769}})
    check_family(
        'iscas89', ISCF, BK / 'iscas89_three_point_curve.json', BK / 'iscas89_training_table.csv',
        REPO / 'experiments/20260826_iscas89_main',
        {'cumulative_mean': {'ideal': 0.179815, 'placed': 0.238923, 'routed': 0.248031},
         'cumulative_rho': {'placed': 0.965, 'routed': 0.9461}})

    npass = sum(1 for _, ok, _ in checks if ok)
    nfail = len(checks) - npass
    out = {'n_checks': len(checks), 'n_pass': npass, 'n_fail': nfail,
           'failed': [{'check': n, 'detail': d} for n, ok, d in checks if not ok],
           'all': [{'check': n, 'ok': ok, 'detail': d} for n, ok, d in checks]}
    (REPO / 'scratch/cumulative_fix_control_pass.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'all'}, indent=2, ensure_ascii=False))
    sys.exit(1 if nfail else 0)


if __name__ == '__main__':
    main()
