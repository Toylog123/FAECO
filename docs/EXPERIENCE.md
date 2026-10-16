# 开发经验库（踩坑记录）

> 解决问题后当天登记。历史坑位自 work_log 摘录高频项，完整记录见 `project_docs/LOGS.md`。

## 2026-10-16 字节SHA钉定的新证据须防Git换行转换

本次新QA/B17proof/v6-v8/Cprime-v3包由root加.gitattributes -text，防core.autocrlf检出后SHA变化；仅新包、不重写旧证据。提交前仍须核index blob与working raw逐字节一致，属性本身不能替代该检查。当前校验由root执行中，不先称通过。

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
