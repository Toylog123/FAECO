# B3 同族复验设计（2026-10-16，只读）

`execution_ready=false`。未执行 EDA、STA、映射、SEC，未修改生产/测试或旧审计证据。该设计仅针对旧 B 族中 b09/b20/b21 的三态错误终点，不能替代 B 全矩阵，也不跨用 C、C′、D。机器可读来源/逐文件 SHA、历史 blob、配置分级、实际检查均在同名 JSON。

## 先纠正入口归属

三例实际保留的是 `outerloop_result.json`、`eval_trials.json`、`state.current_netlist_text` 和 `eval/iterNNN_candNNN/...`，共同批次 `summary.json` 记录 parallel=2、workers_per_circuit=1。它们属于 **B 的统一 stateful outer loop**，可复用 `code/scripts/run_outerloop_real_wns.py` 与既有 `run_outerloop_batch.py` 调度。

**当前 `run_hybrid_repair.py` 不能保持 B 方法。** 它是 C 族 per-instance greedy：逐关键实例评估其全部候选，选最好者并立即提交，一轮可以多次提交；B 按 outer iteration 生成 cut、维护共享 SearchState/预算/失败反馈。换用 hybrid 不只是 correctness 适配，会换调度。不得为 B3 新造 scheduler，也不得借 C′ weighted_st 消融替代旧 B 的 legacy cut 路径。

## 已绑定的真实对象

| 电路 | 完整 raw mapped 起点 | SHA256 | 历史 WNS/ns（仅身份上下文，非新有效结果） | ledger 行数 | 真正 accepted final 的错误 |
|---|---|---|---|---|---|
| b09 | `experiments/20260826_itc99_main/b09/b09/mapped.v` | `7f80e3b9c97d70a4af8a5ca3ab67adc87ed5046bea3f92b018c871d4f8b14337` | -1.14 → -1.04 | 117 | `_818_` / `sky130_fd_sc_hd__einvn_1` 缺 TE_B |
| b20 | `experiments/20260826_itc99_main/b20/b20/mapped.v` | `4a800657a0f64f997fb8d440b5fcc125721b58dd16842524ee9957644a64f377` | -13.21 → -11.23 | 144 | `_106558_` / `sky130_fd_sc_hd__einvn_1` 缺 TE_B |
| b21 | `experiments/20260826_itc99_main/b21/b21/mapped.v` | `5067fd16ecc1af7a3187479817fe4bc918495a4a02b6c2302f4d436f809b9563` | -13.7 → -10.95 | 43 | `_108500_` / `sky130_fd_sc_hd__einvn_2` 缺 TE_B |

三份 raw mapped 都包含 top 与 `dff` helper；三态 used-types 交集均为空，当前纯函数 `validate_cell_input_connections` 全部通过，two-state unsupported gate 无拒绝原因。三份旧 final 的真实来源是 `correctness_audit.json.last_committed_source`；实际打开该 candidate 并 CRLF→LF 后，与原 `outerloop_result.json:state.current_netlist_text` 逐字相等，且 UTF-8/LF SHA 等于 `state.current_netlist_hash`。完整 candidate 路径/SHA/state 字段在 JSON，不凭 `final.v` 文件名绑定。

旧三终点各自有上表一项 einvn，三者 TE_B 都缺失；当前 required-input checker 正确拒绝，two-state SEC gate 同时返回 unsupported。这是只读静态检查，没有重新运行旧 SEC。不能给 TE_B 补常量后继续算作原 accepted 对象，也不能沿用旧缺三态模型的 proof。

## 配置：确知、文档恢复与未知分开

直接产物恢复：period=0.5 ns；`sta.tcl` 的时钟端口 CK；RGB；joint-enumerate-depth=3；proxy=false；hold=false；初始三权重均 1；state budget 的 max_iterations=8、max_patches=8、epsilon=0；STA/formal/wall 硬预算均 null。三者各有 8 个 accepted patches，stop_reason=max_patches。b20/b21 的 F5 事件阈值实际为 60.0 s；b09 没有 F5 事件，不能由此证明它的阈值。三者 ledger 分别 117/144/43 行，仅是评估记录；state.sta_used 为 90/142/41，不能把任何一套直接称为新 STA launch 次数。

`LOG-20260826-01` 记录 beam/candidates-per-iteration=1、enable-buffer、tns-aware、early-stop、workers=1、最多8轮；legacy-regression 报告亦区分 ITC-99 含 tns-aware、ISCAS89 不含。这是文档恢复，**不是运行时 argv 记录**。B trial 行存在可以证明 B 实际被使用，但不能恢复完整 buf 配置。反馈应保持旧 legacy 路径，不能引入 D 的 EMA 或 UCB；初末权重相同也不能反推出禁用了反馈。

仍未知：完整 argv、运行的 Python/STA binary、runtime HEAD/dirty 文件、priority-table 路径/内容/hash、adaptive UCB flag、max-instances、joint-k、完整 metric/patch/formal-cost 参数，以及原运行 RTL/Liberty 字节哈希。未找到三例的 run_config/manifest/runner/map.log/sta.log。无 TOPOLOGY 记录不证明该功能被禁用；邻近历史代码默认启用，但不能当 runtime capture。不得使用当前默认值冒充已恢复参数。

`map.ys` 实际保存：读取 `benchmarks/raw/itc99/v/<c>.v`，synth -top、dfflibmap、abc（相同 SKY130 tt_025C_1v80 Liberty）、clean、write_verilog -noattr。当前对应 RTL 路径迁移至 `data/raw/benchmarks/raw/itc99/v/`，当前 Liberty SHA 与实际文件已登记；这不是旧 runtime 输入哈希。重跑优先原 raw mapped，不重映射，保留 helper。

## 原脚本版本与当前适用性

只读查看邻近修复提交 `c58ad8e`、`b7abaac` 的 outerloop CLI、batch、real_wns 与 priority table。八个 git blob 的完整 OID/SHA 在 JSON。它们是可审查语义快照，**没有恢复到运行时 revision 绑定**，尤其 Aug26 存在多次 F2/vector/signature 修复。当前预览 HEAD 见 JSON；逐生产来源 before/after SHA 相同。当前主线的 `early_stop=True` 默认值和旧谱系 `store_true` 默认 False 曾不同，必须显式注册取值；不可仅因同一个 flag 名字就假定同调度。

当前 outerloop 已有本轮 actual Liberty metadata、F1/F2/duplicate physical instance、三态 required-input 与独立 SEC unsupported 处理，可用于 correctness 修复后的 B 同族复验。保留 legacy cut、原实例/候选顺序、RGB+B、TNS 规则、inner first-improvement、跨轮 legacy feedback 和原 accepted-state 提交规则；多输出/别名/声明/必需输入修复引发的新候选轨迹应归因于 correctness 修复，不要求重现错误 final。

## 最小待补工具与执行门

1. 用三条 B-specific manifest transaction 包住现有 outerloop，不写新搜索/调度器。复用现有 common 的 `source_manifest`、`final_sec`、`evidence_receipt`、`validate_completion`；D 专用 builder 限定其家族，不能把 B 塞入 D 参数表。若使用既有 batch 并保留 parallel=2，需要最小增加 `--skip-mapping` 等显式参数透传；当前 batch 没有该透传，直接调用会重映射。
2. staging 用独占创建，完整 raw mapped 字节 SHA 与上表一致；缺 mapped 时必须在启动前失败。当前 CLI 的 skip-mapping 在文件缺失时会回退 mapping，adapter 必须封住此路。新路径独立于旧 run，不覆盖。
3. 先补缺失配置证据；找不到时，正式登记“B 同族重建”参数：文档的 beam1/early-stop/TNS/B/legacy feedback，加显式选择 priority table、max-instances/joint-k、topology、F5/metric 设置。真实历史 argv 仍为 null；JSON 的 proposed_command_argv 也保持 null，本次不构造貌似忠实的可执行命令。
4. 正式运行前绑定 clean source HEAD+文件 SHA、原始 mapped、Liberty、完整新 models、工具 binary/version、全部解析参数、wrapper/checker 哈希。保留 timeout、逐候选 base/candidate 身份、STA launch event、cache/duplicate、baseline/refresh 与 commit 分开的计数。历史 ledger 行数只作历史记录。
5. 每终点以完整初始 mapped 为 gold、实际 `state.current_netlist_text` 为 gate，保留 dff helper，检查 required inputs/三态与 Z 域/显式 X 隔离，再用完整实际模型独立 final SEC；必须有非空实际证明点、assert 成功及零 unproven，并将 proof gate/source hash 绑回真实 accepted state。不是文件 exit0 或旧脚本结果即通过。

## 优先反驳验收

先测“旧坏终点仍能通过”这个最强反例：三项漏 TE_B 必须在启动 STA/SEC 前拒绝。随后测普通 inv/clkinv→einvn 即使 function 相同也不能作为合法 R；真实已连接三态只能获得局部门语义支持，独立 two-state SEC 必须 unsupported 非 pass。

调度反证使用两个实例 fixture：一 outer iteration 的 B 提交不得变为 C 的逐实例多提交；first improvement 与 later best 不同应能被观测。WNS 持平/TNS 更好和更坏分别控制接受/拒绝；legacy feedback 与关闭反馈/EMA 不得混淆。改 mapped/Lib/source hash、缺输入导致 remap、C/C′命令错入 B、duplicate instance、改 assign/输出/FF helper、伪造 state→proof binding都必须拒绝。top/helper 同名实例应合法，禁止跨模块误拒。

通过完整三个新终点才汇总 B3；不把 B3 成功外推为 B30 全闭合，也不跨补 C/D。严格保持同一 pin；发现源码/模型/输入漂移即停止。详细反例清单在 JSON。

本轮只读脚本以 run_with_timeout.sh 120 秒包装，5 秒结束、exit0；日志 `scratch/r22_tristate_20261016/b3_recover_final.log`。该结果不包含 EDA 或新性能结论。
