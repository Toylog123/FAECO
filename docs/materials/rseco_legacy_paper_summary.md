# 学长 RSECO 旧稿归纳

更新时间：2026-07-07

原始文件：

- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.docx`
- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.pdf`
- `论文/基于重综合的掩膜前时序ECO框架研究_英文.docx`

## 1. 论文定位

旧稿提出 **RSECO：一种基于重综合的掩膜前时序 ECO 框架**。它关注的问题是：芯片设计后期出现严重 setup timing violation 时，传统 buffering 和 gate sizing 难以解决逻辑级数过深的问题；直接重综合整个模块又会破坏已有物理设计。RSECO 利用重新综合得到的新网表作为候选来源，将其中时序更优、且与原始网表等价的局部 patch 移植回原始 APR 网表。

## 2. 可继承的技术主线

| 模块 | 旧稿内容 | 新工作继承方式 |
|---|---|---|
| 问题定义 | 掩膜前时序 ECO，使用重综合网表辅助修复严重违例 | 继续作为主问题，不改成 post-mask ECO |
| 等价点搜索 | 基于 SAT-Sweeping 的等价点搜索 | 作为 patch boundary 合法性的基础 |
| 匹配替换 | 关键路径感知的匹配替换算法 | 作为 Failure-Aware RSECO 的核心继承对象 |
| 网络流切割 | 基于权重函数和 min-cut 的 patch extraction | 作为后续 failure-aware refinement 的基础 |
| CutFinder | 递归学习策略调整搜索空间 | 新工作可把它重写为 failure-aware cut refinement |
| 实验指标 | WNS、TNS、Max-LL、Runtime、Change Num、Patch Size | 继续使用，并补公开 benchmark 可复现版本 |

## 3. 旧稿已有结构

| 章节 | 当前作用 | 后续处理 |
|---|---|---|
| 摘要 | 概括 RSECO 背景、方法和实验效果 | 需要重写，突出可复现和 failure-aware 新贡献 |
| 引言 | 描述 timing ECO 背景和重综合动机 | 保留框架，重写缺口和贡献 |
| 相关工作 | 覆盖 B&G、timing ECO、ML timing prediction | 需要更新 2024-2026 文献 |
| 形式化定义 | 布尔电路、切割、等价切割、ECO 问题 | PDF 公式主体可见；Word 字段更新证明原式(16)-(20)应改为(15)-(19)，FAECO 仍需重写符号和假设 |
| 算法框架 | 等价点搜索、关键路径感知匹配替换 | 作为主方法基础 |
| 扩展问题与优化 | 功能损伤、搜索空间优化、CutFinder | 新工作的主要创新入口 |
| 实验验证 | 8 个工业组合电路案例、图9和表1-5 | 保留为历史 case study，补公开 benchmark |
| 结束语 | 总结 RSECO | 按新贡献重写 |

## 4. 已发现的风险

| 风险 | 说明 | 处理策略 |
|---|---|---|
| 代码不可用 | 当前没有原实现，且用户判断旧代码可能有大问题 | 不再依赖旧代码，重写最小可复现原型 |
| 数据不可公开 | 旧稿使用 8 个工业案例，审稿时可复现性弱 | 补公开 benchmark flow |
| 编号和数据一致性 | 公式缓存编号未刷新、图6误引；表2正文/Avg/逐行均值/slack 反算四套统计不一致 | 按 `legacy_source_locator.md` 和 `legacy_table2_recalculation.md` 修订，旧均值不作为 FAECO 证据 |
| baseline 描述不足 | B&G 商业工具设置不够透明 | 补公开 baseline 和公平性说明 |
| 创新边界不够尖锐 | 容易被认为是重综合 + min-cut 的工程组合 | 聚焦 failure-aware cut refinement |

## 5. 新工作继承结论

旧稿不是废弃材料，而是本项目的基础问题定义和叙事来源。新工作不再以“复刻 RSECO 旧实现”为目标，而是以旧稿为基础提出：

> 一个可复现的 Failure-Aware RSECO 框架，通过公开 benchmark flow、验证反馈驱动的 cut refinement 和 timing-aware patch ranking，解决旧 RSECO 在代码、数据和切割失败恢复方面的不足。
