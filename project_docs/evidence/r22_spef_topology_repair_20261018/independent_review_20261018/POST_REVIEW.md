# 原四项反例修后独立复核（2026-10-18）

结论：**原四项反例在当前冻结源码上均已静态修复。** 只重放原脚本的六个输入（四项问题及两项原有拒绝控制），输入字节逐SHA与修前相同，没有新增随机probe，没有改生产或执行EDA/Git。

| 原问题 | 实际修后结果 |
|---|---|
| escaped scalar与位选混网 | `\a[0] ` 与 `a[0]` 各自保留独立端口和网，分别只连b2:A、b1:A；SPEF中名称分别转义/未转义，不再短接 |
| 纯port直连遗漏 | `assign Z=A` 生成D_NET、A输入P、Z输出P，以及默认RC下3.6000Ω的A→Z支路 |
| module外非法内容漏检 | 明确拒绝 Unsupported syntax outside SPEF modules |
| 输出接literal静默丢失 | 明确拒绝 Output pin cannot connect to a literal |

两项原有负控——缺非ANSI端口声明、超范围alias——继续拒绝。原修前报告/输入/输出/源快照全部保留，本次另存 `post_counterexamples/`、`post_source_*.py` 与 `POST_REVIEW.json`。

生产及测试四份来源SHA在本次重放前后相同；120秒包装实际约5秒返回0。只调用生产静态解析/生成函数，没有真实工具过程。转义方案虽然在文本层保持了区别，**实际OpenSTA是否完整识别这些端点尚未由本次证明**。须在新clean pin下做独立登记的实际注入验证，核缺pin/未注入/错误日志与端点覆盖后，才可支持物理增益结论。

根的整体冻结源码pytest仍按主线验收；本复核不能替代整体回归、新pin与正式同族SPEF复验。
