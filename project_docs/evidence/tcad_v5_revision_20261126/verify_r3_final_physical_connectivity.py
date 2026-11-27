#!/usr/bin/env python3
"""Verify the archived OpenROAD placement and PDN observations without EDA."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile


LABELS = ('reference', 'single_boxed', 'fixed_boxed', 'faeco_boxed')
FINAL_REQUESTS = {'single_boxed': '07', 'fixed_boxed': '06', 'faeco_boxed': '03'}
CHECKS = ('ODB_ROUTED', 'PLACEMENT', 'PSM_VDD', 'PSM_VSS')
TOOL_SHA = '2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19'


def require(condition, context):
    if not condition:
        raise ValueError(context)


def digest(data):
    return {'sha256': sha256(data).hexdigest(), 'bytes': len(data)}


def def_section(data, name):
    match = re.search(rb'(?ms)^' + name + rb'\s+(\d+)\s*;\s*\n(.*?)^END ' + name + rb'\b', data)
    require(match, f'DEF missing {name!r}')
    entries = {key: b' '.join(body.split()) for key, body in
               re.findall(rb'(?ms)^\s*-\s+(\S+)\s+(.*?)(?<!\\);\s*$', match[2])}
    require(len(entries) == int(match[1]), f'DEF entry count differs for {name!r}')
    return entries


def normalized_net(entry):
    connectors, _, routing = entry.partition(b' + ')
    terminal = re.compile(rb'\( [^()]+ \)')
    require(not terminal.sub(b'', connectors).strip(), f'unsupported DEF net syntax {connectors!r}')
    # OpenDB may reorder logical connector tuples after reimport. Compare the
    # connector set and the entire routing payload after only the lock flag.
    return sorted(terminal.findall(connectors)), re.sub(rb'(^|\+ )(FIXED|ROUTED) ', rb'\g<1>ROUTED ', routing, count=1)


def audit(archive):
    read = lambda name: json.loads(archive.read(name))
    index = read('ORIGINALS.json')
    require(sorted(archive.namelist()) == sorted([*index, 'ORIGINALS.json']), 'archive member list differs')
    for name, facts in index.items():
        require(digest(archive.read(name)) == facts, name)

    def check_binding(binding, name):
        require({field: binding[field] for field in ('bytes', 'sha256')} == index[name], name)

    protocol = read('run/protocol.json')
    results = read('run/results.json')
    state = read('stage5/state.json')
    seed = read('stage5/seed.json')
    check_binding(results['protocol'], 'run/protocol.json')
    check_binding(protocol['driver'], 'producer/check_final_odb.py')
    check_binding(protocol['old_stage5_state'], 'stage5/state.json')
    check_binding(protocol['old_stage5_seed'], 'stage5/search_protocol.json')
    check_binding(read('stage5/search_protocol.json')['seed'], 'stage5/seed.json')
    require(protocol['tool'] == seed['bindings']['tools']['openroad']
            and protocol['tool']['sha256'] == TOOL_SHA, 'frozen OpenROAD binding')
    require(results['passed'] and tuple(row['target'] for row in results['endpoints']) == LABELS,
            'four successful readbacks')

    summary = {}
    ref_def = archive.read('reference/input.def')
    reference_nets = def_section(ref_def, b'NETS')
    reference_components = def_section(ref_def, b'COMPONENTS')
    for row in results['endpoints']:
        label = row['target']
        target = protocol['input'][label]
        require(row == read(f'run/{label}/result.json') and row['passed'] and row['returncode'] == 0,
                f'{label} completion')
        check_binding(target['odb'], f'{label}/input.odb')
        check_binding(target['def'], f'{label}/input.def')
        check_binding(target['receipt'], f'{label}/original_receipt.json')
        require(row['odb_unchanged'] and row['def_unchanged'], 'original input integrity')
        for name, info in row['artifacts'].items():
            check_binding(info, f'run/{label}/{name}')

        lines = archive.read(f'run/{label}/check.tcl').decode().splitlines()
        options = row['command']
        require(options[0:5] == ['/usr/bin/timeout', '--foreground', '--kill-after=5s', '120s',
                                 protocol['tool']['path']]
                and options[5:10] == ['-no_init', '-no_splash', '-threads', '1', '-exit']
                and options[10] == row['artifacts']['check.tcl']['path'], f'{label} command line')
        commands = '\n'.join(lines)
        require(f'read_db {{{target["odb"]["path"]}}}' in lines
                and 'run_r3_check ODB_ROUTED {design_is_routed -verbose} 1' in lines
                and re.search(r'(?m)^run_r3_check PLACEMENT \[list check_placement -verbose -report_file_name \{[^}]+\}\] 0$', commands)
                and not re.search(r'\b(?:write_db|write_def|detailed_route|detailed_placement|pdngen)\b', commands),
                f'{label} immutable placement and route-status check')
        for supply in ('VDD', 'VSS'):
            require(re.search(rf'(?m)^run_r3_check PSM_{supply} \[list check_power_grid -net {supply} '
                              rf'-error_file \{{[^}}]+\}}\] 1$', commands), f'{label} strict {supply} check')
        stdout = archive.read(f'run/{label}/openroad.log').decode()
        require(tuple(re.findall(r'(?m)^R3_CHECK_PASS (\w+)$', stdout)) == CHECKS
                and row['checks'] == dict.fromkeys(CHECKS, 'pass')
                and 'R3_READ_DB_COMPLETE' in stdout and 'R3_CHECKS_COMPLETE 0' in stdout
                and not re.search(r'\[ERROR|R3_CHECK_FAIL', stdout), f'{label} check output')
        for supply in ('VDD', 'VSS'):
            require(f'[INFO PSM-0040] All shapes on net {supply} are connected.' in stdout,
                    f'{label} {supply} PSM completion')

        data = archive.read(f'{label}/input.def')
        for name in (b'PINS', b'SPECIALNETS'):
            pattern = rb'(?ms)^' + name + rb'\s+.*?^END ' + name + rb'\s*$'
            section = re.search(pattern, data)
            require(section and section.group().rstrip() == re.search(pattern, ref_def).group().rstrip()
                    and digest(section.group().rstrip()) == protocol['def_sections'][label][name.decode()],
                    f'{label} stable {name!r} section')

        summary[label] = {'odb_sha256': target['odb']['sha256'], 'psm_connected': ['VDD', 'VSS'],
                          'placement_passed': True, 'route_presence_passed': True,
                          'specialnets_and_pins_match_reference': True}
        if label == 'reference':
            check_binding(state['qualification'], f'{label}/original_receipt.json')
            qualification = read(f'{label}/original_receipt.json')
            require(all(target[k] == qualification['control_output_paths'][k] for k in ('odb', 'def')),
                    'frozen qualified reference')
            continue

        checkpoint = state['arms'][label]['accepted_checkpoints'][-1]
        require(checkpoint['physical'] == target['receipt']
                and PurePosixPath(target['receipt']['path']).parts[-3] == FINAL_REQUESTS[label],
                f'{label} last accepted checkpoint')
        original = read(f'{label}/original_receipt.json')
        require(all(original['artifacts'][key] == target[key] for key in ('odb', 'def')), f'{label} bound physical input')
        check_binding(target['old_route_log'], f'{label}/previous_route.log')
        check_binding(target['route_scope_audit'], f'{label}/previous_routing_audit.json')
        check_binding(target['independent_drc'], f'{label}/previous_independent_drc.json')
        check_binding(target['sec'], f'{label}/previous_sec.json')
        ledger = read(f'{label}/previous_subprocesses.json')
        check_binding(state['arms'][label]['tool_ledger'], f'{label}/previous_subprocesses.json')
        (operation,) = [item for item in ledger if item['log'] == target['old_route_log']['path']]
        previous_script = archive.read(f'{label}/previous_route.tcl').decode()
        previous_log = archive.read(f'{label}/previous_route.log').decode()
        require(operation['command'] == target['old_route_command'] and operation['returncode'] == 0
                and operation['command'][0] == protocol['tool']['path'] and 'detailed_route ' in previous_script
                and 'if {![design_is_routed]}' in previous_script and 'check_placement -verbose' in previous_script
                and all(marker in previous_log for marker in ('IBEX_DRT_COMPLETE', 'IBEX_RCX_COMPLETE',
                                                             'AES_SELECTIVE_ANTENNA 0', 'IBEX_ROUTE_COMPLETE'))
                and 'DRT-0206' not in previous_log, f'{label} original routing')
        candidate_drc = read(f'{label}/previous_independent_drc.json')
        candidate_sec = read(f'{label}/previous_sec.json')
        require(candidate_drc['drc_markers'] == 0 and candidate_sec['passed'] and candidate_sec['proven'] == 4559
                and candidate_sec['unproven'] == 0, f'{label} frozen qualification')

        candidate_components = def_section(data, b'COMPONENTS')
        require(candidate_components.keys() == reference_components.keys()
                and all(body.partition(b' ')[2] == reference_components[k].partition(b' ')[2]
                        for k, body in candidate_components.items()), f'{label} fixed placements')
        expected_edit = {name.lstrip('\\').encode(): cell.encode()
                         for name, cell in (edit.split('=', 1) for edit in checkpoint['actions'])}
        actual_edit = {key.lstrip(b'\\'): body.partition(b' ')[0] for key, body in candidate_components.items()
                       if body.partition(b' ')[0] != reference_components[key].partition(b' ')[0]}
        require(expected_edit == actual_edit, f'{label} exact edited masters')
        candidate_nets = def_section(data, b'NETS')
        require(candidate_nets.keys() == reference_nets.keys(), f'{label} signal net inventory')
        changed = {k.decode() for k, body in candidate_nets.items()
                   if normalized_net(body) != normalized_net(reference_nets[k])}
        route = read(f'{label}/previous_routing_audit.json')
        scope = read(f'{label}/previous_routing_scope.json')
        require(changed == set(route['changed_nets_ignoring_route_type'])
                and not changed.intersection(scope['fixed_nets'])
                and changed.issubset(route['observed_touched_nets'])
                and len(scope['fixed_nets']) == route['fixed_nets_count'],
                f'{label} unchanged protected signal geometry')
        summary[label].update({'changed_masters': len(actual_edit), 'changed_component_placements': 0,
                               'protected_nets': len(scope['fixed_nets']), 'changed_protected_nets': 0,
                               'changed_touched_nets': len(changed)})
    return {'originals': len(index), 'source_openroad_sha256': protocol['tool']['sha256'], 'ports': ['VDD', 'VSS'],
            'scope': 'Exact processor reference and three accepted SEC-fixed final ODBs', 'endpoints': summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, nargs='?',
                        default=Path(__file__).with_name('R3_FINAL_PHYSICAL_CONNECTIVITY_ORIGINALS.zip'))
    args = parser.parse_args()
    with ZipFile(args.archive) as archive:
        print(json.dumps(audit(archive), sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
