#!/usr/bin/env bash
# Run the V5 measurements in protocol order on the pinned WSL inputs.
set -euo pipefail

EVID_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
LOG_FILE="${FAECO_V5_LOG_FILE:-/home/toylog/faeco_v5_master.log}"
LOCK_FILE="${FAECO_V5_EDA_LOCK:-/home/toylog/faeco_v5_eda.lock}"
CPU_LIST="${FAECO_V5_CPUS:-0-5}"
STAGE=all
FORCE=0
MATCHED_ZERO=0
PLAN=0
OUTPUT_ROOT=""

usage() {
  cat <<'HELP'
Usage: bash run_all_v5_experiments.sh [--stage all|1|2|3|4|5]
                                    [--matched-zero] [--force]
                                    [--output-root DIR] [--plan]
  --matched-zero     Run only the two Stage 4 matched 0 s controls.
  --output-root DIR  Store and resume V5 outputs under DIR.
  --force            Create a fresh run-* child under the output root.
                     Defaults to /home/toylog/faeco_v5_reruns.
  --plan             Print the selected commands and outputs without running.
HELP
}

while (($#)); do
  case "$1" in
    --stage|--output-root)
      if (($# < 2)) || [[ "$2" == --* || -z "$2" ]]; then
        printf 'Missing value for %s\n' "$1" >&2
        exit 2
      fi
      if [[ "$1" == --stage ]]; then
        STAGE="$2"
      else
        OUTPUT_ROOT="$2"
      fi
      shift 2
      ;;
    --force) FORCE=1; shift ;;
    --matched-zero) MATCHED_ZERO=1; shift ;;
    --plan) PLAN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

case "$STAGE" in
  all|1|2|3|4|5) ;;
  *) printf 'Invalid stage: %s\n' "$STAGE" >&2; exit 2 ;;
esac
if ((MATCHED_ZERO)); then
  if [[ "$STAGE" != all && "$STAGE" != 4 ]]; then
    printf '%s\n' '--matched-zero requires Stage 4.' >&2
    exit 2
  fi
  STAGE=4
fi

if ((FORCE)); then
  OUTPUT_ROOT="${OUTPUT_ROOT:-/home/toylog/faeco_v5_reruns}"
  if ((PLAN)); then
    OUTPUT_ROOT="$OUTPUT_ROOT/run-<new>"
  else
    mkdir -p -- "$OUTPUT_ROOT"
    OUTPUT_ROOT="$(mktemp -d -- "$OUTPUT_ROOT/run-XXXXXXXX")"
  fi
fi

RECEIPT_DIR="$EVID_DIR"
if [[ -n "$OUTPUT_ROOT" ]]; then
  if [[ "$OUTPUT_ROOT" != /* ]]; then
    OUTPUT_ROOT="$PWD/$OUTPUT_ROOT"
  fi
  RECEIPT_DIR="$OUTPUT_ROOT/receipts"
fi

# The published Python drivers use module-level output paths. Redirect those
# paths only for isolated runs, leaving the scripts and all pinned inputs intact.
read -r -d '' ISOLATED_DRIVER <<'PY' || true
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

filename, raw_root, receipt, *options = sys.argv[1:]
sys.argv = [filename, *options]
sys.path.insert(0, str(Path(filename).parent))
spec = spec_from_file_location("faeco_v5_driver", filename)
driver = module_from_spec(spec)
sys.modules[spec.name] = driver
spec.loader.exec_module(driver)
if raw_root:
    driver.OUT_ROOT = Path(raw_root)
driver.OUT_JSON = Path(receipt)
raise SystemExit(driver.main())
PY

log() {
  printf '%s\n' "$*" | tee -a "$LOG_FILE"
}

run_driver() {
  local stage="$1" script="$2" raw_root="$3" receipt="$4"
  shift 4
  local -a command=(taskset -c "$CPU_LIST" python3 -B)
  if ((PLAN)); then
    printf '[Stage %s]' "$stage"
    printf ' %q' "${command[@]}" "$EVID_DIR/$script" "$@"
    printf '\n    Receipt: %s\n' "$receipt"
    if [[ -n "$OUTPUT_ROOT" ]]; then
      printf '    Isolated raw directory: %s\n' "$raw_root"
    fi
    return 0
  fi
  if [[ -n "$OUTPUT_ROOT" ]]; then
    command+=(-c "$ISOLATED_DRIVER" "$EVID_DIR/$script" "$raw_root" "$receipt" "$@")
  else
    command+=("$EVID_DIR/$script" "$@")
  fi
  log "[$(date '+%F %T')] Stage $stage: $script $*"
  local -a status
  if "${command[@]}" 2>&1 | tee -a "$LOG_FILE"; then
    return 0
  else
    status=("${PIPESTATUS[@]}")
    if ((status[1] != 0)); then
      return 2
    fi
    return "${status[0]}"
  fi
}

run_measurement() {
  local stage="$1" script="$2" filename="$3"
  shift 3
  if ((stage == 1 && ! PLAN)) && [[ -f "$RECEIPT_DIR/$filename" ]]; then
    log "[Stage 1] Existing receipt; resume skips it. Use --force for a fresh run."
    return 0
  fi
  run_driver "$stage" "$script" "${OUTPUT_ROOT:+$OUTPUT_ROOT/stage$stage}" "$RECEIPT_DIR/$filename" "$@"
}

receipt_identity() {
  if [[ -f "$1" ]]; then
    stat -c '%d:%i:%s:%y' -- "$1"
  fi
}

run_rejected_reference() {
  local variant="$1" raw_root="$2"
  shift 2
  local status_file="$raw_root/stage5_progress.json"
  local before rc
  if ((! PLAN)); then
    before="$(receipt_identity "$status_file")"
  fi
  if run_driver 5 run_v5_step5_10k_timing_closed.py "$raw_root" \
      "$RECEIPT_DIR/$(v5_qualification_name "$variant")" \
      --variant "$variant" --output-root "$raw_root" --reference-only; then
    if ((PLAN)); then
      printf '    Expected reference-only status: %s\n' "$*"
      return 0
    fi
    log "[Stage 5] $variant unexpectedly passed its historical reference-only control."
    return 1
  else
    rc=$?
  fi
  if ((rc != 1)) || [[ "$(receipt_identity "$status_file")" == "$before" ]]; then
    log "[Stage 5] $variant did not publish a fresh rejection; exit $rc."
    return "$rc"
  fi
  python3 -B - "$status_file" "$@" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

result = json.loads(Path(sys.argv[1]).read_bytes())
qualification = result["qualification"]
qualification_bytes = Path(qualification["path"]).read_bytes()
control = json.loads(qualification_bytes)
expected = sorted(sys.argv[2:])
if (result.get("status") != "reference_not_qualified" or result.get("arms") != {}
        or sorted(result.get("failures", [])) != expected
        or sorted(control.get("failures", [])) != expected
        or hashlib.sha256(qualification_bytes).hexdigest() != qualification["sha256"]):
    raise SystemExit("Stage 5 rejected for an unexpected reason")
PY
  if [[ -n "$OUTPUT_ROOT" ]]; then
    cp -- "$raw_root/qualification/CONTROL.json" "$RECEIPT_DIR/$(v5_qualification_name "$variant")"
  fi
  log "[Stage 5] $variant reproduced the expected qualification failure."
}

v5_qualification_name() {
  case "$1" in
    tc10ns) printf '%s\n' V5_STEP5_TC10NS_QUALIFICATION.json ;;
    tc40ns_mmmc) printf '%s\n' V5_STEP5_TC40NS_MMMC_QUALIFICATION.json ;;
    *) return 2 ;;
  esac
}

run_stage_five() {
  local root10="${OUTPUT_ROOT:+$OUTPUT_ROOT/stage5/tc10ns}"
  local root40="${OUTPUT_ROOT:+$OUTPUT_ROOT/stage5/tc40ns_mmmc}"
  local root_drv="${OUTPUT_ROOT:+$OUTPUT_ROOT/stage5/tc40ns_mmmc_drv}"
  run_rejected_reference tc10ns "${root10:-/home/toylog/faeco_v5_step5_riscv32i_tc_20261126_v1}" \
    SS:negative_setup SS:negative_hold
  run_rejected_reference tc40ns_mmmc "${root40:-/home/toylog/faeco_v5_step5_riscv32i_tc40ns_mmmc_20261126_v1}" \
    TT:absolute_electrical
  run_driver 5 run_v5_step5_10k_timing_closed.py \
    "${root_drv:-/home/toylog/faeco_v5_step5_riscv32i_tc40ns_mmmc_drv_20261127_v1}" \
    "$RECEIPT_DIR/V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json" \
    --variant tc40ns_mmmc_drv --output-root "${root_drv:-/home/toylog/faeco_v5_step5_riscv32i_tc40ns_mmmc_drv_20261127_v1}"
  if [[ -n "$OUTPUT_ROOT" ]] && ((! PLAN)); then
    cp -- "$root_drv/qualification/CONTROL.json" "$RECEIPT_DIR/V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json"
  fi
}

if ((! PLAN)); then
  mkdir -p -- "$RECEIPT_DIR"
  exec {lock_fd}>>"$LOCK_FILE"
  flock -x "$lock_fd"
  log "[$(date '+%F %T')] V5 launcher ($STAGE); receipts: $RECEIPT_DIR"
fi

if [[ "$STAGE" == all || "$STAGE" == 1 ]]; then
  run_measurement 1 run_v5_step1_power_7nm_det.py V5_STEP1_POWER_7NM_DET_VERIFIED.json
fi
if [[ "$STAGE" == all || "$STAGE" == 2 ]]; then
  run_measurement 2 run_v5_step2_dedup_and_native_protected.py V5_STEP2_DEDUP_NATIVE_VERIFIED.json
fi
if [[ "$STAGE" == all || "$STAGE" == 3 ]]; then
  run_measurement 3 run_v5_step3_multibudget_online.py V5_STEP3_MULTIBUDGET_VERIFIED.json
fi
if [[ "$STAGE" == all || "$STAGE" == 4 ]]; then
  if ((! MATCHED_ZERO)); then
    run_measurement 4 run_v5_step4_probe_sensitivity.py V5_STEP4_PROBE_SENS_VERIFIED.json
  fi
  run_measurement 4 run_v5_step4_probe_sensitivity.py V5_STEP4_PROBE_SENS_VERIFIED.json --matched-zero
fi
if [[ "$STAGE" == all || "$STAGE" == 5 ]]; then
  run_stage_five
fi

if ((! PLAN)); then
  log "[$(date '+%F %T')] All selected V5 steps finished; receipts: $RECEIPT_DIR"
fi
