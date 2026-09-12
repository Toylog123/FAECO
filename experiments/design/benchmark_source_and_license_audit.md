# Benchmark 来源与许可审计

更新时间：2026-07-20

本文档固定 FAECO 公开 benchmark 的来源、版本、许可和使用边界。它是工程侧来源审计，不替代正式法律意见。

## 1. 当前决策

| 数据源 | 当前用途 | 论文主实验 | 可再分发状态 | 决策 |
|---|---|---|---|---|
| EPFL Combinational Benchmark Suite `v2025.1` | Stage A 公开组合逻辑主数据源 | 待导入、构造 case 和 formal 验证后可用 | MIT，保留版权与许可声明后可分发 | 选为论文级主来源 |
| 当前 `c432/c499/c880` 第三方 Genus Verilog | parser、flow 和 batch smoke | 否 | 上游仓库未声明 license | 仅保留为本地 smoke 数据 |
| Berkeley ABC ISCAS 下载索引 | 可获得性线索 | 否 | 索引页未展示明确 license | 不据此升级当前文件许可状态 |
| SIR 数据源 | 不采用 | 否 | 非商业、不可转让且限制再分发 | 不纳入可再分发实验包 |

## 2. EPFL 固定版本

| 字段 | 固定值 |
|---|---|
| 官方页面 | `https://www.epfl.ch/labs/lsi/page-102566-en-html/benchmarks/` |
| 官方仓库 | `https://github.com/lsils/benchmarks.git` |
| tag | `v2025.1` |
| commit | `8c832d5d07d822d28ba84dc6e95295367702401f` |
| license | MIT |
| license Git blob | `ab602974d200aa6849e6ad8220951ef9a78d9f08` |
| 机器可读清单 | `benchmarks/source_manifests/epfl_v2025.1.json` |

EPFL 官方页面说明该套件包含 23 个组合逻辑电路，并提供 Verilog、VHDL、BLIF 和 AIGER 格式；官方页面指向 `lsils/benchmarks` 仓库。仓库 `LICENSE` 为 MIT，复制或派生发布时必须保留版权与许可声明。

## 3. 第一批候选电路

| 波次 | 电路 | 类别 | 官方输入/输出 | 官方 LUT-6/Levels | 选择理由 |
|---|---|---|---:|---:|---|
| 1 | `ctrl` | random/control | 7/26 | 29/2 | 小规模控制逻辑，适合先打通规范化链路 |
| 1 | `int2float` | random/control | 11/7 | 49/3 | 小规模转换逻辑，适合验证 escaped identifiers |
| 1 | `router` | random/control | 60/30 | 89/7 | 中小规模且有更复杂重汇聚结构 |
| 2 | `cavlc` | random/control | 10/11 | 122/4 | 增加控制逻辑规模 |
| 2 | `dec` | random/control | 8/256 | 287/2 | 扩展多输出场景 |
| 2 | `priority` | random/control | 128/8 | 210/31 | 增加深逻辑控制电路 |
| 2 | `adder` | arithmetic | 256/129 | 254/51 | 增加算术与深逻辑场景 |
| 2 | `max` | arithmetic | 512/130 | 842/56 | 增加中等规模算术场景 |

候选 Verilog 和同版本官方 BLIF 的路径与 Git blob SHA 已固定在 `benchmarks/source_manifests/epfl_v2025.1.json`。上述 LUT-6 和 Levels 是 EPFL 官方 README 中的参考特征，不是当前 FAECO 实测结果。

2026-07-19 已重新核验本地来源副本：HEAD、tag `v2025.1` 和 manifest commit 均为 `8c832d5d...2401f`，MIT license blob 为 `ab602974...9f08`，8 个 Verilog blob 与 8 个官方 BLIF blob mismatch 均为 0，来源工作树干净。

## 4. 格式兼容性审计

EPFL Verilog 使用 escaped identifiers 和连续赋值。当前轻量 parser 对 8 个候选都能读取 I/O 声明，但 gate count 全部为 0，因此不能直接进入 FAECO flow。

本机 smoke 结果显示，Yosys 0.9 可读取 `ctrl.v`，经 `proc; opt; flatten; techmap; simplemap` 后得到 306 个简单单元，其中 169 个 AND、132 个 NOT、5 个 OR。该结果只证明规范化路径可行，不是最终 benchmark 指标。

隔离导入就绪探针位于 Git 忽略的 `tmp/x21_epfl_readiness_probe_20260719_01/`，最终 `probe_summary.json` SHA256 为 `F268C5BF0A42DE0127F60B15DE65596F948169A2F0CDD09796685773B83E2A49`。探针从固定 Verilog 运行 Yosys 0.9 规范化，再以同一 tag 的官方 BLIF 为独立参照执行 `yosys-abc -s cec`：8/8 规范化成功、8/8 CEC pass，且双方 ABC `print_stats` 的 I/O、AIG and-node 和 level 全部一致。

| 电路 | 波次 | 直接 parser gates | AIG and-node | AIG level | 对官方 BLIF CEC |
|---|---:|---:|---:|---:|---|
| `ctrl` | 1 | 0 | 174 | 10 | pass |
| `int2float` | 1 | 0 | 260 | 16 | pass |
| `router` | 1 | 0 | 257 | 54 | pass |
| `cavlc` | 2 | 0 | 693 | 16 | pass |
| `dec` | 2 | 0 | 304 | 3 | pass |
| `priority` | 2 | 0 | 978 | 250 | pass |
| `adder` | 2 | 0 | 1020 | 255 | pass |
| `max` | 2 | 0 | 2865 | 287 | pass |

表中 node/level 是 ABC AIG 统计，不是 EPFL README 的 LUT-6 count/level，也不是当前 FAECO gate count。该探针只证明固定源文件的规范化功能一致性和规模可处理性，不代表 EPFL cases 已导入或产生 FAECO 方法结果。

第一波 ctrl/int2float/router 的 Yosys 规范化耗时分别约 0.361/0.497/0.444 秒，CEC 约 0.132/0.139/0.137 秒，可按“小、小、中”顺序推进。但 `write_verilog -noexpr` 仍输出 escaped `\$_AND_`/`\$_NOT_` 单元、named ports 和 escaped buses；当前 parser 对这三个导出文件仍为 0 gates，logic-level 计算失败。2026-07-20 已批准 Yosys JSON 作为 FAECO 权威内部格式；BLIF 保留为 ABC/formal 参照，simple-gate Verilog 暂不作为首轮主路径。

正式导入要求：

1. 从固定 tag/commit 获取原文件并校验 Git blob SHA。
2. 在实验产物中保留原始 source metadata、Yosys 命令、版本和 runtime。
3. 实现 Yosys JSON importer 作为 FAECO 权威规范化格式；不能把当前 0-gate Verilog 导出当作成功导入。
4. 对 original、normalized 和 resynthesized 版本执行 formal equivalence，并显式记录 full-netlist/boundary scope。
5. 为每个 case 固定 target output、resynthesis 生成策略、命令和随机性。
6. 分发任何 EPFL 源文件或派生产物时保留 MIT `LICENSE` 和第三方声明。

## 5. 当前 ISCAS85 边界

`c432/c499/c880` 来自 `jpsety/verilog_benchmark_circuits` 固定提交，文件头表明它们由 Cadence Genus 16.22 生成。来源提交、Git blob SHA 和本地 SHA256 已写入 `benchmarks/source_manifests/iscas85_jpsety_b4c6b620.json`。

该上游仓库没有声明可适用于这些文件的 license。EPFL 仓库的 MIT 许可也不能反向覆盖这些第三方 Genus 文件。因此：

- 当前 5-case batch 仍可作为本地工程 smoke 和回归产物；
- 论文中不能把该 batch 称为“许可完备的公开主实验集”；
- 对外发布数据包时不纳入这三个文件，除非后续取得明确许可；
- 新论文主结果优先迁移到固定版本的 EPFL 数据。

## 6. RR06 完成门槛

RR06 继续保持 `in_progress`，完成需要同时满足：

1. 8 个 EPFL 候选 Verilog/官方 BLIF 已固定并通过隔离 CEC；仍需把它们导入正式数据目录。
2. 仓库包含 MIT license/第三方 notice，并能追溯每个派生文件。
3. original/resynthesized case 构造命令、配置和运行环境可复现。
4. original/normalized/resynthesized 的 formal equivalence 有真实状态和日志。
5. benchmark summary、main comparison 和 runtime 表不再依赖许可未声明的 ISCAS85 文件作为主数据。
