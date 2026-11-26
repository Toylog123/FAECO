# 开发经验库（踩坑记录）

> 解决问题后当天登记。历史坑位自 work_log 摘录高频项，完整记录见 `project_docs/LOGS.md`。

## 2026-10-16 字节SHA钉定的新证据须防Git换行转换

本次新QA/B17proof/v6-v8/Cprime-v3包由root加.gitattributes -text，防core.autocrlf检出后SHA变化；仅新包、不重写旧证据。提交前仍须核index blob与working raw逐字节一致，属性本身不能替代该检查。后root实际核60新包index blob==working raw逐字节一致；git add --renormalize才使raw入index，单调用cr-at-eol diffcheck rc0，原件未改。属性保护与实际index校验均须完成，不把仅写属性当已保护。

## 2026-10-16 增强专属检查器不应悄改共享唯一性API的输入语法

完整v7源稳定却965pass/1fail：F1 named-pin覆盖严格性扩入公共_assert_unique_physical_instances，使topology合法positional参数抛异常。归因为实现接口兼容性，不是科学想法失败。仅F1显式opt-in提取连接，公共唯一性检查保留positional；保持严格覆盖同时不误伤其它调用者。最小opt-in修复后scope30pass、精确V3pass与完整v8=969pass/4skip/156subtests、155.12s/wrapper157.969exit0、170SHA稳定。OI040/041实现门现可关闭，旧v7失败原件不覆盖，科学域不泛化。

## 2026-10-16 字节保真QA归档不自动改变脚本的相对路径上下文

直接运行Cprep qa归档副本20例FileNotFoundError，原因测试R=parents[2]依赖原scratch位置，未触生产代码；原位同源控制20pass/1.10s。原件不改，以原scratch上下文重跑或在新副本适配路径/重新锁SHA，不能把归档调用错误当生产缺陷。OI041新集成10原件同样保source/target/hash，README明确该界限。

## 2026-10-16 修复后须原样重放反例，不能仅测格式化改写的同义例

原seq反例是单行：顺序子门多行测试和926整套通过后，原样重放仍reset→set pass；gate_sizing行首regex两侧漏为[]，F1 strip实际cells后空集合伪pass。原反例混合了parser与seq语义两层缺陷，初述归因不完整。保留失败SEQUENTIAL_GATE_VERIFICATION，不覆盖为绿；OI040仅多行子门有效，新增OI041修单行/$/注释strings/escapednet与物理↔parsed完整覆盖，并用旧源多行反证独立归因。需新v7/commit，不能以926通盖该反例。

## 2026-10-16 FF输出同为IQ不等于完整状态机语义相同

合法dfrtp_1→dfstp_1连全输入将reset改set，F1仍返回pass，LR仅按IQ给34个错误顺序R；新SEQUENTIAL_GATE_COUNTEREXAMPLE实证，而旧835通过仅表示未覆盖它。比较next-state/event/clear/preset，顺序单元不进组合R，保留合法同族G；actual63顺序类型已被graph正确识别，不改无缺陷模块。OI040已限定LR105pass/F1专属14pass和相关201pass，v6最终926pass/4skip/156subtests、155.08s/wrapper157.875exit0、168SHA稳定/PYTHONUTF8=1，OI040代码阶段已关闭；九份旧proof模型重生成9/9字节一致/source与LIB稳定（非新外部proof），新整套/commit仍待；不自动否定模型未变、实际非seq修改且已有真实独立proof的A6/B2/B17对象。

## 2026-10-16 B17未证点不能仅凭note认定工具伪阴性

实际旧_177917_由nor4b_1→nor4b_2的改动驱动；旧脚本未flatten/无assert，log有changed cell No SAT model。find_same_wires false-negative旧note不足以归因。按真正baseline/accepted raw与完整模型新flatten/assert proof已返回pass13.375s、12879/0，主线POST_RUN_VERIFICATION已确认原bytes/完整decoded/唯一nor4b尺寸变化/全部artifacts与44source匹配、12879/0实log成功；不得把新证明反填旧运行或补造旧schema没有的state hash。首次历史map.ys因CP936而UTF8预飞失败在SEC前，明确strictCP936保原bytes/hash，不能宽松吞错或改proof网表编码。

## 2026-10-16 同族恢复必须保运行器调度且不把recipe见证当runtime身份

B3_RERUN_DESIGN实际绑定B的stateful outerloop，不能改用C逐实例greedy或C′cut调度；runtime argv/source/priority等未知，execution_ready=false，当前defaults不能冒充恢复值。C增量14对完整trial/终点相同是更强recipe见证，但确定性重跑和派生档案都能产生此观测，不证明复制/重跑，也不补runtimepin；canonical s382仍缺。新同族重建可明确选择参数/冻结输入，必须与旧identity区分，避免因恢复困难悄换算法。两报告均已实读，只读非EDA。

## 2026-10-16 B2恒X边界证书须与独立proof和原字节对象同时绑定

B2 checker66fe72ff…独立review准确为20/20负拒、5/6正接受，actual2pair7/0cert；escaped output保守误拒不影响实际对象，不能称26/26期待全匹配。44d20bb正式新模型B2两pair已pass，core6.078s/mul0.750s，wrapper16exit0/source稳定；POST_RUN_VERIFICATION原bytes、完整decoded、全部artifacts和动态cert双pair一致。证明只组合two-state SEC与独立孤立constant-X identity，不泛化四态/复位等价；旧runtimehash不补造。OI038当前新模型缺证已恢复，B3三态缺输入仍另需同族恢复，不能借B2关闭。

## 2026-10-16 控制组通过指预期状态匹配，不等于全部等价证明通过

新pin02e82a2正式9控制为3正确pass/3故意错fail/2三态unsupported/1缺输入input_error，9/9 matches、source稳定、wrapper31exit0，后验44source/LIB/driver无漂移。只有按预锁状态解读才准确：错误应拒、能力外应unsupported、缺输入应input_error。不能称“9个等价证明通过”或三态支持已证；三态能力恢复仍open。来源sec_controls_phase2/controls.json与POST_RUN_VERIFICATION，均已实读。

## 2026-10-16 父进程-Xutf8不替代全进程PYTHONUTF8环境

- **实际归因**：完整v4运行中3F，独立3个子CLI测试复现3fail+4warnings/0.97s，子CLI仍按CP936输出而父按UTF8读取；父命令-Xutf8不会自动设置所有子Python环境。
- **限定修复**：源码不改，scratch harness设置PYTHONUTF8=1传递全进程，同3例3pass/0.82s。完整v4实际832pass/3fail/4skip/5warn/156subtests、148.38s/wrapper152.968exit1、166SHA稳定，3F均该环境原因；原件保留。完整v5最终835pass/4skip/156subtests，147.00s/wrapper152.781exit0、166来源SHA稳定，JSON显式environment_overrides PYTHONUTF8=1；已可确认该环境下当前实现全回归通过，不升级四态/科学结论。
- **另一个边界**：原Zvs0/1在临时guard下精确输入均unsupported/commandNone/source稳定，证明门确实拒绝不可靠工具，并非四态证明。两类问题分别归因，不把编码环境修复说成Z语义恢复。

## 2026-10-16 更强反例推翻证明方案时保留准确模型与支持恢复路径

- **归因**：Zvs0工具伪pass之后，二态cut组合方案又被两个独立反例（含Z^Z vs0）推翻，因此不实施。函数/三态公式静态准确，不代表当前二态SEC soundness。
- **当前处置**：actualtri、显式Z或switch给structured unsupported非pass，准确writer保留；这是临时证明器能力门，三态真实语义支持仍open，恢复路径是显式四态编码，不把unsupported称为已证或科学降级定稿。限定domain红5→含scope16pass/扩展11pass，整体v4未开始。
- **整体失败层次**：v3=822pass/2fail/4skip/156subtests、165SHA稳定，两CLI旧fixture缺dfrtp/RESET_B被新门正确拒，拟补真实fixture保留assert。不是生产门误拒合法完整输入，不改门放行。
- **日志纪律**：原CP936混编码log使harness UTF8展示失败，但JSON/JUnit完整有效；原件不改，用适当解码实读，后续-Xutf8。不因展示异常抹掉真实失败结果。

## 2026-10-16 真实三态控制需优先检验Z与常量可区分性

- **实证反驳**：dirty三态首5组2正pass/2负fail/1input_error全部matches，source稳定/0STA；更强控制中Zvs0预期fail实际pass、Zvs1fail，诊断passed=false。首组20s exit0与后组11s exit1均保留，不能只报前组“全过”。
- **归因**：当前Yosys默认流程Z塌缩，普通真值控制能过不能证明工具保持四态语义；不是已证论文实际电路不等价，也不是writer静态语义检查可替代的工具可靠性门。
- **处置**：OI039追加soundness阻断，主线+两agent先只读设计composition boundary proof、暂不改生产；验证工具能区分推翻主张的负控制后再谈正式证明。完整v3在跑至少2F待结束归因，无STA/pilot。
- **来源**：r22_correctness_20261016/tristate_tool_diagnostic/diagnostic.json与tristate_z_diagnostic/diagnostic.json，记录员已实际读取status/expected/actual/source_stable/timing_runs。

## 2026-10-16 独立接线probe通过后仍须核对writer实际导出

- **已实读限定结果**：TRISTATE_INDEPENDENT_REVIEW的联合data/enable映射与batch必需输入门probe16s/exit0、5来源SHA稳定；合法只到subprocess sentinel，无EDA，不认证审查者自己的writer。
- **新增自审边界**：actual Liberty13个三态中4个einvp使用后缀反相(TE')，parser保留原文但writer只字符串替换导出非法Verilog。不能从metadata解析/接线通过推断模型可编译或工具Z语义可靠。
- **处理与状态**：另开TDD覆盖全部13三态实际导出、后缀反相转换，再重新冻结/整套与真工具正负控制。OI-039仍open，v2仅dryrun不执行，新v3待；当前不写解决/科学通过。

## 2026-10-16 function真值表一致不能证明三态语义完整

- **实际发现**：B模型audit.json的einvn_1/_2只function真值表与普通inverter相同，但实际Lib还含three_state(TE_B)；b09/b20/b21 actual final和SEC gate均缺TE_B。旧模型及8192193初版writer忽略三态，候选只按function可能误选三态cell。
- **归因**：同根Lib语义/连接完整性实现缺口；旧28 SEC对象绑定仍真，不证明模型完整，也不能据此直接判电路不等价。本次使用类型审计中23未见缺口，5有缺口（含Pico2），不继续把26统称完整语义。
- **处理**：完整pin block/three_state metadata与联合候选语义，RW模型/F1F2必需输入、ABC明确不支持边界和最终SEC输入门同步修。旧757/6控制不覆盖新反证，需新整套/commit/pin；v2只dryrun未执行，原manifest保留，新源v3。A6结果保留待usedtypes复核，不轻率推翻或无限外推。
- **当前状态**：OI-039已登记，修复与新验收尚待；没有STA/pilot。

## 2026-10-16 s713 SEC raw字节SHA差异须先检查实际文本/换行

- **观察**：A s713 receipt的gate归档SHA为3c982ac0…，proof final_raw为5fe19204…，其它五对象相同；记录员先报主线而未宣称六对象全部确切闭合。
- **实际归因**：原fixed16561B/LF，final_raw17585B、1024CRLF；utf8-sig通用换行读取后逐字完全相同，原LF文本hash与归档SHA一致，是Windows写出CRLF。未改候选/模型，不留虚假科学缺口。
- **验证**：A六对象proof_run.log/逐receipt全部pass、wrapper21/exit0，frozen8192193/clean source与输入哈希绑定。实际文本一致应明确换行转换，不能仅因字节哈希差就否定对象，也不能不查差异便放行。

## 2026-10-16 完整回归揭示声明文本比较误拒合法B（当前完整v2已通过）

- **实际失败**：首整套741pass/1fail/4skip/156subtests，108.20s、wrapper112/exit1；源码before/after SHA稳定。旧合法buffer-chain测试中wire N;改wire N,N_BUF;，_non_rgb_structure按整条声明Counter误判N删除。
- **归因与处理**：实现兼容性错误，不是想法失败或测试对象漂移。models仅修函数按既有net语义保持宽度/signedness，允许分组合并与新增线；不改旧fixture凑过，专属后再完整回归。
- **证据纪律**：full_regression三证据原件保留，修后另用full_regression_v2并重新冻结当前源码。专属红7fail/8pass后相关五文件145pass/22.28s、wrapper26/exit0，原sole failure通过；新增15参数例约束宽度/signedness/次数。新版整套实际757pass/4skip/156subtests，102.50s/wrapper107/exit0、162源码SHA稳定，已可确认当前实现验收；真实SEC/EDA与科学恢复仍不能宣称通过。

## 2026-10-16 物理多输出支持须贯穿source/别名root/锥外边界与split

- **反证/归因**：独立复审找到无输入源未连source、alias root静默空锥、次输出被锥外消费者使用却记internal；修后split仍可能BO与internal重叠。metadata.cells与实际evaluator.lib的属性错配也会丢输出角色。均为可修集成边界，不据此否定方法。
- **处置/限定验证**：主线按原网表driver/全网消费者维护物理节点、root别名、external boundary与split互斥；integration_review_red 3fail/6pass、split_external_red 1fail之后，scope_final_green5最终68pass+1subtest/3.71s/timeout exit0。旧c17预期漏N11/N16外部消费者，经原网表确认后更新期望，保留检查。
- **A对象绑定教训**：s713 counterpart baseline带tie变化；只证明该baseline→fixed不足以覆盖原A。恢复工具主pair明确用原A mapped→实际fixed，干跑52输入/44源码SHA及六对象，工具9pass；尚未实际SEC，不把准备成功冒充候选已证明。
- **下一门**：production/tests冻结后完整回归和最终独立复审，真实证明/EDA另登记。上述限定修复不提前关闭历史A/D/C科学问题。

## 2026-10-16 r22多输出/刷新/SEC模块边界的反例驱动集成（限定范围已验证）

- **红测**：scope_red.log四项分别命中次输出依赖丢失、一个物理实例分裂/次输出根识别、CLI端点取helper同名D、S刷新失败仍提交；sec_module_red.log另命中注释假module污染独立SEC helper。
- **归因/处置**：主线graph/cut各输出共用同一物理节点、CLI先截取明确top、RGB/S均在提交前按top+Liberty刷新，独立SEC复用公共module_spans避免全文正则误读注释/字符串。深链fixture的循环内同名GROOT属于真实重复，移到循环外保留深链测试意义，不放宽生产唯一性门。
- **验证/边界**：日志实读scope相关七文件63passed+1subtest/3.85s、timeout120/exit0；parser35、models69为独立限定相关范围，不能加总当全回归。当前完整回归/独立复审与真实SEC/EDA仍待，不提前宣布所有K门或科学证据闭合。
- **复用**：scratch/r22_resume_20261016/{scope_red,sec_module_red,scope_final_green}.log，恢复计划R22_CORRECTNESS_RESUME_PLAN_20261016.md；有用日志待主线晋级跟踪证据包。

## 2026-10-16 r22恢复复用与验收对象约束（尚非新修复完成记录）

- **复用起点**：用户已明确恢复；先实读NAMESPACE_FIX_REVIEW的K1–K6最小反例、historical_correctness REPORT及已有v1失败原件，不重造归因或把旧667当当前通过。
- **本轮约束**：修复应同时保持多输出完整语义、物理实例身份/分母、目标module作用域；当前源码/fixture/模型/输入冻结后整套回归、独立复审，新pin/v2与独立最终SEC。旧失败输入和构造反例分别标注，不把构造探针说成真实实验已触发。
- **科学恢复**：A六补确切接受对象证明，D/C按同族输入/臂恢复；新C′单独18pilot→72，不跨族替换历史。未知不等失败，结构invalid不等新证不等价，计数对账不证明候选合法。
- **验证状态**：此条仅同步已核验教训与恢复纪律；本轮新的问题解决/测试结果待实际日志后补，不声称K1–K6已闭合。

## 2026-10-14 r22 多模块netlist：局部门成功不能替代独立最终SEC

- **真实反证**：首正式pilot两W0 runner均exit0，独立最终SEC却发现helper definitions不同并停止batch。B instance被insert_buffer放在首个endmodule/helper dff，而新wire/目标pin在真正top；旧局部F1/F2全文件parser合并模块命名域造成伪pass，截取真实top后F2 declared-undriven。
- **归因**：定位为可修实现与模块namespace边界缺陷，不直接否定cut/cost设想，也不把中间+.10/+.05 ns记作有效成果。原失败目录完整保留，首轮其它臂未启动；旧权威论文哪些accepted动作受影响另做来源审计，不先猜范围。
- **处置规则（修复尚未验收）**：目标模块必须从真实instance/明确top定位，新增wire、instance和pin改动保持同一模块；helper字节/同名instance/缺失目标/多模块异常都进入TDD。F1/F2必须在正确模块namespace内校验，并保留独立工具最终SEC。修复改变production后新commit/pin/v2，当前版本整体回归与完整受影响矩阵重跑，不能沿用旧通过或借旧pilot结果。
- **计数教训**：首pilot实读launch12/11、eval14/13，n_cache_replays/skipped_duplicate均0，各2条非STA为F1前置拒绝。差额不是缓存证据；同时保留真实launch、前置门拒绝、缓存与独立SEC状态，避免把局部成功字段升级为全流程验收。
- **证据**：LOG-20261014-23、OI-035/036、experiments/20261014_r22_cut_ablation的两W0 eval_trials/runner日志/final_sec/batch_failures。生产修复与最终验证继续推进。

## 2026-10-14 r22 回归时不可并行修改被测源码/fixture

- **现象**：第二次全回归628passed/1fail，batch输入锁stub失败；同一会话pytest已经载入旧fixture，但主线又加入LIB/mapped锁并修改production脚本，发生旧fixture与新脚本组合。
- **归因**：测试对象跨版本，不是这个结果已推翻实验设计。新输入锁与Path(m.LIB)统一必须在稳定组合中重测。
- **处理**：停止core编辑，重启session14951全回归，测试期间保持production源码、fixture与输入锁不变；若必须接纳修改，废弃旧验收对象并重新启动，不边测边改。
- **验证**：稳定最终源码实际629passed/4skipped/156subtests、99.79s，timeout包装102s/exit0。前两次回归只作历史，不合并为当前门；正式EDA未启动。

## 2026-10-14 r22 静态mincut探针：先检验预期，保留无作用与tie

- **现象**：P2原断言uniform与高size权重应选不同门，实际两者都选g1，断言失败。
- **归因**：实际求解确认uniform为确定tie，高size也选择g1；测试预期不能从“权重改变”自动推出“这个输入割必改变”。这不是已经证明实现错误或方法无效。
- **修复**：以高size与默认配置（g2）检验代码具备改变割的能力，同时保留uniform确定tie与根退化场景；不删零差异例，不为了pilot好看换真实实验臂。
- **验证**：主线TDD先失败后通过，candidate十二项与批运行器共15passed/0.21s，无EDA。静态可辨识能力不等于实际电路时序贡献，正式C′按预锁正负判据报告。

## 2026-10-14 r22 历史来源恢复：JSON缺字段可用独有报告交叉验证

- **现象**：r21仅依旧JSON判断b17新STA数量不可识别；该判断不能证明仓库其他档案也没有来源。r22先查既往/原始报告，而非重跑或补造schema。
- **恢复**：b17的104条trial按iteration与组内序号精确对应104独有STA日志/Tcl，所有日志有限WNS与trial相同，候选mapped输入路径一一绑定；当前可报告104个有独有来源的候选STA结果，结合另18实例2890得到2994。它不含基线/刷新/重试/SEC的所有工具执行。
- **验证**：只读历史审计300s超时包装、51s/exit0，输入清单及两个结果JSON哈希回验；证据为r22_historical_audit_20261014包。主线确认B/D计数可闭合；没有改原始档案、没有新EDA。
- **边界**：C的输出目录跨pass覆盖，缺base hash与实际revision；重复candidate描述不等于缓存，现存报告数不等于历史总调用。flags恢复分recovered/launcher_recovered/inferred/missing，launcher模板不能当实际argv证书。s382 v3的数值/输入匹配不证明发布身份，不自动借入主表。
- **复用**：先用独有报告/Tcl/输入哈希寻找可审计来源；无法恢复的身份/执行数明确保留，不猜参数、不套其他族缓存规则，也不把档案审计拖成无期限等待。

## 2026-10-14 STA 台账：来源字段不证明新执行，缺失 schema 不等于零

- **现象**：D 的归档 B(k) 含 `skipped_duplicate`，缓存字典保留旧 STA provenance；旧 runtime 把全部评估记录当测量。B 的 3363/664/104 也恰等于全部 trials，含前置拒绝/缓存，不能称新增 OpenSTA 次数。
- **根因**：逻辑评估记录、带来源记录、新 STA 执行、预算计数是不同事件；字段名 `n_candidate_sta_runs` 和有 provenance 不足以证明新测量。
- **修复**：D 从原始 trials 筛有效来源/WNS 并剔缓存，逐运行与唯一报告路径和 sta_used 对齐；实际图轴/表列使用重建数，旧记录列与墙钟保持。B 的指标名改为评估记录；18 实例可确认新 STA 2890，b17 缺来源/缓存 schema，保留未知，不能补 0 或把 104 全当新执行。
- **验证**：独立 `methodology_verification.md`、`sta_count_followup.md` 与当前主稿一致；D Fixed/EMA 新 STA 1947/2003，随机均值 2480.7；本轮全稿质量门零错误/溢出/未引用。只做已有台账重算，没有新 EDA。其它族审计继续留 OI-034。
- **复用规则**：计数单位先落到真实事件、原始记录和独有报告路径；同族缓存标记规则不能套给缺字段的历史 schema。曲线按各臂停止位置结束，不在停止后外推收益。

## 2026-10-14 双栏末页 balance 的微小 vbox 溢出

- **现象**：r21 内容与配图集成后仍有末页 0.8534 pt Overfull vbox，hbox 和引用已全通过。
- **归因与修复**：主线单独禁用旧 balance 后溢出归零，定位为末页平衡算法；enlargethispage 引入 Infinite glue shrinkage，已回退。使用本机 `flushend[noshrink,nospread]` 平衡双栏，未缩字体/行距/砍内容。
- **验证**：当前 `.tex` 已使用 flushend，`build_qa.json` 为 12 页、hbox/vbox 全零。该解决只适用于本稿/当前安装的包版本；后续版式变动仍要重编译并看末页，不照搬通过结论。

## 2026-10-14 配图数据读取：零候选 schema 与符号字形

- **现象**：r21 配图首跑读取 s641 的 S 统计时缺少 `tier2`，报 KeyError；部分数学下标/对号未被导出字体覆盖。
- **归因**：原始 `summarize_s_l1.json` 的 s641 确实是零抽窗、零候选、零测量，不提供候选测量汇总层。把每电路都当成非空候选 schema 是读取实现错误，不能据此认定数据丢失；字体中没有对应字形是另一个导出问题。
- **处理**：`paper/zh/figures/data/scripts/review_r21_figures.py` 仅在 `n_candidate == 0` 且 `n_measured == n_extracted == 0` 的断言成立后生成全零分类；其他电路继续直接读取 `tier2`，保留分类总和与总候选数断言。缺字标记改为覆盖可用的字形/字体。
- **验证**：实读零候选原始记录与当前分支，首版图件已导出；最终六新图和整稿逐页视觉/字形审计通过，详见r21 qa_notes。此为既有证据的绘图读取/导出修复，不是新 EDA 实验。
- **复用规则**：零候选可补零分类必须基于明确 schema 与零抽窗/测量断言；对未知缺项直接补零会掩盖证据缺失，不可采用。导出成功后仍要目检字形，不能只看进程 exit code。

## 2026-10-14 预算曲线读取：配置字段层级不能从参数名猜测

- **现象与归因**：新增既有族 D 的 B(k) 备选图时，首次读取把 `sta_budget` 当 `run_config.json` 顶层字段；真实配置保存在 `resolved_args` 中，这是绘图读取实现问题。
- **修复与验证**：改为 `config['resolved_args']['sta_budget']` 并断言为 500；同族全部电路、全部配置分别加载自身数据，按各自自然终止点截断。最终入稿文件为 `fig5_budget_curves_r21`（前期备选名figD），实际轴又按原始台账剔缓存重建，详见上方计数修复；不将族 C 数字接入曲线。
- **复用规则**：先实读原始 JSON 的 schema，再绑定图中计数单位。预约额度不是实际 STA 测量次数，配置字段正确读取也不能将两种计数自动等同。此为既有数据后处理，不是新 EDA 实验。

## 工具链

1. **Windows Yosys 0.9（32 位）映射大电路 OOM**
   - 现象：b18/b19（原型约 7.0 万/23.1 万门；**2026-09-28 更正**：原记「37.6 万/75.5 万门」在任何证据文件中均无法定位，映射后为 7.57 万/15.10 万个 SKY130 单元，见 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md` §6）read_verilog bad_alloc；$shr 技术映射 OOM。
   - 解决：WSL2 64 位 Yosys 0.33（`run_yosys_mapping` 增加 `yosys_cmd` 参数）。
   - 验证：b18/b19 映射成功（峰值 4.7 GB）。

2. **SKY130 `clkinv_1` 不在 Liberty → CEC unavailable**
   - 解决：从 Liberty boolean function 提取 assign-style `sky130_cells_v2.v` + Yosys `miter -equiv` + `sat -prove-asserts`；8/8 等价证明通过（20260803）。

3. **b19（7.5 万单元）WSL2 STA 输出截断**
   - 解决：`run_opensta()` 3 次重试 + 手工复测校验（WNS=-17.42 一致）。

## 形式验证

4. **顺序 SEC `find_same_wires` 局限（b17 剩 1 个未证明点）**
   - 现象：nor4b_1→nor4b_2 同函数尺寸替换因两侧 wire 命名不一致未匹配。
   - 结论：Liberty function 等价即 effective_pass；论文如实单独报告（12812/12813）。

## 流程 / 工程

5. **多轮 ablation 被 early-stop 截断（假阴性）**
   - 原因：flow.py 接受分支无条件 return True。
   - 解决：仅 `early_stop` 开启时提前返回（flow.py:471）；264 测试全绿；备份 `project_docs/archive/superpowers_backup/T19_20260908/`。

6. **论文数字与实验产物混源（2026-09-11 审计）**
   - 教训：同一小节混用两轮运行数字（1012 次 STA、b21 +2.16、JOINT-12 均无产物支持）。
   - 规则：先更新聚合 summary 再动论文；审计记录 `project_docs/review_history/paper_audit/consistency_audit_20260911.md`。

7. **仓库迁移（2026-09-12）**
   - 目录 rename 被 BaiduSync 客户端句柄阻塞（Device or resource busy）→ robocopy 复制（316,765 文件/117.7 GB，0 失败）+ 源目录留作归档。
   - `.venv` 可编辑安装路径失效 → 重新 `pip install -e .`；硬编码绝对路径脚本改为 `__file__` 锚定。

8. **LaTeX 双栏 `figure*` 独占整页造成版面塌陷（2026-09-28）**
   - 现象：第 5 页仅 7 行、约 80% 空白；且 §3.3 正文在上一页末被截断，跨过图页才续上，阅读流断裂。
   - 根因三重叠加：① 图为 1254×1254 正方形、宽度 `0.85\textwidth`（14.4×14.4 cm）过高；② 位置参数 `[!htbp]` 含 `p`，允许 LaTeX 生成"只含浮动体"的浮动页；③ 图前 `\FloatBarrier`（`placeins` 包）强制立即输出，与图后屏障形成夹逼。
   - 解决：改 `[!tb]` 禁用浮动页 + 宽度降到 `0.55\textwidth` + 删除图前屏障 + 合并相邻重复 `\FloatBarrier`（全文 20 处，其中 2 组为连续重复，功能等价无意义）。
   - 结果：10 页 → **9 页**；第 5 页 7→43 行（图 + 正文 + 表 3 同页共存），末页结论与参考文献同页、不再孤立成页；0 Error / 0 Overfull / 0 Underfull。
   - 规则：双栏文档慎用 `figure*` + `p` 位置 + `\FloatBarrier` 三者叠加；`\FloatBarrier` 只在节边界保留 1 个，禁止连续重复（重复调用无额外作用，却让版面僵硬）。

9. **PDF SHA256 不能作为"内容一致"的判据（2026-09-28）**
   - 现象：同一 `.tex` 一字未改，重编译后 PDF SHA256 由 `5c98b77d…` 变为 `611741c5…`，看似"内容变了"。
   - 根因：PDF 内嵌编译时间戳（CreationDate / ModDate）元数据，每次编译字节必变。
   - 解决：判定内容是否真一致改用 **`pdftotext -layout` 全文的 SHA256**（本次 `856fac5b…`），并配合页数与质量门；实测两次编译文本指纹完全相同、`diff` 无差异，确认仅元数据变化。
   - 规则：冻结记录须同时给出「PDF 字节 SHA256」（标识该文件副本）与「文本指纹」（标识内容）；不可只用前者断言内容一致，也不可因前者变化就判内容被改。

10. **`\FloatBarrier` 在双栏下退化为 `\clearpage` → 孤儿参考文献页（2026-09-29）**
   - 现象：论文改完正文后编译多出 1 页，第 10 页仅 8 条参考文献、约 80% 空白；上一页左栏亦有约 28% 留白。
   - 根因：`placeins` 的 `\FloatBarrier` 在**双栏模式下遇到待排浮动体会退化为 `\clearpage`**（须把两栏都清空）。§3.4 表 `tab:failures` 之后、§3.5 之前那处屏障前方有表未排出，于是强制结束该页 → 正文整体后移 → 参考文献被挤成独立末页。
   - 解决：**只删掉那一处多余 `\FloatBarrier`**（除该行外 `.tex` 与上一版逐字节相同，`diff` 输出仅 `311d310`）。10 页 → **9 页**；第 5 页 = 图 2 + §3.3 正文 + 表 3 + §3.5 开头，第 9 页 = §5 结论 + 参考文献 [1]–[19]（约 95% 满）。
   - 规则：**页数异常 / 末页孤儿 / 大面积留白，第一优先是逐个试删（或下移）`\FloatBarrier`，而不是缩字体、行距或砍内容。** 排查方法：数出全文所有 `\FloatBarrier` 位置（`grep -n '\\FloatBarrier'`），每次只删一处后重编译，看页数与每页有效行数（`pdftotext` + 按 `\f` 切页统计）。

11. **内容指纹依赖 pdftotext 实现：Git Bash 的 `pdftotext` ≠ poppler（2026-09-29）**
   - 现象：冻结记录的内容指纹 `7adf0279…` 用"同一条命令"复算得到 `443c5c3a…`，看似内容被改；但 git 工作区干净、PDF 字节 SHA256 与冻结记录一致。
   - 根因：`pdftotext` 在本机有**两个实现**——Git 自带 `C:\Program Files\Git\mingw64\bin\pdftotext.exe`（**xpdf 4.00**，Git Bash 默认解析到它）与 WinGet poppler `…\poppler-25.07.0\Library\bin\pdftotext.exe`。两者对同一 PDF 提取的文本不同（布局/空格处理差异）→ 指纹不同。用 poppler 25.07.0 复算**精确复现** `7adf0279…`，证实内容未变、指纹 oracle 是工具相关的。
   - 规则：**文本指纹必须连同工具版本一起冻结**——记录指纹时注明工具（本仓钉定 poppler 25.07.0：`"$LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin\pdftotext.exe"`）；复算不一致时**先用 git 干净度 + 字节 SHA 排除文件被改，再换 pdftotext 实现逐一对算**，不得直接判"内容被改"。

12. **双栏稿压页：删掉正文全部 `\FloatBarrier`（2026-10-09）**
   - 现象：文字收敛后末页出现孤儿参考文献页（[13][14] 独占第 9 页、约 93% 空白）。
   - 排查：① 先证"参考文献本身无压缩余地"——`itemsep≈0`、`\linespread{0.95}` 下仍 9 页；② 删约 5 行正文 → 仍 9 页（省下的空间被栏底松动吸收）；③ 按经验 10 的思路**逐处删除 `\FloatBarrier`**（正文原有 11 处，均为节边界）→ 配合 7 处去重编辑。
   - 解决：**只保留图 2（全宽 `figure*`）之后那 1 处**，其余 10 处全删。9 页 → **8 页**，且**图/表的页面分布逐项不变**（先在与主稿逐字节一致的实验副本 `_exp8.tex` 上验证，再落到主稿）。
   - 规则：双栏稿正文**不应放** `\FloatBarrier`；它只在"约束某个全宽浮动体的落点"时才值得保留。压页次序恒为 **调浮动体参数 → 删屏障 → （最后）才考虑改版式**；禁缩字体/行距/砍内容。并在导言区留维护注记，防止后人回插。

13. **Word 转排管线硬编码摘要，只改 OUT 路径会产出旧摘要（2026-10-09）**
   - 现象：v5 轮重建 Word 稿时只改了 `postprocess.py` 的 `OUT` 路径，结果 `…20261009b.docx` 的摘要**实为 v4 文本**（v5 摘要从未进入 Word 稿），而文档却声称"随 v5 重建"。
   - 根因：`scratch/word_convert/postprocess.py` 内 `zh_abs` / `en_abs` / 中英关键词 / 标题 / 作者均为**硬编码字符串**，**不从 `.tex` 读取**；管线各步（preprocess → pandoc → postprocess → Word 导出）对摘要文本无一致性校验。
   - 解决：以 `.tex` 为准重写硬编码块（并核对字数），重跑整条管线产出 `…20261009c.docx`；缺陷归档 `word/superseded/README.md`。
   - 规则：**改摘要/标题/关键词后，必须同步 Word 管线的硬编码块并重跑整条管线**；验收时须从产出的 Word/PDF 反读摘要文本与 `.tex` 逐字比对，`preprocess.py` 的 `N_BIB` 计数守卫也要随参考文献条数变化同步。

14. **内容指纹值会跨文档传播并被误记——必须回验（2026-10-09）**
   - 现象：v6 冻结记录的内容指纹 `91034fee…` 被写入 11 个文件；但用**任何**提取口径都复现不出它。
   - 排查：以 v5 的 PDF（从 git 取回）反推口径——`pdftotext -layout <pdf> - | sha256sum`（**原始输出，不去空白**）精确复现 v5 记录值 `0a2b0723…`；据此口径，规范脚本对 v6 稳定给出 `88b03403…`（连跑两次一致）。
   - 结论：`91034fee…` 为误值（字节 SHA `09197e5f…` 与页数均正常，说明 PDF 未变）。已更正全部 11 处。
   - 规则：**内容指纹必须由脚本按固定命令现算**，不手抄、不跨文档复制粘贴；跨文档引用指纹时回验一次。判内容一致用**指纹**，判文件副本用**字节 SHA**，两者不可混用。


## 2026-10-16 C′v3 pilot：无提交先查预算，不改协议求正结果（LOG-41）

首W0/s27实际候选WNS从-.27改善到-.26，但TNS从-.49退到-.50，eval_trials明确setup_tns hard_gate拒。finalSEC pass但提交0/WNS不变符合当前接受协议；应区分严格WNS接受目标、TNS等硬预算和tns-aware平局选择。不能用“唯WNS无约束”描述，也不为得到改善调整已注册参数。候选9/8字段有legacy计数语义，最终审计必须分别核理想候选、baseline/refresh/physical调用与提交，不能把候选台账字段当全体STA总数。mapping/static准备receipt明确not_run/STAfalse，不把静态门当RTL→mapped证明。


## 2026-10-16 只读审计须依据实际序列化schema（LOG-42）

C′v3首次独立audit误期待as_dict未序列化的epoch字段，KeyError且未形成结果receipt；不能记为生产或实验失败。修正审计schema假设，保留实际完整网表commit哈希链，并交叉核argv、source、mapped/log、candidate_ideal launch与finalSEC非零proven/0unproven，前5/18已通过。最终脚本另按receipt SHA归档，旧失败不伪装成实验返回值。


## 2026-10-16 权重接通与增益归因分开核验（LOG-45）

两pilot的W0/U0、W1/U1首round candidate_pool_trace显示configured node_costs非均匀且uniform全部1，但pool/dispatch cut hash相同。不能由臂结果相同断言权重未接通，也不能将当前改善直接归因给权重。先记录实现接通与实际cut相同的观察，等待全矩阵比较；不为得到正结论调整已注册参数。


## 2026-10-16 跨机器恢复运行pin须保存确切输入字节（LOG-49）

Git换行属性并不包含所有ignored本机输入，也不能保证未来检出的字节等同runtime。C′v3另建source_snapshot将44runtime source/Lib/8RTL/8mapped/preparer共62件原字节入ZIP，用manifest逐项SHA与ZIP SHA双核；记录员独立62/62匹配。保留工具登记版本且明确不含二进制，不能称完整工具环境可搬运。运行pin不变，受ignore的ZIP在72全部验收后归档阶段须force-add，不为快照提前commit。


## 2026-10-16 机制比较先按相同网表状态对齐（LOG-64）

同一轮编号可能对应不同累计ECO状态，不能直接把候选差异归因权重。C′v3先按base_netlist_hash匹配四已完成电路的W0/U0、W1/U1八配对，再核nodecost、cut列表、ordered pool、dispatch和最终全文SHA。当前各对20条同状态轮记录均为非均匀weighted代价但行为与终点相同；这是partial诊断，不能由“权重接通”推断“权重有增益”。重复同状态轮不作独立样本，未完成电路排除，不以调参追求预设正结论。


## 2026-10-16 输入不可变门须覆盖末次工具调用和提交前（OI042/LOG65）

C适配器原finally只核mapped，末candidate调用期间TCL Lib路径漂移仍1commit/qa_complete；应把TCL/Lib等完整冻结输入在调用finally与提交前核验，末次调用也不能漏。保留原probe原字节，修后独立重放PinDrift/exit1、0commit/无completion，再审注册38控制和60来源前后SHA后仅关闭实现门。作者84联合QA不替独立38接口QA/精确probe；C未正式EDA。plainSHA anchor检测可信本地写入下漂移，不是签名或抗任意整目录重写的授权。


## 2026-10-16 并发实验审计的N不能推断具体对象集合（LOG74）

C′v3审计期间运行继续完成。MATRIX_AUDIT_36实际为三电路各9、s420八臂加s713W0；实时后来四电路各9完成，不能倒推旧36快照也覆盖那四电路。原stdout/receipt及单对象验收一致，属于审计集合时点与记录推断问题，不是生产/科学失败。先按receipt明确对象范围并保留原件，再用新auditor在开始冻结eligible pair+completion SHA、结束重核以形成有定义的快照；新N另存，不重写旧报告“凑齐”。


## 2026-10-16 双栏PDF回读先区分提取顺序与版式缺陷（OI043/LOG80）

中文page7整页pdftotext-layout把左右栏交错，拼接空白不能恢复周期设置句；这是提取方法问题，不能据此判断句子丢失、版式失败或科学结果错误。保留首READBACK_PROCEDURAL_FAILURE/原全页文本，改用实际左栏crop回读并对照渲染页。时钟元数据修正同时核beforeafter完整14表块/7图引用不变、两遍编译/38页视觉与各PDF副本SHA，才关闭说明门；不能连带关闭历史科学缺口。新命名build路径此前不存在时保留路径说明，从仍完整canonical preview保旧PDF字节后再同步。


## 2026-10-16 历史QA源码须在后续修改前按字节备份（OI044）

证据内适配器也属于被测源码。B3旧24/44阶段保留QA日志但未备份对应adapter/tests；2277文件与3ZIP负查找无四目标SHA，不能把当前51QA源码反向重构成旧原件或声称历史可重放。当前51 source/receipt身份独立成立。C修前六原件按before manifest、旧review及旧QA SHA保真快照后才修，可避免同类身份缺口；新区域census首失败与v2也各自exact source归档。负查找与缺失限制须持续保留，不伪造恢复。


## 2026-10-18 最终矩阵验收：计数集合与源码身份以实际收据为准

- **现象**：旧current文档停在51运行中，恢复时已有72 completion；另有54快照尚未入记录。仅看完成文件数不能替代最终逐对象审计。主线首次手填完整期望SHA错误导致预飞assert拒绝，实际脚本无变化。
- **归因与处理**：将期望SHA来源改为实际打开既有MATRIX_AUDIT_54.audit_sha256逐字比较，而非手抄；重新实际启动冻结开始对象集合的v2审计器，不重跑已完成EDA。旧51/54与失败原件保留，不回写扩大范围。
- **验证**：MATRIX_AUDIT_72 SHAa34da9c3…为72/72、source_stable和all_matrix_verified true；8458评估、6858candidate+72baseline=6930过程、other0、192提交；72completion当前SHA全匹配，endpoint SEC均非零proven/0unproven。stage72五原件SHA独立保真。仅当前已登记支持域闭合，B3/C/D及四态/历史S/SPEF仍各守独立证据门。


## 2026-10-18 审计器也须反证：合法!与信号B1不能报模型错误

旧S审计把258 filtered模型标defect，根因Python evaluator不能解析合法Verilog !，不是模型被证伪；独立新parser首版又把B1信号误滤为常量造成314unknown。明确真值表正/负控及B1与1'b1区分后，V2对258文件1032组合条目全match/0mismatch/unknown（V2_REVIEW ed32cbe1…），旧失败原件保留。此结论仅二值组合输出函数，不扩大到顺序/XZ或整机。真正S非法接受链/CEC pre-post覆盖与SPEF驱动/双侧连接/报告顺序另待修，不以审计器错误掩盖。

## 2026-10-18 图件人工无碰撞结论须接受自动几何反例

完整矩阵v1人工与独立视觉均未发现标签问题，但自动COLLISION_AUDIT给出6处旋转tick bbox overlap/FIX BEFORE DELIVERY。原人工报告保留，不回写为未通过；当前交付门改为未过。数据CSV/图源重现一致、面板对齐通过，问题归因到标签几何而非数据/EDA；另出v2、重跑字形/碰撞/对齐/视觉与数据验收后才能闭合，当前尚待。

几何修复后验追加（LOG12）：最新v3源d9ef05b…/FINAL_REVIEW32ff889a…保存最终14文件SHA；raw/paired CSV逐字节不变、collision0/对齐PASS/最小6.8pt、root实际视觉与partial51提前拒绝都过。仅此几何门关闭，独立v3视觉追加和正式稿整合另验，原v1/先前错误判断继续保留。


## 2026-10-18 物理测量边界：输入漂移和双流诊断必须独立留证

确定性native控制重现Tcl调用中变化/SPEF生成后跨阶段变化（red3 2F17P）和stdout无末换行掩盖stderr锚定Error（red4 2F19P）。修复按实际两侧网表各自SPEF、同RC与逐侧输入/Tcl前后绑定；两个输出流分别检查诊断，失败/缺pin/无法解析不记有效float。限定green4 71pass/6.43s、221原件SHA-size全符。仅local QA完成snapshot未采source-before，整体回归必须另做前后锁；不是实际OpenSTA/科学效果验证。首green1 synthetic CELL_A句法不符现有quoted extractor属于夹具问题，保独立Y→Z意图改句法，不能把夹具失败计成新的生产bug。


## 2026-10-18 SPEF连接必须区分词法身份与物理端点

独立四类反例揭示escaped scalar和vector bit合网、纯port alias没有D_NET、module外未知文本漏覆盖、cell输出literal丢pin；不能因作者51/53限定测试通过跳过独立最小输入。红5case保真后修复，v5 58pass，POST_REVIEW46d9972e…原输入SHA相同/四source前后一致，身份与RC feedthrough/拒绝行为静态闭合。8实际mapped仅静态parsed，12无pin常量alias显式记录，不把无tie源的connected constant当可注入。真实escaped SPEF工具注入尚须新pin实际OpenSTA验证，静态通过不能推广物理收益。


## 2026-10-18 已完成agent续工必须触发新turn

OI045修复指令仅用send_message发给completed agent时只入队，未实际执行。根list_agents实查状态后改followup_task才启动；之前是协作调度空等，不是模型/代码技术卡死。续工需先查状态，idle/completed用followup_task，执行中才用send_message补充；派发后看实际消息/工具/产出，不把已发消息当已执行。原反例与全v1原件不受影响，后续红绿须凭实际收据再登记。


## 2026-10-18 native正控通过不能替代真实top反例（OI047/048）

primitive-only c17缺少used SKY时返回整库使无关$mul模型污染归一化（正确error）；精确used模型/显式空model修后native26pass仍不能证明完整CEC对象正确。更强ztop Y=A/Y=B反例实际不同，ABC却选first库buf而假pass，故必须绑定真实source top/唯一root并hierarchy-check-top。保真bca40修前源、原两个Verilog、native日志；修后原字节输入正确fail/NOT EQUIVALENT，三文件28pass。整体v3唯一旧assign-only测试仍要求wholeLib返回，属已被真实工具风险证伪的旧测试契约；仅更新该测试保原Lib字节/无无关module/缺model报错，再做v4。正控、原负控、整体回归、历史影响边界分别验收，不用限定绿声称全部旧证明有效/无效。


## 2026-10-18 Windows子进程编码与Git文本checkout必须实测

全v4三CLI失败伴stdout None/UnicodeDecodeError，-X utf8只约束当前Python，不能替子进程继承的PYTHONUTF8=1。相同CLI/参数两次rc0的原始stdout显示unset非UTF8/set1UTF8，两个文件显式env13pass，不改生产来掩环境；原v4失败保留，下一整套显式记录env。native测试改写5个tracked c17产物须先保generated/HEAD；Git restore自动CRLF可文本等同而exactSHA不同，保首assert失败后核归一文本再恢复HEAD精确字节，最终逐SHA5/5，而非猜同步软件或覆盖科学结果。


## 2026-10-18 SPEF静态身份分离须用有约束真实路径反证注入

无约束单buf组合网即便工具给数也不足以证明RC注入；微型控制改为两DFXTP夹buf真实reg→reg、同actualLib/CK/5ns，普通与busbit+escaped literal两条不同D_NET在40/4000um对RC正响应且四report_parasitic_annotation均零未/部分注入，两个错误pin底层仍有有限slack但API全null/error。根与独立56bdc6b1…核43manifest/47原件，关闭该tiny注入边界，仍不代RC几何标定、b18双向或benchmark收益；tool身份独立review仅核原收据，不能冒称复测Linuxbinary或stderr空。


## 2026-10-18 完整CEC须绑定两侧真实对象、状态优先级和选择前源窗口（OI048）

修Verilog原top后仍须用mapped右侧反例：同ztop inverter前插dummy identity可令ABC选firstdummy误pass。mapped/generated BLIF统一走共享normalizer，按引用图唯一root或显式有效模型、hierarchy/flatten；独立多root不猜，保raw与normalized各自SHA。实际ABC缺输入可rc0，错误/多root/非零优先于equivalence字样，保benign abc.rc查找区别。selector运行后原source新增wrapper仍能选旧top的普通/BOM2fail说明绑定要早于prepare/top推断，launch前与after也核原始source，不能仅核派生BOM副本。176原件/20normalization收据和原三输入根重放、独立263原件9cbabd66…闭合当前反例；全v5显式UTF8/native环境1056pass/174来源稳定。此实现门不自动关闭历史省top证明对象影响或静态timeout bytes异常OI049，历史旧报告继续保留/按实际调用与top逐对象界定。


## 2026-10-18 只读最终审计也必须保存实际执行脚本/输入原字节（P08）

P08首v1把旧SEC模板按新hierarchy/assert字面筛查，按实际prep-top-equiv及日志数量适配后结果成立；但最终适配通过PowerShell here-string管道送python stdin，未落脚本/原stdin/本地stdout。只能保留实际产物/会话文本及unknown，不能事后重建脚本称原件。原inventory2268B与splitlines/join后的discovery2290B也不可互代；补件恢复精确原inventory/v1源与log、旧receipt不改。后续派生审计先保存将执行的实际文件/输入SHA、命令与原双流，再运行。当前104来源/具体proof检查可逐对象复核，不等最终原流程byte replay已恢复。


## 2026-10-18 反馈后call_log只见初始权重须先查调用是否发生（D两例）

s27/s382 fixed-adaptive终点和actualSTA序列相同，不能直接判漏传weights。真实trace证明EMA开启/更新并传入cut，s382第7–20轮排序变化印证参数到生成器；pool/dispatch set与全部same-base跨对无新身份，flow在RealWnsEvaluator前去重，所以更新后没有新调用、call_log自然只记初始权重。两例63来源/45源/四completion绑定，candidate字段与87/124actualSTAevent同序；cut级8/11调用不是STA次数，326/292trace交叉对不是独立样本。先归因为本次beam/搜索新颖性及去重状态的限定现象，保方法目标/负结果，不改去重制造效果，不外推其它六例或反馈普遍无效。


## 2026-10-18 审计/归档harness统一绝对ROOT路径再枚举

外部adapter snapshot和D archive root-post两次在同类relative_to错误停于预飞：ROOT为绝对，而Path(root_name).rglob返回相对路径。入口先明确ROOT.resolve；配置中的相对路径用ROOT/root_name变绝对，枚举/relative_to双方同坐标系，必要时对传入Path显式resolve。root-post首300s wrapper5exit1原码/原log保，v2只改绝对枚举且新log，不把harness失败当archive/生产/EDA失败；外wrapper0与每case ROOT_POST接受分别核。仅文档经验，不在D源冻结期间修改code。


## 2026-10-18 同一exact对象的equiv点数可随证明构造改变（A8/s820）

旧B复用s820为137/0，新统一A8为139/0，旧稿138。独立核raw输入/top一致后，发现旧先flatten再equiv_make、新先equiv_make再flatten，保留dfxtp模型旧直接Q状态/新IQ后assignQ，待证日志集合也不同；不能把新旧equiv cell数视为同一集合或据此比较证明强弱。无最终RTLIL时两额外cell精确身份保unknown，不新EDA凑归因。稿表取新同批实log139及原runtime，旧证明与点数不覆盖。原raw/snapshot与prover raw因通用换行序列化可不同SHA，须分别绑定解码全文，不能把prover raw SHA回写原字节身份。


### 2026-10-18 PDF占用与构建身份（LOG103）

EN float v2首LuaLaTeX输出FAECO.pdf不可写，rc1且既有PDF SHA不变；改独占attempt02/build后两遍成功，说明输出IO失败不能当内容/算法失败。保首失败源/日志/收据，不终止用户进程；可独占输出并有界同步，持续锁定时明确交付新路径及旧canonical未同步。编译成功仍需检查目标版式：本例新PDF仍表16，未解决页位退步，不以产物存在宣称修好。


### 2026-10-18 进程并发门与整机计时协议分开（LOG110）

运行环境口径（LOG110）：D期同时存在mock adapter QA、只读7z压缩/恢复、A8串行SEC及LuaLaTeX/Poppler；科学STA≤2电路，但整机非独占benchmark。observed walltime不得直接作独占或跨方法速度因果；输入/结果/实际STA计数不变，不据此判D失效或重跑。严格速度主张另登记受控同硬件计时协议。 记录运行环境无需据此无证推翻科学正确性；若另做性能优越性测试，预登记硬件/后台负载/缓存/计时区间，结果与当前矩阵分族，不回改原walltime。


### 2026-10-18 浮动布局修订以实际字形和分节读序验收（LOG102–120）

A表新脚注令EN表旧15移16、B正文先开始；只加!或缩重复note未解决，FloatBarrier单独令28页/多留白，不能以编译0直接交付。先测原Fig3所有label/tick/legend最小8.184960pt，.78→.70投影7.345477pt后才限定include缩放，保图向量/数据；最终实际7.345520pt、图+A表15/B16/26页，作者及独立38页实际视觉与根回读后接受。区分字号投影/新PDF实际字形、固定HEAD图像字节绑定/编辑前filesystem快照。锁PDF用独占构建+有界同步，实际sync成功才更新canonical身份；保所有失败版/日志。


### 2026-10-18 skipped_duplicate标志不等STA缓存复用（LOG116/124）

D28独立checker_v2假定每个skipped_duplicate都有cached_from_seq，在s641失败。实读当前real_wns：_sta_cache命中有原launch身份，tested_candidate_hashes另有只查identity并返回baseline的无重放分支，且前置拒绝也可缓存。冻结ROOT28只读581来源诊断得5821实际STA重放+29hash无重放=旧宽cache5850，另76未缓存preSTA拒绝；分类必须结合launch身份/同base/hash/config/cache公式/原STA结果，不能只看bool或把缺字段补成想象STA。保旧字段口径，新增派生分类与实际启动成本分别报告，检查器适配先审核且不得改实验对象/结果。诊断当轮v3尚待完整独立重验，不以诊断代验收。后续LOG130实际v3 RESULT79ad2ce4…/16407来源稳定及根f14c3306…已正式接受固定28，wrapper185s/0；保全部rawSTA/SEC/45pin门与分型数，不把归因脚本当最终审计，未来全56继续同v3另预登记timeout。


### 2026-10-18 合取断言失败不能反推流类型或是否收到输出（LOG125）

OI049 redv1的isinstance(stdout,bytes) and stdout失败，只能知合取为false，不能推断一定在partial stdout到达之前；实际type/value未采且v2亦unknown。原SETUP_FAILURE过强句不改旧原件，新增CLARIFICATION9140b292…明确更正。合成bytes真红仅证public direct-CEC193→215→_tail902异常呈现，不替_run_abc_cec/mapped helper路径实证，也不说明真实OS/EDA timeout流类型；未覆盖路径仍静态风险，保至后续源修/回归。


OI049归因续验（LOG126）：不同owner只读FINAL1d89a8a7…核72原件稳定/45源pin、7final件，确认仅direct公共CEC注入路径三控制及v1合取断言边界，不重probe或EDA；归因接受不替代码修复/其它helper实证，D后修门仍open。

## 2026-10-18 r23审稿恢复经验（LOG145–149）

- 审稿卡先commit后看作者证据；A8真实日志归纳前已全证，不能仅因工具含equiv_induct推断实际证明依赖弱归纳；b17证明已做先绑定端点再改文，不重复实验。
- Windows CRLF可同时破坏固定raw pin与os.O_RDONLY/stat字节比较：先实测归因，保原件；隔离恢复固定LF、验证JSON语义/工具字节不变，不能改验证器条件求绿。详r23/qa。
- 生产完成/独立验收/全量归档是三门；C′不能替历史C/D，320匹配轮也不是独立样本。
- 专职记录应动作后立即落盘。收尾多次监测无输出时先问阻塞，仍未写则中断并主线最小同步；避免扩读和等待。

### 2026-10-18 后续授权要更新当前入口，历史审稿边界保留（LOG150–151）

r23只读审稿完成后，用户明确授权按审稿修改中文稿和配图：r24当前入口须切为修订in_progress，旧只读范围保留在dated历史交接，不得反过来阻止已授权编辑。论文/图件写权限与D固定runtime源/HEAD冻结分开登记；生产完成、正式验收、raw归档根post三门分别记录，不能因编辑授权提前提交或修源。专职记录先落最小启动日志再扩展交接，避免读完所有材料后才写。

### 2026-10-18 证明域分层与原数据再分析不能混成新实验（LOG153–162）

b17已有新模型证明且accepted raw端点与summary绑定，不足以把ITC正文18/19直接改19/19：旧模型审计中b09/b20/b21使用三态不完整模型，三对象须unsupported。保全19时序观察并单列支持域16与三态3，使用户同时看到历史改善与功能保证边界，不删除高改善/不利对象。先注册库、16网表与其余原输入SHA，再静态复核C′成本/面积/ITC分层/端点，不重跑已验SEC或STA；输入稳定证明只支持本次再分析，不恢复旧runtime hash。L与W1改变候选空间不作纯排序因果；W1/U1无差异须保留。

### 2026-10-18 annotation进程rc0不等端点完整（LOG171–172/OI051）

fresh C′W1/s382同网表u40反驳控制中，ideal及SPEF两侧delta0均成立，annotation重放rc0仍报告43 partially unannotated。必须执行预注册0partial/0unannotated门，5新STA后即停止并保原件，不能取物理WNS解释效果。模块端口DFF_N:D与叶端点DFF_N/_0_/D属于层级注入域，不能混作三态/inout或删合法网求绿。先完整规范化flat输入并重新证明的下一版须单独设计/新SHA/再注册，不改旧失败输入，也不归咎旧OpenROAD物理族。

### 2026-10-18 caption替换须绑定环境与label（LOG179）

r24 EDIT03将图件描述误放tab:overview的表caption，引入unsupported样式说明及表自引。此为编辑实现错误，独立检查发现后由EDIT06恢复汇总表标题，数据/脚注保持；不能以编译无错判语义正确。caption目标须连同table/figure环境、准确label和前后文匹配，修改后审查具体环境与整稿阅读/图表语义，再用最新源重构验证。保原receipt，不把错误归咎科学设计或工具QA误报。

### 2026-10-18 冻结清单必须在最后append事件之后形成（LOG180）

v2阶段12的FROZEN清单登记了仍会追加完成事件的PROGRESS.jsonl，根复核发生post-freeze仅该日志SHA-size漂移，门按约停住。完成动作应先写最后事件，再冻结或把可变进度日志与immutable最终收据分开；发生后不得改旧清单求符，应保旧清单/原日志、出POST_FREEZE_AUDIT与新最终清单重审。合同未过与科学数据/源/SEC漂移必须分层归因，不能以其它全符跳过唯一不符，也不能无证否定flat科学对象。

### 2026-10-18 记录脚本应实查写回，读句柄要关闭（LOG188–194）

ReadLines后只取首行可留下未释放枚举器，随后的WriteAllText同路径报文件占用。本轮首合并脚本末尾仍打印成功且记录完成句，实际写入失败；LOG189立即纠正，改ReadAllText取标题并每文件写后整串回读，LOG194才确认成功。脚本采用ErrorActionPreference=Stop，不能以末尾提示当动作成功；保旧记录/备份和失败日志，不将内部读句柄问题误判外部锁或科学数据漂移。

### 2026-10-18 内外迭代索引不能混比（r25/LOG217）

trial.iteration是evaluator内调用序号，history.iteration是外轮；不能据二者数值比较计“首个未提交外轮后新STA”。OUTER_LOOP_STOP_EVIDENCE已明确撤回33对象及8/144/56后续量，既有MATRIX72/曲线依sta_launch_seq和commit哈希链而不受该错误影响。必须先核字段语义/关联键再做反事实早停计数。C′无feedback时refined只是空actions历史标签，不证明权重/窗口变化；无提交不立即外停与是否真正追加STA是两个不同结论。

### 2026-10-18 r25压缩稿规则对齐与核查界限（LOG218–223）

现象：压缩时漏完整硬门、误加“无提交即停”，既有运行器记录中的refined又易被当作本批真实权重变化。原因是用摘要直觉替代固定runtime/caller和配置取证。解决：按3ea冻结ZIP核完整Accept=H且Timing，C′TNS硬门容差0；固定初始目标、仅提交后刷新P和锥，feedback关闭时不更新权重。EDIT03双源及FINAL_EVIDENCE_CHECK对8最低条件/负面保留通过，双稿构建/根视觉亦实录；后续主文小幅去重仍绑定新源构建，不借旧验收。

临时取证还曾把trial.iteration内层调用号与history.iteration外轮号混比，得出33对象“后续新STA”说法，现已明确撤回，不能作为实验事实或成本反事实。正式曲线按sta_launch_seq与commit hash链，不受该临时索引错误影响。文稿一致性修正不等于生产修复/实验失败，也不关闭固定池因果等科学partial。

### 2026-10-18 r26完整论文恢复与生成示意图核查（LOG229–241）

用户将r25的5页主稿判为压缩过头。修订应先识别必须由主文自行解释的方法、各实验角色和反例，再删重复；页数不作削减实质内容的硬门。r26复用已纠正TNS硬门、固定目标/提交刷新及无反馈语义，不能恢复旧完整稿时把旧公式/流程误写带回。

图像模型总览首版出现候选直达提交、reject进入提交、B画INV；根拒绝，保原件后定向编辑。v2按箭头和图注/正文组合核查，不把缺失刷新标签说成仍在像素中。六门例按全部连线/双c引脚/区域边界与代价核验；光栅稿原像素复制、prompt/未知模型身份/拒绝版本留存，不把矢量审计或投稿资格附会为已通过。

补充移除旧总览后，TeX进程rc0仍遗留本地fig:method_flow引用，源引用静态QA拒绝，修显式主文图1并重编。S证据复核曾错取wns_history[-1]形成4例表面差异，改按顶层wns、state.current_wns及已提交网表后8对终点一致；这是审计提取归因，不是新科学失败，原件不改。

## 2026-10-19 r27量化图统一色系与渲染同一性（LOG249）

现象：只改颜色复用绘图源，PDF字符/位图矩形字节级比较仍出现false。归因：r24导出舍入及ISCAS旧tight_layout重算导致亚点级文字/页面裁切差异，不能把CSV一致写成全部几何字节一致。实际数据逐SHA一致，科学绘图函数去颜色后AST相同；明确记下字符最大0.09034/0.42676/0.82237/1.47052pt与ISCAS裁切1.23312pt。三图辅助网格及ISCAS零参考线改无色防穿数字，旧iteration01保留；源码/5pt字形/碰撞工具rc0，5个fill-edge WARN以实际图形逐项解释。解决范围为工作稿颜色/可读性，不新增科学结果或关闭旧科学OI；根整体视觉另门。

### 2026-10-19 r27样式转向须保旧合同并重验新输出（LOG251–252）

用户将低饱和蓝灰进一步收敛为纯黑白灰。已验证旧数据/绘图逻辑可以复用，但旧蓝灰输出及视觉结论不能冒充新灰度输出已验；应先保存旧合同为superseded，登记新合同/提示词/原件SHA，再逐图核实际像素/分支可读性与双稿整体版面。本地旧exec不存在不能推断服务器任务已取消，记录仅限可观察事实。

### 2026-10-19 r27原图保全核查须按资产类型过滤（LOG254）

安装新图前的保护脚本将figures/CHANGE_LOG.md也当旧图核同，触发assert；此时未发生TeX修改。应先按.pdf/.png过滤9个实际输入图，再逐SHA与before核对。过滤修正后9原图均同，不能把记录文档更新误判为图被改，也不能据此跳过原图检查。

纯灰PDF在默认MuPDF ICC转换下可出现1/255通道舍入差；应同时检查实际PDF paint色值、嵌入栅格、原生PNG与ICC-off RGB，区分渲染转换与资产残留色。AI原生RGB的spread11/12不同于此类舍入，原件失败仍明记，文档DeviceGray输出另验。

### 2026-10-19 r27 TeX bundled Ghostscript环境与文档灰度输出（LOG256）

模型PNG外观中性仍可含微量RGB残差，保留原生图片后，可通过最终PDF文档DeviceGray输出统一交付色彩空间。首次MSYS将/DeviceGray转换成Git路径，第二次缺gs_init；定位bundled Resource/Init、Font、kanji与ICC资源并关闭MSYS参数转换后attempt03成功，失败原件保留，不能归为科学/输入错误。重导前先看已有rc0产物，复用后验而不盲重跑。

导出不能只测灰度：同时核原生嵌图尺寸、链接数、文字/字形序列与页面/字形几何。main p9提取空白改变，非空白字形序列全同，glyph原点最大0.0287552pt/页框舍入0.0040283pt；应实记PDFserialization微差，不能笼统称exactgeometry。后续仅LuaLaTeX重编会恢复原生RGB，交付必须再执行记录的DeviceGray及整体QA。

### 2026-10-19 r27完整稿黑白灰交付应绑定最终文档与复现链（LOG257）

原生AI PNG微量RGB残留保持原件和失败原始门，最终PDF经DeviceGray通过19页实际灰度；交付必须绑定最终PDF SHA、全部页实际视觉和六副本，并永久保存编译/导出/QA快照。若只保TeX重新编译，原生RGB会恢复；交接须明确compile→DeviceGray→QA。数据图线型/标记/灰度层级可读性须实际逐图逐面板看，不能只读通道统计。完整稿内容通过逆替换核字与旧源一致，样式完成不关闭科学证据门。

### 2026-10-19 r28图片占幅应按字形投影分别缩放（LOG260；整稿视觉待）

用户指出完整稿图片占页过大。复用既有资产先量原生PDF最小字号，再按实际正文/栏宽投影，避免全部图统一缩小而损可读性。两AI示意图改0.82正文宽、面积减32.76%；6量化图0.92后最小6.397–6.440bp。ISCAS89当前单栏6.118bp，若同缩至0.92会5.629bp，故维持1.0栏宽。原生PNG无法从PDF字形层取得字号，须新PDF整页实际目视；投影通过不替代最终视觉。只改11处width，逆替换与r27原源逐字同，资产/科学正文/数据不变。

### 2026-10-19 r28缩图后仍须重审浮动体堆叠（LOG262；修订验收待）

只缩includegraphics宽度也可能让原本分开的表与多幅图在同一页满足强制top布局，mainbuild01第6页表1/图3/图4堆叠、出现2次onlyfloats提示。编译rc0和0overflow不等布局合格；根实际contact拒绝后保原件，仅将图4[!t]恢复[t]约束，重新构建main02，补充未变不重编。应按稿面层归因，不能改科学数据或回避整体视觉；修订是否恢复平衡等待新PDF实际验收。

记录员首次EDIT02逆替换校验误将当前LF源转为CRLF后算SHA，assert在共享文档写入前拒绝。实查字节为LF，改用原字节replace后精确回EDIT01的b8ebb934；这是记录校验器的换行假定错误，不是源漂移，未改TeX或源码格式。

LOG263补记：只改图4仍不足，后续图5的!t继续绕过topfraction，main02虽rc0，实际vbox106.74588pt溢出并出页底。应同时核相邻全宽浮动体，保失败原件后仅恢复后续图5普通t；main03验收待，不借灰度/编译成功称版面通过。

### 2026-10-19 r28版面修订收束与视觉回执内容核对（LOG265）

相邻全宽图4/5统一恢复普通t约束后，main03静态/实际整页均无原main01堆图与main02溢出；实际量化文字floor须从最终PDF读取，主6.39716bp/补6.11806bp，而不能只引用原生投影。补充视觉回执曾复制主文示意图/参考文献页观察，记录员接收时实际对照发现，根仅修回执并更新最终包SHA；复用QA模板仍须逐字段按对象核对。原图/科学正文与数据未改，尺寸修改也须整稿验证并保失败原件。


## 2026-10-19 r29：投稿政策与主题适配须按现行官方来源分层核实

本次期刊咨询中，ScienceDirect期刊主页/aims-and-scope直接访问403；可访问的官方论文检索摘要只支持主题相关性，不能扩为完整作者指南、录用难易或分区结论。排除相似非官方域，HTTP依赖缺失后改用stdlib读取已确认官方域，无需安装软件。Elsevier官方现行AI政策允许满足披露条件的解释性图件；不可沿用旧印象判所有AI示意图必须重画。原图工具具体模型版本未知与目标刊披露要求仍须保留，不能据出版社通用政策直接通过投稿资格。根报告及实际来源/读取边界：paper/zh/review_rounds/r29_20261019/VALUE_AND_JOURNAL_ASSESSMENT.md及sources/。本次未改图、论文、生产或运行实验。

### 2026-10-24 Windows→WSL 的 TSV 管道：CRLF 会伪装成"工具缺资源"，BOM 会伪装成"目录名乱码"（LOG-20261024-03）

从 Windows 生成、给 WSL 脚本读的 TSV，默认编码会同时带 **CRLF** 和 **UTF-8 BOM**，两者都表现为与真实原因无关的报错：

- **CRLF**：末尾列多出一个 `\r`，使 `met1-met5` 变成 `met1-met5\r`，OpenROAD 报 `Layer met5 not found`（报错里那个夹在 "met5" 与 "not found" 之间的换行就是 `\r` 的指纹）。差点误判为 LEF 缺层——实查 tlef 才发现 met5 在第 263 行、方向合法。修法：TSV 用**原始字节 + 显式 LF** 写出（`write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))`），不要用 PowerShell `Set-Content -Encoding UTF8`（带 BOM），也不要让 Python 用文本模式默认换行（Windows 上会变 CRLF）。
- **BOM**：首字节 `EF BB BF` 使第一个作业键变成 `\ufeff<key>`，运行目录名带 BOM，聚合时对不上。

驱动侧再加一道保险：`tr -d '\r' < jobs.tsv | sed '1s/^\xEF\xBB\xBF//'`。**教训：报错文本里出现不可见字符（换行/零宽）时，先 dump 字节，再怀疑资源缺失。**

### 2026-10-24 冻结版图：`-utilization` 会让门尺寸 ECO 顺手改芯片尺寸（LOG-20261024-04）

用 `-utilization U` 时 OpenROAD 按**网表单元面积**反推芯片尺寸，于是门尺寸 ECO 顺带改了 die：s27 实测 baseline 11×69 sites / die (0 0)(36420 36420) dbu，ECO-fixed 变成 11×**71** sites / die (0 0)(**37180** 37180)。这让"物理后收益"里混进了"芯片尺寸漂移"一项，实测量级 **0.01 ns**——恰好压在论文的报告分辨率上。

真实 ECO 在冻结版图上做，所以比较必须**钉死 die + core**。OpenROAD 2.0（`v2.0-17598-ga008522d8`）的实测约束，逐条都是实跑撞出来的：

- `-core_space` 不能与 `-die_area` 同用 → `IFP-0024`；
- `-core_area` 不能单独用 → `IFP-0019`（要求 `-utilization` 或 `-die_area`）；
- `-die_area` 必须同时给 `-core_area` → `IFP-0017`；
- 坐标列表**不能带花括号**：Tcl 变量展开后 `"{0 0 36.42 36.42}"` 的 `llength` 是 1 → `IFP-0015` / `IFP-0016`。

可行写法：`initialize_floorplan -die_area $DIE_AREA -core_area $CORE_AREA -site unithd`，两个变量都是**不带花括号**的 4 元素列表。验证方式：冻结版图下的 baseline 必须**逐项复现**归档数值（s27：tns −0.67 / worst slack −0.36 / 0.47 实测一致），否则几何提取有误。

### 2026-10-24 从归档 P&R 日志提取版图几何：必须取最后一组 floorplan 块（LOG-20261024-04）

OpenROAD 的日志里会出现**多组** `IFP-0028 / IFP-0001`（tapcell、global placement 会重算 floorplan）：s27 归档日志实测 6×40、6×40、**11×69** 三组，**最后一组才生效**。用"第一条匹配"提取会得到 6×40 的错核心区。几何应从最后一组取 `Added N rows of M site` 及其**之前**最近的 `snapped to (llx, lly)`，再按 site unithd = 0.46 × 2.72 µm 推出 core 矩形。

顺带一个 bash 陷阱：作业 TSV 有 18 列而 `read` 只命名了 12 个变量时，bash 会把**剩余列全部塞进最后一个变量**，`core_area` 变成一长串带制表符的字符串，OpenROAD 报 `-core_area is a list of 4 coordinates`。凡是按列名取值，**要么读满所有列，要么显式丢掉余下部分**。

### 2026-10-24 物理后验数值必须从 OpenROAD 日志直取，不能用"看起来像 WNS"的行（LOG-20261024-06）

OpenROAD 的 `report_worst_slack -max` / `-min` 打印的是**两行不带 max/min 标签**的

```
worst slack -0.72      <- setup WNS (max)
worst slack 0.47       <- hold min slack
```

而 OpenSTA 打印的是**带标签**的 `worst slack max X` / `worst slack min Y`。因此任何
`line.startswith('worst slack')` 的提取器，**在 OpenROAD 日志上必然抓到第二行**（除非再加
`max`/`min` 判别或"取 TNS_END 之后第一行"）。本次即栽在这里：`scratch/crossbench_physical_summary.py`
用 `startswith('worst slack') and 'max' not in t`，把 hold min slack 当成 setup WNS，于是
ITC-99 跨基准的 post-route 增益几乎全变成 0，得出"物理后收益几乎全丢（保持率约 2%）"的
**假结论**；从归档日志直取后重算是 **约 96% 保持率**。同仓库的
`scratch/iscas8_pre_post_table.py` 已在注释里写明这个坑并显式区分两行，所以 ISCAS89 侧未受影响。

**教训**：① 同一份仓库里两个提取器对同一格式可以有不同的正确性，**不要因为"上一轮跑过"就
信任产物**，引用任何数字前必须回到原始日志核对；② 自制提取器必须有**交叉校验**（用两种独立
方法或与人工读日志对拍），否则一个 20 字符的判别式错误能翻转整篇结论；③ 结论方向与预期相反
时先怀疑提取器（实现问题），再怀疑设定（想法问题）——本例即"实现问题，修正后原设定仍成立"。


## 2026-10-24 噪声底只能用"组内"散布：组间差异是信号不是噪声

**现象**：物理转移噪声底最初按"各电路实现间 ΔWNS 的标准差"汇总，并把组间（各电路 ΔWNS 均值
之差）也算进池化，得到 σ ≈ 0.12 ns。若拿它当阈值（2σ = 0.25 ns），全部已报告效应
（0.01–0.61 ns）都会被判成不显著。

**归因**：Δ(电路 c, 实现 j) = μ_c + e(c,j)。μ_c 是该电路**真实**的 post-route 效应——b03 真增益
0.51 ns、b02 真增益 0.02 ns、s27 真增益 0.11 ns，电路之间差一个数量级是**效应量本身的差异**，
是**信号**；只有 e 才是"同一网表换物理实现"的测量噪声。把 μ_c 的离散度并进阈值是类别错误，
不是"更保守"。

**处理**：噪声底取**组内**跨实现的散布，σ_w = Σ(n_c−1)s_c² / Σ(n_c−1) = **0.028541 ns**
（95% CI 0.020818–0.036623，自举 2000 次，12 电路 / 48 配对）；组间单独报告并显式标注
`sigma_between_is_signal`。每电路只有 3–6 个实现，样本 1σ 相对误差 40–70%，不能直接当阈值，
故用 James–Stein 式收缩 σ_c² = ((n_c−1)s_c² + σ_w²)/n_c。

**教训**：① 做噪声底时**先问"这个离散度是随机的还是被测量的"**——同网表跨实现是前者，
跨电路是后者；② 小样本方差必须收缩，不能直接当阈值；③ 池化方差要按自由度加权
（Σ(n_c−1)s_c²/Σ(n_c−1)），不能对各电路方差取算术平均再开方（忽略了实现数不同）；④ 噪声底
变大不会让结论更"安全"，只会让它失去判别力——阈值必须落在效应量尺度上才有意义。


## 2026-10-24 跨电路相关会骗人：决策相关的相关必须轮内计算

**现象**：用代理模型原型的特征与 post-route 增益做相关，先在**全池**（跨电路）算出
`proxy_score` ρ = +0.327、`critical_path_coverage` ρ = −0.358、`strategy_priority` ρ = −0.422，
一度据此写下"代理目标与物理结果反向相关"的结论；加做**轮内（同一电路内去均值）**检验后，
三者分别变成 ρ = −0.058 / +0.035 / −0.089，即**轮内几乎全无信号**。

**归因**：全池相关被**电路间尺度差异**主导——大电路的理想增益、post-route 增益和特征量级都更大，
池化后每个特征在不同电路上取不同的符号，相关系数变成跨电路的比较而非同电路内的预测力。
而 FAECO 的实际决策是**在同一轮候选池内挑一个**，轮内相关才是决策相关的量。

**处理**：凡"这个特征能不能预测另一个量"的结论，必须同时报**整体 ρ 与轮内 ρ**，并以轮内为准；
决策质量用**轮内遗憾**（oracle 最优 − 所选候选的真实收益）度量，比相关更贴近后果。

**教训**：① 先问**这个相关对应的是哪一次决策**——决策发生在哪个粒度，相关就必须算在哪个粒度；
② 整体与分组结论冲突时，通常不是数据矛盾而是口径问题，必须把两种口径都写出来而不是挑一个；
③ "整体负相关"和"轮内零相关"可以同时成立，此时"负"是假象、"零"才是事实；
④ 我自己写下的中间结论也必须回头核——本例先写下"代理目标反向"，核完后改为"轮内无信号"，
两者方向一致但**数值与机理不同**，不能只凭方向一致就跳过更正。


## 2026-10-24 台账里的"基线"要先核实是哪一层基线

**现象**：候选级数据集需要把"理想线网边际增益"与"post-route 边际增益"对比，但台账
`acceptance_evidence.metric_references.setup_wns` 到底指**原始基线**还是**本轮基线**，若指原始
基线，则理想侧是累积量、物理侧是边际量，两者不可比——整个相关分析会失效。

**核实**：逐轮读 s27 台账，引用值随接受链递推：iter1 引用 −0.27（= 原始基线），iter2 引用 −0.19
（= iter1 接受候选的 WNS），iter3 引用 −0.18（= iter2 接受候选的 WNS）。故它确为**本轮基线**，
`ideal_delta_wns` 是**边际**量，与 post-route 边际增益同口径。

**教训**：① 从台账/日志取"基线"时，先用**递推自证**（第 2 轮引用的值是否等于第 1 轮接受候选的值）
确认层级，再动手算差；② 同一个字段名在不同族可能含义不同（主族的 `physical_*` 全为 None，
L1 物理通道在另一族），不要跨族借用语义；③ 边际/累积混比会造出"所有候选都改善 0.11 ns"这种
整体平移的假象（本项目此前已踩过一次），本次先核实口径再建数据集，避免重蹈。


## 2026-10-24 布线违例计数要读"最终值"，不是峰值

**现象**：写完违例普查脚本后第一次跑出"293 个运行里 249 个有布线违例"（s641 106/106，
峰值 176），结论像是"绝大多数标签来自没布干净的网表"。

**核实**：打开一个 s641 的原始日志看尾部，发现 OpenROAD 的 `detailed_route` 在**每次**优化迭代
后都打印 `[INFO DRT-0199] Number of violations = N`，该计数在搜索过程中上下波动
（36 → 4 → 0），最后一条 `Number of violations = 0` 之后才是
`[INFO DRT-0198] Complete detail routing.`。也就是说交付的布线是干净的，
中间峰值只是搜索过程的历史。

**改正**：普查脚本改为取 `Complete detail routing` 之前的**最后**一条 `DRT-0199`
作为最终违例数，峰值单独列作参考。改正后：**293 个完成布线的运行，最终违例数全部为 0**，
所有标签都来自干净布线。

**教训**：① 计数器类日志必须区分"过程量"与"终态量"——**峰值不等于结果**；
② 拿到"大面积异常"的普查结果时，先抽查一两个原始日志确认语义，再决定要不要报警；
③ 同一个"违例"概念在 OpenROAD 里至少有两个来源（`Completing N% with M violations`
与 `DRT-0199 Number of violations`），前者是搜索进度，后者才是交付状态。


## 2026-10-24 噪声底必须按基准族分带，跨族池化会同时压窄一族、放宽另一族

**现象**：噪声底族共 15 个电路（8 个 ISCAS89 的 s\* + 7 个 ITC-99 的 b\*），早前把它们的组内
方差池化成一条 σ_w = 0.028862 ns 供两族共用，候选级判定、校准的 2σ、候选级带的比值全用它。

**核实**：把同一套口径**分族**重算：ISCAS89 本族 σ_w = **0.023536 ns**（8 电路 / 46 配对，
CI 0.018886–0.028074），ITC-99 本族 = **0.039881 ns**（7 电路 / 21 配对，
CI 0.025166–0.051177）——**两族相差 1.71 倍**（1.38 是各族对**跨族池化值**的比值，不是两族之比；池化值 0.028642 对 ITC-99 偏窄 28%，对 ISCAS89 偏宽 19%）。池化值对 ITC-99 偏窄 28%（会把噪声带内的
边际增益误判成"已确认"，**制造假确认**），对 ISCAS89 偏宽 18%（**掩盖**真实退化）。

**改正**：`noise_model.py` 增加 `per_family` 拆分；每电路的 James–Stein 收缩目标从"跨族池化值"
改为"**族目标**"（保留 `sigma_shrunk_pooled_all` 作对照）；两个族的判定阈值一律用本族 σ_w。

**连带更正**：分族后 ISCAS89 的反事实判定由 GAIN 8/REGRESSION 0/INCONCLUSIVE 13 变成
8/1/13——**带的选择会改结论**，任何"REGRESSION 为 0"的说法都必须声明用的是哪条带。

**教训**：① **分族记录不只适用于结论，也适用于阈值**——阈值也是族相关的量；
② 池化只有在"各成分同分布"时才安全，实现敏感度显然不是；
③ 跨族池化最危险的方向是**压窄**（假确认），不是放宽；④ 换一个分母，**比值的符号都可能反**
（候选级带/σ_w 由 0.88× 变成 1.21×，"继承带偏保守"变成"继承带偏窄"）。


## 2026-10-24 同一张网表在两个物理实现下都有行时，按键匹配会跨实现取错标签

**现象**：反事实接受分析突然只剩 22/27 条决策有标签（此前更多），而数据集里明明有
post-route 标签。

**归因**：数据集现在同时含 F0 与 F1 两批的**同一批候选网表**。反事实工具按
`(iteration, instance, kind)` 建索引、在里面挑"ideal WNS 匹配的第一行"——于是挑中的可能是
F1 批里那条（`post_status=failed`，或尚未跑）。s713 更是叠了一层：F0 批因 `DRT-0305` 全失败，
标签在 S713R 批（修复网表），键相同。

**改正**：索引**只收 `post_status == ok` 的行**，并在同键多行时**优先取主实现批次**
（`LABEL_BATCHES`），"同轮最优候选"的比较也限定在同一批内（否则会跨实现比较）。
改正后 ISCAS89 **22 → 26** 条有标签，ITC-99 **0 → 38** 条。

**教训**：① 一个键在多批次数据集里**不再唯一**，任何"取第一条"的写法都要先问"哪一批"；
② 补跑一个实现会**污染**已有分析的取行逻辑，必须回头复核所有按 (circuit, key) 或
(iteration, instance, kind) 建索引的工具；③ 这类 bug 表现为"标签变少"，很容易被误读成
"批次没跑完"，而真实原因是**取错了行**——看到标签数下降要怀疑索引而不是进度。


## 2026-10-24 计数器类日志：代码必须真的按文档取终态，不能只改文档

**现象**：违例普查报告"F1/s953 有 1/6 跑次最终违例 8"。原始日志显示那些跑次的
`Complete detail routing` 之前的最后一条 `DRT-0199` 都是 0。

**归因**：脚本的文档写的是"取 `Complete detail routing` 之前最后一条"，**实现却取全文最后一条**。
被超时杀掉的跑次在搜索中途留下 `Number of violations = 8`，就成了它的"最终违例数"。
即：**上一轮登记的"要读终态"这条教训，代码本身并没有落实**。

**改正**：按文档意图实现（`Complete detail routing` 标记之后的行不再覆盖计数），
并把"未完成布线"与"完成但有违例"**分开统计**。改正后 412/413 个完成布线的跑次**全部 0 违例**，
唯一未完成的是超时被杀的那一个。

**教训**：① **改了文档不改代码，等于没改**——上一轮"经验"只写了"要读终态"，没落到实现上，
于是同一个坑又踩了一次（这次是实现错、文档对）；② 报告里"大面积异常"要能追到**单个原始日志**
并区分"过程量"与"终态量"；③ "未完成"与"完成但不合格"是两类，必须分列，否则会把
"没跑完"误报成"跑坏了"。


## 2026-10-24 硬编码的结论文案会与数据自相矛盾，结论必须由数据生成

**现象**：报告里写着"已标注的接受决策**没有一条**被物理证据判定为有害"，而同一段的数字是
`REGRESSION = 1`；又写着"残余差异**几乎全部是物理测量噪声**"，而残差 sd 已是 σ_w 的 1.36 倍；
还写着"斜率 ≈ 0.91"，实际是 0.86。

**归因**：这些文案是早期版本手写的，**没有跟着产物更新**。分族带、匹配修复、批次补全每一次都
改变了数字，只有数字是自动生成的、文案是手写的。

**改正**：`make_report.py`、`sync_status_docs.py`、`gen_r30_handoff.py`、`append_log_11.py`
里的**全部结论文案**改为由产物计算（例如 REGRESSION 计数决定"没有一条"还是"有 N 条"；
残差/σ_w 比值决定"几乎全是噪声"还是"还有一块未被噪声解释的差异"）。数字变了，文案自动跟着变。

**教训**：① **数字自动生成 ≠ 结论自动生成**——后者最容易被漏掉，且一旦数字变了就会当场自相矛盾；
② 报告生成器里凡是出现"没有/全部/都是/均"这类**全称判断**的地方，都必须能从数据推出；
③ 发现矛盾时，**先改生成器**再重跑，不要手工改产物里的文案。


## 2026-10-24 "判据错了"和"测不出来"必须分开：接受门槛可能低于测量分辨率

**现象**：反事实分析给出大量 INCONCLUSIVE，容易被读成"物理证据推翻了接受决策"。

**核实**：把决策的**理想增益**与物理测量的**分辨率**直接对比：FAECO 接受任意理想的严格改善
（报告分辨率 0.01 ns），而物理测量的 2σ 是 0.047–0.057 ns。22 条已标注决策里
**15 条（68%）的理想增益本身就低于物理分辨率**（中位数仅 0.020 ns）——对这些决策，
物理证据**在原理上**就无法确认或否证；唯一被判物理退化的那条（s832 第 3 轮）理想增益恰好是
0.01 ns、物理余量只有 0.0056 ns（约一个 0.01 ns 刻度），在更宽的候选级带下即判为 INCONCLUSIVE。

**改正**：新增 `tools/resolution_analysis.py`，把每条决策的"理想增益 vs 两条带""退化判定的物理余量"
逐条列出，报告里单列一节（6.4）。

**教训**：① **INCONCLUSIVE 不是失败的证据**，也不等于"效应不存在"；要问"这个效应**本原理上**
能不能被测到"；② 判据的**接受门槛**与测量的**分辨率**是两个独立的量，门槛低于分辨率时，
"评估器无用"是错误归因，正确说法是"评估器在仪器分辨率以下做判决"；③ 判为退化的结论必须附
**余量**，一个 0.0056 ns 的余量只是一个刻度，不能当作系统性证据。

## 2026-10-24 共用 run 目录的多作业表：后跑的表会静默覆盖先跑的表

**现象**：噪声底族有 8 张作业表（`jobs.tsv` / `jobs_patch.tsv` / `jobs_patch2.tsv` / `jobs_r4.tsv` /
`jobs_r4lo.tsv` / `jobs_itc99.tsv` / `jobs_r1test.tsv` / `jobs_smoke.tsv`），全部写进**同一个**
`runs/<key>` 目录。键的命名是 `<电路>_<baseline|fixed>_<实现>`，于是同一张网表的同一个实现
只要被两张表声明，就只有**最后一次**写入的结果存活。

**核实**：33 个键被多表声明，其中 16 个的**实现参数不同**（R1：met2/met3 vs met5/met4；
R4：util 25/5 vs util 40/20）。用两条独立证据判定存活者：① `log/master_<batch>.log` 的逐作业
行给出批次成员关系，键在多批出现时取最后那批；② 各表**独占键**的日志 mtime 给出执行窗口。
两条证据一致：`jobs_patch2.tsv` 批（10:39–11:32）覆盖了全部 16 个 R1 键与 16 个 R4 键。
存储的测量因此**不带任何实现参数痕迹**——看到 `runs/s27_baseline_R1/` 无法知道它是 met2/met3
还是 met5/met4 的那次跑。

**改正**：① runner 每个作业在 `rc.tsv` 旁写 `impl.tsv`（含全部实现参数与批次标签）；
② 新增归属脚本，用上面的双证据把 138 个历史作业回填归属并产出 `run_attribution.json`；
③ 噪声模型新增 `pairing_audit`，把"配对的两侧是否共享同一实现"变成**每次重算都自动检查**的项。

**教训**：① **共用 run 目录的多作业表必须给键带上"实现身份"，否则后来的表会吃掉前面的结果**；
更稳的做法是键里带实现指纹，或每张表用独立 OUTDIR；② 覆盖发生后"哪一份存活"要靠
**批次日志 + 时间戳**回溯，不能靠表名猜；③ 只要测量结果没有把产生它的**配置**一起存下来，
数据集就等于不可审计——溯源信息要写进产物，不是写进脚本注释。

## 2026-10-24 配对的前提必须审计：共享实现才抵消实现系统偏移

**现象**：噪声底的核心量是配对差 δ(c,j) = fixed(c,j) − baseline(c,j)。它成立的**前提**是
baseline 与 fixed 共享同一套物理实现，实现的系统偏移在配对内抵消。

**核实**：共用 run 目录使这个前提不再自动成立——理论上可能出现 baseline 来自 met5/met4、
fixed 来自 met2/met3 的配对，那样的 δ 里混进了实现差，会**污染**噪声底。加 `pairing_audit`
后实测：67 对中非零 rc 0、实现不匹配 0、缺溯源记录 0 → 前提经审计成立。

**教训**：配对类统计量要**显式审计配对前提**，并把审计结果放进产物（`pairing_audit`），
让任何一次重算都能复核；这与"键在多批数据集中不再唯一"是同一类错误的两个面：前者是
**跨实现取错行**，后者是**跨实现配错对**。

## 2026-10-24 利用率的方向：util 越高，核越小，电源条越放不下

**现象**：给 s27 补 R4（密度上臂）时，先按 util 20 跑，OpenROAD 报
`PDN-0185 Insufficient width (22.54 um) to add straps on layer met4 ... total strap width 15.17 um
and offset 13.57 um`；第一反应是"核太小 → 提高利用率给条带腾空间"，于是改成 util 40，
结果核宽反而变成 **15.64 um**，PDN 依旧失败。

**改正**：核宽随 util **递减**（util 20 → 22.54 um，util 40 → 15.64 um）；met4 主条带需要
`offset 13.57 + strap 15.17 = 28.74 um` 的核宽，所以 s27 在这条臂上**物理不可行**。
而能跑通的 util 5 与 s27 的 R4lo 同参、util 10 与 R0 同参 → 补出来只会是**重复样本**，
还会往 σ_w 里塞一个 0 方差观测。最终把 s27 R4 记为"尝试过且物理不可行"。

**教训**：① **改参数前先确认参数的方向语义**——"利用率"对版图尺寸的作用方向与直觉相反时，
先量两次（util 20 / 40 的核宽都留了证据）再决定第三次怎么改；
② **补洞时如果唯一"可行"的取值会造出重复样本，正确做法是把它记成负结果**，而不是硬补；
负结果也是数据集的结论，只是要带证据（PDN 报错原文 + 两次实测核宽）。

## 2026-10-24 物理阶段会退化成"上一阶段的重复测量"：寄生估计惰性比缺数据更危险

**现象**：要给"理想线网 → 布局后 → 布线后"补中间一档，于是照着 post-route 的 flow 写了个
布局后脚本（去掉布线、改用 `estimate_parasitics -placement`）。跑出来一看，
布局后的 setup slack 与**理想线网的值逐字相同**（-0.19 / -0.20 / -0.18 / -0.26，
83/83 个候选完全一致），相关系数 ρ = 1.0、衰减斜率 = 1.0——一个物理测量不可能这么完美。

**核实**：日志里其实已经写了 `[WARNING RSZ-0018] wire capacitance for corner default is zero.
Use the set_wire_rc command to set wire resistance and capacitance.`。OpenSTA 没有线 RC，
就没有任何连线延迟可加，`estimate_parasitics -placement` 于是什么都没估出来，
整档测量退化成"零线延迟的理想线网"的重复测量。

**改正**：估计前 `set_wire_rc -layer met2 -signal` / `-layer met4 -clock`（值取自平台 LEF）。
改完同一批网表给出：理想 -0.19 → 布局后 -0.22 → 布线后 -0.25，三点分开。
另做过**逐层标定**（met1–met5）：布局后结果 -0.22…-0.23，RC 层选择影响 ≤0.01 ns，
远低于物理分辨率带，说明这个建模选择不是实质不确定性。

**教训**：① **"跑出来了"不等于"测到了东西"**——一个阶段如果测出的量恰好等于上一阶段的量，
它多半是**退化**而不是**完美**；看到 ρ=1.0 / 斜率=1.0 要先怀疑口径，而不是当成好消息；
② 中间物理阶段**必须自己确认它带了新的物理量**（本例的判据是连线延迟是否非零、
路径报告里是否出现连线段），并把"这一档的估计模型与上一档有什么不同"写成必须随数字走的警告；
③ 工具日志里的 WARNING 是**口径缺陷的第一手线索**，要逐条读，不要只看 rc。

## 2026-10-24 同族比较必须同量纲：边际与累积不能交叉

**现象**：写三点曲线工具时，先把布局后的**累积**增益（候选对电路基线）去比布线后的**边际**
增益（候选对它所派生自的那张网表），结果 ρ(理想, 布局后) = 1.0、均值 +0.092 vs -0.003，
一眼就不对。

**改正**：数据集里同时有**边际**（一次替换的效果，对派生自的网表）与**累积**（对电路基线）两列，
三点曲线的每个阶段都必须**各自同口径**：边际量三段比边际量，累积量三段比累积量。
修正后得到合理的形态（理想 → 布局后 → 布线后逐段衰减）。

**教训**：① 一个数据集里同时存在"边际/累积""绝对/相对"这类同族量时，
**做跨阶段比较前先确认量纲一致**，并且把"比较的是哪一列"写进工具的输出与报告；
② 工具同时输出两列时，报告只能引用与其它阶段同列的那一列。

## 2026-10-24 交叉验证里 one-hot 词表必须在切分前固定

**现象**：代理模型原型工具（留一电路交叉验证）在某轮数据上崩了：
`ValueError: operands could not be broadcast together with shapes (19,12) (13,)`。

**原因**：`build_matrix()` 的 one-hot 类别词表是**按传入的行子集**算的，于是留出的电路若不含
训练集里的某个 kind，测试矩阵就少一列，归一化向量对不上。

**改正**：词表在**折外**固定一次（全局 `kinds_all`），并在每折加一道列宽断言。

**教训**：交叉验证里的编码（one-hot、标准化、缺失值填充策略）必须在**切分之前**确定，
否则编码本身会携带折之间的信息或让折之间的形状不一致；这类缺陷在数据凑巧时不会暴露，
一换数据集就崩。

## 2026-10-24 跨阶段比较前必须先证明"同一个网表"

**现象**：三点曲线（理想 → 布局后 → 布线后）第一版把 s713 的布局后档（跑未修复网表）
与布线后标签（跑 tie 单元修复网表）放在一起比。两者不是同一个网表，
但**没有任何报错**：修复是逻辑等价的，而布局后阶段不布线，坏网表在那一档照样跑通。

**改正**：新增守卫 `tools/check_netlist_consistency.py`，逐候选比对网表路径与 sha256，
**自动推导**每个电路该用哪张作业表；分析工具从守卫产物取数，守卫不通过就**拒绝出数**。

**教训**：① 跨阶段/跨批次的比较，前提是各阶段测的是**同一对象**；
这个前提**不能靠"它们看起来是同一个电路"**成立，必须有可自动核对的证据；
② **逻辑等价的修复会静默改变物理量**——它不改功能，但会改单元数、版图占用与时序；
③ 守卫必须**先于**分析工具运行，且分析工具要在守卫失败时**拒绝出数**，
否则守卫只是个摆设。

## 2026-10-24 "缺陷真实存在"与"数值影响大"要分开报

**现象**：修完网表不一致后，s713 的布局后绝对 WNS 有 23/30 个键变化（最大 0.05 ns），
但三点曲线的 ρ 与斜率几乎没变。

**原因**：修复带来的是电路级**公共偏移**，在**边际**量（候选对它派生自的网表）里抵消。

**教训**：报告缺陷修复时**两个量都要给**——① 缺陷是否存在（29 个候选的真实不一致）；
② 数值影响多大（最大 0.05 ns、相关性几乎不变，但 2σ 带由 0.042876 变 0.04836 ns）。
只报"影响很小"会让人以为当初可以不查；只报"缺陷很大"则是夸大。
**阈值变了就是变了**，哪怕相关性没变。

## 2026-10-24 汇总/普查文件不能被部分模式覆盖

**现象**：随手跑 `rc_census.py labels` 后，噪声族与 ITC-99 族在 `rc_census.json` 里消失，
下游日志脚本读同一个文件，渲染出"噪声底族共 0/0 作业跑完"。

**改正**：`rc_census.py` 永远写入**全部族**的普查，命令行参数只决定打印范围。

**教训**：作为**下游输入**的汇总文件，其内容不能随"查看某一部分"的命令而变；
过滤只应发生在**呈现层**，落盘的文件保持完整。

## 2026-10-24 测量的报告粒度是一层噪声底：0.00 不等于"没有影响"

**现象**：给 ITC-99 族写三点曲线时，布局后档的候选级边际增益**每一个都恰好是 0.0000**
（布线后档同样有 8/44 条恰好为 0）。第一反应是"这一档饱和了"——比如 setup slack 被时钟路径
钉死，候选怎么改都不动。

**实查**：不是饱和。OpenSTA 的 `report_worst_slack` 只打**两位小数**，
所以任何候选级边际量都被**量化到 0.01 ns**。逐键对拍可见布局后档的 delta 有 0.00 / +0.01 /
-0.01 三种取值，布线后档同量级——都是量化台阶，不是"没有效应"。

**后果**：① 报告里写"0"时必须理解为"低于报告粒度"，不能写成"没有影响"；
② 边际量的**最小可分辨单位是 0.01 ns**，所以以 0.01 ns 分辨率比较两个阶段的边际量时，
本身带着 ±0.01 ns 的量化噪声；
③ 量化是否"卡脖子"要看带：ITC-99 本族候选级 2σ = 0.0875 ns ≈ 9 个量子，
ISCAS89 本族 2σ ≈ 0.055 ns ≈ 5 个量子，**带比量子宽一个量级**，所以量化不决定三档判定。
但如果将来用更小的带（例如某电路的分辨率远细于 0.01 ns），量化就会变成主导误差项。

**教训**：任何"差值恰好为 0"的观测，先查**报告精度**，再谈饱和；
差值的最小非零步长 = 报告精度，它是一层**隐含的噪声底**，必须与显式的 σ_w 一起写进边界。

## 2026-10-24 三档判定必须按"理想线网是否接受"拆开统计

**现象**：做统一训练表时，把每个候选的三档判定统计出来，得到的数字很难看——
全部候选里 REGRESSION 77（噪声底族带）/ 63（候选级带），即"约四分之一的候选物理上退化"。

**归因**：三档判定是按**该候选自己的边际量**算的，而候选集里绝大多数本来就被理想线网
**拒绝**。对它们，"边际量为负 → REGRESSION"只是把"理想线网拒了它"重说一遍，
不构成任何新信息。把"物理上退化"的**修辞**套到一个本来就被否掉的候选上，
会凭空制造出一个 25% 的"退化率"。

**改正**：按 `accepted_ideal` 拆成两个总体再统计：
- **被接受的候选**：REGRESSION = "接受是错的"（这才是要盯的数）；
- **被拒绝的候选**：REGRESSION = "拒绝是对的"，GAIN = "漏掉的真实改善"。
拆开后，被接受那一侧的计数与"反事实接受分析"**口径一致**（后者统计接受决策，不是候选）。

**教训**：① 任何"退化率/成功率"式统计，先问**分母是什么**；
同样的判定列，换一个总体就会得出完全不同的结论；
② **"被拒绝的候选"与"被接受的决策"是两个不同的总体**，计数不可互相替代，
报告里必须写明用的是哪一个；
③ 数据集交付时**判定列必须与"是否被接受"这类分组列并列**，
否则下游很容易把它们混起来读——这正是统一训练表把 `accepted_ideal` 放在同一行的原因。

## 2026-10-24 小样本下的模型比较必须逐电路配对，池化指标说明不了问题

**现象**：跨阶段代理实验里，"用布局后标签训练"与"用布线后标签训练"对布线后标签的
池化 Spearman 分别是 0.6477 与 0.6515，差 0.004 量级——看起来"布线后标签也许多一点点"。

**为什么池化差值不可用**：留一电路交叉验证只有 8 个折，池化值把折间方差完全抹平；
0.004 的差可能只是某一个电路拉动的结果。

**改正**：改做**逐电路配对**——同一个被留出的电路上，哪个格子的 Spearman 更高，
记一次 win。结果：布局后 vs 布线后训练 **4 胜 4 负**，
理想 vs 布局后训练 **1 胜 7 负**。

**教训**：① 折数少时，**池化 Spearman 差值一律不作为结论**，只报逐电路配对；
② 配对比较要报 wins/ties/losses 三个数（胜负分布本身就是证据）；
③ 结论用"无差别"而不是"略差"——当配对是 4:4 时，"略差"是过度解读。

## 2026-10-24 监督信号的成本决定实验能不能做：中间物理档可替最终物理档

**现象**：造"每改一次跑一次真实 Post-Route STA"的训练集时，布线后档每个候选要 ~515 s，
布局后档只要 ~2 s——两者差两个数量级。如果监督信号必须来自布线后档，
数据集规模就被物理成本卡死。

**实查**：用同一批候选、同一批折训练，比较"用布局后标签训练"与"用布线后标签训练"
对布线后标签的预测能力，逐电路配对是 4 胜 4 负——**没有差别**；
而"用理想线网标签训练"明显更差：布局后 vs 理想是 1 胜 7 负，布线后 vs 理想是 2 胜 6 负。

**含义**：**监督信号可以由便宜的中间物理档产生**，最终物理档的标签不必进入训练集；
最终物理档的价值转为**评测集**（用来验收模型），而不是训练集。
这让"几千次真实 ECO + 真实 Post-Route STA"的数据集构造从"跑不动"变成"可跑"。

**教训**：① 造数据集前先量**每一档监督信号的单候选成本**，成本差异会改写实验设计；
② "中间阶段能否替最终阶段"是一个**可测的配对问题**，不要凭直觉断言；
③ 替得了监督 ≠ 替得了评测——最终档仍然要留一部分做独立的验收。

## 2026-10-24 学习模型未必打败简单基线：收益可能在成本而不在决策质量

**现象**：跨阶段代理模型在**决策遗憾**上与"理想线网 argmax"打成平手（同池平均遗憾 0.007222 vs 0.007222），并没有像预期那样选得更准。

**但**：把模型用在**筛选**上（模型排序，只验前 50%，验完取最好的），
平均遗憾 0.002692、最差 0.03，布线后 STA 调用省 47.95%；
而全量验证下的 ideal_argmax 平均遗憾是 0.014231。

**结论**：这个场景下学习模型的**可测收益是省验证成本，不是选得更准**。
诚实的写法是把这个收益如实写出来，而不是把"代理模型有用"写成泛泛的结论。

**教训**：① 当代理模型打平简单基线时，**先找它的成本优势**，而不是硬吹精度优势；
② "打平"本身是结果，要如实报（含同池比较的数字）；
③ 用**同一批池**比较不同选择器，否则各选择器的可用池数不同，数字不可比。

## 2026-10-24 同一条"带"的不同聚合口径会给出不同判定，判定必须带口径

**现象**：写带敏感性工具时发现，同一个族里"候选级带"其实有两个来源：

- **族池化**：2σ = 0.055542 ns（全部电路的配对网表池化，三点曲线与训练表用这个）；
- **逐电路**：数据集每一行里的 `cand_threshold`（该电路自己的配对网表估计，rejected_side 等工具用这个）。

两者**判定不同**：被接受的候选在候选级带上，池化口径 GAIN/REG/INC = 7/1/18，逐电路口径 = 11/0/15；翻转候选：噪声底族带 22 条、候选级带 49 条。

**为什么会有这个问题**：工具是分批写的，每批各自挑了一个"看起来对"的带，**没人把两套口径放在一起对拍**。两套都不是错的——池化稳、逐电路贴合本电路——错在**名字相同、口径不同**，于是同一个问题在不同工具里得到不同答案，而且**没有任何报错**。

**教训**：① 任何"阈值/带宽"类量，**必须把聚合口径写进名字或列名**（本次改成 `*_pooled` / `*_perckt`）；
② 同一族里出现**第二个**阈值来源时，要主动做**跨工具对拍**，而不是各自跑各自的；
③ "是否退化""是否显著"这类结论**必须写明带的口径**，否则换个工具就自相矛盾；
④ 小样本电路的逐电路估计**方差大**（本族逐电路的候选级带每个电路只有 **6 对**配对网表（df=5），池化用 **48 对**（df=40）；s832 的逐电路 2σ 因此达 0.0847 ns、是池化值的 1.53 倍，s713 是 0.0744 ns、1.34 倍），这类电路用池化带更稳；
⑤ 注意**总计数相同不代表判定相同**：翻转可能互相抵消（本族噪声底族带在被接受侧两口径计数相同，但仍有 4 个候选翻转了档）。

## 2026-10-24 去重规则会静默换掉溯源锚点：优先保留"带产物"的那一行

**现象**：统一训练表按"每个候选键取第一行"去重。s713 的候选在 F0 与 S713R（tie 单元修复批）各有一行，F0 那行**没有标签**（未修复网表不可布线），于是 23 个**有标签**的 s713 候选被挂上了**未修复网表的 sha256**，阈值列全为 null，`label_batch` 写成 F0——标签来自修复网表，溯源锚点却指向未修复网表。

**为什么没被发现**：训练表的标签是从三点曲线取的（曲线按"有标签"筛行，是对的），所以**标签本身正确**；错的是同一行上的**元数据**。也就是说：**数值对、溯源错**，这种错误不会被数值检查抓到。

**改正**：去重规则改为"**优先保留带标签的那一行**"，并让所有下游工具用同一规则；两工具的接受侧计数随后逐候选一致。

**教训**：① 去重规则要按**产物完整性**定（哪一行带标签/带结果），不能按"先来后到"；
② 从别处取标签、从本地取元数据的表，**必须逐行核对两者出自同一行**——否则会出现"标签对、锚点错"的静默不一致；
③ 交付数据集时，行内的溯源锚点（网表哈希 / 批次名 / 阈值）**必须与该行的标签来自同一次运行**，这条要有自动检查，不能靠人记。

## 2026-10-24 反馈机制"没用"要先看它实际拿到的信号是什么

**现象**：论文的 F1-F6 失效反馈按失效类型调权重，自适应版本没有收益。常见猜测是"候选空间太死板、换汤不换药"。

**实查**：归档账本里**只记录了一种失效事件**（`acceptance_budget_violation`，201 次），而且它**只在理想判据已经拒绝的候选上触发**（理想增益 ≥ +0.02 ns 的带事件候选有 0 个）。在同一个理想增益带内做对照，它还能分开布线后结果，但只分开约 0.019 ns，远小于候选级 2σ 带。

**归因**：这条信号**近似等于理想判据自身的裁决**（一位信息）。一个拿一位信息去调权重的机制，相对"已经知道理想增益"的基准**没有可加的信息量**——所以"自适应无收益"是**信号不足**的直接后果，不必假设候选空间有问题。

**教训**：① 评价任何反馈机制前，先查**它实际收到的信号**（种类数、触发条件、与判据的独立性），而不是先假设机制设计有问题；
② 检验"新信息 vs 同义反复"要用**同一个判据值分带后的对照**，整体均值差会被判据本身混淆；
③ 顺带确认"结构特征可获得性"：本归档里 `topology_metrics` 与电气度量全为 null、且候选**全部**落在关键路径上 → **现有归档做不了 GNN**，要得上结构特征必须新抽取。

## 2026-10-24 检验"结构有没有用"之前，先问这个族里有没有结构变化可测

**现象**：想回答"网表图里有没有物理信号"，就写了图特征 + 代理模型，ISCAS89 族跑出"结构特征 ≈ 随机"。

**实查**：ISCAS89 族的候选**全是单胞驱动强度替换**——`d_depth` / `d_n_cells` / `d_max_fanout` 三个拓扑 delta 特征**全是常量**（`structural_features_summary.json` 的 `constant_features` 明确列出）。后果有两层：① 该族"结构变化量"在 26 个候选池里**全部一致**，池内比较直接无定义（全部被排除）；② 该族任何"结构无信号"的结论都带**族特异性**，不能外推。

**教训**：① 设计"结构类"实验前，先查**这个族的候选到底改了什么**（改拓扑还是只换驱动），否则得到的是"族特异性"结论而不是结论；② 结构实验要有**一个拓扑会变的族**做对照，否则"没测到信号"无法区分"图里没信号"与"这个族没结构变化"；③ 把"常量特征"显式写进产物（如 `constant_features` 列表），比在报告里口头说明更耐用。

## 2026-10-24 决策指标要用电路内 ρ：pooled ρ 会被电路级常量特征抬高

**现象**：同一批数据，`graph:depth` 对理想标签的 pooled Spearman 是 **−0.4583**（看着像强信号），但它在每个电路内**是个常量**，电路内 ρ 根本不存在（0 个电路有变异）。

**原因**：pooled ρ 混合了"电路之间"与"电路之内"两种差异。电路级属性（depth / n_cells / max_fanout / n_primary_*）在电路内是常量，**不可能重排同一电路的候选池**，但能抬高 pooled ρ；而决策遗憾是**池内**的选型问题。

**教训**：① 代理模型的**主指标要用"池内/电路内"的 ρ**（本轮加了 `mean_per_circuit_spearman` 这一栏），pooled ρ 只能当辅助；② 每张特征表都要配一栏"**这个特征在几个电路里真正有变异**"，否则读者会把电路级常量当成可用信号；③ 线性模型里加一个电路级常量特征，**池内排序完全不变**（对所有行加同一个偏移），所以它只可能污染 pooled 数字，不可能提供决策信息——这一点可以直接说明，不必靠实验去证。

## 2026-10-24 累积量不能当单个候选的动作量：必须用池内离散度

**现象**：想用 `d_n_cells`（候选网表相对电路基线的单元数差）度量"这个候选改了多少结构"，结果它随迭代单调增长（kind R：iter 1–4 平均 0.00–0.67，iter 5–8 平均 3.46–4.92）——量到的是 **ECO 历史累积**，不是本候选的动作。

**为什么仍能用**：**同一池（同一电路、同一迭代）的候选共享同一迭代基线**，所以池内离散度 `d_n_cells(候选) − min(池内)` 恰好就是该候选自己的改动量。

**教训**：① 任何"相对某个基线"的差量，先查它**是否随流程累积**（看它与迭代号的相关），是则必须换成**同批比较的离散度**；② 同理适用于累积增益、面积增量、线长增量等一切 ECO 累积量；③ 把"为什么池内比较是干净的"写进工具的文档字符串，别只写在结论里——否则下一个人会误用原始值。

## 2026-10-24 跨类比较要控制选择偏差：判据按类拒绝的强度差异巨大

**现象**：按类统计物理结果时，ITC-99 的 R 类 mean_routed = −0.0698、G 类 = −0.0167，看起来"R 类差得多"。

**但这是选择效应**：理想线网对不同类的拒绝强度悬殊——R 被拒 306/321、B 被拒 343/354，而 G 只被拒 102/120；被拒候选本来就是差的那批，所以全样本按类平均是在比**两个不同总体**，不是比两种策略。

**改正**：改成**池内跨类配对**（同一池内两类候选被同时提出）：布线后 G vs R 10 胜 0 负 1 平 p = 0.0117、B vs R 10 胜 0 负 2 平 p = 0.0386、B vs G 无差别 p = 0.8036。

**教训**：① 任何"某类候选更差"的结论，都要先问**判据是不是按类筛过的**，是则必须做同池配对；② 报告里要同时给出"该类被接受/被拒的样本量"，让人能判断选择效应；③ 池内配对还能顺带暴露**理想线网判错在哪**：本例里 G vs R 在理想与布线后两个口径结论一致（都是 10:0:1），说明理想线网对"类"并没有误判。

## 2026-10-24 理想线网的"虚假繁荣"有了机理：它偏爱加逻辑深度

**现象**：池内比较"加逻辑深度最多的候选 vs 最少的候选"——理想线网口径 **12 胜 2 负 p = 0.0129**（显著偏好），布线后口径 **7 胜 2 平 5 负 p = 0.7744**（偏好消失）；而"加单元数"两个口径方向一致。

**解读**：理想线网没有寄生，加深逻辑层级只改变驱动关系，它把这当成收益；物理世界里加深层级意味着更长的连线与更多寄生，这个收益被吃掉了。**这是"理想线网虚假繁荣"从相关性走向机理的第一个可测证据**。

**如实边界**：两个口径之差**未做正式检验**（只是"一个显著、一个不显著"，不等于"两者之差显著"）；且布线后标签噪声受限（782 行里只有 183 行超候选级带），**衰减是可能的方向**，所以这是"与虚假繁荣一致"，不是证明。正确说法是"理想口径的偏好强度显著、布线后观测不到"。

**教训**：① 看到"一个显著一个不显著"时，**别写成"差异显著"**；② 机制类结论要同时给出机制方向（这里是什么量让理想线网高估）和它在物理上为何被抵消（寄生随连线长度增长）；③ 这种机理证据是**可复用的**：同样的池内配对协议可以直接用于检验别的"理想线网偏差维度"。

## 2026-10-24 把理想线网的时序信息喂给物理预测，会显著变差

**现象**：`cp_pos` / `cp_pos_frac`（被改单元在**理想线网**关键路径上的位置）看起来是最"有用"的结构特征——单变量电路内 ρ 对布线后标签 0.1076/0.1625。但把它并进特征集后，ITC-99 的逐电路配对变成 **0 胜 1 平 6 负 p = 0.0312**，**显著更差**。

**原因**：理想关键路径位置是**理想线网的时序信息**，它把模型拉向"理想线网认为好不好"，而那正是与物理脱节的方向。

**口径冲突（如实并列，不单取一边）**：同一格子的**决策遗憾反而更好**（0.0120/0.0082 vs 0.0140/0.0112）——全池排序质量变差、top-1 恰好更好，因为可用池只有 20 个且 b01 占 8 个。两个指标不能互相替代。

**教训**：① 特征"有没有用"和"用了会不会误导"是两回事：**理想线网的信息即使相关也可能有害**，必须实测；② 凡是从理想线网侧取来的特征（关键路径、slack 序、路径长度），在物理任务里都要**单独成组**并对照，不能混进"结构特征"；③ 指标之间冲突时，**两个都报并说明各自样本量**，挑一个讲就是选择性报告。

## 2026-10-24 阶段不足时让工具显式降级并喊出来，而不是静默替换

**现象**：ITC-99 的布局后档（真实 placement + CTS）刚跑完 1190/1207，训练表里布局后标签只有 6 行，而布线后已有 833 行。跨阶段代理模型默认要三阶段齐全，会直接报错退出——自动定稿链就会**断在中途**。

**处理**：给工具加 `--stages`（可指定子集）与 `auto`（三阶段行数不足时降级到 ideal+routed），并且**在报告里显式打印 `*** STAGES DROPPED : ['placed'] ***`**；同时把配对检验的格子对按"实际存在的格子"过滤（否则缺 placed 的运行会 KeyError）。另外把 `cross_kind` 等只在特定阶段下才有意义的分析块也一并做成条件块。

**教训**：① 自动化链路上任何"数据可能不齐"的环节，都要**能降级且把降级写进产物**，否则要么链断、要么出数但看不出少了什么；② 降级必须是**显式告警**而非静默替换（silent substitution 是最坏的一种）；③ 降级后新增的分析块要跟着条件化，不能让"某阶段缺了"变成崩溃。

## 2026-10-24 先量"可证明的改进空间"，再决定要不要换模型

**现象**：跨阶段代理模型给出"纯图特征预测物理收益 ≈ 随机"。本能的反应是"特征选得不好，换个更强的表示（真 GNN）再来"。但还有另一种可能：**标签本身在池级就分辨不出差异**，换什么表示都没用。

**实测**：把每个选择器对池内最大值的遗憾拆成"物理上可证明"（存在候选比所选候选好过判定带）与"落在噪声带内"两部分——
- **被接受候选（FAECO 实际做的事）**：ISCAS89 观测遗憾 0.0072 / ITC-99 0.0124 ns，**可证明部分 = 0.0000**；
- 对照"靠结构改动量选"：0.0762 / 0.1100 ns，**可证明部分 0.0673 / 0.0945**（真差）。

**解读**：这是**关于可证明性**的陈述，不是"FAECO 最优"的陈述。当前分辨率下**证明不了**有更好的选择，
所以任何模型都无从被证明更好。这把"该不该训 GNN"从口味变成了有测量依据的问题。

**教训**：① 评价任何学习方法之前，先问**"在当前测量分辨率下，改进能不能被证明"**——
   如果答案是不能，那么特征、模型、训练集都不是瓶颈，**测量才是**；
② 遗憾类指标要拆成"可证明 / 不可证明"两部分，否则读者会把噪声当成方法缺陷（或反过来把方法缺陷当成噪声）；
③ 拆完之后要**换阈值重算**（判定带 / 经验配对σ / 2×量化 / 带的一半），确认结论不是某一个带的产物。

## 2026-10-24 提高物理标签分辨率的最便宜手段是"同一网表跑两个物理实现"

**现象**：蒙特卡洛下界显示，单次测量下任何选择器都不可约地损失 0.0133（ISCAS89）/ 0.0493（ITC-99） ns；
**把同一候选在两个物理实现下各测一次并平均**，下界降到 0.0072 / 0.0311 ns。

**同时查到**：44 个真实双实现配对给出的经验单次测量 σ=0.0232 ns（ISCAS89 13 个配对给 0.0134），
分别是判定带/2（0.0437 / 0.0278）的 **0.53 倍 / 0.48 倍** → **判定带偏保守**，所以上界的下界偏悲观；
两组数都要列，不能只取一个。

**教训**：① "要不要上更强的模型"这个问题，往往先被"要不要多测一次"替代——**重复测量比换模型便宜且直接**；
② 用真实重复测量**校准**理论噪声模型（而不是只信模型假设），能同时发现"阈值太保守"这类问题；
③ 理论下界要**两个版本都给**：按假设 σ 的与按实测 σ 的，并说明哪个方向偏悲观。

## 2026-10-24 稀疏的重复测量要明说"还不能比"，不要硬凑一个结论

**现象**：想用真实的双实现配对做池内"平均两次测量 vs 单次测量"的比较，但 44 个配对候选**每个池只有 1 个**，
没有任何池能凑够两个可比的候选。

**处理**：如实写"**池内比较尚不可做**，须等第二批实现覆盖全族"，同时仍然给出**候选级**的可用部分
（经验 σ、|y1−y2| 分布）与**模拟**的池级下界，并标明哪些是估计、哪些是实测量。

**教训**：① 数据稀疏时，**把"能做什么/不能做什么"分列**，比给一个勉强的数字诚实且有用；
② 稀疏的重复测量仍然有用——它能**校准理论模型**（本例就发现了判定带偏保守）；
③ 每个数字都要能回答"这是测量还是估计"。

## 2026-10-24 结论会随扩样改变，发布前必须重算而不是引用旧值

**现象**：LOG-20261024-15 在**部分标注族**（20 池 / 833 条布线后标签）上得出"被接受候选的可证明遗憾 = **0.0000**"，这是一个很干净、很有冲击力的数字。扩样到 30 池 / 946 条后，它变成 **0.0033 ns（占观测遗憾 22.5%）**。

**处置**：核心结论（"可证明的改进空间比噪声高一数量级地小"）**保持**（对照组仍是 0.0753–0.0953 ns），但**"完全为 0"的说法作废**，改为"占 22.5%、绝对值 0.0033 ns"，并在 LOG-16 里显式写出这是对上一条的**口径更正**。

**教训**：① 批次在跑时出的数是**探针**，不是结论——**引用前先看批次是否已收齐**；
② "0.0000"这类极端读数尤其危险：它往往来自**样本没覆盖到反例**，而不是机制干净；
③ 数字变了而结论没变时，要**同时报告两者并说明哪一个作废**，不能默默改数；
④ 交接文档与登记条目要能看出"这条数是哪个标签集上的"（本轮把批次进度写进了每一段）。

## 2026-10-24 交叉验证的第二个族，往往能同时给出"更强"和"要修口径"两件事

**现象**：ITC-99 补齐布局后档后，892 个候选的三档校准与 ISCAS89 的 325 个**逐项一致**（布局后→布线后斜率 1.022 vs 0.964 ≈ 1；理想→布线后 ρ 0.703 vs 0.684），**跨族一致性成立**；但同一批重跑也让上一条的"可证明遗憾 0.0000"变成 0.0033。

**处置**：把"① 跨族一致性"与"⑤ 口径更正"**分开写**在同一条记录里，不让后一条抹掉前一条，也不让前一条掩盖后一条。

**教训**：① 第二个族的价值不只在"再确认一次"，还在于**它同时是独立复算**——用它同时**加强**结论和**修正**数字；
② 记录里要显式标出"哪几段是加强、哪几段是更正"，让读者能分别对待；
③ 族间一致时，**共用同一套口径**（同样的池定义、同样的带口径、同样的符号检验），否则"一致"没有意义。

## 2026-10-24 看到"零矛盾"先问是不是带宽造成的，再问是不是真的

**现象**：布局后档与布线后档的判定转移矩阵在两族都是**零矛盾**（没有一次"布局后说退化、布线后说增益"）。这看起来是个漂亮结论。

**反驳性检验**：把两档的判定带换成同一个带，矛盾立刻出现（ITC-99 19 例）；干脆不用带、只比符号，矛盾 73 例（8.2%）。**原因**：布局后的候选级带 0.024052 ns 比布线后的 0.087496 ns **窄 3.64 倍**，带宽不对称本身就禁止了大量翻转。→ **零矛盾是口径的产物，不是物理定律。**

**但一致性本身是真的**：加了**安慰剂对照**——把布线后标签在电路内置乱（保持两档各自的边际分布），矛盾数是 2 / 31 / 0 / 151（四个口径），**观测值 0 / 19 / 0 / 73 全部低于安慰剂下界**。没有这个对照，"一致"和"平凡"分不开。

**机制**：电路内 `routed_delta ~ placed_delta` 的斜率均值 0.951954 / 0.930217、R² 多在 0.89–0.97 → **布线阶段主要是一个逐电路的常数偏移，不重排候选**。所以"布局后档能替布线后档"的真正原因不是"布局后档预测得准"，而是"两档测的几乎是同一个量"。**这两种解释对实践的含义完全不同**：前者说"可以信任布局后档"，后者说"布线阶段几乎不改变排序，但会改变绝对值，所以最终验收还得跑布线"。

**教训**：① 任何"两档结论完全一致"的读数，**先做同带与无带两种口径**，确认不是带宽不对称的产物；② 加上**安慰剂对照**（把标签在正确分组的层级内置乱），否则无法区分"真一致"与"平凡一致"；③ 一致性成立时**必须给出机制**（回归斜率/R²），因为"一致"有两种完全不同的来源；④ **监督可替 ≠ 判定可替**——前者只要求排序信息可用，后者要求绝对判定可用，必须分开测、分开写。

## 2026-10-24 池化比例差异必须过逐电路配对，否则不成立

**现象**：布局后判据的证伪率 13.3% 低于理想判据的 23.3%（ITC-99），看起来"布局后判据更好"。但**逐电路配对是 3 胜 2 平 2 负，p=1.0**，ISCAS89 的方向还相反（16.0% vs 10.7%）。

**教训**：① 少量电路上的**池化比例差**极易被个别电路拉出假象，**必须配对检验**；② **"一个族显著、另一个族不显著"不能推出"两者有差别"**，反过来"两族方向相反"就是反证；③ 把**族间方向相反**这一事实写进结论，而不是只报自己那族好看的数。

## 2026-10-24 两族出现完全相同的分组数字时，先查是不是同一批数据

**现象**：两族的 `both_accept` 分组数字**完全相同**（23 / 19 / 2 / 2），概率上很可疑。

**核查**：写独立复算脚本从原始 `training_table.jsonl` 重算，并对两族的候选键集合取 sha256 —— **e320b02ffd2a7c9c vs ddd483cd06053c6f，键集合完全不同**，两族的电路名也不同。→ **确认是真实巧合**（两族流程同构、边际量量化到 0.01 ns，小计数撞车并不罕见），并在记录里注明此事经过核查。

**教训**：① **异常干净/异常巧合的数字都要独立复算**，并把核查过程写进记录（结论"是巧合"也要有证据）；② 独立复算脚本应从**原始产物**重算并比对**键集合哈希**，而不是复跑同一个脚本；③ 巧合本身不删，但要**说明它被查过**——否则下一轮接手的人会重新怀疑一次。


## 2026-10-24 族级比例差异要过三道闸：配对、量化边沿、池结构

**现象**：按 kind 统计"布局后与布线后符号相反"（= 判定走错分支）时，ITC-99 的 B 类翻转率 23.2%，R 类只有 7.3%，读起来就是"**插 buffer 的收益被布局后档系统性低估**"。

**三道闸**：

1. **逐电路配对**：B vs R 1 胜 3 负（p=0.625）、B vs G 2 胜 4 负（p=0.6875） → **不成立**；
2. **量化边沿**：翻转若涉及的值在 ±0.01 ns 内，可能只是舍入变号。剔除后 B 塌到 6.5%、R 塌到 0.6%、JOINT 塌到 0.0% → **族级差异主要由近零小数值变号贡献**。
3. **池结构**：b09 的 53/87 个候选集中在 iter 8，该池整体偏移 +0.07283 ns，**同池内非 B 翻转 9/11 与 B 翻转 28/42 几乎一样** → **是池级效应不是 kind 效应**。

**教训**：① **族级比例差是最容易骗人的读数**，任何"某类候选特别糟"的读法都要依次过**逐电路配对 → 量化边沿 → 池结构**三道闸；② **量化边沿这一关最容易被跳过**——边际量量化到 0.01 ns 时，"符号相反"里很大一部分是±0.01 的小数值变号，不是物理；
③ **反例先查结构再下结论**：b09 的 R² 异常一开始被我读成"布线重排候选"，实际是"某池整体偏移"——两者的实践含义相反（前者说不可信，后者说可同池标定吸收）；
④ **判别"平移 vs 重排"要用池内偏移展度 ÷ 量化底**，而不是目测比值：b09 iter-8 = 9.8538、b01 iter-8 = 3.7031，前者超出量化底说明"既非纯平移也非纯重排"。

## 2026-10-24 报"高相关"之前，先排除量化底

**现象**：LOG-17 报"布局后与布线后的电路内拟合 R² 0.89–0.97、斜率≈1"，据此说"布线阶段主要是逐电路偏移"。

**证伪**：边际量量化到 0.01 ns，若两档都只是舍入，高 R² 完全可以是假的。检验：**量化底** = 0.01/√12 = 0.00288675 ns（两个独立舍入测量能产生的最小展度）。实测电路内残差 sd 是量化底的 **3.594–17.3285 倍**，量化底只占残差方差的 **0.33%–7.74%**，而两档共享的信号展布是量化底的 **6.6601–26.6013 倍** → **R² 不是舍入产物**。

**教训**：① **任何"高相关/高拟合"的读数都要先问"分母是什么"**——这里分母是量化底，比值要显著大于 1 才有意义；
② 报"差异由 X 贡献"时，要同时给**分子（观测值）与分母（可解释该差异的上限）**，否则读者无法判断这个贡献是不是全部；
③ 证伪用的检验**要成为正式工具进链**，因为批次收齐后必须重算——放在 scratch 里下次就会忘。


## 2026-10-24 比较"测量方案 A 与方案 B 谁更好"时，评分器不能是 A 或 B 自己

**现象**：要回答"跑第二次物理实现能不能让**选择**更好"，直觉做法是让两个选择器（单次测量 vs 两次平均）各选一个候选，再看谁离"最好的候选"更近。但"最好的候选"要用标签定义，而**平均标签的最大值**恰恰是平均选择器自己用的那把尺子——它被自己的尺子评分，天然占便宜。

**做法**：**留一法**——留出一个实现当评分器，选择器只能用留下的实现，两个方向各做一次。这样任何选择器都不会靠它读过的测量得分。

**实测得到的额外约束（比方法本身更重要）**：**只有两个实现时，留一法下的"平均选择器"退化为"单次选择器"**（留进的只剩一个实现），比较**必然是平局**。ISCAS89 的 3 个池实测：两方向遗憾均 0.00000 ns、选中同一候选；ITC-99 为 0 池。→ **要有区分力的比较需要第三个实现**。

**教训**：① **任何"方案 A vs 方案 B"的比较，先检查"评分用的尺子是不是 A 自己的"**——这是最隐蔽的一类自证偏差；
② **留一法在只有两个实现时会退化**，这不是实现 bug 而是**方法的前提**，必须写进结论而不是报告一堆平局；
③ 遇到"比较做不出来"时，**先算清楚需要几个实现**（这里需要 3 个），才能把"等数据"变成"跑一个特定的批次"；
④ 顺带查出的另一件事比原问题更重要：那条**候选级带**（决定每个候选 GAIN/REGRESSION 判定的阈值）当时只由 51 个网表支撑，而同物理轴的 I1 批跑完后可扩到 1207 个（**约 20 倍**）——**一个批次的价值可能不在它被设计来做的事上**。

**现象**：候选级带（决定每一个 GAIN / INCONCLUSIVE / REGRESSION 判定的阈值）在 ITC-99 上只由 I0P0 / I1P0 这个 58 键 pilot 支撑（51 对、df=44），而全族 I0 / I1 的 1207 个候选**从未进过带计算**——因为工具里把 `F0_SIDE` / `F1_SIDE` 写死成了 pilot。pilot 是"当时两边都齐的唯一选择"，但它同时也是**一个电路子集**，不是随机样本。

**做法**：把作用域从**常量**改成**数据属性**——新增 `band_scope_itc99.py`，按实际覆盖度选 `full_family`（I0 vs I1，1207 键，两边标签齐全时自动切换）或 `pilot_subset`（I1 未齐时回落并显式标注），并把 `band_scope` / `f0_batches` / `f1_batches` 写进 `candidate_level_noise.json` 本身。**审计工具与测量工具共用同一个 `select_scope`**，不允许两处各写一套判断。

**教训**：① **一个带数字不带样本量就是无法解读的**——同一个工具在 pilot 上给 0.087496 ns、在全族上会给另一个值，引用时必须带作用域；
② **作用域选择规则必须和数据放在一起**：写死在覆盖里的话，批次跑完后链子会"跑完但没变"，而且没人发现；
③ **改作用域要两边同步**：审计说"已切全族"而测量还在用 pilot，比不改更危险；
④ 共享工具里被两个族共用的统计量，**抽成函数再复用**（`compute_band`），不要让第二个工具复制一份实现——复制出来的两份迟早漂移。

**现象**：布局后候选级带是在 IPLACEDF1 只跑完一部分时算出来的（749 对 / 6 个电路，2σ = 0.024052 ns）。补齐到全量（1207 对 / 9 个电路）后，带**变宽到 0.029826 ns（+24.0%）**，而不是收窄。

**原因**：被漏掉的电路恰好离散度最大（b09 电路内 sd 0.032812，是家族 pooled 0.014913 的 2.2 倍），而"先跑完的那几个电路"不是随机样本。带宽比（routed / placed）因此由 3.637785 降到 2.933514——**一个被当作结论引用的比值，误差来自样本选择而不是物理**。

**教训**：① **批次未完成时算出的量不是"暂时的"，方向可能是错的**——这次是偏窄 24%，会让"布局后档分辨率高"的结论被夸大；
② **补数据后第一个要重算的是所有阈值类量**，因为它们决定后续每一个判定；
③ **电路内离散度在家族内差约 3.8 倍**（b13 0.008633 → b09 0.032812）→ **"家族单一带"本身是伪概念**，要么按电路给带、要么用保守上界，并写明用的是哪种口径；
④ 产物里必须能看出**它是在多少样本、哪些电路上测的**，否则下一个接手的人无法判断它是否过期。

**现象**：候选级带是"同一网表在两个物理实现下的读数差"，但没说清它里面是否混了**运行级噪声**。I0P0 与 I0 正好是同一网表、同一实现、跑两次，可以直接量。

**实测**：42 个可比键的 post-route WNS **逐位相同**（非零差 0 个，最大绝对差 0.0 ns）→ **布线是确定性的，带里没有运行噪声成分**。

**意义**：① **"重跑同一个实现"对降低不确定性毫无帮助**——这是**物理上的零**，不是方法退化造成的平局；② 要降低不确定性只能换**真正不同的实现**，这与"留一法需要第三个实现"是两条**互相独立**的证据，指向同一件事；③ **零差值要当成结果报告**，"0.0 ns"和"不可测"是两种完全不同的结论，不能因为数字是 0 就当作没跑起来而跳过。
## 2026-10-24 指标先于模型：先检查尺子的分辨率够不够，再谈结论

**现象**：项目里用来比较"哪个选择器更好"的指标是**池级决策遗憾**（选中的候选比池内最优差多少 ns）。跑了很久之后回头看这个量：全部选择器在 25% 验证预算下的平均遗憾落在 **0.004146–0.029268 ns**，而同一批数据上测出的**候选级判定带是 0.087496 ns**。也就是说**所有方法之间的差异都小于测量本身的分辨率**。

**后果**：此前"纯门级图特征与随机无异"的结论**不是模型结论，是尺子坏了**。在低于分辨率的指标上，任何方法都测不出差异——包括真正有效的方法。

**做法**：换成候选级的**二分类**（标签 = 该候选的物理读数是否超过判定带），指标是 AUC，CI 用**按候选池自助重采样**（同一池的候选不独立，按候选重采样会低估不确定性）。判据也从"CI 是否排除 0.5"改成量纲无关的版本：**阈值扫描的每一个点 CI 都排除 0.5**。

**教训**：① **任何模型比较，第一步是检查指标量纲与测量分辨率的关系**——指标差值小于分辨率时，比较本身没有意义，结论一律不成立；
② 换尺子之后要**回头重述旧结论**：本例中"结构特征无信号"在新尺子上仍然成立（两族 AUC 0.4444 / 0.4368，点估计低于随机），但它的**证据强度完全不同**了（CI 明确、正例数 243/79、模型类交叉验证一致）；
③ **指标失效时的旧结论不是被推翻，是被降级**——"数据没错，读法错了"，两者必须分开说。

## 2026-10-24 "理想线网说谎"的准确形状是"避害有效、增益无效"，不是"随机"

**现象**：物理标签家族做出来后，直觉结论是"理想线网的接受判据与物理无关"。直接测之后发现这个强版本是错的。

**实测（ITC-99 布线后档，判定带 0.087496 ns）**：FAECO 实际接受的 44 个候选里，**真实增益 11.36%、真实损害 4.55%、物理惰性 84.09%**；被拒绝的 1149 个候选里是 **0.61% / 20.71% / 78.68%**。即接受判据把真实增益**富集 18.65 倍**、把真实损害压到拒绝集的 **0.219**；ISCAS89 独立复现（增益富集 8.94 倍、损害比 0.186）。两种置换零模型（电路匹配、池匹配）下 p ≤ 0.0245，逐电路比较**所有不平的电路方向一致**（损害：ISCAS89 布局后 0 胜 8 负，已达 8 个电路的最小可达 p）。

**教训**：① **"两个东西无关"和"两个东西弱相关"是两回事**，前者需要强的反证，不能从一个弱相关就跳过去；
② **一个判据的价值要拆成"避害"和"增益"两个维度分别量**——本例中判据在避害上很强（损害率降到 1/4.6），在增益上很弱（84% 的接受候选物理惰性），合在一起说成"无效"会把一个真实结论一起丢掉；
③ **"惰性"要定义清楚**：本例指效应小于"换一次物理实现"带来的差异，**不等于"完全没有效应"**——定义写不清，结论就会被读歪；
④ 零模型要**匹配要检验的那个量**：电路匹配（控制电路难度）与池匹配（额外控制迭代历史）两种都要给，且**置换统计量必须与观测量同量纲**（池化率比逐电路率）。

## 2026-10-24 判别式指标的正例数有功效下限，低于下限只能当噪声

**现象**：做候选级分类时，标签取"真实增益"（Δ > +带），布线后只有 **12 个正例**、布局后 **23 个**。它们的 AUC 在两档之间**方向相反**（布线后 0.2262、布局后 0.8495），阈值扫描时更离谱（1.5 倍处所有特征集齐刷刷 0.9713——那是正例只剩 1 个的退化）。而同一套流程换成"可分辨"标签（|Δ| > 带，正例 243 / 576）后，AUC 稳定、CI 合理。

**做法**：工具为每个格子输出 `n_positive` 与 `powered` 标志（正例数 < 30 即 `POWERED=False`），**三类标签（gain / harm / resolvable）一起输出**，不只报好看的那个。

**教训**：① **任何 AUC / 分类率 / 召回率，必须同时报正例数与 CI**——只有点估计的分类指标是不可解读的；
② **正例数少的时候，阈值扫描会产生退化解**（正例数随阈值变化而塌缩时，某些阈值处 AUC 会跳到接近 1），**必须同时扫阈值并扫正例数**；
③ 遇到"AUC 在两档之间方向相反"这种矛盾，**先怀疑功效，再怀疑物理**——不要拿一个 12 个正例的 AUC 去支撑任何结论。

## 2026-10-24 给基线加特征反而变差，是结果不是 bug

**现象**：把门级图特征加到"理想线网标签"上，AUC **不升反降**（ITC-99 0.8852 → 0.8383；ISCAS89 0.7572 → 0.6552）。而把 23 个图特征**单独**用，AUC 是 0.4444 / 0.4368（低于随机）。同一个特征集，单独用没信号，加上去还拖后腿。

**同时测到的对照**：**单个"布局后档标签"**（~2 s/候选，250 倍便宜于布线后档）作为预测器，AUC **0.9266 / 0.7466**，比 23 个图特征、比 14 个人工 proxy 特征、比理想线网标签都强。

**教训**：① **"加特征变差"通常是过拟合或特征冗余，不是实现 bug**——但要排除实现问题再下这个结论（同一套折叠、同一套 CI、同一个模型类交叉验证下才敢报）；
② **当基线特征本身就是一个物理测量时，人工结构特征往往带不来新信息**——它们描述的是同一张网表的另一种投影；
③ **这类结论的边界必须写死**：这里用的是**门级图的标量摘要**，不是图编码器，所以"图结构无信号"**不能外推为"GNN 无信号"**；要否证 GNN 路线必须用真正的编码器再测一次；
④ 由此得到的工程结论比"哪个模型更好"更有用：**该省的不是模型的钱，是物理仿真的钱**——先用便宜档筛选，再对高价值候选跑昂贵档。


## 2026-10-24 摘要口径不一致会让长批次静默丢掉一小部分标签

**现象**：给第三个布线实现 F2 写标签构建器时，按**字节**摘要给网表建索引、用 ledger 的 `base_netlist_hash` 查迭代基线。跑起来一切正常，直到专门查摘要口径才发现：ledger 里的 `base_netlist_hash` 是**文本模式**摘要（`Path.read_text()` 会做通用换行转换，CRLF 变 LF 再编码），不是字节摘要。1193 个候选里 **39 个（3.27%）** 的迭代基线是 6 个带 CRLF 的电路级 `mapped.v`，它们在字节口径下查不到 → 这 39 个候选拿不到边际量。**批次全跑完、rc 全是 0、标签文件看起来有 96.7% 的边际量覆盖，没有任何地方报错**——那 39 个候选仍带着"对电路基线的差"，只缺"对迭代基线的差"，两列都像有数据。

**做法**：① 两种口径的摘要**都**索引（取并集，不是二选一）；② 构建器里加**两道自检**——**摘要口径自检**在任何一次 run 存在之前就可算：每个 ledger 基线哈希必须匹配作业表里某个网表的字节或文本摘要，否则硬失败；**空列自检**只在批次完整后生效：批次全跑完而边际量一列都没有就硬失败。

**教训**：① **同一个文件的"哈希"在文本模式与二进制模式下可以不是同一个值**——`read_text()` 的通用换行转换是隐式的，跨工具沿用摘要约定时必须先确认对方用的是哪一种；② **静默的部分缺失比整体失败危险得多**——整体失败会停下，部分缺失会产出一份"看着挺完整"的标签文件，而丢失的恰好是**带 CRLF 的那批网表**，分布不随机；③ **能在跑数据之前算的检查就要在跑之前算**——摘要口径自检只需要作业表与 ledger，不需要任何 run，所以它能在 2–4 h 的批次开跑前就把这个 bug 拦下来。

## 2026-10-24 半成品批次算出来的"带"必须自带完整性判定

**现象**：判定带（band）是本项目每一个 GAIN/INCONCLUSIVE/REGRESSION 判定的门槛。写三实现探针时，直接对"当前存在的行"调用 `compute_band()` 并把结果写进产物。在 F1 侧只跑到 378/1207 时，它报出 2σ = **0.031297 ns**、377 对、**只覆盖 1 个电路**——正好是此前已点名过的"半成品全族带"陷阱值，而那个值单看完全正常，只是比家族带窄 2.8 倍。

**做法**：每个带都带一个**逐对完整性判定**，判据落在**配对键集**上：两侧共享的每一个键都必须有标签，才算"族带"。半成品带照打（它有信息量），但**不进**稳定性比值、**不进**跨实现比较。批次覆盖率也一并输出（promised / ok / complete），让人一眼看出数据缺在哪。

**教训**：① **一个数字必须带着它的样本量与覆盖率一起出现**——"2σ = 0.031297"看着像个正常结果，"2σ = 0.031297（377 对 / 1 个电路 / 覆盖率 31.3%）"立刻暴露出它是半成品；② **"族带"这个概念只有在配对键集上才成立**——某一侧多出来的键根本不进带，用"整张表是否跑完"来判完整性会误判（ISCAS89 的 F0 侧只有 309/338，但共享键 56/56 全有标签，带其实是完整的）；③ **完整性闸门必须同时挡住下游**——不允许半成品带进入比值与比较，否则整条链会带着一个偏倚的门槛继续往下传。

## 2026-10-24 跨族共享的工具不能把批次名写死

**现象**：三实现探针作为"两族共享工具"放在共享目录下，但实现→批次的映射写死成了 ITC-99 的 `I0/I1/I2`。ISCAS89 的两个布线实现其实叫 `F0`+`S713R` 对 `F1`+`F1S713`——在 ISCAS89 上跑这个工具会算出**空带**，而且**不报错**。

**做法**：把映射抽成按族显式配置，每个族写明自己的实现批次与对应的作业表；统计量本身仍然走共享的 `compute_band()`，不另写一份。

**教训**：① **"共享族"不等于"共享命名"**——跨族复现的前提是每个族的批次语义被显式登记，而不是靠工具作者记得两族命名一样；② **一个工具在某族上算出空结果却不报错，通常是映射错了而不是数据错了**——先查映射，再查数据；③ 改完之后要**用已存储的产物做交叉验证**：重写后的探针在 ISCAS89 上独立复现出 df **40**、CI95 **[0.01709, 0.031385]**、**48** 个候选网表，与 `candidate_level_noise.json` 逐项吻合，唯一差别是 1e-6 的**舍入口径**（存储产物把池化 sd 先舍入到 6 位再乘 2，探针乘的是未舍入值）——这说明复用的是同一个统计量，而不是碰巧算出同一个数。

## 2026-10-24 结论要分层：门槛一变，先算哪几条会翻，再决定改哪几条

**现象**：判定带要从 pilot 口径的 0.087496 ns 切到全族口径（预览 0.050419 ns，窄约 42%）。而上一轮
（LOG-20261024-21）的一整批结论都是**以带为门槛**的：可分辨正例数、AUC、接受集的三分拆、"惰性 84.09%"、
"图结构无信号"。带一变，这些数字全部要重算——问题是，**该改哪几条**？

**做法**：不重写统计量，而是 **import 现有工具、只覆盖 band 参数**，对**同一张训练表**跑两遍：
**对照遍**（现行带）与**预览遍**（新带）。**对照遍必须精确复现存储产物**，否则预演作废——这一条
不是形式主义：第一版 harness 把联表过滤后的 1117 行传给了接受判据工具，而该工具用的是**原始** 1207 行
训练表，拒绝集因此变成 1073 而不是 1149，是对照遍把这个错误抓出来的。修正后对照 **20 项检查、0 处不符、
最大偏差 0.0**。

**为什么预演近乎最终答案**：训练表的**布线后标签来自已收齐的 I0 批**、**布局后标签来自已收齐的 IPLACED**，
**I1 只改带、不改标签**——所以唯一的未知量是带的最终值。

**教训**：① **结论要分层，不要整体重写或整体保留**：预演给出的结果是"同批结论里，有的站得住、有的会翻"——
"给标签加图特征反而变差"更成立（差距 0.047 → 0.103）、"便宜档当监督"站得住（`placed_only` 仍是最强单特征）、
但**"图结构无信号"对 `gain` 标签不成立**（AUC 0.226 → 0.661），"**增益无效**"要改成"**增益有限**"
（接受集真实增益 11.36% → 25.00%）；
② **"翻转"往往来自标签定义而不是模型**：同一个模型在两个标签上一个低于随机、一个高于随机，差别只在"标签是
|Δ|>带 还是 Δ>带"——所以**凡是换门槛的结论，标签模式要一起报**；
③ **降门槛会同时给正例数补功效**：`gain` 标签的正例数 12 → 37，跨过了功效下限，于是一个此前被判为
"纯噪声"的格子变成了可读数——**功效不足的格子不该被"证伪"，只该被标成"不可解读"**；
④ **预演的价值在于提前知道该改什么**，它不替代最终重算：最终数字仍由定稿链给出，预演只负责把
"哪几条会翻"提前摆到台面上。

## 2026-10-24 池内 vs 池级：候选级信号必须和平凡基线比

**现象**：判定带落定后（图特征在 `resolvable`/`harm` 标签上接近随机、在 `gain` 标签上却"翻号"到 0.698），
很容易得出"图特征在 gain 上有信号"的结论。但这个结论**在候选生成器用不上**：它要回答的是
"同一个池里，这个候选值不值得跑一次昂贵的后布线 STA"。

**做法**：用同一套**留一电路交叉验证**的 OOF 预测，把池化 AUC 拆成三个读数：
① **池化 AUC**（全部行一起）；② **仅池均值**（每个候选只拿到自己所在池的平均分 → 只剩池间成分）；
③ **池内 AUC**（逐池算 AUC 再平均 → 只剩候选级成分）。
再加两个对照：**`kind_only`**（kind 独热 + iteration 的平凡基线）和 **harm 标签**
（能预测"变坏"的特征，是在预测方向还是在预测幅度）。

**结果**：ITC-99 `gain` 标签上 `structural` 池化 AUC 0.698248，**只给池均值就有 0.677415**；
`resolvable` 上 `one_depth` 池化 0.591712、仅池均值 0.560235、**池内 0.548140（CI 含 0.5）**。
池内读数下，**`kind_only` 0.555062 与最好的图特征集 0.561297 持平**（`harm` 上 0.572068 vs 0.577145；
`gain` 上 0.655336 vs 0.651380–0.672469），ISCAS89 三标签池内全部 ≈0.5。
而 `one_depth`/`one_max_fanout` 在 `harm` 上同样预测为正（0.641897 / 0.628593）→ **幅度效应**。

**教训**：
① **池化 AUC 不是候选生成器能用的读数**：它混进了电路间的差异（本族逐电路正例率 0.207–0.616），
   会在电路异质时制造"信号"。**报候选级结论必须同时报池内读数**；
② **任何候选级特征都必须和"kind 独热 + iteration"这个平凡基线比**：不比的"0.59 显著"可能只是基线的水平；
③ **用 harm 标签当方向检验**：一个特征若对"变坏"和"变化"都预测为正，它预测的是**幅度**不是**方向**——
   这条对照能一句话拆掉"某特征学到了物理规律"的错觉；
④ **看现象先问"这个信号在谁的分层里"**：本条差点把一条电路级差异写成"图结构有信号"，
   而 LOG-23 的预演、LOG-24 的分解两次都指向同一个动作——**把标签拆成可分辨/增益/损害三档分别读**；
⑤ **post-hoc 的特征子集要跨族复现才算数**：预演带下 `one_depth` 在 ITC-99 逐电路 0.6048 看着很稳，
   真带（0.049752）下掉到 0.545425（CI 含 0.5）——**门槛一变，post-hoc 的"发现"就会缩水**。

## 2026-10-24 用两个实现造不出可交换的第三个实现：夹具必须三侧全合成

**现象**：要给「第三个物理实现」写解读判据（三个两两带该相等吗？平均标签挑选器该赢吗？），就得先造一份**已知真值**的合成数据做夹具。直觉做法是：拿真实的两个实现，再加噪声造第三个。

**问题**：这样做出来的第三个实现**与第二个共享同一份噪声**（F2 = F1 + ε），于是 Var(d_F1F2) = σ_r² 而不是 2σ_r²、Var(d_F0F2) = 3σ_r² —— 三个带必然不相等（实测 max/min = 1.72）。更根本的是：**三个两两差在代数上相关**（d_F0F2 = d_F0F1 + d_F1F2），**用两个实现根本造不出可交换的第三个实现**。如果把这个 mock 的比值当成"真实第三个实现应该长什么样"，就会把一个建模错误当成物理预期。

**做法**：夹具**三侧全合成**——共同信号 + 三个独立同分布的实现噪声；再单独造一档「相关的第三侧」作为对照档，证明"某一对特别松/紧"是机器看得见的。夹具跑在沙箱（探针的族目录指向 scratch 副本），产物不落进真实目录。

**结果**：可交换夹具给出三个带 max/min = **1.028 ≈ 1**（每个差的方差相同，带应当一致），且留一比较显示**平均标签挑选器胜 38 / 平 85 / 负 21、p = 0.0363**（平均两个实现把噪声减半 → 平均应当更好）；相关夹具给出 max/min = **1.718**。

**教训**：
① **判据必须来自可实现的合成真值**：用两个实现造第三个，造出来的"真值"是假的；夹具要三侧全合成；
② **代数相关的估计量不能按独立样本解读**：三个两两带是同一批差的三种切法，max/min 比值的采样散布比三个独立估计更大，比值偏离 1 不自动等于"某一对特殊"；
③ **先在夹具上跑通"从未跑过的代码路径"**：三实现比较分支此前只打印过 "NOT COMPUTED"，若其中有缺陷，等 2–4 h 批次跑完才发现就太贵了；夹具把"代码可用"与"数据到位"两件事分开；
④ **夹具也要有对照档**：正向档（可交换）说明工具在有优势时**会**显示优势，反向档（相关）说明工具**能**看出异常——两者一起，才能把真实结果里的"无差异"正确读成数据结论而不是工具故障。

## 2026-10-24 长批次的存活不能交给 WSL：看门狗必须住在宿主侧

**现象**：F2 批（1207 个 OpenROAD 布线作业）跑到 626 个时，状态文件 8 分钟不再更新、`openroad` 进程归零、load 掉到 0.23。
同时消失的还有那条一直等待批齐的后处理链。`uptime` 显示 **0 min** —— **WSL 实例被重启了**。

**为什么"看起来像 OOM"其实不是**：内存上限 11962 MB、空闲 10119 MB、swap 未使用，新 boot 的 dmesg 里没有任何 OOM 记录。
但**旧 boot 的内核日志随实例一起消失**，死因无法再确证 —— 所以只能记"实例被重启，原因未确证"，**不能编一个归因**。

**两条教训**：

① **看门狗必须住在宿主侧**。第一反应是在 WSL 里再挂一个守护进程——那它会跟实例一起死，什么也修不了。
把状态探针（`f2_watchdog_check.sh`，输出 `SUP=/CHAIN=/DONE=/OPENROAD=`）和拉起脚本（`restart_f2.sh`）
放到 **Windows 侧**的 PowerShell 循环里，每 120 s 探一次，缺哪条链拉哪条，批满自动退出——
**这样实例重启后最多 2 分钟就自愈**。

② **断点续跑要按一等公民设计**。这次能 2 分钟回到 629/1207，靠的不是运气：
`run_labels.sh` 里"**已有 rc.tsv 的作业跳过**"这一行是抗重启的全部资本——
已完成的 626 个结果不丢，6 个在飞作业（没有 rc.tsv）自动重跑，不留半成品。
**所以长批次的记录里，"恢复步骤"必须和"启动命令"同级写出来**：checkpoint 在哪、
怎么判断已跑过多少、哪些目录是半成品会被重跑。只写启动命令的记录，等于没写。

## 2026-10-25 同一个减法被标成两种口径时，数字会自己告密

**现象**：核对三点曲线产物时，发现 marginal 块与 cumulative 块的 ideal 档 mean **完全相同**
（-0.046184）。两个本该不同的量给出同一个数，第一反应是"巧合"，第二反应才是去查。
查出来是：**这两个块用的是同一个减法**——`ideal_cumulative_wns = ideal_wns − ideal_baseline_wns`，
而 `ideal_baseline_wns` 是**迭代基线**（ledger 的 `metric_references.setup_wns`），不是电路基线。

**为什么这一层能藏这么久**：训练表里 `ideal_delta_wns` 的 schema 写的是"边际增益：候选相对其迭代基线"，
`ideal_cumulative_wns` 写的是"累积增益：候选相对电路基线"——**两句话都写得通，但只有一句是真的**；
数据集卡也照抄了这两句，于是错名被复制到了对外交付物里。更糟的是它**不报错**：rc 全 0、覆盖率看着正常、
判定计数一个没变，只有把两个块并排放时才看得出指纹。

**教训**：

① **先做恒等性检查，再看相关系数**。两种读法如果给出同一个数，说明它们是同一个量——
这个检查比任何统计检验都便宜，且能直接定位口径问题。

② **负相关是口径 bug 的气味，不是物理结论**。物理阶段与理想阶段 rho = −0.11 只可能是口径坏了；
遇到"物理上不可能的相关性"，先怀疑口径，再怀疑物理。

③ **命名要写清"参照物是谁、来自哪个文件的哪个字段"**。`ideal_baseline_wns` 这种名字天然像"电路基线"，
而它其实是"迭代基线"；**数据集卡是 bug 的传播者**——把错的声明写进对外文档，下游就会照着错的口径引用。

④ **改不受版本控制的文件前先确认**。`experiments/` 被 git ignore，本轮四个被改的工具**都不受追踪**，
补丁脚本里的占位符被原样打进源码后**无法 git 回滚**，只能按文本模式回补。
"这个目录受不受版本控制"应该是动手前的第一个问题，不是出事后的第一个问题。

⑤ **布尔标志必须配一个原始数字探针**。本轮取数脚本里一个 tuple 循环产出的标志
（`iscas89_dec_unchanged` = False）与事实矛盾（直接比较 True、逐条 0 处不同、对照遍也通过）。
改成**显式逐项比较 + 同时打印原始数字**后全部一致。**一个从不失败的对照遍没有价值，
一个没有原始数字的布尔标志没有可信度。**

**新增教训（LOG-20261025-28）**：读产物、按预注册判据下判决，这条链上有两个**不会报错**的坑。

⑥ **判决必须带显著性门，不能只比胜负计数**。F2 的 C3 判决是"均值挑选器是否比单实现挑选器好"。
产物给的是 27 胜 / 92 平 / 25 负，精确二项 p = 0.8899。第一版判决脚本写成
"`wins > losses` 就算通过"，于是把 27 vs 25 判成 **C3 成立**——那是掷硬币，不是"略好且稳定"。
加 p < 0.05 门之后判决变成"不成立"。**计数差 2、p 接近 1，是"没有证据"，不是"弱证据"。**

⑦ **字段名要按产物的实际名字读，不能猜**。同一份产物的总表用 `averaged_better` /
`single_better`，逐方向表用 `averaged_better_pools` / `single_better_pools`。
第一版脚本按猜的名字读，结果是**判决字符串根本没生成**（脚本不报错，只是 `verdict_C3` 为 None）——
一个"没有输出"的判决看起来像"判决还没做"，而不是"读错了"。**先打印产物的一个键名集合，
再写取值代码。**

**新增教训（LOG-20261025-28 的附带事故）**：一个"自愈看门狗"本身也会制造故障。

⑧ **"读不到状态"和"状态为空"必须分开**。Windows 侧看门狗用一个 WSL 调用读状态，
那个调用**偶尔返回空**（同一脚本手工跑就正常）。看门狗把空返回当成"进程没了"，
于是连续三次重拉后处理链——**每次重拉都基于一个错误的判断**。判据要写成：
**"探测失败"→ 跳过本轮并告警；"探测成功且状态为空"→ 才判定为缺失。**
一个不会区分"没读到"和"没有"的看门狗，比没有看门狗更糟。

⑨ **跨 WSL 互操作启动 Windows 进程可能永久挂起**。三条链的 `/init` 包装进程停在 S 状态、
CPU 时间 00:00:00，而 Windows 侧**根本没有 python 进程出现**；同一条命令**从宿主直接跑只要
13.9 秒**。**因此长链路的分析步骤必须能在宿主侧直接运行**（不能只依赖"在 WSL 里调 Windows
解释器"这一条路），否则一次挂起就让整条链停在那里、而表面上"进程还在"。

**新增教训（LOG-20261025-29）**：手写一个模型出来，最容易犯的错不是数学，而是**把"跑通了"
当成"有效果"**。

⑩ **先过数值梯度校验，再看任何 AUC**。numpy 手写反传时，我第一版把 `dW` 的 einsum 下标写错
（输出维没出现在输入里），第二版把**求和损失**的数值差分和**平均损失**的解析梯度直接相比
（差恰好是 batch 大小的倍数：解析值小 6 倍 = 1/len(y)）——**两个版本都会产出漂亮的 AUC**，
但其中一个的梯度是错的。**数值梯度校验是唯一能发现这件事的检查**，而且它比任何统计检验便宜。

⑪ **单折烟测不是效果证据**。只留出 b01 一折时，模型给出 0.6531 的测试 AUC，看着像"有信号"；
**完整 7 折协议下同一模型只有 0.479242**。烟测的价值是"代码跑通了"，效果证据必须来自完整协议，
两者要分开记账。**同理，基线必须由同一套工具算**：本条用项目自己的 `resolvable_positive_classifier.py`
算基线，精确复现了 LOG-24 的存储数字（池内 0.555062、池化 0.432507），这一致性本身就是对照遍。

**新增教训（LOG-20261025-30）**：这一条是**自查抓出来的**，不是别人指出的。

⑫ **比较多个带（多个估计量）之前，必须先检查它们的样本支撑是否一致**。本条的教训来自
`compute_band()` 的池化方式：`pooled_sd = sqrt( Σ_c (n_c−1)·sd_c² / Σ_c (n_c−1) )`。
**某个电路的差异恒为 0 时，它贡献 0 到分子、却贡献 (n_c−1) 到分母** —— 它不提供任何信息，
只会**稀释**这个带。三个两两带的 df 相同（同一批候选）、**携方差的电路却不同**，
于是 max/min 是在比三个**被不同量稀释过的**估计量：全族口径 1.476087 落在"C2 成立"，
共同非退化子集上只有 1.173530，**同一份数据、同一套工具，判决却翻了**。
**判据**：任何"比几个量的大小"的比较，先问三件事——
① 它们是不是在同一批样本上算的？② 有没有样本对其中某些量**恒等为零**？
③ 零差异样本是否仍然进了自由度？**"df 相同"不等于"支撑相同"。**

⑬ **恒等性指纹先于相关系数**。观察到"某对差异在 4/7 电路上逐位为 0"时，
**第一反应不能是"这意味着什么"，必须是"这是物理事实还是记账假象"**。
可用的判别式是候选级恒等式 `d_F0F2 = d_F0F1 + d_F1F2`：**若某对恒为 0，则另两对的电路内 SD
必须逐位相等**。这是**恒等式**（成立或不成立，没有"相关强度"可言），本条实测 5/5
精确成立（差 0.0）→ 退化是真实性质。**再补一层产物级证据**：三个批次各自的日志与 ODB 逐字节不同
（说明作业真的跑了），但退化电路上 **I0 与 I2 的 `final.odb` 逐字节相同**、而日志里
`place_pins` 的 **Number of slots 不同** → **设置确实生效了，只是设计收敛到了同一个结果**。
**"运行配置不同"与"结果相同"必须分别取证**，只看其中一半会得出相反的结论。

**新增教训（LOG-20261025-31/32）**：这两条都是"用前人的工具去问一个更准的问题"问出来的。

⑭ **判决是阈值的阶梯函数：先问"阈值落在量子网格的哪一格"，再谈阈值本身变了多少**。
布线后 WNS 量化到 **0.01 ns** → 路由后差值都是 0.01 的整数倍 → 标签集合
`{|Δ| > band}` 只由整数 **floor(band/0.01)+1** 决定。六个带变体（0.035406 … 0.050272）
只落进**三个**集合，且**同一集合内的变体，标签数、分类器 AUC、接受判据数字逐位相同**。
**推论**：此前几轮的"带敏感性"分析真正测的是**"阈值跨过了哪条量子边界"**——
pilot→定稿的"窄约 42%"其实是 **idx 9 → idx 5 的 4 格移动**（真改标签集合），
而 LOG-28 说"F1/F2 与 F0/F1 完全等价"的真实原因是**同一格**（idx 5），
**不是**"两者相差 0.004 < 0.01"（那只是数值巧合，机制是同格）。
**纪律**：报告判定带**必须同时报它落在量子网格的哪一格**，否则读者会把"同格"误读成
"数值接近"，把一个结构事实当成巧合。

⑮ **"平均/投票没帮助"这类结论，先查参与成员之间是否结构性等价，再谈收益**。
本轮把 LOG-28 的"C3 不成立"拆开：全族 27/92/25 的平局**不是没有效应**，
而是**两个方向相反、各自显著（p = 0.0004）的效应相消**——被留出的实现与单实现 picker
所用的实现逐候选相等时，单实现 picker **已经精确命中**（遗憾恒 0），平均只会注入噪声
（**显著有害**）；相等的是被平均的另一个时，平均是朝真相的收缩（**显著有益**）；
三个实现真正互异时**什么也没有**（+0.14 量子，Wilcoxon p = 0.31）。
**纪律**：任何"多跑一个实现取平均/投票"的结论，**先问：参与平均的成员之间是不是
在结构上等价**（例如同一张网表跑同一个实现）？等价性一旦成立，平均就不是"降噪"，
而是"把另一个实现的噪声灌进来"。**同理**，代数上相关的量（`d02 = d01 + d12` 这类）
的相关系数**不携带独立信息**——它被三个方差钉死，只能当一致性检查。

⑯ **"翻"标记先问它标的是数字还是判决，再落文档**。本轮证据包里的
`flip_table_vs_published[].flips` 标的是"**这个数字相对参考值朝该行声明的方向动了**"，
而且**逐行极性不同**：接受判据四行里"增益率↑、富集↑、惰性↓、损害比↓"都被标成 `flips=true`
——那恰恰是**判决被加强**的方向；标签计数那三行的 `flips=true` 只是"阈值放宽 → 纳入更多"。
**纪律**：产物里凡有 `flips` / `changed` / `reversed` 这类标记，
**落文档前必须把它的极性逐行写清楚**，并明确本文说的"翻转"是**判决方向**还是**数字**；
否则读者对不上证据包，会把一个被加强的判决读成被推翻。

⑰ **对照必须与被检验对象同架构——"同一协议"里的"协议"包含架构**。本轮最贵的一个发现
    不是统计结果，而是**对照用错了架构**：工具里的 C2 空标签与 C4 随机初始化探针固定跑
    `readout='mod'`，而被检验的变体 `gnn_global` 用 `readout='global'`。
    按实际实现的口径，两条对照读数都高于 0.53，判据"未触发"；补跑**架构匹配**的对照后，
    匹配对照落在随机附近，判据"触发"——**同一个判决因口径而反向**。
    **纪律**：凡是"对照读数 < 阈值"型的门，先问三件事：对照与被检验对象**同架构**吗？
    同协议吗？阈值量的是**同一个量**吗？**任一条为否，这个门量的就不是你想量的东西。**
    证据包里凡是列对照的地方，**逐条标出架构**（本轮证据包第 3、4 节都加了 readout 列）。

⑱ **引用任何数字前先做一次"复算校验"，它同时是可信度证明和回归护栏**。本轮把
    `gnn_global` 的预测向量从工具里复算了一遍，池内 AUC **逐位相同**
    （0.6536246765108727）；有了这一条，后面所有基于该预测向量的机制诊断
    （D1–D7）才敢引用。**纪律**：新工具的产物在进文档之前，先跑一遍"从原始输入
    重新算出来与发布值逐位相同"的校验；不一致先归因（实现 bug / 设定缺陷 / 环境），
    **不要先改措辞**。

⑲ **新增代码路径：先沙箱跑通、再把中间产物落盘、并且把"维度契约"钉成自检**。本轮三处踩坑
    都属同一类：(a) 嵌套选择的沙箱**打印了全部结果却在写 JSON 前死掉**——"跑通了"不等于
    "产出物存在"，所以正式批会把**中间产物分阶段落盘**（控制读数先落盘，诊断段失败也不丢）；
    (b) 新增的 C4-global 路径照抄了 mod 路径的 `w_out` 宽度（2·D_H+1），而 global 读出的
    表示只有 D_H 宽 → 形状不匹配，**9 分钟的批白跑**；
    (c) 隔离断言如果从不触发，就只是一句注释——自检必须**故意泄漏**并确认断言会响。
    **纪律**：凡新增一条代码路径，交付三样东西——沙箱产物（证明跑通）、分阶段落盘
    （证明不丢）、以及把"契约"（维度、隔离、种子、顺序）写成**会失败的断言**的自检。

⑳ **分块长批的产物必须自证完整：残缺读数与完整读数在文件里必须可区分**。本轮组件 F
    改成可续跑分块（`--max-folds` + 逐折检查点 + `--resume`）之后出现一个**静默陷阱**：
    工具跑完 N 折后**照样把结果写进正式路径**，于是落盘脚本会把一个只有 1/8 外层折的
    读数**当成完整读数**写进记录——所有嵌套数字被静默欠采样，而记录里**看不出任何异常**。
    **纪律**：① 分块跑批的产物必须带**完整性标记**，本轮用 `--require-complete`
    （跑满全部外层折才写正式文件，检查点照留以便续跑）；② **读侧必须再验一次**
    （落盘脚本与证据包生成器各查一次 `complete` 字段，缺标记就当"没有读数"处理，
    宁可不下结论）；③ **"产物存在"不等于"产物完整"**，读者必须能一眼区分两者。

㉑ **空判决必须配齐四项对照，否则判决无法解释**。本轮预注册的 H1 两族都未触发，
    如果只写"H1 未触发"，读者无法分辨四种完全不同的情形：
    ① **尺子坏了**（根本没有分辨力）；② **判据本来就没用**（换什么都没用）；
    ③ **没有钱可分**（奖池 ≈ 0）；④ **钱分到了别处**（机制错位）。
    本轮把四问做成四个带读数的对照，全部落在同一批决策上：
    **正向对照**（同一个检验对 oracle 做：D3b，100.0% / 100.0% 的种子
    p < 0.05 → 尺子有分辨率）、**最强竞争基线**（随机合格候选：D3，
    6.5% 的种子显著 → 现有判据本就在机会水平附近）、
    **奖池**（D6：oracle 显著优于理想判据 → 奖池存在）、
    **机制归因**（D7 排序器质量、D2 分歧处的收益差分布、D8 稀疏度）。
    **纪律**：任何"未触发"型判决，落地前先把这四问各做一遍并写进证据包；
    少一问，读者就只能猜，而"未触发"很容易被误读成"证明了反面"。

㉒ **候选级指标不能替代决策级指标，池内排序变好也不能替代顶端选择变好**。
    本轮同时踩到这两个坑：布局后 Δ 作为**候选级**预测器很强（当前产物 `resolvable_positive.json`：AUC 0.896779，理想档单独 0.859390），
    作为**池内排序器**也显著更强（ITC-99 Spearman 0.644043 vs 0.399218，p = 0.021484），
    但作为**选择器**只拿到 8/5/14、p = 0.581055、挽回 0.073171。
    原因：判据只读 **argmax**，而"整体排序更准"的优势大多落在中段；
    两判据分歧处的布线后收益差全部落在 **±1–2 个 0.01 ns 量子**里。
    **纪律**：凡是"用 X 替代 Y"的方案，必须同时报三个读数：
    **候选级**（池内 AUC / 相关）、**排序级**（池内 Spearman）、
    **决策级**（逐决策配对检验 + 挽回比例 + 与 oracle 的重合率）；
    只有第三个才是策略收益，前两个只是必要条件。

㉓ **极小 p 值不能用定点格式打印，分数与百分数不可混用**。本轮两个真实的坑：
    ① `round(1.5e-08, 6)` = `0.0`，写进记录会读成 **"p = 0"**——
    这是把"极小"夸大成"恰好为零"，属于让记录说谎；正确写法是科学计数法。
    ② 随机对照的 `frac_p_below_0_05 = 0.065` 是**分数**，写成 "0.065%" 就被读成
    0.065%，而正确读数是 **6.5%**。
    **纪律**：格式化要**按量级选**，不按习惯选——小于 1e-4 的数默认科学计数法；
    分数与百分数之间必须显式换算并落进变量名；交付前跑一次**占位符/格式守卫**
    （本轮证据包生成器加了 `%s` / `{key}` 残留守卫，它当场抓到了这两类问题）。
㉔ **"回退到另一个字段"必须先证明那个字段在**缺失**的那批对象上也是测量值**。
    本轮最贵的错误不是没看见 bug，而是**修得太快**：回退到 `trial.wns` 在
    "同时带有两个字段"的 trial 上 100% 正确（3734/3734、332/332，0 不符），
    于是在"缺少字段"的那批对象上回退看起来也安全 —— 实际上那批对象的 `wns`
    是**迭代基线的占位符**（310/310 恰好相等，
    0/310 有 STA provenance，而对照组 3734/3734 全有），
    回退等于**伪造"恰好无影响"**。它甚至真的改变了读数（b01/2 的 `gain_impl` 0.01→-0.01、
    `impl_key` t022→t021），若不是"回退改变了不该改变的数"这条检查把它捞出来，
    它就会带着一个假的零进入训练表。
    **纪律**：验证"回退等价"时，**对照集必须是"会用到这个回退的那批对象"**，
    而不是"恰好也有这个字段的那批对象"；并且要查这批对象的**来源标记**
    （有没有 STA provenance / report path / slack_status），
    而不只是查**数值相等**。**数值相等有三种成因：同一个量、复制、默认值。**

㉕ **"空"有三种，混起来会造出假测量**：**没测**（没有该档的运行产物）、
    **测了但读不出**（产物在但解析失败）、**测了等于零**。本轮把第一类当成了第三类。
    正确做法不是把空填成 0，而是**给"空"一个名字**：本轮新增 `ideal_label_status`
    （`measured` / `not_measured_pre_sta`）+ `ideal_wns_placeholder`（保留原值但标明是基线的），
    并让**下游按"有该档测量的子集"统计**（工具本来就是这么做的，只是准入门把两者混了）。
    **纪律**：数据管线里每个"空"都要能被回答"为什么空"；
    **宁可让一列带着原因的空值活着，也不要让它变成一个看起来正常的数字。**

㉖ **"丢弃"必须留痕，且要逐类留痕**。本轮的三点曲线把
    "理想档为空"和"物理档失败"用同一个 `continue` 处理掉，丢掉的候选里
    76 个**物理档是完好的真实测量**。修复后新增的 drop 普查产物把每一类丢弃都写下来：
    ITC-99 候选 1237 个；丢弃：other_batch 1265、post_failed 0、missing_routed_label 28；其中理想档未测量 76 个。
    **纪律**：任何"按条件跳过"的循环，都要在产物里留下**按原因分类的计数**；
    静默丢弃在短数据集上无害，在长批次上就是"看起来完整的结论其实缺了一块"。

㉗ **新开未决问题的编号必须按文件里**实际已用**的号取，不能凭印象顺延**。
    本轮自己的收尾检查差点带出一个假编号：新开的两条未决被写成 `OI-043` / `OI-044`，
    而这两个号在 OPEN_ISSUES.md 里**早就被 2026-10-16 的两条旧未决占用**；文件里的
    号空间其实已经到 `OI-052`，而且部分未决是**散文体**（`**OI-046（...）— ...**`），
    只扫表格行会漏掉它们。落地脚本当时只校验"这条块在不在文件里"，**没有校验编号是否已被占用**，
    于是"唯一"检查通过、撞号照旧发生。
    **纪律**：新开未决的编号要**从文件里实际已用的号集合现算**（表格行 + 散文体都要扫），
    且落地脚本要自带**编号唯一性守卫**；靠"上一轮用了 040–042"这类记忆来顺延是
    不可靠的——本项目的编号序列与轮次顺序并不一致（046–052 早于 040–042 出现）。

**新增教训（LOG-20261025-36）**：这一轮的三条教训都来自"**读**"，不是来自"**算**"。

㉘ **判决里的 p 值必须带检验名**。同一组数据可以有两个 p 值：LOG-31 那一组的
**Wilcoxon 双侧 p = 0.305200** 与**符号检验 p = 0.749300**。
记录里写的是裸 `p = 0.305200`，而它紧跟在"符号 37/217/34（p = 0.8126）"之后——
读者极容易把两者对调，对调之后结论方向就变了。
**纪律**：任何 p 值入记录时，**要么写全检验名，要么给出"检验名 + p"的对照**；
**裸 p 值是不可追溯的**——核对脚本按数字回读时都会抓错（本次核对脚本自己的第一版就
把符号检验 p 当成了 Wilcoxon p）。

㉙ **"有输出但非零退出"的命令，不能用 `|| echo 默认值` 兜底**。
`pgrep -c` 无匹配时**打印 0 并返回 1**，`|| echo 0` 于是把状态变成**两行**；
读数方按**位置**取最后一行就取到了那个孤立的 0 → **"读不到状态"被当成了"状态为空"**，
一个已完成的批被当成空批，于是**每两分钟重拉一次**（教训⑧讲的是"读不到"与"没有"必须分开，
本条补上机制：**分开的办法是让状态只有一行、并按标记选行，不是按位置取最后一行**）。
**纪律**：状态探测要满足三条——**只输出一行**、**读数按标记选行而不是按位置取**、
**不可解析时只告警不动作**；并且**兜底值必须由命令自己产生**（`|| true` 后再取首行并补空），
不能用 `|| echo` 追加。

㉚ **撤回一条过度概括，也是这一轮最可迁移的一条**：把"**OI-052 第 30 条的未决已定论**"
说成"**OI-052 已 closed**"——OI-052 是**含 42 条子项的容器**，容器至今 open。
**纪律**：**"某条未决的一个子项被解决"≠"这条未决被关闭"**；
对外表述一个未决的状态时，**必须带上它的粒度**（哪一条、哪个未决），
否则下一个接手的人会以为整条都结了——**未决的粒度就是未决的一部分**。

㉛ **显示用的舍入不许作用在写进产物的数值上，也不许把非零 p 变成 0**。
本轮两个轴结构工具的 `exact_binom_p()` 末尾是 `round(min(1.0, 2 * tail), 4)`：
本意是把显示值理顺，**结果作用在了产物里存的那个数上**——
真实双侧 p **3.051758e-05** 被舍成 **0.0**，记录再按 `%.6f` 打印成 **0.000000**，
**读起来就是"p 恰为 0"**。定性结论没受影响（两个检验都远小于 0.05），
**受影响的是被印出来的数字**。**纪律**：
① **产物里的数值要留精度**（要么保留原值，要么用科学计数），**显示层的舍入放在最后一层**；
② **修完必须逐字段 diff**：重跑后的产物与旧产物**只允许预期的字段变**，
本轮 diff 证明**只有那 2 个 p 变了、其余逐位未动**——
这条 diff 比"重跑成功"重要得多；
③ **"0.000000"这种定点零永远是可疑的**：真值 0 与"被舍没"必须分开。

㉜ **"重新落地"必须证明它只动自己那一块，而默认动作应是"原地替换"，不是"切出再追加"**。
本轮发现第 32 轮的折叠脚本是从标记**截到文件末尾**的——这只在它是最新一条记录时安全；
现在它后面还跟着 LOG-34、LOG-35、LOG-36、OI-052 第 53/54 条、教训㉑–㉛ 与两条登记册条目，
**跑一次就会把它们全删掉**；而"切出再追加"还会把块挪到文件末尾，**破坏 LOGS.md 的时间顺序**。
实测四个文件被挪了位（已复原并与另一份独立备份逐字节交叉核对）。
**纪律**：块替换的默认动作是**原地重写"本块首行 → 下一块首行"这一段**；
并且必须带一条**回环自证**——在内容本该不变的时刻跑一次，文件必须**逐字节复现**。
"跑通了"证明不了"它没动别人的东西"，**逐字节相等才能**。

㉝ **超时本身就是判据时，并发就是污染**。
探针的单作业 1800 s 上限不是"跑不完就算了"，而是"该电路在 util=30 下不可达"的**定义**（rc=124）。
本轮差点在探针还在计时的时候并行跑第 32 轮的嵌套批（CPU 密集的 numpy 分析）：
一旦抢核，原本能在 1500 s 跑完的作业可能被拖到 1800 s，
**"不可达"这个科学读数就成了机器负载的函数**。
**纪律**：凡是"超时即结论"的批，**其它计算密集任务必须排在它后面**，
并把这条依赖写进启动脚本（等 driver 与作业全部消失才开跑）；**不要用"顺手并行"换几分钟**。

㉞ **换设备后，归档工具的路径变了，出处必须写进收据**。
    前三个 D case 的收据里记着 7z 的路径在**另一台机器**的 scoop shim 下；本轮那台机器的 shim 随换机消失，只能用 `C:\Program Files\7-Zip`。
    **压缩器版本不同 → 分卷字节不同 → 归档哈希不同**，这不是缺陷，但**必须写明**，否则下一个接手的人会把"哈希不同"当成"证据被改过"。
    **纪律**：**工具的出处是证据的一部分**（路径、版本、SHA）；换设备、换机器、换工具位置都要落到收据里。    同时记住：**根后验比对的是解出来的字节**——那才是"证据没被改过"的判据，分卷哈希只是这次压缩的结果。

㉟ **时限要按实测登记，不能把上一批的当已验证**。
    28 键的独立审查实测 184.8 s，按"作业翻倍"外推 56 键约 370 s，**实测 613.6 s（高出 1.66 倍）**——因为读到的原件比预想的多。
    **纪律**：批的时限**必须按本批的实测或按实测外推登记**，并且把"外推值 / 实测值"的差距写进收据；**照抄上一批的时限并把它当成"已验证"是本轮最容易犯的错**——本轮外推差了 1.66 倍，若当时按外推值登记时限，这个批会被自己的超时砍掉。

㉠ **"跑不完"和"不可达"是两句话，而并发会把前者变成后者**。
    第 34 轮把 b05 判成"已确认超时不可达"，但**同一个脚本、同一个网表**在档案里**串行 838 s 就跑完了**（rc=0、有 final.odb）。探针用 PAR=2，墙钟被抬了 1.22–2.11 倍，**更宽的 1800 s 上限输给了更窄的 900 s 上限**——这只有"上限之外还有差异"时才可能发生，而差异就是并发。
    **更狠的是机制**：b05 的详细布线 **1 分钟就完成（0 violations）**，超时全部发生在 `report_checks` 打印 97k 条路径报告上——**超时点在报告阶段，不在布线阶段**。
    **纪律**：① **超时即结论的批，其它计算密集任务必须排在它后面**（这条当时已写进预注册，但真正被违反的是"探针自己与其它任务并行"）；② **"在有限时间内跑不完"≠"不可达"**，两者之间必须有一次**独立证据**的仲裁（这里是档案的串行运行）；③ 判"不可达"前要**先看日志停在哪一段**——路径报告的数量能立刻区分"布线没完成"和"布线完成了但报告没打完"。

㉡ **口径要先回读既有产物，再写进预注册**。
    本轮预注册草稿把"只标 gate-eligible 候选"当成主口径（省 3.6 倍成本），理由是"决策级只需要每轮 ≥2 个合格候选"。**但这个理由答的是分析层的问题，被错当成了标注层的口径**。回读标签族自己的作业表才发现：**既有标签就是全量 distinct 候选做的**（1193 个哈希与台账逐电路完全相等，missing=0、extra=0）——合格性只出现在**分析层**（决策池取合格候选），不出现在**标注层**。若不读这一条就开跑，扩面会得到一批**与已发布 27 个决策不同口径**的标签，而且这个偏差要到合并分析时才暴露。
    **纪律**：① **池定义必须先证明它与既有产物同口径**，方法是拿既有作业表和台账求差集（不是靠推理）；② **省本的口径裁剪只能是对照，不能替换主口径**；③ 生成器与核对器**给出不同的池**时（b06 差 35、b07 差 12），那说明**规则没写死**——同一个网表被多个 trial 产出时，合格判定必须落在**同一个 trial**上，否则两张表用了不同规则。

㉢ **长批次在"还没开跑"的窗口里是最便宜的质量闸门**。
    脱离链本来就要等另一个批次结束才开跑，这段等待看起来是纯浪费，    实际上它是**唯一一个"批尚未消耗任何算力"的检查点**。    本轮在这段窗口里把批脚本对着既有产物读了一遍，    **零作业开跑就拦下三处缺陷**：没有试点门、没有修复段、时限与已发布口径不一致。
    **纪律**：① **挂长批之前，先把批脚本对着"同类批的既有产物"逐条核**——    本轮的第三处缺陷就是靠回读标签族自己的启动脚本才发现的    （既有序布局批用 TIMEOUT=3600，新脚本写了 1800）；    ② **批脚本本身要当交付物对待**：语法检查 + 合成输入的行为测试，    在挂批之前跑一遍（本轮 17 项，0 失败）；    ③ **改动批脚本用新文件名并存**，旧的保留当记录，    并**按精确 PID 停旧 launcher**（`pkill -f` 会误杀执行者）；    ④ 停旧挂新之后要**确认只有一个 launcher 活着**。

㉣ **制造伪影的条件会被继承，所以"修复段"必须是批的一部分，不是补丁**。
    第 34 轮学到的是"并发会把跑不完变成不可达"，    但**没有人把那条教训用进下一批的脚本里**——    扩面批照样跑在 PAR=2，照样没有区分"伪影"与"真上限"的机制，    于是同一个错误在下一个批次里**重新具备发生的条件**。
    **纪律**：① **上一轮学到的机制必须落成下一批的自动化环节**，    否则它只是一段文字；    ② **"超时"要自动降级为串行重测**，且降级后仍超时的才算真上限；    ③ 重测前的原始记录**改名保留而不是删除**    （改名恰好又是让续跑逻辑重跑它的手段，一石二鸟）；    ④ **时限必须与同类已发布批一致**——    把上限改严不叫严谨，叫制造不可比。

㉤ **内容核验对行尾是盲的，行尾必须单独设门**。
    OPEN_ISSUES.md 从 LF 变成 CRLF，发生在 LOG-37 的落地；那一次的核验有 25 项、全部通过，却**一次都没发现**整篇文件被改写。    原因不是漏看，而是**核验手段本身看不见**：    内容 diff 走 `read_text()` 的通用换行转换，    "删掉新块后与备份逐字节比较"也因为新块是追加的而查不到旧内容的行尾变化。
    **纪律**：① **格式类属性（行尾、编码、BOM、缩进风格）必须有独立的检查项**，不能指望内容核验顺带发现；    ② **落地脚本的写法要能自证**：本轮修好后每个文件都同时报告"修复前行尾/修复后行尾"与"规范化后内容是否逐字节相同"，两条信息缺一不可；    ③ **house rule 要写进门里**，而不是只存在于人的记忆里——    本轮之前四个文件没有一个符合它。

㉥ **Windows 上的 `write_text()` 会静默改写整个文件的行尾**。
    `Path.write_text(data)` 不传 `newline=` 时，`'\n'` 会被翻译成 `os.linesep`（Windows = `'\r\n'`）。    配合 `read_text()` 的反向归一化，就得到一个**读回来是 LF、写回去变 CRLF** 的回路，    整篇文件被改写，而脚本自己毫无察觉。    **纪律**：① **跨平台的记录文件，落地必须显式给 `newline=`**（`write_text(..., newline='')` 或 `io.open(..., newline='')` + 显式写结束符）；    ② **追加与整体重写要用不同写法并各自显式指定结束符**，本轮三个脚本里追加用 `io.open` 是对的、整体重写用 `write_text` 是错的，两者混用就会出事；    ③ **改了记录文件的写法后，要留一个备份以便逐字节回退**。

㉦ **"split 之后再查竖线"对绝对值记号是假阴性，而"恰好 4 格"从来不是全局规则**。
    本轮为核 LOG-40 的行格式，先按"首行恰好 4 个竖线"写检查，一跑发现 **927 条 LOG 行里 896 条不满足**。
    回头才看清两层：① 真正的 house rule 是**摘要格与证据格不含裸竖线**，而它是用 `own.split('|')` 之后再看 `cells[2]`/`cells[3]` 实现的——**split 已经把 |Δ|、|ρ| 这类绝对值记号切成了三个 cell，所以那道门永远查不到它们**，它实际只拦得住"竖线落在单元格中间"这一种情形；② 若把"恰好 4 格"当成全局门，**896 条历史行会全部失败**，逼着人去倒改历史措辞。
    **纪律**：① **收紧检查之前先量全量分布**，再决定新规则只管新写的行还是也管历史；② **检查手段本身要先被验证**——造一个含 |Δ| 的样本，看这道门到底抓不抓得到，别把"门一直绿"当成"门在管这件事"；③ **历史不合规要报告、不要倒改**（本轮只出统计报告，不动历史措辞）；④ **当检查手段有盲区时，把盲区写进门里**，否则下一个人会以为它管住了全部。

㉧ **用异口径档案秒数外推批成本是错的，必须用实测 + 每电路剖面**。
    本轮的批预算是从 2026-08-21 档案（`pr_auto.tcl`、PAR=1）的基线串行秒数外推的，得到"180.8 s/作业"。实测把它否定了：试点 10 个 rc=0 作业的均值 663.7 s/作业（只覆盖 b04），是原估的 3.67 倍。
    **为什么不能外推**：两者的 floorplan 口径不同（档案按利用率定 die，扩面用冻结 die）。基族自己的 I0 批（同为 `pr_label.tcl`）候选秒数 ÷ 档案基线秒数，比值在 b01 0.464、b02 1.62、b03 5.508、b08 1.684、b09 3.832、b10 2.832、b13 3.541 之间散开（最小 0.464、最大 5.508）——**一个比值在两个倍以上的差异里不可外推**。
    **纪律**：① **成本必须实测**，且要按**每电路剖面**加权（b04 的候选 713.5 s 与 base/final 的 469/460 s 属于不同电路，不能用单一均值代替）；② **"布局后 = 布线的 60%" 是估**，实测是 ≈ 0.25（基族 IPLACED ÷ I0 的每电路候选均值比：b01 0.146、b02 0.358、b03 0.22、b08 0.234、b09 0.305、b10 0.196、b13 0.289）；③ **批预算在试点段跑完前只能是上界**，必须在试点结束后重算并记录偏差（本轮 298.02 h ≈ 12.42 天就是这个上界）。
    **另一条可复用的判据（本轮实测，产物 `scratch/par_label_identity.json`）：并发只改墙钟、不改标签**——同网表、同 TCL、同实现的两对批对照（I0↔I0P0、I1↔I1P0，每对 58 键）的标签 **116/116 逐位相同、0 条不同**，而墙钟比在 0.781–2.636 之间。提升并行度因此是**机器时间旋钮**而非标签口径旋钮；反了这条可以用来否定"日志字节不同 ⇒ 标签不同"这个判据（两批的 `pr_run.log` SHA256 有 116/116 都不同，而标签一致）。

**新增教训（LOG-20261025-42）**：关掉一个测量段不等于它的信息不重要；关段前必须先问"这段是不是某类证据的唯一来源"。

㉨ **"关掉一个测量段"和"它的信息不重要"是两句话，而第二句不能用第一句的证据来判**。
    本轮 D1 关掉了扩面族的对照池（389 键），理由是它**纯复现、不携带新物理信息**（对照池与主池同名键 17 个字段全同、realisation 全为 F0、试点段已免费提供 58 对复现对照）——这条理由在"**新物理信息**"这个口径上是**成立的**。但同一个池同时是扩面族**唯一的族内复现性底噪来源**，而判定带的族内取值只能由它供给；按"没有新信息"的口径把它关掉，等于顺手关掉了族内底噪的**唯一产地**。
    **判据（可复用）**：关闭任何测量段之前，先列出该段的**唯一性清单**——它是否提供了**其它任何段都无法提供**的证据类型（哪个族内/族外、哪一种量、哪一条判定链）；若有，关闭它的代价**不能**用"没有新信息"这种新信息口径来衡量。关段的理由必须写在**被关掉的那类证据**的名下，不能借用另一种口径的结论。
    **可替代性要用"同等口径的替代方案"来谈**：本轮 `scratch/ext_band_source_options.py` / `scratch/ext_band_source_options.json`（主线程实算）的分层抽样方案里，**28 键 ≈ 1.329 h、覆盖 5 个电路**，相对全跑 389 键（17.529 h）**省约 16.2 h**；而族内底噪的可信度由基族自己的实测支撑（基族 0/58 与 0/8 对差异非零 → 底噪恰为 0；偏移是确定性的，要么恰为 0、要么是可见偏移，故看得见偏移只需 n≥1 对，n≥20 已足够；只有"每对概率 5% 的稀有事件"才需要 n≥59 才有 95% 功效，n=20 只有 64%）。也就是说：**抽样替代在"能不能看见族内底噪"这个口径上可行，但在"这个段还开着吗"这个口径上，先决条件是它得开着**。
    **本轮同时暴露的两条伴生教训**：
    ① **"默认跑法必然卡死"是可用性缺陷，不是配置建议**——`scratch/post_ext_chain.sh` 的默认 `--guard-batches default` 会要求对照池 389 键的回执，而 D1 已决定对照池不跑；**默认跑法必然卡死在第 1 步**，批跑完必须显式传 `--guard-batches v3`。被关掉的段会**以另一种方式**回来索取它的回执：**关段必须同步改掉依赖它的默认路径**，否则关段只省下了算力、没省下人力。
    ② **"部分完成度绝不出科学读数"这类性质，必须在批跑完前用真实数据验**——本轮在批运行中（试点 35/58、主池 0/1393）实测 `scratch/post_ext_guard.py` 两种模式，**都 exit code 2**（v3 模式 blocked 3 批；default 模式额外 blocked 对照池 missing=389），且 `experiments/20261025_physical_labels_itc99_ext/decision_readings.{json,txt}` **均不存在** → 链停在第 1 步、**未产出任何决策级读数**。批跑完后再验这条性质就**不可复现**了（数据已齐，门自然放行），所以它属于"**必须在窗口期内验**"的性质，和"跑完再算"的那类判据不是一回事。
    **纪律**：① **关段的理由必须写在被关掉的那类证据的名下**——"没有新物理信息"不能用来论证"没有族内底噪"；② 关段前先出**唯一性清单**，只要清单里有"只有它能提供"的条目，就要先给出**同等口径的替代方案**（本轮是分层抽样），再谈省多少；③ **关段要连带改默认路径**（默认参数、默认守卫、默认产物清单），否则被关的段会从别处把成本要回来；④ **"绝不出读数"这类性质要在窗口期内用真实数据验**，窗口过了就再也证明不了；⑤ **抽样量的依据要写清是"看得见偏移"还是"约束稀有事件"**——两者的 n 差 3 倍（本轮 n=1 vs n≥59），混用会把功效不足的抽样写成"已验证"。
    **边界**：本条全部属**工具/口径/工程层**，**非论文证据**；抽样测算的 1.329 h / 17.529 h / 16.2 h 与功效结论均**引用主线程的实算产物** `scratch/ext_band_source_options.json`（该产物由 14:13:34 的第一版修正而来：第一版只累加了「试点实测过的键」、把同电路的其余键静默丢弃，把对照池算成 1.43 h（真值 17.529 h）、并给出 30 键/6 电路/1.739 h 的抽样数；修正后为 28 键/5 电路/1.329 h，已与另一个独立实现互验一致），本条**未独立复算**；闸门实测的 ok=31 / recovered=4 / missing=23 与 missing=1393 是 **14:1x 的时点值**（完整性门读的是回执快照，批运行中随时在变），**不是终值**；扩面批结果尚未产生，本条不含任何扩面后的读数。

㉩ **同一份规则被两个脚本各存一份，必然漂移；自检脚本必须从被检脚本**读取**它的定义，而不是**复制**一份。**
    本轮的真实经过：常驻同步门 `scratch/verify_round34_sync.py` 里有一份`REGISTERED_BLOCKS`（登记块清单），而它的反向对照脚本 `scratch/selfcheck_sync_gate_line_range.py` 里**另存了一份完全相同的清单**。本轮在门里登记了两个新块（`| OI-058 |` 与 `**补充（LOG-20261025-45）**`）——**只改了门那一处**。结果：门是绿的（FAILURES: 0），自检却报 **10 passed, 1 failed**，失败项是"真实文件里新规则没有留下未解释的 added 行"，被列为未解释的 6 行正是新登记块的内容。**这不是门出了问题，而是两份真相里有一份是旧的**；更糟的是，如果当时只信自检，会误以为门有 6 行来路不明；如果只信门，会漏掉"自检与门已经脱节"这个事实。
    **为什么必然漂移**：副本意味着"更新规则"这个动作有两个可独立编辑的落点，而**任何一次登记、任何一次规则变更都只会改其中一处**。副本在写下当天是一致的，之后就一直在等一个不会到来的"两边一起改"的时刻。
    **判据（可复用）**：**凡是需要两个脚本保持一致的定义，只允许存在一份。**自检脚本对被检对象的配置**只能读取、不能复制**。本轮的修法是：自检改用 `ast` 从门脚本的**源码**里读出 `REGISTERED_BLOCKS`（`ast.literal_eval`），因为 `import` 那个模块会执行整个门。修完自检回到 **11 passed, 0 failed**，且新规则解释的行数 60 > 旧规则的 54（规则没有被削弱，反而更严）。
    **这条的边界**：`ast` 读出的是**字面量列表**；如果那份定义以后变成计算式（例如由作业表推导），`ast` 就会失效 —— 那时正确的做法不是退回复制，而是把定义抽到一个**共享的只读模块**里，由门与自检**同时 import**。判据不变：**一份定义、两个读者**。
    **推论**：凡是"两个文件必须同步"的场景（登记表与作业表、门与自检、生成器与消费者），都要问一句"这两个是**一份真相**还是**两份副本**"；若它们是两份副本，就应当立刻把其中一份改成读取方，而不是靠人手去记得同步。

㉪ **验收仪器本身也会假绿：证伪一个结论之前，先证伪"测量它的仪器"。**
    本轮的真实经过：第 38 轮判定的 17 条假绿已由三路修复关闭，并"经主线自己的验收复核"——但**那一轮验收的仪器本身是坏的**：`scratch/accept_falsgreen.py` 的 `w()` 把 WSL 路径原样交给 **Windows venv python**（这里唯一有 numpy 的解释器，链也用它），而 Windows python 读不了 `/mnt/d/...`，会去找 `D:\mnt\d\...` → 工具在"找不到输入"处退出；判定式又只判 `rc != 0` → **"门正确拒绝"、"输入不存在"、"工具崩溃"三者的退出码都是非零，判定式无法区分** → 整组 A/B/C 断言实际测的是"路径能不能打开"，不是它们声称的空表 / 无日志 / 畸形行 / 覆盖率。**物证**：那轮验收在**工作区外**建出了 `D:\mnt\d\...\scratch\...`（29 个目录 / 20 个文件），它连自己的产物都没落在工作区。同一批工具里唯一把仓库根写死成 `/mnt/d/...` 的自检脚本，还在 Windows python 下模块级异常 → rc=1、stdout 为空 → 验收把空 stdout 解析成"失败计数 = -1"，记成"反向对照失败"——**工具根本没跑起来，却被记成被检对象失败**（假红）。
    **判据（可复用）**：① 判定"某个工具拒绝了"必须能区分**三种情形**——门正确拒绝（**具体退出码 + 具体理由**）、输入不存在（理由是"找不到"）、工具崩溃（无输出或 traceback）。**只判"非零退出码"的断言不构成证据**；② 同一份脚本要在它可能运行的**每个解释器/环境**下各跑一次（本项目里 WSL `python3` 与 Windows `.venv/Scripts/python.exe` 都能跑工具脚本，而它们的路径语义不同：前者读 `/mnt/d/...`，后者读 `D:\...`）；③ **工具里不要写死仓库根**，用 `Path(__file__).resolve().parents[1]` 推导（本项目里当时只有那一个自检脚本是异类）；④ 判定式要能区分**"工具没跑起来"**与**"被检对象失败"**：前者重试并标注，不能当成后者的证据。
    **推论**：**假绿不只掩盖缺陷，它还会污染验收者的预期**。路径修好后真值是 exit 8，而按上一轮留下的假数字把期望码写成 7，差一点点就把一次**完全正确**的拒绝判成失败，逼人去改**正确的那一边**。所以验收的"期望值"也必须来自**当前工具的实际行为**，不能沿用上一次（可能就是错的）记录。

㉫ **修真实数据不等于修测试资产：同一段口径逻辑在生产路径与测试夹具里各存一份副本，夹具那份往往更旧。**
    本轮的真实经过：第 38 轮已查明并修过真实族的一个隐蔽缺陷——ledger 的 `base_netlist_hash` 是**文本模式摘要**（`read_text()` 的通用换行转换）、job 表的 `candidate_hash` 是**字节摘要**，构建器只索引字节摘要 → 1193 个候选里 39 个（3.27%）查不到迭代基线 → 边际量静默为空而 rc 全 0；真实族已改为**双摘要索引**。本轮适配合成演练时发现：**同一处逻辑在演练 fixture 里的那份副本**只注册字节摘要 → 迭代基线链断裂 → 2/27 行没有边际 delta → 覆盖门以 exit 8 拒收整个数据集。
    **归因**：**门是对的，fixture 是错的**。覆盖门正是为了抓这种"键覆盖率看着 100%、实际 join 之后少了一半"的情况才存在的——它在演练里**第一次真正发挥了作用**。
    **判据（可复用）**：**凡是被复制过的口径，都要单独登记**：生产侧修了不代表夹具侧修了，夹具副本通常**更旧**（它不会被生产数据触发）。发现方式是**把夹具放到同一口径下让门去判它**，而不是让夹具去迁就门。
    **推论**：**一个夹具第一次真正跑通某道门时，往往暴露的是夹具自己的错，而不是门的错**——此时不要去改门。（这条与教训㉩是同一件事的两面：㉩讲"副本必然漂移"，本条讲"副本漂移的方向通常偏向更旧的那一份"。）

㉬ **钉死"失败形态"的断言会随外部状态推进而过期；钉死"性质"的才守得住。**
    本轮的真实经过：`scratch/h4_chain_fix/run_tests.sh` 的 T8 硬编码了 live 失败的一种**形态**——断言日志里出现 `NO comparable pair at all`（"一对都没比上"），并断言 artefact 里 `compared == 0 && missing == 58`。批推进后（**试点段 58/58 完成**、主池刚开始）live 的实际形态变成"**5 对可比 / 53 对缺**"（缺的是**主池**侧）→ 两条红了。**被测的性质并没有变**：live 状态**必须被拒**、`h4_pass` 必须为 False、拒绝必须点名预注册的 58。**失效的是快照，不是性质。**
    **判据（可复用）**：① 断言要问**性质**（必须被拒 / 守恒式 `compared + missing == 期望数`），不要问**形态**（具体取值）；② **一条会随外部状态推进而失效的断言，等于一条不再守任何东西的断言**；③ 一句话自查："把它写成守恒式，外部推进会不会让它变红？写成具体数值式，会不会一定会变红？"会 → 改守恒式。
    **边界**：不是所有快照都要去掉——**合成夹具的快照是对的**（夹具自己造的，状态不会动）；只有**针对 live / 真实状态**的断言才必须按性质写。

### ㉭ 无人值守链的看护必须跨故障域；文档里的"不要做的事"不会自己修东西（2026-10-26）

**事情**：r30 的扩面批链（批 + 看门狗 + 两个触发器 + 两个看护）全部活在同一个 WSL 实例里，
`.wslconfig` 又设了 `vmIdleTimeout=180000`（空闲 3 分钟释放整台）。2026-10-26 凌晨约 07:23
整台 WSL 消失，链上六个进程**一起没了**，主池停在 1100/1393，**无人知晓**；上午我例行巡查才发现。
独立审计在上一轮已经点名过这条风险（"最需要修的一处不在链里而在链外"），但**那只是写在报告和 handoff 里**。

**代价**：几乎为零（1100 个回执 rc 全 0，逐键 resume 语义使重启只补 293 个键，段 0 门重跑通过、
试点段 30 s 跑完 58 键＝全跳过）。**但如果再晚一天没人巡查，扩面族会一直停在"看起来在跑"的状态**——
这正是无人值守最坏的失败方式：**不响、不报、只是不动**。

**教训（三条）**：
1. **看护若与被看护对象共享同一个故障域，它就不是看护，只是同一个故障的另一个受害者。**
   修复：把看护放到**宿主侧**（`scratch/ext_chain_supervisor.ps1`，Windows 进程），
   并让它**自己知道什么时候该收工**（链跑完即退出，内存按 `.wslconfig` 的本意归还）。
   附带的好处：**看护的轮询本身就是一个 WSL 进程，顺带把虚拟机拉住不被释放**。
2. **"无人值守"这个词，此前只覆盖了"WSL 活着的时候"。** 写 handoff 的"不要做的事"是有用的，
   但**文档不会自己修东西**——风险要变成**另一个故障域里的进程**才算被处理。
3. **恢复脚本必须幂等，而且必须知道"别人正在做交接"**。段 8 的交接会**故意**停掉批与看门狗再以
   `--with-control-replicate` 重启；若恢复脚本落在那个窗口，就会拉起一个**不带开关**的批，
   对照池段永远跑不成。故恢复脚本读触发器日志的 "the batch has exited" / "handover done" 计数，
   **交接未完成时一律不碰批与看门狗**。

**顺带记一个技术坑**：`grep -c` 在**零匹配**时退出码为 1，于是 `$(grep -c ... || echo 0)` 得到
**"0\n0"** 两个零 → `[: 0\n0: integer expression expected`。要写"计数"就别用 `|| echo 0` 兜底，
**取计数本身并做数字清洗**。这条在两个脚本里都踩了。

### ㉮ 无人值守的看护必须由操作系统拥有，而不只是"跨故障域"（2026-10-26 下午）

**事情**：同一天里，扩面批的无人值守链**丢了两次**。第一次（凌晨 07:23）是 WSL 实例被释放，
链上六个进程一起消失；**修法**是加一个跑在 Windows 侧的看护，跨过 WSL 这个故障域。第二次（11:44）
**链又全没了**，而那个 Windows 侧看护**自己的日志也停在同一分钟**——**它也没了**。

**根因**（第一版修复自己查出来的）：它是 `Start-Process powershell` 从**工具会话**里起的。
**Windows 上 `Start-Process` 起的子进程仍在启动它的会话的作业对象里**，会话一清理，子进程跟着死。
它从 10:08 活到 11:43 只是因为那次会话的清理更晚。**"跨故障域"这个说法不完整**——
真正跨故障域意味着**由操作系统拥有**（计划任务 / 服务 / Run 键），而不是由任何一个会话拥有。

**修法（本会话无管理员权限，所以走两条免提权、互为补盲的通路）**：
1. **`schtasks` 计划任务**（`/sc minute /mo 5`）——每 5 分钟轮询一次；
2. **HKCU Run 键**——每次登录起一个实例（覆盖"机器重启"）；
3. **单例锁**（PID 文件）：两者会叠加触发，所以看护启动时先读锁里的 PID，
   **那个进程还活着就退出**。实测第二个实例记 "holds the lock -> exit"，**进程数恒为 1**。

**教训（两条）**：
1. **"无人值守"要成立，先问"这个进程归谁所有"**。由会话起就随会话死；由系统起就随系统活。
   **同一个洞踩两次，两次都是"归谁所有"的问题**——第一次是"看护与被看护对象共享故障域"，
   第二次是"看护与启动它的会话共享生命周期"。**每次修完都要问：下一个会杀死它的是谁？**
2. **一个会自我报告的组件要能区分"我失败了"和"没人来问"**。本条的宿主看护把状态写在
   Windows 侧，**所以"它不在了"这件事本身是可见的**——这比"它还在但工作着"更难得：
   **沉默的失败最贵**。

**顺带**：PowerShell 里**函数必须先定义后调用**（守卫里调 `Write-Status` 时它还没定义，
于是带着 "is not recognized" 报错退出——守卫本身是生效的，但报错会掩盖真相）。

### ㊱ 判断一个物理能力在不在，先去二进制里找那个命令（2026-10-26 下午）

**情境**：用户要求“跑完 RCX 提取寄生参数，拿签核级 WNS”。批正在跑，不能起 EDA。
第一反应是“写个 TCL 跑一下看行不行”——那要起 OpenROAD、要设计、要时间，而且**失败模式模糊**（是命令不存在？是参数错？是许可问题？）。

**做法**：先做**能力体检**——对可执行文件本体与它 `ldd` 列出的全部 `.so` 做二进制字符串检索：
`extract_parasitics` 命中 **0**、`set_rcx_layer_rules` **0**、`estimate_parasitics` 2、`write_spef` 4、`read_spef` 5；
再把二进制里所有含 `parasitics|spef|rcx` 的符号**全列出来**（`rcx_tcl_inits`/`rcx_py`/`spef_reader`/`diff_spef`），
于是分清了两件不同的事：**OpenSTA 侧会读写 SPEF** ≠ **OpenROAD 侧会做布线级 RC 提取**。

**代价对比**：检索 83 MB 二进制 + 30 个 `.so`，秒级、零设计、零副作用；
而“跑一次看报错”要几分钟到几十分钟，且**测不出能力边界**（失败原因不可分辨）。

**教训（两条）**：
1. **“能力有没有”是可以静态回答的问题**，别用一次运行去回答。**“命令不在二进制里”与“命令用法错了”必须分开**——前者是缺件（要换工具/编译），后者是写法问题（改 TCL 就行），混起来会让人去改一行本来没错的代码。
2. **静态检索要检索“链接闭包”，不能只搜主程序**：命令可能住在 `.so` 里；反过来，只搜主程序也可能漏掉**同名但不同物**的符号，所以还要**把相关符号全列一遍**再逐个判断归属（本例 `rcx_*` 全属 OpenSTA 侧）。**“命中数 0”只能证明“不在这些文件里”，不能证明“工具没有这个能力”**——所以结论必须限定到**本机这个构建**。

### ㊲ 文档会过期，进程命令行不会（2026-10-26 下午）

**情境**：`scratch/post_ext_chain.sh` 的文件头注白纸黑字写着“对照池 `round35_ext_t1` **按决策 D1 不再跑**，所以 `--guard-batches default` 模式**永远红**”；而 `scratch/ext_control_pool_trigger.sh` 的头注写着（引 OI-058，2026-10-25 项目负责人决策）会用 `--with-control-replicate` 重启批把那 389 键**跑起来**。
两份文档、同一件事、互相矛盾——而**这条链当时正在无人值守地跑**。

**处置**：不按文档站队，按**运行态**判定：`run_ext_batch_v3.sh` 是否真有 `--with-control-replicate` 开关与段 8 实现；
**当前批进程的命令行**（`pgrep -af`）；交接日志是否已发生过。**文档只是线索，不是证据**。

**教训（两条）**：
1. **决策会改，文档不一定跟着改**：被推翻的决策（D1）会继续留在被它改过的文件的头注里，**而后来者读到的是"看起来很权威"的旧结论**。头注越详细、越像判决书，越危险。
2. **无人值守的链上，"文档过期"会变成"链停住"**：如果照头注去把触发器改成 `v3`，就会**放弃对 389 个回执的校验**；如果照头注判定 `default` 永远红，就会**永远不跑链**。所以**链上的每个判据都要有一个"当前是谁说了算"的指针**（本例是 OI-058），并**定期用运行态复核**，而不是靠注释。

### ㊳ “DONE”只能由 rc=0 产生；标记里的 rc 必须被读（2026-10-26 傍晚）

**情境**：一条无人值守链的最后一个触发器，用一个标记文件防重复执行，标记里存的是**退出码**。
但“已经跑过了”那一分支**只判标记是否存在**，于是链失败（rc=2）后，任何一次重启都会写出 `state=DONE`。
而 `DONE` 是这条链上**唯一**的“科学产物已存在”信号：探针的 `finished`、下一段的放行条件、
宿主看护写“读数已就绪”的条件，**全都只认 `DONE`**。于是：**失败会被自动宣判成成功**，
连“读数已就绪”的持久标记都会被写出来。同一类洞在两个触发器里各有一个（F3 那个还多一处：普查失败时把标记写成**硬编码的 0**）。

**教训（三条）**：
1. **“完成标记”与“成功标记”必须分开**。如果标记里存的是退出码，**读它的每一处都必须读那个值**；
   “文件在”只说明“**跑过了**”，不说明“**跑成了**”。写 `DONE` 的唯一合法条件是 `rc == 0`，其余一律失败态。
2. **失败态必须比成功态更显眼**：失败的分支要**常驻**（让看护持续报警），而不是退出——退出会被自动重启，
   而重启正是把失败洗成成功的那个动作。**自动重试在这里是错的**：重跑会烧 CPU、会覆盖报告；
   “要重试”是**人**的决定，不是触发器的。
3. **同型缺陷要一次搜干净**：发现一个之后，要去问“这条链上还有谁读这个标记、还有谁写这个标记”，
   本项目因此一次改掉了两个触发器 + 一个硬编码的 `echo 0 > $MARKER`。

**顺带（同样值得记住）**：**存活判定不能只看命令行**。`pgrep -f` 匹配的是命令行，
于是①脚本里的 `$(...)` 会产生**同名子进程**，②测试残留的沙箱实例与真实实例**命令行完全一样**（区别在**环境变量**里），
两者都会让“组件还活着”变成假绿。本轮实测两次踩到（一次让真实触发器根本没起来而探针仍报 alive）。
**判据**：看 `/proc/<pid>/environ`（并排除父进程同名的子进程），不要看 `/proc/<pid>/cmdline` 就下结论。

### ㊴ 无人值守的"活着"要有证据：状态行必须能说出"多久没进展了"（2026-10-27 上午）

**情境**：一条跑了两天多的无人值守链昨夜停了 **13 小时**。早上看状态：
回执计数 **1261/1393**、**rc 全 0**、状态文件 **`state=OK`** ——**一切正常**，
因为**这些量只在"此刻"是对的**。真正丢掉的 13 小时，**在任何一个当时的状态行里都看不出来**。
（链本身没问题：宿主不在线，唤醒后 40 秒自愈，**零数据损失**。）

**教训（三条）**：
1. **状态量必须带时间维**。"现在有多少"不能回答"它还在动吗"。加两个字段就够：
   **`last_rc_age_min`（最新回执的年龄）** 与 **`outage_min`（超过阈值多久没进展）**。
   本轮实测：那 13 小时从"不可见"变成状态文件里的 **`outage_min=787`**。
   **没有这一行，这个故障会一直"看起来正常"地持续下去。**
2. **静默失效的代价高于崩溃**。崩溃会留下错误码和栈；静默失效留下的是**一份漂亮的正常报告**——
   而报告越漂亮，越没有人去看时间戳。**看护自己写"OK"的时候，也要能写出"多久了"**。
3. **根因常常在"链之外"**：这次不在批、不在触发器、不在恢复脚本，而在**宿主计划任务的 XML**
   （电池即停、空闲即停、无时限、注销即失效）。**排查"无人值守为什么停了"，
   要从"谁拥有它"一路查到"拥有者的配置"，而不是只查链上的脚本。**
   同一次排查还暴露了一个更隐蔽的点：**`MultipleInstancesPolicy=IgnoreNew` 让"每 5 分钟一次"不是备份，是被拒绝**——
   `Last Result = 0x800710E0`（"操作员或管理员拒绝该请求"），**看起来有冗余，其实冗余的那条路从未被走过**。

**顺带**：`RestartOnFailure` 在任务 XML 里**必须排在 `AllowStartOnDemand` 之后、`MultipleInstancesPolicy` 之前**；
顺序错了，调度器**不报错、静默丢弃**那个元素——**"导入成功"不等于"你要的设置生效"，必须回读存储后的 XML 逐项核对**。

### ㊵ 告警必须每轮重新计算，而且必须说出“这一轮到底是什么”（2026-10-27 上午）

**情境**：给看护加告警时，读代码发现一个更基础的问题——轮询循环里的 `$alarm`
**只在出错那一支被置真，从不复位**。PowerShell 的变量跨循环保留，于是
**一次 ALARM 之后，状态永远是 ALARM**，而文案永远写死为“post-chain step FAILED”，
**哪怕真正出问题的是别的东西**。

**教训（三条）**：
1. **告警状态要在每轮开头清零**，并且**把“这一轮的原因”一起算出来**，
   而不是只存一个布尔量。否则**告警越多，状态越没用**——读者会学会忽略它。
   这条在别的语言里同样成立（循环外的标志位、粘性的状态字段，是同一类病）。
2. **“计数正常”不等于“事情在推进”**。本轮补上的四种告警共同点是：
   **在计数上一切正常**（回执数、rc、状态文件都正常），但链其实没在动：
   没有进展、恢复无效、交接没发生、下一阶段卡住。
   → **告警要盯“时间”和“变化”，不能只盯“当前值”**。
3. **静默失效必须能被区分成不同种类**：机械性的（一对都比不上）与物理性的（有的对不同）
   **必须分开报**，否则**机械故障会被读成物理结论**。本次 exit 2 的两种含义就是这样一个坑：
   产品本身措辞正确，**只有一行日志在误导**——所以修的是那行日志与状态文件，
   **没有碰测量逻辑**。

**顺带一条夹具教训**：**沙箱夹具的行尾也会骗人**。PowerShell 的 `Set-Content` 写 CRLF，
而 bash 脚本行尾的 `\r` 会跑进 `cat` 的路径参数里，报出来是 “no such file or directory”，
看起来像**被测对象坏了**，其实是自己造的夹具坏了。**写 bash 夹具就写 LF**
（`[System.IO.File]::WriteAllText($p, ($lines -join "`n"))`）。

### ㊶ “活着吗”要问环境，不能只问命令行（2026-10-27 上午）

**情境**：切换一个常驻触发器时，脚本报“**已经在跑，别起第二个**”——**其实那是一条上一轮
被取消的沙箱测试残留**。它的命令行与真实触发器**一字不差**（都是
`bash .../ext_post_chain_trigger_v2.sh`），区别只在**环境变量**里（夹具的 `EXT_ROOT` 指向 `/tmp`）。
结果：**真实触发器根本没起来**，而 `pgrep -f` 命中残留 → 探针照样报 `post_chain=1`
→ **一个死掉的组件看起来活着**，看护不会去复活它，链会静悄悄地停住。

**教训（三条）**：
1. **“进程在”不等于“就是它”**。命令行可以被**一模一样地伪造**；**环境变量不会**。
   要判“是不是那个组件”，就把**身份证据**也读出来（`/proc/<pid>/environ`）。
   **并且要把它显示出来**（本轮加了 `sandbox_leftovers=` 计数）——**看不见的残留会一直冒充活人**。
2. **排除条件要写窄**。真实组件是 `EXT_ROOT` **未设**（用脚本内置默认根），
   所以只能排除 `/tmp/*`；**把“未设”也算成夹具，会杀掉真实进程**——
   我今天已经因为这个误杀过一次真实的触发器（误判“未设=沙箱”）。
   **判别身份时，先把真实样本的环境看一遍**，再写排除规则。
3. **正则、glob、引号三者混用最容易出“永远查不到”的错**。`pgrep -f` 认正则，
   `case` 认 glob，而**带引号的变量在 `case` 模式里是字面量**：
   `case "$cmd" in *"$pat"*)` 里 `"$pat"` 会连反斜杠一起去找 → **健康链被判成死的**。
   本轮第一次写 v3 就栽在这里（批与看门狗报 0）。**先问一句：这一层的匹配语义是什么？**

### ㊷ 写完不等于写对了：记录文件要扫 U+FFFD（2026-10-27 上午）

**情境**：给一批记录（LOG/经验库/状态文档）追加内容后，顺手扫了一下替换字符，
发现 `LOGS.md` 里有**四处 U+FFFD**——非法字节被解码成的替换字符，
**其中三处来自前几轮我自己写的**，一段话读出来是「不会造□活锁」这种样子（**□ = 一个被毁的字节**）。
**没有报错、没有异常、写入返回成功**。

**教训（三条）**：
1. **「写入成功」不等于「字节正确」**。经由某些写入路径（尤其是"读—改—写"整文件替换、
   或者跨编码边界的拼接）时，**一个字符可能被毁成 1–3 个替换字符**，
   而 API 层面一切正常。**记录类文件必须写完就扫**：

   `text.count("\ufffd")` 一行就够，**把这一条写进终检脚本**，让它每次都跑。
2. **判据要能自证**：**3 个连续 U+FFFD = 一个被毁的三字节汉字**（字节数对得上），
   **2 个 = 混入的多余两字节残片**；再叠加「删掉后句子是否通顺」与
   「同一段散文是否有干净副本可对照」——**三者对不上就不修**，
   **绝不许蒙一个字符上去**（蒙出来的字可能改变原意，而记录一旦被改就没人知道原文是什么）。
3. **坏字符是"静默的失效"**：它不影响任何门、不触发任何异常，
   只在**有人引用那句话的时候**才被发现。所以**扫字符这件事要自动化**，
   不要指望"下次读到时顺手发现"——下一个人不一定读得到那段。

**顺带**：**历史记录被修，也要追加一条披露**（本项目规矩：不倒改历史）。
**「修的是坏字节」和「改了结论」必须能被区分开**——披露条目要写明：
修了哪几处、每处还原成什么、依据是什么（字节数／通顺性／干净副本）、
以及**没有改任何数字与措辞**。

### ㊸守门分支先证明它能被触发：写完要修正，不要信自己的推理

**情境**：r61 给看护加一个新分支——“族内带的产物失败/卡住就 ALARM”。
写完后自认了一遍（触发器确实不写 WAITING、
FAILED 要拆成物理发现与机械失败、
判据用 `floor is not zero` 而不是 `DIFFER`），似乎无疑。
然后跑沙箱：**44 项里 7 项失败**，而且失败的不是我猜的那两个新用例。

**三个真实结论（都是“读不出来的”）**：
1. **我写的补丁把自己写贯了**：插入新块后同一段文本出现两次，
   `replace(old, '', 1)` 删掉的是**刚插入的那份**，
   “前移”被完全抵消。→ **补丁脚本自身也要被测试**，
   不能只测被修的东西。
2. **旧代码里的一个小缺口正好杀死了我的新分支**：
   探针键名正则 `^([A-Za-z_]+)=` **不允许数字**，
   而对照池计数发布为 **`t1=389`** → `t1` **从未进过 `$kv`**，
   看护从来就**不知道对照池有多少**。
   于是我的新分支恒取 0、**是条死分支**。
   → **当你新加一个分支时，先确认它读的那个值真的能被拿到**；
   否则你只是加了一只不会响应的监控。
3. **断言失败时先怀疑自己的夹具**：两个新用例“失败”的方式是
   **条件算出来为假**（而不是抛异常），
   它指的是“输入没进来”，而不是“逻辑写错了”。

**常规补丁（不要越位）**：
- **修正卡死分支**（它不是输入，它挂了不会报错）→
  **一般化的规则：产物的「交付”不能只由它的下游验收——
  它必须自己有一个独立的守卫。**
- **触发器写的状态本身就是契约**：取哪个值作为“正常”、
  哪个值就是“异常”，必须回到**触发器源码**里确认它真的写哪些值。
  否则就会给自己写一个**永远不会触发**的条件。
- **分类判据要选“只在目标分支出现”的特征字符：
  本轮用 `'DIFFER'` 就误判了（**`-match` 不区分大小写**，
  而相似的理由里含 `differ=0`）。
- **修正一个表达式时，要顺手检查它的每个依赖项**：
  本轮的依赖项就是**那个计数变量**（`$kv['t1']`）。

### ㊹恢复脚本也是被看护的对象：守卫的窗口要覆盖真正危险的窗口，而不是日志标记出现的时刻

**情境**：扩面族的批跑完之后，交接触发器要把批换成带 `--with-control-replicate` 的，
中间会把看门狗**杀掉**（它不能在交接期间重启死批）。
恢复脚本是全链的救命绳，它有一个守卫：“交接进行中就别碰批和看门狗”。

**三个真结论**（都是逐字读源码确认的）：
1. **守卫的窗口必须覆盖真正危险的窗口**，而不是“日志里出现了某个标记”的时刻。
   触发器在步骤 2 就杀看门狗，而“交接进行中”这个标记到步骤 3 才出现
   → 两者之间的那几分钟就是窗口，而守卫在这里是空的。
   **规则**：**守卫的起点要定在“已经有东西被杀了”那一刻**，
   而不是“下一个信号到了”的时刻。
2. **“期望作业数”可配置的地方，配错的后果不是“多重启几次”，而是“永久退出”**。
   普通看门狗的期望数是 2844（没有 389 那个对照池）。它到 2844 就写 `state=FINISHED` 并 **break 退出**——
   而当时对照池还有 389 键没跑。**一个只数了一部分作业的完成判据，会在另一部分还没完成时宣布完成并退出**。
   → **对“可配置的期望值”要多问一句：配错了会产生什么后果？**
3. **恢复脚本必须能被测试**，而不是“只能靠人类比”。
   它是启动引擎，一面写它一面靠它救场——**它自己就是被看护的对象**。
   本轮给它加了 `RCV_DRY_RUN=1`（只打印不启动）与可注入的 ROOT / 回执根 / 存活判据，
   然后用 7 个场景的夹具把它的**决策**全部测了一遍（**771f链从未被碰**）。
   → **给“会启动真东西”的脚本加一个“什么都不启动”的模式**，
   并把它的所有判据都推到可注入的输入上。这不是测试的师父，这是**供应链的应性**。

### ㊺在跑的脚本不能就地改；改的流程是「停 → 改 → 起」（且要把脚本自身的 sha256 写进状态行）

**情境**：我要给一个**常驻**的 bash 触发器加一条语义，直接就把它**就地编辑**了（插入约 20 行）。本项目的规矩是明文禁止的：**运行中的 bash 脚本不可就地编辑（按字节偏移增量读）**。

**为什么严重**：bash 脚本**按字节偏移读自己**：插入行会把**其后所有内容**的偏移顺带一起挪弓，进程从 `sleep` 里醒来时可能**执行错乱的命令**。这不是风险论，是**字节字法实事**。

**正确流程（已固化为脚本，三步中间有断言）**：
```
1. 停掉实例        → 2. 断言「没有实例在跑」 → 3. 改文件 → 4. 起新实例
```
断言不过就**不改**（绝不带着活实例改文件）；新实例从头解析新文件。

**一个便宜的附属保护**：让脚本**把自己的 sha256 写进状态文件**（`script_sha256=`）→
“这个文件在实例运行期间被不被改过”这个问题，**从状态行就能回答**，不用猜。
本轮启动后状态行里的 sha256 与文件实测**逐字一致**（`ff1dcd4a…`）。

### ㊻`$( )` 是命令替换，不是变量展开：与 `$` 只差两个字符的东西，会静静地返回空值

**情境**：状态行里写 `echo "script_sha256=$(SELF_SHA)"`，变量**确实被正确赋值了**，但状态文件里那一行**是空的**。

**原因**：**`$( )` 是命令替换**（执行裸中的命令，把输出拼进去），**`${ }` 才是变量展开**。
`$(SELF_SHA)` 对应的是“执行一个名为 `SELF_SHA` 的命令”→ `command not found` → 空值。
**阅代码时看不出来**（两者只差两个字符）；**是 `set -x` 的跟踪抓到的**：
`++ SELF_SHA` / `SELF_SHA: command not found`。

**规则**：
- **变量展开用 `${ }`**（尤其是在字符串里、或需要清晰边界时）；**`$( )` 只用于真正要执行命令的地方**。
- **空值不报错时，先用 `set -x` 追踪那一行**：它会把“变量是未设置”、“命令不存在”、“退出码非零”分开。
- **变量被设为空串与“未设置”是两件事**：若用 `set -u`，未设置会直接终止脚本。上面这个例子里变量**是设置了的**（`[ -n "$X" ] || X=unknown`），但表达式是**命令替换**→ 变量**并未**被读取。

### ㊼一个检查“通过”时，也要问“它真的检查了吗”：管道的退出码是最后一个命令的

**情境**：我给链的第 0 道门（作业表完整性）写检查：
`sha256sum -c JOB_TABLES.sha256 | sed ...`，然后 `if` 判断退出码。结果报了 **PASS**。

**两个错叠在一起，一个比另一个更危险**：
1. **清单格式不对**：家族的 `JOB_TABLES.sha256` 是自定义格式
   （`<名>  sha256=<哈希>  (source <路径>)`），`sha256sum -c` **根本不认**，
   它只打印了一行「no properly formatted checksum lines found」——**而我那句 if 没看到。**
2. **管道的退出码是最后一个命令的**：`sha256sum | sed` 的退出码是 **sed 的**（永远 0），
   不是 sha256sum 的。所以它报的是 **sed 的退出码**，而不是检查的结果。
   → **一个什么都没查的检查报了绿。**

**三条规则（本轮实际用了）**：
1. **判断退出码时不要用管道**；要么不管道，要么用 `PIPESTATUS`。
2. **每个检查都要断言「我确实比对了 N 个」**（如 `CHECKED -eq 3`）——
   **空解析必须响亮地失败**，而不是静默地过。
3. **给检查配一个负向对照**（故意改坏一个输入 → 检查必须变红）。
   **没有负向对照的检查，它的绿灯是未经验证的**。
4. **用被测对象自己的解析方式**（这里是链自己的 awk 解析），
   不要用「看起来像」的通用工具。

### ㊽一次性的动作必须留「已完成」标记，而执行它的组件必须**常驻**——否则会变成「缺组件 → 恢复 → 再缺」的循环

**情境**：无人值守战役里有一个**一次性**动作：把批从「跑三段」换成「跑第四段（对照池）」（叫「交接」）。
交接触发器做完这件事就**自己退出了**。而恢复脚本的逻辑是「缺哪个组件就补哪个」→ 它发现「没有交接触发器了」→ **又起了一个** →
这个重复实例**又走了一遍交接**（把刚起好的看门狗杀了），然后卡在「等批退出」——**批要跑完 389 个键才退出** → 对照池段在剩下的时间里**没有看门狗**。
而这个循环**每 5 分钟重复一次**（恢复脚本又发现「没有触发器了」）。

**原因**：**「谁执行了一次性动作」与「谁需要常驻」被当成了同一件事**。
一次性动作做完，执行者就消失了；而下游的「缺了就补」逻辑把「执行者不在」误判成「需要再执行一次」。

**规则**：
1. **一次性动作必须留下一个「已完成」标记**（写在日志里、或者一个状态文件），让后来的同型实例**一眼看出不用再做**。
2. **发现了「已完成」的实例必须变成无害的常驻观察者**，而不是「再执行一次」——本轮的做法是转成**常驻看护**（每 5 分钟报一次进度），这样「组件存活」这个不变量也保住了。
3. **恢复脚本的守卫要问「这件事现在还有可能发生吗」，而不是数日志标记**：
   计数（几次开始、几次完成）在**有实例死在中途**时会被永久误导。
4. **「常驻组件自己退出」是危险动作**：它会让「缺组件 → 恢复 → 再缺」循环起来，并最终变成**假告警**。

**附带的一条**：**夹具若与代码共享同一个错误前提，它会让回归套件全绿却零覆盖**——
本轮那个「45 分钟保险阀永远不触发」的 bug，**夹具日志用的前缀和代码用的前缀是同一个错的前缀** → 20/20 全绿。
**所以套件必须每次从活脚本刷新夹具**，并且让夹具**尽量贴近真实日志**（前缀、时间格式都要一样）。

### ㊾永久红的告警 = 永久被忽略的告警：告警必须**每轮重算**，判据必须指向**当前在跑的那一段**

**情境**：三个告警同时红着，其中两个是**假的**：
① 「宿主可能不在线，已经 277 分钟没有进展」——其实批在跑、回执每分钟都在产出；原因是**掉线判定只扫已经完成的那一段**（那一段完成后就冻结，年龄单调增长）；
② 「批一直在死」——其实批很健康；原因是**把批每跑一个键就 fork 的临时子进程当成了「批重启」**；
③ 而且这个告警**粘住不清**：条件消失后状态仍停在 ALARM。

**原因**：
- **判据指向了错误的对象**（冻结的段，而不是正在跑的那一段）；
- **进程集合不等于进程身份**（子进程继承了同样的命令行）；
- **告警变量在轮询之间保留**（置真之后从不复位）→ 一次误报就变成永久误报。

**规则**：
1. **掉线/停滞判定必须扫「当前在跑的」全部对象**（本轮：四个批段全扫，取最新回执），且**「事情已经做完」不算掉线**（做完之后本来就不会再有回执）。
2. **计数进程身份时只数进程树的根**（父进程也在那个集合里 → 它是子进程，不算）。
3. **告警每轮重算**，不粘住；条件消失就必须回到正常状态，否则后来发生的真告警会被盖住。
4. **任何告警都要问「它红了多久」**：一个连续红了几小时的告警，第一嫌疑是**它自己坏了**，不是被看的东西坏了。
5. **看护与演练都不能写生产树**：演练用合成夹具跑真链时，**输出路径必须可注入**，否则夹具的失败会变成生产的失败（本轮：演练把生产的曲线状态写成「FAILED rc=2」）。


### ㊿同一个工具被用两次时，它的「自我描述」必须**模式感知**——否则产物会否认自己做过的事

**情境**：一个比较工具被用在两处：① 链的门（试点池 vs 主池，期望 58 对）；
② 族内地板（**对照池** vs 主池，期望 389 对）。机制两处都对，但工具里
「这是什么 / 这不是什么」和 txt 页脚**只有一份**，写死给①。
于是②那份产物里写着：「**对照池不在这份比较里**……对照池与主池的比较按构造就相同、什么也证明不了」——
而②**恰恰就是在比较对照池**，并且「是否逐位相同」是**要测的假设**，
不是可以先行断言的前提。这句话还引用了一条**已被推翻的旧决策**。

**原因**：**工具的输出里混着「机制」和「对机制的解释」**，
而解释被当成了机制的一部分、被复用了。复用解释的风险是：
它会**随调用场景改变含义**，而产物是**要被别人按字面引用的**。

**规则**：
1. **产物里的任何「这是什么 / 这不是什么」都必须能在产物里找到判据**——
   至少写一个机器可读的**模式字段**（本轮加的是 `comparison_mode`），让读者一眼看出这是哪一次调用。
2. **一份工具被用于两种场景时，措辞要分支**；判据要**只用已有的标识**（本轮用批次名），
   不要引入新的数据依赖。
3. **引用的旧决策要查它是否已被推翻**：产物里出现「按决策 D1 …」时，
   如果 D1 已被后来的决定推翻，**这句话本身就是错的**。
4. **提前验「从未在真实数据上跑过」的那一环**：本轮在对照池只完成 117/389 时就用真实树
   **只读**跑了一遍——机制是通的（117 对逐位相同、DIFFER=0），
   **但产物会自我误述**这件事只有真跑一遍才看得见。
5. **顺便**：Unicode 带圈数字的真实编号**必须查 `unicodedata.name()`**——
   按码位偏移算会错（㊨ 的真实编号是 29，不是 41）；带圈字符本身可以作为编号用，
   因为它天然连续。


### 51 派生数字在展示前必须重新派生（或校验新鲜度）；「已完成的键」不是随机样本

**情境**：状态页要报「这场无人值守战役还剩多久」。它读的是估算器写下的 JSON。
某轮实测：状态页报「剩 123 键 ≈1.61 h」，而真值是 **31 键 ≈2.33 h**——
那份 JSON 的时点是 **100 分钟前**的，状态页**从不校验新鲜度**。

**原因（两个独立的坑）**：
1. **派生文件被当成事实源**：JSON 曾经是对的，于是被读成「当前值」。
   派生文件的价值在于「便宜地重算」，一旦不再重算，它就是**上一刻的快照**，
   而且**看起来和实时值一模一样**。
2. **定价用的样本不是随机的**：估算器按「同电路**已完**键的秒数中位数」给剩余键定价，
   缺样本时落回全段中位。实测：已完成 357/389 键里**没有一个 b12**，
   而剩下的 31 键里 **19 个是 b12**（慢电路）→ 全部按「全段中位 101 s」定价，
   而主池对同一网表的实测是 **284–1254 s** → **低估 4.93 倍**。

**规则**：
1. **状态页在展示派生数字之前，先重新派生**；派生失败就**报失败**，
   绝不继续显示上一次的值（“报旧数”比“不报”更坏：它看起来是新鲜的）。
2. **任何派生输出都要带时点**，并在展示时**显式打出年龄**；超过阈值就标成过期。
3. **给「未完成」的量定价，要用与它**同名、同实现**的独立实测**（主池跑过同一网表），
   不要用「同一段里已完成的那些」的分布——**先完成的永远是快的那批**。
4. **回退值要能被看见**：本轮把「用了哪个口径、落回了几次」写进输出
   （`n_priced_by_main_pool_same_key` / `n_priced_by_segment_median`），
   于是「0 回退」本身成了一个可核对的断言，而不是一句口头保证。

**附带的反面教材**：校正「对照池比主池快 3.8 倍」时，
**358 对同名键的逐键配对**给出的是 **0.9533**——两池成本基本相同。
那个 3.8 是「按主池秒数定价」与「当时的速率」之比，而**速率是混合电路的加权**。
**速率不是逐键比值**：要比较两个池的快慢，就逐键配对，不要拿速率相除。

### 52 门要覆盖「文件不在了」；观察器到期不等于被观察对象失败；子 agent 的结论也要自己复核

**情境**：链即将自动起飞（一次性、失败不自动重跑），于是派两个只读 agent 并行审计
「收齐后会不会自动起飞」与「第 3 步 + 六产物契约」。审计抓出三处，其中两处是**门本身的问题**。

**一、门要覆盖「文件不在了」**
- 体检判族内带：读 `verdict or floor_ns or two_sigma_ns`，**只要求非空**；
  可产物的真字段是 `verdict`（DETERMINISTIC / **REFUSED**）与 `in_family_reproducibility_floor_ns`，
  `floor_ns`/`two_sigma_ns` **在产物里不存在** → **`REFUSED`（对不一致 → 不出带）也判 PASS**。
  **假绿，且恰好落在最该拦下的情形上。**
- 内容级检查：`已删除` 的文件只打印、**不计数、不影响退出码** → 文件被删时门仍绿；
  汇总行还写「真差异 = 12」，与它上一行 `paper/ 真差异 19` 自相矛盾（删除数被漏在总数外）。

**规则**：
1. **「差异」要按类别分清**（内容变 / 文件没了 / 新增未跟踪），**每一类都要计数、都要能变红**；
   汇总数必须等于各分类之和（否则总数本身就是假的）。
2. **判据要用产物里真实存在的字段名**——`d.get(a) or d.get(b)` 这种写法在字段不存在时
   会**静默换口径**：第一个字段拿到 `REFUSED` 就算过，而真正的数值字段压根没被读。
   **更稳的写法是「白名单式」**：明确要求 verdict 是某个**确定值**、数值字段能解析成数字。
3. **判据要能表达「没有也等于坏」**：族内带的 REFUSED 是「**结论是坏的**」，不是「结论缺失」。

**二、派生产物要判新鲜度**
链**不删**上一轮的产物，而曲线生产者与 F3 普查都是**先写文件、再判内容可用**
→ 重跑失败时体检会读到**上一轮的旧文件**而假绿。
**规则**：以本轮链的 `started_at` 为基准，**比它更早的产物一律判失败**；
否则「跑过一次再失败」会伪装成「跑成功了」。

**三、观察器到期 ≠ 被观察对象失败**
我的观察器硬编码「最多等 25 min」，而实测还要 1.8–2.3 h → 它**到期退出**。
**退出的是观察器**。若把「观察器没了」写成「战役挂了」，就会去查一个根本没坏的链路。
**规则**：观察器超时时**只报告现状、不判失败**；等待窗口按**实测 ETA** 设，别按直觉设。

**四、子 agent 的结论也要自己复核**
agent 报「族内带触发器尚未启动、状态文件不存在」——实测该触发器**已等待 15.4 h**，
状态文件本来就要等 389 键收齐才写。**它把「等待期的正常形态」当成了「缺件」。**
**规则**：子 agent 的结论是**证据**，不是结论；凡是要据此改动动作的，先用**独立的一手观测**复核一次
（这里是 `ps` 的进程表 + 触发器自己的日志）。

### 53 一次性组件的「终态」不止一种；组件列表要覆盖全链路；恢复脚本必须知道当前纪元

**情境**：族内带（对照池 vs 主池）给出三种状态之一：**OK / REFUSED / ALARM**。
`REFUSED` 的含义是「**389 对里有对不一致 → 这族有跑批噪声 → 不出带**」——
带看护自己的 reason 里写着「a legitimate scientific outcome, **not a failure**」。

**却出事了**：看护的组件豁免表只认 `OK`/`DONE` → `REFUSED` 被读成「组件缺失」→
复活它 → 它立刻再次判 `REFUSED` 并退出 → **连续三轮后报假 ALARM**，
而每次复活都会调**恢复脚本**——而恢复脚本在那个纪元会复活**普通批**（见下）。

**规则**：
1. **一次性组件的终态要按「结论的性质」分类豁免**：**成功**（OK/DONE）、
   **合法但不成功**（REFUSED）、**真失败**（ALARM/FAILED）——三者都要有各自的处置，
   **合法结论绝不能被当成缺件**。否则「一次诚实的结果」会变成「一次事故」。
2. **组件列表必须覆盖全链路**：漏一个（当时是 `f3_stage_a`）就意味着
   「它死了没人复活」，而轮询式系统的**静默卡死**只能靠时间戳告警揭穿。
3. **恢复脚本必须知道当前纪元**：它判断「三段齐 **且** 对照池未完成」→
   一旦对照池收齐，同一段代码就会用**plain 模式**复活组件：
   普通批会**重跑段 3 并改写 `ext_par_decision.json` / `ext_groups/`**——
   **污染这轮战役自己产出的数**。**判据要跟着纪元走，不能只写一次。**

**附带的两个自省**：
- **`pgrep -f` 的模式会匹配到我自己**：我用 `pgrep -fc 'r41_recover_chain'` 判断「有没有实例在跑」，
  报 1；实测**零实例**——匹配到的是**我自己那条包装 shell 的命令行**。
  **判「某个脚本在不在跑」要用 `ps | grep '[p]attern'`（方括号技巧），或者读 /proc。**
- **在飞脚本被就地编辑过**：本轮审计发现 3 个常驻脚本的文件 mtime **晚于**其进程启动时间，
  其中 `ext_extras_trigger.sh` 的日志里留下过 **"command not found" 碎片执行**——
  bash 会**重读**被改写的文件，于是同一个进程把新内容又执行了一遍。
  **在跑的脚本要原子替换**（临时文件 + rename，运行中实例继续用旧 inode），
  且改完要**停 → 起**让新代码生效（本轮 ps1 就是这么做的：解析器验语法 → 停 → 起 → 实测单实例 + `state=OK`）。

### 54 用真数据预演一次性链；「第一个非空路径说了算」的多路径门；「空是合法答案」必须显式实现

**情境**：一条**一次性、失败不自动重跑**的链，产出这一族全部的科学读数。它的每一道门
（完整性闸门、H4 复现门、预注册覆盖门、报告门）都可能是「跑了一整天才发现过不去」。

**一、演练（合成夹具）不能替代真数据预演**
演练证明的是**接口通**；这次死掉的地方**恰恰是「措辞与规则的匹配」**——
夹具里的数据不会触发它。做法：把每一步在**真实树**上只读跑一遍，输出全部写 scratch/
（构建数据集用 `nice -n 19`，不抢正在测量的 CPU，不写生产树）。
**收获**：链的**七步全部**在真实数据上预验过，且**第 3 步的「长杆」担忧被实测证伪**
（2844 个日志 / 2.87 GB → 34.2 s）。

**二、多路径的门：别让「第一个非空路径说了算」决定规则含义**
预注册要求「对照池读数必须标注为『合格候选子集读数』」，
检查器给了三条路径（kind / label / note），却实现成：
**找到第一个非空路径就判定并 return** → 只看 `kind` → 判红 → **根本不去看 note**
（note 里其实写着正确的话）。
**规则**：多路径的规则要么「**任一**路径满足即通过」，要么路径顺序本身就是规则的一部分
（写下来）。**更根本的一条**：门失败时先问「**读数说的是不是假话**」——
本次三处 D1 时代文案（OI-058 推翻 D1 后已成假话）会被原样发布。

**三、「空是合法答案」必须显式实现**
规则说「判决不一致**必须报告**」→ **没有不一致 = 空列表 = 合法答案**；
但通用的 `is_empty` 跳过逻辑把空列表当「读不出来」→ 判红。
**这是一条取决于数据的潜伏门**：本次真跑的不一致数是 8，**恰好没触发**；换成 0 就会死。
**规则**：凡是规则文本里出现「空是合法答案」，就给它一个**显式的 `empty_ok` 标记**，
并让检查器认它——不要指望通用逻辑碰巧对。

**四、一条链的预验清单（可直接复用）**
把链拆成「门 + 产物」，对每一道门：**用链将要用的同一个工具**、在**真实数据**上、
**输出写 scratch** 跑一遍 → 记录它的 rc 与关键字段。链是**一次性**的，
所以这件事必须在它起飞**之前**做，而不是等它跑完。

### 56 「还剩多久」要从**将要跑的那一批**的实测秒数定价，而不是从感觉

**情境**：一条无人值守链的**最后**还有两个会起 OpenROAD 的批次（F3 Stage A、b14 重测），
而「从对照池收齐到全部收尾还要多久」**从来没被算过**——它恰恰是决定
「现在要不要动 b14 / 要不要开 C 路线」的输入。

**规则**：
1. **先数规模，再谈工期**：F3 的作业表只有 **7 个键**（不是几百个）→ 工期从「未知」变成
   「作业时间 8.3 min / par=2 墙钟 4.2 min」。
2. **定价用「将要跑的那一批」的同键实测秒数**：这 7 个键是**基族**电路（b01/b02/b03/b08/b09/b10/b13），
   **不在扩面主池里** → 要回**基族 I0/I1/I2** 取同名键的秒数；
   **F3 与 F0 只差横向一轴**（met5/met2 vs met3/met2），所以 F0 的秒数是**数量级可用的代理**——
   但必须**明写它是代理**。
3. **每个会起 EDA 的东西都先做零 EDA 预检**：F3 有 `--dry-run`（打印完整计划、**不写任何东西**）、
   b14 有 `--check-only`（校验表/TCL/路径、**不启 OpenROAD**）。预检要确认三件事：
   **命令行对不对、表对不对、并发保护在不在**——b14 的 check-only 正好**当场证明**了它的并发闸门
   会正确拒绝（当时战役的 openroad 还在跑 → 它拒绝并写明「并发会污染双方的墙钟」）。
4. **收尾清单要写成可核的表**（每项：耗时 + 它产出什么 + 谁写它），
   这样「等多久」和「等的时候能做什么」都是**有依据的决定**，不是感觉。

### 57 出处表要能被别人打开：「有登记」不等于「可核」

**情境**：一张数据卡承诺「正文里每一个数字都有出处」，生成器也确实**逐个登记**了；
独立核验脚本却判它**不成立**——`FAIL: 43 provenance row(s) name a source file that cannot be found`。

**规则**：
1. **出处必须是可定位路径，不是裸文件名**：核验脚本要在「仓库根 / 卡片目录 / cwd」三处能真的打开它。
   只写 `decision_readings.json` 这种裸名，**目录一换就解析不到**——本例里 43 行就是这么丢的。
2. **描述性来源不能冒充路径**：`DATASET_CARD.md (base label family)` 这种「文件名 + 说明」是标签不是路径；
   正确做法是**路径给路径、说明放 key 列**。
3. **核验工具自己不能有硬编码路径**：写死本机绝对路径，工具就只在那一台机器上成立；
   让它**从被检对象的位置向上找仓库根**（用标志目录判定，如 `data/raw/benchmarks/source_manifests`）。
4. **门要往前移**：既然「出处打不开」在生成时就能判定，就该**生成时拒写**（本例 exit 5），
   而不是等收尾体检才发现——那时前面的产物全跑完了。
5. **改完产物要逐行核对差异面**：重生成后与旧版逐行比对，确认「差异只在预期的那一节」。
   本次实测：**167 行差异全部在第 19 节出处表内**，正文唯一变动是「生成器自身大小 / sha256」。
6. **计数对账**：两个工具报的条目数不一致时，先查清差在哪（本例差 1 是**值为空串**的登记项，不是漏项），
   再决定写进记录的数字。

**通用一句**：**一张声称「每个数字都有出处」的表，出处必须能被一个不认识这张卡的人独立打开**——
否则它只是把「有登记」换成了「有出处」的**说法**。

### 58 门红时先分清：代码坏了，还是**用例的前提旧了**

**情境**：收尾总检报 `DRILL FAILED: 3 check(s) failed`。链明明跑通并出了报告，
而用例坚持「这个状态必须 exit 7 且不写报告」。

**根因**：那条断言**当年是靠一个工具缺陷触发的**——读数里对照池的标签被写死成旧的「独立复现」口径。
**缺陷被修好、预注册语义被澄清之后，这个状态变合法了**，于是断言变成了**误报**——
它报告的不是真缺陷，是**旧语义**。

**规则**：
1. **门红先分类**：**代码坏了 / 前提旧了 / 工具环境变了**——三者的处置完全不同，
   而**按「代码坏了」去改生产侧，会把好工具改坏**。
2. **正负对照要配对**：一个状态在现行语义下合法时，把它**改成正对照**（断言它**必须通过**）；
   同时**单独造一个负对照**——把**已修好的缺陷植回副本**，用**同一个工具**判定它**必须被拒**。
   这样「不得发布」的保证不依赖缺陷长期存在。
3. **证据要有区分度**：某个规则名若**在正对照的 stdout 里也会出现**，它就**不能**用作拒绝证据。
   取证要用**只有负对照才成立**的那个信号（退出码 + 它自己的结构化产物）。
4. **副本要另存**：负对照的缺陷副本**不得覆盖**正对照的产物，并要**回头确认正对照没被污染**。

**通用一句**：**红门的含义要先判**——把「断言写在了一个已经不存在的缺陷上」当成「代码坏了」来修，
**代价是把已经正确的工具改错**。

### 59 测试要自足；断言要读对方的汇总；读数本身也会骗人

**情境**：战役收尾，四套验收套件里有两套红了。**两个红都不是生产缺陷**：
① r78 的一条断言是「**真批次仍在 pid 集合里**」——它**借了活着的生产批进程当夹具**；
战役一收尾、真批次一退，这条断言就必然失败（17/18）。
② r81 的一条断言写死「r61 必须是 **23/23**」——而 r61 当天合法地加了一个用例（变成 28）→ 假红。

**规则**：
1. **夹具必须自足**：任何依赖「活着的生产进程 / 生产现场状态」的断言，**在被测对象做完之后必然变红**。
   正确做法是把两种情形都**在夹具里造出来**（本例：沙箱里再造一个「命令行带仓库路径」的生产型假进程，
   带唯一标记、只杀自己，什么真的都没起也没杀）。
2. **快照有次序**：pid 集合是**快照**——假进程必须在**取快照之前**起。
   本例我第一版把假进程放在取快照之后 → 又一次假红，**实测才发现**（设计时不会暴露）。
3. **断言读对方的汇总，不要写死项数**：别人的套件加一个用例，不该让你的验收变红；
   但**项数退步**必须抓到 → 用「**≥ 下限**」而不是「**== 旧值**」。
4. **读数本身也会骗人**：`grep '^PASS'` 匹配不到**带两个前导空格**的输出行，
   于是「四套全绿」的汇总打印成「PASS 行数: 0」——**绿灯被报成零通过**。
   修的是**读数**，不是结论。
5. **红门先分类**：**代码坏了 / 前提旧了 / 读数坏了**——处置完全不同。
   不查清楚就改生产侧，是把已经正确的工具改错。

**通用一句**：**测试必须能在被测对象做完之后仍然跑**；
**写死的数字和借来的现场，都是会过期的夹具**。

### 60 「全绿」不等于「对」：门只问字段在不在，不问它说了什么

**情境**：战役收尾体检 31/31、四套验收套件全绿、链清单 CURRENT、git 锁 OK。
然后派一个**只读审计**子任务，把每个产物的**文字性陈述**与已核实的战役事实逐条比对——
翻出 **10 处不一致**（**我自己只找到 1 处**）。

**规则**：
1. **产物自述也要审**：产物里的假陈述**不会让任何门变红**——门只查「字段在不在、是不是空的」，
   不查「它说的是不是真的」。它只会安静地被人抄进论文。
2. **预注册命题不能站在结论位**：每个读数都必须带 `outcome`（MET / NOT_MET）+ `message`；
   **门必须查 outcome**。本例 H1/H4 有 outcome 而 H2/H3 没有 → 门一路放过 →
   「布局后档**是**有效的监督源」这句**预注册命题**就站在了 H2 的结论位上，
   而实测 placed AUC 0.843611 < 0.85（**未过门槛**）。
3. **同一个工具在两个 regime 下用，静态句子必错其一**：D1 时代「对照池没被重跑」是真的；
   OI-058 开全对照池之后它就是假的，而工具**别处会分支、这句不会**。
   → **每个 regime 都要有自己的句子**，不是只改头部注释。
4. **「列空」与「理由假」是两回事**：训练表的列真的是空的，但 limitation 给的理由是假的
   （「本族没有三点曲线产物」—— 产物其实早就存在，真因是**构建器只读基族曲线**）。
   → 改**理由**，不动**数字**。
5. **改名/删字段前先查消费者**——**要查全目录**：本例把报告顶层 `is_a_scientific_conclusion` 改名，
   我先查了覆盖检查器与两个草稿生成器，**漏查了子目录里的体检脚本** → 体检当场从 31/31 变 30/31；
   **是体检抓住的，不是我自查出来的**。改完还要给旧字段名留**回退**，让旧报告不因此判红。
6. **门红了，命令就必须红**：体检的退出码曾被 `after_campaign.sh` **打印了却不外传** →
   体检红着，收尾总检仍 exit 0 → **管道层的假绿**。现在判定一路传到总检的退出码。
7. **审计要独立**：作者查自己的产物会漏（作者知道它想说什么）；独立审计按「事实清单」逐条比对，
   才找得到「这句话与事实矛盾」——本例我自己只找到 1 处，独立审计找到 10 处。

**通用一句**：**验收门要问「产物说了什么对不对」，而不只是「产物在不在」**——
否则全绿的战役会把一句假陈述原样送进论文。

### 61 「就绪」要按「它检查了什么」来读

**情境**：C 路线的预检报告写「**就绪 8 / 缺 4**」，看上去只差 4 个源码包。
但它**只查了 6 个工具**（cmake / ninja / swig / g++ / bison / flex，全在 PATH），
**一个库都没查**。只读补查后：**Boost、spdlog、lemon、re2 的头文件都不在**（apt 候选都在，可装）。

**规则**：
1. **「就绪」是检查范围的函数，不是系统的属性**：先问「它查了什么」，再读它的结论。
   **检查范围之外的缺口不会自己报错**——它只会让你在几小时之后才发现。
2. **下载与构建之前，先把依赖查全**：头文件（`-e /usr/include/...`）比包名可靠；
   `apt-cache policy` 只能告诉你**装得上**，装不上/缺包本身就是答案（本次 CUDD 无 apt 包 →
   要么不带它构建，要么从源码侧解决）。
3. **代价用实测算，别用别处的平均值套**：本族 b04 一家就占 7.75 GB / 24.61 h，
   拿「平均每作业 31.4 MB」套上去会低估一个数量级。
4. **「没有观测到失败」不是「证明了不会失败」**：b05 的 167 个作业全 rc=0 是**观测**，
   不能写成「已证明没有上限」——这条纪律从 OI-057 起就一直管着它，现在也一样。

### 62 「结论在不在论文里」与「结论的前提在不在论文里」是两件事

**情境**：扩面族的读数做完后，我以为下一步是「把扩面族写进论文」。派一个只读审计把三份稿件
**逐句**对到读数上，才发现**论文自己的两条头条结论有口径问题**：
① ITC-99 表只报了**理想线网档**，而**同一批端点**（SHA 逐位核对）的布线后档位里 **4/13 落进判定带内**
（b04 由 +0.18 变 −0.01）；② §5.6 的物理后验是**单一实现点**，同族归档扫描显示
s420/s953 **符号翻转**、s832 变改善 → 「方向不保持」不稳健。

**规则**：
1. **别急着把新数据写进论文，先用它给论文当尺子**：一个族的价值往往**不在于它自己那组数字**，
   而在于**它能测出论文缺哪句口径**。本例扩面族的 2σ=0.049752 ns（跨族继承）**划出的可分辨区**，
   正好指出了论文那张表的增益里哪几例其实**不可分辨**。
2. **「结论在不在论文里」与「结论的前提在不在论文里」是两件事**：论文没写「图结构无信号」，
   就**不必**给它加族限定；但论文写了「平均改善 0.208 ns」，而那批端点的**另一档口径**有 4 例落在带内
   → **要加的是档位口径**。**加限定的对象要看「论文说了什么」，不是「我知道什么」。**
3. **单一实现点上的结论要标成「实现轴敏感」**：族内地板 0.000000 ns 已经划清了「哪些差属于实现轴」，
   **论文却用单一实现点下了跨实现的结论**——这正是「带」的用处。
4. **同批网表的不同口径读数不能互称「重测」**：SHA 逐位相同 ≠ 口径相同
   （扩面族用**冻结版图**、论文用**利用率派生 die**）→ 引用时必须写明是「另一族、另一口径的测量」。

**通用一句**：**新数据的第一用途是给旧结论量尺寸**；写进论文是第二用途。

### 63 门红先问一句「是不是有人在跟我抢」：同一个门两次结论相反，就是竞态

**情境**：cron 定时复查收尾体检，第 7 项「链演练」红了。同一分钟里，演练自己写的归档
（`post_ext_drill.json`）说 `passed:true, checks:68`，而体检抓到的 stdout 说 `DRILL FAILED: 3 check(s) failed`。
**同一个东西、同一分钟、两个相反的结论**——这本身就是竞态的指纹，不是一个待查的谜。

**规则**：
1. **门红时先看「这个门有没有共享的可变状态」**。本例：演练用**固定夹具根**
   `scratch/post_ext_drill/fixture_*`，且 `make_fixture()` 每次 `shutil.rmtree` 重建它；
   两个体检实例并发时，**后者把前者的夹具删了**，于是前者报出一串因果自相矛盾的失败：
   `rc=7`、**覆盖门根本没跑**（它的重定向目标目录被删了）、`JOB_TABLES.sha256 does NOT exist`、
   `recovered concurrency artefact -- n=0`。
   **一串互相打架的失败项，本身就是「有人在改我的文件」的证据**，而不是「产品坏了」。
2. **用证伪测试定性，而不是靠机制自洽**。我把同一份演练复制到**私有夹具根**跑
   （只改 `REPO`/`DRILL` 两个常量，其余逐字节相同）→ **68 PASS / 0 FAIL**。
   这一步是决定性的：**同一个二进制、同一套逻辑、只换夹具根就全绿** → 红门成因锁定在「共享可变状态」。
   机制说得通不等于结论成立，**必须跑一次能翻转结果的对照**。
3. **共享可变状态要治两层，别只治一层**：① 私有化（夹具根按实例唯一 `fixture_run_<pid>_<ts>`）；
   ② 加**互斥锁**（`fcntl.flock`）。只做①，两个实例仍会争抢**归档文件**，链清单会莫名变 STALE；
   只做②，串行化掩盖了「共享根」这个隐患。**锁文件必须放在不会被 rmtree 的目录之外**，
   否则锁自己被删掉，等于没锁。
4. **归档路径不要顺手「规范化」**：链清单按哈希钉住了 `post_ext_drill.log/.json`，
   把它们挪进私有目录就**废掉了清单**。**并发隔离的是「中间态」，不是「交付物」。**
5. **同类缺陷要往上再查一层**：修完夹具才发现，**体检脚本自己的临时文件**
   （`/tmp/drill_closeout.txt` 等）也是固定路径，两个实例会互截对方的日志，
   人按提示去打开的可能**是另一个实例的文件**。
   **同一类缺陷会在不同层重复出现**——修一层不算修完。
6. **回归测试要复现「红」的那个场景**：修复后的验收**不是**「单跑一次绿」，
   而是「**两个实例同时跑，两个都绿**」——那正是修复前必红的场景。单跑绿不能证明竞态被修掉。
7. **审计报的「陈旧文档」要按真实 git 状态复核再改**：独立审计报 `README` 说两个清单「在盘上、未入库」，
   实测二者**已在 index**（`git status` 为 `A`）；而仍被 ignore 的另两个文件对应的是 `.gitignore`
   **第 76–77 行**，README 原指第 70–72 行——**指错了行**。**文档里的行号也会过期**，
   更正时要以 `git check-ignore -v` 的实测输出为准。

**通用一句**：**门红先分清「它坏了」和「有人在跟它抢」**；**同一门两次结论相反 = 竞态**，
而**判定竞态要靠一次能翻转结果的对照**，不是靠推理。

8. **写下这条规矩的人当天就犯了两次**：写本轮的 LOG 行时，我把命令与锚点字符串**原样引进表格单元**
   （`ps -ef | grep ...`、`| OI-072 |`），**裸竖线把表格切成了 5 格 6 格**，行校验器当场报红；
   修第一次只替换了两个引用，**漏了四处**，第二次改成**整段重写**才干净。
   **「把规矩写下来」不等于「照着做」**——写记录的工具本身要过同一道校验器，
   **而且要真的按它的报告改，而不是改到“看起来对”为止**。

### 64 跨族的「结论相反」多半是**基线不可比**，不是被比较的东西变强了

**情境**：工作线 A 要回答「基族说图结构特征无信号、扩面族说图结构特征显著更好」
这个矛盾。翻转检验逐一排除了判据（带）、样本量（池数）、电路数（12 次抽样
0/12 同号）、标签难度（resolvable 与 harm 都相反），最后定位到：
**`kind_only` 这个基线本身就是「候选类型 × 物理标签」的交叉表，
而这张表在两族方向相反**——基族里 R（等效替换）正例率 0.5236、远高于 G 的 0.3022，
扩面族里 R 只有 0.3707、低于 G 的 0.3838。
于是扩面族的正差值（`structural` 比 `kind_only` 高 +0.103，CI 不含 0）
**来自「基线变弱」，不是「图特征变强」**。

**规则**：
1. **「A 在族 1 打败 B、在族 2 输给 B」时，先问 B 是不是同一样东西**。
   一个基线若依赖被比较对象的**构成**（候选类型分布、电路规模、动作可用性），
   它在两族之间就**不是同一个基线**，「谁打败谁」的结论也就不可跨族搬运。
2. **用能翻转结论的对照，而不是靠机制自洽**。本轮最关键的一次翻转尝试
   （把两族电路数对齐）**单次抽样翻了、多抽样 12/12 没翻**——
   **单次抽样翻转不是结论**，必须重复。本轮因此没有把「电路数」当成主因。
3. **口径先对账，再谈结论**。本轮前两版工具算不出 H1 的 +0.103117，
   原因是统计量用错（逐池 AUC 差 vs 配对池自助重采样差）与行集取错
   （合并训练表里的标签列是空的）。**算不出别人的数时，先怀疑自己的口径**，
   不要急着宣布「矛盾」。
4. **「救回」与「省下」不是一回事**（工作线 C）：把超时拒绝的候选改成
   「按其网表大小配更长时限」，实测 **STA 次数增加 773、多花 87003 s 墙钟**，
   救回的候选里真实收益未知。**更长的时限是花时间买质量，不是省测量**；
   **省测量只能靠剪枝/配额**。计划阶段就该把「总 STA 次数」与
   「首次改善的候选序号」分成两个指标，否则会把排序/时限的收益写成「省了 X% STA」。
5. **自变量要选对粒度**：`n_c`（锥内门数）在电路内几乎不变（b02/b09/b13 只有
   1 个不同取值），它是**电路级**的量，预测不了**候选级**耗时（R² 0.0977）；
   能预测的是**候选网表字节数**（R² 0.9632，且 STA 之前就已知）。
   **粒度错配的拟合，R² 会诚实地告诉你它不成立**——别改口径去救它。

**通用一句**：**跨族结论相反时，先查基线；基线依赖被比较对象的构成时，
"谁更强" 就不是可搬运的结论。**

### 65 「这个门能不能用」要问两个量：候选级的判别力，和它的样本量

**情境**：工作线 B 要做「候选级准入门」——按候选的线载敏感度分档，
在进入 STA 之前挡掉那些「理想线网有收益、布线后收益消失」的候选。
做了 6 个候选级代理，**全体口径的 AUC 看起来很好**（0.75 左右）；
但按电路分层后，层内 AUC **在电路之间乱跳**（1.000 与 0.100 并存），
而能算出层内 AUC 的电路只有 4 个、每电路样本量最小 3 个 → 判为不成立，方向终止。

**规则**：
1. **「全体 AUC 高」与「候选级判别力高」是两件事**。候选生成器要决定的是
   **同一个电路里**先测哪个候选，所以要的是**层内**的量；
   全体 AUC 可能整段由**电路间**的差异贡献。
   本轮那 6 个代理的全体 AUC（0.75）与层内 AUC（有的 0.43、有的 0.74）的落差，
   就是这个陷阱的量级。**先分层，再谈能不能用。**
2. **样本量先说话**。能算出层内读数的格子一共 4 个电路 × 每格 3–11 个样本；
   在这种格子上 AUC 0.9 与 0.1 都可能只是噪声。**「n=3 的 AUC 0.9」不是证据**。
   判据要写「每格至少 N 个样本」，不够就写「未验证」，不要写「有效」。
3. **终止也要有产物**：方向三终止时，**保留它挖出来的东西**——
   本轮最大的收获不是那个门能不能用，而是「理想线网有收益、布线后没兑现」
   这个**候选级**集合本身（扩面族主池 37 个 ideal 有收益的候选里，
   按论文口径的带判兑现只有 8 个）。它与论文那 8 例**端点对级**的物理后验
   **不可互相替代但方向一致**，是论文缺的另一半证据。
4. **兑现判据本身会改变结论**：同一个集合，用带（0.049752 ns）判兑现是 8/37，
   用「> 0」判是 19/37 → 落空率 78.4% vs 51.4%。
   **两个口径的数字必须同时给出**；只报一个会把一个依赖判据的量写成定论。
5. **先查「这个量是不是已经有了」**：方向三要「为每个候选各自生成寄生」，
   但扩面族的 T2 档**本来就是每个候选各自跑一次**物理流程（数据卡 §3）→
   **不需要新 EDA**；真正不可用的是**签核级 RCX（T4）**。
   **新实验的成本应该先从数据卡/产物里查，而不是凭印象估。**

**通用一句**：**门能不能用，看「层内判别力 × 每格样本量」；不能用就把挖出来的东西留下。**

### 66 物理流程有两种「跑完了」：空数据与无穷迭代，都不报错

**情境**：补齐 SKY130HD 物理档环境，目标是产 DEF/SPEF，让「布线后档」真的能算。
流程每一行都返回成功，却两次拿到假结果：
① yosys 映射时序设计时缺 `dfflibmap`，寄存器留成 `$_DFFE_PP_` 内部单元；
OpenSTA 读到不认识的单元就建**黑盒**，于是所有路径消失，`report_wns` 报
`wns max 0.00`、`worst slack max INF`——**没有任何一行是 Error**。
② 加回 DFF 后 `detailed_route` 停在「剩余 1 个违规」，`DRT-0195` 从第 1 次
一直刷到第 59 次，每轮都只剩 1 个违规，**它自己不会停**。

**规则**：
1. **工具说「完成」不算完成，要看它有没有数据**。判断标准是能不能打出
   `data arrival time` 与真实 slack；`wns 0.00` 配 `No paths found`
   是红灯，不是「时序很松」。凡是「全 0 / INF / 空表」的读数，先质疑
   分析对象建起来没有，再谈数值。
2. **版本谱系不能按 tag 名对号入座**。同一项目的两块资产是**各自演进**的：
   ORFS 的 `v2.0` tag 是 2021 年的，其 lib/LEF 与既有归档**逐字节全不同**；
   而既有归档那一版 commit 的脚本又依赖 OpenROAD 3.x 才有的 `utl::` API。
   结论：**锁 commit 取静态资产，流程用自己的命令驱动**，
   不要把「上游 tag 号 = 二进制版本号」当成同一件事。
3. **符号链接型依赖在 sparse checkout 下会静默断链**。
   `sky130hd/rcx_patterns.rules -> ../sky130hs/rcx_patterns.rules`，
   只检出 hd 时链接存在但目标缺失，表现是提取阶段「没有数据」而不是「文件不存在」。
   取平台资产时要把**链接目标的实体**一并检出或拷过来。
4. **迭代型优化器必须自己设硬上限**。DRT 用 `-droute_end_iter` 掐住；
   否则「差 1 个违规」会让它跑到天荒地老，而结果和跑 15 轮没区别。
5. **档位可当基线的前提是确定性**：同一输入两次跑，DEF/SPEF **字节相同**
   （本轮 109 471 B / 122 536 B 复现一致）才敢拿它做「理想档 vs 布线后档」的差。
   另外注意工具会往**当前目录**吐工作文件（`route.guide`），
   跑之前先切到输出目录，否则污染仓库根。

**通用一句**：**「跑完了」要拆成三问：断言了吗、有数据吗、可复现吗。**

### 67 物理档要能进论文，先过「口径三件套」：同网表、同 SDC、同库；差一个就换了个族

本轮差点留下一个错误读数，值得单独记一条。

**事故**：给 ISCAS89 跑布线后档时，我自己写了一份「看起来合理」的 SDC
（`create_clock -period 2.0`、20% I/O delay、0.1 pF 负载）。跑得很顺，
得到 s641 理想档 **−5.61** / 布线后档 **−6.41**，差 0.80 ns，看上去是个漂亮结论。
但主实验 `20260826_iscas89_main/s641/s641/sta.log` 里 s641 的理想档是 **−1.63**——
差了 3.98 ns。也就是说，那份「布线惩罚 0.80 ns」是**在另一个约束族里测的**，
既不能和论文数字并列，也不能和别的电路并列。

**根因**：SDC 是时序口径的一部分，不是「配置项」。
项目里同时存在**三种**写法，各管一段，混用就换族：

| 出处 | 约束 | 用途 |
|---|---|---|
| `code/src/rseco/sdc.py` | `clk_virtual` / period 10.0 / load 0.05 / 驱动 `buf_1` / `set_max_delay 0` | Stage B 预布局虚时钟分析 |
| `20260826_iscas89_main/<c>/<c>/sta.tcl` | `create_clock -name clk -period 0.5 [get_ports CK]`，**无** I/O delay、**无** load、**无** 驱动单元 | 论文主实验的真值口径 |
| 本轮初版脚本（已废） | 真时钟 period 2.0 + 20% I/O delay + load 0.1 | 无人需要，属于自造 |

**正确做法**：物理流程**不许自拟约束**。入口二选一并写进脚本参数：
`-n <既有 mapped.v>` 跳过综合、`--sdc <file>` 原样使用既有 SDC。
这样唯一的新增变量就是寄生参数，A/B 才是干净的。

**验收标准（机械可查）**：重新算出的**理想档**必须与主实验 `sta.log` 的
`worst slack max` **逐位相同**。本轮 7 例全部一致（s27 −0.27、s382 −0.98、
s420 −1.56、s641 −1.63、s820 −1.19、s832 −1.23、s953 −1.31）。
**理想档对不上，后面所有 Δ 都不用看了**——这是最便宜的守门。

**这一关过了之后才拿到的数**：布线后档 ΔWNS 全部为负，**−0.06 ~ −0.61 ns**
（中位 −0.23），相对恶化占理想档 WNS 绝对值的 **13.8% ~ 37.4%**。
这个量级和论文里讨论的候选改善（0.02–0.46 ns）、判定带（0.0498 ns）
是**同一量级**——这正是「理想线网的说谎程度」的一个硬锚点，
但它**只能作为上界参照**，不能写成「因此候选改善无效」。

**另外两条**：
1. `ΔTNS` 的均值不可单引：s641（8.37）+ s953（7.30）占 74.7%，
   又是「均值被少数电路拉动」的老坑，必须逐电路报。
2. **未评估 ≠ 零变化**。s713 布局布线全过、DEF 也写出了，但 OpenRCX
   在 `order_wires` 上反复失败且**不终止**（靠 `timeout` 兜住才停下来）。
   它必须记成「未评估」，绝不能在表里填 0 或跳过不提。

**通用一句**：**跑物理档之前先问「我这份约束是哪来的」；跑完先问「理想档对得上主实验吗」。**
### 68 布线后 STA 必须读「布线后网表」：名字对不上时 read_spef 静默不标注，Δ 恰好等于 0

这一轮把 17 例从 Windows 搬到 WSL 重做，连续踩了三个**不报错**的坑，
每一个都能安静地把读数变成假的。

**坑一：Δ 恰好为 0，不是「没有退化」，是 SPEF 根本没被采纳。**
第一版把 `mapped.v`（布局前）配 `read_spef`（布线后），跑出 s420/s641/s713
三例 ΔWNS = **0.0000**。看着像「同族一致」，实际是 `read_spef` 大量
`Warning 1650: net ... not found` / `instance ... not found` 之后**什么都不标注**。
根因：SPEF 里的网表含 CTS 缓冲（`clkbuf_0_CK` 等），布局前网表里根本没有这些单元。
**正确做法**：物理流程在 `detailed_route` 之后 `write_verilog <top>.routed.v`，
双档都读这份网表——ideal 不读 SPEF、post 读 SPEF，差异才只剩寄生。
改对之后 s641 由 −1.36 变 −1.76（Δ −0.40），s713 由 −1.49 变 −2.18（Δ −0.69）。
**机械判据：如果全表 Δ 都是 0.0000，先怀疑没标注，不要当成结论。**
（`run_physical_flow_sky130.sh` 已补这一步；漏写时脚本会从 DEF 复原 `routed.v`。）

**坑二：论文主实验的网表里，触发器是子模块黑盒。**
主实验 `mapped.v` 只做了 `synth -top`，没有 `flatten`：`dff` 作为子模块留在网表里
（s641 有 **19** 个 `dff` 实例），真正映射成 `dfxtp_1` 的只有 **1** 个。
也就是说触发器没有进入时序路径。这解释了为什么主实验的理想档对
`dff` 数量不敏感。本批改用 `synth -top <c> -flatten`，17 例触发器全部落到
`sky130_fd_sc_hd__dfxtp_*`（s820=5、s953=29 等，与其注释的触发器数一致）。
**代价**：两族的理想档数值不可并列，只能族内比较；这一点必须写进清单。

**坑三：`dff` 端口顺序按「想当然」补，会得到驱动冲突而不是报错。**
s820/s832/s953 原始 `.v` 只实例化 `dff` 却没给模型。补定义时我按
`(CK, D, Q)` 写，而 ISCAS89 原分发是 `(CK, Q, D)`（`dff DFF_0(CK,G38,G90)`
即 Q=G38）。结果 yosys 报 `multiple conflicting drivers`，`abc` 静默不出单元，
网表从 17.5 KB 缩到 4.3 KB、**0 个触发器**。补定义前必须先读原文的实例写法，
端口序照抄，不要凭 API 习惯。

**附**：`order_wires failed` 是 OpenRCX 的硬边界。DRT 留下真实重叠
（DEF 里 met1 两条线交于一点）时，RCX 反复重排且**不终止**。
试过 `-clock met4-met5`、`-signal met2-met5`、迭代 40、利用率 25/35，
四种组合全部复现；`-no_cc` 在 v2.0 不存在。处理方式只有
`timeout` + 明确记「未评估」，**不得**记 0 或跳过不提。

**这一轮最终拿到的数**（16/17 成对，全部在 WSL 内、单一映射族）：
ΔWNS **−0.06 ~ −0.73 ns**，中位 −0.32、均值 −0.3675；
恶化占理想档 WNS 绝对值 **14.1% ~ 47.1%**，中位 27.3%。
比上一批（−0.06 ~ −0.61，13.8%~37.4%）整体更重，差别主要来自
触发器真正进入时序后路径更长。两个数不能混着引用。

### 69 换基准族之前，先查两件事：有没有时钟端口，dff 的定义在不在文件里

ITC'99 官方分发的门级形态是 BLIF，`.latch out in init` 只有三个字段——**没有时钟**。
BLIF 语义里它是电平敏感锁存器，yosys 读成 `$ff`，`techmap` 之后落成
"使能端接常量 1 的透明锁存器"：寄存器不进时序，路径整条消失，**且不报错**。
这与 ISCAS'89 那次 `$_DFF_` 黑盒（只报 `wns 0.00`）是同一类沉默失败。

出路不是硬转 BLIF，而是换个入口：ITC'99 另带官方 Verilog 版
（`data/raw/benchmarks/raw/itc99/v/<c>.v`，文件头写着 `Generated by Yosys 0.9`），
已经是门级网表，自带 `module dff(input CK, D, output Q)` 和顶层 `CK` 端口，
结构与 ISCAS'89 那批同构，可以直接进 `synth -flatten`。

但它的 dff 端口序是 **(CK, D, Q)**，而 ISCAS'89 那批是 **(CK, Q, D)** ——
**同一个名字，意思相反**。两边各自"定义与实例化在同一文件内"所以都自洽；
一旦把一边的定义搬到另一边，就是 `multiple conflicting drivers`、
网表从 17 KB 缩到 4 KB 那种事故。

所以动手前固定做三件事：

1. `grep -m1 '^module ' <file>` —— 顶层有没有时钟端口；
2. `grep -m1 'module dff' <file>` —— dff 的定义在不在文件里；
3. 在的话，看端口序是否与实例化的位置连接一致（`dff X (CK, D, Q)` 对应
   `module dff(input CK, D, output Q)`，不能想当然）。

只有"定义缺失"时才需要补模型，补的时候端口序必须照原分发的实例化顺序来。

**附**：新族落地的两个硬边界，都按 `timeout` + 记「未评估」处理，不记 0：
一是 b12（629 cells / 121 dff）在 util=35/20/5 三档下 `detailed_route`
均抛 `DRT-0073` 后 core dump，`Blockages` 恒 24107、`yosys check` 无告警，
判为 OpenROAD v2.0 的 DRT 边界；二是 `synth` 的 opt 会把不可观测寄存器删掉
（b13 的 53 个 `$dff` → 43 个 `$_SDFF_*` + 7 个 `$_SDFFE_*`），
所以"映射后 dfxtp 数少于源 dff"是正常现象，但**必须报出来**，
并注明未做形式等价验证。
### 70 换 EDA 版本不是重编译：26Q3 换栈的三类暗坑 + 一条保旧纪律

从 OpenROAD v2.0（2021）升到 26Q3，真正花时间的不是编译，而是下面四件事。

**坑一：同一份网表，新前端把常量建成 POWER 网。**
映射网表里有 `assign X = 1'h1;` 时，26Q3 的 Verilog 前端建出的网名叫
`one_`、类型是 POWER，DRT 直接拒绝：`DRT-0305 Net one_ of signal type
POWER is not routable by TritonRoute`。v2.0 不检查这个，会把无驱动的常量
当普通信号布掉——所以这不是"新版本变差了"，是旧版本一直没报。
修法 `hilomap` 换库内 tie cell（`sky130_fd_sc_hd__conb_1`，liberty/LEF 都有），
但**必须先验证改动对无常量电路是零改动**：拿最小例（s27）跑一遍，
输出与原 `mapped.v` 逐字节比，相同才可以批量套。b13 改 17 处、b11 改 1 处。

**坑二：DRT-0073 多半不是工具边界，是自己漏了流程步骤。**
b12 在 v2.0 下 util=35/20/5 三档全崩、`Blockages` 恒 24107，当时判成
"v2.0 的 DRT 边界"。换到 26Q3 仍然崩，且 11 cell 的 s27 也崩——最小例
能复现的故障，一定不是规模问题。查 26Q3 自带的 `gcd_sky130hd` 流程才发现
它比旧流程多两步：CTS 后 `repair_clock_nets` + `detailed_placement`
（合法化时钟缓冲），布线前 `pin_access`。缺这两步，CTS 缓冲落在非站点位置，
TritonRoute 找不到接入点。补上后 b12 util=35 一次过。
**教训：报"工具边界"之前，先找同版本官方 flow 脚本逐条比步骤。**

**坑三：依赖链是硬耦合的，不是"装新版就好"。**
`utl::format_as` / `odb::Rect` 的格式化在 `FMT_VERSION < 100000` 时退化，
apt 的 fmt 9.1 + spdlog 1.12 组合会让 1573/2810 个格式化点编译失败。
往上试 spdlog 1.15.0 + fmt 11/12 又撞 `basic_format_string` 被删；
spdlog 1.15.0 默认 C++11 还要显式改 C++17。**最终解是 fmt 12.1.0 +
spdlog 1.15.3**（`SPDLOG_FMT_EXTERNAL=ON`，在 tweakme.h 里写死），
旧版整体移到 `quarantine_fmt_spdlog/` 而不是卸载。
另外两处：yaml-cpp 0.8 只导出 `yaml-cpp::yaml-cpp`，裸名只加 `-lyaml-cpp`
不带 include（`src/odb/src/3dblox/CMakeLists.txt:24` 一行补丁）；
LEMON 1.3.1 在 C++20 下 `std::allocator::construct` 已被 P0619 删除，
用 OpenROAD 自带 `allocator-patch.patch` 但**只取 `array_map.h` 那部分**
（path.h 的 6 个 hunk 打不上，硬来会破）。
还有 boost_iostreams 的传递依赖：链接缺 `-llzma -lzstd` 要先装 dev 包。

**坑四（旧族污染）：新版布线结果比映射网表多触发器。**
旧族 s641 的 `routed.v` 有 19 个 `dfxtp` 而 `mapped.v` 只有 17，
意味着那条记录里的"理想档 −1.36 / 布线后 −1.76"**不是同一个电路**。
26Q3 全族 17 例逐例相等（差异恒 0）。所以每次跑完必须做一次机械核对：
`grep -c dfxtp mapped.v` 与 `grep -c dfxtp <c>.routed.v` 逐例相等。
不等就说明记录不可用，不能"看起来合理"就留着。

**保旧纪律**：换栈时新步骤一律做成**默认关闭的开关**
（`OR_BIN` / `POSTCTS_LEGALIZE` / `PIN_ACCESS`），旧族结果才能逐位复现；
新族开开关另跑一目录，两族不拼表。
"换栈即换数字"——同网表只换工具也要重跑，不能拿旧 Δ 加新工具名。

### 71 物理实验的三道门：DRC、布局阶段、噪声底

这一条来自"ECO 四数对照"整批返工。三个错误都出在流程层，不是算法层，但任何一个都会让数字作废。

**门一：DRC 必须是硬门槛，不是参考信息。**
第一版 16 次运行里 12 次带 DRC 违规（li1 Metal Spacing 98~153 条），而此前四个物理族
38 个 `drc.rpt` 全是 0 违规——**因为没人去数**。带违规的布线不是"略有偏差"，
是另一个电路：`RCX-0114 Net ... does not start from an iterm or a bterm` 会让 SPEF 的
`*CONN` 段为空，`read_spef` 直接报 `Error 1670 syntax error`，STA 读不出数。
更糟的是当时汇总脚本把空值当 0 参与相减，`d_post` 虚高成 1.80（真值 0.46）。
**做法**：每次布线后 `grep -c "violation type" drc.rpt`，非 0 就标 invalid，
汇总层拒绝参与均值。缺读数、坏读数一律不进算术。

**门二：布局种子的阶段决定成败——必须取 CTS 之前。**
第一版拿 base 的**布线后** DEF 当布局来源。那份 DEF 已经包含 CTS 插入的时钟缓冲及其位置；
两臂从"已被缓冲占据"的布局重跑 CTS 时，新缓冲无处落脚，第二次 `detailed_placement`
大幅挪动单元，DRT 随后不收敛。**报错在下游，病根在上游**。
正确做法是单独跑一个只到 `detailed_placement` 的种子阶段，两臂共用：
`initialize_floorplan → make_tracks → place_pins → global_placement → detailed_placement`。
判据很干净：base 侧从自己的种子位置出发，合法化位移必须**恒为 0**；不为 0 就是流程有问题。

**门三：布局与布线本身不是逐位可复现的，噪声底要自己标。**
同一网表、同一条命令序列跑两遍，`global_placement`/`detailed_placement` 之间
**4~15% 的单元位置不同**（最大位移 5.44 µm、3~13 个朝向变化）。但 base 的 WNS 只差
0~0.03 ns（中位 0.01）。所以布局随机性对 WNS 的影响是 0.01~0.03 ns 量级。
**这条直接解释了上一族"保持率跨 0.20~3.50"**：不是布局噪声大，是分母 C−A 只有
0.02~0.09，0.03 ns 的噪声足以让比值翻倍。**比值型指标在分母接近噪声带时没有意义，
必须逐例判断分母是否大于噪声底，不能只报比值。**

**顺带一条正面经验：`replace_cell` 是 ECO 物理档最干净的模型。**
CO 臂只换 drive strength（实例名 100% 相同、连接关系 0 差异、1~5 个 master 不同），
于是可以直接 `read_def base 的 CTS 后 DEF` → `replace_cell` → 重新合法化与布线。
布局与时钟树与 base 逐位相同，`d_post` 里只剩换门、寄生、布线三项。
比"重新读网表再跑一遍 CTS"（会打散 72.7% 单元）紧得多。
但这条路径**必须先校验连接零差异**，有结构改动就不能用。

### 72 别用「规模」解释退化幅度：先回读关键路径的最差单级

ITC'99 补到六例后，恶化占比跨 22.8%~125.6%，而 ISCAS'89 十七例只在
14.1%~47.1%。最省事的解释是「ITC'99 更大所以退化更重」——这个解释是错的，
回读关键路径就能推翻。

三例大电路的最差单级，全都是**最小驱动门带几十个负载**：

| 电路 | 最差单级 | fanout | 输出 slew | 单级延迟 |
|---|---|---|---|---|
| b14 | `nand2_1` | 71 | 2.138 ns | 2.032 ns |
| b20 | `o311ai_0` | 29 | 11.070 ns | 8.295 ns |
| b15 | `nor4b_1` | 29 | 9.231 ns | 6.960 ns |

而 ISCAS 最差两例（s838、s953）路径上最大扇出只有 7 和 17，单级延迟
不超过 0.66 ns。**差别不在电路规模，在映射后有没有做扇出修复。**
`synth -flatten` 不含 `repair_design` 那类步骤，最紧的门被直接挂上
29~71 个负载，布线一放大线长与电容， slew 就雪崩到 9~11 ns，
下游整条路径被一起拖垮。b14 全设计有 **794 个 pin 的 slew > 2.0 ns**，
说明这是普遍现象而不是个别路径的偶然。

**教训**：看到幅度差异，先问「是不是流程里没做的那一步在放大」，
再问「是不是对象本身的属性」。归因错了，跨族比较整体作废——
「ITC'99 退化更严重」这句话如果写进论文，审稿人只要要一张关键路径
的表就崩了。

**顺带一条**：不要为了让表"好看"去补流程。补 `repair_design` 会改写
基线网表，理想档读数全变，等于开新族；本族内混做就是把两种网表混进一张表。

### 73 参数预选等于放弃族内惯例，代价是不一致却解释不清

族内惯例是「util 从 35 起逐档降，取首个成功档」。因为 b17 在 35 下
DRT 不收敛，我在跑 b20 时**预选**了 util 25，跳过了 35 这一档。
结果表里六例有五个 35、一个 25，成了一个必须写进报告才能解释的不一致。

后来补跑 35：**一次通过，1617 s**。也就是说预选完全没有必要，
只是为了"应该会崩"的猜测，换来一条要额外解释的参数差异。

**纪律**：除非有**该例**的实测失败记录，一律从族内默认档起跑。
「上一例崩了」不是预选下一例参数的理由——不同电路的拥挤程度不同，
b17 有 104 pin 的网，b20 没有。

### 74 两次运行差 0.23 ns，不是「敏感性」

b20 util 25 与 util 35 的 ΔWNS 是 −6.97 与 −6.74（差 0.23 ns），
布线后档 −20.29 与 −20.06。这个差看起来很"稳定"，但它是 **n=1 对 n=1**。
用它去说「ΔWNS 对密度不敏感」是拿两次抽样冒充趋势。

**做法**：把变体单独存目录 + 写 NOTE 说明「不进表、不参与统计」，
并写明为什么不能当敏感性分析。留着是为了将来替换用，不是为了引用。

### 75 效果量必须是「同档位、改前比改后」，不是同一网表的前后差

物理档曾经这样报：`ΔWNS = 布线后 WNS − 理想档 WNS`，两者取自**同一份网表**。
这个量只说明「布线寄生把 WNS 拉低多少」——一份**完全不改**的网表，这个差同样成立，
所以它无法回答「改完之后还剩多少收益」。

**正确形式是四数**：A=基线预布局、B=基线布线后、C=改后预布局、D=改后布线后；
预布局档改善 `C−A`，布线后档改善 `D−B`，保持率 `(D−B)/(C−A)`。
`D−C`（同一网表布线前后）**不入表、不作效果口径**。

**判据**：任何"效果"数字，先问一句「如果把改动撤掉，这个数字会不会变」。
不会变，它就不是效果量。

### 76 大例三臂串行跑不完：B 直接取「之前那次」的布线，只补改后臂

ISCAS 八例每臂十几分钟，三臂一天能跑完；ITC'99 的 b15（4007 cells）
一次 `detailed_route` 就要 73~90 分钟，三臂串行 4.5 小时/例，两例就把一天吃光。

**做法**：`base` 臂只跑到 CTS（拿 `cts.def` 给 `ecofix` 当起点），
**B 直接取原族「之前那次不修改的实际布线」**（同网表、同 util、同流程，
只是不同一次布局，差在噪声底 ≤0.03 ns）。这样每例只需补**改后臂**一次布线。
脚本里用 `BASE_STOP_AT=cts` 截断 base，读阶段缺产物时自动回退到原族，
并在 `readings.tsv` 的 `post_src` 列标明来源（`out` / `legacy_orig`）。

**前提**：C−A 与布局无关（理想档），所以 A、C 仍精确可比；只有 B 换了来源，
必须在报告里写清，不能默不作声。

### 77 换门后 legalize 位移会带出 DRC，先看是否时钟网

b15 换 3 个门、位移仅 8 个单元（0.2%），却出现 2 条 `met1 Short`，
网名是数据网 `_50533_` / `_52787_`，不是时钟网。这类违规与 s953 的
`clknet_0_CK` 不同：时钟网短接是"迭代次数不够"，数据网短接更适合先看
是否换门后局部过于拥挤。

**纪律**：DRC≠0 一律先记 invalid 并归档到 `_failed_*` 目录，
再决定重跑参数；不得把"差 2 条违规"的读数当结果用。

### 78 改一个口径，要连带改三样东西：推论句、跨文件硬编码编号、其它文件里的「禁替代」

把 §4.5 的物理后验从「两例退化」扩成「固定布局 8/8 为正」时，真正耗时的不是写新段，
而是三处**不在改动范围内、却已经和新证据矛盾**的地方：

1. **下游推论句**。§5 有一句「物理估计后的收益损失表明预搜索应与实现检验结合」。
   新证据说收益并没收损，这句就从「结论」变成了「错误前提」。只改 §4.5 会留下自相矛盾的全文。
2. **跨文件硬编码编号**。补充材料里有两处写死「主文表6」。主稿新插一个表之后，
   原线载表顺延成表 7，这两处指向就错了。`\ref` 不会报错，编译器也不会提醒——
   因为写死的是中文数字，不是 label。
3. **证据清单里的禁令**。「禁替代论文现行两例后验」这条是上一轮为了让论文冻结而写的；
   本轮用户解冻后，正确的动作是「新增 + 改解释，不替换原数字」，禁令要改写成新的用法说明，
   否则下一轮接手的人会照着旧禁令把新内容删掉。

**纪律**：口径变化的影响面 = 正文段落 + 全篇推论句 + 其它文件对该表的编号引用 + 证据清单禁令。
四项都要过一遍，再宣称"改完了"。

**另一半**：主稿只放**守得住的量**。本轮 C−A 与主实验有 3 例 0.01~0.02 ns 未查清，
且 C−A 均值 0.1613 与主文 0.16125 数值相同**只是三例偏差 +0.02/−0.01/−0.01 相互抵消**，
不是一致性证据（数值相同 ≠ 逐例相同）。所以主稿只写 D−B（8/8、均值 0.2462），
C−A 连同这处口径差一起放进补充材料并写明"尚未查清"。
能被审稿人一击打穿的量，留在主稿就是负债；放到补充里标注清楚才是资产。

### 79 相对改善比例：小基数会把 0.13 ns 放大成 33%，必须与绝对量同列

用户要求"加一个比例，相较于之前的提升多少"。比例本身不难算，难的是**它会在最不该
显眼的地方最显眼**：s27 只改善 `+0.13 ns`，基线才 `0.39 ns`，比例就是 **33.3%**；
s641 改善 `+0.89 ns`（绝对量是它 6.8 倍），比例 **36.2%**。两个数几乎相同，
放在一起读，读者会以为两例效果相当。

**这不是算错，是分母变了。** 处理办法不是把比例删掉，而是：

1. **逐例比例与绝对改善同表同列并排**，不把比例单独做成一个"效果指标"。
2. 正文点明放大的机理与具体例（"s27 的 +0.13 ns 因基线仅 0.39 ns 而被放大到 33.3%"），
   让读者自己看到失真发生在哪里。
3. **另给一个总量比** `Σ改善 / Σ基线违例`，它对基数不敏感：ISCAS 8 例 1.97/12.83 = **15.4%**，
   而逐例均值 15.9%、中位 13.1% —— 三个数在同一量级，说明总体结论不靠单例撑。
   只看逐例均值时，s27 这类小基数例贡献了 1/8 的权重，很容易把结论带偏。

**分母是什么必须写死。** 本文口径是"基线 WNS 绝对值"，不是理想档 WNS，也不是总路径延迟，
更不能读成"距收敛还差多少"。同一个比值换分母能从 15% 变成 50%，不写分母的比例等于没定义。

**跨族别合并。** ITC-99 六例算出 19.6% / 15.1%，与 ISCAS 的 15.9% / 15.4% 量级相近，
但两族电路规模差 20 倍、修改构造不同（关键路径升档 vs 方法输出）、b15/b20 基线还取自
旧布线。量级相近只能写"相近"，不能写成"两族一致印证"，更不能并表求均值。
## 2026-10-30 臂名写错不会报错，只会在审稿时炸掉

固定布局后验（`20261029_eco_phys_samelayout`）从写进论文到被审稿人抓出，中间隔了两轮修订。
错的不是数字，是**数字属于哪个臂**：正文按 `eco` 臂（两侧各跑时钟树）描述方法，
表里的数却取自 `ecofix` 臂（只换门、不重跑 CTS）；同时把网表对写成「受控 W1」，
实际是**策略枚举纯 G 臂**。

为什么两轮都没发现：

1. **数字全对**。逐格核对脚本只比"表里的数 = readings.tsv 的数"，`readings.tsv` 的
   `arm` 列写得很清楚，但没人把正文那句方法描述也送去核对。
2. **合计恰好相等**。纯 G 与 W1 的理想档合计都是 1.29 ns（三例 ±0.01–0.02 相互抵消），
   均值同为 0.16125。合计相等让人以为"就是同一批"。**合计相等不是逐例相等**；
   逐例比一遍就能看到 s382 0.15 vs 0.17、s641 0.46 vs 0.45、s953 0.10 vs 0.09。
3. **补充材料先写了一句"口径差尚未查清"**，把可查的事写成了悬案。查法其实一行：
   `md5sum 20261029_eco_phys_contrast/s27/eco/raw.v 20260826_ablation_pureG/s27/mapped_hybrid.v`
   ——逐字节相同。悬案当场结案，且结论是"族差，不是测量误差"。

落地的检查项（以后带物理后验的段落照做）：

- 表头/表注必须写**臂名**，不只写"基线/修改后"；臂名与 `readings.tsv` 的 `arm` 列同名。
- 正文的方法描述与表的 `arm` 必须同源：`ecofix` 就写"不重跑时钟树"，别写"两侧各自独立完成布局与布线"。
- **合计相等要当红旗**：看到"均值/合计一样"，立刻逐例比一遍，差异往往正好在带内、被噪声底掩盖。
- 写"未查清"之前先花五分钟做一次 md5/逐例比对；查得清的事写进论文比留白更安全。

**压页要按行数算，不按字数感觉。** 主稿加一段 + 一张表后 10 → 11 页，末页是 12 条文献。
真实账是：11 页的溢出量 = 末页文字行数（两栏各 ~14 行），一行 26 个汉字，
所以需要腾出 ~28 个栏行 ≈ 700 字，或等高的浮动体。按这个账逐轮"改—编译—数末页行数"，
写了五轮才回到 10 页；凭感觉改两轮只会白改。同理，**表里恒为 0 或恒不变的列就是可压的信号**：
表 5 的独立缓冲列 8/8 恒 0、单元数列 8/8 不变，只剩面积列有效，整表并进正文一行就够。

## 2026-10-30 r99 冷读暴露的两个反模式

1. **把「可由其他列还原」当删列理由**。r98 压页时删掉表 5 的「修改后 D」列，理由写的是「该值可由基线 + 改善还原」。这是作者视角：作者知道怎么算，读者不会去算。读者读物理后验只想知道「布线后到底是多少」，两列倒推属于额外劳动，且看不出四数结构。**规则**：压页优先删重复表述与限定堆叠，不删读者用于判断的关键端点；若确需删列，须在表注给出被删列的数值或明确指向补充表。

2. **同一统计量跨表沿用结论**。§5.1 判「5 例超带」，§5.5 另一批读数沿用「5 例超带」，但 s820 在理想档 0.02 < 带 0.0717（带内），在四数组 0.08 > 0.0717（带外，余量 0.008 < 噪声 0.03）。**规则**：凡出现「N 例超带/超阈值」，必须对**该表自身那一列**逐例重算并核对，不得从相邻实验沿用；同一电路在两族里可以一侧带内、一侧带外，这本身是需要写出来的信息。

## 2026-10-31 r100 扩面的两个反模式

1. **扩面不能直接复用「手边有的网表」**。ITC-99 b01--b10 的首版输入取自早前准备的 `_src/`，
   那是 Windows 侧 Yosys 0.67 映射、`dff` 以子模块残留的网表（b03 30 个 `dff` 实例、全文件仅 1 个 `dfxtp`），
   与既有 6 例的 0.70+255 flatten 族**不是同一映射族**，读数不可并表。
   诊断信号有三条，任一命中就该停：① 文件头 Yosys 版本与族内其他例不同；
   ② `grep -c '^  dff '` 不为 0（触发器还在子模块里）；③ 物理流程 `place_from_seed` 报 `skipped=N`
   （N 恰为触发器数）。**规则**：扩面第一步是验映射族（版本 + 层级 + dfxtp 数），不是直接跑流程；
   发现不匹配就整份隔离（本例 `_stale67/`）重映射，不要「先跑完再说」。

2. **常量网络不是「无害的语法糖」**。映射网表里的 `assign X = 1'h1;` 会被 OpenROAD 建成
   `one_`(POWER)/`zero_`(GROUND) 特殊网络，TritonRoute 直接拒布（`DRT-0305 ... not routable`），
   且**只在含常量赋值的例上出现**（b05/b07/b09，其余 7 例无事），很容易被当成偶发失败重跑。
   修法有顺序陷阱：`setSigType SIGNAL` 必须放在 `read_def` **之后**——DEF 里写着 `+ USE POWER`，
   在读 DEF 前改会被覆盖，表现为「改了没用」。**规则**：物理流程失败先看 DRT 错误码与网络名，
   别把「少数例失败」当噪声；修完要在报告里写明改了类型、没改网表与约束。

## 2026-10-31 噪声底与判定带都不是总误差预算

`s641/b13 × util 30/35/40` 的布局敏感性实验给出一个反例式的提醒：s641 的 D−B 在三档布局下是
+0.86/+0.89/+0.84，**极差 0.05 ns，约为其逐电路判定带（0.0246 ns）的两倍**。
也就是说，我们长期引用的两个"不确定性"量——同网表重跑的 0.03 ns 噪声底、逐电路配对网表的判定带——
**都只覆盖了网表级抽样，没有一个覆盖布局实现抽样**。它们不是总误差预算的一部分，而是其中一块。

**规则**：任何"超过 X 就算确认"的判据，先问 X 的抽样空间覆盖了什么。本例中：
大效应例（0.86，为带 34 倍）不受影响；边际例（s820 +0.08 vs 带 0.0717）必须继续记"未确认"，
且理由要从"余量小于噪声"升级为"余量小于布局离散"。**判据的作用域要写在判据旁边，不能只写在心里。**


## 2026-10-31 不报 Overfull 不等于可读

补充表 S16 有 9 个数值列，塞在单栏 `table` 里时：`tabcolsep 3pt` 与 `2pt` 都报 Overfull，
压到 `1.5pt` 后**编译干净、质量门 PASS**，但渲出来看相邻列已经贴连（`+0.45` 紧挨 `-1.18`，
肉眼读成 `-1.18+0.45`）。改成 `table*` 跨栏 + `\small` + `tabcolsep 5pt` 后列间距正常，页数不变。

**规则**：① 列数 ≥ 8 的表优先考虑跨栏，不要靠压 `tabcolsep` 硬塞；② 质量门只查 Overfull/Underfull，
        查不出"挤在一起但没越界"，所以**新表落版后要看一眼渲染图**（`pdftoppm -png` 再读图），
        这是机械终检的盲区，与"未引用的 label"同类。

## 2026-11-02 反事实要先问「能不能精确算」，改算法前先问「损失是否真实存在」

决策层离线反事实（`experiments/20261102_offline_decision/`）里，同一张表混着两种性质完全不同的数：
**预算截断**（把候选 STA 上限压到 k）是**精确**的——它只砍掉前缀之后的评测，前缀逐位不变；
**决策替换**（把某组选中的候选换成另一个）只能是**一阶估计**——换完后后续实例的评测条件全变，
归档没有重放那条分支。若不把两者分列声明，读者会把 `Σregret 0.34 ns` 当成实测损失。

同一轮还有一个更值得记的教训：伪代码写「首个满足 Accept 即提交并 break」，
两个运行器实现都是「该候选集全测完后取 WNS 最优者提交」。23/23 个提交组的提交者都是组内最优，
说明**没有损失可捞**——上一轮曾把「argmax→top-k」列为补强项，实际是个不存在的缺陷。
反过来，按伪代码字面执行会让 8 例合计增益从 1.29 掉到 0.95 ns（保留 73.6%），
所以**该改的是文字，不是算法**（已登记 OI-075）。

**规则**：① 任何「如果当时不这么做」的反事实，先判定它是「前缀不变」（可精确算）还是「路径改变」（只能估）；
② 改算法之前先用归档反事实证明损失真实存在；若实现已在上限（如 argmax），先怀疑是描述写错了而不是方法不够好；
③ 描述性偏差与数字错误要分开声明——本轮的终点数字一个都没动。

## 2026-11-02 伪代码里的一行 break，改的是语义，动的是版面

论文 `alg:search` 原来写“首个满足 Accept 即提交并 `break`”，两个运行器都不是这么做的（`23/23` 提交组的提交者
都是组内 WNS 最优者）。改法本身简单，但有三件事值得记。

**一、改语义前先把两族的“分组粒度”读清楚。** 纯 G 族（`run_hybrid_repair.py`）按**实例**分组：一个实例的候选
全测完后递进取最优，提交后立即改 `text`，所以**一轮可以提交多次**（s641 首轮 4 次、次轮 1 次）。
受控 9 臂族（`real_wns.py`）的 `jobs` 是**整轮**候选集，`if best is not None` 每轮只提交一个。
若只写“取最优者提交”而不交代粒度，等于用一个族的形状描述了两个族。

**二、页数溢出与增加的字数可以完全不成比例。** 首版伪代码净加 3 行、正文只多 518 B，结果算法浮动体位移，
把参考文献 [11]--[17] **整块**顶到第 11 页。用字节数判断“是不是字太多”在这里是错的——
先看浮动体落在哪、页底有没有被拉出空隙；压到比原稿**少**一行即回 10 页。

**三、`write_text` 在 Windows 上会静默改写全文行尾。** `OPEN_ISSUES.md` 原为纯 LF，Python 文本模式写入后
整份变成 CRLF（1153 行）。凡对“行尾有约定”的文件做整文件写，必须 `write_bytes` + 显式 `\n`，
写完立刻数一遍 `CRLF==LF`。

## 2026-11-02 总量稳不等于分级稳：把“超过判定带”放到布局维度上测

r101 只用 2 例就写下“判定带只含网表级离散”的限定，这一轮把它扩到 8 例、每例三档利用率（48 次物理流程）。
结果分成两层，而两层结论相反：

**总量稳**：8 例合计 1.80 / 1.97 / 1.85 ns（u30/u35/u40），均值 0.2250 / 0.2462 / 0.2643，波动 ±8%；
D−B 的**符号 8/8 三档同号**；`C−A` 跨档极差 0.0000 ns。看总量，结论完全站得住。

**分级不稳**：u35 下 6/8 例超过判定带，但三档**一致**超带的只有 4/8——s820 与 s953 随布局翻转，
其中 s953 的 D−B 在 0.02 与 0.19 之间摆动（其带的 3.8 倍、自身近 10 倍）。

**教训**：① “某例超过判定带”是“该电路 + 该次布局”的联合属性，写成该电路的属性就错了；
② 均值/合计这类合成量会把分例的摆动抵消掉，**合成量稳不能替分例判读做担保**，报结果要把两层分开写；
③ 扩面时先钉守门（本例 u35 逐位复现原族 8/8），否则三档差异分不清是布局还是流程抖动；
④ 请求的 `-utilization` 不等于实际利用率——小设计被站点量化成 35.0/37.8/49.4，s27 在“40 档”直接排版失败，
这类例只能记未评估，不能当零变化。

## 2026-11-02 三个抓手全部试完：加动作、换枚举、改判据，都越不过判定带

B 路线（硬做方法论文）的三条技术抓手今天全部跑完，结论一致：**单点改进都落在判定带以内**。

**抓手一 · pin swap（新动作，零面积）**：liberty 里同层引脚的 arc 差最大 0.094 ns（nor4，9.4 个量子），
四例实测中位只有 **0.0388 ns**，全部低于各自判定带（最大 0.96 倍），24 次尝试回滚 10 次（42%）。
**我自己的静态度量高估了 3–5 倍**（估 s420 0.211、实测 0.0405）——liberty 最小 slew/load 格的比值只能筛机会，不能当预期。

**抓手二 · JOINT 滑窗枚举**：候选从 1 个/区域扩到几十个，**8 例里 7 例终点逐位相同**，只有 s713 从 0.05 到 0.22（4.4 倍）。
机制不是 JOINT 自己贡献增益，而是它**改变了关键路径走向**，让后续 G 落到原本走不到的门上。
命中率 1.24%（161/2），预注册门槛 7.5% 未过。

**抓手三 · 判据加带**：r102 已证会毁累积（8/8 → 4/8）；三级漏斗又证它在候选级精准（假阳性 0）。
两者不矛盾：加带提高单次提交质量，但减少提交次数。

**教训**：
① 当项目已经写下“动作粒度 < 测量分辨率”这个第一性原因时，任何“再加一个动作”的方案都要先算
   “单点效应量 ÷ 判定带”，算出来小于 1 就不必跑；pin swap 是 0.5–1.5，注定不过。
② **组合动作的价值可能不在自身增益，而在改变搜索轨迹**。只看“该动作类的命中率”会低估它——
   但反过来，只有 1/8 例需要重定向，也说明它不是普遍手段。
③ 实现与论文语义不一致会被实验放大成“机制无效”。JOINT 滑窗枚举里“R 优先”这一行代码，
   足以让 7/8 例的组合候选全部劣于基准；**下结论前先核代码与论文描述是否同一件事**（OI-076）。
④ 预算不公平必须当场处理：J2 多用 1.49× STA，所以要同时报终预算与同预算两个读数，
   否则 +13.2% 会被误读成方法增益（实际扣除单例后为 0）。

## 2026-11-02 追差距要追到“对手改了哪几个门”，不要停在统计量上

外部基线出来（OpenROAD 2.3286 对 FAECO 1.2900，1.81 倍）之后，我先做了两件“看起来对”的事，
都被数据否掉了。最后真正有用的动作是把对手的修复网表**逐实例比对**了一遍。

**第一个假线索**：算出“覆盖率 vs 外部差距”的秩相关 ρ=−0.714（n=8），覆盖最低的 s820（9.1%）差距 9.65 倍。
于是做扩覆盖实验（`max_instances` 8 → 不限）。结果 7/8 例增益**逐位相同**，同预算下 8 例合计增量精确为 0.0000 ns。
观测相关在因果链上完全失效——因为“覆盖高的例正好容易改”与“覆盖低导致差距”在观测数据上长得一样。

**第二个假线索**：以为 OpenROAD 改了几百个门。实际它只改了 14 个（138 个里的 10.1%）：10 个 resize + 4 个 buffer。
**改动数量根本不是差距来源，改动的“类别”才是**——那 14 个里有 5 个是 `dfxtp_1 → dfxtp_4`。

**真正的发现**：我们的动作集从来没有触发器。W1 的 s820 共 107 次候选尝试，`dfxtp` 出现 0 次；
`critical_instances` 的 99 项全是组合门。根因是一个正则：`(\w+)/\w+` 匹配不到含点号的 `DFF_1._0_`。
补上后 4/8 例超过判定带（1.41–2.31 倍），是全项目唯一的多例超带正结果。

**四条规则**：
① 有外部基线时，**先导出对手的输出逐实例 diff**，再谈归因。统计相关（覆盖率、相关性系数）只能提出假设，
   不能定因果；一个受控实验的成本通常低于基于相关做的错误推断。
② **“改动数量”与“改动类别”要分开看**。对手 14 处改动胜过我们 2 处，不是因为 14 > 2，
   而是因为它改的那 14 处里有我们根本不会生成的动作。
③ **组合动作不能用单点贪心估上限**。DFF 全升 +0.3615，逐点贪心只有 +0.2158（1.67 倍），超带例数 4 对 1。
   原因是单升一个触发器会抬高它的 CK 电容、加重时钟负担，抵消收益；同步升才显现。
   凡动作之间有共同副作用，“可加性”假设就会系统性低估。
④ **解析层的静默排除最危险**。正则匹配不到就直接丢弃，不报错、不告警，整类动作消失两年都没人发现。
   写解析器时要用“总数对账”：解析出的实例数 + 跳过数 必须等于网表实例数。
   本轮的第一条证据就是“2200+ 次尝试里 dfxtp 出现 0 次”——这个数字本该更早被看见。

## r113：想让动作落进证明域，改候选而不是改检查器

- 现象：触发器升档被 `_scoped_module_pair` 拒（`Non-target helper module changed`）。直觉是"放宽检查器"，但那是
  让证明域静默缩水——顶层等价证明把 helper 当共同定义，改了 helper 就等于假设失效而声明不变。
- 正解：把改动**搬进**被证明覆盖的模块。`dff` 实例就地展开成同族库单元后，helper 字节不变，
  同一检查器直接通过；检查器只需多识别这一类**精确改写**（解释不了仍 fail-closed）。
- 判据：先问"这个改动落在谁的证明域里"，再决定改代码还是改检查。
- 另一条口径错误：统计同库面积时，`parse_mapped_netlist` 不认 `dff` 这类 helper 实例，
  初始面积会系统性少算（本例少算 5×20 µm²，把 +2.45% 误算成 +15.8%）。凡"初始 vs 最终"对比，
  两侧必须用同一口径覆盖全部单元，包括藏在子模块里的。

## 2026-11-04 环境收敛：可删性看「包含关系 + 引用面」，不看名字与时间

- 两个同名可执行文件、两个发行版并存**不等于冗余**。先分清两种角色：**默认入口**（PATH 里排第一的那个）
  与 **pinned 证据路径**（被写进证据链绝对路径的那个）。
- 卸载前先问「删掉之后默认会落到哪里」。本例 `/usr/bin/yosys`（0.33）是 SEC 链 pin
  （见 `LOGS.md` LOG-20261018-91），而 Yosys 0.70+255 根本不在 PATH ⇒ 删 0.33 只会让 `yosys`
  变成 command not found，**不会**自动切到新版。真正该修的是**默认解析目标**，不是二进制数量。
- **软链对「自定位型 launcher」无效**（本轮实测踩到并回退）：OSS CAD Suite 的 `bin/yosys` 是
  shim 脚本，用 `dirname "${BASH_SOURCE[0]}"` 推出自己的 topdir，再 exec
  `<topdir>/lib/ld-linux-x86-64.so.2`。从 `/usr/local/bin/yosys` 软链过去时 `BASH_SOURCE`
  变成软链路径，于是它去找 `/usr/local/lib/ld-linux-x86-64.so.2`
  → `No such file or directory`（报在第 9 行，连 `-V` 都过不去）。
  **正解是转发 shim**：`exec /real/path/bin/yosys "$@"`；判断依据是 launcher 是否用
  `BASH_SOURCE`/`$0` 推导自身路径。凡「文件名对、版本对、一跑就 ENOENT」先怀疑这一点。
- **先查这个工具在各批次里的角色，再决定改不改**。映射版本是**按时段/批次**划分的，不是按测试集：
  `0.67+146` 覆盖基族（`20261024_physical_labels*`）与近期主线（`20261102_gate2`、`20261104_w1_remap067`）；
  `0.70+255` 覆盖 `20261029_*` 与 `20261030_*` 那几批（ITC-99 四数族 + 扩面族，**含 ISCAS 扩面
  `20261030_eco_ext_iscas`**）；`0.33` 是 SEC 证明器。所以「ISCAS 用 0.67、ITC-99 用 0.70」这种按
  测试集的划分**是错的**，只能按批次目录 + 读 `mapped.v` 头部 `Generated by Yosys ...` 判。
- 判可删性用两张表：① 内容集合是否**严格超集**（`sta`、`sby`、`z3`、`/opt/faeco_toolchain` 逐项比对，
  保留侧更多且含 `openroad`）；② 引用面是**代码还是文档**（代码零依赖、只有文档提旧名 ⇒ 可删）。
- **顺序陷阱**：先 `--set-default` 再 `--unregister`。默认发行版恰是待删那个时，删完裸 `wsl` 直接失配。
- 用户选择不备份时，把**依据**写进日志（哪几项核过、结论是零独有数据），不要只写「已删」。

## r115：换映射器 ≠ 提升质量（关于「统一到最新 Yosys」）

- 现象：仓库同时有 0.67 与 0.70 两个映射族，直觉是"统一到新的更干净"。
- 实测：0.70 网表（点号直接实例）喂进受控运行器后 **0 候选、0 次 STA**，坏在割/补丁构造而不是解析；
  要统一等于先修代码、再重跑 72 次主矩阵、再改触发器动作实现、再全文改数。
- 判据：**换工具版本是"重做"，不是"升级"**——只要它改变输入网表，既有数字全部失效。
  版本新旧本身不是质量指标，可复现性与口径一致才是。
- 做法：两族分工写进口径（0.67 = 论文主族；0.70 = ITC-99 与物理后验），并在补充材料明写"不跨族比较"。

## r116：全量测试 6 红，先分层再归因（环境 / 编码 / 误读）

- 现象：`pytest code/tests` 报 `6 failed, 1050 passed`，摘要像"代码回归"。
- 分层结果（2026-11-04 实测）：
  1. **5 例是环境**：`yosys -V` 无输出，PowerShell 里 `$LASTEXITCODE = -1073741511`（`0xC0000139`
     `STATUS_ENTRYPOINT_NOT_FOUND`）。原因是 PATH 中 `/ucrt64/bin` 的 DLL 抢在
     `C:\oss-cad-suite-build\oss-cad-suite\lib` 之前。把 OSS-CAD 的 `bin` + `lib` 提前后，同一批用例 **24 passed**。
     `docs/environment.md` §5.2 本就写明"`bin` 与 `lib` 同时入 PATH，否则 `yosys -V` 无输出"——**文档对、环境漂了**。
  2. **1 例是真实编码缺陷**：`test_fix_crcrlf.py::test_real_repository_is_clean` **不是**"工作区洁净"断言，
     而是扫被跟踪文本里的 `
`（测试体第 69–71 行 `scan_and_fix(REPO_ROOT, apply=False)`）。
     命中 `paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/actual_correction_v1/zh_applied_table.tex` 21 处。
     **LOG-20261104-05 把它读成"dirty 必然红、提交后转绿"，与代码不符**——以代码为准。
  3. 修法：`python code/scripts/fix_crcrlf.py --apply`（仓库自带），行数 21→21、内容不变，测试转绿。
- 判据：**红门先问"是代码、环境，还是断言读法"**；测试名不能替代测试体，日志里的归因也要回读代码复核。

## r117：机制修改方向 A 证伪——扇出线载模型结构上无法表达缓冲收益

- 现象：想用“打开已内置的 `--physical-gate --enable-buffer`”来解锁 B 类缓冲（方向 A），s382 实测 110 个 B 候选全部被物理档拒绝（physical_delta ≤ 0）。
- 分层归因（2026-11-09 实测）：
  1. **不是环境**：两臂端到端跑通，B 类确实生成并评估了 110 次（arm2 共 185 候选：G 42 / B 110 / R 33）。
  2. **不是 B 类“没用”，是线载模型结构缺陷**：`spef.py:estimate_net_rc` 线长 = `unit_len_um * max(1, sqrt(fanout)) * fanout_penalty * depth_penalty`。
     每条网有 `max(1,·)≥1` 的 40µm 底线；拆网（插缓冲）后总长 `40 + 40*sqrt(N−1) > 40*sqrt(N)`（N≥2 恒成立）。
     即模型把“线长”当 fanout 计数的单调函数，而不是“布局固定的物理距离”，于是缓冲永远“加线 + 加门”。
  3. **真实布局下缓冲收益来自“隔离驱动的大电容负载 + 线长不因拆网而变长”**，该模型两条都不表达。
- 判据：**“已内置但默认关”的能力不等于“打开就有用”**——先跑最小证伪，再看它是真实现还是启发式占位。
  一个线载模型若把 wire length 写成 fanout 的单调函数且每网带底线，它对“拆网”类动作（缓冲/复制）在数学上就是负面的，任何参数都救不回来。
  真正能表达缓冲收益的，必须让寄生来自布局（如 OpenSTA `estimate_parasitics -global_routing` 或 OpenROAD OpenRCX）。
- 记录：LOG-20261109-01；smoke 产物在 `scratch/smoke_physical_gate/`（git-ignored）。

## r118：布局感知判定带——3 点极差只能做敏感性检查，不能当方差

- 现象：判定带 b 是「网表级」带（r30 配对同网表离散），r103 用 8 例 × 3 util 测出布局实现极差 R 0.01–0.17 ns（中位 0.04），2 例 R>b（s641 2.0×、s953 3.8×），导致「超带」分级随布局翻转（s820、s953）。
- 处理：布局感知带取 max(b, R) 做敏感性检查（只改 s641、s953 两例的带）；但 **3 点极差不是方差**，不能当新的带定义——R 是有偏且噪声大的 3 点 range，与 b 的 2σ 口径本就不等价。
- 教训：判定带要写清「覆盖哪层离散」（网表级 vs 布局实现级）。换 floorplan 不改 D−B 符号（8/8 同号），但改分级（三档全超 4/8 < u35 单档 6/8）。「某例超带」是「该电路+该次布局」的属性。
- 记录：LOG-20261109-02；数据 `experiments/20261102_layout_stability_n8/`。

## r119：候选级代理更好 ≠ 决策级策略更好（方向 C 预证伪）

- 现象：想用「布局后档替换理想线网做判据/排序」（方向 C），但 r30 已测过（LOG-20261025-34）：布局后档是显著更好的池内排序器（ITC-99 Spearman 0.644 vs 0.399，p=0.0215），决策级 H1 却两族都未触发。
- 分层：D3b 尺子有分辨率、D6 奖池存在、D7 排序器确实更好——但分歧处的布线后差全在 ±1–2 个量子（0.01 ns）里，argmax 读不到。
- 教训：**候选级代理更好 ≠ 决策级策略更好；池内整体排序变好 ≠ 顶端选择变好**。缺的不是「换哪一档监督」，是「决策级有分辨力的判据」+「足够大的决策级奖池」。与「动作粒度 < 测量分辨率」（CANON §7.4）同源。
- 记录：LOG-20261109-03。
## r120：判据"档位"决定动作是否可达；门槛必须用该档位自己的分辨率（2026-11-10）

**结论一（机制级，可写）**：接受判据的**档位**决定了动作空间里哪些类动作**可达**。同一套搜索、同一批候选，理想档 4 例 11 个接受里 B 类 0 个（W1 全 8 例 0/606），布局档 2 例各接受 1 个 B。原因是结构性的：理想档下插 buffer 只增加一级门延迟，而它省下的线载延迟在理想网表里不存在。这条把"判据偏置"假设从推断变成正面证据。

**结论二（成本级，可写）**：判据的**门槛**必须用**该档位自己的分辨率**，不能沿用另一个档位的量子。理想档量子 0.01 ns，而布局档的判决噪声是**布局之间的离散**（r103 单臂跨布局极差中位 0.055 ns）。臂 P 沿用 0.010 后，8 个接受里 4 个低于 0.055（份额 0.50）；把 gate 抬到 0.050 后：接受数 4（原 8）、候选评估 **602**（原 878；理想档 1157），布线后端点数**不降**（均值 0.3095 对 0.3124，差 0.003 ns，远小于噪声）。⇒ **换 gate 门槛是零成本的质量中性、成本 -48% 的操作**。

**结论三（证伪，必须记住）**：换接受档位**没有**通过预注册的转移门。臂 P 布线后更好仅 2/4 例、均值差 +0.0334 ns < 0.05。三个布局档设置（0.010/0.030/0.050）互相不可分辨，全部比理想档高约 0.03 ns——**这个量级就是布局离散本身**，不是效应。⇒ 不得写"布局判据更好"，只能写"布局判据改变了可达动作集，其质量收益未获证据"。

**结论四（方法教训，两条）**：
1. **端点必须独立测量，不能拿 runner 汇报的 `wns` 横比**：gate 模式下 runner 的 `wns/gain` 是**物理档**读数，与理想档不可比（本轮臂 P 的 `registered_wns` 普遍比臂 I 差 0.2–0.3 ns，但布线后反而略好）。跨臂比较只能用同一流程独立测的端点。
2. **读 JSON 的上下文方向要对**：`ops_grep` 的 `afterContext` 读到的是**下一个** trial 的字段（因为 `accepted`/`committed` 在对象尾部），据此读"被接受的候选是什么 kind"会**系统性读错**——必须用 `beforeContext`，或直接脚本按 `accepted` 过滤后打印同一对象的字段。本轮据此一度误判"P 臂在 s641/s832 接受了 B"，复查后才纠正。

**结论五（"验证式接受"的真实量级）**：补丁链逐网表布线后发现，被接受的 9 步里 7 步布线后为正、2 步为负（−0.0326 两次，同一补丁）；布线后最优前缀相对最终态最多只多 0.033 ns（s953 臂 P）与 0.003 ns（臂 I）。⇒ 在"单步效应 0.01–0.12 ns、布局离散 0.055 ns"的尺度上，**逐补丁做布线后确认不值得**；要让决策效应高于噪声，正确方向是**加大动作粒度（每轮批量接受）**，不是换来更贵的判据。

**边界**：4 例 ISCAS89 子集、非签核 RC、gate 首轮混档、DRC 未入判据。详见 `experiments/20261110_placed_gate/REPORT.md`。
**结论六（实现纪律，本轮踩到）**：把「基线/候选各测一次」抽成 `RealWnsEvaluator._physical_measure()` 时，
函数签名保住了、**顺序性不变量没保住**——① 原代码在每次 `run_opensta_sequential` 前都调 `_deadline_or_budget_event`
预留 STA 预算，抽象后只在其中一个后端分支里预留；② SPEF 路径迁移后父目录不存在，写入抛错被 fail-closed 成 `error`。
12 个**新增**用例全绿，红的是 13 个**既有**物理档用例。⇒ **抽函数后必须跑全量回归**，新用例通过不构成「没坏」的证据；
并且「新增后端不改旧后端行为」要用**同配置重跑 + 逐项比对**证明（本轮：终态网表 sha16、216 条 trial 的状态/种类直方图、
两个接受的 delta 全部逐项相同）。
## r121：判决器不是瓶颈——把「判决噪声」压下去也换不来端点收益

**结论**：把接受判据的**判决噪声**从「单布局」降到「三布局均值」（理论 1/√3），
判决确实被改写（接近门槛的候选 **46.8%** 换布局就翻判），但**端点收益没有随之兑现**
（arm E 优于 arm P 仅 2/4 例，均值差 +0.0112 ns < 预注册的 0.05 ns）。
⇒ 「接受判据不够准」不是这套机制的主要瓶颈；**要动的是单次动作的效应量或测量分辨率**。

**怎么做才算证据**：
1. 先承认上一轮 H2 FAIL 的正确读法是「未分辨」——同一网表换布局端点摆动实测
   12 格均值 **0.1042 ns**（范围 0.0011–0.2328），而待判效应只有 +0.0334 ns。
2. 再把「判决精度」做成受控变量（k=3 布局均值判决），其余一切不动，**运行前预注册**
   H1（分歧率 > 15%）/H2（端点 ≥3/4 且 ≥0.05 ns）/H3（成本 ≤1.6×）。
3. 结果分开报：H1 PASS 说明「判决噪声是真的」；H2 FAIL 说明「修判决不等于修收益」。
   两条同时成立才是完整结论——**只报 H1 会把「判决不准」错当成本瓶颈**。

**坑**：
- 新增测量字段必须同时加进 **trial 组装字典**（`real_wns.py` 的 `result = {...}`），
  否则 `eval_trials.json` 里读不到（本次 `physical_wns_per_util` 首次就是这样丢的）。
- 分析脚本读 `wns_per_util` 要取 `["wns"]`，它是 `{wns,tns,min_slack,error}` 字典不是标量。
- 同一实验里若两臂终态网表逐字节相同（s382 E==I），端点读数会完全相同——这不是巧合，
  要核对网表哈希后再解释差异，别把「同网表」当成「同策略所以同结果」。

## r122：动作粒度不是杠杆，「贪心单步不选大动作」+ B 类才是被低估的动作（2026-11-12）

**做了什么**：把机制已有的联合动作宽度 `--joint-k` 从 2 抬到 6（一次决策改 6 个门），
预注册 H1（动作确实变大）/ H2（端点转移）/ H3（成本 ≤2×），主检验臂 A6j 与 arm E 只差 joint-k。

**结果**：H1 1/8 FAIL、H2 −0.0023 ns FAIL、H3 1.15× PASS ⇒ 不晋级。
s641/s832 的终态网表与 E **逐字节相同**——放大宽度后机制选到同样的补丁。

**三个可复用的教训**：

1. **"把动作做大"要先问"机制会不会选它"**。JOINT 每轮只构造 1 个候选（取 actionable[:k] 各改一档），
   贪心又按单步增益取最大 ⇒ 大动作在多数轮次被单门动作压掉（s641 单门 +0.609 vs 6 门 +0.4767）。
   度量"动作是否变大"要用**被接受补丁的改动门数**，不是候选里有没有大动作。
2. **改动门数不能用 diff 行数替代**：`difflib` 行数会把 JOINT 双计（每门删+加=2 行）、
   把插一个缓冲算成 3 行（wire/端口/实例）。按实例计改动门数才与"动作宽度"语义一致；
   本轮的 H1 在行数口径下 3/8 PASS、门数口径 1/8 FAIL——**口径选择直接决定门的结论**，
   所以两个口径都要报，且预注册里要写清单位。
3. **补丁链（逐补丁布线后增量）比端点总数更能发现问题**：s382/s953 两个最大增量
   （+0.1001 / +0.1253）都来自 **B 类插缓冲**——正是理想线网判据从不接受、真实布局档判据
   才开始接受的那一类。端点总数看不出"哪类动作值钱"，逐补丁链可以。

**边界**：4 例 ISCAS89、三布局均值端点残余误差 ~0.06 ns/例；只动一个旋钮；JOINT 空间几乎未搜索。

**下一步（需另立预注册）**：A. 把 B 类插缓冲做成主搜索方向（现在 B 只是 R/G/B 一支且被排序压后）；
B. 改选择结构（多联合候选 / 先接受后组合）。若都不过，机制侧只剩测量分辨率一条。

## r123：按种类校准的失败点在「常数」不在「排序」（2026-11-13）

1. **先把机制改成「只改同轮比较、不改接受门」再谈效果**。`postroute_calibration` 的设计要点是接受门仍用**原始** `physical_delta >= 0.010`，校准只影响「已过门候选之间的排序」。这样即使结论是负的，也不会有「放宽门槛」的嫌疑；同时默认空表时与历史规则逐位等价，可用归档读数做回归对照。
2. **只接受少数几次「否定」不能定常数**。本轮 k_B=5.64 来自 4 个补丁步（2 个电路各 2 步），基线里 B 的布线后/布局档比值是 5.91 与 5.44，看似一致，但换成 held-out 后方向立刻不稳：s641 +0.0351、s832 ±0.0000、in-sample s953 **−0.0976**（util 0.35 的布线后读数甚至比 base 更差）。⇒ 判据常数必须按电路/按输出负载分层，且样本要 ≥5–10 个逐补丁配对，否则拟合的是抽样噪声。
3. **接受新动作种类会改变搜索路径与成本**。arm K 因为接受 B 打开了新锥，s641/s382/s953 三例都在 4 轮吃满 500 STA 预算（约 72 候选/轮），总候选评估 1005 对 arm E 的 738（1.36×）。**端点打平 + 成本上升 = 性价比为负**，这类读数必须和端点一起报。
4. **「候选被压掉」和「候选不存在」要分开查**。s832 的 H1 失败不是排序没生效，而是 20 轮里只有第 1 轮有合格候选且无 B 过关（轨迹问题）；若只看「K 没接受 B」就会误判成机制 bug。
5. **负结果要写清「证到哪一步」**：本轮证到「按种类校准能把 B 送进接受集」，但**没有**证到「B 类被系统性低估」——后者需要更多逐补丁布线后配对；也不能反推「B 类无价值」。
## r124：改判据不动端点，先量「判据还有多少自由度」

- 四轮判据侧实验（理想档 / 单布局档 / 三布局档 / 按种类校准）端点均值落在 0.2727–0.3095 ns，
  极差 0.0368 ns，比实测布局离散 0.1042 ns 还小 ⇒ 不是某个判据"略差"，而是**判据这一层改不动**。
- 离线量一次自由度（不跑 STA）：**top-3 同实例只 15%（3/20 轮）**说明池里有多个实例可挑；
  但**跨臂 top-1 同实例 4/7、同种类 6/7** 说明不同判据几乎选同一个实例 ⇒ 真正的决定权在
  **候选生成与排序**，不在最后一个接受判据。
- 逐补丁配对 Spearman 只有 0.164（n=10）⇒ 布局档对"单步布线后增量"的排序能力很弱；
  这也解释了为什么"判据看起来更对"（E 的 H1 判决噪声 46.8% 确实被修掉了）却没有端点收益。
- 教训：**改判据前先做离线回放并量自由度**（本轮成本 0 分钟 STA，替代了一轮 ~2 h 实验）；
  若 top-1 跨判据高度一致，就不该再开判据侧实验，应转向候选生成/动作集。
- 教训：比较不同臂的端点必须统一到**同一布局集合的均值**，否则布局离散（0.10 ns）会伪装成判据差异。

## r124：批接受实验——即使接受所有物理门合格的候选也换不来额外端点收益（2026-11-14）

**结论**：`--accept-all` 把每轮所有 `paired_improved` 候选全部累积接受后，4 例均值增益差 **-0.2574 ns**（比 arm E 单步贪心更差），动作空间触顶（当前 R/G/B + joint_k=2 的动作集布线上限 ≈ 0.31 ns/4 例均值）。

**教训**：
1. 判据侧换档位、校准种类、放大动作宽度、全部接受——六轮实验都证伪。问题不在"怎么选"或"接受多少"，在当前动作种类本身的物理天花板。
2. s641/s953 的 `stagnation` 回退（63/14 个候选被接受后理想 WNS 反而不如 单步贪心）说明"累积叠加"不是"贪心"的上界——`accept_all` 可能用 更激进的动作集合把理想 WNS 做差，使后续候选过不了 epsilon 门槛。
3. `_accept_result` 闭包用 nonlocal 累积迭代最优状态，在隔离回放时必须 先 reset 才能独立判决——这是"只读一次就写复杂闭包的逻辑"的经典缺陷。
4. s382/s832 的微弱改善（+0.008/+0.009 ns）只有布局离散的 1/10，不可分辨；即使是真的，投入产出比也太差。
5. 完整证据链（P/E → K → A6j → All）支持 CANON §7.4 的原始诊断：「动作粒度 < 测量分辨率」。

**代码落点**：同 LOG-20261114-01。
**实验入口**：`experiments/20261114_accept_all/`，REPORT sha256@16=cd631f84a8a490c9。

## r124：方向转折——从预布局机制优化转布局后 SOTA ECO（2026-11-11）

**背景**：六轮预注册实验（P/E/A6j/K/All/LLM回放）全部封口，任一刻度的机制改动都不带来端点收益。根因是“动作粒度 < 测量分辨率”（CANON §7.4），在预布局设定下已触天花板。

**关键发现（s382 iter1 4例签核测量）**：同迭代同基线口径下 placed→signoff Spearman 0.80–0.85（而非此前跨迭代口径的 0.164）。贪心 max placed_delta 选中的候选在签核上 +0.0852 ns，真正最优的候选 +0.1188 ns（贪心错失 40%）。转向前的“判据秩相关很弱”诊断是跨迭代累积补丁链的误算口径。

**教训**：
1. “跨迭代累积补丁链”和“同迭代同基线”是两个完全不同的口径，前者混了行为器的选择误差。
2. “六轮封口”不等于“这个方向死了”——它只证明预布局设定下天花板已触，换设定后有新空间。
3. 文献调研要做到最新（2026）才能确定竞争格局——仅看 2023–2024 会低估当前 SOTA。
4. 用户的“要实证不要论述”是正确的——P1 实验结果比任何分析都有说服力。


## r125：输给成熟工具时，先量"动作量"再谈判据，并改问可组合性（2026-11-11，P1）

1. **先量被比较对象在做什么，再解释差异。** P1 一开始我把差距往判据/判决上猜；实际把两条臂的布线后 DEF
   一数，resizer 在 4 个电路上分别净增 8/9/13/38 个逻辑单元，而 FAECO-P 净增 0/0/0/1 —— 差距首先在**动作量**，
   不在"谁更会挑"。以后任何"我们的选择质量不如 X"的说法，先给出 X 与我们的**改动门数/单元数**对照。
2. **两段读数必须分开报，否则会把结论读反。** FAECO-P 对 base 是 8/8 为正（均值 +0.2473 ns），
   resizer 对 base 是 +0.5836 ns ⇒ 结论是"我们有效但幅度只有它的 42%"，不是"我们无效"。
3. **比较协议要各自用各自的定义流程，但 STA 约定必须完全一致。** resizer 的扁平化 `routed.v` 塞回标准流程会
   稳定 segfault（139，两次复现）⇒ 改成"每条臂跑它自己的流程、读数用同一套 ideal-clock + extracted-SPEF STA"，
   并在报告里显式声明流程不对称。硬凑同一流程会得到不可复现的数。
4. **缓存必须带输入指纹。** 端点缓存按 (arm, circuit, util) 键控，第一次跑时 s382 的三条 FAECO-P 读数命中了
   accept-all 时代的旧缓存（网表已换但 key 没变，差值 0.02–0.06 ns）。修法：实验网表的缓存写入 netlist sha256
   并在命中时校验；跨实验复用 base 读数时必须确认输入网表逐字节相同。
5. **负结果要直接给下一问。** P1 的 FAIL 把问题从"能不能赢 resizer"改成"我们的 ECO 能不能让 resizer 更好"
   （同一流程、只换起始网表的 Hybrid 臂），后者是公平 A/B，也是唯一可能产生增量贡献的问法。

## r126：赢了胜场、输了幅度 —— 事后追加臂必须两条件同时判（2026-11-11，Hybrid）

1. **胜场数（sign test）与效应量（均值差）必须同时过门。** Hybrid 在 8 例里 5 例优于 resizer，
   看起来"过半"，但均值差只有 +0.0243 ns（门槛 +0.05）—— 因为赢的三例赢得少（+0.0012/+0.0142/+0.0243），
   输的三例输得多（−0.0623/−0.0215/−0.0125）。只看胜场会把"正负相抵"读成"更好"。
2. **事后追加的实验臂要在报告里明确标 post-hoc。** Hybrid 是 P1 判定后才提出的问法；判据虽在读数前写定，
   但选题本身是看了 P1 结果才有的，属事后假设，不能与预注册臂的结论等价。
3. **"组合我们的 ECO + 成熟工具"不等于有贡献。** 组合臂比 resizer 多跑了一次我们的搜索 ⇒ 成本更高、
   收益不显著；这类结果若包装成"增益"会被审稿人直接点破。要么证明同预算下更好，要么承认无贡献。
4. **负结果要给出下一步的可检验形式。** 本轮把"可组合性"也否掉后，路线只剩"把 resizer 当内层优化器、
   我们做预算调度"这类**调度**问题——这是可以把工作量和收益都量化的问法，而不是模糊的"做得更好"。

## r127：工具产物的「形状」是接口契约——扁平网表、同名不同字节、以及为什么对照臂必须同字节

1. **解析器只认一种写法，就会把别家的产物读成空。** OpenROAD `write_verilog` 把第一个命名连接写在实例头
   同一行（`sky130_fd_sc_hd__dfxtp_1 DFF_14  (.D(UC_17VD),`），旧解析器只在行尾是 `(` 时才开始缓冲多行实例
   ⇒ 每个实例都是碎片 ⇒ 门数 0 ⇒ 下游 `logic_levels()` 抛 `KeyError`。**症状离病根很远**：报错是某个网络名找不到，
   而根因是"整份网表没解析出任何门"。诊断靠一个笨办法：把中间产物抄一份、用同一个函数数一下 gates 是不是 0。
2. **"逻辑等价"不等于"布线等价"。** 把 `\DFF_14/_0_` 改名为 `DFF_14` 后单元多重集、网络集合、FF 名 1:1 映射
   全同（已单独验证），但字节不同 ⇒ 重新 floorplan/place 后读数差 0.0027 ns，恰好与被判效应同阶。
   所以**对照臂必须用与机制输入同字节的网表**：否则测的是"改名带来的布局抖动"而不是"我们补丁的效果"。
   这类错误不会报错，只会让结论方向随机。
3. **中间产物要在读数之前就固定成"同字节"契约。** 本轮的顺序是：先测了原始导出（对照）与 RF（归一化输入）→
   发现不同源 → 作废、清缓存、改 `netlist_for()` 指向 flat 版 → 重测 18 条。**代价是 40 分钟**；
   如果一开始就把"对照臂 = 机制输入"写进预注册，这 40 分钟不需要花。
4. **逐补丁链比总端点更能立住结论。** 总差 +0.1202 可以来自一个幸运补丁；拆成逐步后 5 个补丁**全部为正**
   且单调累积，才排除"单个补丁抽中好布局"的解释。只要每步一次布线（本例 ~2 min），成本可接受。
5. **跨工具组合要先问"谁的终点"，再问"谁的动作空间"。** resizer 的终点不是全局最优——它不做等价改写、
   不按覆盖率排序；我们的 2–3 个单实例动作在它的终点上仍有 +0.12 ns。这不是"我们更好"，而是"动作空间互补"，
   两种说法的证据要求完全不同（后者只需要配对改进 + 逐补丁正增量，前者需要同预算下的整体对比）。
6. **pilot 的门槛要按样本量写。** 3 例 pilot 用「≥2/3 为正 且 均值 ≥0.05」是合理的筛选门，
   但过门只能写"有残余空间、值得扩样"，**不能**写"方法更优"。扩样必须另立预注册（现在的 `PREREGISTRATION.md`
   没有 8 例的分层与判据）。

## r128：布局档判断在 post-CTS 终点上不是可迁移代理（2026-11-11）

**背景**：P1′ 二轮把 resizer 段换成 post-CTS 变体，预注册 H2 判「我方 ECO 是否在真正 resizer 终点上还有余量」。
结果 3/3 变差（均值 −0.395 ns），而布局档判断认为四个接受动作都是 +0.06~+0.61 ns 的改善。

**教训**

1. **同一条判断链在不同终点上的可迁移性可以相差整个符号**。pre-CTS 变体终点上 5/5 补丁布线后为正（+0.03~+0.05），
   post-CTS 终点上 3/3 为负。不要把「在某终点上验过」当成「判断器可用」——终点网表的**寄生结构**（有无时钟树、
   驱动负载分布）改变了判断器看到的主要矛盾。
2. **先量档位绝对水平，再谈增量**。同一份 post-CTS 网表：placed 判 −2.10、布线后 −1.11，差约 1 ns。
   当两档绝对水平差远超被判效应量时，增量符号不可信，必须先做一次同网表的两档对照（`_probe_postcts_judge.py` 那种）。
3. **排除替代解释要用 probe 而不是推理**。「新增时钟树是不是造成了布局档高估？」——直接跑 with-CTS / skip-CTS 两遍，
   得到 +0.6369 / +0.6187，两遍几乎相同 ⇒ 与 CTS 无关，结论才能写。
4. **工具产物的形状是接口契约（再次）**：post-CTS 网表塞回会自建 CTS 的流程 = 双重建树 = 稳定 segfault 139。
   先做三变体探针（原样/跳 CTS/跳 CTS+去 assign）把原因钉死，再改代码（`render_flow_tcl_skip_clock_tree`），
   并且默认路径必须逐字不变 + 加回归测试。
5. **负结果也要能给下一问**：本轮把「继续这条线必须先解决判断器与端点一致性」写成唯一前提，
   而不是笼统说「没余量」。同时明确区分「本机制的动作空间没余量」与「终点没余量」。


## r129：逐 reversion 诊断揭示 Resizer 69% 浪费；FAECO 面积效率 4.4x（2026-11-12）

**教训**：
1. **逐 reversion 测量是最硬的浪费证据** - 对 Resizer 每个改动单独回退并测 WNS 影响（d=0.000 -> 改动无贡献），得 69%/107 个改动可逐门核证为浪费。这比推测强太多了。
2. **面积效率比不等于更好** - Resizer 的 +0.584 ns 面积换来的，FAECO 的 +0.247 ns 轻量换来的，两者在 Pareto 前沿的不同位置。主张只能是面积效率高 N 倍，不能是我们更好。
3. **测量工具必须和结果一起报告** - 独立 sta 读 SPEf 的布线后 WNS 是唯一有效度量；placed_ens gate（三布局均值）是 FAECO 的内部分，不能当终端。
4. **不同电路的 Resizer 浪费率变幅极大**（s382 81%、s820 100%、s27 0%），与电路规模/复杂度/时序余量有关——写论文时不能盲目 pooled。
5. **starecovery 算法本身对 WNS 的累积退化 <=0.05 ns 保护带**是实验设置的可调参数，不是自然属性——放宽 0.05->0.10 会增加可回退数但退化更大，收紧 0.05->0.02 会减少可回退数但更安全（论文必须写死某一档并逐例报告退化）。
6. **面积效率 vs 绝对 WNS 是两个独立度量** - 对流程 X 选 A、对设计 Y 选 B 的故事留到讨论段。

## r131 — ITC-99 跨基准族 Recovery（2026-11-12）

**结论**：Recovery 机制在 ITC-99（与 ISCAS89 完全不同的电路族）同样成立。
6/6 电路实现面积回收（含 b07 33.3% 大额回收），跨基准族 14 例合计 72% 改动可回退。

**教训**：
1. top_module 自动检测不能用 parent.name（对 flat 输入目录如 inputs/b01.v 返回 "inputs" 而非 "b01"）。
   正确做法：parse Verilog module 声明，回退到 parent.name。
2. 合成管线的路径需显式控制输出目录，避免 wsl.exe 与 MSYS 路径转换交互。
3. `run_resizer_one` 内部已拼接 circuit 名到 output dir → 调用方不应再拼接，
   应把 RESIZER_DIR 设为不包含 circuit 的父目录。
4. 组合逻辑 EPFL 基准不能直接用于 Resizer（无时钟 → repair_timing -setup 不可用）。
   OpenCores 拓展需先构造带 clock 的 wrapper。
5. b02 只有 1 处改动且在关键路径（ΔWNS −0.042 ns），
   机制按设计约束正确保护——属于 legitimate negative，非机制失效。

**产物**：experiments/20261113_itc99_recovery/{inputs,arms,recovered,batch_results.json}


## 2026-11-12 — Recovery 零值与独立 CLI 导入边界（OI-083，专用测试通过）

WNS=0 与 delta=0 是合法物理量，不能用 `x or -inf` 或 `if x` 判断缺失。此处应显式比较 None；否则合法候选被拒、交互回滚排序改变、最终零值被写成 null。专用测试先得到 5 failed / 2 passed，四处最小修复后与 routed_sta 测试合跑 18 passed（1.75 s），整体回归由主线继续执行。

直接 CLI 导入测试须防当前环境 editable install 意外兜底；本次用 `python -I -S` 运行 help 才稳定暴露 ROOT/src 与实际 ROOT/code/src 的不匹配。Windows 子进程输出用 bytes 捕获避免测试诊断被编码 warning 干扰。工程测试中的外部 STA 替身不构成新科学证据，亦不自动决定历史结果影响。


## 2026-11-13 — packaged Windows 进程下 Yosys DLL 搜索与可复用镜像（OI-080）

本次正确 PATH 仍有 0xC0000135 DLL_NOT_FOUND，不能沿用历史 0xC0000139 的归因。Codex package identity 下的 DLL 搜索规则与普通终端不同；将字节同一的 2 exe / 8 DLL 放同目录后可运行。`code/scripts/prepare_packaged_yosys.py` 固化临时镜像和 share/yosys，359 项 SHA 绑定，拒绝异哈希覆盖并验证重复调用收据不变，不改工具安装。

镜像环境完整回归 1113 passed / 156 subtests，清理并发结束后受影响测试再次 24 passed。教训：测试运行时不得由另一智能体恢复/移动它正在写的产物；若发生，保留备份并在清理完成后重验受影响测试，不能只依总 rc 宣告无干扰。

## 2026-11-13 — routed DEF 重入须先显式处理已有普通布线

Phase 0 同状态结构/独立 STA 一致后，Phase 1 CONTROL 仍可能因已有 routed wires 导致 global_route 不产新 guides，触发 DRT-0626。此类装置失败先归因，不解释为恢复机制失效。此次在新预注册版本中只清副本 regular signal/clock dbWire、保留 PG/nets/连接，三臂一致，再进入重试；本条记录修正方法，物理通过状态另以运行收据为准。


## 2026-11-13 — 先保简单严格基线，不以面积或WNS单项遮蔽多指标失败

s382 A13单点补偿与B12组合均无WNS/TNS/hold全非劣点；从CONTROL出发独立回退13个动作，096却以0.594530321046%面积下降、WNS/TNS改善且hold不变通过结构/物理配置门及SEC。D三路径补偿虽然可保约2.14–2.38%面积节省，但TNS/hold退化，不能替代严格可行baseline。D独立复核未完成，本条仅记录当前主线实查与方法教训。

WNS改善不代表所有端点或hold不退化；补偿候选在固定逻辑路径上看似有利，也会经全重布线改变其它寄生。保留全矩阵和所有负例，先实际诊断，再决定修实现、改动作或换机制；容差不能替代用户零退化目标。


## 2026-11-13 — 共享路径覆盖不决定补偿收益符号（Stage D只读归因）

依据 `project_docs/evidence/recovery_repair_20261113/pathdiag/JOINT_ATTRIBUTION.md` 及SHA证据，先证实三补偿臂输入/目标正确：各只改变固定B基线指定1cell，完整连接/接口/声明不变、STA读本臂新SPEF。JOINT057覆盖5条top路径却令共享级报告增量增加17.795473ps，后继改善12–14.5ps不足抵消，五端点全恶化。覆盖识别影响范围，不能给收益符号。

Liberty A3fall弧在同一说明性slew/load下，o31a_2相较o31a_1传播更慢但输出transition更快；因此同函数、驱动档后缀/maxcap更大不能保证当前弧更快。必须区分实际pin/转换方向、输入slew、负载和上下游传播。这里插值不是实际STA工作点，路径级还含入网延时，不能将17.795473ps全归cell弧。上游输入电容与线电容略降、DFF20反而变快，也不支持笼统归因上游增载；布线电阻/RC分布未隔离，不能称唯一因果。

失败应归于本次具体动作/实现下的观测，并继续保留WNS/TNS/hold严格门，不把它写成补偿普遍无效。归因仅读既有文件，未新增STA/路由/SEC。


## 2026-11-13 — WSL 同一次调用的 stdout/stderr 可能异编码

strict_area_search自包含副本preflight中，WSL sha256sum返回rc0且stdout ASCII正常，但stderr有UTF16LE代理警告，subprocess text=True统一解码崩溃。修复为bytes捕获、只按协议decode stdout，stderr保原始诊断；不要把这类异常误判为SHA不一致或重跑EDA。修复后197本地副本/210alias校验及默认preflight通过，selection专用34测试通过。


## 2026-11-13 — 先确认候选池有可行改进，再判断排序价值

固定096 seed与另外9个正面积rollback动作组合，全9实测TNS退化、strict0；面积/风险两冻结排序所有prefix均退回原exactseed，k3无优势。全集k9同终点是数学/实现自检，不是调度收益。两策略共享测量只计9route，不按两排序倍增；历史13标签是旧41route子集，不能重复加成本。没有可行改进的池不能靠改排序名称产生收益，结论也不外推排序普遍无效。

完整网表+Liberty静态审计得到62兼容降面积target，旧rollback仅覆盖10，说明历史撤销表不是完整生成器。但候选合法不等于物理安全：漏掉的054→2与→1同面积，单/双点实际三时序都更差。扩展应先建立完整候选签名/实例/来源和约束，再逐项验证，不把62当62个收益，不简单将遗漏全归bug。clock-family名称也不等于时钟图，clkload0虽输出未连却承担时钟负载，不能按无输出删/缩。

实际接受必须保留原端点网表/ODB/SPEF精确SHA；全失败复用已验seed而不重路由，预测只排序不做实际准入。当前数据IO约束未齐，已验相对非退化只限原约束域。


## 2026-11-13 — 超时包装日志与混合编码的结构化读取

timing_budget历史重筛两次工程失败：超时wrapper向stdout加[run]文本使整流JSON解析失败；历史WSL代理警告与指标异编码导致严格UTF8读取失败。保留原raw，在独立文件输出结构化JSON；历史日志先核字节SHA，再按既有审计方式errors=replace/NUL清理，仅提唯一ASCII指标。该兼容读取不改变输入或指标身份，不把解析失败当物理科学失败。v3与独立审计rc0，重筛0route/0STA。


## 2026-11-13 — 用阶段快照而非综合输入归因Resizer净新增面积

s382完整层级/DEF审计把综合809.5264、修复前CTS892.1056、Resizer最终1052.2592分开。若用综合初态作纯Resizer分母，会混入82.5792的CTS/前处理增量。以原flow中CTS后、repair_timing前快照为A0，最终master净新增160.1536，RESTORE074回收46.2944，对应28.90625%；总降4.399524%仍另报。

完整有符号账8新增buffer+24最终master变化与日志34过程resizes不是同一计数，不硬改工具日志。没有立即repair后快照时明确归属受控repair流程的最终master净差，不声称瞬态操作总和。该分母只验s382，不反推其它设计；证明/时序/IO门继续独立验收。


## 2026-11-13 — 已验环境workaround须进入每次完整回归配置

budget_core整体回归v1遗漏前置packaged DLL镜像，再现原Yosys3221225781(DLL_NOT_FOUND)。同exe SHA在已验scratch镜像rc0，既有prepare_packaged_yosys.py验证359项一致，支持环境配置遗漏归因，不能据失败先改新生产代码。应保留v1完整失败日志并等退出，再用正确PATH串行回归；避免为节时并发清理与重跑造成测试产物干扰。此条尚不声明重跑已过。


## 2026-11-13 — Git直连失败时复用已启用的系统代理

本轮push两次直连失败（reset/443连接超时），系统Internet Settings已有ProxyEnable=1而Git未配置http.proxy。读取现有代理后通过单次 `git -c http.proxy=<系统已启用地址> -c http.version=HTTP/1.1 push origin main` 成功；不改全局代理、不更换remote，也不把连接失败误归因提交内容。日志保存实际成功提交与返回码。


## 2026-11-21：OpenROAD `initialize_floorplan -utilization` 百分比单位陷阱（`b15` 11.4 万 tapcell 超时根因）

- **现象**：ITC-99 `b15`（4,300 个逻辑单元，功能面积 `34,895.97 µm²`）在重布线阶段 `pin_access` 耗时 2 分钟、`detailed_route` 超过 600s 超时，即使只清除 6 条局部直连信号线仍超时。
- **根因**：`resizer_flow.tcl` 中写了 `set UTIL 0.35; initialize_floorplan -utilization $UTIL`。OpenROAD 的 `-utilization` 参数单位是**百分比（0–100）**而非小数（0–1），传入 `0.35` 被当作 **0.35% 利用率**，导致生成的 Die 面积膨胀 100 倍至 `2937 µm × 2937 µm`（`8.60 × 10^6 µm²`），随后 `tapcell -distance 14` 在空版图上插入了 **114,480 个 tapcell**（总组件 118,780 个），拖垮了全图 `pin_access` 与 `detailed_route` 区域索引。
- **修复**：将 `-utilization` 改为百分比整数（如 `35` 表示 35% 利用率），`b15` 核心面积即回归正常的 `85,280.54 µm²`（`297 µm × 297 µm`），tapcell 降至 `1,144` 个，总组件数由 `118,780` 降至 `5,494`，内存占用由 `712 MB` 降至 `175 MB`。


## 2026-11-23 — 同一个实例贯穿 Verilog 候选、OpenDB 操作与物理回读（OI-088）

`s713` 的 Verilog 将带斜线的实例写成 `\DFF_0/rebuffer1`，DEF 和 OpenDB 使用 `DFF_0/rebuffer1`。初版 `replace_cell` 使用词法转义名导致 `STA-0125`。仅修命令后，布线成功，但期望 master 表带转义前缀，后验对比将同一实例识别成两个键，跳过 STA。两次错误分开保留。

候选动作 ID 保留来源可追溯性，物理命令与期望 master 使用同一个去前缀实例名，并逐候选校验实际 DEF 中的原 master。复用路线必须绑定全部动作、参考输入及工具资产指纹、产物 SHA256，再独立读取网表和执行四场景 STA。`s713_replay/RUN_001` 已确认目标 master、DRC=0 与四场景有效度量，随后因实测 IO+OCV hold 未过门。工程失败、复用路线和真实时序拒绝分别记账。


## 2026-11-23 — 读既有 OpenDB 前绑定物理生产器与数据库 schema

ASAP7 GCD 原 ORFS 物理结果的 ODB 需要 schema 0.142，OpenROAD 26Q3 读器仅支持 0.134，`read_db` 在时序分析之前退出。应保留生产器版本和二进制指纹，先确认数据库兼容性，再把失败归入时序或算法。现成 DEF 与 DRC 报告仍可用于绑定原物理状态。

时序复测可从同一输出端点的 V、SDC 与 SPEF 单独恢复，逐视图固定 Liberty；ODB/DEF/DRC 保留原件与哈希。本轮 OpenSTA 3.1.0 读同源三件，FF setup/hold 与生产器报告在其输出精度下一致，TT 和 SS 也获得有效结果。此方法验证 STA 导入和已有时序，物理重布线的兼容性继续由原生产器或后续独立预检判定。证据见 `project_docs/evidence/tcad_preflight_20261123/`。


## 2026-11-23 — 先用等价、不等价夹具与合成自比验证 Ibex SEC 模型

含异步触发器的 Ibex 映射网表需要明确两态时序模型。当前驱动用 Yosys `clk2fflogic` 将时序单元转换为 SAT 可处理的逻辑，使用库模型并记录同时发生异步复位撤销和时钟边沿时的负保持时间约定。开发夹具区分了等价与不等价实例（`1/0` 与 `0/1`）；同样策略在 SKY130HD 和 ASAP7 各自的合成网表上自比得到 `13517/0`、`17235/0`。技术探针、合成自比和实际布线后端点 SEC 分开记账，候选验收绑定真实 gold/gate、具体库、输出及证明计数。


## 2026-11-23 — 物理专用单元需要与 SPEF 保持同一表示（OI-090）

SKY130HD Ibex 原生 ODB 包含 84 个天线单元，ORFS 用物理专用 master 过滤生成逻辑 Verilog。若直接把逻辑导出与完整物理 SPEF 配对，独立 STA 仍可能完成且给出数值，同时报 `ANTENNA_*` 节点找不到。先审查寄生注解告警，再以同一输出的完整物理 ODB、原 SDC 与 SPEF 重测，模型中缺失的天线节点告警消失。TT 正常复现原生报告，SS 的负 hold 则是真实当前模型结果。同工艺对照各臂要使用同一表示，SEC 仍可使用面向逻辑的导出，分别绑定端点和工具身份。


## 2026-11-23 — 末段填充后的 ODB 重入需检查 filler 占用

SKY130HD Ibex 从原布线终点添加 14 个 hold buffer 后，原 21,961 个末段 filler 全部保留，合法化因 100.1% 占用触发 `DPL-0038`。固定输入和原约束，按 master 验证仅移除原四种 filler，在增量布线完成后用同四种 master 恢复填充。复测保留 14 个新 buffer 与原非 filler 实例，完成合法化、零 DRC DRT、RCX 和 21,936 个 filler 的复填。物理 DRC 与独立天线检查分开，天线一处未过由 OI-093 记录。


## 2026-11-23 — 局部改线后独立检查天线

SKY130HD Ibex 的 hold 修复增量路由可以在详细布线 DRC=0 时仍有天线违规，`_02` 首次新提取端点就是此例。先用原 ORFS 规则独立检查，记录违规网和接收引脚；对 `_03` 的实际两条违规网原地调用 diode-only，同一工艺续跑增量 DRT。两个门均清零后才提取并使用同一 SDC 重新测时序。记录零 DRC、天线零、RCX 和等价四类验收结果及产物哈希。

## 2026-11-23 — 零编辑重布线可改变 hold，复提取可验证冻结端点

SKY130HD Ibex 在修复后共同起点做零动作 DRT，以文本导引或保留 ODB 内嵌导引分别改变 13 或 16 条网的布线。两次最终 DRC 均为零，SS hold WNS 均减少 0.079936 ps，高于既定 0.001 ps 非退化容差。若目的在于验证冻结物理端点能否重读，应以同一 ODB 重提寄生并保留原走线。此处复提后 FF/TT/SS 的 setup 与 hold WNS/TNS 均精确复现，SEC 为 13648/0。零编辑复提、零编辑重布线以及实际候选 DRT+RCX 单独计数。候选继续相对冻结起点执行原有时序门。[三版实测收据](../project_docs/evidence/tcad_ibex_20261123/SKY130_NOOP_AUDIT.json)

## 2026-11-24 — 分开诊断有限预算下的覆盖损失和重布线 hold 变化

六次物理预算下，Ibex 和 GCD 的原 FAECO 递归花四次拆分首次被拒整批，剩余一槽单门，只覆盖候选池头四名。两例各有较后排名的整批实际通过。先把命中相对 hold 的首批拆分延后，在只读回放中走到固定臂已经实测的合格端点。AES 的固定臂同样零回收，说明扩大覆盖本身无法解除这批相对 hold 拒因。验证调度改动时，固定起点、候选池、工艺门和物理配额，分别记录排序覆盖、实际工具成本和绝对时序。有实测收据的回放可确认已有物理端点，独立复跑才能测新调度及墙钟。[调度诊断](../project_docs/evidence/tcad_ibex_20261123/SCHEDULER_COVERAGE_DIAGNOSTIC.md)

AES 一个同配方零编辑控制可产生 0.676792 ps 的 SS hold WNS 下降，未触达的六条网有改线。调换该参照可以诊断共同扰动与候选剩余变化，8/18 的投影仍没有达到原面积目标。要把寄生效应从候选单元切换分开，应在原 SDC 和对应 Liberty 下做 CONTROL/候选 ODB 和两套 SPEF 的四格 STA，先校验同源两格复现原指标，并核验寄生注解与最差路径身份。AES 两个固定批次的三个拒收视图由各自候选 SPEF 复现全部末端 hold WNS 变化。当前数据可定位这三例寄生因素，通用 hold 容差的制定还需独立路由样本。[实测登记](../project_docs/evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-sky130hd-aes-zero-edit-reroute-and-scheduler-diagnostic-v1)

## 2026-11-24 — 保护路由需读回 ODB 实际走线类型，并对齐无序连接

当前 AES 使用的 OpenROAD `b511b6a` 在 `read_def -incremental` 模式未注册 NETS 路径回调。成功读入 DEF 命令日志并不足以说明布线状态被改写。AES v2 的输入补丁含 15,657 条 `FIXED`，实际输出仍是 0 条 `FIXED`，重复了零编辑的六条改线和 SS −0.676792 ps。改用 `read_def -floorplan_initialize` 并在下一步前从 ODB 导出回读实际布线类型，确认 15,657 条保护状态生效。v3 零编辑的三角 setup/hold 指标与冻结起点精确一致，原 0.001 ps 判据仍可使用。

读回会调整 DEF 各网的连接端子顺序。几何比较应将连接视为集合或多重集合，保留线段、过孔、层和线宽规则的完整表示，单列 `FIXED`／`ROUTED` 类型。v3 零编辑的 15,657 条网按此口径全部与 CONTROL 一致。另需注意 `drt::check_drc` 是该版本全块检查入口，部分检查会跳过 `FIXED` 与 `FIXED` 的组合。候选若要用同口径 DRC，应在保持几何不变的副本恢复原 ROUTED 状态重查。[修复试验](../project_docs/evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-sky130hd-scheduler-and-aes-clock-route-repair-v1)

在真实布线上同时保护所有未编辑网可能留下已换门引脚与相邻固定线的间距或短路。AES 两个批次的 DRT 自带最终报告均为零，额外全块检查均发现四条标记。将各自标记涉及的两条非时钟邻网加入同批清线重布线，重新精确审计全部保护网，并在解锁副本做全块 DRC。两例全部通过 DRC，其中一例也通过原三角时序及 SEC，另一例仍触发三角相对 hold。即使保护时钟线的几何不变，邻近重布线后的新耦合仍可能改变 min timing，应按真实抽取结果逐角验收。[AES 保护路由报告](../project_docs/evidence/tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)

## 2026-11-24 — 并行逐候选筛选保留顺序和串行停止前缀

每个固定 SPEF 的候选 STA 独立执行，按原序消费结果。每波大小同时由并发数、未读候选数、剩余试探上限及离目标通过数的余量限制，当前波最早完成的结果不改变下一个波的位置。这样可验证每个实际试探都属于原串行前缀。Ibex/GCD 的 1 路和 4 路都复现原顺序和完整指标。报告墙钟与候选工具时间和，以识别总工具时间上升、阶段墙钟下降的情况。[筛选报告](../project_docs/evidence/tcad_ibex_20261123/SCREEN_WORKERS_BENCHMARK.md)

## 2026-11-24 — FF/TT 与 SS 的残余 hold 需要同时读时钟和数据路径

AES 三个两门子集的寄生代价不同，删掉一门可以减轻捕获侧的部分耦合，也可能去掉 SS 数据路径的延迟补偿。用等面积门替换保留 SS 原改善，又使 FF/TT 的发射时钟延后，实际三角通过。判断时先用 ODB/SPEF 交叉固定同一路径，再比发射、捕获和数据到达的变化。读 SPEF 双节点耦合行要先识别哪个端点属于当前网，避免把列顺序误作归属。多动作组即使直接网没有交集，也应合并后重新详细布线、抽取和三角验收。[AES 残余 hold 优化](../project_docs/evidence/tcad_ibex_20261123/AES_RESIDUAL_HOLD_OPTIMIZATION.md)

## 2026-11-24 — 用只读 ODB 规范化定位 pin access 辅助状态差异

嵌入导引线路里同时执行显式 `pin_access` 和 `detailed_route` 默认步骤会计算两次。去一次后，GCD 和 Ibex 的单端点 DEF、提取和时序验证等值，ODB 原始字节却不同。比对接入点时，应去掉临时对象句柄，按所属 pin、坐标和层读取多重集；把接入点和关联引用从另存的副本清理后再比较原数据库其余内容。两设计各自的副本字节一致。GCD 将两种单次调用各自运行，输出原始 ODB 也一致。此方法可以限定变化域，新增搜索/增量路径是否同样稳定需独立验证。[pin access 对照](../project_docs/evidence/tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)

## 2026-11-24 — 验证接入点配置时把路由起点作为独立变量

在 GCD 原冻结搜索中，把单次与双次 pin access 各独立运行两臂并交换顺序，检查完整六次候选轨迹及相同面积目标；两组均保持验收和物理指标，含筛选首达实测各缩短 4.249、5.073 RAW s。另以真实保存的 A/B ODB 为输入，四格组合第二步的 pin access 配方，能把输入 ODB 差异与第二步配置分开。两设计各自的四格判定一致，但从冻结起点累计重布线与中间 ODB 重入的结果在两个设计上出现相反的接受改判。Ibex 有一个被违反的电容限制位于未改变自身连接和几何的输出网，真实 SPEF 电容仍变大。完整实验应固定起点策略并明确计时范围。加载通用工艺脚本从哈希绑定的 `setRC.tcl` 定位 ORFS 根，设计专用 FastRoute 路径可能多一层目录。[冻结搜索](../project_docs/evidence/tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md) · [两步重入](../project_docs/evidence/tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)

## 2026-11-24 — 自动路由重试要用实际 marker，计入完整验证时间

AES 的保护路由以 DRC marker 同时含已有非时钟信号网与直接触达网／编辑实例作为放行条件，并从同冻起点重试一次。在单门第 1 次，自动放行消除了短路但原 SS hold 仍拒；固定及 FAECO 的第 2 次以同一自动邻网修复通过原门并回收 33.7824。计时将初次路由、解锁态 DRC、重试、三角 STA 和 SEC 全部纳入，并分开报告逻辑派发、完全评估与已启动但被预算截停的物理调用。若两个方法在同一重试被截停，窗外可单独跑一次同一重试检查物理可行性。AES 此六门窗外完成后仍违反 FF/TT 相对 hold，捕获时钟支路虽保持几何，其新提取地电容改变。[AES 正式报告](../project_docs/evidence/tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)

## 2026-11-24 — 从真实跨视图路径定位等面积动作置换

对 AES 累计排名 4–9，先与正式合格三门做 ODB/SPEF 交叉，明确推迟捕获和提前发射同时压缩 FF／TT hold。再用同层 DEF 距离及 SPEF 的捕获支路耦合网定位需撤回的一门，用以前实测可延后发射的同面积动作置换。新的六门实际同时消除了捕获电容增量和增加了发射电容，三视图通过原联合门；保留 setup 新增负端点计数，TT 为 2、SS 为 1。该例对置换双方联合成立，若要归因到某段线或建立通用择优规则，仍需对另一组候选做独立单因素或前置匹配验证。[AES 归因与修复](../project_docs/evidence/tcad_ibex_20261123/AES_RANK4_9_HOLD_REPAIR.md)

## 2026-11-24 — 区分候选覆盖、首次达标与同窗最优面积

延后相对 hold 拒批的拆分可以让新候选先用预算，四路冻结 SPEF 筛选里的 TT hold 和电气在 Ibex 18 个候选间相同，延后队列又未用到。复用冻原 DEF/SPEF 的触达网电容后，保留首批，并在实际相对 hold 拒收触发后用面积与电容重排未访问候选。必须同时报告真实派发序列、目标首达、全额准备时间、720 s 内最优、按次口径和新负 setup。Ibex 首达少一次而窗内面积相同，GCD 首达次数相同而第六次增加合格面积。小电容排序描述风险代理，时钟路径和重布线耦合仍需真实三角验收。[触达电容报告](../project_docs/evidence/tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)

## 2026-11-24 — 工具超时按派发时实际截止来源归类

硬窗执行时，子进程可能因直接受剩余墙钟裁剪而在总 deadline 前几毫秒返回，从异常时刻判断会漏掉。AES v1 独立 DRC 时发生 5.096 ms 的提前返回，导致无真实终态。派发时记录阶段原限时、实际使用限时与截止时间来源，只有真的由全局剩余窗裁剪才记为预算截停。普通阶段工具超时和工具失败应走原异常路径。v2 用回归复现此情形，且新一轮硬窗配对的末尾独立 DRC 实际截停能生成可逐项审计的真实终态。[AES 配对报告](../project_docs/evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

## 2026-11-24 — 将重试的候选风险与已验收端点分开

AES 的低触达电容次组在第一次有 DRC 时已出现相对 hold 退化，实际邻网重试只修正 DRC，FF/TT 仍拒。以最差路径交叉换 SPEF 复现原退化，13 条观察网电阻逐项一致。只用于开发的提前延后规则省去这一实际重试，让后续通过的同字节端点更早进入验收。另一六门的初始 setup/hold 和 DRT 报告可过，却在恢复正常 ROUTED 状态的独立全块 DRC 查出 8 个标记，不能计入回收。比较时分别保留非法初评时序、真实重试是否可修、因预算截停及完整验收；对其他组合需要重新抽取和审计。[AES 配对和重试报告](../project_docs/evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

## 2026-11-24 — 对已绑定的标记先放行，复查同一动作的物理等价

保护路由的全块 marker 坐标应同改动实例或直接信号网关联，限定只放行同个 marker 上的已有非时钟信号邻网。AES 已知三门的真实重试原来同样从冻结起点开始；把两条已证邻网提前放行，仍得到逐字相同的 ODB/DEF/网表、相同提取与三视图，节省一个真正失败的 DRT/RCX、三角 STA 与独立 DRC 调用。对已知六门用同样办法提前放行四条，独立首试及硬窗正式复跑均通过。在读出用时差时先按完成回调截断进程账、拆开共同筛选和准备费，再比较同端点的分项 RAW s。该做法可验证历史标记支持的恢复，自动获得新候选标记的代价与跨设计表现另计。[AES 定向修复报告](../project_docs/evidence/tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md)

## 2026-11-24 — 诊断包复用要绑定动作、原约束和同一路由几何

从外部输入使用既有 DRC 时，逐项比候选动作与直连网、当前冻原矩阵与 SDC、物理收据 ODB／DEF 和独立报告的几何身份，回读原报告复核 marker 数。只有所有标记有明确可操作的非时钟邻网才提前放行。实际再出现 DRC 时只把真新增邻网记入重试，物理验证保持已放行集合。先固定完全相同候选再按 ABBA 实跑，可以同时观察是否少一次真实物理验证和最终端点是否逐项一致。本次读同一组六门诊断后，两种顺序均保留同 SHA 端点并少一轮检查。已有诊断的读取成本与从零生成诊断的成本应分别报告。[诊断组件对照](../project_docs/evidence/tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md)

## 2026-11-24 — 冷诊断先去掉编辑网旧线，非法初评时序只能用于诊断

在冻结 ROUTED 版图换门，同时保留编辑实例的旧直连线会产生额外短路、最小面积和间距标记。AES 同六门保留旧线的 38 个标记中有 30 个均涉及待替换的直连网；清掉这些旧线后，剩余八处与之后真实独立 DRC 逐字相同。实时把每次诊断费用计入同固定派发消融，仍通过少一次完整物理验证节约同端点首达。对另一组旧案按非法初评 SS hold 暂缓的六门，放开真实相关邻线再路由后，原三角 hold 与 setup、DRC 和 SEC 全部过门，证明非法初评的时序可以漏掉可行修复。在窗口内把预检、真实 EDA、因硬窗未完成的候选和完整正式验收各自计数。[冷启动矩阵报告](../project_docs/evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)

## 2026-11-24 — 同派发比后端，同后端比派发

原 AES 三臂还缺 FAECO 配常规后端，无法知道六门面积回收需要两项机制一起出现。补齐后做四组合交换顺序，并独立按完成的物理收据重算。固定和 FAECO 各自使用在线诊断后，同动作与同物理首达均实际节省时间。常规 FAECO 两次仍在第 4 次 DRT 耗尽预算；在线 FAECO 两次都及时完成同组六门，同时其首达到阈值仍晚于固定。分别报告同目标首达、窗内最优和截停阶段，避免以只看时间或只看最后面积替代全验收口径。[2×2 正反序报告](../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md)

## 2026-11-24 — OpenSTA 跨查询只保留端点身份和标量

JPEG 独立最小／最大时序定位中，首版在 `find_timing_paths` 的 min 结果循环内再执行 max 查询，访问下一条旧 PathEnd 时崩溃。固定 OpenSTA 的 `Sta::searchPreamble()` 会在新查询前删除上一组 PathEnd。先读出整组端点名和 min slack，再对这一组端点批量查询 max 并立即提取 slack，实跑复现 26 个端点。时序修复前同时核对同端 min/max 和共享支路的其它约束；四个 FDCT 数据端两侧都负，最差 reset 需要的延时超过公共支路其它端点的 recovery 余量。后续物理修复须按不同支路及路径判断，并重新验收原约束。[JPEG 资格报告](../project_docs/evidence/tcad_holdout_20261123/JPEG_CONTROL_REPORT.md)

## 2026-11-24 — 贪心归因要核对排序、实际派发宽度和物理成本

历史小电路的若干 FAECO 轨迹和强基线都逐门尝试，候选排序不同会改变第一次遇到安全替换的位置，也会改变后续动作的累计参考端点。比较调度时先冻结候选池、共同物理后端和墙钟收费，串行交换运行顺序，再读逻辑请求覆盖、候选拒因和实际工具账。在 AES 的两次配对中，单门的两次早期 SS 相对 hold 拒收令共同阈值延至第 4 次请求。FAECO 同样遇到 hold 拒收，重排后第 3 次通过，少一次完整 DRT、诊断预览和独立 DRC。两种策略各接受两次，批次大小与覆盖带来窗内面积差。用共同阈值回答达标快慢，用窗内合格面积回答同预算收益，分别记录截停候选缺失的验收。共同后端是派发对照的前提，排序和批量的分量需进一步用同反馈拆分。[贪心配对报告](../project_docs/evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md)

## 2026-11-25 — 跨工艺复用物理后端先验证库绑定与零编辑

ASAP7 UART 的资格收据原以哈希组记录库。将其接到筛选入口时逐成员核对字节及 SHA-256，再派生路径表，保留原始收据和符号链接身份。将清点和物理候选分别绑定到 seed 和运行根，以防评估标签从错误的根目录计算。UART 零编辑实际走完整保护布线、RCX、时序、DRC 和 SEC 后，保留原网表并重现原时序，随后才开始计时。 [UART 对照](../project_docs/evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md)

冻结真实候选池后先检验灵敏度排序的分辨率。AES 的 18 个输出裕量均高于历史 200 ps 截顶，原公式产生同一个动作顺序。去顶的预检规则确实改变了顺序，排序 STA 和解析按每臂实计。 [AES 强对照预检](../project_docs/evidence/tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_PREFLIGHT.md)

## 2026-11-25 — 等回收门槛、预检覆盖与实际重布线成本

AES 两次同后端配对改用灵敏度排序后，FAECO 首达预设小门槛早约 17–20 s，实查两法均进行三次 DRT/RCX，等价证明次数由 2 次降为 1 次占了主要时间差。使用同一日志回读 33.7824 µm² 时，两法在不同请求结束后达标，时间差约 147–152 s。记录首达实际回收、逐阶段耗时与时限内最优面积，可避免用一个门槛外推整个搜索过程。 [AES 强对照](../project_docs/evidence/tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_REPORT.md)

GCD 固定候选两轮预检均未见标记，同一三门在四臂正式首轮重布后均产生三处短路。释放标记支持的同一邻网后独立 DRC 清零，TT 相对 hold 仍拒收。新冲突的预判需要覆盖直连网重新生成后的几何。首轮 DRT 耗时在同一物理产物下波动明显，应分别计量预检的直接开销和后端的实际次数，保存验证范围。 [GCD 诊断边界](../project_docs/evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_REPORT.md)

## 2026-11-25 — 区分调度提议和实际物理评估

二分时先接受一个子集，后续子集与累计集合合并可能还原已经拒收的动作。对共用冻结起点、有完整物理验收且仅因 setup 超限的拒收，复用该判定并继续拆分可以释放验证名额。UART 正反序实测各跳过一次，前五次实际评估复现了原轨迹中的五个不同端点，新增的第六次提高了回收。首达小阈值发生在跳过前。应同时记录达到同一物理端点的时间、六次实际评估内的最大回收以及新增提议的验收。 [UART 去重复跑](../project_docs/evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)

## 2026-11-25 — 末次评估排序须分辨候选的实际受限风险

UART 的末次预留按面积和触达电容排序，两序均把最后一次评估派给同一慢角相对 hold 拒收动作，回收少于去重版。对一个拒收和一个同面积合格端点做网表与 SPEF 双向交换，仅更换实布 SPEF 即各自重现 SS hold WNS，固定两门 SPEF 的读数对两项完全相同。低成本预筛需要实测对重布影响的分辨力，再决定是否值得占用末次名额。 [UART 末次预留实验](../project_docs/evidence/tcad_holdout_20261123/UART_DEFERRED_RESERVATION_REPORT.md)

## 2026-11-25 — 等面积条件下核对 hold 预筛分数

UART 冻结直接网和时钟路径的邻近分数可改正开发样本末次排名。迁移到 GCD 后，整体排序仍有信号，但等面积通过／拒收对出现同分。换实布 SPEF 复现 TT/SS 差异，两端点实际均改动了冻结时钟网几何。先记录跨类同分对与等面积子集，再对同分个案核查实际改线范围和寄生变化。用直接电容打破同分后，GCD 等面积排序与电容基线持平。 [跨设计结果](../project_docs/evidence/tcad_holdout_20261123/UART_HOLD_GEOMETRY_REPORT.md)

## 2026-11-25 — 预览费用以省下的一次完整评估为上限

GCD 等面积配对中，增量导引估计与只更新直接网的冻结 SPEF 模型均无法区分 TT/SS。限域两轮布线和原范围早停产生相同的 hold 误判，说明这组候选的区分需要观察较后阶段的布线变化。完整拒收约 9.7 秒，两份最短 DRT 预览也要约 11.5 秒。应用前分别实测拒收、通过、预览及校准，用 `预览两份 + 完整验收通过件` 比较原评估总耗时。直接叠加估计总 C 的增量可能使实布对地电容变成负数，比例缩放和保留耦合只能作为近似诊断。 [GCD 预览试验](../project_docs/evidence/tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)

## 2026-11-25 — 布线检查点读回与工程验收分开核对

GCD 限域检查点解锁后，规范化 DEF 和导引保持同一，恢复调用也确实从保存的 DRC 标记进入后续迭代。同进程仍可不布通或超时。新进程重入跳过 PA 后两序均完成验收，但总时间更长。一个原 hold 拒收端点因时钟支路实际改线而转为合格，可单独作为补救候选证据。计时须包含前段布线、保存与恢复、最终 RCX 和验收，第二段 DRT 时间不单独代表加速。 [GCD 检查点实验](../project_docs/evidence/tcad_ibex_20261123/GCD_LOCAL_ROUTE_REENTRY_REPORT.md)

## 2026-11-25 — 已被时序拒收的完整布线 ODB 可作为备用状态

补救前先与同冻结池已验收的最高面积回收对齐，且只触发纯 hold 拒收。四项试验只救回 UART 三门，净超过旧最好 0.02916 µm²。UART 原 DRT 的 ODB 与两段补救重做出的三个检查点逐字节相同，可直接复用。复现实测逐个终态相同，跳过一段仍需计新进程、第二段 DRT、RCX 和原门验收，且 DRT 波动会侵蚀理论节省。两组六门的 SS 变好后仍因 TT 拒收。此类补救的总成本需要计入失败，性能归因要区分已消除的工作与观测墙钟。 [重入补救报告](../project_docs/evidence/tcad_ibex_20261123/HOLD_REENTRY_RESCUE_REPORT.md)

## 2026-11-25 — 区分开放网与实际改线

UART 的 TT 最差路径为同一触发器自反馈，捕获与发射共享时钟叶。固定邻域外全部线网后，单纯开放以及擦除一条 D 端线再重布均恢复原几何和时序。单独擦除并重布共享时钟叶才产生不同的物理端点，两个候选的 TT 与 SS hold 均进一步下降。以规范化几何和独立全块验收区分未发生变化、真实局部变化和窗口逸出，再用原门计可用面积。 [UART 捕获邻域报告](../project_docs/evidence/tcad_ibex_20261123/UART_TT_CAPTURE_WINDOW_RESCUE_REPORT.md)

## 2026-11-25 — 纯墙钟对照同时报告首达与终点

UART 的独立核验八臂显示，去掉验证次数上限会改变末次批宽及累计轨迹。纯墙钟下固定批和灵敏度单门分别自然结束于 6 和 18 次，现行去重为 19 次，交错为 26 派发／25 完成。强单门先到三个小门槛，现行去重反在共同实际面积 0.77274 µm² 早 105.569／103.522 秒，并验收到更高终点。按已核前缀比较固定时限最高回收、对应实收面积和指定目标首达，另列池耗尽、窗尾截断及全工具实耗。两种 FAECO 各有八个合格检查点，交错两轮都比现行多完成五次 hold 拒收，约额外用 122–123 秒。两法各一对同物理的纯 hold 重复拒收，现有去重只处理完整且确定的 setup-only 拒收。开发结果先冻结，再做独立留出。 [纯墙钟开发报告](../project_docs/evidence/tcad_wallclock_schedule_20261125/REPORT.md)

## 2026-11-25 — 多角资格先核原生流程实际加载的 Liberty

ASAP7 ethmac 的原生 CTS、GRT 与最终报告三个步骤仅加载 RVT FF Liberty。用原 SDC 和实布 SPEF 做三角资格后，hold WNS 均为正且 TNS 为零，TT／SS 电气仍有 9／1,017 个 max-slew 拒因。只读映射在已绑定的 990 个 SS 违规中定位 982 个 `NAND2x1` 受端，涉及该子集的 250 条网。TT 九个受端在三条 `NOR2x1` 驱动网。应先核真实载库和违规引脚绑定，再辨别是否需要在原 SDC 下修复共同起点。物理、时序、电气及 SEC 分开验收，起点资格失败单列为候选缺席。[Ethmac 原资格与归因](../project_docs/evidence/tcad_wallclock_schedule_20261125/REPORT.md)

## 2026-11-25 — 同起始排序用于分离批宽、反馈及物理拒收成本

SKY130HD `riscv32i` 的六臂对照中，强单门在纯墙钟下取得最高回收，现行去重的三个已完成 setup 拒收耗时约 431–432 RAW s，设计未触发相对 hold 重排。固定第 3 批与现行第 1 批的分项冻结 TT TNS 和实际组合 TNS 分别为 −654.747→−144.389 ps、+235.421→−796.959 ps。已有实物验证说明灵敏度最前面的三门和六门累计集合可通过。优先用同起始顺序比较固定、单门和反馈，再读窗内面积和失效成本。保留时间目标交叉，现行去重在一个中等面积阈值先到，在 720 秒最大回收上靠后。[完整报告](../project_docs/evidence/tcad_wallclock_schedule_20261125/REPORT.md)

该设计的后续同榜六臂测到固定与 FAECO 同累计动作、同实布九门和几乎同首达时间，且动态规则全未触发。两者共用三门批宽，在同实收 48.7968 µm² 较灵敏度单门快约 297–304 RAW s。解释等预算收益时依次控制起始排序、批宽与实际触发的反馈。共同下限适用于首达目标，精确实收用于同面积速度比较。定向前缀可行性和策略独立找到端点的费用分别保留。[排序对齐报告](../project_docs/evidence/tcad_rank_alignment_20261125/REPORT.md)

## 2026-11-26 — 原生提案按网表身份验收，按 OpenDB 原名施加动作

`sky130hd/aes` 原生提案的 `sa32_sr\[7\]$_DFF_P_` 初次找不到冻结网表实例。现有规范化器将其对齐到 `sa32_sr[7]$_DFF_P_`，逐项核对源 master 后 120/120 命中。物理脚本继续使用原始转义名字查找 OpenDB 对象。ASAP7 UART 负对照的 16/16 项仍不在冻结动作空间。原生批次重试用独立目录、逐臂原子收据，防止覆盖已有路由日志。用子进程账本区分单次工具上限、外窗截停和完整验收。[V5 实验报告](../project_docs/evidence/tcad_v5_revision_20261126/REPORT.md)

同一名字还用于局部窗口的 `findInst`。修复后，120 项重放生成 81 个窗口并送达预检完成标记，但 OpenDB 遍历到的 241 条直连网与数据网账本的 238 条不一致。触发器的 Q、D、CLK 三网解释该差异，CLK 对应受保护的 `clknet_leaf_3_clk`。因此完整提案落入保护作用域不兼容。数据网投影完整核对 119 个实例、80 个窗口和 238 条直连网。规范化逻辑身份、原始数据库名称和物理权限须按各自边界验证。[V5 实验报告](../project_docs/evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-26 — 更换时序预算须同时绑定验收门与调度策略

同一冻结快照下，物理验收按逐角 WNS／TNS 门判定，外层调度另用标量 WNS 策略。只改调度会使宽档仍被 1% 物理门拒收，并让各档共用旧 TNS 上限。先按原门验证已有零动作参考，再同步重建两层预算。离线同一组三角读数中，270 ps 周期下 4 ps WNS 损失在 1% 拒收、2% 通过，90 ps TNS 损失在 2% 仍拒收。3600 ps 错配直接失败。复用旧预检时还须匹配 CPU 亲和性，绝不能跳过既有的配置一致性检查。[四档预算脚本](../project_docs/evidence/tcad_v5_revision_20261126/run_v5_step3_multibudget_online.py)

## 2026-11-26 — 独立设计资格要比对真实 I/O 与综合时钟单位

旧 SKY130HD `riscv32i` 的原始 Tcl 把空列表值误作 `lappend` 的变量名，导出的 6 ns SDC 只有 99 个输出延时。原始和导出约束文本相符无法证明端口已约束。其 `clock_period.txt` 又将纳秒数 `6.0` 原样传入采用皮秒的 ABC `-D`。新独立构建明确使用 `[all_inputs -no_clocks]`、10 ns 的 2 ns I/O 延时与 10,000 ps 综合目标，资格脚本将导出延时逐端口与实际网表比对，并核对产出的综合时钟记录。物理审计和三角时序通过后才能声明独立参考达到严格收敛。[独立参考资格脚本](../project_docs/evidence/tcad_v5_revision_20261126/run_v5_stage5_reference.py)

## 2026-11-27 — 轮换比较臂时同时绑定评估产物的根目录

Stage 5 的共享零动作资格在 runner 目录成功，首个单门实验切换到独立臂目录后，评价器仍用旧 runner 根计算相对路径，因而在候选物理评估前退出。离线夹具复现该异常，统一在臂入口同步两个目录后覆盖三种派发模式。原合格参考旧协议与关闭前日志保留，以新驱动重新绑定筛选、零动作和在线协议。真实首候选完成 DRT／RCX、DRC、三角时序和 SEC 4559/0，回收 8.7584 µm²。路径修复的验收可与三臂科学结果分别追溯。[Stage 5 报告](../project_docs/evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 — 独立脚本需复用顶层运行时绑定

直接写时序脚本中的 `link_design uart` 只绑定了 Tcl 顶层，STA 包装程序仍独立检查环境变量。470.5 ps 补测首次由包装器在 STA 前退出。复用 `bind_runtime` 同时绑定 Tcl、环境与时钟后，以同输入在新目录取得六份三角 STA，旧失败原件保留。[审稿补测](../project_docs/evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md)

## 2026-11-27 — 清洁证据复算按归档字节和命令行环境验收

Windows Git 的自动换行转换会改变已冻结 JSON 的 SHA，即使 Git blob 正确。将这些收据显式设为 `-text`，用启用自动 CRLF 的新归档测试。命令行采用 ASCII 表头，避免 GBK 重定向报错。原 ZIP 的内部索引可被同一次篡改更新，故外层同时固定 ZIP SHA，再检查每个成员。对清洁包和篡改包分别测成功与非零退出。[离线复算脚本](../project_docs/evidence/tcad_v5_revision_20261126/verify_review_evidence.py)

## 2026-11-27 — 由生成调用和裁切复算确认图件来源

示意图的协作日志曾用 `image-generator` 泛称。通过生成调用、输出 JPEG 文件名及 SHA 和主会话的裁切命令建立对应，重新生成与入稿文件相同的 PNG。披露采用实际执行的工具名称。调用记录中对话模型字段无法用于确定图像后端版本。 [图件溯源](../paper/zh/figures/CHANGE_LOG.md)

## 2026-11-27 — 重放 STA 应绑定包装器实际读取的 ODB

R3-1 的公开 STA 收据含门级网表指纹，原包装器在运行时以同名 ODB 替换 Tcl 的网表加载命令。重放从参考资格和候选物理收据取得 ODB 指纹，同时绑定 SPEF、库视图、SDC 和原二进制。只用网表重建可能改变寄生及天线二极管语义。独立目录的重放在原件比对中保留逐角完整报告。 [R3-1 异址重放](../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#r3-1-冻结-uart-端点的异址-sta-重放)

## 2026-11-27 — 最小化 EDA 环境需验证持久 ABC 的交互协议

一次私有环境的 RTL 综合生成了 BLIF，父 Yosys 却未收到可识别的结束序列。固定 Yosys 和长临时路径的小网表中，缺 `TERM` 时复现停滞，加入 `TERM=xterm-256color` 后正常导出；生产复跑在相同配置下通过。输入清单的版本应在文件写入结束并成功校验后采集摘要。 [隔离重建](../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#从独立输入副本重建-40-ns-处理器参考) · [Yosys 固定源码](https://github.com/YosysHQ/yosys/blob/72b0054f0/passes/techmap/abc.cc#L1097-L1168)

## 2026-11-27 — 分别记录验收、产物读取与进程返回

处理器两臂用独立 cgroup 计量搜索 CPU 和作业内存高水位，另由 scope 外的读者观察原子进度文件，读完四项物理/网表产物并验 SHA 后记时。独立轮询会先观察到停止快照或先观察到外层返回。后处理分别核原验收时刻与观测区间，按原件保留两种顺序。 [V4 补测](../project_docs/evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#40-ns-处理器配对复跑的进程树与下游读取)
