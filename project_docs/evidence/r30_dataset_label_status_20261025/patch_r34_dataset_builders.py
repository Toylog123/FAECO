"""Round 34 (CORRECTED): the ideal-stage label of a candidate that was never
evaluated on the ideal netlist must stay EMPTY -- and the fact that it was
never evaluated must be RECORDED, not silently turned into a zero.

WHAT THE FIRST VERSION OF THIS PATCH GOT WRONG
-----------------------------------------------
The first version fell back to `trial['wns']` when a trial carried no
`acceptance_evidence`.  That fallback was verified to be EXACTLY equal to
`acceptance_evidence.setup_wns` on every trial that carries BOTH
(3734/3734 ITC-99, 332/332 ISCAS89, 0 differ) -- a true statement, but about
the WRONG population.  The trials that need the fallback carry NEITHER field,
and for them the truth is different:

  * their `wns` is EXACTLY equal to the iteration base's WNS
    (310/310 ITC-99, 25/25 ISCAS89) -- i.e. it is the base's value, not a
    measurement of the candidate;
  * they carry NO `sta_provenance`, NO STA report path, no `slack_status`
    and no `min_slack` (the control set: 3734/3734 carry all four);
  * their failure events are PRE-STA hard gates (F1 equivalence failure,
    F2 boundary invalid);
  * NONE of them is the accepted candidate of its iteration when matched by
    candidate HASH (0/310).

So `trial['wns']` for those trials is a PLACEHOLDER.  Filling the ideal label
from it asserts "this candidate is exactly neutral on the ideal netlist",
which the ledger never measured -- and it would also have entered the
training table as a real measurement, next to a genuinely non-zero physical
effect (72 of the 76 have a non-zero routed delta).

THE CORRECT FIX
---------------
Three changes, each of which makes a state VISIBLE that used to be hidden:

  1. the dataset builder keeps the ideal label EMPTY for those candidates and
     adds two columns that say what is actually known:
       * `ideal_label_status`:
             'measured'              -- an acceptance decision exists, the
                                         ideal WNS is a measurement
             'not_measured_pre_sta'  -- the candidate never reached the ideal
                                         netlist STA (pre-STA hard gate), so
                                         there is NO ideal-stage measurement
       * `ideal_wns_placeholder`: the ledger's `wns` for those trials, kept
         for traceability but explicitly flagged as the base's value.
  2. the three-point curve keeps those candidates (their placed and routed
     stages ARE real measurements) instead of dropping them, and computes
     every stage statistic on the subset that carries that stage -- which the
     curve already did for the cumulative reading.  The stage counts are
     reported per stage, so a stage's n is now explicit.
  3. the drop census is written next to the curve, counting every reason a
     candidate is dropped, so a silent drop can never hide again.

The ideal-stage NUMBERS do not change: a candidate that was never measured on
the ideal netlist contributes nothing to any ideal-stage statistic, before or
after the patch.  What changes is that its PHYSICAL stages (placed, routed)
stop being thrown away, and that the gap becomes visible.

The files live under `experiments/2026*/`, which is git-ignored, so they are
NOT recoverable from git: the patch takes a backup first.
"""
import io
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BACKUP = REPO / 'scratch/backup_pre_r34_dataset'
BACKUP.mkdir(parents=True, exist_ok=True)

BUILDERS = [
    REPO / 'experiments/20261024_physical_labels/tools/build_dataset.py',
    REPO / 'experiments/20261024_physical_labels_itc99/tools/'
    'build_dataset_itc99.py',
]
CURVES = [
    REPO / 'experiments/20261024_physical_labels/tools/three_point_curve.py',
    REPO / 'experiments/20261024_physical_labels_itc99/tools/'
    'three_point_curve_itc99.py',
]
ARTEFACTS = []
for fam in ('20261024_physical_labels', '20261024_physical_labels_itc99'):
    d = REPO / 'experiments' / fam
    for name in ('physical_dataset.jsonl', 'three_point_curve.json',
                 'training_table.jsonl', 'dataset_summary.json',
                 'dataset_v1_summary.json', 'training_table_summary.json'):
        p = d / name
        if p.exists():
            ARTEFACTS.append(p)

# ---------------------------------------------------------------- backup
for p in BUILDERS + CURVES + ARTEFACTS:
    dst = BACKUP / (p.relative_to(REPO).as_posix().replace('/', '__'))
    shutil.copyfile(p, dst)
print('backed up %d file(s) -> %s' % (len(BUILDERS) + len(CURVES)
                                      + len(ARTEFACTS),
                                      BACKUP.relative_to(REPO)))

# ================================================================ builders
# 1. the label block: keep the value empty, record WHAT IS KNOWN
OLD_LABEL = """        ideal_cand = ev.get('setup_wns')
        ideal_base = refs.get('setup_wns')
        ideal_delta = (None if ideal_cand is None or ideal_base is None
                       else round(float(ideal_cand) - float(ideal_base), 6))
"""
NEW_LABEL = """        ideal_cand = ev.get('setup_wns')
        ideal_base = refs.get('setup_wns')
        ideal_delta = (None if ideal_cand is None or ideal_base is None
                       else round(float(ideal_cand) - float(ideal_base), 6))
        # IDEAL_LABEL_STATUS (round 34): a trial that never produced an
        # acceptance decision carries NO acceptance_evidence, and its `wns` is
        # the ITERATION BASE's value, not a measurement of the candidate:
        # it is exactly equal to the base in 310/310 ITC-99 and 25/25
        # ISCAS89 trials, and it comes with no sta_provenance, no STA report
        # path, no slack_status and no min_slack, while the trials that DID
        # get an acceptance decision carry all four (3734/3734).  Their
        # failure events are PRE-STA hard gates (F1 equivalence, F2 boundary),
        # and none of them is an accepted candidate when matched by candidate
        # hash (0/310).  So the ideal stage of such a candidate is NOT
        # MEASURED -- it must stay empty, and the placeholder must not be
        # mistaken for a zero delta.  The status says which of the two it is.
        if ideal_cand is None:
            ideal_label_status = 'not_measured_pre_sta'
            ideal_placeholder = trial.get('wns')
            LABEL_COVERAGE['not_measured_pre_sta'] += 1
        else:
            ideal_label_status = 'measured'
            ideal_placeholder = None
            LABEL_COVERAGE['measured'] += 1
"""

OLD_ROW = """            'ideal_wns': ideal_cand, 'ideal_baseline_wns': ideal_base,
            'ideal_delta_wns': ideal_delta,
"""
NEW_ROW = """            'ideal_wns': ideal_cand, 'ideal_baseline_wns': ideal_base,
            'ideal_delta_wns': ideal_delta,
            'ideal_label_status': ideal_label_status,
            'ideal_wns_placeholder': ideal_placeholder,
"""

OLD_SUMMARY = "        'primary_batch': PRIMARY_BATCH,\n"
NEW_SUMMARY = """        'ideal_label_coverage': dict(LABEL_COVERAGE),
        'ideal_label_coverage_note': ('the ideal-netlist stage of a candidate '
                                      'is only a MEASUREMENT when the ECO loop '
                                      'produced an acceptance decision for it.  '
                                      'A candidate that failed a pre-STA hard '
                                      'gate (equivalence / boundary) never '
                                      'reached the ideal netlist STA: the '
                                      'ledger carries no acceptance_evidence '
                                      'for it and its `wns` field is the '
                                      'ITERATION BASE\\'s value (exactly equal '
                                      'in 310/310 ITC-99 and 25/25 ISCAS89 '
                                      'trials) with no STA provenance, no '
                                      'slack_status and no min_slack, while '
                                      'every measured trial carries all of '
                                      'them.  Such a candidate therefore has '
                                      'NO ideal-stage measurement; its label '
                                      'stays empty and `ideal_label_status` '
                                      'records why.  Reading the placeholder '
                                      'as a zero delta would assert a '
                                      'measurement the ledger never made.'),
        'primary_batch': PRIMARY_BATCH,
"""

for p in BUILDERS:
    s = io.open(p, encoding='utf-8', newline='').read()
    if 'IDEAL_LABEL_STATUS' in s:
        print('%-28s already patched' % p.name)
        continue
    assert s.count(OLD_LABEL) == 1, '%s: label anchor %d' % (p.name,
                                                               s.count(OLD_LABEL))
    assert s.count(OLD_ROW) == 1, '%s: row anchor' % p.name
    assert s.count(OLD_SUMMARY) == 1, '%s: summary anchor' % p.name

    s = s.replace(OLD_LABEL, NEW_LABEL, 1)
    s = s.replace(OLD_ROW, NEW_ROW, 1)
    s = s.replace(OLD_SUMMARY, NEW_SUMMARY, 1)
    # the coverage counters, module level (right before main())
    anchor2 = "\ndef main():"
    assert s.count(anchor2) == 1, '%s: main anchor' % p.name
    s = s.replace(anchor2,
                  "\n# round 34: how the ideal-netlist stage of every row was "
                  "obtained (see the patch note)\nLABEL_COVERAGE = {\n"
                  "    'measured': 0,\n"
                  "    'not_measured_pre_sta': 0,\n"
                  "}\n" + anchor2, 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-28s patched' % p.name)

# ================================================================ curves
# The candidates that never reached the ideal netlist still have REAL placed
# and routed measurements, so they must stay in the curve.  The ideal-stage
# statistics are then computed on the subset that carries an ideal reading --
# which is exactly the subset that carried one before the patch.
OLD_CANDS = "    cands = []\n"
NEW_CANDS = """    cands = []
    dropped = {'other_batch': 0, 'post_failed': 0, 'missing_routed_label': 0}
"""

OLD_DROP_OTHER = """        if r.get('batch') not in F0_SIDE:
            continue
        if r.get('post_status') != 'ok':
            continue
"""
NEW_DROP_OTHER = """        if r.get('batch') not in F0_SIDE:
            dropped['other_batch'] += 1
            continue
        if r.get('post_status') != 'ok':
            dropped['post_failed'] += 1
            continue
"""

OLD_CURVE = """        if r.get('ideal_delta_wns') is None or r.get('post_marginal_delta_wns') is None:
            continue
"""
NEW_CURVE = """        if r.get('post_marginal_delta_wns') is None:
            # the ROUTED stage is the one that has to be a measurement; the
            # IDEAL stage may legitimately be absent (the candidate never
            # reached the ideal netlist STA), and such a candidate still
            # carries real placed/routed measurements, so it must not be
            # dropped here -- it used to be, silently, and its physical
            # stages were thrown away with it.
            dropped['missing_routed_label'] += 1
            continue
"""

OLD_IDEAL_MARG = """            'ideal_marginal': r['ideal_delta_wns'],
"""
NEW_IDEAL_MARG = """            # None when the candidate never reached the ideal netlist STA;
            # the stage statistics are computed on the subset that carries
            # the stage, so an absent ideal reading contributes to nothing.
            'ideal_marginal': r.get('ideal_delta_wns'),
"""

OLD_IDEAL_CUM = """            'ideal_cumulative': (round(r.get('ideal_wns') - cb_ideal[ckt], 6)
                                 if r.get('ideal_wns') is not None
                                 and ckt in cb_ideal else None),
"""
NEW_IDEAL_CUM = """            'ideal_cumulative': (round(r.get('ideal_wns') - cb_ideal[ckt], 6)
                                 if r.get('ideal_wns') is not None
                                 and ckt in cb_ideal else None),
            'ideal_label_status': r.get('ideal_label_status'),
"""

OLD_CURVE_WRITE = """    (FAM / 'three_point_curve.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
"""
NEW_CURVE_WRITE = """    (FAM / 'three_point_curve.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    # DROP_CENSUS (round 34): the candidates that never entered the curve,
    # by reason.  Written next to the curve so that a silent drop can never
    # hide again.
    (FAM / 'three_point_curve_drop_census.json').write_text(
        json.dumps({'n_candidates': len(cands), 'dropped': dropped,
                    'n_without_an_ideal_measurement': sum(
                        1 for c in cands if c.get('ideal_marginal') is None),
                    'note': ('a candidate whose ideal stage was never measured '
                             '(it failed a pre-STA hard gate) still carries '
                             'real placed and routed measurements, so it stays '
                             'in the curve; the stage statistics are computed '
                             'on the subset that carries the stage')},
                   indent=2, ensure_ascii=False), encoding='utf-8')
"""

for p in CURVES:
    s = io.open(p, encoding='utf-8', newline='').read()
    if "dropped['missing_routed_label']" in s:
        print('%-28s already patched' % p.name)
        continue
    assert s.count(OLD_CURVE) == 1, '%s: curve anchor %d' % (p.name,
                                                              s.count(OLD_CURVE))
    assert s.count(OLD_CANDS) == 1, '%s: cands anchor' % p.name
    assert s.count(OLD_DROP_OTHER) == 1, '%s: other-drop anchor' % p.name
    assert s.count(OLD_IDEAL_MARG) == 1, '%s: ideal-marg anchor' % p.name
    assert s.count(OLD_IDEAL_CUM) == 1, '%s: ideal-cum anchor' % p.name
    assert s.count(OLD_CURVE_WRITE) == 1, '%s: curve-write anchor' % p.name
    s = s.replace(OLD_CANDS, NEW_CANDS, 1)
    s = s.replace(OLD_DROP_OTHER, NEW_DROP_OTHER, 1)
    s = s.replace(OLD_CURVE, NEW_CURVE, 1)
    s = s.replace(OLD_IDEAL_MARG, NEW_IDEAL_MARG, 1)
    s = s.replace(OLD_IDEAL_CUM, NEW_IDEAL_CUM, 1)
    s = s.replace(OLD_CURVE_WRITE, NEW_CURVE_WRITE, 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-28s patched' % p.name)

print('done')
