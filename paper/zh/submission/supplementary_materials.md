# 补充材料清单（T20 产出，2026-09-29）

> 目标：把"审稿人对照代码 / 产物时可能困惑、正文放不下、但证据链需要"的材料集中成册。
> 所有材料均来自仓库既有证据文件，**不新增实验、不改任何已发表数字**。
> 各条目的数字口径必须遵守 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`（铁律：same claim ⇒ same revision + same config family）。

## 建议随稿提交的材料

| # | 材料 | 内容与来源 | 状态 |
|---|------|-----------|------|
| S1 | **失效事件名映射说明** | 产物台账使用旧事件名 `acceptance_budget_violation`，现行代码输出 `F4_timing_gain_insufficient`；两者判定条件一致（`failures.py:47`），语义相同仅字符串不同。来源：OI-008（`project_docs/OPEN_ISSUES.md`）。**这是 OI-008 遗留的投稿前必办项** | 待成文 |
| S2 | **实验族与可复现性说明** | 论文 §4.1/§4.2 已声明实验族划分与"族 A revision 未完整钉定"限制；补充材料给出更完整的族表（族 A/A′/A″/B/C/D/F 的配置、产物目录映射——**只写功能差异命名，不出现仓库内部路径**，路径映射仅存 `PAPER_EVIDENCE_MANIFEST.md`） | 待成文 |
| S3 | **SEC 逐实例结果表** | 30 实例 / 29 修改 / 28+1 说明；`experiments/20260826_sec/summary.csv`（22 行 PASS + `picorv32_regs` N/A）+ b17 phase-2 `sec_result.json`（12812/12813 proven，1 个未证明点 = 同函数尺寸替换）。论文 §4.5 已给汇总，补充材料给逐实例明细 | 待整理 |
| S4 | **复现环境与工具链版本** | Yosys `0.67+146`（主流程 mapping）、OpenSTA `3.1.0`（WSL2）、Yosys `0.33`（WSL，SEC）、SKY130 HD 库；0.5 ns 为统一 stress-test 约束的说明（论文 §4.1 已有，补充材料给版本细节与关键命令骨架） | 待整理 |
| S5 | **基准电路来源与许可** | ISCAS89 / ITC-99 / EPFL / PicoRV32 的来源版本、固定 blob SHA、许可说明（`data/raw/benchmarks/source_manifests/` 有权威清单；论文用 ITC-99 官方 b18/b19，FF 数与官方一致已在审计中核实） | 待整理 |

## 不放入补充材料的（明确排除）

- 任何**未被论文引用**的实验族数字（族 E 历史 S 消融、3-A 电气采集——内部诊断，判 NO SIGNAL，不入论文主张，见 `PAPER_EVIDENCE_MANIFEST.md` §3）。
- `structure_resynth.rejections`（s420）台账——OI-017 未闭合前**禁止任何引用**。
- 未标定的物理门参数扫描细节（OI-015 裁定降级口径已写入正文 §4.6；补充材料不展开）。

## 待用户确认的事项

1. 期刊补充材料形式：JCAD 模板支持**附录**（正文内）；数据/代码可经 **ScienceDB**（https://www.scidb.cn/c/jcadcg ）提交，非强制——是否公开代码/数据属用户决定。
2. S2 中"功能差异命名"的表述粒度（是否列出具体配置开关名）。
3. 是否需要提供代码/数据的公开仓库链接（当前仓库为私有，公开需用户另行决定）。
