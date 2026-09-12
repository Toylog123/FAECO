# FAECO 论文修订路线

更新时间：2026-07-20

目标：不按原样修补 RSECO 旧稿，而是保留重综合辅助 timing ECO 的问题主线，用 FAECO 的公开、可复现工程证据重写方法和实验。

## 1. 修订原则

1. 旧稿 PDF 只作为历史 claim、公式思想和工业结果的定位源，不作为 FAECO 新结果的证据源。
2. 当前实验 artifacts 是 FAECO 工程事实的权威源；`unavailable`、proxy 和 smoke 状态必须按原口径表述。
3. 先形成真实 formal、baseline、failure recovery 和 timing 证据，再写摘要、贡献和结论中的强 claim。
4. 数字集中进入表格；正文只陈述由表格直接支持的趋势和结论。

## 2. 执行路线

| ID | 阶段 | 状态 | 优先级 | 动作 | 完成标准 |
|---|---|---|---|---|---|
| RR01 | 旧稿证据定位 | done | P0 | 完成 C01-C12、公式、图表和表格的页级定位 | `legacy_source_locator.md`、`claim_evidence_matrix.md`、`formula_figure_audit.md` 一致 |
| RR02 | 旧稿硬伤处置 | in_progress | P0 | 修正公式缓存编号和图6引用；处置表2不可认证的均值 | 已证明原式(16)-(20)应改为(15)-(19)，并完成表2四套统计复算；剩余动作是修改可编辑稿引用并决定是否删除旧均值 |
| RR03 | Formal/ABC 证据 | pending | P0 | 按已批准的门级 full-netlist scope 接入 `yosys-abc` 和 Yosys-BLIF 规范化 | 5-case formal/baseline 有真实状态、日志、版本、产物和 runtime |
| RR04 | Failure-aware 证据 | in_progress | P0 | 实现多轮 refinement 和 without F1/F3/F4 消融 | 已定位 replacement proxy 与真实恢复口径的差异；待确认 Stage A 成功口径后实现 recovery iterations、停止原因和消融表 |
| RR05 | Timing 证据 | in_progress | P0 | OpenSTA 3.1.0 已在 WSL2 构建并通过最小 Liberty/Verilog/SDC smoke；下一步接入 Stage B path mapper、report parser，并扩展 sequential/reg-to-reg case | 可报告真实 WNS/TNS、critical path 和 timing closure 状态 |
| RR06 | 公开 benchmark 证据 | in_progress | P0 | EPFL `v2025.1`、MIT、8 个 Verilog/官方 BLIF blob 和隔离 CEC 已固定；Yosys JSON 已批准为权威内部格式，下一步正式导入并替换许可未声明的 ISCAS85 主表依赖 | benchmark 来源、license、SHA、case 构造、formal 和配置可追溯 |
| RR07 | 方法重写 | pending | P1 | `method_rewrite_readiness.md` 已完成 ready/partial/blocked 盘点；待 X18/X19/X21/X22 关闭关键阻塞后，用工程实现重写问题定义、符号、算法和停止条件 | Method 与代码字段、实验配置、指标边界和 related-work 定位一致，不把目标规范写成已实现能力 |
| RR08 | 实验重写 | pending | P1 | 固定 main comparison、recovery、ablation、runtime、environment 表 | 表中每个数字可追溯到 artifact，正文结论与表一致 |
| RR09 | 引言与贡献重写 | pending | P1 | 按“背景-缺口-方法-证据”重写 | 贡献以 failure-aware refinement 为中心，不沿用旧工业数值 |
| RR10 | 完整审稿 | pending | P1 | 完成 claim/evidence 复核、模拟审稿和二次修订 | 无 P0 问题，所有强 claim 有直接证据 |

## 3. 当前写作边界

当前可以写：FAECO 已形成 5-case Stage A 原型、多 baseline 接口、结构化 runtime/environment schema、cone-level replacement 和 single-refinement failure proxy。

当前不能写：已通过 5-case ABC/SAT formal、已取得真实 ABC 优化收益、正式 batch 已使用真实 STA critical path、获得多轮 failure recovery 统计、完成 timing closure，或已在公开 benchmark 上优于旧 RSECO/商业工具。

## 4. 下一批交付物

| 顺序 | 交付物 | 前置条件 |
|---:|---|---|
| 1 | 5-case ABC formal/baseline/runtime artifacts | 门级 full-netlist formal scope 已批准，等待 runner 实现 |
| 2 | multi-iteration failure recovery 与 ablation 表 | 多轮 refinement loop |
| 3 | 旧稿三项硬伤修订记录 | 表2逐 case 重算和式(15)来源确认 |
| 4 | FAECO Method 符号表与伪代码初稿 | RR03/RR04 的字段和停止条件稳定 |
| 5 | 论文 main comparison/ablation/runtime 表初稿 | RR03-RR06 的 artifacts 完成 |
| 6 | Related Work 第一版证据化段落 | 25 篇 A 级全文和 1 条 B 级官方证据已覆盖 negotiation/restructuring、multi-error/multi-target/resource-aware patch、functional correspondence、传统/学习式/物理感知/LLM B&G、结构变化容忍/跨节点 timing prediction 和 SAT-sweeping；可直接进入分问题设置写作，DAC 2018 保持 B 级边界且不阻塞初稿 |
