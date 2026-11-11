#!/usr/bin/env bash
# Hybrid arm at util 0.30 and 0.40 (util 0.35 already done as arms/Hybrid).
# NOTE: run_resizer.py takes --util; RESIZER_DIR only redirects the output dir.
set -u
cd "$(dirname "$0")/../.." || exit 1
export PATH="/c/Windows/System32:/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:$PATH"
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1
export RESIZER_INPUT_DIR=ends
for u in 0.30 0.40; do
  echo "=== Hybrid @ util $u ==="
  RESIZER_DIR="arms/Hybrid_u$u" .venv/Scripts/python.exe experiments/20261115_p1_resizer_vs_faeco/run_resizer.py \
    --util "$u" s27 s382 s420 s641 s713 s820 s832 s953 2>&1 | tail -12
done
echo "=== Hybrid multi-util done ==="