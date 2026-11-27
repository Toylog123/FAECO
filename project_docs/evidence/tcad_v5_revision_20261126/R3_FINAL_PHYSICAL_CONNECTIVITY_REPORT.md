# 40 ns 处理器最终版图的布局与供电连通核验

对 SEC 修复后隔离复跑的合格参考和单门、固定三门、FAECO 三个最终检查点，使用原物理评估的 OpenROAD 重新读取最终 ODB。四份 ODB 均通过详细布局合法性、非特殊多端网布线存在性以及 VDD、VSS 电源网连通检查。三个候选的全部实例仍位于原位置，受保护线网的几何无变化，DEF 的 `PINS` 与 `SPECIALNETS` 段和参考相同。

## 冻结对象和实跑

物理工具取自隔离复跑的 seed 绑定，并与三条候选的原路由命令和台账交叉核对。实际程序为 `/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped`，118,444,744 字节，SHA-256 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`，原路由日志标识为 `OpenROAD bazel-nostamp`。Tcl 不启动布局、布线或 PDN 生成，也不写回 ODB。每份 ODB 运行前后复核 ODB 和 DEF 哈希。

```tcl
read_db $endpoint_odb
design_is_routed -verbose
check_placement -verbose -report_file_name $placement_report
check_power_grid -net VDD -error_file $vdd_errors
check_power_grid -net VSS -error_file $vss_errors
```

实际 Tcl 对所有命令记录逐项状态，两个供电检查均要求布尔通过。按参考、单门、固定三门、FAECO 顺序串行运行，使用共享 EDA 锁、CPU 0–5、一线程 OpenROAD、每个 ODB 120 s 与外层 610 s。外层约 5 s 返回 0。各文件的原始日志分别记录 VDD、VSS 的 `PSM-0040` 连通消息。通过时同次运行未产生放置错误文件或电源网错误文件，验收依据为退出状态、逐项通过记录和工具日志。

| 对象 | 最终请求／门数 | ODB SHA-256 前缀 | 布线存在性／布局 | VDD／VSS | 核验实耗（s） |
| --- | --- | --- | --- | --- | ---: |
| 冻结控制点 | 零改动 | `8703269738b5` | 通过／通过 | 通过／通过 | 0.862 |
| 单门 | 07／5 | `8b166fa9c70d` | 通过／通过 | 通过／通过 | 0.859 |
| 固定三门 | 06／12 | `e2b5f622ad24` | 通过／通过 | 通过／通过 | 0.854 |
| FAECO | 03／4 | `7ff73d0f3e89` | 通过／通过 | 通过／通过 | 0.846 |

## 几何与连接证据的范围

离线从四份完整 DEF 独立重算。三个候选的单元主单元差分只含各自冻结动作，无新增、删除或迁移实例。单门、固定三门、FAECO 的受保护网数为 5,469、5,435、5,474，三个保护集合中的几何改动均为零。三臂分别只有允许范围内的 27、60、22 条网的几何发生变化。比较普通 `NETS` 时对无序连接端子元组排序，线路内容只归一 `FIXED` 与 `ROUTED` 锁定标记。`PINS` 和 `SPECIALNETS` 分别字节一致，段摘要为 `2d23f9036674f4462d052144c0e6fcf01611ef11ea2440e89e97214e836f5ae6` 和 `7a129bbf39e40c50aa25f855ed4b2780710c47f08406714ae26d1f33bc1af483`。

原候选 Tcl 已在详细路由后执行 `design_is_routed` 与 `check_placement -verbose`，并继续完成零天线、独立全块 DRC 和 SEC 4559/0。OpenROAD 的 `design_is_routed` 检查非特殊多端网是否存在导线、过孔或合法贴靠。详细路由内部另对修改过的网构造线段及端点图并执行连通检查，在失败时报告 `DRT-0206`。路由内部检查在路由过程中运行。本次读回检查验证了布线存在性、布局和两条电源网的物理连通。未进行独立的全信号逐端点版图连接抽取或物理 LVS。全块 DRC、天线与逻辑 SEC 分别保留其原验收范围。 [布线存在性源码](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/odb/src/db/dbBlock.cpp#L3326-L3351) · [详细路由连通检查入口](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/dr/FlexDR.cpp#L1574-L1577) · [修改网的连通检查](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/dr/FlexDR_conn.cpp#L1180-L1203) · [PSM 检查选项](https://github.com/taizun-jj202/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/psm/src/pdnsim.tcl#L4-L34)

## 原件和复算

[原件包](R3_FINAL_PHYSICAL_CONNECTIVITY_ORIGINALS.zip)含四份原始 ODB 和 DEF、运行 Tcl、原始工具日志及状态、原路由脚本与收据、全块 DRC 和 SEC 收据等 51 份成员，另有成员清单。ZIP 为 16,002,118 字节，SHA-256 `5757774b162441017ff8514c89ed4e7f4df8a6a9f04627e5a929079737b2915c`。Windows 原生 Python 和 WSL 均完成离线复算，结果逐字段一致。

```bash
python3 -I -B project_docs/evidence/tcad_v5_revision_20261126/verify_r3_final_physical_connectivity.py
```
