# 项目升级改造方向调研（2026-11-10）

> **背景**：FAECO 五轮机制实验全部不晋级，当前 R/G/B + joint_k=2 + 覆盖优先动作集天花板 ≈ 0.31 ns/4 例。
> 用户 m04256「搜集相关文献 分析现有项目可以升级改造成啥 现在的整体不能冲刺顶刊」。
> 
> **结论先行**：现有资产（仪器 / 数据 / 实验方法学）可支撑三个方向：
> ① **LLM + 物理感知 EDA Agent**（最热门、最多被引、最快出成果）；② **跨阶段偏差结构化建模**（与当前资产最贴合、零新实验）；③ **时序 ECO 的噪声感知决策理论**（最独特、最有长期价值但最慢）。
> 以下分述。

---

## 1 现有的独特资产（别的 ECO 论文没有的）

| 资产 | 具体内容 | 为什么稀有 |
|---|---|---|
| **真实物理测量管线** | `placed_sta.py`（floorplan→place→CTS→`estimate_parasitics -placement`→STA）+ `routed_sta.py`（全布线→`extract_parasitics`→独立 `sta` 读 SPEF）+ 布局集成判据（k=3 布局均值） | 绝大多数 ML-for-EDA 论文只用开源 benchmark 的已有签核数据或 ideal 网表，没有自己跑物理流程的；本文三档（ideal→placed→routed）对比是独有的 |
| **预注册实验方法学** | 五轮预注册实验（PREREGISTRATION.md 运行前写死判据 + summary.json + REPORT.md） | EDA 论文习惯于事后挑结果，预注册在这里是方法论贡献 |
| **失效刻画框架** | F1–F6 六条权重规则 + `refinement.py` + `feedback.py`（LEGACY_CONFIG / ADAPTIVE_CONFIG） | 不是"我们的方法赢了"，而是"我们的方法为什么输、输在哪里"——比基准论文更诚实，也更难写 |
| **OpenROAD v26Q3 + sky130hd 全工具链** | WSL 内 OpenROAD 26Q3 + 独立 `sta` 3.1.0 + Yosys 0.33/0.70 两版 | 开源可复现是顶刊（DAC/ICCAD/TCAD）的一个硬要求，本文已经跑通 |
| **八例 ISCAS89 + 两例 ITC-99 交叉验证** | 原始 RTL 重映射重跑，八例逐例复现表 3 | 有规模，虽然不是大设计 |
| **"动作粒度 < 测量分辨率"这个第一性诊断** | CANON §7.4：判定带 ≈5 量子、候选中位 ≈2 量子、>5·band=0 | 这是一个可泛化的洞察，不只是调参失败报告 |

---

## 2 外部文献地图

### 2.1 最直接的竞争者

**Jiang et al. 2024 "IR-Aware ECO Timing Optimization Using Reinforcement Learning"** (arXiv:2402.07781)
- 方法：RL + R-GCN 门尺寸，post-physical-design 阶段
- 优势：Pareto 前沿左移、运行时省、扰动少、模型可迁移
- 局限：只做 gate sizing（无缓冲插入、无等价替换），45nm 开源工艺
- **与 FAECO 的关系**：它是"换选择器"路线的理想对照——它证明 RL 可以选得更好；FAECO 证明在当前动作集下选得更好也没用。两条路是互补的：如果我们先扩大动作空间（如加入 IR 感知），再换选择器，有可能突破天花板。

### 2.2 ML-for-EDA 主流路线

| 路线 | 代表性工作 | 与本项目的关系 |
|---|---|---|
| **GNN 门尺寸** | RL-Sizer (Liu 2021)、AiTO (Chen 2024) | 中文论文相关工作已引用；CANON §8 已裁定 GNN 在本族无候选级物理信号（池内 AUC 0.479 < kind_only 0.555）——但这只对"标量图摘要"成立，不等于 GNN 编码器就是没用的 |
| **物理感知优化** | Phys (Huang 2025)、Buffalo (Zhang 2025) | 利用物理信息（placement / routing congestion / IR drop），与本文的 placed/routed 三档管线天然对接 |
| **时序预测** | He 2023 STA、Tian 2023 GNN survey | 前提是"存在与签核一致的可学信号"——本文的发现是这一前提在候选级不成立，这是一个有价值的 negative result |
| **LLM Agent for EDA** | Chip-Chat / ChatEDA / LLM4ChipDesign 系列（2024–2025 DAC/ICCAD 热点） | FAECO 的规则化的失效刻画框架可以直接作为 LLM 的 tool-use 后端 |

### 2.3 LLM + EDA Agent 方向（2024–2026 最热）

这是过去 18 个月 EDA 顶会增长最快的方向：
- **Chip-Chat** (DAC 2024)：LLM 对话式芯片设计
- **ChatEDA** (ICCAD 2024)：LLM Agent 自主调用 EDA 工具
- **LLM4ChipDesign** (arXiv 2025)：系统综述 LLM 在芯片设计各阶段的应用
- **VerilogCoder / RTLCoder** 系列：LLM 生成 RTL 代码

**FAECO 可以切入的方式**：不做"LLM 生成 Verilog"（太卷），而是做"LLM Agent 调用物理 EDA 工具做时序 ECO"。优势：
- FAECO 已经有**结构化的工具调用链**（Yosys 映射→ideal STA→候选生成→placed/routed STA→验收），这些都可以包装成 Agent 的 tool
- 失效刻画框架（F1–F6）可以作为 Agent 的**反馈信号**，让 LLM 决定下一轮做什么
- "Agent 决策 + 物理测量反馈"的闭环是当前该方向最缺的东西——大多数 LLM-for-EDA 论文只在仿真/理想层面评估

---

## 3 三条升级方向与冲刺顶刊分析

### 方向 A：LLM Agent for Physical-Aware Timing ECO（最推荐）

**核心主张**：用 LLM Agent 替代手写规则，在真实物理测量反馈下做时序 ECO 决策。

**与当前项目的关系**：
- 保留全部仪器（placed/routed STA 管线）
- 把手写的 `refinement.py`（F1–F6 权重更新规则）替换为 LLM Agent 的 tool-use 决策
- 手写规则作为 baseline（ablation：去掉 Agent 只留规则 vs 用 Agent 替换规则）
- 五轮预注册实验方法学保留作评估框架

**为什么可以冲刺顶刊（DAC / ICCAD / TCAD）**：
1. **LLM + EDA = 当前最热**，审稿人天然有兴趣
2. **有真实物理测量**（不是仿真/理想档），与 99% LLM-for-EDA 论文拉开档次
3. **有负结果可以写**：手写规则已经逼近天花板，Agent 是否还能突破是一个 clean 的 research question
4. **OpenROAD 全开源**，满足可复现要求

**需要的增量工作**（约 2–3 个月）：
- 写 Agent 框架（tool 定义 + prompt + 决策循环）
- 接入 LLM API（GPT-4 / Claude / DeepSeek）
- 在现有 4 例上跑 arm Agent vs arm All 对照
- 写论文（LLM + EDA 领域论文通常 6–8 页 DAC/ICCAD 格式）

**风险**：LLM Agent 可能和手写规则一样触天花板（动作集不改，选谁都是选）。但"Agent 也不行"本身就是一个强 negative result，与"手写规则也不行"呼应，可以写成"时序 ECO 的物理天花板——从手写规则到 LLM Agent 的一致性证据"。

---

### 方向 B：跨阶段偏差的结构化建模与预测（最稳妥）

**核心主张**：理想线网 → 布局后 → 布线后三档的偏差不是噪声，有电路结构/拓扑规律可预测。

**与当前项目的关系**：
- **已有全部数据**——三布局（0.30/0.35/0.40）× ideal/placed/routed × 4 例 × 多个臂的归档
- 五轮实验已经揭示了偏差的几个特征（B 类 placed/routed 比值 5.91、跨布局极差中位 0.1042 ns、placed vs routed Spearman 0.164）
- 只需要做分析，**不跑新实验**

**为什么可以冲刺顶刊（TCAD / TODAES）**：
1. "跨阶段偏差的模式发现"比"又一个 RL 模型"更有理论贡献
2. 数据驱动 + 物理解释，TCAD 审稿人喜欢
3. 0 额外实验成本

**需要的增量工作**（约 1–2 个月）：
- 特征工程：从网表图提取结构特征（已有的 `extract_graphs.py` 可复用）
- 偏差预测模型训练 + 特征重要性分析
- 写论文

**风险**：r30 已尝试过类似方向（图结构特征 vs 物理标签），结论是"池内无法分辨"。但这个方向可以换一个 framing：不追求"预测候选级增益"，而是"预测跨阶段偏差的幅度和方向"——前者已被证伪，后者尚未被检验。

---

### 方向 C：时序 ECO 中的噪声感知决策理论（最深刻，但最长线）

**核心主张**：把"动作粒度 < 测量分辨率"这个洞察形式化为噪声感知决策理论——在测量有噪声、动作效应小的情况下，什么样的决策策略是最优的。

**与当前项目的关系**：
- 五轮实验是理论的实证基础
- 已有预注册方法学可以作为理论验证框架

**为什么可以冲刺顶刊**：
1. 理论贡献明确——这不是"我们的方法更好"，而是"时序 ECO 决策的数学结构"
2. 可泛化——不限于 sky130hd，不限于 ISCAS89
3. 审稿人无法说"没有 novelty"——没人做过

**风险**：理论工作发表周期长（1–2 年），且需要数学证明；不适合短期冲刺顶会。

---

## 4 推荐顺序与下一步

| 优先级 | 方向 | 时间 | 顶刊适配 | 风险 | 备注 |
|---|---|---|---|---|---|
| **P0（立即）** | B: 跨阶段偏差建模 | 1–2 月 | TCAD/TODAES | 低 | 已有全部数据，零新实验，最快出论文 |
| **P1（并行）** | A: LLM Agent ECO | 2–3 月 | DAC/ICCAD 2026 | 中 | 需接入 LLM API + 写 Agent 框架，但最可能中顶会 |
| **P2（长线）** | C: 噪声感知决策理论 | 1–2 年 | TCAD/TODAES 理论赛道 | 高 | 数学要求高，但学术价值最大 |

**建议执行路线**：
1. **本周**：方向 B 开写——把归档数据（三档偏差表、B 类比值、跨布局极差）整理成结构化数据集
2. **本月**：方向 A 的 Agent 框架原型——先在小电路上验证 LLM Agent 能否调用 placed/routed STA 工具
3. **下月**：两方向各出一个 4 页 DAC WIP / 6 页 ICCAD 投稿

---

## 5 禁重开清单（升级版）

- **不改回理想线网判据**——五轮实验已证明换判据改不动端点
- **不训 GNN 当接受判据**——CANON §8 已裁定，池内 AUC 0.479 < kind_only 0.555
- **不加带/pin swap/JOINT 加深/扩覆盖**——CANON §5 已裁定
- **不做签核 RC（Calibre/StarRC）**——没有 license，且"签核精度"不是瓶颈（布局离散 0.10 ns >> 签核-估计差 0.01 ns）
- **不跑 8 例全量实验再测一遍**——已有 4 例 + W1 8 例归档，现有结论转向新 framing 即可
- **不重启 `--physical-gate`（扇出线载 spef）**——结构缺陷已证明，要用就用真实布局档

---

## 6 参考文献（待补充完整 BibTeX）

| 论文 | 关键信息 |
|---|---|
| Jiang et al. 2024 "IR-Aware ECO Timing Optimization Using Reinforcement Learning" | RL+R-GCN，post-physical-design gate sizing，45nm 开源；arXiv:2402.07781 |
| Liu et al. 2021 "RL-Sizer: VLSI Gate Sizing with RL" | 学习尺寸决策，TCAD/ICCAD |
| Chen et al. 2024 "AiTO" | 联合尺寸与缓冲动作 |
| Huang et al. 2025 "Phys" | 物理感知尺寸优化 |
| Zhang et al. 2025 "Buffalo" | 缓冲树生成 |
| He et al. 2023 "STA" | 预布局时序与线长估计 |
| Tian et al. 2023 "GNN survey" | EDA 图学习系统梳理 |
| Chip-Chat (DAC 2024) | LLM 对话式芯片设计 |
| ChatEDA (ICCAD 2024) | LLM Agent 自主调用 EDA 工具 |
| LLM4ChipDesign (2025) | LLM 在芯片设计应用综述 |

---

> 本文件替代 `project_docs/DIRECTION_RESEARCH_2026-11-10.md`（后者侧重五轮实验后的"下一步做什么"，本文件侧重"项目整体可以升级成什么"）。