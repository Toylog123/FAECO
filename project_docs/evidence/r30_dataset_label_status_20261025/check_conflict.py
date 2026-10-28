"""Round 34 -- the PRECISE form of "nothing changed that was already measured".

The previous diff counted every difference in the measured-stage columns, which
lumps two very different things together:

  * a row whose value was NULL and now carries a value  -> a FILLED cell;
  * a row whose value was NOT null and now differs      -> a CONFLICT, i.e. a
    number that used to be published has changed.

Only the second would be a problem.  This script separates them, for the
three stage columns of the training table and for the stage statistics of the
three-point curve.

Everything is written to a text file.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / 'scratch/round34_baseline'
OUT = REPO / 'scratch/round34_conflict_check.txt'

FAMS = {
    'itc99': ('20261024_physical_labels_itc99',
              REPO / 'experiments/20261024_physical_labels_itc99'),
    'iscas89': ('20261024_physical_labels',
                REPO / 'experiments/20261024_physical_labels'),
}

MEASURED = ['ideal_wns', 'ideal_baseline_wns', 'ideal_delta_wns',
            'ideal_cumulative_wns', 'placed_delta_wns', 'placed_cumulative_wns',
            'routed_delta_wns', 'routed_cumulative_wns',
            'routed_verdict_candlevel_pooled', 'placed_verdict_candlevel_pooled',
            'routed_verdict_noise_family_pooled',
            'above_noise', 'above_noise_candlevel',
            'noise_threshold_ns', 'cand_threshold_ns']

out = []
w = out.append


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines()
            if l.strip()]


w('=' * 78)
w('ROUND 34 -- FILLED vs CONFLICT (the precise form)')
w('=' * 78)

summary = {}
for fam, (dirname, famdir) in FAMS.items():
    w('')
    w('### %s' % fam)
    a = load_jsonl(BASELINE / ('%s__training_table.jsonl' % dirname))
    b = load_jsonl(famdir / 'training_table.jsonl')
    ka = {r['key']: r for r in a}
    kb = {r['key']: r for r in b}
    filled = {}
    conflict = []
    for k in sorted(set(ka) & set(kb)):
        for f in MEASURED:
            va, vb = ka[k].get(f), kb[k].get(f)
            if va == vb:
                continue
            if va is None and vb is not None:
                filled[f] = filled.get(f, 0) + 1
            else:
                conflict.append((k, f, va, vb))
    w('  training table: FILLED cells (null -> a value)  : %s'
      % (filled,))
    w('  training table: CONFLICTS (a value -> another value) : %d'
      % len(conflict))
    for c in conflict[:20]:
        w('     !! %s' % (c,))

    # the same for the physical dataset
    a = load_jsonl(BASELINE / ('%s__physical_dataset.jsonl' % dirname))
    b = load_jsonl(famdir / 'physical_dataset.jsonl')
    ka = {(r['batch'], r['key']): r for r in a}
    kb = {(r['batch'], r['key']): r for r in b}
    dfields = ['ideal_wns', 'ideal_baseline_wns', 'ideal_delta_wns',
               'post_wns', 'post_tns', 'post_delta_wns',
               'post_marginal_delta_wns', 'post_cumulative_delta_wns',
               'noise_threshold', 'cand_threshold', 'above_noise',
               'above_noise_candlevel']
    dfilled = {}
    dconflict = []
    for k in sorted(set(ka) & set(kb)):
        for f in dfields:
            va, vb = ka[k].get(f), kb[k].get(f)
            if va == vb:
                continue
            if va is None and vb is not None:
                dfilled[f] = dfilled.get(f, 0) + 1
            else:
                dconflict.append((k, f, va, vb))
    w('  physical dataset: FILLED cells : %s' % (dfilled,))
    w('  physical dataset: CONFLICTS     : %d' % len(dconflict))
    for c in dconflict[:20]:
        w('     !! %s' % (c,))

    # the three-point curve's stage statistics
    la = json.loads((BASELINE / ('%s__three_point_curve.json' % dirname))
                    .read_text(encoding='utf-8'))
    lb = json.loads((famdir / 'three_point_curve.json').read_text(encoding='utf-8'))
    w('')
    w('  three-point curve, the stage statistics, block by block:')
    for blk in ('stages_marginal', 'stages_cumulative',
                'stages_marginal_common_subset'):
        va, vb = la.get(blk) or {}, lb.get(blk) or {}
        for stage in sorted(set(va) | set(vb)):
            sa, sb = va.get(stage) or {}, vb.get(stage) or {}
            keys = sorted(set(sa) | set(sb))
            diffs = [(k, sa.get(k), sb.get(k)) for k in keys
                     if sa.get(k) != sb.get(k)]
            if diffs:
                w('    %s / %s :' % (blk, stage))
                for d in diffs:
                    w('        %-32s %r -> %r' % d)
            else:
                w('    %s / %-22s UNCHANGED' % (blk, stage))
    # the ideal stage specifically: its numbers must be identical, because
    # an ideal measurement can only come from a measured candidate
    for blk in ('stages_marginal', 'stages_cumulative'):
        sa = (la.get(blk) or {}).get('ideal') or {}
        sb = (lb.get(blk) or {}).get('ideal') or {}
        w('    %s / ideal  n: %s -> %s   (must be equal)' % (blk, sa.get('n'),
                                                             sb.get('n')))
    # the bands
    w('')
    w('  bands identical : %s'
      % (json.dumps(la.get('bands'), sort_keys=True)
         == json.dumps(lb.get('bands'), sort_keys=True)))
    w('  decisions identical : %s'
      % (json.dumps(la.get('decisions'), sort_keys=True)
         == json.dumps(lb.get('decisions'), sort_keys=True)))

    summary[fam] = {
        'table_filled': filled,
        'table_conflicts': len(conflict),
        'dataset_filled': dfilled,
        'dataset_conflicts': len(dconflict),
        'ideal_stage_n_baseline': {
            b: ((la.get(b) or {}).get('ideal') or {}).get('n')
            for b in ('stages_marginal', 'stages_cumulative')},
        'ideal_stage_n_patched': {
            b: ((lb.get(b) or {}).get('ideal') or {}).get('n')
            for b in ('stages_marginal', 'stages_cumulative')},
        'bands_identical': json.dumps(la.get('bands'), sort_keys=True)
        == json.dumps(lb.get('bands'), sort_keys=True),
        'decisions_identical': json.dumps(la.get('decisions'), sort_keys=True)
        == json.dumps(lb.get('decisions'), sort_keys=True),
    }

w('')
w('=' * 78)
w('SUMMARY')
w('=' * 78)
w(json.dumps(summary, indent=2, ensure_ascii=False))
(REPO / 'scratch/round34_conflict_check.json').write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
(REPO / 'scratch/round34_conflict_check.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('wrote scratch/round34_conflict_check.txt')
