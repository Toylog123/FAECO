# r24 fresh双侧SPEF：同网表反证门停止

按root批准设计 `f212e784…` 执行，先对C′W1/s382的同一初始网表在u40进行双侧对照。实际启动4次API STA与1次annotation replay；没有启动后续u10/u40/u160候选对，也没有重试。

API返回同网表ideal WNS两侧均−0.98ns，SPEF WNS两侧均−1.90ns；ideal和SPEF delta均0，两个生成SPEF字节相同。然而首个真实annotation replay明确报告**0 unannotated、43 partially unannotated drivers**，故完整注入门失败。上列物理数值只作为失败控制的观测，**不准入科学增益/保持比例**。

实际原流：`paired_spef_runs/control_same_u40/baseline_spef/annotation_replay/{stdout.bin,stderr.bin}`。报告列出的43个partial组可分为：CK驱动21个`DFF_N/_0_/CLK`，21个`DFF_N/_0_/Q`驱动组，以及21个组合逻辑驱动到`DFF_N/_0_/D`组。生成器却写`DFF_N:CK/D/Q`模块接口端点。当前parser读取helper模块方向，但未递归展开到真实leaf；静态有方向/可生成并不保证实际工具完整注入。该行为超出既有tiny direct-cell普通/escaped正控覆盖，不能以tiny通过外推本层级输入。

本次失败首先归于当前SPEF实现/支持域的层级端点闭合，不能归因FAECO想法失败，也不否定既有C′理想STA或终点SEC。修复需在未来明确授权且解除源锁后处理递归leaf映射或对层级输入fail-closed，并用本exact case作为真实注入反例；本轮不改生产、不扁平化替换对象、不假设遗漏端点不影响收益。

采集wrapper只在原runner的subprocess边界保存stdout/stderr bytes，并按原UTF-8/errors=replace/通用换行规则返回结果，native argv、600s超时与returncode保持。静态后审计逐次比较raw双流解码拼接与原runner的sta.log、原measurement_receipt argv/timeout；source/Lib/input/HEAD前后仍按设计锁定。全部采集源码、逐launch intent/returncode、原Tcl/log/receipt及hash保留供root核验，完整明细见 `PAIRED_SPEF_STOP_AUDIT.json`。

实验已停止，等待root裁决；不能在论文中声称本新配对负载扫描完成。
