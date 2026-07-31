# 工程结构说明

更新时间：2026-07-07

## 1. 目录划分原则

本项目同时包含论文、算法、数据和实验。目录划分按责任边界组织：

- 原始材料只读保存；
- 新论文材料集中在 `paper/`；
- 工程代码集中在 `src/`；
- 测试集中在 `tests/`；
- 可复现实验输入集中在 `benchmarks/` 和 `data/`；
- 每次实验输出集中在 `experiments/`；
- 过程性说明和设计文档集中在 `docs/`。

## 2. 工程目录

```text
03_FAECO/
├── README.md
├── RSECO学长论文接手发表方案.md
├── 项目重启与论文推进方案.md
├── 论文/
├── 课题构想/
├── ECO相关文献/
├── docs/
│   ├── mainline.md
│   ├── engineering_structure.md
│   ├── paper_audit/
│   ├── experiment_design/
│   └── literature/
├── paper/
│   ├── README.md
│   ├── draft/
│   ├── figures/
│   ├── tables/
│   ├── reviews/
│   └── submission/
├── src/
│   └── rseco/
├── tests/
├── benchmarks/
│   ├── raw/
│   ├── normalized/
│   └── generated_cases/
├── data/
│   ├── cases/
│   ├── libraries/
│   └── constraints/
├── experiments/
└── scripts/
```

## 3. 后续代码模块边界

后续 `src/rseco/` 建议按以下模块拆分：

| 模块 | 责任 |
|---|---|
| `netlist` | 读取、规范化和表示 gate-level netlist |
| `graph` | 电路图、fanin/fanout cone、cut boundary |
| `equivalence` | Z3/ABC 等价验证和 counterexample 解析 |
| `timing` | OpenSTA 输出解析、关键路径和 slack 特征 |
| `cut` | min-cut 建模、权重函数、failure-aware refinement |
| `patch` | patch 表示、替换、合法性检查 |
| `ranking` | timing-aware patch ranking |
| `flow` | benchmark case generation 和端到端实验流程 |
| `metrics` | success rate、patch size、logic level、runtime 等指标 |

## 4. 实验输出规范

每次实验使用独立目录：

```text
experiments/YYYYMMDD_short_name/
├── config.yaml
├── logs/
├── raw_results/
├── tables/
├── figures/
└── summary.md
```

任何论文表格必须能追溯到对应实验目录。
