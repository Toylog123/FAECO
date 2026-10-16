"""Only process-local Liberty/batch wiring probes; never invoke EDA."""
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
import ast
import hashlib
import importlib.util
import itertools
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code/src'))
FILES = ['code/src/rseco/logic_rewrite.py', 'code/scripts/run_r22_cut_ablation.py',
         'code/src/rseco/real_wns.py', 'code/src/rseco/verilog_modules.py']
LIB_PATH = ('data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/'
            'da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')
FILES.append(LIB_PATH)
before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}
from rseco.logic_rewrite import LibCell, equivalence_candidates, parse_liberty_cells


def cell(name, data, disable, inputs, output='Z'):
    return LibCell(name, name, 1, output, data, inputs,
                   output_functions={output: data}, three_state_functions={output: disable})


def value(expression, assignment):
    tree = ast.parse(expression.replace('!', '~').strip(), mode='eval')
    assert all(isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp,
        ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert, ast.Name, ast.Load, ast.Constant))
        for node in ast.walk(tree))
    return eval(compile(tree, '<Boolean probe>', 'eval'), {'__builtins__': {}}, assignment) & 1


signatures = []
cases = [
    (cell('src1', '(A&B)', '(A)', ['A', 'B']),
     cell('dst1', '(D&E)', '(E)', ['D', 'E']), False),
    (cell('src2', '(A&B)', '(B)', ['A', 'B']),
     cell('dst2', '(E&D)', '(D)', ['E', 'D']), True),
    (cell('src3', '(!A)', '(EN)', ['A', 'EN']),
     cell('dst3', '(!D)', '(!OE)', ['D', 'OE']), False),
    (cell('src4', '(!A)', '(EN)', ['A', 'EN']),
     cell('dst4', '(!D)', '(OE)', ['D', 'OE']), True),
]
source = cell('src5', '(!A)', '(EN)', ['A', 'EN'])
target = replace(source, name='dst5', three_state_functions={})
cases.append((source, target, False))
for source, target, expected in cases:
    choices = dict(equivalence_candidates(source, {target.name: target}))
    accepted = target.name in choices
    record = {'source_data': source.function, 'source_disable': source.three_state_functions,
        'target_data': target.function, 'target_disable': target.three_state_functions,
        'expected_candidate': expected, 'actual_candidate': accepted, 'mapping': choices.get(target.name)}
    assert accepted == expected, record
    if accepted:
        mapping = choices[target.name]
        truth_rows = []
        for bits in itertools.product((0, 1), repeat=len(source.input_pins)):
            inputs = dict(zip(source.input_pins, bits))
            mapped = {mapping[pin]: signal for pin, signal in inputs.items()}
            left = (value(source.function, inputs), value(source.three_state_functions[source.output_pin], inputs))
            right = (value(target.function, mapped), value(target.three_state_functions[target.output_pin], mapped))
            assert left == right, (inputs, left, right)
            truth_rows.append({'input': inputs, 'source_data_disable': left, 'mapped_target': right})
        record['exhaustive_data_enable_rows'] = truth_rows
    signatures.append(record)

actual = parse_liberty_cells((ROOT / LIB_PATH).read_text())
plain = actual['sky130_fd_sc_hd__clkinv_1']
plain_candidates = dict(equivalence_candidates(plain, actual))
tri = actual['sky130_fd_sc_hd__einvn_1']
tri_candidates = dict(equivalence_candidates(tri, actual))
actual_controls = {
    'parsed_three_state_count': sum(len(c.three_state_functions) for c in actual.values()),
    'plain_to_tristate_candidates': [n for n in plain_candidates if actual[n].three_state_functions],
    'tristate_to_plain_candidates': [n for n in tri_candidates if not actual[n].three_state_functions],
    'einvn2_mapping': tri_candidates.get('sky130_fd_sc_hd__einvn_2'),
    'einvp_disable_raw': actual['sky130_fd_sc_hd__einvp_1'].three_state_functions,
}
assert actual_controls['parsed_three_state_count'] == 13
assert not actual_controls['plain_to_tristate_candidates']
assert not actual_controls['tristate_to_plain_candidates']
assert actual_controls['einvn2_mapping'] == {'A': 'A', 'TE_B': 'TE_B'}

spec = importlib.util.spec_from_file_location('independent_tristate_batch', ROOT / FILES[1])
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
batch._to_wsl = lambda path: Path(path).as_posix()

TOP = '''module top(A,EN,Y,Q);
input A, EN;
output Y, Q;
sky130_fd_sc_hd__einvn_1 g (.A(A), .TE_B(EN), .Z(Y));
dff seq (.CK(A), .D(A), .Q(Q));
endmodule
'''
HELPER = '''module dff(CK,D,Q);
input CK, D;
output Q;
sky130_fd_sc_hd__buf_1 g (.A(D), .X(Q));
endmodule
'''
VALID = HELPER + TOP


class ProcessBoundaryReached(Exception):
    pass


probes = []
all_cases = [
    ('legal_tristate_and_wrapper_same_named_instance', VALID, VALID, True),
    ('gold_missing_enable', VALID.replace('.TE_B(EN), ', ''), VALID, False),
    ('gate_missing_enable', VALID, VALID.replace('.TE_B(EN), ', ''), False),
    ('gate_empty_enable', VALID, VALID.replace('.TE_B(EN)', '.TE_B()'), False),
    ('gate_ordinary_empty_input', VALID, VALID.replace('.A(A)', '.A()'), False),
    ('both_helpers_missing_required_input', VALID.replace('.A(D), ', ''), VALID.replace('.A(D), ', ''), False),
    ('unknown_sky_cell', VALID, VALID.replace('einvn_1', 'unknown_cell_1'), False),
    ('wrapper_control_connected_constant', VALID.replace('.TE_B(EN)', ".TE_B(1'b0)"),
        VALID.replace('.TE_B(EN)', ".TE_B(1'b0)"), True),
]
for name, gold, gate, should_reach in all_cases:
    calls = []
    def no_eda(*args, **kwargs):
        calls.append({'command': args[0] if args else kwargs.get('args')})
        raise ProcessBoundaryReached('Stopped before actual subprocess launch')
    out = ROOT / 'scratch/r22_tristate_20261016/independent_batch_probes' / name
    error = None
    try:
        with patch.object(batch.subprocess, 'run', no_eda):
            batch.final_sec(gold, gate, 'top', out)
    except (ValueError, ProcessBoundaryReached) as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    record = {'name': name, 'expected_reach_process_boundary': should_reach,
              'reached_process_boundary': bool(calls), 'error': error}
    assert bool(calls) == should_reach, record
    if not should_reach:
        assert error and error['type'] == 'ValueError', record
        assert re.search(r'input|unknown Liberty', error['message'], re.I), record
    probes.append(record)

after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}
payload = {'schema': 'r22-tristate-independent-integration-review-v1', 'eda_executed': False,
    'scope': 'Independent logic_rewrite parser/shared signature and batch required-input wiring; RW implementation not independently certified',
    'source_before': before, 'source_after': after,
    'source_changed': [name for name in FILES if before[name] != after[name]],
    'shared_variable_mapping_probes': signatures, 'actual_liberty_controls': actual_controls,
    'final_sec_process_boundary_probes': probes,
    'boundary_limit': 'Valid cases only reached an intercepted subprocess boundary; no Yosys/ABC/OpenSTA launched and no equivalence verdict inferred.'}
OUT = ROOT / 'project_docs/evidence/r22_correctness_20261016/TRISTATE_INDEPENDENT_REVIEW.json'
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'source_changed': payload['source_changed'], 'mapping_probes': len(signatures),
    'actual_liberty_controls': actual_controls, 'batch_probes': probes}, ensure_ascii=False, indent=2))
