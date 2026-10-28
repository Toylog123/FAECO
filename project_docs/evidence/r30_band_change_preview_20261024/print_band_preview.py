"""Print the band-change preview in a readable form (UTF-8 file)."""
import json
import pathlib

REPO = pathlib.Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
d = json.loads((REPO / 'scratch/band_change_preview.json').read_text(encoding='utf-8'))
o = []
o.append('rows: training table %d, after join %d, circuits %s'
          % (d['n_rows_in_training_table'], d['n_rows_usable_after_join'],
             d['circuits']))
o.append('band: %s (in force)  ->  %s (full-family preview)'
          % (d['band_in_force_now'], d['band_preview_full_family']))
o.append('control faithfulness: %s (max dev %s, %d checks)'
          % (d['control_faithfulness']['faithful'],
             d['control_faithfulness']['max_absolute_deviation'],
             d['control_faithfulness']['n_checks']))
o.append('')

for lm in ('resolvable', 'gain', 'harm'):
    c = d['classifier'][lm]['control']
    p = d['classifier'][lm]['preview']
    o.append('=== label mode %s ===' % lm)
    o.append('  n_positive %d -> %d   powered %s -> %s'
             % (c['n_positive'], p['n_positive'], c['powered'], p['powered']))
    o.append('  %-24s %-34s %-34s' % ('feature set', 'control AUC [CI]', 'preview AUC [CI]'))
    for fs in sorted(c['cells'].keys()):
        cc, pp = c['cells'][fs], p['cells'].get(fs, {})
        def f(x):
            ci = x.get('ci95')
            cis = '[%.4f, %.4f]' % (ci[0], ci[1]) if ci else '-'
            return '%s %s' % (x.get('pooled_auc'), cis)
        o.append('  %-24s %-34s %-34s' % (fs, f(cc), f(pp)))
    o.append('  gates (control -> preview):')
    for fs in sorted(c['gates'].keys()):
        cg, pg = c['gates'][fs], p['gates'].get(fs, {})
        def gs(g):
            return 'G1%s G2%s G3%s G4%s' % (
                'Y' if g.get('G1_auc_ci_excludes_0.5') else 'n',
                'Y' if g.get('G2_auc_above_kind_only_baseline') else 'n',
                'Y' if g.get('G3_threshold_sweep_ci_excludes_0.5_everywhere') else 'n',
                'Y' if g.get('G4_budget_recall_above_random') else 'n')
        o.append('    %-24s %-18s -> %-18s' % (fs, gs(cg), gs(pg)))
    o.append('')

o.append('=== ablation (label = resolvable) ===')
ac = d['ablation']['routed']['control']
ap = d['ablation']['routed']['preview']
o.append('  n_positive %d -> %d' % (ac['n_positive'], ap['n_positive']))
o.append('  %-24s %-34s %-34s' % ('feature set', 'control AUC [CI]', 'preview AUC [CI]'))
for fs in sorted(ac['cells'].keys()):
    cc, pp = ac['cells'][fs], ap['cells'].get(fs, {})
    def f(x):
        ci = x.get('pooled_auc_ci95')
        cis = '[%.4f, %.4f]' % (ci[0], ci[1]) if ci else '-'
        return '%s %s (n=%s)' % (x.get('pooled_auc'), cis, x.get('n_features'))
    o.append('  %-24s %-34s %-34s' % (fs, f(cc), f(pp)))
o.append('')

o.append('=== acceptance selectivity (routed) ===')
for tag in ('control', 'preview'):
    e = d['acceptance']['routed'][tag]
    o.append('  -- %s (band %.6f, accepted n=%d, rejected n=%d)'
             % (tag, e['band_ns'], e['n_accepted'], e['n_rejected']))
    o.append('     accepted  gain %s (%.4f)  harm %s (%.4f)  inert %s (%.4f)'
             % (e['accepted']['real_gain'], e['accepted']['real_gain_rate'],
                e['accepted']['real_harm'], e['accepted']['real_harm_rate'],
                e['accepted']['inert'], e['accepted']['inert_rate']))
    o.append('     rejected  gain %s (%.4f)  harm %s (%.4f)  inert %s (%.4f)'
             % (e['rejected']['real_gain'], e['rejected']['real_gain_rate'],
                e['rejected']['real_harm'], e['rejected']['real_harm_rate'],
                e['rejected']['inert'], e['rejected']['inert_rate']))
    o.append('     gain enrichment %s   harm ratio %s' % (e['gain_enrichment'], e['harm_ratio']))
    o.append('     perm p  gain cm %s / harm cm %s / gain pm %s / harm pm %s'
             % (e['p_gain_circuit_matched'], e['p_harm_circuit_matched'],
                e['p_gain_pool_matched'], e['p_harm_pool_matched']))
    o.append('     per-circuit  gain %s | harm %s' % (e['per_circuit_gain'],
                                                      e['per_circuit_harm']))
o.append('')
o.append('NOTE: the two passes hold the training table FIXED; the final recomputation')
o.append('      will also have more labelled rows, so the shift shown here is the')
o.append('      threshold effect alone.')

dst = REPO / 'scratch/band_change_preview.txt'
dst.write_text('\n'.join(o), encoding='utf-8')
print('written')
