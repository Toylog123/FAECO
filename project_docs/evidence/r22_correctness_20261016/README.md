# r22 当前实现正确性恢复（2026-10-16）

从main/781c031恢复，第一阶段8192193已push。当前P0是实际Lib三态语义与证明器能力边界；A6已真实补证，B2/B3与D/C仍待。没有STA/pilot，当前稿不是科学定稿。

## 实际验收与诊断（各对象分开）

| 证据 | 实际结果 | 边界 |
|---|---|---|
| full_regression.json/.log/.xml | 741pass/1fail/4skip/156subtests，108.20s，wrapper112exit1，源码稳定 | 合法B声明分组合并被文本比较误拒；原件保留 |
| full_regression_v2.json/.log/.xml | 757pass/4skip/156subtests，102.50s，wrapper107exit0，162Python源码/fixture SHA稳定 | 8192193阶段真实通过，不覆盖后发现的三态反证 |
| full_regression_v3.json/.log/.xml | 822pass/2fail/4skip/156subtests，144.12s，wrapper147.735exit1，165SHA稳定 | 两CLI fixture缺dfrtp模型/RESET_B被正确拒；仅补真实fixture、保留assert，CLI fixture全9pass后完整v4在跑/166beforeSHA，子CLI编码3F已定位；等结束保留再显式PYTHONUTF8=1完整v5 |
| sec_controls/controls.json | 6expected全匹配：3正pass/3负fail，source_stable=true，wrapper15exit0 | 常量/全加器/enable FF真SEC；不是三态Z soundness认证 |
| tristate_tool_diagnostic/diagnostic.json | dirty首5组：2pass/2fail/1input_error均matches，source稳定，wrapper20exit0/0timing | 首组不能认证工具Z语义 |
| tristate_z_diagnostic/diagnostic.json | Zvs0应fail却pass，Zvs1 fail符合；passed=false/source稳定，wrapper11exit1/0timing | 当前Yosys默认Z塌缩，OI039工具soundness阻断，不据前组放行 |

原v3 log含CP936混编码，harness结束UTF8展示报UnicodeDecodeError；原JSON/JUnit/日志完整保留，不能把展示失败说成回归未结束。后续Python使用-Xutf8。

当前完整v4已结束：832pass/3fail/4skip/5warn/156subtests、148.38s/wrapper152.968exit1、166SHA稳定；3F为父UTF8/子CP936环境。源码未变，v5已实际running/166beforeSHA，JSON记录PYTHONUTF8=1传全children，尚无最终结果。phase2_tdd/58文件source/target/manifest SHA已逐条核验匹配，原失败完整保留。

当前最终完整v5已通过：**835pass/4skip/156subtests，147.00s，wrapper152.781s/exit0**，166来源before/after SHA一致/source_stable=true，environment_overrides PYTHONUTF8=1，JUnit0fail/0error。原v4环境失败及此前各次证据保留；这是当前实现验收，不是科学证据全部闭合或三态支持完成。记录冻结供阶段commit/push，新pin待实际完成。

下一阶段新pin9正式控制（3正pass/3负fail/2unsupported/1input_error）、B2+X identity证书、C′v3实际mapped复查后18pilot→72、D56预飞56/56后14pilot；均未STA/pilot。unsupported仅临时证明器能力门，显式四态编码恢复路径open。

## 已完成的实现阶段

- K1各组合输出模型、常量与enable FF真实状态语义；K2实际Lib输出方向、一物理实例一Gate、所有输出驱动/锥外边界/split互斥；K3 CLI明确top再查D。
- K4/K5非目标assign/端口/wrapper保护、既有net宽度/符号/维度/声明次数与合法B重组、重复物理实例拒绝；K6 RGB/S均提交前按top+Liberty刷新，失败硬F2且不提交。
- 独立SEC使用module_spans忽略注释/字符串假module、helper不变门；三态完整metadata/联合data-enable候选语义/必需输入门已落盘且限定相关测试通过。
- 后缀反相转换后actual13个三态/52binary行writer静态检查通过；准确writer保留。INTEGRATION_REVIEW与TRISTATE_INDEPENDENT_REVIEW保留各轮源码身份、反例和独立范围；tdd_logs/及scratch日志中的限定数量不能相加冒充整套。

## 当前证明能力门与科学证据

当前二态cut组合方案被独立Z^Z等反例推翻，不实施。final_sec/fullchecker对actual三态cell、显式Z/switch给structured unsupported非pass，这是临时证明器能力门；显式四态编码是支持恢复路径，三态真实语义支持仍open，不能声称三态已证。domain红5→绿16含scope，扩展11pass；原Zvs0/1精确输入的guard核验均unsupported/command=None/source_stable=true，只是拒绝门、不是四态证明。完整v4运行中/166beforeSHA，父-Xutf8未传子CLI造成3编码失败；独立3fail+4warn→PYTHONUTF8=1的3pass。源码不改，等v4结束保留后v5显式环境。

A6在 `../r22_a_sec_20261016_frozen/` 已用8192193模型/source pin真实SEC六pass，wrapper21exit0；TRISTATE_IMPACT_CHECK逐pair三态交集为空。s713原LF与proof raw CRLF差经逐字通用换行核查，实际对象未改；历史runtimehash不补造。

B模型审计见 `../r22_b_model_audit_20261016/`：旧28对象绑定仍真，23未见本次used-model defect、5有缺口（Pico2错误edfxtp模型/OI038；b09/b20/b21缺TE_B及三态模型/OI039）。不据缺口判电路不等价。B2新模型实际proof、B3合法候选恢复/证明、D/C同族恢复及双语稿图回填仍待。

## 下一步门与目录

补完整CLI fixture及临时能力门后，冻结新版完整v4与独立汇合，再commit/新source pin。B2计划raw、D56保留输入/共享canonical8的已存输入三态交集空；C′v2八prospective mapped不存在，仍unknown，不能外推未来候选。

C′ `experiments/20261016_r22_cut_ablation_v2/manifest.json` 仅注册72jobs，已知缺陷pin禁执行、不覆盖原manifest；新源码另建v3，仍须18pilot全部通过才扩72。v1失败原件、历史证据、失败完整回归与诊断原件均保留，输入/库变化必须停。没有STA/pilot运行。

D56_ACTUAL_CLI_PREFLIGHT.json为全56真实parse_args内存预飞：每argv与历史expected resolved_args逐字段比，56/56无mismatch/source_stable=true/eda_executed=false；不是D56真实实验。脚本scratch/check_d56_actual_cli.py及其SHA已登记，待晋级归档。
