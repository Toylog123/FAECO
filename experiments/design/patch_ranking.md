# Timing-Aware Patch Ranking 设计草案

更新时间：2026-07-07

## 1. 目标

当同一个 timing ECO case 产生多个候选 patch 时，需要选择一个既能改善时序、又能控制修改规模和验证成本的 patch。第一版不使用 GNN/RL，采用可解释的确定性评分。

## 2. 评分公式草案

```text
score = alpha * timing_gain
      - beta  * patch_size
      - gamma * boundary_complexity
      - delta * verification_cost
      + eta   * equivalence_confidence
```

## 3. 特征定义

| 特征 | 含义 |
|---|---|
| timing_gain | WNS/TNS 改善，或第一阶段用 logic level reduction 近似 |
| patch_size | patch 内 gate 数 |
| boundary_complexity | cut boundary 的输入输出数量、fanout、reconvergence 程度 |
| verification_cost | 等价验证运行时间、SAT 难度或 cone size |
| equivalence_confidence | 等价点数量、边界映射稳定性、验证通过情况 |

## 4. Baseline

| baseline | 说明 |
|---|---|
| random ranking | 随机选择候选 patch |
| size-only ranking | 只选 patch size 最小 |
| timing-only ranking | 只选 timing gain 最大 |
| critical-path-only ranking | 只按关键路径覆盖排序 |
| FAECO ranking | 综合评分 |

## 5. 第一版取舍

- 不上 GNN/RL。
- 不声称 score 是最优，只声称它是工程可解释的多目标排序。
- 如果第一版结果足够好，论文里把 ranking 作为补强贡献。
- 如果 ranking 结果一般，论文主贡献仍放在 failure-aware cut refinement。

## 6. 后续扩展

后续可以把这些人工特征输入轻量模型，如 GBDT 或 GNN，但不作为第一篇中文论文的必要条件。

