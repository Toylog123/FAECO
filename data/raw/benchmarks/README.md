# Benchmarks

这里保存公开 benchmark 和规范化后的 timing ECO case 输入。`raw/` 目录只放原始或第三方整理后的 benchmark 文件，不在原地做实验性修改。

## 目录说明

| 路径 | 作用 |
|---|---|
| `raw/` | 原始公开 benchmark 或来源可追溯的第三方整理版本 |
| `normalized/` | 经过统一格式转换的 netlist，后续需要时再生成 |
| `generated_cases/` | 根据时序约束变化生成的 ECO cases，后续需要时再生成 |
| `source_manifests/` | 固定上游版本、许可、文件哈希和使用边界的机器可读清单 |

## 当前已放入

| 路径 | 来源 | 说明 |
|---|---|---|
| `raw/iscas85/c17.v` | 项目早期手工最小联调用 ISCAS85 c17 Verilog | 用于最小 parser、flow 和 demo smoke |
| `raw/iscas85/c432.v` | `jpsety/verilog_benchmark_circuits` at commit `b4c6b6203b95b5314d47365f4a8196c08145519b`, blob `c886d1ca96acbfea3d04ede8636a5ad0aafde796` | ISCAS85 c432 generic-gate Verilog，Cadence Genus 生成，repo 未声明 license |
| `raw/iscas85/c499.v` | `jpsety/verilog_benchmark_circuits` at commit `b4c6b6203b95b5314d47365f4a8196c08145519b`, blob `b68d6bc0eceb6da9b5072cddb4fa751bb4fb8d95` | ISCAS85 c499 generic-gate Verilog，Cadence Genus 生成，repo 未声明 license |
| `raw/iscas85/c880.v` | `jpsety/verilog_benchmark_circuits` at commit `b4c6b6203b95b5314d47365f4a8196c08145519b`, blob `1c40743fc6332319823354b3bdd4f622dad8345f` | ISCAS85 c880 generic-gate Verilog，Cadence Genus 生成，repo 未声明 license |

源仓库 README 说明这些文件来自 ISCAS85 Benchmarks 和 EPFL Combinational Benchmark Suite，并被综合为 consistent generic gate Verilog format。当前记录为“来源可追溯的第三方整理版本”，不能等同于官方原始发布包。

## 来源治理决策

| 来源 | 固定版本 | 许可状态 | 当前用途 |
|---|---|---|---|
| EPFL Combinational Benchmark Suite | tag `v2025.1`，commit `8c832d5d07d822d28ba84dc6e95295367702401f` | MIT，发布时保留版权和许可声明 | 已选为论文级 Stage A 主来源；8 个 Verilog/官方 BLIF 已固定并通过隔离 CEC，尚待正式导入 |
| 当前 c432/c499/c880 | commit `b4c6b6203b95b5314d47365f4a8196c08145519b` | 上游未声明 license | 仅用于本地 parser/flow/batch smoke，不进入论文主实验或可再分发数据包 |

详细审计和候选电路见 `docs/experiment_design/benchmark_source_and_license_audit.md`；机器可读锁定信息见 `source_manifests/epfl_v2025.1.json` 和 `source_manifests/iscas85_jpsety_b4c6b620.json`。

## 导入工具

| 脚本 | 作用 |
|---|---|
| `scripts/make_minimal_case_from_raw.py` | 从本地 raw Verilog 生成一个最小 ECO case，可直接进入 `build_case_metrics` 和 batch runner |
| `scripts/make_minimal_case_from_bench.py` | 从本地 ISCAS-style `.bench` 文件转换生成最小 ECO case，当前支持 `NAND`、`AND`、`OR`、`NOR`、`NOT`、`BUF`、`XOR`、`XNOR` |

## 当前缺口

- EPFL `v2025.1` 的 8 个 Verilog/官方 BLIF blob 已复核，隔离 Yosys 规范化对官方 BLIF CEC 为 8/8 pass；原文件仍未进入正式 benchmark/data 目录，MIT license/第三方 notice 也尚未随派生数据归档。
- EPFL Verilog 和 Yosys `write_verilog -noexpr` 输出均超出当前轻量 parser grammar；正式导入需先批准 BLIF、Yosys JSON 或确定性 simple-gate Verilog 作为权威格式。
- 当前 ISCAS85 文件仍缺少明确 license，只保留为本地 smoke 数据。
- 当前 raw 文件用于 Python-only 原型实验，尚未接入 Yosys/ABC/OpenSTA/SAT 级验证。
