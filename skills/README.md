# 项目级技能

## 科研技能包（nature-skills，Apache-2.0）

面向科研全流程的 19 个技能，来源：https://github.com/Yuan1z0825/nature-skills

| 技能 | 用途 |
|------|------|
| `nature-academic-search/` | 学术检索 |
| `nature-citation/` | 引用生成/管理 |
| `nature-data/` | 科研数据处理 |
| `nature-downloader/` | 文献/资料下载 |
| `nature-experiment-log/` | 实验记录 |
| `nature-figure/` | 科研绘图 |
| `nature-literature-pipeline/` | 文献阅读管线 |
| `nature-paper-card/` | 论文速览卡片 |
| `nature-paper-to-patent/` | 论文转专利 |
| `nature-paper2ppt/` | 论文转 PPT |
| `nature-polishing/` | 论文润色 |
| `nature-proposal-writer/` | 项目申请书写作 |
| `nature-reader/` | 文献精读 |
| `nature-ref-verifier/` | 引用核查 |
| `nature-response/` | 审稿回复 |
| `nature-reviewer/` | 审稿人视角评审 |
| `nature-shared/` | 共享工具/资源 |
| `nature-statistics/` | 科研统计 |
| `nature-writing/` | 论文写作 |

## 学术论文（ARS 技能包）

| 技能 | 描述 |
|------|------|
| `deep-research/` | 13-agent 深度学术调研 |
| `academic-paper/` | 12-agent 论文写作 |
| `academic-paper-reviewer/` | 7-agent 同行评审模拟 |
| `academic-pipeline/` | 全流程编排：调研→写作→评审→定稿 |

> 来源：academic-research-skills（CC-BY-NC-4.0）。

## 项目本地补充

| 技能 | 描述 |
|------|------|
| `chinese-paper-style/` | **本项目**文档写作规范（论文 / 技术说明 / 报告 / 设计文档）：证据校验 / 术语统一 / 引用核查 / 格式自检。 |

## 发现路径

1. 先读本文件与对应技能说明（`README.md` 或 `SKILL.md`）。
2. 写论文时：`nature-writing` / `academic-paper` + `chinese-paper-style`；审稿时：`nature-response` / `academic-paper-reviewer`。
3. 若 `skills/` 不可用，回退 `project_docs/agent_handoff/skill_snapshots/`。

## 规则

- 技能变更时同步更新 `project_docs/agent_handoff/skill_snapshots/` 快照（项目本地 `chinese-paper-style` 必同步）。
- 外部技能（nature-*、ARS）保持与上游同步；项目本地规则写在 `chinese-paper-style`。
