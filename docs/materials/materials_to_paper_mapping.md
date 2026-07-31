# 材料到新论文用途映射

更新时间：2026-07-07

## 1. 新论文暂定结构

| 章节 | 目标 |
|---|---|
| Introduction | 说明 timing ECO 痛点、旧 RSECO 启发、新工作缺口 |
| Related Work | 归纳 timing ECO、resynthesis、functional ECO、formal verification、AI timing optimization |
| Problem Formulation | 定义 resynthesis-assisted timing ECO、patch boundary、失败类型 |
| Method | Failure-aware cut refinement + timing-aware patch ranking |
| Benchmark Flow | 公开 benchmark timing ECO case generation |
| Experiments | 成功率、patch size、logic level、runtime、消融实验 |
| Discussion | 工业案例、适用边界、局限 |
| Conclusion | 总结贡献和后续方向 |

## 2. 材料用途映射

| 材料 | 论文用途 | 使用方式 |
|---|---|---|
| 学长 RSECO 主稿 | Introduction / Method / Experiments | 继承问题定义、算法结构、实验指标 |
| 学长 RSECO PDF | Method / Experiments | 核对公式、图表、结果表 |
| 学长英文稿 | Abstract / Introduction | 术语和英文表达参考 |
| `课题构想.md` | Introduction / Future Work | 说明 ECO 研究背景和长期路线 |
| `课题二_功能时序协同ECO_详细文档.md` | Discussion / Future Work | 支撑后续功能-时序协同扩展 |
| `ECO技术研究-课题概述.docx` | Introduction / Motivation | 提供导师视角和工程风险判断 |
| `时序ECO优化/` 文献 | Related Work / Baselines | 直接比较 timing ECO 方法 |
| `传统缓冲器与门尺寸/` 文献 | Related Work / Baselines | 支撑 B&G baseline |
| `逻辑综合与等价验证/` 文献 | Method / Verification | 支撑 SAT sweeping、equivalence checking |
| `功能ECO与逻辑修复/` 文献 | Related Work / Method | 支撑 patch generation 和 logic rectification |
| `机器学习与时序预测/` 文献 | Related Work / Discussion | 支撑 timing-aware ranking 和后续学习扩展 |

## 3. Claim-Evidence 起点

| 论文 claim 草案 | 需要的证据 | 当前材料来源 | 缺口 |
|---|---|---|---|
| 严重 timing violation 不能仅靠 B&G 稳定修复 | B&G 与 RSECO 对比 | 学长实验表 + timing ECO 文献 | 需要公开 benchmark 复现 |
| 重综合网表可提供更浅逻辑级数的 patch 来源 | 原始/重综合网表 Max-LL 对比 | 学长表 1 | 需要新 flow 复现 |
| 固定 min-cut 可能失败 | w/o CutFinder 失败表 | 学长表 5/6 | 需要失败类型定义 |
| failure-aware refinement 能提升成功率 | 消融实验 | 新实验 | 待做 |
| timing-aware ranking 能降低 patch 代价 | ranking 对比实验 | 新实验 | 待做 |

## 4. 优先转化顺序

1. 先把学长旧稿转成 claim-evidence matrix。
2. 再把 timing ECO 和 equivalence checking 文献转成 related work matrix。
3. 然后设计 benchmark flow 补公开证据。
4. 最后再开始写方法和实验章节草稿。

