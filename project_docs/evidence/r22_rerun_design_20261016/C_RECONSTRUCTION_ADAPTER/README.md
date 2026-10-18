# C 同族重建：证据内安全适配器预览

本目录是新的、独立可审查适配器，不是已经安全化的生产 `run_hybrid_repair.py`，不是 C′/outerloop，也不是恢复出来的原 runtime revision。没有改 `code/`、旧证据，没有执行 Git 操作或改变 HEAD，没有映射、STA、SEC 实验注册或执行。QA 的 STA/SEC 边界全部使用 stub；真实八起点只做静态模型/F1/F2 检查。`recipe_preview.json` 为 `execution_ready=false`、`formal_source_pin=null`。

## 文件与复用边界

- `adapter.py`：历史 greedy pass 调度的语义适配，追加式 journal、独立 trial/commit 目录、真实 STA 进程尝试分账、源/输入 guard、完整终点 SEC 收据门。
- `backend.py`：复用当前安全 F1/F2、Liberty 模型、编辑函数及历史 `_build_r_candidates`、`_critical_instances_from_sta`、`run_opensta`。只在其函数 globals 的**独立副本**里接入 subprocess 边界，不 monkeypatch 生产模块 globals。不调用旧 runner 的 main、映射或覆盖式候选评估 helper。
- `test_adapter.py`：限定反驳性 QA。模拟结果只能标 `qa_complete`；实际模型和 helper 作用域控制使用真实 F1/F2。不是正式科学实验结果。
- `recipe_preview.json`：6 臂 × 8 电路新重建参数，保留历史未知字段，使用已有 C pureG `mapped.v` 的冻结字节，不重映射、不借 sibling 终点或 C′ 结果。
- `QA_REPORT.json`：本轮 QA 命令/日志、源码快照、起点 SHA 及未解决限制；不是正式运行 pin。

## 保留的 C 调度

1. baseline STA 与每 pass 多路径 refresh 分开记录。pass 开始解析当前 top 的 cells，取得本 pass 固定 critical-instance 顺序。
2. 按该顺序逐实例枚举 R→G→B；该实例全部候选来自相同当前 base。全部评估后按提交顺序选 best，立即提交**已评估的确切 bytes**，然后下一实例使用更新后的 text。一个 pass 可有多次提交。
3. 单一 seeded RNG 只 shuffle 每实例候选列表。并行只在实例内部，按提交顺序收集 futures；完成快慢不改变 tie 选择。
4. 使用历史 `_accepts`：WNS 严格改善，或 tns-aware 时 WNS 精确相等且 TNS 改善。没有新增 epsilon、first-improvement、EMA、cut 评分、缓存或重复候选跳过。与旧代码一致，refresh 用于关键实例列表，不把 refresh WNS 默写进最后已接受的 current metric。
5. 轮后从本 pass 已接受 singles 的实例名排序、截取 joint-pairs。JOINT 在**已提交 singles 的当前 text**上再应用操作，保留旧行为；不会改在 pass 起点重放。重复 B 若产生重复实例/非法连接，真实 F1/F2 会拒绝，零 JOINT STA。没有给随机臂补 JOINT。
6. 无改善 pass 停止，20 为上限。候选生成仍使用 pass 开头的 snapshot；下一 pass 才重解析新 buffer 等实例。

策略语义修复来自当前生产模块：R 排除时序源/目标，G 同族时序尺寸仍受完整 state/control 门约束，多输出角色取实际 Liberty。B 保留旧 driver-inclusive fanout 计数作为搜索策略，输出 pin 则用实际全部 output_functions 排除。正确 top 作用域排除 helper 名字污染。这些是**新安全适配**，不声称与错误旧程序逐字节产生相同轨迹。

## 实际启动、配置与输入一一对应

每个 trial 有不可覆写 `base.v`、`candidate.v`、proposal/decision；每次提交另有不可回写 `commit_N.json`，不把旧格式最后-applied 标记误当累计提交数。新 output 目录必须不存在，已有完整或失败目录均不自动覆盖/恢复。

F1/F2/unsupported-domain 先于 STA。候选 proposal/evaluation、静态拒绝、预算拒绝、STA reservation、invocation attempt、实际进程观测、成功/超时/失败、commit 各自登记。baseline/refresh/candidate/JOINT/final STA 分账，SEC 单列。真实进程启动由旧 helper 的 subprocess 边界观察，重试每次分别计数，不能用一次 helper 调用冒充一次 STA。

每个 `sta/attempt_N/` 保存：

- 确切 argv、timeout、role、输入/Tcl SHA；
- 当次 `sta.tcl` 原始 bytes；
- Tcl 中唯一 `read_verilog` 实际解析到的完整 netlist bytes（含全部 helpers）及路径、字节数、SHA；
- stdout/stderr，timeout 的部分输出也保留原 bytes；
- 进程观测、rc、耗时与 simulated 标签。

**每次 invocation，包括 retry 之前**核验当前 mapped SHA、Tcl SHA和实际 read_verilog 路径；启动前再次核验，finally 再核验。只支持旧 writer 的一个字面绝对 read_verilog 路径，含已知 `/mnt/<drive>/` 转换；动态 Tcl/多输入/无法解释的路径拒绝，不能猜测。源、Lib、八个原始 mapped 文件在运行前后和每个外部进程边界由 PinGuard 核验。旧 trial 的 base/candidate、测量输入和提交收据也在 final/SEC/complete 前重新核验，不能把后续被改写的文件收进成功包。

新 STA cap 计算实际 candidate/JOINT 进程调用（含重试），JOINT 也执行预算门；它不同于旧 runner 按 trial 长度的隐式上限。所有预览值 cap=0，因此该差异在计划矩阵中不绑定。wall timeout=3600 秒，旧 STA 命令和重试顺序不改，单次 timeout 只按剩余 run 时间收紧；最终 SEC 预留其 180 秒上限。正式未来调用还须外层 timeout wrapper。

## 独立终点 SEC

复用 `common.final_sec`，没有另实现模型或证明引擎。运行前独立生成新 `sec_preflight/model_preflight.v`，并用 `common.sec_designs` 固定 gold/gate/helpers 的真实分割。RGB 适配不授权修改 helpers；common 会核验 helpers 一致后才共享，区别于尚未实现的 RTL→mapped 证明。

complete 要求 rc=0、status=pass、完整原始初始/最终与 result SHA 绑定、gold/gate/helpers 等于预飞分割、actual `cells.v` SHA 等于独立预飞模型，以及日志中**非零 proven、零 unproven、success 断言且无 No SAT model available**。仅有伪 statuspass/空 equiv success 不够。三态/Z、不支持、timeout、缺收据或不匹配均不能 complete。

预飞文件自身在 SEC 前后也不允许漂移。最终 receipt 散列全体现存配置、trial、启动、提交、模型和证明产物。`run_frozen` 要求另行提供已审查 `C-reconstruction-r22` 正式 pin：clean HEAD、完整 source_manifest（生产 common 来源＋旧 helper＋本目录源码/预览/QA＋恢复依据）、Lib SHA、八输入路径/SHA 必须与预览一致。它**不创建注册 pin**；未来正式 pin 应在外部实验登记包留存并与每个 run 关联。

## 新声明参数，历史未知继续保留

| 臂 | 新重建值 | 来源与限制 |
|---|---|---|
| hybrid | RGB+B、buf1/2、tns-aware、JOINT3、workers2、seed20260806 | 七例有旧 launcher recipe；s382 采用相同值是新声明，canonical run 仍缺 |
| pureG | only G、无 B、tns-aware=false、JOINT0、workers2 | 旧 launcher 和六对相同完整台账提供 recipe 支持；08-26 完整 argv/source 未恢复 |
| pureB | only B、buf1/2、tns-aware=false、JOINT0、workers2 | 八对旧台账/终点相同；未保存 flag 继续 unknown |
| random1/2/3 | RGB+B、buf1/2、tns-aware=false、JOINT0、workers2、seed1/2/3 | random flag/seed 有 C 记录；其余显式新选择，JOINT0 保留观测到的 mixed/random 不对称，不冒充恢复原 flag |

共同 rounds20、period0.5、empty priorities、cap0、clock CK、wall3600。没有将不明 runtime revision、worker/default、预算或原库 SHA 倒填为已恢复。s382 使用保留 C pureG 初始 SHA `608cf28c...` 是新重建输入选择，不把 v3 sibling 认作 canonical。

## QA、限制与后续门

QA 命令：

```powershell
bash code/scripts/run_with_timeout.sh 180 .venv/Scripts/python.exe -m pytest -q project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/test_adapter.py
```

反例覆盖 first-vs-best、多提交、共享 RNG/实例顺序、逆完成 tie、同名 helper 编辑、轮后重复 B、非法候选/预算不启动 STA、source/input/跨 trial 漂移、timeout 部分输出、空/NoSAT/unproven 伪 pass、分割网表/模型不匹配，以及 actual writer 正控。最终日志 `scratch/r22_sequential_20261016/C_adapter_frozen_QA.log`：38 passed/58.70s；此前限定控制和各阶段真实红测日志由 QA_REPORT 索引。

明确限制：

- 当前是证据内适配器，未与任何正式 EDA 进程集成验证，不能称已复验 C48。八份实际输入只证实当前静态门接受，不等于时序/等价证明。
- F2 的传统 netlist parser 对混在同一行的声明/多 cell 布局有限制。本轮 compact fixture 曾在第二 B 前报 undeclared A，改成逐声明但多 cell 同行又报输出 driver 变化；这是合法布局被保守拒绝的限制，未放宽生产门。重复 B 目标 QA 改用真实归档 C 的逐声明/逐实例布局；不声称 generic Verilog 全覆盖。
- 旧 R 编辑器遇空输出/复杂 escaped 表达式等可能不能保持完整结构；当前 F1/F2 拒绝不合法编辑。没有为扩大通过率改门或 silently normalize 原输入。
- 无自动恢复、矩阵并发启动器或注册器；正式 pin 外置保存和全48结果汇总仍由下一阶段建立。当前不允许拿 root 正在运行的 C′72 pin/结果替代该新 C 族。
- common Boolean SEC 的四态、初始化/复位及已知 unsupported 域限制全部保留；非零证明点和准确 writer 不把二态工具升级为通用四态证明。

下一步是 root 对源码/QA 复核，在当前 C′72 完成验收后再决定提交与新 C pin/首反证 pilot。此目录未触发该执行步骤。
