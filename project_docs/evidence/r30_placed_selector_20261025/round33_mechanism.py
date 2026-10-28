"""Round 33 mechanism: WHY was the placed criterion worth nothing?

The pre-registered decision-level comparison came out null (H1 not triggered
in both families).  A null verdict alone is not a finding, and per the
project's own discipline (LOG-20261025-31) "the data no longer supports the
claim" is NOT "the opposite has been proven".  So before landing anything we
run the two checks that decide what the null actually MEANS:

  D1  rank agreement -- inside the gate-eligible set, how much does the ideal
      ranking and the placed ranking agree at all?  (Spearman, ties-aware,
      per decision + pooled)
  D2  disagreement analysis -- on the decisions where the two criteria DO pick
      different candidates, how large is the post-route (routed) gain
      difference?  Is it at the 0.01 ns quantum level?
  D3  STRONGEST COMPETING BASELINE -- a random eligible candidate.  If the
      ideal criterion itself cannot beat a random pick at the decision level,
      then "the placed criterion is no better" is the wrong conclusion: the
      right conclusion is "no criterion is better than chance here".
      This is the check that separates the two readings.
  D4  headroom -- how much post-route gain the oracle holds over the ideal
      choice (the size of the prize) and how much of it placed captured.
  D5  quantum -- are the routed deltas quantised, and at what granularity?

Everything is recomputed here from the same sources as the tool
(scratch/round33_placed_selector.py); the tool's own functions are imported and
re-used, not copied, so the two cannot drift apart.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scratch'))
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))
import round33_placed_selector as tool   # noqa: E402
import resolvable_positive_classifier as rpc  # noqa: E402

N_SEEDS = 200
SEED0 = 20261025


# ---------------------------------------------------------------- ranks
def avg_ranks(xs):
    """Tie-aware average ranks (1-based)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return None
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return num / (va ** 0.5 * vb ** 0.5)


def spearman(a, b):
    return pearson(avg_ranks(a), avg_ranks(b))


def is_quantum(x, q=0.01):
    if x is None:
        return None
    y = x / q
    return abs(y - round(y)) < 1e-6


def family_diagnostics(name, fam_dir):
    rows = tool.load_training_table(fam_dir)
    allowed = tool.PRIMARY_BATCHES[name]
    primary = [r for r in rows if r.get('label_batch') in allowed]
    usable = [r for r in primary
              if r.get('ideal_delta_wns') is not None
              and r.get('placed_delta_wns') is not None
              and r.get('routed_delta_wns') is not None]
    pools = {}
    for r in usable:
        pools.setdefault((r.get('circuit'), str(r.get('iteration'))), []).append(r)
    ledger = tool.load_ledger(tool.LEDGER_FAM[name])

    # ---- rebuild the same eligible sets the tool used
    per_dec = []
    for key in sorted(ledger, key=lambda k: (str(k[0]), str(k[1]))):
        pool = pools.get(key)
        if not pool or len(pool) < 2:
            continue
        matched = tool.match_trials(pool, ledger[key]['trials'])
        if not matched:
            continue
        eligible = [(r, t) for r, t in matched if t['eligible']]
        if len(eligible) < 2:
            continue
        per_dec.append({'circuit': key[0], 'iteration': key[1],
                        'eligible': eligible, 'matched': matched,
                        'accepted': ledger[key]['accepted']})

    # ---- D1 rank agreement inside the eligible set
    d1 = []
    for d in per_dec:
        el = d['eligible']
        ideal = [float(r['ideal_delta_wns']) for r, _ in el]
        placed = [float(r['placed_delta_wns']) for r, _ in el]
        sp = spearman(ideal, placed)
        d1.append({'circuit': d['circuit'], 'iteration': d['iteration'],
                   'n_eligible': len(el), 'spearman_ideal_placed': sp})
    sps = [x['spearman_ideal_placed'] for x in d1
           if x['spearman_ideal_placed'] is not None]
    d1_summary = {
        'n_decisions': len(d1),
        'n_with_spearman': len(sps),
        'median_spearman': (round(sorted(sps)[len(sps) // 2], 6)
                             if sps else None),
        'mean_spearman': (round(sum(sps) / len(sps), 6) if sps else None),
        'min_spearman': (round(min(sps), 6) if sps else None),
        'n_spearman_ge_0_9': sum(1 for x in sps if x >= 0.9),
        'n_spearman_lt_0_5': sum(1 for x in sps if x < 0.5),
        'note': 'Spearman between the ideal and the placed marginal delta '
                'inside the gate-eligible set of one ECO decision',
    }

    # ---- D2 disagreement analysis
    dis = []
    for d in per_dec:
        el = d['eligible']
        ideal_el = min(el, key=lambda p: (-p[0]['ideal_delta_wns'],
                                          p[0]['key']))
        placed_el = min(el, key=lambda p: (-p[0]['placed_delta_wns'],
                                            p[0]['key']))
        same = ideal_el[0]['key'] == placed_el[0]['key']
        g_i = round(float(ideal_el[0]['routed_delta_wns']), 6)
        g_p = round(float(placed_el[0]['routed_delta_wns']), 6)
        dis.append({
            'circuit': d['circuit'], 'iteration': d['iteration'],
            'same_candidate': same,
            'n_eligible': len(el),
            'gain_ideal': g_i, 'gain_placed': g_p,
            'routed_diff': round(g_p - g_i, 6),
            'ideal_delta_gap': round(float(placed_el[0]['ideal_delta_wns'])
                                     - float(ideal_el[0]['ideal_delta_wns']), 6),
            'placed_delta_gap': round(float(placed_el[0]['placed_delta_wns'])
                                      - float(ideal_el[0]['placed_delta_wns']), 6),
        })
    disagree = [x for x in dis if not x['same_candidate']]
    d2 = {
        'n_decisions': len(dis),
        'n_disagree': len(disagree),
        'frac_disagree': (round(len(disagree) / len(dis), 6)
                           if dis else None),
        'routed_diff_histogram': dict(Counter(
            '%+g' % x['routed_diff'] for x in disagree)),
        'n_disagree_with_zero_routed_diff': sum(1 for x in disagree
                                                if x['routed_diff'] == 0),
        'n_disagree_with_routed_diff_ge_0_01': sum(
            1 for x in disagree if abs(x['routed_diff']) >= 0.01),
        'sum_routed_diff_on_disagreement': round(
            sum(x['routed_diff'] for x in disagree), 6),
        'max_abs_routed_diff_on_disagreement': (
            round(max(abs(x['routed_diff']) for x in disagree), 6)
            if disagree else None),
        'mean_abs_ideal_delta_gap_on_disagreement': (
            round(sum(abs(x['ideal_delta_gap']) for x in disagree)
                  / len(disagree), 6) if disagree else None),
        'note': 'on the decisions where the ideal criterion and the placed '
                'criterion pick different candidates: what does the '
                'post-route gain difference look like?',
    }

    # ---- D3 the strongest competing baseline: a random eligible candidate
    rng_results = []
    for si in range(N_SEEDS):
        rng = random.Random(SEED0 + si)
        diffs = []
        for d in per_dec:
            el = d['eligible']
            ideal_el = min(el, key=lambda p: (-p[0]['ideal_delta_wns'],
                                              p[0]['key']))
            pick = el[rng.randrange(len(el))]
            diffs.append(round(float(pick[0]['routed_delta_wns'])
                               - float(ideal_el[0]['routed_delta_wns']), 6))
        p, pos, neg = rpc.sign_test_p(diffs)
        rng_results.append({'seed': SEED0 + si, 'sign_test_p': p,
                            'wins_random': pos, 'losses_random': neg,
                            'mean_diff': round(sum(diffs) / len(diffs), 6)})
    ps = [r['sign_test_p'] for r in rng_results
          if r['sign_test_p'] is not None]
    # ---- D3b POSITIVE CONTROL: the same test against the oracle.  If the
    # oracle cannot beat a random pick either, the test has no resolution and
    # "the ideal criterion is no better than chance" would be a statement
    # about the instrument, not about the data.
    rng_oracle = []
    for si in range(N_SEEDS):
        rng = random.Random(SEED0 + si)
        diffs = []
        for d in per_dec:
            el = d['eligible']
            oracle = min(d['matched'],
                         key=lambda p: (-p[0]['routed_delta_wns'], p[0]['key']))
            pick = el[rng.randrange(len(el))]
            diffs.append(round(float(pick[0]['routed_delta_wns'])
                               - float(oracle[0]['routed_delta_wns']), 6))
        p, pos, neg = rpc.sign_test_p(diffs)
        rng_oracle.append({'seed': SEED0 + si, 'sign_test_p': p,
                            'wins_random': pos, 'losses_random': neg,
                            'mean_diff': round(sum(diffs) / len(diffs), 6)})
    pso = [r['sign_test_p'] for r in rng_oracle
           if r['sign_test_p'] is not None]
    d3b = {
        'n_seeds': N_SEEDS,
        'n_seeds_with_p': len(pso),
        'median_p': (sorted(pso)[len(pso) // 2] if pso else None),
        'min_p': (min(pso) if pso else None),
        'max_p': (max(pso) if pso else None),
        'frac_p_below_0_05': (round(sum(1 for x in pso if x < 0.05) / len(pso), 6)
                               if pso else None),
        'mean_diff_median': (round(
            sorted(r['mean_diff'] for r in rng_oracle)[N_SEEDS // 2], 6)
            if rng_oracle else None),
        'note': 'POSITIVE CONTROL: random eligible candidate vs the routed '
                'oracle over the same seeds.  This is the resolution check '
                'of the decision-level instrument itself.',
    }

    # ---- D6 is the ideal criterion significantly worse than the oracle?
    head_diffs = []
    for d in per_dec:
        el = d['eligible']
        ideal_el = min(el, key=lambda p: (-p[0]['ideal_delta_wns'],
                                          p[0]['key']))
        oracle = min(d['matched'], key=lambda p: (-p[0]['routed_delta_wns'],
                                                  p[0]['key']))
        head_diffs.append(round(float(oracle[0]['routed_delta_wns'])
                                - float(ideal_el[0]['routed_delta_wns']), 6))
    p6, pos6, neg6 = rpc.sign_test_p(head_diffs)
    d6 = {
        'n': len(head_diffs),
        'statistic': 'routed gain of the oracle minus that of the ideal '
                     'criterion, per decision',
        'wins_oracle': pos6, 'losses_oracle': neg6,
        'sign_test_p': p6,
        'mean_diff': (round(sum(head_diffs) / len(head_diffs), 6)
                      if head_diffs else None),
        'n_zero': sum(1 for x in head_diffs if x == 0),
        'note': 'if the oracle is NOT significantly better than the ideal '
                'criterion, then this dataset has no decision-level signal '
                'to redistribute, and moving the criterion cannot pay off',
    }

    d3 = {
        'n_seeds': N_SEEDS,
        'seed0': SEED0,
        'n_seeds_with_p': len(ps),
        # NOT rounded to a fixed point: a p of ~1e-8 would be flattened to
        # 0.000000, which reads as "p = 0" and over-claims.
        'median_p': (sorted(ps)[len(ps) // 2] if ps else None),
        'frac_p_below_0_05': (round(sum(1 for x in ps if x < 0.05) / len(ps), 6)
                               if ps else None),
        'frac_p_above_0_05': (round(sum(1 for x in ps if x >= 0.05) / len(ps), 6)
                               if ps else None),
        'mean_diff_median': (round(
            sorted(r['mean_diff'] for r in rng_results)[N_SEEDS // 2], 6)
            if rng_results else None),
        'mean_diff_min': (round(min(r['mean_diff'] for r in rng_results), 6)
                          if rng_results else None),
        'mean_diff_max': (round(max(r['mean_diff'] for r in rng_results), 6)
                          if rng_results else None),
        'note': 'random eligible candidate vs the ideal-criterion choice, '
                'paired sign test per seed; if the ideal criterion cannot '
                'beat chance either, the null is about the CRITERION, not '
                'about the placed stage',
    }

    # ---- D4 headroom
    heads = []
    for d in per_dec:
        el = d['eligible']
        ideal_el = min(el, key=lambda p: (-p[0]['ideal_delta_wns'],
                                          p[0]['key']))
        placed_el = min(el, key=lambda p: (-p[0]['placed_delta_wns'],
                                            p[0]['key']))
        oracle = min(d['matched'], key=lambda p: (-p[0]['routed_delta_wns'],
                                                  p[0]['key']))
        heads.append({
            'circuit': d['circuit'], 'iteration': d['iteration'],
            'gain_ideal': round(float(ideal_el[0]['routed_delta_wns']), 6),
            'gain_placed': round(float(placed_el[0]['routed_delta_wns']), 6),
            'gain_oracle': round(float(oracle[0]['routed_delta_wns']), 6),
        })
    sum_i = sum(h['gain_ideal'] for h in heads)
    sum_p = sum(h['gain_placed'] for h in heads)
    sum_o = sum(h['gain_oracle'] for h in heads)
    d4 = {
        'n_decisions': len(heads),
        'sum_gain_ideal': round(sum_i, 6),
        'sum_gain_placed': round(sum_p, 6),
        'sum_gain_oracle': round(sum_o, 6),
        'headroom_oracle_minus_ideal': round(sum_o - sum_i, 6),
        'headroom_per_decision': (round((sum_o - sum_i) / len(heads), 6)
                                   if heads else None),
        'placed_captured_fraction': (round((sum_p - sum_i) / (sum_o - sum_i), 6)
                                     if (sum_o - sum_i) > 0 else None),
        'ideal_share_of_oracle_gain': (round(sum_i / sum_o, 6)
                                       if sum_o != 0 else None),
        'n_oracle_below_ideal': sum(1 for h in heads
                                    if h['gain_oracle'] < h['gain_ideal']),
        'note': 'the oracle is the routed-delta maximum over the SAME '
                'eligible set, so headroom is the prize the ideal criterion '
                'leaves on the table',
    }

    # ---- D5 quantum
    all_routed = [float(r['routed_delta_wns'])
                  for d in per_dec for r, _ in d['matched']]
    all_ideal = [float(r['ideal_delta_wns'])
                 for d in per_dec for r, _ in d['matched']]
    all_placed = [float(r['placed_delta_wns'])
                  for d in per_dec for r, _ in d['matched']]
    d5 = {
        'n_values': len(all_routed),
        'n_routed_multiple_of_0_01': sum(1 for x in all_routed
                                          if is_quantum(x)),
        'n_ideal_multiple_of_0_01': sum(1 for x in all_ideal if is_quantum(x)),
        'n_placed_multiple_of_0_01': sum(1 for x in all_placed
                                         if is_quantum(x)),
        'min_abs_nonzero_routed': (round(min(abs(x) for x in all_routed
                                             if x != 0), 6)
                                   if any(x != 0 for x in all_routed) else None),
        'distinct_abs_routed_diff_values': sorted(set(
            abs(x['routed_diff']) for x in disagree)),
        'note': 'the routed stage is quantised; the decision-level effect '
                'must be read against that grid',
    }

    # ---- D7 the missing link: how good is each cheap criterion as a
    # WITHIN-ELIGIBLE-SET ranker of the ROUTED outcome?  The decision-level
    # prize is only reachable by a criterion that ranks the routed delta
    # inside the eligible set; this measures the two candidates for that
    # job directly (and compares them with the oracle's own ranking, which
    # is 1 by construction).
    d7_rows = []
    for d in per_dec:
        el = d['eligible']
        ideal = [float(r['ideal_delta_wns']) for r, _ in el]
        placed = [float(r['placed_delta_wns']) for r, _ in el]
        routed = [float(r['routed_delta_wns']) for r, _ in el]
        sp_ir = spearman(ideal, routed)
        sp_pr = spearman(placed, routed)
        d7_rows.append({
            'circuit': d['circuit'], 'iteration': d['iteration'],
            'n_eligible': len(el),
            'spearman_ideal_vs_routed': sp_ir,
            'spearman_placed_vs_routed': sp_pr,
            'spearman_placed_minus_ideal': (None if (sp_ir is None
                                                     or sp_pr is None)
                                            else round(sp_pr - sp_ir, 6)),
        })
    sir = [x['spearman_ideal_vs_routed'] for x in d7_rows
           if x['spearman_ideal_vs_routed'] is not None]
    spr = [x['spearman_placed_vs_routed'] for x in d7_rows
           if x['spearman_placed_vs_routed'] is not None]
    dif = [x['spearman_placed_minus_ideal'] for x in d7_rows
           if x['spearman_placed_minus_ideal'] is not None]
    p7, pos7, neg7 = rpc.sign_test_p(dif)
    d7 = {
        'n_decisions': len(d7_rows),
        'n_with_spearman_both': len(dif),
        'n_spearman_undefined': len(d7_rows) - len(dif),
        'undefined_reason': 'the Spearman is undefined when the eligible set '
                            'has a constant ideal or a constant routed delta '
                            '-- such a decision carries no rank information '
                            'at all',
        'median_spearman_ideal_vs_routed': (round(sorted(sir)[len(sir) // 2], 6)
                                            if sir else None),
        'median_spearman_placed_vs_routed': (round(sorted(spr)[len(spr) // 2], 6)
                                             if spr else None),
        'mean_spearman_ideal_vs_routed': (round(sum(sir) / len(sir), 6)
                                          if sir else None),
        'mean_spearman_placed_vs_routed': (round(sum(spr) / len(spr), 6)
                                           if spr else None),
        'paired_diff_placed_minus_ideal': {
            'wins': pos7, 'losses': neg7, 'sign_test_p': p7,
            'mean_diff': (round(sum(dif) / len(dif), 6) if dif else None),
            'n': len(dif),
        },
        'n_placed_better': sum(1 for x in dif if x > 0),
        'n_ideal_better': sum(1 for x in dif if x < 0),
        'per_decision': d7_rows,
        'note': 'within the gate-eligible set, the rank correlation of each '
                'cheap criterion with the ROUTED delta -- i.e. how good a '
                'within-decision ranker each criterion actually is',
    }

    # ---- D8 sparsity: how many of the eligible candidates carry a real
    # physical effect at all?  A better ranker can only pay off if there is
    # something to rank.
    d8_rows = []
    tot_el = 0
    tot_zero = 0
    tot_pos = 0
    tot_neg = 0
    for d in per_dec:
        el = d['eligible']
        vals = [round(float(r['routed_delta_wns']), 6) for r, _ in el]
        nz = [v for v in vals if v > 0]
        tot_el += len(vals)
        tot_zero += sum(1 for v in vals if v == 0)
        tot_pos += len(nz)
        tot_neg += sum(1 for v in vals if v < 0)
        d8_rows.append({'circuit': d['circuit'], 'iteration': d['iteration'],
                        'n_eligible': len(vals),
                        'n_routed_positive': len(nz),
                        'n_routed_zero': sum(1 for v in vals if v == 0),
                        'n_routed_negative': sum(1 for v in vals if v < 0),
                        'n_unique_positive': len(set(nz))})
    d8 = {
        'n_decisions': len(d8_rows),
        'n_eligible_total': tot_el,
        'n_routed_zero': tot_zero,
        'frac_routed_zero': (round(tot_zero / tot_el, 6) if tot_el else None),
        'n_routed_positive': tot_pos,
        'n_routed_negative': tot_neg,
        'n_decisions_with_exactly_one_positive': sum(
            1 for x in d8_rows if x['n_unique_positive'] == 1),
        'n_decisions_with_zero_positive': sum(
            1 for x in d8_rows if x['n_routed_positive'] == 0),
        'n_decisions_with_2plus_positive': sum(
            1 for x in d8_rows if x['n_routed_positive'] >= 2),
        'median_n_eligible': (round(
            sorted(x['n_eligible'] for x in d8_rows)[len(d8_rows) // 2], 6)
            if d8_rows else None),
        'note': 'the eligible set of one decision: how many candidates carry '
                'a non-zero post-route effect.  A better ranker can only pay '
                'off if there is something to rank.',
    }

    return {'family': name, 'D1_rank_agreement': d1_summary,
            'D1_per_decision': d1,
            'D2_disagreement': d2,
            'D3_random_control': d3,
            'D3b_random_vs_oracle_control': d3b,
            'D6_oracle_vs_ideal': d6,
            'D7_within_pool_ranker_quality': d7,
            'D8_sparsity': d8,
            'D3_per_seed': rng_results,
            'D4_headroom': d4,
            'D5_quantum': d5,
            'D4_per_decision': heads}


def main():
    out = {}
    for name, fam_dir in tool.FAMS.items():
        print('=== %s ===' % name, flush=True)
        d = family_diagnostics(name, fam_dir)
        out[name] = d
        print('  D1 spearman(ideal,placed) in eligible sets: median %s  '
              '>=0.9 in %s/%s decisions'
              % (d['D1_rank_agreement']['median_spearman'],
                 d['D1_rank_agreement']['n_spearman_ge_0_9'],
                 d['D1_rank_agreement']['n_decisions']), flush=True)
        print('  D2 the two criteria disagree in %s/%s decisions; the routed '
              'gain difference on those: %s'
              % (d['D2_disagreement']['n_disagree'],
                 d['D2_disagreement']['n_decisions'],
                 d['D2_disagreement']['routed_diff_histogram']), flush=True)
        print('  D3 random eligible vs ideal criterion: median p %s, '
              'p<0.05 in %s of %s seeds, median mean diff %s'
              % (d['D3_random_control']['median_p'],
                 d['D3_random_control']['frac_p_below_0_05'],
                 d['D3_random_control']['n_seeds_with_p'],
                 d['D3_random_control']['mean_diff_median']), flush=True)
        print('  D3b POSITIVE CONTROL random vs oracle: median p %s, '
              'p<0.05 in %s of %s seeds'
              % (d['D3b_random_vs_oracle_control']['median_p'],
                 d['D3b_random_vs_oracle_control']['frac_p_below_0_05'],
                 d['D3b_random_vs_oracle_control']['n_seeds']), flush=True)
        print('  D6 oracle vs ideal criterion: %d/%d (w/l) p=%s mean diff %s'
              % (d['D6_oracle_vs_ideal']['wins_oracle'],
                 d['D6_oracle_vs_ideal']['losses_oracle'],
                 d['D6_oracle_vs_ideal']['sign_test_p'],
                 d['D6_oracle_vs_ideal']['mean_diff']), flush=True)
        print('  D4 headroom oracle-ideal %s ns over %s decisions; placed '
              'captured %s'
              % (d['D4_headroom']['headroom_oracle_minus_ideal'],
                 d['D4_headroom']['n_decisions'],
                 d['D4_headroom']['placed_captured_fraction']), flush=True)
        print('  D7 within-pool ranker quality (Spearman vs the routed '
              'delta): ideal %s / placed %s (median); paired placed-ideal '
              '%d/%d p=%s'
              % (d['D7_within_pool_ranker_quality']
                ['median_spearman_ideal_vs_routed'],
                 d['D7_within_pool_ranker_quality']
                ['median_spearman_placed_vs_routed'],
                 d['D7_within_pool_ranker_quality']
                ['paired_diff_placed_minus_ideal']['wins'],
                 d['D7_within_pool_ranker_quality']
                ['paired_diff_placed_minus_ideal']['losses'],
                 d['D7_within_pool_ranker_quality']
                ['paired_diff_placed_minus_ideal']['sign_test_p']), flush=True)
        print('  D8 sparsity: %s/%s eligible candidates have a ZERO routed '
              'effect; decisions with exactly one positive candidate: %s/%s'
              % (d['D8_sparsity']['n_routed_zero'],
                 d['D8_sparsity']['n_eligible_total'],
                 d['D8_sparsity']['n_decisions_with_exactly_one_positive'],
                 d['D8_sparsity']['n_decisions']), flush=True)
        print('  D5 routed deltas on the 0.01 ns grid: %s/%s'
              % (d['D5_quantum']['n_routed_multiple_of_0_01'],
                 d['D5_quantum']['n_values']), flush=True)
    p = REPO / 'scratch/round33_mechanism.json'
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', p, flush=True)


if __name__ == '__main__':
    main()
