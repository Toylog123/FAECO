#!/usr/bin/env bash
# ==============================================================================
# FAECO V5 Master Experiment Launcher (WSL2 Ubuntu, pinned exclusive CPU 0-5)
# Usage:
#   bash run_all_v5_experiments.sh              # Run all 5 stages sequentially (skips finished)
#   bash run_all_v5_experiments.sh --stage 1    # Run only Stage 1 (~5 min)
#   bash run_all_v5_experiments.sh --stage 2    # Run only Stage 2 (~15 min)
#   bash run_all_v5_experiments.sh --stage 3    # Run only Stage 3 (~45 min)
#   bash run_all_v5_experiments.sh --stage 4    # Run only Stage 4 (~40 min)
#   bash run_all_v5_experiments.sh --stage 5    # Run only Stage 5 (~35 min)
#   bash run_all_v5_experiments.sh --force      # Re-run even if verified JSON exists
# ==============================================================================
set -euo pipefail

EVID_DIR="/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_v5_revision_20261126"
LOG_FILE="/home/toylog/faeco_v5_master.log"
STAGE="all"
FORCE_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage) STAGE="$2"; shift 2 ;;
    --force) FORCE_FLAG="--force"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

run_stage() {
  local num="$1"
  local script="$2"
  local json_out="$3"
  local est="$4"
  echo "" | tee -a "$LOG_FILE"
  echo "========================================================================" | tee -a "$LOG_FILE"
  echo "[$(date '+%F %T')] STAGE ${num}: ${script} (est. ${est})" | tee -a "$LOG_FILE"
  echo "========================================================================" | tee -a "$LOG_FILE"
  if [[ -z "$FORCE_FLAG" && -f "${EVID_DIR}/${json_out}" && "$num" != "2" && "$num" != "3" && "$num" != "4" ]]; then
    echo "[SKIP] ${json_out} already exists (pass --force to re-run)." | tee -a "$LOG_FILE"
    return 0
  fi
  taskset -c 0-5 python3 "${EVID_DIR}/${script}" ${FORCE_FLAG} 2>&1 | tee -a "$LOG_FILE"
  echo "[$(date '+%F %T')] STAGE ${num} FINISHED -> ${EVID_DIR}/${json_out}" | tee -a "$LOG_FILE"
}

echo "[$(date '+%F %T')] FAECO V5 Master Launcher started (STAGE=${STAGE}, FORCE=${FORCE_FLAG:-none})" | tee -a "$LOG_FILE"

[[ "$STAGE" == "all" || "$STAGE" == "1" ]] && run_stage 1 "run_v5_step1_power_7nm_det.py" "V5_STEP1_POWER_7NM_DET_VERIFIED.json" "~5-8 min"
[[ "$STAGE" == "all" || "$STAGE" == "2" ]] && run_stage 2 "run_v5_step2_dedup_and_native_protected.py" "V5_STEP2_DEDUP_NATIVE_VERIFIED.json" "~15 min"
[[ "$STAGE" == "all" || "$STAGE" == "3" ]] && run_stage 3 "run_v5_step3_multibudget_online.py" "V5_STEP3_MULTIBUDGET_VERIFIED.json" "~45 min"
[[ "$STAGE" == "all" || "$STAGE" == "4" ]] && run_stage 4 "run_v5_step4_probe_sensitivity.py" "V5_STEP4_PROBE_SENS_VERIFIED.json" "~40 min"
[[ "$STAGE" == "all" || "$STAGE" == "5" ]] && run_stage 5 "run_v5_step5_10k_timing_closed.py" "V5_STEP5_10K_TIMING_CLOSED_VERIFIED.json" "~35 min"

echo "" | tee -a "$LOG_FILE"
echo "================ V5 VERIFIED RECEIPTS SHA-256 SUMMARY ================" | tee -a "$LOG_FILE"
sha256sum "${EVID_DIR}"/V5_*_VERIFIED.json 2>/dev/null | tee -a "$LOG_FILE" || true
echo "[$(date '+%F %T')] ALL REQUESTED V5 STAGES COMPLETE." | tee -a "$LOG_FILE"
