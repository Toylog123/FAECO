# 未决问题 — r30物理数据集构造进行中（2026-10-24/LOG-20261024-11）

r29只读咨询补记（2026-10-19）：研究价值/期刊判断未关闭任何科学OI；优先检验简单覆盖/常规关键实例贪心与完整法、相容强外部的统一预算对照，目前只是建议，未授权新实验。r28稿件交付保持，咨询报告见paper/zh/review_rounds/r29_20261019/VALUE_AND_JOURNAL_ASSESSMENT.md。

当前状态（2026-10-25/LOG-20261025-27）：r30 **物理（post-route）数据集构造**进行中——评价口径不再用理想线网，改用真实 post-route。噪声底 σ_w = 0.023322 ns（95% CI 0.018886–0.027302，8 电路 / 47 配对；**组内=噪声底、组间=信号**；**按族分带**——ISCAS89 用本族值、ITC-99 用本族值，跨族池化值 0.028642 ns 不用于判定）；候选级物理标签覆盖 ISCAS89 全族并**新增 ITC-99 族**（含本族第二物理实现 F1 批）；实现敏感度已**分解**为随机部分 0.0278 ns（候选级判定用，为本族 σ_w 的 1.19 倍）与每电路**系统偏移** -0.090..0.030 ns（整体平移**累积**增益，第 2 节须单独标注）；反事实接受分析 GAIN/REGRESSION/INCONCLUSIVE = 8/1/17（候选级带 11/0/15），即已标注的接受决策中有 **1 条**（噪声底族带）/**0 条**（候选级带）被物理证据判定为**退化**——**理想线网的接受判据并非被物理证据完全支持**；另有多数落在噪声带内**无法确认**。批次进度：F0 338/338、F1 56/56、S713R 30/30、F1S713 7/7、final 8/8、ARCHF 16/16、PLACED 338/338、PLACEDF1 56/56、PLACEDS713 30/30、PLACEDF1S713 7/7、I0P0 58/58、I0 1207/1207、I1P0 58/58、I1 1207/1207、IPLACED 1207/1207、IPLACEDF1 1207/1207、main 64/64、itc99 42/42、r4lo 16/16、patch2 33/33、patch3 3/3。**未改论文、9图、`code/`；未提交**——HEAD 仍 f761ee1996a83fc4f0f3de0999b74d85a8237858（== origin/main），`code/` clean。四partial/D28/56raw3/8/OI051及HEAD锁保持。**判定带已落定**：作用域 `full_family`，布线后候选级 2σ = 0.049752 ns（预演值 0.050419，差约 1.3%；LOG-20261024-23 的定性结论全部兑现）。**候选级结论（LOG-20261024-24）**：图特征在 `resolvable`/`harm` 标签上 0.432507/0.499071（低于或接近随机），仅在 `gain` 标签上为 0.698248；**但那不是候选级信号**——池内读数下平凡基线 `kind_only` 0.555062 与最好的图特征集 0.561297 持平，即"图结构无候选级物理信号"成立且更强；真正可用的是**便宜的布局后档当监督**与**按池排序验证预算**。**接受判据的物理选择性（布线后，最终带）**：接受集真实增益/损害/惰性 25.00/6.82/68.18，拒绝集 3.31/35.07/61.62，增益富集 7.5593、损害比 0.1944 → "避害更强、增益有限"，**"接受了 N 个候选因此改善了 WNS"仍然不能写**。**三点曲线的累计口径已修正（LOG-20261025-27）**：ledger 的 `metric_references.setup_wns` 是**迭代基线**网表的理想 WNS、不是电路基线的 → 训练表的 `ideal_cumulative_wns` 其实是**边际量**，三点曲线的 CUMULATIVE 块三档混用了口径（ISCAS89 侧甚至给出 ρ = -0.1251 的负相关）。修正后：ITC-99 累计 ideal mean -0.046184 → 0.028613、ρ(理想,布线后) 0.5150 → 0.8769；ISCAS89 累计 ideal mean -0.033354 → 0.179815、ρ(理想,布线后) -0.1251 → 0.9461。**已发布结论全部建立在 marginal 块上、逐位未变**（对照遍 114/114 通过）。**结论改述**：理想线网的问题**既不是「高估收益幅度」也不是「把方向说反」**（边际口径斜率 0.9627 / 0.9572，几乎不衰减；累计口径斜率 > 1、ρ 强）：**真正的失效是「改善幅度落在物理噪声以下、不可分辨」**——44 个接受决策里 84.09% 低于布线后判定带 0.049752 ns、34.1% 理想增益恰好 0.00 → **「理想线网说谎」必须改述为「改善大多不可分辨」**；多轮 ECO 的**累计净效果**上理想线网的预测反而很强。**判定带不是唯一值（LOG-20261025-28）**：F2（第三个布线实现）批 1207/1207 收齐，三个两两实现敏感度带 **F0/F1 0.049753 ns（= 已发布用的族带）/ F1/F2 0.045540 ns / F0/F2 0.033706 ns**，**max/min = 1.476087** → 按 LOG-25 **开批前**写死的判据，**C1（可交换）不成立、C2 成立**（可交换夹具 1.028124、相关夹具 1.718223）：**实现敏感度由物理轴驱动**（两轴皆差的一对带最大）。**C3 也不成立**（均值挑选器 27 胜 / 92 平 / 25 负，p=0.8899）→ **「跑两个实现取均值降噪」在本族没有数据支持**。**已发布结论全部存活**：F1/F2 带与 F0/F1 带在 Δ 量化到 0.01 ns 下**完全等价**；最小的 F0/F2 带把 resolvable 434→500、gain 48→65、harm 386→435，但接受集真实增益 25.00→27.27、惰性 68.18→65.91、增益富集 7.5593→5.6975、损害比 0.1944→0.1729、`structural` 池内 0.540114→0.516203 → **没有任何结论翻转**，且**已发布用的 F0/F1 带是三者中最大、也就是最保守的一个**。**须改述**：凡引用「判定带 0.049752 ns」必须写明用的是 **F0/F1 这一对**（族带定义不变，另两对是诊断量）。**GNN 编码器级裁决（LOG-20261025-29）**：LOG-24 留下的边界（"标量摘要不是 GNN 编码器，负结论不能替 GNN 背书"）**正面关掉**——环境无 torch/dgl/sklearn/scipy，用 **numpy 手写 2 层消息传递 GNN**，反传先过**数值梯度校验**（最大绝对误差 0.000）；图数据此前从未生成过，先沙箱预演再全量（ITC-99 **1207 图**、ISCAS89 **339 图**，两次提取重跑 SHA256 逐字节相同）。**留一电路协议、基线取自项目自己的工具**：池内 AUC `kind_only` 0.555062、`structural` 0.540114；GNN 四档——传播+改动单元读出 0.479242、全局读出 0.495365、**不传播** 0.523367、**去单元类型嵌入** 0.508663 → **没有任何一档超过平凡基线**；**消息传递没有带来任何好处**（点估计 0.479242 < 0.523367，配对池符号检验未达显著）；**去掉单元类型嵌入后归零**（0.508663 ≈ 随机）→ **GNN 唯一用到的信号就是改动单元的类型（≈ kind）**；「不传播」一档池化 0.612254 高于 `kind_only` 的 0.538238 但池内更低 → **优势是池间/电路间的**；空标签对照 0.454474、随机初始化探针 0.554609 均在随机附近；**所有配对池检验 p > 0.28** → **GNN 与平凡基线在候选级统计上不可区分**。**须改述**：LOG-24 的「图结构无候选级物理信号」**不能再被读成「标量摘要不够好、也许 GNN 行」**。**未决**：超参事先固定、未做嵌套选择、样本仅 1117 行 / 7 个小电路 / 54 池、只在 ITC-99 做 → **「更重的调参下 GNN 仍无空间」尚未被证明**。**F2 带支撑混淆审计与 LOG-28 判决更正（LOG-20261025-30）**：追查「F2 批在部分电路上与 F0/F1 逐候选完全相同」时发现**三个两两带并不建立在同一批电路上**——F0/F2 在 b02/b08/b09/b13 上与 F0 **逐候选全等**（349/1200 对）、F1/F2 在 b10 上与 F1 全等（216 对）；而 `compute_band()` 池化为 `sqrt(Σ(n_c−1)·sd_c²/Σ(n_c−1))`，**sd_c 恒 0 的电路只进分母不进分子 → 稀释带**，且三个对的稀释量各不相同。**共同非退化子集只有 b01／b03**，其上 F0/F1 0.040078、F1/F2 0.041550、F0/F2 0.035406、**max/min = 1.173530**（落在预注册判据的 INCONCLUSIVE 区 [1.10, 1.35)）。**判决分层**：**C1（可交换）不成立在所有口径下都成立**（全族 1.476087、共同子集 1.173530、各对自己的支撑 1.260455、留一电路 1.218976–1.758842、以电路集自助 CI95 [1.145302, 3.273719]、仅 0.0051 的重采样落到 1.10 以下）；**C2（相关夹具量级）不成立，撤回**；**「实现敏感度由物理轴驱动」的机制归因也撤回**（共同子集上 F1/F2 0.041550 > F0/F1 0.040078 > F0/F2 0.035406，**只差一轴的 F1/F2 反而最大**，全族排序是稀释假象）。**已发布结论不受影响**：族带定义与数值不变（F0/F1 = 0.049753，该对**零退化电路**，既未被稀释也无支撑冲突），LOG-28 的「带敏感性无结论翻转」是门槛敏感性陈述、不受影响。**新发现（可保留）**：第三个实现**部分退化**——单轴 pin 层变化在 4/7 电路上让 **布线数据库逐字节相同**（日志行级差分 + **恒等指纹 全部成立 精确成立**，已排除「作业没真跑」）→ **族带是单轴实现敏感度的上界**，不是它的无偏估计。**C3 机制定论（LOG-20261025-31）**："取均值降噪"在本族失败的符号由**实现等价结构**强制决定（LOG-30 查明 F0≡F2 于 b02/b08/b09/b13、F1≡F2 于 b10 → 两类各 10 格、**违例 0 个**）。**全族平局不是"没有效应"**：真值 = 单实现 picker 的实现 → 平均**显著有害**（-0.006250 ns，-0.625000 量子，p=0.000400）；真值 = 被平均的另一个 → **显著有益**（0.009375 ns，p=0.000400）；三个实现真正互异的电路（b01／b03）上**无可利用收益**（自助 CI95 上界 0.006875 ns ≈ 0.687500 个量子 < 1 个量子 → 不可能改变一次离散的选择）。**OI-052 第 30 条的未决在此定论**：候选级恒等式 `imp02 = imp01 + imp12`（最大偏差 6.939e-18）把 `r(imp01,imp12)` **代数钉死**（该相关系数不携带独立信息），有信息量的只有方差比 **0.349058**（干净子集）→ **"一度自由度"与"独立噪声"两个假设都被否证**（两轴扰动正耦合、部分抵消）。**须改述**：LOG-28 的"C3 不成立"作为显著性判决成立，但理由改为"**平均在本族有时显著有害**"→ **"多跑一个实现取平均"不得作为实践建议**。**单轴带与判定带的量子格（LOG-20261025-32）**：竖轴（F0↔F2）**0.039884 ns**、横轴（F1↔F2）**0.050272 ns**、全族双轴 **0.049753 ns**；**同口径**（b01／b03）上双轴 **0.040078** < 横轴 **0.041550** → **"同时改两个轴"不比"只改主导那个轴"更具破坏性** → 族带是**上界**，但**不是两个单轴带的平方和**。**方法学结论：判决是阈值的阶梯函数**——布线后 WNS 量化到 0.01 ns → 标签集合只由 `floor(band/0.01)+1` 决定；**六个带变体只落进三个标签集合，同格内的标签数 / 分类器 AUC / 接受判据数字逐位相同**（违例 0）。**已发布结论无一翻转**：`structural` 池化 0.445175/0.432507/0.426741 全部远低于 0.5，且**在池化与池内两种读法下都低于同格的 `kind_only`** → "图结构无候选级物理信号"三格下都成立；接受集增益率与损害比三格下形状不变 → "避害更强、增益有限"成立。**带的量子格普查**：pilot_subset band (LOG-20261024-20) 0.087496→idx 9、band-change preview (LOG-20261024-23) 0.050419→idx 6、published family band F0/F1 (LOG-20261024-24) 0.049752→idx 5、probe F0/F1 (LOG-20261025-28) 0.049753→idx 5、probe F1/F2 (LOG-20261025-28) 0.04554→idx 5、probe F0/F2 (LOG-20261025-28) 0.033706→idx 4、single-axis vertical 0.039884→idx 4、single-axis horizontal 0.050272→idx 6、two-axis, common subset 0.040078→idx 5、single-axis vertical, common subset 0.035406→idx 4、single-axis horizontal, common subset 0.04155→idx 5 → **LOG-28"F1/F2 与 F0/F1 完全等价"的真实原因是同一格**；pilot→定稿的带宽收窄其实是**跨格移动**（换了标签集合）→ **报告判定带必须同时报它落在量子网格的哪一格**。**GNN 裁决的加强（LOG-20261025-33）**：**候选级的物理信号并不小，但它不在图拓扑里**——把**理想线网 Δ / 布局后 Δ** 直接当预测器，池内 AUC 两族分别是 ITC-99 **0.875733**（理想）/ **0.907572**（布局后），ISCAS89 **0.852203** / **0.927566**，对 kind_only 的逐池配对 p 全部 ≤ 0.000 → **"图结构无候选级物理信号"只对拓扑成立，对候选级可学性不成立**；换成**连续目标**（布线后边际 Δ），拓扑标量摘要与 GNN 编码器的池内 Pearson 只有 0.136468 / 0.151648（ISCAS89）、0.119288 / 0.141438（ITC-99），oracle 是 0.689507 / 0.901113。**跨族复现**：ITC-99 对照遍**逐位复现** LOG-29（kind_only 池内 0.555062、structural 0.540114、gnn_mod 0.479242、gnn_global 0.495365）；**ISCAS89 上 gnn_global 池内 0.653625**（对 kind_only 配对 p = 0.049，**标签置换经验 p = 0.012**；留一池 0.114934–0.173757、留一电路 0.090867–0.185020，**均不变号**）→ **族特异**。**口径纠错（本轮最可移植的一条）**：工具的 C2/C4 对照跑的是 `readout=mod`，与被检验的 `global` 不匹配 → 补跑**架构匹配**的对照 **C2-global 0.503974** / **C4-global 0.565744**（阈值 0.53 未改）；**H1 四条件在两种口径下都未触发**，但**这不是信号被否证**——C4 是在**真实标签**上训练的探针（mod 0.531432 / global 0.565744，**本身高于平凡基线** 0.517298），**"< 0.53"这个门对带信息的架构不可满足** → 登记为**判据缺陷**（OI-052 第 39 条），**不据此改门、不据此宣称否证**。证据：`project_docs/evidence/r30_gnn_cross_family_20261025/`。**接受判据搬到布局后档的决策级反事实（LOG-20261025-34）**：把 ECO 循环的接受判据从"理想线网边际 Δ"换成"布局后边际 Δ"（便宜约两个数量级），在**决策级**（不是候选级）量一次能挽回多少物理收益。判据在跑之前写死；符号口径的更正**保留原预注册不改**、另立有独立证据的附记（ledger 的 `improved` 标志与非零 Δ 的符号 ISCAS89 27/27、ITC-99 74/74 一致）。**结果**：H1 两族**均未触发**（ISCAS89 1 胜 2 负、p = 1.000000、挽回 0.0556；ITC-99 8 胜 5 负、p = 0.581055、挽回 0.0732）——**但"未触发"不等于"布局后档更差"**，D1–D8 把它拆成四问：**尺子坏了吗**（D3b 正向对照：随机合格候选 vs 布线后 oracle，两族 100.0% / 100.0% 的种子 p < 0.05 → **有分辨率**）；**奖池存在吗**（D6：oracle 显著优于理想判据，7/0 p = 0.015625 与 20/0 p = 1.907e-06 → **存在**，但每决策只有 0.0129 / 0.0152 ns）；**现有判据本来有用吗**（D3：随机合格候选 vs 理想判据，ITC-99 只有 6.5% 的种子显著 → **理想判据本就在机会水平附近**）；**钱去哪了**（D7：布局后 Δ 是**显著更好的池内排序器**——Spearman(判据, 布线后 Δ) 0.6440 vs 0.3992，配对 9/1、p = 0.021484——**但判据只读 argmax**，分歧 14/27 个决策的布线后收益差全在 ±1–2 个 0.01 ns 量子里）。**结论分层**："不用理想线网"的诊断方向是对的（池内排序能力显著提高），**但本轮未观察到决策级收益**；真正缺的不是"换哪一档"，而是**有分辨力的判据**与**足够大的决策级奖池**（可评估决策只有 14 / 27 个）→ 下一步先补**标注覆盖度**。**最可迁移的一条：候选级代理更好 ≠ 决策级策略更好；池内整体排序变好 ≠ 顶端选择变好。**证据：`project_docs/evidence/r30_placed_selector_20261025/`。**数据链缺陷：理想档"未测量"被当成了"标签为零"，已分开（LOG-20261025-35）**：候选级物理标签族在 ledger → 数据集 → 训练表的链上**静默丢候选**：构建器只从 `acceptance_evidence` 取理想档读数，而**从未产生接受决策的 trial 不带该字段**（ITC-99 310 / ISCAS89 25 个）→ 理想档被静默留空；三点曲线再按"理想档为空"丢弃它们，**连同其真实的布局后/布线后测量一起丢掉**。**第一版补丁（回退到 ledger 的 `trial.wns`）已被本轮自身推翻并回滚**：该值在 310/310 上**恰好等于迭代基线**、0/310 有 STA provenance（对照 3734/3734 全有）、失败于 STA 之前的 F1/F2 硬门 → 是**基线占位符**，回退等于**伪造"理想档恰好无影响"**。**诚实修复**：理想档**保持为空** + 新增 `ideal_label_status` 与 `ideal_wns_placeholder`；三点曲线**不再丢弃**有真实物理档的候选；新增 drop 普查产物。**实测**：ITC-99 训练表 **0 冲突**、76 行由空变有；ISCAS89 0 冲突 0 填充；**理想档样本量不变**（1161→1161）→ 理想档统计与两个判定带**逐位未动**；决策级判决不变（ITC-99 27 决策、p = 0.5810546875、H1 = False）；下游级联 ISCAS89 **0/23** 产物变动、ITC-99 8 个变动（形态一律"样本 +76、比值微移"，**无方向翻转**）。附带查实一个与本补丁无关的**跨口径陈旧比值**（`band_scope.json` 的 `stored_ratio_in_three_point_curve` 2.933548→1.668075，可由 0.087496/0.029826 = 2.933548 精确复现）。**扩面可达性探针**：5/12 可达、7 超时不可达、0 未跑完（**"未跑完"≠"不可达"**）；扩面约 1321 作业/档、90.97 h 串行或 22.74 h @PAR=4，可评估决策上界 29。**本轮已用档案证据重分类（LOG-20261025-38）**：探针的 7 个"不可达"里，**b05 是并发伪影**（2026-08-21 档案用同一脚本、同一个网表**串行**跑 838 s 完成、rc=0、有 final.odb；探针的墙钟带 1.22–2.11 倍并发膨胀，且 b05 的超时发生在 STA 路径报告阶段而非布线阶段），**b14 改判"未证实"**（归档日志有 38493 条路径报告 ⇒ 布线已完成，但 3600 s 仍砍在报告阶段），**b15/b17/b20/b21/b22 才是真物理上限**（死在详细布线，无任何路径报告）；因此**可达 = 6 个**（含 b05）、**未证实 = 1 个**（b14）。**扩面口径同时修正**：既有 7 电路的标注池是**全量 distinct 候选**（1193 个哈希与台账逐电路相等，missing=0、extra=0），故**主池 = 全量池 = 1393 作业/档**（与既有 27 个决策同口径），**对照池 = 合格候选池 = 389 作业/档**（省 3.58 倍，仅作敏感性对照）；成本按档案**串行**秒数重算：主池 ≈ 69.97 h 串行 / 17.49 h @PAR=4，对照池 ≈ 25.96 h 串行 / 6.49 h @PAR=4，**决策上界 35 个**。证据：`project_docs/evidence/r30_dataset_label_status_20261025/`；**扩面批 v3 的设计依据已用实测锁定**（并发只改墙钟不改标签、对照池是纯复现、成本口径以实测替换原估；试点真实 rc 分布为完成 12 / rc=0 10 / rc=124 2，慢组按电路调 PAR=1 且布线后上限 3600 s）见 **LOG-20261025-41**；**常驻同步门 `PAIRS` 的范围限制已记为 OI-056**（未关闭，待项目负责人决定）。 本轮（LOG-20261025-42/43）：扩面批已换批 v3 并开跑（批 PID 478 / 看门狗 PID 696 / 切换 2026-10-25 13:44:18），全族改用 lite TCL（report_checks -endpoint_count 1000）；lite 与 full 的标签等价性由结构证明（54/54、52/52 代码行各只差一行）+ 标签源证明（成功日志里 worst slack 全文只出现 2 次）+ 族外 b02 与族内 b04 两点实测三重锁定，批首段闸门现场通过（两个被验对象的解析值与打印串差异均为空）；b05 之死定案为 report_checks 路径报告阶段所致，lite 下在试点同参数 10/10 rc=0（92–186 s、均值 128.9 s、日志约 1.65 MB），full TCL 口径的工期与磁盘旧数（298.02 h / 101.5 GB / 每作业 31.4 MB）作废待重算；扩面结果尚未产生，本句不含任何扩面读数。 **扩面批 v3 在跑（LOG-20261025-45）**：批 PID 478 / 看门狗 696 / 13:44:18 切换；试点段 lite TCL 推进中；**「部分完成度绝不出科学读数」已在真实部分数据上实测拦截**（完整性门两模式均 exit 2，决策读数产物不存在）；**LOG-41/42 的工期数字定案作废**（其算法是把 b04 一家的 663.7 s 套到所有键上）→ 实测分电路口径主池布线后 37.51 h、对照池 17.53 h，批实际约 **2 天**而非 12.42 天；**族内判定带无来源**已登记 OI-058 待拍板。
r28图片占幅/字号/布局、灰度/全页视觉/6副本已验交付；main01/02失败原件保历史，无本轮版面待办。仅版面反馈，不新建科学失败或关闭原科学OI。

## r25稿面规则一致性门已修复（不关闭科学OI）

r24接受式漏C′TNS硬门及r25压缩误加“无提交即停”、目标刷新/H且Timing作用域，已按3ea冻结ZIP/真实trace修正；FINAL_EVIDENCE_CHECK对修后双源8最低条件/原R1/R2歧义核查，最终main0c8b/补eb9构建、根全15页视觉、两组各三PDF同步完成。当前PDF主abfa/补626b。稿面表达门已验；原OI026固定池因果partial继续open，不记实验失败/生产修复。临时inner/outer iteration混比的33对象后续STA说法已撤回，MATRIX/launch链计数不受影响；原错误及修正保LOG208–225/证据包。

## r25继承说明（LOG206）

用户授权压缩中文稿/突出主线，细节拟转补充材料；这是写作/结构任务，不关闭r24四partial或任何科学OI。负面结果/限制/证明域保留，不以移出主稿当已解决。无新EDA/production或HEAD更改，D正式28/56/raw3/8与两门源锁保持。

## r24最终响应的四个partial（LOG197；未决必须持续告知）

最终源a234/build05 PDF142ddba6…已15页/9图/18表/14bib静态/根视觉/三副本同步全部完成，FINAL_PACKAGE9e0eba7f/ROOT_VISUALebab6c2e实读，可审阅工作稿已交付；这不关闭以下科学缺口，也不撤销r23 Major Revision。

| 路线图 | 关联既有问题 | 已落实/仍缺 |
|---|---|---|
| REV01 | OI026/核心机制归因 | C′72及实际预算曲线、零权重收益和随机局部反例已入稿；全程固定同一候选池的离线纯排序因果重放未取得，W1/UR仍策略级/可分叉 |
| REV02 | 原创性/外部强基线 | 文献技术归属和逐方法差异已修；相容强外部基线同库同预算直接性能比较未执行，AiTO全文访问边界保留 |
| REV05 | OI035/036及历史恢复 | 新族/证明域/当前输入已分层绑定；历史A/B及B3/C/D/S版本/输入/运行模型或科学恢复门未齐，D正式28/56/raw3/8 |
| REV21 | OI015/新OI051 | 公式/双侧新flat实测24STA已根限定接受；旧共享SPEF扫描未恢复，原raw helper→leaf层级注释生产支持仍open，旧失败5/43partial保留 |

OI049/OI046/P08/四态及其它未决条目不因作者修订关闭。HEAD/codef761与D完整56+全部8包rootpost锁保持，本轮不commit。
## 2026-10-18 r24修订启动（LOG150）

用户已授权中文稿/配图按r23修订，先复用已有证据、缺项再补；22项已按EDIT01–08实质修订并补限定新实验，逐项最终验收/仍缺项待最终响应；既有科学OI不因稿面编辑关闭。A8不重复证明；b17先核端点绑定；C′新族不替旧C/D；图件保零/负结果。D producer56、accepted28/raw3，56+8post齐前HEAD/code冻结不提交；专职记录不自行启动科学任务；LOG167–168根另已批准fresh C′W1/s382成对SPEF正式实验并先登记，worker同网表负控已43partial注释FAILED停于5新STA（LOG171–172/OI051），结果不接受；v2只处设计请求。当前入口已切r24，下方r23完成说明为历史。
v2历史冻结门附带记录（LOG180，LOG181已补审）：原FROZEN2a9清单唯一PROGRESS.jsonl在冻结后append漂移，根脚本停门、未接受；其它artifact根查SHA-size符。保旧manifest/日志并出POST_FREEZE_AUDIT及新最终清单后再审，STA仍0授权。此元数据门不混淆层级注释科学问题，但未补齐前不能称v2冻结全符。

LOG181根限定接受补记：ROOT_ACCEPTANCE76225a8a…实读，仅接受完整守恒及2SEC的flat派生输入，finalmanifest360ab10f…68件/POST_FREEZEa80e9b09…已根核符；不接受raw层级SPEF支持或物理效果，OI051仍open。STA仍0授权，必须另登记新设计。

LOG186新派生物理数据准入补记：ROOT43ccd357…根全验194件/16API/8annotation后只接受flat pair简化负载测量，u10改善0.11/u40-u160零，已EDIT07入稿。此不是原raw层级支持修复，OI051继续open，v1失败43partial和5STA保持；新24实际STA另计，不恢复旧scan。

## OI-051（2026-10-18，open）— 新成对SPEF层级helper到叶实例端点覆盖不完整

关联OI015的物理证据有效性，但不是OI046的inout/三态问题。r24 fresh C′W1/s382原始层级输入同网表u40控制（DESIGNf212e784…/root批准b2a03636…）实测4API+1annotation replay共5新STA后，在14.238s因43 partially unannotated（0完全unannotated）按预注册门停止；DFF_N:D模块端口与DFF_N/_0_/D叶端点不闭合。FAILURE.json已实际回读，annotation stdout/return原件保。ideal及SPEF两侧delta都0不能替代0partial门，相关物理WNS不接受作效果。

禁止按库名删网/丢43告警求绿，不将新gap归到旧OpenROAD A物理族。源pin终验已STOP_AUDIT03b306f5…确认HEAD/源/Lib/两输入前后稳定（LOG173）；不因此提前修production/code/HEAD。根最初仅要求v2设计，LOG175已批准第一二阶段2flatten+2SEC，STA仍0授权；flat规范化将是新数据输入族，须新SHA/证明/预注册、负控先行与完整注释门，不能改称本次失败恢复。旧实验失败原件持续保留，用户须获知此未决。
### r24取证关联：B模型域及实现公式（LOG153）

沿用OI035/036与既有B模型域问题，不新设重复OI。记录员已实际回读`project_docs/evidence/r22_b_model_audit_20261016/audit.json` summary：prior_complete_proofs=28，其中23无used-model defect，5为b09/b20/b21/picorv32/picorv32_pcpi_mul；旧28份仅记录model路径而非runtime hash，不能伪造历史runtime身份。根报告Pico两对象已有新证明、b17唯一raw候选已有新证明和accepted_object_binding，仍须将端点与全19时序观察/功能支持域分层；三态b09/b20/b21须unsupported，不能直接把ITC正文18/19写19/19。LOG161–162已完成QUANTITATIVE4eb77b24…静态19/16/3分层及b17直接端点绑定：16支持域strict15/16、mean0.208125，三态3仍unsupported且时序观察保留。旧28份模型runtime hash未恢复的身份限制持续保留；不是新SEC或历史身份全闭。

方法worker发现cover-first、lambda_c及SPEF公式与正文存在实质差异；详细实现行号/参数报告METHOD_EVIDENCE.md/JSON已交付（LOG159），根已用当前JSON b0eff5f4…绑定EDIT02方法正文，编译/完整验收仍待，关联OI026及既有方法/公式项。先取证再改定义，不用措辞弱化或跨族补证据代替修复。均为只读实查，非新增科学实验。
## 2026-10-18 r23审稿关联更新（不关闭既有科学门）

审稿已完成Major Revision，22项见`paper/zh/review_rounds/r23_20261018/REVISION_ROADMAP.md`。复用既有OI，不因角色重复意见新造重复问题：

| 范围 | 当前状态/关联 | 后续 |
|---|---|---|
| 核心机制/权重/排序归因 | OI026及既有证据归因项持续open；REV01、REV06–08；新C′已做未写稿 | 分离同族对照与零收益，补可执行定义；不以弱化主张代替设计/验证 |
| 历史结果身份/证明影响 | OI035/036及P08持续open；REV05/09/10 | b17新证据先绑定端点；A8补前提/阶段披露，不误记八份证据依赖弱归纳 |
| 文献与工程解释 | REV02、REV11–22待改稿 | 纠正原始文献技术归属；补网表代价、RC/u(e)/物理设置 |
| D验收/其它实现科学门 | producer56已完，accepted28/raw3；OI049/OI046/P08/四态等不变 | D56+8post前继续锁HEAD/code；当前审稿不执行新EDA或源修 |

工具LF兼容性已定位并恢复，不作为论文缺陷；TeX缩略词工具未运行如实保留，无假通过。


用户10-18明确继续，旧暂停为历史。当前支持域v8实现门及C′v3全72已独立验收，OI035/036历史科学影响、B3/C/D同族恢复、四态与S/SPEF仍开放；OI040/041/042只关闭各自实现门，OI043只关闭时钟元数据门。具体旧尝试与失败持续保留，不把旧阶段运行中当当前事实。

# 未决问题追踪（Open Issues）

> 未解决的问题必须登记于此；**只要未解决就持续保留**，每轮检查进展。
> **未解决的问题必须告知用户，不得隐瞒或淡化。**

## 已决（2026-09-29 用户拍板；选项与依据原文见 `agent_handoff/DECISION_BRIEF_20260912.md`）

| ID | 问题 | 决策 | 落地动作 | 后续 |
|----|------|------|----------|------|
| OI-003 | versions/v1 基线冻结方案 | **A 轻量冻结** | tag `v2026-09-29-submission-ready`（提交 `d84061a`）+ `versions/v1/MANIFEST.sha256`（117 条全 OK 自校验通过）+ `BASELINE_INDEX.csv` active 行；已推送 origin | 期刊若要求证据打包，再按 D-01=B 补 |
| OI-006 | 机制图处置 | **A 维持现状** | 无动作（9 页稿 3 图布局维持，"4 图拆分"问题不存在） | 投稿后视审稿意见再定 |
| OI-001 | DOI | **A 投稿时按期刊模板补** | 无正文动作（主稿无 DOI 占位符） | 已列入 T20 投稿检查单 |
| OI-002 | DRC signoff | **A 维持如实声明** | 无动作 | Magic/KLayout 补跑留作 rebuttal 备选（OI-002 备选路径保留） |
| OI-018 | 1-C（增量 ECO 小节）插入时机 | **留到修稿轮**（用户 2026-09-30 拍板） | 无动作（§12.2 文本继续留待贴；冻结令维持） | 修稿轮随审稿意见一并插入，届时重走质量门 + 重冻结 |
| OI-019 | JCAD Word 转排路径 | **不问邮件、直接转排**（用户 2026-09-30 拍板） | `draft_email_to_jcad.md` 作废不用；按官方 2026 模板启动 Word 转排 | 转排产物见 `paper/zh/submission/word/`；MathType 环节需用户本机配合 |
| OI-020 | 摘要改写授权 | **授权且同步冻结版**（用户 2026-09-30 拍板） | **已执行（v2，2026-09-30）**：中文摘要压至 295 字去第一人称、英文压至 149 词；重编译 9 页 / 0/0/0；重冻结 v2（`v2026-09-30-submission-ready`，新指纹 `43becd39…`，v1 superseded）。**后续同一授权下的可读性改写（v5，2026-10-09）：中 264 字 / 英 148 词，重冻结 v5（`v2026-10-09-abstract-plain`）。再续（v6，2026-10-09）：随文字专项审稿采纳审稿人摘要，中 228 字 / 英 148 词** | 详见 `CHANGE_LOG.md` 2026-09-30 与 2026-10-09（摘要）行 |
| OI-021 | AIGC 使用披露 | **暂缓**（用户 2026-09-30 拍板） | 无动作；检查单保留该必办项 | ⚠ 投稿时必须解决（原按 JCAD：未披露视为抄袭），建议届时与通信作者共同拟定。**2026-10-12 更新**：目标期刊**改投 Integration, the VLSI Journal**（Elsevier）⇒ 须按 **Elsevier 的 AI 使用披露政策**重新核对（Elsevier 要求在手稿中声明生成式 AI 的使用），不可直接沿用 JCAD 口径 |
| OI-028 | **目标期刊由 JCAD 改为 Integration, the VLSI Journal（Elsevier，英文）** | 2026-10-12 | **用户已裁定**（复审四轮；审稿人第一推荐 ★★★★★） | 论文现为**中文稿**（ctexart + lualatex，`paper/zh/`）。改投 Integration 需：① **英文全文**翻译（中文稿作为内容母本）；② **Elsevier 格式**（`elsarticle` 类、英文摘要与关键词、图表题录、参考文献样式）；③ 投稿材料（cover letter、作者信息、**AIGC 披露**见 OI-021）；④ 摘要现为中文 **349 字** / 英文 **214 词**（**2026-10-13 r13 更新**：由 244 字 / 164 词扩为"大背景 → 具体问题 → 方法 → 结果 → 意义"结构）；**原 JCAD「≤300 字 / ≤150 词」规则随改投 Integration 失效**，新约束（Elsevier 常见 ≤250 词，214 尚在范围内）**须在英文稿轮按 Integration 作者指南正式复核**。**审稿人「投稿前必须补」三项**：runtime 表 ✅ 已补（表 11）、baseline 定位 ✅ 已补（表 2 + §2.2）、feature 消融 ❌ 未做（OI-026，2026-10-12 用户裁定**暂缓**）；**★ r11 已定英文标题 `FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO`，中文题同步改为「FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画」，主稿文件（`.tex` + 双副本 `.pdf`）已随题改名并同步 7 处指针文件** | 复审四 `paper/zh/review_rounds/r10_20261012/{comments.md,response.md}`；`versions/v8/README.md`；LOGS `LOG-20261012-04` | ① 是否先做 OI-026 feature 消融再启动翻译（用户已表示可投入新算力）；② 翻译与格式转化的时机与范围（整稿 vs 分章）；③ 是否保留中文版投《计算机辅助设计与图形学学报》作为并行选项（审稿人称其"非常匹配"） | 用户（时机与范围） |
| OI-022 | 3 个证据汇总文件 git add | **维持默认：不入 git，由 manifest 锁定**（用户未改默认） | 无动作 | `versions/v1、v2/MANIFEST.sha256` 均含此 3 文件 |
| OI-023 | 外部「文字专项审稿」（9 页稿）全量落地 | **用户 2026-10-09 授权「全部执行」（P0+P1+P2，约 20–30 处）** | **已执行并重冻结 v6**（tag `v2026-10-09-text-review` = `b1eee25`；论文 tag `faeco-paper-final-20261009c`）：口径修正 / 贡献重组 / 术语统一 / §4.6 主张强度下调并令表 8 算式闭合（0+36+90=126）/ A* 披露按审稿人删除 / 正文去 `\FloatBarrier` 消除末页孤儿（9 页→8 页）；**零数字、零实验、零新增主张** | 逐项处置见 `paper/zh/review_rounds/r7_20261009/{comments,response,README}.md`；未采纳项的驳回理由（图 2 caption A/B 因已烘入 PNG）亦记录在案 |

**附带发现（2026-09-29，D-01 执行时实测）**：`experiments/20260826_aggregation/summary.json`（论文主数字源）、`ablation_summary.json`、`20260826_sec/summary.csv` 此前**未被 git 跟踪**（与决策简报"git 已跟踪聚合 summary"的描述不符）；现由 `versions/v1/MANIFEST.sha256` 锁定完整性。是否纳入 git 跟踪待用户确认。

### 长期教训（跨轮，2026-10-09 r7 归纳；已同步 `docs/EXPERIENCE.md`）

1. **双栏论文正文禁插 `\FloatBarrier`**：`placeins` 的 `\FloatBarrier` 在双栏模式下遇待排浮动体会**退化为 `\clearpage`**，造成栏底留白、正文后移、**参考文献被挤成孤儿末页**。压页/版面异常应优先调浮动体参数，**禁缩字体/行距/砍内容**。本稿 v6 正文已移除（仅保留图 2 后一处用于约束全宽浮动体）。
2. **Word 转排管线含硬编码摘要**：`scratch/word_convert/postprocess.py` 的 `zh_abs`/`en_abs`/关键词/标题/作者为**硬编码**，不从 `.tex` 读取。改摘要后若只改 `OUT` 路径，会产出**旧摘要**的 Word 稿（v5 轮即发生：`…20261009b.docx` 实为 v4 摘要文本）。**改摘要后必须同步硬编码块并重跑整条管线**（preprocess → pandoc → postprocess → Word 导出）。
3. **内容指纹必须用可复现命令、并跨文档回验**：口径 = `pdftotext -layout <pdf> - | sha256sum`（原始输出，**不**去空白；poppler 25.07）。本轮发现 v6 指纹 `91034fee…` 系误值——用 v5 PDF 反推口径（复现 `0a2b0723…`）后，规范脚本对 v6 稳定给出 `88b03403…`，遂更正 11 个文件（含 `PAPER_EVIDENCE_MANIFEST.md` §6、`versions/v6/README.md`、T20 包）。**字节 SHA ≠ 内容指纹**；指纹值跨文档传播时必须回验。

## 待用户拍板（2026-09-29 决策轮新增；**2026-09-30 已全部拍板完毕**，决议见上方「已决」表 OI-018~OI-022）

> 本节保留作为决策过程记录：OI-018 = 留修稿轮；OI-019 = 直接转排（不发询问邮件）；OI-020 = 授权且同步冻结版（已执行）；OI-021 = 暂缓（投稿时必须解决）；OI-022 = 维持默认（manifest 锁定、不入 git）。S2 表述粒度默认"不列具体开关名"。

## 进行中 / 未解决

当前执行锁（LOG139）：D producer56/56完成，但正式accepted仍28/raw3；完整56与8/8archive+rootpost均齐前HEAD/codef761锁不commit。r23本轮仅中文全稿只读审稿，不启动D终验/归档/修源，不提前新增重复OI，等实际报告逐问题登记。

**D28-CHECKER-CACHE-SCHEMA（2026-10-18，closed仅冻结28验收器分型兼容门；LOG116–130）— skipped_duplicate不全是STA重放。** 原v2在s641缺cached_from_seq KeyError失败保。DIAGNOSIS6772089b…只读581来源锁明实际STA缓存/无重放hash去重/前置拒绝差异；v3 f6b053df…保全部rawSTA/SEC/45pin门并明确immutable subset，根设计/code审后执行。RESULT79ad2ce4…/16407来源稳定及ROOT_ACCEPTf14c3306…正式接受冻结28；11169records=5243candidateSTA+5821有launch缓存复用+29hash无重放+76preSTA（cachedreject0），旧宽cache5850=5821+29，不改原schema/结果。

此门闭合不等D全56或科学其它域关闭，extra producer不在28接受内；full56继续v3全key审查并另登记timeout。源/结果/HEAD未改，旧v2/run28v1失败/准备原件保，s420七臂仅按根单例准入归档，不外推s641。

**OI-050（2026-10-18，closed仅A SEC句表/EN布局/副本与metadata门；LOG90–120）— A证明表exact对象/点数/同批计时修正。** 新统一原A8 SEC已独立87b3b721…/根a6caf8a1…接受；11/90/79/124/126/139/146/228全0及实际同批runtime已写双语句表。作者FINALbc951338…/397件、SYNC29a6ee35…/POST2602df5a…、不同ownerFINAL334a893b…/38页实际视觉/63final件和562来源链齐；根ROOT_MANUSCRIPT_ACCEPTANCE472b441b…实际最终accepted，允许仅此门关闭。ZH12页/三PDF同173ae809…，EN v5 26页/current同c2783046…/A图表15-B16/min7.345520pt，4metadata同步。

旧v1-v4/PDF不可写失败/准备checker未另存原件等均保真披露；s820旧137与新139证明构造不同、无最终RTLIL故两额外cell精确身份unknown，不比较pointset强弱。本门不等历史proof影响、D/B3/C/S/SPEF/四态/作者或投稿门关闭；工作稿仍需其它科学恢复。

**OI-049（2026-10-18，open/显式异常注入已复现，待D后修；LOG54/121/125–126）— CEC timeout bytes尾部构造TypeError。** red_v3/RESULT bb5e332b…实际3mockCEC控制：str/empty均正确timeout，syntheticbytes partial在public direct-CEC路径193→215→_tail902 TypeError（join期望str得到bytes），45source/HEADf761前后稳定。范围明确normalization与CEC均mock，非真实EDA超时/OS输出流类型复现，不是proof误pass。

red_v1/v2为harness先假设真实timeout应有非空bytes而在API前失败，不能算生产真红；两脚本保、v2原log保、v1仅tooltrace转写无本地raw原件。原v1 SETUP_FAILURE称未到partial stdout是过度推断，合取assert不区分类型/空，v1/v2实际stream type/value均unknown（新增CLARIFICATION9140b292…、原件不改）。redv3不证明_run_abc_cec/mapped helper均复现，这些仅静态风险。不同owner只读独立FINAL1d89a8a7…/RESULT5cb89699…/72原件稳定/7final件当前SHA核符已接受此窄归因；不重probe/EDA或生产import，非代码修复通过。D完整56与全部8case归档根post齐前不改，D后按此原输入最小修复/局部及整体回归再闭门，不因OI048已修或本次A稿件通过误关异常呈现能力。

**OI-048（2026-10-18，历史top/proof影响open/P0；当前复现实现门closed）— 完整CEC证明对象与输入选择窗口。** 原Verilog库buf首root和mapped BLIF前置dummy两个真实反例曾假pass；ordinary/BOM source-window真红2F、状态错误rc0控制也保原件。当前source/mapped引用图top、状态优先级及prepare前original-source绑定/launch前后核已修，原输入根重放正确fail/error、独立代码/原件review9cbabd66…及全v5/最终独立67da65a4…通过，已f761提交推送；当前复现入口不再是待修/待commit。

P08历史门仍open：当前限定现存15旧CEC的13成功单model/2实际readerror及s27-s820两旧显式equivtop SEC已新checker独立复算，11/0与137/0/A初终-Bstate绑定吻合（FINALe8fa6a29…/109来源稳定），未新增wrongmodulepass；不外推未覆盖/缺失对象。历史candidate附件差异、同期source/BLIF收据缺失仍unknown。原inventory/v1脚本-log精确补齐，但原最终PSstdin/localstdout不可恢复；新checker可复算不是历史原流程恢复。D14当前实际显式top SEC已根与不同owner独立接受，不能将旧API风险外推C′/D新证明无效。

**OI-047（2026-10-18，当前实现门closed；原发现LOG35、验收LOG59–60）— primitive-only CEC整库fallback。** 真实native c17无SKY引用时旧提取器返回整库，引入无关$mul导致error而非pass。精确referenced模型提取/明确empty独立model修复后，native正控、完整v51056pass/174稳定及最终独立67da65a4…验收通过，已随f761实际commit+push。原22P1F/局部红绿等原件保留；当前不是待修/待commit。历史proof对象范围留OI048/P08，timeout呈现另留OI049。证据：r22_s_spef_integrated_20261018/。

**OI-046（2026-10-18，open；关联OI015/LOG27）— b18_light真实inout LOGIC0使物理复验unsupported。** 最终静态报告绑定baseline c5c89e3a…与唯一R候选42db3970…，两者mapped行80均有inout LOGIC0；当前SPEF显式拒双向网，未执行STA/SEC。不能因此判输入非法，也不能把旧b18物理失效归因写全修复。下一步先分析LOGIC0来源、恒定驱动与双向建模/合法输入契约，保全部端点后设计恢复；禁止把inout默改input，禁止丢该网后填有效物理比较。当前新SPEF最小真实pilot先用合法s382，正式源pin前不EDA。LOG30只读来源初查：bench第6行明确pseudo-input，INPUT/OUTPUT同名LOGIC0，两个BLIF亦双角色，预转换b18.v已inout（非本次mapped引入）。原EDIF常量语义unknown，不能凭LOGIC0名字钉0；窄域恢复设计与冻结AUDIT2c3ec37a…/REPORTe38dbafd…已齐，15source前后/current核符。保单P B+4I的外部边界被动RC和8反驳控制仅设计、未实施/测试；完整BLIF与acquisition SHA不同/原转换receipt与EDIF未知继续保留。


| ID | 问题 | 发现日期 | 状态 | 影响 | 尝试过 | 下一步 | 阻塞 |
|---|---|---|---|---|---|---|---|
| OI-045 | S CEC实际派生filtered模型仅记调用后SHA；normalize启动失败缺日志 | 2026-10-18独立反例/LOG25 | 原反例+当前全v5/独立验收通过，输入绑定实现门closed | *_cells.v调用中81→129B漂移仍pass/input_drift空，证明收据未绑定实际模型边界；不等模型函数或真实等价已证错误 | 修前5f7d5cfe…/66+40原件核符；作者4F10P→51P1skip，根ROOT_ACCEPTANCEbcbfdfb1…/56原件/原12输入同，drift非pass及normalize日志齐 | 当前全v5/最终独立67da65a4…已过且f761 commit+push；正式S同族科学对象/配置仍需另登记，OI049异常呈现另留 | 正式S同族科学证据生成（当前源码实现已验收） |

**FIG-R22-MATRIX-GEOMETRY（2026-10-18，closed仅几何实现门/LOG12）**：v1自动六处tick bbox overlap原件保留；最新v3源d9ef05b…/FINAL_REVIEW32ff889a…实核，碰撞0FAIL/0WARN、PANEL_ALIGNMENT PASS、glyph最小6.8pt/60runs低于5pt0、root四panel/整图视觉通过，raw/paired CSV与v1逐字节相同。独立v3视觉71d9a480…已通过，正式主稿整合尚待，不称投稿格式最终验收。

当前冻结复核（2026-10-18，LOG10，关联OI014/OI015/OI036）：历史S/SPEF已冻结独立审计：旧258 filtered模型defect被V2推翻（1032组合条目全match/0mismatch或unknown）；S接受链非法基准混淆负gain和CEC pre/post覆盖、SPEF漏真实Lib输出direction/两侧共享SPEF/报告顺序混杂为下一阶段必修。s382历史RC对1/40当前生成均不全文等，仍unknown；不借b18 unit1或scan对象填补。7231阶段已push，源码修复正在先红后绿；整体回归/独立审查及新源码commit后另clean pin做同族EDA。 S126个base中仅14静态闭合、126候选中10闭合，不能仅凭required pins通过判全合法；126/76/0与36零90负可复算但不能成为S无效结论。当前S关闭/physical关闭的C′不因此失效。

### r22 当前状态：10-18已全72验收；以下10-16阶段叙述保历史（以顶部当前冻结复核为准）

旧钉定代码完整v5=835pass/166来源稳定/PYTHONUTF8=1，但当前v8=969pass/170SHA稳定，OI040/041实现门验收关闭并已push3ea0f75；新pin正式9控制预期符合（3正/3负/2unsupported/1input_error），不是9个等价证明或四态支持。A6实际对象新SEC已补且三态交集空，稿图待；B旧28绑定仍真，但23未见本次used-model defect、5有缺口（B2状态模型、B3三态TE_B）。B2已44d20bb新模型双pair pass（proof/QA/docs已ddb4c33提交）+7/0孤立X身份绑定，rawbytes/完整decoded/artifact/动态cert后验均匹配；旧runtime身份不补造，D56真实CLI预飞56/56仅内存非实验。C′v3已注册且18pilot运行；C′v2仅注册禁执行。OI038/039及B3/D/C科学证据、三态真实支持恢复/稿图仍待。

B17新增恢复：B17_PROOF_RECOVERY_DESIGN.json已实读新common完整模型+flatten/assert真SEC返回pass（13.375s、12879proven/0unproven），源HEADddb4c33/原件稳定；主线POST_RUN_VERIFICATION已完成：原bytes/完整decoded/唯一nor4b尺寸变化/全部artifacts与44source全匹配，12879/0实log成功，producerJSON acaf5f…哈希已核。旧未flatten/NoSATmodel实证不能简写为find_same_wires已证伪阴性。首map.ys CP936预飞读UTF8失败在SEC前；严格CP936保字节SHA后才运行，旧schema无state text/hash不补造。

B3_RERUN_DESIGN与C_RECOVERY_EXTENSION已实际读，均execution_ready=false：历史runtime argv/source/priority等仍有unknown，不默用defaults。B3保B stateful outerloop，不换C逐实例greedy；C十四完整trial/终点匹配只加强recipe见证，不冒称实际argv/runtimepin，canonical s382仍缺。C′v3准备工具仅evidence-only；8例真实prep通过后18pilot已运行，结果不能替代B3/C同族恢复。

当前运行（LOG41）：当前main/origin已push3ea0f75，完整v8=969pass/170源码SHA稳定，OI040/041实现门closed。C′v3同HEAD正式72jobs已注册（manifest SHA72dfbef9…/44source）。真实8例mapping/static prep已completed，wrapper46s/exit0；preflight与PREPARATION_POST_VERIFICATION逐例8/8匹配、source稳定，明确mapping_equivalence=not_run、sta_executed=false：准备不是RTL→mapped等价证明，也不计STA。18pilot（s27/s382×9）已实际启动session91713，整体timeout36000s、每job3900/3930s、PYTHONUTF8=1。18pilot运行日志已18/18 DONE均报告exit0/finalSEC pass，整体wrapper1028s/exit0；最终独立audit待，最后PILOT_AUDIT_07仍7/18，未记录全部后验通过或扩54，source稳定/argv匹配，逐candidate mapped/tcl/log SHA、实际launch、commit完整哈希链和finalSEC非零proven/0unproven均匹配。完整sta.log路径恰为candidate理想记录加初始baseline；resolved physical/electrical/S均false。七例每例baseline实际过程1次，candidate_ideal合计205次+baseline7次=212次已审计STA过程（other0），不是物理STA。W1的s27/s382保留提交2/3次，最终WNS-.18/-.83；其余全矩阵效果与验收仍待。HEAD在完整72jobs全部验收前固定3ea0f75，records只写docs不commit；18通过后同pin扩余54，B3/C ADAPTER提交也必须等72全验收，可继续独立review/QA但不占STA。

当前接受协议为严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不意味着关闭setup_tns预算。W0/s27首候选WNS -.27→-.26但TNS -.49→-.50，被setup_tns硬门拒。零提交/零WNS收益如实保留，不为正结果调参。最终审计分开理想候选、baseline/refresh/physical STA与提交。

### r21 最新同步状态（2026-10-14，以本段覆盖旧行的当前稿状态）

- **OI-024**：Word 转排件仍为 v6，未同步 r8–r21（机制图 1/2、新图 4～7、证据来源/图注/引用）。继续暂缓 Word；r21 为工作修订，未冻结 v19。
- **OI-027**：本轮已验收稿为 12 页/7 图/14 表/21 引用，质量项全零；首版 S 图漂页与末页 balance 溢出已修，改用 flushend[noshrink,nospread]，未缩字号/行距/砍内容。逐页视觉/双副本/作者版同步已完成；投稿格式的最终版式仍留后续。
- **OI-032/033**：b17 批次披露与 D 真实测量计数修复已完成。D 新测量列来自已有原始台账重算，旧记录数保留；不运行新 EDA。
- **OI-030/031/034**：独立机制证据、逐臂配置、其他旧 schema/计数器语义仍开放。B 的 3363/664/104 已确认为评估记录；18 实例新 STA 2890 可识别，b17 旧 schema 缺来源，实际数不可恢复，不能填零或假定 104。

| ID | 问题 | 发现日期 | 状态 | 影响 | 尝试过 | 下一步 | 阻塞 |
|----|------|----------|------|------|--------|--------|------|
| OI-033 | **族 D 缓存/前置拒绝被计为实际 STA 测量** | 2026-10-14（r21 独立复核） | **closed（图、表与单位修复完成）** | 归档 B(k) 保留缓存 provenance；旧4146/4883/5624为评估记录。当前从40原始台账剔缓存/无来源记录重建，新STA Fixed1947/Adaptive2003，随机2439/2476/2527（均值2480.7）；旧数保留为记录列 | methodology_verification、原始eval_trials/唯一报告路径/sta_used交叉核对；主线已重建图5和表11，删除旧预约与实际口径混淆句；构建质量门通过 | 保持当前筛选规则与CSV/来源指纹；不要用归档曲线长度直接估算实际测量，不运行新EDA | 无（本族确定计数错误已修） |
| OI-034 | **历史评估记录/缓存/STA来源分层审计** | 2026-10-14（r21开；r22恢复） | **B/D来源已闭合；C精确执行数不可识别的历史限制保留** | B全部评估3363、b06 664保持记录单位；18实例独有结果2890+b17独有报告恢复104=2994。D计数/真实曲线已修；C跨pass覆盖、缺base hash/完整revision，不能由重复描述或文件数猜完整新增调用 | r22历史审计51s/exit0，b17 104条日志/Tcl逐trial交叉，26240输入/blob指纹；C配置recovered/launcher/inferred/missing分级。主线确认关闭B/D范围 | C精确新STA、覆盖前输入/报告等归为不可识别边界，发布可证实分层计数；完整历史复现仍见OI-031，不反向补造，不阻塞新C′冻结对照 | B/D已闭合；C已知历史来源限制持续保留 |
| OI-035 | **B缓冲插入跨模块错放** | 2026-10-14（r22真实pilot） | **当前支持域实现/全72已验收；历史科学影响open** | insert_buffer曾把新增instance插入helper，wire/pin在top；v1最终门拦截，中间收益无效 | 起点781c031已有模块隔离/B作用域修复；旧667仅历史，当前修复版本整体/真实矩阵验收未完成 | 当前v8=969pass/170SHA及C′72终点非空SEC已验收；B3/C/D等按原族新pin复验，稿图回填，不用C′替代 | 历史同族科学恢复/稿图仍缺；当前C′实现与矩阵不再缺验收 |
| OI-036 | **局部F1/F2 namespace与模型/解析门及历史correctness影响** | 2026-10-14（r22真实pilot） | **当前支持域实现/全72已验收；历史科学影响open** | 全文namespace曾伪pass；K1多输出模型、K2合法conb、K3端点D作用域、K4 assign语义、K5实例唯一、K6 legacy S刷新仍需本轮闭合 | NAMESPACE_FIX_REVIEW及历史REPORT已实读；B已证明对象保留，C代表不外推；恢复起点781c031，不把旧667当新通过 | 当前v8=969pass/170SHA及C′72终点非空SEC已验收；B3/C/D等按原族新pin复验，稿图回填，不用C′替代 | 历史同族科学恢复/稿图仍缺；当前C′实现与矩阵不再缺验收 |
| OI-037 | **族A接受候选SEC对象错绑/缺失** | 2026-10-14（r22历史correctness确认） | **六实际接受对象新SEC全部pass且三态usedtypes交集空；稿图回填待** | 旧8份A SEC gate指原mapped而非accepted；2对象可复用B完全相同初始/final证明，另6未知，不能称已证明 | REPORT/correctness_audit明确对象来源，记录员2026-10-16重读REPORT；本轮frozen六实际对象新证明已六pass，21s/exit0 | 模型/解析验收后，补6个实际accepted对象的来源/模型SHA/独立SEC，再同步A/物理迁移图和双语论证 | 六对象新证明已补齐，两版稿图回填仍待 |
| OI-038 | **B两Pico旧edfxtp模型状态语义缺口** | 2026-10-16（B实际模型审计） | **新模型实际对象缺证已恢复；历史身份边界/稿图回填保留** | 旧model仅Q=IQ且IQ无driver/always，原审计结论保真；不追认旧模型完整，也不补造旧runtime模型SHA | 44d20bb/new_model_proofs双pair真实pass：core6.078s+7X identity、mul0.750s+0X，wrapper16exit0/source稳定；POST_RUN_VERIFICATION原bytes/完整decoded/artifacts/动态cert全匹配 | 将新证明按确切raw/source/LIB/checker/producer绑定回填稿图；限定two-state SEC+孤立constant-X identity，不宣称任意四态或复位等价 | B2新correct模型缺证已补；B3三态另见OI039，旧runtime身份不补造 |
| OI-039 | **三态Lib语义/必需输入完整性缺口及B3历史候选漏TE_B** | 2026-10-16（B实际模型审计） | **open；Z soundness受限，临时unsupported能力门已限定过；CLI fixture全9pass、强Z guard已验证；v4编码失败原件保留；v5完整835pass/4skip/156subtests、166源码稳定，显式全进程UTF8，第二阶段02e82a2已push，新pin正式9项预期状态全符合（3正/3负/2unsupported/1input_error），非三态支持证明，v2禁执行** | b09/b20/b21 actual final与SEC gate中einvn_1/_2漏TE_B；真实Lib three_state(TE_B)被旧/8192193 writer忽略，function-only使普通clkinv可能选到三态cell。仅缺连接/模型实证，尚未新证不等价 | r22_b_model_audit_20261016/audit.json已实读；旧28绑定仍真，23未见本次used-model defect/5有缺口（含Pico2）；旧757和6控制不覆盖新反例 | parser完整pin/three_state metadata和候选联合语义；models RW模型/F1F2必需输入/ABC边界；root最终SEC完整性门。dirty首5控制不能认证Z语义：Zvs0预期fail实际pass、Zvs1fail，source稳定/0STA；只读composition boundary proof设计，暂不改生产。完整v3=822pass/2fail，165SHA稳定；CLI fixture缺dfrtp/RESET_B被正确拒，拟补fixture保留assert。二态cut被Z^Z等反例推翻不实施；actualtri/Z/switch structured unsupported是临时能力门，显式四态编码支持路径open，domain11限定过但v4未开始；新pin后C′v3，v2只注册禁执行。A6三态交集空已核 | 后缀导出已限定187pass、13三态52行静态语义检查；第二批已冻结，即将dirty真Z控制/完整v3，02e82a2新pin正式9控制预期全符合（3正/3负/2unsupported/1input_error），临时能力门核验完成但四态支持恢复open、B3恢复/证明、显式四态支持与稿图仍待；完整v5当前835pass，不升级科学闭合 |
| OI-040 | **顺序单元被当组合R且F1只比IQ导致reset→set伪pass** | 2026-10-16（root合法输入反例） | **实现门closed：精确V3+完整v8=969pass/170SHA稳定；科学边界保留** | dfrtp_1→dfstp_1完整输入把reset改set，F1应fail实际pass；LR给34错误FF-R候选，未比next-state/event/clear/preset | SEQUENTIAL_GATE_COUNTEREXAMPLE.json实读，44来源匹配v5快照；actual63seq graph全识别，非graph漏类；无EDA | LR禁seq进组合R；F1完整顺序语义并保合法同族G；反例/正控+当前全v6/独立汇合/commit后才能注册C′v3；不必改graph | 历史v6=926pass后单行原例仍pass的失败保留；现精确V3单行原例正确拒reset→set且合法Gpass/parsed1/1，完整v8=969pass/170SHA稳定已验收，OI040/041实现门闭合，科学域不泛化。9proof模型重生成9/9字节一致/source与LIB稳定，非新外部证明；A6/B2/B17保各自pin，6statetable不扩writer支持 |
| OI-041 | **gate_sizing单行漏解析与F1空解析集合伪pass** | 2026-10-16（原样重放原seq反例） | **实现门closed：精确V3+scope30pass+完整v8=969pass/170SHA稳定** | _CELL_INST_RE要求行首导致合法单行gold/gate都parsed=[]；F1 strip actual cells后空集合比较通过，原reset→set仍pass | SEQUENTIAL_GATE_VERIFICATION.json passed=false/source稳定/无EDA；合法Gpass/seqR0，失败原件不覆盖；v6真926未覆盖 | 单行/$名/注释strings/escapednet解析；F1物理↔parsed完整覆盖；旧源码多行seq独立反证区分OI040根因；新完整v7/commit后才v3注册 | 精确V2已reset→set fail/legalGpass/R0、parsed1/1；相关214pass，原失败receipt保留。v7原失败保留；仅F1 opt-in连接提取/公共门保positional，scope30pass、原始V3pass与完整v8=969pass/170SHA稳定已验收；实现门关闭，不升级科学闭合；当前C′v3/18pilot执行另登记，不升级科学结论 |
| OI-042 | **C同族重建适配器末候选STA输入TCL/Lib漂移仍可提交** | 2026-10-16（models独立反例） | **实现门closed：原反例独立PinDrift拒/0commit，注册38独立QA通过；C科学待** | 最后candidate调用期间改TCL Liberty路径，finally仅核mapped，捕获TCL与最终live SHA不等仍qa_complete/commit1 | C_ADAPTER_REVIEW/REVIEW.json blocked_by_OI-042/SHAf6e24f…，54before/afterSHA一致/HEAD3ea；正式可重复probe独立receipt仍input_drift_accepted/1commit/completiontrue；原38QA独立再过66.09s，无EDA | parser已备份并按原probe有效红→绿，作者transaction_interface QA_REPORT（e867e9…）84pass；models独立C_TRANSACTION_ADAPTER_REVIEW（e5b47c…）原probeexit1/PinDrift/0commit无completion，register38pass17.70s/60beforeafter来源稳定，主线授权核符后关闭此实现门。C48仍未正式注册/无EDA，不影响C′source/结果 | 旧review/38QA/红probe及修后独立receipt全部保留，修前6原件永久快照C_ADAPTER_REVIEW/source_snapshot_pre_OI042已SHA闭合；仅此输入漂移门关闭，不升级C科学恢复。anchor只是可信本地写入下plainSHA一致性/漂移检测，不是签名授权或抗整目录篡改证明 |
| OI-043 | **中英环境段误称全部数据集统一0.5ns时钟** | 2026-10-16（root时钟TCL实证审计） | **closed：中英设置/caption修正、两遍编译/38p视觉/副本同步已核** | 实际Pico core5ns/mul2ns/regs0.5ns；中英环境段将全部数据集写0.5ns | TIMING_CONSTRAINT_CHECK.json/Pico187TCL=26/160/1逐SHA与create_clock独立核符；MAIN27.json/canonical B27 baseline均0.5ns，aggregate.py SHA匹配 | 主线metadata_correction_01各2处最小修中英setting/图4caption；en首替换字面TeX转义另V2修复，原V1保留。当前zhcb9bd…/enbdde6…两遍编译/source稳，FINAL_QA38p contact+细查零视觉缺陷/PDF句回读通过，SYNC中文80416…双副本/英文bb6b35…当前SHA核符；两版各14表块与7图引用独立比较未变 | 仅设置说明错误关闭，其他科学门不变；旧V1/V2/QA/源码/PDF备份保留。初次整页layout回读串栏为程序性提取错误，crop实际左栏更正，不是版式/科学失败 |
| OI-044 | **B3旧24/44阶段QA对应源码字节备份缺失** | 2026-10-16（models保全自查） | **open，历史可重放限制；当前51QA独立有效** | 当时未对旧adapter5f965…/f983…及旧tests事前备份；旧QA/log仍有，但不能保真重放其源码 | historical_source_lookup原JSON/log保真归档：2277source候选/3ZIP、4旧目标SHA匹配0/errors0；当前4146…before/after稳定 | 后续若找到旧字节按SHA验证恢复；不由新源码反向重构/伪造旧source snapshot。当前root51源码/收据独立钉定，非阻断当前已审域 | 不声称旧24/44源码已归档或完整可重放；旧QA仅阶段历史，保全遗漏明示，当前51不能替旧source身份 |
| OI-030 | **族 C 的双割/代价机制归因与排序对照混杂** | 2026-10-14（r21） | **错误归因已修；独立机制证据未闭合** | 族 C 运行器不调用 cost/Cw/Cc，混合含 JOINT 而随机台账仅 R/G/B，1.07→0.40 ns 不能解释为纯排序或双割消融；数字保留为历史策略配置对照 | 五视角报告、methodology_verification 与主线裁定；正文/表注已写明候选构造与顺序联合作用 | r22用户继续授权已恢复双割/权重独立因果证据；同运行器新C′不拼旧C，首pilot实现bug修复后新pin/完整重跑 | 机制独立归因未闭合，不因图件完成而关闭；新C′partial MATCHED_STATE_PAIRS_08四电路八配对同base轮代价非均匀但cut/pool/dispatch/endpointSHA全同，不能归因权重收益/不外推八电路，重复轮非独立样本 |
| OI-031 | **族 C 接受/提交语义与逐臂配置档案不完整** | 2026-10-14（r21） | **接受/提交披露已修；各臂完整 flags/argv 未钉定** | 混合 tns-aware、WNS 平台/TNS 改善接受与轮内逐实例多提交，区别于算法1；对照臂完整命令/revision 不能由结果推测 | 混合配置与台账已实查，方法/领域复核确认披露通过；正文明确历史逐实例 pass、表注承认命令缺失 | 恢复逐臂原始命令/flags/revision 与公平对照档案；无法恢复的字段明确标缺失，不补写推测参数 | 配置完整性/完全复现证据继续开放 |
| OI-032 | **主结果评估记录与 F1–F6 统计使用不同 b17 批次** | 2026-10-14（r21） | **closed（批次披露完成）** | 主结果3363条记录含180s重跑b17的104；F1–F6分母4044含默认785，差681来自批次替换；两者不是全部新STA执行总数 | 表注批次已披露；r22报告级另恢复b17独有候选STA结果104，主结果有来源2994，计数分层见OI-034 | 保留批次披露与原记录单位；报告级来源恢复不等全部工具调用，不与正确性验收混淆 | 无（披露已闭合；正确性另见OI-036/037） |
| OI-004 | 实验目录磁盘占用（历史瘦身残留） | 2026-08-28 | blocked（用户声明不删） | experiments/ 共 116 GB / 122 目录（itc99_main 19G、phys_closure 2.6G 等） | 已清理 STA 中间日志 + 旧仓库副本全删（2026-09-12） | INVENTORY 的 cleanup-candidates 档位待用户逐项确认；实验证据严禁删 | 用户 |
| OI-005 | 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` | 2026-09-12 | 基本关闭 | 内容已全删（含旧 .venv、C 盘 3 个 worktree；3 条 codex 分支已推送固化） | robocopy 校验 + 全量删除 | 会话关闭后空壳若仍在，手动删除即可 | 无 |
| OI-007 | hold 模式跨测试集效果有限 | 2026-09-08 | 记录在案（不阻塞投稿） | 14 电路仅 b01 改善 min_slack；已写入论文 limitation | 单 patch 无法同时改善 setup+hold | 未来工作（多目标 hold/setup 联合搜索） | — |
| OI-008 | 论文表 F1/F6 反馈动作描述与代码实现不一致 | 2026-09-23 | **论文侧已修正**（2026-09-23）；**S1 补充说明已成文并更正本条两处过时表述**（2026-09-30） | 三处差异已按代码事实修正论文 8 处表述（另 F4 行措辞统一，共 9 处）；已发表数字不受影响 | 逐行对照 `refinement.py` + `git show 216a118` 溯源 + 实测产物统计；**2026-09-30 复跑探针复核**（19 电路 / 4044 trials 分布逐项一致） | **【2026-09-30 更正】** ① 本条原记"当前 `code/` 已无旧事件名字符串"已过时：0a 步骤 4 合并（`258f588`）后，`real_wns.py:1864` 的运行器**仍以 `acceptance_budget_violation` 写试验台账**——故产物与现行代码在事件层**一致**，真正的差异是"工具层事件名 vs 方法层 F4 分类名"的两层命名分工（`failures.py` 的 `FailureType` 承担归因）；② 该两层对应关系已成文为投稿补充材料 `paper/zh/submission/supplementary/S1_失效事件名映射说明.md`，**"投稿前建议在补充材料说明"事项就此闭合**；③ "反馈的独立贡献"隔离实验已由 L2 三臂 + k=1 判别完成（见 OI-012），残余事项仅剩 S1 的转 Word 排版 | 投稿流程（随补充材料提交） |
| OI-009 | **Algorithm 1 的"不叠加"描述与主实验实际行为矛盾** | 2026-09-23 | **论文侧已修正**（2026-09-23） | 论文 Algorithm 1 第 250 行称"各轮候选均相对固定基线 $G_0$ 评估，不叠加多个局部补丁"，但实测 `base_netlist_hash` **逐轮内唯一、跨轮变化**（b01 8 轮 9 个基准 / b03 9 个 / b04 8 个 / b05 8 个），且变化发生在**接受轮之后**（b01 iter1 接受 1 个 patch → iter2 基准哈希改变）——**主实验实际为逐轮累积叠加**，仅"效率优先配置"（sprint1）为单轮不叠加。§4.3 对 PicoRV32 的"由 R/G/B 多类接受补丁叠加形成"表述反而与实测一致，与 Algorithm 1 自相矛盾 | 探针 `scratch/probe_base_hash2.py`（逐 trial 校验：同轮内哈希唯一、跨轮改变）；`20260805_tcad_sprint1_iscas89` summary `iterations=1` | **已改**：Algorithm 1 重写为"从**当前网表** $N$ 提取锥 → 接受后 `$N\gets N+\Delta$` 提交为下一轮基准 → 同轮候选共享同一基准且互不叠加 → 该轮一旦提交，基于旧基准的其余候选作废"；并拆出失败反馈为独立步骤；算法后补"候选按轮提交…效率优先配置仅执行单轮，不产生累积叠加"。遗留：把该行为与 OI-011 的 codex 实现（`SearchState.accept_patch` / `refreshed_cone`）对齐到同一层级描述 | OI-011 已定案（路径 B）；本项复核并入实施步骤 0a（`SearchState` 落权威布局） |
| OI-010 | 论文 §4.2 的 ISCAS89 策略分布与实测不符 | 2026-09-23 | **已闭合（2026-09-28 晚）：⚠️ 原判「两族均不支持该映射」系本人解析错误——该分布本就有据；A\* 重跑改为「可复现性限制」证据** | §4.2 称"JOINT 对应 s27/s382/s420/s953，G 对应 s641/s713/s832，R 对应 s820"（4 JOINT + 3 G + 1 R）。**两套 ISCAS89 运行都不支持该映射**：① `20260826_iscas89_main` 实测 **G 23 次/7 电路（s27/s382/s420/s641/s713/s832/s953）、R 4 次/2 电路（s641、s820）、JOINT 0、B 0**；② 图 4 源 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 为旧格式（多对象拼接、非严格 JSON，即 20260806-16 修掉的写盘 bug），无法直接统计，其 `summary.json` 仅记 3 个电路（s953/s832/s820，`iterations=1`）。**并且 §4.2 的数据集归属本身存疑**：§4.2 称"图 4 对应效率优先配置（最大 1 轮 + 首改进即停）"，但 `20260826_iscas89_main/summary.json` 显示 `iterations: 8`、`wns_history` 长度 3–7（多轮累积）；`20260805_tcad_sprint1_iscas89/summary.json` 却为 `iterations: 1`。`RESULTS.md` §2 的 strategy 列同源同错（"JOINT 是主要增益来源 4/8"） | 探针 `scratch/probe_iscas89_dist.py`、`scratch/probe_iscas89_two.py`、`scratch/probe_sprint1_dist.py`；两套 summary.json | **【2026-09-28 裁定：选 A】** §4.2 该段所有量（WNS / strategy distribution / accepted patch / STA count / 图表）**必须全部来自同一 efficiency-first / sprint1（`iterations=1`）实验族**；`20260826`（`iterations: 8`）是另一算法运行状态，**只能用于多轮/收敛类实验**。sprint1 缺字段 ⇒ **重跑 sprint1，不得从 20260826 借值**。原则：`same claim ⇒ same code revision + same config family`。**本轮不改该句（避免编造）**：需用户先裁定 §4.2 以哪套运行报告——(A) 效率优先/Tcad-sprint1 口径（则需重跑或从旧格式产物恢复策略分布，并解决其 summary 仅 3 电路的问题）；(B) 20260826 口径（则 §4.2 的策略分布改为 G 7/8 电路、R 2/8 电路、JOINT 0，并把"效率优先/1 轮"表述改为与 `iterations: 8` 一致）。定案后一并同步 `RESULTS.md` §2 | 用户（投稿前） |
**▲【2026-09-28 晚 · 更正与闭合】** 该条原判据（"两套 ISCAS89 运行都不支持该映射"）**不成立，系本人的解析错误**：图 4 源族 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 确为"多对象拼接、非严格 JSON"，但**只要用 `json.JSONDecoder().raw_decode(…)[0]` 读第一个对象**即可拿到 `call_log[0].accepted.kind`——逐电路结果为 **JOINT{s27,s382,s420,s953} / G{s641,s713,s832} / R{s820}**，**恰好就是 §4.2 所写的 JOINT 4 / G 3 / R 1**；且**独立印证**：A′ 族 `20260807_real_pr_iscas8/manifest.json` 的 8 条候选标签（`029_JOINT_JOINT`、`001_JOINT_JOINT`、`089_JOINT_JOINT`、`000__101__G`、`000__085__G`、`002__121__R`、`002__140__G`、`006_JOINT_JOINT`）**逐条与之一致**。此前之所以误判，是因为把该文件按单对象 `json.load` 读取、`JSONDecodeError` 被 `try/except` 静默吞掉（探针输出 `{}`）而未察觉。⇒ **结论：§4.2 的策略分布不需替换、不需从任何族"借数字"**；原裁定"A 口径 + 重跑补齐"的**方向保留**（§4.2 全部量仍须同属 efficiency-first 族 ✓），但**"重跑"的用途改变**。
**重跑（新族 A\* `experiments/20260928_sprint1/`，git HEAD `6b95f8c`，与 A 同配置）实测**：8/8 电路仍严格改善，但**候选序列漂移**——接受类型分布变为 **G 6 / JOINT 1（s382）/ R 1（s820）**；s382 候选级 STA 2→41、s420 90→66。⇒ 该结果**只作"族 A 在冻结 revision 下不可复现"的可复现性限制**写入 §4.2 的「族与可复现性」段，**不替换 A 的历史数字**（替换即等于"从其他实验族借数字"，正是本条要防的错误）。A\* 的 8 个 `final_patch_id` 与族 B（`20260826_iscas89_main`）**逐电路完全相同**，说明 A\* 实为族 B 流水线的第 1 轮切片，不是族 A 的重现。
**方法论教训（已写入 skill `doc-evidence-number-consistency`）**：判"某台账不支持某结论"之前，必须先确认**能够读到该台账**；`json.load` 抛 `Extra data` 只说明它不是单对象 JSON，不说明字段不存在。**禁止用被 `try/except` 兜住的解析失败作为"无证据"的依据。** | 已闭合 |
| OI-011 | **main 分支 `code/` 不是产出论文主实验产物的实现（代码谱系分叉）** | 2026-09-23 | **已裁定路径 B；G2/G3/G4 已冻结；0a 步骤 2–5 已实施并过 gate（`a12ecab`/`9ac06bf`/`258f588`/`870d062`/`9870abc`/`1777a78`），**等价门 24/24 × 3 电路全 PASS**；**legacy regression 步骤 6 亦通过：8 个 ISCAS89 电路（s27/s382/s420/s641/s713/s820/s832/s953）**8/8 × 24/24 全等**（含 bookkeeping），报告 `reports/FAECO_LEGACY_REGRESSION_20260923.md`，下一阶段 L2 Adaptive 解除阻塞 | 产物侧字段 `base_netlist_hash`/`acceptance_evidence`/`sta_provenance`/`topology_metrics`/`cache_key`/`config_hash` 在 **main 的 `code/` 全 0 命中**；产出实现在 `codex/faeco-unified-loop` 分支（`flow.py:483` 建 `SearchState`、`:684` 接受后 `refreshed_cone=extract_fanin_cone(...)`、`:726` 调 `accept_candidate`；`real_wns.py:784 accept_candidate` 内 `self.mapped_text=str(text)`）。main 侧 `flow.py:392` 锥只抽一次、`real_wns.py:197` 后 `mapped_text` **永不更新** → **main 无逐轮累积行为**。谱系 `merge-base=b8c3759 (08-13)`，main 在 08-14~09-07 无提交（恰跨 20260826 主实验期）。**任何阶段 1 实验若在 main 上跑，数字与论文不可比。必须最先处置。** | `git log -S` 检索产物字段（限 `-- "*.py"`）；`codex/faeco-unified-loop:src/rseco/{flow,real_wns,refinement_loop}.py` 逐行对照 | **路径 B 已定**：`SearchState` 为**唯一运行时状态所有者**（详见 `planning/FAECO_V2_TECH_DESIGN_20260923.md` §2）。实施步骤 0a：把 `SearchState` 体系落到权威布局，增持 `FailureFeedbackState`/`cone_limit`/`round_id`；`rollback()` 需同时回滚 EMA 与 cone_limit；以 3 电路 sentinel 复跑复现既有数字（或如实记录差异）。**配套前置 G2/G3/G4 已冻结**：状态更新契约 / checkpoint+`netlist_epoch` 契约 / `W_*`→F1–F6 映射 → `planning/FAECO_V2_IMPL_CONTRACT_20260923.md`。**0a 第一阶段不得改变算法行为**，gate = 等价报告六项全等（候选顺序 / F1–F6 序列 / 每轮权重 / 接受补丁 / 最终 WNS / STA 次数）。另须修一处既有缺口：`candidate_hash` 不含基准网表，多轮去重会误杀（改 `candidate_key = sha256(netlist_hash ‖ candidate_hash)`）。**实施与 gate 结论（2026-09-23）**：步骤 2 EMA 反馈（`a12ecab`）→ 3 `SearchState`+checkpoint+G2/G4（`9ac06bf`）→ 4 codex 能力合并（`258f588`）+ 09-12 路径修复（`870d062`）→ 5 等价门。报告：`reports/FAECO_0A_EQUIVALENCE_20260923.md`。**gate 结果：codex `9435846` vs main `fcdf06b`，`s382`/`b03`/`b06` 三电路均 24/24 项全等（E1–E6 全 PASS），回归 411 passed/4 skipped，算法行为未变**。已获硬证据：`experiments/20260826_iscas89_main/s382/s382/outerloop_result.json` 的 `state` 键集与 codex `SearchState.to_dict()` 完全一致 → §8.3「基线 = codex 谱系」由推断升级为实测。**A5 已裁定**：产物为串行 `--workers 1` + 内层 `early_stop=True`；runner 默认保留 `True`，旧口径"首次接受即停"写作 `--max-patches 1`。**附带钉住产物配置**：ISCAS89 主实验用 `--candidates-per-iteration 1`（s382 因此 24/24 精确复现），且批次启用 `--tns-aware` | **0a 已完成；下一步 L2 Adaptive（$\rho=0.5$）** |
| OI-012 | **论文 §4.4 表 6 的"失效反馈开/关"对照在运行器层面不成立** | 2026-09-23 | **论文侧已修正**（2026-09-23） | §4.4 原称"以**禁用 F1–F6 失效反馈**、保持权重固定的纯 G/纯 B/随机为基线，与**启用失效反馈**的 20 轮混合策略比较"。**证据链三重闭合**：(a) 表 6 四列均出自 `code/scripts/run_hybrid_repair.py`（混合列由 `20260807_multiround_8c_067/run_all.bat` 证实），该脚本**不使用** `refine_weights`/`RefinementWeights`/`enable_feedback`；(b) 该脚本输出 schema 与四列产物完全一致（`rounds_history` + `candidate_sta_before_round/after_round`、`random_order`、`seed`、`improvement`）；(c) 表 6 混合列 8/8 电路与 `20260807_multiround_8c_067/convergence_summary.json` **逐值精确吻合**（0.28/1.00/1.54/1.63/1.33/0.99/0.57/1.25，均值 1.074），纯 G 列均值 0.161 亦同源。→ 四列**都无 F1–F6 反馈**，该表实际对比"候选空间 + 排序启发式"。**附带修正三处**：表注"随机列与混合列共享 R/G/B/**JOINT** 候选类型"不成立（随机列实测 B 7154/G 3114/R 1954，**JOINT 0**）；`tab:configs` 中"20 轮收敛"列的 `F1--F6 失效反馈 = 轮内 + 跨轮` 无依据；**表 6 三列基线所用的 `20260826_ablation_pureG/pureB/random_seed{1,2,3}` 目录顶层运行脚本 0 个**（.bat/.sh/.md/.log 全无），调用命令未归档 | `code/scripts/run_hybrid_repair.py`（imports + 输出 schema grep）、`20260807_multiround_8c_067/run_all.bat` 与 `convergence_summary.json`、`20260826_ablation_*/hybrid_result.json`、探针 `scratch/probe_ablation_cfg{,2}.py` | **已改**：§4.4 首段重写为"比较候选空间与候选排序两类设置"并明示"各列由同一固定权重运行器产生、不构成失效反馈的开关对照，失效反馈的独立贡献需另设对照实验量化"；表标题改为"候选空间与候选排序设置的 WNS 改善对比"；表注改为"纯 G/纯 B 列分别只生成 G/B 候选，随机列与混合列在混合候选空间生成候选（混合列另含 JOINT 组合候选）…各列均使用固定搜索权重、不启用 F1--F6 权重重整"；`tab:configs` 20 轮收敛列反馈行改为"不启用（固定权重）"并在表注说明。遗留：**核心主张 Failure-Aware 目前仍无有效对照**，须由 `planning/FAECO_V2_DESIGN_PLAN_20260923.md` §2 的三臂实验补齐（且须归档运行命令 + 在结果 JSON 记录 `enable_feedback`）。**2026-09-24 三臂实验已完成整改与补齐**：运行命令归档（`run_config.json`：argv+resolved args+git head+臂身份）与结果 JSON 的 `enable_feedback`/`feedback_config` 均已落地（提交 `6e44fae`→`6276cff`）；三臂 × 8 电路结果见 `reports/FAECO_L2_THREEARM_20260924.md`——**§6.4 行 ③ 命中：EMA 失效反馈在 k=8 混合候选 regime 下无独立贡献**（8/8 电路终点/k₁st/maxB(k) 与 fixed 全等，4 电路多花 9%–116% STA），价值定位回退到「候选空间 + 权重排序」（random 臂 k₁st 恶化 1–2 个数量级为对照证据）。**遗留**：k=1（隔离反馈 regime）的 fixed vs adaptive 补充对未跑，L2 最终判读待用户裁定 → **2026-09-24 k=1 判别实验已完成，L2 封板**（`reports/FAECO_L2_K1_DISCRIMINANT_20260924.md`）：8/8 电路逐位相同、top-1 候选身份 0 次改变（EMA 高频触发且权重漂移可观但低于割评分 top-1 重排阈值）→ 按预锁定判据 EMA 降级为可选机制、不调 ρ/η；论文表述拆分为「候选空间+权重排序」+「失败归因（诊断）」，对照实验义务（运行命令归档 + enable_feedback 记录 + 开关对照）已全部履行 | 用户（投稿前补实验） |
| OI-013 | **20260826 批次产物只能部分由 codex HEAD 复现（revision 未钉死）** | 2026-09-23 | **已裁定（2026-09-28）：选 A —— 认当前冻结 HEAD；已打 tag `faeco-exp-rev1` → `87d01ba`** | 0a 步骤 5 做对照时顺带验证产物可复现性：**`s382` 完全复现（24/24，含 `n_candidate_sta_runs=22`）**，但 **`b03` 仅 12/24、`b06` 仅 8/24**，且差异落在 decision core（非仅计数）：`b03` 产物 `-1.27`（8 轮每轮接受）vs HEAD/`30f4164` 给 `-1.21`；`b06` 产物 6 个 `--tns-aware` 接受（TNS -3.98→-3.92，`stop=max_iterations`）vs HEAD 无接受（`stop=stagnation`）。**已排除**：环境（Yosys `0.67+146` 与产物 `map.log` 逐字相同）、参数复原方法（s382 已 24/24）、束宽（b03 在 k=1 与 k=8 结果相同）、HEAD 特有（`3e93fd2`、`30f4164` 两处 worktree 定点重跑 b03 仍 `-1.21`）。**2026-09-24 更新（legacy regression 配置 A 的附带检查，`reports/FAECO_LEGACY_REGRESSION_20260923.md` §8）**：ISCAS89 批次用配置 A（k=1、**无** `--tns-aware`）在 **7/8 电路 decision-reproducible**（`s27/s382/s420/s641/s713/s820/s953`，其中 `s713`/`s820` 仅差一个 `E6.n_candidate_sta_runs` 计数），唯一例外 **`s832` 为"路径不同、终点相同"**（最终 `wns=-1.16`/`tns=-5.48`/`final_patch_id`/`final_netlist_hash` 全等，仅接受轮次 1–3 vs 1–4 不同）。**且实测 `--tns-aware` 只属 ITC-99 批次**：s382 不含该开关复现 24/24，含该开关首轮接受点 `-0.88→-0.98`、匹配度降至 11/24（已登记为契约修订 A8） | `code/scripts/compare_0a_equivalence.py`；产物时间戳（`s382 11:22 / b03 11:25 / b01 11:29 / b06 11:51`）对照 08-26 当天 7 个落在 10:47–12:25 的代码提交（`5966991` 恢复 critical-path cover 首选候选、`d595c71` 保留非 R 可改写门、`30f4164`/`b7abaac`/`c58ad8e` 改 F2/SEC 检查而检查结果经 `r_available_for` 反向影响候选生成）；三个 worktree 定点重跑；`code/scripts/compare_equivalence_sweep.py`（2026-09-24 新增的多电路聚合判定） | **【2026-09-28 裁定：选 A + 固化 tag】** 主实验基线**认当前冻结 HEAD**，冻结为 annotated tag
**`faeco-exp-rev1` → `87d01ba`**。规则写明为：**下一轮权威主实验以一个冻结 commit 为基准，随即打 tag /
记 hash**；**禁止**把"20260826 的 `b03`/`b06`"与"当前 HEAD 的其他电路"拼成同一张表。
原则：`same claim ⇒ same code revision + same config family`（而非"哪个数字好用用哪个"）。
`b03` 取 HEAD 的 **-1.21**（优于产物 -1.27）。08-26 产物**保留为历史实验族，不删除、不改数字**，
但**不再作为未来主结果的局部补丁来源**；受 revision 影响的结果须以 `faeco-exp-rev1` + 同一 config family 重跑。
**定性已完成，revision 待钉**：这是 codex 谱系内部 08-26→08-28 的**既有漂移**，非本次合并引入。需用户裁定"论文主实验基线取哪个 revision"——(A) 认 HEAD 行为（则 `b03`/`b06` 相关数字需按 HEAD 重跑更新，方向是 HEAD 更优：-1.21 优于 -1.27）；(B) 认 08-26 产物（则须继续定位到具体 commit 并固化 tag）。**裁定影响面已收窄**：ISCAS89 侧 7/8 电路的论文数字可由 HEAD 复现（`s713`/`s820` 需接受 E6 计数口径差异），`s832` 终值一致仅轨迹不同 ⇒ 实质分歧集中在 **ITC-99 的 `b03`/`b06`（终值不同）**。**另有 2 个未记入论文的开关需登记**：`candidates_per_iteration=1`（两批次共用）与 `tns_aware=true`（**仅 ITC-99 批次**，见报告 §5.3 与契约 A8） | 用户（投稿前） |
| OI-014 | **L3 S 机制已验证；接入实时循环的 {S 开, S 关} 消融给出"无独立贡献"（能力型）——论文定位待裁定** | 2026-09-25 → 09-28 更新 | **2026-10-16 provisional正确性/基线解释重开待核；旧裁定仅历史。已裁定（2026-09-28）：(B) 降级为可选候选类型/探索性能力** —— L1 全量三层裁决为 NEGATIVE（能力型），按预锁定 §13.4-3 规则判 (B)；**不阻塞投稿** | ① 机制侧（§8.12）：真实工具链九阶段全通过，22 项单测；`s641` 窗 `DFF_13` **ΔL=+1、ΔWNS=+0.03 ns**，CEC-1/2 双闭合 + 全网表 structure_check 通过 + 复跑逐位相同。② **环路侧（09-27 新，§8.13）**：8 电路 × {S 关, S 开}，S 在 **7/8 电路真的执行**（抽窗 469、实测候选 37），**接受 0/8**，两臂 `dWNS`/`maxB(k)`/`k₁st`/接受链**逐位相同**；37 候选 **ΔL(BLIF)>0 37/37、ΔL(SKY130)>0 16/37、ΔWNS>0 0/37**（含 16 个权威层变浅者亦无一改善）→ 窗口不在真时序关键锥上。off 臂 **8/8 逐位复现归档 L2 fixed 臂**（惰性 gate 通过）；两臂 `sta_used` 差 ≤8、全停 `max_iterations`（预算不绑定） | 真实 Yosys `0.67+146`+ABC+WSL OpenSTA；`code/scripts/run_s_ablation_batch.sh`（钉版本）、`compare_s_ablation.py`（配对差 + 台账 + 区分"没执行/执行了没用"）、`verify_s_off_reproduces_l2.py`（惰性 gate）、`analyze_s_candidates.py`（双层深度 × ΔWNS 交叉表）；`code/tests/test_flow_structure_resynth.py`（9 项，含"S 拒绝不改反馈通路"逐位断言）；回归 486 passed / 4 skipped | ① **已完成**加宽分配稳健性对照（`k4`：配对差仍全 0.000、候选 37→39 ⇒ 排除"配额不足"，瓶颈定位为可用窗口集合受"接受次数"限流）；② 裁定 S 定位——证据倾向 **(B) 如实降级为可选类型**并与 L2 封板结论合并，主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」；(A) 独立贡献需先实现**时序加权选窗**（当前割选窗与 R/G/B 同源，正是被实测定位的瓶颈） | 用户（投稿前） |
| OI-015 | **既有物理门（SPEF 复测）在 ISCAS89 上几乎无判别力：F6 标签近乎恒真** | 2026-09-27 | **2026-10-16 provisional对象/物理参数/paired-baseline重开待核；旧裁定仅历史。已裁定（2026-09-28）：降级为物理诊断/过滤机制；标定另开 OI-016，不得以"让 F6 变多"为目标** | s27 实测：20 轮官方口径 **521/532 trial 为 F6**（98%）、小规模探针 **32/34**，`physical_delta` **29/34 恰为 0** → 成对物理增益并不区分候选。**2026-09-27 规模化坐实**：8 电路 4349 条物理 trial 中 `physical_delta≠0` 仅 **10.3%**、F6 少数类仅 **1.17%**（51/4349）。与 OI-008 的"ITC-99 主实验 F6 触发 0 次"互补。直接关切 §7 第⑦条（b17"人工放宽预算"）质疑 | 3-A 四臂采集（`phys`/`elec` 带 `--physical-gate`）；探针 `scratch/elec_probe/phys_elec_probe` | **【2026-09-28 裁定：降级 + 另开标定】** 不采用简单的三选一。① **机制定位先降级**：F6 当前**只能**安全主张"对**少量** ideal-net 有利、但物理估计后失效的候选进行**识别与拒绝**"；**不得**主张"F6 显著改善后续搜索或物理 WNS"。② **同时允许做 `unit_len_um` 标定**，但**标定目标必须在实验前定义，且不得以 `maximize F6 count` 为目标**（否则变成"为了让机制看起来有用而调参"）。合理目标：`min |WNS_simplified_SPEF − WNS_OpenROAD|`，或至少最大化排序/符号一致性 `sign(ΔWNS_SPEF) = sign(ΔWNS_OpenROAD)` —— 即**用 OpenROAD 作外部参照标定物理 proxy，而不是用 F6 命中率标定**。③ 标定后 F6 若仍罕见，**接受该事实**。⇒ 标定工作转为独立任务 **OI-016**。④ (C) 弱化 F6/物理增益表述、主实验只报理想口径 —— 仍作为**兜底**保留 | 用户（投稿前） |
| OI-016 | **物理 proxy（`unit_len_um` 等）标定：以 OpenROAD 为外部参照** | 2026-09-28 | **已开（由 OI-015 裁定引出；不阻塞 3-A/当前 L1）** | 现状物理门参数（`physical_unit_len_um=40`、`fanout/depth_penalty=1.0`、`min_physical_gain_ns=0.01`）**手工设定且未标定**，判别力弱（见 OI-015）。任务目标：把简化的 SPEF/物理估计与真实物理实现对齐 | 需新增外部参照链：OpenROAD（或等价 STA/RC 工具）在 sky130 上对同一网表出 WNS | **标定目标（须写在实验之前，冻结）**：主判据 `min |WNS_simplified_SPEF − WNS_OpenROAD|`；辅判据 `sign(ΔWNS_SPEF) = sign(ΔWNS_OpenROAD)` 的一致率。**明确禁止**以 `maximize F6 count` / 提升物理门触发率为目标。**产出**：标定后的 `unit_len_um` 等参数 + 标定报告 + 参数依据。**注意**：标定**不得**反改论文既有数字的既有实验族；若标定后 F6 仍罕见，如实接受（联动 OI-015） | 用户（后置；投稿前可选） |
| OI-017 | **`structure_resynth.rejections` 台账在 s420 上未闭合** | 2026-09-28 | **记录在案（不阻塞 L1 裁决；不影响候选数/实测数/ΔWNS/接受数）** | s420 的 {S on} 报 6 个候选（全 S0）与 6 条变体级拒绝 `W_STRUCT_ERROR`（**均标 S0**），但磁盘 `case/results/structure_resynth/round020/` 下只有 **8 个窗口 × {S0,S1,S2}**。8 个 S0 槽位无法同时产出 6 候选 + 6 条 S0 拒绝 ⇒ 台账不闭合。其余 7 电路 rejections 为空、无此现象。`W_STRUCT_ERROR` 的语义是**硬有效性失败**（`structure_check(grafted, baseline_text=…).ok == False` ⇒ 返回 `(LABEL_STRUCT_ERROR, None)`，**不产候选**） | `experiments/20260928_s_l1_ablation/on/s420/outerloop_result.json`（`structure_resynth.rejections`）、`case/results/structure_resynth/round020/` 目录树；`code/src/rseco/structure_resynthesis.py` L694-712 / L757-774（`if candidate is not None … elif label is not None …`，S1/S2 同 canonical ⇒ `(None,None)` 丢弃） | **待查（低优先，仅记账语义）**：需按 (窗口, 变体) 逐槽打点，确认是 `variant` 标签记录错位还是 S1/S2 的 `(None,None)` 路径在 STRUCT 失败时未走。**在任何后续引用该 `rejections` 台账的结论前必须先解决**；本报告的 L1 裁决**不依赖**该台账 | 后续（S 候选质量归因时顺带） |
| OI-024 | **Word 转排件与论文内容脱节（仍为 v6 版；r8~r20 改动均未同步）** | 2026-10-13（r16 更新） | 记录在案（**投稿前必须解决**；若改投 Integration 则中文 Word 转排件用途需重估） | `paper/zh/submission/word/FAECO_投稿Word转排_20261009c.*` 仍为 **v6** 内容：**标题/摘要为旧口径（非 v9 的「候选探索与失效刻画」/ `Candidate Exploration and Failure Characterization`）**、**缺六张新增表（r9 表 5/8/9 + r10 表 2/4/11）**、§4.1 无运行环境、§3 无特征设计动机小节、§4.4 未弱化 k₁st 且无运行时间表、§4.5 未弱化物理口径、**术语仍为「结构化候选搜索与失效归因」**；与 **v18** 主稿（内容指纹 `63e62c52…`，11 页，文件名为 `FAECO_面向预布局门级时序ECO的候选探索与失效刻画`）不一致 | 已定位根因：`scratch/word_convert/postprocess.py` 的摘要/关键词/标题为**硬编码**（不从 `.tex` 读，v5 轮已因此产出过旧摘要 Word 稿）；r8~r14 均未重跑管线（r12 = 一致性 pass：表 5/表 11 表注 + 5 处 PicoRV32 记法；**r13 = 摘要中/英两段 + §1.1 引言首段改写；r14 = 正文 10 处去防御化改写；r15 = 全篇去防御化编辑（正文 11 处 + 摘要末句）；r16 = 术语一致性与 claim 强度校准（17 处：P0×3 + P1×2 + 结构 2 + 配套 8，含摘要末句与 §1.1 新增映射句；r17 = 逻辑一致性精修（12 处：P0×4 + P1×2 + 配套 6，含摘要末句、表 5 表题/表头、§3.3 新增 $C_w$/cost/$C_c$ 关系句）；r18 = 图 2 机制图替换（零 .tex 改动，仅换图件，文本层不变）；r19 = 论文定位重构（12 处叙述层改写：A1–A3 概念定义 / B1–B3 主线与 §3.3 拆分 3.3.1–3.3.3 / C1–C3 重要性 / D1–D4 实验定位）；r20 = 学术叙事收敛（13 处叙述层改写：唯一主线「候选探索」/ 摘要核心思想句 / §1.3 贡献分层为 2 贡献 + 平台 / 失效反馈语言弱化 / §4.5 标题 / 结论意义强化 / 删 §4.1 边界句））**，`postprocess.py` 硬编码摘要块须同步） | 随 T20 重建：① 同步 `postprocess.py` 硬编码块（标题 + 摘要中/英 + 关键词，取 v18 文本）；② `preprocess.py` 的 `\bibitem` 计数守卫仍为 14（未变，无需改）；③ **输入路径随主稿改名一并更新**；④ 重跑 preprocess→pandoc→postprocess→Word 引擎导出；⑤ 更新 `转排说明.md` 与 `T20_SUBMISSION_PACKAGE.md` 哈希。**注意**：六张新表为 LaTeX 表，Word 管线需新增对应表格处理。**若最终确定只投 Integration（英文）**，中文 Word 转排件的必要性下降，可先做英文稿再定 | 投稿流程 |
| OI-025 | **图源文件不在 `versions/*/MANIFEST.sha256` 冻结覆盖内** | 2026-10-12 | 记录在案（不阻塞投稿） | manifest 117 条口径 = 论文 `.tex` + 双副本 `.pdf` + `code/src` + `code/tests` + 若干 experiments 汇总文件，**不含 `paper/zh/figures/`**。而 PDF 由图源编译而来（r8 已重绘 `fig_cut_generation_mechanism_imagegen.png` 以对齐 $P_w$/$P_c$ 图注）。⇒ `sha256sum -c` **无法检出图源漂移**，仅 git 可回溯 | v7/v8 manifest 生成时确认（`scratch/gen_manifest_v{7,8}.py` 对 117 条重算，`figures/` 命中 **0** 条） | 二选一：① 维持既有口径（图源由 git 把关），在 v7/v8 README 与 manifest §6 显式声明该边界；② 下一轮冻结起把 `paper/zh/figures/` 加入 manifest（条数 117→约 147，属**冻结策略变更**，需用户确认） | 用户（策略选择） |
| OI-026 | **加权割（cost / feature）消融实验未做——复审三"§三 实验 2"建议，复审四列为「投稿前必须补」第 3 项** | 2026-10-12 | **用户 2026-10-12 表示"可以投入新的算力"**（= 该项曾获算力授权；执行前先出方案。**★ 2026-10-12 用户改判：暂缓 —— 不作为当前投稿前置条件**；理由：论文主论证链已闭合（候选空间 1.07 vs 纯 G 0.16 / 候选排序 STA 次数 / runtime 4146 vs 5624），且新增 cost 消融会引入"为什么主实验不用这个配置 / 为什么表 9 不是这条 cost 路径"的解释成本；**若审稿人要求 "Need more ablation on weighting terms" 再补**） | 复审四明确：审稿人要的「feature 消融」＋「补 runtime / baseline 定位 / feature 消融三项可明显提高一个档次」。其中 **runtime 表**（表 11）与 **baseline 定位**（表 2 + §2.2）已于 r10 零算力补齐；**唯 feature 消融需算力**，故为当前提升档次的最大杠杆。不做则贡献 1（多特征加权割）仅有"混合 vs 纯 G/纯 B"的候选空间证据 | 已勘察：`code/src/rseco/flow.py:359/385` **硬编码**调用 `constrained_weighted_cut_candidates`/`weighted_cut_candidates`；`run_outerloop_batch.py` 仅暴露 `--no-feedback/--adaptive/--strategies/--joint-k/--tns-aware/--enable-buffer/--init-*-penalty/--early-stop`，**无候选源开关**；`cut.py:292` 已把 `fixed_min_cut/random_cut/size_only_cut/critical_path_only_cut` 混入同一候选池 | **执行顺序（须先方案后代码，遵循"技术方案先行"）**：① 在 `planning/` 落**消融方案**（消融臂定义 / 预锁定判据 / 与 §4.4 的族归属，避免跨族拼表）；② `cut.py`/`flow.py` 增加候选源开关（多特征权 / 等权 / 随机权 / 仅规模 / 仅关键路径）+ 单元测试；③ 按冻结 revision 跑 ISCAS89（估计 **40–60 min** 墙钟，双臂）；④ 结果写入新表 → 重走质量门 → **重冻结 v9**。**红线**：新增实验必须与既有族绑定、不得改动既有数字。<br>**【2026-10-12 取证更正（r11 方案阶段）】**：上列"已勘察"的定位**不准确**，经实测更正 —— ① §4.4 表 6/表 8 出自**族 C，其运行器 `run_hybrid_repair.py` 根本不使用 `cost(v)`**（它从 OpenSTA 直接解析关键实例、逐实例枚举 R/G/B，排序仅由 `--strategy-priorities` + `exploration_order()` + 可选 `--random-order` 决定，`parse_args()` 内**无任何 λ**）⇒ **在族 C 上无可切换的 cost 项**，"Base/+boundary/+size/+verification/Full" **无法在该 runner 上运行**；② `cost(v)`（式 2）实现在 `cut.py` 节点代价函数（L182–213），经 `flow.py::_cone_candidates` 使用，权重来自 `real_wns.py` 的 `init_weights`，该 dict **仅 3 键**（`boundary_penalty`/`size_penalty`/`critical_coverage_reward` = λ_b/λ_s/λ_c），**λ_v 与 λ_f 无初始参数、无 CLI**（靠 `getattr(...,1.0)` 兜底）——这才是真实代码缺口；③ `flow.py:359/385` 并非"λ 硬编码点"，而是约束割/覆盖割分支。④ 使用 `cost(v)` 的族 D **复现不出表 6**（s27 1 vs 30 等）⇒ 消融结果**必须**属新族 **C′**、**必须**新表 + 表注声明不可跨表比较。**方案已落** `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7（臂定义 / 预锁定判据 / 代码清单 / 预算修正为 **4–5 h**，原"40–60 min"过时）。**λ_c 有三重角色**（节点折扣 `cut.py:208`、覆盖候选插入 `:306` 且门控为 `>1.0`、size-refined 覆盖奖励 `:403`）⇒ 跑前须先做可分离性探针。 | 用户/智能体（下一步即办） |
| OI-027 | **页数递增（8→9→10）与版式压缩时机** | 2026-10-13（r16 更新） | 记录在案（不阻塞投稿；JCAD **无 8 页硬限**，仅 15 页内按约 350 元/页计费；**Integration 亦无 8 页硬限**） | **当前 v18 = 11 页**（r20 学术叙事收敛后页数仍 11 页、逐页分布不变；r12 一致性 pass、r13–r18 文字/图件轮后页数均为 10 页；**r19 论文定位重构新增约 17 行叙述内容后增至 11 页，第 11 页仅含参考文献尾部 = 孤儿末页**。两道压页实验已做且**均已回退**：① 删 §3.5 唯一正文 `\FloatBarrier` —— 无效（仍 11 页）；② 图 2 宽度 0.65→0.58`\textwidth` —— 无效，且浮动体级联使末页承载**更多**（p10 5568→4590、p11 339→2567 字符）。⇒ 页数增长源于**用户指定的叙述层新增内容**、非版式缺陷；按项目纪律**未缩字体/行距、未砍内容**）；质量门 0 Error / 0 Overfull / 0 Underfull（hbox 与 vbox **均无**） | r8 轮实测（40+ 变体）：删正文 `\FloatBarrier` **有害**、`\balance` **不可删**（删后末页右栏只剩 1 条文献）、图 2 移到 `[!t]/[!b]` 无效、表 3/4/8 位置调整无效；**图 2 宽度 ≤0.53 可回 8 页**但会裁小 imagegen 图约 18%。r10 轮追加实测：**`\linespread` 调小反而使 `\balance` 末页 vbox 溢出恶化**（0.96pt → 1.55pt，已回退）；最终靠**删除表 14 表注中与正文重复的一句**（释放 1 行）使 Overfull 归零 | 用户裁定"**等内容定稿再统一排**"——待 OI-026（feature 消融）与可能的 Integration 英文稿定稿后，统一做一次版式收尾并按 `latex-paper-layout-freeze-audit` 流程重冻结 | 用户（时机） |

| OI-029 | **第五份外部审稿（投稿前最后一轮审稿人视角）落地：Submission consistency pass（r12）** | 2026-10-13 | **已完成并重冻结 v10**（用户裁定「不要再加实验」；仅 M1–M5）；**续：r13 大同行入口改写→v11；r14 去防御化重构→v12；r15 全篇去防御化编辑→v13；r16 术语一致性与 claim 强度校准→v14；r17 逻辑一致性精修（claim calibration）→v15；r18 图 2 机制图替换→v16；r19 论文定位重构（主线强化 + 首次概念定义 + 重要性提升）→v17；r20 学术叙事收敛（唯一主线 + 贡献分层 + 失效反馈弱化 + 实验/结论口径）→v18** | 审稿人评分：问题价值 9 / 方法完整性 8 / 创新表达 8 / 实验完整性 8 / **证据一致性 7** / Integration 匹配度 8.5；最大风险 = **可读性风险**（「哪个实验验证哪个机制」），非实验风险；审稿人判定「完成 M1–M5 后即为真正的投稿版本」，并**再次否决**补做 cost/feature 消融。 | M1 表 5 SEC `19/19`→`18/19` + 表注；M2 PicoRV32 `2/3`→`2/2` + 分母解释（5 处）；M3 表 11 表注补「两个 STA 计数口径不同」（预约计数 vs 测量计数，数字无需更正）；M4 贡献 1 弱化 `1.07 ns` ↔ 加权割绑定；M5 §3.4 + 表 4 措辞降调；另 §4.4 开头补「不单独隔离式 (2)」句。 | 归档 `paper/zh/review_rounds/r12_20261013/`（`comments.md` / `response.md` / `manuscript_before.tex` / `manuscript_after.tex`）；`versions/v10/README.md`；LOGS `LOG-20261013-01/02`；tag `v2026-10-12-pre-submission-consistency-r12` / `faeco-paper-final-20261013`；`.tex` `c5828999…`、双副本 PDF `4ef380f7…`、内容指纹 `c7b4d807…`（poppler 25.07）；10 页 0/0/0/0 | 零（审稿人已认可投稿就绪；剩余均为 OI-028/OI-024/OI-021 等流程项） |

### OI-014 **L3 S（窗口局部结构重综合）机制已验证；接入实时循环的 {S 开, S 关} 消融给出"无独立贡献"（能力型）结论——**但 2026-09-28 定位到该证据被集成缺陷混淆（S 的窗口池被 R/G/B 配额截断）**——论文定位待裁定** | 2026-09-25 开 / 2026-09-28 更新 | 待裁定（不阻塞投稿；阻塞 §4/§5 的 S 相关表述） | 报告 `reports/FAECO_L3_S_VALIDATION_20260925.md`（机制）、`reports/FAECO_L3_S_LOOP_ABLATION_20260927.md`（环路消融）；契约 §8.12 / §8.13；技术设计 §13（窗口来源重设计）

### OI-015 **既有"物理门"（SPEF 复测）在 ISCAS89 上几乎无判别力：F6 标签近乎恒真** | 2026-09-27 开 / 2026-09-27 更新（规模化坐实） | 记录在案（不阻塞 3-A；阻塞 F6 相关表述与"物理增益"类数字） | 契约 §8.15；3-A 报告 `project_docs/reports/FAECO_ELECTRICAL_3A_20260927.md`

- **【2026-09-27 更新】规模化证据（8 电路 × `phys`/`elec` 两臂，4349 条带回电气记录的物理 trial）**：
  - **`physical_delta ≠ 0` 仅 448/4349 = 10.3%** ⇒ 约 **90% 候选的成对物理 WNS 与打补丁前完全一致**；
  - **F6 少数类仅 51/4349 = 1.17%**，且高度集中（`s420` 20/136、`s641` 13/886，其余六电路各 1–8）
    ⇒ 除 s420 外物理门几乎**从不接受**；
  - 因 51 个少数样本上的 AUC 是高方差估计，3-A 判定**拒绝**了唯一那条近阈读数
    （`worst_max_capacitance_slack` @ `f6` = 0.6519，仅高阈值 0.0019、跨电路不同向）。
  - ⇒ 此前"32/34"的小规模探针结论在**全量规模上被坐实**：该门既不能当好标签，也不能当有效筛选器。

- **现象（实测，真实工具链）**：以论文既有物理门参数（`physical_unit_len_um=40`、`fanout/depth_penalty=1.0`、`min_physical_gain_ns=0.01`）跑 s27：
  - 20 轮官方口径（`run_electrical_collection.sh` 的 `phys` 臂，`k=8`、`--joint-k 2`、`--physical-gate`）
    **521/532 trial 发射 `F6_physical_load_failure`**（98%）；
  - 小规模探针（`--max-iterations 2 --candidates-per-iteration 3`）**32/34 为 F6**，
    且 `physical_delta`（成对物理 WNS 增益）**29/34 恰为 0**。
- **含义**：
  1. 该物理门在当前参数下**几乎不区分候选** —— "接受/拒绝"两侧的成对物理 WNS 变化多为 0；
     F6 不是一个可用的判别标签（正例率 98%，AUC 无从谈起）。
  2. 这与 **OI-008 记录的"F6 在 19 电路 ITC-99 主实验中触发 0 次"** 并不矛盾而是互补：
     F6 只在物理门控实验里出现，而那套门控的触发率**极端不平衡**。
  3. 直接关系到 §7 第⑦条的外部质疑（b17 "人工放宽预算"）：物理门参数是**手工设定且未标定**的，
     这会成为审稿攻击面。
- **对 3-A 的处置（已实施）**：3-A 的预锁定判据不依赖单一 F6 标签 ——
  ① 标签**双类各 ≥20 才算可用**，退化标签如实报为不可用、不产出判定；
  ② 判定要求**同一特征在 ≥2 个可用标签上同时成立**；③ 另跑理想 regime 提供
  `no_ideal_gain` / `hard_fail` 两个有方差的标签。见契约 §8.15(b)(c)。
- **需用户裁定（投稿前）**：(A) 保留现有物理门参数并**如实报告其判别力不足**
  （把"物理门"降级为"保守的成对一致性检查"而非"增益筛选器"）；(B) 标定 `unit_len_um`
  等参数使物理门有判别力（需额外标定实验与依据）；(C) 在论文中**弱化 F6/物理增益**相关表述，
  主实验数字只报理想（无 SPEF）口径。**当前证据不支持**用现有物理门做"增益筛选"的强主张。

- **机制已验证（§8.12）**：`code/src/rseco/structure_resynthesis.py` 在真实 Yosys `0.67+146` + ABC + WSL OpenSTA 上端到端打通（EXTRACT→…→STRUCT 九个阶段全通过并出候选）；22 项单测；**§5.5 判据达成**：`s641` 窗 `DFF_13`（root `G127`，29 门，R_S=1.00）**ΔL=+1、ΔWNS=+0.03 ns、ΔTNS=+0.01 ns**，CEC-1/CEC-2 双闭合 + 全网表 structure_check 通过 + 逐次复跑逐位相同。
- **【2026-09-27 新】接入 `run_multi_iteration_case`（r2 §4.9）并做正式口径消融**（8 电路 × {S 关, S 开}，`k=8`、20 轮、`--joint-k 2`、STA 预算 700 两臂相同；契约 §8.13）：
  - **单变量对照成立且有 gate 把守**：off 臂 **8/8 电路逐位复现归档 L2 fixed 臂**（success/iterations/stop_reason/final_patch_id/wns/wns_history/接受补丁链/`sta_used` 全等）→ S-off 路径完全惰性（`code/scripts/verify_s_off_reproduces_l2.py`）。
  - **S 真的执行了**：7/8 电路（除 `s641`）累计成功抽窗 **469** 个、产出并实测候选 **37** 个；`s641` 是"报价 72 窗但**成功抽窗 0**"（r2 §4.2 不变量拒绝）→ 属**程序/几何**原因，与能力结论必须分开。
  - **结果：接受 0/8 电路**，且两臂 `dWNS`、`maxB(k)`、`k₁st`、接受数**逐位相同**（8/8 电路 `diff = 0.000`）；两臂 `sta_used` 最大差 +8、16/16 run 均停在 `max_iterations` → **预算不绑定**（排除"S 被饿着"的第一层）。
  - **机制解释（关键表）**：37 个候选 **ΔL(BLIF)>0 为 37/37**、**ΔL(SKY130，权威层)>0 为 16/37**、**ΔWNS>0 为 0/37**，且 **ΔL(SKY130)>0 且 ΔWNS>0 = 0/37**；R_S 判定 ok 33/soft 4；变体全为 S0（S1/S2 与 S0 逐位相同 → §4.7 DROP）。→ **不是"降到错的那一层"能解释的**（那只解释 21/37），而是"**被割选中的窗口不在真正的时序关键锥上**，窗口内结构变浅传不到端点 WNS"。
- **判读**：在当前 regime 下 **S 是可选候选类型，不是独立贡献**——与 L2 的 EMA 封板结论同形（增量来自候选构造 + 加权排序 + 验证纪律，而非新增搜索维度）。**反向加强 §4.8 的论证**：即使 S 产生 ΔL>0、甚至权威层 ΔL>0，也未必换成 ΔWNS>0 → "结构深度下降"不是"时序改善"的可替代指标。
- **必须同时声明的边界**：① **已完成**加宽分配对照（`--resynth-per-iteration 4`，8/8 电路）：配对差仍全 `0.000`、接受数仍 0/8，候选仅 37 → **39** → **"S 被饿着"被排除**；并定位到真正瓶颈是**可用窗口集合**（窗口身份 `(netlist_hash, boundary_key)` 去重 ⇒ 可触及窗口上界 ≈ 不同 `G_r` 个数 × 每 `G_r` 割边界数，而 `G_r` 只在接受时改变）→ **加大配额无用，只能改窗口来源**；② r2 §4.9 的 `S→G` 一档**有意未实现**（避免同时改两件事破坏单变量对照，契约 §8.13.4）→ 结论仅针对**纯 S 候选类型**；③ **割选窗仍未做时序加权**（用的是与 R/G/B 相同的割候选）——这既是被实测定位到的瓶颈，也是下一步真正的杠杆；④ 上游在该 regime 已把可用增益吃得较满。
- **待裁定**：(A) 把 S 作为**独立贡献**写入 §4/§5（现有证据不支持，需先实现时序加权选窗）；(B) **如实降级为可选候选类型**并与 L2 封板结论合并叙述，主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」。**当前证据倾向 (B)。**
- **【2026-09-28 新】瓶颈定位到具体代码行（比 ① 的"窗口身份去重"更精确）**：`flow.py` L626
  `round_candidates = list(candidates[:max_candidates_per_iteration])` **截断**加权割列表，
  而 L890 的 S 循环**复用的正是这个截断列表** ⇒ **S 的窗口宇宙 ≤ `candidates_per_iteration`（=8）/
  每个 `(G_r, cone)`**，与 `resynth_per_iteration` 无关。实测（`20260924_l3s_ablation` vs `_k4`）：
  配额 1→4 只使候选 **37→39（+2，仅在 s420）**，7/8 电路逐位相同，触及轮数由 ~7 轮压到 ~2 轮
  ⇒ **配额只改变"摊入几轮"，不改变池子**。去重命中率佐证：s713 `offered=123/extracted=105/新窗口=7`
  （**93% 是同一批割边界被重复走过**）。
  ⇒ 现有"接受 0/8"只覆盖到"**在 R/G/B 的 top-8 割边界里 S 无可接受候选**"，**不可外推为"S 无贡献"**
  —— OI-014 的现有证据**被这一集成缺陷混淆**。设计见技术设计 **§13**（L1 池子规模 / L2 时序加权选窗 /
  L3 曝光轮数；预锁定验收判据见 §13.4）。
- **【2026-09-28】池子普查结果 —— 并**修正**了上面的归因**：只读插桩 `s_stats["pool_census"]`
  （仅 S 开启时记录，{S off} 产物逐位不变）在 **s382/s713/s832/s953** 四电路上给出
  **`len(candidates) = 9`、`len(round_candidates) = 8`** —— ⇒ **L626 的截断只损失 1 个窗口**，
  **不是瓶颈**；真正封顶的是 **L607 `_cone_candidates(..., k=max_candidates_per_iteration)`**：
  **枚举本身只被要求返回 8 个**（+1 前置关键路径 cover = 9）。
  ⇒ **修正 L1**：扩池必须**用更大的 `k` 重新枚举**（S 专属第二次枚举），
  **不能**实现为"加宽 `candidates[:W_s]` 切片"（切片只会从 9 变 9）。
  —— 这是"最便宜的先做"在设计被实现前就纠正它的收益。
  **补充普查（✅ 已完成）**：`candidates_per_iteration = 32` 时未截断列表 = **33**（s382/s953 一致）；
  s420 全 20 轮恒为 **9** ⇒ 关系为 **`len(candidates) = min(k+1, 该锥体的可计分割空间)`**
  （未饱和时与轮次/cone/`G_r` 无关）。
  ⇒ **枚举随 `k` 线性增长 ⇒ L1 成立**（给 S 一次 `k=32` 专属枚举即可把窗口池 8 → 32，**4×**），
  无需改 cone / 深度切分。**可引用表述**：S 的可触及窗口上界 = 不同 `G_r` 数 ×
  `min(candidates_per_iteration, 割空间)` —— **S 的触达范围被 R/G/B 的束宽直接决定**（小锥体除外）。
- **【2026-09-28】闭合反例：小锥体**饱和**，`k+1` 不是上界（L1 重跑暴露）**：`s27`（10 门，目标锥
  G10 极小）在 `k=8` 与 `k=32` 下 `len(candidates)` 均为 **6**（`pool_census` = `[3,6,6,…]`，20 轮），
  L1 重跑中 `window_pool=32` 但 `window_pool_offered` 仍 **6**、S 候选仍 2、接受仍 0。
  ⇒ L1 对"割空间 < `candidates_per_iteration`"的电路**天然惰性**（非失效，是无可扩余地）；
  **判定 L1 有效性必须排除饱和电路**。报告 `reports/FAECO_S_WINDOW_CENSUS_20260928.md` §3.1。
- **【2026-09-28】L1 已实现并重跑**（`resynth_window_pool`，严格惰性守卫，2 项新单测）：
  `experiments/20260928_s_l1_ablation/`（8 电路 × {off,on}，`on` = `--resynth-per-iteration 8
  --resynth-window-pool 32`，两臂 `--sta-budget 1600`）。
- **【2026-09-28 ★ L1 全量裁决：NEGATIVE（能力型）⇒ 裁 (B)】** 报告
  `reports/FAECO_S_L1_WINDOW_POOL_20260928.md`；工具 `code/scripts/summarize_s_l1.py`。
  8 电路 × {`off`,`on`}，16/16 `ALL_RUNS_DONE`，`on` = `--resynth-per-iteration 8
  --resynth-window-pool 32`，两臂同 `--sta-budget 1600`（**两侧都不绑定**，max 482）。
  - **纪律全过**：① 控制臂 8/8 逐位复现归档 `off`（`mapped.v`/`patch_id`/`wns`/停因/预算台账）；
    ② **单变量干净 8/8**：两臂**非 S（R/G/B/JOINT）试验序列逐位相同**
    （s27 416、s382 769、s420 1048、s641 596、s713 306、s820 312、s832 306、s953 393）；
    ③ 惰性单测 11 passed。
  - **第一层 enumeration ✅**：`s382 8→32`、`s420 1→6`、`s713 7→22`、`s820 6→14`、
    `s832 5→17`、`s953 8→33`；**37 → 126（3.4×）**。`s27` **SATURATED**（池只有 6）、
    `s641` **NO-ENGAGE**（抽窗 0）。**机制被完全解释**：历史 s382/s953 候选数**恰好 = 8 = 池上限**；
    L1 后 = `resynth_per_iteration`(8) × 参与轮数 ⇒ **历史 S 候选数被池子钉死**。
  - **第二层 candidate quality ⚠️**：`ΔL(SKY130)>0` 由历史 43% 升到 **76/126（60.3%）**
    ⇒ 新窗口**更常真的降低权威层深度**；但 **`ΔWNS>0` = 0/126**，且 **90/126 的 `ΔWNS<0`**
    （多数候选**反而让 WNS 变差**）⇒ **问题不在 L1，在 S transformation quality**。
  - **第三层 repair capability ❌**：**接受 0/8**、配对 `ΔWNS(on−off)` **全 0.000**。
  - **固定指标集（纪律）**：`N_unique_window` = `N_S candidate` = `N_measured` = **126**
    （**无重复窗口哈希** ⇒ 126 个候选来自 126 个不同窗口，扩池是真探索）；
    `N_extracted`=1724 ≫ 126 ⇒ 印证该字段是**重复扫描**指标，**不作**"搜索空间扩大"的证据。
  - **判定**：**枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime 下没有体现 timing repair
    capability** ⇒ **(B)**。**明确不做**：不再扩池（32→64→128，池已用满且非瓶颈）。
  - **下一步（§13.7）**：转 **S 候选质量归因**——为什么通过 CEC 的 S patch 没有 timing gain？
    (i) 窗口内 depth 是否真的下降（已部分回答 76/126）；(ii) 映射后 depth 是否又回来；
    (iii) cell delay 是否变差；(iv) fanout/cap 是否抵消结构收益；(v) critical path 是否不穿过窗口。
  - **⚠️ 待查（不影响上述结论）**：s420 报 6 候选 + 6 条变体级拒绝 `W_STRUCT_ERROR`（均标 S0），
    但磁盘上只有 8 窗口 × {S0,S1,S2} ⇒ `rejections` 台账在 s420 上**未闭合**，见 **OI-017**。
- **【2026-09-28 用户三层裁决口径（已执行）】** 不直接看最终 WNS 一项，按三层顺序裁决；
  **不得因"L1 扩池成功、候选数明显增加"就把 S 升格**：
  - **第一层 enumeration（L1 自身是否有效）**：非饱和电路上 `N_S,L1 > N_S,old`。
    成立 ⇒ 只证明"**L1 的 enumeration bottleneck 被真实解除**"，排除"S 没效果只是因为从未获得
    足够候选"这一解释。**不构成 timing capability**。
  - **第二层 candidate quality（问题是否已不在 L1）**：看 `N_CEC pass`、`N_measured`，
    以及 S 候选的 `ΔWNS` **分布**。若枚举涨 3× 但全部 `ΔWNS ≤ 0` ⇒ **问题在 S transformation
    quality，不在 L1**。
  - **第三层 repair capability（决定 OI-014）**：`N_accepted,S > 0` 且至少一个电路
    `ΔWNS_on−off > 0`（最好同时 `ΔL < 0`）。
  - **判定规则**：达到第三层 ⇒ 才有资格重新考虑 (A) 独立贡献；若 `N_accepted,S = 0`
    ——**即使 S 候选 37 → 100+**——结论仍为"**枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime
    下没有体现 timing repair capability**" ⇒ 选 **(B) 降级为可选候选类型/探索性能力**。
  - **负结果的处置**：若出现"候选 37→100+ 而 accepted 仍 0"，这是**有价值的负结果**；
    **不得**再把 window pool 32→64→128 继续扩大，而应转向 **S 候选质量归因**：分解
    (i) logic depth 是否实际下降；(ii) 映射后 depth 是否又回来；(iii) cell delay 是否变差；
    (iv) fanout/cap 是否抵消结构收益；(v) critical path 是否根本不穿过被重综合窗口。
- **【2026-09-28 指标口径纪律：不得再用 `windows_offered` 作 L1 主证据】** 它包含**重复扫描过的
  割边界**（s27 的 114 ≈ `19×6`），不是 unique window 数。L1 报告固定看：
  `N_unique_window`（按 window/canonical hash 去重）、`N_extracted`、`N_S candidate`、`N_measured`、
  `N_accepted` —— **其中后四个最关键**。`windows_offered` 只保留作**内部扫描开销指标**，
  **不承担"搜索空间扩大多少"的解释责任**。
- **论文改动一律等裁定后一次性进行**（本轮仍未触碰任何 `.tex`）。

### OI-008 明细（2026-09-23 代码—论文对照，含实测触发分布）

> 【2026-09-30 加注】下表"旧版事件名，当前 `code/` 已无此字符串"的说法在 **0a 步骤 4 合并（`258f588`）后已过时**：现行 `real_wns.py:1864` 仍以 `acceptance_budget_violation` 写试验台账（另有姊妹事件 `acceptance_budget_unavailable`）。差异的正确表述是**两层命名分工**（工具层事件名 ↔ 方法层 F4 分类名），非"产物与代码不一致"；已成文为 `paper/zh/submission/supplementary/S1_失效事件名映射说明.md`。下表按历史快照保留。

**实测触发分布**（权威源：`experiments/20260826_itc99_main/b*/b*/eval_trials.json`，19 电路 / 4044 trials，探针 `scratch/count_failures.py`）：

| 产物事件名 | 次数 | 对应 FailureType（`failures.py`） |
|---|---:|---|
| `acceptance_budget_violation` | 2434 | **F4** `F4_timing_gain_insufficient`（`failures.py:47` 判定"未满足接受判据"）——**旧版事件名，当前 `code/` 已无此字符串** |
| `F5_verification_too_expensive` | 915 | F5 |
| `F1_equivalence_failure` | 138 | F1 |
| `F3_patch_too_large` | 16 | F3 |
| `F2_boundary_invalid` | 3 | F2 |
| `F6_physical_load_failure` | 0（本实验） | F6（仅物理门控实验触发） |

| 项 | 论文表述 | 代码实际 | 性质与影响 |
|----|----------|----------|-----------|
| F1 局部功能/结构失败 | 表 tab:failures F1 行仅写"增加边界惩罚 $\lambda_b$" | `refinement.py` L41–46：`boundary_penalty += 1.0` **且** `equivalence_stability_reward += 1.0`（对应式(2) 扇出项 $\lambda_f$） | **论文漏写一项**。F1 在主实验中实测触发 **138 次**，即该反馈动作**实际生效**，属实质遗漏而非纯表述问题 |
| F6 SPEF 复测失败 | 表 F6 行写"增加边界惩罚 $\lambda_b$ **与尺寸惩罚 $\lambda_s**" | 当前 `code/` 仅 `boundary_penalty += 1.0` | 论文**多写**一项。但 F6 由 20260807 物理门控实验（旧内环代码路径）触发，**当时是否实现了 $\lambda_s$ 增量尚未溯源**，不能排除"重构后丢失" |
| $\lambda_c$ 作用 | §3.3 文字："用于调整关键路径覆盖割 $C_c$ 的排序优先级与覆盖得分权重" | 该用途成立（`cut.py` L270/L291），**另有**节点代价分母折扣（`cut.py` L193，仅 `r_ok` 门，式(2) 未列该项） | 表述**不完整**，非错误 |
| 事件命名可追溯性 | — | 主实验产物用旧名 `acceptance_budget_violation`，现代码输出 `F4_timing_gain_insufficient` | 语义一致（已核实 `failures.py:47` 判定条件相同）；但产物与当前代码字符串不一致，投稿前建议在论文或补充材料中说明，避免审稿人对照代码时困惑 |

影响评估：**所有已发表数字不受影响**（事件名映射语义一致，F4 占比 60% 与论文"主循环主要由 F4 驱动"相符）；需处置的是 F1/F6 两行的反馈动作描述，其中 F6 行需先溯源 20260807 实验代码。

## 已关闭（近期）

| ID | 问题 | 关闭说明 |
|----|------|----------|
| OI-005（主体） | 旧仓库副本 | 2026-09-12 内容全删（LOG-20260912-02），仅剩空壳 |
| — | §4.3.1 数据混源 | 2026-09-11 一致性审计修复（d329f19） |
| — | C 盘分支处置 | 3 个 worktree 删除前推送固化 + 抢救 2 份未提交文档（archive/phase0_worktree_salvage_20260912/） |
| — | 网络阻塞推送 | 已恢复，全部提交已上 origin/main |

## r26继承说明（LOG229）

用户纠正r25的5页主稿压缩过头，r26需要完整论文，只突出主线/删冗余，并重做示意图；不是科学新实验授权。r25稿面规则修正仍保留，但新的全文/图件须单独构建验收。四partial/D28/56raw3/8/四态/原raw OI051等继续open，无新EDA/production或HEAD变化。

## r27文档精确灰度门已验（LOG256；原生AI RGB残留明记）

两原生AI PNG等通道比例70.525169%/78.446261%、spread11/12保持原件。最终主/补PDF已实际DeviceGray导出并实测19页ICC-off RGB差0，native图尺寸/链接数及非空白字形序列保留；文档精确灰度门已验，原生RGB门未修复而保留明记。根全19页视觉、6canonical及FINAL_DELIVERY10701c76已验交付，不留本轮样式待办；样式门不关闭任何科学OI。

## OI-052（2026-10-24，open）— 物理"结构特征/拓扑效应"结论出自部分标注的 ITC-99 族，须批次收齐后重算

**现象**：LOG-20261024-14 的结构特征代理检验与拓扑效应分析是**探针级**结论，但 ITC-99 侧的
布线后标签只覆盖 833/1207（I0 批仍在跑，I1 未开；可用池 20 个且 b01 占 8 个），布局后标签当时仅 6 行
（工具已按 `--stages auto` 显式降级为 ideal+routed 并在报告里打印 `*** STAGES DROPPED ***`）。

**现状更新（LOG-20261025-36，2026-10-25）**：本容器里前若干条是用**条件句**写的（"I0 批仍在跑，I1 未开"、
"批齐后重算"、"I1 收齐后须复核"、"待重算"）。**这些前提现在全部兑现**，按产物逐条更正如下。
**本容器仍然 open，下面的更新不等于其中任何一条未决被关闭**——被更正的是"条件还没到"这一层，
不是"问题已解决"那一层。
  * **批次已收齐**（`experiments/20261024_physical_labels_itc99/band_scope.json` → `sections.coverage`）：
    I0 **1207/1207**、I1 **1207/1207**（coverage 1.0、complete=true），
    I0P0 / I1P0 各 **58** / **58**；
  * **判定带的作用域已是 `full_family`**（同文件 `sections.scope`：f0_batches=I0、
    f1_batches=I1，理由是"两个键集一致且逐键有标签"）→ 第 14 条要求的复核**已执行**：
    布线后 2σ **0.049753 ns**、布局后 2σ **0.029826 ns**、带宽比 **1.668108**
    （旧 pilot 口径的布线后带是 0.087495 ns）；
  * **第 4 / 6 条要求的后续重算已在全量标签集上跑过**：`stage_verdict_transfer.json`
    （ITC-99 训练表 **1207** 行 / 两档齐全 **1193** 行 / **7** 电路；
    ISCAS89 **339** / **325** / **8**）与 `topology_effect.json`
    （ITC-99 行 1207 / 带布线后标签 1193、池总数 **47**、
    含 ≥2 候选的池 **41**；ISCAS89 行 339 / 325、
    **34** / **26**）→ 第 1 条当初预警的"池数与电路数会变、**数值会变**"
    **确实兑现了**（旧读数出自 20 个池、4 个电路）；重算后的判决见第 15 条；
  * **第 22 条的复核项全部满足**（`project_docs/evidence/r30_f2_third_impl_20261025/f2_chain_receipt.json`
    → `source.f2_labels_summary`）：`digest_convention_check.n_unmatched == 0`、
    `candidate_self_check.passed == true`（`candidate_marginal_coverage == 1.0`）、
    F2 批 **1207/1207** 解析成功、边际量覆盖 **1193**（0.988401）、
    `missing` 为空（0 项）→ **本条不再是"待复核"项**；
  * **第 20 条**（F2 待跑）已于 LOG-20261025-28/30/31/32 更正为"已收齐"。
  * **仍然未决的**（不受本次更正影响）：第 2 条的"偏好消失"正式检验、第 3 条的改动量与类别纠缠、
    第 5/5-bis/5-ter 条的双实现与第三实现问题、第 8 条的逐电路复核、第 9 条的池级偏差量化、
    第 11 条的电路间离散度、第 16 条的池级指标分辨率、第 17 条的改述、第 18 条的 AUC 功效下限、
    第 33 条的"单轴为何在某些电路上完全无效"、以及第 34 条起新增的机制与口径条目。

**具体未决**：
1. **拓扑效应**（池内"加逻辑深度"理想 12:2 p=0.0129 vs 布线后 7:2:5 p=0.7744；跨类 G vs R 10:1
   p=0.0117）出自 20 个池、4 个电路，样本偏小且偏斜；I0/I1 收齐后可用池数与电路数都会变，
   **数值会变**。
2. **"偏好消失"未做正式检验**：现有读法是"一个显著、一个不显著"，**不等于"两者之差显著"**；
   且布线后标签噪声受限（782 行里只有 183 行超出候选级带 0.087496 ns），**衰减是可能方向**，
   故当前只能读成"与虚假繁荣**一致**"，**不是证明**。
3. **结构改动量与候选类别纠缠**（插 buffer 按定义就加单元），本测量**无法完全分离**二者。
4. **ISCAS89 族的结构性否定带族特异性**：该族候选全是单胞驱动强度替换、拓扑不变
   （`d_depth`/`d_n_cells`/`d_max_fanout` 全为常量），26 个池的"结构变化量"全部一致、**全部被排除**；
   该族**不能**用来否证"GNN 路线"，只能用来确认"该族无结构变化可测"。

**解除条件**：ITC-99 的 I0 / I1 / IPLACEDF1 三批收齐 → 重跑 `run_analysis_itc99.sh`
（已含 `extract_graphs` 与 `topology_effect` 两步）→ 由定稿链写 LOG-20261024-12 时重算并复核这四条。
在此之前，**LOG-20261024-14 的 ITC-99 数字一律标注"部分标注族"**。

**边界**：本条不构成对 GNN 路线的否证——实测的是**手工标量图摘要**，"图里无信号"只对这些摘要成立，
**不得**外推为"神经网络不可行"。
5. **真实双实现配对仍太稀疏**（LOG-20261024-15）：44 个配对候选**每个池只有 1 个**，
   池内"平均两次测量 vs 单次测量"的真实比较**尚不可做**（ISCAS89 仅 3 个池，且两个选择的遗憾都是
   0.0000）；目前只能给出候选级的经验 σ（ITC-99 0.0232 ns、ISCAS89 0.0134 ns）与模拟下界。
   解除同样依赖 I1 / F1 批覆盖全族。

**补充（LOG-20261024-15 / LOG-20261024-16，两次）**：本条之外还新增了一条**决定性的负结果**——
在当前标签分辨率下，**能证明的改进空间比噪声高一数量级地小**：被接受候选（FAECO 实际做的事）的
可证明遗憾 ISCAS89 **0.0000**（观测遗憾 0.0072）、ITC-99 **0.0033**（观测遗憾 0.0148，**占 22.5%**），
阈值扫描下始终 ≤0.0100 ns；而对照组"靠结构改动量选候选"的可证明损失是 **0.0673 / 0.0753** ns。
**口径更正**：LOG-15 报的 ITC-99 "0.0000" 是**部分标注族**（20 池 / 833 标签）的读数，扩样到
30 池 / 946 标签后变为 **0.0033 ns（占 22.5%）**；"完全为 0"的说法**已作废**，核心结论（没有可供
学习模型夺取的空间）**保持**。**这不改变 OI-052 的解除条件，但改变了优先级**：先提高分辨率
（同一网表跑第二个物理实现），再谈模型。

**补充（LOG-20261024-17）**：本条新增两项未决，与前四条并列，**解除条件同样依赖批次收齐**：

6. **跨阶段判定转移结论（LOG-17）出自部分标注族**：布局后档作为接受判据的证伪率 0.133333（ITC-99）/ 0.159574（ISCAS89）、漏放率 0.097844 / 0.10119，均在**布线后 946/1207、I0 在跑、I1 未开**的标签集上测得；批齐后由定稿链重跑 `stage_verdict_transfer.py` 复核。
7. **"零矛盾"已被证明是带宽口径的产物，且两档测的几乎是同一个量**：各档用各自带时两族均零矛盾，但同带口径下 ITC-99 有 19 例矛盾、纯符号口径下 73 例（8.2%）；电路内回归斜率均值 0.951954 / 0.930217、R² 多在 0.89–0.97 → **布线阶段主要是逐电路偏移**。这意味着**最终验收不能用布局后档替代**（布局后接受的候选有 0.133333 / 0.159574 会被布线后证伪）。**"监督可替、判定不可替"这一分工目前只在部分族上成立**，须在完整标签集上复核。

**逐电路配对的补充**：LOG-17 里"布局后判据优于理想判据"的池化差异（13.3% vs 23.3%）在**逐电路配对上不成立**（3 胜 2 平 2 负，p=1.0；ISCAS89 方向相反），故该差异**不作为结论**，只作为池化读数记录。

**补充（LOG-20261024-18）**：本条再新增两项未决：

8. **"布局后档误判某类候选"的读法未成立，须在完整标签集上复核**：族级 B 类符号翻转率 23.2% 高于 R 类 7.3%，但**逐电路配对不通过**（B vs R 1 胜 3 负 p=0.625、B vs G 2 胜 4 负 p=0.6875），且剔除量化边沿后翻转率塌到 B 6.5% / R 0.6% / JOINT 0.0% → **不作为 kind 效应结论**。批齐后须由 `stage_kind_effect.py` 重算并复核。
9. **布局后档偏差的"池级"成分远大于"kind 级"**：b09 的 53/87 个候选集中在第 8 轮迭代，该池整体偏移 +0.07283 ns（族内其余池多在 ±0.02 ns 内），且**同池内非 B 候选的翻转率与 B 候选几乎相同** → 偏差是**逐池的**，不是**逐种类的**。这意味着"按 kind 特判"不是有效的改进方向，**同池重新标定**与**提高读数分辨率**才是。但"同池标定"需要同池的布线后标签，在只有布局后标签的实战里不可得 → **这一约束尚未被量化**，登记为未决。


**补充（LOG-20261024-19）**：第 5 条（真实双实现配对）**从"等批次"升级为"需要第三个布线实现"**：

5-bis. **"单次测量 vs 两次实现平均"的真实比较需要第三个布线实现**：留一法（留一个实现当评分器、选择器只用留下的实现）是唯一不偏袒选择器的做法；但**只有两个实现时它会退化**——留进的只剩一个实现，"平均选择器"变成"单次选择器"，比较必然是平局。实测 ISCAS89 的 3 个池两方向遗憾均 0.00000 ns、选中同一候选；ITC-99 为 0 池。**因此 LOG-15/16 的"跑第二个实现更有效"目前只有蒙特卡洛模拟支撑，不是实测。** 若要做实测，需**第三个布线实现**（I2 批），建议**只跑有 ≥2 候选的池**以控制代价；在此之前，**不得把模拟下界当实测引用**。

5-ter. **I1 批次还决定判定带的样本量（比原设想更基础）**：候选级带（2σ = 0.087496 ns，df=44，51 个网表）决定了全项目每一个 GAIN/INCONCLUSIVE/REGRESSION 判定；**I0/I1 与 I0P0/I1P0 是同一物理实现轴**（F0: pins met3/met2 util 10；F1: pins met5/met4 util 30，同冻结版图，58/58 netlist 哈希相同），**I1 跑完后 1207 个候选全部可配对，样本量约 20 倍** → 判定带会收紧，**LOG-14/15/16/17/18 的每一个依赖带的结论都要重算**（定稿链已挂好重跑）。**这是 I1 批次的第二重价值。**



**补充（LOG-20261024-20）**：本条再新增六项未决，都**不是"等批次"**，而是"链子本来就不会自动变"：

10. **判定带的样本作用域从未显式化，且布局后带此前测在半成品上**：
    - 布线后带一直在 pilot 子集上（I0P0 / I1P0，58 键 / 51 对 / df=44），**全族 I0 / I1 的 1207 个候选从未进过带计算**——工具里 `F0_SIDE` / `F1_SIDE` 写死为 pilot。已改为按覆盖度自动选择作用域（`full_family` / `pilot_subset`），并把作用域写进 `candidate_level_noise.json`；**I1 收齐后必须确认带确实切到了全族**。
    - 布局后带此前是在 **IPLACEDF1 只完成 749/1207（覆盖 6/9 个电路）** 时算出来的，2σ = 0.024052 ns；补齐到全量（1207 对 / 9 电路 / df=1198）后 **变宽到 0.029826 ns（+24.0%）**，带宽比（routed/placed）由 3.637785 降到 **2.933514**。**因此 LOG-14/15/16/17/18 中每一个依赖带的口径都必须重算**，其中 LOG-17 引用的 "3.64 倍带宽不对称" **数字作废**。
11. **电路间离散度在家族内差约 3.8 倍，"家族单一带"是伪概念**：布局后带逐电路 sd 从 b13 0.008633 到 b09 0.032812（max/min ≈ 3.80），被漏测的 b09 恰是离散度最大的电路。布线后带在 I1 收齐后须同样检查。任何"用家族带判 GAIN/REGRESSION"的结论都必须写明用的是**池化带**还是**逐电路带**（`band_sensitivity.py` 已同时给出两种口径），否则同一个候选在不同口径下可能得到相反判定。
12. **同实现重跑的可复现性底噪 = 0.000000 ns**（I0P0 vs I0 共 58 个、I1P0 vs I1 共 8 个可比键逐位相同）→ 布线确定性成立，候选级带里**不含运行噪声成分**。推论：**"重跑同一实现"对降低不确定性毫无帮助**（物理上的零，不是方法退化）；这与第 5-bis 条"需要第三个布线实现"是两条独立证据，指向同一件事。
13. **kind 效应在扩样后仍不成立，且新出现的"显著"是口径产物**：逐电路配对在"工具口径"（0.00 与正数也算翻转）下 G vs R 为 0 胜 6 负、p=0.03125，**看起来显著**；但**严格口径**（两值非零才算翻转）p=0.21875、**去量化边沿** p=0.21875、**池内配对** p=0.453125 → **四道门只过一道，判定为口径产物，不作 kind 结论**。新增 `kind_gate_probe.py` 把双口径 + 三道闸固化为正式工具并入链。**教训：翻转率这类统计量对"零值怎么算"敏感，任何 kind 级读法必须同时报两种口径。**
14. **判定带的作用域已改为数据属性，但规则本身要在 I1 收齐后复核**：I1 收齐后**必须确认** `band_scope` 从 `pilot_subset` 切到 `full_family`，并**重算** LOG-20 表中的全部前后对照数字。**注意：本次修正来自"IPLACEDF1 半成品"，不是 I1；I1 到位后布线后带还会再变一次。**
15. **"理想线网偏爱加逻辑深度"这一诊断在扩样后失去统计支持**（理想口径 p=0.0931、布线后口径 p=0.3833，两档都不显著），而**跨类判断在两档都显著**（布线后 B vs R p=0.0013、G vs R p=0.0023）→ **LOG-14 的诊断须修正为"理想线网对候选种类的判断与物理一致（继续成立）；深度偏好不成立"**。注意这是**"不显著"而不是"证伪"**，样本仍不足以排除中等效应，**须在 I1 收齐后的全族上复核一次**。

**补充（LOG-20261024-21）**：本条再新增五项未决，全部**与"等批次"无关**，而是"结论本身的适用范围"：

16. **池级决策遗憾指标在本族没有分辨率，所有以它为口径的模型比较都无效**：全部选择器在 25% 验证预算下的平均遗憾落在 **0.004146 – 0.029268 ns**，而判定带是 **0.087496 ns**（布线后）——**所有方法差异都低于测量分辨率**。LOG-14 的"纯图特征≈随机"因此**不是模型结论而是指标失效**。**规矩：任何模型比较，先检查指标量纲是否超过判定带；不超过就没有分辨率，结论一律不成立。**
17. **"理想线网说谎"的强版本作废，须改述为"避害有效、增益无效"**：接受判据有真实物理选择性（增益富集 ITC-99 18.6533 倍 / ISCAS89 8.9446 倍；损害比 0.2194 / 0.1855；置换 p ≤ 0.0035，两族两档均如此，逐电路方向一致），但**接受集里 84.0909%（ITC-99）/ 69.2308%（ISCAS89）的候选物理惰性**，真实增益只有 11.3636% / 26.9231%。**论文表述受影响：不能再写"理想线网判据与物理无关"，也不能写"接受了 N 个候选因此改善了 WNS"；能站住的说法是"在接受候选中避免了多少可分辨的真实退化"。**
18. **候选级 AUC 有功效下限，必须先报正例数**：`gain` 标签布线后只有 12 个正例、布局后 23 个，AUC 在两档之间**方向相反**（布线后 0.226244 / 布局后 0.849456）→ 纯噪声。工具已加 `powered` 标志（正例数 < 30 即 `POWERED=False`）。**规矩：任何以 AUC / 分类率为指标的结论，必须同时报正例数与 CI；正例数 < 30 的格子只能当噪声。**
19. **门级图结构在候选级没有物理信号，且加到标签上有害**：两族 `structural` 的 AUC 分别为 0.444433 / 0.43676（均低于 0.5），且 `ideal_only` → `structural_plus_ideal` **两族都变差**（0.885202 → 0.83832 / 0.757152 → 0.655166）。→ **"训练 GNN 替代 OpenSTA"在本族没有可夺取的空间**，真正的杠杆是把便宜的布局后档当监督信号（LOG-16"监督可替"的候选级确认，布局后标签单特征 AUC 0.926597 / 0.746578）。**但注意边界：这里用的是门级图的标量摘要，不是图编码器，"图结构无信号"不能外推为"GNN 无信号"**——若要否证 GNN 路线，必须用真正的图编码器再测一次。
20. **F2（第三个布线实现）已收齐：1207/1207 作业完成（第三实现覆盖率 1.0），原解锁条件已由第 29／32／33／34／35 条承接**：作业表已备好（1207 作业，pin 轴 F2 = met3 横 / met4 竖，与 F0 只差纵向、与 F1 只差横向；identity check 不匹配 0、缺失网表 0），实测代价外推 **2–4 h 墙钟**（PAR=6）。它同时解锁：① **判定带稳定性**——三个实现给出三组配对差，可检验"带"是不是只有两个实现时的偶然；② **留一法选择器比较**——LOG-19 已证明两个实现时留一法必然平局。**注意 F2 刻意不注册进 `build_dataset_itc99.py` 的 `BATCHES`**（主数据集与判定带定义不因侧实验移动），跑完后须由独立工具读 `runs/I2`。


**补充（LOG-20261024-22）**：本条再新增两项未决——一项是**判定带换值的量级已经可以预告**，一项是**F2 标签链必须复核**：

    - **补充（LOG-20261025-28/30/31/32）**：本条的"待跑"已过期——F2 批 **1207/1207** 作业全部完成（第三实现覆盖率 1.0，标签 1207 条，其中带边际量 1193 条、覆盖率 0.988401），收据与三套证据包俱在。**本条不再是"F2 待跑"，而是"两项结论的解锁条件已满足"**：
      - 判定带稳定性 → 第 29 条（全族 max/min 1.476087）与第 32 条（共同非退化子集上 该比较被混淆、C2 必须撤回）；
      - 第三个实现的部分退化 → 第 33 条；
      - C3 的机制定论 → 第 34 条；
      - 单轴敏感度与判决的量子格 → 第 35 条。
    - **边界**：运行与记录状态更新，无新科学结论；`code/` 未动、HEAD 未变、未提交。

21. **布线后判定带将从 pilot 口径切到全族口径，且收窄幅度已可预告（这会改动 LOG-21 的每一个数）**：
    在 I1 侧完成 **1058/1207（覆盖率 87.66%）** 时，`band_scope_itc99.py` 的 `full_family` 口径已给出预览值
    **2σ = 0.050419 ns**（池化 sd 0.025209，df=1046，1052 个候选网表，6 个电路），而当前生效的 pilot 口径是
    **2σ = 0.087496 ns**（df=44，51 对，7 电路）——**收窄约 42%**。带宽比（routed/placed）随之由 2.933514
    降到约 **1.69**。**后果**：① LOG-21 的**可分辨正例数 243 会明显增加**（门槛变窄），AUC 的 CI 会随之变宽
    或变窄，**四道闸的通过与否可能翻转**；② **接受集的三分拆（真实增益/损害/惰性）会重排**，"惰性比例 84.09%"
    这类读法大概率下降（门槛放宽后更多候选被判为"可分辨"）；③ **GAIN/REGRESSION 判定本身会变**，故 LOG-21
    的第 17/18/19 条结论**全部处于"待重算"状态**，不得在定稿前当作定论引用。
    **同时确认了一件好事**：作用域闸门在覆盖率 87.66% 时**仍然守住 `pilot_subset`**（理由写明"I1 侧不完整：
    缺 149/1207 个标签"），**半成品没有被提升为族带**——这是 `select_scope()` 按实际覆盖度选择的直接效果。
    **解除条件**：I1 收齐 → 定稿链重跑两族分析链 → 复核 `band_scope.json` 的 `scope.selected` 确为
    `full_family`，并重算第 16–20 条与本条引用的全部数字。

22. **F2 标签构建链曾有一个静默丢标签的缺陷（已修，但复核项仍在）**：ledger 的 `base_netlist_hash` 用的是
    **文本模式**摘要（`Path.read_text()` 的通用换行转换，CRLF 变 LF 再编码），而 `build_f2_labels.py` 原本只
    索引**字节**摘要——实测 47 个不同的 ledger 基线哈希中字节口径只命中 41 个，**1193 个候选里 39 个
    （3.27%）** 的迭代基线（6 个带 CRLF 的电路级 `mapped.v`）查不到，那 39 个候选会**静默失去边际量**，
    而批次 rc 全 0、标签文件覆盖率看着像 96.7%、**没有任何地方报错**。已改为**双摘要索引**并加**两道自检**
    （摘要口径自检在任何 run 之前即可算；空列自检在批次完整后生效）。**复核项**：F2 批次跑完后，
    `f2_labels_summary.json` 必须同时满足 `digest_convention_check.n_unmatched == 0`、
    `candidate_self_check.passed == true`，且 `candidate_marginal_coverage` 接近 1——**若仍有一批候选缺边际量，
    说明同一类缺陷以别的形式复发**，此时 F2 的三点比较与带稳定性结论**一律不得引用**。


**补充（LOG-20261024-23）**：本条再新增一项未决——**判定带收窄后，LOG-21 的结论必须分层改述，而不是整体重写或整体保留**：

23. **"图结构无物理信号"与"增益无效"这两句话在收窄的带下部分失效**：
    - 预演（对照遍精确复现存储产物：20 项检查、0 处不符、最大偏差 0.0；训练表固定，只变门槛）：
      **`resolvable` 标签**（正例 243 → 389）下 `structural` 0.444433 → 0.445175（CI 仍含 0.5）、
      `placed_only` 0.926597 → 0.894462（仍是单特征最强）、`structural_plus_ideal` 0.83832 → 0.751665
      （与 `ideal_only` 0.854611 的差距由 0.047 扩到 0.103）→ **"加到标签上有害"更成立**；
      **`harm` 标签**方向不变。
    - **但 `gain` 标签翻号**：正例 **12 → 37**（跨过功效下限 30），`structural` 的 AUC
      **0.226244 → 0.661449**（CI [0.4560, 0.8176] 排除 0.5，G1/G2 过，G3 阈值扫描与 G4 预算召回不过）
      → **"训练 GNN 替代 OpenSTA 在本族无可夺取空间"这句话必须加限定**：它成立于"可分辨"与"损害"标签，
      **不成立于"真实增益"标签**。
    - **接受判据的读法要改**：接受集真实增益 **11.36% → 25.00%**、惰性 **84.09% → 70.45%**、
      增益富集 18.6533 → 11.0483（下降是因为拒绝集真实增益率也从 0.61% 升到 2.26%，**不是**接受集变差）、
      损害比 **0.2194 → 0.1419**（**避害更强**）→ **"理想线网说谎 = 避害有效、增益无效"须改为
      "避害更强、增益有限"**；**"惰性 84.09%"这个数字作废**（改为约 70.45%）。
      **但"接受了 N 个候选因此改善了 WNS"仍然不能写**（增益仅占接受集的四分之一，且富集倍数在收窄后下降）。
    - **解除条件**：I1 收齐 → 定稿链重算两族链 → 复核本条引用的全部数字，并用**新的带**重述
      LOG-21 的第 17/19 条。**在定稿前，LOG-21 的第 17/19 条均处于"待重述"状态**。
    - **边界**：G3/G4 在 `gain` 标签上仍不过，**不得据 `gain` 标签的单点 AUC 宣称图特征有信号**；
      预演固定了训练表（只变门槛），最终数字由定稿链给出，唯一未知量是带的最终值。


**补充（LOG-20261024-24）**：判定带落定（`full_family` 口径，布线后 2σ = 0.049752 ns，df 1193、1200 个候选网表、7 电路）后，本条再新增一项未决——**"图特征有没有物理信号"必须分两层回答，而现有文档只写了一层**：

24. **候选级读数与池级读数给出的答案相反，且只有前者对候选生成器有效**：
    - **池内读数（候选生成器唯一能用的读数）**：ITC-99 `resolvable` 标签上，`kind_only`（kind 独热 + iteration 的
      **平凡基线**）池内 AUC **0.555062** [0.5036, 0.6093]，最好的图特征集 `one_n_cells` 0.561297、
      `struct_global_only` 0.555466、`one_depth` 0.548140（CI 含 0.5），`structural` 复合集 0.540114 最低；
      `harm` 标签上 `kind_only` 0.572068 与 `struct_global_only` 0.577145 持平；
      `gain` 标签上 `kind_only` 0.655336 与图特征集 0.651380–0.672469 持平（`structural` 0.613867 最低）。
      **ISCAS89 三标签的池内读数全部 ≈0.5 且 CI 均含 0.5**。
      → **"图结构无候选级物理信号"成立，且可以更强地表述为"没有超过平凡的 kind+iteration 基线"**。
    - **池化读数里出现的信号几乎全部是池间成分**：ITC-99 `gain` 标签上 `structural` 池化 AUC 0.698248，
      而**只知道池均值的预测器就有 0.677415**；`resolvable` 上 `one_depth` 池化 0.591712、仅池均值 0.560235、
      池内 0.548140。
      → **LOG-23 记录的"`gain` 标签上 `structural` 由 0.226244 翻到 0.661449（最终 0.698248）"必须补上这一层：
      那不是候选级区分能力，是电路/池之间的差异**。
    - **幅度效应而非拓扑效应**：`one_depth`、`one_max_fanout` 在 `harm` 标签上同样预测为正
      （池化 0.641897 / 0.628593）——**它们预测 WNS 会动多远，不预测往哪边动**。
    - **预演兑现**：LOG-23 预演的带 0.050419 与真值 0.049752 差约 1.3%，**定性结论全部兑现**；
      对照遍复现定稿链产物 20 项检查、0 处不符、最大偏差 0.0。
    - **解除条件**：**本条不需要解除，但需要改述**——凡写"图结构有/无物理信号"，必须注明是**池内还是池化**、
      与哪个基线比、以及是否为**幅度**（对 `harm` 也预测为正）而非方向。
    - **边界**：探针级、非论文证据；特征子集 post-hoc（≈60 格，未做多重比较校正与嵌套选择）；
      图特征是标量摘要不是 GNN 编码器；池化读数混入很强的电路间成分。


**补充（LOG-20261024-25）**：F2（第三个布线实现）批落地**之前**的一项前置工作——**「三实现比较」这条代码路径此前从未在有第三实现的状态下跑过**（它只打印过 "NOT COMPUTED"），若其中有缺陷，等 2–4 h 批次跑完才发现就太贵：

25. **F2 落地后的解读判据（必须先看这条再解释结果）**：
    - **配对前置条件已实查**：三张作业表 I0/I1/I2 键集完全相同，每键网表路径 / candidate_hash / kind **0 处不符**；
      物理轴 F0(met3/met2/util 10) → F1(met5/met4/util 30) → **F2(met3/met4/util 30)**（与 F0 只差纵向、与 F1 只差横向）；
      数据集行 **1207/1207 全部出现在 F2 作业表** → 探针按 `(circuit, key)` 配三个实现**不会静默落空**。
    - **完整性闸门已验证**：无 F2 文件时探针给出 F0-F1 2σ = 0.049753 ns（= 定稿存储值，1e-6 为工具自述的舍入口径）
      并**拒绝**三实现路径。
    - **可交换性是判据**：夹具给出**完全合成的可交换三实现**三个带 max/min = **1.028 ≈ 1**；
      真实结果若 ≈1 → 三个实现可交换、带是测量系统的良定义属性；**若明显偏离 → F2 的噪声水平与 F0/F1 不同**
      （F2 与 F0 同横向 pin、与 F1 同纵向 pin）→ **实现敏感度由物理轴驱动**，这是物理结论，不是"带挑了哪一对"的随意性。
    - **留一比较的参照**：可交换夹具中**平均标签挑选器胜 38 / 平 85 / 负 21、p=0.0363**（平均两个实现把噪声减半 → 平均应当更好）；
      **若真实结果出现"平均更差"，那是数据结论而不是工具故障**（夹具已证明工具在有优势时会显示优势）。
    - **自我更正留痕**：第一版夹具把合成 F2 建成"真 I1 行 + 噪声"，导致 **F2 与 F1 共享噪声**、三个带必然不等（max/min = 1.70），
      **差点被当成真实预期**；**用两个实现造不出可交换的第三个实现**（三差代数相关），夹具必须三侧全合成。
    - **边界**：夹具级、非论文证据；**合成夹具数字不得当作物理结果引用**；真实结果须等 I2 收齐后由 `finalize_f2_chain.sh` 自动产出。


**补充（LOG-20261024-26）**：一条**运行可靠性**的未决项——**长批次的存活不能交给 WSL**：

26. **WSL 实例重启会全灭脱离会话的 EDA 批**：
    - **现象与归因**：2026-10-24 22:00 前后 WSL 实例被重启（`uptime` 0 min、新 boot 的 dmesg、无 OOM 记录；
      旧 boot 的内核日志随实例消失，**死因无法确证**），F2 批停在 **626/1207**、后处理链同时消失。
    - **已恢复**：`scratch/restart_f2.sh`（可分别拉起批/链）+ `run_labels.sh` 的 rc.tsv 断点续跑 →
      22:12 回到 629/1207；已完成的 626 个结果**不丢**，6 个在飞作业会重跑。
    - **已加固**：**Windows 侧看门狗** `scratch/f2_watchdog.ps1`（120 s 一次，缺哪条链拉哪条，I2 满 1207 自动退出）。
      **关键点：看门狗不能住在 WSL 里**——实例一重启它自己先死。
    - **遗留风险**：本会话若结束而 WSL 再次重启，批会再次中断；**恢复入口固定为
      `bash scratch/restart_f2.sh`（Windows 侧或 WSL 均可）**，状态判据用
      `bash scratch/f2_watchdog_check.sh`（输出 `SUP=/CHAIN=/DONE=/OPENROAD=`）。
    - **纪律修订**：长批次的记录必须把**恢复步骤**（checkpoint 在哪、如何判断已跑过多少、哪些是半成品会被重跑）
      与启动命令**同级**写出；**断点续跑按一等公民设计**，而不是事后补。
    - **边界**：运行事件记录，无新科学结论；F2 的物理结论仍等 I2 收齐后由 `finalize_f2_chain.sh` 产出。


**补充（LOG-20261025-27）**：一条**口径缺陷**——三点曲线的 CUMULATIVE 块把理想线网的**边际量**当成了**累计量**，与 placed / routed 两档混用口径：

27. **ledger 的参照是迭代基线，不是电路基线**：
    - **现象**：`three_point_curve.json` 的 marginal 块与 cumulative 块的 ideal 档 mean 完全相同（-0.046184）——同一个减法被同时标成两种口径；ISCAS89 的累计块给出 rho(理想, 布局后) = -0.1125、斜率 -0.3064（物理阶段与理想阶段**负相关**），物理上不可能。
    - **判决（三层证据）**：① ledger 直读——iteration-1 trials 的 `base_netlist_hash` = 电路基线网表哈希、其参照值即电路基线理想 WNS；iteration>=2 trials 的参照值 = 上一轮被接受候选的 `setup_wns`；② 数据集统计——每电路 `ideal_baseline_wns` 有 2–7 个不同值且随迭代变化，2218 个可比行里 1630 行匹配迭代基线、0 行匹配电路基线；③ 重算一致性——用迭代基线重算 `ideal_delta_wns`，1630 行中 0 行不同。
    - **物理侧未被改动**：`routed_cumulative_wns` 逐位等于 `post_wns(候选) − post_wns(同 batch BASE)`（1207/1207），`routed_delta_wns` 逐位等于 `post_wns(候选) − post_wns(迭代基线)`（1193/1193）→ 只修 ideal 一侧。
    - **已修**：两族 `three_point_curve` 工具改从 ledger 的 iteration-1 参照值取电路基线理想 WNS，口径写进产物新块 `ideal_cumulative_basis`；`build_training_table.py` 的 `ideal_cumulative_wns` 改为真累计；`ideal_baseline_wns` 的 schema 说明改为「迭代基线」；数据集卡补口径提示。
    - **已发布结论不受影响**：marginal 块两族 JSON 全等（逐位未变）；`calibration_three_stage.json` 自带「every number is a MARGINAL quantity」声明；`coverage` / `verdict_counts` / `bands` / `decisions` 逐项未变（对照遍 114/114）。
    - **须改述**：凡引用「理想→物理累计衰减」的旧数字（rho 0.5286 / 0.515、ISCAS89 -0.1125 / -0.1251、斜率 1.1073 / 1.089）**一律作废**；修正后理想线网对**多轮 ECO 净效果**的预测rho = 0.8769（ITC-99）/ 0.9461（ISCAS89）、斜率 1.2057 / 1.3839 > 1 → **「理想线网说谎」必须限定在「单次替换的方向性」上**：边际口径下幅度几乎不衰减（斜率 0.9627 / 0.9572），衰减的是方向确定性（布线后 924/1161），而单次替换的效应远低于判定带 0.049752 ns → **那部分「翻转」里大部分是噪声**。
    - **聚合不可外推**：逐电路方向不一致——b09 理想 +0.028 → 布线后 −0.042211、s832 理想 +0.020417 → 布线后 −0.024167，而 b03、s641 全改善 → 全族聚合被少数电路拉高。
    - **边界**：探针级、非论文证据；理想档的电路基线取自 ledger 的 iteration-1 参照值，与物理档的 OpenROAD 实测基线 WNS 不是同一来源（各自相对自身基线可比，绝对值不可互比）；寄生来自 `estimate_parasitics`、非签核 RC 提取；**F2 尚未纳入本条**。


**补充（LOG-20261025-27 的后续核查）**：修完累计口径后，按同样的怀疑检查了**相邻口径**（布局后档的累计），并查出一件**不是记账错误**的事：
28. **布局后档与布线后档的累计改善在 b01 上差 25 倍，原因是关键路径换了一条**：
    - **先排除记账错误**：用数据集构建器自己的 `parse_log`（import，不重写）从**原始运行日志**重算布局后累计，**逐候选与已发布列一致（1117/1117 全等，0 处不符）**；且每个批次每个电路**恰好一个 BASE 行**、WNS 唯一（IPLACED：b01 −0.66 / b02 −0.26 / b03 −2.12 / b08 −1.34 / b09 −1.34 / b10 −1.54 / b13 −1.57）→ **参照本身没有问题**。
    - **实查到的现象**：布局后累计为正的候选数 —— b01 10/569、b02 13/53、b03 69/69、b08 95/125、b09 34/90、b10 186/214、b13 55/73；而布线后累计为正的是 b01 10/531、b02 14/54、b03 75/75、b08 95/125、b09 35/95、b10 173/200、b13 63/81（已发布口径）→ **b01 在布局后档下只有 10/569 为正，在布线后档下却有 10/531 为正（25 倍差）**，而 b09 方向相反（布局后 34/90 > 布线后 35/95）→ **不是统一的系统偏移**。
    - **判读**：布局后档（placement 寄生模型）与布线后档（global-routing 寄生模型）的**关键路径不是同一条**；同一批网表、同一批候选，两档的"净改善"可以差一个数量级。这直接关系到 **LOG-16/LOG-21 的杠杆结论**（"便宜的布局后档当监督"）——它建立在**跨阶段相关性**（OOF Spearman ≈ 0.63–0.65）上，而**相关性中等不等于逐电路的净改善一致**。
    - **未决**：需要按电路检查"布局后档与布线后档的关键路径是否同一批"，并量化"用布局后标签排序、在布线后验收"的**逐电路**收益/损失；在此之前，"布局后档可以替布线后档"这一说法必须**限定在"跨阶段排序相关性"上**，不能写成"两档的净改善一致"。**注意：这不是对已发布结论的推翻**——LOG-24 的池内/候选级分解结论与本条无关（本条是**跨档**比较）。
    - **边界**：探针级、非论文证据；布局后档与布线后档的寄生估计模型不同，"布线后−布局后"混了阶段变化与模型变化；**F2 尚未纳入**。

**补充（LOG-20261025-28）**：F2（第三个布线实现）批收齐后的两条，**都改写"带是什么"这件事，
但都不推翻已发布结论**：

29. **判定带不是唯一值：三个实现两两之间给出三个不同的带，max/min = 1.476087**：
    - **事实**：同一批 1207 个候选网表上，F0/F1 **0.049753 ns**、F1/F2 **0.045540 ns**、
      F0/F2 **0.033706 ns**；按 LOG-25 **开批前**写死的判据，**C1（可交换）不成立、C2 成立**。
    - **机制**：F0 = (met3 横 / met2 竖 / util 10)、F1 = (met5 / met4 / util 30)、
      F2 = (met3 横 / met4 竖 / util 30)——**两轴都差的一对带最大，只差一轴的对带较小**，
      所以**实现敏感度由物理轴驱动**（不是某个实现坏了）。
    - **对已发布结论的影响：无**。F1/F2 带与 F0/F1 带在 Δ 量化到 0.01 ns 下**完全等价**
      → 所有带门槛量逐项相同；最小的 F0/F2 带把 resolvable 434 → 500、gain 48 → 65、
      harm 386 → 435，但接受集真实增益 0.250000 → 0.272727、惰性 0.681818 → 0.659091、增益富集 7.5593 → 5.6975、
      损害比 0.1944 → 0.1729、`kind_only` 池化 0.538238 → 0.534794、`structural` 池化 0.432507 → 0.426741、
      `structural` 池内 0.540114 → 0.516203 → **"避害更强、增益有限"与"图结构无候选级物理信号"在最宽松的
      带下依然成立**（后者更强）。
    - **须改述**：凡引用"判定带 0.049752 ns"的地方**必须写明用的是 F0/F1 这一对**；带不是测量本身的
      唯一属性，而是**"某一对实现之间的差"**的属性。**族带定义不变**（仍是 F0/F1），另两对是诊断量。
    - **边界**：三个两两差**代数相关**（`d_F0F2 = d_F0F1 + d_F1F2`）→ 三个估计不独立，
      **不能做独立性假设下的同质性检验**，只作一致性检查；Δ 量化 0.01 ns；探针级、非论文证据；
      F2 只在 ITC-99 侧；寄生 `estimate_parasitics`、非签核 RCX。

30. **"用两个实现取均值来降噪"在本族没有支持（C3 不成立）**：
    - **事实**：均值挑选器（两个实现的均值打分）对比单实现挑选器：27 胜 / 92 平 / 25 负，
      精确二项 **p = 0.8899**；逐方向 F0 10/28/10(p=1.0)、F1 7/37/4(p=0.5488)、
      F2 10/27/11(p=1.0)，**没有方向显示优势**。
    - **性质**：按 LOG-25 预注册判据，这是**数据结论而非工具故障**——合成夹具里工具确实报出了优势
      （38/85/21, p=0.0363）。
    - **影响**：第三个实现的价值是**诊断性**的（它揭示了带的任意性），**不是降噪手段**；
      任何"多跑一个实现取平均"的建议在本族**没有数据支持**，不得写成实践建议。
    - **未决**：C3 为何在合成夹具上成立、在真实数据上不成立？候选的物理实现敏感度可能**不是
      独立噪声**（同一候选在两个实现下的偏差可能正相关），此时平均**不降低**方差。
      **下一轮可查**：逐候选算 d_F0F1、d_F1F2、d_F0F2 之间的相关性（注意三者代数相关，
      只能算前两者与第三个的**残差**），并与"独立噪声"零模型对比。**（本条已由 LOG-20261025-31 定论，见文末第 34 条）**

**补充（LOG-20261025-29）**：LOG-24 留下的那个边界——"图特征是**标量摘要**、不是 GNN 编码器，
所以负结论不能替 GNN 背书"——本条正面关掉了：

31. **GNN 编码器级裁决：候选级（池内）没有信号，而且消息传递在候选级有害**：
    - **怎么做的**：环境里**没有 torch / dgl / sklearn / scipy**（只有 numpy / networkx /
      matplotlib），因此**用 numpy 手写了一个 2 层消息传递 GNN**（节点特征 = 单元类型嵌入 +
      改动单元标记 + fanin/fanout/level/cone_down/FF + 图规模），**反传先过数值梯度校验**
      （最大绝对误差 2.784e-11，30 项）→ 评估协议、基线、AUC 与池自助代码**全部取自项目自己的工具**
      （`resolvable_positive_classifier.py`），**没有另写一套**。
    - **判决**：`kind_only` 池内 0.555062；GNN 四档池内分别是——加传播+改动单元读出 0.479242、
      全局读出 0.495365、**不传播**+改动单元读出 0.523367、去单元类型嵌入 0.508663 →
      **没有任何一档超过平凡基线**；**消息传递没有带来任何好处**（点估计 0.479242 < 0.523367，
      差异**未达统计显著**）；**去掉单元类型嵌入后归零**（0.508663 ≈ 随机）→ **GNN 唯一用到的信号
      就是改动单元的类型（≈ kind）**，图的其余部分没有贡献。"不传播"一档池化 0.612254
      （高于 `kind_only` 的 0.538238）但池内更低 → **优势是池间/电路间的，不是候选级的**；
      **所有配对池检验 p > 0.28** → GNN 与平凡基线在候选级**统计上不可区分**。
    - **须改述**：LOG-24 的"图结构无候选级物理信号"**不能再被读成"标量摘要不够好、也许 GNN 行"**
      —— **在事先固定的一套合理超参下，消息传递编码器也没有候选级优势**。
    - **未决（不能越过的边界）**：本实验**超参事先固定、未做嵌套选择、无早停**，样本只有
      **1117 行 / 7 个小电路 / 54 池（39 池有双类）**，且**只在 ITC-99 做**（ISCAS89 的 339 张图
      已就绪但未跑）→ **"更重的调参 / 更大的模型 / 更多数据下 GNN 仍无空间"尚未被证明**，
      只能说"在本设置下没有"。若要把这条升级成"彻底没有可夺取空间"，需要
      ① 嵌套超参选择；② ISCAS89 跨族复现；③ 更大规模族（b17/b18/b19 不在本族内）。
    - **一条方法论教训**：动手前的**单折烟测**给出 0.6531 的测试 AUC（看着像有信号），
      **完整 7 折协议下同一模型只有 0.479242** → **单折烟测只能证明"代码跑通了"，不能当作效果证据**。
    - **边界**：探针级、非论文证据；节点特征不含任何标签派生量；`code/` 未动、HEAD 未变、未提交。

**补充（LOG-20261025-30）**：对第 29 条的**自查式更正**——那条的判决建立在一个被忽略的混淆上；
同时带出一个**新的、可保留的物理发现**：

32. **三个两两带建立在不同的电路支撑上：max/min = 1.476087 这个比较被混淆，C2 必须撤回**：
    - **事实**：F2 批在 **b02 55/55／b08 127/127／b09 92/92／b13 75/75** 上与 F0 **逐候选完全相同**（349 对 / 1200 对），
      在 **b10 216/216** 上与 F1 完全相同（216 对）。`compute_band()` 按电路池化
      `sqrt(Σ(n_c−1)·sd_c² / Σ(n_c−1))`，**sd_c 恒为 0 的电路只进分母不进分子** →
      **零差异电路稀释带**，而三个对的稀释量各不相同（携方差电路：F0/F1 七个、F0/F2 b01／b03／b10、
      F1/F2 b01／b02／b03／b08／b09／b13）。**共同非退化子集只有 b01／b03**。
    - **重算**：共同子集上 F0/F1 0.040078、F1/F2 0.041550、F0/F2 0.035406，**max/min = 1.173530**
      → **落在预注册判据的 INCONCLUSIVE 区 [1.10, 1.35)**（全族口径是 1.476087）。
      留一电路 7 次 1.218976–1.758842；以电路集自助 2000 次，CI95 [1.145302, 3.273719]，
      **只有 0.0051 的重采样落到 1.10 以下**。
    - **须改述（更正第 29 条的判决）**：**C1（可交换）不成立在所有口径下都成立**（三个带确实不相等，
      稳健）；**但 C2（相关夹具量级）不成立**，共同子集与自支撑口径都在 INCONCLUSIVE 区；**撤回的准确含义是「数据不再支持 C2」，不是「证明了 C2 的反面」**（电路集自助 CI95 [1.145302, 3.273719] 跨过 1.35 → C2 既未被证实也未被证伪）；
      第 29 条的机制归因"**实现敏感度由物理轴驱动**（两轴皆差 → 带最大）"**不成立**——
      共同子集上 **F1/F2 0.041550 > F0/F1 0.040078 > F0/F2 0.035406**，只差一轴的 F1/F2 反而最大，
      全族排序是稀释假象。
    - **须改述（对"最大/最保守"这句话）**：**"已发布用的 F0/F1 带是三者中最大"只在全族池化下成立**；
      安全说法是 **F1/F2 与 F0/F1 在 0.01 ns 量化下等价**，两者算出的判决逐项相同。
    - **对已发布结论的影响：无**。**族带定义与数值不变**（F0/F1 = 0.049753，该对**零退化电路**，
      既未被稀释也无支撑冲突）；第 29 条的"带敏感性无结论翻转"是门槛敏感性陈述，不受影响。
    - **边界**：探针级、非论文证据；Δ 量化 0.01 ns；底板冻结 ⇒ util 轴无效；共同子集只有 2 个电路，
      该子集上的比值精度有限；三个两两差代数相关；寄生 `estimate_parasitics`、非签核 RCX。

33. **第三个实现是"部分退化"的：单轴实现变化在 4/7 电路上对布线结果完全没有影响**：
    - **事实**：在 b02/b08/b09/b13 上，**只改竖向 pin 层（met2 → met4）后 `final.odb` 与 F0
      逐字节相同**；在 b10 上只改横向 pin 层（met5 → met3）后与 F1 逐字节相同；
      **b01/b03 两轴都有效**。
    - **已排除"作业没真跑"**：作业表三批物理轴确实不同（util 与 pin 层）；三个批次各有自己的日志
      与 ODB，日志逐字节不同（含计时与内存行）；**日志行级差分显示退化电路上两日志行数完全相同**，
      差异只有 `[INFO PPL-0001] Number of slots` 与计时行，**连 `[InitialPlace]` 的 HPWL 都逐字相同**，
      而对照电路 b01/b03 差异是数百到数千行 → **`place_pins` 确实按不同层执行了
      （slot 数不同），但设计收敛到了同一个结果**。
    - **恒等性指纹成立**：候选级恒等式 `d_F0F2 = d_F0F1 + d_F1F2` 蕴含"某对恒为 0 则另两对的
      电路内 SD 必相等"；实测 **5 个退化电路上全部精确相等（差 0.0）** →
      **退化是真实性质，不是记账假象**。
    - **意义**：**族带 0.049753 测的是"两轴都变"的一对 → 它是单轴实现敏感度的上界，不是无偏估计**；
      "实现敏感度"也**不是处处存在的噪声，而是某些轴/某些电路上恒为 0 的量**
      （逐电路 F0/F1 带 0.028922（b02）… 0.102154（b09），跨 3.53 倍）。
    - **未决**：**为什么某些设计的某一轴完全无效**（候选：这些设计的单元在该方向上无可用 pin 位、
      或该轴的变化被 placer/router 吸收）→ 需要读 OpenROAD 的 `place_pins` 行为与这些设计的
      pin 分布才能定论；**在定论前不得把"单轴无效"写成普遍规律**。
    - **边界**：探针级、非论文证据；只在本族 7 个电路上观察；`code/` 未动、HEAD 未变、未提交。

**补充（LOG-20261025-31）**：第 30 条的"未决"（C3 为何在合成夹具上成立、在真实数据上不成立）
**在本条定论**：

34. **C3 的机制定论："取均值降噪"的收益符号由实现等价结构决定，不是"有/没有"**：
    - **可证伪的预测**：LOG-30 查明 F0 ≡ F2（b02/b08/b09/b13）、F1 ≡ F2（b10）
      → 留一比较里，**被留出的实现若与单实现 picker 所用的实现逐候选相等，该 picker
      已经精确命中真相（遗憾恒 0），平均只能打平或更差**；若它与被平均的另一个相等，
      平均是朝真相的收缩。实测 **两类各 10 格、违例 0 个**。
    - **配对分析**（预注册的符号检验功效不足）：全族配对改进 0.001458 ns
      （0.145800 量子），Wilcoxon p = 0.213500、自助 CI95 [-0.000903, 0.004028]；
      **但两组被强制符号的格子各自显著**：真值 = 单实现 picker 的实现 → 平均
      **-0.006250 ns（-0.625000 量子）、0 胜 48 平 16 负、Wilcoxon p = 0.000400（显著有害）**；
      真值 = 被平均的另一个 → **0.009375 ns（0.937500 量子）、16 胜 48 平 0 负、
      Wilcoxon p = 0.000400（显著有益）**。**全族平局是两个方向相反的显著效应相消。**
    - **在三个实现真正互异的电路（b01／b03）上**：配对改进 0.002292 ns（0.229200 量子），
      Wilcoxon p = 0.305200，自助 CI95 上界 0.006875 ns ≈ 0.687500 量子
      → **低于测量分辨率（0.01 ns），不可利用**。
    - **OI 第 30 条的未决（一度自由度 vs 候选特异多维）**：**这个二分法用三个带是分不开的**——
      恒等式 `imp02 = imp01 + imp12` 把 `r(imp01,imp12)` 钉死
      （实测与恒等式完全一致，差 0.0），**该相关系数不携带独立信息**；
      有信息量的只有方差比 `var(imp02)/(var(imp01)+var(imp12))` = 0.349058
      （干净子集）→ **两个假设都被否证**，本族是**两轴扰动正耦合、部分抵消**的结构。
    - **须改述**：LOG-28 的"C3 不成立"**作为显著性判决成立**，但理由要改：
      不是"平均没用"，而是"**平均在本族有时显著有害**"。**"多跑一个实现取平均"
      不得作为实践建议**；若要写，必须先查参与平均的成员之间是否**结构性等价**。
    - **边界**：探针级、非论文证据；干净子集只有 2 个电路（可证伪、不能确立）；
      Wilcoxon 为带并列修正的正态近似；Δ 量化 0.01 ns；寄生非签核 RCX。

**补充（LOG-20261025-32）**：把两个物理轴拆开测，并得到一条关于"判定带"本身的方法学结论：

35. **单轴敏感度低于双轴族带；且判决只依赖带落在 0.01 ns 量子网格的哪一格**：
    - **单轴带**：竖轴（F0↔F2，b01/b03/b10）**0.039884 ns**（855/852）；
      横轴（F1↔F2，6 电路）**0.050272 ns**（985/979）；
      全族双轴带 **0.049753 ns**。**同口径**（共同子集 b01／b03）上：
      双轴 **0.040078**、横轴 **0.041550**、竖轴 **0.035406**
      → **"同时改两个轴"并不比"只改主导那个轴"更具破坏性** → 族带是上界，
      **但不是两个单轴带的平方和**（两轴扰动正耦合、一起施加时部分抵消）。
    - **判决重算**：六个带变体只落进**三个标签集合**（布线后 WNS 量化到 0.01 ns →
      标签集合只由 `floor(band/0.01)+1` 决定）；**结构检查通过**：同一格内的变体，
      标签数、分类器 AUC、接受判据数字**逐位相同**（0 处违例）。
    - **已发布结论无一翻转**：`structural` 池化 0.445175／0.432507／0.426741 全部远低于 0.5，
      且**在池化与池内两种读法下都低于同格的 `kind_only`**（池化 0.548661／0.538238／0.534794、
      池内 0.548825／0.555062／0.538223）→ **"图结构无候选级物理信号"三格下都成立**；
      接受集增益率 0.272727／0.250000／0.250000、惰性 0.659091／0.681818／0.704545、损害比 0.172900／0.194400／0.141900
      → **"避害更强、增益有限"三格下形状不变**。
    - **口径澄清**：证据包 `flip_table_vs_published[].flips` 标的是"**这个数字动了**"
      （逐行极性不同：接受判据四行朝更有利方向），
      **`flips=true` ≠ "判决被推翻"**；
      本条的"结论无一翻转"指**判决方向没有反过来**。
    - **方法学结论**：项目至今用过的带的量子格 = pilot 0.087496 → idx 9、
      预览 0.050419 → idx 6、**定稿 0.049752 → idx 5**、F1/F2 0.045540 → **idx 5**、
      F0/F2 0.033706 → idx 4。**LOG-28"F1/F2 与 F0/F1 完全等价"的真实原因是同一格**，
      不是"带差 0.004 < 0.01"；pilot→定稿的"窄约 42%"其实是 **idx 9 → idx 5 的 4 格移动**。
      → **报告判定带必须同时报它落在量子网格的哪一格**；"带敏感性"分析测的是
      **阈值跨过了哪条量子边界**，不是带的连续值。
    - **边界**：探针级、非论文证据；单轴带只能在"该轴有效"的电路上测量，
      与双轴带**不在同一批电路上**（同口径只有 b01／b03 2 个电路）；Δ 量化 0.01 ns；
      寄生非签核 RCX；`code/` 未动、HEAD 未变、未提交。

**补充（LOG-20261025-33）**：GNN 裁决的加强轮新增三条未决。

36. **"图结构无候选级物理信号"必须按读出与族收窄，不能再作为族无关结论**：
    LOG-20261025-29 的判决在第二个族（ISCAS89）复现时，**首次出现池内 AUC 明显高于
    平凡基线的变体**：`gnn_global`（readout='global'）池内高于 `kind_only`，
    逐池配对 p < 0.05；而 oracle 上限对照同时表明**候选级的物理信号很大**
    （理想 / 布局后 Δ 当预测器，池内 AUC 0.85–0.93，两族一致）。
    → 结论必须改写为：**"拓扑（标量摘要与 GNN 编码器）读不出候选级物理信号，
    而网表派生的『测量』可以"**。
    **待办**：(a) 论文里所有"图结构无候选级物理信号"式的表述按此收窄，
    逐处回读原文后再改，**不得凭记忆改**；(b) `gnn_global` 的抬升是否**族特异**
    由 ITC-99 对照遍裁决（见第 38 条）；(c) 若要更强的单轴结论，仍需**只差单轴的
    第四个布线实现**（开批前必须先做沙箱预演与判据写死）。

37. **预注册文本与其网格不一致，必须作为缺陷登记（不得事后静默修补）**：
    `scratch/round32_preregistration.json` 的 `scope_limit` 写的是"嵌套选择覆盖
    readout、传播、类型嵌入与权重衰减**四个维度**"，但它列出的**四个配置全部把
    readout 固定为 'mod'** → 网格**没有**覆盖 readout 维度。
    本轮的处理：严格按预注册网格给出 `pre` 判决（**未改动**），
    另加一个**对抗臂**（把 `global` 追加到网格末尾）给出 `extended` 判决，
    并写明该臂的偏差方向是**只能让负面结论更难成立**，因此是保守测试。
    **待办**：下一轮写预注册时，scope 句必须由网格**逐项生成**，不得手写；
    并把"网格覆盖的维度"做成**可执行断言**（网格里实际出现的取值集合 == scope 句声明的维度）。

38. **组件 F 的嵌套批已补完（分块跑批）**：
    **(a) harness 的后台任务有 1 小时硬上限**（`Background bash timed out after
    3600000ms`），到点会把 python 子进程一起杀掉 → 第一遍 ITC-99 对照遍就是**这样被
    掐死在 C2 那一档**的（已重跑，逐位复现 LOG-29）；ISCAS89 嵌套批（5 配置 × 8 外层折
    + 5 配置空标签对照，每折 5×7 次内层 LOCO 训练 × 120 epoch）需要约 3.5 小时，
    **单次后台任务跑不完**。
    **(b) 算力预算驱动的范围收缩**：机器 8 物理核 / 16 逻辑核，五路并行时每路只拿到
    约 1.0–1.5 核（numpy/OpenBLAS 多线程）；**ITC-99 同规格嵌套批约需 9 小时** →
    本轮**主动停掉**，把 CPU 让给匹配对照机制诊断与 ITC-99 对照遍。
    **本轮已做的工程修复**（供下一轮直接用）：嵌套工具加了 **① flush 打印**
    （原先 stdout 重定向到文件时是块缓冲，日志几十分钟不更新，"看日志确认在推进"
    这条纪律会静默失效）、**② 逐外层折检查点 + `--resume` / `--max-folds`**
    （分块跑，结果与一次跑完相同：各折独立、种子固定）、**③ 设置指纹**
    （检查点记录网格/读出/传播/类型/wd/epoch/族/标签模式，**异设置续跑直接拒绝**，
    防止 1-epoch 沙箱折被静默混进 120-epoch 产物）。
    **误判留档**：第一遍嵌套沙箱"崩溃"（exit -1）**不是工具崩**，是 PowerShell 管道
    `Select-Object -First N` 提前关闭上游把进程打死的——**长批的输出不得接 `-First`**。
    **结果**：ISCAS89 的嵌套批已用分块跑批补完（每块 ≤ 50 分钟，`--max-folds 2`，逐外层折检查点 + `--resume` + 设置指纹），正式读数见 LOG-33 第 ⑥ 节；**ITC-99 的嵌套批仍因算力预算未跑**（同规格约 9 小时）→ 本条的"两族"由**两族复现遍**提供，**嵌套选择只在 ISCAS89 上完成**。

39. **口径纠错的可复用规则（本轮最可移植的一条）**：预注册判据里的"**同一协议下的**
    对照"，协议**包含架构**。本轮工具里的 C2 空标签与 C4 随机初始化探针固定跑
    `readout='mod'`，而被检验的变体 `gnn_global` 用 `readout='global'` →
    那两个对照其实是 `gnn_mod` 的对照；实测 mod 对照池内高于匹配对照
    （见 LOG-33 第 ④ 节），**用错口径的对照会把门槛量在别的东西上**。
    **待办**：任何"对照读数 < 阈值"型判据，落地前先确认对照与被检验对象**同架构**，
    并把这一点写进证据包的对照表（**逐条标 readout**）。

**本轮未关闭的既有未决**：D 正式矩阵（28/56 accepted、raw 3/8、OI-051）、
四 partial、四态能力、b18 inout 域、显式 bytes 注入、OI-049、S/SPEF 科学效果
**全部保持 pending**，本轮未扰动；`code/` 未动、HEAD 未变、未提交、论文未改。

**补充（LOG-20261025-34）**：接受判据搬到布局后档这一轮新增三条未决。

40. **"候选级代理更好"与"决策级策略更好"是两件事，必须分开记账（本轮最可迁移的一条）**：
    LOG-20261024-21/24 已证明布局后 Δ 是布线后标签的**强候选级**预测器
    （当前产物：布局后档单独预测布线后标签的候选级 AUC **0.896779**，理想档单独 0.859390），LOG-20261025-33 又证明候选级物理信号很大
    （oracle 池内 AUC 0.85–0.93）。本轮把这些结论**推到决策级**检验之后，
    结果是：**候选级的好读数没有变成决策级的收益**——
    布局后判据在 ITC-99 上确实是**显著更好的池内排序器**
    （Spearman 与布线后 Δ 0.644043 vs 理想 0.399218，配对 9/1，
    p = 0.021484），但逐决策配对符号检验只有 8/5/14、p = 0.581055、
    挽回比例 0.073171。
    → **论文与后续实验里凡是引用候选级指标的地方，都必须写清它是候选级读数**，
    不得让读者以为它已经等价于策略收益。
    **待办**：(a) 论文中"布局后档可以替代理想线网作接受判据"式的表述，
    按本轮读数**收窄**为"布局后档是显著更好的**池内排序器**，但本轮未观察到"
    "决策级收益"；(b) 后续任何"换判据/换代理"的方案，必须**先跑决策级反事实**
    （逐决策配对 + 挽回比例 + 与 oracle 的重合率），再谈候选级指标。

41. **决策级奖池太小，任何判据改进都显不出形——这是本轮真正的限制**：
    布线后 oracle（同一合格集合内的布线后 Δ 最大者）**显著优于**理想判据
    （ISCAS89 7/0，p = 0.015625；ITC-99 20/0，p = 1.907349e-06），
    说明**决策级确实有可重新分配的物理收益**；但这个奖池每决策只有
    0.012857 ns（ISCAS89）/ 0.015185 ns（ITC-99），约 n/a / n/a 个 0.01 ns 量子，
    而可评估决策数只有 14 / 27 个（ledger 轮次中多数因**无标注池**或
    **不足 2 个合格候选**而不可评估）。
    → **换判据之前，先把决策级奖池做大**：把"三档标签齐备"的覆盖度提上去
    （当前 ITC-99 的 1207 个候选里只有 1117 个三档齐备、ledger 143 轮里只有
    27 轮可评估）。
    **待办**：下一轮优先做**标注覆盖度**（哪些 ledger 轮次缺标注池、缺在哪一档）
    的诊断与补齐，而不是再换一个判据档位。

42. **接受判据的符号口径必须由独立的物理事实核验，不能凭直觉写进预注册**：
    本轮预注册原文把符号写反了（写成 `gain = −Δ`、取 Δ 最小者）。发现路径是
    **把 ledger 的逐 trial 记录与训练表逐行对齐**，发现"循环接受的候选不是池内
    Δ 最小者，而是 Δ 最大的那个"，追查 ledger 才发现硬门 `acceptance_budget_violation`
    恰好拒掉 Δ < 0 的 trial。独立核验：ledger 的 `improved` 标志与非零 Δ 的符号
    **ISCAS89 27/27、ITC-99 74/74 一致**。
    → **纪律**：凡是把"越大越好"还是"越小越好"写进判据的场合，
    必须找一个**与该判据无关的物理事实**（如 ledger 自己的 `improved` 标志）
    来核验符号；写反了会把整个判决翻面，而且**不会有任何报错**。
    本轮的处理：原预注册**保持原样不改**（保留"跑之前写了什么"的原始凭证），
    更正另立有证据的附记，**阈值与判据一律不动**。

**本轮未关闭的既有未决**：D 正式矩阵（28/56 accepted、raw 3/8、OI-051）、
四 partial、四态能力、b18 inout 域、显式 bytes 注入、OI-049、S/SPEF 科学效果
**全部保持 pending**，本轮未扰动；`code/` 未动、HEAD 未变、未提交、论文未改。

## **补充（LOG-20261025-35）**

| 编号 | 标题 | 首次出现 | 状态 | 说明 | 证据 | 影响 |
|---|---|---|---|---|---|---|
| OI-053 | **理想档"未测量"与"等于零"必须分开，标签缺失也要可见** | 2026-10-25（LOG-20261025-35） | **open：修复已落地，下游已重跑** | 构建器只从 `acceptance_evidence` 取理想档读数，而从未产生接受决策的 trial 不带该字段 → 理想档被静默留空（ITC-99 310 / ISCAS89 25 个 trial）；三点曲线再按"理想档为空"丢弃它们，连同其真实的 placed/routed 测量一起丢掉。**第一版补丁（回退到 `trial.wns`）已回滚**：该值在 310/310 上恰好等于迭代基线、0/310 有 STA provenance（对照 3734/3734）、失败于 STA 之前的 F1/F2 硬门 → 是占位符而非测量 | 证据包 `r30_dataset_label_status_20261025/`（check_placeholder_provenance / check_affected_detail / check_filled_vs_conflict / drop 普查） | 理想档"未测量"与"为零"从此可由 `ideal_label_status` 区分；构建器与曲线工具已修，产物已重建且 0 冲突；**下游产物按带换值纪律已逐一报出（ISCAS89 0/23 变动，ITC-99 8 个变动，形态为样本 +76、比值微移）**；D 正式矩阵与 pending 门未触动 |
| OI-054 | **`band_scope.json` 的 `stored_ratio_in_three_point_curve` 是跨口径陈旧值** | 2026-10-25（LOG-20261025-35） | **open：已定位，本轮只报告不改历史** | 该字段读三点曲线产物的两个带之比，但长期保留的是**换带前**的值：可由 0.087496（pilot 口径布线后带，LOG-20）/ 0.029826（全样本布局后带，LOG-22）= 2.933548 精确复现，即**跨口径**比值；同工具自测的同口径 `ratio_routed_over_placed` 两侧都是 1.668108。与本轮补丁无关（曲线两个带在补丁前后逐位相同） | 证据包 `r30_dataset_label_status_20261025/`（check_band_ratio） | 本轮重跑后该字段已自动刷新为 1.668075（与同口径自测值一致）；**LOG-22 记录的 2.933548 是当时同一写法的跨口径值，本身没有错，但"带宽比"这个量必须写明口径**；建议后续在 `band_scope.json` 内把"口径"字段与比值一起写出，避免再出现同名字段不同口径 |
| OI-055 |**`LOGS.md` 的行号不是唯一键：2026-07-31 的三组记录共用了同一个编号**|2026-10-25（LOG-20261025-40）|**open：已定位，不倒改历史**|同一天的两批记录复用了同一编号：`LOG-20260731-20/21/22` 各出现两次（物理行 171/172/173 与 180/181/182），**内容不同**。按编号索引 LOG 行会**只读到其中一条**、静默丢掉另一条——本轮两个工具（块级比较与字典索引）因此对同一对文件给出了**矛盾结论**。|`scratch/count_log_row_keys.py`（可随时复现：LOGS.md 927 行 / 924 个不同编号 / 3 个编号重复）|**不改编号**：2026-07-31 写进日志的编号是那份日志的一部分，重编即改历史。**处置要求**：读 LOG 行的工具必须按（编号, 位置）或行区间索引，不能只按编号；本轮 `scratch/diff_log_blocks.py` 与 `scratch/show_block_diff.py` 的矛盾就是这么来的。|
| OI-056 | **常驻同步门的 `PAIRS` 只覆盖 5 个文件，LOG 行被原地重写对它不可见** | 2026-10-25（LOG-20261025-41） | **open：未关闭，待项目负责人决定** | `scratch/verify_round34_sync.py` 的 `PAIRS` 只 diff 五个文件：`.codex-handoff.json`、`README.md`、`project_docs/README.md`、`project_docs/OPEN_ISSUES.md`、`AGENTS.md`。**`project_docs/LOGS.md`、`docs/EXPERIENCE.md`、`project_docs/evidence/EXPERIMENT_REGISTRY.md` 都不在其中**，所以"LOG 行被原地重写"（例如第 32 轮折回重写 LOG-20261025-33 行）这道常驻门根本看不见。**这是范围限制，不是白名单遗漏**——白名单只治理这道门实际看见的行。扩大 `PAIRS` 属**设计改动**：三个记录文件的历史改动量大（LOGS.md 927 行、EXPERIENCE.md 1673 行、REGISTRY 1940 行），直接纳入会大面积误红，必须配套白名单机制（逐块登记 + 负控）才能安全扩大。**本轮不改该脚本**：`code/` 只读、HEAD 锁在 `f761ee1996a83fc4f0f3de0999b74d85a8237858`。 | `scratch/verify_round34_sync.py` 的 `PAIRS` 定义（第 34–40 行）；`scratch/parse_audit_20261025.md` 第 #15 条与第 3 节第 7 点 | **未关闭**；待**项目负责人（根会话）**决定是否扩大 `PAIRS` 及其白名单方案。**影响哪些门**：`scratch/verify_round34_sync.py`（常驻同步门）对 `project_docs/LOGS.md`、`docs/EXPERIENCE.md`、`project_docs/evidence/EXPERIMENT_REGISTRY.md` 的**内容改动完全不可见**；该门的**行尾检查仍覆盖**这四个文件（LOGS/EXPERIENCE/REGISTRY 要全 CRLF、OI 要全 LF），但那是**格式门、不是内容门**。本轮落地 LOG-20261025-41 时对这三个文件的追加，只能靠"改后与改前逐字节比对"自证，不能靠这道门。 |
| OI-057 | **b05 在 lite TCL 下"没撞上限"不等于"没有上限"；full TCL 口径的工期/磁盘旧数已作废** | 2026-10-25（LOG-20261025-42） | **open：待批跑完后重算** | b05 的四次死亡（rc=124 / 1751–1757 s / 110–128 MB）已定案为 `report_checks` 打印 100000 条路径报告所致的**报告阶段**问题（该日志 `Startpoint` 恰好 100000 次、`worst slack` 恰好 2 次），lite TCL 下同参数 10/10 rc=0（92–186 s、均值 128.9 s、日志约 1.65 MB）。但**"没观测到上限命中"不等于"证明没有别的上限"**：lite 下是否还存在内部路径数上限或其它限制**未单独证伪**。同时 full TCL 口径的旧数（墙钟上界 298.02 h、磁盘 101.5 GB、每作业 31.4 MB、b04 候选均值 663.7 s）**已作废**，须按 lite 实测重算 | `scratch/ext_b05_lite_preflight/preflight_b05_lite.json`、`scratch/ext_b05_lite_preflight/`、`experiments/20260821_real_pr_crossbench/runs/b05_baseline/pr_run.log`（`Startpoint` 计数 100000）、`scratch/prove_lite_tcl_codelines.py`、`scratch/ext_par_decision.json`、`scratch/ext_wallclock_lite.py` | **未关闭**；工期/磁盘重算须等试点段 58 个作业跑完后按**分电路实测**给出（工具 `scratch/ext_wallclock_lite.py` 已就位），不跨电路混算；b05 的"是否还有别的上限"在 lite 下继续观测，**不得**写成"已证明没有上限" **补充（LOG-20261027-82）— 工期/磁盘已按分电路实测重算**（试点段 58 个作业已跑完，本条的重算条件因此满足）：主池 1393 键的**布线后 + 布局后墙钟合计 57.53 h**（试点实测 5.76 h），**日志 8.02 GB**；逐电路（布线后 h / 布局后 h / 日志字节）：**b04 24.61 / 6.15 / 7.75 GB**、b05 1.30 / 0.32 / 119 MB、b06 1.96 / 0.49 / 96 MB、b07 7.99 / 2.00 / 421 MB、b11 1.99 / 0.50 / 129 MB、b12 8.18 / 2.05 / 94 MB；**没有试点测量的电路 0 个**（不跨族、不跨口径外推）。**旧的 full TCL 数（墙钟上界 298.02 h、磁盘 101.5 GB、每作业 31.4 MB、b04 候选均值 663.7 s）就此作废**（证据 `scratch/r88_paper_audit/wallclock_lite_recompute.json`，工具 `scratch/ext_wallclock_lite.py`）。**b05 在 lite 下仍未观测到任何上限命中**：战役里 b05 的 **167 个作业全部 rc=0**（主池 70 / 布局后 70 / 对照池 27），**无一超时**——但这仍然只是**观测**，**不是「证明没有别的上限」**，按本条纪律**不得**写成「已证明没有上限」。**建议按此关闭**（重算条件已满足；「上限」那句作为观测事实保留）。 |
| OI-058 | **扩面族缺族内判定带：D1 关掉对照池时把族内复现性底噪的唯一产地一并关掉了，而「35.9 h」这个省时理由本身是一个已被作废的数** | 2026-10-25（LOG-20261025-45） | **已定案（2026-10-25/LOG-20261025-49）：② 开全对照池 389 键（+17.53 h）**；**执行中**，族内带数字尚未产生 | 扩面族只有一个布线实现 F0，候选级「是否真的不同」（判定带）需要同网表同实现重跑来定。基族有该测量（`scratch/par_label_identity.json`：116/116 逐位相同 → 底噪 0.0 ns），但那是**跨族继承**；扩面族**族内**的唯一来源是对照池（389 键 = 主池同名键、17 字段 0 差异、realisation 全 F0）。D1 以「纯复现、不携带新物理信息」为由关掉它，代价是**族内底噪无产地**。而 D1 给出的省时理由「71.7 h @PAR=1 / 35.9 h @PAR=2 / 17.9 h @PAR=4」**其算法是把 b04 一家的 663.7 s 套到所有键上**（LOG-20261025-45 第五节已定案作废）；按试点实测分电路口径，**全跑 389 键只要 17.53 h**（不含 b12 的 21 键）。分层抽样 **28 键 / 5 电路 = 1.33 h**（全跑的 1/13） | `scratch/ext_band_source_options.py`、`scratch/ext_band_source_options.json`、`scratch/probe_budget_method.py`、`scratch/ext_budget_v2.json`（`measured_seconds_per_job_pilot = 663.7`）、`scratch/par_label_identity.json` | **未关闭（方案已定案，执行中）**；原三个待选项（**以下推荐已于 2026-10-25 被拍板取代，见本单元格末尾**）：① **开分层抽样**（+1.33 h，补上族内底噪的最小充分证据，**推荐**）；② 开全对照池（+17.53 h，389 对全量复现）；③ 跨族继承基族的 0.0 ns 并**显式标注是跨族**（0 h，但扩面族 H1 的带必须写明口径）。**推荐 ①** 的理由：同实现重跑的偏移是**确定性**的（基族 0/58 与 0/8 非零差），样本量不是约束、**电路覆盖**才是，28 键已足够确认族内底噪。**选 ③ 的代价**：H1 的族内带将没有直接证据，只能跨族继承。**连带**：`scratch/post_ext_chain.sh` 的默认 `--guard-batches default` 会要求对照池 389 键的回执，若选 ③（或任何不跑对照池的方案）**必须显式传 `--guard-batches v3`**，否则链会卡死在第 1 步。**【2026-10-25/LOG-20261025-49 已拍板】** 项目负责人选 **② 开全对照池 389 键**（+17.53 h），**不做分层抽样、不走跨族继承**；实现路径 = 批脚本**已内置**的 `--with-control-replicate`（段 8 → `runs/round35_ext_t1`，389 作业），看门狗**已内置** `EXT_WD_WITH_CONTROL_REPLICATE=1` 的认识。已就位两个常驻触发器：**段 8 自动交接**（`scratch/ext_control_pool_trigger.sh`，PID 126442，armed；等三段收齐 → 等批退出 → **按精确 PID 停旧看门狗** → 等机器空闲 → 带开关重启批 → 段 1-7 由每键一目录 resume 跳过、只跑段 8 → 起认识 389 键的新看门狗）与**族内带自动测量**（`scratch/ext_infamily_band_trigger.sh`，PID 127792，armed；等 389 回执 → 跑 H4 复现门 `--expect-pairs 389` → 跑族内带工具 → 产物落 `scratch/infamily_band/`）。**族内带判据在数据产出前写死**：期望 389 对硬钉、0 对可比即失败、**主判据 = 389 对全部逐位相同 → 族内底噪 0.000000 ns**；任一对不同 → **不出带**、逐对点名并要求重算下游判决（工具 `scratch/ext_infamily_band.py` + 套件 6 场景 **20/20 全绿**）。**连带更正**：上面那句"默认跑法必然卡死在第 1 步"**在选 ② 之后不再成立**——`scratch/post_ext_guard.py` 的 `DEFAULT_BATCHES` 要求的 `round35_ext_t1` 389 回执**将被跑出来**，故第 1 步不再因"对照池缺回执"而阻塞（该门**仍**要求主池与布局后两段齐全）。**族内带数字尚未产生**（对照池段未跑）→ 本条**继续 open**，待族内带出数后关闭 |

**补充（LOG-20261025-37）**：**D 正式矩阵的"完成性审查"与"raw 归档"已收齐**：根审计 56/56（68.1 s）、独立原件审查全量 56 键（613.6 s，`full_56_registered_keys_reviewed = True`，extra 列表为空）、根接受收据已签（`full56_accepted = true`，计数与根审计独立重算逐项对上）、八个电路的 raw 包全部归档并逐 SHA 后验验收（8/8）。
  * **被关掉的是"完成性"这一层**：56 个注册完成件都被独立重读过，每条 SEC 主张有证据，注册的 45 份执行源未漂移，八个电路的原件可自证恢复。
  * **没有被关掉的**：签核 RC 物理闭环、四态能力、四 partial、**OI-051**（SPEF helper → 叶实例端点覆盖，**与完成性审查不是同一件事**）、显式 bytes 注入。
  * **出处差异**：前三个 case（s27/s382/s420）用另一台机器的 scoop 7z shim（7-Zip 26.00），**本轮五个 case**（s641/s713/s820/s832/s953）用 `C:\Program Files\7-Zip`（26.05），压缩器版本不同已写进收据；**归档脚本也分两代**（s27/s382 用初版，其余六个用其改编版，`adapted_from` 链完整）；根后验比对的是**解出来的字节**。
  * `code/` 未动、HEAD 未变、未提交；论文未动。

**补充（LOG-20261025-38）**：**扩面池定义已写死，可达性判定已重分类**（详见 LOG-20261025-38）：
  * **b05 由"不可达"改判为真可达**——档案的同脚本同网表串行跑 838 s 完成（rc=0、有 final.odb）；探针的 rc=124 是 **PAR=2 并发 + 1800 s 上限**造成的伪影，且超时点在 **STA 路径报告阶段**（布线 1 分钟就完成了）。
  * **b14 改判为"未证实"**（归档日志有 38493 条路径报告 ⇒ 布线已完成，但 3600 s 仍砍在报告阶段），**需单独串行重测才能定论**。
  * b15/b17/b20/b21/b22 维持**真物理上限**（死在详细布线，无任何路径报告）。
  * **扩面主池 = 全量 distinct 候选**（1393 作业/档，与既有 7 电路同口径）；**对照池 = 合格候选池**（389 作业/档，省 3.58 倍，仅作敏感性对照）。
  * **扩面批已挂**，等第 32 轮嵌套批结束后自动开跑；**结果尚未产生**，本条不含任何扩面后的读数。
  * 历史记录与 `probe_result.json` **未改动**；`code/` 未动、HEAD 未变、未提交；论文未动。

**补充（LOG-20261025-39）**：**扩面批已从 v1 修订到 v2，开跑前拦下三处缺陷**（详见 LOG-20261025-39）：
  * **加了试点门**：先跑 58 作业试点（覆盖全部 6 个电路，b05 10 个），通过再进 1393 作业全量批。
  * **加了修复段**：每段之后把 rc≠0 的作业用 **PAR=1 + 3600 s** 重跑，**串行仍超时才算真物理上限**；原始 rc.tsv **改名保留为 rc.tsv.orig**，证据不丢。
  * **布局后档时限改回 3600**：标签族自己的 IPLACED/IPLACEDF1 批用的就是这个值，v1 写 1800 会产出**与已发布布局后档不可比**的截断结果。
  * **核实扩面不重复劳动**：扩面 1393 作业与既有 1207 作业**键交集 0**，因为电路不同（既有 b01、b02、b03、b08、b09、b10、b13 vs 扩面 b04、b05、b06、b07、b11、b12）；跑完即覆盖 ITC-99 全部 7+6 个可评估电路。
  * 挂批前自检 17 项全过、失败 0 项；v2 launcher 已挂，**批仍未开跑，扩面结果尚未产生**。

**补充（LOG-20261025-40）**：**四个记录文件的行尾已修回 house rule**（详见 LOG-20261025-40）：
  * **查出并定位了历史缺陷**：LOG-20261025-37 的落地用 `Path.write_text()` 写 OPEN_ISSUES.md 而未传 `newline=`，在 Windows 上把**整篇 LF 文件改写成了 CRLF**（备份链证据：LOG-37 落地前仍是 LF，落地后已是 CRLF）；LOG-38/39 沿用了同一写法。**当时 25 项核验没抓到，是因为内容核验对行尾是盲的。**
  * **修复**：`OPEN_ISSUES.md` 的 898 处 CRLF 转回 LF；LOGS.md / EXPERIENCE.md / EXPERIMENT_REGISTRY.md 的 107 处孤立 LF 转成 CRLF。
  * **内容零改动**：修复前后各自规范化成 LF 后**逐字节相同**，不符 0 处。
  * **脚本修正**：`append_log_37/38/39.py` 的 OI 写法统一改成写 LF；**同步门新增行尾检查**，四个文件必须各自符合 house rule。
  * `code/` 未动、HEAD 未变、未提交；论文未动；扩面结果尚未产生。
**补充（LOG-20261025-41）**：**扩面批 v3 的三条设计依据已用实测锁定，并记下一处常驻门的范围限制**（详见 LOG-20261025-41）：
  * **并发只改墙钟、不改标签**：同网表、同 TCL、同实现的两对批对照（I0↔I0P0、I1↔I1P0，每对 58 键）的标签 **116/116 逐位相同、0 条不同**，而墙钟比 0.781–2.636 → 并行度是**机器时间旋钮**，不是标签口径旋钮。
  * **对照池是纯复现**：389 键与主池同名键 17 字段 0 条差异、realisation 全为 F0 → 对照池唯一作用是可复现性对照（试点段已免费提供 58 对）。
  * **成本口径以实测替换原估**：档案 `pr_auto.tcl` 秒数与族内 `pr_label.tcl` 秒数之比在 0.464–5.508 之间乱跳、不可外推；试点 10 个 rc=0 作业均值 663.7 s/作业，预算重算为 298.02 h（≈12.42 天）**上界**，须待试点段 58 个作业跑完后重算。
  * **试点段的真实 rc 分布**：完成 12、rc=0 10、rc=124 2（b05 的 2 个作业被 1800 s 上限杀掉）；b04 的 10 个标签 `worst_slack` 落在 -2.80 ~ -2.75、`base__b04` 与 `final__b04` 标签不相同 → 提取链在真实数据上跑通。**b05 当前只是"在 PAR=2 / 1800 s 下被上限杀掉，待 repair 段以 PAR=1 / 3600 s 重测定夺"，既不是"不可达"也不是"真物理上限"。
  * **慢组设计**：慢电路从一开始就按 PAR=1 跑，慢组布线后上限 3600 s，快组维持 PAR=2 / 1800 s（出处 `scratch/round37_ext_batch_v3_decision.md`；慢组 3600 s 是本轮主线的最新指令，与该文件 D4 条文不同，待其后续追加）。
  * `code/` 未动、HEAD 未变、未提交；论文未动；扩面结果尚未产生。

**补充（LOG-20261025-42）**：**扩面批已换批 v3 并开跑；b05 之死定案；full TCL 口径旧数作废**（详见 LOG-20261025-42）：
  * **批已开跑**：批 PID 478 / 看门狗 PID 696 / 切换时刻 2026-10-25 13:44:18；段 0 标签等价闸门**双被验对象**（族外 `base__b02` + 族内 `base__b04`）现场通过，两个被验对象的解析值与打印串差异均为空。
  * **全族改用 lite TCL**：9 个段逐段打印自己的 TCL；自检 10/10 全过；段 1 在任何 lite 回执产生之前把 10 个 full-TCL 键冻结为跨报告口径对照，4 个失败回执改名保留后以 lite 在 PAR=2 重排。
  * **b05 之死定案**：主因是 `report_checks` 的 100000 条路径报告（b05 日志 `Startpoint` 恰好 100000 次、`worst slack` 恰好 2 次），不是布线、不是墙钟上限、不是并发、不是资源；lite 下同参数 10/10 rc=0。
  * **作废的旧数**：298.02 h、101.5 GB、31.4 MB/作业、b04 候选 663.7 s 均为 full TCL 口径。
  * **更正 LOG-20261025-38**（详见 LOG-20261025-43）："路径报告 100001 条"应为 **100000 条**；"决策上界 35 个"是**跑批前的投影上界**，实际决策数待扩面族 placed-selector 跑出后重算。
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果尚未产生**。

**补充（LOG-20261025-45）**：**扩面批运行期的三项硬结果 + 一项被推翻的旧数**（详见 LOG-20261025-45）：
  * **「部分完成度绝不出科学读数」已实测拦截**：批运行中（试点 41/58、主池 0/1393）跑 `scratch/post_ext_guard.py` 两种模式，**均 exit code 2**；`experiments/20261025_physical_labels_itc99_ext/decision_readings.{json,txt}` **均不存在** → 链停在第 1 步、**未产出任何决策级读数**。试点分类 ok=31、concurrency_artefact_recovered=4（正是 b05 被 lite 重跑救回的 rc=124）、missing=23。**附带可用性缺陷**：`scratch/post_ext_chain.sh` 默认 `--guard-batches default` 会要求对照池 389 键的回执，而 D1 已关对照池 → **默认跑法必然卡死在第 1 步**，批跑完必须显式传 `--guard-batches v3`。
  * **11:47 的 `scratch/post_ext_report.json` 是阻塞报告不是读数**（`status = blocked`、`decision_readings = null`、`blocked_because` 四个批次），已归档到 `scratch/post_ext_readings/20261025_114732/`（json sha256 49a51a54…、txt sha256 54b25914…）；该路径是链的**默认输出路径**，正式链会覆盖它。
  * **段 3 → 段 4/6 判定闭环已确认**：段 3 跑 `ext_par_rule.py` 写判定 → `ext_split_tables.py` 据此**重新派生**四张分组表 → 段 4/6 用 `group_par_timeout` 取每电路 PAR 与上限；`check_preconditions` 只查文件存在性、不校验判定内容 → 重判后不会误停。（断链就要重跑两天的批。）
  * **暂判判定不得产出工期**：`scratch/ext_wallclock_lite.py` 加了两道**只能变红**的门（`summary.pilot_complete` 必须为真 + 判定文件 mtime 不早于最新回执），实测暂判 → **exit 3、stdout 0 行**；合成最终判定 → 正常出数。原来的缺陷是：13:17 的暂判把 b05/b06/b07 判成 slow（PAR=1），而试点随后实测它们是 129.8 / 22.8 / 203.9 s，**按规则应全部是 fast**。
  * **工期旧数定案作废**：`scratch/ext_budget_v2.json` 的 `measured_seconds_per_job_pilot = 663.7` 是 **b04 一个电路**的试点均值，却被当作全族每作业秒数套到所有键上（389×663.7÷2 = 35.86 h、1393×663.7÷2 = 128.41 h、总计 298.02 h）。按试点实测**分电路**重算（两个独立实现互验一致）：主池布线后 **37.51 h**、对照池 **17.53 h**（均不含 b12）→ 批实际约 **2 天**，不是 12.42 天。
  * **族内判定带的来源缺口**：对照池是扩面族**唯一**的族内复现性底噪产地，D1 以「纯复现」关掉了它，而其省时理由 35.9 h 本身正是上面那个作废的数；分层抽样 28 键 / 5 电路只要 **1.33 h** → **OI-058 已于 2026-10-25 拍板**：选 **② 开全对照池 389 键**（+17.53 h），已就位**段 8 自动交接**与**族内带自动测量**两个常驻触发器（详见 LOG-20261025-49）。
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果尚未产生**。

**补充（LOG-20261025-49）**：**OI-058 拍板落地 + 两个常驻触发器就位**（详见 LOG-20261025-49）：
  * **拍板**：项目负责人就 OI-058 选 **② 开全对照池 389 键**（+17.53 h），**不做分层抽样、不走跨族继承**；`data/cases/**/results/` 的归一化**保持现状、本轮不动**（生成器在 `code/src/rseco/` 内，而 `code/` 本轮内容级锁定；受跟踪文件当前 0 脏）。
  * **段 8 自动交接触发器**（`scratch/ext_control_pool_trigger.sh`，5,029 B，PID 126442，armed）：等三段收齐（试点 58 / 主池 1393 / 布局后 1393）→ 等批退出 → **按精确 PID 停旧看门狗** → 等机器空闲 → 以 `--with-control-replicate` 重启批 → 段 1-7 由每键一目录 resume 语义跳过、只跑段 8 的 389 键 → 起**认识 389 键**的新看门狗。**批脚本与看门狗本身一个字节都没改**（开关本来就内置），**触发器自身不跑任何 EDA**；等待循环含幂等保护（`runs/round35_ext_t1` 若已满 389 回执则记一行后退出，不重复跑）。
  * **族内带工具与判据**（`scratch/ext_infamily_band.py`，11,036 B）：比较器**复用**`scratch/post_ext_replicate.py`（pilot=对照池、main=主池、`--expect-pairs 389`），新工具只做"产物 → 带 + 判决"、**一个门都不改**。判据**在数据产出前写死**：389 对硬钉、0 对可比即失败、**主判据 = 389 对全部逐位相同 → 族内底噪 0.000000 ns**；任一对不同 → **不出带**并要求重算下游判决；打印串不同也算不同；孤儿键拒绝；缺输入 = FATAL（exit 3）**不是判决**。套件 6 场景 **20/20 全绿**（本轮复跑确认）。
  * **口径边界**：**族内带 ≠ 候选级判定带**——族内带测"同网表同实现重跑有无运行噪声成分"（预期 0.000000 ns，既有依据 LOG-20261024-20 ④：F0 58 对 / F1 8 对非零差均为 0）；候选级判定带仍是**跨实现** F0/F1 = 0.049752 ns。若族内出现非零差 → **不出带**、**不得**沿用 0.000000 ns 的预期值。
  * **连带更正**：`scratch/post_ext_chain.sh` 的默认 `--guard-batches default` `DEFAULT_BATCHES` 含 `round35_ext_t1`（389）——选 ② 后该回执**将被跑出来**，故此前"默认跑法必然卡死在第 1 步"**不再成立**（主池/布局后两段的齐全要求不变）。
  * **批状态**：批 PID 478 / 看门狗 PID 696；试点段 **58/58 完成**（15:47:48 rc=0）；段 3 的 PAR/上限判定已更新、分组表已重新派生（`control_fast` 389 + `rest_fast` 1004 = 1393）；主池在跑（20:14 时 `round35_ext_full` **234/1393**、布局后 0/1393）。
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果与族内带数字均尚未产生**。

**补充（LOG-20261025-50）**：**主线自查无人值守路径 → 查出一个会静默卡死的真缺口并堵上**（详见 LOG-20261025-50）：
  * **缺口**：段 8 之前的批主流程里有 **4 个 `exit 1` 点**（`scratch/run_ext_batch_v3.sh` 第 **958 / 974 / 977 / 979-982** 行），而**重启后的批会重跑段 3** → 任何一处失败都会**在段 8 之前退出** → 对照池段一次都跑不到 → 看门狗每 600 s 重启一次、族内带触发器**永远空等**，**全程无人出声**。责任缺口 = **交接的发起方不确认结果，等待方又只会等**。
  * **关键假设已被证明**（不再只是注释里的断言）：**零 EDA 预演**（`scratch/r40_resume_rehearsal/run_rehearsal.sh`，7 项全过）用**假 `openroad` 写哨兵文件**当探针——三键都有回执时**哨兵从未出现**、回执逐字节未变、master 日志 3 次 `SKIP (already done)`；**反向对照**（删一个回执）→ **哨兵出现**，证明探针能分辨"跳过"与"真跑"；`FORCE` **在批脚本里从未被设置** → resume 确实生效。
  * **第三个常驻组件：交接看护** `scratch/ext_handover_supervisor.sh`（PID **139777**，只读、不起 EDA）：`WAITING`（还没发生）／`RUNNING`（正在出回执）／`OK`（389 到齐→退出）／`ALARM`（卡住→写明原因 + **批日志尾部**）**四态显式区分**；套件 **9/9 全绿**。**"还没发生"与"卡住了"必须可区分**——`ALARM` 是唯一的失败信号。
  * **两个落地门的假红根因是快照型断言**（`verify_log40_landing.py` 46/1、`verify_log41_landing.py` 92/6）：它们保护的是"某时刻的文件长这样"，而文件**本来就应该**继续长。**处置不是"过期即放过"，而是改成性质型断言**（每条被替换的断言都要有**至少同等强度**的替代、一条都不许删）。
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果与族内带数字仍尚未产生**。

**补充（LOG-20261025-51/52）**：**两个过期落地门改成了性质型断言；独立审计抓出并修好了本轮自己两个看护组件的两个真缺陷；第四个布线实现 F3 的设计与判据已预写**（详见 LOG-20261025-51/52）：
  * **两个落地门不再需要逐轮确认"过期即放过"**：`verify_log40_landing.py` **46/1 → 48/0**、`verify_log41_landing.py` **92/5-6 → 102/0**（主线独立复跑确认），**反向对照 16/16 场景**在隔离副本里逐条破坏、门**逐条变红**；**七条被替换的断言每条都有"至少同等强度"的性质型替代，一条都没删**。
  * **独立审计（`scratch/trigger_audit_r40b/REPORT.md`）总体判决 YES-WITH-RISKS**，并**抓出两个真缺陷**：① 交接看护的**活锁告警几乎永不触发**（"空→出现"不算重启，把"批死了又回来"也吞了）；② 族内带结果看护**把坏测量误标成科学结论**（`post_ext_replicate.py` 的 **exit 2 同时表示"至少一对不同"与"一对都比不上"**）。两者已修（看护升 **v3**，套件 **9/9** 与 **12/12**）。审计另**纠正主线一处判断**：`ext_failed.py --drop` 是**改名**不是删除 → **段 8 的 389 达不到的唯一路径**是"驱动被杀、留下只有 orig 没有 rc.tsv"。
  * **一处链外的结构性风险（须告知）**：批/看门狗/触发器/看护**全部活在同一个 WSL `Ubuntu` 实例内**，**Windows 侧零监护** → **WSL 一关整条链整体死掉且无人重启**。另 `scratch/ext_status.txt` 里的 `3233` 是**旧 v2 看门狗的陈旧遗留**，现行状态在 `ext_status_v3.txt`；查进程必须用 `Ubuntu` 这个 distro。
  * **第四个布线实现 F3**：**pin_hor `met5` / pin_ver `met2`**（{met3,met5}×{met2,met4} 网格里唯一缺失的角，与 F0 只差横向轴）。**判据已在数据产出前写死**（`scratch/fourth_impl_r40/f3_prereg.json`）：退化**双口径**（标签恒等为主、DB 指纹为旁证）、判决用 **ρ = 单轴/双轴** 的**五区对称分区**、**自助 CI95 跨 1 一律降级 INCONCLUSIVE**；**已发布族带 F0/F1 = 0.049752 ns 永不可改**。**关键新信息**：用这条判据跑**现有数据**，两个单轴比较**已经**是 **INCONCLUSIVE**（ρ = 0.926070 / 1.015863，CI95 均跨 1）→ **"族带是单轴敏感度的上界"这句措辞已被压在死区里**，F3 是去检验该偏离**是否系统性**。**一处细化（非推翻）**：LOG-30 的"b02 55/55"是**标签**计数，**"布线数据库逐字节相同"在 b02 并非全电路成立**（3 个候选 ODB 字节不同，差异是对象 id 计数器平移、长度与标签不变）→ **字节不同 ≠ 轴是活的**。
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果与族内带数字仍尚未产生**。

**补充（LOG-20261025-53）**：**"我们的数据集是不是公开可下载的公认基准"——查清了，并补上了缺失的溯源层**（详见 LOG-20261025-53）：
  * **不是 ICCAD 2015**。仓库全仓 **ICCAD 2015 / superblue / ISPD 作为数据来源 0 命中**；`ICCAD` 只以两种身份出现——**文献引用**（ICCAD 2010 FRAIG、ICCAD 2025 BUFFALO）与**竞赛问题规范引用**（ICCAD 2017 Problem A），**都不是基准网表**。
  * **当前用的是 ITC'99 + ISCAS89 + SKY130 HD + PicoRV32**，四者都是**可下载、许可明确、公认的公开基准**，仓库对每一个都记了**上游 URL + 固定 commit + SPDX + 逐文件 SHA-256**（`data/raw/benchmarks/source_manifests/`）。
  * **但必须分三层**：上游公开网表（别人**能**下载）／本项目派生的物理标签与训练表（别人**不能**下载，尚无公开归档与 DOI）。
  * **已补的缺口**：数据卡 §9 溯源链**前插了上游公开基准层**（原本从账本起步，答不上"从哪来"）；新增 §10 三层区分、§11 许可与再分发状态；`data/raw/benchmarks/README.md` 的治理表补入四条实际来源并修好一处**指向不存在路径**的断链；`experiments/design/benchmark_source_and_license_audit.md`（2026-07-20 定稿、**全文 ITC-99 与 ISCAS89 命中均为 0**）已补表。
  * **论文侧**：英文稿 `paper/en/manuscript/FAECO.tex:448` 的数据可得性 `\AuthorInput{}` **仍是占位符**；现已备好**只留"归档 DOI"一个占位、其余全部写实**的替换稿（`scratch/r41_provenance/DATA_AVAILABILITY_DRAFT.md`，含中英两版）。**本轮未改论文**。
  * **新登记的未决**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-059** | **仓库无顶层 LICENSE / NOTICE**（`LICENSE`/`LICENSE.md`/`LICENCE`/`NOTICE`/`COPYING` 实测**全部不存在**）→ 现在**不能**把仓库或本数据集称为"公开可再分发的项目"；而 Apache-2.0 / BSD-3-Clause / ISC 都要求随附许可声明 | open：须补 LICENSE + NOTICE（**须用户决定授权与发布形式**，不由 AI 代办） |
    | **OI-060** | **四份来源清单在盘上但未入库**：`sky130hd_openroad.json`、`picorv32.json`、`epfl_v2025.1.json`、`iscas85_jpsety_b4c6b620.json` 被 `.gitignore:70-72` 排除；**前两份是论文实际使用的上游**（SKY130 单元库、PicoRV32） | open：建议入库前两份（清单本身仅数 KB，不含 PDK 体积） |
    | **OI-061** | ~~13 个 b 电路的入选规则未记录~~ | **已关闭（LOG-20261025-55）**：规则**其实早已写在族 README**（`experiments/20261024_physical_labels_itc99/README.md:18-20`），本轮已**补录进 `source_manifests/itc99.json` 的 `selection` 段**：主族 7 个 = **"有台账 + 有噪声底族基线运行"**（冻结版图要跨族迁移），扩面族 6 个 = 主族不覆盖且物理可达；排除的 6 个各有实证理由（**b14 未证实**、**b15/b17/b20/b21/b22 真物理上限**、**b16 上游不存在**）；且 `pool_rule` 明写 **selection reads the ledger only**（防物理结果泄漏进选集） | closed：规则已入清单，数据卡 §9 已指向它 |
    | **OI-062** | **口径混淆风险**：论文 ITC-99 用 **19** 个电路（b01--b15、b17、b20--b22），物理标签族只用 **13** 个（b01--b13，基族 7 + 扩面族 6，互补拆分）；且扩面族**当前标签数为 0**（`dataset_summary_ext.json` 两批 `n_post_ok` 均为 0，**1393 是作业表行数不是标签数**） | open：论文与数据卡必须显式区分两套口径 |
    | **OI-063** | **许可表述精度**：ITC'99 与 ISCAS89 的**原始发布**无明确再分发许可声明；清单里的 EUPL-1.2 / Apache-2.0 属**镜像仓库自设**许可 | open：论文只能写"从 <repo>@<commit> 获取、该仓库许可为 <SPDX>"，**不得**写"ITC'99 是 EUPL-1.2" |
  * `code/` 未动、HEAD 未变、未提交；论文未动；**扩面结果与族内带数字仍尚未产生**。

**补充（LOG-20261025-54）**：**补上了"上游摘要 ↔ 我们实际用的文件"这一环，并查实了两个派生件**（详见 LOG-20261025-54）：
  * **新工具 `scratch/verify_benchmark_integrity.py`**：把六份来源清单逐条与盘上文件核对，分开计 `match / mismatch / missing / deviation / upstream-pin`。当前结果 **`match=57  mismatch=0  missing=0  deviation=3  upstream-pin=10`，退出码 0**。
  * **b18 / b19**：清单里的 `sha256` **就是上游文件在钉住 commit 处的 sha256**（用 GitHub contents API 取回上游内容逐字节核对确认）；**上游原件逐字节保存在 `experiments/20260804_itc99_probe/b18_truncated.blif` 与 `b19_truncated.blif`**（**"truncated" 是项目当时的误称**，它们就是上游原件：b18 141,045 B、b19 322,813 B）；而**获取路径上现在是项目自产的再导出件**（6,946,788 B / 16,010,495 B，2026-08-04 的 b18/b19 修复产物）。清单现已**同时**记下两个摘要（上游 `sha256` + 本地 `local_sha256`）。**影响范围有限**：b18 / b19 只出现在论文里"单独报告的大例子"，**不在** r30 物理标签族内（该族只用 b01--b13）。
  * **新登记的未决**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-064** | ~~b18 / b19 的"上游 → 派生件"这一步没有记录~~ | **已关闭（LOG-20261025-55）**：派生配方已**逐step 写进 `source_manifests/itc99.json` 的 `selection.derived_circuits.derivation_recipe`**（上游件 → 项目展开+注入隐式全局时钟 → Yosys `read_verilog/synth/dfflibmap/abc/clean/write_verilog` → `bNN_mapped.v`，脚本与产物路径逐个点名），**两个摘要也已并存**（`sha256` = 上游、`local_sha256` = 现文件） | closed：配方与双摘要均已入清单；**不影响任何已发布数字**（b18/b19 不在 r30 标签族内） |

**补充（LOG-20261026-56）**：**WSL 实例被释放曾让整条无人值守链一起消失，已用宿主侧看护堵上；残余风险另记**（详见 LOG-20261026-56）：
  * **事故**：2026-10-26 上午发现批 / 看门狗 / 两个触发器 / 两个看护**全部不在**，主池停在 **1100/1393**；`uptime` 显示 WSL 实例 **10:00:51 才启动**（uptime 0 min），两个看护状态文件的最后写入是 **07:23:36**——整台连同进程一起没了。根因是 `.wslconfig` 的 **`vmIdleTimeout=180000`**（空闲 3 分钟释放整台）**与"链活在 WSL 里"组合成了一个死锁**：链死 → 3 分钟无人 → 虚拟机被释放 → **连"把链叫回来"都做不到了**。
  * **损伤极小**：主池 **1102 目录 / 1100 回执、rc 全 0**，只有 2 个被腰斩；批的**逐键 resume 语义**使重启只补 293 个键。已实证 resume（段 0 门重跑通过、试点段 **30 s** 跑完 58 键＝全跳过、repair nothing to repair）。
  * **已堵**：`scratch/ext_chain_supervisor.ps1`（**Windows 侧**，PID 20636，300 s 轮询）——**跑在宿主上**，WSL 释放/重建都不影响它；**它自己的轮询顺带把虚拟机拉住不被释放**；**链跑完自动退出**把内存还给用户；状态文件在 Windows 侧、**WSL 挂了也读得到**。已做**端到端验证**（杀组件 → 检测 → 恢复 → 复活）。
  * **新登记的未决**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-065** | ~~宿主侧看护本身没有第二层保护~~ | **部分关闭（LOG-20261026-58）**：看护已改由**操作系统拥有**——**`schtasks` 计划任务（每 5 分钟）** + **HKCU Run 键（每次登录）**，外加**单例锁**（PID 文件，实测进程数恒为 1），**机器重启**这一种已被 Run 键覆盖。**仍 open 的部分**：**用户注销**期间两条通路都不跑（未实测），以及**自产复现包的公开归档**（仓库/版本号/DOI，**AI 不代为发布**） | open：注销场景未实测；若要彻底覆盖，需要一个 SYSTEM 身份的常驻服务（**要管理员权限**） |

**补充（LOG-20261026-61）**：**把“布线后到底是哪一档物理”立成台账，并查实签核级 RC 档在本机缺件**（详见 LOG-20261026-61）：
  * **寄生档位台账（新增）**：T0 理想线网 / T1 布局后（`estimate_parasitics -placement`）/ **T2 布线后（本族当前标签，`estimate_parasitics -global_routing`）** / T3 项目自有 SPEF（网表级启发式 RC）/ T4 签核级 RCX。**本族 = T2**，且已写进数据卡 §13，避免把 T2 说成“签核级”。
  * **T4 在本机不可用（实测）**：`extract_parasitics` / `set_rcx_layer_rules` 在 openroad 二进制与其全部 `ldd` 链接闭包中命中数均为 **0**；ORFS 在本机**只有平台子集**（无 `flow/scripts`、无 designs）→ **“接 ORFS 跑签核级 RCX”在这台机器上是工具链缺件，不是流水线开关**。
  * **新登记的未决**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-066** | **签核级寄生档（T4）在本机不可用**，以及“要不要开一条第二寄生模型交叉校验线（B）” | open：**C 路线（换/编译带 rcx 的 OpenROAD）需项目负责人决定**（代价=一次性构建任务，且换构建=另一套物理，**不得与已发布带 0.049752 ns 混用**）；**B 路线预注册草案已就位**（`scratch/r46_rcx/rcx_prereg.json`，参数与判据已写死），**待 go/no-go**；**A 路线（口径写清）零新件，本轮已随数据卡 §13 落一半**，剩余是论文侧表述 |

**补充（LOG-20261026-62）**：**无人值守链尾部的两个“失败被洗成成功”缺陷已修；三条残余未决**（详见 LOG-20261026-62）：
  * **已修**：后置链触发器与 F3 Stage A 触发器的 `DONE` **只允许由 rc=0 产生**（v2 新文件 + 沙箱 23/23 + 已切换 + 恢复脚本组件清单同步改名）；
    `post_ext_chain.sh` 的过期头注与默认守卫（`v3` → `default`）已按“只追加更正”改写。
  * **新登记的未决**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-067** | **三条残余**：① `ext_infamily_band_trigger.sh` 的日志把 exit 2 记成“有对不同”，而 exit 2 **同时**表示“一对都比不上” → 机械性失败会被引向物理归因（**产品本身措辞正确，仅日志行误导**；该组件在跑，改它需换实例）；② **存活判定只按命令行匹配**（`pgrep -f`）→ 沙箱残留或同名子 shell 可冒充“组件存活”，本轮已实测踩到并自纠；③ **“F3 永远 WAITING”无独立告警**（看护只对 `FAILED` 敏感） | open：①留到该组件下次重启时一并改（不得就地编辑在跑脚本）；②建议判据改为读 `/proc/<pid>/environ` 的 `EXT_ROOT` 并排除同名子 shell；③建议宿主看护增读 `ext_handover_status.txt` / `ext_f3_stage_a_status.txt` |

**补充（LOG-20261027-01）**：**昨夜 13 小时停机的根因查实并修好；OI-065 的残余从“假设”变成“实测”**（详见 LOG-20261027-01）：
  * **事故**：最后一份回执 2026-10-26 19:12:51 → WSL 今晨 08:09 才起来 → **13 小时零产出**；**零数据损失**（rc 全 0，逐键 resume 生效）；**40 秒内自动自愈**（恢复脚本拉起八个组件，含 v2 触发器）。
  * **根因（在宿主计划任务的 XML 里）**：`StopIfGoingOnBatteries=true` / `IdleSettings/StopOnIdleEnd=true` / **无 `ExecutionTimeLimit`** / `LogonType=InteractiveToken`，再加 `MultipleInstancesPolicy=IgnoreNew` 使每 5 分钟的触发被调度器**拒绝**（`Last Result=-2147020576`）。
  * **已修**：任务 XML 重写并导入（电池两项 false、`StopOnIdleEnd=false`+`RestartOnIdle=true`、`ExecutionTimeLimit=PT0S`、`RestartOnFailure=PT1M×999`、触发器改为「每 5 分钟 + 登录时」、`IgnoreNew` 保留）；新增 `scratch/ext_chain_probe_v2.sh`（`last_rc_age_min`/`outage_min`），宿主看护改指它 → **停机时长从此在状态文件里可见**（现为 787 min）。
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-065** | ~~宿主侧看护没有第二层保护~~ | **部分关闭（LOG-20261026-58）** → **再次更新（LOG-20261027-01）**：**机器重启**已由 Run 键覆盖；**电池/空闲导致的常驻实例被杀**已修（任务 XML 重写）；**注销/宿主关机期间的通路**仍是残余，且**现在有实测**：昨夜宿主不在线 → **13 小时零产出**（唤醒后 40 s 自愈、零数据损失）。**彻底覆盖需 S4U 或服务身份 → 要管理员权限**（注册为 SYSTEM 已被拒）。另：**这条链的日历进度由“宿主开着多久”决定**——昨夜赔掉 13 h；要压时间只能保持宿主不休眠，或缩减剩余段（对照池 389 键 vs 分层抽样，需重新拍板） |
    | **OI-068** | **`run_ext_batch_v3.sh` 头注仍是 D1 时代文案**（写“对照池不携带新物理信息”，已被 OI-058 取代） | open：该脚本**正在运行**，**不可就地编辑**；等它停下来再按“只追加更正”处理（行为本身正确——段 8 确实用 lite TCL + PAR=2 + 1800 s 上限跑那 389 键） **补充（LOG-20261027-82）— 已按「只追加更正」处理**：批脚本在战役收尾时**已停止**（2026-10-28 02:49 之后无实例），`scratch/run_ext_batch_v3.sh` 的头注**原文保留**，其后**追加**了一段更正：**OI-058 ② 已开全对照池（389/389、rc=0）**；「对照池不携带新物理信息」这句话**只在物理轴的意义上仍然成立**——复现的价值是**族内可复现性地板**（实测 0.000000 ns、389/389 逐位相同），而它的读数是「**合格候选子集读数**」、**不是**独立复现（独立复现只认 H4 的 58 对）。**脚本的行为本身未被改动**（段 8 仍是 lite TCL + PAR=2 + 1800 s 上限跑那 389 键）。**建议按此关闭**。 |

**补充（LOG-20261027-02）**：**看护的四种静默失效已变成告警；OI-067 的第 1、3 条关闭，第 2 条仍 open**（详见 LOG-20261027-02）：
  * **已关**：① **族内带触发器的 exit 2 报告**（v2：读产物 JSON，把“机械性失败（一对都比不上）”与“物理差异（有的对不同）”分开写，并写状态文件）；③ **“F3 永远 WAITING 无告警”**（看护新增该分支）。
  * **另修**：看护的 `$alarm` **从未复位** → 一次 ALARM 后状态永远 ALARM 且文案写死；已改为每轮复位并写当前原因。
  * **仍 open**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-067** | **存活判定只按命令行匹配**（`pgrep -f`）→ 沙箱残留或同名子 shell 可冒充“组件存活”（本轮已实测踩到并自纠） | open：**仍未改**。探针的 `alive()` 仍按命令行判定；正确做法是读 `/proc/<pid>/environ` 的 `EXT_ROOT` 并排除父进程同名的子 shell。改动会触及在跑的探针 → 需按“新文件 + 切换”做，且要同步恢复脚本与看护的组件清单 |

**补充（LOG-20261027-03）**：**OI-067 全部关闭**（详见 LOG-20261027-02 / LOG-20261027-03）：
  * ① **族内带触发器的 exit 2 报告** → 已修（v2：读产物 JSON，把「机械性失败（一对都比不上）」与「物理差异（有的对不同）」分开写，并写状态文件）；
  * ② **存活判定只看命令行** → 已修（`scratch/ext_chain_probe_v3.sh`：命令行 **且** `/proc/<pid>/environ` 的 `EXT_ROOT` 不在 `/tmp/` 之下；新增 `sandbox_leftovers=` 计数；看护已改指 v3 并重启）；
  * ③ **「F3 永远 WAITING 无告警」** → 已加告警（看护新增该分支，阈值 60 min）。
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-067** | ~~三条残余：族内带触发器的 exit 2 日志行、存活判定只按命令行匹配、「F3 永远 WAITING」无告警~~ | **已关闭（LOG-20261027-02 / LOG-20261027-03）**：三条全部处理完毕；其中第 ② 条是今天实测踩到的真洞（沙箱残留冒充存活 → 真实触发器没起来而探针报 alive），已加 `sandbox_leftovers=` 让残留**可见** |

**补充（LOG-20261027-23）**：**四项决策来自问卷的「自动选中」，不是项目负责人的确认**（必须留痕）：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-069** | **四项决策在 2026-10-27 12:09 由问卷自动选中（60 s 无应答 → 取推荐项）**：①对照池 389 键全跑；②b14 只入 base 一行；③B 路线 go；④宿主不休眠 | **open（待负责人确认）**。已按推荐项推进的部分只有两处，且**都不与批并发**：①对照池全跑 = **现状**（批本来就带 `--with-control-replicate`），无需动作；②b14 与 B 路线的**机件**备好且**排在战役之后**（`scratch/r63_postcampaign/ext_extras_trigger.sh`，两道门：战役 FINISHED + 机器空闲）。**改判的代价**：①改抽样 → 交接与族内带口径要重做；②b14 要候选级全族 → ≈415 h + 带门槛全量重算 + `itc99.json` 两条规则冲突（OI-066/D1–D6 那一串）；③B 路线 no-go → 预注册作废、机件闲置（无害，不删）；④若宿主仍会休眠 → **日历进度不可信**，进度只能按「机器开机时间」报 |


**补充（LOG-20261027-24）**：**B 路线预注册里有一格规则是空的，需要项目所有者补**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-070** | **预注册的判定规则漏了一格**：`rho>=0.9 且一致率>=0.9` → ROBUST、`rho<0.7` → SENSITIVE、`0.7<=rho<0.9` → MIDDLE —— 但 **「rho>=0.9 且一致率<0.9」这一格三条都不匹配** | **已补规则（LOG-20261027-37），仍待负责人确认**：那一格**在任何 T3 数据存在之前**填为 **MIDDLE**（沿用 rule_middle 的措辞：两个数照报、不作稳健/崩塌声明；**一致率未知仍报 UNRULED**）。**该规则由问卷自动选中的推荐项写入，负责人未确认，可随时改（改也同样在 T3 数据之前）**。**live 探针未获授权 → 预注册保持 DRAFT → 战役后那一步记为「跳过」而非失败 → 本轮不产生任何 T3 数据**：

**补充（LOG-20261027-38/39）**：这四条「自动选中」现在处在什么位置
    | 项 | 现状（2026-10-27 20:07 实测） |
    |---|---|
    | ① 对照池全跑 | **已在执行**：批 pid `292220` 带 `--with-control-replicate`，对照池 **121/389**；四段里三段已完成（试点 58 / 布线后 1393 / 布局后 1393，rc 全 0）。族内带路径**已在真实树上预验**（已完成的对逐位相同、DIFFER=0），**最终数字要等 389 键跑完**才算 |
    | ② b14 只入 base 一行 | 未动：排在战役之后（`scratch/r63_postcampaign/ext_extras_trigger.sh`，两道门：战役 FINISHED + 机器空闲） |
    | ③ B 路线 go | 预注册已补全规则（OI-070），但 **live 探针仍未授权** → 战役后那一步记为**「跳过」**（不是失败），本轮不产生任何 T3 数据 |
    | ④ 宿主不休眠 | 仍**未确认**：日历进度只按「机器开机时间」报；昨夜曾因此赔掉约 13 h |
    **另需知情**：本轮在战役中途修掉了**监控链自己的五个缺陷**（LOG-20261027-38）——
    其中最严重的一个曾让**对照池段有约 2.5 h 没有看门狗**（恢复脚本反复起重复的交接触发器，
    而那个重复实例每次都把刚起好的看门狗杀掉）；现已修复并补回看门狗，
    剩余时段有「懂 389 键」的看门狗兜底，且 Windows 侧看护已回到 **state=OK**。
    **这四条仍然是「问卷自动选中、未经负责人确认」**；若改判，代价仍按上表（抽样 → 交接与族内带口径重做；
    b14 候选级全族 ≈415 h + 带门槛全量重算；B 路线 no-go → 预注册作废、机件闲置）。

**补充（LOG-20261027-41）——C 路线的状态从「被网络卡死」改成「只差构建与拍板」**：
    | 项 | 现状（2026-10-27 20:5x 实测） |
    |---|---|
    | 旧理由 | 「取不到源码」 → **已被推翻**：`github.com` 不通，但 **`codeload.github.com` 返回 200**，三个源码 tarball 的首字节是 gzip 魔数；**apt 源全通**，`cmake/ninja/g++/bison/flex/swig` 都在 PATH |
    | 工具链 | 当前 OpenROAD **没有** `extract_parasitics`（布线级 RC 提取，命中 0）；那 1017 个 `rcx::` 符号来自 **OpenSTA 的 SPEF 读写** → **数据卡 T4 行「本机不可用」成立** → **需要一次新构建**（1–2 h、12 核） |
    | 准备件 | `scratch/r79_c_route/`：**取源脚本**、**就绪门**（当前 就绪 6 / 缺 4，缺项全是可自动补齐的工程件）、**准备文档**（含开线前写死的验收标准） |
    | 硬约束 | ① **时间隔离**：构建/EDA 不得与战役墙钟测量重叠；② **口径隔离**：独立族目录 + 独立带命名空间，**不得**与 0.049752 ns / `full_family` 混用或覆盖 |
    | 状态 | **未启动**。2026-10-27 的问卷在 60 s 无应答后**自动选中**了「并行准备、不跑 EDA」——**这不是负责人的选择**；待战役收尾体检通过 + 机器空闲 + 负责人拍板后再执行 |


**补充（LOG-20261027-42）——④「宿主不休眠」这一项的机制查实了，请按更正后的口径处理**：
    | 项 | 查实结果（2026-10-27 20:40，只读 `powercfg /query`，**未改任何设置**） |
    |---|---|
    | 睡眠超时（交流） | **0x00000000 = NEVER（从不）** → **本来就never** |
    | 休眠超时（交流） | **0x00000000 = NEVER** |
    | 供电 | **接着电源**（Win32_Battery status=2 = AC） |
    | 结论 | 「请保持宿主不休眠」对应的风险点**找错了**：昨夜那 13 h 的空档**不是睡眠定时器**，更可能是**关机/断电/注销**（与已知的 `LogonType=InteractiveToken` 残余一致） |
    | 有效对策 | **不是改电源设置**（已是 never），而是**机器回来时链自动接上**——**已就位且已实测有效**（19:02 触发器换代即接上、19:39 看护 `state=OK`） |
    | 仍存在的真风险 | **注销**期间两条通路都不跑（需 S4U/服务身份，需管理员权限）；这与「睡眠」是两回事，处置方式不同 |


**补充（LOG-20261027-43）——C 路线那一条的**结论更正**（独立事实核查之后）**：
    | 项 | 初版写的 | **更正后** |
    |---|---|---|
    | 工具链 | 「`extract_parasitics` 命中 0 → T4 档在本机确实不可用 → 需要新构建」 | **判据是空判**（TCL 压缩嵌入二进制，`strings` 看不见任何 TCL 命令名，**连已注册的 `estimate_parasitics` 也测出 0**）；二进制里**有** `rcx::Ext::extract` / `ord::initOpenRCX` → **「必须新构建」未获证实**，取决于**运行期** `info commands extract_parasitics`（**判定要在机器空闲时做**） |
    | 网络 | 「github.com 两侧都超时」 | **时点现象，已不复现**（20:4x 复测两侧都 200）；C 路线走 codeload 的 tarball，不依赖主站 |
    | 许可 | 「ORFS = BSD-3-Clause」「OpenRCX 的 paranoid 模式需商业许可」 | ORFS 仓库整体 **NOASSERTION/Other**（仅 build/run scripts 部分是 BSD-3-Clause）；「paranoid 需商业许可」**查无上游出处**（源码无该字样、仓库根无 LICENSE）→ **引用前须补出处** |
    | 带宽 | 未写 | **codeload 忽略 Range 头**（取首字节等于下整个包），实测吞吐 **3–10 KB/s** → 取源脚本改**断点续传**、失败不删 `.part`、**机器忙时拒绝下载** |
    | 现状 | 「只差一次新构建 + 一次拍板」 | **源码与规则都能拿到、依赖能装**；**「要不要构建」被降级为一条命令可答的运行期判据**；其余准备工作不变。**仍未启动** |



**补充（LOG-20261027-52）——一个**此前无人知晓的未提交删除**，需负责人决定（OI-071）**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-071** | **工作区里 `paper/zh/submission/word/superseded/` 整目录 7 个被跟踪文件被删除，且这次删除从未登记** | **open（待负责人决定）**：该目录是 **LOG-20261009-04/05 有意建立**的「旧 Word 转排稿归档」（HEAD 里的 10 个 `submission/word/` 文件含这 7 个）；工作区现在只剩 3 个（`FAECO_投稿Word转排_20261009c.*` + `转排说明.md`）→ **删除未提交、未登记**。**后果**：下一次提交（待办里已有「提交两份清单 + NOTICE」）会**顺手把这 7 个归档文件带走**，且不留任何痕迹。**两个选项**：① **恢复**（`git checkout -- paper/zh/submission/word/superseded/`，文件在历史里）；② **登记为有意删除**（写进 LOG、随下次提交一起提交）。**AI 不代为选择**（两者都改变仓库内容）。**同时已修门**：内容级检查原来把「已删除」只打印、**不计数、不影响退出码** → 文件被删时门仍绿；现改为删除单独计数、**有删除即红**，并在输出里点名需登记 | 


**补充（LOG-20261027-58）——OI-071 关闭：按自动选中的推荐项恢复了那 7 个归档文件**：
    | 编号 | 事项 | 状态 |
    |---|---|---|
    | **OI-071** | ~~工作区里 `paper/zh/submission/word/superseded/` 整目录 7 个被跟踪文件被删除，且这次删除从未登记~~ | **已关闭（LOG-20261027-58）**：2026-10-28 00:28 的问卷**60 s 超时 → 自动选中**推荐项「恢复它们」（**这不是负责人的选择**，可随时改）。已执行 `git checkout -- paper/zh/submission/word/superseded/` → 7 个文件（9.9 MB）回到与 HEAD 一致；**内容级检查由「19（内容 12 + 已删除 7）」回到「12（内容 12 + 已删除 0）」**。**该动作完全可逆**（文件在 git 里，若负责人另有决定——例如登记为有意删除——随时可在下次提交前改回） |

    | **OI-072** | **战役已 FINISHED，但对照池触发器仍是常驻进程**（`scratch/ext_control_pool_trigger_v2.sh`，实测 etime 9 h+、每 300 s 一跳、`ext_control_trigger.log` 持续追加「389 / 389 receipts」） | **open（待负责人决定是否收掉）**：supervisor 自身已在 2026-10-28 05:35 正常收束为 `state=FINISHED`（日志：「the campaign is FINISHED … the supervisor stops here so the WSL VM can be released again」），**但触发器没有随之退出**。**它现在只做计数、不起 EDA**（实测 `ps -ef` 里 openroad 进程数 = 0），因此**不影响任何测量**，但会**一直占着 WSL 实例**（宿主不能真正释放）。**本轮（r92）未终止它**——终止常驻件不在本轮 cron 的授权内，且它属于「战役期」的看护件，由负责人决定收尾更合适。**建议**：确认战役不再需要该触发器后，手动停掉它并把它的日志尾部归档；若它本应随 supervisor 一起退出，则那是**触发器缺少「战役已结束就退出」的分支**（可另立一条修）。**边界**：这一条只是**如实登记**，不是本轮修的东西。 |
    | **OI-073** | **链清单每次跑过演练就会变 STALE**（`scratch/post_ext_chain_manifest.sha256` 钉住了 `scratch/post_ext_drill/post_ext_drill.log` 与 `.json`，而演练每次重跑都重写这两个文件） | **open（设计使然，已知悉）**：清单之所以钉住演练归档，是为了**证明「跑演练的那份代码」没有变**；但演练归档里含**本次运行的指纹**（夹具里嵌了时间戳的合成产物哈希），所以**任何一次演练都会让它变 CHANGED**。r92 实测：清单重生成后 `21 same / 0 changed / 0 missing` → **CURRENT**；但只要再跑一次演练（体检第 7 项就会跑），它又会变 STALE。**这不是缺陷，是「钉住运行产物」这一做法的固有代价**。**处理办法**（待定）：要么接受「清单在跑演练后需重生成」这一约定（收尾清单 `after_campaign.sh` 第 4 步本来就会重生成），要么把清单改为只钉**演练脚本本身**（`post_ext_drill.sh` / `.py`，已钉）而不钉**演练归档**。**边界**：r92 **未改**清单的钉法（改它会动 `scratch/post_ext_manifest.py`，属清单语义变更，应由负责人拍板）。 |

## OI-074（2026-10-31，open）— 判定带只覆盖网表级离散，未含布局实现离散（2026-11-09 r116 论文侧已入文）

**现象**：`experiments/20261031_layout_stability/`（2 例 × floorplan 利用率 30/35/40 × base/ecofix）
实测 D−B 的跨布局极差：s641 **0.05 ns**（+0.84/+0.89/+0.84）、b13 **0.01 ns**（+0.11/+0.10/+0.10），
符号 6/6 全正；同网表同 util 重跑（u35）逐位复现既有四数族读数（偏差 0.0000×4），
故差异只能归因 floorplan。**s641 的极差约为其逐电路判定带 0.024558 ns 的 2 倍。**

**影响**：正文与补充里「D−B 超过逐电路带 ⇒ 可确认改善」这一判据，严格说只排除了**网表级抽样**，
没有排除**布局实现抽样**。对大效应例无碍（s641 的 0.86 是带的 34 倍以上，布局离散淹没不了它），
但对边际例（s820 +0.08 vs 带 0.0717、b04 −0.01）意味着"超带"不能升格为可确认改善，
现有"未确认"的处理是对的，但理由需要补上这一层。

**待决**：① 是否在 §5.5 表注或补充 S4.2 加一句限定（**论文冻结中，需用户明确批准**）；
② 是否把判定带改称"网表级判定带"；③ 是否扩到更多例（s820/s27/b11）以给出极差分布，
目前只有 2 例、只动利用率一个维度，不足以断言"所有例都稳定"。

**边界**：单工艺角（TT/1.8 V/0.5 ns）；aspect_ratio、pin 策略、CTS 缓冲列表、布线层均未变。

**扩面结果（2026-11-02 r103，`experiments/20261102_layout_stability_n8/`）**：待决 ③ 已完成。
8 例 × 利用率 30/35/40 × base/ecofix 共 48 次物理流程（约 42 min），u35 守门 **8/8 逐位复现**原四数族
（max|Δ|=0.0000）。请求的利用率经站点量化后实际 30.7%--42.9%（s27 被量化到 35.0/37.8/49.4），
核心面积变化 23%--26%（s953 由 5540.3 降到 4086.4 µm²），三档确为不同布局。
- **符号 8/8 三档同号**（全正）；`C−A` 三档逐位相同（跨档极差 **0.0000 ns**）⇒ 理想档与布局无关，
  布局依赖全部落在 D−B。r101 在 2 例上的结论现在 8 例全成立。
- **极差 R 0.01--0.17 ns**（中位 0.04）；`R/b` 中位 **0.61**，两例 >2：**s953 0.17 ns（3.8 倍带）**、
  s641 0.05（2.0 倍）。按预注册判据命中"个别例敏感"分支：带在中位意义上够用，对个别例不足。
- 合计 1.80 / 1.97 / 1.85 ns（u30/u35/u40），均值 0.2250 / 0.2462 / 0.2643 ⇒ **总量波动 ±8%，分例摆动远大于总量摆动**。
- **分级翻转**：u35 超带 6/8（与论文一致），但三档**全超只有 4/8**；s820（0.04/0.08/0.08 对带 0.071668）
  与 **s953（0.02/0.19/0.15 对带 0.045126）** 随档翻转。两者不同类：s820 是"仅高出 0.008 ns"，
  论文已记未确认；**s953 是幅度本身摆动近 10 倍**，而论文把它计入"6 例高于带值"。
- s27 的 u40 在 `detailed_placement` 失败（`DPL-0036`，CTS 后利用率 88.2%，1 个 DFF 放不下）⇒ **未评估**，不记零变化。
- 三档 `replace_cell` 命令逐条相同（同 4 个实例、同 master），故差异只能归因布局。
- **结论**：「某例超过判定带」是「该电路 + 该次布局」的属性，不是该电路的属性。

**新增待决**：④ §5 那句"6 例高于带值"是否改为"在 util 35 的这一次布局下 6 例高于带值，三档一致超带 4 例，
s820 与 s953 随布局翻转"，并把 8 例表放进补充 S4.6。

**处置（2026-11-09 r116，用户「A+B+C 全做」授权后执行）**：④ 已落地——主稿 §5.5 改为
「在利用率 35 的这一次布局下 6 例高于带值；三档利用率 30/35/40 重跑后三档一致超带的为 4 例
（s27/s382/s420/s641），s820 与 s953 随布局翻转（补充材料 S4.6）」，噪声底句由 r101 两例扩为
r103 八例，补充 S4.6 表由 2 例扩为 8 例 23 行、补 s27（u40 `DPL-0036` 未评估）与
s953（u35 base 臂 DRC=1）两条边界；**冻结读数、7/8 超带等主结论、图表编号均未动**，
补充 14→15 页，两篇质量门 PASS（主稿 11 页、补充 15 页，Overfull 0）。①（改称「网表级判定带」）
与 ② **未做**（正文已写明作用域，改称非必需）。剩余仅英文稿同口径（P1）。对应 `LOGS.md` LOG-20261109-04、
`paper/zh/CHANGE_LOG.md` §r116。

## OI-075（2026-11-02 立，2026-11-02 r102 关闭）— 伪代码写"首个可接受即提交"，两个运行器实现都是"候选集 argmax"

**现象**：`experiments/20261102_offline_decision/`（零新增 STA，读 `20260826_ablation_pureG`
的 3066 条逐候选记录）实测两件事：① **23/23 个提交组的提交者都是组内 WNS 最优者**
（`argmax`），没有一组是"构造顺序上第一个可接受的"；② 若按伪代码字面执行，
23 组中 **6 组**会取到更差的候选，其中 **2 组超过本电路判定带**
（s641 `_091_` 首命中 −1.42 / 最优 −1.25，差 0.17 对其带 0.024558；s420 `_058_` 差 0.10 对其带 0.042068），
一阶估计 8 例合计增益由 1.29 掉到 0.95 ns（保留 73.6%）。
另有一处结构差异：纯 G 族**一轮内对多个实例各提交一次**（s641 第 1 轮 4 次、第 2 轮 1 次），
与伪代码"提交即 break、刷新 `P` 再重提锥"的单提交语义不同；受控 9 臂族（`real_wns.py`）才是每轮一次提交。

**影响**：不影响已发表数字（本实验不改任何终点），但**按论文伪代码字面复现不出表中终点**；
§"评估、提交与停止"那句"首次可接受候选成为新基准"与 `alg:search` 第 8--11 行对两族都不成立。
三个代码位置：`code/scripts/run_hybrid_repair.py`（逐实例 all-then-argmax、`_accepts` 只认严格改善）、
`code/src/rseco/real_wns.py`（parallel 分支 collect-all-then-pick-best，serial 分支才有 `early_stop` break）。

**处置（2026-11-02 r102，用户"继续完善"后执行）**：①② 已改，③ 未做。
① `alg:search` 原第 9--11 行"首个满足 Accept 即提交并 `\textbf{break}`"改为
"按实例成组 → 组内测完 → `p^\star \gets \arg\min \operatorname{WNS}(p)` → 满足 Accept 才提交"，
净行数比原稿**少一行**（嵌套 `\If`/`\EndIf` 与 `break` 消失，压缩后算法框仍 11 行）；
§"评估、提交与停止"首句改为"候选按实例成组，组内全部测量完毕后取 WNS 最优者……
故提交的是组内实测最优候选，而非首个满足判据者"。
② 同段补两句族间差异："提交后网表随即更新，同轮后续实例在更新后的网表上构造候选，
因此一轮内可有多次提交；受控配置以整轮为组，每轮至多提交一次"，以及"`P` 与原端点 `t` 的锥在下一轮开始时刷新"
（`real_wns.py` 的 `jobs` 是整轮候选集、`if best is not None` 每轮只提交一个，已回读代码确认）。
另**摘要与 §1 各一处**"首次满足条件即提交"同步改为"按实例成组……提交最优者"——
否则摘要保留旧机制会与新正文互相矛盾。
③ 预算结论（上限压到 64 次候选 STA 仍保留 97.7% 增益）**未写入论文**：它属新增陈述而非纠错，
留给"要不要加一段预算说明"单独决定。
**校验**：10 页（改前 10 页）、0 Error / 0 Overfull / 0 Underfull；`verify_fournum_tables.py` BAD=0；
`check_env_refs.py` 无未引用图表；三份副本 PDF 逐字节一致 `bc7bdfff`。**所有数字未动，未提交 git。**

**边界**：只覆盖 ISCAS89 策略枚举族（纯 G 臂）；0.34 ns 的 Σregret 是一阶估计（换决策后后续实例
评测条件会变，归档未重放该分支），精确部分只有单组 0.17/0.10 两条；判定带借自 W1 族作分辨率尺子。

## OI-076（2026-11-02，open）— JOINT 滑窗枚举在组合内"R 优先"，与论文"各选首个 G"的语义不一致

**现象**：`code/src/rseco/real_wns.py:1543-1548` 的 `_joint_enumerate_combos` 在给组合内每个实例挑动作时，
先找 `kind == "R"`，找不到才退到 `"G"`：

```python
chosen = next((c for c in cands if c[2] == "R"),
              next((c for c in cands if c[2] == "G"), None))
```

而同文件 `joint_k` 路径在默认 `joint_mix=False` 时是**只选 G**；论文 §3.2 也写"联合动作取前两个可执行 G 的实例，各选首个 G"。
⇒ **两条 JOINT 构造路径语义不同**，滑窗枚举把 R 混进了组合。

**为什么重要**：R 在全池 1393 个候选里只有 6 个改善（1.3%），G 有 29 个（15%）。
组合里掺入弱动作会让 JOINT 候选系统性劣于基准——这与
`experiments/20261102_joint_depth3/` 观察到的"8 例中 7 例 JOINT 从未被接受"一致。

**证据**：`experiments/20261102_joint_depth3/REPORT.md` §4。该实验本身是单变量对照
（只改 `--joint-k` 与 `--joint-enumerate-depth`），结论"按现有实现无普遍效果"成立；
但**不能据此断言"联合动作无效"**，因为实现里混了 R。

**待决**：
① 是否把组合内选择改为按 `joint_mix` 分支（默认只 G），使实现与论文一致；
② 若改，需重跑 `experiments/20261102_joint_depth3/` 的 8 例作为新对照，`depth=3 只 G` vs `depth=0 只 G`；
③ 论文 §3.2 目前的描述对 `depth>0` 这条路径**没有覆盖**（该路径在主族未启用），若将来启用需补一句。

**影响面**：仅 `joint_enumerate_depth > 0` 时触发。论文现有的 72 次受控运行与 `tab:ablation`
全部是 `depth=0`，**既有读数不受影响**。

## OI-077（2026-11-02 立，2026-11-03 r113 关闭）— 动作集从未包含触发器：就地展开接入后 +0.39 ns

**现象**：`code/src/rseco/real_wns.py` 的候选集只覆盖组合门。

证据三条：

1. W1 的 s820 共 107 次候选尝试，`dfxtp` 出现 **0 次**；8 例合计 2200+ 次尝试，`dfxtp` 仍为 0。
2. `critical_instances` 的 99 项**全部是组合门**，无一时序单元。
3. 逐实例比对 OpenROAD 的修复结果，s820 上 14 处改动里有 **5 处是 `dfxtp_1 → dfxtp_4`**
   （该电路一共只有 5 个触发器，即全升），另有 `clkinv_1 → inv_2` 一处跨族替换。

**根因（两条独立路径，各自都足以排除）**：

```
_INSTANCE_LINE_RE = re.compile(
    r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)", re.M)
```

触发器实例名形如 `DFF_1._0_`（Yosys `synth -flatten` 产生，含点号，网表中为转义标识符 `\DFF_1._0_`）。
`(\w+)/\w+` 的 `\w` 不含 `.`，匹配在 `DFF_1` 处中断 ⇒ 实例被丢弃。
其次，即使匹配到，`cut` 只覆盖组合逻辑锥，时序单元不在 `gates` 里，`in_patch` 因此不含 DFF。

**这不是设计取舍，是实现疏漏。** 关键路径的起点与终点都是触发器，其驱动强度直接决定路径延迟。

**效应量**（`experiments/20261102_ff_action/`，网表级替换后同口径 STA）：

| 电路 | ΔWNS | Δ/判定带 |
|---|---:|---:|
| s832 | +0.1955 | 2.31 |
| s820 | +0.1013 | 1.41 |
| s953 | +0.0939 | 2.08 |
| s420 | +0.0669 | 1.59 |
| s713 / s382 / s27 / s641 | −0.0151 / −0.0106 / −0.0272 / −0.0432 | 负 |

**4 正 4 负，4 个正的都超过各自判定带**，净 +0.3615 ns。面积代价 +2.12%–10.71%
（`dfxtp_4/dfxtp_1` 面积比 1.19×）。

组合效应：逐点贪心合计只有 +0.2158 且仅 1 例超带 ⇒ 全升是单点贪心的 1.67 倍。
机制是同步升级消除「时钟负担」这一共同副作用。

**为什么重要**：这是全项目**唯一**的多例超带正结果（pin swap 0/4、JOINT 7/8 零变化）。
它也否定了准备写进论文的「动作空间已穷尽」——那个结论是在**缺少整类动作**的前提下得出的。

**待决**：

① 是否修 `_INSTANCE_LINE_RE` 纳入含点号的实例名，并把路径端点 DFF 加入 `actionable`
（须用开关保护，默认关闭，否则既有族不可复现）；
② 是否把「全部时序单元升一档」做成**一个组合动作**（而非逐点），因为单点贪心只拿到 1/1.67；
③ 接入后须补：SEC 复核（同功能换尺寸理论上等价，按纪律须实测）、物理档验证
（B 类曾在此翻车）、`_2` 中间档、只升路径上 DFF 的细变体；
④ 论文表述：这是「我们自己的实现缺口」，须写成「归纳出的设计原则 + 可复现证据」，
不宜写成「我们的 bug」，否则会被判为工程失误而非科学发现。

**影响面**：所有既有族的读数**不受影响**（它们本来就没跑过 DFF）。但论文中
「动作粒度小于测量分辨率」这一第一性原因的适用范围须收窄为「在仅含组合门动作集的前提下」。

### OI-077 追加（2026-11-02 r111）：接入尝试失败，两条路都被堵

**实验**：加 `--enable-ff-resize`（默认关，已验证默认参数下 s27 与 W1 逐位相同：−0.18 / 49 次 STA）。
实现分两支：① 顶层若有 `sky130_fd_sc_hd__df*` 直接实例，生成多实例联合候选；
② 若没有（0.67 族的形态），把 `module dff` 子模块内的 `dfxtp_1` 升为 `dfxtp_4`。

**失败一（0.67 族 = 论文实际用的族）**：候选被执行 2 次，但 `sta_executed=False`，被硬门拒绝：

```
F1_equivalence_failure: checker failed closed: Non-target helper module changed
F2_boundary_invalid:   boundary_closure fail, Non-target helper module changed
```

⇒ 等价检查器只允许修改**目标模块**，`module dff` 是 helper 模块，改它被判不等价。
**这是安全设计，不是 bug**：触发器是共享时序元件，改它会牵动整个时钟域。

**失败二（0.70 族）**：该族 DFF 是 `DFF_0._0_` 形式的直接实例（名字含点号），运行器启动即报
`no critical instances / endpoint D net` ⇒ `_INSTANCE_LINE_RE` 的 `(\w+)/\w+` 解析不了，整族跑不起来。

**结论**：现有实现下 DFF 动作**无法接入任何一族**。
潜力已有量化（理想档 4/8 超带；routed 档 0.239–0.474 ns、3.3–5.6 倍带，见 `20261102_ff_physical/`），
但「接入搜索后能拿到多少」这个数**拿不到**。

**同时必须记录的连带问题**：先前报的「1.81×」是**跨映射族比较**——
FAECO 1.2900 来自 0.67 族（`20261016_r22_cut_ablation_v3`），OpenROAD 2.3286 跑在 0.70 族
（`20261029_eco_phys_contrast`）。违反「同一 claim ⇒ 同一 config family」。**该比值作废。**

**因此论文的改法必须降级**：不能写「动作集完备性 > 搜索策略」并配一个「接入后增益」的结果；
只能写「发现一个被完整排除的动作类别 + 量化其单步潜力 + 说明接入的两个障碍」，
且不宜作为主贡献，建议放补充材料、主稿局限段加一句。

### OI-077 追加（2026-11-03 r112）：上一段的「1.81× 作废」撤回

在 **0.67 族同一批 8 个初态网表**上重跑 OpenROAD `repair_timing -setup`（`experiments/20261102_or_baseline067/`），
读数与 0.70 族首跑 **8/8 逐位相同**（s820 均 −1.1922→−0.9991、CELLS 138）⇒ 映射族**不进入 OpenROAD 侧**，
两侧比较等价于同网表比较，**比值合法**。r111 判「跨映射族」的依据是「FAECO 数与 OR 数来自不同映射器版本」，
但没有验证 OR 对该版本是否敏感；复跑证明不敏感。判据改为「网表是否同一批」。

该比值已按**幅度参照**写入主稿 §5.5 与补充 §4.7，并并列三条限制（动作集不同、预算不对等、参数未调优）。
**这不改变 OI-077 的 open 状态**：触发器动作仍接不进任何一族，接入后增益仍拿不到。

### OI-077 结案（2026-11-03 r113）：就地展开接入，8 例 +0.39 ns

**做法**：在目标模块内把 `dff` 实例展开成同族库单元（`CK→CLK`，`D/Q` 不变），helper 子模块字节不变；
检查器只增加一条精确识别（能解释为展开才折回，否则 fail-closed）。**`_scoped_module_pair` 未改。**

**结果**（`experiments/20261103_ff_unfold/`）：3 例接受，s820 +0.11、s832 +0.15、s953 +0.13 ns，
合计 1.29→1.68 ns（+30.2%），超带 5/8→7/8，候选 STA +11.8%，面积 +2.45%--3.18%，三例独立 SEC 全过。
`all` 作用域同终点但 STA +21.6%、s953 面积 +7.37% ⇒ 动作定义取割边界作用域。

**仍未做**：布线后档未重测（r110 的 2.0--2.9 倍放大属于离线网表，不能直接搬用）；
0.70 族的含点号实例名解析（OI-078）与本条解耦，仍按需处理。

**结论**：OI-077 关闭。论文不再写「动作空间已穷尽」，改写「补入一个被排除的动作类别后的收益」。

## OI-078（2026-11-04 立，2026-11-04 决策关闭 won't-fix）— 是否把映射族统一到 Yosys 0.70+255

**问题**：仓库里同时存在 0.67+146（Windows `bin/yosys.exe`）与 0.70+255（WSL `oss-latest`）两个映射族。
前者是论文主族（全部 ISCAS89 发表网表 + 受控矩阵 72 次运行），后者用于 ITC-99 映射与物理后验网表。

**实测代价（2026-11-04）**：
把 0.70 族网表（`experiments/20261029_iscas17_yosys_latest/s820/mapped.v`）直接喂给受控运行器，
2 轮结果是 `candidate_pool 0`、`sta_runs 0`、`stop_reason=no_new_candidate`；端点解析正常
（`endpoint=_260_ D=DFF_1.D`）、单元解析正常（146 个），但**割/补丁构造出不来候选**。
关掉全部触发器开关重试结果相同 ⇒ 0.70 族**目前跑不了**受控运行器，不是换配置能解决。

**统一的实际开销**（若先把 0.70 跑通）：
① 修含点号实例名下的区域构造；② 重跑主矩阵 9 臂 × 8 电路 = 72 次（约 4--6 h），
W1 的 1.29 ns、0.16125、5/8 超带、847 次 STA、面积区间、表 3/4/5 全部重算；
③ 触发器动作换实现（0.70 无 `dff` 壳，退回直接 resize），SEC 与物理档重做；
④ 论文全部数字与结论重写，与既有审稿口径断开。

**决策（2026-11-04，用户确认「按你的意见来」）：不统一，维持两族分工。**
理由：换映射器不会让结果更好，只会让既有数字全部失效；两族的归属与「不跨族比较」已在
补充材料 §2 与证据清单中写明，是可辩护的口径。

**保留动作**：0.70 族的解析与区域构造仍未打通，作为**未来若要迁移的前置条件**记录在此，
不列入当前待办。


## OI-079（2026-11-12，open）— 新主机交接入口与当前工作树状态漂移

**发现**：主线初检 HEAD 为 `51cebf5aa6a8946e81b7e2d6018ba8879660c749`（main，初始 clean、相对本地 origin/main ahead 59），交接材料却仍含 `94b75d9` / `7776ccb` 等旧身份。`.codex-handoff.json` 的 read_order 首项缺少 `project_docs/` 前缀，指向不存在的根目录文件；部分状态描述停在 Recovery 之前。

**科学计数冲突待查**：最新 LOGS 写跨族 145/202，接手提示写 136/202。须打开对应原始 summary/batch_results 并核对算法版本、配置与统计口径，不能直接改数字抹平冲突。

**处理**：先核验三项环境自检和实际路径，再同步现行交接文档。只有路径、身份、当前状态与计数归属均有证据后才关闭；计数若属不同版本须分别列明。历史记录保留，不修改旧科学结论冒充新验收。现有 OI-051 / OI-052 / OI-074 / OI-076 等状态不因本轮接手自动改变。


### OI-079 核验追加（2026-11-12）

审计智能体回报当前结果合计为 136/202，约 14% 对应新增面积回收，平均总面积降低约 4.54%。历史 145/202 与此不应合并；待审计将诊断版和最终算法版逐例绑定，交接材料同步后再判本问题是否闭合。

## OI-080（2026-11-12 立，2026-11-13 限定关闭）— 新主机完整测试存在 5 项 Yosys 相关失败

**实测**：`scratch/takeover_20261112_pytest.log` 记录 5 failed、1101 passed、156 subtests，199.89 s。失败包括 `test_convert_itc99_blif_to_v` 三项、`test_demo_runner` 一项、`test_yosys_abc_flow` 一项，涉及转换/CEC。CLI help 正常、Recovery 稿件 pdflatex 两遍正常不抵消该回归失败。

**待办**：先逐项复现和校验实际 Yosys/ABC 路径与版本、输入及调用，再区分环境问题、实现缺陷或设定问题；归因前不宣称全套测试通过，不重新启动科学批次。用户当前请求机制规划，本轮不实施修复。

## OI-081（2026-11-12，open）— check_record.sh 仍要求已停用交接文档

**发现**：记录自检脚本 `code/scripts/check_record.sh` 仍检查 deprecated `WORK_PROGRESS.md` / `project_docs/agent_handoff/` 文档，与 2026-11-04 起的现行 AGENTS 文档约定不一致。

**待办**：按现行 CANON / HANDOFF / LOGS / OPEN_ISSUES 入口契约更新检查器，再验证其能发现真实缺失且不要求维护旧入口。本轮仅登记，不为满足旧脚本而改停用文档。


### OI-079 核验收尾（2026-11-12，保持 open）

用户要求先做 ICCAD 适配性评估，未授权本轮推进完整机制实施。审计指出：202 为同名 cell swap，136 为累积实际回退；现行 CANON 尚缺 22 项资产登记，现有科学结论还需按 OI-082 澄清。主线仅加路线图评估横幅，未完成全部入口与科学口径同步，因此本项保持 open。

## OI-082（2026-11-12，open）— Recovery 科学主张超过当前测量对象与物理验证

**审计发现**：
- 分母 202 仅为同名 cell swap；136 为累积实际应用回退，不能替换成「逐个零影响」的计数。s953 `_351_` 个体读数 +0.0318 是反例。
- 约 14% 的分母是新增面积；平均总面积下降约 4.54%，两者不可混用。
- 当前结果复用原 SPEF 与 ideal clock，未重新合法化或布线，DRC 为 None，不能直接主张布线后物理安全。
- 跨布局按均值门槛为 6/8，按所有测点通过为 2/8；需绑定各自判据与原始值，不再笼统写旧 5/8。
- 官方 OpenROAD `recover_power` 与既有 parallel recovery 属必须比较的相关方法；Recovery 思路本身的新颖性尚未确立。

**待办**：先绑定数据版本、动作集合、分母和判据，再设计最强同条件基线及重新合法化/布线的物理闭环验证；待用户确认研究方向后实施。本轮只做 ICCAD 主题适配评估，未补实验、未修改历史科学结果。

## OI-083（2026-11-12 立，2026-11-13 修复关闭）— Recovery WNS 零值处理与导入路径错误

**源码定位**：`code/scripts/recover_area.py`（约 280/300/405 行与第 37 行，最终以表达式为准）：
- `res['wns'] or -inf` 把合法 WNS=0 当作缺失值。
- `delta_wns or -inf` 将零增量排在负增量之后。
- `if final_wns` 将合法零值转换为 None。
- `sys.path` 使用 `ROOT/src`，当前源码目录应为 `ROOT/code/src`。

**待办**：构造 WNS=0、delta_wns=0 和 final_wns=0 的边界输入，并核验 CLI 直接运行的模块导入路径；确认影响后修复并做整体回归。本轮为源码静态发现，无单独审计文件，未修复、未复现，不代表已确认历史全部结果受影响。


### 2026-11-12 验证推进授权更新（OI-080 / OI-082 / OI-083）

用户已授权持续推进三道验证门，覆盖失败测试归因/修复、Recovery CLI 零值/导入边界修复，以及原生基线与物理闭环的限定 pilot 预检和预注册。前文「本轮不实施」描述属于上一轮评估阶段；本次授权下进入执行。当前 OI-080 / OI-082 / OI-083 仍 open，须待实际复现、修复与回归/物理证据后逐项更新；不因授权自动关闭。


### OI-083 复现更新（2026-11-12，仍 open）

专用工程测试已得到 5 failed / 2 passed（0.90 s，无 warning），覆盖 CLI import、两种 baseline 下合法 WNS=0 被拒、零 delta 排序引起错误交互回滚、final WNS=0 写成 None。原「静态未复现」阶段已结束；测试使用外部 STA 替身，不能外推历史科学结果影响范围。尚待生产修复、专用测试变绿与整体回归。


### OI-083 修复更新（2026-11-12，等待整体回归）

四处最小修复已完成，新增 7 行为用例；与 routed_sta 测试合跑 18 passed / 1.75 s / rc=0，无 warning。当前专用工程门已通过；待主线完整回归与合并审查后再关闭。历史科学结果未重算。

## OI-084（2026-11-12，open，静态发现）— Recovery 自定义 Liberty 未贯通时序测量

**源码依据**：`code/scripts/recover_area.py` 约第 534 行 `--liberty` 仅参与面积计算，三处 STA 调用未传入该库；`code/src/rseco/routed_sta.py` 约第 151 行使用 DEFAULT_PLATFORM 的固定 TT 库。

**风险与待办**：传自定义 Liberty 时可能出现面积基于指定库而时序基于默认 TT 库。先确认当前实际源码路径、默认调用是否同库及自定义库复现，再决定最小修复并验证库身份贯通。本次只登记，未修复；不能推断默认历史结果已经失效。


### OI-080 归因与限定验证更新（2026-11-13，等待整体回归）

`yosys -V` 的失败为 0xC0000135，正确 PATH 仍复现；字节同一 exe/DLL 同目录镜像恢复 0.67+146 并令 24 项针对性测试通过（29.73 s）。诊断见 `scratch/oi080_diagnosis.md`，当前 Codex package identity 与 Windows packaged DLL 搜索顺序支持加载环境归因。本轮未改永久安装或代码。整体回归运行中发生测试产物清理并发，须主线整套结束后重检受影响 demo；未完成前不关闭。


### OI-080 限定关闭（2026-11-13，环境 workaround 已验）

字节同一的 Yosys/DLL 同目录镜像支持完整 1113 passed / 156 subtests（144.22 s），清理并发结束后受影响三文件再次 24 passed（29.35 s）。环境归因与重现工具 `code/scripts/prepare_packaged_yosys.py` 已固化，359 项 SHA 验证、幂等与拒绝异哈希覆盖实测通过。关闭范围为本主机 package 加载环境下的失败恢复；未修改永久工具安装，不主张改变 Windows 加载规则。

### OI-083 关闭（2026-11-13，四项 CLI 边界已验）

四处最小修复经先红后绿的专用测试、1113 项完整回归及并发清理后的 24 项重检通过。关闭范围为合法 WNS/delta 零值、final WNS 序列化与独立 CLI 导入路径；历史科学结果未因此重算。另发现的自定义 Liberty 贯通问题归 OI-084，保持 open。


## OI-085（2026-11-13，open）— escaped DFF 被生产解析跳过，Recovery 总面积分母不完整

**主线已确认**：生产 `parse_named_instances` 使用 `\w+` 而漏 escaped DFF。s382 CONTROL 全解析为 102 个已知 Liberty 单元、面积 1052.2592；旧解析为 81 个、611.8368，漏 21 个 DFF。RECOVERY 全面积 1005.9648，旧解析 565.5424。绝对节省 46.2944 相同，但完整总面积降幅 4.399526%，旧解析降幅 7.56648%。

**影响**：前轮从 14 份 summary 算得平均总面积下降 4.54223469% 不能再当完整总面积结果，应标为历史 parser-limited 分母。不能以同一分母错误下看似自洽的 summary 复算替代实例全量核验。

**待办**：只读重算全部 14 例、逐例绑定全解析/旧解析计数与面积，再更正现行 CANON/交接口径；生产解析修复需保 escaped 标识符语义、补失败对照并整体回归。当前尚未修复，旧科学文本暂保，不改论文掩盖缺陷。


### OI-085 关联影响追加（2026-11-13）

SEC 前置全解析还检出 `final_sec` 的 used_cells 扫描同样以 `\w+` 漏 21 个转义 DFF，使模型集不完整。此次在 prover 启动前被拦截，失败目录保留；证据脚本拟用全解析 cell 集生成模型，其余证明链保持。生产 SEC 解析缺口仍需作为本问题的影响面核验，不能仅修面积分母便宣布全关。


### OI-085 14 例审计更新（2026-11-13，保持 open）

`recovery_qualification_20261112/area_audit.{py,json}` 全解析证明 14 对网表均漏 escaped DFF；每例原/终漏项集合相同，绝对节省未变，完整总面积分母不同。s382 完整降幅约 4.40%，b07 约 7.81%。只明确排除无连接 tap，其数量和结构 hash 留存，未知有连接实例 fail-closed。层次 baseline 与 penalty 分母本次未审；生产解析/SEC 模型收集缺陷仍未修复，不能关闭。


### OI-085 完整分母复算更新（2026-11-13）

主线从 `area_audit.json` 14 对结果复算平均总 mapped-cell 面积下降 3.071500828%，s382 4.399524%，最大 b07 7.810443%。旧 4.54223469% parser-limited 平均值不再用作完整总面积结果。新增面积回收约 14% 仍须层次 baseline 审计，不因绝对节省量不变便确认分母正确。待生产解析、生产 SEC 模型收集及 baseline 口径一并处理。


### OI-085 漏项原因细分（2026-11-13）

最新 area_audit JSON 区分：14 例 DFF 漏项；s713/s953 各 1 个 escaped buf_4 正则漏项；s820 的 1 个 probe_p_8 来自显式 skip policy。完整面积以全部 Liberty-known 导出实例计，包含 probe；后续修复必须分别处理正则覆盖与面积统计策略，不能把 policy 差异冒充 regex bug。


### OI-082 物理 pilot 收尾（2026-11-13，保持 open）

s382 同状态重入/物理三臂/两组 SEC 已完成（`recovery_qualification_20261112/REPORT.md`），RECOVERY 总 mapped-cell 面积下降 4.399524%，propagated setup 退化 0.009971635 ns、hold 退化 0.000018596 ns、TNS 退化 0.312647 ns，严格非劣门 FAIL；native 零动作不构成强基线胜出。完整 SDC/DRV 约束覆盖未建立，路由 DRC 仅限支持规则。状态 NON_PROMOTION；新机制创新性、强等预算基线和物理安全尚未证明。

### OI-079 入口同步进展（2026-11-13，保留审计待办）

主线已同步 CANON 顶部、交接警示和 `.codex-handoff` 指针；Recovery 数字已区分累积回退、完整面积与 parser-limited 历史分母。现行入口有修正不等于全部资产/旧口径均已审清；22 项资产与后续 production/baseline 审计仍须交叉核验后再判本项全关。


## OI-086（2026-11-13，open）— ROADMAP 旧机制排他性与新颖性主张缺当前证据

**主线实查**：FAECO_ROADMAP旧§2含「文献中无竞品」「唯一」「Resizer缺JOINT」等排他性陈述，未由本轮机制/文献核验支持。OpenROAD当前官方Resizer文档（https://openroad.readthedocs.io/en/latest/main/src/rsz/README.html）明列多种变换、可配置sequence/phases，不能用旧简化描述论证我方新颖性。

**待办**：给旧段加历史/未验证标识，逐条映射我方动作、选择规则、预算与安全门到原生工具及最强相关工作；以当前源码/文档/实测和原论文证据定位差异。完成前不使用「唯一/无竞品/缺某机制」作为投稿创新论据，不改冻结论文伪造已完成文献审计。机制贡献仍待等预算强基线验证。


### OI-082 严格补偿阶段进展（2026-11-13，保持 open）

41次新物理试验中，A13/B12无strict点；C13唯一FORWARD096省0.594530321046%，WNS/TNS分别改善0.001714739461534/0.004840851ns、hold不变，完整结构/配置物理门/SEC101-0通过。D3主线实查均strict失败，尚待独立审核。局部严格可行性已有简单单动作baseline，不等于新机制、完整约束或泛化成立；不以更高节省但时序退化的D点替代可行终点。

### OI-086 新颖性门延续（2026-11-13）

当前唯一严格点来自从CONTROL独立回退一个cell的保守baseline；复杂B/D没有更优strict点。任何新选择/补偿机制须先胜过这一已验简单基线并做同预算对照，不能把41次探索后找到的点归因给尚未证明的复杂机制。


### OI-082 / OI-086 本轮阶段结案边界（2026-11-13）

A–D完整审计41有效，局部唯一严格点096及SEC/独立接受已齐；阶段STAGE_CLOSED，不等于研究目标达成。联合机制与同预算强基线优势、完整约束与泛化仍未建立。D失败已排输入/目标错误并完成路径/Liberty只读归因，未将其判为补偿普遍无效。OI-082/086保持open；OI-084/085工程与口径缺口不因本轮endpoint接受而关闭。


### OI-082 完整约束缺口定位（2026-11-13，严格搜索新轮静态审计）

主线实读旧 `resizer_flow.tcl` / `resizer_sta.tcl`，只有create_clock，无set_input_delay/set_output_delay；已接受FORWARD096的propagated.tcl同样没有IO delays、loads、transition。顶层含CK及CLR/FM/TEST三个data inputs、六个outputs。已接受点仍只在当前约束域成立，不能外推IO时序/外部负载完整覆盖。后续须明确真实接口约束来源和测量对象后补齐，不能事后任意补约束再混用旧验收；本轮9点计划不因只读审计被静默改写。


### OI-085 候选范围审计追加（2026-11-13，静态不改变九点计划）

`strict_area_search_20261113/space_audit` 完整102实例/335pin静态审计得同family、全部pin/functions及sequential属性一致的正面积替换62pair/33实例。旧13回退只有10positive覆盖10pair，另3zero；遗漏52pair（23新实例51pair，原054额外4→2一pair）。其中FF12pair/8实例、clock-family14pair/4实例、其它组合36pair/21实例。

旧rollback log并非完整候选生成器，不能称动作空间穷尽；但这些只是逻辑兼容候选，未EDA/未SEC，遗漏不能全归解析bug。未来生成器需独立枚举并绑定面积/逻辑/约束，先完善时钟与接口约束再扩FF/clock域。本轮已冻结9候选不变。


### OI-082 / OI-085 / OI-086 严格搜索阶段结案（2026-11-13，保持 open）

9+2新物理点全部有效strict失败，旧096 exact endpoint仍是接受基线；本轮无SEC新结果。OI-082的IO约束缺口具体为3data inputs/6outputs未设IO delays/loads/transition，不能外推完整IO保证。OI-085候选生成审计表明62静态兼容目标仅10被旧rollback覆盖；不是62有效收益，也非52全为bug，未来需独立生成并逐项物理验证。OI-086本轮风险排序在k3及全部prefix没有收益，不能包装机制创新；需转候选覆盖与强同预算基线，而非给已无改进九池换排序。三项及customLib等其它未决继续保留。


### OI-082 约束诊断实测（2026-11-13）

记录端实际读library_area_search_20261113/constraint_audit/REPORT.md；两次readonly STA rc0，CONTROL与已接受096均报告3项missing input delays（CLR/FM/TEST）、6项missing output delays及6个unconstrained outputs（GRN1/GRN2/RED1/RED2/YLW1/YLW2）。clock/原约束未改、WNS/hold复现旧值，不证明IO时序；无连接tap blackbox警告保留。用户WNS-primary/TNS-secondary新目标不修复该覆盖缺口。须来源明确的完整SDC，不能臆造IO预算当原benchmark规范。


### 当前用户时序政策更新（2026-11-13，OI-082等未决不自动关闭）

用户最新允许10ps WNS损失，主门改CONTROL−0.010ns（1e-6数值容差），TNS辅助，hold原非退化/非负硬门保留，需0/5/10ps对照。明确为预算权衡，不能称原零退化目标已达成。旧WNS-primary重筛与待证明对象暂停，新包重新选择；缺IO约束、科学泛化/机制/解析等未决仍保持。


### 当前准备状态（2026-11-13）

用户清除长期goal并要求简要解释后，本轮准备阶段收束。10ps门下RESTORE074为根/独立一致的历史重筛最优候选，尚未新SEC、未正式验收；25库候选和新政策证明待续，均非运行中。原IO约束等缺口保持open，不因新政策筛出候选自动关闭。


### OI-085 分母子门限定闭合（2026-11-13，整体仍open）

s382 area_baseline_audit已完整解析层级/DEF并绑定阶段：A0修复前CTS892.1056，AR1052.2592，AF1005.9648，净新增160.1536、回收46.2944（28.90625%），CTS前处理82.5792排除。该s382快照分母子门闭合；AR为repair后最终合法化/布线快照、不是瞬态累计。其它13设计分母及生产escaped/SEC scanner问题未因此关闭，不恢复旧全族比例。


### OI-082 / OI-085 限定接受更新（2026-11-13）

RESTORE074已有10ps新政策、SEC101/0与根/独立接受；s382同阶段净新增分母核验完毕。该单点资格不补齐IO约束，不外推其它设计分母/production解析，也不证明算法机制优势。整体未决保持open，旧strict失败不回写。


### 可调预算实现门更新（2026-11-13）

预算纯核心/历史端点CLI及全回归1147passed/156subtests通过，v1环境遗漏已用同字节镜像修正并保留原失败。此门不关闭online physical evaluator接入、完整IO/多角/跨设计、旧生产parser/SEC scanner、customLib等问题，也不证明新机制优越。OI-080既有workaround再次验证，不新增安装变更；OI-082/084/085/086等保持各自未决范围。


### OI-081 本轮复查（2026-11-13，保持 open）

check_record.sh返回rc0，仍警告4份obsolete文档。继续按现行AGENTS不维护停用文件，检查器迁移待处理；不因rc0把此契约漂移关闭。其它未决按上述范围保留。


### OI-086 总体机制调研更新（2026-11-13，保持 open）

总体研究邻域包含E-Layout ICCAD2026、PCR2026预印本、RL-CCD DAC2023、Trident2 ICCAD2013、Task-based TCAD2023、OpenPhySyn WOSET2020及OpenROAD，详见overall_related_work_20261113/REPORT.md与来源表。预算、多动作、反馈不能直接当独创机制；相关工作存在也不自动否定本项目。

实际outerloop/recover_area/budgeted_search三链未统一，完整候选与交互选择的价值仍是待验假设。需相同实际物理验证成本的强贪心/原生恢复对照、组件消融、完整约束和跨设计验证，才能主张预算内净面积回收优势。本轮定向调研无EDA/SEC，不是系统综述或算法效能验收。


## OI-087（2026-11-23，open）— v22 端点口径、主稿对照与复现材料待对齐

- **SKY130**：TT 10/10 正面积回收（0.67%–5.58%）和 SS/IO+OCV 通过率涉及不同端点。中文 v3 §7 的 `s713/s832` 在 IO+OCV 门控下回退 `CONTROL`、面积收益为零，原端点 IO+OCV 通过仅 8/10，且若干通过 setup 预算的端点仍有 hold 下降。SS 10/10 含 `s641` 改用的安全端点（0.66% 降幅），FF hold 严格非退化 6/10。待逐电路对齐 TT、SS、FF、IO+OCV、面积及 SEC 端点，并同步摘要、贡献、结论、图 1 旧 `7/7 IO` 标签和总入口。
- **对照与复杂度**：同预算单门在线贪心面积均降 2.11%（9/10 正收益），FAECO 均降 2.01%（10/10 正收益）。`b15` 的 7.7× 来自 `184.83 s / DRC=0` 对 `1426.14 s / 66 DRC`。LR 0/10 限于本轮 5 次冻结 SPEF 实现及后验门。微批次实现可递归两半，限定 `O(log N)` 为满足条件的单转折路径。
- **ASAP7**：中文 v3 §7.3 的 `−21866.84 ps` 是负裕度变体重布线前的绝对 TNS，对应差量 `−9461.64 ps`。对应 `SUMMARY.json` 的字段为 `tns_ps_pre_reroute`、`dtns_ps_pre_reroute`。应与正常原生变体全局布线后 `−2516.01 ps` 的 TNS 差量明确区分。单设计、估算全局布线寄生、理想时钟，评估次数与原生单次运行不同。v22 清单绑定报告及汇总，原始 LR/ASAP7 驱动、日志及重放资产分散在忽略目录与 WSL，需归档输入身份和证据回执。
- **交接记录**：`HANDOFF_2026-11-23.md` 的 16 页与实测 15 页不一致，`PROJECT_MAP.md` 保留旧 HEAD/v19，`EXPERIMENT_REGISTRY.md` 缺 v21/v22 原实验条目。待同步现行入口、登记与证据交叉表。OI-081 的旧检查脚本单列。


### OI-087 联合门复查启动（2026-11-23，open）

既有 `s713/s832` IO+OCV CONTROL 原始 STA 日志给出绝对 hold `−98.219/−75.316 ps`。历史回退端点的 IO+OCV 相对 setup 与 hold 差值均为零，绝对 hold 仍为负。联合门是否能在同一端点恢复正面积收益，按 `SKY130-JOINT-B10-S713-S832` 实验登记与本轮证据包判定。


## OI-088（2026-11-23，open）— 联合门驱动跨 Verilog/DEF 的转义实例名绑定

`SKY130-JOINT-B10-S713-S832` 的 `s713` 初跑 `RUN_001/RUN_003/RUN_004` 在制备候选物理端点时由 `STA-0125` 退出。Verilog 有转义实例 `\DFF_0/rebuffer1`，冻结 DEF 的 OpenDB 实例 `DFF_0/rebuffer1` 存在且 master 一致。三个运行在替换阶段停止，未获得候选布线与 STA 度量。先对本轮驱动进行 DEF 精确实例及原 master 验证，并以相同预算在独立输出目录重试。是否闭合以重试及身份核验结果为准。


### OI-088 限定闭合（2026-11-23）

本轮实验驱动在发出 OpenROAD 命令和构造读回期望 master 表时统一使用 DEF 实例名，候选 ID 保留源 Verilog 字符串。逐候选校验源 master 后，`s713_replay/RUN_001` 重用动作和工件哈希均匹配的 DRC=0 物理产物，身份门通过，四场景各自产出有效 STA。该候选由真实 IO+OCV 绝对与相对 hold 门拒收。修复范围为本实验驱动，生产工具中既有 escaped DFF 解析议题仍归 OI-085。


### OI-087 SKY130 证据子项收口（2026-11-23，整体 open）

十个名义正回收物理端点及 s641 替代、s713/s832 回退点已逐一对齐，原始 CONTROL 差异、相对约束及绝对 hold 违例均在 `project_docs/evidence/sky130_joint_constraints_20261123/ENDPOINTS.md` 明列。两例联合复查已完成，严格正收益端点 0/2，s832 有单独的相对诊断端点。中文主稿、图 1 及入口同步由后续稿件验收判定。强基线与复杂度解释、ASAP7 证据复现和历史索引剩余事项仍按 OI-087 跟踪。


### OI-087 中文工作稿修订（2026-11-23）

四场景与两例联合研究口径、贪心比较、b15 的 DRC 条件、ASAP7 TNS 的阶段与量，以及图 1 的历史 IO 注记已在中文工作稿对齐。新实验原始证据已归档。其他历史复现驱动与索引继续跟踪。


## OI-089（2026-11-23，open）— 中文 v3 近邻覆盖与引用元数据

按主稿提交 802c453a 与一级来源核对。主稿 §2 尚未纳入直接近邻 Fatemi 等关于产业后布线尺寸/阈值优化的研究。该方法使用灵敏度排序和可调 slack 下限，检查 hold 与电气约束，并在工业多模式多角流程验证。差异论证应聚焦共同物理起点与质量门下，昂贵详细重布线预算内的可接受面积收益。[作者稿](https://vlsicad.ucsd.edu/Publications/Journals/j129.pdf)

参考文献 PCR 的主稿作者与一级来源不同，一级来源为 Jiang、Pan、Lan、Zhu 的 2026 arXiv:2610.01918，当前条目写作 ICCAD 2025。E-Layout 的一级来源为 2026 arXiv:2610.26432，作者页注明 ICCAD 2026，当前条目写作 ICCAD 2025。待逐条对齐作者、年份和发表状态，并同步相关工作表的任务边界。[PCR](https://arxiv.org/abs/2610.01918) · [E-Layout](https://arxiv.org/abs/2610.26432)


### OI-089 TCAD 准备状态（2026-11-23，open）

用户已选定 TCAD 作为后布局 v3 投稿目标。直接近邻缺项、PCR 与 E-Layout 的作者和出处偏差仍待随稿件核验修订。启动可复现实装底稿、约束来源及近邻基线的准备检查。具体实验以正式预注册为准。


## OI-090（2026-11-23，open）— SKY130HD 物理专用单元与独立 STA 寄生端口不一致

SKY130HD Ibex 的原始布线及 RCX 已完成。ORFS 的 `6_report.json` 记 84 个天线单元，原 `write_verilog` 导出排除物理专用 master。独立 FF 以原 `6_final.v/.sdc/.spef` 读入时，`qualify_original_io/FF.log` 告警 `ANTENNA_*` SPEF 端点找不到。该会话的 FF 度量保留为模型诊断。资格复测使用保留物理单元的 `6_final.odb` 与同源 SDC/SPEF，并通过同生产器 OpenROAD 内置 STA 同口径测三个视图及后续 SKY 候选。待验证读取和门控收据。


### OI-090 限定闭合（2026-11-23）

按完整物理 ODB 和同源 SDC/SPEF 重测，三个视图均返回有效读数，TT 复现生产器，证据见 `sky130_control/CONTROL.json`。所得 SS hold 为实测违例，另归 OI-091 跟踪。

## OI-091（2026-11-23，open）— SKY130HD Ibex 原始共同起点的 SS hold 违例

原 ORFS 输入保持原 I/O 与时钟，虽然 DRC 和天线均为零，物理 ODB 三视图重测的 SS 绝对 hold 仍为 `−1379.766 ps`。原始 CONTROL 和资格不通过的记录一并保留。另起独立目录从同一原始快照诊断并修复 hold。修复后 CONTROL 须以原 SDC 在三视图闭合 hold、DRC、天线、RCX 和共享零动作资格，方可开始 SKY130HD 三臂。


### OI-091 限定闭合（2026-11-23）

修复后共同起点在原 I/O、完整 ODB 及新 SPEF 的 FF/TT/SS 下得到 +288.152/+466.107/+115.914 ps hold WNS。新 DRT=0、天线零、RCX、原 SDC 字节一致及原始至修复两态 SEC 13648/0 均核验通过。此闭合覆盖该共同起点的 P0 资格。原始 CONTROL 的不合格收据及 SS setup 负余量保留。共享零编辑复提 RCX 后同三视图精确复现，并开始 P1。[修复起点收据](evidence/tcad_ibex_20261123/sky130_control/REPAIRED_CONTROL.json) · [零动作核验](evidence/tcad_ibex_20261123/SKY130_NOOP_AUDIT.json)

## OI-092（2026-11-23，open）— 原终态 filler 占位阻断新增 hold buffer 合法化

SKY130HD 的首个 hold 修复续跑从原终态派生，保留原终态 21,961 个末段 filler，合法化 `DPL-0038` 报 100.1% 占用，未开始布线或 RCX。重试保留物理输入与 SDC，先验证拆除对象只属于原 filler master，再在详细布线后补回 filler，查核其余原实例身份。原失败与技术修正后的新物理证据分开。


### OI-092 限定闭合（2026-11-23）

仅移除原四种末段 filler，满足合法化前置条件并在布线后合法复填 21,936 个，完成 DRT 及 RCX。新端点的独立天线违规由 OI-093 跟踪。

## OI-093（2026-11-23，open）— SKY130HD hold 修复端点的天线违规

`hold_repair_sky130_02/endpoint/` 的 DRT=0 且 RCX 完成，独立天线检查仍报告一条网、一个引脚。原件 `antenna.rpt` 指向 `data_rvalid_i → hold3717/A`。保持共同起点资格门，等待同一原约束下的天线闭合和新提取；诊断 STA/SEC 仅供判定后续修复。


### OI-093 限定闭合（2026-11-23）

`_03` 的 DRT=0 后再次独立检查发现两条天线路径。按原生 diode-only 修复一次、两颗二极管及增量 DRT 后，最终独立天线和 DRC 报告均为空，RCX 完成，原 SDC 指纹一致。收据 `hold_repair_sky130_03/RECEIPT.json` 绑定原件。此修复的时序和 SEC 准入仍按 OI-091 跟踪。

## OI-094（2026-11-23，open）— Ibex 相对预算运行配置的旧字段

P1 setup sweep 的原始配置沿用基础驱动的 `tns_gate=false` 与 `final_budget_slot` 描述。逐候选重算核对了实际逐角 TNS 门。ASAP7 FAECO 最后一轮有两门，来源为已发起批次的二分递归，三臂仍各用六次物理评估。原配置随哈希封存，重用驱动时应让运行器显式输出实际门和递归预算口径。[实验报告](evidence/tcad_ibex_20261123/REPORT.md#按原周期归一化的-setup-预算对照)

## OI-095（2026-11-23，open）— Ibex 等面积耗时的同负载复现

ASAP7 主档单门与 FAECO 在各自第三次到达同一已验证物理端点，分别实测 1135.931 s 与 810.920 s。相同端点的一次 DRT+RCX 本身差 83.558 s。单门阶段与另一工艺同机并行，自适应阶段独占该机的 EDA 队列。当前样本提供时间、物理验证次数和 SEC 次数的配对描述。要把耗时差归因至调度方法，需要同负载环境下调整方法运行顺序并做独立重复。[ASAP7 主比较](evidence/tcad_ibex_20261123/REPORT.md#asap7-主比较)


### OI-095 同机同负载配对复现（限定闭合）

相同 CPU 亲和性、四线程和冻结输入下，两对交换顺序，四臂第三次获得同一个达到面积目标的 SEC 端点。单门多用 40.311 与 35.195 WSL 单调秒，候选物理调用次数相同、SEC 多一次。结论限于本台机器、同一设计同一验收端点下这两组观测。独立时钟测量范围另见 OI-096，跨设计及方法速度普适性尚未验证。[复跑报告](evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md)


## OI-096（2026-11-23，open）— WSL 单调计时与宿主稳定时钟的速率差

ASAP7 复跑期间短时同机配对采样显示，WSL `CLOCK_MONOTONIC_RAW` 与 Windows QPC 吻合，`time.monotonic()` 在采样区间推进约快 4.0%–4.6%。预登记的四臂比较保留同一 WSL 单调秒，日历 UTC 用作顺序标记。抽查倍率仅用于讨论时间差对共同缩放的敏感性。换算宿主实时时间仍缺少从每臂起点到终点的同域 QPC/RAW 计时。[时钟原件](evidence/tcad_ibex_20261123/ASAP7_SERIAL_CLOCK_AUDIT.md)

### OI-096 新一轮筛选消融计时已改用 RAW（限定进展）

新一轮筛选、物理探针和矩阵记录使用 `CLOCK_MONOTONIC_RAW`。跨早期筛选与探针准备的宿主 QPC 围栏为 107.747–108.334 s，RAW 经过 108.030 s，符合围栏，旧 `CLOCK_MONOTONIC` 同段经过 112.922 s。新轮计时直接使用 RAW，先前 ASAP7 各臂仍按当时所测时钟标记。并发负载差异另作为试验工况记录。[新筛选消融](evidence/tcad_ibex_20261123/SCREEN_ABLATION_REPORT.md)


## OI-097（2026-11-23，open）— SKY130HD 高扇出缓冲候选筛选

18 个候选的 TT 最差 setup 路径均穿过本次缩小的高扇出缓冲。FIFO 与寄存器堆各一例用七组 TT STA 交叉验证，CONTROL SPEF 下换候选 ODB 就出现大幅 WNS/TNS 损失。诊断闭合到这两个分支的归因。候选筛选如何处理高扇出和时序敏感度、排序变化后能否在相同 setup/hold/SEC 门下回收面积，仍需新实验。[TT 归因](evidence/tcad_ibex_20261123/SKY130_TT_CAUSE.md)

### OI-097 温和换门及低扇出探针（限定进展）

两处高扇出缓冲降至较近的 `buf_8` 与两处扇出 1 的替换均完成详细布线及三角 STA，四个端点都通过 setup 联合包络与绝对 hold。原 CONTROL 的 SS 相对 hold 门拒收四个端点，实测候选面积下降 5.0048–8.7584。历史零编辑自身下降 0.079936 ps，四个探针对它的差异在 −0.026645 至 +0.003553 ps。T02 在同一正式门下把原排序 TT setup 拒收从 18 降到 0，并确认四个正回收实例。主要剩余拒因为 SS 相对 hold。当前在高扇出上直接验证的仍只有两处代表缓冲，其他扇出与档位下是否复现、以及零编辑重布线能否成为稳健的相对 hold 对照仍待检验。[筛选消融报告](evidence/tcad_ibex_20261123/SCREEN_ABLATION_REPORT.md)

## OI-098（2026-11-23，open）— 自适应拆分占用后续候选评估预算

留出 GCD 的冻结筛选池中，固定批次在第 5 次以排名 13–15 的三门获得回收 11.2608（0.234742%，SEC 262/0）。FAECO 在相同六次预算内依次评估 `(1,2,3)`、`(1)`、`(2,3)`、`(2)`、`(3)`、`(4)`，同池未触及可行组合。该样本表明早期被拒批次的拆分会与向后覆盖竞争预算。何时切换到向后扩展，以及新调度能否同时保留 ASAP7 的 SEC 节省仍待独立实验。GCD 证据限于本次六次预算。[GCD 留出核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_GCD_VERIFIED.json)

Ibex T02 在筛选池上重现同一 FAECO 候选排名序列，六次都只因 SS 相对 hold 拒收。固定批次在第 3 次覆盖排名 7–9 并回收 22.5216，首达 0.01% 目标，六次累计选中 62.56。此时观察范围覆盖 Ibex 开发样本与 GCD 留出样本。[Ibex 核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_IBEX_VERIFIED.json)

Ibex 第三次 FAECO 已测物理端点面积减 17.5168，SS hold 与旧零编辑重布线完全相同。在历史零编辑基准下的端点诊断已补原网表对候选网表 SEC 13648/0。正式矩阵使用冻结原 CONTROL，FAECO 在六次内的回收仍为零。用零编辑重布线作相对门后，调度会实际怎样推进、用多少时间，仍待独立实跑。[hold 投影](evidence/tcad_ibex_20261123/SKY130_SCREEN_HOLD_PROJECTION.json) · [端点 SEC](evidence/tcad_ibex_20261123/SKY130_SCREEN_FAECO_HOLD_SEC.json)

2026-11-24 补查，AES 的筛选 FAECO 同样只覆盖排名 1–4，不过覆盖至排名 16 的原固定臂也未找到合格端点。按相对 hold 拒因延后拆分的只读回放在三个 SKY130HD 设计上重现固定臂的六次动作，触及 Ibex/GCD 原已验收端点。两条 ASAP7 实测轨迹均保留 setup 失败后的原拆分。当前已定位六次配额下的覆盖损失，规则能否在独立对象上超过固定批次、减少实际验证耗时仍为 open。[调度诊断](evidence/tcad_ibex_20261123/SCHEDULER_COVERAGE_DIAGNOSTIC.md)

显式启用的改进调度已在原 Ibex/GCD 筛选池各独立实跑六次，均弥补了原 FAECO 未覆盖的动作组，并复现各自原固定臂的验收端点、面积、时序和等价证明。两个旧样本上首达耗时由各自观察值报告，旧固定臂均用时更少；当前仍待测试新样本、预算和实际同负载比较，以判断触发策略何时有优势。[调度实跑](evidence/tcad_ibex_20261123/HOLD_AWARE_REPAIR_REPORT.md)

后续四路筛选实测减少了相同探针前缀的组件时间，但原固定和修复调度的首达物理路径相同，筛选机制可由两方法共用。独立留出及采用优化配置的完整搜索比较仍为 open。[筛选报告](evidence/tcad_ibex_20261123/SCREEN_WORKERS_BENCHMARK.md)

用于正式同池比较的 Ibex 三臂采用单次 pin access 和四路筛选实测成本。固定与 FAECO 六次轨迹相同，720 s 内均回收 43.792 µm²、六次 62.56 µm²，均在第 3 次首达。AES 三臂采用共同自动邻网释放规则，固定和 FAECO 的实际前三次派发均相同，第 2 次均回收 33.7824 µm²。至今同轨迹样本可支持相对单门的具体优势，FAECO 与固定的行为分离和跨独立样本的收益仍待实测。[Ibex 正式报告](evidence/tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_REPORT.md) · [AES 正式报告](evidence/tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)

新一轮先查实延后队列未被耗尽的原因，再冻结触达电容重排。Ibex 新配对改变派发，0.01% 首达从第 3 次到第 2 次，720 RAW s 的最优面积持平。GCD 转移第 5 次达标的时间相近，第 6 次新接受使窗内最优从 11.2608 到 15.0144 µm²。两设计窗内新臂最优各增加一处负 setup，但满足原预算。不同设计的共同时间或面积优势、排序效果和真实剩余窗消耗仍不确定，需要也保留 AES 和新族结果以及同面积时序细节。[触达电容报告](evidence/tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)

AES 完整复跑 v2 中，电容重排使第 2 组多支付一次 DRC 返修仍因 FF/TT hold 拒，首达到第 3 次，固定第 2 次即达到相同合格面积。v3 开发臂避免一项已知徒劳重试，恢复部分时间，但仍慢于固定的实测首达。另一个初评 SS hold 失败的六门跳过真实重试，其可修性未知。要检验可迁移性，需维持独立设计／候选验证与已跳过候选的机会成本，并报告真实余量与原绝对、相对 hold 门。[AES 配对和重试报告](evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

AES 定向配对复现固定第 2 批逐字相同的合格端点，事先用该端点的历史独立 DRC 标记省下实际一次初次物理验证。随后已知六门和四邻网全新实跑，720 RAW s 窗内比固定多 31.28 µm²。同一设计的已知动作和标记可省实跑工作，独立设计如何提前获取同类证据及普通候选首达收益仍待验证。该轮未实测原 v3 第 4 次跳过的重试。[AES 定向修复报告](evidence/tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md)

进一步只固定同一组六动作，用已有同动作诊断包的定向预放行与原重试做 ABBA 四臂，在同物理验收目标上两次都少一次失败物理验证。现有证据说明已有诊断如何节省后续真实评估，新增诊断的代价、候选排序及跨电路的收益仍需独立验证。[诊断组件对照](evidence/tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md)

冷启动三臂已计入从冻结输入生成待修候选前置诊断的成本。固定和在线固定相同派发、同物理首达由 429.504 降至 358.364 RAW s，窗口最大合格回收相同。FAECO 与固定共用在线后端时首达晚一次，窗内最大合格回收由 33.7824 增至 67.5648 µm²。实际验收前轮 v3 第 4 次暂缓的六门，该组当前可修性得到验证。候选池与设计之外的派发收益、首达与最佳面积的取舍及拒批拆分策略仍是 open。[冷启动矩阵报告](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)

新的同电路 2×2 正反序补齐 FAECO 常规缺格，常规后端下 FAECO 两次均比固定首达晚、最终面积持平，在线后端下也较固定晚首达，两次在共同窗内多回收 33.7824 µm²，均为同组六门和同物理端点。两种调度各自开启诊断后，在保持同物理首达的配对中两次均节省时间。下一层未决是如何兼顾首达和未来大面积候选、与共在线后端的单门强基线比较，以及跨设计／工艺的效果。[2×2 正反序报告](evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md)

同在线后端的单门比较已在 SKY130HD AES 完成两种运行顺序及四臂独立核验。FAECO 在 720 RAW s 的合格面积回收 67.5648 µm²，单门贪心 22.5216 µm²，两种顺序的共同目标首达分别早 137.843／128.373 RAW s。前四个完成请求中 FAECO 触及 12 个候选，单门触及 4 个候选，两种策略各接受两次。批量尝试和反馈排序同时变化，仍需让单门使用同反馈、在同时间和同验收门下分离两项作用，另需在独立设计／工艺上检验。前轮固定批次首达更快。ASAP7 UART 的原约束冻结起点已通过 hold、DRC、电气与自证，正式候选比较尚未启动。[贪心配对报告](evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) · [UART 资格登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-asap7-uart-original-control-qualification-v1)

## OI-099（2026-11-24，open）— AES 主留出原始起点的 SS hold 违例

SKY130HD AES 的原生 ORFS 流程已完成 DRT 和 RCX，DRC 为 0。原 3600 ps/720 ps SDC 与 I/O 均匹配，SS hold WNS 为 −975.978 ps、TNS 为 −124464.094 ps，原起点资格状态为 `hold_infeasible`。后续需从冻结原生端点在原约束下实际修复、重布线和复提取，并重做三角绝对 hold、DRC 与 SEC，才可作为留出矩阵共同起点。[留出报告](evidence/tcad_holdout_20261123/REPORT.md)

### OI-099 最终修复共同起点（限定闭合）

同原约束的 `ss_hold_targeted_v2b` 端点重新完成 DRT/RCX，DRC 为 0，FF/TT/SS hold WNS 为 +336.274/+523.915/+55.296 ps，原生至修复后全网表 SEC 11089/0。资格文件和证明分别为 SHA-256 `c697450a257ef4e63182f02c0ce4fb3c5925b41f366628a97672ac440192d4f8` 和 `bdc28e0f27e7b653965de68a27e611cbc4da006105bb68ef063756ee1f3ac02f`。此资格限于共同起点，候选效应另验。[留出起点报告](evidence/tcad_holdout_20261123/REPORT.md)

## OI-100（2026-11-24，open）— AES 筛选候选的多视图相对 hold 拒收

AES 的 18 个冻结筛选候选均完成 DRT/RCX，setup、DRC、电气与绝对 hold 全部通过。每个候选至少触发一角相对 hold 拒收，SS 17、TT 3、FF 3，候选可跨角。两个固定批次均实测面积减 33.7824，第 2 次只因 SS 下降 1.609379 ps 拒收；第 5 次 SS 改善 0.190514 ps，而 FF/TT 各下降 0.070222/0.108413 ps 并被拒。正式回收为零。[AES 核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_AES_VERIFIED.json)

2026-11-24 新的同配方零编辑重布线改变了六条未触达网，SS 相对 hold 下降 0.676792 ps，绝对 SS hold 仍为 +54.618976 ps。更换相对参照的只读投影使 8/18 次评估通过其余物理和时序门，最大面积减量 0.009665%，六次面积减量为 33.7824 的三门评估均仍被拒。对其中两次的三个实际拒收视图做 12 次 ODB/SPEF 交叉 STA，确定这些 hold 变化由候选寄生复现，沿最差路径定位到发射或捕获的时钟到达变化。待检验减少未触达网变动、保护关键时钟寄生后，原正式联合门能否稳定保留回收，及在其他物理实现上的复现范围。[AES 归因](evidence/tcad_ibex_20261123/AES_REROUTE_HOLD_DIAGNOSTIC.md)

真保护零编辑保持原布线并精确复现三视图四个 WNS/TNS。按实测 DRC 标记分别放行两个非时钟邻网后，原固定第 2 次修复端点面积降低 33.7824（0.028996%），15,646 条保护网未变，恢复 ROUTED 的全块 DRC、天线均为 0，原三角 hold 和 tradeoff setup 门、SEC 11089/0 通过。该端点新增 SS 负 setup 端点，原 slack +0.329958 ps 降到 −0.228706 ps。第 5 次释放其两个邻网后同样通过 DRC，三视图相对 hold 仍退化。其他动作、跨设计效果和可自动确定的开放网范围仍为 open。[AES 保护路由报告](evidence/tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)

第 5 次的剩余退化经三视图交叉 STA 归因于寄生变化。三选二全部因原相对 hold 门被拒。将一门替换成已测有发射侧补偿趋势的等面积降档后，原三视图联合门、解锁态全块 DRC、天线及 SEC 全过，回收 33.7824，无新增负 setup 端点。合并上轮另一个合格端点实际通过以上各门，回收 67.5648，SS 新过零端点仍来自前一动作组，slack 为 −0.214495 ps。扩大放行网和补偿动作的自动选择及独立设计实测继续 open。[AES 残余 hold 优化](evidence/tcad_ibex_20261123/AES_RESIDUAL_HOLD_OPTIMIZATION.md)

自动保护与按真实 DRC marker 放行的共享规则，在正式固定／FAECO 的第二组实际达到 33.7824 µm²，均有独立实际 SEC 11089/0，三角保持原 hold 门。两臂同一六门的第三次重试超出硬窗。窗外完成同一重试虽解锁态 DRC 为 0，仍有 FF/TT 相对 hold 下降 0.049849/0.077660 ps。捕获时钟网保持几何锁定时提取总电容仍增 0.0000792 pF。自动选出适合多门提交的组合、减少首轮与自动重试的实际开销，以及跨设计测试仍待完成。[AES 正式报告](evidence/tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)

对该窗外排名 4–9 候选，12 次 ODB/SPEF 交叉复现了相对合格三门的三角寄生变化。定向用等面积 `_21033_` 替换 `_13098_`，保留其余五门，实际回收 67.5648 µm²（0.057992%），绝对和相对 hold、解锁态全块 DRC、天线及 SEC 11089/0 全部合格。原 setup 预算内，TT／SS 分别新增 2／1 个负 setup 端点。三角配对路径实测捕获分支的原电容增量消失，且发射侧延迟给 FF／TT 提供补偿。该定向选择属于独立于正式计时的控制性修复，原候选状态保留。候选替换的自动化、用完整成本验收、降低新增负 setup 端点与跨设计覆盖仍待验证。[AES 归因与修复](evidence/tcad_ibex_20261123/AES_RANK4_9_HOLD_REPAIR.md)

新配对中另一个次组放行数据邻网解决 DRC 后尚有 FF/TT 相对 hold 退化，12 次交叉 STA 复现其 SPEF 效应。v3 第 5 个不同六门候选的三角可过，窗外同字节物理端点的独立全块 DRC 仍有 8 项。两种阻塞均须在未来自动选组时纳入，跳过重试后的未知可修性另列。当前最大定向合格端点和硬窗方法结果保持各自证据来源。[AES 配对与重试报告](evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

v3 第 5 次的 8 项标记已在同一六动作上定向解决。由独立全块报告定位的四条非时钟邻网，从同冻原一起重新路由后，两次完整物理均解决短路、间距且原三角与 SEC 11089/0 通过。新计费配对在 454.205 RAW s 接受 65.0624 µm²，TT 和 SS 各一条新增负 setup，预算内。此局部问题限定闭合。六门组跨设计选择、无需历史已知标记的候选修复和新增负 setup 减少仍为 open。[AES 定向修复报告](evidence/tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md)

诊断接口另对三份已有真实报表做只读检查，分别解析 4 标记到两条邻网、6 标记到另一对邻网、0 标记到空集合；其中 6 标记的原真实重试仍有 FF/TT 相对 hold 拒收。当前已验收接口能从输入取到合理物理邻网，其三视图效果仍取决于实际布线、提取与原 hold 门。[诊断组件对照](evidence/tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md)

冷启动在原冻 ROUTED 布线上换门后先去除直接信号的旧线，由实时全块检查生成预放行。先前按非法初评 SS hold 暂缓的另一组六门，实时按原标记邻网开线后，窗内回收 67.5648 µm²，三角 hold 改善、无新增负 setup、独立全块 DRC 0 和 SEC 11089/0。固定同后端的多组六门仍有 FF／TT 相对 hold 拒收，说明能否消除实体 DRC 和能否通过 hold 是两道实际门。[冷启动矩阵报告](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)

冷启动 FAECO 第 5 次九门的独立检查被硬窗截停，对原产物进行窗外独立全块 DRC、天线和真实 SEC 后确认合格 98.8448 µm²。此例定位出剩余验证流水线开销，不能按布局后的初报判定通过。若要在相同硬窗及时提交这个大小的端点，须缩减前期无效评估或完整端点验收用时，并保留所有原门。其它设计上的泛化和潜在负 setup 端点继续 open。[冷启动矩阵报告](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)

## OI-101（2026-11-24，open）— 减少 pin access 次数改变 ODB 二进制身份

在 GCD、Ibex 各自固定且原可接受的一个三门端点，删去嵌入导引情形的显式 `pin_access` 语句、保留 DRT 内部默认步骤，顺序交换均减少单次候选耗时。两种方式的 DEF、V、去日期 SPEF、三视图时序、DRC、实际改线和证明点相同。仅 B 的 ODB 字节不同，且不满足预登记的全对象一致门。需定位 ODB 内部变化并用更完整的下游重复评估检验，暂保留原搜索配方。[pin access 对照](evidence/tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)

后续读回的 AP 接入点几何多重集一致；将诊断副本中的 AP 与其引用清理后，同一设计各臂字节一致。GCD 仅保留显式单次的 C 与仅保留 DRT 内置单次的 B 产生字节相同的原始 ODB，均与原双次方式不同。差异已定位至 AP 辅助数据，原对象次序及中间 ODB 重入后的下游行为仍待检验，原生产配方尚未改变。[pin access 对照](evidence/tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)

GCD 完整冻结路径四个六次搜索臂的候选接受与输出一致，单次方式在两对顺序各缩短 4.249、5.073 RAW s 的含筛选首达时间。两步重入的 GCD/Ibex 分别在全部四种模式组合复现共同判定。限于受验路径，当前已支持下一阶段同范围 SKY130 冻结起点比较统一显式启用单次，默认双次仍可复现历史配置。ODB 原始字节身份与更多重入步数、候选和流程的稳定性仍需继续跟踪。[搜索报告](evidence/tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md) · [重入报告](evidence/tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)

## OI-102（2026-11-24，open）— 冻结起点累计重布线与 ODB 重入改变验收

GCD 相同累计四门原冻结路由未过 TT/SS 相对 hold，重入前一步合格 ODB 后追加同一门达 15.0144 µm²、SEC 262/0；Ibex 相同累计六门原冻结路由通过，重入却出现 TT 新电容违例与超预算 TNS 并拒收。两设计在各自所有单双次 pin access 组合下得到共同判定。后续需要单独对比路由起点、已有几何和目标改线范围，判断何时重入有益。现行方法比较继续使用同一冻结起点路由规则，重入结果单独登记。[重入报告](evidence/tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)

## OI-103（2026-11-24，限定闭合）— 硬墙钟裁剪的工具超时需运输为候选截停

新 AES 触达电容配对 v1 优化臂第 3 次重试的独立恢复 ROUTED DRC 被剩余墙钟裁剪至 2.626940724 s。子进程的 `TrialFailure rc=None` 比硬墙钟早 0.005096355 s 返回，驱动以 1 退出，优化臂没有正式终态。前两次完成且拒，第三次无完整独立 DRC 和 SEC。v2 根据是否实际受剩余墙钟裁剪判定，保留普通工具超时与真正工具失败的异常路径。v1 的针对性回归复现，v2 三例通过。[实验登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-sky130hd-dispatch-optimization-and-aes-rank49-v1)

v2 重新串行两臂实际退出 0，优化第 4 次复现受硬窗裁剪的独立 DRC 截停，真实终态通过独立核验。此次 AES 驱动在剩余窗超时前少量返回时的处理闭合。其它流程和更广负载不由本例认定，v1 原始异常保留。[AES 配对报告](evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

## OI-104（2026-11-24，open）— JPEG 原生起点的 SS hold 不可行

原生 SKY130HD JPEG 的 DRT、原生天线和 RCX 完成，保留原 5 ns、1 ns I/O 与原时钟语义。三次提取后 STA 证明 FF、TT hold 非负，SS hold WNS/TNS −2,340.727／−41,475.257 ps。最差为 `rst` 的异步 removal，另有 `qnt_val[0]` 输入到常规寄存器 D 的 −1,256.375 ps。若另做共同起点修复，须继续用同一 I/O 与绝对 hold 门并独立完成原物理和证明条件。原生不合格保留，候选和方法比较尚未启动。[资格登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-sky130hd-jpeg-original-control-qualification-v1)

独立 SS 清点 26 个负 min 端点，其中 14 个 `RESET_B`、12 个 `D`。同端 max 复核显示，14 个 reset 和 8 个 `qnr.divider` 的 D 端有理想等量延时余量，另 4 个 FDCT 数据端的 min/max 同时为负。最差 reset 端理想所需延时约 2.341 ns；原 SS 报告中另一 reset 分支仅余 1.451 ns recovery，不能用共享输入的全量延迟解决。局部分支、不同数据路径及采样钟需分别判断，尚无修复或新共同起点。

## OI-105（2026-11-25，open）— 现行布线前诊断与调度的跨设计及强对照

2026-11-27 补做 AuDoPEDA 功耗恢复首轮排序投影。保持 40 ns 处理器的共同目标、固定三门、720 s 和后端，原灵敏度／功耗乘 Setup 裕量排序终态回收分别为 91.3376／43.7920 µm²，6 次完成中分别验收 4／2 次。该例形成了同池同后端的现代外部排序对照。全局布线原生算法、跨设计迁移和先进学习方法的共域测评仍开放。ECC Sizer 发布版的实例排除与全局门禁无法表达逐实例目标配对，可作为原生提议参考。 [对照证据](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#40-ns-处理器同池同后端的外部排序对照) · [AuDoPEDA 作者论文](https://arxiv.org/html/2601.06268v2#S4.SS3) · [ECC Sizer 发布版](https://github.com/openecos-projects/ecc-sizer/releases/tag/v0.1.0-alpha.1)

2026-11-27 只读审查固定 OpenROAD 的 `repair_timing -setup -phases GLOBAL_SIZING`。原生 LR 在 WNS 达到配置目标后退出，搜索等价库主单元并以时序和漏电或面积决策。默认设置预期在正裕量的 40 ns 参考上没有迭代。人为调高目标可测原生时序修复，但原生门仍要求最终 WNS 不退化。全局 `dont_use` 同时影响源和目标，无法表达现有 NOR4 链的逐实例降尺寸集合。这与项目已测的冻结 TT SPEF 上五轮、18 个固定动作的经典 LR 构成不同配置。保留同后端的完整原生提议为可验候选，当前只有源码结论。 [固定停止条件](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/rsz/src/policy/GlobalSizingPolicy.cc#L1007-L1022) · [原生候选过滤](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/rsz/src/Resizer.cc#L2120-L2158) · [已测经典 LR](evidence/tcad_external_baselines_20261125/REPORT.md#3-经典-5-轮冻结寄生拉格朗日松弛lr四设计同门实测与保护后端解耦对照)

TAPCO-G 提供布局后图时序传播、功耗评分及失败批次二分的直接相关工作。其时序收益按起点 TNS 绝对值归一，当前 40 ns 参考各角 TNS 均为零。移植前需先固定全零 TNS 的目标解释和功耗输入。公开论文与作者成果页尚未给出可直接固定的实现入口。 [TAPCO-G 原论文 §4](https://arxiv.org/html/2611.13931v1#S4) · [作者成果页](https://wqtang.com/)

2026-11-27 补查相关公开入口。LearnSize 训练使用 ICC2 的优化信息，LEGO-Size 使用商业 3 nm 库和工业设计；查阅的原论文未提供可用于当前池的推理入口。DPH-Sizer 作者成果页列出论文，未附代码或权重。ISPD 2026 官方可执行基线以布局估计寄生、理想时钟下的 `repair_design` 和 `repair_timing -setup` 生成提议，后续评价用全局布线寄生。可作为独立原生流程参照，逐实例配对和冻结布线后三角验收仍需单独接入。 [LearnSize 原论文](https://arxiv.org/abs/2403.08193) · [LEGO-Size 原论文](https://research.nvidia.com/labs/electronic-design-automation/papers/yichen_LEGO_ispd25.pdf) · [DPH-Sizer 作者成果页](https://jinoh-cho.github.io/#publications) · [ISPD 2026 固定基线脚本](https://github.com/ABKGroup/ISPD26-Contest/blob/f7b29d242fc7d441f3b4eadc556f40099ccca067/scripts/evaluation_baseline.tcl#L26-L50)

2026-11-27 核查两条公开学习实现的准入。ASP-DAC24 教程固定版本的 Nangate45 字典对冻结池 18 项无目标可绑定，原名称解析器对 36 个源与目标名均报错。换字典后，冻结 SKY130HD TT 库中仍有两项跨越相邻驱动档，教程单步动作最多覆盖 16/18。公开入口初始化网络后训练，未找到可固定的检查点。ResizerAgent 静态传输夹具将 18/18 个指定实例目标准确转换为 `replace_cell`，原执行器也接受池外目标和重复实例。完整作者流程以 post-CTS 和指定模型为入口。当前实验应保留精确候选池验证，并将同池排序与部分端点提议分别登记。以上为准入检查，未运行作者模型或测得物理结果。 [ASP-DAC24 训练入口](https://github.com/ASU-VDA-Lab/ASP-DAC24-Tutorial/blob/7d25bfab195d95d8f41a0df1567d98a8578aa788/session1/demo2_gate_sizing.py#L139-L190) · [相邻档动作](https://github.com/ASU-VDA-Lab/ASP-DAC24-Tutorial/blob/7d25bfab195d95d8f41a0df1567d98a8578aa788/session1/demo2_gate_sizing_helpers.py#L258-L297) · [ResizerAgent 条件](https://github.com/ASU-VDA-Lab/ResizerAgent/blob/ae402b9bf00b5116b9f2743b3bd8f7c9aed52127/README.md#L3-L15) · [动作执行器](https://github.com/ASU-VDA-Lab/ResizerAgent/blob/ae402b9bf00b5116b9f2743b3bd8f7c9aed52127/scripts/python/executor.py#L345-L373)

上轮 40 ns 隔离在线原件复算得到 20 次原位预检（13 个唯一提议）均为零。独立首轮 DRC 在 19 次已完成检查中检出 5 次，涉及 3 个唯一提议，另一次在 DRT 截停。两次复修均清除标记，最终仍受 SS 相对 Hold 拒收。该处理器观察对应同一窗口后端，提前诊断的跨设计净收益仍需同提议干预。此前 GCD 的常规与全块在线 ABBA 提供后生冲突对照，四臂仍需复修且均止于 TT 相对 Hold 拒收。 [处理器原件复算](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#重建参考后的三臂在线搜索) · [GCD 配对原件](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_REPORT.md)

AES 现行在线后端已完成正反序原序单门对照和独立的后端交叉对照。同端点的诊断收益成立于 AES，候选调度的回收收益仍混合批宽、失败处理和排序。ASAP7 UART 已在原约束下完成三法正反序，在线固定、单门、FAECO 两序各回收 0.23328、0.17496、0.14580 µm²。UART 实际 36 次在线诊断均无 marker 或重试，因此仍需在出现诊断事件的独立设计估算净收益。下一层包括同后端灵敏度单门、固定批宽、同数量几何邻网放行和独立 SKY130HD 非 AES 设计，保留零回收和时窗删失。中英文工作稿均补至已核验的 UART 结果。[TCAD 成熟度评估](../paper/zh/review_rounds/r20261125_tcad_readiness/REVIEW_REPORT.md) · [UART 六臂](evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md)

2026-11-25 已在 AES 独立复核 TT 裕量灵敏度单门四臂。相较此前原序配对，新配对里 FAECO 首达领先缩小至 17.117／20.151 RAW s，窗内比较变为 67.5648 对 33.7824 µm²。静态灵敏度排序基线已补，仍需比较固定批宽、在线更新排序、邻网释放及独立设计。[灵敏度单门配对](evidence/tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_REPORT.md)

UART 去重两次同预算达到 0.20412 µm²，既有固定四门为 0.23328 µm²。实验优先顺序下先在冻结起点复测累计三门 `_0814_`／`_0886_`／`_1027_` 的可行性。预计面积与固定四门相同。该候选来自已读历史轨迹，保留事后定向诊断身份；自动调度达到该目标需要另做预设规则和同预算比较。[去重四臂](evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)

定向三门实际通过原门，回收 0.23328 µm²。原 FAECO 曾在首批尝试包含 `_0886_` 的三门，因 SS 相对 hold 失败，随后未在原合格两门上试到这项附加动作。目前已确认存在同面积可行端点，有限配额怎样分给延后候选、能否在不同设计复现收益仍待预设对照。[三门物理核验](evidence/tcad_holdout_20261123/UART_FIXED_AREA_PROBE_VERIFIED.json)

新鲜六臂表明用现有预估面积和单位电容优先级为延后候选预留末次并未改善 UART 回收。去重两序为 0.20412 µm²，固定 0.23328，预留 0.14580。预留末次两次均选面积同分但电容优先级更高的 `_0562_`，累计组合只因 SS 相对 hold −0.008424 ps 拒。仍需在统一信息成本下验证能够区分好坏的派发反馈，SS 的物理归因另做。[预留六臂](evidence/tcad_holdout_20261123/UART_DEFERRED_RESERVATION_REPORT.md)

同两门参考的七组网表与 SS SPEF 交换已实跑。两候选只换网表的 WNS 变化为 0，换各自真实 SPEF 分别精确重现其相对两门的 −0.015806800、+0.001484923 ps。七组保持同一路径和寄生注释计数。当前这一个案例的分歧由 SPEF 重现，冻结两门寄生未给出可行性区分。低成本几何或寄生风险分数须与现行去重、固定批次按同预算硬门实测，原时序门继续保留。[交换试验原件](evidence/tcad_holdout_20261123/UART_HOLD_EXCHANGE_RESULTS.json)

布线前时钟几何分通过 UART 开发判据，同面积末次只读重放能指向旧定向合格的 `_0886_`。固定公式转移至 GCD 历史同流程的九个候选后，TT／SS AUC 均为 0.75，但零分组有三过三拒，同面积的 `_091_` 拒与 `_093_` 过几何同分。电容后验破同分未提高等面积排序。先查明同分的物理来源，再确定是否有可部署的低成本区分办法，暂缓在线升级。[UART 与转移诊断](evidence/tcad_holdout_20261123/UART_HOLD_GEOMETRY_REPORT.md)

GCD 同分对八次 TT／SS STA 交换表明，仅更换候选实布 SPEF 即足以重现真实相对 hold 差异，单换候选网表效应为零。两点的实布产物均显示 `clk` 与 `clknet_0_clk` 的几何发生变化。与先前 UART 交换诊断相同的实验结论只覆盖这两个端点对。下一项门应核对能否用限域物理或增量寄生信息区分每次实际要选择的同前缀候选，测量净验证成本，并按统一预算保留拒收及零收益。[GCD 交换结果](evidence/tcad_ibex_20261123/GCD_HOLD_GEOMETRY_EXCHANGE.json)

GCD 同机换序的完整后端已复现同面积候选的原标签。dirty GRT 和直接网增量寄生均误收原拒收件，2 轮限域 DRT、去掉保护后的 0／2 轮均误拒合格件；后两种 DRT 预览也超出净费用门。正序已读出 `_093_` 后段的时钟几何与总 C 变化。进一步工作可检验复用同一路由状态、在实际布线过程中提取廉价中间反馈能否节约重复 DRT/RCX；本阶段继续用完整原门，未开方法同预算对照。[物理预筛诊断](evidence/tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)

同一 GCD 候选的两轮路由检查点续跑已完成从头、同进程和新进程的正反序核对。同进程四次续跑未完成可验收链；新进程 `_091_` 两次从 TT／SS 相对 hold 拒收转为合格，回收 11.2608 µm²，且两序分别多用 2.082／2.097 RAW s。原速度主张未过此轮放行门。后续待检查换设计后能否在完整布线拒收且池内缺等面积合格端点时按原门触发，比较相对从头重试的追加成本、获救率和合格回收。[检查点报告](evidence/tcad_ibex_20261123/GCD_LOCAL_ROUTE_REENTRY_REPORT.md)

按冻结候选规则已对 GCD 与 UART 试验四项检查点补救，本轮原后端从头均再现纯 hold 拒收。UART 三门有两次同一合格新物理端点，前沿由 0.23328 增至 0.26244 µm²；GCD 三门和 UART 两个六门均未获救。两段补救四项触发共追加 146.591 RAW s，其中成功项 38.101 s。对 UART 三项已确认与两轮检查点完全等同的原拒收 ODB 直接重入，三项均复现物理与门判定，合计少 8.729 s。生产采用前须以独立案例验证无需先跑两轮也能判定适用的触发条件、各角失败限制和净回收，并维持原完整验收。[补救试验报告](evidence/tcad_ibex_20261123/HOLD_REENTRY_RESCUE_REPORT.md)

两个固定 UART 六门的 TT 捕获叶与反馈窄域测试已完成。两级保线／清末级反馈均复现原几何和 TT／SS 拒因；主动清叶仅改变该叶，仍降低 TT／SS 裕量。加试累计成本超过全解锁，UART 既有 0.26244 µm² 前沿保持。试过的三种窄域规则未提供新的合格端点。后续若需定位修复杠杆，先以受控物理变化区分共享捕获叶与数据反馈的寄生贡献，再设同预算候选规则。独立设计上的触发有效性继续 open。[局部补救报告](evidence/tcad_ibex_20261123/UART_TT_CAPTURE_WINDOW_RESCUE_REPORT.md)

只读复核保留两项分别检查的门：逐角绝对 hold WNS 非负、相对冻结起点的 0.001 ps 容差。AES／Ibex 零编辑重布线已有 SS 回退，AES／GCD 代表点的 SPEF 交叉可重现回退。AES 同机换序可复现后端同点省时与 FAECO 对强单门的面积收益；固定先到共同小面积，Ibex FAECO 与固定同轨迹，UART 去重改善后仍低于固定。GCD 的已测低成本预筛误判，UART 继续限域追加验证成本增加而无净回收。现有结果按原门冻结，待明确相对 hold 余量应作为何种研究目标及当下验收边界。本轮无新增 EDA。[AES 归因](evidence/tcad_ibex_20261123/AES_REROUTE_HOLD_DIAGNOSTIC.md) · [AES 交叉对照](evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [GCD 预筛](evidence/tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md) · [UART 去重](evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)

UART 开发现已独验同后端 720 RAW s 纯墙钟八臂。现行去重 FAECO 两序均回收 0.83106 µm²，强单门 0.77274，固定 0.33534，交错 0.75816。共同实际回收 0.77274 µm² 到达时间中，现行两序早 105.569／103.522 s，预设的三档较小门槛均由单门先达。交错扩大了 hold 拒收代价，保留为开发负例。已按原门冻结留出仅比较现行、固定和灵敏度单门。[纯墙钟报告](evidence/tcad_wallclock_schedule_20261125/REPORT.md) · [UART 完整独验](evidence/tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json)

SKY130HD `riscv32i` 已完成原约束起点资格、筛选及 v2 六臂独验。ASAP7 `ethmac` 在原约束下恢复完成详细布线和 RCX，三角 hold 非负、hold TNS 零、SEC 52287/0。TT 的九处、SS 的 1,017 处 max slew 违规仍阻止起点资格，单列的独立 DRC／天线检查也因 45 s 限时未完成。没有候选物理评估或回收读数，不能把起点拒收计作算法零收益。若继续此设计，先在原 SDC 下闭合起点电气与独立 DRC。[Ethmac 原资格收据](evidence/tcad_wallclock_schedule_20261125/ETHMAC_CONTROL_INCOMPLETE.json)

原生 CTS、GRT 和最终报告只载入 FF Liberty。只读定位中，SS 的 990 个可绑定违规有 982 个 `NAND2x1` 受端，分布在该子集的 250 条网上，TT 的九处都来自三组 `NOR2x1` 到 `NAND2x1/A` 的扇出。后续保持原约束，先试多角电气修复调整实际驱动或网负载，再重新做 DRT／RCX、三角、独立 DRC／天线及 SEC。该诊断没有覆盖 SS 的所有违规，也没有生成可验收起点。[报告](evidence/tcad_wallclock_schedule_20261125/REPORT.md)

`riscv32i` 留出两序的灵敏度单门／固定／当前去重 FAECO 窗内最大值为 57.5552／52.5504／45.0432 µm²。当前去重在至少 45.0432 µm² 的后验共同量先到，但其最大合法回收最低。三次 setup 拒收花费 431–432 RAW s，未触发相对 hold 反馈。单项冻结 TT TNS 加和在两个已核组合误判方向相反；灵敏度排名的三门及六门累计集合在既有真实台账已经合格。下一轮应让固定和 FAECO 共享强单门的初始排名，再隔离批宽与反馈，继续使用完整物理预算。如本设计用于选择规则，另以新的独立设计验证。[SKY 六臂独验](evidence/tcad_wallclock_schedule_20261125/RISCV_WALLCLOCK_VERIFIED.json) · [后验前缀证据](evidence/tcad_wallclock_schedule_20261125/RISCV_RANKED_PREFIX_REPLAY.json)

补查 `riscv32i` 后，现行主要差距落在冻结起序及后续组合；每臂一次 setup-only 去重已消除该重复。后端重试即使提前取消，两个顺序观察到的第 6 次剩余成本约 61 秒。优先按同灵敏度初序复跑三法，保持原验收并使用同排名固定识别反馈作用。若仍需限制重试，验证实际可修复对照，不用冻结单门 TNS 相加或带 DRC 的首次 WNS 作硬拒。18 项静态总上界低于原 0.25% 标记，此项另作覆盖读数。[只读归因](evidence/tcad_wallclock_schedule_20261125/REPORT.md#riscv32i-调度差距的只读归因)

同排名开发复跑已在原门及同 720 RAW s 完成六臂独验。固定三门和 FAECO 两序均为 75.072 µm²，强单门为 57.5552 µm²；固定与 FAECO 全部累计派发及九门物理端点相同，两序均无 hold 延后、二分或缓存复用。当前证据支持共享排序和批处理。在有实际调度分歧的独立设计上，仍需以同排名固定三门检验反馈是否能带来净回收或同实收省时。[两阶段证据](evidence/tcad_rank_alignment_20261125/REPORT.md#720-raw-s-完整比较)

投稿评估后，先在独立设计隔离在线 DRC 诊断的收益。同榜同批宽、同门和同墙钟比较常规标记重试、简单几何邻网放行与实际候选标记诊断，记录同端点用时和合格面积。外部基线先复查原生回收与 TritonSizer 兼容性，现有历史对照与对应口径继续保留。动态调度的独立收益仍在实际分叉样本上验证。[稿件证据与判定](evidence/tcad_publication_assessment_20261125/REPORT.md)

2026-11-26 新轮实测更新（多项子门闭合，跨设计冲突复现与动态分叉边界继续保留）：
1. **SKY130HD AES 几何邻网预放行消融闭合**：6 臂正反序实测证实 `geo_m1_k1`（等规模，召回 46.2%）与 `geo_m1_r0`（100% 召回但 3.19× 放行）在 720 s 内合格回收均归零（`0.0000` vs `online` `67.5648 µm²`），同一 Request 3 三门提议中两几何规则均因错放/多放保护网令 SS hold 暴跌 −10.482 ps，确立现场 DRC 最小释放集对相对 hold 合法性的因果作用。[几何消融报告](evidence/tcad_geo_neighbor_20261125/REPORT.md)
2. **四设计同口径外部基线、功耗与 TritonSizer 预检闭合**：SKY130HD AES / `riscv32i` 与 ASAP7 UART / AES 上 OpenROAD 原生 `repair_timing -recover_power 100` 合格回收全为 0.0000 µm²，四设计 FAECO 最优端点总/组合/漏电功耗三项均降；TritonSizer 实查归档于 2018-12-01（Tcl 8.4 + 闭源 `sizer.tbc` + 无 SKY130HD），不具同工具链接入条件。[外部基线报告](evidence/tcad_external_baselines_20261125/REPORT.md)
3. **7 nm 独立留出设计 `asap7/aes` 6 臂同排名验证完成**：批处理（`fixed_online` 与 `faeco_dedup`）均回收 0.612360 µm²，为强单门 0.204120 µm² 的 3.00×，同实收提前 220–252 RAW s（SEC 10,027/0，正反序逐字节复现）。但该独立设计前两批直接通过、未触发动态 hold 反馈（固定三门与 FAECO 同终点打平），且 16 次全块预诊断均 0 marker（均耗 44.02 s）。[7 nm 留出报告](evidence/tcad_asap7_aes_holdout_20261125/REPORT.md)
4. **`1.0 × H_row` 局部窗口化布线前 DRC 预检闭合全块预检扩展性瓶颈（2026-11-26）**：全部 14 组历史不重复批次验证原地零位移与 56/56（100%）零漏报；7 nm `asap7/aes` 6 臂正反序将单次预检从 38.11 s 压至 7.03 s（5.42×）、达 0.61236 µm² 提前 64.7–66.0 s 且 720 s 内跑完第 3 批捕获 `SS:hold_regression` 触发暂缓反馈（对同步窗口化强单门仍 2.00×）；130 nm `sky130hd/aes` 4 臂正反序将单次预检从 14.40 s 压至 3.33 s（4.32×）、共同 5 组请求释放邻网 100% 一致且 0 重试，两序均把第 5 批 9 门拉入 720 s 内通过全签核，合格面积由 67.5648 跃升至 **98.8448 µm²（+46.30%，占 18 项池 50.00%）**，功耗降 −0.0512%/−0.0710%/−0.0320%。**剩余诚实边界（留作论文明确界定，不阻断投稿）**：(a) 真实换门邻线 DRC 冲突收益目前由高冲突 SKY130HD AES 完整因果实证，两 7 nm 设计呈零冲突（已通过窗口化消除 44 s 时间税）；(b) 动态 hold 暂缓反馈在 `asap7/aes` 第 3 批及 SKY130HD AES 均实际触发，而在前两批无 hold 拒收的 `riscv32i` 与同排名固定批打平，论文如实定位为高 hold 风险场景的自适应保护与前沿重排机制。[窗口化报告](evidence/tcad_boxed_drc_20261126/REPORT.md)

V5 的同一 riscv32i RTL 独立重建 40 ns 三角电气合格参考已完成严格收敛三臂实验。固定三门和 FAECO 在同排序的第二批均因 DRC／天线拒收，固定跳过，FAECO 二分，后者没有 Hold 暂缓或 Setup 去重命中。终态固定 91.3376、单门 48.7968、FAECO 31.28 µm²，支持如实报告此非 Hold 冲突分叉的代价，不能外推到 Hold 反馈活跃的其它设计。强对照及跨设计机制边界持续保留。[完整收据](evidence/tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json)

## OI-106（2026-11-25，限定闭合）— 累计动作在二分后被重复物理验证

UART 正序 FAECO 的第 2 次累计三门因 FF setup 拒，二分后第 3 次先接受左支单门 `_1027_`，右支加上已接受动作使第 4 次再次评估三门 `_0814_`、`_0893_`、`_1027_`。两次同冻结起点的 ODB、DEF、网表、独立 DRC 与三角 STA 相同，SPEF 30,890 行仅 `*DATE` 不同。正式物理各耗 19.420／19.574 RAW s，重复占一个实际验证配额。反序进度的前缀也已派发两次该累计集合。待记录完整基线后，单独对试探身份去重进行回归和实物配对，保留原始轨迹及六次实际评价上限。[UART 实验](evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md)

完成 UART 原门、同预算新鲜 ABBA 四臂独立核验。去重范围限定同一臂内且已完整确定的 setup-only 拒收，两次各消除重复一次，新第 6 次物理评估通过并将合格面积从 0.14580 提至 0.20412 µm²。UART 上确认该缺陷和修复，跨设计的作用、默认启用的取舍及与固定批次的差距归 OI-105。[物理复跑报告](evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)

## OI-107（2026-11-25，open）— GCD 固定提议在布线前预检无标记但正式布线后出现短路

同一三门提议和冻结 GCD 起点，常规与首次实时在线的初轮 ODB 和独立 DRC 相同。布线前实测 0 marker，保护路由结束后独立检查发现 3 个 met1 Short，涉及 `net242`／`net266`。两臂放行同一个邻网后独立 DRC 清零，TT 相对 hold 仍退 0.022621 ps，按 0.001 ps 容差拒收。继续检查四臂复现、同数量几何邻网基线和保护约束来源。与此前同动作 11.2608 µm² 合格的历史链相比，本轮新增加载并读回 476 条 `FIXED` 线，也新增独立解锁 DRC。旧 endpoint 与本轮不能混列。[GCD 规约](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_PREFLIGHT.md)

四臂独立核验现已确认请求、重试、实际端点和 TT 拒因复现，保护模式下全为零回收。候选诊断漏报与最终 hold 拒因属于两个可查现象。下一步待用几何邻网基线和保护路由对照辨别重布来源，同时保留原 TT 判定口径。[正式报告](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_VERIFIED.json)

同提议三臂正式补入一行高窗口。窗口与全块预检均空，三个后置短路的位置完整落入 `_093_` 窗口。三个臂首轮和复修各自复现原 ABBA 端点，复修均只释放 `net242`，独立 DRC 清零后 TT Hold WNS 仍下降 0.022621 ps。窗口对照和检查阶段的证据已齐。等数量单网预放行也已补测。几何择一同距选到 `_073_`，仍需追加 `net242` 复修。事后已知 `net242` 臂首轮无标记，省去一次 DRT/RCX，两臂最终仍因 TT 相对 Hold 拒收。更广保护范围干预、独立设计上的诊断净收益仍待验证。 [单网预放行补证](evidence/tcad_ibex_20261123/GCD_GEOMETRY_RELEASE_REPORT.md) [三臂原件与复算](evidence/tcad_ibex_20261123/GCD_WINDOW_DIAGNOSIS_REPORT.md)

## OI-108（2026-11-26，open）— 原生整批动作的实例身份与保护后端可评估性

V5 Stage 2B 240 s 原收据中，SKY130HD 两设计因单次保护路由触及上限，ASAP7 两设计的部分原生动作落在冻结 runner 动作空间之外。中断批次的 master log 额外显示，两臂 SKY130HD AES 600 s 均在 120 项中遇到一个 `sa32_sr\[7\]$_DFF_P_` 查找失败，riscv32i 曾完成零动作预检；该遍未进已提交收据。先比对 OpenDB 与冻结网表的原始名字、Verilog 转义、master 和一一对应关系，确认是否是可修的名称映射；真正缺失的实例保留兼容性类别。600 s 物理跑通后再核原门及 SEC，按超时、动作不兼容和完整物理拒收分别解释。[原断点收据](evidence/tcad_v5_revision_20261126/V5_STEP2_DEDUP_NATIVE_VERIFIED.json) · [执行交接](HANDOFF_2026-11-26_V5_EXEC.md)

已查中断批次 `native_diffs.txt` 与冻结 SKY130HD AES `6_final.v`。OpenDB `sa32_sr\[7\]$_DFF_P_` 对应网表 `\sa32_sr[7]$_DFF_P_`，两者旧 master 均为 `sky130_fd_sc_hd__dfxtp_4`，原生目标为 `sky130_fd_sc_hd__dfxtp_1`。已有 `compare_ibex.canonical_odb_name` 可用于逻辑校验，OpenDB 物理调用仍需原始名字。

名称绑定已通过离线核验，AES 120/120 项匹配同一源 master，ASAP7 UART 的 16 条真缺保持。600 s 已续跑，物理可评估性等待四臂收据。[续跑记录](LOGS.md#log-20261126-12stage-2b-600-s-启动与后续阶段预审)

窗口诊断还有第二处同类名称绑定缺陷。600 s 首臂在原名 swap 与 241 条直连走线清除后，预检以逻辑名查实例包围盒，触发 OpenDB 查找失败，随后主动中断。该次产物保存在 attempt_z9jgzkfx。预检日志 SHA-256 80807baa2b14f86109f62238be5323557a66c5507896ea16653f7beb66294316。使用原名查 OpenDB、保留规范名匹配归属后，须以同一 120 项原生真实预检复核，方可恢复完整试验。

原名修复后，真实 120 项回放到达预检完成标志并生成 81 盒，仍被走线计数不变量拦截。多清除的 3 条网均由同一 DFF 引入，其中 clknet_leaf_3_clk 的 DEF 用途为 CLOCK。现行数据网保护协议保持时钟树冻结，完整提议应归 unsupported_protected_scope。新增只移除该 DFF 的 119 项投影，两臂同 600 s 路由与 840 s 评估上限，单列结果。回归诊断 SHA-256 e5e523080154b64f444772c5ef4f76159b6cc8a0af1c03f9923e0230f087a481。

600 s 的四个完整提议键已落盘。AES 两臂为完整提议的窗口保护作用域不兼容，riscv32i 两臂均为单次路由触及 600 s 上限，未得物理时序和 SEC 终态。119 项数据网投影两臂均已完成测试，实际结果为 600 s DRT 截停、无时序/SEC 终态。整批比较仍受动作空间与物理时限限制。[阶段报告](evidence/tcad_v5_revision_20261126/REPORT.md#3-stage-2b原生-recover_power-保护后端对照)

## OI-109（2026-11-26，限定闭合）— 万门级独立对照的资格门与共用后端缺失

只读核查接手版 `run_v5_step5_10k_timing_closed.py`。候选验收只有 DRC 计数和 FF/TT/SS 的 Setup/Hold WNS；三角 TNS、电气、天线、SEC 与真实网表面积未绑定。窗口 DRC 产物没有进入邻网归因与放行，固定批拒收后也会二分。子进程未按外层剩余时间裁剪，单次路由超时可让整阶段异常退出。需先用可核对的新 10 ns 起点接入共用保护后端、完整资格门、三臂同定义与硬窗，再接受结果为合格回收。独立起点的严格时序门应保留。[当前脚本](evidence/tcad_v5_revision_20261126/run_v5_step5_10k_timing_closed.py)

10 ns 独立起点构建已经完成。最终 SDC 覆盖 65 个非时钟输入与 99 个输出、延迟同为 2 ns，无独立物理与原生电气拒因。SS 的 Setup/Hold WNS 分别为 −22392.385/−126.299 ps，起点未达到严格三角门，候选臂未启。CONTROL SHA-256 b8522af55121f1fc0a4d2a66fc8900a6a92c9849373b40e2c7ba7faa8144e73a。原 SS 日志（SHA-256 73d87c051b82f344a9dfce904ef1d39e6f0882a9c405b90ab5bd3f179166460a）已支持只读归因。最差 Setup 为 instr[15] 进 PC 寄存器（−22.39 ns），I/O 组还报告 instr[20] 到 aluout[31]（−20.46 ns）。最小松弛违例属 reset 到 FF 的异步 removal（−0.1263 ns），普通 clk 组 Hold +2.17 ns。下一独立新建参考设计拟以 40 ns 和 TT/SS/FF 联合实现，保留两向 2 ns I/O 以覆盖原异步复位边界，显式 ABC 40000 ps，预留 Setup 0.50 ns、Hold 0.30 ns。替代参考已独立构建完成。CTS 与 GRT 日志确认三角库和 Setup/Hold 修复调用，65 输入/99 输出均完整 2 ns，最终全角 Setup/Hold WNS 非负且 TNS 均零，独立 DRC/天线和 SEC 模型自检通过。唯一资格拒因为 TT:absolute_electrical：_3804_/Y 同时触发最大转换时间和电容限制。控制点 SHA-256 8dd1d882e908cdcf40d50807755d6dc7501c840ebb99e18b9401d8320700c586，没有候选臂。原 TT 报告中该驱动为 sky130_fd_sc_hd__a2111oi_0，实际转换时间 1.481687427 ns 对应限制 1.462190032 ns，实际电容 0.022171792 pF 对应限制 0.021067001 pF。独立电气修复变体已排在 Stage 4 后等锁，约束与三角时序余量保持，原生全局布线增加电容和转换时间修复余量 15% 与 10%。新构建已通过全项资格，实际 GRT 日志显示显式电容/转换时间修复，三角电气报告为空、同一完整 SDC、全角时序非负且所有 TNS 为零、0 DRC/天线、参考 SEC 自检 4559/0。资格 SHA-256 ce7b57b58e1d9968ce07876fe36911293ca32d66de090c9b975eee478350d9d7。严格收敛及电气两类参考门已闭合，[DRV 资格入仓副本](evidence/tcad_v5_revision_20261126/V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json) 与 WSL 原件同字节。Stage 5 三臂已于同榜、同后端及同 720 s 外窗完成，收据 SHA-256 af4f0fb7fa91ec8ef48f4072938c5774f2a68850765502db8f654c36c3f0c98f，三臂的合格端点均满足绝对时序门。固定／单门／FAECO 的终态依次回收 91.3376／48.7968／31.28 µm²，方法优劣的适用边界归 OI-105。[入仓资格收据](evidence/tcad_v5_revision_20261126/V5_STEP5_TC40NS_MMMC_QUALIFICATION.json)[已保全资格收据](evidence/tcad_v5_revision_20261126/V5_STEP5_TC10NS_QUALIFICATION.json)

## OI-110（2026-11-26，限定闭合）— 多档 Setup 生效门与探针敏感性对照口径

接手版 Stage 3 尝试实例化未定义的 `compare_ibex.Gate`，`hasattr` 使 `runner.gate` 静默保留原 1% 设置。后端 `audit_timing` 直接使用该门，外层 `BudgetPolicy` 的更新不足以落实宽松档，并且每角 TNS 仍为 1% 档。应复用 `run_setup_budget_sweep.budget_gate` 并绑定周期及 per-view 门，防止 2% 被预拒或将 1% 的 TNS 结果混入其他档。[位置](evidence/tcad_v5_revision_20261126/run_v5_step3_multibudget_online.py)

Stage 4 接手版 0 s 导入 AUC 为硬编码正序四舍五入值。直接积分 [原检查点收据](evidence/tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) 得 SKY 正/反 19.368673/20.076147、ASAP7 正/反 0.254383/0.253990 µm²。0 s 导入须绑定取向；旧默认 $\tau$ 为 SKY 180 s、ASAP7 约 169.12 s。V4 与 V5 接手版 Hybrid 回退缓存全部已返回拒收，须在全族写作中与 UART 独立 Setup-only 消融区别，或以同一拒收规则新测成组对照。[V4 实现](evidence/tcad_v4_revision_20261126/run_v4_hybrid_faeco.py) · [Stage 4 接手脚本](evidence/tcad_v5_revision_20261126/run_v5_step4_probe_sensitivity.py)

两项实现问题已做离线回归。Stage 3 的小松弛反例令 1% 与 2% 物理门发生预期分叉，并确认较差 TNS 与误绑周期会拒绝。Stage 4 绑定原检查点、探针截止和冻结回退，并保留历史缓存策略口径。Stage 3 八臂实测与重读已完成，各档预算在物理后端生效。Stage 4 正预算新测已开始。实际比较源脚本确认历史 SKY 纯微批次六次派发上限且无拒收复用，ASAP7 纯微批次仅缓存完整 Setup/TNS 拒收；V5 统一回退缓存所有完成拒收、无请求上限。历史 0 s 与默认保留描述性比较。六条正预算新臂已齐。同协议双设计 0 s 新对照已完成，连同六正预算臂构成八个新执行。历史零探针仍作独立参照，最终收据 SHA-256 5a63f0adfc02a897f8e8fd6f18eea3a972eb635207164e427b23dadf0868299c。新 0 s 对照使纯微批次与正子预算探针可在当前配置内对照，单次执行的时间量未跨环境外推。

## OI-111（2026-11-26，open）— riscv32i 旧约束缺失输入延迟

原 ORFS designs/sky130hd/riscv32i/constraint.sdc 用 lappend $non_clock_inputs $input 拼接输入列表，变量名被先展开，non_clock_inputs 为空。实查旧 6 ns 起点 /home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/results/sky130hd/riscv32i/base/6_final.sdc（SHA-256 74524c0bcc0e07bb1a43609125b5f7bfd03250ac47715ea492a73fb067229d7b），含 0 条 set_input_delay、99 条 set_output_delay，物理与虚拟时钟均为 6 ns。先前的两侧同源约束核验仍可复查原实验的一致性，覆盖范围限于实际生成的约束。

Stage 5 的独立 10 ns ORFS 新构建使用 [all_inputs -no_clocks] 明确收集非时钟输入；导出后核对所有预期非时钟输入与输出的 2 ns 延迟、实际/虚拟时钟、独立三角时序及物理资格。若完整约束使 10 ns 起点无法闭合，保留实测失败分类和完整 I/O 约束；样本资格继续待解决。原 6 ns 数据保留其实际约束口径。[新实验登记](evidence/EXPERIMENT_REGISTRY.md#tcad-v5-revision-suite-续跑预登记)

同一次源路径核查发现旧 ORFS 将 SDC 的 ns 数值 6.0 直接传入以 ps 计的 ABC 目标。旧生成 clock_period.txt 为 6.0，原 Yosys 日志明确为 ABC -D 6.0。新独立构建将映射目标显式设为 10000 ps，并核验构建产物 clock_period.txt。该修正与完整 I/O 同为新起点的预登记条件。独立构建已启动，实际新 clock_period.txt 显示 10000；最终 10 ns SDC 已验证所有 65 个非时钟输入与 99 个输出均附 2 ns 延迟。旧约束与 ABC 问题在新构建的配置修正通过。独立严格时序收敛仍受 OI-109 的 SS Setup/Hold 失败限制。

## OI-112（2026-11-27，限定闭合）— Stage 5 阶段切换时的评价器输出根

共享零动作原件通过后，Stage 5 的第一臂切至 arms/single_boxed/attempt_01，前端 runner.output 已改变，底层 runner.eval.args.out 仍为 runner/attempt_01。窗口预检后，Evaluator.evaluate 以旧根对当前试验路径做 relative_to 计算失败。实际初臂原件与搜索协议已留，阶段进度没有完成臂。统一本臂前端与评价器输出根，并用真实冻结参考复验。实验身份包含驱动文件散列，修复后的筛选和零动作写到独立尝试；合格参考无需重建。共同 run_arm 入口单行对齐后，三种真实路径的离线回归通过，初次四标记按清单无损保全（SHA-256 2296c5fbf438477fef787630ec7f68ca348e57df3723134c74c39ae1bbca3d9e）。修复后重跑的 single_boxed/attempt_02 首个实际候选完成 DRT/RCX、三角 STA、独立 DRC/天线及 SEC，候选原件 SHA-256 08b11cbac5274a3e2c1fc323cb4da52f8984c89544ce9d68ea79b8554515ce92。路径实现闭合，三臂完整结果仍待。

后续三臂全部通过收据与终态复核，未再出现输出根错配。[Stage 5 最终收据](evidence/tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json)

## OI-113（2026-11-27，open）— TCAD 英文投稿与正式材料

13 页 V5 中文稿通过内部小修核验。图 1–2 的 Google Antigravity `generate_image` 工具身份已通过原始记录与裁切回算确认，中文致谢已更正。待作者确认完整英文转译及正式署名、通信作者、每位作者的 ORCID 和投稿声明，并在拟投英文包验收 IEEE 版式、修回篇幅与最终致谢。强外部对照及同后端准入仍见 OI-105/108，完整冻结物理重建仍需历史输入和工具路径映射。 [英文投稿入口](../paper/en/README.md) · [终版复审](../paper/zh/review_rounds/r20261127_v5_tcad/REREVIEW_FINAL.md) · [IEEE TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)

复现中已完成 R3-1 的已布线端点 STA 异址重放，也在同一 WSL 主机的隔离输入副本上重建 40 ns 参考、原首批合格项并复跑完整三臂。另一物理主机环境的完整执行及其他设计的异址物理复跑仍开放。 [V6 运行说明](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#从独立输入副本重建-40-ns-处理器参考)

V4 资源补证覆盖 40 ns 处理器的自然结束与时窗截停两臂，也补齐小 UART 与两项最大网数代表双 AES 的阶段资源。已核验进程树 CPU、scope 内存高水位、实际读档与返回时刻。跨设计稳定速度、重复方差和外层硬返回接口仍待验证。 [处理器 V4](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#40-ns-处理器配对复跑的进程树与下游读取) · [三项阶段资源](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#小-uart-与两项最大代表设计的阶段资源)

## OI-114（2026-11-27，闭合）— 近临界 STA 复验缺顶层运行时绑定

470.5 ps 补测首次已核输入身份，首个 FF 调用因 STA 包装器未收到 `FAECO_DESIGN_TOP` 退出，未产生可用 STA 读数。保留首次日志和协议。复用既有 `bind_runtime("uart", None)`，在新目录以同一输入复跑；六视图的日志和门槛决定全部复算一致。修复只影响调用，未改周期或验收规则。[补证报告](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md)

## OI-115（2026-11-27，SEC 链限定闭合）— 单次 SEC 截停后后代进程脱离墙钟窗

40 ns 处理器隔离复跑中，单门第 8 个请求的 SEC 包装器在剩余 1.717614 s 时被截停，未生成验收收据。内部 Yosys 的证明日志却在下一固定三门排序日志之后约 2.420 s 才停止写入，含 4559／0 完成末行。此请求保持超时和未验收。固定臂起序与该后代重叠，影响未量化。外层 RAW 运行器只杀候选包装器的进程组，旧内层 GNU timeout 默认将 Yosys 放进另一组。冻结运行保留原代码与原始账本。

假工具沿真实 SEC 和 RAW 运行入口可复现。当前共享 SEC 入口增加 `--foreground` 以保留外层进程组，已通过同一夹具。真实同网表短窗 A/B 与足窗证明通过。原版仍有后代和日志增长，修复版两次观察均零后代且字节稳定，足窗 SEC 4559/0。修复后同主机完整三臂复跑已通过。18 次共同完成请求及三臂终态重现。单门再次在第 8 次 SEC 触限，包装器结束后首个采样中同组三进程均已退出，随后进入固定三门。全轮 10,523 次采样中未见跨臂重叠。跨工具、跨负载的硬返回仍开放。[三臂修复验证](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#sec-修复后的完整三臂验证)[后置真实对照](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#sec-截停和后置修复验证) [超时执行入口](evidence/tcad_wallclock_schedule_20261125/raw_timed_process.py) · [SEC 启动器](evidence/tcad_ibex_20261123/prove_ibex.py) · [回归测试](../code/tests/test_tcad_sec_process_group.py)
