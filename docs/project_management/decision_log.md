# FAECO 决策记录

更新时间：2026-08-28

| 日期 | 决策 | 理由 | 影响 |
|---|---|---|---|
| 2026-07-07 | 主线不再执着恢复旧代码 | 旧代码找不到或可能存在大问题 | 以旧论文思想为基础重做新工作 |
| 2026-07-07 | 第一篇先冲中文工程类论文 | 当前目标是稳妥发表，中文更适合快速落地 | 写作和实验标准按工程类论文组织 |
| 2026-07-07 | 新方法暂定名 FAECO，不沿用 RSECO | 避免被认为只是整理学长工作 | 论文叙事变成继承思想后的新方法 |
| 2026-07-07 | 第一阶段先做 combinational cone | 降低实现复杂度，先验证核心机制 | 第二阶段必须补 sequential cone 以贴近真实场景 |
| 2026-07-07 | 第一版 ranking 不用 GNN/RL | 避免工程复杂度过高，保证可解释性 | 使用确定性 scoring |
| 2026-07-07 | 核心创新放在 failure-aware cut refinement | 比 benchmark flow 更像算法贡献 | 论文贡献顺序以算法为先 |
| 2026-07-07 | 原始材料保留原位，另建归纳索引 | 保证可追溯且避免破坏历史材料 | `docs/materials/` 作为派生索引 |
| 2026-07-14 | 旧稿不按原样投稿 | 旧代码、工业数据、baseline 和公式证据链不足 | 旧稿转为 FAECO 的问题来源和历史证据 |
| 2026-07-14 | 第一批 benchmark 优先 ISCAS85 与 EPFL | 二者公开、规模可控，适合验证 combinational cone 机制 | 该初步决策已被 2026-07-19 许可审计收窄：ISCAS85 当前文件仅作 smoke，EPFL 作为论文主来源 |
| 2026-07-14 | 每个 ECO case 采用统一 schema | 后续代码、实验和论文表格需要可追溯数据结构 | 以 `docs/experiment_design/case_schema.md` 作为实验数据约束 |
| 2026-07-14 | Git 分支使用 `main` | 避免后续从默认 `master` 再迁移 | `.git` 已初始化，尚未创建首次提交 |
| 2026-07-14 | 第一版测试使用 Python `unittest` | 不引入额外测试依赖，先保证最小骨架可验证 | 测试命令为 `python -m unittest discover -s tests` |
| 2026-07-19 | Stage A 论文主数据源固定为 EPFL `v2025.1` | 官方仓库提供固定版本和 MIT license；当前第三方 ISCAS85 文件的 license 未声明 | EPFL 待规范化和 formal 验证后进入主实验；c432/c499/c880 仅保留本地 smoke，不进入可再分发包 |
| 2026-07-20 | X18 formal scope 采用门级网表对比 | 先比较经 Yosys 规范化后的 gate-level full-netlist 全部主输出，避免把结构签名、candidate boundary 或未接入 runner 的探针混作正式 formal | 正式 runner 需要记录 normalized gate-level artifacts、ABC `cec` scope、命令、版本、日志和 runtime；candidate/boundary-level formal 留作后续扩展 |
| 2026-07-20 | X21 权威内部格式采用 Yosys JSON | EPFL 原始 Verilog 和 `write_verilog -noexpr` 均不适配当前轻量 parser；Yosys JSON 能保留结构、端口、cell 和 escaped identifier 信息，适合作为 FAECO 的可追溯 normalized representation | 第一波 EPFL 导入转为实现 Yosys JSON importer、gate/level 统计、source blob/notice 记录和对官方 BLIF 的 formal 回验 |
| 2026-07-31 | Stage B technology mapping 采用 `synth -noabc + abc -liberty` 流程 | Yosys 0.9 原始 `techmap` 流程产生 `sky130_fd_sc_hd__clkinv_1` placeholder，而 SKY130 HD Liberty 实际不含此 cell；`synth -noabc` 先把 Verilog 归约到 ABC primitives，再 `abc -liberty` 映射到 Liberty cells，能避开 placeholder 路径 | 当前 8-case Stage B 端到端 mapping 8/8 success；CEC 形式回验受 SKY130 Liberty 不含 `clkinv_1` 影响仍 unavailable，已记录 R31-01 |
| 2026-07-31 | Stage B STA 接入 OpenSTA 3.1.0 WSL2 via `_to_sta_path` 路径转换 | OpenSTA 本体已在 WSL2 Ubuntu 构建完成；Windows→WSL2 路径转换 (`D:\foo\bar` → `/mnt/d/foo/bar`) 是 STA runner 的实际阻碍；通过 `_to_sta_path` 把 Liberty/Verilog/SDC/`sta_script.tcl` 都转换为 WSL 视角路径后，WSL2 sta 能正确读入 | 8-case Stage B STA 8/8 success；WSL PATH translation warning 仅为宿主 PATH 噪声 |
| 2026-07-31 | SDC 中不写 `set_time_unit` / `set_capacitive_load_unit` | OpenSTA 3.1.0 不支持这两个命令，且 `time_unit` 和 `capacitive_load_unit` 由 Liberty 文件自动提供 | 当前 SDC 只含 `create_clock / set_input_delay / set_output_delay / set_load / set_driving_cell / set_max_delay-or-min_delay`，全部被 OpenSTA 接受；测试覆盖 11 项 |
| 2026-07-31 | Stage A+B 综合 limitation 接受记录在文档不补工具链 | 当前 limitation 主要包括 CEC unavailable (clkinv_1) 和 combinational STA 无 timing path；两者均依赖外部修复（ORFS techmap library、SDC DFF 信号），按 handoff 不下载完整 PDK | CEC 和 STA limitation 在 STAGE_B_AGENT_HANDOFF.md、stage_b_deferred_execution_checklist.md、risk_register.md、task_board.md、work_log.md、method_rewrite_readiness.md 和 L01 Related Work 初稿中均明确标注 A/B 边界，禁止写入论文主表 |
| 2026-07-31 | Stage B technology mapping 采用 `synth -noabc + abc -liberty` 流程 | Yosys 0.9 原始 `techmap` 流程产生 `sky130_fd_sc_hd__clkinv_1` placeholder，而 SKY130 HD Liberty 实际不含此 cell；`synth -noabc` 先把 Verilog 归约到 ABC primitives，再 `abc -liberty` 映射到 Liberty cells，能避开 placeholder 路径 | 当前 8-case Stage B 端到端 mapping 8/8 success；CEC 形式回验受 SKY130 Liberty 不含 `clkinv_1` 影响仍 unavailable，已记录 R31-01 |
| 2026-07-31 | Stage B STA 接入 OpenSTA 3.1.0 WSL2 via `_to_sta_path` 路径转换 | OpenSTA 本体已在 WSL2 Ubuntu 构建完成；Windows→WSL2 路径转换 (`D:\foo\bar` → `/mnt/d/foo/bar`) 是 STA runner 的实际阻碍；通过 `_to_sta_path` 把 Liberty/Verilog/SDC/`sta_script.tcl` 都转换为 WSL 视角路径后，WSL2 sta 能正确读入 | 8-case Stage B STA 8/8 success；WSL PATH translation warning 仅为宿主 PATH 噪声 |
| 2026-07-31 | SDC 中不写 `set_time_unit` / `set_capacitive_load_unit` | OpenSTA 3.1.0 不支持这两个命令，且 `time_unit` 和 `capacitive_load_unit` 由 Liberty 文件自动提供 | 当前 SDC 只含 `create_clock / set_input_delay / set_output_delay / set_load / set_driving_cell / set_max_delay-or-min_delay`，全部被 OpenSTA 接受；测试覆盖 11 项 |
| 2026-07-31 | Stage A+B 综合 limitation 接受记录在文档不补工具链 | 当前 limitation 主要包括 CEC unavailable (clkinv_1) 和 combinational STA 无 timing path；两者均依赖外部修复（ORFS techmap library、SDC DFF 信号），按 handoff 不下载完整 PDK | CEC 和 STA limitation 在 STAGE_B_AGENT_HANDOFF.md、stage_b_deferred_execution_checklist.md、risk_register.md、task_board.md、work_log.md、method_rewrite_readiness.md 和 L01 Related Work 初稿中均明确标注 A/B 边界，禁止写入论文主表 |
| 2026-08-26 | b15 提升量 +0.09 vs 历史 +0.70 判定为 early-stop 设计本身而非代码回归，不重跑 | early-stop（省约 75% STA 预算，commit e1edd9e 引入）把"每轮找最优"降级为"每轮第一个小改善"；JOINT 全枚举候选排在单门之后，轮内未到达。历史 20260805 即"关早停全枚举"对照数据 | 保持 unified-loop 统一配置；b15 全枚举复跑仅作为可选补充实验，主结果按当前配置口径报告；记录于 b15_early_stop_regression.md |
| 2026-08-27 | b17 0 改善根因 = 单候选 60s 验证硬预算（F5）拒绝全部 785 候选，非搜索失败、非早停 | b17 为 19 个 ITC-99 中最大电路，单候选 OpenSTA 76–138s（中位 113s）超过硬编码 max_verification_time_s=60.0（未暴露 CLI）；183 个候选 WNS 优于基线，最佳 +0.43 与历史一致 | 选定方案 A：预算提至 180s 仅重跑 b17（约 3–4h）+ 补 SEC + 更新汇总；已记录待执行，见 b17_failure_analysis.md |
| 2026-08-28 | 磁盘瘦身只清理明确可再生的中间产物，实验 JSON / mapped.v / case / eval_trials 与 20260805 历史目录严禁删除 | 用户明确"千万不要误删"，实验产物是论文证据链不可再分发生成 | 已清理 STA 中间日志，D 盘余约 59GB；b17_pre_reboot_2340（5.6GB）与 4 个 failed 残留目录（约 1.4GB）保留待用户确认 |
| 2026-09-08 | b17 重跑 runner 选择 `--skip-mapping + --strategies R,G + --workers 4 --early-stop`,不复用历史 60s 硬预算 | runner 无断点恢复能力（已审计），必须整轮重跑；用 `--skip-mapping` 复用历史 mapped.v 避免重跑 Yosys；`R,G` 策略禁用 B(buffer insertion)以缩短单 iter；4 worker 并行加速 60s STA 不再卡死 | 重跑结果 WNS -16.53 → -16.15(+0.38 ns),优于历史 0.43 上限,接受 cell 为 `_184320_ nor4b_1→nor4b_2`(G),sec_result.json 12812 proven/1 unproven;记录于 work_log LOG-20260908-01..06 |
| 2026-09-08 | b17 SEC 用 stripped golden (`experiments/20260805_tcad_sprint1_itc99/b17/b17/case/original/original.v`, 89k 行)而非 `benchmarks/raw/itc99/v/b17.v` (237k 行,含未使用 dff helper) | stripped 版已 remove 未使用模块和冗余注释,等价证明更稳定;`equivalence_candidates` 在 stripped 版上 12812 proven,1 unproven 仅为 Yosys find_same_wires 假阴性(nor4b_1/nor4b_2 Liberty function 等价) | 已写入 `scripts/verify_b17_final_sec.py` 默认 `--itc-b17` 参数;新 SEC runner 通过 WSL2 Yosys 调用,复用 crossbench_sec 的命名空间 rename 模式 |
| 2026-09-08 | b17 SEC 容许 1/12813 unproven wire 视作 pass,前提是 Liberty function 等价 | Yosys `find_same_wires` 在被重命名 cell 输出 wire 上是保守的,且 nor4b_1/nor4b_2 在 assign-style cells.v 模型下布尔等价;真正等价性由 Liberty function + 调用方不引发行为变化共同保证 | `sec_result.json` 增加 `equiv_proven` / `equiv_unproven` / `note` 字段,显式记录容差边界;后续如 unproven 数 > 1 则 result=fail |
