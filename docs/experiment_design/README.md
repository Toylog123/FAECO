# Experiment Design

用于记录新工作实验设计。

计划产物：

- `benchmark_flow.md`：公开 benchmark timing ECO case 构造流程。
- `benchmark_selection.md`：第一批 benchmark 选择与取舍。
- `benchmark_source_and_license_audit.md`：固定 benchmark 上游版本、许可、哈希和论文使用边界。
- `case_schema.md`：ECO case 数据结构。
- `failure_taxonomy.md`：失败类型、检测条件和反馈动作。
- `failure_aware_cut.md`：failure-aware cut refinement 实验设计。
- `patch_ranking.md`：timing-aware patch ranking 实验设计。
- `baseline_protocol.md`：baseline 定义和公平性协议。
- `metrics_and_tables.md`：指标公式与结果表模板。
- `faeco_algorithm.md`：FAECO 算法伪代码与模块切分。
- `self_audit_protocol.md`：实验立项自审协议（自杀式测试 / 竞争基线先行 / 主张-证据匹配 / 措辞一致性门禁）。

当前状态：

| 文件 | 状态 | 说明 |
|---|---|---|
| `benchmark_flow.md` | 已有草案 | 已明确 Stage A/B/C |
| `benchmark_selection.md` | 已更新 | Stage A 论文主集优先固定版本的 EPFL；许可未声明的 ISCAS85 只作本地 smoke |
| `benchmark_source_and_license_audit.md` | 已更新 | 已固定 EPFL `v2025.1`、MIT、8 个 Verilog/官方 BLIF blob；隔离规范化 CEC 8/8 pass，正式导入仍待权威格式审批 |
| `case_schema.md` | 已有初版 | 后续代码和实验目录按此组织 |
| `failure_taxonomy.md` | 已有初版 | F1-F5 已细化为检测条件和反馈动作 |
| `failure_aware_cut.md` | 已有草案 | 已被 `failure_taxonomy.md` 和 `faeco_algorithm.md` 细化，后续转测试用例 |
| `patch_ranking.md` | 已有草案 | 需固定参数和消融方式 |
| `baseline_protocol.md` | 已有初版 | 需在原型实现后校订运行参数 |
| `metrics_and_tables.md` | 已有初版 + Stage B 真实结果 | Stage A 5-case + Stage B 8-case 真实结果已分别落盘 `experiments/20260718_minimal_combinational_batch_demo/tables/*.json` 和 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}` |
| `faeco_algorithm.md` | 已有初版 | 后续按模块实现 |
| `self_audit_protocol.md` | 新增（2026-08-06） | 由 TCAD 第二轮审稿教训固化的强制检查项，每个新实验立项时必须逐项回答 |
