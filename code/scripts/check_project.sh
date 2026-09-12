#!/usr/bin/env bash
# 项目健康检查 —— 输出"交接就绪度"。任何智能体 / 工具 / 人都可运行。
# 用法：bash code/scripts/check_project.sh
# 退出码：0 = 就绪；1 = 有待办（WARN）。
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY="$(date +%F)"
PASS=0; WARN=0

ok()   { echo "[PASS] $1"; PASS=$((PASS+1)); }
warn() { echo "[WARN] $1"; WARN=$((WARN+1)); }

echo "=== 项目健康检查 $TODAY ==="

# 1. 记录
WP="$ROOT/project_docs/WORK_PROGRESS.md"
CS="$ROOT/project_docs/agent_handoff/status_logs/CURRENT_STATUS.md"
if [ -f "$WP" ] && grep -q "$TODAY" "$WP" 2>/dev/null; then ok "今日记录已更新（WORK_PROGRESS.md）"; else warn "今日 ($TODAY) 未在 WORK_PROGRESS.md 记录"; fi
if [ -f "$CS" ] && grep -q "$TODAY" "$CS" 2>/dev/null; then ok "今日状态已更新（CURRENT_STATUS.md）"; else warn "今日 ($TODAY) 未在 CURRENT_STATUS.md 更新"; fi

# 2. 根目录卫生（主目录整洁）
tmp_files=$(find "$ROOT" -maxdepth 1 -name 'tmp_*' 2>/dev/null)
if [ -z "$tmp_files" ]; then ok "根目录无散落 tmp_* 文件"; else warn "根目录存在散落文件：$(echo "$tmp_files" | tr '\n' ' ')"; fi

# 3. git 状态
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -z "$(git -C "$ROOT" status --porcelain)" ]; then ok "git 工作区干净"; else warn "git 有 $(git -C "$ROOT" status --porcelain | wc -l) 项未提交改动"; fi
  if git -C "$ROOT" rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    ahead=$(git -C "$ROOT" rev-list --count "@{u}..HEAD" 2>/dev/null)
    if [ "$ahead" -eq 0 ]; then ok "git 与远端同步"; else warn "git 领先远端 $ahead 个提交（未推送）"; fi
  fi
else
  warn "不是 git 仓库"
fi

# 4. 占位 / TODO 残留（提示项，模板阶段属预期）
ph=$(grep -rEn --include='*.md' --include='*.tex' --include='*.json' --include='*.csv' \
  -E '\[占位\]|\[项目名\]|\[基线ID\]|\[主稿件\]|TODO|FIXME' "$ROOT" 2>/dev/null \
  | grep -vE '\.git/|/scratch/|check_project\.sh|check_record\.sh|versioning\.md|GLOSSARY|README\.md|AGENTS\.md' | wc -l)
echo "[INFO] 占位 / TODO 残留：$ph 处（模板阶段属预期，实际项目应清零）"

# 5. 未决问题（Open Issues）
OI="$ROOT/project_docs/OPEN_ISSUES.md"
if [ -f "$OI" ]; then
  open_count=$(grep -c '未解决' "$OI" 2>/dev/null || true)
  if [ "$open_count" -gt 0 ]; then
    warn "有 $open_count 个未决问题（见 project_docs/OPEN_ISSUES.md），必须告知用户"
  else
    ok "无未决问题"
  fi
else
  ok "无未决问题清单（模板阶段）"
fi

echo "=== 结果：PASS=$PASS WARN=$WARN ==="
[ "$WARN" -eq 0 ] || exit 1
exit 0
