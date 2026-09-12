#!/usr/bin/env bash
# 带超时与监测的运行包装器——防止长任务（测试/实验/构建/仿真）卡死空等。
# 用法：bash code/scripts/run_with_timeout.sh <秒数> <命令...>
# 退出码：0 = 正常完成；124 = 超时终止；其他 = 命令本身退出码。
set -u
TIMEOUT="${1:?用法: run_with_timeout.sh <秒数> <命令...>}"
shift

echo "[run] 启动（超时 ${TIMEOUT}s）：$*"
start=$(date +%s)

"$@" &
PID=$!

while kill -0 "$PID" 2>/dev/null; do
  now=$(date +%s)
  elapsed=$((now - start))
  if [ "$elapsed" -ge "$TIMEOUT" ]; then
    echo "[run] ⚠ 超时（${elapsed}s），终止进程 PID=$PID"
    kill "$PID" 2>/dev/null
    sleep 2
    kill -9 "$PID" 2>/dev/null
    exit 124
  fi
  sleep 5
done

wait "$PID"
code=$?
echo "[run] 完成（$(( $(date +%s) - start ))s），退出码 $code"
exit "$code"
