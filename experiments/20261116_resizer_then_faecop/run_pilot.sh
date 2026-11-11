#!/usr/bin/env bash
# P1' pilot orchestrator: R' endpoints -> RF runs -> RF endpoints.
# Usage: bash experiments/20261116_resizer_then_faecop/run_pilot.sh [stage ...]
#   stages: rprime rf rmeasure  (default: all three, in that order)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXP="$SCRIPT_DIR"
cd "$EXP/../.."

export MSYS_NO_PATHCONV=1
export PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

CIRCUITS="s382,s641,s832"
UTILS="0.30,0.35,0.40"

if [ "$#" -gt 0 ]; then
    STAGES=("$@")
else
    STAGES=(rprime rf rmeasure)
fi

for stage in "${STAGES[@]}"; do
    case "$stage" in
        rprime)
            echo "=== stage rprime: measure exported resizer netlist (standard flow) ==="
            .venv/Scripts/python.exe "$EXP/measure.py" --arms Rprime --circuits "$CIRCUITS" --utils "$UTILS"
            echo "=== stage rprime done rc=$? ==="
            ;;
        rf)
            echo "=== stage rf: FAECO-P on resizer endpoint ==="
            bash "$EXP/run_rf.sh" s382 s641 s832
            echo "=== stage rf done rc=$? ==="
            ;;
        rmeasure)
            echo "=== stage rmeasure: measure RF endpoint netlists ==="
            .venv/Scripts/python.exe "$EXP/measure.py" --arms RF --circuits "$CIRCUITS" --utils "$UTILS"
            echo "=== stage rmeasure done rc=$? ==="
            ;;
        *)
            echo "unknown stage: $stage"
            ;;
    esac
done

echo "PILOT_DONE"