"""Archive one D case and run the root postcheck on it.

This is the generic counterpart of the s27/s382/s420 pair
(run_first_two.py / run_s420_v2.py + run_d_s420_root_post_20261018.py).  It
runs the ARCHIVER UNCHANGED (same SHA as the three accepted cases) and the
ROOT POSTCHECKER UNCHANGED (same SHA as recorded in the accepted s27 case),
and it does both steps in one authorized run.

WHAT IS NEW, AND WHY IT IS RECORDED
------------------------------------
1. **7z location.** The three accepted cases were archived on another machine
   with a scoop shim (`C:\\Users\\<other user>\\scoop\\shims\\7z.EXE`).  On
   this machine that shim no longer exists; the archive tool is
   `C:\\Program Files\\7-Zip\\7z.exe` (7-Zip 26.05).  The directory is
   therefore prepended to PATH for this run, and the resolved tool path and
   its version output are recorded in the invocation receipt.  The compressor
   version differs from the earlier three cases -- the extracted BYTES are
   what the root postcheck compares, and each case carries its own receipt.
2. **The audit/acceptance pair.** The 56-job root completion audit and the
   56-key independent root acceptance are used, and their SHAs are recorded.
3. **Timeout registration.** The archiver's own per-phase timeouts are
   unchanged (7z create 600 s, test 120 s, restore 120 s); the outer wrapper
   is 900 s / parent 930 s, which covers the measured create times
   (s27 6.6 s, s382 76.0 s, s420 111.2 s) and the predicted ones for the
   remaining cases (s641 ~133 s, s713 ~96 s, s820 ~72 s, s832 ~86 s,
   s953 ~178 s) with margin.

Usage:  python run_d_case_archive_post_20261025.py <circuit>
"""
from pathlib import Path
import json, hashlib, subprocess, os, sys, time, datetime

ROOT = Path.cwd().resolve()
BASE = ROOT / 'project_docs/evidence/r22_D_revalidation_20261018'
ARCH = BASE / 'full_artifact_archives'
ARCHIVER = ARCH / 'archive_d_cases_v2.py'
POSTCHECK = ARCH / 'root_post_d_archives_20261018.py'
AUDIT = BASE / 'ROOT_COMPLETION_AUDIT_56.json'
ACCEPT = BASE / 'INDEPENDENT_56_ROOT_ACCEPTANCE.json'
SEVENZIP_DIR = r'C:\Program Files\7-Zip'

# the archiver and the postchecker must be the ones the accepted cases used
ARCHIVER_SHA = 'b60cc3f1f4e7dfbb0db884b21b4b0faa55b7909260d70b9aa28ecbda42c40b3f'

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))

if len(sys.argv) != 2:
    raise SystemExit('usage: run_d_case_archive_post_20261025.py <circuit>')
c = sys.argv[1]

assert sha(ARCHIVER) == ARCHIVER_SHA, 'the archiver drifted from the accepted cases'
assert sha(POSTCHECK) == read(ARCH / 's27/ROOT_POST_VERIFICATION.json')['checker_sha256'], \
    'the root postchecker drifted from the accepted s27 case'
case = ARCH / c
assert not case.exists(), 'the case directory already exists -- refusing to overwrite'
assert read(ACCEPT)['accepted'] is True
audit = read(AUDIT)
assert read(ACCEPT)['completion_set'] == audit['completion_set_frozen_at_start']
manifest = read(ROOT / 'experiments/20261018_r22_D_revalidate_v1/manifest.json')
arms = [j['key'] for j in manifest['jobs'] if j['circuit'] == c]
assert len(arms) == 7, 'the case does not have seven arms: %s' % arms
for key in arms:
    assert key in audit['completion_set_frozen_at_start'], 'arm not in the accepted set: %s' % key

env = os.environ.copy()
env['PYTHONUTF8'] = '1'
env['PATH'] = SEVENZIP_DIR + os.pathsep + env.get('PATH', '')
_where = subprocess.run(['where', '7z'], capture_output=True, text=True,
                        env=env).stdout.strip().splitlines()
assert _where, '7z is still not on the PATH after the Program Files prepend'
sevenzip = _where[0]
sevenzip_version = subprocess.run([sevenzip], capture_output=True, text=True,
                                  env=env).stdout.strip().splitlines()[:2]

argv = ['C:/Program Files/Git/bin/bash.exe', 'code/scripts/run_with_timeout.sh',
        '900', str(ROOT / '.venv/Scripts/python.exe'), '-X', 'utf8', '-u',
        str(ARCHIVER), '--circuit', c, '--output-dir', str(case),
        '--audit', str(AUDIT), '--acceptance', str(ACCEPT)]
record = {
    'argv': argv, 'cwd': str(ROOT),
    'archiver_sha256': sha(ARCHIVER),
    'archiver_unchanged_since_accepted_cases': True,
    'root_postchecker_sha256': sha(POSTCHECK),
    'root_audit_sha256': sha(AUDIT),
    'root_acceptance_sha256': sha(ACCEPT),
    'sevenzip_resolved': sevenzip,
    'sevenzip_version': sevenzip_version,
    'sevenzip_path_note': ('the three accepted cases were archived with a scoop '
                           'shim on another machine; that shim no longer exists '
                           'here, so Program Files\\7-Zip is prepended to PATH'),
    'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'wrapper_timeout_s': 900, 'parent_timeout_s': 930,
    'authorized_case_only': c,
    'case_arms': arms,
    'no_new_EDA': True,
}
(ARCH / ('%s_INVOCATION.json' % c)).write_text(json.dumps(record, indent=2) + '\n',
                                                encoding='utf-8')
(ARCH / Path(__file__).name).write_bytes(Path(__file__).read_bytes())

started = time.monotonic()
with (ARCH / ('%s_WRAPPER.log' % c)).open('xb') as log:
    p = subprocess.run(argv, env=env, stdout=log, stderr=subprocess.STDOUT,
                       timeout=930)
result = {**record, 'returncode': p.returncode,
          'runtime_s': time.monotonic() - started,
          'wrapper_log_sha256': sha(ARCH / ('%s_WRAPPER.log' % c))}
if (case / 'receipt.json').is_file():
    result['producer_receipt_sha256'] = sha(case / 'receipt.json')
(ARCH / ('%s_RUN_RECEIPT.json' % c)).write_text(json.dumps(result, indent=2) + '\n',
                                                 encoding='utf-8')
assert p.returncode == 0, 'the archiver failed; the originals are preserved'
assert read(case / 'receipt.json')['status'] == 'verified'

# ---------------------------------------------------------------- the root post
post_argv = ['C:/Program Files/Git/bin/bash.exe', 'code/scripts/run_with_timeout.sh',
             '300', str(ROOT / '.venv/Scripts/python.exe'), '-X', 'utf8', '-u',
             str(POSTCHECK), c]
post_record = {
    'argv': post_argv, 'cwd': str(ROOT),
    'checker_sha256': sha(POSTCHECK),
    'producer_receipt_sha256': sha(case / 'receipt.json'),
    'root_acceptance_sha256': sha(ACCEPT),
    'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'wrapper_timeout_s': 300, 'parent_timeout_s': 330, 'no_new_EDA': True,
}
(ARCH / ('ROOT_POST_%s_INVOCATION.json' % c.upper())).write_text(
    json.dumps(post_record, indent=2) + '\n', encoding='utf-8')
started = time.monotonic()
with (ARCH / ('ROOT_POST_%s.log' % c.upper())).open('xb') as log:
    p2 = subprocess.run(post_argv, env=env, stdout=log, stderr=subprocess.STDOUT,
                        timeout=330)
post_result = {**post_record, 'returncode': p2.returncode,
               'runtime_s': time.monotonic() - started,
               'log_sha256': sha(ARCH / ('ROOT_POST_%s.log' % c.upper()))}
if (case / 'ROOT_POST_VERIFICATION.json').exists():
    post_result['post_result_sha256'] = sha(case / 'ROOT_POST_VERIFICATION.json')
(ARCH / ('ROOT_POST_%s_RUN_RECEIPT.json' % c.upper())).write_text(
    json.dumps(post_result, indent=2) + '\n', encoding='utf-8')
assert p2.returncode == 0, 'the root postcheck failed'
print(json.dumps({'case': c, 'archive_rc': p.returncode,
                  'post_rc': p2.returncode,
                  'archive_receipt_sha256': result['producer_receipt_sha256'],
                  'post_result_sha256': post_result.get('post_result_sha256')}))
