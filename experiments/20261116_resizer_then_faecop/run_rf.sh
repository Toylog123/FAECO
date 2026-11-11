#!/usr/bin/env bash
# RF arm: run FAECO-P on top of the exported (post-resizer) netlist.
# Usage: bash experiments/20261116_resizer_then_faecop/run_rf.sh [circuit ...]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXP="$SCRIPT_DIR"
OUTDIR="${RF_OUTDIR:-arms/RF}"
# The Python entry point is a Windows interpreter: an MSYS-style path such as
# /d/Baidu/... would resolve to D:\d\Baidu\... and silently create a new tree.
# Always hand it a Windows path.
EXP_WIN="$(cygpath -w "$EXP")"
cd "$EXP/../.."

export MSYS_NO_PATHCONV=1
export PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

if [ "$#" -gt 0 ]; then
    CIRCUITS=("$@")
else
    CIRCUITS=(s382 s641 s832)
fi

for circuit in "${CIRCUITS[@]}"; do
    out="$EXP/$OUTDIR/$circuit"

    if [ -f "$out/outerloop_result.json" ]; then
        echo "[$circuit] already done, skipping"
        continue
    fi

    mkdir -p "$out"
    # The exported netlist is a *flattened* netlist: write_verilog emits the
    # clocked cells as escaped names such as \DFF_14/_0_.  Rename them to the
    # hierarchical W1 form (DFF_14) so the mechanism's FF model applies; this
    # only renames instances, the topology is untouched (see PREREG A3).
    .venv/Scripts/python.exe "$EXP/_sanitize_names.py" "$circuit" || exit 1
    src="$EXP/exports/$circuit/resized_gate_flat.v"
    if [ ! -f "$src" ]; then
        echo "[$circuit] MISSING exported netlist: $src"
        continue
    fi
    # Always refresh the mechanism input from the sanitized export: leaving a
    # stale mapped.v behind (for example from an earlier run with the raw
    # escaped-name export) silently feeds the wrong netlist to the mechanism.
    cp "$src" "$out/mapped.v"

    echo "[$circuit] running FAECO-P on resizer endpoint ..."
    .venv/Scripts/python.exe code/scripts/run_outerloop_real_wns.py \
        --circuit "$circuit" \
        --period 0.5 \
        --output-dir "$EXP_WIN/$OUTDIR" \
        --max-iterations 20 \
        --max-patches 20 \
        --sta-budget 500 \
        --wall-timeout-s 3600 \
        --candidates-per-iteration 8 \
        --max-instances 8 \
        --joint-k 2 \
        --joint-enumerate-depth 0 \
        --strategies R,G,B \
        --enable-buffer \
        --early-stop \
        --no-feedback \
        --no-proxy-ranking \
        --disable-topology \
        --skip-mapping \
        --cut-search-policy weighted_st \
        --cut-sources full \
        --node-cost-mode configured \
        --init-boundary-penalty 1 \
        --init-size-penalty 1 \
        --init-critical-coverage-reward 1 \
        --init-verification-cost-penalty 1 \
        --init-equivalence-stability-reward 1 \
        --workers 4 \
        --physical-gate \
        --physical-backend placed_ens \
        --placement-utils 0.30,0.35,0.40 \
        --relaxed-instance-parse \
        --seed 1

    rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "[$circuit] FAILED rc=$rc"
    fi
done

echo "All RF runs completed."