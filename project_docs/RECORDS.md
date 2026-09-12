# 记录体系总览

> 所有该记录的活动都有对应记录文档。**每次执行任务，默认要求更新相关记录文档**（非可选）。
> 任务完成而未记录，视为任务未完成。

## 记录点一览

| 触发时机 | 记录文档 | 记录内容 |
|----------|----------|----------|
| 每个关键动作 | `project_docs/LOGS.md` | 总日志 |
| 每轮结束 | `WORK_PROGRESS.md` `CURRENT_STATUS.md` `TASK_BOARD.md` `CURRENT_RUN_HANDOFF.md` `NEXT_AGENT_PROMPT.md` | 进度 / 状态 / 任务 / 交接 |
| 发现问题 | `project_docs/OPEN_ISSUES.md` | 未决问题 |
| 解决问题 | `docs/EXPERIENCE.md` | 经验（现象→原因→解决→验证） |
| 每次实验 | `project_docs/evidence/EXPERIMENT_REGISTRY.md` | 实验登记（防重复做） |
| 每次改论文 | `paper/zh/CHANGE_LOG.md` | 论文修改（内容 / 数字 / 术语） |
| 每次改图 | `paper/zh/figures/CHANGE_LOG.md` | 图片修改（数据 / 样式 / 尺寸） |
| 审稿轮次 | `paper/zh/review_rounds/r<N>/` | 意见 + 回复 + 修改前论文 |
| 结构 / 路径变更 | `README.md` `AGENTS.md` `.codex-handoff.json` `project_docs/README.md` | 目录角色 / 规则同步 |
| 版本相关 | `project_docs/versioning.md` `baselines/` | 版本 / 基线 |
| 术语变更 | `docs/GLOSSARY.md` `paper/GLOSSARY.md` | 术语 / 译名 |
| 数据 / 结论变更 | `project_docs/evidence/`（交叉表、索引） | 证据映射 |
| 每周日 | `reports/weekly/` | 周报 |
| 自检 | `bash code/scripts/check_record.sh` | 今日已记录 |

## 默认要求

1. **每次执行任务，默认更新相关记录文档**——任务完成即记录，不事后补。
2. 多智能体协作时：专职记录智能体负责实时记录（见 `AGENTS.md`）。
3. 未记录视为任务未完成；交接前逐项核对（`agent_handoff/checklists/HANDOFF_PUSH_TEMPLATE.md`）。
4. 记录使用**实时性**：边做边记，防止遗忘 / 失真 / 丢细节。
