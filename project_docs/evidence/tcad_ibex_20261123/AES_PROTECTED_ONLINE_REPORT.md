# SKY130 AES 共享保护布线的在线对照

2026-11-24。以此前冻结的 AES `ss_hold_targeted_v2b` 为起点，使用原矩阵已筛选的完整、有序候选池。三臂分别为单门贪心、三个一批的固定批次、hold-aware FAECO。此前人工挑选的三门和六门端点作为独立物理诊断，在线三臂由相同候选池、既有调度器和同一自动布线规则产生。[前轮物理诊断](AES_RESIDUAL_HOLD_OPTIMIZATION.md)

## 比较口径

- 起点原 IO、3.6 ns 时钟、FF／TT／SS Liberty 与 RCX 不变。所有候选须通过原 36 ps setup WNS 预算、各视图原 setup TNS 预算、绝对 hold 与 0.001 ps 容差下的相对 hold、原电气门、独立全块 DRC、天线与 SEC。时间到目标衡量原功能面积的 0.01%。
- 每次逻辑请求从同一冻结 ODB 应用累计编辑，初始只清除直接连接到编辑单元的信号网，锁定其余已布线网。真实 DRC 若给出与编辑实例或直接编辑网同标记的非时钟信号邻网，只允许一次从同一起点重试。只放开报告中命名且原已布通的这些信号网。每次物理尝试均保留，路线没有反馈给调度器额外的编辑替换权限。
- 候选在恢复原线型标志后另外执行全块 DRC，比较状态恢复前后路由、组件和专用网几何；角色记录固定网及实际改线路径。面积、时序、物理门通过后执行整个网表的 SEC。共享局部 DRT 使用原 ODB 内嵌 guides 和一次内部 pin access。
- 在 CPU0–5 上串行运行三个方法，OpenROAD 路由用四线程。每臂最多派发六次逻辑请求。端到端窗为 720 `CLOCK_MONOTONIC_RAW` 秒，各计入一次原 AES 完整筛选的实测 113.363032 秒；剩余时间内实际执行前端、物理、STA、检查、证明和自动重试。到窗的在途阶段按剩余时间截断，所有已调用子进程有实测开始、结束、配置超时和有效超时。筛选成本相同，且预检在计时窗外执行。

## 预检

第一次环境准备在任何 EDA 调用前因源 SDC 的比值反推存在浮点舍入差退出。采用原 holdout 的读法，校验源 SDC 的真实系数与已绑定的原 IO 语义。第二次环境准备在错误的默认顶层绑定下拒绝导出网表。第三次准备显式绑定 `aes_cipher_top` 后启动实际布线。两次准备失败均未创建候选端点。

严格零编辑按真实 DRT、重新提取、三角 STA、独立全块 DRC 和 SEC 验收。15,657 条保护线全部保持，实际日志只有一次 pin access；FF／TT／SS 各视图的 setup 与 hold WNS／TNS 完全复现冻结起点，独立全块 DRC 和天线均为零，SEC 11,089 通过、0 未证。按池顺序排在前 3 的批次另做同流程技术预检，119.945760 RAW 秒，面积收益候选 33.7824 µm²，独立物理门合格，SS 唯一相对 hold 回退 −0.157652 ps。预检与后续三臂的计时和评估分开。

在正式启动前独立读取此前两个四违例的完整 DRC 报告。自动解析分别复现 `net4840`／`net8407` 和 `_03615_`／`_08784_` 两组实体邻线。此测试仅校验真实报告语法及非时钟规则；三臂不读这些历史邻网作为策略输入。

定位实际资料的原矩阵为 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1`。零编辑及首批预检位于同目录下的 `aes_protected_online_preflight_v3`，预检结果 SHA-256 为 `79e6450453cecfcbf592ffd2a5fb1d8d04f5f3f2362cc7ce6c1cf79f357758d9`。正式原件目录为 `aes_protected_online_matched_v1`，配置 SHA-256 为 `c1b2644c615f3319b7f791bbbeaea9605a4e88920403e8009c0b2251cf311534`。[在线驱动](run_aes_protected_online.py) · [独立核验](verify_aes_protected_online.py)

## 正式在线结果

单门第一请求换 `_10814_`。恢复线型状态后的全块检查报告该单元与 `net8204` 有三处 met1 短路，自动仅放开这条邻线。一次重试把全块 DRC 计数从 3 降到 0。SS hold 从初始候选的 +55.309979 ps 变为 +55.187632 ps，低于冻结起点 0.108136 ps。该请求最终由原相对 hold 门拒绝。

单门在端到端 517.791 秒保留 `_10992_`，回收 11.2608 µm²（0.009665%），三角 setup WNS 和 hold WNS 完全复现冻结起点，SEC 通过。第三请求的两门累计网表有 22.5216 µm² 面积收益，SS 相对 hold 仍回退；第四请求的 DRT 在壁钟截止时中断。窗内只完成三次逻辑请求，最终面积略低于 0.01% 目标。截止后的约 0.135 秒是子进程终止与清理时间，无窗外结果计入。

固定批次第一请求因 SS 相对 hold 回退被拒。第二请求按未经改动的有序池派发排名 4–6 的三门。恢复 `ROUTED` 后的全块检查指出四处违例，自动放开报告里的 `net4840`／`net8407`，一次重试后 DRC 为零，SEC 11,089 已证、0 未证。固定批次由此在 532.099 秒回收 33.7824 µm²（0.028996%）并达到目标。FF／TT／SS hold WNS 分别变化 +0.000056／0／+0.610845 ps，hold TNS 均为零。SS 新增一处负 setup 端点，setup WNS/TNS 均符合原预算。网表与此前的手选 `02` 端点逐字节一致，这次的派发、DRC 邻网选择、物理计时和 SEC 均在正式在线臂中重新执行。

FAECO 通过相对 hold 延后拆分首个被拒的三门批次，下一次派发进入和固定批次相同的排名 4–6，重新得到相同的两条邻网、合格物理端点和 SEC。第二请求在端到端 529.887 秒达到同一面积目标，实际耗时与固定批次相差 2.212 秒。两方法的前三个派发完全相同，有限窗口内该结果体现了固定与自适应两臂共有的批次行为。

| 方法 | 逻辑派发／窗内完成 | 真实 DRT 调用 | 最终面积回收 / µm²（%） | 到达 0.01% 目标的端到端 RAW 秒 |
|---|---:|---:|---:|---:|
| 单门贪心 | 4／3 | 5 | 11.2608（0.009665%） | 未达到 |
| 固定批次 | 3／2 | 5 | 33.7824（0.028996%） | 532.099 |
| Hold-aware FAECO | 3／2 | 5 | 33.7824（0.028996%） | 529.887 |

各臂均执行四次独立恢复线型后的全块 DRC、十二次成功的视图 STA 和一次非空通过的 SEC。第五次 DRT 在各自端到端窗截止时中断。固定批次与 FAECO 最终候选的 ODB、DEF、Verilog、DRC 报告逐字节一致，去掉日期行后的 SPEF 同 SHA-256 `ad847a22193010de306d452ff302475ab1397df6dc6e679e2241a85b7e26c4d1`，三个视图记录也完全相同。批次的面积达标结果优于本次单门臂；在这三个相同派发上，2.212 秒的墙钟差异无法支持固定和 FAECO 的调度速度排序。

正式汇总 `aes_protected_online_matched_v1/results.json` 的 SHA-256 为 `0e5887637b4b29c9bf8fe66cf0d8f2b345185ab98f79477191745238264db33e`。独立核验复走调度的接受前缀、自动释放邻网和端到端墙钟，复核计数、SEC 物理对象与面积值，核验记录 SHA-256 为 `2d27b218fe218803964ab3bcde800217b05aac23753115631b29aea389d51b7a`。

## 截止后的单次诊断

固定和 FAECO 的第三请求为同一六门累计组合。两臂的初次独立 DRC 都报告 10 处标记，均从实际报告选出 `_01220_`、`net4840`、`net8222`、`net8407` 四条邻网。固定臂上剩 40.545 RAW 秒，FAECO 上剩 56.615 秒，两次重试的 DRT 都被壁钟中断。

同一六门和同一释放集合在独立目录完成一次重试，未重跑初试，耗时 137.305 RAW 秒。面积候选为 67.5648 µm²，恢复线型后的全块 DRC 为零，天线违例为零，三视图 setup 门和绝对 hold 门均合格。FF／TT／SS 的 hold WNS 分别为 +336.224049／+523.837196／+55.738747 ps，相对起点变化 −0.049849／−0.077660／+0.442979 ps。FF 和 TT 仍被原相对 hold 门拒绝，未进入 SEC。该后验诊断不计入三个正式结果。

最差 hold 路径与此前合格的三门保持一致。对比两份提取寄生，13 条最差路径数据和时钟网中，只有三个时钟网的观测电容有差异。相同捕获分支 `clknet_3_1__leaf_clk` 总电容增加 0.0000792 pF，其中地电容增加 0.000074512 pF。这个方向与 FF／TT 的回退一致。缩短流程能够给这轮六门候选留出核验时间，实际完成的端点仍需要解决捕获分支的相对 hold 回退。

迟到诊断 `aes_protected_online_censored_retry_v1/result.json` SHA-256 为 `4b65dfcd2857904d2a2253e6d777110af0df367ff10dd23653bccc37177fd7fb`，同目录 `path_net_deltas_vs_accepted_batch.json` SHA-256 为 `4dec64b1c6f0ce551961d3c9737229f6be409a1385c8c8c9cb91fb1b18c9bd2b`。[截止后诊断驱动](probe_aes_censored_retry.py)

## 完整原件

预检与正式三臂原件归档至 `scratch/tcad_ibex_20261123/aes_protected_online_matched_20261124.tar.gz`。压缩包 421679422 字节、597 个成员，542 个普通文件逐项 SHA-256 核对相同。压缩包 SHA-256 为 `b58edd7afd696193512d3920b752b2560950cfc7550e3dc3a1ff33ea41a50bd6`。

截止后重试的独立归档为 `scratch/tcad_ibex_20261123/aes_protected_online_censored_retry_20261124.tar.gz`，28354866 字节、49 个成员，45 个普通文件逐项 SHA-256 核对相同。压缩包 SHA-256 为 `70e35973a20e27010801d55a4b8af771634317c2b5f8bae0fd737bc8a7bb85b6`。

## 复现入口

在 WSL 的仓库根目录执行。预检和正式运行均使用新的输出目录。正式运行绑定刚完成的独立预检，三臂各重新执行自己的第一批和后续候选。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
bash code/scripts/run_with_timeout.sh 1065 taskset -c 0-5 python3 -B \
  "$e/run_aes_protected_online.py" "$raw/aes_matrix_v1" "$raw/aes_online_preflight_replay" --preflight-only
bash code/scripts/run_with_timeout.sh 2000 taskset -c 0-5 python3 -B \
  "$e/run_aes_protected_online.py" "$raw/aes_matrix_v1" "$raw/aes_online_matched_replay" \
  --verified-preflight "$raw/aes_online_preflight_replay/preflight/result.json"
python3 -B "$e/verify_aes_protected_online.py" "$raw/aes_online_matched_replay"
```

如果两方法均在同一请求的同一次确定性重试中被截止，可执行一次窗外物理诊断。

```bash
bash code/scripts/run_with_timeout.sh 450 taskset -c 0-5 python3 -B \
  "$e/probe_aes_censored_retry.py" "$raw/aes_matrix_v1" \
  "$raw/aes_online_matched_replay" "$raw/aes_online_retry_replay"
```
