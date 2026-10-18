# START HERE — 当前2026-10-18

用户于2026-10-18明确“继续推进 做好记录”，当前授权为继续执行。唯一工作区 `D:/BaiduSyncdisk/01_Papers/03_FAECO`，当前main阶段提交为 `7231e0296da357df435414f75b0a41fe78265837`（941files），origin/main已实际push到7231e02（session60883 exit0）；C′原始source pin仍3ea0f75不回写。归档/图件审查已齐，当前进入S/SPEF修复计划先红后绿，生产可按明确文件归属改动，整体回归/独立review/源码新commit后才注册正式EDA；不恢复已结束的session9345。

**C′v3全72已独立验收。** `project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json`（SHA `a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738`）实核8电路×9臂、all_matrix_verified/source_stable/completion_set_frozen_at_start均true，72个当前completion SHA匹配。8458候选评估记录、6858 candidate_ideal STA+72初始baseline=6930实际STA过程，other0，192保留提交；每终点独立SEC均非零proven/0unproven。physical/electrical/S均false，不能称物理STA。最终审计exit0/runtime46.546s；剩54原运行wrapper3728s/exit0。stage72五件script/log/invocation/receipt/原运行log保真归档；旧51/54/v1失败/v2仅注册原件不覆盖。

当前接受协议是严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不关闭setup_tns预算。零收益与不利结果保留，不调参制造正结果。完整16个weighted/uniform配对已按所有重复同base轮独立核查，5454次交叉比较cut/pool/dispatch全同、16终点全文同（FIGURE_CPRIME_REVIEW269205b9…）；本矩阵未观察到独立权重收益，重复轮不是独立统计样本。新C′不替代旧B3/C/D。

完整v8历史收据为969pass/4skip/156subtests、170源码SHA稳定，OI040/041实现门closed；A6/B2/B17实际对象新证明已各自绑定原pin，B3主线51QA及C作者84/独立注册38QA、原OI042反例拒绝仅关闭工具实现门，尚未新clean pin正式登记同族EDA。四态支持仍open，实际三态/显式Z/switch须unsupported非pass。中英稿时钟元数据OI043已两遍编译/38p视觉/副本验收，仅设置说明门closed；科学回填和投稿声明仍待。

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

完整七段交接：`project_docs/agent_handoff/handoff_20261018_r22.md`。过程见LOG-20261018-01起；历史段只作历史，不能恢复已结束任务。

## 历史记录（含2026-10-14暂停前状态；不作为当前授权）

# START HERE

> r21 Git收口：实现提交 `e592bfd`、SVG导出规范化提交 `483b5e9` 已成功推送 `origin/main`（2026-10-14）。本轮审稿/配图/计数修复已完成，后续只处理保留的未决项；下文Git待办措辞为推送前记录。

接手者入口。**阅读顺序见 `README.md`**。最后更新：2026-10-14（r22_20261014，进行中）。

## 当前立即工作（r22，以本节为准）

- 用户继续授权恢复机制证据与投稿推进，旧r21暂缓只作历史；先读CURRENT_RUN_HANDOFF最上r22节、CURRENT_STATUS、TASK_BOARD、EXPERIMENT_REGISTRY、OPEN_ISSUES与EXPERIENCE。
- 源码/历史审计阶段28c3c2b已push，旧production644全回归+后加39组合门分别有证据。真实C′首pilot已执行两W0、最终SEC阻断，原目录完整保留，无有效新族结果；当前修复OI-035跨模块B插入/OI-036局部namespace伪pass。
- 修复后新commit/pin/v2与当前版本完整回归，重跑受影响矩阵；不要沿用旧源码通过或中间WNS，不拼旧C。不把records减launch称缓存：实读12/14和11/13、缓存0，各2条是F1前置拒绝。
- 当前中文12页/7图14表/21refs全门通过，三PDF e27eaf3a…/793545B。2994是有独有报告的候选STA结果，3363仍评估记录；不是全工具调用。英文27页首draft待视觉/事实核验，非提交件。
- OI-030/031/034/035/036开放；OI-032/033已修范围追踪。旧论文correctness受影响范围待审计，不推定全有效或全无效。主线负责稿/图/code/EDA/Git；专职记录只改记录文档。

## r21已完成提示（历史；旧暂缓不作为r22当前指令）

- 唯一工作副本 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，分支 main；本轮起始 HEAD `73dc0e7`、clean。当前是 r21 工作修订，**不冻结 v19**；v18 作为不可变参考保留。
- 用户授权论文审稿、配图修改/增加和必要图注/引用。五视角审稿已形成 Major Revision，图 1/2 重绘、图 4～7 新增、图 3 沿用，正文必要证据说明已修。
- 先读 `CURRENT_RUN_HANDOFF.md` 最上一节、`status_logs/CURRENT_STATUS.md`、`TASK_BOARD.md`，再读 `../evidence/PAPER_EVIDENCE_MANIFEST.md` 与 `../OPEN_ISSUES.md`。
- 本轮已验收稿 12 页/7 图/14 表/21 引用，质量项全零。逐页视觉/源字形/40账本审计通过，双PDF和作者版三份一致，文档与记录已完成；阶段commit+push待主线执行，最新状态只认最上一节，不套用下方旧 v18 状态。
- OI-030/031 机制与配置缺口、OI-034 历史计数审计继续开放；OI-032 批次披露、OI-033 D 真实计数修复已完成。B 的 3363/664/104 是评估记录，b17 实际 STA 未识别；不得再称真实测量。
- 不新跑 EDA；cost 消融、大规模验证、Word 转排继续暂缓；不擅自插 1-C，不删除证据。阶段 commit+push 依当前 AGENTS，旧“push 等用户”仅为历史状态。
- 图源验收须结合字节哈希和渲染；不能只看文本指纹。验收后的作者版按既有约定同步 `01_Papers/00_Summary/`。

## r20/v18 历史快照（下列冻结/推送安排不作为 r21 当前指令）

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的候选探索与失效刻画
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本）
- 分支：main；**v18 冻结终态 = v18 双 tag 所指提交**（`git rev-parse v2026-10-13-narrative-convergence-r20^{commit}`；r20 **单一提交**（13 处叙述层改写 + 台账/交接层同步），其后另有 tag 之外的簿记提交；前置 v17 终态 = `40eb8b8`、v16 终态 = `0000885`、v15 终态 = `49aa835`、v14 终态 = `4d5e511`、v13 终态 = `0a03841`、v12 终态 = `dfc0394`、v11 终态 = `d59e00f`、v10 终态 = `b1403d9`、v9 终态 = `e00315a`）；remote: https://github.com/Toylog123/FAECO.git（**v11 + v12 + v13 + v14 + v15 + v16 + v17 + v18 均尚未推送**——按项目惯例 push 等用户明确指令；v10 及以前已推送）
- 主稿件（唯一 `.tex`，**内容冻结 v18，内容改动留投稿/修稿轮**）：
  `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`
  **11 页 / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox**；内容指纹 `63e62c52…`（poppler 25.07）；第 11 页为参考文献孤儿页（版式压缩见 OI-027）
- 基线 tag：**`v2026-10-13-narrative-convergence-r20`**（四元绑定 manifest `versions/v18/MANIFEST.sha256`，117 条）；
  论文发布 tag `faeco-paper-final-20261013i`；前置 v17 = `v2026-10-13-positioning-r19` / `faeco-paper-final-20261013h`，v16 = `v2026-10-13-fig2-update-r18` / `faeco-paper-final-20261013g`，v15 = `v2026-10-13-logic-calibration-r17` / `faeco-paper-final-20261013f`，v14 = `v2026-10-13-terminology-calibration-r16` / `faeco-paper-final-20261013e`，v13 = `v2026-10-13-defensive-purge2-r15` / `faeco-paper-final-20261013d`，v12 = `v2026-10-13-defensive-purge-r14` / `faeco-paper-final-20261013c`，v11 = `v2026-10-13-abstract-broaden-r13` / `faeco-paper-final-20261013b`，v10 = `v2026-10-12-pre-submission-consistency-r12` / `faeco-paper-final-20261013`（= `b1403d9`）；实验 revision tag `faeco-exp-rev1`（= `87d01ba`）
- 投稿目标期刊：**Integration, the VLSI Journal**（Elsevier；由 JCAD 改投，OI-028）；旧投稿包 `paper/zh/submission/`（T20/JCAD 版，作历史参考）
- 实验入口：`experiments/INVENTORY.md`、`experiments/RESULTS.md`（rev. 2026-09-29 已对齐论文口径）
- 环境：`.venv`（Python 3.11.9）；pytest import 报错先 `.venv\Scripts\python.exe -m pip install -e .`

**版本定义**：代码/论文版本由具名基线（tag）决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **读 `CURRENT_RUN_HANDOFF.md` 最上一节**（2026-10-13 学术叙事收敛 r20（13 处改写））：**用户对作者版(7) = v17 的第五轮通读意见**（非外部匿名审稿，**不增实验**）。用户判断「整体框架已基本正确、主线比之前清晰很多」，本轮**「已经不是『需要重构』，而是『需要最后一次学术叙事收敛』」**；唯一核心 = **Candidate exploration under limited verification budget**，要求让所有章节回答同一问题「如何在有限验证预算下进行有效的预布局 ECO 候选探索」。用户裁定 3 项：核心问题句 = 替换为新句；贡献结构 = 2 条贡献 + 平台段落；§4.1 边界句 = 删除。**13 处改写**（E1/E2 摘要核心思想句 / E3 §1.1 核心问题句 / E4 §1.3 贡献分层 / E5+E6 失效反馈弱化 / E7 §4.5 标题 / E8 §5 结论 / Edel 删 §4.1 边界句）；全部唯一命中；**零数字/零实验/零代码/零参考文献**；页数 11（不变）。重冻结 **v18**；无新增遗留。
2. **当前最高优先 = OI-028：投 Integration, the VLSI Journal**——需**英文稿 + `elsarticle` 格式 + 投稿材料**（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；AIGC 披露改按 **Elsevier** 政策复核（OI-021）。
3. **已暂缓（用户裁定，勿擅启）**：OI-026 cost/feature 消融（**非投稿前置条件**，审稿人要求再做；方案见 `../planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7）、§七 大规模验证、OI-027 版式压缩。
4. **未同步项（投稿前必办）**：⚠ **OI-024 Word 转排件仍为 v6 版**，现缺 **r8–r20** 全部改动（标题/摘要/术语 + 六张表 + r12 的 15 处文本改动 + r13 的摘要两段 + §1.1 改写 + r14 的 10 处 + r15 的 11 处 + r16 的 17 处 + r17 的 12 处 + r18 的图 2 替换 + r19 的 12 处定位重构 + r20 的 13 处叙事收敛），且 `postprocess.py` 标题/摘要/关键词为硬编码，须随 `scratch/word_convert/` 管线重建并改输入新名；**OI-025** 图源 PNG 不在 manifest 覆盖内。
5. 若审稿意见返回：以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**先读 `../evidence/PAPER_EVIDENCE_MANIFEST.md`**，只处理新意见；新增内容修改须先取得用户同意（**1-C 插入留修稿轮**，OI-018）。

## 不要做什么

- **不要修改论文内容**（内容已冻结 v18）——任何内容改动（含摘要）须先取得用户同意，一切内容修改留投稿/修稿轮；Word 转排稿中的摘要改写也须先获授权（OI-020）。
- `experiments/` 证据目录严禁删除；`paper/zh/figures/fig_iscas89.pdf` 是编译依赖，亦禁删。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；引用任何数字前**实查证据文件**。
- 未跑测试不修改 `code/src/rseco/`。
- 双栏模式下 `\FloatBarrier` 遇待排浮动体会**退化为 `\clearpage`**（造成栏底留白 / 末页孤儿）；本稿正文已移除，仅保留图 2 后一处用于约束全宽浮动体。压页/版面异常**勿再插入 `\FloatBarrier`**——优先调浮动体参数，不要缩字体、行距或砍内容。
- 未拍板前**不要**发送 `draft_email_to_jcad.md`、**不要**启动 Word 转排、**不要**插入 1-C 小节。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（族 B；b17 phase-2 180 s 预算例外已披露）；§4.2 效率优先子研究（族 A，**revision 未完整钉定**）与 §4.4 消融（族 C/D）、§4.6 S 能力边界（族 F）是**各自独立配置，数字严禁互混**。
- 铁律：**`same claim ⇒ same revision + same config family`**；逐数字绑定见 `../evidence/PAPER_EVIDENCE_MANIFEST.md`。
- §4.1 已声明：**以 WNS 严格改善为主要统计口径**（ITC-99 = **18/19**，b06 的 TNS 辅助接受单独声明、不计入）；"WNS 严格改善"≠ timing closure；0.5 ns 为 stress-test 约束。**PicoRV32 = 2/2**（第三子模块无 setup 路径、不计入分母，r12 统一）。
- SEC：30 实例 29 修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**；无 DRC signoff（如实声明，D-03=A）。

## 构建与验收（论文）

见 `CURRENT_RUN_HANDOFF.md` 最上一节与 `versions/v18/README.md`：`cd paper/zh/manuscript` → `lualatex` ×2 → 质量门（`paper/zh/scripts/checks/latex_quality_gate.py`，Errors/Overfull/Underfull 须全 0）→ 双副本 `cp` + SHA256 核对 → 内容指纹（`pdftotext -layout … | sha256sum`，须用 poppler 25.07）。完成后按用户 standing 约定把作者版 PDF 同步到 `01_Papers/00_Summary/`。
