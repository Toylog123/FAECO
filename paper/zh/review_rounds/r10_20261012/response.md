# 复审四（r10）— 处置与真伪核验

用户裁定范围：**只做零算力项**（`AskUserQuestion` 2026-10-12）。运行时间表口径：**族 D 三臂**。目标期刊：**改投 Integration, the VLSI Journal**。
本轮**未动任何实验、未改任何既有数字**；`.tex` diffstat = **69 insertions / 5 deletions**。

---

## 一、逐项处置

| # | 审稿人项 | 判定 | 处置 |
|---|---|---|---|
| 1 | §三 Feature design motivation 小节（feature ↔ ECO 风险对照表） | ✅ **零算力** | **已做** — 新增 **§3.4 特征设计动机**（`sec:feature_motivation`）+ **表 4**（`tab:feature_motivation`）。逐项对应式 (2) 的边界/尺寸/验证/扇出/深度五项；不引入公式证明。 |
| 2 | §五 运行时间表 | ⚠️ **只能部分做** | **已做（换口径）** — 新增 **表 11**（`tab:runtime`），口径为**族 D 三臂**：固定权重 4146 次/2010.8 s、EMA 自适应 4883 次/2065.3 s、随机排序三种子均值 5624 次/2460.3 s。**审稿人要的 Random/Pure G/FAECO 三元组不可零算力实现**（见 §二）。 |
| 3 | §六 baseline 定位 + qualitative comparison table | ✅ **零算力** | **已做** — §2.2 补「为什么无法直接比较」整段（spare cell 依赖布局信息 / 逻辑补丁以 SAT·CEC 为判据 / RL sizing 需训练环境 + 商用流程不可复现），并新增 **表 2**（`tab:baseline_cmp`）。原有 `tab:related_diff`（表 1）保留。 |
| 4 | §七 大规模验证 | ❌ **需新算力** | **本轮未做**（用户本轮范围 = 零算力）。用户随后表示**可投入新算力** → 另列待办。 |
| 5 | §八 结论补失效统计句 | ✅ **零算力** | **已做** — §5 结论补「失效统计显示，大部分候选的失败来源于时序收益不足（F4 占候选级评估的 60.2\%），而非功能保持问题」。数字与表 12 一致。 |
| 6 | §九 期刊定位 | — | **用户裁定：改投 Integration, the VLSI Journal**（见 §四）。 |

---

## 二、运行时间表：为什么不能照审稿人的表做（核心核验）

审稿人要 `方法 \| STA 次数 \| 总运行时间(s)`，方法列 = **Random / Pure G / FAECO**。这三列出自 **表 9**（`tab:ablation`）= **族 C**（`20260807_multiround_8c_067` + `20260826_ablation_{pureG,pureB,random_seed1..3}`）。

**穷举核验结果（探针 `scratch/probe_runtime_fields.py`）：族 C 全部目录的 JSON 中不存在任何时间类键**
（键集合为 `period_ns/circuit/rounds/candidate_trials/rounds_history/random_order/seed/baseline_wns/final_wns/improvement/netlist_audit`）。
族 C 的 `.log` 亦无 `elapsed|took|seconds|runtime|wall` 任何匹配。⇒ **表 9 的运行时间列在冻结 revision 下不可恢复。**
族 C 的可复现性另有既有结论（OI-012）：`20260826_ablation_*` **顶层运行脚本 0 个**、调用命令未归档。

各证据族的运行时间可得性：

| 族 | 论文主张 | 运行时间字段 |
|---|---|---|
| A | §4.2 效率优先（图 2） | **无** |
| B | §4.3 跨测试集主实验 | **有**（ISCAS89 8 电路 = 357 次 / 455.4 s；ITC-99 `summary.json` `elapsed_sec` = 8658.4 s、2 路并行 ≈ 2.41 h） |
| **C** | **§4.4 第一组（纯G/纯B/随机/混合20轮）= 表 9/表 10** | **无** |
| D | §4.4 第二组（fixed/adaptive/random 三臂） | **有**（2010.8 ~ 2494.8 s） |

### 关键否证：族 D **不能**充当表 9/表 10 的数据

族 D（`20260924_threearm`）的 `random_s1/s2/s3` 带 `--random-order`（`random_order: true`），表面上正好可给「结构化 vs 随机」补运行时间。**实测复现失败**（探针 `scratch/probe_famD_repro.py`）：

| 对照项 | 表 9 / 表 10（族 C） | 族 D |
|---|---|---|
| 结构化排序 s27 首次改善 | 1 | **30** |
| 随机列均值 ΔWNS | 0.40 | **0.265** |
| 混合 20 轮均值 ΔWNS | 1.07 | fixed **0.285** |

根因：**运行器不同** —— 表 9 四列出白 `code/scripts/run_hybrid_repair.py`（OI-012 已证），族 D 出自 `code/scripts/run_outerloop_real_wns.py`（`run_config.json` 的 `argv` 可查），且 `git_head` 不同（族 D = `main @ 6276cff`）。
⇒ **两者为硬族边界，禁止并表**。故表 11 采用「族 D 三臂」独立口径，并在表注显式声明「与表 9、表 10 出自不同运行配置，其 STA 计数不与表 10 的首次改善位置口径对应」。

### 旁证：r9 的 k₁st 纠错方向正确

族 D 报告 `reports/FAECO_L2_THREEARM_20260924.md` 第 54 行原文为
「随机排序普遍使 k₁st 恶化 1--2 个数量级（s641: 1→123；s713: 5→216；s953: 1→185）」，
与 **v6 版 §4.4 原句**的 `s713 5→216、s953 1→185` 完全一致 ⇒ 证明 v6 原句确实取自族 D，而 r9 将其改为同族（族 C）三种子口径是正确处置。

---

## 三、STA 次数口径对账（出表前钉死）

论文既有两个数：§4.3「19 个电路共 **3363** 次候选级 STA 测量」、表 12 表注「19 个电路、**4044** 次候选级评估」。
探针 `scratch/reconcile_sta_counts.py` 对账结果：

- `n_candidate_sta_runs` **==** `len(trials)`（族 B ITC-99 合计 = 4044）⇒ **这就是论文的 STA 计数口径**。
- **3363 = 18 个电路合计 3259 + b17 的 180 s 重跑目录 `20260908_phase2_b17_resume/b17`（`n_candidate_sta_runs` = 104）**。
  该 104 与 §4.3 正文「在 104 次候选级 STA 测量内取得 +0.38 ns 改善」自洽。
- **4044 = 同一 18 个电路 3259 + b17 默认批次（785）**。
- 两者差异**纯由 b17 目录选择造成**，均可追溯；`state.budget.sta_runs`（3401）**不是**论文口径，已弃用。

⇒ 表 11 使用与论文同一计数器（`n_candidate_sta_runs`），族 D 得 4146 / 4883 / 5624。

---

## 四、期刊目标

用户裁定：**改投 Integration, the VLSI Journal**（Elsevier，英文刊），取代原定 JCAD。
**影响（尚未执行，另列待办）**：需英文稿 + Elsevier 格式与投稿材料；现有中文稿（ctexart / lualatex）作为内容母本。
审稿人给出的投稿前必补三项中，**runtime 表与 baseline 定位本轮已补**；**feature 消融**属需算力项。

---

## 五、执行记录（as executed）

```
scratch/probe_runtime_fields.py      # 证明族 C 无任何时间字段
scratch/probe_runtime_data.py        # 族 B/D 运行时间汇总
scratch/probe_famD_ordering.py       # 族 D 排序复现第一次尝试
scratch/probe_famD_repro.py          # 族 D vs 表 9/表 10 的关键否证
scratch/probe_runtime_all_families.py# 全族运行时间可得性清单
scratch/reconcile_sta_counts.py      # 3363/4044 口径对账
scratch/build_r10_tables.py          # 生成表 11 → r10_20261012/table_data.json
scratch/probe_r10_anchors.py         # 锚点唯一性预检（§3.5 出现 3 次，跨 2 行）
scratch/apply_r10_review.py          # 7 处精确匹配替换
scratch/fix_r10_eol.py               # 归一化为纯 CRLF（插入块曾引入 60 处裸 LF）
scratch/float_order_probe2.py        # 加固版浮动体顺序探针（按 .tex caption 反查）
```

编译与质检：`lualatex ×2` → `Errors 0 / Overfull hbox 0 / Underfull hbox 0 / Overfull vbox 0 / undefined refs 0`；
`??` = 0；**未被引用的表/图: 无**（14 表 + 3 图全覆盖）；表/图编号阅读顺序 **1..14 / 1..3 全递增**。

### 版面调平记录（Overfull 归零过程）

1. 首次编译出现 `Overfull \hbox (13.70378pt)` 于表 4「深度」行 —— 不可断行的 `$\lambda_c\,\mathrm{depth}/\mathrm{depth}_{\max}$` 撑破 `p{2.0cm}`。**改列宽 1.5/2.0/3.4 → 1.3/2.6/3.0 cm**，hbox 归零。
2. 余 `Overfull \vbox (0.95665pt)` —— 定位为 **`\balance` 末页（第 10 页）分栏溢出**：
   - 试 `\linespread{0.95→0.94}` → **恶化**（1.55127pt）⇒ 行距不是正确杠杆，回退。
   - 试临时注释 `\balance` → 全绿，但末页右栏只剩 `[14]` 一条文献（**这正是 `\balance` 要防的缺陷**）⇒ **必须保留 `\balance`**。
   - 最终：删除**表 14 表注中与正文重复的一句**「扩大候选池仅作用于窗口来源侧，不改变接受谓词与验证流程。」（释放 1 行）→ **全绿**。
