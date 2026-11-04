# 最终方案的新颖性核对（2026-11-02）

> 问题：按 `REVISION_PLAN_2026-11-02.md` 改完之后，那个方案有没有别人已经做过？
> 方法：外部检索（2026-11-02），只读摘要与正文片段。与 `LIT_POSITIONING_2026-11-02.md` 不重复的部分才记在这里。

---

## 0 先明确"最终方案"是哪三条

改完之后的方案由三层组成，必须分开核对，因为它们的新颖性完全不同：

| 层 | 内容 | 在本方案里的角色 |
|---|---|---|
| **L1** | 量化"早期/预布局档"与"最终 sign-off"之间的 gap | 立论的**动机** |
| **L2** | 用 OpenROAD `repair_timing` 做同视图外部基线，量化差距 | **证据强度**的关键 |
| **L3** | 把阴性结果（五个方向全撞线）写成"动作空间已穷尽"的正面证据 | **认知增量**的来源 |

---

## 1 L1 已被人做过，而且不止一次 —— 这是最危险的一层

| 工作 | 原话 | 做了什么 |
|---|---|---|
| Reimann, Sze, Reis（Integration 52:347–354, 2016） | "the advantages in the quality of results provided by those more sophisticated algorithms are usually **offset by the error range of the timing model**" | 定性陈述 |
| **Liu et al.（IEEE TCAD 44(5):1942–1953, 2025；DOI 10.1109/TCAD.2024.3506216）** | "**there is no consistency guarantee between early stage metrics and sign-off timing performance**"；正文另写早期指标"have a **considerable gap** to the accurate sign-off timing metrics" | **承认 gap，然后用深度学习绕过去**（TSteiner，直接对齐 sign-off） |
| EDA-Schema-V2（arXiv 2026） | "slack-based metrics cluster near zero with weak correlation in early design stages"；"arrival time exhibits moderate correlation **beginning at placement**" | 用 7780 实例量化相关性 |

**结论**：L1 作为"命题"没有任何新颖性。TCAD 2025 那篇的摘要第一段就把这件事当已知前提写出来了。

**唯一还剩的空间**是**量化的粒度**：上述工作给的是**相关性系数**或**百分比**（工业界口径是 WLM 精度 ±50%、差 10–30%），我们要给的是 **ns 级绝对量 + 逐电路可分辨判定带（0.0246–0.0847 ns）**。这个粒度我没找到先例，但它是"表述方式"的新，不是"发现"的新。

---

## 2 L2 是标准做法，不是新颖点 —— 但这是好消息

**BIGX（ICCAD 2025，"GPU Acceleration for Versatile Buffer Insertion"）** 的对照臂里第四项就是：

> "(4) **the `repair_timing` command in OpenROAD**, which applies both buffering and sizing for setup violation repair"

它还给了两个我们正在用的关键设定：

- sizing 的覆盖是 **top 200 worst-slack paths**，每轮迭代都调，共 15 轮；
- "Buffering only" 流"exhibit **diminishing improvements**"——与我们观测到的边际递减同形。

**判读**：把 OpenROAD `repair_timing` 当基线**是社区认可的写法**，我们的 L2 因此站得住。但同时说明 **L2 不提供任何新颖性**，它只是"把该做的事做了"。

⇒ 之前判断"不补外部基线就一定被拒"仍然成立；但不能反过来指望它加分。

---

## 3 L3 有先例 —— 说明期刊收，但也说明我们不是第一个

| 工作 | 与我们的相似处 |
|---|---|
| **"Enhancing sensitivity-based power reduction for an industry IC design context"**（Integration，PII S0167926018306357） | 明确做"**gap 研究**"：研究学术 sizer 与工业生产用例的差距，并断言"**simplified constraints in contest benchmarks can potentially drive academic sizers in wrong directions**"——即负结果被当成正面结论 |
| **Involution Tool**（Integration 76:87–98, 2021） | 正文写负结果："对 NAND 电路，任何模型并不显著更好" |
| AiTO（Integration，PII S0167926024000750） | 10 个真实设计（28/110 nm），对打 OpenROAD 与 Innovus——同刊的规模门槛 |

**判读**：L3 这种写法在该刊**有先例、被接受**；但它已经有人做过一次"学术方法被基准误导"的版本。我们如果只写"我们也发现了负结果"，会显得重复。

---

## 4 分层判定表

| 层 | 有没有人做过 | 我们能主张的新颖性 | 强度 |
|---|---|---|---|
| L1 命题 | **有，多次（2016 / 2025 TCAD / 2026 数据集）** | 只在新**量化粒度**（ns 级绝对量 + 逐电路判定带） | 弱 |
| L2 OpenROAD 基线 | **有，是标准做法（BIGX 2025 等）** | 无 | 零（但是必需项） |
| L3 负结果当证据 | **有（Integration 2018 的 gap 研究）** | 我们的负结果**更系统**（五个方向、逐一预注册判据、四条止损线） | 中 |
| **"可确认性"判据** | **未找到先例** | 用同网表重跑噪声底（n=8，中位 0.01 ns）+ 逐电路判定带，把"改善"分成可确认/不可确认 | 中，但偏方法学 |
| **"搜索覆盖"当自变量** | **未找到先例**（"如何选门"有人做，MDPI *Technologies* 8(2):25, 2020 用 criticality 剪枝只为省算力；"**选多少门才够、不够的代价多大**"没人定量） | `max_instances` 受控实验 + 外部基线给出代价上界 | 中，且是我们独有 |

**综合**：整体方案**不是全新的**。每一块单独都能被审稿人指到一篇已有工作；空位只剩"可确认性 + 覆盖代价"这两点的**组合**。

---

## 5 一个更严重的问题：L1 与新的基线结果互相矛盾

上一轮拿到的事实：OpenROAD 同视图下 8 例合计 **2.3286 ns**，我们 **1.2900 ns**，比值 **1.81×**；弱例差 5.49×（s713）、9.66×（s820）。

这直接破坏了"边界论文"的诚实性：

- 如果**扩覆盖后接近 OpenROAD** ⇒ 说明"上界"其实是"我们搜索范围的上界"，写"预布局档的可确认收益上界"就是**把实现缺陷包装成领域结论**；
- 如果**扩覆盖后仍差很多** ⇒ 才能写边界，但那时 L1 又撞上 TCAD 2025 已经说过的话。

**两条分支都不利。** 这是"最终方案新颖性"问题背后真正的风险——不是"有人做过"，而是"**我们的立论依赖于一个还没跑的实验**"。

---

## 6 结论

1. **L1 已被做过且被 TCAD 2025 写进摘要**，我们不能把它当贡献。
2. **L2 是必需项但不加分**。
3. **L3 有 Integration 先例**，可以写，但要有"更系统"的差异。
4. **真正的空位只有两个，且都偏方法学**：可确认性判定带、搜索覆盖代价的受控量化。
5. **在跑完"扩覆盖"实验之前，不该动笔**——它决定我们是"方法论文"（撞 BIGX/Du）还是"边界论文"（撞 TCAD 2025），而这两条现在都堵着。

**建议顺序**：先跑扩覆盖（`max_instances` 提到全电路量级，8 例，约 40 分钟）→ 看与 OpenROAD 的比值落点 → 再定写哪一类 → 最后才改论文。

---

## 7 参考（均于 2026-11-02 检索）

- Reimann, Sze, Reis. Integration, the VLSI Journal 52:347–354, 2016. DOI 10.1016/j.vlsi.2015.09.001
- Liu, Wang, Liu, Lin, Yu, Wong. "Sign-Off Timing Considerations via Concurrent Routing Topology Optimization." IEEE TCAD 44(5):1942–1953, 2025. DOI 10.1109/TCAD.2024.3506216
- "GPU Acceleration for Versatile Buffer Insertion"（BIGX）. ICCAD 2025.
- Du, Guo, Lin, Wang, Huang. "Fusion of Global Placement and Gate Sizing with Differentiable Optimization." ICCAD 2024.
- "Enhancing sensitivity-based power reduction for an industry IC design context." Integration, the VLSI Journal. PII S0167926018306357
- AiTO. Integration, the VLSI Journal. PII S0167926024000750
- "Gate Sizing Methodology with a Novel Accurate Metric to Improve Circuit Timing Performance under Process Variations." Technologies 8(2):25, 2020.
- EDA-Schema-V2（arXiv 2026）；EDALearn
- Involution Tool. Integration 76:87–98, 2021
