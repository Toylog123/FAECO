#!/usr/bin/env bash
# Run OpenROAD resizer baseline on all 8 ISCAS89 circuits.
# Usage: bash experiments/20261115_p1_resizer_vs_faeco/run_resizer.sh [circuit ...]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../.."

export MSYS_NO_PATHCONV=1
export PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

.venv/Scripts/python.exe experiments/20261115_p1_resizer_vs_faeco/run_resizer.py "$@"