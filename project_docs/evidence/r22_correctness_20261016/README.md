# r22 当前实现与证明证据 — 2026-10-16（LOG-25）

用户10-16恢复后，代码当前835整套通过，正式9控制预期全符合；A6与B2真实补证已完成。当前main/origin44d20bb，166代码来源自v5未变。B3/D/C与四态支持恢复、稿图仍待；无STA/pilot，新矩阵尚未注册。原发现/失败不覆盖。

## 完整回归对象

| 文件前缀 | 实际结果 | 归因/边界 |
|---|---|---|
| full_regression | 741pass/1fail/4skip/156subtests，108.20s/wrapper112exit1 | 合法B wire声明重组误拒，实现修复；源码稳定 |
| full_regression_v2 | 757pass/4skip/156subtests，102.50s/wrapper107exit0，162SHA稳定 | 第一阶段8192193真通过，不覆盖后来三态反证 |
| full_regression_v3 | 822pass/2fail/4skip/156subtests，144.12s/wrapper147.735exit1，165SHA稳定 | 旧CLI fixture缺dfrtp/RESET_B被正确拒；补真实fixture保留assert |
| full_regression_v4 | 832pass/3fail/4skip/5warn/156subtests，148.38s/wrapper152.968exit1，166SHA稳定 | 父UTF8/子CP936环境，源码不改；原件保真 |
| full_regression_v5 | **835pass/4skip/156subtests，147.00s/wrapper152.781exit0，166SHA稳定** | environment_overrides PYTHONUTF8=1传全children，JSON/JUnit/log实读，提交前被测SHA再核 |

各前缀json保存命令/版本/before-after SHA，xml/stdout原件保留。v3混编码log的UTF8展示异常未损坏JSON/JUnit，不抹掉真实失败。限定红绿数量不相加充当整套。

## 模型与能力控制

- sec_controls/：8192193的6控制3正pass/3负fail预期匹配，wrapper15exit0/source稳定。
- dirty tristate_tool_diagnostic/首5matches被tristate_z_diagnostic/的Zvs0预期fail实际pass推翻；Zvs1 fail符合，source稳定/0STA。二态cut又被Z^Z等独立反例推翻，未实施。
- tristate_guard_verification/：原强Z输入均unsupported/commandNone/source稳定，只认证拒绝门，不是四态证明。
- **sec_controls_phase2/**：02e82a2正式9预期全匹配，3正确pass/3故意错fail/2三态unsupported/1input_error，wrapper31exit0/source稳定；POST_RUN_VERIFICATION后验44source/LIB/driver无漂移。不能称9个等价证明通过或三态已支持。

当前actual三态/显式Z/switch是structured unsupported非pass；准确writer保留，actual13三态/52行静态导出已核。临时二态证明器能力门不代替真实三态支持，显式四态编码恢复路径仍open（OI039）。

## A6、B2与独立审查

A6在../r22_a_sec_20261016_frozen/用8192193来源/模型对实际原mapped→accepted fixed真实六pass，wrapper21exit0，各pair三态交集空；s713 LF/CRLF字节差经通用换行逐字一致，不补旧runtime身份。

B旧模型审计../r22_b_model_audit_20261016/保留初审23未见本次used-model defect/5有缺口。随后44d20bb的new_model_proofs/真实双pair pass：core6.078s+7孤立X identity、mul0.750s+0X，wrapper16exit0/source稳定；POST_RUN_VERIFICATION原bytes/完整decoded/artifacts/动态cert双pair均匹配。OI038新correct模型实际对象缺证已恢复，旧模型缺陷/runtime身份不追认不补造。

B2_X_INDEPENDENT_REVIEW.md/.json等绑定checker66fe72ff…：20/20负拒、5/6正接受，escaped output保守误拒不影响actual2pair；独立scanner另8负控制。范围仅two-state SEC加独立孤立constant-X identity，不泛化四态/复位等价。INTEGRATION_REVIEW与TRISTATE_INDEPENDENT_REVIEW保留其它作者代码审查、每轮SHA和反例范围。

## 归档、预飞与下一步

phase2_tdd/58文件与phase2_final_qa/15份新增/修订QA分别有独立ARCHIVE_MANIFEST，记录员source/target/manifest SHA实际逐条核验58/58和15/15。原58不覆盖。phase2_harnesses/保留实际调用脚本及manifest。D56_ACTUAL_CLI_PREFLIGHT.json真实parse_args逐字段56/56无mismatch/source稳定/无EDA，不等D实验运行。已存B2/D56/canonical raw空三态交集不外推缺失的prospective mapped/candidate。

当前proof/QA/docs准备阶段commit，新矩阵尚未注册。随后C′v3新pin/实际mapped复查→18pilot全过才扩72；D先14pilot，B3/C同族恢复只读报告进行中，不把半成品当结论。C′v1失败/v2仅dryrun禁执行，原件不覆盖。无STA/pilot，不写论文/图定稿。
