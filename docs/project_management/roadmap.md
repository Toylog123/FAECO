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
| Phase 1 | 论文证据审计 | 已完成 | 明确旧稿哪些 claim 可继承、哪些需要补实验 | claim-evidence matrix、预投稿审计 |
| Phase 2 | Benchmark flow 细化 | 已完成 | 固定公开 benchmark、case 构造方式和指标 | benchmark flow spec、case schema |
| Phase 3 | 最小算法原型 | 已完成 | 跑通 FAECO 最小闭环 | netlist/cone/cut/equivalence/ranking 原型 |
| Phase 4 | 第一轮实验 | 已完成（Stage A 5-case + Stage B 8-case） | 形成可用于论文的初步结果表 | experiments、tables、figures、summary |
| Phase 5 | Sequential 场景扩展 | 部分完成（N31-05 待启动） | 从组合逻辑扩展到 reg-to-reg cone | sequential cone flow、路径级实验 |
| Phase 6 | 论文初稿 | 部分完成（L01 Related Work 初稿落地；N05 方法符号表 + 主体段落待启动） | 完成中文论文完整初稿 | paper draft、图表、参考文献 |
| Phase 7 | 内部审稿与修改 | 未开始 | 修复方法、实验、叙事硬伤 | review report、revision roadmap、修订稿 |
| Phase 8 | 投稿准备 | 未开始 | 按目标期刊/会议格式提交 | final manuscript、cover letter、supplement |

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

当前处于 **Phase 6：论文初稿** 的开始位置（Phase 4 combinational 实验 + Stage B 8-case 端到端已收口，L01 Related Work 初稿已落地，N05 方法符号表待启动）。

Phase 0-4 已完成：

- Phase 0（2026-07-07）：主线 FAECO 固定、工程目录重构、材料归纳、benchmark/cut/ranking 草案
- Phase 1（2026-07-14 至 2026-07-19）：claim-evidence matrix 完整（含 16 页 PDF 页级出处）、预投稿审计、公式图表审计、revision roadmap
- Phase 2（2026-07-19）：EPFL `v2025.1` 主来源固定、ISCAS85 边界明确、case schema / baseline protocol / metrics and tables 完整
- Phase 3（2026-07-17 至 2026-07-20）：最小闭环原型 + 66 项 Stage A 单元测试
- Phase 4（2026-07-20 至 2026-07-31）：Stage A 5-case combinational smoke + Stage B 8-case 端到端（mapping 8/8 + STA 8/8）；24 项新增 TDD 测试；A-only 范围 22 commits 入库

下一步（按 Phase 6 写作阶段）：

1. N05 方法符号表：基于 `method_rewrite_readiness.md` 18 项要素（METH-02/15 ready、METH-17 partial）产出 N05 伪代码与符号表初稿（PM27）。
2. 论文 Introduction / Method / Experiments / Conclusion 主体段落落地（PM25/27/28）。
3. L01 Related Work 迁入 `paper/submission/related_work.md`，按论文主风格重组并补充 [F08-B]/[B06] evidence-level 边界声明（PM26）。
4. N31-01 X19 多轮 refinement 设计（需用户 design 审批；blocked on user）。
5. N31-03 ORFS techmap library 修复 L31-01 CEC limitation（blocked on user，PDK 部分）。
6. N31-05 SKY130 sequential ECO 拓展（M5 完成，需 DFF/restore 进 SDC）。

