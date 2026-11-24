#!/usr/bin/env bash
# Produce and read back a new native SKY130HD JPEG holdout from the original SDC.
set -euo pipefail

flow=/home/toylog/faeco_eda/orfs/flow
openroad=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
yosys=/usr/local/bin/yosys
base=${1:-/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/sky130hd}
work="$base/jpeg"
design="$flow/designs/sky130hd/jpeg"
target="$work/logs/sky130hd/jpeg/base/6_report.log"
mkdir -p -- "$base"
mkdir -- "$work"

{
    git -C "$flow" rev-parse HEAD
    git -C "$flow" ls-tree HEAD designs/src/jpeg
    sha256sum "$design/config.mk" "$design/constraint.sdc" "$design/fastroute.tcl" "$openroad" "$yosys"
    "$openroad" -version
    "$yosys" -V
    printf 'ORFS FLOW_VARIANT=base NUM_CORES=4 DESIGN_CONFIG=%s WORK_HOME=%s target=%s\n' \
        "$design/config.mk" "$work" "$target"
} > "$work/input_manifest.log"

echo "Building native JPEG CONTROL in $work"
status=0
timeout --kill-after=15s 3600s taskset -c 6-11 /usr/bin/time -p make --no-print-directory -j1 -C "$flow" \
    DESIGN_CONFIG="$design/config.mk" WORK_HOME="$work" FLOW_VARIANT=base NUM_CORES=4 \
    OPENROAD_EXE="$openroad" YOSYS_EXE="$yosys" "$target" \
    > "$work/producer.log" 2>&1 || status=$?
printf '%s\n' "$status" > "$work/producer.rc"
if ((status != 0)); then
    echo "Native producer exited $status. See $work/producer.log" >&2
    exit "$status"
fi

timeout --kill-after=5s 420s taskset -c 6-11 python3 -B - "$base" <<'PY' | tee "$work/qualification_stdout.log"
import sys
from pathlib import Path

sys.path.insert(0, "project_docs/evidence/tcad_holdout_20261123")
import qualify_sky_holdout as qualification

qualification.BASE = Path(sys.argv[1]).resolve(strict=True)
qualification.DESIGNS = {"jpeg": ("jpeg_encoder", (5.0, 0.2, "clk", "clk", 1.175))}
qualification.qualify("jpeg")
PY
