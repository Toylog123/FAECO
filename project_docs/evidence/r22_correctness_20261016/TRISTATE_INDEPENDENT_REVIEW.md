# 三态解析与最终 SEC 接线独立复核

日期：2026-10-16。只读审查其他作者的 `logic_rewrite.py` 与 batch `final_sec` 接线，不修改 production/tests、不运行 EDA 或全套。进程内探针为 `scratch/r22_tristate_20261016/independent_review.py`，120 s timeout 包装，实际 16 s / exit 0。五个来源文件运行前后 SHA 相同，完整值与逐项输出保存在同名 JSON。

**限定结论：本次未找到联合 data/enable 签名或 batch required-input 接线的反例。** 这不代表 Yosys/ABC 支持三态证明；合法输入只到达被拦截的 subprocess 边界，没有启动工具。

## 联合语义映射

独立构造 5 对候选：data `(A&B)`、disable `(A)` 与目标 data `(D&E)`、disable `(E)` 因共享角色不同被拒；把共享角色一致重命名的目标保留。还验证 enable 极性不同被拒、data/enable/output 同时改名的正确对象保留、原三态条件被删除的目标被拒。对保留的两对候选穷举每个输入组合，data 与 disable 值在同一个映射下分别完全相同。逐行结果保存在 JSON，没有仅凭 signature 字符串相同下结论。

实际 Liberty 确实解析 13 项 three_state；clkinv 的 R 候选没有三态目标，einvn 的候选没有普通 inverter；einvn_1→einvn_2 的映射完整保留 A、TE_B。后缀反相原文 `(TE')` 也被 parser 保存，未静默删掉该控制。

## batch 输入门在外部工具前生效

独立调用真实 `batch.final_sec`，只替换 `subprocess.run` 为记录后立即抛出 sentinel，防止 EDA 启动：

| 输入 | 实际结果 |
|---|---|
| 合法三态连接，helper/top 同名实例 g，wrapper dff | 到达被拦截的 subprocess 边界 |
| 合法 TE_B 常量连接 | 到达被拦截的 subprocess 边界 |
| gold 缺 TE_B | 工具前 ValueError 拒绝 |
| gate 缺 TE_B / TE_B() | 工具前 ValueError 拒绝 |
| gate 普通 A() | 工具前 ValueError 拒绝 |
| 两侧相同 helper 缺普通输入 A | 工具前 ValueError 拒绝，证明不是只查 top 或借 helper 差异误拒 |
| gate 未知 SKY 单元 | 工具前 ValueError 拒绝 |

合法同名实例分属不同 module，不产生跨域误拒；非 SKY wrapper 不当作未知 Liberty 单元。此处没有独立认证审查者自己编写的 RW validator 全部实现，只验证另一个作者的 batch 接口确实对 gold/gate 全文接入 required-input 门。

## 作者自审缺口，单独记录

审查过程发现 actual Liberty 的 4 个 einvp 单元使用后缀反相 `(TE')`。审查者编写的 RW writer 当时只做字符串替换，内存生成出现非法 Verilog `assign Z=((TE')) ? 1'bz : ((!A));`。这属于作者自审发现，不与上面的独立复核通过混成一项认证。已通知主线并获授权另开 TDD 修复，需补全实际 13 个三态单元导出及后缀反相转换后重新冻结。

作者修复后补记：actual 库全字段扫描只有这四个 einvp 的 three_state 含后缀撇号；仍将 next_state、clock、clear/preset、latch enable 接入同一表达式转换，避免同类遗漏。先运行后缀反相红测 13 failed，再实施 Boolean token parser；标识符/括号表达式和重复后缀反相有穷举验证，未知语法明确 ValueError，非后缀表达式保留既有格式。限定六文件回归实际 **187 passed / 44.27 s / exit 0**，日志 `scratch/r22_tristate_20261016/postfix_final_related.log`。这属于作者验证，未计入上面的独立复核。

另在内存中用真实 writer 导出 actual 全部 **13 个三态 cell**，逐 cell 的所有二值输入共 **52 行**，分别核对输出为 Z 的条件和未禁能的数据函数，全部一致；原式、生成 assign 与逐行值保存在 `scratch/r22_tristate_20261016/postfix_all13_probe.json`。此进程内生成/解释验证没有运行 Yosys，不代替工具对 Z 的真实正负控制。

主线后续真实正负控制仍须判断工具对 Z 的处理是否可靠；本报告不预判结果，也不把到达工具边界说成等价证明通过。
