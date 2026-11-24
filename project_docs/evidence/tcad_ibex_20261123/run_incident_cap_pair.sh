#!/usr/bin/env bash
set -euo pipefail

evidence=project_docs/evidence/tcad_ibex_20261123
holdout=project_docs/evidence/tcad_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow
ibex=/home/toylog/faeco_tcad_ibex_20261123
sky130=/home/toylog/faeco_tcad_sky_holdout_20261123
screen=/home/toylog/faeco_tcad_screen_workers_20261124_v1
design=${1:-}
case "$design" in
  ibex)
    base="$ibex"
    control="$base/hold_repair_sky130_03/endpoint"
    drc="$control/drc.rpt"
    qualify="$control/qualification/CONTROL.json"
    sta="$evidence/sky130_control/sta_from_odb.py"
    sec="$evidence/prove_ibex.py"
    probe="$screen/ibex_a2_w4"
    driver=("$evidence/run_screened_matrix.py")
    timeout=4200
    ;;
  gcd)
    base="$sky130"
    control="$base/gcd/results/sky130hd/gcd/base"
    drc="$base/gcd/reports/sky130hd/gcd/base/5_route_drc.rpt"
    qualify="$base/gcd/qualification/CONTROL.json"
    sta="$holdout/sta_holdout.py"
    sec="$holdout/prove_holdout.py"
    probe="$screen/gcd_b2_w4"
    driver=("$evidence/run_holdout_screened.py" matrix --top gcd
      --routing-config "$flow/platforms/sky130hd/fastroute.tcl"
      --helper-source "$holdout/holdout_tools.py"
      --helper-source "$evidence/sky130_control/sta_from_odb.py"
      --helper-source "$evidence/prove_ibex.py")
    timeout=1200
    ;;
  *)
    echo 'usage: run_incident_cap_pair.sh {ibex|gcd} [out]' >&2
    exit 2
    ;;
esac

out=${2:-$base/${design}_incident_cap_pair_20261124_v1}
exec bash code/scripts/run_with_timeout.sh "$timeout" taskset -c 6-11 python3 -B "${driver[@]}" \
  --pdk sky130hd --control-dir "$control" --control-drc "$drc" \
  --original-sdc "$flow/designs/sky130hd/$design/constraint.sdc" \
  --views-json "$qualify" --sta "$sta" --sec "$sec" \
  --screen-pool "$probe/screen_pool.json" --screen-receipt "$probe/screen_receipt.json" \
  --embedded-guides --zero-reextract --single-pin-access --report-setup-endpoints \
  --threads 4 --max-evals 6 --batch-size 3 --droute-iters 64 \
  --route-timeout 1500 --sta-timeout 180 --sec-timeout 210 \
  --wall-limit-seconds 720 --target-area-pct .01 --screened-risk-pair --out "$out"
