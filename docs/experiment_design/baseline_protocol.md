# Baseline Protocol

更新时间：2026-07-14

本文档定义 FAECO 实验中的 baseline、运行规则和公平性约束。

## 1. Baseline 总表

| ID | Baseline | 作用 | 必须对比 |
|---|---|---|---|
| B01 | fixed min-cut | 验证 failure-aware refinement 是否优于固定切割 | 是 |
| B02 | random cut | 排除随机边界偶然有效 | 是 |
| B03 | size-only cut | 验证只追求小 patch 不够 | 是 |
| B04 | critical-path-only cut | 验证只覆盖关键路径不够 | 是 |
| B05 | ABC rewrite/refactor/resyn | 开源重综合 baseline | 是 |
| B06 | ABC if/map | technology mapping baseline | 可选但建议 |
| B07 | no-refinement FAECO | 去掉失败反馈，只保留初始权重 | 是，用于消融 |
| B08 | FAECO without ranking | 验证 ranking 是否贡献额外收益 | 可选 |

## 2. Baseline 定义

| Baseline | 输入 | 输出 | 说明 |
|---|---|---|---|
| fixed min-cut | original、resynthesized、target cone | 一个 candidate patch | 使用固定权重，不根据失败结果调整 |
| random cut | 同上 | 多个随机 candidate patch | 使用固定 seed，重复运行取均值和方差 |
| size-only cut | 同上 | patch size 最小的 candidate | 只优化修改规模 |
| critical-path-only cut | 同上 | 关键路径覆盖最高的 candidate | 不考虑边界复杂度和验证代价 |
| ABC rewrite/refactor/resyn | original netlist | optimized netlist | 作为纯重综合参考，不一定生成局部 patch |
| ABC if/map | original netlist | mapped netlist | 观察 technology mapping 对逻辑级数的影响 |

## 3. 公平性规则

| 规则 | 要求 |
|---|---|
| 相同输入 | 所有方法使用同一个 original/resynthesized pair 和 target cone |
| 相同验证 | 所有 candidate patch 使用同一个 equivalence checker |
| 相同时间预算 | 单个 case 的总时间预算一致，单个 patch verification timeout 一致 |
| 固定随机种子 | random cut 必须记录 seed，默认至少 5 次重复 |
| 相同指标口径 | patch size、logic level、runtime、equivalence pass rate 使用同一计算脚本 |
| 失败也记录 | timeout、non-equivalent、patch too large 都进入统计，不丢弃 |

## 4. 默认实验配置

```yaml
experiment:
  max_iterations: 10
  random_trials: 5
  verification_timeout_s: 60
  case_timeout_s: 600
  max_patch_ratio: 0.15
  min_logic_level_reduction: 1
  seed: 20260714
```

## 5. 主结果表模板

| Case | Method | Eq Pass | Logic Level Before | Logic Level After | Gain | Patch Size | Change Ratio | Runtime(s) | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| TBD | fixed min-cut | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | FAECO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## 6. 消融实验

| ID | 方法 | 目的 |
|---|---|---|
| A01 | FAECO without F1 feedback | 验证等价失败反馈是否必要 |
| A02 | FAECO without F3 feedback | 验证 patch size 控制是否必要 |
| A03 | FAECO without F4 feedback | 验证 timing gain 反馈是否必要 |
| A04 | FAECO without ranking | 验证 patch ranking 是否必要 |
| A05 | max iteration sensitivity | 验证迭代次数对成功率和 runtime 的影响 |

## 7. 第一轮实验验收

第一轮实验可以进入论文草稿，需要至少满足：

1. Stage A 至少 8 个公开 combinational benchmark。
2. 每个 benchmark 至少比较 fixed min-cut、size-only、critical-path-only 和 FAECO。
3. 记录 equivalence pass/fail/timeout。
4. 至少有一张 main comparison table 和一张 failure recovery table。
5. 所有结果能追溯到 `case.yaml`、日志和 metrics 文件。
