# Handoff Push Checklist

> 每轮工作结束、准备交接前逐项核对。全部通过才视为「可交接」。

## 状态文档

- [ ] `WORK_PROGRESS.md` 顶部新增本轮条目
- [ ] `status_logs/CURRENT_STATUS.md` 更新本轮细节
- [ ] `TASK_BOARD.md` 活跃表更新状态与证据门
- [ ] `CURRENT_RUN_HANDOFF.md` 更新
- [ ] `NEXT_AGENT_PROMPT.md` 更新
- [ ] `OPEN_ISSUES.md` 未决问题已核对（未解决的全部列出）
- [ ] 运行 `bash code/scripts/check_record.sh`，确认今日已记录

## 证据

- [ ] 每条新结论都能定位到 `project_docs/evidence/` 或具名基线
- [ ] 关键数字与证据一致；估测 vs 实测明确区分
- [ ] 证据包自包含（README + 摘要 + 输入 + 原始输出 + hash）

## 卫生（防冗余）

- [ ] 根目录无 `tmp_*` 散落文件
- [ ] 临时脚本已放 `scratch/` 或已晋级到 `code/scripts/` / `code/tests/`
- [ ] 生成物已 git-ignored，未误提交
- [ ] 无重复文档；同一主题只在一处维护

## 提交

- [ ] 提交信息描述清楚；涉及数据/结论变更的 PR 附 Evidence 小节
