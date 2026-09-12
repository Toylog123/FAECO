#!/usr/bin/env bash
# 记录检查（通用）——任何智能体 / 工具 / 人都可运行。
# 用法：bash code/scripts/check_record.sh
# 作用：检查"今日"是否已更新交接记录。仅提示，不阻塞、不修改文件。
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY="$(date +%F)"
WP="$ROOT/project_docs/WORK_PROGRESS.md"
CS="$ROOT/project_docs/agent_handoff/status_logs/CURRENT_STATUS.md"

log=""
[ -f "$WP" ] && grep -q "$TODAY" "$WP" 2>/dev/null && log="WORK_PROGRESS.md"
[ -f "$CS" ] && grep -q "$TODAY" "$CS" 2>/dev/null && log="$log CURRENT_STATUS.md"

if [ -n "$log" ]; then
  echo "[记录] OK 今日已记录：$log"
else
  echo "[记录] WARN 今日 ($TODAY) 尚未记录。结束工作前请更新："
  echo "  - project_docs/WORK_PROGRESS.md"
  echo "  - project_docs/agent_handoff/status_logs/CURRENT_STATUS.md"
  echo "  - project_docs/agent_handoff/TASK_BOARD.md"
  echo "  - project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md"
fi
exit 0
