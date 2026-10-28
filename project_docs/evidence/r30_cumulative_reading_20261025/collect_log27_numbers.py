"""Collect every number that LOG-20261025-27 will quote, straight from the
artefacts.  Nothing here is typed in by hand.

Sources
  * experiments/20261024_physical_labels_itc99/three_point_curve.json   (after the fix)
  * experiments/20261024_physical_labels/three_point_curve.json         (after the fix)
  * scratch/backup_pre_cumfix/*.json                                    (before the fix)
  * scratch/cumulative_fix_control_pass.json                            (the control pass)
  * scratch/ideal_ref_semantics.json / ledger_baseline_ideal.json       (the adjudication)
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ITCF = REPO / 'experiments/20261024_physical_labels_itc99'
ISCF = REPO / 'experiments/20261024_physical_labels'
BK = REPO / 'scratch/backup_pre_cumfix'


def j(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    out = {}

    itc_new = j(ITCF / 'three_point_curve.json')
    itc_old = j(BK / 'itc99_three_point_curve.json')
    isc_new = j(ISCF / 'three_point_curve.json')
    isc_old = j(BK / 'iscas89_three_point_curve.json')
    out['_files'] = {'itc_new': str(ITCF / 'three_point_curve.json'),
                     'itc_old': str(BK / 'itc99_three_point_curve.json'),
                     'isc_new': str(ISCF / 'three_point_curve.json'),
                     'isc_old': str(BK / 'iscas89_three_point_curve.json')}

    out['itc99_cumulative_after'] = itc_new.get('stages_cumulative')
    out['itc99_cumulative_before'] = itc_old.get('stages_cumulative')
    out['iscas89_cumulative_after'] = isc_new.get('stages_cumulative')
    out['iscas89_cumulative_before'] = isc_old.get('stages_cumulative')
    out['itc99_marginal_after'] = itc_new.get('stages_marginal')
    out['iscas89_marginal_after'] = isc_new.get('stages_marginal')
    out['itc99_marginal_before'] = itc_old.get('stages_marginal')
    out['iscas89_marginal_before'] = isc_old.get('stages_marginal')

    # marginal blocks must be untouched -> compare the two JSON blobs field by field
    for tag, a, b in (('itc99', itc_old.get('stages_marginal'), itc_new.get('stages_marginal')),
                      ('iscas89', isc_old.get('stages_marginal'), isc_new.get('stages_marginal'))):
        out[f'{tag}_marginal_identical'] = (json.dumps(a, sort_keys=True)
                                            == json.dumps(b, sort_keys=True))
    def same(x, y):
        return json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)

    # explicit per-field comparisons: the tuple loop that preceded this block
    # produced a flag that contradicted both the control pass and a direct
    # element-wise comparison, so the comparisons are written out one by one.
    for field in ('coverage', 'verdict_counts', 'bands', 'decisions',
                  'netlist_consistency', 'measure_note'):
        out[f'itc99_{field}_unchanged'] = same(itc_old.get(field), itc_new.get(field))
        out[f'iscas89_{field}_unchanged'] = same(isc_old.get(field), isc_new.get(field))

    out['_probe'] = {
        'itc_old_decisions_n': len(itc_old.get('decisions') or []),
        'itc_new_decisions_n': len(itc_new.get('decisions') or []),
        'isc_old_decisions_n': len(isc_old.get('decisions') or []),
        'isc_new_decisions_n': len(isc_new.get('decisions') or []),
        'isc_old_decisions_circuits': sorted({str(x.get('circuit'))
                                               for x in (isc_old.get('decisions') or [])}),
        'isc_new_decisions_circuits': sorted({str(x.get('circuit'))
                                               for x in (isc_new.get('decisions') or [])}),
    }

    # how much the shipped ideal cumulative column moved
    for tag, fam, old in (('itc99', ITCF, itc_old), ('iscas89', ISCF, isc_old)):
        oldc = {c['key']: c.get('ideal_cumulative') for c in (old.get('candidates') or [])}
        newc = {c['key']: c.get('ideal_cumulative')
                for c in j(fam / 'three_point_curve.json').get('candidates') or []}
        diffs = []
        for k, v in oldc.items():
            if v is None or newc.get(k) is None:
                continue
            diffs.append(abs(float(v) - float(newc[k])))
        out[f'{tag}_ideal_cumulative_moved'] = {
            'n_comparable': len(diffs),
            'n_differing': sum(1 for d in diffs if d > 1e-9),
            'mean_abs_diff_ns': round(sum(diffs) / len(diffs), 6) if diffs else None,
            'max_abs_diff_ns': round(max(diffs), 6) if diffs else None,
        }

    # per-circuit cumulative decomposition, recomputed from the artefact itself
    def per_circuit(fam, cb_ideal):
        rows = {}
        with (fam / 'training_table.csv').open(encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh):
                rows[r['key']] = r
        agg = defaultdict(lambda: {'n': 0, 'ideal': [], 'placed': [], 'routed': []})
        for c in j(fam / 'three_point_curve.json').get('candidates') or []:
            r = rows.get(c['key'])
            if r is None:
                continue
            iw = r.get('ideal_wns')
            cb = cb_ideal.get(c['circuit'])
            if iw in (None, '') or cb is None:
                continue
            a = agg[c['circuit']]
            a['n'] += 1
            a['ideal'].append(round(float(iw) - cb, 6))
            for name, key in (('placed', 'placed_cumulative'), ('routed', 'routed_cumulative')):
                v = c.get(key)
                if v is not None:
                    a[name].append(float(v))
        res = {}
        for ckt, a in sorted(agg.items()):
            res[ckt] = {
                'n': a['n'],
                'mean_ideal_cum': round(sum(a['ideal']) / len(a['ideal']), 6),
                'mean_placed_cum': round(sum(a['placed']) / len(a['placed']), 6) if a['placed'] else None,
                'mean_routed_cum': round(sum(a['routed']) / len(a['routed']), 6) if a['routed'] else None,
                'n_ideal_improved': sum(1 for x in a['ideal'] if x > 0),
                'n_placed_improved': sum(1 for x in a['placed'] if x > 0),
                'n_routed_improved': sum(1 for x in a['routed'] if x > 0),
            }
        return res

    ledger_itc = j(REPO / 'scratch/ledger_baseline_ideal.json')
    cb_itc = ledger_itc['itc99']['_summary'] and {c: v['circuit_baseline_ideal_wns']
                                                   for c, v in ledger_itc['itc99'].items()
                                                   if c != '_summary'}
    cb_isc = {c: v['circuit_baseline_ideal_wns']
              for c, v in ledger_itc['iscas89'].items() if c != '_summary'}
    out['itc99_per_circuit_cumulative'] = per_circuit(ITCF, cb_itc)
    out['iscas89_per_circuit_cumulative'] = per_circuit(ISCF, cb_isc)

    # attenuation of the multi-round effect, ideal -> physical
    def attenuation(fam, cb_ideal):
        rows = {}
        with (fam / 'training_table.csv').open(encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh):
                rows[r['key']] = r
        res = {}
        for name, key in (('placed', 'placed_cumulative'), ('routed', 'routed_cumulative')):
            pairs = []
            for c in j(fam / 'three_point_curve.json').get('candidates') or []:
                r = rows.get(c['key'])
                if r is None:
                    continue
                iw = r.get('ideal_wns')
                cb = cb_ideal.get(c['circuit'])
                v = c.get(key)
                if iw in (None, '') or cb is None or v is None:
                    continue
                pairs.append((round(float(iw) - cb, 6), float(v)))
            ic = sum(a for a, _ in pairs) / len(pairs)
            pc = sum(b for _, b in pairs) / len(pairs)
            res[name] = {
                'n': len(pairs),
                'mean_ideal_cum': round(ic, 6),
                'mean_physical_cum': round(pc, 6),
                'ratio_physical_over_ideal': round(pc / ic, 6) if ic else None,
                'n_ideal_improved': sum(1 for a, _ in pairs if a > 0),
                'n_physical_improved': sum(1 for _, b in pairs if b > 0),
                'n_ideal_improved_physical_not': sum(1 for a, b in pairs if a > 0 and b <= 0),
                'n_ideal_not_physical_improved': sum(1 for a, b in pairs if a <= 0 and b > 0),
            }
        return res

    out['itc99_attenuation_cumulative'] = attenuation(ITCF, cb_itc)
    out['iscas89_attenuation_cumulative'] = attenuation(ISCF, cb_isc)

    # the adjudication artefacts
    out['ledger_baseline_summary'] = {
        'itc99': ledger_itc['itc99']['_summary'],
        'iscas89': ledger_itc['iscas89']['_summary'],
    }
    sem = j(REPO / 'scratch/ideal_ref_semantics.json')
    out['ideal_reference_adjudication'] = {
        'T1_distinct_ideal_reference_per_circuit': {
            c: v.get('n_distinct_ideal_baseline_wns')
            for c, v in sem['T1_ideal_reference_constant_within_circuit'].items()},
        'T2': {k: v for k, v in sem['T2_ideal_reference_tracks_iteration_base'].items()
               if k != 'samples'},
        'T4': sem['T4_ideal_delta_vs_iteration_base_version'],
    }
    rec = j(REPO / 'scratch/recheck_cumulative_columns.json')
    out['physical_side_recheck'] = {
        'routed_cumulative': {k: v for k, v in rec['routed_cumulative_recheck'].items()
                              if k != 'note'},
        'routed_marginal': {k: v for k, v in rec['routed_marginal_recheck'].items()
                            if k != 'note'},
    }
    cp = j(REPO / 'scratch/cumulative_fix_control_pass.json')
    out['control_pass'] = {'n_checks': cp['n_checks'], 'n_pass': cp['n_pass'],
                           'n_fail': cp['n_fail'], 'failed': cp['failed']}

    (REPO / 'scratch/log27_numbers.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({
        'itc99_cum_after': out['itc99_cumulative_after'],
        'iscas89_cum_after': out['iscas89_cumulative_after'],
        'itc99_marginal_identical': out['itc99_marginal_identical'],
        'iscas89_marginal_identical': out['iscas89_marginal_identical'],
        'itc99_moved': out['itc99_ideal_cumulative_moved'],
        'iscas89_moved': out['iscas89_ideal_cumulative_moved'],
        'control_pass': out['control_pass'],
    }, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
