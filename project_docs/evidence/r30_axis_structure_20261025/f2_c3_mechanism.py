"""WHY DID THE TWO-IMPLEMENTATION AVERAGE FAIL HERE?  (OI-052 item 30)

C3 (pre-registered in LOG-20261024-25) asks: should a picker that scores
candidates on the MEAN of two realisations beat a picker that scores them on a
SINGLE realisation, when both are judged by a held-out third realisation?

On this family it did NOT (27 better / 92 ties / 25 worse, p = 0.8899), even
though the synthetic fixture reproduced the advantage (38/85/21, p = 0.0363).
The open question in OI-052 item 30 was: is the implementation effect ONE
degree of freedom, or candidate-specific multi-dimensional noise?

LOG-20261025-30 supplies the missing ingredient.  The three realisations are NOT
three distinct points in implementation space: F0 == F2 on b02/b08/b09/b13 and
F1 == F2 on b10.  That makes a sharp, falsifiable prediction about the
leave-one-out comparison:

    If the HELD-OUT realisation coincides with the SINGLE-realisation picker's
    realisation, the single picker is already EXACT (its regret is 0 for every
    pool), so averaging can only tie or lose -- it has nothing to gain and the
    other realisation's noise to lose.
    If the held-out realisation coincides with the OTHER averaged realisation,
    averaging is a shrinkage toward the truth and should help.
    On circuits where all three differ, averaging should behave like the
    synthetic fixture.

This tool:
  1. re-implements the leave-one-out comparison with a PER-CIRCUIT breakdown
     and checks it reproduces the published numbers exactly (control pass);
  2. labels every (hold-out, picker, circuit) cell with the degeneracy
     structure and tests the prediction;
  3. re-runs C3 on the non-degenerate subset {b01, b03}, where all three
     realisations genuinely differ.

Output: scratch/f2_c3_mechanism.json
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))
import impl_stability_probe as isp  # noqa: E402

FAM = 'itc99'
FAM_DIR = isp.FAM_DIRS[FAM]
SETUP = isp.FAMILY_SETUP[FAM]
OUT = REPO / 'scratch/f2_c3_mechanism.json'
PUBLISHED = REPO / 'experiments/20261024_physical_labels_itc99/impl_stability.json'

REALS = ('F0', 'F1', 'F2')


def exact_binom_p(wins, losses):
    n = wins + losses
    if n == 0:
        return None
    k = min(wins, losses)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    p = min(1.0, 2 * tail)
    r = round(p, 4)
    # the 4-decimal rounding is for display; it must never turn a non-zero
    # p into 0.0 (the forced-sign groups have p = 3.1e-05)
    return p if r == 0.0 else r


rows = isp.load_rows(FAM_DIR) + isp.load_f2_rows(FAM_DIR)

real_of_batch = {}
for name, batches in SETUP['realisations'].items():
    for b in batches:
        real_of_batch[b] = name

# --- the three realisations per candidate -----------------------------------
by = defaultdict(dict)
meta = {}
for r in rows:
    if r.get('post_status') != 'ok' or r.get('post_wns') is None:
        continue
    real = real_of_batch.get(r.get('batch'))
    if real is None:
        continue
    by[(r.get('circuit'), r.get('key'))][real] = r['post_wns']
    meta[(r.get('circuit'), r.get('key'))] = (r.get('circuit'), r.get('iteration'))

pools = defaultdict(list)
for (ckt, key), vals in by.items():
    if len(vals) < 3:
        continue
    pools[meta[(ckt, key)]].append((key, vals))

# --- the degeneracy structure, per circuit ----------------------------------
circuits = sorted({k[0] for k in meta})
degenerate = {}
for ckt in circuits:
    d = {}
    for a, b in (('F0', 'F1'), ('F0', 'F2'), ('F1', 'F2')):
        same = 0
        tot = 0
        for (c, key), vals in by.items():
            if c != ckt:
                continue
            if a not in vals or b not in vals:
                continue
            tot += 1
            if vals[a] == vals[b]:
                same += 1
        rec = {'n_pairs': tot, 'n_identical': same,
               'identical_for_all': bool(tot and same == tot)}
        d['%s_vs_%s' % (a, b)] = rec
        d['%s_vs_%s' % (b, a)] = rec      # symmetric: the relation is symmetric
    degenerate[ckt] = d

non_degenerate = sorted(c for c in circuits
                        if all(not v['identical_for_all'] for v in degenerate[c].values()))

# --- the leave-one-out comparison, with a per-circuit breakdown -------------
# Semantics copied from impl_stability_probe.three_way_choice: per pool and per
# held-out realisation, the net score over the two ordered picker pairs is
# accumulated; a positive net means "averaging was better".
cells = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0,
                             'reg_single': [], 'reg_avg': [],
                             'n_pools': 0})
per_direction = {}
per_pool = []
for pkey, cands in sorted(pools.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    if len(cands) < 2:
        continue
    ckt = pkey[0]
    pool_entry = {'pool': '%s iter %s' % pkey, 'circuit': ckt,
                  'n_candidates': len(cands), 'directions': {}}
    for hold_out in REALS:
        others = [x for x in REALS if x != hold_out]
        reg_single, reg_avg, changed, better = [], [], 0, 0
        for r_prime in others:
            r_second = [x for x in others if x != r_prime][0]
            best = max(v[hold_out] for _, v in cands)
            p_single = max(cands, key=lambda kv: kv[1][r_prime])
            p_avg = max(cands, key=lambda kv: (kv[1][r_prime] + kv[1][r_second]) / 2.0)
            r_s = best - p_single[1][hold_out]
            r_a = best - p_avg[1][hold_out]
            reg_single.append(r_s)
            reg_avg.append(r_a)
            if p_single[0] != p_avg[0]:
                changed += 1
            if r_a < r_s:
                better += 1
            elif r_s < r_a:
                better -= 1
            # per-circuit cell
            cell = cells[(hold_out, r_prime, r_second, ckt)]
            cell['n_pools'] += 1
            cell['reg_single'].append(r_s)
            cell['reg_avg'].append(r_a)
            if r_a < r_s:
                cell['wins'] += 1
            elif r_s < r_a:
                cell['losses'] += 1
            else:
                cell['ties'] += 1
        e = {
            'regret_single_measurement_ns': round(sum(reg_single) / len(reg_single), 6),
            'regret_averaged_label_ns': round(sum(reg_avg) / len(reg_avg), 6),
            'n_comparisons': len(reg_single),
            'averaged_better': better,
            'single_better': -better,
            'ties': len(reg_single) - abs(better),
            'pick_changed_in': changed,
        }
        pool_entry['directions'][hold_out] = e
        per_direction.setdefault(hold_out, []).append(e)
    per_pool.append(pool_entry)

summary = {}
for hold_out, entries in per_direction.items():
    w = sum(1 for e in entries if e['averaged_better'] > 0)
    l = sum(1 for e in entries if e['single_better'] > 0)
    t = len(entries) - w - l
    summary[hold_out] = {
        'n_pools': len(entries),
        'regret_single_measurement_ns': round(
            sum(e['regret_single_measurement_ns'] for e in entries) / len(entries), 6),
        'regret_averaged_label_ns': round(
            sum(e['regret_averaged_label_ns'] for e in entries) / len(entries), 6),
        'averaged_better_pools': w,
        'single_better_pools': l,
        'ties': t,
        'exact_binomial_p': exact_binom_p(w, l),
    }
allw = sum(1 for e in per_direction.values() for x in e if x['averaged_better'] > 0)
alll = sum(1 for e in per_direction.values() for x in e if x['single_better'] > 0)
overall = {'n_pool_direction_pairs': sum(len(v) for v in per_direction.values()),
           'averaged_better': allw, 'single_better': alll,
           'ties': sum(len(v) for v in per_direction.values()) - allw - alll,
           'exact_binomial_p': exact_binom_p(allw, alll)}

# --- control pass against the published artefact -----------------------------
ctrl = {}
if PUBLISHED.exists():
    pub = json.loads(PUBLISHED.read_text(encoding='utf-8'))
    ptw = pub.get('three_way_choice') or {}
    ctrl['published_per_direction'] = ptw.get('per_direction')
    ctrl['published_overall'] = ptw.get('overall')
    ctrl['recomputed_per_direction'] = summary
    ctrl['recomputed_overall'] = overall
    ctrl['per_direction_match'] = {
        h: all(summary[h].get(k) == (ptw.get('per_direction') or {}).get(h, {}).get(k)
               for k in ('n_pools', 'averaged_better_pools', 'single_better_pools',
                         'ties', 'exact_binomial_p'))
        for h in summary}
    ctrl['overall_match'] = all(
        overall.get(k) == (ptw.get('overall') or {}).get(k)
        for k in ('n_pool_direction_pairs', 'averaged_better', 'single_better',
                  'ties', 'exact_binomial_p'))
    ctrl['control_pass'] = all(ctrl['per_direction_match'].values()) and ctrl['overall_match']

# --- the degeneracy-labelled cells ------------------------------------------
def label(hold_out, r_prime, r_second, ckt):
    """How does the held-out realisation relate to the two averaged ones here?"""
    d = degenerate[ckt]
    tp = d['%s_vs_%s' % (hold_out, r_prime)]['identical_for_all']
    ts = d['%s_vs_%s' % (hold_out, r_second)]['identical_for_all']
    if tp:
        return 'truth_equals_single_picker'
    if ts:
        return 'truth_equals_second_averaged'
    return 'all_three_differ'


cell_out = {}
for (hold_out, r_prime, r_second, ckt), c in sorted(cells.items()):
    lab = label(hold_out, r_prime, r_second, ckt)
    key = '%s|%s|%s|%s' % (hold_out, r_prime, r_second, ckt)
    cell_out[key] = {
        'hold_out': hold_out, 'single_picker': r_prime, 'second_averaged': r_second,
        'circuit': ckt, 'degeneracy_label': lab,
        'n_comparisons': c['wins'] + c['losses'] + c['ties'],
        'averaged_better': c['wins'], 'single_better': c['losses'], 'ties': c['ties'],
        'mean_regret_single_ns': round(sum(c['reg_single']) / len(c['reg_single']), 6)
        if c['reg_single'] else None,
        'mean_regret_averaged_ns': round(sum(c['reg_avg']) / len(c['reg_avg']), 6)
        if c['reg_avg'] else None,
        'max_regret_single_ns': round(max(c['reg_single']), 6) if c['reg_single'] else None,
    }

# --- PREDICTION 1: where the truth equals the single picker's realisation,
#                    the single picker's regret must be 0 and averaging can
#                    never win.
pred = {'statement': ('if the held-out realisation is IDENTICAL to the single '
                       'picker\'s realisation on that circuit, the single picker is '
                       'already exact (regret 0 in every comparison) and averaging '
                       'can only tie or lose -- it must never win'),
        'cells': [], 'violations': []}
for key, v in cell_out.items():
    if v['degeneracy_label'] != 'truth_equals_single_picker':
        continue
    pred['cells'].append(key)
    if v['averaged_better'] > 0:
        pred['violations'].append(key)
    if (v['max_regret_single_ns'] or 0.0) != 0.0:
        pred['violations'].append(key + ' (single picker regret not zero)')
pred['n_cells'] = len(pred['cells'])
pred['holds'] = not pred['violations']

# --- PREDICTION 2: where the truth equals the SECOND averaged realisation,
#                    averaging is a shrinkage toward the truth -> it must never
#                    be worse than the single picker in aggregate.
pred2 = {'statement': ('if the held-out realisation is IDENTICAL to the second '
                        'averaged realisation on that circuit, the mean is a '
                        'shrinkage toward the truth, so the averaged regret must '
                        'not exceed the single regret'),
         'cells': [], 'violations': []}
for key, v in cell_out.items():
    if v['degeneracy_label'] != 'truth_equals_second_averaged':
        continue
    pred2['cells'].append(key)
    if (v['mean_regret_averaged_ns'] or 0) > (v['mean_regret_single_ns'] or 0) + 1e-12:
        pred2['violations'].append(key)
pred2['n_cells'] = len(pred2['cells'])
pred2['holds'] = not pred2['violations']

# --- C3 re-run on the non-degenerate subset ---------------------------------
def rerun_on(circuit_subset, tag):
    sel = [e for e in per_pool if e['circuit'] in circuit_subset]
    d = {}
    for hold_out in REALS:
        ents = [e['directions'][hold_out] for e in sel]
        w = sum(1 for e in ents if e['averaged_better'] > 0)
        l = sum(1 for e in ents if e['single_better'] > 0)
        t = len(ents) - w - l
        d[hold_out] = {'n_pools': len(ents), 'averaged_better_pools': w,
                       'single_better_pools': l, 'ties': t,
                       'exact_binomial_p': exact_binom_p(w, l),
                       'mean_regret_single_ns': round(
                           sum(e['regret_single_measurement_ns'] for e in ents) / len(ents), 6)
                       if ents else None,
                       'mean_regret_averaged_ns': round(
                           sum(e['regret_averaged_label_ns'] for e in ents) / len(ents), 6)
                       if ents else None}
    aw = sum(1 for h in d for x in sel if x['directions'][h]['averaged_better'] > 0)
    al = sum(1 for h in d for x in sel if x['directions'][h]['single_better'] > 0)
    n = sum(d[h]['n_pools'] for h in d)
    return {'subset': tag, 'circuits': sorted(circuit_subset), 'per_direction': d,
            'overall': {'n_pool_direction_pairs': n, 'averaged_better': aw,
                        'single_better': al, 'ties': n - aw - al,
                        'exact_binomial_p': exact_binom_p(aw, al)}}


subsets = {
    'full_family': rerun_on(set(circuits), 'all 7 circuits (as published)'),
    'non_degenerate': rerun_on(set(non_degenerate),
                               'circuits where all three realisations differ: %s'
                               % '／'.join(non_degenerate)),
    'degenerate_only': rerun_on(set(circuits) - set(non_degenerate),
                                 'circuits where at least one pair is degenerate'),
}

out = {
    'question': ('why did the two-implementation average fail on this family when '
                 'the synthetic fixture reproduced the advantage?'),
    'key': ('LOG-20261025-30 established that the three realisations are NOT three '
            'distinct points: F0 == F2 on b02/b08/b09/b13 and F1 == F2 on b10.  That '
            'makes the leave-one-out averaging structurally powerless in the '
            'directions where the held-out realisation coincides with the single '
            'picker\'s realisation.'),
    'n_rows': len(rows),
    'n_pools': len(per_pool),
    'circuits': circuits,
    'non_degenerate_circuits': non_degenerate,
    'degeneracy_per_circuit': degenerate,
    'control_pass': ctrl,
    'recomputed_per_direction': summary,
    'recomputed_overall': overall,
    'cells': cell_out,
    'prediction_1_single_picker_already_exact': pred,
    'prediction_2_shrinkage_toward_truth': pred2,
    'subsets': subsets,
    'boundary': ('PROBE level, NOT paper evidence.  The three pairwise realisation '
                 'differences are algebraically dependent (d_F0F2 = d_F0F1 + d_F1F2), '
                 'so this is a mechanism check, not an independence test.  The '
                 'non-degenerate subset has only %d circuits, so its C3 verdict has '
                 'very low power -- it can REFUTE the advantage but cannot establish '
                 'it.  The post-route WNS is quantised to 0.01 ns, so a regret of '
                 '0.0000 ns means "the two picks are indistinguishable at the '
                 'quantum".  Parasitics come from estimate_parasitics, not signoff '
                 'RCX.' % len(non_degenerate)),
}
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

# --- print ------------------------------------------------------------------
print('CONTROL PASS vs the published artefact')
print('  per-direction match: %s' % json.dumps(ctrl.get('per_direction_match')))
print('  overall match      : %s' % ctrl.get('overall_match'))
print('  published overall  : %s' % json.dumps(ctrl.get('published_overall')))
print('  recomputed overall : %s' % json.dumps(overall))
print()
print('DEGENERACY STRUCTURE')
for c in circuits:
    d = degenerate[c]
    parts = []
    for k in ('F0_vs_F1', 'F0_vs_F2', 'F1_vs_F2'):
        v = d[k]
        parts.append('%s %d/%d%s' % (k.replace('_vs_', '/'), v['n_identical'],
                                      v['n_pairs'], ' *IDENTICAL*' if v['identical_for_all'] else ''))
    print('  %-5s %s' % (c, '  |  '.join(parts)))
print('  non-degenerate circuits: %s' % '／'.join(non_degenerate))
print()
print('PREDICTION 1 (the single picker is already exact -> averaging can never win)')
print('  cells: %d   violations: %d   holds: %s'
      % (pred['n_cells'], len(pred['violations']), pred['holds']))
for key in pred['violations'][:8]:
    print('    violation: %s' % key)
print()
print('PREDICTION 2 (shrinkage toward the truth -> averaging is not worse)')
print('  cells: %d   violations: %d   holds: %s'
      % (pred2['n_cells'], len(pred2['violations']), pred2['holds']))
for key in pred2['violations'][:8]:
    print('    violation: %s' % key)
print()
print('C3 BY SUBSET')
for tag in ('full_family', 'non_degenerate', 'degenerate_only'):
    s = subsets[tag]
    o = s['overall']
    print('  %-16s circuits=%-28s %d better / %d ties / %d worse   p=%s'
          % (tag, '／'.join(s['circuits']), o['averaged_better'], o['ties'],
             o['single_better'], o['exact_binomial_p']))
    for h in ('F0', 'F1', 'F2'):
        d = s['per_direction'][h]
        print('      %s: %d/%d/%d p=%s  regret single %s vs averaged %s'
              % (h, d['averaged_better_pools'], d['ties'], d['single_better_pools'],
                 d['exact_binomial_p'], d['mean_regret_single_ns'],
                 d['mean_regret_averaged_ns']))
print()
print('PER-CELL DETAIL (regret single -> averaged)')
for key in sorted(cell_out):
    v = cell_out[key]
    print('  %-42s %-28s %s -> %s   %d/%d/%d'
          % (key, v['degeneracy_label'], v['mean_regret_single_ns'],
             v['mean_regret_averaged_ns'], v['averaged_better'], v['ties'],
             v['single_better']))
print()
print('wrote %s' % OUT)
