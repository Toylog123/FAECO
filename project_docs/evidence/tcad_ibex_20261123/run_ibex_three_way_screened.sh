#!/usr/bin/env bash
# Matched fixed-origin Ibex experiment: one frozen screened pool, three schedulers.
set -euo pipefail

evidence=project_docs/evidence/tcad_ibex_20261123
flow=/home/toylog/faeco_eda/orfs/flow
ibex=/home/toylog/faeco_tcad_ibex_20261123
control="$ibex/hold_repair_sky130_03/endpoint"
screen=/home/toylog/faeco_tcad_screen_workers_20261124_v1/ibex_a2_w4
out=${1:-$ibex/ibex_screened_single_pa_three_way_20261124_v1}

exec bash code/scripts/run_with_timeout.sh 6000 taskset -c 6-11 python3 -B \
    "$evidence/run_screened_matrix.py" --pdk sky130hd \
    --control-dir "$control" --control-drc "$control/drc.rpt" \
    --original-sdc "$flow/designs/sky130hd/ibex/constraint.sdc" \
    --views-json "$control/qualification/CONTROL.json" \
    --sta "$evidence/sky130_control/sta_from_odb.py" --sec "$evidence/prove_ibex.py" \
    --screen-pool "$screen/screen_pool.json" --screen-receipt "$screen/screen_receipt.json" \
    --embedded-guides --zero-reextract --single-pin-access --report-setup-endpoints \
    --threads 4 --max-evals 6 --batch-size 3 --droute-iters 64 \
    --route-timeout 1500 --sta-timeout 180 --sec-timeout 210 \
    --wall-limit-seconds 720 --target-area-pct .01 --screened-hold-aware --out "$out"
