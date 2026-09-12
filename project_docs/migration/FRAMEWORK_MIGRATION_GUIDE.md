# 框架移植指南

> 目的：把**已有项目**移植进本框架。任何智能体 / 人按此步骤可完成迁移。
> 智能体可直接以本文档为执行依据。

## 0. 前提

- 框架模板：`[模板仓库]`（本框架，GitHub: Toylog123/Project-Structure-Template）
- 源项目：待移植的已有项目（代码、文档、数据等）

## 1. 复制框架

1. 整体复制模板 → 重命名为新项目（如 `<新项目目录>`）。
2. 填 `README.md` 占位：项目简介、整体设计。
3. 清理占位符：`[占位]`、`[项目名]`、`[基线ID]` 等（`check_project.sh` 会提示剩余）。

## 2. 归类已有内容（映射表）

| 已有项目的内容 | 放入框架哪里 |
|----------------|--------------|
| 源代码 | `code/src/`（按模块分子目录） |
| 脚本 / 工具 | `code/scripts/` |
| 测试 | `code/tests/` |
| 构建工程 / 配置 | `project/` |
| 实验 / 评估 | `experiments/`（含反驳性测试计划） |
| 论文 / 报告 | `paper/zh/`（或 en） |
| 数据 | `data/`（`manifests/` 登记来源，`raw/` `derived/` 入 git-ignored） |
| 技术文档 / 环境 | `docs/`（`environment.md`、`GLOSSARY.md`） |
| 历史版本 / 基线 | 冻结为 `versions/<基线ID>/` + `project_docs/baselines/` |
| 旧文档 / 归档 | `project_docs/archive/` |
| 结果 / 日志 | `project_docs/evidence/`（自包含证据包） |

## 3. 初始化

1. 环境：填 `docs/environment.md`（工具链版本、依赖、复现步骤）。
2. 术语：`paper/GLOSSARY.md` 登记论文用到的全部术语（中英对照）。
3. 立项：填 `project_docs/design_specs/PROJECT_PROPOSAL_TEMPLATE.md`（创新评估 + 自杀式测试）。
4. 基线：`project_docs/baselines/BASELINE_TEMPLATE.md` → 首个基线；`BASELINE_INDEX.csv` 登记。
5. 版本：当前开发在 `code/`，首个冻结版本入 `versions/v1/`。
6. 记录：`WORK_PROGRESS.md`、`LOGS.md`、`OPEN_ISSUES.md`（把源项目**未解决的问题**登记进来）。
7. 经验：`docs/EXPERIENCE.md`（移植中踩的坑 + 源项目已知坑）。
8. 技能：按需更新 `skills/`。

## 4. 验证

- `bash code/scripts/check_project.sh`：WARN 逐项说明。
- 跑通一个最小复现（环境验证），记录"环境就绪"。
- `git commit` + `git push`。

## 5. 注意事项

- 保留源项目 git 历史（可选）：先 copy 保留，或在新仓库重写历史。
- **移植不改变代码行为**：只重组织目录，不重构逻辑（重构单独做）。
- 源项目的密钥 / 敏感信息**不迁入**（见 `SECURITY.md`）。
- 移植完成后，源项目按需归档。
