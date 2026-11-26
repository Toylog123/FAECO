#!/usr/bin/env python3
"""Build and qualify the Stage 5 10 ns reference before any candidate trials."""

import argparse
from dataclasses import asdict
import fcntl
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace


EVIDENCE = Path(__file__).resolve().parents[1]
for folder in ('tcad_ibex_20261123', 'tcad_holdout_20261123', 'tcad_wallclock_schedule_20261125'):
    sys.path.insert(0, str(EVIDENCE / folder))

import compare_ibex as cmp
from asap7_control.qualify_asap7_control import audit_final_sdc, expected_sdc
from probe_aes_selective_repair import read, verify
from probe_gcd_local_route_reentry import independent_physical
from run_screened_matrix import bind_runtime
from run_v5_step1_power_7nm_det import OR_BIN, SKY_CORNER_LIBS


OUT_ROOT = Path('/home/toylog/faeco_v5_step5_riscv32i_tc_20261126_v1')
HOLDOUT_ROOT = Path('/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1')
ORFS = cmp.ORFS
ORFS_COMMIT = 'da8f092a02a8e75658cc3100691aabff05f35629'
PDK = 'sky130hd'
DESIGN = 'riscv32i'
TOP = 'riscv'
VARIANT = 'tc10ns'
STAGE_PATH = Path(PDK, DESIGN, VARIANT)
CLOCK_NS = 10.0
CLOCK_PS = CLOCK_NS * 1000.0
OPENROAD = Path(OR_BIN)
YOSYS_HOME = Path('/home/toylog/faeco_eda/oss-latest')
YOSYS = YOSYS_HOME / 'bin/yosys'
STA = HOLDOUT_ROOT / 'sta_native.py'
SEC = HOLDOUT_ROOT / 'sec_native.py'
ROUTING = ORFS / 'platforms' / PDK / 'fastroute.tcl'
DESIGN_DIR = ORFS / 'designs' / PDK / DESIGN
SOURCE_SDC = DESIGN_DIR / 'constraint.sdc'
BUILD_LIMIT_S = 1800
NATIVE_INPUT_LOOP = (
    'set non_clock_inputs [list]\n'
    'foreach input [all_inputs] {\n'
    '  if { $clk_port != $input } {\n'
    '    lappend $non_clock_inputs $input\n'
    '  }\n'
    '}\n'
)
EXPLICIT_DATA_INPUTS = 'set non_clock_inputs [all_inputs -no_clocks]\n'


def render_source_sdc(source):
    replacement, count = re.subn(r'(?m)^set clk_period 6\.0$', f'set clk_period {CLOCK_NS}', source)
    if count != 1:
        raise ValueError('expected exactly one pinned 6.0 ns source period')
    if replacement.count(NATIVE_INPUT_LOOP) != 1:
        raise ValueError('unexpected riscv32i source SDC I/O expansion')
    # In the native list loop lappend is given the empty list value as its variable name.
    replacement = replacement.replace(NATIVE_INPUT_LOOP, EXPLICIT_DATA_INPUTS)
    source_semantics(replacement)
    return replacement


def source_semantics(source):
    try:
        return expected_sdc(source, pinned=(CLOCK_NS, 0.2, 'clk', 'clk', 0.775), time_unit='ns')
    except RuntimeError as error:
        raise ValueError(f'unexpected riscv32i source SDC: {error}') from error


def reference_failures(views, native_drc, native_antenna, independent, proof):
    failures = list(independent['failures'])
    if independent.get('drc') != 0 or independent.get('antenna') != 0:
        failures.append('independent_physical')
    if native_drc != 0:
        failures.append('native_drc')
    if set(native_antenna) != {'nets', 'pins'} or any(value != 0 for value in native_antenna.values()):
        failures.append('native_antenna')
    if proof.get('passed') is not True or proof.get('proven', 0) <= 0 or proof.get('unproven') != 0:
        failures.append('sec_model')
    for corner in cmp.CORNERS:
        view = views[corner]
        if min(view['setup_wns_ps'], view['setup_tns_ps']) < 0:
            failures.append(f'{corner}:negative_setup')
        if min(view['hold_wns_ps'], view['hold_tns_ps']) < 0:
            failures.append(f'{corner}:negative_hold')
        if any(view['electrical'].values()):
            failures.append(f'{corner}:absolute_electrical')
    return failures


def provenance_paths():
    return [SOURCE_SDC, DESIGN_DIR / 'config.mk', ORFS / 'Makefile',
            ORFS / 'scripts/variables.mk', ORFS / 'scripts/synth_preamble.tcl',
            *(ORFS / 'platforms' / PDK / name for name in ('config.mk', 'rcx_patterns.rules', 'setRC.tcl', 'fastroute.tcl')),
            *sorted((ORFS / 'designs/src' / DESIGN).glob('*.v')), OPENROAD, YOSYS,
            YOSYS_HOME / 'libexec/yosys', STA, SEC,
            EVIDENCE / 'tcad_holdout_20261123/holdout_tools.py',
            Path(cmp.__file__), Path(independent_physical.__code__.co_filename),
            Path(audit_final_sdc.__code__.co_filename),
            *(Path(lib) for group in SKY_CORNER_LIBS.values() for lib in group)]


def build_reference(root):
    root.mkdir(parents=True, exist_ok=True)
    src_text = render_source_sdc(SOURCE_SDC.read_text(encoding='utf-8'))
    work = root / 'orfs'
    sdc = root / 'constraint_tc10ns.sdc'
    protocol = root / 'build_protocol.json'
    if not sdc.exists():
        sdc.write_text(src_text, encoding='utf-8')
    elif sdc.read_text(encoding='utf-8') != src_text:
        raise ValueError('copied 10 ns SDC changed; select an unused output root')
    commit = subprocess.check_output(['git', '-C', ORFS, 'rev-parse', 'HEAD'], text=True, timeout=10).strip()
    if commit != ORFS_COMMIT or cmp.sha(OPENROAD) != cmp.OPENROAD_SHA:
        raise ValueError('ORFS or pinned OpenROAD provenance mismatch')

    build_log = work / 'logs' / STAGE_PATH / '6_report.log'
    result_dir = work / 'results' / STAGE_PATH
    control = {key: result_dir / f'6_final.{key}' for key in cmp.CONTROL_FILES}
    abc_clock = result_dir / 'clock_period.txt'
    route_json = work / 'logs' / STAGE_PATH / '5_2_route.json'
    route_drc = work / 'reports' / STAGE_PATH / '5_route_drc.rpt'
    command = [
        'make', '--no-print-directory', '-j1', '-C', str(ORFS),
        f'DESIGN_CONFIG={DESIGN_DIR / "config.mk"}', f'WORK_HOME={work}',
        f'FLOW_VARIANT={VARIANT}', f'SDC_FILE={sdc}',
        'NUM_CORES=6', f'OPENROAD_EXE={OPENROAD}', f'YOSYS_EXE={YOSYS}',
        f'ABC_CLOCK_PERIOD_IN_PS={CLOCK_PS:g}',
        'route', str(build_log), str(control['v']), str(control['sdc']),
    ]
    initial = {
        'design': f'{PDK}/{DESIGN}', 'clock_period_ps': CLOCK_PS,
        'orfs_commit': commit, 'command': command, 'build_timeout_s': BUILD_LIMIT_S,
        'constraint_changes': ['set physical and virtual clocks to 10 ns via clk_period',
                               'fix empty native input list and apply 2 ns input delay to non-clock inputs',
                               'set the ABC target explicitly in ps because ORFS reads the ns SDC scalar unchanged'],
        'affinity': sorted(os.sched_getaffinity(0)),
        'inputs': [cmp.bind(path) for path in (*provenance_paths(), sdc)],
    }
    if protocol.exists():
        if read(protocol) != initial:
            raise ValueError('build configuration or inputs changed; select an unused output root')
    elif work.exists():
        raise ValueError(f'ORFS artifacts have no Stage 5 protocol: {work}')
    else:
        cmp.save(protocol, initial)

    receipt = root / 'build_receipt.json'
    if receipt.exists() and read(receipt)['status'] == 'finished':
        saved = read(receipt)
        for asset in (*saved['control_output_paths'].values(), *saved['native_reports'].values()):
            verify(asset)
        return saved

    # Preserve every prior timeout stdout and permit make to resume the same input-bound build.
    run_number = len(list(root.glob('orfs_build_*.log'))) + 1
    log = root / f'orfs_build_{run_number:02d}.log'
    print(f'[Stage 5] starting ORFS 10 ns P&R, stdout {log}', flush=True)
    result = cmp.run_process(command, log, BUILD_LIMIT_S)
    saved = {'status': 'finished' if result.returncode == 0 else 'build_failed',
             'operation': asdict(result), 'log': cmp.bind(log), 'protocol': cmp.bind(protocol)}
    if result.returncode == 0:
        changed = [item['path'] for item in initial['inputs'] if cmp.bind(Path(item['path'])) != item]
        if changed:
            raise ValueError(f'inputs changed during ORFS build: {changed}')
        if any(not path.is_file() or not path.stat().st_size for path in control.values()):
            raise ValueError(f'ORFS completed without all five final physical artifacts: {log}')
        if float(abc_clock.read_text(encoding='utf-8').strip()) != CLOCK_PS:
            raise ValueError(f'ORFS ABC target differs from the 10 ns clock in ps: {abc_clock}')
        saved['control_output_paths'] = {key: cmp.bind(path) for key, path in control.items()}
        saved['native_reports'] = {key: cmp.bind(path) for key, path in
                                   {'finish': build_log, 'route_json': route_json, 'route_drc': route_drc,
                                    'abc_clock_target_ps': abc_clock}.items()}
    cmp.save(receipt, saved)
    if result.returncode != 0:
        raise cmp.TrialFailure(f'ORFS build rc={result.returncode}: {log}')
    return saved


def qualify_reference(root, build):
    out = root / 'qualification'
    control = {kind: verify(item) for kind, item in build['control_output_paths'].items()}
    saved = out / 'CONTROL.json'
    if saved.exists():
        data = read(saved)
        if data['build_receipt'] != cmp.bind(root / 'build_receipt.json'):
            raise ValueError('qualification receipt refers to another ORFS run')
        return data
    out.mkdir(exist_ok=True)
    trial = out / f'attempt_{len(list(out.glob("attempt_*"))) + 1:02d}'
    trial.mkdir()
    source = root / 'constraint_tc10ns.sdc'
    semantics = source_semantics(source.read_text(encoding='utf-8'))
    ports, extra = audit_final_sdc(control['sdc'].read_text(encoding='utf-8'), semantics)
    native = {key: verify(item) for key, item in build['native_reports'].items()}
    routing = read(native['route_json'])
    net_drc = routing['detailedroute__route__drc_errors']
    antenna = {key: routing[f'detailedroute__antenna__violating__{key}'] for key in ('nets', 'pins')}
    rcx = re.findall(r'(?m)^\[INFO RCX-0045\] Extract (\d+) nets, (\d+) rsegs, (\d+) caps, (\d+) ccs$',
                     native['finish'].read_text(encoding='utf-8'))
    if len(rcx) != 1 or any(int(n) <= 0 for n in rcx[0]):
        raise ValueError('native finalization did not certify extracted coupling parasitics')
    libraries = {corner: [Path(lib) for lib in files] for corner, files in SKY_CORNER_LIBS.items()}
    args = SimpleNamespace(openroad=OPENROAD, sta=STA, sta_timeout=180.0,
                           report_setup_endpoints=True, sec=SEC, sec_timeout=210.0, pdk=PDK)
    operations = {}
    with bind_runtime(TOP, ROUTING):
        views = cmp.describe_sta(args, libraries, control['v'], control['sdc'], control['spef'], trial, operations)
        coverage_ok = all(ports['input'] == set(view['ports']['INPUT']) - {semantics['clock_port']} and
                          ports['output'] == set(view['ports']['OUTPUT']) for view in views.values())
        physical = independent_physical(SimpleNamespace(args=args), build['control_output_paths'], trial / 'independent')
        masks = cmp.liberty_areas(libraries['TT'])
        masters = cmp.logical_masters(control['v'], masks)
        evaluator = cmp.Evaluator(args, control, libraries, masters, views, (), 'stage5_tc10ns_reference')
        proof_ok = evaluator.proof(control['v'], trial, operations)
    proof_log = trial / 'sec/receipt.json'
    proof = read(proof_log) if proof_log.is_file() else {}
    failures = reference_failures(views, net_drc, antenna, physical, proof)
    if not coverage_ok:
        failures.append('source_sdc_missing_expanded_io')
    if native['route_drc'].stat().st_size:
        failures.append('native_drc_report_nonempty')
    if not proof_ok or not all(proof.get(key) == build['control_output_paths']['v'] for key in ('gold', 'gate')):
        failures.append('sec_control_binding')
    timing_closed = not any(reason.endswith((':negative_setup', ':negative_hold')) for reason in failures)
    for item in (*build['control_output_paths'].values(), *build['native_reports'].values()):
        verify(item)

    data = {
        'design': DESIGN, 'top': TOP, 'platform': PDK,
        'status': 'hold_qualified' if not failures else 'qualification_incomplete',
        'strictly_timing_closed': timing_closed, 'failures': sorted(set(failures)),
        'all_views_nonnegative_hold': not any(reason.endswith(':negative_hold') for reason in failures),
        'build_receipt': cmp.bind(root / 'build_receipt.json'), 'control_output_paths': build['control_output_paths'],
        'raw_reports': list(build['native_reports'].values()), 'native_drc_report': build['native_reports']['route_drc'],
        'source_sdc': cmp.bind(source), 'views': views, 'operations': operations,
        'source_sdc_semantics': {**semantics, 'source_io_matches_all_nonclock_inputs_and_outputs': coverage_ok,
                                 'expanded_port_counts': {key: len(value) for key, value in ports.items()},
                                 'other_exported_set_commands': extra},
        'library_paths': {name: list(map(str, files)) for name, files in libraries.items()},
        'view_liberty_groups': {name: [cmp.bind(lib) for lib in files] for name, files in libraries.items()},
        'sta_binary': cmp.bind(STA),
        'native_rcx': dict(zip(('nets', 'rsegs', 'caps', 'couplings'), map(int, rcx[0]))),
        'detailed_route_drc_count': net_drc, 'native_antenna': antenna, 'independent': physical,
        'sec': cmp.bind(proof_log) if proof_log.is_file() else None,
        'logical_cell_count': len(masters), 'logical_cell_area_um2': evaluator.ref_area,
    }
    cmp.save(saved, data)
    print(f'[Stage 5] reference {saved}, failures={data["failures"]}', flush=True)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=OUT_ROOT)
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        build = build_reference(root)
        if args.build_only:
            return 0
        return 0 if not qualify_reference(root, build)['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
