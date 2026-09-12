# Benchmark Flow 设计草案

更新时间：2026-07-19

## 1. 目标

建立一个公开、可复现的 timing ECO case generation flow，解决旧 RSECO 工作依赖工业案例、代码和实验数据不可恢复的问题。

## 2. 分阶段数据范围

| 阶段 | 数据范围 | 目的 |
|---|---|---|
| Stage A | Combinational benchmark，如 ISCAS/EPFL | 先验证 patch replacement、等价性和逻辑级数变化 |
| Stage B | Sequential benchmark，如 ITC/ISCAS sequential | 抽取时序路径中的组合逻辑 cone，更接近真实场景 |
| Stage C | 可恢复工业案例，如果后续能拿到 | 作为工程 case study，而不是唯一证据 |

## 3. Case 构造思路

每个 case 包含：

1. 原始网表 `original_netlist`。
2. 约束变化或目标变化后的重综合网表 `resynthesized_netlist`。
3. 关键路径或目标 cone。
4. 候选 patch boundary。
5. 等价验证结果。
6. 时序/结构指标。

## 4. 第一阶段输入输出

输入：

- 公开 combinational Verilog / BLIF；
- 简化 gate library；
- synthesis script；
- 目标 delay / logic-level constraint。

输出：

- normalized original netlist；
- resynthesized netlist；
- target cone list；
- candidate patch list；
- case metadata；
- baseline results。

## 5. 第二阶段扩展

对 sequential benchmark，不直接修改寄存器结构，而是：

1. 识别 reg-to-reg timing path；
2. 提取两个寄存器边界之间的组合逻辑 cone；
3. 在 cone 内执行 FAECO patch replacement；
4. 保持寄存器、时钟和状态边界不变；
5. 用 OpenSTA 验证路径级 WNS/TNS 变化。

## 6. 指标

| 指标 | 说明 |
|---|---|
| WNS / TNS | 工程类时序指标，能接 OpenSTA 时优先使用 |
| violating paths | 违例路径数量 |
| logic level / Max-LL | 关键路径逻辑级数 |
| patch size | 替换 patch 的 gate 数 |
| change ratio | patch size / 原网表 gate 数 |
| runtime | 总运行时间和分阶段运行时间 |
| equivalence pass rate | patch 等价验证通过率 |
| recovery success rate | 初始失败后经 refinement 成功的比例 |

## 7. Baseline

| baseline | 作用 |
|---|---|
| fixed min-cut | 最重要消融，证明 failure-aware refinement 有效 |
| random cut | 证明不是随机边界就能成功 |
| size-only cut | 证明只追求小 patch 不够 |
| critical-path-only cut | 证明只看关键路径不够 |
| ABC resyn/resyn2/rewrite/refactor | 开源重综合 baseline |
| ABC if/map | technology mapping baseline |

## 8. 当前决策

- 第一篇中文论文以公开 benchmark 为主，工业案例可选。
- Stage A 论文主数据源固定为 EPFL Combinational Benchmark Suite `v2025.1`；当前许可未声明的第三方 ISCAS85 文件只用于本地 smoke。
- 第一阶段允许只做 combinational cone，但论文必须说明第二阶段如何映射到 sequential timing path。
- 指标体系继承工程类 ECO 论文，不强制复刻学长表格，但保留 WNS/TNS、patch size、logic level、runtime 等核心指标。

## 9. 数据准入门槛

公开 benchmark 进入论文主结果前必须满足：

1. 固定官方或权威上游 tag、commit 和文件哈希。
2. 许可允许当前研究使用和预期发布方式，并归档所需 notice。
3. 原始文件、规范化文件和 case 生成命令可追溯。
4. 规范化前后和重综合前后的功能等价有 formal 结果。
5. benchmark summary 明确区分上游参考特征与 FAECO 实测指标。

当前来源审计见 `benchmark_source_and_license_audit.md`。
