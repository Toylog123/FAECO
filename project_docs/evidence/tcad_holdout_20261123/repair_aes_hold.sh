#!/usr/bin/env bash
set -euo pipefail
base=/home/toylog/faeco_tcad_sky_holdout_20261123/aes
flow=/home/toylog/faeco_eda/orfs/flow
evidence=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
openroad=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
export FAECO_HOLDOUT_SOURCE=$base/results/sky130hd/aes/base
export FAECO_HOLDOUT_REPAIR=$base/ss_hold_repair_v1
export FAECO_HOLDOUT_MARGIN_NS=0.10
export FAECO_HOLDOUT_FASTROUTE=$flow/designs/sky130hd/aes/fastroute.tcl
export FAECO_HOLDOUT_INVENTORY=$evidence/../tcad_ibex_20261123/sky130_control/recovery/hold_repair_sky130_03/inventory_utils.tcl
mkdir "$FAECO_HOLDOUT_REPAIR"
sha256sum "$openroad" "$evidence/repair_sky_holdout.tcl" "$FAECO_HOLDOUT_FASTROUTE" "$FAECO_HOLDOUT_INVENTORY" \
  "$FAECO_HOLDOUT_SOURCE"/6_final.{odb,sdc,spef,v,def} > "$FAECO_HOLDOUT_REPAIR/input_manifest.log"
set +e
timeout --kill-after=10s 1800s /usr/bin/time -p "$openroad" -threads 4 -no_init -exit "$evidence/repair_sky_holdout.tcl" \
  > "$FAECO_HOLDOUT_REPAIR/repair.log" 2>&1
rc=$?
set -e
echo "$rc" > "$FAECO_HOLDOUT_REPAIR/repair.rc"
exit "$rc"
