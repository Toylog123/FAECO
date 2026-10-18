# r22 继续推进交接 — 2026-10-18（LOG-20261018-59）

## 1. 项目是什么

FAECO研究预布局门级时序ECO候选探索、验证与失效刻画；本轮继续论文审稿修订、证据恢复和配图完善。10-14暂停已被10-16及10-18用户继续指令覆盖；v18保历史，当前r22是工作修订。

## 2. 当前做到哪一步

用户于2026-10-18明确“继续推进 做好记录”，当前授权为继续执行。唯一工作区 `D:/BaiduSyncdisk/01_Papers/03_FAECO`，当前main阶段提交为 `7231e0296da357df435414f75b0a41fe78265837`（941files），origin/main已实际push到7231e02（session60883 exit0）；C′原始source pin仍3ea0f75不回写。归档/图件审查已齐，当前进入S/SPEF修复计划先红后绿，生产可按明确文件归属改动，整体回归/独立review/源码新commit后才注册正式EDA；不恢复已结束的session9345。

**C′v3全72已独立验收。** `project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json`（SHA `a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738`）实核8电路×9臂、all_matrix_verified/source_stable/completion_set_frozen_at_start均true，72个当前completion SHA匹配。8458候选评估记录、6858 candidate_ideal STA+72初始baseline=6930实际STA过程，other0，192保留提交；每终点独立SEC均非零proven/0unproven。physical/electrical/S均false，不能称物理STA。最终审计exit0/runtime46.546s；剩54原运行wrapper3728s/exit0。stage72五件script/log/invocation/receipt/原运行log保真归档；旧51/54/v1失败/v2仅注册原件不覆盖。

当前接受协议是严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不关闭setup_tns预算。零收益与不利结果保留，不调参制造正结果。完整16个weighted/uniform配对已按所有重复同base轮独立核查，5454次交叉比较cut/pool/dispatch全同、16终点全文同（FIGURE_CPRIME_REVIEW269205b9…）；本矩阵未观察到独立权重收益，重复轮不是独立统计样本。新C′不替代旧B3/C/D。

完整v8历史收据为969pass/4skip/156subtests、170源码SHA稳定，OI040/041实现门closed；A6/B2/B17实际对象新证明已各自绑定原pin，B3主线51QA及C作者84/独立注册38QA、原OI042反例拒绝仅关闭工具实现门，尚未新clean pin正式登记同族EDA。四态支持仍open，实际三态/显式Z/switch须unsupported非pass。中英稿时钟元数据OI043已两遍编译/38p视觉/副本验收，仅设置说明门closed；科学回填和投稿声明仍待。

## 3. 已完成的关键工作

- 当前支持域内作用域、多输出物理身份、必需输入、顺序语义与单行解析门已修；v8和原精确V3反例/合法G控制均有原件，不用旧667/757替代当前来源。
- A6、B2、B17确切接受对象新SEC和主线后验已保真，各守source/model/LIB/raw身份；历史runtime缺字段不补造。B2孤立X证书不外推任意四态。
- C′v3固定3ea0f75/manifest72dfbef9…完成8mapped准备、18pilot、余54与最终72验收；准备明确RTL→mapped equivalence=not_run。
- C适配器OI042原末候选TCL漂移反例已被修后独立PinDrift拒绝/0commit，注册38限定QA通过；B3 root51限定QA通过；均未正式同族EDA。
- 18pilot预览v2已有中英caption/最小7pt/视觉通过，尚未插正文。全72四面板v1的72raw/64paired/全部completion SHA与数据解读已独立通过、最小6.8pt；后加自动几何门发现v1六处tick bbox overlap，现另存v3（源d9ef05b…）已collision0/对齐PASS/最小6.8pt/root整图视觉通过，raw/paired CSV与v1逐字节同；独立v3视觉71d9a480…已通过，正式稿件整合待，旧v1/审查不改。
- OI043中英时钟设置已按模块修正，zh12p/en26p，38页视觉/回读及同步副本通过，收益数字/图资产未随此元数据修正改变。

## 4. 当前阻塞与风险

B3/C/D历史科学证据、四态能力与S/SPEF历史风险仍须各自闭环；历史S/SPEF已冻结独立审计：旧258 filtered模型defect被V2推翻（1032组合条目全match/0mismatch或unknown）；S接受链非法基准混淆负gain和CEC pre/post覆盖、SPEF漏真实Lib输出direction/两侧共享SPEF/报告顺序混杂为下一阶段必修。s382历史RC对1/40当前生成均不全文等，仍unknown；不借b18 unit1或scan对象填补。归档阶段已commit7231e02，当前按修复计划先红后绿；整体回归/独立审查及新源码commit后另clean pin做同族EDA。不能把S候选全判invalid或否定物理想法。B3旧24/44阶段源码未找回的OI044边界持续保留。论文仍含待科学复验的旧数，当前中英稿均非投稿定稿。全部未决项见OPEN_ISSUES。

Git新阶段检查点7231e02已commit，push已exit0，远端origin/main=7231e02核符。新修复阶段会有未提交源码，不与C′原始pin混淆。没有新增科学基线tag。旧归档receipt生成不自动等于root后验接受，原实验文件不删。

## 5. 下一步最值得做的任务

当前S/SPEF源修复已保留全部红→绿与失败原件：S限定47pass1skip、OpenSTA/双侧SPEF native边界71pass、SPEF58pass；OI045共享helper派生模型漂移真红→51pass1skip及根原12输入重放已过。整体v1为1013pass2fail11skip（两旧夹具修后2case pass），v2在原工具环境1019pass11skip；其后三文件native补测22pass1fail暴露OI047整库fallback，最小模型子集修复后26pass。上述数字分别对应各自版本/设定，不相加。

OI048更强native负控曾因ABC误选库buf而将ztop Y=A与Y=B实际不同误报pass，修前bca40完整源/输入/log保真。当前真实source top/唯一root并hierarchy-check-top修复后，两个原Verilog输入字节相同、native已正确fail/ABC明确NOT EQUIVALENT，tool_checks_v3为28pass4.29s/RUN4.9232689s且source173稳定；仅原负控及该补测范围过，独立生产review与历史top影响分界审计仍待。

OI048 mapped-right与source-window修复已明确冻结：FINAL_RECEIPTcd5361e2…176原件/四frozen源SHA实核，ya0ba8bb70…/vme8aa320b…；原source prepare前保真、launch前后核，普通/BOM窗口2fail与status真红保留，最终邻接47pass1skip4.64s/native七控+baseline合预期。根原probe三输入逐字节同重放，single inverter正确fail、dummy多root正确error，PROBE8b0d7cd1…/三源稳定；仅原反例与限定实现层通过。当前全v5实际1056pass156subtests208.27s、无skip/warnings，RUN209.1403265/600rc0/wrapper210exit0，显式PYTHONUTF8=1/nativePATH；174before=after=current与ZIP逐SHA核符。独立当前复现代码/产物review9cbabd66…通过（263原件稳定），独立最终接受67da65a4…/FINAL_CLOSURE9928cd3b…已通过（174当前源身份/五轮866ZIP成员/86原件核符）；当前复现实现层限定闭合，历史top影响分界审计仍open，不提前sourcecommit/newpin/正式EDA。

整体v3为1034pass1fail156subtests，唯一assign-only旧wholeLib测试契约更新后v4实得1032pass3fail5warnings156subtests181.75s（RUN182.4937594/600/rc1）；173source before=after与ZIP逐SHA核符。三fail均CLI子进程stdout编码：harness仅-X utf8未传PYTHONUTF8=1，原流反证同CLI同参unset非UTF8/设1可UTF8，均rc0；两相关测试文件显式env后13pass2.72s，无生产改。下一full harness显式env，不能把定向13P冒充全量或覆盖v4。5件tracked c17副产物先保generated/HEAD后精确恢复5/5已实核，首次Git CRLF exactassert失败及两脚本保留；不是科学结果修改。当前source修复仍dirty未commit，OI048新mapped右侧原反例已修/根重放通过，独立最终67da65a4…接受当前实现+全v5实际1056P/174来源稳定；待stage字节QA/阶段source-evidence commit+push，不称完整实现通过/新pin/正式EDA。

真实OpenSTA微型注入已产RESULTf9589064…：actualLIB+spef/opensta前后稳定、43原件SHA核符；两DFXTP夹buf的普通/escaped-literal-vs-busbit路径在RC40/4000um均4.43→-8.38 WNS，四annotation均0未/部分未注入，两个错误pin均null/error。仅这类微型注入实现边界通过，不代b18/任意拓扑/同族科学物理收益；根wrapper16exit0/ROOT_ACCEPTANCE79f5725c…已通过；独立micro复核56bdc6b1…已接受该tiny范围（47原件稳定）。

b18物理恢复OI046仍open：真实baseline/唯一R两对象inout LOGIC0明确unsupported。冻结AUDIT2c3ec37a…/REPORTe38dbafd…15来源稳定：bench明确pseudo-input+同名output，预转换V已有inout，不能按名钉0/默改input或丢输出。保单PB+4I外部被动RC与8反驳控制尚为设计，真实工具未验；BLIF acquisition/原转换receipt/EDIF未知保留。新SPEF真实pilot先合法s382，须新clean pin登记。

OI049新静态待验证边界：ABC CEC timeout partial若bytes，_tail的str join可能TypeError；未跑反例/未修，不是误pass或本次引入结论。全v5已1056P/174源稳定，本阶段源仍冻结待commit，另门先反证再回归，不能笼统称所有timeout已闭。

| ID | 任务 | 状态 | 优先级 | 完成标准 | 下一步动作 |
|---|---|---|---|---|---|
| P02 | C′最终图正式稿件整合 | pending | P1 | 主稿引用/图注/版式与科学证据对应 | v3独立71d9a480…、数据/几何/字形/root与独立视觉已验收；待其他历史族科学门齐后整合 |
| P03 | 新源码回归/独立审查与sourcecommit | in_progress | P0 | OI048原负控正确拒/当前全源码回归与独立review已通过，stage字节QA/sourcecommit+push及clean pin | 7231已push；OI045原反例层及OI048原native负控/三文件28P通过；v3旧assign-only契约1fail保真，仅测试更新后v4运行，v4环境归因已证，mapped原反例修后根重放通过；独立review9cbabd66…限定通过，全v5已1056P/174源稳且最终独立接受，准备stage字节QA/sourcecommit+push |
| P04 | B3/C/D同族科学复验 | pending | P0 | 各族独立新pin/配置/实际EDA/计数/SEC验收 | 全v5/独立review后source阶段commit+push，以新clean HEAD登记D56，先s27/s382共14pilot再余42；全56验收前HEAD/code不变，文档可dirty，不用C′代替 |
| P05 | 四态门与S/SPEF实现修复 | in_progress | P0 | 能力反例与冻结历史对象报告闭环 | 四态继续unsupported；S/SPEF修复限定QA与OI045原反例层已过，整体v2已过/工具skip另补；四态仍unsupported，同族科学复验须新pin |
| P06 | 中英稿图/声明最终回填 | pending | P1 | 同族证据回填、图表/主张一致、编译和视觉QA | 依据CLAIM_REPLACEMENT_MAP逐项推进，不称投稿定稿 |
| P07 | b18 LOGIC0窄域被动RC支持 | pending | P0 | 保原PB+4I和真实接口，新pin下真OpenSTA注入/无缺pin及同族比较 | 报告2c3ec37a…来源15稳定/设计与8反驳控制已齐，尚未实施/测试，不按名钉0 |
| P08 | 历史ABC完整证明真实top影响分界 | pending | P0 | 逐实际调用/CLI/script/log辨识对象与top绑定，不补造缺失身份 | 审OI048受影响API无显式top路径；独立SEQ按实际证据保留，不跨族外推 |
| P09 | ABC timeout bytes异常呈现边界OI049 | pending | P1 | 先真反例复现，再必要修复/回归并保原始partial | 当前仅静态_tail(str join)疑点，未跑/未修；全v5已过/阶段源仍冻，独立后续门 |

## 6. 关键文档与命令

- 总日志 `project_docs/LOGS.md`；登记 `project_docs/evidence/EXPERIMENT_REGISTRY.md`；问题 `project_docs/OPEN_ISSUES.md`；经验 `docs/EXPERIENCE.md`。
- 当前72证据 `project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json`；审计保真包 `matrix_qa/stage72/ARCHIVE_MANIFEST.json`；62件精确运行输入 `source_snapshot/runtime_inputs.zip`。
- B3适配器 `project_docs/evidence/r22_b_model_audit_20261016/B3_RECONSTRUCTION_ADAPTER/`；C适配器及独立review在 `project_docs/evidence/r22_rerun_design_20261016/`。
- 论文主张替换表 `paper/zh/review_rounds/r22_20261016/CLAIM_REPLACEMENT_MAP.md`；时钟修正 `metadata_correction_01/FINAL_QA.json`。
- 记录自检 `bash code/scripts/check_record.sh`；长任务用 `code/scripts/run_with_timeout.sh` 并监测。
- 当前图件复用r21脚本/新r22 contract，禁用旧全量硬编码gen_figures.py重建当前图。

## 7. 文档缺口与建议补齐项

本交接与current状态已基于实际72替换旧51运行层，历史10-16交接保留在 `handoff_20261016_r22.md`。八包归档root后验与机制复查已齐；v3独立视觉追加、稿件整合、提交及后续同族EDA进展必须继续即时同步；周日报告在 `project_docs/reports/weekly/2026-W42.md`。提交前核-text/raw index字节、force-add被忽略ZIP/log/分卷，完整只读审查后commit+push；不得让未提交本地成果被误写为远端可恢复。

## 历史交接（含2026-10-14暂停；当前授权以上方2026-10-16为准）

# r22 暂停交接 — 2026-10-14

> **2026-10-14：用户明确暂停，状态 paused。仅完成状态保全与交接；等待用户明确恢复，不得自动执行下文历史推进任务。**

## 1. 项目是什么

FAECO：预布局门级时序 ECO 的候选探索、验证与失效刻画。当前 r22 是工作修订，v18 保留为历史冻结基线；当前不冻结新基线、不提交期刊。

## 2. 当前做到哪一步

用户最后指令：“先暂停吧 总结 交接 之后再说吧”。所有修复/实验子任务已停止；本机 TOYLOG_DESKTOP、Windows/PowerShell、main。暂停检查点 `71a4c12` 已推送 origin/main，后续仅行政记录收口提交，最终 HEAD 用 `git log -1` 查看。进程只读检查未发现项目 Python/STA/Yosys/LaTeX 在运行；v2未开始，不能自动恢复。

## 3. 已完成的关键工作

- r21五视角模拟审稿与图件修订已归档；中文12页、7图14表，引用与排版已验收。r22仅补2994条可逐项核查独立候选STA报告来源，3363仍是评估记录数；不是完整历史工具启动数。
- 英文 elsarticle 完整初稿27页、7图14表；源稿、PDF、矢量图、CSV/来源、QA、highlights/cover-letter/AI披露及作者输入表已保存。科学结果待恢复，作者事实/声明仍待核。
- 受控候选政策与真实STA启动台账实现；v1只执行W0/s27和W0/s382，最终helper不变门正确拦截跨模块B插入，两例中间收益无效。原始失败目录未改，109文件完整ZIP+逐文件SHA已跟踪。
- B插入、R/G/JOINT作用域、本地F1/F2模块隔离、目标F3分母和异常SEC收据已修；最后完成全套回归667 passed/4 skipped/156 subtests，100.20s/wrapper103/exit0。此数只代表该次测试对象；新反证门尚未修，不代表科学正确性闭合。多输出解析器任务在写盘前被中断，三个parser文件无diff、对应新测试不存在。
- 实读独立历史审计：B保留28个完整实际final/gold SEC绑定；14个ITC对象另有wire声明纪律缺口，不能据此推翻已有功能证明。A两项可复用确切证明、六项待补实际接受候选证明。D 38/40及k1 14/16终点结构不合法；C检查12代表中9不合法、3未知，未外推全集。结构不合法不是本次新SEC证明不等价；未知不是失败。

## 4. 当前阻塞与风险

主线依据历史审计确认需修复实现与证据，不能只弱化结论。两版稿件仍包含待复验的历史A/D/C结果，不是投稿定稿。独立修复审查K1–K6指出：多输出Liberty模型漏HI/COUT、合法conb被F2误拒、CLI端点D全文查找、assign常量变化可穿过局部门、重复实例拒绝不一致、legacy S刷新全文解析/吞异常。见 `../evidence/r22_preflight_20261014/NAMESPACE_FIX_REVIEW.md`。这些尚未修完；OI-030/031/034/035/036/037及既有问题持续保留。

## 5. 恢复后最值得做的任务（当前全部pending）

| ID | 任务 | 状态 | 优先级 | 完成标准 | 下一步动作 |
|---|---|---|---|---|---|
| P01 | 修复K1–K6及验证库模型/解析口径 | pending | P0 | 多输出语义完整、物理实例分母不变、反证门与稳定整套回归通过 | 用户恢复后先复用已归档最小反例，TDD与独立复核 |
| P02 | 恢复历史A/D/C科学证据 | pending | P0 | A六实际接受候选证明；D同臂同输入整族复验；C全实例核查或受影响矩阵重跑 | 保留原结果/归因，B已有证明单列保留 |
| P03 | 新C′受控矩阵 | pending | P1 | 新源码pin/v2目录，18项pilot全部通过才扩至72项 | 不覆盖v1，不拿C′替代历史C/D |
| P04 | 中英稿/图表/提交材料一致回填 | pending | P1 | 当前证据与两版表图结论对应、作者信息声明确认、最终排版QA | 科学证据闭合后重审稿件、更新投稿件 |

## 6. 关键文档与命令

- 入口：`README.md`、`START_HERE.md`、`status_logs/CURRENT_STATUS.md`、本交接、`NEXT_AGENT_PROMPT.md`；全量未决见 `../OPEN_ISSUES.md`。
- 历史审计：`../evidence/r22_historical_correctness_20261014/REPORT.md`；计数恢复 `../evidence/r22_historical_audit_20261014/`。
- 失败pilot：`../evidence/r22_preflight_20261014/PILOT_DYNAMIC_AUDIT.md`、`failed_v1_pilot_snapshot.zip`、`pause_snapshot_manifest.json`。ZIP SHA256 `20940150795c63a19b037b0ab37f026d28c1ac92ce71aa06443b7bf5d4f57cc4`，109条/489998B，CRC与清单数量实查PASS。
- 中文：`../../paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex/.pdf`；PDF SHA `e27eaf3a2c8eaa693a857135d1e266318c0b40233dd54e2f111a36fd7de088cb`，三副本一致。
- 英文：`../../paper/en/manuscript/FAECO.tex`、`../../paper/en/build/FAECO.pdf`（已强制跟踪预览）；PDF SHA `ba4aba890f7bbceb39fc9cdc2b5e7379044098714c3e3d1311982c74e601d14c`。
- 恢复后回归命令：`bash code/scripts/run_with_timeout.sh 300 .venv/Scripts/python.exe -m pytest code/tests -q`。当前只运行交接自检 `bash code/scripts/check_record.sh`、Git差分/快照完整性检查；没有恢复实验或修复。

## 7. 文档缺口与补齐要求

大规模历史原始实验与库/工具仍为本机ignored资产；审计、逐项来源SHA和恢复边界已跟踪，不能声称所有历史raw均可从Git独立复现。本次失败v1完整原件已另外归档。最后667回归来自当时工具回显，不补造原始stdout日志；恢复时重新绑定被测源码并保存完整日志。尚缺新库模型/解析器、新完整正确性证明、有效C′结果、A/D/C科学回填和作者声明确认；均等待用户恢复，不自动执行。


---

## 下方为暂停前历史记录（不代表当前授权）

# Current Run Handoff

> r21 Git收口：实现提交 `e592bfd`、SVG导出规范化提交 `483b5e9` 已成功推送 `origin/main`（2026-10-14）。本轮审稿/配图/计数修复已完成，后续只处理保留的未决项；下文Git待办措辞为推送前记录。

> 最近一轮在最上，历史轮次原样保留在下。**新接手者只需读最上一节**。

## 2026-10-14 — 恢复机制证据、历史档案与投稿推进（r22_20261014，进行中）

**当前阶段（LOG-20261014-23）**：C′正式pilot已实际执行，但首W0/s27与W0/s382最终独立SEC拦截，batch58s/exit1；其它臂未启动，**无有效新族效果结果**。原实验目录完整保留，修复后须新commit/production pin与v2目录，重跑完整受影响矩阵。

**最新历史审计（LOG-20261014-24，待主线复核裁定）**：已实读r22_historical_correctness报告/逐实例JSON与输入SHA。B28完整final/gold SEC绑定保留，b17部分/regs N/A；B14 ITC另有声明纪律缺口，不直接推翻功能保持。A有效证明可复用2，另6旧SEC错绑/缺证；D38/40与k1 14/16结构invalid；C仅12代表中9 invalid/3未知，不外推全集。未知不等失败，结构invalid不是本轮新SEC不等价实测，计数可复算不证明合法候选。论文/复验范围待主线裁定，原证据保留、不借C′覆盖旧结果。

**版本与验收**：r22起始main clean/46ede94；源码/历史审计阶段28c3c2b已commit+push，原manifest绑定43 production文件、8原始输入/LIB SHA及72完整commands。旧production稳定全回归644passed/4skip/156subtests（99.14s，wrapper102/exit0）；后加JOINT on/off static action13项，与flow/candidate/launch联合39passed/0.93s，collection分别列证。修复会改变production，旧通过不可替代修复后当前版本门。

**失败归因与计数**：B插入首个endmodule/helper dff，wire/目标pin留真正top；局部全文件F1/F2解析合并namespace形成伪pass，隔离top后F2 declared-undriven。OI-035跨模块插入与OI-036局部namespace门/历史correctness影响已登记open；domain负责buffer多模块TDD，主线负责目标模块隔离/boundary门与历史影响审计。独立SEC正确阻断，不能以中间+.10/+.05 ns称有效收益，也不据此否定cost设想。实读s27 launch12/eval14，s38211/13；cache0/0，各2条非STA是F1前置拒绝。

**实际pilot配置**：`.venv/Scripts/python.exe -u -X utf8 code/scripts/run_r22_cut_ablation.py --output-dir experiments/20261014_r22_cut_ablation --circuits s27,s382`，session66717，batch43200s包装、每run3900/3930s；共享mapping两例完成，runner47/48s exit0，随后独立SEC失败停止。来源见原manifest、W0两目录/batch_failures.json、EXPERIMENT_REGISTRY。

**历史与论文**：OI-031可恢复档案审计完成，但完整flags/argv/revision仍缺；OI-034 B/D来源闭合，C精确执行数/身份不可识别边界保留。b17独立104row/208SHA及B18独有2890合为2994有报告来源的候选STA结果；3363仍评估记录，非全部工具调用。中文母稿唯一补来源句，12页/7图14表/21引用，质量项全0与逐页视觉通过；三PDF SHA e27eaf3a2c8eaa693a857135d1e266318c0b40233dd54e2f111a36fd7de088cb，793545B，旧作者版先备份。英文约52KB/27页首draft仅已有结果，视觉/声明待核，不可当提交件。

**授权与分工**：用户“继续推进吧那就”恢复历史审计、同运行器双割/cost新族消融和后续英文/投稿材料/Word必要性与最终排版，取代旧暂缓；r21不新EDA只描述历史。专职记录仅改记录文档，不改稿/图/code/Git。OI-030/031/034/035/036保持开放，OI-032/033已修范围追踪，不删旧问题；每次版本/配置变化先新锁，不拼旧C。

| 待推进 | 当前状态 |
|---|---|
| OI-035/036生产修复 | TDD/namespace隔离推进，整体回归与新pin待完成 |
| C′新族完整矩阵 | 首pilot失败目录保留；修复后新v2重跑，不借旧两例成果 |
| 历史correctness影响 | 独立审计accepted动作与最终SEC来源，范围待证据裁定 |
| 英文/材料/Word必要性/排版 | 英文首draft待QA/事实，证据汇合后继续投稿流程 |

## 2026-10-14 — 论文审稿与配图修订（r21_20261014，本轮完成）

**请求与版本**：用户要求审稿本篇论文并修改/增加配图，授权必要图注与引用调整。起始 v18/r20、HEAD `73dc0e7`、工作区 clean。当前为 r21 工作修订，**不冻结 v19**；v18 为不可变参考。下方历史冻结/push 等用户安排不阻塞当前明确授权及 AGENTS。

**审稿交付**：`paper/zh/review_rounds/r21_20261014/` 有五份独立报告（领域、方法、期刊、交叉视角、反驳性）、综合 `editorial_decision.md`、原稿与复核。综合建议 Major Revision；不能把图件改好当成双割因果证据已经闭合。

**图件与文字**：旧源保留；图 1/2 改可编辑矢量，图 3 沿用；新增图 4 B 族全实例、图 5 D 族真实测量 B(k)、图 6 A→A′ 物理保持、图 7 F 族 S 负结果。PDF/SVG/PNG 与数据 CSV/来源指纹齐备。C 明确历史关键实例枚举、不调用 cost/双割、混合含 JOINT/随机无 JOINT、轮内多提交与 TNS 辅助接受；保留旧收益数字，修相关表注与结论归因。A/B 历史 revision/漂移及 b17 两批次分母已披露。

**计数归因**：归档 D 曲线含缓存 provenance，已从原始 trials 排除 `skipped_duplicate` 与无有效来源记录重建 B(k)，保留零收益不修改基线与自然停止点。新 STA Fixed 1947、EMA 2003、随机 2439/2476/2527（均值 2480.7），逐运行与唯一报告路径/sta_used 一致；旧 4146/4883/5624 保留为评估记录。B 的 3363/664/104 改称评估记录；18 实例可确认新 STA 2890，b17 旧 schema 无来源，实际数不可识别。新展示数字是已有台账重算，**没有新 EDA 实验**。

**构建验收**：`build_qa.json` 已验收稿 **12 页 / 7 图 / 14 表 / 21/21 引用 / Error、hbox、vbox、未定义引用全零**；PDF SHA256 `c65169b74925446233345d7dad21ab0abd66b4ff4d9fe2f0c8f2b299c1352ae3`，tex `d36812c85b457e8b40ebd5a110099d5484a839bfc86735da23c30fcd8c94183c`，实际回算吻合。首版 S 图漂页与末页 balance 0.8534 pt 已修；最终用 `flushend[noshrink,nospread]` 双栏平衡。enlargethispage 的 Infinite glue shrinkage 尝试已回退，没有缩字号/行距/砍内容。全12页视觉通过，重点页及图5逐板已核验；源预检0 FAIL、字形最低7 pt、40运行账本审计实际exit0。双PDF与作者版三份字节一致（793394 B）；归档改后稿/差分/QA及证据交叉表已完成。

| 问题/收尾 | 当前状态与下一步 |
|---|---|
| OI-030 | 解释已修；双割/cost 独立因果证据仍开放，消融继续暂缓 |
| OI-031 | 混合接受/提交已披露；对照臂 flags/argv 与历史 revision 档案待恢复 |
| OI-032 | b17 默认 785 与重跑 104 的批次披露完成 |
| OI-033 | D 实际计数/曲线/表列修复完成 |
| OI-034 | 其他历史族计数/旧 schema 审计开放；b17 实际 STA 不可从现档识别 |
| 视觉/副本/文档/记录 | 本轮全部完成；QA与独立账本审计通过 |
| 阶段 Git | 待主线按当前 AGENTS commit+push，另记真实 Git 结果 |
| OI-021/024/027/028 与既有问题 | 保留；Word、成本消融、大规模验证不擅启 |

**接手纪律**：实查证据，不跨族拼接，不删除实验/证据，不擅自插入 1-C。完整原始问题见 `../OPEN_ISSUES.md`；当轮节点日志 LOG-20261014-01～09。

## 2026-10-13 — 学术叙事收敛（r20：唯一主线「候选探索」+ 贡献分层 + 失效反馈弱化 + 实验/结论口径，13 处改写）+ 重冻结 v18

**本轮性质**：**用户对作者版(7) = v17 的第五轮通读意见**（非外部匿名审稿、非技术修改、**不增实验**）。用户判断：**「这一版的整体框架已经基本正确，主线比之前清晰很多」**，本轮**「已经不是『需要重构』，而是『需要最后一次学术叙事收敛』」**；核心要求 = **强化「候选探索」作为唯一主线，让加权割、R/G/B/JOINT、失效刻画、验证流程都围绕该主线服务**，让所有章节回答同一个问题：**如何在有限验证预算下进行有效的预布局 ECO 候选探索**。用户裁定 3 项：核心问题句 = **替换为新句**；贡献结构 = **2 条贡献 + 平台段落**；§4.1 边界句 = **删除**。

**本轮做了什么（13 处叙述层改写）**：
1. **E1/E2 摘要核心思想句**：CN/EN 摘要在「方法之后、结果之前」插入核心思想句——**通过组织多类型候选空间并安排评估顺序，提高有限验证预算下的搜索效率**。
2. **E3 §1.1 核心问题句替换**：「关键挑战并非单一修改动作的优化…」→「**核心问题并非缺少单一优化动作，而是在缺少物理信息的条件下，如何组织多类型局部修改候选并有效分配有限验证资源。**」
3. **E4 §1.3 贡献分层**：引导句「主要**工作**」→「主要**贡献**」；贡献① 主要→**核心**贡献、② 支撑→**辅助贡献**；原第③条（迭代 ECO 与分层验证流程）**移出 enumerate**，改写为独立段落「**在上述贡献之外，本文构建基于公开 EDA 工具链的实现与验证平台作为实验基础：…**」（数字 8/8、18/19、2/2 原样保留）⇒ **2 条贡献 + 1 个平台**。
4. **E5 §3.3.3 末去防御 + 失效反馈弱化**：「定位为搜索诊断与分析机制 / 其是否带来独立增益由 §4.4 单独检验」→「**用于分析失效类型对后续候选构造的影响 / 其实际搜索效果在 §4.4 中评估**」。
5. **E6 失效反馈措辞全篇弱化**：算法 `alg:main`「更新搜索参数」→「按对应失效类型**记录**，并更新后续**搜索分析的输入**」；§3.6「下一轮搜索参数更新」→「下一轮**搜索分析的输入**」；**§4.5（计划外发现）**同源对齐 ⇒ **全篇「搜索参数」= 0 残留**。
6. **E7 §4.5 标题**：「物理时序评估与失效检测」→「**预布局候选筛选的物理相关性分析**」（label `sec:phys_closure` 不变；§4.4 / §4.6 标题按用户肯定保留）。
7. **E8 §5 结论收束句强化**：「…性能提升**可以通过候选空间组织与评估策略优化实现，而不仅依赖单一修改动作**。FAECO 在公开 EDA 工具链上实现了这一思路，为自动化 ECO 搜索提供了可复现的方法基础。」
8. **Edel §4.1（用户裁定删除）**：删「；WNS 改善不等同于完整时序收敛」边界句。
9. **实施**：CRLF 安全脚本 `scratch/patch_r20_tex.py`（13 次替换全部 `count == 1` 唯一命中）+ `scratch/patch_r20_tex_b.py`（E6c 追加），归一化 LF 后改写、再回归 CRLF 并断言无 `\r\r\n`。
10. **质量门**：**11 页**（与 v17 相同、逐页分布不变） / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??` = 0；表图 `\ref` 覆盖 **17/17**；浮动体顺序 **1..14 / 1..3**。
11. **重冻结 v18（四要素）**：tag **`v2026-10-13-narrative-convergence-r20`** + 论文 tag **`faeco-paper-final-20261013i`**；`versions/v18/MANIFEST.sha256`（**117 条全 OK**，相对 v17 **恰 3 条变化** = `.tex` + 双副本 `.pdf`）；`BASELINE_INDEX.csv` v17→superseded / v18→active（**19 行、恰 1 active**）。双副本 PDF `1ebb2864…`（2,610,131 B）。
12. **台账收口**：`LOGS.md`（LOG-20261013-12）、`CHANGE_LOG.md`（r20 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v18」，v17 降为「前序发布版」）、`OPEN_ISSUES.md`（OI-024 `r8~r19`→`r8~r20` + v17→v18 + `取 v17 文本`→`v18`；OI-027 更新为 **v18 = 11 页（页数不变）**；OI-029 续 r20→v18）。
13. **归档**：`paper/zh/review_rounds/r20_20261013/`（`edits.diff` / `abstract_before.txt` / `abstract_after.txt`）；方案 `project_docs/planning/FAECO_R20_NARRATIVE_CONVERGENCE_PLAN_20261013.md`。

**★ 本轮两个要点**：① **零数字用词级比对**——数字 token / 引用键 **0 差异**，`\命令` 差异仅 `\item` 6→5、`\textbf` 83→81（E4d/E5 结构改动，非数据）。② **计划外 E6c**——规划只列 3 处「搜索参数」措辞，执行时全文扫描在 §4.5 又发现 1 处同源表述并弱化，确保全篇 0 残留。

**推送**：**v11 + v12 + v13 + v14 + v15 + v16 + v17 + v18 均未推送 origin**（`origin/main` = `b1403d9`）；push 按惯例等用户明确指令。

**遗留**：无新增。**OI-024 Word 转排件仍为 v6 版，现缺 r8–r20 全部改动**。**CN 摘要 410 汉字（v17 为 372）/ EN 摘要 241 词（v17 为 217）**，须按 Integration 作者指南复核（EN 241 词逼近 Elsevier ≤250 词上限）。

## 2026-10-13 — 论文定位重构（r19：主线强化 + 首次概念定义 + 重要性提升，12 处改写）（前序）+ 重冻结 v17

**本轮性质**：**用户直接指定的「论文定位重构」轮**（非外部匿名审稿、非技术修改、**不增实验**）。用户**自主修正反馈层级**——「前面几轮我更多是在给『审稿结论』，没有展开到**论文修改指导层面**」。核心判断：**当前论文最大的问题不是技术不足，而是论文叙事没有把「FAECO 为什么重要」讲到最高层次——现在像一个完整的 EDA 工具流程，而不像围绕一个核心科学问题展开的方法论文。** 用户三项优先级：**① 重新强化主线 → ② 首次概念定义 → ③ 强化重要性**，并明确「**最需要的是论文定位重构，不是技术重构**」。

**本轮做了什么（12 处叙述层改写 = 16 次替换）**：
1. **A1–A3 首次概念定义**：§1.1 末新增「**候选探索（candidate exploration）**」**定义段**；CN/EN 摘要**首次**出现处展开四类候选全称（逻辑等价替换 R / 门尺寸调整 G / 缓冲器插入 B / 联合修改 JOINT）；§1.2 首句后补「需在多个候选间搜索 ⇒ 大量候选失败 ⇒ 失败并非无效信息」**动机链**（F1–F6 由「附加模块」变为**候选探索闭环的一部分**）。
2. **B1–B3 主线与核心问题**：§1.1 三问引子前加**核心问题句**（候选类型单一 + 候选评估成本高）；§1.3 由三个**平行**贡献改为「**核心问题 + 三个支撑块**」，点明 ① 候选探索框架为**主要贡献**、② 失效刻画为搜索分析**支撑**、③ 迭代 ECO 与分层验证为**可复现承载**；§3.3 标题「加权割与候选搜索」→「**多类型候选探索与排序**」，新增 3 个 `\subsubsection` = **3.3.1 局部逻辑窗口提取 / 3.3.2 多源候选边界生成 / 3.3.3 候选融合排序**（**仅分区与标题化，算法/公式/数字一字未动**）。
3. **C1–C3 重要性**：§1.1 首段补「布局后修改代价上升 ⇒ 迭代依赖尽早、完整的 ECO ⇒ 预布局缺物理信息」链条；§1.1 末新增**关键挑战句**（并非单一修改动作的优化，而是在有限验证预算下如何有效探索多类型局部修改空间）；§5 结论收束句按用户原句替换并保留「在本文实验范围内」。
4. **D1–D4 实验定位句 ×4**：§4.2 / §4.4（新增 2 处表引用）/ §4.3 ITC-99（新增 1 处表引用）/ §4.5。
5. **实施**：CRLF 安全脚本 `scratch/patch_r19_tex.py`——归一化 LF 后 **16 次替换全部 `count == 1` 唯一命中**，再回归 CRLF 并断言无 `\r\r\n`。
6. **质量门**：**11 页**（v16 = 10 页，**+1**；第 11 页仅含参考文献尾部 = **孤儿末页**） / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??` = 0；表图 `\ref` 覆盖 **17/17**；浮动体顺序 **1..14 / 1..3**。
7. **重冻结 v17（四要素）**：tag **`v2026-10-13-positioning-r19`** + 论文 tag **`faeco-paper-final-20261013h`**；`versions/v17/MANIFEST.sha256`（**117 条全 OK**，相对 v16 **恰 3 条变化** = `.tex` + 双副本 `.pdf`）；`BASELINE_INDEX.csv` v16→superseded / v17→active（**18 行、恰 1 active**）。双副本 PDF `862ee713…`（2,609,658 B）。
8. **台账收口**：`LOGS.md`（LOG-20261013-11）、`CHANGE_LOG.md`（r19 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v17」，v16 降为「前序发布版」）、`OPEN_ISSUES.md`（OI-024 `r8~r18`→`r8~r19` + v16→v17 + `取 v16 文本`→`v17`；OI-027 改写为 **v17 = 11 页 + 孤儿末页 + 两道压页实验均已回退**；OI-029 续 r19→v17）。
9. **归档**：`paper/zh/review_rounds/r19_20261013/`（`README.md` / `edits.diff` / `abstract_before.txt` / `abstract_after.txt`）；方案 `project_docs/planning/FAECO_R19_POSITIONING_RESTRUCTURE_PLAN_20261013.md`。

**★ 本轮两个陷阱 / 纪律**：① **页数 10→11**——两道压页实验（删 §3.5 唯一正文 `\FloatBarrier`、图 2 宽度 0.65→0.58）**均未回收页数且已回退**；增长源于用户指定的叙述层新增内容、非版式缺陷；按纪律**未缩字体/行距、未砍内容**；版式压缩并入 OI-027。② **零数字须用词级比对**——`git diff` 行级会连带重现已存在数字 ⇒ 改用**词级 token 多重集比对**确认新增/删除的数据数字为**无**。

**推送**：**v11 + v12 + v13 + v14 + v15 + v16 + v17 均未推送 origin**（`origin/main` = `b1403d9`）；push 按惯例等用户明确指令。

**遗留**：无新增。**OI-024 Word 转排件仍为 v6 版，现缺 r8–r19 全部改动**。**CN 摘要 372 汉字（v16 为 345）/ EN 摘要 217 词（v16 为 203）**，须按 Integration 作者指南复核。

## 2026-10-13 — 图 2 机制图替换（r18：零 `.tex` 改动）（前序）+ 重冻结 v16

**本轮性质**：**用户直接指定的图件替换轮**（非外部匿名审稿、非技术修改、**不增实验**、**零 `.tex` 改动**）。用户指令 **「用这个图片替换图2」**，提供更新版机制图（`违例扇入锥与候选融合排序示意图.png`，1,254×1,254）。

**本轮做了什么（仅换图件）**：
1. **图 2（`fig:cut_generation`）源图替换**：`paper/zh/figures/fig_cut_generation_mechanism_imagegen.png` 由 1,251,525 B（`a3b53e80…`）换为新图 1,152,805 B（`67af5ce4…`，源为剪贴板 JPG，经 `.venv` Pillow 12.3 无损转 PNG）。
2. **新图内容**：在旧版 4 面板（(a) 违例扇入锥 / (b) s-t 分裂图 K(G,t) / (c) 加权最小割候选 / (d) 关键路径覆盖割候选）基础上，**新增「候选融合排序」中间层**（依据：cost(v) + 路径覆盖 + 策略优先级），并将 JOINT 标注由「关键路径联合」改为「关键路径**区段**联合」。该增补与 r17 强调的模块关系清晰化同向。
3. **尺寸 1,254×1,254 不变（1:1）⇒ 版式零位移**：仍 **10 页**，逐页分布不变，无需调 `\FloatBarrier`。
4. **`.tex` 逐字节不变**（`5775eb51…`，图注 / 图表编号 / 参考文献全部未动）；`\includegraphics` 沿用同名文件。
5. **质量门**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0；表图 `\ref` 覆盖 **17/17**；浮动体顺序 **1..14 / 1..3**；图 2 落点第 5 页，渲染正常。
6. **重冻结 v16（四要素）**：tag **`v2026-10-13-fig2-update-r18`** + 论文 tag **`faeco-paper-final-20261013g`**；`versions/v16/MANIFEST.sha256`（**117 条全 OK**，相对 v15 **恰 2 条变化** = 双副本 `.pdf`）；`BASELINE_INDEX.csv` v15→superseded / v16→active（**17 行、恰 1 active**）。双副本 PDF `05ee4ec0…`（2,604,856 B）。
7. **台账收口**：`LOGS.md`（LOG-20261013-10）、`CHANGE_LOG.md`（r18 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v16」，v15 降为「前序发布版」）、`OPEN_ISSUES.md`（OI-024 `r8~r17`→`r8~r18` + v15→v16 + `取 v14 文本`→`v16`；OI-027 v15→v16 页；OI-029 续 r18→v16）。
8. **归档**：`paper/zh/review_rounds/r18_20261013/`（`README.md` / `figure_before.png` = v15 图 2 / `figure_after.png` = v16 图 2）；方案 `project_docs/planning/FAECO_R18_FIG2_REPLACE_PLAN_20261013.md`。

**★ 重要陷阱（本轮）**：**`pdftotext` 内容指纹不变**（`c5fa3f26…` = v15）—— 换图为栅格图、文本层零变化。**换图类改动的验收证据 = PDF 字节 SHA + 页面渲染，不能依赖文本指纹。** 另：`figures/` 不在 manifest 覆盖内（**OI-025**），故 manifest 仅 PDF 两行变化。

**★ 3 项可回退（详见 `versions/v16/README.md` §偏离项）**：① 沿用原文件名（未用中文名，以免动 `.tex`）；② JPG→PNG 转码；③ 图注未显式点出「候选融合排序」层。

**推送**：**v11 + v12 + v13 + v14 + v15 + v16 均未推送 origin**（`origin/main` = `b1403d9`）；push 按惯例等用户明确指令。

**遗留**：无新增。**OI-024 Word 转排件仍为 v6 版，现缺 r8–r18 全部改动**。**CN 摘要 345 汉字 / EN 摘要 203 词**（v15 起，本轮未变）须按 Integration 作者指南复核。

## 2026-10-13 — 逻辑一致性精修（r17：12 处改写）（前序）+ 重冻结 v15

**本轮性质**：**用户直接指定的逻辑一致性精修轮（claim calibration）**（非外部匿名审稿、非技术修改、**不增实验**）。用户对 **作者版(5) = v14** 做**逻辑链专项复审**（自评逻辑完整度 **8.5/10**），裁定「已明显不是防御型论文；问题不是'解释太多'，而是少数地方**贡献强度 > 实验支撑一点点**」，并明确「**不要再增加实验。下一轮应该做：逻辑一致性精修（claim calibration）。重点：控制 claim 范围；明确模块关系；统一'分析/调整/控制'等词。**」

**本轮做了什么（12 处改写 = `.tex` diffstat 11 行；E8+E12 同处摘要行）**：
1. **P0×4**：① §1.3 贡献 1「减少**候选评估开销**」→「减少**候选级评估开销**」；② §3.3 开头**新增三者关系句**「$C_w$ 用于确定候选修改边界，$\mathrm{cost}(v)$ 用于边界内部节点的选择与排序，$C_c$ 用于补充关键路径覆盖」（用户原文『其中，…』因置于小节开头落地为显式主语）；③ 表 5 表题「搜索**参数调整**」→「搜索**分析动作**」；④ §5 结论「…主要因素」前加「**在本文实验范围内**」。
2. **P1×2**：⑤ 摘要末句（中）「上述结果可为…提供参考」→「**实验结果表明，候选空间扩展与候选排序是预布局 ECO 搜索效果的重要影响因素**」；⑥ 摘要末句（英）`and these results inform the design of future …` → `These results highlight the importance of candidate exploration and ranking in pre-placement ECO search`。
3. **配套×6**：表 5 表头 / §3.5 / §4.4 统一「搜索分析（动作）」×3；§1.3 贡献 2 加「**依据**」（用户 §九：不暗示自动优化）；§1.1 与摘要「候选评估开销」→「候选级评估开销」×2（与贡献 1 同句族 / 中英摘要一致）。
4. **目标词实测**：`搜索参数调整` 4→0、`搜索分析动作` 0→3、`候选评估开销`（无级）3→0、`候选级评估开销` 0→3、`控制` 12→12；摘要 CN 331→345 汉字 / EN 201→203 词（同口径）。
5. **质量门**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0；表图 `\ref` 覆盖 **17/17**；浮动体顺序 **1..14 / 1..3**；`.tex` **668 CRLF / 0 裸 LF / 0 `\r\r\n`**。
6. **重冻结 v15（四要素）**：tag **`v2026-10-13-logic-calibration-r17`** + 论文 tag **`faeco-paper-final-20261013f`**；`versions/v15/MANIFEST.sha256`（**117 条全 OK**，相对 v14 **恰 3 条变化**）；`BASELINE_INDEX.csv` v14→superseded / v15→active（**15 行、恰 1 active**）。`.tex` `5775eb51…`（61,801 B）、双副本 PDF `b1d6e5a2…`（2,769,586 B）、内容指纹 `c5fa3f26…`（poppler 25.07）。
7. **台账收口**：`LOGS.md`（LOG-20261013-09）、`CHANGE_LOG.md`（r17 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v15」，v14 降为「前序发布版」）、`OPEN_ISSUES.md`（OI-024 `r8~r16`→`r8~r17` + `f8437a73…`→`c5fa3f26…` + v14→v15；OI-027 v14→v15 页；OI-029 续 r17→v15）。
8. **归档**：`paper/zh/review_rounds/r17_20261013/`（`comments.md` / `response.md` / `README.md` / `manuscript_before.tex` = v14 / `manuscript_after.tex` = v15）；方案 `project_docs/planning/FAECO_R17_LOGIC_CALIBRATION_PLAN_20261013.md`。

**★ 三处配套已列明可回退（详见 `versions/v15/README.md` §偏离项）**：① E2 措辞适配（`其中`→显式主语）；② E4/E5/E6 表头与 §3.5/§4.4 随表题统一为「搜索分析（动作）」；③ E11/E12「候选级评估开销」全篇统一（E11 与贡献 1 同句族 / E12 兼顾中英摘要一致）。

**保留清单（同 r14–r16）**：`控制` 12 处全保留（加权割本体 / 配置开关名 / 内存分治 / 研究问题 / 电路类型）、门尺寸调整等域内术语、§1.1 三问、§2「定义比较维度」、§4.1 主动指标表述、结论「主要因素」本体、r12 M1/M2/M3 表注、PicoRV32 分母说明、NEGATIVE finding 本体、r6 P0「其余无退化」。

**推送**：**v11 + v12 + v13 + v14 + v15 均未推送 origin**（`origin/main` = `b1403d9`）；push 按惯例等用户明确指令。

**遗留**：无新增。**OI-024 Word 转排件仍为 v6 版，现缺 r8–r17 全部改动**。**CN 摘要 345 汉字**（v15）须按 Integration 作者指南复核（旧 JCAD ≤300 规则已失效）。

## 2026-10-13 — 术语一致性与 claim 强度校准（r16：17 处改写）+ 重冻结 v14

**本轮性质**：**用户直接指定的术语一致性 + claim 强度校准轮**（非外部匿名审稿、非技术修改、**不增实验**）。用户以正式期刊审稿人视角对 **作者版(4) = v13** 做第三轮通读，裁定「方向正确，已进入最后精修阶段；主要问题已不是'防御性过强'，而是少数地方仍存在**逻辑层级不够清晰**、个别表述**略偏强**、方法贡献和实验贡献**边界需要进一步统一**」，并明确「**现在不要再增加实验。最后一轮应该做：术语一致性 + claim 强度校准。重点检查三个词：控制、降低、性能边界。**」

**本轮做了什么（17 处改写；`.tex` diffstat 17/17）**：
1. **P0×3**：① §3.5 标题「类型化失效刻画与**搜索控制**」→「…与**搜索分析**」（+ 新增 `\label{sec:failure_char}`）；② §1.3 贡献 1「**降低候选验证开销**」→「**减少候选评估开销**」（依据：验证含 function check/STA/SEC，实验只量化 candidate STA）；③ 摘要末句 CN「**性能边界**」→「**影响**」（改为「分析…对搜索效果的影响」）+ EN `performance boundaries`→`effects … on search performance`。
2. **P1×2**：④ §3.4 正文「边界特征**控制**单次改动的区域范围」→「**影响**…」+ 表 4 行「**控制候选规模**」→「**约束候选规模偏好**」；⑤ §5 结论删逐测试集三元组（8/8、18/19、2/2）与 PicoRV32 分母说明。
3. **结构×2**：§1.1 三问后**新增「问题→方法」映射句**（问题 1→候选探索框架 §3.2 / 问题 2→分层验证流程 §3.6 / 问题 3→失效刻画 §3.5；为 §3.5 新增 `\label{sec:failure_char}`）；§3.2 `λ_c` 角色拆句澄清（节点代价深度折扣 vs 覆盖候选排序）。
4. **配套×8**：验证开销→评估开销 ×4（摘要 CN/EN、§2.3、§3.4）、搜索控制→搜索分析 ×3（§1.1 问题三、§1.2、§3.2 机制名）、「控制输入」→「辅助输入」、「搜索诊断与控制机制」→「搜索诊断与分析机制」、表 5 表注/表头「搜索控制动作/控制动作」→「搜索参数调整」。
5. **目标词实测**：**控制 22→12**、**性能边界 2→0**、**验证开销（自述语境）4→0**、降低 13→12；摘要 CN 330→333 汉字 / EN 207→209 词。
6. **质量门**：**10 页** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / 0 Overfull vbox；`??`=0（`Undefined: 5` = 字体替身警告）；表图 `\ref` 覆盖 **17/17**；浮动体顺序 **1..14 / 1..3**；`.tex` **668 CRLF / 0 裸 LF / 0 `\r\r\n`**。
7. **重冻结 v14（四要素）**：tag **`v2026-10-13-terminology-calibration-r16`** + 论文 tag **`faeco-paper-final-20261013e`**；`versions/v14/MANIFEST.sha256`（**117 条全 OK**，相对 v13 **恰 3 条变化** = `.tex` + 双副本 `.pdf`）；`BASELINE_INDEX.csv` v13→superseded / v14→active（**14 行、恰 1 active**）。`.tex` `9b0bb2ec…`（61,550 B）、双副本 PDF `5c1d060c…`（2,769,462 B）、内容指纹 `f8437a73…`（poppler 25.07）。
8. **台账收口**：`LOGS.md`（LOG-20261013-08）、`CHANGE_LOG.md`（r16 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v14」，v13 降为「前序发布版」）、`OPEN_ISSUES.md`（OI-024 `r8~r15`→`r8~r16` + `55bde9d4…`→`f8437a73…` + v13→v14；OI-027 v13→v14 页；OI-029 续 r16→v14）。
9. **归档**：`paper/zh/review_rounds/r16_20261013/`（`comments.md` / `response.md` / `manuscript_before.tex` = v13 / `manuscript_after.tex` = v14）；方案 `project_docs/planning/FAECO_R16_TERMINOLOGY_CALIBRATION_PLAN_20261013.md`。

**★ 需用户确认的一处取舍（§5 结论 E17）**：用户要求"删 PicoRV32 解释"，但 **r12 M2（★★★★）** 要求 `2/2` 每处都带分母说明。故**删整个逐测试集三元组**（结论不再出现 `2/2`），而非"只删括号保 `2/2`"。三元组已在**摘要 / §1.3 贡献 3 / §4.3** 三处；如用户希望结论保留三元组，回退本项一行即可。

**「控制」的 in/out-of-scope 切分（判据）**：凡「控制」描述由**构造/开关直接决定**的事 → 保留（加权割本体 3 处：L230/L281/L287；配置开关名 6 处；内存分治 1 处；研究问题 1 处；电路类型 1 处）；凡只是**软权重对排序的偏好**或**对失效反馈作用的框定** → 改。

**保留清单（同 r14/r15）**：PicoRV32 分母说明其余 4 处、摘要「其余无退化」（r6 P0）、表 5/8/11 表注口径（r12 M1/M2/M3）、NEGATIVE finding 本体、§3.6/§3.7 口径、§4.1 唯一一处「不等同于完整时序收敛」、表 2 的 `\ref`。

**推送**：**v11 + v12 + v13 + v14 均未推送 origin**（v10 及以前已推送，`origin/main` = `b1403d9`）；push 按惯例等用户明确指令。

**遗留**：无新增（r16 = 单一提交收敛）。**OI-024 Word 转排件仍为 v6 版，现缺 r8–r16 全部改动**。

## 2026-10-13 — 全篇去防御化编辑（r15：正文 11 处语言风格改写）+ 重冻结 v13

**本轮性质**：**用户直接指定的第二轮语言风格轮（非外部匿名审稿、非技术修改）**。用户在 r14 之后按**正式期刊审稿人（Integration / TODAES / TVLSI 方向）视角**再做一次通读，结论：「**这一版技术内容已经比较成熟，但文字风格仍有明显'答辩稿/项目报告'痕迹。最大的问题不是 claim 过强，而是作者过于主动解释审稿人可能的问题，导致主线贡献被稀释**」；指令 = 「论文现在应该从：'证明我没有问题' 转向：'清楚告诉读者我做了什么、发现什么'」；**「剩余工作：不是增加内容。而是：减少解释性文字，提高陈述力度。」** 故 r15 = 在 r14 基础上做**第二轮全篇去防御化**（表达层；**非技术修改**）。**零数字、零实验、零代码、零参考文献改动**；**摘要结构与篇幅未变**（仅末句口径改写）。方案先落 `../planning/FAECO_R15_DEFENSIVE_PURGE2_PLAN_20261013.md`；记录见 `LOGS.md` LOG-20261013-07、`CHANGE_LOG.md` r15 行、`versions/v13/README.md`。

1. **★ 动笔前先与 r14 已清项对账（避免重复劳动）**：用户标注的部分落点 r14 已处理 —— `不主张` = 0、`不等同于`（原 §4.1 / §4.5 / §5 三处）已删至 0、`不单独隔离式 (2)` 已删；故 r15 **不重复**。实测 v12 基线计数：`不讨论` = 1、`未带来额外收益` = 1、`留下三个` = 1。
2. **11 处改写（`.tex` diffstat 11 insertions / 11 deletions = 恰 11 行替换）**：**E1 / E2 摘要末句（中 / 英）** —— 负结果句由「未带来额外收益…逻辑深度降低不等于 WNS 改善」改为「进一步**揭示**候选反馈机制与结构重综合候选的**性能边界**」（能力边界陈述；结构与篇幅不变）；**E3 §1.1**「上述方法留下三个需要在公开工具链上量化的问题」→「**因此，预布局门级 ECO 仍需要解决三个问题**」；**E4 §1.3 贡献 1** 删实验数字句「…取得更大的平均 WNS 改善（1.07\,ns 对 0.16\,ns）」（数字归 §4.4 实验节）；**E5 §1.3 贡献 2**「并利用失效信息分析候选搜索瓶颈、调整后续候选生成策略」→「并**辅助**分析候选搜索瓶颈与候选生成策略调整」；**E6 §2.3** 压成一句并**保住表 2 引用**；**E7 §3.3** 删代码级异常解释（「继续施加深度折扣可能使搜索偏向无法实例化为 R 候选的边界」），保留 r7-P0 事实「其仍可参与 G/B 候选生成」；**E8 §3.4** 扇出特征改「**被优先选择的概率**」；**E9 §4.1** 改「**主要**评价指标」+ 保留**全文唯一一处**「不等同于完整时序收敛」；**E10 §4.5** 改「**分析预布局筛选结果在寄生估计条件下的稳定性**」；**E11 §5 结论**「依据」→「**参考**」（并补"候选探索"口径）。
3. **★ 三处必要偏离（逐条取证，已列入报告）**：① **E6 压缩后仍保留表 2 引用** —— `tab:baseline_cmp` 全文**仅此一处**被引用，照用户「一句话、不带表引用」字面执行会造出**未引用表**、破硬门 **17/17 引用覆盖**；故改写为「…重点比较…三项；**各方法的主要差异见表~2**」。② **E9 保留全文唯一一处「不等同于」**（用户 §十.2「保留一次即可」；r14 已在结论与 §4.5 各删一次，若 E9 再删则计数 = 0）。③ **E11 结论改「候选探索策略」**（与 v9 起标题口径「候选探索与失效刻画」一致）。
4. **保留清单（与 r14 一致）**：PicoRV32 分母说明（5 处，r12 M2 ★★★★）、摘要「其余无退化」（r6 P0）、表 5/8/11 表注口径（r12 M1/M2/M3）、§4.1 b06 TNS 统计口径（r12 M1）、**NEGATIVE finding 本体**、§3.6 物理复测流程说明、§3.7 复杂度口径、§3.4 固定权重声明。
5. **★ 回读校验方法修正（本轮核心教训）**：**默认与 `-layout` 两种 `pdftotext` 模式在双栏边界都会跳栏**，跨栏长片段在被提取文本中**不连续** ⇒ 子串匹配给出**假阴性**（首版脚本误报 4 项 MISSING，如 `扇出特征降低高负载节点被优先选择的概` 被换行截断）。正确做法 = **短片段（≤14 字符）+ 逐行匹配**（任一行命中即算命中）+ **比较前两侧同时剥空白**（`re.sub(r"\s+","",s)`）；修正后 **GONE 10/10 ok、PRESENT 13/13 ok**。
6. **质量门与终检**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox**；`??` = 0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**；浮动体编号阅读顺序 **1..14 / 1..3**；`.tex` **`6ce1d51c…`**（61,334 B；**668 CRLF / 0 bare LF / 0 `\r\r\n`**，vs v12 恰 **11/11**）；双副本 PDF 字节 SHA **`48854388…`**（2,768,538 B）；内容指纹 **`55bde9d4…`**（poppler 25.07 原始输出）。
7. **重冻结 v13（四要素）**：tag **`v2026-10-13-defensive-purge2-r15`** + 论文 tag **`faeco-paper-final-20261013d`**；`versions/v13/MANIFEST.sha256`（**117 条全 OK**，相对 v12 **仅 3 条变化** = `.tex` + 双副本 `.pdf`；由 `scratch/gen_manifest_v13.py` 从 v12 派生、**LF-only**）；`BASELINE_INDEX.csv` v12→`superseded` / v13→`active`（**13 行、恰 1 active**）。**尚未推送 origin**（v11 + v12 + v13 均未上远端；按惯例等用户明确指令）。**r15 = 单一提交**（论文 + 台账 + 交接层）。
8. **台账收口**：`LOGS.md`（LOG-20261013-07）、`CHANGE_LOG.md`（r15 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v13」，v12 降为「前序发布版」）、`OPEN_ISSUES.md`（**OI-024** 扩到「r8~r15」、与 v13 主稿（指纹 `55bde9d4…`）不一致；**OI-027** 更新为 v13 = 10 页；**OI-029** 续记 r15）、交接与状态文档 8 份、`.workbuddy/memory`。
9. **归档**：`paper/zh/review_rounds/r15_20261013/`（`comments.md` = 用户意见原文；`response.md` = 响应 + 11 项清单 + 保留清单 + 三处偏离；`manuscript_before.tex` = v12；`manuscript_after.tex` = v13）。
10. **00_Summary 同步**：作者版 PDF 同步为 `48854388…`；文件名不变（本轮**未改标题**）。

### 下一步（有明确指令再做）

- **OI-028 Integration 转化（当前最高优先）**：英文稿（中文稿作母本）+ `elsarticle` + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；**英文摘要词数上限须按 Integration 作者指南复核**（现 214 词）。
- **OI-024 Word 转排件重建**：仍为 v6 版，现缺 **r8–r15 全部改动**（含六张新表 + r13 摘要两段 + §1.1 改写 + r14 的 10 处 + r15 的 11 处语言风格改写）；`scratch/word_convert/postprocess.py` 的标题/摘要/关键词为**硬编码**，须先同步为 **v13 文本** + 改输入新名 + 重跑整条管线。
- **OI-021 AIGC 披露**按 Elsevier 政策复核；**OI-025** 图源 PNG 不在 manifest 覆盖内；**OI-027** 版式压缩（10 页，留内容定稿后统一排）。
- **OI-026（cost/feature 消融）= 审稿人两轮连续否决 + 用户裁定「暂缓」**，**非投稿前置条件**；**§七 大规模验证**暂缓。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字；④ 不要在正文插 `\FloatBarrier`；⑤ **改 `.tex` 必须纯 CRLF**——写盘前先归一化，并断言 `count("\r\r\n") == 0`；⑥ **manifest 必须 LF-only**；⑦ **回读校验勿用 `-layout`**，且**双栏下两种模式都会跳栏** ⇒ 回读须用**短片段（≤14 字符）+ 逐行匹配 + 两侧剥空白**。


## 2026-10-13 — 去防御化重构（r14：正文 10 处语言风格改写）+ 重冻结 v12

**本轮性质**：**用户直接指定的语言风格轮（非外部匿名审稿、非技术修改）**。用户裁定：**「论文加入了过多防御性限定语，导致主线贡献被削弱。好的论文不是不断解释'我没有声称什么'，而是直接陈述做了什么、发现什么、适用范围是什么」**（「论文不像论文，像答辩稿」）；要求**下一轮不是增加内容，而是做"去防御化重构"**——表达层面由**防御模式**（"本文不声称 / 不等同于 / 不作为 / 不直接比较"）转为**陈述模式**（"本文采用 / 本文评估 / 实验显示 / 结果表明 / 该机制用于"）。**零数字、零实验、零代码、零参考文献改动**；**摘要一行未动**（用户判定"已有少量限定 → 保持"）。方案先落 `../planning/FAECO_R14_DEFENSIVE_PURGE_PLAN_20261013.md`；记录见 `LOGS.md` LOG-20261013-06、`CHANGE_LOG.md` r14 行、`versions/v12/README.md`。

1. **判据（唯一取舍标准，三者皆为"是"才改）**：① 是否在**预先回答一个假想的质疑**（而非陈述事实/结果/范围）？② 删改后**信息是否已被别处覆盖**（表注 / 实验节 / 首次定义）？③ 是否**不是审稿人（r12）指定落点**、也非既有裁定（OI-014 / OI-015 / r6 P0）的载体？
2. **10 处改写（`.tex` diffstat 10 insertions / 10 deletions = 恰 10 行替换）**：用户指定 6 处 —— **E1** §1.3 贡献 2「定位为搜索诊断与候选控制——…而非独立的收敛增益来源」→「利用失效信息分析候选搜索瓶颈、调整后续候选生成策略」；**E2** §2.3「本文不与它们进行直接的定量对比：[三条原因]」→「主要障碍汇总于表 2。本文因此基于公开工具链建立统一实验环境…比较重点为…三项」（三条原因本已在表 2 中）；**E3** §3.4 表 4 表注「不主张权重取值的理论最优性」→「本表总结各特征在候选排序中的作用」；**E4** §4.1「该约束不代表各设计的目标工作频率…不等同于时序收敛」→「本文将 WNS 改善作为评价指标，不讨论完整时序收敛；所有设计在同一约束下比较」；**E5** §4.4 第一组开头「不单独隔离式 (2) 中各特征项的贡献」→「评估候选空间扩展与候选评估顺序对搜索效果的影响；固定权重配置用于保持候选排序规则一致」；**E6** §5 结论删「仅指 WNS 改善，不等同于时序收敛」。同模式追加 4 处 —— **E7** §4.4 第二组「本文不将自适应反馈作为独立的性能提升来源」→「本文将 F1--F6 用于失效分类与搜索参数调整」；**E8** §4.5 删「不等同于对物理实现有效性的验证」；**E9** §4.2「不与 §3.6 的过滤规则冲突」→「即在该准则下产生」；**E10** §4.3.2 同段三重复述收敛为一句（删「该实例未经历时序修复，不属于算法修复失败」）。
3. **★ 保留清单（9 项，逐条附理由）**：**PicoRV32 分母说明（5 处）**（用户明示"必要" + **r12 M2 ★★★★ 指定落点**；2/2 每处都需分母说明，否则被读作抹去一个实例）；**「其余无退化」**（r6 P0 边界声明，正面事实非防御）；**表 5 / 表 8 / 表 11 表注口径**（r12 M1/M2/M3 指定；M3 的"两个 STA 计数口径不同"防**误读**）；**§4.1「b06 … 不计入严格 WNS 改善」**（r12 M1 口径统一载体）；**§3.4 固定权重声明**；**§4.6 S 负结果 +「保留为可选候选类型」**（OI-014(B) 裁定）；**摘要「逻辑深度降低不等于 WNS 改善」+ §4.3「未观察到严格 WNS 改善」**（**NEGATIVE finding 本体**）；**§3.6 物理复测流程说明**；**§3.7 复杂度口径界定**。
4. **★ 与用户范围的唯一偏离（取证处理）**：用户 §六「PicoRV32 正文多次解释 → **一次即可**」**按"不删位置、只去重复"处理** —— 该说明是 r12 M2 指定落点（5 处），且 **2/2 的比值出现在哪些地方，分母说明就必须出现在哪些地方**（否则"2/2"被读成抹去一个实例，与 §4.1 声明的"3 个 PicoRV32 子模块"自相矛盾）。故不删位置，只在**同一处**去掉第二、三遍复述（E10）。详见 `paper/zh/review_rounds/r14_20261013/response.md` §三。
5. **★ 判据应用要点（写入 `versions/v12/README.md` 教训）**：**防御性限定语 ≠ 证据，不能一刀切删除**——保留清单中 **r12 M1/M2/M3 口径表注**与**负结果陈述**是核心不可动项；**"同处三重复述"与"多处各一句必要说明"处置相反**（改前须先分辨）；**去防御化的正确落点常是"把理由搬进表"**（E2 的三条原因本已在表 2）。
6. **质量门与终检**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox**；`??` = 0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`）；`.tex` **`6e2c9ab9…`**（61,839 B；**668 CRLF / 0 bare LF**，vs v11 **10 insertions / 10 deletions**）；双副本 PDF 字节 SHA **`43aedfbb…`**（2,770,198 B）；内容指纹 **`4bc80603…`**（poppler 25.07 原始输出）。
7. **★ 回读校验（用按栏阅读顺序抽取，非 `-layout`）**：8 处旧防御句已消失 / 10 处新陈述句已出现 / 10 项保留项完好。**教训**：`pdftotext -layout` 在双栏下会把右栏文字串进左栏句中间，回读校验会出现"未匹配"**假象**（本轮曾误报 5 处"缺失"）；**回读校验须用 `pdftotext <pdf> -`（按栏阅读顺序），`-layout` 仅用于内容指纹**。
8. **重冻结 v12（四要素）**：tag **`v2026-10-13-defensive-purge-r14`** + 论文 tag **`faeco-paper-final-20261013c`**；`versions/v12/MANIFEST.sha256`（**117 条全 OK**，相对 v11 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变；由 `scratch/gen_manifest_v12.py` 从 v11 派生、**LF-only**）；`BASELINE_INDEX.csv` v11→`superseded` / v12→`active`（**12 行、恰 1 active**）。**尚未推送 origin**（v11 + v12 均未上远端；按惯例等用户明确指令）。**r14 = 单一提交**（论文 + 台账 + 交接层）。
9. **台账收口**：`LOGS.md`（LOG-20261013-06）、`CHANGE_LOG.md`（r14 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v12」，v11 降为「前序发布版」）、`OPEN_ISSUES.md`（**OI-024** 扩到「r8~r14 全部改动均未同步、与 v12 主稿（指纹 `4bc80603…`）不一致」；**OI-027** 更新为 v12 = 10 页）、交接与状态文档 8 份、`.workbuddy/memory`。
10. **归档**：`paper/zh/review_rounds/r14_20261013/`（`comments.md` = 用户意见原文；`response.md` = 响应 + 10 项清单 + 保留清单 + 唯一偏离；`manuscript_before.tex` = v11；`manuscript_after.tex` = v12）。
11. **00_Summary 同步**：作者版 PDF 同步为 `43aedfbb…`；文件名不变（本轮**未改标题**）。

### 下一步（有明确指令再做）

- **OI-028 Integration 转化（当前最高优先）**：英文稿（中文稿作母本）+ `elsarticle` + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；**英文摘要词数上限须按 Integration 作者指南复核**（现 214 词）。
- **OI-024 Word 转排件重建**：仍为 v6 版，现缺 **r8–r14 全部改动**（含六张新表 + r13 摘要两段 + §1.1 改写 + r14 的 10 处语言风格改写）；`scratch/word_convert/postprocess.py` 的标题/摘要/关键词为**硬编码**，须先同步为 **v12 文本** + 改输入新名 + 重跑整条管线。
- **OI-021 AIGC 披露**按 Elsevier 政策复核；**OI-025** 图源 PNG 不在 manifest 覆盖内；**OI-027** 版式压缩（10 页，留内容定稿后统一排）。
- **OI-026（cost/feature 消融）= 审稿人两轮连续否决 + 用户裁定「暂缓」**，**非投稿前置条件**；**§七 大规模验证**暂缓。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字；④ 不要在正文插 `\FloatBarrier`；⑤ **改 `.tex` 必须纯 CRLF**——写盘前先归一化，并断言 `count("\r\r\n") == 0`；⑥ **manifest 必须 LF-only**；⑦ **回读校验勿用 `-layout`**（双栏串栏假象），`-layout` 仅用于内容指纹。

## 2026-10-13 — 大同行入口改写（r13：摘要 + §1.1 引言）+ 重冻结 v11

**本轮性质**：**用户直接指定的大同行入口改写（摘要 + §1.1）**（非外部匿名审稿）。用户裁定「**摘要应该改**——这是当前版本最值得做的最后一处"非技术性增强"」：现摘要开头直接进入「预布局门级时序 ECO / 局部修改映射网表 / 候选多」，**对 EDA 小同行清楚、对 Integration 这类期刊的大同行入口偏窄**（缺"为什么 ECO 重要 / 为什么需要这个阶段 / 为什么已有方法不够"）。要求按 Introduction 的「**大背景 → 具体问题 → 方法 → 结果 → 意义**」重排。范围 = **摘要两段 + §1.1 引言首段**；**零数字、零实验、零代码改动**。记录见 `LOGS.md` LOG-20261013-04、`CHANGE_LOG.md` r13 行、`versions/v11/README.md`。

1. **结构重排**：① 首句补大背景（「随着集成电路规模与设计复杂度持续提升，时序收敛已成为数字芯片设计流程中的关键挑战」）；② 次句补 ECO 定位（「工程变更命令（engineering change order，ECO）通过在已有设计上做局部修改，可降低重新综合与物理实现带来的迭代成本」）；③ 第三句收窄到「其中，预布局门级时序 ECO 在布局布线前探索局部网表修改方案，但受候选空间限制、候选验证开销较高」；④ 方法句补「**关键路径覆盖割**」使中英对称；⑤ 末句并入"意义"（「…可为预布局 ECO 搜索策略设计提供参考」）。英文摘要同步同一结构。
2. **★ 与用户草案的 5 处偏离（逐条取证，非风格取舍）**：① 「工程变更**优化**」→「工程变更**命令**」——**术语错误**（ECO = Engineering Change **Order**），且 §1.1 正文原文即"工程变更命令（engineering change order，ECO）"，照草案写会与正文冲突；② **保留** M2 分母解释句「（PicoRV32 第三个子模块无 setup 路径，不参与改善判定）」（草案改「2/2 个**可评估**实例」= 回退 **r12 审稿人 ★★★★** 指定落点）；③ **保留**「其余无退化」（r6 P0 边界声明；**加入大背景句后更不可删**——背景越宏大，"有限改善"与"时序收敛大问题"的落差越会被审稿人反打）；④ 去「**快速**探索」的无据修饰（效率结论是候选级 STA 次数少 26.3%，非"快速探索"）；⑤ 末句补"意义"（用户五段结构中含"意义"；沿用 r11 结论末句口径，不引入新主张）。
3. **遵从用户自我约束**：**不写"先进制程"**（落文用"集成电路规模与设计复杂度持续提升"，不涉工艺节点，避免与 SKY130 实验被指"先进节点 claim 过大"）；中文首句未用"先进数字芯片"而作"数字芯片设计流程"；**摘要仍无第一人称**（中文不出现「本文」——草案含"本文提出"已改"为此提出"；英文无 we）。
4. **长度复核**：中文 244 → **349** 汉字、英文 164 → **214** 词。**「中文 ≤300 字 / 英文 ≤150 词」是 JCAD 征稿简则规则，随改投 Integration 已失效**；新约束（Elsevier 常见 ≤250 词）**须在 OI-028 轮按 Integration 作者指南正式复核**——已记入 OI-028，不沿用失效规则判合规。
5. **★ 本轮自造事故与修复（写入 `versions/v11/README.md` 教训 1）**：改写脚本 `raw.decode()` 后**未归一化即** `replace("\n","\r\n")`，把每行变成 **`\r\r\n`（668 处）**；LuaLaTeX 把多出的裸 `\r` 当作额外换行 ⇒ 插入大量 `\par` ⇒ **83 Errors / 2 Overfull / 11 页**。且 `count("\r\n")` 与 `count("\n")-count("\r\n")` **无法检出**（仍 = 668 / 0）。用 `scratch/fix_r13_eol.py` 恢复纯 CRLF 后全绿。**判据**：落盘后断言 `count("\r\r\n") == 0`。
6. **质量门与终检**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox**；`??` = 0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`）；`.tex` **`8fccfab0…`**（62,936 B；**668 CRLF / 0 bare LF**，vs v10 **3 insertions / 3 deletions = 恰 3 行替换（摘要 CN + 摘要 EN + §1.1 引言首段）**）；双副本 PDF 字节 SHA **`a720829b…`**（2,773,302 B）；内容指纹 **`65e29b84…`**（poppler 25.07 原始输出）。
7. **重冻结 v11（四要素）**：tag **`v2026-10-13-abstract-broaden-r13`** + 论文 tag **`faeco-paper-final-20261013b`**；`versions/v11/MANIFEST.sha256`（**117 条全 OK**，相对 v10 **仅 3 条变化** = `.tex` + 双副本 `.pdf`；由 `scratch/gen_manifest_v11.py` 从 v10 派生、**LF-only**）；`BASELINE_INDEX.csv` v10→`superseded` / v11→`active`（11 行、恰 1 active）。**尚未推送 origin**（按惯例等用户明确指令）。**r13 收敛链 = 2 提交**（`bd51520` 摘要 → 链末提交「§1.1 引言入口 + 台账全量同步」）；**v11 双 tag 经 `git tag -f` 一并前移至链末提交**（v11 从未推送 origin，故 tag 在链内前移、无历史改写影响，与 r11 先例一致；两 tag 均为**注释 tag**，与仓库既有 25 个 tag 一致）。
8. **台账收口**：`LOGS.md`（LOG-20261013-04）、`CHANGE_LOG.md`（r13 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v11」，v10 降为「前序发布版」）、`OPEN_ISSUES.md`（**OI-024** 扩到「r8~r13 全部改动均未同步、与 v11 主稿（指纹 `65e29b84…`）不一致」；**OI-028** 更新摘要长度口径 = 中文 349 字 / 英文 214 词 + "须按 Integration 作者指南复核词数上限"）、交接与状态文档 8 份、`.workbuddy/memory`。
9. **归档**：`paper/zh/review_rounds/r13_20261013/`（`comments.md` = 用户意见原文；`response.md` = 响应 + 5 处偏离取证；`manuscript_before.tex` = v10；`manuscript_after.tex` = v11）。
10. **00_Summary 同步**：作者版 PDF 同步为 `a720829b…`；文件名不变（本轮**未改标题**）。

### 下一步（有明确指令再做）

- **★ §1.1 引言入口（已于同日续轮一并落地）** —— 用户追加指令「§1.1 引言入口一并补大背」后，§1.1 首句已一并改写：补与摘要**逐字一致**的大背景句（「…时序收敛已成为数字芯片设计流程中的关键挑战」）+ ECO 迭代成本定位，并把原句改为「按修复目标，ECO 可分为功能与时序两类」（**避免同段二次定义 acronym**）；全文「先进制程 / 先进工艺」计数 = 0。**该增量为 r13 收敛链第 2 个提交**（链末提交 `d59e00f`）。
- **OI-028 Integration 转化（当前最高优先）**：英文稿（中文稿作母本）+ `elsarticle` + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；**英文摘要词数上限须按 Integration 作者指南复核**（现 214 词）。
- **OI-024 Word 转排件重建**：仍为 v6 版，现缺 **r8–r13 全部改动**（含六张新表 + r13 摘要两段 + §1.1 改写）；`scratch/word_convert/postprocess.py` 的标题/摘要/关键词为**硬编码**，须先同步 + 改输入新名 + 重跑整条管线。
- **OI-021 AIGC 披露**按 Elsevier 政策复核；**OI-025** 图源 PNG 不在 manifest 覆盖内；**OI-027** 版式压缩（10 页，留内容定稿后统一排）。
- **OI-026（cost/feature 消融）= 审稿人两轮连续否决 + 用户裁定「暂缓」**，**非投稿前置条件**；**§七 大规模验证**暂缓。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字；④ 不要在正文插 `\FloatBarrier`；⑤ **改 `.tex` 必须纯 CRLF**——写盘前先归一化（`decode` 后立刻 `replace("\r\n","\n")`，落盘再 `replace("\n","\r\n")`），并断言 `count("\r\r\n") == 0`；⑥ **manifest 必须 LF-only**。

## 2026-10-13 — 投稿前一致性 pass（r12：第五份外部审稿 M1–M5）+ 重冻结 v10

**本轮性质**：用户提供**第五份外部审稿**（「**投稿前最后一轮审稿人视角**」，对 **v9 / 作者版 10 页**；归档 `paper/zh/review_rounds/r12_20261013/`），审稿人评分 = 问题价值 9 / 方法完整性 8 / 创新表达 8 / 实验完整性 8 / **证据一致性 7** / Integration 匹配度 8.5，**最大风险被明确为可读性风险**（审稿人能否准确理解「哪个实验验证哪个机制」）。审稿人给出的必改清单 **M1–M5**，并明确指令：**「不要再加实验。做一次 Submission consistency pass……完成后，这篇论文才是真正的投稿版本。」** 用户据此裁定范围 = **仅 M1–M5**。审稿人**再次否决**补做 cost/feature 消融（与 r10 立场一致，与 r11 用户「暂缓」裁定一致）。**零数字、零实验、零代码改动**（纯口径统一 + 主张强度 + 措辞）。记录见 `LOGS.md` LOG-20261013-01/02、`CHANGE_LOG.md` r12 行、`versions/v10/README.md`。

1. **M1 · SEC 统计口径统一（表 5）**：表 5（`tab:overview`）ITC-99 行 SEC 列 `\textbf{19/19}` → `18/19`，并在**表注前置**「SEC 列为完全证明的修改网表对数；ITC-99 的 b17 有 1 个等价点未完成证明（见 `\S\ref{sec:ood}`），故记为 18/19」。
   - **判据**：正文自始为「30 实例 / 29 产生修改 / **28/29** 完全证明」，拆分式 `8 (ISCAS89) + 18 (ITC-99) + 2 (PicoRV32) = 28` 一直自洽 ⇒ **表 5 是唯一漏改处**。**审稿人猜「表 7」，实为表 5**（审稿人指出的位置不准，但错误真实存在）。改后全文 `19/19` 计数 = **0**。
2. **M2 · PicoRV32 统计与分母解释（5 处）**：`2/3` → **`2/2`** + 一句「PicoRV32 第三个子模块无 setup 路径，不参与改善判定 / 不计入分母」。落点 = **摘要 CN**、**摘要 EN**、**§4.3**（`sec:ood`）、**结论**、**表 5** PicoRV32 行。改后 `2/3` 计数 = **0**、`2/2` 计数 = **7**（渲染 PDF 逐字复核）。
3. **★ M3 · 表 11 预算解释 —— 本轮最重要取证：论文里存在两个不同的 STA 计数器**（审稿人指出「500 预算」与「4146」看似矛盾）：
   - `state.budget.sta_used`（`code/src/rseco/search_state.py:254` `reserve_budget`；检查点 `code/src/rseco/flow.py:591`）= **每轮迭代预约一次、到迭代边界才判顶**（`trial_count >= sta_budget → stop_reason = "sta_budget"`）的**预约计数**，**逐电路** ≤ 500；**random 臂确实触顶**：`random_s1/s420`、`random_s2/s420 + s641`、`random_s3/s420 + s641`。
   - `n_candidate_sta_runs`（`code/scripts/run_outerloop_real_wns.py:437` = `len(evaluator.trials)`）= **候选级 STA 测量次数**（= 论文 §4.4 口径），逐电路最高 **1321**。
   - ⇒ 表 11 的 8 电路合计（fixed **4146** / adaptive **4883** / random 三种子均值 **5624**）**不受 `500×8` 约束，数字无需更正**；缺的只是口径说明，已写入表 11 表注。**旁证**：`--sta-budget` 的 CLI help 原文即 "Hard maximum candidate STA **reservations**"，而表 11 数的是 **measurements**。
4. **M4 · 贡献 1 弱化 `1.07 ns` 与加权割的绑定（§1.3）**：不再把 `1.07\,ns` 对 `0.16\,ns` 紧挂在「多特征加权割 + 关键路径覆盖割」的机制归因上（主实验实际对照的是**候选空间 + 排序**的联合效应），改为「在固定权重、20 轮迭代配置下，**混合候选策略**相较**单一门尺寸调整策略**取得更大的平均 WNS 改善（1.07\,ns 对 0.16\,ns）」。贡献 2 的自我限制句（搜索诊断与控制、非独立增益来源）**保留**。
5. **M5 · 特征动机措辞降调（§3.4 正文 ×3 + 表 4 行 ×3）**：`避免修改跨越局部逻辑闭合边界`→`降低跨越局部逻辑边界候选被优先选择的概率`；`降低候选的功能与结构验证成本`→`使搜索倾向于选择验证规模较小的候选`；`避免在扇出较大的节点上引入电气与负载风险`→`以降低引入电气与负载风险的可能`；表 4 对应行改「降低…的优先级 / 倾向选择… / 降低…候选的优先级」。**依据**：这些特征只进入式 (2) 的**排序**，硬约束来自**构造级检查**，故「避免 / 保证」属过强主张。
6. **另（审稿人「问题 2」）**：§4.4 开头补「…比较候选空间与候选评估顺序的**联合影响，不单独隔离式~`\eqref{eq:cost}` 中各特征项的贡献**（特征项属候选生成过程的一部分，其权重在本组固定不变）：」。
7. **质量门与终检**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox**；`??` = 0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`）；`.tex` **CRLF 668 / 0 bare LF**（61,948 B，vs v9 **15 insertions / 15 deletions**）；双副本 PDF 字节 SHA **`4ef380f7…`**（2,770,949 B）；内容指纹 **`c7b4d807…`**（poppler 25.07 原始输出）。
8. **重冻结 v10（四要素）**：tag **`v2026-10-12-pre-submission-consistency-r12`** + 论文 tag **`faeco-paper-final-20261013`**；`versions/v10/MANIFEST.sha256`（**117 条全 OK**，相对 v9 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变；由 `scratch/gen_manifest_v10.py` 从 v9 派生、**LF-only**）；`BASELINE_INDEX.csv` v9→`superseded` / v10→`active`（11 行、恰 1 active）。**已推送 origin（2026-10-13，用户指令「推送」）**：`main` = `origin/main` = **`b1403d9`**（v10 双 tag 所指），`git ls-remote --tags origin` 中两 tag 的 `^{}` 均 = `b1403d9a683b…`；推送簿记提交位于 tag 之外，符合 r9（`0602326` tag + `f29475c` 文档提交）与 r11 先例。
9. **台账收口**：`LOGS.md`（LOG-20261013-01/02）、`CHANGE_LOG.md`（r12 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v10」，v9 降为「前序发布版」）、`OPEN_ISSUES.md`（**OI-024** 扩到「r8~r12 全部改动均未同步、与 v10 主稿（指纹 `c7b4d807…`）不一致」/ **OI-027** 更新为 v10 = 10 页 / **新增 OI-029** = 第五份外部审稿落地）、`.workbuddy/memory`。
10. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF（`4ef380f7…`）；文件名不变（本轮**未改标题**）。
11. **本轮踩坑与经验（写入 `versions/v10/README.md` 教训节）**：① **「台账里有两个同名概念」是最隐蔽的口径错误来源** —— 判据 = 一个数字若与另一数字"看起来"违反同一约束，先确认两者**是否同一计数器**，再决定改数字还是补说明；② **审稿人指出的错误位置可能不准，但错误往往真实存在** —— 用完整拆分式回代唯一定位（`8+18+2=28` ⇒ 只有表 5 矛盾）；③ **口径统一 ≠ 数字改动** —— 记录时须与"新增/修改数字"明确区分，否则污染"零数字改动"声明；④ **主张强度修正须回代码确认约束来源**（M5 的「避免 ×3」过强，是因为硬约束在构造级检查、而特征只进排序）；⑤ **`.tex` 每次插入块后须重新归一化行尾**（三引号块用 `\n` 会引入裸 LF，须统一回 CRLF）。

### 下一步（有明确指令再做）

- **OI-028 Integration 转化（当前最高优先）**：英文稿 + `elsarticle` 格式 + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；**英文标题已定锚**（`FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO`）。
- **OI-024 Word 转排件重建**：仍为 v6 版，现缺 **r8–r12 全部改动**（含**六张**新表 + 本次 15 处文本改动）；`scratch/word_convert/postprocess.py` 的标题/摘要/关键词为**硬编码**，须先同步 + 改输入新名 + 重跑整条管线。
- **OI-021 AIGC 披露**：按 **Elsevier** 政策复核。**OI-025** 图源 PNG 不在 manifest 覆盖内。**OI-027** 版式压缩（10 页，留内容定稿后统一排）。
- **OI-026（cost/feature 消融）= 审稿人两轮连续否决 + 用户裁定「暂缓」**，**非投稿前置条件**；方案备于 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7（新族 C′ / 新表 / 4–5 h / 允许 NEGATIVE）。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：需新基准接入 + 新算力；暂缓。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（r12 再次确认零数字改动；`19/19→18/19`、`2/3→2/2` 属口径统一）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（**必须纯 CRLF**，插入块后须重新归一化）；⑥ **manifest 文件必须 LF-only**（`sha256sum -c` 遇 CRLF 会把 `\r` 当文件名；`.gitattributes` 已锁 `versions/*/MANIFEST.sha256 text eol=lf`）。

## 2026-10-12 — 投稿前精修（r11：标题 / 摘要 / 贡献定位 / 术语与语言风险）+ 重冻结 v9

**本轮性质**：用户提供一份「投稿前精修」六阶段方案（阶段 1 贡献重定位 / 阶段 2 §3.4 固定权重声明 / 阶段 3 cost 消融 / 阶段 4 英文标题重设计 / 阶段 5 Related Work 比较焦点句 / 阶段 6 语言风险审计），**先取证核验再执行**（方案落 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md`，不做重复项）。用户随后裁定三则：① **英文标题** = `FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO`，**中文标题** = `FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画`；② **cost 消融暂缓**（不作为当前投稿前置条件；理由 = 主论证链已闭合，新增会引入"为什么主实验不用这个配置"的解释成本，**若审稿人要求再做**）；③ **Step 1（标题、贡献、语言风险、定位调整）立即执行**。**零数字、零实验、零代码改动**（纯文字/定位）。记录见 `LOGS.md` LOG-20261012-05/06、`CHANGE_LOG.md` r11 行、`versions/v9/README.md`。

1. **★ 决定性核验：六阶段中三阶段已在 r10/v8 落地，不可重做**。阶段 2（§3.4 特征设计动机 + 固定权重 $1.0$ 声明）、阶段 3 所指的 runtime 表（= 表 11 `tab:runtime`）、阶段 5（§2.2 基线定位 + 表 2 `tab:baseline_cmp`）**均已由 r10 落地**；重做会造出**重复表**与**自相矛盾句**。故本轮只落地真正未做的部分。
2. **★ 取证更正（OI-026，纠正 r10 台账的误定位）**：审稿人所指的 cost/feature 消融**不能在 §4.4 的运行器上做** —— 表 9/表 10 出自 **族 C**，其运行器 `code/scripts/run_hybrid_repair.py` 的 `parse_args()` **完全没有 λ 参数**，候选排序只由 `--strategy-priorities` + `strategy_selector.exploration_order()` + 可选 `--random-order` 决定，**根本不调用 `cost(v)`（`cut.py:182–213`）**。因此 r10 台账"加权割消融…改 `flow.py:359/385`"属**误定位**（`flow.py:359/385` 是 constrained-cut/cover-cut 分支，不是 λ 硬编码点）。正确表述：式 (2) 消融 = **新实验族 C′**，需给 `real_wns.py` 的权重对象（现仅 3 键 λ_b/λ_s/λ_c）补 **λ_v/λ_f** 并新加 CLI（λ_v/λ_f **无初始参数、无 CLI** = 真正的代码缺口）；预算由"40–60 min"更正为 **4–5 h**。附带澄清 **λ_c 三重角色**：节点代价深度折扣（`cut.py:208`）、关键路径覆盖候选**插入**（`cut.py:306`，门控 `critical_reward > 1.0`）、尺寸精化割 `covered` 奖励（`cut.py:403`）。
3. **7 组改动（23 insertions / 23 deletions）**：① 标题 CN/EN；② 摘要 CN/EN + 英文关键词（减"structured framework"，增"candidate exploration"）；③ §1.3 贡献 1/2 重写（**贡献 1** 框架定位 = 多特征加权割 + 关键路径覆盖割扩展局部修改空间 + 候选排序降低验证开销，并给 1.07 vs 0.16 ns；**贡献 2** 失效刻画机制 = F1--F6 六类，明确**定位为搜索诊断与候选控制、非独立收敛增益来源**；**贡献 3 保留**）；④ 术语统一（`类型化失效归因`→`类型化失效刻画`、`失效归因`→`失效刻画`、`结构化归因`→`类型化刻画`、**`结构化排序`→`候选排序` ×7**）；⑤ §2.2 比较焦点句；⑥ **结论末句（M4）**不得停在"当前 EMA 反馈与 S 候选均未取得独立收益"，改为"实验分析进一步揭示了候选排序、验证预算和结构扩展之间的关系，为后续预布局 ECO 搜索策略设计提供依据"；⑦ 3 处语言风险修正。
4. **重命名（live pointers 已更新，历史记录保留旧名）**：`…FAECO_面向预布局门级时序ECO的…结构候选搜索与失效归因.tex` → **`…FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`**（PDF 双副本同步改名）。**live pointers 已同步**：`tools/sync_to_summary.py`、`paper/zh/figures/{insert_spef,convert_tables}.py`、`paper/zh/manuscript/{_extract_pages,_render_exp}.py`、`README.md`、`paper/zh/README.md`、`docs/GLOSSARY.md`、`.codex-handoff.json`、`START_HERE.md`、`NEXT_AGENT_PROMPT.md`。**历史记录刻意保留旧名**：`versions/v1..v8/`、`CHANGE_LOG.md`/`LOGS.md` 旧行、`agent_handoff/` 快照、`submission/`。
5. **语言风险实测（非臆造）**：v8 `.tex` 计数 —— `首次提出`=0 / `显著`=0 / `有效提升`=0 / `创新`=0 / `突破`=0；`优于`=1（事实陈述）、`有效`=5（均为"有效/valid"义）、`证明`=8（均为 SEC/CEC 形式证明）、`关键`=39（多为"关键路径"）。结论：仅约 5 处真实风险，已逐一处置。
6. **质量门与终检**：**10 页** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox** / 0 undefined refs；`??`=0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`，硬编码路径已随重命名更新）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`，须传 `<pdf> <tex>`）；论文 `.tex` **`22de39a0…`**（668 CRLF / 0 bare LF, 61,144 B，vs v8 **23 insertions / 23 deletions**）；双副本 PDF 字节 SHA **`f642e533…`**（2,769,731 B）；内容指纹 **`3832eeb2…`**（poppler 25.07 原始输出）。
7. **重冻结 v9（四要素）**：tag **`v2026-10-12-submission-polish-r11`** + 论文 tag **`faeco-paper-final-20261012c`**（**均 → `e00315a`**，即 v9 终态提交；链：`daba5ab` 主稿/台账 → `da61cdf` 指针状态同步 → `e00315a` handoff 补记）；`versions/v9/MANIFEST.sha256`（**117 条全 OK**，相对 v8 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变；由 `scratch/gen_manifest_v9.py` 从 v8 派生）；`BASELINE_INDEX.csv` v8→`superseded` / v9→`active`（10 行、恰 1 active）。**已推送 origin**（`main` = `origin/main` = `e00315a`，21 个 tag 全部上远端）。
8. **台账收口**：`LOGS.md`（LOG-20261012-05/06）、`CHANGE_LOG.md`（r11 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增"★ 当前发布版 v9"，v8 降为"前序发布版"）、`OPEN_ISSUES.md`（**OI-026 标暂缓** / **OI-024 扩到"r8+r9+r10+r11 改动均未同步 + 标题/摘要为旧口径 + 术语仍为旧名"** / **OI-027 更新为 v9 = 10 页** / **OI-028 记入已定标题与重命名**）、`.workbuddy/memory`。
8b. **★ 发现并修复「指针/状态层」三轮漂移（非本轮改动，系 r9/r10/r11 遗留）**：`README.md`、`START_HERE.md`、`NEXT_AGENT_PROMPT.md`、`.codex-handoff.json`、`WORK_PROGRESS.md`、`CURRENT_STATUS.md`、`TASK_BOARD.md` 七份文档**只跟到 v6**（`b1eee25` / 8 页 / JCAD / 指纹 `88b03403`；`.codex-handoff.json` 的 `project` 串甚至是旧题目），与本轮新标题拼成"**新标题 + v6 旧状态**"的混合信息（旧 stem 残留探针 `grep -rln 结构化候选搜索与失效归因` 揪出）。已全部同步到 v9（commit **`da61cdf`**）。**教训：交接层不止 `CURRENT_RUN_HANDOFF.md` 一份** —— r9/r10 只更新它，导致其余 7 份漂移 3 轮；下一轮收口须按 `AGENTS.md` 工作规则 7 逐份过：**WORK_PROGRESS / CURRENT_STATUS / TASK_BOARD / CURRENT_RUN_HANDOFF / START_HERE / NEXT_AGENT_PROMPT / `.codex-handoff.json` / README**。
9. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF 为 **`FAECO_面向预布局门级时序ECO的候选探索与失效刻画_作者版.pdf`**（`f642e533…`），**旧名文件已删除**（同一论文只保留一份最新作者版）。

### 下一步（有明确指令再做）

- **OI-026（cost/feature 消融）= 用户裁定「暂缓」**，**不作为当前投稿前置条件**；方案已就绪（`planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7 = 新族 C′ / 新表 / **4–5 h** / **允许 NEGATIVE**）；**仅当审稿人明确要求时**再启动，且须先落方案。
- **OI-028 Integration 转化（当前最高优先）**：英文稿 + `elsarticle` 格式 + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；**英文标题已定锚**（见本轮）。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：需新基准接入 + 新算力；**暂缓**。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（r10/r11 均已确认零数字改动）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（**必须纯 CRLF**，插入块后须重新归一化）；⑥ **manifest 文件必须 LF-only**（`sha256sum -c` 遇 CRLF 会把 `\r` 当文件名，报 `'…'$'\r': No such file or directory`，须用 `open(..., newline="\n")` 写）。

## 2026-10-12 — 复审四（r10，零算力增强）+ 目标期刊改投 Integration：重冻结 v8

**本轮性质**：用户提供**第三方复审四**（对 **v7 / 作者版 9 页**；总判断 = 已从「实验不闭环」提升为「**基本完整的 EDA 论文实验体系**」，**主要问题不再是实验不足，而是创新高度、方法定位与期刊匹配**；归档 `paper/zh/review_rounds/r10_20261012/comments.md`）。用户三则裁定：① 执行范围 = **只做零算力项**；② 运行时间表口径 = **族 D 三臂**；③ 目标期刊 = **改投 Integration, the VLSI Journal**（取代 JCAD）。**零数字、零实验、零代码改动**。记录见 `LOGS.md` LOG-20261012-03/04、`CHANGE_LOG.md` r10 行、`versions/v8/README.md`。

1. **★ 决定性核验：审稿人要的运行时间表不可零算力实现**。审稿人要求 `方法 \| STA 次数 \| 总运行时间(s)`，方法列 = **Random / Pure G / FAECO**，三列出自**表 9 = 族 C**（`20260807_multiround_8c_067` + `20260826_ablation_*`）。穷举探针 `scratch/probe_runtime_fields.py` 证明**族 C 全部 JSON 与 `.log` 均无任何时间字段** ⇒ 该列在冻结 revision 下**不可恢复**（族 C 的调用命令亦未归档，OI-012）。
2. **★ 关键否证：族 D 不能充当表 9/表 10 的数据**。族 D（`20260924_threearm`）的 `random_s1/s2/s3` 带 `--random-order`，看似正好补"结构化 vs 随机"，但**实测复现失败**（`scratch/probe_famD_repro.py`）：结构化 s27 首次改善 **1 vs 30**、随机三种子均值 ΔWNS **0.40 vs 0.265**、混合 20 轮 **1.07 vs 0.285**。根因 = **运行器不同**（表 9 出 `code/scripts/run_hybrid_repair.py`（OI-012 已证）vs 族 D 出 `code/scripts/run_outerloop_real_wns.py`，`git_head` 亦不同）⇒ **硬族边界，禁止并表**。故表 11 采用族 D 独立口径并在表注显式声明「与表 9、表 10 出自不同运行配置，STA 计数不与表 10 的首次改善位置口径对应」。
3. **旁证 r9 纠错方向正确**：族 D 报告 `reports/FAECO_L2_THREEARM_20260924.md` 第 54 行「s641: 1→123；s713: 5→216；s953: 1→185」与 **v6 版 §4.4 原句完全一致** ⇒ 确认 v6 原句取自族 D，r9 改为同族族 C 三种子口径是正确处置。
4. **★ STA 计数口径对账（`scratch/reconcile_sta_counts.py`）**：`n_candidate_sta_runs` == `len(trials)` 即论文口径。§4.3 的 **3363** = 18 电路合计 3259 + **b17 的 180 s 重跑目录 `20260908_phase2_b17_resume/b17`（= 104）**（与正文"104 次候选级 STA 测量内取得 +0.38 ns"自洽）；表 12 的 **4044** = 同一 18 电路 + **b17 默认批次（785）**。差异**纯由 b17 目录选择造成**，均可追溯；`state.budget.sta_runs`（3401）**非**论文口径。
5. **落地 5 项（全部零算力）**：① **新增 §3.4 特征设计动机**（`sec:feature_motivation`）——逐项说明式 (2) 的边界/尺寸/验证/扇出/深度特征对应的预布局 ECO 风险，不引入公式证明，声明权重取固定值（默认 $1.0$）；顺带把原 §3.4 类型化失效归因顺延为 §3.5。② **新增 表 4** `tab:feature_motivation`（特征 ↔ 式 (2) 项 ↔ ECO 风险）。③ **§2.2 补整段「为什么无法直接定量比较」**（结构重映射依赖布局后负载与备用单元布局 / 逻辑补丁以 SAT·CEC 而非 WNS 为判据 / B/G 物理优化含学习驱动需训练环境与商用或内部流程）+ **表 2** `tab:baseline_cmp`。④ **§4.4 第二组补引导句 + 表 11** `tab:runtime`（族 D 三臂：固定权重 **4146 次/2010.8 s**、EMA 自适应 **4883/2065.3 s**、随机排序三种子均值 **5624/2460.3 s**；结构化较随机少 **26.3%** 次、少 **18.3%** 墙钟）。⑤ **§5 结论补失效统计句**（F4 占候选级评估 **60.2%**，与表 12 一致）。
6. **3 处硬编码 `§3.5` 改 `\S\ref{sec:validation}`**：插入 §3.4 后 §3.5 顺延，硬编码会失准（全库仅此 3 处，跨 2 行，已逐一核对指代同一小节）。
7. **质量门与终检**：**9 → 10 页** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox** / 0 undefined refs；`??`=0；逐页行数 `[52,68,65,74,35,60,67,68,72,52]`；表/图引用覆盖 **14/14 + 3/3**、编号阅读顺序 **1..14 / 1..3 全递增**（**加固版探针 `scratch/float_order_probe2.py`** —— 按 `.tex` 的 `\caption` 反查、按"最长可匹配数字前缀"解析编号，可排除行内引用与数字粘连）；论文 `.tex` `3bb99129…`；双副本 PDF 字节 SHA `6f27a08b…`；内容指纹 `96a2070f…`（poppler 25.07）。
8. **★ 版面调平（Overfull 归零，可复用经验）**：① 表 4「深度」行的不可断行数学 `$\lambda_c\,\mathrm{depth}/\mathrm{depth}_{\max}$` 撑破 `p{2.0cm}` → 列宽改 **1.3/2.6/3.0 cm**。② 余 `Overfull \vbox (0.95665pt)` 定位为 **`\balance` 末页（第 10 页）分栏溢出**：**试改 `\linespread{0.95→0.94}` 反而恶化至 1.55127pt**（证明行距不是正确杠杆，已回退）；**试注释 `\balance` 则全绿但末页右栏只剩 `[14]` 一条文献**（**正是 `\balance` 要防的缺陷 ⇒ 必须保留**）；最终**删除表 14 表注中与正文重复的一句**（释放 1 行）→ 全绿。③ 插入块曾引入 **60 处裸 LF**，已由 `scratch/fix_r10_eol.py` 归一化为纯 **CRLF 668/0**（`.tex` 必须纯 CRLF）。
9. **重冻结 v8（四要素）**：tag **`v2026-10-12-review-r10`** + 论文 tag **`faeco-paper-final-20261012b`** + `versions/v8/MANIFEST.sha256`（**117 条全 OK**，相对 v7 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变）+ `BASELINE_INDEX.csv` active 行（v7 → superseded）。
10. **台账收口**：`LOGS.md`（LOG-20261012-03/04）、`CHANGE_LOG.md`（r10 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增"当前发布版 v8"，v7 降为"前序发布版"）、`OPEN_ISSUES.md`（**OI-021 按 Elsevier 政策复核 / OI-024 扩到六张表 / OI-025 记 v8 / OI-026 记为"已获算力授权" / OI-027 更新为 10 页 / 新增 OI-028 目标期刊改判**）、`.workbuddy/memory`。
11. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF，SHA-256 与双副本一致（`6f27a08b…`）。

### 下一步（有明确指令再做）

- **OI-026（已获用户算力授权，"可以投入新的算力"）**：feature/cost 消融 —— **须先落方案**（`planning/`：消融臂定义 / 预锁定判据 / 族归属），再改 `code/src/rseco/flow.py:359/385` + `cut.py` 加候选源开关 + 单元测试，再跑 ISCAS89（估 **40–60 min**），结果入表并**重冻结 v9**。审稿人明示：补 runtime（已补）+ baseline 定位（已补）+ **feature 消融**可"明显提高一个档次"。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业规模 netlist）：需新基准接入 + 新算力；审稿人自注"不一定实现"。
- **OI-028 Integration 转化**：英文稿 + `elsarticle` 格式与投稿材料（中文稿作内容母本）；AIGC 披露按 Elsevier 政策复核（OI-021）。
- **绝对不要做**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（本轮已再次确认零数字改动）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（必须纯 CRLF）。

## 2026-10-12 — 复审三·针对性增强（r9，零算力项）+ r8 文字复审并入：重冻结 v7

**本轮性质**：用户提供第三方审稿意见（总判断「**不建议大改方法，而做针对性增强**」；核心诊断 = **论文声称的贡献强度 > 实验已经证明的强度**；归档 `paper/zh/review_rounds/r9_20261012/comments.md`）。用户四则裁定：① 执行范围 = **只做零算力项**；② 摘要 = **改口径并压回 150 词**；③ 版面 = **等内容定稿再统一排**；④ 搜索效率（k₁st）指标 = **同源重算 + 弱化主张**。同时把上一轮「已改但未冻结」的 r8 文字复审（21 行）**并入本轮**。**零数字、零实验、零代码改动**。记录见 `LOGS.md` LOG-20261012-01/02 与 `CHANGE_LOG.md` 两行。

1. **新增三张表**（数字**全部由既有台账现算**：`scratch/build_r9_tables.py` → `review_rounds/r9_20261012/table_data.json`）：**表 5** 三测试集总体结果（8/8、18/19、2/3；ΔWNS 均值/中位 0.16/0.10、0.43/0.18、0.60/0.60；SEC 8/8、19/19、2/2）、**表 8** 首次取得改善所需的候选级 STA 次数（结构化排序 vs 随机排序三种子）、**表 9** F1--F6 触发次数（19 电路 / 4044 次，138/3/16/2434/915/0，F4 占 60.2%）。表 9 须先套 **OI-008 事件名映射**（工具层 `acceptance_budget_violation` ≡ 方法层 F4）才与 `PAPER_EVIDENCE_MANIFEST.md:38` 逐项一致。
2. **摘要口径**：「以记录失效并调整搜索参数」→「**作为搜索诊断与消融分析的依据**」（+ 一句消融负结果）；中 **228 字** / 英 **149 词**（压回 JCAD ≤150）。
3. **§1.3 三贡献重组**：贡献 1 补"统计特征（边界、候选规模、验证代价、扇出）+ 关键路径特征（覆盖、逻辑深度）"；贡献 2 明确「**搜索诊断与候选控制**…而非独立的收敛增益来源」；贡献 3 补"统一数据流"与分层验证次序。
4. **§3.6** 补「在实际运行中，总运行时间主要由候选级 STA 测量与最终 SEC 决定，单次最小割求解所占比例很小」。
5. **§4.1 补运行环境**：WSL2 / Ubuntu 24.04.4 LTS / 内核 `6.6.87.2-microsoft-standard-WSL2` / **AMD Ryzen 7 7435H** / WSL 可见 16 逻辑核与 15 GB 内存。
6. **★ §4.4 k₁st 主动纠错（本轮最重要的一处；非审稿人提出，系自查发现）**：原句把 **族 C 的 ΔWNS（0.40 ns）** 与 **族 D 单种子（seed 1）** 的首次改善次数（s713 5→216、s953 1→185）并列——**跨实验族 + 单种子**，而表注写"随机列为种子 1/2/3 的均值"，即**该句口径与它所引的表格自相矛盾**；族 D seed 2 下 s713=5、s953=1（与结构化排序**相同**），单种子会翻转结论。经用户裁定改为**同族族 C 三种子口径**并弱化（7 个有台账电路 6 个优于随机均值；种子敏感最大相差 7 倍；s713 相反），**结论页口径同步**。证据 `review_rounds/r9_20261012/k1st_audit.{md,json}`（逐条回原始 `candidate_trials` 校验，非解析产物）。
7. **§4.5 物理口径弱化 ×2**：标题句去"物理验证"；段末补「本节的物理结果为基于布局与全局布线寄生估计的**后验评估**…**不等同于对物理实现有效性的验证**」。
8. **★ 补齐 4 张表的正文引用（投稿硬伤；非审稿人提出）**：`scratch/check_env_refs.py` 审计发现 **表 4/5/9/11 零正文引用**（其中**表 4、表 11 属 v6 既有遗留**——机械终检只查 `??` 与未定义引用，**不报"未被引用的 label"**）。已在 §4.1/§4.3.1/§4.6 各补一句，表/图引用覆盖 **14/14**。
9. **r8 并入（21 行）**：表 3 F5 行改"当前配置的单候选验证时限"、表 4 F1--F6 行「仅轮内」→「启用」、§1.3 导语去宣传语、§2.1 窗口表述、§4.4 补对照条件；**图 2 图注 A/B → $P_w$/$P_c$ 并同步重绘 imagegen 图源 PNG**（顺带消除 v6 遗留的图文不一致）。期间自查并修复本轮自造的 Overfull hbox（表 4 中列回退为「启用」）。
10. **质量门与终检**：**9 页** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox / 0 undefined refs；`??`=0；表 1--11 与图 1--3 **视觉顺序递增**（`scratch/float_order_probe.py`，按 `pdftotext -bbox-layout` 的 (页,栏,y) 判定）；14 `\bibitem` ↔ 14 `\cite` 且编号按首次引用顺序；双副本 PDF 字节 SHA `417398ab…`、内容指纹 `8c8fd2fd…`（poppler 25.07）；论文 `.tex` `4539efa4…`。
11. **重冻结 v7**：tag `v2026-10-12-review-r9` + 论文 tag `faeco-paper-final-20261012`（均 → 提交 `0602326`）；`versions/v7/MANIFEST.sha256`（**117 条全 OK**，相对 v6 **仅 3 条变化** = 论文 `.tex` + 双副本 `.pdf`）；`BASELINE_INDEX.csv` v6→superseded / v7→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v7 为当前发布版。
12. **00_Summary 同步**：新增 `tools/sync_to_summary.py`（幂等 + staleness 守卫 + SHA-256 回读）与 `Makefile` 的 `summary` 目标；本轮已把作者版 PDF 同步到 `01_Papers/00_Summary/`（`417398ab…`）。

**不要做**：① ⚠ **Word 转排件仍是 v6 版**（摘要与三张新表未同步）——投稿前**必须**随管线重建（**OI-024**），且 `postprocess.py` 的摘要/关键词为**硬编码**，须先同步为 v7 文本；② **不要再往正文插 `\FloatBarrier`**（导言区已有注记）；③ 页数 8→9 属三张新表所致（末页 81 行**满页、非孤儿**），**版式压缩留待内容定稿后统一排**（**OI-027**），不得为此缩字号/行距/裁内容；④ 加权割（cost）消融**未做**（**OI-026**），若做需先给 `flow.py:359/385` 加候选源开关 + 单元测试 + ~40–60 min 算力；⑤ **图源 PNG 不在 manifest 覆盖内**（**OI-025**，117 条口径不含 `paper/zh/figures/`），图 2 重绘只能靠 git 回溯；⑥ v7 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---
## 2026-10-09 — 文字专项审稿全量落地轮（r7）：重冻结 v6 + 末页孤儿修复 + Word 稿重建

**本轮性质**：用户提供外部 **FAECO 文字专项审稿**（全文文字级意见，归档 `paper/zh/review_rounds/r7_20261009/comments.md`），审稿人明确"不建议大规模重写、不要求新增实验、不直接改论文文件"。逐项核验后由用户拍板 4 项（摘要方向=**完全采纳审稿人**；执行范围=**全部执行 P0+P1+P2**；§4.6 口径=**采纳审稿人更保守写法**；A\* 可复现性披露=**按审稿人删除**），随后一次性落地全部意见，并修复文字收敛引入的**末页孤儿**。**零数字、零实验改动**，主张强度仅 §4.6 一处**下调**。

1. **P0×5（降主张/修事实）**：摘要"其余无退化"限定为**预布局理想线网 WNS** 口径；§4.1 删"保证不同基准电路均产生 setup 违例"（改述为严格时钟约束、非目标工作频率、不等价于时序收敛）；§4.6 由"枚举瓶颈已排除"下调为"本次扩大候选池未带来时序收益，尚不能排除更大规模扩展"；§3.1 拆开"候选的时序接受条件"与"对最终修复网表执行独立顺序 SEC"；§3.3 纠正事实性错误"缺少 R 等价候选的门不可重写"→"仅关闭 R 相关折扣，仍参与 G/B 候选生成"。
2. **P1×6**：§1.3 三项贡献重组；"20 轮收敛配置"→"20 轮迭代配置"（4 处）；§4.4 首现处补 $B(k)$ 定义（截至第 $k$ 次候选级 STA 的累计最优 WNS 改善曲线，对齐 `code/src/rseco/flow.py:1214`）；符号统一（`A(p)`→`\operatorname{Accept}(p)`、$S$→$S_2$、`\mathcal R`→$V_R$）；去工程日志式表述（子研究/台账/主力/拖高）；F1--F6 与物理门控按"一处定义、余处简引"收敛。
3. **P2×3**：表 1 表头"主要优势"→"主要技术特点"；§5 结论三段压两段；表 8 补 $\Delta_{\mathrm{WNS}}=0$ 行（36/126，使 $0+36+90=126$ 自洽）、§4.5 改题"物理时序评估与失效检测"。
4. **术语统一**：关键词/正文统一"**局部门级修改**"（英文同步 `gate-level local modification`，修 CN/EN 不一致）；"功能保持可用性"→"R 等价候选可用性"；"理想线网收益"→"理想线网 WNS 改善"；表 8"扩池"→"扩大候选池"。
5. **★ 末页孤儿修复（非审稿人要求，为消除本轮引入的版面退化）**：文字收敛后参考文献 [13][14] 被挤到第 9 页、该页约 93% 空白。实测归因：① 参考文献 `itemsep`/`\balance` 已无压缩余量（`footnotesize + linespread 0.95 + itemsep≈0`）；② 纯文字精简约 5 行**亦无效**——节省篇幅被第 3/5/6/7 页**栏底留白**吸收；③ **删正文 10 处 `\FloatBarrier`（双栏下遇待排浮动体会退化为 `\clearpage`）+ 去重精简 7 处 → 8 页**，且图 1/2/3、表 1--8 逐页分布与改前**完全一致**（无浮动体位移）。导言区已加维护注记防回退。图 2 图注 A/B 保持不变（已烧入 PNG，改则图文不一致）。
6. **质量门**：**8 页** / 0 Error / 0 Overfull / 0 Underfull；`??`=0；`\bibitem`↔`\cite` 14/14 且编号按正文首次引用顺序；字节 SHA `09197e5f…`（双副本一致）、内容指纹 `88b03403…`（poppler 25.07）；摘要中 228 字 / 英 148 词。
7. **重冻结 v6**：tag `v2026-10-09-text-review` + 论文 tag `faeco-paper-final-20261009c`；`versions/v6/MANIFEST.sha256`（117 条全 OK，相对 v5 变动 3 条）；`BASELINE_INDEX.csv` v5→superseded / v6→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v6 为当前发布版。
8. **Word 转排稿重建**：`word/FAECO_投稿Word转排_20261009c.*`（摘要与关键词改为**从 v6 `.tex` 抽取后写入** `postprocess.py`）；⚠ **同时修正上一轮管线缺陷**——`20261009b` 稿的摘要实为 v4 版（v5 轮重建时漏改 `postprocess.py` 硬编码的 `zh_abs`/`en_abs`/关键词），b 稿已归档 `word/superseded/` 并在该目录 README 写明作废原因。
9. **r7 归档**：`paper/zh/review_rounds/r7_20261009/`（`comments.md` 原文 + `response.md` 逐项核验与**执行记录** + `README.md` + `manuscript_before.tex` 改前 v5 主稿）。

**不要做**：① 论文内容修改仍按用户指令**终止**（本轮系用户授权执行外部审稿意见）；② **不要再往正文插 `\FloatBarrier`**（导言区已有注记）；③ 改正文后必须复核"图表是否仍紧跟其引用处"，并把页数/图表页码分布列入常规验收；④ 任何 `.tex` 摘要/题录改动**必须同步** `scratch/word_convert/postprocess.py` 的硬编码串（`preprocess.py` 的 `N_BIB` 守卫只管参考文献条数）；⑤ v6 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---
## 2026-10-09 — 摘要可读性改写轮：去术语 + 重冻结 v5 + Word 稿再重建

**本轮性质**：用户反馈"摘要太多技术要点、很难让大同行看懂"，授权改写。**摘要两段 + §1.1 引言首段**（`.tex` 两处），重编译 → 重冻结 v5 → Word 转排稿随管线再重建。**零数字、零实验、零主张改动**——正文、公式、图表、参考文献一字未动。记录见 `LOGS.md` LOG-20261009-04。

1. **去术语/缩写、只留概念**：删除 R/G/B/JOINT、F1--F6、多特征加权割、关键路径覆盖割、违例扇入锥、简化 SPEF 复测、独立全网表顺序等价检查、纯 G、WNS/TNS 等**未展开的机制名与缩写**，改为概念化表述（"按多种结构特征构造修改候选并统一排序""将候选失效归纳为若干类型""依次通过时序分析与等价性检查验证""仅门尺寸调整"）。
2. **补"为什么重要"**：首句点明时序 ECO 在芯片设计中的位置与预布局阶段约束（合法修改手段有限、候选空间大、验证代价高）。
3. **结果层保留主数字与诚实边界**：8/8、18/19、2/3；1.07 vs 0.16 ns；"无实例退化""尚未达到完全时序收敛"（替代"非 timing closure"）；结尾保留"单纯降低逻辑深度未必带来时序收益"。
4. **字数**：中文 **264 字**（原 298）、英文 **148 词**（原 150），均符合 JCAD ≤300 字/≤150 词；英文维持无第一人称。
5. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；字节 SHA `5c37725a…`（双副本一致）、内容指纹 `0a2b0723…`（poppler 25.07）。
6. **重冻结 v5**：tag `v2026-10-09-abstract-plain`（= 提交 `1c67f50`）+ 论文 tag `faeco-paper-final-20261009b`；`versions/v5/MANIFEST.sha256`（117 条全 OK，相对 v4 变动 3 条）；`BASELINE_INDEX.csv` v4→superseded / v5→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v5 为当前发布版。
7. **Word 转排稿再重建**：`word/FAECO_投稿Word转排_20261009b.docx` + `…_Word导出.pdf`（8 页，本机 Word 实测）；`postprocess.py` 摘要串同步、OUT 改 `…_20261009b.docx`；旧 20260930/20261009 两批归档 `word/superseded/`（README 说明作废原因）；`word/转排说明.md` 更新。

**正文刻意保留机制名**（R/G/B/JOINT、F1--F6 等）——摘要给大同行、正文给同行，这是本轮的设计取舍。

**不要做**：论文内容修改仍按用户指令**终止**（本轮改写系用户明确授权）；`sha256sum -c versions/v5/MANIFEST.sha256` 117 条应全 OK；v5 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---

## 2026-10-09 — 参考文献修复轮：重排文献表 + 重冻结 v4 + Word 稿重建（用户授权"方案 A"）

**本轮性质**：T20 检查单 #3 参考文献核对（`paper/zh/submission/REFERENCE_AUDIT_20261009.md`，LOG-20261009-02）发现 **1×P0**——参考文献编号未按正文首次引用顺序排列（首处引用渲染 `[1, 7, 9]`，18/19 条错位，违反 JCAD 规范一.1）。用户 **2026-10-09 授权"方案 A"**：从 `.tex` 源头修复 → 重冻结 v4 → Word 稿随管线重建。**零数字、零实验、零正文主张改动**——仅参考文献著录层。记录见 `LOGS.md` LOG-20261009-03。

1. **P0（编号顺序）**：`thebibliography` 由 19 条按正文首次引用顺序重排为 **14 条**；正文首处引用现渲染 `[1, 2, 3]`、全表按引用顺序递增。
2. **5 条纯 URL 工具/文档引用改正文页脚脚注**（JCAD 规范一.12）：picorv32 / yosys / OpenSTA / skywater-pdk（引用 2 次，含原 `liberty` 所指的 Liberty 文件句）→ 5 处 `\footnote{\url{…}}`；同时消除 `liberty`/`sky130` 的 bibitem-cite 不匹配。
3. **P1/P2 全处置**：会议文献 `[C] //` 空格（11 条）、期刊名 `Integration, the VLSI Journal` 全称、BUFFALO 题名补全（…`via group relative policy optimization`）、kravets 页码 `1-6`→`71:1-71:6`、`[Z]` 类型移出、DOI 中 `_` 转义（`6\_5`）。
4. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；正文无 `[15]`–`[19]`；字节 SHA `dea21bb3…`（双副本一致）、内容指纹 `6ca972d5…`（poppler 25.07）。
5. **重冻结 v4**：tag `v2026-10-09-reference-fix`（= 提交 `1d01881`）+ 论文 tag `faeco-paper-final-20261009`；`versions/v4/MANIFEST.sha256`（117 条全 OK）；`BASELINE_INDEX.csv` v3→superseded / v4→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v4 为当前发布版。
6. **Word 转排稿随管线重建**：`word/FAECO_投稿Word转排_20261009.docx` + `…_Word导出.pdf`（8 页，本机 Word 实测），5 条 URL 为 Word 原生脚注（落引用页页脚）；`preprocess.py` 守卫 19→14；旧 20260930 稿归档 `word/superseded_20260930/`（附 README 说明作废原因）；`word/转排说明.md` 更新至 20261009。
7. **T20 包同步**：检查单 #3 状态 → ✅ 已修；§3 登记新 Word 件字节 SHA256（docx `984cf0bc…`、PDF `4cf7dfd4…`）。

**不要做**：论文内容修改仍按用户指令**终止**——此后仅剩投稿手工项与审稿修稿轮（1-C 插入也在修稿轮，OI-018）；`sha256sum -c versions/v4/MANIFEST.sha256` 117 条应全 OK。

> **提交说明**：本轮 `1d01881`（论文制品 + v4 版本记录）已提交并打双 tag；后续文档同步提交见 `git log`。**注意**：v4 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---

## 2026-09-30（傍晚）— 终审修正轮：5 处正文一致性修正 + 冻结 v3（内容修改终止）

**本轮性质**：用户终审确认前 4 项一致性问题已改对，提出**最后 5 处正文修正**并明示"改完即停止内容修改、不加任何实验"。记录见 `LOGS.md` LOG-20260930-07。

1. **5 处修正全部落地**（零数字、零实验）：① §3.4 F6 交叉引用纠错（§4.4→§4.5）；② §4.1 接受准则复述闭合 b06 TNS 辅助接受例外；③ 摘要（中/英）PicoRV32 分母解释（`picorv32_regs` 无 setup path **不参与判定**，消除"其余 1 个电路"歧义；中文 298 字 / 英文 150 词）；④ 表 8 补 $\Delta L=L_{\mathrm{before}}-L_{\mathrm{after}}$ / $\Delta_{\mathrm{WNS}}$ 符号定义；⑤ §4.5 F6 措辞对齐"启用式反馈"口径。
2. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）；内容指纹 `70bbd610…`（poppler 25.07）。
3. **冻结 v3**：tag `v2026-09-30-submission-ready-r2`（= 提交 `26f4f3b`）+ 论文 tag `faeco-paper-final-20260930-r2`；manifest `versions/v3/MANIFEST.sha256`（117 条全 OK）；v2/v1 依次 superseded。
4. **Word 转排稿同步**：摘要串与正文 5 处随管线重建，Word 引擎重导出 8 页（首页目检通过）；`word/转排说明.md` 与 T20 检查单锚点已刷新至 v3。
5. **用户手工收尾清单不变**（`word/转排说明.md`）：MathType 转换 / 黄色占位 / 图 2 通栏 / AIGC 披露（OI-021，投稿时必须解决）/ 终稿 PDF。

**不要做**：论文内容修改已按用户指令**终止**——此后仅剩投稿手工项与审稿修稿轮（1-C 插入也在修稿轮，OI-018）；`sha256sum -c versions/v3/MANIFEST.sha256` 117 条应全 OK。

---

## 2026-09-30（下午）— 投稿执行轮：五项拍板落地 + 摘要适配重冻结 v2 + Word 转排完成

**本轮性质**：用户拍板 OI-018~022 后执行。记录见 `LOGS.md` LOG-20260930-05/06。

1. **拍板结果**：OI-018 1-C 留修稿轮；OI-019 直接转排（询问邮件作废删除）；OI-020 授权且同步冻结版；OI-021 AIGC 暂缓（**投稿时必须解决**）；OI-022 维持默认（manifest 锁定、不入 git）。
2. **OI-020 已执行**：中英摘要按 JCAD 改写（295 字 / 149 词，去第一人称），其余正文零改动；质量门 9 页 / 0/0/0；**重冻结 v2**（tag `v2026-09-30-submission-ready` = `4dc16c6`，新内容指纹 `43becd39…` poppler 25.07，v1 superseded）+ 论文 tag `faeco-paper-final-20260930`。
3. **OI-019 已执行（Word 转排）**：`paper/zh/submission/word/` 三件套——`FAECO_投稿Word转排_20260930.docx` + `…_Word导出.pdf`（**本机 Microsoft Word COM 导出，实测 8 页全对**）+ `转排说明.md`。管线：引用字面化预处理（式1-3/表1-8/图1-3/算法1/文献[1-19] 零未解析）→ pandoc（OMML）→ python-docx JCAD 版式（题录块单栏 + 正文双栏 continuous 同页、三线表、上标引文、首页脚注块）。**LibreOffice 预览的多栏表格竖排是其渲染局限**（XML 经探针验证合规），校对以 Word 为准。
4. **方正字体已装**（用户请求）：官方免费四款（书宋/仿宋/黑体简体，出版场景免费）经 AUR SHA256 校验装为用户级字体；docx 用免费版实名；GBK 版为商业字库（编辑部终排用自有正版）。
5. **用户手工收尾清单**（`word/转排说明.md`）：MathType 批量转换（OMML→MathType）、黄色占位替换（通信作者 \*/基金/日期/作者简介）、图 2 通栏、AIGC 披露（OI-021）、终稿 PDF 导出。

**不要做**：除上述用户手工项与审稿修稿轮外，不再改论文；LaTeX 冻结版与 v2 manifest 未动（`sha256sum -c versions/v2/MANIFEST.sha256` 117 条应全 OK）。

---

## 2026-09-30 — 补充材料成文轮（S1–S5 全部初稿完成）

**本轮性质**：T20 补充材料成文 + 台账更正，**未动论文、未改代码**。记录见 `LOGS.md` LOG-20260930-01..04。

1. **S1–S5 初稿完成**（`paper/zh/submission/supplementary/`）：S1 失效事件名映射（**OI-008 投稿前必办项就此闭合**）、S2 实验族与可复现性（功能差异命名脱敏）、S3 SEC 逐实例表、S4 环境工具链、S5 基准来源许可。清单与检查单状态已同步。
2. **更正两处过时表述**（均以实查为准）：① OI-008"当前 `code/` 已无旧事件名"——0a 合并（`258f588`）后 `real_wns.py:1864` 仍以 `acceptance_budget_violation` 写台账，正确表述是"工具层事件名 ↔ 方法层 F 分类"两层分工；② manifest §2 SEC 行"22 行 PASS"——实读 CSV 为 **29 PASS + 1 N/A = 30**，与论文口径闭合。
3. **缺口闭合**：PicoRV32 补建 source manifest（`picorv32.json`，clone HEAD `a473fc8f…`；`modules/` 三个 .v 为上游单文件的三份相同副本——易误判点已在 manifest/S5 写明）。
4. **待用户拍板不变**（OI-018~OI-022）：1-C 插入时机 / Word 转排路径 / 摘要改写授权 / AIGC 披露 / 3 个证据文件 git add。S2 的表述粒度亦待用户定。
5. 论文内容冻结未破（指纹 `7adf0279…`，poppler 25.07 口径，见经验库第 11 条）。

---

## 2026-09-29（晚）决策轮 — D-01~D-03 落地 + RESULTS.md 对齐 + T20 启动

**本轮性质**：决策执行 + 文档对齐 + 投稿准备，**未动论文内容、未动代码**。

1. **四项用户拍板**：D-01=A 轻量冻结 / D-02=A 维持 3 图 / D-03=A（DOI 投稿时补、DRC 如实声明）/ T20 目标期刊 = **JCAD（计算机辅助设计与图形学学报）**。
2. **D-01 落地**：tag `v2026-09-29-submission-ready`（`d84061a`）+ `versions/v1/MANIFEST.sha256`（117 条，`sha256sum -c` 全 OK）+ `BASELINE_INDEX.csv` 首个 active 行；已 push（3 个本地论文 tag 一并上 origin）。**附带发现**：`20260826_aggregation/summary.json`（论文主数字源）等 3 个证据汇总文件此前未被 git 跟踪，现由 manifest 锁定（OI-022 待用户定是否 `git add`）。
3. **RESULTS.md 对齐**（rev. 2026-09-29）：实查修正 3 处 headline 错误——ISCAS89 中位 +0.14→**+0.10**、ITC-99 中位 +0.21→**+0.18** 且 success 19/19→**18/19 严格改善**、PicoRV32 中位 +0.05→**+0.60**；§3 b06 补 TNS 辅助接受事实（WNS 持平、TNS −3.97→−3.92、`--tns-aware` 批次、不计入严格统计 = 论文 §4.1 口径）。依据：`20260826_aggregation/summary.json` 复算 + b06 `outerloop_result.json` 实读。
4. **T20 投稿包**（`paper/zh/submission/`）：`JCAD_REQUIREMENTS_20260929.md`（要求核实报告，✔/⚠ 标注 + 官网来源）、官方《投稿模板（2026）.doc》副本、`T20_SUBMISSION_PACKAGE.md`（检查单 + 4 个决策点）、cover letter 草稿、补充材料清单（S1=OI-008 事件名映射为投稿前必办）、`draft_email_to_jcad.md`（询问 LaTeX PDF 可否评审）。**核心事实：JCAD 无官方 LaTeX 模板，投稿须 Word(.doc)+PDF、公式 MathType、2026 起另要求英文长摘要（3 页，修改阶段）与 AIGC 披露。**
5. **1-C 评估完毕**：代码语义已在 `search_state.py` 落地并过 0a 等价门；§12.2 论文文本已备、§12.4 前置 gate（OI-013/OI-014/3-A）全清。剩余唯一动作 = 插入 `.tex`，**属内容修改，与冻结令冲突** → 默认留修稿轮（OI-018），待用户拍板。

**待用户拍板**（`OPEN_ISSUES.md` OI-018~OI-022）：1-C 插入时机 / Word 转排路径 / 摘要改写授权 / AIGC 披露口径 / 3 个证据文件 git add。

**不要做**：论文内容修改仍冻结（含摘要）；未拍板不发询问邮件、不启动 Word 转排、不插入 1-C 小节。

---

## 2026-09-29 — 论文终稿收敛 + 仓库收敛 + 版面收尾

**详细交接见 [`handoff_20260929.md`](handoff_20260929.md)**（本轮主文档）。要点：

1. **论文内容冻结**。终稿审稿轮三批修改全部落地：评审 15 项中优先 7 项（`681841a`）、评审第二轮 10 项（`0ea80b6`）、必改 4 项（`a8142b6`）。**用户明确要求此后停止内容修改。**
2. **版面回到 9 页**（0 Error / 0 Overfull / 0 Underfull）。根因是 `placeins` 的 `\FloatBarrier` 在**双栏下遇待排浮动体退化为 `\clearpage`**；删掉 §3.4 表 3 之后那一处多余屏障即恢复 9 页（第 5 页 = 图 2 + 正文 + 表 3；第 9 页 = §5 + 全部 19 条参考文献）。
3. **仓库收敛**：删 81 个历史 `.tex`（3.0 MB，`eaec1f4`→`ff6ed96`）与 82 个历史 PDF（119.4 MB，`973b325`→`3a8d1a7`）；删前均先固化进 git，可回滚。`paper/` 下现只有**唯一主稿**。
4. **发布冻结**：tag `faeco-paper-final-20260929`（`a8142b6`）；PDF 字节 SHA256 `9af41d77…`；**内容指纹 `7adf0279…`**（判内容一致看这个，不看字节 SHA）。
5. **机械终检全过**：`??` = 0、无未定义引用、29 个 label 无重复、19 条 bibitem ↔ 19 个 cite 一一对应。遗留 6 个未被引用的 label（无可见影响，按"停止内容修改"未动）。

**下一手要做**：① 用户对 D-01/D-02/D-03 拍板（见 `DECISION_BRIEF_20260912.md`）→ 落地执行清单 → T20 投稿件打包；② 1-C（技术设计 §12）未落地；③ `experiments/RESULTS.md` 待与论文新口径对齐（**均非论文内容修改**）。

---

# 历史轮次：2026-09-12 交接收尾（**以下内容为历史快照，勿作为当前状态**）

## 1. 项目概览

FAECO：面向预布局门级时序 ECO 的失效驱动候选搜索（中文论文 + Python 工程 + 公开 benchmark 实验）。
工作区：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（**唯一副本**，旧副本与 C 盘 worktree 已清理）；分支 main（与 origin 同步，HEAD f5b6380）；活跃基线待 D-01 决策后建立。

## 2. 本轮（2026-09-12 全天）做了什么

1. **上午**：robocopy 全量迁移仓库（316,765 文件 / 117.7 GB / 0 失败）→ 按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）→ 路径修复（pyproject / 12+ 硬编码脚本 / 31 个测试文件锚点 / .gitignore / README / .codex-handoff）→ pytest 264 全绿（35fd558）。
2. **中午**：`.venv` 重建 + 依赖安装（再次 264 全绿）；C 盘 3 个 git worktree 删除（3 条 codex 分支先推送固化，2 份未提交 phase2 文档抢救至 `../archive/phase0_worktree_salvage_20260912/`）；旧目录全删（f5b6380）。
3. **下午**：三项待决策事项编写决策简报（`DECISION_BRIEF_20260912.md`，含事实核实——主稿无 DOI 占位符、当前 9 页稿仅 3 图）；刷新 OPEN_ISSUES / TASK_BOARD / 全套交接文档。

## 3. 证据门（本轮验收，全部通过）

- [x] git 历史完整、main 与 origin 同步、3 条 codex 分支固化
- [x] pytest 264 passed + 4 skipped（迁移前后基线一致）
- [x] check_project.sh PASS；live 文件旧绝对路径残扫 0
- [x] 论文未动（9 页审计闭环状态保持）

## 4. 下一步（下一次接手者）

1. **先读** `README.md` → `START_HERE.md` → `DECISION_BRIEF_20260912.md` → `../OPEN_ISSUES.md`。
2. 用户对 D-01（versions/v1 冻结，建议轻量 tag+manifest）、D-02（机制图，建议维持 3 图）、D-03（DOI/DRC，建议维持如实声明）拍板后执行简报末尾的执行清单。
3. 之后进入 T20：投稿件打包（目标期刊模板 + cover letter + 补充材料清单）。
4. 环境：如 pytest 报 import 错误，先 `.venv\Scripts\python.exe -m pip install -e .`。

## 5. 不要做

- `experiments/` 证据严禁删除（OI-004 的 cleanup-candidates 档位须用户逐项确认）。
- 论文改动前先跑测试 + 数字对账；新审稿意见走第 19 轮流程，以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线。
- 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` 由用户手动删除。

## 6. 增量：2026-09-14 交接整理

- 补齐上轮交接缺口：未提交的交接文档 + `DECISION_BRIEF_20260912.md` 统一 commit+push；`NEXT_AGENT_PROMPT.md` 空模板补全（阅读顺序 / 本轮目标 / 约束 / 证据门）；`.codex-handoff.json` 刷新（timestamp + read_order 补决策简报）。
- versions/v1/ 核查为模板占位（待 D-01 决策后冻结，无动作）。
- 环境复验：pytest 264 passed + 4 skipped。项目状态与第 2~4 节描述一致，无其他变更。
