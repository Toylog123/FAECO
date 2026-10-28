"""Smoke probe for the NEVER-EXECUTED `--write-graphs` code path.

The ITC-99 / ISCAS89 family directories have no `graphs/` directory, so the
graph-writing branch of `extract_graphs.py` has never run.  AGENTS.md requires
that a path that has never executed be sandboxed first.  This probe:

  * imports the tool (no re-implementation -- the point is to exercise the
    REAL code path),
  * builds the graph for a handful of candidates taken from DIFFERENT circuits,
  * serialises it exactly the way the tool does,
  * writes into `scratch/graph_smoke/` (never into the family directory),
  * reads the file back and checks that node/edge counts survive the round
    trip (a serialisation bug that silently drops edges would be invisible
    otherwise),
  * measures per-candidate wall time and file size so the full-run cost can be
    extrapolated before anything is written into the family directory.

It writes NOTHING into `experiments/`.
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / 'experiments/20261024_physical_labels/tools/extract_graphs.py'
OUT = REPO / 'scratch/graph_smoke'

spec = importlib.util.spec_from_file_location('extract_graphs', TOOL)
eg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eg)

FAMILY = sys.argv[1] if len(sys.argv) > 1 else 'itc99'
cfg = eg.FAMILIES[FAMILY]
fam_dir = cfg['dir']

# --- same key -> netlist mapping the tool builds -------------------------
key2net = {}
for batch, tname in cfg['batch_tables'].items():
    tpath = fam_dir / tname
    if not tpath.exists():
        continue
    lines = tpath.read_text(encoding='utf-8').splitlines()
    hdr = lines[0].split('\t')
    for line in lines[1:]:
        if not line.strip():
            continue
        row = dict(zip(hdr, line.split('\t')))
        k, net = row.get('key'), row.get('netlist')
        if k and net:
            key2net[(batch, k)] = net

tt_path = fam_dir / 'training_table.jsonl'
table = [json.loads(l) for l in tt_path.read_text(encoding='utf-8').splitlines() if l.strip()]

# --- pick a few candidates from distinct circuits ------------------------
picked, seen_ckt = [], set()
for row in table:
    ckt = row.get('circuit')
    if ckt in seen_ckt:
        continue
    batch = row.get('label_batch')
    net_rel = key2net.get((batch, row.get('key')))
    if net_rel is None:
        for (b, k), v in key2net.items():
            if k == row.get('key'):
                net_rel, batch = v, b
                break
    if not net_rel or not (REPO / net_rel).exists():
        continue
    seen_ckt.add(ckt)
    picked.append((row, net_rel, batch))
    if len(picked) >= 3:
        break

report = {'family': FAMILY, 'training_table_rows': len(table),
          'key2net_entries': len(key2net), 'probes': []}

OUT.mkdir(parents=True, exist_ok=True)
for row, net_rel, batch in picked:
    key = row.get('key')
    ckt = row.get('circuit')
    t0 = time.time()
    modules = eg.parse_netlist(REPO / net_rel)
    tops = [m for m in modules if modules[m]['instances']]
    top = max(tops, key=lambda m: len(modules[m]['instances']))
    g = eg.build_graph(modules, top)
    t_build = time.time() - t0

    t1 = time.time()
    payload = {
        'key': key, 'circuit': ckt, 'top': top,
        'n_cells': g['n_cells'], 'n_ff': g['n_ff'], 'depth': g['depth'],
        'nodes': [{'id': n, 'type': c['type'],
                   'fanin': len(c['ins']), 'fanout': g['fanout'].get(n, 0),
                   'level': g['level'].get(n, 0),
                   'is_ff': bool(g['is_ff'](c)),
                   'cone_down': g['cone_down'](n)}
                  for n, c in g['cells'].items()],
        'edges': [{'src': a, 'dst': b} for a, b, _n in g['edges']],
        'primary_inputs': g['pinputs'], 'primary_outputs': g['poutputs'],
    }
    txt = json.dumps(payload, ensure_ascii=False)
    t_json = time.time() - t1

    dest = OUT / ckt / f'{key}.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(txt, encoding='utf-8')

    back = json.loads(dest.read_text(encoding='utf-8'))
    ok_nodes = len(back['nodes']) == g['n_cells'] == len(payload['nodes'])
    ok_edges = len(back['edges']) == len(g['edges'])
    ok_head = back['depth'] == g['depth'] and back['n_cells'] == g['n_cells']
    # every edge endpoint must exist as a node
    ids = {n['id'] for n in back['nodes']}
    dangling = sum(1 for e in back['edges'] if e['src'] not in ids or e['dst'] not in ids)

    report['probes'].append({
        'key': key, 'circuit': ckt, 'batch': batch, 'netlist': net_rel,
        'n_cells': g['n_cells'], 'n_ff': g['n_ff'], 'depth': g['depth'],
        'n_edges': len(g['edges']), 'json_bytes': len(txt.encode('utf-8')),
        't_build_s': round(t_build, 3), 't_json_s': round(t_json, 3),
        'roundtrip_nodes_ok': ok_nodes, 'roundtrip_edges_ok': ok_edges,
        'roundtrip_header_ok': ok_head, 'dangling_edges': dangling,
        'has_cycle': bool(g.get('has_cycle')),
    })

tot_cells = sum(p['n_cells'] for p in report['probes'])
tot_bytes = sum(p['json_bytes'] for p in report['probes'])
tot_t = sum(p['t_build_s'] + p['t_json_s'] for p in report['probes'])
n = len(report['probes'])
report['extrapolation_full_run'] = {
    'n_candidates': len(table),
    'avg_json_bytes': tot_bytes // n,
    'avg_seconds': round(tot_t / n, 4),
    'est_total_MB': round(tot_bytes / n * len(table) / 1e6, 1),
    'est_total_minutes': round(tot_t / n * len(table) / 60, 2),
}
report['all_roundtrips_ok'] = all(p['roundtrip_nodes_ok'] and p['roundtrip_edges_ok']
                                  and p['roundtrip_header_ok'] and p['dangling_edges'] == 0
                                  for p in report['probes'])

(REPO / 'scratch/graph_write_probe.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
