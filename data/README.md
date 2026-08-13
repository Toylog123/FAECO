# Data

这里保存实验输入数据、最小 ECO cases、库文件和约束文件。

## 目录说明

| 路径 | 作用 |
|---|---|
| `cases/` | 小型手工或脚本生成的 ECO cases |
| `libraries/` | 标准单元库或简化 gate library，后续接入真实 EDA 工具时使用 |
| `constraints/` | SDC 或简化时序约束，后续接入 timing flow 时使用 |

## 当前最小 case

| 路径 | 说明 |
|---|---|
| `cases/minimal/iscas85_c17_case01/` | ISCAS85 c17 / target `N22` 最小 ECO case，用于原型联调 |
| `cases/minimal/iscas85_c17_case02/` | ISCAS85 c17 / target `N23` 第二目标 case，用于 batch runner 双目标 smoke |
| `cases/minimal/iscas85_c432_case01/` | ISCAS85 c432 / target `N432`，从 raw generic-gate Verilog 导入 |
| `cases/minimal/iscas85_c499_case01/` | ISCAS85 c499 / target `N755`，从 raw generic-gate Verilog 导入 |
| `cases/minimal/iscas85_c880_case01/` | ISCAS85 c880 / target `N880`，从 raw generic-gate Verilog 导入 |

c432/c499/c880 当前只用于本地 Stage A smoke。其第三方上游未声明 license，不进入论文主实验或可再分发数据包；固定来源与替代方案见 `benchmarks/source_manifests/` 和 `docs/experiment_design/benchmark_source_and_license_audit.md`。

## 生成工具

| 脚本 | 作用 |
|---|---|
| `scripts/make_minimal_case_variant.py` | 从已有 case 派生不同 target output 的 case |
| `scripts/make_minimal_case_from_raw.py` | 从本地 raw Verilog 生成最小 ECO case |
| `scripts/make_minimal_case_from_bench.py` | 从本地 ISCAS-style `.bench` 文件生成最小 ECO case |

当前 case 的 `original/` 与 `resynthesized/` 暂时相同，主要用于验证 FAECO 原型的数据流、cut/ranking/replacement 输出和 batch 汇总结构。真实 resynthesis、STA 和 SAT/ABC 验证仍待后续工具链接入。
