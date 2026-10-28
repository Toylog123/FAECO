"""HOW BIG IS THE TWO-IMPLEMENTATION AVERAGE EFFECT, REALLY?  (C3, continued)

The pre-registered C3 criterion was a sign test on the net score of each
(pool, hold-out) pair.  On this family it read "27 better / 92 ties / 25
worse, p = 0.8899" and the conclusion was "no support for averaging two
realisations".

f2_c3_mechanism.py showed WHY the sign test is uninformative here:

  * where the held-out realisation coincides with the single picker's
    realisation, the single picker is already exact (regret 0 in every pool)
    and averaging can only tie or lose  -> the sign is forced;
  * where all three realisations differ, averaging is close to a coin flip
    (21 wins / 18 losses);
  * the two forced signs cancel, so the family-level sign test is a wash.

But on the non-degenerate subset the MEAN regret does drop (F0: 0.015625 ->
0.011875 ns).  The sign test cannot see that, because the per-pool
improvements are smaller than the 0.01 ns quantum of the measurement.

This tool measures the effect properly:
  * a PAIRED per-pool regret difference (single minus averaged), per
    (pool, hold-out, picker pair);
  * a sign test and a bootstrap CI of the mean paired difference
    (resampling POOLS, the unit of independence);
  * a Wilcoxon signed-rank statistic (normal approximation, tie-corrected);
  * the effect expressed in units of the 0.01 ns measurement quantum;
  * the same split by the degeneracy label.

Output: scratch/f2_c3_paired_effect.json
"""
import json
import math
import random
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
OUT = REPO / 'scratch/f2_c3_paired_effect.json'
QUANTUM_NS = 0.01
BOOT = 5000
SEED = 20261025

REALS = ('F0', 'F1', 'F2')

rows = isp.load_rows(FAM_DIR) + isp.load_f2_rows(FAM_DIR)
real_of_batch = {}
for name, batches in SETUP['realisations'].items():
    for b in batches:
        real_of_batch[b] = name

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

# --- the degeneracy labels (same construction as f2_c3_mechanism) -----------
circuits = sorted({k[0] for k in meta})
degenerate = {}
for ckt in circuits:
    d = {}
    for a, b in (('F0', 'F1'), ('F0', 'F2'), ('F1', 'F2')):
        same = tot = 0
        for (c, _k), vals in by.items():
            if c != ckt or a not in vals or b not in vals:
                continue
            tot += 1
            if vals[a] == vals[b]:
                same += 1
        rec = {'identical_for_all': bool(tot and same == tot),
               'n_identical': same, 'n_pairs': tot}
        d['%s_vs_%s' % (a, b)] = rec
        d['%s_vs_%s' % (b, a)] = rec
    degenerate[ckt] = d


def label(hold_out, r_prime, r_second, ckt):
    d = degenerate[ckt]
    if d['%s_vs_%s' % (hold_out, r_prime)]['identical_for_all']:
        return 'truth_equals_single_picker'
    if d['%s_vs_%s' % (hold_out, r_second)]['identical_for_all']:
        return 'truth_equals_second_averaged'
    return 'all_three_differ'


# --- the paired differences -------------------------------------------------
# one record per (pool, hold_out, picker pair): the two candidate regrets and
# the difference single - averaged (positive = averaging helped)
recs = []
for pkey, cands in sorted(pools.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    if len(cands) < 2:
        continue
    ckt = pkey[0]
    for hold_out in REALS:
        others = [x for x in REALS if x != hold_out]
        for r_prime in others:
            r_second = [x for x in others if x != r_prime][0]
            best = max(v[hold_out] for _, v in cands)
            p_single = max(cands, key=lambda kv: kv[1][r_prime])
            p_avg = max(cands, key=lambda kv: (kv[1][r_prime] + kv[1][r_second]) / 2.0)
            r_s = best - p_single[1][hold_out]
            r_a = best - p_avg[1][hold_out]
            recs.append({
                'pool': '%s iter %s' % pkey, 'circuit': ckt, 'hold_out': hold_out,
                'single_picker': r_prime, 'second_averaged': r_second,
                'label': label(hold_out, r_prime, r_second, ckt),
                'regret_single_ns': r_s, 'regret_averaged_ns': r_a,
                'diff_ns': r_s - r_a,          # positive = averaging helped
                'pick_changed': p_single[0] != p_avg[0],
            })


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


def wilcoxon(diffs):
    """Signed-rank statistic with the normal approximation and a tie
    correction.  diffs are the paired differences (positive = averaging
    helped)."""
    nz = [d for d in diffs if abs(d) > 1e-15]
    n = len(nz)
    if n == 0:
        return {'n_nonzero': 0, 'W_plus': 0, 'z': None, 'p_two_sided': None}
    order = sorted(range(n), key=lambda i: abs(nz[i]))
    ranks = [0.0] * n
    i = 0
    tie_groups = []
    while i < n:
        j = i
        while j + 1 < n and abs(abs(nz[order[j + 1]]) - abs(nz[order[i]])) < 1e-15:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        tie_groups.append(j - i + 1)
        i = j + 1
    w_plus = sum(r for r, d in zip(ranks, nz) if d > 0)
    tie_term = sum((t ** 3 - t) for t in tie_groups) / 48.0
    mean_w = n * (n + 1) / 4.0
    sd_w = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0 - tie_term)
    z = (w_plus - mean_w) / sd_w if sd_w > 0 else None
    p = None
    if z is not None:
        p = round(min(1.0, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))), 4)
    return {'n_nonzero': n, 'W_plus': round(w_plus, 3), 'z': round(z, 4) if z else z,
            'p_two_sided': p}


def boot_mean_ci(diffs, by_pool, n_boot=BOOT, seed=SEED):
    """Bootstrap CI of the mean paired difference, resampling POOLS (the unit
    of independence), not individual comparisons."""
    if not diffs:
        return None
    groups = defaultdict(list)
    for d, pool in zip(diffs, by_pool):
        groups[pool].append(d)
    keys = sorted(groups)
    means = []
    rng = random.Random(seed)
    for _ in range(n_boot):
        samp = []
        for _k in keys:
            samp.extend(groups[keys[rng.randrange(len(keys))]])
        if samp:
            means.append(sum(samp) / len(samp))
    means.sort()
    m = len(means)
    return {'n_resamples': n_boot, 'seed': seed,
            'ci95': [round(means[int(0.025 * m)], 6), round(means[int(0.975 * m)], 6)],
            'median': round(means[m // 2], 6),
            'frac_above_zero': round(sum(1 for x in means if x > 0) / m, 6)}


def describe(subset, tag):
    diffs = [r['diff_ns'] for r in subset]
    pools_of = [r['pool'] for r in subset]
    pos = sum(1 for d in diffs if d > 1e-15)
    neg = sum(1 for d in diffs if d < -1e-15)
    ties = len(diffs) - pos - neg
    mean_d = sum(diffs) / len(diffs) if diffs else None
    mean_s = (sum(r['regret_single_ns'] for r in subset) / len(subset)) if subset else None
    mean_a = (sum(r['regret_averaged_ns'] for r in subset) / len(subset)) if subset else None
    out = {
        'tag': tag,
        'n_comparisons': len(subset),
        'n_pools': len(set(pools_of)),
        'mean_regret_single_ns': round(mean_s, 6) if mean_s is not None else None,
        'mean_regret_averaged_ns': round(mean_a, 6) if mean_a is not None else None,
        'mean_paired_improvement_ns': round(mean_d, 6) if mean_d is not None else None,
        'mean_paired_improvement_in_quantum': (round(mean_d / QUANTUM_NS, 4)
                                              if mean_d is not None else None),
        'sign_test': {'averaging_better': pos, 'single_better': neg, 'ties': ties,
                      'exact_binomial_p': exact_binom_p(pos, neg)},
        'wilcoxon': wilcoxon(diffs),
        'bootstrap_mean_ci': boot_mean_ci(diffs, pools_of),
        'pick_change_rate': (round(sum(1 for r in subset if r['pick_changed']) / len(subset), 6)
                              if subset else None),
    }
    return out


groups = {}
groups['full_family'] = describe(recs, 'all comparisons (as published)')
non_deg = sorted(c for c in circuits
                 if all(not v['identical_for_all'] for v in degenerate[c].values()))
groups['non_degenerate_circuits'] = describe(
    [r for r in recs if r['circuit'] in non_deg],
    'circuits where all three realisations differ: %s' % '／'.join(non_deg))
groups['degenerate_circuits'] = describe(
    [r for r in recs if r['circuit'] not in non_deg],
    'circuits with at least one degenerate pair')
for lab in ('truth_equals_single_picker', 'truth_equals_second_averaged',
            'all_three_differ'):
    groups['label_' + lab] = describe([r for r in recs if r['label'] == lab], lab)
for ho in REALS:
    groups['hold_out_' + ho] = describe([r for r in recs if r['hold_out'] == ho],
                                         'held-out realisation %s' % ho)

out = {
    'question': ('how large is the two-implementation averaging effect, measured '
                 'with a PAIRED statistic instead of the pre-registered sign '
                 'test on the net score?'),
    'key': ('the sign test can only see the SIGN of the per-pool change, and the '
            'degeneracy structure forces the sign in 20 of the 42 cells -- so the '
            'family-level wash hides an effect that is present in the MEAN'),
    'quantum_ns': QUANTUM_NS,
    'n_comparisons': len(recs),
    'n_pools': len(set(r['pool'] for r in recs)),
    'circuits': circuits,
    'non_degenerate_circuits': non_deg,
    'groups': groups,
    'interpretation_rules': {
        'positive_mean_paired_improvement': 'averaging reduced the regret',
        'the_effect_must_be_read_in_quanta': ('the post-route WNS is quantised to '
                                               '0.01 ns, so an improvement below one '
                                               'quantum cannot change a discrete '
                                               'decision "which candidate to pick"'),
        'bootstrap_unit': 'the POOL (the unit of independence); comparisons inside a '
                          'pool are not independent',
    },
    'boundary': ('PROBE level, NOT paper evidence.  The three realisation '
                 'differences are algebraically dependent (d_F0F2 = d_F0F1 + d_F1F2). '
                 'The non-degenerate subset has only %d circuits, so any verdict '
                 'there has very low power.  The Wilcoxon statistic is a normal '
                 'approximation with a tie correction, not an exact test.' % len(non_deg)),
}
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

print('n comparisons: %d   n pools: %d   quantum: %s ns' % (len(recs), out['n_pools'], QUANTUM_NS))
print()
for tag in ('full_family', 'non_degenerate_circuits', 'degenerate_circuits',
            'label_truth_equals_single_picker', 'label_truth_equals_second_averaged',
            'label_all_three_differ', 'hold_out_F0', 'hold_out_F1', 'hold_out_F2'):
    g = groups[tag]
    ci = g['bootstrap_mean_ci'] or {}
    print('%-36s n=%-4d mean regret %s -> %s   paired improvement %s ns (%s quantum)'
          % (tag, g['n_comparisons'], g['mean_regret_single_ns'],
             g['mean_regret_averaged_ns'], g['mean_paired_improvement_ns'],
             g['mean_paired_improvement_in_quantum']))
    print('%-36s   sign %d/%d/%d p=%s | wilcoxon z=%s p=%s | boot CI95 %s'
          % ('', g['sign_test']['averaging_better'], g['sign_test']['ties'],
             g['sign_test']['single_better'], g['sign_test']['exact_binomial_p'],
             g['wilcoxon']['z'], g['wilcoxon']['p_two_sided'], ci.get('ci95')))
print()
print('wrote %s' % OUT)
