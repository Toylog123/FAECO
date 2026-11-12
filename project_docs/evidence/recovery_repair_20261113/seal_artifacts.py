"""Seal or verify this evidence package; excludes only bytecode and self-manifest."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'ARTIFACT_MANIFEST.json'


def inventory():
    return {str(p.relative_to(HERE)).replace('\\', '/'): {
                'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(HERE.rglob('*')) if p.is_file() and p != MANIFEST
            and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def main(verify):
    files = inventory()
    if verify:
        recorded = json.loads(MANIFEST.read_text(encoding='utf-8'))
        if recorded['files'] != files:
            raise ValueError('Evidence files changed, added or removed since sealing')
    else:
        if MANIFEST.exists():
            raise ValueError('Refusing to overwrite an existing seal')
        MANIFEST.write_text(json.dumps(dict(scope='s382 four separately registered experimental stages; all successes and failures retained',
            exclusions=['__pycache__ directories', '*.pyc', 'ARTIFACT_MANIFEST.json (self)'],
            files=files), indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(mode='verify' if verify else 'seal', files=len(files), bytes=sum(f['bytes'] for f in files.values()),
                         manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    main(parser.parse_args().verify)
