# Minimal Cases

这里保存用于单元测试和第一轮原型联调的小型 ECO case。

当前包含：

| Case | 来源 | 用途 |
|---|---|---|
| `iscas85_c17_case01` | ISCAS85 c17 | 验证 case schema、netlist 读取、fanin cone 自动抽取、结构等价、fixed cut patch 和草案 `results/metrics.json` |
| `iscas85_c17_case02` | ISCAS85 c17 / target `N23` | 验证同一公开电路的第二 target-output case、batch summary 和 replacement 输出 |
| `iscas85_c432_case01` | ISCAS85 c432 generic-gate Verilog | 独立 combinational benchmark case，target output `N432`，已生成 metrics、selected patch 和 replacement |
| `iscas85_c499_case01` | ISCAS85 c499 generic-gate Verilog | 独立 combinational benchmark case，target output `N755`，已生成 metrics、selected patch 和 replacement |
| `iscas85_c880_case01` | ISCAS85 c880 generic-gate Verilog | 独立 combinational benchmark case，target output `N880`，已生成 metrics、selected patch 和 replacement |

当前 batch 已包含 `c432`、`c499`、`c880` 三个独立电路，已经从 c17 双目标 smoke 推进到最小多电路组合逻辑实验。注意：这些 case 仍是 Python-only 原型验证，结构等价仍为 structural signature，不是 ABC/SAT 论文级验证；其第三方来源 license 未声明，因此也不是许可完备的论文主实验集。
