"""Repair the two placeholder artefacts left by the first patch attempt.

The patch script built the new helper function with a plain string literal, so
the `{MARK}` marker and the `{{}}` escapes were written out literally instead of
being substituted.  Only the two three-point-curve tools contain that block;
build_training_table.py and make_dataset_card.py were patched with plain
literals and are untouched by this repair.

The repair is text-only and asserted: if the expected pattern is not found the
script refuses to write.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = '# --- cumulative-reading fix (LOG-20261024-27) ---'

TARGETS = [
    REPO / 'experiments/20261024_physical_labels_itc99/tools/three_point_curve_itc99.py',
    REPO / 'experiments/20260826_never/does_not_exist.py',   # placeholder, skipped
    REPO / 'experiments/20261024_physical_labels/tools/three_point_curve.py',
]


def main():
    report = {}
    for p in TARGETS:
        if not p.exists():
            report[str(p.name)] = 'missing (skipped)'
            continue
        text = p.read_text(encoding='utf-8')
        n_mark = text.count('{MARK}')
        n_braces = text.count('{{}}')
        if n_mark == 0 and n_braces == 0:
            report[p.name] = 'clean'
            continue
        if n_mark != 1:
            raise SystemExit(f'REPAIR FAILED {p.name}: {n_mark} markers')
        text = text.replace('{MARK}', MARKER, 1)
        text = text.replace('{{}}', '{}')
        p.write_text(text, encoding='utf-8', newline='\n')
        report[p.name] = f'repaired (markers={n_mark}, braces={n_braces})'

    # the patch script itself must not emit the placeholders again
    ps = REPO / 'scratch/patch_cumulative_reading.py'
    if ps.exists():
        t = ps.read_text(encoding='utf-8')
        if "{MARK}" in t:
            t = t.replace("LEDGER_FN = '''\n\n{MARK}", "LEDGER_FN = '''\n\n__MARK__")
            t = t.replace("{{}}", "{}")
            t = t.replace("__MARK__", "{MARK}")
            ps.write_text(t, encoding='utf-8', newline='\n')
            report['patch_cumulative_reading.py'] = 'repaired'
        else:
            report['patch_cumulative_reading.py'] = 'clean'

    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
