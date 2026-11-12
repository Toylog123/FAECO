"""Read-only full-instance area audit of 14 archived recovery pairs.

Uses the strict flat-netlist Reader; unknown cells are errors, not zero area.
The legacy regex is reproduced only to diagnose omissions. No EDA or baseline
hierarchy expansion is performed; recovery-of-penalty percentages are not audited.
"""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from check_phase0_structure import Reader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIB = ROOT / 'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def areas_from_liberty(path):
    text = path.read_text(encoding='utf-8')
    starts = list(re.finditer(r'^\s*cell\s*\(\s*"([^"\n]+)"\s*\)\s*\{', text, re.M))
    areas = {}
    for i, match in enumerate(starts):
        end = starts[i+1].start() if i+1 < len(starts) else len(text)
        values = re.findall(r'^\s*area\s*:\s*([\d.eE+-]+)\s*;', text[match.end():end], re.M)
        if len(values) != 1 or match[1] in areas:
            raise ValueError(f'Nonunique/missing area or cell: {match[1]} {values}')
        value = Decimal(values[0])
        if not value.is_finite() or value < 0:
            raise ValueError(f'Invalid area: {match[1]} {value}')
        areas[match[1]] = value
    if not areas:
        raise ValueError('No Liberty cells found')
    return areas


def audit_netlist(path, areas):
    text = path.read_text(encoding='utf-8')
    parsed, _ = Reader(text).parse()
    exported = parsed['instances']
    unknown = {name: item for name, item in exported.items() if item['cell'] not in areas}
    connected_unknown = {name: item['cell'] for name, item in unknown.items() if any(item['pins'].values())}
    if connected_unknown:
        raise ValueError(f'{path}: connected unknown Liberty cells: {dict(Counter(connected_unknown.values()))}')
    instances = {name: item for name, item in exported.items() if item['cell'] in areas}
    excluded_signature = json.dumps(unknown, sort_keys=True, separators=(',', ':'))

    skipped_prefixes = ('fill_', 'tapvpwrvgnd', 'decap_', 'antenna_', 'probe_')
    legacy = {}
    for cell, name in re.findall(r'(sky130_fd_sc_hd__\w+)\s+(\w+)\s*\(', text):
        if cell in areas and not any(prefix in cell for prefix in skipped_prefixes):
            legacy[name] = cell
    for name, cell in legacy.items():
        if name not in instances or instances[name]['cell'] != cell:
            raise ValueError(f'Legacy result not a subset of strict parser: {path}: {name}')
    omitted = {name: item['cell'] for name, item in instances.items() if name not in legacy}
    omission_reasons = {name: ('explicit_legacy_skip_policy' if any(prefix in cell for prefix in skipped_prefixes) else 'legacy_identifier_regex_omission') for name, cell in omitted.items()}
    total = sum((areas[item['cell']] for item in instances.values()), Decimal(0))
    legacy_total = sum((areas[cell] for cell in legacy.values()), Decimal(0))
    result = {
        'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
        'strict_instance_count': len(instances), 'exported_instance_count': len(exported),
        'unknown_connected_cells': [], 'excluded_unconnected_unknown_count': len(unknown),
        'excluded_unconnected_unknown_types': dict(sorted(Counter(item['cell'] for item in unknown.values()).items())),
        'excluded_unconnected_unknown_signature_sha256': hashlib.sha256(excluded_signature.encode()).hexdigest(),
        'strict_total_mapped_cell_area': str(total),
        'legacy_instance_count': len(legacy), 'legacy_area': str(legacy_total),
        'omitted_count': len(omitted), 'omitted_area': str(total-legacy_total),
        'omitted_instances': omitted, 'omission_reasons': omission_reasons,
        'omission_reason_counts': dict(sorted(Counter(omission_reasons.values()).items())),
        'omitted_cell_type_counts': dict(sorted(Counter(omitted.values()).items())),
        'strict_cell_type_counts': dict(sorted(Counter(x['cell'] for x in instances.values()).items())),
    }
    return result, instances


def main():
    areas = areas_from_liberty(LIB)
    rows = []
    for family, circuits in [('ISCAS89', ['s27','s382','s420','s641','s713','s820','s832','s953']),
                             ('ITC99', ['b01','b02','b03','b06','b07','b08'])]:
        for circuit in circuits:
            if family == 'ISCAS89':
                original = ROOT / 'experiments/20261115_p1_resizer_vs_faeco/arms/Resizer' / circuit / 'routed.v'
                final = ROOT / 'experiments/20261112_resizer_recovery/arms/RECOVERED_V2' / circuit / 'recovered.v'
            else:
                original = ROOT / 'experiments/20261113_itc99_recovery/arms/Resizer' / circuit / 'routed.v'
                final = ROOT / 'experiments/20261113_itc99_recovery/recovered' / circuit / 'recovered.v'
            row = {'family': family, 'circuit': circuit}
            try:
                before, before_i = audit_netlist(original, areas)
                after, after_i = audit_netlist(final, areas)
                strict_saved = Decimal(before['strict_total_mapped_cell_area'])-Decimal(after['strict_total_mapped_cell_area'])
                legacy_saved = Decimal(before['legacy_area'])-Decimal(after['legacy_area'])
                row.update(original=before, final=after, pass_complete=True,
                           strict_area_saved=str(strict_saved), legacy_area_saved=str(legacy_saved),
                           saved_difference=str(strict_saved-legacy_saved),
                           omitted_instances_unchanged=before['omitted_instances']==after['omitted_instances'],
                           strict_reduction_fraction=str(strict_saved/Decimal(before['strict_total_mapped_cell_area'])),
                           instance_names_equal=set(before_i)==set(after_i))
            except (ValueError, OSError) as error:
                row.update(pass_complete=False, error=str(error))
            rows.append(row)
    receipt = {
        'scope': 'All Liberty-known cells present in 28 archived flat Verilog exports; unconnected unknown physical-only instances explicitly counted but excluded; connected unknown cells reject.',
        'liberty': {'path': str(LIB.relative_to(ROOT)), 'sha256': sha(LIB), 'cell_count': len(areas)},
        'script_sha256': sha(Path(__file__)), 'reader_sha256': sha(HERE/'check_phase0_structure.py'),
        'production_parser_sha256_at_audit': sha(ROOT/'code/scripts/recover_area.py'),
        'area_number_encoding': 'Decimal strings in the Liberty area unit, avoiding binary float rounding.',
        'limitations': ['No EDA run or timing/equivalence validation.', 'No baseline hierarchy expansion; no corrected penalty-recovery percentage is claimed.',
                       'Areas cover mapped cells in Verilog exports, not floorplan/core area or cells absent from exports.'],
        'pass_complete': all(row['pass_complete'] for row in rows), 'pairs': rows,
    }
    target = HERE/'area_audit.json'
    target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        if row['pass_complete']:
            print(row['circuit'], row['original']['strict_instance_count'], row['original']['omitted_count'],
                  row['original']['strict_total_mapped_cell_area'], row['final']['strict_total_mapped_cell_area'],
                  'saved='+row['strict_area_saved'], 'saved_difference='+row['saved_difference'])
        else:
            print(row['circuit'], 'FAIL', row['error'])
    print('COMPLETE',receipt['pass_complete'], 'pairs',len(rows))
    if not receipt['pass_complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
