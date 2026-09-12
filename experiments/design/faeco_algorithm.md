# FAECO Algorithm

更新时间：2026-07-19

文档性质：目标算法规范。当前实现只覆盖组合逻辑 fanin cone、cut/candidate/ranking 和单次 refinement proxy；`equivalence_map`、真实 boundary closure、Boolean patch synthesis、可综合 `patched_netlist`、候选级 formal/STA 以及多轮停止条件尚未完整实现。论文表述应以 `docs/paper_audit/method_rewrite_readiness.md` 和当前代码/实验产物为准，不能把下述目标流程直接写成已实现能力。

FAECO，即 Failure-Aware ECO，是一个基于验证反馈的重综合辅助时序 ECO 框架。第一版目标是稳定跑通公开 benchmark 上的局部组合逻辑 cone，不直接声明修改寄存器结构。

## 1. 输入与输出

输入：

| 字段 | 含义 |
|---|---|
| `original_netlist` | 原始网表，模拟已有 APR netlist 的逻辑结构 |
| `resynthesized_netlist` | 新约束或新综合脚本下的重综合网表 |
| `target_cone` | 目标关键路径或目标输出的局部 cone |
| `equivalence_map` | 新旧网表中的等价点映射 |
| `case_config` | 阈值、timeout、最大迭代轮数、baseline 配置 |

输出：

| 字段 | 含义 |
|---|---|
| `selected_patch` | 最终选择的 patch |
| `patched_netlist` | 应用 patch 后的网表 |
| `metrics` | patch size、logic level、equivalence、runtime 等指标 |
| `failure_log` | 每轮失败类型和反馈动作 |

## 2. 总体流程

```text
FAECO(original_netlist, resynthesized_netlist, target_cone, config):
    normalize netlists
    compute graph features
    find or load equivalence map
    initialize cut weights
    candidates = []

    for iteration in 1..max_iterations:
        boundary = min_cut(original_graph, resynthesized_graph, weights)
        patch = extract_patch(boundary)
        verification = check_equivalence(patch)
        metrics = evaluate_patch(patch)
        failure_types = classify_failure(verification, metrics)

        record candidate, metrics, failure_types

        if is_success(verification, metrics):
            candidates.append(patch)
            if enough_candidates(candidates):
                break

        weights = refine_weights(weights, failure_types, boundary, metrics)

    selected_patch = rank_candidates(candidates)
    return selected_patch, metrics, failure_log
```

## 3. 初始化权重

每条候选 cut edge 的初始权重由以下特征构成：

| 特征 | 方向 |
|---|---|
| `is_equivalence_point` | 非等价点权重设高 |
| `critical_path_distance` | 越靠近关键路径越允许被 cut 覆盖 |
| `logic_level_gain` | 新网表相对原网表收益越大，越优先 |
| `boundary_complexity` | fanout/reconvergence 越复杂，权重越高 |
| `estimated_patch_size` | 过大 patch 区域权重越高 |

初始形式：

```text
weight(e) =
    w_base
  + w_non_eq      * non_equivalence_penalty(e)
  + w_boundary    * boundary_complexity(e)
  + w_size        * estimated_patch_size(e)
  - w_critical    * critical_path_coverage(e)
  - w_gain        * logic_level_gain(e)
```

## 4. 成功条件

candidate patch 只有同时满足以下条件才视为成功：

1. equivalence checking 通过。
2. boundary closed，无悬空输入和未映射输出。
3. `patch_size <= max_patch_size` 且 `change_ratio <= max_patch_ratio`。
4. Stage A 中 `logic_level_reduction >= min_logic_level_reduction`。
5. Stage B 中 WNS/TNS 或 path delay 有改善。
6. verification 和 case runtime 未超时。

## 5. 失败分类

失败分类使用 `failure_taxonomy.md`：

| 类型 | 触发条件 | 是否可继续 refinement |
|---|---|---|
| F1 等价失败 | verification fail | 是 |
| F2 边界不闭合 | boundary invalid | 是 |
| F3 patch 过大 | size 超阈值 | 是 |
| F4 时序收益不足 | gain 不足 | 是 |
| F5 验证代价过高 | timeout 或 cone 过大 | 是，但需强制限制规模 |

## 6. 权重反馈规则

```text
refine_weights(weights, failures, boundary, metrics):
    if F1 in failures:
        penalize current boundary edges
        reward nearby stable equivalence points

    if F2 in failures:
        penalize high-fanout and reconvergent boundary
        require closed boundary candidates

    if F3 in failures:
        penalize non-critical region expansion
        increase size penalty

    if F4 in failures:
        reward uncovered critical path nodes
        increase timing gain weight

    if F5 in failures:
        reduce max cone size
        increase verification cost penalty

    decay update magnitude by iteration
    return weights
```

## 7. Candidate ranking

多个成功 candidate 使用确定性 score 排序：

```text
score = alpha * timing_gain
      - beta  * patch_size
      - gamma * boundary_complexity
      - delta * verification_cost
      + eta   * equivalence_confidence
```

默认优先级：

1. equivalence pass。
2. 不超过 patch size 阈值。
3. timing gain 更高。
4. patch size 更小。
5. verification cost 更低。

## 8. 停止条件

算法在以下任一条件满足时停止：

| 条件 | 说明 |
|---|---|
| `max_iterations` 达到 | 默认 10 |
| 找到足够候选 | 默认至少 1 个成功 candidate |
| case timeout | 默认 600 秒 |
| 连续失败无新 boundary | 避免重复搜索 |
| verification 连续 timeout | 降低 cone size 或终止 |

## 9. 与 baseline 的区别

| 方法 | 是否使用失败分类 | 是否更新权重 | 是否 ranking |
|---|---|---|---|
| fixed min-cut | 否 | 否 | 否 |
| size-only cut | 否 | 否 | 按 size |
| critical-path-only cut | 否 | 否 | 按 coverage |
| FAECO | 是 | 是 | 是 |

## 10. 最小实现切分

| 模块 | 最小功能 |
|---|---|
| `netlist` | 读取小型 gate-level netlist |
| `graph` | 计算 fanin/fanout cone 和 logic level |
| `equivalence` | 对 cone/patch 做等价检查 |
| `cut` | 生成 min-cut boundary 和更新 weights |
| `patch` | 表示 patch 并检查 boundary closed |
| `ranking` | 对成功 candidate 打分 |
| `metrics` | 输出统一 metrics JSON |

第一版验收标准：至少一个 ISCAS85 case 能从 original/resynthesized 生成 candidate patch，完成等价验证、failure classification、weight refinement 和 metrics 输出。
