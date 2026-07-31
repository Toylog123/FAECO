# 原始材料总索引

更新时间：2026-07-07

## 1. 原始材料保留策略

本项目原始材料不移动、不改名、不覆盖。所有归纳、摘要、用途映射和论文引用准备工作都放在 `docs/` 下作为派生文档。

原因：

1. 学长论文、PDF 和文献库是后续追溯依据。
2. 中文文件名和历史目录可能已经被外部同步或手工记录引用。
3. 后续论文写作需要能回到原件核对表格、公式和上下文。

## 2. 顶层原始材料

| 目录 | 文件数 | 项目角色 | 当前处理方式 |
|---|---:|---|---|
| `论文/` | 3 | 学长 RSECO 工作的核心遗产 | 保留原件，派生旧稿审计 |
| `课题构想/` | 3 | 早期课题方向和导师思路 | 保留原件，派生方向归纳 |
| `ECO相关文献/` | 49 | 相关工作和方法支撑 | 保留原件，派生 literature matrix |

## 3. `论文/`

| 文件 | 类型 | 用途 |
|---|---|---|
| `基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.docx` | Word 主稿 | 旧稿审计、claim-evidence matrix、论文结构继承 |
| `基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.pdf` | PDF 稳定版 | 公式、图表和排版核对 |
| `基于重综合的掩膜前时序ECO框架研究_英文.docx` | 中英稿/英文稿 | 英文投稿叙事和术语参考 |

## 4. `课题构想/`

| 文件 | 类型 | 用途 |
|---|---|---|
| `课题构想.md` | Markdown | 四个 ECO 方向总览，作为长期路线背景 |
| `课题二_功能时序协同ECO_详细文档.md` | Markdown | 功能-时序协同 ECO 详细设想，作为后续扩展方向 |
| `ECO技术研究-课题概述.docx` | Word | 导师/项目层面的方向判断和风险提示 |

## 5. `ECO相关文献/`

| 子目录 | 文件数 | 主要内容 | 与当前主线关系 |
|---|---:|---|---|
| `时序ECO优化/` | 7 | timing ECO、spare cells、technology remapping、symbolic rectification | 直接支撑 related work 和 baseline |
| `功能ECO与逻辑修复/` | 10 | functional ECO、logic rectification、patch generation | 支撑等价 patch、功能验证和失败恢复讨论 |
| `逻辑综合与等价验证/` | 4 | SAT sweeping、sequential redundancy、formal checking | 支撑等价点搜索和验证闭环 |
| `机器学习与时序预测/` | 21 | timing prediction、GNN/RL gate sizing、AI for EDA benchmark | 支撑 timing-aware ranking 和后续智能扩展 |
| `传统缓冲器与门尺寸/` | 5 | buffer insertion、gate sizing、物理优化 | 支撑传统 timing ECO baseline |
| 根目录 Markdown | 2 | 文献索引和 AI_ECO 索引 | 当前 literature matrix 的入口材料 |

## 6. 当前正式主线材料优先级

| 优先级 | 材料 | 原因 |
|---|---|---|
| P0 | 学长 RSECO Word/PDF 主稿 | 决定论文继承点、缺口和可发表性 |
| P0 | `时序ECO优化/` 文献 | 直接定义 related work 和 baseline |
| P0 | `逻辑综合与等价验证/` 文献 | 支撑等价点搜索和 formal verification |
| P1 | `传统缓冲器与门尺寸/` 文献 | 用于比较 B&G、gate sizing、buffer insertion |
| P1 | `功能ECO与逻辑修复/` 文献 | 用于 patch generation 和 failure-aware 叙事 |
| P1 | `机器学习与时序预测/` 文献 | 用于 timing-aware ranking 和后续 AI 扩展 |
| P2 | 课题一/二/三/四构想 | 用于长期路线，不作为第一阶段实现目标 |

## 7. 派生核验提示

第一轮 P0 文献核验发现，`ECO相关文献/逻辑综合与等价验证/` 下标为 *SAT Sweeping with Local Observability Don't-Cares* 的本地 PDF 内容实际为 keeper architecture 论文，不能作为 SAT sweeping 引文证据。原始文件继续保留原位，不改名、不覆盖。第十批已从 Cadence Labs 原始链接的 Common Crawl 归档恢复正确 6 页 PDF 并完成哈希与首末页核验，但该副本只存于 Git 忽略的本机缓存，不进入仓库或发布包；正确书目、归档定位、两个文件的 SHA256、证据等级和再分发状态统一记录在 `docs/literature/core_paper_notes.md` 与 `docs/literature/source_manifests/sat_sweeping_local_odc_dac2006.json`。
