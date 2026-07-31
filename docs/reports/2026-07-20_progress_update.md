# 2026-07-20 进度更新

当前阶段：Phase 4 继续推进。今天关闭 X18/X21 的路线决策，把 X22 从只读就绪推进到 WSL2 OpenSTA 本体安装和最小 STA smoke 通过，并完成 X18 Yosys-BLIF-ABC formal/baseline 正式 runner 接入。

## 1. 今日完成

| ID | 任务 | 产物 |
|---|---|---|
| D01 | 批准 X18 formal scope | `decision_log.md`、`task_board.md`、`long_term_task_plan.md`、`toolchain_setup.md` |
| D02 | 批准 X21 权威内部格式 | `decision_log.md`、`benchmark_selection.md`、`benchmark_source_and_license_audit.md`、`experiments/README.md` |
| D03 | 复测 WSL2/OpenSTA 状态 | `toolchain_setup.md`、`risk_register.md`、`task_board.md` |
| D04 | 同步下一批执行顺序 | `future_task_backlog.md`、`revision_roadmap.md`、`README.md` |
| D05 | 刷新 A-only 首次基线副本 | `tmp/initial_commit_a_only_dry_run_20260720_01/`、`initial_commit_scope_audit.md` |
| D06 | 在 WSL2 安装并验证 OpenSTA 本体 | `/opt/faeco/OpenSTA-parallaxsw-dc5ccd2/`、`tmp/faeco_opensta_smoke_20260720_01/`、`experiments/environment/toolchain_2026-07-20.json` |
| D07 | 修复带参数工具命令的版本检测 | `scripts/check_toolchain.ps1`、`scripts/run_minimal_combinational_demo.py`、`tests/test_toolchain_script.py`、`tests/test_demo_runner.py` |
| D08 | 正式接入 Yosys-BLIF-ABC formal/baseline | `src/rseco/yosys_abc.py`、`src/rseco/flow.py`、`tests/test_yosys_abc_flow.py`、5-case batch artifacts |
| D09 | 修复 UTF-8 BOM 网表规范化输入 | `original.sanitized.v`/`revised.sanitized.v` artifact、BOM 回归测试 |

## 2. 新决策

| 决策 | 当前口径 | 影响 |
|---|---|---|
| X18 formal scope | 采用 Yosys 规范化后的门级 full-netlist 全部主输出对比 | 正式 runner 需记录 normalized artifacts、ABC `cec` scope、命令、版本、日志和 runtime；candidate/boundary-level formal 暂不作为首轮完成标准 |
| X21 canonical format | 采用 Yosys JSON 作为 FAECO 权威内部格式 | EPFL 第一波导入转为实现 Yosys JSON importer、gate/level 统计、escaped identifier 映射、case metadata 和官方 BLIF 回验证据 |

## 3. WSL2/OpenSTA 实测与安装

| 检查项 | 结果 |
|---|---|
| WSL2 distro | `Ubuntu 24.04.4 LTS`，`x86_64`，可启动 |
| 安装前状态 | `which sta/opensta`、常见路径和 root filesystem 搜索均未找到 OpenSTA 可执行文件 |
| 已安装依赖 | `cmake`、GCC/G++、Git、Tcl/Tcl readline、SWIG、Bison、Flex、automake/autotools、Eigen、fmt、zlib |
| CUDD | `/opt/faeco/cudd-3.0.0/cudd/.libs/libcudd.a` 存在；archive SHA256 `b8e966b4562c96a03e7fbea239729587d7b395d53cadcc39a7203b49cf7eeb69` |
| OpenSTA source | `https://github.com/parallaxsw/OpenSTA.git`，commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56` |
| OpenSTA binary | `/opt/faeco/OpenSTA-parallaxsw-dc5ccd2/build/sta`，`/usr/local/bin/sta` 已链接到该二进制 |
| 版本验证 | `/usr/local/bin/sta -version` 返回 `3.1.0` |
| 最小 smoke | `tmp/faeco_opensta_smoke_20260720_01/smoke.tcl` 读入 Liberty/Verilog/SDC，输出 max timing path、`0.70 slack (MET)`、`wns max 0.00`、`tns max 0.00` |
| 工具链快照 | `experiments/environment/toolchain_2026-07-20.json` 记录 OpenSTA `available=true`、命令 `wsl.exe -d Ubuntu -- /usr/local/bin/sta`、版本 `3.1.0` |

结论：OpenSTA 本体已经在 WSL2 安装并完成最小 STA smoke；但正式 Stage B runner 还未实现 Windows-WSL 路径桥、STA 输入生成、report 解析和 per-case artifact 写回，因此当前正式 5-case batch 仍不能报告真实 WNS/TNS 或 STA critical path。

## 4. 现在还剩的问题

| ID | 问题 | 影响 | 下一步 |
|---|---|---|---|
| Q01 | EPFL Yosys JSON importer 尚未实现 | 当前 5-case formal/ABC 已是 local smoke，论文主表仍不能使用 license 未完备的 c432/c499/c880 | 按 TDD 导入 ctrl/int2float/router，保留 MIT notice、Yosys JSON、官方 BLIF 回验和 batch 配置 |
| Q02 | Stage B OpenSTA runner 未接入 | OpenSTA 本体可用，但正式实验还不能自动产生 WNS/TNS、critical path 和 timing closure artifact | 按 TDD 设计 Windows-WSL path mapper、STA input/report 目录、report parser 和 runtime 写回 |
| Q03 | Windows-WSL 路径桥未设计 | runner 即使能调用 WSL `sta`，也可能找不到 Liberty/Verilog/SDC/report 路径 | 设计 path mapper，并用临时文件/报告路径做最小测试 |
| Q04 | 多轮 refinement 未实现 | `failure_recovery` 仍是 `stage_a_proxy` | 明确 Stage A 成功口径后实现 residual failure loop 和 ablation |
| Q05 | Git 首次基线未提交 | 缺少可回退工程历史 | 确认 A-only 范围、Git 身份、发布属性和行尾策略后精确 staging |
| Q06 | Z3 未安装 | 若后续 candidate/boundary SAT/SMT formal 使用 Z3，目前环境不可运行 | 需要时安装 `z3-solver` 并补快照/测试；full-netlist formal 当前由 ABC CEC 覆盖 |

## 5. 验证记录

| 命令/检查 | 结果 |
|---|---|
| WSL readiness probe | 安装前 Ubuntu 24.04.4 可启动，但 `sta/opensta` 缺失；安装后 `/usr/local/bin/sta -version` 返回 `3.1.0` |
| OpenSTA smoke | `tmp/faeco_opensta_smoke_20260720_01/smoke.out` 包含完整 timing path、`0.70 slack (MET)`、`wns max 0.00`、`tns max 0.00` |
| Yosys/ABC 5-case batch | `experiments/20260718_minimal_combinational_batch_demo/tables/case_summary.json` 显示 5/5 `formal_equivalence_result=pass`、5/5 `abc_baseline_status=success`；raw results 下归档 normalized BLIF、ABC logs、optimized BLIF、stats 和 runtime |
| 工具链快照 | `experiments/environment/toolchain_2026-07-20.json` 显示 Python 3.11.9、Yosys 0.9、UC Berkeley ABC 1.01、OpenSTA 3.1.0、NetworkX 3.4.2 可用；Z3 不可用 |
| 文档状态同步 | X18 从 in_progress 更新为 done；X21 保持 Yosys JSON importer 待实现；X22 保持 OpenSTA 本体已安装、Stage B runner 待接入 |
| A-only 隔离副本 | `tmp/initial_commit_a_only_dry_run_20260720_01/` 是 OpenSTA/工具链修复前的上一版 dry-run：136 个核心文件，missing=0、mismatch=0，路径 SHA256 `051CB158...65227`；47 项测试、single demo 和 c17-only batch 通过；当前主工作区已升级为 50 项测试，首次提交前需刷新 |
| 单元测试 | `$env:PYTHONPATH='src'; python -m unittest discover -s tests`，57 项通过 |
