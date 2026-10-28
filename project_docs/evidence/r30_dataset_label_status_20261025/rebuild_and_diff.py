"""Round 34 -- rebuild the PRE-PATCH baseline and then the PATCHED artefacts,
and diff them.

The first version of the round-34 patch was rolled back (it fabricated an
ideal-stage measurement out of a placeholder).  The corrected patch is now in
place.  To compare, the chain is rebuilt TWICE:

  step 1  with the ORIGINAL tools (from scratch/backup_pre_r34_dataset) ->
          the pre-patch artefacts, saved to scratch/round34_baseline/
  step 2  with the PATCHED tools (the live ones) -> the patched artefacts

The originals are used through a temporary swap: the original tool file is
copied over the live one, the chain runs, the patched tool is restored from
its own copy, and the chain runs again.  Both are verified byte-wise at the
end (the live tool must be the patched one).

The diff then answers the question the round needs: what EXACTLY changed.
"""
import filecmp
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = REPO / '.venv/Scripts/python.exe'
BACKUP = REPO / 'scratch/backup_pre_r34_dataset'
BASELINE = REPO / 'scratch/round34_baseline'
OUT = REPO / 'scratch/round34_rebuild_diff.txt'

FAMS = {
    'itc99': ('20261024_physical_labels_itc99',
              REPO / 'experiments/20261024_physical_labels_itc99'),
    'iscas89': ('20261024_physical_labels',
                REPO / 'experiments/20261024_physical_labels'),
}
TOOLS = {
    'itc99': ('build_dataset_itc99.py', 'three_point_curve_itc99.py'),
    'iscas89': ('build_dataset.py', 'three_point_curve.py'),
}
ARTEFACTS = ('physical_dataset.jsonl', 'three_point_curve.json',
             'training_table.jsonl', 'training_table_summary.json',
             'dataset_summary.json', 'dataset_v1_summary.json')

report = []


def w(s):
    report.append(str(s))
    print(s, flush=True)


def run(cmd, label):
    r = subprocess.run([str(PY)] + [str(c) for c in cmd], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        w('    %s FAILED exit=%d' % (label, r.returncode))
        for l in (r.stderr or '').splitlines()[-25:]:
            w('    ! %s' % l)
        raise SystemExit('%s failed' % label)
    w('    %s ok' % label)


def chain(fam, dirname, famdir):
    tools = TOOLS[fam]
    run([famdir / 'tools' / tools[0]], '%s: build_dataset' % fam)
    run([famdir / 'tools' / tools[1]], '%s: three_point_curve' % fam)
    run([REPO / 'experiments/20261024_physical_labels/tools'
         / 'build_training_table.py', '--family', fam],
        '%s: build_training_table' % fam)


w('=' * 78)
w('ROUND 34 -- BASELINE (original tools) vs PATCHED (corrected tools)')
w('=' * 78)

# ---- keep a pristine copy of the patched tools
PATCHED = REPO / 'scratch/round34_patched_tools'
if PATCHED.exists():
    shutil.rmtree(PATCHED)
PATCHED.mkdir(parents=True)
for fam, (dirname, famdir) in FAMS.items():
    for t in TOOLS[fam]:
        shutil.copyfile(famdir / 'tools' / t, PATCHED / (dirname + '__' + t))

# ---- step 1: the baseline
w('')
w('STEP 1 -- rebuild with the ORIGINAL tools')
if BASELINE.exists():
    shutil.rmtree(BASELINE)
BASELINE.mkdir(parents=True)
for fam, (dirname, famdir) in FAMS.items():
    for t in TOOLS[fam]:
        shutil.copyfile(BACKUP / ('experiments__%s__tools__%s' % (dirname, t)),
                        famdir / 'tools' / t)
for fam, (dirname, famdir) in FAMS.items():
    chain(fam, dirname, famdir)
    for a in ARTEFACTS:
        p = famdir / a
        if p.exists():
            shutil.copyfile(p, BASELINE / ('%s__%s' % (dirname, a)))

# ---- step 2: the patched artefacts
w('')
w('STEP 2 -- rebuild with the PATCHED tools')
for fam, (dirname, famdir) in FAMS.items():
    for t in TOOLS[fam]:
        shutil.copyfile(PATCHED / (dirname + '__' + t), famdir / 'tools' / t)
for fam, (dirname, famdir) in FAMS.items():
    chain(fam, dirname, famdir)

# ---- verify the live tools are the patched ones
w('')
w('VERIFY -- the live tools are the patched ones:')
for fam, (dirname, famdir) in FAMS.items():
    for t in TOOLS[fam]:
        same = filecmp.cmp(PATCHED / (dirname + '__' + t),
                           famdir / 'tools' / t, shallow=False)
        w('   %-34s patched copy == live tool : %s' % (t, same))
        if not same:
            raise SystemExit('the live tool is not the patched one')

# ---- the diff
w('')
w('=' * 78)
w('DIFF -- baseline vs patched')
w('=' * 78)


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines()
            if l.strip()]


summary = {}
for fam, (dirname, famdir) in FAMS.items():
    w('')
    w('### %s' % fam)
    w('')

    # ---- A) the dataset
    a = load_jsonl(BASELINE / ('%s__physical_dataset.jsonl' % dirname))
    b = load_jsonl(famdir / 'physical_dataset.jsonl')
    ka = {r['key']: r for r in a}
    kb = {r['key']: r for r in b}
    changed_fields = {}
    new_fields = set()
    value_conflicts = []
    for k in sorted(set(ka) & set(kb)):
        for f in set(ka[k]) | set(kb[k]):
            if ka[k].get(f) != kb[k].get(f):
                changed_fields[f] = changed_fields.get(f, 0) + 1
                if f in ('ideal_wns', 'ideal_baseline_wns', 'ideal_delta_wns'):
                    value_conflicts.append((k, f, ka[k].get(f), kb[k].get(f)))
            if f not in ka[k]:
                new_fields.add(f)
    w('  A) physical_dataset.jsonl   baseline %d rows / patched %d rows'
      % (len(a), len(b)))
    w('     keys only in baseline / only in patched : %d / %d'
      % (len(set(ka) - set(kb)), len(set(kb) - set(ka))))
    w('     changed fields: %s' % (changed_fields,))
    w('     newly present fields: %s' % (sorted(new_fields),))
    w('     IDEAL-VALUE conflicts (must be 0) : %d' % len(value_conflicts))
    for c in value_conflicts[:10]:
        w('        %s' % (c,))
    # the status distribution
    st = {}
    for r in b:
        st[r.get('ideal_label_status')] = st.get(r.get('ideal_label_status'), 0) + 1
    w('     ideal_label_status distribution (patched): %s' % (st,))
    # the placeholder check: for the not-measured rows, does the placeholder
    # equal the row's own base?
    n_ph_eq = n_ph_ne = 0
    for r in b:
        if r.get('ideal_label_status') == 'not_measured_pre_sta':
            ph = r.get('ideal_wns_placeholder')
            if ph is None:
                continue
            if ph == r.get('ideal_baseline_wns'):
                n_ph_eq += 1
            else:
                n_ph_ne += 1
    w('     not-measured rows whose placeholder == its own iteration base: %d'
      % n_ph_eq)
    w('     not-measured rows whose placeholder differs            : %d'
      % n_ph_ne)
    summary[fam] = {
        'dataset_rows_baseline': len(a), 'dataset_rows_patched': len(b),
        'dataset_changed_fields': changed_fields,
        'ideal_value_conflicts': len(value_conflicts),
    }

    # ---- B) the curve
    la = json.loads((BASELINE / ('%s__three_point_curve.json' % dirname))
                    .read_text(encoding='utf-8'))
    lb = json.loads((famdir / 'three_point_curve.json').read_text(encoding='utf-8'))
    ca = {c['key']: c for c in (la.get('candidates') or [])}
    cb = {c['key']: c for c in (lb.get('candidates') or [])}
    w('  B) three_point_curve.json  candidates baseline %d / patched %d'
      % (len(ca), len(cb)))
    w('     only in baseline / only in patched : %d / %d'
      % (len(set(ca) - set(cb)), len(set(cb) - set(ca))))
    # which fields changed on the SHARED candidates
    shared_changed = {}
    for k in sorted(set(ca) & set(cb)):
        for f in set(ca[k]) | set(cb[k]):
            if ca[k].get(f) != cb[k].get(f):
                shared_changed[f] = shared_changed.get(f, 0) + 1
    w('     shared candidates with a changed field: %s' % (shared_changed,))
    for tag in ('stages_marginal', 'stages_cumulative',
                'stages_marginal_common_subset', 'common_subset_n', 'bands',
                'coverage', 'verdict_counts', 'decisions'):
        va, vb = la.get(tag), lb.get(tag)
        if va != vb:
            w('     %s CHANGED' % tag)
            if isinstance(va, dict) and isinstance(vb, dict):
                for k in sorted(set(va) | set(vb)):
                    if va.get(k) != vb.get(k):
                        w('        %s: %s' % (k, json.dumps(
                            {'baseline': va.get(k), 'patched': vb.get(k)},
                            ensure_ascii=False)))
            elif tag in ('common_subset_n',):
                w('        baseline=%s patched=%s' % (va, vb))
            else:
                w('        baseline=%s' % (json.dumps(va, ensure_ascii=False)[:400],))
                w('        patched =%s' % (json.dumps(vb, ensure_ascii=False)[:400],))
    summary[fam].update({
        'curve_cands_baseline': len(ca), 'curve_cands_patched': len(cb),
        'curve_new': len(set(cb) - set(ca)),
        'curve_shared_changed_fields': shared_changed,
    })

    # ---- C) the drop census
    cen = famdir / 'three_point_curve_drop_census.json'
    if cen.exists():
        w('  C) drop census (NEW): %s'
          % json.dumps(json.loads(cen.read_text(encoding='utf-8')),
                       ensure_ascii=False))

    # ---- D) the training table
    a = load_jsonl(BASELINE / ('%s__training_table.jsonl' % dirname))
    b = load_jsonl(famdir / 'training_table.jsonl')
    ka = {r['key']: r for r in a}
    kb = {r['key']: r for r in b}
    tf = {}
    nval = 0
    for k in sorted(set(ka) & set(kb)):
        for f in set(ka[k]) | set(kb[k]):
            if ka[k].get(f) != kb[k].get(f):
                tf[f] = tf.get(f, 0) + 1
                if f in ('ideal_wns', 'ideal_baseline_wns', 'ideal_delta_wns',
                        'placed_delta_wns', 'placed_cumulative_wns',
                        'routed_delta_wns', 'routed_cumulative_wns'):
                    nval += 1
    w('  D) training_table.jsonl   baseline %d rows / patched %d rows'
      % (len(a), len(b)))
    w('     keys only in baseline / only in patched : %d / %d'
      % (len(set(ka) - set(kb)), len(set(kb) - set(ka))))
    w('     changed fields: %s' % (tf,))
    w('     VALUE changes on the measured stages (must be 0) : %d' % nval)
    summary[fam].update({
        'table_rows_baseline': len(a), 'table_rows_patched': len(b),
        'table_changed_fields': tf, 'table_measured_value_changes': nval,
    })

    # ---- E) the summaries
    for name in ('training_table_summary.json', 'dataset_summary.json',
                 'dataset_v1_summary.json'):
        bp = BASELINE / ('%s__%s' % (dirname, name))
        lp = famdir / name
        if not (bp.exists() and lp.exists()):
            continue
        sa = json.loads(bp.read_text(encoding='utf-8'))
        sb = json.loads(lp.read_text(encoding='utf-8'))
        diffs = [k for k in sorted(set(sa) | set(sb))
                 if sa.get(k) != sb.get(k)]
        w('  E) %s : differing top-level keys = %s' % (name, diffs))
        for k in diffs:
            va, vb = sa.get(k), sb.get(k)
            if isinstance(va, (int, float, str, type(None))) and \
                    isinstance(vb, (int, float, str, type(None))):
                w('        %s: %r -> %r' % (k, va, vb))
            else:
                w('        %s: (structure differs)' % k)

w('')
w('=' * 78)
w('SUMMARY')
w('=' * 78)
w(json.dumps(summary, indent=2, ensure_ascii=False))

(REPO / 'scratch/round34_rebuild_diff.json').write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
OUT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print('\nwrote scratch/round34_rebuild_diff.txt')
