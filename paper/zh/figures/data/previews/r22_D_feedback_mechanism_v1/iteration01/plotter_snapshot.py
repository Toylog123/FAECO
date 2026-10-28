"""Two-circuit D/beam8 diagnostic; binds completed traces, never runs EDA."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import ScaledTranslation
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT/'project_docs/evidence/r22_D_revalidation_20261018/pilot_mechanism_audit'
CIRCUITS = ('s27', 's382')
FIELDS = ('boundary_penalty', 'size_penalty', 'critical_coverage_reward')
COLORS = ('#68717B', '#BE743C', '#245B9E')
mpl.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'svg.fonttype': 'none', 'pdf.fonttype': 42, 'axes.linewidth': .5,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white', 'savefig.dpi': 600})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write_csv(path, rows):
    with path.open('x', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--alignment-auditor', type=Path, required=True)
    args = parser.parse_args()
    audit_path = EVIDENCE/'actual_v2/MECHANISM_AUDIT.json'
    read_path = EVIDENCE/'actual_v2/READ_SHA_MANIFEST.json'
    receipt_path = EVIDENCE/'FINAL_RECEIPT.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    for path in (audit_path, read_path):
        if sha(path) != receipt['artifacts'][path.relative_to(EVIDENCE).as_posix()]['sha256']:
            raise ValueError('Mechanism audit no longer matches its frozen receipt')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    read_manifest = json.loads(read_path.read_text(encoding='utf-8'))
    if not (audit['frozen_completions_match_root_07'] and audit['read_sha_before_after_stable']
            and all(audit['source_matches_registered_pin'].values())):
        raise ValueError('Source audit not accepted')
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (audit_path, read_path, receipt_path)}
    weights_rows, diagnostic_rows, summary = [], [], []
    pairs = {p['circuit']: p for p in audit['paired']}
    if set(pairs) != set(CIRCUITS):
        raise ValueError('Only the two audited D/beam8 pilot circuits are allowed')
    for circuit in CIRCUITS:
        for arm in ('fixed', 'adaptive'):
            run = audit['runs'][f'D/{arm}/{circuit}']
            if run['resolved_args']['candidates_per_iteration'] != 8:
                raise ValueError('This figure is exclusively the D/beam8 diagnosis')
            for name in ('run_config.json', 'outerloop_result.json', 'eval_trials.json', 'completion.json'):
                path = ROOT/'experiments/20261018_r22_D_revalidate_v1/D'/arm/circuit/name
                rel = path.relative_to(ROOT).as_posix()
                if sha(path) != read_manifest[rel]['sha256']:
                    raise ValueError(f'Completed run artifact changed: {rel}')
                inputs[rel] = sha(path)
            if [w['round_id'] for w in run['weights_trace']] != list(range(1, 21)):
                raise ValueError('Incomplete per-round weights')
            for w in run['weights_trace']:
                values = [float(w[k]) for k in FIELDS]
                if not all(np.isfinite(values)):
                    raise ValueError('Non-finite weights')
                weights_rows.append({'circuit': circuit, 'arm': arm, 'round': w['round_id'],
                                     **{k: w[k] for k in FIELDS}})
        pair = pairs[circuit]
        if not (pair['actual_sta_launch_event_sequence_equal']
                and all(pair['trial_sequence_equal_fields'].values())):
            raise ValueError('Actual evaluation identity/STA sequence mismatch')
        if len(pair['round_pairs']) != 20 or not all(p['same_base'] for p in pair['round_pairs']):
            raise ValueError('Unmatched round bases')
        for p in pair['round_pairs']:
            diagnostic_rows.append({'circuit': circuit, 'round': p['round'],
                'order_differs_from_fixed': int(not p['dispatch_order_same']),
                'set_differs_from_fixed': int(not p['dispatch_set_same']),
                'unseen_dispatch_at_same_base': int(bool(p['adaptive_dispatch_not_offered_before_same_base'])),
                'pool_order_same': int(p['pool_order_same']), 'pool_set_same': int(p['pool_set_same']),
                'dispatch_set_same': int(p['dispatch_set_same'])})
        f, a = [audit['runs'][f'D/{arm}/{circuit}'] for arm in ('fixed', 'adaptive')]
        summary.append({'circuit': circuit, 'fixed_candidate_records': f['candidate_record_count'],
            'adaptive_candidate_records': a['candidate_record_count'], 'fixed_new_candidate_sta': f['n_new_sta_runs'],
            'adaptive_new_candidate_sta': a['n_new_sta_runs'], 'actual_sta_sequence_same': True,
            'actual_candidate_sequence_same': True, 'first_weight_change_round': a['first_changed_weights']['round_id'],
            'source_head': audit['source_head_from_registered_manifest']})
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_csv(out/'weights_all_80.csv', weights_rows)
    write_csv(out/'matched_rounds_40.csv', diagnostic_rows)
    write_csv(out/'evaluation_sequences_2.csv', summary)
    write_json(out/'INPUT_BINDINGS.json', inputs)
    stem = 'r22_D_feedback_mechanism'
    # Project preview: 170 x 135 mm, raw deterministic per-round observations.
    fig = plt.figure(figsize=(6.6929133858, 5.3149606299))
    axes = []
    for column, circuit in enumerate(CIRCUITS):
        x = .105 + column*.50
        ax = fig.add_axes((x, .63, .355, .24))
        axes.append(ax)
        rows = [w for w in weights_rows if w['circuit'] == circuit and w['arm'] == 'adaptive']
        rounds = [w['round'] for w in rows]
        for j, (field, color, linestyle, marker) in enumerate(zip(FIELDS, COLORS,
                                                ('--', '-.', '-'), ('x', 's', 'o'))):
            ax.step(rounds, [w[field] for w in rows], where='post', color=color,
                    linewidth=1.05, linestyle=linestyle)
            # Alternate exact-round markers make coincident value-1 paths visible.
            selected = list(range(j, len(rows), 4))
            ax.plot([rounds[i] for i in selected], [rows[i][field] for i in selected],
                    linestyle='none', marker=marker, color=color, markersize=3,
                    markerfacecolor='white' if marker != 'x' else color, markeredgewidth=.65)
        ax.set(xlim=(.5, 20.5), ylim=(.92, 2.08), xlabel='Search round', ylabel='In-force weight')
        ax.set_xticks([1, 5, 10, 15, 20])
        ax.set_yticks([1, 1.5, 2])
        ax.spines[['top', 'right']].set_visible(False)
        ax.tick_params(length=2.5, width=.5, pad=2)
        label_transform = ax.transAxes + ScaledTranslation(-30/72, 12/72, fig.dpi_scale_trans)
        ax.text(0, 1, chr(97+column), transform=label_transform, fontsize=9, fontweight='bold')
        ax.text(0, 1, circuit+' | EMA feedback',
                transform=ax.transAxes+ScaledTranslation(0, 12/72, fig.dpi_scale_trans), fontsize=8)
        lower = fig.add_axes((x, .285, .355, .135))
        axes.append(lower)
        dr = [r for r in diagnostic_rows if r['circuit'] == circuit]
        matrix = np.array([[r[key] for r in dr] for key in
                           ('order_differs_from_fixed', 'set_differs_from_fixed', 'unseen_dispatch_at_same_base')])
        lower.imshow(matrix, aspect='auto', interpolation='none', vmin=0, vmax=1,
                     cmap=ListedColormap(['#EEF0F3', '#245B9E']))
        lower.set_xticks([0, 4, 9, 14, 19], [1, 5, 10, 15, 20])
        lower.set_yticks([0, 1, 2], ['Order differs', 'Set differs', 'New dispatch'])
        lower.set_xlabel('Search round')
        lower.set_xticks(np.arange(-.5, 20, 1), minor=True)
        lower.set_yticks(np.arange(-.5, 3, 1), minor=True)
        lower.grid(which='minor', color='white', linewidth=.4)
        lower.tick_params(which='minor', length=0)
        lower.tick_params(length=0, pad=3)
        lower.spines[:].set_visible(False)
        transform = lower.transAxes + ScaledTranslation(-30/72, 12/72, fig.dpi_scale_trans)
        lower.text(0, 1, chr(99+column), transform=transform, fontsize=9, fontweight='bold')
        lower.text(0, 1, circuit+' | Dispatch diagnosis',
                   transform=lower.transAxes+ScaledTranslation(0, 12/72, fig.dpi_scale_trans), fontsize=8)
        s = summary[column]
        fig.text(x, .166, f"Actual candidates: {s['fixed_candidate_records']} / {s['adaptive_candidate_records']}, same order", fontsize=7)
        fig.text(x, .130, f"New candidate STA: {s['fixed_new_candidate_sta']} / {s['adaptive_new_candidate_sta']}, same sequence", fontsize=7)
    handles = [Line2D([], [], color=color, linewidth=1.1, linestyle=style, marker=marker,
                      markersize=3, label=label) for color, style, marker, label in
               zip(COLORS, ('--', '-.', '-'), ('x', 's', 'o'), ('Boundary', 'Size', 'Critical coverage'))]
    fig.legend(handles=handles, loc='center', bbox_to_anchor=(.53, .525), ncol=3,
               frameon=False, fontsize=7.5, handlelength=2.6, columnspacing=2)
    fig.text(.105, .48, 'Fixed: all three weights = 1. Coincident EMA traces are retained.', fontsize=7)
    fig.legend(handles=[Patch(facecolor='#EEF0F3', label='No'), Patch(facecolor='#245B9E', label='Yes')],
               loc='center', bbox_to_anchor=(.53, .225), ncol=2, frameon=False, fontsize=7)
    fig.text(.105, .050, 'D / beam 8; two circuits; Fixed / EMA counts. No general efficacy claim.', fontsize=7)
    spec = importlib.util.spec_from_file_location('figure_alignment', args.alignment_auditor)
    alignment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alignment)
    alignment.require_matplotlib_panel_alignment(fig, axes=axes,
        panel_ids=['a', 'c', 'b', 'd'], row_groups=[['a', 'b'], ['c', 'd']],
        column_groups=[['a', 'c'], ['b', 'd']], require_panel_labels=True,
        json_out=out/'PANEL_ALIGNMENT.json', overlay_svg=out/'PANEL_ALIGNMENT_OVERLAY.svg')
    fig.savefig(out/f'{stem}.pdf', format='pdf')
    fig.savefig(out/f'{stem}.svg', format='svg')
    fig.savefig(out/f'{stem}.png', format='png', dpi=600)
    plt.close(fig)
    (out/'plotter_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out/'alignment_auditor_snapshot.py').write_bytes(args.alignment_auditor.read_bytes())
    write_json(out/'QA_RENDER.json', {'status': 'rendered; external PDF and visual QA pending',
        'physical_size_mm': [170, 135], 'weight_rows': len(weights_rows), 'diagnostic_rows': len(diagnostic_rows),
        'subset': 'Only D/beam8 fixed/adaptive s27/s382; no other six circuits or full56 inference',
        'statistics': 'Raw deterministic traces; no sampling, smoothing, uncertainty or significance test.',
        'source_script_sha256': sha(__file__), 'alignment_auditor_sha256': sha(args.alignment_auditor),
        'outputs': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'output_dir': str(out), 'weights': len(weights_rows), 'matched_rounds': len(diagnostic_rows)}))


if __name__ == '__main__':
    main()
