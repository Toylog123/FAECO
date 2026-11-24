# ASAP7 UART 原约束起点资格规约

2026-11-24 · 独立设计起点 · [运行入口](prepare_uart_control.sh)

## 输入预检

选用本机 ORFS 的 `designs/asap7/uart`，顶层 `uart`，原生 `base` 变体，`DATA_WIDTH=8`。原生配置为 `CORNER=TC`、Slang 综合、布局密度 0.70。源 SDC 的核心及虚拟时钟周期均为 270 ps，虚拟时钟延迟 66.270 ps，非时钟输入与输出延迟均为 54 ps。RTL 给出 28 个非时钟输入与 15 个输出。实际 ORFS、OpenROAD、Yosys、独立 OpenSTA 及 15 个 FF/TT/SS RVT Liberty 的输入预检通过。

从项目根目录在 WSL 执行，安排在同机 AES 墙钟比较结束后。

```bash
bash project_docs/evidence/tcad_holdout_20261123/prepare_uart_control.sh --check-inputs
bash code/scripts/run_with_timeout.sh 2300 bash project_docs/evidence/tcad_holdout_20261123/prepare_uart_control.sh
```

原始工作目录为 `/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/asap7/uart`。原生制备固定四线程、CPU 0–5、1,800 秒上限。目录已存在时须使用新路径。只复查已成功制备的物理端点时，可以用 `--qualify-only qualification_v2` 新建独立复核目录。

## 资格与计数

原始生产记录为 `producer_receipt.json` 和 `producer.log`。资格阶段要求实际完成详细布线与寄生提取，五份冻结端点产物齐全，原生 DRC 和天线计数为零。三套 RVT Liberty 共用最终 SPEF，沿用独立 OpenSTA 的网表口径，逐角核对原虚拟时钟、传播核心时钟和 28/15 个真实 I/O，保存 setup/hold WNS/TNS 和最差路径。

输出 `qualification/CONTROL.json` 记录 FF／TT／SS 最小裕量与资格状态。三角 hold 均非负时为 `hold_qualified`，任一视图为负时为 `hold_infeasible`。零动作候选链与候选 SEC 使用后续实验的单独收据。在这一步，候选评估次数为零。

## 资格实测

原生 UART 完成详细布线和实际寄生提取。原 270 ps 周期、54 ps I/O 及虚拟时钟延迟经导出 SDC 和实际 STA 读回一致。原生与独立 DRC、天线均为零。以同一冻结 ODB/DEF/网表/SDC/SPEF 复核 FF、TT、SS，原始和独立的四项时序指标逐值一致。

| 视图 | Setup WNS (ps) | Setup TNS (ps) | Hold WNS (ps) | Hold TNS (ps) | 原有负 setup 端点 |
|---|---:|---:|---:|---:|---:|
| FF | +25.852903 | 0 | +50.314898 | 0 | 0 |
| TT | −39.580256 | −1893.102120 | +67.502115 | 0 | 77 |
| SS | −199.705308 | −13697.365020 | +54.052915 | 0 | 78 |

逐角 max slew 与 max capacitance 均无违例。冻结后布线网表的非空两态自证为 567 已证明、0 未证明。UART 可进入后续原约束对照的起点队列；后续候选须各自验证时序和等价性。此轮候选布线、候选 STA、候选 SEC 计数均为 0。 [原生资格](UART_CONTROL.json) · [独立复核](UART_CONTROL_VERIFIED.json)

本地归档 `scratch/tcad_ibex_20261123/uart_control_20261124.tar.gz` 包含完整原生流程、物理端点、原始报告、补充核验与实际执行的脚本。归档 121 个文件逐文件验证，13,673,108 字节，SHA-256 `03ed8fc2b3525df0e312a489fc86563cdb8334e4306486fc4592079521dbb4b6`。补充核验用归档中的 `auditor_sources/check_uart_control.py` 从项目根的 `scratch/tcad_ibex_20261123/` 运行，参数为原始工作目录和 `--sec --output supplemental_v2`。独立复核收据 SHA-256 `6b8c1eb744d3357479b6091199cc593ab6f18bedc796186eef9bf736c9e123aa`。
