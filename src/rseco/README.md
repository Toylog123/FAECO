# rseco package

FAECO 算法原型代码放在这里。

第一阶段计划模块：

- `netlist`
- `graph`
- `equivalence`
- `cut`
- `patch`
- `ranking`
- `flow`
- `metrics`

当前已有最小实现：

| 文件 | 作用 |
|---|---|
| `abc_baseline.py` | ABC rewrite/refactor/resyn baseline wrapper；无 ABC 时写回 `unavailable` |
| `case_loader.py` | 读取最小 case 的 `case.yaml` 和标准路径 |
| `netlist.py` | 解析当前 c17 风格的简单门级 Verilog，计算 gate count 和 logic level |
| `graph.py` | 抽取 fanin cone，并生成 boundary/internal/gate 信息 |
| `equivalence.py` | 最小结构等价检查，以及 ABC `cec` formal equivalence wrapper；无 ABC 时写回 `unavailable` |
| `cut.py` | fixed baseline、weighted split graph 和 Edmonds-Karp s-t min-cut 初版 |
| `patch.py` | patch candidate 表示和写回字段 |
| `replacement.py` | selected patch 的 cone-level 内部替换结果表示 |
| `flow.py` | 构造并写出最小 case metrics、target cone、candidate patch、selected patch、formal equivalence 状态和 ABC baseline 状态 |
| `metrics.py` | `change_ratio`、`logic_level_reduction` 等基础指标 |
| `failures.py` | F1-F5 失败类型枚举、阈值和失败分类 |

当前还没有实现 fanout cone、可综合 Verilog patch 写回、真实外部 SAT/ABC pass/fail 批量验证和真实 ABC/Yosys baseline 输出。批量 benchmark runner 已有最小版本，ABC formal wrapper 和 ABC baseline wrapper 已接入但当前工具链不可用；实验 runner 已在每个实验目录下归档 `environment/toolchain_snapshot.json`，用于解释这些 unavailable 状态。
