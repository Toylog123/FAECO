"""Round 34 -- INDEPENDENT verification of the fallback sources, BEFORE any
file under `experiments/` is touched.

Four questions, each answered by reading the ORIGINAL artefacts:

  A  Does `trial['wns']` equal `acceptance_evidence.setup_wns` on every trial
     that carries both?  (this is the candidate-side fallback)
  B  Does `call_log[iteration]['baseline_wns']` equal
     `acceptance_evidence.metric_references.setup_wns` on every trial that
     carries both?  (this is the iteration-base fallback)
  C  For every trial WITHOUT `acceptance_evidence`: is `trial['wns']` present,
     and does the ledger's call_log cover its iteration?
  D  Does the jobs TSV's `iteration` column agree with the ledger trial's
     `iteration` field for the SAME trial index?  (the builder looks the
     iteration base up by the JOBS row's iteration, so a mismatch here would
     silently make the fallback useless)

Everything is written to a text file; nothing is printed to a console that
cannot be trusted with UTF-8.
"""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'scratch/round34_fallback_verify.txt'

FAMILIES = [
    ('itc99', REPO / 'experiments/20261024_physical_labels_itc99',
     REPO / 'experiments/20260826_itc99_main',
     {'jobs_itc99_p0.tsv': 'I0P0', 'jobs_itc99.tsv': 'I0',
      'jobs_itc99_f1_p0.tsv': 'I1P0', 'jobs_itc99_f1.tsv': 'I1'}),
    ('iscas89', REPO / 'experiments/20261024_physical_labels',
     REPO / 'experiments/20260826_iscas89_main',
     {'jobs.tsv': 'F0', 'jobs_f1.tsv': 'F1', 'jobs_final.tsv': 'final',
      'jobs_s713_repaired.tsv': 'S713R', 'jobs_f1_s713.tsv': 'F1S713'}),
]


def read_jobs(path):
    rows = []
    if not path.exists():
        return rows
    text = path.read_text(encoding='utf-8-sig')
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return rows
    hdr = lines[0].split('\t')
    for l in lines[1:]:
        p = l.split('\t')
        if len(p) != len(hdr):
            continue
        rows.append(dict(zip(hdr, p)))
    return rows


out = []
w = out.append

for fam, famdir, ledgerfam, batches in FAMILIES:
    w('=' * 78)
    w('FAMILY %s' % fam)
    w('=' * 78)

    # ---- load the ledger
    ledger = {}          # (ckt, idx) -> trial
    call_log = {}        # (ckt, str(iteration)) -> baseline_wns
    call_log_iter = {}   # (ckt, str(iteration)) -> raw iteration value
    for ckt in sorted(os.listdir(ledgerfam)):
        p = ledgerfam / ckt / ckt / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        for idx, t in enumerate(d.get('trials', [])):
            if isinstance(t, dict):
                ledger[(ckt, idx)] = t
        for e in (d.get('call_log') or []):
            if not isinstance(e, dict):
                continue
            bw = e.get('baseline_wns')
            if bw is None:
                continue
            k = (ckt, str(e.get('iteration')))
            if k in call_log and call_log[k] != bw:
                w('  !! duplicate call_log iteration %s with DIFFERENT baseline'
                  % (k,))
            call_log[k] = bw
            call_log_iter[k] = e.get('iteration')

    w('  circuits=%d  trials=%d  call_log entries=%d'
      % (len({k[0] for k in ledger}), len(ledger), len(call_log)))

    # ---- A / B / C over the ledger
    a_both = a_same = a_diff = 0
    b_both = b_same = b_diff = 0
    c_total = c_has_wns = c_has_base = c_recoverable = 0
    c_no_wns = []
    c_no_base = []
    missing_iter_trial = 0
    for (ckt, idx), t in sorted(ledger.items()):
        ev = t.get('acceptance_evidence') or {}
        refs = ev.get('metric_references') or {}
        tws = t.get('wns')
        if ev:
            evw = ev.get('setup_wns')
            if evw is not None and tws is not None:
                a_both += 1
                if abs(float(evw) - float(tws)) <= 1e-12:
                    a_same += 1
                else:
                    a_diff += 1
                    if a_diff <= 5:
                        w('  !! A mismatch %s trial#%d ev=%.12g trial.wns=%.12g'
                          % (ckt, idx, float(evw), float(tws)))
            rw = refs.get('setup_wns')
            if rw is not None:
                it = t.get('iteration')
                if it is None:
                    missing_iter_trial += 1
                    continue
                kb = (ckt, str(it))
                b_both += 1
                if kb in call_log:
                    if abs(float(call_log[kb]) - float(rw)) <= 1e-12:
                        b_same += 1
                    else:
                        b_diff += 1
                        if b_diff <= 5:
                            w('  !! B mismatch %s iter=%s call_log=%.12g refs=%.12g'
                              % (ckt, it, float(call_log[kb]), float(rw)))
                else:
                    b_diff += 1
                    if b_diff <= 5:
                        w('  !! B missing call_log for %s iter=%s (refs=%.12g)'
                          % (ckt, it, float(rw)))
        else:
            c_total += 1
            hasw = tws is not None
            it = t.get('iteration')
            hasb = it is not None and (ckt, str(it)) in call_log
            c_has_wns += 1 if hasw else 0
            c_has_base += 1 if hasb else 0
            if hasw and hasb:
                c_recoverable += 1
            if not hasw:
                c_no_wns.append((ckt, idx))
            if not hasb:
                c_no_base.append((ckt, idx, it))

    w('')
    w('  A  candidate-side fallback: trial["wns"] vs acceptance_evidence.setup_wns')
    w('     both present      : %d' % a_both)
    w('     exactly equal     : %d' % a_same)
    w('     DIFFERENT         : %d' % a_diff)
    w('')
    w('  B  base-side fallback: call_log[it].baseline_wns vs '
      'metric_references.setup_wns')
    w('     both present      : %d' % b_both)
    w('     exactly equal     : %d' % b_same)
    w('     DIFFERENT/missing : %d' % b_diff)
    w('     trials with iteration=None (excluded from B): %d' % missing_iter_trial)
    w('')
    w('  C  trials WITHOUT acceptance_evidence')
    w('     total             : %d' % c_total)
    w('     carry trial["wns"]: %d' % c_has_wns)
    w('     iteration covered by call_log: %d' % c_has_base)
    w('     FULLY RECOVERABLE (both)      : %d' % c_recoverable)
    w('     missing wns  (first 5)         : %s' % (c_no_wns[:5],))
    w('     missing base (first 5)         : %s' % (c_no_base[:5],))

    # ---- D: the jobs TSV iteration column vs the ledger trial's iteration
    jobs = []
    for fname, batch in batches.items():
        p = famdir / fname
        if not p.exists():
            continue
        for r in read_jobs(p):
            r['_batch'] = batch
            jobs.append(r)
    d_both = d_same = d_diff = d_noiter = 0
    d_examples = []
    for r in jobs:
        try:
            tidx = int(r['trial_index'])
        except (KeyError, ValueError):
            continue
        ckt = r.get('circuit')
        t = ledger.get((ckt, tidx))
        if t is None:
            continue
        ti = t.get('iteration')
        ri = r.get('iteration')
        if ti is None or ri is None:
            d_noiter += 1
            continue
        d_both += 1
        if str(ti) == str(ri):
            d_same += 1
        else:
            d_diff += 1
            if len(d_examples) < 5:
                d_examples.append((ckt, tidx, ti, ri))
    w('')
    w('  D  jobs TSV "iteration" vs ledger trial "iteration" (same trial index)')
    w('     comparable        : %d' % d_both)
    w('     agree             : %d' % d_same)
    w('     DISAGREE          : %d' % d_diff)
    w('     one side None     : %d' % d_noiter)
    if d_examples:
        w('     examples (ckt, tidx, ledger, jobs): %s' % (d_examples,))

    # ---- D2: the fallback lookup that the PATCH would actually perform, on
    #         the JOBS rows (this is the real path, not the trial path)
    d2_rows = 0
    d2_hit = 0
    d2_miss = []
    for r in jobs:
        try:
            tidx = int(r['trial_index'])
        except (KeyError, ValueError):
            continue
        ckt = r.get('circuit')
        t = ledger.get((ckt, tidx))
        if t is None:
            continue
        if t.get('acceptance_evidence'):
            continue
        d2_rows += 1
        it = r.get('iteration')
        if it is not None and (ckt, str(it)) in call_log:
            d2_hit += 1
        else:
            d2_miss.append((ckt, tidx, it))
    w('')
    w('  D2 the patch lookup, on the jobs rows of the evidence-less trials')
    w('     rows without acceptance_evidence : %d' % d2_rows)
    w('     call_log hit by the jobs iteration: %d' % d2_hit)
    w('     miss (first 5)                    : %s' % (d2_miss[:5],))

    # ---- E: SIMULATE the patched builder on the REAL dataset, row by row.
    #        For every existing row of physical_dataset.jsonl the patched
    #        builder must produce a bit-identical label triple; rows whose
    #        label was null must become non-null.
    dspath = famdir / 'physical_dataset.jsonl'
    if dspath.exists():
        ds = [json.loads(l) for l in dspath.read_text(encoding='utf-8').splitlines()
              if l.strip()]
        same = 0
        newly = 0
        conflict = []
        still_null = 0
        for r in ds:
            ckt = r.get('circuit')
            try:
                tidx = int(r.get('trial_index'))
            except (TypeError, ValueError):
                tidx = -1
            t = ledger.get((ckt, tidx), {}) if tidx >= 0 else {}
            ev = t.get('acceptance_evidence') or {}
            refs = ev.get('metric_references') or {}
            old_c = ev.get('setup_wns')
            old_b = refs.get('setup_wns')
            new_c = old_c if old_c is not None else t.get('wns')
            new_b = old_b if old_b is not None else call_log.get(
                (ckt, str(r.get('iteration'))))
            old_triple = (r.get('ideal_wns'), r.get('ideal_baseline_wns'),
                          r.get('ideal_delta_wns'))
            new_delta = (None if new_c is None or new_b is None
                         else round(float(new_c) - float(new_b), 6))
            new_triple = (new_c, new_b, new_delta)
            if old_triple == new_triple:
                same += 1
            elif old_triple[0] is None and old_triple[1] is None:
                newly += 1
            else:
                conflict.append((r.get('key'), old_triple, new_triple))
            if new_triple[2] is None:
                still_null += 1
        w('')
        w('  E  SIMULATED patched builder vs the current physical_dataset.jsonl')
        w('     rows in the dataset            : %d' % len(ds))
        w('     label triple UNCHANGED         : %d' % same)
        w('     label RECOVERED (was null)     : %d' % newly)
        w('     CONFLICT (would change a value): %d' % len(conflict))
        if conflict:
            for c in conflict[:8]:
                w('       !! %s' % (c,))
        w('     rows still without a delta     : %d' % still_null)
    else:
        w('')
        w('  E  (no physical_dataset.jsonl in %s)' % famdir)
    w('')

OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('wrote', OUT)
