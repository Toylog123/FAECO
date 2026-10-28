"""Round 33: would the PLACED stage pick better candidates than the ideal
netlist, once the outcome is measured on the post-route (routed) stage?

The FAECO loop accepted one candidate per ECO iteration on the IDEAL netlist.
The physical labels give three stages for the same candidate: the ideal
marginal delta, the placed marginal delta and the routed marginal delta.
Round 32 established that the candidate-level physical signal lives in those
netlist-derived measurements (oracle within-pool AUC 0.85-0.93) and not in
the topology, and rounds 21/24 established that the placed delta is the
strongest cheap proxy for the routed label.  What nobody has measured is the
DECISION-level consequence: if the acceptance criterion moves from the ideal
stage to the placed stage, how much post-route gain is recovered?

Sign convention (settled from the ledger, see
scratch/round33_preregistration_correction_01.json)
------------------------------------------------------------
    marginal delta = candidate WNS - the iteration base WNS the candidate was
    derived from.  A negative WNS is a violated path, so a LESS negative WNS
    is a SMALLER violation:  delta > 0 is an IMPROVEMENT and the best
    candidate of a set is the one with the LARGEST delta.
    Independent evidence: over every ledger decision of both families the
    sign of (accepted.wns - baseline_wns) agrees with the ledger's own
    `improved` flag (ISCAS89 27/27, ITC-99 74/74 non-zero).

The candidate set
-----------------
    The loop does NOT simply pick the best WNS: a hard gate
    (`acceptance_budget_violation`, e.g. a setup_tns violation) rejects
    candidates first.  Every selector here therefore chooses inside the
    GATE-ELIGIBLE set of the iteration, so the comparison is between the
    ideal criterion and the placed criterion over the SAME options.  The
    loop's actual choice is reported as a reference.

Data provenance
---------------
    rows: <family>/training_table.jsonl -- one row per candidate of the
    PRIMARY physical realisation (F0/S713R for ISCAS89, I0 for ITC-99), with
    the ideal / placed / routed marginal deltas of that realisation.
    decisions: the LEDGER (eval_trials.json) -- the acceptance decision and
    the per-trial gate outcome are recorded there, not in the dataset.
    The dataset's accepted_ideal field carries two meanings (the accepted
    candidate, and the circuit BASE rows with iteration '-1'), so it is not
    used to identify decisions.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'experiments/20261024_physical_labels/tools'))
import resolvable_positive_classifier as rpc   # noqa: E402  (project kernel)

FAMS = {
    'iscas89': REPO / 'experiments/20261024_physical_labels',
    'itc99': REPO / 'experiments/20261024_physical_labels_itc99',
}
PRIMARY_BATCHES = {
    'iscas89': ('F0', 'S713R'),
    'itc99': ('I0',),
}
LEDGER_FAM = {
    'iscas89': REPO / 'experiments/20260826_iscas89_main',
    'itc99': REPO / 'experiments/20260826_itc99_main',
}
RECOVERY_FRACTION_GATE = 0.25
P_GATE = 0.05
MIN_DECISIONS = 10


def load_training_table(fam_dir):
    rows = []
    with (fam_dir / 'training_table.jsonl').open(encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_ledger(ledger_fam):
    """The ECO loop's own record: per iteration, the acceptance decision and
    every trial with its gate outcome."""
    out = defaultdict(lambda: {'trials': [], 'accepted': None})
    if not ledger_fam.exists():
        return out
    for ckt_dir in sorted(ledger_fam.iterdir()):
        if not ckt_dir.is_dir():
            continue
        for p in sorted(ckt_dir.rglob('eval_trials.json')):
            try:
                d = json.loads(p.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            ckt = ckt_dir.name
            for entry in (d.get('call_log') or []):
                if not isinstance(entry, dict):
                    continue
                it = str(entry.get('iteration'))
                key = (ckt, it)
                acc = entry.get('accepted')
                if isinstance(acc, dict):
                    out[key]['accepted'] = {
                        'instance': acc.get('instance'),
                        'kind': acc.get('kind'),
                        'wns': acc.get('wns'),
                        'baseline_wns': entry.get('baseline_wns'),
                        'improved': entry.get('improved'),
                        'n_trials': entry.get('n_trials'),
                    }
            for t in (d.get('trials') or []):
                if not isinstance(t, dict):
                    continue
                it = str(t.get('iteration'))
                ae = t.get('acceptance_evidence') or {}
                viol = ae.get('violations') or []
                hard = [fe for fe in (t.get('failure_events') or [])
                        if fe.get('hard_gate')]
                out[(ckt, it)]['trials'].append({
                    'instance': t.get('instance'),
                    'kind': t.get('kind'),
                    'wns': t.get('wns'),
                    'accepted': bool(t.get('accepted')),
                    'violations': list(viol),
                    'hard_gate_failures': [fe.get('type') for fe in hard],
                    'eligible': (not viol) and (not hard),
                })
    return out


def match_trials(pool_rows, trials):
    """Attach each labelled candidate to its ledger trial.

    The disambiguation is the one the project's counterfactual tool uses:
    the trial is matched by instance AND kind, and the ideal WNS has to
    agree with the ledger's own reading of that trial.
    """
    by_inst_kind = defaultdict(list)
    for t in trials:
        by_inst_kind[(t.get('instance'), t.get('kind'))].append(t)
    matched = []
    for r in pool_rows:
        cands = by_inst_kind.get((r.get('instance'), r.get('kind')), [])
        if not cands:
            continue
        wns = r.get('ideal_wns')
        hit = None
        for t in cands:
            if (wns is not None and t.get('wns') is not None
                    and abs(float(t['wns']) - float(wns)) < 1e-9):
                hit = t
                break
        if hit is None:
            continue
        matched.append((r, hit))
    return matched


def analyse_family(name, fam_dir):
    rows = load_training_table(fam_dir)
    allowed = PRIMARY_BATCHES[name]
    primary = [r for r in rows if r.get('label_batch') in allowed]

    usable = [r for r in primary
              if r.get('ideal_delta_wns') is not None
              and r.get('placed_delta_wns') is not None
              and r.get('routed_delta_wns') is not None]

    pools = defaultdict(list)
    for r in usable:
        pools[(r.get('circuit'), str(r.get('iteration')))].append(r)

    ledger = load_ledger(LEDGER_FAM[name])

    decisions = []
    n_ledger_iters = 0
    n_no_pool = 0
    n_no_eligible = 0
    for key in sorted(ledger, key=lambda k: (str(k[0]), str(k[1]))):
        n_ledger_iters += 1
        pool = pools.get(key)
        if not pool or len(pool) < 2:
            n_no_pool += 1
            continue
        matched = match_trials(pool, ledger[key]['trials'])
        if not matched:
            n_no_eligible += 1
            continue
        eligible = [(r, t) for r, t in matched if t['eligible']]
        if len(eligible) < 2:
            n_no_eligible += 1
            continue

        acc_rec = ledger[key]['accepted']

        def pick(pairs, field):
            # the LARGEST delta = the best (a less negative WNS = a smaller
            # violation); ties broken by key so the choice is deterministic
            return min(pairs, key=lambda p: (-p[0][field], p[0]['key']))

        ideal_el = pick(eligible, 'ideal_delta_wns')
        placed_el = pick(eligible, 'placed_delta_wns')
        routed_all = pick(matched, 'routed_delta_wns')

        # the loop's actual choice, if it carries a physical label
        impl = None
        if acc_rec:
            for r, t in matched:
                if (acc_rec.get('instance') == r.get('instance')
                        and acc_rec.get('kind') == r.get('kind')
                        and (acc_rec.get('wns') is None
                             or r.get('ideal_wns') is None
                             or abs(float(acc_rec['wns'])
                                    - float(r['ideal_wns'])) < 1e-9)):
                    impl = (r, t)
                    break

        decisions.append({
            'circuit': key[0],
            'iteration': key[1],
            'n_pool': len(pool),
            'n_matched': len(matched),
            'n_eligible': len(eligible),
            'n_gate_rejected': len(matched) - len(eligible),
            'ledger_n_trials': (acc_rec or {}).get('n_trials'),
            'ledger_accepted_wns': (acc_rec or {}).get('wns'),
            'ledger_baseline_wns': (acc_rec or {}).get('baseline_wns'),
            'ledger_improved': (acc_rec or {}).get('improved'),
            'impl_key': impl[0]['key'] if impl else None,
            'impl_eligible': (impl[1]['eligible'] if impl else None),
            'gain_impl': (round(float(impl[0]['routed_delta_wns']), 6)
                          if impl else None),
            'gain_ideal_eligible': round(float(ideal_el[0]['routed_delta_wns']), 6),
            'gain_placed_eligible': round(float(placed_el[0]['routed_delta_wns']), 6),
            'gain_routed_oracle': round(float(routed_all[0]['routed_delta_wns']), 6),
            'ideal_eligible_key': ideal_el[0]['key'],
            'placed_eligible_key': placed_el[0]['key'],
            'oracle_key': routed_all[0]['key'],
            'placed_is_ideal_eligible': (placed_el[0]['key']
                                         == ideal_el[0]['key']),
            'placed_is_oracle': (placed_el[0]['key'] == routed_all[0]['key']),
            'ideal_eligible_is_oracle': (ideal_el[0]['key']
                                         == routed_all[0]['key']),
            'ideal_delta_ideal_eligible': ideal_el[0]['ideal_delta_wns'],
            'placed_delta_placed_eligible': placed_el[0]['placed_delta_wns'],
            'routed_delta_oracle': routed_all[0]['routed_delta_wns'],
        })

    # ---- the pre-registered primary comparison
    diffs = [d['gain_placed_eligible'] - d['gain_ideal_eligible']
             for d in decisions]
    p, pos, neg = rpc.sign_test_p(diffs)
    nonzero = [x for x in diffs if x != 0]

    diffs_impl = [d['gain_placed_eligible'] - d['gain_impl']
                  for d in decisions if d['gain_impl'] is not None]
    p_impl, pos_impl, neg_impl = rpc.sign_test_p(diffs_impl)

    num = sum(d['gain_placed_eligible'] - d['gain_ideal_eligible']
              for d in decisions)
    den = sum(d['gain_routed_oracle'] - d['gain_ideal_eligible']
              for d in decisions)
    recovery = (num / den) if den > 0 else None

    n = len(decisions)
    overlap_placed = sum(1 for d in decisions if d['placed_is_oracle'])
    overlap_ideal = sum(1 for d in decisions if d['ideal_eligible_is_oracle'])
    same_sel = sum(1 for d in decisions if d['placed_is_ideal_eligible'])

    per_circuit = {}
    for d in decisions:
        per_circuit.setdefault(d['circuit'], []).append(d)
    per_circuit_out = {}
    for ckt, ds in sorted(per_circuit.items()):
        dd = [x['gain_placed_eligible'] - x['gain_ideal_eligible'] for x in ds]
        pc, ppos, pneg = rpc.sign_test_p(dd)
        per_circuit_out[ckt] = {
            'n_decisions': len(ds),
            'wins': ppos, 'losses': pneg, 'sign_test_p': pc,
            'mean_gain_ideal_eligible': round(
                sum(x['gain_ideal_eligible'] for x in ds) / len(ds), 6),
            'mean_gain_placed_eligible': round(
                sum(x['gain_placed_eligible'] for x in ds) / len(ds), 6),
            'mean_gain_oracle': round(
                sum(x['gain_routed_oracle'] for x in ds) / len(ds), 6),
            'mean_gain_impl': (round(
                sum(x['gain_impl'] for x in ds if x['gain_impl'] is not None)
                / len([x for x in ds if x['gain_impl'] is not None]), 6)
                if any(x['gain_impl'] is not None for x in ds) else None),
            'n_impl_labelled': sum(1 for x in ds if x['gain_impl'] is not None),
        }

    sufficient = n >= MIN_DECISIONS
    cond1 = bool(sufficient and p is not None and p < P_GATE)
    cond2 = bool(recovery is not None and recovery >= RECOVERY_FRACTION_GATE)
    cond3 = bool(overlap_placed > overlap_ideal)
    h1 = bool(cond1 and cond2 and cond3)

    return {
        'family': name,
        'n_rows_training_table': len(rows),
        'n_rows_primary_realisation': len(primary),
        'n_rows_three_stage': len(usable),
        'n_ledger_iterations': n_ledger_iters,
        'n_ledger_iterations_without_a_labelled_pool': n_no_pool,
        'n_ledger_iterations_without_two_eligible_candidates': n_no_eligible,
        'n_decisions_evaluable': n,
        'sign_convention': 'delta = candidate WNS - base WNS; delta > 0 = the '
                           'violation got smaller = an improvement; the best '
                           'candidate of a set is the one with the LARGEST '
                           'delta (settled from the ledger, see the '
                           'pre-registration correction 01)',
        'primary_comparison': {
            'statistic': 'routed delta of S_placed_eligible minus that of '
                         'S_ideal_eligible, per decision',
            'n': n, 'wins': pos, 'losses': neg,
            'ties': len(diffs) - len(nonzero),
            'sign_test_p': p,
            'mean_diff': round(sum(diffs) / len(diffs), 6) if diffs else None,
            'median_diff': (round(sorted(diffs)[len(diffs) // 2], 6)
                            if diffs else None),
            'sum_diff': round(sum(diffs), 6),
        },
        'reference_vs_the_loop_actual_choice': {
            'note': 'S_placed_eligible against the candidate the loop really '
                    'accepted (the loop chose among the gate-eligible set '
                    'using the ideal stage)',
            'n': len(diffs_impl), 'wins': pos_impl, 'losses': neg_impl,
            'sign_test_p': p_impl,
            'mean_diff': (round(sum(diffs_impl) / len(diffs_impl), 6)
                          if diffs_impl else None),
        },
        'recovery_fraction': {
            'definition': 'sum(gain_placed_eligible - gain_ideal_eligible) / '
                          'sum(gain_routed_oracle - gain_ideal_eligible)',
            'numerator': round(num, 6), 'denominator': round(den, 6),
            'value': round(recovery, 6) if recovery is not None else None,
        },
        'overlap_with_the_oracle': {
            'placed_eligible_is_oracle': overlap_placed,
            'ideal_eligible_is_oracle': overlap_ideal,
            'placed_is_ideal_eligible': same_sel,
            'n': n,
        },
        'per_circuit': per_circuit_out,
        'verdict': {
            'gate_p': P_GATE,
            'gate_recovery_fraction': RECOVERY_FRACTION_GATE,
            'min_decisions': MIN_DECISIONS,
            'n_decisions': n,
            'sufficient_n': sufficient,
            'cond1_paired_sign_test': cond1,
            'cond2_recovery_fraction': cond2,
            'cond3_overlap_direction': cond3,
            'H1_triggered': h1,
            'verdict': ('H1 触发：搬到布局后档在决策层面有可检验的收益'
                        if h1 else
                        'H1 未触发：搬到布局后档没有拿到判决级别的收益'),
        },
        'decisions': decisions,
        'pre_registration': 'scratch/round33_preregistration.json',
        'pre_registration_correction': ('scratch/round33_preregistration_'
                                        'correction_01.json'),
    }


def main():
    out_path = REPO / 'scratch/round33_placed_selector.json'
    res = {'families': {},
           'pre_registration': 'scratch/round33_preregistration.json',
           'pre_registration_correction':
               'scratch/round33_preregistration_correction_01.json'}
    for name, fam_dir in FAMS.items():
        print('=== %s ===' % name, flush=True)
        r = analyse_family(name, fam_dir)
        res['families'][name] = r
        pc = r['primary_comparison']
        ov = r['overlap_with_the_oracle']
        print('  ledger iterations=%d  evaluable decisions=%d' %
              (r['n_ledger_iterations'], r['n_decisions_evaluable']), flush=True)
        print('  placed_eligible - ideal_eligible: %d/%d (w/l) p=%s  '
              'recovery=%s' % (pc['wins'], pc['losses'], pc['sign_test_p'],
                              r['recovery_fraction']['value']), flush=True)
        print('  overlap with the oracle: placed %d / ideal %d ; the two '
              'selectors pick the same candidate in %d of %d'
              % (ov['placed_eligible_is_oracle'],
                 ov['ideal_eligible_is_oracle'],
                 ov['placed_is_ideal_eligible'], ov['n']), flush=True)
        v = r['verdict']
        print('  H1 triggered: %s (cond1=%s cond2=%s cond3=%s)'
              % (v['H1_triggered'], v['cond1_paired_sign_test'],
                 v['cond2_recovery_fraction'], v['cond3_overlap_direction']),
              flush=True)
    out_path.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                        encoding='utf-8')
    print('written', out_path, flush=True)


if __name__ == '__main__':
    main()
