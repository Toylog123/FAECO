# OI047/OI048修复独立审查：mapped右边界仍需修复

本包只读审查冻结生产源码，另执行两个极小原生正确性反例和有限静态控制；没有科学EDA批次、Git或生产修改。

OI047的assign-only不再注入整库、inline真实使用模型提取已通过独立静态控制；根的完整Verilog→Verilog ztop反例修后产物也实际核到左右各单一ztop，原生ABC返回fail。不能据此关闭所有CEC边界。

## 确认的剩余假pass

`check_mapped_blif_equivalence`只归一化original，右侧mapped BLIF直接送ABC。本次原生控制左侧为ztop的Y=A：

- 右侧单一ztop的Y=!A：实际fail，符合A=0时应不等的语义。
- 同一右侧ztop前加一个独立dummy模型Y=A：实际pass。实际ABC日志明确“2 root-level modules，first one(dummy) will be used”，证明比较了错误对象。

这是一对同条件正负控制，保留原件、工具日志及精确源码SHA，未把mock pass当反例。首次native启动缺OSS-CAD bin/lib的子进程PATH，返回DLL相关错误码，未生成证明；原包保留。仅修探针进程环境后v2才得到上述原生fail/pass。

## 统一最终门问题

直接调用真实 `_abc_status_from_output`，确认以下仍返回pass：非零rc7+pass短语、多root明确错选诊断+pass、同输出先non-equivalent后equivalent。合法rc0单一equivalent对照也pass。当前先认pass短语的顺序不够，不能把退出错误或错误对象的报告当证明。

## 窄修及反驳控制

1. 共用root解析/层次规范化：BLIF按`.model`及`.subckt`/`.gate`引用图识别根，唯一根才自动选择；多独立根须明确指定或拒绝。不要取第一个，也不要删除非指定模型后声称保全原对象。显式top必须真实存在，引用缺失由hierarchy-check明确失败。
2. mapped右输入经实际选定top的`read_blif → hierarchy -check -top → flatten`及共享后续归一化，保raw/selected-top/normalized输入SHA。合法多model、只有一个顶层且引用helper的设计保留支持。
3. ABC baseline生成的optimized BLIF也进入同一对象绑定/规范化门后再backcheck，不能仅因它由本轮ABC输出就跳过验证。
4. 统一CEC状态门先处理非零退出、明确错选/多root诊断与不等价，再认成功短语；正常单一已选对象pass不变。

必要控制：原native反例的两种root排序；显式指定ztop时证明真正inverter不等；指定不存在top拒绝；合法单root等价/不等价；合法child先列、唯一top引用child仍等价；baseline优化产物被注入额外root不可success；非零rc/多root告警不可pass。

源码审查与探针已先交主线，OI048保持open。后续实施须另存真实红灯、最小改动、邻接验证与独立复验，不修改本包修前证据。
