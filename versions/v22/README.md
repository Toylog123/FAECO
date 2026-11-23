# 版本 v22 —— 跨方法横向实测对比与 ASAP7 7 nm 两万门跨工艺扩展基线（2026-11-23）

| 项 | 值 |
|---|---|
| 基线 ID | `v2026-11-23-cross-pdk-lr-baselines` |
| 前置基线 | `v21`（`v2026-11-23-postroute-baselines-b15`，历史参照保持不可变） |
| 当前论文（中文 v3） | `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（15 页，6 套 Nature 矢量图，LuaLaTeX 0 Error / 0 Overfull / 0 Undefined，无孤儿尾页） |
| 英文稿状态 | **暂冻**（按指令先专注中文版本，英文稿保留历史同步点） |

## 本轮新增冻结内容（相对 v21）

1. **通用多工艺库适配器增强**（源码与单测全通过）：
   - `code/src/rseco/logic_rewrite.py` 新增 `parse_generic_liberty_catalog`（支持任意 PDK 未加引号单元头、`area`、`dont_use` 与多 Vt 家族解析）；
   - `code/src/rseco/physical_budget_adapter.py` 扩展 `generate_compatible_candidates` 支持多 `.lib` 目录清单（如 ASAP7 15 库 LVT/RVT/SLVT）与同 Vt 优先平局保持；
   - `code/tests/test_physical_budget_adapter.py` 新增 ASAP7 风格多库单测。
2. **新增证据包** `project_docs/evidence/cross_pdk_lr_baselines_20261123/{REPORT.md, SUMMARY.json}`：
   - **OpenROAD 负裕度门限证伪（`s382`）**：显式负目标松弛裕度与允许 setup 违例开关均返回 `0 Resized`（`+0.0%`）；
   - **Track A：经典冻结寄生 LR 10 电路实测**：5 轮子梯度 LR 表面回收 7.81%–14.14%，经详细重布线 + RCX + 传播 STA 后 **10/10（0% 合格）** 发生 `-79.60 ~ -706.03 ps` Setup 坍塌；
   - **Track B：ASAP7 7 nm `aes_cipher_top`（20,097 实例）**：在 MLCAD26 后布局全局布线口径下（明确与 SKY130 全详细重布线签核区分），OpenROAD 原生仅降 0.118% 且 TNS 恶化 `-2516.01 ps`（`-20.3%`），FAECO 提交 191 处替换回收 **0.266%（原生 2.25×）**、$\Delta\text{WNS}=+0.000\,\text{ps}$、$\Delta\text{TNS}=+48.181\,\text{ps}$（改善）、$\Delta\text{hold}=+0.000\,\text{ps}$、总功耗 `0.432 -> 0.431 W`、Yosys `1252/1252 $equiv` 全证明。
3. **论文矩阵扩充与版面定稿**：
   - 中文 v3 摘要、表 1（8 类工作含 Trident 2.0、OpenPhySyn、RL-Sizer、IR-Aware ECO、GoalEvolve、经典 LR）、§6.3（五方法对照）、§6.5（ASAP7 跨工艺表 14）、§7.3 与 §8 全面对齐，16 页均衡无孤儿尾页，三副本 PDF 一致同步。
