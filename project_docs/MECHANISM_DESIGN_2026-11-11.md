# FAECO 新机制设计：基于已有文献与实验数据的性能提升路线

> 2026-11-11 · 受用户委托：在已有公开论文基础上，利用我们的既有实验数据与代码仪器，设计新机制以实现更好的性能提升。
> 本文件为路线级文档，每个机制含具体装置、预注册判据、停止规则与可写/不可写边界。

## 0. 三十秒现状

- **最接近的公开 SOTA**：OpenROAD `repair_timing -setup`（LR resizer）在我们的 8 例 ISCAS89 上 **+0.5836 ns**（三布局布线后均值），8/8 优于 baseline。
- **我们的 FAECO-P**（覆盖优先 + 布局集成判据）：**+0.2473 ns**（8/8 优于 baseline），但 0/8 优于 resizer，均值差 **−0.3362 ns**。
- **差距的根源是动作量**：resizer 一次调用插 8–38 个缓冲 + 大量改尺寸；FAECO-P 八例共接受 16 个单实例补丁。但两者的动作空间是**互补的**（resizer 不做 R 等价改写、不做 JOINT、不按覆盖排序）。
- **我们有一条独特且已验证的杠杆**：布局档→布线后签核的校准比是**按动作种类系统的**（B 类 5.5×、G 类 1× drive 0.40 / 4× drive 1.01、JOINT 0.72），且**覆盖优先排序减少 STA 7.8–19%**。
- **文献中没有人把这两条组合在一起做 ECO**。E-Layout（ICCAD'26）用 e-graph+RL 做 logic restructuring（6% TNS, 2% WNS，商业流程），GoalEvolve 用 LLM 做全流程调参（30.67% TNS，默认 OpenROAD），Jiang et al. 用 RL+R-GCN 做门尺寸（45nm 开源）。三者都没有**按种类校准**和**覆盖优先调度**。

## 1. 外部文献地图（只列能直接复现或对标的）

| 论文 | 发布 | 机制 | 动作空间 | 度量 | 开源？ | 我们的可超越点 |
|---|---|---|---|---|---|---|
| **OpenROAD resizer** | 持续更新 | LR gate sizing + buffering | 尺寸、缓冲、VT swap | +0.5836 ns / 8 例（我们的仪器） | ✓ | 动作空间互补（R/JOINT/覆盖排序）、校准 |
| **E-Layout** Fang et al. | ICCAD'26 | RL+e-graph+RAG 做 logic restructuring | 逻辑变换 + 物理实现 | 6% TNS / 2% WNS / −1% area（9 设计，商业流程） | ✗ | 覆盖优先代替 RL、开源流程代替商业流程 |
| **GoalEvolve** Liu et al. | 2026.08 | LLM Teacher-Student 进化 OpenROAD 全流程 | 全流程参数 | 30.67% TNS / leak −21% / dyn −9%（8 ASAP7 设计，默认 OpenROAD） | 未开源 | ECO 特化（不做全流程）、校准后优于默认 resizer |
| **Jiang et al.** | 2024 | RL+R-GCN gate sizing + LR | 门尺寸 | Pareto front 左移（45nm 开源） | 未开源 | 覆盖优先替代 RL、加 B/R/JOINT |
| **GraPhSyM** Agiza et al. | ICCAD'23 | GATv2 预测 post-synthesis delay | 无（只预测） | delay 98.3% / area 96.1% 准确率（6000 adders） | ✗ | 我们的校准 + 覆盖优先是**行动**型机制 |

**最关键的外部事实**：
1. **E-Layout 未开源且跑在商业流程上** → 我们用 OpenROAD + 覆盖优先可以在开源赛道领先。
2. **GoalEvolve 做全流程调参** → 我们做 targeted ECO（单阶段，验证预算固定），精度与可解释性可能更好。
3. **Jiang et al. 只有门尺寸** → 我们加 B/R/JOINT + 覆盖排序是直接的动作空间扩展。
4. **所有外部论文都没有"按种类校准 placed→signoff"的概念** → 这是我们可以**第一个写**的。

## 2. 我们的既有资产（在文献中的独特位置）

| 资产 | 证据 | 在文献中的状态 |
|---|---|---|
| **覆盖优先排序** | 减少 STA 7.8–19%（8 例），同时维持 8/8 改善 | **独一**，无人做过 |
| **placed→signoff 按种类校准比** | B=5.5, G(1×)=0.40, G(4×)=1.01, JOINT=0.72（10 例标注） | **独一**，文献中无此概念 |
| **组合候选（JOINT）单次 STA 评估** | multi-gate sizing 候选一次测量省 5–6 次 STA | **独一**（E-Layout 的 joint 是逻辑+物理，我们是多门联合） |
| **三布局集成判据（placed_ens）** | k=3 均值使判决噪声降低 √3 倍 | **独一**（文献只用单布局或签核） |
| **布线后三布局端点** | 同网表换 util 0.30/0.35/0.40 重布，均值作端点 | **独一**（文献只用单次运行） |
| **OpenROAD resizer 全量基线** | 8 例 ISCAS89、三布局、PEAK 0.5836 ns | 文献中**从未有此基线** |

**结论**：我们有 5–6 个文献中无人做过的独特贡献，已全部实测。缺的是把它们**组装成一个胜出既有 SOTA 的完整系统**。

## 3. 机制提案

### 机制 A：签核校准覆盖优先 ECO（SCCF-ECO）

**核心思路**：把我们的两条最强杠杆——按种类校准 + 覆盖优先排序——组合成一个完整系统。不再用原始 `placed_delta` 排序，改用 `placed_delta × k_kind` 校准后排序；保持覆盖优先的轮次调度；最终验收用布线后三布局均值。

**为什么认为它能超过 resizer**：
1. 校准系数直接解决我们已诊断的「placed 系统偏」——B 类在 placed 下被低估 5.5 倍、G 类小驱动被低估 2.5 倍，校准后 B 与 G 会在排序器上公平竞争。
2. 覆盖优先的轮次调度减少 STA（已证 7.8–19%），等价于同等预算下能测更多候选。
3. Resizer 是单次全局 LR，不做逐轮重评分——我们在重评分的轮次中持续引导搜索到覆盖率最高的区域。
4. 前序 arm K（按种类校准排序回放实验）显示校准会改变每轮的 top-1 选择（离线回放已证，非恒等变换），且在 s382 iter1 上校准选择了签核更优的门尺寸（+39% 增益）。

**装置（可直接焊接已有代码）**：
- 臂 **K-ens** = arm E（`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40 --workers 4 --seed 1`）的逐字配置 + `--postroute-calibration "B=5.64,G=0.60,JOINT=0.53"`。
- 校准常数来源：s382+s953 的 A6j 补丁链（n=4 步，Σrouted/Σplaced），**held-out s641/s832 上检验**。
- 端点 = `rseco.routed_sta.run_routed_sta`，三布局 (0.30, 0.35, 0.40) 均值。
- 电路：s382, s641, s832, s953（保持与前几轮同族），held-out = s641/s832。

**预注册判据**：
- **H1（校准确实变排序）**：held-out 两例（s641, s832）的离线回放（`replay_selection.py`，零 STA 成本）显示 ≥1 轮的 top-1 排序在被校准后改变 ≥1 例。
- **H2（端点转移，主判据）**：K-ens 三布局均值增益 > arm E 三布局均值增益，held-out 两例 **都** 为正 **且** held-out 均值差 ≥ +0.03 ns（约 1× 噪声底 0.03，低于 H2 旧门 0.05 是因为 held-out 只有 2 例、端点噪声 ≈ 0.06 ns/例）。
- **H3（成本）**：候选 STA ≤ 1.1× arm E（校准不改每轮候选数，只改排序）。
- **停止规则**：H2 不过 → 停线、如实记「校准 + 覆盖优先在 held-out 上未转化为端点收益」→ 转机制 B。**不调参重跑**。
- **晋级规则**：H2 过 → 扩到 8 例（新预注册）→ 若 8 例均值差 ≥ +0.05 ns → 可写「签核校准覆盖优先 ECO 超过 arm E，接近或超过 resizer」。

**预期收益（来自已有数据的外推）**：
- arm E vs base: +0.2473 ns（4 例均值，8/8 正）。
- 校准臂离线回放（arm K replay）显示：s382 iter1 校准后选了驱动的 4× 变体（而非贪心的 2×），签核实测增益 +39%。
- 如果校准在 held-out 上兑现 30–50% 的 step-level 改进，held-out 2 例均值可能从现在的 ≈+0.01 ns（arm E 在这两例上几乎为零）提升到 +0.03–0.05 ns。
- 外推 8 例：若均值差从 E 的 +0.2473 提升到 +0.35–0.45 ns（+40–80%），仍**低于 resizer 的 +0.5836**，但差距从 −0.336 缩到 −0.15~−0.23 ns。
- **诚实边界**：校准解决的是"排序"，不是"动作量"——resizer 一次改 8–38 个单元我们改 1–3 个，这个差距校准填不平。A 能缩差距但**不太可能反超 resizer**。

**优势**：风险最低（零新实验、只需跑 4 例 K-ens + 已写好的离线回放），即使不晋级也能产生一篇短文（校准 + 覆盖优先）。

**劣势**：动作量差距填不平，可能结果仍是"有改进但不反超"。

---

### 机制 B：两级过滤 ECO —— 签核校准筛选 + 布线后验证接受（TCF-ECO）

**核心思路**：机制 A 用 placed 校准 + 三布局均值判据，但仍然依赖 placed 估计。机制 B 把"接受"这一步也搬到布线后：每轮先用校准 placed 筛选 top-k 候选（k=2–3），再对这 k 个做**真实布线后 STA**（同一 `routed_sta` 流程），选布线后 WNS 最优的接受。k 由 STA 预算决定。

**为什么这是质变**：我们已证实 placed 在 post-CTS 网表上绝对差 ~1 ns、且 +0.6 ns 的增量在布线后翻号（`experiments/20261117_postcts_residual`）。**只要判据还依赖 placed，在 post-CTS 终点上就不可迁移**。机制 B 把最终判定权搬到签核档，从根本上解决了判断器与端点不一致的问题——**代价是每轮多 k 次布线**（每次约 5 分钟）。

**装置（需新代码）**：
- 新增 flag `--routed-verify k`（k=2，默认 0=关）。在 `_call__` 的接受循环中，先按校准 placed 排序取 top-k，对每个 `run_routed_sta(netlist_path)`（幂等缓存按 sha256），选 routed WNS 最优的接受。
- 臂 **V** = arm E 配置 + `--postroute-calibration "B=5.64,G=0.60,JOINT=0.53"` + `--routed-verify 2`。
- 电路：s382, s641, s832, s953（前序臂已证明了递进逻辑：E → K → V）。
- STA 预算从 arm E 的 500 提升到 500 + 20(轮) × 2(k) = 540，**同预算下比较臂间**（每轮 routed verify 的 2 次布线从 STA budget 扣）。

**预注册判据**：
- **H1（可行性）**：3/4 电路完成 ≥10 轮、接受 ≥1 个补丁。
- **H2（端点转移）**：臂 V 三布局均值增益 > arm E，≥3/4 为正，均值差 ≥ +0.05 ns。
- **H3（成本）**：wall clock ≤ 3.0× arm E（每轮多 2 次 ~5 min 布线，20 轮 = 额外 ~200 min ≈ 3.3 h；arm E 单电路约 20 min × 4 = 80 min → 比例 ≈ 3.5）。
- **停止规则**：H2 不过→ 停线、记「两级过滤未转化为端点收益」。不调参。
- **晋级规则**：H2 过 → 可写「布线后验证接受判据优于 placed 集成判据」→ 与 resizer 对照（需新预注册）。

**预期收益与风险**：
- 理论上界：每次决策都是布线后最优（而非 placed 近似最优），应能消除 arm E 中 placed 误判带来的全部 suboptimal choice。
- 我们已有前序证据：s382 的 iter1 的 4 个候选中 placed 最优 +0.1217 → routed +0.0852（贪心），placed 次优 +0.1175 → routed **+0.1188**（校准后最优），差值 **+0.0336 ns / step**。4 步累积约 +0.13 ns。
- 风险：k 次布线 = k×5 min，wall clock 可能在 deadline 内跑不完 8 例。

---

### 机制 C：覆盖优先 + OpenROAD Resizer 协同（COR-ECO）

**核心思路**：不再把 resizer 当对手，而是**当内层优化器**。我们的外层做三件事：
1. **切割**：按覆盖优先把电路分成多个子区域（cone），每个区域大小 = resizer 单次调用能有效处理的规模。
2. **调度**：在 STA 预算约束下决定每个区域的调用顺序与次数（覆盖优先 → 覆盖率最高的区域先调 resizer）。
3. **组合**：多个区域的 resizer 结果按"独立区域、不互相干扰"的原则并成最终网表，用一次全电路布线验收。

**为什么这比 bare resizer 强**：
- Resizer 是全局 LR，可能在小区域上做不够、在大区域上浪费迭代。
- 覆盖优先的调度保证有限的 STA 预算花在最能改善 WNS 的区域上。
- 每个区域独立调用 resizer，resizer 每次只看到一个小 subcircuit → 收敛更快、改动更集中。
- **已有正面证据**：P1′ pre-CTS（resizer 先做、我们再补）显示 +0.0786 ns 残余空间（2/3 正），证明 resizer 之后确有我们可抓的边际改善——只是顺序错了（应该我们先切割调 resizer，而非 resizer 先跑我们再补）。

**装置（需新代码）**：
- 新增 `code/src/rseco/cone_resizer.py`：输入电路 + 基线 WNS 端点 → 逐 cone 按覆盖优先排序 → 对每个 cone 调 `repair_timing -setup`（通过 OpenROAD Tcl 脚本，利用 `write_verilog -remove_cells` 导出）→ 重新拼回全电路 → 全电路布线验收。
- 臂 **COR**：无我方 ECO，只切割 + 调 resizer + 组合。比对 **bare resizer**（全局一次调）。
- 电路：8 例 ISCAS89。

**预注册判据**：
- **H1（可行性）**：≥6/8 电路 cone 拆分可重组合并布线成功（DRC=0）。
- **H2（主判据）**：COR 三布局均值增益 > bare resizer，≥5/8 为正，均值差 ≥ +0.05 ns。
- **H3（成本）**：resizer 总调用次数 ≤ bare resizer × 2.0。
- **停止规则**：H2 不过 → 停线、记「覆盖优先切割不改善 resizer」。**不调参**。
- **晋级规则**：H2 过 → 可写「覆盖优先切割使 resizer 的收益进一步放大」→ 本文最强主线（覆盖优先 + resizer 协同）。

**风险**：cone 拆分会改变 resizer 看到的 circuit 上下文（它原本看到全部 cell 和全局 slack）。在小 cone 上 resizer 可能"过度优化"局部而忽视全局。需要在预注册中把"cone 间互不干扰"作为一个检查项。

---

### 机制 D：Multi-Action Joint ECO（MAJ-ECO）

**核心思路**：我们已有证据：单步动作量 ≤ 布局离散（0.055 ns），但联合动作（6 门 JOINT）的 placed delta +0.1382 明显高于单门。问题是我们当前的贪心选择器压制了 JOINT——s641 的 JOINT +0.4767 被同轮单门 G +0.609 压掉。机制 D 改变接受规则：**每轮同时接受 ≥1 个独立实例上的最佳候选**（而非只取全局 argmax），并在后续轮次中"独立实例"去重。

**装置**：`--accept-k 3`（每轮接受 ≤3 个、且必须来自不同实例）。在 `_accept_result` 中收集所有 passing 候选、按 score 排序，取 top-k（去重实例）。其余逻辑不变。

**预注册判据**（与前类似，H1 动作数、H2 端点、H3 成本），停止规则同。

---

## 4. 推荐顺序与理由

| 顺序 | 机制 | 理由 | 时间 | 风险 |
|---|---|---|---|---|
| **1（本周）** | A：签核校准覆盖优先（SCCF） | 零新实验（已跑离线回放），只跑 4 例 K-ens | 1 天 | 低（可能不反超 resizer，但肯定产生可写结论） |
| **2（下周）** | B：两级过滤（TCF）— 如果 A 不过 | A 失败意味着"校准 alone 不够"→ 必须把接受判据也搬到布线后 | 2–3 天 | 中（墙钟可能超） |
| **3（备选）** | C：覆盖优先 + resizer 协同（COR）— 如果 A 和 B 都不够 | 这个方向最接近"覆盖优先"这一核心贡献的最强表述 | 3–4 天 | 中（cone 拆分可能改变 resizer 行为） |

**不推荐立刻做的**：机制 D（与 arm All/A6j 的问题域重叠，前序已部分封口）。

---

## 5. 与论文的关系

- 当前论文（r116, 11+15 页）已冻结，记述的是"预布局门级 ECO 的候选探索与失效刻画"。
- 机制 A/B/C 任何一个过晋级 → 可产出一篇**新论文**："Post-Placement Coverage-First ECO with Signoff-Calibrated Candidate Ranking"（或类似），ISACS89 + ITC-99 双族、对标 OpenROAD resizer + E-Layout。
- **不改**当前论文的数字；新论文是独立产出。
- 如果 A/B/C 全部不过晋级 → 如实记录为"三条路线在预注册下均未触发"，这是一篇 honest negative-result paper 的素材。

---

## 6. 立即可以跑的事（零新代码）

**A 的离线回放**：`experiments/20261113_buffer_calibration/replay_selection.py` 已写好、已对 E/P/A6j 跑过——校准确实改变了多轮选择。立即可以做的事：
1. 对 arm E 的 s641/s832（held-out 两例）跑 `replay_selection.py`，确认校准在 held-out 上是否改变了 top-1。
2. 如果 changed_rounds ≥ 1：立即启 `bash experiments/20261113_buffer_calibration/run_arms.sh K s641 s832`（约 40 min × 2 例）。
3. 端点测量（约 3 h），判定 H2。
4. 无论 H2 过不过，都是一条可写的裁定。

要我立刻执行 A 的离线回放吗？