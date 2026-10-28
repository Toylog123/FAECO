"""New independent read-only recomputation, not recovered historical stdin.

Run from repository root. --output must name a new directory. Uses stdlib only;
no project imports, subprocesses, EDA, simulation, tests or Git operations.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import time

BASE = Path('project_docs/evidence/r22_cec_top_scope_audit_20261018/historical_objects_followup')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def identity(path):
    raw = Path(path).read_bytes()
    return {'sha256': digest(raw), 'bytes': len(raw)}

def text(path):
    return Path(path).read_bytes().decode('utf-8-sig')

def load(path):
    return json.loads(text(path))

def write(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def nonempty_lines(data):
    return '\n'.join(line.strip() for line in data.splitlines() if line.strip())

def top(data, name):
    blocks = re.findall(r'(?ms)^\s*module\s+' + re.escape(name) + r'\s*\(.*?^\s*endmodule\b', data)
    assert len(blocks) == 1, (name, len(blocks))
    return nonempty_lines(blocks[0])

def blif(path):
    source = text(path)
    logical = source.replace('\\\r\n', ' ').replace('\\\n', ' ')
    models = []
    refs = []
    for line in logical.splitlines():
        tokens = line.split('#', 1)[0].split()
        if not tokens:
            continue
        if tokens[0] == '.model':
            assert len(tokens) == 2, (path, tokens)
            models.append(tokens[1])
        if tokens[0] in ('.subckt', '.gate'):
            assert len(tokens) >= 2, (path, tokens)
            refs.append(tokens[1])
    assert len(models) == len(set(models)) and models, path
    return {'path': path, 'models_in_order': models,
            'root_models': [m for m in models if m not in set(refs)],
            'unresolved_refs': sorted(set(refs) - set(models)), 'identity': identity(path)}

def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=False, exist_ok=False)
    controls = [BASE / n for n in ['FINAL_OBJECT_AUDIT.json', 'FINAL_READ_SHA_MANIFEST.json',
                'FINAL_RECEIPT.json', 'REPORT.md', 'reproducibility_supplement/RECOVERY_RECEIPT.json']]
    audit = load(controls[0])
    expected = load(controls[1])
    assert len(expected) == 104
    observed = {p: identity(p) for p in expected}
    assert observed == expected, 'current source identity differs from retained 104-file manifest'
    before = {str(p).replace('\\', '/'): identity(p) for p in controls}
    before.update(observed)
    write(out / 'SOURCE_BEFORE.json', before)
    print('Bound 104 retained source identities; reading 15 raw CEC logs and 30 BLIFs.', flush=True)
    rows = []
    for old in audit['rows']:
        log = text(old['log'])
        # These are actual ABC result lines, not metadata status strings.
        equivalents = [s for s in log.splitlines() if re.match(r'^Networks are equivalent\b', s)]
        errors = [s for s in log.splitlines() if re.search(r'Cannot find the model for subcircuit|Reading network from file has failed', s)]
        assert not (equivalents and errors), old['log']
        commands = re.findall(r'(?m)^ABC command line: "(cec\s+.*?)"\.?\s*$', log)
        assert len(commands) == 1, (old['log'], commands)
        objects = commands[0].split()[1:]
        assert len(objects) == 2 and objects == old['command_objects'], (old['log'], objects)
        # Strip the obsolete absolute workspace prefix only for locating retained files.
        located = [s[s.index('experiments/'):] for s in objects]
        assert located == [s['path'] for s in old['retained_sides']]
        sides = [blif(s) for s in located]
        for result, old_side in zip(sides, old['retained_sides']):
            assert result['models_in_order'] == old_side['models_in_order']
        if equivalents:
            assert not errors
            assert all(len(s['models_in_order']) == 1 and len(s['root_models']) == 1 for s in sides)
            status = 'retained successful single-model CEC log'
        else:
            assert errors, old['log']
            status = 'recorded model-read error; not equivalence'
        rows.append({'log': old['log'], 'command': commands[0], 'identity': identity(old['log']),
                     'actual_equivalence_lines': equivalents, 'actual_error_lines': errors,
                     'sides': sides, 'status': status})
        print(status, old['log'], flush=True)
    assert len(rows) == 15
    assert sum(bool(r['actual_equivalence_lines']) for r in rows) == 13
    assert sum(bool(r['actual_error_lines']) for r in rows) == 2
    assert [len(s['models_in_order']) for s in rows[0]['sides']] == [378, 378]
    assert any('$mul' in line for line in rows[0]['actual_error_lines'])
    epfl = load('experiments/20260731_epfl_ctrl_sky130_mapping/cec_summary.json')['per_case'][0]['result']
    assert epfl['status'] == 'error' and epfl['returncode'] == 0
    mapping = load('experiments/20260731_epfl_ctrl_sky130_mapping/ctrl/mapping_report.json')
    assert mapping['mapped_artifacts_sha256']['mapped.blif'] == identity('experiments/20260731_epfl_ctrl_sky130_mapping/ctrl/mapping/mapped.blif')['sha256']
    assert any('clkinv' in line for line in rows[2]['actual_error_lines'])
    proofs = []
    for circuit, count in [('s27', 11), ('s820', 137)]:
        folder = Path('experiments/20260826_sec') / circuit
        script = text(folder / 'verify.ys')
        commands = [line.strip() for line in script.splitlines() if line.strip() and not line.lstrip().startswith('#')]
        for command in [f'rename {circuit} gold', f'rename {circuit} gate', 'equiv_make gold gate equiv', 'prep -top equiv', 'equiv_status']:
            assert command in commands, (circuit, command)
        assert commands.index(f'rename {circuit} gold') < commands.index(f'rename {circuit} gate') < commands.index('equiv_make gold gate equiv') < commands.index('prep -top equiv') < commands.index('equiv_status')
        assert 'equiv_status -assert' not in commands
        reads = [line.split(None, 1)[1] for line in commands if line.startswith('read_verilog ')]
        assert len(reads) == 3
        gold_path = reads[1][reads[1].index('experiments/'):]
        gate_path = reads[2][reads[2].index('experiments/'):]
        assert gold_path == f'experiments/20260826_iscas89_main/{circuit}/{circuit}/case/original/original.v'
        assert gate_path == f'experiments/20260826_sec/{circuit}/final.v'
        log = text(folder / 'verify.log')
        actual_counts = [(int(a), int(b)) for a, b in re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven', log)]
        assert actual_counts == [(count, 0)] and 'Equivalence successfully proven!' in log
        assert re.search(r'Top module:\s+\\equiv\b', log), circuit
        a_initial = f'experiments/20260805_tcad_sprint1_iscas89/{circuit}/{circuit}/mapped.v'
        a_final = f'experiments/20260807_real_pr_iscas8/{circuit}/fixed/mapped.v'
        gold_top = top(text(gold_path), circuit)
        gate_top = top(text(gate_path), circuit)
        assert gold_top == top(text(a_initial), circuit)
        assert gate_top == top(text(a_final), circuit)
        state_path = f'experiments/20260826_iscas89_main/{circuit}/{circuit}/outerloop_result.json'
        state = load(state_path)['state']
        state_hash = digest(state['current_netlist_text'].encode('utf-8'))
        assert state_hash == state['current_netlist_hash']
        assert gate_top == top(state['current_netlist_text'], circuit)
        proof = {'circuit': circuit, 'script': str(folder / 'verify.ys'), 'actual_commands': commands,
                 'log': str(folder / 'verify.log'), 'proven': count, 'unproven': 0,
                 'has_equiv_status_assert': False, 'actual_log_top_equiv': True,
                 'gold': gold_path, 'gate': gate_path, 'A_initial': a_initial, 'A_final': a_final,
                 'comparison_rule': 'circuit module body; strip line boundaries/outer spaces and discard blank lines',
                 'gold_top_equal_A_initial': True, 'gate_top_equal_A_final': True,
                 'gold_top_text_sha256': digest(gold_top.encode()), 'gate_top_text_sha256': digest(gate_top.encode()),
                 'state_file': state_path, 'state_current_netlist_sha256': state_hash,
                 'state_recorded_hash_matches': True, 'gate_top_equal_actual_B_state': True}
        proofs.append(proof)
        print('Actual explicit prep-top-equiv proof', circuit, count, 'proven / 0 unproven; A initial/final and B state bound.', flush=True)
    recovery = load(controls[-1])
    assert 'unknown' in recovery['final_adaptation_execution']['stdin_original_bytes']
    after = {p: identity(p) for p in before}
    assert after == before, 'read-only source drift'
    write(out / 'SOURCE_AFTER.json', after)
    result = {'schema': 'p08-independent-current-recheck-v1', 'client_date': '2026-10-18',
              'actual_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_s': time.monotonic() - started,
              'new_checker_not_historical_stdin': True, 'checker_identity': identity(__file__),
              'argv': sys.argv, 'cwd': str(Path.cwd()), 'no_EDA_simulation_tests_source_or_Git_operations': True,
              'retained_104_manifest_equal_current': True, 'all_read_source_identity_stable': True,
              'source_file_count_including_control_reports': len(before),
              'successful_single_model_CEC_logs': 13, 'recorded_model_read_errors': 2,
              'rows': rows, 'old_A_reused_explicit_equiv_objects': proofs,
              'epfl_status_error_despite_tool_rc0': True, 'epfl_mapped_blif_matches_mapping_receipt': True,
              'limits': ['Current independent recomputation only; historical final PowerShell stdin bytes remain unrecovered/unknown.',
                         'No contemporaneous source/normalized-BLIF SHA receipt or source commit is recovered by this check; historical overwrite remains possible.',
                         '13 retained proof objects are not 13 new experiments or independent scientific cases.',
                         'Single-model scope check is not model semantics, four-state, initialization or scientific correctness validation.',
                         'No re-review of 81 new proofs, no simulation or EDA; differently named/missing/other archived objects remain unknown; P08/OI048 historical impact stays open.']}
    write(out / 'RESULT.json', result)
    print('VERIFIED retained CEC 13+2; old A 11/0 and 137/0; source identities stable:', len(before), flush=True)
    print('RESULT_SHA256', identity(out / 'RESULT.json')['sha256'], flush=True)

if __name__ == '__main__':
    main()
