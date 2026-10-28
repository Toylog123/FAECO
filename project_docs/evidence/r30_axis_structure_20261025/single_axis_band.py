"""SINGLE-AXIS BANDS, AND WHAT THE PUBLISHED VERDICTS LOOK LIKE UNDER THEM.

The published family band (F0 vs F1, 2 sigma = 0.049752 ns) is measured on the
pair that changes BOTH physical axes at once.  LOG-20261025-30 established that
the third realisation is PARTIALLY degenerate -- a single-axis change leaves the
routed database byte-identical on 4 of 7 circuits -- which means the family
band is an UPPER BOUND on the sensitivity to a single physical axis.

This tool separates the axes and measures the single-axis bands, then re-derives
every band-thresholded published quantity under them:

  A  the single-axis bands (vertical / horizontal / both) and their support,
     with leave-one-circuit-out sensitivity;
  B  the band-thresholded label counts (resolvable / gain / harm);
  C  the classifier readouts (kind_only, structural), from the project's own
     tool, no re-implementation;
  D  the acceptance selectivity (real gain / harm / inert, enrichment, harm
     ratio) and which published statements flip.

The axis mapping comes from the job tables:
    F0 = pins met3(hor) / met2(ver), util 10
    F1 = pins met5(hor) / met4(ver), util 30
    F2 = pins met3(hor) / met4(ver), util 30
with die_area and core_area identical in all three (the floorplan is frozen and
the utilisation target is inert), so:
    F0 -> F1 changes BOTH axes;  F0 -> F2 the VERTICAL one;  F1 -> F2 the
    HORIZONTAL one.

Usage:
  python scratch/single_axis_band.py --family itc99
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve()
REPO = _HERE.parents[1]
TOOLS = REPO / 'experiments/20261024_physical_labels/tools'
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / 'scratch'))
import candidate_level_noise as cln      # noqa: E402
import impl_stability_probe as isp       # noqa: E402
import resolvable_positive_classifier as rpc   # noqa: E402
import acceptance_physical_selectivity as aps  # noqa: E402
import band_pair_sensitivity as bps     # noqa: E402

FAMILY = 'itc99'
FAM_DIR = isp.FAM_DIRS[FAMILY]
SETUP = isp.FAMILY_SETUP[FAMILY]

# the axis each pair varies, and the published band definition
PAIRS = {'F0_vs_F1': (('I0',), ('I1',)),
         'F0_vs_F2': (('I0',), ('I2',)),
         'F1_vs_F2': (('I1',), ('I2',))}
AXIS = {'F0_vs_F1': 'both_axes', 'F0_vs_F2': 'vertical_only', 'F1_vs_F2': 'horizontal_only'}


def band_of(rows, a, b):
    band, per_ckt = cln.compute_band(rows, list(a), list(b))
    sd = band['pooled_sd']
    two = round(sd * 2, 6) if sd else None
    carrying = sorted(c for c, d in per_ckt.items()
                      if d.get('sd_imp_candidates') not in (None, 0.0))
    zero = sorted(c for c, d in per_ckt.items() if d.get('sd_imp_candidates') == 0.0)
    return {'two_sigma_ns': two, 'pooled_sd_ns': sd, 'df': band['df'],
            'n_candidate_netlists': band['n_candidate_netlists'],
            'circuits_carrying_variance': carrying,
            'circuits_with_identically_zero_difference': zero,
            'per_circuit_sd': {c: d.get('sd_imp_candidates')
                               for c, d in sorted(per_ckt.items())}}


def loco(rows, a, b, label):
    """Leave-one-circuit-out on the band of one pair."""
    circuits = sorted({r.get('circuit') for r in rows if r.get('circuit')})
    out = {}
    for c in circuits:
        sub = [r for r in rows if r.get('circuit') != c]
        v = band_of(sub, a, b)
        out['without_%s' % c] = v['two_sigma_ns']
    vals = [x for x in out.values() if x]
    return {'label': label, 'per_circuit_removed': out,
            'min_ns': min(vals) if vals else None,
            'max_ns': max(vals) if vals else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default=FAMILY)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    fam = args.family

    rows = isp.load_rows(FAM_DIR) + isp.load_f2_rows(FAM_DIR)

    # ---- A  the bands, per axis -------------------------------------------
    full = {name: band_of(rows, a, b) for name, (a, b) in PAIRS.items()}
    supports = {name: set(v['circuits_carrying_variance']) for name, v in full.items()}
    # the support on which an axis is actually measurable
    vertical_support = sorted(supports['F0_vs_F2'])
    horizontal_support = sorted(supports['F1_vs_F2'])
    common = sorted(supports['F0_vs_F1'] & supports['F0_vs_F2'] & supports['F1_vs_F2'])

    def band_on(circuits, name):
        a, b = PAIRS[name]
        sub = [r for r in rows if r.get('circuit') in circuits]
        v = band_of(sub, a, b)
        v['axis'] = AXIS[name]
        v['circuits'] = circuits
        return v

    variants = {
        'published_two_axis_all_circuits': band_on(sorted(supports['F0_vs_F1']), 'F0_vs_F1'),
        'single_axis_vertical': band_on(vertical_support, 'F0_vs_F2'),
        'single_axis_horizontal': band_on(horizontal_support, 'F1_vs_F2'),
        'two_axis_common_subset': band_on(common, 'F0_vs_F1'),
        'single_axis_vertical_common': band_on(common, 'F0_vs_F2'),
        'single_axis_horizontal_common': band_on(common, 'F1_vs_F2'),
    }
    locos = {}
    for vname, v in variants.items():
        a, b = PAIRS[{'published_two_axis_all_circuits': 'F0_vs_F1',
                      'single_axis_vertical': 'F0_vs_F2',
                      'single_axis_horizontal': 'F1_vs_F2',
                      'two_axis_common_subset': 'F0_vs_F1',
                      'single_axis_vertical_common': 'F0_vs_F2',
                      'single_axis_horizontal_common': 'F1_vs_F2'}[vname]]
        locos[vname] = loco(rows, a, b, vname)

    # ---- the band-thresholded quantities ----------------------------------
    trows, kinds, circuits = bps.load_rows(fam)
    col = rpc.TARGET_COL['routed']
    rows_full = [json.loads(l) for l in
                 (rpc.FAM_DIRS[fam] / 'training_table.jsonl')
                 .read_text(encoding='utf-8').splitlines() if l.strip()]

    cells = {}
    for vname, v in variants.items():
        band = v['two_sigma_ns']
        cell = {'band_ns': band, 'axis': v['axis'], 'circuits': v['circuits'],
                'labels': {}, 'classifier': {}, 'acceptance': {}}
        for lm in ('resolvable', 'gain', 'harm'):
            y = rpc.evaluate('routed', trows, kinds, circuits, band,
                             np.random.default_rng(rpc.SEED), feature_sets=(),
                             label_mode=lm)
            cell['labels'][lm] = {'n_positive': y['n_positive'],
                                  'positive_rate': y['positive_rate'],
                                  'powered': y['powered']}
        for fs in ('kind_only', 'structural'):
            for lm in ('resolvable', 'gain', 'harm'):
                if lm == 'gain':
                    y = np.array([1.0 if rpc.num(r.get(col), -1e18) > band else 0.0
                                  for r in trows])
                elif lm == 'harm':
                    y = np.array([1.0 if rpc.num(r.get(col), 1e18) < -band else 0.0
                                  for r in trows])
                else:
                    y = np.array([1.0 if abs(rpc.num(r.get(col), -1e18)) > band else 0.0
                                  for r in trows])
                preds, _ = rpc.oof_predict(trows, kinds, circuits, y, fs, model='ridge')
                m = bps.pool_metrics(trows, y, preds)
                m['n_positive'] = int(y.sum())
                cell['classifier'].setdefault(fs, {})[lm] = m
        acc = [r for r in rows_full if aps.is_accepted(r) and r.get(col) is not None]
        rej = [r for r in rows_full if not aps.is_accepted(r) and r.get(col) is not None]
        am = aps.mix(acc, col, band)
        rm = aps.mix(rej, col, band)
        cell['acceptance'] = {
            'n_accepted': len(acc), 'n_rejected': len(rej),
            'accepted': {k: am.get(k) for k in ('real_gain_rate', 'real_harm_rate',
                                                'inert_rate')},
            'rejected': {k: rm.get(k) for k in ('real_gain_rate', 'real_harm_rate',
                                                'inert_rate')},
            'gain_enrichment': (round(am['real_gain_rate'] / rm['real_gain_rate'], 4)
                                if rm['real_gain_rate'] else None),
            'harm_ratio': (round(am['real_harm_rate'] / rm['real_harm_rate'], 4)
                           if rm['real_harm_rate'] else None),
        }
        cells[vname] = cell

    # ---- the quantum index: which multiple of 0.01 ns does the band admit? --
    # The post-route WNS is quantised to 0.01 ns, so every routed delta is a
    # multiple of 0.01 ns and the label set is determined by ONE integer: the
    # smallest multiple of 0.01 ns that is strictly above the band.  Two bands
    # with the same index must therefore select exactly the same candidates and
    # produce bit-identical numbers.  That is a falsifiable structural claim,
    # and it is checked here rather than asserted.
    QUANTUM = 0.01

    def quantum_index(band):
        if band is None:
            return None
        return int(math.floor(band / QUANTUM + 1e-9)) + 1

    def index_of(cell):
        return quantum_index(cell['band_ns'])

    # ---- the |routed delta| histogram on the quantum grid --------------------
    hist = defaultdict(int)
    for r in rows_full:
        v = rpc.num(r.get(col), None)
        if v is None:
            continue
        k = int(round(abs(v) / QUANTUM))
        hist['%d' % k] += 1
    histogram = {'quantum_ns': QUANTUM,
                 'counts_by_abs_delta_in_quantum_steps':
                     {k: hist[k] for k in sorted(hist, key=lambda x: int(x))},
                 'cumulative_counts': {}}

    # ---- the structural check: same index => identical numbers --------------
    groups_by_index = defaultdict(list)
    for vname, c in cells.items():
        groups_by_index[index_of(c)].append(vname)
    index_check = {'rule': ('the label set is determined by the smallest multiple '
                            'of 0.01 ns strictly above the band, so two bands with '
                            'the same index must give bit-identical numbers'),
                   'groups': {}, 'violations': [], 'holds': True}
    for idx, names in sorted(groups_by_index.items(), key=lambda kv: (kv[0] is None, kv[0])):
        same = {}
        if len(names) > 1:
            base = cells[names[0]]
            for other in names[1:]:
                c = cells[other]
                eq = {
                    'labels': all(c['labels'][k] == base['labels'][k] for k in base['labels']),
                    'classifier': all(c['classifier'][fs][lm] == base['classifier'][fs][lm]
                                      for fs in base['classifier'] for lm in base['classifier'][fs]),
                    'acceptance': c['acceptance'] == base['acceptance'],
                }
                same['%s_vs_%s' % (other, names[0])] = eq
                if not all(eq.values()):
                    index_check['holds'] = False
                    index_check['violations'].append('%s vs %s: %s' % (other, names[0], eq))
        index_check['groups']['%s' % idx] = names
        if same:
            index_check['groups']['%s' % idx] = {'variants': names, 'comparisons': same}
    for vname, c in cells.items():
        c['quantum_index'] = index_of(c)
        c['admitted_abs_delta_min_ns'] = (index_of(c) * QUANTUM if index_of(c) else None)
    for vname, v in variants.items():
        v['quantum_index'] = quantum_index(v['two_sigma_ns'])
        v['admitted_abs_delta_min_ns'] = (v['quantum_index'] * QUANTUM
                                          if v['quantum_index'] else None)

    # ---- the quantum index of every band this project has used --------------
    # The bands that appear in the published record, so the whole "band" story
    # can be read on one axis: which quantum step does each band admit?
    band_census = [
        ('pilot_subset band (LOG-20261024-20)', 0.087496),
        ('band-change preview (LOG-20261024-23)', 0.050419),
        ('published family band F0/F1 (LOG-20261024-24)', 0.049752),
        ('probe F0/F1 (LOG-20261025-28)', 0.049753),
        ('probe F1/F2 (LOG-20261025-28)', 0.045540),
        ('probe F0/F2 (LOG-20261025-28)', 0.033706),
        ('single-axis vertical', variants['single_axis_vertical']['two_sigma_ns']),
        ('single-axis horizontal', variants['single_axis_horizontal']['two_sigma_ns']),
        ('two-axis, common subset', variants['two_axis_common_subset']['two_sigma_ns']),
        ('single-axis vertical, common subset',
         variants['single_axis_vertical_common']['two_sigma_ns']),
        ('single-axis horizontal, common subset',
         variants['single_axis_horizontal_common']['two_sigma_ns']),
    ]
    census = [{'label': lab, 'band_ns': b, 'quantum_index': quantum_index(b),
               'admits_abs_delta_ge_ns': (quantum_index(b) * QUANTUM if b else None)}
              for lab, b in band_census]

    # ---- the flip table against the published band -------------------------
    ref = cells['published_two_axis_all_circuits']
    flips = []

    def note(kind, name, ref_v, other_v, higher_is_stronger=True):
        if ref_v is None or other_v is None:
            flips.append({'kind': kind, 'name': name, 'reference': ref_v,
                          'other': other_v, 'flips': None})
            return
        f = (other_v > ref_v) if higher_is_stronger else (other_v < ref_v)
        flips.append({'kind': kind, 'name': name, 'reference': ref_v,
                      'other': other_v, 'flips': bool(f)})

    for vname, c in cells.items():
        if vname == 'published_two_axis_all_circuits':
            continue
        note('label_count', 'resolvable_positives',
             ref['labels']['resolvable']['n_positive'],
             c['labels']['resolvable']['n_positive'])
        note('label_count', 'gain_positives',
             ref['labels']['gain']['n_positive'], c['labels']['gain']['n_positive'])
        note('label_count', 'harm_positives',
             ref['labels']['harm']['n_positive'], c['labels']['harm']['n_positive'])
        note('classifier', 'kind_only_pooled_auc(resolvable)',
             ref['classifier']['kind_only']['resolvable']['pooled_auc'],
             c['classifier']['kind_only']['resolvable']['pooled_auc'])
        note('classifier', 'structural_within_pool_auc(resolvable)',
             ref['classifier']['structural']['resolvable']['mean_within_pool_auc'],
             c['classifier']['structural']['resolvable']['mean_within_pool_auc'])
        note('classifier', 'structural_pooled_auc(resolvable)',
             ref['classifier']['structural']['resolvable']['pooled_auc'],
             c['classifier']['structural']['resolvable']['pooled_auc'])
        note('acceptance', 'accepted_real_gain_rate',
             ref['acceptance']['accepted']['real_gain_rate'],
             c['acceptance']['accepted']['real_gain_rate'])
        note('acceptance', 'accepted_inert_rate',
             ref['acceptance']['accepted']['inert_rate'],
             c['acceptance']['accepted']['inert_rate'], higher_is_stronger=False)
        note('acceptance', 'gain_enrichment',
             ref['acceptance']['gain_enrichment'],
             c['acceptance']['gain_enrichment'])
        note('acceptance', 'harm_ratio',
             ref['acceptance']['harm_ratio'],
             c['acceptance']['harm_ratio'], higher_is_stronger=False)

    out = {
        'family': fam,
        'question': ('the published family band is measured on the pair that changes '
                     'BOTH physical axes; what do the band-thresholded published '
                     'verdicts look like under a SINGLE-axis band?'),
        'axis_mapping': ('F0 = pins met3/met2 util 10; F1 = met5/met4 util 30; '
                         'F2 = met3/met4 util 30; die_area and core_area identical in '
                         'all three (frozen floorplan, inert utilisation target)'),
        'bands': variants,
        'full_family_bands_by_pair': full,
        'supports': {'vertical_axis_measurable_on': vertical_support,
                     'horizontal_axis_measurable_on': horizontal_support,
                     'all_three_pairs_measurable_on': common},
        'leave_one_circuit_out': locos,
        'n_training_rows': len(trows),
        'cells': cells,
        'quantum_grid': {
            'quantum_ns': QUANTUM,
            'admitted_index_rule': ('a candidate is labelled resolvable/gain/harm when '
                                    '|routed delta| > band; the routed delta is a '
                                    'multiple of 0.01 ns, so the label set is '
                                    'determined by the integer '
                                    'floor(band/0.01)+1'),
            'structural_check': index_check,
            'band_census': census,
        },
        'routed_delta_histogram': histogram,
        'flip_table_vs_published': flips,
        'note': ('the family band DEFINITION stays F0 vs F1; the single-axis bands '
                 'are DIAGNOSTICS that answer "how sensitive is a post-route WNS to '
                 'one physical axis", and they change no published verdict by '
                 'themselves -- this tool only asks whether the published verdicts '
                 'would SURVIVE them'),
        'boundary': ('PROBE level, NOT paper evidence.  A single-axis band can only '
                     'be measured on the circuits where that axis is active, so the '
                     'single-axis bands and the two-axis band are NOT measured on '
                     'the same circuits; the common-subset rows are the '
                     'like-for-like comparison and they cover only %d circuits.  '
                     'The post-route WNS is quantised to 0.01 ns.  Parasitics come '
                     'from estimate_parasitics, not signoff RCX.' % len(common)),
    }
    dest = Path(args.out) if args.out else REPO / 'scratch/single_axis_band.json'
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

    L = []
    L.append('single-axis bands and the published verdicts under them (family %s)' % fam)
    L.append('')
    L.append('%-34s %-11s %-16s %-24s %s'
             % ('variant', 'axis', 'band 2sigma', 'circuits', 'n/df'))
    for vname, v in variants.items():
        L.append('%-34s %-11s %-16s %-24s %s/%s'
                 % (vname, v['axis'], '%.6f' % v['two_sigma_ns'],
                    '／'.join(v['circuits']), v['n_candidate_netlists'], v['df']))
    L.append('')
    L.append('%-34s %-16s %-16s %-16s %-16s %-16s'
             % ('variant', 'labels r/g/h', 'kind_only pool',
                'struct within-pool', 'acc gain/inert', 'enrich/harm'))
    for vname, c in cells.items():
        lab = '%d/%d/%d' % (c['labels']['resolvable']['n_positive'],
                            c['labels']['gain']['n_positive'],
                            c['labels']['harm']['n_positive'])
        ko = c['classifier']['kind_only']['resolvable']['pooled_auc']
        sw = c['classifier']['structural']['resolvable']['mean_within_pool_auc']
        ac = '%.4f/%.4f' % (c['acceptance']['accepted']['real_gain_rate'],
                            c['acceptance']['accepted']['inert_rate'])
        eh = '%s/%s' % (c['acceptance']['gain_enrichment'],
                        c['acceptance']['harm_ratio'])
        L.append('%-34s %-16s %-16s %-16s %-16s %-16s'
                 % (vname, lab, ('%.4f' % ko) if ko is not None else '-',
                    ('%.4f' % sw) if sw is not None else '-', ac, eh))
    L.append('')
    L.append('THE QUANTUM GRID: the band only matters through the integer it admits')
    L.append('%-34s %-10s %-14s %s' % ('variant', 'band', 'quantum idx', 'admits |d| >='))
    for vname, c in cells.items():
        L.append('%-34s %-10.6f %-14s %s'
                 % (vname, c['band_ns'], c['quantum_index'],
                    c['admitted_abs_delta_min_ns']))
    L.append('')
    L.append('structural check (same index => bit-identical numbers): holds=%s'
             % index_check['holds'])
    for idx, g in index_check['groups'].items():
        if isinstance(g, dict):
            L.append('  index %s: %s' % (idx, '／'.join(g['variants'])))
            for k, v in g['comparisons'].items():
                L.append('      %s -> labels=%s classifier=%s acceptance=%s'
                         % (k, v['labels'], v['classifier'], v['acceptance']))
        else:
            L.append('  index %s: %s' % (idx, '／'.join(g)))
    L.append('')
    L.append('|routed delta| histogram (steps of 0.01 ns):')
    for k, v in histogram['counts_by_abs_delta_in_quantum_steps'].items():
        L.append('  %s x 0.01 ns  : %d candidates' % (k, v))
    L.append('')
    L.append('THE BAND CENSUS: every band this project has used, on the quantum grid')
    L.append('%-44s %-10s %-8s %s' % ('band', 'value', 'idx', 'admits |d| >='))
    for c in census:
        L.append('%-44s %-10.6f %-8s %s'
                 % (c['label'], c['band_ns'], c['quantum_index'],
                    c['admits_abs_delta_ge_ns']))
    L.append('')
    L.append('flip table (vs the published two-axis band):')
    for f in flips:
        L.append('  %-14s %-42s ref=%s other=%s flips=%s'
                 % (f['kind'], f['name'], f['reference'], f['other'], f['flips']))
    (REPO / 'scratch/single_axis_band.txt').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))
    print('\nwrote %s' % dest)


if __name__ == '__main__':
    main()
