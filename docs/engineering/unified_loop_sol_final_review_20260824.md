# Unified Loop Sol 最终复审记录

日期：2026-08-24（Asia/Shanghai）
实现基线：`79b8f05cf0274efca2895a588ada82f6e1234140`

## 结论

初审结论为 `CHANGES_REQUIRED`，共 2 项 Critical、4 项 Important。修复提交 `79b8f05` 后逐项复核，结论为 `APPROVED`。本记录只覆盖代码与测试证据，不把尚未重跑的大型 outer-loop/P&R 实验写成已验证。

## Closure matrix

| ID | 初审级别与问题 | 修复/证据 | 复审结论 |
|---|---|---|---|
| C1 | Critical：跨 cell 重命名时只比较规范化函数，未验证输入 pin role 是否保持 | `src/rseco/real_wns.py` 使用 `function_vars` 与 `source.pins`/`target.pins` 逐角色比较；`tests/test_production_runner.py::test_real_equivalence_checker_checks_cross_cell_boolean_pin_roles` 覆盖正确映射通过、交换映射失败 | closed |
| C2 | Critical：full-netlist SEC 对顺序单元异步 clear/preset 的建模及 ABC 输入路径不可靠 | `src/rseco/logic_rewrite.py` 解析 `clear`/`preset`；`src/rseco/real_wns.py` 生成带极性与连接的模型。Yosys `opt_clean` 保留 reset mux/DFF 结构，是该 async SEC 修复的必要细节，不是独立 finding；`tests/test_sol_review_residuals.py::test_real_wsl_sec_models_async_clear_polarity_and_connection` 真实 WSL 通过 | closed |
| I1 | Important：stateful loop 在 timing 已满足时未可靠 early-stop | `src/rseco/flow.py` 在接受候选后显式检查 setup/hold timing 并设置 `timing_met`；相关 stop-reason 测试通过 | closed |
| I2 | Important：达到 `max_iterations` 后 stop reason 与最后接受补丁 `final_patch_id` 可能不完整 | `src/rseco/flow.py` 补充 `max_iterations` 与最后一个 accepted patch 的 `final_patch_id`；`tests/test_sol_review_residuals.py` 覆盖迭代上限、stop reason 与最后补丁回传 | closed |
| I3 | Important：paired physical acceptance 在 hold 模式下只按 setup WNS 排序，可能接受 hold 较差候选 | `src/rseco/real_wns.py` 增加 `best_physical_hold`，hold 模式按 min-slack 优先、setup WNS 作 tie-break；`test_physical_hold_candidate_ranking_prioritizes_hold_gain` 等测试通过 | closed |
| I4 | Important：并行 physical candidate 的 baseline/cache key 与 single-flight 语义需要明确 | `src/rseco/real_wns.py` 使用 baseline hash+RC config hash 的独立 key，并在锁内复用 baseline；`test_parallel_physical_candidates_share_single_baseline_cache`、`test_physical_mode_keeps_distinct_candidate_sta_cache_keys` 通过 | closed |

## 命令与结果

| 检查 | 结果 |
|---|---|
| `python -m pytest -q -p no:cacheprovider` | `351 passed, 4 skipped, 1 subtests passed` |
| 真实 WSL async-clear SEC | `1 passed` |
| WSL Yosys | `0.33` |
| WSL ABC | `1.01` |
| 实现修复提交 | `79b8f05cf0274efca2895a588ada82f6e1234140` |

4 个 skip 仍属于当前 Windows shell 的外部工具可用性边界；一次真实 WSL async-clear 已通过，不能外推为所有大型真实 SEC、outer-loop 或 P&R 均已重跑。

## async event 残余边界

当前证据确认：Liberty `clear`/`preset` 的极性被解析，非 ABC 模型保留异步敏感列表，ABC 兼容模型通过 next-state mux 表达异步控制，且 reset 连接改变会被 full-netlist SEC 拒绝。残余边界是多异步控制优先级、复杂时钟门控/锁存器语义、真实大规模网表及不同 ABC/Yosys 版本的兼容性；这些需要后续针对性 WSL 实验，不能由本次 1 个 async-clear 用例概括。
