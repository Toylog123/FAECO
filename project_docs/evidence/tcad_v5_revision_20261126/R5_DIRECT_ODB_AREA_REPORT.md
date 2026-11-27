# 第五轮 OpenDB 面积直读审计

审计覆盖 4 个冻结参考和 25 个关键终态，共 29 条读取记录，对应 22 份不同 ODB 指纹。全部 20 条 ASAP7 结果行与第四轮的表 4、表 10 回读清单逐条对齐，另读入 SKY130HD AES 的 9 门微批终态、18 门成功探针终态，以及表 12 修复后隔离复跑的三个 40 ns 处理器终态。旧 6 ns 处理器使用其历史记录。表 10 的 500 ps 固定批与表 4 UART 固定批有一组相同 ODB 指纹，另有三组跨配置的相同字节实例。每条结果保留各自物理收据和约束批次的归属。 [ASAP7 上轮回读清单](R4_ASAP7_AREA_ENDPOINT_READBACK.json) · [40 ns 主表](V5_STAGE5_TABLE12.json)

## 功能单元口径

固定原运行 OpenROAD 可执行文件并检查 SHA-256。对每个 ODB 只执行 `read_db`，逐个读取实例名、master 名、`getType`、`getWidth` 和 `getHeight`，所有版图均为 1000 DBU/µm。功能类保留 `CORE`、`CORE_FEEDTHRU`、`CORE_TIEHIGH`、`CORE_TIELOW`，排除物理类 `CORE_SPACER`、`CORE_WELLTAP`、`CORE_ANTENNACELL`。实际实例只出现功能类 `CORE` 和上述三个物理类，SKY130HD 处理器的逻辑 `conb_1` 实例作为 `CORE` 保留。每个用数据库类型筛出的功能实例集合和 master 映射，均与独立递归解析同次冻结 Verilog 得到的完整叶实例映射一致。SKY130HD AES 与处理器的 57、5 个物理天线二极管均未出现在对应功能网表。

| 冻结参考 | 功能实例 | Filler | Well tap | Antenna | 功能面积（µm²） | 计入所有物理实例的面积（µm²） |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ASAP7 UART | 765 | 937 | 110 | 0 | 101.89962 | 221.32440 |
| ASAP7 AES | 12,180 | 10,228 | 411 | 0 | 1414.39122 | 1975.06512 |
| SKY130HD AES | 15,487 | 20,345 | 2,838 | 57 | 116507.9904 | 214618.3360 |
| 40 ns SKY130HD 处理器 | 5,456 | 11,673 | 1,863 | 5 | 69750.6464 | 138002.3552 |

表末列用于检查口径。错误地计入填充、电源接触和物理天线单元会放大参考面积。本批替换的物理单元总面积保持一致，因而全部实例的净面积差仍等于功能净面积差。面积降幅使用功能面积作为分母。

## 净面积双路径复算

第一条路径从两个实际 ODB 独立累计功能 master 的宽乘高，取 `A_ODB(R) − A_ODB(F(S))`。第二条路径逐项读取接受收据中的 `S`，取参考和端点 ODB 中该实例的实际源、目标 master 面积差之和。两者在整数 DBU² 上完全相等，且与公布净面积相符。25/25 个终态的功能实例名集合不变，变化的实例及目标 master 与接受动作严格一一对应，未列入动作的功能实例 master 及面积均无偏差。

| 样例 | 动作数 | 终态功能面积（µm²） | 两种方法的净面积（µm²） |
| --- | ---: | ---: | ---: |
| ASAP7 UART，K=9 | 7 | 101.40390 | 0.49572 |
| ASAP7 UART，K=36 | 19 | 100.39788 | 1.50174 |
| ASAP7 AES，纯微批 | 6 | 1413.77886 | 0.61236 |
| SKY130HD AES，纯微批 | 9 | 116409.1456 | 98.8448 |
| SKY130HD AES，整池探针 | 18 | 116310.3008 | 197.6896 |
| 40 ns 处理器，单门 | 5 | 69710.6080 | 40.0384 |
| 40 ns 处理器，固定三门 | 12 | 69659.3088 | 91.3376 |
| 40 ns 处理器，FAECO | 4 | 69719.3664 | 31.2800 |

离线负对照分别删除一项接受动作，以及把 `CORE_SPACER` 类型强制纳入功能白名单。第一项在接受动作集合核对处被拒，第二项在独立网表的功能实例核对处被拒。两次均只在内存中改动。

## 冻结与复算

原二进制为 WSL 中 `/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped`，SHA-256 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。读取在共享 EDA 锁、CPU 0–5、一线程下串行运行，逐对象 8 s、外层 120 s。正式复核 16 s、退出码 0。原始 ODB 在各次读取前后复核字节数与 SHA-256，未发生写回。首轮 29 份 ODB 均读出，脚本随后在处理器网表顶层的假定名称处中止。正式复核从表 12 已绑定的协议读取顶层 `riscv`。两轮没有启动布局或布线。

[审计 ZIP](R5_DIRECT_ODB_AREA_AUDIT.zip)含直接 ODB TSV、同次 Verilog、Tcl、原始读取日志、输入指纹、逐对象汇总和成员清单，不复制 ODB 本体。ZIP 为 3,669,457 字节，SHA-256 `db38c119fa7a1a01c698cfdc4e60327f6866057d9ba0556bc5346d49033602b8`。在仓库根执行以下命令可在 Windows 或 WSL 离线校验所有 ZIP 成员并复算。第二条用原始 WSL 冻结资产重新直读。

```bash
python3 -I -B project_docs/evidence/tcad_v5_revision_20261126/audit_r5_direct_odb_area.py --verify project_docs/evidence/tcad_v5_revision_20261126/R5_DIRECT_ODB_AREA_AUDIT.zip
bash code/scripts/run_with_timeout.sh 120 flock -w 8 /home/toylog/faeco_v5_eda.lock taskset -c 0-5 python3 -B project_docs/evidence/tcad_v5_revision_20261126/audit_r5_direct_odb_area.py --run /var/tmp/FAECO-r5-odb-new-audit
```
