#!/bin/bash
# Re-start the F2 batch and/or its post-processing chain.
#
# Usage: bash scratch/restart_f2.sh [batch|chain|all]
#
# WHY THIS IS SAFE TO RE-RUN
# --------------------------
# run_labels.sh skips any job whose run directory already has an rc.tsv, so
# the jobs that finished before a restart are NOT repeated; only the remaining
# ones (plus any that were in flight and therefore have no rc.tsv) are run.
# The batch is resumable by construction.  The post-processing chain is
# idempotent too: it waits for I2 to reach the promised key count, then builds
# the labels, runs the probe and writes a machine receipt.
set -u
ROOT=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
ITC=$ROOT/experiments/20261024_physical_labels_itc99
WHAT="${1:-all}"
cd "$ROOT" || exit 1

count_done() {
  local dir="$1" total=0
  [ -d "$dir" ] || { echo 0; return; }
  for d in "$dir"/*/; do
    [ -f "$d/rc.tsv" ] && total=$((total + 1))
  done
  echo $total
}

echo "$(date '+%F %H:%M:%S') F2 resume ($WHAT): I2 already done = $(count_done "$ITC/runs/I2")/1207"

if [ "$WHAT" = "batch" ] || [ "$WHAT" = "all" ]; then
  setsid nohup bash scratch/batch_supervisor.sh f2 \
    "$ROOT/scratch/itc99_f2_status.txt" \
    "$ROOT/scratch/itc99_f2_supervisor.log" \
    jobs_itc99_f2.tsv:I2 >> "$ROOT/scratch/itc99_f2_launcher.log" 2>&1 < /dev/null &
  echo "  batch supervisor launched: pid=$!"
fi

if [ "$WHAT" = "chain" ] || [ "$WHAT" = "all" ]; then
  setsid nohup bash scratch/finalize_f2_chain.sh >> "$ROOT/scratch/f2_chain_launcher.out" 2>&1 < /dev/null &
  echo "  post-processing chain launched: pid=$!"
fi

sleep 15
echo "$(date '+%F %H:%M:%S') --- verification ---"
ps -eo pid,ppid,sid,etimes,stat,cmd | grep -E 'batch_supervisor|finalize_f2_chain' | grep -v grep
echo "I2 now: $(count_done "$ITC/runs/I2")/1207"
echo "openroad: $(pgrep -c openroad 2>/dev/null || echo 0)"
