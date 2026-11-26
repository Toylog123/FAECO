# 实验登记表

> 记录**所有做过 / 正在做的实验**，避免重复做。**做新实验前先查本表**。

**历史恢复起点（2026-10-16，以下保留当时状态）**：用户“继续”已恢复r22。起点main clean/781c031已push；K1–K6修复进行中，首整套741pass/1fail修后v2完整757pass/4skip/156subtests、162源码SHA稳定已通过；尚无新真实EDA结果。v1保持stopped且原件不改；新v2须修复版整套回归/独立复审后另锁source pin、配置、模型/库/输入/工具，再18pilot→72。旧667不能作当前版本验收。

**当前状态（2026-10-18/LOG139）**：r23“审稿中文稿”为当前授权，只读稿件/图/证据；先盲标准后稿可见的五视角已注册INPUT2d76968c…/FIELDfcd0e2e2…/contractQA1a3651b0有效，未校准/无确认期刊fit，最终报告未齐。HEAD/codef761不变。D remaining106a6234…finished0/5898.406s、04:01monitor30098530…实际56producer/active-failed空/源稳定；93检查的lifetime68c282be…自动收束。正式accepted28/raw3，两门（56+全部8post）未齐仍锁；本轮不新D验收/归档/源修或EDA。

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


TDD-SPEF-TOPOLOGY-RED-V2（LOG17）：7231修复基线，12fail0.55s=11新API尚未实现TypeError+1旧API真实端口重复/丢cellpin，不是12独立bug；原log在scratch/spef_topology_red_v2_20261018.log，source/test/log原件由主线后续归档绑定。无真实STA。
TDD-S-CEC-RED-V2（LOG18）：RED_V2_RECEIPT2815e4ea…/14件SHA实核，5fail3.10s/wrapper5exit1；首fixture错保留，正确V2先红/production未改后minimalfix。mock边界，不是新SEC。
TDD-OPENSTA-PAIRED-SPEF-RED（LOG19）：RED_RECEIPTd6e4cf50…/31件SHA-size实核，8fail1pass2.06s/wrapper5exit1，native fake、actual_opensta=false。确认timing来源、失败float及共享baseline SPEF现有缺口，不是物理效果实验，后续绿灯与完整集成待。

TDD-S-CEC-GREEN-LIMITED（LOG20）：GREEN_FINAL47pass1skip3.69s/wrapper5exit0，SOURCE_FINAL_BEFORE/AFTER三SHA与当前文件实核一致。原timeout-byte RED_V3 1fail8pass保留；仅限定S/邻接测试，不等完整回归/独立审查/正式新SEC，完整作者报告待。

TDD-OPENSTA-PAIRED-SPEF-GREEN4（LOG21）：green4 receipt08a1df80…/221件369464B SHA-size实核，71pass6.43s/wrapper10exit0/300s。native controls/no actualOpenSTA/EDA，source只有completion snapshot无before，不声称运行前后稳定。red2(12F2P)、red3(2F17P输入漂移)、red4(2F19P双流诊断)及各green/夹具误配保原件，主线整体与独立验收待。

TDD-SPEF-TOPOLOGY-GREEN5（LOG22）：独立四类5case真红5fail0.59s保修前source/探针，修后v5 58pass2.08s/wrapper5exit0；v3 51pass/v4 53pass各原log保留。8实际rawmapped当前SHA核符/staticparsed，12无pin常量alias显式omission，仅静态非STA/SEC。fixture合法化与nullbaseline真bug分开，不借QA称科学效果。
REGRESSION-S-SPEF-INTEGRATED-V1（LOG23）：HEAD7231/working repaired source173个code.py beforeSHA当前核符，session90911实际启动pytest600s/外650s，result/after待；不得提前填通过，不新正式EDA。

VERIFY-SPEF-STATIC-POST（LOG24）：POST_REVIEW46d9972e…/四source before=after=current/9artifact SHA核符，原四类及两拒绝控制静态通过、120s/wrapper5exit0/toolprocess0。仅静态连接实现门，escaped真实OpenSTA注入/同RC各侧验证待新pin正式登记，不是物理结果或全修复。

REVIEW-S-CEC-INDEPENDENT-DRIFT（LOG25/OI045）：review5f7d5cfe…/66作者+40独立原件SHA-size全核、3source前后/current稳定；controlled派生_cells.v81→129B后仍pass/input_drift空，启动错误unavailable但缺normalize.log。仅input identity/diagnostic缺口、无真实EDA/函数错误证明；共享归一化helper待修，原47QA/旧报告保留，full173v1结束后才能解冻source。

REGRESSION-S-SPEF-INTEGRATED-V1-FAILED（LOG26）：1013P2F11skip156subtests/205.77s，RUN206.789275s/600s，wrapper210exit1，173before=after及ZIP173成员SHA逐件核符，source snapshot records验收独存。两fail为旧physical fixture非法；仅修fixture且保断言后2case pass0.37s，整体v2待OI045修复冻结后-ra。失败原件不覆盖、不把fixture修复当生产降级或新科学结果。

STATIC-ACTUAL-SPEF-FINAL10（LOG27/OI046）：FINAL_ACTUAL_INPUT_STATIC_CHECK source2前后/current与10原mapped SHA核符；8ISCAS parsed、b18_light baseline c5c89e3a…/R42db3970…两者在真实inout LOGIC0上unsupported。仅静态、非STA/SEC/整机合法性。b18双向/常量驱动语义待分析设计支持，不默改方向/不造物理比较；s382最小合法pilot另待新pin。

ARCHIVE-SPEF-TOPOLOGY-QA（LOG28）：TOPOLOGY_QA_RECEIPTc6abaae2…/5current-source与5final-source snapshots SHA核符，12原log/独立pre-post/最终static10保留；中间仅有manifest的source字节声明可重放。port fanout/pureport/RES编号修正会改变新SPEF，旧RC原件不可覆盖或借新生成器追认，未新STA/SEC。

TDD-OI045-SHARED-NORMALIZER（LOG31）：author FINAL4456ddb7…/73原件SHA-size+3source beforeaftercurrent核符；最终兼容RED_V2 4F10P2.32s→51P1skip4.28s。根ROOT_ACCEPTANCEbcbfdfb1…/56manifest核符，原三case12输入逐字节同、drift非pass/launch日志齐，原反例层关闭，整体v2待；未真实Yosys/ABC/STA。
REGRESSION-S-SPEF-INTEGRATED-V2-START（LOG32）：session73955/-ra/pytest600s外650s，173source before current/前置ZIP173成员SHA已核，SOURCE_SNAPSHOT_RECORDS_PRE_VERIFICATION独存；result/after待，不提前写全过。

AUDIT-B18-DOMAIN-PASSIVE-DESIGN（LOG33/OI046）：AUDIT2c3ec37a…/report e38dbafd…/receipt8cb35f3d…，15sources前后/current及artifact SHA-size核符，300s/wrapper10exit0。bench24consumer/无driver与mapped4input端点相同，BLIF acquisition身份/EDIF/转换运行receipt unknown保留。单PB+4I被动外部边界窄域与8反驳控制仅设计，未实现/未测试/无EDA，不能填双向支持或恒0。

REGRESSION-S-SPEF-INTEGRATED-V2-PASSED（LOG34）：1019P11skip156subtests220.11s，RUN221.0839812/600s/rc0、wrapper225s0；173before=after=current及前置ZIP成员逐SHA实核，logb4c176a4…，POST_VERIFICATION独存。-ra skip3convert/1realc17工具不可见+7Gitbashpwd-W，后续childPATH显式现有工具只补4文件独立计，不与1019合并总数；sourcecommit与真实同族科学门仍待。

REGRESSION-TOOL-VISIBILITY-SUPPLEMENT-NATIVE-FAILED（LOG35/OI047）：实际3文件（修正此前计划4）22P1F0skip8.18s，RUN8.7945943/300/rc1；源173map与fullv2after同/稳定、logSHA实核，不与1019累加。native c17真实Yosys/ABC error，$mul来自noused时整库fallback/未top剪枝混入无关模型，底层rc0但正确非pass。定向红→最小used模型提取修复/native与全当前回归待，非新科学campaign。

TDD-OI047-MODEL-SUBSET-LOCAL/NATIVE（LOG36）：真red3F5deselected0.38s→43P1skip3.27s；tool_checks_v2真26P5.77s/RUN6.4527533/300/rc0/source173stable，nativec17pass只是该正控，不代top绑定。
FALSIFY-NATIVE-CEC-WRONG-TOP（LOG37/OI048）：RESULTd3822ed1…，ztop Y=A vsY=B在A0B1不同却APIpass；ABC实际first sky130_buf_1，源bca40已在top_scope_repair完整保真核符。根requested/unique-source-top修复局部45P1skip尚待native原负控与全当前回归；旧scope审计独立门，禁止跨推C′SEQ无效。

NATIVE-OI048-POST/TOOL-V3（LOG38）：两个原Verilog输入字节同，native_top_counterexample_post statusfail/ABC NOT EQUIVALENT，tool_checks_v3三文件28P4.29s/RUN4.9232689/300/rc0/173stable，log e48fa860…；限定门通过，历史top分界/独立review/当前整体验收待，不与1019相加。

REGRESSION-S-SPEF-INTEGRATED-V3-FAILED（LOG39）：1034P1F156subtests158.23s/RUN158.9890298/600/rc1，173before=after+ZIP173逐SHA核符，logd067e517…；唯一旧assign-only wholeLib测试契约失败，不回退生产提取。原件保留。

REGRESSION-S-SPEF-INTEGRATED-V4-START（LOG40）：实际session11108/native childPATH/600pytest650wrapper，173before=current/ZIP173逐SHA匹配，与v3仅test_cells_extract.py变更53ad1713…。结果待，native改写5个受跟踪c17产物拟保真/diff再恢复，非科学成果。

FALSIFY-OI048-MAPPED-RIGHT-TOP（LOG41）：fix_independent_review_v2/PROBE_RESULT892ff5b7…，三源beforeaftercurrent符，native sourceY=A/单ztopinv正确fail，但前置dummyY=A后ABC选dummy假pass，mapped两文件SHA符。OI048仍阻断，不能以原双Verilog负控28P关闭所有接口；v4冻结结束后才改源。

REVIEW-INTEGRATED-V1-V3（LOG42）：独立REVIEWf980e55f…/70原件前后当前SHA-size全符，173×3ZIP/log/RUN/源稳定通过；仅原范围审计，v4未定。root_invocations/MANIFESTd6aaf66c…18原脚本/log逐SHA符，保真而非新测试/EDA。

REGRESSION-S-SPEF-INTEGRATED-V4-FAILED/ENV-ATTRIBUTION（LOG43）：1032P3F5warnings156subtests181.75s/RUN182.4937594/600/rc1，173beforeafter/ZIP核符。三CLI失败环境漏子进程PYTHONUTF8=1；同CLI同参两rawstreamsrc0但unset非UTF8/set1UTF8，RECEIPT5ccc14f8…/四源符；两文件13P2.72s定向绿、无生产改、不替新全量。

RESTORE-NATIVE-TRACKED-OUTPUTS（LOG44）：RESTORE_RECEIPT697c0b70…5当前path逐HEAD exactSHA符，generated/head快照各5件保留。首GitCRLF转换导致exactassert失败/finalize文本等同再写HEAD字节；非科学回滚或新实验，未宣workspaceclean。

PLAN-NATIVE-SPEF-MICRO-INJECTION（LOG45/2026-10-18）：根即执行真实OpenSTA tiny单buf实现反证：普通标识与literal escaped bracket/busbit身份，RC放大正控、错误pin负控；串行每次≤30s，opensta4a59e0f1…/spef5a9d6075…当前核符，actualLIB与输入须运行收据绑定。结果/路径待；不是收益实验/原族复验，不改变旧RC，不提前关闭escaped实际注入门。

NATIVE-SPEF-MICRO-ACTUAL（LOG46–47）：PRE_REGISTER433d9a22…/RESULTf9589064…43artifacts SHA、spef/opensta及actual LIB_SEQ ec0e1067…前后当前全符。实际两DFXTP夹buf reg→reg（取代无约束单buf草拟），普通/escaped-vs-busbit×RC40/4000um×API+annotation共8过程，另2缺pin负控，总10串行/每30s；四annotation均0未注入/0部分未注入，WNS4.43→-8.38同响应，缺pin两者null/error。仅微型注入实现控制，不是论文benchmark/收益或新同族实验；wrapper待根回传。

REVIEW-INTEGRATED-V1-V4/MICRO-ROOT（LOG48）：FINALfc5a87ef…listedSHA-size核符，REVIEWac4d71c4…/77evidence当前核符、692 ZIPmembers四套173/logRUN全符，v1/v3/v4保持fail/v2仅scope过。micro根wrapper16exit0/ROOT_ACCEPTANCE79f5725c…、真实OpenSTA3.1.0 binary96833cf6…，4API+4annotation+2neg有限slack但API全None，根通过/独立复核待；非科学benchmark。

REVIEW-NATIVE-SPEF-MICRO（LOG49）：INDEPENDENT_REVIEW56bdc6b1…/MD74e3aee5…/ARTIFACT0ef9e64d…实际读核43manifest+47总原件beforeafter/currentSHA-size/receiptSHA全符；仅tiny ordinary/escaped endpoint+annotation accepted，未重启STA/WSL/EDA。非致命WSLstderr留存，非物理benchmark或b18/任意域支持。

TDD-OI048-SOURCE-WINDOW（LOG50）：mapped_scope_repair/RED_SOURCE_WINDOW实际2F19deselected0.42s/wrapper5exit1；ordinary+BOM在top选择后原source新增wrapper仍normalizerrc0，PRE_SOURCE_WINDOW源原件保。根要求prepare前original-source绑定/保真、launch前后校验。fake边界非真实EDA，GREEN_V2 45P1skip属修前局部，GREEN_V3无结果；关联OI048/OI045不新编号。

TDD-OI048-MAPPED-SCOPE-FINAL（LOG51）：FINALcd5361e2…176artifact/四source当前SHA核符；14F2P/diagnostic2F6P/window2F原红保留，rc127仅bash环境；47P1skip4.64s/native7预期+baseline合且源stable，仅作者限定冻结。

ROOT-OI048-MAPPED-ORIGINAL-REPLAY（LOG52）：PROBE8b0d7cd1…三原输入逐字节同，singleinverterfail、dummy多rooterror，三sourcebeforeaftercurrent符/wrapper6exit0，原反例层过非历史全证明。

REGRESSION-S-SPEF-INTEGRATED-V5-START（LOG53）：session19880，显式PYTHONUTF8=1/nativePATH/600pytest650wrapper，174真实before/current+ZIP174逐SHA核符，result待/独立review待，不能以47限定或根反例层代全量。

STATIC-ABC-TIMEOUT-BYTES-PENDING（LOG54/OI049）：仅读ya0ba8bb70…_tail与两个CEC TimeoutExpired路径，partial bytes可TypeError疑点，未跑反例/红绿/修复，不新增执行或科学计数；当前v5源冻，后续独立异常呈现门验证，不等误pass或已修。

PLAN-D56-POST-SOURCE-CLOSURE（LOG55，仅计划待注册）：当前全v5/独立review/source-evidence阶段commit+push通过后，另以实际新cleanHEAD与manifest登记D56，先s27/s382×7共14pilot，余42须pilot验收后；全56验收前HEAD/code固定，记录文档可dirty/scoped source洁净。当前无正式newpin/manifest/D执行/结果，不把预备条目称正式实验。OI048当前实现反例层与历史省top证明影响分别验收，OI049仍待验证。

REVIEW-OI048-FINAL-CODE-EVIDENCE（LOG56）：INDEPENDENT9cbabd66…/MD9b99d34e…/receipt67922982…实际读核263原件beforeafter/currentSHA-size及receipt SHA全符；176owner artifacts/4frozen/20normalization/native7+baseline/root原输入byte对照/source-window链接受，仅读无新求解。首错派生文件名审查失败保真/纠正actual optimized.normalized.blif后过；非生产缺陷。仅当前复现范围通过，v5结果/历史top影响与OI049另门。

REGRESSION-S-SPEF-INTEGRATED-V5-PASSED（LOG57）：1056P156subtests208.27s/no skip-warnings，RUN209.1403265/600/rc0/wrapper210exit0/log3f5f39fa…，174beforeaftercurrent/ZIP174逐SHA集合核符，POST_VERIFICATION另存，完整收据独立补验待。仅当前冻结源码整体门，不闭历史proof/科学/timeout能力。

CLEANUP-NATIVE-FINAL-BYPRODUCTS（LOG58）：CLEANUP8e1bfdcc…85ZIP09ce0b9f…逐成员SHA核符、6items72movedSHA符、5tracked exactHEAD符；indexrefresh7608f2d2 beforeafter5blob同，修stat虚M后data状态clean，非科学结果改写/删除。wholeworkspace仍source+recordsdirty待stagecommit。

ACCEPT-CURRENT-IMPLEMENTATION-V5-FINAL（LOG59）：STAGE_ACCEPTANCE67da65a4…/MD20b001e5…/REVIEWv1-v5 0b7d8bed…/FINAL_CLOSURE9928cd3b…7final逐SHA-size核符；当前174/sourcebeforeafterZIP与五轮866ZIP成员/86evidence核符，v5真实1056P156subtests/no skipwarnings。当前复现实现scope接受，历史OI048/P08及OI049/OI046/四态/科学稿件门open；HEAD7231阶段sourcecommit/push尚待stage字节QA。

CHECKPOINT-SOURCE-FACTOR-F761EE1（LOG60）：COMMIT_PUSH_RECEIPTfddfa80c…HEAD/originf761ee1996…1278files，commit1.86s/push5.344s rc0；preownstagebytesdd91c9a3为1276/1256/0mismatch不回写，final1278/1258根报告待原件。新D56配置预登记pin=f761ee1996…/output experiments/20261018_r22_D_revalidate_v1/先s27-s38214pilot，实际manifest与执行待；不是已运行EDA/新baseline。

REGISTER-D56-F761-20261018（LOG61）：REG9277ac0e…runtime.657/wrapper5exit0/EDAfalse，manifest fd336745fd6bbb3039eaf5c043f67206a5567e74116b7787e093f89592a3ff4d at experiments/20261018_r22_D_revalidate_v1/，f761clean/45source121provenanceactualLibSHA全核，56jobs8×7：D fixed/adaptive/random_s1-s3及D_k1 fixed/adaptive。先s27/s38214selected、parallel2，runner3900outer3930；legacy/RGB/skipmapping/no-proxy/physicalSfalse，k8或k1/0.5ns/20轮/STA500/workers1按job命令。pilot尚未启动/无结果，不与C′拼接，旧历史dirtyruntime身份不补造。

ARCHIVE-FINAL-STAGE-BYTES（LOG61）：66c95710…原final收据1278staged/1258pinned/0mismatch，postcommit保真归档，不覆盖beforeown1276/1256。

EXP-D14-F761-PILOT-START（LOG62）：PILOT_INVOCATION3cc3c14e…/sourcef761/manifestfd336745…，actualsession36932，s27/s38214jobs，parallel2/workers1/global2STA；perjob3900/runner3930，pilotwrapper27800/parent27900。原stdout实际LAUNCH D/fixed/s27与s382，无completion/failure，正式pilot执行已开始/未验收；HEAD/code锁到全56，42待pilot接受。

AUDIT-D-COMPLETION-02（LOG63）：ROOT02bead5a67…冻结D/fixed/s27-s3822/56，completionSHA核符，根只读existingcomplete/runtime3.203/wrapper6exit0/无新STA-SEC。s27-.27→-.18/eval155/new87/cache68；s382-.98→-.83/eval272/new124/cache148，SECpassrc0，两adaptive运行/无failure。根作者后验不是独立全pilot科学验收，不补猜baseline总STA。

AUDIT-P08-HISTORICAL-OBJECTS（LOG64）：FINAL47149cd3…/receipt29aa4f19…104source当前SHA-size及artifactSHA核符，15旧CEC13单model成功+2实际读error、两A复用旧B显式topSEC11/0-137/0实核，未新增wrongmodulepass/无新EDA。历史候选身份/同期sourceBLIFSHA缺失及未覆盖对象继续unknown/P08open；最终适配script/原scratchinventory保真待补确认，不冒称全可重跑。

RECOVER-P08-ORIGINAL-INPUT-V1（LOG65）：RECOVERY3d4dc722…三原件SHA-size核符，原inventory2268B/7bb319f2…准确绑定104manifest，旧2290discovery/v1及FINAL_RECEIPT保留不改。最终adaptation为未保存PSstdin，originalstdin/localstdout unrecoveredunknown，不能认证最终原脚本/全流程byte replay；无新重审/EDA/HEAD变化。

PLAN-P08-INDEPENDENT-RECHECK（LOG66）：根指定archive新independent_recheck checker+invocation/log，仅旧15CEC/30BLIF及s27-s820 A复用旧SEC实际脚本/log/初终/state复算；原最终PSstdin仍unknown，不重建冒称原件，不重审81新proof/无EDA测试/Git，结果待。

RECHECK-P08-INDEPENDENT-CURRENT（LOG67）：FINALe8fa6a29…/checkerb7f9c00d…/RESULTbb013ab6…7artifactSHA-size和109beforeaftercurrent核符，180wrapper6exit0，newchecker.109s。15rawCEC/30BLIF独立解析13单modelequivalent+2实际读error、两旧A复用explicit-equivtopSEC11/0-137/0/Ainitialfinal/Bstate绑定符；104原来源+5control稳定。当前新流程可复算，旧PSstdin/同期sourceBLIF身份不补造/P08open，无EDA仿真测试/Git/81新proof重审。

AUDIT-D-COMPLETION-07/MONITOR11（LOG68）：ROOT07bfdb5474…冻结7completionSHA现核符，7/56verified/runtime13.297/wrapper15exit0/作者根只读无新STA-SEC。后monitor35caf891…11producer/14pilot,s27all7/s382r3运行+k1two待、无failure；7与11时点和门不同，不倒扩旧audit。fixed/adaptive两case终点/newcandidateSTA87-124同，反馈机制只读归因待最终证据，不外推8case或改去重制造正果。

DERIVED-D-PILOT-MECHANISM-TWOCASES（LOG69）：FINAL1f02fc99…/actual_v2AUDITb83f9abb…/script02fac5e3…10artifact+63来源SHA-size核符/45sourcef761/4completionROOT07，wrapper5exit0/120s只读无EDA。s27round4权重变但20序同；s382round5权重变、7-20序变而set同；326/292samebase对无新dispatch，pre-evaluator去重后无更新权重调用，cut级8/11calls不等STA，candidate与87/124newSTAevent同序。只两case四对象限定诊断，不外推full56/普遍反馈无效，不改去重造效果，v1/v2审计均保真。

MONITOR-D-PILOT12/FIGURE-PLAN（LOG70）：31cd6258…snapshot producer12/14，s382k1fixed finalSEC/helpers.v更新、k1adaptive待，无failure/sourceunchanged；根audit07仍冻结7，不填14完成。拟现有两case四对象机制独立诊断图预览，未实际生成/QA，不写主稿结论，产物后续登记。

CHECK-B3-C-ADAPTER-CURRENT-PIN-START（LOG71）：INVOCATION35e9b56f…v2/session49033/twoisolatedpytest/B3+C注册mock/300wrapper330parent/UTF8，当前f761源pin，result待。v1snapshot相对绝对混用ValueError在tests之前，原harness保/首MD转录非rawlog；v2ROOT绝对化新独占目录。无真实EDA/历史身份恢复/源改，不影响D冻结。

MONITOR-D13（LOG72）：snapshot0d4dd5a5…13producer/14，最后D_k1/adaptive/s382实际JOINT STA日志更新，failed空/pinunchanged；audit07仍只冻结7，独立全14验收未出，42不得先跑。

CHECK-ADAPTER-CURRENT-PIN-PASSED（LOG74）：RUN22156fc7…HEADbeforeafterf761/源stable/codeclean，B351P19.72s wrapper25/C84P98.30s wrapper102，日志SHA符。5810beforeafter/current=174code.py+B3tree5628含历史sandbox+Ctree8，不是5810生产文件，mock/static非科学EDA。

ACCEPT-D14-INDEPENDENT（LOG75）：FINALb3c6c8d5…/RESULT27efaf79…/checkerd282313a…7final产物SHA-size核符，14jobs2471records/1369newcandidateidealSTA+14baseline/1102cache/0preSTAtrial/14SECpass、s27each11/0/s382each90/0，45source/Lib/manifest和4533原件稳定，36.531s/wrapper41exit0。仅读无EDA/测试，仅14两case接受，42actualstartawaited，不外推56/物理/四态。

EXP-D42-F761-START（LOG77）：REMAINING_INVOCATIONd33ef208…绑定D14根/独立/根接受191b35b6…后，actualsession96821启动六电路42jobs，samef761/fd336745/parallel2/jobworkers1/3900-3930/batch90000-parent90100，stdoutfixeds420-s641 LAUNCH；尚无42结果，pilot原summary单存不覆。

DERIVED-FIG-D-MECHANISM-PREVIEW02（LOG78）：FINALa1a150fe…54artifactSHA-size+CSV80-40-2行核符，script20fc7b98…/PDFSVG600dpiPNG/contract中英caption；作者QA19P2W0F/alignment0/collision0/glyph7pt/visualpass，根独立review待，仅2case4objects不主稿/不full56。iteration01保留/02Candidate records改名避cache误读。

ARCHIVE-D14-RAW-START/PRODUCER-S27（LOG79–80）：D新archiverfcc1d170…由原C′模板cacfba82…适配，2cases7arms each/2archiveparallel2threadseach900wrapper，source45/Lib/provenance/pilotacceptance绑定。s27producer7e590d0b…2061files32411467Bto1943986B/495ba5e6…member7zt/newrestoreSHA+source稳定，通过producer门/rootpost待；s382运行，无EDA/源改/Git。

ACCEPT-ADAPTER-MOCK-FIXTURE-ARCHIVE（LOG81）：ROOT_QA7b62e0e9…51/84pass/174source稳定，QAfixturesZIP431c66a8…3901files8725147Bto2764621B，CRC/逐memberbyteSHA根核，原temps保留；5810宽域不是生产数，不入旧B3sandbox/不升科学EDA。

ACCEPT-D-FIGURE-PREVIEW-ROOT（LOG82）：ROOT3067eb58…75readSHA当前核符/80-40-2CSV独立原数据对应、全PNG-PDF四panel根视觉，120wrapper6exit0。仅2case diagnosticpreview，非正文/full56/收益结论。

PLAN-A8-EXACT-SEC-PROPOSAL（LOG83）：根proposal待确认，当前pin统一A8 exact新SEC批次补同批runtime/noSTA；对象manifest/tool/命令/超时待注册，未执行/未改正文，旧复用runtime来源不可拼。

ARCHIVE-D14-FIRST-TWO-PRODUCER-DONE（LOG84）：index4358d19a…s27receipt7e590d0b…/s382receipt436eb575…原2061-3808file32411467-837866652B→1943986-6304539B，总8248525B，两包source/member/7zt/newrestoreSHA全true，31/118wrapperexit0，ROOT_POST仍待，非全56raw齐。

ACCEPT-D-RAW-ARCHIVES-FIRST-TWO-ROOT（LOG86）：s27ROOT_POSTa4738c47…/s382a20edd82…accepted/source-restored2061-3808/volume-sidecar-logSHAallmatch，checker18056e1f/4.969-11.296s/wrapper21exit0；原producer门独立通过，2/8Dcase归档闭合，不外推full56/noEDA。

MONITOR-D-PRODUCER16（LOG87）：ee22619b…snapshot16/56，新增fixeds420-s641、adaptive2actualevalSTA持续，failed空/sourcepinunchanged；正式独立接受仍14，不把producer16当验收数/full56，session96821继续。

MONITOR-D42-LIFETIME-START（LOG88）：session99002/INVOCATIONb1f8dabb…watcher06912194…每60s调用已有readonlymonitor/每次30s/截止90300外90400，PROGRESS.jsonl+timestamps，见结束receipt/失败/漂移停止。仅当前batch96821生命周期，非automation/科学接受/新EDA，monitor依赖实际scratch脚本已records原byte快照+SHA。

PLAN-C03-C04-A8-UNIFIED（LOG90）：proposal0e367085…原A8exactpairs/87sources/f76145sourceLibpin，s713不换A′baseline；旧六A6与两B复用proof/计时来源分别保，旧表点数和runtime混用拟同批新证明纠正，草稿非主稿。

EXP-A8-UNIFIED-REGISTER/START（LOG91–92）：manifest2cdedb1d6316188a0ea2ebd592c879efa3ef81fabb4e033632537dd424223325，16原A input rawSHA-size与45source/Lib当前核符、快照decoded双绑定/接口二态helpers预飞；WSLYosys0.33binary88c0a12b…，serial1/每180/whole1800，registrationproverfalse。后RUN_INVOCATIONa095cbff…02:31:44已启动串行8/partiallogs，全结果待；STA0/mapping0/search0，计时prover+log排prep、DSTA并发无跨法性能claim，不改HEAD/code。

EXP-A8-UNIFIED-PRODUCER-PASS（LOG93/OI050）：RUN8ff8909b…actual8proofpass/60s/wrapper67exit0，source-input-toolstable/STA0，72artifactSHA/8rawEQUIV末log实际点数11/90/79/124/126/139/146/228全0核符，wall .281/.281/.250/.313/.328/.344/.391/.407精度原件留。独立接受/稿表修订尚待；s820新139与旧137/138差异先核脚本模型，不期待回填旧数。

MONITOR-D18（LOG94）：fd3f95a8…producer18/56/adaptive s420-s641新增complete，random1两例实际STA中/无failure/pinstable；独立已接受仍14，A8只SEC不计DSTA。

ACCEPT-A8-INDEPENDENT-ROOT（LOG95）：独立FINAL87b3b721…/RESULTeae2ae82…8finalartifactSHA-size核符，173sourcesstable/45source-f761Lib-WSLbinary88c0原16pair模型rawhelpers/top/log/runtime核；95.375s/wrapper98exit0。ROOTa6caf8a1…接受新8行；s820old137/new139 proof构造/modelstate表示不同，extra2cell精确身份unknown无RTLIL，不比pointset/强弱，不新EDA。

EDIT-A8-MANUSCRIPT-AUTHORIZED（LOG96）：双语A句表按新8行实际值改稿、2passbuild38pvisual/sync已根授权，完成收据待/OI050open；不把授权当已编译/改稿完成。

PREPARE-D-INDEPENDENT-COMPLETED-V2（LOG97）：PREPAREDd3c17a36…/checker59e51ed5…仅compile syntaxchecked，未D16/18新验收，无EDA/Git；显式frozenAUDIT_N+exclusiveoutput及allstartcompletion集合约束，等根派发/实际结果。

PREPARE-D-NEXT-REVIEW-ARCHIVE-V2（LOG98）：TOOLS38931534…6artifactSHA-size核符，checker59e51ed5 --audit/--output不改，archiverv2b60cc3f1…--acceptance显式门/rootaccepted全冻结set等同+case7SHA齐；full56仅56key全部实际原件核后true。原pilot/v1不变，syntaxonly prepared未执行/未审18/未压新case，等根正式28+/case准入，无EDA/Git。

PRESERVE-A8-ADAPTER-GIT-BYTES（LOG99）：原gitattributes8fb8d07f…先保，新A8/当前adapterprefix -text、actual两文件textunset；图/metadata02已有规则，不变code/HEAD，不commit。

EDIT-BUILD-A8-METADATA02（LOG100）：EDITc0001a6e…两Tex afterSHA当前符/eachA sentence+SECtable限定、14table7includegraphics不变；zh4f9d05df…/ene9e48ea5…4compilepass0/source稳定、当前buildPDF173ae809/d129dbe4 SHA符，38pvisual/copy同步待/OI050open，无新STA/WNS/code。

RENDER-A8-METADATA-V1/EN-FLOAT-V2-PLAN（LOG101–102）：zh840fd4f9…/en5b35fb1d…static12+26render0/A8行匹配/其它13表7图引用保持，visualpending；首QA labelregex badescape失败保真不算TeXbug。根实际before/new页比对ENtableold15→new16但ref14，限定exclusive ENfloat[!htbp]v2保存v1后2passbuild+26prender/visual/copy sync待，ZH不重跑，不新EDA/数据/代码，OI050open。


BUILD-A8-EN-V2-V3/PLAN-V4（LOG103–105）：首canonicalPDF写入失败322a03a4…rc1/旧PDF不变，exclusive attempt02编译2pass0/26p但table16；v3build19ccd1e3…/QAd62d5eba…2pass0/26p/table16/PDFb4e6da09…，不构成布局final。根授权现有placeins的A表后FloatBarrier独占v4，仅防跨下一实验、不强制页号/字号/数据。等待actual/独立/根视觉与副本同步，OI050open，无新STA/生产。


ACCEPT-D-CAPTION-EN-V2（LOG107）：ROOT_CAPTION_EN_V2_ACCEPTANCE8dcf657c…实际true，selected86831fdb…与SUPPLEMENT18e08613…绑定；future集成选新caption，原图/data/FINAL不动，无重绘/EDA/新QA门。


2026-10-18 EN v4当前（LOG108）：EDIT8a918cf6…仅一FloatBarrier，build d65bd931…2pass0/5.375s各，PDF5d1be23c…；QA769da499…实际28页/render0/A8行与13表7图保持。A图15/表16先于B正文但浮动页留白增加，根暂缓sync/final并独立核Fig3字形/物理尺寸；OI050仍open/canonical与metadata未同步，ZH不重编，不把28页写26或局部绿写交付。


LAYOUT-A8-EN-V4/PLAN-V5（LOG108–109）：v4 EDIT8a918cf6…一barrier/source d7c5c180…，两编译0/28页静态通过但根不接受新增留白；Fig3实测MEASUREMENT016641c0…min8.184960pt，.70width投影7.345477pt，授权v5仅EN include宽.70，向量源/数据/中文图不变。投影不当新PDF实测，实际字形≥6.8/读序/空页/contact+根独立最终接受/sync待，无新EDA。


ENV-D-RESOURCE-SCOPE（LOG110）：运行环境口径（LOG110）：D期同时存在mock adapter QA、只读7z压缩/恢复、A8串行SEC及LuaLaTeX/Poppler；科学STA≤2电路，但整机非独占benchmark。observed walltime不得直接作独占或跨方法速度因果；输入/结果/实际STA计数不变，不据此判D失效或重跑。严格速度主张另登记受控同硬件计时协议。 各阶段actual commands/time/log分别保存，不新增科学实验、故障或OI。


2026-10-18 EN v5实际构建/字形（LOG111）：EN v5仅Fig3 include宽.70，当前source d89b207c…/PDFc2783046…实核匹配；两编译rc0/26页render0，图和A表同15、下一Cross-dataset标题16，实际图内label/tick/legend最小7.345520pt≥6.8。作者静态/实测门已过，visual字段仍pending，最终不同owner/根接受与canonical/metadata同步待，OI050open；ZH不重编，原图vector/data不动。 EDIT4a1c114b…/build825dd0eb…/STATIC128315a8…/actualglyph23f79ebf…；保v4投影为预估，v5为实际PDF测量，未提前最终接受。


MONITOR-D28/ROOT-EN-V5-PAGE-VECTOR（LOG112）：monitor974fa2ec…03:01UTC实际28producer/56，含s713fixed，s713adaptive/s641k1adaptive active/failed空/sourcepin稳定；accepted仍14。根实看ENv5第15页清晰/顺序正确要求继续既定sync；14向量c4ff6ad9…current=固定f761blob逐SHA核符，非pre-filesystem。作者final/完整视觉/独立与根最终接受/sync待，OI050open。


2026-10-18作者最终v5/实际副本同步（LOG113）：FINAL_QA_v21902d011…作者38页视觉/限定inverse scope/A8行与EN实测字号通过；SYNC29a6ee35…ZH build-root-manuscript三PDF同173ae809…，ENv5与canonical build同c2783046…，4metadata已同步，记录员当前逐源/PDF/metadataSHA核符。Tex冻结/作者最终清单收尾；不同ownerchecker1291f4e9…仅syntax prepared未执行，独立与根最终接受待/OI050open，不再误写同步未执行。


AUDIT-D-ROOT28/INDEPENDENT28-START（LOG114）：根新增冻结ROOT_COMPLETION_AUDIT_28（1db9b0fb…）已只读重放通过28/56、50.407s（wrapper56.781s/0），含s713fixed而非完整前4case；不同owner既有checker59e51ed5…已实际session51969/run_28_v1启动（900/930，INVOCATIONf91355fc…），开始集合正好28、后续completion排除。当前不同owner正式accepted仍14，28独立终验待，无新STA/SEC。 根RUN6a13a8cd…/independentINVf91355fc…保exact argv/timeout/checker-source及auditSHA。


2026-10-18作者最终收据冻结（LOG115）：FINAL_RECEIPTbc951338…/397件清单4e9aaf1c…明确authorcompleted/selectedENv5，QA1902d011…/SYNC29a6ee35…/POST_SYNC2602df5a…链齐，当前源/PDF/metadata回读一致。全部构建和测试已停，Tex/PDF冻结；根已派发不同owner独立终验，但实际invocation/结果收据尚待，不提前闭OI050。D s420七臂归档仅获准备指令，须D28独立接受和根准入再执行，无新归档/EDA。


FAIL-D28-INDEPENDENT-CHECKER-V2（LOG116）：D28不同ownerchecker_v2实际run_28_v1失败（FINAL1061094c…，20.812s/rc1，前三job后s641缺cached_from_seq KeyError），未完成独立28验收。根已派只读归因：实际STA缓存重放、重复hash无重放、缓存前置拒绝须拆分类；v3待根评审。D root28仍已通过/不同owneraccepted仍14，不预判科学run失败、不改生产结果/HEAD、s420归档待准入。

START-A8-MANUSCRIPT-INDEPENDENT-FINAL（LOG117）：INV946ec65c…actual03:05:58/checker41fd6997…/session33239/300-330，作者bc951338冻结后只读原件+独立PDF渲染/38p实际视觉，未编译EDA；运行身份不混准备1291f4e9，最终结果待/OI050open。


2026-10-18独立静态/渲染完成（LOG118）：RESULT53f76dba…/runtime6.563s（wrapper11s/0）核562来源前后稳定、397作者清单及当前45源/proof/rawcompile/readback/copy/metadata；独立38页实际视觉仍进行，最终receipt/根接受待/OI050open。准备checker1291f4e9…未执行且未另存文件（消息/tool历史仅），最终397schema/v2-priorQA适配后实际首次运行41fd6997…；不伪称准备原件可恢复。


2026-10-18不同owner最终38页接受（LOG119）：FINAL334a893b…/VISUALaf2c892e…/REPORTfd1aa6f2…已冻结，63final原件逐SHA-size核符/562来源视觉后仍稳定。独立实际12+26页/10contact+两表页高res，A8行/完整注/图3最小7.345520pt及A图表先于B正文，无新裁切碰撞或异常空白，限定接受A元数据/EN局部版式/同步。根最终接受待/OI050暂open，非整体科学或投稿接受。


2026-10-18根最终接受（LOG120）：ROOT_MANUSCRIPT_ACCEPTANCE472b441b…实际accepted，重核独立63原件/562来源、作者finalsource/PDF/canonical与metadata、八实际表行和29图中文字min7.345520pt、45源与HEAD稳定。OI050仅A句表/EN Fig3包含布局与A-B读序/编译副本与metadata门关闭；非其它科学或投稿验收。ZH173ae809…/ENc2783046…为当前有效工作稿PDF，旧失败及v1-v4留档。


RED-OI049-EXPLICIT-BYTES（LOG121）：RESULTbb5e332b…3mockCEC，str-empty正常timeout/syntheticbytes publicAPI TypeError，45source+HEAD稳定/noEDA。v1-v2 API前harness假设失败不作代码红灯，v1仅tooltrace转写无rawlog；保持open待D后修。

MONITOR-D31（LOG122）：7d275ba8…actual03:09:21UTC，producer31/56/adaptive-s820与random1-s713真实STA Tcl active/failed空/pinstable。root28冻结通过、独立v2 schema失败待v3评审，正式独立仍14，不外推31accepted/full56。


PRESERVE-OI049-EVIDENCE-BYTES（LOG123）：GITATTRIBUTES_RECEIPT930f477f…唯一追加OI049/** -text，实际textunset，before1e367444…prefix原字节完整保/afterbb37726d…记录员当前核符；不stage/commit/HEAD/code更改，保原rawCRLF-UTF16日志SHA，非新增实验。


DIAGNOSE-D28-LEDGER-DUPLICATE（LOG124）：DIAGNOSIS6772089b…/INVc504dc33…180wrapper/readruntime3.296s/581稳定；仅ROOT28，新candidateSTA5243、真正有launch缓存复用5821、hash无重放29、未缓存preSTA拒绝76/cachepreSTA0；旧cache5850=5821+29逐job相等，不改producer或schema。v3准备须根评审/再独立过，accepted仍14，未审新增3completion/无EDA。


CLARIFY-OI049-BOUNDARY（LOG125）：CLARIFICATION9140b292…保原SETUP_FAILURE不改，v1合取assert失败不能区分类型/空；v1/v2actual type-value均unknown。redv3仅public direct-CEC193→215→_tail902显式注入，不证明_run_abc_cec/mapped helper均复现/noOS-EDAstream推断，非falsepass/D后修待。


REVIEW-OI049-READONLY-ATTRIBUTION（LOG126）：FINAL1d89a8a7…/RESULT5cb89699…/REPORT3c583206…7finalSHA-size核符、72原件/45sourcef761稳定；AST/hash readonly.172s/60wrapper实际5s0，无import生产/重probe-pytest-EDA-Git。只接受direct check_yosys_abc_equivalence nonemptybytes注入归因，mappedhelper未实测/非falsepass/OI049仍D后修open。


PREPARE-D28-CHECKER-V3（LOG127）：PREP16f6fdd2…/DESIGNfd3f0dba…/checkerf6b053df…/minimaldiffe3c6cf65…SHA当前核符，仅AST未执行；ROOT28 immutable registeredsubset/extra明确排除、full56仅全key验、四nonlaunch严格分类缺base另记chain/cache推导不改raw，原STA-SEC-source门全保。root代码评审后新exclusive执行，accepted仍14/noEDA。


START-D28-INDEPENDENT-V3（LOG128）：INV2c4d1c7f…actual03:17:07/checkerf6b053df/ROOT281db9/diag6772089b-designfd3f-diffe3c6绑定，根完整源审后批准immutable28subset/extra排除与严格分类，原rawSTA/SEC/45pin门保；session60030/900-930实际运行、结果待/accepted14/noEDA/生产HEAD不改。


MONITOR-D34/V3-FULL-ENTRY（LOG129）：46b944dd…03:18UTC实际34producer/56、random2s713-s820active/failed空/pinstable；v3实际过旧s641失败点并继续VERIFIED，无final收据accepted仍14。后续全56独立原件审查入口固定为`project_docs/evidence/r22_D_revalidation_20261018/ledger_duplicate_diagnosis_20261018/checker_v3.py`（f6b053df…）；原checker_v2/TOOLS_PREPARATION保历史。当前28的900/930不是未来全56已登记timeout，全56按实测量/runtime另登记并持续监测。 全56前不commit/变HEAD/code。


ACCEPT-D28-INDEPENDENT-V3-ROOT（LOG130）：FINAL938ae623…184.844s/wrapper185s0、RESULT79ad2ce4…16407stable/45sourcef761；ROOTf14c3306…120wrapper5s0 acceptedfrozen28/extraexcluded/full56false。11169records/5243candidateSTA+28baseline/5821actualSTA-cache/29hash-no-replay/76preSTA/0cachedreject/28SEC0unproven。monitor20174131…producer35无failure；s420七臂获单例归档准入，s641缺1未准入。v2失败保，不变生产/结果/HEAD，futurefull56用v3另登记timeout/监测。


START-D-S420-RAW-ARCHIVE（LOG131）：INVcf6868c0…actual03:21:40/archiveb60cc3f1-runnerff57f032-ROOT281db9-rootacceptf14c绑定、onlys4207arms/session49553/900-930监测10s；producer/restore/rootpost待，已接受raw仍2/8，s641未准入/不重跑前两包/无EDA-sourceHEADchange。


QA-RECORDS-D28-CHECKPOINT（LOG132）：records_checkpoint_01/RECEIPT 2b9031aa16970f0e52ed2f173c19af4cdaf1df8e00af8787ecb0eda308876b69，30s wrapper/40parent的check_record与CRLF感知semantic whitespace（ignore-space-at-eol、排除evidence/data）均0/5.437-5.422s，stdout/stderr/script/HEADbeforeafter全保。仅.gitattributes未来LF-CRLF提示，不改源/HEAD或stagecommit，不科学EDA/测试。


PRODUCER-D-S420-RAW/ROOTPOST-START（LOG133）：receipt09e5cd66…7591raw-provenance/1285328911B→8182410B/vol35c38aec…、sourcebeforeafter/member-size/7zt/fullscratchrestoreSHA全true，195swrapper0；rootpostINV77d88e10/checker18056e1f unchanged/session4449/300-330实际运行，未接受前raw仍2/8，7591非生产源计数，无新EDA/HEADchange。


FREEZE-D56-AND-ALL8ARCHIVES（LOG134）：归档器还读当前45runtime/Lib核f761，完整56独立+根验收和8case archive/rootpost均齐前HEAD/code不解锁/不commit，当前稿图证据dirty保留；其后源修/回归/新cleanpin B3-C，不停止科学96821/60s监测99002。

ACCEPT-D-S420-ROOTPOST/MONITOR37（LOG135）：post ecc44332…/RUNfc745c5b…26.015s0（checker21.828s），7591原件+恢复全sizeSHA/1vol8182410B+sidecars-commandlogs核符，producer09e5/vol35c38绑定；raw3/8=s27-s382-s420。monitor514f6b29…03:25UTCproducer37、random3s820/k1fixeds713active/noFAIL/pinstable，independentaccepted28不扩。


QA-RECORDS-FINAL-CHECKPOINT02（LOG137）：RECEIPT a59ae23eb4009f7d446abcb660215cf1e6892e897ab7fbb9bf8fc288937c0df0，check_record0/semanticwhitespace0（cr-at-eol/ignore-space-at-eol/excludeevidence-data），各5.438s/30wrapper，HEADbeforeafterf761稳定，原stdstreams/argv/script保。仅.gitattributes未来CRLF提示，不stagecommit；当前37producer/accepted28/raw3，两门56+8post前源HEAD锁/科学监测继续。


REVIEW-R23-CHINESE-SCOPE（LOG138）：用户“审稿中文稿”新范围，只读全稿五视角/先盲标准后看稿；不喂旧r22reviewers意见、不改正文图源、不EDA。当前Tex c750ff9c…/PDF173ae809…与HEADf761/codeclean已实查；r23目录/快照由主线生成后另记，未预称已建。

PRODUCER-D56-COMPLETE-NOT-ACCEPTED（LOG139）：remaining106a6234…actual42finished0/5898.406s/head_afterf761；04:01monitor30098530…56/56completion、active[]/failed[]/writing[]/sourcepintrue；lifetime68c282be…93checks/batch_receipt_observed/runtime5521.047s自动止。正式独立+根仅28/raw3，不解锁/不本轮启动终验归档。


REGISTER-R23-INPUT-CONTRACT（LOG140）：INPUT2d76968c…20输入逐SHA/母稿Tex c750-PDF173核符，FIELDfcd0e2e2…五same-family新forknone两call/先盲标准，未校准无具体期刊fit。contract9e8eb029…/QA1a3651b0…Schema13.2 valid/.703s0，单eligiblemandatory D1-D2-D6 SC12 warning保，非论文缺陷；最终报告未齐。

RESTORE-R23-REVIEW-VALIDATOR（LOG141）：ARS检查器actual包根scripts/47e800dd…，非reviewer/scripts；scratch目标jsonschema4.25.1+deps安装15s0/原log5c373372…，子进程PYTHONPATH由INV记录，不改科学venv/toolchain/源。工具预飞路径/import失败不当论文缺陷。


REVIEW-R23-PHASE2-FIRST3（LOG143）：EIC5fd9ab9e/method52ce0f48/perspectivefd90c1f6 actualconformancePASS，分别5.734/5.516/1.328s，wordtriggerwarning保；非稿件已过/domain-DA及final待。

REVIEW-R23-EXISTING-EVIDENCE-CROSSWALK（LOG144）：B17 resultb5a0d5d4/POST9d12b8fc existing13.375s/12879-0/NOR4Bonly/rawbytes-goldgate绑定，稿L497旧12812+1，后续仅复用证据更新绑定，不重证明/不本轮改稿。Cprime72a34da9c3全验及MATCHED16ef78ed8a partialdiagnostic/解释限制分开，新族不替旧C-D，无新EDA。

## 2026-10-18 r23只读审稿（LOG145–149）

本轮无新EDA/STA/SEC实验。只读核对A8日志、b17已完成新证明、C′72与16配对，确切来源/SHA见r23/ROOT_EVIDENCE_CROSSCHECK；不重复登记为新科学实验。D producer56完成但正式accepted28/raw3保持。

## 2026-10-18 r24修订复用分析登记（非新EDA/科学效果实验）

| ID | 对象/版本/输入 | 方法与输出 | 当前状态与限制 |
|---|---|---|---|
| R24-METHOD-STATIC-20261018 | f761当前实现；C′ runtime pin3ea0f75及runtime_inputs.zip620a0eb9…；A8既有proof与A物理pr.tcl/旧SPEF证据；人工六门输入 | paper/zh/review_rounds/r24_20261018/METHOD_EVIDENCE.json SHAbae97315…、METHOD_EVIDENCE.md d08ecca3…；逐源SHA/行号、静态动作实例化、公式/域与参数取证 | worker已交付、根审待；非新STA/SEC/计时/科学效果实验，不替历史runtime身份或历史物理效果复验。不得重做已验A8/b17证明；源/HEAD冻结不变。 |

| R24-QUANTITATIVE-REUSE-20261018 | ANALYSIS_REGISTRATION.json dc3b30bc…先登记22输入（C′矩阵/manifest/同库/旧ITC/B17设计/模型审计+W1的16网表），HEAD f761冻结 | QUANTITATIVE_REUSE.json4eb77b24…：9arm候选STA与端点、W1逐层次cell/Liberty面积、ITC19/16/3分层、b17 accepted raw端点绑定；全部注册输入稳定，记录员实际逐SHA复核 | 已完成静态原数据再分析；非新STA/SEC/EDA/计时，不新增timing值。W1-U1同847/0.16125；L不是纯排序；三态3对象unsupported并保时序观察，不能19/19等价通过；旧runtime身份边界保留。 |

## 2026-10-18 r24正式新实验预登记（执行结果待）

| ID | 被测对象/配置与来源 | 反驳先行与预算/监测 | 状态与边界 |
|---|---|---|---|
| R24-PAIRED-SPEF-CPW1-S382-20261018 | PAIRED_SPEF_DESIGN f212e784…；精确C′W1/s382 initial/final raw pair（新鲜支持域实验，非旧scan恢复），先核90/0模型证据/支持域/Source-Lib-HEAD pin | 根PAIRED_SPEF_ROOT_DESIGN_REVIEW已approve_execution；先同网表u40反驳控制，再u10/u40/u160固定顺序；最多16 API STA+8 annotation replay；单case600s/global1800s，按wrapper/日志监测 | 正式新科学EDA，worker执行结果待；不能计作静态再分析、不能提前报成功/注释完整，不能用它补旧scan runtime身份。生产code/HEADf761冻结，D仍producer56/accepted28/raw3。 |

R24-PAIRED-SPEF-CPW1-S382-20261018 **FAILED / nonaccepted（LOG171）**：同网表u40反驳控制按预注册门在14.238s停止，实际4 API STA+1 annotation replay=5新STA；其余u10/u40/u160未启动。ideal两侧-0.98/物理两侧-1.90虽均delta0，但真实annotation存在43 partially unannotated、0完全unannotated，层级helper端口与leaf端点不闭合，结果不得作负载效果证据。保FAILURE及全部raw警告；源pin终验待worker回执。不得静默剔除网或修改门取绿。后续flat新输入+新SEC只处于v2设计请求、尚未授权执行，不重试本次、不混旧OpenROAD A族。

R24-PAIRED-SPEF-CPW1-S382-20261018停止审计补齐（LOG173）：PAIRED_SPEF_STOP_AUDIT.json03b306f5…实际50335B、HEAD/source/Lib/两raw输入前后SHA吻合；实际4API+1annotation=5STA，4API raw双流按原规则复现sta.log/argv/600timeout，annotation43partial分CK1+leafQ21+组合到leafD21组。无重试/后续扫描，所有新原件清单保留；状态仍FAILED/nonaccepted，OI051不关闭。下一flat+SEC方案仅设计，不是已补做实验。

## R24-PAIRED-SPEF-FLAT-V2-STAGE12-20261018（LOG175；阶段授权预登记）

根通读PAIRED_SPEF_FLAT_V2_DESIGN.md SHA7de9771d…后，仅批准有界第一/二阶段：2次Yosys原生flatten（保standard-cell blackbox、展开用户helper、无综合/ABC/重映射）+两份original→flat新SEC。原始C′W1/s382两raw SHA608cf28c…/5745c7fb…与TT库、HEAD/source固定；新的flat输入和SEC附helper副本须逐SHA登记、flat top保持一致。此为新派生输入族规范化+证明，不是旧失败重试/修production/OI051已修。**STA阶段当前0授权**，不得据预案直接运行负载扫描。实际运行配置、wrapper超时、产物SHA/结果待worker独立准备/执行回执；v1失败原件持续保留。

阶段12设计参数补充（LOG175）：PAIRED_SPEF_FLAT_V2_DESIGN.json SHAce042520d71af073a797360ae4433ccd51575d8b7d144931b15d631681e37aa0；原生flatten每次60s、两份SEC各180s、全阶段600s，Yosys0.33/2584903a060及binary88c0a12b…先核。静态全port/type/pin/alias/state守恒不过即停不SEC；2SEC各原raw→其flat，flat两输入冻结后须根另审新STA预注册。STA仍0授权，执行前完整root批准receipt由worker保存，当前登记不预报产物/通过。

R24-PAIRED-SPEF-FLAT-V2-STAGE12-20261018作者完成（LOG178，根审待）：FROZEN_DERIVED_INPUTS.json2a9c6ef5…已冻结两flatSHA5f44719a…/1d179ced…；2flatten+2原→flat SEC，静态10port/90stdcell逐pin/21dfxtp与106net-94bit别名守恒PASS；两SEC各129/0（simple新增4、induct新增56，非旧A8），26.216s/wrapper31s，source/Lib/rawinput/HEAD稳定。**STA实际0且0授权**，未自动接阶段3；须根审新对象与单独新STA登记。v1 FAILED与OI051继续保留，不能称生产层级支持已修。

阶段12根复核未接受（LOG180）：FROZEN2a9c6ef5…含PROGRESS.jsonl post-freeze append漂移，登记a1b039d8…/1239B→91812adb…/1392B；根报告其它artifact SHA-size吻合，但审核脚本按冻结门停止。须保旧manifest及原日志，新增POST_FREEZE_AUDIT/最终清单，解释append完成事件并再根审；未准入新STA，不能称原冻结全件PASS。此记录不把元数据append当源/flat/SEC本身漂移，也不隐去合同门失败。

阶段12根限定接受（LOG181）：修正manifest360ab10f…的68件已根逐SHA-size核符，旧PROGRESS1239B前缀同SHA、仅153B末complete事件append已独立证实；原2a9manifest/日志保留，POST_FREEZE归因后新清单复核不是覆旧。PAIRED_SPEF_FLAT_V2_ROOT_ACCEPTANCE.json接受仅新派生flat输入，根重算两侧94bits/10ports/90type-pin/21DFF及两原→flat129/0；**未接受物理效果/未修OI051/STA仍0，须新设计单独预注册根审**。

## R24-PAIRED-SPEF-FLAT-V2-STA-20261018（LOG183；正式新STA预登记）

| 配置 | 预注册值/身份 |
|---|---|
| 根批准 | 根实际读STA_DESIGN.json887ccacc4fd57a9c87009544cc3e37a0314ea052cd9944e0610d2a335e17bd19及MD93e4…后明确批准4case，worker保存reviewreceipt；批准不是结果 |
| 输入/版本 | f761当前生产源/TT Lib ec0e1067…与固定工具；C′3ea0f75原端点经保standardcell helper-flat派生，flat baseline5f44719a…/final1d179ced…；两原→flat各129/0/根派生准入76225a8a…/finalmanifest360ab10f… |
| 顺序/反驳门 | control同网表u40先行，双侧SPEF bytes相同、ideal/annotated delta0、两annotation 0partial/0unannotated；成功后pair u10→u40→u160固定，不调参取正收益 |
| RC/时序 | TT025C1v80/CK0.5ns，无新增IOdelay；L=unit*max(1,sqrt(fanout))*1*1，R0.09Ω/um、C0.21fF/um，负载代理非几何/签核 |
| 预算/监测 | 每case4API+2annotation，最多16API+8annotation=24新STA；单case600s/global1800s/annotation60s，严pin漂移/注释/返回值门，异常即停不盲重试 |
| 隔离/状态 | 新目录paired_spef_flat_v2_STA_runs，v1原5STA失败/43partial及OI051保留；结束先关journal再最终manifest。执行刚获批，actual launch/结果/根后验待，未接受物理WNS，不称生产支持修复 |

| ID | 对象/输入 | 静态输出 | 状态/边界 |
|---|---|---|---|
| R24-CP-CURVE-RECONSTRUCTION-20261018 | 根授权既有C′72原event/trial/commit+MATRIX72收据，保原source/runtime身份 | audit_r24_cp_budget_curves.py；previews/r24_cp_curve_audit_v1/CURVE_RECONSTRUCTION_AUDIT.json77b1ecff…：72可重建、6858候选actualSTA/6930含k0曲线点/192commits、0cachedcommit/0acceptednotcommitted/0failedlaunch | worker预审已交付、根审/新8panel图仍待；只读原数据曲线重建，非新EDA，不增加历史测量次数，不替换旧图或混候选点/基线点/commit。 |

R24-PAIRED-SPEF-FLAT-V2-STA-20261018 producer完成（LOG185，根后验待）：RESULT eebc5398…/73102B，实际4case/16API+8annotation=24新STA，不含v1失败5；194成员先closejournal再冻结。controlu40 delta0/同SPEF bytes；pairu10理想+0.15/代理SPEF+0.11，u40/u160代理SPEF均0改善。8annotation replay均rc0/0partial/0unannotated/与API WNS同。worker最终raw/pin终审及根独立接受待；不得据producer写根接受或将新派生简化负载结果冒称旧raw扫描恢复/真实物理签核，零结果保持。

R24-PAIRED-SPEF-FLAT-V2-STA-20261018根限定接受（LOG186）：ROOT_ACCEPTANCE43ccd357…已根复核194原件SHA-size/16measurement receipt-input-Lib-Tcl-log-rc-read_spef顺序/8annotation原流全0partial全0unannotated及API同WNS，codeclean/HEADf761。准入仅此flatpair/简化负载代理；实际24新STA与v1失败5分开，u10+.11/u40-u1600保留。原raw层级支持/OI051及历史F6/scan未恢复，非route/真实物理签核。EDIT07把该限定证据入正文表18，最终稿QA另门。

新flatSTA终审补齐（LOG187）：PAIRED_SPEF_FLAT_V2_STA_POST_AUDIT.json8d2d23e9…/STA_REPORT0fa67f15…，16raw双流→log/argv600timeout/16receipt输入库Tcl前后与8annotation原流审计齐；最终194件作者重核均符，journal当前/登记cbd5d4ef…末eventcomplete、没有再append，RESULT eebc5398…/root43ccd357…保持。此为只读后审，不新增STA；限定域及旧失败5/新24分离不变。

新flatSTA外部报告收尾更正（LOG191）：仅STA_REPORT由0fa67f15…更新47ab290c91bf5243386329093714ba9e3ed254d45675bdcf2fc965f5e682e76f/3396B，最终运行45.575s取RESULT而非末complete事件45.228；wrapper52s单列。194冻结成员与POST_AUDIT8d2d23e9…未变/无append，不新增EDA或改变根43ccd357限定准入。

C′预算曲线根接受/入稿（LOG195）：ROOT_CURVE_ACCEPTANCE06e90680…根重核33manifest成员/72曲线/192commit/40共同预算比较并实际view，晋级34files包括最终manifest；EDIT08入稿新图6，有限预算随机胜W1反例保留。不新增EDA，不用端点同值宣称全预算支配，不扩大历史族身份；最新源a290待build04与整体视觉。

r24最终表号/响应澄清（LOG197）：最终PDF中tab:paired_load为表16、PR表17、S表18。此前“新增表18”是当时18总表数，不作当前固定表号。新24STA仅flatpair代理模型根准入，四partial REV01/02/05/21持续open，正式D28/56/raw3/8与HEAD/source锁不因作者修订关闭。

r24本轮交付确认（LOG199）：FINAL_PACKAGE08de2647…、ROOT_VISUAL4ce8760d…已实读，最终中文a290/PDFce085898/15-9-18-14，3PDF同步全部完成。此为稿件包/视觉交付，不是新科学实验或关闭D/历史/四态/原raw支持门；四partial与OI051继续，原5失败/新24STA/阶段2flatten2SEC分别计数。

本轮稿件最终身份更新（LOG204；不是新科学实验）：EDIT09只补证明段小节归属，最终build05源a2349e07…/3PDF142ddba6…，FINAL_PACKAGE9e0eba7f…/ROOT_VISUALebab6c2e…/final_verification_build05 af6a05fb…已根验并记录员实读；旧build04包在interim_build04_delivery保历史。新flat数据/24STA与原5失败范围不变，四partial/D/历史/原raw OI051未决不闭。

r25写作修订边界（LOG206）：当前为中文压缩/主线重构任务，无新EDA/实验启动；既有科学实验配置/结果/计数与四partial保持。详细证据拟移补充材料不改变科学族身份或关闭未决，不给文字压缩虚构新实验ID/STA次数。

r25既有接受协议只读再核（LOG210，非新科学实验）：TNS_HARD_GATE_EVIDENCE MDe3033d82/JSON0bdad71a绑定3ea科学runtime ZIP620a0eb9…及W0/s27原trial0/8W1配置，r24公式漏setup_tns前置hard gate；strict_gates/strict_budgets为实际caller硬编码true，不由run_config未序列化推断关闭。无新EDA/STA/源码/TeX修改，数值/实验计数不新增；稿面epsilon0修正及根审待。

r25外循环只读取证（LOG216–217，非新实验）：OUTER_LOOP_STOP_EVIDENCE65da7a92…绑定3ea ZIP/MATRIX72，未提交不立即外停；但refined无反馈/actions空、参数/target不变。index_erratum撤回inner trial.iteration与outer history.iteration混比得到的33对象后续新STA及8/144/56量，不作提前停止因果计数。既有accepted MATRIX72/launchseq及commit-hash曲线不受该索引错误影响，无新增STA/结果。

### 2026-10-18 r25写作压缩/既有证据复核（非新科学实验，LOG218–223）

复用r24/固定3ea原件；FINAL_EVIDENCE_CHECK对修后完整H且Timing、TNS作用域及8最低条件/负面保留有界核查；MAINLINE_FIGURE_CROSSCHECK对24图文项及9旧图PDF身份核查。双稿编译/渲染是文档QA，非STA/SEC新实验。停止规则取证内call与外轮混比的33对象后续STA说法已撤回，不计新科学样本/成本反事实；MATRIX72/sta_launch_seq计数不变。r25本轮新EDA=0，无新增科学实验ID，D accepted28/raw3与旧族、四partial不变。

### 2026-10-18 r26完整稿恢复/示意图生成与有界复核（LOG229–241；无新科学实验）

正文恢复完整方法与各实验族角色，复用旧原件并由FULL_PAPER_EVIDENCE_CHECK重新打开核值。内置image_gen仅作两幅示意图（总览v1拒绝后定向编辑v2；六门例），不生成/改变量化数据图；prompt/provenance/未知模型身份/原像素与科学QA存r26。TeX构建/引用QA不是EDA。r26新STA/SEC/科学实验均0，不新增科学样本或实验ID；S history末项表面差异属本次审计提取错、已按已提交终点纠正，原结果无改。D正式28/raw3及原科学partial不变。

### 2026-10-19 r27配色统一（LOG246–247；无新科学实验）

仅统一中文主/补2示意图与7数据图的配色，复用原图/数据源；19before逐SHA-size已核。图像生成/TeX重编/视觉核对属于图件与文档QA，不新增STA/SEC、科学样本或实验ID。原科学族配置/结果/计数及四partial/D28raw3/OI051保持。

### 2026-10-19 r27纯黑白灰转向（LOG251–252；无新科学实验）

用户“黑白灰配色”取代蓝灰/灰褐；PALETTE 1f9f50d2，旧合同/7图保superseded未入TeX。两内置模型原生黑白灰图已返回（dcfcf9d0/6e6a575a），待结构/标签/实际像素QA；量化图复用已验数据/逻辑重生黑白灰。仅图件与文档QA，无新STA/SEC或科学样本，不改变原配置/结果/计数、四partial、D28/56/raw3/8及OI051。

### 2026-10-19 r27原生AI精确灰度只读检查（LOG253；非科学实验）

RECORDS_AI_PIXEL_READONLY.json只读两原生PNG，实测等通道比例70.525169%/78.446261%、最大通道差11/12，原件未改。拟最终PDF DeviceGray输出后重新检查全文RGB/文本/页数/布局；当前未验。不产生STA/SEC、科学样本、参数或结论变化。

### 2026-10-19 r27最终文档灰度与静态QA（LOG256；非科学实验）

显式LuaLaTeX双遍四pass0/source稳定，随后文档DeviceGray导出main9d0394e8/Sup27ac11ab。10+9页ICC-off RGB差0，图native尺寸/链接数保留；main非空白字形序列同而提取空白及小于0.03pt原点变化明记；静态0overflow/underfull/缺字/undefined/rerun，字体提示保留。根全页实际视觉/副本/包未以静态替代；无STA/SEC或科学样本变化。

### 2026-10-19 r27黑白灰完整工作稿交付（LOG257；无新科学实验）

FINAL_DELIVERY 10701c769c1f5d498e001a2166ef2c5c0b74f220274ce6dfbc27f663feef6bc4实读核符。主10页7图6表8554CJK14refs、补9页5图12表9632CJK，双源1d3b94f4/9886b68a与各3PDF9d0394e8/27ac11ab已实际同字节。根19页contact、main3/4/7/9及Sup7/8整页、7量化图全部面板已实看。记录员再核19before/9旧图/10CSV对、7量化源/PDF和AI原件，数据/科学内容稳定；2CHANGE_LOG与3永久WORKFLOW快照/复现说明齐。本轮图件/构建/DeviceGray/视觉/副本/包已完，无STA/SEC新样本或科学计数变化，四partial/D28/56raw3/8/OI051和源锁保持。

### 2026-10-19 r28图件占幅调整启动（LOG259；非科学实验）

复用r27已验9个唯一图及完整黑白灰论文，19before独立逐SHA-size全符；本轮只调整includegraphics尺寸和必要浮动布局，随后对新双稿重新编译/DeviceGray/全页视觉。未重生成原图，无新STA/SEC、科学样本或实验ID；原科学配置、数据和结论不变，四partial/D28/56raw3/8/OI051与HEADf761锁保持。

### 2026-10-19 r28图件比例工作稿交付（LOG265；无科学新实验）

FINAL_DELIVERY 1a1aa1b24e169fe297023fd3f4493da2779c47d412d898b0c4dc512191ca0e2b实读核符；主10页/补9页，11width与两float选项逆转精确回r27、9图


### 2026-10-24 PHYS-NOISE-FLOOR-20261024（post-route 实现敏感度噪声底族）

`experiments/20261024_physical_transfer_noise/`：同网表多物理实现配对（core_space / 引脚层 / 目标利用率），netlist 变化在实现内配对以抵消实现系统偏差；R0 为归档参考实现。作业：jobs.tsv 64（8 电路×{baseline,fixed}×R0–R3）、jobs_patch2.tsv 33（R1 修正 + R4 密度臂 + s953_R3）、jobs_itc99.tsv 42、jobs_r4.tsv 16、jobs_r4lo.tsv 16（独立 key `_R4lo`，避免与 patch2 的 `_R4` 同 key 覆盖）。流程 pr_var.tcl（`-utilization` 变版图），OpenROAD v2.0-17598-ga008522d8。

权威统计源：`tools/noise_model.py` → `noise_model.json`。**噪声底 = 组内**跨实现散布 σ_w = **0.028541 ns**（95% CI 0.020818–0.036623，自举 2000 次，12 电路 / 48 配对）；**组间 0.11997 ns 是各电路真实效应量之差（信号，非噪声）**，以 `sigma_between_is_signal=true` 显式标注。每电路阈值用 James–Stein 收缩 σ_c²=((n_c−1)s_c²+σ_w²)/n_c（每电路仅 3–6 实现，样本 1σ 相对误差 40–70%）。**12 电路 R0 逐项复现 20260807/20260821 归档 post-route 数值**（自校验全过）；**s420 / s953 的 Δ 跨实现变号**。

已知失败：`s27_{baseline,fixed}_R4` rc=1（PDN-0185 Insufficient width，util+10 使 die 变小、电源条放不下）；`final__s713` rc=1（主族 s713 常量无真实驱动，DRT-0305，已由 tie 单元修复版 S713R 覆盖）。边界：测的是**实现敏感度**非重复性（流程确定性，重跑恒等），**上界**复现不确定性；寄生来自 `estimate_parasitics -global_routing`，**非签核 RC 提取**。本族产物在 git-ignored 的 `experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-LABELS-20261024（候选级 post-route 物理标签数据集族）

`experiments/20261024_physical_labels/`：把论文主结果族（`experiments/20260826_iscas89_main`，fig4 family B）的**全部 330 个唯一候选网表 + 8 基线 + 8 多轮提交网表**送进 OpenROAD 布线后端，得到候选级 post-route 标签。作业：jobs.tsv 338（F0）、jobs_final.tsv 8、jobs_f1.tsv 56（第二实现交叉校验）、jobs_s713_repaired.tsv 30（tie 单元修复版）、jobs_archfrozen.tsv 16（归档 20260807 网表对在**冻结版图**下的复算）。

关键设计：**冻结版图**（`initialize_floorplan -die_area + -core_area` 双钉）——`-utilization` 会按网表单元面积反推芯片尺寸，门尺寸 ECO 顺手把芯片改大（s27 实测 11×69 → 11×71 sites），该混淆量级 0.01 ns 恰压在报告分辨率上。

产物：`physical_dataset.jsonl` / `.tsv`（schema 含**边际**与**累积**两列）、`dataset_v1_summary.json`、`ideal_vs_post.json`、`counterfactual_acceptance.jsonl` + `_summary.json`、`archfrozen_compare.json`、`surrogate_prototype.json`、`surrogate_within_vs_pooled.json`、`RESULTS.md`（9 节，全部从产物回读）。工具：`build_dataset.py`（噪声源改用 `noise_model.json`）、`ideal_vs_post.py`、`counterfactual_acceptance.py`（三档判定 GAIN/REGRESSION/INCONCLUSIVE）、`archfrozen_compare.py`、`surrogate_{prototype,diagnose,within_vs_pooled}.py`、`make_report.py`、`gen_archfrozen_jobs.py`。

**已确认口径**：台账 `acceptance_evidence.metric_references.setup_wns` 是**本轮基线**（s27 逐轮递推自证），故 `ideal_delta_wns` 为**边际**量，与 post-route 边际增益同口径可比。主族 357 条 trial 的 `physical_*` 字段全为 None（无既有物理标签可交叉校验）。边界：批次仍在跑，候选级与代理模型结论为**部分数据探针**；代理模型原型在轮内给出反例——FAECO `proxy_score` 轮内与 post-route 增益 |ρ|≤0.1，按其选候选的轮内遗憾 0.1087 ns vs 理想线网 argmax 0.0060 ns、实际接受 0.0045 ns。产物未提交、`code/` 未动、HEAD 仍 f761ee1。字节同、CJK8554/9632同。当前main03/Sup01显式双遍/DeviceGray19页/静态/实际量化字号主6.39716bp补6.11806bp/根全页视觉/各3PDF均实过，19before逐SHA-size同。main01/02版面失败原件保，Sup视觉记录复制错已纠正，不是科学数据问题。无新STA/SEC、科学样本、图像模型调用或实验ID；四partial/D28/56raw3/8/OI051及HEAD锁保持。

### 2026-10-24 PHYS-LABELS-ITC99-20261024（ITC-99 候选级 post-route 物理标签族）

`experiments/20261024_physical_labels_itc99/`：把 ITC-99 主族（`experiments/20260826_itc99_main`）的**候选网表**送进同一套 OpenROAD 后端，取得 ITC-99 侧的候选级 post-route 标签。作业表：`jobs_itc99.tsv` **1207**（7 基线 + 1193 个不同候选 + 7 个多轮提交网表）、`jobs_itc99_p0.tsv` **58**（基线 + **全部 44 个已接受候选** + 提交网表）。覆盖电路 7 个：`b01 b02 b03 b08 b09 b10 b13`。

可行性依据：① ITC-99 主族的 `eval_trials.json` **内联每个候选的网表文本**，取得物理标签**无需重跑综合**；② 噪声底族已把这 7 个电路在 OpenROAD 里跑通（`jobs_itc99.tsv`，**42/42 全成、零失败**）；③ 噪声底族所跑的网表与 ITC-99 主族 `mapped.v` **逐字节相同**（SHA-256 已核，`itc99_manifest.json/netlist_identity_check`），故基线版图几何可安全跨族迁移。其余 ITC-99 电路（b04/b05/b06/b07/b11/b12/b14/b15/b17/b20/b21/b22）**本族不覆盖**，不外推。

关键设计沿用 ISCAS89 族：**冻结版图**（`-die_area` + `-core_area` 双钉），几何取自噪声底族各电路的基线日志 `runs/<ckt>_baseline_R0/pr_run.log`（取**最后一块**版图初始化块，OpenROAD 在 tapcell/global placement 后会重初始化）。流程序列与 ISCAS89 族完全一致（`pr_label.tcl` 副本 + `run_labels.sh`，断点续跑规则相同）。

成本（据噪声底族**高负载**下的实测均值）：全量约 **37 CPU·h**（b01 43 s/次、b02 18 s、b03 193 s、b08 248 s、b09 152 s、b10 176 s、b13 154 s），仅供排产参考。

边界：本族为**只读探针 + 独立实验族**，不改 `code/`、不改论文、不插入任何论文图；寄生来自 `estimate_parasitics -global_routing`，**非签核 RC 提取**；未跑完的批次**不得**当作"该电路无物理标签"；本族与 ISCAS89 族结论**分族记录**，不跨族替代。产物在 git-ignored 的 `experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-FAMILY-SPLIT-20261024（噪声底按族分带 + 候选级带在本族直接测量 + 接受门槛 vs 物理分辨率）

**动机**：r30 早期把噪声底族的 15 个电路（8 个 ISCAS89 + 7 个 ITC-99）**池化**成一条 σ_w（0.028862 ns）供两族共用，而噪声底族的实现轴是"多实现 × 全 ECO 轮次"，候选级判定要的是"同一张网表、两个物理实现"的量，两者不是一回事。三个具体问题：

1. **跨族池化带不成立**。分族后 ISCAS89 本族 σ_w = **0.023536 ns**（8 电路 / 46 配对，CI 0.018886–0.028074），ITC-99 本族 = **0.039881 ns**（7 电路 / 21 配对，CI 0.025166–0.051177），**相差 1.70 倍**（1.38 是各族对**跨族池化值**的比值，不是两族之比）。池化值对 ITC-99 **偏窄 28%**（会把噪声带内的边际增益误判成"已确认"），对 ISCAS89 **偏宽 18%**。修正：`experiments/20261024_physical_transfer_noise/tools/noise_model.py` 增加 `per_family` 拆分，且每电路的 James–Stein 收缩目标改为**族目标**（同时保留 `sigma_shrunk_pooled_all` 供对照）；两个族的判定阈值、候选级带的比值、校准的 2σ 一律改用**本族** σ_w。（**数值更新**：s953 的 R3 观测在同日的 PHYS-NOISE-GAP-CLOSURE-20261024 中恢复，ISCAS89 本族 σ_w 随之变为 **0.023322 ns**（8 电路 / **47** 配对，CI 0.018886–0.027302），跨族池化值变为 0.028642 ns；两族之比变为 **1.71 倍**。）
2. **ITC-99 族缺自己的候选级带**。原设计让 ITC-99 继承 ISCAS89 的候选级带，但按第 1 点这不成立。新增 `experiments/20261024_physical_labels_itc99/gen_itc99_f1_jobs.py`，生成 **第二物理实现 F1** 的作业表（`jobs_itc99_f1_p0.tsv` 58、`jobs_itc99_f1.tsv` 1207）：与 F0 **完全相同**的网表/版图/布线层集合，只把引脚层 met3/met2 → met5/met4；键与 F0 表一一对应，便于跨实现配对。批 `I1P0` 已投放。族内接线：`build_dataset_itc99.py` 增加候选级带列、`run_analysis_itc99.py` 增加 `candidate_level_noise` / `cross_impl_check` / `resolution_analysis`、新增 `run_analysis_itc99.sh`（**必须建两遍数据集**：候选级带要看到两个实现的行才算得出来）。
3. **"判据错了"与"测不出来"必须分开**。新增 `experiments/20261024_physical_labels/tools/resolution_analysis.py`（产出 `resolution_analysis.json`）：FAECO 接受任意理想的严格改善（0.01 ns 分辨率），而物理测量的 2σ 分辨率是 0.047–0.057 ns。实测 22 条有标签的接受决策里 **15 条（68%）的理想增益低于物理分辨率**（中位数仅 0.020 ns），唯一被判物理退化的那条（s832 第 3 轮）理想增益恰为 0.01 ns、物理余量仅 0.0056 ns，在更宽的候选级带下判为 INCONCLUSIVE。

**顺带修掉的两个真缺陷**：① `tools/violation_census.py` 的实现与其文档意图不符（取全文最后一条 DRT-0199，而非"完成布线之前最后一条"），把**被超时杀掉**的跑次误报成"完成但有违例"；改为按文档意图实现，并把"未完成布线"与"完成且违例"分开统计（现状：395/396 完成布线的跑次**全部 0 违例**，1 个未完成 = F1/s953 超时）。② `tools/candidate_level_noise.py` / `tools/calibration.py` / `tools/cross_impl_check.py` 的 σ_w 引用改为**族内**值；`make_report.py`、`scratch/sync_status_docs.py`、`scratch/gen_r30_handoff.py`、`scratch/append_log_11.py` 里所有硬编码结论（"REGRESSION 均为 0"、"残余几乎全是噪声"、"斜率≈0.91"、"池化带偏保守"）改为**由数据生成**——分族后 REGRESSION 由 0 变 1、残差 sd 是 σ_w 的 1.36 倍，原文案会与数字自相矛盾。

边界：分族只改**阈值口径**，不改任何 EDA 输入与既有产物；全量 1207×2 的 ITC-99 批次（供拒绝侧分析）**尚未投放**；产物在 git-ignored 的 `experiments/2026*/` 下，未提交；不改论文与 `code/`。

### 2026-10-24 PHYS-NOISE-GAP-CLOSURE-20261024（噪声族实现溯源 + 配对自洽审计 + s27 密度上轴物理不可行）

**动机**：r30 收尾批次时，对噪声底族做"入样是否干净"的复查暴露出两个**数据集构造层面的缺陷**
（不是统计口径问题），以及两个真实的物理/工程缺口。本条目记录复查方法、证据与处置。

**发现 1（键覆盖：存储的测量不带实现溯源，真缺陷）**。噪声族的**所有作业表共用同一个
`runs/<key>` 目录**。审计发现 **33 个键被多于一张表声明**，其中 **16 个的参数不同**：
R1 在 `jobs.tsv` 是引脚层 met2/met3（横竖反置：sky130 里 met2 垂直、met3 水平），
在 `jobs_patch.tsv`/`jobs_patch2.tsv` 是 met5/met4（合法）；R4 在 `jobs_patch.tsv`/`jobs_r4.tsv`
是 util 25（s27 为 5），在 `jobs_patch2.tsv` 是 util 40（s27 为 20）。**后跑的表静默覆盖先跑的表**，
于是 `runs/<key>` 里的测量到底来自哪套实现，没有任何痕迹可查。
**归属判定（两条独立证据一致）**：① 批次成员关系来自 `log/master_<batch>.log` 的逐作业行
（`==== <key> rc=... <n>s`），键在多批出现时取**最后**那批；② 各表执行窗口由其**独占键**的日志
mtime 推得。两条证据给出一致结论：`master_patch.log`（33 行）即 `jobs_patch2.tsv` 批
（10:39–11:32），它覆盖了全部 16 个 R1 键（→ met5/met4）与 16 个 R4 键（→ util 40）。
**处置**：① `run_all.sh` 的每个作业在 `rc.tsv` 旁写 `impl.tsv`
（key/netlist/top/util/realisation/core_space/pin_hor/pin_ver/sig_layers/clk_layers/batch）；
② 新增 `tools/attribute_noise_runs.py`（归属 + 回填），回填 **138 个** `impl.tsv`，
产出 `run_attribution.json`（含"归属表与首个声明表参数不同"的完整清单，32 条）。

**发现 2（配对自洽必须审计而不是假定）**。配对差 δ(c,j) = fixed(c,j) − baseline(c,j) 只有在
baseline 与 fixed **共享同一套实现**时才抵消该实现的系统偏移。噪声族共用 `runs/` 使这条前提
不再自动成立。`noise_model.py` 新增 `pairing_audit`：**67 对中非零 rc 0、实现不匹配 0、
缺 impl 记录 0** —— 配对自洽经实查成立，不是假定。

**发现 3（s27 的密度上轴物理不可行 —— 负结果也是数据集结论）**。s27 的 R4（密度上臂）两次实测
均失败，且失败原因是物理约束而非流程错误：`PDN-0185 Insufficient width`。
实测数据：util 20 → 核宽 **22.54 um**；util 40 → 核宽 **15.64 um**；而 met4 主条带需要
`offset 13.57 + strap width 15.17 = 28.74 um` 的核宽。可行的 util 5 与 s27 的 **R4lo 完全同参**
（util 5 / cs 2 / met3 / met2），util 10 与 **R0 完全同参**（util 10 / cs 2 / met3 / met2）——
任何"能跑通"的取值都会造出与已有观测**重复**的样本，并把一个 0 方差观测塞进 σ_w 而压低噪声底。
**处置**：s27 R4 记为"尝试过且物理不可行"，**不补**；s27 的密度轴只有下臂（R4lo，util 5）。

**发现 4（利用率的语义，与常识相反）**。`util` 越高 → 核**越小**（util 20 → 22.54 um，
util 40 → 15.64 um）。第一版补洞把 s27 R4 的 util 从 20 改成 40，方向恰好搞反，PDN 依旧失败；
两次实测的日志与核宽数字都保留在 `runs/s27_{baseline,fixed}_R4/pr_run.log` 与本条目里，
作为"负结果带证据"的样本。

**发现 5（s953 超时是负载 × 时限的叠加，不是流程缺陷）**。s953 是 ISCAS89 族最重电路
（openroad RSS 660–917 MB），在 1800 s 限下被杀了 3 次：噪声族 `s953_baseline_R3`（rc=124, 1683 s）、
F1 `s953__t009`（rc=124）、F0 `s953__t002`（rc=124, 1786 s）；F0 的 `s953__t011` 同样 rc=124。
**处置**：`TIMEOUT=3000` + `PAR=1` 重跑即通过（实测 F1 `s953__t009` 1088 s、
F0 `s953__t014` 1635 s / `s953__t016` 1492 s）。`s953_fixed_R3` 早已成功（rc=0, 205 s，TNS 完整），
故只需补 baseline 一侧。噪声底作为"实现敏感度**上界**"的定位不受影响，但 s953 的样本量由
5 恢复到 6。

**批次实况（本条目写入时，定稿数字以产物回读为准）**：ISCAS89 F0 336/338（2 个 s953 重跑中）、
F1 **56/56 全成**（rc 分布 0:48 / 1:7，7 个 rc=1 是已知 tie 单元问题，由 S713R 批覆盖）、
S713R 30/30、F1S713 7/7、final 8/8、ARCHF 16/16；ITC-99 I0P0 **58/58 全成**、I1P0 **58/58 全成**；
噪声族 main 64/64、itc99 42/42、r4lo 16/16、patch2 33/33、patch3 3/3（2 个 s27 R4 rc=1 失败已归档）。

**边界**：本条目只改噪声族的**溯源记录与观测补全**，不改任何 EDA 输入、阈值口径或既有科学结论；
σ_w 的数值变化（s953 由 n=5 到 n=6）需在定稿时回读 `noise_model.json` 后再引用；
产物在 git-ignored 的 `experiments/2026*/` 下，未提交，`code/` 未动，HEAD 仍 f761ee1。

### 2026-10-24 PHYS-THREE-POINT-20261024（补上"布局后"这一档：理想线网 → 布局后 → 布线后）

**动机**：r30 之前只有两个点——论文自己的**理想线网**（预布局、无寄生）与本族的 **post-route**。
两者之间缺一档：**布局+CTS 之后、布线之前**。缺了它，任何"理想增益在物理世界里衰减了多少"的
说法都只能把**全部**衰减归给布线，而布局本身已经移动了单元、已经改变了连线长度。
用户对论文的明确要求正是"理想线网提升 vs 布局后提升 vs 详细布线后提升"。

**新增**：`experiments/20261024_physical_labels/pr_placed.tcl`（布局后档 flow）、
批次 `PLACED`（338 作业，F0 实现）与 `PLACEDF1`（56 作业，F1 实现）、
工具 `experiments/20261024_physical_labels/tools/three_point_curve.py`（产出 `three_point_curve.json`）、
报告新增 6.6 节。`run_labels.sh` 增加 `TCL=` 环境变量（默认仍是 `pr_label.tcl`，不影响既有批次）。

**flow 定义**：`pr_placed.tcl` = `pr_label.tcl` 去掉布线段，其余**逐字相同**（同一冻结版图、同一
引脚层、同一 PDN、同一 tapcell、同一 global/detailed placement、同一 CTS、同一第二次
detailed placement），然后用 `estimate_parasitics -placement` 估寄生并报 STA；日志输出格式与
`pr_label.tcl` 完全一致（TNS_BEGIN / report_tns / report_worst_slack -max / -min），
因此既有解析器与既有分析链可直接复用。已实查两档的 CTS 段**逐行相同**（同行号同内容），
说明布局+CTS 阶段在两档之间一致，差异只来自布线段。

**踩到的真陷阱（测量口径缺陷，已修）**：`estimate_parasitics -placement` 在**没有设置线 RC** 时
**完全惰性**——实测布局后档的 setup slack 与理想线网值**逐字相同**（83/83 个候选完全一致，
例：-0.19 / -0.20 / -0.18 / -0.26），因为 OpenSTA 没有任何连线延迟可加；OpenROAD 其实已经警告
`[WARNING RSZ-0018] wire capacitance for corner default is zero. Use the set_wire_rc command...`。
**布线后档不受此影响**（`estimate_parasitics -global_routing` 的 RC 取自平台 LEF 的层属性）。
修法：在 placement 估计前 `set_wire_rc -layer met2 -signal` / `-layer met4 -clock`（值取自平台
LEF，不自造数字），布局后档随即出现真实连线延迟。
**若不修，这一档会退化成"理想线网的重复测量"，并给出 ρ=1.0 的假完美相关**——本轮第一版正是如此，
已作废并重跑。

**RC 标定（非拍脑袋）**：在 s27 的一个候选上（理想 -0.19、布线后 -0.25）逐层扫
`set_wire_rc -layer met1..met5`，布局后档给出 -0.22 / -0.22 / -0.23 / -0.23 / -0.23 ——
**RC 层选择的影响 ≤0.01 ns，远低于本族物理分辨率带（2σ ≈ 0.047 ns）**，
故该建模选择不是实质不确定性。最终用 signal=met2 / clock=met4（sky130hd 的主信号/主时钟层），
标定记录在 `scratch/probe_rc_sweep.sh` 与 `scratch/probe_placed_parasitics.tcl`。

**必须随每个数字一起走的警告**：布局后档与布线后档的**寄生估计模型不同**
（布局后 = Steiner 估计线长 × 单一代表层 R/C；布线后 = 实际布线拓扑 × 每层 R/C），
因此"布线后 − 布局后"**混合了物理阶段变化与估计模型变化**，**不是纯布线惩罚**，
报告 6.6 节已把它写死。

**边界**：本档只覆盖 ISCAS89 族（F0 的 338 个作业 + F1 的 56 个作业）；ITC-99 族未做布局后档；
寄生来自 `estimate_parasitics -placement`（Steiner 线长估计），**不是**签核 RC 提取；
`code/` 未动，HEAD 仍 f761ee1，产物在 git-ignored 的 `experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-NETLIST-CONSISTENCY-20261024（跨阶段网表一致性守卫：发现并修复"布局后档用错网表"）

**缺陷（真实存在，且完全静默）**：三点曲线把"布局后"档与"布线后"标签放在一起比，但两者
**跑的不是同一个网表**。s713 的主族网表常量没有真实驱动（`assign x = 1'h1`），
`detailed_route` 报 DRT-0305，所以 s713 的**布线后标签**只能来自 tie 单元**修复批** S713R
（逻辑等价修复，`netlists_repaired_manifest.json` 记录 pre/post sha256 与修复的常量个数）；
而**布局后档**是由主作业表 `jobs.tsv` 启动的，测的是**未修复网表**。
缺陷之所以静默：① 修复是逻辑等价的，不改功能；② 布局后阶段**不布线**，
DRT-0305 根本不触发，未修复网表在布局后档"跑得好好的"。
实查后果：s713 上 `mean(routed − placed)` 混入了一个 −0.12 ns 量级的**网表级**偏移，
而它本该只反映"物理阶段 + 寄生估计模型"的差异。

**守卫（新工具）**：`experiments/20261024_physical_labels/tools/check_netlist_consistency.py`
（产出 `netlist_consistency.json`）。它**不硬编码**"电路 → 作业表"的映射，而是逐候选比对
"标签批作业表"与"全部布局后作业表"的**网表路径与 sha256**，**自动推导**每个电路该用哪张表；
并按**去重后的候选数**报告受影响范围（同一候选可能与多张表不符，按表相加会重复计数）。
实测：**29 个已标注候选不一致，全部集中在 s713**；其余 7 个电路 **0 处**；
路径相同处 sha256 也 **0 处**不一致。

**修复**：补跑修复网表的布局后档 —— `PLACEDS713`（`jobs_s713_repaired.tsv` + `pr_placed.tcl`，
30 作业，rc=0）与 `PLACEDF1S713`（`jobs_f1_s713.tsv` + `pr_placed.tcl`，7 作业，rc=0）。
`three_point_curve.py` 改为**从守卫产物读取**每个电路该用哪批布局后运行，
守卫报出无法解析的电路时**拒绝出数**；守卫已接进 `run_analysis.sh`（三点曲线之前）。

**影响量化（缺陷真实存在，但数值影响小 —— 两件事分开报）**：
`tools/compare_placed_repair_effect.py`（产出 `placed_repair_effect.json`）逐键对比修复前后的
布局后绝对 WNS：**23/30 个键发生偏移**，最大 **0.05 ns**、均值 **0.016897 ns**；
`mean(routed − placed)` 由 **−0.12069** 变 **−0.134333** ns。
偏移主要是电路级公共量，在**边际**量（候选对它派生自的那张网表）里抵消，
因此三点曲线的总体相关性几乎不变（ρ(理想, 布局后) = 0.7889、ρ(理想, 布线后) = 0.6876、
ρ(布局后, 布线后) = 0.8224），但**布局后候选级 2σ 带**由 0.042876 变 **0.04836** ns
—— 判定阈值确实变了。

**顺带修掉的第二个缺陷**：`tools/rc_census.py` 原来把"命令行指定的族"写进 `rc_census.json`，
于是随手跑一次 `rc_census.py labels` 就会把噪声族与 ITC-99 族的记录从普查文件里**抹掉**，
日志脚本再读同一文件就读到空的噪声族计数（渲染出"共 0/0 作业跑完"）。
现改为**永远写入全部族**，命令行参数只控制打印范围。

**边界**：本条只覆盖 ISCAS89 族；ITC-99 族尚未做布局后档；`code/` 未动，HEAD 仍 f761ee1，
产物在 git-ignored 的 `experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-ITC99-THREE-POINT-20261024（把三点物理曲线扩到 ITC-99 族）

**动机**：ISCAS89 族的三点曲线（理想 → 布局后 → 布线后）已在
PHYS-THREE-POINT-20261024 与 PHYS-NETLIST-CONSISTENCY-20261024 中完成，但 ITC-99 族
（7 个电路、候选数是 ISCAS89 的数倍）此前只有布线后一档。三点曲线要能覆盖更大的族，
否则"理想线网的虚假繁荣"这个结论只在小电路上成立。

**flow 定义**：`experiments/20261024_physical_labels_itc99/pr_placed.tcl` = 本族
`pr_label.tcl` **去掉布线段**，其余**逐字相同**（同一冻结版图、同一引脚层、同一 PDN、
同一 tapcell、同一 global/detailed placement、同一 CTS、同一第二次 detailed placement），
然后 `set_wire_rc -layer met2 -signal` / `-layer met4 -clock`（取自平台 LEF）+
`estimate_parasitics -placement`。输出格式与 `pr_label.tcl` 完全一致，既有解析器与既有分析链可直接复用。
`run_labels.sh` 增加 `TCL=` 环境变量（默认仍是 `pr_label.tcl`，不影响既有批次）。

**退化检查（必做）**：冒烟跑一个候选 `b01__t010__9ebef79c` → 理想 **-0.62** /
布局后 **-0.66** / 布线后 **-0.71** ns。**三档互不相同**，说明该档带了新的物理量。
若不设 `set_wire_rc`，布局后档会退化成"理想线网的重复测量"并给出 ρ=1.0 的假完美相关
（ISCAS89 族第一版正是如此，已作废重跑）。

**投放前的网表一致性核对**（ISCAS89 族踩过的坑）：本族 F0 与 F1 作业表的 1207 个键
**网表路径与 sha256 全部一致**、实现标签（F0/F1）**全部不同**
（`scratch/probe_itc99_f0f1_netlist.py`）。因此布局后 F0 侧（IPLACED）与 F1 侧（IPLACEDF1）
测的是同一批网表，候选级带测到的才是实现敏感度而不是网表变更。

**成本实测**：布局后档**很便宜**——b10 候选 **2 s**（布线档 515 s），因为布线的时间几乎全在
TritonRoute 的固定启动开销上。所以本族布局后档与布线档可以并行投，两者不争同样的瓶颈。

**新增工具与报告**：`experiments/20261024_physical_labels_itc99/tools/three_point_curve_itc99.py`
（产出 `three_point_curve.json`）与本族 `RESULTS.md` 的 **6.6 节**；
`run_analysis_itc99.sh` 增加该步骤；`tools/rc_census.py` 认识 IPLACED / IPLACEDF1 两个批次。
该工具内含**网表一致性守卫**：F0/F1 两侧网表不一致时**拒绝出数**。

**顺带查明的测量粒度**：OpenSTA 的 `report_worst_slack` 只打**两位小数**，所以候选级边际量
被量化到 **0.01 ns**；"差值恰好为 0"应读作"低于报告粒度"，不是"没有影响"。
本族候选级 2σ ≈ 0.0875 ns ≈ 9 个量子、ISCAS89 族 ≈ 0.055 ns ≈ 5 个量子，
**带比量子宽一个量级**，故量化不决定三档判定（已记入 `docs/EXPERIENCE.md`）。

**边界**：本档覆盖 ITC-99 族；寄生来自 `estimate_parasitics -placement`（Steiner 线长估计），
**不是**签核 RC 提取；`code/` 未动，HEAD 仍 f761ee1，产物在 git-ignored 的
`experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-TRAINING-TABLE-20261024（把数据集变成"能直接拿来训练"的表 + 数据卡）

**动机**：用户要的"数据集"此前只以**按批次组织**的原始产物存在
（`physical_dataset.jsonl` 布线后标签、`three_point_curve.json` 布局后标签、
噪声底在另一个族目录），学习者要自己按候选键把它们 join 起来、还要自己分清
"边际/累积"两种读法和"两条带"。数据存在 ≠ 数据可用，所以补上两层。

**① 统一训练表**：`tools/build_training_table.py`（`--family iscas89|itc99`），
产出 `training_table.jsonl` / `training_table.csv` / `training_table_summary.json`。
**每个已标注候选一行**，同时带：
ECO 侧特征与账本（circuit / iteration / kind / instance / from_type / to_type /
accepted_ideal / realisation / label_batch / netlist_sha256）、
**三个物理阶段的边际量与累积量**（ideal / placed / routed × marginal / cumulative）、
**两条带**（噪声底族带、候选级带）与其三档判定、以及 QA 列（OpenROAD 版本、批次、
运行状态、返回码、耗时、系统偏移）。

**② 数据卡**：`tools/make_dataset_card.py` 产出 `DATASET_CARD.md`（数字全部从产物回读），
说明：一行是什么、每个列何时为 null、两种读法为什么不可混用、两条带各自怎么来的、
**三档判定必须按"理想线网是否接受"拆开读**、跨阶段怎么退化、以及不得外推的边界与溯源链。

**修掉的一个口径错误（第一版训练表）**：三档判定最初按**全部候选**统计，得到
REGRESSION 77（噪声底族带）/ 63（候选级带），看着像是"三分之一的候选物理上退化"。
实际上多数候选本来就被理想线网**拒绝**，对它们说"退化"只是废话。
按 `accepted_ideal` 拆开后：
- **被接受的候选**（这才是"接受是否正确"）：GAIN 8 / REGRESSION 1 / INCONCLUSIVE 17
  （噪声底族带）、7 / 1 / 18（候选级带）、11 / 0 / 15（布局后候选级带）——
  与反事实接受分析的计数**口径一致**（后者统计的是接受决策，不是候选）；
- **被拒绝的候选**（这才是"拒绝是否正确"）：REGRESSION 76 / 62（拒对了）、
  GAIN 9（**漏掉的真实改善**）、INCONCLUSIVE 214 / 228。
两个总体**不可**混为一谈。

**接进分析链**：`run_analysis.sh` 与 `run_analysis_itc99.sh` 各加两步
（build_training_table + make_dataset_card），所以数据卡与训练表**不可能**与数据脱节。

**边界**：训练表仍是**只读探针级**资产：寄生不是签核 RC 提取、边际量被量化到 0.01 ns、
布局后与布线后档的寄生估计模型不同、s713 的标签来自修复网表。
`code/` 未动，HEAD 仍 f761ee1，未提交。

### 2026-10-24 PHYS-CROSS-STAGE-SURROGATE-20261024（跨阶段代理模型：便宜的布局后标签能不能替掉昂贵的布线后标签）

**动机**：破局思路里有一条是"用学习模型替代 F1-F6 反馈，预测候选在物理布线后的收益"。
要问的第一个可测问题是**监督信号从哪来**：本族第一次能同时提供三个阶段的候选级标签——
理想（免费）/ 布局后（ITC-99 实测 ~2 s/候选）/ 布线后（ITC-99 实测 ~515 s/候选）。
若布局后标签能替掉布线后标签，训练集的制造成本就降两个数量级；这直接决定这个数据集怎么造。

**工具**：`experiments/20261024_physical_labels/tools/surrogate_cross_stage.py`（`--family iscas89|itc99`），产出 `surrogate_cross_stage.json` / `.txt`。

**协议**：留一电路交叉验证 + ridge（λ 在训练电路内 LOO 选）；**每个格子用同一批行、同一批折**，格子之间才可比。
特征白名单：FAECO 自己的 7 个 proxy 特征 + proxy_score + proxy_rank + kind one-hot + iteration（`proxy_plus_ideal` 再加 ideal_gain）。
**显式排除**：accepted 标记、同一行的 placed/routed 标签、账本的 physical_* 字段——都泄漏答案。

**① 拼接审计**：325/325 行与账本 trial 一一对应（覆盖 1.0000），kind/iteration/instance **零不一致**（mismatch=none）。电路 8 个、候选池 26 个。

**② 转移矩阵**（OOF Spearman；列 = 被预测的标签）：

| 特征集 / 训练标签 | 预测理想 | 预测布局后 | 预测布线后 |
|---|---|---|---|
| 只用 proxy 特征 / 训练标签=理想 | 0.0756 | -0.0014 | -0.0273 |
| 只用 proxy 特征 / 训练标签=布局后 | 0.1049 | 0.0310 | 0.0032 |
| 只用 proxy 特征 / 训练标签=布线后 | 0.0915 | 0.0237 | -0.0022 |
| proxy+理想增益 / 训练标签=理想 | 0.9697 | 0.7447 | 0.6321 |
| proxy+理想增益 / 训练标签=布局后 | 0.9028 | 0.7394 | 0.6477 |
| proxy+理想增益 / 训练标签=布线后 | 0.8689 | 0.7360 | 0.6515 |

**③ 逐电路配对符号检验**（8 个电路时池化差 0.01–0.02 说明不了问题，只能逐电路配对）：

- proxy_plus_ideal|ideal vs proxy_plus_ideal|placed：**wins=1 ties=0 losses=7**（8 个电路）
- proxy_plus_ideal|ideal vs proxy_plus_ideal|routed：**wins=2 ties=0 losses=6**（8 个电路）
- proxy_plus_ideal|placed vs proxy_plus_ideal|routed：**wins=4 ties=0 losses=4**（8 个电路）
- proxy_only|routed vs proxy_plus_ideal|routed：**wins=0 ties=1 losses=7**（8 个电路）

**④ 决策遗憾**（布线后标签；左栏全部池，右栏**只有存在被接受候选的池**——只有这样 `accepted` 与各模型才是同一批实验）：

| 选择器 | 全部池 n | 全部池平均遗憾 | 全部池最差 | 同池 n | 同池平均遗憾 | 同池最差 |
|---|---|---|---|---|---|---|
| accepted | 18 | 0.0072 | 0.0500 | 18 | 0.0072 | 0.0500 |
| ideal_argmax | 26 | 0.0142 | 0.0800 | 18 | 0.0072 | 0.0500 |
| random_mean | 26 | 0.0502 | 0.1141 | 18 | 0.0445 | 0.1141 |
| proxy_only / ideal | 26 | 0.0365 | 0.1900 | 18 | 0.0300 | 0.1900 |
| proxy_only / placed | 26 | 0.0342 | 0.2300 | 18 | 0.0278 | 0.2300 |
| proxy_only / routed | 26 | 0.0350 | 0.2300 | 18 | 0.0278 | 0.2300 |
| proxy_plus_ideal / ideal | 26 | 0.0188 | 0.1300 | 18 | 0.0072 | 0.0500 |
| proxy_plus_ideal / placed | 26 | 0.0173 | 0.1300 | 18 | 0.0072 | 0.0500 |
| proxy_plus_ideal / routed | 26 | 0.0188 | 0.1300 | 18 | 0.0094 | 0.0500 |

**⑤ 验证预算**（模型给候选排序，只有前 k 个真的跑布线后 STA，验完取最好的）：

| 模型 | 预算 | 平均遗憾 | 最差遗憾 | 平均调用 | 平均池大小 | 节省 |
|---|---|---|---|---|---|---|
| proxy_only / ideal | 25% | 0.0142 | 0.1000 | 3.423 | 12.192 | 71.92% |
| proxy_only / ideal | 50% | 0.0131 | 0.1000 | 6.346 | 12.192 | 47.95% |
| proxy_plus_ideal / ideal | 25% | 0.0065 | 0.0500 | 3.423 | 12.192 | 71.92% |
| proxy_plus_ideal / ideal | 50% | 0.0031 | 0.0300 | 6.346 | 12.192 | 47.95% |
| proxy_only / placed | 25% | 0.0188 | 0.2300 | 3.423 | 12.192 | 71.92% |
| proxy_only / placed | 50% | 0.0185 | 0.2300 | 6.346 | 12.192 | 47.95% |
| proxy_plus_ideal / placed | 25% | 0.0077 | 0.0800 | 3.423 | 12.192 | 71.92% |
| proxy_plus_ideal / placed | 50% | 0.0027 | 0.0300 | 6.346 | 12.192 | 47.95% |
| proxy_only / routed | 25% | 0.0188 | 0.2300 | 3.423 | 12.192 | 71.92% |
| proxy_only / routed | 50% | 0.0185 | 0.2300 | 6.346 | 12.192 | 47.95% |
| proxy_plus_ideal / routed | 25% | 0.0092 | 0.0800 | 3.423 | 12.192 | 71.92% |
| proxy_plus_ideal / routed | 50% | 0.0042 | 0.0400 | 6.346 | 12.192 | 47.95% |

**⑥ 标签本身是噪声受限的**：布线后边际量恰好为 0.00 的有 32/325 条，超出候选级带（0.055542）的只有 79/325 条（24.3%）；布局后档 63/325 恰好为 0、可分辨 91/325。
所以符号准确率必须分"全部行 / 可分辨行"两栏读；全行那一栏基本被噪声主导。

**边界**：**探针级**，单族（本次 iscas89），特征是 FAECO 自己的 proxy 特征、**不是 GNN**；
边际量量化到 0.01 ns；寄生不是签核 RC 提取；布局后与布线后档的寄生估计模型不同；s713 的标签来自修复网表。
**逐电路覆盖不全**：格子 `proxy_only|ideal` 在电路 s820=-0.168, s832=-0.116 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
**逐电路覆盖不全**：格子 `proxy_only|placed` 在电路 s420=-0.001, s820=-0.203, s832=-0.098 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
**逐电路覆盖不全**：格子 `proxy_only|routed` 在电路 s820=-0.126, s832=-0.063 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
**逐电路覆盖不全**：格子 `proxy_plus_ideal|ideal` 在电路 s832=-0.088 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
**逐电路覆盖不全**：格子 `proxy_plus_ideal|placed` 在电路 s832=-0.072 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
**逐电路覆盖不全**：格子 `proxy_plus_ideal|routed` 在电路 s832=-0.063 上与布线后标签**负相关**——模型在该电路上是反着的，不能报"整体有效"就略过。
`code/` 未动，HEAD 仍 f761ee1，产物在 git-ignored 的 `experiments/2026*/` 下，未提交。

### 2026-10-24 PHYS-BAND-CONVENTION-20261024（"候选级带"的两套聚合口径 + 训练表溯源缺陷修复）

**发现**：同一族里"候选级带"其实有**两个来源**且**给出不同判定**——
- **族池化**：2σ = 0.055542 ns（全部电路的配对网表池化；三点曲线、训练表、数据卡用这个）；
- **逐电路**：数据集每一行里的 `cand_threshold`（该电路自己的配对网表估计；rejected_side、counterfactual_acceptance 等工具用这个）。

两者都"对"，但**同一个问题得到不同答案**，而且没有任何报错：被接受候选在候选级带上，池化口径 GAIN/REG/INC = 7/1/18，逐电路口径 = 11/0/15；被拒候选分别 9/62/228 与 13/90/196；噪声底族带上被接受侧两口径**计数相同**（8/1/17）。
翻转明细：噪声底族带 **22** 条、候选级带 **49** 条（`band_sensitivity.json` 逐条列出）。

**因此"被接受的候选里有 1 个物理退化"这句话是带口径相关的**：
池化候选级带成立（s832__t007__92d63402，−0.06 ns < −0.0555 ns），逐电路候选级带不成立（s832 自己的候选级带 2σ = 0.0847 ns > 0.06 ns）。
逐电路估计每个电路只有 **6 对**配对网表（df=5），池化用 **48 对**（df=40），所以小样本电路的逐电路带**方差大**（s832 是池化值的 1.53 倍、s713 是 1.34 倍）。

**顺带查实并修掉的第二个缺陷（真缺陷）**：统一训练表的去重规则是"每个候选键取第一行"，
而 s713 的候选在 F0 与 S713R（tie 单元修复批）各有一行、**F0 那行没有标签**——
于是 23 个**带标签**的 s713 候选被挂上了**未修复网表的 sha256**、`cand_threshold`/`noise_threshold` 全为 null、`label_batch` 写成 F0。标签本身是对的（标签取自三点曲线，而曲线按"有标签"筛行），错的是同一行的**元数据**：**数值对、溯源错**，数值检查抓不到这种错。
去重规则改为"**优先保留带标签的那一行**"，训练表与 `band_sensitivity.py` 用同一规则，修后两工具的接受侧计数**逐候选一致**。

**产物**：`tools/band_sensitivity.py` → `band_sensitivity.json`；训练表列名显式带口径（`routed_verdict_*_pooled` / `routed_verdict_*_perckt`，阈值列同理）；`DATASET_CARD.md` 第 5、6 节改为"两族 × 两种聚合口径"并列出逐电路阈值表；数据卡与训练表的判定计数一律带齐 GAIN/REGRESSION/INCONCLUSIVE 三个键（Counter 会省掉计数为 0 的键，下游会把"缺键"读成"未知"）。

**边界**：本族两族的"跨族池化带"仍**不用于**任一族判定（两族 σ_w 相差约 1.71 倍）；本条只统一**族内**的聚合口径，不改变任何 EDA 结果；`code/` 未动，HEAD 仍 f761ee1，未提交。

### 2026-10-24 PHYS-THREE-STAGE-CALIBRATION-20261024（"预估偏差拟合曲线"补成三档）

**动机**：用户要求的"理想线网提升 vs 布局后提升 vs 详细布线后提升 + 预估偏差拟合曲线"，此前只有**两档**（理想→布线后）的校准图，看不出**预测是在哪一步丢掉的精度**。

**产物**：`tools/calibration_three_stage.py` → `calibration_three_stage.json`；`tools/make_calibration_three_stage_figure.py` → `preview_calibration_three_stage.png/pdf`（**预览，不入主稿**）。

**结果**（共同子集 n = 325，**边际**口径）：

| 比较 | 斜率 | se | 残差 sd | ρ | 符号一致 | 源侧需增益多少才够目标档 2σ |
|---|---|---|---|---|---|---|
| ideal → placed | 0.891054 | 0.019632 | 0.023436 | 0.787 | 249/325 | 0.044815 ns（目标带 0.04836） |
| ideal → routed | 0.851256 | 0.028375 | 0.033873 | 0.6838 | 213/325 | 0.053472 ns（目标带 0.055542） |
| placed → routed | 0.963501 | 0.021098 | 0.024137 | 0.819 | 257/325 | 0.055419 ns（目标带 0.055542） |

**与三点曲线独立吻合**：三点曲线的衰减斜率 0.8911 / 0.8513 / 0.9635 与 ρ 0.7870 / 0.6838 / 0.8190 在本工具里被**独立重新导出**，逐字一致（两条独立代码路径）。

**读法**：**衰减主要发生在布局阶段**——理想→布局后斜率 0.8911、而布局后→布线后斜率 0.9635（几乎不衰减）；但**理想→布线后的残差 sd（0.0339 ns）比任何一步都大**，说明两段的误差不是简单相加，"整段归给布线"也不对。
另外"源侧要预测多大才够目标档 2σ"：理想→布局后需 0.0448 ns、理想→布线后需 0.0535 ns、布局后→布线后需 0.0554 ns，而 FAECO 的实际接受门槛是**严格 WNS 改善**（0.01 ns 量级）→ **门槛与物理可确认性差约 5 倍**。

**边界**：布局后档用 placement 寄生模型、布线后档用 global-routing 模型，故"布线后 − 布局后"**不是**纯布线惩罚；标签量化到 0.01 ns，斜率因标签噪声而**被低估**，只能作指示性结论；图**只作预览**，不入主稿；`code/` 未动，HEAD 仍 f761ee1，未提交。

### 2026-10-24 PHYS-FAILURE-SIGNAL-DIAGNOSTIC-20261024（"自适应反馈没用"的测量级解释）

**动机**：论文的 F1-F6 失效反馈按上一轮失效类型调候选权重，论文自报"自适应相比固定权重未取得额外收益"。此前只能猜测原因；本族第一次能在**物理标签**上检验这条反馈信号本身。

**工具**：`experiments/20261024_physical_labels/tools/failure_signal_diagnostic.py`（产出 `failure_signal_diagnostic.json`）。

**① 归档里到底记录了什么反馈**：`failure_event_types` = {"acceptance_budget_violation": 201}，即**只有一种**事件类型（`acceptance_budget_violation`）；全账本共 201 次触发。

**② 它带不带物理信号**：带事件的候选 n=197，平均理想增益 -0.0609 ns、平均布线后边际增益 -0.0422 ns；不带事件的 n=128，+0.0090 / +0.0184 ns。整体看有区分度，但这可能只是"理想判据已经拒绝的候选"的重说。

**③ 决定性检验：同一个理想增益带内还分不分**（只有这里能区分"新信息"与"同义反复"）：

| 理想增益带 | 带事件 n | 不带 n | 带事件平均布线后 | 不带平均布线后 | 差 |
|---|---|---|---|---|---|
| [-10.00, -0.02) | 125 | 2 | -0.06304 | -0.025 | +0.0380 |
| [-0.02, +0.00) | 40 | 4 | -0.0045 | -0.01 | -0.0055 |
| [+0.00, +0.02) | 32 | 104 | -0.008125 | 0.010769 | +0.0189 |
| [+0.02, +0.10) | 0 | 14 | n/a | 0.034286 | 不可比 |
| [+0.10, +10.00) | 0 | 4 | n/a | 0.21 | 不可比 |

**④ 结论（机理，不是猜测）**：带事件的候选里**理想增益 ≥ +0.02 ns 的有 0 个**——即该事件**只在理想判据已经拒绝的候选上触发**；在最大的可比带（理想增益 ∈ [0, +0.02)）内，它仍能分开布线后结果，但只分开约 0.019 ns，**远小于候选级 2σ 带**（本族 0.0555 ns）。所以这条反馈信号**几乎等同于理想判据自身的裁决**（一位信息），驱动它去调权重，相对"已经知道理想增益"的机制**几乎没有可加的信息**——这就是论文"自适应无额外收益"的一个**测量级解释**。

**⑤ 同时得到的一个坏消息**：归档账本里 `topology_metrics` 为 null、电气度量（max_fanout / max_capacitance / max_transition / area）为 null、且 **325/325 个候选都在关键路径上**（该判别量零方差）——**现有归档不含任何可用于 GNN 的结构特征**，要验证"用 GNN 识别卡脖子结构"必须**新抽取网表图结构特征**，不能复用现有账本。

**边界**：探针级、单族（ISCAS89）；归档的失效分类法**不是**论文的 F1-F6 分类法本身，故本条诊断的是"实际可得的反馈信号"，不是论文的设计意图；`code/` 未动，HEAD 仍 f761ee1，未提交。

### 2026-10-24 PHYS-STRUCTURAL-SURROGATE-20261024（结构特征能不能替掉理想判据：GNN 路线的前提检验）

**动机**：上一条（PHYS-FAILURE-SIGNAL-DIAGNOSTIC）查明现有归档**不含任何可用于 GNN 的结构特征**（`topology_metrics` 全 null、电气度量全 null、候选 100% 落在关键路径上）。要判断"用 GNN 预测物理布线后的收益"这条路是否可行，第一步不是训模型，而是**先测图里到底有没有物理信号**。

**工具**：`experiments/20261024_physical_labels/tools/extract_graphs.py`（直接解析门级 Verilog 出图与结构特征，不引 PDK/Yosys；ISCAS89 339 行 / ITC-99 1207 行；组合环断边并标记，ITC-99 命中 73 个）+ 改 `tools/surrogate_cross_stage.py`（新增三个结构特征集、电路内平均 ρ、单变量电路内关联表、精确二项 p、`--stages` 子集/`auto`）。产物 `structural_features.jsonl`、`structural_features_summary.json`、`surrogate_cross_stage.{json,txt}`。

**协议**：留一电路交叉验证 + ridge（λ 在训练电路内 LOO 选）；每个格子用**同一批行、同一批折**；拼接审计两族均 100% 且 kind/iteration/instance **零不一致**；特征白名单分三档（`proxy_only` / `proxy_plus_ideal` / `structural` / `structural_plus_ideal` / `structural_cp_plus_ideal`），其中 `cp_*` 来自 ledger 的理想线网关键路径，**单独成集、不算作"结构"证据**；显式排除 accepted 标记、同行 placed/routed 标签与账本 physical_* 字段。

**关键结果（电路内平均 Spearman vs 布线后标签 / 决策遗憾）**：

| 特征集 | ISCAS89 电路内 ρ | ISCAS89 遗憾 | ITC-99 电路内 ρ | ITC-99 遗憾 |
|---|---|---|---|---|
| `proxy_only`（FAECO 现有特征） | 0.1506 | 0.0350 | 0.2861 | 0.0230 |
| `structural`（纯图特征） | **0.0322** | **0.0485** | **0.1172** | **0.0745** |
| `proxy_plus_ideal` | 0.5080 | 0.0188 | 0.5450 | 0.0100 |
| `structural_plus_ideal` | 0.4484 | 0.0169 | 0.5552 | 0.0140 |
| `structural_cp_plus_ideal` | 0.4304 | 0.0177 | 0.4814 | 0.0120 |
| 随机参考 | — | 0.0502 | — | 0.0756 |

逐电路配对符号检验：ISCAS89 `structural` vs `proxy_only` **1 胜 7 负 p = 0.0703**；`structural_plus_ideal` vs `proxy_plus_ideal` **3 胜 5 负 p = 0.7266**；ITC-99 后者 **3 胜 1 平 3 负 p = 1.0**；`structural_cp_plus_ideal` vs `structural_plus_ideal`（ITC-99）**0 胜 1 平 6 负 p = 0.0312**。单变量电路内 ρ 对布线后标签最高仅 0.17，而 `ideal_gain` 为 0.5082 / 0.5909。

**结论**：① **纯图特征预测物理收益 ≈ 随机**（两族、两种拓扑情形一致）；② 加上理想增益后，结构特征与 FAECO 现有 proxy 特征**无差异** → 图里**没有测到**可提取的物理信号，**"用 GNN 替掉 F1-F6 反馈"缺前提**；③ 理想线网的**关键路径位置**信息加进去反而**显著变差**（p = 0.0312），与"理想线网的虚假繁荣"一致。

**边界**：探针级、非论文证据；特征是手工标量图摘要**不是 GNN**，"无信号"只对这些摘要成立；ISCAS89 族候选不改拓扑（`d_*` 恒定），该族的结构性否定有族特异性，决定性检验在 ITC-99；ITC-99 为部分标注族（routed 833/1207，可用池 20 个）；`code/` 未动，未提交。

### 2026-10-24 PHYS-TOPOLOGY-EFFECT-20261024（改结构在布线后到底划不划算：理想线网的"虚假繁荣"机理）

**动机**：论文 4.6 节报"把 S 候选从 37 扩到 126，0 个带来 WNS 改善、90 个变差"，但那是**理想线网**口径。用户痛点三问的是：改结构在**物理世界**还划不划算，以及理想线网到底**错在哪**。

**工具**：`experiments/20261024_physical_labels/tools/topology_effect.py`（产出 `topology_effect.{json,txt}`）。

**测量口径（关键）**：`d_depth` / `d_n_cells` / `d_max_fanout` 是候选网表相对**电路基线**的差，会**随 ECO 历史累积**（实测 kind R 的平均 `d_n_cells` 从 iter 1–4 的 0.00–0.67 涨到 iter 5–8 的 3.46–4.92），故**不能当"本候选的动作量"**；但**同一池（同一电路、同一迭代）的候选共享同一迭代基线**，所以**池内离散度就是该候选自己的改动量**。所有主结论都在池内做出。

**结果（ITC-99，20 个可用池；b01=8 / b03=6 / b08=4 / b02=2）**：
- **池内"改动最多 vs 改动最少"**：加**逻辑深度**——理想口径 **12 胜 2 负 p = 0.0129（显著偏好）**，布线后口径 **7 胜 2 平 5 负 p = 0.7744（偏好消失）**；加**单元数**两口径方向一致（理想 13 胜 6 负 p = 0.1671，布线后 11 胜 8 负 p = 0.6476）。
- **池内跨类配对**（控制选择偏差：理想线网按类拒绝强度悬殊，R 被拒 306/321、G 只被拒 102/120）：布线后 **G vs R 10 胜 0 负 1 平 p = 0.0117**、**B vs R 10 胜 0 负 2 平 p = 0.0386**、B vs G p = 0.8036、JOINT vs R p = 1.0；理想口径 G vs R 同样 **10 胜 0 负 1 平 p = 0.0117**。
- **决策遗憾**：accepted 0.0124、ideal_argmax 0.0160（接受子集 0.0129）、随机 0.0756；**`min_struct_change` 0.1060 / `max_struct_change` 0.0990** → 靠结构改动量挑候选接近随机，比 ideal_argmax 差约 6 倍。

**结论**：① **物理上 G、B 确实优于 R，JOINT 无优势**，且**理想线网对"类"的判断基本正确**（G vs R 两口径一致）——理想线网的错误集中在"**偏爱加逻辑深度**"这一维度，不在分不清候选种类；② 这给"理想线网的虚假繁荣"提供了**机理级**证据：理想线网把加深逻辑层级当收益，物理上不成立；③ 结构改动量本身**不是**选候选的依据。

**边界**：探针级、非论文证据；布线后口径与理想口径之差**未做正式检验**，且布线后标签噪声受限（782 行中仅 183 行超候选级带 0.087496 ns），衰减是可能方向，故"偏好消失"是**与虚假繁荣一致**而非证明；结构改动量与候选**类别纠缠**（插 buffer 按定义就加单元），两者无法在本测量里完全分离；ISCAS89 族 26 个池的改动量全部一致、全部被排除（证实该族无结构变化可测）；ITC-99 为部分标注族；`code/` 未动，未提交。

### 2026-10-24 PHYS-DECISION-FLOOR-20261024（决策遗憾下界：物理标签还剩多少信息，AI 最多能省多少）

**动机**：LOG-20261024-14 测得纯图特征预测物理收益 ≈ 随机。需要区分两种解释：**(a) 特征选错了**，还是 **(b) 标签本身在池级就分辨不出差异**。若是 (b)，那么"该不该训 GNN"就不是口味问题，而是有测量依据的判断。

**工具**：`experiments/20261024_physical_labels/tools/decision_floor.py`（产出 `decision_floor.{json,txt}`），两族各跑一次，已接进两条分析链。

**方法**：池 = (电路, ECO 迭代)，与代理模型同口径。对每个选择器把"对池内最大值的遗憾"拆成
*可证明部分*（存在候选比所选候选好过判定带）与*噪声部分*（其余）；另做蒙特卡洛：把观测标签
当真值、叠加 σ=带/2 的合成噪声，估计**任何**单次测量选择器的不可约遗憾，并给出"跑第二个物理
实现并平均"后的版本；再在四个阈值下重算可证明遗憾做稳健性检验；最后用真实的双实现配对
校准 σ。

**结果（ISCAS89 / ITC-99）**：

| 指标 | ISCAS89 | ITC-99 |
|---|---|---|
| 判定带（池化，2σ） | 0.055542 ns | 0.087496 ns |
| 被接受候选：观测遗憾 / **可证明部分** | 0.0072 / **0.0000** | 0.0124 / **0.0000** |
| 理想 argmax：观测遗憾 / 可证明部分 | 0.0142 / 0.0058 | 0.0160 / 0.0000 |
| 靠结构改动量选：观测遗憾 / 可证明部分 | 0.0762 / **0.0673** | 0.1100 / **0.0945** |
| 可分辨候选 / 可分辨候选对 | 74/317 (23.3%) / 1266/4060 (31.2%) | 185/806 (23.0%) / 11544/38221 (30.2%) |
| 下界：单次测量 → 两次实现平均 | 0.0133 → 0.0072 ns | 0.0493 → 0.0311 ns |
| 真实配对经验 σ（判定带/2 的倍数） | 0.0134（0.48×） | 0.0232（0.53×） |

**结论**：① 在当前标签分辨率下**无法证明**存在比 FAECO 当前选择更好的选择（可证明遗憾 0.0000）；
"改结构选候选真的更差"则从相关升级为**可证明**（0.0673 / 0.0945 ns）；② 结论对带口径稳健
（四个阈值下可证明遗憾 ≤0.0044 / 0.0065 ns）；③ **把同一候选在两个物理实现下各测一次，
比换一个更聪明的模型更能改善选择**——这给"验证预算"一个物理依据，也给出"先提分辨率、
再谈模型"的次序；④ 判定带偏保守（经验 σ 只有带/2 的约 0.5 倍），故下界偏悲观。

**边界**：探针级、非论文证据；蒙特卡洛下界是估计（观测标签当真值），已用真实配对标出偏悲观方向；
真实双实现配对目前每池只有 1 个候选，池内"平均两次测量"的真实比较尚不可做，须等 I1/F1 批覆盖全族；
判定带用池化口径；ITC-99 为部分标注族；`code/` 未动，未提交。

### 2026-10-24 PHYS-ITC99-THREE-STAGE-20261024（第二个族的三点曲线 + 三档衰减：布局后档既便宜又更准）

**动机**：此前"理想 vs 布局后 vs 布线后"只在 ISCAS89 族（325 候选）成立，且 ITC-99 族的布局后档只跑到 6 个候选。布局后批 IPLACED 收齐（1207/1207）后，第二个族的完整三档首次可算——而这正是用户点名的"三点曲线与预估偏差拟合曲线"。

**工具链**：`three_point_curve_itc99.py` → `build_dataset_itc99.py` → `build_training_table.py --family itc99`
→ `extract_graphs.py --family itc99` → `surrogate_cross_stage.py --family itc99`
→ `calibration_three_stage.py` / `band_sensitivity.py` / `topology_effect.py` / `decision_floor.py`（均经
`run_analysis_itc99.py` 包装器）。

**结果**：

| 量 | ITC-99（n=892 / 922） | ISCAS89（n=325） |
|---|---|---|
| 理想→布局后 斜率 / 残差 sd / ρ | 0.9411 / 0.0250 / 0.8319 | 0.8911 / 0.0234 / 0.7870 |
| 布局后→布线后 斜率 / 残差 sd / ρ | **1.0219** / 0.0248 / 0.8362 | **0.9635** / 0.0241 / 0.8190 |
| 候选级带：布局后 / 布线后 | **0.024052** / 0.087496 ns | — / 0.055542 ns |
| 布局后标签训练 → 布线后标签 ρ（pooled） | 0.7486（布线后训练 0.7401） | 0.6477（布线后训练 0.6515） |
| 逐电路配对：布局后 vs 布线后训练 | **5 胜 0 平 2 负，p=0.4531** | 4 胜 0 平 4 负，p=1.0 |

布局后候选级带由 **749 对** IPLACED/IPLACEDF1 配对测得（pooled sd 0.012026、df=743、95% CI
[0.011165, 0.012705]）。

**结论**：① **衰减集中在布局阶段**——过了布局之后，物理信号基本不再衰减（布局后→布线后的斜率两族都 ≈1）；
② **布局后档同时更便宜（250 倍）且分辨率更高**（带窄 3.6 倍）；③ 因此
**"便宜的布局后标签可替昂贵的布线后标签做监督"在第二个族、30 池、7 电路的规模上确认**
（逐电路 p=0.4531，无差别）——这同时给出"验证预算"的物理依据与"训练集该怎么造"的答案：
**监督信号用布局后档，最终档只留作独立验收**。

**边界**：ITC-99 的 I0 批仍在跑（布线后 946/1207）、I1 未开 → **全部为部分标注族**，
批齐后由定稿链重算；布局后带由 749 对配对测得，尚非全族；布局后档与布线后档的寄生估计
**模型不同**，"布线后−布局后"**不是纯布线惩罚**；寄生来自 `estimate_parasitics`，非签核 RC 提取；
`code/` 未动，未提交。

### 2026-10-24 PHYS-STAGE-VERDICT-TRANSFER-20261024（跨阶段判定转移：布局后档能不能替布线后档做**判定**）

**动机**：LOG-20261024-16 证明的是"便宜的布局后档可替昂贵的布线后档做**监督**"（逐电路配对 5 胜 0 平 2 负，p=0.4531）。但**监督**与**判定**是两个不同的主张：前者说"布局后标签可以拿来训练预测器"，后者说"布局后档的接受/拒绝结论可以替代布线后档做最终验收"。后者才是"接受判定放到布局阶段、省掉布线运行"这一实践动作的依据，**此前无人测过**。

**工具链**：`stage_verdict_transfer.py`（新增）→ 读 `training_table.jsonl`（三档边际增益）与 `three_point_curve.json`（两档的候选级带）。两条分析链各加一步。

**结果**：

| 口径 | ITC-99 矛盾（n=892） | ITC-99 安慰剂 min/中位/max | ISCAS89 矛盾（n=325） | ISCAS89 安慰剂 min/中位/max |
| 各档用各自带 | **0** | 2 / 8.0 / 14 | **0** | 1 / 6.0 / 12 |
| 同带（布局后带） | **19** | 31 / 40.0 / 50 | **0** | 1 / 7.0 / 12 |
| 同带（布线后带） | **0** | 0 / 1.0 / 4 | **0** | 0 / 4.0 / 10 |
| 纯符号（无阈值） | **73** | 151 / 169.0 / 191 | **32** | 61 / 83.0 / 97 |

| 量（符号口径） | ITC-99 | ISCAS89 |
|---|---|---|
| 布局后档接受数 | 105 | 94 |
| 其中布线后证伪（证伪率） | 14（**0.133333**） | 15（**0.159574**） |
| 其中布线后为增益（存活率） | 74（0.704762） | 76（0.808511） |
| 布局后档拒绝后漏放的真实收益 | 59（0.097844） | 17（0.10119） |
| 台账现有接受决策的证伪率 | 0.295455（13/44） | 0.115385（3/26） |
| 电路内回归斜率均值 / R² 范围 | 0.951954 / 0.186305–0.972919 | 0.930217 / 0.566032–0.942888 |
| 逐电路配对：布局后判据 vs 理想判据 | 3 胜 2 平 2 负，p=1.0 | 1 胜 4 平 3 负，p=0.625 |

**结论**：① **"零矛盾"是带宽造成的假象，不是物理定律**——各档用各自带时 ITC-99 0 / ISCAS89 0 例矛盾，但同带口径下 ITC-99 出现 19 例、纯符号口径下 73 例（8.2%）；布局后带 0.024052 ns 比布线后带 0.087496 ns **窄 3.64 倍**，这个不对称本身就禁止了大量翻转；② **但一致性本身是真的**——安慰剂对照（把布线后标签在电路内置乱）的矛盾数远高于观测值，四个口径**全部低于安慰剂下界**；③ 机制是**两档测的几乎是同一个量**：电路内回归斜率均值 0.951954 / 0.930217、R² 多在 0.89–0.97 → **布线阶段主要是逐电路偏移，不重排候选**；④ **判据层面**：布局后档接受时布线后证伪 0.133333 / 0.159574、漏放 0.097844 / 0.10119；⑤ **逐电路配对两族都无差别**（p=1.0 / 0.625）→ "布局后判据优于理想判据"的池化差异**不成立**。

**与 LOG-20261024-16 合读**：监督层（布局后标签可替布线后标签训练）**成立**；判定层（布局后档的接受结论可替布线后档做最终验收）**不成立**。→ 工作流建议：**监督信号用布局后档（省 250 倍布线时间），最终验收必须用布线后档**。

**边界**：探针级、非论文证据；ITC-99 为部分标注族（布线后 946/1207、I0 在跑、I1 未开），批齐后由定稿链重算本条全部数字；布局后档与布线后档的**寄生估计模型不同**，"布线后−布局后"不是纯布线惩罚；寄生来自 `estimate_parasitics`，非签核 RC 提取；边际量量化到 0.01 ns；本条测的是**单候选判据的转移**，不是选择规则的遗憾（后者由 decision_floor 测）；`code/` 未动，未提交。


### 2026-10-24 PHYS-STAGE-KIND-EFFECT-20261024（布局后档误判了哪一类候选：kind 效应与池级偏移的分离）

**动机**：LOG-20261024-17 测的是"两档多久不一致"，没问"不一致的是哪一类候选"。若布局后档系统性误判某一类候选，则"按布局后档接受"的流程会系统性地做错某类决定，且纠正方向事先已知。

**工具链**：`stage_kind_effect.py`（新增，测 kind 与池级效应）+ `stage_quant_floor.py`（新增，量化底证伪）。两条分析链各加两步。

**结果 1 —— 按 kind 的符号翻转率（布局后与布线后符号相反 = 判定走错分支）**：

| kind | ITC-99 n | 翻转率 | 剔除量化边沿后 | 布局后正比例 | 布线后正比例 |
|---|---|---|---|---|---|
| B | 371 | **86 (0.232)** | 0.065 | 0.154 | 0.272 |
| G | 135 | **22 (0.163)** | 0.022 | 0.200 | 0.319 |
| JOINT | 45 | **3 (0.067)** | 0.000 | 0.089 | 0.111 |
| R | 341 | **25 (0.073)** | 0.006 | 0.050 | 0.088 |

**结果 2 —— 逐电路配对检验（池化差异不作结论）**：

| 对比 | 逐电路 | 精确二项 p |
|---|---|---|
| B vs G | B 更低 2 / 平 0 / G 更低 4（6 电路） | **0.6875** |
| B vs JOINT | B 更低 0 / 平 0 / JOINT 更低 3（3 电路） | **0.25** |
| B vs R | B 更低 1 / 平 0 / R 更低 3（4 电路） | **0.625** |
| G vs JOINT | G 更低 0 / 平 1 / JOINT 更低 2（2 电路） | **0.5** |
| G vs R | G 更低 0 / 平 0 / R 更低 4（4 电路） | **0.125** |
| JOINT vs R | JOINT 更低 1 / 平 0 / R 更低 1（2 电路） | **1.0** |

**结果 3 —— b09 反例查清（池级效应，不是 kind 效应）**：

| 量 | 值 |
|---|---|
| b09 iter 8 候选数 / 占 b09 | 53 / 60.9% |
| 该池偏移 | +0.07283 ns |
| 该池翻转率 | 37/53 = 0.698 |
| 池内偏移展度 / 量化底（b09 iter 8） | 9.8538 |
| 池内偏移展度 / 量化底（b01 iter 8） | 3.7031 |

同池内 **非 B 候选翻转 9/11 与 B 候选 28/42 几乎一样** → 池级效应，不是 B 的 kind 效应。

**结果 4 —— 量化底证伪（对 LOG-17 机制解释的检验）**：

| 族 | 残差 sd / 量化底 | 量化底占残差方差 | 共享信号展布 / 量化底 |
|---|---|---|---|
| ITC-99 | 3.594–17.3285 | 0.33%–7.74% | 6.6601–26.6013 |
| ISCAS89 | 2.8842–12.5828 | 0.63%–12.02% | 10.8685–29.128 |

**结论**：① **"插 buffer 被布局后档系统性误判"这个族级读法不成立**——逐电路配对 B vs R 1 胜 3 负（p=0.625）、B vs G 2 胜 4 负（p=0.6875），且剔除量化边沿后翻转率塌到 B 0.065 / R 0.006 / JOINT 0.000，**族级差异主要由近零小数值变号贡献**；② **b09 不是"布线重排候选"的反例，而是"某个网表状态被布线阶段整体改变"的反例**（该池 53/87 个候选集中在 iter 8，偏移 +0.07283 ns，同池内非 B 与 B 的翻转率几乎相同）；③ **LOG-17 的机制解释通过量化底检验**：残差 sd 是量化底的 3.594–17.3285 倍、量化底只占残差方差 0.33%–7.74% → **R² 0.186305–0.972919 不是舍入产物**；④ 因此布局后档的偏差结构是"**逐池平移 + 近零小数值变号**"，不是"某类候选不可信" → 提升可用性的正确方向是**同池重新标定**与**提高读数分辨率**，**不是**按 kind 特判。

**边界**：探针级、非论文证据；ITC-99 为部分标注族（布线后 946/1207、I0 在跑、I1 未开）；布局后档与布线后档的**寄生估计模型不同**，"布线后−布局后"不是纯布线惩罚；**kind 与池结构纠缠**（本条用逐电路配对与逐池表分离，但**不能完全分离**）；边际量量化到 0.01 ns，**近零小数值变号占翻转的多数**；`code/` 未动，未提交。


### 2026-10-24 PHYS-TWO-IMPL-CHOICE-20261024（第二次物理实现是否改善"选择"：留一法 + 判定带样本量的发现）

**动机**：LOG-20261024-15/16 用蒙特卡洛模拟给出"跑第二个物理实现比换一个更聪明的模型更有效"（单次 0.0419 ns → 两次平均 0.0257 ns），并把"池内平均两次测量 vs 单次测量"的**真实**比较登记为 OI-052 第 5 条（当时：每个池只有 1 个双实现候选，**尚不可做**）。本条做三件事：① 把"怎么做这个比较"在方法上定清楚，并**证明现有做法有偏**；② 实测该比较在现有数据上的行为；③ 查出一个此前没被注意的推论——**I1 批次还决定判定带的样本量**。

**工具链**：`two_impl_choice.py`（新增，留一法）+ 批次结构核查 + 带的独立复算。两条分析链各加一步。

**结果 1 —— 留一法（LOO）与现有做法的差别**：

| 方案 | 定义 | 是否有偏 |
|---|---|---|
| 现有做法 | 单次 argmax 与平均 argmax **都相对于"平均标签的最大值"** | **有偏**：平均选择器被用它自己的尺子评分 |
| **留一法** | 留出一个实现当**评分器**，选择器只能用留下的实现；两方向各做一次 | **无偏**：选择器永远不靠它读过的测量得分 |
| 三实现方案 | 选择器看 2 个（均值），评分器看第 3 个 | 无偏，且**两个选择器真正不同** |

**结果 2 —— 实测行为（这是本条的关键约束）**：

| 族 | 双实现候选 | 可用池 | 两方向结果 |
|---|---|---|---|
| ISCAS89 | 13 | 3 | F0: 3 池全平局（遗憾均 0.00000 ns，选中同一候选）；F1: 3 池全平局（遗憾均 0.00000 ns，选中同一候选） |
| ITC-99 | 44 | 0 | F0: no pool has two candidates carrying the realisation F0；F1: no pool has two candidates carrying the realisation F1 |

**关键约束**：**只有两个实现时，留一法下"平均选择器"退化为"单次选择器"**（留进的只剩一个实现），比较**必然是平局**——这不是数据不好，是**方案在两个实现的样本量下没有区分力**。**真实的"单次 vs 两次平均"比较需要第三个布线实现。**

**结果 3 —— 判定带的样本量（此前未被注意的推论）**：

| 配对 | 可配对网表 | df | 2σ |
|---|---|---|---|
| I0P0 vs I1P0（**当前用的**） | 51 | 44 | **0.087496 ns** |
| I0 vs I1（**I1 跑完后可用**） | 1207（当前 0，I1 带标签 0/1207） | — | — |

**I0/I1 与 I0P0/I1P0 是同一条物理实现轴**（F0: pins met3/met2 + util 10；F1: pins met5/met4 + util 30，同冻结版图），`I0P0` 与 `I0` 重叠的 58 个键 **netlist 哈希 58/58 相同**，是真正的同网表配对。→ **候选级带（决定全项目每一个 GAIN/INCONCLUSIVE/REGRESSION 判定的那条阈值）当前只由 51 个网表支撑；I1 跑完后可扩到 1207 个，样本量约 20 倍**，所有依赖带的结论都要重算。

**结论**：① "两次实现是否改善选择"的**真实**比较**需要第三个布线实现**，现有两实现数据无法给出有区分力的答案（ISCAS89 的 3 个池实测全平局，ITC-99 为 0 池）；② LOG-15/16 的"跑第二次实现更有效"目前**只有模拟支撑**，本条明确它是模拟而非实测；③ **I1 批次的第二重价值（且更基础）是扩大判定带的样本量**，这条带支撑着 LOG-14/15/16/17/18 的每一个判定结论。

**边界**：探针级、非论文证据；ITC-99 为部分标注族（I0 带标签 932/1207、**I1 带标签 0/1207**）；"两个实现不够"是**方法学推导**（LOO 下的退化性），在 ISCAS89 的 3 个池上实测到"必然平局"的行为，但**样本极小**，不作为统计结论；判定带样本量的结论是**算术事实**，**带的收紧幅度未知**，须待 I1 完成后实测；`code/` 未动，未提交。


### 2026-10-24 PHYS-BAND-SCOPE-AUDIT-20261024（判定带作用域审计：满样本修正 +24%、可复现性底噪 0、留一电路敏感性、恒等式缺陷修复）

**动机**：LOG-20261024-19 查出"判定带只由 58 个网表支撑"这条**算术事实**，但没有回答两个更基础的问题：① **链子会不会自己改**（不会——`F0_SIDE`/`F1_SIDE` 写死为 pilot，且**布局后带是在 IPLACEDF1 只跑完 749/1207 时算的**，方向是偏窄）；② **带里有没有运行噪声**（此前从未测过，而 I0P0 vs I0 正好是同网表同实现的重跑）。本条把"带"从一组裸数字变成**带作用域、带来源、带稳健性门**的量，并因此改掉三处旧结论。

**工具链**：新增 `band_scope_itc99.py`（批次覆盖 + 同实现重跑底噪 + 作用域选择 + 布局后带满样本重算 + 留一电路敏感性）与 `kind_gate_probe.py`（kind 效应的双口径三道闸）；改 `candidate_level_noise.py`（抽出 `compute_band` 供两族复用 + 写入作用域溯源）、`decision_floor.py`（删除恒等式口径，改引留一法）、`run_analysis_itc99.py`（作用域按覆盖度自动选择）；两条分析链各纳入新工具并调整先后。

**结果 1 —— 判定带此前没有作用域，而且链子不会自动变**：

| 作用域 | 批次对 | 可配对 | 电路 | df | 2σ |
|---|---|---|---|---|---|
| `pilot_subset`（此前一直用的） | I0P0 vs I1P0 | 51 | 7 | 44 | 0.087495 ns |
| `full_family`（家族该用的） | I0 vs I1 | 1207 | 7 | 待 I1 收齐后实测 | — |

作用域现由 `select_scope()` **按实际覆盖度**选择（审计工具与测量工具共用同一函数），并把 `band_scope` / `f0_batches` / `f1_batches` 写进 `candidate_level_noise.json`。**当前生效 `pilot_subset`**，理由（I1 缺 829/1207 标签）写进产物。

**结果 2 —— 布局后带此前测在半成品 F1 侧上，方向是偏窄**：

| 口径 | 配对 | 电路 | df | pooled sd | 2σ |
|---|---|---|---|---|---|
| 旧（IPLACEDF1 只完成 749/1207，覆盖 6/9 电路） | 749 | 6 | 743 | 0.012026 | 0.024052 ns |
| 新（满样本） | 1207 | 9 | 1198 | 0.014913 | **0.029826 ns（+24.0%）** |

带宽比（routed/placed）由 **3.637785 降到 2.933514** → **LOG-17 引用的"3.64 倍带宽不对称"作废**。原因不是测量误差，而是**"先跑完的那几个电路"不是随机样本**（被漏掉的 b09 电路内 sd 是家族 pooled 的 2.2 倍）。

**结果 3 —— "半成品的全族带"是陷阱（作用域必须显式的实证）**：当前 I1 只有 378 个标签，"I0 vs I1"口径已给出 2σ = 0.031297 ns（比 pilot 带窄 2.8 倍），**而它只覆盖 1 个电路**。若链子"看到 I1 有数据就用"，项目会拿到一个看起来更精确、实则只来自一个电路的带。

**结果 4 —— 同实现重跑的可复现性底噪 = 0.000000 ns**：I0P0 vs I0（58 个同网表同实现的重跑）与 I1P0 vs I1（8 个）**逐位相同，非零差 0 个** → 布线确定性成立，**带里不含运行噪声成分**。推论：**"重跑同一实现"对降低不确定性毫无帮助**（物理上的零，不是方法退化）；要降低不确定性只能换**真正不同的实现**——与 LOG-19"需要第三个布线实现"是两条独立证据。

**结果 5 —— 电路间离散度差约 3.8 倍，"家族单一带"是伪概念**：逐电路 sd 从 b13 0.008634 到 b09 0.032812；b01 一家占掉 df 的 47.4%；**留一电路后池化带最大变动 24.6%**。任何"用家族带判 GAIN/REGRESSION"的结论都必须写明口径（池化带 / 逐电路带，`band_sensitivity.py` 两种都给）。

**结果 6 —— 修掉一个恒等式缺陷**：`decision_floor.py` 的"平均标签 argmax 遗憾 vs 单次测量 argmax 遗憾"**都相对于平均标签的最大值**，而前者的遗憾**恒等于 0**（它按定义就取到了那个最大值）→ 该比较**永远不可能有别的结果**；I1 覆盖到 7 个池后它浮出水面，形状像"平均两次测量更优"。已删除，改引留一法结论（两族均为全平局）。

**结果 7 —— kind 效应在扩样后仍不成立，新出现的"显著"是口径产物**：

| 比较 | 门1 逐电路（工具口径） | 门1 严格口径 | 门1 去量化边沿 | 门3 池内配对 | 稳健？ |
|---|---|---|---|---|---|
| G vs R | p=0.03125 | p=0.21875 | p=0.21875 | p=0.453125 | **否** |
| B vs R | p=0.6875 | p=0.6875 | p=0.6875 | p=0.453125 | **否** |
| B vs G | p=1.0 | p=0.125 | p=0.453125 | p=0.011818 | **否** |

"工具口径"把 0.00 与正数的组合也算翻转；"严格口径"要求两值非零。**四道门只过一道 → 判定为口径产物，不作 kind 结论**（与 LOG-18 对 B-vs-R 的处理同一套三道闸）。

**结果 8 —— LOG-14 的"理想线网偏爱加逻辑深度"在扩样后失去统计支持**：理想口径 16 胜 0 平 7 负 p=0.0931、布线后口径 13 胜 2 平 8 负 p=0.3833，**两档都不显著**；而**跨类判断在两档都显著**（布线后 B vs R 16:2 p=0.0013、G vs R 15:2 p=0.0023）→ **"理想线网分不清候选种类"继续被否证；"它偏爱加逻辑深度"这一诊断在扩样后不成立**（是"不显著"，不是"证伪"）。

**结论**：① 判定带**必须带作用域**，且作用域必须由数据决定、由审计与测量共用同一规则；② **批次未完成时算出的阈值量方向可能是错的**（本次偏窄 24%）；③ 布线确定性成立 → 只有换实现才能降低不确定性；④ "家族单一带"是伪概念，判定必须写明口径；⑤ kind 效应仍不成立，且**翻转率对"零值怎么算"敏感**，任何 kind 级读法必须同时报两种口径。

**边界**：探针级、非论文证据；ITC-99 为部分标注族（I0 带标签 1207/1207、I1 带标签 378/1207），**布线后带的最终值仍未定**（全族口径待 I1 收齐后实测，届时须复核本条的全部前后对照数字）；布局后与布线后档寄生估计模型不同，"布线后−布局后"不是纯布线惩罚；寄生来自 `estimate_parasitics`，非签核 RC 提取；边际量量化到 0.01 ns；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-RESOLVABLE-POSITIVE-20261024（候选级"可分辨"分类 + 接受判据物理选择性 + F2 第三个布线实现就绪）

**动机**：LOG-20261024-20 查清了判定带的作用域与底噪，但**没有解决"用哪把尺子量模型"**。本轮先证伪本项目一直在用的那把尺子（池级决策遗憾），再换上候选级分类，并把"理想线网说谎"这个命题**从强版本修正为有证据支撑的形状**。

**工具链**：新增 `resolvable_positive_classifier.py`（候选级分类：标签模式 gain/harm/resolvable、按池自助 CI、阈值扫描、模型类交叉验证、四道闸、消融）与 `acceptance_physical_selectivity.py`（接受 vs 拒绝的物理分类 + 两种置换零模型 + 逐电路配对）；新增 `gen_itc99_f2_jobs.py`（第三个布线实现的作业表与清单）；两条分析链各纳入两个新工具。

**结果 1 —— 池级决策遗憾指标在本族没有分辨率（尺子坏了）**：`surrogate_cross_stage` 里全部选择器在 25% 验证预算下的平均遗憾落在 **0.004146 – 0.029268 ns**，而判定带是 **0.087496 ns**（布线后）/ **0.029826 ns**（布局后）→ **所有方法差异都低于测量分辨率**。此前"纯图特征≈随机"（LOG-14）因此是**指标失效**，不是模型结论。

**结果 2 —— 换上候选级分类后（图结构依然无信号）**（布线后档，标签 resolvable = |Δ|>带，243 个正例）：

| 特征集 | ITC-99 AUC | ISCAS89 AUC |
|---|---|---|
| `structural`（23 个门级图特征） | **0.444433** | **0.43676** |
| `proxy_only`（14 个人工 proxy 特征） | 0.667006 | 0.578368 |
| `ideal_only`（理想线网标签，1 个特征） | 0.885202 | 0.757152 |
| `placed_only`（布局后标签，1 个特征） | 0.926597 | 0.746578 |
| `structural_plus_ideal` | 0.83832 | 0.655166 |
| `proxy_plus_ideal` | 0.889887 | 0.758156 |

**纯图特征在两族都低于 0.5**（点估计低于随机）；**给理想线网标签加上图特征在两族都变差**（0.885202 → 0.83832 / 0.757152 → 0.655166）；**单个布局后标签（~2 s/候选）比 23 个图特征、比 14 个 proxy 特征、比理想线网标签都强**。

**结果 3 —— 一类标签欠功效**：布线后 `gain` 标签只有 **12** 个正例、布局后 **23** 个，AUC 在两档之间**方向相反**（布线后 0.226244 / 布局后 0.849456）→ 纯噪声。工具新增 `powered` 标志（正例数 < 30 即 `POWERED=False`），三类标签一起输出而不是只报好看的那个。

**结果 4 —— 接受判据的物理选择性（修正"理想线网说谎"的强版本）**：

| 族 / 档 | 接受：增益 / 损害 / 惰性 | 拒绝：增益 / 损害 / 惰性 | 增益富集 | 损害比 | 置换 p（电路匹配 / 池匹配） |
|---|---|---|---|---|---|
| ITC-99 routed | 11.3636% / 4.5455% / 84.0909% | 0.6092% / 20.7137% / 78.6771% | 18.6533 | 0.2194 | 0.0001 / 0.0035 , 0.0 / 0.0029 |
| ITC-99 placed | 29.5455% / 9.0909% / 61.3636% | 0.9320% / 51.1650% / 47.9031% | 31.7012 | 0.1777 | 0.0 / 0.0 , 0.0 / 0.0 |
| ISCAS89 routed | 26.9231% / 3.8462% / 69.2308% | 3.0100% / 20.7358% / 76.2542% | 8.9446 | 0.1855 | 0.0 / 0.0198 , 0.0 / 0.0245 |
| ISCAS89 placed | 42.3077% / 0.0000% / 57.6923% | 2.0067% / 24.7492% / 73.2441% | 21.0832 | 0.0 | 0.0 / 0.0009 , 0.0 / 0.0267 |

逐电路配对（损害）：ISCAS89 布局后 **0W/8L**（p=0.0078125，已达 8 个电路的最小可达值）、ISCAS89 布线后 1W/6L、ITC-99 布局后 0W/7L、ITC-99 布线后 1W/6L → **所有不平的电路方向一致**。

**结论**：① **理想线网判据不是随机的**——它是**有效的避害过滤器**（损害率降到拒绝集的 1/4.6~1/5.4，置换 p ≤ 0.0035），"理想线网对物理毫无选择性"的**强版本说法作废**；② **但它几乎不交付增益**——接受集里 **84.0909%（ITC-99）/ 69.2308%（ISCAS89）** 的候选**物理惰性**（效应小于换一次实现），真实增益只有 11.3636% / 26.9231% → **"理想线网说谎"的准确形状是"避害有效、增益无效"**；③ **候选级 AUC 才是本族可用的尺子**，且**所有可学习信号都在两个标签里**（理想线网、布局后），**图结构在候选级没有信号**。

**结果 5 —— F2（第三个布线实现）已就绪**：作业表 `jobs_itc99_f2.tsv`（1207 作业：7 baseline + 1193 候选 + 7 final），pin 轴 F0 (met3 横, met2 竖) → F1 (met5 横, met4 竖) → **F2 (met3 横, met4 竖)**，F2 与 F0 只差纵向、与 F1 只差横向；identity check 不匹配 0、缺失网表 0。**刻意不注册进 `build_dataset_itc99.py` 的 `BATCHES`**——主数据集、判定带定义与分析链不因侧实验移动。实测代价：I1 批 8.481 CPU·h（均值 36.83 s、中位 12 s、p90 88 s），I0 批 23.79 CPU·h → **F2 全族外推 2–4 h 墙钟**（PAR=6）。

**结论与工程含义**：① **池级遗憾在本族不可用**（低于判定带），任何模型比较必须先检查指标是否超过判定带；② **"训练 GNN 替代 OpenSTA"在本族没有可夺取的空间**（纯图特征 AUC < 0.5，且加到标签上有害）——真正的杠杆是**把便宜的布局后档当监督信号**（LOG-16"监督可替"的候选级确认）；③ **"理想线网说谎"要改述为"避害有效、增益无效"**；④ F2 是判定带稳定性与留一法比较的唯一解锁条件。

**边界**：探针级、非论文证据；**布线后带仍是 pilot 口径**（0.087496 ns，I1 未收齐，全族口径待定稿链复跑后实测）——**带一变，本条全部以带为门槛的分类结果都要重算**；"惰性"指**效应小于换一次布线实现**，不是"完全无效应"；置换零模型只控制**电路**与**池**，不控制候选生成器的选择偏好；AUC 自助 CI 以**池**为单位重采样；图特征是**门级图的标量摘要**，不是 GNN 编码器 → **"图结构无信号"不能外推为"GNN 无信号"**；寄生来自 `estimate_parasitics`，非签核 RC 提取；边际量量化到 0.01 ns；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-TOOL-VERIFICATION-20261024

**目的**：在第三个布线实现 F2 的长批次（外推 2–4 h 墙钟）开跑之前验证其后处理工具，并把验证中查出的缺陷修掉；这是"先验证再开批"纪律的一次实际兑现。

**产物**：`experiments/20261024_physical_labels_itc99/tools/build_f2_labels.py`（修）、`experiments/20261024_physical_labels/tools/impl_stability_probe.py`（重写）、`experiments/20261024_physical_labels{,_itc99}/impl_stability.json`、`experiments/20261024_physical_labels_itc99/f2_labels_summary.json`、`scratch/{check_f2_hash_and_smoke.py,quantify_f2_hash_impact.py,which_affected_bases.py,f2_chain_receipt.py,finalize_f2_chain.sh,launch_f2_chain.sh}`、`scratch/{f2_hash_impact.json,f2_hash_affected_files.json}`

**查出的缺陷（摘要口径）**：ledger 的 `base_netlist_hash` 用**文本模式**摘要（`read_text()` 的通用换行转换），F2 标签构建器却只索引**字节**摘要。实测：47 个不同的 ledger 基线哈希，**字节口径命中 41 个、文本口径命中全部 47 个**；逐候选回读后，1193 个候选里 **39 个（3.27%）** 会静默失去边际量（基线是 6 个带 CRLF 的电路级 `mapped.v`：b01 11、b02 11、b10 9、b09 6、b03 1、b08 1）。**修法**：双摘要索引 + 两道自检（摘要口径自检在任何 run 之前即可算；空列自检在批次完整后生效）。修后实跑：`47 ledger base hashes -- byte 41 / text 47 / unmatched 0`。

**重写的探针**：批次映射按族显式配置（ITC-99 = `I0/I1/I2`；ISCAS89 = `F0`+`S713R` 对 `F1`+`F1S713`）；每个带带**逐对完整性判定**（判据落在配对键集上）；F2 只有在标签相对作业表收齐时才算可用；半成品带照打但不进稳定性比值与三点比较。

**交叉验证（ISCAS89）**：重写后的探针独立复现存储产物——df **40**、CI95 **[0.01709, 0.031385]**、候选网表 **48**、2σ **0.055543**（存储值 0.055542；差 1e-6 是**舍入口径**：存储产物先把池化 sd 舍入到 6 位再乘 2）。

**边界**：工程与工具链条目，**不产生新的科学结论**，不改动 LOG-20261024-21 的任何数字；探针级、非论文证据；F2 批次本身仍在跑，本条记录的是工具侧缺陷与修复，**不是 F2 的结果**；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-BAND-CHANGE-PREVIEW-20261024（LOG-20261024-23）

**目的**：在 I1 批收齐之前，量化"判定带从 pilot 口径（2σ = 0.087496 ns）切到全族口径（预览 2σ = 0.050419 ns，窄约 42%）"对 LOG-20261024-21 全部结论的影响，并把结论分成"站得住"与"会翻"两类。

**产物**：`project_docs/evidence/r30_band_change_preview_20261024/`（`band_change_preview_summary.json`、`BAND_CHANGE_PREVIEW.md`、`band_change_preview.py`、`print_band_preview.py`）、`scratch/band_change_preview.py`、`scratch/print_band_preview.py`、`scratch/check_control_faithfulness.py`

**方法**：harness **import 两个工具、只覆盖 band 参数**（不重写任何统计量），对**同一张训练表**跑对照遍（现行带）与预览遍（新带）。**对照遍必须精确复现存储的 LOG-21 产物**——实测 **20 项检查、0 处不符、最大偏差 0.0**（含 `structural` 0.444433、`proxy_plus_ideal` 0.889887、三种标签的正例数 243/12/231、接受集 44 与拒绝集 1149、增益富集 18.6533）。第一版 harness 把联表后的 1117 行误传给使用原始 1207 行的接受判据工具（拒绝集因此变成 1073），是**对照遍抓出了这个错误**。

**为什么预演近乎最终答案**：训练表的**布线后标签来自已收齐的 I0 批**、**布局后标签来自已收齐的 IPLACED**，**I1 只改带、不改标签**；唯一未知量是带的最终值（预览取自 I1 = 1058/1207）。

**结果 —— `resolvable` 标签（正例 243 → 389）**：`structural` 0.444433 → 0.445175（CI [0.3726, 0.5301] 仍含 0.5，四道闸 G1 不过）；`ideal_only` 0.885202 → 0.854611；`placed_only` 0.926597 → 0.894462（**仍是单特征最强**）；`proxy_plus_ideal` 0.889887 → 0.814108；`structural_plus_ideal` 0.83832 → **0.751665**（与 `ideal_only` 的差距由 0.047 扩到 0.103）。**`harm` 标签**（231 → 352）方向不变（`structural` 0.476877 → 0.503017）。

**结果 —— `gain` 标签翻号（本条最重要的发现）**：正例 **12 → 37**（跨过功效下限 30），`powered` 由 False 变 True；`structural` **0.226244 → 0.661449**（CI [0.4560, 0.8176] 排除 0.5，G1、G2 过，**G3 阈值扫描与 G4 预算召回不过**）；`structural_plus_ideal` 0.233974 → 0.684222；`kind_only` 0.293401 → 0.103804；`proxy_plus_ideal` 0.701207 → 0.657432（G1 由 Y 变 n）。

**结果 —— 接受判据的物理选择性**（同一张表、同一批候选 44/1149）：接受集真实增益/损害/惰性 **11.36% / 4.55% / 84.09% → 25.00% / 4.55% / 70.45%**；拒绝集 0.61% / 20.71% / 78.68% → **2.26% / 32.03% / 65.71%**；增益富集 **18.6533 → 11.0483**（下降是因为**拒绝集**的真实增益率也升了几倍，**不是**接受集变差）；损害比 **0.2194 → 0.1419**（**避害更强**）；置换 p 全部降到 0.0；逐电路：增益 3W/0L/4T p=0.25 → **5W/0L/2T p=0.0625**，损害 1W/6L/0T p=0.125 不变。

**结论分层**：**站得住**——(a) "图结构无候选级物理信号"（限于 `resolvable` / `harm` 标签）；(b) "给标签加图特征反而变差"（且更强）；(c) "便宜的布局后档可当监督"；(d) "接受判据有真实物理选择性"。**会翻 / 须改述**——(e) **"训练 GNN 替代 OpenSTA 在本族无可夺取空间"必须加限定**（不成立于 `gain` 标签）；(f) **"理想线网说谎 = 避害有效、增益无效"须改为"避害更强、增益有限"**，**"惰性 84.09%"作废**（改为约 70.45%）；**"接受了 N 个候选因此改善了 WNS"仍然不能写**。

**边界**：探针级证伪预演，**不是论文证据**；预演**固定了训练表**（只变门槛），最终数字由定稿链在 I1 收齐后重算；G3/G4 在 `gain` 标签上仍不过，**不得据 `gain` 标签的单点 AUC 宣称图特征有信号**；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-SIGNAL-ATTRIBUTION-20261024

**目的**：判定带落定（`full_family` 口径，布线后 2σ = 0.049752 ns）后，把"图特征到底有没有物理信号"追问到底：拆分特征集 → 跨族复现 → `harm` 标签方向对照 → **池级 vs 候选级分解**。

**产物**：`project_docs/evidence/r30_signal_attribution_20261024/`（`signal_attribution_summary.json`、`SIGNAL_ATTRIBUTION.md` + 6 个 harness 副本）、`scratch/pool_level_decomposition.py`、`scratch/structural_signal_harm.py`、`scratch/build_attribution_evidence.py`

**方法**：全部复用工具自己的代码（`build_matrix` 被 monkey-patch 以支持拆分特征集；留一电路交叉验证、ridge 解析 LOO λ 搜索、按候选池自助 CI 全部不变）。**池级 vs 候选级分解**用同一套 OOF 预测算出三个读数：池化 AUC、**仅池均值**（每个候选只拿自己池的平均分 → 只剩池间成分）、**池内 AUC**（逐池 AUC 再平均 → 只剩候选级成分）。再加两个对照：平凡基线 `kind_only`（kind 独热 + iteration）与 `harm` 标签（能预测"变坏"的特征是在预测方向还是幅度）。

**结果 —— ① 拆特征集**（最终带、`resolvable`，正例 434）：局部拓扑 0.446149、全局规模 0.483604、改动量 0.560230、**`one_depth` 0.591712**（池化里唯一 CI 排除 0.5 的，但**逐电路降到 0.545425、CI 含 0.5 不再显著**——预演带下的 0.6048 是更宽的带喂出来的）、`one_max_fanout` 0.533817、`one_n_cells` 0.531071。

**结果 —— ② 原假设被推翻**：LOG-23 怀疑 `gain` 标签上的信号是"改动量代理被接受"，实测**方向相反**：`d_depth` 与 `gain` 标签相关 **-0.194702**、`d_n_cells` **-0.244070**（正例 mean|Δcells| 0.8125 vs 负例 3.128157）→ 改动越小的候选反而越可能是真实增益。

**结果 —— ③ 幅度效应而非拓扑效应**：`one_depth`/`one_max_fanout` 在 **`harm` 标签上同样预测为正**（池化 0.641897 / 0.628593，逐电路 0.609394 / 0.6358）；ISCAS89 同向（`struct_global_only` 在 harm 上池化 0.683751）→ **它们预测 WNS 会动多远，不预测往哪边动**。

**结果 —— ④ 池级 vs 候选级分解（最硬的一条）**：`gain` 标签上 `structural` 池化 **0.698248**，而**只知道池均值的预测器就有 0.677415**、池内 0.613867 → **LOG-23 记录的"`gain` 上 `structural` 由 0.226244 翻到 0.661449（最终 0.698248）"是电路/池间差异，不是候选级区分能力**。池内读数下 **`kind_only` 0.555062 与最好的图特征集 0.561297 持平**（`harm` 上 0.572068 vs 0.577145，`gain` 上 0.655336 vs 0.651380–0.672469），ISCAS89 三标签池内全部 ≈0.5 且 CI 均含 0.5。

**结论分层**：**站得住且更强**——"图结构无候选级物理信号"（不是"低于随机"，而是"没有超过 kind 独热 + iteration"）；"便宜档当监督"（`placed_only` 0.896779 仍是最强单特征）；"接受判据有物理选择性且避害更强"（接受集增益 25.00% / 损害 6.82% / 惰性 68.18%，增益富集 7.5593、损害比 0.1944、置换 p 全 0.0）。**必须加限定**——"训练 GNN 替代 OpenSTA 无可夺取空间"要注明是**候选级读数**上的结论；**唯一可用的正面结论**——池级信号是真的（池均值预测器单独 0.677415），杠杆是"便宜的布局后档当监督 + 按池排序验证预算"。

**边界**：探针级、**非论文证据**；特征子集 **post-hoc**（9–11 个特征集 × 3 标签 × 2 族 ≈ 60 格，**未做多重比较校正、未做嵌套选择**）；图特征是**门级图的标量摘要，不是 GNN 编码器**（"摘要无信号"不等于"GNN 无信号"）；池化读数混入很强的电路间成分（ITC-99 逐电路正例率 0.206612–0.616438）；寄生来自 `estimate_parasitics`、非签核 RC 提取；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-F2-PREFLIGHT-20261024

**目的**：F2（第三个布线实现）批落地**之前**，把「从未在有第三实现的状态下跑过的三实现比较路径」在合成夹具上先跑通，并**定下真实数据的解读判据**。

**产物**：`project_docs/evidence/r30_f2_preflight_20261024/`（`f2_preflight_keycheck.txt`、`f2_preflight_probe.txt`、两个 harness 副本）、`scratch/f2_preflight_keycheck.py`、`scratch/f2_preflight_probe.py`

**方法**：① **配对前置条件实查**——三张作业表 I0/I1/I2 的键集、网表路径、candidate_hash、kind 是否逐项一致（探针按 `(circuit, key)` 配三个实现，对不上会静默出 0 个池）；② **沙箱夹具**——把探针的族目录指向 scratch 下的沙箱（真 F0/F1 数据 + 合成 F2），跑三档：无 F2（闸门）、完全合成的可交换三实现、相关（不可交换）第三侧；③ 每档都核对输出并对照"该出现什么"。

**结果 —— 配对条件**：三张作业表各 1207 行，**键集完全相同**；每键的**网表路径 0 处不符、candidate_hash 0 处不符、kind 0 处不符**；物理轴 F0(met3/met2/util 10) → F1(met5/met4/util 30) → **F2(met3/met4/util 30)**（与 F0 只差纵向、与 F1 只差横向）；数据集行 I0 1207、I1 1207，**1207/1207 全部出现在 F2 作业表** → **配对不会静默落空**。

**结果 —— 夹具 A（无 F2）**：探针给出 F0-F1 2σ = **0.049753 ns**（与定稿存储的 0.049752 差 1e-6，即工具自述的舍入口径），并**拒绝**三实现路径（"NOT COMPUTED: the third realisation is not complete"）→ **完整性闸门按预期生效**。

**结果 —— 夹具 B（完全合成的可交换三实现）**：三个两两带 **0.050648 / 0.051984 / 0.050562**，**max/min = 1.028124 ≈ 1**（可交换下三个差的方差相同，带应当一致）；三实现留一比较跑出 **144 个 pool-direction 对**，平均标签挑选器胜 **38** / 平 **85** / 单次胜 **21**，**p = 0.0363**（平均两个实现把噪声减半 → 平均应当更好；这是合成真值）。

**结果 —— 夹具 C（相关的第三侧）**：用 F2 = F1 + 噪声造的非可交换第三侧给出 max/min = **1.718223** → **"某一对特别松或特别紧"这件事机器看得见**。

**自我更正（夹具抓住的建模错误）**：第一版夹具把合成 F2 建成"真 I1 行 + 噪声"，于是 **F2 与 F1 共享同一份噪声**（F2 = I1 + ε）→ Var(d_F1F2) = σ_r² 而非 2σ_r²、Var(d_F0F2) = 3σ_r² → 夹具给出 max/min = 1.70，**差点被当成"真实 F2 的预期值"**。修正：**用两个实现造不出可交换的第三个实现**（三个两两差代数相关：d_F0F2 = d_F0F1 + d_F1F2），夹具必须**三侧全合成**。

**给真实 F2 的解读判据**：① 三对带 max/min ≈ 1 → 三个实现**可交换**，带是测量系统的良定义属性；② 明显偏离 → **F2 的噪声水平与 F0/F1 不同**（F2 与 F0 同横向 pin、与 F1 同纵向 pin），说明实现敏感度**由物理轴驱动**；③ 三实现留一比较参照夹具 B：**平均标签挑选器应小幅但一致地优于单次测量**（夹具 38/21、p=0.036，差幅在 0.004–0.005 ns 量级，0.01 ns 量化带来大量平局）；**若真实结果出现"平均更差"，那是数据结论而不是工具故障**（夹具已证明工具在有优势时会显示优势）。

**边界**：全部为**夹具/探针级**，**不是论文证据**；合成夹具的数字**只用于验证代码路径与判据**，**不得当作物理结果引用**；真实 F2 的三条带与三实现比较**必须等 I2 收齐后由 `finalize_f2_chain.sh` 自动产出**，**首次解读前先核对本条的判据**；`code/` 未动、HEAD 未变、未提交。

### 2026-10-24 PHYS-F2-WSL-RESTART-20261024

**目的**：记录 2026-10-24 22:00 前后 **WSL 实例重启**把 F2 批（626/1207）与后处理链一起带走的事件，以及恢复与加固措施。

**产物**：`scratch/restart_f2.sh`（可分别拉起 `batch` / `chain`）、`scratch/f2_watchdog.ps1`（**Windows 侧**看门狗）、`scratch/f2_watchdog_check.sh`（状态探针）、`scratch/diag_f2_now.sh`、`scratch/diag_f2_death.sh`

**现象与归因**：22:00:36 状态文件最后一次写入后不再更新（监督器每 30 s 写一次）；`openroad` 进程 0、load 0.23。
`uptime` = **0 min**、`dmesg` 全是新启动日志 → **实例被重启/回收**；新 boot 无 OOM 记录、内存上限 11962 MB、空闲 10119 MB、swap 未用 → **不是 OOM**。
**旧 boot 的内核日志随实例消失，死因无法确证**，故记为"实例被重启，原因未确证"，不做无证据归因。

**影响面**：F2 批停在 **626/1207**、后处理链同时消失；**已完成部分不受影响**（定稿链 21:36 已完成、LOG-20261024-12 已落地、626 个作业结果不丢）。

**恢复**：`scratch/restart_f2.sh` → 监督器 PID 435（SID 435）、后处理链 PID 436（SID 436）、6 个 openroad；22:12 回到 **629/1207**。恢复之所以快，是 `run_labels.sh` 的 **rc.tsv 断点续跑门**：已完成作业跳过，只有剩余 ~581 个会跑，6 个在飞作业（无 rc.tsv）重跑、不留半成品。

**加固**：**Windows 侧看门狗** `scratch/f2_watchdog.ps1`（每 120 s 用 `f2_watchdog_check.sh` 读 `SUP=/CHAIN=/DONE=/OPENROAD=`，缺哪条链拉哪条，I2 满 1207 自动退出）。**看门狗不能住在 WSL 里**——实例一重启它自己先死。

**纪律修订**：长批次的记录必须把**恢复步骤**（checkpoint 在哪、如何判断已跑过多少、哪些目录是半成品会被重跑）与启动命令**同级**写出；断点续跑按一等公民设计。

**边界**：运行事件记录，无新科学结论；F2 的物理结论仍须等 I2 收齐后由 `finalize_f2_chain.sh` 产出，并按 LOG-20261024-25 的判据解读；`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-CUMULATIVE-READING-20261025

**目的**：查出并修正三点曲线 CUMULATIVE 块的口径缺陷——理想线网那一档的"累计"其实是用
**迭代基线**减出来的**边际量**，与 placed / routed 两档（真·相对电路基线）混用了口径。

**产物**：`experiments/20261024_physical_labels_itc99/three_point_curve.json`、
`experiments/20261024_physical_labels/three_point_curve.json`（两族重跑）、
两族 `training_table.{csv,jsonl}` 与 `training_table_summary.json`（重跑）、
`project_docs/evidence/r30_cumulative_reading_20261025/`（`CUMULATIVE_READING.md` + `cumulative_reading_numbers.json` + `control_pass.json` + harness 副本）

**判决证据**：① ledger 直读（iteration-1 trials 的 `base_netlist_hash` = 电路基线网表哈希；
iteration>=2 的参照值 = 上一轮被接受候选的 `setup_wns`）；② 每电路 `ideal_baseline_wns` 有 2–7 个不同值
且随迭代变化，2218 个可比行里 1630 行匹配迭代基线、
0 行匹配电路基线；③ 用迭代基线重算 `ideal_delta_wns`，
1630 行中 0 行不同。

**物理侧未改**：`routed_cumulative_wns` 逐位 = `post_wns(候选) − post_wns(同 batch BASE)`
（1207/1207）；
`routed_delta_wns` 逐位 = `post_wns(候选) − post_wns(迭代基线)`
（1193/1193）。

**修正结果**：ITC-99 累计 ideal mean -0.046184 → 0.028613、
rho(理想,布线后) 0.515 → 0.8769；
ISCAS89 累计 ideal mean -0.033354 → 0.179815、
rho(理想,布线后) -0.1251 → 0.9461
（原为负相关）。**marginal 块两族 JSON 全等（逐位未变）**；对照遍 114/114 通过。

**边界**：探针级、非论文证据；理想档的电路基线取自 ledger 的 iteration-1 参照值，与物理档的
OpenROAD 实测基线 WNS 不是同一来源；寄生来自 `estimate_parasitics`、非签核 RC 提取；
逐电路方向不一致（b09 / s832 反例），聚合数字不可外推；F2 尚未纳入本条。
`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-THIRD-IMPL-20261025

**目的**：F2（第三个布线实现）批收齐后，按 LOG-20261024-25 **开批前**写死的判据
C1/C2/C3 解读，并回答一个此前没被问过的问题：**"判定带"是不是一个唯一值**。

**产物**：`experiments/20261024_physical_labels_itc99/f2_labels.jsonl`、
`f2_labels_summary.json`、`impl_stability.json` / `impl_stability.txt`、
`project_docs/evidence/r30_f2_third_impl_20261025/`
（`F2_THIRD_IMPL.md` + 产物 JSON + 4 个 harness 副本）

**批次与自检**：1207/1207 完成；标签 1207 条（带边际量 1193，
覆盖率 0.988401，缺的 14 条原因统一为 `no_base_hash_in_ledger`）；
摘要口径自检 字节 41 / 文本 47 / 未匹配 0；
候选自检 1193/1193 通过。

**判决**：三个两两带 F0/F1 **0.049753 ns**、F1/F2 **0.045540 ns**、F0/F2 **0.033706 ns**，
**max/min = 1.476087** → **C1 不成立、C2 成立**（可交换夹具 1.028124、相关夹具 1.718223）；
实现敏感度由**物理轴**驱动（两轴皆差的一对带最大）。**C3 不成立**：均值挑选器
27/92/25（p = 0.8899）→ "跑两个实现取均值降噪"在本族**没有数据支持**。

**对已发布结论的影响：无**。F1/F2 带与 F0/F1 带在 Δ 量化 0.01 ns 下完全等价；
F0/F2 带把 resolvable 434 → 500、gain 48 → 65、harm 386 → 435，
但接受集真实增益 0.250000 → 0.272727、惰性 0.681818 → 0.659091、增益富集 7.5593 → 5.6975、
损害比 0.1944 → 0.1729、`structural` 池内 0.540114 → 0.516203 → **"避害更强、增益有限"与
"图结构无候选级物理信号"在最宽松的带下依然成立**（后者更强）→ 已发布用的 F0/F1 带
是三者中**最大、也就是最保守**的一个。

**边界**：探针级、非论文证据；**族带定义仍是 F0/F1**，另两对是诊断量、不改任何已发布判决；
三个两两差代数相关（`d_F0F2 = d_F0F1 + d_F1F2`）→ 估计不独立，不能做同质性检验；
Δ 量化 0.01 ns；F2 只在 ITC-99 侧；寄生 `estimate_parasitics`、非签核 RCX；
`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-GNN-ADJUDICATION-20261025

**目的**：正面回答 LOG-20261024-24 自己声明的边界——"图特征是标量摘要、不是 GNN 编码器，
所以负结论不能替 GNN 背书"。

**产物**：`experiments/20261024_physical_labels_itc99/graphs/`（1207 图 / 14.12 MB）、
`experiments/20261024_physical_labels/graphs/`（339 图 / 6.33 MB）、
`project_docs/evidence/r30_gnn_adjudication_20261025/`
（`GNN_ADJUDICATION.md` + `gnn_candidate_signal.json` + `gnn_gradient_check.json` + harness 副本）

**方法**：环境无 torch/dgl/sklearn/scipy → **numpy 手写** 2 层消息传递 GNN；**数值梯度校验**
（最大绝对误差 2.784e-11，30 项）先过；评估协议、基线、AUC、池自助代码**全部取自项目自己的工具**，
没有另写一套；留一电路协议。

**结果**（池内 AUC / 池化 AUC）：`kind_only` 0.555062 / 0.538238；`structural` 0.540114 / 0.432507；
GNN 传播+改动单元读出 0.479242 / 0.486678；GNN 全局读出 0.495365 / 0.462452；
**GNN 不传播** 0.523367 / 0.612254；GNN 去单元类型嵌入 0.508663 / 0.507204；
空标签对照 0.454474 / 0.420122；随机初始化编码器探针 0.554609 / 0.388605。

**判决**：**没有任何一档 GNN 在候选级超过平凡基线**；**消息传递没有带来任何好处**
（点估计 0.479242 < 0.523367，差异**未达统计显著**）；**去掉单元类型嵌入后 GNN 归零** →
**GNN 唯一用到的信号是改动单元的类型（≈ kind）** →
LOG-24 的"图结构无候选级物理信号"**在编码器层面被加强**，不再只是标量摘要的结论。

**边界**：探针级、非论文证据；**超参事先固定、未做嵌套选择、无早停** → 不能排除"另有超参下更好"；
样本 1117 行 / 7 个小电路 / 54 池；**只在 ITC-99 做**；"不传播"一档的池化优势是**池间/电路间**的；
单折烟测（0.6531）与完整 7 折（0.479242）的差距提醒：**烟测只证明"跑通了"**；
`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-F2-BAND-SUPPORT-20261025

**目的**：自查 LOG-20261025-28 的 C1/C2 判决是否建立在同一批电路上。

**方法**：用项目自己的 `compute_band()`（导入，不重实现）重算三个两两带；逐候选统计
**布线后 WNS 逐位相同**的配对数；共同非退化子集重算；留一电路 + 以电路集为单位的自助；
**恒等性指纹**（某对恒为 0 ⇒ 另两对的电路内 SD 必相等）；**运行产物字节级与日志行级比对**
（排除"作业没真跑"）。

**结果**：F0/F2 在 **b02 55/55／b08 127/127／b09 92/92／b13 75/75** 上与 F0 逐候选全等（349/1200），F1/F2 在 **b10 216/216** 上与 F1 全等
（216）；**sd_c 恒 0 的电路只进分母不进分子 → 稀释带，三个对稀释量不同**；共同非退化子集只有
b01／b03，其上 max/min = **1.173530**（INCONCLUSIVE），全族口径 1.476087；留一 1.218976–1.758842；
自助 CI95 [1.145302, 3.273719]，仅 0.0051 落到 1.10 以下；恒等指纹 5/5 精确成立。

**判决**：**C1 不成立在所有口径下成立（稳健）**；**C2 撤回**（**撤回 = 数据不再支持它，不是证明了它的反面**：电路集自助 CI95 [1.145302, 3.273719] 跨过 1.35 → 既未被证实也未被证伪）；**"物理轴驱动"的机制归因撤回**
（共同子集上 F1/F2 0.041550 > F0/F1 0.040078 > F0/F2 0.035406）。**族带定义与数值不变**（F0/F1 = 0.049753，
零退化电路），**已发布结论不受影响**。**新发现**：第三个实现**部分退化**——单轴 pin 层变化在
4/7 电路上让 `final.odb` 逐字节相同 → **族带是单轴实现敏感度的上界**。

**证据**：`project_docs/evidence/r30_f2_band_support_20261025/`（`F2_BAND_SUPPORT.md` +
4 个 JSON + 4 个 harness 副本）

**边界**：探针级、非论文证据；Δ 量化 0.01 ns；底板冻结 ⇒ util 轴无效；共同子集只有 2 个电路；
三个两两差代数相关；寄生 `estimate_parasitics`、非签核 RCX；`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-C3-MECHANISM-20261025

**目的**：定论 LOG-20261025-28 的 C3（"用两个实现取均值降噪"）失败的原因，
关闭 OI-052 第 30 条的未决。

**方法**：把 LOG-30 查明的**退化结构**代入留一比较，得到两条可证伪的预测并逐一检验；
再用**配对**遗憾差（符号检验 + Wilcoxon + 以池为单位的自助）替代功效不足的净符号检验；
最后用候选级恒等式 `imp02 = imp01 + imp12` 检验"一度自由度 vs 候选特异多维"这个二分法
本身能否用三个带回答。

**结果**：预测 1/2 各 10 格、**违例 0**；全族配对改进 0.001458 ns（0.145800 量子）、
Wilcoxon p = 0.213500；**真值 = 单实现 picker 的实现 → 平均显著有害**（-0.006250 ns，
Wilcoxon p = 0.000400）；**真值 = 被平均的另一个 → 显著有益**（0.009375 ns，Wilcoxon p = 0.000400）；
三个实现真正互异的 b01／b03 上 **+0.002292 ns（0.229200 量子，Wilcoxon p = 0.305200）→ 无可利用收益**；
恒等式最大偏差 6.939e-18；`r(imp01,imp12)` **被三个方差代数钉死**（不可作独立证据）；
方差比 0.349058（干净子集）→ **两个假设都被否证**。

**判决**：LOG-28 的"C3 不成立"作为显著性判决成立，但**理由改写**：
不是"平均没用"，而是"**平均的收益符号由实现等价结构决定，在本族有时显著有害**"。

**证据**：`project_docs/evidence/r30_axis_structure_20261025/`（`AXIS_STRUCTURE.md` + JSON + harness）

**边界**：探针级、非论文证据；干净子集只有 2 个电路；Wilcoxon 为正态近似；
Δ 量化 0.01 ns；`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-SINGLE-AXIS-BAND-20261025

**目的**：把两个物理轴拆开测，回答"族带（双轴）对单轴敏感度意味着什么"，
并重算已发布判决。

**方法**：用项目自己的 `compute_band()` 在各轴的有效支撑上测单轴带；
用项目自己的 `resolvable_positive_classifier.py` / `acceptance_physical_selectivity.py`
（复用 LOG-28 的敏感性工具）重算标签数、分类器 AUC、接受判据选择性；
并检验一个结构性断言——布线后 WNS 量化到 0.01 ns，故标签集合只由 `floor(band/0.01)+1` 决定，
**同一格内的带必须给出逐位相同的数字**。

**结果**：竖轴 0.039884 ns、横轴 0.050272 ns、全族双轴 0.049753 ns；同口径（b01／b03）上
**双轴 0.040078 < 横轴 0.041550** → "同时改两轴"不比"只改主导轴"更具破坏性；
**六个带变体只落进三个标签集合，同格内数字逐位相同（违例 0）**；
**已发布结论无一翻转**（`structural` 池化 0.445175／0.432507／0.426741 全远低于 0.5，且在池化与
池内两种读法下都低于同格 `kind_only`；接受集增益率 0.272727／0.250000／0.250000、损害比 0.172900／0.194400／0.141900 形状不变）；
**口径提醒**：证据包的 `flip_table_vs_published[].flips` 标的是"**数字动了**"（逐行极性不同，
接受判据四行的极性朝判决更有利），
**`flips=true` ≠ "判决被推翻"**；
**方法学结论**：判决是阈值的阶梯函数，报告判定带必须同时报它落在量子网格的哪一格。

**证据**：`project_docs/evidence/r30_axis_structure_20261025/`

**边界**：探针级、非论文证据；单轴带与双轴带不在同一批电路上（同口径只有 2 个电路）；
Δ 量化 0.01 ns；`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-GNN-CROSS-FAMILY-20261025

**目的**：把 LOG-20261025-29 的 GNN 负面判决放到**第二个族**与**嵌套超参选择**之下复核，
并补一个此前从未测过的对照：**理想线网 / 布局后 Δ 当预测器**（候选级信号的上限参照）。

**方法**：复用项目自有工具 `gnn_candidate_signal.py`（**一行未改**）与评价内核
（`resolvable_positive_classifier.py` 的 loader / 基线 / AUC / 逐池配对检验）；
新增三个工具：oracle 上限对照、拓扑信息极限检验（连续目标 + 池内 Pearson/Spearman）、
嵌套超参选择（外层留一电路 / 内层只在训练电路上留一 / 内层分数 = 池内 AUC，
外层测试电路进入内层会被 `assert` 拦下）。
**判据在跑之前写死**：`scratch/round32_preregistration.json`；
匹配对照与机制诊断的判据另写 `scratch/round32_preregistration_addendum_A.json`。

**结果**：
- **oracle 上限**：候选级的物理信号**很大** —— 池内 AUC ITC-99 理想 0.875733 /
  布局后 0.907572，ISCAS89 理想 0.852203 / 布局后 0.927566；
  对 kind_only 的逐池配对 p = 4.177e-07 / 1.233e-07 / 1.312e-03 / 1.526e-05。
  → **"图结构无候选级物理信号"只对拓扑成立，对候选级可学性不成立。**
- **信息极限（连续目标）**：布线后边际 Δ 的池内 Pearson，拓扑标量摘要与 GNN 编码器
  仍在 0.1 量级，oracle 在 0.63–0.90。
- **跨族复现**：ISCAS89 四个变体池内 0.555103 / 0.653625 /
  0.547595 / 0.561199；ITC-99 对照遍**逐位复现** LOG-29（26 项精确浮点相等）。
- **口径纠错（关键）**：工具的 C2/C4 对照跑的是 `readout=mod`，而被检验的是
  `readout=global` → 补跑**架构匹配**的对照：C2-global 0.503974、C4-global 0.565744
  （阈值 0.53 未改）。按工具实际实现的口径（对照为 mod）H1 **未触发**，按匹配口径（对照为 global）H1 **未触发**。
- **机制诊断 D1–D7**：**标签置换零分布**（B = 2000，固定预测向量、池内置换标签，零分布自动吸收池大小、正例数与并列结构）把两者分开：`gnn_global` 观测 **0.653625**，零分布均值 0.501169、SD 0.061147、97.5% 分位 0.621007，**经验 p = 1.199e-02（超出随机）**；`kind_only` 观测 0.517298，**经验 p = 4.273e-01（不超出随机）**；配对差经验 p = 3.398e-02

**判决**：**结论必须分层改述**：**(a)** "图结构无候选级物理信号"这句**只对拓扑描述成立**，对"候选级可学性"**不成立**——候选级的物理信号很大（oracle 池内 AUC 0.85–0.93，两族一致），它**不在拓扑里，而在网表派生的"测量"里**（理想 / 布局后 Δ）；**(b)** LOG-29 的负面判决在 **ITC-99 逐位复现**（`gnn_global` 池内 0.495365）；**(c)** 但在 **ISCAS89** 上，`global` 读出**确实带出了候选级信号**（池内 0.653625，逐池配对 p = 4.904175e-02，**标签置换经验 p = 1.199e-02**；（留一池 / 留一电路**均不变号**）→ **族特异**，且**信号很薄**：D5 显示 global 读出的池内分数标准差只有 7.706e-03（kind_only 3.921e-02），**3 个池完全退化**（分数恒定 → 并列打破后 AUC 恒 0.5），18 个可用池里实际有效的只有 15 个；D7 在正负例都 ≥ 3 的 8 个池上 mean_diff 缩到 0.087092、p = 7.031e-02（**同向但不显著**）→ **族特异 + 样本薄**，机制尚未钉住。**因此 H1 四条件在两种口径下都未触发，**但**这不是"信号被否证"**——是因为**条件 4 这个门量错了东西**：C4 随机初始化探针在**真实标签上训练**，它不是"随机"对照——只要随机特征带任何标签相关信息（本族是"规模→扰动幅度"，见 LOG-20261024-24），它就会高于 0.5；实测它在 mod / global 两种读出下分别是 **0.531432** / **0.565744**，**都高于平凡基线 0.517298** → **"对照 < 0.53"这个门对带信息的架构不可满足**。本条把该门登记为**判据缺陷**（OI-052 第 39 条），**不据此改门、不据此宣称否证**。

**证据**：`project_docs/evidence/r30_gnn_cross_family_20261025/`

**边界**：探针级、非论文证据；ISCAS89 仅 8 个极小电路 / 325 行 /
18 个可用于配对检验的池 → 功效有限，可证伪、不能确立；
寄生来自 `estimate_parasitics` 非签核 RCX；Δ 为边际量（LOG-27 口径）；
组件 F 的 ITC-99 嵌套批因算力预算未跑完（OI-052 第 38 条）；
`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-PLACED-SELECTOR-20261025

**目的**：把 ECO 循环的接受判据从"理想线网边际 Δ"换成"布局后边际 Δ"（比布线后
便宜约两个数量级），在**决策级**（不是候选级）量一次"能挽回多少物理收益"。

**方法**：新增两个工具——决策级反事实（`scratch/round33_placed_selector.py`）
与机制诊断（`scratch/round33_mechanism.py`）；复用项目评价内核
（`resolvable_positive_classifier.py` 的 `sign_test_p`）。
**判据在跑之前写死**：`scratch/round33_preregistration.json`；
发现预注册的符号定义有误后**原文件保持原样**，更正另立有独立证据的附记
`scratch/round33_preregistration_correction_01.json`（阈值、判据、池定义一律未改）。
选择器只在**循环真实用过的失效门合格集合**内挑选。

**结果**：
- **H1 两族均未触发**：ISCAS89 1/2/11、p = 1.000000、挽回 0.055556；
  ITC-99 8/5/14、p = 0.581055、挽回 0.073171。
- **D3b 正向对照**：随机合格候选 vs 布线后 oracle，两族 100.0% / 100.0%
  的种子 p < 0.05 → **尺子有分辨率**。
- **D6**：oracle 显著优于理想判据（7/0 p = 0.015625；
  20/0 p = 1.907349e-06）→ **奖池存在**，但每决策只有 0.012857 / 0.015185 ns。
- **D3**：随机合格候选 vs 理想判据，ITC-99 只有 6.5% 的种子显著
  → **理想判据在决策层面本就在机会水平附近**。
- **D7**：池内排序器质量（Spearman 与布线后 Δ）ITC-99 placed 0.644043 vs
  ideal 0.399218，配对 9/1、p = 0.021484 → **布局后档是显著更好的
  物理排序器**，但决策级收益未出现。

**判决**：**两族 H1 均未触发**（ISCAS89 1/2/11，p = 1.000000，挽回 0.055556；ITC-99 8/5/14，p = 0.581055，挽回 0.073171）→ **"把接受判据从理想线网搬到布局后档"在决策层面没有拿到可检验的收益**。**但这不等于"布局后档更差"**：正向对照 D3b 显示这把尺子**有分辨率**（随机合格候选 vs 布线后 oracle，两族都是 100.0% 的种子 p < 0.05）；D6 显示**奖池确实存在**（oracle 显著优于理想判据：ISCAS89 7/0 p = 0.015625、ITC-99 20/0 p = 1.907349e-06）；D3 显示**理想判据在 ITC-99 上本就在机会水平附近**（只有 6.5% 的随机对照种子能显著优于随机合格候选）；D7 显示布局后 Δ 是**显著更好的池内排序器**（ITC-99：Spearman 与布线后 Δ 0.644043 vs 0.399218，配对 9/1，p = 0.021484）→ **真正缺的不是"换哪一档"，而是"决策级有分辨力的判据"，以及一个足以让这种差别显形的大得多的决策级奖池。**

**证据**：`project_docs/evidence/r30_placed_selector_20261025/`

**边界**：探针级、非论文证据；寄生来自 `estimate_parasitics` 非签核 RCX；
Δ 为边际量（LOG-27 口径）；布局后与布线后寄生模型不同；
反事实只覆盖"已生成且已标注"的候选；可评估决策数 14 / 27；
D7 的配对检验只在 Spearman 有定义的决策上做（8 / 13 个）；
`code/` 未动、HEAD 未变、未提交。
| PHYS-DATASET-LABEL-STATUS-20261025 | **理想档"未测量"与"等于零"的分家 + 数据链静默丢标签的修复与证伪** | 2026-10-25 | 第 34 轮 | **问题**：候选级物理标签族在 ledger → 数据集 → 训练表的链上静默丢候选（ITC-99 决策级覆盖 96/143 轮次缺标注池，根因是 12 个电路从未标注 + 链上丢标签）。**做法**：① 覆盖度调查（把缺口定位到电路范围而非键匹配）；② 独立穷尽验证回退等价性；③ **证伪第一版补丁**（ledger 的 `trial.wns` 是基线占位符而非测量）；④ 诚实修复（理想档留空 + `ideal_label_status` + 曲线不再丢弃有真实物理档的候选 + drop 普查）；⑤ 基线 vs 修复版逐行 diff（0 冲突 / 76 行填充 / 理想档 n 不变 / 带与判决逐位相同）；⑥ 两族原链重跑并报出全部级联变动（ISCAS89 0/23，ITC-99 8 个）；⑦ 12 个新电路可达性探针（判据跑前写死）。**结果**：ITC-99 训练表 0 冲突、76 行由空变有，ideal_label_status measured 2322 / not_measured_pre_sta 208；决策级判决不变（ITC-99 27 决策、p = 0.581055、H1 = False）；附带查实 `band_scope.json` 一个跨口径陈旧比值。**边界**：探针级、非论文证据；寄生来自 `estimate_parasitics` 非签核 RCX；placed 与 routed 档寄生模型不同；扩面成本按实测基线跑成本外推 | `project_docs/evidence/r30_dataset_label_status_20261025/` | LOG-20261025-35 / OI-053 / OI-054 / 教训㉔-㉗ |

### 2026-10-25 PHYS-RECORD-HARDENING-20261025

**目的**：收尾加固——修掉 F2 看门狗的读数缺陷、把 LOG-28/30/31/32 引用的数字逐项回读、纠正一处过期标题与一条过度概括。

**方法**：根因定位（`pgrep -c` 有输出但非零退出 → `|| echo` 追加第二行 → 读数方按位置取最后一行）→ 三处修复 → 用**从真实脚本抽出的解析块**跑三态测试；对四条 F2 LOG 行做数字级回读核对（数字必须在该行里出现）；OI-052 第 20 条的标题按证据包收据改写。

**结果**：三态测试 2 用例 0 失败；数字回读 76 项检查 0 失败（唯一真实缺陷是裸 p 值，已补检验名）；OI-052 容器状态如实写为 open；另修掉折叠脚本的块替换缺陷（从标记截到末尾 → 原地替换，四个文件回环逐字节复现），并把"超时即判据时并发即污染"写进批次的依赖顺序。

**边界**：记录与运行可靠性条目，无新科学结论，不改任何已发布判决；探针级、非论文证据；`code/` 未动、HEAD 未变、未提交；论文未动。


### 2026-10-25 D-MATRIX-56-ACCEPTED-20261025

**目的**：把 D 正式矩阵的**完成性审查**从 28 键扩到全部 56 键，并把八个电路的 raw 原件包全部归档、逐 SHA 后验验收。

**方法**：① 根审计只读回放（56/56，68.1 s）；② 用**与 28 键那批同一个、且一行未改**的 checker（SHA f6b053dfa655）做全量独立原件审查（613.6 s / 32709 份原件）；③ 根接受收据的计数与根审计独立重算逐项比对后才签；④ 八个 case 用**逐位相同的归档器**归档，再由根脚本独立重哈希并解包逐 SHA 比对。

**结果**：`full_56_registered_keys_reviewed = True`、`full56_accepted = true`、8/8 raw 包根后验通过（合计 44519 份源件 / 8 个分卷）。

**边界**：**只**覆盖完成性审查与原件自证，**不是**签核 RC 物理闭环、**不是**四态支持、**不是**全局科学结论；四 partial、OI-051 等既有未决未动；`code/` 未动、HEAD 未变、未提交；论文未动。

### 2026-10-25 PHYS-EXT-POOL-RECLASS-20261025

**目的**：把 ITC-99 物理标签的**扩面池定义写死**，并用档案证据**重分类第 34 轮探针的可达性判定**。

**方法**：① 回读 2026-08-21 档案的串行运行日志（`log/master.log`），用**独立证据**仲裁"探针的 rc=124 是不是物理上限"；② 回读标签族为已发布 7 电路生成的作业表，**证明既有标注池是全量 distinct 候选**（1193 个哈希与台账逐电路相等）；③ 据此把预注册的池口径从"合格池"改为"**全量池为主、合格池为对照**"，并补上"合格判定落在首次出现的 trial 上"这一条；④ 用串行秒数重算成本，用三态测试验证脱离链的等待逻辑。

**结果**：b05 由"不可达"改判为**真可达**（串行 838 s，rc=0，有 final.odb）；b14 改判为**未证实**；b15/b17/b20/b21/b22 维持**真物理上限**；主池 1393 作业/档、对照池 389 作业/档，两张表 **3636 项核验 0 失败**；扩面批已挂（等第 32 轮嵌套批结束后自动开跑）。

**边界**：**只**记录可达性重分类、池口径修正与批的启动；**扩面结果尚未产生**；历史记录与 probe_result.json 未改动；`code/` 未动、HEAD 未变、未提交；论文未动。

### 2026-10-25 PHYS-EXT-BATCH-V2-20261025

**目的**：在 ITC-99 物理标签扩面批**开跑之前**，把批脚本从 v1 修订到 v2，并核实扩面池与既有已标作业不重叠。

**方法**：① 回读标签族自身的启动脚本与既有批目录，核对各批的 TCL、时限与并行度；② 回读既有五批的 rc.tsv 与扩面作业表，**求作业键交集**并逐电路回读键的来源；③ 写失败项工具与合成批自检，验证"列出/计数/改名重跑"三件事；④ 按精确 PID 停 v1 launcher、挂 v2 launcher。

**结果**：v1 的三处缺陷被拦下（无试点门、无修复段、布局后档时限 1800 收紧了已发布的 3600）；扩面池 1393 作业与既有 1207 作业**键交集 0**（电路不同：既有 b01、b02、b03、b08、b09、b10、b13 vs 扩面 b04、b05、b06、b07、b11、b12）；试点表 58 作业覆盖全部 6 电路；挂批前自检 17 项全过、失败 0 项；v2 launcher 已挂（仍在等第 32 轮嵌套批结束）。

**边界**：**扩面结果尚未产生**，本条不含任何扩面后的读数；v1 脚本与 LOG-20261025-38 记录保留不改；`code/` 未动、HEAD 未变、未提交；论文未动。

### 2026-10-25 PHYS-RECORD-LINEENDINGS-20261025

**目的**：查清并修回四个记录文件的行尾，同时定位"OPEN_ISSUES.md 被整篇改写"这一历史缺陷。

**方法**：① 用 scratch/ 里的历史备份画出 OI 的行尾时间线，定位变更点；② 回读落地脚本找到根因（`Path.write_text()` 未传 `newline=`）；③ 写修复脚本，按 house rule 归一行尾，并用"CRLF→LF 规范化后逐字节相同"自证内容零改动；④ 修正三个落地脚本的 OI 写法；⑤ 给常驻同步门加行尾检查。

**结果**：变更点定位在 **LOG-20261025-37 的落地**；OI 的 898 处 CRLF 转回 LF，另外三个文件的 107 处孤立 LF 转成 CRLF；内容零改动证明不符 0 处；三个落地脚本已修正；同步门新增行尾检查。

**边界**：只改行尾、不改内容；`code/` 未动、HEAD 未变、未提交；论文未动；扩面批结果尚未产生。

### 2026-10-25 PHYS-EXT-PAR-INVARIANCE-20261025

**目的**：实测“提高并行度”是否会改变扩面批的标签口径。

**方法**：基族两对"同网表、同 TCL、同实现"的批对照（I0↔I0P0、I1↔I1P0，每对 58 键）：从 `pr_run.log` 解析 worst slack 与 TNS，逐键比较两批的标签，并计算墙钟比；同时比较两批 `pr_run.log` 的 SHA256。

**结果**：I0↔I0P0 与 I1↔I1P0 的标签均 **116/116 逐位相同、0 条不同**；墙钟比 I0↔I0P0 中位 1.226、均值 1.363、最小 0.944、最大 2.636，I1↔I1P0 中位 1.222、均值 1.338、最小 0.781、最大 2.5；两批的 `pr_run.log` SHA256 有 116/116 都不同。

**边界**：并发度是**机器时间旋钮**，不是标签口径旋钮；标签口径不随并发度漂移。探针级、不作论文证据；`code/` 未动、HEAD 未变、未提交。


### 2026-10-25 PHYS-EXT-CONTROL-REPLICATE-20261025

**目的**：确认扩面对照池（`jobs_itc99_ext_t1.tsv`，389 作业）是否携带新物理信息。

**方法**：把对照池的 389 个键与主池同名键逐字段比较（17 个字段：netlist、top、util、realisation、core_space、pin_hor、pin_ver、sig_layers、clk_layers、die_area、core_area、circuit、kind、candidate_hash、trial_index、iteration、accepted）；比较 realisation 取值与主池网表路径的唯一性；比对试点段与全量段的子集关系。

**结果**：17 个字段全部 **0 条差异**；realisation 全部为 **F0**；主池 1393 个键引用 1393 个互不相同的网表路径；试点段 58 键是全量段的子集且输入完全相同（netlist 差异 0 条、realisation 差异 0 条）。

**边界**：对照池 = 同网表同实现的**可复现性对照**，不携带新物理信息；试点段已免费提供 58 对复现对照。探针级、不作论文证据；`code/` 未动、HEAD 未变、未提交。


### 2026-10-25 PHYS-EXT-BUDGET-REBASELINE-20261025

**目的**：把扩面批的成本预算从"档案秒数外推"改为"实测 + 每电路剖面"。

**方法**：读 `scratch/ext_budget_v2.json`（试点实测、墙钟预测、磁盘）与 `scratch/base_family_timing_profile.json`（基族每电路的 I0 / IPLACED 秒数与档案比值）；用 `scratch/ext_budget_calibration.md` 取磁盘与 D 盘余量；按试点实测均值与 PAR=2 直算各段墙钟。

**结果**：试点实测（`round35_pilot`，PAR=2，TIMEOUT=1800）：完成 12 个作业，rc 分布 **rc=0: 10、rc=124: 2**（b05 的 2 个作业被 1800 s 上限杀掉）；10 个 rc=0 作业的均值 **663.7 s/作业**（中位 719 s）；b04 候选 8 个作业 478–914 s、均值 **713.5 s**，`base__b04` 469 s、`final__b04` 460 s。原估 "180.8 s/作业"不可外推（档案秒数 ÷ 基族秒数的比值在 b01 0.464、b02 1.62、b03 5.508、b08 1.684、b09 3.832、b10 2.832、b13 3.541 之间散开）；"布局后 = 布线的 60%" 实测为 ≈ 0.25（b01 0.146、b02 0.358、b03 0.22、b08 0.234、b09 0.305、b10 0.196、b13 0.289）。按实测均值 + PAR=2 直算：主池布线后 128.41 h、主池布局后 128.41 h（未实测，按布线同值算的上界）、对照池 35.86 h、试点 5.35 h，合计 **298.02 h ≈ 12.42 天**。磁盘：每作业 31.4 MB，全批 3233 作业 ≈ 101.5 GB，D 盘余 202 GB。

**边界**：**298.02 h 是上界**，且以试点单电路样本外推，必须在试点段跑完 58 个作业后重算并记录偏差。成本与磁盘条目，不含科学结论；扩面结果尚未产生；`code/` 未动、HEAD 未变、未提交；论文未动。

### 2026-10-25 PHYS-EXT-LITE-TCL-SWITCH-20261025

**目的**：b05 在 full TCL 下 4/4 作业 rc=124（1751 / 1751 / 1756 / 1757 s、日志 110–128 MB），死因在 `report_checks` 的报告阶段；把报告端点从 100000 封顶到 1000（`pr_label_lite.tcl` / `pr_placed_lite.tcl`）后，同参数下 10/10 rc=0（92–186 s，均值 128.9 s，日志约 1.65 MB）。

**方法**：用**三重证明**论证"封顶报告不改变标签"，缺一不可——（a）**结构证明**：lite 与 full 的**非注释代码行**逐行只差一行（`report_checks ... -endpoint_count 100000` → `1000`），`pr_label.tcl` **54/54** 行、`pr_placed.tcl` **52/52** 行行数相同、逐行对齐（产物 `scratch/prove_lite_tcl_codelines.py`）；（b）**标签源证明**：解析器只取**两行 `worst slack`** + **TNS_BEGIN/TNS_END 块内的 `tns`**，成功日志里 `worst slack` 全文**恰好 2 次**且**都在 TNS_BEGIN 之后**（产物 `scratch/probe_parser_label_source.py`）；（c）**经验证明**：族外 `base__b02` 与**族内 `base__b04`** 两点实测，标签的**解析值与打印串都逐位相同、0 差异**（产物 `scratch/check_lite_tcl_identity.sh`、`scratch/ext_lite_check/`、`scratch/ext_b05_lite_preflight/preflight_b05_lite.json`）。

**结果**：full TCL 下 b05 的 4 个试点作业全部 **rc=124**（1751 / 1751 / 1756 / 1757 s），日志 110–128 MB、在报告路径中途被硬截断；换 lite TCL 后**试点同参数**（PAR=2 / 上限 1800 s）下 b05 的 **10/10 作业 rc=0**、秒数 **92–186**（均值 **128.9 s**）、日志约 **1.65 MB**、10 个标签全部可解析——**被换法救回的正是那条杀人的电路**。

**边界**：`report_checks` 的端点数只影响**打印多少条路径**，不影响标签定义；**b05 在 lite 下是否还有别的上限未单独证伪**——只是 10/10 跑通、**没有观测到**上限命中，**不得**写成"证明没有上限"。探针级、非论文证据；扩面批结果尚未产生，本条不含任何扩面后的读数；`code/` 未动、HEAD 未变、未提交；论文未动。


### 2026-10-25 PHYS-EXT-GATE-DUAL-SUBJECT-20261025

**目的**：段 0 标签等价闸门原先只有族外 `base__b02` 一个被验对象，等于**用族外证据护族内 3 天批**，不可接受。

**方法**：闸门新增族内 `base__b04` 作为**第二个被验对象**；并发保护补上 `openroad -exit` 进程检测，并改为"**先等 300 s 再拒绝**"（看门狗只在批与 openroad **都**为 0 时才重启，故不会活锁）；看门狗改为**在闸门通过之后才启动**，避免闸门失败时变成每 INTERVAL 秒重跑一次的无限失败循环（产物 `scratch/run_ext_batch_v3.sh`、`scratch/launch_ext_batch_v3.sh`、`scratch/ext_watchdog_v3.sh`）。

**结果**：v3 批 13:42:41 启动，13:44:16 闸门现场**双对象通过**（`base__b02`：wns -0.31 / 0.47 / tns -0.95；`base__b04`：wns -2.76 / 0.45 / tns -143.14；两侧 `parsed_differences` 与 `printed_differences` 均为空），13:44:18 看门狗启动（`scratch/ext_batch_v3.log`、`scratch/ext_launch_v3.log`）。

**边界**：闸门只证明**标签**等价，不证明**日志正文**等价——正文会变（端点数不同），那不是标签。探针级、非论文证据；扩面批结果尚未产生，本条不含任何扩面后的读数；`code/` 未动、HEAD 未变、未提交；论文未动。


### 2026-10-25 PHYS-EXT-GUARD-PARTIAL-DATA-20261025

**目的**：预注册要求"部分完成度绝不出科学读数"，需在**批跑完前**用真实数据证明这条性质——跑完后就不可复现了。

**方法**：在批运行中（试点 35/58、主池 0/1393）实测 `scratch/post_ext_guard.py`，两种模式各跑一次，输出隔离到 `scratch/probe_guard_partial/`；并核对 `experiments/20261025_physical_labels_itc99_ext/decision_readings.{json,txt}` 是否存在。

**结果**：**两种模式都 exit code 2**。v3 模式 `blocked_batches = 3`（pilot / ext_full / ext_full_placed），pilot 分类 ok=31、`concurrency_artefact_recovered`=4（正是 b05 那 4 个被 lite 重跑救回的 rc=124）、missing=23；主池与布局后档各 missing=1393。default 模式额外 blocked 对照池 round35_ext_t1（missing=389）。**`decision_readings.json` 与 `decision_readings.txt` 均不存在** → 链停在第 1 步，**未产出任何决策级读数**。**附带发现（属可用性问题）**：`post_ext_chain.sh` 的默认 `--guard-batches default` 会要求对照池 389 键的回执，而 D1 已决定对照池不跑 → **默认跑法必然卡死在第 1 步**；批跑完必须显式传 `--guard-batches v3`。

**边界**：完整性门读的是回执快照，批运行中随时在变，上述数字是 14:1x 的**时点值**、不是终值；探针级、非论文证据；扩面批结果尚未产生，本条不含任何扩面后的读数；`code/` 未动、HEAD 未变、未提交；论文未动。


### 2026-10-25 PHYS-EXT-ACCEPT-INSTRUMENT-FIX-20261025

**目的**：第 38 轮把 17 条假绿路径判为已修复，并"经主线自己的验收复核"；本轮先**证伪那个验收仪器本身**——在把任何"已修复"当结论之前，必须确认验收用的尺子不是坏的。

**方法**：读 `scratch/accept_falsgreen.py` 的调用链并在**两个解释器**下各跑一遍相关脚本（WSL `python3` 与仓库 `.venv/Scripts/python.exe`）；把 harness 的路径传递改为与链同源的 `wslpath -m`；把判定式由 `rc != 0` 收紧为「输入必须真实存在 + 具体期望退出码 + 工具必须出声 + stderr 不得含 traceback + 拒绝理由不得是"文件不存在"」，并把「工具错误」与「语义判决」分开（工具错误重试一次后仍记红并标注）。独立诊断件：`scratch/diag_winpy_paths.sh`、`scratch/diag_refusal_codes.py`、`scratch/repro_d3.py`、`scratch/probe_prereg_expect_pairs.py`。

**结果**：**根因 A（成组假绿）**：harness 的 `w()` 把 WSL 路径直喂 Windows venv python → 解析成 `D:\mnt\d\...` → 工具在"找不到输入"处退出，而 `rc != 0` 无法区分「门正确拒绝 / 找不到输入 / 工具崩溃」→ 上一轮 A/B/C 整组断言实际测的是路径；**物证**：那轮验收在**工作区外**建出 `D:\mnt\d\...\scratch\...`（29 目录 / 20 文件），连自己的产物都没落在工作区。**根因 B（假红）**：`scratch/selfcheck_sync_gate_line_range.py` 是同批脚本里唯一把仓库根写死成 `/mnt/d/...` 的 → Windows python 下模块级异常 → rc=1、stdout 空 → 被记成"反向对照失败（-1 failed）"；复现：WSL python3 → `RESULT: 11 passed, 0 failed`（exit 0），同一台机器的 `.venv/Scripts/python.exe` → traceback、stdout 0 字节、exit 1。**修正后的真值**：决策读数工具的覆盖率门退出码是 **8**（不是上一轮记的 7）；拒绝理由经核对为真的覆盖率门（`1393 of the 1393 planned key(s) are MISSING`、`circuit b04 has a delta coverage of 0/265`）。**主线验收最终 21/21 全绿**（A 4/4、B 4/4、C 2/2、D 3/3、E 3/3、F 5/5）；`--expect-pairs` 契约的独立对照 **7/7**（默认路径仍拒绝声称 6 对的读数、理由点名 58；显式 6 才放行且必须带 `expect_pairs=6` + `synthetic_expect_pairs=true` + 文本合成标记；`--expect-pairs 58` 与默认逐项等价）。

**边界**：本条全部属**工具/验收层**，**非论文证据**；不含任何扩面后的科学读数（扩面批主池仍在跑）。`code/` 未动、HEAD 未变、未提交；论文未动。工作区外那棵 `D:\mnt\d\...` 产物树**尚未清理**（可回撤删除被 runtime 以"dangerous removal target"拦下），根因已修、不会再新增。

### 2026-10-25 PHYS-EXT-DRILL-CONTRACT-ADAPT-20261025

**目的**：链的契约在第 38 轮变更（新增第 0 步作业表 SHA256 校验 + 期望对数硬钉 58）后，两个**合成演练**在第 0 步 exit 8 → 链失去了自己的端到端回归；本轮把演练适配到现行契约，并确认"过期的是 fixture、不是链"。

**方法**：链新增 `--prereg` 通路（第 6 步同时下传 `--prereg` 与 `--expect-pairs`，两个期望对数不再可能分叉）；预注册核对新增 `--expect-pairs`（默认 58，默认路径**逐项等价**；非 58 时输出必须带合成标记）；演练 fixture 自备 `jobs/JOB_TABLES.sha256`（真实格式、CRLF）与自己的合成预注册 JSON，断言一律收紧为"具体退出码 + 拒绝理由"。主线**独立复跑**（不依赖子任务套件）两个演练，并在两个解释器下各跑一次。

**结果**：**两个演练全绿**（v1 `DRILL PASSED`、v2 `DRILL v2 PASSED`；Windows venv python 下 v2 亦 PASS）。**适配过程中挖出同一根因的复发**：ledger 的 `base_netlist_hash` 是**文本模式摘要**、job 表 `candidate_hash` 是**字节摘要**，演练 fixture 只注册字节摘要 → 迭代基线链断裂 → 2/27 行缺边际 delta → **覆盖门以 exit 8 正确拒收**（门对、fixture 错）——这正是第 38 轮在真实族修过的同一个 bug（LOG-20261025-22），**修真实数据不等于修测试资产**。**h4 套件**：原 62 条中 2 条因**批推进**而过期（硬编码了 live 失败"0 对可比"的旧形态；实测形态已是"5 对可比 / 53 对缺"，缺的是主池侧），改为**按性质判定**（点名预注册的 58 + 守恒式 `compared + missing == 58`）后 **63/63 全绿**；被测性质（live 必须被拒）始终成立。**顺带纠正子任务报告的一处事实错误**：h4 套件**失败时确实 exit 1**（三套件实测一致），"失败也 exit 0" 不成立；但仍给验收 E 组加了**失败数解析**作为双保险。

**边界**：本条全部属**工具/回归层**，**非论文证据**；不含任何扩面后的科学读数。演练会覆盖 `scratch/ext_summary.{txt,json}`（清点工具的既有副作用），真实族对应产物未受影响（演练自带的"发布族必须逐字节不变"断言每次都过）。`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 PHYS-EXT-CONTROL-POOL-RULING-AND-HANDOVER-20261025

**目的**：扩面族只有一个布线实现 F0，候选级判定带需要**族内**的复现性底噪，而其唯一产地（对照池 389 键）被 D1 以「纯复现」关掉；OI-058 因此挂着三个待选项。项目负责人本轮**拍板**，并要求把"批跑完后要跑对照池段"这件事从"靠人记得"变成"自动接续"。

**方法**：拍板选 **② 开全对照池 389 键**（+17.53 h；不做分层抽样、不走跨族继承），实现路径 = 批脚本**已内置**的 `--with-control-replicate`（段 8 → `runs/round35_ext_t1`，389 作业），看门狗**已内置** `EXT_WD_WITH_CONTROL_REPLICATE=1` 的认识。缺的只是**交接**，故新写两个常驻触发器（运行中的 bash 脚本不可就地编辑，批脚本与看门狗本身**一个字节都没改**）：① `scratch/ext_control_pool_trigger.sh`（5,029 B，PID 126442，armed）——等三段收齐（试点 58 / 主池 1393 / 布局后 1393）→ 等批退出 → **按精确 PID 停旧看门狗**（留着它会以旧命令行重启批，段 8 永远到不了）→ 等机器空闲（并发 EDA 污染墙钟读数）→ 以 `--with-control-replicate` 重启批 → 段 1-7 由每键一目录的 resume 语义跳过、只跑段 8 → 起认识 389 键的新看门狗；② `scratch/ext_infamily_band_trigger.sh`（3,408 B，PID 127792，armed）——等 389 回执 → 等批退出 → 跑 H4 复现门 → 跑族内带工具。**两个触发器自身都不跑任何 EDA**，等待循环都带幂等保护。

**结果**：两个触发器**实测存活**（`ps` 实查 PID 126442 / 127792，日志均为 "armed"）。批状态：批 PID 478 / 看门狗 PID 696；试点段 **58/58 完成**（15:47:48 rc=0）；段 3 的 PAR/上限判定已更新、分组表已重新派生（`control_fast` 389 + `rest_fast` 1004 = 1393，`control_slow`/`rest_slow` 为空）；主池在跑（20:14 时 `round35_ext_full` **234/1393**、布局后 0/1393）；段 0 的标签等价性闸门现场通过。**连带更正**：`scratch/post_ext_chain.sh` 的默认 `--guard-batches default`（`post_ext_guard.py` 的 `DEFAULT_BATCHES` 含 `round35_ext_t1` 389）此前因 D1 关掉对照池而**必然卡死在第 1 步**；选 ② 之后该 389 回执**将被跑出来**，故该阻塞**不再成立**（主池/布局后两段的齐全要求不变）。

**边界**：本条属**决策与工具层**，**非论文证据**；**对照池段尚未跑**，族内带数字**尚未产生** → 本条不含任何扩面后的科学读数。触发器是后台进程、**无守护**，被杀则需人工接手。`code/` 未动、HEAD 未变、未提交；论文未动；`data/cases/**/results/` 归一化按拍板**保持现状**（生成器在 `code/src/rseco/` 内，受跟踪文件当前 0 脏）。

### 2026-10-25 PHYS-EXT-INFAMILY-BAND-TOOL-20261025

**目的**：族内带（"同网表同实现重跑有没有运行噪声成分"）此前在本族**没有产地**，只有基族的跨族继承。本轮把测量工具与**判据**在数据产出**之前**写死，避免"看到数再定标准"。

**方法**：**复用**既有的 `scratch/post_ext_replicate.py`（`--pilot-batch/--pilot-table/--main-batch/--main-table/--expect-pairs`）做比较——pilot 侧指向控制池、main 侧指向主池，389 对全是"同一网表 / 同一实现 F0 / 同一 realisation 跑两次"；**新写的 `scratch/ext_infamily_band.py`（11,036 B）只做"产物 → 带 + 判决"，一个门都不改**。判据（写死）：期望 389 对硬钉、0 对可比即失败、**主判据 = 389 对全部逐位相同 → 族内底噪 0.000000 ns**、判决 `DETERMINISTIC`；任一对不同 → **不出带**、逐对点名 key/pilot/main/解析差并要求"**下游判决全部重算**"；值相等但打印串不同也算不同；孤儿键拒绝；**缺输入 = FATAL（exit 3）而非判决**（沿用第 39 轮根因 A 的教训：工具错误与语义判决必须分开）。套件：`scratch/infamily_band_tests/{mkfix.py,run_tests.sh}`，6 场景 20 条断言。

**结果**：套件 **20/20 全绿**（本轮**复跑确认**，非引述）：全同→出带 0.000000 ns 且判 `DETERMINISTIC`；一对不同→不出带且**点名数量与 key**、明说下游须重算；值同但打印串不同→不出带；可比对数不足→不出带且点名期望数；0 对可比→不出带且点名"空过"；孤儿键→不出带且点名；缺输入→exit 3 且点名缺哪个文件。**口径边界**：**族内带 ≠ 候选级判定带**——后者是**跨实现**的 F0/F1 = 0.049752 ns（LOG-20261024-24 已发布口径）。族内带的既有依据是 LOG-20261024-20 ④（F0 58 对 / F1 8 对同实现重跑非零差均为 **0**）。

**边界**：本条属**工具/判据层**，**非论文证据**；**族内带数字尚未产生**（对照池段未跑）→ **不出带、不出判决**。若族内出现非零差 → **不出带**、下游判决全部重算，**不得**沿用 0.000000 ns 的预期值。`code/` 未动、HEAD 未变、未提交；论文未动。

### 2026-10-25 PHYS-EXT-HANDOVER-SUPERVISOR-20261025

**目的**：第 40 轮把"批跑完后要跑对照池段"交给两个常驻触发器自动接续；主线**不直接采信这条无人值守链会work**，转而去审它。结果查出**一个会静默卡死的真缺口**，并把那条"段 1-7 会被 resume 跳过"的关键假设从**注释里的断言**变成**被证明的事实**。

**方法与发现**：① 读 `scratch/run_ext_batch_v3.sh` 的段 3（**每次批启动都会重跑**）→ 找到 **4 个 `exit 1` 点**（第 **958** 行 `ext_failed.py --drop`、第 **974** 行 `ext_par_rule.py`、第 **977** 行 `ext_split_tables.py`、第 **979-982** 行 `check_preconditions`），**全部位于段 8（第 1017 行）之前** → 重启后的批可能**在段 8 之前退出**，对照池段一次都跑不到；而触发器**不检查结果**、看门狗只会**每 600 s 重启一次**、族内带触发器**永远空等** → **活锁且无人出声**。责任缺口 = **交接的发起方不确认结果，等待方又只会等**。② **零 EDA 预演**（`scratch/r40_resume_rehearsal/run_rehearsal.sh`）：把真实驱动 `experiments/20261024_physical_labels_itc99/run_labels.sh` 的 `run_one()` **逐字节复制**（real=907 B / copy=907 B，一致），只改 ROOT/FAM 指向假家族目录、PATH 前置**假 `openroad`**（它只写哨兵文件并 exit 0）；三键都预置 `rc.tsv` → **哨兵从未出现**、回执**逐字节未变**、master 日志 **3** 次 `SKIP (already done)`；**反向对照**（删一个键的 `rc.tsv`）→ **哨兵出现**、该键生成新回执 → 证明探针能分辨"跳过"与"真跑"。机制核对：`run_one()` 的跳过条件是 `[ -f "$outdir/rc.tsv" ] && [ "${FORCE:-0}" != "1" ]`（第 47 行），而 **`FORCE` 在批脚本里从未被设置** → resume 确实生效。**边界**：跳过判据是"**回执存在**"而非"rc==0"——失败键同样有回执、同样被跳过，这正是批里另有 `repair_batch`（先 `ext_failed.py --drop` 再重跑）的原因。

**结果**：新增**第三个常驻组件**——**交接看护** `scratch/ext_handover_supervisor.sh`（PID **139777**）：只读，**不碰批 / 看门狗 / 两个触发器 / 不起任何 EDA**；把状态**四态显式区分**——`WAITING`（交接尚未发生）／`RUNNING`（对照池段正在出回执）／`OK`（389 回执到齐 → 交接成功 → 退出）／`ALARM`（交接卡住 → 写明原因 + **批日志尾部**，留在原地不退出）；两条报警判据 = ① 批进程集合**变了 ≥3 次**（非空→非空）却**一个对照池回执都没有** → "keeps dying before segment 8"；② 已出过回执但**停滞 ≥45 min** 且当前无批在跑 → "stalled"。**语义细节**：首次观测到批集合算"出现"**不算**重启（故合法交接本身算第 1 次重启，`RESTART_LIMIT=3` = 再看门狗重启两次仍无回执就报警）；**空集合瞬间不算重启**（否则阈值被白吃、误报）——这一条是**它自己的测试套件抓出来的**（第一版把空集合也计成重启）。套件 `scratch/handover_supervisor_tests/run_tests.sh` **9/9 全绿**（跑在假 runs 树上，不碰真批）：健康交接→OK；批反复死在段 8 之前→ALARM 且理由点名该失效模式；对照池段停滞→ALARM 且理由点名 stall；交接前→WAITING（**"还没发生"与"卡住了"必须可区分**）；断言看护**永不 kill / start 批**。测试用**观测驱动**（等日志/状态出现确切标记再推进），不靠 sleep 猜时序。

**附带诊断**：两个"每轮过期"的落地门**假红的根因是快照型断言**——`scratch/verify_log40_landing.py` **46 checks / 1 FAIL**（唯一红的是"自备份以来只新增了 LOG-40 一行"，而 LOG-41..49 都合法存在）、`scratch/verify_log41_landing.py` **92 checks / 6 FAIL**（"试点恰为 12 完成 / rc=0:10 / rc=124:2"这种**活状态快照**、状态段字节数快照、OI 编号只到 56、圈号只到㉬，以及用**原始 `git status` 口径**判 `code/` clean 的那条——而内容级口径 `scratch/check_code_clean.py`（`--ignore-cr-at-eol`）判的是 **content-level CLEAN、差异 0**）。**处置：不采用"过期即放过"，而是改成性质型断言**，要求每条被替换的断言都有**至少同等强度**的替代、**一条都不许删**，并配**反向对照**（在副本里故意破坏 → 门仍须变红）。本轮另按既有机制在常驻同步门登记 `'**补充（LOG-20261025-49）**'` 锚点（OPEN_ISSUES 新增补充块并改 OI-058 状态格后同步门**正确报红**），**未删任何检查、未弱化任何判据**，复跑 `FAILURES: 0`、反向对照仍 **11/11**。

**边界**：本条全部属**工具/编排层**，**非论文证据**；对照池段未跑，**族内带数字尚未产生**（不出带、不出判决），扩面结果也尚未产生。`code/` 未动、HEAD 未变、未提交；论文未动。工作区外的 `D:\mnt\d\...` 产物树（21 文件 / 31 目录 / 92 KB）与 `D:\BaiduSyncdisk\01_Papers\03_Papers`（1 文件）**仍需用户手动删**（可回撤删除被 runtime 以 "dangerous removal target" 拦下，**未绕过**）。

### 2026-10-25 PHYS-EXT-LANDING-GATES-PROPERTY-20261025

**目的**：两个"每轮过期"的落地验收门（`scratch/verify_log40_landing.py`、`scratch/verify_log41_landing.py`）每轮都要人来确认"过期即放过"——这等于承认门没用。本轮把它们的**快照型断言**改成**性质型断言**，让门**继续有用**。

**方法**：先实跑两个门取基线（`verify_log40_landing.py` **46 checks / 1 FAIL**、`verify_log41_landing.py` **92 checks / 6 FAIL**），逐条判定每条红**到底在保护什么**，再为每一条写出**至少同等强度**的性质型替代（脚本注释里逐条记「原断言 → 新断言 → 为什么等价或更强」）。**一条都不许删**；找不到同等强度替代的检查一律原样保留并单列说明。判据与"强度"取自本项目既有的机制：常驻同步门的**登记块行区间**（`scratch/verify_round34_sync.py` 的 `REGISTERED_BLOCKS`，用 `ast` 读出）、`compute_band` 的池化口径、`check_code_clean.py` 的内容级口径。

**结果**：**48 checks / 0 FAIL** 与 **102 checks / 0 FAIL**（**主线独立复跑确认**）。**七条替换逐条如下**：① "自备份以来只新增了 LOG-40 一行" → LOG-40 块的**之前每一个字节**与备份**逐字节相同** + 备份行序是当前行序的**前缀** + LOG-40 之后的每一行都是备份里没有的新行；② "试点恰为 12 完成 / rc=0:10 / rc=124:2"（**快照了一个会推进的活状态**） → 试点回执数 **== 试点表的键数**（键数从**表的指针**读，不是写死的数字）+ 完成记录/表/回执三者一致 + rc 分布与完成时记录一致 + 重跑台账自洽（`rc.tsv.orig` 仍在、无孤儿原件）；③ "只有状态段被就地改过一行" → **规则**化："被就地修改的每一行必须落在已登记块区间内或状态段内" + 已登记块正文不得被改写 + 备份时已存在的 OI 表格行逐字节不变；④ "状态段增长恰为 915 字节" → 状态段**首句未被截断** + **新增的每一句都带 LOG 编号作为出处标记**；⑤ "OI 编号只到 56" → OI 编号**连续无空洞** + OI-056 仍存在且表格行唯一；⑥ "圈号连续到㉬" → 圈号**从㉠起连续** + **每个圈号都领起一条教训条目**；⑦ "**`code/` is clean**"（用的是**原始 `git status` 口径**，报的是已知的 LF/CRLF checkout 假象） → `code/` 相对 HEAD **内容级干净**（`--ignore-cr-at-eol`，比原口径**更强**）+ 无未跟踪新文件 + **今天没有受跟踪的 `code/` 文件被改过**。**反向对照 16/16 场景**在隔离副本里逐条破坏被保护的性质、门**逐条变红**（唯一噪声：夹具仓库无法复现真实 HEAD 的 SHA，属预期）。**一个活证据**：改造期间本项目自己又落了一条 LOG-20261025-50（LOGS.md 新增一行 + OPEN_ISSUES 新增一个补充块），两个门**依然全绿**。

**边界**：本条属**工具/验收层**，**非论文证据**。一条**环境差异**须记：⑦ 在 **WSL git 下报 57 个 `M code/scripts/...`**（checkout 假象），在 **Windows git 下报 0 条** → 改造前该门在 WSL 下 **6 FAIL**、Windows 下 **5 FAIL**；这恰恰说明该断言**本身不该存在**（它把 git 的换行归一化设置当成了被测对象），新口径统一为内容级。`code/` 内容级差异 0、HEAD 未变、未提交。

### 2026-10-25 PHYS-EXT-HANDOVER-WATCHER-DEFECT-FIX-20261025

**目的**：本轮新加的两个看护组件（交接看护、族内带结果看护）是**无人值守**的，而"无人值守组件自己有没有效"**不能靠它自己的作者审**。故派了一个**独立审计**（只读，报告 `scratch/trigger_audit_r40b/REPORT.md`，31 KB）复核整条链的 8 条结论。

**方法与发现**：审计逐条给出「成立 / 不成立 / 部分成立」+ `file:line` 证据，并对段 3 的重判定做了一次**独立复算**（在自己的目录里重跑 `ext_par_rule.py` + `ext_split_tables.py`，结论一致）。**总体判决：YES-WITH-RISKS**——正常路径上链能自己跑完对照池段并测出族内带；段 8 之前那 4 个 `exit 1` 闸门**幂等通过**。审计**抓出本轮自己两个组件的两个真缺陷**：① **交接看护的活锁告警几乎永不触发**——v2 只在"**非空**集合替换**另一个非空**集合"时计一次重启，而活锁形态是批每次死掉时集合**变空**、下次起来时前一个集合为空 → 被判成"出现" → `restarts_seen` **永远是 0** → **组件要堵的那个洞它自己没堵上**；② **族内带结果看护把坏测量误标成科学结论**——`post_ext_replicate.py` 的判定是 `h4_pass = not reasons`（第 353 行），故 **exit 2 同时涵盖"至少一对不同"（合法科学结果）与"there is NO comparable pair at all"（坏掉的测量）**（第 307-311 行）。审计还**纠正了主线一处判断**：我曾担心 `ext_failed.py --drop` 删目录会让段 8 的 389 **永远凑不齐**，实查第 54-69 行——`--drop` 是把 `rc.tsv` **改名**为 `rc.tsv.orig`、**不删目录**，故 **389 达不到的唯一路径**是"驱动被杀、留下只有 orig 没有 rc.tsv"；**我的担心不成立**。

**结果**：两个看护升到 **v3**（`scratch/ext_handover_supervisor_v3.sh`、`scratch/ext_band_watch_v3.sh`）：① 改为记住**最后一个非空集合**并与它比较——空隙本身不计数，但"批死了又回来"**是**一次替换；② 改为以 replicate 产物的 JSON 为**权威**读 `n_compared_pairs`/`n_missing_pairs`/`pairs.differ`，**先确认 389 对全部可比、0 缺失**才允许给 `REFUSED`，`n_compared == 0` 一律判 **ALARM**。套件 **9/9** 与 **12/12** 全绿（新增"活锁无空隙/有空隙均须报警""一次带空隙的替换 = 恰好 1 次重启""exit 2 但 0 对可比 → ALARM 而非 REFUSED"等场景）。另把**状态文件的写**改成**原子**（临时文件 + `mv` 改名）——原先 `{ ...; } > "$STATUS"` 会**先截断再写**，读者可能读到半个文件（这正是恒红假红的来源之一）。

**边界**：本条属**工具/编排层**，**非论文证据**。审计指出**一处链外的结构性风险**：批/看门狗/触发器/看护**全部活在同一个 WSL `Ubuntu` 实例内、Windows 侧零监护** → **WSL 一关，整条链整体死掉且无人重启**；另 `scratch/ext_status.txt` 里的 `3233` 是**旧 v2 看门狗的陈旧遗留**（mtime 13:05），**现行状态在 `ext_status_v3.txt`**，查进程必须用 `Ubuntu` 这个 distro。`code/` 未动、HEAD 未变、未提交。

### 2026-10-25 R30-F3-FOURTH-IMPLEMENTATION-AXIS-20261025

**目的**：族级判定带 F0/F1 = 0.049752 ns 是**双轴**实现敏感度；单轴带（竖轴 F0/F2 = 0.039884 ns、横轴 F1/F2 = 0.050272 ns）**每轴只有一次实现**（n = 1），"双轴带是单轴敏感度的上界"这句措辞**没有第二个样本支撑**。需要一个**只差单轴的第四个布线实现**来检验这句话。按既有纪律：**开批前先沙箱预演并把判据写死**。

**方法**：**F3 = pin_hor `met5` / pin_ver `met2`**——它是 **{met3,met5}×{met2,met4} 四格网格里唯一缺失的那个角**（F0/F1/F2 占了另外三格），故 **F3 与 F0 只差横向、与 F1 只差竖向**：**补齐网格，而不是再加一个离群点**。退化判据用**双口径**：**标签恒等**为**主判据**（对带算术的零方差）、**布线 DB 指纹**为**物理旁证**、**`place_pins` slot 数**为"pin 层真换了"的证明。判决用 **ρ = 2σ(单轴) / 2σ(双轴)**（匹配子集 S = 两侧都携带方差的电路；带在 S 上用项目自己的 `compute_band` 算）的**五区对称分区**（阈值 1.10 / 1.35，镜像 LOG-20261025-30 的口径），自助按**电路集**重采样 2000 次（电路内候选不独立），**CI95 跨 1 一律降级为 INCONCLUSIVE**；样本量门 N ≥ 2（目标 4），不足判 `NO_VERDICT` 而非否证。**不可动边界**：`0_immutable_boundary` 写死——已发布族带 F0/F1 = 0.049752 ns（`full_family`、df 1193、n 1200）**F3 不得改动**，F3 只是**诊断量**，不得进 `BATCHES`、不得进数据集或分析链，`code/` 保持逐字节不变。

**结果**：**判据在 F3 数据产出之前写死**（`scratch/fourth_impl_r40/f3_prereg.json`，schema `faeco.f3_prereg/2`，`written_before_any_f3_data: true`）。**沙箱预演 16/16**，12 个脚本 `--dry-run` 全部 exit 0 且**前后文件清单逐项相同**（**零 EDA**；全仓库**只有批驱动第 136 行**能调 openroad，dry-run 分支在第 53 行、**在 EDA 行之前**）。**带工具逐位复现** LOG-20261025-32：F0/F1 = 0.049753、F0/F2 = 0.033706、F1/F2 = 0.04554，单轴 0.039884（n 855/df 852）与 0.050272（n 985/df 979）；1207 键全表普查**独立复现** LOG-20261025-30 的"携带方差电路集"（7 / 3 / 6），T1 恒等式 1207 项 **0 违例**。**一条必须写进记录的新信息**：**用这条判据跑现有数据，两个单轴比较已经是 INCONCLUSIVE**——竖轴 F0/F2 vs F0/F1（b01/b03/b10，n 855/df 852）单轴 0.039884 vs 双轴 0.043068、**ρ = 0.926070**、自助 CI95 **[0.743185, 1.0]**（95.95% 的重采样落在 1 以下）；横轴 F1/F2 vs F0/F1（b01/b02/b03/b08/b09/b13，n 985/df 979）单轴 0.050272 vs 双轴 0.049487、**ρ = 1.015863**、CI95 同样跨 1 → **均落在区 C**。**含义**：**"族带是单轴敏感度的上界"这句措辞，在现有数据与这条预注册判据下已处于"不能说"的状态**；LOG-20261025-32 那句"双轴带 0.040078 < 横轴 0.041550"只是**点估计**层面的陈述，**没有**跨过这条更严的门。**F3 的价值因此被重新定义**：不是首次检验这句话，而是检验**这个偏离是系统性的、还是单个实现的偶然**。**一处必须细化（非推翻）LOG-30 的措辞**：直接对 `final.odb` 求 SHA-256 复核，**F0 ≡ F2 于 b02/b08/b09/b13、F1 ≡ F2 于 b10** 与 LOG-30 **逐项一致**，且每对退化电路的 slot 数都不同（b02：150/58/108）→ pin 层确实真换了；但**"b02 55/55"是标签计数**，而**"布线数据库逐字节相同"在 b02 并非全电路成立**——**3 个候选的 ODB 字节不同**，差异是**对象 id 计数器平移 3 个对象**、**文件长度不变**、**标签不变** → **字节不同 ≠ 轴是活的**。**成本（分电路实测，不套用单电路均值）**：Stage A 7 作业 ≈ **8 min**（可一票否决）→ Stage B 70 作业 **1.68 h 串行 / 0.92 h @PAR=2** → Stage C 1207 作业 **21.83 h 串行 / 11.85 h @PAR=2 / 7.00 h @PAR=4**。

**边界**：本条属**方法学/诊断设计层**，**非论文证据**；**本轮未跑任何 EDA**，**(met5,met2) 的可布通性未证实**（Stage A 首验）；成本估算中"F3 只改 PIN_HOR/PIN_VER 故每作业代价与 F0/F1/F2 相同"这一条**是假设、未实测**。**一条对我自己原始设想的更正**：我最初把 F3 的作用说成"把单轴带从 n=1 变成 n=2"——**不成立**：四个实现构成 2×2 网格，六条两两差只由**三个**自由的 per-candidate 对比决定，F3 **只增加一个独立对比**；且**同轴的两个单轴样本是"同一层对的镜像互换"，并非独立物理扰动**。`code/` 内容级差异 0、HEAD 未变、未提交；论文未动。

### LAYOUT-STABILITY-20261031 | 布局实现敏感性（D−B 是否依赖单次布局）

**问题**：四数族每个 D−B 都建立在一次具体布局上（`-utilization 35` 固定），
既有 0.03 ns 噪声底来自同网表重跑，只度量工具确定性；"换一次 floorplan 结论是否成立"此前无法回答。

**方法**：2 例（s641、b13）× 利用率 30/35/40 × base/ecofix = 12 次运行。
base 网表 SHA `d436a0ba…`(s641)/`52b968ac…`(b13)、ECO 网表 `bbaadb96…`/`251eae61…`，三档各三份逐字节相同；
换门清单三档逐行相同（s641 5 门、b13 2 门），只换 floorplan。脚本 `scratch/r98_tmp/run_layout_stability.sh`。

**结果**：D−B 符号 6/6 全正（s641 +0.86/+0.89/+0.84，极差 0.05；b13 +0.11/+0.10/+0.10，极差 0.01）；
C−A 三档恒定（+0.45/+0.05）⇒ 理想档与布局无关，布局依赖全部落在 D−B；
**守门**：u35 逐位复现既有族读数（偏差 0.0000）⇒ 流程确定；12 次运行 DRC 全 0。

**边界**：只 2 例、只动利用率；单角；s641 极差 ≈ 2× 逐电路带 ⇒ 判定带只含网表级离散（登记 OI-074）；
**证据包** `experiments/20261031_layout_stability/`（REPORT.md、stability.json）。

### 2026-11-02 DECISION-OFFLINE-COUNTERFACTUAL-20261102 | 决策层离线反事实（策略枚举族纯 G 臂）

**目的**：上一轮自评把"改进 2（argmax→top-k/序列）"列为候选补强项，但它有一个未验证的前提：实现真的在用"首个可满足即提交"。若实现本来就取候选集最优，则改动无收益可捞；若实现与论文伪代码字面语义不同，则要改的是文字而不是算法。同时把"候选 STA 预算与收益的关系"从估计变成可核。

**方法**：零新增 STA，只读 `experiments/20260826_ablation_pureG/<c>/hybrid_result.json`（8 例、3066 条候选记录、23 次提交）。族身份先钉死：该族 `final_wns` 与论文 `tab:ablation` 纯 G 列 8/8 逐位相同（+0.09/+0.17/+0.35/+0.45/+0.05/+0.02/+0.07/+0.09），且该列终点网表即四数表的修改侧（C 列）。三道自检内联在 `scratch/r102_offline_decision/analyze_decision.py`：① 可加性——逐条提交增益之和 == 终点−基线（`max_additivity_err = 0.0`）；② 提交对齐——`applied_changes[].trial_id` 与逐组重建的提交集合逐条一致（`selfcheck_bad = 0`）；③ 决策身份——23/23 提交组的提交者即组内 WNS 最优者。两个反事实的代价不同：**预算截断是精确的**（只砍掉前缀之后的评测，前缀逐位不变），**决策替换是一阶估计**（换决策后后续实例的评测条件会变，归档未重放该分支）。

**结果**：**预算**——3066 次候选 STA 只换到 23 次提交，有用率 **0.75%**；把每例上限压到 16 次仍得 1.15/1.29 ns（**89.1%**），压到 64 次得 1.26（**97.7%**），与无限上限差 0.03 ns 恰落在噪声底 0.03 ns 上；7/8 例的 80% 增益在前 8 次内完成，s953 跑了 726 次而末次提交在第 45 次，s382/s641 的末次提交分别在第 155 次。**决策**——字面"首个可接受"与实现"候选集最优"在 **6/23 组**不同，超本电路判定带的仅 **2 组**（s641 `_091_`：首命中 −1.42 / 最优 −1.25，差 **0.17** 对其带 0.024558 = 6.9 倍；s420 `_058_` 差 **0.10** 对其带 0.042068），Σregret **0.34 ns** 中 **79.4%** 来自这两例，一阶保留率 **73.6%**（1.29 → 0.95 ns）。**结构差异**——纯 G 族一轮内对多个实例各提交一次（s641 第 1 轮 4 次、第 2 轮 1 次），与伪代码"提交即 break、刷新 `P` 再重提锥"的单提交语义不同；受控 9 臂族（`real_wns.py`）才是每轮一次提交。

**边界**：只覆盖 ISCAS89 策略枚举族（纯 G 臂），**不与受控 9 臂族拼 STA 计数**（后者单 worker、500 次预约、每轮一提交）；Σregret 是一阶估计，精确部分只有单组 0.17/0.10 两条；判定带借自 W1 族作"同电路分辨率"尺子，不搬其增益结论。**本实验不改任何论文数字**（8 例终点与纯 G 列逐位相同），论文未动；伪代码与 §"评估、提交与停止"那句"首次可接受候选成为新基准"的描述性偏差已登记 **OI-075**。产物 `experiments/20261102_offline_decision/`（REPORT.md、readings.tsv、perchange.tsv、pergroup.tsv、summary.json）。

### 2026-11-02 LAYOUT-STABILITY-N8-20261102 | 布局实现敏感性扩到 8 例

**目的**：r101 只用 2 例（s641、b13）就把"判定带只含网表级离散、不含布局实现离散"写成覆盖全文的限定，而主文表 5 的 8 例 D−B 各自只建立在一次 floorplan 上。本实验把同一口径扩到全部 8 例，问两件事：换布局后 D−B 的符号是否仍成立；"超过判定带"这一分级是否稳定。

**方法**：与 r101 完全同一脚本（`code/scripts/run_eco_phys_itc.sh`），只换 CASES。8 例 × `-utilization` 30/35/40 × base/ecofix = 48 次物理流程（约 42 min），输入网表与 r101 逐字节同源（`_src/s641/mapped.v` = `d436a0ba…`，ECO 侧 `bbaadb96…`）。判据在看到数据前写定（G 守门 / H1 符号 / H2 幅度 `R/b` / H3 分级翻转），见 `REPORT.md` §3。

**结果**：守门 8/8 逐位复现原四数族（最大偏差 0.0000），三档 `replace_cell` 命令逐条相同；请求利用率经站点量化后实际 30.7%--42.9%，核心面积变化 23%--26%，三档确为不同布局。**符号 8/8 三档同号**；`C−A` 跨档极差 0.0000 ns（理想档与布局无关，布局依赖全落在 D−B）；**D−B 极差 0.01--0.17 ns**（中位 0.04），`R/b` 中位 0.61、两例大于 2（**s953 0.17 = 3.8 倍带**、s641 0.05 = 2.0 倍）；合计 1.80 / 1.97 / 1.85 ns，均值 0.2250 / 0.2462 / 0.2643。**分级**：u35 超带 6/8（与论文一致），三档全超 4/8，**s820 与 s953 随档翻转**；s27 的 u40 详细布局失败（`DPL-0036`，CTS 后利用率 88.2%）记未评估。

**边界**：单工艺角（TT/1.8 V/0.5 ns），`aspect_ratio`/`core_space`/CTS 缓冲列表/布线层均未变，只动 utilization；每个 D−B 仍是实现点读数，三点给的是极差不是分布。**不改任何已发表数字**；论文未动，§5 那句的改写建议见 `OPEN_ISSUES.md` OI-074 待决④。产物 `experiments/20261102_layout_stability_n8/`（REPORT.md、`u{30,35,40}/readings.tsv`、guard.tsv、stability_n8.json）。

### 2026-11-02 COVERAGE-SWEEP-20261102 | 扩覆盖受控对照（max_instances 8 → 不限）

**目的**：外部基线显示 OpenROAD `repair_timing` 在同视图下 8 例合计 2.3286 ns，FAECO 为 1.2900 ns（1.81×）。一个自然解释是"搜索覆盖不足"——s820 的关键路径上有 99 个实例而 W1 只覆盖 9 个（9.1%）。本实验检验该解释。

**方法**：E1 仅把 `max_instances` 由 8 改为 10000，其余 argv 从 W1 的 `run_config.json` 逐项复制，输入网表逐字节相同；零新增代码。预注册判据：G 守门（s27 只有 8 个组合门，等于全覆盖，必须逐位复现）、H1（覆盖是主因则应 ≥3/8 例超带）、H2（逐位相同则否证）。

**结果**：守门通过（s27 −0.18 / 49 次 STA，与 W1 逐位相同）。实例覆盖 9–10 → 10/11/16/24/25/34/36（1.0–4.0 倍）、STA 增加 1.00–3.74 倍，但 **7/8 例增益逐位相同**。唯一变化的 s713（+0.12）在同预算 137 次处两臂完全一致，需 2.2 倍预算（300 次）才拿到 ⇒ 不构成改进。**同预算 8 例合计增量 = 0.0000 ns。** H2 成立、H1 不成立。

**边界**：只动一个参数，扩出的实例仍受 `candidates-per-iteration 8` 的 beam 截断，故"覆盖"指"参与排序的实例范围"而非"全部被测量"；单族单角。**不改任何已发表数字**，论文未动。产物 `experiments/20261102_coverage/`（REPORT.md、readings.tsv、compare.json、E1/<c>/）。

### 2026-11-02 FF-ACTION-GAP-20261102 | 动作集缺口：触发器从未进入候选集

**目的**：继续追查 1.81× 差距的来源。逐实例比对 OpenROAD 的修复网表后发现其主要改动之一是触发器驱动升级，而 FAECO 的动作集从未包含时序单元。

**方法**：导出 OpenROAD `repair_timing -setup` 前后网表逐实例比对；再在 FAECO 侧的 `eval_trials.json` 里统计 `dfxtp` 出现次数。效应量用网表级替换探针测（全部 `dfxtp_1` → `dfxtp_4`，视作一个组合动作，同口径理想档 STA），另做逐点贪心（每步只保留 WNS 变好者）作对照。

**结果**：s820 上 OpenROAD 共改 14 个门（10.1%）= 10 resize + 4 buffer，其中含 **5 个 `dfxtp_1 → dfxtp_4`**（该电路一共只有 5 个触发器，即全升）与 1 个 `clkinv_1 → inv_2`。FAECO 侧：W1 的 s820 共 107 次尝试，`dfxtp` 出现 **0 次**；8 例合计 2200+ 次尝试仍为 0。根因两条独立路径：`_INSTANCE_LINE_RE` 的 `(\w+)/\w+` 无法匹配含点号的 `DFF_1._0_`；即使匹配到，`cut` 只覆盖组合逻辑锥。效应量 **4 正 4 负**：s832 +0.1955（2.31 倍带）、s820 +0.1013（1.41×）、s953 +0.0939（2.08×）、s420 +0.0669（1.59×），负例 −0.0106 至 −0.0432；正的 4 例**全部超过各自判定带**，净 +0.3615。逐点贪心合计仅 +0.2158 且只有 1 例超带 ⇒ 全升是单点的 1.67 倍。面积代价 +2.12%–10.71%（`dfxtp_4/dfxtp_1` = 1.19×）。

**边界**：探针是网表级字符串替换，**不是通过运行器动作集执行**，接入后的实际增益未测；只测 `_1 → _4` 一档；**未做 SEC 复核、未做物理档验证**；4/8 为负须与正例并列报告。这是"我们自己的实现缺口"，写成论文须表述为"归纳出的设计原则"而非"我们的 bug"。产物 `experiments/20261102_ff_action/`（REPORT.md、readings.tsv、summary.json）、`scratch/r110_orchg/`。
### 2026-11-10 PLACED-GATE-20261110 | 用真实布局寄生档做接受判据（预注册）

**目的**：上一轮把方向 A（打开 `--physical-gate` 解锁 B 类缓冲）证伪，根因是 `spef.py` 的扇出线载模型结构上无法表达缓冲收益。本轮换成**真实布局后端**（floorplan→place→CTS→`set_wire_rc met2/met4`→`estimate_parasitics -placement`），把接受判据放在这一档，并用**完整布线 + RCX 提取**的独立 STA 做端点，重问"理想档是否废掉了缓冲插入、换档位能否提高最终质量"。

**方法**：预注册（`experiments/20261110_placed_gate/PREREGISTRATION.md`，运行前写死）：臂 I = 理想档判据（逐字复制 W1 flags，作为代码回归与控制组）；臂 P = 同搜索 + `--physical-gate --physical-backend placed`（布局档成对增益 ≥0.010 ns 才接受）。4 例 s382/s641/s832/s953，period 0.5，20 轮。端点 = `code/src/rseco/routed_sta.py` 对三网表（base/armI/armP）**同一流程**布线后测量。门：H1 构成（臂 P 在 ≥2/4 例接受 B、臂 I 0 例）、H2 转移（臂 P 布线后增益在 ≥3/4 例更好且均值差 ≥0.05 ns 才晋级 8 例）、H3 分辨率（臂 P 的接受里布局档增益 <0.055 ns 的比例 >50% 即"接受的是噪声"）。

**结果**：H1 **PASS**——臂 P 在 s641（`and4_1→buf_2`，+0.0270）与 s832（`or3_1→buf_2`，+0.0109）各接受 1 个 B，臂 I 4 例 11 个接受全为 G/R、B=0（W1 全 8 例 0/606）⇒ **"理想判据废掉缓冲插入"在真实布局寄生下成立**；但 B 的物理价值依电路而定（s641 B 候选正例 88/160、中位 +0.0016、最大 +0.2371；s382 仅 12/168、中位 −0.0142）。H2 **FAIL**——布线后增益 I +1.1157（均值 0.2789）对 P +1.2495（0.3124），P 更好仅 **2/4**（s641 +0.1304、s832 +0.0847；s382 −0.0517、s953 −0.0298），均值差 **+0.0334 ns** < 0.05 门槛；H3 4/8（份额 0.50）未过。**PROMOTE = NO ⇒ 停止，不扩 8 例、不调参重跑。** 事后阈值臂（A2，不进晋级判定）：gate 抬到该档位自己的分辨率后，`P_g005`（0.050）4 接受 / **602 次候选评估**、`P_g003`（0.030）6 / 739、`P`（0.010）8 / 878、`I` 11 / **1157** ⇒ 布局档离散 gate 比理想档少 **48%** 候选评估而端点不降（均值 0.3095 / 0.3067 / 0.3124 / 0.2789，互不可分辨）。补丁链（s382/s953，9 步逐网表布线）：7 步布线后为正、2 步为负（s953 第 2 步 −0.0326，两臂相同）；s953 布线后最优前缀是第 1 步（+0.1240），其后两步净 ≈0.003 ns ⇒ "验证式接受"可得量级 ≤0.03 ns/例。另 1 例（臂 I/s832）理想档接受把布线后 WNS 从 −1.6712 做坏到 −1.7374（−0.0663），为"理想线网说谎"首次出现在端点层面，但 1/4 例不成结论。

**边界**：4 例 ISCAS89 子集（非论文 8 例矩阵）；布局档 = `estimate_parasitics -placement`、布线后档 = RCX 提取，**都不是签核 RC**；机制 gate 首轮仍是"布局档候选 vs 理想基线"混档；DRC 未进端点判据；成本读数受 `--workers` 影响（A1：同 workers 才可比，臂间可比、与 W1 归档不可比）；补丁链只覆盖 2 例。**未改论文、未改 CANON 冻结数字。**

**产物**：`experiments/20261110_placed_gate/`（`PREREGISTRATION.md`、`REPORT.md`、`summary.json`、`patch_chain.json`、`arms/{I,P,P_g005,P_g003}/<c>/`、`endpoint/<c>/{base,arm*}/`、`endpoint_chain/`）。

### 2026-11-11 PLACED-ENS-20261111 | 布局集成判据（k=3 布局均值判决）

**状态**：完成（4 例 × 单臂 E；预注册判定 H1 PASS / H2 FAIL / H3 PASS ⇒ **不晋级**）
**问题**：上一轮（`PLACED-GATE-20261110`）H2 FAIL 是「未分辨」还是「已证否」？——同一网表换布局端点摆动 0.044–0.057 ns，而待判效应只有 +0.0334 ns。
**装置**：新增 `physical_backend="placed_ens"`，判决用 0.30/0.35/0.40 三个利用率布局档读数的均值（噪声 1/√k）；其余搜索 flag 与 W1 / arm I / arm P 逐字相同；端点用 `routed_sta` 同一流程测三布局并取均值。预注册 H1（分歧率 > 15%）/ H2（端点 E 优 ≥3/4 且均值差 ≥0.05 ns）/ H3（候选 STA ≤1.6×），运行前落地。
**结果**：H1 **PASS**——单布局判决与三布局均值判决在接近门槛的候选上分歧 **89/190 = 46.8%** ⇒ 单布局档判决一半是布局抽签（OI-074 的机制侧定量形式）。H2 **FAIL**——三布局均值端点增益 E 对 P：s382 +0.1780 / +0.1757、s641 +0.9093 / +0.9606、s832 +0.0131 / +0.0189、s953 +0.1377 / +0.0379；E 优 2/4、均值差 **+0.0112 ns** < 0.05。H3 PASS，候选 STA 738 / 878 = **0.84×**。**PROMOTE = NO**：判决器不是瓶颈。s953 的 +0.0998 来自 arm E 接受了 1 个 JOINT 补丁（+0.0604），属**动作种类**差异而非判决精度差异。
**读数边界**：12 个「电路 × 网表」格跨布局增益极差均值 **0.1042 ns**（范围 0.0011–0.2328）⇒ 三布局均值残余误差 ≈0.060 ns/例、4 例均值标准误 ≈0.030 ns，与 0.05 ns 门槛同阶 ⇒ **H2 记「未分辨 + 不晋级」，不是「已证否」**；4 例小规模 ISCAS89；RC 为 RCX 估计非签核；arm E 的 STA 计数不可与 I/P 横比（`--workers 4`，见 `PLACED-GATE-20261110` §7 A1）；s382 的 arm E 终态网表与 arm I 逐字节相同（`2927efa7fdfd58d7`）。
**产物**：`experiments/20261111_placed_ens_gate/`（`PREREGISTRATION.md`、`REPORT.md`、`summary.json`、`arms/E/<c>/`、`endpoint{,_u0.30,_u0.40}/<c>/armE/`）；代码 `code/src/rseco/real_wns.py` 的 `physical_backend="placed_ens"`；测试 `code/tests/test_placed_sta.py::PlacedEnsembleTest`。

### 2026-11-12 ACTION-GRANULARITY-20261112 | 把一次动作放大到 6 门（joint-k 2→6）

**状态**：完成（4 例 × 两臂 A6j/A6，对照归档 arm E；预注册 H1 FAIL / H2 FAIL / H3 PASS ⇒ **不晋级**）
**问题**：前两轮（判据档位、判决噪声）端点都不动。归档读数显示每个被接受补丁只改 **1 个门**、单次决策物理增益 0.01–0.12 ns，与跨布局离散 0.1042 ns 同阶 ⇒ 单次动作效应量是否就是瓶颈？
**装置**：用机制**已有**的 `--joint-k`（`code/src/rseco/real_wns.py:3111-3155`，取 `actionable[:k]` 各改一档合成一个候选）。**A6j（主检验）** = 与 arm E 逐字相同、只把 joint-k 2→6（候选池相同）；**A6（补充）** = 另把 `--max-instances` 8→16。判据仍为 `placed_ens` 0.30/0.35/0.40；端点 = `routed_sta` 三布局布线后 WNS 均值（base 复用 `20261110_placed_gate`）。
**结果**：H1 动作变大 **FAIL 1/8**（只有 s382 iter1 的 JOINT 是 6 门；其余 7 个补丁各改 1 门）⇒ **机制几乎不选大动作**。H2 端点转移 **FAIL**：A6j 三布局均值增益 +1.2289（均值 0.3072）对 arm E +1.2381（0.3095），**差 −0.0023 ns**，仅 1/4 优；**s641/s832 的终态网表与 E 逐字节相同**。H3 成本 PASS（候选 STA 850 vs 738 = 1.15×）。A6 补充：H1 1/7、H2 0/4（−0.0236）、成本 1.58×，四例全部 `stop_reason=sta_budget`。**PROMOTE = NO**。
**本轮最重要的正面线索（补丁链，布线后逐补丁增量，util 0.35）**：s382 +0.0727(JOINT 6 门) / −0.0038(G) / **+0.1001(B)**；s953 +0.1240(G) / −0.0428(G) / **+0.1253(B)** ⇒ 两个最大增量都来自 **B 类插缓冲**，即理想线网判据从不接受、真实布局档判据才开始接受的那一类。
**机制诊断**：瓶颈不是判据档位、不是判决噪声、也不是动作宽度，而是「每轮只生成 1 个联合候选 + 贪心按单步增益取最大」的选择结构（s641：单门 +0.609 压掉 6 门 +0.4767）。
**运行期修订**（`PREREGISTRATION.md` §7）：A1（`--max-instances 16` 使每轮候选从 ~10 抬到 65–155、500 次 STA 预算 2–4 轮耗尽，故主检验改 A6j；端点未测时写下）；A2（H1 度量由 diff 行数改为**改动门数**，行数会双计 JOINT/把插缓冲算 3 门；改后 H1 由 3/8 PASS 变 1/8 FAIL，结论更保守）。
**读数边界**：4 例 ISCAS89 小电路、period 0.5；端点仍是三布局均值，残余误差 ~0.06 ns/例、4 例标准误 ~0.03 ns，与 0.05 ns 门槛同阶 ⇒ **能判"无差别"，不能判"略有优劣"**；只动一个旋钮，JOINT 组合空间几乎未搜索，**不得**外推为"大动作原理无效"；判据是布局档、布线后端点非签核 RC。**未改论文、未改 CANON 冻结数字。**

**产物**：`experiments/20261112_action_granularity/`（`PREREGISTRATION.md`、`REPORT.md`、`summary.json`、`patch_chain.json`、`run_arms.sh`、`run_endpoints.py`、`analyze.py`、`run_patch_chain.py`、`arms/{A6j,A6}/<c>/`、`endpoint{,_u0.30,_u0.40}/<c>/arm*/`、`endpoint_chain/`）。

### 2026-11-13 BUFFER-CALIBRATION-20261113

- **族**：机制（接受判据的排序规则）；臂 K vs 归档臂 E。
- **预注册**：`experiments/20261113_buffer_calibration/PREREGISTRATION.md`（sha256 前 16 位 `f0cb9b1b8af432b9`，6117 B，写于运行之前）。
- **装置**：`--physical-backend placed_ens --placement-utils 0.30,0.35,0.40`，`--max-instances 8 --joint-k 2`，`--sta-budget 500 --workers 4`；唯一差异 `--postroute-calibration "B=5.64,G=0.60,JOINT=0.53"`。
- **主判据电路**：held-out s641/s832；in-sample s382/s953（不判）。
- **读数**：s641 +0.9444（E +0.9093）、s832 +0.0131（E +0.0131）、s382 +0.1851（E +0.1780）、s953 +0.0401（E +0.1377）；候选 STA 1005 对 738（1.36×）。
- **判定**：H1 FAIL（s832 无 B 过关）、H2 FAIL（held-out 均值差 +0.0175 < 0.05）、H3 FAIL（1.36× > 1.2）⇒ PROMOTE = NO，停线。
- **结论**：按种类校准能改变判决但不能转移收益；故障点在常数抽样误差（4 个补丁步），不是排序机制。
- **产物**：`experiments/20261113_buffer_calibration/{PREREGISTRATION.md,REPORT.md,summary.json,replay_selection.json,arms/K/,endpoint*/}`。
- **勿重复**：不要再用 4 个补丁步的按种类常数重跑；要重开需先补逐补丁布线后配对（每例 5–10 步）再重新拟合。
### 2026-11-14 SELECTION-CEILING-20261114
- 类型：离线分析（不跑 STA、不跑布线）
- 脚本：`experiments/20261114_selection_ceiling/analyze_ceiling.py`
- 产物：`ceiling.json`（sha256 前 16 `9653f3103460dcea`）、`ANALYSIS.md`（`eabf4da79033e188`）
- 输入：`20261110_placed_gate/arms/{I,P}`、`20261111_placed_ens_gate/arms/E`、
  `20261113_buffer_calibration/arms/K` 的 `eval_trials.json`
- 结论：四臂端点极差 0.0368 ns；top-3 同实例 15%；跨臂 top-1 同实例 4/7；逐补丁 Spearman 0.164（n=10）
  ⇒ 判据侧无空间，瓶颈在候选生成
- 勿重复：不要再开"换判据/改判决精度/按种类校准"的实验，除非先给出 top-1 跨判据不一致的证据

### 2026-11-14 ACCEPT-ALL-20261114（批接受实验）
- 臂：All（arm E + `--accept-all`） vs E（归档）
- 电路：s382 / s641 / s832 / s953
- 端点：布线后 WNS，三布局 0.30/0.35/0.40 均值
- H1（接受数量）PASS，H2（端点转移）FAIL（均值差 -0.2574），H3（成本）PASS，PROMOTE=NO
- 目录：`experiments/20261114_accept_all/`
- 预注册 sha256@16=8a5929d009b86ca4；报告 sha256@16=cd631f84a8a490c9
- **勿重复**：动作空间天花板已被六轮实验（P/E→K→A6j→All）封口。

### 2026-11-11 P1-RESIZER-VS-FAECOP

- 问题：FAECO-P（布局后覆盖优先、placed_ens 判据、单补丁接受）的**布线后 WNS** 是否优于 OpenROAD
  `repair_timing -setup`（默认参数）。
- 输入：`experiments/20261016_r22_cut_ablation_v3/W1/<c>/mapped.v`（8 例 ISCAS89，period 0.5）。
- 读数：`rseco.routed_sta`，每臂每 util 一条，三布局（0.30/0.35/0.40）均值。
- 结果：base→resizer **+0.5836 ns**、base→FAECO-P **+0.2473 ns**、FAECO-P−resizer **−0.3362 ns**，
  **0/8 胜**、p=1.0 ⇒ **PROMOTE = NO**。
- 产物：`experiments/20261115_p1_resizer_vs_faeco/{REPORT.md,summary.json,arms/*,endpoint*}`。
- **勿重复**：不要再以「改判据/改判决精度去赢 resizer」为题重跑；重开须先回答可组合性（Hybrid 臂）。

### 2026-11-11 HYBRID-RESIZER-FAECOP

- 问题：同一 resizer 流程、只把起始网表换成 FAECO-P 终点网表，终点是否更好（P1 的组合臂）。
- 读数：三布局（0.30/0.35/0.40）均值，`summary_hybrid.json`。
- 结果：胜 **5/8**、均值差 **+0.0243 ns**（门槛 +0.05）⇒ **PROMOTE = NO**；事后追加臂。
- **勿重复**：不要再以"组合我们的 ECO + resizer"为题重跑；只允许调度/预算类问法。

### 2026-11-11 P1P-RESIZER-THEN-FAECOP

- 问题：resizer 先做、我们的 ECO 在它终点上继续做，是否还有残余空间（P1 的镜像组合臂）。
- 装置：`experiments/20261116_resizer_then_faecop/`；resizer 段 = pre-CTS `repair_timing` 变体导出网表；
  我方段 = FAECO-P（单补丁接受、三布局 placed 判决）；端点 = routed STA，util 0.30/0.35/0.40 三布局均值。
- 结果：H1 可行性 **PASS**（18 次布线 DRC=0）；**H2 残余空间 PASS**——RF−R′ = 0.0000 / +0.1202 / +0.1157
  （s382/s641/s832），均值 **+0.0786 ns**；**PROMOTE=YES**。逐补丁布线后增量 5/5 为正。
- 边界：R′ 是比 P1 post-CTS resizer 弱 0.19/0.21 ns 的变体（re-entry gap），结论只限 RF vs R′ 配对；
  三例 pilot，扩样须另立预注册；仅测 WNS，未测功耗/面积。
- **可续做**：扩到 8 例（需新预注册）；把 resizer 段换成 post-CTS 变体（须先解决扁平网表重入 segfault）。
- 前置缺陷修复：`code/src/rseco/netlist.py` 扁平网表多行实例解析（commit `ef72abd`）。

### 2026-11-11 P1P2-POSTCTS-RESIDUAL

- 问题：把 P1′ 的 resizer 段换成 post-CTS 变体（与 P1 实际对手同形）后，本文机制在它终点上还有没有残余空间。
- 装置：`experiments/20261117_postcts_residual/`；导出点在 CTS 之后；我方段 = FAECO-P（单补丁接受、三布局 placed 判决）；
  端点 = routed STA + `skip_clock_tree=True`，util 0.30/0.35/0.40 三布局均值。
- 结果：H1 可行性 **PASS**（18 次布线 DRC=0）；**H2 残余空间 FAIL**——RF−R′ = −0.1659 / −0.5325 / −0.4879
  （s382/s641/s832），均值 **−0.3954 ns**，0/3 为正；**PROMOTE=NO**。
  re-entry gap +0.0168/+0.0160/−0.0830（|gap|<0.15，对照端点忠实）。
- 诊断：布局档判断在 post-CTS 终点上不可迁移——同网表 placed −2.10 vs routed −1.11；+0.609 的 placed 改善
  在布线后翻成 −0.532（探针 with-CTS +0.6369 / skip-CTS +0.6187，排除双重建树）。
- 边界：3 例 pilot；只测 WNS；只检验本机制的动作空间与判断器 ⇒ 不得写「post-CTS 终点没有残余空间」。
- 前置缺陷：post-CTS 网表重入需 `skip_clock_tree`（`code/src/rseco/routed_sta.py`）。
- 结论：P1′ 线在当前机制下封口；继续必须先解决判断器与端点一致性。


### 2026-11-12 RECOVERY-20261112
**目的**：逐 reversion 诊断 Resizer 在 8 例 ISCAS89 上的改动哪些对 WNS 有贡献，哪些是盲目放大。
**方法**：对每个电路取 Resizer routed.v -> parse 改动（changed cells vs baseline mapped.v）-> 逐 revert 用 sta_routed 独立评估 WNS 影响 -> 按 dWNS 升序累积应用（max_degradation=0.05 ns）。
**主结果**：FAECO 面积效率 = 4.4x Resizer（几何均值，7/8 例）。107 个改动中 74 个（69%）可安全回退。
**产物**：experiments/20261112_resizer_recovery/REPORT.md；每电路 arms/RECOVERED/<c>/summary.json。
**记录**：project_docs/LOGS.md（LOG-20261112-01）、docs/EXPERIENCE.md（r129）。
**判定**：面积效率比 >=2x on 7/8 PASS；Recovery >=20% on 4/8 PASS。
**状态**：NON_PROMOTION（诊断性实验，不晋级，但结果强）。


### 2026-11-12 RECOVERY-QUALIFICATION-PHASE0

- **状态**：ENGINEERING_PILOT_COMPLETE / NON_PROMOTION（2026-11-13 完成限定工程验收；严格时序门失败，不作科学晋级）。
- **预注册**：`project_docs/evidence/recovery_qualification_20261112/PREREGISTRATION.md`；parent source HEAD `51cebf5aa6a8946e81b7e2d6018ba8879660c749`，本轮修正后的 CLI 另绑定文件 SHA。
- **问题与先行证伪**：s382 同状态 DEF 重入能否恢复原 netlist 功能单元/连接，且独立原 SPEF ideal-clock setup/hold slack 与历史终点相差不超过 1e-6 ns；任一失败则停止解释后续 recovery 差值。
- **输入**：`experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/` 的 routed DEF/Verilog/SPEF；恢复配方 `experiments/20261112_resizer_recovery/arms/RECOVERED_V2/s382/{summary.json,recovered.v}`。交接中 `20261112.../arms/Resizer/s382` 路径不存在，不使用。
- **环境**：sky130hd TT 025C 1v80 与既有 ORFS RCX；`/home/toylog/faeco_eda/or26Q3/bin/openroad`、`/usr/local/bin/sta`。主线已实查 installed help 支持 `repair_timing -recover_power 100`（`scratch/recovery_preflight.log`）。
- **后续条件臂**：仅 phase 0 通过后运行同起点 CONTROL / RECOVERY_V2 / NATIVE，统一物理流程及终点约束，重新合法化、布线、提取寄生；propagated-clock 另表，不混历史 ideal-clock。
- **门槛与边界**：严格非劣 slack 降幅 <=1e-6 ns；placement/DRC/setup/TNS/hold/slew/cap 检查缺项即 unknown；科学晋级还需 SEC。面积主口径为总 standard-cell 面积下降，不混新增面积回收。单例只能证明可行性。
- **运行纪律**：STA/重入每子进程 300 s，routing 900 s，串行布线、持续日志/进度；输入/工具/驱动 SHA、argv、耗时、rc、输出与实际 pass/fail/unknown 必须留存。不得观测结果后改门槛，无论文修改。


#### RECOVERY-QUALIFICATION-PHASE0 / Phase1_v2 收尾（2026-11-13）

- **实际核验源**：`recovery_qualification_20261112/REPORT.md`、`PILOT_SUMMARY.json` 已由记录端实际打开；逐输入/输出、工具与驱动身份见该目录 manifest、SHA 收据和 SEC proof receipts。
- **Phase0**：同状态结构全部 3128 实例/335 bindings/10 ports/109 声明/4 assigns 通过；ideal-clock setup/hold 精确复现。端口顺序差异只限 named 顶层接口。
- **Phase1_v2**：s382 三臂同起点、合法化/重新布线/新 SPEF。CONTROL 面积 1052.2592 μm²，RECOVERY_V2 1005.9648 μm²，降 4.399524375743126%；NATIVE 0 resize，面积与时序同 CONTROL。
- **严格门 FAIL**：propagated setup 退化 0.009971634629124537 ns、hold 退化 0.000018596235662471372 ns、TNS 退化 0.312647 ns，超过 1e-6 ns 严格非劣阈值。三臂均有负 setup slack，非 timing closure；ideal-clock 门也失败。
- **物理/逻辑边界**：三臂 route DRC=0 仅限支持规则（LEF58_ENCLOSURE 缺 CUTCLASS 被跳过）；DRV raw 无 VIOLATED 不等于完整 SDC/约束覆盖已建立。两组 SEC 均 101 proven/0 unproven，含完整 102 功能 cell/21 FF，明确剔除同一 3026 零 pin tap；模型域内等价不覆盖物理时序。
- **工程门**：1113 passed/156 subtests，清理并发后 24 passed 重检；零值/导入修复与 packaged helper 已固化。代码提交 `a20f48c`，预注册/roadmap 提交 `e3c694c`。
- **数据口径修正**：14 例只读审计总 mapped-cell 面积平均降 3.071500828%，旧 4.54223469% 分母漏项；绝对节省不变。新增面积回收约 14% 仍待层次 baseline 审计。
- **后续门**：生产 escaped parser/SEC scanner、baseline 层次、完整 SDC/DRV、自定义 Liberty，以及最强等预算基线与新机制证据仍待解决。本轮无论文改动，非 ICCAD 研究任务全部完成；仅 s382 新物理 pilot，未重跑全部 14 例。


### 2026-11-13 RECOVERY-REPAIR-S382

- **状态**：PRE_REGISTERED，限定单电路最小补偿研究；记录端已在实际 EDA 前打开 `recovery_repair_20261113/PREREGISTRATION.md` 与 `PLAN.json`。
- **输入/身份**：自包含 inputs 副本源于已验 recovery_qualification_20261112，13 文件/哈希、reentry OpenDB、原 SPEF、13-action recipe、结构 checker、既有 CONTROL/RECOVERY 终点；工具/Liberty/LEF/RCX 与原 flow 固定。不得修改原证据或生产 parser。
- **先行测量**：CONTROL 与原 RECOVERY 各一次 standalone STA，TNS 9 位和详细 full-clock 路径；同终点 netlist/SPEF、不重路由。路径归因不用于过滤候选。
- **Stage A**：全 13 单点 restore，分别恢复 `_052_/_054_/_055_/_074_/_077_/_079_/_081_/_093_/_096_/_098_/_102_/_111_/_113_` 之一为 Resizer cell，保留另外 12 个回退，不提前停止/删负例。
- **统一物理流程**：period 0.5 ns，propagated-clock 终点，副本清 regular wires 后 full reroute 15 iterations，统一 legalization/RCX；routing 串行且 timeout 900 s，STA 300 s，计成本但不称独占 benchmark。
- **固定门槛**：WNS 损失预算 0/0.002/0.005/0.010 ns 加 1e-6 ns 数值容差；TNS 非劣 1e-6 ns；hold >=0、supported-rule DRC=0、无报告 slew/cap violations。hold 是新的绝对可行性门，旧 hold 非劣差值另报；完整 SDC/DRV 覆盖仍未知，全部点仍有 setup violation，不称 timing closure。
- **Stage B 条件**：仅全 singletons 中不存在零预算、正面积节省合格点时，才按组合结果产生前明确固定的规则扩展，最多 12 次新物理运行。组合精确规则尚待记录；预测不作接受依据。全恢复 CONTROL 零节省仅 fallback。
- **验收**：完整实例/连接与 intended edits、完整 Liberty cell 模型下 SEC、原日志/error 核查、SHA封存；面积用 canonical 完整分母（含 escaped FF，只排明确无连接 tap）。四预算最大保留面积、所有失败与 candidate/route/STA 成本共同报告，限 s382 单实现，不主张新颖性或强基线优越。


#### RECOVERY-REPAIR-S382 运行前用户收紧主门（2026-11-13）

主线在全部新物理运行前写入预注册 steering，记录端已实际复读：主接受门改为 WNS/TNS/hold 全部相对 CONTROL 非劣（1e-6 ns 数值容差），同时 hold>=0；先前仅 hold 绝对可行的描述被此条覆盖。2/5/10 ps 仅诊断，不允许据此科学晋级或隐藏退化。用户要求按 ICCAD 标准发展独立机制，须形成明确选择/补偿算法并与等预算强基线比较；本轮单例搜索不直接构成创新性证明。


#### RECOVERY-REPAIR-S382 启动记录与登记时序澄清

主线报告批次 session74268 已启动，日志 `scratch/recovery_repair_singletons.log`，外层 timeout1200 s、每 routing900 s并持续监测。预注册/PLAN 与严格 WNS/TNS/hold steering 已在运行前固化（commit `facf9d3`）。记录端完成 registry 写入时与主线启动观测并发，主线启动前读尾部未见新条目；本登记按主线视为批次开始后补记，不回填为已证实的 registry-before-run。实验预注册先于执行的事实以提交和驱动身份绑定为准；两种文档时间不得混淆。


#### RECOVERY-REPAIR-S382 Stage B 条件就绪（2026-11-13，组合未执行）

Stage A 13 个物理臂已由主线实查全部结束：391 s/rc=0，日志 `scratch/recovery_repair_singletons.log`；独立审查当时完成 12 个失败，末项待审，故此刻不提前声称 13/13 strict 失败。

记录端实际读取预注册 frozen combination rule：仅全部有效 singleton strict 失败时，取排名最好 3 个 singleton 做 beam，依次扩 cardinality2/3/4/5；每层只执行 3 个此前未测集合，最多12次。只加原13动作，按排序实例集去重。提案预测=原RECOVERY+单点相对RECOVERY差之和，仅排序；面积精确计算。排名为(无效/物理检查flag、最大规范化deficit、deficit和、负保留面积、实例名)，deficit=max(0,CONTROL-candidate-1e-6)，setup/TNS/hold 分母分别0.010/0.312647/0.001 ns，hold<0亦不可行。每层实测3点作为下一beam；失败/timeout计预算且先归因，不替换；一层出现strict正节省点即停。原 PLAN 保持冻结，组合另有 COMBINATION_PLAN。该 heuristic 尚无等预算强基线创新性证据，预测不可接受候选；主门未改变。


#### RECOVERY-REPAIR-S382 Stage A 冻结结果

SUMMARY.json `5ae335bc5e981842a41a912bbf1b4ccf213738106dba02d94b1a52495079c8a9` 独立验完13有效/13 strict失败，所有WNS/TNS退化，7例hold退化，四档均无合格点（TNS为硬门）。13route/26STA，逐job合386.312s、外层391s/rc0。无终点接受故无SEC；满足Stage B预设触发条件，不能改称单点补偿有效。


#### RECOVERY-REPAIR-S382 Stage B 启动

全13失败触发条件已独立与主线确认，主线review/drycheck通过。组合预注册/计划commit `2e8e590` 早于EDA；session49554 timeout1200 s正式运行最多12个组合，首层074+098、054+098、098+111，严格主门与失败预算规则不变。


### 2026-11-13 RECOVERY-REPAIR-S382-FORWARD-STAGE-C

- **状态**：CONFIG_PLANNED / NOT_RUN，等待实际 `FORWARD_PREREGISTRATION` / PLAN / driver 固化审阅提交，不表示预注册文件已核验。
- **用途**：独立强简单baseline与可行域探针，不是Stage B额外预算，也不称新机制。
- **配置**：同CONTROL起点，分别只实施原13中的1个回退（restored集合为其它12）；共13独立physical臂、全量无早停，不另增动作集。
- **固定门**：WNS/TNS/hold相对CONTROL严格非劣1e-6ns、hold>=0、面积正节省、既有physical/log/DRV/SEC验收边界；继承原样driver/audit，未知失败先归因。
- **前置**：主线完成独立预注册、plan、run_forward并审阅/commit后才执行；记录端收到具体文件后实读补充身份。


#### Stage B 完成 / Stage C 实际预注册核验（2026-11-13）

Stage B 12/12 有效且 strict 全失败，主线rc0并独立核验一致，COMBINATION_SUMMARY已冻结；预算耗尽，不暗增组合。记录端实际打开 `FORWARD_PREREGISTRATION.md` 与 `FORWARD_PLAN.json`：Stage C sorted-instance顺序全13，从CONTROL仅回退一项、禁止累积/有利早停；零面积 `_074_` 仍保诊断但不可晋级。最大13新增physical独立记账。物理driver仅plan文件名变化、full-structure auditor不变；route900s/STA300s/每subprocess1530s、失败停止归因不自动重试。全13后在面积正节省且strict合格点中选面积收益最大者（同值按arm名）做CONTROL完整二态SEC，独立证据审查后才接受。四文件drycheck已通过，尚待独立审核与主线commit再执行。原有完整约束/多corner/多电路限制保留。


#### Stage C 启动与零面积动作修正

独立review通过，commit `8e031f8`（前序 `7cb2bd4`）固化后才启动。零面积诊断动作实际为 `_074_/_077_/_081_` 三个，已在最终PLAN明确，不能沿用先前仅提074的口径。最终PLAN SHA `be04334ca8c8ffe5ffea951ded2ce8fe8f856fa2c7ea1cca01770fae2997eaa1`。session50740、timeout1200s、日志scratch/recovery_forward.log，独立13臂完整执行，无早停。


### 2026-11-13 RECOVERY-REPAIR-S382-PATH-STAGE-D

- **状态**：PREPARATION / NOT_RUN，预注册及runner准备中，未开始EDA。
- **固定对象**：Stage B实测TNS亏损最小的 `COMBO_054_074_093_098_111`；从该同一base分别额外提升 `_057_`、`_083_`、`rebuffer1` 中一个，不累积，总3独立physical。依据为已实际读取Liberty的函数/端口与路径诊断，非新颖性证明。
- **目标/门**：尝试以小面积代价补偿多端点损失，沿用WNS/TNS/hold全非劣、正面积节省及完整既定证据门，不改容差。
- **前置**：Stage C全13完成；新预注册/plan/runner审阅和commit后才允许启动。当前不消耗Stage B/C预算，不把准备候选算成运行结果。


#### Stage C 全矩阵完成与 SEC 启动

主线确认全13完成、wrapper380s，独立审查通过，唯一strict候选FORWARD__096_。按预注册选定该终点启动SEC session91025 timeout240s，完整模型102功能实例（含21FF）；实际proof结果待回报。Stage D drycheck已满足all13_valid，但仍待独立review/commit，尚未运行。


#### Stage D 预注册实查与正式启动

记录端实际打开 JOINT_PREREGISTRATION：三臂JOINT_057/083/REBUFFER1，固定B诊断base目标，分别1个upsize，最终各8个原downsize+1个新upsize；每次仍从相同输入ODB构造全目标后重布线/提取，不复用B布线或旧寄生作为终点。原13配方保持，3额外编辑语义显式，严格门不变。主线与独立评审通过、五文件commit `8dd39bb` 后启动session33049 timeout600s，scratch/recovery_joint.log，独立预算3，全部valid臂运行完不早停。之后最大面积strict点须SEC/独立审查；这是额外预算探索，不能据此主张等预算超过Stage C。

Stage C选定096已完成SEC：101proven/0unproven，receipt pass、sources unchanged、102实例含21FF；prover3.859s、wrapper10s。其局部严格物理/模型域等价通过不代表完整signoff或机制新颖性。


#### Stage D producer结束 / 本轮计数（等待独立验收）

三臂92s wrapper完成、主线实读JOINT_RECEIPT，均有效strict失败：057省2.378121%而三指标退化；083省2.378121%、WNS改善但TNS/hold退化；buf8省2.140309%而三指标退化。无SEC候选；D独立审核与路径归因待收齐。当前本轮总计A13+B12+C13+D3=41route、82终点STA，另2次路径STA。唯一C096可行且SEC通过，不能以D较大面积但不合门点代替它；阶段未最终封存。


#### A–D独立验收完成（2026-11-13）

JOINT_REVIEW确认D全3有效strict失败。FORWARD_ACCEPTANCE.json `e7d217e8976f79c06724111b5850d64daa0d88b0b913454b76dadfc50ca9b9dd` 接受唯一096局部baseline；SEC39种cell模型/102功能含21FF/3026零pin tap投影，101proven0unproven、源不变。D3route6STA、job87.063s/wrapper92s；A–D41candidate route82endpointSTA，另2诊断STA及SEC分开记。独立验收完成不等同创新性或完整signoff。


#### RECOVERY-REPAIR-S382 A–D 阶段结案（2026-11-13）

**状态：STAGE_CLOSED / ACCEPTED_LOCAL_BASELINE_ONLY；研究目标未完成。** 记录端实际读取REPORT.md与FINAL_RESULTS.json；根summarize_study逐项重审41个冻结row全部一致，postcheck确认5个工具及RCX/setRC哈希未变。A13/B12/C13/D3均有效，strict通过计数0/0/1/0；总41route、82endpointSTA、2pathdiagSTA、1SEC。逐阶段job秒数386.312/344.641/373.592/87.063，共享主机不作独占benchmark。

唯一接受FORWARD__096_：nor4_2→nor4_1，面积1052.2592→1046.0032（−6.256，−0.594530321046%），propagated WNS+0.0017147394615336ns、TNS+0.004840851ns、hold0；完整二态SEC101/0及独立接受回执齐。A/B/D的较高面积下降均未过严格门，不作有效收益。路径归因只读完成，未新增EDA。

四阶段是逐步观察后分别登记的预算，不包装成事先单一算法；局部可行baseline不证明联合机制、等预算优越、跨设计泛化或完整signoff。结果/失败/成本与边界以RESULTS.csv、FINAL_RESULTS.json、REPORT及各冻结summary/review为准。OI-082/084/085/086等继续open，生产算法/冻结论文未改。主线继续封ARTIFACT_MANIFEST与提交/推送；本登记不预报其成功。


### 2026-11-13 STRICT-AREA-SEARCH-S382

- **状态**：PREPARING / NOT_RUN，等待主线设计与预注册独立审查。
- **起点**：已接受 `_096_` 固定seed，另9个正面积动作分别构成双动作星形邻域；新证据包 `strict_area_search_20261113`，旧封存包只读。
- **比较**：事前冻结面积优先与物理风险排序，同9候选、同验证预算；全9物理点无早停，以k=1/3/6/9前缀比较实际可接受面积。预测只排序不接受。
- **门**：沿用相对Resizer CONTROL的propagated WNS/TNS/hold非劣1e-6ns数值容差、hold>=0、正面积、既有物理/证据与最终SEC门；不扩大容差。
- **边界**：当前无EDA，seed为既有证据不重复计新实验；局部排序是否有效待检，不称创新或泛化已成立。


#### STRICT-AREA-SEARCH-S382 运行启动（2026-11-13）

**状态：RUNNING。** 主线根preflight及Path.open拒读旧包守卫通过，独立预审通过；协议/代码先commit `3e70243` 后启动session60904，外层1860s/内层batch1800s，日志scratch/strict_area_search.log，PLAN SHA `2efbac2bfaf603fd2814e1e1ba00e0c6254dc7e5aeaf1c314f3fe169b5fcf45e`。

记录端实际打开PREREGISTRATION确认：9额外动作052/054/055/079/093/098/102/111/113分别与096同CONTROL ODB构造双动作，不以seed routed ODB累积；lexical测全9/18STA，两排序共享池。k3主比较，k1/6/9及完整前缀次要，k9同终点是自检而非优势。风险预测Mseed+Mj−Mcontrol只排序；actual gate固定CONTROL，允许既有slack margin被使用但不改参考到seed；严格三时序与完整证据门不变。每前缀最大实际saving单调、全失败exact seed fallback、只最优新增点最终SEC。历史13singleton与更广41route/seedproof成本单列，非端到端等成本或独立9电路统计。


### 2026-11-13 STRICT-AREA-SEARCH-S382-VARIANT

- **状态**：PREPARED / NOT_RUN；记录端实读VARIANT_PREREGISTRATION。独立2route/4STA预算，九点全valid+独立审阅+commit后才执行，不改九候选池/排名/预算。
- **对象**：VARIANT_054_2仅054 or3b_4→or3b_2；VARIANT_096_054_2同时096 nor4_2→nor4_1及054→or3b_2，从同CONTROL ODB独立构造。与已登记054→1的单点/双点等面积比较（节省2.5024/8.7584），检验历史rollback遗漏等面积库目标。
- **门/纪律**：沿用严格WNS/TNS/hold对CONTROL、面积/hold绝对可行/支持DRC及配置DRV/结构/SHA门；完整两臂、不有利早停，route900/STA300/child1530/batch1800秒，失败占预算停归因。recipe仅显式适配054 target，原历史recipe不改。全两例后新strict且优于seed者才SEC，不重生成端点。
- **界限**：无FF/clock改动、不补SDC、不放宽时序，结果不进入九点排序重放；不是纯弧因果隔离或新优化器证明，失败不否定全部52遗漏目标。


#### STRICT-AREA-SEARCH-S382 九点实测/独立验收结果

9/9证据有效，strict0；9route/18STA，runner373.578s/jobs372.829s，外包装另计。INDEPENDENT_AUDIT.json/INDEPENDENT_REVIEW.md与independent_check.py逐项核验，两冻结排序所有prefix均exact seed6.256，无k3优势、无新增严格终点；未重做seedSEC。该结果限原9个正面积rollback动作的固定seed星形邻域，不代表已审计的52遗漏候选无效。

variant独立实现预审通过但文字判据须先澄清：单点仅省2.5024<seed6.256，作为等面积target诊断；pair省8.7584才有严格超seed的可检验空间。尚未variant运行。


#### STRICT-AREA-SEARCH-S382-VARIANT 正式启动

执行前已修正预注册角色：single仅等面积target时序对照，only pair可能严格超seed。commit `37fc6e3` 与 `145146a` 均先于EDA，最终VARIANT_PLAN SHA `e600cd53f9899d179152d6c84c0cc84476a96998f7e4f117d7f1b4fc4772c7f7`；根drycheck与独立实现review通过后启动session62902，外1860/内1800s，scratch/strict_area_variants.log。两臂RUNNING，独立2route预算；旧plan/prereg版本Git+qa留存，未在旧版本执行EDA。


#### STRICT-AREA-SEARCH-S382-VARIANT 独立验收结果

2/2证据有效、strict0，独立checker/JSON/REVIEW已产出；2route/4STA，runner55.484s/jobs55.375s。相对CONTROL，两臂Δsetup均−0.034445057917ns、Δhold均−0.001212918654ns，TNS单点−0.286940575ns、双点−0.282325745ns。与各自同面积_1目标比较，setup/TNS/hold均更差。首条reported critical path转为DFF12→DFF3且经过054/X(or3b2)，只作路径观察，不称单弧因果。exactseed继续回退、无新增SEC，九例冻结summary未变；两中间档具体目标失败，不否定全部52遗漏候选。


#### STRICT-AREA-SEARCH-S382 + VARIANT 阶段结案（2026-11-13）

**状态：STAGE_CLOSED / NO_NEW_STRICT_ENDPOINT。** 记录端已实际打开最终REPORT：9+2全部证据有效、strict0；新增11route/22endpointSTA/0SEC，旧exact seed复制校验复用、不重路由。九点job372.829s/runner373.578s/wrapper383s，两variant job55.375s/runner55.484s/wrapper61s，共享主机不作独占性能比较。k3主比较及全部prefix两策略均seed6.256，无排序优势。

九点固定seed邻域扩展假设被本矩阵否证；两等面积中间档均比_1目标三时序更差。静态62候选/33实例与旧覆盖10/62只说明生成范围缺口，不表示收益。下一阶段转完整候选生成/约束覆盖/强基线，不继续在已无改进九点池改排序叙事；旧13标签成本属前轮41route子集，不重复累计。47证据层测试通过，生产/论文未改，旧封存包只读。封manifest及commit/push由主线继续，登记不预告其成功。


### 2026-11-13 LIBRARY-AREA-SEARCH-S382

- **状态**：PREPARING / NOT_RUN；新包library_area_search_20261113，等待生成器核验计数与实际预注册审核。
- **候选域**：完整静态候选中的未测组合逻辑替换，拟25项；排除历史10正面积目标与已测054→2，seq/clock不改。最终实例/目标清单和数量以生成器与独立审查一致为准。
- **协议**：CONTROL起点每目标独立单点，固定lex全量、无有利早停，拟25route/50STA；保持完整结构/SHA、新布线/提取、propagated WNS/TNS/hold严格非劣、正面积/hold可行及既有物理门。通过且优于seed的最大收益点须SEC与独立接受。
- **边界**：尚未EDA，不将25静态候选写成25实验或收益；生产/旧证据不改。用户授权论文完善，但科学结论更新先依证据映射及验收，不擅改冻结数字。


### 2026-11-13 LIBRARY-AREA-CONSTRAINT-AUDIT

- **状态**：PRE_REGISTERED，记录端已实读constraint_audit/PREREGISTRATION；预注册/MANIFEST/两copy端点由主线commit `07c6cf2` 先固化。
- **范围**：CONTROL与已接受FORWARD096精确副本各一次readonly STA，保留0.5ns与propagated设置，仅加installed-supported check_setup -verbose / report_checks -unconstrained；不新增IO delay/load/transition，不修改接受门，无routing。
- **计数/超时**：2diagnostic STA，与拟25candidate/50endpoint STA分开；每次120s、串行总300s，失败停归因。保raw stdout/stderr、source/copy/Tcl/tool SHA及rc；复现指标不是新独立科学样本。
- **边界**：审计缺失IO规范/clock/unconstrained端点等，不凭空补规格；完整signoff仍未建立。


### 2026-11-13 WNS-PRIMARY-POLICY-CHANGE

- **状态**：POLICY_PREPARATION / NO_NEW_PHYSICAL_RUN；用户新指令改变接受目标。
- **新门**：propagated WNS/hold相对CONTROL非退化1e-6ns、hold>=0及既有证据/物理硬门；面积收益首选，TNS报告且用于同面积次级择优，不再hard拒绝。
- **首步**：新policy包隔离重筛既有actual物理端点，新增入选者必要SEC；不把重筛计为新route/STA，未宣称新数值结果。
- **历史与待运行**：旧WNS/TNS/hold strict矩阵与失败不改，论文需准确区分政策变更和证据变化。LIBRARY-AREA-SEARCH拟25新route在新政策定稿前不启动；约束诊断与新policy计数分别保留。


#### LIBRARY-AREA-SEARCH-S382 准备暂停点（用户新政策）

新WNS-primary规则定稿前暂停旧严格三硬门构建。已核静态25候选/11实例，233本地副本/443alias与未冻结PREREG草案；尚无PLAN/per-arm recipe/runner/新driver/新TDD，无EDA/SEC/commit。不是完成包，也不是运行中实验，后续计划需与新policy显式对齐。


#### LIBRARY-AREA-CONSTRAINT-AUDIT 完成

两端点各STA一次、均rc0，2diagnosticSTA/0route。CONTROL与096均3missing inputs CLR/FM/TEST，6missing outputs且6unconstrained endpoints GRN1/GRN2/RED1/RED2/YLW1/YLW2；clock/约束不变、旧WNS/hold复现。证据RESULTS.json/REPORT.md，不能据此宣称IO签核。新WNS-primary规则不改变此缺口，拟25candidate仍未执行。


### 2026-11-13 TIMING-BUDGET-POLICY-CHANGE

**状态：POLICY_PREPARATION / NO_NEW_RUN。** 用户授权首轮10ps WNS损失：WNS>=CONTROL−0.010ns+数值容差1e-6ns，TNS辅助；hold相对CONTROL非退化1e-6且hold>=0保持，其余证据/面积/SEC门不变。0/5/10ps对照以新timing_budget_20261113包承载；旧strict和wns_primary预注册/PLAN/RESCREEN只读，旧selectedSEC暂停等待重筛，不将新政策通过回填旧失败。尚未新筛选结果/SEC/route/STA。


#### TIMING-BUDGET 历史端点独立重筛（非新增物理运行）

52已审端点按0/5/10ps计6/15/19合格，最优分别COMBO054074098（3.6860879905%）与RESTORE074（5/10ps同4.399524375743%，ΔWNS−3.098077350ps、Δhold+3.577305119ps、ΔTNS−231.982231ps）。新政策重判，尚待新package与SEC接受；0新增route/STA。原fullRECOVERY虽过10ps WNS仍不满足hold门，不接受。旧WNSprimary计划/helper保历史无SEC执行。


#### TIMING-BUDGET / LIBRARY准备阶段收束（2026-11-13）

**状态：PREPARATION_STOPPED / PENDING_CONTINUATION，非RUNNING。** 用户转为简要解释并清除长期goal，本轮不再新增POLICY/PLAN、不执行新SEC或25候选EDA。根与独立52端点重筛一致，5/10ps最优RESTORE__074_仅为待验证候选：area1005.9648/save4.399524375743162%，WNS差−0.0030980773502164993ns、hold差+0.003577305118795948ns、TNS差−0.231982231ns。未正式接受，待续SEC；重筛0route/0STA，约束诊断2STA单列。既有WNSprimary helper/PLAN保历史且无proof，25proposal只到准备停点。


### 2026-11-13 TIMING-BUDGET-EXECUTION-PREPARATION

**状态：PREPARING。** 用户授权继续。配置0/5/10/20ps历史端点分析，固定W_R/A_R/H_R、TNS辅助、hold与证据门不变；52历史重筛为0新EDA，纯策略/oracle测试不计物理收益。选中点SEC拟180s/外240s，待主线POLICY/PLAN/SHA完成后实读登记。另有budget_core纯策略/有限组合TDD与A0/CTS面积归因并行，不启动25候选物理批次。


#### TIMING-BUDGET POLICY/历史分析固化（SEC尚待注册）

记录端实际读POLICY.json、RESCREEN.json：POLICY SHA `78621e219112254d521d295ccbcdd88338852d23dc8db41b5f968cc15205a421`，固定CONTROL、默认10ps，0/5/10/20ps对照，硬门WNS>=W_R−B−1e-6、hold>=H_R−1e-6且>=0；目标面积，次序TNS/WNS/hold/lexical辅助。52历史候选重筛v3 rc0，独立旧审计重跑rc0，0route/0STA。各档eligible6/15/19/21；0ps选COMBO054074098省3.686087990487513%，5/10/20ps同选RESTORE074省4.399524375743162%，均pending SEC，不作新的搜索成效。proof180/wrapper240已写政策，具体SEC PLAN待下一步。


#### TIMING-BUDGET 选中端点SEC运行前登记

记录端已实际打开新PLAN.json：仅RESTORE__074_，固定10ps政策、原物理端点重用，不重布线。PLAN SHA `a984d47d53e994d2b01b6679e60ad5601e4c72cf369225036601ce8201bafba9`；helper SHA `78eee438eac5c570837cb655900610fd829d6a929932b0b6d2d183645b2e6c01`，help已通过。proof timeout180s、外wrapper240s，完整模型/零pin tap投影及source/copy SHA按既有受控证明链。状态PREPARED / NOT_PROVED，待独立准入与主线commit后才执行；预计只新增1SEC、0route/0STA，实际次数以后验收据为准。


#### TIMING-BUDGET SEC RUNNING

运行前注册commit `c5a4d05` 与独立准入均完成，唯一RESTORE074现进入SEC（180/240s），无新route/STA。状态RUNNING仅指该证明，25候选EDA仍未运行。


#### TIMING-BUDGET 选中端点限定接受完成

RESTORE074在用户10ps/现有约束域获根与独立接受，ACCEPTANCE SHA2de50d475fec765bb0b8729addf75a43d8e929bdcf06b04b752d4fb6eafdff75。全SEC SHA/102实例含21FF/41模型/101proven0unproven通过，精确历史端点未重布线，新增1SEC、0route/0STA。s382净新增面积回收28.90625%同阶段分母独立绑定，WNS损3.098077ps、hold增3.577305ps、TNS损231.982231ps完整报告；新政策接受非旧strict通过、非新算法收益。core工程全回归及在线物理接入另行待办。


#### TIMING-BUDGET 工程完整回归完成

v2正确packaged Yosys镜像环境：1147passed/156subtests，pytest128.96s、wrapper132s/rc0，code全py SHA前后同。v1错误环境5failed/1142passed原件保留，未改生产代码只修测试环境。5 tracked fixture备份恢复、44新生成文件隔离，FIXTURE_CLEANUP留痕。历史52四档core一致性和CLI预算合法性通过；均不增加route/STA或证明在线物理收益。实际科学新增仍1SEC/0route/0STA，约束诊断2STA另计。


#### TIMING-BUDGET 本轮阶段核验收尾

工程VERIFICATION包含1147/156全套、34专用、compile/CLI4项/真实52pool一致；旧624+398工件SHA未变、233准备副本来源一致。record检查rc0但4obsolete警告归OI-081，25候选草案SUPERSEDED/未运行。阶段成果为历史预算重筛+1SEC接受及纯核心工程门，不作prospective搜索收益；online evaluator/完整约束/跨设计继续pending。科学新route/STA=0，约束诊断2STA单列。最终包封存与commit/push由主线随后执行，本记录不宣称已推送。


### 2026-11-13 OVERALL-RELATED-WORK-RESEARCH

**类型：定向总体机制调研/只读架构审查，非科学运行、非系统综述。** 证据入口overall_related_work_20261113/{REPORT.md,SOURCES.json,MECHANISM_AUDIT.md,LITERATURE_NOTES.md}由主线汇合；记录端实读scratch完整机制审计。比较区域/候选、动作与交互、有限验证成本、多精度STA物理反馈、接受证明链及整体近邻。0新EDA/0STA/0route/0SEC，未改生产/稿件/封存证据。

当前结论为三条实现链未统一，预算/多动作/反馈不是独创性证据；待检假设是完整候选+交互选择在同实际物理验证成本下改善预算内净面积回收。下一实验须在强简单/原生基线、组件消融与约束/跨设计要求下重新登记，不由本研究条目自动启动。OI-086继续open，未预报提交/推送。


### 2026-11-13 ~ 2026-11-16 ITC99-CROSS-DESIGN-SELECTIVE-RECOVERY

- **状态**：DIAGNOSTIC_COMPLETED（16电路已评估：14电路完成固定SPEF选择性恢复，b14 Resizer 0修改，b22 359修改单步线性回滚在verify_143处600s超时未闭合；b17–b21合成完成但Resizer详细布线超30–56min未完成）。
- **定义与证据路径**：`experiments/20261113_itc99_recovery/`（含 `recovered/b01..b10`、`arms/Recovery/b05,b11,b12,b13`、`arms/Resizer/b14,b15,b22`）与 `project_docs/evidence/itc99_recovery_20261113/REPORT.md`。
- **配置与口径边界**：`code/scripts/recover_area.py`（`max_degradation=0.015ns, safety_factor=1.5`），复用Resizer输出 `routed.spef` 与理想时钟 `sta_routed`，`\w+` 同名实例解析（未含escaped DFF分母修正，未重合法化/重布线/重提SPEF，未跑最终SEC）。14完成电路回退 501/612 (81.9%)，回收面积 3026.66/12635.87 µm²（加权23.95%，算术均值18.95%），ΔWNS ∈ [−0.0115, +0.0162] ns。


### 2026-11-20 POSTROUTE-RECOVERY-AND-ONLINE-SEARCH

- **状态**：COMPLETED（project_docs/evidence/postroute_recovery_20261120/{REPORT.md,SUMMARY.json}）。
- **ISCAS89 8例真实重布线 + SEC**：全 8 例执行重合法化+15轮详细布线（DRC=0）+新RCX+传播STA；NATIVE (-recover_power 100) 8/8 为 0%；我方 6/8 有效回收（1.55%–4.68% 总面积降幅，6/6 SEC PASS），s953 二分隔离 14/23 降 4.68% 且 WNS +17.26 ps，s820 回退 CONTROL。
- **s382 在线 ounded_search**：ONLINE_007（_096_ + rebuffer1），−1.31% 面积、ΔWNS −7.028 ps、Δhold 0.000 ps、SEC 101/0 PASS。
- **22 转折门隔离**：10 次验证 STA 隔离 _160630_，356/359 回收 3024.15 µm²（33.1%，ΔWNS +0.0011 ns，固定 SPEF 口径）。


### 2026-11-20 ITC99-POSTROUTE-AND-ONLINE-ABLATION

- **状态**：COMPLETED（汇总于 project_docs/evidence/postroute_recovery_20261120/{REPORT.md,SUMMARY.json}）。
- **ITC-99 4例重布线**：05 通过 =10\text{ ps}$ + SEC（−5.04%、+8.63ps）；04/b11/b12 超 10ps；NATIVE 4/4 为 0%。
- **s641/s953 同预算消融（udget=12）**：s641 Sequential Greedy 22.52 µm² > bounded_search 15.01 µm²；s953 16.27 vs 16.27 µm²（RUN_012 实证动作补偿）。
- **s382 IO 审计（OI-082）**：setup WNS 不变，ONLINE_007 TNS 优于 CONTROL。


### 2026-11-23 V22-ASAP7-SEC-HANDOFF-REPLAY

- **状态**：REGISTERED。核验 v22 所引用的既有 `eval_016` 与 `eval_059` 两态 Yosys SEC。历史 `sec_eval_016.log`、`sec_eval_059.log` 各仅 1 字节，需带完整 stdout 和退出码重放。
- **配置**：Yosys `0.70+255`（`72b0054f0`），Ubuntu，本地 `main=bd44e1994cf157d972dfcaf539862273e4e27a02`。使用 `/home/toylog/faeco_asap7_aes/` 下既有 `sec_eval_{016,059}.ys`、`asap7_models.v`、`control.v` 和对应 `evals/eval_{016,059}/opt.v`。既有脚本删 TAPCELL、flatten、`equiv_simple -undef`、`equiv_induct -undef`、`equiv_status -assert`。非静默执行，每端点独立限时 120 s。只重放形式验证，布线与 STA 次数均为 0。

- **状态**：COMPLETED（2/2 SEC PASS）。两条限时命令各约 25 s，退出码均为 0，均为 1252 proven / 0 unproven。完整非静默日志位于 `scratch/v22_handoff_sec_20261123/`。原始 1 字节日志已保留。本回放验证同一 CONTROL 与现有网表的两态等价，不含新布线、新 RCX 或 STA。

| 输入或日志 | SHA256 |
|---|---|
| WSL `asap7_models.v` | `8800783e51ed20a9cb666cb42723b00a8c979704b183d26697f9460f88165ff9` |
| WSL `control.v` | `87f0fc0ba6cf0f47aaee623ff32fa42db67b2bc748495d0114ac57ad2a641e94` |
| WSL `sec_eval_016.ys` | `286a80570295ae6229cabc2f78c85abb5c29455b4bcfc3a97ab7e271f1f197d8` |
| WSL `sec_eval_059.ys` | `165548e1db541f6aeade761f7eb22be8b3e9bb371c928c1738158858bea23c4e` |
| WSL `evals/eval_016/opt.v` | `c5a7a0b313c3aeaf79464202c8cadf6bb1d029dc52fa827a10c8255caa3800d0` |
| WSL `evals/eval_059/opt.v` | `541410f39257248953cba09792b68783b4ff12bbfc72e51f7b2680e8514b2fa7` |
| scratch `eval_016.log` | `a3e72288a649a2c2910d236e00ec6d52581ea4b48651c6ec3b979fdf67605a0e` |
| scratch `eval_059.log` | `9694fe779517f32e70a0439db7a10d5da59e7c695c190d374e3251464c2f713b` |


### 2026-11-23 SKY130-JOINT-B10-S713-S832

- **状态**：PREREGISTERED，未启动新 EDA，待既有 10 电路端点对齐。假设为至少一个电路在同一候选端点上实现正面积收益且通过四场景联合门。合格端点为零可否定本预算、候选空间和评测配置下的假设，工具失败与未完成单列。
- **版本与输入**：本地 v22 `bd44e1994cf157d972dfcaf539862273e4e27a02`。固定 `experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/{s713,s832}/routed.{def,v,spef}` 为各电路 CONTROL。四个参照值从同一原始 CONTROL 网表与 SPEF 重测。先以同一 OpenSTA 配置重测历史正收益 `s713/RUN_008`、`s832/RUN_009`（观察对照，与新搜索分开），另从冻结 DEF 和 LEF 各做一次零动作路线对照。
- **物理评估**：OpenROAD 26Q3，每电路 4 线程，重合法化、全量重布线、15 轮 DRT、新 RCX。每个候选的同一网表和 SPEF 分别执行时钟约束下的 TT、SS、FF 分析，以及 TT 显式 IO+OCV 分析。全部使用 CK 0.5 ns、传播时钟。IO+OCV 沿用 v21，输入及输出延迟 0.10 ns、输入转换时间 0.05 ns、输出负载 0.01 pF、early/late 降额 0.90/1.10。
- **联合接受门**：每一场景相对其 CONTROL 的 setup WNS 差值 ≥ −10.001 ps、绝对 hold ≥ 0 ps、hold 差值 ≥ −0.001 ps。面积必须降低、DRC 必须为零，最终端点必须通过非空全网表两态 SEC。TNS 作辅助指标。单列相对 CONTROL 诊断，诊断只撤去 IO+OCV 的非负 hold 硬门，仍报告残留绝对 hold，不计入严格联合通过。
- **搜索及限时**：现有兼容候选枚举，每实例最多一动作，安全驱动优先排序，3 动作微批次与二分。零动作对照外每电路至多 10 次新物理评估，最多并行 2 电路。OpenROAD、每场景 STA、SEC 分别限时 180、60、180 s，每电路累计墙钟上限 2500 s。
- **产物**：`project_docs/evidence/sky130_joint_constraints_20261123/` 记录输入指纹、命令、Tcl、动作、对照、度量及验收回执，`scratch/sky130_joint_constraints_20261123/` 留存本轮物理原始工件与日志。按端点绑定并计数，区分历史端点重测、新路线、STA、SEC 与失败/超时。


- **状态**：RUNNING。先完成 `project_docs/evidence/sky130_joint_constraints_20261123/{ENDPOINTS.md,ENDPOINTS.json}` 端点对齐，再启动两电路。运行入口为同目录 `run_joint.py`（SHA256 `79794439279c2a64431a707af0021abaaE368adde9328d23418331e3faf3df52`，大小写无关）；两份 `scratch/sky130_joint_constraints_20261123/{s713,s832}/config.json` 已冻结实际输入、工具资产指纹和有序候选（18、23 个）。四场景 STA 用 build26 OpenROAD 源树测试库，TT 与 IO+OCV 使用同一 TT 库；OpenROAD 物理步骤沿用 ORFS 平台 TT。SEC 沿用历史 `/usr/bin/yosys` 0.33。
- **先验对照重测**：本轮按同一固定 V/SPEF 分别重测各电路四场景的 CONTROL 与历史正收益端点。两个 CONTROL 的 IO+OCV 绝对 hold 为 `−98.219/−75.316 ps`。`s713/RUN_008` 的 IO+OCV setup 差值为 `+9.917 ps`，但 IO+OCV 绝对 hold `−98.116 ps`、FF hold 差值 `−3.884 ps`；`s832/RUN_009` 的 IO+OCV setup 差值为 `−36.161 ps`、绝对 hold `−74.524 ps`。这两条是各 8 次独立 STA 的历史观察对照，登记在当前配置下复测的差值，不沿用 v21 不同 CONTROL 的数值。原始 `{CONTROL,HISTORIC_TT}/metrics.json` 随每电路运行目录留存。


- **RUNNING 更新与技术重试预注册**：`s713` 首轮 `RUN_001/RUN_003/RUN_004` 在 OpenROAD `replace_cell` 阶段退出，`STA-0125` 报 `\DFF_0/rebuffer1` 不存在。实查固定 CONTROL 网表第 236 行的 Verilog 转义名为 `\DFF_0/rebuffer1`，DEF 第 220 行精确实例名为 `DFF_0/rebuffer1`，原 master 同为 `sky130_fd_sc_hd__buf_4`。三个错误均保留为工具输入身份故障，单列计数。预注册在独立 `_retry` 目录按同一 `s713` 预算、原物理输入、同排序动作及验收条件完整重试，唯一变更是生成物理替换命令时去掉一个 Verilog 转义前缀，并验证 DEF 的精确实例名与原 master。等原 `s713` 运行结束再启动重试，同时运行最多两个电路。无改动 `s832` 运行。


- **技术重试已启动**：修正驱动 SHA256 `ac6de1d3940baf66dbabbf0188afbd8049a91612fd82000b4736de2f59f213b5`。离线前置核验逐一绑定 `s713` 的 18 个与 `s832` 的 23 个候选到 DEF 实例和原 master。重试配置为 `scratch/sky130_joint_constraints_20261123/s713_retry/config.json`，SHA256 `85208460c30fddad9e523e480303bf6c1755f40aa00e6bcca751b317556ae6e5`。首次驱动保存在 `scratch/sky130_joint_constraints_20261123/run_joint_initial.py`。初跑 `s713` 10 次候选调用中 7 次走完物理流，3 次替换前置失败。零动作对照另 1 次，原始结果全部保留。


- **第二次身份故障与恢复预注册**：`s713_retry/RUN_001` 的 OpenROAD 返回码为 0，DRC 为 0，新 DEF 第 220 行和网表均证实 `DFF_0/rebuffer1` 已替换为 `sky130_fd_sc_hd__buf_1`，但替换期望表仍以带前缀的原始动作名为键，Verilog Reader 则返回规范名，导致身份门拒绝并跳过 STA。保留初跑与第一次技术重试，统一命令、期望 master 表和读回数据使用的 DEF/Verilog 规范实例身份。新独立 `s713` 最终评测以同一固定输入、候选、10 次调用预算与门限运行。仅在动作元组、输入与工具资产指纹、原路线产物哈希一致时复用第一次重试已完成的路线，对缺失的四场景 STA 独立补测。动作不同或路线不全时运行新物理评估。分开记录实际新路线、复用路线、实际物理评估和 STA。


- **身份修复回读通过**：`s713_replay/config.json` SHA256 `4e20582324ebf4fc196357b55df5e2589f6ffba41c0868054f0eb087ac05c435`，使用驱动 SHA256 `fe296122f6defb45a824c25ba8aedf33e671e09ebdda77e1629ae72b409cd42e`。回放首个候选复用 `s713_retry/RUN_001` 的已完成路线，读回 master 一致，DRC=0，四景 STA 全部有效。IO+OCV hold 绝对 `−98.719 ps`，低于同源 CONTROL `−98.219 ps`，由真实时序门拒收。OI-088 限定修复验证通过。
- **`s832` 验证完成**：1 次无变更控制 + 10 次新候选路线均完成且 DRC=0，共 52 次实际独立 STA（CONTROL 与历史重测 8、零动作对照 4、候选 40），1 次 SEC。严格门无交付，十个候选的 IO+OCV 绝对 hold 均为负。相对诊断端点 `RUN_005` 把 `rebuffer10` 降至 `buf_1`，回收 `3.7536 µm²`（`0.322%`），IO+OCV 的 setup、hold 差值为 `+6.404/+0.801 ps`，绝对 hold `−74.515 ps`，SEC `162/0`。仅供相对诊断。无变更物理对照、搜索与 SEC 墙钟合计 `436.375 s`。


- **状态** COMPLETED，两个最终运行退出码均为 0。合格结果以 `s713_replay`、`s832` 为准。两例各 10 个候选、1 个零动作对照，分别执行 52 次 STA（参照与历史点各四景、对照四景、候选四景）。`s713_replay` 全部 11 条路线均由第一次技术重试的动作、输入及产物指纹匹配复用，执行 0 条新路线、0 SEC；10 个候选通过物理身份门与 DRC，IO+OCV 绝对 hold 为 `−99.035 至 −98.036 ps`，严格及相对诊断均无端点。s832 的相对诊断结果见上一条，两例合计严格接受 `0/2`。
- **计数与追溯**：初跑 `s713` 11 次物理调用，8 条完成，40 次 STA。技术重试 `s713_retry` 11 次物理调用全部完成，3 条因身份表错误跳过 STA，共 40 次 STA。最终回放独立 STA 52 次，不新增物理调用。`s832` 11 次物理调用全部完成，52 次 STA 及 1 次 SEC。汇总全阶段 33 次物理调用、30 条完成路线、184 次 STA、1 次 SEC，另有最终 s713 的 11 条路由产物复用。最终证据集为 20 个候选、2 个零动作对照、104 次 STA、1 次 SEC，工程失败的初跑不进入候选可行率。
- **最终本机收据**：`scratch/sky130_joint_constraints_20261123/s713_replay/summary.json` SHA256 `8b727b3f0e6559deb5e71bb39d9292babcb1e1643cfac48e42292f769dd4a180`；`scratch/sky130_joint_constraints_20261123/s832/summary.json` SHA256 `072294ba7b0a73ab6eceb2b7fac26e3b94fd504d680c83e2d8150f3b3f1fbe3d`。可携带证据目录为 `project_docs/evidence/sky130_joint_constraints_20261123/`。


### 2026-11-23 ASAP7-GCD-CONTROL-3VIEW-SMOKE

- **状态** PREREGISTERED。目标为确认既有 ASAP7 GCD 详细布线起点能在三场景读取原约束并得到 setup、hold 测量。此项为资格冒烟，范围限于开发用 GCD 的既有 CONTROL。
- 固定输入为 WSL `/home/toylog/rseco_timing/adaptive_20261120/rcx_smoke/results/asap7/gcd/base/6_final.{odb,sdc,spef,v,def}`。同一运行的 `logs/asap7/gcd/base/5_2_route.json` 报告 `detailedroute__route__drc_errors=0`。保留源 SDC 的 310 ps 传播 core clock、310 ps 虚拟 I/O 时钟和 62 ps 输入/输出延迟，三场景共用一份原 SPEF。因此比较维度为 Liberty PVT，寄生口径固定。
- 固定 WSL OpenROAD 26Q3 `/home/toylog/faeco_eda/or26Q3/bin/openroad`。RVT FF、TT、SS 三视图分别独立启动 OpenROAD，每视图明确载入 AO、INVBUF、OA、SIMPLE_211120、SEQ 五套 NLDM Liberty。原输入及布线产物只读。每视图限时 30 s，整体限时 100 s，共至多 3 次 STA，物理布线、RCX、SEC 调用均为零。
- 要求既有 DRC 为零，三视图均有有效、可测的 setup 与 hold，且每个视图绝对 hold 非负才能通过本次严格冒烟。setup 可保留负 slack。输出落在 `project_docs/evidence/tcad_preflight_20261123/`。本项不提供算法比较或留出规模验证。

- **工具准备事件** 初次命令在 SHA256 输入预检停止。组装 Liberty 文件名时遗漏 `asap7sc7p5t_` 前缀，本次调用未进入 OpenROAD，实测计数为 0 STA。根据原 ORFS 文件清单和 `6_report.log` 对正确库名逐一定位，按原登记的 RVT 视图与五组 Liberty 启动后续复测。

- **工具兼容性与复测预案** OpenROAD 26Q3 在 FF 场景的 `read_db` 阶段退出。错误为原 ODB schema `0.142` 新于读器的 `0.134`，保留 `FF.log`，至此实际测完 0 次 STA。优先找回并固定 ORFS 产出该 ODB 的 OpenROAD 二进制，或使用 OpenSTA 3.1.0 读取同一已固定的 `6_final.v/.sdc/.spef` 及按场景列明的原五组 RVT 库。ODB、DEF 和 DRC 仍与评测端点以哈希绑定，不转换或修改原件。已有生产器 FF 读数只用来做复现差异核对，原联合门、预算及完整三视图要求保持。


- **状态** COMPLETED。使用 OpenSTA 3.1.0，直接读取已固定的 `6_final.v/.sdc/.spef`，每场景使用同一原 SPEF 和登记的五组 RVT NLDM Liberty。三进程均 rc 0，分别用时 1.766、1.578、1.531 s。FF setup/hold `−37.960829/+41.599637 ps`，TT `−166.709424/+59.198008 ps`，SS `−401.929379/+43.915302 ps`。FF 与原生产器 `6_report.json` 的 `−37.9608/+41.5996 ps` 在后者精度下一致。三视图 hold 非负，控制件通过本次测量及 hold 门。实测计数 3 STA、0 新布线、0 RCX、0 SEC。无候选评估。
- [配置与输入指纹](tcad_preflight_20261123/CONFIG.json) SHA256 `bb1c84d59892f5dbab3da2eb9bf2ad294608bcd9067b6d66d42305930ee3eeab`，[结果及日志指纹](tcad_preflight_20261123/SUMMARY.json) SHA256 `8f57c80d4985edfce128c43f66404ace90cdc72f43ce7f557f0aadbdaa75b324`。ODB 读入诊断保存在同目录 `openroad26q3_odb_diagnostic/`。


### 2026-11-23 TCAD-IBEX-P0-P1-DEFAULT-SKY130HD-ASAP7

- **状态** PREREGISTERED。用户授权完整执行 Ibex 的 SKY130HD 与 ASAP7 P0/P1。每工艺先完成并验证原始 ORFS 基准 CONTROL，仅通过门控的起点可进入另行登记的三臂对照。实验起点 FAECO Git `c4b9fa37`。
- **固定源码与工具** WSL Ubuntu `/home/toylog/faeco_eda/orfs`，Git `da8f092a02a8e75658cc3100691aabff05f35629`。两个普通 `base` 任务分别使用 `flow/designs/{sky130hd,asap7}/ibex/config.mk` 及其原始 `constraint.sdc`。保留源设计配置及 SDC，保持源时钟、I/O 和保持时间门限。OpenROAD 为 Bazel 构建 `/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad`，SHA256 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。综合用 `/usr/local/bin/yosys` 与 slang。
- **执行边界** 各工艺 4 线程，整次构建外层限时 3600 s，最多并行 2 构建。WSL 原始运行目录为 `/home/toylog/faeco_tcad_ibex_20261123`，可携带记录为 `project_docs/evidence/tcad_ibex_20261123/`。需保存输入指纹、实际工具身份、命令、运行阶段日志及终点指纹。
- **CONTROL 资格** 要求 CTS、详细布线最终 DRC=0 与 RCX 完成，保留可绑定的终点及最终 SDC、SPEF。用同一物理终点和传播时钟量测 FF、TT、SS 的有效 setup/hold，并要求各视图绝对 hold ≥ 0。未完成的工艺、工具失败和真实不合格分别记录。此条只登记 CONTROL 资格，三臂候选评估另行冻结并登记。

- **源约束回读** 两工艺 `DESIGN_NAME=ibex_core`、核心端口 `clk_i`，各有同周期虚拟 I/O 时钟，按周期 20% 施加输入/输出延迟。SKY130HD 核心周期 10.0 ns、I/O 2.0 ns、两时钟的 latency 由源文件的 `set_clock_latency 1.095` 指定；ASAP7 周期 1000 ps、I/O 200 ps、对应 latency 参数 161.775 ps。ASAP7 `FLOW_VARIANT=base` 选原 `constraint.sdc`，另一个 `pos_slack` 变体不在本次登记内。
- **输入 SHA256** SKY130HD `config.mk`=`df322ddec0186a25c1dea64df013d4b08c7e083329b3713fc1672b8d6b8a28fe`、`constraint.sdc`=`2fb819cb8e9bcd2ff0fe825ed3f7d5a96ebfeea301d53c83bcf5225121255151`。ASAP7 `config.mk`=`9649449735e38750d087026c4cceee2cac3069f3f5529f1de9bd28293c3384ef`、`constraint.sdc`=`23e0ea9d7b72924fd06b07f012c77f44192c67fac92c215eece12dffb08b2346`。两工艺共用 `/usr/local/bin/yosys`，SHA256 `4f8e613d835c248c63f0e487fb956e1667b9291ef87f0514fffb4dc07878d379`。

- **状态** RUNNING。实查两个 WSL 限时进程分别为 SKY130HD PID 429 与 ASAP7 PID 1194，均对各自 `WORK_HOME` 的 `6_report.log` 目标执行 `make`，按登记使用 4 线程与 3600 s 超时。两边各自产出 `1_1_yosys_canonicalize.log`、`1_2_yosys.log` 并正在综合。


### 2026-11-23 TCAD-IBEX-P1-MATCHED-LOCAL-DRT-THREE-ARM

- **状态** 条件式预注册。候选尚未启动。每工艺须先有 `TCAD-IBEX-P0-P1-DEFAULT-SKY130HD-ASAP7` 的原始 CONTROL 合格收据，再绑定各自的冻结 SDC、ODB、DEF、Verilog 和 SPEF。每工艺各跑一次三臂共用的零动作对照，完成可重现核验和全网表两态 SEC 后启动候选对照。执行命令及零动作阈值另记。
- **三臂与预算** 相同功能兼容候选池和顺序、共同物理评估器、每臂最多 6 次。单门逐次、固定批次大小 3、FAECO 自适应微批次大小 3。每次均从该工艺的共同起点执行同一局部触线 DRT 和新 RCX，复用 B-011 路线内核，保留未触线的走线。按同次数预算和公共墙钟前缀报告，仅分析达标的净面积回收。零动作对照为共享成本。
- **判据** 每个候选在同一网表、SPEF 和原约束下回读三个 PVT 视图，setup 相对 CONTROL 的损失不超过 10 ps，绝对 hold 非负且相对 hold 差值在 0.001 ps 数值容差内不减。电气检查不得新增违规项，DRC=0，净面积须下降，最终交付为全网表两态 SEC 通过的端点。TNS 单列记录。
- **限时** 每个 DRT/RCX 调用上限 1500 s；每个 STA 视图限 180 s，SEC 内部限 180 s。每工艺布线用 4 线程。最终命令、并发和零动作阈值以启动前确认记录为准。
- **开发探针，单独计数** 主线已用等效/非等效小电路实查两态 SEC 分别为 `1/0`、`0/1`。SKY130HD 的异步触发器 SAT 模型用 `clk2fflogic` 规范化，初始综合网表自比为 `13517/0`。这些为 proof 工具探针，候选评估、面积结论及最终 SEC 另计。

- **SEC 技术预检补充** ASAP7 的 `1_2_yosys.v` 自比使用 Yosys 0.70+255、`clk2fflogic` 及五组 ASAP7 RVT TT Liberty，耗时 78.976 s，`17235/0`，rc 0。gold/gate 同一合成文件及 SHA256 `e7363135f0a23856ef3c11f4552b3ff0546435c14f58cf84a1b283b783994f85`，收据 `/tmp/ibex-sec-asapsynth-clock-self/receipt.json`。它证实工具模型可处理初步综合网表，正式 P1 验收另绑定实际物理输入和候选。

- **物理评估器及零动作启动门** 导入各 PDK 资格通过的 `6_final.odb` 与同一 ORFS 运行的原 `route.guide`，指纹入配置。清理换门直连信号网线并保留原放置，DRT 迭代上限 64，沿用生产器默认种子（无 `-or_seed`）。记录工具自动改变的邻近未触线路由，不将几何变化本身增列为拒绝门。两工艺各自独立资格通过后，可分别开始零动作，随后按本工艺共同起点比较三臂。
- **零动作验收与开发探针** 零动作对照单列，使用和候选相同的三视图 setup 10 ps 限、绝对 hold 非负、hold 相对非退化（0.001 ps 容差）、无新增电气违规、DRC=0、全网表 SEC，另外保留网表、位置和路由几何变化记录。ASAP7 GCD 开发模型零动作重布线收敛 DRC=0 并完成 RCX，`Δsetup=+0.028560 ps`、`Δhold=+0.000323 ps`，两条时钟网几何改变且无组件移动。开发探针和 Ibex 验收分账。


- **ASAP7 资格与 P1 零动作启动** `asap7_control/CONTROL.json` 为 `hold_qualified`，SHA256 `eee48dc4991206dcec1cf0e78d46356fdb1fb7accf19ccf9b786c8220007d137`。明确 DRC=0、原 SDC 的 1000 ps 周期和 200 ps I/O，三视图共用原 SPEF。独立 STA 的 FF/TT/SS setup/hold 顺序为 `+0.380362/+35.955849`、`−382.748166/+53.158783`、`−1085.186052/+77.237466 ps`。另记两次有效 FF 读回，原物理生产器的 ODB/SPEF 为 `+0.772160` ps setup，同一生产器 V/LEF/SPEF 为 `+0.677236` ps，独立 V/SPEF 为 `+0.380362` ps，hold 均 `+35.955849` ps。缺 LEF 的预置失败无时序计数。候选和零动作用共同独立 STA 参照。
- **状态** ASAP7 共享零动作 RUNNING，工作目录 `/home/toylog/faeco_tcad_ibex_20261123/compare_asap7_v1`，实发命令 `scratch/tcad_ibex_20261123/compare_asap7_v1_command.txt`（SHA256 `09fd9e16021cd1f7d8ff8356e593f233c2c2f8b73451f1b06f505b0a48fe3f7f`），启动 `config.json` SHA256 `7bb1ffd0354fc9b349eb4d1f0f23825eaa68f4803ef3bb44b25fadb020df92af`。沿用每臂 6 次、批次 3、线程 4；单路由 1500 s、每视图 STA 180 s、SEC 外层 210 s 包内层 180 s。只有共享零动作通过后，同一驱动才进入三臂。SKY130HD 仍等待原始 CONTROL 资格。

- **ASAP7 共享零动作通过** `compare_asap7_v1/noop/receipt.json` 确认一次 DRT/RCX 完成、DRC=0、三次 STA、电气与时序拒绝理由均为空、一次全网表两态 SEC `17363/0`（47.338 s）；整次 323.883 s。FF/TT/SS 的 setup 差为 `+0.002665/−0.322409/−0.541789 ps`，hold 差在 `±0.000028 ps` 内。零显式触线、10 条网几何改变、0 组件移动。TT Liberty 定义的功能单元面积基准为 `2129.78808 µm²`，沿用该分母。候选池为 4151 个，已转入 `single` 第 1/6 次候选。原始 CONTROL 五件及导引归档为 `scratch/tcad_ibex_20261123/asap7_control.tar.gz`，SHA256 `7d97ab8f3d6127e267d6c242dd0643dbae966743263559706d578bd16407786d`。

- **SKY130HD 原始物理结果及资格复测方案** 原生 `make` rc 0，3141.28 s。经历初始详细布线和两次天线修复后重布线，最终 DRC 0、天线违规网和引脚为 0，RCX 15242 网，五件终点均保存。初次独立 FF STA 完成计算，但 `qualify_original_io/FF.log` 有 `ANTENNA_*` 的 SPEF 端点无法绑定。原 `6_report.json` 记 84 个天线单元，原 ORFS 导出按物理专用 master 过滤，独立 V/SPEF 两者实例集合不一致。本次读法的 FF 测量隔离为诊断。以相同原 I/O、`6_final.sdc` 和 `6_final.spef`，改用同生产器 Bazel OpenROAD 内置 STA 从 `6_final.odb` 测量 SKY130HD 三视图，并在后续 SKY 各臂保持同一测量路径。ASAP7 活动评估口径照旧。SKY 预备使用来自最终 ODB 的嵌入导引回读，SHA256 `fd4c2b3df466b7b129c5adc4001068d01a1e8fae79c642173fad2552be2530b1`；早期 GRT 文本导引 SHA256 `07e075c47e3a1b88d5b7f79ea634077589f4256c76781a87f3604f5c4ba1c3da`，两者各保原身份。


- **SKY130HD 原始 CONTROL 资格结果** `sky130_control/CONTROL.json` 为 `hold_infeasible`，SHA256 `f261513bcd005319b23169d509a25577419ea8605ea017b7846e8dbdc3f32fe9`。原物理 ODB、同源 SDC/SPEF 与固定同一 OpenROAD 完成三次有效 STA。FF setup/hold `+1171.698294/+288.150503 ps`，TT `−456.739535/+466.105821 ps`，SS `−38754.158993/−1379.766079 ps`，SS hold TNS `−13035.098334 ps`。TT 与原生读数一致至报表精度。原版不进入三臂和零动作，旧 FF 缺物理单元诊断保留。

### 2026-11-23 TCAD-IBEX-SKY130HD-COMMON-HOLD-REPAIR

- **状态** 条件式预登记。SKY130HD 原始 ORFS CONTROL 的 SS 绝对 hold 未满足入选条件。保持原始 CONTROL 和原始 I/O/SDC，只从同一原始 ODB/SPEF 新建独立修复输出。先用原 OpenROAD 物理生产器，在 SS 视图下试做共享起点的 hold 修复，初始处方为 `repair_timing -hold`、允许 setup 已有违例路径、hold guard 0.05 ns、最大 buffer 比例 10%，具体命令及限时另在启动前锁定。完整物理路线将在早期探针支持后运行。
- 新起点资格沿用原 P0 门，保留原始约束，要求物理路线与 RCX 实测、最终 DRC 与天线为零，并以物理 ODB 和同源 SDC/SPEF 获得 FF/TT/SS 下绝对 hold 非负。单列共同起点修复开销、动作与原始和修复后的 setup/hold。通过资格后方可开始共享零动作，三臂从完全相同的一个修复后 CONTROL 启动。此结果与原始 CONTROL、ASAP7 各自绑定，原始 3600 s 构建结果保留。

- **共同 hold 修复初探锁定** `/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_dry_root` 为独立输出。输入为已资格审计的原 `control_sky130/results/sky130hd/ibex/base/6_final.odb/.sdc/.spef`，精确指纹见原 `sky130_control/CONTROL.json`。用原物理生产器 Bazel OpenROAD、原 CONTROL 的 TT/FF/SS Liberty，`define_corners` 后逐视图读同一原 SPEF，读该平台 `setRC.tcl`。命令 `repair_timing -hold -hold_margin 0.05 -max_buffer_percent 10 -allow_setup_violations`。4 线程，外层限 300 s，报告修复前后 hold，只写初探 ODB，0 新布线/RCX。初探时序为诊断，原始文件只读。

- **初探实测** 命令 rc 0，生成 `hold_repair_sky130_dry_root/dry.odb`。原 SS 最差路径为 `rst_ni` 到寄存器 `RESET_B` 的 removal，24 个 hold 违例端点。修复器 2.21 s，插 14 个 hold buffer，三视图估计最差 hold 从 `−1379.766 ps` 改善到 `+51.001 ps`，最差 setup 估计保持 `−38754.159 ps`，工具报告面积由 148771 增至 148912 µm²。本阶段 0 新路线/RCX，估计端点不进入 P1。安排以这份精确初探 ODB 为输入，在独立 `hold_repair_sky130_01` 进行新物理实现和资格复测。

- **物理闭合续跑锁定** 独立 WSL 输出 `/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_01/`，终点在 `endpoint/`。用原 Bazel OpenROAD 2d966271…、4 线程，`timeout --kill-after=10s 120s` 执行 `original_inventory.tcl` 仅盘点原 ODB，之后 `timeout --kill-after=15s 1500s` 执行 `route_continue.tcl`。加载精确初探 `dry.odb`（SHA256 `755695216bec8e72e314ed11ffdf23997d910012624c6bdf7a3146458dd12dfa`），与原 ODB `1eaadcd071f59cc9b9d1cb7bded205235122eab7184e9687e4352615d9c99b15` 对照，物理评估使用 ORFS 原 TT 库和原 `6_final.sdc`（SHA256 `4e178c0c3469e33a244e3829b75ba473d1bae71dfd7c3765acb8847d63c508f5`）。读回初探及合法化后的实例，对新连线、变化的连接或位移实例的相邻网清线，更新全局导引，DRT 上限 64，单独记录天线，然后 RCX 并导出。原 SDC 不改，续跑不再调用 Resizer。待通过原严格资格后，才可为修复后 CONTROL 启动共享零动作。

- **首次物理续跑 _01** 原 ODB 盘点完成，随后合法化以 `DPL-0038` 在 100.1% 占用处停止。终点 ODB 的原末段填充包含 21,961 个 filler，尚未启动 DRT 或 RCX。保留失败原件与原盘点。
- **同输入修正 _02** 独立输出 `/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_02/`，使用同一 dry ODB、原 SDC、已锁定的物理库及字节同一原盘点。先 `remove_fillers` 并验证只移除原流程使用的 `sky130_fd_sc_hd__fill_{1,2,4,8}`，校验其他原实例不被删除；详细布线完成后，用原四种 master 重新填充。无需再次调用 Resizer 或执行原盘点工具。驱动 `route_continue.tcl` SHA256 `75aeedd034cf9a5dc134f8b6d2781e6026297951ff7271733cf5d304bb8756a3`，同一 OpenROAD、4 线程、`/usr/bin/timeout --kill-after=15s 1500s`。继承其余路线、RCX 及严格资格条件。

- **_02 路由结束，天线资格未过** `hold_repair_sky130_02/RECEIPT.json` 记录 164.128 s、rc 0，DRT 违规依次 `448→173→121→6→0`，RCX 提取 15,256 网。恢复 21,936 个 filler，全部物理接口及原 SDC SHA 不变。路线日志 SHA256 `abdee00db704cd6a89eeac2aa52daba372ea552acf3fc48eab0391c1ca8cb801`。另行 `check_antennas` 仍有一条网和一个引脚，原始 `endpoint/antenna.rpt` 绑定为 `data_rvalid_i → hold3717/A`。0 个新增候选评估，当前不能进入 P1。

- **_02 独立 STA/SEC 诊断完成** 同原 SDC 与端点的新 SPEF，三个视图 hold WNS 为 `+288.150781/+466.106043/−3.293366 ps`。SS hold TNS 亦为 `−3.293366 ps`，剩余一条 `instr_rdata_i[30]` 到 prefetch FIFO 寄存器的 min 路径。原始功能网表到修复后端点的两态 SEC `13648/0`、rc 0、40.537 s。该端点保留 SS hold 与独立天线各一项未通过证据，三臂未启动。
- **二次 hold 初探预登记** 原 `_02` 的最终 ODB/SPEF 与不变 SDC 为新只读起点，同原生产器、相同 TT/FF/SS 及同一 dry 评估流程。仅将 guard 由 0.05 改至 `0.10 ns`，其他 `repair_timing -hold -max_buffer_percent 10 -allow_setup_violations` 参数沿用，4 线程、外层限时 300 s。输出独立 dry_02 ODB，只作预测，0 新布线/RCX。随后候选 `_03` 的真实路由、提取和天线处理独立登记。

- **二次 hold 初探完成** 目录 `hold_repair_sky130_dry_root_02`，命令 rc 0，修复器 1.65 s。10 个端点低于 `0.10 ns` guard，插入 10 个 buffer，估计 hold 最差从 `−3.293366` 到 `+115.011 ps`，最差 setup `−38757.570 ps` 保持，原生面积估计 148912→149012 µm²。输出 `dry.odb` SHA256 `091333a9a36415e687a4bf97d6b07929ea49a609ada0c8a0dcac362651d2049b`，Tcl SHA256 `4f2384ba5c4aedffd012f82690b9989c31e2e4a0b50b6fe279dd20a76509792c`，原始日志 `scratch/tcad_ibex_20261123/sky130_dry_repair_02.log` SHA256 `92d4d7c1f08c53ca43e31dcd3d4ed21869d5ba60d548bf1927dbf725f933dc16`。0 新布线/RCX，真实 `_03` 验收另计。

- **_03 物理闭合与天线修复锁定** 独立输出 `/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/`。原 _02 ODB SHA256 `8018f00a04dd56ddac720ebbd46dd3828ec994314a95a8f060530a70886d5da6`；盘点命令用原固定 OpenROAD、4 线程、`timeout --kill-after=15s 120s`，`original_inventory.tcl` SHA256 `ea213b1790391ff0c4832eb6b74588e26606f6eb12d3c3692bce674d891cdf37`。后续用同一 OpenROAD、4 线程、`timeout --kill-after=15s 1500s` 执行 `route_continue.tcl`，传入已绑定的二次 dry ODB 和预期 10 个新增 hold buffers；Tcl SHA256 `1f2503bf8ce821696c743cb9cfc377df4fded2172eeec2ae01e2c24bc15efbc8`。固定原 SDC SHA256 `4e178c0c3469e33a244e3829b75ba473d1bae71dfd7c3765acb8847d63c508f5`、同 TT 库与 RCX 规则。限定拆除 _02 的 21,936 个已知 filler，合法化后按完整 _02 盘点差分清除变化连线，GRT+DRT（每次上限 64 轮）。若独立天线检查有违规，按原生 `repair_antennas -iterations 1 -diode_only` 做天线点修复、增量 DRT 并重新检查，最多两个循环。恢复 filler，最终天线和 DRC 都为零后 RCX，保留原 SDC 字节和完整终点。原严格时序与独立 SEC 门守到最后。
- **_03 启动前命令修正** 固定版 OpenROAD 的 `-exit` Tcl 不接收原方案的两个尾部参数。实际命令截至 `route_continue.tcl`，二次 dry ODB 与预期 10 个 buffer 以同值直接绑定到脚本内。实际 Tcl SHA256 `8493be922cfc9afa7ba09afa77a41569efd0a9e880d628da26fb444cf920e523`，其余配置沿用前条。旧命令构形未执行。

- **_03 实际物理终点** 原盘点 1.041 s，增量物理路由 235.650 s，均 rc 0。初段 DRT=0 后，独立天线发现 `net204→output198/A`、`data_rvalid_i→hold3717/A`，一次 diode-only 插入两个二极管。再次 DRT 的违规计数为 `66→75→129→5→0`，最终独立天线也为 0，两份报告均为空。新 RCX 提取 15,266 网，原 SDC 的字节指纹不变；完整原件、物理结果与哈希存 `hold_repair_sky130_03/RECEIPT.json`；等待三视图 STA 与原始到修复 SEC。

#### SKY130HD 资格核验及正式 P1 起点

- _03 修复后共同起点为 hold_qualified。原 SDC 字节一致，完整 ODB 与新 SPEF 的 FF/TT/SS setup/hold WNS 为 +1185.547216/+288.151891、−457.216487/+466.107042、−38756.656551/+115.913501 ps。DRC/antenna=0，SEC 13648/0（39.478 s）。原始与修复 TT Liberty 功能单元面积 144372.2144→144612.4448。修复原件包 SHA256 0d36cf6f3046b67fe9c5b1313b08932fea3154a826bf71efc04cc616b4aed0bd。[修复收据](tcad_ibex_20261123/sky130_control/REPAIRED_CONTROL.json) · [恢复过程](tcad_ibex_20261123/sky130_control/recovery/README.md)

#### TCAD-IBEX-P1-MATCHED-LOCAL-DRT-THREE-ARM 分阶段结果

- SKY 共用零动作 v1 以文本 guide 做 DRT，v2 用冻结 ODB 的 embedded guide 做 DRT。两者均为 1 DRT、1 RCX、3 STA，改线 13/16 条，SS hold 同为 −0.079936 ps 相对变化，均无 SEC 或候选。在候选前修订零编辑门为冻结 _03 布线重新 RCX。v3 为 0 新 DRT、1 RCX、3 STA、1 SEC 13648/0，DRC 沿用冻结零，三个视图 setup/hold WNS/TNS 及布线几何精确复现。进入正式 v3 候选，候选仍统一局部 DRT+新 RCX、相对 setup −10 ps/hold 非负及 0.001 ps 容差、每臂六次/批大小三/四线程。正式运行器 SHA256 7335409577e9a5b2a69e664d8b447be47cb46defcfe744ef52134f756309461f。[实际命令](tcad_ibex_20261123/SKY130_P1_REEXTRACT_COMMAND.txt) · [零动作三版核验](tcad_ibex_20261123/SKY130_NOOP_AUDIT.json)
- ASAP7 三臂结束并独立核验。单门／固定微批次／FAECO 自适应均 6 DRT、6 RCX、18 STA，SEC 次数为 3/0/1。选中 single/05、CONTROL、faeco/03，面积回收 0.37908/0/0.26244 TT Liberty 功能单元面积。公共 1325.602 s 窗口完成 4/6/5 次并回收 0.26244/0/0.26244。共享零动作独立记账。[配置](tcad_ibex_20261123/ASAP7_P1_CONFIG.json) · [原结果](tcad_ibex_20261123/ASAP7_P1_RESULTS.json) · [核验](tcad_ibex_20261123/ASAP7_P1_VERIFIED.json)

#### SKY130HD P1 暂停（用户指示）

- v3 已取得最终收据的候选为 single/01–06 与 fixed/01，共 7 次 DRT、7 次 RCX、21 次 STA、0 候选 SEC，均 DRC=0 且被门拒收。控制进程已暂停，fixed/02 子进程已退出、控制进程未归档最终收据，后续候选未启动。六次/臂预算与验收阈值沿用登记。fixed/02 完成性和计时需由最终收据确认，暂停间隔另记。阶段记录暂不形成完整三臂比较或公共墙钟结论。
- ASAP7 单门和自适应已完成的账本均在第三次达到面积回收 0.26244，对应本次观测累计 835.516/751.489 s。该观测保留为同收益时间描述，等调用次数和等公共墙钟前缀结果见完整核验。[ASAP7 三臂核验](tcad_ibex_20261123/ASAP7_P1_VERIFIED.json)

### 2026-11-23 TCAD-IBEX-P1-B0-SETUP-SENSITIVITY

- **讨论草案，未批准，未启动** 用户正在讨论 setup 预算，认为零 setup 损失作为主门槛过严。以下记录的是先前以 B0 为主的拟案。主预算、诊断档以及候选策略均待讨论决定。截至此条，两处拟用新输出目录均未创建，也未新开物理实验。先前固定 −10 ps 的 ASAP7 结果与已封存 SKY130HD v3 保留原口径。
- **共同起点** ASAP7 使用已合格的原始 ORFS CONTROL，SKY130HD 使用同原始 SDC 的已合格 _03 修复 CONTROL。保持各工艺先前的匹配比较所用 ODB/DEF/V/SPEF、原 SDC、DRC 收据、TT/FF/SS 库与各自 STA 表示，分别在新输出运行。新运行时输入、目标目录与工具指纹由实际命令及配置绑定。[ASAP7 起点](tcad_ibex_20261123/asap7_control/CONTROL.json) · [SKY130HD 起点](tcad_ibex_20261123/sky130_control/REPAIRED_CONTROL.json)
- **拟议 setup 门** 每个视图单独将候选与其固定 CONTROL 比较。主结果 B0 为 0 ps 相对损失预算。诊断档以原生 clock period 的 0.1%、0.25%、0.5%、1% 为预算。ASAP7 原生 1,000 ps，对应 1/2.5/5/10 ps。SKY130HD 原生 10,000 ps，对应 10/25/50/100 ps。相对比较保留 0.001 ps 数值容差，故候选需满足 CONTROL WNS 减预算与该容差。任何 CONTROL setup WNS 已非负的视图，候选同时须通过 0 ps 绝对 setup 下限，该绝对下限无负向容差。已有负 setup 视图继续按相对预算。TNS 辅助记录。
- **拟议共用硬门与物理评估** hold 绝对非负且相对起点在 0.001 ps 容差内非退化，电气违例无新增、DRC=0，满足接受条件的端点须通过非空全网表两态 SEC。同工艺沿用原局部 DRT 与新 RCX、三视图 STA、同源导引及等资源。面积仍为同 TT Liberty 的功能单元和。零动作独立记账。
- **拟议搜索预算与台账** 各工艺各预算档从相同 CONTROL 及同序候选池独立执行单门、固定大小三的微批次、FAECO 自适应微批次。每臂至多 6 次逻辑候选评估。新实验内部，仅当完整动作及同一冻结物理输入身份匹配时复用已得到的物理端点。复用仍记一次本臂逻辑评估。台账绑定工艺、预算、策略、依序逻辑试次、完整动作、端点来源、接受失败原因、面积/各视图量及耗时，分开记录逻辑计费次数和时间，以及实际 DRT/RCX/STA/SEC 和复用次数。各门均按该档重新判断。等逻辑次数比较为主，缓存后实际总墙钟另表。

- **旧运行封存** 原 compare_sky130_v3 的七次完整候选与 fixed/02 已产生的 DRT/RCX 单独留档。后者 0 STA、0 SEC、无完整判定，旧中间收据 SHA256 73d5464cc7f368e4c699793e410318c5199efc7097f6daebf01dca37ed93bff1。两个进程均已退出。旧候选产物和暂停时间不并入新运行。
- **拟用运行资源** WSL /home/toylog/faeco_tcad_ibex_20261123 下使用 setup_budget_asap7_v1 和 setup_budget_sky130_v1，分工艺各四线程、两队列可并行。单次 DRT/RCX 1500 s、每视图 STA 180 s、SEC 外层 210 s（内部 180 s），DRT 上限 64 轮，微批次大小三。setup 独立测试 15 项通过。实际命令待写入证据。

### 2026-11-23 TCAD-IBEX-P1-SETUP-PROTOCOL-V1

- **状态与旧证据** 用户已批准根据原论文核查后的评测方案开新实验。主口径为 tradeoff@1%，以相同的最终时序包络和墙钟预算比较三策略的最大已验收回收量，另记到等面积目标的时间。此前 B0 主比较仍为未批准拟案。旧 ASAP7 固定 10 ps 结果和 SKY130HD 暂停封存结果保留自身门限，均另计。

- **SKY130HD 本轮完成** 三臂各六次独立物理评估、各 18 次视图 STA、候选 SEC 0 次。主档及两种门的全部三个预算档均选择 CONTROL。720 s 内对三臂分别确认 3/3/5 次，回收均为零。诊断 108 次全部命中本轮精确动作缓存。每个候选在 TT 超过 WNS/TNS 损失限，同时触发 SS 相对 hold 门。原件、配置与结论经只读重算绑定，ASAP7 继续跑。[SKY130HD 核验](tcad_ibex_20261123/SKY130_P1_SETUP_VERIFIED.json)

- **双工艺完成并复核** 实跑与只读复核均 rc 0。ASAP7 主档各六次候选物理评估，共 54 次视图 STA、4 次候选 SEC。1200 s 窗口三臂分别回收 0.26244/0/0.26244，六次全部完成后分别为 0.37908/0/0.26244。单门与 FAECO 首次达标在 1135.931/810.920 s，均为相同两门及同一物理端点。0.5% 和 1% protect 下则分别得到独立的单门策略/FAECO 端点，回收 0.24786/0.13122，FF 保持非负，无新增 setup 违例端点。ASAP7 诊断补做 7 DRT/RCX、21 次视图 STA、2 SEC，实际 101 次缓存命中。SKY130HD 的 108 个诊断均复用主档。以各自 raw 结果和配置 SHA 绑定，两套完整原件另存归档。时间证据只支持本轮观测，负载不对称与原始配置遗留字段已记录。[ASAP7 核验](tcad_ibex_20261123/ASAP7_P1_SETUP_VERIFIED.json) · [报告与归档](tcad_ibex_20261123/REPORT.md#原始产物与复查)
- **冻结起点** 每工艺统一使用原已合格 P0，ASAP7 为原生 ORFS 已布线 CONTROL，SKY130HD 为同原 SDC 的 _03 共同 hold 修复 CONTROL。FF/TT/SS 三视图、各工艺原始 I/O、时钟周期、Liberty、STA 表示、下游局部 DRT/新 RCX 和同工艺既定导引模式均保留。每工艺使用相同候选池及原排序，对在线单门、固定大小三的微批次和 FAECO 自适应微批次各最多六次候选评估。
- **时序包络** 给定允许损失占周期的百分比 p 与原始周期 T，逐视图相对 CONTROL 允许 WNS 退化 B=(p/100)·T，允许 TNS 退化 max(10B,(p/100)·abs(TNS_CONTROL))，两项均检查。两工艺原周期 1,000/10,000 ps，主档 B 分别 10/100 ps。tradeoff 允许原本非负的 setup 在包络内小幅跨零，作为时序与面积折衷实验。protect 对原本非负的 setup 加 0 ps 绝对下限。诊断百分比档 0%、0.5%、1%，0% 仅保守参照。hold 绝对非负、相对非退化 0.001 ps 容差、无新增电气违例、DRC=0、功能面积回收及非空全网表两态 SEC 依然适用。tradeoff 端点须如实报告负 setup 及其视图，实验门与生产签核分别解释。
- **共同时间与面积** 主试验每臂独立执行实际候选 DRT、RCX、三视图 STA 和所需 SEC，真实墙钟包括策略成本。共享零动作另计。固定公共窗口 ASAP7 1200 s、SKY130HD 720 s，仅计窗口内已完成全部验收的端点，另报等次数前缀。等面积目标为各自冻结 CONTROL 功能面积的 0.01%，ASAP7 为 0.212978808、SKY130HD 为 14.46124448 TT Liberty 功能面积单位。报告同一时序门下首次达到所需实际墙钟或在公共窗口未达到。诊断可在本工艺的新试验中复用相同输入及完整动作产生的物理结果，以各档的实际门重判，分别登记逻辑调用、等效计费时间与真实执行次数。诊断缓存时间用作流程解释。
- **运行与报告边界** 两工艺各四线程，单次 DRT/RCX 1500 s、每视图 STA 180 s、SEC 外层 210 s（内层 180 s）。沿工艺既定路由模式使用新目录 setup_protocol_asap7_v1、setup_protocol_sky130_v1。记录 WSL 12 个逻辑 CPU 环境及实际亲和性，可用时分配两组互不重叠 CPU。窗口、面积目标与 TNS 上限是本轮预先指定的工程比较参数，跨设计结论需另验。按实际命令绑定工具、资源与哈希，启动和结果另补。[评测方法依据](../planning/FAECO_EVALUATION_PROTOCOL_DRAFT_20261123.md) · [已合格起点](tcad_ibex_20261123/REPORT.md)

- **执行已绑定** 本地 17:13:36（UTC+8）并行启动。ASAP7 PID 670、CPU 0–5、原文本导引，配置 SHA256 14c47373d13f84bfdaf499847bfce96dc2f37dd7548c45268ae106e69e88eaad；SKY130HD PID 673、CPU 6–11、ODB 内嵌导引及共享零编辑复提取，配置 SHA256 cf01d187a703752a3ee7f83cddf8a315ff8f2981ac202a292d4e9941e3af372c。两份配置分别为 WSL /home/toylog/faeco_tcad_ibex_20261123/setup_protocol_asap7_v1/config.json 和 setup_protocol_sky130_v1/config.json。两进程各四线程、64 DRT 轮、1500/180/210 s，候选启用 setup 端点盘点。共享零动作单次保留原 setup 预检 10 ps，计时在主臂窗口外。在启动前确认 93 项测试与端点审计探针。
- **TNS 字段解读** 原配置的 tns_gate=false 为基础驱动遗留字段。新 setup_tns_loss_budget 字段绑定本轮逐视图 TNS 包络，sweep 的候选评估直接调用该门，超限标记 setup_tns_budget。复核以实际候选门和收据为准，原始配置留存。


### 2026-11-23 TCAD-IBEX-ASAP7-TARGET-SERIAL-REVERSE-V1

- **目的与对照** 用户要求排除前轮同机并行干扰后，确认 ASAP7 两种方法到同一回收目标的墙钟差。此次在同一工作站、同一进程串行执行两对完整复跑，先 FAECO→单门贪心，再单门贪心→FAECO。四臂固定 CPU 0–5、OpenROAD 各 4 线程，运行前查无其他 EDA 作业，记录起止时间与背景负载。原件输出为 WSL /home/toylog/faeco_tcad_ibex_20261123/setup_serial_asap7_v1。此前 810.920 s 和 1135.931 s 仅为原有不等负载观测，不并入本轮配对计时。[前轮主比较](tcad_ibex_20261123/REPORT.md#asap7-主比较)
- **冻结配置** 沿用前轮 ASAP7 原始 CONTROL、原 SDC 与 I/O、相同候选池顺序、文本导引、FF/TT/SS 三视图及物理设置。采用相同 tradeoff 1% 路径，WNS 各角相对损失最多 10 ps，TNS 沿原逐角包络，hold、DRC、电气和非空 SEC 门不变。以 CONTROL 的 0.01% 即 0.212978808 面积为阈值，四臂各最多六次候选评估，首次完整验收并达到目标即停止。共享起点和一次零动作预检单列，不计入方法墙钟。实际命令、版本与输入哈希在启动回执登记。
- **计时和核验** 四臂从各自策略入口计时到首个满足目标的端点完成验收，记录每次已完成检查点及 DRT/RCX、三角 STA、实际 SEC 次数与耗时。四臂独立重跑全部所需物理验证和 SEC，不走缓存。若停止前未达目标，报告已有完整前缀和六次内未达到。分别核对首达面积、候选动作、ODB/DEF/V 和去日期 SPEF、逐角时序及 SEC 绑定。两对分别比较时间差的方向和波动，确认本机本例的复现范围和工作量来源，跨设计或稳定提速仍需额外数据。
- **实际启动** WSL `ps` 实查为 21:11:55（UTC+8），外层限时 PID 346，实验驱动 PID 428、CPU 0–5。原调用在相同资格回执和 `setup_protocol_asap7_v1` 前轮原件下运行 `run_asap7_serial_repeat.py`。外层限时 14400 s，单次 DRT/RCX、每视图 STA、SEC 限时 1500/180/210 s，4 线程、64 次 DRT 轮、批宽上限 3、启用 setup 端点报告。配置 SHA-256 `280c776244e3dfe187aa685b7a177be1c8ebae1910a7932337d66243010e2427`，启动前针对性测试 33 项通过。


- **完成与复核** 四臂均独立实跑至第三次，同面积回收 0.26244。逆序 688.233/728.543 s，原序 695.670/730.866 s，分别为 FAECO 和单门。单门在两对中均多一次 SEC，增加 38.480/37.066 s 的 SEC 计时。核验 rc 0，四端点与前轮首达端点的 ODB、DEF、V 和去日期 SPEF 一致，四端点 SEC 均为 17363/0，合计 12 DRT/RCX、36 STA、6 SEC、缓存命中 0。结果 SHA-256 `d5b1adc79bee8c39278401486f20d306b9552f2068b8d40197aecd613d8e0a29`。QPC/RAW 与 WSL MONOTONIC 差异单列，正式差值使用预登记 WSL 时钟。完整 EDA 归档 SHA-256 `b016a9f5e103c2db7281d74c69e0fe6d97486a8f85f57d609fd653df8b1fcccd`。[复跑报告](tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md) · [独立核验](tcad_ibex_20261123/ASAP7_SERIAL_VERIFIED.json)


### 2026-11-23 TCAD-IBEX-SKY130HD-TT-TIMING-CAUSE

- **先行资料核查** 绑定此前 SKY130HD 主档的 18 个候选、同起点 TT 收据和零动作对照，逐端点检查 setup WNS/TNS、大幅变化的路径、换门与布局和寄生证据。先读取已有日志、SPEF、DEF 等，不与 ASAP7 串行计时竞跑 EDA。仅在证据不足时另登记针对性工具查询，保持原约束。将直接验证的路径和因素与尚未检验的解释分开记录。[前轮核验](tcad_ibex_20261123/SKY130_P1_SETUP_VERIFIED.json)

- **交叉复测预登记** 对 FIFO 单门 01 和寄存器堆单门 05 分别交叉 CONTROL/候选 ODB 与 CONTROL/候选 SPEF，两例共用 CONTROL×CONTROL，预期七组 TT STA。固定原 SDC、TT Liberty 与 OpenROAD。真实组合先检查能否复现原 WNS、TNS 与负端点，再比较固定发射/捕获路径、同一驱动器的固定分支及逐端点负 slack 累计。交叉结果用于分离同一固定样本的单元选择和 RC 效应。ASAP7 四臂结束前不启动。[路径证据和组合说明](tcad_ibex_20261123/SKY130_TT_CAUSE.md)

- **交叉复测完成** ASAP7 四臂结束后运行，七组均 rc 0。真实 CONTROL 和候选组核对 WNS、TNS、负端点集一致。固定 CONTROL 寄生使用候选 ODB 时，FIFO 和寄存器堆的 WNS 变化分别为 −474.644、−403.733 ps，TNS 变化为 −24.628、−22.368 ns。固定 CONTROL ODB 只换候选寄生时，WNS 变化为 −0.002665、+0.986766 ps，TNS 变化为 +0.035481、+0.565102 ns。逐负端点 slack 和与 TNS 的取值差绝对值上界 0.007191 ps。结论覆盖两例交叉拆分和 18 例观测路径。原结果 SHA-256 `1040196a01aecbdf0efe36b8dad3f1284ffb6c1895938ba0de08978954c421ab`。[TT 归因](tcad_ibex_20261123/SKY130_TT_CAUSE.md)

### 2026-11-23 TCAD-SKY130HD-SCREEN-ABLATION-HOLDOUT-V1

- **状态与目的** 用户已授权执行 T01 候选筛查、T02 同预算消融、T03 留出验证。T01/T02 使用原 `hold_repair_sky130_03/endpoint` 的冻结 Ibex CONTROL、原 SDC 与 I/O、TT/FF/SS、原局部布线方式和功能面积定义。各角 setup WNS 相对损失限为原周期的 1%，Ibex 为 100 ps，TNS 允许损失为 `max(10B, 0.01×abs(TNS_CONTROL))`，沿用 tradeoff 的过零口径。正式验收同时检查三角绝对 hold 非负、相对非退化 0.001 ps 容差、无新增电气违规、DRC=0、正面积收益和非空两态全网表 SEC。绝对 hold、相对 hold、setup、电气和实际证明确认分项记账。[起点和上轮协议](tcad_ibex_20261123/REPORT.md#按原周期归一化的-setup-预算对照)
- **T01 局部验证** 固定此前定位的 FIFO `place2749` 和寄存器堆 `place2755`，复查可合法使用的较温和降档，并纳入最多两个低负载对照。先在固定 CONTROL SPEF 上做有界候选筛查，再选最多四个端点实跑 DRT/RCX、三角 STA 与按门触发的 SEC。精确替换、输入哈希、入选判据和限时在启动回执绑定。原 `buf_12→buf_1` 已有实测值单列作对照，固定 SPEF 的预测与实跑端点分开。[原归因](tcad_ibex_20261123/SKY130_TT_CAUSE.md)
- **T02 同预算消融** 原面积排序与新筛选排序各自运行单门贪心、固定三门批次、FAECO，形成两种前端×三种调度。每臂六次候选物理调用，独立执行且不跨臂复用物理结果。每种排序内三方法共用同一候选池和顺序。公共窗口 720 s，共同面积目标为起点的 0.01%，Ibex 为 14.46124448。计时使用 `CLOCK_MONOTONIC_RAW`，同时报搜索纯耗时、筛选实测耗时和把筛选成本全额计入每条筛选策略的端到端前缀。共同起点、基础输入准备与预检单列。报告截止时完整验收的最大面积、首达面积目标、六次前缀、各视图 WNS/TNS/hold、端点拒收和 DRT/RCX/STA/SEC 成本。冻结筛选规则后才启动对照。
- **T03 留出验证** 在看到留出候选表现前登记设计身份，制备原始 I/O 和 SDC 下经过 DRT/RCX、DRC 与三角绝对 hold 资格的共同起点。沿用冻结筛选规则和 1% tradeoff 指标，在同起点、同预算下比较三种调度并登记原排序对照及计时范围。候选筛选禁止在留出结果上调参。记录可用设计数、路径、工具和输入指纹。T01 预定 CPU 0–5，留出起点制备 CPU 6–11，实际并发与时序比较各自分账；T02/T03 的计时亲和性和同时运行负载待实际启动回执确认。

- **筛选规则锁定** 沿原工程兼容性、`PLACED` 与非时钟门范围，每实例枚举所有合法更小目标，按 TT Liberty 目标面积从大到小选一个最近档位，同面积按名称稳定择取。排序键为实测各输出网接收引脚数的最大值升序、预估面积收益降序、动作 ID 升序。沿排序最多尝试 32 个固定 CONTROL ODB/SPEF TT 单动作 STA，按原周期归一化的 TT WNS/TNS、绝对 hold 非负和转换时间/电容无新增违规判定，累计通过 18 个即停止。保留通过候选的原顺序。T01 的四个物理探针为两例高扇出最近档和上述序列中前两个通过筛查的低扇出动作，四个均单独详细布线和复提取。正式验收沿原三视图联合门。相对原 CONTROL 与零编辑路由的 hold 差异另作归因。

- **T01 启动与 T03 对象登记** Ibex 筛选进程 PID 2250，WSL 实查启动为 23:14:19（UTC+8），CPU 0–5，使用原 Ibex `_03`、内嵌导引及原三角 STA/SEC 入口。输出 `screen_ibex_v1`，后续四个物理探针为 `screen_ibex_pilot_v1`，OpenROAD 四线程、DRT 64 轮、DRT/每视图 STA/SEC 限时 1500/180/210 s，计时使用 RAW。筛选脚本启动时 SHA-256 `a19a3f9ee1cf5d140cde2bc3301a5de5193279fa7cad219c390f40e130874612`。同机 CPU 6–11 开始制备留出原始起点。主留出为 ORFS `sky130hd/aes`（`aes_cipher_top`，周期 3.6 ns，I/O 0.72 ns），补充对象为 `sky130hd/gcd`（`gcd`，周期 1.1 ns，I/O 0.22 ns）。生产脚本 PID 312，实查 23:11:51（UTC+8）启动，ORFS `da8f092a02a8e75658cc3100691aabff05f35629`、固定 OpenROAD、每设计 4 线程和 3600 s。两者尚未运行候选。T01 成本记录此并发背景。[命令](tcad_ibex_20261123/SCREEN_PILOT_COMMAND.txt) · [留出起点报告](tcad_holdout_20261123/REPORT.md)

- **T01 工程重试** v1 在近邻兼容覆盖检查处退出，固定 SPEF 候选、DRT 与 RCX 均为 0。保留原目录及清单。修复重复规范化 ODB 实例名的问题，按现有对齐映射使用原名，旧 inventory 的 1112 个实例全部覆盖，两处高扇出最近档均为 `buf_8`。冻结的门、排序和预算参数保持原口径。修正版 SHA-256 `477e8a14f38b8d3434b14896fea4959c1a2afca262d6653156aa7ff82aa3b7d3`，PID 2422 在 23:17:27（UTC+8）启动新目录 `screen_ibex_v2`，后续物理目录 `screen_ibex_pilot_v2`，亲和性仍为 CPU 0–5。

- **Ibex 筛选池实测和四探针封存** 固定 SPEF 筛选 18/18，扇出全为 1，RAW 耗时 129.454710207 s，已封存池 SHA-256 `4c393545b7d356002bd4fc3bf534b686bf1ee3da170b70469359d796f1f984e0`、筛选收据 `2d14b8bd78fbe7b103fd31fc93acc9d8a355217c13341dfe9eff0f347ad54447`。四探针为 `place2749`/`place2755` 的 `buf_8`、`_15066_` 的 `o31ai_2`、`_15882_` 的 `a31oi_2`；固定 SPEF TT 初筛均通过。探针清单 SHA-256 `ee88f8bb3d4b9ef5160ac01c3eaebe014f1b83e4e8b3eb5f4e86a86d960ca95c`，物理验收单独记录。T02 的筛选计费来自筛选收据，不将额外两次高扇出诊断读回计入算法筛选。

- **T03 GCD 起点已取得资格** 实际以单独的两线程起点生产提前完成 GCD，CPU 6–11、1200 s 限时，`producer.rc` 为 0。用原 1100 ps 周期、220 ps I/O 与 35 个输入/18 个输出，原 SDC SHA-256 `7dc2766d530b78c92e12c8e84462f8dade2f0bf2074e85580f7364976252767c`。三视图 hold WNS 为 FF +358.948、TT +430.727、SS +342.905 ps，DRC 为 0，资格收据 SHA-256 `5c2dfa530777cca5e141209d027445b8e966aa070890d1570cef880c4ba34ea9`。计数仅为 3 次起点 STA，候选布线、STA、SEC 均为 0。AES 继续生产。[留出起点报告](tcad_holdout_20261123/REPORT.md)

- **T01 Ibex 四例物理验证完成** 总计 4 次 DRT、4 次 RCX、12 次候选视图 STA、0 候选 SEC、0 缓存，545.012907478 RAW s。温和降档与低扇出四例的 TT WNS 改变量为 −0.002665 至 +0.986766 ps，TNS 均改善，三角 setup 联合预算和绝对 hold 均满足，DRC 均为 0。面积候选测量为 5.0048、5.0048、8.7584、8.7584，唯一拒因都是 SS 相对 hold。原门的正式回收为 0。候选对历史零编辑的 SS hold 差分别 0、−0.026645、+0.003553、0 ps，作为共同重布线扰动诊断。原结果 SHA-256 `c63a5ce29513ffe39d7fe6516cf604b082d02734cbd0bd63fd799eb3704abeb2`。
- **T02 Ibex 启动** PID 6235，23:31:00（UTC+8），CPU 0–5，活动配置 SHA-256 `586be0f6f8ef8eaf1eb219790978882cca6f37ac6c12cbf874a5720d26f4af97`。顺序为原排序、筛选排序，每种排序内单门、固定批次、自适应，候选物理调用独立。冻结池和筛选成本沿 `screen_ibex_v2`，每筛选臂 RAW 预付 129.454710207 s。AES 在另一组 CPU 上制备起点，评价时记录资源背景。

- **T03 GCD 工程修正、筛选与启动** 初次筛选因资格 `0.22/1.1` 的浮点重构与原 SDC 字面 `0.2` 的微差在 EDA 前停止。独立包装器以 `1e-12` 核对后保留原 SDC 字面和原核验入口，恢复原门。`gcd_screen_v1` 实跑筛选 20、通过 18、TT WNS 拒收 2，52.520672847 RAW s。原周期 1100 ps 对应 TT WNS/TNS 11/570.255 ps。池和筛选记录冻结后，`gcd_matrix_v1` 于 23:34:28（UTC+8）在 CPU 6–11 启动，PID 7536，筛选排序先行，配置 SHA-256 `004d77026633fbc2bd6e6b9a07d3ca9440ed0b884ba72ed9ae7a825622c107e0`。AES 起点同 CPU 组正在生产，并发背景按阶段单列。

- **T03 GCD 六臂完成** 独立核验 rc 0，原排序三臂回收均为 0，筛选排序单门／固定／FAECO 为 0／11.2608／0。候选 DRT/RCX 36 次，三角 STA 108 次，SEC 1 次，缓存 0 次。筛选固定批次第 5 次包含候选池排名 13–15 的三门，合格回收 0.234742%，SEC 262/0，无新增负 setup 端点。相同预算 FAECO 六次只覆盖到 4 名。计入 52.520672847 s 筛选后，唯一合格臂目标时间为 146.249239816 RAW s。原排序／筛选排序任一 setup 门拒收数为 17／5，TT WNS 或 TNS 拒收并集为 15／0，仅相对 hold 拒收数为 1／12。原结果 SHA-256 `eb9a8838d8918530f31fd8f421b10f3e1e350e97fb8d131e90efec62a217e0bc`，归档 SHA-256 `2199d21b28109bd5a0e408567cd66a0cce67b3e45589345d7fe8589fde9d8f8b`。[留出核验](tcad_ibex_20261123/SCREEN_MATRIX_GCD_VERIFIED.json)

- **2026-11-24 AES 原生起点结果与有界修复** producer 工具报告 2832.64 s、rc 0，DRC=0、RCX 完成。原 SDC 3600 ps、720 ps I/O，端口 258 入/129 出，通过文本和导出约束同源复核。FF/TT/SS hold WNS 为 +341.429/+529.873/−975.978 ps。原资格状态 `hold_infeasible`，收据 SHA-256 `88f22171c81197aa9b1e4bdeb5e4b94ffd7ef0975de456d218124aea6bbd08b8`。先在相同原 SDC/IO 下做独立留出的共享起点 hold 修复，修复产物重新过原资格及 SEC 后方可进入冻结规则。此时仅有三次原生起点 STA、候选 0。[留出报告](tcad_holdout_20261123/REPORT.md)

- **2026-11-24 AES 修复共同起点取得资格** 首次 SS hold 修复 DRT 后仅余 −66.616 ps。定向技术重试 `ss_hold_targeted_v2b` 在唯一残留 D 引脚前插入一个延时单元，完成 DRT/RCX 与三角 STA，DRC=0，RCX 提取 15657 个网，FF/TT/SS hold WNS +336.274/+523.915/+55.296 ps，TNS 均为 0。保留原 SDC/I/O，修复后资格 SHA-256 `c697450a257ef4e63182f02c0ce4fb3c5925b41f366628a97672ac440192d4f8`。原生端点导出网表与最终修复网表的全网表 SEC 11089/0、rc 0，收据 SHA-256 `bdc28e0f27e7b653965de68a27e611cbc4da006105bb68ef063756ee1f3ac02f`。起点生产、修复与候选阶段独立计费。此时 AES 留出候选仍未实跑。[留出报告](tcad_holdout_20261123/REPORT.md)

- **2026-11-24 T03 AES 筛选与矩阵启动** 冻结规则在 AES 的固定 SPEF TT 读回通过 18/18，均扇出 1，TT 预算 36 ps WNS 和 360 ps TNS。筛查 113.363032440 RAW s，池 SHA-256 `1bd07df9ff7d5f0679f46968a19f09be4543ce2692af6e5c362b636cfd6177ce`，筛查收据 `3bf60527e63e877e9cb05af70b82ec1698118773cefbc0d6c4b6dd2b42a5bd79`。原排序先行，`aes_matrix_v1` 实查 PID 15006、00:21:18（UTC+8）、CPU 6–11，使用 AES 自身 FastRoute 配置。配置 SHA-256 `bc62ef9ac0225aca50768bd1b243ae1311a2565c7863ad4183d29a23030002d9`，共同窗口 720 RAW s，面积目标 0.01%，每个筛选臂全额计入 113.363032440 s。Ibex 并行使用 CPU 0–5。

- **2026-11-24 T02 Ibex 六臂完成** 独立验收包含 36 次 DRT/RCX、108 次 STA、4 次候选 SEC、0 缓存。原排序三臂 0。筛选排序单门／固定／FAECO 六次回收 7.5072／62.56／0，720 s 窗 0／22.5216／0，筛选固定批次在计费 562.522642755 RAW s 时达到 0.01% 目标，首次三门为筛选池排名 7–9。筛选排序任一 setup 拒收由原排序 18 次降到 1，TT 拒收由 18 降到 0，新增 13 个仅 SS 相对 hold 拒收和 4 个严格合格候选。原结果 SHA-256 `0380617dae7d5a7c66f46ec89c64dcc221889764d38612c37dcdc44435fe9800`。[Ibex 核验](tcad_ibex_20261123/SCREEN_MATRIX_IBEX_VERIFIED.json)

- **2026-11-24 T03 AES 六臂完成** 36 次实际 DRT/RCX、108 次视图 STA、0 次候选 SEC、0 次缓存、26 种动作组。两种排序下各三方法的六次前缀和 720 RAW s 窗内回收均为 0，预设 11.65079904 面积目标均未达到。原排序与筛选排序各 18 次，违反 setup 门的计数为 12／0，TT WNS 或 TNS 拒收并集为 12／0，仅相对 hold 拒收数为 6／18。筛选候选都是绝对 hold 非负，只违反相对 hold，按视图计 SS 17、TT 3、FF 3，可重叠。原结果 SHA-256 `b4289fa51f666f500517ba24d1534eb41050991abbe33f68de132501c3db21a3`，独立核验 SHA-256 `506551827c0f9531f2359877c57b013f163481b6c0f1ce79a3ee6c5487f7e136`。[AES 核验](tcad_ibex_20261123/SCREEN_MATRIX_AES_VERIFIED.json)

- **Ibex 历史零编辑 hold 诊断补 SEC** 正式计时全部完成后，对 T01 探针 01、03、04 和 T02 筛选 FAECO 第 3 次已有的候选网表各独立运行一次原 CONTROL 对候选的 SEC，均为 13648/0、rc 0。四个端点对历史嵌入导引零编辑路由的 hold 诊断通过，面积分别已测为 5.0048、8.7584、8.7584、17.5168。四次另立诊断计费，正式矩阵继续使用冻结原 CONTROL。新相对门下的搜索和首达耗时尚未经实跑。[探针诊断核验](tcad_ibex_20261123/SKY130_SCREEN_HOLD_SEC_VERIFIED.json) · [FAECO 端点证明](tcad_ibex_20261123/SKY130_SCREEN_FAECO_HOLD_SEC.json)

- **2026-11-24 T01–T03 执行与核验完成** 三套 36 个候选的正式矩阵共 108 DRT/RCX、324 视图 STA、5 候选 SEC、0 缓存。T01 物理探针为额外 4 DRT/RCX、12 视图 STA、0 正式 SEC。Ibex 历史零编辑 hold 归因另有 4 次 SEC。面积、三视图 setup/hold、负端点、SEC 与计时对照以同一候选端点验收记录绑定。完整四包列于 `LOG-20261124-14`，原件 SHA-256 复验一致，独立核验和封存索引见总报告。[筛选消融与留出报告](tcad_ibex_20261123/SCREEN_ABLATION_REPORT.md) · [日志](../LOGS.md#log-20261124-14t01t03-规约实验收尾与原件封存)

### 2026-11-24 TCAD-SKY130HD-AES-ZERO-EDIT-REROUTE-AND-SCHEDULER-DIAGNOSTIC-V1

- **AES 对照预登记** 冻结 `aes_matrix_v1` 的 `ss_hold_targeted_v2b`、原 SDC/I/O、FF/TT/SS Liberty、AES 原生 FastRoute 设置及工具版本。从同一物理起点以空动作组运行 ODB 内嵌导引的 DRT、RCX 和三视图 STA，四线程、64 个 DRT 迭代上限。原件写至 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_zero_reroute_diag_v1`。复提取预检与真实零编辑重布线分别记账。即使零编辑违反正式门，也保留按原 CONTROL 计算的三角 setup/hold、绝对裕度、DRC 与门收据。比较固定批次第 2、5 次与其余已测候选的 hold 路径、寄生和重布线参照，检验共同重布线能解释多少差值。单一零编辑试次不能给出跨种子容差，诊断投影不构成新的候选验收或 SEC。
- **调度回放预登记** 读取已有 Ibex/GCD/AES 冻结筛选动作组、候选状态和六次配额内实际尝试，比较优先拆分与先覆盖后续批次的动作组触达情况。对未测动作组保留未知，已有端点只在物理起点与完整动作身份匹配时借用原收据。调度诊断不新增 DRT/RCX/STA/SEC，历史工具耗时只对应原执行路径。对照 ASAP7 已测的提前批量提交案例，以区分覆盖与 SEC 开销。
- **AES 对照实际启动** WSL 进程表为 07:41:25（UTC+8），外层限时进程 PID 438、驱动 PID 439，CPU 6–11。使用 `probe_aes_zero_reroute.py` 的 `--embedded-guides --probe-only`，不使用 `--zero-reextract`。外层限时 2400 s，DRT/RCX 1500 s，单视图 STA 180 s，SEC 限时配置 210 s。配置 SHA-256 `50aaf0ea602ace552a408d873e3c34427afeae073dbca30effd6ade661c47ee9`，绑定原矩阵配置 `bc62ef9ac0225aca50768bd1b243ae1311a2565c7863ad4183d29a23030002d9` 及其原始输入。驱动使用共享零动作预检的 10 ps setup WNS 限制，绝对 hold 非负、相对 hold 容差 0.001 ps。正式候选原有百分比 setup 包络与实际验收继续按各自矩阵读回。[实际命令](tcad_ibex_20261123/AES_ZERO_REROUTE_COMMAND.txt) · [入口](tcad_ibex_20261123/probe_aes_zero_reroute.py)
- **AES 零编辑重布线完成** `noop/receipt.json` SHA-256 `8cfbff74559103f990f73b39073efba3c08a7c6d15c6f7e686cc69052a466052`，空动作组、1 DRT/RCX、3 STA 均 rc 0、DRC=0、逻辑网表与原控制字节一致，面积差为零，零编辑自身未满足 SS 相对 hold。三视图 hold WNS 的 FF/TT/SS 差值为 +0.0000555/0/−0.676792 ps，实际 SS 绝对 hold +54.618976 ps，三角 hold TNS 仍为 0。六条无显式触达的网改变走线，组件摆放无变化。实际评估 113.555908 RAW s，其中 DRT/RCX 100.836876 s。共同起点重读另含 3 STA 与 ODB inventory，候选及 SEC 计数均为零。[总日志](../LOGS.md#log-20261124-16aes-零编辑触发-ss-相对-hold-拒收)
- **调度收据回放完成** 复核三个 SKY130HD 筛选矩阵及两条 ASAP7 实跑。任一角相对 hold 拒收即延后拆分的回放在三个 SKY130HD 设计上和已有固定批次动作逐项匹配。Ibex 第 3 次和 GCD 第 5 次触及正式接受的原收据，AES 仍为零。ASAP7 两回放未触发延迟规则，保留原第 3 次达标的拆分端点。回放新增 DRT/RCX/STA/SEC 均为 0，未测独立留出上的新调度和墙钟。[调度诊断](tcad_ibex_20261123/SCHEDULER_COVERAGE_DIAGNOSTIC.md)
- **AES 零编辑参照投影** 用实测零编辑作为相对 hold 参照，保留 0.001 ps 容差和绝对 hold，以及原矩阵已记录的 setup、DRC、电气等条件。18 次原筛选评估中单门 4 次、固定 1 次、FAECO 3 次通过物理和时序投影，对应 5 种不同单门编辑。最大面积减量 11.2608（0.009665%），均未达到 0.01%。六次面积减量为 33.7824 的三门评估仍被联合 hold 门拒收。投影未执行新搜索和 SEC，原矩阵的正式面积为 0。
- **AES ODB/SPEF 交叉复测** 原始目录 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_hold_cross_diag_v1`，CPU 0–5、每次 OpenROAD 单线程和 90 s 限时，原 CONTROL SDC 与各角 Liberty 保留。输入清单和最终结果写入时间为 07:43:47、07:44:29（UTC+8）。固定批次第 2 次 SS、第 5 次 FF/TT 各做原 CONTROL 与候选 ODB/SPEF 的四格 STA，共 12 次，均完成并核对最差路径和注解。只换候选 SPEF 复现 −1.609379/−0.070222/−0.108413 ps 的实测 hold WNS 损失，只换候选 ODB 三例均保持原值。清单和结果 SHA-256 为 `872d357715b8db8d60113e44b35f7a58bd6ad7aa04eb8ad661a9ae2db5c0afdd`、`8894f60adb0bb8cda566f7dbc49a4adccbf2a9b750f70e59526892f6cdab404d`。无新增候选布线和 SEC。[AES 归因](tcad_ibex_20261123/AES_REROUTE_HOLD_DIAGNOSTIC.md)
- **核验与封存** `scratch/tcad_ibex_20261123/aes_hold_cause_diag_v1.tar.gz` 归档含本轮零编辑和交叉 STA 原件，16,741,646 字节，SHA-256 `999f944c7925a90997b80eb446512685731a5cfb14a3d0513df829c9da9a5aab`。读取归档成员验证零编辑收据及交叉清单、结果均与原 SHA-256 一致。候选正式验收采用原矩阵口径。[精简回执](tcad_ibex_20261123/AES_ZERO_REROUTE_VERIFIED.json) · [总日志](../LOGS.md#log-20261124-19完成归因核验与原件归档)

### 2026-11-24 TCAD-SKY130HD-SCHEDULER-AND-AES-CLOCK-ROUTE-REPAIR-V1

- **调度修复预登记** 起始代码 `4469d6e9`。实现显式启用的原因感知策略，在同一候选拒收且 FF／TT／SS 任一角触发 `hold_regression` 时，将拆分延后并尝试后续整批。只有 setup 拒因时保持原递归行为，验收条件与可用预算沿原矩阵。先做单元与流程回归，再固定 CPU 6–11 串行在两个已用于归因的 SKY130HD Ibex、GCD 筛选池实跑，绑定各自原始 CONTROL、冻结排序、原 SDC、Liberty 和路由。每设计六次物理调用，公共窗口 720 RAW s，各臂计入原筛选成本，目标为原起点面积 0.01%。记录完整实际动作、DRT/RCX、逐角 STA、候选 SEC、每次成本、首达和窗口内/六次最佳面积，复核实际通过的端点及原对照。区分原固定批次墙钟、修复臂实测时间和跨样本结论。[先前诊断](tcad_ibex_20261123/SCHEDULER_COVERAGE_DIAGNOSTIC.md)
- **AES 路由修复预登记** 原合格起点 `ss_hold_targeted_v2b` 与原 IO/SDC，三视图和原联合验收口径。先以零编辑检验关键时钟网能否保留及原时序能否复现，再对已测的 hold 拒收候选试保护路由。校验改线与 ODB、DEF、SPEF、最差路径、DRC、三视图 hold 和原 setup 包络。任何通过正式候选门的动作须用真实新网表执行非空两态 SEC。独立 CPU 0–5，具体网、运行命令、动作绑定和限时另记。[先前 AES 归因](tcad_ibex_20261123/AES_REROUTE_HOLD_DIAGNOSTIC.md)
- **AES 执行规格** 在每次读取同一合格 ODB 后，用增量 DEF 标记已有走线的非目标网为 `FIXED`，保留全部内嵌导引，按去除状态标记后的布线几何逐网和原 DEF 核对。零编辑、原 `screened/fixed/02`、`screened/fixed/05` 按序运行；原件计划写到 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_selective_drt_repair_v1`。限定 CPU 0–5、四线程、DRT 上限 64 轮，整批 1200 s，每例 DRT/RCX 240 s、逐角 STA 180 s 和 SEC 210 s。候选按原每角 36 ps WNS 与登记的逐角 TNS 损失包络、原绝对与相对 hold、电气、DRC 和 SEC 门判定。
- **调度实跑 GCD 已启动** WSL 进程表 08:06:46（UTC+8），timeout PID 344、Python PID 414，CPU 6–11。先 `run_hold_aware_sky130.sh gcd`，再串行 `run_hold_aware_sky130.sh ibex`。新原件路径为 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_hold_aware_v1` 与 `/home/toylog/faeco_tcad_ibex_20261123/ibex_hold_aware_v1`。每设计外层限时 2400 s，单候选 DRT/RCX 1500 s，逐角 STA 180 s，SEC 210 s。使用原内嵌导引，零编辑预检仅复提寄生。新臂显式启用 `--hold-aware-only`，固定四线程、批宽 3、六次物理调用、原比例 setup/hold 等联合门、720 RAW s 和 0.01% 功能面积目标。实时 CPU 负载与原固定臂对比单列。[实跑入口](tcad_ibex_20261123/run_hold_aware_sky130.sh)
- **GCD 配置绑定** GCD 配置 SHA-256 `367c379153493be773dc88a8e0f917c5465bfba5f0e50fe9e79f9774b66f5282`，同原筛选池输入和原矩阵设置。新规则延后的拆分在未访问候选用尽且有余额时按队列顺序处理，末槽顶层派发为单门。
- **AES 保护实跑启动** WSL 进程 08:06:58（UTC+8），外层 PID 505、Python PID 507，第一零编辑 OpenROAD PID 516。`aes_selective_drt_repair_v1/inputs.json` SHA-256 `4da01601ebad9faf83dbf8c320a7f4e1a5f633080d123dbd7b02b23c5f7e6792`。原定 CPU 0–5、四线程与各阶段限时；每次详细布线后单列全块 DRC（含 PDN）和天线检查。[执行入口](tcad_ibex_20261123/probe_aes_selective_repair.py)
- **AES 首次零编辑工程退出** DRT 到 0 个详细布线违规并打印完成标记后，二进制报 `invalid command name "check_drc"`，阶段 rc 1，用时 135.687877 RAW s。该零编辑未完成 RCX、STA、SEC；第 2 次换门候选随后启动但在定位检查接口故障后定向停止，第 5 次未启动。`zero/receipt.json` SHA-256 `c90e04db63aa3a2b9555a65b09ac3ebeeba257fe224d287821910139abff0eb7`。保留原件，同配方检查方式的修正另起版本。
- **调度 GCD 实跑完成** `gcd_hold_aware_v1/results.json` 状态 `matched`，SHA-256 `06a792e375a59425d944ee161f83f7e2baddd9129cd66aa5e656bea290a21465`。六次调用均为实跑 DRT/RCX，18 次 STA，1 候选 SEC，无缓存。第 5 次排名 13–15 通过全部门并证明 262/0，原起点 4797.1008，候选 4785.84，回收 11.2608（0.234742%）。含筛选首达 154.336399 RAW s，搜索 101.815727 RAW s，720 s 窗的六次前缀保留该端点。原固定臂与新达标端点的 ODB、DEF、V、去日期 SPEF 及三视图 setup/hold WNS/TNS 一致，新端点没有新增负 setup 端点，SEC 收据 SHA-256 `bb06ee5678dd7562da00822cfef5199f6411e5f1c4cf1e66d7e7ac2d7340dceb`。
- **Ibex 实际启动及调度回归** 08:10:07（UTC+8）在 GCD 之后串行开始，CPU 6–11，WSL 外层 PID 1412、驱动 PID 1413。`ibex_hold_aware_v1/config.json` SHA-256 `9767375585468175167bceb42eea5a10e11e87e67d550986d3337604d0d2f85f`。GCD 独立物理核验返回 0，逐一对齐了原固定臂的六个物理端点。两组原 ASAP7 同目标轨迹的 setup-only 拒因经新调度只读回放，末端、接受逻辑和面积 0.26244 精确复现。ASAP7 没有新增物理调用。[GCD 核验](tcad_ibex_20261123/HOLD_AWARE_GCD_VERIFIED.json)
- **AES 检查接口修正重跑** 工具源码显示全块检查入口位于 `drt::check_drc`，v2 用已存在的 Tcl 命令，其余试验设定、候选和限时保持原预登记。08:10:24（UTC+8）开始，WSL 外层 PID 1474、Python PID 1476，CPU 0–5。`aes_selective_drt_repair_v2/inputs.json` SHA-256 `eaefbf4b9bf25fd45edccfdd2cfc39888e7fac568f9b7c43df722e6baa8b9e25`。v1 驱动按启动时字节另存 `producer_v1.py`，SHA-256 `26a38b0d013e5d8ef90a1b8e42fe208931361bc8a76f76d6d75ea1c60314d183`。
- **调度工程回归** 针对性集成回归 104 项全通过，19.21 s，覆盖原 setup/端点/串行验证、物理评估和新拒因调度分支、延后队列。六个新旧 GCD SPEF 仅删除 `*DATE` 后均字节匹配。[调度报告](tcad_ibex_20261123/HOLD_AWARE_REPAIR_REPORT.md)
- **AES v2 保护未加载** 输入补丁 NETS 区 15,657 条 `FIXED`，零编辑输出 NETS 区 0 条 `FIXED`。已完成 1 DRT/RCX 和 3 STA，详细／全块 DRC 与天线报告均为空；改变的六条网和三视图 hold 值与普通零编辑精确一致。零编辑收据 `924f8a35376b79baa4fd2c4e23ae7ebc1536890b07b639ae1b770e09aff55c48`，v2 原源码副本 `1cc1fd925be452a0d5dd2d2a9f97d0bd9f6089c559e8f95da324f3e1262c4cf4`。v2 第 2 次后续候选仅部分执行，定位到增量 DEF 未注册 NETS/路径回调后停止，第 5 次未启动。替代模式将在 DRT 前从实际导出校验载入状态，在 DRT 后回读保护几何。
- **AES v3 已启动并回读保护** 绑定 AES 实际 Bazel OpenROAD SHA-256 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`，对应 OpenROAD 源提交 `b511b6a2bc936844b0319efc8b4972bb4ad7d911` 的 `src/odb/src/defin/definReader.cpp`，仅 FLOORPLAN 等读法注册 NETS 路径回调。新目录 `aes_selective_drt_repair_v3` 于 08:13:55（UTC+8）运行，外层 PID 2651、驱动 PID 2653、首个 OpenROAD PID 2661，沿原候选、预算与 CPU 组。输入清单 SHA-256 `4b5bdd408989a76552e72ce00843db6c43edf09e1ab0be012f15ac6d800d89e0`。零编辑在 DRT 前实际回读 15,657 条 `FIXED`，后续重新检查逐网几何和原联合门。
- **AES 恢复常规走线状态的 DRC 审计规格** 同版本 `FlexGC_main.cpp` 对部分 `FIXED`–`FIXED` 规则检查跳过标记。以未修改的 CONTROL ODB、原导引和几何运行 `drt::check_drc`，生成 ROUTED 状态下的全块参照。对可能通过原门的保护候选，在副本仅把走线类型恢复为 ROUTED，复用同一检查，比较实际 marker 数和来源，校验状态标志与几何作用。CPU 4–5、单线程、120 s，原件目录 WSL `aes_unlocked_drc_audit`。该 DRC 审计与 DRT/RCX 和策略墙钟分账。
- **AES 解锁态 DRC 的 CONTROL 参照** 08:15:19（UTC+8）开始，PID 2830/2832、CPU 4–5、单线程、外层 135 s。`aes_unlocked_drc_audit/control/inputs.json` SHA-256 `488048508610ad07ce087cfe830b83f8e92e516eb6e86cccb3833fbd16f21201`。审计实际 28.687035 s（WSL 单调钟），标记为 0，重新导出的 DEF 与原 CONTROL 字节一致。收据 SHA-256 `e1083cdcaf3a420d928a6a6d586606ce13b184a71cea86d62c2c9781211df6c6`。[审计入口](tcad_ibex_20261123/audit_aes_unlocked_drc.py)
- **AES v3 零编辑终点** 三角 setup/hold WNS/TNS 精确复现冻结起点，新鲜 DRT/RCX 后详细布线、全块 DRC 和天线报告为空，零编辑两态证明 11089/0。主收据 SHA-256 `cd117d9f7c654a81e032f7b4172a833cbe58d64b1076b3eba16ab1381b1e99d5`，证明 SHA-256 `796a960012646d371022a4fdb55c42a4a7d60facb1eebb309789c53bc49c85d7`。外层审计因连接端子写出顺序变化报差，独立对无序端子排序且统一保护标签后 15,657 条实际 NETS 几何与连接全部匹配。两个候选继续执行。
- **AES v3 强保护第 2 次与局部修复规格** `aes_selective_drt_repair_v3/02/receipt.json` SHA-256 `e21b659dad3414635e595b65c96edb276d3c8a3ffdcb4bfd179aa2c02f1e04eb`。原逐角时序门通过，面积减 33.7824，路由自身 DRC 与天线为空。额外全块 DRC 的一个 met1 间距、三个 met1 短路使该端点拒收，报告 SHA-256 `a71a8c915a1c8780042d4cd4684768410a35822336187bd94f4fc1a04cc151c1`。下一独立目录 `aes_selective_drt_repair_v4_02` 只释放报告所指两条非时钟邻网 `net8407` 与 `net4840`，与九条候选触达网一同重新布线，其余网保持保护。CPU 0–5 四线程与原各阶段限时保持，验收包括解锁态全块 DRC。根据本次实际标记定向修复，候选策略的推广性能仍待验证。
- **Ibex 第 3 次到达已知合格端点** 新臂第 3 次 DRT/RCX、三角 STA、原联合门和 SEC 13648/0 实测通过，22.5216（0.015574%），FF/TT/SS 无新增负 setup 端点。第三次收据 SHA-256 `2b07a6474f31d0e33da7774c2927d23485970cb392fe3d9222d5da8661422fdd`。剩余三次继续。
- **AES v3 第 5 次与零编辑复核** 第 5 次面积减 33.7824，FF/TT/SS hold WNS 分别较原 CONTROL 下降 0.029921/0.046019/0.283107 ps，正式相对 hold 拒收，亦有 4 个 met1 全块 DRC 标记。第 5 次收据与全块 DRC 报告 SHA-256 分别为 `d8bfee96dba7ccab54438aa9f7a701780f3a741113217bb04a13cd469f99d78e`、`bd3802bf6c670b631cfe0046855dded70ac2ea385a5376c3c31c1c5f1c1b9577`。根据报告登记另一候选释放 `_08784_` 与 `_03615_`，延续解锁态全块 DRC 与原联合门。规范化后的 v3 零编辑复核结果 `aes_selective_drt_repair_v3_qualify_zero/results.json` SHA-256 `10fd88081ea13f1d6930daec21039a7185c4f04bb088551b18748578cf4b8e9b`，保持原物理几何与三角时序，恢复 ROUTED 后全块 DRC 0，SEC 11089/0。
- **AES v4 第 2 次实跑启动** 08:21:54（UTC+8）开启 `aes_selective_drt_repair_v4_02`，外层 PID 5064、驱动 PID 5066，CPU 0–5、四线程、外层 990 s；`inputs.json` SHA-256 `1da63f98478b215ce7845b77c5323f522eea2f44c7b74b8cb69a89c6317eb1c0`。在 DRT 前读回 15,646 条保护网和 11 条计划放行的数据网。
- **AES v4 第 2 次局部路由初验** DRT/RCX、3 STA 已完成，DRT、保护状态全块 DRC、天线无标记。面积减 33.7824（0.028996%）；FF/TT/SS setup WNS 变化 −0.084821/−0.157652/−0.007105 ps，hold WNS 变化 +0.000056/0/+0.610845 ps。初验结果 SHA-256 `777f606a422634155b7214c1a15b4a91ebf6fc851f88c4c968c7c968f4e13ec0`，实际几何、ROUTED 状态的全块 DRC 和 SEC 继续校验。
- **AES v4 第 2 次几何回读及新增负 setup 端点检查** 15,646 条保护网全部未变，恰有 11 条允许放行的数据网改变。原 tradeoff 门允许新增过零端点，SS 记录新增 `text_out[83]$_DFF_P_/D`。按冻结起点的 SDC／Liberty，对 CONTROL 和实测候选各执行一次只读单线程 SS STA，绑定该端点并保留确切 slack，每次限时 45 s。新增端点的诊断耗时与路由、SEC 分账。
- **AES v4 第 2 次正式候选验证完成** 规范化实际输出几何后，恢复 ROUTED 的全块 DRC=0，实际候选两态 SEC 11089/0、rc 0，SEC 外层 24.608021 RAW s。验收收据 `aes_selective_drt_repair_v4_02_qualified/results.json` SHA-256 `410d42e0258080e1df55918fcf53dda31f18807a71b452c782e86e49fb128ee5`，解锁态 DRC `f4b4d96c7953082f21ec43e92441d954eec5f013212f095ad6936975dbc4d8f0`，SEC 收据 `a5046e65973d6fa6a3a6ef7ebdc5bd45990352de16bbd4f2db1d471da4b87082`。面积降低 33.7824（0.028996%），三角绝对/相对 hold 通过，SS TNS 较原 CONTROL 降 −103.000275 ps，新增 1 个 SS 负 setup 端点，原 tradeoff 联合门通过。这里采用事后选定的邻网定向修复。原六臂矩阵保持其历史结果。
- **AES v4 第 2 次 SS 过零端点复测** 两次只读 STA 从冻起点和修复端点实测同一发射到捕获路径 `u0.w[1][19]$_DFF_P_` 到 `text_out[83]$_DFF_P_/D`，slack 从 +0.329958 ps 到 −0.228706 ps。精确值见原始日志，派生结果 `aes_selective_drt_repair_v4_02_named_setup/results.json` SHA-256 `cc4c7a534542c23b091b9adc2f2e410c3c88371b2661f1cbe26c79ab9d1b2111`。
- **AES v4 第 5 次局部放行启动** `aes_selective_drt_repair_v4_05` 于 08:26:59（UTC+8）开始，外层 PID 7213、驱动 PID 7215、首个 OpenROAD PID 7360，CPU 0–5 四线程，外层 620 s、逐阶段限时同例 2。放行原候选触达九条网与 `_08784_`、`_03615_`，实际读回 15,646 条 `FIXED`。输入清单 SHA-256 `39d56084305710bb36de94351673e99b536ba33f674ad573643b65823d9e4303`。
- **AES v4 第 5 次局部放行结果** 完成 DRT/RCX 和三视图 STA，面积减 33.7824，DRT、保护态全块 DRC 与天线报告均为空。FF/TT/SS hold WNS 分别较原 CONTROL 下降 0.022204/0.034306/0.054623 ps，绝对 hold 保持非负，原相对 hold 门拒收，未触发候选 SEC。结果 SHA-256 `6ae8017f69f7826058fc94317a97fd2d73cd7a1abfdccf8e4c2b8c504af45da9`，物理收据 `28c7cd09549eeaaa4243870009c05eab26886cf85a31da8bc8a36b9e4e30cf6c`。
- **AES v4 第 5 次终态及封存** 规范化后仅方案内 11 条数据网几何改变，15,646 条保护网不变，恢复 ROUTED 的全块 DRC 为 0，原三角相对 hold 拒收且无候选 SEC。最终复核 SHA-256 `3ba9c7f56a4060138ea0982df7c71e15bdef525e97539f611815f9d3b0ab115b`。本轮 10 个 AES 运行与验收目录归档 `scratch/tcad_ibex_20261123/aes_selective_drt_repair_20261124.tar.gz`，157,214,689 字节、252 个成员；224 个普通文件对原件 SHA-256 逐项核对。包 SHA-256 `e69ad275ab7f9636a4b0cef12f7438eb4fd584fffefc93d934926042bdb36dc5`。[AES 保护路由报告](tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)
- **调度 Ibex 实跑完成** `ibex_hold_aware_v1/results.json` SHA-256 `ad8c890e09f7c0dc7f37c47a102336044616da2432555fe3e98f6e96b78c894b`，六次实际 DRT/RCX、18 次 STA、3 次候选 SEC、0 缓存。搜索首达 522.567420 RAW s，含 129.454710 s 筛选首达 652.022131 RAW s，720 s 窗内回收 22.5216，六次内最佳 62.56。六次动作、接收决定、ODB/DEF/V、去日期 SPEF 和三视图 setup/hold WNS/TNS 与原固定臂逐次精确相同。GCD、Ibex 合计 12 次 DRT/RCX、36 次视图 STA、4 次候选 SEC、缓存 0，共同起点与零编辑复提预检另计。[调度报告](tcad_ibex_20261123/HOLD_AWARE_REPAIR_REPORT.md)
- **调度独立核验与归档** GCD、Ibex 独立程序核验均 rc 0，最终针对性回归 104 项通过、13.37 s。调度归档 `scratch/tcad_ibex_20261123/hold_aware_sky130_repair_20261124.tar.gz`，140,315,265 字节、368 个成员、330 个普通文件逐项核对原件。SHA-256 `d9116bfed26a0f11563ec3d6dafc1e8307ed43431ed6824828352996910318b8`，额外读取包内两份 `results.json` 确认文件摘要与原件一致。[Ibex 核验](tcad_ibex_20261123/HOLD_AWARE_IBEX_VERIFIED.json) · [GCD 核验](tcad_ibex_20261123/HOLD_AWARE_GCD_VERIFIED.json)

### 2026-11-24 TCAD-SKY130HD-TARGET-COST-AND-AES-RESIDUAL-HOLD-V1

- **首达成本分解预登记** 起始代码 `b0c8477f`。读取已核验 Ibex/GCD 原固定臂与修复调度，在完全相同面积目标、起点和首达物理端点上，逐候选分解 DRT/RCX、三角 STA、SEC 及其余开销，冻结筛选成本单列。原实跑负载不同，差值只支持定位下一步优化对象。按分解结果选择需要实际优化的阶段，明确实现、资源偏好、运行顺序和限时，再用新的匹配基线做实跑。保留原 IO/SDC、三视图 setup/绝对与相对 hold、电气、DRC、非空 SEC、0.01% 面积目标及已登记的计时口径。报告相同目标的真实首达、面积和阶段耗时。
- **AES 第 5 次残余 hold 预登记** 从 v4 第 5 次真实物理收据中核对原 CONTROL、实际变更网、FF/TT/SS 最差 hold 端点、寄生与相对退化。按归因选择有限物理替代，至少保留原 SDC/IO、三角联合门、实际路由、后提取和相同功能面积口径，候选若入围则复核恢复 ROUTED 状态后的全块 DRC、天线和非空两态 SEC。计划 CPU 0–5，动作、原件目录、边界和阶段限时另绑。[上一轮 AES 修复](tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)
- **AES 交叉归因规格** 从 v2b 冻结 CONTROL 与 `aes_selective_drt_repair_v4_05/05` 取 ODB 与 SPEF，逐角实行 CONTROL/候选四种组合，实际做 12 次只读 STA，分别核对最差路径、注解和标量，并展开九位小数路径，逐网核对发射/捕获时钟树与数据网 RC/Cc。CPU 0–5 每次单线程、90 s，整批 180 s，原件 WSL `aes_v4_05_residual_cross_v1`。有限物理替代优先保留原合法布线或去掉主要诱因的一门 XOR，若保留两个原降档则目标净回收 22.5216（超过 0.01%）。物理四线程，DRT/RCX 240 s、逐角 STA 180 s、SEC 210 s；动作和实际路径待候选绑定。
- **首达成本只读分解完成** 对原固定臂与修复调度的 Ibex 第 3 次、GCD 第 5 次同目标检查点，累计每次物理及证明实际用时。Ibex 搜索差 89.499488 RAW s，内部 DRT/RCX、STA、SEC 和余量差分别为 +63.691227、+11.213296、+13.990065、+0.604900 s。GCD 搜索差 8.087160 s，对应 +5.552594、+2.446877、+0.066639、+0.021051 s。筛选耗时各自共用，并未产生差值。两对原件的动作与工具次数逐次相同，计时来自不同运行负载，并作为优化方向的诊断。新增物理成本为零。
- **AES 交叉物理端点绑定及启动** 08:38:41（UTC+8）启动，外层 PID 448、Python PID 450，CPU 0–5，单次单线程。WSL `aes_v4_05_residual_cross_v1/inputs.json` SHA-256 `ae3ee9d11c344210a343dd913ce96246d3aaf45cab0bc7a51452c2263c64af30`，原 CONTROL 和 v4 第 5 次实际候选物理收据绑定于清单，首项 FF CONTROL×CONTROL 复现原值。[交叉入口](tcad_ibex_20261123/probe_aes_residual_hold.py)
- **筛选并行实跑预登记** 用 Ibex/GCD 的原 CONTROL、固定 SPEF、TT Liberty、原排序及筛选规则。每个候选 OpenROAD 单线程，比较 1 路与 4 路独立 STA，用有界波次按原序提交结果，探针数不超过串行最先取得 18 个通过的前缀或 32 次尝试上限。预定六臂 `ibex 1 a1`、`ibex 4 a2`、`gcd 4 a1`、`gcd 1 a2`、`gcd 1 b1`、`gcd 4 b2`，在 CPU 6–11 串行。原件根 WSL `/home/toylog/faeco_tcad_screen_workers_20261124_v1`，单臂外层 420 s，单次 STA 180 s，用 RAW 时钟。核查筛选池 SHA、全部候选度量和接受/拒收序列，报真实筛选与总体准备时间，并核对 GCD 逆序差值，在共同物理下游耗时尚未实跑前保留筛选组件范围。AES 并发作为运行背景登记。[筛选执行入口](tcad_ibex_20261123/run_screen_workers_benchmark.sh)
- **筛选实跑启动及命令修正** 首个命令缺共用解析器必填的 `--sec` 参数，在创建臂输出前 rc 2，零实际 STA。包装入口补充原 `prove_ibex.py`／`prove_holdout.py` 的路径，筛选仍无 SEC。修正后第一臂 `ibex_a1_w1` 于 08:40:21（UTC+8）实跑，外层 PID 760、驱动 PID 763，CPU 6–11。针对性测试 8 项全过，其中新增 1、2、4、8 路场景均复现相同串行试探前缀。
- **AES 残余 hold 交叉结果与双门候选规格** 三视图 12 次 STA 全完成，原候选的三角微降恰由更新 SPEF 复现（FF/TT/SS −0.022204460/−0.034305891/−0.054622973 ps），保持旧 SPEF 只换 ODB 三角均等于 CONTROL。最差路径不变。`clknet_3_1__leaf_clk` 电容差 +0.0000345 pF，SS 数据到达延后 0.101567 ps，部分抵销捕获侧延迟。交叉结果 SHA-256 `3cf2ea52a82fbf547fffd2c4b1b897a43113fe0327796f13f2bcd29262969bed`，路径网电容差 `a4ad73d6f303f273ad36523bb90426feb4d3fcd41320a36213f4332471581064`。从几何和耦合邻近选取一项对照，保留 `_20893_` 及 `_20897_`，撤掉 `_20883_` 与原邻网 `_08784_` 的放行，只保留 `_03615_` 放行，预估面积差 22.5216。目录 `aes_v4_05_subset_drop_20883_v1`，CPU 0–5、四线程、外层 650 s，各阶段 240／180／210 s。
- **重复 pin access 组件对照预登记** `probe_duplicate_pin_access.py` 比较原 Tcl A 与删除唯一显式 `pin_access` 行、保留 DRT 内 pin access 的 Tcl B。锁定已验收的 GCD 第 5 次（筛选排名 13–15）和 Ibex 第 3 次（7–9），每个设计按 A→B→B→A 串行。CPU 6–11、四线程、64 个 DRT 迭代上限，DRT/RCX 限时 1500 s，三角 STA 分别 180 s，SEC 210 s。目录 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_pin_access_ab_v1` 和 `/home/toylog/faeco_tcad_ibex_20261123/ibex_pin_access_ab_v1`，计划整批外限分别 720/1350 s。每次新的物理/时序评估及 SEC 均比对输入、联合门、换门动作、ODB/DEF/V、去日期 SPEF、三个视图和邻网改线；不一致时仅用于物理差异诊断。筛选组和本组不并发占用同一 CPU 组。既有首达的显式 pin access 日志约 Ibex 106 s、GCD 16 s，记录为工具日志粒度，与墙钟对照分开。
- **AES 双门候选启动与寄生表修正** `aes_v4_05_subset_drop_20883_v1` 于 08:41:30（UTC+8）运行，外层 PID 991、Python PID 993、OpenROAD PID 1018，CPU 0–5、四线程和 650 s 外限。`inputs.json` SHA-256 `2f5e36557f58b29b4b360a8a0ea1d10c6402f53bb41aff808eefe41e4f96b3fd`，布线前 15,650 条 `FIXED`、7 条计划放行网。将 SPEF 耦合归属改为从各行两端识别本地节点，新表 `aes_v4_05_residual_caps_v2/path_net_cap_deltas.json` SHA-256 `5e953bd49b63579aa1b669227606f46ce4313d44d0b708a45bf5a09429bc0126`，对应近邻 `net8069` +0.000003600 pF、`_20134_:A` +0.000001090 pF。原交叉 12 次 STA 不重跑。
- **AES 首个双门候选终态与第二候选规格** 撤 `_20883_` 的对照完成 DRT/RCX 和 3 STA，面积减 22.5216，保护态 DRT／全块 DRC／天线报告为空，FF/TT/SS 相对 hold 变化 −0.008105／−0.012546／−0.166533 ps，未全部保持原门，SEC 为 0。物理收据 SHA-256 `053e2addc7d90da71560e0b11a7819f3d567ce2b8bb7ace5836068ce26c3c359`，结果 `5026f2126c852685e4af1ba74890daf45aa67801fe509230deb9986b8f9c07e6`。第二对照保持 `_20883_` 和 `_20893_`，撤掉 `_20897_` 及其短路近邻 `_03615_` 的放行，保留放行 `_08784_`。计划 `aes_v4_05_subset_drop_20897_v1`，同 CPU 0–5、四线程、650 s 外限及原阶段预算和门。
- **Ibex 1→4 路筛选计时收齐** 两臂各扫描 18、通过 18，全部动作、扇出、指标、拒因和顺序与原池及串行一致。池 SHA-256 相同 `4c393545b7d356002bd4fc3bf534b686bf1ee3da170b70469359d796f1f984e0`，两臂筛选收据 SHA-256 分别为 `c52cafc28631ec1c6ba83d4ae2af61ec09af7091f4f7542da8571d740420411a`、`991d99171be9be75883f6f042e97dabbcf227c05dffa289d1d0b09c5145340b7`。组件端到端筛选用时 131.940646／77.493270 RAW s，实际少 54.447376 s；GCD 交换顺序试验尚在执行，物理搜索计时单列。
- **AES 双门解锁态复核及第二实跑** 首个双门对照 `aes_v4_05_subset_drop_20883_v1_qualified/results.json` SHA-256 `a272f0875c90711553e76951e78d176e61ce6a19c7fc67a570c3a338fd0af683`，解锁态全块 DRC 0，三视图相对 hold 仍拒，候选 SEC 为 0。撤 `_20897_` 的第二个双门对照 08:44:43（UTC+8）启动，外层 PID 2233、驱动 PID 2235、首个 OpenROAD PID 2240；`inputs.json` SHA-256 `411cd9bb20cf6ac3d76189f44181d0d117d7c7cb1298470b8c44718ce850c4ba`。同 CPU、650 s 外限和原逐阶段设置，读回实际 15,650 保护与 7 放行网。若该组合也被原门拒收，拟补互补组合 `aes_v4_05_subset_drop_20893_v1`，撤 `_20893_`，保留另两门及邻网 `_08784_` 和 `_03615_` 的放行。
- **GCD 两对筛选完成** 4→1 四路／单路耗时 37.271200／50.709156 RAW s，1→4 单路／四路 51.951921／39.206443。分别节省 13.437956 和 12.745479 s，四臂均扫描 20、通过 18。与原冻结池的每次动作、扇出、指标、拒因和顺序精确一致，池 SHA-256 `ede7990f6f7f4c7ff26cd9c9bd9cc506d5bd4281258cc7118e8a66c33568f40b`。六臂筛选合计 116 次候选 STA，历史实跑的筛选/物理搜索时间仍各用自己的收据。
- **GCD 重复 pin access 对照启动** 08:47:23（UTC+8），PID 3520/3521，CPU 6–11，四线程和 720 s 外层限时。`gcd_pin_access_ab_v1/config.json` SHA-256 `7d66fd51565e2b033b13d84ef76568130aea00a4b3465d404aacc90638a566d3`，筛选队列已完结。原 DRT 零 DRC 早停和 64 次上限保留，唯一变化为去掉重复显式 `pin_access`。[对照报告](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- **AES 第二双门物理结果** 撤 `_20897_` 的实跑完成 DRT/RCX 与三角 STA，面积减 22.5216，DRT、保护态全块 DRC 与天线为 0。FF/TT/SS 相对 hold −0.014100／−0.021705／+0.171640 ps，FF/TT 超过原容差而拒收，候选 SEC 为 0。原始物理及臂结果 SHA-256 为 `2e8fed57d5f5af9ca8853980bc62dc611125fdc1692d00a1330ff8f5d44ee5c2`、`360785cbeb81eba99924399dccb7473c043e09ea9379c7ce20050e156bc5bec5`。恢复原线型的几何及全块 DRC 单列。
- **AES 第二双门复核及第三组启动** 第二组恢复 ROUTED 状态后的全块 DRC 为 0，仍因 FF/TT 相对 hold 拒收，终态 SHA-256 `bb924a849428fd6243f14b475bf7ee9165c47868f319da1a38f1059243b30031`。第三组于 08:48:06（UTC+8）启动，PID 3774/3776，首个 OpenROAD PID 3779，按预登记撤 `_20893_` 放行两条非时钟邻网。`aes_v4_05_subset_drop_20893_v1/inputs.json` SHA-256 `bc3de286d99ad2df44ec3e5baf0394b2570bb8421c802821518a351bfe03284b`。
- **并行筛选独立核验与封存** 六臂和独立核验均 rc 0，各设计的两种模式均复现原候选顺序、指标、寄生注解和池哈希，无额外候选探针。两项 GCD 计时改善 26.50% 和 24.53%，Ibex 41.27%，仅计实施筛选阶段。归档 `scratch/tcad_ibex_20261123/screen_workers_20261124.tar.gz`，1,466,414 字节、555 个成员、402 个普通文件按原件 SHA 核验；包 SHA-256 `cade6fdda4dd84a6f7cd0251ba88f19bd8e6ad81473d3e5372c084d510ba6148`。[筛选报告](tcad_ibex_20261123/SCREEN_WORKERS_BENCHMARK.md) · [独立核验](tcad_ibex_20261123/SCREEN_WORKERS_VERIFIED.json)
- **GCD pin access 首次预检与重试** 首次完成共同 CONTROL 和零编辑预检后，候选入口回调参数数目不匹配，进程 rc 1，0 候选 DRT/RCX、STA 或 SEC。保留 `gcd_pin_access_ab_v1`，修正签名后以 `gcd_pin_access_ab_v2` 继续，08:48:13（UTC+8）、PID 3812/3813，CPU、线程、限时、顺序与输入不变。新配置 SHA-256 `9b8ac25e272cb4ad05cad3e0762a169daa1be33bd243156a972cd1d6d2e22d04`。
- **AES 等面积替换预登记** 三选二后保留第二双门对照中的 `_20883_`、`_20893_`，以原筛选固定第 6 次实测的 `_21033_` 降档代替 `_20897_`。该单门历史候选对普通零编辑的 FF/TT hold +0.063172/+0.099032 ps、SS 0，13 条最差路径网中发射支路 `clknet_3_0__leaf_clk` 电容增加 0.0001006 pF。放行 `_08784_` 与穿过新目标框且原单门候选曾改线的 `net8148`。计划 WSL `aes_v4_05_donor_launch_compensation_v1`，CPU 0–5 四线程、外层 650 s、先前同物理与验收预算。目标面积减量 33.7824，完全以新物理端点三视图及各联合门确认实际性能。
- **GCD 去重复 pin access 四臂完成** `gcd_pin_access_ab_v2/results.json` SHA-256 `417f2aa81cc7ea713d92b9b17647d065fa6889aff9a9dab1584354edd236b0d0`，4 DRT/RCX、12 STA、4 候选 SEC、无缓存。A、B 皆回收 11.2608，通过原联合门。两对单端点评估时间的 A−B 差值 3.100760／3.448795 RAW s，操作实际 pin access 次数 2→1。DEF、V、去日期 SPEF、三角读数、DRC、邻网几何和证明点与历史一致。B 的 ODB 字节不满足原全对象一致判据，具体差异另做审计，当前结果保留为组件阶段差范围。[对照报告](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- **Ibex 去重复 pin access 四臂开始** GCD 退出后，08:50:29（UTC+8）在 CPU 6–11 串行启动，外层 PID 4663、驱动 PID 4664，四线程、1350 s 外层限时。`ibex_pin_access_ab_v1/config.json` SHA-256 `5a4060c8d7a35263b9b3e700547919d2455f92bf3f98e0a6fbe9f157c6282e6e`。
- **AES 三选二终态及等面积替代实跑** 三个双门候选均完成物理与三视图评估、解锁态 DRC，原相对 hold 拒收，未调用候选 SEC。第三组撤 `_20893_`，FF/TT/SS −0.022204／−0.034306／+0.099476 ps，终态 SHA-256 `e1fb1c9c4bb4c35fb96f6f82d8642c3913ce5b1e739c1729e7d5974110322e8f`。等面积替代按预设于 08:51:26（UTC+8）启动，外层 PID 4869、驱动 PID 4871、OpenROAD PID 5037，冻结范围 15,646 条并清线 11 条。`aes_v4_05_donor_launch_compensation_v1/inputs.json` SHA-256 `a1d1893accb95ffea4581021af7fc439f31537dc4751a79ec59df59fc6663889`，旧单门参照及同路径寄生审计 SHA-256 `4d79c58b8a36c001205ea3f7c107ccb52f9c91cbac78f35aeab0f752de1c1387`。
- **AES 等面积替代的物理与时序初验** DRT/RCX、3 STA 完成，面积减 33.7824，保护态 DRT/全块 DRC/天线无标记。FF/TT/SS hold WNS 改善 +0.048961／+0.076883／+0.171640 ps，setup WNS 变化 −0.001332／−0.002220／−0.003553 ps，三角无新增负 setup 端点。物理收据 SHA-256 `fbdb05190606a10e5bfcf3735930c59571dc54efe8c2181e6fe0aef1380be820`，初验汇总 SHA-256 `3b257f29950a66ab0319d02f9175a3be4326f7ac7ef2a8697294a99fc1038fe1`。恢复 ROUTED 后的几何与全块 DRC 和候选 SEC 继续核对。
- **AES 成对路径诊断规格** 对带 SS 正裕量增量的第二双门候选和等面积替换，各按自己的实际 ODB/SPEF 绑定、原 SDC 与对应 Liberty 实跑三视图只读匹配路径，共 6 次单线程 STA，每次 45 s。固定各角路径发射和捕获端点，确认边际时钟到达与最差 hold slack，单列诊断成本。
- **AES 等面积替代正式验收及成对路径结果** 按几何同一条件恢复 ROUTED 后，全块 DRC 0，保护网 15,646 条全部未变，11 条变线均在放行范围，三角原联合门及候选 SEC 11089/0、rc 0。`aes_v4_05_donor_launch_compensation_v1_qualified/results.json` SHA-256 `2541b0d52fdccb53c1d11a419684955ee7ba83a705b74d000885d47c5f73d857`，SEC 外层 21.060984 RAW s，证明实际 gate 网表 SHA-256 `55f2e09803d4d780bb2d42ee035b437c3f93480b6f5d53831bd5d17187c9fd51`。面积减 33.7824（0.028996%），没有新增负 setup 端点。另做 6 次实际匹配路径 STA，两端点 FF/TT hold 差 +0.063061/+0.098588 ps，数据到达延后而要求到达时刻不变，SS 精确一致；配对结果 `aes_v4_05_donor_paired_exact_v1/results.json` SHA-256 `f9789a535f8ecacd2476f94ea12e49bceec473129cfae1a8c61bb17f3a3bb26d`。
- **AES 两个三门端点联合验收预登记** v4 第 2 次资格 SHA-256 `410d42e0258080e1df55918fcf53dda31f18807a71b452c782e86e49fb128ee5` 和本轮等面积替代资格 `2541b0d52fdccb53c1d11a419684955ee7ba83a705b74d000885d47c5f73d857` 均为正式通过，单元和放行数据网无交。合并 `_11178_`、`_11724_`、`_12777_`、`_20883_`、`_20893_`、`_21033_`，另放行 `_08784_`、`net4840`、`net8148`、`net8407`，共 22 条开放数据网、其余 15,635 条要求保护。新目录 `aes_v4_05_qualified_union_six_v1`，CPU 0–5 四线程、整批 650 s，DRT/RCX 240 s、每视图 STA 180 s、SEC 210 s，只做一次确定组合。目标净面积减量 67.5648，仍须重布线、复提取、原三角联合门及恢复 ROUTED 状态的 DRC、天线和非空 SEC。
- **Ibex pin access 首对收据** A→B 单端点评估时间 186.113393／139.386816 RAW s，DRT/RCX 129.659367／83.862256 s。两者均回收 22.5216 且通过三角和 SEC 13648/0。除 B 的 ODB 二进制外，比较字段均匹配历史同动作，逆序次对继续。
- **AES 六门联合物理实跑启动** 08:58:31（UTC+8）开始，外层 PID 8202、驱动 PID 8204、首个 OpenROAD PID 8209。`aes_v4_05_qualified_union_six_v1/inputs.json` SHA-256 `5fe523ab86aeb0715020728dc6cbae5df4b1c683f19bb54b0026e90869177193`。保持原 CPU 0–5、四线程与各阶段限时，实际输入已绑定两份验收结果。
- **AES 等面积替代原件封存** 联合之前的 13 个运行和核验目录归档到 `scratch/tcad_ibex_20261123/aes_residual_hold_optimization_20261124.tar.gz`，109,925,296 字节、233 个成员，207 个文件逐一与原件做 SHA 核对。包 SHA-256 `022cf082854c45cc1e4350b12841d505d063a2718cea9f448683c9dd1c3bc1b6` 已复验。实测配对 FF/TT 发射时钟延后 +0.062406/+0.097751 ps，捕获与要求时刻及 SS 路径不变。[AES 残余 hold 优化](tcad_ibex_20261123/AES_RESIDUAL_HOLD_OPTIMIZATION.md)
- **AES 六门未解锁态初验** 六门新实跑完成 DRT/RCX 与三角 STA，面积降 67.5648（0.057992%），保护态 DRT/全块 DRC/天线无标记，FF/TT/SS 相对 hold WNS +0.049183/+0.076716/+0.782263 ps，setup WNS −0.086153/−0.155875/−0.008882 ps，SS 有一条新增负 setup 端点。物理收据与初验汇总 SHA-256 分别为 `bb47277ab03ccf19938c34cee4ae43accce3e330efb8b714f7b858106acb3e24`、`b194d2350356b59634a21411f9878ba9fb2309d8484c2d46b1d226a46084ba76`。几何、解锁后 DRC 和 SEC 随正式资格另核。
- **AES 六门联合正式验收** `aes_v4_05_qualified_union_six_v1_qualified/results.json` SHA-256 `662ded5cb91cd2eff5bd38ca2d02d0359f0532a22b01864a65f65044111d49c4`，保护的 15,635 条网保持几何一致，实际改线 22 条，恢复 ROUTED 后的全块 DRC 为 0，原三视图联合门及实际候选两态 SEC 11089/0、rc 0，外层 SEC 23.265324 RAW s。按原 tradeoff 口径，SS 原第 2 次的新增过零端点仍为 `text_out[83]$_DFF_P_/D`，精确 slack 另测。
- **AES 六门 SS 过零复测与证明绑定** 同一条到 `text_out[83]$_DFF_P_/D` 的 setup 路径从 +0.329958 ps 到 −0.214495 ps。派生诊断 SHA-256 `681a492c6d5cd6d656bd531f844439f26d1081ac76ab745bba4f1eb784e8223c`。实际 SEC gate SHA-256 `33e0dc9a4ef42cee14a9e4505840e64e09fcb0815d95e50e973e3cf6837e26d2`，内部 SEC 收据 `64606c7c6f5686e0c701e3a88401ae7db96dc4856404b34f02d8b8517492a0d3`。
- **Ibex 去重复 pin access 四臂完成** `ibex_pin_access_ab_v1/results.json` SHA-256 `e8088035b1a4055024c1a837ad023d4308f2c3a9b5a136d0b5b737c1995d4f5f`，4 DRT/RCX、12 STA、4 次 SEC、0 缓存。两对 A−B 单端点评估时间为 46.726577／22.067014 RAW s，DRT/RCX 降 45.797112／33.884919 s。两次 B 的 ODB 字节与原对象不同，其他已登记物理、时序、电气和证明字段全部相同。原登记的全对象一致门未满足，仍以单端点阶段耗时观察记录。[对照报告](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- **AES 六门联合封存** 四个原件及验收目录归档 `scratch/tcad_ibex_20261123/aes_qualified_union_repair_20261124.tar.gz`，29,028,405 字节、56 个成员、48 个普通文件按原件逐项核验。宿主包 SHA-256 `b351d794555e0f566bce0c83038104d91a9791eedfce12fa7823c9faaf418478` 已复验。归档独立保留六门实际物理、全块 DRC、三角时序、候选 SEC 和新增负端点读数。[AES 残余 hold 优化](tcad_ibex_20261123/AES_RESIDUAL_HOLD_OPTIMIZATION.md)
- **GCD 仅显式 pin access 补充对照与 ODB 语义审计** `gcd_pin_access_explicit_only_ab_v1` 用 A→C→C→A 重跑原三门。C 保留显式调用，关闭 DRT 内置重复，四臂 4 次 DRT/RCX、12 次 STA、4 次 SEC、0 缓存，均通过原联合门且回收 11.2608。A−C 耗时差 2.484664／3.237155 RAW s，C 的 ODB 原始哈希与 B 精确一致。结果 SHA-256 `45cd7830de86fcb39ac5c2648ee5b2e00705f4ea2f61f65d871930fcca3a0d49`。各设计 AP 所属 pin／坐标／层的多重集一致，在副本中删除 AP 与关联引用后各自字节一致，GCD 哈希 `8987da52d7918dc5d7d9fead3f24e734c9e7e269e63d8c26c154667474906034`，Ibex 哈希 `56b575aae8f4e4b33aaeacac22bc221bff3d90e9201b12b218d91cdcc6525c29`。原始 ODB 字节判据与诊断副本分别报告。[对照报告](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- **pin access 封存与工程回归** A/B 和附加 GCD A/C 合计 12 次候选 DRT/RCX、36 次候选 STA、12 次候选 SEC、无缓存，预检失败与 ODB 诊断单列。归档 `scratch/tcad_ibex_20261123/pin_access_ab_20261124.tar.gz`，156,613,093 字节、494 个成员、438 个普通文件与原件逐项校验，SHA-256 `c7a043ee854c5ad862be8dd63f5afd63aff7f6f03bbb362fe09758558bb41d18`。最终针对性回归 108 项通过、17.47 s。[对照报告](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)

### 2026-11-24 TCAD-SKY130HD-SINGLE-PIN-SEARCH-AND-ODB-REENTRY-V1

- **原冻结搜索单次 pin access 前置验证** 从 `4f28ada3` 实现明确选择的单次方式。在 GCD 原合格 CONTROL、筛选池、排序、候选配额、窗口、0.01% 原面积目标及三视图联合门下，CPU 6–11 同机串行实跑默认与单次，保留实际 DRT/RCX、STA、SEC 计数与分阶段用时，核对候选顺序、接受决定、首达和相同面积、ODB/DEF/V、去日期 SPEF、逐角读数和 SEC。先判断优化是否影响完整搜索，待本前置检查再决定范围更大的新矩阵；旧试验数据保持各自配方与计时。[旧组件对照](tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- **两步保存 ODB 重入预登记** GCD/Ibex 均从已有双次、单次 pin access 各自实际保存的第一步 ODB 重入，比较下一个独立动作的 DRT/RCX、三视图 STA、原物理/电气/时序门及按门的两态 SEC。锁定同物理起点、真实中间对象和续做动作，不以去 AP 的诊断副本替代真实重入。计划 CPU 0–5，记录 ODB 字节与语义比较、路径/网及后续接受是否发生变化。输入绑定、第二步动作、预算和实际运行入口另记。[ODB 差异追踪](../OPEN_ISSUES.md#oi-1012026-11-24open-减少-pin-access-次数改变-odb-二进制身份)
- **两步重入动作与预算** 各设计 A→A、B→B、A→B、B→A 比较，其中 A 为双次，B 为单次。GCD 从已验收 ranks 13–15 的保存端点出发，追加 rank 16 `_095_→mux2_1`；Ibex 从已验收 ranks 7–9 的保存端点出发，追加 ranks 10–12（`_14570_→nor4_1`、`_464_→xor2_1`、`_476_→xnor2_1`）。原时序门和 SEC gold 保留原 CONTROL；物理只改重入实际 ODB 和几何参照 DEF，原 SDC、RCX 配方和各角 Liberty 保持。原件拟 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_pin_access_reentry_v1` 和 `/home/toylog/faeco_tcad_ibex_20261123/ibex_pin_access_reentry_v1`，CPU 0–5 四线程，外限 600／1600 s，单次 DRT/RCX、单视图 STA 和 SEC 分别 1500／180／210 s。保留候选接受逻辑，已做出完整网表而正式拒收的端点可做单列诊断 SEC，成本不计正式搜索。原 GCD 同动作直接累计评估曾因 TT/SS 相对 hold 拒收。
- **GCD 冻结搜索四臂开跑** A→B→B→A，入口 `run_hold_aware_sky130.sh gcd {double|single} /home/toylog/faeco_tcad_pin_search_20261124_v1/{a1|b1|b2|a2}`；默认 A 双次，B 经 `--single-pin-access` 显式选择单次。各臂从原合格 CONTROL 和原筛选 52.520673 RAW s 的池独立出发，实际跑 6 候选，原接受门、720 RAW s 窗和 0.01% 目标。CPU 6–11 串行、四线程、单臂 2400 s，DRT/RCX 1500 s、逐角 STA 180 s、SEC 210 s。首臂 WSL 09:15:15（UTC+8）启动，PID 350/428。对照两种顺序，记录 CPU 0–5 重入试验并发影响。显式单次入口的针对性 9 项回归通过。[冻结搜索启动器](tcad_ibex_20261123/run_hold_aware_sky130.sh)
- **冻结搜索首臂配置与重入启动** `a1/config.json` SHA-256 `b600d03d2b946f097d2b44954d4eb0c196bb72c7f7a2fafa336d3bd01307f94d`。重入实跑 `gcd_pin_access_reentry_v1` 09:15:42（UTC+8）启动，外层 PID 614、驱动 PID 615，CPU 0–5、四线程、600 s 外限，绑定已验收 `gcd_pin_access_ab_v2` 的 A/B 真实保存 ODB。重入配置 SHA-256 `30ba27763994fcddc3301310338ea8424724c52b72f361e913fd95dfbb8f4735`。[重入报告](tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)
- **GCD 双步重入完成** 四组合相同的 DEF、V、去日期 SPEF、改线和全部三角验收读数，SEC 262/0；ODB 原始字节仍有差异。相对第一步的更新回收 3.7536，相对原始 CONTROL 回收 15.0144（0.312989%），FF/TT/SS hold +0.009270／+0.125983／+0.443368 ps，无新增负 setup 端点。原一次累计四门在 TT/SS 相对 hold 分别损失 1.084438／4.336809 ps 且未通过，不能将其与重入状态当成同一次路由任务。此次共计 4 DRT/RCX、12 STA、4 SEC、0 缓存。结果 SHA-256 `7863ca59f2d956466cb9d76cb2aafc4e290b2b2f7860db1d9117c615a74aa1a5`。[重入报告](tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)
- **Ibex 重入首试工程失败及重试** v1 在换门前因从设计专用 FastRoute 反推 ORFS 根错误，找不到原 `setRC.tcl`，工具 rc 1，未完成 DRT/RCX，未启动 STA/SEC。v1 收据 SHA-256 `6436c2041b0032feeb345a590fb3172eb0293e242457d0af3fa3b7d3da14c9fa`。从原已绑定 `setRC.tcl` 确定正确 ORFS 根后，`ibex_pin_access_reentry_v2` 于 09:17:39（UTC+8）实跑，外层 PID 1685、Python PID 1686、首个 OpenROAD PID 1800，CPU 0–5、四线程、1600 s 外限。新配置 SHA-256 `8da172552e38320c4cfc5cd3029c7f9d3949164ba3d713917670abc1b773dc75`。
- **GCD 冻结搜索首对完成** `a1`、`b1` 两臂各 6 DRT/RCX、18 STA、1 实际候选 SEC、0 缓存。第 5 次首达 11.2608，含筛选的首达为 122.988636／118.739976 RAW s。两臂三角 STA 含电气的字段、去日期 SPEF 和候选判定在每次均与历史相同，实际各做双次或单次 pin access，原始 ODB 字节有差。结果 SHA-256 `c1836189c1a16641167abca1adaa50cc695c64be4e160200a5d80b4f780c90a9`、`38da6e4bf5ced86eaf4903b0d559307fc120c78cf9b6f61fd591b95335fa5bda`，未混入 ODB 重入路径。
- **首对独立核验** 两臂各自独立矩阵核验 rc 0，逐次比较 DEF、V、DRC、SPEF、逐角时序、电气、真实改线、证明与 Tcl/调用次数，实际 A/B 物理 Tcl 仅差重复的显式调用。`b1/config.json` SHA-256 `d4b59fe0b29e8e18d42e29429719f723a2f9f2d6befcf0f7123c309248552e0a`；两臂全六次未含筛选搜索时间 84.989319／80.462802 RAW s，首达前五次 DRT/RCX 56.896474／51.969708 s。补模式边界后针对性回归 11 项通过。
- **Ibex A→A 重入阶段证据** 实测 DRT/RCX、三视图 STA 到齐，累计面积候选减量 43.792。TT 新最大电容违例 `_12540_/Y`，setup TNS 相对原 CONTROL 下降 1029.633268 ps，超过原 1000 ps，TT 有 6 个新增负 setup 端点。该候选未接受，实际输出网表事后诊断 SEC 13648/0。与原冻结累计六门通过（TT TNS 改善 60.058625 ps）分开记账。其他重入方式继续。
- **Ibex 电气拒因只读路径核查** `_12540_/Y` 是原冻结累计和重入的同名最差 core_clock setup 路径的一节点。其元件和连接相同，输出 `_02456_` 的 DEF 表示字节一致，SPEF 总电容由冻结累计的 0.0659667 pF 到重入的 0.0661425 pF。重入 STA 实报 cap 0.075289480 pF，高于 0.074167997 pF 限制。此次只读核查定位一个实际电气拒因，未分解整个 TNS 差值。
- **GCD 冻结搜索四臂完成** 合计 24 次候选 DRT/RCX、72 次视图 STA、4 次候选 SEC、0 缓存。四臂均第 5 次达目标 11.2608，含同筛选收据 A→B 122.988636→118.739976 RAW s，B→A 113.860043→118.933382 s，实际 A−B 为 4.248660／5.073339 s。首达前 DRT/RCX 差值 4.926766／7.134141 s。逆序 `b2/results.json`/`a2/results.json` SHA-256 `5d488623a1db6451360fa4668125506f55d23ba29698808393dafdd888d71fa9`、`19c6baeb096c7f3469cf624947a1053de12a7b90fd86a3cf42965590318e6943`。全部 24 个物理收据的动作、逐角时序、DEF/V、去日期 SPEF、DRC、实际改线及拒因复现原冻结路径。原始 ODB 字节差异和另一 CPU 组的并发条件按本轮对照保留。
- **GCD 冻结搜索独立核验和封存** 四臂独立核验 rc 0，归一后的 Tcl 仅删除显式重复调用，实际所有物理、时序、电气、候选判定与等价读数相同。归档 `scratch/tcad_ibex_20261123/pin_access_search_20261124.tar.gz`，27,401,310 字节、713 个成员，640 个文件与原件 SHA-256 逐一相符，归档 SHA-256 `6df7e677640aa27488ca8cdd80acf7ced0a996854e3a4d17d10fcfda2c364b1c`。[搜索报告](tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md) · [独立验证](tcad_ibex_20261123/PIN_ACCESS_SEARCH_VERIFIED.json)
- **Ibex 双步重入完成** 4 次候选 DRT/RCX、12 STA、0 正式 SEC、无缓存；四个拒收端点另行诊断 SEC，均 13648/0。四组合 ODB 有三种原始哈希，A→B 与 B→A 字节相同。DEF/V、去日期 SPEF、DRC、三视图、改线、物理面积候选与验收判定逐项相同。TT 最大电容及 TNS 共同拒因、6 个新增负端点，原 CONTROL 至此累计面积候选减量 43.792（较第一步 21.2704），不计合格。结果 SHA-256 `2154326d5aad18a0b4082c8a62038d549b3633d5096fb46e9ee23871a33f7c2b`。[重入报告](tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)
- **重入归档与配置前置验证结论** `scratch/tcad_ibex_20261123/pin_access_reentry_20261124.tar.gz`，91,607,384 字节、240 个成员、213 个普通文件按原件逐项校验。包 SHA-256 `b97f444fcd0bc272f88e94afe060ef8fc3a9ed2029c22736c9c1449e2b96850d`。最终回归 111 项通过、16.29 s。下一阶段正式 SKY130 嵌入导引的同冻结起点对照，将对各方法一律显式启用 `--single-pin-access`，历史输入、失败收据及默认方式分别保留。外部导引仍用原入口，重入作为独立变量，下一阶段尚未实跑。[重入报告](tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md) · [搜索报告](tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md)

### 2026-11-24 TCAD-SKY130HD-FORMAL-SINGLE-PIN-AND-AES-PROTECTION-V1

- **Ibex 正式同池比较预登记** 从 `4d73426a`，同一个原冻结合格 CONTROL、原 I/O/SDC、嵌入 guide、相同 RCX 和 FF/TT/SS Liberty。单门、固定批次、hold-aware FAECO 使用同一验证过的有序筛选池，各最多六次真实物理调用，计划 18 DRT/RCX、54 次视图 STA，原 setup 损失包络、绝对/相对 hold、DRC、电气和非空两态 SEC 门不变。四线程、CPU 6–11 三臂串行，全程显式单次 pin access。每臂计入同一四路筛选实际耗时，共同 720 RAW s 窗口和 0.01% 面积目标。逐次记录实际操作与证明，报告首达、窗口内/六次面积、端点门和积累阶段时间，正式证据仍属于已参与开发的 Ibex 设计。若固定与 FAECO 最终轨迹相同，此轮的单次先后顺序只给运行时观察。[单次接入点前置验证](tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md)
- **AES 共享保护路由预登记** 原合格 CONTROL、原 IO/SDC、原筛选候选仍为共同输入，先将已验证的路由保护机制整理成三策略都可调用的入口。冻结通用动作放行条件后做零编辑的真 DRT/RCX，检查所有规定保护网、原三角时序、恢复普通走线类型的全块 DRC、电气、天线和非空两态 SEC。预检通过后计入每臂共用筛选及实际重布线、非法或拒收试次和候选/证明开销，三方法共用同一开放邻网规则与联合门。计划 CPU 0–5，候选选择、CPU/线程、阶段预算、配置和实跑顺序另绑。[定向修复历史](tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)
- **AES 放行规则、预检与硬计时规格** 冻结 v2b 原 CONTROL 和 `aes_matrix_v1/screened_pool_used.json` 的原顺序，沿用原 IO、36 ps WNS、各角原 TNS 包络、绝对及 0.001 ps 相对 hold、电气、DRT DRC、天线、恢复 ROUTED 状态的独立全块 DRC、SEC。先仅开放累计编辑单元的直接数据网；若 DRT 或全块的真实 marker 同时含编辑实例／编辑网和现有非时钟 `SIGNAL` 邻网，允许一次从同冻结起点只追加这些 marker 指定邻网的重试。预检严格锁线零编辑与池前 3 门，零编辑须通过几何、DRC/天线、精确三角四项时序读数、实际 SEC。通过后启动三方法，各至多 6 次逻辑申请，物理尝试和重试全部计入 720 RAW s 的端到端硬窗，单阶段按剩余时间裁剪。每臂全额计原筛选实测 113.363 s，0.01% 原面积目标。CPU 0–5，四线程，内嵌导引与 DRT 内部单次 pin access。
- **Ibex 三臂正式启动** `run_ibex_three_way_screened.sh` 于 09:40:55（UTC+8）启动，外层 PID 348、Python PID 428，CPU 6–11、四线程。执行顺序单门→固定→hold-aware FAECO，无按达标提前停止，三臂各至多 6 次实际物理验证后逐检查点计算 720 RAW s 截止。总体外限 6000 s，DRT/RCX 1500 s、逐角 STA 180 s、SEC 210 s。原件目录 `/home/toylog/faeco_tcad_ibex_20261123/ibex_screened_single_pa_three_way_20261124_v1`，`config.json` SHA-256 `91099181f80fa287ce715c283f9ee7960ab2307f97c7f6eabee79018ba1ab7dc`。采用 `ibex_a2_w4` 的已测四路筛选收据 77.493270 RAW s；池 SHA-256 `4c393545b7d356002bd4fc3bf534b686bf1ee3da170b70469359d796f1f984e0` 与原池逐字节相同。启动前针对性 14 项检查通过。[Ibex 实跑入口](tcad_ibex_20261123/run_ibex_three_way_screened.sh)
- **AES 两次早期参数修复与预检实跑** v1/v2 分别因原 SDC 比率浮点规范化和误用 Ibex 顶层的物理网表绑定在创建输出及任何 EDA 前退出。复用留出约束校验并绑定 AES 原顶层，保持原 SDC/网表。v3 `aes_protected_online_preflight_v3` 于 09:44:02（UTC+8）启动，PID 1472/1474，首个 OpenROAD PID 1485，CPU 0–5 四线程、1065 s 外限。`config.json` SHA-256 `43e8a2ead5428331bf61481474a27558835b82338dd85206ff10c9ad53a8faa8`，运行器 SHA-256 `eb569cdbc063ce75015f03121cd45b78211e3509a286d598364d2b09cc564617`，池 SHA-256 `1bd07df9ff7d5f0679f46968a19f09be4543ce2692af6e5c362b636cfd6177ce`。零编辑已读回 15,657 条 FIXED，未清线。正式三臂复用同规约的前置资格，预检候选不进入缓存。[AES 统一入口](tcad_ibex_20261123/run_aes_protected_online.py)
- **AES 单次 pin access 的真零编辑预检通过** 1 DRT/RCX、3 STA、1 零编辑 SEC（11089/0）。详细布线、原及恢复 ROUTED 类型的全块 DRC 与天线均过，15,657 条网几何保持，三视图 setup/hold WNS/TNS 精确一致。实测 155.102764 RAW s，为共享预检单列。`preflight/zero/result.json` SHA-256 `7e82889634b0d8740d1ba3af4c52cf9cd22d087ee34d02db553acdf15d016f71`，SEC 收据 `43894e6ce92f03dcd979534698e2ea2f5f8370a24a64dedbe399982d6883edef`。旧两个物理报告仅用于验证 marker 解析能指向正确邻网，正式依据当次 DRC 决定允许范围。
- **AES 首个固定组三门预检结束** 排名前三门完成新 DRT/RCX、三角 STA 和独立全块 DRC 0，119.945760 RAW s，实测候选面积减 33.7824，SS 相对 hold 下降 0.157652 ps 而拒收，绝对 SS +55.138116 ps，未调用候选 SEC。预检汇总 SHA-256 `79e6450453cecfcbf592ffd2a5fb1d8d04f5f3f2362cc7ce6c1cf79f357758d9`，零编辑通过已绑定、三门结果不进入正式缓存。
- **AES 正式同池三臂启动** `aes_protected_online_matched_v1` 09:49:14（UTC+8）实起，外层 PID 2871、Python PID 2873、OpenROAD PID 2878，CPU 0–5 四线程、外层 2000 s。配置 SHA-256 `c1b2644c615f3319b7f791bbbeaea9605a4e88920403e8009c0b2251cf311534`。顺序单门→固定→FAECO。各臂统一计原筛选 113.363032 RAW s，实际墙钟余量 606.636968 s、6 个逻辑申请上限。初始路由和最多一次真实 marker 诱导重试均使用原冻起点与同一物理判定并逐次全额计费。[AES 统一入口](tcad_ibex_20261123/run_aes_protected_online.py)
- **正式 AES 自动重试首次实际触发** 单门第 1 次 `_10814_` 与 `net8204` 在保护态与解锁态全块 DRC 有 3 个相同的 met1 短路标记，两报告 SHA-256 均 `674a46074ba582c3fb878f60dddc80c1ee72ee5a62ce50011e8b15471b9edcdd`。只追加该非时钟 `net8204`，与候选三条数据网一起在同原起点重试。首试及重试均占用同一臂剩余实际墙钟。
- **正式 AES 首个自动重试的门和成本** 独立解锁态 DRC 由 3 到 0，重试后 SS +55.187632 ps，较原起点下降 0.108136 ps，候选由原相对 hold 门拒收且无 SEC。两次物理阶段 111.394376／99.864732 RAW s，两次独立全块 DRC 各 16.102077／16.491298 s；含筛选检查点 363.328680 s。`single/01/result.json` SHA-256 `ef75a53b736ff4863705bad001ef3e9a379187b58c82deedb65c16ee28aae53b`。这是一次逻辑调用、两次实际路由。
- **Ibex 单门臂结束** 6 DRT/RCX、18 STA，第六次合格且 SEC 13648/0，面积减 7.5072，含筛选完成时间 781.567324 RAW s。六次与 720 s 窗均未达 0.01% 目标，窗口内完成五次且正式回收 0。单门汇总 SHA-256 `632768f84398122fe27430c7a646652e7f11b8d227aa25168695b6dc99d6edc3`，候选 SEC `d6c0305bff52c84e2b99c3ab1cd644c8dc5d7f72e559d35ed68770f4229f818a`。固定臂随后串行。
- **Ibex 单门五拒因只读核对** 5 个被拒端点的未触达改线都包含原普通嵌入导引无编辑重布线中的 16 条网。第 2–4 次 SS hold WNS 相对原 CONTROL 的降低与原零编辑的 0.079936058 ps 精确相等，第 5 次较原零编辑再损失 0.100808251 ps。新扫描与时序收据和旧物理参照分别记录，未变更验收门。[Ibex 分析](tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_REPORT.md)
- **AES 单门第 2 次候选通过** `_10992_` 一次实际 DRT/RCX，无重试，原三角电气/时序、解锁态 DRC/天线合格，SEC 11089/0。面积回收 11.2608（0.009665%），三角 setup 和 hold WNS 与 CONTROL 一致。逻辑费 154.460269 RAW s，包含筛选的完成点 517.790573 s，低于 0.01% 面积目标。结果 SHA-256 `31c7baef4e0d963efeb1f105834dff27887c55d5dbdd8ec8b655e37d5903172e`，实际 SEC 收据 `688f7b56db02f9c5ffb52fb90d05e8b4c74b7b9675ec4b7bbcff34c4e1ee9890`。
- **AES 单门窗内完成** 720 RAW s 内 4 逻辑派发、3 逻辑完成、5 route 调用（含 1 次重试与 1 次窗末截停）、4 次解锁态 DRC、12 视图 STA、1 SEC。第 3 次候选 22.5216 因 SS 相对 hold 被拒，保留第 2 次 11.2608（0.009665%）。窗末约 0.135 s 进程清理成本不进入验收检查点。`single/summary.json` SHA-256 `8271d8cb82bc32fd57533efbb9e40c874c199fc61fc339fc108429efb1f75134`。
- **Ibex 固定组三次达目标** 第 3 次实际候选通过原三视图门且 SEC 13648/0，面积回收 22.5216（0.015574%），三角无新增负 setup 端点。物理和 SEC 收据 SHA-256 `139b3cb8dbabf2c4481b0b10a1e4bd7a38a3d1e9b4041b86dd0ffc8f51b2be89`、`6b4d2e7161b7296f96829ba7b5e2812bb08c86a85c677c8954bb56a8162d43ef`。六次仍执行，等待整臂带时钟检查点。
- **AES 固定前两次阶段结果** 正式排名 1–3 的新物理仅 SS 相对 hold 拒收，全块 DRC 0，含筛选 241.577723 RAW s 完成；排名 4–6 新路由的 4 个实际 DRC 标记自动触发释放 `net4840`、`net8407` 并再次从冻起点执行。报告 SHA-256 `a71a8c915a1c8780042d4cd4684768410a35822336187bd94f4fc1a04cc151c1`，该重试的端点与耗时待实际收据。
- **AES 固定批次首次达标** 排名 4–6 经当次 DRC 自动放行两网和重试，解锁态全块 DRC 0、三角联合门及新 SEC 11089/0，回收 33.7824（0.028996%）。含共同筛选首次达标 532.098942 RAW s，逻辑 #2 含两次实际物理和全部审计、证明为 290.518365 s。FF/TT/SS hold +0.000056/0/+0.610845 ps，SS 同名新增负 setup 端点，原包络认定通过。`fixed/02/result.json` SHA-256 `daeaaf9bf5e582cd945d675eb3880223349d4a7d7fce249b6a2eb54670a61d7b`、实际 SEC `25d13a9c1fffccd911d98f91f084d0dc5d5638ff0ce99dcbd2d8d8b672751b9f`。第三逻辑累计候选继续。
- **Ibex 固定完整对照** 6 DRT/RCX、18 STA、3 候选 SEC，固定第 3 次 22.5216，在 452.491595 RAW s（含筛选）首达。720 s 内四次、保留 43.792；六次保留 62.56。`screened/fixed/summary.json` SHA-256 `1046fb2d9acd89191327c1df5193cfff30ee5eae8e48085167a89c302e0c3bf8`，末臂随后串行。
- **AES 固定硬窗截至** 逻辑派发 3、完成 2，route 调用 5 次（2 重试，最后 1 次截停），独立 DRC 4、STA 12、候选 SEC 1。第 3 次六门初始解锁 DRC 有 10 个标记，自动扩大到 `_01220_`、`net4840`、`net8222`、`net8407`，重试在窗末未完成。窗内最优保留第 2 次 33.7824，532.098942 RAW s 首达。`fixed/summary.json` SHA-256 `da630e952945b603686da238a98d84f853896078fd058f4d14c69ac1a3fd242d`。同驱动 FAECO 已启动。
- **AES 共同截停候选的条件性补跑** 仅当固定和 FAECO 都在硬窗截停同一第 3 次候选的自动重试，且完整动作及允许邻网逐项相同时执行。独立 `aes_protected_online_censored_retry_v1` 从同一原冻起点完成一次同动作、同邻网的真实重试；CPU 0–5 四线程，450 s 外限；重做 DRT/RCX、三角 STA、解锁态 DRC，通过正式门才另做 SEC。此为窗外机制诊断，不作为任何方法的正式时间、面积或达标证据。任一动作、邻网或停止条件不一致则停止补跑计划。
- **AES FAECO 第 2 次首次达标** 自动仅放行 `net4840`、`net8407`，实际合格的 33.7824、SEC 11089/0。529.886975 RAW s（含筛选）首达，固定实测 532.098942 s。两臂前两个候选的实际 ODB/DEF/V/去日期 SPEF/DRC 与每角度量逐项完全相同，第 3 次实际派发动作也相同。`faeco/02/result.json` SHA-256 `3e71f67d3e3550f807cfb6d895ab23b3e0a2c31fffb0c774d64ca830470de5af`、实际 SEC 收据 `9899ade28d9decf68fe90bf07c5401c0524ef4cf0af9c1bcd3a97604172ea07d`。
- **Ibex FAECO 第 3 次达标** 原联合门与 SEC 13648/0，实测面积 22.5216，与固定臂的原达标端点 ODB/DEF/V/三角读数逐项一样。三视图无新增负 setup 端点。原物理 SHA-256 `ffafbdadb8acdaaf454ead98f3e8cd5e3e4a92050e9679bf7d43142e85dc3d20`，SEC SHA-256 `1682d4ddbe7332d0a86e73e98dea69acdc52b689699c80496b376258da1593a6`。前两次 SS 相对 hold 拒收，后续三次继续。
- **AES 共用保护三臂正式结束** 单门／固定／FAECO 硬窗派发 4／3／3、完成 3／2／2，窗口内正式面积回收 11.2608／33.7824／33.7824。合计 15 次 route 启动（12 次完成 DRT/RCX）、12 次解锁态 DRC、36 次 STA、3 次候选 SEC。固定 A 与 FAECO 实际相同前三个动作组，第三次同样在复跑时截止。`aes_protected_online_matched_v1/results.json` SHA-256 `0e5887637b4b29c9bf8fe66cf0d8f2b345185ab98f79477191745238264db33e`。
- **AES 第 3 次共同截停重试诊断启动** 两种方法的第三次完整动作与真实允许邻网完全相同（`_01220_`、`net4840`、`net8222`、`net8407`），均硬窗截停，满足预登记。`aes_protected_online_censored_retry_v1` 10:20:16（UTC+8）开始，PID 13414/13416/13423，CPU 0–5、四线程、450 s 外限，配置 SHA-256 `a0e00d0ddf748646ca7bcd887b0769ec921772aa3b9bbb38e6c59c4f52fe1e8a`。重新完整执行这一次同路径重试，结果和成本独立登记。
- **AES 正式三臂独立核验** `aes_protected_online_matched_v1/independent_verification.json` SHA-256 `2d27b218fe218803964ab3bcde800217b05aac23753115631b29aea389d51b7a`。重算真实提交检查点和端点验收，两个达标臂的接受 ODB/DEF/V、DRC、去日期 SPEF、所有视图完全一致，首达来自同一批次和自动放行动作。第三重试分别在 40.545 s 与 56.615 s 的窗尾余量处截停。[AES 正式报告](tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)
- **AES 窗外共同六门重试结束** 同动作和四个真实 marker 邻网独立完成 1 DRT/RCX、3 STA、1 解锁态 DRC（0），物理面积候选减 67.5648（0.057992%）。FF/TT/SS 相对 hold −0.049849／−0.077660／+0.442979 ps，原相对 hold 拒收且候选 SEC 为 0。TT/SS 各有 1 个新增负 setup 端点。物理及诊断汇总 SHA-256 分别为 `7bd01fe05b63425be40f034319470d132385d4d17486cbfadc6afe329b528943`、`4b65dfcd2857904d2a2253e6d777110af0df367ff10dd23653bccc37177fd7fb`。诊断结果单列，正式三方法的面积和时间采用原硬窗收据。
- **AES 捕获分支读回与原件归档** 窗外重试完整计 137.305 RAW s；捕获分支 `clknet_3_1__leaf_clk` 虽几何固定，提取总电容较三门端点增 +0.0000792 pF（地电容 +0.000074512 pF）。正式与预检原件归档 `scratch/tcad_ibex_20261123/aes_protected_online_matched_20261124.tar.gz`，421,679,422 字节、597 成员、542 普通文件与原件逐项 SHA-256 校验，包哈希 `b58edd7afd696193512d3920b752b2560950cfc7550e3dc3a1ff33ea41a50bd6`。窗外诊断另包 `scratch/tcad_ibex_20261123/aes_protected_online_censored_retry_20261124.tar.gz`，28,354,866 字节、49 成员、45 普通文件逐项核验，包哈希 `70e35973a20e27010801d55a4b8af771634317c2b5f8bae0fd737bc8a7bb85b6`。[AES 正式报告](tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)
- **Ibex 三臂完整结果** 18 DRT/RCX、54 STA、7 SEC、0 缓存，`results.json` SHA-256 `ddca77ab6400d3be743b1fabb05b2c419d18cee26a295b47f5bafdf8efbc6fb5`。含筛选 720 RAW s 内，单门／固定／FAECO 完成 5／4／4 次，回收 0／43.792／43.792。六次实际回收 7.5072／62.56／62.56。固定、FAECO 同在第三次 22.5216 达标，452.491595／454.057586 RAW s，首达点全部三角无新增负 setup 且 SEC 13648/0。固定与 FAECO 全六次物理动作、各项指标、改线产物与接受/拒收结果相同，各自真实墙钟观察单列。[Ibex 正式报告](tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_REPORT.md)
- **Ibex 独立核验与正式对照收尾** 独立 MatrixAudit rc 0。720 s 内固定与 FAECO 保留的同一端点三视图无新增负 setup。`scratch/tcad_ibex_20261123/ibex_screened_single_pa_three_way_20261124.tar.gz`，354,402,976 字节、458 成员、420 普通文件和原件 SHA-256 逐项一致，包哈希 `092219f99535c3fa59795b8c4f2cc7a28fdb1562ee0d735c4f507268441001de`。Ibex 和 AES 两设计正式共完成 30 DRT/RCX、90 视图 STA、10 候选 SEC，AES 截停物理调用及预检/窗外诊断另计。最终针对性回归 114 项通过、17.60 s。[Ibex 核验](tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_VERIFIED.json) · [AES 正式报告](tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)

### 2026-11-24 TCAD-SKY130HD-DISPATCH-OPTIMIZATION-AND-AES-RANK49-V1

- **同轨迹归因预登记** 从 `da329ccf`，先只读复核两种批方法的完整派发、早段拒因、后来接收的累计状态和终止条件，同时分开记录哪些候选特征在派发前就已知、哪些来自实际物理评估。依据事前可用信息再选改法，冻结后用新物理对照证伪。Ibex 保持原合格 CONTROL、原 I/O/SDC、原筛选池、单次 pin access、同已测四路筛选成本；全方法用原三视图 setup/hold、电气、DRC 和非空 SEC 门，720 RAW s、0.01% 目标与共同调用配额。单列记录同目标真实首达、窗内最好面积与工具成本。已有设计用于调度开发与机制验证，其他设计另验证。[Ibex 原矩阵](tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_REPORT.md) · [AES 原矩阵](tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)
- **AES 排名 4–9 六门修复预登记** 保持 v2b 原冻结起点、原 I/O/SDC、原 setup、绝对／相对 hold、电气、恢复 ROUTED 时的全块 DRC、天线和 SEC 门。先以已有实际六门窗外端点与三门达标端点为诊断，读回 FF/TT 发射和捕获 RC 的变化，再择有限物理修复。阶段成本、动作及自动／定向开放邻线另绑。本项独立于任何正式搜索的 720 s 对照和历史手选六门端点。[原窗外诊断](tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)
- **AES 交叉路径与后续边界** 绑定窗外 `aes_protected_online_censored_retry_v1/retry/receipt.json` SHA-256 `7bd01fe05b63425be40f034319470d132385d4d17486cbfadc6afe329b528943`，六门为 `_11178_`、`_11724_`、`_12777_`、`_12929_`、`_13098_`、`_13122_`，对照取本次正式 `fixed/02` 重试。各角交叉四组共 12 次只读 STA，CPU 0–5 单线程、每次 90 s、整体 180 s，原件 `aes_rank4_9_residual_cross_v1`。若归因指向可尝试的发射补偿，拟用 `_21033_` 置换排名 7–9 的一门且保留排名 4–6。候选最多两到三次物理尝试，允许原报告涉及的保留动作邻线和可追踪的 `net8148`，必要时最多一次当次 DRC 报告定向复跑。每例 CPU 0–5 四线程，DRT/RCX 240 s、STA 180 s/角、SEC 210 s；合格按原 36 ps WNS 与原 TNS、hold、DRC、电气、天线及 SEC 门。此前同面积手选合格的六门组成不同，需单独实测该候选。
- **只读轨迹与前置特征查实** Ibex 固定和 FAECO 相同累积序列 `(1–3)`、`(4–6)`、`(7–9)`、`(7–12)`、`(7–15)`、`(7–16)`。FAECO 在前两次 SS 相对 hold 拒收时延后拆分；第六槽只试 16，17、18 仍新，预算内未消耗延后队列。AES 第 1 批 SS hold 延后，第 2 批通过，累计第 3 批硬窗未完成。原固定 SPEF 筛选的 18 个候选均扇出 1，TT hold、电气与新增负 setup 无区分度。冻结 DEF/SPEF 下各动作直接触及 3–6 网，涉及网的总电容 6.498–241.712 fF；排名 1 与 3 共享一网，存在可登记的前置代理线索，尚需实际门对照。
- **AES 首试 `_13098_→_21033_` 规格** 仅置换窗外候选一门，保留其余五门。失败端点的 `net7951`、`net8215` 改线距原捕获支路约 0.34 µm，到耦合邻网 `net8139` 约 1.70／1.36 µm，用作试探依据。保留开放 `_01220_`、`net4840`、`net8222`、`net8407`，新增 donor 原住邻网 `net8148`，预计 23 数据网放行、15,634 条保护。`aes_rank4_9_donor_replace_13098_v1`，CPU 0–5 四线程，730 s 外限，原三角验收及最多一次当次 DRC 指向非时钟邻网的重试。
- **新规则冻结在首次预览和物理运行之前** 首批按原序，任何一角 `hold_regression` 第一次实际导致拆分延后时，按 `面积节省 / (1 + 冻结 DEF/SPEF 的触达网总电容 / 全筛选池该总电容的中位数)` 降序重排未访问的候选，平局保持原排名，仅重排一次。原批宽、末槽单门、延后队列与各联合门保留。原物理结果不参与分数。新臂除同筛选收据外，计入一次实际特征准备耗时。Ibex 计划固定批次和新动态重排各从同原 CONTROL、原 I/O 和筛选池重新物理实跑六次，使用单次 PA、720 RAW s 和 0.01% 目标；配置、起跑顺序及审计另绑。GCD 如能执行，同口径作为未参与本轮规则选择的迁移检查。
- **AES 交叉完成与置换实际启动** 12 STA，固定合格三门 ODB 换成原失败六门 SPEF 可精确复现 FF/TT/SS 的 −0.049905／−0.077660／−0.167866 ps hold；固定合格 SPEF 换 ODB 三角都是 0。同名路径 FF/TT 发射提前、捕获延后，13 条路径网 RES 边匹配，注解覆盖一致。`aes_rank4_9_residual_cross_v1/results.json` SHA-256 `1c0eb2da40f203a324269678f5c0cd0ef293946f7527f3396a2bcefcd5c460a9`。`aes_rank4_9_donor_replace_13098_v1` 于 10:34:29（UTC+8）实际起跑，PID 436/438/445、CPU 0–5 四线程、730 s 外限，实际打开 18 条直接数据网+5 条邻网；配置 SHA-256 `ee919dbff902c7e838727296dbaae366c13c23bec1381cf6f4373aca1493a8ee`。[六门修复入口](tcad_ibex_20261123/probe_aes_rank6_repair.py)
- **AES 六门等面积替换验收通过** 1 DRT/RCX、3 STA、解锁态全块 DRC 0、天线 0、1 次非空 SEC 11089/0。实际改线恰为 23 条放行网，15,634 条保护网几何一致。一次完整验证用时 137.850971 RAW s，无重试，面积回收 67.5648（0.057992%）。FF/TT/SS hold 改善 +0.063172／+0.098699／+0.653255 ps。原 setup 成本包络过，TT/SS 各新增 2／1 个负 setup 端点。真实验收 SHA-256 `f9609181296bcf41b959a01efb9a2a93cc6c0a44bb9d156d28c8762879ef6d69`，候选 SEC `e5305b4d1a89ff53d060af7f3f0918f63cbe6d324dd7f8e9ffe902af3115b5ce`。实施时按已知物理归因选取一门，实际结果单列于前轮正式矩阵。[AES 物理修复报告](tcad_ibex_20261123/AES_RANK4_9_HOLD_REPAIR.md)
- **规则后首次只读预览与两设计实跑规格** 新规则先冻结，再从原 DEF/SPEF 读出两设计各 18 个特征，Ibex/GCD 池内触达总电容中位数 0.054086022／0.020697664 pF。如果原首批遇相对 hold 延后，预计下一组 Ibex 排名 6、10、11，GCD 4、5、6，后续未访排序变化以 trace 为准。实跑 `run_incident_cap_pair.sh {ibex|gcd}`，按设计 Ibex→GCD 串行，各自固定→动态重排、每臂六次，再算 720 RAW s 前缀与 0.01% 目标。CPU 6–11 四线程，外限 4200／1200 s，单次 DRT/RCX、逐角 STA、SEC 1500／180／210 s，统一单次 PA。固定、优化臂共费已测四路筛选 Ibex 77.493270／GCD 39.206443 RAW s，优化臂额外计真实特征准备，原三角联合门全守。实跑前针对性 15 项检查通过。[实跑入口](tcad_ibex_20261123/run_incident_cap_pair.sh)
- **Ibex 实际启动** `ibex_incident_cap_pair_20261124_v1` 于 10:38:45（UTC+8）开始，外层 PID 336、驱动 PID 440，CPU 6–11 四线程，显式 `--screened-risk-pair` 与 `--single-pin-access`。输入配置 SHA-256 `4ecede25300b5e6a1fb115b7b279ed83932a4ed9177c381d2af47160a4c79775`，两臂共用四路筛选收据 `991d99171be9be75883f6f042e97dabbcf227c05dffa289d1d0b09c5145340b7`。实际运行顺序固定→动态重排，测原前提资格后的实际物理与时序。
- **AES 等面积修复配对路径与原件收束** 两端点各做 3 次高精度 STA，复核原最差路径不变。修复较原失败六门在 FF／TT 延后发射 0.080168／0.126958 ps，提前捕获 0.032008／0.048339 ps，hold 改善 0.113021／0.176359 ps。SS arrival 一致且捕获提前 0.210046 ps，hold 改善 0.210276 ps。捕获分支原 +0.0000792 pF 电容增量消失，新增发射分支 +0.0001006 pF；13 条路径网电阻边一致。配对 SHA-256 `b2e1639f1bdbd112e0a576792922fadfe133aa5bfea05e6a84a8be6ef45ae8cf`。归档 `scratch/tcad_ibex_20261123/aes_rank4_9_hold_repair_20261124.tar.gz`，29,105,129 字节、104 成员、97 个普通文件逐项 SHA-256 核验，包摘要 `775f09b276b7f2c74d1ad1fc9cd06946453113a67cd91292b17127b34449e8a5`。[AES 归因与修复](tcad_ibex_20261123/AES_RANK4_9_HOLD_REPAIR.md)
- **预登记 AES 迁移对照** `aes_incident_priority_preflight_v1` 新跑保护零动作及原首组三门验资格，再在 `aes_incident_priority_matched_v1` 按固定→新 FAECO 串行，原 v2b 冻结 DEF/ODB/SPEF、原有序池、原 I/O/三角 setup/hold、电气及 SEC 门，6 逻辑请求、720 RAW s 硬执行窗、0.01% 目标。两臂共同计原实测筛选 113.36303244 RAW s，新臂另外计一次实测特征准备，FAECO 在原首批后首次真实相对拒因延后时才按共用触达电容公式重排。两臂使用同一保护与基于当次真实 DRC marker 放行非时钟邻网的规则，最多重试一次，另验解锁态全块 DRC、天线。CPU 0–5 四线程，物理进程按墙钟余量限制。预检、上一候选修复、历史点均不缓存到两臂，诊断原件与正式比较分别保存。
- **AES 共同资格实际启动** `aes_incident_priority_preflight_v1` 于 10:42:35（UTC+8）运行，驱动 PID 1489、首次 OpenROAD PID 1496（四线程），配置 SHA-256 `ff168edc90daefdbba5f004a43149251c3e668a219f623fced205ffd369103f0`。等待同原起点的保护零动作与首批收据，完成资格后再启正式臂。
- **AES 正式前特征预览** 冻结公式计算的 18 个有效候选中位数为 0.03896634 pF，若首批实际相对 hold 延后，新臂下一批应选原排名 15、9、10，固定应选原 4–6。该预览仅来自冻结输入与规则，真实与否由新派发核验，物理验收另证。
- **Ibex 固定首个实测合格组** 固定第 1、2 次均仅 SS 相对 hold 拒收；第 3 次真实回收 22.5216 µm²，约为 0.015574%，SEC 13648/0。`screened/fixed/03_physical/receipt.json` SHA-256 `b3448c9c682eb5f15b3a95e4b65ae70180f08bec8c6976ed041e170d1037b758`，候选 SEC `765caca7906c95e27331799373dfcac26fd8bde91b43857d06a99ea543996231`。首达和 720 s 前缀以完整收据为准。
- **AES 迁移实际起跑** 新零动作资格通过真实 SEC 11089/0，原首组仅 SS 相对 hold 拒收，预检汇总 SHA-256 `fb4bd00ec1535ff85ab6267430984f9a8f6cb474f07d6f847c44a6c377eb265e`，零动作 SEC `545b645e4a1248975b02252062b343e2feb731c5af8295d8e0fe7142e975c258`。`aes_incident_priority_matched_v1` 于 10:47:17（UTC+8）由 PID 3511 驱动，CPU 0–5 上四线程，固定先派发。配置 SHA-256 `3b58df6cb5754c00528ad6b8dfac6da0810dc4571d73dabfef83d67bc6a8bb4d`，迁移资格绑定 `8c0ce0a97bcfedc6246968e927f1ea563b434c2fb88de52eeeabf3ec3a78c774`。[AES 启动入口](tcad_ibex_20261123/run_aes_incident_priority_matched.py)
- **AES 迁移固定首达** 排名 4–6 由实际 marker 只放行 `net4840` 和 `net8407`，重试后各门、解锁态全块 DRC 0 及 SEC 11089/0。回收 33.7824 µm²（0.028996%），含筛选首达 561.985993 RAW s。`fixed/02/result.json` SHA-256 `4326769337aa10bf5b71c84e3aceb1c0caddc38f7c53b87324273b619267159b`，合格物理收据 `c344785e0c020546bddd0e7fc6c4fa15cc2684669840c9228b0b2ca6f6d84f14`。
- **Ibex 固定完整／优化启动** 固定实跑 6 DRT/RCX、18 STA、3 SEC，第 3 次 22.5216 µm² 达标，含筛选 435.253506 RAW s；720 s 内完成 4 次且回收 43.792 µm²，六次最佳 62.56 µm²，计费全六次 1009.914459 RAW s。`screened/fixed/summary.json` SHA-256 `1911818f009394bd97741d2c8597d844e40959f1d7764e9219d505a8d91ef910`。仅新臂计实际特征准备 0.743538314 RAW s，从同一排名 1–3 开始真实物理。[调度报告](tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)
- **AES 固定硬窗收束／优化启动** 固定实派 4、窗内回调 3，前两次完成全部物理判定。第 3 次排名 4–9 重试余量约 20.939 s，超时回调返回；第 4 次约 0.218 s 后截断。DRT 6 次、解锁态全块 DRC 4、STA 12、候选 SEC 1。固定窗内保留第二次合格 33.7824 µm²，首达 561.985993 RAW s，`fixed/summary.json` SHA-256 `d47f277167d370dec423074ceac4baecd2597a72a0c9137875c8465c7725c867`。优化臂从首组三门开始，冻结特征准备 0.756592 s 已计费，优先表 SHA-256 `770528a6985bdd9c7d16f3803fdf893a699b462fe50be532b7093bee52bb1041`。
- **Ibex 与 AES 新臂实际重排** 首组各仅 SS 相对 hold 拒收。Ibex 次组按事前规则选原排名 6、10、11，回收 22.5216 µm²、SEC 13648/0，物理 SHA-256 `d99cebe47733e7fc06e78ad55b80c502c7a1ea223271555877dad962029d186c`、候选 SEC `71a0630bd5e5928564d43dde0dd805482e4edeae0791fe1fb982615e1f70abd6`。AES 次组如前置预测选同一池的 15、9、10，实际物理仍在执行。各臂完整首达和 720 s 前缀以后验收据为准。
- **AES 次组自动重试后仍拒收** 初始有 6 个 DRC marker，自动仅放行 `_03615_`、`net8222`，重试独立 DRC 0、天线 0。物理面积减量 33.7824 µm²，FF/TT/SS 相对 hold WNS −0.008049／−0.012490／+0.073719 ps、绝对三角均为正且 hold TNS 0。原相对门拒 FF/TT，无正式 SEC。`faeco/02/result.json` SHA-256 `36e89d8802b5c52e4c80ca54cdef96be1af3efef012a9e4ca0df97d3199fad74`、`retry/receipt.json` `5c7cf0178d555cca56baf6ce278619bd58c87a0de901c6278d11499b07f5d95e`。第 3 次仍自首次重排后的未访问队列选排名 6、13、16。
- **AES 新次组另行只读归因预登记** 正式两臂结束后，按原始物理与约束字段绑定新被拒 `/02` 重试和冻结 CONTROL，目录 `aes_incident_priority_hold_cross_v1`，三角各交叉 ODB/SPEF 四次，对照原 endpoint 后读 FF/TT 发射、捕获时钟及相关网电容；CPU 0–5 单线程，每个 STA 90 s、整批约 160 s，正式窗的已验收状态与耗时保留。
- **AES 优化臂窗尾部分记录** 第 3 次重试独立恢复 ROUTED DRC 的有效窗口耗尽，`TrialFailure rc=None` 传至驱动并以 1 退出，未生成优化臂正式终态。原件保留，确认两个完整候选拒收，第三未完成验收。完整配对待解决超时终态处理，本轮已有固定与优化候选的实际物理观测单列。
- **AES v2 拟重新配对** 限定修复硬窗裁剪引发的 `TrialFailure rc=None` 提前少量返回，真实裁剪保留候选截停和原完整时间口径，实际工具错误保留异常。完成回归后在全新目录重新实跑固定→FAECO，保持原配置和面积、时间、全部验收门，使用 fresh 候选且不拼接 v1。v1 不覆写，v2 与归因输出单列。
- **AES v2 实际启动与 v1 根因实查** v1 第 3 次重试独立 DRC 的 120 s 原限时受剩余窗裁剪到 2.626940724 s，进程例外比截止早 0.005096355 s，解释何以未运输成窗内候选截停。物理 33.7824 µm² 和三角 hold 改善已有记录，原联合门仍无独立解锁态 DRC 和 SEC。重现测试 v1 保留失败、v2 三例通过。`aes_incident_priority_matched_v2` 于 11:09:43（UTC+8）PID 10344 串行固定→优化实跑，CPU 0–5 四线程。配置 SHA-256 `64c4c82d9781cbbd7ca13e8ad4c482f0addcf357ba153062d48b5f16eacb9435`，驱动 `fd937db6d18a074b769ca30e8e4afc7dc4229dcec0aff09489829013b4d7b2b0`。[单独 v2 驱动](tcad_ibex_20261123/run_aes_incident_priority_matched_v2.py)
- **Ibex 完整配对实测** 固定与优化各有 6 DRT/RCX、18 STA、候选 SEC 3／4，720 RAW s 内同为 4 次及 43.792 µm²（0.030282%）。同目标 22.5216 µm² 首达第 3→2 次，计费时间 435.253506→368.344845 RAW s（−66.908661 s，−15.37%），新臂已计特征准备 0.743538 s。新臂首次达标三角无新增负 setup。相同窗内面积端点的新 SS 负 setup 固定／优化 0／1，优化较固定 SS hold WNS +3.330225 ps、SS setup TNS 差 78.129233 ns。六次口径 62.56／68.816 µm²，对应 1009.914459／951.122921 RAW s。`results.json` SHA-256 `c4138fc7ee175efbc64dc1954f6249be07a8c2ab6df744108c60f4f67830080a`，优化臂 `summary.json` `fa5d020ea3036fc03404b98f1fa27ac368641005ddd30ca1ef208987a68e7282`。[Ibex 配对报告](tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)
- **GCD 转移实际启动与固定完成** `gcd_incident_cap_pair_20261124_v1` 于 11:10:39（UTC+8）启动，PID 11176/11178，CPU 6–11 四线程，固定→优化。配置 SHA-256 `45d112a0e8444cf68ff1c72f5f03ff245743d198c71a7f97e2b6b510cf8f3113`；共同筛选 `4dd1fd0c2c20d778efbd3515a84cd9f7ed47d7e7baaa0ba7d96216cf3880d62e`。固定已完成 6 DRT/RCX、18 STA、1 SEC，窗内 11.2608 µm²，首达 94.278734 RAW s，全六次 106.931513 s；固定汇总 `ecfea4ff3edb84afee96ecec158c36167cee1d3cd3c0ab74c4073577e2c874ef`。
- **AES v1 部分实跑独立核对** 固定回调 3／派发 4、窗内 33.7824 µm²；优化回调 2／派发 3，两个完整请求均拒，第三 `clipped_child_timeout_driver_exit`。`independent_reconciliation.json` SHA-256 `c00549d8056293c304e590ab4f07a05aa9997653189c81b2191227bb1f3f8225`。第 2 次放行重试额外付 130.884 工具秒，解决 DRC 但 FF/TT hold 仍拒；第 3 次初始独立 DRC 有 5 个标记，重试已用 101.995 工具秒而未完成独立全块 DRC。保留为部分真实观测。
- **AES v3 开发臂条件预登记** 先完成 v2。与可归属非时钟邻网的独立 DRC 标记同时出现时，若初评 DRT/RCX/STA 已完成且至少一角原相对 hold 失败，则暂缓申请拆分、先尝试未访池并省下该自动重试。若初次三角相对 hold 合格，仍按原 marker 严格重试。其它原物理与时序门、原起点和池、6 请求、720 RAW s、0.01% 和前处理费用保持。另做一个新 FAECO 开发臂与 v2 同资格数据比较；非法初评几何的相对 hold 可能在真实重试中转正，需要报告漏过机会。本条是观察本设计后提出的机制诊断。
- **GCD 转移完整与独立验收** 12 DRT/RCX、36 STA、3 候选 SEC、9 个不同元组、零缓存。两臂 720 s 内完成全部六次，均第 5 次以 11.2608 µm² 达标，首达 94.278734／94.450929 RAW s，优化计真实特征准备 0.014574 s。第 6 次不同的追加动作令新臂回收 15.0144 µm²（0.312989%），固定留在 11.2608 µm²（0.234742%），新多 3.7536 µm²。各最优端 SEC 262/0，优化新增 TT 负 setup 1，固定三角为 0。原结果 SHA-256 `8bafa83cfdc57d9eccc52ecbf6050a3b5425fbb9fd21033af2fbd33d022f37fa`，独立核验摘要 `cff49aab5e53203fc2f144e44f899f6ed777465c33d0816f6b194de39ae283ac`。[GCD 独立核验](tcad_ibex_20261123/GCD_INCIDENT_CAP_PAIR_VERIFIED.json)
- **Ibex/GCD 合并审计归档** 审核两次退出 0，Ibex 核验 SHA-256 `fcf8c1706563c4a0cc7a3ae136370982a3734c5b35002e29073ba45b4703171f`，GCD `cff49aab5e53203fc2f144e44f899f6ed777465c33d0816f6b194de39ae283ac`；24 个候选的 route 日志逐一确认单次 PA 完成。`scratch/tcad_ibex_20261123/incident_cap_pair_ibex_gcd_20261124.tar.gz` 261,811,921 字节、648 成员、590 个普通文件逐项摘要一致，包 SHA-256 `98089d930c09473affd5afa15bae6c731c02afe72c8821ae6e1505d73a7d2d03`。[Ibex 独立核验](tcad_ibex_20261123/IBEX_INCIDENT_CAP_PAIR_VERIFIED.json) · [GCD 独立核验](tcad_ibex_20261123/GCD_INCIDENT_CAP_PAIR_VERIFIED.json)
- **AES v2 固定完成** 派发 4、完成 3，6 DRT、5 独立全块 DRC、15 STA、1 SEC。第 2 次获 33.7824 µm² 并首达 447.228744 RAW s，合格物理 SHA-256 `4900e80b8e8f35cc8f1e71e58ef4ba2ca8c39b953f24968450dbad1486529f95`；v1 对应固定首达 561.985993 s。第 3 次同原排名 4–9 的六门在 649.578134 RAW s 完成物理、独立全块 DRC 及三角 STA，FF/TT 仍纯相对 hold 拒收（SS 改善），未做候选 SEC。物理 SHA-256 `7691239f8a91821cfac5cc562fda88c2d09d58bdd11ebec8b0a483c70b6c2059`，固定汇总 `789b835a9b65a6037f8990e5e09140a386026dd5177a5e7b87404da9d4dc8a29`。
- **AES v2 优化实际达标** 第 2 次仍 FF/TT hold 拒收；第 3 次原排名 6、13、16 经真实重试、解锁态全块 DRC 0、天线 0 与 SEC 11089/0，回收 33.7824 µm²（0.028996%），含筛选和实测特征首达 622.069313 RAW s，较固定同面积晚 174.840569 s。三角 hold +0.048961／+0.076827／+0.884626 ps、SS 新负 setup 1。第 3 次结果 SHA-256 `13ddc2195f2f56667ad7646bc618dd281ce6fa20274245aaf2162e11d2adc520`，物理 `70b5bf2ba76c2752a8dfb32c129634d98d762c27c2a4b0e9f969db1b9982da7e`，SEC `a893e29686a5fca4c2d8ef3005f8a83e2471e3bb8b8c2da770dfda58a6d73755`。同 v1 截停候选的实体输出逐字吻合，该时点仅 v2 有完整验证账。
- **AES v2 正常完成并独立核验** 固定和优化各派发 4 次、完成 3 次，物理 DRT 各启动 6 次、独立 DRC 5／6、三角 STA 15／18、候选 SEC 1／1。优化第 4 次独立 DRC 受硬窗截停，驱动实际返回 0 并成功保留终态。总结果 SHA-256 `07e36a96a4adf6a8f7444c2ceaca8272ce939135ada4a1eab5dea294e7212d06`，独立核验 `5d5b6b407f37ec9818a6411bc43205dbb3cc54d2e2123fb635560eda7788f230`。取消 v1 相同实体输出的重复 DRC/SEC 后验跑，v1 原终态仍独立；保留 v3 后对新的 `/02` 被拒候选做只读归因。[AES 配对报告](tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)
- **AES v3 独立开发实启** `aes_retry_triage_v3` 于 11:30:15（UTC+8）PID 15650，CPU 0–5 四线程，初始按原排名 1–3，原资格、池、720 RAW s 硬窗与验收门沿用。配置 SHA-256 `96b1ca104472719ff04ebae388a860653cdcb68ee393035965044bb05a37032d`。按 v1/v2 已观察的重试费用提出本设计开发臂，另运行、另统计，后验只读归因在本臂结束后做。[v3 驱动](tcad_ibex_20261123/run_aes_retry_triage.py)
- **AES v3 确认跳过实际物理重试** 第 2 次初评发现独立 DRC 6 个标记，所指 `_03615_`、`net8222` 保留记录，且三角初步相对 hold 均失败。实际 `deferred_retry.json` SHA-256 `9ebc770117c301764507fe4b21311c8f0278c97b8f70993f0a96f1b14a3b873e`，无该批第二趟 DRT。第 3 次原排名 6、13、16 与 v2 一致，在两臂各自活时窗约 295.529／197.851 s 处派发。最终时间和端点以后续完整原件为准。
- **AES v3 复现共同达标端点** 第 3 次经真实重试、独立 DRC 0、天线 0、SEC 11089/0，在 524.180922 RAW s 首达 33.7824 µm²，对 v2 优化同端点实测提前 97.888391 s、对 v2 固定同面积慢 76.952178 s。与 v2 优化第 3 次 routed ODB/DEF/V 和三角指标逐项一致。第三次结果 SHA-256 `cef11b4209082abb7e1344ff894f4c6ae82db76004a92f4b240fc6e46538fade`，物理 `053619c4c11717da789ff60cf1e4e71222e6d40c409a2d50584299b4fd468e80`。累计第 4 次已实派，最终硬窗及终态另验。
- **AES v3 另一个六门重试未试** 第 4 次累计六门排名 6、7、11、13、14、16，独立 DRC 8，初始 SS 相对 hold 下降 0.082157 ps，规则记录四条数据邻网后延后，`deferred_retry.json` SHA-256 `0728a2c36c2c43c2ad82e97101cb533e5c2251e92e6827ab42dcb1f005a97ea0`。未实跑真实重试，资格未知。第 5 次尝试把原排名 4、6、12、13、16、17 累计提交至硬窗，剩余约 42 s，状态另验。
- **AES v3 开发臂完整收束** 实际 5 派发／4 完成，第 5 次被硬窗截停；6 DRT 启动、6 独立 DRC 启动、18 STA、1 SEC。窗内仍以第 3 次保留 33.7824 µm²，在 524.180922 RAW s 首达。与 v2 优化同 DRT 启动数，新请求替换了预算内部分物理重试。结果 SHA-256 `8f1dd2d18748b899024f31e688d2b65c310ec6e6bc4c360ca60f3a1900429b4d`、独立核验 `61aa126039665acf0f6743daab778e2ca4af1ed16a29774260b5f4e3c416268c`。
- **AES v3 第 5 次已完成物理的窗外补审预登记** 原产物有 DRT/RCX 与三角完整读数，初步面积 65.0624 µm²，原三角门和初报 DRC 0，硬窗在独立全块 DRC 截停。按同物理 SHA 只补独立 DRC、天线、SEC，不重布线，另记候选观察及成本；任何新增验收都不回填 v3 时间或面积。
- **AES 被拒次组 12 次交叉实测** 只换 SPEF 精确重现 −0.008049117／−0.012490009／+0.073718809 ps 的 FF/TT/SS hold 变化，单换 ODB 三角 0。13 条路径网电阻不变，FF/TT 数据到达提前大于要求时间提前，SS 数据到达延后且要求时间提前。`aes_incident_priority_hold_cross_v1/results.json` SHA-256 `1c3cd8eb020468c0eaf4bfe0325d5524c90674427cc755d7311d0484e0353964`。
- **AES 窗外补审实际启动** `aes_retry_triage_v3_cutoff_completion_v1`，CPU 6–11 上 195 s 外限，仅独立全块 DRC／天线／SEC。绑定物理收据 SHA-256 `faea94fdff54db417b2739e650e5e705c5691ab793483c2b5075ff9ddcc8efd8`、驱动 `9e823dfed32d68c25c8f482472de4c0a705783499a18f586bbb0898d8720df10`。核心回归 115 项与 WSL 3.12 AES 针对性 9 项均通过。
- **AES v3 六门窗外补审拒收** 保持实际原产物并恢复 ROUTED 状态，规范 DEF 逐字一致，独立全块 DRC 发现 8 个标记（6 处 met1 short、2 处 spacing）。65.0624 µm² 候选拒收，按预登记无物理修复和 SEC。独立审计 SHA-256 `6b59a26347033d617b9e1159cc85ec559bb04bc35b1ac2e416559a05bf626018`，marker 报告 `3c9b97ff6886520c3c1e2959d0550990354583773584ea48c1a6461ed51533cd`。v3 正式硬窗仍保留第 3 次的 33.7824 µm²。
- **AES 触达电容与重试实验归档** `scratch/tcad_ibex_20261123/aes_incident_priority_study_20261124.tar.gz` 覆盖共用预检、v1 原异常及核对、v2 匹配对照、v3 开发臂、第二次交叉 STA 和第五次窗外独立 DRC，共 6 根目录、822,891,438 字节、1,219 个成员，1,110 个普通文件逐项核对。Windows 与 WSL 包 SHA-256 `e7a2b0629aeb62a425bb518086302e62cc2969ab25d6078142e78578b025dbe6`。Ibex/GCD 配对和 AES 排名 4–9 定向替换另包如本节前述。实验记录、现行口径及未决范围已同步；115 核心与 9 项 AES WSL 专项通过。[AES 实验报告](tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

### 2026-11-24 TCAD-SKY130HD-AES-RETRY-DRC-AND-MATCHED-V1

- **预登记** 从 `3f038afd` 独立核算 v2 固定与 v3 优化的剩余首达时间，再对 v3 第 5 次独立检查报告的 8 处违规按实际标记定位信号邻网，定向修正同一个六门。新同预算对照保持同一原冻结输入、I/O 和三角联合门、720 RAW s/0.01%，费用按当次完整物理操作结算。定向修复与同预算对照分开；具体候选、驱动与配置另绑。[前轮 AES 配对报告](tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)
- **独立原收据分解** 由 v2 固定和 v3 优化首次达标回调分别锁定第 2／3 批。总工具 322.553768／395.915501 RAW s，新臂准备 0.579150 s，其它搜索开销 11.311944／14.323238 s，均计 113.363032 s 原筛选。总差 +76.952178 s，分量 DRT/RCX +51.920696、三角 STA +8.968882、独立全块 DRC +13.016016、SEC −0.543861、特征 +0.579150、其余 +3.011294 s。v3 实际多做中间一个完整初始物理请求；v2 优化所做而 v3 避免的该组重试用 95.494303 工具 s。v2 固定和 v3 优化 `subprocesses.json` SHA-256 分别为 `432f65209cd68a6eb4a5d354539936afab30a97c80f3266cce2cb1e782dc846a`、`d6b79cc81d88dca359fbc4313c0b0feb721ea24ff72e957aa7485477a5b72948`。
- **定向可行性及条件新鲜配对** 重跑 v3 第 5 次的原排名 4、6、12、13、16、17，从冻结 CONTROL 首试仅额外放开由旧独立 DRC 报告绑定重算的 `_08784_`、`net4840`、`net8148`、`net8407`；CPU 0–5 四线程、路由限时 240 s，原三角、全块独立 DRC、天线、电气与 SEC。若此件实际合格，再独立串行固定和定向试验，各先真实派相同排名 1–3、4–6，定向第 3 次从同冻原重跑完整指定六门（可撤回上批排名 5），首次放网从已记录的 AES 标记学习，候选全验证费用重新纳入，不复用探针端点。各臂 6 个请求、硬窗 720 RAW s 含共同 113.363032440 s 筛选、0.01% 比较目标与原门，另外披露已知候选／邻网使用和最终面积。
- **首试实际启动与第二批的前置物理优化** `aes_v3_six_marker_feasibility_v1` 16:11:18（UTC+8）启动（驱动 PID 413，首次 DRT PID 426），配置 SHA-256 `f1e3db348e6be2c3dd9132a344e985e735df476d3db3da14fdc3ff29d151f0b2`，计划 `8b2bf9753c2ef0076a62ffcb4330c9aace2c2af33cc3905a897d62c56bc83874`。实际释放四额外实体邻网和 20 条直接网，DRT 实际硬限 234.943943 s。在首次可行性结论前冻结同预算定向臂第 2 次已知标记直接放行 `net4840` 与 `net8407`，保持同原排名 4–6，目的是省一次已知无效初评。其历史 marker hash 核对、开销与全部原门的当次独立验收计入定向臂。若出现新的真正 DRC 允许原规则最多一次追加邻网重试，原时序失败不另放宽。第 3 次照计划，结果属 AES 开发验证。
- **可行性实际通过** 首次物理即回收 65.0624 µm²（0.055844%），121.387627 RAW s，1 DRT/RCX、3 STA、独立全块 DRC 0、天线 0、SEC 11089/0。改线恰为 24 条计划网，15,633 条保护网规范后几何未变。三角 hold WNS 改善 +0.059064／+0.092537／+0.937028 ps，hold TNS 全 0，TT／SS 各一个新增负 setup，原预算通过。物理 SHA-256 `0bd6116e5d01fb932ac9177d8dca8dc3d5a64ed1e7b2b97ceb208d224c5e2917`，结果 `d5c194c536a6749818958efe3c88c4603200ccd04d77eb18b079022237ab07f8`，SEC `a4757b9ef29e7674d6daea072b50ae0622699d614ad582bee3aa5fe5ccdcfa5e`。启用条件性配对，但独立可行性原件不计任何正式窗或做物理缓存。
- **实际配对启动与末次预登记收敛** 已通过首轮独立可行性后，两项带历史标记提示的定向请求均只发一次真实完整物理，失败时拒并保留前一合格点，固定沿原 marker 重试规则。实际 `aes_marker_repair_pair_20261124_v1` 16:14:49（UTC+8）起跑，PID 505/507/513，CPU 0–5、四线程、两臂固定→定向、外限 1,280 s。配置 SHA-256 `b2b24848471732bb6057e68b5809ede407d938a5eb03706e32b2c8f48853d705`，驱动 `083f1f4fcc0f18d16e86bd8b3db37975c1f74a1af107409a895c3d9d59a63943`，资格 `8c0ce0a97bcfedc6246968e927f1ea563b434c2fb88de52eeeabf3ec3a78c774`。运行规格 720 RAW s／6 请求／0.01%，共费实际筛选 113.363032440 s，候选执行不缓存。11 项 WSL 回归通过。[匹配驱动](tcad_ibex_20261123/run_aes_marker_repair.py)
- **停止与计量** 定向驱动提供三项已冻结请求，不为补满六次评估生成额外元组。两臂比较同目标首达、各自 720 s 窗内最好、实际工作量与物理细节，整臂总耗时分别随裁剪或计划完成等实际停止原因解释。
- **新鲜固定首次达标** 首批 215.543343 RAW s 因 SS 相对 hold 拒收；第 2 次初评独立 DRC 4，经真实 marker 放开两信号邻网重试，独立 DRC 0、天线 0、三角门与 SEC 11089/0。计费首达 434.355541 RAW s，33.7824 µm²；三角绝对 hold +336.273953／+523.914856／+55.906613 ps、TNS 0，SS 新负 setup 1。首达重试收据 SHA-256 `11bea47a3cc008ea7b5b9541e643319cd126f80462e150876df7fa79fc97f5f1`，SEC `37feb41b043be9f386ef4c68f2876883cac40c1a81f88a1897d96c9d0fe2c0fb`。第 3 次已起跑。
- **固定完成与定向开始** 固定第 3 次计费 641.052479 RAW s 完成且 FF/TT 相对 hold 拒，第 4 次启动后在首次 FF STA 被硬窗截停。固定派发 4／完成 3，6 DRT 启动、16 STA 启动、5 独立 DRC、1 SEC，最优仍 33.7824 µm²；`fixed/summary.json` `19d1bb4b07b784bd9551770f41a6e404143de752534cf18b12a33d3e81340327`。定向实际计划准备 0.041655 RAW s 已收费，历史 marker 报告 `a71a8c915a1c8780042d4cd4684768410a35822336187bd94f4fc1a04cc151c1`／`3c9b97ff6886520c3c1e2959d0550990354583773584ea48c1a6461ed51533cd`；计划 SHA-256 `b05645665318f1e49b8e78fb2d682111d7a1af69f225149035c5f137f0105d76`，追加实际提示绑定的最终输入配置 `632fa75f80a4d21eeaab2cd667858c1191d2422765d711ed151928f54978e42e`。
- **同物理端点的一次物理首达** 定向第 2 次实跑一次即通过原三角、独立 DRC／天线 0 与 SEC 11089/0。面积同固定 33.7824 µm²，ODB／DEF／V、三角完整读数一致、SPEF 除日期一致。首达 434.355541→332.364686 RAW s（−101.990855 s，−23.48%）；省去固定相同动作的首次有 4 个独立标记的物理调用，实测该首次工具合计 98.014270 s。定向第二次结果 SHA-256 `aa7735f4dda8c6614d1a262d3f10599252a52286abcddf9c594c4d05c9a92f3d`，物理 `22e34be752643a8882e93490bb40be69e3fc5daa0dd0e2fde06a0bcddfb023c9`，SEC `d626a915e0566bc608ddc51af56951da56b1a551320b8b8e16b74f39c03187a8`。第三次原六门继续真实物理。
- **完整两臂与窗内六门通过** 定向第三次 454.205221 RAW s 成功，窗内回收 65.0624 µm²（0.055844%），较固定 33.7824 多 31.28 µm²。六门按同一冻结起点和已登记放行范围重做 1 次 DRT/RCX、3 STA、独立 DRC 0、天线 0、SEC 11089/0。与单独可行性 ODB/DEF/V、同视图和去日期 SPEF 一致，非缓存。固定／定向派发与完成 4/3、3/3，DRT／独立 DRC／STA／SEC 启动数分别 6／5／16／1 与 3／3／9／2。总结果 SHA-256 `81f684dfc6a0236da300295827e88999364ff300a093d9bd5f8303d07725a92e`，定向六门物理 `85f1f5e76f50d6414d9ba99c7f7a676dac3c3ece685bb7cc5e7f341d0ceb8622`、SEC `0e2579a0c6eb594534a6a3a86e9017fe3673acf41bd41bc6d487a6658c4c0263`。已知候选和邻网的使用显式保留，本样本为 AES 定向开发验证。
- **独立核验与归档** 核验驱动退出 0，原件和仓库核验收据 SHA-256 `7b9a49f585b922b372cfaef422384afa48308675585ac0fc1a4fd3dcd3b12a0a`。两类原件归档 `scratch/tcad_ibex_20261123/aes_marker_repair_20261124.tar.gz`，273,120,148 字节，411 个成员，374 个普通文件逐项 SHA-256 与 WSL 原件一致，包 SHA-256 `dd5148e4dc926ab50c7122a1c1f34df5dde4f5d4b96cb5cfed01a5eeded106b3`。115 项核心与 11 项 WSL AES 回归通过，记录脚本退出 0。现行口径及 OI-098／OI-100 更新。[AES 定向修复报告](tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md) · [独立核验](tcad_ibex_20261123/AES_MARKER_REPAIR_VERIFIED.json)

### 2026-11-24 TCAD-SKY130HD-DIAGNOSTIC-INPUT-ECO-ABBA-V1

- **预登记与检验点** 从 `db72dd09`，两种物理验证策略用相同诊断包、相同冻原和六动作。标准执行冻结起点初次物理及当次标记证据重试；诊断输入式在首次物理评估前从绑定的独立 DRC 证据计算预放行非时钟信号网，实际新标记有据才能回退。对照应保持原物理与证明门、三角、原 I/O／SDC、0.01% 目标、720 RAW s 与共费筛选 113.363032440 s，单次 PA，每臂实测准备和实际工具收费，无物理／合格端点缓存。同机同核 ABBA 顺序优先。若输出面积、时序、几何或证明变化，逐项报告，不以耗时差作为相同端点证据。开发接口无需已知 AES 目录、排名或网名；物理证据限于同一个 AES 六门。[先前 AES 组件证据](tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md)
- **输入与正式起跑** 无 EDA 干跑先查出 CPU 0–11 与原资格 CPU 0–5 不同，改绑后得 8 标记、20 直连、4 邻网，准备 0.096189 RAW s。错误候选、错误 DEF 和有未归属 marker 的行为回归，AES 专项共 15 项通过。运行时从证据重算，无显式候选排名和邻网硬编码；输入绑定冻结矩阵、SDC、原 EDA 布线和独立审计身份，完整可操作证据才提前放行。历史独立审计耗 15.075220 RAW s，已有诊断包与本轮实测的读取／映射费用分开。`aes_diagnostic_repair_abba_20261124_v1` 16:45:41（UTC+8）发出，CPU 0–5 上四线程，PID 431/433/438，外限 2,530 s，正式顺序 `retry_1`、`guided_1`、`guided_2`、`retry_2`，每臂一个同六门逻辑请求，原硬窗和全部门。配置 SHA-256 `74b711f7052a2a271efa581d05eae22f583c945639bca2a412f1dccae5a74e2a`、驱动 `ab801dab27eb74b590e4a93734def58c142272edb3691ca38076a02a071867bf`、额外审计输入 `2f8bdcaa174fcae9e5d2b3d7ac9568839bd814d964e03d4132cba6b82c8a87ec`。[运行入口](tcad_ibex_20261123/run_aes_diagnostic_repair.py)
- **首个标准臂初次物理复现 DRC** 真实 `retry_1/01/initial` 的解锁几何和独立标记逐字复现原件，有 8 条 DRC 且无其它物理或时序拒因，单次 PA。实际审计 SHA-256 `b630028390acbd3fc4c18e6b7ee0078b24defaad943c559b62030987520886b9`，当次自动重试决策 `f6cd7623a4568fc6a8eeac89053d92abaa6a35d4d91c1d8551f4d6e0e768aa86`，精确释放先前预期的四条非时钟信号网；真实重试已启动。
- **第一标准结束及诊断臂起跑** `retry_1` 两次 DRT/RCX、6 STA、2 独立 DRC、1 候选 SEC，最终独立全块 DRC 和天线为 0，SEC 11089/0，65.0624 µm² 在计费 335.523258 RAW s 通过。汇总 `10b2b814c25e75c73faf940a984b5435e075d15ceb7e7659c63bf1b1f95a5933`、物理 `ec0ec719c4742bb56c65ffe81fda95884829ad999085787908f9ecc0409431ab`。`guided_1` 当次提示计算 0.066997 RAW s 已全计，实际提示记录 `ead208591a5c2361b8bbc67d9f44e71f25fb8f8a313f1ce711e08304ba9f31b6`，原报告给出同四邻网，开始首趟真实路由。
- **追加回归** 直接调原普通重试路径会把已预放行邻网与真正新增邻网同时列为新项；现有驱动有独立用例确认只列新邻网并在实际重试保留前后集合。固定专项目增至 16 项通过，开始物理时绑定的执行器字节未改。
- **第一顺序配对** `retry_1`／`guided_1` 含相同筛选的首达 335.523258／231.616129 RAW s，差 103.907129 s，均回收 65.0624 µm²，候选 ODB／DEF／V、去日期 SPEF 及所有三角读数相同，DRT/RCX 2／1、独立 DRC 2／1、STA 6／3、候选 SEC 1／1（11089/0）。`guided_1` 物理 SHA-256 `c27c51ecca62e06979f1c15991626bcf55fcb0ec6754bd4be994fd9aabe9bab1`、新 SEC `cb25e1c3f107bcaa2ff2aa86427abe4cb17e8c6f6d1e64533c8a0f047a6b53a7`。`guided_2` 已启动，实际提示准备 0.067225 RAW s。
- **反序诊断臂已验收** `guided_2` 含原筛选 231.123264 RAW s 达 65.0624 µm²，1 DRT、3 STA、1 独立 DRC（0）和 1 SEC 11089/0，候选 ODB／DEF／V 与第一诊断臂相同。实际物理 SHA-256 `b0f933b50aa87eb897859b8ce770401be9504dc8dcd39b72762fefe6bc014c98`、候选证明 `0ef6c45ce7f4acc7f26e7361f1051c2412fbdc6c634cea141bb8f1f9ca032d7b`，最后标准臂继续。
- **四臂端点与反序比较** 四臂均在原门下回收 65.0624 µm²；两次计费首达对比分别 335.523258→231.616129 与 333.166168→231.123264 RAW s（少 103.907129／102.042905 s）。两标准初次报告和规范几何逐字复现旧诊断，8 标记；两成功重试与两次诊断首次结果的 ODB/DEF/V、去日期 SPEF、DRC/天线、全部三角量及新增负 setup 相同。24 条数据网实际变化，15,633 条保护网零变化，四个新 SEC 均与物理网表相绑、11089/0。标准两臂 4 DRT/RCX、4 独立 DRC、12 STA、2 SEC，诊断为 2／2／6／2；省掉的标准初次失败验证为 100.231572／98.278111 工具秒。总结果 SHA-256 `95e896f71d36576a9e3af8912a1602dba5e789a56c8729a1e128a59066e90412`，反序标准汇总 `69b98699306b917444729bd1709b4ddd85a35f8b3e52b8e89c0cbe1206db9d3a`。
- **四臂独立核验及适配额外输入** 独立核验退出 0，SHA-256 `ed765defd96d4beef855226e837c38ab10fd58de072990487a1f7821140afddb`。另外三份已有真实包只读检查，标记数 4／6／0 分别到两邻网／另两邻网／空；6 标记案例沿原实测仍是 FF/TT hold 拒收。只读结果 `678311dd893a13bd0bb68bbfb94e0c17b74a4d9e66d403dc140006a519713aa1`，没有新物理端点。核心 115 项及 AES 专项 16 项通过。[诊断组件对照](tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md) · [四臂独立核验](tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_VERIFIED.json)
- **原件归档及收尾** `scratch/tcad_ibex_20261123/aes_diagnostic_repair_20261124.tar.gz` 170,375,901 字节、280 个成员、253 普通文件逐个 SHA-256 核验，与 WSL 原件一致，包摘要 `1f65491a614ba7610562418aca979746f82a1ec296d7348f7f01ab91c309e926`。本节登记为带已有诊断输入的同候选物理组件对照，保留统一原门，正式证明和物理均新跑。诊断产生、其它候选和设计迁移仍另计。

### 2026-11-24 TCAD-SKY130HD-AES-COLD-ONLINE-ECO-V1

- **预登记** 从 `1be3c920` 先证伪低成本的 DRT 前诊断：真实换门，保留冻结线路，读取实际前置 DRC，检查邻网可归属性、早期标记是否遗漏原后续实体冲突和成本。若不足以定向，考虑只在现场 DRT 确实生成实体非法标记时提前转向重试，拟提交的候选仍必须满足实际 RCX、原 I/O／三角时序／电气、独立恢复 ROUTED 全块 DRC、天线和 SEC。冷启动比较固定和在线 FAECO，以同冻原、原有序筛选池、720 RAW s、0.01%、共同计筛选 113.363032440 RAW s 与同 CPU 配置重跑，不给候选专用旧报告，不缓存候选物理，阶段与消费成本从实跑原件记录。[已有诊断组件证据](tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md)
- **前置探针实际** `aes_cold_pre_drt_probe_20261124_v1/erase` 17:29:14.113→17:29:29.336（UTC+8）rc0，CPU 6–11、OpenROAD 1，实际六次换门且只清 20 条直接旧线，冻结其余 ROUTED；无 DRT／RCX／STA，子进程 14.366561 RAW s。得到 8 个可归属标记到 `_08784_`、`net4840`、`net8148`、`net8407`，报告 SHA-256 `3c9b97ff6886520c3c1e2959d0550990354583773584ea48c1a6461ed51533cd` 逐字同此前恢复 ROUTED 后实际标记。`erase/result.json` `dcfd0bf5800b4c181c185abba58a152f3cce4b3bac9f2e118ea6d994007cc7a1`。`keep` 同换门保留原直连旧线时得到 38 个标记，只有原 8 个可归属相同邻网，结果 SHA-256 `c787fbcc7044fe6bd2a57dfccd2e0a2326aaf956b6148277864d4dd6ff9184e2`，14.531757 RAW s。探针脚本 SHA-256 `f63c4a0dcc28e38dbb6ece9a15bcc65d181d5a57764bbf9c178d033e0abda7db`。冻结零动作另验。
- **探针零动作和额外标记** 冻结零动作 17:30:34.987 至 17:30:50.489 完成，rc0，14.394786 RAW s，空 DRC 报告，结果 SHA-256 `99510aee09a53ae051a45caaaad9bbac4a92439807639f239ca59570f6431ce9`。保留直连旧线多出的 30 个标记各涉及至少一条应清除的直连网，分别为 15 short、10 最小面积、4 间距、1 cut short。三项诊断均无 DRT／RCX／STA 或正式端点。
- **配对识别及有效门** 冻结正式三臂次序固定→固定加在线诊断→FAECO 加在线诊断。原筛选池和同冻原，无硬编码先前候选与旧报告，不复用候选端点。后两臂共用同一实时前置 `drt::check_drc`，真实换门、只清直连旧线，OpenROAD 1 和 60 s 阶段上限，实际完整非空且每项可归属才提前放邻网，最多一次由真正新 marker 支持的回退。比较共同 720 RAW s／0.01%／6 次逻辑及共同 113.363032440 RAW s 筛选，CPU 0–5、DRT 四线程、全部原门含最终独立全块 DRC、天线和新 SEC。任何实际前置开销均计入所属臂。
- **一体化诊断与正式启动** 一体化真实调用单独从同六门动作复现 8 个标记和四邻网，不读取旧候选报告，无 DRT；14.595520 RAW s（含工具和解析），`aes_cold_preview_driver_smoke_20261124_v1/preview/diagnosis.json` SHA-256 `1a6e3ea9fa4cd076448c872837fd26393d962d24a6be8b9ab4b1610e6df2a53d`。旧分支两项失败可复现，新版 AES 专项 18 项通过。实际 `aes_cold_online_matrix_20261124_v1` 17:32:32（UTC+8）起跑、PID 457/459/462，CPU 0–5、DRT 四线程/诊断单线程、外限 1,900 s，三臂 `fixed`→`fixed_online`→`faeco`。配置 `591d18715ecac17cd181a68d481417f1d526db3c8cc6e05e2f8b1a2173731d6a`、驱动 `1bc106d589a771379c2c2c1fe5cde017c8849bae4d15a75efde859369c4b076a`。FAECO 只保留原相对 hold 延后和触达电容重排，禁用旧开发案按非法布局初读 hold 暂缓重试。[正式入口](tcad_ibex_20261123/run_aes_cold_online.py)
- **固定首次达标** 初次计费 213.704420 RAW s 因 SS 相对 hold 拒；第 2 次按当次 4 个 DRC 标记释放 `net4840`、`net8407` 并重试全门通过，独立 DRC 0、SEC 11089/0、真实回收 33.7824 µm²、含共同筛选首达 429.504405 RAW s。重试物理 SHA-256 `82de4cd0ba36942aa206c32e4814d31b51b9555a17714f73a90bcf890866b0e5`，SEC `2f5097b10ad89f7d26bad19bf1b089d64bd95c418586318abb3083e9378a7544`。第 3 次实跑中。[冷启动报告](tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)
- **固定收束和同派发诊断启用** 固定派发 4／完成 3，6 DRT、6 独立 DRC、18 STA、1 SEC 启动，窗内 33.7824 µm²。第 3 次在 633.036522 RAW s 判 FF／TT hold 拒，第 4 次独立 DRC 被最后 2.311277 s 硬窗截停。固定汇总 `28aaf3edd4d0c2ae9adb9e87bb216ce66291ebd6a98a00edc35941beda1dcf8e`。后续 `fixed_online` 首组实际诊断 0 marker、无预放行，已有 14.685819 RAW s 开销，诊断 SHA-256 `5297a729861f5b7f6725b89216b7ff4fe5d807efd066dda84b4ef61c2f893b01`。
- **同固定派发冷启动首达** `fixed_online` 前两次实时诊断 0／4 标记，第二次实际发现 `net4840`、`net8407`，两诊断总 28.530726 RAW s 均已收费。第二次仅一次完整物理即接受，回收同 33.7824 µm²、独立 DRC 与天线 0、SEC 11089/0；与 `fixed` 合格 ODB/DEF/V/逐角一致、SPEF 去日期同。首达 429.504405→358.364204 RAW s（−71.140202 s，−16.56%）。固定第 2 次失败初始耗 96.870336 工具秒。诊断 SHA-256 `129975205c0078bef64ecdb21f312db20371e480a0d8021408e5c6cdbcff851e`，物理 `3cfb1fb2682a085cfadf7be65720f141d1a2cf7c7f14f3eb999a4d77d3da3766`，新 SEC `352164983e394c77c6b6dbf71df7da3a8fd4256c98a6a5b7870785002ab55b12`。第 3 批新鲜诊断 10 标记到 4 条邻网，正式重布线在跑。
- **同派发第三次及下一项** `fixed_online` 排名 4–9 的第三次经一次预放行物理在 476.335564 RAW s 完成，FF/TT 相对 hold 仍拒，不计物理面积。结果 `708c62b266cae7fb833a5db3f3e65fcf241065a24f34ddc628cf78908cfee671`。第四次与纯固定原派发相同，诊断 4 标记识别 `net4840`、`net8407`，耗 13.734402 RAW s，SHA-256 `1008516ad770e771c8a536d084be43e82d6798df81e612c119a56d6c02dfd26f`，正式评估继续。
- **在线固定收束** 6 个派发、5 个完整请求，真实 5 DRT、5 独立 DRC、15 STA、1 SEC、0 物理重试，窗口保留 33.7824 µm²。第 4／5 次 594.682588／709.623803 RAW s 完成，均只有 FF/TT 相对 hold 拒收。5 个完整诊断合计 70.403389 RAW s，第 6 次诊断被硬窗截停（子进程实际 9.957614 s），无第 6 个诊断收据或正式 DRT。汇总 SHA-256 `bbbecc263bc90e1795be6c2fe3fd099435f8b15b4d08d78c9f67449c070529e9`。第三臂按同物理后端开始。
- **FAECO 实际首个重排** 冻结电容特征准备计 0.583219 RAW s，首组 SS 相对 hold 触发原后缀重排。第二组排名 9、10、15，实时 6 标记预放 `_03615_`、`net8222`，一次 DRT 后独立 DRC 0，但 343.985468 RAW s 时仅 FF/TT 相对 hold 拒。结果 SHA-256 `83db2462d7fdf34364b1d3682633c1cc23bd4336053cf6b795e56756302268c0`。下一组排名 6、13、16，诊断重新得到 5 标记与三条非时钟邻网，SHA-256 `17898dce9041916ce086f3d0b0d9f0b2a6c809e31bceeeeefd7e7c44d058ac65`，本组三角与其它原门仍实跑。
- **FAECO 第三次达标及旧未知六门确实派发** 第 3 次一次完整物理和新 SEC 11089/0，计费 476.503964 RAW s 接受 33.7824 µm²，SS 新负 setup 1；同后端固定在线为 358.364204 s。物理 SHA-256 `12660745d0c56677f7340759193043e826bb315941add004fad5ce2eb73e6cf6`、SEC `8f0e4d54f89f01bfeaa05ceaab9d6c91177b422afea4daf19e9631ab08d3796b`。第 4 次原排名 6、7、11、13、14、16 与旧 v3 未验证重试的组相同，实时 8 标记预放四条数据邻网，诊断 `ba4d6c8f650574c324aa46cb436a61080608aa6b828ad5a02f5aa0949c45ddb3`，正式物理继续。
- **旧暂缓六门在窗内合格** FAECO 第 4 次于 609.355825 RAW s 实际回收 67.5648 µm²（0.057992%），22 实际改线均允许、15,635 条保护网零几何变化。三角 hold +0.048961／+0.076827／+0.730305 ps、TNS 0，原 setup 预算过且无三角新增负 setup；全块 DRC 和天线为 0，SEC11089/0。原 v3 同组非法初评 SS hold −0.082157 ps 曾导致暂缓，该组新鲜实际修正后资格已验证。实际结果 SHA-256 `34e014c63236b4e162e60b865b5866a2d532fa46f59346326430e14957f2e4db`、物理 `aa2ecd7f84b9ece00084ed839d977c811b98184748cb1efb7b1dcc8a045994ff`、SEC `c3129f3d3c334ce6f3ac8dd0a0c0e3340c89e1cf42fe8cae8082fa13a23a879b`。
- **三臂终态** 固定／在线固定／FAECO 最优正式回收 33.7824／33.7824／67.5648 µm²，含筛选首达 429.504405／358.364204／476.503964 RAW s。FAECO 派发 5 完成 4，5 DRT、5 独立 DRC、15 STA、2 SEC 开始，5 个完整诊断合计 73.023165 RAW s。第 5 次有物理、三角和初步 98.8448 µm² 候选，独立恢复 ROUTED 全块 DRC 被最后 7.520571 s 停止、无 SEC，故留在正式窗未验收。物理 SHA-256 `7e7e5e691462798c4777cdf80dec4172f73f5a352b44378a7b0c475c1a713298`。总结果 `b6a2ff7dc93bfbf4a11dad73d8124ecc14033944eaa28c95ca44d2683bfc63c9`，FAECO 汇总 `799412646dbe22d7311c8dcbf25e529601338e619b74515123e76e49f253d7f8`。
- **独立核验与窗外补审预登记** 三臂独立核验退出 0，摘要 `0dbe08db65c62b6815d1a850a682648414dc2d17355ee05ae750ae29e02deff7`，115 核心／18 AES 专项回归通过。第 5 次按当时原物理 ODB/DEF/V、原 RCX 和三角收据及规范几何 SHA 绑定，独立重查同几何真实全块 DRC 和天线，各 0 才实际 SEC；若违例即拒，不再修线／重布线、不另跑 STA 或 RCX。物理 98.8448 µm² 的窗外资格只在独立检查完整后判定，正式 720 s 矩阵保留 67.5648 µm²。
- **同一第 5 次产物窗外合格** `aes_cold_online_fifth_completion_20261124_v1` 的 9 动作端点保留原已测 DRT/RCX 和三角，不重做。恢复 ROUTED 的同几何 DEF SHA-256 `a5be8b084fca4a9fc6611b91f707a85a1cc3e3e4785df9409fcaa61dd1f5211d`，独立 DRC 0、天线 0、SEC 11089/0，三项分别 14.664002／10.294580／15.784759 RAW s，候选 V `a798d19c49f831f27e58549c245a8e37618e215af01cc95a51a3e95fcc29209d`。确认窗外同物理回收 98.8448 µm²（0.084840%），TT 新增 1 负 setup 且原门过。结果 SHA-256 `d82b592d7ddc171c6601f061361de6596b5154389c97bde8e640e709e9d105df`、独立 DRC `7a78515e7c283530eacd9ce98134d93d91fad9da9ab8a1e186219e3636fe7d43`、SEC `841b952b54406a22424e18050277cf674255b772b5a0af5d24dc71b8b9001ac2`。原 720 s 验收不回填。
- **归档收尾** `scratch/tcad_ibex_20261123/aes_cold_online_20261124.tar.gz`，457,281,993 字节、766 成员、686 个普通文件逐项核对 SHA-256，包摘要 `580541950ca6d1dd970e5e32579219c258ac26fd208881be02428a7d2d1c8fc1`。包含前置诊断、一体化烟测、冷启动三臂和第 5 次窗外补审共四个原件根。正式及窗外口径分别保留。最终核心回归 115、AES 专项 18，记录脚本退出 0。[三臂证据报告](tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md) · [独立核验](tcad_ibex_20261123/AES_COLD_ONLINE_VERIFIED.json)

### 2026-11-24 TCAD-SKY130HD-AES-FACTORIAL-REVERSED-ORDER-V1

- **配方预登记** 从 `18a34c3c` 新跑完整 2×2 和反向重复。固定／FAECO 派发分别配旧保护／冷启动实时诊断物理后端，每种顺序四个组合，CPU 0–5 串行，OpenROAD DRT 四线程、诊断单线程。两个 FAECO 用同一相对 hold 首次延后触发的触达电容后缀排序，固定臂原机制共用。两后端仅改变实时诊断和首次放行；后备现场 marker 重试照旧。原冻结输入、筛选池、113.363032440 RAW s 共费筛选、720 RAW s、6 个请求、0.01%、原 I/O、三角 setup/hold、电气、全块解锁 DRC／天线／非空 SEC 保持，候选专用历史诊断、端点与证明不缓存。独立核验对象包括首达、合格面积、逐角与工具台账、真正截停时点。交换顺序检查观测时差，以同一 AES 设计解释，不将重复当作更多设计。[实验路线](../planning/TCAD_EXPERIMENT_ROADMAP_20261124.md) · [前三臂证据](tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)
- **留出原配方只读核对** WSL ORFS `da8f092a02a8e75658cc3100691aabff05f35629` 的四优先与四替补均有原 `config.mk`／`constraint.sdc`。JPEG 5 ns，Microwatt 15 ns 且按具名端口绑原 I/O；UART 270 ps，Ethmac 1,000／300／300 ps 三实际时钟和对应虚拟 I/O 时钟。多时钟全域约束与门值应在读取方法输出前锁定。尚无新物理、STA、筛选和资格裁定，不纳入 AES 本轮计时。[留出名单与门](../planning/TCAD_EXPERIMENT_ROADMAP_20261124.md)
- **实际起跑** `aes_factorial_20261124_v1` 于 19:07:25（UTC+8）启动，PID 435/437，CPU 0–5、DRT4/诊断1、外限 5,150 s。正序 `fixed_legacy`→`fixed_online`→`faeco_legacy`→`faeco_online`，下一轮完全反向。协议 SHA-256 `cc4d521ac900c001b72f285f53c0728ef04043cfde79e1dd86ddfebcdc56a1b0`、首单元 `38f37f0cddf0dd7856e71a248ec7a1c4228e494e0a61f77b0e92c758698a0267`、启动驱动 `9ffbb99145edff395f5c7b700fc21f31f0d04f99769fc8aea9d78d1d6d7c5376`、预检迁移 `8c0ce0a97bcfedc6246968e927f1ea563b434c2fb88de52eeeabf3ec3a78c774`。回归复现旧三臂缺格，新 WSL AES 专项 19 项过。同机执行期间无并行新 EDA，第一单元正式路由已开始。[矩阵驱动](tcad_ibex_20261123/run_aes_factorial.py)
- **首单元同目标实际接受** 正序固定常规第 1 次 SS 相对 hold 拒收，第 2 次依据当次 4 个独立标记重试后全部原门和 SEC 11089/0 通过，回收 33.7824 µm²，计费首达 448.639061 RAW s。实际物理 `a9b3a2d4d1437995b0cd3e5ffafa915b1df2c4fb6f1da82634dbf534f23bd1b6`、SEC `de8c18e1fb2bc0ee0d40131d3dfd416db9c08f2431935bbe98ab6dd7219a7792`。
- **正序常规固定完成、在线固定开始** 常规固定 4 派发／3 完成，6 DRT 开始、15 STA、5 独立 DRC、1 SEC，窗内 33.7824 µm²；第 3 次仅 FF／TT hold 拒、第 4 次 DRT 硬窗截停。汇总 `7088e0f210d0c4a67bd19ab3397f4a98fb1eee3f3a13d7e2aec010b5a1a59115`。在线固定第 1 次实际前置 0 marker、14.881522 RAW s 已计，从原首批正式物理继续，配置 `bc32aa72088edd261efd3d3151145aa81747c9cafce4680374a590dff0b198f6`。
- **正序固定同物理首达对照** 固定常规／固定在线都第 2 次接受同一 33.7824 µm² 端点，合格 ODB／DEF／网表逐字节一致，真实 SEC 11089/0。448.639061→364.633179 RAW s（少 84.005882 s），计入在线两次诊断 29.362355 RAW s。在线物理 SHA-256 `326ce541ca33001bcc847497a52a55e443a0062df2b2cb61f119b5410fe7d20c`、新 SEC `e2510f2108cc623594de12da83f57a7ac1d7e634a4a9f1f6d54d770d7578197b`。
- **正序在线固定终态与 FAECO 常规启动** 在线固定 6 派发／5 完成，5 DRT、15 STA、5 独立 DRC、1 SEC，正式回收 33.7824 µm²。完整诊断 5 次共 71.553828 RAW s，另第 6 个预检被墙钟截停；第 3–5 次只因 FF／TT hold 拒。汇总 `5741461474a3c9fea0d87658e4cc208928a67ee4af51f4c848ff96b91ca08b68`。正序 FAECO 常规保留相同触达后缀排序和原反馈，禁用在线诊断，配置 `de202ea44f5d10e70af76030a778f0beeccedc684f3091d1dc16348561dd0b01`，首批已派发。
- **前两臂独立核验** 真实 `independent_verification_prefix_2.json` SHA-256 `86873fd13490945a994cf7666f750143f07416f903c2ab0c7dc74253fc4b8dd2`，同首达动作和端点 ODB/DEF/V、去日期 SPEF 及完整时序相同。完整物理重试 2→0，诊断开始 0→6（最后一次截停）。
- **正序 FAECO 常规首达** 实际第 1 次 SS hold 拒，第 2 次真实重试后 FF/TT hold 拒；第 3 次原排名 6/13/16 经当前合法 DRC 重试、原三角门和新 SEC 11089/0，于 641.813831 RAW s 回收 33.7824 µm²。实费特征准备 0.606531 s，无在线诊断。候选物理 `6488f07dc2b4b395f016a7570e80342c5a1f9513926c79592ecd1eae976848cf`、SEC `1456aeba171d98376e6aebe7aaa0e414c47b98f438513d5302ff31dcb9b26099`。累计第 4 组正实跑。
- **正序 FAECO 常规终态** 4 派发／3 完成，6 DRT、15 STA、5 独立 DRC、1 SEC；第 4 次 DRT 受硬窗 78.116372 s 截停，窗内仍为 33.7824 µm²。汇总 `7e836295b49d6129b061889caa569f07e5628f991523d044f92f58eef9b1bc2e`。FAECO 在线配方 `b890d2c14fba17ea354a429203cf935f33cda7103e10f65faeaf2507405f77b9` 同调度，首组在线诊断实测 0 marker、14.322271 RAW s 已计。
- **前三单元独立核验** `independent_verification_prefix_3.json` SHA-256 `8955c833255a0bc5ca9b96d3a0d80d388cc43890541e4fb9e49f4aacf0a719fc`、审核退出 0。常规后端中固定和 FAECO 首达同面积、不同物理，正序 FAECO 实测晚 193.174770 RAW s，两臂各两次完整重试。
- **正序 FAECO 同调度首达对照** 同样第 3 次接受同动作和同物理端点 33.7824 µm²，常规→在线 641.813831→483.860280 RAW s（−157.953551 s）；前三诊断合计 42.634696 RAW s 已计。ODB/DEF/V、去日期 SPEF、完整逐角相同，在线真实 SEC 11089/0。在线物理 SHA-256 `16b13830bec3ea66b55d5643b2d3fdf4b7e526b74484bda7492aacb107c58177`、SEC `33efebe2a5b056c972cfbf7eb3537c4cd353f761b1b0a52cbbc3f863a2a5f79f`。
- **正序四臂验收与反序起跑** 正序 FAECO 在线第 4 次 619.308802 RAW s 回收 67.5648 µm²（0.057992%），三视图无新增负 setup、独立 DRC 和天线 0、SEC 11089/0；同后端固定首达快 119.227101 s，但窗内少 33.7824 µm²。第 5 次在 SS STA 被硬窗截停，线上 5 派发／4 完成、5 DRT、15 STA 启动、4 独立 DRC、2 SEC、5 诊断。物理 SHA-256 `6fc51fc2e399f70b3ed5e1fc520f079d69fe879a6d03f84a5d3123f7828078f2`，独立正序核验 `2161d1e7ea29d4df84babbe49c2de39a2cd3636abb5396282109f1f4a1144e8f`。反序已真实从 FAECO 在线起跑，首配置 `258085a4811462f8517e58afb9f9646235d613c7f0304bc59354a08fe74cbd97`。
- **反序在线 FAECO 复制六门** 第 3 次 483.866765 RAW s 回收 33.7824 µm²；第 4 次 620.070334 RAW s 回收 67.5648 µm²。该六门实测相同 ODB/DEF/V、去日期 SPEF 和全三角，新 SEC 11089/0、无新负 setup。物理 SHA-256 `6850557a2603cf59a16133494ad3bd89dc32b48a207f486d7dce7935cebb81c7`、SEC `1ee110ca4cd9ec19e47f9793232e43177aa1c7306b7cfc6784d4b4fa82a19862`。第 5 次已派发，正式终态另验。
- **反序在线 FAECO 终态及独立核验** 5 派发／4 完成、5 诊断、5 DRT、4 独立 DRC、14 STA 开始、2 SEC；九门第 5 次 TT STA 截停（2.842291 RAW s，续窗上限 2.991800），未发 SS、独立 DRC／SEC，窗内正式保留 67.5648 µm²。汇总 `bef2fe7bdf5f4552e8dcb7daa0e9e8da0a7566ab9eafbc51e8ad92a160670822`，前五单元独立核验 SHA-256 `a41636800de39f8a383c2c453e3fed8a4fa2f97da96c6e553ba8b3ae64320117`；反序 FAECO 常规继续。
- **反序 FAECO 后端对照终态** 常规第 3 次经重试首达 648.246971 RAW s，33.7824 µm²、SEC 11089/0，在线实测早 164.380206 s。常规第 4 次 DRT 硬窗截停，窗内仍为 33.7824 µm²；4 派发／3 完成、6 DRT、15 STA、5 独立 DRC、1 SEC。汇总 `f4bc3e81201d3175e58b881ca597b1b445cd0af0ddfd2c4f7abb84d1a4e5e624`；反序固定在线已起跑，配置 `f0d732a77508403ee5cdaf7e55fa1652dd3985c959a108bf2c448f4e0b546bc0`。
- **六单元独立核验** `independent_verification_prefix_6.json` SHA-256 `aec6248e606c160be6fec3d4e88960d01a9c429abd497f7784a25c9228085950`，审核退出 0。反序同 FAECO 调度切在线，确认首达同动作／物理、窗内面积多 33.7824 µm²；常规 FAECO 同物理跨序时差 +6.433140 RAW s。
- **反序固定在线首达** 前两次实时 0／4 marker 诊断共付 30.751658 RAW s，第 2 次一次正式物理及 SEC11089/0 接受，计费首达 370.875315 RAW s、33.7824 µm²，物理和三角与正序固定在线复现。物理 SHA-256 `a1952f35487b83cb6c3b07cbf3bf532e979713f3aa760e3141c63a6d3ea557ff`，新 SEC `044f8ada5added79fe353395981bd796255ce3db28144d9948d0aedb647b88a3`。
- **反序固定在线终态** 5 派发／4 完成，5 个完整诊断计 77.255485 RAW s，5 DRT、15 STA、5 独立 DRC 启动、1 SEC。第 5 次硬窗截停于恢复 ROUTED 独立 DRC，允许 0.992095 RAW s，实际至终止 1.008927 s，未做其 SEC；窗内 33.7824 µm²。汇总 `d938a29f30ae5b08ad76974f60e97609d9f94443a1c37e56e5072404a24b051b`。最后反序固定常规已实际发出，配置 `eb6197efcb41fcb45f179198f897b0c149716b23f87ef184dee0fa3aad691b14`。
- **反序固定同物理首达对照** 常规→在线 443.274307→370.875315 RAW s，少 72.398992 s，同首次 33.7824 µm²。独立实查同 ODB/DEF/V、去日期 SPEF 和所有视图，两件新 SEC 11089/0。常规首达物理 `8046ec46c47800a2c0dd09c4fe83b02e5ff93ca4d3c69e392374c92e7672c53c`、新 SEC `2e8afc077af295846a5aa2ebdae54f71e4e8425ded032ae431fc8677b126f286`，末臂剩余预算继续。
- **八单元完成** 总结果 SHA-256 `a9efe4ed1b2ed28674ec57be380b153528a6db321360a91f8fa5c3971ffb3510`。37 派发／29 完成，DRT、STA、独立 DRC、在线诊断、SEC 启动／正常返回 44/40、119/117、38/37、21/20、10/10。四常规单元第 4 次 DRT 截停，在线实际分别在预诊断、SS STA、TT STA、独立 DRC 截停。固定正反序的后端首达改善 84.005882／72.398992 RAW s，FAECO 157.953551／164.380206 s，均对应同调度同物理。在线组内改变调度，比在线固定窗内多合格 33.7824 µm²，正反序首达更晚。全部八个的独立审查另记。
- **全量独立核验** 两顺序的每个同条件首达和合格最优均复现同动作、物理、三角。在常规后端内，FAECO 两次分别慢 193.174770／204.972664 RAW s 而同面积；在线后端下 FAECO 两序分别在 619.308802／620.070334 RAW s 验收相同 67.5648 µm² 六门，三角无新增负 setup。核验 SHA-256 `707ec4622cf563fb90fbda26594f8966e21f581b1db4a6f5acc7b9f9bcbbb335`、退出 0。核心 115 项、WSL AES 专项 19 项通过。[2×2 正反序报告](tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [独立核验](tcad_ibex_20261123/AES_FACTORIAL_VERIFIED.json)
- **原件归档** `scratch/tcad_ibex_20261123/aes_factorial_20261124.tar.gz` 包含两顺序八单元、原件、源码与独立核验，1,127,603,727 字节，1,659 个普通文件逐个 SHA-256 和源一致，包 SHA-256 `e99b28c640312cd384973414739fd85e2b1fda607ed2c9feee38c8dd1592f9ad`。完整矩阵完成计时和审计；跨设计与在线单门仍另设实验。

### 2026-11-24 TCAD-SKY130HD-JPEG-ORIGINAL-CONTROL-QUALIFICATION-V1

- **拟启动而未运行** 等 AES 八臂真实时窗全结束，再从原生 SKY130HD JPEG 配方只制备冻结 CONTROL。原顶层 `jpeg_encoder`，SDC 5 ns、原 I/O 各 1 ns、时钟源延迟 1.175 ns，CPU 6–11／四线程，native producer 上限 3,600 s、资格原件读取上限 420 s。目录 `/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/sky130hd/jpeg`。原 DRT/RCX、原 I/O/三角、hold、电气与 DRC／天线及非空证明单列，资格受具体门控制。阶段保留失败资格，不启动候选和方法比较。[起点入口](tcad_holdout_20261123/prepare_jpeg_control.sh) · [留出计划](../planning/TCAD_EXPERIMENT_ROADMAP_20261124.md)
- **启动前发现顶层入口依赖** 当时 `holdout_tools.py` 只允许 `aes_cipher_top` 和 `gcd`，JPEG 资格需纳入 `jpeg_encoder` 并独立验证。先完成 AES 当前源码绑定复核，再适配资格入口，进程中的 AES 配方保持完整。此检查只读取源码。
- **原生制备实际启动** AES 八单元与独立核验结束才适配共享白名单，加入 `jpeg_encoder` 且入口冒烟通过。JPEG 原生 20:30:36（UTC+8）从 `/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/sky130hd/jpeg` 正式起跑，PID 334／422／438／440，CPU 6–11 四线程，producer 3,600 s、资格 420 s、整个外限 4,140 s。原配置和 SDC `ed25747fae86be6f0f91812f4910c9ffe992f45e072ae2f891cfc4ab6f7dd365`／`287e631b6692a6887390f28def96cb3e812862a78d3a537fa005ceb3d1996868`，原件 `input_manifest.log` SHA-256 `dc3052f4df848567ec8902ad35f9fe710a2f0aecd4ec6d15d52b06bc4b1d168c`。Yosys 已实跑，资格读数待原生端点。
- **GRT 完成并真正启动 DRT** `5_1_grt.log` 20:37:00.719（UTC+8）落盘，SHA-256 `535dd29338179822f1d49dc086047117e4a8219fe56e2ccab66807779b4494ae`。随后正式 `5_2_route.tmp.log` 有实际详细布线进度。最终 DRC／RCX／三角资格仍未出。
- **阶段快照** 20:46:47（UTC+8）实际日志第 0／1 轮迭代末违例 22,331／12,270，第 2 轮仍在执行。AES 八臂和论文阶段可以交付，JPEG 起点继续单列跟踪。
- **原生 DRT／RCX 完成** `producer.rc` 为 0，`real` 1,951.17 s。原生共实际三次 DRT，首次 DRC 归零后插入 35 个天线二极管，第二次 DRC 归零后为两处残余再插入两个；最终 DRC 0、天线 0 网／0 引脚。`6_final.spef` SHA-256 `111374abce87f0700da477d535698c1a0603b499e566c262b5542d83d047897b`。冻结端点的原约束三角正在回读；无候选调用。
- **原生端点资格拒收** 原 19 非时钟输入及 27 输出按原 I/O 逐项核对，三次 STA 实跑并退出 0。FF／TT／SS hold WNS +218.048191／+357.532115／−2,340.726724 ps，TNS 0／0／−41,475.257007 ps；setup WNS +1,549.836703／−545.897105／−19,881.404967 ps，TNS 0／−95,987.552129／−35,205,266.613048 ps。`qualification/CONTROL.json` 为 `hold_infeasible`，SHA-256 `f6c7c85363ffe2a7a8e3842d28d5425977399c8335aa23dea2d065a1159a0cc0`。SS 同一报告最差 min 为异步 `rst`→`qnr.qnt_cnt[1]$_DFFE_PN0P_/RESET_B` 的 removal，普通 `qnt_val[0]` 输入到 D 端也为负。实际候选 DRT／STA／SEC 均 0。原生最终电气三项计数为 0，逐角电气与证明没有单独执行。
- **SS 零编辑诊断** 独立实跑清点 26 个负 min，14 `RESET_B`、12 `D`，SHA-256 `725806e9d54abd463fa0a1f010ab79eaa9a0569438f1d2b7ba61612066a2f097`。读取同端 min/max 的首版在第二次解引用 PathEnd 时崩溃，保留失败收据。v2 先将端点与标量转存再实跑，26 端点完整，22 有理想等量延时区间，4 个 FDCT 数据端两侧均负。v2 `minmax.json` SHA-256 `426a5c766ad90c9045b17f311ef9dcd30a696a38f141d7087b281540270e451b`。原报告的全局 reset recovery 表明公共输入不能累加全部最差需求，当前仅给出分支诊断，无修复或候选。
- **原件封存** `scratch/tcad_ibex_20261123/jpeg_control_20261124.tar.gz` 169,170,108 字节，114 个普通文件逐个校验，包 SHA-256 `78c76cdb6dfe88a4c453fbd78e62f02fd8e88131010719d6c8c6f6428890fbce`。独立 STA 启动／完成 6／5，含三角一组、一个端点清点以及同端探针失败和成功各一。实验结论为原生资格拒收。[JPEG 报告](tcad_holdout_20261123/JPEG_CONTROL_REPORT.md) · [起点收据](tcad_holdout_20261123/JPEG_CONTROL.json) · [SS 端点](tcad_holdout_20261123/JPEG_SS_HOLD_ENDPOINTS.json) · [SS 延时余量](tcad_holdout_20261123/JPEG_SS_DELAY_HEADROOM.json)

### 2026-11-24 TCAD-ASAP7-UART-ORIGINAL-CONTROL-QUALIFICATION-V1

- **预登记** 等 AES 正反序四臂的最后计时结束，再用 ASAP7 原生 UART 配方制备冻结 CONTROL。原周期 270 ps、I/O 各 54 ps、虚拟 I/O 延迟 66.270 ps，28 个非时钟输入、15 个输出。CPU 0–5，OpenROAD 四线程，原生 producer 上限 1,800 s、逐角 STA 120 s、外限 2,300 s。入口 `wsl --exec bash code/scripts/run_with_timeout.sh 2300 bash project_docs/evidence/tcad_holdout_20261123/prepare_uart_control.sh`，输出 `/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/asap7/uart`。主线报告预检完成，实查脚本 SHA-256 `c73e262e301b3a3265945afe82b3094ff7fabb900ab1f743bade4cbbb78f3eeb`。原 SDC、逐角 hold 非负、布线和寄生完整、原生 DRC 与天线为零后再做独立 DRC、电气和自证。此分支计原始起点资格，候选比较单列。 [UART 资格入口](tcad_holdout_20261123/prepare_uart_control.sh)

- **实际启动** AES 四臂全部写出结果后，23:38:31（UTC+8）UART 原生命令执行，外层 PID 449、驱动 451、原生限时 462、make 464。初发 `producer_receipt.json` SHA-256 `5f370ef14ed85ee635a5a16091a59353d15a61d2dfc9c81eb0c953e9fd80a7ee`。实际 ORFS `da8f092a02a8e75658cc3100691aabff05f35629`、OpenROAD `b511b6a2bc936844b0319efc8b4972bb4ad7d911`，UART config 与 SDC 分别 `9526e85d9613ffebef58f4e0ba4f02fa53b80d5dbb4de44dfa3a6f7ff0a1200e`、`73a46fba5414eb32d1fb24f2681eae9c1fdeba90a2a9762a73848f9c4edfef8b`。原生 CTS、全局布线日志已落盘，`5_2_route.tmp.log` 的详细布线推进。终态与原约束回读另报。

- **原生详细布线与提取完成** 制备实耗 77.38 s，最终 DRC 0、天线 nets/pins 0/0、标准单元 105.107 µm²／875 个。原约束读取保持周期、I/O 和虚拟延迟。三角 hold WNS +50.315／+67.502／+54.053 ps，hold TNS 均为 0；setup WNS +25.853／−39.580／−199.705 ps。`qualification/CONTROL.json` SHA-256 `18b16f9f0ddcc7ddae3d6ef54b7ae55a4996fdcc8582213f4333d9070863d77b`，状态 `hold_qualified`。候选仍 0，独立全块 DRC／电气和自证另记。
- **独立补充验收** `supplemental_v1/SUMMARY.json` SHA-256 `6b8c1eb744d3357479b6091199cc593ab6f18bedc796186eef9bf736c9e123aa`，状态 `supplemental_passed`。独立全块 DRC／天线 0／0，三角最大转换时间和最大电容违规均 0。WNS、TNS 与资格复核各角差 0 ps，setup 负端点 0／77／78。起点自 SEC 567/0，收据 SHA-256 `8c4575a6faef85e90b5932c791014468f4a5a01964807cc9ecba1c17fd64a1ba`。新增核验为一次物理、三次 STA、一次 SEC，均单列为起点资格，候选评估仍为零。[制备规约](tcad_holdout_20261123/UART_CONTROL_RUN.md)
- **原件封存** `scratch/tcad_ibex_20261123/uart_control_20261124.tar.gz` 13,673,108 字节，逐文件校验 121 件，包 SHA-256 `03ed8fc2b3525df0e312a489fc86563cdb8334e4306486fc4592079521dbb4b6`。[起点收据](tcad_holdout_20261123/UART_CONTROL.json) · [独立核验](tcad_holdout_20261123/UART_CONTROL_VERIFIED.json)

### 2026-11-24 TCAD-SKY130HD-AES-ONLINE-SINGLE-VS-FAECO-ABBA-V1

- **预登记** 基准 `e01b01bb`。同一冻结起点、18 个有序筛选动作、同一在线换门／清线／DRC 诊断后端，对比逐门贪心 `single` 与现行 `faeco`。按单门→FAECO、FAECO→单门在同机固定 CPU 组串行实测。物理和证明逐臂重新执行；前轮在线固定批次结果列为历史参照。两对比较 720 RAW s 内的合格最大面积与 0.01%（11.65079904 µm²）同面积目标首达时间。每臂限 6 个逻辑请求，均计筛选 113.363032440 RAW s，并计实时排序（如适用）、诊断、DRT/RCX、逐角 STA、独立 DRC、天线和 SEC。原 3.6 ns 周期和 I/O，setup WNS 逐角损失限 36 ps，FF／TT／SS TNS 损失限 360／360／27,049.177334 ps，逐角 hold 非负并满足 0.001 ps 相对容差，沿用现有电气、零独立 DRC、零天线和非空两态 SEC 门。报告每臂接受、拒绝及窗尾截停、候选动作覆盖及阶段计时。若两对中单门达到相等或更高的合格面积，按实际结果界定 FAECO 面积优势。 [八臂报告](tcad_ibex_20261123/AES_FACTORIAL_REPORT.md)
- **入口与输入** 实查驱动源码指纹 `a730de162b60fb948711e935c59b4f067e342a3ddb7135aad8152a89caf24f69`，冻矩阵配置 `bc62ef9ac0225aca50768bd1b243ae1311a2565c7863ad4183d29a23030002d9`、原共同物理预检 `fb4bd00ec1535ff85ab6267430984f9a8f6cb474f07d6f847c44a6c377eb265e`。WSL 计划 `taskset -c 0-5`、外部超时 2,700 s，输出 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_online_greedy_matched_20261124_v1`。 [运行入口](tcad_ibex_20261123/run_aes_greedy_matched.py)
- **实际启动** 22:57:13（UTC+8），外层 PID 328、驱动 407。实际协议 `fd55d066b3bc48bb9ab1dfb1a3d6e12f6c32cca3c59c64ae83339c59f1a2b7f4`、正序单门配置 `d6eed2f11ee3f018c9f2db77cffb613185fa0a0ff38f7ba3579294a424f89003`。正序单门首请求 `_10814_ → sky130_fd_sc_hd__xor2_2` 的实时诊断以 15.199233 RAW s 完成，预报 3 个 met1 违规、放开 `net8204`，四线程正式 DRT 已实跑。标记报告 SHA-256 `674a46074ba582c3fb878f60dddc80c1ee72ee5a62ce50011e8b15471b9edcdd`。
- **正序首个单门拒收** `_10814_` 放行 `net8204` 后一次真实 DRT/RCX 获独立 DRC 0，计费 230.114666 RAW s 因 SS 相对 hold 单项拒收（+55.187632 ps，相对冻原 −0.108136 ps），首次正式物理收据 `ee9fe128e1d163489ab13b0e0b7ba73747886896948b024cf81848a1530ffdc4`。第 2 次单门 `_10992_` 已开始。
- **正序单门第 2 次提交** `_10992_` 在 361.033971 RAW s 实际验收 11.2608 µm²（0.009665%），SEC 11089/0，无新增负 setup 端点。共同面积目标仍未达到。物理 SHA-256 `ac940ed4122f7e5d3b82665e02e4fd473fe5286e1d29f9b2c402970e26de68b1`，新 SEC `b4f52c52f686c402961a7914bc6587d830532beef13c4be0182b55b3ba09f015`。第 3 次累计 `_10992_`、`_11167_` 已实际派发。
- **正序单门进一步覆盖** 第 3 次累计 `_10992_`、`_11167_` 得候选 22.5216 µm²，477.010759 RAW s 时因 SS 相对 hold −0.172085 ps 拒。保留前项合格 11.2608 µm²，第 4 次重新尝试 `_10992_`、`_11178_`。
- **正序单门首次达标** 第 4 次累计 `_10992_`、`_11178_` 在 607.805717 RAW s 通过全部门，回收 22.5216 µm²。物理 SHA-256 `3972ed44069a999ef57a273be6e4581097b5f30092924f450ce366c51c1f2485`，新 SEC `7815bbe1c9164aa4eed3648094fdda5ca132ffa31dc0acc5518b50c5155d85e1`。第 5 次已实际派发，累计加 `_11724_`。
- **正序单门终态与 FAECO 起跑** 单门 5/4 派发／完成，首达 607.805717 RAW s，窗口合格 22.5216 µm²。第 5 次累计候选初步 33.7824 µm²，逐角 STA 完成，独立 DRC 按墙钟截停，未启动其 SEC。各次启动诊断／DRT／逐角 STA／独立 DRC／SEC 分别 5／5／15／5／2。汇总 `29b95498389bd78ccb80f1e0a52aa22cbad8c1e863d313812342673a98dad623`。正序 FAECO 配置 `250af8d6e7237b9e6c9f343aa12112ee0c94727c33729e28be350947dec08528`。
- **正序 FAECO 启用重排** 首批原排名 1／2／3 @227.798511 RAW s，SS 相对 hold 单项拒收，触发延后拆分与触达重排；排序成本 0.621071 RAW s 已计入，实际第 2 次为原排名 9／10／15。
- **正序 FAECO 第 2 次拒收** 排名 9／10／15 的在线诊断释放两个现有邻线，正式一次物理后 FF／TT 相对 hold 拒，计费 341.609914 RAW s。第 3 次开始探索原排名 6／13／16。
- **正序同目标首达** FAECO 第 3 次原排名 6／13／16 @469.963208 RAW s 完整验收 33.7824 µm²，较单门达共同阈值快 137.842509 RAW s。两者首达的实际回收面积为 33.7824 与 22.5216 µm²。FAECO 到阈值前完成 3 DRT／3 诊断／3 独立 DRC／9 逐角 STA／1 SEC，单门为 4／4／4／12／2。已派 FAECO 第 4 次累计六门。
- **正序 FAECO 六门验收** 第 4 次 @600.498791 RAW s 回收 67.5648 µm²（0.057992%），原三角无新增负 setup，SEC 11089/0。物理 SHA-256 `8bf2b4e0fba152dcee5c1659dd5cf837a94390541b603759e4b451b90987453c`，新 SEC `c903d852798e93563fad244572998b6f9d7db18dd50b6fd67784f4b27617b279`。第 5 次累计九门正运行。
- **正序配对终态** FAECO 正式回收 67.5648 µm²，比单门 22.5216 µm² 多 45.0432 µm²，两臂均 5 派发／4 完成。FAECO 九门初步 98.8448 µm²，三角通过且独立 DRC 0，TT 新增一个负 setup 端点符合原门。其 SEC 被墙钟截停，允许 2.065237 RAW s、运行 1.908486 s。汇总 `6b07703f50e09d5f80367a261433002c5b4a397ef017f106c246ba4703bcf89f`。反序 FAECO 真实起跑，其配置 `65ac29b67eb34ed7d237d04d25f426f70f2bedccbda2471f813926bfb2b46845`。
- **反序 FAECO 前缀** 原排名 1／2／3 @229.469719 RAW s 被 SS 相对 hold 拒，原排名 9／10／15 @342.467443 RAW s 被 FF／TT 相对 hold 拒。重排成本 0.608749 RAW s，下一次派原排名 6／13／16。
- **反序 FAECO 首达** 第 3 次同三门在 471.423584 RAW s 获 33.7824 µm²。反序物理收据 `45e06c792f754562c310bfa75b1b76036d7189dd7f7ebe33af79e490ddb5adb4`，新 SEC `562d72a2873bf1d93569ad155b0ce0c1406c80baaeafc72fc88db771264406ac`。ODB／DEF／网表与正序收据哈希各同，完整独立核验另计。
- **反序 FAECO 六门验收** 第 4 次 @601.581914 RAW s 得 67.5648 µm²。物理 `6deb8cf1089d8f8442c768047a07b3ddec21099ff8deb6631b73337f08fa1ea6`，新 SEC `fae919226706db5c909468680c56ef1112f57f083b873cc67b63c3f6e7f9bb86`；三个主要物理身份哈希与正序一一同，完整审计另报。
- **反序 FAECO 终态与最后单门起跑** 窗内正式 67.5648 µm²，5 派发／4 完成。九门在独立 DRC 完成后仍因 SEC 裁剪未正式验收，SEC 有效限 1.102924 RAW s。汇总 `30f6a96574223be70d3aed8b8345afa1c075cec6bcdf6100bca7a4944e4b4cd1`，最后单门新发配置 `549002abcaea59cce74ccc8a07efaacf04d1651991c2b054f750785b907dbdba`。
- **反序单门前缀** 第 1 次 @228.644616 RAW s 仅因 SS 相对 hold 拒。第 2 次 @357.140827 RAW s 验收 11.2608 µm²，共同目标尚未到。三个主要物理工件的哈希同正序，独立审核另计。第 3 次累计原排名 2／3。
- **反序单门第 3 次** @469.925285 RAW s 仍因 SS 相对 hold 拒，实际第 4 次改加原排名 4。
- **反序同目标首达** 单门第 4 次 @599.796206 RAW s 验收 22.5216 µm²，较同序 FAECO 首达慢 128.372622 RAW s。独立物理收据 `09ff6b79ba82e4457fa9cd47a6adaebf822c68511c0a5f7773478f78887b83d6`，新 SEC `66d656b69298d4a080b7ca03fc71002298f9eef1dc5f18af272467ca571fb698`。第 5 次已派。
- **四臂终态** 总结果 SHA-256 `b3f49344a094be568b92c359d66018a7cb2771f9d5e58512429b569527aec79d`。两序 FAECO 正式 67.5648 µm²、单门 22.5216 µm²，共同目标配对首达差 137.842509／128.372622 RAW s。反序单门窗口终止在第 5 次 SEC，正序在第 5 次独立 DRC。合并 20 派发／16 完成，工具启／正常返分别为诊断 20／20、DRT/RCX 20／20、逐角 STA 60／60、独立 DRC 20／19、SEC 11／8。
- **独立验收** 覆盖四臂，`full_audit=true`，首达和最优跨序各自同动作同物理端点。共同阈值首达 FAECO 469.963／471.424、单门贪心 607.806／599.796 RAW s。固定 720 RAW s 下两序合格最优 FAECO 67.5648、单门贪心 22.5216 µm²。核验收据 SHA `588495c2b9cd4b60fa284c3c20acfb7e4e8cb31a706f80eabc8b1bff315bd69b`。[配对报告](tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) · [独立核验](tcad_ibex_20261123/AES_ONLINE_GREEDY_VERIFIED.json)
- **原件封存** `scratch/tcad_ibex_20261123/aes_online_greedy_matched_20261124.tar.gz` 563,116,476 字节，逐文件验证 883 件，包 SHA-256 `a86a25537bdcbd37fadfeb93c57268e9e1295c5f683e09c13cb69b374b5b37e1`.


### 2026-11-25 TCAD-ASAP7-UART-ORIGINAL-CONSTRAINT-ONLINE-ADAPTATION

- 基线 `c8b9e0fd`，尝试将现行布线前冲突诊断和端点验收适配到 ASAP7 UART。依据已通过资格的原生 CONTROL，保留原 SDC 的 270 ps 周期、54 ps I/O、66.270 ps 虚拟时钟延迟和 FF／TT／SS，报告已有 setup 负余量。清点候选来源及面积口径，检查适配是否保留 DRT／RCX、独立 DRC／天线、三角电气、时序及非空候选 SEC。计划与 AES 强单门正式实物测试串行。实际冻结配置与证据待登记。[起点报告](tcad_holdout_20261123/UART_CONTROL_RUN.md) · [独立验收](tcad_holdout_20261123/UART_CONTROL_VERIFIED.json)
- **起点适配与预筛已执行** 原生收据缺少 runner 所用 `library_paths`，ASAP7 FF SIMPLE 库软链接和实体的路径字串不同，内容哈希相同。由适配脚本逐一绑定原资格的 15 个 Liberty。冻结 TT SPEF 预筛 18／18 通过，共同计费 81.563830427 RAW s。原件在 `/home/toylog/faeco_tcad_uart_online_20261125_screen_v2`，池 SHA-256 `73bc816db40e5ca76e4a1dd34392dc1ab9bfeba3a7b9c0cff196ce2188b8fdff`，筛选收据 `e3f6003fd6a0c97c8132798c75282308d02550e24eeec26999c58fb104419f56`。正进行零动作实物预检，候选实物仍为零。
- **实际六臂规约** `/home/toylog/faeco_tcad_uart_online_20261125_matrix_v2`，协议 SHA-256 `90bf70bb080d5544d51265e575c3ec94ff72f6342fe6b9aaf452c5476d374a4f`。单门、在线固定、FAECO 串行后完全反序。同一 720 RAW s 和 6 逻辑请求，均计筛选 81.563830427 s。原三角每角 setup WNS 限 2.7 ps，TNS 限 FF／TT 27、SS 136.973650200 ps，绝对 hold 非负、相对 hold 容差 0.001 ps。冻结 TT Liberty 功能面积 79.00902 µm²，0.01% 阈值 0.007900902 µm²。
- **strict-zero 后正式运行** v1 因评估目录相对 seed 错配在第一物理子进程前退出，保留原件。v2 分离目录，实际零动作 16.773417292 RAW s 完整通过，独立 DRC 0，网表同哈希，自 SEC 567/0，收据 SHA-256 `8ea78b314aa9ec130f37cf138421047e115c05c1cf477cc05afcdadee8a22b85`。正序单门前两次仅 SS 相对 hold 拒，第 3 次 @152.164514538 RAW s 验收单门 0.08748 µm²并首次达阈值。
- **正序单门终态** 6 派发／6 完成、2 接受，最大回收 0.17496 µm²，累计 `_0886_`／`_1027_` 于请求 5 @199.707520308 RAW s 验收。第 4 次仅 FF setup 门拒，第 6 次仅 SS 相对 hold 门拒，停在逻辑上限。正序在线固定开始。
- **正序在线固定终态** 6 派发／6 完成、2 接受，请求 3 三门首达 0.17496 µm² @152.777640878 RAW s，请求 6 四门终态 0.23328 µm² @223.565693580 RAW s。拒收为请求 1 的 SS 相对 hold、2 的 SS 相对 hold 与 FF setup、4／5 的 TT 与 SS 相对 hold。正序 FAECO 首个相对 hold 拒收、第二个 FF setup 拒收。
- **正序 FAECO 终态** 6／6、2 接受，单门 `_1027_` 第 3 次以 0.08748 µm² @151.795224386 RAW s 首达，两门请求 6 回收 0.14580 µm² @222.512908783 RAW s。请求 2、4 累计同三门、均 FF setup 拒，ODB、DEF、网表逐项哈希相同，正式物理尝试分别耗 19.420318518 和 19.574381910 RAW s。反序 FAECO 开始。
- **反序 FAECO 终态** 6／6、2 接受。相同单门首达 0.08748 µm² @152.288565333 RAW s，同两门最优 0.14580 µm² @222.660176836 RAW s。重复请求 2、4 仍为 FF setup 拒，两次候选 ODB、DEF、网表与正序对应逐项同哈希，正反序最优端点的三份工件也相同。反序在线固定已派请求。
- **反序在线固定终态** 6／6、2 接受。首达 0.17496 µm² @152.066594903 RAW s，四门最优 0.23328 µm² @221.946674999 RAW s。正反序墙钟首达方向未能在在线固定与 FAECO 间重复，FAECO 窗内最优面积两轮均较低。最后单门反序已派。
- **六臂原结果** 反序单门首达 0.08748 µm² @151.161324416 RAW s，最优 0.17496 µm² @198.260869548 RAW s。六臂均完整判定 6 次、接受 2 次、停在请求上限；候选 DRT／独立 DRC／逐角 STA／SEC 合计 36／36／108／12。两序合格最大面积为单门 0.17496、固定 0.23328、FAECO 0.14580 µm²。共同目标首达的六个观察值均在 151.161–152.778 RAW s，各方法的时间差方向跨序不稳定。矩阵原结果 SHA-256 `1bc709c4a2429e2ed0276a0c37f4c0b2ba0e830cb8ea0350371c3e82ee843da8`，完整独立核验另计。[实验报告](tcad_holdout_20261123/UART_ONLINE_REPORT.md)
- **独立核验** v2 原结果完整检查 6／6 臂，原件与仓库验收收据 SHA-256 同为 `51dbf9eb4ed0c950717d88350d179a71c5d343672c2abe9ebbc55c6fed3a5777`。三法最优端点的最大逐角 setup WNS 损失为 0.0428／1.3380／0.0251 ps，SS TNS 相对起点 +0.565／+10.113／−0.332 ps（单门／固定／FAECO）。全过原门、独立 DRC 与天线为零、SEC 567/0。36 次在线诊断无 marker、无额外邻网释放及重试。FAECO 正反序各重复一次 FF setup 失败动作，含诊断分别耗 23.221／23.318 RAW s。[独立核验](tcad_holdout_20261123/UART_ONLINE_VERIFIED.json)
- **已验收前缀的探索性阈值扫描** 保留预登记 0.01% 主终点。0.10% 的六臂首达读数与主终点一致；0.15% 时固定／单门／FAECO 的正反首达为 152.778／152.067、199.708／198.261、222.513／222.660 RAW s。0.20% 仅固定和单门达到，0.25% 仅固定达到，0.30% 六臂均未达到。使用同一批原有验收前缀，候选重评次数为零。[阈值读数](tcad_holdout_20261123/UART_ONLINE_REPORT.md)

### 2026-11-25 TCAD-ASAP7-UART-EXACT-CUMULATIVE-TRIAL-DEDUPLICATION

- 正序实物证实被拒完整批拆分后可在累计接受部分时恢复原失败动作集合。单独评估 opt-in 去重，限同一臂、同一冻结起点和评价配置下已取得完整物理结果和判定的累计动作身份。复用既有判定后继续真实二分，重复事件与六次真实评估配额分列。保留原六臂配置与实际轨迹，正式规约、源码和回归收据待记录。[问题 OI-106](../OPEN_ISSUES.md)
- **隔离原型与离线回放** 旧结构回归先因未知 opt-in 参数失败，补回调后 scratch 隔离模块的 adapter 专项 14／14。已验证默认行为精确重放 UART 两序真实轨迹。启用去重后分别跳过一次相同三门拒收，剩余第 6 次实际请求拟派 `_0703_`／`_0814_`／`_1027_`，按单元面积预计最多 0.20412 µm²，低于原固定批次 0.23328 µm²。新候选实物次数为零，当前 AES 绑源码保持同一字节。
- **实物配对预登记** 基线 `6a79448b`。在同机串行跑原 FAECO→去重 FAECO→去重 FAECO→原 FAECO，各臂从同一 ASAP7 UART 冻结布线起点及原顺序 18 候选开始，共计筛选 81.563830427 RAW s，硬窗 720 RAW s、最多六次实际物理评估。复用仅限同一臂已完整判定、采用同一冻结配置的累计动作身份，重复事件单列并继续二分；每臂重新执行实际物理工作。
- **预设验收与读数** 保留 270 ps 周期、原 I/O、虚拟延迟和三角，setup WNS 损失各限 2.7 ps，TNS 损失限 FF／TT 27、SS 136.973650200 ps，绝对 hold 非负、相对容差 0.001 ps，并用原电气、独立 DRC／天线与非空候选 SEC。核对第六次真实请求是否新触及此前拟派的三门、是否过全门，并与原在线固定四门最佳 0.23328 µm² 比较。共同 0.01% 首达和双时间读数一并保留，固定为既有独立结果。本轮只更新中文主稿。[原 UART 六臂](tcad_holdout_20261123/UART_ONLINE_REPORT.md)
- **实际启动** 09:01:38（UTC+8）启动外层 PID 357，09:01:39 驱动 PID 453，CPU 0–5、外限 3,250 s。输出 `/home/toylog/faeco_tcad_uart_dedup_20261125_v1`，实发协议 SHA-256 `0fd3ac354e11f2c35e9b700bd22a182db45c9362a6086a8bc8a930e946c269cd`，继承原 protocol `90bf70bb080d5544d51265e575c3ec94ff72f6342fe6b9aaf452c5476d374a4f`。驱动 SHA-256 `1e66deba125c18f8129f67906f25e47c31cb571d2eb7466b983af76a43f5bb5e`，scheduler `50a5ff8a29d2e6735e821fe183cb90b02293e4dd7cb1e05e46bb64b4cc99e53f`。实作复用范围限同一臂内、三角物理时序和独立 DRC 齐备、仅 setup WNS/TNS 门失败的同累计动作，拒收收据单列。strict-zero 初始物理已开。
- **strict-zero 与第一原调度前缀** 共用零动作真实验证 19.504175927 RAW s，收据 SHA-256 `3bc9c1f701d5630f7aa803e638467ac4bef23678fb23c46d035cb649641f9f46`，自 SEC 567/0。第一原调度第 1 次仅 SS hold 相对拒、第 2 次仅 FF setup 拒。第 3 次同单门 `_1027_` @163.279714784 RAW s 验收 0.08748 µm²；第 4 次已派同第 2 次累计三门。
- **第一原调度终态** 6 次完整物理、2 次接受，第 6 次最佳 0.14580 µm² @241.557577710 RAW s。第 2、4、5 次仅 FF setup 拒，重复的 2、4 同累计三门。最优 ODB 同原六臂 FAECO 正序，下一个去重臂已开始。原臂汇总 SHA-256 `24edd5ec0f70a60f2f38be2804f9f7ae3b89709c62ac261a44b882bb13a71a41`。
- **第一去重实物终态** 同累计三门只复用第 2 次 FF setup 拒收一次，原拒收 SHA-256 `b444f9034ffa71ddcb70d09468a7fcb8e709449b73935fbfde59d870f0d80282`。第 5 次 @217.410712512 RAW s 取得原最优 0.14580 µm²；第 6 次新组合 `_0703_`／`_0814_`／`_1027_` @245.368758120 RAW s 联合验收，回收 0.20412 µm²，多 0.05832，仍比原固定少 0.02916 µm²。新结果 SHA-256 `f328b678fa3f425953cecae88d4ff1ea3b30e02a54b8d1cc9c50fbf4ad61a347`，母臂 6 次真实物理、3 次接受。第二去重已启动。
- **第二去重终态** 同样跳过一次失败三门并完成六次真实物理。第 5 次 @219.256187936 RAW s 得同两门 0.14580 µm²；第 6 次 @246.745303355 RAW s 过门获 0.20412 µm²，实际 ODB／DEF／网表与第一去重逐项同 SHA。新第 6 次结果 SHA-256 `f3736d3ccbb0926e84c46abf4786a9a4c16051481e296ac78a8e7954871b63e7`。最后原调度开始。
- **四臂正式原结果** 正反序原调度第 6 次 0.14580 µm² @241.557577710／242.760525959 RAW s，去重第 5 次 0.14580 µm² @217.410712512／219.256187936 RAW s，四个同两门 ODB 同 SHA。去重第 6 次在两个顺序均增至 0.20412 µm²。预设 0.01% 的四臂首达都在第 3 次。24 次真实候选全部完成，候选预览／DRT/RCX／独立 DRC／逐角 STA／SEC 实际程序正常结束分别 24／24／24／72／10。结果 SHA-256 `df7ce868a4c88cb43c3f55667b424f7d254ed49c77657d6929f7c6769c227f54`。独立核验另记。
- **四臂独立验收** Linux 和仓库收据 SHA-256 均为 `c0af811ee40ae845eec0cd67f4f59791484e9c3f208dbb0caee5bdab5177aff9`。实查四臂请求均为 6，接受次数原／去重／去重／原为 2／3／3／2，复用次数 0／1／1／0，最大合格回收 0.14580／0.20412／0.20412／0.14580 µm²。各调度跨序物理身份一致，原 1／2／3／5／6 与去重 1–5 逐项同 ODB／DEF／网表／去日期 SPEF／时序。去重事件在第 3、4 次间，收据来自本臂第 2 次。新增三门跨序复现，仍比既有固定四门少 0.02916 µm²。[复跑报告](tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md) · [独立核验](tcad_holdout_20261123/UART_REJECTION_DEDUP_VERIFIED.json)
- **原件归档** `scratch/tcad_ibex_20261123/uart_dedup_20261125_v1.tar.gz`，tar 比较通过、实读 1,061 项、29,925,015 字节，SHA-256 `d4596b4327a29d46cc50d085b01c45c1b9eb26efb491218fdc689a28f74eba77`。

### 2026-11-25 TCAD-ASAP7-UART-DIRECTED-COMBINATION-0886（意图登记）

- 基线 `6a79448b`，复用 UART 原冻结起点、同一在线物理后端及原 I/O、三角时序、电气、独立 DRC、天线与 SEC 门。在曾已验收的原 FAECO 累计两门 `_0814_`／`_1027_` 上，验证再加入 `_0886_`。原单门轨迹的 `_0886_`／`_1027_` 已过全部门，累计三门此前未做实际物理验收。
- 按功能单元差预计三门共回收 0.23328 µm²，等于上轮固定四门的已验收结果。只派一次事后定向提议，从同一冻结点重新完整测量。实际是否过原门及是否达到预计面积待验证。此次读数衡量同一候选的联合物理可行性及累计面积，调度策略归因另做预设配对。[历史三法](tcad_holdout_20261123/UART_ONLINE_REPORT.md) · [去重四臂](tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)
- **实发规约** 09:33:29（UTC+8）外层 PID 342、驱动 422，CPU 0–5、外超时 900 s。输出 `/home/toylog/faeco_tcad_uart_fixed_area_probe_20261125_v1`，实发协议 SHA-256 `9d7ab4dce7276f3f405c1385d154dfd24f33b8926be89d85331056f0e795d627`，驱动 `e87a7272f80bd2962596f76a5654e6c9929602cb9e1ebde40f0b6c5412b147d7`。绑定去重四臂原规约及独立核验，使用相同筛选费／720 RAW s，最多 1 个实际定向请求。三门替换依次为 AND2x2、NOR3xp33、NOR3xp33 RVT；strict-zero 已开。 [固定面积诊断入口](tcad_holdout_20261123/probe_uart_fixed_area.py)
- **实际定向结果** strict-zero 19.799210421 RAW s、自 SEC 567/0，收据 SHA-256 `59e443d8d15840628133876778ef5808de699e5e7da3cd43aa49f55960b535e1`。单一累计三门在线诊断 0 marker、0 邻网，一次 DRT/RCX 及正式三角、独立 DRC／天线 0，SEC 567/0，回收 0.23328 µm²。最差 setup WNS 损失 0.042272 ps，无新增负 setup，三角 hold 门合格。实物含筛选用时 111.674214935 RAW s，摘要 SHA-256 `6a1bb7542bb14ff598a3d910b876858f51a0b4854ea017958fed7f95a08cab1c`、逻辑结果 `f8def585c4d7ff834e345cf5d69357ceb8906135ba3c15bdc18904c58c93772c`。事后定向达到既有固定面积，等预算自动调度仍由已核配对衡量。
- **独立物理核验** 读取三门的实收、三角时序、保护路由、诊断、端点身份及证明。工作树核验 SHA-256 `3619d8aab89b37fecfbbf33f19b2fd12941a920f2818cc30e6dfe568554495ac`。[核验收据](tcad_holdout_20261123/UART_FIXED_AREA_PROBE_VERIFIED.json)

### 2026-11-25 TCAD-SKY130HD-AES-ONLINE-SENSITIVITY-SINGLE-COMPARISON

- 基线 `c8b9e0fd`，在先前在线诊断比较的 SKY130HD AES 中引入灵敏度排序单门作为强基线。延续共享筛选池、原 I/O／三角时序、同一物理后端与联合验收，按共同墙钟与面积目标报告，实付排序成本单列。计划与 UART 正式实物测试串行。实际排序来源、计费、窗口、运行顺序和配置收据待登记。[既有对照](tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md)
- **排序预检** 在冻结 CONTROL、原 SDC／SPEF 与 TT Liberty 上查询 18 个实例的输出最小 setup slack。候选相对 TT WNS 的裕量为 297.415–515.914 ps，历史公式 200 ps 截顶使全部饱和，复现原清单顺序。正式预设保留其它排序条件、去掉截顶，前六重排，预检端到端 3.454 RAW s，独立读回 18 条。每轮单门的新查询拟在 720 RAW s 内实付，所有臂计相同历史筛选 113.363032440 s，原 36 ps WNS 限、6 次请求及 0.01% 面积首达阈值沿用。预检正式物理候选 0。[排序与实跑规约](tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_PREFLIGHT.md)

- **实际启动** UART 六臂完整结束后，07:26:25（UTC+8）单机串行启动，`taskset -c 0-5` 及外限 3,100 s，输出 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_online_sensitivity_greedy_20261125_v1`。协议 SHA-256 `197e0a4c6b796570e9ffbff8cb888b8d8b87d693110471824e39a9b2ce16ba3f`，驱动 `26c1ede54b2aeb228c00bb43a871c0f5e08b4f4edff4dd3feaa8800007f58df5`。正序灵敏度单门→FAECO、完全反序。单门每臂实际重做且计费 TT 去顶查询，命令限 40 s。正序单门实发配置 SHA-256 `28e1ccc45e31d27946224c70340524601c295aa8de839ad2437d802acb6309bc`，实发顺序 `1bd07df9ff7d5f0679f46968a19f09be4543ce2692af6e5c362b636cfd6177ce`。首请求为 `_20893_→sky130_fd_sc_hd__xor2_2`。
- **正序灵敏度单门开局** `_20893_` @230.643614817 RAW s 仅 SS 相对 hold 拒，结果 SHA-256 `577aa6c4618a2c068b5cad74cc5c1c7990f51def3ce79f77d59139c61b7ae507`。第 2 次 `_12777_` @359.313133099 RAW s 通过，回收 11.2608 µm²，小于 0.01% 下限 11.65079904 µm²，结果 `ba1f94f303340af2e9ef8a60f4b969c51f5b5a41c27738329add11907f6db69a`。第 3 次累计追加 `_10992_`。
- **正序灵敏度单门首达** 第 3 次累计 `_10992_`、`_12777_` @489.514774208 RAW s 回收 22.5216 µm²。完整结果 SHA-256 `0f40f268e411c26519afd9a04cbf8c224711f51558d3f13ad85482fa47950152`，新 SEC 正常返回，实际耗 15.637115457 s。第 4 次累计追加 `_11724_`。
- **正序灵敏度单门第三次提交** 第 4 次追加 `_11724_` 验收累计三门 33.7824 µm² @619.296298275 RAW s。完整结果 SHA-256 `5dbcda530a767f9dfd877c5c54e35cbacb14871e221032601830a0ba13d0475f`。第 5 次追加 `_20897_`，只使用剩余墙钟。
- **正序灵敏度单门终态** 派发 5、完成 4、接受 3，首达 489.514774208 RAW s，最优 33.7824 µm²。真实 TT 评分查询 3.460456136 s，另与 15 次候选三角 STA 分列。第 5 次在独立 DRC 受硬墙钟裁剪，限 1.901146799 s，实际 1.781745034 s。汇总 SHA-256 `3f53c1687eed5e4491f90a3d266dc14b91377a8628c8e2a7c8d8866ee2542197`，正序 FAECO 实发配置 `7296b6892c82876ee1fc51adb19246ef465573fe2f126b0530b38a02d91ccc25`。
- **正序 FAECO 开局** 第 1 次原排序前三 @229.828592325 RAW s 只因 SS 相对 hold 拒。共同池触达排序实付 0.593106599 RAW s，反馈后第 2 次实派 `_13122_`／`_13645_`／`_20897_`。
- **正序共同阈值读数** FAECO 请求 2 因 FF／TT 相对 hold 拒，第三次 `_12777_`／`_20883_`／`_21033_` @472.397604600 RAW s 验收 33.7824 µm²，较配对灵敏度单门的 489.514774208 RAW s 早 17.117169609 s。两臂均第 3 次首达，各完成 3 DRT／在线诊断／独立 DRC、9 逐角 STA；SEC 1 对 2，合计 16.134596262 对 31.388546427 RAW s。第 4 次累计六门开始。
- **正序 FAECO 六门验收** 请求 4 @603.241523267 RAW s 完整验收 67.5648 µm²，结果 SHA-256 `0d041c153bbb8b7bf42fea5b9490747542b50ba5b0b7461ef3b9e2f488326f6d`。第 5 次累计九门进入剩余硬窗。
- **正序 FAECO 硬窗终态** 5 派发／4 完成／2 接受，最佳 67.5648 µm²。九门完成 DRT 和三角 STA，独立 DRC 获 14.473175206 s、实跑 13.501614730 s 后截停，SEC 未启动。汇总 SHA-256 `1178df7247ddd39b4cbfd631cdc56db32711f2bbbe2b1d60c203b969d9bd22a2`，反序 FAECO 实发配置 `faf0c988b919d10d9c72ca4c74f0a4110666e593938531f89bac17b85dd0bd22`。
- **反序 FAECO 开局** 触达排序 0.587397786 RAW s，前三动作 @228.734993463 仅 SS 相对 hold 拒，重排第 2 次 @345.510226554 触发 FF／TT 相对 hold，与正序候选和拒因相同。第 3 次同组三门已派。
- **反序 FAECO 首达** 第 3 次 @477.342231847 RAW s 获同三门 33.7824 µm²，ODB、DEF、网表与正序同哈希。结果 SHA-256 `88e2ff975365ea032917783debfe44403d525c8df704bf78c13965af14c703b5`，第 4 次累计六门已派。
- **反序 FAECO 六门验收** 第 4 次 @611.372262678 RAW s 得 67.5648 µm²。结果 SHA-256 `4fa85dab13ce2d8a47ee63a441499cf56f43ab509944ccb95e86875e234a50a2`，主要三份物理对象同正序。第 5 次按余窗评估九门。
- **反序 FAECO 终态** 5 派发／4 完成，九门在独立 DRC 截停，获限 5.125442696 s、实跑 4.789670612 s，SEC 未启动。汇总 SHA-256 `94cb7d5b3e54a79f849a84e61c0a4b0fa85739683d5d23a50a6c7eb7afb27c43`。最后一臂灵敏度单门配置 `8edadc2c3b2f7a4c857143af680127bc3ac04bc743c51da66b26640298c82f6c`，实付重测的排序哈希同正序。
- **反序灵敏度单门开局** TT 排序实付 3.441389107 s。第 1 次 `_20893_` @231.355045073 RAW s 仅因 SS 相对 hold 拒；第 2 次 `_12777_` @364.648946171 RAW s 累计 11.2608 µm²，首达门尚差 0.38999904 µm²；第 3 次累计追加 `_10992_`。
- **反序共同阈值读数** 灵敏度单门第 3 次同两门 @497.492773503 RAW s 验收 22.5216 µm²，较配对 FAECO 的 477.342231847 RAW s 晚 20.150541656 s。两序单门首达 ODB、DEF、网表分别同哈希。首达前仍各 3 DRT／诊断／独立 DRC 和 9 候选逐角 STA，FAECO 的 SEC 16.010559663 s 对单门两次合计 32.647645333 s。第 4 次累计追加 `_11724_`。
- **四臂终态原件** 反序灵敏度单门第 4 次同三门 @629.378279059 RAW s 验收 33.7824 µm²，与正序最优 ODB、DEF、网表同哈希，第 5 次在 DRT 截停。各臂均 5 派发／4 完成。合计子进程启／正常返分别为排序 2／2、诊断 20／20、DRT/RCX 20／19、独立 DRC 19／16、候选逐角 STA 57／57、SEC 10／10。四臂实际结果 SHA-256 `ef8eb40c7281517dc71839ff624719519a42efffba486ad917f6f1abd74415a6`，待完整独立核验。
- **四臂独立验收** `audited_cells=4`、`full_audit=true`，原件 SHA-256 `b88974f78e6c9b0695f075384eaf54b6e2227bf639bdfac5b72acbf02efb2179`。0.01% 共同下限 FAECO 早 17.117／20.151 RAW s，按同批验收前缀重读 33.7824 µm² 时早 146.899／152.036 RAW s。窗内最佳 FAECO 67.5648，灵敏度单门 33.7824 µm²，跨序各自端点复现。单门与 FAECO 最优的新增 SS 负 setup 数 1／0、SS TNS 变化 −228.511／−192.358 ps、最大 setup WNS 损失 0.127／0.086 ps，均满足同一验收门及 SEC 11089/0。[正式报告](tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_REPORT.md) · [独立核验](tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_VERIFIED.json)


### 2026-11-25 TCAD-SKY130HD-GCD-SAME-PROPOSAL-ONLINE-MARKER-MECHANISM

- 沿用 `gcd_incident_cap_pair_20261124_v1` 的已布线嵌入导引起点和筛选 39.206442669 RAW s。原 1100 ps 周期、220 ps I/O、290 ps 虚拟时钟延迟，原三角 WNS 限 11 ps 和完整验收。固定原排名 13–15 的 `_092_`／`_093_`／`_094_` 三门，已静态核对 9 条直连网、486 条原有线网、两条时钟网，诊断及正式 Tcl 预检和两项专项测试通过。实物进程为零。
- 计划 strict-zero 后，常规→实时诊断→实时诊断→常规串行，每臂一个固定提议和 720 RAW s，实际计费并保留零回收、截停和验收。后续另做按冻结几何和同数量邻网放行对照。[静态预检与复现](tcad_ibex_20261123/GCD_MARKER_MECHANISM_PREFLIGHT.md)

- **实际启动与 strict-zero** 08:14:43（UTC+8），CPU 6–11、四线程详细布线、外限 3,100 s，正式输出 `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_marker_mechanism_20261125_v1`。规约 SHA-256 `be1e8b5e6aa0fe00554346f506d0fdd5bdf1a378402d4d8908822eddbbec4c6c`，正式实发含 10 条直连网。strict-zero @7.593986548 RAW s 过门，自 SEC 262/0，收据 `d8283e568ae4e07bd4d5248ecf3d10da072d075cdd395fbaeb7dcd5394ca9493`。已派第一常规臂的固定三门。

- **第一常规终态与在线开局** 常规初轮 DRT/RCX 285.860713565 RAW s，独立 DRC 3 个 met1 Short，均涉及 `net242`／`net266`。释放 `net242` 重布 DRT/RCX 6.599093636 s，独立 DRC 回到 0；TT 相对 hold WNS 退化 0.022620794 ps，在原门下正式拒收。第一次在线诊断 0 marker、0 邻网，正式初轮物理开始。

- **第一在线终态** 实时预览实耗 0.711514924 s，0 marker、0 放行。首次 DRT/RCX 351.433454082 s，初次 ODB 和独立 DRC 逐项同第一常规；放行同 `net242` 并实际重布，DRT/RCX 8.742110576 s，独立 DRC 零，末端仍由 TT 相对 hold 拒。第三臂在线诊断同样 0 marker、0 放行，初次物理开始。

- **第二在线终态** 实时预览 0.906880487 s，0 marker、0 释放。初次 DRT/RCX 394.898720177 s，独立 DRC 与前两臂同三个 met1 Short；同邻网重布 DRT/RCX 9.275954019 s，独立 DRC 零，并因同 TT 相对 hold 拒。初次和重布 ODB 分别同相应前两臂。最后常规已启动。

- **四臂原结果** 末臂常规初次 DRT/RCX 434.766476123 s、重布 9.013692381 s，仍 TT 相对 hold 拒。四臂各两次物理，分别复现同初次三处独立短路、同邻网放行和重布后零 DRC。4 次逻辑完成，候选 DRT/RCX／独立 DRC／逐角 STA／SEC 为 8／8／24／0，面积均为零。原结果 SHA-256 `08eec7bdc16ba260d8cbb10afdf2db7f7129707c2617f8f58e640e81abb3849c`，待独立核验。

- **独立核验** `checked=4`，四臂均完成同固定提议并同为 TT 相对 hold 拒。Linux 原件与仓库收据实查 SHA-256 同为 `bf66317a21c06a2e1151208dd53f8f663a25dd532fed5ee312d12d05899232e5`。[独立核验](tcad_ibex_20261123/GCD_MARKER_MECHANISM_VERIFIED.json)

- **正式结果报告** 两次在线实测预诊断分别 0.714895403／0.910451249 RAW s，四次首轮布线 285.861–434.766 s。初次与重布两个阶段各自跨臂同 ODB、DEF、网表、去日期 SPEF 和三角 STA。正式报告保留零结果及保护配置差异。[正式报告](tcad_ibex_20261123/GCD_MARKER_MECHANISM_REPORT.md)


### 2026-11-25 TCAD-ASAP7-UART-RESERVED-SS-VERILOG-SPEF-ATTRIBUTION

- 计划在完整六臂计时结束后串行做独立 SS hold 归因。共用原 SDC、同一 SS RVT Liberty 和已验收的 `_0814_`／`_1027_` 两门端点，对照本轮预留被拒 `_0562_` 累计三门与先前定向已验收 `_0886_` 累计三门的网表和 SPEF。固定寄生比较两套候选网表，并按实际提取对照，核查便宜指标能否区分原有 SS 相对 hold 接受／拒收，以及是否需要布线后的寄生反馈。
- 针对已观察的失败做诊断，保持原门和同一候选身份，STA 次数及耗时单列；正式六臂的结果与计时独立保留。不同网表和寄生的混配只作归因探针，对未映射段和注释覆盖做核查。具体端点与原始读数待正式收据。
- **v1 工具呈现差异及 v2 修正** v1 的第一组 STA 成功，扩展路径文本 54.060298920 ps 相对工具标量 54.060297905 ps 有 1.015×10⁻⁶ ps 浮点呈现差，超原文本校对的 10⁻⁶ ps。保留 v1 原件；v2 单独设路径文本匹配差容差 2×10⁻⁵ ps，真实标量复现容差和原实验 hold 门继续沿用。v1 protocol SHA-256 `143bf53572cd86c7da67f17c5cbff638cea32e988e762c7703ea4f0b6eeaf172`。
- **v2 七组结果** `/home/toylog/faeco_tcad_uart_hold_exchange_20261125_v2`，协议 SHA-256 `3440fb0fdd7ae228f134516ca3c19c756c3640ec8777a3de84cbca23397915fd`，七次 SS STA 均 rc0，合计 10.871989892 RAW s，DRT/RCX 和候选 SEC 为 0。原相对 SS hold 下限 54.05191492177611 ps。两门实配 54.060297904889865 ps，`_0562_` 实配 54.044491104576764 ps，`_0886_` 实配 54.0617828281853 ps。两候选只换网表 Δ0，只换提取 SPEF 精确复现实配，交互项 0。统一最差 min 路径为 `rxd` → `uart_rx_inst.rxd_reg$_SDFF_PP1_`，未注释驱动 12、部分注释 0 在七组一致。原件与仓库 JSON SHA-256 `af510ca36f2224d9eefbbeda63a8f5e055ba5427e017cf598c65b6d13b4ca38a`。[诊断收据](tcad_holdout_20261123/UART_HOLD_EXCHANGE_RESULTS.json)

### 2026-11-25 TCAD-ASAP7-UART-LAST-TRIAL-RESERVE-SCHEDULE-ABBA（意图登记）

- 基线 `5033cb53`。计划串行现行去重 FAECO、末次预留 FAECO、在线固定批次，随后完全反序，共六臂。共同冻结 UART CONTROL 与 18 动作有序池，计筛 81.563830427 RAW s、硬窗 720 RAW s、各六次实际评估、三门常规批宽及 0.01% 首达下限。沿用 270 ps 原约束与完整三角 setup／hold、电气、独立 DRC／天线、非空 SEC 验收。应在新固定臂实查原 0.23328 µm² 的可复现性。
- 最后一次真实评估优先从曾因相对 hold 被拒并暂缓的批次挑一个动作，限该动作未单独物理评价、累积组合身份为新。预估面积下降量与既有单位电容优先级按降序，冻结池原顺序为最终同分规则。先跑专项回归，此后正式比较保留实际时间、合格面积、派发、裁剪及每臂物理账。事后动机来自已观察 UART 定向诊断，限定为开发设计上的预设规则复跑。此轮实验优先。[现行去重](tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md) · [定向证据](tcad_holdout_20261123/UART_FIXED_AREA_PROBE_VERIFIED.json)

- **实际启动与严格零动作** 09:54:08（UTC+8），外层 PID 353、驱动 447、CPU 0–5、外限 4,650 s。输出 `/home/toylog/faeco_tcad_uart_deferred_reservation_20261125_v1`，协议 SHA-256 `36ce1a17c92f30858fade7482d60711f918b54bf3592e524ef02fcf10626cc44`。驱动 `cf3d7b5b25adea2f2f8cfe74738933eb685cdcb2f2495f756fd7123e9a8894f2`，调度源 `c7569beadcde9ea3ceb589c09867ce900c1344e2e5c5bfaa388ff7fed18bf010`，实发序列去重、预留、固定、固定、预留、去重。strict-zero 实耗 19.623321149 RAW s，自 SEC 567/0，收据 SHA-256 `65b3df02bd60f3fcd7d99473f78162d8e40ebae1da6aea3004d276ea3a1443a2`。正序去重开始。

- **开跑前专项回归** 新策略用例于旧参数签名下先红；改动后 adapter 专项 15／15。第六次真实请求才作预留判断，排除已累计、按单门已实测及完整累计组合已测的动作。无合格候选时沿原派发。正式独验重放真实请求与预留事件。

- **正序现行去重终态** 6 实评／6 完成、3 接受，0.01% 首达 166.207665062 RAW s，第 5 次得 0.14580 µm²、第 6 次 @251.964863688 RAW s 达 0.20412 µm²。最优 ODB 与上一轮去重同一。汇总 SHA-256 `20747f05d7bcf9a3af76f2236f702dedceb7139d1f0f0f483d71c0cc2db267d1`，正序预留已开始。

- **正序预留终态** 第 6 次真实预留 `_0562_`，累计 `_0814_`／`_1027_`。优先因三项面积同分而单位电容排序更高。组合物理面积可减 0.23328 µm²，SS 相对 hold 损失 0.008423817 ps 超 0.001 ps 门，最终拒收。6 实评／6 完成、2 接受，最大合格 0.14580 µm²。第六实际结果 SHA-256 `8949aec7a13672d3a1640619ee9ce2ee74a16ed7a402a4a5d81446aeb75c08bf`。正序固定已开始。

- **正序固定终态** 6／6、2 接受，首达 @167.546273113 RAW s 获三门 0.17496 µm²，第 6 次 @252.520388223 RAW s 过门获四门 0.23328 µm²，最优 ODB 同已有固定臂。汇总 SHA-256 `6b83ecc3b10adafd2ed17e299314ecbb9cbb46be025785c1f21a7ca11b823511`。反序固定已开始。

- **反序固定终态** 全六次物理完成，两次接受。三门首达 @166.233043192 RAW s，四门 0.23328 µm² @249.993039804 RAW s，以同 ODB 复现正序和以前固定端点。汇总 `1f46507e54991455574761026241e8c8d6379ab55cd3abec71d43276587b2805`，反序预留已开。

- **反序预留终态** 完成六次实际物理、接受两次，第 5 次 @222.367810217 RAW s 合格面积 0.14580 µm²。第 6 次仍为 `_0562_`／`_0814_`／`_1027_`，物理面积差 0.23328 µm²、SS 相对 hold 损失 0.008423817 ps，唯一拒因复现，拒收 ODB 与正序相同。最后去重已开。

- **六臂原结果** 反序现行去重 6／6／3，166.051875559 RAW s 首达，第 6 次 @250.070577155 RAW s 回收 0.20412 µm²。全六臂均完成六次真实评价；在线诊断／DRT/RCX／独立 DRC／逐角 STA／SEC 顺次正常返回 36／36／36／108／14 次。两序固定 0.23328＞去重 0.20412＞预留 0.14580 µm²。预设首达均为第 3 次，范围 165.392–167.546 RAW s。原总结果 SHA-256 `7fe225fde20e2df12ce65c2d0f5492f3398141bd7e7d51e26f6f6c10412e0c72`，待独立核验。

- **独立核验完成** 实读六臂核验收据 SHA-256 `fef8a92de178140bbf00f330834743c799c56ae9d2f50618998396a2773f82fd`，两序最大合格面积复现，末次预留均在第 6 次实际评估选相同动作并被相同 SS hold 门拒收。[正式报告](tcad_holdout_20261123/UART_DEFERRED_RESERVATION_REPORT.md)

- **原件归档** `scratch/tcad_ibex_20261123/uart_reservation_20261125_v1.tar.gz`，实读 1,595 项、44,191,625 字节，SHA-256 `b2dae97e343ef78363eb688f7197963d68ccb3b5dcf0da1f51f1297d4d3db14d`。tar 与原件比较 rc0，含六臂正式运行、SS v1 停止原件和 v2 完整七组。[正式结果核验](tcad_holdout_20261123/UART_DEFERRED_RESERVATION_VERIFIED.json) · [SS 专项原件摘要](tcad_holdout_20261123/UART_HOLD_EXCHANGE_RESULTS.json)


### 2026-11-25 TCAD-ASAP7-UART-PRE-DISPATCH-GEOMETRY-DISCRIMINATION（事前登记）

- 基线 `7b1ca348`，使用已冻结正反序派发之前可获得的原始物理几何和先前合格路径。待核各特征的输入身份、缺失与可计算覆盖、风险方向及 AUC。候选正式布线产生的独立拒收/合格标签和物理签名用于审计与去重。保留阶段、实际窗口及各端点 provenance。
- 开发检验的入围条件包括同时区分同两门追加 `_0562_` 的已知 SS 相对 hold 拒收和追加 `_0886_` 的已知通过，且在其他可比较候选上有方向一致性。符合条件再冻结规则供独立对象验证。默认调度与论文保持既有版本，具体规约、用时及结果另记。[六臂核验](tcad_holdout_20261123/UART_DEFERRED_RESERVATION_VERIFIED.json) · [七组 SS 交换](tcad_holdout_20261123/UART_HOLD_EXCHANGE_RESULTS.json)

- **详细规约冻结** 输入用原 DEF／Liberty／SDC，以及同起点零编辑 FF／TT／SS 每组四条最小路径；末次补用事前已验收两门路径。主项在拟重布直连信号网和时钟路径网同层平行重叠时，以三轨间距内的“重叠长／轨距 ÷（1＋间距／轨距）”逐段累计，取路径最大值；全路径、仅数据路径为机制对照，原直连电容为基线。正式 UART 三批去重、定向非正式证据另列，分别读取 SS 与其它角 hold 标签。门为关键次序正确、全体 SS AUC ≥0.65、剔除两已知应力点后 SS AUC >0.50 且至少三正三负。

- **UART v1 已读取** 协议 `8e362c128fe1c380a0b526d96e60e6e16b2f364ce5499a028305761dee3ac6c5`、先冻结的评分 `ab175ba706ca510fa94db19e200e1169e89564897bc6e29b0f8664344c4141ac`、结果 SHA-256 `20ee3974ee4f9ad54b88628cd03b2ea652ba35246e869b4eb2f2d01b26240992`。六次事前 STA 耗 7.941024849 RAW s、每视图八条路径，18 门的 54 条直连网有几何。96 正式实布与 1 定向合并为 18 正式、19 合计，无缺视图。正式 SS 8 拒 10 过，主 AUC 0.9125、全路径 0.875、数据 0.900、直连电容 0.7625。参考两门下 `_0562_` 主分 0.8325779863、`_0886_` 为 0。去掉已知对照后正式 7 拒 10 过，主 AUC 0.9142857。开发诊断入围，异设计独立核验和自动收益另计。

- **只读末次重放** 按原候选资格，两序均有三项等预估面积 0.08748 µm²。面积后接电容选出的 `_0562_` 与实跑同，面积后接几何选 `_0886_`（0；既有定向验收），其余 `_0562_` 0.8325779863（正式拒收）、`_0601_` 3.268820862（同前缀无物理标签）。同宽度下单门几何／电容为 4/4／3/4，三门为 12/12／10/12，其它宽度无跨类对。末次只读重放 SHA-256 `18ee4b7142ece70f349fffbfaed3dacb27eae8d93efb490582f0a59f6e6b8383`，新物理评估 0。
- **UART 原件封存** `scratch/tcad_ibex_20261123/uart_hold_geometry_20261125_v1.tar.gz`，实读 19 项、48,070 字节，SHA-256 `bdbc52222882d301e2766c57b09735dcff51475212577c3ab42ea98f9f21ff6a`。正式工作树的评分、标签合并及末次重放见报告索引。[几何开发报告](tcad_holdout_20261123/UART_HOLD_GEOMETRY_REPORT.md)


### 2026-11-25 TCAD-SKY130HD-GCD-PRE-DISPATCH-GEOMETRY-TRANSFER（历史物理对照）

- 冻结 UART 几何公式转移到 GCD 历史触达电容对照，12 个同流程已实布记录合并为 9 个独立物理身份，TT／SS 各 6 拒 3 过。三次参考 STA 耗约 2.524520 RAW s，新候选 STA／DRT 为 0。协议 `4699d8d92090f065dbe7e31f81d47552a774e1127c9f3153777f1aeacc269e2d`、评分 `8527489b14ffab64e14cb975edd7f64861e48d69d8a597ed322213075dde93f7`、结果 SHA-256 `77b0a6812bd6634139b9f97a1f96149259e845c2cec2157e1bfe23b36deff400`。
- 主几何 AUC 0.75（9 对方向正确、9 对同分、0 对反向），电容 0.5556。零几何分同时包含 3 拒和 3 过。等面积同宽度的 `_089_/_090_/_091_` 拒与 `_089_/_090_/_093_` 过在主几何、全路径与数据路径上均同分，电容有正确次序。暂缓独立在线比较，待同分风险和可部署基线进一步核验。 [历史 GCD 原配对](tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)

- **几何同分电容回退复查** GCD 全池 TT／SS AUC 0.7500→0.7222，九个几何同分打破后 4 对正确、5 对反向。GCD 等面积五对几何、电容、组合各 0.70／0.80／0.80；UART SS 等面积十对三者均 0.70。以既有分值与标签计算，未增加物理试探。原 `gcd_hold_geometry_tie_20261125_v1/score_tiebreak.json` SHA-256 `3ba74df1fc2166b4c6205943052c8c42f091d29bc3394525b3e51f609afa3c33`。

### 2026-11-25 TCAD-SKY130HD-GCD-TT-SS-HOLD-ACTION-SPEF-EXCHANGE（意图登记）

- 使用历史同一后端的两支实配端点。两者共同动作 `_089_`、`_090_`，追加 `_091_` 已因 TT／SS hold 拒、追加 `_093_` 已过，物理面积均 11.2608 µm²。保持原 SDC 和 TT／SS 各自 Liberty，每角实跑两组原 V／SPEF 和两个双向混配，共计划 8 次 STA，候选 DRT／RCX／SEC 为 0。
- 逐角读回原配标量复现、最差 min 路径、寄生注释数量和分量；不同 V／SPEF 的混配限物理归因。新派发规则和正式收益另计。[历史原对照](tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)

- **实际交换结果** 输出 `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_hold_geometry_tie_20261125_v1`，协议 `71bec9d783f23f119d349d99af52e257f45696e2c22702173be17b991c9cf7dc`，结果 `49a63d12615359ed8f11b53680022f0dc6007f4f5e2d68c840f83ec07277c0e0`。8 次 STA 合计 4.576997117 RAW s，DRT/RCX/SEC 均 0。TT／SS 实配拒对过的 WNS 差为 −0.497074604／−1.869893129 ps，只换 SPEF 精确重现，V 效应与交互均 0。各视图四组最差路径相同，八组注释计数均为未注释 5、部分注释 0。独立正式派发未启动。
- **GCD 原件封存与覆盖** 实查 `scratch/tcad_ibex_20261123/gcd_hold_geometry_20261125_v1.tar.gz`，含 GCD 冻结评分与交换原件 51 项、33,357 字节，SHA-256 `d9875c82b697bea8a6bd52cd3d2bec6e6c47c4ad80d10fdc760571f310f0a8ba`，tar 对原件比较 rc0。冻结转移 64 条触达网全覆盖，三角各 8 路径。等面积实配产生的 `clk`／`clknet_0_clk` 几何变化位于预计直连网输入范围外。GCD 评分、标签、交换和同分复查均在仓库逐项绑定原 SHA。[总报告](tcad_holdout_20261123/UART_HOLD_GEOMETRY_REPORT.md) · [GCD 交换结果](tcad_ibex_20261123/GCD_HOLD_GEOMETRY_EXCHANGE.json)


### 2026-11-25 TCAD-SKY130HD-GCD-BOUNDED-ROUTE-INCREMENTAL-RC-SCREEN（意图登记）

- 基线 `f91df069`，同历史已冻结 GCD、同两组等面积三门 `_089_/_090_/_091_`（原拒）和 `_089_/_090_/_093_`（原过）。以限域布线和增量寄生估计读取 TT/SS 原 SDC 下绝对与相对 hold。共享冻结起点和原门，正式接受仍以完整物理、时序与证明验收。
- 记录同机下真假候选的实际筛选费用和完整后端费用。预设 go 条件为 TT、SS 两角均正确区分两组，并且两份筛选加通过候选的一份完整验收所用墙钟小于对两组都完整验收。否则保留失败或代价并诊断，暂缓同预算派发比较。具体技术范围和资产哈希待冻结。[GCD 真实物理来源](tcad_ibex_20261123/GCD_HOLD_GEOMETRY_RESULTS.json)

- **历史完整后端参照** `screened/fixed/04.json` 拒收 10.884134710 RAW s（DRT/RCX 8.575996567，三角实际 STA，候选 SEC 未起）；`screened/faeco/05.json` 通过 12.219985378 RAW s（DRT/RCX 9.089512727，三角 STA，SEC 0.805111041）。合计 23.104120088 RAW s。源 CPU 6–11、4 线程、local、单次 pin access、嵌入导引、64 轮，OpenROAD 二进制 SHA `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。这组历史花费作为参照，新净成本门使用新比较。

- **细化规约冻结** 同历史 GCD ODB/guide/SDC 与库，CPU 6–11、4线程；两顺序 `_091_`→`_093_` 再反序。完整后端 64 轮 DRT、单 pin access、RCX、三角和正式证。预筛 A 为 dirty GRT 增量估计，配同估计法零编辑与原 RCX 底座校准；B 为外部 FIXED 的 2 轮 DRT，允许网是直连、冻结几何至多 20 条三轨内同或邻层近邻及 TT／SS 原最小路径时钟网，只清直连线。本机原生 RCX 无按网／按框入口，B 计实际全块耦合 RCX。失去路径注释、未布通、抽取中止及锁区几何改动均保留失败。[现场规约](tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)

- **v1 工具绑定修正与 v2 发出** v1 在 GCD TOP 绑定前解析 masters，默认 `ibex_core` 检查失败，实际 EDA 0。将解析移入既有 GCD 运行绑定后，v2 于 10:42:33（UTC+8）启动，CPU 6–11、外限 700 s。实发协议 `8b4f3caeef2733dc22fbc9179151592b45a50c37854b79de5cf34b02595683a3`。首轮零编辑 GRT 和两候选的原始估计同分，首轮限域 DRT 形成已读的 TT/SS 数据，正式对照另计。
- **v2 两序原结果** `_091_` 完整后端拒收 9.696863891／9.773684028 RAW s，`_093_` 完整后端过门 11.871181930／11.854773017 s，合计 21.568045821／21.628457045 s。dirty GRT 两候选原门 TT／SS 全判通过，按每种顺序计零编辑校准并加通过项完整验收为 16.650995534／16.481877340 s，标签错误。限域两轮 DRT 的 TT/SS 两候选均拒，合成相同计费为 30.117233470／29.949757805 s。原结果 SHA-256 `ed38b357f80149014dd60ede24434d307d05f6e6208fd38914363a29e5869e22`，两种预筛均未达到双门。


### 2026-11-25 TCAD-SKY130HD-GCD-EARLY-DRT-UNRESTRICTED-ABLATION

- 在已观察的首轮限域失败后，复用同一历史 GCD 冻结嵌入导引和原后端路由范围，诊断仅改变 DRT 结束轮次，预先固定 0、2 两值。对 `_091_` 与 `_093_` 两候选执行同一单轮比较，读回原 TT/SS、早停 DRC、时钟线变化、实际路由范围与 RAW 墙钟。按原门及既有完整实耗判断，限制端点与只改早停的结果分别登记。
- **实读结果** `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_hold_route_cutoff_20261125_v1`，规约 `8680c9de906dadaa1ec769a9ebdca58845d2ba55ea777ed97713c53fb89793a9`，结果 `4a82cb02991ab1252288fa3f8f65363a19dfdc4087fec1bb7f25045443f2c131`。两序共 8 组。0 轮候选原生 DRC 11／21，2 轮为 7／17，两个设置和限域 2 轮的各候选 TT／SS WNS 逐项相同，皆拒。两筛各序合计 0 轮 11.563057165／11.501283020 RAW s，2 轮 17.820620441／17.644273994 s，都大于相应可避免的完整拒收开销 9.696863891／9.773684028 s。


### 2026-11-25 TCAD-SKY130HD-GCD-TOUCHED-NET-GRT-DELTA-SPEF

- 以实际 dirty GRT 候选和零编辑产生的导引、路由估计为输入。在原冻结 SPEF 对应的直连网块施加候选对零编辑的 ΔC 与估计电阻比例，保留其他寄生和耦合。两候选各做 TT／SS 一次，原 SDC，原门，差量预测的构建和原有估计实耗均单列。该探针用于区分直连估计修正和全量 GRT 估计；正式各角 STA 和物理验收按原后端。
- **v1 输入域失败与 v2 构建** `_017_` 原 RCX 的 ground C 为 0.001609684 pF，GRT 估计总 C 从 0.00428110 变 0.00189957 pF，将估计总 C 差直接叠加会产生负 ground C，v1 在 EDA 启动前退出。v2 使用候选／零编辑 GRT 估计 C 和 R 比值缩放原 SPEF 的候选直接网 ground C 和电阻，耦合保留。v1 protocol `a0ea4ea2f027e0b9491a22478cb95b8ee5e2b071b4ec7b343acb21748ec1e4b`。
- **v2 原结果** `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_incremental_hold_rc_20261125_v2`，协议 `7dc081f10106dc121961948981057c1ff9b1e2ea34b5aba2015bf6a6b7ca03e6`，结果 `34190097904b8858adb3ab609f1bbe69e7fc2412e9ba0dff0859badd21672fb9`。各变更 10 条直接网、无缺估计网，候选导引改 6／5 条，均无时钟网。四次 TT/SS STA 返回 0。两候选均得到与原参考相同 TT／SS hold 430.726704304／342.905315254 ps，误收历史与新鲜完整均拒的 `_091_`。既有 GRT 完成后的增量构建和 STA 附加 1.312271761／1.108678603 RAW s，GRT、校准费用仍需计入完整路径。

- **阶段归档与关闭判定** `scratch/tcad_ibex_20261123/gcd_local_hold_preview_20261125_v2.tar.gz` 390 项、20,073,635 字节，SHA-256 `fd8cfd207442ae6476631f93299eeb584bc1dbbaeb3677fa2f25cdb280fc3a42`，tar 比较 rc0。包含主 v2 同机对照、裸早停、直连增量成功执行原件及两个 0 EDA 失败版本。正序 `_093_` 在 2 轮到完整后 `clk` 和 `clknet_0_clk` 总 C 分别 10.79950→9.91285 和 13.35230→13.09290 fF。所有预筛方案均未过正确性／净成本双门，未进入预筛策略矩阵。[物理诊断报告](tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)


### 2026-11-25 TCAD-SKY130HD-GCD-DRT-PREVIEW-RESTART-AND-FULL-SERIAL（意图登记）

- 基线 `6d0002cc`。同原冻结 GCD 物理端点、SDC、三角库、工具、CPU 6–11 四线程。两候选为历史同面积三门，`_091_` 旧 TT/SS 相对 hold 拒，`_093_` 旧正式验收。新鲜全链与两轮限域 DRT 保存、恢复并解锁后继续 DRT/RCX 的链同机串行；候选次序与方法次序正反切换。恢复不重复换门／清线，物理身份和实际路由范围单列核查。
- 两链均做独立解锁全块 DRC、天线、原三角时序及电气检查。每个物理合法候选实做非空 SEC，时序拒收的 SEC 作为诊断与原通过门和原链时间分开。记录启动、预览、保存、恢复、布线与寄生、STA 及验收实耗。详细动作和停点、版本、实物结果待正式配置。[前轮限域诊断](tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)

- **详细规约冻结** B1 从头 091→续跑 091→从头 093→续跑 093，B2 完全反序。同一 OpenROAD 进程内两轮限域保护 452 网、保存实际 DEF/ODB，再以 `floorplan_initialize` 的 NETS 片段只改 FIXED 为 ROUTED。读回几何、接线、元件及导引。第二次 DRT 沿用已形成的 pin access（`-no_pin_access`），原 64 轮上限，重新生成搜索与 worker。中间不执行 RCX/STA，正式路由后沿用三角、完整原门与独立 DRC／天线及 SEC。只有原门分类保持且两顺序总时间均下降，才支持此处流程净收益。

- **实际发出** 11:08:36（UTC+8），PID 493／495、CPU 6–11、外超时 1,100 s、逐路由命令限 100 s。输出 `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_local_route_reentry_20261125_v1`，协议 SHA-256 `ef9e0448d1ef351f779b0055ebfe9b5e781ac6a1a66486f42250b3fb00f6016f`，驱动 `f871188c6d4396b81a3ca1ca3e2c0f53b3114799461944e158c3769d03c12510`，原 TT／SS hold 下限 430.725704304／342.904315254 ps。首臂从头 091 执行。

- **正序首批实读** 从头 091 原门 TT／SS 拒，诊断 SEC262/0、独立 DRC／天线零，12.957414232 RAW s 含诊断证，原拒收门 12.134389461 s。从头 093 全门过、SEC262/0、14.489221974 s。续跑 091 的第二次 DRT 虽报 0 DRV，`design_is_routed` 失败，完整阶段未启动。
- **正序续跑 093 截止** 第二次 DRT 实际在顽固区第 11 次迭代仍报告 2 处违规，整路由进程按 100 s 限时结束，累计 100.212428991 RAW s。该次未进入最终三角与 SEC。逻辑结果 SHA-256 `99ef92fe3c44e83b9d252f881f894b5063d8d9f4a0e4293a953bfc3710a1a9c4`；第一组两续跑均缺最终物理验收，反序 093 同进程续跑启动。
- **正反序同进程终态** 四个从头臂均 DRC／天线 0、诊断 SEC 262/0，并复现原门对 091 拒／093 过的区分。四个续跑均缺最终 RCX／STA／SEC，091 两次在原生 0 DRV 后仍未布通，093 两次路由超时，反序耗 100.280981307 RAW s。按含全部检查的实际耗时，完整两候选共 27.446636206／27.911912155 s，续跑共 109.595720302／110.765576348 s 且均未完成。结果 SHA-256 `c3d80f22be2023b10cf53a1d17dc26f2f36d43784d00664018f375b02d528c27`。实际差包括失败和超时，不视为完整端点速度。


### 2026-11-25 TCAD-SKY130HD-GCD-DRT-PREVIEW-FRESH-PROCESS-REENTRY（意图登记）

- 同进程续跑的首个 `_091_` 在第二次 DRT 0 DRV 时未布通。保留原连续调用结果，补验新进程按两轮限域保存的 ODB 恢复，随后解锁并走 `-no_pin_access`，完整执行原 DRT/RCX/三角、独立 DRC、天线及 SEC。对两候选和从头链完全反序，同机把两个 OpenROAD 启动、保存、读回、布线和验证纳入端到端计时。若出现与旧 pin access 状态相关的现象，再以相同 checkpoint 验证重做 pin access 的影响，诊断结果单列。

- **发出并实读首个 091** 原路径 `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_local_route_checkpoint_restart_20261125_v1`，11:13:39（UTC+8），PID1731／1733、CPU 6–11、外限 1,100 s。协议 SHA-256 `6a02a3ee13909518675e7800c2dd747d40d76df5237a1dd635b04c72aaf93b55`，入口 `ff599859738b4f95d0b76229781234963249a31e5a3eca94b9f9b3d7a0cc4087`。新进程 B1 091 @14.446384902 RAW s 完整通过、回收 11.2608 µm²（独立 DRC／天线零，SEC262/0）；原门从头拒收，诊断全账 12.907943389 s。两条链的 ODB 物理身份有别，续跑实际 marker 恢复日志在原件中。

- **八单元终态** 两序全链完整，独立 DRC／天线全 0，SEC 均 262/0。091 两序从头 TT/SS 拒，恢复均验收 11.2608 µm² 且跨序相同 ODB。093 四次均过门，恢复与从头的网表、去日期 SPEF、三角相同，ODB／DEF 物理身份不同。全账两序从头 27.474597443／27.474492467 RAW s，恢复 29.556607516／29.571648851 s，两个顺序均额外约 2.09 s。不满足等原门判定与净时间双门。原结果 SHA-256 `3fa5f0274501b5beb0066c5d154421202653a943d5025d2d14e0c4967e46e1bb`。

- **独立核验与归档** 两个矩阵共核 8 个检查点，452 条固定线均在几何、接线、元件和导引相同下解锁，第二段无重复 PA，DRT 日志分别从第 3 轮读取 7／17 个 marker。091 两序新物理端点同一，功能网表与从头一致，10 网几何改变，TT／SS hold WNS 提高 0.533990／1.869893 ps。093 规范化几何相同。独验 SHA-256 `2c835e720884536a38fc167cdbb64e9a8a0b62b368f6b34af0f10d0fa2751204`。保留备用物理端点，未达到净加速门。原件封存于 `scratch/tcad_ibex_20261123/gcd_route_reentry_20261125_v1.tar.gz`，515 项、19,397,599 字节，SHA-256 `9122868d7edf7c9e1fd9ca40dceef556805801449d14b9b6429e0fa2e5c8e6e5`，tar 比较 rc0。[正式报告](tcad_ibex_20261123/GCD_LOCAL_ROUTE_REENTRY_REPORT.md) · [独立核验](tcad_ibex_20261123/GCD_ROUTE_CHECKPOINT_AUDIT.json)


### 2026-11-25 TCAD-POSTROUTE-CHECKPOINT-HOLD-SALVAGE（意图登记）

- 基线 `593fb9fa`。按已完整原预算台账筛选同冻结起点、同后端、仅因 hold 拒收且回收潜力严格超过该台账全部合格端点的候选。预先固定来源、动作、原验收及该来源既有最佳，不随补救结果调整。旧 GCD `_091_` 与已合格 `_093_` 同面积，提供补救机制依据。若已登记各矩阵入选不够，先实查其余已登记台账，再作有限扩展并登记来源。
- 每个入选候选做同机串行 fresh 从头和两轮实际检查点保存后新进程重入。原门全链均保留，逐项记录触发后的追加秒数、失败／超时、合格端点相对历史最佳的净增和共享动作。详细输入、门、触发规则、超时和执行顺序在启动前补齐。[前轮配对](tcad_ibex_20261123/GCD_LOCAL_ROUTE_REENTRY_REPORT.md)

- **锁定输入与触发** GCD `gcd_incident_cap_pair_20261124_v1/screened/fixed/02`，18.768 µm²、TT／SS 纯 hold，历史最佳 15.0144 µm²，CPU 6–11，原 11 ps setup WNS 门。UART `faeco_tcad_uart_online_20261125_matrix_v2/cell_02/fixed_online/01,04,05`，潜力 0.26244／0.34992／0.34992 µm²，原拒因为 SS／TT+SS／TT+SS hold，历史已验收最佳 0.23328 µm²，CPU 0–5，原 270 ps、2.7 ps setup WNS、原逐角 TNS 和 0.001 ps hold 容差。先做 fresh，复现纯 hold 拒才进入补救；GCD 用上轮几何规则确定限域，UART 用原报告的保护网，两轮保存并新进程读回、先解锁再跳 PA，用原三角与全块 DRC、天线、非空 SEC。主试每项最多一次补救，补救两段 DRT 共用 100 s，成功项同配置另复跑一次。补救费用为触发后实际追加 RAW 秒，包含失败；复核不计入触发成本。[预登记明细](tcad_ibex_20261123/HOLD_REENTRY_RESCUE_REPORT.md)

- **GCD 实际运行** `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_hold_reentry_rescue_20261125_v1`，CPU 6–11、外限 470 s。协议 `b6639029e73cd7c27ac02ee381d4dcbec498ebc5181c4acbef2d4a61debba672`，驱动 `bbd5429c80708313290c20a1acc740bbe720f9d0266212ba31b232e275ddbba9`。新鲜从头复现 TT／SS hold 拒收（430.431690290／341.936978732 ps），重入两角仍拒（427.816782000／330.468041820 ps）。两条均 DRC／天线零，诊断 SEC 262/0。补救收费 35.226741728 RAW s，含诊断 SEC 35.923469381 s；历史最佳保留，净增 0。原件结果 SHA-256 `e19d1c41cbcc7240dd10fc3cd82e6bb6dde07859321fafbc715fe9a3ce602eef`.

- **GCD 失败归因** 两法功能网表与 TT／SS 最差路径身份相同。重入后规范 DEF 有 8 条网变化，`clknet_0_clk` 提取总 C 13.3128→14.7743 fF，TT／SS hold 下降 2.614908／11.468937 ps。两段 DRT 实测约 8.995／22.050 s。多网同时改变，证据为物理变化与退化共同出现。

- **UART 实际发出** 11:28:33（UTC+8），`/home/toylog/faeco_tcad_uart_hold_reentry_rescue_20261125_v1`，CPU 0–5、四线程、外限 1,100 s，固定执行 `uart_01`、`uart_04`、`uart_05`。协议 SHA-256 `99fc2f66eca5291be7664f97088ae2895d339cae08dc1b1af61509796d899405`，入口与 GCD 相同。三角 TNS 预算 27／27／136.973650200 ps，TT／SS 相对 hold 下限 67.501115009／54.051914922 ps。

- **UART 首项及确认** `uart_01` 从头全链 28.851505557 RAW s，仅 SS hold 拒（54.038593045 ps）。重入及同配置确认通过，SS 54.066501276 ps，独立 DRC／天线零，SEC567/0，回收 0.26244 µm²，较历史前沿净增 0.02916 µm²。触发后的追加墙钟 38.100835381 RAW s，确认 37.785812397 s 单计。检查点有 0 个 marker，第二进程从第 0 轮开始；两次重入 ODB 同为 `accf471c5bc92bc7a819965b6829357d9561cb10a2c76a44c60908b18e0f77db`。

- **UART 六门及主试终态** `uart_04`、`uart_05` 均复现 TT／SS 拒，重入 SS 过门，TT 仍分别低于原门 0.001546574／0.000422473 ps。两者独立 DRC／天线零，诊断 SEC 567/0，补救各付 36.618141055／36.645325927 RAW s。UART 共 3 触发、1 合格、追加 111.364302363 RAW s，净增 0.02916 µm²。两设计合计 4 触发、1 合格、追加 146.591044091 RAW s。UART 结果 SHA-256 `40daffaba15317649145f66f6e69324edba5678f409cae8f545ef7aafd428c87`。


### 2026-11-25 TCAD-ASAP7-UART-REUSE-REJECTED-ROUTED-ODB（意图登记）

- 原 UART 三个 fresh 预 RCX routed ODB 与各自两轮检查点 ODB 逐字节同一，规范 DEF 同一、均无 checkpoint marker。SHA-256 分别 `5198369e3fef56a6e81812370fd009e3790a109e3b2eec9f43a0cabb668544c3`、`952d74eebb984a71faeb8e0ae3c760ae8f660dd6d2ab9a93c1d5326a00473bc8`、`3a0d631a7feeb2b2543bcd2a3ac74baeae20110da006833e85286ac8f58ae413`。GCD 无此同一证据，不进入本消融。先锁定 UART 原三项与预 RCX ODB、各项既有配对结果，再直接读回该原 ODB，用原新进程解锁和 `-no_pin_access`。按原门及独立 DRC／天线／SEC 验收，实测触发后全部时间；逐项比较 ODB、DEF、网表、去日期 SPEF、逐角时序与原门判定。

- **实发** 11:35:40（UTC+8），`/home/toylog/faeco_tcad_uart_rescue_existing_odb_20261125_v1`，CPU 0–5、四线程、外限 470 s，固定原序三项。协议 SHA-256 `27ed8866f23f98e9ba346b5720e3d428453aed546d053b49a07791e6d43dc936`，入口 `f4fe1429aabe8559112f304695f4ccbb5a55a556334d13f3e9146fae6f690c47`。

- **逐项结果** 输出 ODB、DEF、功能网表、去日期 SPEF、逐角时序与原门判定三项全一致，独立 DRC／天线零、SEC 567/0。依次追加 35.817057374／33.789948992／33.028336698 RAW s；总计 102.635343064 s，比原两段少 8.728959299 s（7.84%）。合格仍为 `uart_01` 回收 0.26244 µm²。结果 SHA-256 `c3562b97b8f44318fd6db9b0c011d261f3a8a3a71251e58ccc601ff4be36ea5f`。

- **封存** GCD、UART 两段及 UART 直接复用原件均归档至 `scratch/tcad_ibex_20261123/hold_reentry_rescue_20261125_v1.tar.gz`，494 项、18,095,482 字节，SHA-256 `31a5f0da724b6655cb9fc4e84960d62fc53df93b7445aa4d82d3e772e650e466`，重新比较 rc0。[总报告](tcad_ibex_20261123/HOLD_REENTRY_RESCUE_REPORT.md) · [复用原件](tcad_holdout_20261123/UART_RESCUE_EXISTING_ODB_RESULTS.json)


### 2026-11-25 TCAD-ASAP7-UART-TT-HOLD-CAPTURE-CLOCK-LOCAL-RESCUE（意图登记）

- 基线 `9e675fd4`。固定 UART `uart_04`、`uart_05` 的原拒收预 RCX ODB，动作、冻结原约束、三角库与工具沿用。围绕原 TT 最差 hold 的捕获时钟支路开放限域重布，其余既有网几何锁定并独立核对。用原 setup／hold、电气、独立全块 DRC／天线及 SEC 验收。范围与启动参数在执行前补记。
- 配对原全解锁重入两组六门，分别仍因 TT 拒收，追加 33.789948992／33.028336698 RAW s。拟回收均为 0.34992 µm²，当前已验收 0.26244 µm²。预先约定比较完整追加 RAW 墙钟、原门和净超过前沿的实际回收，所有失败成本计入，两个共享动作候选不累加。[原证据](tcad_holdout_20261123/UART_RESCUE_EXISTING_ODB_RESULTS.json)

- **原件路径读取** 两份 TT 最差 hold 同为 `uart_rx_inst.busy$_SDFFE_PP0P_` 自反馈，共用同一 launch/capture `/CLK`。原 DEF 捕获网均为 `clknet_3_7__leaf_clk`，覆盖 12 个 CLK 负载，其中包括原 SS 最差路径 `uart_rx_inst.rxd_reg`。候选范围与测试前冻结的工具设定另记。

- **冻结补救规则** 允许原 TT 捕获叶网及闭合反馈网。反馈边界为捕获 FF 原点 ±1 µm 与叶网 bbox 外扩三条有效轨距的交集，M2 合并偏移轨；其余网和时钟 FIXED。先保留原线只开放，失败才从同一 ODB 重启，只擦除允许数据网中接捕获 D 的一网；两级均 75 s DRT 上限，沿用 pin access，不扩域。对前后 DEF 核查几何、接线、元件、guide 和新线／via 锚点，在验收副本仅解除 FIXED 做原独立全块 DRC／天线／原门／SEC。

- **实际发出** 12:46:07（UTC+8），CPU 0–5、四线程、外限 520 s，`/home/toylog/faeco_tcad_uart_tt_capture_window_20261125_v1`。协议 `6eb751b8f54a1274ca203f1a2c4e26b5905d95b4c24bd0348087b6c8ffcfc045`，入口 `37790f802fd5476d8b32ecb81dea36f353d041998bad83bf4707efaf8ceaec6d`。两候选同三网 `clknet_3_7__leaf_clk`、`_0103_`、`_0120_`，二级只擦 `_0103_`，`net38` 锁定。锚点 `(11826,10530)` DBU，叶域 `[10773,9765,14661,15579]`，数据域 `[10826,9765,12826,11530]`，实际外扩 144 DBU。固定 `uart_04`→`uart_05`。[报告](tcad_ibex_20261123/UART_TT_CAPTURE_WINDOW_RESCUE_REPORT.md)

- **四次主试终态** 两级和两候选均产出完整实物，789 保护网几何未变，最终全网规范几何变化 0。二级 `_0103_` 重布后几何复原，逐角原指标复现。两组六门两级均拒 TT／SS，独立 DRC／天线零、诊断 SEC 567/0。含范围计算的两级追加 20.912214224／21.217278479 RAW s，原全解锁 33.789948992／33.028336698 s（SS 通过、仅 TT 拒）。实际净回收 0；前沿保留 0.26244 µm²。结果 SHA-256 `2268fb69daf059c14d3d29ac322f30597dc79d676db9b619fe679ca71710460b`。

- **补充诊断 C 预登记** 主两级最终几何均未改。复用同一原拒收 ODB 和完全相同的三网范围，另只清除捕获叶网 `clknet_3_7__leaf_clk`，保持两反馈网原线。沿用 pin access，单次 DRT 限 75 s，仍做范围核查、原三角和独立全块 DRC／天线及 SEC。成本独立列，并按三段依次触发计算累计费用。

- **诊断 C 实发** 12:48:10（UTC+8），CPU 0–5、四线程、外限 410 s，`/home/toylog/faeco_tcad_uart_tt_capture_leaf_reroute_20261125_v1`。协议 `30572bc52ce38d008d99a62511f9866843788ec95116b3e4618b3edfd7d84b39`，入口 `8c51b5cf62f755c84e9077ee872770bee9d8bcb865a6c6c571e878e05e01d164`。

- **诊断 C 终态** 只改捕获叶几何，其余网、功能网表和最差路径保持，独立 DRC／天线 0，诊断 SEC 567/0。叶 C 1.47498→1.57315／1.46184→1.56014 fF，TT 变 −0.046504／−0.006196 ps，SS −0.128397／−0.139014 ps，均仍由 TT／SS 拒收。C 两次追加 14.470563506／14.900985247 RAW s，主+C 条件累计 35.382777730／36.118263726 s，高于全放开。净回收增加 0。结果 `6f190314d9a1a51795e15267f368c28ebd248d09939f4a4564b9609232ef8765`。

- **封存** 主试和诊断原件均归档 `scratch/tcad_ibex_20261123/uart_tt_capture_window_20261125_v1.tar.gz`，220 项、8,478,782 字节，SHA-256 `ec6083f9d01d374c1cb482251b8cb97852b49f2605decdaa26a76f4d790f797b`，与原始目录比较通过。[主试结果](tcad_holdout_20261123/UART_TT_CAPTURE_WINDOW_RESULTS.json) · [诊断结果](tcad_holdout_20261123/UART_TT_CAPTURE_LEAF_REROUTE_RESULTS.json)


### 2026-11-25 TCAD-TWO-PDK-PURE-WALL-CLOCK-SCHEDULING（意图登记）

- 基线 `b73d92b8`。开发验证后冻结新失败调度，再在两个工艺的未调参留出设计上复用。四方法共用冻结候选池、原约束及同一在线后端，均受 720 RAW s 硬窗；候选验证数随实际耗时和自然收束变化。公共与策略专有筛选排序、候选失败和截止前实际工作进入同一账。
- 对照为现行去重 FAECO、固定批次与灵敏度排序单门。新变体每个失败批最多一次立即拆分试探，然后优先访问尚未派发的新批。预先锁定同面积阈值，记录首达的实收量、指定目标的实际首达、窗内最佳合格收回、未达和删失；正式运行前登记绑定、命令、顺序和硬门。[规约](tcad_wallclock_schedule_20261125/REPORT.md)

- **实现规约与留出资格** 沿用首次相对 hold 触发旧重排。有未试新批时失败多门批只立即尝试左子组一次，右组与更深拆分排队，待新批耗尽后按旧拆分推进。立即试失败的 singleton 只有累计接受集合实际改变后才可重试一次。纯墙钟配置 `max_evaluations=None`。拟 SKY130HD `riscv32i`、ASAP7 `ethmac`，各自原约束起点须先过资格并冻结。

- **工程验证及资格实发** 新增测试先两项按预期失败，补适配后两个专项模块合计 51 项通过。UART 18 项冻结池及 81.563830427 RAW s 实测筛选每臂等额计入，共享零动作单列，无跨臂候选结果复用。15:05:33（UTC+8）已冻结并启动 `riscv32i` 起点制备，CPU 6–11、四线程、外限 1,800 s。目录 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i`，`command.sh` SHA-256 `77a6e53024d76b91cbf615a84192b466d9c5fe1d7a703b44e56e5e34efe942fc`，`input_manifest.log` SHA-256 `1d1e79668ab25047ce72e98d42df3d37482b48bb8895d079ce06f6d445add14e`。

- **只读派发前缀** 18 个历史同范围已核物理点，现行纯钟第 6 次新整批、交错第 5 次新累计四门各因缺收据停止。交错在首个 SS 三门拒后立即实际派发过的 `_0562_` 单门历史标签为 SS 拒，随后恢复新批优先。自然多门批与旧第六次单门截断不同。此预检仅验证派发前缀，0 新 EDA。

- **UART 开发拟用配置** 正序 `fixed_online`→`single_sensitivity`→`faeco_dedup`→`faeco_interleave_dedup`，反序完全反转。CPU 0–5，外层 6,500 秒，输出 `/home/toylog/faeco_tcad_uart_wallclock_20261125_v1`。主面积阈值 0.01%，同约束窗内重新读取 0.15% 和 0.25%。正式入口、哈希、完整命令及状态见[开发报告](tcad_wallclock_schedule_20261125/REPORT.md)。

- **集成回归** Windows Python 3.11 的旧脚本语法收集问题经正式 WSL Python 3.12.3 消除，68 项专项通过。独立物理验收器已准备，等待候选件。

- **默认兼容复核** 新选项关闭时，500 个覆盖候选集、有限预算、不同批宽、hold 延后、setup 去重和末次预留的确定模拟与 `b73d92b8` 逐项同轨迹、同端点。此项为代码回归，无候选实布。

- **源码里程碑** 适配器与测试冻结至 `50aced718ace7d6016fcac22ba2d367704ca7e09`，已推 `origin/main`。原实验设定讨论基线仍记 `b73d92b8`。

- **SKY130HD 留出 P0 完成** `riscv32i` 原生 ORFS 784.87 s、rc0。原／导出 SDC 严格同命令，独立 DRC、天线、电气均零，非空起点 SEC 4559/0，三角绝对 hold 全正且 hold TNS 零。保留 TT／SS setup 残余，候选 EDA 0。仓库收据 87,033 字节，与 `qualification/CONTROL.json` 逐字节比较相同，SHA `5c85e150d8d8073af9dfef15fa59467b91b678a84e0dadff20ba0fed4902e9e9`。[原资格收据](tcad_wallclock_schedule_20261125/RISCV32I_CONTROL.json)

- **开发实发** 15:19:46（UTC+8），仓库统一 6,500 s 包装，CPU 0–5，PID 334／412、exec session 44907，stdout `/home/toylog/faeco_tcad_uart_wallclock_20261125_v1.stdout.log`。实发协议 `6d36c36ac5e764ed28e5c77f72ed8c167c19083930e2f220575f3f4e34773aab`，确认原 18 项池／历史筛选等额计费。出结果后再核验。

- **共享严格零动作** 17.328252706 RAW s，面积 79.00902 µm²，独立 DRC=0，SEC 567/0，原门失败空集。收据 SHA-256 `f76436278bc46d83e2f34b16a0c681154061191790b87757db021e2d5ab582be`。实发逻辑上限空值、三门批宽、单次 pin access。随后固定正序已实际派发。

- **开发正序首臂** 固定批次 6/6，18 项池自然耗尽；155.609207824 RAW s 首达 0.01%／0.15%（0.17496 µm²），230.144711114 RAW s 首达 0.25%（0.33534 µm²，亦为窗内最好）。第六次累计完整六门过门。`cell_01/arm.json` SHA-256 `2ee47d78dd01e931f5ed5d1be68af6f89772fba642b97778a0468c79594c1f60`，待矩阵独验。

- **正序灵敏度单门** 18/18 自然耗尽，TT 排序实际 1.361633380 RAW s；三阈值首达 108.269052663／134.134048210／159.554748240 RAW s，实收 0.08748／0.17496／0.26244 µm²；窗内最大 0.77274 µm²（0.978040%）。`cell_02/arm.json` SHA-256 `20de06306cac2ecbbbf5b5043d6e03e8ee95f8038fb4e7a8e6bc7b01bfe7ac6c`。正序前两臂独验通过，回执 `verification_prefix_02.json` SHA-256 `c886e7d5673a7d5a5ed36e7802be853f702d713e9ecb6ff175dd8ecae246f598`。

- **正序现行去重 FAECO** 19/19 自然结束，跳过一个完全相同的物理拒收，最高 0.83106 µm²（1.051855%）。三阈值首达 155.122484639／204.317873377／229.496407565 RAW s，实收 0.08748／0.14580／0.32076 µm²。前三臂独验通过，`verification_prefix_03.json` SHA-256 `c59ab0316a3fda63bd369fb19a1aa21a2514ea336943a1928983072ce18c8e75`。

- **正序交错去重 FAECO** 完成 25/26，最后 DRT/RCX 由 720 RAW s 裁剪，setup-only 命中零。三阈值首达 180.382296276／205.501912054／205.501912054 RAW s，实收 0.08748／0.26244／0.26244 µm²。最佳 0.75816 µm²（0.959587%），SHA-256 `c0c9ea43e562381939b7cd30bb804cb35822f3c57276c4115c15da233765727d`。反序首臂进行中。

- **正序四臂独核与机制诊断** 验收 `verification_prefix_04.json` SHA-256 `f5fb0cfade757a11baa770f6722e2692f48fc1caba78d14cb0ee527f22109a3e`。现行 #13/#15 与交错 #10/#12 各有一对同物理纯 hold 拒收，两法合格检查点数均为 8；交错 #26 截断提案的静态回收潜力 0.81648 µm²，小于现行最高 0.83106 µm²。

- **反序交错** 26 派发／25 完成，墙钟裁剪，无 setup-only 重用，0.75816 µm²，最优物理端点和三角时序与正序同。三阈值首达 180.004371361／205.269785507／205.269785507 RAW s。反序仍 8 过、14 hold 拒、3 FF setup 拒。原件 SHA-256 `d71f13ae6e3b92acb6c7f7ad0b2eb3671d20cc90808b505faf73a2541c3699ad`。

- **反序交错尾次核验** #26 与正序同一 12 门，冻结静态潜力 0.81648 µm²。预诊断完成，DRT/RCX 受剩余壁钟 13.554883190 s 裁剪，后续物理验收未启动。前五臂独验 `1069d80ed775b644b35ebc1cfe2746395bfd09130718ec3540f53ac479218946`。交错暂留开发负例。

- **留出入口限定选项** `run_qualified_wallclock.py --confirmed-only` 已在 `riscv32i` 合格输入 dry-run 通过，入口 SHA-256 `07ee25e24cc2e294bb8db9275abe412d4b38774f6e238650d02ee53fd6dce446`。仅能选择固定／灵敏度单门／现行去重并做正反序；共用 720 RAW s 和原门。待 UART 完结后冻结实际方法集合与命令，无留出候选 EDA。

- **反序现行去重** 19/19 自然结束，setup-only 去重一次，最高 0.83106 µm²，最优端点与正序一致。三阈值首达 156.072974744／205.412775640／230.475692382 RAW s。反序 8 过、9 hold 拒、2 FF setup 拒；完整 hold 拒收约 220.567 RAW s，对照交错约 343.006 s。`cell_06/arm.json` SHA-256 `3bc43aae0711edd1c7c57e5da0da57cb2f18c7e7384db7b10b1bffc175bb8471`。

- **首六臂独验与实际留出方法** `verification_prefix_06.json` SHA-256 `d224b92481a83a322bffdb0eb9f10085481e4c89b523f5c1f860d0dd58b2ef43`。现行两序均 0.83106 µm²，交错两序均 0.75816 µm²。留出方法冻结为现行去重、固定、灵敏度单门三组，原约束与纯墙钟沿用，交错保留为开发负例。正式待八臂结束。

- **ASAP7 留出 P0 预登记** `ethmac` 原 WB／TX／RX 时钟 1000／300／300 ps，I/O 200／60／60 ps，虚拟时钟延迟 229.195／55.660／76.515 ps，保留原三个独占时钟组及最大扇出。CPU 6–11、4 线程，原生／资格拟限 1,800／500 s，原件 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/asap7/ethmac`。原 SDC 与视图输入已绑，原生制备尚未发出。[资格规约](tcad_wallclock_schedule_20261125/REPORT.md)

- **预登记 SKY130HD 留出筛选** UART 八臂及全机 EDA 退出后，用合格 `riscv32i` 原输入实际筛选，`--screen-only --screen-workers 1 --confirmed-only --top riscv --pdk sky130hd`。CPU 0–5、预定总限 1,800 s，每工具 180 s。输出原起点根下 `screen_qualified_v1`，候选物理六臂保持待发。

- **反序灵敏度单门** 18/18 自然结束，TT 排序 1.358792412 RAW s，三阈值首达 108.366319576／134.077469689／159.633272864 RAW s，窗内 0.77274 µm²。两序现行 FAECO 到同 0.77274 µm² 分别比强单门早 105.569325892／103.522299898 RAW s。反序单门原件 SHA-256 `a201b4b8d2a44c40d3523e7845b25441f55deedbc5094e30d4cfe99c65ea33ad`。

- **完整 UART 生产结果** 反序固定 6/6 自然耗尽，最高 0.33534 µm²；三阈值首达 154.824248192／154.824248192／227.539684209 RAW s。八臂合计 138 派发、136 完整，两次截止均为交错尾次 DRT/RCX。结果 SHA-256 `f05eba825679d0a15660d0cba60fd090dd5a778536ce58173f6043ece0989954`，完整独验待写。

- **完整开发独验** 八臂均通过独验，SHA-256 `515aecdae7b892bfb4fdfa65d283064026799842d37dfa262c4ee4421dab59b9`。两序固定／灵敏度单门／现行去重／交错去重为 0.33534／0.77274／0.83106／0.75816 µm²。对应输入协议及结果原件逐字节入仓。交错留开发负例，正式跨工艺待证。[协议](tcad_wallclock_schedule_20261125/UART_WALLCLOCK_PROTOCOL.json) · [结果](tcad_wallclock_schedule_20261125/UART_WALLCLOCK_RESULTS.json) · [验收](tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json)


### 2026-11-25 TCAD-SKY130HD-RISCV32I-PURE-WALL-CLOCK-HOLDOUT

- 原约束、资格及实际筛选分别绑定 `RISCV32I_CONTROL.json` SHA `5c85e150d8d8073af9dfef15fa59467b91b678a84e0dadff20ba0fed4902e9e9` 与 `qualified_inputs.json` SHA `6aab7445cad94c543428fc7ace316a84f423e0f7f7b56d96d1e26707ad1bdca3`。仅限三方法正反序、原门、720 RAW s。筛选结束时物理臂 0/6。
- 真筛选由仓库统一包装，PID 469／471、session 16146、CPU 0–5、1 worker，每次工具限 180 s、总限 1,800 s。实测 64.099573641 RAW s，包装 67 s rc0，20 次候选 TT 单门筛查 18 过；两拒为 TT TNS。6,000 ps 原周期对应 60 ps WNS、600 ps TNS。原件 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/screen_qualified_v1/screen/`，池 SHA-256 `748d2a2866764f71672e95b968dd1122cf1faf3ecdd92f8246e781c66c01826f`，收据 `ea7d5a1a9a3ed519f387aa2ce83b33386d4a1f39a7800b62278134cd027570c2`。

- **筛选独验及矩阵实发** 独验 SHA-256 `445a0d6fd3be225d25acb93278a8c7365c527c73aeb3a549ab536ce995463c61`。16:21:32（UTC+8）`matrix_qualified_v1` 实发，CPU 0–5、4 线程、外限 6,500 s、PID 343／423、session 42647。原 P0 及筛选收据同一，资格绑定 SHA-256 `b4c71fde9d9f1f429b5f093382a379b9445aaf4bbd2d8da7e8c3e11c10615f2a`。三法正反序共六臂、720 RAW s、每候选由共同阶段截止控制。`ethmac` 等待 SKY130HD 计时完毕再发。[运行规约](tcad_wallclock_schedule_20261125/REPORT.md)

- **正式配置及资格复测** `protocol.json` SHA-256 `8b979b6931ca9f5a9f5eb0a20638f5a12dbdc8a6d2a169785fd407e0fb95f419`，`seed/control/receipt.json` SHA-256 `7f77c245d216b45d0e9b8301c55aab778b24ae78e98338a2d9d186366fc1c8fe`。现场三角 hold 匹配原 P0，实际配置 60 ps 的 setup WNS 门和 `logical_dispatch_cap=null`，待新鲜零动作结束。

- **共同严格零动作已验收** 59.361742441 RAW s、面积 71,427.2544 µm²，独立 DRC／天线 0，SEC 4559/0，无原门失败，费用单列。零动作收据 SHA-256 `064e0d35be6b8509741f4a8d1f8158fa85ea94a6a534653a7329d4e85ddc8a4e`。固定首臂已实际派发三门；阶段代码与原 UART 证据提交 `bbc28dba`。

- **正序首个合格候选** 固定第 2 次在 211.831371594 RAW s 回收 26.2752 µm²（0.036786%），DRC／天线零、SEC 4559/0。此前第 1 次仅 TT TNS 拒。仅为候选级收据，当前臂进行中，后续独验。

- **原诊断边界候选** 正序固定第 3 次累计六门，预诊断 0 marker，实际首次独立发现 10 处 Short／Cut Short，重复 DRT/RCX 后清零并过原门与 SEC，在 539.183750966 RAW s 验收 52.5504 µm²。生产候选收据 SHA-256 `2d0396274bd993e25a8c2de5d82ea9724ae46bd56187dda1fc48d3ecd66f66f4`。

- **正序固定完成** 3/4 完成，最好 52.5504 µm²（0.073572%）。0.01% 首达 211.831371594 RAW s，0.15%／0.25% 未达。第四次初始 DRT/RCX 被剩余墙钟裁剪，整臂含筛选实际 712.230973644 RAW s。同臂生产 SHA-256 `e8172bba56f3687ae56c95e2efdefd8c0900989a122991a938ae20f88cd54a9e`。正序灵敏度单门运行。

- **v1 中止及归因** 758 s 后 rc1，第二臂真实排序 STA 返回 18 个已绑实例，3 个输出为 `+Inf`（`_5736_/Y`、`_6414_/Y`、`_6788_/Y`），旧 AES 严格有限值校验拒绝，候选派发 0。原 TT WNS 精确复现、原约束保留。通用入口拟让全 `+Inf` 动作按冻结序放末位，有限公式与验收门保留。原件结果 SHA-256 `57055442966f46c3186e61905d3d3a79e52c69840064b97951ac2569314e841b`，另做 v2 完整结果。

- **v2 入口核验** 实际排名重放中 15 项有限保持原公式次序，3 个全 `+Inf` 候选排在池尾，非法身份与缺失记录仍拒。7 项核对独立于包含 RAW 计时两项的 70 项 WSL 回归（16.91 s）。正式窗口使用 100 ms 轮询的同一 RAW 时钟，其他阶段保留原执行。v1 固定尾次子进程等待与绑定的 RAW 截止相差约 7.770 s。入口 SHA-256 `a8324e5b94747193c742d5174c8e71fac89918f1ea699988aea4ca3e5d3e9c35`，工具 SHA-256 `03de2e39b8c178d205e5e80f1857040af7f8270a9e062120524cb145a8f2eb8d`，待 `ethmac` 当前计时完毕发出。

- **最终源 dry-run** 最终 `a8324e5b` 字节重新绑定原 P0、三角库、实际池和阶段配置。合格输入原件 `/tmp/riscv_v2_dry_final_ENPGT6/validate/qualified_inputs.json` SHA-256 `e7e29999721a0373f80bfc5c2507ee0f39025aff6d043b475ba228186ffa9a3f`，RAW 轮询 0.1 s，`protocol_and_inputs_validated`，0 个候选物理臂。新增可复现排名测试与 RAW 独立组合共 8 项通过，2.00 s。

- **v2 实发** `ethmac` 资格物理进程退出后，17:09:34（UTC+8）包裹 PID 437、Python PID 439、exec session 85034 进入新根 `matrix_qualified_v2`。同原 P0、18 项池、64.099573641 RAW s，CPU 0–5、外限 6,500 s。现场 `qualified_inputs.json` 与最终 dry-run 逐字节同，实际协议 SHA-256 `a768316f012f7386c2c1d31e43829b9490c0da82174ab884dc3b6634ea5f2dae`。每臂 720 RAW s，并以 RAW 子进程限时，完整正反序与 v1 分开。候选待物理前置资格。

- **v2 严格零动作** 57.497508272 RAW s，原门全过、面积 71,427.2544 µm²。收据 SHA-256 `9e8769707fac96fca71dc8a9ea2e4ebbeb92f0b92b8d77b5489a70699a323d4b`，随后固定正序实际派发。

- **v2 正序固定与实际强单门排名** 固定 3/4 完整，0.01% 205.271893856 RAW s，最高 52.5504 µm²。尾次工具停止时间记录超过 RAW 截止 0.085670931 s，在 0.1 s 轮询尺度内，不计为通过。独验 `verification_prefix_01.json` SHA-256 `bc7c456102c04a723bdf6614d4cdcb658a7230e3d7eb9084595cc19888618b51`。强单门新鲜排名保留 18 项，原三个 `+Inf` 实际排池尾，工具 1.494135247 RAW s，进入候选评估。

- **v2 正序强单门** 8 派发／7 完整且全部通过，0.01% 首达 139.934067577 RAW s、实收 8.7584 µm²，最高 57.5552 µm² 在 582.955503649 RAW s。尾次 DRT/RCX 停止晚于 RAW 截止 0.081223718 s。0.15%／0.25% 未达。原件 SHA-256 `fc9e38c9dffd8087dec911b31ab31129d3777e917677a9a5d820a4a5942bb2e1`，前缀独验 `c48c78bc9e5f2288945bad64a87c5d5ff0431cd0a4953464eb68dae404f05a07`。

- **v2 正序现行去重** 7 派发／6 完整、setup-only 重用 1，首达 204.744496206 RAW s、实收 10.0096 µm²，最高 45.0432 µm²。第 6 次先出现 10 个独立 DRC，真实重试清零后仍因 TT TNS／SS WNS 拒，单请求约 298.486 RAW s。尾次预诊断截止。`cell_03/arm.json` SHA-256 `31f2feaca2a9f700fdef0742b1c1c176a22755f46698027b071553e5b870b9ab`。反序已发。

- **v2 正序三臂独验** SHA-256 `22241070a1817552e48fbf0246a2b09e89121c96979a941461bda9399c1134c2`。现行 3 个完整 setup 拒收共 431.868 RAW s，无 hold 拒收触发。固定第三组和现行首组分项冻结 TNS 直接加和分别偏悲观、偏乐观，不能替代整组实布验收。

- **只读既有排名前缀** 同冻结 scope 的灵敏度前 3、前 6 动作组分别匹配原单门第 3、6 次实际通过，回收 26.2752、48.7968 µm²。9 项处首次缺验收收据。单请求独立成本只作原件，未作新跑累计耗时。SHA-256 `537edd533ad45f93287c428c5383120700e4b342fb7274e84f3e17ce369f1f95`。[复核](tcad_wallclock_schedule_20261125/RISCV_RANKED_PREFIX_REPLAY.json)

- **v2 反序现行去重** 7 派发、6 完成、setup-only 复用 1 次，0.01% 首达 205.321724062 RAW s 实收 10.0096 µm²，第 5 次最高 45.0432 µm²，最优实物和三角与正序同。第 7 预诊断到了 RAW 截止后 0.028278466 s 停止。三 setup 拒收约 430.808 RAW s，无 hold 反馈。`cell_04/arm.json` SHA-256 `0a76ee9e65cc965d8315c8bedccc24ffbab941c8bdbd44e21f1fdaa16a1b15e3`。

- **v2 反序强单门** 8 派发、7 完成全过，0.01% 首达 139.236680946 RAW s 实收 8.7584 µm²、第 7 次 584.308231534 RAW s 最高 57.5552 µm²，最优实物及三角与正序相同。末次 DRT/RCX 于 RAW 截止后 0.084407044 s 停止。`cell_05/arm.json` SHA-256 `c51faa27c1c49726a277d0bc357fc789043fafe7bb7ae1f7bf5974820439b8ba`。

- **v2 反序固定及完整独验** 反序固定 4 派／3 完，0.01% 首达 204.686835858 RAW s（实收 26.2752 µm²），最高 52.5504 µm²。全部六臂生产 rc0／4,039 s，38 派发、32 完整。两序单门／固定／现行去重最高分别为 57.5552／52.5504／45.0432 µm²，三法都未达 0.15% 和 0.25%。主小目标单门先到，后验至少 45.0432 µm² 时现行先到。独验 rc0、6/6，SHA-256 `ef949a66f62d5645ddbef1876e338484ecededbe0896b2efba467ca09814ed04`。[协议](tcad_wallclock_schedule_20261125/RISCV_WALLCLOCK_PROTOCOL.json) · [结果](tcad_wallclock_schedule_20261125/RISCV_WALLCLOCK_RESULTS.json) · [独验](tcad_wallclock_schedule_20261125/RISCV_WALLCLOCK_VERIFIED.json)

- **阶段结论** 本留出支持有限时间的面积与时序权衡，现行最高面积低于两基线。两序非通过原因以 setup 为主且没有触发相对 hold 重排，三个完成拒收约 431–432 RAW s。下一步先统一强单门初始排序，再对固定与现行调度分离批宽和反馈。既有冻结 TT TNS 单项变化线性相加已在两组合分别高估与低估实布损失。原三角和物理门保留。


### 2026-11-25 TCAD-ASAP7-ETHMAC-NATIVE-QUALIFICATION

- SKY v1 退出且无其余计时后启动，16:35:19（UTC+8）、CPU 6–11、四线程、总限 1,800 s、PID 459／468／470。原目录 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/asap7/ethmac`，实发 `command.sh` SHA-256 `4bc4b6ab2c16af6409a6d4c337cf17c806884e8197753eedddb0f56df10c185f`，输入清单 `e837ef1534b2ca046f0696b74f9844e59b1e8f694d21d2b9c482d4015f13e7ec`。原本多时钟 P0 资格未结果，候选 0。

- **原包装超时与原根复位** 原生 rc124 截在 RCX 16%，详细布线已完成 DRT 零违例，原生 DRC／天线均零。保留部分报告 `recovery_finish_v1/6_report.initial_timeout.log`。17:04:55（UTC+8）仍用原根与输入只恢复 `6_report.log`，CPU 6–11、四线程，限 600 s。恢复 `command.sh` SHA `e38c4320f18ef61afc26ca280bd62e5f30e295b2fbf05e3c3a5642871efd2120`，输入前置 SHA 清单 `b1ecf6b78f802227d0d05defdb3e2cb6d7da9ca12dc10ce4e675fbbca8163733`。回执资格待后续。

- **末段完成、资格实发** rc0、原 `final_report.tcl` 用 68.64 s，原 SDC、DRT 和 fill 快照均同。RCX 60,697 网、77,878,734 字节 SPEF。恢复日志 SHA `99e32c632384a5c4e1e22ecac99931def577bbb6d08089de060e2d1cf5a9138c`。独立资格 `qualify_native_recovered.py` SHA `c416e2115946fe93fadd5e5dce2eabb0f7c75c025ee8793f3722324f51823cba`，限 500 s，候选 0。

- **资格进行中** FF／TT／SS hold +28.591324／+43.821717／+55.663543 ps。独立全块检查被原 45 s 子工具限时裁剪，记录 `returncode=null` 和 45.846606863 RAW s；完成 512,346 guides 的加载后仍缺独立最终报告。资格未确认。

- **原起点资格失败** `qualification_incomplete`／rc1，三角绝对 hold 非负、hold TNS 零，SEC 52287/0；FF／TT／SS max slew 超限 0／9／1017，max-cap 均零。独立全块检查超时，原生与独立检查分列。原件 `CONTROL.json` 358,712 字节逐字节入仓，SHA-256 `249a4a5274ff217d2a21f049cf0f318935d54af28a80bc85b1ff7c5b256b2ba6`。候选及收益读数均无。[资格原件](tcad_wallclock_schedule_20261125/ETHMAC_CONTROL_INCOMPLETE.json)


### 2026-11-25 TCAD-SKY130HD-RISCV32I-SENSITIVITY-RANK-ALIGNMENT（预登记）

- 基线 `1c3e17ad`。阶段一在原冻结物理起点真实试验排名前 9 的精确累计动作，沿用原三角、原联合门、独立 DRC／天线与 SEC。前 3／6 的已测前缀作为既往证据，阶段一的物理结果不供阶段二复用。
- 阶段二以原 18 项灵敏度排名对齐同后端单门、固定三门和 FAECO，执行正反序六臂。各臂 720 RAW s、共同筛选 64.099573641 RAW s、现场同排名查询各自实付，FAECO 原 hold 反馈和 setup-only 精确去重保持。冻结 0.01%（7.14272544 µm²）、26.2752、45.0432、52.5504、57.5552 µm² 作为比较下限，记录实收、完成前缀和未达删失。旧 v2 以同方法和顺序配对，具体运行命令待实发绑证。[规约](tcad_rank_alignment_20261125/REPORT.md)

- **第一阶段实发** 18:55:36（UTC+8），CPU 0–5、四线程、限 800 s 外包和 720 RAW s 候选窗，PID 511／513、session 27817。九项绑定 46 条直连信号网，静态减量 75.072 µm²。实发 `preregistration.json` SHA-256 `6fe3dfe22f073d395e7a6271ffe3c8d24d735577c12c22b3ea00f996c73893b8`，脚本 `fba97b8007ac8526f891b9feac47cb5d747a8438ea6029bd4f738312f6bc1322`。完整 DRT/RCX 若因其它门拒而普通 SEC 未执行，则补做、单列诊断 SEC。首次在线预诊断零标记，阶段二待实发。
- **第一阶段验收通过** 75.072 µm²，候选端到端 325.449205905 RAW s（筛选、排序与共享零端点复用），包装 346 s／rc0。初布独立 DRC 10 个，按证据只放行 `net1234` 复做一次，最终 DRC／天线 0、SEC 4,559／0、FF／TT／SS 新负 setup 均为 0，原联合门全过。根按旧 `audit_logical` 独验。结果 SHA-256 `223fd08596d4a766e16f315f4ed3d70976f85f154807252c202ce3b639b638ab`。[细项](tcad_rank_alignment_20261125/REPORT.md#前九门验收)
- **第二阶段实发** 19:02:11（UTC+8），包装 PID 433、Python 435、session 32766，CPU 0–5 顺序独占、外包 6,500 s。资格输入 `e7e29999…`、排名对齐输入 `6dc2b91b…` 与无物理预检完全一致。新的 `matrix_rank_aligned_v1` 从同一冻结起点重新验证，不读第一阶段候选产物。第一阶段协议／结果／独验已逐字节入仓。[实发及原件](tcad_rank_alignment_20261125/REPORT.md#比较矩阵实发)
- **正式绑定与首派** `protocol.json` SHA-256 `49ef72e393042902d844fb846df8045747d7a2adfc0dea47c2001f95c7259392`，共享严格零端点通过（`6254e637…`），首臂新鲜排名 1.571247283 RAW s、池内 18 项逐项同序，随后派前三门。
- **正序固定终态** 4 派／3 成全过，最高 75.072 µm²，五个冻结下限均达到。前三／六／九累计合法端点分别实收 26.2752／48.7968／75.072 µm²，首达 140.944343126／217.972797309／534.264250401 RAW s。第 4 个候选的 DRT／RCX 被 RAW 硬窗裁剪，最后停止晚 0.088810127 s。`cell_01/arm.json` SHA-256 `7d2c47f4e822024ecc17dea1eecd23d1e669177a08045ec177432d5d11e23939`，正序单门已派发。
- **正序强单门终态和两臂独验** 8 派／7 成全过，最高 57.5552 µm²，首达同实收 590.992202129 RAW s。旧 v2 同端点 582.955503649 RAW s，当前约慢 8.037 RAW s。核验 `verification_prefix_02.json` SHA-256 `e21c24ede6a35b8dfe1bbc747f6518d84f3f8cdee444c7e5719c47d7843e527a`。FAECO 正序派出相同前三门。
- **正序 FAECO 终态和三臂独验** 4 派／3 成全过，最高 75.072 µm²。前三个合法实收 26.2752／48.7968／75.072 µm²，首达 141.325963060／217.747515805／534.574689086 RAW s。固定与 FAECO 四次派发累计动作全同、最佳物理端点同，未触发 hold 延后／二分／缓存复用。独验 `c8b7bbca25e5e8dac309292717ffe0b27780d67169310525d70711414e124979`，反序已发。[细项](tcad_rank_alignment_20261125/REPORT.md#六臂运行回执)
- **反序 FAECO 终态** 4 派／3 成全过、最高 75.072 µm²，原件 `e0f68ba009a9b515ed5000bc53aadd08aff654c6434006aecfbec1a373d30153`。首达三实收 141.475853083／217.274253568／531.074738135 RAW s，无 hold 延后、二分、缓存复用。反序单门已启动。
- **反序单门终态** 8 派／7 成全过，最大实收 57.5552 µm²，用 597.310479761 RAW s。正反序面积复现，RAW 止时超量 0.090423441 s。`cell_05/arm.json` SHA-256 `fdca598d198194781dec435da7064a70e6f782457def503af5dda1133297dda2`，末臂反序固定已启动。
- **全六臂终态** 反序固定 4 派／3 成，75.072 µm²。生产 rc0／4,043 s，独验 rc0／6 臂，32 派／26 成全过、6 次末次裁剪。两序同榜固定、FAECO 与强单门最高 75.072／75.072／57.5552 µm²；固定和 FAECO 同动作同物理，同实收首达差不超过 0.67 RAW s，无 hold 延后、二分或拒收缓存复用。保留 WSL 原始目录和已逐字节入仓三件。[完整比较](tcad_rank_alignment_20261125/REPORT.md#720-raw-s-完整比较) · [协议](tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_PROTOCOL.json) · [结果](tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_RESULTS.json) · [独验](tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_VERIFIED.json)


### 2026-11-26 TCAD-EXTERNAL-BASELINES-NATIVE-RECOVER-POWER-AND-TRITONSIZER

- **对象与协议**：SKY130HD AES / `riscv32i`、ASAP7 UART / AES 共四设计，沿用同版本 OpenROAD `b511b6a`（`openroad_unstamped`）、冻结 `CONTROL`、原 SDC 与 FF/TT/SS 三角验收门，测试原生 `remove_fillers` → `repair_timing -recover_power 100`（标准档与 `-allow_setup_violations` 宽松档）并走完整合法化、DRT、RCX、三角 STA、DRC/天线检验；同步以 `report_power -digits 9 -format json` 测四设计 `CONTROL` 与 FAECO 最优端点的同口径 TT 功耗；并对归档仓库 `The-OpenROAD-Project/TritonSizer`（`31c4a04`）完成源码级依赖审计。
- **结果与收据**：四设计 OpenROAD 原生回收合格面积全为 `0.0000 µm²`（AES 120 门 SS setup −761.82 ps 且三角 hold 全退化；UART 16 门同面积替换且 FF/TT hold 退化；`riscv32i` 24 门 TT TNS −5,621.11 ps 超 600 ps 预算且新增 1 处天线；ASAP7 AES 179 门 720 s 内重布线超时 `rc=124` 且报 `checkConnectivity break`）。四设计 FAECO 已验收端点总/组合/漏电功耗三降。独立原始日志核验 SHA-256 `9e274d6bececb7e7e5d0156da34605a39ca3492bfc71f634218949705289818b`。[总报告](tcad_external_baselines_20261125/REPORT.md) · [核验收据](tcad_external_baselines_20261125/NATIVE_RECOVER_POWER_VERIFIED.json) · [TritonSizer 审计](tcad_external_baselines_20261125/TRITONSIZER_COMPAT_AUDIT.md)


### 2026-11-26 TCAD-SKY130HD-AES-GEOMETRIC-NEIGHBOR-ABLATION

- **对象与协议**：SKY130HD AES 冻结起点、18 项池、同一 FAECO 调度、720 RAW s 硬时窗（含 113.363 s 筛选与现场索引/诊断计费）、CPU 0–5 独占串行、4 线程、共享当前代码指纹下新鲜严格零动作预检（`shared_preflight`，SEC 11,089/0）。正反序 6 臂对照等放行规模最近邻 `geo_m1_k1`（只读召回 12/26 = 46.2%）、全覆盖接触几何 `geo_m1_r0`（只读召回 26/26 = 100.0%，放行 3.19×）与 FAECO 现场 DRC 标记归因 `online`。
- **结果与收据**：两几何基线正反序合格回收均为 `0.0000 µm²`，`online` 两序均回收 `67.5648 µm²`（首达 490.07/501.25 RAW s，ODB/DEF/V/去日期 SPEF 跨序一致，SEC 11,089/0）。完全相同三门提议（Request 3）下，`geo_m1_k1`（3 网）触发重试 208.73 s 且 SS hold −10.482 ps；`geo_m1_r0`（9 网）免重试 105.60 s 仍因多放 6 条保护网令 SS hold −10.482 ps 拒收；`online`（精确 3 网，122.75 s）三角 hold 全改善并通过。原始根 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_vs_online_faeco_20261125_v1`，独立核验 SHA-256 `48304ef41b9006f717b836bc46e186a9b2b3ff09c6b3f262047f3ae9e5de3da1`。[消融报告](tcad_geo_neighbor_20261125/REPORT.md) · [核验收据](tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json)


### 2026-11-26 TCAD-ASAP7-AES-INDEPENDENT-HOLDOUT

- **对象与协议**：全新 7 nm 独立留出设计 `asap7/aes`（`aes_cipher_top`，22,819 实例，72% 利用率，380 ps 单时钟原 SDC，无硬宏）。原生制备 575 s，经 21 条局部 M3 非时钟网保护修复（`repaired_control_v4`，`write_db` 置于 `extract_parasitics` 之前保留全部 24,521 个 ASAP7 `RECT` 补丁）取得 `hold_qualified` 共同起点（FF/TT/SS hold +35.358/+52.071/+24.664 ps、零电气、独立 DRC/天线 0、原生至修复 SEC 10,027/0）。冻结 TT 筛选 156.27 RAW s 得 18 项候选；共享实时灵敏度排序正反序 6 臂（`fixed_online`、`single_sensitivity`、`faeco_dedup`，720 RAW s 纯墙钟，CPU 0–5 独占串行，4 线程）。
- **结果与收据**：批处理（`fixed_online` 与 `faeco_dedup`）正反序均回收 `0.612360 µm²`（0.0518%，6 门，SEC 10,027/0），为强单门 `0.204120 µm²`（0.0173%，2 门）的 **3.00×**；到达共同实收 `0.204120 µm²` 提前 220–252 RAW s（414.55/417.00 & 418.55/401.62 vs 667.13/637.02 s）。三策略跨序 ODB/DEF/V/去日期 SPEF 逐字节一致。前两批直接通过未触发 hold 反馈，固定三门与 FAECO 逐字节同端点；16 次全块预诊断均为 0 marker（均耗 44.02 s）。原始根 `/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_rank_aligned_v1`，独立核验 SHA-256 `d2df3be99b701b97b63db87ec1c2a20c01702958582b590415d7fa3b1a59a5da`。[留出报告](tcad_asap7_aes_holdout_20261125/REPORT.md) · [核验收据](tcad_asap7_aes_holdout_20261125/ASAP7_AES_HOLDOUT_VERIFIED.json)


### 2026-11-26 TCAD-BOXED-PRE-DRT-DRC-1HROW-DUAL-PDK

- **对象与协议**：工艺无关 `1.0 × H_row` 局部窗口化布线前 DRC 预检（`tcad_boxed_drc_20261126/boxed_drc.py`，终检 `unlocked_drc` 维持全块 DRC）：(1) 全部 14 组历史不重复批次（SKY130HD AES 9 组 × 3 档 halo + ASAP7 AES 5 组 × 2 档 halo）零漏报/零位移审计；(2) 7 nm `asap7/aes` 同排名 6 臂正反序（`faeco_full_drc` vs `faeco_boxed_drc` vs 同步窗口化 `single_boxed_drc`，720 RAW s，CPU 0–5 串行）；(3) 130 nm `sky130hd/aes` 4 臂正反序（`faeco_full_drc` vs `faeco_boxed_drc`，720 RAW s，CPU 0–5 串行）及新 9 门端点同口径 TT 功耗实测。
- **结果与收据**：历史 37 组测试 `moved_other = 0`，SKY130HD AES 56/56（100%）精确 marker 与邻网一致，单次预检 130 nm 提速 3.04×–6.31×、7 nm 提速 4.61×–16.69×。7 nm `asap7/aes` 6 臂中 `faeco_boxed_drc` 单次预检 38.11→7.03 s（5.42×）、达 0.61236 µm² 提前 64.7–66.0 s 且跑完第 3 批触发 `SS:hold_regression` 暂缓，对 `single_boxed_drc`（0.30618 µm²）仍保持 2.00× 面积与提前 163–169 s；130 nm `sky130hd/aes` 4 臂中共同 5 组请求 100% 释放邻网一致且 0 重试，单次预检 14.40→3.33 s（4.32×），两序均将第 5 批 9 门拉入 720 s 内验收，回收面积由 67.5648 跃升至 **98.8448 µm²（+46.30%，占 18 项池 50.00%）**，Setup 仅耗 <0.23% 预算、三角 Hold 全改善、功耗降 −0.0512%/−0.0710%/−0.0320%。全 10 臂跨序逐字节复现、全块 DRC/天线 0、SEC 全过。原始根 `/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1` 与 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_boxed_drc_20261126_v1`，独立核验 SHA-256 `41e08aa3d88240bd8d9fa125ba43f9c7ef23d918c419dbffaaa36dd18153e0fa`。[报告](tcad_boxed_drc_20261126/REPORT.md) · [零漏报审计](tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json) · [10臂核验](tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) · [9门功耗](tcad_boxed_drc_20261126/SKY130_AES_9G_POWER.json)


### 2026-11-26 TCAD-CLASSICAL-LR-4DESIGNS-AND-BACKEND-CONTROL

- **对象与协议**：SKY130HD AES / `riscv32i` 与 ASAP7 UART / AES 四大设计同 18 项池与 1% Setup 预算下执行经典 5 轮冻结 TT SPEF 子梯度拉格朗日松弛（Chen/Chu TCAD'99 & Flach TCAD'14 范式），先后挂载 FAECO `1.0 × H_row` 窗口化保护后端并在 `sky130hd/aes` 上对照标准全片重布线（清信号线 + `pin_access` + GRT + DRT）。
- **结果与收据**：独立标准全片重布 LR 在 `sky130hd/aes` 上 600 s 超时（`0.0000 µm²`）；慷慨挂载 FAECO 窗口化保护后端后，LR 在 `sky130hd/aes` 140.9 s 一次通过 18/18 门（`197.6896 µm²`，0 DRC，SEC 11,089/0），但在其余 **3/4 设计上仍全军覆没（0.0000 µm²）**：`riscv32i` 240 s 局部 DRT 超时、`asap7/uart` 报 `FF:setup_budget` + `TT/SS:hold_regression`、`asap7/aes` 重试后报 `SS:hold_regression`（463.85 s）。原始根 `/home/toylog/faeco_tcad_lr_4designs_20261126_v1`。[报告 §3](tcad_external_baselines_20261125/REPORT.md) · [核验收据](tcad_external_baselines_20261125/LR_4DESIGNS_VERIFIED.json)


### 2026-11-26 TCAD-V4-REVISION-SUITE（LEF 规则/确定性、同窗口组件消融、Hybrid FAECO、Timing-closed 基准与 b/K 敏感性）

- **对象与协议**：针对模拟审稿全部 P0/P1 意见的五组实证（均用 CPU 0–5 独占、同一 $1.0\times H_{\mathrm{row}}$ 窗口保护后端、720 RAW s 预算与原三工艺角全门）：(1) SKY130HD & ASAP7 真实 `.tlef` 逐层规则半径核验 + 3× 同版图 RCX/STA 确定性 + 既有收据 Hold 容差敏感性与 18 项池唯一性审计；(2) `SKY130HD AES`（`single_sens_boxed`/`fixed_boxed`/`faeco_defer_only_boxed`）与 `ASAP7 AES`（`fixed_boxed`）同窗口组件消融；(3) **Hybrid FAECO**（$\tau_{\mathrm{probe}}=\min(180\text{ s},0.30(\tau_{\max}-t_{\mathrm{screen}}))$ 单遍全池探针 + 自适应微批次回退）四设计实测；(4) 绝对时序收敛基准 `asap7/uart @ 500 ps`（FF/TT/SS Setup/Hold 均严格非负）三策略实测；(5) `asap7/uart` 批宽 `b ∈ {1,2,3,6,9,18}` 与池规模 `K ∈ {9,18,36}` 敏感性及 7 nm 18–120 门/原地镜像 DRC 审计。
- **结果与收据**：(1) SKY130HD 全栈（$\le 1.60\,\mu\text{m}$）与 ASAP7 引脚/信号层 `M1–M7`/`V0–V7`（$\le 0.072\,\mu\text{m}$）均严格小于 $1.0\times H_{\mathrm{row}}$，3× RCX/STA 极差 `0.000 ps`，四设计池 18/18 互异；(2) `SKY130HD AES` 同窗口下直连电容重排独立实现 `33.7824 → 98.8448 µm²`（`2.93×`），微批次独立提 AUC `+50.3%`，`ASAP7 AES` `fixed_boxed` 回收 `0.61236 µm²`（AUC `0.247`）；(3) Hybrid FAECO 四设计分别回收 `197.6896`（100% 池，137.6 s 通过，AUC `128.78`）、`75.0720`、`0.83106`、`0.61236 µm²`，4/4 终态持平或 2× 超越纯 FAECO，0 DRC/SEC 全证；(4) Timing-closed `asap7/uart @ 500 ps` 上 FAECO 回收 `0.83106 µm²`（13/18，AUC `0.4561`）胜过单门（`0.68526`）与固定批（`0.33534`），终态仍严格 Timing-closed；(5) `b=2,3` 达峰值 `0.83106 µm²`（AUC `0.526/0.491`），`K=36` 达 `1.50174 µm²`（`1.901%` 功能单元面积，AUC `0.7216`）。[总报告](tcad_v4_revision_20261126/REPORT.md) · [LEF/确定性](tcad_v4_revision_20261126/LEF_AND_DETERMINISM_AUDIT.json) · [组件消融](tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json)（SHA-256 `40f524b3…`）· [Hybrid](tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json)（SHA-256 `726b6a06…`）· [Timing-closed 与敏感性](tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json)（SHA-256 `04e55044…`）


### 2026-11-26 TCAD-V5-REVISION-SUITE（部分执行：Stage 1 完成、Stage 2 完成 2A 与 2B 第一遍；响应第二轮评审 85/100）

- **状态（2026-11-26 22:25 中断点）**：Stage 1 **已完成**（收据 `V5_STEP1_POWER_7NM_DET_VERIFIED.json`，SHA-256 `85bfc165…`，1060.11 s）；Stage 2 完成 2A 两臂与 2B 第一遍八个 key（收据 `V5_STEP2_DEDUP_NATIVE_VERIFIED.json`，SHA-256 `917a6655…`），2B 第二遍（SKY 两设计 600 s 预算，`::rt600s`）在用户要求转交时被中止、**未落盘**；Stage 3/4/5 未启动。机器上已无 EDA 残留进程。续跑与必查项见 [执行交接](../HANDOFF_2026-11-26_V5_EXEC.md)。
- **Stage 1 实测**：TT 真实 SPEF 功耗 `SKY130HD AES` 18 门 −0.102%／−0.140%／−0.064%、`ASAP7 UART-TC` 13 门 −0.660%／−2.142%／−0.777%、`ASAP7 UART K=36` 19 门 −0.623%／−2.234%／−1.391%（总／组合／漏电，均降）；UART-TC 端点三角 Setup 255.927／190.381／28.931 ps、Hold 50.315／67.502／54.054 ps 且仍严格 Timing-closed；7 nm `asap7/aes` 受控非零 DRC 窗内 5 例 37 marker，TP/FP/FN = 37/0/0、marker 与网集合逐例相同、均值提速 17.34×，另 1.05×$H_{\mathrm{row}}$ 窗外负对照 2 marker 仅全块可见（作用域边界）；两设计 3× 重复完整 DRT+RCX+STA 去日期 SPEF 逐字节一致、WNS 极差 0.000 ps（该 3 门批次本身为 `SS:hold_regression` 拒收，结论仅限产物与判据确定性）。
- **Stage 2A 实测**：`asap7/uart` 同窗口 720 s，`dedup_off` 0.83106 µm²／AUC 0.4344／20 次评估／634.6 s，`dedup_on` 0.83106 µm²／AUC 0.4764／19 次评估／1 次命中／588.0 s。
- **Stage 2B 第一遍实测（240 s 单次路由预算）**：`sky130hd_aes` 120 项与 `sky130hd_riscv32i` 24 项四臂均 `rejected`，原因为触及 240 s 路由上限而非时序判定；`asap7/uart` 16 项与 `asap7/aes` 174 项判为 `not_in_action_space`（原生改到 ORFS 端口缓冲实例，不在冻结 runner 的 `ref_masters` 内）。
- **脚本修正（实现层，未改科学设定）**：sky130 `FF`／`SS` liberty 路径、`worst_slack` 按 liberty 时间单位的换算、7 nm 受控 DRC 改为合成 aggressor 注入（原 `dbWireEncoder` 会重写既有走线）、Stage 1.4 试验目录与 `initial_hint`、Stage 2B 目录／`qualify_zero` 目录／动作空间分类／600 s 第二遍、Stage 3–4 `initial_hint`、Stage 5 的 ORFS 目标名与 liberty 复用。逐条见 [执行交接 §3](../HANDOFF_2026-11-26_V5_EXEC.md)。
- **预检与启动器（沿用）**：`smoke_verify_v5.py` 通过并落盘 `V5_PREFLIGHT_PART1_AUDIT.json`（SKY130HD AES 非单调反例 $T_3 \subset S_{18}$、4/4 Hybrid 检查点 $\le 720.00\,\mathrm{s}$）。
- **5 阶段定义与一键启动器**：`project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh`（独占 `taskset -c 0-5`，支持 `--stage 1..5|all` 与断点续跑）：
  1. Stage 1 (`run_v5_step1_power_7nm_det.py`, ~5–8 min)：Hybrid 18g / UART-TC / UART K=36 功耗与 6 角 WNS + 7 nm `asap7/aes` 5 组受控非零 M1/M2/M3 短路/间距 DRC + 4 线程 DRT+RCX+STA 3× 重复确定性；
  2. Stage 2 (`run_v5_step2_dedup_and_native_protected.py`, ~15 min)：`asap7/uart` Setup 去重开/关独立消融 + 四设计原生 `recover_power` 挂载 FAECO $1.0H_{\mathrm{row}}$ 保护后端解耦；
  3. Stage 3 (`run_v5_step3_multibudget_online.py`, ~45 min)：`asap7/uart` & `sky130hd/aes` 四档 Setup 预算（0/0.5/1/2%）独立在线搜索；
  4. Stage 4 (`run_v5_step4_probe_sensitivity.py`, ~40 min)：双 AES Hybrid 探针子预算 $\tau_{\mathrm{probe}}\in\{0,60,120,180,240\}\text{\,s}$ 五点敏感性；
  5. Stage 5 (`run_v5_step5_10k_timing_closed.py`, ~35 min)：全新 ORFS 从头构建的万门级独立 Timing-closed 基准 `SKY130HD riscv32i-TC @ 10.0 ns`（显式 Timing-closed 硬门控）。
- **交接与说明**：[HANDOFF_2026-11-26_V5.md](../HANDOFF_2026-11-26_V5.md) · [V5 目录 README](tcad_v5_revision_20261126/README.md) · [离线预检收据](tcad_v5_revision_20261126/V5_PREFLIGHT_PART1_AUDIT.json)

#### TCAD-V5-REVISION-SUITE 续跑预登记

- 继承 `dd18120f6db836d2d3fe8d14e0761900652342f3` 已落盘的 Stage 1 与 Stage 2 第一遍，原收据 SHA-256 分别为 `85bfc1657fbc0663649e417abbe7a9c9827d7d1cded05c121133bd150f28a235`、`917a665550f695198148cd428f3ec56149fa4f8596121db358367724000c95e8`。硬件及原件路径沿用[执行交接](../HANDOFF_2026-11-26_V5_EXEC.md)。同一 Bazel 构建的 OpenROAD，实验作业串行绑定 WSL CPU `0–5`，各阶段监测日志与收据，按键跳过已完成臂。
- **Stage 2B**：SKY130HD AES、riscv32i，原生标准与允许 setup 违规各一臂。单次路由上限 600 s，外层 840 s；同冻结参考与 $1.0\times H_{\mathrm{row}}$ 保护后端。先核原生实例到冻结网表的唯一映射。若全动作可绑定，才按物理门与 SEC 判定。路线超时、动作不兼容、完整物理门拒收分别登记；只有完整过门且实际交付支持合格回收。22:45:27（UTC+08:00）开始四臂串行续跑，外层启动器上限 8000 s，沿用 CPU `0–5` 并持有 EDA 互斥锁。续跑脚本 SHA-256 `d7fda4e8c43515783a9be9f64b336ab918affd2d0fb9280bbc8499c085d89b7d`，新原件按 `mode::rt600s/attempt_*` 分开保存。 AES 原生完整 120 项在名称绑定通过后确认有一个 DFF 触及 CLOCK 网，归后端作用域不兼容。追加 119 项仅数据网投影的两臂，使用相同 600/840 s 设置和独立 ::signal_only 结果键。保留完整原生结果为独立类别。 四个 600 s 完整提议键已齐并独验旧十项不变，完整提议快照 SHA-256 ae4c5329fbcba39a974a71f4cee6b283ad614057a316a7bda9fc4e901c497f5e。AES 两臂为作用域不兼容，riscv32i 两臂因单次 DRT 到限未形成物理判定，AES 119 项投影两臂也均因单次 DRT 到限结束。最终收据共 14 个原生键和两条去重臂，SHA-256 b6ef9577384fdabe88f6b82baabfa9344a98f726c9881e6c1e7e5334e8963da4，与前次四键快照比较旧键内容一致。
- **Stage 3**：ASAP7 UART、SKY130HD AES，同 720 s 计费窗内分别在线搜索 0%、0.5%、1%、2% Setup 预算。逐档核对起点、候选池、Setup 与 Hold 拒因、端点是否新增负 Setup 及签核。预算放宽扩大静态许可范围，但搜索路径可变，若实测回收不单调，保留结果并核对派发与墙钟轨迹。1% 对照只在起点、策略与计费协议对齐时比较。修复后的逐角 Setup/TNS 生效门离线分叉与错误周期反例均通过，23:52:37 已从 ASAP7 UART 0% 档串行开跑，CPU 0–5、EDA 互斥、每臂 720 s，外壳上限 12000 s 及 60 s 清理。 已实测完成 UART 0% 档，回收 0.32076 µm²（5/18），原三角 WNS/TNS 零损失预算与配套容差，SEC 567/0。UART 0.5% 档也已完成，0.77274 µm²（12/18）、AUC 0.442559 µm²、21 个完成评估、SEC 567/0。UART 1% 档复现 0.83106 µm²（13/18）、AUC 0.496827 µm²、19 个完成评估、SEC 567/0。2% 档已完成，19 个评估、0.83106 µm²（13/18）、AUC 0.504324 µm²、SEC 567/0。1%/2% 的派发顺序与拒因及终态物理产物相同。UART 四档快照 SHA-256 ed73ba28dfba163e554aa17370bcbdf9410b6a73ef390d7b5d0c203542314370。SKY130HD AES 0% 已开。
- **Stage 4**：SKY130HD 与 ASAP7 AES，同 720 s 窗内新测 60/120/240 s 探针子预算。0/180 s 从既有收据导入并标来源。仅完整签核且在计费窗内的检查点计交付；分别读取探针通过、物理拒收、子预算截停及回退首达/AUC。失败探针若延后交付或降低 AUC，记录探索代价。导入绑定历史收据和序向，ASAP7 AES 旧默认子预算为 169.1196825123001 s。续跑脚本 SHA-256 db1d92385bb4e6995a6047487d0189a38214436a06838e5d9a68d92a0ec9d709，离线反例与中断恢复路径合计 5 项通过。
- **Stage 5**：SKY130HD riscv32i，独立 ORFS 从头构建，目标周期 10 ns，`route finish` 构建预算初设 1800 s。确认历史 6 ns 的已存 SDC 缺输入延迟；新构建完整保留 10 ns 时钟和 20% 周期（2 ns）I/O 延迟设置，显式纳入全部非时钟输入和输出。先运行 reference-only，等 Stage 2 释放 EDA 锁后串行优先进行独立起点硬门反证，外壳限时 2800 s。ABC 合成目标显式用 10000 ps，核验 ORFS clock_period.txt；旧起点的 ABC 原件记录为 6.0。23:41:57 接锁开始构建，实际 10 ns 新任务的 clock_period.txt 已记录 10000。ORFS 528.958 s 完成（rc0），65 输入/99 输出全部 2 ns。CONTROL SHA-256 b8522af55121f1fc0a4d2a66fc8900a6a92c9849373b40e2c7ba7faa8144e73a 给出 SS Setup/Hold 负值，原 10 ns 起点资格未通过、零候选臂测试。已保全 V5_STEP5_TC10NS_QUALIFICATION.json 并用原 SS 日志定位最差 Setup 涉及输入路径，最小松弛违例为异步 reset removal。须先见 FF/TT/SS Setup/Hold 均非负的独立严格时序收敛参考点，再以同始点、同 720 s 窗跑单门、固定批和 FAECO 三臂。零回收按构建资格、在线截停、路由/DRC、时序/SEC 分类。任何已交付端点出现负 Setup/Hold 即推翻保持严格时序收敛的主张。

- **Stage 5 替代独立参考（tc40ns_mmmc）**：10 ns 资格反证后登记 40 ns 新综合、布局和布线，两个方向 I/O 均保持 2 ns 的绝对延迟，保留 reset removal。ABC 40000 ps、CORNERS=tt ss ff，Setup/Hold 修复目标余量 0.50/0.30 ns；CTS/GRT 的真实日志需证明角库与两类修复调用，三角资格共用名义布线提取 SPEF。等 Stage 3 放同一 EDA 锁才开始，等待上限 12100 s，实际外壳 3100 s，构建上限 1800 s，CPU 0–5。脚本 SHA-256（参考）2e2a49ef45fbaf5430034b821b178393f99b86f01aa5961b590e9a63c31e398e；（候选和 CLI）d1fc0317f77832d804dcf8be9e596ccfb4a4a873ecae7ed368f0d94c094a379f。原 10 ns 参考及原件保全，候选臂仍受新参考资格门。
