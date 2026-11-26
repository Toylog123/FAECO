#!/usr/bin/env python3
"""Stage 5 matched search on an independently routed riscv32i reference."""

import argparse
from dataclasses import asdict, replace
import fcntl
import math
from pathlib import Path
import sys
from types import SimpleNamespace

from run_v5_stage5_reference import (
    CLOCK_PS, DEFAULT_VARIANT, EVIDENCE, OPENROAD, ORFS, PDK, ROUTING, SEC, STA, TOP, VARIANTS,
    build_reference, qualify_reference,
)

for directory in ('tcad_boxed_drc_20261126', 'tcad_asap7_aes_holdout_20261125'):
    sys.path.insert(0, str(EVIDENCE / directory))

import boxed_drc
import compare_ibex as cmp
import run_qualified_wallclock as qualified
from probe_aes_selective_repair import read, verify
from run_aes_incident_priority_matched_v2 import process_ledger
from run_asap7_aes_rank_aligned import run_aligned_strategy
from run_screened_matrix import bind_runtime, raw_seconds
from run_v5_step1_power_7nm_det import SKY_CORNER_LIBS, measure_tt_power, power_delta_pct


OUT_JSON = EVIDENCE / 'tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_VERIFIED.json'
LIMIT_S = 720.0
SCREEN_LIMIT_S = 1800
SETUP_BUDGET_PCT = 1.0
SETUP_BUDGET_PS = CLOCK_PS * SETUP_BUDGET_PCT / 100.0
POOL_SIZE = 18
STRATEGIES = {
    'single_boxed': 'single_sensitivity',
    'fixed_boxed': 'fixed_online',
    'faeco_boxed': 'faeco_dedup',
}


class TimingClosedBoxedComparison(qualified.QualifiedWallclockComparison):
    def diagnose(self, actions, directory):
        return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)


def comparable_auc(accepted):
    previous_t = best = integral = 0.0
    for elapsed, gain in accepted:
        if not all(map(math.isfinite, (elapsed, gain))) or not previous_t <= elapsed <= LIMIT_S or gain <= best:
            raise ValueError('accepted Stage 5 checkpoints must strictly improve within the common window')
        integral += (elapsed - previous_t) * best
        previous_t, best = elapsed, gain
    return (integral + (LIMIT_S - previous_t) * best) / LIMIT_S


def strict_timing_failures(reference, views, clock_ps=CLOCK_PS):
    setup_budget_ps = qualified.sweep.policy.setup_budget_ps(clock_ps, SETUP_BUDGET_PCT)
    failures = []
    for corner in cmp.CORNERS:
        base, trial = reference[corner], views[corner]
        failures += qualified.sweep.policy.setup_gate_failures(
            corner, base['setup_wns_ps'], trial['setup_wns_ps'], setup_budget_ps,
            cmp.PS_TOLERANCE, protect_clean=False,
        )
        if trial['setup_wns_ps'] < 0:
            failures.append(f'{corner}:setup_floor')
        failures += qualified.sweep.policy.tns_gate_failures(
            corner, base['setup_tns_ps'], trial['setup_tns_ps'],
            qualified.sweep.policy.setup_tns_budget_ps(clock_ps, SETUP_BUDGET_PCT, base['setup_tns_ps']),
            cmp.PS_TOLERANCE,
        )
        if trial['hold_wns_ps'] < 0:
            failures.append(f'{corner}:negative_hold')
        if trial['hold_wns_ps'] < base['hold_wns_ps'] - cmp.PS_TOLERANCE:
            failures.append(f'{corner}:hold_regression')
        if trial['hold_tns_ps'] < base['hold_tns_ps'] - cmp.PS_TOLERANCE:
            failures.append(f'{corner}:hold_tns_regression')
    return failures


def next_attempt(output):
    output.mkdir(parents=True, exist_ok=True)
    attempt = output / f'attempt_{len(list(output.glob("attempt_*"))) + 1:02d}'
    attempt.mkdir()
    return attempt


def candidate_args(root, control, variant=DEFAULT_VARIANT):
    clock_ps = control['source_sdc_semantics']['period_ps']
    if clock_ps != variant.clock_ps:
        raise ValueError('qualification clock does not match the selected Stage 5 variant')
    return SimpleNamespace(
        top=TOP, pdk=PDK, clock_period_ps=clock_ps, shortest_clock_period_ps=clock_ps,
        threads=4, droute_iters=64, max_evals=1, batch_size=3, route_mode='local',
        embedded_guides=True, single_pin_access=True, report_setup_endpoints=True,
        route_guide=None, route_timeout=240., sta_timeout=180., sec_timeout=210.,
        zero_reextract=False, probe_only=False, prepare_only=True, screen_workers=1,
        openroad=OPENROAD, sta=STA, sec=SEC, orfs=ORFS, routing_config=ROUTING,
        control_dir=verify(control['control_output_paths']['odb']).parent,
        control_drc=verify(control['native_drc_report']),
        original_sdc=verify(control['source_sdc']), views_json=root / 'qualification/CONTROL.json',
        helper_source=[Path(__file__).resolve(), Path(boxed_drc.__file__).resolve(),
                       Path(run_aligned_strategy.__code__.co_filename).resolve()],
    )


def prepare_search(root, args):
    marker = root / 'search_inputs.json'
    _, assets, clock = qualified.prepare_binding(args)
    setup_budget_ps = qualified.sweep.policy.setup_budget_ps(args.clock_period_ps, SETUP_BUDGET_PCT)
    if clock['absolute_wns_loss_budget_ps'] != setup_budget_ps:
        raise ValueError('reference clock disagrees with Stage 5 budget')
    if marker.exists():
        prepared = read(marker)
        if prepared['reference_inputs'] != assets:
            raise ValueError('reference or driver changed since Stage 5 screening')
        for bound in prepared['prepared_files'].values():
            verify(bound)
    else:
        screened = next_attempt(root / 'screen')
        with process_ledger(screened / 'subprocesses.json', raw_seconds() + SCREEN_LIMIT_S):
            if qualified.run_qualified_screen(args, read(args.views_json), screened):
                raise cmp.TrialFailure('Stage 5 screening failed')
        screened = screened / 'screen'
        args.screen_pool, args.screen_receipt = screened / 'screen_pool.json', screened / 'screen_receipt.json'
        if len(read(args.screen_pool)) != POOL_SIZE:
            raise ValueError(f'expected the preregistered {POOL_SIZE} compatible screened actions')
        bindings, seconds = qualified.bind_screen_inputs(args)
        if not 0 < seconds < LIMIT_S:
            raise ValueError('screening charge exhausted the arm wall window')
        prepared_dir = next_attempt(root / 'seed') / 'checked_seed'
        seed_args = SimpleNamespace(**(vars(args) | {'out': prepared_dir}))
        rc = cmp.run(seed_args, config_overrides={
            'budget_attempts_per_arm': None, 'original_clock_period_ps': args.clock_period_ps,
            'setup_budget_ps_per_view': setup_budget_ps, 'tns_gate': True,
            'screen_inputs': bindings, 'charged_screening_seconds': seconds,
        }, extra_sources=(Path(qualified.__file__), *args.helper_source))
        if rc != 0:
            raise cmp.TrialFailure(f'qualified Stage 5 seed validation failed: {prepared_dir}')
        prepared = {
            'reference_inputs': assets, 'period_basis': clock,
            'prepared_files': {**bindings, 'seed': cmp.bind(prepared_dir / 'config.json'),
                               'baseline': cmp.bind(prepared_dir / 'control/receipt.json'),
                               'inventory': cmp.bind(prepared_dir / 'control/inventory.log'),
                               'index': cmp.bind(prepared_dir / 'control/flattened_instance_index.txt')},
        }
        cmp.save(marker, prepared)

    files = prepared['prepared_files']
    args.screen_pool, args.screen_receipt = verify(files['pool']), verify(files['receipt'])
    bindings, seconds = qualified.bind_screen_inputs(args)
    base = next_attempt(root / 'runner')
    runner = TimingClosedBoxedComparison(args, verify(files['seed']).parent, base, bindings, seconds)
    if strict_timing_failures(runner.eval.ref_views, runner.eval.ref_views, args.clock_period_ps):
        raise ValueError('live seed STA does not preserve absolute reference closure')
    runner.gate = replace(runner.gate, protect_clean=True)
    runner.config.update({
        'gate': qualified.sweep.gate_summary(runner.gate, runner.eval.ref_views),
        'period_basis': clock, 'screen_install': cmp.bind(marker), 'strategies': STRATEGIES,
        'selection': 'rank-aligned single-gate, fixed micro-batch, and FAECO scheduling under one boxed backend',
        'box_halo_rows': 1.0, 'wall_window_seconds_including_screen': LIMIT_S,
        'rank_charge_policy': 'fresh TT sensitivity rank in each arm; initial rank order equal across arms',
    })
    if len(runner.pool) != POOL_SIZE:
        raise ValueError('validator did not bind the full Stage 5 pool')
    return runner


def strict_zero(root, runner):
    marker = root / 'strict_zero.json'
    if marker.exists():
        bound = read(marker)
        if bound['scope'] != runner.eval.scope:
            raise ValueError('shared no-op refers to another seed')
        record = read(verify(bound['record']))
        endpoint = cmp.Endpoint(**record['endpoint'])
        for raw in bound['raw'].values():
            verify(raw)
    else:
        runner.use_preview = False
        endpoint = runner.qualify_zero()
        result = runner.output / 'preflight/zero/result.json'
        record = read(result)
        observed = verify(record['physical_receipt'])
        proof = observed.parent / 'sec/receipt.json'
        cmp.save(marker, {'scope': runner.eval.scope, 'record': cmp.bind(result),
                         'raw': {'physical': record['physical_receipt'], 'sec': cmp.bind(proof),
                                 'audit': cmp.bind(observed.parent / 'unlocked_drc/audit.json')}})
    if record['failures'] or not endpoint.valid or not endpoint.sec_pass:
        raise ValueError('shared no-op did not pass the protected backend')
    return endpoint


def checked_commit(reference, row, requests, evaluator):
    endpoint = row['endpoint']
    if endpoint['scope_id'] != reference.scope_id or not endpoint['valid'] or not endpoint['sec_pass']:
        raise ValueError('checkpoint lacks valid endpoint, common scope or SEC')
    final_dir = Path(endpoint['evidence_id'])
    record_path = final_dir.parent / 'result.json'
    record = read(record_path)
    request = requests.get(final_dir.parent.name)
    if (request is None or request['actions'] != record['actions'] or record['failures']
            or record['endpoint'] != endpoint or verify(record['physical_receipt']) != final_dir / 'receipt.json'):
        raise ValueError('checkpoint is not bound to an accepted dispatch and physical receipt')
    evidence = read(final_dir / 'receipt.json')
    views = evidence['views']
    if set(views) != set(cmp.CORNERS) or strict_timing_failures(evaluator.ref_views, views, evaluator.args.clock_period_ps):
        raise ValueError('accepted endpoint failed the explicit Stage 5 setup/TNS/hold conditions')
    audit = final_dir / 'unlocked_drc/audit.json'
    proof_path = final_dir / 'sec/receipt.json'
    proof = read(proof_path)
    if (read(audit)['drc_markers'] != 0 or proof['passed'] is not True or proof['proven'] <= 0
            or proof['unproven'] != 0 or proof['gate'] != evidence['artifacts']['v']
            or proof['gold'] != cmp.bind(evaluator.control['v'])):
        raise ValueError('accepted endpoint failed the raw DRC or SEC evidence check')
    verify(proof['gate'])
    return {
        'elapsed_s': row['elapsed_seconds'], 'area_saved_um2': reference.area - endpoint['area'],
        'gates': len(record['actions']), 'actions': record['actions'],
        'receipt': cmp.bind(record_path), 'physical': record['physical_receipt'], 'drc': cmp.bind(audit),
        'sec': cmp.bind(proof_path), 'sec_proven': proof['proven'], 'sec_unproven': proof['unproven'],
        'views': {c: {metric: views[c][metric] for metric in ('setup_wns_ps', 'setup_tns_ps',
                                                             'hold_wns_ps', 'hold_tns_ps')} for c in cmp.CORNERS},
    }


def run_arm(runner, reference, arm, expected_rank, ref_power):
    name = STRATEGIES[arm]
    runner.eval.args.out = runner.output
    print(f'[Stage 5] {arm} from {runner.output}', flush=True)
    summary, reuse = run_aligned_strategy(runner, name, reference, expected_rank, qualified.matrix.run_strategy)
    data = runner.output / summary['method']
    progress = read(data / 'progress.json')
    requests = {f'{row["id"]:02d}': row for row in progress['logical_requests']}
    accepted = [checked_commit(reference, row, requests, runner.eval)
                for row in progress['checkpoints'] if row['accepted']]
    auc = comparable_auc([(item['elapsed_s'], item['area_saved_um2']) for item in accepted])
    best = accepted[-1] if accepted else None
    power = None
    if best:
        physical = read(verify(best['physical']))['artifacts']
        best_power = measure_tt_power(verify(physical['odb']), verify(physical['spef']), runner.eval.control['sdc'],
                                      SKY_CORNER_LIBS['TT'], runner.output, 'best_pwr')
        power = power_delta_pct(ref_power, best_power)
    tool_ledger = data / 'subprocesses.json'
    return {
        'strategy': name, 'accepted_checkpoints': accepted,
        'qualified_gates': best['gates'] if best else 0,
        'qualified_area_saved_um2': best['area_saved_um2'] if best else 0.0,
        'final_6corner_ps': best['views'] if best else runner.eval.ref_views,
        'still_timing_closed': True, 'power_delta_pct': power, 'anytime_auc_um2': auc,
        'summary': cmp.bind(data / 'summary.json'), 'progress': cmp.bind(data / 'progress.json'),
        'tool_ledger': cmp.bind(tool_ledger), 'stage_costs': qualified.matrix.audit_tools(read(tool_ledger)),
        'logical_finished': summary['logical_finished'], 'logical_admitted': summary['logical_admitted'],
        'charged_screening_s': runner.screen, 'exact_setup_only_dedup_hits': reuse,
    }


def run_stage(root, reference_only=False, variant=DEFAULT_VARIANT):
    build = build_reference(root, variant)
    control = qualify_reference(root, build, variant)
    status = root / 'stage5_progress.json'
    control_ref = cmp.bind(root / 'qualification/CONTROL.json')
    if control['status'] != 'hold_qualified' or not control['strictly_timing_closed']:
        cmp.save(status, {'status': 'reference_not_qualified', 'qualification': control_ref,
                          'failures': control['failures'], 'arms': {}})
        return 1
    if reference_only:
        return 0

    args = candidate_args(root, control, variant)
    with bind_runtime(TOP, ROUTING), qualified.qualified_ranking(), qualified.qualified_process_clock():
        runner = prepare_search(root, args)
        protocol = root / 'search_protocol.json'
        if protocol.exists():
            if read(protocol) != runner.config:
                raise ValueError('saved Stage 5 search protocol differs from the current frozen inputs')
        else:
            cmp.save(protocol, runner.config)
        reference = strict_zero(root, runner)
        state = read(status) if status.exists() else {
            'status': 'running', 'clock_period_ps': variant.clock_ps,
            'setup_budget_ps': qualified.sweep.policy.setup_budget_ps(variant.clock_ps, SETUP_BUDGET_PCT),
            'design': f'sky130hd_riscv32i_{variant.name}_independent',
            'qualification': control_ref, 'protocol': cmp.bind(protocol), 'reference': asdict(reference),
            'screened_pool_size': len(runner.pool), 'arms': {},
        }
        if state['qualification'] != control_ref or state['protocol'] != cmp.bind(protocol):
            raise ValueError('existing Stage 5 progress differs from the current frozen inputs')
        if state['reference'] != asdict(reference):
            raise ValueError('existing Stage 5 progress differs from the strict zero')
        power_path = root / 'reference_power.json'
        if power_path.exists():
            ref_power = read(power_path)
        else:
            power_dir = next_attempt(root / 'reference_power')
            ref_odb, ref_spef = (runner.eval.control[key] for key in ('odb', 'spef'))
            ref_power = measure_tt_power(ref_odb, ref_spef, args.control_dir / '6_final.sdc',
                                         SKY_CORNER_LIBS['TT'], power_dir, 'reference')
            cmp.save(power_path, ref_power)
        expected_rank = {'order': state.get('rank_order')}
        for arm in STRATEGIES:
            if arm in state['arms']:
                existing = state['arms'][arm]
                for key in ('summary', 'progress', 'tool_ledger'):
                    verify(existing[key])
                for checkpoint in existing['accepted_checkpoints']:
                    for key in ('receipt', 'physical', 'drc', 'sec'):
                        verify(checkpoint[key])
                continue
            runner.output = next_attempt(root / 'arms' / arm)
            state['status'] = 'running'
            state['active_arm'] = {'name': arm, 'path': str(runner.output)}
            cmp.save(status, state)
            result = run_arm(runner, reference, arm, expected_rank, ref_power)
            state['arms'][arm] = result
            state['rank_order'] = expected_rank['order']
            state['active_arm'] = None
            cmp.save(status, state)
        state.update(status='finished', reference_power=cmp.bind(power_path))
        cmp.save(status, state)
        published = (OUT_JSON if variant == DEFAULT_VARIANT
                     else OUT_JSON.with_name(f'V5_STEP5_10K_TIMING_CLOSED_{variant.name.upper()}_VERIFIED.json'))
        cmp.save(published, state)
        print(f'[Stage 5] completed three arms; {published}, sha256 {cmp.sha(published)}', flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-only', action='store_true')
    parser.add_argument('--variant', choices=VARIANTS, default=DEFAULT_VARIANT.name)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--force', action='store_true', help='run from a fresh child directory')
    args = parser.parse_args()
    variant = VARIANTS[args.variant]
    root = (args.output_root or variant.output_root).resolve()
    if args.force:
        root = next_attempt(root / 'reruns')
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return run_stage(root, args.reference_only, variant)


if __name__ == '__main__':
    raise SystemExit(main())
