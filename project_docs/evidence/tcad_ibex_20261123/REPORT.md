# Ibex 的跨工艺详细布线与同预算面积回收

## 执行口径

两套 Ibex 分别从 ORFS `base` 配置构建至 `6_report`。原始顶层为 `ibex_core`，实际时钟 `core_clock` 绑定 `clk_i`，I/O 由虚拟时钟 `vclk_core_clock` 约束。资格检查比对原始 SDC 与最终导出的每个数据输入和输出。核心时钟使用 CTS 实际传播延时，虚拟时钟保留原始延迟。三视图分别读取对应 Liberty 与同一份 DRT 后提取的 SPEF。

| 工艺 | 周期 | 输入与输出延时 | 虚拟时钟延迟 | 生产器的 PVT |
|---|---:|---:|---:|---|
| SKY130HD | 10,000 ps | 2,000 ps | 1,095 ps | TT |
| ASAP7 | 1,000 ps | 200 ps | 161.775 ps | FF |

固定 ORFS `da8f092a02a8e75658cc3100691aabff05f35629`、该工作区的 OpenROAD Bazel 二进制、Yosys `72b0054f0`、独立 OpenSTA 3.1.0。工具与原件的路径、SHA-256 记录在各资格回执。重型产物保留于 WSL `/home/toylog/faeco_tcad_ibex_20261123/`。实验账本见 [登记册](../EXPERIMENT_REGISTRY.md)。

## 起点资格与同预算对照

| 工艺 | 详细布线 DRC | RCX | 原始 SDC 覆盖 | FF setup / hold（ps） | TT setup / hold（ps） | SS setup / hold（ps） |
|---|---:|---|---|---:|---:|---:|
| ASAP7 | 0 | 20,323 网 | 157 输入，106 输出 | +0.380362 / +35.955849 | −382.748166 / +53.158783 | −1085.186052 / +77.237466 |
| SKY130HD | 0 | 15,242 网 | 157 输入，106 输出 | +1171.698294 / +288.150503 | −456.739535 / +466.105821 | −38754.158993 / −1379.766079 |

ASAP7 通过起点资格。源 I/O 延时及虚拟时钟延迟与导出 SDC 一致，三个视图共享最终版物理寄生。独立 OpenSTA 回读绑定导出的 Verilog、SDC 与 SPEF。补充的 FF setup 诊断分别给出 OpenROAD ODB 回读 +0.772160 ps、同一 OpenROAD Verilog 回读 +0.677236 ps、独立 OpenSTA Verilog 回读 +0.380362 ps，三者 FF hold 一致。策略对照固定独立 OpenSTA 回读。[ASAP7 资格回执](asap7_control/CONTROL.json)

ASAP7 五件端点、布线导引和生产日志另存于工作区的 `scratch/tcad_ibex_20261123/asap7_control.tar.gz`，已复核归档目录和 SHA-256 `7d97ab8f3d6127e267d6c242dd0643dbae966743263559706d578bd16407786d`。

SKY130HD 原始终点三次 DRT 均收敛至零，最后一次含天线修复，最终天线报告为空。首个 Verilog/SPEF 检查发现 ORFS 的功能网表过滤了物理天线二极管，无法读回这些二极管关联的 SPEF 节点。以生产器版本 OpenROAD 读取同一最终 ODB、SDC、SPEF 后，TT 与原生报告一致。SS 仍存在 hold 违例，原始终点未取得对照资格。正在原 I/O 约束下尝试共同 hold 修复。[SKY130 原始资格回执](sky130_control/CONTROL.json)

SKY130HD 原始五件端点、布线导引、生产日志及两种 STA 读法原件另存于 `scratch/tcad_ibex_20261123/sky130_control_original.tar.gz`。SHA-256 为 `a345751e20c7e0a19b35e401ab39fac905589168a298dd8dd736a8bdb8b1f8f8`。

面积回收的实验门为 TT、FF、SS 各视图不超过 10 ps 的 setup WNS 相对损失，hold 非负且保持起点裕量（0.001 ps 数值容差），电气违例不新增，DRC 为零，功能网表等价。每臂 6 次物理评估，对比在线单门、固定三门及自适应三门批次。各次重用同工艺的原始布线导引，清理被换门相邻网线，记录详细路由自身对相邻线网的改动。分别登记等候选评估次数和等实测墙钟前缀。候选前的零动作重放单独计费。

ASAP7 的共享零动作复测已通过，DRC 为零，SEC 为 17,363/0（已证/未证），三视图的最大 setup WNS 损失为 0.541789 ps，hold WNS 变化绝对值小于 0.001 ps。十条网的几何发生变化，组件位置未变。候选池有 4,151 个实例，功能单元的 TT Liberty 面积和为 2129.78808。三臂执行中。[执行命令](ASAP7_P1_COMMAND.txt)

## SEC 工具预检

Yosys 使用 TT Liberty 导入单元功能模型，并以 `hierarchy -simcheck` 拒绝使用未定义和黑盒模块。SKY130 工艺的 Liberty 触发器含异步复位，初始直接 SAT 导入报告缺少相关 FF 模型。采用 `clk2fflogic` 将事件显式化，按工具的两态时序模型和异步复位撤销与时钟同刻时的负 hold 约定检查。SKY130 和 ASAP7 的合成阶段网表自比分别为 13,517/0 与 17,235/0（已证/未证）。正式对照的等价证明绑定实际布线网表。
