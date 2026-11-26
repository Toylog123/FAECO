#!/usr/bin/env python3
"""Build and qualify an independent Stage 5 reference before any candidate trials."""

import argparse
from dataclasses import asdict, dataclass
import fcntl
import os
from pathlib import Path
import re
import shlex
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


@dataclass(frozen=True)
class ReferenceVariant:
    name: str
    output_root: Path
    clock_ns: float
    io_fraction: float
    corners: tuple[str, ...] = ()
    setup_margin_ns: float = 0.0
    hold_margin_ns: float = 0.0

    @property
    def clock_ps(self):
        return self.clock_ns * 1000.0

    @property
    def stage_path(self):
        return Path(PDK, DESIGN, self.name)

    def liberty_paths(self, corner):
        return SKY_CORNER_LIBS[corner.upper()]


DEFAULT_VARIANT = ReferenceVariant(VARIANT, OUT_ROOT, CLOCK_NS, 0.2)
MMMC_VARIANT = ReferenceVariant('tc40ns_mmmc', OUT_ROOT.with_name('faeco_v5_step5_riscv32i_tc40ns_mmmc_20261126_v1'),
                                40.0, 0.05, ('tt', 'ss', 'ff'), 0.50, 0.30)
VARIANTS = {variant.name: variant for variant in (DEFAULT_VARIANT, MMMC_VARIANT)}


def render_source_sdc(source, variant=DEFAULT_VARIANT):
    replacement, count = re.subn(r'(?m)^set clk_period 6\.0$', f'set clk_period {variant.clock_ns}', source)
    if count != 1:
        raise ValueError('expected exactly one pinned 6.0 ns source period')
    if replacement.count(NATIVE_INPUT_LOOP) != 1:
        raise ValueError('unexpected riscv32i source SDC I/O expansion')
    # In the native list loop lappend is given the empty list value as its variable name.
    replacement = replacement.replace(NATIVE_INPUT_LOOP, EXPLICIT_DATA_INPUTS)
    if variant.io_fraction != DEFAULT_VARIANT.io_fraction:
        replacement, count = re.subn(r'(?m)^set clk_io_pct 0\.2$', f'set clk_io_pct {variant.io_fraction}', replacement)
        if count != 1:
            raise ValueError('expected exactly one native 0.2 I/O delay fraction')
    source_semantics(replacement, variant)
    return replacement


def source_semantics(source, variant=DEFAULT_VARIANT):
    try:
        semantics = expected_sdc(source, pinned=(variant.clock_ns, variant.io_fraction, 'clk', 'clk', 0.775),
                                 time_unit='ns')
    except RuntimeError as error:
        raise ValueError(f'unexpected riscv32i source SDC: {error}') from error
    if semantics['io_delay_sdc_units'] != 2.0:
        raise ValueError('all Stage 5 controls must use a 2 ns absolute I/O delay')
    return semantics


def orfs_timing_options(variant):
    if not variant.corners:
        return []
    return [
        'CORNERS=' + ' '.join(variant.corners),
        *[f'{corner.upper()}_LIB_FILES=' + ' '.join(variant.liberty_paths(corner)) for corner in variant.corners],
        'LIB_FILES=' + ' '.join(variant.liberty_paths('tt')),
        f'SETUP_SLACK_MARGIN={variant.setup_margin_ns:g}', f'HOLD_SLACK_MARGIN={variant.hold_margin_ns:g}',
        'SKIP_CTS_REPAIR_TIMING=0', 'SKIP_INCREMENTAL_REPAIR=0',
    ]


def validate_native_timing_logs(logs, variant):
    expected = {corner: set(variant.liberty_paths(corner)) for corner in variant.corners}
    def margin(words, flag):
        return float(words[words.index(flag) + 1]) if flag in words else None

    evidence = {}
    for stage, log in logs.items():
        seen = {}
        commands = []
        for line in log.splitlines():
            if line.startswith('read_liberty -corner '):
                _, _, corner, path = shlex.split(line)
                seen.setdefault(corner, set()).add(path)
            elif line.startswith('repair_timing '):
                words = shlex.split(line)
                if (margin(words, '-setup_margin') == variant.setup_margin_ns
                        and margin(words, '-hold_margin') == variant.hold_margin_ns
                        and not {'-setup', '-hold', '-path_group', '-allow_setup_violations'}.intersection(words)):
                    if seen != expected:
                        raise ValueError(f'{stage} dispatched repair before loading the pinned views')
                    commands.append(line)
        if seen != expected or not commands:
            raise ValueError(f'{stage} did not log the required corner loads and setup/hold repair invocation')
        evidence[stage] = {'loaded_corner_paths': {key: sorted(value) for key, value in seen.items()},
                           'commands': commands}
    return evidence


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


def build_reference(root, variant=DEFAULT_VARIANT):
    root.mkdir(parents=True, exist_ok=True)
    src_text = render_source_sdc(SOURCE_SDC.read_text(encoding='utf-8'), variant)
    work = root / 'orfs'
    sdc = root / f'constraint_{variant.name}.sdc'
    protocol = root / 'build_protocol.json'
    previous = read(protocol) if protocol.exists() else None
    if previous is not None:
        if (previous['clock_period_ps'] != variant.clock_ps or
                f'FLOW_VARIANT={variant.name}' not in previous['command']):
            raise ValueError('output root already belongs to another Stage 5 variant')
    elif work.exists():
        raise ValueError(f'ORFS artifacts have no Stage 5 protocol: {work}')
    if not sdc.exists():
        sdc.write_text(src_text, encoding='utf-8')
    elif sdc.read_text(encoding='utf-8') != src_text:
        raise ValueError(f'copied {variant.name} SDC changed; select an unused output root')
    commit = subprocess.check_output(['git', '-C', ORFS, 'rev-parse', 'HEAD'], text=True, timeout=10).strip()
    if commit != ORFS_COMMIT or cmp.sha(OPENROAD) != cmp.OPENROAD_SHA:
        raise ValueError('ORFS or pinned OpenROAD provenance mismatch')

    logs = work / 'logs' / variant.stage_path
    build_log = logs / '6_report.log'
    result_dir = work / 'results' / variant.stage_path
    control = {key: result_dir / f'6_final.{key}' for key in cmp.CONTROL_FILES}
    abc_clock = result_dir / 'clock_period.txt'
    route_json = logs / '5_2_route.json'
    route_drc = work / 'reports' / variant.stage_path / '5_route_drc.rpt'
    command = [
        'make', '--no-print-directory', '-j1', '-C', str(ORFS),
        f'DESIGN_CONFIG={DESIGN_DIR / "config.mk"}', f'WORK_HOME={work}',
        f'FLOW_VARIANT={variant.name}', f'SDC_FILE={sdc}',
        'NUM_CORES=6', f'OPENROAD_EXE={OPENROAD}', f'YOSYS_EXE={YOSYS}',
        f'ABC_CLOCK_PERIOD_IN_PS={variant.clock_ps:g}', *orfs_timing_options(variant),
        'route', str(build_log), str(control['v']), str(control['sdc']),
    ]
    initial = {
        'design': f'{PDK}/{DESIGN}', 'clock_period_ps': variant.clock_ps,
        'orfs_commit': commit, 'command': command, 'build_timeout_s': BUILD_LIMIT_S,
        'constraint_changes': [f'set physical and virtual clocks to {variant.clock_ns:g} ns via clk_period',
                               'fix empty native input list and apply 2 ns input delay to non-clock inputs',
                               'set the ABC target explicitly in ps because ORFS reads the ns SDC scalar unchanged'],
        'affinity': sorted(os.sched_getaffinity(0)),
        'inputs': [cmp.bind(path) for path in (*provenance_paths(), sdc)],
    }
    if variant.corners:
        initial['constraint_changes'].append('adjust clk_io_pct to preserve the existing 2 ns absolute I/O delays')
        initial['repair_protocol'] = {
            'phase_corners': list(variant.corners),
            'setup_margin_ns': variant.setup_margin_ns, 'hold_margin_ns': variant.hold_margin_ns,
            'checks': 'native CTS and GRT setup/hold repair including the original asynchronous reset checks',
        }
        initial['inputs'].extend(cmp.bind(ORFS / 'scripts' / name) for name in (
            'read_liberty.tcl', 'load.tcl', 'util.tcl', 'cts.tcl', 'global_route.tcl', 'final_outputs.tcl',
        ))
    if previous is not None:
        if previous != initial:
            raise ValueError('build configuration or inputs changed; select an unused output root')
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
    print(f'[Stage 5] starting ORFS {variant.name} P&R, stdout {log}', flush=True)
    result = cmp.run_process(command, log, BUILD_LIMIT_S)
    saved = {'status': 'finished' if result.returncode == 0 else 'build_failed',
             'operation': asdict(result), 'log': cmp.bind(log), 'protocol': cmp.bind(protocol)}
    if result.returncode == 0:
        changed = [item['path'] for item in initial['inputs'] if cmp.bind(Path(item['path'])) != item]
        if changed:
            raise ValueError(f'inputs changed during ORFS build: {changed}')
        if any(not path.is_file() or not path.stat().st_size for path in control.values()):
            raise ValueError(f'ORFS completed without all five final physical artifacts: {log}')
        if float(abc_clock.read_text(encoding='utf-8').strip()) != variant.clock_ps:
            raise ValueError(f'ORFS ABC target differs from the pinned clock in ps: {abc_clock}')
        saved['control_output_paths'] = {key: cmp.bind(path) for key, path in control.items()}
        saved['native_reports'] = {key: cmp.bind(path) for key, path in
                                   {'finish': build_log, 'route_json': route_json, 'route_drc': route_drc,
                                    'abc_clock_target_ps': abc_clock}.items()}
        if variant.corners:
            repair_logs = {'cts': logs / '4_1_cts.log', 'grt': logs / '5_1_grt.log'}
            saved['native_timing_repair'] = validate_native_timing_logs(
                {stage: path.read_text(encoding='utf-8') for stage, path in repair_logs.items()}, variant,
            )
            saved['native_reports'].update({f'{stage}_repair': cmp.bind(path) for stage, path in repair_logs.items()})
    cmp.save(receipt, saved)
    if result.returncode != 0:
        raise cmp.TrialFailure(f'ORFS build rc={result.returncode}: {log}')
    return saved


def qualify_reference(root, build, variant=DEFAULT_VARIANT):
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
    source = root / f'constraint_{variant.name}.sdc'
    semantics = source_semantics(source.read_text(encoding='utf-8'), variant)
    ports, extra = audit_final_sdc(control['sdc'].read_text(encoding='utf-8'), semantics)
    if variant.corners and extra:
        raise ValueError(f'new exported SDC contains unexpected constraint commands: {extra}')
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
        evaluator = cmp.Evaluator(args, control, libraries, masters, views, (), f'stage5_{variant.name}_reference')
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
    if variant.corners:
        data['flow_variant'] = variant.name
        data['native_timing_repair'] = build['native_timing_repair']
    cmp.save(saved, data)
    print(f'[Stage 5] reference {saved}, failures={data["failures"]}', flush=True)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=VARIANTS, default=DEFAULT_VARIANT.name)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    variant = VARIANTS[args.variant]
    root = (args.output_root or variant.output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        build = build_reference(root, variant)
        if args.build_only:
            return 0
        return 0 if not qualify_reference(root, build, variant)['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
