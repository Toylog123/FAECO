#!/usr/bin/env bash
# Use the frozen Ibex and GCD controllers for a serial screen timing series.
set -euo pipefail
evidence=project_docs/evidence/tcad_ibex_20261123
holdout=project_docs/evidence/tcad_holdout_20261123
sky130=/home/toylog/faeco_tcad_sky_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow
raw=/home/toylog/faeco_tcad_screen_workers_20261124_v1
design=${1:-}
workers=${2:-}
slot=${3:-}
if [[ ! "$workers" =~ ^[14]$ || ! "$slot" =~ ^[ab][12]$ ]]; then
  echo 'usage: run_screen_workers_benchmark.sh {ibex|gcd} {1|4} {a1|a2|b1|b2}' >&2
  exit 2
fi

case "$design" in
  ibex)
    control=/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint
    drc="$control/drc.rpt"
    qualify="$control/qualification/CONTROL.json"
    sec="$evidence/prove_ibex.py"
    driver=("$evidence/screen_sky130_candidates.py")
    ;;
  gcd)
    control="$sky130/gcd/results/sky130hd/gcd/base"
    drc="$sky130/gcd/reports/sky130hd/gcd/base/5_route_drc.rpt"
    qualify="$sky130/gcd/qualification/CONTROL.json"
    sec="$holdout/prove_holdout.py"
    driver=("$evidence/run_holdout_screened.py" screen --top gcd)
    ;;
  *)
    echo 'unknown control' >&2
    exit 2
    ;;
esac

mkdir -p "$raw"
exec bash code/scripts/run_with_timeout.sh 420 taskset -c 6-11 python3 -B "${driver[@]}" \
  --pdk sky130hd --control-dir "$control" --control-drc "$drc" \
  --original-sdc "$flow/designs/sky130hd/$design/constraint.sdc" --views-json "$qualify" \
  --sec "$sec" \
  --embedded-guides --sta-timeout 180 --screen-workers "$workers" \
  --out "$raw/${design}_${slot}_w${workers}"
