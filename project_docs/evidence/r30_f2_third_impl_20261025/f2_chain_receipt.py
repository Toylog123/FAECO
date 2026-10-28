"""Machine receipt for the F2 (third realisation) post-processing chain.

Reads the two artefacts the F2 chain produces and emits the numbers a log
entry must quote.  The point is that the log entry is then a TRANSCRIPTION of
a receipt, not a recollection: every figure below is read back from the
artefact that produced it.
"""
import json
from pathlib import Path

REPO = Path('D:/BaiduSyncdisk/01_Papers/03_FAECO')
FAM = REPO / 'experiments/20261024_physical_labels_itc99'
OUT = REPO / 'scratch/f2_chain_receipt.json'


def read_json(p):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    summ = read_json(FAM / 'f2_labels_summary.json')
    probe = read_json(FAM / 'impl_stability.json')
    rec = {'source': {}, 'missing': []}

    if summ:
        rec['source']['f2_labels_summary'] = {
            'n_jobs': summ.get('n_jobs'),
            'n_records': summ.get('n_records'),
            'n_parsed_ok': summ.get('n_parsed_ok'),
            'n_parse_failed': summ.get('n_parse_failed'),
            'n_no_log': summ.get('n_no_log'),
            'n_with_marginal_delta': summ.get('n_with_marginal_delta'),
            'marginal_coverage': summ.get('marginal_coverage'),
            'missing_reason': summ.get('missing_reason'),
            'digest_convention_check': summ.get('digest_convention_check'),
            'candidate_self_check': summ.get('candidate_self_check'),
        }
    else:
        rec['missing'].append('f2_labels_summary.json')

    if probe:
        bands = probe.get('bands_by_pair') or {}
        tw = probe.get('three_way_choice') or {}
        rec['source']['impl_stability'] = {
            'third_realisation_complete': (probe.get('meta') or {}).get(
                'third_realisation_complete'),
            'coverage_I2': (probe.get('coverage') or {}).get('I2'),
            'bands_by_pair': {
                k: {
                    'scope': v.get('scope'),
                    'two_sigma_ns': v.get('two_sigma_ns'),
                    'df': v.get('df'),
                    'n_candidate_netlists': v.get('n_candidate_netlists'),
                    'n_circuits': v.get('n_circuits'),
                    'ci95': v.get('ci95'),
                    'completeness': v.get('completeness'),
                } for k, v in bands.items()},
            'band_stability': probe.get('band_stability'),
            'three_way_per_direction': tw.get('per_direction'),
            'three_way_overall': tw.get('overall'),
            'three_way_note': tw.get('note'),
        }
    else:
        rec['missing'].append('impl_stability.json')

    OUT.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(rec, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
