# r22 当前实现与证明证据 — 2026-10-16（LOG-36）

当前完整v8：**969pass/4skip/156subtests，155.12s/wrapper157.969exit0，170来源before/after SHA稳定，PYTHONUTF8=1**；JSON/JUnit/log实读，JUnit0fail0error。原始精确V3正确拒reset→set、合法Gpass、R0、parsed1/1，公共scope30pass。OI040/041实现门已闭合，科学范围不泛化。

当前main/origin仍ddb4c33，代码修复阶段commit待；records停写供root归档harness/更新根入口与commit/push。随后同一HEAD注册C′v3→真map8/静态门→18pilot全过才扩72，不再加前置工具。当前v3未注册、无mapping/STA；B3/C ADAPTER WIP不纳此次commit。

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
