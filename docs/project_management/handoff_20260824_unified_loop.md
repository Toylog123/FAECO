# FAECO 统一闭环完成交接

更新时间：2026-08-24（Asia/Shanghai）

状态：本轮 T03–T05 文档与复审工作完成；实现已通过复审，适合进入合并准备。尚未合并 `main`，也未执行远端 push 等最后收尾。

## 1. 项目是什么

- FAECO 是面向逻辑级时序 ECO 的 failure-aware 修复框架。当前开发主线是把加权割、F1–F6 失败反馈、多轮候选搜索、真实形式验证、setup/hold 与成对物理验收合并为同一个可审计的 stateful timing-closure loop。
- 项目总览见 `README.md`；本轮代码主线位于 `src/rseco/`，生产入口和实验入口主要位于 `src/rseco/real_wns.py` 与 `scripts/run_outerloop_real_wns.py`。

## 2. 当前做到哪一步

- 实现分支：`codex/faeco-unified-loop`。
- 实现基线：`79b8f05cf0274efca2895a588ada82f6e1234140`（`fix final unified-loop review findings`）。
- 相对 `origin/main`（本轮最终提交后的 git 实测口径）：18 个提交、26 个文件、5270 行新增、135 行删除；其中实现分支当前本地 HEAD 尚包含未 push 的文档提交链。
- 工作树：`C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop`；当前 feature worktree 在提交检查后保持干净，主目录状态单独记录为 8 modified/3 deleted/103 untracked。
- 运行状态：实现修复已完成；只剩干净 integration worktree 中的合并演练、全量回归/WSL SEC 复核和用户批准后的 push。
- 2026-08-24 主代理新鲜回归：`python -m pytest -q -p no:cacheprovider` → `351 passed, 4 skipped, 1 subtests passed`。
- 真实 WSL 复核：async-clear SEC `1 passed`；WSL 工具版本为 Yosys `0.33`、ABC `1.01`。

## 3. 已完成的关键工作

- 统一 stateful timing-closure loop，覆盖状态提交、patch budget、停止条件与反馈轨迹，核心见 `src/rseco/flow.py`、`src/rseco/refinement_loop.py`、`src/rseco/real_wns.py`。
- constrained k-best cut、关键路径 anchor 与 topology rewrite 已接入，核心见 `src/rseco/cut.py`、`src/rseco/logic_rewrite.py`、`src/rseco/replacement.py`。
- 生产验收已覆盖真实 Yosys/ABC full-netlist SEC、Liberty named-pin/顺序单元建模、setup/可选 hold、成对 physical gain 与 fail-closed 路径，核心见 `src/rseco/yosys_abc.py` 与 `src/rseco/real_wns.py`。
- Sol 规格初审为 `CHANGES_REQUIRED`（2 Critical + 4 Important）；复审结论为 `APPROVED`。全部闭环及证据见 `docs/engineering/unified_loop_sol_final_review_20260824.md`。
- `79b8f05` 关闭了异步 clear/preset SEC 建模、stateful timing stop/final patch、跨 cell Boolean pin-role、full-netlist ABC 兼容模型、physical hold 排序与 physical baseline cache 等复审项。
- 回归测试集中在 `tests/test_constrained_cut_and_topology.py`、`tests/test_production_runner.py`、`tests/test_sol_review_residuals.py`、`tests/test_unified_loop_state.py`。

## 4. 当前阻塞与风险

- 远端状态：历史 13 个实现提交与旧交接文档已推至 `f909a31`；`origin/codex/faeco-unified-loop` 当前实测停在该 SHA。本地 feature worktree 的 `79b8f05`、`8353a55` 及本轮文档提交仍未 push。主目录 `main` 的历史脏改动不属于本轮分支，禁止清理、覆盖或混入合并。
- 主目录 `D:\BaiduSyncdisk\03_FAECO` 当前有 8 个 modified、3 个 deleted、103 个 untracked 项；不得把主目录写成 clean，也不得在其上直接 merge。
- 4 个 Windows skip 仍是外部工具可用性边界；WSL 已补跑 async-clear SEC 1 passed，但尚未声称所有大型真实 outer-loop/P&R 均重跑。
- 尚未合并 `main`，也尚未完成远端 push 等最后收尾；主目录的历史脏改动不得混入合并。
- `docs/project_management/STAGE_B_AGENT_HANDOFF.md` 保留历史正文并带 superseded banner；统一闭环当前状态以本文、`.codex-handoff.json` 和新增复审/策略文档为准。

## 5. 下一步最值得做的 3 到 5 项

| ID | 任务 | 状态 | 优先级 | 完成标准 | 下一步动作 |
|---|---|---|---|---|---|
| T01 | 在具备真实 Yosys/ABC/WSL 的环境复跑 SEC | pending | P0 | 4 个环境 skip 转为执行并通过，保存命令与原始输出 | 激活完整工具链后重跑 `tests/test_convert_itc99_blif_to_v.py`、`tests/test_yosys_abc_flow.py` 与真实 SEC 用例 |
| T02 | 重新生成一份可存档的 Sol 最终复审 | done | P0 | 初审 2 Critical+4 Important 全部 closure，复审 APPROVED | `docs/engineering/unified_loop_sol_final_review_20260824.md` |
| T03 | 制定合并策略并保护主目录脏改动 | done | P0 | 明确干净 integration worktree 路线；不触碰主目录 114 项历史改动 | `docs/project_management/unified_loop_merge_strategy_20260824.md` |
| T04 | 更新长期项目文档 | done | P1 | 交接、看板、日志与统一闭环分支状态一致 | 本文及 `STAGE_B_AGENT_HANDOFF.md` 已同步 |
| T05 | 将新闭环与论文 claim/实验表重新对齐 | done（证据审计） | P1 | claim 映射到代码/测试/commit，并标出未重跑的大型实验边界 | `docs/paper_audit/unified_loop_claim_evidence_20260824.md`；论文 headline 数字暂不更新 |

## 6. 关键文档与命令

- 首要交接文档：`docs/project_management/handoff_20260824_unified_loop.md`
- Sol 最终复审：`docs/engineering/unified_loop_sol_final_review_20260824.md`
- 合并策略：`docs/project_management/unified_loop_merge_strategy_20260824.md`
- Claim 证据审计：`docs/paper_audit/unified_loop_claim_evidence_20260824.md`
- 磁盘审计：`docs/project_management/disk_usage_audit_20260824.md`
- 旧项目总交接：`docs/project_management/STAGE_B_AGENT_HANDOFF.md`（状态滞后，仅作历史背景）
- 任务看板：`docs/task_board.md`（统一闭环 T02–T05 已同步；磁盘删除/进一步清理仍需用户按路径批准）
- 用户旧任务：`codex://threads/01a021eb-9273-7e13-8c07-9642e8d2f589`
- 状态检查：`git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop status --short --branch`
- 实现提交：`git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop log --oneline b8c3759..79b8f05`
- 全量回归：`python -m pytest -q -p no:cacheprovider`
- 环境 skip 复核：`python -m pytest -q -rs -p no:cacheprovider tests/test_convert_itc99_blif_to_v.py tests/test_sol_review_residuals.py tests/test_yosys_abc_flow.py`

## 7. 文档缺口与建议补齐项

- 主目录磁盘审计与 `experiments/` NTFS 原位压缩最终结果见 `docs/project_management/disk_usage_audit_20260824.md`；删除、移动、重命名、归档均为 0。
- 独立只读复核的 full-current 压缩汇总：310251 files / 79074 directories，310251 compressed / 0 uncompressed，18,073,112,096 logical bytes → 5,877,220,044 physical bytes，3.1:1；D 可用空间 42.931→54.387 GiB（+11.456 GiB）。抽检 `sta.log` 333,472,702→125,054,976 bytes 且可读。
- 大型真实 outer-loop/P&R 尚未重跑；旧论文 headline 数字保持原状，不能由本轮代码回归自动更新。

## Push 状态

- 目标远端：`origin`（`https://github.com/Toylog123/FAECO.git`）
- 目标分支：`codex/faeco-unified-loop`
- 实现修复 commit：`79b8f05cf0274efca2895a588ada82f6e1234140`
- 当前本地文档链：`8353a559766fd162f508f1485aa3582e20876855` 为提交前一节点；本轮文档提交尚未写入自身 SHA，见 `.codex-handoff.json` 的非自指说明。
- 当前远端：`origin/codex/faeco-unified-loop=f909a310a86c7338bfd1f733b515e688c2283ecd`；尚未合并 `main`，也未 push。
