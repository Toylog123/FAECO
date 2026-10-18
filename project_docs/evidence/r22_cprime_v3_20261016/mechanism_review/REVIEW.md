# C′v3 代价机制独立归因：partial 四电路

**结论：当前四电路的权重确实进入了所建图的容量，求解器对该图求解正确；割不变可由根门单点割解释。不是“权重未生效”的实现证据，也不是代价有收益的证据。** 四电路、八配对、160条 weighted trace 全部重建成本/边界，并用独立 NetworkX mincut 复算一致；对应20个不同 circuit+base状态。重复轮不作独立样本，不外推其余四电路或完整72结果。

| 电路 | weighted trace数 | 不同base状态 | 选中根门 | weighted割成本 | 排除根门后的最优割 |
|---|---:|---:|---|---:|---|
| s27 | 40 | 3 | `_11_` | 2.181515 | 无有限合法node割：根有锥外输入G0 |
| s382 | 40 | 4 | `_073_` | 1.823560 | 无有限合法node割：根有锥外输入C3_Q3 |
| s420 | 40 | 7 | `_066_` | 0.791497 | `_064_`,`_065_`，2.968707；比根贵2.177211 |
| s641 | 40 | 6 | `_141_` | 1.652727 | 无有限合法node割：根有锥外输入G8 |

四例全部 selected-root singleton，没有利用tie解释零差异。s420 uniform根成本1，最优非root割成本2；weighted与uniform均严格偏好根。其余三例120条trace的根是任何有限割必选，所有其它节点成本为正，根singleton即唯一最小解。排除根门只用于结构可行性证书：该split边设为现有INF，其余容量不变；没有改变注册参数或生成新的科学实验结果。INF=1e9远大于这些图所有合法split容量总和；返回INF表示必须切受禁止的root/依赖边，不能当作有限替代候选。

## 数据结论的独立回查

实读原 `mechanism_audits/MATCHED_STATE_PAIRS_08.json`、16份配对outerloop_result及相应mapped输入；逐件SHA匹配原报告，所有对象before/after稳定。对每条weighted trace，比较**所有**相同base SHA的uniform轮，而非只取重复状态最后一轮：subcone cut-hash列表、ordered pool、dispatch均相同，uniform全部nodecost=1。weighted成本非均匀；两臂实际终点全文、hash相同。W0各例一个base、无提交；W1有多个base，但成本图/根选择的上述判据在各实际状态成立。没有用轮号相同代替状态相同。

从完整baseline及accepted chain全文按hash恢复每个实际base，使用actual Liberty output metadata解析正确top，按登记target_net重建fanin cone。四例trace均为一个未split锥；每个trace的节点集合、按实际effective weights/R_available重算的nodecost、production solver选门/割成本与trace逐项一致。另用NetworkX3.6.1的minimum_cut对相同容量图独立复算原最优值与root-excluded替代。独立算法复核的是**所建图**，不等同证明该图正是最适合局部ECO的目标。

`DIAGNOSTIC.json` 保存160条逐轮证书、替代边界、20个状态覆盖、全部输入/源码SHA及配对明细；此文只压缩呈现。命令经既有timeout包装180s，实际5s/exit0，无STA/Yosys/ABC调用、无参数/生产修改、HEAD保持3ea0f757。

## 可证伪的归因及设计含义

`_build_st_capacities` 对任何具有锥外输入的gate连接source→gate:in(INF)，对驱动boundary_outputs的gate连接gate:out→sink(INF)。单root有锥外输入时，存在source→root:in→root:out→sink的直接路径。任何分离**全锥所有源到sink**的有限node割都必须切root split边；上游更便宜的gate无法切断这条直接依赖。这同时解释s27/s382/s641里root并非全图最低nodecost却仍被选中。s420没有该直接路径，真正可替代的两门割存在，但其总成本在两种代价下均严格更高。

这与局部ECO合法区域是两种目标。局部区域可以保留尚未修改的输入作为区域boundary，由所有实际依赖及外部消费者闭合校验；它不必分离每条PI→endpoint路径。**不得简单删除真实source边以让mincut“产生区别”**：那会改变原图的分离语义并漏掉真实依赖。当前结果属于“正确求解一个常被根门支配的separator目标；该目标未在这些输入上提供额外动作机会”的设定层归因，不是solver实现bug。

以下任一证据会推翻/收窄本归因：同source/input pin重建成本或边界与trace不符；独立mincut得到更低有限容量；强制根案例缺少所称direct source path；s420发现成本低于root的合法非root separator；同base配对pool/dispatch并不相同。当前诊断逐项通过这些检验。它不能证明更大区域必有可接受ECO或时序收益，也不能由容量门控推断functional合法性。

## 若完整72仍无weight差异：最小后续设计评审（当前不执行）

1. 保持当前矩阵/pin不变完成并验收全部72。若八电路同状态cost控制全无cut/pool/action/终点差异，按预锁判据报告“该policy与该输入范围未观察到独立代价贡献”；非均匀nodecost、toy正控或数学能力不能改写真实负结果。分开报告cover/source与排序，不能用W1相对W0收益归因cost。
2. 先做无EDA的结构可辨识审查，复用现有 `constrained_weighted_cut_candidates`、`_cut_for_selected_gates`、boundary闭合与OI-030/旧R22 planning，**不另造搜索器**。冻结实际网表/critical列表/Lib及约束；并列保留singleton和全cover基线。对同一合法域，记录connected区域、hard anchors、min_critical_coverage、window_size、beam/evaluation limit、singleton开关的明确语义。约束须由所需ECO修改机会和真实critical覆盖说明，不能为“让weighted胜”任意禁根或调λ；约束新增就是新设计/新source pin。
3. 最先跑反驳控制：PI直达根、零输入source、单一合法区域、根不可编辑、无R但有G/B、multi-output外部消费者及helper同名均必须保留真实依赖；不存在第二合法区域时明确返回不可辨识，而非伪造多候选。现有constrained为bounded-beam区域生成器，不称精确k-best mincut；其排序/约束的实际路由必须先静态验证，不能把当前weighted_st负结果悄悄换成另一对象。
4. 对实际保留网表先做全体、确定性结构census，预先按是否有直接根路径/多个合法区域分层，包含null strata；不要按事后WNS挑电路。以固定默认五权重和uniform对**相同可行区域集**排序，先检验能否改变合法候选/动作身份。toy仅作实现正负控，actual网络没有辨别力就先评审目标与约束，不启动无辨别力大矩阵。
5. 只有actual静态门确认至少两个不同、F1/F2闭合且可实例化的区域、且默认configured/uniform的机会或次序可观察后，再预登记最小同base配对pilot。固定输入、候选全集/动作规则、cold cache、工具、预算及顺序；计候选/STA/commit分账、B_valid(k)/首次有效改善及final SEC。需要隔离“区域来源”和“排序”时用固定union candidate bank作静态重放/次序控制，不能用换池对照称纯排序效应。静态身份差异是开展pilot的可辨识条件，不是收益保证；真实负结果、硬门拒绝和no-improvement均保留。

## 仍未知与记录边界

本报告严格partial4；其余四电路未纳入，即使审查时已有更多job完成也不扩大样本。未分析所有72的合法收益曲线/完整动作身份轨迹、随机敏感性或机制性能；本次无新EDA。未证明root-excluded图割能产生完整合法ECO，未证明现有constrained函数在同域实际产生两个可用区域，亦未证明权重改变这些区域后的时序排序。上述都应由新设计评审/反例先行补验，不能倒填本轮。重复round不是独立统计样本。

先查复用依据：`docs/EXPERIENCE.md`的2026-10-14静态mincut/tie和2026-10-16同状态对齐；`OPEN_ISSUES.md` OI-030；`R22_ABLATION_DESIGN_REVIEW_20261014.md` P2/P6及归因顺序；`R22_CODE_REVIEW_20261014.md`；`R22_EVIDENCE_CLOSURE_PLAN_20261014.md`预锁零差异判据。新独立报告不覆盖这些旧文件。

归档 `diagnose_exact_invoked.py` 与实际调用的 `scratch/cprime_mechanism_review/diagnose.py` 字节相同。它保留原scratch相对根解析和独占输出，不宜从归档位置直接执行；需复跑时另复制新文件、明确适配根/新输出路径并另锁SHA，不覆盖此次诊断。
