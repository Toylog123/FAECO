#!/usr/bin/env bash
set -euo pipefail
orfs=/home/toylog/faeco_eda/orfs/flow
build=/home/toylog/faeco_tcad_ibex_20261123/control_sky130
openroad=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
yosys=/usr/local/bin/yosys
config="$orfs/designs/sky130hd/ibex/config.mk"
sdc="$orfs/designs/sky130hd/ibex/constraint.sdc"
mkdir -p "$build"
git -C "$orfs" rev-parse HEAD
git -C "$orfs" ls-tree HEAD designs/src/ibex_sv
sha256sum "$config" "$sdc" "$openroad" "$yosys"
"$openroad" -version
"$yosys" -V
target="$build/logs/sky130hd/ibex/base/6_report.log"
set -x
timeout --kill-after=15s 3600s /usr/bin/time -p make -C "$orfs" \
  "DESIGN_CONFIG=$config" "WORK_HOME=$build" FLOW_VARIANT=base NUM_CORES=4 \
  "OPENROAD_EXE=$openroad" "YOSYS_EXE=$yosys" "$target"
