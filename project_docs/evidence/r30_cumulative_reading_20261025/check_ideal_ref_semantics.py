"""Adjudicate what `acceptance_evidence.metric_references.setup_wns` actually is.

Question
--------
The training table carries, per candidate:
    ideal_wns           = setup_wns of the candidate
    ideal_baseline_wns  = metric_references.setup_wns of the candidate
    ideal_delta_wns     = ideal_wns - ideal_baseline_wns

The three-point-curve tool labels `ideal_delta_wns` as the MARGINAL effect
(against the netlist the candidate was derived from) and claims that
`ideal_wns - ideal_baseline_wns` is the CUMULATIVE effect (against the circuit
baseline netlist).  Both cannot be true at once: they are the same subtraction.

This script decides which reference `metric_references.setup_wns` is, using the
dataset itself (no re-implementation of the build logic):

  T1  is `ideal_baseline_wns` constant across iterations of a circuit?
      -> constant  => circuit baseline
      -> varies   => iteration base
  T2  for candidates whose iteration base is another CANDIDATE (iteration >= 2),
      does `ideal_baseline_wns` equal that candidate's `ideal_wns`?
      -> yes => the reference tracks the iteration base (MARGINAL reading)
      -> no  => the reference is the circuit baseline (CUMULATIVE reading)
  T3  same test on the physical side, where the two readings are known to be
      distinct: `post_delta_wns` (circuit baseline) vs
      `post_marginal_delta_wns` (iteration base).  This validates the test
      machinery itself.
  T4  how often does ideal_delta_wns == ideal_wns - ideal_baseline_wns hold
      (arithmetic tautology, but the COUNT is what the tool relies on), and
      does ideal_delta_wns ever differ from post_marginal-style marginal?

Output: JSON to stdout (English/ASCII keys only).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

FAM = Path(__file__).resolve().parent.parent / 'experiments/20261024_physical_labels_itc99'
DS = FAM / 'physical_dataset.jsonl'


def load():
    rows = []
    with DS.open(encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    rows = load()
    out = {'n_rows': len(rows), 'batches': sorted({r.get('batch') for r in rows})}

    # ---- T1: is the ideal reference constant within a circuit?
    by_ckt = defaultdict(list)
    for r in rows:
        if r.get('ideal_baseline_wns') is not None:
            by_ckt[r['circuit']].append((r.get('iteration'), r['ideal_baseline_wns'],
                                          r.get('key'), r.get('post_iter_base_key')))
    t1 = {}
    for ckt, v in sorted(by_ckt.items()):
        vals = sorted({w for _, w, _, _ in v})
        iters = sorted({i for i, _, _, _ in v if i is not None})
        t1[ckt] = {
            'n': len(v),
            'iterations': iters,
            'n_distinct_ideal_baseline_wns': len(vals),
            'values': vals[:8],
        }
    out['T1_ideal_reference_constant_within_circuit'] = t1

    # index candidates by key so the iteration base can be looked up
    by_key = {r.get('key'): r for r in rows}

    # ---- T2: for iteration >= 2 candidates whose iteration base is a candidate,
    #          does ideal_baseline_wns == that candidate's ideal_wns ?
    t2 = {'n_checked': 0, 'n_match_iter_base': 0, 'n_match_circuit_base': 0,
          'n_match_neither': 0, 'samples': []}
    circuit_base_wn = {}
    for r in rows:
        if r.get('kind') == 'BASE' or str(r.get('key', '')).startswith('base__'):
            circuit_base_wn[r['circuit']] = r.get('ideal_wns')
    for r in rows:
        ibk = r.get('post_iter_base_key')
        if not ibk or ibk.startswith('base__'):
            continue
        if r.get('ideal_baseline_wns') is None:
            continue
        t2['n_checked'] += 1
        ib = by_key.get(ibk)
        ib_ideal = ib.get('ideal_wns') if ib else None
        cb_ideal = circuit_base_wn.get(r['circuit'])
        if ib_ideal is not None and abs(r['ideal_baseline_wns'] - ib_ideal) < 1e-9:
            t2['n_match_iter_base'] += 1
            hit = 'iter_base'
        elif cb_ideal is not None and abs(r['ideal_baseline_wns'] - cb_ideal) < 1e-9:
            t2['n_match_circuit_base'] += 1
            hit = 'circuit_base'
        else:
            t2['n_match_neither'] += 1
            hit = 'neither'
        if len(t2['samples']) < 8:
            t2['samples'].append({
                'key': r.get('key'), 'iteration': r.get('iteration'),
                'ideal_wns': r.get('ideal_wns'),
                'ideal_baseline_wns': r.get('ideal_baseline_wns'),
                'iter_base_key': ibk, 'iter_base_ideal_wns': ib_ideal,
                'circuit_base_ideal_wns': cb_ideal, 'hit': hit,
            })
    out['T2_ideal_reference_tracks_iteration_base'] = t2

    # ---- T3: validate the machinery on the physical side, where the two
    #          readings are definitely different fields.
    t3 = {'n_checked': 0, 'n_post_delta_eq_base_minus_circuit': 0,
          'n_post_marginal_eq_base_minus_iter': 0, 'n_both_equal': 0,
          'n_differ': 0, 'n_ambiguous_both_zero': 0}
    for r in rows:
        ibk = r.get('post_iter_base_key')
        if not ibk:
            continue
        ib = by_key.get(ibk)
        if ib is None:
            continue
        if r.get('post_wns') is None or ib.get('post_wns') is None:
            continue
        t3['n_checked'] += 1
        d_circ = round(r['post_wns'] - (circuit_base_wn and 0 or 0), 6)  # placeholder
        # physical reference values
        p_circ = None
        for rr in rows:
            if rr.get('circuit') == r['circuit'] and str(rr.get('key', '')).startswith('base__'):
                p_circ = rr.get('post_wns')
                break
        d_circ = None if p_circ is None else round(r['post_wns'] - p_circ, 6)
        d_iter = round(r['post_wns'] - ib['post_wns'], 6)
        eq_circ = d_circ is not None and abs(d_circ - r.get('post_delta_wns', 1e9)) < 1e-6
        eq_iter = abs(d_iter - r.get('post_marginal_delta_wns', 1e9)) < 1e-6
        t3['n_post_delta_eq_base_minus_circuit'] += int(eq_circ)
        t3['n_post_marginal_eq_base_minus_iter'] += int(eq_iter)
        if eq_circ and eq_iter:
            t3['n_both_equal'] += 1
        else:
            t3['n_differ'] += 1
            if d_circ == 0 and d_iter == 0:
                t3['n_ambiguous_both_zero'] += 1
    out['T3_physical_side_machine_check'] = t3

    # ---- T4: how many rows would CHANGE if the ideal marginal were computed
    #          against the iteration base instead of metric_references?
    t4 = {'n_rows': 0, 'n_ideal_delta_available': 0,
          'n_ideal_delta_differs_from_iterbase_version': 0,
          'mean_ideal_delta_vs_reference': None,
          'mean_ideal_delta_vs_iterbase': None}
    s_ref = []
    s_itb = []
    for r in rows:
        t4['n_rows'] += 1
        if r.get('ideal_delta_wns') is None:
            continue
        t4['n_ideal_delta_available'] += 1
        s_ref.append(r['ideal_delta_wns'])
        ibk = r.get('post_iter_base_key')
        ib = by_key.get(ibk) if ibk else None
        if ib is not None and ib.get('ideal_wns') is not None and r.get('ideal_wns') is not None:
            v = round(r['ideal_wns'] - ib['ideal_wns'], 6)
            s_itb.append(v)
            if abs(v - r['ideal_delta_wns']) > 1e-9:
                t4['n_ideal_delta_differs_from_iterbase_version'] += 1
    if s_ref:
        t4['mean_ideal_delta_vs_reference'] = round(sum(s_ref) / len(s_ref), 6)
    if s_itb:
        t4['mean_ideal_delta_vs_iterbase'] = round(sum(s_itb) / len(s_itb), 6)
        t4['n_comparable'] = len(s_itb)
    out['T4_ideal_delta_vs_iteration_base_version'] = t4

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
