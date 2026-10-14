# R22 核心证据链代码审查

日期：2026-10-14；起点：主线给定 `46ede94`；对象：当前待提交的 `candidate_policy.py`、`flow.py`、真实 STA launch/cache、`sta_ledger.py`、CLI 与 `run_r22_cut_ablation.py`。采用 requesting-code-review 的问题—证据—影响—处置纪律。仅修改本报告；没有运行 EDA 或执行 git 操作。

角色说明：CLI 与 launch 计数由本审查者参与实现，这两块属于交叉链路自检；candidate policy、flow、ledger 与 batchdriver 的实现由其他执行者完成，本次对它们作独立只读审查。未将参与者的通过声明直接当作代码正确性证据。

## 审查结论

**当前没有剩余的实质性启动阻塞。可在主线稳定整体回归、源码提交与 source pin 完成后进入预注册 pilot。** 此结论表示软件控制链路和已执行的静态/桩测试已达到 pilot 门槛，不表示 P1–P12 的全部探针均已执行，也不表示 cost、cover 或融合已经有正向时序贡献。真实输入/工具、独立最终 SEC、来源实际参与程度与真实预算效应仍必须由 pilot/正式实验检验。

审查发现并向主线即时报告的批处理问题均已修复：重复输出目录破坏共享映射、SEC 重复 helper 定义、凭 completion 标签复用缺少原始证明的结果、首个失败后另一电路继续启动剩余臂、外层超时缺少归因收据，以及逐臂共享 mapped/Liberty 输入未再次锁定。下文保留问题与复核依据，避免只报最终通过而失去记录。

## 1. 本次实际执行的验证

1. 独立运行 7 个相关测试文件：`test_r22_batch.py`、`test_r22_sta_ledger.py`、`test_r22_candidate_policy.py`、`test_r22_sta_launch.py`、`test_r22_cli_controls.py`、既有 `test_outerloop_cli.py` 与 `test_production_runner.py`。最新本次输出：**114 passed，1.96 s**。工具边界由测试替换，未调用 EDA。
2. 用临时目录和模拟真实 CLI 目录契约，实际触发旧 batchdriver 的共享 mapped 缺失与结果路径错误；修复后 batch 集成测试覆盖九臂及不重启 resume。
3. 用仅有 completion/status/result hash、缺少独立 SEC receipt 的临时结果，实际证明旧实现会直接复用；修复后的缺 receipt 测试已通过。
4. 用真实 flow + RealWnsEvaluator、仅替换 STA 工具结果，构造“内层候选 WNS 改善 0.5、accepted=True，但外层 cone_refresh 强制失败”。当前得到 `committed=False`、外层接受数 0、最终 WNS 保持 −1、`B_observed=[0.5]`、`B_valid=[0.0]`。这直接验证了提交轨迹与候选测量轨迹的区分。
5. 主线随后报告稳定源码完整回归：**629 passed / 4 skipped / 156 subtests，99.79 s，超时包装 102 s、exit 0**。这是主线执行结果；本审查者没有重新运行完整套件。此前在源码/fixture 并行变化期间的失败轮不作为最终验收依据。

## 2. 重要问题与关闭依据

| 问题 | 原影响与反证 | 当前处置与复核 |
|---|---|---|
| R1（P1）输出目录重复拼接 | driver 的 out 已含 circuit，而 CLI 再追加 circuit；共享 mapped 在外层、CLI 重映射，结果也在内层 | `job_command` 给 `out.parent`；九臂模拟真实 CLI 输出契约与共享 mapped 测试通过 |
| R2（P1）SEC helper 重定义 | 实际 mapped 网表有非黑盒 dff helper；先后读 gold/gate 会重复定义；旧 SEC 也明确隔离 helper | `sec_designs` 提取两份顶层，只共享左右逐模块完全相同的 helper；变化时 fail closed；测试覆盖相同/变化 helper。官方 Yosys 文档明确非黑盒重定义默认报错：[read_verilog 文档](https://yosyshq.readthedocs.io/projects/yosys/en/v0.67/cmd/index_frontends.html#read-verilog-read-modules-from-verilog-file) |
| R3（P1/P2）completion 标签替代证明 | 缺 final_sec/result.json 时，旧分支仍因 completion.sec_status=pass 而复用 | `evidence_receipt` 绑定结果、trials/launch、runconfig、mapped、SEC receipt/log/script/raw双方/helper/cells；`validate_completion` 检查 raw initial 对共享基线、raw final 对实际 state，以及 SEC 双方 hash |
| R4（P2）批失败传播 | 首个 future 报错后 executor 等待另一电路，但另一电路仍可启动剩余九臂 | 共享 stop Event、每臂/启动前检查、首错置位并取消 pending；已经运行的臂仍按既定超时结束，不继续启动新臂。停止前禁止映射/启动的测试通过 |
| R5（P2）外层超时缺归因 | TimeoutExpired 直接抛出，未写 completion | 写 returncode=124、sec_status=not_run、超时原因与耗时；停止信号置位。该异常分支本次静态核查，未真实等待 3930 s |
| R6（P2）长批输入漂移 | mapped/Liberty 只在循环前检查，后续臂可能读不同输入却仍附旧 manifest | 注册后固定 expected mapped hash；每臂检查共享 mapped 与 LIB，复制后再检查臂 mapped；源码 manifest 每臂也核对 |
| R7（P1，主统计）内层 best 不等于外层 commit | 如果 cone_refresh 失败，仅 accepted=True 会把未提交正收益纳入主曲线 | 真实 trials 初始 committed=False；外层 accept_patch 后按唯一 launch seq 标 true；ledger 要求字段存在时 committed is True。本次真实 flow 工具 stub 反例通过 |

这些关闭依据不包含真实 Yosys/OpenSTA 证明。尤其 SEC helper 隔离修正的软件测试不能代替 pilot 的独立最终 SEC。

## 3. P1–P12 门对照：准确区分覆盖程度

| 门 | 当前证据与已执行测试 | 本轮覆盖判断 | pilot/后续还需确认 |
|---|---|---|---|
| P1 政策路由 | candidate tests 的 weighted-only、flow bypass legacy；batch 九臂命令与路径桩集成 | 静态控制已验证 | 各真实 run_config 与有效入口一致 |
| P2 cost 改变能力与退化 | `test_cost_can_change_cut_identity_and_preserves_degenerate_case`：size 权重改变 cut；等权合法 tie 与端点退化保留 | 已有可辨识性例，不等于真实效果 | 八电路 Full/Uniform 是否真改变窗口/动作；不能因退化挑掉实例 |
| P3 深度与 cover 分离 | reward=0/1/20 下 cover-only 门集不变；weighted-only 无 cover/旧来源 | **部分**：生成分离有测试；未完整跑全部路径/排序组合矩阵 | 真实来源账、cover-first、cost 权重不偷偷改变其他开关 |
| P4 R 可用性域 | cover 保留无 R 关键门测试；当前 flow weighted_st 的 recompute 范围为 cone.gates，legacy 保持 active_critical | **部分**：完整域修正已读代码，尚无专门“非critical但可R门”全链测试 | 台账 R_available 与当前锥/库一致，不误删 G/B/JOINT 机会 |
| P5 重叠去重 | same window 的 cover+weighted 仅一个区域、origins 同时保留测试 | 单锥已验证 | 真实来源重叠率、动作缓存复用与新 launch 数 |
| P6 同池顺序对照 | UR 命令除随机/seed 外与 W1 相同；flow 先取相同截断池，再 seeded shuffle | **部分**：未独立运行新 policy 的同 epoch pool/hash 交换全链反例 | 第一个 epoch 池身份一致；后续因提交不同而分岔属于策略下游效应 |
| P7 动作作用域/类型 | 读真实 evaluator：只取 patch 内关键门，固定 max_instances、joint_k；CLI/batch 明关 TOPOLOGY/S | **部分**：未跑“全部生成 jobs 的改单元均在窗口”专门测试 | R/G/B/JOINT 出现情况，JOINT 受可达门影响，不能声称切源后逐候选集合相同 |
| P8 实际预算/缓存 | launch tests 覆盖正常、cache、预算0、结构拒绝、超时异常、换 base、并行不同候选、physical不增 ideal count；ledger 别名/重复 seq/空 events | 已有核心桩覆盖；未真实做 K=0/1/2 全组合 | `n_new_sta_runs == sta_used <=500`；真实 launch/event/trial 一一对应，前置拒绝与cache不消耗新k |
| P9 主/观测曲线 | ledger hard failure、timeout/error/running、非有限结果、cache、physical failure、committed 标记测试；真实外层刷新失败反例 | 核心统计口径已验证 | 主曲线终点、实际提交网表 WNS 与最终 SEC 对应 |
| P10 提交/刷新/缓存 | 新 base 新 seq、既有 production 闭环/拓扑刷新回归；本次强制刷新失败不提交 | 已有核心闭环桩覆盖 | 每轮 committed base hash、accepted metadata、路径更新与 source trace 对应 |
| P11 patch 与 boundary 安全阈值 | 既有 production F2/F3 测试；代码按实际改门数1或JOINT大小计 ratio，非整个 Cc 窗口 | **部分**：未执行建议的 N=10/20 单门/双门专门矩阵 | 小电路 JOINT 是否被15%阈值拒绝；所有臂同阈值，不能为 Cc 单独放宽 |
| P12 配置/证据锁/默认兼容 | 新 CLI 两 mode 主流程归档测试；完整五 λ 透传；legacy策略兼容、非法政策提前拒绝；batch receipt/source/input锁；既有整体回归 | 配置软件门已有覆盖，非逐字段动态全验 | 源码 commit/tag+SHA、工具版本、冷缓存、共享 mapped/SDC/Liberty、完整 SEC 证据包 |

没有把“candidate tests 的数量”当成十二个门全部通过。标为部分的门也未发现确定性实现阻塞；其未执行的专门探针与真实动态核查应在预注册 pilot 检查中如实记录，而不能后补一句“全验通过”。

## 4. 统计效应与默认兼容的使用条件

显式 weighted_st 不混旧 fixed/random/size/critical 来源；Full 是预锁 **cover-first 调度**，不叫新的归一化加权融合 score。等权只改变节点代价，来源开关独立；LegacyMatched 保持原 constrained 评分/门控语义，结果只能作当前实现强基线。root 锁定矩阵的 W0/W1/U0/U1 名称与早期独立设计建议不同，应以正式 `R22_EVIDENCE_CLOSURE_PLAN_20261014.md` 和实际 ARMS 为准，不能按字母猜 Full/Uniform。

来源比较具有必然联合因果边界：切 Cw/Cc 会改变可达门与可生成 JOINT，估计的是候选来源经动作机会和提交路径产生的总效应。UR 只改变同 epoch 外层池评估顺序，实例内动作规则不变；后续轨迹分岔是该策略的结果。20轮、500次真实新 STA 为两个共同上限，臂的实际消耗不保证相同。没有首次合法改善时不能记k=0；没有 cost 的新测量或接受机会时不能称 cost 已产生收益。

## 5. source pin 后的交接门

稳定整体回归已由主线报告；本审查未发现还需改 production code 的实质性阻塞。提交/source pin 后，先执行固定两电路 pilot，核对九臂：共享初始 mapped/Liberty/SDC、政策/五权重/候选类型、actual launch 与预约数、来源参与/重叠、committed主曲线、停止原因、final SEC proof receipt。任何失败先归因为实现、配置、工具/输入或机制退化，再决定修复/建立新 revision；不得看 pilot 收益后改臂以凑正效应。pilot 的正负结果均不替代八电路全集。
