# FAECO Introduction 初稿（Draft 1）

更新时间：2026-07-31

本文档为论文 Introduction 章节的初稿，基于：
- `docs/mainline.md` 主线定义
- `paper/draft/related_work.md`（L01）6 大主题
- `paper/draft/method_symbol_table.md`（N05）符号与算法骨架
- `docs/project_management/roadmap.md` 当前所处阶段

尚未经用户最终审定；结构和措辞仅作为论文主体起点，禁止作为主表事实性表述。

---

## 1. 问题背景

时序 ECO 是数字后端物理实现的关键修复步骤。当 timing closure 不能在 RTL/综合阶段一次性收敛时，需要通过 ECO 在已布线或已生成版图的网表上做局部修改。传统时序 ECO 主要依赖 buffer insertion（B）和 gate sizing（G）：通过在违例路径上插入缓冲器或调整单元尺寸来减少 delay 并修复 WNS/TNS。这类 B&G 方法在工艺扰动或路径级违例严重的场景下往往力不从心 [T01, T05, B01]。

学长 RSECO 旧稿观察到：把已布线网表中违例 cone 用新综合网表中对应的"时序友好 patch"整体替换，可以获得比 B&G 更稳定的违例修复收益。但 RSECO 的实验完全依赖不可重建的工业数据与未声明 license 的 benchmark，方法可复现性弱，论文投稿前需要重构 [SRC-01..04]。

## 2. 缺口

近十年来的 ECO 工作可以按"方法定位"分成三股：

1. **Timing ECO 主线** [T01-T07]：post-mask spare cells / metal-only resources / template-driven remapping。共同问题是数据来自工业设计、license 不明、不可复现。
2. **Functional ECO 与逻辑修复** [F01-F08]：SAT/interpolation/cube enumeration 等构造 Boolean patch。多面向 functional 修复，与 timing 收益分开。
3. **缓冲/门尺寸** [B01-B06]：固定树最优 buffer insertion / RL+DL 联合 sizing。仍在用 SPICE/工业流或仅当 placement-aware baseline。

公开 EPFL combinational benchmark 上同时跑通 timing ECO 修复 + 等价 + 时序结果 的端到端可复现流程仍然稀缺。SKY130 公开 PDK + EPFL v2025.1 提供了一个组合逻辑基准和工艺库，但 Yosys 0.9 / ABC 0.9 的 techmap 流程在 SKY130 HD Liberty 上产生 `sky130_fd_sc_hd__clkinv_1` placeholder（Liberty 实际不含此 cell），导致 ABC 形式回验失败 [L01][V01]。

另外 [F08-B] DAC 2018 cost-aware multi-target rectification 提供 weighted support cost / patch size / runtime 三维度代价，但仅 B 级证据（NTU/作者站点/IA archive 多源复核仍无合法公开全文）。

## 3. FAECO 方法

本文提出 FAECO：Failure-Aware Resynthesis-Assisted ECO。在 RSECO 思路基础上，把"重综合辅助 patch replacement"形式化为三步流水线：

(a) **多轮 refinement 的切割与替换**：先用固定权重的 fanin cone + weighted s-t min-cut 抽出 selected patch [METH-05 ready]；当 patching 出现等价失败、边界失败、size 过大、timing 收益不足或验证超时（F1-F5）时，按失败类型确定性调整 cut 权重并重新搜索。FAECO 的 failure-aware 反馈循环是 [E03][METH-10 partial]，当前 Stage A 是单次权重更新，X19 设计获批后将升级为 multi-iteration loop。

(b) **公开 benchmark 上的可复现端到端**：使用 EPFL `v2025.1` 8 个 combinational benchmark（ctrl/int2float/router/cavlc/dec/priority/adder/max）作为主数据，固定 commit `8c832d5d07d822d28ba84dc6e95295367702401f` + MIT license。Stage A 5-case（c17×2 + c432 + c499 + c880）已跑通 multi-baseline 比较 + runtime breakdown + failure recovery proxy；Stage B 8-case 已端到端跑通 Yosys `synth -noabc + abc -liberty` 流程映射到 SKY130 HD Liberty + 确定性 pre-layout SDC + OpenSTA pre-layout STA（mapping 8/8 success，STA 8/8 success，slack_status=MET (INF)）。

(c) **方法公开性边界**：本文不下载完整 Sky130 PDK，仅用 ORFS 固定的 SKY130 HD Liberty timing asset；当前 SKY130 techmap library 缺失导致 Stage B mapped-BLIF 与 reference BLIF 的 ABC `cec` 不可达（CEC unavailable），已记录 R31-01；combinational 路径导致 OpenSTA `slack=null` / `slack_status=MET (INF)`。这两个 limitation 在论文主表中必须明确标注，不引用 B 级证据 [F08-B] 的算法细节与数字。

## 4. 本文贡献

1. **算法贡献**：在 RSECO 重综合辅助 patch replacement 思路基础上，给出 F1-F5 失败分类驱动的 failure-aware 切割与替换原型，单轮权重调整已实现并跑通 5-case 端到端（X19 多轮设计与消融获批后升级）。
2. **流程贡献**：建立 EPFL `v2025.1` + SKY130 HD Liberty 公开组合逻辑 benchmark 上的可复现 mapping→SDC→STA 端到端流程，8-case 跑通，产物归档 `experiments/20260731_epfl_8case_stage_b/` 含 mapping + STA 完整表与 runtime breakdown。
3. **可复现工程贡献**：基于 Yosys + ABC + OpenSTA 的开源工具链完成所有映射、等价与 STA 实验；当前 limitation（`clkinv_1` cell 不兼容 / combinational 无 timing path）在文档中透明记录，与 L01 Related Work 的 25A/1B 证据等级严格一致。

## 5. 论文组织

第 2 节综述时序 ECO、Functional ECO、等价检查、B&G、ML Timing 与开源工具链 6 大主题的相关工作。第 3 节给出 FAECO 的问题输入、fanin cone、weighted s-t min-cut、F1-F5 失败分类、failure-aware refinement、tech mapping、SDC 与 OpenSTA pre-layout STA 的方法细节。第 4 节报告 Stage A 5-case 端到端与 Stage B 8-case 端到端的实验结果、限制与 ablation。第 5 节总结并展望 sequential cone、SKY130 techmap library、X19 多轮 refinement 等下一步工作。

## 6. 后续修订

- N05 方法符号表通过工程反校后，本 Introduction 与 `paper/draft/method_symbol_table.md` 同步修订符号与算法骨架。
- L01 Related Work 迁入 `paper/submission/` 后，本文的"问题背景"段重排。
- 用户最终审定 Introduction 后迁入 `paper/submission/introduction.md`。
- 任何对 B 级证据 [F08-B] 和 [B06] 的引用须保留禁止声明，禁止引用其算法细节与数字。