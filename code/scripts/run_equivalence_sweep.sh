#!/usr/bin/env bash
# 多电路 × 多配置的「行为等价」复跑驱动（E1-E6 gate）。
#
# 用途：把 codex 谱系实现（worktree，参考侧）与当前 main 布局（候选侧）
#       在完全相同的命令行下跑同一批电路，产物交给
#       code/scripts/compare_equivalence_sweep.py 判定。
#
# 用法：
#   bash code/scripts/run_equivalence_sweep.sh <config> <side> [circuits]
#
#     config    artifact | gateA | ctrl
#               artifact : 论文主实验产物反推出的开关（k=1 + --tns-aware）
#               gateA    : 0a gate 用的配置（默认 k=8；显式 --early-stop）
#               ctrl     : gateA 去掉 --early-stop —— 敏感性正控制，不是 gate
#     side      main | codex | both
#     circuits  逗号分隔（默认全部 8 个 ISCAS89 电路）
#
# 环境变量：
#   FAECO_WORKTREE  codex 谱系 worktree（默认 <ROOT>/scratch/codex_wt）
#   FAECO_OUT_ROOT  产物根目录（默认 <ROOT>/experiments/20260923_legacy_reg）
#
# 退出码：0 = 全部 run 成功（注意这只是"跑完了"，判定由 sweep 工具给出）。
#
# ─────────────────────────────────────────────────────────────────────────────
# 两个必须显式规避的陷阱（否则对照静默失效，见 reports/FAECO_LEGACY_REGRESSION_20260923.md §4）
#
# 1) 入口脚本相对路径两侧不同：main 是 code/scripts/...，codex worktree 是
#    scripts/...（迁移前布局）。用同一个相对路径会让一侧秒退（exit=2）。
# 2) .venv 的 editable .pth 硬编码 rseco -> <main>/code/src，无论 cwd 如何
#    `import rseco` 都解析到主仓库。两侧必须显式 PYTHONPATH=<该侧根>/src，
#    否则 codex 侧静默加载 main 的代码，"全等"变成同义反复。
# ─────────────────────────────────────────────────────────────────────────────
set -u
export PATH="/usr/bin:/bin:$PATH"

# Git Bash 的 ``pwd`` 返回 POSIX 形式（/d/...），把它交给 Windows 版 Python 会被
# 解释成 ``\d\...`` 而找不到源文件。必须取 Windows 形式（``pwd -W``；非 Git Bash 环境
# 没有 -W，回退到普通 pwd，因为那种环境下本来就是原生路径）。
ROOT="$(cd "$(dirname "$0")/../.." && { pwd -W 2>/dev/null || pwd; })"
WORKTREE="${FAECO_WORKTREE:-$ROOT/scratch/codex_wt}"
OUT_ROOT="${FAECO_OUT_ROOT:-$ROOT/experiments/20260923_legacy_reg}"
ISCAS="$ROOT/data/raw/benchmarks/raw/iscas89"
PY="$ROOT/.venv/Scripts/python.exe"

ALL8="s27 s382 s420 s641 s713 s820 s832 s953"

CONFIG="${1:?usage: run_equivalence_sweep.sh <artifact|k1tns|gateA|ctrl> <main|codex|both> [circuits]}"
case "$CONFIG" in
  # The archived 20260826 ISCAS89 batch: pinned by the s382 probe 2026-09-23.
  # WITHOUT --tns-aware -- adding it flips s382 round 1 to a WNS-neutral /
  # TNS-improving accept and drops the artifact match to 11/24.
  artifact) DIR="configA_artifact"
            COMMON=(--period 0.5 --max-iterations 8 --workers 1 --early-stop
                    --candidates-per-iteration 1) ;;
  # k=1 *with* --tns-aware: the switch belongs to the ITC-99 batch.
  k1tns)    DIR="configA2_k1tns"
            COMMON=(--period 0.5 --max-iterations 8 --workers 1 --early-stop
                    --candidates-per-iteration 1 --tns-aware) ;;
  gateA)    DIR="configB_gateA"
            COMMON=(--period 0.5 --max-iterations 8 --workers 1 --early-stop) ;;
  ctrl)     DIR="configC_ctrl"
            COMMON=(--period 0.5 --max-iterations 8 --workers 1) ;;
  *)        echo "unknown config: $CONFIG (use artifact|k1tns|gateA|ctrl)" >&2; exit 2 ;;
esac
COMMON+=(--iscas89-dir "$ISCAS")

SIDES="${2:-both}"
case "$SIDES" in
  main|codex) LIST="$SIDES" ;;
  both)       LIST="main codex" ;;
  *)          echo "unknown side: $SIDES (use main|codex|both)" >&2; exit 2 ;;
esac

if [ $# -ge 3 ] && [ -n "${3:-}" ]; then
  CIRCUITS="$(echo "$3" | tr ',' ' ')"
else
  CIRCUITS="$ALL8"
fi

EXP="$OUT_ROOT/$DIR"
[ -x "$PY" ] || { echo "venv python not found: $PY" >&2; exit 2; }
[ -d "$WORKTREE" ] || { echo "codex worktree not found: $WORKTREE" >&2; exit 2; }

# 干跑：只打印解析结果，不启动任何 run、不建任何目录。用于单测与人工核对路径形态
# （尤其确认 ROOT/ISCAS 是 Windows 形式，而不是 /d/... 的 POSIX 形式）。
if [ -n "${FAECO_DRY_RUN:-}" ]; then
  echo "ROOT=$ROOT"
  echo "WORKTREE=$WORKTREE"
  echo "ISCAS=$ISCAS"
  echo "EXP=$EXP"
  echo "SIDES=$LIST"
  echo "CIRCUITS=$CIRCUITS"
  echo "COMMON=${COMMON[*]}"
  exit 0
fi

mkdir -p "$EXP/main" "$EXP/codex" "$EXP/logs"

# 子 shell 是本 shell 的 fork，普通变量与数组都会被继承（不要改成 bash -c）。
run_side() {
  local side="$1" c="$2" root rel
  if [ "$side" = "main" ]; then
    root="$ROOT"; rel="code/scripts/run_outerloop_real_wns.py"
  else
    root="$WORKTREE"; rel="scripts/run_outerloop_real_wns.py"
  fi
  cd "$root" || return 1
  PYTHONPATH="$root/src" "$PY" "$rel" \
      --circuit "$c" "${COMMON[@]}" \
      --output-dir "$EXP/$side" \
      > "$EXP/logs/${side}_${c}.log" 2>&1
  local rc=$?
  echo "[$CONFIG/$side] $c exit=$rc"
  return $rc
}

echo "config=$CONFIG dir=$DIR sides=$LIST circuits=$CIRCUITS"
echo "worktree=$WORKTREE"

rc_all=0
pids=()
for side in $LIST; do
  ( for c in $CIRCUITS; do run_side "$side" "$c" || exit 1; done ) &
  pids+=($!)
done
for pid in "${pids[@]}"; do wait "$pid" || rc_all=1; done

if [ "$rc_all" -ne 0 ]; then
  echo "SOME_RUNS_FAILED ($CONFIG/$LIST) — see $EXP/logs/*.log" >&2
else
  echo "ALL_RUNS_DONE ($CONFIG/$LIST)"
fi
exit "$rc_all"
