# r22 correctness repair and evidence recovery

用户2026-10-16明确“继续”，解除10-14暂停。起点main/781c031，git status干净。沿用R22_EVIDENCE_CLOSURE_PLAN与已归档K1–K6反例，不另造方法或更改预锁矩阵。

**目标**：修复实际Liberty语义与模块边界上的实现错误，再恢复真实证明和实验；不是通过措辞调整掩盖缺证。

**设计与归属**：parser agent独占netlist.py/netlist_io.py及replacement.py解析入口；models agent独占real_wns.py；主线负责graph/cut、CLI/flow集成与批次独立SEC入口；records agent实时记录。共享接口为可选cell_output_functions字典与Gate.all_outputs；一个物理实例永远只计一个Gate。主线按实际diff与反例统一复核，源码冻结后整体回归。

- [ ] K1：全部组合输出逐个生成assign；用实际428-cell库完整核对输出集合，多输出反例不得使用不完整模型证明。
- [ ] K2：按实际Liberty识别连接输出、constant aliases、空连接、重复实例与物理门数；图/割的所有输出共用同一物理节点，次输出不能被当输入或漏驱动。
- [ ] K3：CLI端点D只查明确top；测试helper/top同名实例及错误top。
- [ ] K4/K5：局部功能门拒绝非目标assign变化/重复实例，R/G不能仅以最后输出函数判断多输出单元等价；保留未改assign/wire的合法B修改。
- [ ] K6：S与RGB共用提交前top+Liberty cone刷新；失败记录硬F2，不提交、不吞异常；对合法多模块和失败刷新分别测。
- [ ] 独立SEC模块发现复用module_spans，忽略注释/字符串伪module，保留helper字节不变门；源码/模型/输入哈希写入新证据。
- [ ] 各项先红测后最小实现，局部相关回归；不在整体回归时修改源码/fixture。完整pytest使用300s timeout并保存stdout/JUnit与被测SHA。
- [ ] 独立修复审查通过后阶段commit+push；新v2目录/源码pin，预锁18pilot全部通过才扩72，不覆盖v1，不按正向结果调臂。
- [ ] A六个已识别接受候选独立SEC；历史D/C按同族配置复验/审计，不用C′替代。保留B已有28个绑定及其声明纪律缺口，未知与不合法分开。
- [ ] 证据闭合后同步两版稿件、图表及声明；当前稿仍是科学结果待补验的工作稿。

验证日志暂存scratch/r22_resume_20261016；有用证据与摘要晋级project_docs/evidence/r22_correctness_20261016。实验启动前登记版本/输入/配置、运行后记录结果与归因。正式矩阵超时/并发仍按原设计，运行期间持续监测。
