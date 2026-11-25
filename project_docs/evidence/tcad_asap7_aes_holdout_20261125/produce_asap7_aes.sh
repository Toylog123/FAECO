#!/usr/bin/env bash
set -euo pipefail
root=/home/toylog/faeco_tcad_asap7_aes_20261125_v1
flow=/home/toylog/faeco_eda/orfs/flow
or_source=/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a
openroad=$or_source/bazel-bin/openroad
yosys=/usr/local/bin/yosys
work=$root/asap7/aes
design=$flow/designs/asap7/aes
rtl=$flow/designs/src/aes
target=$work/logs/asap7/aes/base/6_report.log
mkdir -p -- "$root/asap7"
mkdir -- "$work"
{
  git -C "$flow" rev-parse HEAD
  git -C "$flow" ls-tree HEAD designs/src/aes
  git -C "$or_source" rev-parse HEAD
  sha256sum "$design/config.mk" "$design/constraint.sdc" "$flow/Makefile" "$flow/platforms/asap7/config.mk" "$flow/platforms/asap7/rcx_patterns.rules" "$openroad" "$yosys" "$rtl"/*.v
} > "$work/input_manifest.log"
cmd=(timeout --kill-after=15s 2400s taskset -c 0-5 /usr/bin/time -p make --no-print-directory -j1 -C "$flow" "DESIGN_CONFIG=$design/config.mk" "WORK_HOME=$work" FLOW_VARIANT=base NUM_CORES=4 "OPENROAD_EXE=$openroad" "YOSYS_EXE=$yosys" "$target")
printf '%q ' "${cmd[@]}" > "$work/command.sh"
printf '\n' >> "$work/command.sh"
printf 'START %s %s\n' "$(date -Is)" "$work"
status=0
"${cmd[@]}" > "$work/producer.log" 2>&1 || status=$?
printf '%s\n' "$status" > "$work/producer.rc"
tail -20 "$work/producer.log"
exit "$status"
