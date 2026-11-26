# V5 图表与证据复核

本目录开放汇总收据、代表性原始记录、工具调用入口和无 EDA 复算。先从仓库根运行以下命令。Python 脚本只使用标准库，可从任意工作目录调用。

```bash
python3 project_docs/evidence/tcad_v5_revision_20261126/verify_review_evidence.py
bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --plan
```

[原件压缩包](V5_REVIEW_ORIGINALS.zip) SHA-256 为 `eec4d4bdc4911ec42aa31cb874c0fb9a1ebfa4a11508a19573858f9137d3237f`，包含 297 份逐字节原件和一份 SHA-256/字节数清单。目录键源自原始运行路径，复算脚本直接读取 ZIP，无需按本机路径解包。已包含 7 nm 六组标记报告、130 nm 嵌套反例的原物理收据、双 AES 探针工序台账，以及处理器 12 个合格检查点的原物理和 SEC 收据、终检记录、三角 STA 与路由日志。三臂最终交付的门级网表和 Yosys 日志也在包内。大体积 ODB、DEF、完整 SPEF 和 PDK 仍由原始运行目录或依赖路径提供。相同处理器端点的公开复算检查收据中的 ODB/DEF 指纹，作者现场另读对应原件及去日期 SPEF。该包支持审核记录与复算指标；独立完整物理重建遵循 [运行依赖与路径](README.md)。

## 主张与证据入口

| 图表或主张 | 收据、数据与重算入口 |
|---|---|
| 主基准、起序、原生和冻结 TT 全池直提 | [原生及经典参照](../tcad_external_baselines_20261125/REPORT.md) · [旧处理器同起序](../tcad_rank_alignment_20261125/REPORT.md) · [7 nm 留出](../tcad_asap7_aes_holdout_20261125/REPORT.md) · [旧处理器输入约束](../../OPEN_ISSUES.md#oi-1112026-11-26open-riscv32i-旧约束缺失输入延迟) |
| 图 3 已交付面积轨迹及历史默认探针 | [数据图生成器](../../../paper/zh/figures/tcad_20261126/generate_tcad_figures_v4_zh.py) · [历史 Hybrid 收据](../tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json) · [UART 墙钟](../tcad_wallclock_schedule_20261125/REPORT.md) |
| 图 4 放行策略、部件、批宽与历史参数 | [邻网归因](../tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json) · [2×2 后端交叉](../tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [窗口消融](../tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json) · [批宽、池规模和 UART-TC](../tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json) |
| 图 5 窗口化诊断、历史 56 标记与 7 nm 37 个注入标记 | [窗口对照](../tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) · [历史回放](../tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json) · [V5 Stage 1](V5_STEP1_POWER_7NM_DET_VERIFIED.json) · [LEF 和检查器作用域](WINDOW_RULE_SCOPE.md) |
| Hold 容差离线变化 | [既有试探计数与离线重判入口](../tcad_v4_revision_20261126/audit_hold_tolerance_and_table9.py)。UART 的 8 臂共有 200 份收据，排除 2 份预检和 62 份不具完整三视图的记录，余 136 次完成评估、62 个不同累计动作集。按请求计数，允许同一动作从不同臂进入。 |
| 去重、原生对照资格、在线 Setup 调节 | [Stage 2](V5_STEP2_DEDUP_NATIVE_VERIFIED.json) · [Stage 3](V5_STEP3_MULTIBUDGET_VERIFIED.json) |
| 双 AES 同协议探针 | [Stage 4](V5_STEP4_PROBE_SENS_VERIFIED.json)；原件包对应 `phase1_probe` 与 `phase2_fallback` |
| 独立处理器参考与三臂 | [10 ns 资格](V5_STEP5_TC10NS_QUALIFICATION.json) · [40 ns 资格](V5_STEP5_TC40NS_MMMC_QUALIFICATION.json) · [40 ns 电气护栏资格](V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json) · [Stage 5](V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json) |
| 同起序批宽、470.5 ps 零下限、资源与清理时间 | [审稿补证](REVIEW_SUPPLEMENT.md) · [同起序批宽收据](V5_REVIEW_MATCHED_BATCH_VERIFIED.json) · [近临界 STA 收据](V5_REVIEW_SETUP_FLOOR_VERIFIED.json) · [补证原件包](V5_REVIEW_SUPPLEMENT_ORIGINALS.zip) · [处理器资源复跑](V5_STAGE5_RESOURCE_REPLAY_ORIGINALS.zip) |

## 主要对照协议

| 对照 | 冻结参考、批操作与计费 | Setup/Hold、电气与交付 |
|---|---|---|
| 原生独立流程、挂保护后端准入 | 原生提议按其自身动作数；独立全片重布或保护窗口准入检查。保护后端最长试验为单次 DRT 600 s，投影另有外窗 840 s。 | 区分实例缺失、触及时钟作用域、超时未达 STA/SEC、完成后物理拒收和合格交付。 |
| 历史窗口比较 | 各自冻结参考与统一 18 项池。SKY130HD A 臂现场 TT 灵敏度排序，B/C/D 初始沿原序。ASAP7 AES 同榜。正反序仅见相应成对诊断实验。 | 参考相对逐角 Setup WNS/TNS 和 Hold WNS，源周期为 SKY130HD AES 3.6 ns、旧处理器 6 ns、ASAP7 UART 270 ps 与 ASAP7 AES 380 ps。终检物理门与 SEC 共用。 |
| UART Setup 去重与双设计 Setup 预算 | 270 ps UART／3,600 ps SKY130HD AES。窗口后端中每次派发计时，微批次，关闭全池探针；去重按各自白名单。Stage 2A 实际仅一次 FF Setup WNS 命中。 | 真正逐角改 WNS/TNS 门，Hold 门保持；允许相对合格的新增负端点，额外记录。 |
| 双 AES 探针 0/60/120/240 s | SKY130HD AES 3,600 ps／ASAP7 AES 380 ps，同一设计回退规则一致。完成的拒收可在该候选会话复用。双 0 s 新臂最后补测，旧默认及旧零臂有独立来源。 | 相对门，720 s 自已计费公共预筛开始。只有验收在窗内的端点计入曲线；工具停止、收尾和外层返回可更晚。 |
| 40 ns 处理器 | 独立重建，同一 18 项池和新鲜 TT 灵敏度起序。单门、固定三门、FAECO 微批次；均关闭探针。公共预筛 58.474014 s，参考构建与资格作为前处理单列。 | 绝对 Setup/Hold 与相对 400 ps Setup WNS、逐角 TNS 及 Hold 非退化。全角最大电容和转换时间报告、DRC、天线、SEC 完整。 |

各组共用单一工作模式。FF/TT/SS 对应标准单元库通过各冻结协议中的 Liberty 指纹定位，详细布线名义 SPEF 跨三个库角共用。Stage 5 的 SDC、公共预筛和三角报告见 ZIP 内相应协议和原件。功耗基于 OpenSTA TT 默认活动。已计费墙钟及工具子步骤台账保留。Stage 5 固定和自适应两臂后续做了整棵进程树 CPU、内存高水位和独立读者补测。 [资源与读档补测](REVIEW_SUPPLEMENT.md#40-ns-处理器配对复跑的进程树与下游读取)

## R3-1 冻结 UART 端点的异址 STA 重放

新版 [重放驱动](replay_uart_setup_floor.py) 从 V5 补证包及 UART 参考资格收据定位 20 份外部输入。先列出相对于输入根的文件路径。准备对应的已布线 ODB／SPEF、15 份 Liberty 和原 OpenROAD 可执行文件，并保留其相对层次。工具需在目标 Linux 环境中能够启动。470.5 ps SDC 由驱动从补证包中校验后写入新的输出根。

从仓库根执行以下命令，将 `/path/to/pinned-inputs` 和 `/path/to/new-results` 替换为实际路径。

```bash
driver=project_docs/evidence/tcad_v5_revision_20261126/replay_uart_setup_floor.py
python3 -E -s -B "$driver" --list-inputs
bash code/scripts/run_with_timeout.sh 120 python3 -E -s -B "$driver" \
    --inputs-root /path/to/pinned-inputs --output /path/to/new-results
```

同一 WSL 主机上的两组试验分别使用原仓库与从 `a01e1262` 提取的最小依赖树，第二组在仓库外启动。两组均使用独立目录下的 20 份输入副本。每组重跑参考与候选各 FF／TT／SS 三角。在原报告中移去包装器的 ODB 路径头，在新报告中映射回原路径，然后比较全文及解析的时序数据。两组各 6 份报告全部一致，确认参考 SS Setup WNS 为 +0.794642 ps、候选为 −0.568545 ps，仍由绝对下限独立拒收。同大小候选 SPEF 改一个字节的反例在启动 STA 前退出。此项覆盖同一主机的已布线端点分析。跨主机 PDK／工具兼容性、重新布线、寄生提取、DRC 与 SEC 的重建仍待验。

两组原始收据、SDC、Tcl、实际 STA 日志和拒收反例封装为 29 份原件及一份清单，ZIP SHA-256 为 `2f88fbf9f9ddaac023cbe473613a39a1770191e69f2d164aa4654f3f3f439a3e`。 [异址重放原件](V5_UART_STA_RELOCATED_ORIGINALS.zip)
