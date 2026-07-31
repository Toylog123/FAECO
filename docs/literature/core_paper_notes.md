# FAECO 核心文献核验笔记

更新时间：2026-07-19

本文档记录前十批核心文献核验结果。每篇文献均区分书目信息、方法、可支撑表述和证据边界，避免只凭标题或摘要把相关工作写成实验依据。

## 1. 核验范围与方法

当前覆盖 25 篇 A 级全文证据，并核对首页、摘要、方法概述、结论、页数、DOI 和 SHA256；其中 DAC 2006 SAT sweeping 的正确全文来自 Cadence Labs 原始链接的 Common Crawl 归档，只保留在忽略提交的本机核验缓存。另有 1 条 B 级官方证据，即 DAC 2018 cost-aware multi-target rectification 的正式书目、摘要和竞赛问题规范；同时核对 ABC、Yosys、OpenSTA 的官方资料。

证据等级：

| 等级 | 定义 | 使用方式 |
|---|---|---|
| A | 本地全文已核验，书目信息与内容一致 | 可用于方法综述和边界明确的结果描述 |
| B | 官方或作者页面提供全文/摘要，书目信息可核验 | 可用于背景和方法定位，结果数字需回到全文 |
| C | 只有书目记录或本地文件错配 | 只记录来源，不用于方法细节或结果论证 |

## 2. Timing ECO 核心文献

### LIT-T01 ECO Timing Optimization Using Spare Cells and Technology Remapping

| 字段 | 内容 |
|---|---|
| 书目 | K.-H. Ho, Y.-P. Chen, J.-W. Fang, and Y.-W. Chang, IEEE TCAD, 29(5), 697-710, 2010 |
| DOI | [10.1109/TCAD.2010.2043573](https://doi.org/10.1109/TCAD.2010.2043573) |
| 本地证据 | 14 页；SHA256 `F3E6314741571F6489E376A78B018C959FC2A5E743EE0B238D66027F765064C8` |
| 等级 | A |

方法分为两阶段：先在动态 spare-cell wiring cost 下做 buffer insertion 和 gate sizing，再对第一阶段无法修复的路径执行 technology remapping。实验来自 5 个工业设计，并接入商业设计流。

可支撑：经典 post-mask timing ECO 不只依赖 B&G，逻辑 remapping 可作为后续修复手段。不能支撑：FAECO 在公开 benchmark 上优于该方法；其工业数据、spare-cell 和 metal-only 约束均未在当前项目复现。

### LIT-T02 TRECO: Dynamic Technology Remapping for Timing Engineering Change Orders

| 字段 | 内容 |
|---|---|
| 书目 | K.-H. Ho, J.-H. R. Jiang, and Y.-W. Chang, IEEE TCAD, 31(11), 1723-1733, 2012 |
| DOI | [10.1109/TCAD.2012.2201480](https://doi.org/10.1109/TCAD.2012.2201480) |
| 本地证据 | 11 页；SHA256 `F268FF88D680A94A4E464CB69BFEE6C210BC44B52125AA27DDBA77B953F33953` |
| 等级 | A |

TRECO 面向有限 spare cells 和动态 wiring cost，使用预计算 representative templates，迭代重映射 timing-critical subcircuits，直到不能继续消除违例。论文同样使用 5 个工业设计。

可支撑：动态 remapping 是 FAECO “重综合辅助局部替换”最接近的经典相关工作。不能支撑：TRECO 与当前 Stage A Python proxy 可直接公平对比；二者设计阶段、物理约束和验证链不同。

### LIT-T03 Comprehensive Search for ECO Rectification Using Symbolic Sampling

| 字段 | 内容 |
|---|---|
| 书目 | V. N. Kravets, N.-Z. Lee, and J.-H. R. Jiang, DAC 2019, Article 71, 1-6 |
| DOI | [10.1145/3316781.3317790](https://doi.org/10.1145/3316781.3317790) |
| 作者来源 | [IBM Research publication](https://research.ibm.com/publications/comprehensive-search-for-eco-rectification-using-symbolic-sampling) |
| 本地证据 | 7 页；SHA256 `69533889C3707257DF51927EFF452C40065035A3F68A989165A0F9FB73560596` |
| 等级 | A |

该工作面向 heavily optimized implementation 与 revised specification 结构差异较大的 functional ECO，使用 symbolic sampling 搜索 rectification points，并通过结构无关的 rewiring formulation 重用现有逻辑。论文报告工业微处理器 ECO，并与工业工具和 DeltaSyn 比较。

可支撑：ECO 搜索必须对结构差异鲁棒，rectification point 选择直接影响 patch 规模。不能支撑：该方法解决 timing ECO；其 timing 数据只作为 functional patch 对已布局设计的影响观察。

### LIT-T04 IR-Aware ECO Timing Optimization Using Reinforcement Learning

| 字段 | 内容 |
|---|---|
| 书目 | W. Jiang, V. A. Chhabria, and S. S. Sapatnekar, MLCAD 2024, 1-7 |
| DOI | [10.1145/3670474.3685945](https://doi.org/10.1145/3670474.3685945) |
| 作者全文 | [University of Minnesota PDF](https://people.ece.umn.edu/users/sachin/conf/mlcad24wj.pdf) |
| 本地证据 | 7 页；SHA256 `534C93E2411DB1B01801BCDD3C5B37497E6903EA4431FB9A76C47960F210A821` |
| 等级 | A |

论文在 physical design 和 power-grid synthesis 后处理 IR-drop-induced timing degradation，以 gate sizing 为动作，结合 Lagrangian relaxation、R-GCN 和 deep Q-learning。实验采用 open 45 nm technology，并讨论跨 timing specification 和跨设计迁移。

可支撑：近年的 timing ECO 已开始联合电源完整性、时序、功耗和最小扰动，并使用公开工具链。不能支撑：学习式 gate sizing 能替代 resynthesis-assisted logic patch，或当前 FAECO 已具备物理/IR 感知能力。

### LIT-T05 Timing ECO Optimization Via Bezier Curve Smoothing and Fixability Identification

| 字段 | 内容 |
|---|---|
| 书目 | H.-Y. Chang, I. H.-R. Jiang, and Y.-W. Chang, IEEE TCAD, 31(12), 1857-1866, 2012 |
| DOI | [10.1109/TCAD.2012.2209117](https://doi.org/10.1109/TCAD.2012.2209117) |
| 开放书目 | [NYCU institutional repository](https://ir.lib.nycu.edu.tw/items/6f729044-a318-4b3f-9ab2-5b68a8ec72c7) |
| 本地证据 | 10 页；SHA256 `FF19C10AB1810FCBC7A182D8F6C2BA1EE7208CD535366F867AC608F66418AA31` |
| 等级 | A |

论文针对 metal-only spare-cell timing ECO，提出 fixability 作为比单一 slack/delay 更丰富的修复优先级。该指标综合 flexibility、path sharing、spare-cell availability 和基于 Bezier 曲线的路径 smoothness；算法将违例路径分段，提取关键门，再用 minimum-weight perfect matching 选择 spare cells，并迭代至违例消除。

可支撑：候选修复点不能只按 slack 或单门 delay 排序，拓扑共享、资源可达性和物理几何会共同决定可修复性。不能支撑：FAECO 当前 `critical_path_only_cut` 已实现该 fixability；Stage A 尚无布局、真实 slack 或 spare-cell availability。

### LIT-T06 Timing ECO Optimization Using Metal-Configurable Gate-Array Spare Cells

| 字段 | 内容 |
|---|---|
| 书目 | H.-Y. Chang, I. H.-R. Jiang, and Y.-W. Chang, DAC 2012, 802-807 |
| DOI | [10.1145/2228360.2228505](https://doi.org/10.1145/2228360.2228505) |
| 开放书目 | [NTU Scholars publication](https://scholars.lib.ntu.edu.tw/entities/publication/8445c25b-4638-41ab-a692-8cc5b48df555) |
| 本地证据 | 6 页；SHA256 `7F83DB3621A0E82166304ECA531008E3D0C4078180742299802A704BB1908272` |
| 等级 | A |

论文把传统固定功能 spare cells 扩展为可通过金属层配置功能的 gate-array spare cells，以 aliveness 衡量 spare array 的可用能力，并用迭代 MILP 同时处理 aliveness、routability 和 timing safety。

可支撑：ECO 的可修复性受可用实现资源及其位置/连线约束限制，patch size 之外还需明确资源与物理扰动口径。不能支撑：FAECO 的 pre-mask resynthesis-assisted patch 与 metal-configurable spare-array flow 属于同一问题设置，或当前项目已建模 leakage、routing 和 metal-only 约束。

### LIT-T07 ECO Timing Optimization with Negotiation-Based Re-Routing and Logic Re-Structuring Using Spare Cells

| 字段 | 内容 |
|---|---|
| 书目 | X. Wei, W.-C. Tang, Y. Diao, and Y.-L. Wu, ASP-DAC 2012, 511-516 |
| DOI | [10.1109/ASPDAC.2012.6165006](https://doi.org/10.1109/ASPDAC.2012.6165006) |
| 书目来源 | [DBLP](https://dblp.org/rec/conf/aspdac/WeiTDW12) |
| 本地证据 | 6 页；SHA256 `03C22C4996321577C44DB5DB7CE7E925C5F5EEA6A911F27302820123C105BFBB` |
| 等级 | A |

论文把多条 ECO 违例路径上的 active/spare cells 视为共享且稀缺的 routing resources。`NEGO-ROUT` 先允许路径共享资源以获得 timing-optimal 但尚未合法化的解，再通过 congestion/history penalty 逐轮消除资源冲突；随后使用保持组合功能的 logic rewiring 扩大不同功能 spare cells 的替换空间，并在每次接受重构前用 STA 检查 TNS 是否改善。

论文在 MCNC/ITC 电路上注入相当于原路径延迟 10% 的负 slack，并以约 10% gates 作为 spare cells。相对 DCP，作者报告最终 TNS 为 DCP 的 50%、未解决 ECO paths 减少 31%，runtime 为 1.33 倍；logic restructuring 在 negotiation routing 之上平均再减少约 10% TNS。这些数字仅是原论文在其注入场景和 timing model 下的结果。

可支撑：多路径资源竞争需要迭代式冲突反馈，逻辑重构可在同功能 gate sizing 之外扩大候选空间。不能支撑：FAECO 当前 Stage A 权重更新已经复现 `NEGO-ROUT`，或原论文的 post-placement spare-cell flow 能直接证明 pre-mask FAECO 的 formal/timing closure。

## 3. Functional ECO 与协同修复

### LIT-F01 Simultaneous Functional and Timing ECO

| 字段 | 内容 |
|---|---|
| 书目 | H.-Y. Chang, I. H.-R. Jiang, and Y.-W. Chang, DAC 2011, 140-145 |
| DOI | [10.1145/2024724.2024757](https://doi.org/10.1145/2024724.2024757) |
| 本地证据 | 7 页；SHA256 `BE08B7E027BF362AB365E91CFB8360799B659AE9BABF2D9E8AB23A4AB65E5A2B` |
| 等级 | A |

论文以 augmented bipartite graph 同时建模 functional 和 timing ECO，并通过 constant insertion 与 bridging 扩大 spare-cell 实现能力。结果表明，顺序执行 functional/timing 修复可能留下违例，而联合求解可处理所给工业案例。

可支撑：功能正确性与时序目标不能默认独立，顺序拼接两个优化器可能失败。不能支撑：当前 FAECO 已实现 functional/timing simultaneous optimization；其 Stage A 仍只有结构 proxy 和逻辑级指标。

### LIT-F02 A Robust Functional ECO Engine by SAT Proof Minimization and Interpolation Techniques

| 字段 | 内容 |
|---|---|
| 书目 | B.-H. Wu, C.-J. Yang, C.-Y. Huang, and J.-H. R. Jiang, ICCAD 2010, 729-734 |
| DOI | [10.1109/ICCAD.2010.5654265](https://doi.org/10.1109/ICCAD.2010.5654265) |
| 作者全文 | [NTU PDF](https://alcom.ee.ntu.edu.tw/assets/publications/iccad10-eco.pdf) |
| 本地证据 | 6 页；SHA256 `0352DE8B732F250FE25B551DCC09BE79FE895CEAE2813862D31920468B9E5E55` |
| 等级 | A |

该工作先用 FRAIG 合并等价区域，再用 MUX-remodeled SAT proof minimization 处理简单修改；当 error-model 路径不足时，转向 incremental repair 和 interpolation 生成剩余 patch。

可支撑：ECO 搜索需要显式失败回退，简单快速路径和更完整但昂贵的验证/综合路径可组合。不能支撑：FAECO 的 F1-F5 refinement 已被该论文验证；二者失败分类、搜索对象和实验口径不同。

### LIT-F03 Efficient Computation of ECO Patch Functions

| 字段 | 内容 |
|---|---|
| 书目 | A. Q. Dao, N.-Z. Lee, L.-C. Chen, M. P.-H. Lin, J.-H. R. Jiang, A. Mishchenko, and R. K. Brayton, DAC 2018, Article 51, 1-6 |
| DOI | [10.1145/3195970.3196039](https://doi.org/10.1145/3195970.3196039) |
| 作者全文 | [UC Berkeley PDF](https://people.eecs.berkeley.edu/~alanmi/publications/2018/dac18_eco.pdf) |
| 本地证据 | 6 页；SHA256 `98A08DDA3643362C5F9848A1171B10D3A8CFED3087C4C8F562B5215C8F9AD062` |
| 等级 | A |

论文明确把 functional ECO 分为 target-signal 选择和 patch-function 计算，并只聚焦后者。方法通过 structural pruning 缩小窗口，以 SAT/QBF 判断 targets 和 supports 是否充分，计算 minimum-cost support，并用 cube enumeration 生成多输出 patch；SAT 超时时退回 primary-input structural patch。

可支撑：boundary/target 选择、support 选择、Boolean patch synthesis 和最终 equivalence verification 是不同子问题，论文叙事和 artifact 应分别报告。不能支撑：该工作直接解决 timing-aware boundary search，或 FAECO 当前 cone-level replacement 已实现 Boolean patch-function synthesis。

### LIT-F04 Resource-Aware Functional ECO Patch Generation

| 字段 | 内容 |
|---|---|
| 书目 | A.-C. Cheng, I. H.-R. Jiang, and J.-Y. Jou, DATE 2016, 1036-1041 |
| DOI | [10.3850/9783981537079_0946](https://doi.org/10.3850/9783981537079_0946) |
| 官方全文 | [DATE proceedings PDF](https://past.date-conference.com/proceedings-archive/2016/pdf/0946.pdf) |
| 本地证据 | 6 页；SHA256 `2E4764517A532CCF9F1B81AE3AC69523D5F4173939CC50E0853DA31A643474B9` |
| 等级 | A |

论文不把最小逻辑差异直接等同于最低实现代价。其流程迭代产生可修复同一 PO subset 的 strong partial-fix patch，以 area-complexity regression 或 AIG subject-graph core size 估计 gate count，再结合 nearby spare-cell search、virtual placement 和两类距离项估计映射后的 wiring cost，最后用 SAT/interpolation-based resubstitution 调整 supports 并减少资源需求。代价计算阶段并不执行 technology mapping，因此 wiring cost 明确是近似值；最终使用 ECOS 完成 metal-only mapping。

表 II 实际列出 8 个 industrial testcases，表 III 报告 resource-aware patch 的平均 AIG size 从 5 增至 6，但 resulting wiring cost 相对 minimal patch 平均降低 28.08%。论文摘要写“nine industrial testcases”，与正文表 II 的 8 行不一致，后续引用案例数时以表格为准并保留该差异。

可支撑：patch size 与物理实现代价可能相互冲突，ranking 应把资源可用性和估计 wiring cost 作为独立维度。不能支撑：FAECO 当前 `boundary_complexity` 或 Python score 已等价实现该论文的 spare-cell search、virtual placement、HPWL 和 technology mapping。

### LIT-F05 Unified Approach for Simultaneous Functional and Timing ECO

| 字段 | 内容 |
|---|---|
| 书目 | J.-H. Hung, Y.-C. Lin, W.-K. Cheng, and T.-M. Hsieh, IET Circuits, Devices & Systems, 10(6), 514-521, 2016 |
| DOI | [10.1049/iet-cds.2015.0395](https://doi.org/10.1049/iet-cds.2015.0395) |
| 出版方全文 | [Wiley/IET](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cds.2015.0395) |
| 本地证据 | 8 页；SHA256 `5850EABAE18EB81C068F063AE9679B552A77609FA6443B2BB5400249403B7B8D` |
| 等级 | A |

论文接收 placed/routed DEF、cell library、functional changes 和 timing constraints，以总 HPWL 为 ECO cost。其三阶段流程先用 detour reduction、buffer insertion 和 gate sizing 把 timing ECO 转成带 virtual nodes 的 functional ECO，再用 technology mapping 扩展候选，最后用 modified Hungarian matching 处理候选间互斥和 spare-resource competition；匹配后继续用 STA 驱动 refinement，去除连续冗余 buffers/inverters。

作者在 4 个 timing cases、5 个 functional cases 和 4 个 unified cases 上评估流程。表 VII 中 sequential functional-then-timing ECO 在 case1/case4 仍留下 1/10 条 timing violations，而 unified ECO 的 4 个 case 均记录 `#TP=0`、`#FC=0`，代价是部分 case runtime 略增。这些结果属于作者的工业 contest 数据和 timing model，且论文把 routing congestion 留作 future work。

可支撑：功能修复和 timing repair 会竞争同一批物理资源，顺序拼接优化器可能留下违例；统一搜索必须结合 STA、technology mapping 和资源互斥。不能支撑：FAECO 当前已实现 simultaneous functional/timing ECO、真实 STA refinement 或 placement/routing-aware matching。

### LIT-F06 Multi-Patch Generation for Multi-Error Logic Rectification by Interpolation with Cofactor Reduction

| 字段 | 内容 |
|---|---|
| 书目 | K.-F. Tang, P.-K. Huang, C.-N. Chou, and C.-Y. R. Huang, DATE 2012, 1567-1572 |
| DOI | [10.1109/DATE.2012.6176722](https://doi.org/10.1109/DATE.2012.6176722) |
| 官方全文 | [DATE proceedings PDF](https://past.date-conference.com/proceedings-archive/2017/pyear/PAPERS/2012/DATE12/PDFFILES/12.6_1.PDF) |
| 本地证据 | 6 页；SHA256 `DFAEF833C7954A081346ED76DC21CA36025BFFE92C88970526643F7A75477AD5` |
| 等级 | A |

论文定义 multi-error rectifiability 以及多修复函数存在的充要条件，将特定 2QBF 问题约化为 SAT，并从不可满足证明通过 interpolation 构造多个 patch function。`CofactorReduction` 不枚举全部 cofactor vector，而是迭代扩充足以完成修复的集合。完整流程先由组合等价检查器产生反例并反向传播，再执行带 cardinality 控制的 SAT diagnosis；若当前诊断点无法完成 rectification，则回到 diagnosis 重新搜索。

实现基于 ABC 和 MiniSAT，并用 ABC `cec` 检查正确性。ISCAS89/ITC99 时序电路在 sequential elements 处切开后按组合电路处理。相对作者 2011 年的 partial-fix 方法，表 2 中 patch-size ratio 平均为 0.11，runtime ratio 平均为 4.25；RTL 案例也显示补丁更小但部分运行更慢。图 2 表明 cofactor reduction 在大多数案例上降低运行时间。这些数字只属于论文的随机改错构造、诊断设置和工具版本。

可支撑：multi-error ECO 需要区分 diagnosis、patch-function synthesis、equivalence checking 和失败后重新诊断，较小 patch 可能以更高求解成本为代价。不能支撑：FAECO 当前 boundary/ranking 已生成 Boolean multi-patch，或切开时序元件后的组合验证等同于 sequential equivalence。

### LIT-F07 Intuitive ECO Synthesis for High Performance Circuits

| 字段 | 内容 |
|---|---|
| 书目 | H. Ren, R. Puri, L. Reddy, S. Krishnaswamy, C. Washburn, J. Earl, and J. Keinert, DATE 2013, 1002-1007 |
| DOI | [10.7873/DATE.2013.209](https://doi.org/10.7873/DATE.2013.209) |
| 作者来源 | [IBM Research publication](https://research.ibm.com/publications/intuitive-eco-synthesis-for-high-performance-circuits) |
| 官方全文 | [DATE proceedings PDF](https://past.date-conference.com/proceedings-archive/2013/PDFFILES/08.3_2.PDF) |
| 本地证据 | 6 页；SHA256 `DA7BA4C16FC197DB193C28000F0F15FE65485C6C0900EAB3CDBC7EDC809D9C38` |
| 等级 | A |

论文把 functional correspondence 定义为新旧网表中一组可直接替换、替换后使两网表等价的信号对，并用它形成逻辑修改的输出侧边界。方法通过名称保留综合生成候选对应点，结合等价检测和用户 hints，按拓扑顺序贪心构造有效 correspondence；随后把 correspondence 与 functional equivalence 之间的缩小子问题交给 Boolean matching，减少逻辑 delta。

工业 flow 将逻辑 delta 接入增量物理综合：固定未删除的原有门，只放置 ECO gates，再做电气修复、尺寸调整、缓冲和扩展区域优化。12 个 IBM microprocessor macros 上，表 1 的 INTUIT delta 总量为 223，对照 DeltaSyn 为 3746，即论文报告的 94% reduction；两者 runtime 接近，且 90% 以上耗时来自 synthesis。表 2 汇总显示 INTUIT 物理综合后的 WNS/TNS 相对 pre-ECO 改善 14%/46%，added gates 相对 DeltaSyn 减少 84%。扩大优化区域参数 `K` 可改善 QoR，但会增加新增/改动门数和后端扰动。

可支撑：可验证的功能对应点可以作为逻辑复用边界，逻辑 delta 大小会影响后续物理 ECO 的时序和扰动，QoR 与扰动需要共同报告。不能支撑：这些非公开 IBM 结果可直接复现，或 FAECO 当前 Stage A 已具备名称保留综合、真实物理综合、WNS/TNS 优化及 correspondence verification。

### LIT-F08 Cost-Aware Patch Generation for Multi-Target Function Rectification of Engineering Change Orders

| 字段 | 内容 |
|---|---|
| 书目 | H.-T. Zhang and J.-H. R. Jiang, DAC 2018, Article 96, 1-6 |
| DOI | IEEE [10.1109/DAC.2018.8465933](https://doi.org/10.1109/DAC.2018.8465933)；ACM [10.1145/3195970.3196017](https://doi.org/10.1145/3195970.3196017) |
| 书目来源 | [NTU Scholars](https://scholars.lib.ntu.edu.tw/entities/publication/29877740-e494-44bc-ae41-043cda52c011)、[NTU author publication list](https://www.ee.ntu.edu.tw/publist1.php?id=678)、[DBLP](https://dblp.org/rec/conf/dac/ZhangJ18) |
| 问题规范 | [ICCAD 2017 Resource-aware Patch Generation](https://www.iccad-contest.org/2017/Problem_A/default.html) |
| 全文状态 | 未找到合法公开全文或本地 PDF；OpenAlex 为 `closed`，Semantic Scholar 为 `CLOSED`，Crossref 仅返回 ACM 出版者入口；NTU 博士论文记录无公开 bitstream，2.76 MB 文件为受限访问且未授权公开 |
| 来源清单 | `source_manifests/cost_aware_multi_target_rectification_dac2018.json` |
| 等级 | B |

论文摘要将问题定位为：利用 SAT 与 interpolation，为多个指定 target points 同时生成 resource-aware patch，并宣称算法 sound and complete；实验与 ICCAD 2017 contest winning teams 比较。作者站点、机构仓储、开放获取 API 和 Internet Archive 资产索引复核均未发现目标全文。由于全文未公开，本项目不进一步写入其 rectifiability 判定、rebasing/base-selection 步骤、复杂度或逐案例数字。

竞赛官方规范可独立核验问题边界：输入给定旧电路 `F`、新电路 `G`、指定 target points 和旧电路内部节点权重；patch 可以使用 `F` 中的内部节点作为 supports/base nodes。首要资源代价是所用 support 权重之和，patch gate count 与 runtime 是后续独立排序项；多个 targets 仍由一个多输出 patch module 修复，并要求 patched `F'` 与 `G` 功能等价。这里的节点权重是竞赛提供的综合物理代价代理，不是 FAECO 实测的 placement、STA、power 或 area。

可支撑：multi-target patch 必须同时报告功能正确性、加权 support/resource cost、patch size 和 runtime，不能把最小边界或最少门数直接等同于最低实现代价。不能支撑：FAECO 当前已生成 Boolean multi-output patch、已复现该论文算法/结果，或 contest 权重可以替代真实 STA 和物理设计证据。

## 4. Equivalence 与 formal scaling

### LIT-V01 SAT Sweeping with Local Observability Don't-Cares

| 字段 | 内容 |
|---|---|
| 书目 | Q. Zhu, N. Kitchen, A. Kuehlmann, and A. L. Sangiovanni-Vincentelli, DAC 2006, 229-234 |
| DOI | [10.1145/1146909.1146970](https://doi.org/10.1145/1146909.1146970) |
| 书目来源 | [DBLP](https://dblp.org/rec/conf/dac/ZhuKKS06)、[UC Berkeley faculty page](https://www2.eecs.berkeley.edu/Faculty/Homepages/kuehlmann.html) |
| 正确全文 | Cadence Labs 原始 PDF 的 Common Crawl 归档核验副本；6 页，SHA256 `DA48ABD498D20FC7D69A411C4B1E81DB8847C4D2C22C3C21DCF97E4B272DFB42`；[ResearchGate author-uploaded full text](https://www.researchgate.net/publication/221059137_SAT_Sweeping_with_Local_Observability_Don%27t-Cares) 作为作者来源交叉核对 |
| 来源清单 | `source_manifests/sat_sweeping_local_odc_dac2006.json` |
| 等级 | A |

基础 SAT sweeping 在 AIG 上组合 structural hashing、simulation 和 SAT：simulation vector 先形成候选类，SAT 证明等价时合并节点，反例则继续细分类。论文进一步引入按路径长度 `k` 限定的 local observability，以保守 observability 计算处理 reconvergence，并使用 observability vectors、trie-based candidate lookup 和 level-order processing 控制候选搜索成本。

论文在 IWLS 2005/OpenCores 组合电路上比较 basic 与 ODC-based SAT sweeping，并报告较小 `k` 已取得主要额外合并收益，代价是中等 runtime 增长。该结果只能作为原论文方法表现，不能转写成 FAECO 实验结果。

可支撑：SAT sweeping 不只搜索全局功能等价节点，也可在输出不可观察差异的约束下增加局部合并，并为 equivalence checking 的 cutpoint/subproblem decomposition 提供方法动机。不能支撑：旧稿已复现该算法、ODC 可直接替代 patch formal equivalence，或当前 FAECO 已完成 SAT-sweeping 等价点搜索。

文献库内的同名 PDF **内容仍错误且禁止引用**：实际是 H. F. Dadgour、R. V. Joshi 和 K. Banerjee 的 *A Novel Variation-Aware Low-Power Keeper Architecture for Wide Fan-In Dynamic Gates*，DOI `10.1145/1146909.1147156`，SHA256 `DC27E10961218C0D47CB444238F0C9E3F94F9C29AFC3EE965A41B90BA22652B3`。原文件继续保留追溯，不改名、不覆盖。正确 SAT sweeping PDF 仅在 `tmp/pdfs/literature_b_to_a_batch10/` 下作本机核验，目录被 Git 忽略；版权页未授权服务器发布或再分发，因此不复制到仓库或发布包。

### LIT-V02 Toward Exhaustive Sequential Redundancy Removal

| 字段 | 内容 |
|---|---|
| 书目 | R. Dureja, J. Baumgartner, R. K. Gajavelly, R. Kanzelman, and K. Y. Rozier, FMCAD 2024, 217-226 |
| DOI | [10.34727/2024/isbn.978-3-85448-065-5_27](https://doi.org/10.34727/2024/isbn.978-3-85448-065-5_27) |
| 开放来源 | [TU Wien repository](https://repositum.tuwien.at/handle/20.500.12708/200794?mode=full)，CC BY 4.0 |
| 本地证据 | 10 页；SHA256 `B892260828D9A44F651588699EC3832E690004394CA3E7D9FE5634B81848417B` |
| 等级 | A |

论文通过 resource-sweeping、BMC/induction、counterexample simulation、speculative reduction 和 Proof Graph 提升 sequential redundancy removal 的可扩展性。它不是 timing ECO 算法，但说明 sequential equivalence/redundancy 验证需要显式处理 proof resource、反例和未收敛状态。

可支撑：FAECO Stage B 不能把 combinational structural signature 直接推广到 sequential equivalence。不能支撑：当前项目已具备 sequential formal 或论文中的规模能力。

### LIT-V03 A Semi-Tensor Product based Circuit Simulation for SAT-sweeping

| 字段 | 内容 |
|---|---|
| 书目 | H. Pan, R. Zhang, Y. Xia, L. Wang, F. Yang, X. Zeng, and Z. Chu, DATE 2024, 1-6 |
| DOI | [10.23919/DATE58400.2024.10546678](https://doi.org/10.23919/DATE58400.2024.10546678) |
| 官方全文 | [DATE proceedings PDF](https://date24.date-conference.com/proceedings-archive/2024/DATA/326_pdf_upload.pdf) |
| 本地证据 | 6 页；SHA256 `B02BFA84F523649955A9C5CC2426A8D0A6539E3EDFE5D7890E1886ABADA6ECC6` |
| 等级 | A |

论文为 k-LUT 网络构造基于 semi-tensor product 的矩阵仿真器，并将其嵌入 ABC `&fraig` SAT-sweeping。流程先用 SAT-guided initial simulation 和 constant substitution 缩小等价类，再把非候选区域映射为 k-LUT，只对候选等价类执行局部 exhaustive simulation；当局部窗口少于 16 个 leaf nodes 时枚举全部模式，并用 SAT 反例继续细化候选。STP 在这里负责 simulation/candidate filtering，不负责最终证明。

实现基于 ALSO、ABC `&fraig -x`，并用 `&cec` 检查结果。EPFL k-LUT 仿真实验中，作者报告相对 Mockturtle 的几何平均加速为 7.18 倍；HWMCC'15/IWLS'05 子集上，STP 版本的 simulation 时间约为 `&fraig` 的 1.99 倍，但 satisfiable SAT calls 降至 0.09、total SAT calls 降至 0.60，最终 total runtime 降至 0.65，即论文所述平均 35% reduction。两种引擎的结果 gate count 一致，实验在 Apple M1/8 GB 环境完成。

可支撑：SAT-sweeping 可以用更有表达力的局部穷举仿真减少错误等价候选和 SAT 调用，但 simulation、SAT merge proof 与最终 CEC 仍是不同证据层。不能支撑：FAECO 当前 structural signature 已实现 STP SAT-sweeping，或 STP 仿真可以替代 patch formal equivalence。

## 5. Buffering 与 Gate Sizing

### LIT-B01 O(mn) Time Algorithm for Optimal Buffer Insertion of Nets With m Sinks

| 字段 | 内容 |
|---|---|
| 书目 | Z. Li, Y. Zhou, and W. Shi, IEEE TCAD, 31(3), 437-441, 2012 |
| DOI | [10.1109/TCAD.2011.2174639](https://doi.org/10.1109/TCAD.2011.2174639) |
| 书目来源 | [DBLP journal record](https://dblp.org/rec/journals/tcad/LiZS12)；[ASP-DAC 2006 preliminary paper](https://www.cecs.uci.edu/~papers/aspdac06/pdf/p320_3C-4.pdf) |
| 本地证据 | 5 页；SHA256 `4DB532F8C32AF7AF25035552F3E3E5089668B1A606BABF667CD152C47CA37F04` |
| 本地文件名校正 | 文件名标为 `[2006]_[ASP-DAC]`，正文实际是增加作者 Y. Zhou、证明和 cost-minimization 扩展的 2012 IEEE TCAD 版本 |
| 等级 | A |

论文在给定 Steiner routing tree、候选 buffer positions、离散 buffer library 和 Elmore delay 模型下求 max-slack 最优 buffer insertion。核心数据结构在 `(Q,C)` 候选平面维护 convex hull，并用 linked list/pointers 把增加 wire 或 buffer 的更新摊还到 `O(1)`；two-pin 复杂度为 `O(b^2 n)`，扩展到 `m` sinks 后为 `O(b^2 n + bmn)`，另给出 buffer-cost minimization 扩展。

实验把所有算法用 C 重实现并采用相同 pruning。作者报告 two-pin 最多加速 20 倍、大型工业 multi-pin nets 最多 16 倍、1000-net max-slack 组最多 17 倍；各算法得到相同 slack。cost-minimization 工业网表来自 300k+ gates ASIC，平均提升较小，且 buffer type 较少时新数据结构可能略慢。这些结果证明给定模型下的算法效率，不是 ECO timing closure 结果。

可支撑：buffer insertion baseline 应明确 routing tree、buffer positions/library、delay model、优化目标和最优性口径；传统 B&G 能在固定拓扑上做强局部优化。不能支撑：buffer insertion 可以处理逻辑级数或功能改变，或该算法可直接作为当前无布局/无 Liberty 的 FAECO Stage A 可运行 baseline。

### LIT-B02 RL-Sizer: VLSI Gate Sizing for Timing Optimization using Deep Reinforcement Learning

| 字段 | 内容 |
|---|---|
| 书目 | Y.-C. Lu, S. Nath, V. Khandelwal, and S. K. Lim, DAC 2021, 733-738 |
| DOI | [10.1109/DAC18074.2021.9586138](https://doi.org/10.1109/DAC18074.2021.9586138) |
| 作者全文 | [Georgia Tech PDF](https://gtcad.gatech.edu/www/papers/dac21-3.pdf) |
| 本地证据 | 6 页；SHA256 `2EE0663AFC13EA44AE3470AFDFFBC10AD01B5C56E05D695C0F33995478ECB288` |
| 等级 | A |

论文把 post-route combinational gate sizing 建模为 MDP。state 由目标实例的 three-hop local graph、STA 特征和 technology-library 特征经 GNN 编码；action 是 driving-strength change；reward 是局部图 TNS 变化。DDPG actor/critic 按拓扑顺序处理从 worst path 与重叠负 slack paths 中选出的实例，每轮完成全部动作后才调用一次 full-chip STA，以控制 C++ EDA tool 与 Python RL 之间的通信成本。

作者把 RL-Sizer 集成到 Synopsys ICC2，在 6 个匿名商业 post-route designs、5/12/16 nm technology nodes 上从头训练。表 IV 中 RL-Sizer 在 4 个设计上获得更好的 TNS/NVE，在 2 个设计上不如 ICC2；运行时间为 5-22 小时，而 ICC2 为 10 分钟至 1 小时。block2 从 `TNS=-101.82 ns` 到 `-0.81 ns` 需要约 250 iterations/14 小时，前 13 iterations/不足 3 小时先到 `-2.18 ns`。论文明确承认缺少商业工具的局部 closure heuristics，部分可闭合设计会停滞。

可支撑：现代 gate-sizing baseline 需要真实 post-route netlist、library/technology features、full-chip STA、停止条件、runtime 与 PPA 共同报告；局部 reward 与全局 timing 之间存在近似和干扰。不能支撑：RL-Sizer 是 functional/timing ECO 算法，或其匿名商业结果可作为 FAECO 当前公开 benchmark 的直接 baseline；Stage A 的静态 timing-gain proxy 也不等价于该论文的 STA reward。

### LIT-B03 Learning-Driven Physically Aware Large-Scale Circuit Gate Sizing

| 字段 | 内容 |
|---|---|
| 书目 | Y. Ye, P. Xu, L. Ren, T. Chen, H. Yan, B. Yu, and L. Shi, IEEE TCAD, 44(5), 1901-1914, 2025 |
| DOI | [10.1109/TCAD.2024.3488577](https://doi.org/10.1109/TCAD.2024.3488577) |
| 作者全文 | [CUHK PDF](https://www.cse.cuhk.edu.hk/~byu/papers/J126-TCAD2025-LearnSize.pdf) |
| 本地证据 | 14 页；SHA256 `286744C81D0E60561DC8D24A44700958C4B4554D25A6CE190711D357D9D85439` |
| 等级 | A |

论文面向 post-routing gate sizing，把多个关键路径的 timing features、多个尺度的布局物理特征以及 ICC2 产生的优化信息联合编码为 multimodal timing model。PrimeTime 生成 gatewise TNS/WNS slack labels，ICC2 sizing 结果形成 gradient labels；优化阶段再通过 sizing-oriented straight-through estimator 处理离散 cell size，并用 Gumbel-Softmax 驱动的 adaptive back-propagation 优先更新 timing bottleneck gates。

作者在 TSMC 16-nm 上训练和测试 OpenCores 设计，并按设计规模划分 seen/unseen circuits。论文报告相对 ICC2 平均 `16.29%/18.61%` 的 TNS/WNS 改善和 `6.64x` speedup，训练本身使用 4 张 V100、约 4.5 小时和 128 GB 内存；消融结果支持 multipath timing、multiscale physical features、slack/gradient labels、STE 和 adaptive sampling 各自的作用。论文未给出实现仓库，且训练标签和 sign-off 评估依赖 Synopsys 工具与 TSMC 16-nm 环境，因此公开设计不等于公开可复现 flow。

可支撑：physically-aware sizing 需要把多路径 timing、布局拥塞/密度和离散 cell choices 联合建模，跨设计结果必须区分训练成本与推理/优化 runtime。不能支撑：FAECO 当前 Stage A 已具备真实 physical features、PrimeTime/ICC2 gradients 或同等跨设计泛化能力；论文结果也不能替代 FAECO 自身的公开 benchmark 和 STA 对比。

### LIT-B04 AiTO: Simultaneous Gate Sizing and Buffer Insertion for Timing Optimization with GNNs and RL

| 字段 | 内容 |
|---|---|
| 书目 | H. Wu, Z. Huang, X. Li, and W. Zhu, Integration, 98, Article 102211, 2024 |
| DOI | [10.1016/j.vlsi.2024.102211](https://doi.org/10.1016/j.vlsi.2024.102211) |
| 出版方页面 | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0167926024000750) |
| 本地证据 | 12 页；SHA256 `506B8958F9CF98B13C637423180863B1F6E4FDCDFEA3E7C9FB2B1D561EB6000F` |
| 等级 | A |

AiTO 面向 post-placement timing optimization，先从 WNS path 扩展 path graph，并在 FLUTE Steiner topology 上预选不会造成不可恢复 timing degradation 的 candidate buffer locations。已有 gate 的 action 是 driving-resistance change；candidate buffer 的 action 在“size 0 即不插入”和离散 buffer sizes 之间选择，因此 buffer insertion 被统一为特殊 gate sizing。GCN 编码两跳局部 timing/size state，DDPG actor-critic 决定动作，每轮处理完全部 candidate gates 后执行一次 full-chip STA，并用整轮 WNS 变化作为 reward。

论文在 10 个保密 real designs、28-nm/110-nm、约 28.8 万至 109.5 万 cells 上评估。作者报告相对 OpenROAD 平均 WNS/TNS 改善 `11.8%/14.0%`，平均 runtime 降低 `6.6%`，但 area/power 略增；消融中联合优化在 9/10 designs 上优于先 sizing 再 VGDP buffer insertion，`AiTO+Innovus` 相对直接 Innovus 平均再改善 `15.6%` WNS。论文公开的是 iEDA 平台代码，数据明确标为 confidential，未提供 AiTO 训练/推理仓库。

可支撑：sizing 与 buffering 会竞争同一 timing/capacitance 空间，联合 action space 可能优于串行拼接；候选 buffer 判断、STA 调用粒度和停止条件应进入 baseline protocol。不能支撑：AiTO 是逻辑重构或 functional ECO，或其保密数据、未公开模型可作为 FAECO 的可复现 baseline；当前 FAECO 也尚未实现联合 B&G。

### LIT-B05 Recursive Learning-Based Virtual Buffering for Analytical Global Placement

| 字段 | 内容 |
|---|---|
| 书目 | A. B. Kahng, Y. Liu, and Z. Wang, MLCAD 2025, 1-11 |
| DOI | [10.1109/MLCAD65511.2025.11189114](https://doi.org/10.1109/MLCAD65511.2025.11189114) |
| 开放来源 | [作者全文](https://vlsicad.ucsd.edu/Publications/Conferences/416/c416.pdf)、[arXiv:2506.17247](https://arxiv.org/abs/2506.17247)、[官方代码与数据](https://github.com/ABKGroup/MLBuf_MLCAD)，BSD-3-Clause |
| 本地证据 | arXiv v2 全文 10 页；SHA256 `EA377DA5BA8E0028D98805431A87D78C4DC91B4CD56F7D1CBCB0B6CDFD9DC645`；正式 MLCAD 书目为 11 页 |
| 本地文件名校正 | 文件名使用 `MLBuf RePlAce Virtual Buffering` 简写；正文正式标题为 *Recursive Learning-Based Virtual Buffering for Analytical Global Placement* |
| 等级 | A |

MLBuf 递归预测 buffer type、location 和 buffer-embedded tree，并通过 teacher forcing、ERC/wirelength/buffer-area global penalties 训练。MLBuf-RePlAce 把预测结果接入 OpenROAD/RePlAce 的 analytical global placement，在 placement bins 中预留 buffer porosity，再由后续标准 sizing、buffering、legalization、CTS 和 routing flow 完成设计。训练样本来自 OpenROAD `rsz` 生成的 trees，并保留 BP/MB 作为 unseen-design evaluation。

相对 OpenROAD 默认 TD-RePlAce，论文报告 OpenROAD flow 中 TNS 最大/平均改善 `56%/31%`，commercial completion flow 中为 `53%/28%`，后者平均 post-route power 改善 `0.2%`；large nets 的 tree prediction 报告超过 `3x` speedup，但该 runtime 假设 features 已提取。作者同时明确 MLBuf 主要处理 ERC、对 timing constraints 不敏感，极紧 timing 下收益会饱和。官方仓库提供训练数据、预训练模型、OpenROAD/ORFS integration branches、结果脚本和 BSD-3-Clause license。

可支撑：buffer porosity 和下游全流程评估会影响最终 timing/PPA，现代 buffering baseline 应区分算法 inference、placement integration 和 end-to-end runtime。不能支撑：MLBuf 是 post-route timing ECO 或 FAECO 的直接同问题 baseline；其结果更适合 related-work/discussion 和未来 placement-aware Stage B，而不是当前 Stage A 主表。

### LIT-B06 BUFFALO: PPA-Configurable, LLM-based Buffer Tree Generation via Group Relative Policy Optimization

| 字段 | 内容 |
|---|---|
| 书目 | H.-H. Hsiao, Y.-C. Lu, S. K. Lim, and H. Ren, ICCAD 2025, 1-9 |
| DOI | [10.1109/ICCAD66269.2025.11240744](https://doi.org/10.1109/ICCAD66269.2025.11240744) |
| 官方来源 | [NVIDIA EDA Research](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2025buffalo/)、[Georgia Tech author PDF](https://gtcad.gatech.edu/www/papers/Hsiao-ICCAD25.pdf)、[DBLP](https://dblp.org/rec/conf/iccad/HsiaoLLR25) |
| 本地证据 | 9 页；SHA256 `1C0395519489C464E06B1F48847F5F9776A752EDF8865F67656B32B60B33E8C4` |
| 本地文件名校正 | 文件名标为 `2024/arXiv`，正文实际是带 DOI 的 2025 ICCAD camera-ready IEEE 版本 |
| 来源清单 | `source_manifests/buffalo_iccad2025.json` |
| 等级 | A |

BUFFALO 将 buffer-tree topology、buffer size 和 placement 统一编码为 DFS bracketed full-tree sequence，并在 T5-Large encoder-decoder 上同时预测结构 tokens 与坐标。训练数据由 RTL net generator 和商业 buffering engine 生成，正文称超过 20M unbuffered/buffered pairs；先做 supervised fine-tuning，再使用 INSTA timing/gradient proxy 执行 net-level 与 chip-level GRPO。合法性通过结构规则、非法候选惩罚和 inference token masking 约束；full-chip 阶段只优化高 fanout 或 INSTA `netGrad` 选出的高影响 nets，其余 nets 仍交给商业 placement optimization。

实验使用 8 张 A100 GPU、AMD EPYC 7742 和 2 TB RAM；SFT 在 20M 数据上训练 6 天。full-chip 表覆盖 9 个 ASAP7 7-nm designs，并对照默认商业 buffering tool 和经相同 INSTA net-selection/downstream flow 增强的 OpenPhySyn academic baseline。Table IV 中最大 TNS/WNS 改善分别是 `71.10%/67.69%`，但 `pci_bridge32` 的 WNS 反而恶化 `21.15%`，功耗也有升有降。摘要写约 `71%` TNS 改善，结论写 `77.7%`，与 Table IV 不一致；`83x` speedup 来自代表性 50-sink 单网的 `0.5-1 s` 对 `30-43 s`，不是 9-design full-chip 平均 runtime。

官方论文页未给出 BUFFALO code/model/data repository，全文也没有 artifact availability 声明；公开的是作者 PDF和 academic baseline 使用的 OpenPhySyn，不是 BUFFALO 本体。可支撑：现代 buffering 可以用统一生成模型和 timing-guided RL 联合优化 topology/sizing/placement，且必须把训练成本、单网 inference、net selection、下游 commercial flow 和 full-chip PPA 分开报告。不能支撑：BUFFALO 可作为当前 FAECO 可运行 baseline，或其未公开 20M 数据、INSTA/商业 flow 和模型已可复现；它属于 post-placement physical buffering，不是 functional/timing ECO logic replacement。

## 6. ML 时序预测与泛化

### LIT-M01 Restructure-Tolerant Timing Prediction via Multimodal Fusion

| 字段 | 内容 |
|---|---|
| 书目 | Z. Wang, S. Liu, Y. Pu, S. Chen, T.-Y. Ho, and B. Yu, DAC 2023, 1-6 |
| DOI | [10.1109/DAC56929.2023.10247802](https://doi.org/10.1109/DAC56929.2023.10247802) |
| 官方来源 | [CUHK author PDF](https://www.cse.cuhk.edu.hk/~byu/papers/C167-DAC2023-PathPred.pdf)、[DBLP](https://dblp.org/rec/conf/dac/WangLPCHY23) |
| 本地证据 | 6 页；SHA256 `130DD9DA0C5E14004C6FD28B308623E775F94F117E332F1D44FEB7687ED1BECD`；与作者 PDF 完全一致 |
| 来源清单 | `source_manifests/restructure_tolerant_timing_dac2023.json` |
| 等级 | A |

论文针对 timing optimization 会重写网表、导致局部 net/cell 标签与输入结构错配的问题，改为直接预测 endpoint arrival time。方法把 netlist GNN embedding 与 endpoint mask 下的 layout CNN embedding 融合；数据由 Cadence Genus、edge-cut ASAP7 7-nm PDK 和 Innovus 的 placement/timing optimization/routing flow 生成。训练集与测试集各 5 个开源设计，Table I 显示测试集平均有 `43.7%` nets 和 `22.8%` cells 被替换，未替换 net/cell delay 仍平均变化 `63.9%/35.5%`。

Table II 的 5 个测试设计上，endpoint arrival-time 平均 R2 从 DAC19/DAC22 两类基线的 `0.4965/0.6207/0.6071` 提高到 GNN-only 的 `0.7958` 和完整模型的 `0.8724`；CNN-only 为 `-0.0283`，说明布局模态必须与网表信息结合。Table III 报告平均 `4154x`，但分母是商业工具的 timing optimization、routing 和 STA 总时间 `102654 s`，分子是图构建/关键区域预处理与 inference 总时间 `25.42 s`；论文同时说明相对完整 flow 的 arrival-time 结果约损失 `13%` R2。该数字不是同阶段 STA-vs-STA 加速，也不证明模型完成 timing closure 或可替代 sign-off STA。

正文和作者/机构页面未给项目仓库；精确标题仓库检索也未发现公开实现。源 RTL 可追溯不等于处理后的标签、模型、Cadence 脚本或 7-nm 实验环境可复现。可支撑：重综合/时序优化造成的结构变化会破坏局部监督，FAECO 后续 timing-aware ranking 应优先使用对边界变化稳健的全局路径/端点表示。不能支撑：FAECO 当前 Stage A 已具备真实 endpoint arrival-time predictor、7-nm physical features、STA 替代能力或同等跨设计结果。

### LIT-M02 Disentangle, Align and Generalize: Learning A Timing Predictor from Different Technology Nodes

| 字段 | 内容 |
|---|---|
| 书目 | X. Zhang, B. Zhu, F. Liu, Z. Wang, P. Xu, H. Xu, and B. Yu, DAC 2024, Article 133, 1-6 |
| DOI | [10.1145/3649329.3656251](https://doi.org/10.1145/3649329.3656251) |
| 官方来源 | [CUHK publication record](https://research.cuhk.edu.hk/en/publications/disentangle-align-and-generalize-learning-a-timing-predictor-from/)、[CUHK author PDF](https://www.cse.cuhk.edu.hk/~byu/papers/C225-DAC2024-AdaTimer.pdf) |
| 本地证据 | 6 页；SHA256 `1FA79D2EDEFB82431EEEDFA3E5098623A9A6F02A5BB65A76979186A9265EAC83`；与作者 PDF 完全一致 |
| 来源清单 | `source_manifests/cross_node_timing_dac2024.json` |
| 等级 | A |

论文在 LIT-M01 的 multimodal endpoint predictor 上研究 130-nm 到 7-nm 的 transfer learning。框架先把 timing path feature 拆成 node-dependent 与 design-dependent 表示，分别用 node-based contrastive loss 和 design-based discrepancy loss 对齐，再用 Bayesian readout 建模 arrival-time 变化。训练集由 4 个 130-nm Freecores 设计和 1 个 7-nm `smallboom` 组成，测试集是 `arm9/chacha/hwacha/or1200/sha3` 5 个 7-nm 设计；130-nm 标签使用 Cadence Genus、SkyWater PDK 和 Innovus，7-nm 数据沿用 LIT-M01 的处理流。

Table II 中，目标 7-nm 测试集平均 R2 为 `0.810`，高于仅用有限 7-nm 数据的 `0.396`、parameter sharing 的 `0.414` 和 pretrain-then-finetune 的 `0.575`；直接混合两节点数据为 `-3.407`。平均 inference runtime 从共同基线的 `4.982 s` 增至 `5.154 s`，约增加 `4%`。Table III 显示 130-nm 训练设计从 1 个增加到 4 个时，平均 R2 从 `0.507` 提升到 `0.810`，但这仍是特定 `130 nm -> 7 nm` 设置，且训练中使用了一个目标节点设计，并非零目标数据或任意节点泛化。

正文和作者/机构页面未给项目仓库；公开 Freecores、Chipyard 和 SkyWater PDK 不等于处理后的标签、7-nm technology data、模型及 Cadence flow 已公开。DAC 2024 会议论文与 2025 TCAD 扩展 *Pre-Routing Timing Prediction Across Different Technology Nodes* 必须分开引用，不能混合实验数字。可支撑：technology shift 与 design shift 需要分开建模，FAECO 后续跨 benchmark 学习不能只报告随机切分精度。不能支撑：FAECO 当前已具备跨 technology 泛化、无需目标节点数据，或论文的 inference runtime 等价于端到端 EDA runtime。

## 7. 工具链引用

| 工具 | 推荐引用 | 在 FAECO 中的角色 | 证据边界 |
|---|---|---|---|
| ABC | R. Brayton and A. Mishchenko, [ABC: An Academic Industrial-Strength Verification Tool](https://people.eecs.berkeley.edu/~alanmi/publications/2010/cav10_abc.pdf), CAV 2010, 24-40 | AIG optimization、CEC、SAT-based verification | 论文说明工具能力；FAECO 是否成功必须以本项目命令、日志和产物为准 |
| Yosys | C. Wolf and J. Glaser, [Yosys - A Free Verilog Synthesis Suite](https://yosyshq.net/yosys/files/yosys-austrochip2013.pdf), Austrochip 2013, 47-52 | Verilog 读取、规范化和 BLIF 输出 | 不能把 Yosys 可读取输入等同于前后网表功能等价 |
| OpenSTA | [OpenSTA official repository](https://github.com/The-OpenROAD-Project/OpenSTA) | Liberty/SDC/SPEF 驱动的静态时序分析 | 当前未安装，不能引用为已完成 STA 的证据 |

## 8. 对 FAECO 论文叙事的直接结论

1. 经典 timing ECO 主要处理 post-mask spare-cell、B&G 和 remapping；FAECO 应明确定位为 pre-mask、resynthesis-assisted local logic replacement，避免声称相同问题设置。
2. functional ECO 文献已经系统研究结构差异、rectification point、patch reuse 和 formal fallback；FAECO 的新意必须落在 timing-aware cut failure feedback，而不是泛称“使用重综合网表生成 patch”。
3. 2024 IR-aware ECO 表明现代工作重视真实物理信息、公开技术栈和多目标约束；FAECO Stage A 的 logic-level proxy 只能作为算法原型，最终论文仍需 Stage B STA。
4. equivalence checking 是独立的证据门槛。structural signature、工具可用、wrapper 状态和 formal pass 必须分开报告。
5. fixability 与 metal-configurable spare-cell 工作说明，真实 timing ECO 的候选质量依赖 slack、路径共享、资源可用性、几何和布线；Stage A 的 target-output proxy 只能是这些特征的占位入口。
6. 2018 patch-function 工作把 target selection 与 patch synthesis 明确拆开；FAECO 当前已实现的是 cut/ranking 和内部表示 replacement 原型，不能把它写成完整 Boolean patch-function 计算器。
7. multi-patch 工作进一步表明 diagnosis、Boolean patch synthesis、formal checking 和失败回退是不同阶段；FAECO 的 single-refinement proxy 不能借用该论文写成真实多轮恢复。
8. Intuitive ECO 的 functional correspondence 和工业物理综合结果支持“边界复用、逻辑扰动、时序 QoR 需要联动评估”，但不能替代 FAECO 自身的公开 benchmark 与 STA 证据。
9. DAC 2018 cost-aware multi-target rectification 与竞赛规范进一步区分 weighted support cost、patch gate count 和 runtime；其 B 级摘要/规范证据不能替代全文算法、复杂度或结果核验。
10. 最优 buffer insertion 依赖固定 routing tree、候选位置、buffer library 和 delay model；它是传统物理优化的强基线，但与改变逻辑结构的 resynthesis-assisted patch 不同。
11. RL-Sizer 说明现代 gate sizing 以真实 STA 和 technology features 为前提，并可能付出显著 runtime；FAECO 的 baseline 设计必须报告工具设置和停止条件，不能只比较一个 proxy score。
12. STP SAT-sweeping 通过仿真减少候选和 SAT calls，但最终仍调用 CEC；它强化了 formal 分层叙事，不会降低 FAECO 接入真实 ABC/SAT 验证的要求。
13. Physically-aware large-scale sizing 表明多路径 timing、multiscale layout 和离散梯度需要联合建模；公开 benchmark 名称不能替代公开 technology/library、标签生成和工具脚本。
14. AiTO 的联合 sizing/buffering 消融支持“资源共享动作应联合优化”的动机，但其保密数据和未公开 AiTO 实现只能进入相关工作，不能充当可复现主 baseline。
15. MLBuf 把虚拟缓冲闭合到 placement 和 post-route PPA，且代码数据公开；其问题阶段仍是 global placement/ERC-aware buffering，不是 post-route functional/timing ECO。
16. BUFFALO 展示了 full-tree LLM generation 与 INSTA-guided GRPO 的现代 physical-buffering 路线，但训练数据、模型和商业闭环未公开，且论文自身的 71%/77.7% TNS 表述不一致；它只进入 related-work/discussion，不进入当前可运行 baseline 表。
17. Restructure-tolerant timing prediction 证明 timing optimization 会替换大量 nets/cells 并改变未替换局部 delay；FAECO 若引入学习式 ranking，应优先按端点/路径和结构变化分组验证，不能把局部 proxy 当作 sign-off timing。
18. 130-nm 到 7-nm 的 transfer result 说明 technology shift 与 design shift 不能靠直接混合数据解决，但该方法仍需要目标节点训练设计和商业标签流；其 R2/inference runtime 只能进入 related-work，不能替代 FAECO 的 STA、formal 和端到端 runtime 证据。

## 9. 下一轮精读

| 优先级 | 任务 | 完成标准 |
|---|---|---|
| P1 | 定期复核 DAC 2018 cost-aware multi-target rectification 的合法全文 | 当前正式书目、摘要和竞赛规范证据为 B；多源 OA 检索已收敛，25A/1B 可进入初稿，取得合法全文后再补算法细节、复杂度和实验数字 |
