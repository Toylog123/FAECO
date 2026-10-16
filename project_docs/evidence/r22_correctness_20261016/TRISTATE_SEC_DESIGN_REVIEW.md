# 三态 SEC 支持域与组合证明设计复核

日期：2026-10-16。本轮只读设计、现存诊断和输入字节；未改 production/tests、未运行 EDA。只调用本机 Yosys 0.33 的 `help equiv_simple/equiv_induct/sat/setundef` 查看选项，没有执行设计综合或证明。

## 结论与最小实施范围

当前默认 Yosys SEC 已被真实反例证伪：`tristate_z_diagnostic/z_vs_constant_0` 的 gold 输出为 EN 禁能时 Z、gate 恒 0，却报告 pass。此前“相同三态正控通过、反相某些负控失败”不足以认证工具的 Z 语义。

推荐立即对实际使用 three_state cell、显式 Z 或三态 primitive 的独立 SEC 返回 **unsupported，不能是 pass**；不能删 Z、强制 EN 或改成二值输出后继续声称完整证明。模型仍忠实生成三态，局部语义仍支持合法三态，这个限制单独属于尚未可靠的独立证明后端。

大规模四态引擎目前不是当前科学矩阵的前置任务。实际支持域扫描见 `TRISTATE_MATRIX_SCOPE_CHECK.json`：D56 的 56 个 retained mapped、B2 四个真实 raw 输入均与实际库 13 个三态类型无交集；C′旧 pilot 仅保留两个 mapped，也均无交集。C′v2 尚没有八个实际 mapped，必须在冻结输入时再查，不能借源 RTL 或其它族的零交集替代。

## 为什么“共享任意 Boolean cut input”不充分

设 gold/gate 都保留同一三态 cell，输入 data/EN 逐字相同，其输出为 n。拟将 n 切成两侧共享的任意 Boolean 输入，再比较所有三态输入和原输出：

```verilog
// 保持三态 component 本身及其输入不变
// gold environment
assign Y = n ^ n;
// gate environment
assign Y = 1'b0;
```

| n | gold n^n | gate 0 |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 0 | 0 |
| X 或 Z（四态运算） | X | 0 |

因此共享任意 **二值** 输入的环境 SEC 对所有输入都通过，但三态网络禁能时，真实四态环境不等价。检查所有 tri input boundary 也不能修复这个缺口，因为反例的 data/EN 本来完全相同。它是演绎反例，本轮没有把它交给工具运行。

多驱动 resolution、tri 输出经 FF 返回 enable 的反馈、由 tri-tainted 值控制的时钟/复位，进一步要求闭包和初始状态对应；不能只切第一条 tri 输出线。两个模块中同名实例必须用完整层次路径区分，helper 的稳定性也不能靠局部实例字典合并。

## 可选后续方案与 soundness 条件

1. **当前推荐：清楚返回 unsupported。** 对无 Z/三态的冻结实际对象继续二值域证明；遇支持域外对象先停，不声称其不等价。源/模型/input hash 与 non-pass 原因写入收据。
2. **小范围组合证明：冻结完整三态影响区域。** 从所有三态输出和 resolution net 出发，沿组合逻辑、寄存器 D/Q、控制/时钟/复位边形成完整下游闭包；该区域的模型语义、所有连线/别名、相关 helper 与状态对应必须保持。闭包不得再向改动区域输出 tri-tainted 信号。只对剩余不受三态影响的二值机器证明所有顶层输出及进入冻结区域的每条边界输入相等。由冻结区域的结构同态及相等输入/初态，才能按周期归纳推出它的输出相等。若闭包无法准确提取、跨层次/多驱动/反馈不明、区域内有改动，则 unsupported。这里的结构保留证书是证明的一部分，不是单靠“二值 SAT 已通过”。
3. **完整四态语义编码或经验证的四态后端。** 用明确的 value/defined/Z 编码，覆盖组合算子、条件运算、总线驱动解析、状态转移和输出比较，再使用可靠二值 solver；或采用直接支持这些语义的独立后端。必须以 Z→0、X→0、冲突 driver、反馈/初态等负控验收。实施面明显大于当前未使用域所需，不建议为恢复本轮矩阵先搭建。

方案 2 可支持一部分确切 RGB 结构保持的对象，但不能允许任意 R/Boolean 化简穿过 tri-tainted 区域，也不能把环境共有 cut bit 当作真实 Z。当前不实现该方案。

## 必须优先运行的反驳测试

| 场景 | 验收要求 |
|---|---|
| 真实已有 Z→constant 0 反例 | 支持域门拒绝/unsupported；可靠四态后端必须 fail |
| Z→constant 1 | 同样拒绝，不能只覆盖恰好失败的常 1 |
| 保留 tri，n^n→0 | 不能因共享 Boolean cut 证明通过而放行 |
| 保留 data，改变 disable 极性 | 语义/边界门拒绝 |
| 缺 TE_B、普通 input 空、unknown SKY | 工具前明确拒绝 |
| 多驱动总线改变额外 driver | resolution 闭包或完整四态证明拒绝 |
| tri 反馈经过 FF/异步控制 | 需完整状态/控制闭包，不能仅检组合输入 |
| helper/top 同名实例 | 层次隔离正确；合法对象不误合并，改 helper 拒绝 |
| 任一 tri/SAT 参数或模型缺失 | non-pass；不以工具 exit 0 代替证明状态 |

## B2 的显式 X 与 -undef

同一 X assign 在 gold/gate 原样存在，**本身不足以一般化保证独立四态等价**：改动的消费逻辑仍可能把 X 当 0 后产生伪通过。F1 非 RGB 文本保护只证明 X 的源语句未变；如还需依靠所有局部变换的精确运算语义保留，那是另一张组合化证书，不能把默认 SAT 收据改称独立四态证明。

实际 B2 有更窄的可核查事实，已保存 `B2_X_SCOPE_CHECK.json`：

- Pico core 两侧有完全相同的 7 条 X assign。每个源在所有实际 SKY cell pin 和其它 assign RHS 中的引用数均为 0；其中 trace_data、pcpi_insn 是直接恒 X 的顶层输出，其余为无消费者内部网。
- pcpi_mul 两侧没有显式 X literal。
- 真正 baseline/accepted raw 字节 hash 与 proof_pairs 匹配，审计期间未变化。

因此可以给这两个实际对象增加一个很小的 X-isolation/identity 证书：所有 X 源原句、位宽、端口角色不变且不进入被证明的功能/状态逻辑；直接 X 顶层输出单独按原赋值身份覆盖。剩余二值 SEC 不借 X→0 的推断认证这些 X 输出。若未来任何 X 有内部消费者、来源/位宽/角色改变或无法枚举，则这个证书不适用，应启用可靠 undef 建模或返回 unsupported。

本机 help 明确显示 `equiv_simple -undef`、`equiv_induct -undef` 可开启 undef 建模，`sat -enable_undef` 类似；默认选项没有该承诺。若依赖 undef 模型，**simple 和 induct 都必须开启**，不能让默认 simple 先错误证明掉所有 $equiv，再指望 induct -undef 补救。`-undef` 也不自动变成“strict X/Z equality”：必须先用 X→0、X→1、同源 X 的不同消费逻辑、相同 X source 正控明确后端是在做严格相等还是 don't-care/refinement，并检查预处理是否已消掉 X。

本机 `help equiv_induct` 还说明其归纳等价定义是先已连续若干周期同步后不再分歧；本报告不把它当作独立初态/复位可达性证明。是否采用 `-undef` 强化及如何描述独立证明范围，应由这些真实控制和原研究的等价定义决定。本轮不运行新的工具证明。
