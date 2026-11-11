#!/usr/bin/env bash
# Run our ECO (FAECO-P) on top of the post-CTS resizer endpoint of one circuit.
#
# usage: run_rf.sh [circuits...]
#   default circuits: s382 s641 s832
#
# Input  : exports/<c>_postcts/resized_gate_flat.v   (post-CTS export, names normalised)
# Output : arms/RFpost/<c>/                          (same flag set as the P1 pilot RF arm)
#
# Notes
#   * --output-dir must be a WINDOWS path: the Python side resolves MSYS /d/...
#     to D:\d\..., silently writing nowhere (2026-11-11 lesson).
#   * mapped.v is refreshed on every run: a stale copy from an earlier attempt
#     is what made the first RF run report "no critical instances".
#   * the post-CTS netlist contains a clock tree, so the *endpoint* flow runs
#     with skip_clock_tree=True (see measure.py); the ECO itself is unchanged.
set -euo pipefail

EXP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$EXP/../.." && pwd)"
EXP_WIN="$(cygpath -w "$EXP")"

if [ "$#" -gt 0 ]; then
  CIRCUITS=("$@")
else
  CIRCUITS=(s382 s641 s832)
fi

export MSYS_NO_PATHCONV=1 PYTHONUTF8=1
export PATH="/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:/c/Windows/System32:$PATH"

cd "$ROOT"

for c in "${CIRCUITS[@]}"; do
  src="$EXP/exports/${c}_postcts/resized_gate_flat.v"
  if [ ! -f "$src" ]; then
    echo "SKIP $c: missing $src"
    continue
  fi
  out="$EXP/arms/RFpost/$c"
  mkdir -p "$out"
  cp -f "$src" "$out/mapped.v"
  echo "=== $c: running FAECO-P on the post-CTS endpoint"
  .venv/Scripts/python.exe code/scripts/run_outerloop_real_wns.py \
    --circuit "$c" \
    --period 0.5 \
    --output-dir "$EXP_WIN\\arms\\RFpost\\$c" \
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
    --seed 1 2>&1 | tee "$out/runner.log" | tail -5
done

echo "All post-CTS RF runs completed."