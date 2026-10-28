"""Patch the three-point-curve cumulative reading in BOTH families, plus the
training table and the dataset card that inherit it.

THE DEFECT
----------
`acceptance_evidence.metric_references.setup_wns` in the ECO ledger is the
ITERATION BASE netlist's ideal WNS, not the circuit baseline's:
  * iteration-1 trials have base_netlist_hash == the circuit baseline netlist
    hash, so their reference IS the circuit-baseline ideal WNS;
  * iteration>=2 trials have the previous accepted candidate as their base.
The training table's `ideal_cumulative_wns` was computed as
`ideal_wns - ideal_baseline_wns`, and `ideal_baseline_wns` IS that iteration
base -> the "cumulative" column was the MARGINAL quantity under a wrong name,
while the placed and routed cumulative columns really are circuit-baseline
readings.  The shipped cumulative block therefore mixed readings and produced
negative correlations in ISCAS89 (spearman -0.11 / -0.13).

THE FIX
-------
  * read the circuit-baseline ideal WNS per circuit from the ledger
    (iteration-1 trials' reference) and subtract THAT from ideal_wns;
  * record the basis in the artefact so the reading can be audited;
  * keep the marginal block byte-for-byte identical (it is already published
    and it is correct);
  * fix the training table's column to carry the true cumulative reading and
    correct the schema text of `ideal_baseline_wns` (it is the iteration base);
  * note the reading in the dataset card.

Idempotent: every replacement is guarded by a marker check.
"""
import io
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARK = '# --- cumulative-reading fix (LOG-20261024-27) ---'

LEDGER_FN = '''

{MARK}
def circuit_baseline_ideal_wns():
    """circuit -> ideal WNS of the CIRCUIT BASELINE netlist.

    The ledger's `acceptance_evidence.metric_references.setup_wns` is the
    ITERATION BASE netlist's ideal WNS, not the circuit baseline's.  For the
    iteration-1 trials the base netlist hash IS the circuit baseline netlist,
    so their reference value is the circuit-baseline ideal WNS.  A circuit that
    does not yield exactly one value is left out on purpose: a silent guess
    would corrupt the cumulative reading.
    """
    out = {}
    if not LEDGER_FAM.exists():
        return out
    for ckt_dir in sorted(p for p in LEDGER_FAM.iterdir() if p.is_dir()):
        p = ckt_dir / ckt_dir.name / 'eval_trials.json'
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        refs = set()
        for t in d.get('trials', []):
            if not isinstance(t, dict) or str(t.get('iteration')) != '1':
                continue
            mr = (t.get('acceptance_evidence') or {}).get('metric_references') or {}
            v = mr.get('setup_wns')
            if v is not None:
                refs.add(round(float(v), 6))
        if len(refs) == 1:
            out[ckt_dir.name] = refs.pop()
    return out
'''

OLD_IDEAL_CUM = """            'ideal_cumulative': (r.get('ideal_wns') - r.get('ideal_baseline_wns')
                                 if r.get('ideal_wns') is not None
                                 and r.get('ideal_baseline_wns') is not None else None),"""

NEW_IDEAL_CUM = """            # CUMULATIVE = against the CIRCUIT BASELINE netlist.  The training
            # table's `ideal_baseline_wns` is the ITERATION base, so subtracting
            # it here would repeat the marginal reading under a wrong name.
            'ideal_cumulative': (round(r.get('ideal_wns') - cb_ideal[ckt], 6)
                                 if r.get('ideal_wns') is not None
                                 and ckt in cb_ideal else None),"""

BASIS_BLOCK = """        'ideal_cumulative_basis': {
            'note': ('the circuit-baseline ideal WNS per circuit, read from the '
                     'ledger as the reference of the iteration-1 trials (whose base '
                     'netlist hash IS the circuit baseline netlist); the cumulative '
                     'reading subtracts THIS, while the marginal reading subtracts '
                     'the iteration base'),
            'ledger_family': str(LEDGER_FAM.relative_to(REPO)),
            'n_circuits': len(cb_ideal),
            'circuit_baseline_ideal_wns': cb_ideal,
        },
"""


def patch(path, edits):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    applied = []
    for name, old, new in edits:
        if new.strip() and new in text:
            applied.append(name + ':already')
            continue
        if old not in text:
            raise SystemExit(f'PATCH FAILED {p.name} / {name}: anchor not found')
        if text.count(old) != 1:
            raise SystemExit(f'PATCH FAILED {p.name} / {name}: anchor not unique '
                             f'({text.count(old)} hits)')
        text = text.replace(old, new, 1)
        applied.append(name + ':ok')
    p.write_text(text, encoding='utf-8', newline='\n')
    return applied


def main():
    report = {}

    # ---------------- ITC-99 family ----------------
    itc = REPO / 'experiments/20261024_physical_labels_itc99/tools/three_point_curve_itc99.py'
    edits = [
        ('ledger_const',
         "NOISE = REPO / 'experiments/20261024_physical_transfer_noise'",
         "NOISE = REPO / 'experiments/20261024_physical_transfer_noise'\n"
         "LEDGER_FAM = REPO / 'experiments/20260826_itc99_main'"),
        ('ledger_fn',
         "F0_SIDE = ('I0P0', 'I0')",
         "F0_SIDE = ('I0P0', 'I0')" + LEDGER_FN),
        ('call',
         "    cands = []\n    for r in rows:\n"
         "        if r.get('batch') not in F0_SIDE:\n"
         "            continue\n"
         "        if r.get('post_status') != 'ok':\n"
         "            continue\n"
         "        if r.get('ideal_delta_wns') is None or r.get('post_marginal_delta_wns') is None:\n"
         "            continue\n",
         "    cb_ideal = circuit_baseline_ideal_wns()\n"
         "    if not cb_ideal:\n"
         "        raise SystemExit('circuit-baseline ideal WNS not derivable from the ledger'\n"
         "                         ' -- refusing to produce a cumulative reading')\n\n"
         "    cands = []\n    for r in rows:\n"
         "        if r.get('batch') not in F0_SIDE:\n"
         "            continue\n"
         "        if r.get('post_status') != 'ok':\n"
         "            continue\n"
         "        if r.get('ideal_delta_wns') is None or r.get('post_marginal_delta_wns') is None:\n"
         "            continue\n"),
        ('ideal_cum', OLD_IDEAL_CUM, NEW_IDEAL_CUM),
        ('basis',
         "        'netlist_consistency': cons,",
         BASIS_BLOCK + "        'netlist_consistency': cons,"),
    ]
    report['three_point_curve_itc99.py'] = patch(itc, edits)

    # ---------------- ISCAS89 family ----------------
    isc = REPO / 'experiments/20261024_physical_labels/tools/three_point_curve.py'
    edits = [
        ('ledger_const',
         "NOISE = REPO / 'experiments/20261024_physical_transfer_noise'",
         "NOISE = REPO / 'experiments/20261024_physical_transfer_noise'\n"
         "LEDGER_FAM = REPO / 'experiments/20260826_iscas89_main'"),
        ('ledger_fn',
         "F0_SIDE = ('F0', 'S713R')",
         "F0_SIDE = ('F0', 'S713R')" + LEDGER_FN),
        ('call',
         "    cands = []\n    for r in rows:\n"
         "        if r.get('batch') not in F0_SIDE:\n"
         "            continue\n"
         "        if r.get('post_status') != 'ok':\n"
         "            continue\n",
         "    cb_ideal = circuit_baseline_ideal_wns()\n"
         "    if not cb_ideal:\n"
         "        raise SystemExit('circuit-baseline ideal WNS not derivable from the ledger'\n"
         "                         ' -- refusing to produce a cumulative reading')\n\n"
         "    cands = []\n    for r in rows:\n"
         "        if r.get('batch') not in F0_SIDE:\n"
         "            continue\n"
         "        if r.get('post_status') != 'ok':\n"
         "            continue\n"),
        ('ideal_cum', OLD_IDEAL_CUM, NEW_IDEAL_CUM),
        ('basis',
         "        'placed_sources': sources,",
         BASIS_BLOCK + "        'placed_sources': sources,"),
    ]
    report['three_point_curve.py'] = patch(isc, edits)

    # ---------------- training table ----------------
    tt = REPO / 'experiments/20261024_physical_labels/tools/build_training_table.py'
    old_cum = """        ideal_cum = (r.get('ideal_wns') - r.get('ideal_baseline_wns')
                     if r.get('ideal_wns') is not None
                     and r.get('ideal_baseline_wns') is not None else None)"""
    new_cum = """        # the cumulative reading comes from the three-point-curve artefact, which
        # subtracts the CIRCUIT BASELINE; `ideal_baseline_wns` in the dataset is
        # the ITERATION base, so it must not be used here (it would repeat the
        # marginal reading under a wrong name).
        ideal_cum = t.get('ideal_cumulative')"""
    edits = [
        ('ideal_cum', old_cum, new_cum),
        ('schema_base',
         "    ('ideal_baseline_wns', '理想线网下该电路基线的 worst slack (ns)'),",
         "    ('ideal_baseline_wns', '理想线网下该候选的迭代基线网表的 worst slack (ns)；"
         "注意不是电路基线，电路基线见 ideal_cumulative_wns 的口径说明'),"),
        ('schema_delta',
         "    ('ideal_delta_wns', '理想线网边际增益：候选相对其迭代基线的 WNS 差 (ns)'),",
         "    ('ideal_delta_wns', '理想线网边际增益：候选相对其迭代基线的 WNS 差 (ns)'),"),
    ]
    report['build_training_table.py'] = patch(tt, edits)

    # ---------------- dataset card ----------------
    dc = REPO / 'experiments/20261024_physical_labels/tools/make_dataset_card.py'
    old_card = ("    w('- **累积（cumulative）**：相对**电路基线网表**的效果 —— '\n"
                "      '`ideal_cumulative_wns` / `placed_cumulative_wns` / `routed_cumulative_wns`。')")
    new_card = ("    w('- **累积（cumulative）**：相对**电路基线网表**的效果 —— '\n"
                "      '`ideal_cumulative_wns` / `placed_cumulative_wns` / `routed_cumulative_wns`。'\n"
                "      '注意 `ideal_baseline_wns` 是**迭代基线**而不是电路基线，'\n"
                "      '累积口径的电路基线取自 ledger 的迭代 1 参照值。')")
    edits = [
        ('card', old_card, new_card),
        ('nulls',
         "        'ideal_cumulative_wns': '缺 ideal_wns 或 ideal_baseline_wns',",
         "        'ideal_cumulative_wns': '缺 ideal_wns 或该电路的 ledger 参照值',"),
    ]
    report['make_dataset_card.py'] = patch(dc, edits)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
