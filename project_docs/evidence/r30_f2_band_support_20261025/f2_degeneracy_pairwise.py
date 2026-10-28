"""PAIRWISE version of the degeneracy artefact probe.

The first pass showed the per-circuit totals; this one compares the three run
directories of one candidate PAIRWISE (I0 vs I2, I1 vs I2, I0 vs I1), file by
file, and names the files -- so "the F2 run produced the same bytes as the F0
run" can be read directly, and distinguished from "the F2 run did not run".

It also prints the pin-layer / utilisation configuration that each batch's job
table declares, so the configuration difference that the runs were SUPPOSED to
implement can be read off the job table itself.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / 'experiments/20261024_physical_labels_itc99/runs'
JOBS = REPO / 'experiments/20261024_physical_labels_itc99'
OUT = REPO / 'scratch/f2_degeneracy_pairwise.json'

CIRCUITS = ['b01', 'b02', 'b03', 'b08', 'b09', 'b10', 'b13']


def sha(p):
    h = hashlib.sha256()
    try:
        h.update(Path(p).read_bytes())
    except OSError:
        return None
    return h.hexdigest()


def find_candidate(batch, circuit, key):
    base = RUNS / batch
    for d in sorted(base.iterdir()):
        if d.is_dir() and d.name.startswith(circuit + '__t') and key in d.name:
            return d
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


def files_of(d):
    return {str(f.relative_to(d)): f for f in sorted(d.rglob('*')) if f.is_file()}


out = {'probe': 'pairwise run-artefact comparison for one candidate per circuit',
       'per_circuit': {}}

for ckt in CIRCUITS:
    key = pick_key(ckt)
    e = {'key': key}
    dirs = {b: find_candidate(b, ckt, key) for b in ('I0', 'I1', 'I2')}
    e['run_dirs'] = {b: (str(d.relative_to(REPO)) if d else None) for b, d in dirs.items()}
    maps = {b: files_of(d) for b, d in dirs.items() if d}
    e['file_names'] = {b: sorted(m.keys()) for b, m in maps.items()}
    common_names = sorted(set.intersection(*[set(m.keys()) for m in maps.values()])) if maps else []
    e['common_file_names'] = common_names
    e['pairwise'] = {}
    for a, b in (('I0', 'I2'), ('I1', 'I2'), ('I0', 'I1')):
        if a not in maps or b not in maps:
            continue
        e['pairwise']['%s_vs_%s' % (a, b)] = {
            n: {'same_bytes': sha(maps[a][n]) == sha(maps[b][n]),
                'size_%s' % a: maps[a][n].stat().st_size,
                'size_%s' % b: maps[b][n].stat().st_size}
            for n in common_names}
    out['per_circuit'][ckt] = e

# ---- the job tables: what configuration was each batch SUPPOSED to implement ----
jobinfo = {}
for name, fn in (('I0', 'jobs_itc99.tsv'), ('I1', 'jobs_itc99_f1.tsv'), ('I2', 'jobs_itc99_f2.tsv')):
    p = JOBS / fn
    if not p.exists():
        jobinfo[name] = {'error': 'missing %s' % fn}
        continue
    lines = p.read_text(encoding='utf-8', errors='replace').splitlines()
    jobinfo[name] = {'file': fn, 'header': lines[0] if lines else None,
                     'n_lines': len(lines) - 1, 'first_row': lines[1] if len(lines) > 1 else None}
out['job_tables'] = jobinfo

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

print('=== PAIRWISE FILE IDENTITY (one candidate per circuit) ===')
for ckt in CIRCUITS:
    e = out['per_circuit'][ckt]
    print('--- %s key=%s ---' % (ckt, e['key']))
    print('    files: %s' % ', '.join(e['common_file_names']))
    for pair, d in e['pairwise'].items():
        for n, v in d.items():
            print('    %-9s %-28s same_bytes=%-5s  size %s'
                  % (pair, n, v['same_bytes'],
                     '/'.join(str(v.get('size_%s' % x)) for x in pair.split('_vs_'))))
print()
print('=== JOB TABLES ===')
for b, v in jobinfo.items():
    print('%s (%s): %s lines' % (b, v.get('file'), v.get('n_lines')))
    print('    header: %s' % v.get('header'))
    print('    row   : %s' % v.get('first_row'))
print()
print('wrote %s' % OUT)
