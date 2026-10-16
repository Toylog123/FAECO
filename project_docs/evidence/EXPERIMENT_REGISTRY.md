# 实验登记表

> 记录**所有做过 / 正在做的实验**，避免重复做。**做新实验前先查本表**。

**当前状态（2026-10-16）**：用户“继续”已恢复r22。起点main clean/781c031已push；K1–K6修复进行中，首整套741pass/1fail修后v2完整757pass/4skip/156subtests、162源码SHA稳定已通过；尚无新真实EDA结果。v1保持stopped且原件不改；新v2须修复版整套回归/独立复审后另锁source pin、配置、模型/库/输入/工具，再18pilot→72。旧667不能作当前版本验收。

## 登记表

| 实验 ID | 名称 | 版本 | 类型 | 实验定义路径 | 证据包路径 | 状态 | 关键结果 | 运行日期 |
|---------|------|------|------|-------------|-----------|------|----------|----------|
| EXP-001 | example_case | v1 | rtl | `experiments/v1/rtl/example_case/` | `evidence/v1/rtl/example_case/20260811_r01/` | 完成 | … | 2026-08-11 |

## 规则

1. **做新实验前**：先查本表 + `evidence/`，确认未做过（同版本 / 同配置 / 同输入）。
2. **每次实验完成后**：登记一行（或更新现有行），含实验定义路径与证据包路径。
3. 登记表与证据包**一一对应**，防重复、防混淆（版本 / 配置 / 结果）。
4. 查询：按实验名 / 版本 / 类型 / 日期搜索本表，或沿 `evidence/<版本>/<类型>/<实验>/` 定位。

## 与其它文档的关系

- 实验定义：`experiments/<版本>/<类型>/<实验>/`
- 结果证据：`evidence/<版本>/<类型>/<实验>/<YYYYMMDD>_r<N>/`（自包含包）
- 论文数字对照：`CROSSWALK_TEMPLATE.md`
- 分类规范：`../FILE_ORGANIZATION.md`

## 2026-10-14 既有记录重算（非新EDA）

| 登记ID | 类型 | 输入 | 输出 | 结果 |
|---|---|---|---|---|
| DERIVED-R21-STA | 原始台账审计与重绘 | B/D/F既有实验族，r21_source_manifest绑定输入 | r21_20261014/sta_ledger_audit.json、sta_count_followup.md及图件CSV | D 40/40通过，固定/EMA新STA1947/2003，随机均值2480.7；B旧schema不补猜测 |

## 2026-10-14 r22 实验规划与执行登记

| 规划ID | 目的 | 起始版本 | 配置/输入 | 定义/证据路径 | 状态 | 结果 |
|---|---|---|---|---|---|---|
| PLAN-R22-CUT-COST | 新族C′，同运行器双割/cost/顺序可辨识对照 | 起始46ede94；首源码阶段28c3c2b已push，修复工作区尚未新pin | W0/W1/U0/U1/C/UR1/2/3/L九臂×八电路；首manifest锁72commands/8原始input SHA/LIB与工具；0.5ns/20轮/候选STA500/k8/joint_k2/workers1，不拼旧C | `project_docs/planning/R22_EVIDENCE_CLOSURE_PLAN_20261014.md`、`experiments/20261014_r22_cut_ablation/manifest.json` | **resumed；v1失败保留，v2新pin8192193/dryrun72已注册，18pilot待** | 无有效C′结果；原失败目录保留 |

本规划获得用户r22“继续推进”新授权，覆盖旧消融暂缓安排。正式运行前必须更新真实revision、输入、参数、超时和预锁判据；运行后按实际证据登记，不补写推测结果。

### r22 已执行静态探针（非EDA）

| 登记ID | 版本/输入 | 定义与证据 | 状态/结果 | 边界 |
|---|---|---|---|---|
| PROBE-R22-LEGACY-GATING | 46ede94；六门DAG g1→g4、g2→g4/g5、g3→g5、g4/g5→g6；critical=[g1,g4,g6]、R={g1,g4}、其余λ=0，比较λc=0/1 | `project_docs/planning/R22_ABLATION_DESIGN_REVIEW_20261014.md` §2，领域评审python -B只读/无文件写出 | **已执行**；旧nonconstrained两λ均cover优先且混备用源，constrained cover在λ=0时第5、λ=1时第1 | 只检来源/门控混杂，无Yosys/OpenSTA，无时序或性能结论；其余12项建议探针未执行 |

### r22 历史派生审计（非EDA）

| 登记ID | 输入/版本 | 输出/执行 | 结果与边界 |
|---|---|---|---|
| DERIVED-R22-HISTORICAL | 既有C六配置臂与b17 180s报告档案；26240文件/git blob指纹，不改变原始数据 | `evidence/r22_historical_audit_20261014/`、`code/scripts/python/audit_historical_evidence_r22.py`；300s timeout，51s/exit0 | b17报告级恢复104，ITC-99独有报告结果2994；C flags/argv/revision分级，完整身份仍缺，s382 v3不自动借用；不运行EDA |
| DERIVED-R22-CORRECTNESS | A/B/D/k1与C12代表已归档accepted/final、SEC脚本/log/gold/gate；410来源/依赖SHA，r21匹配42与既往r22匹配22 | `evidence/r22_historical_correctness_20261014/REPORT.md`、correctness_audit.json/input_hashes.json/audit.py；只读派生审计，无EDA、未改原数据/稿/production | **报告已实读确认；2026-10-16恢复后续处置**：B完整绑定28/unknown2；A exact可复用2/缺证6；D结构invalid38/40、k1 14/16；C代表结构invalid9/12/unknown3不外推。invalid不推断已证明不等价，unknown非失败；非新SEC/时序实验 |

### r22 预检（未启动电路EDA）

| 登记ID | 输入/输出 | 执行结果 | 边界 |
|---|---|---|---|
| PREFLIGHT-R22-72 | `scratch/r22_preflight_config`，正式计划九臂×八电路配置；执行源码尚未最终冻结 | nativeYosys0.67+146 git468ba27d9dirty/OpenSTA3.1.0/SECYosys0.33版本校验成功，72配置注册 | dryrun只配置与工具版本，不mapping/STA；不当正式运行、不填性能结果，最终源码回归待完成 |
| DRYRUN-R22-LOCKED | `experiments/20261014_r22_cut_ablation/manifest.json`；actualgit28c3c2b、production SHA、8原始输入SHA/LIB、72完整命令 | 三工具版本锁；配置清单已注册 | 仅正式路径的locked dryrun，无mapping/STA；尚未正式执行72运行 |

### C′正式登记（首pilot已执行，SEC失败停止）

| 实验ID | 族/版本 | 输入与配置 | 定义/证据目录 | 状态/结果 |
|---|---|---|---|---|
| EXP-R22-CPRIME-72 | C-prime-r22；首执行git28c3c2b，逐文件SHA锁 | 八ISCAS89原始input SHA/LIB SHA；W0/W1/U0/U1/C/UR1/2/3/L，72完整commands；500候选STA/20轮/k8/joint_k2/workers1等由首manifest决定，3900s包装/3930s硬超时；三工具版本/Python3.11.9 | `experiments/20261014_r22_cut_ablation/manifest.json`及W0/s27、W0/s382、batch_failures.json；预锁计划见R22_EVIDENCE_CLOSURE_PLAN | **stopped（v1失败历史，恢复不重开原目录）**；两pilot SEC失败batch58s/exit1，其它臂未启动；无v2开跑/有效结果。新v2须修复验收后新pin、完整受影响矩阵 |

每个pilot/正式run以该manifest中的真实命令为定义；开跑与完成需逐项补真实时间、退出码、停止原因及证据，不由dryrun注册数推算执行数。若production/config改变，先新钉版本/清单，不沿用此条假称同一对象。

首轮pilot实际命令：`.venv/Scripts/python.exe -u -X utf8 code/scripts/run_r22_cut_ablation.py --output-dir experiments/20261014_r22_cut_ablation --circuits s27,s382`，session66717，batch wrapper43200s。共享mapping2例后仅W0两run启动：s27 runner47s/exit0、s38248s/exit0，最终独立SEC发现helper definitions变化，batch58s/exit1并停止。两run中间WNS不计有效成果。实读STA launch12/11、评估14/13、缓存0/0，差额各2为F1前置拒绝。归因与修复见OI-035/036、LOG-20261014-23；尚无v2正式开跑。


## 2026-10-14 r22用户暂停（不新增实验）

正式v1仅W0/s27、W0/s382，SEC输入helper改变门失败；原目录完整保留。已归档109原文件ZIP与逐文件SHA：r22_preflight_20261014/failed_v1_pilot_snapshot.zip、pause_snapshot_manifest.json。最后全回归667/4skip/156subtests；K1–K6待修，v2未注册/未运行。历史A/D/C审计REPORT已主线确认，不以计数恢复证明合法终点。等待用户明确恢复。


## 2026-10-16 r22恢复登记（尚无新实验执行）

| 登记ID | 类型 | 被测版本/输入 | 定义/证据 | 状态/结果 |
|---|---|---|---|---|
| RESUME-R22-20261016 | 恢复授权/计划状态，非实验 | 起点main clean/781c031已push；当前K1–K6修复中，正式被测源码/模型尚未新锁 | `../agent_handoff/handoff_20261016_r22.md`、`../planning/R22_EVIDENCE_CLOSURE_PLAN_20261014.md`；复用r22_preflight_20261014/NAMESPACE_FIX_REVIEW | 已恢复；无本轮新EDA/SEC/全回归成果，不新增虚拟执行记录 |
| PLAN-R22-CPRIME-V2 | 新C′恢复后矩阵计划 | 修复验收source pin8192193，44source/库/输入/工具锁；不复用v1 pin | experiments/20261016_r22_cut_ablation_v2/manifest.json，72完整commands正式dryrun已注册 | superseded/禁止执行已知缺陷pin；OI-039新反证须修复+新整套/pin并另建v3；v2从未mapping/STA，原manifest保留 |

A六接受对象确切证明与D/C同族恢复，待对象/配置及实际命令确定后分别运行前登记；不与C′合并。旧10-14暂停及所有真实失败记录保留为历史，不重复执行已有来源审计。

### 2026-10-16 修复限定验证（非EDA，不代表整套回归）

| 登记ID | 被测范围/输入 | 命令与证据 | 实际结果/边界 |
|---|---|---|---|
| CHECK-R22-K2-PARSER | 当前K2 parser输出/命名端口/assign别名三测试文件 | scratch/r22_resume_20261016/k2_parser_final_green.log：pytest test_r22_cell_outputs/test_named_port_parser/test_assign_alias_parser；timeout120s | 35passed/1.03s，wrapper5s/exit0；无EDA，非完整回归 |
| CHECK-R22-MODELS | 当前模型/real_wns/namespace/static action四文件 | validation_models_final_related.log；timeout180s | 69passed/10.03s，wrapper15s/exit0；无真实SEC，未用此关闭全部K门 |
| CHECK-R22-SCOPE | 当前graph/cut、CLI/flow、批次SEC及7个相关测试文件 | scope_red.log先4fail；sec_module_red.log假module先1fail；scope_final_green.log最终，timeout120s | 63passed+1subtest/3.85s，wrapper5s/exit0；test修复在当前工作区，不是完整source pin/整套验收 |

主线说明parser/models已冻结，继续整体回归/独立审查；A六确切对象工具准备尚未运行EDA。相关日志由记录员实际读取；完整命令见日志头，不合计三次计数充当全回归数。

### 集成复审追加与A工具准备（LOG-20261016-05）

| 登记ID | 被测范围/输入 | 命令与证据 | 实际结果/边界 |
|---|---|---|---|
| CHECK-R22-SCOPE-REVIEW | source/alias/cone外次输出与split边界；lib metadata真实属性lib | integration_review_red.log 3fail/6pass、split_external_red.log 1fail；scope_final_green5.log timeout120s | 最新68passed+1subtest/3.71s，wrapper5s/exit0；替代63+1为最新限定状态，不覆盖旧真实记录；整体门待 |
| CHECK-R22-A-RECOVERY-TOOL | A六确切accepted对象绑定/工具；s713原A→fixed主pair覆盖tie变化 | a_sec_recovery_green.log，pytest test_r22_a_sec_recovery.py；timeout120s | 9passed/0.97s，wrapper5s/exit0；工具验证，不是6对象实际SEC |
| DRYRUN-R22-A-RECOVERY | r22_a_sec_20261016/input_manifest.json，6cases/52input SHA/44source SHA；HEAD781c031，source_tree_clean=false | code/scripts/python/prove_historical_a_r22.py --dry-run --manifest project_docs/evidence/r22_a_sec_20261016/input_manifest.json；a_sec_recovery_dry_run.log，timeout120s | wrapper6s/exit0，eda_executed=false；工作区快照，尚非已提交新pin或实际证明 |

2026-10-16主线宣布production/tests冻结，完整回归准备中；正式stdout/JUnit/被测SHA证据目标为r22_correctness_20261016，启动/结束事实待追加。新A实际证明与C′v2/历史D/C仍需分别登记运行前真实对象/配置。

### 完整回归运行中（LOG-20261016-06）

| 登记ID | 被测版本/设定 | 命令/证据 | 状态/结果 |
|---|---|---|---|
| CHECK-R22-FULL-20261016 | 起始HEAD781c031；工作区当前production/tests冻结，beforeSHA见json | Git Bash run_with_timeout.sh 300 .venv/Scripts/python.exe -m pytest code/tests -q --junitxml=project_docs/evidence/r22_correctness_20261016/full_regression.xml；full_regression.json/.log；session63511 | completed/failed；741passed/1failed/4skipped/156subtests、108.20s、wrapper112s/exit1；before/after SHA稳定。合法B声明重组被新_non_rgb_structure误拒，归因实现兼容性错误，修复后新v2全回归，不覆盖原三证据 |
| PROBE-R22-INTEGRATION-FROZEN | 最终冻结7生产文件before/after SHA一致 | INTEGRATION_REVIEW.md/.json最终冻结节、integration_review_final_frozen.log；timeout60s | 约5s/exit0；原source/metadata/alias/secondary/split及S/top/SEC/helper控制符合；无EDA，不代替整套 |

### 首完整回归归因与新版计划（LOG-20261016-07）

唯一失败为既有合法B buffer-chain测试，wire N;扩为wire N,N_BUF;被整条声明Counter误判已有N删除；models只修_non_rgb_structure，net宽度/signedness不变、允许分组/合并/新增线，不能改旧fixture凑过。专属限定通过后冻结新版，完整回归另用full_regression_v2.{json,log,xml}，运行前补当前被测SHA。旧完整回归已真实失败，不用限定或独立probe覆盖其失败状态；尚无A实际SEC/v2 EDA。

### 声明修复与完整v2执行（LOG-20261016-08）

| 登记ID | 被测对象/输入 | 命令/证据 | 状态/实际结果 |
|---|---|---|---|
| CHECK-R22-WIRE-REGROUP | _non_rgb_structure声明语义兼容，15参数例检查宽度/signedness/次数，原sole failure保留 | validation_wire_regroup_red/green.log；pytest validation_models/real_wns/module_namespace/static_action_gates/sol_review_residuals，timeout180s | 红7fail/8pass/27deselected→绿145pass/22.28s、wrapper26/exit0；限定非整体 |
| CHECK-R22-FULL-V2-20261016 | production/tests重新冻结、162beforeSHA、HEAD781c031工作区修后对象 | full_regression_v2.json/.log/.xml；pytest code/tests -q --junitxml=…/full_regression_v2.xml，timeout300s/主线外330s；session54033 | completed/passed；757pass/4skip/156subtests，102.50s、wrapper107/exit0；162源码before/after SHA一致source_stable=true；独立前缀保留首失败三证据 |
| PLAN-R22-SEC-MODEL-CONTROLS | conb双输出/错误交换HI-LO、fa手写真值/保持SUM而错误COUT | r22_correctness_20261016/sec_model_controls.py（证据目录工具，非production） | running；整套757pass后8192193已push，timeout1200s/逐case180s；首读tie正pass/错接fail符合预期，6组未核齐，无STA |

D56配置/C未知边界与B历史模型完整性仅只读恢复设计；B28已归档对象绑定与实际旧模型语义应分别核查，不能由新writer改动外推历史B失效。

### 完整v2验收与B2新证明待办（LOG-20261016-09）

当前完整修复版本已通过，不升级科学结论。主线实际审计发现B两Pico旧proof使用edfxtp_1不完整IQ模型，登记OI-038；B28对象绑定仍真，26其它对象与2项新语义缺口分开。models补正式报告后记录员实读；后续新库/source pin对B2实际final独立SEC，与A6分别登记，旧证据不修改，当前未实际运行SEC/EDA。阶段commit/pin准备，记录员本轮停写等待Git事实。

### 正式SEC控制运行登记（LOG-20261016-10）

| 实验ID | 版本/输入/配置 | 命令/证据 | 状态/结果 |
|---|---|---|---|
| SEC-R22-MODEL-CONTROLS-20261016 | pin81921932d9348408e237edfa13a42257a43007f2，LIB ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9；6组conb/fa/edfxtp DE正负对照，source manifest与脚本SHA在controls.json | .venv/Scripts/python.exe -u -X utf8 project_docs/evidence/r22_correctness_20261016/sec_model_controls.py；timeout1200s/逐case180s；sec_controls_run.log、sec_controls/controls.json与逐组SEC产物 | completed/passed；6expected全部匹配：3正pass/3故意错误fail（含edfxtp DE），source_stable=true、wrapper15s/exit0。真实SEC工具执行，无STA，不当时序结果 |

主线阶段commit/push8192193、82files完成，记录员只读实查main/origin refs一致；757被测162源码SHA由主线提交前逐项再匹配。A6/B2实际接受对象与v2 pilot仍未运行，后续分别登记。

### A六实际对象证明与C′ v2锁定（LOG-20261016-11）

| 实验ID | 版本/输入/配置 | 命令/证据 | 状态/结果 |
|---|---|---|---|
| DRYRUN-R22-A-FROZEN | pin8192193、source_tree_clean=true，6cases/原A gold→accepted fixed、输入/库/源码SHA | r22_a_sec_20261016_frozen/input_manifest.json | 正式frozen输入准备；eda_executed=false仅描述该manifest创建时dryrun状态，不用于否认随后实际proof |
| SEC-R22-A6-FROZEN | s382/s420/s641/s713/s832/s953实际原A mapped→accepted fixed；pin8192193、实际库SHA；逐case前后输入/源码校验 | prove_historical_a_r22.py --manifest project_docs/evidence/r22_a_sec_20261016_frozen/input_manifest.json --output-dir …/proofs；proof_run.log/各receipt+sec.log；timeout1500s/每case180s，session45026 | completed，6/6pass、wrapper21s/exit0，真实Yosys SEC，无STA；s713 LF→CRLF字节差经通用换行逐字一致核验 |
| DRYRUN-R22-CPRIME-V2 | pin8192193、44source SHA、9arms×8circuits=72commands、输入/LIB/tools锁 | experiments/20261016_r22_cut_ablation_v2/manifest.json | 正式dryrun已注册但8192193已识别OI-039，不执行；无mapping/STA，原manifest/v1保留，新源改v3 |

A六确切归档对象新证明补齐，历史runtime hash不补造、稿图回填仍待。B2尚未新模型重证，OI-038及D/C科学恢复开放，不由A或控制通过外推全部科学结论。

### 新三态语义反证与v2停用（LOG-20261016-12）

| 登记ID | 类型/来源 | 实查结果 | 后续/边界 |
|---|---|---|---|
| AUDIT-R22-B-USED-MODELS | 只读历史actual SEC模型/Lib输入审计，r22_b_model_audit_20261016/audit.json | 旧28完整对象绑定仍真，23未见本次used-model defect/5有缺口（B3三态+Pico2）；133 used types，einvn_1/_2实际three_state与缺TE_B已列 | 非新SEC/STA，不先判电路不等价；OI-038/039开放，历史runtime模型hash限制保留 |
| PLAN-R22-CPRIME-V3 | 新源修复后独立目录计划（精确pin/路径/命令待主线登记） | OI-039修复及新当前源码完整回归/commit/pin之前不能启动 | v2只有dryrun未mapping/STA、manifest不改；v3同预锁18pilot→72，不按正向结果调臂 |

旧8192193整套757与6模型控制通过是该版本真实结果，不覆盖新three_state反证。A6真实pass保留在其旧模型/source pin边界下，usedtypes复核待；当前无STA或pilot运行。

### 三态限定独立复核（LOG-20261016-13，非EDA）

| 登记ID | 被测对象/输入 | 定义/证据 | 实际结果/边界 |
|---|---|---|---|
| PROBE-R22-TRISTATE-INDEPENDENT | 其它作者logic_rewrite联合data/enable语义与batch final_sec required-input接线；实际13three_state及构造映射/缺输入控制 | TRISTATE_INDEPENDENT_REVIEW.md/.json；scratch/r22_tristate_20261016/independent_review.py，timeout120s | 16s/exit0，5来源SHA前后一致；合法只到被sentinel拦截的subprocess、缺输入先拒，无EDA；不独立认证审查者自己的RW writer |

作者自审发现actual4个einvp使用(TE')，RW writer字符串转换导出非法，另TDD修复待；这属于OI-039，非上述独立probe通过所覆盖。新writer全库导出/真Z正负控制/完整回归与新pin仍待；C′v2禁执行、v3仅计划，无STA。

### 第二批冻结与三态诊断前登记（LOG-20261016-14）

| 登记ID | 被测范围/输入 | 证据/执行设定 | 当前结果/边界 |
|---|---|---|---|
| CHECK-R22-TRISTATE-RELATED | actual Liberty metadata/候选联合语义/RW writer及局部门；含后缀反相 | liberty_final_green13pass/1.59s；rw_final_related174pass/39.50s；postfix_final_related187pass/44.27s/wrapper46exit0；final_sec_inputs_green24pass/9.76s | 限定相关通过，各范围不合计为整套；新整体v3待 |
| PROBE-R22-ALL13-POSTFIX | actual13三态、52binary输入行，真实writer内存边界 | scratch/r22_tristate_20261016/postfix_all13_probe.json | 静态生成语义检查，eda_executed=false；不代替真实工具Z支持 |
| CHECK-R22-D-REVALIDATION-TOOL | D同族复验控制/失败receipt测试工具 | d_revalidation_final_green.log，timeout180s | 20pass/8.42s、wrapper10exit0；工具测试非D实验已重跑 |
| AUDIT-R22-A6-TRISTATE-IMPACT | frozen六实际A proof pair与actual13三态types | r22_a_sec_20261016_frozen/TRISTATE_IMPACT_CHECK.json | 六pair交集逐一空，保留各自来源/模型下真实proof，不补历史runtimehash |
| PLAN-R22-DIRTY-TRISTATE-DIAG | 第二批production/tests已冻结、dirty工作区；确切source SHA/命令由主线诊断入口保存 | 即将真SEC正负三态诊断（非STA），随后完整v3 | prepared/结果待，不预填工具通过/失败 |

### dirty三态真实诊断与完整v3运行（LOG-20261016-15）

| 登记ID | 对象/配置/来源 | 实际结果 | 边界/后续 |
|---|---|---|---|
| DIAG-R22-TRISTATE-TOOL-DIRTY | HEAD8192193+第二批dirty source44SHA，diagnostic_only=true、timing_runs=0；tristate_tool_diagnostic/diagnostic.json | 5matches：2正pass/2负fail/1input_error，source_stable=true；主线包装20s/exit0 | 首组不能认证Z soundness，见更强反例；非正式新pin/无STA |
| DIAG-R22-Z-SOUNDNESS-DIRTY | 同冻结源码，tristate_z_diagnostic/diagnostic.json，Zvs常量0与1应均fail | Zvs0实际pass/return0/matches=false，Zvs1fail符合；source_stable=true、passed=false；主线包装11s/exit1，0timing | 当前Yosys默认Z塌缩，OI039新增工具阻断；只读composition boundary proof设计，不改生产 |
| CHECK-R22-FULL-V3-20261016 | 第二批冻结，165beforeSHA、HEAD8192193工作区修后对象 | full_regression_v3.json/.log/.xml目标；json running，stdout至少2F、首读至59% | completed/failed：822pass/2fail/4skip/156subtests、144.12s/wrapper147.735exit1，165before/after SHA稳定；两CLI fixture缺dfrtp/RESET_B被正确拒，修fixture后新v4未开始 |

### 完整v3失败归因与能力门限定验证（LOG-20261016-16）

| 登记ID | 对象/证据 | 实际结果 | 边界/后续 |
|---|---|---|---|
| CHECK-R22-CLI-FIXTURE-RED | 两旧CLI测试，cli_fixture_red.log；新必需输入门 | 2fail/0.77s/wrapper5exit1，复现缺dfrtp模型/RESET_B导致正确前置拒与lazy baseline None | 补真实fixture保留assert，不改门凑过；非STA实验 |
| CHECK-R22-SEC-DOMAIN | actual三态cell、显式Z/switch不进入不可靠二态证明器 | sec_domain_red5fail/0.57s→green含scope16pass/9.57s；sec_domain_extended11pass/0.28s | structured unsupported非pass是临时能力门；准确writer保留，显式四态编码恢复支持open，完整v4未开始 |
| AUDIT-R22-MATRIX-TRISTATE-SCOPE | TRISTATE_MATRIX_SCOPE_CHECK.json；B2四raw、D56保留输入/8独有SHA、共享canonical8已存在 | 已有对象三态交集空；v2八prospective mapped不存在→unknown | 只读非EDA；不能把已存raw结论外推未来mapped/candidate；无STA/pilot |

v3原混编码log保真；harness UTF8展示解码异常不否定已保存JSON/JUnit，记录员从原bytes核计数。后续Python -Xutf8。二态cut组合方案被独立Z^Z等反例推翻，未实施；不能把临时unsupported称为三态已证明。

### 拒绝门核验与完整v4编码环境（LOG-20261016-17）

| 登记ID | 对象/证据 | 实际结果/状态 | 边界/后续 |
|---|---|---|---|
| VERIFY-R22-TRISTATE-GUARD | tristate_guard_verification/verification.json复用历史Zvs0/1精确输入及SHA | 2均unsupported，command=None/runtime0，source_stable=true/passed=true | 外部工具未启动；拒绝门核验非四态等价证明 |
| CHECK-R22-CLI-FIXTURE-GREEN | cli_fixture_green.log，真实dfrtp/RESET_B fixture、旧assert保留 | test_outerloop_cli全9pass/0.71s，wrapper6exit0 | fixture/test已冻结，不改生产门 |
| CHECK-R22-FULL-V4-20261016 | full_regression_v4.json/.log/.xml目标，166beforeSHA、源码冻结 | completed/failed：832pass/3fail/4skip/5warn/156subtests、148.38s/wrapper152.968exit1、166SHA稳定；3F均父UTF8/子CP936环境 | 等完整结束保留，不能预填整体计数/通过 |
| CHECK-R22-UTF8-PROCESS-ENV | utf8_environment_red/green.log；3个子CLI测试，源码不改 | 红3fail+4warn/0.97s→PYTHONUTF8=1传全进程绿3pass/0.82s | 仅scratch harness修环境，完整v5拟在v4结束后显式记录PYTHONUTF8=1 |

### 完整v4结束与显式环境v5运行（LOG-20261016-18）

| 登记ID | 对象/证据 | 实际状态/结果 | 边界/后续 |
|---|---|---|---|
| CHECK-R22-FULL-V5-20261016 | 166beforeSHA、源码未改，full_regression_v5.json/.log/.xml目标；environment_overrides PYTHONUTF8=1传全children | completed/passed：835pass/4skip/156subtests、147.00s/wrapper152.781exit0、166before/after SHA稳定/PYTHONUTF8=1；JSON/XML/log实读 | 尚无最终结果，v4原失败保留，v5过后才阶段commit/pin |
| ARCHIVE-R22-PHASE2-TDD | phase2_tdd/ARCHIVE_MANIFEST.json，scratch晋级58文件 | source/target/manifest SHA记录员逐条实际核验58/58 | 归档动作非新测试/EDA，不把晋级计为运行 |
| AUDIT-R22-B2-X-BOUNDARY | phase2_tdd/b2_explicit_x_refs.json +主线双agent只读审查 | core7X无cell/alias消费者、mul0X已读；主线通报2直连恒X PO同句/宽/roles | identitychecker待可重复绑定B2正式proof，二态SAT不升级一般四态认证；未实际新B2证明 |

### D56实际CLI只读预飞（LOG-20261016-19）

| 登记ID | 输入/执行 | 证据/实际结果 | 边界 |
|---|---|---|---|
| PREFLIGHT-R22-D56-ACTUAL-CLI | Dmanifest全56 argv，真实run_outerloop_real_wns.parse_args，与历史expected resolved_args逐字段比 | D56_ACTUAL_CLI_PREFLIGHT.json：56/56 mismatches空、passed/source_stable=true、eda_executed=false；scratch/check_d56_actual_cli.py SHA91af68ae…待归档 | 内存预飞非D56实验运行，补足buildmanifest/mock范围；production/tests冻结，无STA |

### 当前完整v5通过与阶段冻结（LOG-20261016-20）

当前第二批实现835pass/4skip/156subtests，147.00s、wrapper152.781exit0，166Python来源SHA稳定，environment_overrides PYTHONUTF8=1，JUnit0fail/0error。首失败及v2/v3/v4均保留。记录员停止写入供主线commit/push，新pin未实际保存，不先填commit。

| 下一计划 | 当前状态/边界 |
|---|---|
| 新pin正式9模型/能力控制 | pending，3正确/3故意错/2unsupported/1input_error；未执行 |
| B2新模型正式proof+可重复X identity certificate | pending，X边界只读审查不当一般四态SAT认证 |
| C′v3实际mapped复查→18pilot→72 | pending，先新pin/独立目录/真实输入；v2只注册禁执行，原manifest不改 |
| D56同族实验，先14pilot | pending，真实parse_args56/56预飞已过，不当运行完成 |

暂无STA/pilot；A6真实proof与空三态交集保持。OI038/039及B3/D/C与稿图回填仍待；临时unsupported能力门不是三态真实语义已证，显式四态编码恢复支持路径open。
