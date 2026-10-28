contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "关键比较缺少可补充的控制、输入配置对应关系或失败结果记录，或分析把依赖观测当独立样本，使主要结果尚不能核验；需补充记录、重分析或针对性复验后才能判断主要结论。"
block_class: repairable

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
trigger: "中心论证存在可定位的证据到结论跳步，例如由混杂比较作因果归因或将受限观察外推到未覆盖条件；通过补充辨别性证据或重建推理链仍有可能维持原研究命题。"
block_class: repairable

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

本席检查研究设计、实验族之间的可比性、方法可重建性、功能验证状态与证据到结论的对应关系。Calibration Status 为 NOT_CALIBRATED。未确认投稿目标，本报告不作目标契合判断。审查材料限本轮提供的论文内容、合同和本席预承诺；没有查阅项目实验原件或其他审稿席报告，因此以下结果核查属于论文内部核查。

目前的证据支持“所报告配置在若干公开电路上观察到理想线网 WNS 改善”这一描述。主要缺口在于：论文以加权割、覆盖割和有限验证预算下的效率作为核心方法贡献，但最醒目的定量比较来自明确未使用这两类割的另一运行器；核心运行结果又存在版本未固定和复跑漂移。补充辨别性对照并建立输入、程序与结果的对应关系，仍可能支持原来的候选探索研究命题，故 D1、D3 为 repairable。本席未发现必须替换中心命题的逻辑矛盾，也没有证明所有现有核心证据在原则上均不可辨识；不据混杂比较本身判为 fatal。

### S1: 区分测量、提交与最终功能证明

**Evidence Anchor**: equation: 式(3)接受谓词及方法“验证与接受”（manuscript_numbered.txt L371–383）

论文明确将候选的 WNS/TNS 接受谓词、可选 SPEF 门控与最终顺序 SEC 分开。这样的分层定义允许读者区分时序获益与功能证明，不把局部规则检查直接当作全网表等价证明。

### S2: 报告零收益和退化结果，并限制解释范围

**Evidence Anchor**: table: tab:s_boundary，结构候选能力边界（L665–688）

S 扩展实验同时报告逻辑深度下降、WNS 不变及下降，并将结论限定在当前窗口构造、重综合与映射流程。0/126 的改善和未能抽取窗口的电路均未被隐藏。该报告方式有利于区分代理指标与目标指标；126 个候选仍是嵌套于电路的观测，不能视为126个独立电路样本。

### S3: 物理后验比较保留全部八个实例

**Evidence Anchor**: table: tab:pr8，全局布线寄生估计后WNS对比（L627–648）

表中保留5个改善、1个持平和2个退化，并按每个条件自身的基线计算变化量。该设计比只报告理想线网成功候选的正向物理结果更容易核查；其结论适用于这些候选及所报告的物理估计流程。

### W1: 核心割机制与有限预算效率缺少对应的辨别性对照

**Severity**: Major
**Evidence Anchor**: absence: 主要贡献与候选空间排序消融 — expected 同一运行器、相同接受准则和新STA预算下的加权割及覆盖割控制比较; checked L144–149主要贡献、L398–419实验配置、L508–546策略对照说明与表注、L575–589反馈运行开销、L692–694结论
**Confidence**: 5，设计对照与方法归因

主要贡献将“由多特征加权割与关键路径覆盖割生成候选”与减少评估开销连接起来；但第一组消融明确不用这两类割，且混合臂比随机臂多 JOINT、保留 TNS 辅助接受，实际 STA 消耗亦不同。其1.07 ns与0.16 ns的比较可以描述这些历史策略配置，却不能验证核心割机制改善了有限预算下的搜索效率。第二组主要辨别 EMA 更新，其随机排序结果也未提供割机制开关对照。论文已承认此限制，但摘要、主要贡献和结论仍把这些证据串接为当前框架的效率依据。

最低补证方案是在当前同一运行器上固定输入、候选类型、接受准则和停止规则，比较有无加权割、有无覆盖割；在相同新 STA 检查点报告逐电路最佳收益及首次改善开销。检验排序贡献时应固定候选集合；检验候选空间贡献时应固定排序规则并报告各臂实际候选数量。保留随机种子逐项结果和零收益实例。无需以不匹配的外部工具比较替代这组内部辨别实验。该缺口需要新控制数据，但不要求改变“组织多类型候选空间”的研究问题。

### W2: 主要历史结果缺少可重建的程序与配置身份

**Severity**: Major
**Evidence Anchor**: text: 实验设置L402“代码 revision 未完整钉定”；同段“同配置重跑在部分电路出现结果漂移”；策略表注L546“各臂完整命令未全部归档”
**Confidence**: 5，复现身份与配置追踪

上述缺口同时涉及效率优先、统一跨测试集与历史策略配置。工具大版本和轮数不足以判断漂移来自程序、输入、库、约束还是随机状态；也无法确认当前方法定义与产生主要数字的实际程序一致。s382混合策略缺少逐候选台账进一步限制首次改善指标的完整性；作者正确留空，但其他终点值并未因此获得运行身份。

最低补证方案是为每个用于主要论证的实验族提供源代码固定版本、输入及库散列、完整命令、约束、种子、超时、停止条件、逐项结果与输出标识。能恢复的旧运行应依据原件恢复；无法恢复的数字应明确保持为历史描述，并用固定版本的同输入复验建立新的可审计主结果。对已发生的漂移先逐层归因，报告前后差异，不用一个重跑终点反向宣称旧版本已被恢复。这是身份和复现证据缺失，不是对数字真实性的指控。

### W3: 覆盖割、实例化与融合排序缺少可执行定义

**Severity**: Major
**Evidence Anchor**: absence: 方法的多源候选边界与融合排序 — expected 关键路径覆盖割构造规则及两类边界到候选和最终顺序的确定性映射; checked L233–240符号表、L264–281算法、L291–320候选生成与代价式、L385–389复杂度说明
**Confidence**: 4，算法可重建性检查

节点代价式给出了可核查的数学对象，但“覆盖时序关键门”“按割代价、路径覆盖和策略优先级排序”没有规定覆盖集合如何取得、覆盖割怎样求出、两类边界怎样生成R/G/B/JOINT、排序键的优先关系、归一化及并列处理。读者因而可能实现出不同的候选集合和顺序，而这两个量恰是主要贡献的研究对象。最大流复杂度也不能补足这些定义。

最低修订是增加覆盖割和候选实例化伪代码，给出关键路径提取数量与选择规则、边界到门/端口集合的映射、R/G/B/JOINT枚举及去重身份、融合顺序的完整键和确定性并列规则，并列明子锥划分和规模阈值。用一个小锥给出输入、边界、候选清单和最终顺序的可核查实例；补充材料中的相应实现须绑定到W2所要求的版本。这样才能检验实际程序是否实现论文算法。

### W4: b17的时序获益仍缺少完整的最终等价证明

**Severity**: Major
**Evidence Anchor**: text: 跨测试集评估L497“另有 1 个等价点未完成证明”
**Confidence**: 5，验证状态与效果指标对应

论文诚实区分了28/29个完全证明网表对与b17的未完成证明点，这是必要的；但b17的改善仍进入18/19及ITC-99均值等主要时序效果汇总。该点来自同函数尺寸替换，只能解释为何预期保持功能，不能替代最终网表的证明结果。这里的不确定性是验证未闭合，不能解释为发现功能不等价。

最低补证是完成该点的独立证明并说明单元模型、状态和复位假设以及证明命令；若暂时无法完成，应同时给出“全部测量实例”与“完全证明修改网表对”的配对效果汇总，让读者直接判断核心收益是否依赖该未闭合实例，并始终保留其未证明状态。现有表的SEC计数是良好起点，但不能由通过计数自动推出所有时序改善均已完成等价验证。该缺口可通过补证或明确的分层结果分析处理，不构成单项致命反证。

### 论文内部算术核查与边界

只读脚本methodology_scratch/arithmetic.py对印刷表格进行了精确分数核算，原始输出在methodology_scratch/arithmetic_rawlog.json。策略表四列按已印刷8行求均值分别为0.16125、0.53625、0.3975和1.07375 ns；按常用就近舍入到两位小数与0.16、0.54、0.40、1.07相符。这是对已舍入表内行的汇总核查，不能验证未显示的小数或原始STA结果。F4的2434/4044为60.1879327%，与60.2%的显示相容。默认与放宽时限的评估计数满足4044−785+104=3363。首次改善表确有6/7个可比较电路的混合值小于随机三种子均值，最大种子比为7。物理表各行差值与5/1/2分类一致，S结果的0+36+90=126亦相符。未据此发现算术错误。

论文未报告t/z/F/卡方检验、p值、自由度或SD，故不存在可套用相应三种有界程序的项目。连续WNS均值和一般比例内部核算不冒称GRIM检验。离散STA均值可尝试GRIM，但文稿没有明确舍入规则；以下逐项保留实际分数推导，并将正式可达性判定记为not_computable，避免把审稿人采用的就近舍入习惯当作作者明确声明。该边界不构成数值不符发现。

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: tab:runtime随机新STA行与表注（L587–589）
reported_inputs: N=3; discrete integer totals=2439,2476,2527; reported mean=2480.7; precision=0.1
assumptions: 三种子的电路合计取无权算术平均；计数为整数；舍入规则未声明。
derivation: 2439+2476+2527=7442; exact mean=7442/3=2480.6666666666667; truncation to one decimal and rounding to nearest need not yield the same display.
derived_value_or_range: exact mean=7442/3; formal reported-value rounding interval unavailable
comparison_rule: 不采用未声明的就近舍入或截断规则；精确均值可算，但正式GRIM显示可达性不判定。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR2
procedure_id: grim
evidence_anchor: table: tab:efficiency s27（L562）
reported_inputs: N=3; integer STA counts=3,3,1; reported mean=2.3; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (3+3+1)/3=7/3=2.3333333333333; a formal rounding interval is not licensed by an explicit rule.
derived_value_or_range: exact mean=7/3; formal rounding interval unavailable
comparison_rule: 不从小数位数自行指定舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR3
procedure_id: grim
evidence_anchor: table: tab:efficiency s382（L563）
reported_inputs: N=3; integer STA counts=6,3,8; reported mean=5.7; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (6+3+8)/3=17/3=5.6666666666667; truncation and rounding to nearest yield different first decimals.
derived_value_or_range: exact mean=17/3; formal rounding interval unavailable
comparison_rule: 不从已印刷均值倒推并假定作者的舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR4
procedure_id: grim
evidence_anchor: table: tab:efficiency s420（L564）
reported_inputs: N=3; integer STA counts=5,1,1; reported mean=2.3; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (5+1+1)/3=7/3=2.3333333333333; a formal rounding interval is not licensed by an explicit rule.
derived_value_or_range: exact mean=7/3; formal rounding interval unavailable
comparison_rule: 不从小数位数自行指定舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR5
procedure_id: grim
evidence_anchor: table: tab:efficiency s641（L565）
reported_inputs: N=3; integer STA counts=7,5,1; reported mean=4.3; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (7+5+1)/3=13/3=4.3333333333333; a formal rounding interval is not licensed by an explicit rule.
derived_value_or_range: exact mean=13/3; formal rounding interval unavailable
comparison_rule: 不从小数位数自行指定舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR6
procedure_id: grim
evidence_anchor: table: tab:efficiency s713（L566）
reported_inputs: N=3; integer STA counts=1,5,2; reported mean=2.7; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (1+5+2)/3=8/3=2.6666666666667; truncation and rounding to nearest yield different first decimals.
derived_value_or_range: exact mean=8/3; formal rounding interval unavailable
comparison_rule: 不从已印刷均值倒推并假定作者的舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR7
procedure_id: grim
evidence_anchor: table: tab:efficiency s820（L567）
reported_inputs: N=3; integer STA counts=1,3,1; reported mean=1.7; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (1+3+1)/3=5/3=1.6666666666667; truncation and rounding to nearest yield different first decimals.
derived_value_or_range: exact mean=5/3; formal rounding interval unavailable
comparison_rule: 不从已印刷均值倒推并假定作者的舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR8
procedure_id: grim
evidence_anchor: table: tab:efficiency s832（L568）
reported_inputs: N=3; integer STA counts=1,2,1; reported mean=1.3; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (1+2+1)/3=4/3=1.3333333333333; a formal rounding interval is not licensed by an explicit rule.
derived_value_or_range: exact mean=4/3; formal rounding interval unavailable
comparison_rule: 不从小数位数自行指定舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR9
procedure_id: grim
evidence_anchor: table: tab:efficiency s953（L569）
reported_inputs: N=3; integer STA counts=3,1,1; reported mean=1.7; precision=0.1
assumptions: 表注明确三种子无权算术平均；舍入规则未声明。
derivation: (3+1+1)/3=5/3=1.6666666666667; truncation and rounding to nearest yield different first decimals.
derived_value_or_range: exact mean=5/3; formal rounding interval unavailable
comparison_rule: 不从已印刷均值倒推并假定作者的舍入算法。
status: not_computable
not_computable_reason: rounding_rule_ambiguous
