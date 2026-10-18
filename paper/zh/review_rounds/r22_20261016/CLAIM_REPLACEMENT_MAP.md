# r22 中英论文主张回填交叉表

本报告只读当前稿件、生产源码与真实来源，新增本 MD/JSON；没有改稿、图、适配器或 HEAD，没有启动 EDA/编译。按 user-academic-writing-style 的证据纪律，先恢复实验与对象绑定，再同步主张。标为待证的项目不能只靠弱化措辞绕过。

审计快照以已冻结 `MATRIX_AUDIT_24.json` 为界：C′独立验收24/72，不把实时新增 completion 当独立验收。所有所引来源路径、逐文件 SHA/字节、确切 tex 行号、14表目录及计算结果保存在同名 JSON。运行期间文档可能更新，状态文件不作数值原始来源。

## 直接结论与回填顺序

1. **摘要/结论 1.07 vs 0.16 ns 仍依赖历史 C，不能回填为已恢复。** 纯G .16与B统一ISCAS均值同为.16不构成实验身份。C48目前只有84项mock QA；保留同pass/同实例evaluate-all/select-best、多提交及轮后JOINT，再真实运行/独立验收48项后重算。
2. **A功能对象已恢复，但旧SEC表不能原样留。** A6精确pair新证明加s27/s820确切B对象复用可更新功能绑定。s832新log是146/0，旧表145；六项耗时来自新证明，不得冒充旧错绑proof时间或同批运行。
3. **B17已补12879/0，不等全体可写29/29。** B2新模型2对通过；b09/b20/b21旧三态inv遗漏TE_B/enable的B3恢复尚未真实执行。受影响的18/19改善比例、.43均值、b20/b21最大增益及动作归因仍须同族有效终点。
4. **周期说明可立即准确修正。** 实际B Pico core5ns/mul2ns/regs.5ns；root另核全部187份保留TCL（26/160/1）一致。当前中英setup笼统全.5ns会误述图4与2/2收益依赖；新SEC不会改变当时约束。
5. **D结论不能由可复算曲线维持。** D40中38及k1 16中14结构invalid的原审计保留；56 CLI匹配不是科学复验。需D56正式同族重验后重填图5/runtime/EMA结论。C′不替代D。
6. **F4 60.2%不能直接升级成可靠失效原因结论。** 原19默认批次4044评估可重算；本轮state.failure_history未提供2434逐trial对应分类。即使补齐计数，旧F1误接受/错误模型还会影响“而非功能保持问题”的解释。须补分类映射与有效域审计，不能只删一句限定。

## 逐主张→原实验族→新证据→回填位置

| ID | 主张/位置（zh行；en行） | 原族→当前新证据 | 回填动作/门 |
|---|---|---|---|
| C01 | 摘要/贡献/总表严格改善比例<br>zh:94,113,149,435,436,437,439,445,477,497; en:30,59,259,260,261,300 | B → B_gain,B_model_audit,B2,B17,B3 | 数值可由B summary复算，但b09/b20/b21原实际Lib语义缺口未闭合；B3真实同族运行和finalSEC后重算相关gain/分母/均值，保留b06零改善和regs N/A。不得用C′各臂收益或QA数改写B比例。 |
| C02 | 摘要/结论1.07vs0.16ns<br>zh:94,113,512,544,692; en:30,310,333,432 | C → C_historical,C48 | 完成新C48同族重建的全部48独立验收后，以新run来源重算四列并同步中稿双语摘要、英稿摘要、两结论和表；保留未知旧argv/revision，不拿C′或B中恰好同为0.16的均值替代。 |
| C03 | A效率优先8/8功能保持<br>zh:445,461; en:267,274 | A → A6,A2 | A6恢复确切原mapped→accepted fixed；s27/s820保留确切B对象复用交叉表，可据此更新已恢复功能证据。不能沿用旧错绑gate的proof身份或把新proof当新STA。 |
| C04 | A SEC表点数/耗时<br>zh:445,461,474; en:267,274,283 | A → A6,A2 | 逐row换成真实receipt来源、点数及耗时：s832新log146/0而非145；其他六项见A6表。若保留两项复用proof，必须标明异源/异批次，不能拼成同一旧runtime。 |
| C05 | B17及统一SEC总数<br>zh:94,113,149,436,439,497; en:30,59,260,263,300 | B → B17,B2,B3,B_model_audit | 确切b17新proof12879/0可补其状态、模型/flatten/assert来源，旧partial留档。但B3三项尚缺实际Lib语义证据，禁止直接宣布全体29/29；先建立逐pair支持域状态，后更新总表。 |
| C06 | Pico 2/2与新模型SEC域<br>zh:94,113,139,149,398,400,437,439,493,495,497,504,541; en:30,50,59,236,238,261,297,298,331,446 | B → B_gain,B2,Pico_constraints | 收益保留其5ns/2ns当时约束；B2按完整新模型及孤立恒X证书（core7、mul0）回填功能证明，不能泛化任意X/Z、初始化/复位或四态等价。 |
| C07 | B3最大收益与接受动作归因<br>zh:487,704,715; en:293 | B → B_gain,B_model_audit,B3 | 旧clkinv→einvn遗漏TE_B/three_state使R动作不能当合法等价替换。完成B3保留真实策略与显式新参数的科学恢复后重算收益和动作构成；对其他B对象保留已审证据，不从三例外推全族无效。 |
| C08 | F1–F6分布与F4解释<br>zh:487,597,604,606,694; en:293,366,369,371,434 | B-default60s → B_default_failure_accounting,B_model_audit | 4044是含b17默认785评估的原配置；本次state.failure_history不能直接恢复表中2434映射，分子逐候选映射仍unknown。需补分类生成器/逐行交叉表并核旧F1误接受影响，必要时在原域重验；不把B3新族计数混进旧4044，也不只删除因果句掩盖实现缺口。 |
| C09 | 3363与2994计数边界<br>zh:487,606; en:293,371 | B-rerun180s → B_accounting,B17 | 保持记录数/可识别结果数单位及2890+104来源，不称实际完整工具启动数；b17 proof补齐不改候选运行计数。aggregate.py旧直接读main b17的终点为-16.53，当前summary为phase2 -16.15，回填/再生成必须显式保留该override。 |
| C10 | C策略表四列和首次改善开销<br>zh:510,512,521,528,544,553,571,589; en:308,310,318,322,333,339,351,362 | C → C_historical,C48 | 保留每pass固定关键实例、每实例evaluate-all/select-best即提交、多提交、轮后JOINT和mixed/random不对称。新C48需真实launch/commit分账后重算首次改善；旧s382 mixed canonical缺失不借sibling补值。 |
| C11 | D反馈、预算曲线与runtime<br>zh:349,514,516,522,578,586,694; en:200,312,314,318,355,359,362,434 | D → D40_raw,D56 | D40含38结构invalid，k1含14/16 invalid，原计数可复算不足以支持合法ECO的EMA零收益结论。D56同族五臂×8+k1两臂×8真实复验、最终SEC/计数验收后重画图5并重填表runtime；C′不能替代。 |
| C12 | 物理保持5/1/2<br>zh:540,612,618,619,630,641,694; en:330,375,379,389,396,434 | A/A_prime → A6,A2,physical_A_prime | 数字从A′两个audit可复算，继续按全局布线估计而非signoff表述；与A确切候选和baseline逐文件绑定，尤其s713原A与A′baseline非同SHA。A6补功能、不重做物理测量；不把C′理想网收益填进图6。 |
| C13 | S结构边界负结果<br>zh:469,472,474,475,589,654,656,661,662,668,675,676,677,678,679,688,709,714; en:77,278,281,283,284,293,362,407,411,415,418,419,420,421,422,428 | S-independent → S_raw | 本轮直接读聚合与8对delta复算；新A/B/C/D证明没有复核该批S候选独立SEC/完整commit合法性，不能把新工具通过倒签给旧S。保留单独族/来源，若需当前正确模型下的能力结论，先做独立S域/对象审计和必要复验；C′禁S不能提供替代。 |
| C14 | 双割/cost机制贡献<br>zh:94,97,113,115,137,145,191,220,237,251,271,287,295,297,328,510,512,692; en:30,33,48,55,124,141,156,163,308,310,432 | Cprime-new → Cprime | C旧关键实例运行器未用双割，不能由1.07ns推断其增益。C′目前仅冻结独立验收24/72；等全72后按注册对照、实际dispatch与真实STA成本检验机制，零收益/重合路径保留，不将正确性通过等同机制增益。 |
| C15 | 实验周期笼统全.5ns<br>zh:398,612; en:236,375 | B-Pico constraints → Pico_constraints | 直接改setup/overview/图4附近约束说明为ISCAS/ITC .5ns与Pico core5/mul2/regs.5ns；不用新SEC或不相同周期重跑为旧数字补身份。root已独立核187TCL(26/160/1)。 |
| C16 | SEC/三态支持域与方法前提<br>zh:128,139,149,161,170,207,218,220,258,281,372,445; en:50,59,63,70,102,216,267 | A/B/C/D all → A6,B2,B17,B_model_audit,production_support_domain | 普通inv与三态inv必须保data+enable，seq R排除并保状态语义，所有输出/required pins完整；实际tri/Z在当前Boolean final_sec是unsupported非pass。保留OI039，恢复需显式四态编码/经证明语义变换，不能只改声明或把writer产生Z说成四态证明。 |
| C17 | SPEF 40um/unit及50/6个F6<br>zh:512,624,661,688; en:310,382,384,386 | SPEF-independent → SPEF_unknown | 正文数字已定位，但本轮未定位完整逐候选接受/复测manifest，50/6的独立绑定标unknown；补确切scan/gate原件+候选输入与RC配置+前后合法性证据，不以C′关闭physical的结果替代。 |

## 图4–7真实来源

| 图 | 中英实际输入与原族 | 本轮实查/后续门 |
|---|---|---|
| 4 | `20260826_aggregation/summary.json`，B；三个数据集30实例，regs N/A | 8/8、18/19、2/2及均值.16125/.429473684/.600可从保留aggregate复算；B3语义/约束门未闭合，不是新科学验收。b17 aggregate明示phase2值，旧aggregate.py直接读默认main会退回-16.53，必须显式保留override。 |
| 5 | `20260924_threearm/{fixed,adaptive,random_s1,s2,s3}/{8c}/{outerloop_result,eval_trials,run_config}.json`，D | 实读120份来源，排前拒/cache的新测量数1947/2003/2439/2476/2527；数字可复算与ECO合法性分开。D56尚无EDA，待同族验收重画。 |
| 6 | `20260807_real_pr_iscas8/{pre_layout_audit_summary,post_route_audit_summary}.json`，A/A′ | 实读16明确counterpart，5正/1零/2负可复算；A6只补接受fixed功能。s713原A与A′baseline不同SHA，保留crosswalk；不能说新做了OpenROAD/signoff。 |
| 7 | `20260928_s_l1_ablation/aggregation/{summarize_s_l1,s_ablation_summary_l1}.json`，独立S族 | 126/76/0/36/90与8对零差可复算；新C′关闭S/physical/electrical，不能为该批负结果/功能正确性补证。S支持域/对象审计未在本轮恢复。 |

中英图对应CSV逐行比较结果：图4=True; 图5=True; 图6=True; 图7=True。完整位置、PDF/CSV SHA与行数见JSON；未重新生成或渲染任何图。

## A6实际proof日志（不是旧运行时间）

| case | proven/unproven | 新proof runtime(s) |
|---|---:|---:|
| s382 | [[90, 0]] | 2.140 |
| s420 | [[79, 0]] | 0.203 |
| s641 | [[124, 0]] | 0.219 |
| s713 | [[126, 0]] | 0.344 |
| s832 | [[146, 0]] | 0.375 |
| s953 | [[228, 0]] | 0.344 |

s27/s820仅复用确切B对象的旧proof；六项新proof的pin为8192193，后来的模型保全/三态usedtypes检查不能改写原proof pin。s713通用换行解码全字相同，不作逻辑归一化，也不追认旧runtime hash。

## 当前新证据的可用范围

| 证据 | 真正已完成 | 不能替代/尚待 |
|---|---|---|
| A6 | 六个原mapped→accepted fixed，非零proven/零unproven；actual used三态交集空 | 补功能身份，不新测WNS/物理、不补造旧revision |
| B2 | core6871/0、mul917/0；core7孤立恒X源identity与其余二值SEC分账，mul0 | 非一般四态/Z/复位初始化证明；不改变5ns/2ns收益约束 |
| B17 | 12879/0，13.375s；确切接受raw/新完整模型flatten/assert，后验绑定通过 | 不沿用12812+1，不以同函数推断旧proof可靠；不升级整个B族比例 |
| C′ | 首18独立验收；当前冻结matrix24/72、source稳定；实际计数见JSON | 全72未验收，不能替C/D/B/物理/S；QA/零收益/同路径不能当机制增益 |
| D56 | 56实际CLI与历史resolved_args一致，无EDA | 五臂×8和k1两臂×8的真实STA/finalSEC/计数仍待 |
| B3 | root51项mock QA，无EDA | b09/b20/b21实际语义/合法候选同族恢复仍待 |
| C48 | 作者84项mock QA；OI042精确反例最小修复的作者拒绝检查 | 独立修复复核按另包推进；没有正式注册/EDA/新C科学数字 |

## 支持域与不可回避的实验门

当前actual tri/Z是Boolean final_sec的unsupported，非pass；准确writer输出Z并不能使二值Yosys等价证明具备四态能力。ordinary inv与三态inv的data/enable必须匹配，顺序单元不能作为组合R。恢复三态支持需要显式四态编码或已证明的语义变换，OI039保持open。B2孤立恒X PO证书只覆盖实际7/0源，不可泛化到任意X内部消费、多驱动或三态。

C历史只抽查12代表9invalid/3unknown，不外推48全部invalid；D结构invalid不写成本轮已由SEC证明不等价；未知不写作失败。所有新运行须保完整源码/库/输入/argv/真实launch/实际commit/终点独立SEC。保留旧结果和归因，以有效实验补足主张，不能只弱化文字或移去不利样本。

SPEF 40µm/unit及50/6个F6的完整逐候选绑定本轮未恢复，明确unknown，后续需定位scan/gate原件与RC/候选inputs。不把这项unknown描述成已证伪，也不能用关闭physical的C′代填。

14张表的完整zh/en起止行与对应主张见JSON：9张涉及配置/实验（configs、overview、sec_iscas8、ablation、efficiency、runtime、f16_dist、pr8、s_boundary）；另5张为相关工作/符号/方法定义，不用新实验数字替换。

本轮没有回填正文；应先按上表闭合B3/D56/C48与必要S/SPEF来源门，再同步中稿中文摘要、内嵌英文摘要、英稿、表/图注、结论与补充材料，最后编译和版式复核。确定的周期说明、A6/B17对象状态可先以精确范围修正，不能带动未闭合的总体效果结论。
