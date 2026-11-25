# FAECO 的文献对照与投稿判断

2026-11-25。以当前可核的布线后证据为依据，与相近工作的目标、验证成本和实验指标对照。资料来自本次定向检索的论文原文与官方代码仓库。

## 与已有工作的关系

| 工作 | 原文的目标与指标 | 对 FAECO 的意义 |
|---|---|---|
| Lee 与 Gupta，增量门尺寸调整 | 为工艺变化后的时序违例做 ECO。相对商用工具平均减少 89% 的扰动面积。 | 已有后期换门和布局保护先例。该文衡量改动所触及的面积，FAECO 衡量最终净标准单元面积。[原文](https://nanocad.ee.ucla.edu/wp-content/papercite-data/pdf/j24.pdf) |
| Fatemi 等，Sizer | 工业多角多模式布线后功耗回收，报告等运行时间与等时序质量的对照。工业 140 nm 案例报告约 7% 漏电节省。 | 等时间和多角约束已有先例。可借鉴其比较方法。原文指向 [TritonSizer](https://github.com/The-OpenROAD-Project/TritonSizer)，仓库已归档，可先试公开实现与共同物理后端的兼容性。[原文 §6](https://vlsicad.ucsd.edu/Publications/Journals/j129.pdf) |
| Cheng 等，DAGSizer | 使用时序图学习同占位的阈值电压与沟道长度替换，评估漏电回收和时序，并核算特征提取和推理时间。 | 同占位替换可保持布线。FAECO 研究会改变引脚位置、需要重布线的降面积替换，优化重点是节约重复物理验证。[原文](https://vlsicad.ucsd.edu/Publications/Journals/j140.pdf) |
| Mangiras 与 Dimitrakopoulos，增量 LR | 使用同一个 LR sizer 比较不同初始化，评估 WNS、TNS、漏电和运行时间。末段重布线效应用随机 ±10% RC 扰动模拟，多角采用由典型库派生的模型。 | 同优化器的消融说明为何要固定 FAECO 的排序、批宽和后端逐项对照。FAECO 已有真实重布线、实际三角库与原 hold 门的证据。项目内简化的冻结寄生 LR 试验对应另一实现。[原文 §4](https://www.mdpi.com/2227-7080/9/4/92) |
| CoRe-ECO、SLO-ECO、Adaptive Pin Pattern Modification | 联合调整摆放、布线或引脚图形，处理已存在的引脚访问和 DRC 难题。CoRe-ECO 平均消除 58.6% 的剩余违规。SLO-ECO 平均降低 DRC 与 SLO 违规 45.14%，提供公开实现。 | 局部冲突驱动的物理调整有先例。FAECO 用降面积候选现场暴露的冲突识别需提前放行的邻网，并量化它对限时合格面积的影响。相近研究的违规率或局部模块提速与 FAECO 采用不同的性能指标。[CoRe-ECO](https://vlsicad.ucsd.edu/Publications/Conferences/385/c385.pdf) · [SLO-ECO](https://vlsicad.ucsd.edu/Publications/Conferences/406/c406.pdf) · [开源实现](https://github.com/ABKGroup/SLO-ECO) · [ICCAD 2025 引脚访问研究](https://snu.elsevierpure.com/en/publications/adaptive-pin-pattern-modification-on-standard-cells-towards-eco-r/) |
| ICCAD 2025 Problem C | 联合门尺寸、缓冲和搬移，要求可重放 ECO，统一计量时序、功耗、线长、位移与运行时间。 | 为统一评估与记录变更提供参考。竞赛起点是增量布局，FAECO 当前主结果从已布线参考出发，经详细重布线和寄生重提取验收。[竞赛论文](https://research.nvidia.com/labs/electronic-design-automation/papers/yichen_iccad25_contest.pdf) |

## 当前效果

| 证据 | 可写结论 | 证据范围 |
|---|---|---|
| SKY130HD AES，后端 × 调度，同机换序 | 每种调度内改用在线冲突诊断后，达到同一个验收端点，固定三门省 72–84 秒（16%–19%），FAECO 省 158–164 秒（约 25%）。首达前完整 DRT／RCX 分别从 3 次降为 2 次、5 次降为 3 次。已计现场诊断。 | 当前最强的机制证据。在线后端下，FAECO 在 720 秒内验收 67.5648 µm²（约占初始功能面积 0.058%），固定验收 33.7824 µm²，但固定早约 113–119 秒到达该较小面积。该交叉实验同时有 6 次逻辑请求上限，且只在一个设计验证同端点提速。[原件](../tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) |
| ASAP7 UART，720 秒正反序 | FAECO 最高 0.83106 µm²（约 1.052%），强单门 0.77274 µm²，固定批次 0.33534 µm²。FAECO 较强单门多 7.55%，同实收 0.77274 µm² 早 104–106 秒。 | 三个小阈值均由单门先到。UART 已用于开发，且该实验未统一各法的起始排序，支持报告整体策略的差距。反馈的独立增益仍待测。[原件](../tcad_wallclock_schedule_20261125/REPORT.md) |
| SKY130HD riscv32i，720 秒正反序、共享灵敏度排序 | 固定和 FAECO 都回收 75.072 µm²（约 0.1051%），单门为 57.5552 µm²（约 0.0806%）。到相同 48.7968 µm²，批处理早 297–304 秒。 | 固定和 FAECO 的动作、九门物理端点及面积一致，所有同实收时间差不超过 0.67 秒，反馈没有触发。该设计已用于选择改进排序。[原件](../tcad_rank_alignment_20261125/REPORT.md) |
| SKY130HD GCD，低成本 hold 预览 | 受验的限域路由或增量寄生估计误判一对等面积候选，限域预览加实布的净耗时高于直接完整评估。时钟支路变化可迟至详细布线后段。 | 布线前诊断可用于选择重布线范围。原有保持时间和 DRC 验收仍有独立价值。[原件](../tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md) |

历史小电路对照中，FAECO 与在线单门的名义平均面积降幅分别为 2.01% 和 2.11%，使用 6–10 次评估上限及 10 ps 建立时间预算。历史 OpenROAD 原生回收和自实现冻结寄生 LR 也已实测。ASAP7 早期 AES 采用全局布线寄生估算。现代外部 sizing 方法在最新 720 秒协议下的完整对照仍待完成。[小电路基线](../postroute_strong_baselines_20261122/REPORT.md) · [历史横向证据](../cross_pdk_lr_baselines_20261123/REPORT.md)

## 论文主张和决定性实验

**可以推进中文稿。** 当前最值得作主线的改进是，对会引发局部冲突的降面积替换，在完整详细布线前根据本次候选产生的实际 DRC 标记识别需额外放行的信号网，保护其余布线并减少无效的完整物理验证。最终面积收益依据可调 setup WNS／TNS 上限、原 I/O 与 hold、独立 DRC／天线、SEC 验收后的实际端点，在同墙钟下计量。报告标准单元面积与百分比、各角 setup／hold、总运行时间与同面积首达，在可比端点一并记录功耗。

AES 同动作同端点的时间差为主张提供初步因果证据。UART 展示批处理策略的收益曲线，riscv32i 解释同榜条件下的打平。投 TCAD 前，优先让在线诊断在独立设计上接受检验，再决定动态调度是否进入核心贡献：

1. 冻结同一候选排序、批宽、起点与总时间预算。预先登记有合法面积候选的独立设计，尽量覆盖两 PDK。比较常规初布后按真实标记重试、放行规模相近的几何邻网规则、在线标记诊断。同步披露未出现可归属冲突的情形。正反序均纳入前处理、失败、路由、提取与验收时间。
2. 报告窗口内最大合格回收和共同实收面积的首达。能配同物理端点的另报省时与免去的 DRT／RCX 次数。若在线诊断较两种简单基线均无法净省时或多回收，或收益依赖放宽保护范围造成的时序变化，主张的适用条件须据实收窄。
3. 对外部工具先同门跑 OpenROAD 原生 recover_power，保留面积与功耗。对 TritonSizer 先验证库、SDC、输入转换和候选导出，成功后接共同后端，记录适配程度与额外时间。动态反馈须在实际派发分叉的独立设计上，共享排序与后端对固定三门证明净收益，方可作为单独贡献。

[接手入口](../../HANDOFF_2026-11-25.md)
