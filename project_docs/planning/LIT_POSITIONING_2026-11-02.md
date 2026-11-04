# 文献定位与工作价值评估（2026-11-02）

> 目的：把 FAECO 放到真实文献坐标里，判断它值多少、位置在哪、风险是什么。
> 方法：外部检索（2026-11-02），只读摘要与正文片段，未获取全文；所有引用标明出处。

---

## 1 文献地图：这条线上有谁

| 工作 | 阶段 | 方法 | 基准 | 报告效果 | 对比基线 |
|---|---|---|---|---|---|
| **ECOSight**（Frontiers of Computer Science, 2026）| 布局后（读 placement+LEF） | GNN 时序代理（R²=0.9998）+ 梯度解释得敏感度图 + 规则分配 | ITC'99 b12/b14/b15，500 MHz | **TNSRE 0.888**（vs Tool A 0.274 / Tool B 0.273）；运行时间 −56.9% / −53.1% | **两家商业 P&R 的 ECO 引擎** |
| **Du et al.**（ICCAD 2024）| **融合**全局布局与 sizing | 可微目标 + GPU | OpenROAD 基准 | **TNS +77.1%、WNS +43.5%**、漏电 −1% | OpenROAD |
| **IMPRoVED**（TODAES 2023）| 布局 → 预测布线后 | RandomForest 预测 post-route slack | 5 个 ITC-99 + 4 个 Intel 工业块（10 nm，14–23 万 µm²） | 预测精度（对比 SOTA 预测） | 预测类方法 |
| **Stage-based Path Delay Prediction**（IEEE 2023）| ECO 生成 | ML 预测 gate+wire delay | — | 误差 2.61 ps / 0.35% | — |
| **Reimann, Sze, Reis**（Integration, VLSI J. 52:347–354, 2016；DOI 10.1016/j.vlsi.2015.09.001）| 布局后 + CTS 后 | 拉格朗日松弛 + 排序减少 timer 调用 | 工业微处理器块 | 漏电 −10.8%（最高 18.2%），timer 调用 10× 加速 | 现有算法 |
| **FAECO（本工作）** | **预布局（理想线网，无寄生）** | 区域构造 + 调度，无 ML | 8 ISCAS89 + 19 ITC-99 + PicoRV32 + b18/b19 | WNS 0.16 ns（占违例 15.4%）；省 7.8–19% STA | **内部 9 臂对照，无外部** |

---

## 2 三处必须直面的对照

### 2.1 我们的核心洞察，2016 年已被定性写出

Reimann 等人在 Integration 期刊上，解释"为什么工业流程早期只用逐门启发式"时列了四条理由，其中第 2 条原文：

> "During early stages of physical synthesis flows, it is very common to use simple timing models.
> Therefore, **the advantages in the quality of results provided by those more sophisticated algorithms
> are usually offset by the error range of the timing model used.**"

译：早期阶段常用简单时序模型，因此**更复杂算法带来的质量优势通常被时序模型的误差范围抵消**。

这句话与我们的"动作粒度 < 测量分辨率"是同一件事。
⇒ **我们的核心命题不是新的**，2016 年已在期刊上作为工程常识陈述。

### 2.2 我们这条路线，2024 年已被判"应该合并而非独立"

Du 等人（ICCAD 2024）开篇即写：

> "Traditional design flows typically treat gate sizing as a separate step... this approach not only
> undermines the optimization efforts of earlier stages like placement, but also **restricts the
> exploration space for gate sizing**."

而且他们用"融合布局与 sizing"拿到 **WNS +43.5%**——是我们 15.4% 的约 **2.8 倍**。

⇒ 我们做的正是"把 sizing 当作独立步骤"，而这恰是该文主张要放弃的做法。

### 2.3 效果量级与对比方式差一个档

- 效果：我们 0.16 ns（15.4%）；Du 2024 是 43.5%；ECOSight 是修复率 0.888。
- 对比：ECOSight **直接打商业工具**；Du **打 OpenROAD**；我们打**自己的 9 个臂**。
- 基准：ECOSight 用 b12/b14/b15；IMPRoVED 有 4 个 Intel 工业块；我们用 8 个 ISCAS89（最小 s27 仅十输入一输出）。

⇒ 按"方法论文"的标准，这三项（量级、对比、规模）**都不过**。

---

## 3 那我们还有什么？——三个真实但狭窄的位置

### 位置 A：唯一把"预布局独立优化的上限"测到 ns 级的工作（可信度最高）

Reimann 说"优势被模型误差抵消"，但**没有给误差的量级**。
工业界的口径是"WLM 精度 ±50%""预布局与布线后差 10–30%""pre-synthesis 时序误差可达 60%"——
这些是**百分比**，不是**可分辨的绝对量**。

我们给的是：
- 逐电路判定带 **0.024558–0.08474 ns**（由独立标签族 2σ 估得，非取自被评数据）
- 候选改善中位 **2 个报告量子**（0.01 ns/量子），判定带约 **5 个量子**
- 候选池 1393 个的构成：B 700（命中 0.3%）、R 464（1.3%）、G 198（15%）、JOINT 19（0%）
- **B 类与 JOINT 在理想档超带数为 0**
- 三级漏斗：理想档超带者到布线后仍超带 11/16（基族 7/7、扩面族 4/9）

**这是别人没有的**：把"不靠谱"从形容词变成可测的纳秒数。

### 位置 B：给"shift-left 该往哪边移"提供反向证据

Du 2024 主张"往左融合"。我们的数据说明的是**另一件事**：
在**完全不看物理**的前提下，收益上限本来就低，且卡在候选池而非搜索算法。
⇒ 这两者不矛盾，反而互补：**我们是"只往左、不引入物理信息"这条路的负面对照组**。

引用它做对照，比回避它有利。

### 位置 C：全套 SEC + 跨四族复现

- 72 次受控运行全部有最终 SEC，非空已证明点、0 未证明
- b17 完整模型证明 **12879/0**
- 四族 31 对物理四数，符号检验 p=2.98×10⁻⁸
- 三档物理标签 3175 行

这在同类论文里算扎实的一档（很多只做 STA 不做形式等价）。

---

## 4 客观评分（按顶刊审稿人视角）

| 维度 | 评价 | 说明 |
|---|---|---|
| 新颖性 | **弱** | 核心命题 2016 年已被定性提出；路线方向被 2024 年工作判为应放弃 |
| 严谨性 | **强** | 判定带独立估计、SEC 全套、多族复现、阴性结果如实报告 |
| 效果量级 | **弱** | 15.4%，不到同类最强工作的 1/2.8 |
| 可比性 | **不合格** | 无外部基线（这是硬伤，非偏好问题） |
| 规模 | **弱** | 机制归因只在 8 个小电路；大设计改善塌缩（b18 0.07 ns） |
| 认知增量 | **中** | 把定性判断量化；但没有改变领域对该问题的看法 |

**综合：按"方法论文"投顶刊，会被拒，且理由充分。按"分析/边界论文"，可投但要选对期刊与写法，且必须补外部基线。**

---

## 5 风险清单（审稿人会怎么打）

1. **"Reimann et al. 2016 已经指出算法优势被模型误差抵消，你的贡献是什么？"**
   → 唯一可答：我们给出误差的量级与可分辨性判据，并证明候选池而非搜索是瓶颈。
2. **"Du et al. 2024 已证明应融合布局与 sizing，为何还要研究独立预布局优化？"**
   → 唯一可答：作为负面对照，量化"不引入物理信息"的上界，为 shift-left 的**方向选择**提供依据。
3. **"与商业 ECO 引擎相比如何？"**
   → **目前无解**。必须做。
4. **"8 个 ISCAS89 太小。"**
   → 部分可答（有 ITC-99/PicoRV32/b18/b19），但机制归因仍只在 8 个小电路。
5. **"0.16 ns 的意义？"**
   → 可答：报告的是违例深度收窄 15.4%，不是收敛；但说服力有限。

---

## 6 结论：这份工作的真实价值

**它不是一篇好方法论文，但它可能是一篇有用的"边界论文"。**

- **不要**继续往"我们的方法更好"方向加实验——今天五个方向（新动作、组合枚举、判据加带、决策规则、预算分配）全部撞线，且文献已给出独立解释。
- **要**把定位收窄成一句话：**"在完全不使用物理信息的预布局档上，时序 ECO 的可确认收益上限是多少、瓶颈在候选池还是搜索算法。"**
  这个问题目前没有公开的定量答案，而我们有全套数据。

**位置的价值取决于一件事**：能不能把"我们是唯一测出这个上限的"讲清楚。
如果只是重复"预布局不准"，那就没有价值——因为 2016 年就有人说过了。
如果能把"不准到什么程度、卡在哪一环、因此 shift-left 应该往哪边移"讲成一条可复核的链，那就有价值。

**必须补的一项**：外部基线（同信息条件下跑一个公开流程）。
不补，第 3 条风险无法回答，任何期刊都会卡住。

---

## 7 参考（均于 2026-11-02 检索）

1. T. Reimann, C. C. N. Sze, R. Reis. *Challenges of cell selection algorithms in industrial high performance microprocessor designs.* Integration, the VLSI Journal, 52:347–354, 2016. DOI 10.1016/j.vlsi.2015.09.001
2. T. J. Reimann, C. C. N. Sze, R. Reis. *Cell Selection for High-Performance Designs in an Industrial Design Flow.* ISPD 2016, 65–72. DOI 10.1145/2872334.2872358
3. Y. Du, Z. Guo, Y. Lin, R. Wang, R. Huang. *Fusion of Global Placement and Gate Sizing with Differentiable Optimization.* ICCAD 2024.
4. *ECOSight: an explainable graph AI tool for automated decision-making in timing ECO.* Frontiers of Computer Science. DOI 10.1007/s11704-026-51891-6
5. *IMPRoVED: Integrated Method to Predict PostRouting setup Violations in Early Design Stages.* ACM TODAES. DOI 10.1145/3572546
6. *Automatic Timing ECO Using Stage-based Path Delay Prediction.* IEEE, 2023（文献号 9842155）。

> 说明：以上均只读摘要/正文片段（检索页提供的摘录），**未获取全文**，未核对图表与实验细节；
> 引用其结论时仅限摘要明确陈述的内容。
