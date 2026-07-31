# Failure Taxonomy

更新时间：2026-07-19

文档性质：目标 taxonomy 与阈值规范。当前 `FailureThresholds` 只实现 change ratio、logic-level reduction 和 verification time 三类阈值；flow 仍把 `boundary_closed=True`、`verification_runtime_s=0.0` 固定传入，并且只记录一次 refinement proxy。以下 F1-F5 全量检测条件、Stage B timing 阈值和多轮日志不能视为当前已实现结果。

本文档把 FAECO 中的 patch 失败从简单 pass/fail 拆成可检测、可记录、可反馈的失败类型。

## 1. 失败类型总表

| ID | 名称 | 检测条件 | 主要影响 | 反馈动作 |
|---|---|---|---|---|
| F1 | 等价失败 | SAT/ABC/Z3 miter 返回 non-equivalent 或 counterexample | patch 不能应用 | 惩罚当前 boundary，扩大或移动到更稳定的等价点 |
| F2 | 边界不闭合 | patch 存在悬空输入、未映射输出、多输出覆盖不完整 | 替换后功能不完整 | 惩罚高 fanout、reconvergence 和不稳定 mapping 区域 |
| F3 | patch 过大 | `patch_size > max_patch_size` 或 `change_ratio > max_change_ratio` | ECO 修改规模过大 | 提高非关键区域 cut cost，压缩 patch |
| F4 | 时序收益不足 | `timing_gain < min_timing_gain` 或 logic level 未下降 | 修复效果不足 | 提高关键路径未覆盖节点优先级 |
| F5 | 验证代价过高 | equivalence timeout、cone size 超阈值、SAT 调用过多 | flow 不稳定或不可扩展 | 限制 cone size，分层验证，惩罚过大边界 |

## 2. 默认阈值

第一版阈值先采用保守配置，后续通过实验调整。

| 参数 | 默认值 | 说明 |
|---|---:|---|
| `max_patch_ratio` | 0.15 | patch gate 数占 original gate 数比例 |
| `max_patch_size_small` | 200 | 小型 benchmark 的 patch gate 数上限 |
| `min_logic_level_reduction` | 1 | Stage A 至少降低 1 级逻辑级数 |
| `min_timing_gain_ratio` | 0.05 | Stage B WNS/TNS 至少改善 5% |
| `max_verification_time_s` | 60 | 单个候选 patch 等价验证时间上限 |
| `max_iterations` | 10 | failure-aware refinement 最大迭代次数 |

## 3. 失败记录格式

```yaml
failure:
  case_id: iscas85_c432_case01
  iteration: 3
  candidate_id: patch_003
  failure_types:
    - F1
    - F3
  equivalence:
    result: fail
    counterexample: available
  size:
    patch_size: 83
    change_ratio: 0.192
  timing:
    logic_level_before: 18
    logic_level_after: 17
    timing_gain: 1
  verification:
    runtime_s: 12.4
    timeout: false
  refinement_action:
    penalize_boundary: true
    increase_critical_coverage: false
    shrink_noncritical_region: true
```

## 4. 多失败优先级

同一个 candidate 可能同时触发多个失败。处理优先级如下：

| 优先级 | 失败 | 原因 |
|---:|---|---|
| 1 | F1 等价失败 | 功能不正确时不能讨论时序收益 |
| 2 | F2 边界不闭合 | boundary 不合法会导致后续指标失真 |
| 3 | F5 验证代价过高 | flow 不稳定，需限制搜索空间 |
| 4 | F3 patch 过大 | 功能正确但工程代价过高 |
| 5 | F4 时序收益不足 | 功能和规模可接受后再优化收益 |

## 5. 与论文实验的对应

| 论文实验 | 使用字段 |
|---|---|
| failure recovery table | failure type、initial fail count、recovered count |
| ablation | disable F1/F3/F4 feedback |
| failure case study | counterexample、boundary complexity、patch size |
| runtime breakdown | verification runtime、iteration count |

## 6. 与旧稿的关系

旧稿中的“第一次切割失败”“第二次切割失败”和“功能损伤”可以映射到 F1/F2，但覆盖范围不足。FAECO 将失败范围扩展到 patch size、timing gain 和 verification cost，使 failure feedback 更适合工程类论文的实验评价。
