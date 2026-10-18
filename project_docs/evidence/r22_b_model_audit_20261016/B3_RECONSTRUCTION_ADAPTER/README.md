# B3 同族重建适配器（参数已接受，attempt 补强待根复核，未正式登记）

此目录仅新增 evidence 工具与 QA；不修改 `code/`、旧证据或 `B3_RERUN_DESIGN`。实际运行仍使用 `run_outerloop_real_wns.main`，没有 C 的 per-instance greedy，也没有新搜索算法或批次 scheduler。一个 CLI invocation 只执行一个已登记 circuit transaction；外部由主线控制至多2个并发，不能将串行/不同并发的总墙钟当旧批次公平对比。

当前工具可供审查；**正式注册/运行尚未获本任务授权**。根已接受下表的明确重建参数，历史未知项仍不称为恢复值。旧 `review_preview_20261016.json` 保留，`execution_ready=false`；它不是正式 manifest，不能跨 HEAD 沿用。当前 C′ 全72电路完成前，不提交、不变更 HEAD，也不抢用两个 STA 电路槽位。待根完成阶段提交后，以 fresh HEAD 和新文件名生成独占 preview，审查后显式 register。本补强只用 mock QA，没有新建真实 `B3_RECONSTRUCTION_RUNS`，没有启动 mapping/STA/SEC。

## 预登记的重建选择

| 类别 | 数值与理由 |
|---|---|
| 原产物可恢复 | 三个原 raw mapped/SHA；period0.5、CK；8 iterations、8 patches；RGB；joint-enumerate-depth3；epsilon0；无候选 STA/formal/wall 硬预算 |
| 文档恢复，非 runtime argv | beam1、workers1、B enabled、TNS-aware、inner first-improvement、legacy跨轮反馈 |
| 新重建值 | max-instances8、joint-k0、topology enabled、非UCB/非EMA/非随机；固定当前 canonical priority table 的内容/SHA。原 runtime table/hash 未恢复，不能宣称复现原候选顺序 |
| 显式冻结隐式门 | 从被钉定的现有 evaluator signature 捕获 patch ratio0.15、F5阈值60s；b20/b21旧事件支持60s，b09阈值仍是重建选择。其余解析参数全部保存，禁止隐式漂移 |
| 运行监测 | 4h runner watchdog、4h+30s 父 watchdog，仅防卡死；不是科学 wall budget。触发即保留 failed/incomplete receipt，不能混入已完成性能结果 |

输入是原完整 raw mapped，保留 `dff` helper；不修补非法三态终点，也不把旧 final 当新起点。`--skip-mapping` 必须有正确 staged 文件；guarded child 将旧 runner 的 mapping 入口替换为明确抛错，封住文件丢失时原 CLI 自动重映射的回退。原函数、参数、搜索、候选选择和反馈均继续来自现有 runner。

## 正确性与证据门

`build_plan` 绑定当前 HEAD、生产源码逐文件 SHA、adapter、冻结 X checker、priority table、实际 Liberty、旧设计、三 raw inputs 和对应 RTL 的 SHA。正式 register 要求 `code/`、adapter、checker 的 git 状态 clean；必须使用审过且完全相同的新 pin。正式阶段才查询固定 Ubuntu STA/Yosys/ABC binary hash/version，前后再次核对。preview 不调用这些工具。RTL只用于现有 CLI 的存在性要求和来源记录，不用于新 mapping。

每个 job 独占新目录，已有 partial/completed 目录都不自动重跑、不覆盖。先检查当前实际 Liberty 所需 input、tri/Z 支持域和 X identity certificate。正式 child 观察实际 `subprocess.run` 的 STA 进程调用尝试（包括非零退出、timeout 和启动异常）；不改原 command、参数、返回对象或异常对象，不调整调度。之后将候选 launch ledger 与实际报告目录/候选文件 hash 及进程尝试一一对应，分别报告 candidate records、cache replay、new candidate attempts、baseline/refresh attempts、accepted state commits，不能把记录数当 STA 次数。

每次实际调用先以 `mkdir(exist_ok=False)` 创建独占 `sta_attempts/000001/` 等目录，保存确切 `sta.tcl` 和其唯一 `read_verilog` 所读完整网表的原始字节为 `netlist.v`；`inputs.json` 保存真实路径、字节数、SHA、原命令、实际 `read_liberty` 路径/SHA，并核对登记 Lib pin。Lib 文件不在每次 attempt 重复复制；其 SHA 绑定 manifest 中已冻结的实际库。仅解析被钉定 sequential STA generator 的绝对 WSL repo 路径与固定 TCL 语句；重复 read、动态/外部路径、额外 `source`、未知语法均在启动前拒绝，保存 `rejected.json` 和 trace，不猜路径。

返回后将完整 subprocess API `stdout/stderr` 分存 `stdout.bin`/`stderr.bin`，`result.json` 记录类型、字节数/SHA、returncode 或 exception type/message/timeout、前后输入 SHA，并与输入 receipt 及 launch/return trace 互相绑定。文本 API 值按 UTF-8 保存；字节 API 值逐字节保存；timeout 仅保存 API 提供的 partial output，绝不称为完整 OS 原始字节。原 runner 随后覆写 `sta.log` 或下一次的同名 current 网表，不会覆盖这些快照。两次调用之间可生成不同网表，调用过程中脚本/网表/Lib 发生 SHA 漂移则记录、保留原返回/异常，再使事务拒绝验收。启动前检测的漂移也拒绝并留痕。

trace 的 `launch` 表示进入 run API 的调用尝试，不单凭这个事件声称子进程已启动。`result.json.process_launched` 对正常 CompletedProcess、TimeoutExpired、CalledProcessError 为 true；FileNotFoundError/PermissionError 为 false，其余无法确认的异常为 null，并保存明确的 `launch_confirmation`。未启动/未知的 attempt 和 reservation 留证，但 `execute` 与 `verify` 的共同验收门拒绝将其计入科学 complete，哪怕 runner 捕获错误后继续。原异常对象身份保持不变。

回验逐个检查所有 snapshot/output/receipt 的大小与 SHA、原 command/script/TCL 输入绑定、Lib pin、输入前后相等和完整 attempt 序列；禁止未追踪目录。baseline 的实际输入路径和 byte SHA 必须就是冻结原 mapped，候选快照的全文 hash 必须匹配 candidate ledger。baseline/refresh 重试各自按实际调用次数计数，失败尝试也留证；不会改写候选 ledger 的统计口径。

完成条件要求：实际解析参数及方法与 manifest 一致；完整 accepted chain 的 base/candidate/netlist SHA 可回放至 `state.current_netlist_text/hash`；commit identity 与 trial一致；8/8预算及无硬预算/epsilon不变。独立 final SEC 使用实际 state全文和原完整 raw input，共享 helper必须完全相同。提前生成实际 used-cell model并与 prover实际 cells.v比SHA；proof脚本、gold/gate/helpers/raw、非空证明点、零未证、assert成功、无No SAT model警告均验证。失败/unsupported保留failure receipt，不写可接受的completion；failure receipt存在时即使旁边有completion也拒绝。

`verify` 只读回验所有来源、配置、状态、计数、完整 proof receipt和全部输出文件 hash；不能仅凭 completion 文件名或进程 exit0复用。此工具提供事务/证据门，不把 mock QA 当真实 EDA 验证。

## CLI（本轮只运行 preview）

```powershell
.venv/Scripts/python.exe project_docs/evidence/r22_b_model_audit_20261016/B3_RECONSTRUCTION_ADAPTER/adapter.py preview --output-dir project_docs/evidence/r22_b_model_audit_20261016/B3_RECONSTRUCTION_RUNS/review_20261016 --save project_docs/evidence/r22_b_model_audit_20261016/B3_RECONSTRUCTION_ADAPTER/review_preview_20261016.json
```

根完成当前 C′ 全72并确认补强、提交后，使用全新 preview 文件名重新钉定来源。后续能力为 `register --review-plan <fresh.json>`、`run --manifest <registered-manifest> --circuit b09`（另b20/b21）及 `verify`；本轮没有调用正式 register/run。不要绕过 transaction 直接调用内部 `guarded-run`。

## QA 与剩余限制

限定 QA 的每个 external process、binary query、final SEC 都被 fake 替代；包括完整成功 transaction，并以 final raw/state/model/config/log/launch篡改反例验证验收。TDD日志保留首17红→17绿、失败后验收与缺stage的2红→20绿、candidate/launch/commit/epsilon身份3红→23绿。`qa_red3` 最初 fake prover返回None造成后置异常；`qa_red3b` 改为完整假成功证明，明确复现三个本应拒绝的输入被接受，随后修复。原件与最终SHA索引见 `QA_REPORT.json`。

本次 attempt 补强的 TDD/限定 QA 单独记录在 `STA_ATTEMPT_QA_REPORT.json`，不覆盖旧 QA_REPORT 或 preview。反例包括缺快照、同名文件覆盖、调用中 input drift、timeout/异常身份、未知 TCL、baseline 错读候选、快照/输出/receipt 篡改；正控包括截断重试、两次之间合法替换 current 网表、baseline/refresh 分计数和旧完整 transaction。

根复核随后指出原 attempt 版本把 FileNotFoundError/PermissionError 也写成 `process_launched=true`，会让 runner 捕获异常后的完整事务错误计数。该归因与新增红绿控制另存 `STA_LAUNCH_CONFIRMATION_QA_REPORT.json`；它更新当前适配器验收范围，旧 `STA_ATTEMPT_QA_REPORT.json` 作为原阶段证据保留。

剩余限制：参数是根接受的明确 B 同族重建而非历史精确重放；本轮未测试真实 STA/SEC、WSL trace集成、实际运行耗时；formal tool pin尚未查询；仍待根独立审查 attempt 补强及 fresh HEAD pin，并负责外部至多2并发。前后 SHA 检查不能排除外部进程在两次检查之间改写又恢复相同字节，执行期仍需独占、冻结输入；本 adapter 不冒称文件系统级不可变快照。若 current common SEC脚本、STA generator 或输出schema改变，adapter会拒绝，不能自动兼容或降门。新证据只覆盖B3，不推论其余B23，不跨补C/D。
