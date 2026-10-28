"""THE SHAPE OF THE IMPLEMENTATION EFFECT (OI-052 item 30, the open question).

The open question in OI-052 item 30 was: is the candidate-level implementation
effect ONE degree of freedom (a single per-candidate bias that all realisations
share) or candidate-specific multi-dimensional noise?

There is a third possibility, and this family looks like it:

    the two physical axes have NEGATIVELY CORRELATED effects -- a candidate
    that gains under the vertical pin-layer change tends to LOSE under the
    horizontal one -- so the implementation effect is a TWO-dimensional,
    candidate-specific, anti-correlated structure.

That would explain the C3 failure directly: averaging two realisations can
only cancel an implementation-induced ranking distortion when the two
realisations' distortions are POSITIVELY correlated (common mode).  If they
are negatively correlated, averaging does not cancel anything -- and in the
degenerate cells it actively injects the other axis's error.

Definitions (per candidate x, with wns_R = the post-route WNS under realisation R):

    imp01(x) = wns_F1(x) - wns_F0(x)     (F0 -> F1: BOTH axes change)
    imp12(x) = wns_F2(x) - wns_F1(x)     (F1 -> F2: HORIZONTAL axis only)
    imp02(x) = wns_F2(x) - wns_F0(x)     (F0 -> F2: VERTICAL axis only)

and, per candidate, imp02 = imp01 + imp12 identically.

The axis decomposition follows from the job tables: F0 = pins met3/met2
util 10, F1 = met5/met4 util 30, F2 = met3/met4 util 30, with die_area and
core_area identical in all three (the floorplan is frozen and the utilisation
target is inert -- the run logs echo Util 11.850% in all three).  So F0->F1
changes both axes, F1->F2 changes the horizontal one, F0->F2 the vertical one.

This tool measures the correlation structure, per circuit and pooled, with a
bootstrap over POOLS, and states where the answer sits relative to the two
hypotheses.

Output: scratch/f2_axis_correlation.json
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
OUT = REPO / 'scratch/f2_axis_correlation.json'
BOOT = 5000
SEED = 20261025

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

recs = []
for (ckt, key), v in by.items():
    if len(v) < 3:
        continue
    imp01 = round(v['F1'] - v['F0'], 6)
    imp12 = round(v['F2'] - v['F1'], 6)
    imp02 = round(v['F2'] - v['F0'], 6)
    recs.append({'circuit': ckt, 'key': key, 'pool': '%s iter %s' % meta[(ckt, key)],
                 'imp01': imp01, 'imp12': imp12, 'imp02': imp02,
                 'identical_F0_F2': v['F0'] == v['F2'],
                 'identical_F1_F2': v['F1'] == v['F2'],
                 'identical_F0_F1': v['F0'] == v['F1']})


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    if len(xs) < 3:
        return None
    return pearson(ranks(xs), ranks(ys))


def var(vals):
    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    return sum((v - m) ** 2 for v in vals) / (n - 1)


def describe(subset, tag, boot=False):
    xs = [r['imp01'] for r in subset]
    ys = [r['imp12'] for r in subset]
    out = {'tag': tag, 'n': len(subset),
           'n_pools': len(set(r['pool'] for r in subset)),
           'pearson_r': pearson(xs, ys),
           'spearman_rho': spearman(xs, ys),
           'var_imp01': var(xs), 'var_imp12': var(ys), 'var_imp02': var([r['imp02'] for r in subset]),
           'sd_imp01': math.sqrt(var(xs)) if var(xs) else None,
           'sd_imp12': math.sqrt(var(ys)) if var(ys) else None,
           'sd_imp02': math.sqrt(var([r['imp02'] for r in subset])) if var([r['imp02'] for r in subset]) else None}
    # the variance decomposition: if the two axes were independent, var(imp02)
    # would be var(imp01) + var(imp12); the ratio says how much they cancel.
    if out['var_imp01'] and out['var_imp12'] and out['var_imp02']:
        indep = out['var_imp01'] + out['var_imp12']
        out['var_independent_prediction'] = indep
        out['var_ratio_observed_over_independent'] = round(out['var_imp02'] / indep, 6)
        out['covariance'] = round(out['var_imp02'] - indep, 9)
    # the two hypotheses, as correlations
    out['hypothesis_one_degree_of_freedom'] = {'predicted_r': 1.0,
                                               'meaning': 'all realisations share one per-candidate bias'}
    out['hypothesis_independent_candidate_specific'] = {'predicted_r': 0.0,
                                                        'meaning': 'each realisation perturbs each candidate independently'}
    if boot and len(subset) > 3:
        groups = defaultdict(list)
        for r in subset:
            groups[r['pool']].append(r)
        keys = sorted(groups)
        rs = []
        rng = random.Random(SEED)
        for _ in range(BOOT):
            samp = []
            for _k in keys:
                samp.extend(groups[keys[rng.randrange(len(keys))]])
            if len(samp) > 2:
                r_ = pearson([s['imp01'] for s in samp], [s['imp12'] for s in samp])
                if r_ is not None:
                    rs.append(r_)
        rs.sort()
        m = len(rs)
        out['bootstrap_pearson_r'] = {
            'n_resamples': BOOT, 'seed': SEED, 'n_effective': m,
            'ci95': [round(rs[int(0.025 * m)], 6), round(rs[int(0.975 * m)], 6)],
            'median': round(rs[m // 2], 6),
            'frac_negative': round(sum(1 for x in rs if x < 0) / m, 6),
            'frac_below_minus_0_5': round(sum(1 for x in rs if x < -0.5) / m, 6),
            'frac_above_0': round(sum(1 for x in rs if x > 0) / m, 6),
            'unit': 'the POOL is resampled (the unit of independence)'}
    return out


# --- the degeneracy structure per circuit ------------------------------------
circuits = sorted({r['circuit'] for r in recs})
deg = {}
for ckt in circuits:
    sub = [r for r in recs if r['circuit'] == ckt]
    deg[ckt] = {
        'F0_vs_F2_identical_for_all': all(r['identical_F0_F2'] for r in sub),
        'F1_vs_F2_identical_for_all': all(r['identical_F1_F2'] for r in sub),
        'F0_vs_F1_identical_for_all': all(r['identical_F0_F1'] for r in sub),
        'n_candidates': len(sub),
        'n_F0_eq_F2': sum(1 for r in sub if r['identical_F0_F2']),
        'n_F1_eq_F2': sum(1 for r in sub if r['identical_F1_F2']),
    }
non_deg = sorted(c for c in circuits
                 if not (deg[c]['F0_vs_F2_identical_for_all']
                         or deg[c]['F1_vs_F2_identical_for_all']))

# --- the identity check ------------------------------------------------------
id_err = max(abs(r['imp02'] - (r['imp01'] + r['imp12'])) for r in recs) if recs else None

groups = {}
groups['full_family'] = describe(recs, 'all 7 circuits (the family as published)', boot=True)
groups['non_degenerate'] = describe([r for r in recs if r['circuit'] in non_deg],
                                    'circuits where all three realisations differ: %s'
                                    % '／'.join(non_deg), boot=True)
groups['degenerate'] = describe([r for r in recs if r['circuit'] not in non_deg],
                                'circuits with at least one degenerate pair', boot=True)
for ckt in circuits:
    groups['circuit_%s' % ckt] = describe([r for r in recs if r['circuit'] == ckt], ckt)

out = {
    'question': ('is the candidate-level implementation effect ONE degree of freedom '
                 '(rho = +1), candidate-specific independent noise (rho = 0), or a '
                 'negatively correlated two-dimensional structure (rho < 0)?'),
    'definitions': {
        'imp01': 'wns_F1 - wns_F0   (F0 -> F1: both physical axes change)',
        'imp12': 'wns_F2 - wns_F1   (F1 -> F2: HORIZONTAL pin layer only)',
        'imp02': 'wns_F2 - wns_F0   (F0 -> F2: VERTICAL pin layer only)',
        'identity': 'imp02 = imp01 + imp12 per candidate',
        'axis_mapping': ('F0 = pins met3(hor)/met2(ver) util 10; F1 = met5/met4 util 30; '
                         'F2 = met3/met4 util 30; die_area and core_area identical in '
                         'all three (the floorplan is frozen and the utilisation target '
                         'is inert -- the run logs echo Util 11.850% in all three)'),
    },
    'identity_max_abs_error': id_err,
    'degeneracy_per_circuit': deg,
    'non_degenerate_circuits': non_deg,
    'groups': groups,
    'boundary': ('PROBE level, NOT paper evidence.  The candidate-level correlation '
                 'is a descriptive statistic, not an independent test of the two '
                 'hypotheses: on the DEGENERATE circuits the correlation is forced '
                 'to -1 by the degeneracy itself (imp02 == 0 forces imp01 = -imp12), '
                 'so only the non-degenerate subset carries information.  The '
                 'non-degenerate subset has 2 circuits.  The post-route WNS is '
                 'quantised to 0.01 ns.  Parasitics come from estimate_parasitics, '
                 'not signoff RCX.'),
}
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

print('identity imp02 = imp01 + imp12, max abs error: %s' % id_err)
print()
print('DEGENERACY PER CIRCUIT')
for c in circuits:
    d = deg[c]
    print('  %-5s n=%-4d F0==F2 all: %-5s (%d)   F1==F2 all: %-5s (%d)'
          % (c, d['n_candidates'], d['F0_vs_F2_identical_for_all'], d['n_F0_eq_F2'],
             d['F1_vs_F2_identical_for_all'], d['n_F1_eq_F2']))
print('  non-degenerate circuits: %s' % '／'.join(non_deg))
print()
print('CORRELATION STRUCTURE (imp01 vs imp12)')
for tag in ('full_family', 'non_degenerate', 'degenerate'):
    g = groups[tag]
    boot = g.get('bootstrap_pearson_r') or {}
    print('  %-16s n=%-4d  pearson r=%-9s spearman=%-9s  var(imp02)/[var01+var12]=%s'
          % (tag, g['n'], ('%.6f' % g['pearson_r']) if g['pearson_r'] is not None else '-',
             ('%.6f' % g['spearman_rho']) if g['spearman_rho'] is not None else '-',
             g.get('var_ratio_observed_over_independent')))
    if boot:
        print('  %-16s   bootstrap r CI95 %s  frac negative %s  frac < -0.5 %s'
              % ('', boot.get('ci95'), boot.get('frac_negative'),
                 boot.get('frac_below_minus_0_5')))
print()
print('PER CIRCUIT')
for c in circuits:
    g = groups['circuit_%s' % c]
    print('  %-5s n=%-4d r=%-9s rho=%-9s  var ratio %s   %s'
          % (c, g['n'], ('%.6f' % g['pearson_r']) if g['pearson_r'] is not None else '-',
             ('%.6f' % g['spearman_rho']) if g['spearman_rho'] is not None else '-',
             g.get('var_ratio_observed_over_independent'),
             'DEGENERATE' if c not in non_deg else ''))
print()
print('wrote %s' % OUT)
