# 协作规范（CONTRIBUTING）

> 适用：多人 / 多智能体 / AI 协作。所有变更按此流程。

## 分支策略

- `main`：唯一主干，始终可发布。
- 功能分支：`feature/<任务ID>-<简述>`；改动前从最新 `main` 拉出。

## 提交规范

- 提交信息格式：`<类型>: <描述>`
- 类型：`feat`（新功能）/ `fix`（修复）/ `docs`（文档）/ `refactor`（重构）/ `chore`（杂项）/ `test`（测试）
- 一个提交只做一件事；结构变更必须连带文档更新（见 `AGENTS.md` 文档同步）。

## PR / 合并流程

1. 提交前运行 `bash code/scripts/check_project.sh`（或 `make check`），WARN 需说明。
2. 涉及数据 / 结论变更的 PR，必须附 Evidence 小节（`.github/PULL_REQUEST_TEMPLATE.md`）。
3. 评审：至少一个独立评审（人或智能体）过证据门。
4. 合并到 `main` 前，分支须与 `main` 同步且检查通过。

## 任务分配（多智能体）

- 任务在 `project_docs/agent_handoff/TASK_BOARD.md` 认领，注明归属。
- 可分解的独立子任务默认**并行**（多智能体并发），每个子任务有明确产出与负责人。
- 并行结果汇合后统一审查，再合并。

## 记录要求

- 每轮结束更新 `WORK_PROGRESS.md`、`CURRENT_STATUS.md`、`LOGS.md`；未决问题入 `OPEN_ISSUES.md` 并告知用户。
