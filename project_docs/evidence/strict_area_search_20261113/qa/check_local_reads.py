"""Read-only integration check: deny runtime reads of all other evidence/experiments."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import run_search


def forbid_old(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = Path(args[0]).resolve()
        if (path.is_relative_to(ROOT / 'experiments') or path.is_relative_to(ROOT / 'project_docs/evidence')) and not path.is_relative_to(HERE):
            raise AssertionError('Runtime read outside package: ' + str(path))


sys.addaudithook(forbid_old)
run_search.preflight()
print('Local-only runtime preflight PASS: no reads from older evidence or experiments')
