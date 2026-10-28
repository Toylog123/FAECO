"""Check, for BOTH families, that the circuit-baseline ideal WNS is uniquely
derivable from the ledger (iteration-1 trials' metric_references.setup_wns).

If a circuit does not yield exactly one value, the corrected cumulative column
would silently lose rows for that circuit -- so this must be known BEFORE the
tool is changed, not after.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAMS = {
    'iscas89': REPO / 'experiments/20260826_iscas89_main',
    'itc99': REPO / 'experiments/20260826_itc99_main',
}


def probe(fam_dir):
    out = {}
    if not fam_dir.exists():
        return out
    for ckt_dir in sorted(p for p in fam_dir.iterdir() if p.is_dir()):
        p = ckt_dir / ckt_dir.name / 'eval_trials.json'
        if not p.exists():
            # some families nest differently
            alt = list(ckt_dir.glob('*/eval_trials.json'))
            if not alt:
                continue
            p = alt[0]
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            out[ckt_dir.name] = {'error': str(e)}
            continue
        refs = set()
        hashes = set()
        n1 = 0
        for t in d.get('trials', []):
            if not isinstance(t, dict):
                continue
            if str(t.get('iteration')) != '1':
                continue
            n1 += 1
            mr = (t.get('acceptance_evidence') or {}).get('metric_references') or {}
            v = mr.get('setup_wns')
            if v is not None:
                refs.add(float(v))
            if t.get('base_netlist_hash'):
                hashes.add(t['base_netlist_hash'])
        out[ckt_dir.name] = {
            'path': str(p.relative_to(REPO)),
            'n_iter1_trials': n1,
            'distinct_iter1_refs': sorted(refs),
            'n_distinct_iter1_base_hashes': len(hashes),
            'unique': len(refs) == 1,
            'circuit_baseline_ideal_wns': sorted(refs)[0] if len(refs) == 1 else None,
        }
    return out


def main():
    res = {}
    for fam, d in FAMS.items():
        r = probe(d)
        res[fam] = r
        n_ok = sum(1 for v in r.values() if v.get('unique'))
        res[fam]['_summary'] = {
            'n_circuits': len(r),
            'n_unique': n_ok,
            'n_not_unique': len(r) - n_ok,
            'not_unique_circuits': [c for c, v in r.items() if not v.get('unique')],
        }
    json.dump(res, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
