# FAECO 路线图：从预布局 ECO 到布局后 SOTA

## 2026-11-13 可调预算执行计划（用户已授权继续）

**Goal:** 实现可调WNS预算的联合选择内核，并完成52既有物理端点的可复现预算分析及选中端点SEC。
**Architecture:** Resizer提供固定reference；纯Python策略/有界组合搜索与物理评估器分离。历史重筛仅验证判定/选择接口，不冒充在线搜索优势。
**Tech Stack:** Python/pytest；复用现有OpenSTA/Yosys证明适配器。
**Spec:** 本文件可调预算草案与CANON最新三条；当前checkout保留用户/此前实验状态，不另建worktree。
**Global constraints:** 默认B=.010ns，finite/nonnegative；tol=1e-6ns；固定参考WNS/hold，hold>=0；TNS辅助；完整计数；不改sealed；实验运行前绑定输入和超时。
**Review focus:** baseline漂移；NaN/单位/缺证据；组合非加性；同实例备选冲突；未经SEC输出与实际验证成本混淆。

- [ ] Task1 内核：新建code/src/rseco/budgeted_recovery.py及code/tests/test_budgeted_recovery.py。不可变Endpoint/Action/BudgetPolicy；Endpoint绑定scope_id与evidence_id，valid明确代表调用方已完成物理/结构检查，sec_pass单列。assess使用固定reference；select_endpoint(require_sec=True)默认只交付已证明点，无收益精确返回reference。可显式选择待SEC候选但必须标注。
- [ ] Task1搜索：bounded_search(reference, actions, evaluate, policy, max_evaluations, beam_width, max_depth)。evaluate接收规范排序动作ID元组并从固定reference测联合端点，不累加预测作验收；相同instance不同动作互斥，集合去重，逐实际回调计数。候选从面积估计排序；每层依据实测超预算/hold缺口、面积收益、时序确定保留有界beam，保留数值不合格中间态供后续补偿。已验可行终点档案只作选择，不声称全局最优。宽度/深度/预算为研究参数，默认不向现CLI暗中接入。
- [ ] Task1 TDD：先验证测试失败，再实现；覆盖finite/negative/ps换算、固定总预算、TNS非硬门、hold拒绝、缺证据/错scope、SEC默认门、非加性、同实例冲突、评估上限、无收益fallback、固定pool随B增加面积不升。单元测试是oracle工程验证，不是科学证据。
- [ ] Task2 根：timing_budget_20261113内绑定旧52原始证据，输出0/5/10/20ps预算表与选中端点；确认结构/新SPEF/DRV/DRC，记录0新route/STA。重用已有证明核心，仅注册新唯一RESTORE074，180s内部/240s外部，证明前提交注册。
- [ ] Task3 独立审查：正式核验s382调用repair_timing前CTS面积A0、Resizer后AR、候选AF三点的阶段及完整实例/Liberty计数；形成带SHA回执，缺证据则不报回收率。审核新内核和证明，根复核。
- [ ] Task4 集成：新内核+现有recovery相关测试及完整生产回归（合理超时）；CLI/import smoke；源/证据/文档一致检查，阶段commit+push。CANON/LOG/OI/REGISTRY实时同步，生产CLI15ps/旧SPEF不得误称新物理路径已接通。

**Execution ownership:** 编码子任务独立worker；根负责原始证据/SEC/集成；独立审计worker；专职recorder更新记录。此次只实现/验证本阶段，后续在线物理评估器接入与跨设计/强baseline保持待办，不能称完整ICCAD机制已证实。


> **可调预算草案审查补充（2026-11-13）**：W_R/A_R/H_R固定为Resizer输出，A_0仅用于净新增面积回收率分母，不替换接受门参考。无可行正收益时精确返回原CONTROL或已验证档案端点；评分仅生成提案，ΔA/ΔWNS比率不能保证安全。对既有物理端点按不同预算筛选计0新EDA；预算改变候选搜索后产生的新独立运行另行预注册/计数。旧IO约束覆盖不足仍在，不因新预算或档案筛选宣称完整安全。

## 2026-11-13 可调预算机制草案（设计待落实）

保留Resizer作为前端，固定其终点W_R/A_R；用户设置非负有限WNS最大损失B(ns)，拟默认0.010ns。优化 `max A_R-A(x)`，硬门 `W(x)>=W_R-B`（1e-6ns纯数值容差），原hold安全门、结构/DRV/物理/SEC保持；TNS完整记录并辅助同面积择优。

每轮共同考虑面积与时序代价，组合实际复测，保留已验证非支配物理终点供不同预算选择。参考不能每步重置，预测不能累加冒充安全证明。UI建议ps输入并显式转ns；0/5/10/20ps只说明可配置档，不是已跑结果。下一步仍需确定实际选择算法、完成实现和物理验证。

现有CLI max-degradation默认0.015，且旧SPEF判断与本草案最终物理门不同；此次没有改代码/默认值/旧证据或新EDA，不称机制完成。此为保留Resizer前端的阶段草案，长期完整自有机制仍是探索目标。

## 2026-11-13 用户澄清：保留Resizer前端，自有后续优化机制

默认流程为共同初始设计 → Resizer时序修复 → 自有面积/时序联合优化 → 物理验证。Resizer可以是正式前端，不要求自行重写时序修复器，也不要求主方法脱离Resizer独立冷启动。自有贡献应落在候选构造、联合选择、交互处理和物理反馈；可以利用Resizer修改历史作为线索，但候选能力不能仅限于撤销其历史动作。比较同一Resizer终点上的原生恢复、简单贪心与自有机制，固定约束和评估预算。沿用净新增面积回收率主指标及总面积/时序并列报告，WNS预算10ps、TNS辅助、hold原安全门不变。此前“仅baseline/可选warm start”“必须从初态独立完成修时序”不再是项目要求。这里明确研究边界，不声明新算法已实现，也不未经核验将Resizer称为已证明最优的SOTA。


> **面积归因补充（2026-11-13，现行）**：A_0应取同一物理阶段、Resizer调用前的完整面积；不能用综合前或CTS前A_0与布线后A_R作差并全部归因Resizer。若端到端对照无法隔离其它阶段，指标应称「相对共同初态的净面积开销」，不称「Resizer专属新增面积」。当前area_audit.json明确未展开baseline层次（No baseline hierarchy expansion），因此新增面积回收比例暂不报数。

## 2026-11-13 最新方向与评价口径（优先于下方历史路线）

用户将重点转为回收时序修复带来的净新增面积，评价量为 `(A_R-A_F)/(A_R-A_0)`，仅在A_R>A_0且初始/Resizer/最终三者同库、同阶段、完整实例口径时计算。分母不是改动单元面积总和；始终并列绝对面积、总面积降幅及WNS/TNS/hold，避免把小分母高比例当总收益。A_0未核验前不再引用旧67%。

目标是从同初始网表独立生成修时序和减面积动作、统一选择并反馈实际物理结果的完整自有机制。Resizer作为baseline或可选warm start，不把其edit历史作为候选来源前提。该机制当前未建立、优势未证明；本条只记录研究方向，不展开实现设计或授权新EDA。现行时序偏好为首轮10ps WNS损失预算、TNS辅助、hold原安全门；下方“WNS/TNS/hold均不下降”等是既有strict阶段历史，旧实验结论不回写。

> **2026-11-13 用户最新主目标**：完善为自己的面积优化机制，始终按 ICCAD 标准评估，**保证时序不下降再优化面积**。当前先做 s382 最小补偿研究，主门为 WNS/TNS/hold 均不退化（数值容差1e-6 ns），其余时序预算只作诊断。独立算法贡献须通过等预算强基线、消融、跨设计与完整物理验证建立，不能由工具包装或单例穷举代替。新预注册：`project_docs/evidence/recovery_repair_20261113/PREREGISTRATION.md`；旧资格验证失败原件保留。

> **2026-11-12 接手评估更新**：用户要求先评估现有 Recovery 工作是否匹配 ICCAD，再决定机制优化；确认未提交 DAC 2027 摘要。当前判断：选题属于物理设计优化，但算法新意、强基线与恢复后物理验证尚不足以支持投稿就绪。下方原 P1–P4 和时间预算保留作历史，不代表 Recovery 已获科学晋级；本轮未启动新机制实验。

## 2026-11-13 续跑决策：先完善候选覆盖，再比较选择机制

新证据包 `evidence/strict_area_search_20261113/`：九个固定seed双动作全部TNS退化，面积优先与风险优先在k3主比较及全部前缀均保留原seed；另两同面积库目标也失败。新增11route/22STA、无新SEC，旧seed0.594530321%面积收益不变。本轮不支持调度优势，不继续通过改分数或换名称为该九点池制造机制贡献。

完整网表/Liberty枚举62个兼容降面积目标（33实例），旧13动作只有10个正面积目标；其中52个遗漏目标仅054中间档在本轮测过，失败，另51个未测。这让下一步候选生成有了独立于Resizer回退清单的入口。优先评估未测组合逻辑目标、保存失败边界；FF与clock目标先补完整约束/clock影响审查。候选枚举和严格安全门属于工程基础，独立贡献仍须同预算强基线、消融、跨设计证明。现有3数据输入/6输出没有IO delay/load/transition设置，不能将现有相对非退化推为完整IO保证。

## 2026-11-12 已授权执行：ICCAD 资格验证

用户在上述评估后明确「可以，持续推进」。先验证可信测量、强基线、独立机制三道门；原 P1–P4 不自动重开。本节采用 writing-plans 的分步验证方法，按仓库约定复用本路线图。

1. **仪器修复（OI-080/083）**：复现五个 Yosys 相关失败并按环境/实现归因；`code/scripts/recover_area.py` 仅修直接导入和零值语义，`code/tests/test_recover_area.py` 先红后绿，最后全量 `pytest code/tests`。不改旧结果。
2. **物理重入检查**：先读真实 OpenROAD 26Q3 help，绑定工具和 DEF/Verilog/SPEF/Liberty SHA。使用现有 routed DEF 恢复同一状态，空操作对照验证网表结构与独立 STA 可重现；原始路线的理想时钟只用于复现，新增 propagated-clock 结果单独命名。
3. **单例反驳性 pilot**：先 s382：同起点 CONTROL / 历史 RECOVERY_V2 / 原生 `recover_power`，相同合法化、布线与重新提取；所有输出新目录。固定寄生只作诊断，最终报告 setup、hold、TNS、DRV、DRC、面积及运行代价。空操作对照不通过先修测量链，不能直接判方法失败；零操作 b02 与跨布局敏感 s953、较大回收 b07 为随后扩展对象。
4. **晋级条件**：只有完整物理约束通过、相对强恢复基线仍有面积/成本优势，才研究联合交换等新机制；同预算多轮贪心能追平则不主张联合机制贡献。当前不引入 ML，不承诺收益阈值或投稿日期。

预注册与回执位置：`project_docs/evidence/recovery_qualification_20261112/`。实验运行前登记配置、版本与反驳条件；记录员维护 LOGS/OPEN_ISSUES/EXPERIENCE。工具超时和失败原件保留。未实现、未评估或不支持的检查标 unknown，不把缺失当通过。

## 2026-11-13 执行路线：严格时序约束下的净面积优化

目标函数是完整映射单元面积最小化，硬门是相对固定 Resizer CONTROL 的 propagated setup WNS、setup TNS、hold WNS 均不下降（1e-6 ns 仅作数值容差），并满足当前支持的物理/电气检查和完整功能等价。现阶段仍存在绝对 setup 违例，完整约束、多角和跨设计验证尚未建立；不能把相对非退化写成 timing closure。

**自己的机制应落在候选构造与选择上。** OpenROAD 继续承担数据库、布局布线、提取等基础设施。我们要验证的机制是：把面积释放动作与少量补偿动作组成一个联合候选，以共享违例路径和实际物理反馈分配补偿成本，最大化扣除补偿后的净面积收益。联合候选须整体测量、整体接受或回滚；任何便宜的预测只决定验证顺序，不能越过最终物理门。共享路径覆盖目前只是候选依据，其独立价值尚未证实。补偿提案还必须检查实际相关弧、转换方向与slew/load，不能假定更大驱动档传播更快；本轮失败归因见 `evidence/recovery_repair_20261113/pathdiag/JOINT_ATTRIBUTION.md`。

| 门 | 实施及反驳条件 | 当前状态 |
|---|---|---|
| 测量可信 | 完整转义实例面积、最终网表与新 SPEF 绑定、setup/TNS/hold 同时审查、SEC | 仪器与 s382 对照已建立；完整约束仍 open |
| 回退交互 | 原13动作逐个恢复，再按固定规则测12组合；若简单回退即可达标，先采用简单方案 | 13单恢复+12组合均有效，但没有严格可行点；保留全部阴性结果 |
| 强简单对照 | 从 CONTROL 分别实施13个单动作，完整测量，不按好结果提前停 | Stage C 全13完成，唯一通过点面积省0.594530321%，SEC与独立核验通过；属于简单基线 |
| 联合补偿 | 固定失败基点，新增少量同功能升尺寸动作，验证净面积与全部时序门 | Stage D 三例均有效但严格门失败；共享路径覆盖与驱动档位不足以预测收益 |
| 机制贡献 | 与相同候选空间、相同物理验证预算的安全贪心、面积优先及原生恢复/修复比较；消融共享路径选择和联合动作 | 待前述可行域检查后实施；简单基线追平则不主张联合机制优势 |
| ICCAD 证据 | 跨规模/跨设计、时序收敛与未收敛起点分别测、约束/角覆盖、失败案例、实际工具调用成本、强基线版本冻结 | 未完成；单个 s382 可行点也不能判投稿就绪 |

所有新结果归入 `evidence/recovery_repair_20261113/`。Stages A/B/C 与后续补偿预算分开，禁止事后合成“事先固定的总预算”，禁止只报告成功点。论文冻结数据保持不动。

**旧竞争描述的处理**：下方2026-11-11内容保留为历史路线，尤其“无竞品”“唯一”“Resizer缺JOINT”等排他主张不作为当前依据。当前[官方 Resizer 文档](https://openroad.readthedocs.io/en/latest/main/src/rsz/README.html)列有多种修复变换及可配置 sequence/phases；“使用多种动作”本身不足以区分我们。后续必须按固定实现版本逐项比较候选空间、选择策略、物理反馈和预算，而不是按工具名称建立创新主张（OI-086）。

> **2026-11-11 定稿**。本文是 FAECO 项目的**唯一路线文档**——所有后续实验和论文均按此推进。
> 替代此前 `DIRECTION_RESEARCH_2026-11-10.md` 和 `DIRECTION_UPGRADE_v2_2026-11-11.md`（二者保留作历史溯源）。
>
> **红线**：不改论文冻结数字（r116）、不重开已裁决不可能的门（CANON §8）、不 push、不做纯分析/论述论文。

---

## 0. 三十秒现状（接手者入口）

| 维度 | 现状 |
|---|---|
| 中文论文 | 主稿 11 页 / 补充 15 页，r116，质量门双 PASS |
| 英文论文 | 停 r94 前叙事，1.07/0.16 未同口径，**暂停** |
| 代码 | `placed_sta.py` + `routed_sta.py` 仪器建成，`test_accept_all.py` + `test_postroute_calibration.py` 通过 |
| 测试 | 1094 passed / 7 skipped / 156 subtests |
| 实验 | 六轮预注册实验全部封口（P/E/A6j/K/All/LLM 回放） |
| git | HEAD `fc6ae09`、ahead 39、未 push、worktree clean |
| 环境 | WSL2 Ubuntu, OpenROAD 26Q3, sky130hd, ISCAS89 8 例 + ITC-99 2 例 |
| **本轮方向转折** | 从"预布局改判据"转"布局后覆盖优先 ECO 对标开源 SOTA" |

---

## 1. 为什么转方向

六轮预注册实验的结论：在预布局门级这一设定下，**判据档位、判决精度、动作宽度、按类校准、全盘接受——全部不动端点**。根因是 CANON §7.4「动作粒度 < 测量分辨率」+ placed→signoff 秩相关在跨迭代口径下很弱（Spearman 0.164）。

但**同迭代同基线**的正确口径下，placed→signoff Spearman = **0.70–0.80**（n=10），且存在可预测的系统性偏差（1×:0.40 / 4×:1.01 / B:5.5×）。这意味着：**在布局后设定下，有真实寄生的判据是可靠的，覆盖优先有竞争空间**。

---

## 2. 竞争格局

| 工作 | 时间/发表 | 方法 | 阶段 | 指标 | 开源 |
|---|---|---|---|---|---|
| **E-Layout** (Fang et al.) | **ICCAD 2026** | RL + e-graph + RAG | 布局后 | 6% TNS / 2% WNS 超商业工具 | 否 |
| GoalEvolve (Liu et al.) | 2026.08 | LLM 进化全流程 | 全流程 | TNS +30.67% 超 OpenROAD 默认 | ✅ |
| **OpenROAD resizer** | 持续 | LR | 布局后 | 生产级开源基线 | ✅ |
| Jiang et al. (2402.07781) | 2024 | RL + R-GCN | 布局后 | 延迟-功耗 Pareto | 否 |
| GraPhSyM (Agiza et al.) | ICCAD 2023 | GNN 代理 | 跨阶段 | 98.3% 预测精度 | 否 |

**FAECO 的差异化**：
1. **覆盖优先调度**——文献中无竞品按"覆盖多少失败端点"排候选（E-Layout 的 RL 是全局优化、resizer 的 LR 是灵敏度驱动）
2. **全开源**——E-Layout/Jiang 均未开源，FAECO 是唯一可在 sky130/ISCAS89 上直接复现的 ECO 方法
3. **动作空间更宽**——R（等价改写）+ G（门尺寸）+ B（缓冲插入）+ JOINT（联合动作），resizer 缺 R 和 JOINT

---

## 3. 四阶段路线

### 阶段总览

```
P1: FAECO-P (post-placement)
    └─ 对标 OpenROAD resizer
    └─ 目标：≥5/8 例 WNS 优于 resizer
    └─ 约 3–4 天墙钟（全自动）
    └─ 产出：DAC/ICCAD 短文 或 TCAD 通讯
         │
         ▼
P2: FAECO-P+ML (签核标注训练排序器)
    └─ 替代贪心 max placed_delta
    └─ 目标：≥6/8 例优于 resizer + 跨电路 Spearman ≥0.7
    └─ 约 2–4 周（含数据采集）
    └─ 产出：TCAD 长文
         │
         ▼
P3: Cross-design (跨电路迁移)
    └─ P2 排序器在 held-out 电路族（ITC-99 / OpenCores）上验证
    └─ 目标：性能不退化
    └─ 约 2–4 周
    └─ 产出：DAC 短文 或 TCAD 增刊
         │
         ▼
P4: Multi-objective (Pareto 优化)
    └─ WNS + 面积 + 功耗三目标
    └─ 目标：Pareto 支配 resizer 在 ≥75% 设计点上
    └─ 约 3–6 周
    └─ 产出：TCAD 长文 或 DAC 长文
```

### P1：FAECO-P —— 覆盖优先 vs OpenROAD resizer

> **P1 结果（2026-11-11，已判定 FAIL）**：8 例 ISCAS89 三布局布线后均值，base→resizer **+0.5836 ns**、
> base→FAECO-P **+0.2473 ns**、FAECO-P−resizer **−0.3362 ns**，**0/8 电路更优** ⇒ **不晋级**。
> 主因是动作量（resizer 净增 8/9/13/38 个逻辑单元 vs FAECO-P 0/0/0/1），不是判据精度；
> 详见 `experiments/20261115_p1_resizer_vs_faeco/REPORT.md`、`project_docs/CANON.md` §1 裁定 16。
> **Hybrid 结果（2026-11-11 补记，同样 FAIL）**：同一 resizer 流程、只换起始网表（FAECO-P 终点），
> 三布局均值胜 **5/8**、均值差 **+0.0243 ns**（门槛 +0.05）⇒ 不晋级。
> ⇒ P1 与组合臂一并封口；本路线续做只允许「把 resizer 当内层优化器、我们做预算调度」这类可量化问法，
> 见 `experiments/20261115_p1_resizer_vs_faeco/REPORT.md` §4b、`project_docs/CANON.md` §1 裁定 17。
>
> **P1 之后允许的唯一问法（更新）**：可组合性（Hybrid 臂）也已在上面 FAIL ⇒ 仅剩
> 「把 resizer 当内层优化器、我们做外层预算调度」这一个可量化问法；若它也不成立，本路线需整体重定题（见 §7 风险表）。


**目标**：证明覆盖优先调度在布局后设定下，可以在 ≥5/8 例 ISCAS89 上取得优于 OpenROAD resizer 的 WNS 改善，且面积不增加。

**设定**：
- 电路：ISCAS89（s27, s382, s420, s641, s713, s820, s832, s953），period 0.5 ns
- 基线：同一 mapped.v 输入，Yosys 0.33 映射
- FAECO-P：`--physical-backend placed_ens --accept-all --enable-buffer --strategies R,G,B --joint-k 2`
- OpenROAD resizer：标准 ORFS 脚本（`repair_timing -setup`），默认参数
- 端点：签核布线后 WNS（`routed_sta.py`，util 0.30/0.35/0.40 三布局均值）

**判定门**：

| 条件 | 结果 |
|---|---|
| **FAECO-P WNS 优于 resizer 在 ≥5/8 例** | ✅ P1 成功 → 写论文、推进 P2 |
| FAECO-P 优于 resizer 在 3–4/8 例 | ⚠️ 临界——查逐例差异，针对性改进（补丁链分析 / 加签核校准） |
| FAECO-P 优于 resizer 在 ≤2/8 例 | ❌ 停线——记录"覆盖优先不比 LR 好"，分析原因 |

**实验步骤**（见 §5 复现命令）：
1. 跑 OpenROAD resizer 在 8 例的 baseline
2. 跑 FAECO-P 在 8 例（`--accept-all`）
3. 两组签核布线后端点对比
4. 逐例补丁链分析（哪些候选被接受？B 类占比？面积变化？）

**论文**：DAC/ICCAD 短文（6 页）或 TCAD 通讯（4–6 页）。
- 核心贡献：覆盖优先——一种全新的 ECO 候选调度策略，在布局后与 LR 竞争
- 基线：OpenROAD resizer（开源）、理想线网贪心（消融）、商业工具数字（引用 E-Layout 的基线）

---

#### P1′（2026-11-11，pilot）：镜像组合——resizer 终点之后仍有残余空间

- 装置：`experiments/20261116_resizer_then_faecop/`（resizer 先做 → 我方 ECO → 三布局布线后端点）。
- 判定：**H2 PASS，PROMOTE=YES**——RF−R′ 均值 **+0.0786 ns**（s641 +0.1202、s832 +0.1157、s382 0.0000），
  5 个被接受补丁的布线后增量全部为正。
- 边界：R′ 是比 P1 post-CTS resizer 弱 0.19/0.21 ns 的 pre-CTS 变体 ⇒ 只证明「动作空间互补」，不证明「在 P1 resizer 之上仍有余量」。
- **下一步（须新预注册）**：① 扩到 8 例；② 把 resizer 段换成 post-CTS 变体（先解决扁平网表重入 segfault）。
- **二轮（2026-11-11，post-CTS 变体）：H2 FAIL，PROMOTE=NO**。`experiments/20261117_postcts_residual/` 把 resizer 段换成
  post-CTS（P1 实际对手同形），三例三布局端点 RF−R′ = **−0.1659 / −0.5325 / −0.4879**（均值 **−0.3954 ns**），0/3 为正；
  对照端点忠实（re-entry gap +0.0168/+0.0160/−0.0830，|gap|<0.15）。根因：布局档判断在 post-CTS 终点上不可迁移
  （同网表 placed −2.10 vs routed −1.11，+0.609 的 placed 改善在布线后翻成 −0.532）。
- **结论（路线级）**：P1′ 在**当前机制**下封口。上条「下一步 ②」已完成且为负；「下一步 ①（扩到 8 例）」**不执行**——
  扩样只会把已判负的效应测得更准。若仍要续做这条线，唯一前提是**判断器与布线后端点的读数一致性**
  （例如改用布线后档判断、或把单步动作幅度限制在可迁移区间），并须新预注册。


## P2：FAECO-P+ML —— 签核标注训练排序器

**前提**：P1 成功（≥5/8 优于 resizer）。

**目标**：用 P1 产生的签核标注数据训练一个轻量级候选排序器，替代贪心 max placed_delta，进一步提升端点收益。

**方法**：
- 特征：placed_ens WNS 增益 + TNS 增益 + 驱动倍率 + 动作种类（G/B/R/JOINT）+ 候选实例的 fanout/depth
- 标签：签核 routed WNS 增益（同一基线下的配对测量）
- 模型：XGBoost 或轻量 MLP（≤100 参数），避免过拟合
- 训练/测试：在 ISCAS89 8 例上做 leave-one-circuit-out 交叉验证
- 离线回放：用训练好的排序器在 arm E 的 `eval_trials.json` 上选择，与贪心比端点

**判定门**：

| 条件 | 结果 |
|---|---|
| **排序器在 ≥6/8 例上 WNS 优于贪心，且 pooled Spearman ≥0.7** | ✅ P2 成功 |
| 排序器优于贪心但 Spearman 0.5–0.7 | ⚠️ 发消融研究，不推进 P3 |
| 排序器不比贪心好 | ❌ 停线——记录"placed 特征已经饱和" |

**论文**：TCAD 长文（12–14 页）。
- 核心贡献：第一个针对 ECO 候选的签核校准排序器 + 覆盖优先调度的端到端评估
- 消融：贪心 vs 排序器 vs 理想 oracle

---

### P3：Cross-design —— 跨设计迁移

**前提**：P2 成功。

**目标**：验证 P2 的排序器在未见电路族（ITC-99 或 OpenCores）上不退化。

**方法**：
- 在 ISCAS89 上训练排序器
- 在 ITC-99（b01, b03, 以及更大的 b04–b09）上做 held-out 验证
- 如果退化：加入少量 ITC-99 数据做微调（few-shot 迁移）

**论文**：DAC 短文或 TCAD 增刊。

---

### P4：Multi-objective —— Pareto 优化

**前提**：P2/P3 成功。

**目标**：在 WNS + 面积 + 功耗三目标上给出 Pareto 前沿，支配 resizer。

**论文**：TCAD 长文或 DAC 长文。

---

## 4. 不可做的事（防走偏）

以下方向已在 r30–r116 被实验证伪或裁决否决，**不得重启**：

1. ~~用理想线网档做接受判据（缺陷①）~~ → 已证伪
2. ~~用 spef 扇出线载做物理判据（方向 A）~~ → 已证伪（结构缺陷）
3. ~~换判据档位不改奖池（方向 C / r30 LOG-20261025-34）~~ → 决策级未触发
4. ~~只把判决精度提高（arm E）~~ → 46.8% 分歧但不改端点
5. ~~只把动作做大（arm A6j）~~ → 贪心压掉大动作
6. ~~按种类校准判据（arm K）~~ → 常数不可迁移
7. **GNN 打分器**（CANON §8）——池内 AUC 0.479 < kind_only 0.555
8. **自适应时限**（CANON §8）——R² 0.0977
9. **加带 / pin swap / JOINT 加深 / 扩覆盖 8→10000**（CANON §8）

**新增不可做**（本轮方向转折后）：
10. ~~写"为什么是天花板"的纯分析论文~~ → 用户拒绝
11. ~~在预布局理想线网设定下继续改机制~~ → 六轮证伪后封口
12. ~~用 `--physical-gate`（spef.py 扇出线载）做真实物理~~ → 结构上恒低估缓冲

---

## 5. 复现命令（P1 实验）

### 5.1 跑 OpenROAD resizer 基线

```bash
# 需要先对每个电路生成 OpenROAD flow 脚本，再 run
# 具体 Tcl 模板见 data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/
# resizer 在 CTS 之后、route 之前调用
# 然后对 resizer 输出做 routed endpoint 测量（与 FAECO 同一仪器）
```

### 5.2 跑 FAECO-P

```bash
# 在 experiments/ 下建新目录，复用 run_arms.sh 模板
# 核心 flag：
#   --physical-backend placed_ens --placement-utils 0.30,0.35,0.40
#   --accept-all --enable-buffer --strategies R,G,B
#   --joint-k 2 --max-instances 8 --workers 4 --sta-budget 500
```

### 5.3 端点对比

```bash
# 用 routed_sta.py 对每组终态网表做三布局均值测量
# base 读数从 experiments/20261110_placed_gate/endpoint* 复用
```

### 5.4 判定

```bash
# 逐例对比 FAECO-P routed_wns vs resizer routed_wns
# 统计优例数 → 判定 P1 是否通过
```

---

## 6. 文档更新约定

每完成一个阶段（P1–P4），更新以下文档：

| 文档 | 更新内容 |
|---|---|
| `project_docs/LOGS.md` | 追加 `## 2026-11-XX（P1：FAECO-P vs resizer …）` |
| `project_docs/CANON.md` | §1 新增裁定（如裁定 15：P1 结果） |
| `docs/EXPERIENCE.md` | 追加 `## rXXX` 条目 |
| `project_docs/evidence/EXPERIMENT_REGISTRY.md` | 追加实验条目（含预注册 SHA256） |
| `project_docs/HANDOFF_2026-11-09.md` | 标题日更新 + 新增对应 § |
| `.codex-handoff.json` | `next_steps` / `status` / head 更新 |
| 本文件 | 状态更新（阶段完成标记 + 判定结果） |

---

## 7. 风险与缓解

| 风险 | 概率 | 缓解 |
|---|---|---|
| FAECO-P 在所有 8 例上都不如 resizer | 中 | P1 停线，分析 LR 为什么更好，写"覆盖优先 vs LR 在 ISCAS89 上的实证比较"短文 |
| resizer 在 ISCAS89 上 WNS=0（电路太小，resizer 直接修完） | 中 | 增大 period 或换更大的 ITC-99 电路 |
| P1 过但 P2 排序器不优于贪心 | 中 | 说明 placed 特征已饱和，P1 结果本身够 DAC 短文 |
| P2 过但跨设计不迁移 | 高 | 缩小声称——只写"同族有效"，P3 转 few-shot 微调 |
