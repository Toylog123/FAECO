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

状态：完成（2026-07-14 至 2026-07-19）

交付物：

- `docs/paper_audit/claim_evidence_matrix.md`
- `docs/paper_audit/pre_submission_review.md`
- `docs/paper_audit/revision_roadmap.md`
- `docs/paper_audit/legacy_source_locator.md`
- `docs/paper_audit/legacy_table2_recalculation.md`
- `docs/paper_audit/formula_figure_audit.md`
- `docs/paper_audit/method_rewrite_readiness.md`

完成标准：

- 所有核心 claim 有证据或缺口标记 ✓
- 公式、图表、实验和 related work 的硬伤明确 ✓（公式编号 (1)-(14)/(16)-(20) → (15)-(19)、图 6 误引、表 2 四套统计冲突均已记录）
- 明确哪些旧稿内容可继承、哪些必须重做 ✓

## M2：Benchmark Flow 定稿

状态：完成（2026-07-19）

交付物：

- `docs/experiment_design/benchmark_flow.md`
- `docs/experiment_design/case_schema.md`
- `docs/experiment_design/baseline_protocol.md`
- `docs/experiment_design/benchmark_selection.md`
- `docs/experiment_design/benchmark_source_and_license_audit.md`
- `docs/experiment_design/metrics_and_tables.md`
- `docs/experiment_design/failure_taxonomy.md`
- `docs/experiment_design/faeco_algorithm.md`

完成标准：

- 选定第一批公开 benchmark ✓（EPFL `v2025.1` 主来源 + ISCAS85 本地 smoke）
- 明确 case generation 输入输出 ✓
- 明确 baseline 和指标 ✓（fixed/random/size-only/critical-path-only/ABC wrapper/FAECO）
- 能转化为实现任务 ✓

## M3：FAECO 最小闭环原型

状态：完成（2026-07-17 至 2026-07-20）

交付物：

- `src/rseco/` 22 个模块
- `tests/` 90 项单元测试（66 Stage A + 24 Stage B）
- `data/cases/minimal/` 5-case smoke（c17 N22/N23 + c432 + c499 + c880）
- `experiments/20260717_minimal_combinational_demo/` + `experiments/20260718_minimal_combinational_batch_demo/`

完成标准：

- 能读取/表示 netlist 或简化电路图 ✓（`src/rseco/netlist.py` Genus 风格多行 Verilog parser）
- 能抽取 cone ✓（`src/rseco/graph.py` fanin cone）
- 能做 min-cut ✓（`src/rseco/cut.py` fixed/weighted/s-t Edmonds-Karp）
- 能做等价验证 ✓（`src/rseco/equivalence.py` structural signature + `src/rseco/yosys_abc.py` Yosys-BLIF-ABC CEC）
- 能执行 failure-aware refinement ✓（`src/rseco/refinement.py` F1-F5）
- 能输出 patch ranking ✓（`src/rseco/ranking.py` deterministic scoring）

## M4：Combinational 实验完成

状态：完成（2026-07-20 至 2026-07-31）

交付物：

- `experiments/20260718_minimal_combinational_batch_demo/`（5-case Stage A smoke）
- `experiments/20260720_epfl_wave1_yosys_json/` + `experiments/20260728_epfl_wave2_yosys_json/`（EPFL wave 1+2 Yosys JSON 导入）
- `experiments/20260731_epfl_ctrl_sky130_mapping/`（ctrl SKY130 Liberty mapping 单 case）
- `experiments/20260731_epfl_ctrl_stage_b/`（ctrl 端到端试点）
- `experiments/20260731_epfl_8case_stage_b/`（Stage B 8-case 端到端 batch）
- 结果表：Stage B `tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}` + Stage A 5-case `tables/baseline_comparison.{json,md}` + `tables/runtime_breakdown.{json,md}` + `tables/failure_recovery.{json,md}`

完成标准：

- fixed min-cut 和 FAECO 有可比较结果 ✓（baseline_comparison 表 5 个 run × 6 个方法）
- 至少能支撑论文 2 张结果表 ✓（Stage A + Stage B 各 1 张主表 + 4 张附表）
- 失败案例有解释 ✓（F1-F5 taxonomy 覆盖）

CEC limitation（SKY130 Liberty 不含 `clkinv_1`）与 STA slack limitation（combinational 无 timing path）已记录于 R31-01 与 L31-02；待 N31-03 / N31-05 修复。

## M5：Sequential Cone 扩展完成

状态：未开始（N31-05 计划中）

交付物：

- sequential benchmark cone extraction flow；
- 路径级 ECO 实验；
- WNS/TNS 或路径 delay 结果。

完成标准：

- 能解释寄存器边界；
- 能处理 reg-to-reg path 中的组合逻辑 cone；
- 实验能说明方法更接近真实 timing ECO 场景。

前置：把 DFF/restore 信号加进 SDC，准备 clock tree，扩展 mapping/STA 到 sequential EPFL benchmark。当前 Stage B 8-case 全是 combinational circuit，下一步是 N31-05 SKY130 sequential ECO 拓展。

## M6：论文初稿完成

状态：部分完成（L01 Related Work 已落地）

交付物：

- `paper/draft/` 中文论文初稿（`paper/draft/related_work.md` L01 已落地，其余章节待 N05/N08 审批）
- `paper/figures/` 图（待从 8-case 端到端表格生成）
- `paper/tables/` 表（待 N05/N08 审批）
- `paper/reviews/` 自审或模拟审稿（未开始）

完成标准：

- 论文结构完整（Introduction / Related Work / Method / Experiments）—— Method 待 PM27 N05 符号表
- 图表都有实验来源 ✓（Stage B 8-case tables/ 已落盘）
- 参考文献初步完整 ✓（L01 Related Work 6 大主题覆盖 25A/1B）
- 局限性明确 ✓（CEC + STA limitation 已在多处文档标注 A/B 边界）

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

