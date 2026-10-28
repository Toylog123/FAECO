"""Correct the CUMULATIVE reading of the three-point curve and quantify the
ideal -> physical attenuation on a SINGLE consistent basis.

Adjudicated facts (see scratch/check_ideal_ref_semantics.py and the ledger):
  * ledger trial acceptance_evidence.metric_references.setup_wns is the ITERATION
    BASE netlist's ideal WNS:
      - iteration 1 trials: base_hash = the circuit baseline netlist hash
        (b01: a8a4c19f...), ref_setup_wns = -0.63  -> the circuit baseline ideal WNS
      - iteration 2 trials: ref_setup_wns = the setup_wns of the accepted candidate
        of the previous iteration (b01 trial 11: -0.62 = trial 10's setup_wns, and
        trial 10 carries accepted=True)
  * therefore ideal_delta_wns = setup_wns(cand) - setup_wns(iteration base)
    is a MARGINAL quantity, and the training table's `ideal_cumulative_wns`
    (= ideal_wns - ideal_baseline_wns) is the SAME subtraction under a wrong name.
  * placed_* and routed_* cumulative columns ARE genuinely measured against the
    circuit baseline.

So the shipped `stages_cumulative` block mixes readings: ideal is marginal, placed
and routed are cumulative.

This script rebuilds the cumulative block with the circuit-baseline ideal WNS taken
straight from the ledger, and reports the attenuation of the multi-round ECO effect
from the ideal netlist to the physical stages.

Output: JSON on stdout.
"""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAM = REPO / 'experiments/20261024_physical_labels_itc99'
LEDGER_FAM = REPO / 'experiments/20260826_itc99_main'
TT = FAM / 'training_table.csv'
TPC = FAM / 'three_point_curve.json'


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
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None, None
    slope = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / den
    inter = my - slope * mx
    resid = [ys[i] - (slope * xs[i] + inter) for i in range(n)]
    sd = math.sqrt(sum(r * r for r in resid) / (n - 2)) if n > 2 else None
    return slope, sd


def ledger_circuit_base_ideal():
    """Per circuit: the circuit-baseline ideal WNS, read from the ledger as the
    reference of the iteration-1 trials (their base hash is the circuit baseline)."""
    out = {}
    detail = {}
    if not LEDGER_FAM.exists():
        return out, detail
    for ckt in sorted(p.name for p in LEDGER_FAM.iterdir() if p.is_dir()):
        p = LEDGER_FAM / ckt / ckt / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        refs = []
        hashes = set()
        for t in d.get('trials', []):
            if not isinstance(t, dict):
                continue
            if str(t.get('iteration')) != '1':
                continue
            ev = t.get('acceptance_evidence') or {}
            mr = ev.get('metric_references') or {}
            if mr.get('setup_wns') is not None:
                refs.append(mr['setup_wns'])
            if t.get('base_netlist_hash'):
                hashes.add(t['base_netlist_hash'])
        uniq = sorted({r for r in refs})
        out[ckt] = uniq[0] if len(uniq) == 1 else None
        detail[ckt] = {'n_iter1_refs': len(refs), 'distinct_refs': uniq,
                       'n_distinct_iter1_base_hashes': len(hashes),
                       'unique': len(uniq) == 1}
    return out, detail


def stage_stats(pairs, name):
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    n = len(pairs)
    agree = sum(1 for a, b in pairs if a != 0 and b != 0 and (a > 0) == (b > 0))
    slope, sd = ols(xs, ys)
    return {
        'stage': name, 'n': n,
        'mean': round(sum(ys) / n, 6),
        'median': round(sorted(ys)[n // 2], 6),
        'n_positive': sum(1 for y in ys if y > 0),
        'n_negative': sum(1 for y in ys if y < 0),
        'n_zero': sum(1 for y in ys if y == 0),
        'sign_agreement_vs_ideal': f'{agree}/{n}',
        'spearman_vs_ideal': round(spearman(xs, ys), 4) if n else None,
        'attenuation_slope_vs_ideal': round(slope, 4) if slope is not None else None,
        'residual_sd_ns': round(sd, 6) if sd is not None else None,
    }


def main():
    out = {}
    base_ideal, base_detail = ledger_circuit_base_ideal()
    out['circuit_baseline_ideal_wns_from_ledger'] = base_ideal
    out['circuit_baseline_ideal_wns_check'] = base_detail

    # training table (per candidate, the ideal-side columns)
    tt = {}
    with TT.open(encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            def f(k):
                v = row.get(k)
                if v is None or v == '':
                    return None
                return float(v)
            tt[row['key']] = {
                'circuit': row['circuit'], 'kind': row['kind'],
                'iteration': row['iteration'],
                'ideal_wns': f('ideal_wns'), 'ideal_baseline_wns': f('ideal_baseline_wns'),
                'ideal_delta_wns': f('ideal_delta_wns'),
                'ideal_cumulative_wns_shipped': f('ideal_cumulative_wns'),
            }
    out['n_training_table_rows'] = len(tt)

    # three-point curve candidates (the placed/routed columns, same reading)
    tpc = json.loads(TPC.read_text(encoding='utf-8'))
    cands = tpc.get('candidates') or []
    out['n_three_point_candidates'] = len(cands)

    merged = []
    for c in cands:
        k = c.get('key')
        t = tt.get(k)
        if not t:
            continue
        cb = base_ideal.get(c['circuit'])
        ideal_cum = None
        if t['ideal_wns'] is not None and cb is not None:
            ideal_cum = round(t['ideal_wns'] - cb, 6)
        merged.append({
            'key': k, 'circuit': c['circuit'], 'kind': c.get('kind'),
            'ideal_marginal': t['ideal_delta_wns'],
            'ideal_cum_shipped': t['ideal_cumulative_wns_shipped'],
            'ideal_cum_corrected': ideal_cum,
            'placed_marginal': c.get('placed_marginal'),
            'placed_cum': c.get('placed_cumulative'),
            'routed_marginal': c.get('routed_marginal'),
            'routed_cum': c.get('routed_cumulative'),
        })
    out['n_merged'] = len(merged)

    # ---------- MARGINAL block: must reproduce the shipped numbers ----------
    marg = {}
    for name, key in (('ideal', 'ideal_marginal'), ('placed', 'placed_marginal'),
                      ('routed', 'routed_marginal')):
        pairs = [(m['ideal_marginal'], m[key]) for m in merged
                 if m['ideal_marginal'] is not None and m[key] is not None]
        marg[name] = stage_stats(pairs, name)
    out['recomputed_marginal_block'] = marg
    out['shipped_marginal_block'] = tpc.get('stages_marginal')

    # ---------- CUMULATIVE block, corrected ----------
    cum = {}
    for name, key in (('ideal', 'ideal_cum_corrected'), ('placed', 'placed_cum'),
                      ('routed', 'routed_cum')):
        pairs = [(m['ideal_cum_corrected'], m[key]) for m in merged
                 if m['ideal_cum_corrected'] is not None and m[key] is not None]
        cum[name] = stage_stats(pairs, name)
    out['corrected_cumulative_block'] = cum
    out['shipped_cumulative_block'] = tpc.get('stages_cumulative')

    # ---------- how wrong was the shipped ideal cumulative column ----------
    d = [abs(m['ideal_cum_shipped'] - m['ideal_cum_corrected']) for m in merged
         if m['ideal_cum_shipped'] is not None and m['ideal_cum_corrected'] is not None]
    out['shipped_vs_corrected_ideal_cumulative'] = {
        'n_comparable': len(d),
        'n_differing': sum(1 for x in d if x > 1e-9),
        'mean_abs_diff_ns': round(sum(d) / len(d), 6) if d else None,
        'max_abs_diff_ns': round(max(d), 6) if d else None,
    }

    # ---------- the attenuation the user asked for: multi-round effect ----------
    # for every candidate that carries all three cumulative readings
    att = {}
    for name, key in (('placed', 'placed_cum'), ('routed', 'routed_cum')):
        pairs = [(m['ideal_cum_corrected'], m[key]) for m in merged
                 if m['ideal_cum_corrected'] is not None and m[key] is not None]
        if not pairs:
            continue
        ic = [a for a, _ in pairs]
        pc = [b for _, b in pairs]
        att[name] = {
            'n': len(pairs),
            'mean_ideal_cum': round(sum(ic) / len(ic), 6),
            'mean_physical_cum': round(sum(pc) / len(pc), 6),
            'mean_ratio_physical_over_ideal': round((sum(pc) / len(pc)) / (sum(ic) / len(ic)), 6)
            if sum(ic) != 0 else None,
            'n_ideal_improved_and_physical_improved': sum(1 for a, b in pairs if a > 0 and b > 0),
            'n_ideal_improved_but_physical_not': sum(1 for a, b in pairs if a > 0 and b <= 0),
            'n_ideal_not_but_physical_improved': sum(1 for a, b in pairs if a <= 0 and b > 0),
            'n_ideal_improved': sum(1 for a, _ in pairs if a > 0),
            'n_physical_improved': sum(1 for _, b in pairs if b > 0),
        }
    out['cumulative_attenuation_ideal_to_physical'] = att

    # ---------- per circuit, for a sanity view ----------
    per = defaultdict(lambda: {'n': 0, 'ideal_cum': [], 'placed_cum': [], 'routed_cum': []})
    for m in merged:
        if m['ideal_cum_corrected'] is None:
            continue
        p = per[m['circuit']]
        p['n'] += 1
        for k in ('ideal_cum_corrected', 'placed_cum', 'routed_cum'):
            if m[k] is not None:
                p[k.replace('_corrected', '')].append(m[k])
    out['per_circuit_cumulative'] = {
        c: {'n': p['n'],
            'mean_ideal_cum': round(sum(p['ideal_cum']) / len(p['ideal_cum']), 6) if p['ideal_cum'] else None,
            'mean_placed_cum': round(sum(p['placed_cum']) / len(p['placed_cum']), 6) if p['placed_cum'] else None,
            'mean_routed_cum': round(sum(p['routed_cum']) / len(p['routed_cum']), 6) if p['routed_cum'] else None,
            'n_ideal_improved': sum(1 for x in p['ideal_cum'] if x > 0),
            'n_routed_improved': sum(1 for x in p['routed_cum'] if x > 0)}
        for c, p in sorted(per.items())
    }

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
