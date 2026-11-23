#!/usr/bin/env bash
set -euo pipefail
base=/home/toylog/faeco_tcad_sky_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow
openroad=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
yosys=/usr/local/bin/yosys
out=$base/gcd
mkdir "$out"
config=$flow/designs/sky130hd/gcd/config.mk
sdc=$flow/designs/sky130hd/gcd/constraint.sdc
target=$out/logs/sky130hd/gcd/base/6_report.log
{
    git -C "$flow" rev-parse HEAD
    git -C "$flow" ls-tree HEAD designs/src/gcd
    sha256sum "$config" "$sdc" "$openroad" "$yosys"
    "$openroad" -version
    "$yosys" -V
    echo "ORFS FLOW_VARIANT=base NUM_CORES=2 DESIGN_CONFIG=$config WORK_HOME=$out target=$target"
} | tee "$out/input_manifest.log"
set +e
timeout --kill-after=10s 1200s /usr/bin/time -p make -C "$flow" "DESIGN_CONFIG=$config" "WORK_HOME=$out" FLOW_VARIANT=base NUM_CORES=2 "OPENROAD_EXE=$openroad" "YOSYS_EXE=$yosys" "$target" > "$out/producer.log" 2>&1
rc=$?
set -e
echo "$rc" > "$out/producer.rc"
exit "$rc"
