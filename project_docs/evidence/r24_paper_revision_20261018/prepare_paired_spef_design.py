"""Read-only static preparation; no EDA/tool process is started except git identity reads."""
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.logic_rewrite import parse_liberty_cells
from rseco.real_wns import (validate_cell_input_connections,
    two_state_sec_unsupported_reason, build_boundary_closure_checker)
from rseco.spef import parse_mapped_verilog, build_spef

EXPECTED_HEAD = 'f761ee1996a83fc4f0f3de0999b74d85a8237858'
LIB = ROOT / 'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
CP = ROOT / 'experiments/20261016_r22_cut_ablation_v3/W1/s382'
SOURCE_PATHS = sorted((ROOT / 'code/src/rseco').glob('*.py')) + [
    ROOT / 'code/scripts/run_parasitic_aware_check.py', ROOT / 'code/scripts/run_with_timeout.sh', LIB]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def record(path):
    raw = path.read_bytes()
    return {'path': str(path.resolve()), 'relative_path': path.relative_to(ROOT).as_posix(),
            'sha256': sha(raw), 'bytes': len(raw)}

def write_new(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return record(path)

def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, timeout=30,
                       text=True, encoding='utf-8', errors='strict')
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()

head = git('rev-parse', 'HEAD')
assert head == EXPECTED_HEAD
assert not git('status', '--porcelain', '--untracked-files=all', '--', 'code')
before = [record(p) for p in SOURCE_PATHS]
libtext = LIB.read_text(encoding='utf-8')
cells = parse_liberty_cells(libtext)
pairs = {
    'old_scan_not_selected': [ROOT / 'experiments/20260804_outerloop_decision/s382_beam1_early/s382/mapped.v', ROOT / 'experiments/20260804_outerloop_decision/s382_beam1_early/s382/eval/iter002_cand002/005__071__R/mapped.v'],
    'Cprime_W1_selected': [CP / 'final_sec/initial_raw.v', CP / 'final_sec/final_raw.v'],
}
prechecks = []
used = set()
for name, paths in pairs.items():
    texts = [p.read_text(encoding='utf-8-sig') for p in paths]
    sides = []
    for path, text in zip(paths, texts):
        validate_cell_input_connections(text, cells)
        unsupported = two_state_sec_unsupported_reason(text, cells)
        assert unsupported is None
        netlist = parse_mapped_verilog(path, liberty_text=libtext, top_module='s382')
        spef = build_spef(netlist, unit_len_um=40)
        scopes = sorted(set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+[^\s(]+\s*\(', text)))
        if name == 'Cprime_W1_selected':
            used.update(scopes)
        sides.append({**record(path), 'decoded_utf8_sig_universal_newline_sha256': sha(text.encode()),
            'required_input_validation': 'pass', 'two_state_unsupported_reason': unsupported,
            'spef_static_generation': 'pass', 'spef40_utf8_sha256': sha(spef.encode()),
            'net_count': len(netlist.nets), 'ports': netlist.ports, 'port_directions': netlist.port_dirs,
            'used_actual_Liberty_types': scopes})
    closure = asdict(build_boundary_closure_checker(top_module='s382', liberty_text=libtext)(*texts))
    assert closure['status'] == 'pass'
    prechecks.append({'pair': name, 'sides': sides, 'F2': closure})
modelscope = write_new('PAIRED_SPEF_MODEL_SCOPE.json', {
    'purpose': 'Actual TT Liberty metadata consumed by current parser; not a new SEC proof model',
    'liberty': record(LIB), 'models': {name: asdict(cells[name]) for name in sorted(used)},
    'retained_Cprime_SEC_model': record(CP / 'final_sec/cells.v')})
completion = json.loads((CP / 'completion.json').read_text())
sec = json.loads((CP / 'final_sec/result.json').read_text())
sec_log = (CP / 'final_sec/sec.log').read_text()
for key, expected in completion['evidence_receipt'].items():
    assert sha((CP / key).read_bytes()) == expected
assert sec['status'] == 'pass' and sec['returncode'] == 0
assert sha((CP / 'final_sec/initial_raw.v').read_bytes()) == sec['initial_sha256']
assert sha((CP / 'final_sec/final_raw.v').read_bytes()) == sec['final_sha256']
counts = tuple(map(int, re.search(r'Of those cells (\d+) are proven and (\d+) are unproven', sec_log).groups()))
assert counts[0] > 0 and counts[1] == 0
result = json.loads((CP / 'outerloop_result.json').read_text())
assert sha((CP / 'final_sec/final_raw.v').read_text(encoding='utf-8-sig').encode()) == result['state']['current_netlist_hash']
matrix = ROOT / 'project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json'
matrix_data = json.loads(matrix.read_text())
assert matrix_data['all_matrix_verified'] and matrix_data['source_stable']
assert sha((CP / 'completion.json').read_bytes()) in json.dumps(matrix_data['eligible_completion_sha256'])
precheck_record = write_new('PAIRED_SPEF_STATIC_PRECHECK.json', {
    'scope': 'Static parsing/Liberty/F2/SPEF text generation only; not new SEC/STA',
    'EDA_started': False, 'head': head, 'pairs': prechecks,
    'selected_exact_SEC_binding': {'result': record(CP / 'final_sec/result.json'),
        'script': record(CP / 'final_sec/sec.ys'), 'log': record(CP / 'final_sec/sec.log'),
        'completion': record(CP / 'completion.json'), 'matrix_audit72': record(matrix),
        'retained_proven': counts[0], 'retained_unproven': counts[1],
        'endpoint_decoded_sha256': result['state']['current_netlist_hash'],
        'historical_baseline_wns': completion['baseline_wns'], 'historical_final_wns': completion['final_wns'],
        'all_completion_artifact_bytes_match': True},
    'old_scan_decision': 'Current static support passes, but old shared-SPEF has retained SLEEP missing-pin warnings and exact pair SEC binding was not found in scoped evidence search; select accepted Cprime pair instead.',
    'source_before': before, 'source_after': [record(p) for p in SOURCE_PATHS]})
assert before == [record(p) for p in SOURCE_PATHS]
runner = ROOT / 'code/scripts/run_parasitic_aware_check.py'
initial, final = pairs['Cprime_W1_selected']
jobs = []
for name, length, repaired in [('control_same_u40', 40, initial), ('pair_u10', 10, final), ('pair_u40', 40, final), ('pair_u160', 160, final)]:
    output = OUT / 'paired_spef_runs' / name
    assert not output.exists()
    argv = [sys.executable, str(runner), '--baseline', str(initial), '--repaired', str(repaired),
            '--period', '0.5', '--top', 's382', '--clock-port', 'CK', '--unit-len-um', str(length),
            '--output-dir', str(output)]
    jobs.append({'name': name, 'length_um': length, 'baseline': record(initial), 'repaired': record(repaired),
        'argv': argv, 'cwd': str(ROOT), 'output_dir': str(output), 'outer_case_timeout_s': 600,
        'expected_API_STA_processes': 4, 'annotation_replay_after_API': [
            {'side': side, 'base_tcl': str(output / (side + '_spef') / 'sta.tcl'),
             'annotation_tcl': str(output / (side + '_spef') / 'annotation.tcl'),
             'append_only_tcl_command': 'report_parasitic_annotation -report_unannotated',
             'argv': ['wsl.exe', '-d', 'Ubuntu', '--', '/usr/local/bin/sta', '-no_splash', '-exit',
                      '/mnt/d/' + (output / (side + '_spef') / 'annotation.tcl').relative_to(Path('D:/')).as_posix()],
             'timeout_s': 60} for side in ['baseline', 'repaired']]})
design = {
    'schema': 'r24-fresh-paired-SPEF-design-v1', 'created_UTC': datetime.now(timezone.utc).isoformat(),
    'status': 'prepared_pending_root_review_no_EDA_started', 'head': head,
    'family': 'Fresh current-f761 simplified-SPEF posterior on exact accepted Cprime-W1/s382 endpoints',
    'not_historical_recovery': True, 'not_new_search': True, 'not_real_geometry_or_signoff': True,
    'input_origin_runtime_head': '3ea0f757f5e9bab4a2df75c458b0c665eabcb258',
    'python_executable': str(Path(sys.executable).resolve()), 'sources': before,
    'model_scope': modelscope, 'static_precheck': precheck_record,
    'RC': {'lengths_um': [10, 40, 160], 'reason': 'Three explicit load settings with ideal measurements separately at every setting; unit0 is rejected by unchanged production CLI.',
           'formula': 'L=unit_len_um*max(1,sqrt(fanout))*fanout_penalty*depth_penalty',
           'fanout_penalty': 1, 'depth_penalty': 1, 'r_ohm_per_um': 0.09, 'c_ff_per_um': 0.21,
           'C_SPEF_unit': 'pF', 'R_SPEF_unit': 'ohm', 'geometry': 'none; load surrogate only'},
    'timing': {'period_ns': 0.5, 'clock_port': 'CK', 'corner': 'tt_025C_1v80',
               'explicit_IO_delays': False, 'baseline_candidate_same_settings': True},
    'experiment_global_timeout_s': 1800, 'case_outer_timeout_s': 600,
    'existing_runner_inner_STA_timeout_s': 600, 'annotation_timeout_s': 60,
    'serial': True, 'API_STA_attempt_upper_bound': 16, 'annotation_replay_upper_bound': 8,
    'total_scientific_STA_launch_upper_bound': 24, 'jobs_in_order': jobs,
    'runtime_tool_pin': {'expected_from_accepted_tiny_pilot': {'version': '3.1.0', 'binary': '/usr/local/bin/sta',
        'sha256': '96833cf69282803fc44fc8cc343bfe03ad8279bab9fb276d84a6d4532e15b468'},
        'must_verify_before_first_measurement': True, 'identity_query_timeout_s': 30},
    'accepted_tiny_pilot': [record(ROOT / 'project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding' / n) for n in ['ROOT_ACCEPTANCE.json', 'RESULT.json', 'independent_review/REVIEW.md']],
    'pass_or_abort_rules': ['Before each case and after run, actual HEAD, all pinned source/input/model/Liberty hashes must match.',
        'Retain every launch intent, actual child process launch, raw stdout/stderr, returncode, original Tcl/log/receipt and elapsed time.',
        'Each API measurement valid=true, finite WNS, returncode=0; Tcl read_spef precedes all timing reports for annotated modes.',
        'Each annotation replay uses unchanged original Tcl plus one annotation report; no missing pin/unknown instance/error; zero unannotated and zero partially unannotated drivers required.',
        'Retain API WNS and replay WNS separately; replay must match API at printed precision.',
        'Same-netlist control requires both ideal and SPEF delta exactly0 at printed precision and equal side SPEF bytes; otherwise stop before scan.',
        'At least one baseline or candidate WNS/slack must distinguish ideal versus SPEF or length10 versus160, else injection sensitivity is inconclusive, no claimed load effect.',
        'Preserve zero gains and regressions; no parameter tuning to obtain a positive result.',
        'On timeout/error/source change, stop and inspect retained logs; no blind retry, replacement input or automatic continuation.',
        'No old artifact/source/HEAD changes; all new results remain under this evidence folder.'],
    'claim_scope': 'One exact accepted Cprime endpoint pair under an explicit simplified wire-load model; no historical F6 recovery, general method efficacy, actual routed RC or physical PPA gain claim.',
}
assert git('rev-parse', 'HEAD') == head and before == [record(p) for p in SOURCE_PATHS]
record_out = write_new('PAIRED_SPEF_DESIGN.json', design)
print(json.dumps({'design': record_out, 'model_scope': modelscope, 'precheck': precheck_record,
                  'EDA_started': False, 'source_stable': True}, ensure_ascii=False, indent=2))
