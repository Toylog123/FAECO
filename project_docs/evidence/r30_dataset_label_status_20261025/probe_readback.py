"""Round 34 probe read-back: classify the 12 probe runs and price the extension.

Everything is read from the probe's own products:
  * experiments/20261024_physical_transfer_noise/runs/<ckt>_baseline_R0/rc.tsv
  * .../pr_run.log
The floorplan geometry is extracted with the LABEL FAMILY's own reader
(`gen_itc99_jobs.read_geometry`), not with a re-implementation, so the
geometry this probe produces is by construction the geometry the labelling
batch will consume.

Classification follows the pre-registration (scratch/round34_preregistration.json):
  rc=0 and <= 900 s          -> fast_reachable
  rc=0 and 900 < s <= 1800   -> slow_reachable
  rc=124 (timeout)           -> unreachable
  any other non-zero rc      -> failed (must be attributed, never counted as
                                "unreachable")
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOISE = REPO / 'experiments/20261024_physical_transfer_noise'
MAIN = REPO / 'experiments/20260826_itc99_main'
LABELS = REPO / 'experiments/20261024_physical_labels_itc99'

sys.path.insert(0, str(LABELS))
import gen_itc99_jobs as gj   # noqa: E402  (the label family's own reader)

FAST_S = 900
SLOW_S = 1800

ALREADY = ('b01', 'b02', 'b03', 'b08', 'b09', 'b10', 'b13')

# the measured cost structure of the EXISTING 7-circuit batch (the I0 routed
# family and the IPLACED family), used only to turn the per-circuit probe
# seconds into an extension budget
def batch_seconds(fam):
    secs = []
    d = LABELS / 'runs' / fam
    if not d.exists():
        return secs
    for p in d.iterdir():
        if not p.is_dir():
            continue
        rc = p / 'rc.tsv'
        if not rc.exists():
            continue
        parts = rc.read_text(encoding='utf-8').strip().split('\t')
        if len(parts) >= 3:
            try:
                secs.append(int(parts[2]))
            except ValueError:
                pass
    return secs


def median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def sha256_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def circuit_candidates(ckt):
    """Distinct candidates (dedup key = netlist text sha256) and the ledger
    rounds, counted exactly the way the label family counts them."""
    ledger = MAIN / ckt / ckt / 'eval_trials.json'
    if not ledger.exists():
        return None
    trials = gj.load_trials(ledger)
    seen = set()
    per_round = defaultdict(set)
    n_accepted = 0
    for t in trials:
        if not isinstance(t, dict):
            continue
        text = t.get('candidate_netlist_text')
        if not text:
            continue
        h = sha256_text(text)
        if h in seen:
            continue
        seen.add(h)
        per_round[str(t.get('iteration'))].add(h)
        if t.get('accepted'):
            n_accepted += 1
    return {'n_trials': len(trials), 'n_distinct_candidates': len(seen),
            'n_accepted': n_accepted,
            'n_rounds': len(per_round),
            'rounds_with_ge2_candidates': sum(1 for v in per_round.values()
                                               if len(v) >= 2)}


def gate_eligible_rounds(ckt):
    """Ledger rounds with at least two GATE-ELIGIBLE candidates -- the unit the
    decision-level analysis needs (a round with fewer than two eligible
    candidates cannot be evaluated)."""
    ledger = MAIN / ckt / ckt / 'eval_trials.json'
    if not ledger.exists():
        return None
    trials = gj.load_trials(ledger)
    by_round = defaultdict(list)
    for t in trials:
        if not isinstance(t, dict):
            continue
        ae = t.get('acceptance_evidence') or {}
        viol = ae.get('violations') or []
        hard = [fe for fe in (t.get('failure_events') or [])
                if fe.get('hard_gate')]
        eligible = (not viol) and (not hard)
        by_round[str(t.get('iteration'))].append(eligible)
    n2 = sum(1 for v in by_round.values() if sum(1 for x in v if x) >= 2)
    return {'n_rounds': len(by_round), 'n_rounds_with_ge2_eligible': n2}


routed = batch_seconds('I0')
placed = batch_seconds('IPLACED')
placed_ratio = (median(placed) / median(routed)) if (routed and placed
                                                     and median(routed)) else None

probe_jobs = []
p = REPO / 'scratch/round34_probe_jobs.tsv'
if p.exists():
    lines = p.read_text(encoding='utf-8').splitlines()
    header = lines[0].split('\t')
    for line in lines[1:]:
        if line.strip():
            probe_jobs.append(dict(zip(header, line.split('\t'))))

out = {'measured': {'routed_median_s': median(routed),
                    'placed_median_s': median(placed),
                    'placed_over_routed_ratio': placed_ratio,
                    'n_routed_runs': len(routed),
                    'n_placed_runs': len(placed)},
       'rules': {'fast_reachable_max_s': FAST_S,
                 'slow_reachable_max_s': SLOW_S,
                 'timeout_rc': 124},
       'circuits': {}}

for job in probe_jobs:
    key = job['key']
    ckt = key.split('_')[0]
    d = NOISE / 'runs' / key
    rec = {'key': key, 'ckt': ckt, 'util': job['util'],
           'netlist': job['netlist'], 'top': job['top']}
    rcfile = d / 'rc.tsv'
    if not rcfile.exists():
        rec['status'] = 'not_run'
        out['circuits'][ckt] = rec
        continue
    parts = rcfile.read_text(encoding='utf-8').strip().split('\t')
    rc = parts[1] if len(parts) > 1 else '?'
    secs = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
    rec['rc'] = rc
    rec['seconds'] = secs
    if rc == '0' and secs is not None and secs <= FAST_S:
        rec['status'] = 'fast_reachable'
    elif rc == '0' and secs is not None and secs <= SLOW_S:
        rec['status'] = 'slow_reachable'
    elif rc == '124':
        rec['status'] = 'unreachable'
    elif rc == '0':
        rec['status'] = 'over_timeout_limit'
    else:
        rec['status'] = 'failed'
    # the geometry the label family would consume
    try:
        geom = gj.read_geometry(ckt)
        rec['geometry'] = geom
        rec['geometry_readable'] = True
    except SystemExit as exc:
        rec['geometry_readable'] = False
        rec['geometry_error'] = str(exc)
    except Exception as exc:                       # noqa: BLE001
        rec['geometry_readable'] = False
        rec['geometry_error'] = repr(exc)
    cand = circuit_candidates(ckt)
    if cand:
        rec['ledger'] = cand
    gate = gate_eligible_rounds(ckt)
    if gate:
        rec['gate'] = gate
    # the extension budget for this circuit, at the MEASURED per-run cost
    if rec['status'] in ('fast_reachable', 'slow_reachable') and cand:
        n = cand['n_distinct_candidates'] + 2      # baseline + final netlist
        per = secs
        routed_h = n * per / 3600.0
        placed_h = routed_h * (placed_ratio or 0.22)
        rec['extension_budget'] = {
            'n_jobs_per_stage': n,
            'routed_hours_serial': round(routed_h, 2),
            'placed_hours_serial': round(placed_h, 2),
            'total_hours_serial': round(routed_h + placed_h, 2),
            'total_hours_at_par4': round((routed_h + placed_h) / 4.0, 2),
            'note': 'per-job cost proxy = this circuit\'s measured baseline '
                    'run; the placed stage uses the family-measured '
                    'placed/routed median ratio',
        }
    out['circuits'][ckt] = rec

# ---- the projection: what the extension would buy
reach = [c for c in out['circuits'].values()
         if c.get('status') in ('fast_reachable', 'slow_reachable')]
tot_h = sum((c.get('extension_budget') or {}).get('total_hours_serial', 0.0)
            for c in reach)
extra_rounds = sum((c.get('gate') or {}).get('n_rounds_with_ge2_eligible', 0)
                    for c in reach)
extra_jobs = sum((c.get('extension_budget') or {}).get('n_jobs_per_stage', 0)
                  for c in reach)
out['projection'] = {
    'n_reachable_circuits': len(reach),
    'reachable_circuits': sorted(c['ckt'] for c in reach),
    'unreachable_circuits': sorted(c['ckt'] for c in out['circuits'].values()
                                   if c.get('status') == 'unreachable'),
    'failed_circuits': sorted(c['ckt'] for c in out['circuits'].values()
                               if c.get('status') == 'failed'),
    'not_run_circuits': sorted(c['ckt'] for c in out['circuits'].values()
                                if c.get('status') == 'not_run'),
    'extra_candidate_jobs_per_stage': extra_jobs,
    'extra_hours_serial': round(tot_h, 2),
    'extra_hours_at_par4': round(tot_h / 4.0, 2),
    'extra_evaluable_decisions_upper_bound': extra_rounds,
    'note': 'the extra evaluable decisions are the ledger rounds of the '
            'reachable circuits that have at least two gate-eligible '
            'candidates; the actual yield is lower because a round is only '
            'evaluable if its candidates carry all three stage labels',
}

Path('scratch/round34_probe.json').write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

lines = []
lines.append('%-5s %-6s %-16s %-8s %s' % ('ckt', 'util', 'status', 'seconds',
                                           'gate-eligible rounds'))
for ckt in sorted(out['circuits']):
    c = out['circuits'][ckt]
    lines.append('%-5s %-6s %-16s %-8s %s' % (
        ckt, c.get('util'), c.get('status'), c.get('seconds'),
        '%s / %s' % ((c.get('gate') or {}).get('n_rounds_with_ge2_eligible'),
                     (c.get('gate') or {}).get('n_rounds'))))
p2 = out['projection']
lines.append('')
lines.append('reachable: %s' % p2['reachable_circuits'])
lines.append('unreachable: %s' % p2['unreachable_circuits'])
lines.append('failed: %s' % p2['failed_circuits'])
lines.append('not run: %s' % p2['not_run_circuits'])
lines.append('extra candidate jobs per stage: %s'
             % p2['extra_candidate_jobs_per_stage'])
lines.append('extra hours serial: %s   at PAR=4: %s'
             % (p2['extra_hours_serial'], p2['extra_hours_at_par4']))
lines.append('extra evaluable decisions (upper bound): %s'
             % p2['extra_evaluable_decisions_upper_bound'])
Path('scratch/round34_probe_readback.txt').write_text('\n'.join(lines),
                                                       encoding='utf-8')
print('\n'.join(lines))
