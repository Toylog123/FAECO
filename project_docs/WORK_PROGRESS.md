# 当前进度：r22已恢复（2026-10-16）

## 2026-10-16 — r22恢复推进（当前权威）

用户“继续”覆盖10-14暂停。主线确认恢复起点main clean/HEAD `781c031`，已推送；记录员已实读K1–K6审查和历史correctness报告，保留原失败v1及历史暂停。当前执行K1–K6修复与反驳性验证；旧667回归不充当当前版本通过。

| 任务 | 当前状态 | 证据门/下一步 |
|---|---|---|
| K1–K6源码与库模型/解析修复 | 完整v5已835pass/4skip/156subtests，166SHA稳定/PYTHONUTF8=1，阶段commit/pin待 | 复用已归档最小反例，保持物理实例口径；修后整套回归、独立复审 |
| 当前版本source pin与C′ v2 | pending，依赖修复验收 | 新pin/新目录；两电路九臂18项pilot全通过后才扩72 |
| A/B/D/C历史科学证据恢复 | A6真实pass且三态交集空，B2/B3三态/D/C及稿图待 | A六确切候选证明；D同臂同输入整族；C完整核查/受影响矩阵，不跨族拼接 |
| 中英文稿、图表、投稿材料 | pending，依赖科学闭合 | 一致回填与最终排版/声明确认 |

### 当前完整v5已通过，记录冻结供阶段commit（LOG-20261016-20）

记录员实际读取full_regression_v5.json/.xml/.log：835passed/4skipped/156subtests，147.00s，wrapper152.781s/exit0；166个code/tests Python before/after SHA一致、source_stable=true，environment_overrides PYTHONUTF8=1。JUnit0fail/0error；这是当前第二批实现的完整回归通过，不升级为科学证据或四态支持闭合。

记录员同步后停止写入，供主线stage/commit/push；实际新commit/pin待主线完成后登记。下一阶段：新pin正式9控制（3正确pass、3故意错误fail、2unsupported、1input_error）、B2新模型proof绑定可重复X identity certificate、C′v3先实际mapped复查后18pilot→72、D56真实CLI预飞已56/56但14pilot待。所有正式STA/pilot尚未启动，v2只注册禁执行、原件保留；A6真实proof/三态交集空保留，B3/D/C与稿图仍待。

OI039临时unsupported能力门仅防止二态工具伪pass，准确writer保留；显式四态编码为支持恢复路径，真实三态语义支持仍open。

### D56真实CLI只读预飞已过（LOG-20261016-19）

已实读D56_ACTUAL_CLI_PREFLIGHT.json：真实run_outerloop_real_wns.parse_args解析全部56 argv，与历史expected resolved_args逐字段比较，56/56 mismatches=[]、passed/source_stable=true、eda_executed=false。脚本scratch/check_d56_actual_cli.py（SHA91af68ae…）待归档；这是内存预飞，不是D56真实重跑。生产/测试仍冻结，v5结果待；无STA。

### 完整v4编码失败原件保留；显式全进程UTF8的v5已运行（LOG-20261016-18）

实读v4 JSON/log：832passed/3failed/4skipped/5warnings/156subtests，148.38s、wrapper152.968s/exit1，166源码SHA稳定；3失败均父UTF8/子CP936环境，源码未变。v5 JSON实际status=running、166beforeSHA，environment_overrides={PYTHONUTF8:1}明确传全children；尚无最终结果，不填通过。

phase2_tdd/已从scratch晋级58文件，记录员逐条实际重算source/target SHA与ARCHIVE_MANIFEST.json全58/58一致。失败红测、诊断、局部绿测原件均保留。

B2 X边界两agent只读审查由主线通报：core7个显式X赋值无cell/alias消费者，2个直连恒X主输出同句/宽/roles；mul无X。已实读b2_explicit_x_refs中的7/0与空消费者，PO细节及可重复identity checker待绑定正式B2proof。不能将二态SAT认证为一般四态证明；B2尚未新proof。等v5完整通过后才阶段commit/push与新pin，暂无STA/pilot。

### 拒绝门验证与v4环境失败发现历史（LOG-20261016-17）

已实读tristate_guard_verification/verification.json：原Zvs0/1精确历史输入均unsupported，command=None/runtime0、source_stable=true、passed=true。该门验证拒绝不可靠二态证明器，未启动外部工具、不是四态证明，OI039支持恢复路径仍open。

CLI真实fixture补齐后test_outerloop_cli全文件9pass/0.71s、wrapper6exit0，已冻结。完整v4实际running、166beforeSHA；主线监测3F为-Xutf8仅作用父进程、子CLI仍CP936，独立utf8_environment_red.log复现3fail+4warnings/0.97s，设置PYTHONUTF8=1传递全进程后green3pass/0.82s，记录员均已实读。源码未改，只在scratch harness修环境；等v4完整结束保留，再v5显式记录PYTHONUTF8=1，不提前填v4最终数/整体通过。

暂无STA/pilot；A6真实证明保留，B2/B3/D/C科学恢复与C′新pin/v3仍待。根AGENTS/README/.codex由主线同步，记录员只改责任文档。

### 完整v3失败归因与临时能力门历史（LOG-20261016-16）

记录员实读v3 JSON/JUnit/原log：822passed/2failed/4skipped/156subtests，pytest144.12s，wrapper147.735s/exit1；165源码before/after SHA一致。两失败均CLI旧测试fixture缺dfrtp真实模型与RESET_B输入，F1/F2正确拒、candidate STA未启动，电气lazy baseline为None。parser已独立红复现，拟仅补真实fixture、保留assert，不改门放行非法输入。

原log含CP936混编码，harness结束读取utf8展示报UnicodeDecodeError，但原JSON/JUnit与日志完整保留；记录员按gb18030错误替换读取原bytes核实计数，不改写原日志。后续python -Xutf8避免展示解码混淆，不能把展示失败说成整个回归没有有效结果。

主线二态cut组合方案被两个独立反例（含Z^Z vs0）推翻，不实施。改为当前二态证明器对actual三态cell/显式Z/switch给structured unsupported非pass，准确writer保留；这是临时能力门，三态真实语义支持仍open，恢复路径为显式四态编码。sec_domain_red5fail→green含scope16pass/9.57s，扩展domain11pass/0.28s已实读，完整v4未启动。

计划输入审计TRISTATE_MATRIX_SCOPE_CHECK已实读：B2四raw、D56保留输入（8独有SHA）与8共享canonical raw均无已用三态；v2八prospective mapped不存在，判unknown而非空交集。不能把已存在raw的二态事实冒充未来mapped/candidate全语义验收。A6真实pass/三态交集空保留，无STA/pilot。

### 真三态诊断与v3运行监测历史（LOG-20261016-15）

记录员已实读tristate_tool_diagnostic/diagnostic.json：dirty diagnostic_only=true、timing_runs=0、5组均matches（2pass/2fail/1input_error），source_stable=true；主线实际包装20s/exit0。更强反例tristate_z_diagnostic/diagnostic.json同样source_stable=true、timing_runs=0，但Zvs常量0预期fail实际pass（return0），Zvs常量1 fail符合，整体passed=false；主线包装11s/exit1。

归因当前Yosys默认流程的Z塌缩，前5组控制不能认证该工具对Z的soundness。OI-039追加真实工具可靠性阻断，不能因前组matches便关闭。主线和两领域转只读设计composition boundary proof，暂不改生产，不以“不能支持”直接放弃真实语义目标。

完整full_regression_v3.json实读status=running、165项beforeSHA；stdout至少2个F、首读至59%仍在推进，尚无最终计数/归因，不预填数字。源码继续冻结。A6真实proof且三态交集空保持；B2/新pin/C′v3 pilot仍待，v2仅注册禁执行，无STA。

### 第二批冻结与诊断准备历史（LOG-20261016-14）

主线确认第二批production/tests已冻结，准备先做真实三态SEC正负诊断（明确dirty工作区诊断、非STA），再完整v3回归；此刻不预填诊断/整体结果。记录员实读限定日志：Liberty13passed/1.59s、RW相关174passed/39.50s，后缀反相修后最新相关187passed/44.27s（wrapper46/exit0）；最终输入门24passed/9.76s、D复验工具20passed/8.42s。各限定范围不同不合计当整套。

postfix_all13_probe.json为真实writer内存边界导出13三态/52二进制输入行静态语义检查，eda_executed=false，不代替真实工具Z能力。A TRISTATE_IMPACT_CHECK.json已实读：六实际证明pair的used三态交集逐一为空，保留A6真实证明，不再留下“交集待核”的虚假缺口；旧runtime身份边界及稿图回填另保留。

B2仍待新模型正式proof，B3历史缺TE_B与D/C需各自恢复；C′v2仅注册禁执行、原manifest不改，要新pin/v3。暂无STA/pilot；真三态诊断与新整套即将执行，结果待实际产物。

### 三态限定独立复核与后缀反相发现历史（LOG-20261016-13）

记录员主动实读TRISTATE_INDEPENDENT_REVIEW.md：只读其它作者的logic_rewrite与batch final_sec接线，进程内probe timeout120s、16s/exit0、5来源SHA前后一致。联合data/enable映射保留正确共享角色/重命名、拒绝角色或极性错误；actual Liberty解析13个three_state，clkinv不再选三态目标、einvn不选普通inverter。batch在工具前拒gold/gate/helper缺TE_B/普通输入/未知SKY，合法对象仅到被sentinel拦截的subprocess边界，未新启动EDA。

同报告明确作者自审发现4个einvp类实际使用后缀反相(TE')，当前RW writer只字符串替换生成非法Verilog；此不是独立认证通过的一部分，主线获报后另开TDD，仍须完整13三态导出修复/新冻结。不能用上述限定probe代替writer全验收、工具对Z的真实正负控制或新整套。

B审计README已落盘且记录员实读，确认23未见本次used-model defect/5有缺口，以及28旧日志缺runtime模型SHA的边界；OI-038/039未关闭。v2仍仅dryrun、不执行，新pin/v3/STA仍待。

### 新三态/必需输入语义缺口，先修复再重开门（LOG-20261016-12）

记录员实际读取r22_b_model_audit_20261016/audit.json：旧28个完整proof对象绑定仍真，但23未见本次used-model defect、5有实际模型缺口（b09/b20/b21与两Pico），不能再将26其它统称完整真实Lib语义。实际b09/b20/b21 final和SEC gate的einvn_1/_2漏TE_B；真实Lib三态条件(TE_B)，旧模型及8192193新初版writer均忽略three_state。普通clkinv因只function匹配可能被选为三态einvn；这证明缺连接/模型缺口，尚非新的功能不等价证明。OI-039 open。

当前按parser完整pin block/three_state metadata与候选联合语义，models完整RW模型/F1/F2必需输入和ABC显式不支持边界，主线batch最终SEC输入完整性门分别修复。8192193的757完整回归和6控制通过仍是真实历史，但不覆盖此新反证；新生产源码需新整体回归/commit/source pin。

C′v2只注册过72配置，无mapping/STA，标为已知缺陷pin不可执行；原manifest不改，后续另建v3目录。A6保留为8192193模型下真实pass，usedtypes仍需核查是否涉及新三态边界；不立即推翻其结果，也不外推所有科学结论。B2尚未重证，暂无STA/pilot。

### 模型真SEC控制6/6符合；A六实际接受对象新证明已过（LOG-20261016-11）

已实读sec_controls/controls.json与run.log：6组expected statuses全部匹配（3正确pass/3故意错误fail，含edfxtp DE保持与反相enable），source_stable=true、wrapper15s/exit0。该门验证多输出/顺序模型控制，不是新时序收益。

A正式新目录r22_a_sec_20261016_frozen/input_manifest.json锁8192193、source_tree_clean=true、6对象/输入/库/源码SHA；实际proof_run.log已六pass，wrapper21s/exit0（1500s包装/每case180s）。逐个receipt明确s382/s420/s641/s713/s832/s953的实际原A mapped→accepted fixed对象、真实Yosys SEC返回0。s713原fixed为16561B/LF，final_raw为17585B/1024CRLF；记录员实际比对通用换行后逐字一致，解释原字节SHA3c982ac0…与proof raw5fe19204…，不是换候选。历史runtime输入hash不因本次证明补造，稿图科学回填仍待。

C′正式v2 dryrun manifest已实读：experiments/20261016_r22_cut_ablation_v2/manifest.json，pin8192193、44source、九臂八电路72commands，尚无mapping/STA executed。原v1未动，18pilot待主线汇合A与模型审计后启动。B2尚未重证，OI-038及D/C科学恢复仍待；无STA。

### 阶段commit与模型SEC启动历史（LOG-20261016-10）

主线实际commit+push `8192193`（82files），记录员只读实查.git两main refs均为完整 `81921932d9348408e237edfa13a42257a43007f2`；主线复核757被测162文件SHA与提交前逐项匹配、提交后工作区/code干净。记录员随后获准恢复写docs，不操作Git/源码。原失败JUnit的traceback空白保真，diff检查对代码/docs通过时排除verbatim日志与该原失败XML，不是放宽源码检查。

真SEC正负控制已实际启动：sec_controls_run.log显示timeout1200s执行sec_model_controls.py，逐case180s。controls.json锁HEAD8192193、Lib SHA ec0e1067…、source manifest及6组配置；记录员首读status=registered，已有tie正确双输出pass、错接HI/LO fail，均符合预期；全6尚未核齐。其余为fa手写真值/保持SUM故意错误COUT、edfxtp正确DE保持/故意反相DE。此为真实独立SEC工具运行，无STA；A6/B2/pilot仍未开始，科学结果未闭合。

### 当前完整修复版本已通过，B两Pico旧模型需补证（LOG-20261016-09）

记录员实读full_regression_v2.log/.json：757passed、4skipped、156subtests，102.50s，wrapper107s/exit0；162个code Python文件before/after SHA一致、source_stable=true。可确认该当前修复对象整套通过；首失败三证据保留，不能将该实现验收升级为科学证据已闭合。

主线新B模型审计通报：两Pico归档proof实际使用edfxtp_1，旧model仅assign Q=IQ而IQ无driver/always；dfxtp_1有always。审计细节正由models补写，记录员待实读正式新报告；先登记OI-038为open。B28实际final/gold对象绑定仍成立，但26其它对象与这2个真实FF语义缺口分开；不据此判定电路功能不等价。后续在新库模型/source pin下对这2实际final补独立SEC，旧证据不改，与A6分别绑定。

主线准备阶段commit+pin，记录员此轮同步后停止写入，等待实际Git/SEC启动消息。正式正负模型SEC控制、A6、B2与v2 pilot尚未执行；科学A/B/C/D缺口仍开放。

### 声明兼容修复与完整v2启动历史（LOG-20261016-08）

记录员已实读validation_wire_regroup_red.log（7failed/8passed/27deselected）及green.log：相关五文件145passed/22.28s，180s包装26s/exit0。原sole failure通过，新增15参数例保留已有net宽度/signedness/声明次数约束，支持合法声明分组/合并/新增线；不是修改旧fixture凑过。

production/tests再次冻结，完整v2实际session54033运行，full_regression_v2.json读为running并保存162项beforeSHA，stdout/JUnit独立前缀不覆盖首失败；300s包装/主线330s外超时。首读stdout仍在前段，不能据此称通过。真实SEC/EDA尚未开始。

证据目录sec_model_controls.py准备正式正负SEC控制：conb双输出及错接HI/LO；fa手写真值函数与保持SUM但故意错误COUT。只在整套通过、commit/模型源码pin之后执行。D56配置恢复与C未知边界为只读设计；B28已有final/gold对象绑定保留，新增实际历史模型完整性审计，不能把新writer缺陷直接外推为旧B无效，也不能未查旧模型便断言其完整。

### 首完整回归失败归因历史（LOG-20261016-07）

已实际读取full_regression.log/.json：741passed、1failed、4skipped、156subtests，108.20s，wrapper112s/exit1；before/after SHA一致、source_stable=true。唯一失败为test_sol_review_residuals.py::test_strict_buffer_equivalence_accepts_verified_buffer_chain_and_rejects_wrong_buffer，合法B将wire N;扩为wire N,N_BUF;，新_non_rgb_structure以整条声明Counter比较而误判原N删除。

归因为新实现的合法声明重组兼容性错误，不是测试对象漂移，也不改旧fixture凑过。models仅修该函数，须保留已有net宽度/signedness、允许分组合并与新增线；先专属红→绿，再冻结新版整体回归。旧full_regression.{json,log,xml}原件保留，新全回归用full_regression_v2前缀。此刻完整门仍失败，尚未任何真实SEC/EDA；不新pin放行pilot。

### 完整回归启动与监测历史（LOG-20261016-06）

正式完整回归session63511已运行：Git Bash timeout300s，`.venv/Scripts/python.exe -m pytest code/tests -q --junitxml=project_docs/evidence/r22_correctness_20261016/full_regression.xml`。`full_regression.json`记录起始HEAD781c031、运行前源码/fixture SHA及status=running；stdout为full_regression.log，结束后再核验完整JUnit/afterSHA。记录员首次查看尾部已至85%并见1个F，尚无最终计数/归因，已立即通知主线，不能称全过。

独立最终冻结probe已实读INTEGRATION_REVIEW最后一节：7生产文件before/after SHA稳定，IR source/metadata/alias/secondary boundary/split交集及S错误top、SEC假module/helper不变控制符合；约5s/exit0。此为独立构造探针，不代替完整回归。真实A六对象SEC/EDA尚未启动；D/C只读配置恢复并行，不修改被测源码。

### 集成复审反例汇合与冻结（LOG-20261016-05）

记录员实读integration_review_red.log（3failed/6passed：无输入source、assign别名root、cone外secondary消费者）、split_external_red.log（1failed：BO/internal重叠）以及scope_final_green5.log（最新限定68passed+1subtest/3.71s，120s包装exit0）。主线分别修复物理driver/source、alias root、cone外边界及split传播/内部互斥；lib metadata实际属性为lib，原cells路径反例已加入并修。旧c17断言漏N11/N16外部消费者，主线实查原网表后更新期待，未放宽边界检查。

A证明工具test_r22_a_sec_recovery为9passed/0.97s；dry-run六对象、52个输入文件及44个源码SHA已实际查看input_manifest.json，eda_executed=false，source_tree_clean=false（工作区源码快照，不冒称已提交新pin）。s713主pair选原A mapped→实际fixed，counterpart baseline差异由主pair覆盖，不能只证明带tie变化后的baseline→fixed。

主线声明所有production/tests已冻结，当前准备整体回归；预定完整stdout/JUnit/被测SHA保存到 `project_docs/evidence/r22_correctness_20261016/`。A尚未实际执行六对象证明，v2/EDA尚未开始。已有INTEGRATION_REVIEW保留各轮反例/源码身份，最终全门与独立放行仍待主线实际结果。

### 本轮已实读的限定验证（LOG-20261016-04）

- K2 parser相关三文件：`scratch/r22_resume_20261016/k2_parser_final_green.log`，35 passed/1.03s，120s包装exit0。
- 模型/校验相关四文件：`validation_models_final_related.log`，69 passed/10.03s，180s包装exit0。
- 主线scope反例先4 failed（次输出依赖/物理节点、CLI同名helper D、S刷新失败仍提交）；修复后独立SEC注释假module反例另1 failed，随后使用公共module_spans。最终相关七文件 `scope_final_green.log` 为63 passed、1 subtest/3.85s，120s包装exit0；红测保留在scope_red.log/sec_module_red.log。
- 主线说明deep-signature旧fixture把同名GROOT放循环内造成实际重复，改为循环外，保留深链含义，不放宽production唯一性门。parser/models源码已冻结，领域转A六证明对象工具准备与只读集成复审；尚未整体回归/EDA。

以上是各限定范围结果，不相加冒充完整回归，不宣称K1–K6/科学证据全闭合。新恢复计划：`project_docs/planning/R22_CORRECTNESS_RESUME_PLAN_20261016.md`；当前后续为源码/fixture稳定后完整回归、独立复审及新pin。

## 历史进度

# Work Progress

> r21 Git收口：实现提交 `e592bfd`、SVG导出规范化提交 `483b5e9` 已成功推送 `origin/main`（2026-10-14）。本轮审稿/配图/计数修复已完成，后续只处理保留的未决项；下文Git待办措辞为推送前记录。

本文件按**倒序**记录每一轮工作（最新在上）。完整正序日志见 `LOGS.md`。

## 2026-10-14 恢复机制证据与投稿推进（r22_20261014，进行中）

- **新授权**：用户在剩余事项报告后明确“继续推进吧那就”；本轮恢复 OI-031 历史配置、OI-034 计数审计，并推进同运行器的新族双割/cost 消融，之后处理英文 elsarticle、投稿材料、Word 必要性与最终排版。旧消融暂缓与 r21“不新 EDA”仅作历史安排。
- **起始实查**：main/HEAD/origin-main `46ede94`，clean；r21 PDF 793394B、`c65169b7…`，12页/7图14表。未见既有r22归档。
- **当前阶段（LOG-20261014-23）**：正式C′首pilot两W0真实运行、最终独立SEC拦截，batch58s/exit1；原目录完整保留，无有效新族结果、其它臂未启动。OI-035跨模块B插入与OI-036局部namespace门伪pass/历史correctness影响修复中；须新commit/pin/v2与当前版本全回归后完整重跑受影响矩阵。下列先前准备节点按当时状态保留。
- **独立设计评审**：`R22_ABLATION_DESIGN_REVIEW_20261014.md` 已落盘并实读；仅一次六门静态探针实际执行，登记PROBE-R22-LEGACY-GATING。新源政策/2×2/强反证/12项探针均是待主线审查的建议，未跑正式EDA、不据此声称收益（LOG-20261014-12）。
- **正式计划与档案恢复**：C′九臂×八电路矩阵已在正式计划预锁，开跑revision/输入/命令仍待登记；历史审计只读51s/exit0，b17从独有报告恢复104、ITC-99可识别候选STA结果合计2994。C完整历史argv/revision仍缺，s382 v3不自动借入；OID关闭范围待主线裁定，正式EDA未跑（LOG-20261014-13）。
- **主线已确认**：起始回归538 passed/4 skipped/156 subtests（pytest111.16s、包装113s/exit0）；CLI20项RED→GREEN，25 passed/4 deselected。仅CLI门通过、核心实现未完成。OI-031完整复现缺口仍open；OI-034按B/D计数已闭合+C不可识别历史范围细分，正式EDA未启动（LOG-20261014-14）。
- **核心局部TDD**：candidate_policy先ModuleNotFoundError RED后实施真实Cw/Cc、等权cost1、canonical双来源去重及flow显式分支；与CLI/legacy联合38passed/0.74s。STA launch与汇总子任务仍推进，整体回归/pilot/冻结门尚未完成，无正式EDA（LOG-20261014-15）。
- **批运行与静态反证**：批运行器3fail RED→实现后，与十二candidate静态项联合15passed/0.21s；锁九臂/冷输出/共享映射/SHA及3900s+3930s超时/最终SEC。P2错误预期经真实求解归因，保留tie与退化，不强求阳性。OpenSTA3.1.0已实读，native Yosys环境/版本待校验，无EDA（LOG-20261014-16）。
- **整体验证与后续修复**：首次全回归624/4skip/156subtests（99s，包装102s）；独立review反证批路径/SEC覆盖/伪pass复用/失败调度/timeout后已修，专属91passed/1.13s，需以最终源码再全回归。工具dryrun三版本校验成功、72配置注册但未mapping/STA；英文草稿已并行起步，仅沿r21已证数字（LOG-20261014-17）。
- **最终稳定回归**：第二次629项中1fail因回归中改脚本/fixture造成对象不稳定（628passed/1fail），已停core编辑重启；最终629passed/4skip/156subtests、99.79s（包装102s/exit0）。只认最终源码对象。文档入口同步，阶段源码commit准备，domain最终门待对照；仍无正式EDA/结果（LOG-20261014-18）。
- **阶段快照准备**：domain无生产源码blocking、12静态门仍partial；已补P4/P6 flowstub3passed，P3/P7/P11继续补，不以partial开EDA。b17独立104row/208SHA主线复核通过。代码/历史审计阶段commit准备，记录短暂停写入供stage，不纳入未完成英文稿（LOG-20261014-19）。
- **阶段已提交推送**：28c3c2b、37files，push46ede94→28c3c2b/exit0，HEAD与origin-main实查一致；代码/历史审计固化，不含英文未成稿。记录恢复；最后静态P3/P7/P11/K1/2与source/config锁待完成，formalEDA未启动（LOG-20261014-20）。
- **正式dryrun锁清单**：experiments/20261014_r22_cut_ablation/manifest已锁git28c3c2b、production/8输入/LIB SHA及72commands、三工具；没有mapping/STA。B18独立复核再证2890，+b17得到2994，母稿只补来源说明，旧数据不改；新tex/PDF验收待编译（LOG-20261014-21）。
- **启动门与母稿验收**：最后静态12+flow3通过，全套644passed/4skip/156subtests、99.14s（包装102 exit0），production/LIB匹配28c3c2b清单。中文2994来源句编译12页/全0/21refs、变更p8目视与回读通过，三PDF e27eaf3a…/793545B一致；旧作者版先备份。英文52KB/27页首draft，视觉/声明仍待核；准备pilot，尚无正式EDA（LOG-20261014-22）。
- **真实pilot与归因**：session66717按正式manifest只启s27/s382两W0，runner47/48s exit0，SEC helper变化正确拦截后batch58s exit1；旧B插首helperendmodule、F1/F2全文件合并namespace伪pass，修复分工已启动。新STA12/11、eval14/13、缓存0/0，各2前置F1拒绝，不由差额猜缓存；中间WNS不计有效收益。后加JOINT on/off静态13项联合39passed/0.93s独立于旧644collection，后续修复不能沿用旧source门（LOG-20261014-23）。
- **历史correctness独立报告已到（待主线裁定）**：B完整SEC绑定28有效、b17部分/regs N/A仍分层；A仅2 exact对象可复用证明、6缺绑定；D38/40与k1 14/16终点结构invalid，C代表9/12 invalid、3未知不外推。报告/JSON/输入/脚本已回读现算SHA，不运行EDA。未知不等失败、计数可核不等候选合法；原数据保留，论文/复验范围等待主线复核（LOG-20261014-24）。

| 工作 | 状态与证据门 |
|---|---|
| OI-031历史配置恢复 | 现存档案审计完成；完整flags/argv/revision身份缺口保留 |
| OI-034计数语义审计 | B/D来源闭合；C精确执行不可识别的历史限制已明确 |
| 双割/cost新族 | 首真实pilot被独立SEC拦；原证据保留，OI-035/036修复、新pin/v2/当前版整体回归后完整重跑 |
| 局部正确性与历史影响 | 跨模块B插入和namespace伪pass已确认；独立历史审计已到，B28完整绑定保留、A/D/C分层，主线复核裁定待完成 |
| 英文elsarticle/投稿材料 | 并行草稿；只绑定r21已验证母稿，不使用未出r22数据 |
| Word必要性与最终排版 | 后续评估；尚未转排，旧件仍需口径核对 |

## 2026-10-14 论文审稿与配图修订（r21_20261014，本轮完成）

- **完成内容**：五视角模拟审稿与独立复核；重画图 1/2，新增图 4 统一结果、图 5 同族 D 真实测量 B(k)、图 6 物理收益保持、图 7 S 深度/WNS 分类；图 3 沿用。正文同步必要来源说明、图注与引用。
- **审稿结论**：Major Revision，见 `paper/zh/review_rounds/r21_20261014/editorial_decision.md`。族 C 机制归因/纯排序误读、接受提交差异、b17 两批次分母已披露；OI-030 双割独立因果证据、OI-031 逐臂配置与历史复现档案仍开放。
- **计数修复**：D 从原始 trials 排除缓存/前置拒绝重建曲线，新 STA 为 Fixed 1947、EMA 2003、随机三种子 2439/2476/2527（均值 2480.7）；旧 4146/4883/5624 保留为评估记录。B 的 3363/664/104 改称评估记录；18 实例可确认新 STA 2890，b17 旧 schema 无来源，真实测量数未知。D 是已有台账重算的新展示数字，未运行 EDA。
- **验收已通过**：12 页、7 图/14 表、引用 21/21；Error/hbox/vbox/未定义引用均零。旧 balance 的末页 0.8534 pt 溢出改用 `flushend[noshrink,nospread]` 消除，未缩字体/行距/删内容。验收 PDF `c65169b7…`、tex `d36812c8…`，实查与 `build_qa.json` 相同；逐页视觉、字形审计与40运行账本审计通过，双PDF和作者版三份字节一致。
- **版本边界**：r21 为工作修订，不冻结 v19；v18 不可变参考保留。旧收益数字不改，成本消融/大规模验证/Word 继续暂缓。

| 收尾/后续 | 状态 |
|---|---|
| 本轮逐页视觉、双 PDF 与作者版同步 | 已完成，三份字节一致 |
| 本轮文档与记录自检 | 已完成 |
| 阶段 commit+push | 待主线执行并另记真实 Git 结果 |
| OI-030/031 机制证据与逐臂配置 | 未闭合，继续保留 |
| OI-034 其他历史族计数/旧 schema 审计 | 未闭合；b17 旧档案的实际数不可识别 |
| OI-021/024/027/028 投稿、Word 与最终版式 | 保持既有待办/暂缓安排 |

## 2026-10-13 学术叙事收敛（r20：13 处改写）：重冻结 v18

- **做了什么**：**用户对作者版(7) = v17 的第五轮通读意见**（非外部审稿、非技术修改、**不增实验**）。用户判断「整体框架已基本正确、主线比之前清晰很多」，本轮**「已经不是『需要重构』，而是『需要最后一次学术叙事收敛』」**；唯一核心 = **Candidate exploration under limited verification budget**，要求让所有章节回答同一问题「如何在有限验证预算下进行有效的预布局 ECO 候选探索」。落地 **13 处叙述层改写**：E1/E2 摘要核心思想句；E3 §1.1 核心问题句替换；E4 §1.3 贡献分层为 2 条贡献 + 平台段落；E5/E6 失效反馈语言弱化（全篇「搜索参数」= 0）；E7 §4.5 标题；E8 §5 结论意义强化；Edel 删 §4.1 边界句。
- **关键结果**：**11 页（与 v17 相同、逐页分布不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??` = 0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；摘要 CN 372→410 汉字、EN 217→241 词。**零数字（词级比对：数字/引用键 0 差异）/ 零实验 / 零代码 / 零参考文献**。
- **重冻结 v18**：tag `v2026-10-13-narrative-convergence-r20` + 论文 tag `faeco-paper-final-20261013i`；`versions/v18/MANIFEST.sha256` 117 条全 OK（相对 v17 恰 3 条变化 = `.tex` + 双副本 PDF）；`BASELINE_INDEX.csv` v17→superseded / v18→active（19 行、恰 1 active）；双副本 PDF `1ebb2864…`（2,610,131 B）。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 **241 词**（逼近 ≤250 上限）+ CN 摘要 **410 汉字** 须按作者指南复核）；OI-024 Word 转排件仍 v6（缺 r8–r20）；**v11 + v12 + v13 + v14 + v15 + v16 + v17 + v18 均未推送**（等用户指令）。

## 2026-10-13 论文定位重构（r19：12 处改写）：重冻结 v17

- **做了什么**：**用户直接指定的「论文定位重构」轮**（非外部审稿、非技术修改、**不增实验**）。用户核心判断：**问题不在技术不足，而在叙事未把「FAECO 为什么重要」讲到最高层次**（「像一个完整的 EDA 工具流程，而不像围绕一个核心科学问题展开的方法论文」）；指令优先级 = ① 强化主线 → ② 首次概念定义 → ③ 强化重要性，并明确「最需要的是论文定位重构，不是技术重构」。落地 **12 处叙述层改写（16 次替换）**：A1–A3 概念定义（§1.1 新增「候选探索」定义段 / 摘要中英四类候选全称 / §1.2 动机链）；B1–B3（§1.1 核心问题句 / §1.3「核心问题 + 三个支撑块」/ §3.3 改标题并拆 3.3.1–3.3.3）；C1–C3（§1.1 首段链条 / 关键挑战句 / §5 结论收束句）；D1–D4（实验定位句 ×4）。
- **关键结果**：**11 页（v16 = 10 页，+1）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??` = 0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；摘要 CN 345→372 汉字、EN 203→217 词。**零数字（词级比对）/ 零实验 / 零代码 / 零参考文献**。
- **★ 页数处理**：第 11 页仅含参考文献尾部 = **孤儿末页**；两道压页实验（删 §3.5 唯一正文 `\FloatBarrier`、图 2 宽度 0.65→0.58`\textwidth`）**均未回收页数且已回退**（后者还使浮动体级联、末页承载更多）；⇒ 增长源于**用户指定新增叙述内容**、非版式缺陷；按纪律**未缩字体/行距、未砍内容**；版式压缩并入 **OI-027**。
- **重冻结 v17**：tag `v2026-10-13-positioning-r19` + 论文 tag `faeco-paper-final-20261013h`；`versions/v17/MANIFEST.sha256` 117 条全 OK（相对 v16 恰 3 条变化 = `.tex` + 双副本 PDF）；`BASELINE_INDEX.csv` v16→superseded / v17→active（18 行、恰 1 active）；双副本 PDF `862ee713…`（2,609,658 B）。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 **217 词** + CN 摘要 **372 汉字** 须按作者指南复核）；OI-024 Word 转排件仍 v6（缺 r8–r19）；**v11 + v12 + v13 + v14 + v15 + v16 + v17 均未推送**（等用户指令）。

## 2026-10-13 图 2 机制图替换（r18：零 .tex 改动）：重冻结 v16

- **做了什么**：**用户直接指定的图件替换轮**（非外部审稿、非技术修改、**不增实验**、**零 `.tex` 改动**）。用户指令「**用这个图片替换图2**」，提供更新版机制图。仅替换图 2 源图 `paper/zh/figures/fig_cut_generation_mechanism_imagegen.png`：旧 1,251,525 B `a3b53e80…` → 新 1,152,805 B `67af5ce4…`（源为剪贴板 JPG，经 `.venv` Pillow 12.3 无损转 PNG）。新图在旧 4 面板（(a)–(d)）基础上**新增「候选融合排序」中间层**（依据 cost(v) + 路径覆盖 + 策略优先级），JOINT 标注改「关键路径**区段**联合」。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；图 2 落点第 5 页渲染正常；图尺寸 **1,254×1,254 不变（1:1）⇒ 版式零位移**。**零数字 / 零实验 / 零代码 / 零参考文献 / 零 `.tex` 改动**。
- **★ 陷阱**：`pdftotext -layout` 内容指纹 **= v15（`c5fa3f26…`）**，纯栅格换图不改文本层 ⇒ **换图类的变更证据 = PDF 字节 SHA + 页面渲染**，不能依赖文本指纹。`figures/` 不在 manifest 覆盖内（OI-025），故 manifest 相对 v15 **恰 2 条 PDF 变化**。
- **重冻结 v16**：tag `v2026-10-13-fig2-update-r18` + 论文 tag `faeco-paper-final-20261013g`；`versions/v16/MANIFEST.sha256` 117 条全 OK；`BASELINE_INDEX.csv` v15→superseded / v16→active（17 行、恰 1 active）；双副本 PDF `05ee4ec0…`（2,604,856 B）。
- **★ 3 项可回退**：沿用原文件名 / JPG→PNG 转码 / 图注未点出「候选融合排序」层（详见 `versions/v16/README.md`）。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 **203 词** + CN 摘要 **345 汉字** 须按作者指南复核）；OI-024 Word 转排件仍 v6（缺 r8–r18）；**v11 + v12 + v13 + v14 + v15 + v16 均未推送**（等用户指令）。

## 2026-10-13 逻辑一致性精修（r17：12 处改写）：重冻结 v15

- **做了什么**：**用户直接指定的逻辑一致性精修轮（claim calibration）**（非外部审稿、非技术修改、**不增实验**）。用户对**作者版(5) = v14** 做**逻辑链专项复审**（自评 **8.5/10**），裁定「已明显不是防御型论文；问题不是'解释太多'，而是少数地方**贡献强度 > 实验支撑一点点**」，指令「**不要再增加实验；下一轮做逻辑一致性精修（claim calibration）：控制 claim 范围；明确模块关系；统一'分析/调整/控制'等词**」。落地 **12 处（`.tex` diffstat 11 行）**：**P0×4**（① 贡献 1「减少候选评估开销」→「减少候选级评估开销」；② §3.3 开头新增「$C_w$ 用于确定候选修改边界，$\mathrm{cost}(v)$ 用于边界内部节点的选择与排序，$C_c$ 用于补充关键路径覆盖」；③ 表 5 表题「搜索参数调整」→「搜索分析动作」；④ §5 结论「主要因素」前加「在本文实验范围内」）+ **P1×2**（⑤/⑥ 摘要末句中/英加强为实验结论）+ **配套×6**（表 5 表头/§3.5/§4.4 统一「搜索分析（动作）」×3、贡献 2 加「依据」、§1.1 与摘要「候选级评估开销」×2）。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `5775eb51…`（61,801 B）、双副本 PDF `b1d6e5a2…`、内容指纹 `c5fa3f26…`（poppler 25.07）。**目标词**：`搜索参数调整` 4→0、`候选评估开销`（无级）3→0、`控制` 12→12。**零数字 / 零实验 / 零代码 / 零参考文献**。
- **三处配套已列明可回退**：E2 措辞适配；E4/E5/E6 随表题统一；E11/E12「候选级评估开销」全篇统一（详见 `versions/v15/README.md`）。
- **重冻结 v15**：tag `v2026-10-13-logic-calibration-r17` + 论文 tag `faeco-paper-final-20261013f`；`versions/v15/MANIFEST.sha256` 117 条全 OK（相对 v14 恰 3 条变化）；`BASELINE_INDEX.csv` v14→superseded / v15→active。
- **★ 回读校验教训**：needle 必须逐字抄自实际改写文本（首版 E10 漏抄致假阴性）；浮动体/参考文献行可把长句切成 ≥3 段 ⇒ 分离匹配须支持 **1..K 行累计 head + 更后某行前缀 tail**。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 **203 词** + CN 摘要 **345 汉字** 须按作者指南复核）；OI-024 Word 转排件仍 v6（缺 r8–r17）；**v11 + v12 + v13 + v14 + v15 均未推送**（等用户指令）。

## 2026-10-13 术语一致性与 claim 强度校准（r16：17 处改写）：重冻结 v14

- **做了什么**：**用户直接指定的术语一致性 + claim 强度校准轮**（非外部审稿、非技术修改、**不增实验**）。用户第三轮通读 v13（作者版(4)）后裁定「已进入最后精修阶段；主要问题已不是'防御性过强'，而是**逻辑层级不够清晰** / 个别表述**略偏强** / 方法贡献与实验贡献**边界需统一**」，明确「**不要再增加实验；最后一轮做术语一致性 + claim 强度校准，重点检查控制、降低、性能边界**」。落地 **17 处**：**P0×3**（① §3.5 标题「搜索控制」→「搜索分析」；② 贡献 1「降低候选验证开销」→「减少候选评估开销」；③ 摘要末句 CN「性能边界」→「影响」+ EN `performance boundaries`→`effects … on search performance`）+ **P1×2**（④ §3.4 特征「控制」→「影响」、表 4 行「控制候选规模」→「约束候选规模偏好」；⑤ §5 结论删逐测试集三元组与 PicoRV32 分母说明）+ **结构×2**（§1.1 新增「问题→方法」映射句、§3.5 新增 `\label{sec:failure_char}`；§3.2 `λ_c` 角色拆句）+ **配套×8**（验证开销→评估开销 ×4、搜索控制→搜索分析 ×3、控制输入→辅助输入、表 5 表注/表头→「搜索参数调整」）。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `9b0bb2ec…`（61,550 B）、双副本 PDF `5c1d060c…`、内容指纹 `f8437a73…`（poppler 25.07）。**目标词**：控制 22→12、性能边界 2→0、验证开销（自述）4→0。**零数字 / 零实验 / 零代码 / 零参考文献**。
- **★ 一处取舍（待用户确认）**：§5 结论按"删 PicoRV32 解释"**删整个逐测试集三元组**（结论不再出现 `2/2`）——因为 `2/2` 若不带分母说明会被读作抹去一个实例（**r12 M2**）；三元组已在摘要/§1.3/§4.3 出现，回退本项一行即可。
- **「控制」的 in/out-of-scope**：保留加权割本体 3 处（min-cut 构造即决定候选边界）、配置开关名 6 处、内存分治 1 处、研究问题 1 处、电路类型 1 处。
- **重冻结 v14**：tag `v2026-10-13-terminology-calibration-r16` + 论文 tag `faeco-paper-final-20261013e`；`versions/v14/MANIFEST.sha256` 117 条全 OK（相对 v13 恰 3 条变化）；`BASELINE_INDEX.csv` v13→superseded / v14→active。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 **209 词**须按作者指南复核上限）；OI-024 Word 转排件仍 v6（缺 r8–r16）；**v11 + v12 + v13 + v14 均未推送**（等用户指令）。

## 2026-10-13 全篇去防御化编辑（r15：正文 11 处语言风格改写）：重冻结 v13

- **做了什么**：**用户直接指定的第二轮语言风格轮**（非外部审稿、非技术修改）。用户在 r14 后按**正式期刊审稿人（Integration / TODAES / TVLSI 方向）视角**再做一次通读，裁定「**这一版技术内容已经比较成熟，但文字风格仍有明显'答辩稿/项目报告'痕迹。最大的问题不是 claim 过强，而是作者过于主动解释审稿人可能的问题，导致主线贡献被稀释**」；指令 = 「论文现在应该从：'证明我没有问题' 转向：'清楚告诉读者我做了什么、发现什么'」，**「剩余工作：不是增加内容。而是：减少解释性文字，提高陈述力度。」** 故 r15 在 r14 基础上做**第二轮全篇去防御化**。**动笔前先与 r14 已清项对账**（`不主张` / `不等同于` / `不单独隔离式 (2)` 均已为 0 ⇒ 不重复）；实测 v12 基线 `不讨论`=1、`未带来额外收益`=1、`留下三个`=1。落地 **11 处语言风格改写（E1–E11）**：E1/E2 摘要末句（中/英）负结果 → 「揭示性能边界」（结构与篇幅不变）；E3 §1.1「留下三个需要量化的问题」→「仍需要解决三个问题」；E4 贡献 1 删 `1.07 vs 0.16\,ns`（数字归实验节）；E5 贡献 2 加「辅助」；E6 §2.3 压成一句；E7 §3.3 删代码级异常解释（**保留 r7-P0 事实「其仍可参与 G/B 候选生成」**）；E8 §3.4 扇出改「被优先选择的概率」；E9 §4.1 改「主要评价指标」；E10 §4.5 改「稳定性」；E11 §5 结论「依据」→「参考」。**`.tex` diffstat 11 insertions / 11 deletions**。
- **★ 三处必要偏离（逐条取证）**：① **E6 压缩后仍保留表 2 引用** —— `tab:baseline_cmp` 全文**仅此一处**被引用，照用户「一句话、不带表引用」字面执行会造出**未引用表**、破硬门 **17/17 引用覆盖**；故写为「…重点比较…三项；**各方法的主要差异见表~2**」。② **E9 保留全文唯一一处「不等同于完整时序收敛」**（用户「保留一次即可」；r14 已在结论与 §4.5 各删一次，若 E9 再删则计数 = 0）。③ **E11 结论补「候选探索策略」**口径（与 v9 起标题一致）。**保留清单**同 r14（r12 M1/M2/M3 表注、PicoRV32 5 处分母说明、NEGATIVE finding 本体、r6 P0「其余无退化」、§3.6/§3.7 口径等）。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `6ce1d51c…`（61,334 B；668 CRLF / 0 bare LF / 0 `\r\r\n`）；双副本 PDF `48854388…`（2,768,538 B）、内容指纹 `55bde9d4…`（poppler 25.07）；tag `v2026-10-13-defensive-purge2-r15` + 论文 tag `faeco-paper-final-20261013d`；`versions/v13/MANIFEST.sha256` 117 条全 OK（相对 v12 恰 3 条变化）。**零数字、零实验、零代码、零参考文献改动**。**v11 + v12 + v13 均尚未推送 origin**（按惯例等指令）。
- **★ 回读校验教训**：**默认与 `-layout` 两种 `pdftotext` 模式在双栏边界都会跳栏** ⇒ 跨栏长片段在被提取文本中**不连续** ⇒ 子串匹配给出**假阴性**（首版脚本误报 4 项 MISSING）。正确做法 = **短片段（≤14 字符）+ 逐行匹配**（任一行命中即算命中）+ **比较前两侧同时剥空白**（`re.sub(r"\s+","",s)`）；修正后 **GONE 10/10 ok、PRESENT 13/13 ok**。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 214 词须按作者指南复核上限）；OI-024 Word 转排件仍 v6（缺 r8–r15 全部改动）须随管线重建；OI-021 AIGC 披露按 Elsevier 政策复核；OI-026 cost 消融**审稿人两轮否决 + 用户暂缓**。

## 2026-10-13 去防御化重构（r14：正文 10 处语言风格改写）：重冻结 v12

- **做了什么**：**用户直接指定的语言风格轮**（非外部审稿、非技术修改）。用户裁定「**论文加入了过多防御性限定语，导致主线贡献被削弱。好的论文不是不断解释'我没有声称什么'，而是直接陈述做了什么、发现什么、适用范围是什么**」；要求下一轮**"去防御化重构"**——表达由**防御模式**（"本文不声称 / 不等同于 / 不作为 / 不直接比较"）转为**陈述模式**（"本文采用 / 本文评估 / 实验显示 / 结果表明 / 该机制用于"）。落地 **10 处语言风格改写**（用户指定 6 处 + 同模式追加 4 处）：E1 §1.3 贡献 2、E2 §2.3 相关工作、E3 §3.4 表 4 表注、E4 §4.1、E5 §4.4 第一组开头、E6 §5 结论、E7 §4.4 第二组、E8 §4.5、E9 §4.2、E10 §4.3.2。**`.tex` diffstat 10 insertions / 10 deletions（恰 10 行替换）**。**摘要一行未动**（用户判定"已有少量限定 → 保持"）。
- **判据 + 保留**：判据 = 是否预先回答假想质疑 / 信息是否已被别处覆盖 / 是否非审稿人（r12）指定落点或既有裁定（OI-014/015、r6 P0）；**三者皆"是"才改**。**保留清单 9 项**（r12 M1/M2/M3 口径表注、PicoRV32 分母说明 5 处、NEGATIVE finding 本体、r6「其余无退化」、§3.4 固定权重声明等）——**防御性限定语 ≠ 证据，不能一刀切删除**。**唯一偏离**：用户「PicoRV32 一次即可」按"不删位置、只去重复"处理（r12 M2 指定落点 5 处）。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `6e2c9ab9…`（61,839 B；668 CRLF / 0 bare LF）；双副本 PDF `43aedfbb…`（2,770,198 B）、内容指纹 `4bc80603…`（poppler 25.07）；tag `v2026-10-13-defensive-purge-r14` + 论文 tag `faeco-paper-final-20261013c`；`versions/v12/MANIFEST.sha256` 117 条全 OK（相对 v11 恰 3 条变化）。**零数字、零实验、零代码、零参考文献改动**。**v11 + v12 均尚未推送 origin**（按惯例等指令）。
- **★ 回读校验教训**：`pdftotext -layout` 在双栏下会把右栏文字串进左栏句中间 ⇒ 回读校验出现"未匹配"**假象**（本轮曾误报 5 处"缺失"）；**回读校验须用按栏阅读顺序抽取（`pdftotext <pdf> -` 不加 `-layout`），`-layout` 仅用于内容指纹**。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 214 词须按作者指南复核上限）；OI-024 Word 转排件仍 v6（缺 r8–r14 全部改动）须随管线重建；OI-021 AIGC 披露按 Elsevier 政策复核；OI-026 cost 消融**审稿人两轮否决 + 用户暂缓**。

## 2026-10-13 大同行入口改写（r13：摘要 + §1.1 引言）：重冻结 v11

- **做了什么**：**用户直接指定的大同行入口改写（摘要 + §1.1）**（非外部审稿），裁定「**摘要应该改**——这是当前版本最值得做的最后一处"非技术性增强"」：现摘要对 EDA 小同行清楚，但对 **Integration 这类期刊的大同行入口偏窄**（缺"为什么 ECO 重要 / 为什么需要这个阶段 / 为什么已有方法不够"）。**改中/英摘要两段 + §1.1 引言首段**，按「**大背景 → 具体问题 → 方法 → 结果 → 意义**」重排：补首句大背景 + 次句 ECO 定位 + 第三句收窄到预布局门级时序 ECO；方法句补「关键路径覆盖割」使中英对称；末句并入"意义"。**`.tex` diffstat 3 insertions / 3 deletions（恰 3 行替换：摘要 CN + 摘要 EN + §1.1 引言首段）**。
- **★ 与用户草案 5 处偏离（逐条取证）**：① 术语「工程变更**优化**」→「工程变更**命令**」（ECO = Engineering Change **Order**；§1.1 正文原文即如此）；② **保留** r12 M2 分母解释句（审稿人 ★★★★ 指定落点）；③ **保留** r6「其余无退化」（P0 边界声明；加入大背景句后更不可删）；④ 去「快速探索」无据修饰；⑤ 末句补"意义"。**遵从用户自我约束**：不写"先进制程"（用"集成电路规模与设计复杂度持续提升"）；摘要仍无第一人称。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `8fccfab0…`（62,936 B；668 CRLF / 0 bare LF）；双副本 PDF `a720829b…`（2,773,302 B）、内容指纹 `65e29b84…`（poppler 25.07）；tag `v2026-10-13-abstract-broaden-r13` + 论文 tag `faeco-paper-final-20261013b`；`versions/v11/MANIFEST.sha256` 117 条全 OK（相对 v10 恰 3 条变化）。**零数字、零实验、零代码改动**。摘要长度：中文 244→**349** 汉字、英文 164→**214** 词（原 JCAD ≤300 字/≤150 词规则随改投失效，新约束记 OI-028 复核）。**v11 尚未推送 origin**（按惯例等指令）。
- **★ 本轮自造事故**：改写脚本 `raw.decode()` 未归一化即 `replace("\n","\r\n")` ⇒ **668 处 `\r\r\n`** ⇒ LuaLaTeX 视为额外换行 ⇒ **83 Errors / 2 Overfull / 11 页**；`count("\r\n")` 与 `count("\n")-count("\r\n")` 无法检出（仍 668/0）。`scratch/fix_r13_eol.py` 修复后全绿。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 214 词须按作者指南复核上限）；OI-024 Word 转排件仍 v6（缺 r8–r13 全部改动）须随管线重建；OI-021 AIGC 披露按 Elsevier 政策复核；OI-026 cost 消融**审稿人两轮否决 + 用户暂缓**。

## 2026-10-13 投稿前一致性 pass（r12）：第五份外部审稿 M1–M5 + 重冻结 v10

- **做了什么**：用户粘贴**第五份外部审稿**（「投稿前最后一轮审稿人视角」，对 v9 / 作者版 10 页；归档 `paper/zh/review_rounds/r12_20261013/`），评分 = 问题价值 9 / 方法完整性 8 / 创新表达 8 / 实验完整性 8 / **证据一致性 7** / Integration 匹配度 8.5；**最大风险 = 可读性风险**（审稿人能否理解「哪个实验验证哪个机制」）。用户裁定 **「不要再加实验。做一次 Submission consistency pass」**（仅 M1–M5）。落地：**M1** 表 5 ITC-99 行 SEC `19/19`→`18/19` + 表注声明拆分口径（正文自始 28/29 = 8+18+2，表 5 是唯一漏改处）；**M2** PicoRV32 `2/3`→`2/2` + 分母解释（摘要 CN/EN、§4.3、结论、表 5 共 5 处）；**M3** 表 11 表注补「**两个 STA 计数口径不同**」；**M4** 贡献 1 弱化 `1.07 ns` ↔ 加权割绑定；**M5** §3.4 正文 ×3 + 表 4 行 ×3 措辞降调；另按审稿人「问题 2」§4.4 开头补「第一组不单独隔离式 (2) 各特征项」句。**`.tex` diffstat 15 ins / 15 del（15 处替换）**。
- **关键结果（本轮最重要取证 M3）**：**论文存在两个不同的 STA 计数器** —— `state.budget.sta_used`（`search_state.py:254` `reserve_budget`；检查点 `flow.py:591`）为**每轮迭代预约、迭代边界判顶**的预约计数（逐电路 ≤500，**random 三种子在 s420/s641 触顶** `stop_reason=sta_budget`）；`n_candidate_sta_runs`（`run_outerloop_real_wns.py:437` = `len(trials)`）为**候选级 STA 测量次数**（论文口径，逐电路最高 1321）⇒ 表 11 的 **4146/4883/5624 不受 500×8 约束、数字无需更正**。**质量门**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `c5828999…`（668 CRLF / 0 bare LF）；双副本 PDF `4ef380f7…`、内容指纹 `c7b4d807…`（poppler 25.07）；tag `v2026-10-12-pre-submission-consistency-r12` + 论文 tag `faeco-paper-final-20261013`；`versions/v10/MANIFEST.sha256` 117 条全 OK（相对 v9 恰 3 条变化）。**零数字、零实验、零代码改动**（`19/19→18/19`、`2/3→2/2` 属口径统一）。**已推送 origin（2026-10-13，用户指令）**：`main` = `origin/main` = `b1403d9`，v10 双 tag 已上远端。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料）；OI-024 Word 转排件仍为 v6 版（缺 r8–r12 全部改动）须随管线重建；OI-021 AIGC 披露改按 Elsevier 政策复核；OI-026 cost 消融**审稿人再次否决 + 用户暂缓**（非投稿前置条件）。


## 2026-10-12 投稿前精修轮（r11）：标题 / 摘要 / 贡献定位 / 术语与语言风险 + 重冻结 v9

> ⚠ 说明：r8/r9（v7）、r10（v8）两轮未在本文件登记，详见 `LOGS.md`（LOG-20261012-01~04）与 `CURRENT_RUN_HANDOFF.md`。本节从 v9 起恢复登记。

- **做了什么**：用户提供「投稿前精修」六阶段方案，经取证核验后裁定三项（① 中英标题定稿；② cost 消融暂缓；③ Step 1 立即执行）。落地 **7 组改动**：中/英标题定稿（`Candidate Exploration and Failure Characterization…` / 「面向预布局门级时序 ECO 的候选探索与失效刻画」）+ 摘要 CN/EN 重写 + §1.3 贡献 1/2 重写（贡献 3 保留）+ 术语统一（失效归因→失效刻画、结构化排序→候选排序 ×7）+ 结论末句改写（不留"未取得独立收益"式收尾）+ §2.2 比较焦点句 + 3 处语言风险修正；**主稿文件随标题改名**（`.tex` + 双副本 `.pdf`，同步 live pointer 文件；历史记录保留旧名）；新增 `.gitattributes` 强制 `versions/*/MANIFEST.sha256` 为 LF。
- **关键结果**：**10 页 / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox**；`??`=0；表/图引用覆盖 **17/17**；浮动体编号阅读顺序 1..14 / 1..3；`.tex` `22de39a0…`（668 CRLF / 0 bare LF）；双副本 PDF 字节 `f642e533…`、内容指纹 `3832eeb2…`（poppler 25.07）；tag `v2026-10-12-submission-polish-r11` + 论文 tag `faeco-paper-final-20261012c`（= `e00315a` **终态**；r11 收尾时已用 `git tag -f` 由 `daba5ab` 重指）；`versions/v9/MANIFEST.sha256` 117 条全 OK（相对 v8 恰 3 条变化）。**零数字、零实验、零代码改动**（纯文字与定位）。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料）；OI-024 Word 转排件仍为 v6 版须随管线重建；OI-021 AIGC 披露改按 Elsevier 政策复核；OI-026 cost 消融**暂缓**。

## 2026-10-09 文字专项审稿全量落地轮（r7）：重冻结 v6 + 末页孤儿修复 + Word 稿重建

- **做了什么**：用户提供外部**文字专项审稿**（`paper/zh/review_rounds/r7_20261009/comments.md`）并授权全部执行。① 逐项核验后经用户拍板 4 项（摘要方向 / A\* 披露 / 执行范围 / §4.6 口径）；② 一次性落地 **P0×5 + P1×6 + P2×3 + 术语统一**（`.tex` 共 60+ 处替换，逐处唯一性校验，全程保持纯 CRLF）；③ 摘要按审稿方向重写（中 228 字 / 英 148 词）；④ 修复文字收敛引入的**末页孤儿**（删正文 10 处 `\FloatBarrier` + 去重精简 7 处 → 9→8 页）；⑤ 重冻结 v6 + Word 转排稿重建（并修正 b 稿摘要漏同步的管线缺陷）；⑥ 台账/交接同步。
- **关键结果**：**8 页 / 0 Error / 0 Overfull / 0 Underfull**；`??`=0；`\bibitem`↔`\cite` 14/14 且编号按首次引用顺序；字节 SHA `09197e5f…`（双副本一致）、内容指纹 `88b03403…`（poppler 25.07）；tag `v2026-10-09-text-review` + 论文 tag `faeco-paper-final-20261009c`；`versions/v6/MANIFEST.sha256` 117 条全 OK。**零数字、零实验改动**（仅 §4.6 主张强度下调）。
- **下一步**：投稿手工/流程项（MathType 批量转换、黄色占位替换、图 2 通栏、终稿 PDF；⚠ OI-021 AIGC 披露）；Word 引擎导出的 PDF 若由用户在本机生成，须回填 `T20_SUBMISSION_PACKAGE.md` §3 的两处新哈希。

## 2026-10-09 摘要可读性改写轮：去术语 + 重冻结 v5 + Word 稿再重建

- **做了什么**：用户反馈"摘要太多技术要点、难让大同行看懂"并授权改写。**摘要两段 + §1.1 引言首段**：① 删 R/G/B/JOINT、F1--F6、多特征加权割、关键路径覆盖割、违例扇入锥、简化 SPEF 复测、独立全网表顺序等价检查、纯 G、WNS/TNS 等**未展开机制名与缩写**，改概念化表述；② 首句补"为什么重要"（时序 ECO 在芯片设计中的位置 + 预布局阶段约束）；③ 结果层保留 8/8、18/19、2/3、1.07 vs 0.16 与"无实例退化/尚未达到完全时序收敛"边界；④ 英文摘要同步改写（维持无第一人称）。重编译 → 重冻结 v5 → Word 转排稿随管线再重建（postprocess 摘要串同步）。
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；中文 **264 字**（原 298）、英文 **148 词**（原 150），均合规；PDF 字节 SHA `5c37725a…`（双副本一致）、内容指纹 `0a2b0723…`；tag `v2026-10-09-abstract-plain` + 论文 tag `faeco-paper-final-20261009b`（提交 `1c67f50`）；`versions/v5/MANIFEST.sha256` 117 条全 OK（相对 v4 变动 3 条）。**零数字、零实验、零主张改动**——正文/公式/图表/参考文献未动；正文刻意保留机制名（摘要给大同行、正文给同行）。
- **下一步**：投稿手工/流程项（用户 Word 收尾 + ⚠ OI-021 AIGC 披露 + 承诺书/保密审查/英文长摘要）。

## 2026-10-09 参考文献修复轮：重排文献表 + 重冻结 v4 + Word 稿重建（用户授权方案 A）

- **做了什么**：用户授权方案 A（修 `.tex` 源头 → 重冻结 v4 → Word 重建，涉冻结文件）。① **P0**：`thebibliography` 按正文首次引用顺序由 19 条重排为 **14 条**（原首处引用渲染 `[1,7,9]`，18/19 条错位，违反 JCAD 规范一.1）；② 5 条纯 URL 工具/文档引用（picorv32/yosys/OpenSTA/skywater-pdk×2）按规范一.12 改 `\footnote{\url{…}}` 正文页脚脚注，消除文献表序号占用与 `liberty`/`sky130` 的 bibitem-cite 不匹配；③ P1/P2：`[C]//`→`[C] //`（11 条）、`Integration` 全称、BUFFALO 题名补全 "via Group Relative Policy Optimization"、kravets 页码 `1-6`→`71:1-71:6`、`[Z]` 类型移出、DOI `_` 转义（`6\_5`）；④ 重编译 + 质量门；⑤ **重冻结 v4**（manifest 117 条全 OK，`BASELINE_INDEX.csv` v3→superseded）；⑥ Word 转排稿随管线重建（preprocess 守卫 19→14，pandoc 生成 5 条 Word 原生脚注，Word 引擎导出 8 页），旧稿归档。
- **关键结果**：**9 页 / 0 Error / 0 Overfull / 0 Underfull**；`??`=0；正文无 `[15]`–`[19]`；PDF 字节 SHA `dea21bb3…`（双副本一致）、内容指纹 `6ca972d5…`（poppler 25.07）；tag `v2026-10-09-reference-fix`（投稿就绪）+ 论文 tag `faeco-paper-final-20261009`。**零数字、零实验、零正文主张改动**——仅文献表与引用呈现形式。
- **下一步**：投稿手工/流程项 —— 用户 Word 手工收尾（MathType/占位/图 2 通栏/终稿 PDF，须重算 Word 件哈希）、⚠ OI-021 AIGC 披露（JCAD 硬要求）、承诺书/工作邮箱/保密审查/英文长摘要。

## 2026-10-09 文档同步轮：v3 交接文档对齐 + Word 件哈希登记

- **做了什么**：① 提交 09-30 遗留的 v3 同步批（`5bc0e7d`：LOGS-07 + CURRENT_RUN_HANDOFF v3 节 + T20 锚点 + Word 转排稿随管线重导出）；② 实测复核冻结完好——`versions/v3/MANIFEST.sha256` 117/117 OK、PDF 双副本字节 SHA `28647dc0…`、内容指纹 `70bbd610…`（poppler 25.07）、v3 双 tag 经 `^{commit}` 解析均 = `26f4f3b`；③ 刷新 `START_HERE.md`（HEAD/指纹/tag 由 09-29 旧值 → v3）、`CURRENT_STATUS.md`（补本轮 + 09-30 终审轮）、`TASK_BOARD.md`（T20 行 → v3）、`NEXT_AGENT_PROMPT.md`（v2 → v3）、`.codex-handoff.json`（全字段刷新）、T20 包 §0/§3；④ 登记 Word 转排件字节 SHA256 到 T20 包 §3。
- **关键结果**：main = `5bc0e7d`（论文 v3 tag 仍 = `26f4f3b`）；**未动论文内容、未动代码**；文档与仓库实态对齐。
- **下一步**：投稿手工/流程项 —— 用户 Word 手工收尾（MathType/占位/图 2 通栏/终稿 PDF）、检查单 #3 参考文献核对、⚠ OI-021 AIGC 披露、承诺书/保密审查/英文长摘要。

### 追加：T20 检查单 #3 参考文献核对（2026-10-09）

- **做了什么**：抓取 JCAD 官方《参考文献规范》原文，对 19 条文献做逐条事实核验（IEEE/ACM/dblp/出版社）+ 规范合规比对，报告落 `paper/zh/submission/REFERENCE_AUDIT_20261009.md`。
- **关键结果**：无虚构文献；**发现 1×P0 —— 编号未按正文引用顺序（首处渲染 `[1,7,9]`，18/19 错位）**；5×P1（`[C]//` 缺空格 11 条 / 4 条网址类待定 / Integration 非全称 / BUFFALO 题名截断 / `[Z]` 类型）；4×P2。19 条全英文 → 双语著录规则不适用。修复方案（重排 `.tex` → 重冻结 v4 → Word 重建）**待用户授权**，未动论文。
- **下一步**：等用户对是否修冻结 `.tex` 拍板。

## 2026-09-30 终审修正轮：5 处正文修正 + 重冻结 v3（内容修改终止）

- **做了什么**：用户终审确认前 4 项已改对，提出最后 5 处正文一致性修正（零数字、零实验）：§3.4 F6 交叉引用纠错（§4.4→§4.5）/ §4.1 接受准则闭合 b06 TNS 辅助接受例外 / 摘要（中英）PicoRV32 分母解释（`picorv32_regs` 无 setup path 不参与判定；中文 298 字、英文 150 词）/ 表 8 补 $\Delta L$、$\Delta_{\mathrm{WNS}}$ 符号定义 / §4.5 F6 措辞对齐"启用式反馈"。Word 转排稿随管线同步重建，Word 引擎重导出 8 页。
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）、内容指纹 `70bbd610…`；**重冻结 v3**（tag `v2026-09-30-submission-ready-r2` = `26f4f3b` + 论文 tag `faeco-paper-final-20260930-r2`，manifest `versions/v3`，117 条；v2/v1 superseded）。**用户明示"改完即停止内容修改、不加任何实验"。**

## 2026-09-30 投稿执行轮：五项拍板落地 + 摘要适配重冻结 v2 + Word 转排完成

- **做了什么**：① 用户拍板 OI-018~022（1-C 留修稿轮 / 直接转排 / 摘要授权且同步冻结版 / AIGC 暂缓 / 维持 manifest 默认）；② OI-020 执行——中英摘要按 JCAD 规则改写（295 字 / 149 词，去第一人称），其余正文零改动；**重冻结 v2**（tag `v2026-09-30-submission-ready` = `4dc16c6`）；③ OI-019 执行——Word 转排三件套（`paper/zh/submission/word/`：docx + Word 引擎导出 PDF + 转排说明），管线 = 引用字面化预处理 → pandoc（OMML）→ python-docx JCAD 版式；**本机 Microsoft Word 实测 8 页全对**；④ 方正免费字体四款经 AUR SHA256 校验装为用户级字体。
- **关键结果**：论文未动（v1/v2 冻结版与既有 manifest 未变）；Word 转排件为可溯源新制品（哈希见 T20 包 §3）。

## 2026-09-30 补充材料成文轮：S1–S5 全部初稿完成

- **做了什么**：`paper/zh/submission/supplementary/` 成文 S1（失效事件名映射，**闭合 OI-008 投稿前必办项**）/ S2（实验族与可复现性，脱敏）/ S3（SEC 逐实例，29 PASS + 1 N/A = 30）/ S4（环境工具链）/ S5（基准来源许可）；更正两处过时表述（OI-008 两层命名分工、manifest SEC 行 22→29+1）；补建 PicoRV32 source manifest。
- **关键结果**：论文未动（内容指纹仍 `7adf0279…`）；代码未改；S1–S5 初稿待用户确认。

## 2026-09-29 决策轮：D-01~D-03 落地 + RESULTS.md 对齐 + T20 启动

- **做了什么**：① 用户拍板 D-01=A / D-02=A / D-03=A，T20 目标期刊=JCAD；② D-01 落地——`versions/v1` 轻量冻结（manifest 117 条全 OK 自校验 + tag `v2026-09-29-submission-ready` = `d84061a`，已 push），并实测发现 3 个论文数字源证据文件（`20260826_aggregation/summary.json` 等）此前未被 git 跟踪，现由 manifest 锁定；③ D-02/D-03 台账结案（OPEN_ISSUES「已决」表 + 决策简报注记）；④ `experiments/RESULTS.md` 对齐论文终稿口径——实查修正 ISCAS89/ITC-99/PicoRV32 中位数（+0.10/+0.18/+0.60）与 ITC-99 success 口径（18/19 严格改善），b06 补 TNS 辅助接受事实；⑤ T20 投稿包骨架落 `paper/zh/submission/`（检查单 + cover letter 草稿 + 补充材料清单），JCAD 官方要求调研进行中；⑥ 1-C 评估完毕：代码侧已实现并过 gate，剩余动作是论文插入小节，与内容冻结冲突，待用户拍板。
- **关键结果**：main = `d84061a` + 4 个 tag 上 origin；论文未动（仍 9 页冻结版，内容指纹 `7adf0279…`）；RESULTS.md 三处数字错误已修正并与 `summary.json` 对账一致。
- **下一步**：JCAD 调研回填检查单 → S1–S5 补充材料成文 → 用户决定 1-C（插入论文 / 留到修稿轮）。

## 2026-09-29 论文终稿收敛 + 仓库收敛 + 版面收尾（详见 `agent_handoff/handoff_20260929.md`）

- **做了什么**：终稿审稿三批修改（评审 15 项优先 7 项 `681841a`、第二轮 10 项 `0ea80b6`、必改 4 项 `a8142b6`）；版面两次修复回 9 页（根因均为双栏下 `\FloatBarrier` 退化 `\clearpage`）；删除 81 个历史 `.tex` 与 82 个历史 PDF（删前均先入库固化）；发布冻结 tag `faeco-paper-final-20260929`，机械终检全过（0 `??`、29 label 唯一、19 bibitem ↔ 19 cite）。**用户明确要求停止论文内容修改。**
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull；PDF 字节 SHA256 `9af41d77…`（双副本一致）、内容指纹 `7adf0279…`。

## 2026-09-14 交接整理收尾

- **做了什么**：核查交接文档体系，发现并补齐三处缺口：上轮交接文档变更未提交（本轮 commit+push）、`NEXT_AGENT_PROMPT.md` 为空模板（已补全：目标=D-01~D-03 落地 + T20、约束、证据门）、`.codex-handoff.json` 时间戳过期（已刷新，read_order 补入决策简报）；核查 versions/v1/ 为模板占位（与待 D-01 决策一致）。
- **关键结果**：pytest 264 passed + 4 skipped（环境验证通过）；全套交接文档提交推送，仓库随时可无口头交接。
- **下一步**：不变——用户拍板 D-01~D-03 → 执行决策 → T20 投稿件打包。

## 2026-09-12（下午）决策简报 + 交接收尾

- **做了什么**：为 OPEN_ISSUES 中三项待决策事项（versions/v1 冻结、机制图、DOI/DRC）核实最新事实并编写决策简报 `agent_handoff/DECISION_BRIEF_20260912.md`；刷新 OPEN_ISSUES（OI-001 降级：主稿无 DOI 占位符；OI-006 重定义：当前 9 页稿仅 3 图，原拆分问题已消失；新增 OI-007 hold limitation 记录）与 TASK_BOARD（U26-06/U26-08 关闭、U26-07 部分完成、新增 D-01~D-03 决策项与 T20 投稿打包任务）；重建全套交接文档。
- **关键结果**：三项决策均有明确建议（轻量冻结 / 维持 3 图 / 维持如实声明+按需 rebuttal），用户拍板后下一轮即可执行。
- **下一步**：用户读简报做 D-01~D-03 决策 → 执行（tag+manifest / 无动作 / 关闭对应 OI）→ T20 投稿件打包。

## 2026-09-12 框架架构迁移 + 环境重建 + 旧副本清理

- **做了什么**：robocopy 全量复制仓库（316,765 文件 / 117.7 GB / 0 失败）至 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，git 历史与远程保留；按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）；路径修复（pyproject、12+ 硬编码脚本、19+12 测试锚点）；交接文档重建。随后 `.venv` 用 Python 3.11.9 重建并装依赖；C 盘 3 个 git worktree 删除（分支先推送固化、未提交文档抢救归档）；旧目录全删。
- **关键结果**：pytest 264 passed + 4 skipped 全绿；check_project.sh PASS；live 文件旧路径残扫 0；main 与 origin 同步（35fd558 → f5b6380）。
- **映射全记录**：`migration/MIGRATION_20260912.md`。

## 2026-09-11 第 18 轮审稿修订 + 全文一致性审计

- **第 18 轮**（3d984c6）：接手中断会话的未提交修订（SEC 口径细分、b17 预算披露、benchmark 纳入规则、tab:configs、SPEF 公式、F6 降强），修正幽灵引用/重复段落/配置表事实错误；排版债清零（0 Overfull，9 页）。
- **一致性审计**（d329f19）：修复 8 处正文与实验产物的矛盾（策略分布、b21 +2.75、3363 次 STA、b06 声明、b18/b19 归属、SEC 计数 5 处口径、随机种子、pcpi_mul +0.07）；审计记录 `review_history/paper_audit/consistency_audit_20260911.md`。

## 2026-09-08 ~ 09-09 实验补齐与结果汇总（摘要）

b17 phase-2 重跑（+0.38 ns / 104 STA / SEC 12812+1 unproven）；joint-depth 消融；hold-mode ITC-99（诚实 limitation）；multi-iter ablation 与 --no-early-stop 修复；`experiments/RESULTS.md` + `results.json` 顶层汇总。详见 `LOGS.md`。

（2026-08-11 ~ 08-13 的 17 轮命名版审稿史、2026-08-26 unified-loop 主实验、更早 N31 系列见 `LOGS.md` 与 `review_history/paper_audit/`。）
