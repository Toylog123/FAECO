"""Static, conservative candidate-space inventory; never invokes EDA."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib
import importlib.util
import json
import re

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = HERE.parents[3]
LIB = ROOT / 'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
BRACES = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/|[{};]', re.S)
CELL = re.compile(r'\bcell\s*\(\s*"([^"]+)"\s*\)\s*\{')
IGNORED_PIN_ATTRIBUTES = {
    'capacitance', 'rise_capacitance', 'fall_capacitance',
    'rise_capacitance_range', 'fall_capacitance_range', 'max_capacitance',
    'min_capacitance', 'max_transition', 'min_transition', 'max_fanout',
    'min_fanout', 'fanout_load', 'drive_current', 'output_voltage', 'input_voltage',
}
IGNORED_CELL_ATTRIBUTES = {'area', 'cell_leakage_power', 'driver_waveform_fall', 'driver_waveform_rise'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def close_brace(text, start):
    depth = 1
    for token in BRACES.finditer(text, start):
        if token.group() == '{':
            depth += 1
        elif token.group() == '}':
            depth -= 1
            if depth == 0:
                return token.start(), token.end()
    raise ValueError('Unterminated Liberty group')


def items(body):
    """Parse top-level attributes and groups without matching nested attributes."""
    attrs, groups = {}, []
    pos = 0
    while pos < len(body):
        match = BRACES.search(body, pos)
        if match is None:
            if body[pos:].strip():
                raise ValueError('Unparsed Liberty tail: ' + body[pos:pos+100])
            break
        token = match.group()
        if token.startswith(('//', '/*')):
            if body[pos:match.start()].strip():
                raise ValueError('Unexpected comment inside statement')
            pos = match.end()
            continue
        if token.startswith('"'):
            # Locate the statement delimiter, skipping quoted text/comments.
            search = match.end()
            while True:
                match = BRACES.search(body, search)
                if match is None:
                    raise ValueError('No statement delimiter')
                token = match.group()
                if token in ('{', '}', ';'):
                    break
                search = match.end()
        prefix = body[pos:match.start()].strip()
        if token == '{':
            header = re.fullmatch(r'(\w+)\s*\((.*)\)', prefix, re.S)
            if not header:
                raise ValueError('Unsupported group header: ' + prefix)
            end, nextpos = close_brace(body, match.end())
            groups.append((header.group(1), header.group(2).strip(), body[match.end():end]))
            pos = nextpos
        elif token == ';':
            scalar = re.fullmatch(r'(\w+)\s*:\s*(.*)', prefix, re.S)
            complex_attr = re.fullmatch(r'(\w+)\s*(\(.*\))', prefix, re.S)
            parsed = scalar or complex_attr
            if not parsed or parsed.group(1) in attrs:
                raise ValueError('Unsupported/duplicate attribute: ' + prefix)
            attrs[parsed.group(1)] = parsed.group(2).strip()
            pos = match.end()
        else:
            raise ValueError('Unexpected close brace')
    return attrs, groups


def parse_cells(text, used_families):
    cells = {}
    observed_pin_attributes = set()
    for match in CELL.finditer(text):
        name = match.group(1)
        if re.sub(r'_\d+$', '', name) not in used_families:
            continue
        end, _ = close_brace(text, match.end())
        attrs, groups = items(text[match.end():end])
        pins, pgpins, states = {}, {}, []
        for kind, arguments, body in groups:
            if kind in ('pin', 'pg_pin'):
                pin = arguments.strip('"')
                pa, subgroups = items(body)
                if kind == 'pin':
                    observed_pin_attributes.update(pa)
                    assert 'direction' in pa, (name, pin)
                    assert all(g[0] in ('timing', 'internal_power') for g in subgroups), (name, pin)
                    pins[pin] = {k: v for k, v in sorted(pa.items()) if k not in IGNORED_PIN_ATTRIBUTES}
                else:
                    assert not subgroups, (name, pin)
                    pgpins[pin] = dict(sorted(pa.items()))
            elif kind in ('ff', 'latch', 'ff_bank', 'latch_bank', 'statetable'):
                sa, sg = items(body)
                assert not sg, (name, kind)
                states.append({'kind': kind, 'state_variables': arguments, 'all_attributes': dict(sorted(sa.items()))})
            else:
                assert kind == 'leakage_power', (name, kind)
        assert name not in cells
        family_match = re.fullmatch(r'(.+)_(\d+)', name)
        sig = {'pins': dict(sorted(pins.items())), 'pg_pins': dict(sorted(pgpins.items())),
               'state_groups': states, 'cell_attributes': {k: v for k, v in sorted(attrs.items()) if k not in IGNORED_CELL_ATTRIBUTES}}
        cells[name] = {'area': Decimal(attrs['area']), 'family': family_match.group(1) if family_match else name,
                       'drive_suffix': int(family_match.group(2)) if family_match else None, 'signature': sig}
    return cells, sorted(observed_pin_attributes)


def main():
    reader_path = PKG / 'structure_reader.py'
    spec = importlib.util.spec_from_file_location('space_structure', reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    control_path, recipe_path = PKG / 'inputs/CONTROL/routed.v', PKG / 'inputs/recipe.json'
    source_paths = [control_path, recipe_path, LIB, reader_path, Path(__file__)]
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in source_paths}
    design, _ = reader.Reader(control_path.read_text(encoding='utf-8')).parse()
    used_families = {re.sub(r'_\d+$', '', x['cell']) for x in design['instances'].values()}
    cells, pin_attrs = parse_cells(LIB.read_text(encoding='utf-8'), used_families)
    recipe = json.loads(recipe_path.read_text(encoding='utf-8'))['applied']
    pairs = {(x['instance'], x['old_cell']) for x in recipe}
    recipe_instances = {x['instance'] for x in recipe}
    taps, inventory, candidates, rejections = [], [], [], []
    for inst, entry in sorted(design['instances'].items()):
        if entry['cell'] == 'sky130_fd_sc_hd__tapvpwrvgnd_1' and not entry['pins']:
            taps.append(inst)
            continue
        assert entry['cell'] in cells, entry
        source = cells[entry['cell']]
        assert set(entry['pins']) <= set(source['signature']['pins']), (inst, entry['pins'], source['signature']['pins'])
        missing_pins = sorted(set(source['signature']['pins']) - set(entry['pins']))
        assert all(source['signature']['pins'][p]['direction'].strip('"') == 'output' for p in missing_pins), (inst, missing_pins)
        if source['signature']['state_groups']:
            category = 'sequential'
        elif re.search(r'__(clkbuf|clkinv)$', source['family']):
            category = 'clock_family'
        else:
            category = 'combinational_other'
        inventory.append({'instance': inst, 'cell': entry['cell'], 'category': category,
                          'area': str(source['area']), 'pins': entry['pins'], 'unconnected_output_pins': missing_pins,
                          'signature_sha256': digest(source['signature'])})
        for target_name, target in sorted(cells.items()):
            if source['family'] != target['family'] or target['area'] >= source['area']:
                continue
            row = {'instance': inst, 'source_cell': entry['cell'], 'target_cell': target_name,
                   'category': category, 'source_area': str(source['area']), 'target_area': str(target['area']),
                   'area_saved': str(source['area']-target['area']),
                   'original_recipe_exact_pair': (inst, target_name) in pairs,
                   'original_recipe_instance': inst in recipe_instances}
            if source['signature'] != target['signature']:
                row['reason'] = 'full_conservative_signature_mismatch'
                rejections.append(row)
            else:
                row['signature_sha256'] = digest(source['signature'])
                candidates.append(row)
    recipe_audit = []
    for action in recipe:
        source_name = design['instances'][action['instance']]['cell']
        assert source_name == action['new_cell'], action
        src, dst = cells[source_name], cells[action['old_cell']]
        recipe_audit.append({'instance': action['instance'], 'source': source_name, 'target': action['old_cell'],
                             'same_signature': src['signature'] == dst['signature'],
                             'area_saved': str(src['area']-dst['area']),
                             'enumerated': (action['instance'], action['old_cell']) in {(x['instance'], x['target_cell']) for x in candidates}})
    counts = {'all_instances': len(design['instances']), 'excluded_exact_zero_pin_taps': len(taps),
              'functional_instances': len(inventory), 'connected_pins': sum(len(x['pins']) for x in inventory),
              'functional_category_counts': dict(Counter(x['category'] for x in inventory)),
              'mapped_area': str(sum((Decimal(x['area']) for x in inventory), Decimal(0))),
              'candidate_pairs': len(candidates), 'candidate_instances': len({x['instance'] for x in candidates}),
              'pair_category_counts': dict(Counter(x['category'] for x in candidates)),
              'instance_category_counts': {c: len({x['instance'] for x in candidates if x['category'] == c}) for c in sorted({x['category'] for x in inventory})},
              'original_recipe_actions': len(recipe), 'recipe_exact_pairs_in_positive_area_space': sum(x['original_recipe_exact_pair'] for x in candidates),
              'omitted_pairs': sum(not x['original_recipe_exact_pair'] for x in candidates),
              'omitted_pairs_at_recipe_instances': sum(x['original_recipe_instance'] and not x['original_recipe_exact_pair'] for x in candidates),
              'omitted_pairs_at_new_instances': sum(not x['original_recipe_instance'] for x in candidates),
              'omitted_new_instances': len({x['instance'] for x in candidates if not x['original_recipe_instance']}),
              'smaller_same_family_signature_rejections': len(rejections)}
    assert counts['all_instances'] == 3128 and counts['functional_instances'] == 102
    assert all(sha(p) == hashes[str(p.relative_to(ROOT)).replace('\\', '/')] for p in source_paths)
    result = {'schema': 1, 'scope': 'CONTROL fixed-Liberty static logical-interface-compatible strictly smaller-area candidate space; not timing or physical feasibility',
              'source_sha256': hashes, 'source_unchanged_after_read': True, 'counts': counts,
              'matching_rule': 'Identical family prefix, complete functional pin names/directions/non-electrical scalar attributes, complete PG pins, exact output functions/three_state, exact state variable headers and ALL ff/latch attributes, remaining cell attributes; strictly lower Liberty area. No Boolean algebra or pin remapping.',
              'ignored_pin_attributes': sorted(IGNORED_PIN_ATTRIBUTES), 'ignored_cell_attributes': sorted(IGNORED_CELL_ATTRIBUTES),
              'observed_pin_attributes': pin_attrs, 'ignored_groups': ['leakage_power', 'pin/internal_power', 'pin/timing'],
              'classification': 'sequential takes precedence; clock_family only Liberty family clkbuf or clkinv, not a full clock-net reachability classification',
              'inventory': inventory, 'candidates': candidates, 'recipe_actions': recipe_audit,
              'rejected_smaller_same_family': rejections, 'excluded_tap_instance_ids': taps,
              'used_cell_signatures': {n: cells[n]['signature'] for n in sorted({x['cell'] for x in inventory})},
              'candidate_target_signatures': {n: cells[n]['signature'] for n in sorted({x['target_cell'] for x in candidates})}}
    (HERE / 'SPACE_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
