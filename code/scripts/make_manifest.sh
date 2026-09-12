#!/usr/bin/env bash
# 基线 manifest 生成 —— 冻结基线前，生成源码 + 测试 + 证据的 SHA-256 清单。
# 用法：bash code/scripts/make_manifest.sh [-o <输出文件>] [路径...]
# 默认路径：src tests experiments paper/zh/manuscript project_docs/evidence
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT=""
PATHS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -o) OUT="${2:-}"; shift 2;;
    -h|--help) echo "用法：bash code/scripts/make_manifest.sh [-o 输出] [路径...]"; exit 0;;
    *) PATHS+=("$1"); shift;;
  esac
done
if [ ${#PATHS[@]} -eq 0 ]; then
  PATHS=("src" "tests" "experiments" "paper/zh/manuscript" "project_docs/evidence")
fi
if [ -z "$OUT" ]; then
  OUT="$ROOT/project_docs/baselines/BASELINE_MANIFEST_$(date +%Y%m%d).sha256"
fi
cd "$ROOT" || exit 1
: > "$OUT"
count=0
for p in "${PATHS[@]}"; do
  [ -d "$p" ] || { echo "[skip] 不存在：$p"; continue; }
  while IFS= read -r f; do
    sha256sum "$f" >> "$OUT"
    count=$((count+1))
  done < <(find "$p" -type f -not -name '.gitkeep' -not -path '*/build/*' | sort)
done
echo "manifest 已生成：$OUT"
echo "文件数：$count"
