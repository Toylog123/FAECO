#!/usr/bin/env bash
# Measure the pilot arms through the standard signoff flow.
# Usage: bash _measure_pilot.sh [arms] [circuits]
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

export MSYS_NO_PATHCONV=1 PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

ARMS="${1:-Rprime,RF}"
CIRCUITS="${2:-s382,s641,s832}"

.venv/Scripts/python.exe experiments/20261116_resizer_then_faecop/measure.py \
    --arms "$ARMS" --circuits "$CIRCUITS" --utils 0.30,0.35,0.40
echo "MEASURE_DONE rc=$?"