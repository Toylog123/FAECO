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
