#!/usr/bin/env bash
# OI-010 (D-3) sprint1 重跑驱动：efficiency-first 口径，唯一目的 = 产出**可信的
# strategy distribution**（每电路被接受候选的 kind ∈ {R,G,B,JOINT}）。
#
# 背景：§4.2 原表述"JOINT 对应 s27/s382/s420/s953、G 对应 s641/s713/s832、R 对应
# s820"在**两套已有运行中都不成立**（20260826 批次实测 G 23 次/7 电路、R 4 次/2 电
# 路、JOINT 0；sprint1 产物 eval_trials.json 为旧格式（多对象拼接、非严格 JSON），
# 无法直接统计）。OI-010 已裁定 (A)：§4.2 该段所有量必须来自同一 efficiency-first /
# sprint1 实验族 ⇒ 重跑，不从其他族借值。
#
# 口径（对齐归档 sprint1 `outerloop_result.json` 的实测字段）：
#   iterations=1, strategies=[R,G,B], joint_enumerate_depth=3, init_weights 全 1.0
#   ⇒ --max-iterations 1 --early-stop --joint-enumerate-depth 3（默认 R,G,B / k=8）
# 反馈：papers tab:configs 记"效率优先 = F1--F6 失效反馈仅轮内" ⇒ **不加 --no-feedback**
#       （单轮 ⇒ 轮内反馈生效、无跨轮累积）。
#
# 用法：
#   bash code/scripts/run_sprint1_batch.sh [circuits]      # 默认全部 8 个 ISCAS89
# 环境变量：
#   FAECO_OUT_ROOT   产物根（默认 <ROOT>/experiments/20260928_sprint1)
#   FAECO_K          候选束宽（默认 8）
#   FAECO_EXTRA      追加到 COMMON 的额外参数（探针用）
#   FAECO_DRY_RUN    置 1 只打印解析结果
#   FAECO_PARALLEL   并行电路数（默认 4）
#
# 断点续跑：已存在 outerloop_result.json 的电路跳过（幂等）。
set -u
export PATH="/usr/bin:/bin:$PATH"

ROOT="$(cd "$(dirname "$0")/../.." && { pwd -W 2>/dev/null || pwd; })"
OUT_ROOT="${FAECO_OUT_ROOT:-$ROOT/experiments/20260928_sprint1}"
ISCAS="$ROOT/data/raw/benchmarks/raw/iscas89"
PY="$ROOT/.venv/Scripts/python.exe"
RUNNER="code/scripts/run_outerloop_real_wns.py"

# ---- 工具链钉版本（同 run_s_ablation_batch.sh）---------------------------
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

ALL8="s27 s382 s420 s641 s713 s820 s832 s953"
if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
  CIRCUITS="$(echo "$1" | tr ',' ' ')"
else
  CIRCUITS="$ALL8"
fi

K="${FAECO_K:-8}"
PARALLEL="${FAECO_PARALLEL:-4}"
COMMON=(--period 0.5 --max-iterations 1 --candidates-per-iteration "$K"
        --joint-enumerate-depth 3 --early-stop --iscas89-dir "$ISCAS")
# shellcheck disable=SC2206
[ -n "${FAECO_EXTRA:-}" ] && COMMON+=(${FAECO_EXTRA})

[ -x "$PY" ] || { echo "venv python not found: $PY" >&2; exit 2; }
[ -f "$ROOT/$RUNNER" ] || { echo "runner not found: $ROOT/$RUNNER" >&2; exit 2; }

if [ -n "${FAECO_DRY_RUN:-}" ]; then
  echo "ROOT=$ROOT"; echo "OUT_ROOT=$OUT_ROOT"; echo "CIRCUITS=$CIRCUITS"
  echo "YOSYS=$YOSYS_VERSION"; echo "COMMON=${COMMON[*]}"
  exit 0
fi

mkdir -p "$OUT_ROOT/logs"

run_one() {
  local c="$1"
  if [ -f "$OUT_ROOT/$c/outerloop_result.json" ]; then
    echo "$c SKIP (result exists)"; return 0
  fi
  ( cd "$ROOT" \
    && PYTHONPATH="$ROOT/code/src" "$PY" "$RUNNER" \
        --circuit "$c" "${COMMON[@]}" \
        --output-dir "$OUT_ROOT" \
        > "$OUT_ROOT/logs/${c}.log" 2>&1 )
  local rc=$?
  echo "$c exit=$rc"
  return $rc
}

echo "circuits=$CIRCUITS out=$OUT_ROOT yosys=$YOSYS_VERSION parallel=$PARALLEL"

rc_all=0
running=0
for c in $CIRCUITS; do
  run_one "$c" & running=$((running + 1))
  if [ "$running" -ge "$PARALLEL" ]; then
    wait -n 2>/dev/null || rc_all=1
    running=$((running - 1))
  fi
done
wait || rc_all=1

if [ "$rc_all" -ne 0 ]; then
  echo "SOME_RUNS_FAILED — see $OUT_ROOT/logs/*.log" >&2
else
  echo "ALL_RUNS_DONE"
fi
exit "$rc_all"
