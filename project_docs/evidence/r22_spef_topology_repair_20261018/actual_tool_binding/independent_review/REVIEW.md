# 实际 OpenSTA 微型注入证据独立核验

客户端日期：2026-10-18。仅接受此次 tiny ordinary/escaped 工具绑定控制范围；未重跑 STA、测试或 EDA，未改生产、原件或 Git。

独立逐 SHA 核验 RESULT 的 43 件 artifact，以及 ROOT_ACCEPTANCE 对 RESULT 的字节绑定。源码 spef.py、opensta.py 和真实 Liberty 的预注册、before、after、当前文件 SHA 全部一致；审查读取的全部 47 件原件在前后 SHA/size 不变。精确计数与明细以 INDEPENDENT_REVIEW.json 为准。

- 四次 API 测量及四次 annotation replay 的 Tcl 均指向各自实际 mapped/SPEF、相同 Liberty、top/CK/5 ns；所有报告都位于 read_spef 之后。replay Tcl 正是原 API Tcl 添加一次注入完整性报告。
- 每份 annotation.log 均与保留的 stdout/stderr 原始二进制流一致；四份实际报告均为零 unannotated、零 partially unannotated drivers。API 与 replay 的各项数值从实际日志独立解析后均与 RESULT 相符。
- escaped 电路确实同时含 bus bit `q[0]` 和 escaped literal `\q[0]`，SPEF 中是两个不同的 D_NET：`q[0]` 连接 f0:Q→b0:A，`q\[0\]` 连接 b0:X→f1:D。两个 RC 设定下均未合并或漏端点。
- 40 与 4000 µm 两设定分别在 ordinary/escaped 间得到相同结果；增大 RC 后两者 WNS 均变差。这只证明控制对注入敏感，不是 RC 标定或收益结论。
- 两个 missing-pin 文件均是各自 40 版本将 b0:A 改为 b0:ABSENT；实际日志含该缺 pin，API 返回所有数值为 null。失败收据中的输入、库、SPEF 和独立保存的 Tcl/log SHA 全部吻合；即使工具 rc=0 也未被视为有效测量。

身份收据记录 OpenSTA 3.1.0、Linux executable SHA 96833cf69282803fc44fc8cc343bfe03ad8279bab9fb276d84a6d4532e15b468，两次查询均 rc=0。独立审查核对了收据的命令/结果，不重新启动 WSL 查询或读取 Linux binary。原始 stderr 含非致命的 WSL PATH translation 信息，已保留，不能表述为 stderr 为空。

此门不证明 s382/b18 科学效果、b18 inout/真实三态支持、顺序证明、几何准确性、整体验证完成或新正式实验可立即开始。
