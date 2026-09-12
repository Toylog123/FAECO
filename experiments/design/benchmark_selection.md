# Benchmark Selection

更新时间：2026-07-20

本文档定义 FAECO 第一批公开 benchmark 的选择策略。原则是先保证可复现和可解释，再逐步贴近真实 timing ECO。

## 1. 选择原则

| 原则 | 说明 |
|---|---|
| 公开可获得 | 不依赖学长工业数据或商业内部案例 |
| 规模可控 | 第一轮原型能跑通，避免一开始被工具链和规模卡住 |
| 可构造新旧网表 | 能通过不同综合脚本、约束或 ABC/Yosys pass 生成 original/resynthesized 对 |
| 可验证等价 | 能用 SAT/ABC/Z3 对候选 cone 或 patch 做等价验证 |
| 可扩展到时序场景 | 后续能接 OpenSTA 或至少接 logic-level delay 指标 |
| 来源与许可可审计 | 固定上游 tag/commit/file hash，明确再分发义务和论文使用边界 |

## 2. 第一批 benchmark 决策

| 阶段 | benchmark | 用途 | 当前决策 |
|---|---|---|---|
| Stage A | 当前 ISCAS85 combinational 文件 | 小规模组合逻辑，适合原型、单元测试和回归 smoke | 仅作本地 smoke；c432/c499/c880 上游 license 未声明，不进入论文主集 |
| Stage A | EPFL combinational `v2025.1` | 许可明确的组合逻辑主数据，适合规模扩展和逻辑级数优化 | 选为论文主来源；8 个 Verilog/官方 BLIF blob 已固定并通过隔离 CEC，正式 case 尚未导入 |
| Stage A | MCNC/IWLS combinational 子集 | 可作为补充数据 | 暂列候选 |
| Stage B | ISCAS89 sequential | 抽取 reg-to-reg combinational cone | 第二阶段使用 |
| Stage B | ITC99 sequential | 更接近 sequential timing path 场景 | 第二阶段候选 |
| Stage C | 旧工业案例 | 只能作为历史参考或 case study | 不作为主证据 |

## 3. Stage A 初始样例与论文主集

| 类别 | 建议电路 | 目的 |
|---|---|---|
| 本地 smoke | c17、c432、c499、c880 | 验证 parser、cone extraction、equivalence；不作为许可完备的论文主集 |
| EPFL 第一波 | ctrl、int2float、router | 先打通 escaped identifier、assign Verilog、Yosys 规范化和 formal 链路 |
| EPFL 第二波控制类 | cavlc、dec、priority | 覆盖多输出、深逻辑和重汇聚结构 |
| EPFL 第二波算术类 | adder、max | 覆盖算术逻辑和更大输入输出规模 |

EPFL 固定版本、Verilog/官方 BLIF Git blob SHA、隔离 CEC 和许可义务见 `benchmark_source_and_license_audit.md` 与 `benchmarks/source_manifests/epfl_v2025.1.json`。2026-07-20 已批准 Yosys JSON 作为权威内部格式；第一波正式导入将以 ctrl、int2float、router 为起点实现 JSON importer、case metadata 和 formal 回验。

## 4. Case generation 思路

每个 benchmark 至少生成两类网表：

| 网表 | 生成方式 | 用途 |
|---|---|---|
| original netlist | baseline synthesis script，偏保守优化 | 模拟已有 APR 网表的逻辑结构 |
| resynthesized netlist | aggressive resynthesis script，强调逻辑级数或 delay 改善 | 模拟新约束下的重综合网表 |

候选生成方式：

1. Yosys 统一读入 Verilog/BLIF。
2. ABC 生成不同优化版本，如 `strash; rewrite; refactor; balance; rewrite -z; if -K 6`。
3. 记录每个版本的 gate count、logic level、critical output。
4. 选择 original 中逻辑级数更差的 cone 作为目标区域。
5. 从 resynthesized 中寻找等价或近等价候选 patch。

## 5. 第一轮不做的事情

| 暂不做 | 原因 |
|---|---|
| 一开始接完整 OpenROAD 后端 | 工具链成本高，会拖慢算法验证 |
| 一开始追求真实布局布线增量 ECO | 当前目标是先验证 patch replacement 和 failure-aware refinement |
| 直接复刻旧工业表格 | 数据和代码不可恢复，结论不可复现 |
| 第一版引入 GNN/RL | 复杂度高，不利于中文工程类论文第一版稳定产出 |

## 6. 完成标准

第一批 benchmark 选择视为完成，当满足：

1. Stage A 论文主集至少包含 8 个许可明确的组合逻辑 benchmark。
2. 每个 benchmark 有固定 tag/commit/file hash 和 license/notice 记录。
3. 每个 benchmark 有明确 original/resynthesized 生成脚本。
4. 每个 case 有 `case_schema.md` 中定义的 metadata。
5. 至少能输出 gate count、logic level、patch size、formal equivalence result、runtime。
6. 后续能自然扩展到 Stage B 的 reg-to-reg cone。
