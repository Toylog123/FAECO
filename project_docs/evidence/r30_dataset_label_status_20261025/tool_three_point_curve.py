"""Three-point physical curve: ideal net -> post-placement -> post-route.

Why this tool exists
--------------------
The paper's acceptance criterion is evaluated on the IDEAL netlist (no
placement, no parasitics).  The label family measures the POST-ROUTE outcome.
In between there is a third physical stage that the family did not measure:
after placement and clock tree synthesis, before routing.  Without it, any
statement of the form "the ideal-net gain decays by X ns once physics is
applied" has to attribute the whole decay to routing -- but placement already
moves the cells and already changes the wire lengths, so part of the decay
belongs there.

What the three points are
-------------------------
  ideal     the paper's own number (pre-layout, no parasitics)
  placed    post-placement + post-CTS, parasitics estimated from the placement
            (OpenROAD `estimate_parasitics -placement`)
  routed    post-routing, parasitics estimated from the global routing topology
            (OpenROAD `estimate_parasitics -global_routing`)

  All three use the SAME netlist and the SAME frozen floorplan, so the
  differences belong to the netlist change and to the physical stage.

THE CAVEAT THAT TRAVELS WITH EVERY NUMBER HERE
  The placed and the routed stage use DIFFERENT parasitic ESTIMATION MODELS.
  "routed - placed" therefore mixes (a) the physical stage change (routing,
  router-driven cell movement, wire detours) with (b) the change of the
  parasitic model.  It is NOT a pure routing penalty and is not reported as one.

Resolution per stage
--------------------
A decision can only be confirmed at a stage if the measured difference at that
stage exceeds that stage's own implementation sensitivity.  The routed stage
has two bands (the noise-family band and the candidate-level band measured on
the same netlists under two realisations).  The PLACED stage gets its own
candidate-level band, measured the same way on the PLACED / PLACEDF1 runs --
the routed stage's band is a different quantity and must not be borrowed.

WHICH PLACED RUNS MAY BE USED (the trap this tool has to survive)
-----------------------------------------------------------------
The placed stage must measure the SAME NETLIST as the routed label.  That is
not automatic in this family:

  * s713's main-family netlists cannot be routed (constants without a real
    driver -> DRT-0305), so s713's ROUTED labels come from the tie-cell
    repaired batch S713R, while a placed batch launched from the main job
    table measures the UNREPAIRED netlists.  The repair is logic preserving,
    so nothing looks wrong -- and the placed stage does not route, so it
    succeeds on the broken netlist without any error.

The mapping is therefore NOT hard-coded here.  It is taken from
netlist_consistency.json, which tools/check_netlist_consistency.py derives by
comparing, per candidate, the netlist of the label's job table against every
placed-stage job table.  If that artefact is missing or reports a circuit with
no consistent placed table, this tool REFUSES to produce numbers.
"""
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

FAM = Path(__file__).resolve().parent.parent
REPO = FAM.parents[1]
NOISE = REPO / 'experiments/20261024_physical_transfer_noise'
LEDGER_FAM = REPO / 'experiments/20260826_iscas89_main'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_dataset import parse_log  # noqa: E402  (same directory)

F0_SIDE = ('F0', 'S713R')

# --- cumulative-reading fix (LOG-20261024-27) ---
def circuit_baseline_ideal_wns():
    """circuit -> ideal WNS of the CIRCUIT BASELINE netlist.

    The ledger's `acceptance_evidence.metric_references.setup_wns` is the
    ITERATION BASE netlist's ideal WNS, not the circuit baseline's.  For the
    iteration-1 trials the base netlist hash IS the circuit baseline netlist,
    so their reference value is the circuit-baseline ideal WNS.  A circuit that
    does not yield exactly one value is left out on purpose: a silent guess
    would corrupt the cumulative reading.
    """
    out = {}
    if not LEDGER_FAM.exists():
        return out
    for ckt_dir in sorted(p for p in LEDGER_FAM.iterdir() if p.is_dir()):
        p = ckt_dir / ckt_dir.name / 'eval_trials.json'
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        refs = set()
        for t in d.get('trials', []):
            if not isinstance(t, dict) or str(t.get('iteration')) != '1':
                continue
            mr = (t.get('acceptance_evidence') or {}).get('metric_references') or {}
            v = mr.get('setup_wns')
            if v is not None:
                refs.add(round(float(v), 6))
        if len(refs) == 1:
            out[ckt_dir.name] = refs.pop()
    return out

FAMILY = 'iscas89'

# placed-stage job table -> the run batch it was launched into
PLACED_BATCHES = {
    'jobs.tsv': 'PLACED',
    'jobs_f1.tsv': 'PLACEDF1',
    'jobs_s713_repaired.tsv': 'PLACEDS713',
    'jobs_f1_s713.tsv': 'PLACEDF1S713',
}


def sample_sd(v):
    if len(v) < 2:
        return None
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    ra, rb = rank(list(a)), rank(list(b))
    n = len(ra)
    if n < 3:
        return None
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def ols_slope(x, y):
    n = len(x)
    if n < 2:
        return None
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = sum((a - mx) ** 2 for a in x)
    return num / den if den else None


def read_table(path):
    if not path.exists():
        return {}
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    if not lines:
        return {}
    header = lines[0].split('\t')
    out = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) != len(header):
            continue
        row = dict(zip(header, parts))
        if row.get('key') == 'key':
            continue
        out[row['key']] = row
    return out


def load_batch_runs(batch):
    """key -> parsed record, for one run batch."""
    out = {}
    d = FAM / 'runs' / batch
    if not d.exists():
        return out
    for job in sorted(d.iterdir()):
        log = job / 'pr_run.log'
        if not log.exists():
            continue
        out[job.name] = parse_log(log)
    return out


def resolve_placed_sources():
    """circuit -> (f0_batch, f1_batch) for the post-placement stage.

    Derived from netlist_consistency.json, never hard-coded:
      * the F0-side table is the one the guard found consistent for that
        circuit AND whose realisation is F0;
      * the F1-side table is the one whose realisation is F1 AND whose netlist
        path for that circuit's keys equals the F0-side table's netlist path
        (an implementation pair must measure the same netlist).
    """
    cpath = FAM / 'netlist_consistency.json'
    if not cpath.exists():
        raise SystemExit('netlist_consistency.json missing -- run '
                         'tools/check_netlist_consistency.py first')
    cons = json.loads(cpath.read_text(encoding='utf-8'))
    if cons.get('verdict') != 'CONSISTENT':
        raise SystemExit(f"netlist consistency check says {cons.get('verdict')}: "
                         f"{cons.get('bad_circuits')} -- refusing to produce numbers")

    tables = {t: read_table(FAM / t) for t in PLACED_BATCHES}
    realisation = {}
    for t, rows in tables.items():
        vals = {r.get('realisation') for r in rows.values()}
        realisation[t] = sorted(v for v in vals if v)

    per_circuit = cons.get('per_circuit') or {}
    out = {}
    problems = []
    for ckt, info in sorted(per_circuit.items()):
        consistent = info.get('consistent_placed_tables') or []
        f0_tables = [t for t in consistent if 'F0' in realisation.get(t, [])]
        if not f0_tables:
            problems.append(f'{ckt}: no F0-realisation placed table is consistent')
            continue
        f0t = f0_tables[0]
        # the F1 side must hold the same keys with the same netlist
        f0_nets = {k: r.get('netlist') for k, r in tables[f0t].items()}
        best = None
        for t, rows in tables.items():
            if t == f0t or 'F1' not in realisation.get(t, []):
                continue
            hit = sum(1 for k, r in rows.items()
                      if f0_nets.get(k) is not None and r.get('netlist') == f0_nets[k])
            if hit and (best is None or hit > best[1]):
                best = (t, hit)
        if best is None:
            problems.append(f'{ckt}: no F1-realisation placed table with the same netlist')
            continue
        out[ckt] = {'f0_table': f0t, 'f0_batch': PLACED_BATCHES[f0t],
                    'f1_table': best[0], 'f1_batch': PLACED_BATCHES[best[0]],
                    'n_matching_f1_keys': best[1]}
    if problems:
        raise SystemExit('placed-stage source resolution failed: '
                         + '; '.join(problems))
    return out


def candidate_level_band(per_circuit_pairs, base_keys):
    """imp(x) = wns_B(x) - wns_A(x) over the candidate netlists, pooled within
    circuit (the systematic baseline offset is kept separate).

    per_circuit_pairs: circuit -> (a_by_key, b_by_key) for the F0 and the F1
    realisation of the post-placement stage.
    """
    per_ckt = defaultdict(list)
    n_pairs = 0
    for ckt, (a_by_key, b_by_key) in per_circuit_pairs.items():
        base = base_keys.get(ckt)
        for key, ra in a_by_key.items():
            rb = b_by_key.get(key)
            if rb is None or not ra.get('ok') or not rb.get('ok'):
                continue
            if ra.get('wns_max') is None or rb.get('wns_max') is None:
                continue
            if key == base:
                continue                      # the baseline offset is systematic
            imp = rb['wns_max'] - ra['wns_max']
            per_ckt[ckt].append(imp)
            n_pairs += 1
    num = df = 0
    for ckt, v in per_ckt.items():
        s = sample_sd(v)
        if s is not None:
            num += (len(v) - 1) * s * s
            df += len(v) - 1
    pooled = math.sqrt(num / df) if df else None
    ci = None
    if pooled is not None:
        rng = random.Random(20261024)
        boots = []
        for _ in range(2000):
            n2 = d2 = 0
            for ckt, v in per_ckt.items():
                if len(v) < 2:
                    continue
                samp = [v[rng.randrange(len(v))] for _ in v]
                s = sample_sd(samp)
                if s is not None:
                    n2 += (len(samp) - 1) * s * s
                    d2 += len(samp) - 1
            if d2:
                boots.append(math.sqrt(n2 / d2))
        boots.sort()
        ci = [round(boots[int(0.025 * len(boots))], 6),
              round(boots[int(0.975 * len(boots))], 6)]
    return {'pooled_within_circuit_sd_ns': round(pooled, 6) if pooled else None,
            'ci95': ci, 'df': df, 'n_candidate_netlists': n_pairs,
            'per_circuit': {c: {'n': len(v), 'sd': sample_sd(v)} for c, v in sorted(per_ckt.items())}}


def main():
    dpath = FAM / 'physical_dataset.jsonl'
    if not dpath.exists():
        raise SystemExit('physical_dataset.jsonl missing -- run tools/build_dataset.py first')
    rows = [json.loads(l) for l in dpath.read_text(encoding='utf-8').splitlines() if l.strip()]

    sources = resolve_placed_sources()

    # ---- per-circuit placed run tables --------------------------------------
    placed_by_ckt = {}
    placed_f1_by_ckt = {}
    for ckt, src in sources.items():
        placed_by_ckt[ckt] = load_batch_runs(src['f0_batch'])
        placed_f1_by_ckt[ckt] = load_batch_runs(src['f1_batch'])

    # key -> the placed run that belongs to that key's circuit
    placed = {}
    placed_f1 = {}
    for ckt in sources:
        placed.update(placed_by_ckt[ckt])
        placed_f1.update(placed_f1_by_ckt[ckt])

    # baseline key per circuit, from the F0-side dataset rows
    base_key = {}
    for r in rows:
        if r.get('batch') in F0_SIDE and r.get('kind') == 'BASE':
            base_key[r['circuit']] = r['key']

    # key -> F0-side dataset row (gives the iteration base key, i.e. the
    # netlist this candidate was derived from -- the MARGINAL reference)
    row_by_key = {}
    for r in rows:
        if r.get('batch') in F0_SIDE and r.get('kind') != 'BASE':
            row_by_key.setdefault(r['key'], r)

    def placed_wns(key):
        rec = placed.get(key)
        if rec and rec.get('ok') and rec.get('wns_max') is not None:
            return rec['wns_max']
        return None

    def placed_delta(cand_key, ref_key):
        a, b = placed_wns(cand_key), placed_wns(ref_key)
        if a is None or b is None:
            return None
        return round(a - b, 6)

    # ---- per-candidate three-point table --------------------------------------
    # MARGINAL and CUMULATIVE are kept apart: the marginal effect of ONE
    # substitution is measured against the netlist the candidate was derived
    # from, the cumulative effect against the circuit's baseline netlist.  The
    # two must never be compared against each other (an early version of this
    # tool compared the placed CUMULATIVE delta with the routed MARGINAL delta
    # and produced a meaningless attenuation).
    cb_ideal = circuit_baseline_ideal_wns()
    if not cb_ideal:
        raise SystemExit('circuit-baseline ideal WNS not derivable from the ledger'
                         ' -- refusing to produce a cumulative reading')

    cands = []
    dropped = {'other_batch': 0, 'post_failed': 0, 'missing_routed_label': 0}
    for r in rows:
        if r.get('batch') not in F0_SIDE:
            dropped['other_batch'] += 1
            continue
        if r.get('post_status') != 'ok':
            dropped['post_failed'] += 1
            continue
        if r.get('post_marginal_delta_wns') is None:
            # the ROUTED stage is the one that has to be a measurement; the
            # IDEAL stage may legitimately be absent (the candidate never
            # reached the ideal netlist STA), and such a candidate still
            # carries real placed/routed measurements, so it must not be
            # dropped here -- it used to be, silently, and its physical
            # stages were thrown away with it.
            dropped['missing_routed_label'] += 1
            continue
        ckt = r['circuit']
        iter_base = r.get('post_iter_base_key')
        cands.append({
            'circuit': ckt, 'key': r['key'], 'kind': r.get('kind'),
            'trial_index': r.get('trial_index'),
            'iter_base_key': iter_base,
            # None when the candidate never reached the ideal netlist STA;
            # the stage statistics are computed on the subset that carries
            # the stage, so an absent ideal reading contributes to nothing.
            'ideal_marginal': r.get('ideal_delta_wns'),
            'placed_marginal': placed_delta(r['key'], iter_base) if iter_base else None,
            'routed_marginal': r['post_marginal_delta_wns'],
            # CUMULATIVE = against the CIRCUIT BASELINE netlist.  The training
            # table's `ideal_baseline_wns` is the ITERATION base, so subtracting
            # it here would repeat the marginal reading under a wrong name.
            'ideal_cumulative': (round(r.get('ideal_wns') - cb_ideal[ckt], 6)
                                 if r.get('ideal_wns') is not None
                                 and ckt in cb_ideal else None),
            'ideal_label_status': r.get('ideal_label_status'),
            'placed_cumulative': placed_delta(r['key'], base_key.get(ckt, '')),
            'routed_cumulative': r.get('post_delta_wns'),
        })

    # ---- bands ----------------------------------------------------------------
    nm = json.loads((NOISE / 'noise_model.json').read_text(encoding='utf-8'))
    fam_block = (nm.get('per_family') or {}).get(FAMILY) or {}
    sigma_w = fam_block.get('sigma_within_ns')

    placed_band = candidate_level_band(
        {ckt: (placed_by_ckt[ckt], placed_f1_by_ckt[ckt]) for ckt in sources},
        base_key)

    routed_band = None
    cln_path = FAM / 'candidate_level_noise.json'
    if cln_path.exists():
        cln = json.loads(cln_path.read_text(encoding='utf-8'))
        routed_band = {
            'pooled_within_circuit_sd_ns': cln.get('pooled_within_circuit_sd_ns'),
            'ci95': cln.get('pooled_ci95'),
            'df': cln.get('pooled_df'),
            'n_candidate_netlists': cln.get('n_candidate_netlists'),
        }

    # ---- per-stage statistics -------------------------------------------------
    def stage_block(cands_, prefix):
        out = {}
        for stage in ('ideal', 'placed', 'routed'):
            key = f'{stage}_{prefix}'
            vals = [(c['ideal_' + prefix], c[key]) for c in cands_
                    if c.get(key) is not None and c.get('ideal_' + prefix) is not None]
            if not vals:
                continue
            xs = [a for a, _ in vals]
            ys = [b for _, b in vals]
            pos = sum(1 for y in ys if y > 0)
            agree = sum(1 for x, y in vals if (x > 0) == (y > 0))
            out[stage] = {
                'n': len(vals),
                'mean': round(sum(ys) / len(ys), 6),
                'median': round(sorted(ys)[len(ys) // 2], 6),
                'spearman_vs_ideal': round(spearman(xs, ys), 4) if stage != 'ideal' else 1.0,
                'sign_agreement_vs_ideal': f'{agree}/{len(vals)}',
                'n_positive': pos,
                'attenuation_slope_vs_ideal': round(ols_slope(xs, ys), 4),
            }
        both = [(c[f'placed_{prefix}'], c[f'routed_{prefix}']) for c in cands_
                if c.get(f'placed_{prefix}') is not None and c.get(f'routed_{prefix}') is not None]
        if both:
            out['placed_to_routed'] = {
                'n': len(both),
                'spearman': round(spearman([a for a, _ in both], [b for _, b in both]), 4),
                'slope_routed_on_placed': round(
                    ols_slope([a for a, _ in both], [b for _, b in both]), 4),
                'mean_placed': round(sum(a for a, _ in both) / len(both), 6),
                'mean_routed': round(sum(b for _, b in both) / len(both), 6),
            }
        return out

    stages = stage_block(cands, 'marginal')
    cumulative = stage_block(cands, 'cumulative')

    # ---- common-subset comparison --------------------------------------------
    # The three stages do not cover the same number of candidates (the placed
    # batch is a separate run batch), so comparing the per-stage correlations
    # as they stand would compare different candidate sets.  The fair
    # comparison is on the candidates that carry ALL THREE stages.
    common = [c for c in cands
              if c['ideal_marginal'] is not None
              and c['placed_marginal'] is not None
              and c['routed_marginal'] is not None]
    stages_common = stage_block(common, 'marginal') if common else {}

    # ---- acceptance decisions at each stage -----------------------------------
    cf_path = FAM / 'counterfactual_acceptance.jsonl'
    decisions = []
    if cf_path.exists():
        cfa = [json.loads(l) for l in cf_path.read_text(encoding='utf-8').splitlines() if l.strip()]
        for d in cfa:
            if d.get('post_status') != 'ok':
                continue
            ckt = d['circuit']
            key = d.get('post_key')
            src = row_by_key.get(key)
            iter_base = (src or {}).get('post_iter_base_key')
            decisions.append({
                'circuit': ckt, 'iteration': d.get('iteration'),
                'patch_id': d.get('patch_id'),
                'ideal_gain': d.get('ideal_gain'),
                'placed_delta': placed_delta(key, iter_base) if iter_base else None,
                'routed_delta': d.get('post_delta_wns'),
                'routed_verdict': d.get('post_verdict'),
            })

    def verdict(delta, two_sigma):
        if delta is None or two_sigma is None:
            return None
        if delta > two_sigma:
            return 'GAIN'
        if delta < -two_sigma:
            return 'REGRESSION'
        return 'INCONCLUSIVE'

    placed_two = (placed_band.get('pooled_within_circuit_sd_ns') or 0) * 2 \
        if placed_band.get('pooled_within_circuit_sd_ns') else None
    routed_two = (routed_band or {}).get('pooled_within_circuit_sd_ns')
    routed_two = routed_two * 2 if routed_two else None
    noise_two = sigma_w * 2 if sigma_w else None

    for d in decisions:
        d['placed_verdict_candlevel'] = verdict(d['placed_delta'], placed_two)
        d['routed_verdict_candlevel'] = verdict(d['routed_delta'], routed_two)
        d['routed_verdict_noisefamily'] = verdict(d['routed_delta'], noise_two)
        d['ideal_gain_below_placed_resolution'] = (
            abs(d['ideal_gain']) < placed_two if (d['ideal_gain'] is not None and placed_two) else None)
        d['ideal_gain_below_routed_resolution'] = (
            abs(d['ideal_gain']) < routed_two if (d['ideal_gain'] is not None and routed_two) else None)

    def count_verdicts(key):
        """Always report all three verdicts, so a stage with no regression
        prints 0 and not None -- a missing key reads like a missing measurement."""
        c = defaultdict(int)
        for d in decisions:
            v = d.get(key)
            if v:
                c[v] += 1
        return {v: c.get(v, 0) for v in ('GAIN', 'REGRESSION', 'INCONCLUSIVE')}

    out = {
        'measure_note': ('MARGINAL = the effect of ONE substitution, measured against '
                         'the netlist the candidate was derived from; CUMULATIVE = the '
                         'effect against the circuit baseline netlist.  The two are '
                         'never compared with each other.'),
        'ideal_cumulative_basis': {
            'note': ('the circuit-baseline ideal WNS per circuit, read from the '
                     'ledger as the reference of the iteration-1 trials (whose base '
                     'netlist hash IS the circuit baseline netlist); the cumulative '
                     'reading subtracts THIS, while the marginal reading subtracts '
                     'the iteration base'),
            'ledger_family': str(LEDGER_FAM.relative_to(REPO)),
            'n_circuits': len(cb_ideal),
            'circuit_baseline_ideal_wns': cb_ideal,
        },
        'placed_sources': sources,
        'placed_sources_note': ('derived from netlist_consistency.json: the placed '
                                'stage must measure the same netlist as the routed '
                                'label, and s713\'s routed labels come from the '
                                'tie-cell repaired batch'),
        'stages_marginal': stages,
        'stages_cumulative': cumulative,
        'stages_marginal_common_subset': stages_common,
        'common_subset_n': len(common),
        'common_subset_note': ('the three stages may cover different candidate sets '
                               '(the placed stage is a separate run batch), so the '
                               'stage-to-stage comparison is made on the candidates '
                               'that carry all three stages'),
        'bands': {
            'noise_family_sigma_w_ns': sigma_w,
            'noise_family_two_sigma_ns': round(noise_two, 6) if noise_two else None,
            'routed_candidate_level': routed_band,
            'routed_candidate_level_two_sigma_ns': round(routed_two, 6) if routed_two else None,
            'placed_candidate_level': placed_band,
            'placed_candidate_level_two_sigma_ns': round(placed_two, 6) if placed_two else None,
        },
        'coverage': {
            'labelled_candidates_total': len(cands),
            'with_placed_marginal': sum(1 for c in cands if c['placed_marginal'] is not None),
            'with_routed_marginal': sum(1 for c in cands if c['routed_marginal'] is not None),
            'placed_runs_parsed': sum(1 for v in placed.values() if v.get('ok')),
            'placed_runs_total': len(placed),
            'placed_f1_runs_parsed': sum(1 for v in placed_f1.values() if v.get('ok')),
            'placed_f1_runs_total': len(placed_f1),
            'decisions_labelled': len(decisions),
            'decisions_with_placed': sum(1 for d in decisions if d['placed_delta'] is not None),
        },
        'verdict_counts': {
            'placed_candidate_level': count_verdicts('placed_verdict_candlevel'),
            'routed_candidate_level': count_verdicts('routed_verdict_candlevel'),
            'routed_noise_family': count_verdicts('routed_verdict_noisefamily'),
        },
        'decisions': decisions,
        'candidates': cands,
        'caveat': ('the placed stage uses the placement parasitic model and the routed '
                   'stage the global-routing model, so "routed - placed" mixes the '
                   'physical stage change with the change of the estimation model; '
                   'it is not a pure routing penalty.'),
    }
    (FAM / 'three_point_curve.json').write_text(
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

    print('=== placed sources (derived from the netlist consistency guard) ===')
    for ckt, src in sorted(sources.items()):
        print(f"  {ckt:<6} F0: {src['f0_batch']:<14} F1: {src['f1_batch']:<14} "
              f"f1_keys={src['n_matching_f1_keys']}")
    print()
    print('=== three-point curve (marginal) ===')
    for s in ('ideal', 'placed', 'routed'):
        if s in stages:
            v = stages[s]
            print(f"  {s:<7} n={v['n']:<4} mean={v['mean']:+.4f}  "
                  f"rho(ideal)={v['spearman_vs_ideal']}  "
                  f"slope(ideal)={v['attenuation_slope_vs_ideal']}  "
                  f"sign={v['sign_agreement_vs_ideal']}")
    if 'placed_to_routed' in stages:
        v = stages['placed_to_routed']
        print(f"  placed->routed  n={v['n']}  rho={v['spearman']}  "
              f"slope(routed|placed)={v['slope_routed_on_placed']}  "
              f"mean {v['mean_placed']:+.4f} -> {v['mean_routed']:+.4f}")
    print('=== three-point curve (cumulative) ===')
    for s in ('ideal', 'placed', 'routed'):
        if s in cumulative:
            v = cumulative[s]
            print(f"  {s:<7} n={v['n']:<4} mean={v['mean']:+.4f}  "
                  f"rho(ideal)={v['spearman_vs_ideal']}  "
                  f"slope(ideal)={v['attenuation_slope_vs_ideal']}")
    if stages_common:
        print(f'=== three-point curve (marginal, common subset n={len(common)}) ===')
        for s in ('ideal', 'placed', 'routed'):
            v = stages_common.get(s)
            if v:
                print(f"  {s:<7} n={v['n']:<4} mean={v['mean']:+.4f}  "
                      f"rho(ideal)={v['spearman_vs_ideal']}  "
                      f"slope(ideal)={v['attenuation_slope_vs_ideal']}  "
                      f"sign={v['sign_agreement_vs_ideal']}")
        p2r = stages_common.get('placed_to_routed')
        if p2r:
            print(f"  placed->routed  n={p2r['n']}  rho={p2r['spearman']}  "
                  f"slope(routed|placed)={p2r['slope_routed_on_placed']}  "
                  f"mean {p2r['mean_placed']:+.4f} -> {p2r['mean_routed']:+.4f}")
    print()
    print('  noise-family 2sigma    =', out['bands']['noise_family_two_sigma_ns'])
    print('  routed candidate-level  =', out['bands']['routed_candidate_level_two_sigma_ns'])
    print('  placed candidate-level  =', out['bands']['placed_candidate_level_two_sigma_ns'])
    print()
    print('  coverage:', json.dumps(out['coverage'], ensure_ascii=False))
    print('  verdict counts:', json.dumps(out['verdict_counts'], ensure_ascii=False))
    print(f'\nwrote {FAM / "three_point_curve.json"}')


if __name__ == '__main__':
    main()
