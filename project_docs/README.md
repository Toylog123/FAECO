# 项目过程文档

本目录存放项目过程与治理文档，而非源码。

| 子目录 / 文件 | 角色 |
|---------------|------|
| `WORK_PROGRESS.md` | 工作进度（倒序，最新在上） |
| `LOGS.md` | 总工作日志（按时间正序追加，便于回溯查询） |
| `OPEN_ISSUES.md` | 未决问题追踪（未解决持续保留，必须告知用户） |
| `RECORDS.md` | 记录体系总览（所有记录点 + 默认强制更新要求） |
| `agent_handoff/` | 交接入口与状态（README → START_HERE → CURRENT_STATUS → TASK_BOARD → CURRENT_RUN_HANDOFF） |
| `reports/weekly/` | 周期性总结（周报） |
| `baselines/` | 具名基线：绑定论文、源码、测试与证据 |
| `versioning.md` | 版本管理策略（代码 / 测试多版本、基线绑定） |
| `ARCHIVE_POLICY.md` | 归档与版本迭代规范（各对象何时/如何归档） |
| `FILE_ORGANIZATION.md` | 文件分类与命名规范（按实验/版本/类型分，防混块） |
| `evidence/` | 不可变实验证据与结论交叉表（含 CROSSWALK_TEMPLATE 论文-证据交叉表模板） |
| `design_specs/` | 项目立项评估（创新性评估）与专项设计规范 |
| `review_history/` | 评审历史：论文审稿轮次（REVIEW_ROUND_TEMPLATE）+ 工程审查报告（代码/设计/实验，ENGINEERING_REVIEW_TEMPLATE） |
| `archive/` | 退役版本与迁移历史 |
| `migration/` | 迁移记录 |
| `worktrees/` | 临时工作树注册表 |

分工：技术文档（面向实现）见根 `docs/`；这里只放过程与治理内容。
