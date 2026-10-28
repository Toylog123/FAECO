# D14 独立原件验收

客户端日期 2026-10-18；实际 UTC、运行时长与逐项结果见 `attempt1/RESULT.json`。新 checker 及准确 argv/工作目录/日志重定向分别保存在 `checker_v1.py`、`INVOCATION_V1.json`。300 秒超时包装实际约 41 秒结束、退出码 0；原始输出为 `RUN_V1.log`。checker 仅使用 Python 标准库读文件，没有启动 EDA、仿真、测试、项目验证器或 Git 命令，也未修改生产源或 HEAD。

逐项读取了 s27/s382 的 14 份实际 run_config、预登记、completion、结果及 ledger。配置与 manifest 的 expected_run_config 一致；固定 source HEAD `f761ee1996a83fc4f0f3de0999b74d85a8237858`、45 份执行源、Lib、manifest `fd336745fd6bbb3039eaf5c043f67206a5567e74116b7787e093f89592a3ff4d` 及历史输入 provenance 均匹配。

| 实际口径 | 本次独立复算 |
| --- | ---: |
| 已验 job | 14 |
| 候选评估记录 | 2471 |
| 实际新 candidate ideal STA 启动 | 1369 |
| baseline STA（每 job 单独核） | 14 |
| 缓存复用记录 | 1102 |
| 前置拒绝且未启动 STA 的 trial 记录 | 0 |
| 最终 SEC pass | 14 |
| 全部已读来源（前后 SHA/size 稳定） | 4533 |

每个 candidate launch 均与唯一非缓存 trial、candidate/base hash、实际 mapped.v 及 STA Tcl/log 对应；逐原始日志重读 WNS/TNS，与 event 数值相同。Tcl 的真实 Lib、网表、link_design、CK 时钟和周期匹配配置，为 ideal-net 测量。启动序号连续，没有将 baseline、缓存或未启动项加入 candidate k。缓存记录绑定已有启动的候选与基线 hash，且没有新启动号。观测曲线和 valid 曲线按实际事件与 accepted/committed/硬失败证据独立重算，和结果/账本一致。这里的 0 仅指 ledger 内的前置拒绝 trial 记录，不推断其它未入账的搜索候选数量。

最终保留 state 的全文 SHA 与记录 hash 相同；最终 SEC raw 输入分别绑定真实 baseline 与保留 state。gold/gate 顶层及共享 helpers 与 raw 模块逐文本匹配。每份实际 SEC 脚本均显式 rename→equiv_make→hierarchy -top equiv→flatten→equiv_simple→equiv_induct -seq 10→equiv_status -assert；实际日志顶层为 equiv，s27 各 11 proven/0 unproven，s382 各 90 proven/0 unproven，并有成功输出与 rc0。completion 的证据/附加收据逐 SHA 核对，而非仅采信根汇总。

接受范围是当前两电路 14 项 pilot 的现存原件及实现口径；**不能外推到其余 42 项或全 D56**。也不形成物理 RC 校准、四态支持或其他历史科学域结论。Lib 到 Boolean cell model 的语义没有在本次重新独立推导；使用的模型原件与已冻结实现均有 SHA 绑定。后续实验仍按固定 source/输入与独立登记推进。本审查目录在最终收据写入后冻结，复算须指定新的输出目录与日志。
