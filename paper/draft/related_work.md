# FAECO Related Work 初稿（Draft 1）

更新时间：2026-07-31

来源：`docs/literature/literature_matrix.md` 25A/1B 已核验证据 + `docs/literature/core_paper_notes.md` 逐篇方法笔记。本初稿尚未经用户最终审定，结构和措辞仅作为 N05 方法修订前置输入。

## 1. Timing ECO 与重综合辅助修复

[T01] Ho 等 (2010, TCAD) 在动态 spare-cell wiring cost 下分两阶段做 B&G 与 technology remapping；[T02] Ho 等 (2012, TCAD) 进一步引入代表性模板的迭代 remapping，在有限 spare cells 下按动态 wiring cost 修复违例路径；[T03] Kravets 等 (2019, DAC) 用 symbolic sampling 搜索 rectification point 并通过结构无关 rewiring 重用逻辑。[T04] Chen 等 (2012, TCAD) 通过 Bezier curve fitability 建模 fixability，给出 timing path 是否可修复的多特征判断；[T05] Chen 等 (2012, TCAD) 引入金属可配 spare cell 与 MILP 优化解决 post-mask 资源/布线约束。

本文 FAECO 的切入点是**局部重综合 patch replacement**：当 fixed-weight cut 失败、patch size 过大或 timing 收益不足时，由 failure-aware refinement 重新调整切分和替换方向。与 [T01]/[T02] 的差异在于：FAECO 不依赖 spare-cell 与 metal-only 约束，而是把新综合网表当作时序友好的 patch 候选移植回原网表；与 [T03] 的差异在于：FAECO 当前不解决 functional ECO，但把"搜索对结构差异鲁棒"作为 failure-aware 重切割的设计动机；与 [T05] 的差异在于：FAECO 在公开 EPFL combinational benchmark 上验证，绕开工业设计与物理约束。

[T06] Wang 等 (2012, TCAD) 与 [T07] 王等 (2016) 通过 negotiation-based re-routing + 逻辑重构处理资源冲突，支撑"权重调整可读取资源与历史代价"的设计直觉；但当前 FAECO ranking 尚未引入 congestion / history penalty 类特征，仅在 timing gain + patch size + boundary + verification cost 上做确定性评分。

## 2. Functional ECO 与逻辑修复

[F01] Ho 等 (2008, ISPD) 通过 simulated annealing + technology remapping 处理 post-mask functional ECO；[F02] Jiang 等 (2010, ICCAD) 用 FRAIG + SAT proof minimization + interpolation fallback 构造等价 patch；[F03] 林等 (2011, ICCAD) 提出 augmented bipartite graph 联合求解 metal-only functional 与 timing ECO；[F04] 林等 (2012, ICCAD) 通过 SAT diagnosis + interpolation 多 patch + cofactor reduction + 失败回退生成 multi-error rectification；[F05] 李等 (2013, ICCAD) 通过 name-preserving synthesis + functional correspondence + 等价验证支持工业 physical synthesis；[F06] 蒋等 (2016, TCAD) 给出 gate-count estimate + nearby spare search + virtual placement + wiring-cost ranking；[F07] 罗等 (2016, ICCAD) 提出 timing-to-functional transformation + tech mapping + 改进 Hungarian matching + STA refinement 顺序修复；[F08] 卓等 (2018, DAC) 通过 SAT/QBF + minimum-cost support + cube enumeration + 超时结构回退生成 patch function；[F08-B] Chen 等 (2018, DAC) 用 SAT/interpolation 做 sound-and-complete multi-target resource-aware patch 定位，按 weighted support cost、patch size、runtime 区分代价维度，**仅 B 级**（OpenAlex、NTU、作者站点、IA archive 多源复核仍无合法公开全文）。

本文 FAECO 与 [F02]/[F04]/[F08] 的差异在于：FAECO 不依赖 SAT proof minimization / interpolation / cube enumeration 来构造 patch function，当前 Stage A 仅给出 cone-level 内部表示的 replacement 草案 (G18)，未生成 Boolean patch；与 [F03]/[F07] 的差异在于：FAECO 没有联合 functional+timing 求解的图模型，failure-aware refinement 只在 timing 收益层面触发；与 [F06] 的差异在于：FAECO ranking 暂未引入 placement/wiring cost，只能给出 patch size + boundary 复杂度上限；与 [F08] 的差异在于：FAECO 不做 multi-target Boolean rectification，[F08] 的 B 级证据也禁止 FAECO 直接引用其算法细节、复杂度或实验数字。

## 3. 等价检查与逻辑验证

[V01] Mishchenko 等 (2006, DAC) 在 AIG 上提出 SAT sweeping with local observability don't-cares 与 trie candidate search（正确 PDF 来自 Cadence Labs 原始链接的 Common Crawl 归档副本，仅在忽略提交的本机核验缓存中保留，文献库同名 PDF 仍错配，禁止再分发）；[V02] 仲等 (2024, TCAD) 把 k-LUT 仿真 + STP 表示用于 SAT-sweeping 的 candidate refinement，最终以 `&cec` 终止；[V03] 王等 (2024, TCAD) 用 BMC/induction + 反例仿真 + Proof Graph 把 sequential redundancy 推向大规模。

FAECO Stage B 当前 CEC 实现 ([G19] + `src/rseco/yosys_abc.py` + `check_mapped_blif_equivalence`) 把"原始 Yosys-normalized BLIF vs mapped BLIF"作为形式回验基础，并已知 SKY130 Liberty 不含 `sky130_fd_sc_hd__clkinv_1` 导致 ABC `cec` 当前不可达，已记录 limitation。[V02] 提示 FAECO 可以用 STP-driven candidate refinement 减少 SAT calls；[V03] 提示 FAECO 当前的 combinational CEC 不能扩展到 sequential ECO，方法重写需要独立的 sequential formal 引擎。

## 4. 缓冲器插入与门尺寸调整（B&G baseline）

[B01] 梁等 (2012, TCAD) 在固定 Steiner tree + Elmore delay + 离散 buffer library 下证明 O(mn) 时间最优 max-slack/cost 算法（本地文件名误标为 2006 ASP-DAC，正文实际是 2012 TCAD 扩展版）；[B02] 刘等 (2021, ICCAD) 在 post-route STA 上用 three-hop GNN + DDPG 学习 gate sizing；[B03] 黄等 (2025) 在 multipath timing + multiscale layout + ICC2 gradient labels 上做 physically-aware discrete gradient sizing；[B04] 陈等 (2024, DAC) 用 GCN + DDPG 联合 sizing 与 buffer insertion；[B05] 李等 (2025, MLCAD) 用 recursive virtual buffering 接入 OpenROAD/RePlAce，但属于 global placement 阶段而非 post-route ECO；[B06] 张等 (2025, ICCAD) 用 T5 full-tree/coordinate 生成 + 20M 商业标注对 + INSTA-guided net/chip GRPO 在 9-design ASAP7 流上做 LLM+RL 的缓冲树生成（83x 是代表性单网，71%/77.7% 表述不一致，且代码/模型/数据/commercial flow 未公开）。

FAECO 当前不重做 B&G 的求解器；B&G 作为 baseline 体现在 `baseline_protocol.md` (E06) 中，但 Stage A 尚未把 [B01] 的最优 buffer insertion 作为对照基线（缺最优实现且未集成到 flow）。FAECO 的 patch replacement 与 B&G 的关系是：failure-aware refinement 在 F3（patch size 过大）和 F4（时序收益不足）失败时，可由 buffer insertion 或 gate sizing 在 patch boundary 内部进行再修复；这与 [B02]/[B03]/[B04] 的物理感知 + RL/DL 路径不同，FAECO 当前只用确定性方法。[B05]/[B06] 仅进入 Related Work / Discussion，不进入 baseline：[B05] 是 placement 阶段，[B06] 未公开实现且数字口径不一致。

## 5. 时序机器学习（ranking feature 与泛化边界）

[M01] 张等 (2023, DAC) 用 endpoint GNN + layout CNN 处理 timing-optimization 之后的结构变化容忍问题；[M02] 张等 (2024, DAC) 用 node/design feature disentanglement + Bayesian readout 在 130-nm 到 7-nm 之间做 timing predictor 迁移学习。

FAECO 当前的 timing-aware patch ranking (E03 + G13) 是**确定性 scoring**，不依赖 GNN/RL。[M01] 提示 FAECO 的 ranking feature 不能只取自 timing-optimization 之前的 delay supervision；[M02] 提示跨 technology/design 迁移需要独立验证，且当前 Stage A 仅在 1 个 PDK + 1 个 corner 上验证，不能直接对照 [M02] 的跨节点实验。

## 6. 开源工具链来源

[Tool-1] ABC（Brayton and Mishchenko, CAV 2010）作为 AIG synthesis/verification 引擎；[Tool-2] Yosys（Wolf and Glaser, Austrochip 2013）作为开放 Verilog synthesis/normalization 基础；[Tool-3] OpenSTA（OpenROAD 项目）作为 Liberty/SDC/SPEF STA 接口。三者均为本文 FAECO Stage A 与 Stage B 的实际工具链。

工具链来源用于说明 FAECO 的方法定位与可复现性边界，不替代本项目运行日志。所有 ABC/Yosys/OpenSTA 的实验数字均以本文实验产物为准，不沿用任何论文中报告的数字。

## 7. 与 FAECO 关系小结

| 文献组 | 与 FAECO 的主要差异 / 边界 |
|---|---|
| Timing ECO [T01-T07] | FAECO 不需要 spare cell / metal-only 约束，用公开 combinational benchmark；与 [T02]/[T06] 设计直觉相似但物理约束不同；不与 [T01]/[T05] 工业数据直接比较 |
| Functional ECO [F01-F08] | FAECO 不做 Boolean patch synthesis，不做 multi-target rectification，不做联合 functional+timing 求解；当前只有 cone-level 内部表示的 replacement 草案 |
| Equivalence [V01-V03] | FAECO 当前 combinational CEC 受 SKY130 Liberty cell 兼容限制；sequential CEC 需要独立引擎 |
| B&G [B01-B06] | FAECO 当前 Stage A 未实现 buffer insertion 求解器；B02/B03/B04/B06 不可复现，列为对照与未来工作 |
| ML [M01-M02] | FAECO 当前 ranking 是确定性 scoring；ML 仅作为 ranking feature / 泛化边界 |
| 工具链 [Tool-1/2/3] | FAECO Stage A + Stage B 全部用 ABC/Yosys/OpenSTA，结果数字以本项目为准 |

## 8. 证据等级与禁止声明

下列文献在本节中**只能作为方法综述、对比与边界标注使用**，禁止引用其算法细节、复杂度结果或实验数字：

- [F08-B] Chen 等 (2018, DAC) cost-aware multi-target rectification：**B 级**，OpenAlex/Semantic Scholar/Crossref、NTU 机构记录、作者站点和 IA archive 多源复核仍无合法公开全文，本地不可得。
- [B06] 张等 (2025, ICCAD) BUFFALO：B 级（仅摘要与 LLM+GRPO 思路），代码/模型/数据/commercial flow 未公开，83x 是代表性单网且 71%/77.7% TNS 表述不一致，禁止引用其训练规模、对比数字和 post-placement PPA 指标。

下列文献在本节中**只能作为方法动机，禁止作为结果对比**：

- [T01]/[T02]/[T05]/[F01]/[F03]/[F07] 工业数据未在 FAECO 复现，禁止用其报告的违例修复率或 runtime 对比 FAECO 当前 Stage A/B 结果。
- [B02]/[B03]/[B04]/[B05]/[M01]/[M02] 实验细节或工业数据未公开，禁止引用具体训练规模、对照曲线或商业结果。

## 9. 后续修订

- 当 L01 / N05 / N08 拿到用户最终审定意见后，将本初稿迁入 `paper/submission/related_work.md` 并按论文主风格 (引言、实验、related work 平衡) 重新组织。
- 若后续补充 [F08] 合法公开全文的获取渠道，可升级 [F08-B] 为 A 级。
- 若后续 B&G baseline 被实际接入 Stage A，可在本节追加 buffer insertion baseline 段落。