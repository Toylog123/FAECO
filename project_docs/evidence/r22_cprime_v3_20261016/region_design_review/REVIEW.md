# 新区域对照设计与静态 census（partial4；未登记实验）

**结果：复用当前区域生成器后，四个实际初始状态都存在多个不同、已实例化且通过当前domain/F1/F2静态门的区域；同一冻结union的node-cost排序在三例改变top-1及witness集合，s27 top-1不变。** 这只是新设计有静态辨别力，不是SEC、可提交性或时序收益。当前C′ separator负结果保持原结论，不因新设计能力而改写。

## 事前contract及复用口径

`CONTRACT.json`/`.md` 在census前保存，SHA60971de5…，声明时间早于census started_utc。只用已验收四电路W0的确切initial mapped、已归档baseline STA critical列表及原target；source46项/input17项前后SHA稳定，HEAD3ea0f757未变。没有扫描λ、超参数或不同起点，也没有改注册参数或production。

现有constrained_weighted_cut_candidates固定k5、beam40、最多320区域、window=实际全锥、无hard anchor、coverage1、allow_singleton=false（仅阻止生成器的endpoint单门，非禁止全部单门）。configured是默认五项1、physical1；uniform五项0、physical仍1。两次有界生成结果取一次规范union，补root singleton和full critical cover，origins合并。两个排序使用同一eligible hash集合；保留控制与null，不把生成池差异当纯排序。

主排序明确是**五项nodecost总和**（R_available覆盖全锥），uniform为门数，tie=canonical hash。它不是constrained内部完整region_score：后者额外含boundary、position、size/verification、physical启发式，只用于提案union。这个有偏、有限union是所声明的新对照对象，不是全体可行区域，也不是原L臂/当前C′ weighted_st的隐式替代。未来若实现，必须两臂共享同一次冻结union，不能各自动态改池而继续称纯排序。

## 四电路完整保留

| 电路 | 同union eligible区域 | 多门区域 | configured top-1 | uniform top-1 | uniform最优平局数 | top-1 witness集合 |
|---|---:|---:|---|---|---:|---|
| s27 | 6 | 3 | `_04_` | `_04_` | 3 | 相同：null保留 |
| s382 | 11 | 3 | `_070_` | `_063_` | 8 | 不同 |
| s420 | 10 | 2 | `_066_` | `_064_` | 8 | 不同 |
| s641 | 11 | 2 | `_138_` | `_075_` | 9 | 不同 |

总38区域、10多门区域，两个排序的全序在四例均不同，但所有top-1仍为singleton。configured最优分数各唯一；uniform差异依赖预声明的canonical hash平局规则，不是稳定性/统计显著性证据，也不说明configured更好。s641两模式均触320 evaluation上限，必须称有界census，不得声称该top-1是所有合法区域的全局最优。其它三例也只是函数返回top5后的union，不因预算未触顶就称全域穷举。

原根门source依赖保持原样，局部上游区域可以把真实入/出依赖作为boundary闭合。这解释为何之前separator必须切root与现在存在别的局部编辑区域并不矛盾；没有删source边。

## 静态可编辑性究竟验证了什么

动作复用冻结ActualBackend的candidates/apply/validate；只调用静态路径，subprocess.run在census期间被硬替换为抛错，外部调用0。实例按baseline critical→其余cone顺序、最多8；每实例每R/G/B按原顺序最多3个。共212个候选检查通过domain/F1/F2，确切全文写入`census_v2/*_witnesses/<sha>.v`并逐字节SHA回验。尚有230个proposal未检查；这是有界存在性witness，不能用未测候选证明不存在合法动作。

区域几何另独立核对connected、critical覆盖、真实输入driver、所有外部consumer、module-output/multi-output暴露边界；全部38都有至少一个确切编辑witness。该标签**不等于独立SEC、F3/F5、STA或搜索接受协议已过**；没有测量WNS/TNS、没有提交设计。不同region witness集合只是已测静态子集不同，未穷尽实际运行器完整RGB/JOINT动作机会。

无R仍G/B的实际正控覆盖2/7/6/10个实例（s27/s382/s420/s641）；它们没有被区域生成或eligible筛掉。四例这些区域实际multi-output gate数均0，故不能声称actual benchmark已覆盖多输出；另以actual Liberty全加器+secondary外部consumer做geometry正控，漏secondary边界的坏cut被独立oracle拒绝，断开COUT的坏网表被真实F1/F2拒绝。零输入conb两输出控制正确保留物理driver及边界。这些fixture仅支撑实现检查，不是实际网络时序贡献证据。

## 首次失败归因与保全

首轮实际四例静态检查完成后，conb控制暴露**本诊断oracle**的错误：它把已存在物理driver的module output先解析成1'b0/1'b1，导致合法physical ZERO/ONE边界被错误判不闭合。生产graph正确。`ORACLE_ATTRIBUTION.json`用最小输入实查确认；只修oracle的physical-driver优先，与原图语义一致，没有改约束/λ/输入。首轮脚本`census_v1_failed_exact.py`、日志与witness目录原件保留，`CENSUS_V1_FAILURE.json`记录失败，未把它称为成功。第二轮在独占census_v2目录运行，不覆盖首轮。

第二轮40.34s，wrapper360s实际45s/exit0；source/input/contract前后SHA不变。追加静态反驳控制日志单列，均无外部工具。源脚本确切字节归档为exact_invoked_*，保留原scratch根解析；不从归档位置直接执行，不覆盖结果。

## 最小后续设计评审与反驳验收（仅方案）

1. 将本次schema/区域目标/node-score口径与现有region_score差别先由root裁定；复用现有函数，不另造搜索器。不得将当前C′的全源separator悄悄换成局部region后补写为同一实验。当前72必须按原pin完成验收。
2. 静态前置门保留全部四例及s27 top-1 null；冻结共同union及完整实际动作生成规则/候选全文。witness首3只用于本census存在性，不能擅自成为正式搜索裁剪。验证无R但G/B、多输出、零输入、单一区域/无动作、同hash合并、helper作用域、源依赖不丢、预算及failed launch控制。无两个不同合法区域/实际动作机会时明确不可辨识，不调λ求正。
3. 若裁定继续，最小独立同base配对pilot可保留四个初始状态，比较同一冻结候选域的configured与uniform顺序；固定ties、预算/冷缓存、RGB/JOINT及所有硬门，分开proposal/STA/commit计数，保留正负/zero结果及独立终点SEC。需要机制隔离时固定union bank并确认action hash相同，仅次序变；同时记录全序差异是否真正到达新STA机会。不同pool/source对照另列，不冒称纯排序。
4. 预锁可推翻标准：排序无身份变化/实际动作集合相同；不同候选全被静态/接受门拒；真实B_valid(k)/首次改善/终点没有差异或变差。任何一种都可合法否定实用增量。toy或本次static差异不能转成时序有效声明；不得为了正结果排s27、改变320界限或权重。

新正式EDA、参数注册与生产实现均未执行/未授权。复用依据仍为OI-030、旧R22_ABLATION_DESIGN_REVIEW/closure plan与刚冻结mechanism_review；不外推八电路。
