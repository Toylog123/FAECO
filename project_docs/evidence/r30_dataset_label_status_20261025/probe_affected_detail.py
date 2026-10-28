"""Round 34 -- two decisive checks before I rewrite the patch.

CHECK 1  Do the 310 affected trials carry ANY sign of a real ideal-netlist
         STA run?  (slack_status / min_slack_status / tns / the presence of
         any per-metric reading that could only come from a real STA)

CHECK 2  Of the affected trials that "look like" the accepted candidate of
         their iteration, how many match by CANDIDATE HASH (the strict
         identity) and how many only by instance+kind (a loose match that
         many trials of the same kind can satisfy)?  This decides whether the
         accepted candidate of an iteration can lack acceptance_evidence.

Everything is written to a text file.
"""
import json
import os
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / 'experiments/20260826_itc99_main'
LEDGER89 = REPO / 'experiments/20260826_iscas89_main'
OUT = REPO / 'scratch/round34_affected_detail.txt'

out = []
w = out.append


def read_family(fam):
    trials = []
    call = {}
    for ckt in sorted(os.listdir(fam)):
        p = fam / ckt / ckt / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        call[ckt] = {str(e.get('iteration')): e
                     for e in (d.get('call_log') or []) if isinstance(e, dict)}
        for idx, t in enumerate(d.get('trials', [])):
            if isinstance(t, dict):
                trials.append((ckt, idx, t))
    return trials, call


for label, fam in (('itc99', LEDGER), ('iscas89', LEDGER89)):
    trials, call = read_family(fam)
    aff = [(c, i, t) for c, i, t in trials if not t.get('acceptance_evidence')]
    ctl = [(c, i, t) for c, i, t in trials if t.get('acceptance_evidence')]

    w('=' * 78)
    w('FAMILY %s' % label)
    w('=' * 78)
    w('affected (no acceptance_evidence): %d   control: %d'
      % (len(aff), len(ctl)))
    if not aff:
        continue

    w('')
    w('CHECK 1 -- do the affected trials carry any real STA reading?')
    for tag, rows in (('AFFECTED', aff), ('CONTROL', ctl)):
        w('   %s' % tag)
        for f in ('slack_status', 'min_slack_status'):
            c = Counter(t.get(f) for _, _, t in rows)
            w('      %-20s %s' % (f, dict(c)))
        n_tns = sum(1 for _, _, t in rows if t.get('tns') is not None)
        n_min = sum(1 for _, _, t in rows if t.get('min_slack') is not None)
        n_area = sum(1 for _, _, t in rows if t.get('area') is not None)
        n_prov = sum(1 for _, _, t in rows if t.get('sta_provenance'))
        n_wns_none = sum(1 for _, _, t in rows if t.get('wns') is None)
        w('      tns not None            : %d' % n_tns)
        w('      min_slack not None      : %d' % n_min)
        w('      area not None           : %d' % n_area)
        w('      sta_provenance present  : %d' % n_prov)
        w('      wns is None             : %d' % n_wns_none)
        # is min_slack also equal to the base's min_slack?
        eq = ne = 0
        for c, i, t in rows:
            it = str(t.get('iteration'))
            b = (call.get(c) or {}).get(it) or {}
            bm = b.get('baseline_min_slack')
            tm = t.get('min_slack')
            if tm is not None and bm is not None:
                if abs(float(tm) - float(bm)) <= 1e-12:
                    eq += 1
                else:
                    ne += 1
        w('      min_slack == base min_slack: %d   differs: %d' % (eq, ne))
        w('      proxy_score present     : %d'
          % sum(1 for _, _, t in rows if t.get('proxy_score') is not None))

    w('')
    w('CHECK 2 -- the accepted candidate of each iteration')
    by_hash = 0
    by_ik = 0
    neither = 0
    acc_rows = []
    for c, i, t in aff:
        it = str(t.get('iteration'))
        acc = (call.get(c) or {}).get(it) or {}
        a = acc.get('accepted')
        if not isinstance(a, dict):
            neither += 1
            continue
        h_ok = a.get('candidate_hash') == t.get('candidate_hash')
        ik_ok = (a.get('instance') == t.get('instance')
                 and a.get('kind') == t.get('kind'))
        if h_ok:
            by_hash += 1
        elif ik_ok:
            by_ik += 1
        else:
            neither += 1
        if h_ok:
            acc_rows.append((c, i, it, a.get('instance'), a.get('kind'),
                             t.get('candidate_hash'),
                             a.get('candidate_hash')))
    w('   affected trials matching the accepted candidate BY HASH   : %d' % by_hash)
    w('   affected trials matching the accepted candidate BY inst+kind only: %d'
      % by_ik)
    w('   not the accepted candidate at all                       : %d' % neither)
    if acc_rows:
        w('   the by-hash ones (first 10):')
        for r in acc_rows[:10]:
            w('      %s trial#%d it=%s inst=%s kind=%s  t_hash=%s  a_hash=%s'
              % (r[0], r[1], r[2], r[3], r[4],
                 (r[5] or '')[:12], (r[6] or '')[:12]))

    # does the ACCEPTED entry itself carry acceptance_evidence?
    w('')
    w('   does the ledger\'s accepted entry carry its own '
      'acceptance_evidence?')
    n_acc_with = n_acc_without = 0
    for c, i, t in trials:
        it = str(t.get('iteration'))
        a = ((call.get(c) or {}).get(it) or {}).get('accepted')
        if isinstance(a, dict):
            if a.get('acceptance_evidence'):
                n_acc_with += 1
            else:
                n_acc_without += 1
    w('      accepted entries WITH acceptance_evidence : %d' % n_acc_with)
    w('      accepted entries WITHOUT                  : %d' % n_acc_without)
    w('')

(REPO / 'scratch/round34_affected_detail.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('wrote scratch/round34_affected_detail.txt')
