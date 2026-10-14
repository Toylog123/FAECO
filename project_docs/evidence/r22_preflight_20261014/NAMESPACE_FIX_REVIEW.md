# r22 namespace 修复独立审查

日期：2026-10-14。范围：只读当前 production、测试、已归档 pilot 与 Liberty；仅运行进程内构造、检查器和模型生成探针，不运行 Yosys、ABC、OpenSTA 或新 EDA，不改源码、论文、图件。审查对象是首失败 production pin `28c3c2b5c6325ffbad4e4ac54cc3caab237d68a5` 之后的工作区修复，**不能把该旧 pin 当作修复后的版本号**。本报告配套 `NAMESPACE_FIX_REVIEW.json` 钉定12个源码/测试文件与实际库的 SHA256；探针开始和结束源码哈希一致。

结论：**已修复原 helper-first B 插入的模块跨界问题，但尚不能开放新的真实实验扩展门。** 多输出 Liberty 模型不完整、合法 conb 输入在 F2 中被误拒，是已证实的阻断项。端点D网查找仍有全文命名域残留。其它常量端口与重复实例探针揭示检查器边界，必须与真实生成器已发生的错误分开陈述。审查没有证明新的最终SEC通过，也没有验证当前英语稿的科学结论已恢复。

## 已证实的阻断与剩余问题

### K1 — 多输出组合单元的SEC模型漏赋值

定位：`code/src/rseco/real_wns.py:329` 的 `write_liberty_cell_models`，尤其组合分支约410行；`code/src/rseco/logic_rewrite.py:91` 已保存 `output_functions`；`code/scripts/run_r22_cut_ablation.py:114` 和 `real_wns.py:298` 使用生成模型作为独立证明的单元语义。

实查实际库 `data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib`，SHA256=`ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`。解析结果含428个单元，其中10个组合单元有多个输出。最小生成探针确认：conb_1 的完整函数为 `HI=1, LO=0`，但模型只生成 `assign LO = 0`，HI未赋值。抽查 fa_1/fa_2/fa_4/fah_1/fahcin_1，全部遗漏 COUT。六个模型原文及各输出函数、缺失集合保存在JSON `model_generation_probes`。

这不是未知作者配置问题：当前生成器把所有输出声明为端口，却只为最后一个 `cell.output_pin` 赋值。证明因此使用不完整的库模型。**本次没有运行证明，不能声称已观察到某个错误候选的SEC伪pass；可以确定的是，目前生成模型不能忠实覆盖这些输出。** 修复应按每个组合输出的实际函数生成模型，核查生成赋值集合与Liberty输出集合完整一致，再绑定新的源码/模型哈希执行受影响的独立证明。仅让两侧共用同一不完整模型不能恢复库语义。

### K2 — 合法 conb 输入被F2误判为解析失败

定位：`code/src/rseco/netlist.py:147` 附近以 `{Y,X,Z,Q,Q_N}` 猜测唯一输出；`real_wns.py:423` 的 F2 调用该解析器。与K1相同的实际Liberty明确声明 HI、LO 为功能输出。

合法最小网表 `conb_1 tie (.HI(H),.LO(L))` 对自身检查的结果为：F1 pass，F2 fail，原因 `cannot determine output pin for named-port instance`，见JSON `legal_conb_baseline_identity`。**这是合法单元的分析支持缺口，不是基线非法，也不是新候选改变函数。** 若真实输入使用该单元，则不加区分的严格F2会在所有候选前置门中拒绝它。

输出角色应由实际Liberty/显式单元语义识别，不能只把 HI/LO 再加入“选第一个输出”的白名单。一个物理实例可驱动多个输出；F2需要覆盖各输出，F3需要继续按target物理实例计数。若把多输出拆成多个内部Gate记录，应另保留原实例身份，避免F3分母增加或重复实例门误伤合法单元。本条后半是修复设计约束，尚不是已实施的新错误。

### K3 — CLI初始端点D网查找尚未按top截取

定位：`code/scripts/run_outerloop_real_wns.py:325` 将全文 `mapped_text` 交给 `dff_d_input_net`，约340行才建立top单模块分析输入。函数 `real_wns.py:533` 从全文首个同名dff/SKY实例读取D。

同名实例 `shared` 同时存在于helper和top的最小探针实际得到：全文D=`helper_d`，top slice D=`top_d`，见JSON `endpoint_D_fulltext_vs_scope`。这可令最初target cone取错命名域；应在此调用前截取明确top。**未把它归为首pilot已发生的问题：已读取的s27/s382实例命名未证明存在该碰撞。** 两个新 checker factory 接到正确top，不能代替端点构造入口的作用域约束。

### K4 — 端口常量行为改变可以同时通过局部F1/F2

定位：`real_wns.py:183` 只比较SKY实例局部函数/连线；`netlist.py:96` 对非单标识符assign不建立语义；F2比较端口集合和驱动闭合，不证明端口函数。

保持一个真实 `buf_1` 实例及全部端口原样，仅把主输出 `assign Y = 1'b0` 改为 `assign Y = 1'b1`，F1和F2均返回pass，见JSON `constant_output_behavior_change`。端口顺序改动则F2正确fail、F1 pass，见 `port_header_reorder`。由此应区分“边界/驱动检查”与“完整输出行为证明”。

当前R/G/B构造按局部splicing保留未改的assign，**本审查没有证实本轮生成器会产生该常量变化，也没有将该反例计入真实pilot失败数**。然而两个局部门不能单独作为完整功能证明；若生产要把其承诺扩至任意target替换，应保持非局部端口/assign语义不变或增加相应语义验证，并仍使用正确模型的独立最终SEC。所需反证就是该已构造的具体端口常量对，无需提出宽泛新实验。

### K5 — 同一target内重复实例仍存在不一致拒绝口径

定位：`real_wns.py:182–185` / `:2030–2032` 的实例字典会合并同名项；`gate_sizing.py:151` 只替换第一个匹配；F2未校验同一模块实例身份唯一性；新版 `buffer_insertion.py:109` 已拒绝target内重复实例。

两只 `g1` 分别驱动不同输出的最小重复实例网表对自身检查：F1/F2均pass；G `_apply` 返回只改一只的候选；B `_apply` 则抛 `Duplicate instance in target module`，见JSON三项duplicate探针。这是可复现的输入唯一性门缺口。**没有在已读取真实输入中确认这种重复，不能称实际实验已受影响。** 应统一target实例唯一性检查，检查物理源实例而非可能拆分的多输出分析记录。

### K6 — 结构S的legacy刷新路径还在全文解析且吞异常

定位：`code/src/rseco/flow.py:1121`，S已提交后仍 `parse_verilog_netlist_from_text(s_text)`，随后异常被忽略。RGB主路径约819–823行已正确按 evaluator.top_module 截取，且刷新失败发生在commit前。

这是源码实查的旧路径剩余项。本轮C′明确关闭S，因此**不据此否定当前RGB namespace修复，不借本条推翻历史S负结果**。但“flow刷新全部已经按top闭合”尚不成立；legacy S若仍作为支持功能，需要保持相同作用域并明示刷新失败状态。

## 确认恢复的namespace边界

| 检查 | 实查结果 | 证据 |
|---|---|---|
| 模块发现时忽略注释/字符串，并保留原偏移 | 真实包含假module/endmodule文字的注释与attribute字符串，仍只发现helper/top；原偏移切片一致 | JSON `mask_comments_strings`；`verilog_modules.py:19–43` |
| 未提供top的多模块checker | F1/F2均明确fail，不回退到首模块 | JSON `multi_without_explicit_top` |
| 明确top不存在 | F1/F2均fail，无跨模块回退 | JSON `unknown_explicit_top` |
| helper内容改变/删除/增加 | `_scoped_module_pair` 对helper模块集合及内容逐字比较；最小helper变更F1/F2均fail | JSON `helper_change`；`real_wns.py:150–162` |
| 旧单模块入口 | 不带top的合法单模块对自身F1/F2均pass | JSON `legacy_single_module_identity` |
| B改动的实例/新wire/buffer同域 | explicit top或唯一实例定位同一ModuleSpan；多模块重名无top拒绝、明确错误top拒绝；非target原字节拼回 | `buffer_insertion.py:79–150`；`buffer_namespace_junit.xml` |
| R/G/JOINT及TOPOLOGY的修改域 | `_apply`、`_apply_joint`、TOPOLOGY构造只编辑target slice再replace，helper不进入替换范围 | `real_wns.py:1065–1090,1195–1196`；namespace test同名helper实例 |
| R availability、actionable cells、F3分母 | 都已读明确target；F3当前用target分析gate_count，已包含dff wrapper，后续多输出支持仍须保留物理实例口径 | `real_wns.py:877–879,1797–1798,2030,2104` |
| RGB提交前刷新 | target slice解析；刷新失败记录hard F2并continue，不先提交 | `flow.py:819–840` |
| CLI局部checker传参 | F1、F2 factory均传args.circuit；候选与baseline STA也传明确top | `run_outerloop_real_wns.py:310,356,396,402` |

已实读 `buffer_namespace_junit.xml`：30 tests，0 failures/errors/skipped，包含两份真实首失败pilot冻结输入的测试，时间0.998s。这确认其所覆盖的B namespace修复，不证明新EDA或整体当前版本验收。本报告未复跑全套测试；父任务给出的整体回归数量/时间必须由对应日志和冻结文件哈希绑定，不能用口述或先前通过数替代。

## SEC端到端与科学解释边界

新batch保存 `initial_raw.v` 与 `final_raw.v`，分别由state初始网表与实际提交state形成；`sec_designs` 要求helpers字节一致，再分别rename gold/gate；`equiv_status -assert` 用于最后退出门。完成/复用收据还比较raw网表与result/state哈希。这条对象链修正方向正确，首pilot也确实在helper改变处拒绝，不应通过覆盖helper或改比较对象来放行。

但最终SEC当前仍依赖K1的生成模型；`sec_designs` 的模块发现仍是独立全文正则，尚未复用注释/字符串mask的公共utility。对本轮已知冻结mapped输入未证明后者被触发，记录为未覆盖边界，不能将所有Verilog语法域统称安全。

首pilot两个runner中间报告收益均不得作为已验证机制/时序成果；新修复需要新pin和独立目录、重跑预锁矩阵。历史A/D及其它论文证据由另一个独立审计处理，本报告不凭当前修复推定旧数据全部有效或全部失效。**中文与英文稿的相应科学结论仍需按实际证据回填；现有英文初稿是已编译的编辑产物，不构成可投稿或科学证据已闭合的认证。**
