# SKY130HD Ibex 公共 hold 修复

原 ORFS 物理起点在 SS 视图存在 hold 违例。各轮沿用原始导出 SDC 和同一固定版 OpenROAD。两个初探读取各自源端点的 ODB 和 SPEF，在 TT、FF、SS 三视图运行 hold 修复，使用 10% 缓冲器上限并允许既有 setup 违例。表中的时序和面积均为重布线前估计。原端点身份见 [原始 CONTROL](../CONTROL.json)。

| 初探 | 只读起点 | hold 余量 | 新增缓冲器 | 最差 hold（ps） | 最差 setup（ps） | 工具报告面积（µm²） |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [第一次](hold_repair_sky130_dry_root/dry.tcl) | 原始布线端点 | 0.05 ns | 14 | −1379.766 → +51.001 | −38754.159 → −38754.159 | 148771 → 148912 |
| [第二次](hold_repair_sky130_dry_root_02/dry.tcl) | `_02` 布线端点 | 0.10 ns | 10 | −3.293 → +115.011 | −38757.570 → −38757.570 | 148912 → 149012 |

两个初探均以 4 线程、300 s 外层限时完成，返回码为 0。实际命令、输入及产物哈希和原始日志路径见 [PROVENANCE.json](PROVENANCE.json)。

| 续跑 | 输入及处理 | 路由进程耗时 | 物理结果 |
| --- | --- | ---: | --- |
| [_01](hold_repair_sky130_01/RECEIPT.json) | 第一次初探 ODB，保留原有 filler 进行合法化 | 0.629 s | 占用率 100.1%，合法化报 `DPL-0038`，返回码 1。原 ODB 盘点完成，DRT 和 RCX 均未启动。 |
| [_02](hold_repair_sky130_02/RECEIPT.json) | 同一初探 ODB 和 `_01` 的原 ODB 盘点。合法化前移除 21,961 个 filler，DRT 后按原 master 复填。 | 164.128 s | 返回码 0，DRT 违规数 448→173→121→6→0，RCX 提取 15,256 网，天线仍有 1 项。 |
| [_03](hold_repair_sky130_03/RECEIPT.json) | 第二次初探 ODB，以 `_02` 端点重新盘点。复用先拆后填的流程，初次 DRT 后执行一次原生 diode-only 修复及再次 DRT。 | 235.650 s | 返回码 0，初次 DRT 违规数 157→104→88→0。两颗二极管插入后，DRT 违规数 66→75→129→5→0，天线 0，RCX 提取 15,266 网。 |

两轮物理续跑按实例位置和网连接差分确定受影响信号网。`_02` 有 53 条受影响网，其中清除 25 条既有详细连线。`_03` 有 71 条，其中清除 51 条。`_02` 残余天线位于 `data_rvalid_i` 到 `hold3717/A`，met2 侧面积比 663.06，限值 400.00。`_03` 初次 DRT 后，该引脚和 `net204` 上的 `output198/A` 均触发天线违规。最终 `drc.rpt` 和 `antenna.rpt` 均为空。

`_02` 和 `_03` 各自导出 ODB、功能 Verilog、DEF、SPEF、路由导引及 SDC，SDC SHA256 均为 `4e178c0c3469e33a244e3829b75ba473d1bae71dfd7c3765acb8847d63c508f5`。`_03` 最终 ODB SHA256 为 `e26a97a265ef251feeb4a4b3c981f464117f856d5366bdeaa66c8c2e209dc9ac`，SPEF SHA256 为 `646acf3eeea8ba1647196eade5e633d95d643e4cef62983bb693cbdd6f8fd02f`。原约束三视图 STA 和形式等价资格见独立资格记录。

各续跑目录的 `COMMANDS.txt`、`CONFIG.json`、`RECEIPT.json` 和 Tcl 为逐字节副本。Tcl 内保留执行时的绝对路径。完整路线日志、盘点及大端点仍在 WSL 的 `/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_*/`，两个初探日志位于 `scratch/tcad_ibex_20261123/`。可从 [PROVENANCE.json](PROVENANCE.json) 和各续跑收据校验原件。
