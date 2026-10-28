"""Round 34 -- are the 76 recovered labels MEASUREMENTS or COPIED BASELINES?

All 76 recovered rows came out with ideal_delta_wns EXACTLY 0.0.  Two
explanations, with very different consequences:

  H1  the candidate was really evaluated and really did not move the worst
      path -> the recovered label is a genuine, if inert, measurement;
  H2  the trial was never evaluated and its `wns` was inherited from the
      iteration baseline -> the recovered label is a PLACEHOLDER that would
      masquerade as "no effect" and must not be used as a measurement.

This script checks the ledger's OWN record of each affected trial:
  * does the trial carry an STA provenance / report path / runtime?
  * is its `wns` equal to the iteration base's `baseline_wns`?
  * does the trial carry a `failure_events` entry that says the STA failed?
  * how do the affected trials compare with the trials that DID get an
    acceptance decision?

Everything is written to a text file.
"""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / 'experiments/20260826_itc99_main'
OUT = REPO / 'scratch/round34_recovered_label_provenance.txt'

out = []
w = out.append

# the affected trials: the ones the training table recovered
tt = [json.loads(l) for l in
      (REPO / 'experiments/20261024_physical_labels_itc99'
       / 'training_table.jsonl').read_text(encoding='utf-8').splitlines()
      if l.strip()]
rec = [r for r in tt if r.get('ideal_wns') is not None
       and r.get('ideal_delta_wns') == 0.0
       and r.get('trial_index') is not None]
# the affected set = the trials WITHOUT acceptance_evidence (the ones the
# fallback had to fill in); identify them by the ledger, not by the delta
affected = []
control = []
for ckt in sorted(os.listdir(LEDGER)):
    p = LEDGER / ckt / ckt / 'eval_trials.json'
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding='utf-8'))
    call = {str(e.get('iteration')): e for e in (d.get('call_log') or [])
            if isinstance(e, dict)}
    for idx, t in enumerate(d.get('trials', [])):
        if not isinstance(t, dict):
            continue
        ev = t.get('acceptance_evidence')
        it = str(t.get('iteration'))
        base = (call.get(it) or {}).get('baseline_wns')
        rec_row = {
            'ckt': ckt, 'idx': idx, 'it': it,
            'has_ev': bool(ev),
            'wns': t.get('wns'),
            'base': base,
            'sta_provenance': t.get('sta_provenance'),
            'runtime_s': t.get('runtime_s'),
            'failure_events': t.get('failure_events') or [],
            'trial_failure_events': t.get('trial_failure_events') or [],
            'slack_status': t.get('slack_status'),
            'min_slack_status': t.get('min_slack_status'),
            'physical_status': t.get('physical_status'),
            'kind': t.get('kind'),
            'accepted': t.get('accepted'),
        }
        if not ev:
            affected.append(rec_row)
        else:
            control.append(rec_row)

w('=' * 78)
w('ROUND 34 -- ARE THE RECOVERED LABELS MEASUREMENTS OR COPIED BASELINES?')
w('=' * 78)
w('')
w('trials WITHOUT acceptance_evidence (the affected set): %d' % len(affected))
w('trials WITH    acceptance_evidence (the control set) : %d' % len(control))


def summarise(rows, label):
    w('')
    w('--- %s (n=%d)' % (label, len(rows)))
    n_wns_none = sum(1 for r in rows if r['wns'] is None)
    n_eq_base = sum(1 for r in rows
                     if r['wns'] is not None and r['base'] is not None
                     and abs(float(r['wns']) - float(r['base'])) <= 1e-12)
    n_ne_base = sum(1 for r in rows
                     if r['wns'] is not None and r['base'] is not None
                     and abs(float(r['wns']) - float(r['base'])) > 1e-12)
    n_no_base = sum(1 for r in rows if r['base'] is None)
    w('   wns is None                     : %d' % n_wns_none)
    w('   wns == the iteration base WNS   : %d' % n_eq_base)
    w('   wns != the iteration base WNS   : %d' % n_ne_base)
    w('   no base available               : %d' % n_no_base)
    n_prov = sum(1 for r in rows if r['sta_provenance'])
    n_path = sum(1 for r in rows
                 if (r['sta_provenance'] or {}).get('report_path'))
    n_rt = sum(1 for r in rows if r['runtime_s'] is not None)
    w('   carry an sta_provenance         : %d' % n_prov)
    w('   carry an STA report path        : %d' % n_path)
    w('   carry a runtime_s               : %d' % n_rt)
    n_fail = sum(1 for r in rows if r['failure_events'])
    n_fail_hard = sum(1 for r in rows
                       if any(f.get('hard_gate') for f in r['failure_events']))
    w('   carry failure_events            : %d (hard gate: %d)'
      % (n_fail, n_fail_hard))
    n_tfe = sum(1 for r in rows if r['trial_failure_events'])
    w('   carry trial_failure_events      : %d' % n_tfe)
    kinds = {}
    for r in rows:
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    w('   by kind                         : %s' % (kinds,))
    n_acc = sum(1 for r in rows if r['accepted'])
    w('   flagged accepted                : %d' % n_acc)
    return n_eq_base, n_ne_base, n_prov, n_path


ae, an, ap, ath = summarise(affected, 'AFFECTED (no acceptance_evidence)')
ce, cn, cp, cpth = summarise(control, 'CONTROL (has acceptance_evidence)')

w('')
w('=' * 78)
w('READING')
w('=' * 78)
w('')
w('If the affected trials were really evaluated, their STA provenance and')
w('report path would be present and their WNS would NOT all equal the')
w('iteration base.  If they were never evaluated, the WNS is a copy of the')
w('base and the recovered label is a PLACEHOLDER.')
w('')
w('affected: wns == base for %d of %d (the rest differ: %d)'
  % (ae, ae + an, an))
w('control : wns == base for %d of %d (the rest differ: %d)'
  % (ce, ce + cn, cn))
w('affected: with an STA report path %d ; control: %d' % (ath, cpth))
w('')

# ---- the failure events of the affected trials
w('the failure_events of the affected trials (first 12 distinct):')
seen = set()
for r in affected:
    for f in r['failure_events']:
        key = (f.get('type'), bool(f.get('hard_gate')))
        if key in seen:
            continue
        seen.add(key)
        w('   %s (hard_gate=%s)' % (key[0], key[1]))
        w('      full: %s' % (json.dumps(f, ensure_ascii=False)[:400],))
        if len(seen) >= 12:
            break

w('')
w('the failure_events of the CONTROL trials (first 6 distinct):')
seen = set()
for r in control:
    for f in r['failure_events']:
        key = (f.get('type'), bool(f.get('hard_gate')))
        if key in seen:
            continue
        seen.add(key)
        w('   %s (hard_gate=%s)' % (key[0], key[1]))
        if len(seen) >= 6:
            break

w('')
w('--- the affected trials whose WNS differs from the base (if any)')
n = 0
for r in affected:
    if r['wns'] is not None and r['base'] is not None \
            and abs(float(r['wns']) - float(r['base'])) > 1e-12:
        n += 1
        if n <= 20:
            w('   %s trial#%d it=%s kind=%s wns=%s base=%s prov=%s'
              % (r['ckt'], r['idx'], r['it'], r['kind'], r['wns'], r['base'],
                 json.dumps(r['sta_provenance'], ensure_ascii=False)[:160]))
w('   total: %d' % n)

(REPO / 'scratch/round34_recovered_label_provenance.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('wrote scratch/round34_recovered_label_provenance.txt')
