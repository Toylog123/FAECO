# 版本 v8 — 复审四（r10）零算力增强 + 期刊目标改判

| 项 | 值 |
|---|---|
| 提交 | 见 `git log` / 本轮 tag |
| tag | `v2026-10-12-review-r10`（版本 tag）、`faeco-paper-final-20261012b`（论文 tag） |
| 前置 | v7 = 提交 `0602326`，论文 tag `faeco-paper-final-20261012` |
| 触发 | 第三方审稿复审（对 v7 / 作者版 9 页）；用户裁定 **只做零算力项** |
| 论文 `.tex` | `3bb991290c646b5dc27c7d74e03c10fc6fba45d78b52c355e32e2dca2fd50da6` |
| 双副本 PDF 字节 SHA256 | `6f27a08bbf18bc0786ffc76937b8a9ba1e98bfc78eb7868890a3dd479e4cfb49`（2,766,966 B，两处一致） |
| 内容指纹（poppler 25.07） | `96a2070fce0fb319863af678b6dd9a5d35f6871c544f942c791cbe43b563f747` |
| 页数 / 质检 | **10 页** / `Errors 0 · Overfull hbox 0 · Underfull hbox 0 · Overfull vbox 0 · undefined refs 0`，`??` = 0 |
| 逐页行数 | `[52, 68, 65, 74, 35, 60, 67, 68, 72, 52]` |
| manifest | `versions/v8/MANIFEST.sha256` | **117 条**，`sha256sum -c` 全 OK；**相对 v7 仅 3 条变化**（`.tex` + 双副本 `.pdf`），114 条未变 |

## 相对 v7 的改动（diffstat 69 insertions / 5 deletions）

**三项新增表 + 一小节 + 两处文字**：

| # | 内容 | 论文位置 |
|---|---|---|
| 1 | **新增 §3.4 特征设计动机**（`sec:feature_motivation`）：逐项说明式 (2) 的边界 / 尺寸 / 验证 / 扇出 / 深度特征各自对应哪类预布局 ECO 风险；**不引入公式证明**，声明权重取固定值（默认 $1.0$） | §3（原 §3.4 类型化失效归因顺延为 §3.5） |
| 2 | **新增 表 4** `tab:feature_motivation`：加权割特征 ↔ 式 (2) 项 ↔ ECO 风险与设计取向 | §3.4 |
| 3 | §2.2 补整段「**为什么无法直接定量比较**」：结构重映射依赖布局后负载与备用单元布局；逻辑补丁以 SAT/CEC 而非 WNS 为判据；B/G 物理优化（含学习驱动）需训练环境与商用/内部流程 | §2.2 |
| 4 | **新增 表 2** `tab:baseline_cmp`：方法类别 ↔ 直接定量比较的主要障碍 | §2.2 |
| 5 | §4.4 第二组补引导句 + **新增 表 11** `tab:runtime`：族 D 三臂的候选级 STA 次数与端到端运行时间（固定权重 4146 / 2010.8 s；EMA 自适应 4883 / 2065.3 s；随机排序三种子均值 5624 / 2460.3 s） | §4.4 |
| 6 | §5 结论补失效统计句：大部分候选的失败来源于时序收益不足（F4 占候选级评估 **60.2%**），而非功能保持问题 | §5 |
| 7 | 3 处硬编码 `§3.5` → `\S\ref{sec:validation}`（插入 §3.4 后 §3.5 顺延，硬编码会失准） | §1.2 / §4.1 |

**零数字改动 / 零实验改动 / 零代码改动** —— §2 逐数字表全部照旧：8/8、18/19、2/3、1.07、0.16、0.54、0.40、37→126、76/126、0/126、90/126、5/1/2、3363、4044、664、12812、7.57 万 / 15.10 万。

**版面**：9 → **10 页**（3 表 + 1 小节所致）。末页为「结论 + 参考文献」，`\balance` 生效、两栏均衡（**不可删除 `\balance`** —— 实测删后末页右栏只剩 1 条文献）。

## 本轮的两项关键核验（详见 `paper/zh/review_rounds/r10_20261012/response.md`）

1. **审稿人要的 `Random/Pure G/FAECO × [STA 次数, 总运行时间]` 表不可零算力实现**：该三列出自表 9 = **族 C**，而族 C 全部 JSON/日志**不存在任何时间字段**。族 D 虽有运行时间，但**实测不能复现表 9/表 10**（结构化 s27 首次改善 1 vs 30；随机均值 ΔWNS 0.40 vs 0.265），根因是**运行器不同**（`run_hybrid_repair.py` vs `run_outerloop_real_wns.py`）⇒ **硬族边界，禁止并表**；故表 11 采用族 D 独立口径并显式声明不可跨表比较。
2. **STA 计数口径对账**：`n_candidate_sta_runs` == `len(trials)` 即论文口径。§4.3 的 **3363** = 18 电路 3259 + b17 的 180 s 重跑目录 `20260908_phase2_b17_resume/b17`（= **104**，与正文「104 次」自洽）；表 12 的 **4044** = 同一 18 电路 + b17 默认批次（785）。差异纯由 b17 目录选择造成，均可追溯。

## 目标期刊改判

用户裁定 **改投 Integration, the VLSI Journal**（Elsevier，英文），取代原定 JCAD。
审稿人「投稿前必须补」三项中，**runtime 表**与 **baseline 定位**本轮已补；**feature 消融**属需算力项（OI-026）。
**转化待办**：英文稿 + Elsevier 格式与投稿材料（中文稿作为内容母本）。

## 遗留

| 编号 | 内容 |
|---|---|
| OI-026 | 加权割（cost）消融（审稿人「必须补」第 3 项）；用户已表示可投入新算力 |
| — | §七 大规模验证（OpenCores / RISC-V 完整模块 / 工业规模 netlist）；需新基准接入 + 新算力 |
| OI-024 | Word 转排件仍为 v6 版（摘要与三表已过期） |
| OI-025 | 图源 PNG 不在 manifest 覆盖内（117 条口径只含 `.tex` + 双副本 `.pdf` + `code/src` + `code/tests` + 若干 experiments 汇总文件） |
| OI-021 | ⚠ AIGC 披露（JCAD 硬要求；改投 Integration 后需按 Elsevier 政策复核） |
| OI-018 | 1-C 增量 ECO 小节（留修稿轮） |

## 复核命令

```bash
sha256sum -c versions/v8/MANIFEST.sha256                      # 期望：117 条全 OK
cd paper/zh/manuscript && lualatex -interaction=nonstopmode <n>.tex   # ×2
python paper/zh/scripts/checks/latex_quality_gate.py          # Errors/Overfull/Underfull = 0
python scratch/check_env_refs.py                              # 未被引用的表/图：无
python scratch/float_order_probe2.py <pdf> <tex>               # ALL OK: True
pdftotext -layout <pdf> - | sha256sum                          # 内容指纹 96a2070f…
```
