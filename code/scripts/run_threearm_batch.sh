#!/usr/bin/env bash
# r2 §6 三臂对照实验驱动：Mixed-Fixed / Mixed-Random{seed1,2,3} / FAECO-Adaptive。
#
# 设计出处：project_docs/planning/FAECO_V2_TECH_DESIGN_20260923.md §6.1。
# 统一口径（三臂完全一致，只有臂开关不同）：
#   --period 0.5 --max-iterations 20（对应设计的 --rounds 20）
#   --candidates-per-iteration 8（割候选排序臂间可比；k=1 时随机排序退化为恒等）
#   --joint-k 2 --enable-buffer（R/G/B/J 混合候选空间；设计写的
#     `--strategies R,G,B,J` 在实现上等价于 --strategies R,G,B(默认) + --joint-k>0，
#     因为 JOINT 候选在 patch 层构建、不受 strategy_filter 过滤）
#   --workers 1 --early-stop --sta-budget 500（候选级 STA 预算上限一致）
# 臂开关（唯一自由度）：
#   fixed      --no-feedback
#   random_sN  --no-feedback --random-order --seed N
#   adaptive   --feedback-ema   （EMA 反馈；UCB 决策层 --adaptive 保持关闭以隔离变量）
#
# 用法：
#   bash code/scripts/run_threearm_batch.sh [arms] [circuits]
#     arms     逗号分隔，子集于 fixed,random_s1,random_s2,random_s3,adaptive（默认全部）
#     circuits 逗号分隔（默认全部 8 个 ISCAS89 电路）
#
# 环境变量：
#   FAECO_OUT_ROOT  产物根目录（默认 <ROOT>/experiments/20260924_threearm）
#   FAECO_K         候选束宽（默认 8；k=1 是 r2 §6 的反馈隔离口径——权重决定
#                   唯一候选的身份而非次序，用于 L2 的 k=1 判别实验）
#   FAECO_DRY_RUN   置 1 只打印解析结果，不执行任何 run（单测/核对用）
#
# 断点续跑：某电路已存在 outerloop_result.json 则跳过（幂等）。
#
# 退出码：0 = 全部 run 成功（判定由 compare_threearm.py 给出，这里只负责跑）。
set -u
export PATH="/usr/bin:/bin:$PATH"

# Git Bash 的 pwd 是 POSIX 形式，交给 Windows Python 会变成 \d\... —— 必须 pwd -W。
ROOT="$(cd "$(dirname "$0")/../.." && { pwd -W 2>/dev/null || pwd; })"
OUT_ROOT="${FAECO_OUT_ROOT:-$ROOT/experiments/20260924_threearm}"
ISCAS="$ROOT/data/raw/benchmarks/raw/iscas89"
PY="$ROOT/.venv/Scripts/python.exe"
RUNNER="code/scripts/run_outerloop_real_wns.py"

ALL_ARMS="fixed random_s1 random_s2 random_s3 adaptive"
ALL8="s27 s382 s420 s641 s713 s820 s832 s953"

if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
  ARMS="$(echo "$1" | tr ',' ' ')"
else
  ARMS="$ALL_ARMS"
fi
if [ $# -ge 2 ] && [ -n "${2:-}" ]; then
  CIRCUITS="$(echo "$2" | tr ',' ' ')"
else
  CIRCUITS="$ALL8"
fi

K="${FAECO_K:-8}"
COMMON=(--period 0.5 --max-iterations 20 --candidates-per-iteration "$K"
        --joint-k 2 --enable-buffer --workers 1 --early-stop
        --sta-budget 500 --iscas89-dir "$ISCAS")

arm_flags() {
  # 每臂的唯一自由度；未知臂在这里 fail closed。
  case "$1" in
    fixed)     echo "--no-feedback" ;;
    random_s1) echo "--no-feedback --random-order --seed 1" ;;
    random_s2) echo "--no-feedback --random-order --seed 2" ;;
    random_s3) echo "--no-feedback --random-order --seed 3" ;;
    adaptive)  echo "--feedback-ema" ;;
    *)         echo "" ; return 1 ;;
  esac
}

for a in $ARMS; do arm_flags "$a" >/dev/null || { echo "unknown arm: $a" >&2; exit 2; }; done
[ -x "$PY" ] || { echo "venv python not found: $PY" >&2; exit 2; }
[ -f "$ROOT/$RUNNER" ] || { echo "runner not found: $ROOT/$RUNNER" >&2; exit 2; }

if [ -n "${FAECO_DRY_RUN:-}" ]; then
  echo "ROOT=$ROOT"
  echo "OUT_ROOT=$OUT_ROOT"
  echo "ISCAS=$ISCAS"
  echo "ARMS=$ARMS"
  echo "CIRCUITS=$CIRCUITS"
  echo "K=$K"
  echo "COMMON=${COMMON[*]}"
  for a in $ARMS; do echo "ARM_FLAGS[$a]=$(arm_flags "$a")"; done
  exit 0
fi

mkdir -p "$OUT_ROOT/logs"

run_one() {
  local arm="$1" c="$2" flags
  local out="$OUT_ROOT/$arm"
  flags="$(arm_flags "$arm")"
  if [ -f "$out/$c/outerloop_result.json" ]; then
    echo "[$arm] $c SKIP (result exists)"
    return 0
  fi
  # PYTHONPATH 必须显式指向 <repo>/code/src：.venv 的 editable .pth 也钉在
  # 同一处，这里显式化以免环境漂移（同 run_equivalence_sweep.sh 的陷阱 2）。
  ( cd "$ROOT" \
    && PYTHONPATH="$ROOT/code/src" "$PY" "$RUNNER" \
        --circuit "$c" ${flags} "${COMMON[@]}" \
        --output-dir "$out" \
        > "$OUT_ROOT/logs/${arm}_${c}.log" 2>&1 )
  local rc=$?
  echo "[$arm] $c exit=$rc"
  return $rc
}

echo "arms=$ARMS circuits=$CIRCUITS out=$OUT_ROOT"

# 臂间并行（互不共享目录），臂内电路串行（workers=1 语义干净，B(k) 次序无歧义）。
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
