# 嵌入布线导引的 pin access A/B

## 归因

SKY130HD Ibex 的 hold-aware FAECO 在第 3 次回收 22.5216 µm²。首次达标前，三个候选的 DRT/RCX、三视图 STA 和 SEC 分别花费 414.826、55.292 和 47.656 RAW s。GCD 在第 5 次回收 11.2608 µm²，对应 84.863、15.889 和 0.814 RAW s。以上为历史物理阶段的调用时间，筛选另计。 [原修复报告](HOLD_AWARE_REPAIR_REPORT.md)

两个设计每个候选的 OpenROAD 日志均记了两次 `DRT-0165/0166`，对应 Tcl 的显式 `pin_access` 和 `detailed_route` 的默认 pin access。在 Ibex 达标元组的原 `03_physical/route.log` 中，两次均处理 40,624 个实例、253 种实例模式、相同数量的 access points，粗粒度日志计时分别为 38 和 37 s。Ibex 首次达标前三次的显式阶段分别为 34、34、38 个 OpenROAD 日志秒，GCD 的前五次累计为 16 个日志秒。这个时钟与 RAW 存在口径差异，A/B 用 RAW 比较实际净收益。

OpenROAD 二进制绑定到 `b511b6a2bc936844b0319efc8b4972bb4ad7d911`。该版本 `TritonRoute.cpp:1052–1085` 在有 guides 时仍默认执行内部 pin access，随后读取 guides 和做 track assignment。`TritonRoute.cpp:1099–1131` 的显式调用也计算 pin access 并写回数据库。原来的 64 次迭代是上限，`FlexDR.cpp:2206` 在已清零 DRC 时退出。Ibex 原前三次在第 3 轮索引达到零 DRC，第 6 次在索引 5 清零。GCD 六次在索引 3 或 4 清零。故本次保持 64 上限，只检验显式 pin access 是否重复。

## 实验口径

冻结 GCD 的排名 13–15 三门合格元组和 Ibex 的排名 7–9 三门合格元组。每个设计串行运行 A→B→B→A。两臂均使用同一冻结 CONTROL、原 IO/SDC、原命名网表和原三视图 Liberty、嵌入 guides、相同 DRT 参数、RCX 规则、电气和 setup/hold 门、DRC=0 和非空全网表 SEC。A 保留显式 `pin_access`，B 在嵌入 guides 路径删去这一行，保留 DRT 默认 pin access。相对输出路径归一化后，核对 A 与 B 的完整 Tcl 差异只有这一行。需重新生成 guides 的 GRT 路径继续使用原先显式 pin access。

共同起点和共享零动作资格在各设计 A/B 之前重验。各臂独立 DRT、RCX、三视图 STA 和通过门后的 SEC，阶段及总计均用 RAW；本实验固定编辑元组，测试单次合格物理评估耗时。两设计使用 WSL CPU 6–11、OpenROAD 四线程。GCD、Ibex 整组超时分别为 720、1350 s，单次 DRT/RCX、单视图 STA 和单次 SEC 超时分别为 1500、180、210 s。预先要求接受判定、ODB、DEF、网表、DRC、去日期 SPEF、三视图、改线记录和非空 SEC 对齐，才按同端点比较时间。 [驱动](probe_duplicate_pin_access.py) · [启动器](run_pin_access_ab.sh)

| 设计 | 原元组目录 | 本轮原件目录 |
|---|---|---|
| GCD | `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_hold_aware_v1/screened/faeco/05_physical` | `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd_pin_access_ab_v2` |
| Ibex | `/home/toylog/faeco_tcad_ibex_20261123/ibex_hold_aware_v1/screened/faeco/03_physical` | `/home/toylog/faeco_tcad_ibex_20261123/ibex_pin_access_ab_v1` |

GCD 首次启动 `gcd_pin_access_ab_v1` 完成共同 CONTROL 与零动作验收后，调用适配器参数个数不符而退出，未派发 A/B 候选。更正适配器签名后使用独立目录 `gcd_pin_access_ab_v2`。

## GCD

四臂均达到 11.2608 µm² 面积减量，SEC 为 262/0。两次 A 各出现两段 pin access，两次 B 各只出现一段。四次 DRT/RCX、十二次 STA、四次 SEC 均为独立运行，物理缓存为零。

| 顺序 | A 物理评估 / RAW s | B 物理评估 / RAW s | A−B / RAW s | A−B 的 DRT/RCX 部分 / RAW s |
|---|---:|---:|---:|---:|
| A→B | 17.727 | 14.626 | 3.101 | 3.063 |
| B→A | 18.652 | 15.203 | 3.449 | 3.143 |

两次 A 与历史 ODB、DEF、网表、DRC、去日期 SPEF、三视图、改线清单和 SEC 一致。两次 B 的上述证据仅 ODB 字节不同。取第一对，两个 ODB 均为 3,494,630 字节，共 66,325 个字节位置不同。按预先设定的 ODB 字节一致门，两组均未获通过。这个结果记录单次评估的时间差，尚未确认可在生产流程采用 B。

## Ibex

四臂均达到 22.5216 µm² 面积减量，SEC 为 13648/0。两次 A 均执行两段 pin access，两次 B 均执行一段。合计四次独立 DRT/RCX、十二次 STA、四次 SEC，物理缓存为零。

| 顺序 | A 物理评估 / RAW s | B 物理评估 / RAW s | A−B / RAW s | A−B 的 DRT/RCX 部分 / RAW s |
|---|---:|---:|---:|---:|
| A→B | 186.113 | 139.387 | 46.727 | 45.797 |
| B→A | 180.633 | 158.566 | 22.067 | 33.885 |

A 完整复现原验收端点。B 的两份 ODB 字节相同，且都与 A 的 ODB 哈希不同。DEF、网表、DRC、去日期 SPEF、三视图、改线清单和 SEC 都与 A 和原端点相同。两次 B 也未通过预设的原始 ODB 字节门。两对 DRT/RCX 节省均为正，第二对中 STA 和 SEC 的额外耗时抵消了部分节省。

## ODB 差异定位

用同一 OpenROAD 读取各设计的四份 A/B ODB，枚举 AP 所属的 master pin 或 block pin、坐标和层。Tcl 将 access-type 枚举包装为进程地址，比较几何时去除了这两个句柄字段。GCD 的 2,415 个条目和 Ibex 的 7,155 个条目，在各自设计的四次运行间皆为相同的多重集。然后在内存按对象 ID 顺序删除 AP 和 OpenDB 关联引用，在新目录写独立诊断 ODB。每个设计的四个诊断 ODB 字节一致，原始 ODB 的 SHA-256 在检查前后相同。这把变化范围定位到 pin-access 对象及其引用所保存的状态。此次审查未判定各 pin 的 AP 首选顺序对于后续 ECO 等价。 [独立审查脚本](audit_pin_access_odb.tcl)

| 设计 | 原始 A ODB SHA-256 前缀 | 原始 B ODB SHA-256 前缀 | 清除 AP 后 ODB SHA-256 |
|---|---|---|---|
| GCD | `8ff54ca852ac` | `dc581fe98e54` | `8987da52d7918dc5d7d9fead3f24e734c9e7e269e63d8c26c154667474906034` |
| Ibex | `041e2b414e14` | `a6ee882efefe` | `56b575aae8f4e4b33aaeacac22bc221bff3d90e9201b12b218d91cdcc6525c29` |

GCD 首次诊断将 Tcl 的坐标二元表当成对象调用，未写诊断 ODB。修正后，两设计八个候选在各自的 `*_pin_access_odb_audit_v2` 保存完整日志、诊断 ODB 和哈希汇总。

## GCD 替代单次调用

在同一合格元组保留显式 pin access，只给 `detailed_route` 添加 `-no_pin_access`，称为 C。同一 CPU6–11 上按 A→C→C→A 重新做四次 DRT/RCX、三角 STA 和 SEC，四臂均回收 11.2608 µm²、SEC 262/0。A→C 为 15.190→12.705 RAW s，C→A 为 12.063→15.300 RAW s。两次 C 的原始 ODB 均与之前两次 B 的 ODB 字节完全一致，A 仍复现历史 ODB，DEF 等所有其他证据四次均一致。再次删除 AP 并另存的诊断 ODB 四份哈希相同。C 的首个准备命令在目录创建前因顶层未绑定到 GCD 而退出，修正后重跑四臂。原件在 `gcd_pin_access_explicit_only_ab_v1` 及 `gcd_explicit_only_pin_access_odb_audit_v1`。 [替代配方驱动](probe_gcd_explicit_pin_access_only.py)

这些结果支持把重复 pin access 作为运行时间优化目标。原始 ODB 字节门未达到，生产配方保持原默认。当前范围是两个已合格端点的独立单次评估，尚未测完整搜索或从 B/C 的 ODB 继续做下一次 ECO。

完整原件保存在 `scratch/tcad_ibex_20261123/pin_access_ab_20261124.tar.gz`，含八个运行和诊断目录及四个脚本。SHA-256 `c7a043ee854c5ad862be8dd63f5afd63aff7f6f03bbb362fe09758558bb41d18`，156,613,093 字节，494 个成员，438 个文件按成员与原始 SHA-256 逐个核对。
