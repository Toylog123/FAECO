# ECO Case Schema

更新时间：2026-07-14

本文档定义 FAECO 实验中每个 ECO case 的最小数据结构。后续代码、实验脚本和结果表都应围绕这个 schema 组织。

## 1. 目录建议

```text
data/cases/<case_id>/
  case.yaml
  original/
    original.v
    original.blif
    synth.log
  resynthesized/
    resynthesized.v
    resynthesized.blif
    synth.log
  cones/
    target_cone.json
    candidate_cones.json
  patches/
    candidates.json
    selected_patch.json
  results/
    metrics.json
    verification.log
    run.log
```

## 2. case.yaml 字段

```yaml
case_id: iscas85_c432_case01
benchmark:
  suite: ISCAS85
  circuit: c432
  type: combinational
source:
  original_source: benchmarks/iscas85/c432.v
  license_note: public benchmark
toolchain:
  yosys_version: TBD
  abc_version: TBD
  opensta_version: optional
generation:
  original_script: scripts/synthesis/original.ys
  resynthesized_script: scripts/synthesis/resynthesized.ys
  target_constraint:
    type: logic_level
    value: TBD
target:
  output: TBD
  critical_path_id: TBD
  cone_roots: []
  cone_boundary_inputs: []
  cone_boundary_outputs: []
patch:
  initial_cut_method: fixed_min_cut
  refinement_method: failure_aware
  ranking_method: deterministic_score
metrics:
  required:
    - gate_count
    - logic_level
    - patch_size
    - change_ratio
    - equivalence_result
    - runtime_total
  optional:
    - WNS
    - TNS
    - violating_paths
status:
  stage: draft
  verified: false
```

## 3. 输入字段定义

| 字段 | 含义 | 必填 |
|---|---|---|
| `case_id` | 全局唯一 case 名称 | 是 |
| `benchmark.suite` | benchmark 来源，如 ISCAS85、EPFL | 是 |
| `benchmark.circuit` | 电路名称 | 是 |
| `benchmark.type` | combinational 或 sequential | 是 |
| `source.original_source` | 原始 benchmark 文件路径 | 是 |
| `generation.original_script` | 生成 original netlist 的脚本 | 是 |
| `generation.resynthesized_script` | 生成 resynthesized netlist 的脚本 | 是 |
| `target.output` | 目标输出或目标路径终点 | 是 |
| `target.cone_boundary_inputs` | cone 边界输入 | 是 |
| `target.cone_boundary_outputs` | cone 边界输出 | 是 |

## 4. 输出字段定义

| 字段 | 含义 | 说明 |
|---|---|---|
| `patch.initial_cut_method` | 初始 cut 方法 | 第一版通常为 fixed min-cut |
| `patch.refinement_method` | 失败反馈方法 | FAECO 为 failure-aware |
| `patch.ranking_method` | patch 排序方法 | 第一版为 deterministic score |
| `metrics.gate_count` | 原始电路门数 | 用于规模归一化 |
| `metrics.logic_level` | 最大逻辑级数或目标 cone 逻辑级数 | Stage A 的主要时序替代指标 |
| `metrics.patch_size` | patch 中 gate 数 | 修改规模核心指标 |
| `metrics.change_ratio` | patch size / original gate count | 工程修改比例 |
| `metrics.equivalence_result` | pass/fail/timeout | 正确性指标 |
| `metrics.runtime_total` | 总运行时间 | 工程效率指标 |
| `metrics.WNS` | 最差负松弛 | 接入 OpenSTA 后使用 |
| `metrics.TNS` | 总负松弛 | 接入 OpenSTA 后使用 |
| `metrics.violating_paths` | 违例路径数量 | 接入 OpenSTA 后使用 |

## 5. Sequential case 扩展字段

```yaml
sequential:
  clock: clk
  launch_register: TBD
  capture_register: TBD
  reg_to_reg_path_id: TBD
  state_boundary_preserved: true
```

扩展规则：

1. 不修改寄存器结构。
2. 只抽取 launch register 到 capture register 之间的组合逻辑 cone。
3. patch replacement 只能发生在 cone 内。
4. equivalence checking 以 cone 边界为准。
5. 时序结果优先使用 path delay、WNS、TNS。

## 6. 最小验收标准

一个 case 可以进入实验统计，需要满足：

1. `case.yaml` 字段完整。
2. original 与 resynthesized netlist 均可解析。
3. target cone 可抽取。
4. 至少生成一个候选 patch。
5. equivalence checking 有明确 pass/fail/timeout。
6. metrics 可写入 `results/metrics.json`。
