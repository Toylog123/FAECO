"""Recreate the pinned plot in scratch and gate its rendered geometry before export."""
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys
import matplotlib.figure

root = Path.cwd()
tools_dir = Path.home()/'.codex/skills/nature-figure/scripts'
out = root/'scratch/r22_matrix_geometry_replay'
qa_dir = root/'paper/zh/figures/data/previews/r22_matrix_gain_cost_v1'
spec = importlib.util.spec_from_file_location('panel_alignment', tools_dir/'audit_panel_alignment.py')
alignment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment)
original = matplotlib.figure.Figure.savefig
checked = False

def guarded_save(fig, *args, **kwargs):
    global checked
    if not checked:
        alignment.require_matplotlib_panel_alignment(
            fig, axes=fig.axes[::2], panel_ids=['a', 'b', 'c', 'd'],
            row_groups=[['a', 'b'], ['c', 'd']],
            column_groups=[['a', 'c'], ['b', 'd']],
            require_panel_labels=True,
            json_out=qa_dir/'PANEL_ALIGNMENT.json',
            overlay_svg=qa_dir/'PANEL_ALIGNMENT_OVERLAY.svg')
        checked = True
    return original(fig, *args, **kwargs)

matplotlib.figure.Figure.savefig = guarded_save
plotter = root/'paper/zh/figures/data/scripts/review_r22_matrix_gain_cost.py'
sys.argv = [str(plotter), '--output-dir', str(out)]
runpy.run_path(str(plotter), run_name='__main__')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = ['r22_matrix_gain_cost'+s for s in ['.png', '_raw.csv', '_paired.csv']]
same = {name: sha(out/name) == sha(qa_dir/name) for name in files}
assert all(same.values()), same
receipt = {'plotter_sha256': sha(plotter), 'alignment_tool_sha256': sha(tools_dir/'audit_panel_alignment.py'),
           'replayed_png_and_csv_exact_match': same, 'alignment_checked_before_replay_export': checked,
           'original_figure_geometry_unchanged': True,
           'scope': 'Supplemental pre-export geometry gate; replay PNG and both CSVs byte-identical to reviewed original.'}
with (qa_dir/'GEOMETRY_REPLAY_RECEIPT.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, indent=2)
print(json.dumps(receipt))
