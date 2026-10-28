"""Extract a graph representation and structural features for every candidate.

Why this tool exists
--------------------
The physical label family gives every candidate a real post-route label, but
the archived ECO ledgers carry NO structural information: `topology_metrics` is
null in all 121 537 trials of all 540 archived ledgers, the electrical metrics
are null, and every candidate touches the critical path (that membership has
zero variance, so it cannot discriminate).  In other words the dataset can
teach a model what the IDEAL netlist predicts, but not what the GRAPH says --
which is exactly the representation a learning-driven method would need.

This tool builds that missing half from the candidate netlists themselves:

  * a per-candidate GRAPH (cells as nodes, nets as edges) -- the "GNN input";
  * a per-candidate STRUCTURAL FEATURE vector -- the cheap scalar proxy of
    that graph, so the question "does structural information carry the physical
    signal?" can be answered without training a GNN first.

The netlists are plain gate-level Verilog (module / input / output / wire /
assign / instances; no always blocks, no parameters), so they are parsed here
directly -- no PDK library and no external tool is needed.  The only liberty
assumption is the direction of a blackbox cell's pins: for the sky130 cells
that occur here the output pins are Y / X / Q and every other pin is an input;
submodules defined in the same file (the inline `dff`) take their directions
from their own declarations.

The features are relative to the BASELINE netlist of the same circuit, because
an ECO candidate changes one cell: the interesting quantities are the depth
change, the cone the modified cell influences, and where the modification sits
on the critical path.

Outputs (in the family directory):
  graphs/<circuit>/<key>.json     the graph (only with --write-graphs)
  structural_features.jsonl        one JSON object per candidate
  structural_features_summary.json coverage + sanity counters

Usage:
  python tools/extract_graphs.py --family iscas89 [--write-graphs]
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LAB = REPO / 'experiments/20261024_physical_labels'
ITC = REPO / 'experiments/20261024_physical_labels_itc99'

FAMILIES = {
    'iscas89': {
        'dir': LAB,
        # batch -> the job table that produced it.  A candidate can appear in
        # several tables with DIFFERENT netlists (s713: the unrepaired netlist
        # in the main table, the tie-cell repaired one in the repair table), so
        # the netlist is taken from the table of the row's own label batch.
        'batch_tables': {'F0': 'jobs.tsv', 'S713R': 'jobs_s713_repaired.tsv'},
        'label_batches': ('F0', 'S713R'),
    },
    'itc99': {
        'dir': ITC,
        'batch_tables': {'I0P0': 'jobs_itc99_p0.tsv', 'I0': 'jobs_itc99.tsv',
                         'I1P0': 'jobs_itc99_f1_p0.tsv', 'I1': 'jobs_itc99_f1.tsv'},
        'label_batches': ('I0P0', 'I0'),
    },
}

# output pins of the blackbox cells that occur in these netlists
OUTPUT_PINS = {'Y', 'X', 'Q', 'Z', 'ZN', 'Q_N'}
# instance names that are sequential elements
FF_MARKERS = ('dfxtp', 'dfrtp', 'dfstp', 'dlxtp', 'edfxtp', 'sdfxtp', 'dfbbn')

CONST_RE = re.compile(r"^\d+'[bhd]", re.I)


# ----------------------------------------------------------------- parsing

def _split_names(text):
    return [n.strip() for n in text.split(',') if n.strip()]


def parse_netlist(path):
    """-> {module_name: {'ports': {pin: dir}, 'instances': [...], 'assigns': [...]}}"""
    modules = {}
    cur = None
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        i += 1
        if not s or s.startswith('/*') or s.startswith('*') or s.startswith('//'):
            continue
        if s.startswith('module '):
            name = s[len('module '):].split('(')[0].strip()
            cur = {'ports': {}, 'instances': [], 'assigns': [], 'wires': []}
            modules[name] = cur
            continue
        if s.startswith('endmodule'):
            cur = None
            continue
        if cur is None:
            continue
        if s.startswith('input '):
            for n in _split_names(s[len('input '):].rstrip(';')):
                cur['ports'][n] = 'input'
            continue
        if s.startswith('output '):
            for n in _split_names(s[len('output '):].rstrip(';')):
                cur['ports'][n] = 'output'
            continue
        if s.startswith('wire '):
            cur['wires'].extend(_split_names(s[len('wire '):].rstrip(';')))
            continue
        if s.startswith('assign '):
            body = s[len('assign '):].rstrip(';')
            if '=' in body:
                lhs, rhs = body.split('=', 1)
                cur['assigns'].append((lhs.strip(), rhs.strip()))
            continue
        # an instance: "<type> <name> (" then ".PIN(net)," lines then ");"
        m = re.match(r'^(\S+)\s+(\S+)\s*\($', s)
        if m:
            ctype, iname = m.group(1), m.group(2)
            conns = {}
            while i < len(lines):
                t = lines[i].strip()
                i += 1
                if t.startswith('.'):
                    pm = re.match(r'^\.(\S+?)\s*\(\s*([^)]*?)\s*\)\s*,?$', t)
                    if pm:
                        conns[pm.group(1)] = pm.group(2).strip()
                    continue
                if t.startswith(');') or t == ')':
                    break
            cur['instances'].append({'type': ctype, 'name': iname, 'conns': conns})
    return modules


def _union_find(nets):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    return find, union


def build_graph(modules, top):
    """Cells as nodes, nets as edges.  Returns a dict with the graph and the
    structural measurements.  Sequential cells break the combinational cone."""
    mod = modules[top]
    find, union = _union_find(list(mod['ports']) + list(mod['wires']))

    # net aliases (assign) collapse nets
    for lhs, rhs in mod['assigns']:
        if CONST_RE.match(rhs):
            continue
        union(lhs, rhs)

    insts = mod['instances']

    def pin_dir(ctype, pin):
        sub = modules.get(ctype)
        if sub is not None and pin in sub['ports']:
            return sub['ports'][pin]
        return 'output' if pin in OUTPUT_PINS else 'input'

    cells = {}
    driver_of = {}          # canonical net -> cell name
    sinks_of = defaultdict(list)
    const_inputs = set()

    for inst in insts:
        name = inst['name']
        ins, outs = [], []
        for pin, net in inst['conns'].items():
            if CONST_RE.match(net):
                const_inputs.add((name, pin))
                continue
            net = find(net)
            if pin_dir(inst['type'], pin) == 'output':
                outs.append(net)
                driver_of[net] = name
            else:
                ins.append(net)
        cells[name] = {'name': name, 'type': inst['type'], 'ins': ins, 'outs': outs}

    # primary inputs: nets that are module inputs and have no cell driver
    pinputs = [find(p) for p, d in mod['ports'].items() if d == 'input']
    poutputs = [find(p) for p, d in mod['ports'].items() if d == 'output']

    for cell in cells.values():
        for net in cell['ins']:
            if net in driver_of:
                sinks_of[net].append(cell['name'])
            elif net in pinputs:
                pass
            else:
                # undriven net (should not happen): treat it as a primary input
                pinputs.append(net)

    # sequential cells.
    # A submodule instance counts as SEQUENTIAL when every cell inside it is
    # sequential: the netlists define the flip-flop inline as `module dff ...
    # sky130_fd_sc_hd__dfxtp_1 ... endmodule` and instantiate it, so treating
    # `dff` as combinational would close a D->Q->...->D loop in the graph.
    seq_cache = {}

    def is_seq_type(ctype, _stack=None):
        if ctype in seq_cache:
            return seq_cache[ctype]
        stack = _stack or set()
        if ctype in stack:
            return False
        sub = modules.get(ctype)
        if sub is None:
            low = ctype.lower()
            val = any(mk in low for mk in FF_MARKERS)
        else:
            inner = sub['instances']
            val = bool(inner) and all(
                is_seq_type(i['type'], stack | {ctype}) for i in inner)
        seq_cache[ctype] = val
        return val

    def is_ff(cell):
        return is_seq_type(cell['type'])

    # combinational edges: driver cell -> sink cell, not through a FF
    edges = []
    for net, drv in driver_of.items():
        if drv not in cells:
            continue
        if is_ff(cells[drv]):
            continue                      # a FF output starts a new cone
        for snk in sinks_of.get(net, []):
            edges.append((drv, snk, net))

    # level (longest combinational distance from a source)
    succ = defaultdict(list)
    indeg = Counter()
    for a, b, _n in edges:
        succ[a].append(b)
        indeg[b] += 1
    # a cell is a source if all its inputs are primary inputs or FF outputs
    ff_driven = {n for n, c in driver_of.items() if c in cells and is_ff(cells[c])}
    src_cells = []
    for name, cell in cells.items():
        if is_ff(cell):
            src_cells.append(name)
            continue
        if all((n not in driver_of) or (n in ff_driven) for n in cell['ins']):
            src_cells.append(name)

    level = {}
    stack = list(src_cells)
    for s in src_cells:
        level[s] = 0
    # longest-path DP over the DAG (a combinational netlist is acyclic).
    # ITERATIVE post-order with cycle detection: the combinational paths of
    # these netlists are far longer than Python's recursion limit, and a
    # netlist that really does contain a combinational loop must not hang the
    # tool -- the back edge is dropped and the netlist is flagged instead.
    order = []
    seen = set()
    on_stack = set()
    has_cycle = False
    for root in list(cells):
        if root in seen:
            continue
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                on_stack.discard(node)
                if node not in seen:
                    seen.add(node)
                    order.append(node)
                continue
            if node in seen:
                continue
            if node in on_stack:
                has_cycle = True
                continue
            on_stack.add(node)
            stack.append((node, True))
            for m in succ.get(node, []):
                if m not in seen:
                    stack.append((m, False))
    for n in reversed(order):
        for m in succ.get(n, []):
            level[m] = max(level.get(m, 0), level.get(n, 0) + 1)
    depth = max(level.values()) if level else 0

    # longest path to a sink, and whether a cell lies on one
    best_to = {}
    for n in order:
        best = 0
        for m in succ.get(n, []):
            best = max(best, 1 + best_to.get(m, 0))
        best_to[n] = best

    def cone_down(name):
        seen2 = set()
        stack2 = [name]
        while stack2:
            x = stack2.pop()
            for m in succ.get(x, []):
                if m not in seen2:
                    seen2.add(m)
                    stack2.append(m)
        return len(seen2)

    def cone_up(name):
        pred = defaultdict(list)
        for a, b, _n in edges:
            pred[b].append(a)
        seen2 = set()
        stack2 = [name]
        while stack2:
            x = stack2.pop()
            for m in pred.get(x, []):
                if m not in seen2:
                    seen2.add(m)
                    stack2.append(m)
        return len(seen2)

    fanout = {n: len(succ.get(n, [])) for n in cells}
    max_fanout = max(fanout.values()) if fanout else 0
    n_ff = sum(1 for c in cells.values() if is_ff(c))

    return {
        'cells': cells, 'edges': edges, 'succ': succ, 'pred_edges': edges,
        'level': level, 'depth': depth, 'fanout': fanout, 'max_fanout': max_fanout,
        'n_cells': len(cells), 'n_ff': n_ff, 'n_nets': len(driver_of),
        'n_primary_inputs': len(set(pinputs)), 'n_primary_outputs': len(set(poutputs)),
        'is_ff': is_ff, 'cone_down': cone_down, 'cone_up': cone_up,
        'best_to': best_to, 'pinputs': sorted(set(pinputs)), 'poutputs': sorted(set(poutputs)),
        'has_cycle': has_cycle,
    }


def candidate_features(graph, instance, base_graph):
    """Structural features of one candidate, relative to its circuit baseline."""
    g = graph
    feats = {
        'depth': g['depth'],
        'n_cells': g['n_cells'],
        'n_ff': g['n_ff'],
        'max_fanout': g['max_fanout'],
        'n_primary_inputs': g['n_primary_inputs'],
        'n_primary_outputs': g['n_primary_outputs'],
    }
    if base_graph is not None:
        feats['depth_base'] = base_graph['depth']
        feats['n_cells_base'] = base_graph['n_cells']
        feats['max_fanout_base'] = base_graph['max_fanout']
        feats['d_depth'] = g['depth'] - base_graph['depth']
        feats['d_n_cells'] = g['n_cells'] - base_graph['n_cells']
        feats['d_max_fanout'] = g['max_fanout'] - base_graph['max_fanout']

    cell = g['cells'].get(instance)
    if cell is None:
        feats.update({'mod_found': 0, 'mod_fanin': None, 'mod_fanout': None,
                      'mod_level': None, 'mod_cone_down': None, 'mod_cone_up': None,
                      'mod_on_longest_path': None, 'mod_is_ff': None,
                      'mod_cone_down_frac': None})
        return feats

    lvl = g['level'].get(instance, 0)
    cone_d = g['cone_down'](instance)
    cone_u = g['cone_up'](instance)
    best = g['best_to'].get(instance, 0)
    on_path = 1 if (lvl + best) >= g['depth'] else 0
    feats.update({
        'mod_found': 1,
        'mod_type': cell['type'],
        'mod_fanin': len(cell['ins']),
        'mod_fanout': g['fanout'].get(instance, 0),
        'mod_level': lvl,
        'mod_cone_down': cone_d,
        'mod_cone_up': cone_u,
        'mod_on_longest_path': on_path,
        'mod_is_ff': 1 if g['is_ff'](cell) else 0,
        'mod_cone_down_frac': (cone_d / g['n_cells']) if g['n_cells'] else None,
    })
    return feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', choices=sorted(FAMILIES), required=True)
    ap.add_argument('--write-graphs', action='store_true',
                    help='also write the per-candidate graph JSON (large)')
    args = ap.parse_args()
    cfg = FAMILIES[args.family]
    fam_dir = cfg['dir']

    # key -> netlist path, per label batch
    key2net = {}
    conflicts = []
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
            k = row.get('key')
            net = row.get('netlist')
            if not k or not net:
                continue
            if k in key2net and key2net[k] != net:
                conflicts.append((k, key2net[k], net, batch))
                continue
            key2net[(batch, k)] = net
    # the batch of a candidate: the table it was labelled in
    batch_of = {}
    for (b, k) in list(key2net):
        batch_of.setdefault(k, b)

    tt_path = fam_dir / 'training_table.jsonl'
    if not tt_path.exists():
        raise SystemExit('training_table.jsonl missing -- run tools/build_training_table.py first')
    table = [json.loads(l) for l in tt_path.read_text(encoding='utf-8').splitlines() if l.strip()]

    # the ledger's critical path, for the "where on the critical path" features
    ledgers = {'iscas89': REPO / 'experiments/20260826_iscas89_main',
               'itc99': REPO / 'experiments/20260826_itc99_main'}[args.family]
    cp = {}
    for ckt_dir in sorted(ledgers.iterdir()) if ledgers.exists() else []:
        if not ckt_dir.is_dir():
            continue
        p = ckt_dir / ckt_dir.name / 'eval_trials.json'
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        for i, t in enumerate(d.get('trials', [])):
            cp[(ckt_dir.name, i)] = (t.get('critical_instances') or [],
                                     t.get('critical_endpoints') or [])

    base_graphs = {}
    graphs_dir = fam_dir / 'graphs'
    out_rows = []
    stats = Counter()
    for row in table:
        key = row.get('key')
        batch = row.get('label_batch')
        net_rel = key2net.get((batch, key))
        if net_rel is None:
            # fall back to any table that has this key
            for (b, k), v in key2net.items():
                if k == key:
                    net_rel = v
                    batch = b
                    break
        if not net_rel:
            stats['no_netlist_path'] += 1
            continue
        net_path = REPO / net_rel
        if not net_path.exists():
            stats['netlist_missing'] += 1
            continue
        try:
            modules = parse_netlist(net_path)
        except OSError:
            stats['parse_error'] += 1
            continue
        # the top module: the one that is not a submodule of another instance type
        tops = [m for m in modules if modules[m]['instances']]
        if not tops:
            stats['no_top_module'] += 1
            continue
        top = max(tops, key=lambda m: len(modules[m]['instances']))
        g = build_graph(modules, top)

        ckt = row.get('circuit')
        base_key = f'base__{ckt}'
        if ckt not in base_graphs:
            base_rel = key2net.get((batch, base_key)) or key2net.get(('F0', base_key))
            if base_rel is None:
                for (b, k), v in key2net.items():
                    if k == base_key:
                        base_rel = v
                        break
            bg = None
            if base_rel and (REPO / base_rel).exists():
                bmods = parse_netlist(REPO / base_rel)
                btops = [m for m in bmods if bmods[m]['instances']]
                if btops:
                    bg = build_graph(bmods, max(btops, key=lambda m: len(bmods[m]['instances'])))
            base_graphs[ckt] = bg
        bg = base_graphs.get(ckt)

        feats = candidate_features(g, row.get('instance'), bg)
        if g.get('has_cycle'):
            stats['netlist_with_combinational_cycle'] += 1
        crit, _ends = cp.get((ckt, row.get('trial_index')), ([], []))
        feats['cp_len'] = len(crit) if crit else None
        pos = crit.index(row.get('instance')) if (crit and row.get('instance') in crit) else None
        feats['cp_pos'] = pos
        feats['cp_pos_frac'] = (pos / (len(crit) - 1)) if (pos is not None and len(crit) > 1) else None
        feats['cp_pos_from_end'] = (len(crit) - 1 - pos) if (pos is not None and len(crit) > 1) else None
        feats['key'] = key
        feats['circuit'] = ckt
        feats['instance'] = row.get('instance')
        feats['kind'] = row.get('kind')
        out_rows.append(feats)
        stats['ok'] += 1
        if feats.get('mod_found') == 0:
            stats['modified_cell_not_found'] += 1

        if args.write_graphs:
            d = graphs_dir / ckt
            d.mkdir(parents=True, exist_ok=True)
            (d / f'{key}.json').write_text(json.dumps({
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
            }, ensure_ascii=False), encoding='utf-8')
            stats['graphs_written'] += 1

    dest = fam_dir / 'structural_features.jsonl'
    dest.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in out_rows),
                    encoding='utf-8')

    # sanity: do the structural features carry any variation at all?
    var = {}
    for r in out_rows:
        for k, v in r.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                var.setdefault(k, set()).add(v)
    summary = {
        'family': args.family,
        'n_rows': len(out_rows),
        'counters': dict(stats),
        'netlist_key_conflicts': len(conflicts),
        'conflict_sample': conflicts[:5],
        'distinct_values_per_feature': {k: len(v) for k, v in sorted(var.items())},
        'constant_features': sorted(k for k, v in var.items() if len(v) <= 1),
        'caveat': ('the graph is the COMBINATIONAL structure only: sequential cells '
                   'break the cone, so "depth" is the combinational depth and the '
                   'cone sizes count combinational descendants/ancestors.'),
    }
    (fam_dir / 'structural_features_summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f'family           : {args.family}')
    print(f'rows written     : {len(out_rows)}  ({dest.name})')
    print(f'counters         : {dict(stats)}')
    print(f'netlist conflicts: {len(conflicts)}')
    const = summary['constant_features']
    print(f'constant features: {const if const else "none"}')
    print(f'wrote {dest}')


if __name__ == '__main__':
    main()
