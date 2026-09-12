# rseco package

FAECO 算法原型代码放在这里。

第一阶段计划模块（已完成）：

- `netlist`
- `graph`
- `equivalence`
- `cut`
- `patch`
- `ranking`
- `flow`
- `metrics`
- `failures`
- `case_loader`
- `refinement`
- `replacement`
- `abc_baseline`
- `toolchain`（外部工具命令解析：`FAECO_YOSYS/FAECO_ABC/FAECO_OPENSTA` 环境变量优先）
- `netlist_io`（Genus 风格多行 Verilog parser）
- `yosys_json`（EPFL Yosys JSON importer + wrapper，2026-07-19）
- `yosys_abc`（Yosys-normalized BLIF + ABC `cec` + ABC baseline wrapper + mapped-BLIF equivalence helper）

第二阶段 Stage B 新增（2026-07-31）：

- `technology_mapping` — Yosys `synth -noabc + abc -liberty` 流程，针对 SKY130 HD Liberty；TDD 实现 6 项测试
- `sdc` — pre-layout SDC generator；从 Liberty 读 `time_unit` / `capacitive_load_unit`；确定性 virtual-clock SDC；端口匹配检查；TDD 实现 11 项测试
- `opensta` — OpenSTA pre-layout STA runner；Windows→WSL2 路径转换（`_to_sta_path`）；Tcl 脚本生成；parser 支持 `worst slack max INF` 与 `No paths found`；TDD 实现 7 项测试

当前已有最小实现：

| 文件 | 作用 |
|---|---|
| `abc_baseline.py` | ABC rewrite/refactor/resyn baseline wrapper；无 ABC 时写回 `unavailable` |
| `case_loader.py` | 读取最小 case 的 `case.yaml` 和标准路径 |
| `netlist.py` | 解析当前 c17 风格的简单门级 Verilog，计算 gate count 和 logic level |
| `graph.py` | 抽取 fanin cone，并生成 boundary/internal/gate 信息 |
| `equivalence.py` | 最小结构等价检查，以及 ABC `cec` formal equivalence wrapper；无 ABC 时写回 `unavailable` |
| `cut.py` | fixed baseline、weighted split graph 和 Edmonds-Karp s-t min-cut 初版 |
| `patch.py` | patch candidate 表示和写回字段 |
| `replacement.py` | selected patch 的 cone-level 内部替换结果表示 |
| `flow.py` | 构造并写出最小 case metrics、target cone、candidate patch、selected patch、formal equivalence 状态和 ABC baseline 状态 |
| `metrics.py` | `change_ratio`、`logic_level_reduction` 等基础指标 |
| `failures.py` | F1-F5 失败类型枚举、阈值和失败分类 |
| `toolchain.py` | `FAECO_YOSYS/FAECO_ABC/FAECO_OPENSTA` 环境变量优先的外部工具命令解析 |
| `refinement.py` | F1-F5 反馈的确定性权重调整 |
| `netlist_io.py` | Genus 风格多行 input/output/wire 声明 Verilog parser |
| `yosys_json.py` | EPFL Yosys JSON importer + wrapper |
| `yosys_abc.py` | Yosys-normalized BLIF + ABC `cec` wrapper + ABC baseline wrapper + mapped-BLIF equivalence helper |
| `technology_mapping.py` | Yosys `synth -noabc + abc -liberty` tech mapping 流程 |
| `sdc.py` | pre-layout SDC generator + Liberty units parser |
| `opensta.py` | OpenSTA pre-layout STA runner（含 Windows→WSL2 路径转换） |

Stage B 端到端验证：`experiments/20260731_epfl_8case_stage_b/` 含 ctrl/int2float/router/cavlc/dec/priority/adder/max 共 8 个 case，mapping 8/8 success + STA 8/8 success。

仍待启动：fanout cone、Sequential Cone（N31-05）、可综合 Verilog patch 写回、X19 多轮 refinement（N31-01，需用户 design 审批）、SKY130 techmap library 修复 CEC limitation（N31-03，需用户授权 PDK 下载）。
