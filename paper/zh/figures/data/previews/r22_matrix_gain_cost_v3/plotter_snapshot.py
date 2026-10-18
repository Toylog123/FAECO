"""Full C-prime matrix and matched contrasts; requires independent 72-job audit."""
import argparse
import csv
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
CIRCUITS = ('s27', 's382', 's420', 's641', 's713', 's820', 's832', 's953')
ARMS = ('W0', 'W1', 'U0', 'U1', 'C', 'UR1', 'UR2', 'UR3', 'L')
CONTRASTS = (('W0', 'U0'), ('W1', 'U1'), ('W1', 'W0'), ('W1', 'C'),
             ('W1', 'L'), ('W1', 'UR1'), ('W1', 'UR2'), ('W1', 'UR3'))
mpl.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 7, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'svg.fonttype': 'none', 'pdf.fonttype': 42, 'axes.linewidth': .5,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white', 'savefig.dpi': 600})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('x', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=ROOT/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--alignment-auditor', type=Path, required=True,
                        help='Path to the nature-figure audit_panel_alignment.py helper')
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding='utf-8'))
    if not (audit.get('all_matrix_verified') is True and audit.get('completed_and_verified') == 72
            and audit.get('expected_matrix_jobs') == 72 and audit.get('source_stable') is True):
        raise ValueError('Only the independently accepted complete 72-job matrix can be plotted')
    jobs = audit['jobs']
    expected = {(c, a) for c in CIRCUITS for a in ARMS}
    if len(jobs) != 72 or {(r['circuit'], r['arm']) for r in jobs} != expected:
        raise ValueError('Missing, duplicated or unexpected circuit/arm pair')
    rows = []
    for r in jobs:
        if not (r['sec_proven_points'] > 0 and r['sec_unproven_points'] == 0
                and r['other_sta_process_attempts'] == 0
                and r['total_sta_process_attempts'] == r['candidate_ideal_sta_launches'] + r['baseline_sta_process_attempts']):
            raise ValueError('Invalid equivalence or STA-count scope')
        completion = ROOT/'experiments/20261016_r22_cut_ablation_v3'/r['arm']/r['circuit']/'completion.json'
        if sha(completion) != r['completion_sha256']:
            raise ValueError('Completion bytes no longer match the independent audit')
        gain = (Decimal(str(r['final_wns'])) - Decimal(str(r['baseline_wns']))) * 1000
        if not gain.is_finite():
            raise ValueError('Non-finite WNS measurement')
        rows.append({'circuit': r['circuit'], 'arm': r['arm'], 'baseline_wns_ns': r['baseline_wns'],
            'final_wns_ns': r['final_wns'], 'wns_gain_ps': float(gain),
            'candidate_ideal_sta': r['candidate_ideal_sta_launches'],
            'baseline_sta': r['baseline_sta_process_attempts'], 'total_sta': r['total_sta_process_attempts'],
            'retained_commits': r['retained_commits'], 'completion_sha256': r['completion_sha256'],
            'source_head': audit['head']})
    by = {(r['circuit'], r['arm']): r for r in rows}
    paired = []
    for c in CIRCUITS:
        if len({by[c, a]['baseline_wns_ns'] for a in ARMS}) != 1:
            raise ValueError('Arms have different baseline WNS within a circuit')
        for left, right in CONTRASTS:
            a, b = by[c, left], by[c, right]
            delta = Decimal(str(a['wns_gain_ps'])) - Decimal(str(b['wns_gain_ps']))
            paired.append({'circuit': c, 'contrast': left+'-'+right,
                'gain_difference_ps': float(delta), 'sta_difference': a['total_sta']-b['total_sta'],
                'left_completion_sha256': a['completion_sha256'], 'right_completion_sha256': b['completion_sha256']})
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    stem = 'r22_matrix_gain_cost'
    write_csv(out/(stem+'_raw.csv'), rows)
    write_csv(out/(stem+'_paired.csv'), paired)
    gain = np.array([[by[c, a]['wns_gain_ps'] for a in ARMS] for c in CIRCUITS])
    cost = np.array([[by[c, a]['total_sta'] for a in ARMS] for c in CIRCUITS])
    pby = {(r['circuit'], r['contrast']): r for r in paired}
    labels = [a+'−'+b for a, b in CONTRASTS]
    pgain = np.array([[pby[c, a+'-'+b]['gain_difference_ps'] for a, b in CONTRASTS] for c in CIRCUITS])
    pcost = np.array([[pby[c, a+'-'+b]['sta_difference'] for a, b in CONTRASTS] for c in CIRCUITS])
    blue = LinearSegmentedColormap.from_list('gain', ['#FFFFFF', '#245B9E'])
    grey = LinearSegmentedColormap.from_list('cost', ['#FFFFFF', '#596575'])
    diverging = LinearSegmentedColormap.from_list('difference', ['#C77435', '#FFFFFF', '#245B9E'])
    # 170 x 128 mm; literal inches keep static dimension checks unambiguous.
    fig = plt.figure(figsize=(6.6929133858, 5.0393700787))
    specs = [(.08, .62, gain, ARMS, blue, False, 'WNS gain (ps)'),
             (.58, .62, cost, ARMS, grey, False, 'Total STA invocations'),
             (.08, .20, pgain, labels, diverging, True, 'Paired WNS gain difference (ps)'),
             (.58, .20, pcost, labels, diverging.reversed(), True, 'Paired STA cost difference')]
    for index, (x, y, values, names, cmap, symmetric, title) in enumerate(specs):
        ax = fig.add_axes((x, y, .37, .27))
        if symmetric:
            extent = max(1., float(np.max(np.abs(values))))
            image = ax.imshow(values, cmap=cmap, norm=TwoSlopeNorm(vmin=-extent, vcenter=0, vmax=extent), aspect='auto')
        else:
            image = ax.imshow(values, cmap=cmap, vmin=0, vmax=max(1., float(np.max(values))), aspect='auto')
        ax.set_xticks(range(len(names)), names, rotation=90 if symmetric else 0,
                      ha='right' if symmetric else 'center', rotation_mode='anchor', fontsize=7)
        ax.set_yticks(range(8), CIRCUITS, fontsize=7)
        ax.tick_params(length=0, pad=3)
        ax.set_xticks(np.arange(-.5, len(names), 1), minor=True)
        ax.set_yticks(np.arange(-.5, 8, 1), minor=True)
        ax.grid(which='minor', color='#E4E7EB', linewidth=.35)
        ax.tick_params(which='minor', bottom=False, left=False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for i in range(8):
            for j in range(len(names)):
                value = float(values[i, j])
                label = f'{value:g}'
                rgba = image.cmap(image.norm(value))
                luminance = .2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                ax.text(j, i, label, ha='center', va='center', fontsize=6.8,
                        color='white' if luminance < .50 else '#222222')
        cax = fig.add_axes((x+.06, y+.302, .31, .015))
        colorbar = fig.colorbar(image, cax=cax, orientation='horizontal')
        colorbar.ax.tick_params(labelsize=6.8, length=2, pad=1)
        colorbar.outline.set_linewidth(.4)
        ax.text(0, 1.265, chr(97+index), transform=ax.transAxes, fontsize=9, fontweight='bold')
        ax.text(.09, 1.265, title, transform=ax.transAxes, fontsize=7.1)
    audit_spec = importlib.util.spec_from_file_location('figure_alignment', args.alignment_auditor)
    alignment = importlib.util.module_from_spec(audit_spec)
    audit_spec.loader.exec_module(alignment)
    alignment.require_matplotlib_panel_alignment(
        fig, axes=fig.axes[::2], panel_ids=['a', 'b', 'c', 'd'],
        row_groups=[['a', 'b'], ['c', 'd']],
        column_groups=[['a', 'c'], ['b', 'd']], require_panel_labels=True,
        json_out=out/'PANEL_ALIGNMENT.json', overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    fig.savefig(out/f'{stem}.pdf', format='pdf')
    fig.savefig(out/f'{stem}.svg', format='svg')
    fig.savefig(out/f'{stem}.png', format='png', dpi=600)
    plt.close(fig)
    qa = {'status': 'rendered; visual review pending', 'observations': 72, 'excluded': 0,
        'paired_contrasts': 64, 'audit_sha256': sha(args.audit), 'plotter_sha256': sha(__file__),
        'alignment_auditor_sha256': sha(args.alignment_auditor),
        'physical_size_mm': [170, 128], 'unit': 'ps for gains; actual process attempts for STA',
        'interpretation': 'Positive gain difference favors left arm; negative STA-cost difference favors left arm',
        'statistics': 'Each deterministic arm once; each random seed separately. No aggregation, error bars or significance.',
        'exports_sha256': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    with (out/'QA.json').open('x', encoding='utf-8') as file:
        json.dump(qa, file, ensure_ascii=False, indent=2)
    print(json.dumps({'output_dir': str(out), 'jobs': 72, 'contrasts': 64}))


if __name__ == '__main__':
    main()
