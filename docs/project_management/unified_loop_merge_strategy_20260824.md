# Unified Loop 合并策略

日期：2026-08-24
目标分支：`codex/faeco-unified-loop`
实现修复：`79b8f05cf0274efca2895a588ada82f6e1234140`

## 主目录保护

主目录 `D:\BaiduSyncdisk\03_FAECO` 当前约有 8 个 modified、3 个 deleted、103 个 untracked 项。这些是历史论文、实验和本地资产，禁止在该目录直接执行 merge、rebase、清理或覆盖操作；本轮不改变其中任何文件。

## 建议流程（当前只记录策略）

1. 从 `origin/main` 新建一个干净的 integration worktree，并在该 worktree 中核对分支基线。
2. 在 integration worktree 执行 `git merge --no-ff origin/codex/faeco-unified-loop`，保留可审计的合并节点；不要把主目录脏改动复制进来。
3. 运行全量 Python 回归，并在 WSL 工具链可用时运行真实 SEC/async-clear 复核；记录 Yosys、ABC、OpenSTA 版本及 skip 原因。
4. 检查文档、代码、测试、论文 headline 的证据边界和 `git diff --check`，由用户审阅合并结果。
5. 用户明确批准后，才 push 合并后的 `main`；本轮未执行 merge，也未 push。

## 验收边界

当前分支已完成 Sol 复审（初审 2 Critical + 4 Important，复审 APPROVED），主代理回归为 `351 passed, 4 skipped, 1 subtests passed`，真实 WSL async-clear SEC 为 `1 passed`。这些结果支持“适合进入合并准备”，不等于 main 已合并，也不等于大型 outer-loop/P&R 已重跑。
