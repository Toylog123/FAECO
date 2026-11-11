#!/usr/bin/env bash
# Run FAECO-P (post-placement coverage-first) on ISCAS89 circuits.
# Usage: bash experiments/20261115_p1_resizer_vs_faeco/run_faecop.sh [circuit ...]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXP="$SCRIPT_DIR"
cd "$EXP/../.."

export MSYS_NO_PATHCONV=1
export PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

if [ "$#" -gt 0 ]; then
    CIRCUITS=("$@")
else
    CIRCUITS=(s27 s382 s420 s641 s713 s820 s832 s953)
fi

for circuit in "${CIRCUITS[@]}"; do
    OUTDIR="${FAECOP_OUTDIR:-arms/FAECO-P}"
    out="$EXP/$OUTDIR/$circuit"

    if [ -f "$out/outerloop_result.json" ]; then
        echo "[$circuit] already done, skipping"
        continue
    fi

    mkdir -p "$out"
    if [ ! -f "$out/mapped.v" ]; then
        cp "experiments/20261016_r22_cut_ablation_v3/W1/$circuit/mapped.v" "$out/mapped.v"
    fi

    echo "[$circuit] running FAECO-P ..."
    .venv/Scripts/python.exe code/scripts/run_outerloop_real_wns.py \
        --circuit "$circuit" \
        --period 0.5 \
        --output-dir "$EXP/$OUTDIR" \
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
        --seed 1

    rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "[$circuit] FAILED rc=$rc"
    fi
done

echo "All FAECO-P runs completed."
