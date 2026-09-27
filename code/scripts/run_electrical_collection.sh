#!/usr/bin/env bash
# 电气风险前置 E —— 阶段 3-A 采集驱动
# (project_docs/planning/FAECO_V2_DESIGN_PLAN_20260923.md §3)
#
# 四臂 = 两个 regime × {对照, 采集}。每对臂内唯一自由度是 `--capture-electrical`，
# 因此同一 regime 下对照/采集的 WNS 轨迹与接受链必须逐位相同 —— 这是"采集绝不改变
# 算法行为"的证据，由 code/scripts/analyze_electrical_correlation.py 的 Gate 0 判定。
#
#   phys  --no-feedback --physical-gate                     (对照，物理 regime)
#   elec  --no-feedback --physical-gate --capture-electrical (采集，物理 regime)
#   base  --no-feedback                                      (对照，理想 regime)
#   cap   --no-feedback --capture-electrical                 (采集，理想 regime)
#
# 为什么需要两个 regime：3-A 的问题是"电气量能否预测**增益未兑现**"。物理 regime
# 才发射 `F6_physical_load_failure`，但在论文既有物理门参数下（unit_len=40、penalty=1、
# min_gain=0.01）该标签近乎退化（s27 探针 32/34 为 F6），单标签无判别力；理想 regime
# 提供 `no_ideal_gain` / `hard_fail` 两个有方差的标签。判据要求**同一特征在多标签上
# 同时成立**，故两个 regime 都要采集。
#
# 统一口径：
#   --period 0.5 --max-iterations 20 --candidates-per-iteration $K
#   --joint-k 2 --enable-buffer --workers 1 --early-stop --no-feedback
#   --sta-budget $STA_BUDGET
# 预算取 1600：物理 regime 每候选约消耗 2–3 个 `sta` 记账（理想 STA + 物理候选 STA
# + 每次接受后重建的物理基线 STA），理想 regime 每候选 1 个。两语 regime 同值、
# 且**都不得撞墙**；报告里给出全部臂的 sta_used 以证明预算不绑定。
#
# 用法：
#   bash code/scripts/run_electrical_collection.sh [arms] [circuits]
#     arms     逗号分隔，子集于 phys,elec,base,cap（默认全部四臂）
#     circuits 逗号分隔（默认全部 8 个 ISCAS89 电路）
#
# 环境变量：
#   FAECO_OUT_ROOT  产物根（默认 <ROOT>/experiments/20260926_electrical_3a）
#   FAECO_K         候选束宽（默认 8，与 L2 三臂 / L3 消融一致）
#   FAECO_STA_BUDGET 候选级 STA 预算（默认 1600，四臂同值）
#   FAECO_OSS_CAD   OSS-CAD Suite 根（默认 C:\oss-cad-suite-build\oss-cad-suite）
#   FAECO_DRY_RUN   置 1 只打印解析结果，不执行任何 run
#
# 断点续跑：某电路已存在 outerloop_result.json 则跳过（幂等）。
set -u
export PATH="/usr/bin:/bin:$PATH"

ROOT="$(cd "$(dirname "$0")/../.." && { pwd -W 2>/dev/null || pwd; })"
OUT_ROOT="${FAECO_OUT_ROOT:-$ROOT/experiments/20260926_electrical_3a}"
ISCAS="$ROOT/data/raw/benchmarks/raw/iscas89"
PY="$ROOT/.venv/Scripts/python.exe"
RUNNER="code/scripts/run_outerloop_real_wns.py"

# ---- 工具链钉版本（版本不对会静默改变映射结果）--------------------------
OSS_CAD="${FAECO_OSS_CAD:-/c/oss-cad-suite-build/oss-cad-suite}"
if [ ! -x "$OSS_CAD/bin/yosys.exe" ]; then
  echo "OSS-CAD Suite not found at $OSS_CAD (set FAECO_OSS_CAD)" >&2
  exit 2
fi
export YOSYSHQ_ROOT="$OSS_CAD"
export PATH="$OSS_CAD/bin:$OSS_CAD/lib:$PATH"
YOSYS_VERSION="$(yosys -V 2>&1 | head -1)"
case "$YOSYS_VERSION" in
  "Yosys 0.67"*) ;;
  *) echo "unexpected Yosys: $YOSYS_VERSION (需要 OSS-CAD 0.67+146)" >&2; exit 2 ;;
esac

ALL_ARMS="phys elec base cap"
ALL8="s27 s382 s420 s641 s713 s820 s832 s953"

if [ $# -ge 1 ] && [ -n "${1:-}" ]; then ARMS="$(echo "$1" | tr ',' ' ')"; else ARMS="$ALL_ARMS"; fi
if [ $# -ge 2 ] && [ -n "${2:-}" ]; then CIRCUITS="$(echo "$2" | tr ',' ' ')"; else CIRCUITS="$ALL8"; fi

K="${FAECO_K:-8}"
STA_BUDGET="${FAECO_STA_BUDGET:-1600}"
COMMON=(--period 0.5 --max-iterations 20 --candidates-per-iteration "$K"
        --joint-k 2 --enable-buffer --workers 1 --early-stop --no-feedback
        --sta-budget "$STA_BUDGET" --iscas89-dir "$ISCAS")

arm_flags() {
  # 每臂的唯一自由度；未知臂在这里 fail closed（绝不静默退化成"对照"）。
  case "$1" in
    phys) echo "--physical-gate" ;;
    elec) echo "--physical-gate --capture-electrical" ;;
    base) echo "" ;;
    cap)  echo "--capture-electrical" ;;
    *)    echo "" ; return 1 ;;
  esac
}

for a in $ARMS; do arm_flags "$a" >/dev/null || { echo "unknown arm: $a" >&2; exit 2; }; done
[ -x "$PY" ] || { echo "venv python not found: $PY" >&2; exit 2; }
[ -f "$ROOT/$RUNNER" ] || { echo "runner not found: $ROOT/$RUNNER" >&2; exit 2; }

if [ -n "${FAECO_DRY_RUN:-}" ]; then
  echo "ROOT=$ROOT"; echo "OUT_ROOT=$OUT_ROOT"; echo "ISCAS=$ISCAS"
  echo "ARMS=$ARMS"; echo "CIRCUITS=$CIRCUITS"; echo "K=$K"
  echo "STA_BUDGET=$STA_BUDGET"; echo "YOSYS=$YOSYS_VERSION"
  echo "COMMON=${COMMON[*]}"
  for a in $ARMS; do echo "ARM_FLAGS[$a]=$(arm_flags "$a")"; done
  exit 0
fi

mkdir -p "$OUT_ROOT/logs"

run_one() {
  local arm="$1" c="$2" flags out
  out="$OUT_ROOT/$arm"
  flags="$(arm_flags "$arm")"
  if [ -f "$out/$c/outerloop_result.json" ]; then
    echo "[$arm] $c SKIP (result exists)"
    return 0
  fi
  ( cd "$ROOT" \
    && PYTHONPATH="$ROOT/code/src" "$PY" "$RUNNER" \
        --circuit "$c" ${flags} "${COMMON[@]}" \
        --output-dir "$out" \
        > "$OUT_ROOT/logs/${arm}_${c}.log" 2>&1 )
  local rc=$?
  echo "[$arm] $c exit=$rc"
  return $rc
}

echo "arms=$ARMS circuits=$CIRCUITS out=$OUT_ROOT yosys=$YOSYS_VERSION sta_budget=$STA_BUDGET"

# 臂间并行（互不共享目录），臂内电路串行（B(k) 次序无歧义）。
rc_all=0
pids=()
for a in $ARMS; do
  ( for c in $CIRCUITS; do run_one "$a" "$c" || exit 1; done ) &
  pids+=($!)
done
for pid in "${pids[@]}"; do wait "$pid" || rc_all=1; done

if [ "$rc_all" -ne 0 ]; then
  echo "SOME_RUNS_FAILED — see $OUT_ROOT/logs/*.log" >&2
else
  echo "ALL_RUNS_DONE"
fi
exit "$rc_all"
