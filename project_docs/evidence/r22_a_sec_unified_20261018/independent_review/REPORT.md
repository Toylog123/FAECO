# 原 A 八对统一 SEC 独立验收

客户端日期 2026-10-18。本次独立 checker 的实际 UTC、完整身份和时间见 `attempt1/RESULT.json`，调用及原始输出保存在 `INVOCATION_V1.json`、`RUN_V1.log`。180 秒包装约 98 秒结束、退出码 0。审查没有运行新 EDA、仿真、测试或 Git 命令，没有修改生产源、HEAD、旧 proof 或论文表格。

8 对输入均来自已登记的原 A：baseline 为 `20260805_tcad_sprint1_iscas89/<case>/<case>/mapped.v`，final 为 `20260807_real_pr_iscas8/<case>/fixed/mapped.v`。16 份源文件的当前 bytes/SHA 与 manifest 及原件快照完全一致。尤其 s713 原 A final SHA 为 `3c982ac08503110ad5d6c64ed76197da7d4c1fc6acc0cc032a8825d6db43a695`；未替成 A′。

45 份当前执行源、HEAD、Lib 和注册 manifest 匹配。注册与运行后工具身份收据一致，当前 WSL `/usr/bin/yosys` 还通过只读 UNC 路径独立重算 SHA，匹配 `88c0a12bb814a1a8716b1ae10b482e35d3005ed558e1f5f626b3dc983ea3abd0`。版本输出与八份实际日志均为 Yosys 0.33 / git 2584903a060。保留的非致命 WSL PATH 翻译警告没有被删除，也未称 stderr 为空。

各项已独立核验：原件与 snapshot 字节；UTF-8 BOM/通用换行解码后的原输入与 prover raw 文本；gold/gate 电路模块；对称共享 helpers；实际使用的所有 Sky130 model 集合与固定 Liberty 的 pin、输出表达式及实际简单 dfxtp 时钟/状态逻辑；脚本全部命令与实际 explicit equiv top；日志成功、非零 proven/0 unproven；result/completion/batch/wrapper 的原始 runtime 和全部产物 hash。模型检查未调用项目 parser 或模型生成器。

| 电路 | 实际 proven / unproven | 原 runtime_s（显示至毫秒） |
| --- | --- | ---: |
| s27 | 11 / 0 | 0.281 |
| s382 | 90 / 0 | 0.281 |
| s420 | 79 / 0 | 0.250 |
| s641 | 124 / 0 | 0.313 |
| s713 | 126 / 0 | 0.328 |
| s820 | 139 / 0 | 0.344 |
| s832 | 146 / 0 | 0.391 |
| s953 | 228 / 0 | 0.407 |

表中点数直接来自本批每份实际 EQUIV_STATUS 日志，没有硬编码旧 137/138。未舍入的原浮点 runtime 保存在 RESULT 的 `runtime_s_original`。它测量当前公共 final_sec 的外部 prover 调用与日志写入，不包含模型/输入准备；当时 D STA 并发，因此不用于跨方法速度推论。

原件保真与 prover 文本绑定分开核验。s713 final 的原始字节与 Windows 写出的 `final_raw.v` 字节不同，来自通用换行解码后再次文本序列化；两者解码后的输入文本完全相同。原始 snapshot 仍逐字节匹配原件，绝不把 prover raw 的 SHA 写成原始输入 SHA。

## s820 旧 B / 新统一批次的点数

`attempt1/S820_HISTORICAL_COMPARISON.json` 保存旧/新实际 script、关键 log 行号、顶层输入文本比较和 retained model 片段。旧日志是 137/0，新日志是 139/0。两侧电路 top 按非空行归一后相同；旧脚本先分别 flatten gold/gate 再 equiv_make、prep -top equiv，新脚本先 equiv_make、hierarchy -top equiv 再 flatten。当前保留的旧 dfxtp 模型直接将 Q 作为状态，新固定 Liberty 模型以内部 IQ 为状态再 assign Q=IQ。旧日志 EQUIV_SIMPLE 待证为五个 DFF_*.Q，新日志为一个 `_122_.B`，结构匹配点构造已不同。

这是不同证明构造下的 `$equiv` cell 数量，不能视为同一集合，也不据此比较证明强弱。没有保留最终 RTLIL，本次没有新 EDA，精确多出的两个最终 cell 身份继续 unknown；当前旧模型 bytes 也不能补作其历史同期收据。旧 A6/A2 和旧 B 证明保留各自历史；本次不重写或拼接它们。

本轮接受这 8 对已注册原 A 对象在统一 Boolean SEC 支持域中的现存证据，等待根接受后再由主线更新双语 SEC 表。173 份已读来源前后 SHA/size 稳定。四态、物理时序/RC 校准和其它实验族不在本轮验收范围。最终收据写入后本审查目录冻结。
