# 三态后缀转换与最终 SEC 接线独立复核

日期：2026-10-16。只读复核最终源码、实际 Liberty 和现存证据；实际 writer 仅通过内存文件边界调用，未运行 Yosys/ABC/STA，未改生产或测试。本文的后端风险是基于代码的推断，真实正负诊断由主线执行。

## 结论

实际 13 个三态模型的二进制 data/disable 真值表与 Liberty 一致，四个 einvp 的后缀 `TE'` 已转为合法 Verilog `~(TE)`。**这只确认模型表达式，尚不能证明 final_sec 的 SAT 后端完整保留 Z。** 最终 SEC 当前没有 `-undef`，Yosys 0.33 的默认 SAT 常量导入把非 S1 的非 wire 常量作为 false，因此必须加入下面的 Z/0 专用反证；仅通过反相 enable 的负控制不足以认证四态语义。

## 实际模型核查（不使用 EDA）

从实际 Liberty 各 cell block 独立发现 13 个 three_state 单元；再调用当前真实 writer，拦截 Path.mkdir/write_text 到内存，没有写模型文件。逐个解析生成的 scalar ternary，对 A/enable 的全部 4 种二进制组合与已实读原库的 data/disable 语义比较，共 52 行一致：

- ebufn_1/2/4/8：`assign Z = ((TE_B)) ? 1'bz : ((A));`
- einvn_0/1/2/4/8：`assign Z = ((TE_B)) ? 1'bz : ((!A));`
- einvp_1/2/4/8：`assign Z = ((~(TE))) ? 1'bz : ((!A));`

生成文本 SHA256：`30c72aff1fbbe9e09fd44d275dcbf1dc5cae3286704646d1b478a1877b469be4`，与现存 postfix_all13_probe.json 一致。actual scan 里所有后缀 NOT 仅为上述四个 einvp 的 three_state `(TE')`。`liberty_expression_to_verilog` 逐 token 校验语法并用带优先级 AST 重写后缀 NOT，普通函数、next_state、clocked_on、clear/preset、latch_enable 和 three_state 都使用同一入口；本次实际库未发现剩余未转换的 raw postfix 字段。模型文本表达式和语法结构通过本次独立核查；是否被指定 Yosys 接受，仍以主线编译/正负控制日志为准。

## 最终 SEC 接线

`code/scripts/run_r22_cut_ablation.py:final_sec` 已在启动 subprocess 之前，对原始 gold/gate 全文（含 helper）验证实际 Liberty 必需输入连接；不会给缺失 TE_B/TE 猜 tie-off。`sec_designs` 使用公共 module_spans，非目标 helper 必须逐字一致。模型覆盖 initial/final 的 used-cell 并保留 Z ternary；脚本执行 proc/memory/equiv_make/hierarchy/flatten/opt_clean/equiv_simple/equiv_induct -seq 10/equiv_status -assert，以 returncode=0 且明确成功标志作为 pass。

`build_full_netlist_sec_checker` 的 ABC 路径会对三态明确拒绝，而不是用纯 function 代替 three_state。这一 fail-closed 边界是正确的；它不能为下述独立 final_sec 后端的 Z 语义提供认证。

## [P1] 默认二态 SAT 不能认证 Z 与逻辑 0 可区分

官方与部署目标相同的 Yosys 0.33 源码显示：

- [satgen.h](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/kernel/satgen.h) 的 `importSigSpecWorker`（83–95 行）仅把 S1 导入 true，默认非 wire 常量的其他状态导入 false；SatGen 默认 model_undef=false（70–74 行）。
- [equiv_simple.cc](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/passes/equiv/equiv_simple.cc) 默认 model_undef=false，只有显式 -undef 才改变它；当前 final_sec 未传此参数。
- [equiv_induct.cc](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/passes/equiv/equiv_induct.cc) 同样默认 model_undef=false。其帮助还说明其归纳等价定义有同步前提；本复核不外推新的顺序初态结论。

**必须补的真实负控制（已立即报主线）：** 两侧均定义 `module top(EN,Y); input EN; output Y; ... endmodule`。

```verilog
// gold: Y=EN?Z:0
sky130_fd_sc_hd__einvn_1 u (.A(1'b1), .TE_B(EN), .Z(Y));
// gate: Y=0
sky130_fd_sc_hd__inv_1 u (.A(1'b1), .Y(Y));
```

每侧各自实例化对应一行。四态语义在 EN=1 时不同；二态 Z→0 模型可能把它们判成相同。若当前真实 final_sec 通过该 pair，即为直接伪 pass 反例。相反，单独检查普通动态反相器与反 enable 三态单元可能仍会 fail，因为在 data=1 的区域二态值也不同；这样的负控制不足以排除 Z→0 漏检。

不能把“补上 -undef”直接当充分修复：当前官方 undef 模型对 gold 不定态含方向性处理，且不直接构成精确 Z/驱动状态比较。若负控制确认漏检，应先对该后端无法证明的动态三态对象明确 fail closed，或实现并验证能表达输出驱动状态/四态解析的证明模型。保留库三态 metadata、真实 writer 和合法三态候选能力，不等于允许不支持的最终后端返回 pass；也不必把全部三态库单元从库中删除。无三态 used-cell 的证明应独立按其实际模型范围判定。

## 复核对象钉定

- real_wns.py：`8c8625121be2638090c9f5ea906235888831674acfcc1b6c2b3fe4cf520bec7c`
- run_r22_cut_ablation.py：`0dd56195f35066e2b6e6cec649b2b4519ea669575f819e4fc766f6a36651347e`
- logic_rewrite.py：`b26fbd770bff62b321bbc5e3dee056b4aa4b33a361a63bd2dd4586879f6ecc92`
- actual Liberty：`ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`

本次未修改、生成或补写正式 proof receipt；未以此审查宣称任何三态 SEC 已通过。

## 主线真工具诊断与组合 cut 方案复核（补记）

已实际打开 `project_docs/evidence/r22_correctness_20261016/tristate_z_diagnostic/z_vs_constant_0/{initial_raw.v,final_raw.v,result.json}`：gold 为 einvn_1(A=1,TE_B=EN)，gate 为恒0；结果 **status=pass、returncode=0**。同目录 z_vs_constant_1 的 result 为 fail/returncode=1。前述 Z→0 漏检从源码推断升级为该真实后端的直接反例；不能认证当前 Yosys SEC 的四态语义。旧诊断仅保留，不用新 unsupported 结果覆盖。

拟议的“把结构稳定的三态输出切成共享任意二态输入，再证明全部三态输入边界和主输出”等价，**仍不 sound**。反例是三态实例/全部输入不变，gold Y=t，gate Y=t & 1'b1。对共享二态 cut t=0/1，边界和输出全部相等；实际 t=Z 时 gold 为 Z、gate 为 X。禁止新增/删除三态实例也不能排除此例。

未来恢复路径可选精确四态/驱动状态编码；或把支持域额外收紧为经证明的四态同构变换（所有非三态 function AST、pin-role、顺序状态/事件逻辑精确对应，B buffer 必须在所用四态模型中透明），再用二态 cut SAT 作附加证明，而不是宣称其自身给出四态独立 SEC。

任何未来组合证明至少需要：跨模块 flatten 后用唯一原层级路径配对三态实例；逐输出 data+disable 和使能输入共享映射；三态计数/角色不变；无黑盒/遗漏输出/未知输入；正确处理 net resolution 与多驱动（第一版可明确拒绝）；组合环检测；顺序状态对应及初态关系、clock/reset/enable 事件同构；所有切口和主输出使用包含 X/Z 的域或有独立证明可限制为二态。仅做三态输入的二态边界 SEC 不满足这些条件。

主线选择当前 final_sec 对实际 used-cell 中的三态明确返回 unsupported/非pass、保留 raw/来源/Liberty/理由且不启动 Yosys，是已知工具支持域的正确拒绝边界；metadata、准确 writer 和合法三态候选保留，未把三态从库中删除。OI-039 的四态后端支持保持 open；无三态输入的范围另按实查 usedtypes 判断，不能笼统撤销或认证全部历史对象。
