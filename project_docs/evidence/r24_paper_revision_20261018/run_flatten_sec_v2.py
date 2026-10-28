"""Two approved native helper flattens, full native-JSON connection audit and two SECs; no STA."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import os
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
DESIGN = BASE / 'PAIRED_SPEF_FLAT_V2_DESIGN.json'
EXPECTED = 'ce042520d71af073a797360ae4433ccd51575d8b7d144931b15d631681e37aa0'
V2 = BASE / 'paired_spef_flat_v2'
sys.path.insert(0, str(ROOT / 'code/src'))
sys.path.insert(0, str(ROOT / 'code/scripts'))
from rseco.verilog_modules import module_spans, target_module_text
from rseco.gate_sizing import parse_mapped_netlist
from rseco.logic_rewrite import parse_liberty_cells
from rseco.real_wns import validate_cell_input_connections, two_state_sec_unsupported_reason
from rseco.spef import parse_mapped_verilog, build_spef
import run_r22_cut_ablation as common

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def record(p):
    p = Path(p)
    return {'path': str(p.resolve()), 'sha256': sha(p), 'bytes': p.stat().st_size}

def save(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

assert sha(DESIGN) == EXPECTED
d = load(DESIGN)
review = load(BASE / 'PAIRED_SPEF_FLAT_V2_ROOT_REVIEW.json')
assert review['design_sha256'] == EXPECTED and not review['STA_authorized']
ORIGINAL_RUN = subprocess.run
started = time.perf_counter()
deadline = started + d['global_deadline_s']
V2.joinpath('generated').mkdir(exist_ok=False)
V2.joinpath('sec_inputs').mkdir(exist_ok=False)
progress = V2 / 'PROGRESS.jsonl'
completed = []

def event(name, **data):
    row = {'event': name, 'UTC': datetime.now(timezone.utc).isoformat(), 'elapsed_s': time.perf_counter() - started, **data}
    with progress.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps(row, ensure_ascii=False), flush=True)

def guard():
    p = ORIGINAL_RUN(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
    assert p.returncode == 0 and p.stdout.decode().strip() == d['head']
    assert sha(DESIGN) == EXPECTED
    for r in d['sources'] + [d['model_scope']]:
        assert sha(r['path']) == r['sha256'], r['path']
    for j in d['jobs']:
        assert sha(j['raw']['path']) == j['raw']['sha256']
        assert sha(j['ys']['path']) == j['ys']['sha256']

def native(argv, out, timeout):
    remaining = deadline - time.perf_counter()
    if remaining <= 0:
        raise TimeoutError('V2 global deadline')
    out.mkdir(parents=True, exist_ok=False)
    t = time.perf_counter()
    save(out / 'launch.json', {'argv': argv, 'timeout_s': min(timeout, remaining), 'requested_timeout_s': timeout})
    env = dict(os.environ)
    env['PATH'] = r'C:\Windows\System32;C:\Windows'
    try:
        p = ORIGINAL_RUN(argv, capture_output=True, timeout=min(timeout, remaining), env=env)
    except subprocess.TimeoutExpired as exc:
        (out / 'stdout.bin').write_bytes(exc.stdout or b'')
        (out / 'stderr.bin').write_bytes(exc.stderr or b'')
        save(out / 'return.json', {'timeout': True, 'elapsed_s': time.perf_counter() - t})
        raise
    (out / 'stdout.bin').write_bytes(p.stdout)
    (out / 'stderr.bin').write_bytes(p.stderr)
    save(out / 'return.json', {'returncode': p.returncode, 'elapsed_s': time.perf_counter() - t,
        'stdout_sha256': sha(out / 'stdout.bin'), 'stderr_sha256': sha(out / 'stderr.bin')})
    if p.returncode:
        raise RuntimeError('Native Yosys failed: ' + repr(argv))
    return p

def static_connection_audit(job):
    before, after = load(job['pre_flat_json'])['modules'], load(job['post_flat_json'])['modules']
    pre, post = before['s382'], after['s382']
    assert list(pre['ports']) == list(post['ports']), 'Top port order changed'
    # Native JSON IDs can change between serializations; derive a bijection
    # solely from every pre-existing top net name/bit and check alias classes.
    forward, reverse = {}, {}
    for name, net in pre['netnames'].items():
        assert name in post['netnames'], 'Original top net dropped: ' + name
        new = post['netnames'][name]
        assert len(net['bits']) == len(new['bits']) and len(net['bits']) > 0
        for oldbit, newbit in zip(net['bits'], new['bits']):
            if isinstance(oldbit, str):
                assert oldbit == newbit
            assert oldbit not in forward or forward[oldbit] == newbit, 'Alias class split'
            assert newbit not in reverse or reverse[newbit] == oldbit, 'Distinct original bits merged'
            forward[oldbit], reverse[newbit] = newbit, oldbit
    def mapped(bits):
        return [b if isinstance(b, str) else forward[b] for b in bits]
    for name, port in pre['ports'].items():
        other = post['ports'][name]
        assert port['direction'] == other['direction'] and len(port['bits']) == len(other['bits'])
        assert mapped(port['bits']) == other['bits']
    helper = before['dff']
    assert set(helper['cells']) == {'_0_'}
    leaf = helper['cells']['_0_']
    assert leaf['type'] == 'sky130_fd_sc_hd__dfxtp_1'
    assert set(leaf['connections']) == {'CLK', 'D', 'Q'}
    helper_port_for_bit = {}
    for name, port in helper['ports'].items():
        assert len(port['bits']) == 1
        helper_port_for_bit[port['bits'][0]] = name
    expected, state_map = {}, {}
    for name, cell in pre['cells'].items():
        if cell['type'] == 'dff':
            new_name = name + '._0_'
            connections = {pin: mapped(cell['connections'][helper_port_for_bit[bits[0]]]) for pin, bits in leaf['connections'].items()}
            expected[new_name] = {'type': leaf['type'], 'connections': connections}
            state_map[name] = {'flat_instance': new_name, 'type': leaf['type'], 'connections': connections,
                               'CLK_from': 'CK', 'D_from': 'D', 'Q_from': 'Q'}
        else:
            assert cell['type'].startswith('sky130_fd_sc_hd__')
            expected[name] = {'type': cell['type'], 'connections': {pin: mapped(bits) for pin, bits in cell['connections'].items()}}
    assert len(state_map) == 21
    assert set(expected) == set(post['cells']), 'Missing or additional standard-cell instance'
    for name, cell in expected.items():
        actual = post['cells'][name]
        assert actual['type'] == cell['type'] and actual['connections'] == cell['connections'], 'Cell/pin connectivity changed: ' + name
        assert after[cell['type']]['attributes'].get('blackbox') == '00000000000000000000000000000001'
    flat = Path(job['flat_output'])
    text = flat.read_text(encoding='utf-8')
    assert {m.name for m in module_spans(text)} == {'s382'}
    parsed = parse_mapped_netlist(text)
    assert len(parsed) == len(expected) == 90
    assert sum(c.cell_type == 'sky130_fd_sc_hd__dfxtp_1' for c in parsed) == 21
    # Independently compare parsed textual cells against native JSON names.
    observed = {c.instance.lstrip('\\'): c for c in parsed}
    assert set(observed) == set(expected)
    for name, cell in expected.items():
        assert observed[name].cell_type == cell['type']
        assert set(observed[name].pins) == set(cell['connections'])
    return {'status': 'pass', 'all_original_top_net_alias_classes_bijective': True,
        'original_top_net_names_checked': len(pre['netnames']), 'original_top_bits_checked': len(forward),
        'top_ports_order_direction_width_bits_preserved': True, 'top_ports': post['ports'],
        'all_native_JSON_standard_cell_type_pin_connections_match': True, 'expected_cells': expected,
        'state_map': state_map, 'standard_cell_count': len(expected), 'dfxtp_count': len(state_map),
        'textual_cell_identity_and_pin_sets_match_native_JSON': True,
        'stdcell_blackboxes_preserved': True, 'flat': record(flat),
        'pre_json': record(job['pre_flat_json']), 'post_json': record(job['post_flat_json'])}

try:
    guard()
    save(V2 / 'EXECUTION_PIN.json', {'design': EXPECTED, 'driver': record(__file__),
         'review': record(BASE / 'PAIRED_SPEF_FLAT_V2_ROOT_REVIEW.json'), 'head': d['head'], 'STA_authorized': False})
    tool = d['expected_tool']
    v = native(['wsl.exe', '-d', 'Ubuntu', '--', tool['path'], '-V'], V2 / '_version', 30)
    h = native(['wsl.exe', '-d', 'Ubuntu', '--', 'sha256sum', tool['path']], V2 / '_binary', 30)
    assert ('Yosys ' + tool['version']) in v.stdout.decode('utf-8', 'replace')
    assert h.stdout.decode().split()[0] == tool['sha256']
    libtext = common.LIB.read_text(encoding='utf-8')
    cells = parse_liberty_cells(libtext)
    # Complete both flattened objects/static mappings before starting any SEC.
    for job in d['jobs']:
        guard()
        event('flatten_start', side=job['side'])
        native(job['argv'], V2 / 'flatten_processes' / job['side'], job['flatten_timeout_s'])
        audit = static_connection_audit(job)
        text = Path(job['flat_output']).read_text(encoding='utf-8')
        validate_cell_input_connections(text, cells)
        assert two_state_sec_unsupported_reason(text, cells) is None
        net = parse_mapped_verilog(Path(job['flat_output']), liberty_text=libtext, top_module='s382')
        spef = build_spef(net, unit_len_um=40)
        audit['required_inputs_two_state_static_SPEF'] = 'pass'
        audit['spef40_text_sha256'] = hashlib.sha256(spef.encode()).hexdigest()
        save(V2 / 'generated' / (job['side'] + '.STATIC_AUDIT.json'), audit)
        event('flatten_static_pass', side=job['side'], cells=audit['standard_cell_count'], states=21, sha256=audit['flat']['sha256'])
    for job in d['jobs']:
        guard()
        raw = Path(job['raw']['path'])
        flat = Path(job['flat_output'])
        initial = raw.read_text(encoding='utf-8-sig')
        flat_text = flat.read_text(encoding='utf-8')
        helper = {m.name: m.text for m in module_spans(initial)}['dff']
        proof_copy = Path(job['sec']['flat_sec_compat_copy'])
        proof_copy.write_bytes(flat.read_bytes() + b'\n' + helper.encode('utf-8'))
        final = proof_copy.read_text(encoding='utf-8')
        assert target_module_text(final, 's382') == target_module_text(flat_text, 's382')
        assert {m.name: m.text for m in module_spans(final)}['dff'] == helper
        raw_snapshot = V2 / 'sec_inputs' / (job['side'] + '.raw_exact_bytes.v')
        raw_snapshot.write_bytes(raw.read_bytes())
        assert sha(raw_snapshot) == job['raw']['sha256']
        proof = Path(job['sec']['output_dir'])
        event('SEC_start', side=job['side'])
        # Capture raw bytes for the unchanged final_sec subprocess boundary;
        # preserve exact argv, timeout and original text/newline return values.
        def captured_sec_run(argv, *a, **kw):
            assert argv[:5] == ['wsl.exe', '-d', 'Ubuntu', '--', '/usr/bin/yosys']
            assert kw['timeout'] == 180 and deadline - time.perf_counter() >= 180
            save(proof / 'native_launch.json', {'argv': argv, 'timeout_s': 180})
            encoding, errors = kw.pop('encoding'), kw.pop('errors')
            assert kw.pop('text') is True
            t = time.perf_counter()
            p = ORIGINAL_RUN(argv, *a, **kw)
            (proof / 'native_stdout.bin').write_bytes(p.stdout)
            (proof / 'native_stderr.bin').write_bytes(p.stderr)
            save(proof / 'native_return.json', {'returncode': p.returncode, 'elapsed_s': time.perf_counter() - t})
            def dec(b):
                return b.decode(encoding, errors).replace('\r\n', '\n').replace('\r', '\n')
            return subprocess.CompletedProcess(p.args, p.returncode, dec(p.stdout), dec(p.stderr))
        subprocess.run = captured_sec_run
        try:
            result = common.final_sec(initial, final, 's382', proof)
        finally:
            subprocess.run = ORIGINAL_RUN
        assert result['status'] == 'pass' and result['returncode'] == 0
        log = (proof / 'sec.log').read_text(encoding='utf-8')
        proven, unproven = map(int, re.search(r'Of those cells (\d+) are proven and (\d+) are unproven', log).groups())
        assert proven > 0 and unproven == 0 and 'Equivalence successfully proven!' in log
        assert target_module_text((proof / 'gate.v').read_text(encoding='utf-8'), 's382') == target_module_text(flat_text, 's382')
        used = set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+(?:\\[^\s]+|\w+)\s*\(', initial + '\n' + final))
        model_names = {m.name for m in module_spans((proof / 'cells.v').read_text(encoding='utf-8'))}
        assert model_names == used, 'Actual used model set not exact'
        guard()
        row = {'side': job['side'], 'flat': record(flat), 'raw': job['raw'], 'proof_compat_copy': record(proof_copy),
            'raw_snapshot': record(raw_snapshot), 'gate_top_identical_to_flat_top': True,
            'unused_helper_identical_to_raw': True, 'models': sorted(model_names), 'models_actual_used_set_exact': True,
            'result': record(proof / 'result.json'), 'log': record(proof / 'sec.log'), 'proven': proven, 'unproven': unproven}
        completed.append(row)
        save(proof / 'ACCEPTANCE.json', row)
        event('SEC_pass', side=job['side'], proven=proven, unproven=unproven)
    guard()
    save(V2 / 'FROZEN_DERIVED_INPUTS.json', {'status': 'flat_and_two_SEC_complete_pending_root_review_no_STA',
        'head': d['head'], 'design_sha256': EXPECTED, 'flat_inputs': completed,
        'source_input_Lib_HEAD_stable': True, 'actual_flatten_launches': 2, 'actual_SEC_launches': 2, 'STA_launches': 0,
        'scope': 'Derived mapped objects with original-to-flat equivalence only; does not close OI051 production support or establish physical gain.',
        'artifacts': [record(p) for p in sorted(V2.rglob('*')) if p.is_file()]})
    event('complete_pending_root_review', flatten=2, SEC=2, STA=0)
except Exception as exc:
    subprocess.run = ORIGINAL_RUN
    save(V2 / 'FAILURE.json', {'status': 'stopped', 'error_type': type(exc).__name__, 'error': str(exc), 'completed_SEC': completed,
        'elapsed_s': time.perf_counter() - started, 'STA_launches': 0})
    event('stopped', error_type=type(exc).__name__, error=str(exc))
    raise
