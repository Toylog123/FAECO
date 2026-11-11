#!/usr/bin/env bash
# P1' pilot stage 2: RF runs on the exported (post-resizer) netlists, then measure.
set -uo pipefail

EXP_DIR="experiments/20261116_resizer_then_faecop"
cd "$(dirname "$0")/../.." || exit 1

export MSYS_NO_PATHCONV=1
export PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

echo "=== stage rf ==="
bash "$EXP_DIR/run_rf.sh" s382 s641 s832
echo "=== stage rf rc=$? ==="

echo "=== stage rmeasure ==="
.venv/Scripts/python.exe "$EXP_DIR/measure.py" --arms RF --circuits s382,s641,s832 --utils 0.30,0.35,0.40
echo "=== stage rmeasure rc=$? ==="

echo "=== analyze ==="
.venv/Scripts/python.exe "$EXP_DIR/analyze.py"
echo "PILOT2_DONE"