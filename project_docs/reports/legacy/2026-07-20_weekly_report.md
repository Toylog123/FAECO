# FAECO 周进度补充报告（2026-07-20）

## 1. 本轮目标

承接 7 月 19 日周报后的工具链缺口，关闭 X18/X21 的路线决策，把 X22 从 OpenSTA 只读就绪推进到 WSL2 本体安装、最小 STA smoke 和工具链快照可追溯，并把 X18 Yosys-BLIF-ABC formal/baseline 接入正式 runner。

## 2. 本轮完成

| ID | 任务 | 证据/产物 |
|---|---|---|
| W20-01 | 固定 X18 formal scope | 用户确认“比到门级”；记录为 Yosys 规范化后的门级 full-netlist 全部主输出对比，candidate/boundary formal 留作后续增强 |
| W20-02 | 固定 X21 权威内部格式 | 用户确认“JSON格式”；记录为 Yosys JSON importer 路径，BLIF 保留作 ABC/formal 参照 |
| W20-03 | 安装 OpenSTA 构建依赖和 CUDD | WSL2 Ubuntu 24.04.4；CUDD 3.0.0 archive SHA256 `b8e966b4562c96a03e7fbea239729587d7b395d53cadcc39a7203b49cf7eeb69`；`libcudd.a` 已生成 |
| W20-04 | 构建 OpenSTA 本体 | `https://github.com/parallaxsw/OpenSTA.git` commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56`；`/usr/local/bin/sta -version` 返回 `3.1.0` |
| W20-05 | 完成最小 STA smoke | `tmp/faeco_opensta_smoke_20260720_01/` 读入 Liberty/Verilog/SDC，输出 `0.70 slack (MET)`、`wns max 0.00`、`tns max 0.00` |
| W20-06 | 修复工具链快照对 WSL OpenSTA 的版本检测 | `scripts/check_toolchain.ps1` 保留 `-d`/`--` 参数并过滤 WSL warning；runner 版本探测 timeout 提高到 20 秒；新增回归测试 |
| W20-07 | 刷新环境快照和日志 | `experiments/environment/toolchain_2026-07-20.json` 记录 Python 3.11.9、Yosys 0.9、UC Berkeley ABC 1.01、OpenSTA 3.1.0、NetworkX 3.4.2 可用；Z3 仍不可用 |
| W20-08 | 正式接入 Yosys-BLIF-ABC formal/baseline | `src/rseco/yosys_abc.py`、`src/rseco/flow.py`、5-case batch artifacts；formal 5/5 pass、ABC baseline 5/5 success |
| W20-09 | 修复 BOM 网表导致 Yosys 空 BLIF 的兼容性 | 带 BOM 的 imported Verilog 会在 artifact 目录生成 `*.sanitized.v`，不修改原始 case 文件 |

## 3. 当前可验证结果

| 检查项 | 结果 |
|---|---|
| 单元测试 | `$env:PYTHONPATH='src'; python -m unittest discover -s tests`，57 项通过 |
| JSON 结构 | 221 个 JSON 解析错误 0 |
| OpenSTA 版本 | `wsl.exe -d Ubuntu -- /usr/local/bin/sta -version` 返回 `3.1.0` |
| OpenSTA smoke | `tmp/faeco_opensta_smoke_20260720_01/smoke.out` 含完整 max timing path、slack、WNS 和 TNS |
| PowerShell toolchain snapshot | `experiments/environment/toolchain_2026-07-20.json` 中 OpenSTA `available=true`、`version=3.1.0` |
| Yosys/ABC batch | `experiments/20260718_minimal_combinational_batch_demo/tables/case_summary.json` 中 5/5 formal `pass`、5/5 ABC baseline `success` |
| Python runner snapshot probe | `tmp/opensta_runner_snapshot_probe_20260720_01/environment/toolchain_snapshot.json` 中 OpenSTA `available=true`、`version=3.1.0` |
| 表格结构 | `task_board`、`long_term_task_plan`、`risk_register`、`work_log` 字段数和重复 ID 检查通过 |

## 4. 当前问题

| ID | 问题 | 影响 | 处理计划 |
|---|---|---|---|
| Q20-01 | Yosys JSON importer 尚未实现 | EPFL 主实验 case 还不能进入权威内部表示和 gate/level 统计 | 先为 JSON cell/port/net、escaped identifier 和 level 计算补红测，再导入 ctrl/int2float/router |
| Q20-02 | 当前 5-case 中 3 个 ISCAS 大 case license 未完备 | 已通过 formal/baseline 的结果仍只能作为本地 smoke，不能进入论文主表 | 用 X21 EPFL MIT 数据替代论文主集 |
| Q20-03 | OpenSTA Stage B runner 未接入 | OpenSTA 本体可用，但正式实验还没有 per-case WNS/TNS、critical path、STA runtime 和 report artifact | 设计 Windows-WSL path mapper、STA 输入/输出目录、report parser，并写入 runtime schema |
| Q20-04 | 多轮 refinement 未实现 | `failure_recovery` 仍是 Stage A single-refinement proxy | 实现 residual failure loop、停止原因、首次恢复轮次和 without F1/F3/F4 消融 |
| Q20-05 | A-only 首次提交证据需刷新 | 当前主工作区已从 47 项测试升级到 50 项，上一版 A-only dry-run 不能直接作为最终 staging 证据 | 确认 Git 身份、发布属性、行尾策略后重建 A-only 副本并复测 |
| Q20-06 | Z3 未安装 | 后续 candidate/boundary SAT/SMT formal 若使用 Z3 会被阻塞 | 需要时安装 `z3-solver` 并纳入快照；当前 full-netlist formal 由 ABC CEC 覆盖 |

## 5. 风险变化

| 风险 ID | 变化 | 处理 |
|---|---|---|
| R05 | Yosys/ABC formal/baseline runner 风险下降；OpenSTA Stage B runner 风险仍 active | 继续按 path mapper、report parser 和 runtime artifact 分层接入，不把 OpenSTA 本体可执行误写为 STA 实验闭环 |
| R22 | `/mnt/d/...` smoke 已证明基本读路径可用，但正式 runner 路径语义仍未验证 | Stage B 前必须测试 Liberty/Verilog/SDC/report 的 Windows-WSL 双向路径转换 |
| R17/R18 | 工具链修复新增代码和测试，A-only 首次提交审计需刷新 | 首次 staging 前重新计算 A-only 文件清单、哈希和 50 项测试结果 |

## 6. 下一批计划

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| N20-01 | 实现 Yosys JSON importer | P0 | ctrl/int2float/router 的 source blob、MIT notice、Yosys JSON、gate/level metrics 和官方 BLIF 回验产物完整 |
| N20-02 | 接入 OpenSTA Stage B | P0 | runner 自动生成 STA 输入，调用 WSL OpenSTA，解析 WNS/TNS/critical path，并写回 per-case artifact 和 runtime |
| N20-03 | 将 Yosys/ABC runner 迁移到 EPFL first wave | P0 | EPFL batch 产生 normalized artifacts、ABC logs、stats、版本、runtime 和真实状态 |
| N20-04 | 实现多轮 refinement 和消融 | P0 | recovery 从 `stage_a_proxy` 升级为真实迭代统计，输出 without F1/F3/F4 表 |
| N20-05 | 刷新首次提交 A-only 审计 | P0 | 新 A-only 副本通过 50 项测试、single demo/c17 probe、JSON 和静态卫生检查 |

## 7. 组会一句话结论

7 月 20 日已把 `yosys-abc` formal/baseline 接入正式 runner，并把 OpenSTA 从“只读推荐安装路径”推进到 WSL2 本体安装和最小 STA smoke 通过；下一步重点转为 Yosys JSON EPFL 导入、OpenSTA Stage B path bridge/report parser、多轮 refinement 和首次 Git 基线。
