"""Round 34 -- run the downstream analysis chain with the corrected dataset and
report EVERY number that moved.

The corrected patch changes the ITC-99 training table (76 rows gain their
placed-stage label) and the three-point curve (76 more candidates).  Every
downstream artefact that reads them has to be rebuilt, and every number that
changes has to be reported -- a silent change would be exactly the kind of
"band change" the project's rules forbid.

The procedure:
  1. snapshot the current downstream artefacts (the pre-chain state);
  2. run the family's analysis chain;
  3. diff every artefact that exists in both states, field by field;
  4. report which numbers moved and by how much.

Nothing is written outside the families' own directories.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = REPO / '.venv/Scripts/python.exe'
SNAP = REPO / 'scratch/round34_downstream_before'
OUT = REPO / 'scratch/round34_downstream_cascade.txt'

FAMS = {
    'itc99': ('20261024_physical_labels_itc99',
              REPO / 'experiments/20261024_physical_labels_itc99',
              'run_analysis_itc99.sh'),
    'iscas89': ('20261024_physical_labels',
                REPO / 'experiments/20261024_physical_labels',
                'run_analysis.sh'),
}

# the artefacts the chains write (the ones that matter downstream)
WATCH = {
    'itc99': [
        'band_scope.json', 'candidate_level_noise.json',
        'calibration_three_stage.json', 'resolvable_positive.json',
        'acceptance_selectivity.json', 'topology_effect.json',
        'stage_verdict_transfer.json', 'stage_kind_effect.json',
        'stage_quant_floor.json', 'two_impl_choice.json', 'decision_floor.json',
        'failure_signal_diagnostic.json', 'surrogate_cross_stage.json',
        'kind_g_vs_r_probe.json', 'training_table_summary.json',
        'counterfactual_acceptance_summary.json', 'ideal_vs_post.json',
        'implementation_check.json', 'impl_stability.json',
        'cross_impl_check.json', 'resolution_analysis.json',
        'rejected_side.json', 'band_sensitivity.json',
        'violation_census.json', 'structural_features_summary.json',
    ],
    'iscas89': [
        'candidate_level_noise.json', 'calibration_three_stage.json',
        'resolvable_positive.json', 'acceptance_selectivity.json',
        'topology_effect.json', 'stage_verdict_transfer.json',
        'stage_kind_effect.json', 'stage_quant_floor.json',
        'two_impl_choice.json', 'decision_floor.json',
        'failure_signal_diagnostic.json', 'surrogate_cross_stage.json',
        'training_table_summary.json', 'dataset_v1_summary.json',
        'cross_impl_check.json', 'impl_stability.json',
        'resolution_analysis.json', 'rejected_side.json',
        'band_sensitivity.json', 'violation_census.json',
        'archfrozen_compare.json', 'calibration.json',
        'calibration_fixed_effects.json', 'placed_repair_effect.json',
    ],
}

out = []


def w(s):
    out.append(str(s))
    print(s, flush=True)


def flatten(obj, prefix=''):
    """-> {dotted path: scalar} for the leaves of a JSON document."""
    res = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            res.update(flatten(v, prefix + '.' + str(k) if prefix else str(k)))
    elif isinstance(obj, list):
        # a list is compared as a whole (its order and content are the value)
        res[prefix] = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    else:
        res[prefix] = obj
    return res


w('=' * 78)
w('ROUND 34 -- THE DOWNSTREAM CASCADE (what moved, and by how much)')
w('=' * 78)

# ---------------------------------------------------------------- snapshot
if SNAP.exists():
    shutil.rmtree(SNAP)
SNAP.mkdir(parents=True)
for fam, (dirname, famdir, _sh) in FAMS.items():
    for name in WATCH[fam]:
        p = famdir / name
        if p.exists():
            shutil.copyfile(p, SNAP / ('%s__%s' % (dirname, name)))
w('snapshot: %d artefact(s)' % len(list(SNAP.iterdir())))

# ---------------------------------------------------------------- run
for fam, (dirname, famdir, sh) in FAMS.items():
    w('')
    w('=== %s : %s' % (fam, sh))
    # the chain scripts are bash and they `cd /mnt/d/...`, so they have to run
    # inside WSL.  The Windows python drives them through wsl.exe.
    cmd = ['wsl', '-d', 'Ubuntu', '--', 'bash',
           '/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/' +
           famdir.relative_to(REPO).as_posix() + '/' + sh]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    tail = [l for l in (r.stdout or '').splitlines() if l.strip()]
    w('    exit=%d   (%d stdout lines)' % (r.returncode, len(tail)))
    if r.returncode != 0:
        for l in (r.stdout or '').splitlines()[-30:]:
            w('    | %s' % l)
        for l in (r.stderr or '').splitlines()[-30:]:
            w('    ! %s' % l)
        w('    (the chain FAILED -- the diff below is against a partial state)')
    else:
        for l in tail[-14:]:
            w('    | %s' % l)

# ---------------------------------------------------------------- diff
w('')
w('=' * 78)
w('THE CASCADE -- per artefact, per field')
w('=' * 78)

summary = {}
for fam, (dirname, famdir, _sh) in FAMS.items():
    w('')
    w('### %s' % fam)
    fam_summary = {}
    for name in WATCH[fam]:
        sp = SNAP / ('%s__%s' % (dirname, name))
        lp = famdir / name
        if not sp.exists():
            if lp.exists():
                w('  %-42s NEW artefact (not in the snapshot)' % name)
            continue
        if not lp.exists():
            w('  %-42s GONE (it was there before)' % name)
            continue
        try:
            sa = flatten(json.loads(sp.read_text(encoding='utf-8')))
            sb = flatten(json.loads(lp.read_text(encoding='utf-8')))
        except Exception as exc:
            w('  %-42s not comparable: %s' % (name, exc))
            continue
        added = [k for k in sb if k not in sa]
        removed = [k for k in sa if k not in sb]
        changed = [(k, sa[k], sb[k]) for k in sorted(set(sa) & set(sb))
                   if sa[k] != sb[k]]
        if not added and not removed and not changed:
            w('  %-42s UNCHANGED' % name)
            continue
        w('  %-42s changed: %d, added: %d, removed: %d'
          % (name, len(changed), len(added), len(removed)))
        for k, va, vb in changed[:40]:
            w('      %-62s %r -> %r' % (k, va, vb))
        if len(changed) > 40:
            w('      ... and %d more' % (len(changed) - 40))
        for k in added[:15]:
            w('      + %-61s = %r' % (k, sb[k]))
        for k in removed[:15]:
            w('      - %-61s (was %r)' % (k, sa[k]))
        fam_summary[name] = {'changed': len(changed), 'added': len(added),
                             'removed': len(removed),
                             'changed_fields': [c[0] for c in changed[:60]]}
    summary[fam] = fam_summary

w('')
w('=' * 78)
w('SUMMARY -- the artefacts that moved')
w('=' * 78)
for fam, fs in summary.items():
    moved = {k: v for k, v in fs.items()
             if v['changed'] or v['added'] or v['removed']}
    w('  %s: %d of %d artefact(s) moved' % (fam, len(moved), len(fs)))
    for k, v in moved.items():
        w('      %-42s changed=%d added=%d removed=%d'
          % (k, v['changed'], v['added'], v['removed']))

(REPO / 'scratch/round34_downstream_cascade.json').write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
(REPO / 'scratch/round34_downstream_cascade.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('\nwrote scratch/round34_downstream_cascade.txt')
