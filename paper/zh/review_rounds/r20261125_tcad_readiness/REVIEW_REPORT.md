# FAECO 的 TCAD 投稿成熟度评估

2026-11-25。评估对象为修订后的中文 v3，原稿基线为 `c0a7266e`。本轮依据现有实验、相近工作和期刊作者指南评估稿件。 [中文 v3](../../FAECO_v3_后布局可调预算面积回收.pdf)

## 判断

**方向符合 TCAD 正规论文范围，目前建议完成关键实验后再投稿。** 已布线设计上的限时面积回收、局部布线代价和多角时序验收都是物理设计问题。稿件已有可复查的端点与计时结果，最有说服力的贡献是布线前冲突诊断节省了真实的物理验证开销。投稿前最重要的是在独立设计上复现，并量化相近基线及各模块的作用。TCAD 作者指南列出与先进方法比较不足及相关工作处理不足等可能导致初审退稿的情形。 [TCAD 范围](https://ieee-ceda.org/publications/tcad) · [TCAD 作者指南](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)

## 现有证据

| 论点 | 支持范围 | 投稿前待证 |
|---|---|---|
| 布线前诊断节省重试 | AES 上两种调度各自的首达动作、物理端点、提取寄生与时序一致。计入诊断成本，固定批次少一次详细布线、提前 72.40–84.01 s，FAECO 少两次、提前 157.95–164.38 s。 | 在独立设计上量化含诊断成本的净收益，并与同等放行规模的几何邻网方案对比。 |
| 批次调度增加时限内回收 | AES 同在线后端正反序对照，720 s 内 FAECO 回收 67.5648 µm²（原面积的 0.0580%），原顺序单门回收 22.5216 µm²。首达同一面积下限早 128.37–137.84 s，首达实际面积各为 33.7824 与 22.5216 µm²。 | 同一后端加入灵敏度排序单门，并将批宽、排序和回退处理分开。 |
| 工程折衷 | 单门贪心最早交付的单门回收 11.2608 µm²，低于共同面积下限 11.6508 µm²。在另一组配对中固定批次比 FAECO 提前 112.99–119.23 s 达到同一下限，窗内回收 33.7824 µm²。两轮反序复跑属于同一 AES 设计。 | 分别报告固定时限面积和同目标首达，给出不同预设目标下的结论及删失。 |
| 验收及适用范围 | AES 保留原 I/O，六门的最大 setup WNS 损失 0.086 ps，SS TNS 下降 192.358 ps，逐角 hold 合格，独立 DRC/天线为零，SEC 11,089/0。历史十个名义回收端点在 IO+OCV 下绝对 hold 均为负。UART 通过原约束起点 hold 资格，候选评估为零。 | 报告保护线网、电气和时序端点状态，独立记录起点不合格及零回收设计。 |

[AES 后端交叉对照](../../../../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [AES 单门对照](../../../../project_docs/evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) · [SKY130 联合视图](../../../../project_docs/evidence/sky130_joint_constraints_20261123/REPORT.md) · [UART 起点](../../../../project_docs/evidence/tcad_holdout_20261123/UART_CONTROL_RUN.md)

最接近的技术边界有两条。CoRe-ECO 用局部摆放、详细布线与单元替换联合修复既有 pin-access 违例。FAECO 在候选验证前定位由降尺寸新引入的冲突，目标量是固定时限内通过联合验收的净回收。Sizer 已展示灵敏度排序、工业布线后多角多模式时序和电气约束。当前 AES 的单门对照使用原顺序，历史十例采用灵敏度顺序且名义面积均值略高，值得将该排序放入现行在线后端实测。 [CoRe-ECO 原文](https://vlsicad.ucsd.edu/Publications/Conferences/385/c385.pdf) · [Sizer 原文](https://vlsicad.ucsd.edu/Publications/Journals/j129.pdf)

## 投稿前的优先工作

1. **先做独立设计复现。** 从已有的 ASAP7 UART 合格起点开始，再加入一个独立的 SKY130HD 非 AES 设计。固定每个设计的原始 SDC、初始候选池、物理后端、验证计费和 setup/hold 门。实验同时记录固定窗内最大合格面积和预定义目标的首达时间，也保留零回收、截尾及绝对 setup 跨零的结果。
2. **用公平对照确定贡献。** 对在线诊断比较立即重试与同放行数量的几何邻网选择。对调度比较原顺序单门、灵敏度排序单门和固定批次，并固定顺序比较批宽，再固定批宽比较反馈策略。同一设计的反序复跑用于核验墙钟趋势。若收益集中在单一设计或单一目标，正文据此限定有效场景。
3. **重建并核查英文投稿版。** 旧英文稿仍沿用早期 SKY130 口径，须同步现行证据，逐图复核机制关系和图注。本轮已在中文稿致谢声明六幅示意图的 ImageGen 使用和 Codex 文字修订。按当前 TCAD 指南，正规论文使用 IEEE 双栏，至少 10 pt，限 14 页，摘要 100–250 词，索引词 4–8 个。在参考文献前的致谢中明确生成式 AI 的使用，含工具、所涉部分及使用程度。页数以新版英文 IEEE 稿实测。 [TCAD 作者指南](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions) · [IEEE 模板](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/)
