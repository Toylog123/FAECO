"""What EXACTLY differs between the I0 and the I2 run on a degenerate circuit?

On b02/b08/b09/b13 the I0 and I2 routed databases (final.odb) are byte
identical, so the vertical pin-layer change (met2 -> met4) did not alter the
design at all.  This probe answers the question that decides whether that is
physics or a silently-ignored setting:

  * it diffs the two run logs line by line and prints every differing line --
    if `place_pins` reported a different pin layer or a pin-count warning, it
    is here;
  * it extracts the pin-placement evidence (pins placed, layer names,
    warnings) from both logs;
  * it does the same for a NON-degenerate circuit (b01) as the control, where
    the two runs must differ in the pin layer.

Output: scratch/f2_degeneracy_logdiff.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / 'experiments/20261024_physical_labels_itc99/runs'
OUT = REPO / 'scratch/f2_degeneracy_logdiff.json'

# lines worth looking at: pin placement, layer names, warnings, errors
INTEREST = re.compile(r'pin|layer|warn|error|placed|horizontal|vertical',
                      re.IGNORECASE)


def log_of(batch, circuit, key):
    base = RUNS / batch
    for d in sorted(base.iterdir()):
        if d.is_dir() and d.name.startswith(circuit + '__t') and key in d.name:
            p = d / 'pr_run.log'
            if p.exists():
                return p
    return None


def pick_key(circuit):
    keys = {}
    for b in ('I0', 'I1', 'I2'):
        ks = set()
        for d in sorted((RUNS / b).iterdir()):
            if d.is_dir() and d.name.startswith(circuit + '__t'):
                ks.add(d.name.split('__')[-1])
        keys[b] = ks
    common = keys['I0'] & keys['I1'] & keys['I2']
    return sorted(common)[0] if common else None


def diff_lines(a, b):
    la = a.read_text(encoding='utf-8', errors='replace').splitlines()
    lb = b.read_text(encoding='utf-8', errors='replace').splitlines()
    sa = set(la)
    sb = set(lb)
    only_a = [l for l in la if l not in sb]
    only_b = [l for l in lb if l not in sa]
    return {'n_lines_%s' % 'A': len(la), 'n_lines_%s' % 'B': len(lb),
            'only_in_A': only_a, 'only_in_B': only_b,
            'n_only_in_A': len(only_a), 'n_only_in_B': len(only_b)}


def interesting(path):
    if path is None:
        return []
    out = []
    for ln in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if INTEREST.search(ln):
            out.append(ln.strip())
    return out


PAIRS = [('b02', 'I0', 'I2'), ('b08', 'I0', 'I2'), ('b09', 'I0', 'I2'),
         ('b13', 'I0', 'I2'), ('b10', 'I1', 'I2'), ('b01', 'I0', 'I2'),
         ('b03', 'I0', 'I2')]

out = {'probe': 'line-level diff of the run logs of the degenerate pairs, plus a '
                'non-degenerate control (b01, b03)',
       'pairs': {}}

for ckt, ba, bb in PAIRS:
    key = pick_key(ckt)
    pa = log_of(ba, ckt, key)
    pb = log_of(bb, ckt, key)
    entry = {'circuit': ckt, 'pair': '%s vs %s' % (ba, bb), 'key': key,
             'log_a': str(pa.relative_to(REPO)) if pa else None,
             'log_b': str(pb.relative_to(REPO)) if pb else None}
    if pa and pb:
        entry['diff'] = diff_lines(pa, pb)
        entry['interesting_A'] = interesting(pa)[:60]
        entry['interesting_B'] = interesting(pb)[:60]
        # the union of lines that mention a MET layer name
        def met_lines(p):
            res = []
            for ln in p.read_text(encoding='utf-8', errors='replace').splitlines():
                if re.search(r'\bmet[1-9]\b', ln):
                    res.append(ln.strip())
            return res
        entry['met_lines_A'] = met_lines(pa)[:40]
        entry['met_lines_B'] = met_lines(pb)[:40]
    out['pairs']['%s_%s' % (ckt, ba + '_' + bb)] = entry

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

for name, e in out['pairs'].items():
    print('=== %s (%s) ===' % (name, e['pair']))
    if 'diff' not in e:
        print('  no logs')
        continue
    d = e['diff']
    print('  log lines: %d vs %d   only-in-A %d   only-in-B %d'
          % (d['n_lines_A'], d['n_lines_B'], d['n_only_in_A'], d['n_only_in_B']))
    for ln in d['only_in_A'][:8]:
        print('    A only: %s' % ln.strip()[:150])
    for ln in d['only_in_B'][:8]:
        print('    B only: %s' % ln.strip()[:150])
    print('  met lines A: %d   met lines B: %d'
          % (len(e['met_lines_A']), len(e['met_lines_B'])))
    for ln in e['met_lines_A'][:5]:
        print('    A met : %s' % ln[:150])
    for ln in e['met_lines_B'][:5]:
        print('    B met : %s' % ln[:150])
    print()

print('wrote %s' % OUT)
