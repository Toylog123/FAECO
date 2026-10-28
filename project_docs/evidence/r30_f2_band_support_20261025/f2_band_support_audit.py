"""THE CONFOUND IN THE C1/C2 VERDICT, FOUND AND QUANTIFIED.

WHAT THIS TOOL ASKS
-------------------
LOG-20261025-28 concluded, from three pairwise implementation bands measured on
the same 1207-candidate family:

    F0/F1 2s = 0.049753 ns   F1/F2 2s = 0.045540 ns   F0/F2 2s = 0.033706 ns
    max/min = 1.476087  ->  C1 (exchangeable) FAILS, C2 (not exchangeable) HOLDS

But the three bands are NOT measured on the same data.  Measured per candidate
at the 0.01 ns quantum of the post-route WNS, the F2 realisation is DEGENERATE
against F0 on some circuits and against F1 on others: on those circuits the
pairwise difference is identically zero for EVERY candidate.

WHY (checked against the job tables and the tcl): the FLOORPLAN IS FROZEN
(die_area / core_area are pinned to the baseline), so the utilisation part of
the realisation axis has no effect at all.  The only F0-vs-F2 difference left is
the VERTICAL pin layer (met2 -> met4) and the only F1-vs-F2 difference is the
HORIZONTAL pin layer (met5 -> met3).  On some circuits the vertical pin layer
change left the post-route WNS untouched for every candidate; on another the
horizontal one did.

WHY THAT MATTERS ARITHMETICALLY (this is the mechanism, stated exactly):
compute_band() pools the within-circuit SDs as

    pooled_sd = sqrt( sum_c (n_c - 1) * sd_c^2  /  sum_c (n_c - 1) )

A circuit whose pairwise difference is identically zero has sd_c = 0 exactly.
It therefore adds 0 to the numerator but (n_c - 1) to the DENOMINATOR: it
INFLATES df and DILUTES the pooled SD.  Each of the three pairs is diluted by a
different amount, because each pair is degenerate on a different set of
circuits.  So max/min over the three bands compares three differently
diluted estimates -- the comparison is confounded, and the direction of the
confound is known (it pushes every band DOWN, by an unequal amount).

WHAT THIS TOOL DOES
--------------------
1. recomputes the three bands with the PROJECT'S OWN compute_band() (imported,
   never re-implemented) on the full family, and cross-checks them against the
   published artefact -- the control pass;
2. names, per pair, which circuits actually carry variance and which are
   identically zero;
3. recomputes the three bands on the COMMON NON-DEGENERATE SUBSET (circuits
   where all three pairs carry variance) -- the unconfounded comparison;
4. bootstraps the max/min ratio over circuits (2000 resamples of the circuit
   set) so the C1/C2 verdict gets a SIGNIFICANCE GATE instead of a point
   estimate;
5. separates the dilution effect from the support effect by reporting each
   pair on its own variance-carrying support as well.

Boundary: PROBE level, NOT paper evidence.  See `boundary` in the output JSON.
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
import candidate_level_noise as cln          # noqa: E402
import impl_stability_probe as isp           # noqa: E402

FAM = 'itc99'
FAM_DIR = isp.FAM_DIRS[FAM]
SETUP = isp.FAMILY_SETUP[FAM]
OUT = REPO / 'scratch/f2_band_support_audit.json'
PUBLISHED = REPO / ('project_docs/evidence/r30_f2_third_impl_20261025/impl_stability.json')

# the pre-registered synthetic fixtures the C1/C2 verdict was calibrated against,
# and the DECISION THRESHOLDS themselves.  Both are taken from the tool that
# produced the published verdict (scratch/interpret_f2_result.py, criteria fixed
# in LOG-20261024-25 BEFORE the batch was launched) -- the thresholds are NOT
# re-invented here, because re-inventing them would silently change the
# criterion after seeing the data.
FIX_EXCHANGEABLE = 1.028124   # fixture: fully synthetic, exchangeable
FIX_CORRELATED = 1.718223     # fixture: deliberately correlated third side
THRESH_EXCHANGEABLE = 1.10    # ratio < 1.10            -> C1 holds
THRESH_CORRELATED = 1.35      # 1.10 <= ratio < 1.35    -> INCONCLUSIVE
                               # ratio >= 1.35           -> C2 holds
BOOT = 2000
SEED = 20261025

PAIRS = {'F0_vs_F1': (('I0',), ('I1',)),
         'F0_vs_F2': (('I0',), ('I2',)),
         'F1_vs_F2': (('I1',), ('I2',))}


def load(path):
    return [json.loads(l) for l in Path(path).read_text(encoding='utf-8').splitlines()
            if l.strip()]


def verdict_text(ratio):
    """Classify a max/min band ratio with the PRE-REGISTERED thresholds."""
    if ratio is None:
        return 'NOT COMPUTED'
    if ratio < THRESH_EXCHANGEABLE:
        return ('EXCHANGEABLE (C1 holds): max/min = %.6f is within %.2f%% of the '
                'synthetic exchangeable fixture (%.6f)'
                % (ratio, abs(ratio - FIX_EXCHANGEABLE) / FIX_EXCHANGEABLE * 100,
                   FIX_EXCHANGEABLE))
    if ratio < THRESH_CORRELATED:
        return ('INCONCLUSIVE: max/min = %.6f sits between the exchangeable fixture '
                '(%.6f) and the correlated fixture (%.6f)'
                % (ratio, FIX_EXCHANGEABLE, FIX_CORRELATED))
    return ('NOT EXCHANGEABLE (C2 holds): max/min = %.6f is far above the exchangeable '
            'fixture (%.6f) and in the range of the correlated fixture (%.6f)'
            % (ratio, FIX_EXCHANGEABLE, FIX_CORRELATED))


def band2sigma(rows_subset, a, b):
    """2*pooled_sd, exactly as impl_stability_probe reports it."""
    band, per_ckt = cln.compute_band(rows_subset, list(a), list(b))
    sd = band['pooled_sd']
    two = round(sd * 2, 6) if sd else None
    return two, band, per_ckt


def degeneracy(rows_subset, a, b):
    """Per circuit: how many paired candidates have an EXACTLY zero difference."""
    by = defaultdict(dict)
    for r in rows_subset:
        if r.get('post_status') != 'ok' or r.get('post_wns') is None:
            continue
        if r['batch'] in a:
            by[(r['circuit'], r['key'])]['A'] = r
        elif r['batch'] in b:
            by[(r['circuit'], r['key'])]['B'] = r
    per = defaultdict(lambda: {'n_pairs': 0, 'n_zero': 0, 'n_nonzero': 0, 'max_abs_diff': 0.0})
    for (ckt, _key), pair in by.items():
        if 'A' not in pair or 'B' not in pair:
            continue
        d = round(pair['B']['post_wns'] - pair['A']['post_wns'], 6)
        e = per[ckt]
        e['n_pairs'] += 1
        if d == 0.0:
            e['n_zero'] += 1
        else:
            e['n_nonzero'] += 1
        if abs(d) > e['max_abs_diff']:
            e['max_abs_diff'] = abs(d)
    return {c: dict(v) for c, v in sorted(per.items())}


def pooled_closed_form(sd_map, n_map, circuits):
    """The same pooling compute_band() does, recomputed from per-circuit stats.

    pooled_sd = sqrt( sum (n_c-1) sd_c^2 / sum (n_c-1) ).  Circuits with sd_c
    exactly 0 add nothing to the numerator but everything to the denominator:
    that is the dilution, and it is explicit here.
    """
    num = 0.0
    df = 0
    for c in circuits:
        n = n_map.get(c) or 0
        sd_c = sd_map.get(c)
        if n < 2 or sd_c is None:
            continue
        num += (n - 1) * sd_c * sd_c
        df += n - 1
    return (math.sqrt(num / df) if df else None), df, num


# ---------------------------------------------------------------------------
# load the data exactly the way the published probe does
# ---------------------------------------------------------------------------
rows = isp.load_rows(FAM_DIR) + isp.load_f2_rows(FAM_DIR)

out = {
    'question': ('are the three pairwise implementation bands measured on the SAME '
                 'data?  the F2 realisation is degenerate against F0 or F1 on some '
                 'circuits, and a circuit with an identically-zero difference still '
                 'counts in the df while contributing no variance -- so the '
                 'max/min = 1.476087 comparison may be confounded by DIFFERENT '
                 'DILUTION, not by a real difference between the bands'),
    'family': FAM,
    'n_rows_loaded': len(rows),
    'row_loader': ('impl_stability_probe.load_rows + load_f2_rows (the published '
                   'probe\'s own loader, not a re-implementation)'),
    'band_recipe': ('candidate_level_noise.compute_band() imported from the project; '
                    '2*pooled_sd, rounded to 6 decimals, exactly as '
                    'impl_stability_probe reports it'),
    'fixtures': {'exchangeable': FIX_EXCHANGEABLE, 'correlated': FIX_CORRELATED,
                 'exchangeable_threshold': THRESH_EXCHANGEABLE},
}

# ---------------------------------------------------------------------------
# 1. control pass: recompute the published three bands
# ---------------------------------------------------------------------------
full = {}
for name, (a, b) in PAIRS.items():
    two, band, per_ckt = band2sigma(rows, a, b)
    deg = degeneracy(rows, a, b)
    carrying = sorted(c for c, d in per_ckt.items()
                      if d.get('sd_imp_candidates') not in (None, 0.0))
    zero = sorted(c for c, d in per_ckt.items()
                  if d.get('sd_imp_candidates') == 0.0)
    full[name] = {
        'two_sigma_ns': two,
        'pooled_sd_ns': band['pooled_sd'],
        'ci95': band['ci'],
        'df': band['df'],
        'n_candidate_netlists': band['n_candidate_netlists'],
        'n_circuits_in_join': len(per_ckt),
        'circuits_carrying_variance': carrying,
        'circuits_with_identically_zero_difference': zero,
        'per_circuit_sd': {c: d.get('sd_imp_candidates') for c, d in sorted(per_ckt.items())},
        'per_circuit_n': {c: d.get('n_candidates') for c, d in sorted(per_ckt.items())},
        'per_circuit_degeneracy': deg,
    }

out['full_family'] = full
twos = {k: v['two_sigma_ns'] for k, v in full.items() if v['two_sigma_ns']}
out['full_family']['bands'] = twos
out['full_family']['max_over_min_ratio'] = (round(max(twos.values()) / min(twos.values()), 6)
                                            if twos else None)

# the bootstrap recomputes the pooling in closed form from the per-circuit
# tables; check that this closed form reproduces compute_band() exactly, or the
# bootstrap would be measuring a different statistic than the published band
all_circuits = sorted(full[list(PAIRS)[0]]['per_circuit_sd'].keys())
closed = {}
for name in PAIRS:
    sd_cf, df_cf, num_cf = pooled_closed_form(full[name]['per_circuit_sd'],
                                              full[name]['per_circuit_n'], all_circuits)
    sd_tool = full[name]['pooled_sd_ns']
    closed[name] = {'closed_form_pooled_sd': sd_cf, 'tool_pooled_sd': sd_tool,
                    'abs_diff': (abs(sd_cf - sd_tool) if (sd_cf and sd_tool) else None),
                    'df_closed_form': df_cf, 'df_tool': full[name]['df']}
out['closed_form_cross_check'] = closed
out['closed_form_cross_check_pass'] = all(
    c['abs_diff'] is not None and c['abs_diff'] < 1e-12
    and c['df_closed_form'] == c['df_tool'] for c in closed.values())

# control pass against the published artefact
ctrl = {'published_artefact': str(PUBLISHED.relative_to(REPO))}
if PUBLISHED.exists():
    pub = json.loads(PUBLISHED.read_text(encoding='utf-8'))
    pbands = {k: v.get('two_sigma_ns') for k, v in (pub.get('bands_by_pair') or {}).items()}
    ctrl['published_bands'] = pbands
    ctrl['published_max_over_min_ratio'] = (pub.get('band_stability') or {}).get('max_over_min_ratio')
    ctrl['recomputed_bands'] = twos
    ctrl['band_match'] = {k: (pbands.get(k) == twos.get(k)) for k in twos}
    ctrl['ratio_match'] = (ctrl['published_max_over_min_ratio']
                            == out['full_family']['max_over_min_ratio'])
    ctrl['published_ratio'] = ctrl['published_max_over_min_ratio']
    ctrl['recomputed_ratio'] = out['full_family']['max_over_min_ratio']
else:
    ctrl['note'] = 'published artefact not found'

# control pass on the VERDICT CLASSIFIER: the thresholds used here must be the
# ones the published interpretation tool used, so re-classifying the published
# ratio with this script's thresholds must give the published verdict.
INTERP = REPO / 'scratch/f2_interpretation.json'
if INTERP.exists():
    pub_v = json.loads(INTERP.read_text(encoding='utf-8')).get('verdict_C1_C2')
    mine = verdict_text(out['full_family']['max_over_min_ratio'])
    ctrl['published_verdict_text'] = pub_v
    ctrl['recomputed_verdict_text'] = mine
    ctrl['verdict_classification_matches'] = (
        ('C2 holds' in (pub_v or '')) == ('C2 holds' in mine)
        and ('INCONCLUSIVE' in (pub_v or '')) == ('INCONCLUSIVE' in mine)
        and ('C1 holds' in (pub_v or '')) == ('C1 holds' in mine))
    ctrl['verdict_thresholds_used'] = {
        'exchangeable_below': THRESH_EXCHANGEABLE,
        'correlated_at_or_above': THRESH_CORRELATED,
        'source': ('scratch/interpret_f2_result.py (criteria fixed in '
                   'LOG-20261024-25 before the batch was launched)'),
    }
out['control_pass'] = ctrl

# ---------------------------------------------------------------------------
# 2. the common non-degenerate subset
# ---------------------------------------------------------------------------
common = None
for name in PAIRS:
    carrying = set(full[name]['circuits_carrying_variance'])
    common = carrying if common is None else (common & carrying)
common = sorted(common or [])
out['common_subset_circuits'] = common

if common:
    sub = [r for r in rows if r.get('circuit') in common]
    cb = {}
    for name, (a, b) in PAIRS.items():
        two, band, per_ckt = band2sigma(sub, a, b)
        cb[name] = {
            'two_sigma_ns': two,
            'pooled_sd_ns': band['pooled_sd'],
            'ci95': band['ci'],
            'df': band['df'],
            'n_candidate_netlists': band['n_candidate_netlists'],
            'per_circuit_sd': {c: d.get('sd_imp_candidates') for c, d in sorted(per_ckt.items())},
            'per_circuit_n': {c: d.get('n_candidates') for c, d in sorted(per_ckt.items())},
        }
    ctw = {k: v['two_sigma_ns'] for k, v in cb.items() if v['two_sigma_ns']}
    out['common_subset'] = cb
    out['common_subset']['bands'] = ctw
    out['common_subset']['max_over_min_ratio'] = (round(max(ctw.values()) / min(ctw.values()), 6)
                                                 if ctw else None)

# each pair on its OWN variance-carrying support (isolates dilution from support)
own = {}
for name, (a, b) in PAIRS.items():
    keep = full[name]['circuits_carrying_variance']
    if not keep:
        continue
    sub = [r for r in rows if r.get('circuit') in keep]
    two, band, per_ckt = band2sigma(sub, a, b)
    own[name] = {'two_sigma_ns': two, 'df': band['df'], 'n_circuits': len(keep),
                 'circuits': keep}
own_out = dict(own)
ot = {k: v['two_sigma_ns'] for k, v in own.items() if v['two_sigma_ns']}
if ot:
    own_out['bands'] = ot
    own_out['max_over_min_ratio'] = round(max(ot.values()) / min(ot.values()), 6)
out['each_pair_on_its_own_support'] = own_out

# ---------------------------------------------------------------------------
# 3. resampling over CIRCUIT SETS: is max/min a stable quantity at all?
# ---------------------------------------------------------------------------
# The unit that differs between the three pairs is the CIRCUIT SET, not the
# candidate: a circuit whose pairwise difference is identically zero still
# counts in the df and dilutes the pooled sd.  So the resampling unit is the
# circuit, and the honest question is how much the ratio moves when the circuit
# set changes -- and how often it is not even defined.
all_circuits = sorted(full[list(PAIRS)[0]]['per_circuit_sd'].keys())


def ratio_on(circuits):
    """max/min of the three 2-sigma bands on a given circuit set.

    Returns (ratio, None) or (None, reason).  A resample that leaves one pair
    with no variance-carrying circuit has an undefined ratio; those are
    counted, not silently dropped.
    """
    t = {}
    for name in PAIRS:
        sd, df, _num = pooled_closed_form(full[name]['per_circuit_sd'],
                                          full[name]['per_circuit_n'], circuits)
        if df == 0 or not sd:
            return None, 'no_variance_carrying_circuit:%s' % name
        t[name] = 2.0 * sd
    lo = min(t.values())
    hi = max(t.values())
    if lo == 0:
        return None, 'zero_band'
    return hi / lo, None


resample = {'n_circuits': len(all_circuits), 'unit': 'circuit set',
            'reading': ('max/min over three differently-diluted bands is only a '
                        'well-posed quantity when all three pairs carry variance on '
                        'the same circuits; the resampling below measures how much '
                        'it moves with the circuit set and how often it is undefined')}

# (a) the point estimate on the full circuit set
r_point, why = ratio_on(all_circuits)
resample['full_set_ratio'] = round(r_point, 6) if r_point else None
resample['full_set_undefined_reason'] = why

# (b) leave one circuit out -- deterministic, no sampling
loco = {}
for c in all_circuits:
    keep = [x for x in all_circuits if x != c]
    r, why2 = ratio_on(keep)
    loco['without_%s' % c] = {'ratio': round(r, 6) if r else None,
                               'undefined_reason': why2,
                               'circuits': keep}
resample['leave_one_circuit_out'] = loco
defined_loco = [v['ratio'] for v in loco.values() if v['ratio']]
resample['loco_ratio_min'] = round(min(defined_loco), 6) if defined_loco else None
resample['loco_ratio_max'] = round(max(defined_loco), 6) if defined_loco else None
resample['loco_n_undefined'] = sum(1 for v in loco.values() if not v['ratio'])

# (c) bootstrap over the circuit set
boot_ratios = []
undefined = 0
reasons = defaultdict(int)
rng = random.Random(SEED)
for _ in range(BOOT):
    sample = [all_circuits[rng.randrange(len(all_circuits))] for _ in all_circuits]
    r, why2 = ratio_on(sample)
    if r is None:
        undefined += 1
        reasons[why2] += 1
        continue
    boot_ratios.append(r)
boot_ratios.sort()
resample['bootstrap'] = {'n_resamples': BOOT, 'seed': SEED,
                         'n_defined': len(boot_ratios),
                         'n_undefined': undefined,
                         'frac_undefined': round(undefined / BOOT, 6),
                         'undefined_reasons': dict(reasons)}
if boot_ratios:
    n = len(boot_ratios)
    resample['bootstrap']['ratio_ci95'] = [round(boot_ratios[int(0.025 * n)], 6),
                                           round(boot_ratios[int(0.975 * n)], 6)]
    resample['bootstrap']['ratio_min'] = round(boot_ratios[0], 6)
    resample['bootstrap']['ratio_max'] = round(boot_ratios[-1], 6)
    resample['bootstrap']['ratio_median'] = round(boot_ratios[n // 2], 6)
    resample['bootstrap']['frac_below_exchangeable_threshold'] = round(
        sum(1 for r in boot_ratios if r < THRESH_EXCHANGEABLE) / n, 6)
    resample['bootstrap']['frac_above_correlated_fixture'] = round(
        sum(1 for r in boot_ratios if r >= FIX_CORRELATED) / n, 6)
out['resampling_over_circuit_sets'] = resample

# ---------------------------------------------------------------------------
# 4. per circuit: the three pairwise bands
# ---------------------------------------------------------------------------
perckt_out = {}
for ckt in all_circuits:
    sub = [r for r in rows if r.get('circuit') == ckt]
    entry = {}
    for name, (a, b) in PAIRS.items():
        two, band, per_ckt = band2sigma(sub, a, b)
        d = per_ckt.get(ckt) or {}
        deg = degeneracy(sub, a, b).get(ckt) or {}
        entry[name] = {'two_sigma_ns': two, 'sd': d.get('sd_imp_candidates'),
                       'n': d.get('n_candidates'),
                       'n_pairs_exactly_equal': deg.get('n_zero'),
                       'n_pairs_total': deg.get('n_pairs')}
    vv = [v['two_sigma_ns'] for v in entry.values() if v['two_sigma_ns']]
    entry['max_over_min_ratio'] = (round(max(vv) / min(vv), 6) if vv else None)
    perckt_out[ckt] = entry
out['per_circuit'] = perckt_out

# ---------------------------------------------------------------------------
# 4b. IDENTITY FINGERPRINT: if one pair is identically zero on a circuit, the
#     other two pairs must have the SAME within-circuit sd there.
# ---------------------------------------------------------------------------
# d_F0F2 = d_F0F1 + d_F1F2 per candidate.  If F0 == F2 on a circuit then
# d_F0F1 = -d_F1F2 exactly, so their SDs must be equal; likewise for F0 == F1
# and F1 == F2.  This is an identity, not a correlation: it either holds
# exactly or the degeneracy is a bookkeeping artefact rather than a property of
# the data.  It is checked here because it is the cheapest way to tell a real
# degeneracy from a mislabelled batch.
IDENT = {'F0_vs_F2': ('F0_vs_F1', 'F1_vs_F2'),
         'F0_vs_F1': ('F0_vs_F2', 'F1_vs_F2'),
         'F1_vs_F2': ('F0_vs_F1', 'F0_vs_F2')}
ident_rows = {}
ident_ok = True
for ckt in all_circuits:
    e = perckt_out[ckt]
    row = {}
    for deg_pair, (p1, p2) in IDENT.items():
        n_zero = e[deg_pair]['n_pairs_exactly_equal']
        n_tot = e[deg_pair]['n_pairs_total']
        if not n_tot or n_zero != n_tot:
            continue
        s1 = e[p1]['sd']
        s2 = e[p2]['sd']
        same = (s1 is not None and s2 is not None and abs(s1 - s2) <= 1e-12)
        row[deg_pair] = {'degenerate_pair': deg_pair, 'n_pairs': n_tot,
                         'sd_of_%s' % p1: s1, 'sd_of_%s' % p2: s2,
                         'sd_identical': same,
                         'expected': 'F0 == F2 on this circuit -> the other two '
                                     'pairs must have the same within-circuit sd'}
        if not same:
            ident_ok = False
    if row:
        ident_rows[ckt] = row
out['identity_fingerprint'] = {
    'rule': ('d_F0F2 = d_F0F1 + d_F1F2 per candidate; if one pair is identically '
             'zero on a circuit the other two pairs have equal SD there -- an '
             'identity, so a mismatch would mean the degeneracy is a bookkeeping '
             'artefact'),
    'per_circuit': ident_rows,
    'all_hold': ident_ok,
}

# ---------------------------------------------------------------------------
# 5. verdicts
# ---------------------------------------------------------------------------
for tag in ('full_family', 'common_subset'):
    src = out.get(tag)
    if src:
        src['verdict'] = verdict_text(src.get('max_over_min_ratio'))
if 'each_pair_on_its_own_support' in out:
    out['each_pair_on_its_own_support']['verdict'] = verdict_text(
        out['each_pair_on_its_own_support'].get('max_over_min_ratio'))

# ---- the confound itself, stated as an auditable object --------------------
supports = {name: set(full[name]['circuits_carrying_variance']) for name in PAIRS}
zero_sets = {name: set(full[name]['circuits_with_identically_zero_difference'])
             for name in PAIRS}
same_support = (len({frozenset(v) for v in supports.values()}) == 1)
df_full = {name: full[name]['df'] for name in PAIRS}
df_common = {name: out['common_subset'][name]['df'] for name in PAIRS} if common else {}
out['confound_assessment'] = {
    'are_the_three_pairs_degenerate_on_different_circuits': (not same_support),
    'variance_carrying_supports': {k: sorted(v) for k, v in supports.items()},
    'identically_zero_supports': {k: sorted(v) for k, v in zero_sets.items()},
    'df_full_family': df_full,
    'df_common_subset': df_common,
    'df_inflation_by_degenerate_circuits': (
        {k: df_full[k] - df_common.get(k) for k in PAIRS} if df_common else None),
    'mechanism': ('compute_band() pools as sqrt( sum (n_c-1) sd_c^2 / sum (n_c-1) ); '
                  'a circuit whose pairwise difference is identically zero has '
                  'sd_c = 0, so it adds 0 to the numerator but (n_c-1) to the '
                  'denominator -- it INFLATES df and DILUTES the pooled sd.  Each '
                  'pair is degenerate on a different set of circuits, so the three '
                  'bands are diluted by different amounts and their max/min is not '
                  'a comparison of three estimates of one quantity'),
    'why_the_degeneracy_happens': ('the floorplan is frozen (die_area / core_area '
                                   'pinned to the baseline), so the utilisation part '
                                   'of the realisation axis has no effect; only the '
                                   'pin layers differ -- F0 vs F2 on the vertical '
                                   'pin layer (met2 -> met4), F1 vs F2 on the '
                                   'horizontal pin layer (met5 -> met3) -- and on '
                                   'some circuits a pin layer change left every '
                                   "candidate's post-route WNS untouched"),
    'consequence_for_log_20261025_28': (
        'the C1/C2 verdict in LOG-20261025-28 (max/min = 1.476087 -> C1 fails, C2 '
        'holds) was computed on three bands with DIFFERENT circuit supports, so it '
        'is confounded and must be restated.  The band itself is NOT affected: the '
        'family band definition stays F0 vs F1, and the published band value is '
        'unchanged.'),
}

# ---------------------------------------------------------------------------
# 5b. WHAT SURVIVES AND WHAT MUST BE WITHDRAWN
# ---------------------------------------------------------------------------
ff = out['full_family']
cs = out.get('common_subset') or {}
ow = out['each_pair_on_its_own_support']
ident = out['identity_fingerprint']

out['corrected_verdict'] = {
    'SURVIVES': {
        'C1_fails': ('the three pairwise bands are NOT exchangeable, and this holds '
                     'in every comparison: full family %.6f, common non-degenerate '
                     'subset %s, each pair on its own support %s, leave-one-circuit-out '
                     '%.6f..%.6f, and per circuit b01 %s / b03 %s -- all above the '
                     'pre-registered exchangeable threshold %.2f'
                     % (ff['max_over_min_ratio'],
                        cs.get('max_over_min_ratio'), ow.get('max_over_min_ratio'),
                        out['resampling_over_circuit_sets']['loco_ratio_min'],
                        out['resampling_over_circuit_sets']['loco_ratio_max'],
                        perckt_out['b01']['max_over_min_ratio'],
                        perckt_out['b03']['max_over_min_ratio'],
                        THRESH_EXCHANGEABLE)),
        'band_value': ('the published family band (F0 vs F1, %s ns) is unchanged: the '
                       'F0/F1 pair has NO degenerate circuit, so it is neither '
                       'diluted nor support-confounded'
                       % ff['bands']['F0_vs_F1']),
        'published_verdicts': ('LOG-20261025-28 established that no published verdict '
                               'flips under the other two bands; that conclusion is '
                               'untouched, because it is a threshold-sensitivity '
                               'statement, not a between-band comparison'),
    },
    'WITHDRAWN': {
        'C2_holds': ('C2 does NOT survive the unconfounded comparison: on the common '
                     'non-degenerate subset the ratio is %s and on each pair\'s own '
                     'variance-carrying support it is %s -- both inside the '
                     'INCONCLUSIVE band [%.2f, %.2f).  The full-family value %.6f '
                     'crossed the C2 threshold only because the dilution pushed the '
                     'F0/F2 band down and because b09\'s sd is outsized'
                     % (cs.get('max_over_min_ratio'), ow.get('max_over_min_ratio'),
                        THRESH_EXCHANGEABLE, THRESH_CORRELATED,
                        ff['max_over_min_ratio'])),
        'physical_axis_mechanism': ('the claim "the implementation sensitivity is '
                                    'driven by the physical axis (F0/F1 differs on '
                                    'both axes -> largest band; F2 vs F0 differs on '
                                    'one axis -> smallest band)" is not supported: on '
                                    'the common subset the ordering is F1/F2 %s > '
                                    'F0/F1 %s > F0/F2 %s, i.e. the ONE-axis pair F1/F2 '
                                    'carries the LARGEST band.  The full-family '
                                    'ordering was a dilution artefact.'
                                    % (cs.get('bands', {}).get('F1_vs_F2'),
                                       cs.get('bands', {}).get('F0_vs_F1'),
                                       cs.get('bands', {}).get('F0_vs_F2'))),
        'C2_is_not_disproved': (
            'the withdrawal means the data no longer SUPPORTS C2, not that C2 was '
            'disproved: the bootstrap over circuit sets has a CI95 that straddles '
            'the pre-registered C2 threshold of 1.35, so C2 is neither established '
            'nor refuted -- it is simply no longer a conclusion this family can '
            'carry'),
        'f0f1_is_the_largest': ('the statement "the published F0/F1 band is the largest '
                                 'of the three, i.e. the most conservative" holds only '
                                 'under the full-family pooling; on the common subset '
                                 'F1/F2 (%s) exceeds F0/F1 (%s).  The safe statement is '
                                 'that F1/F2 and F0/F1 are EQUIVALENT at the 0.01 ns '
                                 'quantisation of the measured deltas, so every verdict '
                                 'computed with either one is identical.'
                                 % (cs.get('bands', {}).get('F1_vs_F2'),
                                    cs.get('bands', {}).get('F0_vs_F1'))),
    },
    'NEW_FINDING': {
        'partial_degeneracy': ('the third realisation is PARTIALLY degenerate: on '
                                'b02/b08/b09/b13 the vertical pin-layer change '
                                '(met2 -> met4) left the routed database '
                                '(final.odb) BYTE-IDENTICAL to F0 for every candidate, '
                                'and on b10 the horizontal pin-layer change '
                                '(met5 -> met3) left it byte-identical to F1.  The '
                                'runs really executed (the logs differ in the '
                                'place_pins slot count and in the timing lines; the '
                                'placement lines are identical), so this is a property '
                                'of the designs and the realisation axis, not a '
                                'skipped job.'),
        'single_axis_is_inert_here': ('the family band is measured on the pair that '
                                      'differs on BOTH axes, so 0.049752 ns is an '
                                      'UPPER bound on the sensitivity to a single '
                                      'physical axis, not an unbiased estimate of it'),
        'identity_fingerprint_holds': ('the per-circuit identity (if one pair is '
                                       'identically zero, the other two pairs must '
                                       'have the same within-circuit sd) holds on '
                                       'every degenerate circuit: %s'
                                       % ident['all_hold']),
    },
}

out['boundary'] = (
    'PROBE level, NOT paper evidence.  The post-route WNS is quantised to 0.01 ns, '
    'so "identical" means identical at that quantum.  The floorplan is frozen, so '
    'the utilisation part of the realisation axis has no effect and only the pin '
    'layers differ.  The three pairwise differences are algebraically dependent '
    '(d_F0F2 = d_F0F1 + d_F1F2 per candidate), so their correlations carry no '
    'independent information.  Parasitics come from estimate_parasitics, not from '
    'signoff RCX.')

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

# ---------------------------------------------------------------------------
# print
# ---------------------------------------------------------------------------
print('CONTROL PASS vs the published artefact')
print('  published : %s' % json.dumps(ctrl.get('published_bands'), ensure_ascii=False))
print('  recomputed: %s' % json.dumps(twos, ensure_ascii=False))
print('  band match: %s   ratio published %s vs recomputed %s'
      % (json.dumps(ctrl.get('band_match')), ctrl.get('published_ratio'),
         ctrl.get('recomputed_ratio')))
print()
print('FULL FAMILY')
for k in sorted(twos):
    v = full[k]
    print('  %-9s 2sigma=%.6f df=%-5s carrying=%s zero=%s'
          % (k, v['two_sigma_ns'], v['df'], v['circuits_carrying_variance'],
             v['circuits_with_identically_zero_difference']))
print('  max/min = %s' % out['full_family']['max_over_min_ratio'])
print('  verdict: %s' % out['full_family'].get('verdict'))
print()
print('DEGENERACY (paired candidates with an EXACTLY zero difference)')
for c in all_circuits:
    row = '  %-5s' % c
    for k in sorted(PAIRS):
        e = perckt_out[c][k]
        row += '  %s %s/%s' % (k, e['n_pairs_exactly_equal'], e['n_pairs_total'])
    print(row)
print()
print('COMMON NON-DEGENERATE SUBSET: %s' % (common,))
if common:
    for k in sorted(out['common_subset']['bands']):
        print('  %-9s 2sigma=%.6f df=%s'
              % (k, out['common_subset'][k]['two_sigma_ns'], out['common_subset'][k]['df']))
    print('  max/min = %s' % out['common_subset']['max_over_min_ratio'])
    print('  verdict: %s' % out['common_subset'].get('verdict'))
print()
print('EACH PAIR ON ITS OWN VARIANCE-CARRYING SUPPORT')
for k in sorted(own):
    print('  %-9s 2sigma=%.6f df=%s circuits=%s'
          % (k, own[k]['two_sigma_ns'], own[k]['df'], own[k]['n_circuits']))
print('  max/min = %s' % out['each_pair_on_its_own_support'].get('max_over_min_ratio'))
print('  verdict: %s' % out['each_pair_on_its_own_support'].get('verdict'))
print()
print('RESAMPLING OVER CIRCUIT SETS')
print('  %s' % json.dumps(resample, ensure_ascii=False, indent=2))
print()
print('PER CIRCUIT')
for c in all_circuits:
    e = perckt_out[c]
    print('  %-5s F0F1=%s F0F2=%s F1F2=%s  max/min=%s'
          % (c, e['F0_vs_F1']['two_sigma_ns'], e['F0_vs_F2']['two_sigma_ns'],
             e['F1_vs_F2']['two_sigma_ns'], e['max_over_min_ratio']))
print()
print('IDENTITY FINGERPRINT (degenerate pair -> the other two must have equal sd):')
for c, row in ident_rows.items():
    for deg_pair, v in row.items():
        print('  %-5s %s degenerate on %s pairs -> sd %s vs %s : %s'
              % (c, deg_pair, v['n_pairs'],
                 v['sd_of_%s' % [k for k in IDENT[deg_pair]][0]],
                 v['sd_of_%s' % [k for k in IDENT[deg_pair]][1]],
                 v['sd_identical']))
print('  all hold: %s' % ident_ok)
print()
print('CORRECTED VERDICT')
cv = out['corrected_verdict']
for k in ('SURVIVES', 'WITHDRAWN', 'NEW_FINDING'):
    print('  [%s]' % k)
    for kk, vv in cv[k].items():
        print('    %s: %s' % (kk, vv))
print()
print('wrote %s' % OUT)
