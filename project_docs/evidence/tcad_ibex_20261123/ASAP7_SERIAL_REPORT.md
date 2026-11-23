# ASAP7 Ibex 等面积目标的串行复跑

## 复跑口径

前轮在 1% 周期的 tradeoff 门下，单门和 FAECO 第三次评估均以同一物理端点超过 0.01% 面积目标，计时分别为 1135.931 s 和 810.920 s。单门时段与 SKY130HD 同机并行，自适应时段的 SKY130HD 已结束。本轮复用前轮冻结的 CONTROL、原始 SDC、TT/FF/SS 库、同序候选池及物理验收脚本。保持相同的 10 ps 逐角 WNS 限、逐角 TNS 限、hold、电气、DRC 和非空两态 SEC 门。目标为该 CONTROL 功能面积 2129.78808 的 0.01%，即 0.212978808。 [前轮报告](REPORT.md#asap7-主比较)

四臂从各自同一个物理 CONTROL 开始，依次运行 FAECO、单门、单门、FAECO，组成两个反序配对。全部使用同台 WSL 主机的 CPU 0–5，路由工具四线程，同一时段只有一个实验方法运行。每臂保持六次调用上限及原调度，并在首次完成目标的全部验收时停止。计时包含调度、物理、STA 和所需 SEC，用 WSL `time.monotonic()`，相邻臂不复用候选的物理结果或等价证明。共同 CONTROL 准备及零动作预检在四臂之外只执行一次。 [实际命令](ASAP7_SERIAL_COMMAND.txt) · [预登记](../EXPERIMENT_REGISTRY.md#2026-11-23-tcad-ibex-asap7-target-serial-reverse-v1)

## 同端点实测

| 串行顺序 | FAECO 达目标（s） | 单门达目标（s） | 单门减 FAECO（s） | 相对单门缩短 |
|---|---:|---:|---:|---:|
| FAECO → 单门 | 688.233 | 728.543 | 40.311 | 5.53% |
| 单门 → FAECO | 695.670 | 730.866 | 35.195 | 4.82% |

四臂均在第三次验证完成后回收 0.26244（0.012322%）。在两组顺序中，单门和 FAECO 都执行了三次 DRT/RCX 和每视图三次 STA。单门在中间端点额外取得一次 SEC，自适应在第三次证明最终的两门组合。该端点三视图 hold WNS 均为正，FF setup 从 +0.380362 ps 变为 −4.379830 ps，并新增 15 个负 setup 端点，仍符合本轮允许跨零的研究门。四次首次达标的 SEC 均为 17363/0。

| 环节 | 反序组差值（单门减 FAECO，s） | 原序组差值（单门减 FAECO，s） |
|---|---:|---:|
| DRT + RCX | +0.713 | −2.150 |
| STA | +1.016 | +0.238 |
| SEC | +38.480 | +37.066 |
| 其余开销 | +0.102 | +0.042 |
| 总差值 | +40.311 | +35.195 |

复跑的时间差方向跨顺序一致，平均为 37.753 s。两组的差主要来自额外一次 SEC，而两种策略的 DRT/RCX 实测差值方向相反。前轮混合并行负载的 325.011 s 差值缩为这两组串行观测的 35.195–40.311 s。共享零动作耗时 261.520 s，DRC=0，SEC 17363/0，四臂的耗时均单独记录。 [原始配置](ASAP7_SERIAL_CONFIG.json) · [原始结果](ASAP7_SERIAL_RESULTS.json) · [独立核验](ASAP7_SERIAL_VERIFIED.json)

## 时钟核查与归档

这里的秒为预登记的 WSL `CLOCK_MONOTONIC` 读数。十组同期抽查中，较长区间的该时钟比 Windows QPC 与 WSL `CLOCK_MONOTONIC_RAW` 快约 4.0%–4.6%，其中原序组有完整跨臂抽查，反序组缺少起始样本。保留原始读数，以共同速率因子作敏感性换算时，两组差值仍约 39 s 和 34 s。UTC 日历时间按各臂首尾相减所得的差值分别为 34.820 s 与 37.133 s，方向一致。逐样本及边界记录在时钟核查中。 [时钟核查](ASAP7_SERIAL_CLOCK_AUDIT.md)

独立核验复算全部十二次候选物理评估、三十六次视图 STA 和六次候选 SEC，缓存命中为零。四臂首次达标端点的 ODB、DEF、Verilog 字节完全一致，SPEF 只差日期。同时与前轮首次达标端点逐文件一致。原始输出为 `/home/toylog/faeco_tcad_ibex_20261123/setup_serial_asap7_v1`，完整目录归档在 `scratch/tcad_ibex_20261123/setup_serial_asap7_v1.tar.gz`，SHA-256 `b016a9f5e103c2db7281d74c69e0fe6d97486a8f85f57d609fd653df8b1fcccd`。 [独立核验脚本](verify_asap7_serial_repeat.py)
