# N08 Push to Remote 设计文档

更新时间：2026-07-31

本文档是 N31-04 / N08 的设计文档，对应 P2 项 "Git remote 未配置"。`paper/reviews/round1_self_audit.md` 列此项为 round2 之前需用户决定的事项。本文档不实施推送，仅给出 remote URL 决策树、push 前 final 验收清单、用户决定需求。

## 1. 当前仓库状态

```
$ git log --oneline | head -5
ae16371 docs: append LOG-20260731-20..22 to work log
6b8f84a docs(paper): sync draft README and add supplementary placeholder
bf16d30 docs: add N31-06 Z3 candidate/boundary formal design
027ddf5 docs: mark PM29-a and PM30 done in task board
66b9ef6 docs(paper): add round1 revision notes

$ git remote -v
(empty)

$ git config --local user.name
Toylolog

$ git config --local user.email
Toylolog@local
```

**当前状态**：本地 commit `ae16371` 已就位，46 个 commits；Git identity 是 local-only（`Toylolog@local`），不指向真实邮箱；remote 未配置。

## 2. Push 前必须关闭的事项

### 2.1 P0-1: Stage B CEC unavailable (R31-01)

`paper/reviews/round1_revision_notes.md` P0-1。处理路径：
- **决策 A**：用户授权 N31-03 ORFS techmap library 下载，修复 CEC，push 之前带 CEC pass 状态。
- **决策 B**：保留 CEC unavailable limitation，论文标注 limitation 后 push；这是当前最低风险路径。

### 2.2 P2-3: Git remote URL

用户必须提供：
- **方案 1**：GitHub private repository `Toylog/FAECO-Research`（推荐：私有 + 邀请合作者）
- **方案 2**：GitLab / Gitee / 自建 Gitea
- **方案 3**：保留本地仓库，push 决策延后

### 2.3 P2-5: paper/draft/ 章节审定

6 个章节（introduction / related_work / method_symbol_table / method / experiments / conclusion）均为 Draft 1，用户审定后才能迁入 `paper/submission/`。

push 时 `paper/` 目录状态：
- `paper/draft/` 6 章节 + README（已 commit）
- `paper/submission/` 仅 README 占位（待章节迁入）
- `paper/figures/` `paper/tables/` `paper/reviews/` README 占位

### 2.4 Git identity

当前是 `Toylolog <Toylolog@local>`（local-only）。push 前必须替换为真实身份：
- `--local` 配置仅在本地仓库生效
- push 之前需要 `git config --global user.name "..."` + `user.email "..."`
- 或者 push 时用 `GIT_AUTHOR_NAME=... GIT_AUTHOR_EMAIL=...` env vars

## 3. Push 命令模板

```bash
# 1. 配置 remote
git remote add origin https://github.com/<user>/<repo>.git

# 2. 验证身份
git config user.name "Toylog"
git config user.email "Toylog@users.noreply.github.com"

# 3. 最后一次回归
PYTHONPATH=src ./.venv/Scripts/python.exe -m unittest discover -s tests
# 期望：90 项全绿

# 4. Push
git push -u origin main

# 5. 验证
git log --oneline | head -3
# 期望：出现 push 成功的 commit hash
```

## 4. Push 后验收

- [ ] GitHub Actions / CI（如配置）：90 项测试在云端跑通
- [ ] README.md 在仓库首页显示
- [ ] paper/draft/ 与 paper/submission/ 可浏览
- [ ] experiments/20260731_epfl_8case_stage_b/tables/ 可下载
- [ ] benchmarks/source_manifests/ 可读（提醒：Liberty 等二进制大文件 **不**入库，按 handoff）

## 5. Push 后保留事项

- A-only 范围外（benchmarks/raw/, data/, paper/, experiments/2026*_*）仍 untracked —— 不应 push（按 handoff）
- 任何后续 commit 须遵守 A-only 范围 + secrets/PII 扫描 + 行尾策略
- push 后的 commit history 不可更改（除非 force-push，需协调）

## 6. 用户决定需求汇总

按优先级：

1. **决策 A 或 B（P0-1 CEC limitation）**：影响论文主表能否写 "CEC pass"
2. **remote URL（P2-3）**：决定 push 目标
3. **Git 真实身份（P2-5）**：决定 commit 作者标识
4. **章节审定（P2-5）**：决定是否 push draft 还是先迁入 submission
5. **CI 配置（可选）**：GitHub Actions 跑回归测试

## 7. 不做的事

- 不 force-push 已有的 commits
- 不上传任何 A-only 范围外的文件（Liberty / EPFL Verilog / 实验产物）
- 不修改已 commit 的 commit message（除非用户明确批准）
- 不删除本地 Git 历史（即使 push 失败也保留 `ae16371` 及之前所有 commits）
- 不向 GitHub 暴露 personal access token（使用 SSH 或 GitHub CLI 认证）

## 8. 后续修订

- 用户决定 CEC limitation 处置（决策 A 或 B）后，本文档第 2.1 节更新
- 用户提供 remote URL 后，本文档第 3 节 push 命令模板更新
- push 完成后，本文档迁入 `docs/engineering/n08_push_history.md`（记录 push 时间 + remote URL + commit hash）
- 任何 push 后的 CI 失败，按 round 2 修订说明处理

## 9. 当前状态总结

- 本地仓库 46 commits，HEAD `ae16371`，作者 `Toylolog <Toylolog@local>`
- A-only 范围 135 个核心文件入库
- A-only 范围外仍 untracked（按设计）
- remote 未配置（按当前授权范围）
- CEC limitation 当前为 P0 待解决（不影响 push，但决定论文主表能否写 "CEC pass"）

push 操作本身是**单向的不可逆操作**，必须等待用户明确指令才能执行。