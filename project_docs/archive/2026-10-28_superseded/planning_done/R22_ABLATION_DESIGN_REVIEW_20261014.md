# R22 核心消融设计独立领域评审

日期：2026-10-14。审查基线：`46ede94`；新实验族：**Cprime（C′）**。范围：当前 `cut.py`、`flow.py`、`real_wns.py`、预算状态与入口脚本、旧 R11 方案 §7。仅写本报告，未改 production 源码、论文或实验；做了一次无 EDA、无文件写出的六门 Python 静态探针（`python -B`）。

## 1. 先行裁定

旧“只加五个 λ 的 CLI，再跑 Base/+feature/Full”方案不能直接执行。新显式 `cut_search_policy={legacy_constrained,weighted_st}` 加来源开关是正确方向；应先通过下列辨识探针，再冻结配置、版本和输入，最后启动 EDA。主线要接受以下最强反证：**等权与 Full 同样好；仅 Cc 不弱于融合；随机/简单顺序不弱于声明的融合排序；canonical Cw 总是退化成同一个端点门，导致 cost 未实际改变动作机会。** 上述任一种成立都不能靠换臂、换阈值或挑电路修成正结果。

本轮主对象建议为 **canonical weighted s-t Cw + 独立 Cc**。`legacy_constrained` 为同设置的强当前基线，不能把其结果称作式 (2) 的纯最小割结果。不得把 C′ 的新结果嫁接历史 C 的 1.07 ns、随机 0.40 ns 或首次改善台账。

## 2. 已确认的关键代码与混杂

| 路径/位置 | 真实行为 | 设计影响 |
|---|---|---|
| `real_wns.py:706` → `flow.py:350–383` | 默认 `use_constrained_cuts=True` | 当前默认不是 canonical mincut |
| `cut.py:392–403,444–454` | bounded-beam 评分额外含边界数、门数、门列表位置×5、region_size²、physical load、covered 奖励；beam 剪枝也用此评分 | 改 λ 同时改节点式 (2)、region 评分、搜索空间剪枝；不能说只消融式 (2) |
| `cut.py:361` | constrained 调用节点图时不传 r_available | 所有门都被当作 R 可用施加深度/扇出项，和非约束路径不同 |
| `flow.py:378` vs `:387` | constrained cover 不按 R 集合删门；weighted 旧路径传 r_available | 切路径同时切 R 可用性语义，必须单独冻结政策 |
| `flow.py:388`；`cut.py:297–318` | `critical_first_default=True` 使 λc=0/1 都可插 cover 并排首位 | 旧 §7“λc=1 不触发 cover”不适用于当前入口 |
| `cut.py:292,670–678` | 旧 weighted 池混入 fixed/random/size/critical；旧去重按 method | 未显式禁用会测到备用来源；同一门集可能重复 |
| `flow.py:378–382` | constrained cover 若已在枚举结果中，以 canonical hash 去重后不再前置 | cover 来源重叠会改变优先级，不能仅看有没有 method=cover |
| `real_wns.py:860–862`；`flow.py:611–615` | r_available 仅按传入 active_critical 实例计算 | 若主张“锥内 R 可用性”，应计算全部锥门；不能把非关键但可 R 的门误当不可用。若保留旧语义，须准确记录其域 |
| `real_wns.py:655,735,2049–2068` | TOPOLOGY 默认打开且独立于 R/G/B filter | 必须显式关 TOPOLOGY 和 S；只写 `strategies=R,G,B` 不足 |
| `real_wns.py:1978–1982` | 先按关键路径顺序选门，再截 `max_instances` | Cc 全路径窗口并不保证全部门可被枚举 |
| `real_wns.py:2078–2091,2132–2134` | JOINT 另由 `joint_k` 或 enumerate_depth 生成 | 必须冻结两开关；joint_k=2 不等于枚举所有二门组合 |
| `real_wns.py:2282–2327` | 多 worker 会先评价全部 jobs；串行才使用 first-improvement early_stop | 主臂 workers=1，不以线程结果顺序替代候选策略顺序 |
| `real_wns.py:1245–1248`；`flow.py:1196–1218` | cache hit 复制旧 sta_provenance；旧 B(k) 仅按 provenance 过滤 | provenance 不等于此次真实启动，旧提取方式可多计缓存命中 |
| `real_wns.py:1434–1462`；`SearchState.reserve_budget` | 每次实际候选 STA 前预约；超时仍消耗调用机会 | 应以真实 launch event 构造预算和 B(k)，记录预约/启动/完成三数 |

**已跑静态探针：** 自造六门 DAG g1→g4、g2→g4/g5、g3→g5、g4/g5→g6，critical=[g1,g4,g6]，R_available={g1,g4}，其他 λ=0。旧 nonconstrained 路径在 λc=0 和 1 下都把 cover=[g1,g4] 排第一，且同时保留多种旧 baseline；constrained 路径 cover=[g1,g4,g6] 被区域哈希去重，λc=0 时处于第 5 位，λc=1 时处于第 1 位。该探针只证明开关/门控混杂，不含时序测量。

## 3. 最小有用臂矩阵

接受主线拟定的 Full/Cw/Cc/UniformFull/Full-random/LegacyMatched，但要区分两个层次：这组足以估计 **Full 内 cost 的条件效应** 与添加来源的系统总效应；若要声称 **cost×cover 的交互/协同**，须再加 UniformCw 完成 2×2。建议保留该一臂，避免结果出来后才发现主张无法回答。

| Policy | Cw 来源 | Cc 来源 | Cw 节点代价 | 来源/边界顺序 | 作用 |
|---|---|---|---|---|---|
| W0 | canonical s-t | 关 | 每门=1 | 稳定 canonical tie-break | 等权 mincut；不是“无选择” |
| W1 | canonical s-t | 关 | 式 (2) Full | 同一 tie-break | W1−W0 隔离 Cw cost 总效应 |
| U0 | canonical s-t | 开 | 每门=1 | 同一预锁 fusion policy | 等权双来源 |
| U1（Full） | canonical s-t | 开 | 式 (2) Full | 同一预锁 fusion policy | U1−U0：Full 中 cost 条件效应；U1−W1：加 Cc 总效应 |
| C | 关 | 开 | 不参与 Cw 生成 | 同一实例化/动作顺序 | **最强反证**：U1 是否真的需要 Cw |
| UR | 与 U1 完全相同 | 与 U1 完全相同 | 与 U1 完全相同 | 仅打乱去重后的边界序，种子1/2/3 | 同来源池下的顺序控制 |
| L | legacy_constrained 原路径 | 原 cover 策略 | 原默认评分 | 原分支，参数匹配 | 当前实现强基线；仅用于系统比較 |

主矩阵共七种 policy；UR 三种子时为九组×八电路=**72 次运行**。若省 W0 为 64 次运行，应在预注册中删除交互估计，不把“Full 优于 UniformFull”扩写成任意状态下的 cost 增益。

**重要因果边界：** 切源必然改变可达门、R/G/B 数量及可构造 JOINT 集合。保持的是 *实例化器与动作规则*，不是每臂逐候选集合完全相同。因此 U1−W1/U1−C 是“来源→窗口→动作机会→迭代路径”的总效应。W1−W0 也包含 mincut 门集变化，是 cost 选择机制的总效应。只有 UR−U1 能在同一个网表 epoch 内归因为评估顺序；接受不同候选后网表、关键路径和以后候选池自然分岔，这是顺序策略的下游效应，不应强制拉回同一路径。

## 4. Full 到底如何融合

**建议本轮先使用显式 `cover_priority=first`，将它准确称为“双来源、覆盖优先顺序”，而不是发明一个为了消融而设的新加权融合分数。** 这是已有策略的可控版本，也使 UR 能反驳其顺序价值。λc 的深度折扣只进入式 (2)，cover 来源和优先级由另一个独立开关控制；UniformFull 关闭所有节点特征，但保留完全相同的 cover 开关与优先级。

原因：原 `sum(cost)` 排序天然对多门 Cc 比单门 Cw 更不利；若直接以此为“融合”，可能只是在压制 Cc。临时改成平均 cost、归一化 coverage 或另加奖励，则是新算法设计，不能当成旧机制的消融。若主线决定采用新 score，应先完整冻结公式、量纲、聚合方式、系数和 tie-break，并把同池 cover-first 加为强顺序基线；不能查看 EDA 结果后在 score/cover-first 间选择。

cover-first 也可能令 cost 从未进入有效评价：**若 C 臂和 U1 相同，或者全部接受均来自 Cc、Cw 从不启动新 STA，则“cost 无被检验机会/没有增量贡献”是应保留的结论。** 静态阶段应确认两来源存在不同动作机会，不要求人为调优让二者轮流接受。

## 5. 同一数据生成过程必须控制的功能范围

固定 `weighted_st` 的 source={weighted,cover,full}，显式禁 fixed/random/size/critical 旧来源；等权只改变节点容量，不改 coverage 来源、去重或动作排序。Cw 与 Cc 重合时一个 canonical 区域保留多来源 provenance，不能靠 method 字符串删除身份，也不能执行两遍同一动作。

所有主臂冻结 R/G/B/JOINT（R 的跨功能族规则不变），joint_k=2、joint_enumerate_depth=0，S/TOPOLOGY=false，proxy_ranking=false，adaptive=false，failure_feedback=false，TNS-aware=false，physical_gate=false，workers=1、串行 first-improvement 与一轮一提交，20 轮及 max_patches 相同，缓冲类型、max_instances、锥分治上限、checker/backend、epsilon、面积/电气约束一致。策略优先表最好不使用学习表；如需使用则冻结一个相同哈希及来源，不在各臂分别归纳。

R 可用性政策须单独记录：Full 的式 (2) 按完整当前锥 R_available 门控；Cc 建议保留锥内所有关键组合门（G/B/JOINT 可以修改无 R 门），而不是把 R 可用性当成所有动作的硬合法性。它不是让原实现偷偷变化：C′ 明确属于独立 policy；L 保持原语义并单独标注。

**max_patch_ratio 不直接等于窗口比例。** `_eval_one` 当前用单动作 changed=1、JOINT changed=len(pin_map)，TOPOLOGY 才按窗口门数；15% 阈值仅在 strict_gates 时实际检查（`:1743–1746`）。所以 Cc=allcritical 不因窗口大必然被拒；但小电路二门 JOINT 的 2/N 可能超过15%。须在最小网表上先探针，所有臂同阈值，不得只放宽 Cc。strict boundary 对每个实际候选网表检查声明/消费网/驱动闭合，不能仅以窗口较大断言会通过或失败。

## 6. 必跑静态 probe（无 EDA）与启动门槛

| Probe | 最小输入与断言 | 失败时处置 |
|---|---|---|
| P1 政策路由 | 6门 DAG × policy，记录真实函数入口；weighted_st 绝无 constrained/legacy source | 修路由，不启动 EDA |
| P2 Cw 求解效应 | 能构造等权与 Full 产生不同合法 mincut 的 DAG，并验证割容量/边界；另保留等权与Full相同的端点退化例 | 前者查代码；后者作为合法无效例，不能删 |
| P3 深度与 cover 分离 | λc=0/1 不影响 cover 产生与优先级；cover off 不残留 covered奖励或强制关键锚 | 修独立开关 |
| P4 R 门控 | critical 含无R但可G的门，另含非critical但有R门；验证完整R集合、Cc不误删G门 | 修统计域/政策 |
| P5 重叠去重 | Cw=Cc、不同source相同门集；canonical一次实例化、来源保留两者；无method重复评估 | 修去重/来源账 |
| P6 排序可辨识 | U1/UR 在同epoch的边界与动作全集哈希相同，仅顺序不同；shuffle 发生在截断前或显式只测已选池顺序 | 若池不同，禁止称纯顺序对照 |
| P7 动作作用域 | fake库+网表确认job的改单元都在允许窗口，max_instances截断、joint_k2、无S/TOPOLOGY、无隐藏全关键路径fallback | 修实例化器或记录受控限制 |
| P8 预算/缓存 | monkeypatch STA 为计数stub；K=0/1/2；每种budget拒绝、cachehit、超时/异常分别测试；launch≤K | 修真实调用计数 |
| P9 曲线合法性 | 正WNS但hardgate拒绝、cachehit带旧provenance、超时无WNS；均不得提高合法B(k)或新增STA序号 | 修曲线数据源 |
| P10 提交与缓存key | fake-evaluator首个可接受job后立即返回；新网表hash/newepoch；同候选在不同base不能误用旧cache | 修状态同步 |
| P11 安全阈值 | 小网表N=10/20的单门与2门JOINT，验证F3只按实际改单元；B新网完整声明/驱动闭合 | 根因解释后统一设定，不按臂放宽 |
| P12 全链配置 | CLI→evaluator→flow→cut完整有效policy/五权重/预算，run_config哈希与实际对象一致；保存default模式回归快照 | 修漏透传/兼容默认 |

P2 要证明实现具备改变候选的能力，不是要求八电路都改变。P6 应区分仅打乱外层边界与同时打乱动作顺序，后者会混入策略优先级效应；本轮 UR 建议只打乱外层边界，实例内规则固定。P8/P9 使用 stub，不调用 Yosys/OpenSTA；当前唯一已执行 probe 为 §2 所记的六门旧路径探针，其余未运行。

## 7. 预注册判据和证据产出

先固定八个 ISCAS89 完整实例及基线 mapped netlist/Liberty/SDC 哈希、版本tag、policy、全部配置与种子。主资源为**每电路最多500次新候选STA启动**，超时计入已启动；初始baseline/最终独立SEC另计，cachehit与前置拒绝不计。20轮是第二个共同上限，必须同时记录实际停止原因，不能将“相同预算上限”写成“相同调用数”。同臂冷缓存、全臂统一是否使用运行内memoization；不要跨臂共享热cache。

`B_valid(k)` 定义为截至真实launch序号k，当前策略可接受/已提交的合法网表相对初始基线的最大WNS改善，至少含基线0；不把功能/结构/F3/F5硬失败候选的正WNS收入主曲线。另可保存未过滤的测量最佳值作诊断。记录每launch的base hash、candidate hash、source集合、region hash、动作kind、合法性、cached/launch_seq、budget used、测量值、接受/提交hash、时间及stop_reason。

在跑前固定预算检查点（建议50/100/250/500）、配对差值、首次合法改善和总搜索时间；不足检查点的自然耗尽实例显示真实停止位置和停止值，不伪造调用或延长曲线当新测量。比较各策略在共同预算上限内的最终合法收益时同时给实际N；不可把自然早停当成丢失实例。无改善的首次收益时间是未达到，不能填0或只计算成功电路均值。

旧 R11 用族 D random 极差作为 C′“噪声带”不可沿用：不同运行器/policy的随机变化不是新族的误差模型。UR在C′自身预锁三种子；确定臂报告逐实例配对结果与实测差异，样本仅八电路时不把任意“≥6/8”门槛称为统计显著。预锁主反证顺序：**U1 vs C → U1 vs U0 → W1 vs W0 → U1 vs UR/L**；全部臂和种子完整报告，包括Full变差、零作用、单实例优势及cost未触发的情况。

最后必须检查“声称双来源融合发挥作用”是否真有不同来源的新STA/接受机会。若没有，先按层次归因：路由/透传/计数bug → 固定配置的窗口退化/优先遮蔽 → 方法在该范围无增量；不能用未被调用的来源否定算法，也不能在确认无增量后改policy追求正结论。
