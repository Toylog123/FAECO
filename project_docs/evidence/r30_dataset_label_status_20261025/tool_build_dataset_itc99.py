"""Build the ITC-99 candidate-level post-route label dataset.

The ITC-99 sibling of experiments/20261024_physical_labels/tools/build_dataset.py.
Same joins, same conventions, same noise source; only the source family and the
circuits differ.

  * ledger     : experiments/20260826_itc99_main/<ckt>/<ckt>/eval_trials.json
  * post-route : runs/<batch>/<key>/pr_run.log of THIS family
  * noise      : experiments/20261024_physical_transfer_noise/noise_model.json
                 (the b circuits are part of the noise family, so the same
                 per-circuit sigma applies)

No tie-cell repair is needed here: the b circuits route without the DRT-0305
defect that s713 has (the noise family routed all of them successfully).

Output
------
physical_dataset.jsonl / .tsv   one record per (batch, candidate)
dataset_summary.json             counts per batch and circuit
"""
import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path

FAM = Path(__file__).resolve().parent.parent
REPO = FAM.parents[1]
LEDGER_FAM = REPO / 'experiments/20260826_itc99_main'
NOISE = REPO / 'experiments/20261024_physical_transfer_noise'

NOISE_SIGMA_MULT = 2.0

# job TSV -> batch name
BATCHES = {
    'jobs_itc99_p0.tsv': 'I0P0',
    'jobs_itc99.tsv': 'I0',
    'jobs_itc99_f1_p0.tsv': 'I1P0',
    'jobs_itc99_f1.tsv': 'I1',
}
PRIMARY_BATCH = 'I0P0'

RE_DIE = re.compile(r'Die area:\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)')
RE_VER = re.compile(r'OpenROAD (v[^\s]+)')
RE_WNS = re.compile(r'worst slack\s+(-?[\d.]+)')
RE_TNS = re.compile(r'^tns\s+(-?[\d.]+)\s*$', re.M)


def load_jobs():
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


def load_ledger():
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


def parse_log(path):
    """-> {'ok', 'wns_max', 'wns_min', 'tns', 'error', 'openroad_version'}

    OpenROAD's report_worst_slack prints two UNLABELLED "worst slack" lines
    (setup max, then hold min); the FIRST one is the setup WNS.  The TNS is
    read from the report_tns block delimited by the TNS_BEGIN/TNS_END markers.
    """
    text = path.read_text(encoding='utf-8', errors='replace')
    rec = {'ok': False, 'wns_max': None, 'wns_min': None, 'tns': None,
           'error': None, 'openroad_version': None}
    m = RE_VER.search(text)
    if m:
        rec['openroad_version'] = m.group(1)
    if 'TNS_BEGIN' in text:
        blk = text.split('TNS_BEGIN', 1)[1]
        blk = blk.split('TNS_END', 1)[0]
        tns = RE_TNS.search(blk)
        if tns:
            rec['tns'] = float(tns.group(1))
    slacks = RE_WNS.findall(text)
    if len(slacks) >= 2:
        rec['wns_max'] = float(slacks[0])
        rec['wns_min'] = float(slacks[1])
        rec['ok'] = True
    else:
        errs = re.findall(r'^\[ERROR [^\]]+\].*$', text, re.M)
        rec['error'] = errs[-1] if errs else 'no worst-slack pair'
    return rec


def load_noise():
    path = NOISE / 'noise_model.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    per, nreal, fam = {}, {}, {}
    for s in data.get('per_circuit', []):
        per[s['circuit']] = s.get('sigma_shrunk')
        nreal[s['circuit']] = s.get('n_realisations')
        fam[s['circuit']] = s.get('family')
    pf = data.get('per_family') or {}
    return {'per_circuit': per, 'n_realisations': nreal, 'family_of': fam,
            'pooled_sd': data.get('noise_floor_ns'),
            'pooled_ci95': data.get('noise_floor_ci95'),
            'per_family': pf,
            'family_sigma': (pf.get('itc99') or {}).get('sigma_within_ns'),
            'family_ci95': (pf.get('itc99') or {}).get('ci95'),
            'source': str(path.relative_to(REPO))}


def load_candidate_noise():
    """Candidate-level implementation sensitivity measured ON THE ITC-99
    CIRCUITS (batch I0P0 vs I1P0, the same netlists under two realisations).

    This is the ITC-99 family's own band.  The ISCAS89 band does NOT transfer:
    the noise model shows the two families have materially different
    implementation sensitivity (ITC-99 pooled sigma_w is ~1.38x the ISCAS89
    one), so the band must be measured where it is used.
    """
    path = FAM / 'candidate_level_noise.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    per, offset = {}, {}
    for ckt, d in (data.get('per_circuit') or {}).items():
        per[ckt] = d.get('sigma_shrunk') or d.get('sd_imp_candidates')
        offset[ckt] = d.get('systematic_offset_ns')
    return {'per_circuit': per,
            'systematic_offset': offset,
            'pooled_sd': data.get('pooled_within_circuit_sd_ns'),
            'pooled_ci95': data.get('pooled_ci95'),
            'noise_family_sigma_w': data.get('noise_family_sigma_w_ns'),
            'source': str(path.relative_to(REPO))}


def sha256_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


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
                rec = parse_log(log)
                rc = None
                rcf = job / 'rc.tsv'
                if rcf.exists():
                    parts = rcf.read_text(encoding='utf-8').strip().split('\t')
                    if len(parts) > 1:
                        try:
                            rc = int(parts[1])
                        except ValueError:
                            rc = parts[1]
                rec['rc'] = rc
                if not rec['ok']:
                    rec['ok'] = False
                results[(batch.name, job.name)] = rec

    # baselines per (batch, circuit)
    baselines = defaultdict(dict)
    for (batch, key), row in jobs.items():
        rec = results.get((batch, key))
        if not (rec and rec.get('ok')):
            continue
        if row.get('kind') == 'BASE':
            baselines[row['circuit']][batch] = {
                'wns': rec['wns_max'], 'tns': rec['tns'],
                'min_slack': rec['wns_min'], 'key': key, 'batch': batch,
                # the physical realisation of THIS baseline run.  A candidate may
                # only be compared against a baseline of the same realisation:
                # pairing an F1 candidate with the F0 baseline would mix two
                # implementations into one "cumulative gain".
                'realisation': row.get('realisation')}

    # post-route WNS indexed by (batch, hash) -- never across batches, so a
    # candidate is never compared against another implementation's run
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
                th = hashlib.sha256(net.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
                post_by_hash.setdefault((batch, th), entry)
            except Exception:
                pass

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
        base = baselines.get(ckt, {}).get(batch)
        base_batch = batch
        if base is None:
            # fall back to the primary batch's baseline ONLY if it is the SAME
            # physical realisation; otherwise the candidate would be compared
            # against another implementation's baseline
            for fb in (PRIMARY_BATCH,):
                cand = baselines.get(ckt, {}).get(fb)
                if cand and cand.get('realisation') == row.get('realisation'):
                    base, base_batch = cand, fb
                    break
        if base is not None and base.get('realisation') != row.get('realisation'):
            # last resort: any baseline of the same realisation
            for fb, cand in sorted(baselines.get(ckt, {}).items()):
                if cand.get('realisation') == row.get('realisation'):
                    base, base_batch = cand, fb
                    break
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
            'post_delta_wns': None, 'post_delta_tns': None,
            'post_iter_base_wns': iter_base['wns'] if iter_base else None,
            'post_iter_base_key': iter_base['key'] if iter_base else None,
            'post_marginal_delta_wns': None, 'post_marginal_delta_tns': None,
            'openroad_version': rec.get('openroad_version'),
            'realisation': row.get('realisation'),
            'die_area': row.get('die_area'), 'core_area': row.get('core_area'),
            'noise_sigma': None, 'noise_threshold': None, 'above_noise': None,
            'noise_n_realisations': None, 'noise_sigma_global': None,
            'noise_family': None, 'noise_family_sigma': None,
            'cand_sigma': None, 'cand_threshold': None,
            'above_noise_candlevel': None, 'impl_offset_ns': None,
        }
        if base and rec.get('ok'):
            out['post_delta_wns'] = round(rec['wns_max'] - base['wns'], 6)
            out['post_delta_tns'] = round(rec['tns'] - base['tns'], 6)
        if iter_base and rec.get('ok'):
            out['post_marginal_delta_wns'] = round(rec['wns_max'] - iter_base['wns'], 6)
            out['post_marginal_delta_tns'] = round(rec['tns'] - iter_base['tns'], 6)
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
        # the candidate-level band: measured directly on THIS family's candidate
        # netlists (I0P0 vs I1P0), so it is not inherited from ISCAS89.
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
            'post_wns', 'post_tns', 'post_min_slack',
            'post_base_wns', 'post_base_tns', 'post_base_batch',
            'post_delta_wns', 'post_delta_tns',
            'post_iter_base_wns', 'post_iter_base_key',
            'post_marginal_delta_wns', 'post_marginal_delta_tns',
            'post_status', 'rc', 'above_noise', 'noise_sigma', 'noise_threshold',
            'noise_family', 'noise_family_sigma',
            'above_noise_candlevel', 'cand_sigma', 'cand_threshold', 'impl_offset_ns']
    with (FAM / 'physical_dataset.tsv').open('w', encoding='utf-8', newline='\n') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in records:
            fh.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')

    def block(batch):
        rs = [r for r in records if r['batch'] == batch]
        ok = [r for r in rs if r['post_status'] == 'ok']
        marg = [r for r in ok if r['post_marginal_delta_wns'] is not None]
        signed = [r for r in marg if r['ideal_delta_wns'] is not None]
        flips = [r for r in signed if r['ideal_delta_wns'] > 0 and r['post_marginal_delta_wns'] <= 0]
        return {
            'n_records': len(rs), 'n_post_ok': len(ok),
            'n_with_marginal_delta': len(marg), 'n_with_ideal_label': len(signed),
            'n_ideal_gain': sum(1 for r in signed if r['ideal_delta_wns'] > 0),
            'n_ideal_gain_but_post_not_gain': len(flips),
            'n_post_above_noise': sum(1 for r in marg if r['above_noise']),
            'mean_marginal_delta_wns': (round(sum(r['post_marginal_delta_wns'] for r in marg) / len(marg), 6)
                                        if marg else None),
            'mean_ideal_delta_wns': (round(sum(r['ideal_delta_wns'] for r in signed) / len(signed), 6)
                                     if signed else None),
        }

    summary = {
        'source_family': str(LEDGER_FAM.relative_to(REPO)),
        'noise_source': noise.get('source') if noise else None,
        'noise_pooled_sd': noise.get('pooled_sd') if noise else None,
        'noise_pooled_ci95': noise.get('pooled_ci95') if noise else None,
        'noise_per_circuit': noise.get('per_circuit') if noise else None,
        'noise_per_family': noise.get('per_family') if noise else None,
        'noise_family_sigma_used': noise.get('family_sigma') if noise else None,
        'noise_family_ci95_used': noise.get('family_ci95') if noise else None,
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
        'n_records': len(records),
        'per_batch': {b: block(b) for b in sorted({b for (b, _k) in jobs})},
        'per_circuit': {c: block(b) for (b, c) in
                        sorted({(r['batch'], r['circuit']) for r in records})},
        'caveat': (('the candidate-level band used here is measured ON THE ITC-99 '
                    'CIRCUITS (batch I0P0 vs I1P0); the ISCAS89 band does not transfer, '
                    'because the two families have materially different implementation '
                    'sensitivity')
                   if candnoise else
                   ('the candidate-level band measured on the ISCAS89 candidates does '
                    'NOT transfer to ITC-99: no second realisation has been run for '
                    'these circuits yet, so the noise-family band is used and flagged '
                    'as inherited')),
    }
    (FAM / 'dataset_summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'{len(records)} records -> physical_dataset.jsonl')
    for b, s in summary['per_batch'].items():
        print(f'  {b}: {s}')


if __name__ == '__main__':
    main()
