# B 历史 SEC 实际单元模型审计

日期：2026-10-16。只读历史脚本、日志、实际 accepted state/候选、gold、旧模型与实际 Liberty；没有运行 EDA、修改 production/tests/论文或 Git。只写本 README 与 `audit.json`。来源文件全部登记路径、字节数、SHA256，审计结束回验无变化。

**结论：原先“B28 均已闭合真实库语义”的表述不能维持。28 个旧完整日志中，23 个没有发现本轮检查范围内的已用输出/状态模型缺陷；2 个 Pico 实际使用的 enable FF 被旧模型错误表示；b09/b20/b21 实际使用的三态反相器被旧模型忽略三态控制。** 本结论不直接证明这些五个最终电路不等价，而是其旧 SEC 不足以认证实际 Liberty 语义。b17 仍为 12812 点已证、1 点未证；regs 无 accepted final，保持不适用。

| 对象 | 本轮实际结果 |
|---|---|
| B 原完整日志 28 项 | 23 项未发现所检模型缺陷，5 项受已用模型缺陷影响 |
| picorv32 / picorv32_pcpi_mul | `edfxtp_1.Q` 缺真实状态更新，旧证明不能替代真实 enable FF 证明 |
| b09 / b20 / b21 | 实际 accepted `clkinv -> einvn` 漏接 TE_B，模型忽略 `three_state` |
| b17 | 无新增已用模型缺陷；原部分证明限制不变 |
| picorv32_regs | 未识别到需证明的 accepted final；不补造对象 |

## 旧证明到底读了哪个模型

28 个完整对象和 b17 的脚本均显式读取：

`/mnt/d/BaiduSyncdisk/03_FAECO/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v`

按既有历史审计的明确迁移规则，对应现存 `data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v`，SHA256 为 `fd864f3ba0776f34a0faf475f733418ffa2b30adead703eaade390c4675fcefc`，与 2026-10-14 来源登记一致。日志的 Verilog frontend 路径也实际吻合。没有根据同名文件猜模型、没有使用新 r22 writer 替代旧模型。

本轮只识别到这一套实际读取的模型。28 个旧日志未捕获运行时 model SHA，现存档案匹配不能补造运行时收据；b17 独立 `sec_result.json` 的 `model_sha256` 则可精确回验。

实际 Liberty 为 `data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib`，SHA256 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`。

旧模型有 377 个 module，缺失全部 10 个 conb/fa/fah/ha 多输出组合模块；但本轮逐 gold、实际 final、SEC gate、helper 扫描得到的 **133 种实际使用类型没有这些多输出类型**，因此不能用这个未触发的全库缺口否定这些运行。

## 已用输出与状态语义

129 种实际使用组合类型的各输出，在不含三态扩展条件的普通 Boolean 语义下，按实际 Liberty 输入顺序穷举真值表与旧模型一致；每项保留表达式、行数及两侧真值表 hash。另有 2 种 `einvn` 的 Boolean function 本身相同，但其 `three_state` 被遗漏，单独判为模型不完整，而不是计入完整语义匹配。

实际使用的正常 FF `dfxtp_1` 模型有真实 `output reg Q; always @(posedge CLK) Q <= D;`，与实际 Liberty 的时钟/下一状态一致。dff wrapper 的真实 helper 指向该模型；原 gold 若只保留 top，实际脚本随后载入 gate 定义的同名 helper。完整 mapped baseline 与该 gate helper 的逻辑相同，部分对象仅多了 wire 声明，逐对象比较保存在 JSON，不把缺 helper 的 gold 单文件误称自包含。

### Pico 的 enable FF 不能按普通 assign 代替

旧 `edfxtp_1` 模型只有 `assign Q = IQ;`，没有 IQ 声明、driver 或 always；实际 Liberty 则为：输入 `CLK,D,DE`，state `IQ`，clock `CLK`，next_state=`(D&DE) | (IQ&!DE)`，输出 Q=`IQ`。

| 对象 | final 的 edfxtp 实例 | Q 被其它 cell 输入消费 | 旧日志将 undriven 设为 undef 的行数 | 旧日志已证/未证 |
|---|---:|---:|---:|---:|
| picorv32 | 1248 | 1185 | 8270 | 2357 / 0 |
| picorv32_pcpi_mul | 246 | 214 | 1657 | 29 / 0 |

日志实际含相应实例的 IQ/Q 被设为 undef，行号与样本在 JSON。它们不是空证明（equiv 数量非零），但使用了错误状态语义，不能把“全部已证”当作真实 enable FF 语义完整。

本轮在内存中执行当前 writer，截获文件写边界而不落新模型文件；`dfxtp_1` 和 `edfxtp_1` 均实际生成 `reg IQ`、与 Liberty 完全一致的 posedge next-state 更新及 Q/state 映射。此为模型生成检查，不是新的工具 SEC。

### 额外发现的三个三态对象

| 对象 | 受影响实例 | gold 类型 → accepted 类型 | 实际缺少输入 |
|---|---|---|---|
| b09 | `_818_` | clkinv_1 → einvn_1 | TE_B |
| b20 | `_106558_` | clkinv_1 → einvn_1 | TE_B |
| b21 | `_108500_` | clkinv_1 → einvn_2 | TE_B |

三者实际 Liberty 输出 Z 的 `function="(!A)"`、`three_state="(TE_B)"`。旧模型仅赋 `Z=~A`，省掉高 TE_B 时的高阻语义；三个实际 final 都没有连接 TE_B，旧日志各有一条该实例 `TE_B_gate` 被设为 undef。不能以 function 的二值真值表相同解释为三态语义等价。

本审计时的当前 LibCell/parser/writer 也未保留 `three_state`，所以仅换成新 writer 不能修复这三个对象。该缺口已报告主线另开修复；本包保留发现时源码 pin，不随主线后续修改重写历史结论。

## 两个 Pico 的新证明对象，直接复用 proof_pairs

`audit.json.proof_pairs` 的 `gold_path` 已改为真实运行 `mapped.v` 基线，`gate_path` 为由历史 crosswalk 明确指定、又与末 accepted patch 及 `state.current_netlist_text` 回验的候选 `mapped.v`，均为完整 raw 文件。两对都只有自身 top module、无 helper，无需 strip/共享/覆盖 helper。

| top | 真正 accepted gate 的路径尾部 | 原文件字节 SHA256 |
|---|---|---|
| picorv32 | `eval/iter008_cand008/001__07114__B/mapped.v` | `b5fd51c45519123c9eb293a7d347ad57c4bed053e83875d51752a01e0297704b` |
| picorv32_pcpi_mul | `eval/iter005_cand005/048__0790__B/mapped.v` | `d64a98ec6e5b105aa736352d3733551918cd4308a0cf696bf51449b8c707180c` |

实际 state UTF-8/LF 文本 hash 分别为 `c02141687d996ae3c091d342acf1d1762732ec40ea099657972a7500087e8f4a`、`bf23695dba17f71a7719b322fbc047bee77010b5364fe471c020dbdcbae3a6e2`，同时吻合 `current_netlist_hash`、末 accepted `candidate_hash/netlist_hash`；候选文件 CRLF→LF 后文本与 state 完全相同。保留两种 hash 的不同语义，不把文件字节 SHA 与归一换行后的 state hash 混用。

**绑定勘误**：初版 JSON 的固定 reason 文案错误声称 state 与旧 SEC gate 的 full text 相同，实际比较字段正确为 false。已明确纠正，原因不是不同候选：旧 SEC gate 比 state 仅在 `endmodule` 后额外多 1 个 LF；旧 SEC gold 与真实 mapped baseline 仅在 module header 前后空行位置不同。两组完整 unified diff、原/新路径与 SHA、仅删除空白行后的相同 hash 全部保留在 `proof_pairs`；未改任何旧文件，也未用删 token/逻辑重写去掩盖差异。

## 工具退出门与范围

28 份旧脚本均有 proc/memory、flatten gold/gate、equiv_simple/induct/status，但 **没有 `equiv_status -assert`**。本轮没有拿 exit 0 充当证明，而是实读每份非空 equiv 数量与零未证日志。b17 例外为原部分证明，仍保留未证点。三个三态对象与两 Pico 的 undef 已逐项解释，其他对象没有因此被一并否定。

审计主程序读取/穷举约 16 s，附加三态/绑定核查约 5 s，均有 180/120 s timeout、exit 0；只生成两份本包文件。没有新的 SEC、STA 或收益结论。后续正式复验必须用真正 accepted raw 对与完整库模型，并单独保存新 source/model pin、输入 hash 与独立工具输出。

## 后续恢复（2026-10-16，LOG-23/24；不改写初审发现）

上节“没有新的SEC/STA”仅指本包初审生成时刻。随后parser已保留完整three_state与联合data/enable候选语义，writer准确输出相关逻辑并修后缀反相；独立Zvs0反例暴露二态工具soundness边界，当前actual三态/Z/switch给structured unsupported非pass。准确writer保留，显式四态编码为支持恢复路径，不能称三态已证。

正式B2已在HEAD44d20bb执行新correct enable-FF模型证明：picorv32 pass（6.078s）并绑定7个孤立constant-X identity，picorv32_pcpi_mul pass（0.750s）且0X；wrapper16s/exit0、source_stable=true。new_model_proofs/manifest_and_results.json保存raw/state/LIB/44source/checker66fe72ff…/producer与全部产物SHA；POST_RUN_VERIFICATION逐原bytes、完整decoded gold/gate、artifactSHA和动态重算cert双pair全匹配。

X checker独立review为20负全拒、5/6正控接受，actual2pair7/0证书；合法escaped关键字网output保守误拒不影响这四文件，不能泛化语法支持。组合证明范围是two-state SEC加独立孤立constant-X identity，不是任意四态或复位等价。

OI038的新correct模型实际对象缺证已恢复；旧模型状态缺陷/旧runtime身份缺失仍是历史事实，不追认、不补造。b09/b20/b21缺TE_B的三态accepted对象仍待同族真实语义恢复/重跑（OI039），不能用B2补证替代。没有STA/pilot，新矩阵尚未注册。
