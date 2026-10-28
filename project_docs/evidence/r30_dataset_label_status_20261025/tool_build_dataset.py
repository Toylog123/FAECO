"""Build dataset v1: candidate-level physical labels.

Joins three sources:
  1. the FAECO candidate ledger (ideal-net labels, per trial),
  2. the post-route OpenROAD runs of this family (post-route labels, per
     netlist), and
  3. the noise-floor model of experiments/20261024_physical_transfer_noise
     (noise_model.json: the resolution below which a post-route difference
     cannot be told apart from a change of physical implementation).

Runs are identified by (batch, key): the F0 batch (candidates), the F1 batch
(cross-check realisation) and the FINAL batch (the committed netlist of the
multi-round run) all use the same job keys for their baselines, so keying on
the job name alone would let one batch overwrite another's baseline.

Output
------
  physical_dataset.jsonl   one record per (batch, candidate)
  physical_dataset.tsv     the same records, flat
  dataset_v1_summary.json  counts, thresholds, provenance

Label semantics
---------------
  ideal_delta_wns     = candidate setup_wns - baseline setup_wns   (ideal net)
  physical_delta_wns  = candidate post-route WNS - baseline post-route WNS
  noise_flag          = |physical_delta_wns| > noise_threshold * sigma,
                        where sigma is the pooled implementation sensitivity
                        of the paired difference (same circuit, different
                        physical realisation) measured by the noise family.
                        A candidate whose physical gain is inside the noise
                        band cannot be called an improvement on post-route
                        evidence, no matter what the ideal netlist said.

The post-route baseline of a circuit is the frozen floorplan run of that
circuit's baseline netlist, so every candidate is compared on exactly the same
die, the same pin policy and the same routing stack.
"""
import json
import os
import re
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

FAM = Path(__file__).resolve().parent.parent
REPO = FAM.parents[1]
NOISE = REPO / 'experiments/20261024_physical_transfer_noise'
LEDGER_FAM = REPO / 'experiments/20260826_iscas89_main'
sys.path.insert(0, str(FAM / 'tools'))
try:
    from repair_tie_cells import repair_tie_cells  # noqa: E402
except Exception:                                   # pragma: no cover
    repair_tie_cells = None

NOISE_SIGMA_MULT = 2.0

# job TSV -> batch name
BATCHES = {
    'jobs.tsv': 'F0',
    'jobs_f1.tsv': 'F1',
    'jobs_final.tsv': 'final',
    # s713's main-family netlists cannot be routed (constants without a real
    # driver -> DRT-0305), so its labels come from the tie-cell repaired batch.
    'jobs_s713_repaired.tsv': 'S713R',
    # the F1 rows for s713 pointed at the unrepaired netlists and all failed
    # with DRT-0305, so s713 had no cross-implementation pair at all; this
    # batch is the same F1 rows with the repaired netlists.
    'jobs_f1_s713.tsv': 'F1S713',
}
# the batch whose baselines are the reference for the main dataset
PRIMARY_BATCH = 'F0'

RE_DIE = re.compile(r'Die area:\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)')
RE_VER = re.compile(r'OpenROAD (v[^\s]+)')


def load_jobs():
    """(batch, key) -> row"""
    rows = {}
    for fname, batch in BATCHES.items():
        path = FAM / fname
        if not path.exists():
            continue
        lines = path.read_text(encoding='utf-8').splitlines()
        header = lines[0].split('\t')
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) != len(header):
                continue
            row = dict(zip(header, parts))
            if row['key'] == 'key':
                continue
            rows[(batch, row['key'])] = row
    return rows


def parse_log(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    rec = {'ok': False, 'tns': None, 'wns_max': None, 'wns_min': None,
           'error': None, 'openroad_version': None}
    m = RE_VER.search(text)
    if m:
        rec['openroad_version'] = m.group(1)
    if 'TNS_BEGIN' in text:
        lines = [ln.strip() for ln in text.split('TNS_BEGIN', 1)[1].splitlines() if ln.strip()]
        if lines:
            m2 = re.match(r'^tns\s+(-?[\d.]+)$', lines[0])
            if m2:
                rec['tns'] = float(m2.group(1))
        vals = [float(ln.replace('worst slack', '').strip())
                for ln in lines if ln.startswith('worst slack')]
        if len(vals) >= 2:
            rec['wns_max'], rec['wns_min'] = vals[0], vals[1]
    if rec['tns'] is None or rec['wns_max'] is None:
        errs = [ln for ln in text.splitlines()
                if ln.startswith('[ERROR') or ln.startswith('Error:')]
        rec['error'] = errs[-1] if errs else 'no TNS_BEGIN marker'
    else:
        rec['ok'] = True
    return rec


def load_ledger():
    """(circuit, trial_index) -> trial dict"""
    out = {}
    if not LEDGER_FAM.exists():
        return out
    for ckt in sorted(os.listdir(LEDGER_FAM)):
        p = LEDGER_FAM / ckt / ckt / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        for idx, t in enumerate(d.get('trials', [])):
            if isinstance(t, dict):
                out[(ckt, idx)] = t
    return out


def build_repair_alias(ledger):
    """pre-repair netlist hash -> post-repair netlist hash.

    s713's labels are produced from the tie-cell REPAIRED netlists, so their
    content hash differs from the ledger's hash of the original netlist text.
    The ledger's ``base_netlist_hash`` (used to find the netlist a candidate
    was built from) refers to the ORIGINAL text, so without this alias the
    iteration base of every s713 candidate would fail to resolve and all
    marginal deltas would come out empty.
    """
    alias = {}
    if repair_tie_cells is None:
        return alias
    for (_ckt, _idx), t in ledger.items():
        text = t.get('candidate_netlist_text')
        if not text:
            continue
        pre = hashlib.sha256(text.encode('utf-8')).hexdigest()
        fixed, _ = repair_tie_cells(text)
        post = hashlib.sha256(fixed.encode('utf-8')).hexdigest()
        if pre != post:
            alias[pre] = post
    return alias


def load_noise():
    """Canonical noise model: per-circuit shrunk sigma + the global floor.

    Source: experiments/20261024_physical_transfer_noise/noise_model.json
    (see that script for why the between-circuit spread is signal, not noise).
    """
    path = NOISE / 'noise_model.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    per = {}
    nreal = {}
    famof = {}
    for s in data.get('per_circuit', []):
        sigma = s.get('sigma_shrunk')
        if sigma is not None:
            per[s['circuit']] = sigma
        nreal[s['circuit']] = s.get('n_realisations')
        famof[s['circuit']] = s.get('family')
    pf = data.get('per_family') or {}
    return {'per_circuit': per,
            'n_realisations': nreal,
            'family_of': famof,
            'pooled_sd': data.get('noise_floor_ns'),
            'pooled_ci95': data.get('noise_floor_ci95'),
            'per_family': pf,
            'family_sigma': (pf.get('iscas89') or {}).get('sigma_within_ns'),
            'family_ci95': (pf.get('iscas89') or {}).get('ci95'),
            'model': data.get('model'),
            'source': str(path.relative_to(REPO))}


def load_candidate_noise():
    """Candidate-level implementation sensitivity, measured directly on the
    candidate netlists (F0 vs F1).

    This is a DIFFERENT quantity from the noise family's sigma_w: sigma_w is
    the implementation sensitivity of a full ECO round, while this is the
    spread of the per-netlist implementation effect over a circuit's candidate
    netlists -- the part that bounds a candidate-level verdict.  See
    tools/candidate_level_noise.py for the decomposition into a per-circuit
    systematic offset and a per-candidate random part.
    """
    path = FAM / 'candidate_level_noise.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    per = {}
    offset = {}
    for ckt, d in (data.get('per_circuit') or {}).items():
        per[ckt] = d.get('sigma_shrunk') or d.get('sd_imp_candidates')
        offset[ckt] = d.get('systematic_offset_ns')
    return {'per_circuit': per,
            'systematic_offset': offset,
            'pooled_sd': data.get('pooled_within_circuit_sd_ns'),
            'pooled_ci95': data.get('pooled_ci95'),
            'noise_family_sigma_w': data.get('noise_family_sigma_w_ns'),
            'source': str(path.relative_to(REPO))}


# round 34: how the ideal-netlist stage of every row was obtained (see the patch note)
LABEL_COVERAGE = {
    'measured': 0,
    'not_measured_pre_sta': 0,
}

def main():
    jobs = load_jobs()
    ledger = load_ledger()
    noise = load_noise()
    candnoise = load_candidate_noise()
    repair_alias = build_repair_alias(ledger)

    # results keyed by (batch, key)
    results = {}
    runs_dir = FAM / 'runs'
    if runs_dir.exists():
        for batch in sorted(runs_dir.iterdir()):
            if not batch.is_dir():
                continue
            for job in sorted(batch.iterdir()):
                log = job / 'pr_run.log'
                if not log.exists():
                    continue
                rc = None
                seconds = None
                rcfile = job / 'rc.tsv'
                if rcfile.exists():
                    parts = rcfile.read_text(encoding='utf-8').strip().split('\t')
                    if len(parts) >= 3:
                        rc, seconds = int(parts[1]), int(parts[2])
                rec = parse_log(log)
                rec['rc'] = rc
                rec['seconds'] = seconds
                rec['batch'] = batch.name
                results[(batch.name, job.name)] = rec

    # the post-route baseline per circuit, from the primary batch
    baselines = {}
    for (batch, key), row in jobs.items():
        if row.get('kind') != 'BASE':
            continue
        rec = results.get((batch, key))
        if rec and rec.get('ok'):
            baselines.setdefault(row['circuit'], {})[batch] = {
                'wns': rec['wns_max'], 'tns': rec['tns'],
                'min_slack': rec['wns_min'], 'key': key, 'batch': batch,
                # the physical realisation of THIS baseline run; a candidate may
                # only be compared against a baseline of the same realisation
                'realisation': row.get('realisation')}

    # post-route WNS indexed by netlist hash, so that a candidate can be
    # compared against the netlist it was actually built from (its iteration
    # base).  The iteration base is either the circuit baseline or an earlier
    # accepted candidate, both of which are labelled here.
    #
    # Two hash flavours occur: the ledger hashes the netlist TEXT (LF), while
    # the baseline netlist on disk still has CRLF line endings, so its file
    # hash differs from the ledger's text hash.  Both are registered.
    # post-route WNS indexed by (batch, netlist hash), so that a candidate can
    # be compared against the netlist it was actually built from (its iteration
    # base) WITHOUT mixing physical realisations.
    #
    # The index is batch-aware on purpose: the F1 batch re-routes a subset of
    # the same netlists under a second realisation.  A shared index would let
    # F0's run of a netlist become the "iteration base" of an F1 candidate,
    # i.e. a marginal delta across two different physical implementations.
    #
    # Two hash flavours occur: the ledger hashes the netlist TEXT (LF), while
    # the baseline netlist on disk still has CRLF line endings, so its file
    # hash differs from the ledger's text hash.  Both are registered.
    post_by_hash = {}
    for (batch, key), row in jobs.items():
        rec = results.get((batch, key))
        if not (rec and rec.get('ok')):
            continue
        entry = {'wns': rec['wns_max'], 'tns': rec['tns'],
                 'min_slack': rec['wns_min'], 'key': key, 'batch': batch}
        if row.get('candidate_hash'):
            post_by_hash.setdefault((batch, row['candidate_hash']), entry)
        net = REPO / row['netlist']
        if net.exists():
            try:
                th = hashlib.sha256(
                    net.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
                post_by_hash.setdefault((batch, th), entry)
            except Exception:
                pass
    # register the PRE-repair hash of every repaired netlist as well, so the
    # ledger's original hashes resolve to the routed run (same batch only)
    if repair_alias:
        inv = {v: k for k, v in repair_alias.items()}
        for (batch, h), entry in list(post_by_hash.items()):
            if h in inv:
                post_by_hash.setdefault((batch, inv[h]), entry)

    records = []
    for (batch, key), row in sorted(jobs.items()):
        ckt = row['circuit']
        kind = row.get('kind')
        rec = results.get((batch, key), {'ok': False, 'rc': None, 'error': 'not run'})
        tidx = int(row['trial_index'])
        trial = ledger.get((ckt, tidx), {}) if tidx >= 0 else {}
        ev = trial.get('acceptance_evidence') or {}
        refs = ev.get('metric_references') or {}
        ideal_cand = ev.get('setup_wns')
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
        base = (baselines.get(ckt) or {}).get(batch)
        base_batch = batch
        if base is None:
            # batches without their own baseline job (e.g. the FINAL batch,
            # which only contains the committed netlist) fall back to the
            # primary batch's baseline -- the die and the flow are identical.
            # GUARD: the fallback baseline must carry the SAME physical
            # realisation as the candidate, otherwise the "cumulative gain"
            # would mix two implementations.
            cand = (baselines.get(ckt) or {}).get(PRIMARY_BATCH)
            if cand and cand.get('realisation') == row.get('realisation'):
                base = cand
                base_batch = PRIMARY_BATCH
        if base is not None and base.get('realisation') != row.get('realisation'):
            # any other baseline of the same realisation
            for fb, cand in sorted((baselines.get(ckt) or {}).items()):
                if cand.get('realisation') == row.get('realisation'):
                    base = cand
                    base_batch = fb
                    break
        # the netlist this candidate was built from -- SAME batch only, so the
        # marginal delta never mixes two physical realisations
        iter_base_hash = trial.get('base_netlist_hash')
        iter_base = post_by_hash.get((batch, iter_base_hash)) if iter_base_hash else None
        out = {
            'batch': batch, 'key': key, 'circuit': ckt, 'trial_index': tidx,
            'kind': kind, 'iteration': row.get('iteration'),
            'accepted_ideal': row.get('accepted'),
            'netlist_sha256': row.get('candidate_hash'),
            'base_netlist_sha256': iter_base_hash,
            'instance': trial.get('instance'),
            'from_type': trial.get('from_type'), 'to_type': trial.get('to_type'),
            'ideal_wns': ideal_cand, 'ideal_baseline_wns': ideal_base,
            'ideal_delta_wns': ideal_delta,
            'ideal_label_status': ideal_label_status,
            'ideal_wns_placeholder': ideal_placeholder,
            'ideal_tns': trial.get('tns'), 'ideal_min_slack': trial.get('min_slack'),
            'rc': rec.get('rc'), 'seconds': rec.get('seconds'),
            'post_status': 'ok' if rec.get('ok') else 'failed',
            'post_error': rec.get('error'),
            'post_wns': rec.get('wns_max'), 'post_tns': rec.get('tns'),
            'post_min_slack': rec.get('wns_min'),
            'post_base_wns': base['wns'] if base else None,
            'post_base_tns': base['tns'] if base else None,
            'post_base_min_slack': base['min_slack'] if base else None,
            'post_base_batch': base_batch,
            'post_base_realisation': (base.get('realisation') if base else None),
            # gain against the circuit's original baseline (cumulative)
            'post_delta_wns': None, 'post_delta_tns': None,
            # gain against the netlist this candidate was built from (marginal)
            'post_iter_base_wns': iter_base['wns'] if iter_base else None,
            'post_iter_base_key': iter_base['key'] if iter_base else None,
            'post_marginal_delta_wns': None, 'post_marginal_delta_tns': None,
            'openroad_version': rec.get('openroad_version'),
            'realisation': row.get('realisation'),
            'die_area': row.get('die_area'), 'core_area': row.get('core_area'),
            'noise_sigma': None, 'noise_threshold': None, 'above_noise': None,
            'noise_n_realisations': None, 'noise_sigma_global': None,
            'noise_family': None, 'noise_family_sigma': None,
            # candidate-level band, measured directly on the candidate netlists
            'cand_sigma': None, 'cand_threshold': None,
            'above_noise_candlevel': None, 'impl_offset_ns': None,
        }
        if base and rec.get('ok'):
            out['post_delta_wns'] = round(rec['wns_max'] - base['wns'], 6)
            out['post_delta_tns'] = round(rec['tns'] - base['tns'], 6)
        if iter_base and rec.get('ok'):
            out['post_marginal_delta_wns'] = round(rec['wns_max'] - iter_base['wns'], 6)
            out['post_marginal_delta_tns'] = round(rec['tns'] - iter_base['tns'], 6)
        # the acceptance question is about the MARGINAL effect, so the noise
        # band is applied to the marginal delta
        if noise:
            sigma = noise['per_circuit'].get(ckt, noise.get('pooled_sd'))
            if sigma is not None and out['post_marginal_delta_wns'] is not None:
                out['noise_sigma'] = sigma
                out['noise_sigma_global'] = noise.get('pooled_sd')
                out['noise_n_realisations'] = noise.get('n_realisations', {}).get(ckt)
                out['noise_family'] = noise.get('family_of', {}).get(ckt)
                out['noise_family_sigma'] = noise.get('family_sigma')
                out['noise_threshold'] = round(NOISE_SIGMA_MULT * sigma, 6)
                out['above_noise'] = bool(abs(out['post_marginal_delta_wns']) > out['noise_threshold'])
        # the candidate-level band: the spread of the per-netlist implementation
        # effect over this circuit's candidate netlists.  It bounds a
        # candidate-level verdict directly, while the noise-family band is
        # inherited from full ECO rounds.  Both are reported.
        if candnoise:
            cs = candnoise['per_circuit'].get(ckt, candnoise.get('pooled_sd'))
            out['impl_offset_ns'] = candnoise['systematic_offset'].get(ckt)
            if cs is not None and out['post_marginal_delta_wns'] is not None:
                out['cand_sigma'] = cs
                out['cand_threshold'] = round(NOISE_SIGMA_MULT * cs, 6)
                out['above_noise_candlevel'] = bool(
                    abs(out['post_marginal_delta_wns']) > out['cand_threshold'])
        records.append(out)

    with (FAM / 'physical_dataset.jsonl').open('w', encoding='utf-8', newline='\n') as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')

    cols = ['batch', 'key', 'circuit', 'trial_index', 'kind', 'iteration',
            'accepted_ideal', 'netlist_sha256', 'instance', 'from_type', 'to_type',
            'ideal_wns', 'ideal_baseline_wns', 'ideal_delta_wns',
            'post_wns', 'post_base_wns', 'post_delta_wns',
            'post_tns', 'post_base_tns', 'post_delta_tns',
            'post_status', 'rc', 'above_noise', 'noise_sigma', 'noise_threshold',
            'above_noise_candlevel', 'cand_sigma', 'cand_threshold', 'impl_offset_ns',
            'noise_family', 'noise_family_sigma']
    with (FAM / 'physical_dataset.tsv').open('w', encoding='utf-8', newline='\n') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in records:
            fh.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')

    def block(batch):
        rs = [r for r in records if r['batch'] == batch]
        ok = [r for r in rs if r['post_status'] == 'ok']
        not_run = [r for r in rs if r.get('rc') is None and r.get('post_status') != 'ok']
        failed = [r for r in rs if r.get('rc') is not None and r.get('post_status') != 'ok']
        cum = [r for r in ok if r['post_delta_wns'] is not None]
        marg = [r for r in ok if r['post_marginal_delta_wns'] is not None]
        signed = [r for r in marg if r['ideal_delta_wns'] is not None]
        flips = [r for r in signed if r['ideal_delta_wns'] > 0 and r['post_marginal_delta_wns'] <= 0]
        above = [r for r in marg if r['above_noise']]
        return {
            'n_records': len(rs),
            'n_post_ok': len(ok),
            'n_failed': len(failed),
            'n_not_run': len(not_run),
            'n_with_marginal_delta': len(marg),
            'n_with_ideal_label': len(signed),
            'n_ideal_gain': sum(1 for r in signed if r['ideal_delta_wns'] > 0),
            'n_ideal_gain_but_post_not_gain': len(flips),
            'n_post_above_noise': len(above),
            'mean_marginal_delta_wns': (round(sum(r['post_marginal_delta_wns'] for r in marg) / len(marg), 6)
                                        if marg else None),
            'mean_ideal_delta_wns': (round(sum(r['ideal_delta_wns'] for r in signed) / len(signed), 6)
                                     if signed else None),
            'mean_cumulative_delta_wns': (round(sum(r['post_delta_wns'] for r in cum) / len(cum), 6)
                                          if cum else None),
        }

    summary = {
        'noise_sigma_multiplier': NOISE_SIGMA_MULT,
        'noise_source': noise.get('source') if noise else None,
        'noise_model': noise.get('model') if noise else None,
        'noise_pooled_sd': noise.get('pooled_sd') if noise else None,
        'noise_pooled_ci95': noise.get('pooled_ci95') if noise else None,
        'noise_per_circuit': noise.get('per_circuit') if noise else None,
        'noise_per_family': noise.get('per_family') if noise else None,
        'noise_family_sigma_used': noise.get('family_sigma') if noise else None,
        'noise_family_ci95_used': noise.get('family_ci95') if noise else None,
        'noise_n_realisations': noise.get('n_realisations') if noise else None,
        'cand_level_noise_source': candnoise.get('source') if candnoise else None,
        'cand_level_pooled_sd': candnoise.get('pooled_sd') if candnoise else None,
        'cand_level_pooled_ci95': candnoise.get('pooled_ci95') if candnoise else None,
        'cand_level_per_circuit': candnoise.get('per_circuit') if candnoise else None,
        'impl_offset_per_circuit': candnoise.get('systematic_offset') if candnoise else None,
        'ideal_label_coverage': dict(LABEL_COVERAGE),
        'ideal_label_coverage_note': ('the ideal-netlist stage of a candidate '
                                      'is only a MEASUREMENT when the ECO loop '
                                      'produced an acceptance decision for it.  '
                                      'A candidate that failed a pre-STA hard '
                                      'gate (equivalence / boundary) never '
                                      'reached the ideal netlist STA: the '
                                      'ledger carries no acceptance_evidence '
                                      'for it and its `wns` field is the '
                                      'ITERATION BASE\'s value (exactly equal '
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
        'batches_loaded': sorted({b for (b, _k) in jobs}),
        'n_repair_hash_aliases': len(repair_alias),
        'baselines_found': {k: sorted(v) for k, v in baselines.items()},
        'source_ledger_family': str(LEDGER_FAM.relative_to(REPO)),
        'by_batch': {b: block(b) for b in sorted({r['batch'] for r in records})},
    }
    (FAM / 'dataset_v1_summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
