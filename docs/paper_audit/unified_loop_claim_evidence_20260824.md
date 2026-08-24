# Unified Loop Claim–Evidence 审计

日期：2026-08-24
代码基线：`79b8f05cf0274efca2895a588ada82f6e1234140`

| Claim | 代码证据 | 测试/运行证据 | 当前边界 |
|---|---|---|---|
| 统一 stateful timing-closure loop | `src/rseco/flow.py`、`src/rseco/refinement_loop.py` 的 `run_multi_iteration_case`、`SearchState`、stop reason 与 accepted patch state | `tests/test_unified_loop_state.py`、`tests/test_sol_review_residuals.py`；全量 `351 passed` | 本轮未重跑大型真实 outer-loop |
| constrained k-best cut / topology rewrite | `src/rseco/cut.py`、`src/rseco/logic_rewrite.py`、`src/rseco/replacement.py` | `tests/test_constrained_cut_and_topology.py`、生产 runner 回归 | 规模/运行时间 headline 不由单元回归更新 |
| F1–F6 failure feedback | `src/rseco/refinement_loop.py`、`src/rseco/real_wns.py` 的 failure events、weights 与 refinement | `tests/test_weighted_cut_feedback.py`、`tests/test_sol_review_residuals.py` | 反馈机制通过代码/测试，不代表新增大批量统计 |
| full-netlist SEC | `src/rseco/real_wns.py::build_full_netlist_sec_checker`、`src/rseco/yosys_abc.py` | mock wiring/full-netlist tests；真实 WSL async-clear SEC `1 passed` | 不是所有大型顺序网表已在本轮重跑 |
| setup / optional hold | `src/rseco/flow.py` timing stop；`src/rseco/real_wns.py` `hold_mode`、min-slack 与 optional hold handling | `tests/test_sol_review_residuals.py` hold/optional-hold tests | optional hold 缺失是有记录的证据边界，不可写成全量 hold signoff |
| paired physical acceptance | `src/rseco/real_wns.py` physical candidate comparison、setup/hold pair 与 provenance | physical pair/hold ranking/cache tests | 未重跑大型真实 P&R；不更新旧 P&R headline |
| budget / cache / deadline | `src/rseco/flow.py`、`src/rseco/refinement_loop.py` stop reasons；`src/rseco/real_wns.py` STA/SEC cache、deadline 与 single-flight | budget、terminal timeout、cache-key tests | 本轮验证行为边界，未宣称新吞吐率或规模指标 |

旧论文中的实验 headline 数字依赖特定配置、工具版本、实验目录和原始日志。本轮只完成代码修复、回归和证据映射，未重跑大型真实 outer-loop/P&R，因此旧数字不能因代码通过而自动更新；如要更新，必须另行绑定配置、工具链、日志和 commit。
