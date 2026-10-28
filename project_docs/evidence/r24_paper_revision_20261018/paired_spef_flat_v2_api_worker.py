"""Execute the unchanged registered CLI while retaining each native STA raw stream."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import runpy
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument('--design', required=True, type=Path)
ap.add_argument('--job', required=True)
args = ap.parse_args()
design = json.loads(args.design.read_text(encoding='utf-8'))
job = next(j for j in design['jobs_in_order'] if j['name'] == args.job)
capture = Path(design['output_root']) / '_api_capture' / args.job
capture.mkdir(parents=True, exist_ok=False)
original_run = subprocess.run
sequence = 0

def save(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def utc():
    return datetime.now(timezone.utc).isoformat()

def decode(raw, encoding, errors):
    # Match subprocess text=True universal-newline translation exactly.
    return raw.decode(encoding, errors).replace('\r\n', '\n').replace('\r', '\n')

def captured_run(argv, *a, **kw):
    global sequence
    if not (isinstance(argv, list) and argv and str(argv[0]).lower().endswith('wsl.exe')
            and '/usr/local/bin/sta' in argv):
        raise RuntimeError('Unregistered subprocess from scientific CLI: ' + repr(argv))
    sequence += 1
    d = capture / f'launch_{sequence:02d}'
    d.mkdir()
    requested = dict(kw)
    text_mode = requested.get('text') or requested.get('universal_newlines') or requested.get('encoding') or requested.get('errors')
    assert text_mode and requested.get('capture_output') and requested.get('timeout') == 600
    encoding, errors = requested.get('encoding', 'utf-8'), requested.get('errors', 'strict')
    native = dict(requested)
    for key in ['text', 'encoding', 'errors', 'universal_newlines']:
        native.pop(key, None)
    start = time.perf_counter()
    save(d / 'launch_intent.json', {'argv': argv, 'timeout_s': requested['timeout'],
        'started_UTC': utc(), 'requested_text_encoding': encoding, 'requested_errors': errors,
        'capture_adaptation': 'native raw bytes retained; return same UTF-8/errors/universal-newline decoded strings to unchanged runner'})
    print(json.dumps({'event': 'API_STA_launch', 'job': args.job, 'seq': sequence, 'argv': argv}), flush=True)
    try:
        result = original_run(argv, *a, **native)
        stdout, stderr = result.stdout or b'', result.stderr or b''
        (d / 'stdout.bin').write_bytes(stdout)
        (d / 'stderr.bin').write_bytes(stderr)
        save(d / 'return.json', {'argv': argv, 'returncode': result.returncode,
            'elapsed_s': time.perf_counter() - start, 'finished_UTC': utc(),
            'stdout_sha256': hashlib.sha256(stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(stderr).hexdigest()})
        print(json.dumps({'event': 'API_STA_return', 'job': args.job, 'seq': sequence,
                          'rc': result.returncode, 'elapsed_s': time.perf_counter() - start}), flush=True)
        return subprocess.CompletedProcess(result.args, result.returncode,
            decode(stdout, encoding, errors), decode(stderr, encoding, errors))
    except subprocess.TimeoutExpired as exc:
        (d / 'stdout.bin').write_bytes(exc.stdout or b'')
        (d / 'stderr.bin').write_bytes(exc.stderr or b'')
        save(d / 'return.json', {'argv': argv, 'timeout': True, 'elapsed_s': time.perf_counter() - start})
        raise

subprocess.run = captured_run
sys.argv = job['argv'][1:]
runpy.run_path(sys.argv[0], run_name='__main__')
