#!/bin/bash
# Post-process the F2 (third physical realisation) batch once it is complete.
#
# WHY A SEPARATE CHAIN: F2 is a side experiment whose job table is NOT
# registered in build_dataset_itc99.py's BATCHES, so it does not belong to the
# main analysis chain.  But it still has to be labelled and analysed, and
# leaving that to a human means the result silently waits.  This chain waits
# for the batch, builds the F2 labels with their self-checks, and runs the
# three-implementation stability probe.
#
# ORDER MATTERS:
#   build_f2_labels.py FIRST, because the probe consumes f2_labels.jsonl.
#   The probe refuses to call F2 "available" unless the label file is complete,
#   so running it first would only report "not complete".
set -u
ROOT=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
ITC=$ROOT/experiments/20261024_physical_labels_itc99
LOG=$ROOT/scratch/f2_chain.log
DEADLINE=$(( $(date +%s) + 43200 ))

count_done() {
  local dir="$1" total=0
  [ -d "$dir" ] || { echo 0; return; }
  for d in "$dir"/*/; do
    [ -f "$d/rc.tsv" ] && total=$((total+1))
  done
  echo $total
}

echo "$(date '+%F %H:%M:%S') waiting for the F2 (I2) batch to finish" >> "$LOG"
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  i2=$(count_done "$ITC/runs/I2")
  echo "$(date '+%F %H:%M:%S') I2=$i2/1207" >> "$LOG"
  [ "$i2" -ge 1207 ] && break
  sleep 120
done

i2=$(count_done "$ITC/runs/I2")
if [ "$i2" -lt 1207 ]; then
  echo "$(date '+%F %H:%M:%S') TIMEOUT: I2=$i2/1207 -- nothing analysed" >> "$LOG"
  exit 1
fi

cd "$ROOT" || exit 1
echo "$(date '+%F %H:%M:%S') F2 batch complete ($i2/1207) -> building the labels" >> "$LOG"

echo "=== 1. build the F2 labels (runs its digest-convention and completeness self-checks) ===" >> "$LOG"
.venv/Scripts/python.exe experiments/20261024_physical_labels_itc99/tools/build_f2_labels.py >> "$LOG" 2>&1
rc_labels=$?
echo "$(date '+%F %H:%M:%S') build_f2_labels.py exit=$rc_labels" >> "$LOG"

echo "=== 2. three-implementation stability probe ===" >> "$LOG"
.venv/Scripts/python.exe experiments/20261024_physical_labels/tools/impl_stability_probe.py --family itc99 >> "$LOG" 2>&1
rc_probe=$?
echo "$(date '+%F %H:%M:%S') impl_stability_probe.py exit=$rc_probe" >> "$LOG"

echo "=== 3. machine receipt (the log entry transcribes this) ===" >> "$LOG"
.venv/Scripts/python.exe scratch/f2_chain_receipt.py >> "$LOG" 2>&1
rc_receipt=$?
echo "$(date '+%F %H:%M:%S') receipt exit=$rc_receipt" >> "$LOG"

echo "$(date '+%F %H:%M:%S') F2 chain done (labels=$rc_labels probe=$rc_probe receipt=$rc_receipt)" >> "$LOG"
