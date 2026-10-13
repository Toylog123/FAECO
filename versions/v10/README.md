# 版本 v10 — 投稿前一致性 pass（第五份外部审稿 M1–M5）

| 项 | 值 |
|---|---|
| 提交 | （本轮收口提交；tag 见下行） |
| tag | `v2026-10-12-pre-submission-consistency-r12`（版本 tag）、`faeco-paper-final-20261013`（论文 tag） |
| 前置 | v9 = 提交 `e00315a`，tag `v2026-10-12-submission-polish-r11` / `faeco-paper-final-20261012c` |
| 触发 | 用户粘贴的**第五份外部审稿**（「投稿前最后一轮审稿人视角」，对 v9 / 作者版 10 页）；用户裁定 **「不要再加实验。做一次 Submission consistency pass」**（仅 M1–M5） |
| 论文中文题 | **FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画**（与 v9 同，未变） |
| 论文英文题 | **FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO**（与 v9 同，未变） |
| 论文 `.tex` | `c58289992e69521b9c2bcb3827fc5c28d1924eef3f2998b5678f5ea622f8c419`（61,948 B；**668 CRLF / 0 裸 LF**） |
| 双副本 PDF 字节 SHA256 | `4ef380f797a93440c172333f38fbd83a69c5f5d67b7ec8f22330114d172072ac`（2,770,949 B，两处一致） |
| 内容指纹（poppler 25.07） | `c7b4d807701b217e94714254c2ea24684de91bf9057cf0555f4b93547398cc04` |
| 页数 / 质检 | **10 页**（不变） / `Errors 0 · Overfull hbox 0 · Underfull hbox 0 · Overfull vbox 0`、`undefined` 5（**全部为字体替身警告**，非引用）、`??` = 0 |
| 引用覆盖 | 表 14 + 图 3 = **17/17 均被正文 `\ref`**（`scratch/check_env_refs.py`） |
| 浮动体顺序 | 表 1..14、图 1..3 严格递增（`scratch/float_order_probe2.py` → ALL OK） |
| manifest | `versions/v10/MANIFEST.sha256` | **117 条**，`sha256sum -c` 全 OK；**相对 v9 恰 3 条变化**（`.tex` + 双副本 `.pdf`），114 条未变；**LF 行尾** |
| 归档 | `paper/zh/review_rounds/r12_20261013/`（含 `comments.md` / `response.md` / `manuscript_before.tex` / `manuscript_after.tex`） |

## 相对 v9 的改动（`.tex` diffstat **15 insertions / 15 deletions** = 15 处替换；零数字/零实验/零代码）

### M1 · SEC 统计口径统一（表 5）
- **表 5**（`tab:overview`）ITC-99 行的 SEC 列 `\textbf{19/19}` → `18/19`。
- **表注前置一句**：`SEC 列为完全证明的修改网表对数；ITC-99 的 b17 有 1 个等价点未完成证明（见 \S\ref{sec:ood}），故记为 18/19。`
- **依据**：正文自始即为「30 实例 / 29 产生修改 / **28/29** 完全证明」，且拆分式 `8 (ISCAS89) + 18 (ITC-99) + 2 (PicoRV32) = 28` 一直自洽；**表 5 是唯一漏改处**（审稿人猜「表 7」，实为**表 5**）。
- **终检**：渲染 PDF 中 `19/19` 计数 = **0**。

### M2 · PicoRV32 统计与分母解释（5 处）
- 原记法 `2/3` → **`2/2`** + 一句分母解释（「PicoRV32 第三个子模块无 setup 路径，不参与改善判定 / 不计入分母」）。
- 落点：**摘要 CN**、**摘要 EN**、**§4.3**（`\label{sec:ood}`）、**结论**、**表 5** PicoRV32 行。
- **终检**：渲染 PDF 中 `2/3` 计数 = **0**、`2/2` 计数 = **7**。

### M3 · 表 11 预算解释（本轮最重要取证：**两个不同的 STA 计数器**）
| 计数器 | 定义 | 语义 | 受 `--sta-budget 500` 约束？ |
|---|---|---|---|
| `state.budget.sta_used` | `code/src/rseco/search_state.py:254` `reserve_budget`；检查点 `code/src/rseco/flow.py:591` | **每轮迭代**预约一次，到**迭代边界**判顶（`trial_count >= sta_budget → stop_reason = "sta_budget"`） | ✅ **是**，**逐电路** ≤ 500 |
| `n_candidate_sta_runs` | `code/scripts/run_outerloop_real_wns.py:437` = `len(evaluator.trials)` | **候选级 STA 测量次数**（= 论文 §4.4「候选级 STA 次数」口径） | ❌ **否** |

- **逐电路实测（族 D 三臂）**：`sta_used` 最大 **476**（fixed/adaptive）；**random 臂确实触顶**——`random_s1/s420`、`random_s2/s420+s641`、`random_s3/s420+s641` 的 `stop_reason = "sta_budget"`。而论文口径 `n_candidate_sta_runs` 逐电路最高 **1321**。
- ⇒ 表 11 的 8 电路合计（fixed **4146** / adaptive **4883** / random 三种子均值 **5624**）**不受 `500×8` 约束**，**数字无需更正**；缺的只是口径说明。
- **落点**：表 11 表注改写为「三行均采用 20 轮迭代上限、提前停止与**逐电路候选级 STA 预约上限 500**（`--sta-budget`，在迭代边界检查；随机排序臂在 s420 与 s641 上触及该上限）。表中 STA 次数为 8 个电路**候选级 STA 测量次数之和**，与上述预约为**不同计数口径**，故不受 `500×8` 约束」。
- **旁证**：`--sta-budget` 的 CLI help 原文即 "Hard maximum candidate STA **reservations**"，而表 11 数的是 **measurements**。

### M4 · 贡献 1 弱化 `1.07 ns` 与加权割的绑定（§1.3）
- 原句把 `1.07 ns 对 0.16 ns` 紧挂在「多特征加权割 + 关键路径覆盖割」的机制归因上；主实验实际对照的是**候选空间 + 排序**的联合效应。
- 新句：`\textbf{候选探索框架}：提出面向预布局门级时序 ECO 的候选探索框架，通过多类型局部修改候选生成与候选排序扩展搜索空间，并降低候选验证开销。在固定权重、20 轮迭代配置下，混合候选策略相较单一门尺寸调整策略取得更大的平均 WNS 改善（1.07\,ns 对 0.16\,ns）。`
- **保留**贡献 2 的自我限制句（「定位是搜索诊断与候选控制——为下一轮候选构造提供输入，而非独立的收敛增益来源」）。

### M5 · 特征动机措辞降调（§3.4 正文 ×3 + 表 4 行 ×3）
| 位置 | v9 | v10 |
|---|---|---|
| §3.4 边界 | `避免修改跨越局部逻辑闭合边界` | `降低跨越局部逻辑边界候选被优先选择的概率` |
| §3.4 验证 | `降低候选的功能与结构验证成本` | `使搜索倾向于选择验证规模较小的候选` |
| §3.4 扇出 | `避免在扇出较大的节点上引入电气与负载风险` | `以降低引入电气与负载风险的可能` |
| 表 4 边界行 | （原措辞） | `降低跨越局部逻辑边界候选的优先级` |
| 表 4 验证行 | （原措辞） | `倾向选择验证规模较小的候选` |
| 表 4 扇出行 | （原措辞） | `降低高负载节点候选的优先级` |

- **依据**：这些特征只进入式 (2) 的**排序**；硬约束来自**构造级检查**（`cut.py:214` 一带），故「避免 / 保证」属过强主张。

### 另（审稿人「问题 2」）· §4.4 开头补一句
`本节分两组实验。第一组在固定权重及 20 轮迭代预算下比较候选空间与候选评估顺序：` →
`…比较候选空间与候选评估顺序的**联合影响，不单独隔离式~\eqref{eq:cost} 中各特征项的贡献**（特征项属候选生成过程的一部分，其权重在本组固定不变）：`

## 零数字 / 零实验 / 零代码
- `experiments/`、`code/`、`data/` 一字未动。
- 既有数字**全部照旧**：8/8、18/19、1.07、0.16、0.54、0.40、37→126、76/126、0/126、90/126、5/1/2、3363、4044、664、12812、7.57 万/15.10 万、4146/4883/5624、2010.8/2065.3/2460.3 s。
- `19/19 → 18/19` 与 `2/3 → 2/2` 属**口径统一**（正文早已如此），**不是新的数字结论**。

## ⚠ 未做（用户明确暂缓 / 后续轮）
- **cost / feature 消融（OI-026）**：**审稿人本轮再次否决补做**（与 r10 一致），用户裁定**暂缓**，不作为当前投稿前置条件；方案备于 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7（新族 C′ / 新表 / 4–5 h / 允许 NEGATIVE）。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：暂缓。
- **OI-028 Integration 英文全文 + `elsarticle` 转排 + 投稿材料**：未做（本轮只改中文稿）。
- **OI-021 AIGC 披露**：须按 **Elsevier** 政策复核。
- **OI-024 Word 转排件**：仍为 v6 版，且现缺 **r8–r12 全部改动**（含**六张**新表 + 本次 15 处文本改动），须随 `scratch/word_convert/` 管线重建（`postprocess.py` 标题/摘要/关键词为硬编码）。
- **OI-027 版式**：10 页，用户裁定「等内容定稿再统一排」。

## 验证命令
```bash
cd paper/zh/manuscript
lualatex -interaction=nonstopmode "FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex"   # ×2
cd ../../
python paper/zh/scripts/checks/latex_quality_gate.py      # Errors/Overfull/Underfull 全 0，PAGES=10
python scratch/check_env_refs.py                            # 表/图 \ref 覆盖 17/17
python scratch/float_order_probe2.py "paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.pdf" "paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex"
sha256sum -c versions/v10/MANIFEST.sha256                   # 117 OK
python tools/sync_to_summary.py                             # 00_Summary 同步
```

## 教训
1. **「台账里有两个同名概念」是最隐蔽的口径错误来源**：本轮 M3 的表面矛盾（预算 500 vs 4146）并非数字错误，而是**预约计数**（`state.budget.sta_used`，迭代边界判顶）与**测量计数**（`n_candidate_sta_runs` = `len(evaluator.trials)`）两个不同量被读者当成一个。**判据：一个数字若与另一数字"看起来"违反同一约束，先确认两者是否同一计数器**，再决定是改数字还是补说明。
2. **审稿人指出的错误位置可能不准，但错误往往真实存在**：问题 7 审稿人猜「表 7」，实为**表 5**；判据是"用完整拆分式回代"——正文 `8 + 18 + 2 = 28` 一直自洽，**只有表 5 与之矛盾**，据此唯一定位。
3. **口径统一 ≠ 数字改动**：`19/19 → 18/19`、`2/3 → 2/2` 是把唯一漏改的表对齐正文既有口径；记录时须与"新增/修改数字"**明确区分**，否则会污染"零数字改动"声明。
4. **主张强度修正须回代码确认约束来源**：M5 的「避免 ×3」之所以过强，是因为这些特征只进式 (2) 的**排序**，硬约束在**构造级检查**——不能凭语感降调，须指到代码行为。
5. **`.tex` 每次插入块后须重新归一化行尾**：三引号块用 `\n` 会引入裸 LF，须统一回 **CRLF**（本轮终检 668 CRLF / 0 bare LF）。

## 传播性说明（历史文档保留原样）
- `versions/v9/`、`CHANGE_LOG.md` / `LOGS.md` 旧行、`review_rounds/r7..r10/`、`paper/zh/submission/` 中出现的 `19/19` 或 `2/3` 属**该版本的历史记录**，按约定原样保留、不篡改。
- `BASELINE_INDEX.csv`：v9 → `superseded`，v10 → `active`。
