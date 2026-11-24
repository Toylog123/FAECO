# SKY130 AES 电容优先级与布线重试开销

2026-11-24。固定批次与加入电容优先级的 FAECO 使用相同的 AES 冻结起点 `ss_hold_targeted_v2b` 和原筛选池的全部 18 个候选，分别串行实跑。本轮考察遇到第一个相对 hold 拒绝后，重排剩余候选能否在同一壁钟预算内更快或更多回收面积。此前在同一网表验证的六门替换是独立的路径诊断和物理修复。[历史在线三臂](AES_PROTECTED_ONLINE_REPORT.md) · [独立六门修复](AES_RANK4_9_HOLD_REPAIR.md)

## 比较口径和运行前预测

原 IO 约束、3.6 ns 周期、FF／TT／SS Liberty 与提取方法沿用。目标为 116,507.9904 µm² 原功能面积的 0.01%，即 11.65079904 µm²。各视图 setup WNS 损失预算为 36 ps，setup TNS 损失预算依次为 360／360／27,049.177334 ps。仍需满足绝对 hold、相对 hold 容差 0.001 ps、原电气门、一次内部 pin access、恢复 `ROUTED` 后独立全块 DRC、天线和 SEC。

每次累计编辑都重新从冻结 ODB 起跑，初次放开直接连接编辑实例的信号网，其余布线固定。只有与编辑实例或直接网位于同一 DRC 标记的原有非时钟信号邻网可加入最多一次的实际重试。两臂均在 CPU0–5 上单独收费，详细布线用四线程。均最多六个逻辑请求、720 秒 `CLOCK_MONOTONIC_RAW` 端到端截止，其中各计同一实际历史全池筛选 113.363032440 秒。给每个物理阶段的超时上限随剩余活时窗收紧，在途进程终止和清理后才允许下一臂开始。两臂与预检之间均无物理结果复用。

两种方法的第一批均为原池排名 1–3。FAECO 首次因相对 hold 延后拆分时，只重排尚未访问的后缀，且只执行一次。优先数为预估单门面积收益除以 `1 + C / median(C)`，`C` 为冻结 DEF 中直接信号网在冻结 SPEF 里的总电容。排序准备按 RAW 秒实测，整段计入 FAECO 的 720 秒窗。实跑前校验 18 个候选可读取到完整数据，电容中位数为 0.03896634 pF。如果第一批触发延后拆分，预测优化臂第二批为原池排名 15、9、10（`_20897_`、`_13122_`、`_13645_`），固定批次第二批仍为原池排名 4–6。

## 新鲜预检

严格零编辑完成详细布线、RCX 和三视图 STA。15,657 条原布线均保持，独立全块 DRC 和天线均为零，三个角的 setup 与 hold WNS／TNS 复现冻结起点，SEC 11,089 已证、0 未证。第一组三门另跑完整物理检查，独立 DRC 和天线均为零，SS hold WNS 从 +55.295768 ps 变为 +55.138116 ps，唯一拒绝项为 SS 相对 hold 回退 −0.157652 ps。预检成本在两臂相同的计时窗外。传递到两臂的零编辑收据以原始池、原起点、测试和可执行程序源码收据精确重绑。

原件位于 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123`。预检目录 `aes_incident_priority_preflight_v1`，正式两臂目录 `aes_incident_priority_matched_v1`。[两臂驱动](run_aes_incident_priority_matched.py) · [独立复核](verify_aes_incident_priority_matched.py)

| 原件相对路径 | SHA-256 |
|---|---|
| `aes_incident_priority_preflight_v1/config.json` | `ff168edc90daefdbba5f004a43149251c3e668a219f623fced205ffd369103f0` |
| `aes_incident_priority_preflight_v1/preflight/result.json` | `fb4bd00ec1535ff85ab6267430984f9a8f6cb474f07d6f847c44a6c377eb265e` |
| `aes_incident_priority_matched_v1/config.json` | `3b58df6cb5754c00528ad6b8dfac6da0810dc4571d73dabfef83d67bc6a8bb4d` |
| `aes_incident_priority_matched_v1/transferred_preflight.json` | `8c0ce0a97bcfedc6246968e927f1ea563b434c2fb88de52eeeabf3ec3a78c774` |

## 固定批次

本节与下一节记录原始 V1 实跑。V1 的优化臂因截止时的传输错误未产出正常终态，依其原始派发、物理和进程台账独立重建截止前记录。V2 的修复和新鲜对照单独列出。

首批因 SS 相对 hold 被拒。第二批按原池第 4–6 项派发，完整 DRC 的四处违例触发一次实测重试，仅释放 `net4840` 和 `net8407`。合格端点在 561.985993 端到端 RAW 秒达到目标，回收 33.7824 µm²（0.028996%）。恢复原线型后的独立全块 DRC 和天线均为零，SEC 11,089 已证、0 未证。网表与历史固定批次的合格端点逐字节相同。FF、TT、SS 相对 hold WNS 分别变化 +0.000056、0、+0.610845 ps，hold TNS 均为零。setup WNS 分别变化 −0.084821、−0.157652、−0.007105 ps，setup TNS 分别变化 0、−0.996980、−103.000275 ps。SS 新增 `text_out[83]$_DFF_P_/D` 为负 setup 端点，FF 和 TT 的负 setup 端点集合保持。

固定臂第三个请求是累计排名 4–9 的六门。首次物理评估结束后尝试同动作邻网重试。重试 DRT 只获剩余 20.939 秒，在截止前 0.324 秒返回超时拒绝。第四个请求的 DRT 只获 0.218 秒，在截止时截断。四次派发有三个回调返回，其中两个逻辑请求完成了有效物理判定。实际启动 DRT 六次，完成三视图 STA 的物理尝试四次，执行独立全块 DRC 四次、SEC 一次。保留第二个请求端点。

## 电容优先级 FAECO

从冻结 DEF 和 SPEF 生成优先表用时 0.756592 RAW 秒，费用计入本臂。首批按原池排序，仍由唯一的 SS 相对 hold 回退触发拆分延后。第二批如事前预测采用排名 15、9、10 三门。这三个候选继承同一 11.2608 µm² 单门面积估计，独立的原始信号网总电容依次为 0.0109349424、0.0139139000、0.0162499800 pF。

第二批首次布线有六处独立 DRC 标记。根据报告只放开 `_03615_` 和 `net8222`，一次重试后独立全块 DRC 和天线均为零。FF／TT／SS 的 hold WNS 分别变化 −0.008049／−0.012490／+0.073719 ps，hold TNS 均为零。实际物理合法的三门仍违反 FF 和 TT 的相对 hold 门，因此没有启动 SEC。第三请求继续使用同一排序，派发原池排名 6、13、16 的三门。

### 原始失败与有效观测

第三批初始物理检查有五处独立全块 DRC 标记，实际只释放 `_08784_`、`net8148`、`net8407`。重试的 DRT、RCX 和 FF／TT／SS STA 均完成，原有 hold 和 setup 门的测量值均合格。恢复 `ROUTED` 的独立全块 DRC 只获硬窗末端的 2.626941 秒，运行后返回超时状态，RAW 时标距截止还有 0.005096 秒。旧驱动只检查返回后的 RAW 是否已经到线，故这一被硬窗截断的子进程触发了 `TrialFailure`，驱动返回码 1。原始优化臂保留三次派发、两个完整物理判定，窗内未录取与未达到面积目标。第三批的原始记录没有完成独立全块 DRC 或启动 SEC。独立复核按原始进程有效超时和完成前缀重建了这两臂，原始派发与物理记录保持原样。

| V1 FAECO 请求 | 初始独立 DRC | 初始 relative hold Δ FF／TT／SS / ps | 重试后 relative hold Δ FF／TT／SS / ps | 重试工具秒 |
|---|---:|---|---|---:|
| 第二批 9、10、15 | 6 | −0.015765／−0.023925／−0.054845 | −0.008049／−0.012490／+0.073719 | 130.884 |
| 第三批 6、13、16 | 5 | +0.048961／+0.076883／+0.189404 | +0.048961／+0.076827／+0.884626 | 101.995，独立 DRC 截断 |

第二批的实际重试包含 DRT 91.807 秒、STA 三视图合计 17.361 秒、独立全块 DRC 21.716 秒。重试清除了 DRC 并纠正 SS 相对 hold，两处较快角的 hold 回退仍存在。第三批初始 hold 全部合格，独立 DRC 是触发重试的唯一因素。固定批次的成功第二批初次独立 DRC 有四处标记，FF／TT／SS hold Δ 分别为 +0.000111／+0.000500／+0.053069 ps，同样属于原初 hold 合格的情况。V1 与 V2 的固定第二批初始结果一致。初始非法布局的 hold 可被重试纠正，SS 的结果说明不宜把初始 hold 回退直接当成合法布线的最终拒绝。

| V1 原件相对 `aes_incident_priority_matched_v1` | SHA-256 |
|---|---|
| `faeco/progress.json` | `3b23ff57afbd1f3bc6a7d72135d354ab58239d36f0e2ad05a45dda84a2487c82` |
| `faeco/subprocesses.json` | `b3a6605d246b2ecf9d8b61f49fd69732a479ef8f9bcfaa5852af8325201539c5` |
| `faeco/03/retry/receipt.json` | `df3602999009cac77928f624bd20d1722ba31ea48655e9ed21b3ad3bfb8a2de5` |
| `independent_reconciliation.json` | `c00549d8056293c304e590ab4f07a05aa9997653189c81b2191227bb1f3f8225` |

## V2 截止传输修复与全新两臂

模拟子进程在 RAW 截止前极短时间返回超时。旧驱动三例中的边界用例重现 `TrialFailure`。修复版三例均通过，阶段自己的超时和真实非零返回均保留原有判定。每个子进程在发出时记录 `wall` 或 `stage` 限时来源。由剩余活时窗裁剪的子进程如果返回超时，驱动以硬窗截止结束当前方法。保留旧执行源码、时间台账和物理测量。

使用同一预检的精确配置、物理产物和 SEC 收据迁移其资格，原预检各阶段均无超时。V2 另外从同一冻结 ODB 实跑固定、FAECO 两臂，仍以 720 RAW 秒和六个逻辑请求为上限。配置为 `aes_incident_priority_matched_v2/config.json`，SHA-256 `64c4c82d9781cbbd7ca13e8ad4c482f0addcf357ba153062d48b5f16eacb9435`。[修复后驱动](run_aes_incident_priority_matched_v2.py) · [时窗回归测试](test_aes_wall_transport.py)

V2 固定批次第二个请求在 447.228744 端到端 RAW 秒完成并保留同一组三门，回收 33.7824 µm²（0.028996%）。第三次请求在 649.578134 秒完成了 rank 4–9 六门的独立 DRC、提取和三视图 STA，实测 FF／TT 相对 hold 回退 −0.049849／−0.077660 ps，SS 改善 +0.442979 ps，拒绝该六门。第四次请求的 DRT 由硬窗裁剪，有效限时 70.353051 秒，返回超时状态。它比 RAW 截止早约 1.49 秒返回，修复后驱动正确结束当前方法。固定臂累计派发 4、完成 3，实际启动 DRT 6 次，完成三角 STA 的物理评估 5 次，独立 DRC 5 次、SEC 1 次。该固定臂与 V1 的到目标时间相差约 115 秒，支持用各轮实测路径和完整阶段数解释结果，不以孤立的不同轮次壁钟差作归因。

另对照 V1 与 V2 固定第二批的初次布线与重试，以及 V2 固定第三批的重试与此前相同六门的线下完成重试。三组的 routed ODB、DEF 和网表分别逐字节一致，SPEF 仅 `*DATE` 行不同，三角 `views` 对象完全相同。超时归类修复未改变这些物理输出。

V2 FAECO 复现电容优先级首批和第二批的结果。低电容的第二批在 408.891714 秒完成，合法重试的三角读数与 V1 完全一致，仍由 FF、TT 相对 hold 拒绝。第三次请求独立 DRC 和天线均为零，SEC 11,089 已证、0 未证。它在 622.069313 秒达到目标，回收 33.7824 µm²（0.028996%）。第四次请求的独立 DRC 只获 12.895473 秒，归为硬窗截止。FAECO 派发 4、完成 3，实际启动 DRT 6 次、STA 18 次、独立 DRC 6 次和 SEC 1 次。两臂均正常退出并通过独立核验。在本轮，固定批次达到同面积目标早 174.840569 秒。FAECO 接受的三门比固定端点留出更多三角 hold 余量，SS setup TNS 回退更大。

| V2 接受端点 | FF／TT／SS hold WNS Δ / ps | FF／TT／SS setup WNS Δ / ps | FF／TT／SS setup TNS Δ / ps | 新增负 setup 端点 |
|---|---|---|---|---|
| 固定，排名 4、5、6 | +0.000056／0／+0.610845 | −0.084821／−0.157652／−0.007105 | 0／−0.996980／−103.000275 | SS `text_out[83]$_DFF_P_/D` |
| FAECO，排名 6、13、16 | +0.048961／+0.076827／+0.884626 | −0.080824／−0.130118／−0.009770 | 0／−3.473222／−278.987500 | SS `text_out[83]$_DFF_P_/D` |

两端点三角 hold TNS 为零。V2 FAECO 第三批与 V1 截断第三批的动作、ODB、DEF、网表、三角 STA 逐项相同，SPEF 唯一差异是 `*DATE` 行，V1 截断前已输出的恢复 `ROUTED` 的 DEF 与 V2 实获 DRC 零标记的 DEF 也逐字节相同。V2 SEC 证明恰好绑定这份网表，SHA-256 为 `e8baeb2305898e9e720b77df06edbef1fdb96598c08e47add975d336ba5f4b03`。这组相同字节的新鲜物理和正式证书解决了 V1 截断端点的可行性问题。V1 原始计时仍在独立 DRC 处截止，窗内未达到目标。两轮各自的资格由各自时窗内完成的证据决定。

| V2 原件相对 `aes_incident_priority_matched_v2` | SHA-256 |
|---|---|
| `results.json` | `07e36a96a4adf6a8f7444c2ceaca8272ce939135ada4a1eab5dea294e7212d06` |
| [`independent_verification.json`](AES_INCIDENT_PRIORITY_V2_VERIFIED.json) | `5d5b6b407f37ec9818a6411bc43205dbb3cc54d2e2123fb635560eda7788f230` |
| `v1_censored_endpoint_identity.json` | `db0d262061cf8a19aebc25fa20694f4c07a8694c6d6c2181fbfa6892ea9a8119` |

## V3 开发样本的重试调度预登记

候选满足原有标记邻网重试资格、首次物理评估又出现至少一个原相对 hold 视图回退时，保留真实 DRC 标记与初始三角报告，暂缓该批拆分及其 DRC 重试，先访问未访问候选。初始相对 hold 合格的批次保持原标记重试。在 V2 独立复核结束后，使用相同冻结起点、筛选池、门及预算单独执行一个 FAECO 优化臂。开发样本复用本电路此前的故障信息，验证目标是能否把低优先级维修的时间转移到窗内可验收端点。暂缓可成功的重试可能降低候选覆盖。[V3 驱动](run_aes_retry_triage.py) · [重试调度回归测试](test_aes_retry_triage.py)

实跑前的反驳性检查是第二批仍按原共享电容规则发出，若重现初始回退及可释放的邻网，则记录且跳过其物理重试。下一批应仍为排名 6、13、16，若重现初始 hold 合格及五处 DRC 标记，按照原规则为它重试。任一本来合格的候选因这一规则而失去实际验收机会，均计为策略局限。离线回放、后验 DRC/SEC 完成都独立于 V3 的 720 秒窗。

V3 实跑使用 `aes_retry_triage_v3`，配置 SHA-256 `96b1ca104472719ff04ebae388a860653cdcb68ee393035965044bb05a37032d`。首批由 SS 相对 hold 回退拒绝。第二批重现初次布线的三角相对 hold 回退及标记，`faeco/02/deferred_retry.json`（SHA-256 `9ebc770117c301764507fe4b21311c8f0278c97b8f70993f0a96f1b14a3b873e`）保留 `_03615_`、`net8222` 两条标记邻网。此请求没有启动 DRC 重试。第三批与 V2 的下一组三门逐项相同。V2 和 V3 从各自活时窗开始到派发第三批分别观测到 295.529 和 197.851 秒。可直接核对的工作量差异是省去这一批的一次 DRT/RCX、三角 STA 和独立 DRC。

V3 第三批在 524.180922 端到端 RAW 秒完成，回收 33.7824 µm²（0.028996%）。初次检查 hold 过门且保留基于真实 DRC 的一次重试，最终独立全块 DRC 与天线为零，SEC 11,089 已证、0 未证。V2 和 V3 的合格三门 ODB、DEF、网表及三角读数复现。该端点的 V3 物理收据 SHA-256 为 `053619c4c11717da789ff60cf1e4e71222e6d40c409a2d50584299b4fd468e80`。观察到优化臂比 V2 的优化臂更早 97.888391 秒达到同一目标，仍晚于 V2 固定的 447.228744 秒。对照支持在这个开发样本中用更少的重试抵达同一物理结果。V3 为单独时段的单臂测试，两轮的秒数差覆盖实际跨轮运行差异。

最终派发 5、完成 4。V3 第四个请求为六门，初始独立 DRC 8 处、SS 相对 hold 回退 −0.082157 ps，按预先规则第二次暂缓邻网重试。该六门的合法重试能否过门仍未知。第五个六门请求完成初始 DRT、RCX 和三视图 STA，独立 DRC 只获剩余 7.869158 秒后裁剪，档内及时交付的仍是第三批的 33.7824 µm²。实际工具启动数为 DRT 6、STA 18、独立 DRC 6、SEC 1。与 V2 优化臂这些启动数一致，V3 多完成一个逻辑判定，并保留所有已观察的候选身份与 DRC 终态。最终结果 SHA-256 `8f1dd2d18748b899024f31e688d2b65c310ec6e6bc4c360ca60f3a1900429b4d`，独立复核 SHA-256 `61aa126039665acf0f6743daab778e2ca4af1ed16a29774260b5f4e3c416268c`。[V3 独立复核原字节](AES_RETRY_TRIAGE_V3_VERIFIED.json)

第五个请求原有面积候选 65.0624 µm²（0.055844%），冻结起点相对 hold 三角均过。独立全块 DRC 在正式窗末被截断。窗外只读重新载入这份原 ODB 和 DEF，恢复 `ROUTED` 后的 DEF 与窗末已输出的 DEF 逐字节一致。独立全块 DRC 实得八处违例。六处 met1 短路来自 `_21033_` 与 `net8148`、`_11178_` 与 `net4840`，另两处间距违例涉及 `_08784_` 与 `net7882`、`net7963` 与 `net8407`。按预登记在 DRC 拒绝处停止，该端点没有启动 SEC 或新布线。原件目录 `aes_retry_triage_v3_cutoff_completion_v1`，其中 `restored_checks/audit.json` 的 SHA-256 为 `6b59a26347033d617b9e1159cc85ec559bb04bc35b1ac2e416559a05bf626018`。[复核入口](qualify_aes_retry_triage_cutoff.py)

## 第二批低电容三门的 hold 归因

在 V3 结束后，交叉读取 V2 FAECO 第二批合法重试与冻结起点的 ODB 和 SPEF，覆盖三视图的 12 次 STA。同条件组合复现原始收据的精确数字。只换 ODB 的三角 hold WNS 差均为 0，只换 SPEF 则复现整个 hold Δ −0.008049／−0.012490／+0.073719 ps。13 条关键路径网的 SPEF 电阻边和阻值逐项相同，FF／TT 原最差路径仍由 `sa03_sr[5]$_DFF_P_` 到 `text_out[29]$_DFF_P_`，SS 仍由 `key[35]` 到 `u0.w[2][3]$_DFF_P_`。

| 视图 | 发射时钟 Δ / ps | 捕获时钟 Δ / ps | 数据到达 Δ / ps | 数据要求 Δ / ps |
|---|---:|---:|---:|---:|
| FF | −0.023067 | −0.015080 | −0.023067 | −0.015021 |
| TT | −0.029147 | −0.016690 | −0.029088 | −0.016570 |
| SS | 虚拟时钟 | −0.028133 | +0.045300 | −0.028611 |

在 FF 和 TT，发射时钟比捕获提前更多，足以解释相对 hold 残余。时钟源网 `clk` 总电容减少 0.0000481 pF，`clknet_0_clk` 减少 0.0000150 pF，捕获分支 `clknet_3_1__leaf_clk` 总电容增加 0.0000127 pF。`clk` 至本次释放的 `net8222` 耦合增加 0.0000667422 pF，至 `place7142:A` 减少 0.000325436 pF。单个耦合变化的影响没有被独立置换，方向归因适用于提取的整个 SPEF。冻结输入的低总电容排序能降低候选邻网的负载估计，却没有直接约束改变其它邻接网后发生的发射与捕获相对移动。

原件 `aes_incident_priority_hold_cross_v1/results.json` 的 SHA-256 为 `1c3cd8eb020468c0eaf4bfe0325d5524c90674427cc755d7311d0484e0353964`。寄生电容收据 `path_net_cap_deltas.json` 的 SHA-256 为 `c7463f4e9844c142ff99deb797baa1979aa9161c18383c30687050390c8444d0`。[交叉 STA 驱动](probe_aes_residual_hold.py)

WSL Python 3.12.3 在证据目录直接采集和运行九个专项测试，全部通过。仓库核心测试的 Python 3.11 采集不加载这些针对已固定 WSL 环境执行的实验脚本。

## 复现命令

下列命令从 WSL 仓库根目录运行，复用按字节绑定的 `aes_incident_priority_preflight_v1` 预检。重新布线须使用未存在的输出目录。独立复核与窗外诊断独立计费。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
preflight="$raw/aes_incident_priority_preflight_v1/preflight/result.json"
python3 -B -m unittest discover -s "$e" -p 'test_aes_*.py'
bash code/scripts/run_with_timeout.sh 1270 taskset -c 0-5 python3 -B \
  "$e/run_aes_incident_priority_matched_v2.py" "$raw/aes_matrix_v1" "$raw/aes_priority_repeat" "$preflight"
python3 -B "$e/verify_aes_incident_priority_matched.py" "$raw/aes_priority_repeat"
bash code/scripts/run_with_timeout.sh 650 taskset -c 0-5 python3 -B \
  "$e/run_aes_retry_triage.py" "$raw/aes_matrix_v1" "$raw/aes_priority_repeat" \
  "$raw/aes_triage_repeat" "$preflight"
python3 -B "$e/verify_aes_incident_priority_matched.py" "$raw/aes_triage_repeat"
```

## 原件归档

`scratch/tcad_ibex_20261123/aes_incident_priority_study_20261124.tar.gz` 包含本报告的预检、V1 原失败及复核、V2 两臂与端点身份核对、V3 开发臂、第二批交叉 STA 和第五批窗外独立 DRC，共六个独立根目录。归档大小 822,891,438 字节、1,219 个成员，对 1,110 个普通文件逐条核对 SHA-256，Windows 和 WSL 独立计算包的 SHA-256 均为 `e7a2b0629aeb62a425bb518086302e62cc2969ab25d6078142e78578b025dbe6`。归档内另保留与各实际复核收据匹配的审核源码字节、实验执行脚本副本和专项测试记录。
