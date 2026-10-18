# 最小区域对照设计 contract（先登记静态规则，非实验注册）

本contract在census运行前冻结；仅四个已验收电路s27/s382/s420/s641的W0初始mapped与实际baseline critical。无EDA，不改production、当前C′注册参数或HEAD，不启动新正式实验。

复用现有constrained_weighted_cut_candidates，显式解析当前默认k5、beam40、最多320区域、window=全锥、min critical coverage1、无hard anchor、allow_singleton=false、无内部wall阈值；统一外层360s。configured为RefinementWeights默认五项1/physical1/maxcone1000，uniform只将五项置0，physical1保持。函数是bounded-beam生成器，不是精确k-best全枚举；不得因census无差异改变这些值或λ。

分别生成configured/uniform池，**只取一次规范hash union**，补入root singleton和full critical cover并保留origins。该union随后为两个排序共同使用的同一可行集；不能以原两池差异冒充纯排序。主排序明确选sum(actual nodecost)，uniform为门数，tie=canonical hash；这不是原constrained内部完整region_score复刻，也不混用它的position/physical等额外目标。原region_score只用于生成候选union，必须单独记录生成来源和偏置，后续正式设计需另评审。

静态eligibility逐项记录connected、所有真实dependency与外部consumer/multi-output闭合、critical覆盖、是否存在实际RGB可编辑witness。函数生成时不使用R_available筛区域；R可用性仅进入节点成本门控，不得删除仍可G/B的门。root singleton和full-cover无论是否eligible都保留记录，若同hash则合并origins。

动作静态复用已冻结ActualBackend的snapshot/candidates/apply/validate，不调用measure/sec。实例按baseline critical→剩余cone顺序，至多8；每实例每种R/G/B按原顺序最多尝试3个，buffer1/2。此界限是存在性witness搜索，不是完整候选穷尽；未找到不能宣称不可编辑。通过只称“确切候选全文已实例化并通过当前domain/F1/F2静态门”；不声称独立SEC、F3/F5、真实STA或可提交。保存action/candidate hash和失败原因；比较排名变化时同时比较静态witness集合，防止不同region实际机会相同。

反驳优先：先查同union不变量及无动作/仅一区域null；真实source direct-root依赖必须保留；多输出secondary consumer必须出现在区域边界；零输入source合法闭合；无R仍G/B不被删除。actual四例没有某结构时标未覆盖，独立小fixture只检验实现边界，不能升级为actual收益。两排名top1或全序均相同、或不同region却同witness集合，均是合法负诊断，不排除该电路、不调参。

若actual静态可行域没有多个候选或排序不可辨识，停在该诊断；若有，只能说明后续配对pilot有辨别机会，仍须设计审查、全部当前72验收、提交后fresh source pin、正式预算与真实SEC/STA正负控。新区域机制与当前separator机制分开，不补写当前矩阵为有效。详细参数、事前source/input SHA见CONTRACT.json。
