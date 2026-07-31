# Literature Matrix

更新时间：2026-07-19

说明：矩阵已从“按文件名分类”推进到前十批核心文献核验。逐篇方法、DOI、SHA256、可引用结论和边界见 `core_paper_notes.md`；未列为已核验的论文仍不能仅凭标题写入论文正文。

## 0. 当前核验状态

| 项 | 当前状态 | 证据 |
|---|---|---|
| 核心全文 | 已核验 25 篇 A 级证据 | 首页、摘要、方法概述、结论、页数、DOI、SHA256；SAT Sweeping 正确 PDF 仅在忽略提交的核验缓存中 |
| Timing ECO 主脉络 | 已覆盖 remapping、fixability、metal-configurable resources、negotiation/restructuring、协同 ECO、symbolic rectification、industrial physical synthesis 和 2024 IR-aware ECO | LIT-T01 至 LIT-T07、LIT-F01、LIT-F05、LIT-F07 |
| Formal/patch 主脉络 | 已覆盖 SAT/interpolation fallback、multi-error/multi-target patch、functional correspondence、minimum-cost support、resource-aware wiring cost、STP SAT-sweeping 和 2024 sequential formal scaling | LIT-F02 至 LIT-F08、LIT-V02、LIT-V03 |
| Buffering/Gate Sizing 主脉络 | 已覆盖固定树最优 buffer insertion、post-route RL sizing、物理感知离散梯度 sizing、联合 sizing/buffering、placement-aware virtual buffering 和 LLM+GRPO full-tree generation | LIT-B01 至 LIT-B06 |
| ML Timing 主脉络 | 已覆盖 timing-optimization 后结构变化容忍和 130-nm 到 7-nm 的跨节点 transfer learning | LIT-M01、LIT-M02；仅用于表示/泛化边界，不替代 STA 或可运行 baseline |
| SAT Sweeping 2006 | Cadence Labs 原始 PDF 的归档副本已完成 6 页全文与首末页核验，等级 A；文献库同名 PDF 仍错配 | source manifest 固定 DOI、归档定位、正确 PDF SHA、错配文件 SHA 和禁止再分发边界 |
| Cost-aware multi-target rectification 2018 | 正式书目、摘要和 ICCAD 2017 问题规范已核验，等级 B；OpenAlex/Semantic Scholar/Crossref、NTU 机构记录、作者站点和归档资产复核仍无合法公开全文 | source manifest 固定双 DOI、OA API 状态、受限访问状态、竞赛代价定义和禁用边界 |
| 工具链来源 | 已核对 ABC、Yosys、OpenSTA 官方资料 | 只支撑工具定位，不替代本项目运行日志 |

## 1. 与主线最相关的文献组

| 组别 | 主要作用 | 当前主线用法 |
|---|---|---|
| Timing ECO | 定义 RSECO 的直接对比对象 | Related Work 和 baseline |
| Resynthesis / Technology Remapping | 支撑“重综合辅助 patch replacement” | Method motivation |
| Equivalence Checking / SAT Sweeping | 支撑等价点搜索和 patch 合法性验证 | Method 和 correctness |
| Buffering / Gate Sizing | 传统 timing ECO baseline | Experiment baseline |
| Functional ECO / Logic Rectification | 支撑 patch generation 和失败恢复 | Related Work |
| ML for Timing / AI for EDA | 支撑 timing-aware ranking 后续扩展 | Discussion 和 future work |

## 2. Timing ECO

| 文献 | 角色 | 与本文关系 |
|---|---|---|
| `[2010] ECO Timing Optimization Using Spare Cells and Technology Remapping` | 已核验：post-mask 两阶段 spare-cell B&G + technology remapping | 说明 remapping 是 B&G 无法修复时的经典补充；工业数据不作为 FAECO 主证据 |
| `[2012] Timing ECO Optimization Using Metal-Configurable Gate-Array Spare Cells` | 已核验：aliveness + routability + timing safety 的迭代 MILP | 说明 post-mask 资源/布线约束与本文 pre-mask logic patch 的问题设置差异 |
| `[2012] Timing ECO Optimization Via Bezier Curve Smoothing and Fixability Identification` | 已核验：flexibility/path sharing/resource availability/smoothness 组成 fixability | 支撑多特征可修复性判断；当前 critical-path-only 仍只是 Stage A proxy |
| `[2012] TRECO Dynamic Technology Remapping for Timing Engineering Change Orders` | 已核验：有限 spare cells、动态 wiring cost、模板驱动迭代 remapping | 与 FAECO 局部逻辑替换最接近，但问题设置和物理约束不同 |
| `[2012] ECO Timing Optimization with Negotiation-Based Re-Routing and Logic Re-Structuring Using Spare Cells` | 已核验：多路径资源共享、congestion/history penalty、STA-guarded logic rewiring | 支撑资源冲突反馈和逻辑重构动机；不能当作 FAECO 已复现 `NEGO-ROUT` 的证据 |
| `[2019] Comprehensive Search for ECO Rectification Using Symbolic Sampling` | 已核验：对结构差异鲁棒的 rectification point 搜索与 rewiring | 支撑搜索空间和逻辑重用讨论；本质是 functional ECO |
| `[2024] IR-Aware ECO Timing Optimization Using Reinforcement Learning` | 已核验：LR + R-GCN 的 IR-aware gate-sizing ECO | 现代 physical-aware timing ECO 对照；不作为当前 Stage A 可直接运行 baseline |

## 3. Functional ECO and Logic Rectification

| 文献 | 角色 | 与本文关系 |
|---|---|---|
| `[2008] ECO-Map Technology Remapping for Post-Mask ECO Using Simulated Annealing` | post-mask remapping | 说明 spare-cell 约束场景 |
| `[2010] A Robust Functional ECO Engine by SAT Proof Minimization and Interpolation Techniques` | 已核验：FRAIG + SAT proof minimization + interpolation fallback | 支撑失败回退和 formal patch construction 的价值，不证明 FAECO F1-F5 有效 |
| `[2011] Simultaneous functional and timing ECO` | 已核验：augmented bipartite graph 联合求解 metal-only functional/timing ECO | 说明顺序拼接功能与时序修复可能失败；当前 FAECO 尚未联合求解 |
| `[2012] Multi-Patch Generation for Multi-Error Logic Rectification` | 已核验：SAT diagnosis、interpolation multi-patch、cofactor reduction 和失败后重新诊断 | 支撑 diagnosis/patch synthesis/formal/fallback 分阶段；当前 FAECO 尚未生成 Boolean multi-patch |
| `[2013] Intuitive ECO Synthesis for High Performance Circuits` | 已核验：name-preserving synthesis、functional correspondence、等价验证和 industrial physical synthesis | 支撑边界复用、逻辑扰动与物理 QoR 联动；IBM 非公开结果不能替代 FAECO 公开实验 |
| `[2016] Resource-Aware Functional ECO Patch Generation` | 已核验：gate-count estimate、nearby spare search、virtual placement、wiring-cost ranking 和 resubstitution | 证明最小 patch size 不等于最小物理代价；当前 FAECO 尚无对应 placement/resource features |
| `[2016] Unified approach for simultaneous functional and timing ECO` | 已核验：timing-to-functional transformation、technology mapping、modified Hungarian matching 和 STA refinement | 说明顺序修复可能留下违例，联合搜索需显式处理资源竞争；当前 FAECO 尚未联合求解 |
| `[2018] Efficient Computation of ECO Patch Functions` | 已核验：SAT/QBF、minimum-cost support、cube enumeration 和 timeout structural fallback | 明确 target/boundary 选择与 Boolean patch synthesis 是不同子问题；当前 replacement 尚未实现后者 |
| `[2018] Cost-Aware Patch Generation for Multi-Target Function Rectification of ECOs` | B 级核验：摘要给出 SAT/interpolation 的 sound-and-complete multi-target resource-aware patch 定位；竞赛规范区分 weighted support cost、patch size 和 runtime；多源 OA 复核仍为 closed | 支撑多目标与多代价边界；无公开全文，不能引用算法细节、复杂度和实验数字，也不能证明 FAECO 已生成 Boolean 多输出 patch |
| `[2024] Technology Remapping Approach Using Multi-Gate Reconfigurable Cells for Post-Mask Functional ECO` | multi-gate reconfigurable cells | 后续 post-mask 方向参考 |
| `[2025] DeepCell Self-Supervised Multiview Fusion for Circuit Representation Learning` | circuit representation learning | 后续学习式 ranking 参考 |

## 4. Equivalence and Logic Verification

| 文献 | 角色 | 与本文关系 |
|---|---|---|
| `[2006] SAT Sweeping with Local Observability Don't-Cares` | 已核验归档的 Cadence Labs 正确全文：AIG + simulation + SAT + local ODC + trie candidate search；文献库同名 PDF 仍错配 | 可用于方法与 cutpoint 动机；正确核验缓存不可再分发，也不能把原论文结果当作 FAECO formal 证据 |
| `[2024] A Semi-Tensor Product Based Circuit Simulation for SAT-Sweeping` | 已核验：k-LUT STP simulation、候选等价类细化、SAT calls reduction 和最终 `&cec` | 支撑 simulation/SAT/CEC 分层；不能替代 FAECO patch formal equivalence |
| `[2024] Toward Exhaustive Sequential Redundancy Removal` | 已核验：BMC/induction、反例仿真、Proof Graph 的 sequential formal scaling | 支撑 Stage B 需要独立 sequential formal 设计，不证明当前 flow 已具备该能力 |

## 5. Buffering and Gate Sizing

| 文献 | 角色 | 与本文关系 |
|---|---|---|
| `[2012] O(mn) Time Algorithm for Optimal Buffer Insertion of Nets with m Sinks` | 已核验：固定 Steiner tree、Elmore delay、离散 buffer library 下的最优 max-slack/cost 算法 | 本地文件名误标为 2006 ASP-DAC，正文实际是 2012 TCAD 扩展版；用于固定传统 baseline 假设 |
| `[2021] RL-Sizer VLSI Gate Sizing for Timing Optimization Using Deep Reinforcement Learning` | 已核验：post-route STA、three-hop GNN state、DDPG sizing、local TNS reward | 现代 gate-sizing 对照；匿名商业数据和长训练 runtime 不能作为当前可运行 baseline |
| `[2025] Learning-Driven Physically Aware Large-Scale Circuit Gate Sizing` | 已核验：multipath timing、multiscale layout、ICC2 gradient labels、STE 与 adaptive back-propagation | 强化真实 physical feature/STA/tool dependency；论文未公开实现，不能作为当前可复现 baseline |
| `[2024] AiTO Simultaneous Gate Sizing and Buffer Insertion for Timing Optimization with GNNs and RL` | 已核验：path graph、candidate buffer judging、GCN+DDPG 联合 action space、full-chip STA reward | 支撑联合 B&G 动机；10 个设计和 AiTO 实现不公开，只适合作为方法对照 |
| `[2025] Recursive Learning-Based Virtual Buffering for Analytical Global Placement` | 已核验：MLBuf recursive prediction、ERC/area/wirelength loss、OpenROAD/RePlAce 闭环和 post-route PPA | 正式发表于 MLCAD 2025且 BSD-3-Clause 开源；属于 global placement virtual buffering，不是 post-route ECO baseline |
| `[2016] A New Quadratic Formulation for Incremental Timing-Driven Placement` | incremental placement | 说明 ECO 对物理扰动的约束 |
| `[2025] BUFFALO PPA-Configurable LLM-based Buffer Tree Generation` | 已核验：T5 full-tree/coordinate generation、20M commercial-labeled pairs、INSTA-guided net/chip GRPO 和 9-design post-placement PPA | 只进入 related-work/discussion；代码、模型、数据和 commercial flow 未公开，83x 是代表性单网，且 71%/77.7% TNS 表述不一致 |
| `[2025] Addressing Continuity and Expressivity Limitations in Differentiable Physical Optimization` | differentiable gate sizing | 后续 physical optimization 参考 |

## 6. ML for Timing Prediction and Optimization

| 文献 | 角色 | 与本文关系 |
|---|---|---|
| `[2019] Machine Learning-Based Pre-Routing Timing Prediction with Reduced Pessimism` | early ML timing prediction | 背景 |
| `[2022] A Timing Engine Inspired Graph Neural Network Model for Pre-Routing Slack Prediction` | GNN timing prediction | ranking feature 未来参考 |
| `[2023] Restructure-Tolerant Timing Prediction via Multimodal Fusion` | 已核验：endpoint GNN+layout CNN、timing-optimization restructure、7-nm arrival-time prediction | 支撑结构变化会破坏局部 delay supervision；4154x 对比的是 opt+route+STA 总流与预处理+推理，不是 STA 替代或 ECO 闭环 |
| `[2024] Disentangle Align and Generalize Learning A Timing Predictor from Different Technology Nodes` | 已核验：node/design feature disentanglement、Bayesian readout、130-nm 到 7-nm transfer | 支撑跨 technology/design shift 的独立验证；仍用一个 7-nm 训练设计和商业标签流，不证明零目标数据或任意节点泛化 |
| `[2025] E2ESlack Pre-Routing Slack Prediction` | end-to-end slack prediction | 后续 timing-aware ranking 参考 |
| `[2025] DeepGate4 Circuit Representation` | circuit representation | 后续 GNN ranking 参考 |
| `[2025] DeepCircuitX RTL Dataset` | dataset | 后续 benchmark 扩展参考 |
| `[2025] ForgeEDA Multimodal Benchmark` | benchmark | 可用于公开数据讨论 |
| `[2026] NSF AI for EDA Workshop` | AI for EDA 趋势 | Introduction / motivation 可引用 |

## 7. 开源工具链来源

| 工具 | 已核验来源 | 在论文中的用途 |
|---|---|---|
| ABC | Brayton and Mishchenko, CAV 2010 | 说明 AIG synthesis/verification 能力；正式结果仍以 FAECO artifact 为准 |
| Yosys | Wolf and Glaser, Austrochip 2013 | 说明开放 Verilog synthesis/normalization 基础 |
| OpenSTA | 官方仓库与文档 | 定义后续 Liberty/SDC/SPEF STA 接口；当前未安装 |

## 8. 下一步精读优先级

| 优先级 | 文献组 | 目标 |
|---|---|---|
| P1 | 定期复核 DAC 2018 cost-aware multi-target rectification 的合法全文 | 当前正式书目、摘要和竞赛规范证据已达 B；该缺口不阻塞 25A/1B 初稿，取得全文后再核验算法、复杂度和实验数字 |
