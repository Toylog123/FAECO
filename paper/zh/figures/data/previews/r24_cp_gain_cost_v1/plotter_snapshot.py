"""C-prime accepted 72-job endpoint gains and actual candidate STA costs.

Structural adaptation of the accepted r22 matrix plot: all data are retained,
Chinese typography follows the manuscript, and baseline STA is counted apart.
"""
import argparse
import csv
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
CIRCUITS = ('s27', 's382', 's420', 's641', 's713', 's820', 's832', 's953')
ARMS = ('W0', 'W1', 'U0', 'U1', 'C', 'UR1', 'UR2', 'UR3', 'L')
CONTRASTS = (('W0', 'U0'), ('W1', 'U1'), ('W1', 'W0'), ('W1', 'C'),
             ('W1', 'L'), ('W1', 'UR1'), ('W1', 'UR2'), ('W1', 'UR3'))
AUDIT_SHA = 'a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738'
RUNTIME_HEAD = '3ea0f757f5e9bab4a2df75c458b0c665eabcb258'
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans'],
    'axes.unicode_minus': False, 'font.size': 7.5,
    'axes.labelsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'legend.fontsize': 7, 'axes.linewidth': .6,
    'axes.spines.top': False, 'axes.spines.right': False,
    'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white', 'savefig.dpi': 600,
})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def write_csv(path, rows):
    with path.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_rows(audit_path):
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if sha(audit_path) != AUDIT_SHA:
        raise ValueError('Audit bytes do not match the accepted complete72 evidence')
    if not (audit.get('all_matrix_verified') is True and audit.get('completed_and_verified') == 72
            and audit.get('expected_matrix_jobs') == 72 and audit.get('source_stable') is True
            and audit.get('head') == RUNTIME_HEAD):
        raise ValueError('Only the accepted complete72 matrix can be plotted')
    jobs = audit['jobs']
    if len(jobs) != 72 or {(r['circuit'], r['arm']) for r in jobs} != {(c, a) for c in CIRCUITS for a in ARMS}:
        raise ValueError('Missing, duplicated or unexpected circuit/arm pair')
    rows = []
    for r in jobs:
        completion = ROOT/'experiments/20261016_r22_cut_ablation_v3'/r['arm']/r['circuit']/'completion.json'
        if sha(completion) != r['completion_sha256']:
            raise ValueError('Completion bytes differ from accepted audit')
        if not (r['sec_proven_points'] > 0 and r['sec_unproven_points'] == 0
                and r['other_sta_process_attempts'] == 0 and r['baseline_sta_process_attempts'] == 1
                and r['total_sta_process_attempts'] == r['candidate_ideal_sta_launches'] + 1
                and len(r['launch_artifacts']) == r['candidate_ideal_sta_launches']):
            raise ValueError('Invalid SEC or actual STA ledger scope')
        gain = (Decimal(str(r['final_wns'])) - Decimal(str(r['baseline_wns']))) * 1000
        if not gain.is_finite() or gain < 0:
            raise ValueError('Invalid accepted WNS gain')
        rows.append({
            'circuit': r['circuit'], 'arm': r['arm'], 'baseline_wns_ns': r['baseline_wns'],
            'final_wns_ns': r['final_wns'], 'wns_gain_ps': float(gain), 'wns_gain_ns': float(gain / 1000),
            'candidate_ideal_sta': r['candidate_ideal_sta_launches'],
            'candidate_evaluation_records': r['candidate_evaluation_records'],
            'baseline_sta': r['baseline_sta_process_attempts'], 'total_sta': r['total_sta_process_attempts'],
            'retained_commits': r['retained_commits'], 'sec_proven_points': r['sec_proven_points'],
            'sec_unproven_points': r['sec_unproven_points'],
            'completion_path': completion.relative_to(ROOT).as_posix(),
            'completion_sha256': r['completion_sha256'], 'source_head': audit['head'],
        })
    by = {(r['circuit'], r['arm']): r for r in rows}
    for c in CIRCUITS:
        if len({by[c, a]['baseline_wns_ns'] for a in ARMS}) != 1:
            raise ValueError('Unmatched within-circuit starting WNS')
    return audit, [by[c, a] for c in CIRCUITS for a in ARMS]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=ROOT/'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--alignment-auditor', type=Path, required=True)
    args = parser.parse_args()
    audit, rows = load_rows(args.audit)
    by = {(r['circuit'], r['arm']): r for r in rows}
    paired = []
    for c in CIRCUITS:
        for left, right in CONTRASTS:
            a, b = by[c, left], by[c, right]
            paired.append({'circuit': c, 'contrast': left+'-'+right,
                'gain_difference_ps': float(Decimal(str(a['wns_gain_ps']))-Decimal(str(b['wns_gain_ps']))),
                'candidate_sta_difference': a['candidate_ideal_sta']-b['candidate_ideal_sta'],
                'left_completion_sha256': a['completion_sha256'], 'right_completion_sha256': b['completion_sha256']})
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    stem = 'r24_cp_gain_cost'
    write_csv(out/(stem+'_source.csv'), rows)
    write_csv(out/(stem+'_paired.csv'), paired)
    summaries = []
    for arm in ARMS:
        selected = [by[c, arm] for c in CIRCUITS]
        summaries.append({'arm': arm, 'n_circuits': 8,
            'mean_wns_gain_ns': float(sum(Decimal(str(r['wns_gain_ns'])) for r in selected)/8),
            'mean_candidate_actual_sta': sum(r['candidate_ideal_sta'] for r in selected)/8,
            'sum_candidate_actual_sta': sum(r['candidate_ideal_sta'] for r in selected),
            'sum_evaluation_records': sum(r['candidate_evaluation_records'] for r in selected),
            'sum_retained_commits': sum(r['retained_commits'] for r in selected),
            'sec_endpoints_proven': sum(r['sec_unproven_points'] == 0 and r['sec_proven_points'] > 0 for r in selected)})
    write_csv(out/(stem+'_arm_summary.csv'), summaries)
    savings = [by[c, 'L']['candidate_ideal_sta']-by[c, 'W1']['candidate_ideal_sta'] for c in CIRCUITS]
    write_json(out/'PAIRED_SUMMARY.json', {'contrast': 'L candidate STA minus W1 candidate STA',
        'savings_by_circuit': dict(zip(CIRCUITS, savings)), 'minimum': min(savings),
        'maximum': max(savings), 'total': sum(savings),
        'W1_U1_gain_difference_all_zero': all(by[c, 'W1']['wns_gain_ps'] == by[c, 'U1']['wns_gain_ps'] for c in CIRCUITS),
        'W1_U1_candidate_sta_difference_all_zero': all(by[c, 'W1']['candidate_ideal_sta'] == by[c, 'U1']['candidate_ideal_sta'] for c in CIRCUITS)})
    write_json(out/'FIGURE_CONTRACT.json', {
        'question': '同一冻结C′运行器中，候选来源和排序对应怎样的逐电路终点收益与实际STA代价？',
        'claim': '覆盖来源相关臂达到相同改善；候选成本随政策与顺序变化，本矩阵的加权/均匀对照没有独立收益。',
        'counterevidence_retained': 'W0/U0零改善；W1/U1零差异；s641的C更省8次；s27的UR3更省5次。',
        'archetype': 'quantitative grid', 'backend': 'Python/matplotlib',
        'panel_a': '全部72终点相对于同电路共同起点的WNS改善，ps',
        'panel_b': '全部72对象的候选理想线网STA实际启动次数，不含各自一次基线STA',
        'journal_contract': 'Integration工作稿现有170mm图幅；非投稿格式验收',
        'physical_size_mm': [170, 70], 'font_floor_pt': 7,
        'reuse': 'structural adaptation; accepted data guards and palette preserved, two raw panels, cost scope changed to candidate-only',
        'statistics': '每个确定性臂一次；UR1/2/3逐种子原值；无聚合、无误差条、无显著性检验。',
        'exclusions': 0, 'displayed_observations': 72,
    })
    gain = np.array([[by[c, a]['wns_gain_ps'] for a in ARMS] for c in CIRCUITS])
    cost = np.array([[by[c, a]['candidate_ideal_sta'] for a in ARMS] for c in CIRCUITS])
    blue = LinearSegmentedColormap.from_list('gain', ['#FFFFFF', '#245B9E'])
    grey = LinearSegmentedColormap.from_list('cost', ['#FFFFFF', '#596575'])
    # Fixed 170 x 70 mm manuscript width; no tight-crop resizing.
    fig = plt.figure(figsize=(6.6929133858, 2.7559055118))
    axes = []
    for index, (x, values, cmap, title, ticks) in enumerate([
            (.085, gain, blue, 'WNS 改善（ps）', [0, 100, 200, 300, 400]),
            (.585, cost, grey, '候选实际 STA（次）', [0, 50, 100, 150, 200])]):
        ax = fig.add_axes((x, .19, .37, .50))
        axes.append(ax)
        image = ax.imshow(values, cmap=cmap, vmin=0, vmax=max(1., float(np.max(values))), aspect='auto')
        ax.set_xticks(range(9), ARMS, fontsize=7)
        ax.set_yticks(range(8), CIRCUITS, fontsize=7)
        ax.tick_params(length=0, pad=3)
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Cell edges remain un-stroked so text clearance is unambiguous.
        for i in range(8):
            for j in range(9):
                value = float(values[i, j])
                rgba = image.cmap(image.norm(value))
                luminance = .2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                ax.text(j, i, f'{value:g}', ha='center', va='center', fontsize=7,
                        color='white' if luminance < .50 else '#222222')
        cax = fig.add_axes((x+.06, .76, .31, .025))
        colorbar = fig.colorbar(image, cax=cax, orientation='horizontal', ticks=ticks)
        colorbar.ax.tick_params(labelsize=7, length=2, pad=1)
        colorbar.outline.set_linewidth(.4)
        ax.text(0, 1.39, chr(97+index), transform=ax.transAxes, fontsize=8, fontweight='bold')
        ax.text(.09, 1.39, title, transform=ax.transAxes, fontsize=7.5)
    spec = importlib.util.spec_from_file_location('figure_alignment', args.alignment_auditor)
    alignment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alignment)
    alignment.require_matplotlib_panel_alignment(fig, axes=axes, panel_ids=['a', 'b'],
        row_groups=[['a', 'b']], require_panel_labels=True,
        json_out=out/'PANEL_ALIGNMENT.json', overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    fig.savefig(out/f'{stem}.pdf', format='pdf')
    fig.savefig(out/f'{stem}.svg', format='svg')
    fig.savefig(out/f'{stem}.png', format='png', dpi=600)
    plt.close(fig)
    shutil.copyfile(__file__, out/'plotter_snapshot.py')
    shutil.copyfile(args.alignment_auditor, out/'alignment_auditor_snapshot.py')
    write_json(out/'SOURCE_BINDING.json', {
        'audit_path': args.audit.relative_to(ROOT).as_posix(), 'audit_sha256': sha(args.audit),
        'matrix_manifest_sha256': audit['manifest_sha256'], 'runtime_head': audit['head'],
        'source_completion_count': len(rows), 'plotted_objects': len(rows), 'excluded': 0,
        'candidate_actual_sta': sum(r['candidate_ideal_sta'] for r in rows),
        'candidate_evaluation_records': sum(r['candidate_evaluation_records'] for r in rows),
        'baseline_actual_sta_separate': sum(r['baseline_sta'] for r in rows),
        'total_actual_sta': sum(r['total_sta'] for r in rows),
        'matched_state_pairs16_used_as_acceptance': False,
        'data_field_mapping': {'wns_gain_ps': '(final_wns_ns-baseline_wns_ns)*1000 using Decimal',
            'candidate_ideal_sta': 'candidate_ideal_sta_launches from accepted launch ledger',
            'baseline_sta': 'baseline_sta_process_attempts; excluded only from candidate-cost metric'},
        'sources': [{'path': r['completion_path'], 'sha256': r['completion_sha256']} for r in rows],
        'rendered_exports': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()},
    })
    print(json.dumps({'output_dir': str(out), 'objects': len(rows), 'candidate_actual_sta': int(cost.sum())}))


if __name__ == '__main__':
    main()
