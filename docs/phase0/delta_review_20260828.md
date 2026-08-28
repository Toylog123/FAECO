# FAECO Phase 0.2 增量审查记录（79b8f05..c58ad8e）

日期：2026-08-28
审查分支：`codex/faeco-phase0-stabilization`（HEAD=c58ad8e）
审查范围：`79b8f05cf0274efca2895a588ada82f6e1234140..c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879`

## 1. 审查基础

- 提交数：实际 15 个（计划初稿按交接文档写 16 个，现场核实为 15 个；本记录以此为准）。
- 文档类提交 6 个：`8353a55`、`491280d`、`c284296`、`a524462`、以及 unified-loop 复审/证据/交接文档链。
- 实现类提交 9 个：`2939d6f`、`e9d95d2`、`1c60a58`、`cbb5f7d`、`abd816a`、`5966991`、`d595c71`、`3e93fd2`、`30f4164`、`b7abaac`、`c58ad8e`（其中含为 b15 深锥/非 ASCII 路径的修复）。

## 2. 变更总览

| 文件 | 变更性质 |
|---|---|
| scripts/run_sequential_timing_check.py | Yosys 脚本路径引号 + ANSI 编码（非 ASCII 路径） |
| src/rseco/equivalence.py | 结构签名改为迭代 DFS（深锥/环安全） |
| src/rseco/flow.py | constrained cut 增加关键路径 cover 首候选 + 子锥过滤 anchor |
| src/rseco/netlist.py | 向量声明 bit-blast（`[31:0] x` -> `x[0..31]`） |
| src/rseco/real_wns.py | F2 模块输出驱动数改为相对 baseline 校验 + 输出别名修复 |
| tests/* | 对应回归与新增测试约 +475 行 |

## 3. 逐项结论

| ID | Finding | Evidence | Verdict | Notes |
|---|---|---|---|---|
| C1 | 结构签名迭代化是否保持递归语义 | `_signal_signature` 迭代 DFS 在 pre-order 分配 id，重遇生成 `("ref", id)`；`_signature_equal` 深比较；`tests/test_graph_equivalence.py` 新增共享/分裂 SCC 与环安全用例 | closed | 真实 b15 深锥需在 G3 真实 SEC/哨兵中复核 |
| C2 | 向量 bit-blast 是否破坏 netlist 闭合 | 声明按位展开并映射 Yosys 位网命名；`tests/test_dff_preprocess.py` +129 覆盖 | closed | 若网表以总线基名引用，将 fail-closed（安全侧） |
| I1 | F2 输出驱动检查改为相对 baseline | 单网表检查不再把合法未驱动输出位判为缺陷，改为 before/after 驱动数比较；`real_wns.py` 有结构化失败 JSON | closed | 语义从绝对改为相对，属于明确设计决策 |
| I2 | constrained cut 空候选/锚点越界 | 子锥内过滤 critical instances；锚点不在子锥时不再压制全部候选（s27 G10 场景） | closed | `tests/test_constrained_cut_and_topology.py` 覆盖 |
| I3 | 关键路径 cover 作为首候选 | `_critical_path_cover_cut` 作为 constrained 路径默认候选，避免 beam-1 卡在单门；F1 约束只影响奖励不影响 cover 成员 | closed | `flow.py` 通过 `canonical_cut_hash` 去重 |
| I4 | Yosys map.ys 非 ASCII 路径 | 路径 token 引号转义 + ANSI 编码写出；`tests/test_yosys_map_script_encoding.py` 覆盖中文路径 round-trip | closed | Windows 原生 Yosys 读 ANSI；WSL 路径使用 posix 不受影响 |

## 4. 与 20260826 b15/b17 分析的交互

- b15 深锥导致结构签名递归过深：本范围内 `1c60a58/cbb5f7d/c58ad8e` 已改为迭代并加环安全，b15 场景的候选生成回归由新增测试锁定。
- b17 的 F5 60 秒软成本误拒问题不在本范围：本范围没有修改 `max_verification_time_s`；该问题由 Phase 1 预算语义批次处理（P1.2），不作为本范围 finding。
- 本范围内 `git diff --check` 仍报告 `src/rseco/equivalence.py` 与 `tests/test_graph_equivalence.py` 两处 EOF 空行，属于 P0.3 格式门禁任务，不改变本结论。

## 5. 结论

**APPROVED**：15 个提交中无开放 Critical/Important finding，无需要行为变更才能关闭的项。

已知边界（非阻断）：
- 真实大型顺序网表 SEC、真实 outer-loop 与 P&R 未在本轮重跑（沿用 2026-08-24 证据边界）。
- 向量 bit-blast 与相对输出驱动检查为语义变更，需在 P0.3 全量回归与 G5 哨兵中复核。
