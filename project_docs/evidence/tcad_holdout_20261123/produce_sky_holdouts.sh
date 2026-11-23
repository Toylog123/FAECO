#!/usr/bin/env bash
set -euo pipefail
base=/home/toylog/faeco_tcad_sky_holdout_20261123
flow=/home/toylog/faeco_eda/orfs/flow
openroad=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
yosys=/usr/local/bin/yosys
mkdir -p "$base"
for design in aes gcd; do
    out="$base/$design"
    mkdir "$out"
    config="$flow/designs/sky130hd/$design/config.mk"
    sdc="$flow/designs/sky130hd/$design/constraint.sdc"
    target="$out/logs/sky130hd/$design/base/6_report.log"
    {
        git -C "$flow" rev-parse HEAD
        git -C "$flow" ls-tree HEAD "designs/src/$design"
        sha256sum "$config" "$sdc" "$openroad" "$yosys"
        "$openroad" -version
        "$yosys" -V
        echo "ORFS FLOW_VARIANT=base NUM_CORES=4 DESIGN_CONFIG=$config WORK_HOME=$out target=$target"
    } | tee "$out/input_manifest.log"
    printf 'Producing %s: %s\n' "$design" "$target"
    set +e
    timeout --kill-after=15s 3600s /usr/bin/time -p make -C "$flow" "DESIGN_CONFIG=$config" "WORK_HOME=$out" FLOW_VARIANT=base NUM_CORES=4 "OPENROAD_EXE=$openroad" "YOSYS_EXE=$yosys" "$target" > "$out/producer.log" 2>&1
    rc=$?
    set -e
    echo "$rc" > "$out/producer.rc"
    printf 'Producer %s rc=%d\n' "$design" "$rc"
done
