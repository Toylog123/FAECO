# V5 图表与证据复核

本目录开放汇总收据、代表性原始记录、工具调用入口和无 EDA 复算。先从仓库根运行以下命令。Python 脚本只使用标准库，可从任意工作目录调用。

```bash
python3 project_docs/evidence/tcad_v5_revision_20261126/verify_review_evidence.py
python3 project_docs/evidence/tcad_v5_revision_20261126/generate_stage5_table12.py
python3 project_docs/evidence/tcad_v5_revision_20261126/verify_r3_final_physical_connectivity.py
bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --plan
```

[原件压缩包](V5_REVIEW_ORIGINALS.zip) SHA-256 为 `eec4d4bdc4911ec42aa31cb874c0fb9a1ebfa4a11508a19573858f9137d3237f`，包含 297 份逐字节原件和一份 SHA-256/字节数清单。目录键源自原始运行路径，复算脚本直接读取 ZIP，无需按本机路径解包。已包含 7 nm 六组标记报告、130 nm 嵌套反例的原物理收据、双 AES 探针工序台账，以及处理器 12 个合格检查点的原物理和 SEC 收据、终检记录、三角 STA 与路由日志。三臂最终交付的门级网表和 Yosys 日志也在包内。大体积 ODB、DEF、完整 SPEF 和 PDK 仍由原始运行目录或依赖路径提供。相同处理器端点的公开复算检查收据中的 ODB/DEF 指纹，作者现场另读对应原件及去日期 SPEF。该包支持审核记录与复算指标；独立完整物理重建遵循 [运行依赖与路径](README.md)。

## 第十轮固定协议反例

正文图 4(a) 使用同一执行器的三门和十八门既有记录。归档包括动作身份、各阶段实际限时、终检及 SEC 收据。旧 Hybrid 端点及计时表继续按其历史子预算解释。 [原件与复算](../tcad_r10_counterexample_20261127/REPORT.md)

## 第九轮机制图校对

理论图、搜索图和真实版图图均采用矢量工件。图 3(b) 的放大框直接读取原有坐标，审计同时回读冻结归档的 DEF 和全块 DRC 报告。第九轮保留第八轮实验表和第七轮独立补件。 [核验明细](../../../paper/zh/review_rounds/r20261127_r9_proof/R9_REVIEW_MAP.md)

## 第八轮机制图与既有证据

正文图 2 解释几何覆盖与检查上下文，图 4(a) 使用冻结 SKY130HD AES 子集反例，图 4(b)、(c) 是调度示意。原真实版图图、诊断性能图和限时轨迹图的现行图号为 3、5、6。各原始实验协议、数据、表号及补件继续使用第七轮口径。 [逐图和证据复核](../../../paper/zh/review_rounds/r20261127_r8_mechanism/R8_REVIEW_MAP.md)

## 第七轮中文稿复算指引

当前图 3 为局部诊断性能，图 4 为限时交付轨迹，表号沿用第六轮。表 2 将正反序各臂的原精度均值分别等权汇总，14.39 s 和 7.02 s 取自原诊断收据。实验、版图、候选与验收保持原冻结身份。详表集中于独立补件附录 A–G。 [逐条复核](../../../paper/zh/review_rounds/r20261127_r7_editorial/R7_REVIEW_MAP.md) · [图件数据](../../../paper/zh/figures/tcad_20261126/R7_FIGURE_NOTES.md)

## 第六轮中文稿图表映射

R6 调整图表编号与论证顺序，冻结实验仍由原收据复算。当前主稿表 2 对应原表 9；表 3 对应原表 6、7；表 4 对应原全景表；表 5 对应原配置消融；表 6 合并原表 5、11；表 7 合并 UART-TC 与40 ns 处理器三臂。下方历史编号用于定位原证据。 [逐条映射和随稿补件](../../../paper/zh/review_rounds/r20261127_r6_editorial/R6_REVIEW_MAP.md)

- [图 2 真实 DEF 与 DRC 标记、重建步骤](../../../paper/zh/figures/tcad_20261126/FIG2_AES_GEOMETRY_R6.md)
- [图 3、4 冻结输入 SHA-256、可复绘数据和脚本](../../../paper/zh/figures/tcad_20261126/R6_FIG3_FIG4.md)

## 主张与证据入口

| 图表或主张 | 收据、数据与重算入口 |
|---|---|
| 主基准、起序、原生和冻结 TT 全池直提 | [原生及经典参照](../tcad_external_baselines_20261125/REPORT.md) · [旧处理器同起序](../tcad_rank_alignment_20261125/REPORT.md) · [7 nm 留出](../tcad_asap7_aes_holdout_20261125/REPORT.md) · [旧处理器输入约束](../../OPEN_ISSUES.md#oi-1112026-11-26open-riscv32i-旧约束缺失输入延迟) |
| 图 3 已交付面积轨迹及历史默认探针 | [数据图生成器](../../../paper/zh/figures/tcad_20261126/generate_tcad_figures_v4_zh.py) · [历史 Hybrid 收据](../tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json) · [UART 墙钟](../tcad_wallclock_schedule_20261125/REPORT.md) |
| 图 4 放行策略、部件、批宽与历史参数 | [邻网归因](../tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json) · [2×2 后端交叉](../tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [窗口消融](../tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json) · [批宽、池规模和 UART-TC](../tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json) |
| 图 5 窗口化诊断、历史 56 标记与 7 nm 37 个注入标记 | [窗口对照](../tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) · [历史回放](../tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json) · [V5 Stage 1](V5_STEP1_POWER_7NM_DET_VERIFIED.json) · [LEF 和检查器作用域](WINDOW_RULE_SCOPE.md) |
| §6 同提议的等数量单邻网预放行 | [几何择一与事后已知邻网报告](../tcad_ibex_20261123/GCD_GEOMETRY_RELEASE_REPORT.md) · [226 份原件](../tcad_ibex_20261123/GCD_GEOMETRY_RELEASE_ORIGINALS.zip) · [离线复算](../tcad_ibex_20261123/verify_gcd_geometry_archive.py) |
| §6 非 AES 固定提议的预检阶段对照 | [SKY130HD GCD 三臂](../tcad_ibex_20261123/GCD_WINDOW_DIAGNOSIS_REPORT.md) · [321 份原件](../tcad_ibex_20261123/GCD_WINDOW_DIAGNOSIS_ORIGINALS.zip) · [离线复算](../tcad_ibex_20261123/verify_gcd_window_archive.py) |
| 表 4 历史端点 TT 功耗 | [33 份原 Tcl、报告、日志及 SDC](R3_TABLE4_TT_POWER_ORIGINALS.zip) · [端点绑定与图表复核](../../../paper/zh/review_rounds/r20261127_r3_submission/DISPLAY_EVIDENCE_AUDIT.md) |
| 40 ns 处理器第三轮主表与历史口径 | [表 12 复算程序](generate_stage5_table12.py) · [同次运行指标](V5_STAGE5_TABLE12.json) · [第三轮规则与原生动作诊断](../../../paper/zh/review_rounds/r20261127_r3_submission/R3_EVIDENCE.md) · [历史臂配置](../../../paper/zh/review_rounds/r20261127_r3_submission/R3_HISTORICAL_CONFIG.md) |
| 40 ns 处理器最终版图布局与供电连通 | [参考及三个最终 ODB 的核验](R3_FINAL_PHYSICAL_CONNECTIVITY_REPORT.md) · [51 份原件](R3_FINAL_PHYSICAL_CONNECTIVITY_ORIGINALS.zip) · [离线复算](verify_r3_final_physical_connectivity.py) |
| Hold 容差离线变化 | [既有试探计数与离线重判入口](../tcad_v4_revision_20261126/audit_hold_tolerance_and_table9.py)。UART 的 8 臂共有 200 份收据，排除 2 份预检和 62 份不具完整三视图的记录，余 136 次完成评估、62 个不同累计动作集。按请求计数，允许同一动作从不同臂进入。 |
| 去重、原生对照资格、在线 Setup 调节 | [Stage 2](V5_STEP2_DEDUP_NATIVE_VERIFIED.json) · [Stage 3](V5_STEP3_MULTIBUDGET_VERIFIED.json) |
| 双 AES 同协议探针 | [Stage 4](V5_STEP4_PROBE_SENS_VERIFIED.json)；原件包对应 `phase1_probe` 与 `phase2_fallback` |
| 独立处理器参考与三臂 | [10 ns 资格](V5_STEP5_TC10NS_QUALIFICATION.json) · [40 ns 资格](V5_STEP5_TC40NS_MMMC_QUALIFICATION.json) · [40 ns 电气护栏资格](V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json) · [Stage 5](V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json) |
| 同起序批宽、470.5 ps 零下限、资源与清理时间 | [审稿补证](REVIEW_SUPPLEMENT.md) · [同起序批宽收据](V5_REVIEW_MATCHED_BATCH_VERIFIED.json) · [近临界 STA 收据](V5_REVIEW_SETUP_FLOOR_VERIFIED.json) · [补证原件包](V5_REVIEW_SUPPLEMENT_ORIGINALS.zip) · [处理器资源复跑](V5_STAGE5_RESOURCE_REPLAY_ORIGINALS.zip) |
| 40 ns 同池同后端的外部排序 | [AuDoPEDA 排序投影](REVIEW_SUPPLEMENT.md#40-ns-处理器同池同后端的外部排序对照) · [对照原件](V5_AUDOPEDA_RANK_CONTROL_ORIGINALS.zip) |
| 小 UART、双 AES 的阶段成本和进程树峰值 | [三项冻结候选资源](REVIEW_SUPPLEMENT.md#小-uart-与两项最大代表设计的阶段资源) · [测量原件](V5_V4_STAGE_RESOURCE_CASES_ORIGINALS.zip) |

## 主要对照协议

| 对照 | 冻结参考、批操作与计费 | Setup/Hold、电气与交付 |
|---|---|---|
| 原生独立流程、挂保护后端准入 | 原生提议按其自身动作数；独立全片重布或保护窗口准入检查。保护后端最长试验为单次 DRT 600 s，投影另有外窗 840 s。 | 区分动作绑定失败、触及时钟作用域、超时未达 STA/SEC、完成后物理拒收和合格交付。 |
| 历史窗口比较 | 各自冻结参考与统一 18 项池。SKY130HD A 臂现场 TT 灵敏度排序，B/C/D 初始沿原序。ASAP7 AES 同榜。正反序仅见相应成对诊断实验。 | 参考相对逐角 Setup WNS/TNS 和 Hold WNS，源周期为 SKY130HD AES 3.6 ns、旧处理器 6 ns、ASAP7 UART 270 ps 与 ASAP7 AES 380 ps。终检物理门与 SEC 共用。 |
| UART Setup 去重与双设计 Setup 预算 | 270 ps UART／3,600 ps SKY130HD AES。窗口后端中每次派发计时，微批次，关闭全池探针；去重按各自白名单。Stage 2A 实际仅一次 FF Setup WNS 命中。 | 真正逐角改 WNS/TNS 门，Hold 门保持；允许相对合格的新增负端点，额外记录。 |
| 双 AES 探针 0/60/120/240 s | SKY130HD AES 3,600 ps／ASAP7 AES 380 ps，同一设计回退规则一致。完成的拒收可在该候选会话复用。双 0 s 新臂最后补测，旧默认及旧零臂有独立来源。 | 相对门，720 s 自已计费公共预筛开始。只有验收在窗内的端点计入曲线；工具停止、收尾和外层返回可更晚。 |
| 40 ns 处理器初次正式运行（历史） | 独立重建，同一 18 项池和新鲜 TT 灵敏度起序。单门、固定三门、FAECO 微批次均关闭探针。公共预筛 58.474014 s，参考构建与资格单列。 [历史收据](V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json) | 绝对 Setup/Hold、相对 Setup WNS 预算 400 ps、逐角 TNS、Hold 非退化。全角电气、DRC、天线、SEC。 |
| 40 ns 处理器 SEC 修复后隔离运行（表 12） | 从同一冻结参考重做预筛。三臂共享 18 项池，现场各计费 TT 起序并关闭探针。公共预筛 **61.149943 s** 分别计入三臂的 720 s。 [表 12 生成结果](V5_STAGE5_TABLE12.json) · [修复后完整记录](#sec-修复后的完整三臂验证) | 沿用前述验收门及原参考构建、资格单列口径。 |

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

## 从独立输入副本重建 40 ns 处理器参考

在同一 WSL 主机上用普通用户启动独立用户、挂载与网络命名空间。FAECO 驱动从 `c4ede33d` 清洁提取，ORFS 工作树绑定 `da8f092a02a8e75658cc3100691aabff05f35629`。对拷贝输入中的 25,656 个文件与 121 个符号链接检查路径和字节。外层遮蔽原 `/home`、`/mnt` 与原 `/usr/local/bin`，将冻结副本只读挂载到历史脚本使用的内部路径。运行中从活动 PID 验证三种命名空间不同、三个别名指向只读副本，并确认旧的 Stage 5 输出在该进程中不可见。隔离环境沿用这台主机的 Linux 内核、基础系统工具和系统库。

| 从 RTL 新建的参考检查 | 新旧对照 |
| --- | --- |
| 合成、布局、布线和寄生提取 | ORFS 冷起点完整返回，原构建协议在替换输出根后逐字段一致 |
| ODB、DEF、Verilog、SDC | 四项 SHA-256 完全一致 |
| SPEF | 仅 `*DATE` 行不同，保留该行标签并统一内容后逐字节一致 |
| 独立三角 STA、电气与 I/O | 数据全同，65 个非时钟输入和 99 个输出覆盖，Setup/Hold TNS 零 |
| 原生物理、独立 DRC 与天线 | 全零，独立 DEF 读回指纹与原一致 |
| 等价检查 | 参考自检，4559 个等价点、零未证 |

归档包括重建物理产物、原始 SPEF、三角与终检收据、活动命名空间记录和输入清单，49 个索引成员及索引自身。ZIP SHA-256 为 `8941e1fde843880a3c701f1114a0b4ac48633080e4c42ead49e74e0ff656891e`。 [隔离重建原件](V5_STAGE5_ISOLATED_REBUILD_ORIGINALS.zip)

在原有冻结安装上，用命名空间驱动捕获输入，在已挂载标签之外选择新目录。换一套 Linux 主机时可搬运捕获目录，再从新环境验证清单与工具启动；完整异机运行待验证。脚本使用 Linux rootless user/mount/net namespace、GNU 工具、Git、rsync、Python、make 和兼容的动态加载环境。

```bash
# 从 FAECO 仓库根运行，三个变量均使用 Linux 路径。
driver=project_docs/evidence/tcad_v5_revision_20261126/stage5_rebuild_namespace.sh
bundle=/var/tmp/faeco_stage5_input
output=/var/tmp/faeco_stage5_reference
bash "$driver" capture "$PWD" "$bundle"
bash "$bundle/driver.sh" probe "$bundle"
bash code/scripts/run_with_timeout.sh 2400 taskset -c 0-5 \
    bash "$bundle/driver.sh" run "$bundle" "$output"
```

同时运行其他 FAECO 试验时沿用该安装的共享 EDA 锁。第一次隔离重建在 ABC 已生成 BLIF 后未返回，独立对照中缺少 `TERM` 的长临时路径同样停滞，恢复 `TERM=xterm-256color` 后小网表和完整构建均完成。归档保留中止收据和对照日志。固定版本的 Yosys 源码显示持久 ABC 流程等待命令回显及完成提示。 [Yosys 固定源码](https://github.com/YosysHQ/yosys/blob/72b0054f0/passes/techmap/abc.cc#L1097-L1168)

### 重建参考后的固定首批

以新参考的独立资格收据为输入，重新执行冻结版预筛、零改动资格和 TT 灵敏度排序。18 项候选、策略／门语义及全序与历史一致后，派发原固定三门的第一批。新候选完成 DRT、RCX、三角 STA、电气、独立 DRC／天线和候选相对新参考的 SEC，合格回收 23.7728 µm²，等价点为 4559／0。新旧候选的 ODB、DEF、Verilog 指纹完全相同，SPEF 仅日期行不同，时序和电气结果一致。原参考、首批来源和实际输出各自绑定。此重放覆盖物理验收，在线复跑包含首个固定批次。

候选驱动放在挂载之外，复用上一节已经核验并完成参考资格的输入与输出。下方两个新路径使用同一主机的普通用户可写目录。

```bash
candidate_driver=/var/tmp/faeco_stage5_candidate.py
candidate_output=/var/tmp/faeco_stage5_first_candidate
cp project_docs/evidence/tcad_v5_revision_20261126/replay_stage5_fixed_first.py "$candidate_driver"
bash code/scripts/run_with_timeout.sh 1540 taskset -c 0-5 \
    bash "$bundle/driver.sh" candidate "$bundle" "$candidate_driver" "$output" "$candidate_output"
python3 project_docs/evidence/tcad_v5_revision_20261126/verify_stage5_isolated_evidence.py
```

候选原件包含 35 个索引成员及清单，包含新旧首批的完整 SEC 脚本与日志，ZIP SHA-256 为 `a64d850c924d79f1e2e8865f7368db447069d93465b382f685f19f2e301531af`。无 EDA 核查脚本校验两个包、四类物理字节、SPEF、三角报告和绑定到参考的候选 SEC。 [首批重建原件](V5_STAGE5_ISOLATED_FIRST_CANDIDATE_ORIGINALS.zip) · [两包复核脚本](verify_stage5_isolated_evidence.py)

### 重建参考后的三臂在线搜索

同一 WSL 主机从新的物理参考复跑 720 s 的单门、固定三门和自适应臂。新预筛实测 59.791620 s，三臂各执行一次窗内 TT 排序并得到冻结的 18 项全序。输入清单与上一节相同。活动进程的用户、挂载和网络命名空间与观察者不同，旧 Stage 5 输出根在工作进程内不可见。外层运行 2100 s 并返回 0。 [复算收据](V5_STAGE5_ISOLATED_ONLINE_VERIFIED.json)

| 调度 | 原运行派发/完成/接受 | 隔离复跑派发/完成/接受 | 原／新终态面积（µm²） | 原／新时间均值（µm²） |
| --- | --- | --- | ---: | ---: |
| 单门 | 9/8/6 | 8/7/5 | 48.7968／40.0384 | 23.0862／22.6610 |
| 固定三门 | 6/6/4 | 6/6/4 | 91.3376／91.3376 | 38.4928／36.7427 |
| 自适应 | 6/5/2 | 6/5/2 | 31.2800／31.2800 | 23.5088／23.3011 |

18 次共同完成的请求逐次重现动作、拒收原因、复修及门判定。最终物理评估的 ODB、DEF、Verilog 和 DRC 指纹一致，SPEF 去除唯一 `*DATE` 行内容后相同。新运行 11 个已验收检查点的 44 份物理工件、时序、DRC、天线及非空 SEC 均进入独立核验。固定三门均自然耗尽，自适应两次均在第 6 次 DRT 被截停。新单门在第 8 次的 SEC 包装器触限，旧运行完成该请求并在第 9 次 DRT 触限。新第 8 次的路由、寄生、三角和独立 DRC 与对应旧端点一致，当时没有窗内 SEC 收据。端点计数和时间均值以各自实际窗口为准。

同一轮隔离原件中，20 次完成的原位诊断覆盖 13 个唯一累计提议，均无标记。首轮详细布线后，19 次完成独立 DRC 的请求有 5 次检出标记，涉及 3 个唯一提议和 6 个按提议去重的标记。其余 1 次在 DRT 截停。两次复修的独立 DRC 均清零，最终均因 SS 相对保持时间门拒收。这些标记出现在独立布线后检查，原位预检均为零。三臂共用窗口后端，结果覆盖诊断的阶段边界。 [原件普查脚本](verify_stage5_marker_census.py)

| 归档 | 索引原件数 | ZIP SHA-256 |
| --- | ---: | --- |
| [公共输入与运行原件](V5_STAGE5_ISOLATED_ONLINE_COMMON.zip) | 125 | `8d41ca26aa2e6552ac851546722ffb257db2b79c4b1153c7dbeedb03b2c5e860` |
| [单门](V5_STAGE5_ISOLATED_ONLINE_SINGLE_BOXED.zip) | 704 | `e94b27dcec4501785e0959913578550f504ab2a6e7f74b2ce81f721b8c360d86` |
| [固定三门](V5_STAGE5_ISOLATED_ONLINE_FIXED_BOXED.zip) | 572 | `87bbd4657cae6226dc0de88eed5f9e5e0d36a8fc179867306abdae34291e0f1d` |
| [自适应](V5_STAGE5_ISOLATED_ONLINE_FAECO_BOXED.zip) | 428 | `042e626fb3b2cf49ca022df25860af341ebdd570946ba85c585a66e547bb88b7` |

以已经完成重建的 `output` 和经过预检的 `bundle` 作为输入，驱动及结果须位于命名空间可见的可写路径。运行以历史冻结 SEC 实现复现既有对照，修复验证另见下节。

```bash
e=project_docs/evidence/tcad_v5_revision_20261126
drivers=$(mktemp -d /var/tmp/faeco_stage5_online_tools.XXXXXX)
cp "$e/replay_stage5_online.py" "$e/replay_stage5_fixed_first.py" "$drivers/"
online_output=/var/tmp/faeco_stage5_online_new
lock=/home/toylog/faeco_v5_eda.lock
bash code/scripts/run_with_timeout.sh 3020 flock -w 8 "$lock" \
    timeout --signal=TERM --kill-after=8s 3000s taskset -c 0-5 \
    bash "$bundle/driver.sh" candidate "$bundle" "$drivers/replay_stage5_online.py" "$output" "$online_output"
```

以下绝对路径是原始收据内的归档映射键。离线复算使用 Python 3.11 或更新版本，可在其他主机运行，无需这些 Linux 目录存在。Windows 原生 Python 复算与 WSL 现场复算的 JSON 各字段一致。

```bash
e=project_docs/evidence/tcad_v5_revision_20261126
p="$e/V5_STAGE5_ISOLATED_ONLINE"
python3 -B "$e/verify_stage5_isolated_online.py" \
    --new-state /var/tmp/faeco_v6_stage5_online_20261127_v1/stage5_progress.json \
    --replay-map /var/tmp/faeco_v6_stage5_rebuilt_20261127_v2/qualification=reference \
    --replay-zip "${p}_COMMON.zip" \
    --historical-zip "${p}_SINGLE_BOXED.zip" --replay-zip "${p}_SINGLE_BOXED.zip" \
    --historical-zip "${p}_FIXED_BOXED.zip" --replay-zip "${p}_FIXED_BOXED.zip" \
    --historical-zip "${p}_FAECO_BOXED.zip" --replay-zip "${p}_FAECO_BOXED.zip"
```

### SEC 截停和后置修复验证

隔离单门第 8 次的外层 SEC 在剩余 1.717614 s 时返回超时，没有生成验收收据。原实现的内层 GNU timeout 建立另一进程组，Yosys 继续写完 4559/0 的原始证明日志。末次写入晚于下一固定三门 TT 排序日志约 2.420 s。固定排序发生过跨臂工序重叠，本轮固定时间均值为该运行的观测值。

冻结三臂运行结束后，使用同一参考、同一第 8 次候选、同一 TT 库与 Yosys 做独立对照。原版在 1.717614 s 截停后仍观测到两进程并继续写日志，修复版在相同时限后未再观测到证明进程，日志大小保持 784,150 字节。两次短窗均未发布验收收据。修复版用 30 s 余量在 7.946 s 完成真实 SEC，输出 4559/0 的收据。修复将内层 `timeout --foreground` 留在外层 RAW 工具进程组。此项核验覆盖被测 SEC 链。修复后的完整在线复跑见下节，所有阶段的硬返回仍待验证。 [29 份原件](V5_STAGE5_SEC_CUTOFF_ORIGINALS.zip) · [离线核对](verify_stage5_sec_cutoff.py)

```bash
python3 -B project_docs/evidence/tcad_v5_revision_20261126/verify_stage5_sec_cutoff.py
```

### SEC 修复后的完整三臂验证

新建隔离输入副本。25,656 项文件清单只有 `prove_ibex.py` 的 SHA 变化，路径和符号链接清单保持一致。负对照用未修复输入运行新入口，在 EDA 前拒收。正式运行仍从同一 40 ns 物理参考重新预筛和排序。61.149943 s 预筛费用计入各臂各自的 720 s 账本。独立观察器固定在不同核心，对工作进程的私有挂载命名空间采样。两轮是同一物理主机上的不同 WSL 会话，墙钟价值限于单次观察。 [修复复算收据](V5_STAGE5_SEC_FIXED_VERIFIED.json)

| 调度 | 修复后派发/完成/接受 | 修复前后隔离运行终态（µm²） | 修复前／后隔离时间均值（µm²） | 修复后停止 |
| --- | --- | ---: | ---: | --- |
| 单门 | 8/7/5 | 40.0384／40.0384 | 22.6610／22.7497 | 第 8 次 SEC 触限 |
| 固定三门 | 6/6/4 | 91.3376／91.3376 | 36.7427／37.3614 | 自然耗尽 |
| 自适应 | 6/5/2 | 31.2800／31.2800 | 23.3011／23.3685 | 第 6 次 DRT 触限 |

修复前后 18 次共同完成的请求逐一重现动作、验收、复修和物理结果，11 个新接受点均绑定实际候选动作及 SEC。单门第 8 次仍在 SEC 触限。其 ODB、DEF、Verilog、去日期 SPEF、三角 STA 和独立 DRC 与旧隔离运行一致。该次 SEC 的余量为 4.950455 s。包装器结束后首个样本在约 35.1 ms 时已看不到包装器、计时器和 Yosys，距固定三门起序还有约 1.849 s。该候选仍无 SEC 收据。全轮采样 10,523 次，最大采样间隙为 0.222 s，观察到的 13 组完整 SEC 三元组均同进程组，采样未见跨臂重叠。外层包装器约 2100 s 返回 0。硬返回保证仍需覆盖系统负载、调度与其他工具的边界。

| 归档 | 新原件数 | ZIP SHA-256 |
| --- | ---: | --- |
| [公共账本、输入和观测](V5_STAGE5_SEC_FIXED_COMMON.zip) | 136 | `665d7fffa00fa2b5a858aff5e1da2a4da29f7180e600799c3c29a589b72120db` |
| [单门](V5_STAGE5_SEC_FIXED_SINGLE_BOXED.zip) | 334 | `91af7083b475f2dea8e6e8f201102bfbf7c974130471b66a1cec3d95f19395a6` |
| [固定三门](V5_STAGE5_SEC_FIXED_FIXED_BOXED.zip) | 280 | `e66ece78348ed9cdd16a9fd89f724173243a07fc3955a664eb4da3e959fb90f2` |
| [自适应](V5_STAGE5_SEC_FIXED_FAECO_BOXED.zip) | 211 | `5f6a0e1a54c61ff622e861f0ec3e4fef966f172bf1068dc3ada8290508b4d852` |

四包共 961 项新原件。36 个已发布相同物理文件以旧包成员、字节数和 SHA 引用，离线验证同时核对旧包与本轮实际收据。用 Python 3.11 或更新版本从仓库运行以下复算，命令中的候选根沿用收据内的路径键。

```bash
e=project_docs/evidence/tcad_v5_revision_20261126
p="$e/V5_STAGE5_SEC_FIXED"
python3 -B "$e/verify_stage5_sec_fixed_replay.py" \
    --fixed-zip "${p}_COMMON.zip" --fixed-zip "${p}_SINGLE_BOXED.zip" \
    --fixed-zip "${p}_FIXED_BOXED.zip" --fixed-zip "${p}_FAECO_BOXED.zip"
```

实跑复用上一节的 `bundle` 和已重建的 `output`。把新的副本与驱动、候选输出设在隔离命名空间可见路径，沿用同一 EDA 锁和分核观察。

```bash
fixed_bundle=/var/tmp/faeco_stage5_input_sec_fixed
fixed_run=/var/tmp/faeco_stage5_online_sec_fixed
dirs=$(mktemp -d /var/tmp/faeco_stage5_sec_fixed_tools.XXXXXX)
bash "$e/prepare_stage5_sec_fixed_bundle.sh" "$bundle" "$fixed_bundle" \
    project_docs/evidence/tcad_ibex_20261123/prove_ibex.py
cp "$e/replay_stage5_sec_fixed.py" "$e/replay_stage5_online.py" "$e/replay_stage5_fixed_first.py" "$dirs/"
bash code/scripts/run_with_timeout.sh 3020 flock -w 8 /home/toylog/faeco_v5_eda.lock \
    timeout --signal=TERM --kill-after=8s 3000s taskset -c 0-5 \
    bash "$fixed_bundle/driver.sh" candidate "$fixed_bundle" "$dirs/replay_stage5_sec_fixed.py" "$output" "$fixed_run"
```

在实跑派发之前，从另一个终端启动 `taskset -c 6 python3 -B "$e/observe_stage5_arm_processes.py" "$fixed_run" "$dirs/observations.jsonl"`。观察器先等运行协议，然后采样到退出尾段。

## 第四轮专项证据

第四轮沿用 SEC 清理修复的 40 ns 三臂和原 ASAP7 主试验。ASAP7 分母从完整功能实例与 OpenDB master 面积复算，历史运行账本保留其取数来源。第四轮回执及论文口径见[逐条复核](../../../paper/zh/review_rounds/r20261127_r4_submission/R4_REVIEW_MAP.md)。

| 核验 | 入口 |
| --- | --- |
| ASAP7 参考面积与候选池 | [完整库字段、原 18 项和物理面积](R4_ASAP7_LIBERTY_AUDIT.md) · [复算原件](R4_ASAP7_LIBERTY_AUDIT.zip) · [审计程序](audit_r4_asap7_liberty.py) · [20 个已交付端点净面积](R4_ASAP7_AREA_ENDPOINT_READBACK.json) |
| 40 ns 处理器终态三工艺角时序及功耗收敛 | [终态时序与传播轨迹](R4_STAGE5_POWER_TIMING_REPORT.md) · [13 份原件](R4_STAGE5_POWER_TRACE_ORIGINALS.zip) · [离线复核](verify_r4_stage5_power_trace.py) · [固定二进制诊断](replay_r4_stage5_power_trace.py) |
| ASAP7 UART 原生标准提议的共同物理后端 | [16 项重放与拒因](R4_ASAP7_NATIVE_UART_PROTECTED.md) · [81 份原件](R4_ASAP7_NATIVE_UART_PROTECTED_ORIGINALS.zip) · [固定执行入口](replay_r4_asap7_native_uart.py) |
| 参考文献、历史派发限制、同起序批宽和图表配置 | [第四轮逐条复核](../../../paper/zh/review_rounds/r20261127_r4_submission/R4_REVIEW_MAP.md) · [同起序原件与收据](REVIEW_SUPPLEMENT.md) |

R4 各入口按其所在 Git 提交定位。旧的统计、测试条件和物理运行通过对应归档、成员与 SHA-256 回读。论文附证中的同机冻结输入重放与另机完整物理重建的先决条件见各实验说明。

## 第五轮定稿证据

| 核验 | 入口 |
| --- | --- |
| ASAP7 UART K=9、K=36 及实际派发账本 | [扩展池复算结果](R5_ASAP7_UART_POOL_AUDIT.md) · [103 项证据](R5_ASAP7_UART_POOL_AUDIT.zip) · [执行入口](audit_r5_uart_pool.py) |
| 冻结端点的独立 OpenDB 功能面积 | [面积和实例分类核验](R5_DIRECT_ODB_AREA_REPORT.md) · [只读清单与原始导出](R5_DIRECT_ODB_AREA_AUDIT.zip) · [可移植复核与现场入口](audit_r5_direct_odb_area.py) |
| 稿件源、版图证据和运行程序的版本对应 | [第五轮逐条复核](../../../paper/zh/review_rounds/r20261127_r5_submission/R5_REVIEW_MAP.md) · [定稿版本清单](https://github.com/Toylog123/FAECO/blob/faeco-paper-final-20261127-r5/paper/zh/review_rounds/r20261127_r5_submission/R5_RELEASE_MANIFEST.json) |

表 10 的 K=36 回收和捕获率取自原冻结池。面积字段规范化保留 K=9、K=18 及历史 K=36 的前 18 项，后 18 项发生变化。直接 OpenDB 复核覆盖 4 条参考记录与 25 条交付记录。两项审计通过保存的归档和冻结资产分别复算，沿用当前工具与 PDK 依赖说明。
