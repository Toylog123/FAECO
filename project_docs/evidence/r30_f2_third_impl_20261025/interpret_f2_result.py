"""Interpret the F2 (third routing realisation) result against the criteria
fixed in LOG-20261024-25 BEFORE the batch was launched.

Criteria (from LOG-25, checked against the synthetic fixtures):
  C1  three pairwise bands, max/min ~= 1  -> the three realisations are
      exchangeable and the band is a well-defined property of the measurement.
      Fixture baseline (fully synthetic, exchangeable): max/min = 1.028124.
  C2  max/min clearly apart from 1 -> F2's noise level differs from F0/F1, i.e.
      the implementation sensitivity is driven by the PHYSICAL AXIS (F2 shares
      the horizontal pin axis with F0 and the vertical one with F1).
      Fixture baseline (correlated third side): max/min = 1.718223.
  C3  three-way leave-one-out: the picker scored on the MEAN of two realisations
      should beat the picker scored on a single realisation, slightly but
      consistently.  Fixture baseline: 38 wins / 85 ties / 21 losses, p = 0.0363.
      If the real data shows the opposite, that is a DATA conclusion, not a tool
      failure (the fixture already proved the tool shows the advantage when
      there is one).

Everything is read from the artefacts; nothing is typed in.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ITCF = REPO / 'experiments/20261024_physical_labels_itc99'

FIX_EXCHANGEABLE = 1.028124
FIX_CORRELATED = 1.718223
FIX_LOO = {'wins': 38, 'ties': 85, 'losses': 21, 'p': 0.0363}


def load(p):
    p = Path(p)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError:
        return None


def main():
    out = {}
    isp = load(ITCF / 'impl_stability.json')
    f2s = load(ITCF / 'f2_labels_summary.json')
    receipt = load(REPO / 'scratch/f2_chain_receipt.json')

    out['artifacts_present'] = {
        'impl_stability.json': isp is not None,
        'f2_labels_summary.json': f2s is not None,
        'f2_chain_receipt.json': receipt is not None,
    }
    if not isp:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    # ---- C1/C2: the three pairwise bands -----------------------------------
    bp = isp.get('bands_by_pair') or {}
    pairs = {}
    for k, v in bp.items():
        pairs[k] = {
            'scope': v.get('scope'),
            'two_sigma_ns': v.get('two_sigma_ns'),
            'df': v.get('df'),
            'n_pairs': v.get('n_pairs'),
            'n_circuits': v.get('n_circuits'),
            'ci95': v.get('ci95'),
            'completeness': v.get('completeness'),
            'f0_batches': v.get('f0_batches'),
            'f1_batches': v.get('f1_batches'),
        }
    out['bands_by_pair'] = pairs

    bs = isp.get('band_stability') or {}
    ratio = bs.get('max_over_min_ratio')
    out['band_stability'] = {
        'two_sigma_by_pair': bs.get('two_sigma_by_pair'),
        'max_over_min_ratio': ratio,
        'interpretation_printed': bs.get('interpretation'),
        'note': bs.get('note'),
    }
    out['fixtures'] = {
        'exchangeable_max_over_min': FIX_EXCHANGEABLE,
        'correlated_max_over_min': FIX_CORRELATED,
        'leave_one_out': FIX_LOO,
    }
    if ratio is not None:
        d_ex = abs(ratio - FIX_EXCHANGEABLE)
        d_co = abs(ratio - FIX_CORRELATED)
        if ratio < 1.10:
            verdict = ('EXCHANGEABLE (C1 holds): the three pairwise spreads agree '
                       'within %.2f%% of the synthetic exchangeable fixture -> the '
                       'band is a well-defined property of the measurement, not an '
                       'artefact of which pair was chosen' % (d_ex / FIX_EXCHANGEABLE * 100))
        elif ratio < 1.35:
            verdict = ('INCONCLUSIVE: max/min = %.6f sits between the exchangeable '
                       'fixture (%.6f) and the correlated fixture (%.6f); the three '
                       'realisations do not look exchangeable, but the deviation is '
                       'not the size the deliberately-correlated fixture produced'
                       % (ratio, FIX_EXCHANGEABLE, FIX_CORRELATED))
        else:
            verdict = ('NOT EXCHANGEABLE (C2 holds): max/min = %.6f is far above the '
                       'exchangeable fixture (%.6f) and in the range of the '
                       'deliberately-correlated fixture (%.6f) -> F2\'s noise level '
                       'differs from F0/F1 and the implementation sensitivity is '
                       'driven by the PHYSICAL AXIS (F2 shares the horizontal pin '
                       'axis with F0 and the vertical one with F1)'
                       % (ratio, FIX_EXCHANGEABLE, FIX_CORRELATED))
        out['verdict_C1_C2'] = verdict

    # ---- C3: the three-way leave-one-out comparison ------------------------
    tw = isp.get('three_way_choice') or {}
    out['three_way_choice'] = {
        'per_direction': tw.get('per_direction'),
        'overall': tw.get('overall'),
        'per_pool_note': tw.get('note'),
    }
    ov = tw.get('overall') or {}
    if ov:
        # the artefact names the fields averaged_better / single_better / ties /
        # exact_binomial_p -- read them by their real names, not by guessed
        # aliases, so the verdict is derived from the artefact and not from a
        # naming assumption.
        w = ov.get('averaged_better')
        l = ov.get('single_better')
        t = ov.get('ties')
        p = ov.get('exact_binomial_p')
        out['C3_summary'] = {'averaged_better': w, 'single_better': l,
                             'ties': t, 'p': p, 'fixture': FIX_LOO}
        if w is not None and l is not None:
            # C3 says the mean-of-two picker should be "slightly but consistently"
            # better.  A win/loss difference that is NOT significant is a coin
            # flip, so the significance has to gate the verdict -- counting
            # wins > losses alone would turn 27 vs 25 (p = 0.89) into a "pass".
            sig = (p is not None and p < 0.05)
            if w > l and sig:
                out['verdict_C3'] = (
                    'C3 holds: the picker scored on the MEAN of two realisations wins '
                    '%s vs %s (ties %s, p=%s), the same direction as the synthetic '
                    'exchangeable fixture (%s/%s/%s, p=%s) -> averaging two '
                    'realisations really does reduce the implementation noise'
                    % (w, l, t, p, FIX_LOO['wins'], FIX_LOO['ties'], FIX_LOO['losses'],
                       FIX_LOO['p']))
            else:
                out['verdict_C3'] = (
                    'C3 does NOT hold: the mean-of-two picker wins %s vs loses %s '
                    '(ties %s, p=%s) -> averaging two realisations does NOT improve '
                    'the pick beyond chance.  Per the pre-registered criterion this '
                    'is a DATA conclusion, not a tool failure: the synthetic fixture '
                    'already showed the tool reports the advantage when there is one '
                    '(%s/%s/%s, p=%s).  Note %s.'
                    % (w, l, t, p, FIX_LOO['wins'], FIX_LOO['ties'], FIX_LOO['losses'],
                       FIX_LOO['p'],
                       ('the win/loss count is nominally positive but the exact '
                        'binomial p=%s is far from significant' % p)
                       if (w > l and not sig)
                       else 'the mean-of-two picker is not even nominally ahead'))

    # ---- the F2 label build self-checks -------------------------------------
    if f2s:
        out['f2_labels_summary'] = {
            'batch': f2s.get('batch'),
            'n_jobs': f2s.get('n_jobs'),
            'n_records': f2s.get('n_records'),
            'n_parsed_ok': f2s.get('n_parsed_ok'),
            'n_parse_failed': f2s.get('n_parse_failed'),
            'n_no_log': f2s.get('n_no_log'),
            'n_with_marginal_delta': f2s.get('n_with_marginal_delta'),
            'marginal_coverage': f2s.get('marginal_coverage'),
            'digest_convention_check': f2s.get('digest_convention_check'),
            'candidate_self_check': f2s.get('candidate_self_check'),
            'missing_reason': f2s.get('missing_reason'),
            'dataset_registration': f2s.get('dataset_registration'),
        }
    if receipt:
        out['chain_receipt'] = receipt

    out['probe_caveats'] = isp.get('caveats')
    out['probe_meta'] = isp.get('meta')

    (REPO / 'scratch/f2_interpretation.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items()
                      if k in ('verdict_C1_C2', 'verdict_C3', 'band_stability',
                               'three_way_choice', 'artifacts_present')},
                     indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
