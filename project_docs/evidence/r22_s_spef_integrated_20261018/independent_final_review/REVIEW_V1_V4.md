# S/SPEF 集成证据独立 QA：v4 完成后的补验

客户端日期：2026-10-18。范围为保留证据完整性；未重跑测试、工具、正式 EDA 或 Git，未修改生产和原始结果。此前 REVIEW_V1_V3 原件保留。

v1–v4 各 173 份 Python 源码的 SOURCE_BEFORE 与 AFTER 全部相同；四个 source_snapshot.zip 的成员集合和所有成员 SHA 均与各自清单相符，合计 692 次成员核验。各 pytest.log 的原始字节 SHA 均与相应 RUN_RECEIPT 一致。本次读取的 77 件原始文件在审查前后 SHA/size 不变。

| 轮次 | 保留的实际 pytest 结果 | RUN rc |
|---|---|---:|
| v1 | 2 failed / 1013 passed / 11 skipped / 156 subtests | 1 |
| v2 | 1019 passed / 11 skipped / 156 subtests | 0 |
| v3 | 1 failed / 1034 passed / 156 subtests | 1 |
| v4 | 3 failed / 1032 passed / 5 warnings / 156 subtests，181.75s | 1 |

v4 保持失败。它没有因后续修源、局部通过或环境归因而变为通过；当前正在修改的源码也不等同于 v4 的冻结 ZIP。

## CLI 编码归因的原件补核

独立读取 cli_encoding_environment 中的八份原件，没有再次执行 CLI：

- 相同 argv、相同含中文路径的输入，两条已保留运行均 rc=0。
- 未设置 PYTHONUTF8 的 stdout 原始 SHA 为 234d9f9352c142919d392753c473f88ad2266ed262b85da116b2607b2f6f52db，独立 UTF-8 解码失败；设置为 1 的 stdout SHA 为 db9deb1f96f8ba81b4c0c88a1308f8cc4ae22d9811b4641bbbe9282ecd8dc02e，可 UTF-8 解码且包含实际 PASS 标志。两份 stderr 均为零字节。
- 收据绑定的两份 CLI 脚本及两份测试源码 SHA 均与 v4 ZIP 对应源码相符；保留 targeted_pytest.log 实际为 13 passed in 2.72s，收据 rc=0。

这些原件支持子进程输出编码的限定归因，与 v4 保留的 UnicodeDecodeError 相符。它不能证明修正环境后的整个回归必定通过。逐原件 SHA 与核验结果见 ENCODING_ATTRIBUTION_REVIEW.json。

## native top 反例的复核结论

新旧 original/revised 输入各自全文一致。旧 ABC 日志实际选错第一 buf root 并报告 equivalent；新归一化仅含 ztop，真实 ABC 日志报告 NOT EQUIVALENT，并给出 Y 的区分输入。两份新归一化收据的 top、实际输入/模型前后快照及产物逐 SHA 吻合。完整细节沿用 REVIEW_V1_V3.md/JSON，并在 REVIEW_V1_V4.json 重新检查。

本 QA 不关闭 OI048 的 mapped-right 反例/status gate，也不关闭 OI046、四态、S/SPEF 正式原族科学证据或论文图表回填。上述门须分别验证，不能用证据文件完整性替代功能正确性。
