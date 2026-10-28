"""Read the n_cells / depth distribution per circuit from the STORED structural
features (the authoritative artifact), and cross-check it against the netlist
files on disk.  Purpose: make sure the 'graph' that any GNN would consume is
the real circuit netlist and not a fragment."""
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAM = REPO / 'experiments/20261024_physical_labels_itc99'
tt = [json.loads(l) for l in (FAM / 'training_table.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
sf = [json.loads(l) for l in (FAM / 'structural_features.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]

by_ckt = defaultdict(list)
for r in sf:
    by_ckt[r.get('circuit')].append(r)

lines = []
lines.append('circuit  n_rows  n_cells(min/med/max)  depth(min/med/max)  n_ff  netlist_bytes')
for ckt in sorted(by_ckt):
    rs = by_ckt[ckt]
    nc = sorted(r.get('n_cells') or 0 for r in rs)
    dp = sorted((r.get('depth') or 0) for r in rs)
    nff = sorted((r.get('n_ff') or 0) for r in rs)
    med = lambda a: a[len(a) // 2]
    # netlist dir size on disk
    d = FAM / 'netlists' / ckt
    nb = 0
    if d.exists():
        nb = sum(f.stat().st_size for f in d.glob('*.v'))
    lines.append('%s %6d  %6d/%6d/%6d  %4d/%4d/%4d  %5d  %12d'
                 % (ckt, len(rs), nc[0], med(nc), nc[-1], dp[0], med(dp), dp[-1],
                    med(nff), nb))

# also: rows whose structural features are missing from the table
tt_keys = {r.get('key') for r in tt}
sf_keys = {r.get('key') for r in sf}
lines.append('')
lines.append('training_table rows      : %d' % len(tt))
lines.append('structural_feature rows  : %d' % len(sf))
lines.append('keys in tt not in sf     : %d' % len(tt_keys - sf_keys))
lines.append('keys in sf not in tt     : %d' % len(sf_keys - tt_keys))
lines.append('sf keys unique           : %d' % len(sf_keys))

out = REPO / 'scratch/graph_scale_check.txt'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
