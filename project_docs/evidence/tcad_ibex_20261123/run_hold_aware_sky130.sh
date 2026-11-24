#!/usr/bin/env bash
# Run a fresh screened FAECO confirmation from the matching frozen matrix inputs.
set -euo pipefail

evidence=project_docs/evidence/tcad_ibex_20261123
holdout=project_docs/evidence/tcad_holdout_20261123
ibex=/home/toylog/faeco_tcad_ibex_20261123
sky130=/home/toylog/faeco_tcad_sky_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow

design=${1:-}
case "$design" in
  ibex)
    control="$ibex/hold_repair_sky130_03/endpoint"
    screen="$ibex/screen_ibex_v2"
    out="$ibex/ibex_hold_aware_v1"
    drc="$control/drc.rpt"
    qualify="$control/qualification/CONTROL.json"
    sta="$evidence/sky130_control/sta_from_odb.py"
    sec="$evidence/prove_ibex.py"
    driver=("$evidence/run_screened_matrix.py")
    ;;
  gcd)
    control="$sky130/gcd/results/sky130hd/gcd/base"
    screen="$sky130/gcd_screen_v1"
    out="$sky130/gcd_hold_aware_v1"
    drc="$sky130/gcd/reports/sky130hd/gcd/base/5_route_drc.rpt"
    qualify="$sky130/gcd/qualification/CONTROL.json"
    sta="$holdout/sta_holdout.py"
    sec="$holdout/prove_holdout.py"
    driver=("$evidence/run_holdout_screened.py" matrix --top gcd
      --routing-config "$flow/platforms/sky130hd/fastroute.tcl"
      --helper-source "$holdout/holdout_tools.py"
      --helper-source "$evidence/sky130_control/sta_from_odb.py"
      --helper-source "$evidence/prove_ibex.py")
    ;;
  *)
    echo 'usage: run_hold_aware_sky130.sh {ibex|gcd}' >&2
    exit 2
    ;;
esac

exec timeout --kill-after=10s 2400s taskset -c 6-11 python3 -B "${driver[@]}" \
  --pdk sky130hd --control-dir "$control" --control-drc "$drc" \
  --original-sdc "$flow/designs/sky130hd/$design/constraint.sdc" \
  --views-json "$qualify" --sta "$sta" --sec "$sec" \
  --screen-pool "$screen/screen_pool.json" --screen-receipt "$screen/screen_receipt.json" \
  --embedded-guides --zero-reextract --threads 4 --max-evals 6 --batch-size 3 \
  --droute-iters 64 --route-timeout 1500 --sta-timeout 180 --sec-timeout 210 \
  --report-setup-endpoints --wall-limit-seconds 720 --target-area-pct .01 \
  --hold-aware-only --out "$out"
