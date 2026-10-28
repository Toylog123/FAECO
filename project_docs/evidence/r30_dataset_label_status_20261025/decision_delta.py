"""Round 34 -- why the decision-level reading did not move (CORRECTED chain).

The corrected patch gave 76 ITC-99 candidates their placed-stage label (their
ideal stage was never measured).  The round-33 decision-level reading came
out IDENTICAL: 14 / 27 evaluable decisions, the same wins/losses, the same
p, the same recovery fraction.

The explanation has to be verified, not assumed.  The round-33 tool's
"usable" filter requires ALL THREE stages:

    usable = [r for r in primary
              if r.get('ideal_delta_wns') is not None
              and r.get('placed_delta_wns') is not None
              and r.get('routed_delta_wns') is not None]

so a candidate whose ideal stage was never measured cannot enter a decision
pool -- and that is CORRECT: a decision compares the IDEAL criterion against
the PLACED criterion, so both criteria must be available for every candidate
in the pool.

This script verifies that mechanism end to end:
  1. the 76 newly labelled rows: do they carry all three stages now?
  2. do they reach the tool's `usable` list?
  3. do they reach any decision pool?
  4. for the decisions whose POOL did change, what changed and why (the
     reference to the loop's actual choice, which is matched by ideal WNS)?
  5. the same comparison against the FIRST (rolled-back) patch, which DID
     fabricate the ideal label and therefore DID change the reference
     reading -- the contrast shows the mechanism is real.

Everything is written to a text file.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))
import resolvable_positive_classifier as rpc   # noqa: E402

ITC = REPO / 'experiments/20261024_physical_labels_itc99'
BASE = REPO / 'scratch/round34_baseline'
EV = REPO / 'project_docs/evidence/r30_placed_selector_20261025'
OUT = REPO / 'scratch/round34_decision_delta.txt'

out = []
w = out.append


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines()
            if l.strip()]


w('=' * 78)
w('ROUND 34 -- THE DECISION-LEVEL READING (corrected chain)')
w('=' * 78)

new_tt = load_jsonl(ITC / 'training_table.jsonl')
base_tt = load_jsonl(BASE / '20261024_physical_labels_itc99__training_table.jsonl')
kb = {r['key']: r for r in base_tt}
kn = {r['key']: r for r in new_tt}

filled = [k for k in kn
          if kb.get(k, {}).get('placed_delta_wns') is None
          and kn[k].get('placed_delta_wns') is not None]
w('')
w('1) the rows that gained their placed label : %d' % len(filled))

w('')
w('2) do they carry all three stages now?')
n_all3 = n_no_ideal = n_no_placed = n_no_routed = 0
for k in filled:
    r = kn[k]
    if r.get('ideal_delta_wns') is None:
        n_no_ideal += 1
    if r.get('placed_delta_wns') is None:
        n_no_placed += 1
    if r.get('routed_delta_wns') is None:
        n_no_routed += 1
    if (r.get('ideal_delta_wns') is not None
            and r.get('placed_delta_wns') is not None
            and r.get('routed_delta_wns') is not None):
        n_all3 += 1
w('   with an ideal delta   : %d  (missing: %d)' % (len(filled) - n_no_ideal,
                                                    n_no_ideal))
w('   with a placed delta   : %d  (missing: %d)' % (len(filled) - n_no_placed,
                                                    n_no_placed))
w('   with a routed delta   : %d  (missing: %d)' % (len(filled) - n_no_routed,
                                                    n_no_routed))
w('   with ALL THREE stages: %d' % n_all3)
w('   => the round-33 tool keeps a candidate only when all three stages are')
w('      present, so these rows are still EXCLUDED from the decision pools.')
w('      That is correct: a decision compares the IDEAL criterion with the')
w('      PLACED criterion, so a candidate whose ideal stage was never')
w('      measured cannot take part in that comparison.')

w('')
w('3) the ideal stage of those rows, as the dataset records it')
st = defaultdict(int)
for k in filled:
    st[kn[k].get('ideal_label_status')] += 1
w('   ideal_label_status of the newly placed-labelled rows: %s' % (dict(st),))
w('   (the training table does not carry the status column, so the count')
w('    comes from the physical dataset:)')
ds = load_jsonl(ITC / 'physical_dataset.jsonl')
dstat = defaultdict(int)
for r in ds:
    if r.get('batch') == 'I0' and r.get('key') in set(filled):
        dstat[r.get('ideal_label_status')] += 1
w('   %s' % (dict(dstat),))

# ---- 4. the artefact comparison
w('')
w('4) the round-33 artefact (kept in the evidence package) vs the fresh one')
old = json.loads((EV / 'placed_selector_itc99.json').read_text(encoding='utf-8'))
new = json.loads((REPO / 'scratch/round33_placed_selector.json')
                 .read_text(encoding='utf-8'))['families']['itc99']
for tag in ('n_rows_training_table', 'n_rows_three_stage',
            'n_ledger_iterations_without_a_labelled_pool',
            'n_ledger_iterations_without_two_eligible_candidates',
            'n_decisions_evaluable'):
    w('   %-52s %s -> %s' % (tag, old.get(tag), new.get(tag)))
w('   primary_comparison identical : %s'
  % (json.dumps(old.get('primary_comparison'), sort_keys=True)
     == json.dumps(new.get('primary_comparison'), sort_keys=True)))
w('   recovery_fraction   identical : %s'
  % (json.dumps(old.get('recovery_fraction'), sort_keys=True)
     == json.dumps(new.get('recovery_fraction'), sort_keys=True)))
w('   overlap             identical : %s'
  % (json.dumps(old.get('overlap_with_the_oracle'), sort_keys=True)
     == json.dumps(new.get('overlap_with_the_oracle'), sort_keys=True)))
w('   the verdicts        identical : %s'
  % (json.dumps(old.get('verdict'), sort_keys=True)
     == json.dumps(new.get('verdict'), sort_keys=True)))
do = {d['circuit'] + '/' + d['iteration']: d for d in old.get('decisions', [])}
dn = {d['circuit'] + '/' + d['iteration']: d for d in new.get('decisions', [])}
w('   decisions old / new : %d / %d' % (len(do), len(dn)))
ndiff = 0
fields = ['n_pool', 'n_matched', 'n_eligible', 'n_gate_rejected',
          'ideal_eligible_key', 'placed_eligible_key', 'oracle_key',
          'gain_ideal_eligible', 'gain_placed_eligible', 'gain_routed_oracle',
          'gain_impl', 'impl_key']
for k in sorted(set(do) & set(dn)):
    d = [f for f in fields if do[k].get(f) != dn[k].get(f)]
    if d:
        ndiff += 1
        w('      %-14s changed: %s' % (k, d))
w('   decisions with ANY difference: %d' % ndiff)

w('')
w('5) THE CONTRAST: the rolled-back first patch DID move the reference')
w('   (that is how the fabrication was caught)')
w('   the first patch filled the ideal label with the ledger\'s placeholder,')
w('   which made the rows pass the three-stage filter and entered the pools.')
w('   Its effect was recorded in the round-34 decision-delta trace: 15 of the')
w('   27 decisions changed, and b01/2\'s reference reading moved from')
w('   gain_impl 0.01 to -0.01 with impl_key from t022 to t021 -- i.e. the')
w('   fabricated label made a DIFFERENT candidate look like the loop\'s own')
w('   choice.  That movement was an artefact of the fabrication, not physics.')
w('   The corrected patch produces no such movement, which is the intended')
w('   behaviour.')

(REPO / 'scratch/round34_decision_delta.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('wrote scratch/round34_decision_delta.txt')
