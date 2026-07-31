# RSECO 学长论文接手发表方案

更新时间：2026-07-07
主目标：接手赵晖学长的 RSECO 工作，补齐论文发表所需的技术、实验、叙事和投稿材料。

## 1. 目标重新定位

当前工作的主线不是重新开一个全新的 ECO 课题，而是接手已有的 **RSECO：一种基于重综合的掩膜前时序 ECO 框架**。由于学长论文尚未发表，后续工作应围绕“旧稿抢救、实验补强、叙事重构、投稿落地”展开。

因此，后续优先级应调整为：

1. 先判断旧稿为什么没有发出去。
2. 再确认旧工作哪些部分可继承、哪些部分必须重做或补证据。
3. 优先补足投稿硬伤，而不是立即另做一个新系统。
4. 在旧稿基础上增加一个明确的新贡献，使论文不只是“整理学长工作”。

## 2. 当前旧稿证据

已检查文件：

`论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.docx`

结构状态：

| 项目 | 当前证据 | 判断 |
|---|---|---|
| 论文标题 | RSECO：一种基于重综合的掩膜前时序ECO框架 | 主题清楚 |
| 正文规模 | 149 个非空段落，约 1.26 万中文字符 | 已是完整论文雏形 |
| 表格数量 | 6 个表 | 实验部分已有一定基础 |
| 核心贡献 | SAT-Sweeping 等价点搜索、关键路径感知匹配替换、递归学习式 CutFinder | 方法线完整 |
| 实验数据 | 8 个工业组合电路案例 | 有说服力，但可复现性和公开性可能是风险 |
| baseline | 商业工具中的传统时序 ECO 方法 B&G | 有工业对比，但需要解释工具、设置和公平性 |
| 结果指标 | WNS、TNS、Max-LL、Runtime、Change Num、Patch Size、CutFinder 成功情况 | 指标较完整 |

## 3. 旧稿核心内容判断

### 3.1 论文真正的技术主线

RSECO 解决的是 **掩膜前时序 ECO** 中严重 setup violation 难以通过传统 buffering/gate sizing 修复的问题。它不直接做 post-mask spare-cell ECO，也不是功能 ECO。其核心思想是：

> 当原始 APR 网表在新约束下出现严重时序违例时，先对 RTL 重新综合得到一个满足新约束的新网表，再从新网表中找到与原始网表功能等价、但逻辑级数更浅的局部子电路，将该局部 patch 移植回原始网表。

这个故事的关键词应当是：

- pre-mask timing ECO
- resynthesis-assisted ECO
- equivalence-guided patch replacement
- critical-path-aware min-cut
- layout-preserving incremental repair

### 3.2 当前稿件的可发表潜力

旧稿有真实贡献，不是普通课程项目。它已经具备方法、算法、实验和工业案例。若没有发表，可能问题不在“完全没有东西”，而在以下几个方面：

1. **创新定位不够尖锐**：容易被审稿人理解为“局部重综合 + min-cut 的工程组合”，需要强调它与传统 timing ECO、resynthesis、ECO patching 的边界。
2. **实验可复现性不足**：8 个工业案例有价值，但如果不能公开，必须补公开 benchmark 或给出更透明的构造方式。
3. **baseline 解释不足**：B&G 是商业工具方法，但需要明确工具版本、约束、设置、公平性和失败场景。
4. **形式化定义和结果存在一致性问题**：PDF 公式主体可见；Word 字段更新证明原式(16)-(20)应改为(15)-(19)，另有图6误引和表2四套统计冲突；投稿前必须修复编号、交叉引用、数据和定义。
5. **论文语言和叙事不够国际会议化**：需要从“提出了一个框架”改成“解决了什么现有方法无法处理的技术缺口，并用什么证据证明”。

## 4. 接手后的最优路线

### 4.1 第一阶段：论文审计，而不是先写代码

目标：判断旧稿是否能通过“补写+补实验”投稿，还是必须重做实现。

必须完成：

1. 完整阅读旧稿，标注每个贡献是否有实验支撑。
2. 建立“声明-证据矩阵”：每一句核心贡献对应哪张表、哪个实验、哪个算法。
3. 检查公式、图、表、引用是否完整。
4. 检查是否缺少投稿必须内容：实验环境、数据来源、baseline 设置、ablation、limitations。
5. 模拟审稿，找出可能导致拒稿的 P0/P1 问题。

阶段产物：

- `paper/rseco_claim_evidence_matrix.md`
- `paper/rseco_pre_submission_review.md`
- `paper/rseco_revision_roadmap.md`

### 4.2 第二阶段：恢复最小可验证实现

目标：不一定复刻全部旧代码，但至少要能验证论文中的核心算法链条。

优先恢复的不是完整工业工具链，而是以下最小闭环：

1. gate-level netlist 表示。
2. 新旧网表等价点搜索。
3. 关键路径权重建模。
4. min-cut 生成 patch boundary。
5. patch 替换后的等价性检查。
6. 对小型公开 benchmark 输出 patch size 和逻辑级数变化。

如果旧代码确实找不回，重写策略应围绕“证明论文核心机制”：

- 用 Python 实现算法原型；
- 用 NetworkX 做 min-cut；
- 用 Z3/ABC 做等价检查；
- 用 Yosys 处理 Verilog 到 gate-level netlist；
- 暂时不碰商业 APR 流程，等原型稳定后再接 OpenSTA。

### 4.3 第三阶段：补公开实验

目标：解决“工业案例不可公开”的审稿风险。

建议新增实验：

| 实验 | 目的 | 最低要求 |
|---|---|---|
| 公开 benchmark 补充 | 增强可复现性 | ISCAS/EPFL/ITC 中至少 5-10 个设计 |
| 消融实验 | 证明 CutFinder 和关键路径权重有用 | w/o weight、w/o CutFinder、random cut 对比 |
| 失败案例分析 | 提升可信度 | 说明何时无法找到等价 patch |
| 参数敏感性 | 证明算法不是调参偶然 | 对权重参数、迭代深度做曲线 |
| 运行时间分解 | 回应可扩展性 | 等价点搜索、min-cut、验证分别计时 |

工业案例仍可保留，但应定位为“industrial case study”，公开 benchmark 作为 reproducibility 支撑。

### 4.4 第四阶段：重写论文叙事

建议把论文贡献重写为：

1. **问题定义贡献**：定义 resynthesis-assisted pre-mask timing ECO，即在保持原始物理设计稳定的前提下，移植重综合网表中的时序友好 patch。
2. **算法贡献**：提出 equivalence-guided critical-path-aware patch replacement，将 SAT-sweeping 等价点搜索与 min-cut patch extraction 结合。
3. **鲁棒性贡献**：提出 CutFinder 递归权重调整机制，解决初始割集无法匹配或功能损伤的问题。
4. **实验证据贡献**：在工业案例和公开 benchmark 上证明 RSECO 相比传统 B&G 对严重违例更有效，并能控制修改规模。

注意：不要轻易写“首个”“最优”“通用”。除非文献审计后能支撑，否则改成更稳的表述，如“a resynthesis-assisted framework”“a critical-path-aware replacement method”。

## 5. 论文发表版本建议

### 5.1 如果目标是先发出去

推荐路线：

- 中文核心/国内 EDA 会议/中文期刊版本；
- 重点是把旧稿补完整，减少实验重做；
- 语言用中文，突出工程场景和工业案例；
- 目标是在 2-3 个月内形成可投稿版本。

### 5.2 如果目标是冲更高水平

推荐路线：

- 英文会议/期刊版本；
- 必须补公开 benchmark、消融实验、可复现实现和更强 related work；
- 需要重写 abstract、introduction、method 和 experiment；
- 目标周期至少 4-6 个月。

### 5.3 最现实的双版本策略

先做中文/国内可投版本，把稿件救活；同时保留英文扩展线：

1. 中文版：RSECO 原工作整理 + 补实验 + 工程案例。
2. 英文扩展版：RSECO + verification-aware / learning-assisted patch selection，作为后续更高目标。

这样不会把所有风险压在一个长期英文顶会目标上。

## 6. 下一批任务清单

| ID | 任务 | 状态 | 优先级 | 完成标准 | 下一步动作 |
|---|---|---|---|---|---|
| R01 | 建立论文接手材料目录 | pending | P0 | `paper/` 下有审计、修改、投稿子目录 | 创建目录结构和 README |
| R02 | 提取旧稿章节和图表清单 | done | P0 | 每个章节、图、表都有编号和用途说明 | 已生成 `legacy_source_locator.md`；后续随新稿重编号 |
| R03 | 建立声明-证据矩阵 | done | P0 | 每个核心 claim 都能对应实验或文献 | C01-C12 已完成页级来源和缺口标注 |
| R04 | 做预投稿审稿 | done | P0 | 形成 P0/P1/P2 问题清单 | 已完成；后续在新稿形成后重新模拟审稿 |
| R05 | 修复公式和符号问题 | in_progress | P0 | 公式变量、编号、定义完整 | 旧稿问题已定位；待在 FAECO Method 中重写定义并修复编号/引用/数值 |
| R06 | 确认旧代码/实验数据能否找到 | pending | P0 | 明确“可恢复/不可恢复/部分恢复” | 搜索本地、询问学长、查备份 |
| R07 | 设计公开 benchmark 补实验 | pending | P1 | 明确 benchmark、变更构造、指标和 baseline | 先选 ISCAS/EPFL 小规模电路 |
| R08 | 重写 introduction 和 contributions | pending | P1 | 形成投稿版叙事 | 按“背景-压力-缺口-方法-证据”重写 |
| R09 | 更新 related work | pending | P1 | 加入近年 ML/ECO/timing prediction 工作 | 用现有 48 篇 PDF 建矩阵 |
| R10 | 确定投稿目标 | pending | P1 | 明确中文优先还是英文扩展 | 根据补实验可行性决定 |

## 7. 立即建议

现在不要急着从零实现新 ECO 系统。正确顺序是：

1. **先审旧稿**：确认论文没发出去的真实原因。
2. **再救证据**：找旧代码、旧实验日志、旧 benchmark、商业工具报告。
3. **再补最小实验**：只补能支撑投稿硬伤的实验。
4. **最后重写论文**：把旧稿改成目标 venue 能接受的叙事。

如果旧实验数据和代码能找回，优先走“补写+补实验+改投”；如果找不回，再重建最小原型，目标是验证 RSECO 核心机制，而不是扩大成全新 AI ECO 课题。
