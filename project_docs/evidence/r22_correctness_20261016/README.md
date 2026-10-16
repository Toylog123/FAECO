# r22 当前实现正确性恢复（2026-10-16）

用户明确继续后，从已推送main/781c031恢复。当前工作包括实现修复与证据恢复；本目录静态/测试通过不等于科学结论或真实SEC/STA已通过。

## 验收对象与结果

- `full_regression.json/.log/.xml`：首稳定对象整套741 passed、1 failed、4 skipped、156 subtests，108.20s，wrapper112s/exit1；源码哈希前后一致。唯一失败是合法B的wire分组合并被新非目标结构门误拒。
- `full_regression_v2.json/.log/.xml`：修复每个net的声明比较后，**757 passed、4 skipped、156 subtests，102.50s，wrapper107s/exit0**；162个Python源码/测试文件before/after SHA一致。具体命令、版本HEAD和全部文件SHA在JSON中，不借先前667作为本轮通过证据。
- `INTEGRATION_REVIEW.md/.json`：独立复核保留各轮反例与控制，最终7源码冻结对象原反例均符合预期；不是正式EDA结果。
- `tdd_logs/`：已保存parser、模型/局部门、模块/锥/割集成、wire兼容修复及A绑定工具的红绿回显。各次限定测试集合不同，不将数量相加冒充独立测试总数。

## 实现修复与约束

| 问题 | 当前实现 | 验证 |
|---|---|---|
| K1完整Liberty模型 | 全部组合输出生成assign，常量1-bit；多输出R匹配完整函数/角色 | 实际SKY库10个多输出单元、错误COUT反例；真实SEC正负控制待运行 |
| K2多输出解析/图/割 | 实际Liberty输出方向；一physical instance一Gate；常量alias、空输出、全部驱动；外部消费者边界完整 | 次输出依赖、无输入source、别名根、外部输出、split内外集合反例 |
| K3端点作用域 | CLI先取top再查D | helper/top同名shared实例反例 |
| K4非目标行为保护 | assign/端口/wrapper不变，既有wire宽度/符号/维度/声明次数保留 | 合法B分组扩线允许、改宽/冲突重声明拒绝 |
| K5实例身份 | 目标模块内重复物理实例在解析/门/动作入口统一拒绝 | R/G/B/JOINT/工厂/评估器反例；旧深链fixture的GROOT意外重复已纠正 |
| K6提交前刷新 | RGB/S同样先top+Liberty刷新，失败硬F2且不提交 | S错误top反例与合法alias/helper控制 |
| 独立SEC输入 | module_spans忽略注释/字符串假模块，helper字节不变 | 假module及helper差异反例 |

## 下一阶段（必须实际运行后才升级状态）

阶段commit后冻结源码、输入和模型。`sec_model_controls.py` 将调用同一独立SEC工具验证常量/全加器正确电路通过、故意错误电路拒绝。历史A六例新注册主pair并独立证明；B旧模型语义另审计。C′使用新v2目录，18项pilot全部通过才扩72；D/C同族复验与原数据继续隔离。原失败v1和历史结果不覆盖。

历史B的模型完整性不是本轮pytest的证明范围；以独立 `r22_b_model_audit_20261016/` 审计与后续真实证明为准。当前中英稿仍有历史科学证据待补验。
