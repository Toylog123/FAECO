# FAECO on Top of OpenROAD Resizer: 面积恢复实验设计

> **2026-11-12 定案**。基于用户决策「在 resizer 之上做工作」。

## 核心想法

OpenROAD 的 `repair_timing -setup` 是已知最强的开源 post-placement gate sizing 工具（我们实测 +0.58 ns WNS，8/8 胜 FAECO-P）。但它的问题是没有面积概念——它全盘放大所有关键路径上的门，导致 **+42% 面积**。

FAECO 不做「另一个 resizer 的竞争对手」，而是做 **「resizer 之后的选择性面积恢复」**：
1. 让 resizer 先跑 → 得到最好的 WNS
2. FAECO 检查 resizer 的每一个改动 → 哪些是必要的，哪些是可以回退的
3. 回退不必要的改动 → 面积恢复，WNS 保持在目标范围内

这跟「覆盖优先」一脉相承：覆盖优先的本质是**只改最小的必要集合**。

## 实验臂

| 臂 | 输入 | 操作 | 输出 |
|----|------|------|------|
| **R** | `mapped.v` (W1 基线) | `repair_timing -setup` 一次 | `routed.v`（最大 WNS，最大面积） |
| **FR** (FAECO Recovery) | R 的 `routed.v` | FAECO 回退不必要的改动 | `routed_recovered.v`（接近 R 的 WNS，更小面积） |

## FR 臂操作细节

1. 从 R 的 `routed.v` 出发，与 `mapped.v` 比对 → 找到所有被 resizer 改动的 cell
2. 对每个改动的 cell，生成「回退候选」（revert to baseline cell type）
3. 用 FAECO 的 placed_ens 评估每个回退候选对 WNS 的影响
4. 按 WNS 影响升序（影响最小的先回退）
5. 逐个回退，每个回退后重测 WNS
6. 当累计 WNS 退化达到阈值（例如 0.02 ns = 噪声底）时停止

## 预计效果

假设 resizer 在 s382 上的 +203 area units 中，只有 ~40% 真正影响 WNS：
- 回退 60% 的改动 → 面积从 612 降到 ~490（vs 基线 409，+19.8%）
- WNS 从 −0.8414 退化到 ~−0.86（退化 0.02 ns）
- 最终结果：WNS −0.86 / 面积 +19.8%（vs 纯 resizer 的 −0.84 / +49.6%）
- **面积效率提升约 2.5×**

## 实验规模
- **Pilot（3 例）**：s382、s641、s832（小/中/大）
- **扩展（8 例）**：若 pilot 面积恢复 ≥20% 且 WNS 退化 ≤0.05 ns

## 论文定位
- **不是在跟 resizer 竞赛**——而是在扩展 resizer 的能力
- **覆盖优先应用于不同阶段**：不再用于「从零构造 ECO」，而是「从 brute-force 输出中选择必要改动」
- **与文献的关系**：所有 gate sizing 论文都是从头做优化，没有一篇做 post-optimizer recovery