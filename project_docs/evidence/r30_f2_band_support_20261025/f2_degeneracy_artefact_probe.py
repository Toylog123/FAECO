"""Is the F2 degeneracy a PHYSICAL fact or a BATCH artefact?

The audit found that on b02/b08/b09/b13 the F0 and F2 post-route WNS agree
bit-for-bit for EVERY candidate, and on b10 F1 and F2 agree for every
candidate.  Two explanations are possible:

  (H1) physics -- the frozen floorplan makes the util axis inert and the pin
       layer change really does not move the post-route WNS on those circuits;
  (H2) artefact -- the F2 job did not really run those circuits (reused output,
       skipped, or silently used the F0 configuration).

This probe separates them by looking at the RUN ARTEFACTS themselves, not at the
labels: for one candidate per circuit it compares the I0 and I2 run
directories -- file inventory, byte sizes, hashes of the STA report and of the
routed database, and the CONFIGURATION LINES the runs actually emitted.

Output: scratch/f2_degeneracy_artefact_probe.json
"""
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / 'experiments/20261024_physical_labels_itc99/runs'
OUT = REPO / 'scratch/f2_degeneracy_artefact_probe.json'

# configuration lines whose difference would prove the runs were not identical
CFG_PATTERNS = [
    r'pin_horizontal_layer|pin_h_layer|horizontal_pin|hor_pin',
    r'pin_vertical_layer|pin_v_layer|vertical_pin|ver_pin',
    r'core_utilization|utilization|core_space',
    r'die_area|core_area',
    r'metal\s+\d+',
]
CFG_RE = re.compile('|'.join(CFG_PATTERNS), re.IGNORECASE)


def sha(p):
    h = hashlib.sha256()
    try:
        h.update(Path(p).read_bytes())
    except OSError:
        return None
    return h.hexdigest()


def inventory(d):
    out = {}
    for f in sorted(Path(d).rglob('*')):
        if f.is_file():
            out[str(f.relative_to(d))] = f.stat().st_size
    return out


def cfg_lines(d):
    """The configuration-looking lines the run actually emitted."""
    lines = []
    for f in sorted(Path(d).rglob('*.log')):
        try:
            txt = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for ln in txt.splitlines():
            if CFG_RE.search(ln):
                lines.append('%s | %s' % (f.name, ln.strip()))
    return lines


def find_candidate(batch, circuit, key):
    """The run directory whose name starts with <circuit>__ and contains the key."""
    base = RUNS / batch
    out = []
    for d in sorted(base.iterdir()):
        if not d.is_dir() or not d.name.startswith(circuit + '__'):
            continue
        if key in d.name:
            out.append(d)
    return out


def pick_key(circuit):
    """A candidate key that exists in all three batches."""
    keys = {}
    for b in ('I0', 'I1', 'I2'):
        ks = set()
        for d in sorted((RUNS / b).iterdir()):
            if d.is_dir() and d.name.startswith(circuit + '__t'):
                ks.add(d.name.split('__')[-1])
        keys[b] = ks
    common = keys['I0'] & keys['I1'] & keys['I2']
    return sorted(common)[0] if common else None


CIRCUITS = ['b01', 'b02', 'b03', 'b08', 'b09', 'b10', 'b13']
out = {'question': ('is the F0/F2 bit-identical degeneracy on b02/b08/b09/b13 (and '
                    'the F1/F2 one on b10) a physical property of those circuits or '
                    'an artefact of the F2 batch not really running them?'),
       'probe': 'run-artefact level: file inventory, sizes, hashes, and the '
                'configuration lines each run actually emitted',
       'per_circuit': {}}

for ckt in CIRCUITS:
    key = pick_key(ckt)
    if key is None:
        out['per_circuit'][ckt] = {'error': 'no common candidate key across I0/I1/I2'}
        continue
    entry = {'key': key, 'batches': {}}
    for b in ('I0', 'I1', 'I2'):
        dirs = find_candidate(b, ckt, key)
        if not dirs:
            entry['batches'][b] = {'error': 'run dir not found'}
            continue
        d = dirs[0]
        inv = inventory(d)
        entry['batches'][b] = {
            'run_dir': str(d.relative_to(REPO)),
            'n_files': len(inv),
            'total_bytes': sum(inv.values()),
            'file_names': sorted(inv.keys()),
            'sha256': {k: sha(d / k) for k in sorted(inv.keys())},
            'config_lines': cfg_lines(d),
        }
    # do the three run directories contain DIFFERENT bytes?
    hs = {}
    for b, v in entry['batches'].items():
        if 'sha256' in v:
            for k, h in v['sha256'].items():
                if h:
                    hs.setdefault(k, {})[b] = h
    entry['files_identical_across_batches'] = {
        k: (len(set(v.values())) == 1, sorted(v.keys()))
        for k, v in sorted(hs.items())}
    entry['n_files_identical'] = sum(1 for v in entry['files_identical_across_batches'].values()
                                     if v[0])
    entry['n_files_compared'] = len(entry['files_identical_across_batches'])
    entry['runs_produced_different_bytes'] = (
        any(not v[0] for v in entry['files_identical_across_batches'].values()))
    out['per_circuit'][ckt] = entry

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

print('%-6s %-12s %-8s %-8s %-8s %-10s %s'
      % ('ckt', 'key', 'I0files', 'I1files', 'I2files', 'same?', 'diff bytes'))
for ckt, e in out['per_circuit'].items():
    if 'error' in e:
        print('%-6s ERROR %s' % (ckt, e['error']))
        continue
    b = e['batches']
    n = [b.get(x, {}).get('n_files') for x in ('I0', 'I1', 'I2')]
    same = '%d/%d' % (e['n_files_identical'], e['n_files_compared'])
    print('%-6s %-12s %-8s %-8s %-8s %-10s %s'
          % (ckt, e['key'], n[0], n[1], n[2], same, e['runs_produced_different_bytes']))
print()
for ckt, e in out['per_circuit'].items():
    if 'error' in e:
        continue
    print('--- %s (%s) ---' % (ckt, e['key']))
    for b in ('I0', 'I1', 'I2'):
        v = e['batches'].get(b, {})
        print('  %s: %s files, %s bytes, %s config lines'
              % (b, v.get('n_files'), v.get('total_bytes'), len(v.get('config_lines') or [])))
    ident = [k for k, v in e['files_identical_across_batches'].items() if v[0]]
    if ident:
        print('  identical across I0/I1/I2: %s' % ', '.join(ident[:8]))
print()
print('wrote %s' % OUT)
