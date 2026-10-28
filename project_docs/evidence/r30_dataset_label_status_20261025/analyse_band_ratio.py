"""Round 34 -- the band ratio: why did `stored_ratio_in_three_point_curve`
move from 2.933548 to 1.668075?

The cascade diff showed exactly ONE number in band_scope.json changing.  That
number is NOT a band: it is the RATIO of the two bands, and it is read from
the three-point curve artefact.  The question this script answers:

  is 2.933548 a value that the corrected patch invalidated, or is it a STALE
  value that the chain has been carrying since an earlier round?

The evidence to look for:
  1. the bands themselves in the curve artefact, before and after the patch
     (if they are bit-identical, the patch cannot have invalidated anything);
  2. the two sigma values and their df / n, and what the project's own
     records say the ratio was at each stage;
  3. whether the two fields in band_scope.json are the same QUANTITY:
     `ratio_routed_over_placed` is measured by band_scope_itc99.py itself,
     `stored_ratio_in_three_point_curve` is read out of the curve artefact.
     If they disagree, one of them is stale.

Everything is written to a text file.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / 'scratch/round34_baseline'
ITC = REPO / 'experiments/20261024_physical_labels_itc99'
OUT = REPO / 'scratch/round34_band_ratio.txt'

out = []
w = out.append

w('=' * 78)
w('ROUND 34 -- THE BAND RATIO: stale value or invalidated value?')
w('=' * 78)

lb = json.loads((BASE / '20261024_physical_labels_itc99__three_point_curve.json')
                .read_text(encoding='utf-8'))
lp = json.loads((ITC / 'three_point_curve.json').read_text(encoding='utf-8'))

w('')
w('1) the bands in the curve artefact')
for tag, d in (('baseline', lb), ('patched', lp)):
    b = d['bands']
    w('   %-9s routed 2sigma = %s   placed 2sigma = %s   ratio = %.6f'
      % (tag, b['routed_candidate_level_two_sigma_ns'],
         b['placed_candidate_level_two_sigma_ns'],
         b['routed_candidate_level_two_sigma_ns']
         / b['placed_candidate_level_two_sigma_ns']))
w('   the two band blocks are identical : %s'
  % (json.dumps(lb['bands'], sort_keys=True)
     == json.dumps(lp['bands'], sort_keys=True)))

w('')
w('2) where each band comes from')
rc = lb['bands']['routed_candidate_level']
pc = lb['bands']['placed_candidate_level']
w('   routed band  : pooled sd %s, df %s, n netlists %s'
  % (rc['pooled_within_circuit_sd_ns'], rc['df'], rc['n_candidate_netlists']))
w('   placed band  : pooled sd %s, df %s, n netlists %s'
  % (pc['pooled_within_circuit_sd_ns'], pc['df'], pc['n_candidate_netlists']))
w('   placed per-circuit n: %s'
  % ({k: v['n'] for k, v in pc['per_circuit'].items()},))
w('   sum of the per-circuit n (the circuit count is 9: 7 circuits + base +'
  ' final) = %d' % (sum(v['n'] for v in pc['per_circuit'].values()),))

w('')
w('3) the two fields of band_scope.json')
sb = json.loads((REPO / 'scratch/round34_downstream_before'
                 / '20261024_physical_labels_itc99__band_scope.json')
                .read_text(encoding='utf-8'))
sp = json.loads((ITC / 'band_scope.json').read_text(encoding='utf-8'))
for tag, d in (('before', sb), ('after ', sp)):
    br = d['sections']['band_ratio']
    w('   %s : scope=%s  routed2s=%s  placed2s=%s  own_ratio=%s  '
      'stored_ratio=%s'
      % (tag, br['selected_scope'], br['routed_two_sigma_ns'],
         br['placed_two_sigma_ns'], br['ratio_routed_over_placed'],
         br['stored_ratio_in_three_point_curve']))
w('   the own_ratio is IDENTICAL before and after : %s'
  % (sb['sections']['band_ratio']['ratio_routed_over_placed']
     == sp['sections']['band_ratio']['ratio_routed_over_placed']))
w('   => the two fields were already INCONSISTENT before the chain ran.')
w('      own_ratio = %s (measured by band_scope_itc99.py)'
  % sb['sections']['band_ratio']['ratio_routed_over_placed'])
w('      stored_ratio = %s (read out of the curve artefact)'
  % sb['sections']['band_ratio']['stored_ratio_in_three_point_curve'])

w('')
w('4) what the project records say the ratio was, and when')
for rel in ('project_docs/LOGS.md', 'project_docs/OPEN_ISSUES.md',
            'project_docs/evidence/EXPERIMENT_REGISTRY.md'):
    p = REPO / rel
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8', errors='replace')
    hits = []
    for m in re.finditer(r'(3\.637785|2\.9335\d*|2\.933514|1\.668\d*|'
                         r'2\.933548)', txt):
        s = max(0, m.start() - 260)
        ctx = txt[s:m.end() + 260].replace('\n', ' ')
        hits.append((m.group(1), ctx))
    if hits:
        w('   --- %s : %d hit(s)' % (rel, len(hits)))
        seen = set()
        for val, ctx in hits:
            key = (val, ctx[:80])
            if key in seen:
                continue
            seen.add(key)
            w('      [%s] ...%s...' % (val, ctx[:430]))

w('')
w('5) the reading')
w('   The corrected patch left the curve artefact\'s bands BIT-IDENTICAL,')
w('   so it cannot have invalidated the old ratio.')
w('   The old stored_ratio (2.933548) disagrees with the own_ratio that')
w('   band_scope_itc99.py measures on the SAME data (1.668108) -- the')
w('   two fields are the ratio of the same two bands, so they cannot')
w('   legitimately differ.  One of them is stale.')

(REPO / 'scratch/round34_band_ratio.txt').write_text(
    '\n'.join(out) + '\n', encoding='utf-8')
print('wrote scratch/round34_band_ratio.txt')
