# FAECO 路线图：从预布局 ECO 到布局后 SOTA

> **2026-11-11 定稿**。本文是 FAECO 项目的**唯一路线文档**——所有后续实验和论文均按此推进。
> 替代此前 `DIRECTION_RESEARCH_2026-11-10.md` 和 `DIRECTION_UPGRADE_v2_2026-11-11.md`（二者保留作历史溯源）。
>
> **红线**：不改论文冻结数字（r116）、不重开已裁决不可能的门（CANON §8）、不 push、不做纯分析/论述论文。

---

## 0. 三十秒现状（接手者入口）

| 维度 | 现状 |
|---|---|
| 中文论文 | 主稿 11 页 / 补充 15 页，r116，质量门双 PASS |
| 英文论文 | 停 r94 前叙事，1.07/0.16 未同口径，**暂停** |
| 代码 | `placed_sta.py` + `routed_sta.py` 仪器建成，`test_accept_all.py` + `test_postroute_calibration.py` 通过 |
| 测试 | 1094 passed / 7 skipped / 156 subtests |
| 实验 | 六轮预注册实验全部封口（P/E/A6j/K/All/LLM 回放） |
| git | HEAD `fc6ae09`、ahead 39、未 push、worktree clean |
| 环境 | WSL2 Ubuntu, OpenROAD 26Q3, sky130hd, ISCAS89 8 例 + ITC-99 2 例 |
| **本轮方向转折** | 从"预布局改判据"转"布局后覆盖优先 ECO 对标开源 SOTA" |

---

## 1. 为什么转方向

六轮预注册实验的结论：在预布局门级这一设定下，**判据档位、判决精度、动作宽度、按类校准、全盘接受——全部不动端点**。根因是 CANON §7.4「动作粒度 < 测量分辨率」+ placed→signoff 秩相关在跨迭代口径下很弱（Spearman 0.164）。

但**同迭代同基线**的正确口径下，placed→signoff Spearman = **0.70–0.80**（n=10），且存在可预测的系统性偏差（1×:0.40 / 4×:1.01 / B:5.5×）。这意味着：**在布局后设定下，有真实寄生的判据是可靠的，覆盖优先有竞争空间**。

---

## 2. 竞争格局

| 工作 | 时间/发表 | 方法 | 阶段 | 指标 | 开源 |
|---|---|---|---|---|---|
| **E-Layout** (Fang et al.) | **ICCAD 2026** | RL + e-graph + RAG | 布局后 | 6% TNS / 2% WNS 超商业工具 | 否 |
| GoalEvolve (Liu et al.) | 2026.08 | LLM 进化全流程 | 全流程 | TNS +30.67% 超 OpenROAD 默认 | ✅ |
| **OpenROAD resizer** | 持续 | LR | 布局后 | 生产级开源基线 | ✅ |
| Jiang et al. (2402.07781) | 2024 | RL + R-GCN | 布局后 | 延迟-功耗 Pareto | 否 |
| GraPhSyM (Agiza et al.) | ICCAD 2023 | GNN 代理 | 跨阶段 | 98.3% 预测精度 | 否 |

**FAECO 的差异化**：
1. **覆盖优先调度**——文献中无竞品按"覆盖多少失败端点"排候选（E-Layout 的 RL 是全局优化、resizer 的 LR 是灵敏度驱动）
2. **全开源**——E-Layout/Jiang 均未开源，FAECO 是唯一可在 sky130/ISCAS89 上直接复现的 ECO 方法
3. **动作空间更宽**——R（等价改写）+ G（门尺寸）+ B（缓冲插入）+ JOINT（联合动作），resizer 缺 R 和 JOINT

---

## 3. 四阶段路线

### 阶段总览

```
P1: FAECO-P (post-placement)
    └─ 对标 OpenROAD resizer
    └─ 目标：≥5/8 例 WNS 优于 resizer
    └─ 约 3–4 天墙钟（全自动）
    └─ 产出：DAC/ICCAD 短文 或 TCAD 通讯
         │
         ▼
P2: FAECO-P+ML (签核标注训练排序器)
    └─ 替代贪心 max placed_delta
    └─ 目标：≥6/8 例优于 resizer + 跨电路 Spearman ≥0.7
    └─ 约 2–4 周（含数据采集）
    └─ 产出：TCAD 长文
         │
         ▼
P3: Cross-design (跨电路迁移)
    └─ P2 排序器在 held-out 电路族（ITC-99 / OpenCores）上验证
    └─ 目标：性能不退化
    └─ 约 2–4 周
    └─ 产出：DAC 短文 或 TCAD 增刊
         │
         ▼
P4: Multi-objective (Pareto 优化)
    └─ WNS + 面积 + 功耗三目标
    └─ 目标：Pareto 支配 resizer 在 ≥75% 设计点上
    └─ 约 3–6 周
    └─ 产出：TCAD 长文 或 DAC 长文
```

### P1：FAECO-P —— 覆盖优先 vs OpenROAD resizer

> **P1 结果（2026-11-11，已判定 FAIL）**：8 例 ISCAS89 三布局布线后均值，base→resizer **+0.5836 ns**、
> base→FAECO-P **+0.2473 ns**、FAECO-P−resizer **−0.3362 ns**，**0/8 电路更优** ⇒ **不晋级**。
> 主因是动作量（resizer 净增 8/9/13/38 个逻辑单元 vs FAECO-P 0/0/0/1），不是判据精度；
> 详见 `experiments/20261115_p1_resizer_vs_faeco/REPORT.md`、`project_docs/CANON.md` §1 裁定 16。
> **Hybrid 结果（2026-11-11 补记，同样 FAIL）**：同一 resizer 流程、只换起始网表（FAECO-P 终点），
> 三布局均值胜 **5/8**、均值差 **+0.0243 ns**（门槛 +0.05）⇒ 不晋级。
> ⇒ P1 与组合臂一并封口；本路线续做只允许「把 resizer 当内层优化器、我们做预算调度」这类可量化问法，
> 见 `experiments/20261115_p1_resizer_vs_faeco/REPORT.md` §4b、`project_docs/CANON.md` §1 裁定 17。
>
> **P1 之后允许的唯一问法**：可组合性——同一 resizer 流程、只换起始网表（Hybrid 臂），
> 即"我们的 ECO 是否让 resizer 的终点更好"。若也不成立，则本路线需重定题（见 §7 风险表）。


**目标**：证明覆盖优先调度在布局后设定下，可以在 ≥5/8 例 ISCAS89 上取得优于 OpenROAD resizer 的 WNS 改善，且面积不增加。

**设定**：
- 电路：ISCAS89（s27, s382, s420, s641, s713, s820, s832, s953），period 0.5 ns
- 基线：同一 mapped.v 输入，Yosys 0.33 映射
- FAECO-P：`--physical-backend placed_ens --accept-all --enable-buffer --strategies R,G,B --joint-k 2`
- OpenROAD resizer：标准 ORFS 脚本（`repair_timing -setup`），默认参数
- 端点：签核布线后 WNS（`routed_sta.py`，util 0.30/0.35/0.40 三布局均值）

**判定门**：

| 条件 | 结果 |
|---|---|
| **FAECO-P WNS 优于 resizer 在 ≥5/8 例** | ✅ P1 成功 → 写论文、推进 P2 |
| FAECO-P 优于 resizer 在 3–4/8 例 | ⚠️ 临界——查逐例差异，针对性改进（补丁链分析 / 加签核校准） |
| FAECO-P 优于 resizer 在 ≤2/8 例 | ❌ 停线——记录"覆盖优先不比 LR 好"，分析原因 |

**实验步骤**（见 §5 复现命令）：
1. 跑 OpenROAD resizer 在 8 例的 baseline
2. 跑 FAECO-P 在 8 例（`--accept-all`）
3. 两组签核布线后端点对比
4. 逐例补丁链分析（哪些候选被接受？B 类占比？面积变化？）

**论文**：DAC/ICCAD 短文（6 页）或 TCAD 通讯（4–6 页）。
- 核心贡献：覆盖优先——一种全新的 ECO 候选调度策略，在布局后与 LR 竞争
- 基线：OpenROAD resizer（开源）、理想线网贪心（消融）、商业工具数字（引用 E-Layout 的基线）

---

### P2：FAECO-P+ML —— 签核标注训练排序器

**前提**：P1 成功（≥5/8 优于 resizer）。

**目标**：用 P1 产生的签核标注数据训练一个轻量级候选排序器，替代贪心 max placed_delta，进一步提升端点收益。

**方法**：
- 特征：placed_ens WNS 增益 + TNS 增益 + 驱动倍率 + 动作种类（G/B/R/JOINT）+ 候选实例的 fanout/depth
- 标签：签核 routed WNS 增益（同一基线下的配对测量）
- 模型：XGBoost 或轻量 MLP（≤100 参数），避免过拟合
- 训练/测试：在 ISCAS89 8 例上做 leave-one-circuit-out 交叉验证
- 离线回放：用训练好的排序器在 arm E 的 `eval_trials.json` 上选择，与贪心比端点

**判定门**：

| 条件 | 结果 |
|---|---|
| **排序器在 ≥6/8 例上 WNS 优于贪心，且 pooled Spearman ≥0.7** | ✅ P2 成功 |
| 排序器优于贪心但 Spearman 0.5–0.7 | ⚠️ 发消融研究，不推进 P3 |
| 排序器不比贪心好 | ❌ 停线——记录"placed 特征已经饱和" |

**论文**：TCAD 长文（12–14 页）。
- 核心贡献：第一个针对 ECO 候选的签核校准排序器 + 覆盖优先调度的端到端评估
- 消融：贪心 vs 排序器 vs 理想 oracle

---

### P3：Cross-design —— 跨设计迁移

**前提**：P2 成功。

**目标**：验证 P2 的排序器在未见电路族（ITC-99 或 OpenCores）上不退化。

**方法**：
- 在 ISCAS89 上训练排序器
- 在 ITC-99（b01, b03, 以及更大的 b04–b09）上做 held-out 验证
- 如果退化：加入少量 ITC-99 数据做微调（few-shot 迁移）

**论文**：DAC 短文或 TCAD 增刊。

---

### P4：Multi-objective —— Pareto 优化

**前提**：P2/P3 成功。

**目标**：在 WNS + 面积 + 功耗三目标上给出 Pareto 前沿，支配 resizer。

**论文**：TCAD 长文或 DAC 长文。

---

## 4. 不可做的事（防走偏）

以下方向已在 r30–r116 被实验证伪或裁决否决，**不得重启**：

1. ~~用理想线网档做接受判据（缺陷①）~~ → 已证伪
2. ~~用 spef 扇出线载做物理判据（方向 A）~~ → 已证伪（结构缺陷）
3. ~~换判据档位不改奖池（方向 C / r30 LOG-20261025-34）~~ → 决策级未触发
4. ~~只把判决精度提高（arm E）~~ → 46.8% 分歧但不改端点
5. ~~只把动作做大（arm A6j）~~ → 贪心压掉大动作
6. ~~按种类校准判据（arm K）~~ → 常数不可迁移
7. **GNN 打分器**（CANON §8）——池内 AUC 0.479 < kind_only 0.555
8. **自适应时限**（CANON §8）——R² 0.0977
9. **加带 / pin swap / JOINT 加深 / 扩覆盖 8→10000**（CANON §8）

**新增不可做**（本轮方向转折后）：
10. ~~写"为什么是天花板"的纯分析论文~~ → 用户拒绝
11. ~~在预布局理想线网设定下继续改机制~~ → 六轮证伪后封口
12. ~~用 `--physical-gate`（spef.py 扇出线载）做真实物理~~ → 结构上恒低估缓冲

---

## 5. 复现命令（P1 实验）

### 5.1 跑 OpenROAD resizer 基线

```bash
# 需要先对每个电路生成 OpenROAD flow 脚本，再 run
# 具体 Tcl 模板见 data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/
# resizer 在 CTS 之后、route 之前调用
# 然后对 resizer 输出做 routed endpoint 测量（与 FAECO 同一仪器）
```

### 5.2 跑 FAECO-P

```bash
# 在 experiments/ 下建新目录，复用 run_arms.sh 模板
# 核心 flag：
#   --physical-backend placed_ens --placement-utils 0.30,0.35,0.40
#   --accept-all --enable-buffer --strategies R,G,B
#   --joint-k 2 --max-instances 8 --workers 4 --sta-budget 500
```

### 5.3 端点对比

```bash
# 用 routed_sta.py 对每组终态网表做三布局均值测量
# base 读数从 experiments/20261110_placed_gate/endpoint* 复用
```

### 5.4 判定

```bash
# 逐例对比 FAECO-P routed_wns vs resizer routed_wns
# 统计优例数 → 判定 P1 是否通过
```

---

## 6. 文档更新约定

每完成一个阶段（P1–P4），更新以下文档：

| 文档 | 更新内容 |
|---|---|
| `project_docs/LOGS.md` | 追加 `## 2026-11-XX（P1：FAECO-P vs resizer …）` |
| `project_docs/CANON.md` | §1 新增裁定（如裁定 15：P1 结果） |
| `docs/EXPERIENCE.md` | 追加 `## rXXX` 条目 |
| `project_docs/evidence/EXPERIMENT_REGISTRY.md` | 追加实验条目（含预注册 SHA256） |
| `project_docs/HANDOFF_2026-11-09.md` | 标题日更新 + 新增对应 § |
| `.codex-handoff.json` | `next_steps` / `status` / head 更新 |
| 本文件 | 状态更新（阶段完成标记 + 判定结果） |

---

## 7. 风险与缓解

| 风险 | 概率 | 缓解 |
|---|---|---|
| FAECO-P 在所有 8 例上都不如 resizer | 中 | P1 停线，分析 LR 为什么更好，写"覆盖优先 vs LR 在 ISCAS89 上的实证比较"短文 |
| resizer 在 ISCAS89 上 WNS=0（电路太小，resizer 直接修完） | 中 | 增大 period 或换更大的 ITC-99 电路 |
| P1 过但 P2 排序器不优于贪心 | 中 | 说明 placed 特征已饱和，P1 结果本身够 DAC 短文 |
| P2 过但跨设计不迁移 | 高 | 缩小声称——只写"同族有效"，P3 转 few-shot 微调 |