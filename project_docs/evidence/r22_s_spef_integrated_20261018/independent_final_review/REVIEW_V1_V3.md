# S/SPEF 集成证据独立 QA：v1–v3 与原生 top 反例

客户端日期：2026-10-18。仅只读核验保留证据与源码 ZIP，未重跑测试、求解器或正式 EDA，未执行 Git 操作，未修改生产或原件。v4 此时仍在运行，本报告不判断其通过。

| 轮次 | 逐件核验 | 实际保留结果 |
|---|---|---|
| v1 | 173 份源码 before=after；ZIP 成员集合及逐 SHA 全符；log SHA 与 RUN_RECEIPT 相符 | 2 failed / 1013 passed / 11 skipped / 156 subtests，rc=1 |
| v2 | 同上 173 份全部核符 | 1019 passed / 11 skipped / 156 subtests，rc=0 |
| v3 | 同上 173 份全部核符 | 1 failed / 1034 passed / 156 subtests，rc=1 |

失败 v1/v3 原件保持不变。v2 的通过只属于其自己的冻结源码，不能倒签给 v1/v3 或后续源。具体失败测试名、源码成员及 log/receipt SHA 逐项列于 REVIEW_V1_V3.json。本次共 70 份被读原件在核验前后 SHA/size 不变。

## 原生 top 反例链

native_top_counterexample 与 _post 中 original.v/revised.v 分别逐字节相同。original 的 Y 由 A 驱动，revised 的 Y 由 B 驱动。

旧归一化 BLIF 的首模型是 sky130_fd_sc_hd__buf_1，另有 ztop；真实保留 ABC 日志明确警告两份设计都有两个 root-level modules，并选第一个 buf 模型，然后报告 equivalent。RESULT.json 的 pass 与此日志一致，构成所声称整机 top 证明范围的错误通过。

新归一化两侧均只保留 ztop；两份归一化收据选择 top=ztop、输入/模型 before/after 快照及产物 SHA 全吻合，命令含 hierarchy -check -top ztop。真实保留 ABC 日志报告 NOT EQUIVALENT，并给出 A=1、B=0 时 Y 分别为 1/0；RESULT.json 的 fail 与之相符。

RESULT 中手工语义见证是 A=0、B=1，和 ABC 实际日志中的 A=1、B=0 不同；两者都是 Y=A 与 Y=B 的有效区分点，不能把手工见证冒称为工具原始输出。

新旧 RESULT 的 yosys_abc 源 SHA 均在被检源码 ZIP/保留源快照中找到对应字节；记录的 Yosys/ABC/bash 可执行文件 SHA 与当前文件逐件相符。本审查读取日志，没有重新启动这些工具。

## 未验证范围

v4 完成与否另行补验。上述 native 反例仅为小型组合电路 top 范围控制；不代替顺序/XZ 正确性、历史 S/SPEF 效果、b18 inout 支持、clean source 注册、论文图表回填或正式原族复验。
