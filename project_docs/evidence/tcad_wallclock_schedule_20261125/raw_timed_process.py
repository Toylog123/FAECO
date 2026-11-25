"""Use the experiment's RAW clock for both subprocess limits and accounting."""

import os
from pathlib import Path
import signal
import subprocess
import time

from run_wallclock_matrix import comparison, raw_seconds


POLL_SECONDS = 0.10


def run_process(argv, logfile: Path, timeout: float, *, env=None) -> comparison.ProcessResult:
    start = raw_seconds()
    deadline = start + timeout
    with logfile.open("wb") as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, cwd=logfile.parent,
                                   env=env, start_new_session=True)
        try:
            while (returncode := process.poll()) is None:
                remaining = deadline - raw_seconds()
                if remaining <= 0:
                    break
                time.sleep(min(remaining, POLL_SECONDS))
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
    return comparison.ProcessResult(returncode, raw_seconds() - start, timeout, str(logfile))
