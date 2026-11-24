#!/usr/bin/env bash
set -euo pipefail

evidence=project_docs/evidence/tcad_ibex_20261123
holdout=project_docs/evidence/tcad_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow
design=${1:-}
version=${2:-v1}
if ! [[ "$version" =~ ^v[1-9][0-9]*$ ]]; then
  echo "Version must be v followed by a positive integer" >&2
  exit 2
fi

case "$design" in
  gcd)
    work=/home/toylog/faeco_tcad_sky_holdout_20261123
    control="$work/gcd/results/sky130hd/gcd/base"
    qualify="$work/gcd/qualification/CONTROL.json"
    drc="$work/gcd/reports/sky130hd/gcd/base/5_route_drc.rpt"
    sta="$holdout/sta_holdout.py"
    sec="$holdout/prove_holdout.py"
    limit=720
    ;;
  ibex)
    work=/home/toylog/faeco_tcad_ibex_20261123
    control="$work/hold_repair_sky130_03/endpoint"
    qualify="$control/qualification/CONTROL.json"
    drc="$control/drc.rpt"
    sta="$evidence/sky130_control/sta_from_odb.py"
    sec="$evidence/prove_ibex.py"
    limit=1350
    ;;
  *)
    echo "Usage: run_pin_access_ab.sh {gcd|ibex} [version]" >&2
    exit 2
    ;;
esac

exec timeout --kill-after=10s "${limit}s" taskset -c 6-11 python3 -B "$evidence/probe_duplicate_pin_access.py" \
  --pdk sky130hd --control-dir "$control" --control-drc "$drc" \
  --original-sdc "$flow/designs/sky130hd/$design/constraint.sdc" \
  --views-json "$qualify" --sta "$sta" --sec "$sec" \
  --embedded-guides --zero-reextract --threads 4 --max-evals 6 --batch-size 3 \
  --droute-iters 64 --route-timeout 1500 --sta-timeout 180 --sec-timeout 210 \
  --report-setup-endpoints --matrix "$work/${design}_hold_aware_v1" \
  --out "$work/${design}_pin_access_ab_$version"
