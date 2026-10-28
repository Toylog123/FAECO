"""Execute the root-reviewed v3 checker against the FULL registered D56 set.

This is the 56-key counterpart of
independent_completed_review/run_28_v2/run_d28_independent_v3_20261018.py.
It differs in exactly three ways, and each difference is registered here:

  1. the root audit is ROOT_COMPLETION_AUDIT_56.json (the 56-job root
     completion replay), not the 28-job one;
  2. the output directory is a NEW exclusive directory (run_56_v1) -- nothing
     of the 28-run is touched;
  3. the timeout is registered from the MEASURED runtime of the 28-run, not
     copied from it: the 28-key run took 184.8 s for 16407 read artefacts, so
     the 56-key run is expected to take about twice that; the wrapper limit is
     therefore raised to 1800 s (parent 1830 s), which is still inside the
     harness's own 3600 s ceiling.

The checker itself is UNCHANGED (same SHA as the 28-run), and the contract it
was reviewed against is the same one: read-only independent raw review, no
new EDA, no source/HEAD change, no original record change.
"""
from pathlib import Path
import subprocess, os, json, hashlib, datetime, time

ROOT = Path.cwd().resolve()
BASE = ROOT / 'project_docs/evidence/r22_D_revalidation_20261018'
PREP = BASE / 'ledger_duplicate_diagnosis_20261018'
OUT = BASE / 'independent_completed_review/run_56_v1'
# the directory must be EXCLUSIVE: only this runner may be in it, no output of
# an earlier attempt (the 28-run used mkdir(exist_ok=False); here the runner
# itself lives in the directory, so the exclusivity is asserted instead)
OUT.mkdir(exist_ok=True)
_present = sorted(p.name for p in OUT.iterdir())
assert _present == [Path(__file__).name], \
    'the run directory is not exclusive: %s' % _present

script = PREP / 'checker_v3.py'
audit = BASE / 'ROOT_COMPLETION_AUDIT_56.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

assert sha(script) == 'f6b053dfa6552aca43817f0dc1c1bdefca295c32bdf7ddc4b01cf1b12ab71daf'
assert audit.exists()
audit_sha = sha(audit)

argv = ['C:/Program Files/Git/bin/bash.exe', 'code/scripts/run_with_timeout.sh',
        '1800', str(ROOT / '.venv/Scripts/python.exe'), '-X', 'utf8', '-u',
        str(script), '--audit', str(audit), '--output', str(OUT / 'review')]
env = os.environ.copy()
env['PYTHONUTF8'] = '1'

record = {
    'argv': argv,
    'cwd': str(ROOT),
    'checker_sha256': sha(script),
    'parent_root_audit_sha256': audit_sha,
    'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'root_preexecution_review': {
        'design_sha256': sha(PREP / 'V3_DESIGN.md'),
        'minimal_diff_sha256': sha(PREP / 'checker_v2_to_v3.diff'),
        'diagnosis_sha256': sha(PREP / 'DIAGNOSIS.json'),
        'approved_contract': (
            'The full registered 56-key completion set, taken from the immutable '
            'ROOT_COMPLETION_AUDIT_56.json; every selected completion SHA must '
            'match. Original raw STA/SEC/source checks retained; strict actual '
            'cache / identity dedup / cached rejection separation. Legacy broad '
            'cache field preserved as compatibility sum.'),
    },
    'checker_independently_authored': True,
    'timeout_registration': {
        'basis': 'the 28-key run measured 184.8 s for 16407 read artefacts; the '
                 '56-key run has twice the jobs and roughly twice the artefacts',
        'wrapper_timeout_s': 1800,
        'parent_timeout_s': 1830,
        'measured_28key_runtime_s': 184.8,
        'note': 'the 28-run limits (900/930) were NOT reused as-is',
    },
    'scope': ('Read-only independent raw review of the full registered D56 '
              'completion set; no new EDA/source/HEAD or original record '
              'changes.'),
}
(OUT / 'INVOCATION.json').write_text(json.dumps(record, indent=2) + '\n',
                                      encoding='utf-8')
(OUT / Path(__file__).name).write_bytes(Path(__file__).read_bytes())

started = time.monotonic()
with (OUT / 'WRAPPER.log').open('xb') as log:
    p = subprocess.run(argv, env=env, stdout=log, stderr=subprocess.STDOUT,
                       timeout=1830)
receipt = {**record,
           'returncode': p.returncode,
           'runtime_s': time.monotonic() - started,
           'log_sha256': sha(OUT / 'WRAPPER.log'),
           'checker_unchanged': sha(script) == record['checker_sha256']}
if (OUT / 'review/RESULT.json').exists():
    receipt['result_sha256'] = sha(OUT / 'review/RESULT.json')
(OUT / 'FINAL_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n',
                                         encoding='utf-8')
assert p.returncode == 0 and receipt['checker_unchanged']
print(json.dumps(receipt))
