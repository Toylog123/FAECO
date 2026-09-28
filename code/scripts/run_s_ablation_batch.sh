#!/usr/bin/env bash
# L3 S 消融驱动（r2 §4.9）：同一口径下 {S 关, S 开} 两臂，唯一自由度是
# `--structure-resynth`。
#
# 设计出处：project_docs/planning/FAECO_V2_TECH_DESIGN_20260923.md §4.9；
# 契约 §8.12 的"下一步 ①②"。臂内电路串行、臂间并行（互不共享目录）。
#
# 统一口径（与 L2 三臂实验完全一致，臂间可比）：
#   --period 0.5 --max-iterations 20 --candidates-per-iteration $K
#   --joint-k 2 --enable-buffer --workers 1 --early-stop --sta-budget 500
# 臂开关（唯一自由度）：
#   off  --no-feedback
#   on   --no-feedback --structure-resynth
# 为什么基线取 fixed 而非 adaptive：L2 已封板"EMA 反馈在 k=8 regime 无独立贡献"
# （reports/FAECO_L2_THREEARM_20260924.md），用 fixed 作基线才能让 S 成为单变量。
#
# 用法：
#   bash code/scripts/run_s_ablation_batch.sh [arms] [circuits]
#     arms     逗号分隔，子集于 off,on（默认 off,on）
#     circuits 逗号分隔（默认全部 8 个 ISCAS89 电路）
#
# 环境变量：
#   FAECO_OUT_ROOT          产物根目录（默认 <ROOT>/experiments/20260924_l3s_ablation）
#   FAECO_K                 候选束宽（默认 8，与 L2 三臂一致）
#   FAECO_RESYNTH_PER_ITER  每轮交给 S 的割边界数（默认 1）
#   FAECO_RESYNTH_VARIANTS  S 变体链（默认 S0,S1,S2）
#   FAECO_OSS_CAD           OSS-CAD Suite 根（默认 C:\oss-cad-suite-build\oss-cad-suite）
#   FAECO_DRY_RUN           置 1 只打印解析结果，不执行任何 run
#
# 断点续跑：某电路已存在 outerloop_result.json 则跳过（幂等）。
# 退出码：0 = 全部 run 成功（判定由下游聚合脚本给出，这里只负责跑）。
set -u
export PATH="/usr/bin:/bin:$PATH"

# Git Bash 的 pwd 是 POSIX 形式，交给 Windows Python 会变成 \d\... —— 必须 pwd -W。
ROOT="$(cd "$(dirname "$0")/../.." && { pwd -W 2>/dev/null || pwd; })"
OUT_ROOT="${FAECO_OUT_ROOT:-$ROOT/experiments/20260924_l3s_ablation}"
ISCAS="$ROOT/data/raw/benchmarks/raw/iscas89"
PY="$ROOT/.venv/Scripts/python.exe"
RUNNER="code/scripts/run_outerloop_real_wns.py"

# ---- 工具链钉版本 ------------------------------------------------------
# S 走 ABC 变体 + techmap + CEC，与映射路径共用同一次 Yosys 解析。版本不对
# （WSL yosys 0.33 / 旧 Scoop yosys 0.9）会**静默**改变结果，所以这里显式
# 注入 OSS-CAD 并断言版本串，而不是依赖调用者的 PATH。
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

ALL_ARMS="off on"
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
RESYNTH_PER_ITER="${FAECO_RESYNTH_PER_ITER:-1}"
RESYNTH_VARIANTS="${FAECO_RESYNTH_VARIANTS:-S0,S1,S2}"
# Lever L1 (tech design §13.3): S's own window pool.  Unset ⇒ historical
# behaviour (S reuses the candidates_per_iteration-truncated list).  Set to e.g.
# 32 ⇒ S gets a dedicated _cone_candidates(k=pool) enumeration.  The census
# (2026-09-28) proved the enumeration returns exactly k+1 boundaries, so without
# this the pool is capped at candidates_per_iteration (8) and resynth_per_iteration
# cannot reach past it.
RESYNTH_WINDOW_POOL="${FAECO_RESYNTH_WINDOW_POOL:-}"
# 候选级 STA 预算：两臂必须相同，且**两臂都不得撞墙**，否则 "S on" 的早停会
# 把"预算被 R/G/B 抢光"伪装成"S 无贡献"。实测（L2 fixed 臂）off 侧最大
# sta_used = 476（s420）；S on 侧每轮最多追加 resynth_per_iteration×|variants|
# = 3 次测量，20 轮上限 +60 → 536。故取 700（>536）作为两臂统一预算，
# 并**在报告里同时给出两臂 sta_used 以证明预算不绑定**。
# （L2/论文主口径是 500；本实验的对照是臂内自比，故此处放宽是刻意的。）
STA_BUDGET="${FAECO_STA_BUDGET:-700}"
COMMON=(--period 0.5 --max-iterations 20 --candidates-per-iteration "$K"
        --joint-k 2 --enable-buffer --workers 1 --early-stop
        --sta-budget "$STA_BUDGET" --iscas89-dir "$ISCAS")

arm_flags() {
  # 每臂的唯一自由度；未知臂在这里 fail closed。
  case "$1" in
    off) echo "--no-feedback" ;;
    on)  echo "--no-feedback --structure-resynth --resynth-per-iteration $RESYNTH_PER_ITER --resynth-variants $RESYNTH_VARIANTS${RESYNTH_WINDOW_POOL:+ --resynth-window-pool $RESYNTH_WINDOW_POOL}" ;;
    *)   echo "" ; return 1 ;;
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
  echo "YOSYS=$YOSYS_VERSION"
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
  # 同一处，这里显式化以免环境漂移。
  ( cd "$ROOT" \
    && PYTHONPATH="$ROOT/code/src" "$PY" "$RUNNER" \
        --circuit "$c" ${flags} "${COMMON[@]}" \
        --output-dir "$out" \
        > "$OUT_ROOT/logs/${arm}_${c}.log" 2>&1 )
  local rc=$?
  echo "[$arm] $c exit=$rc"
  return $rc
}

echo "arms=$ARMS circuits=$CIRCUITS out=$OUT_ROOT yosys=$YOSYS_VERSION"

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
