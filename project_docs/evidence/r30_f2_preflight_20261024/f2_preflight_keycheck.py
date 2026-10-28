"""PRE-FLIGHT for the three-implementation comparison: do the F0 / F1 / F2 job
tables line up on KEYS and NETLISTS?

WHY THIS MUST BE CHECKED BEFORE THE BATCH LANDS
------------------------------------------------
`impl_stability_probe.py` pairs the three realisations by ``(circuit, key)``:
a candidate is "the same candidate in three realisations" only if the three
label files carry the same key for the same circuit.  If the F2 job table used
a different key scheme (or a different netlist for the same logical candidate),
the pairing would silently match NOTHING and the tool would print a
three-way comparison with zero pools -- a result that looks like "no effect"
and is actually "no data".

The same applies to the netlists: routing a DIFFERENT netlist under F2 would
make the third realisation a measurement of something else.

This script checks:
  1. the key sets of the three job tables (I0, I1, I2);
  2. for every key, the netlist path and the candidate hash;
  3. the keys actually present in the dataset rows (physical_dataset.jsonl) per
     batch;
  4. the F2 smoke record against the F2 job table row.

Read-only.  No artefact is written.
"""
import csv
import json
import sys
from pathlib import Path

REPO = Path(r'D:/BaiduSyncdisk/01_Papers/03_FAECO')
FAM = REPO / 'experiments/20261024_physical_labels_itc99'

TABLES = {
    'F0 (I0)': FAM / 'jobs_itc99.tsv',
    'F1 (I1)': FAM / 'jobs_itc99_f1.tsv',
    'F2 (I2)': FAM / 'jobs_itc99_f2.tsv',
}

out = []


def read_tsv(path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


def main():
    rows = {name: read_tsv(p) for name, p in TABLES.items()}
    for name, rs in rows.items():
        out.append('%s: %d rows' % (name, len(rs)))
    out.append('')

    keys = {name: {r['key'] for r in rs} for name, rs in rows.items()}
    f0, f1, f2 = keys['F0 (I0)'], keys['F1 (I1)'], keys['F2 (I2)']
    out.append('key sets:')
    out.append('  |F0|=%d |F1|=%d |F2|=%d' % (len(f0), len(f1), len(f2)))
    out.append('  F0 == F1 : %s' % (f0 == f1))
    out.append('  F0 == F2 : %s' % (f0 == f2))
    out.append('  F1 == F2 : %s' % (f1 == f2))
    out.append('  F0 - F2  : %d   F2 - F0 : %d' % (len(f0 - f2), len(f2 - f0)))
    for k in sorted(f0 - f2)[:5]:
        out.append('    only in F0: %s' % k)
    for k in sorted(f2 - f0)[:5]:
        out.append('    only in F2: %s' % k)
    out.append('')

    # netlist + hash per key, per table
    def by_key(rs):
        return {r['key']: r for r in rs}

    b = {name: by_key(rs) for name, rs in rows.items()}
    common = sorted(f0 & f1 & f2)
    out.append('common keys across the three tables: %d' % len(common))
    diff_net = diff_hash = diff_kind = 0
    examples = []
    for k in common:
        r0, r1, r2 = b['F0 (I0)'][k], b['F1 (I1)'][k], b['F2 (I2)'][k]
        if r0['netlist'] != r2['netlist'] or r1['netlist'] != r2['netlist']:
            diff_net += 1
            if len(examples) < 5:
                examples.append('netlist differs at %s: F0=%s F2=%s'
                                % (k, r0['netlist'], r2['netlist']))
        if not (r0['candidate_hash'] == r1['candidate_hash'] == r2['candidate_hash']):
            diff_hash += 1
            if len(examples) < 10:
                examples.append('hash differs at %s' % k)
        if not (r0['kind'] == r1['kind'] == r2['kind']):
            diff_kind += 1
    out.append('  netlist mismatches vs F2 : %d' % diff_net)
    out.append('  candidate_hash mismatches : %d' % diff_hash)
    out.append('  kind mismatches           : %d' % diff_kind)
    for e in examples:
        out.append('    ' + e)
    out.append('')

    # the physical axes -- the whole point of a third realisation
    for name in ('F0 (I0)', 'F1 (I1)', 'F2 (I2)'):
        rs = rows[name]
        axes = {(r['pin_hor'], r['pin_ver'], r['core_space'], r['die_area'], r['util'])
                for r in rs}
        out.append('  %s physical axis: %s' % (name, sorted(axes)))
    out.append('')

    # the dataset rows that the probe will pair
    ds = FAM / 'physical_dataset.jsonl'
    if ds.exists():
        by_batch = {}
        for ln in ds.read_text(encoding='utf-8').splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            by_batch.setdefault(r.get('batch'), set()).add(r.get('key'))
        for bat, ks in sorted(by_batch.items()):
            out.append('  dataset rows batch %s: %d keys' % (bat, len(ks)))
        inter = None
        for bat in ('I0', 'I1'):
            if bat in by_batch:
                inter = by_batch[bat] if inter is None else (inter & by_batch[bat])
        if inter is not None:
            out.append('  I0 & I1 dataset keys: %d' % len(inter))
            out.append('  of which present in the F2 job table: %d'
                       % len(inter & f2))
    out.append('')

    # the F2 label file as it stands right now
    f2p = FAM / 'f2_labels.jsonl'
    if f2p.exists():
        recs = [json.loads(l) for l in f2p.read_text(encoding='utf-8').splitlines()
                if l.strip()]
        out.append('  f2_labels.jsonl: %d records' % len(recs))
        for r in recs[:3]:
            out.append('    key=%s batch=%s status=%s wns=%s base=%s marginal=%s'
                       % (r.get('key'), r.get('batch'), r.get('post_status'),
                          r.get('post_wns'), r.get('post_iter_base_wns'),
                          r.get('post_marginal_delta_wns')))
        known = {r.get('key') for r in recs}
        out.append('  f2 keys that are in the F2 job table: %d / %d'
                   % (len(known & f2), len(known)))
        out.append('  f2 keys that are also in the I0 dataset rows: %d'
                   % len(known & by_batch.get('I0', set())))

    txt = '\n'.join(out) + '\n'
    (REPO / 'scratch/f2_preflight_keycheck.txt').write_text(txt, encoding='utf-8')
    print('written scratch/f2_preflight_keycheck.txt')


if __name__ == '__main__':
    main()
