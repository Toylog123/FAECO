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

### 第二阶段Git与新pin正式9控制（LOG-20261016-21）

主线commit/push02e82a2、301files完成，记录员只读实查main/origin refs均02e82a2fd9f2c0a8b446f42413aa42e59b9ba10e；主线166来源提交前逐项匹配v5/code tree clean。不是用旧757替代当前835。

| 实验ID | 新pin/配置/证据 | 当前状态/实读结果 | 边界 |
|---|---|---|---|
| SEC-R22-MODEL-CONTROLS-PHASE2 | pin02e82a2、LIB/source/script SHA，9配置：3正确/3故意错/2unsupported/1input_error；sec_controls_phase2/controls.json | completed，预期9/9匹配：3正pass/3负fail/2unsupported/1input_error；source_stable=true、wrapper31exit0，POST_RUN_VERIFICATION后验source/LIB/driver全匹配 | 正式新pinSEC控制，无STA；不覆盖旧6目录，不预填全9通过 |

Xchecker独立代码审查/B2正式proof仍待。C′v3尚未注册，避免后续证据commit改变HEAD；实际mapped复查/18pilot与D14pilot尚未执行，不虚写manifest或运行状态。

### 新pin正式9控制结束（LOG-20261016-22）

02e82a2的sec_controls_phase2/controls.json已completed/passed/source_stable=true；3正确pass、3故意错误fail、2三态unsupported、1缺输入input_error全部预期符合，wrapper31s/exit0。POST_RUN_VERIFICATION.json记录all9_expected_statuses_match=true与source_and_library_and_driver_still_match=true（44source/LIB/driver无漂移）。记录员已实读。

这不是9个等价证明通过，三态unsupported是能力门、非四态支持认证。B2 Xchecker独立review/正式proof仍待，新矩阵尚未注册，无STA/pilot。

### B2新模型正式proof（LOG-20261016-23/24）

| 实验ID | 版本/输入/证明范围 | 命令/证据 | 实际结果/边界 |
|---|---|---|---|
| SEC-R22-B2-NEW-MODEL | HEAD44d20bb、44source/LIB/producer/checker SHA，四个原始raw bytes/accepted state绑定；checker66fe72ff…；two-state SEC+独立孤立constant-X identity | prove_actual_pico_pairs.py，wrapper480s/每proof180s；new_model_proof_run.log、new_model_proofs/manifest_and_results.json、逐pair产物/cert、POST_RUN_VERIFICATION | completed/source_stable：corepass6.078s+7X、mulpass0.750s+0X，wrapper16exit0；原bytes/完整decoded/artifacts/动态cert双pair全匹配；无STA，非任意四态/复位等价 |
| QA-R22-B2-X-CHECKER | checker66fe72ff…与实际四raw；独立代码/黑盒探针，不EDA | B2_X_INDEPENDENT_REVIEW.md/.json、B2_X_PRIMARY_REVIEW.json等 | 20/20负拒、5/6正接受、actual2pair7/0cert；合法escaped output保守误拒不影响B2，不称26/26期待全匹配；独立scanner另8负控制拒绝 |

44d20bb已commit/push（code未变），B2新correct模型缺证已恢复，旧runtime身份不补造，B3仍需同族合法候选恢复/重跑。新矩阵尚未注册、无STA/pilot。权威入口已收口为单一快照，动作/失败事实完整保留本登记/LOGS/原件。

### 只读同族恢复设计与新v3注册前（LOG-20261016-26）

| 登记ID | 来源/对象 | 实查结果/边界 | 执行状态 |
|---|---|---|---|
| DESIGN-R22-B3-REVALIDATION | r22_b_model_audit_20261016/B3_RERUN_DESIGN.md/.json；实际B3 raw/accepted state/旧recipe与blob | execution_ready=false；runtime argv/source/priority等unknown，不默用defaults；须保持B stateful outerloop，不能换C greedy或C′调度 | 只读报告完成，无EDA/STA/SEC；新同族重建参数须明确预注册 |
| DERIVED-R22-C-RECOVERY-EXTENSION | r22_rerun_design_20261016/C_RECOVERY_EXTENSION.md/.json | execution_ready=false/formal_source_pin=null；14份完整trial/终点跨表相同加强recipe但不证明copy/重跑或runtime argv；canonical s382身份仍缺 | 只读增量报告完成，无EDA，不把新重建起点选择反填历史identity |
| PLAN-R22-CPRIME-V3-PREPARE | 目标experiments/20261016_r22_cut_ablation_v3 | 实际Test-Path=false/未注册；evidence-only准备工具审查+commit后锁一次新HEAD，再注册mapping/静态域查→18pilot | prepared，尚无mapping/STA/pilot；v1/v2原件不改 |

proof/QA/docs阶段ddb4c33已commit/push，生产166来源不变。原归档phase2_final_qa/independent_primary_x_probes.py的EOF空行保source/target SHA，不改原档；后续diffcheck仅对该原始档和verbatim log/xml作精确排除，不放宽生产/docs。

### B17有界新证明与归因核查（LOG-20261016-27）

| 实验ID | 对象/配置/来源 | 实际文件结果 | 当前边界 |
|---|---|---|---|
| SEC-R22-B17-RECOVERY | HEADddb4c33，真正baseline/accepted raw仅nor4b_1→_2变化，helper相同，actualLib/common完整模型+flatten+assert；授权一次internal180/external240s，独占B17_new_model_proofs | B17_PROOF_RECOVERY_DESIGN.json complete/new_proof pass13.375s/return0；12879proven0unproven、NoSAT0，source/head/original/model稳定 | 主线独立POST_RUN_VERIFICATION已完成：原bytes/完整decoded/唯一尺寸变化/全部artifacts与44source匹配、12879/0实log成功；旧无state.current_netlist字段/hash，不补造，用acceptedrow/result/raw/dedicatedruntime收据交叉。无STA，不外推B23全集 |

首map.ys CP936预飞UTF8读取失败发生在SEC前、无EDA；随后严格CP936保原bytes/hash，实际proof网表仍UTF8。旧唯一未证_177917_实际nor4b输出、旧脚本无flatten且NoSATmodel；旧note的find_same_wires false-negative不是已证归因。新真SEC结果不能反填旧运行已证。C′v3只有evidence-only准备工具，实验目录仍未注册，166生产来源未变。

### B17后验与C′v3正式准备工具阶段（LOG-20261016-28）

| 登记ID | 对象/证据 | 实际结果/边界 | 下一门 |
|---|---|---|---|
| VERIFY-R22-B17-POST | B17_new_model_proofs/POST_RUN_VERIFICATION.json、producer报告SHAacaf5f… | 原bytes/完整decoded/唯一nor4b尺寸变化/全部artifacts与44source匹配、12879/0实log成功；producerJSON SHA实算一致 | B17新proof已恢复，不反填旧statehash/runtime，稿图待 |
| QA-R22-CPRIME-V3-PREPARER | r22_cprime_v3_20261016/prepare_inputs.py SHA22a3254c…；qa/独立manifest | crosscase stale input/artifact红3→最终20pass/0.78s；QA5 source/archive/hash实算5/5；evidence-only，production166未变 | 阶段commit+push后锁新HEAD注册v3→真实mapping8例/静态域查→18pilot→72；不是RTL→mapped等价证明，不新增未计划大型前置工具 |

本时点v3实验目录/manifest未创建，真实mapping/STA未开始；records暂停文档写入供B17/B3design/Cprep/QA/docs阶段提交，Git完成后才登记实际新HEAD/运行。

### 顺序单元新反证与源码重开（LOG-20261016-29）

| 登记ID | 对象/来源 | 实际结果 | 后续/边界 |
|---|---|---|---|
| PROBE-R22-SEQUENTIAL-F1-R | SEQUENTIAL_GATE_COUNTEREXAMPLE.json，HEADddb4c33/v5旧44production来源；合法dfrtp_1→dfstp_1 | F1期望fail实际pass；LR错误34FF-R候选；actual63seq graph边界全识别；eda_executed=false | OI040 open，LR禁seq组合R/F1完整顺序语义+合法G TDD，新完整v6/commit后才能新C′v3注册；graph不改 |

这不是835回归失败，是未覆盖的新反例。A6/B2/B17模型生成未改、实际修改非seq，精确proof各保原pin不自动否定。准备器20QA已过但不能据此注册旧源码实验；v3实验目录实查不存在/未注册，无mapping/STA，无旧实验需中断。

### 顺序门限定修复/旧证明模型保持/完整v6（LOG-20261016-30）

| 登记ID | 对象/证据 | 实际结果/状态 | 边界 |
|---|---|---|---|
| CHECK-R22-SEQUENTIAL-REWRITE | scratch/r22_sequential_20261016/rewrite_red/green.log | 红74fail3pass→相关105pass4.12s，wrapper5exit0 | LR顺序R封闭、合法G保留；非整套 |
| CHECK-R22-SEQUENTIAL-F1 | sequential_f1_red2/green1/related.log | 有效红12fail2pass→专属14pass6.89s，7文件201pass50.82s/wrapper57exit0 | 首red合法G fixture重复inputpin已纠正，不当生产问题；rawseq groups含clear_preset/statetable |
| VERIFY-R22-PRIOR-PROOF-MODELS | verify_proof_model_preservation.py、proof_model_preservation/verification.json | A6+B2+B17九份models9/9字节一致/source与LIB稳定/eda=false，wrapper20exit0 | 重生成字节保持非新外部证明，精确proof保原pin；另6statetable writer原不支持failclosed、不扩支持 |
| CHECK-R22-FULL-V6-20261016 | full_regression_v6.json/.log/.xml目标；168beforeSHA/PYTHONUTF8=1 | completed/passed：926pass/4skip/156subtests、155.08s/wrapper157.875exit0、168before/after SHA稳定/PYTHONUTF8=1；JSON/XML/log实读 | 当前新源码必须待完整v6/commit后才注册C′v3，无mapping/STA |

### 当前完整v6验收与提交前冻结（LOG-20261016-31）

926pass/4skip/156subtests，155.08s/wrapper157.875exit0，168来源SHA稳定、PYTHONUTF8=1，JUnit0fail0error。OI040代码阶段关闭，反例/红绿/旧版本边界保留。preparer在新顺序源码限定再20pass/0.84s，九proof模型字节保持验证保留（非外部重证明）。

记录冻结供立即commit/push→同一新HEAD注册C′v3→真实map8例/静态门→18pilot→72；不再追加前置审计/工具。范围外四态/6statetable支持、B3/C配置与科学回填保持open但不阻碍本已验证域。当前v3未注册/未mapping/无STA，不能预填实验通过。

### 原始顺序反例精确重放失败（LOG-20261016-32）

| 登记ID | 对象/来源 | 实际结果 | 归因/后续 |
|---|---|---|---|
| VERIFY-R22-SEQUENTIAL-EXACT-REPLAY | verify_sequential_gate_fix.py，原SEQUENTIAL_GATE_COUNTEREXAMPLE字节SHA e1cc8bf…；SEQUENTIAL_GATE_VERIFICATION.json | passed=false，reset→set仍pass/合法Gpass/seqR0/source_stable/eda=false | gate_sizing行首regex漏单行，两侧parsed=[]，F1空集伪pass；新OI041 open。OI040多行seq子门有效但原反例归因混合不完整，失败verification不覆盖；新v7/commit后注册v3 |

926是v6真实通过，不是回归失败，而是未覆盖新反例。parser单行/$名/注释strings/escapednet、F1物理↔parsed完整覆盖及旧源多行seq反证TDD进行中；当前无v3注册/mapping/STA，无旧实验要停。

### OI041限定修复、精确重放V2、完整v7（LOG-20261016-33）

| 登记ID | 对象/证据 | 实际结果/状态 | 边界 |
|---|---|---|---|
| CHECK-R22-MAPPED-STATEMENT | mapped_statement_red/green1/buffer_regression原logs | 红21fail6pass→相关119pass2.47s、buffer17pass0.22s | 单行/$/escaped/comment支持，限定非整套 |
| CHECK-R22-F1-PARSER-COVERAGE | coverage red/green1/escaped_comment_red/green2/related | 覆盖红11fail1pass，escaped comment反例另红1；最终27pass、相关214pass52.33s/wrapper56exit0 | 独立物理↔parsed覆盖；限定重叠范围不累加 |
| REPRO-R22-SEQ-MULTILINE-LEGACY | reproduce_multiline_legacy_seq.py+log、SEQUENTIAL_MULTILINE_LEGACY_REPRO.json SHAcd028… | 旧源码多行两物理FF可见仍reset→set伪pass，当前拒两格式 | seq语义缺陷独立于旧单行解析漏匹配，非EDA |
| VERIFY-R22-SEQ-EXACT-V2 | SEQUENTIAL_GATE_VERIFICATION_V2.json锁原counterexampleSHA | reset→set fail/legalGpass/R0，parsed1/1/source_stable/passedtrue | 原失败receipt不可覆盖，新V2限定通过不等整套 |
| CHECK-R22-FULL-V7-20261016 | full_regression_v7.json/.log/.xml目标，170beforeSHA/PYTHONUTF8=1，session32703 | completed/failed：965pass/1fail/4skip/156subtests、155.08s/wrapper158exit1，170来源SHA稳定/PYTHONUTF8=1 | OI041不关闭、不冻结完成，v3尚未注册，无STA |
| ARCHIVE-R22-SEQ-INTEGRATION | 新sequential_integration_qa/ARCHIVE_MANIFEST，10原始完成logs/probe脚本+4派生artifact引用 | source/target/hash亲算10/10，derivedlegacyJSON SHAcd028…匹配 | 旧sequential_tdd/PREIMAGE保留，未覆盖失败verification |

root误直接运行Cprep qa归档副本20F仅为原parents[2]路径上下文不符，未触代码；原scratch同源控制20pass1.10s。归档原件字节不改，重跑用原scratch位置或新副本适配路径，不当生产缺陷。

### 完整v7失败归因（LOG-20261016-34）

唯一失败为test_production_runner::test_runner_accepts_topology_trial_and_records_structural_delta，共享_assert_unique_physical_instances被F1严格named-pin连接提取误扩张，合法positional参数抛Parser coverage异常。实际965pass/1fail/4skip/156subtests，155.08s/wrapper158exit1，170源码SHA稳定；不是来源漂移或科学想法失败。root拟显式opt-in仅F1提取连接，公共唯一性门保留positional；TDD后新完整v8，旧v7原件保真不覆盖。OI041尚未关闭，无C′v3注册/STA。

### 公共唯一性门兼容性修复与完整v8（LOG-20261016-35）

| 登记ID | 对象/证据 | 实际结果/状态 | 边界 |
|---|---|---|---|
| CHECK-R22-F1-SCOPE-COMPAT | include_connections=False default，F1两调用True；scope红2fail14pass/0.39s | 主线实际tool限定30pass/1.27s；原绿stdout未保存，不补造log | f1_scope_qa/ GREEN_RUN_NOTE显式标二手tool回显、非raw执行日志；原红和RW/test preimage3件source/target/hash匹配 |
| VERIFY-R22-SEQ-EXACT-V3 | SEQUENTIAL_GATE_VERIFICATION_V3.json、原counterexampleSHA | reset→set fail/Gpass/R0、parsed1/1/source稳/passedtrue | 原失败/V2/V3并存，限定通过不等整套 |
| CHECK-R22-FULL-V8-20261016 | full_regression_v8.json/.log/.xml目标，170beforeSHA/PYTHONUTF8=1，session70494 | completed/passed：969pass/4skip/156subtests、155.12s/wrapper157.969exit0、170before/after SHA稳定/PYTHONUTF8=1；JSON/XML/log实读 | OI041仍open、等v8完成再冻结docs；无C′v3注册/STA |

### 当前完整v8通过（LOG-20261016-36）

完整v8实际969pass/4skip/156subtests，155.12s/wrapper157.969exit0，170源码SHA稳定/PYTHONUTF8=1，JUnit0fail0error。原始精确V3 passed/parsed1/1/reset→set fail/合法Gpass/R0；公共scope限定30pass。OI040/041仅实现门关闭，科学pending不变；原failedverification/v7与各轮归档保留。

B3_RECONSTRUCTION_ADAPTER与C_RECONSTRUCTION_ADAPTER仍WIP，不纳本次stagecommit。records冻结docs，root归档harness/更新根入口后阶段commit/push，再同一HEAD注册C′v3→真实map8/静态门→18pilot；当前未注册/未mapping/无STA，不新增前置工具。

### C′v3正式登记与真实输入准备（LOG-39/40）

| 实验/登记ID | 版本/输入/配置 | 证据/执行 | 当前状态/边界 |
|---|---|---|---|
| EXP-R22-CPRIME-V3-72 | pin3ea0f757f5e9bab4a2df75c458b0c665eabcb258、44productionSHA/LIB/tools/input锁，9arms×8circuits72jobs | experiments/20261016_r22_cut_ablation_v3/manifest.json，SHA72dfbef9dd36101c543f0d3788084579b31482b1a29cdfcc5875826cc445fd41 | registered，18pilot尚未起；固定HEAD、不覆盖v1/v2 |
| DRYRUN-R22-V3-PREP | 已注册v3 manifest全部8例 | prepare_inputs.py --dry-run，root实际8would_map成功 | 非mapping/STA/SEC，不当实验效果 |
| PREP-R22-V3-MAP-STATIC | 同pin，真实8例首次mapping/静态域/输入receipt，PYTHONUTF8=1，timeout1800s，session21802 | actual_prepare.log（scratch/r22_cprime_v3_20261016），inputs/各例产物；preflight.json目标 | running，首读7STATIC_DONE+s953 MAP，preflight尚未齐；无STA/SEC/18pilot，不是RTL→mapped证明 |

root新包raw-index保护60文件逐字节匹配，renormalize生效，单调用cr-at-eol diffcheck rc0，原raw未改。阶段3ea0f75已push且code/preparer clean；records只写docs不commit，B3/C WIP排除。

### C′v3真实准备完成与18pilot启动（LOG-41）

| 登记ID | 对象/配置 | 当前状态/证据 | 边界 |
|---|---|---|---|
| PREP-R22-V3-MAP-STATIC | 同pin3ea0f75/8例/PYTHONUTF8=1 | completed，wrapper46s/exit0；preflight prepared+PREPARATION_POST_VERIFICATION全8artifacts/F1identity/F2/domain匹配/source稳定 | mapping_equivalence not_run、sta_executed false；不是RTL→mapped证明/STA |
| PILOT-R22-V3-18 | s27/s382×9，session91713，timeout36000s/每job3900或3930s，PYTHONUTF8=1；manifest72dfbef9… | running，pilot.log首W0两例finalSEC pass，候选字段9/8、提交0、WNS-.27/-.98不变；已启动W1 | 首2不等18通过，legacy候选字段不作全部STA次数。18全部独立SEC/分账审计后扩剩余54，不改既有接受预算/参数 |

协议实查：W0/s27首trial WNS-.27→-.26、TNS-.49→-.50，setup_tns硬门拒。当前严格WNS改善受TNS不退化等硬约束，tns-aware只影响平局选择，不能简称无约束唯WNS。

### C′v3 5/18独立核验快照（LOG-42）

最新只读PILOT_AUDIT_05已核验5/18（非全18）：source稳定/argv匹配，candidate_ideal实际launch与mapped/log绑定、commit完整哈希链和finalSEC非零proven/0unproven皆通过。s27 W0/W1/U0候选理想STA=9/41/9、保留提交0/2/0、最终WNS=-.27/-.18/-.27；s382 W0/W1为8/89、提交0/3、最终WNS=-.98/-.83。计数仅candidate_ideal，不含全部baseline/refresh/physical STA。

证据PILOT_AUDIT_05.json；原调用scratch/audit_cprime_v3.py的SHA与receipt实算一致，最终18完成后另建manifest归档。初版审计错误期待未序列化epoch字段KeyError且无receipt，改为实际完整hash链核验；这是证据工具schema假设错误，非生产失败。

监测LOG43：pilot.log实际7/18 DONE均report finalSEC pass，独立PILOT_AUDIT_05仍5/18；新增U0/s382、U1/s27完成，U1/s382与C/s27启动。运行推进，未宣称全18后验通过或扩72。

### C′v3 7/18独立分账审计（LOG-44）

最新PILOT_AUDIT_07独立核验7/18通过（非全18），source稳定/argv匹配，逐candidate mapped/tcl/log SHA、实际launch、commit完整哈希链和finalSEC非零proven/0unproven均匹配。完整sta.log路径恰为candidate理想记录加初始baseline；resolved physical/electrical/S均false。七例每例baseline实际过程1次，candidate_ideal合计205次+baseline7次=212次已审计STA过程（other0），不是物理STA。W1的s27/s382保留提交2/3次，最终WNS-.18/-.83；其余全矩阵效果与验收仍待。

逐项candidate+baseline=actual过程：s27/W0 9+1=10; s27/W1 41+1=42; s27/U0 9+1=10; s27/U1 41+1=42; s382/W0 8+1=9; s382/W1 89+1=90; s382/U0 8+1=9。v05audit原源e6d9…已保留_v1.py；v07新版d932…与receipt SHA一致，最终分别归档。

监测LOG45：日志10/18 DONE均report finalSEC pass，独立最后audit07仍7/18。两电路W0/U0、W1/U1首轮configured实际非均匀、uniform全1，但pool/dispatch hash一致；这是探索观察，不据当前收益归因加权、不调参，完整矩阵后判断。

登记LOG49：source_snapshot/runtime_inputs.zip + snapshot.json确切runtime包62件/2400670B/SHA620a0eb9…，source_stabletrue；root解包核验与记录员直接ZIP SHA62/62一致。44source+Lib1+RTL8+mapped8+prep1，不含二进制工具，仅registered_versions。final72后归档提交ZIP需force-add，本轮不Git。pilot日志15DONE/reportpass，独立audit仍07。

LOG52：18pilot已18DONE全return0/finalSEC reportpass，wrapper1028s/exit0。最后独立audit仍07；最终后验receipt待，不提前登记全18验收或剩余54启动。

### C′v3 18pilot完成独立验收，扩余54（LOG-53）

| 登记ID | 版本/配置 | 实际结果/状态 | 范围 |
|---|---|---|---|
| PILOT-R22-V3-18 | 固定3ea0f75/s27+s382×9，原注册不变 | completed；wrapper1028s exit0，PILOT_AUDIT_18 18/18独立全通过/source稳 | 1360评估记录、1064candidate_ideal STA+18baseline=1082实际STA过程，other0；35保留提交，非物理STA |
| RUN-R22-V3-REMAIN54 | 同HEAD/manifest，s420/s641/s713/s820/s832/s953×9；session9345/108000s/单job3900或3930/wall3600/PYTHONUTF8=1 | running，remaining54.log实际s420W0/s641W0 LAUNCH | 全72验收前不commit/变HEAD，不预填效果或完成，后续B3/C提交等待 |

ARCHIVE-R22-V3-PILOT-QA（LOG54）：pilot_qa新独立manifest共60件source/target/SHA匹配；auditv1/v2分别绑定05和07/18，原pilot stdout与18 completion/SEC receipts/log保真。完整实验raw/models/STA仍单一注册原路径，由manifest证据SHA引用。当前不Git，72验收后root归档提交。

LOG55运行监测：剩54首s420/W0、s641/W0已DONE且finalSEC reportpass；W1运行，全族日志20/72/独立最后audit18。B3已51mockQA通过，C38mock/staticQA通过且formal接口WIP，未注册/未EDA，不计科学复验。

QA-C-ADAPTER-DRIFT（LOG56/OI042）：scratch/c_adapter_review/probe_results_v2.json独立反例，末STA调用TCL Liberty路径漂移仍qa_complete/1commit，mismatch_acceptedtrue。原38mockQA独立再跑38pass66.09s，未EDA/未正式注册；不计新科学结果、不影响C′source矩阵。正式C_ADAPTER_REVIEW报告待落盘，修复闭环待。

LOG58监测：剩54完成6，全族24reportpass/最后独立audit18；s420/s641各W0/W1/U0均完成，U1在跑。18pilot预览图v2独立VISUAL_REVIEW passed-as-preview/18数据全保留，未插正文，不当全72科学结果。

### 全矩阵独立24/72审计（LOG-59）

MATRIX_AUDIT_24已exit0/24已核/source稳定/all_matrix_verifiedfalse：全部candidate raw-tcl-log SHA、argv/STA ledger、commit链、finalSEC非零proven0unproven匹配。当前1418candidate_ideal+24baseline=1442actual STA过程，other0/46保留提交；仅24范围，非物理STA。新增W1s420177STA/6commit/终WNS-1.21，W1s641151/5/-1.17。独立matrix脚本SHA0578cdf9…，原pilot v2/18收据未改；全72运行未完，不跨族归因。

QA-B3-ROOT-FINAL（LOG61）：B3_RECONSTRUCTION_ADAPTER/root_final_qa独立manifest保真2原件；51pass16.28s、wrapper20exit0、runtime20.578s、source before/after/当前SHA全匹配，HEAD3ea/eda=false。仅限定工具QA，正式新pin/B3登记等待C′72完成后提交。

QA-C-TRANSACTION-84（LOG62）：新transaction_interface_20261016/QA_REPORT.json SHAe867e944…，84pass81.73s/wrapper87exit0，mockSTA/SEC，真实8起点仅静态门。原OI042反例作者red→green正确PinDrift拒/无completion；独立修后复核待/OI042仍open，48jobs只是preview，未登记/无EDA。旧C38报告保历史不覆盖。

DIAG-R22-MATCHED-STATE-08（LOG64）：mechanism_audits/MATCHED_STATE_PAIRS_08.json，4完成电路×2配对，各20同baseSHA轮。非均匀weighted代价确实生效但cut/pool/dispatch/endpointSHA均同，EDAfalse/partial。独立ARCHIVE_MANIFEST_08归档脚本原字节3ef4ceaa…，保输入SHA/原scratch调用；重复轮不当独立样本，不能外推全8或因果增益，不调整参数求正结果。

VERIFY-C-OI042-INDEPENDENT（LOG65）：C_TRANSACTION_ADAPTER_REVIEW独立原probe重放PinDrift/exit1，0commit文件和事件/无completion，register38独立QA17.70s/20exit0/60sources稳/新阻断0，原件三SHA核符。主线授权限定关闭OI042实现门；C48未登记/无EDA/非科学恢复。作者84只读不冒充独立全跑，旧红证据保留。

PREP-R22-MATRIX-FIG4（LOG66）：r22_matrix_gain_cost_contract.json+review_r22_matrix_gain_cost.py prepared，72raw增益/实际总STA和64同电路配对差全保留。scratch/r22_matrix_plot_incomplete_guard.json实读对24partial拒绝/exit1/无output，plotterSHA0ff794c6…匹配。未render/未插正文/未验收最终图，等MATRIX_AUDIT72全验收。

ARCHIVE-C-OI042-PREIMAGE-6（LOG67）：C_ADAPTER_REVIEW/source_snapshot_pre_OI042六原件+原before_sha256收据，6/6 source-target-beforeSHA匹配；5条绑定首review frozen表、QA_REPORT绑定其qa_report_sha256。旧adapter6bd06…/backend3d6f…对应38QA/红probe，不覆盖当前代码或旧报告。仅历史快照，HEAD不变。

CHECK-R22-CLOCK-CONSTRAINTS（LOG68）：Pico187脚本+canonical B27 baseline TCL逐SHA/create_clock一致，aggregate source SHA匹配；5ns/2ns/0.5ns明确分模块。只读设置审计无新时序测量，OI043中英环境句错误待主线最小修正，效果数字未动。

LOG70独立mechanism partial4：NetworkX重算160trace/20uniquebase，120根强制+40s420成本优势，source稳/无EDA/无参数改；新mechanism_review/ARCHIVE_MANIFEST保原script/log/reportSHA，非因果收益或8电路结论。LOG71历史B3旧24/44 source查找0匹配，negative lookup二原件独立归档，不声称旧源码恢复/可重放。LOG72 CLAIM_REPLACEMENT_MAP只读17claims/396source冻结matrix24范围，非论文已回填。

### 独立matrix36实际对象与归档（LOG73）

MATRIX_AUDIT_36.json：36已核/72，s27/s382/s641各9+s420八臂（缺L）+s713W0，不是四电路各9。3987评估/3436candidate_ideal+36baseline=3472实际过程/other0/109保留提交，source稳/非物理STA；原stage log10s exit0。matrix_qa/stage36保原脚本/log/receipt3/3SHA，runtime后来的s420L完成待后续新N独立核入，不回写旧36。全证据solid7z分卷仅设计未完成。

EDIT-CLOCK-METADATA-01（LOG75/OI043）：中英setting/图4caption各2处，Pico5/2/.5ns分模块、同电路baseline/repaired同约束。en错误字面转义V1保真且V2修；最新sourcezhcb9bd…/enbdde6…与两遍buildsource稳定实核，buildPDFzh80416…/enbb6b35…当前SHA匹配。仅文稿设置更正非新EDA/非效果数字变化，视觉QA/副本验收待，OI043未关闭。

ARCHIVE-R22-V3-S27-FULL（LOG76）：full_artifact_archives/s27/receipt.json verified：1400原文件/25616925B、9jobs+inputs+固定注册/source/LIB/RTL/audit36；solidLZMA2/80MiB分卷，实际单卷1930551B/SHAfdd26…实核。source稳/member-size/7zt/restore全SHA-size均通过，主线独立复核待；仅s27，不当完整8电路归档或新的EDA。

LOG77 s27全证据包root独立后验accepted：1400source当前SHA-size/所有sidecar/volume/独立7zt匹配。仅s27；s382/s641授权扩大但未预填结果，s420待新N独立9臂。LOG78 metadata zh12/en26静态QA及38p渲染exit0完成，visual仍pending/OI043不关闭。

ARCHIVE-R22-V3-S382-S641（LOG79）：s3822572files/663675739B→5952319B、s6414029files/783814031B→5872335B；receipt/volumeSHA实核，两包均source稳/member-size/7zt/restoreSHA-size true，80MiB配置各一卷。producer verified、root后验待；s27已rootaccepted，s420未授权归档，保持原实验文件。

LOG80/OI043 metadata-only gate closed：FINAL_QA+SYNC独立SHA核符，双语各14表块/7图引用未变、38p visual无缺陷/PDF周期句回读通过、中文双副本80416…和英文bb6b35…当前实核。仅说明修正无新EDA/收益数字变更，不升级科学结论；首提取串栏失败/V1V2/旧PDF备份均留存。

DESIGN-REGION-STATIC-PARTIAL4（LOG81）：先CONTRACT后census，region_design_review三最终SHA核符；初始四电路共同bounded union eligible6/11/10/11=38，212编辑F1/F2静态pass但未SEC/STA/接受，230proposal未检不当invalid。s27top1 null、其余3top1差异/uniform ties/全部singleton均保留。46source17input稳定、无EDA/无参数改/未正式注册；源oracle首失败与v2 exactsrc/TIMING_CORRECTION永久归档。

### v2冻结对象集合独立51/72（LOG83/84）

MATRIX_AUDIT_51 completion_set_frozen_at_starttrue，51eligible当前completionSHA独立复核；范围四电路各9+s7137+s8208，5887评估/4919candidate+51baseline=4970实际STA过程/other0/137保留提交。stage51原v2ea0a…/名含50的原log/51receipt新manifest三件SHA一致；计数以receipt51不以日志名。s27/s382/s641全归档rootaccepted；s420在此51具完整九臂后归档已34681/900s运行，未记结果，全72仍未完成。

PREFLIGHT-S-SPEF-HISTORICAL（LOG85，provisional）：只读初查进行中无EDA；待核S非法起点/可能合法恢复candidate、CEC路径精确绑定，SPEF重复评估/寄生参数/端口方向/paired-baseline。冻结报告未齐，不引用未实读数量、不当新不等价证明或全候选invalid，关联OI014/OI015/OI036开放待核；未改稿或当前C′参数。


### VERIFY-R22-CPRIME-V3-FINAL72（2026-10-18，LOG-20261018-03）

最终MATRIX_AUDIT_72.json SHAa34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738；72/72、8circuits×9arms、all_matrix_verified/source_stable/completion_set_frozen_at_start=true，当前72completion SHA逐一匹配。8458评估记录、6858candidate_ideal STA+72baseline=6930实际STA过程、other0、192保留提交；每endpoint独立SEC非零proven/0unproven。固定HEAD3ea0f75/manifest72dfbef9…/v2审计器ea0a9793…；session54830实际exit0/runtime46.546s。physical/electrical/S均禁用，不称物理STA；本次仅读审计不重跑EDA。stage72/ARCHIVE_MANIFEST五原件逐source-target SHA匹配，旧51/54/失败v1保留。剩54原运行wrapper3728s/exit0已完成。B3/C/D同族恢复、四态支持、S/SPEF历史审计及稿图科学回填仍待，不能跨族补证。


ARCHIVE-R22-V3-S713-S820（2026-10-18，LOG04）：MATRIX72绑定；s7133390files/645811769B→5439288B、s8202769files/490800683B→4516647B。receipt/volume SHA实核、source稳定/成员/7zt/恢复全SHA-size均true，wrapper103/82s exit0；producer verified、root后验待，原数据不删/无EDA/无Git。s832/s953归档进行中，不预填全八归档完成。

ARCHIVE-R22-V3-S832（2026-10-18，LOG05）：MATRIX72绑定；2721files503246244B→4456881B，receipt f2de16ee…/volume SHA实核，source稳定/成员/7zt/恢复全SHA-size true，wrapper77s exit0；producer verified、root后验待，无EDA/未删原件。

ARCHIVE-R22-V3-S953（2026-10-18，LOG06）：MATRIX72绑定；2485files/1365925045B→11433819B，receiptdf6de53a…/volume SHA核符，source稳定/成员/7zt/恢复全SHA-size均true，wrapper164s exit0；producer verified，root后验待。四新包制作全结束，无EDA、无删除。


VERIFY-R22-CPRIME-MECHANISM16/FIGURE（LOG09）：机制16报告ef78ed8a…/32输入SHA实核，ARCHIVE_MANIFEST_16保原script3ef4…与原调用；独立FIGURE_CPRIME_REVIEW269205b9…核raw72/paired64/completion72、16配对全部重复同状态轮5454cross-comparisons零差/终点全文同，source稳定；本矩阵未见独立权重收益，重复轮非独立样本。独立review脚本c410bb…保真归档。v1导出SHA/最小6.8pt/人工及独立视觉均有原件，但LOG11新自动几何门6FAIL推翻无碰撞交付判断，v2待QA；数据/机制科学核验不因此变成失败，不删除旧v1。

REVIEW-S-SPEF-INDEPENDENT-V2（LOG10）：S258文件/1032组合条目match、0issue，旧!解析错误和首新B1误滤错误均保失败原件，V2为权威；126/76/0与静态合法域边界分开。SPEF漏SUM driver、双侧共用SPEF、read_spef后报告混杂均有实对象/静态探针，下一阶段sourcefix+真实同族重跑待。历史s382RC unknown保留，不把b18unit1或scan对象跨借；无EDA/生产改动。

ARCHIVE-R22-V3-ALL8-ROOT-ACCEPTED（LOG08）：八ROOT_POST逐receiptSHA/7zt/source/sidecar/volume等核符；原实验不删。source3ea仍固定，归档accepted不代其他科学族。

VERIFY-R22-MATRIX-FIGURE-V3（LOG12）：FINAL_REVIEW32ff889a…所有14文件SHA核符，源d9ef05b…，CSV与v1逐字节相同；collision0F0W/PanelPASS/glyph6.8pt60runs0below/source19P2W0F，partial51建输出前拒/root四panel+整图视觉通过。仅几何实现门关闭，独立v3视觉追加/主稿整合待；v1负控/人工误漏原件不改。无EDA/生产改动。

VERIFY-R22-MATRIX-FIGURE-V3-INDEPENDENT（LOG13）：独立追加71d9a480…/所有来源当前SHA核符；实际PNG+独立PDF重渲染视觉通过，raw72/paired64与5454同状态既有独立验证保留。v3最终审查预览验收完成，正式主稿整合/其他历史族科学门待，无新EDA/生产/Git。
