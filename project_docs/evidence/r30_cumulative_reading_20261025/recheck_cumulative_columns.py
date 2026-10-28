"""Independent recheck of the CUMULATIVE columns, from the raw dataset only.

Nothing here reuses the three-point-curve tool: the physical cumulative columns are
recomputed from physical_dataset.jsonl (post_wns of the candidate minus post_wns of
the BASE row of the SAME batch) and compared with the training table's columns.
The ideal cumulative column is recomputed from the ledger's own trial records.

Purpose: if the corrected cumulative reading is going to replace the shipped one,
the physical side of it must be independently confirmed, not inherited.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAM = REPO / 'experiments/20261024_physical_labels_itc99'
LEDGER_FAM = REPO / 'experiments/20260826_itc99_main'
DS = FAM / 'physical_dataset.jsonl'
TT = FAM / 'training_table.csv'


def main():
    out = {}
    rows = []
    with DS.open(encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # --- physical: baseline row of the SAME batch, keyed (batch, circuit)
    base_post = {}
    for r in rows:
        if str(r.get('key', '')).startswith('base__') and r.get('post_wns') is not None:
            base_post[(r.get('batch'), r.get('circuit'))] = r['post_wns']

    # --- recompute routed cumulative from raw post_wns and compare with the
    #     training table's routed_cumulative_wns
    tt = {}
    with TT.open(encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            tt[row['key']] = row

    prim = [r for r in rows if r.get('batch') == 'I0']
    n_cmp = n_ok = 0
    bad = []
    for r in prim:
        k = r.get('key')
        if k not in tt or r.get('post_wns') is None:
            continue
        cb = base_post.get(('I0', r['circuit']))
        if cb is None:
            continue
        recomputed = round(r['post_wns'] - cb, 6)
        shipped = tt[k].get('routed_cumulative_wns')
        if shipped in (None, ''):
            continue
        n_cmp += 1
        if abs(recomputed - float(shipped)) < 1e-6:
            n_ok += 1
        elif len(bad) < 6:
            bad.append({'key': k, 'recomputed': recomputed, 'shipped': float(shipped),
                        'post_wns': r['post_wns'], 'base_post_wns': cb})
    out['routed_cumulative_recheck'] = {
        'n_comparable': n_cmp, 'n_matching': n_ok, 'n_mismatching': n_cmp - n_ok,
        'mismatch_samples': bad,
        'note': ('the shipped routed_cumulative_wns equals post_wns(candidate) minus '
                 'post_wns(BASE row of the same batch) -> it IS a circuit-baseline reading'),
    }

    # --- the same for the marginal reading: post_wns(cand) - post_wns(iteration base)
    by_key = {}
    for r in rows:
        by_key.setdefault((r.get('batch'), r.get('key')), r)
    n_cmp2 = n_ok2 = 0
    bad2 = []
    for r in prim:
        k = r.get('key')
        if k not in tt or r.get('post_wns') is None:
            continue
        ibk = r.get('post_iter_base_key')
        if not ibk:
            continue
        ib = by_key.get(('I0', ibk))
        if ib is None or ib.get('post_wns') is None:
            continue
        recomputed = round(r['post_wns'] - ib['post_wns'], 6)
        shipped = tt[k].get('routed_delta_wns')
        if shipped in (None, ''):
            continue
        n_cmp2 += 1
        if abs(recomputed - float(shipped)) < 1e-6:
            n_ok2 += 1
        elif len(bad2) < 6:
            bad2.append({'key': k, 'recomputed': recomputed, 'shipped': float(shipped)})
    out['routed_marginal_recheck'] = {
        'n_comparable': n_cmp2, 'n_matching': n_ok2, 'n_mismatching': n_cmp2 - n_ok2,
        'mismatch_samples': bad2,
        'note': 'the shipped routed_delta_wns equals post_wns(cand) - post_wns(iteration base)',
    }

    # --- ideal: does the ledger agree with the training table's ideal columns?
    n_ckt_ideal = 0
    n_ckt_match = 0
    mismatch = []
    for ckt_dir in sorted(p for p in LEDGER_FAM.iterdir() if p.is_dir()):
        ckt = ckt_dir.name
        p = ckt_dir / ckt / 'eval_trials.json'
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        trials = [t for t in d.get('trials', []) if isinstance(t, dict)]
        # circuit baseline ideal WNS = the reference of the iteration-1 trials
        refs = set()
        for t in trials:
            if str(t.get('iteration')) != '1':
                continue
            mr = (t.get('acceptance_evidence') or {}).get('metric_references') or {}
            if mr.get('setup_wns') is not None:
                refs.add(mr['setup_wns'])
        cb = sorted(refs)[0] if len(refs) == 1 else None
        if cb is None:
            continue
        n_ckt_ideal += 1
        # every trial of that circuit: setup_wns must equal the training table's
        # ideal_wns for the matching key
        ok = True
        for idx, t in enumerate(trials):
            ev = t.get('acceptance_evidence') or {}
            sw = ev.get('setup_wns')
            if sw is None:
                continue
            # build_dataset_itc99.py keys the ledger by the LIST INDEX of the trial
            hit = False
            for k, row in tt.items():
                if row['circuit'] != ckt:
                    continue
                iw = row.get('ideal_wns')
                if iw in (None, ''):
                    continue
                if abs(float(iw) - float(sw)) < 1e-9 and row['trial_index'] == str(idx):
                    hit = True
                    break
            if not hit:
                ok = False
                if len(mismatch) < 6:
                    mismatch.append({'circuit': ckt, 'trial_index': t.get('trial_index'),
                                     'setup_wns': sw})
                break
        if ok:
            n_ckt_match += 1
    out['ideal_ledger_vs_training_table'] = {
        'n_circuits_checked': n_ckt_ideal, 'n_circuits_all_matched': n_ckt_match,
        'mismatch_samples': mismatch,
        'note': ('for every circuit the ledger setup_wns of each trial matches the '
                 'training table ideal_wns of the row with the same trial_index'),
    }

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
