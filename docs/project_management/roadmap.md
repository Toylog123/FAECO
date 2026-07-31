# FAECO 长期路线图

更新时间：2026-07-07

## 1. 总目标

形成一篇可投稿的中文工程类论文，暂定题目为：

**基于验证反馈的重综合辅助时序 ECO 框架**

方法名暂定为 **FAECO: Failure-Aware ECO**。

## 2. 阶段路线

| 阶段 | 名称 | 时间预估 | 核心目标 | 主要交付物 |
|---|---|---:|---|---|
| Phase 0 | 项目整理与方向固定 | 已完成 | 固定主线、整理材料、建立工程结构 | `docs/mainline.md`、材料索引、实验设计草案 |
| Phase 1 | 论文证据审计 | 1-2 周 | 明确旧稿哪些 claim 可继承、哪些需要补实验 | claim-evidence matrix、预投稿审计 |
| Phase 2 | Benchmark flow 细化 | 1-2 周 | 固定公开 benchmark、case 构造方式和指标 | benchmark flow spec、case schema |
| Phase 3 | 最小算法原型 | 3-5 周 | 跑通 FAECO 最小闭环 | netlist/cone/cut/equivalence/ranking 原型 |
| Phase 4 | 第一轮实验 | 2-4 周 | 形成可用于论文的初步结果表 | experiments、tables、figures、summary |
| Phase 5 | Sequential 场景扩展 | 3-5 周 | 从组合逻辑扩展到 reg-to-reg cone | sequential cone flow、路径级实验 |
| Phase 6 | 论文初稿 | 2-3 周 | 完成中文论文完整初稿 | paper draft、图表、参考文献 |
| Phase 7 | 内部审稿与修改 | 2-4 周 | 修复方法、实验、叙事硬伤 | review report、revision roadmap、修订稿 |
| Phase 8 | 投稿准备 | 1-2 周 | 按目标期刊/会议格式提交 | final manuscript、cover letter、supplement |

## 3. 阶段门槛

| 阶段门槛 | 通过标准 |
|---|---|
| Phase 1 -> 2 | 核心 claim 和证据缺口明确 |
| Phase 2 -> 3 | benchmark 输入、输出、指标和 baseline 明确 |
| Phase 3 -> 4 | 最小闭环可运行，单元测试通过 |
| Phase 4 -> 5 | combinational 实验能支撑至少 2 张结果表 |
| Phase 5 -> 6 | sequential cone 实验有清晰结论 |
| Phase 6 -> 7 | 完整初稿包含方法、实验、相关工作和局限 |
| Phase 7 -> 8 | P0/P1 审稿问题关闭 |

## 4. 当前所处阶段

当前处于 **Phase 1：论文证据审计** 的开始位置。

Phase 0 已完成：

- 主线已固定为 FAECO。
- 工程目录已重构。
- 原始材料已归纳。
- benchmark flow / failure-aware cut / patch ranking 已有草案。

下一步：

1. 建立 claim-evidence matrix。
2. 完成旧稿预投稿审计。
3. 将 benchmark flow 草案细化为可执行 spec。

