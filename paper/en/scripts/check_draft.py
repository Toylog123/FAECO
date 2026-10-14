"""Read-only structural/data checks for the English r21 submission draft.

Run from any directory. This does not validate scientific claims or journal fit.
It writes its evidence record only inside paper/en/submission.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
EN = ROOT / 'paper/en'
zh_path = next((ROOT / 'paper/zh/manuscript').glob('*.tex'))
en_path = EN / 'manuscript/FAECO.tex'
zh = zh_path.read_text(encoding='utf-8')
en = en_path.read_text(encoding='utf-8')
refs = (EN / 'references/references.tex').read_text(encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block(text, label):
    pos = text.index(r'\label{' + label + '}')
    start = text.rfind(r'\begin{table}', 0, pos)
    end = text.index(r'\end{table}', pos)
    return text[start:end]


def body_numbers(text):
    # Compare data rows, excluding sizing commands, headers and relocated notes.
    rows = text.split(r'\midrule', 1)[1].split(r'\bottomrule', 1)[0]
    return re.findall(r'[-+]?\d+(?:\.\d+)?', rows)


data_tables = ['tab:configs', 'tab:overview', 'tab:sec_iscas8',
               'tab:ablation', 'tab:efficiency', 'tab:runtime',
               'tab:f16_dist', 'tab:pr8', 'tab:s_boundary']
table_checks = {label: body_numbers(block(zh, label)) ==
               body_numbers(block(en, label)) for label in data_tables}
assert all(table_checks.values()), table_checks
def command_arguments(text, command):
    return re.findall(re.escape(chr(92)+command+'{')+r'([^}]+)}', text)


zh_keys = command_arguments(zh, 'bibitem')
en_keys = command_arguments(refs, 'bibitem')
assert zh_keys == en_keys and len(en_keys) == 14
zh_bib = zh[zh.index(r'\begin{thebibliography}'):zh.index(r'\end{thebibliography}')+len(r'\end{thebibliography}')]
en_bib = refs[refs.index(r'\begin{thebibliography}'):refs.index(r'\end{thebibliography}')+len(r'\end{thebibliography}')]
assert zh_bib == en_bib, 'bibliography content differs'
cited = {key for group in command_arguments(en, 'cite')
         for key in group.split(',')}
assert cited <= set(en_keys), sorted(cited - set(en_keys))
labels = command_arguments(en, 'label')
assert len(labels) == len(set(labels)), 'duplicate labels'
assert en.count(chr(92)+'begin{table}') == 14
assert en.count(chr(92)+'begin{figure}') == 7
assert not re.search('[\u3400-\u9fff]', en), 'untranslated CJK text'
assert 'AUTHOR INPUT REQUIRED' in en
highlights = [line for line in (EN / 'submission/highlights.txt').read_text(encoding='utf-8').splitlines() if line]
assert 3 <= len(highlights) <= 5
assert all(len(line) <= 85 for line in highlights)
csv_checks = {}
for stem in ['fig4_unified_gain_r21', 'fig5_budget_curves_r21',
             'fig5_sta_count_audit_r21', 'fig6_physical_transfer_r21',
             'fig7_s_boundary_r21']:
    old = ROOT / 'paper/zh/figures/data/final' / (stem + '.csv')
    new = EN / 'figures/data/final' / (stem + '.csv')
    # CSV string labels may be translated; numeric fields must agree exactly.
    def numeric_rows(path):
        result = []
        with path.open(encoding='utf-8-sig', newline='') as handle:
            for row in csv.DictReader(handle):
                nums = {}
                for key,value in row.items():
                    try:
                        nums[key] = float(value)
                    except (ValueError, TypeError):
                        pass
                result.append(nums)
        return result
    csv_checks[stem] = numeric_rows(old) == numeric_rows(new)
assert all(csv_checks.values()), csv_checks
report = {
    'scope': 'structural/data-preservation check; no EDA; no semantic or submission approval',
    'english_source_sha256': sha(en_path),
    'current_chinese_source_sha256': sha(zh_path),
    'reference_keys': en_keys, 'citation_keys': sorted(cited),
    'tables': 14, 'figures': 7, 'numeric_table_rows_match': table_checks,
    'numeric_figure_csv_rows_match': csv_checks,
    'highlights_characters': [len(line) for line in highlights],
    'abstract_words': len(en.split(chr(92)+'begin{abstract}', 1)[1].split(chr(92)+'end{abstract}', 1)[0].split()),
    'author_input_markers': en.count(r'\AuthorInput{'),
    'passed': True,
}
(EN / 'submission/draft_checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
