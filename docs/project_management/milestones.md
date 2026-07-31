# FAECO 里程碑

更新时间：2026-07-07

## M0：项目初始化与材料整理

状态：完成

交付物：

- `README.md`
- `docs/mainline.md`
- `docs/engineering_structure.md`
- `docs/materials/`
- `docs/literature/literature_matrix.md`
- `docs/experiment_design/`

完成标准：

- 主线清楚；
- 原始材料可追溯；
- 工程、论文、实验目录分离。

## M1：旧稿审计完成

状态：未开始

交付物：

- `docs/paper_audit/claim_evidence_matrix.md`
- `docs/paper_audit/pre_submission_review.md`
- `docs/paper_audit/revision_roadmap.md`

完成标准：

- 所有核心 claim 有证据或缺口标记；
- 公式、图表、实验和 related work 的硬伤明确；
- 明确哪些旧稿内容可继承、哪些必须重做。

## M2：Benchmark Flow 定稿

状态：草案完成，待细化

交付物：

- `docs/experiment_design/benchmark_flow.md`
- `docs/experiment_design/case_schema.md`
- `docs/experiment_design/baseline_protocol.md`

完成标准：

- 选定第一批公开 benchmark；
- 明确 case generation 输入输出；
- 明确 baseline 和指标；
- 能转化为实现任务。

## M3：FAECO 最小闭环原型

状态：未开始

交付物：

- `src/rseco/` 原型代码；
- `tests/` 单元测试；
- 最小 demo case；
- 初始实验日志。

完成标准：

- 能读取/表示 netlist 或简化电路图；
- 能抽取 cone；
- 能做 min-cut；
- 能做等价验证；
- 能执行 failure-aware refinement；
- 能输出 patch ranking。

## M4：Combinational 实验完成

状态：未开始

交付物：

- `experiments/YYYYMMDD_combinational_*`
- 结果表：成功率、patch size、logic level、runtime、verification pass rate；
- 消融实验表。

完成标准：

- fixed min-cut 和 FAECO 有可比较结果；
- 至少能支撑论文 2 张结果表；
- 失败案例有解释。

## M5：Sequential Cone 扩展完成

状态：未开始

交付物：

- sequential benchmark cone extraction flow；
- 路径级 ECO 实验；
- WNS/TNS 或路径 delay 结果。

完成标准：

- 能解释寄存器边界；
- 能处理 reg-to-reg path 中的组合逻辑 cone；
- 实验能说明方法更接近真实 timing ECO 场景。

## M6：论文初稿完成

状态：未开始

交付物：

- `paper/draft/` 中文论文初稿；
- `paper/figures/` 图；
- `paper/tables/` 表；
- `paper/reviews/` 自审或模拟审稿。

完成标准：

- 论文结构完整；
- 图表都有实验来源；
- 参考文献初步完整；
- 局限性明确。

## M7：投稿版本完成

状态：未开始

交付物：

- 投稿版论文；
- cover letter；
- 补充材料；
- 最终实验归档。

完成标准：

- P0/P1 问题关闭；
- 格式符合目标 venue；
- 所有实验可追溯。

