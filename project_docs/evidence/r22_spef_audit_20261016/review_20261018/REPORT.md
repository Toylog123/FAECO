# SPEF 历史证据独立复核（2026-10-18）

旧 `audit.json` 保留原件，本包只新增审查。没有执行 STA、SEC、ABC，没有改生产、论文或图件。详细逐对象结果与源文件 SHA 复核见同级 `REVIEW.json` 及 S 审查包 `../../r22_s_model_audit_20261016/review_20261018/V2_REVIEW.json`。

## 已确认事实

| 历史对象 | 实际记录 | 不能据此声称 |
|---|---|---|
| s382_big F6 | 50 条拒绝记录，5 个独有候选 SHA；周期 0.5 ns | 50 个独立候选，或当前完整物理门已恢复 |
| b18_light F6 | 6 条拒绝记录，1 个独有候选 SHA；周期 13.15 ns | 6 个独立候选，或和论文 ITC 0.5 ns 族混用 |
| b18_light RC | 6 份 retained SPEF 与当前生成器 unit_len_um=1 的全文换行归一后相等；unit=40 不相等 | 把 40 µm/unit 笼统用于这 6 条 F6 |
| s382_big RC | 50 份 SPEF 对 unit=1 与 40 的现生成器均不全文相等 | 猜测当时 RC 参数；需要恢复旧实际生成器/参数后再定 |
| s382 scan | 9 个 RC 点，确切另一对输入；repaired 日志每点有 `_071_:SLEEP not found` | 用 scan 给 gate 的 5 个候选补物理结论 |
| b18 scan | 10 个 RC 点，13.15 ns；初始 SHA d2afb836… / JOINT 终点 SHA 8ddf669f… | 用这对输入替代 b18_light 初始/单 R 候选 |

所有 19 个 scan 点均让 baseline/repaired 共享同一个 baseline SPEF。scan 的 u40 记录表明各自历史 ideal gain 在该 RC 下变为 0，但 s382 有实际 pin 漂移告警，尚须连接正确的同族复测。未将旧数值重写为新结果。

## 已证实的当前实现问题与最小复现

1. **driver 固定白名单漏 SUM 等输出。** `code/src/rseco/spef.py:10` 和 `MappedNet.driver():24` 使用硬编码输出名。`MappedNet('n', (('u','SUM'),('v','A')))` 的真实 SUM driver 被返回 None，`build_spef` 写 `*I u:SUM I`、没有 u→v 电阻支路。新静态探针 `V2_SPEF_MINIMAL_PROBE.json` 保留输入与完整输出。历史 b18_light 的 `_649725_` 确由 xor2.X 改为 ha.SUM，retained SPEF 原件也正如此误标；它不是仅对未来可能输入的担心。修复应基于实际 Liberty pin direction 并保留每条输出，不用再扩一个有限白名单应付。
2. **baseline SPEF 复用于换 pin 的 repaired 网表。** `code/scripts/run_parasitic_aware_check.py:87–96` 只解析 baseline、生成一份 estimated.spef，再传给 repaired。s382 retained 日志直接报缺 SLEEP pin，确认连接不匹配。修复为两侧各自生成 SPEF，共用明确 RC 参数；若宣称固定物理拓扑，应显式校验合法端点映射并为新增/删除 pin 正确重接。保存 netlist/连接/RC/SPEF 的逐侧 SHA。
3. **同一次物理 STA 输出混入 ideal path report。** `code/src/rseco/opensta.py:263–266` 在 read_spef 前执行首个 report_checks；随后最差 slack 才在注入寄生后报告。`:308` 的首个 slack regex 取到 ideal path slack，WNS 来自注入后的报表。`OPENSTA_ORDER_PROBE.json` 在 resolver 返回缺失工具、subprocess 被禁的环境中实际调用生产函数生成 Tcl，确认顺序且外部进程 0。历史 56 份 gate Tcl 也如此；不能把所有字段都称为物理测量。该问题未证明当前 WNS 接受判据本身错误，但确使 path/slack 来源混杂。最小修复把 read_spef 放在所有 timing reports 前，并用不同 ideal/physical 值的控制验证解析来源。

## 修复与同族复验门

| 顺序 | 必须推进的工作 | 验收 |
|---|---|---|
| 1 | 修上述三个当前实现问题；补 SUM、多输出、端口和换 pin 反例 | 红→绿，实际 Liberty pin direction、全连接集和生成 Tcl 检查；源码冻结后整体回归 |
| 2 | 先合法 s382 小例 pilot，各侧同 RC 各自 SPEF | 独立 SEC、F1/F2、没有缺 pin/未知实例注入；输入、Lib、RC、SPEF、Tcl、日志 SHA 对应 |
| 3 | 同族 s382_big / b18_light 重新登记候选与 gate | 分开报告 5/1 独有输入、50/6重复评估记录；恢复原周期与可识别 RC，不借 scan 终点；每次真实过程分账 |
| 4 | 独立重验 scan 的两对输入及 RC 点 | baseline/repaired 拓扑各自正确；保留所有不利点；无法恢复旧 RC 的 s382 gate 另作显式新设定，不伪造历史恢复 |
| 5 | 同步论文 SPEF 设置、拒绝计数和解释 | 不把工具估计写成实际布线；数据到中英正文/表图逐项交叉校验 |

**unknown 继续保留：** 历史缺少运行时输入 SHA/完整环境身份；retained 字节不是当时执行字节证书。旧独有报告数与重复记录数可核，不等全部过程启动次数。s382_big 的 1/40 µm 不全文相等并不证明方法无效，也不能自动归因 RC 参数；须先恢复实现、参数和对象。静态 domain/required-input 通过不是新功能证明。SPEF 570 条旧来源只有 LOGS 上下文更新，其余 SHA 一致。
