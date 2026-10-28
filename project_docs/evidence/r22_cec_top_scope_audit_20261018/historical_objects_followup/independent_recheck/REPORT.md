# P08 现存对象独立复算

客户端日期：2026-10-18。实际 UTC、脚本身份及输入身份见 `run1/RESULT.json`、`INVOCATION.json` 和 `FINAL_RECEIPT.json`。

这是本次新写并完整保存的独立 checker 对现存证据的只读复算，**不是历史 PowerShell stdin 的恢复件**。新 checker 不导入项目源码，不调用 EDA、仿真、测试或 Git。180 秒超时包装实际约 6 秒结束，退出码 0；完整原始输出保存为 `RUN.log`。

| 核验对象 | 本次实际结果 |
| --- | --- |
| 已列 15 份旧 CEC 原始日志及其 30 侧 BLIF | 13 份有实际 `Networks are equivalent` 结果行，且双侧各只有一个 model；另 2 份有明确模型读取失败，均无 equivalent 结果行。逐份从 raw log 解析 CEC 命令并绑定保留对象路径。 |
| flow_probe formal | 双侧各 378 个 model；日志实际缺 `$mul` 并读取失败。没有把邻接 baseline 的成功挪用于此对象。 |
| EPFL ctrl mapped CEC | 实际缺 clkinv 模型；summary 为 error，尽管工具 rc=0。mapped BLIF 的当前 SHA 与 mapping_report 一致。 |
| s27 旧 A 复用 SEC | 实际脚本 rename→equiv_make→`prep -top equiv`，日志顶层 equiv、11 proven / 0 unproven 和成功输出。 |
| s820 旧 A 复用 SEC | 同一显式顶层流程，日志 137 proven / 0 unproven 和成功输出。 |
| 两份 A/B 身份绑定 | 按电路 module 提取、去空行并去行首尾空格比较，gold top 等于 A initial，gate top 等于 A fixed final，也等于 B outerloop actual state top；state 全文本 UTF-8 SHA 与记录值一致。旧脚本只有 equiv_status，无 -assert。 |
| 来源保真 | 原 104 文件清单的 SHA/size 与当前全部匹配；加上 5 份审计控制文件，本次共 109 文件读取前后 SHA/size 完全一致。 |

checker 从原审计取待核路径集合，独立解析日志实际结果行、CEC 命令、BLIF `.model`、引用以及脚本/状态文本；没有从旧 verdict 字段推导上述计数。完整逐对象复算在 `run1/RESULT.json`。

可重跑命令的 argv、工作目录和日志重定向记在 `INVOCATION.json`。再次执行必须使用新的 `--output` 目录和新日志；脚本拒绝复用输出目录，以保留本次原件。

## 持续未知与范围

原最终适配的 stdin 字节和同期 stdout 仍未恢复，`reproducibility_supplement/RECOVERY_RECEIPT.json` 中的 unknown 不变。本次新脚本不会补成历史原脚本，也不会补出旧输入/归一化 BLIF 同期 SHA 收据或当时源 commit。当前日志路径和文件身份对应不能排除历史覆盖。

13 是已有 proof 对象数，不是新实验数或独立科学案例数。单 model 只排除了这些现存成功对象的多根首模块条件；本轮没有重新验证模型语义、四态、初始化、历史候选身份或科学效果。未重审 81 份新 proof；其它命名、缺失或版本归档对象继续 unknown。P08/OI048 历史影响门保持开放，旧报告、原始证据和旧收据均未修改。
