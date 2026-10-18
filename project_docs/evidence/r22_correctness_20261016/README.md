# r22 当前实现与证明证据 — 2026-10-16（LOG-20261016-53）

当前完整v8：**969pass/4skip/156subtests，155.12s/wrapper157.969exit0，170来源before/after SHA稳定，PYTHONUTF8=1**；JSON/JUnit/log实读，JUnit0fail0error。原始精确V3正确拒reset→set、合法Gpass、R0、parsed1/1，公共scope30pass。OI040/041实现门已闭合，科学范围不泛化。

当前main/origin固定3ea0f757f5e9bab4a2df75c458b0c665eabcb258，完整v8=969pass/170源码SHA稳定，OI040/041实现门closed。C′v3 72jobs/manifest72dfbef9…/44source已注册，8例实际mapping/static准备与后验全过（非RTL→mapped等价证明）。18pilot已completed，wrapper1028s/exit0；PILOT_AUDIT_18实际18/18独立核验通过/all_pilot_verified=true/source稳定，全部argv、candidate raw/tcl/log SHA与STA ledger、提交哈希链及finalSEC非零proven/0unproven匹配。首18合计1360候选评估记录、1064 candidate_ideal STA+18baseline=1082实际STA过程、other0、保留提交35；physical/electrical/S均false，不称物理STA。剩余54已实际启动session9345（s420/s641/s713/s820/s832/s953×9，整体108000s、单job3900/3930s/wall3600，PYTHONUTF8=1），最新MATRIX_AUDIT_51由v2（SHAea0a9793…）在开始冻结eligible pair+completion SHA并结束复核，51/72独立通过/source稳定/all_matrix_verified=false。实际s27/s382/s420/s641各9+s713七臂+s820八臂；51范围5887候选评估、4919candidate_ideal STA+51baseline=4970实际过程/other0、137保留提交，physical/electrical/S=false。原log名字v2_50不代表count，以receipt51为准；v2 script/log/51新stage51原件保真归档，旧36不改。s27/s382/s641完整归档已root后验接受；s420全归档已session34681/900s实际启动、验收待。当前运行仍固定3ea0f75，不称全72完成。完整72验收前保持HEAD不commit；B3/C适配器可独立review/QA但不占STA，提交等72全部验收。首18验收不是全72效果闭合，不跨族补旧B3/C/D科学缺口。

当前接受协议为严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不意味着关闭setup_tns预算。W0/s27首候选WNS -.27→-.26但TNS -.49→-.50，被setup_tns硬门拒。零提交/零WNS收益如实保留，不为正结果调参。最终审计分开理想候选、baseline/refresh/physical STA与提交。

## 各轮完整回归保真

| 前缀 | 实际结果 | 归因/范围 |
|---|---|---|
| full_regression | 741pass/1fail/4skip/156subtests，108.20s/wrapper112exit1 | B声明分组合并误拒，原件保留 |
| v2 | 757pass/4skip/156subtests，102.50s/wrapper107exit0，162SHA稳定 | 第一阶段真实通过，不覆盖后续新反例 |
| v3 | 822pass/2fail/4skip/156subtests，144.12s/wrapper147.735exit1，165SHA稳定 | CLI旧fixture缺dfrtp/RESET_B，补真实fixture保留assert |
| v4 | 832pass/3fail/4skip/5warn/156subtests，148.38s/wrapper152.968exit1，166SHA稳定 | 父UTF8/子CP936，源码不改；原件保真 |
| v5 | 835pass/4skip/156subtests，147.00s/wrapper152.781exit0，166SHA稳定 | 全进程PYTHONUTF8=1；未覆盖后来seq新反例 |
| v6 | 926pass/4skip/156subtests，155.08s/wrapper157.875exit0，168SHA稳定 | 多行seq子门通过，原单行例仍漏解析，不能冒称原例解决 |
| v7 | 965pass/1fail/4skip/156subtests，155.08s/wrapper158exit1，170SHA稳定 | F1 named-pin覆盖误扩公共唯一性门，合法topology positional误拒 |
| v8 | 969pass/4skip/156subtests，155.12s/wrapper157.969exit0，170SHA稳定 | 公共门连接提取opt-in/F1严格覆盖保持，当前实现完整验收 |

完整前缀为full_regression_v<N>，各json/xml/log原件不覆盖，限定数量不合计为整套。v3混编码展示失败未损坏JSON/JUnit。source/输入变化需新冻结。

## 反例与实现修复

K1–K6的模型/多输出物理身份/graph-cut边界/CLI top/非目标行为与重复实例/提交前刷新、module_spans/helper不变和required-input已完成代码阶段验收。

SEQUENTIAL_GATE_COUNTEREXAMPLE在旧源码同时混有seq语义和单行parser缺陷；旧多行独立反证证明seq缺陷不依赖漏解析。原失败VERIFICATION保持false，新V2/V3保独立source/verifierSHA，V3精确原始单行两物理FF可见并正确拒。LR不让seq进组合R；F1完整seq组/角色与物理↔parsed覆盖；共享唯一性门默认不提连接、仅F1显式True保合法positional。graph原63seq边界正确未改。

actual13三态writer/联合data-enable/后缀反相静态检查不代表工具四态能力。dirty首5matches被Zvs0伪pass推翻，二态cut另被Z^Z反例推翻未实施。actual三态/Z/switch structured unsupported是临时能力门，准确writer保留；显式四态编码恢复路径/OI039仍open。6statetable原writer不支持failclosed，不扩模型支持。

## 真proof与控制

- sec_controls_phase2：02e82a2正式9预期全符合，3正确pass/3故意错fail/2unsupported/1input_error，wrapper31exit0/source稳定，后验44source/LIB/driver无漂移。不是9个等价证明或三态支持已证。
- A6：frozen8192193实际原mapped→accepted fixed六pass，wrapper21exit0，逐pair三态交集空；s713 LF/CRLF经逐字decoded绑定，旧runtime身份不补造。
- B2：44d20bb真实新模型双pair pass，core6.078s+7孤立constant-X identity/mul0.750s+0X，wrapper16exit0/source稳定。原bytes/完整decoded/artifacts/动态cert后验一致；checker20负拒/5of6正接受，保守escaped output误拒不影响actual B2，范围非任意四态/复位等价。OI038新模型缺证恢复，旧模型缺陷/runtime限制不追认。
- B17：ddb4c33实际接受raw的完整模型flatten/assert新proof12879proven/0unproven、13.375s。root后验原bytes/完整decoded/唯一nor4b尺寸变化/artifacts/44source全匹配；旧无statehash不补造，旧find_same_wires note不作为已证归因。
- proof_model_preservation：A6+B2+B17九份实际models重生成9/9字节一致/source-LIB稳定，非外部重新证明；各精确proof保原pin。

## 归档与执行边界

phase2_tdd58、phase2_final_qa15、Cprep qa5、sequential_integration_qa10、f1_scope_qa3各自manifest原件保真，旧manifest不覆盖。f1_scope绿30pass仅tool回显NOTE，原绿stdout未保存不补造。QA脚本原scratch相对路径上下文保留，直接跑归档副本可能只路径失败；在原位或新副本适配并另锁SHA，不改原件。

Cprep evidence-only准备器已审，当前源20控制通过；不是RTL→mapped等价证明。D56实际parse_args与historical resolved_args逐字段56/56无mismatch/source稳定/无EDA，不等D实验已运行。B3/C只读恢复设计execution_ready=false，argv/source/priority等未知不默用defaults/不换调度，ADAPTER仍WIP不纳此次提交。

当前未注册C′v3/无STA；C′v1失败/v2仅注册禁执行均保留。B3/C/D科学恢复、四态支持与双语稿图/声明仍pending，但不阻碍当前已验证域按预锁矩阵执行。
