# 版本 v9 — 投稿前精修（标题 / 摘要 / 贡献定位 / 术语与语言风险）

| 项 | 值 |
|---|---|
| 提交 | `e00315a`（v9 双 tag 所指**终态**；链路：`daba5ab` 主稿/台账 → `da61cdf` 指针状态同步 → `e00315a` handoff 补记） |
| tag | `v2026-10-12-submission-polish-r11`（版本 tag）、`faeco-paper-final-20261012c`（论文 tag） |
| 前置 | v8 = 提交 `df7f5ca`，tag `v2026-10-12-review-r10` / `faeco-paper-final-20261012b` |
| 触发 | 用户「投稿前精修」六阶段方案（标题 / 贡献 / 语言 / 定位；**cost 消融暂缓**） |
| 论文中文题 | **FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画** |
| 论文英文题 | **FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO** |
| 论文 `.tex` | `22de39a097101dc0af727b13874f3db51492c6f30fce63c29ce2eb0bd82dc719` |
| 双副本 PDF 字节 SHA256 | `f642e533684bcd0037abd8c9c92bf7a35d107bdb5ee31f6d77c0a6533ae0ea12`（2,769,731 B，两处一致） |
| 内容指纹（poppler 25.07） | `3832eeb2fe5cd7a2ef84c3fbabc7ac2109dd8c5962666ff80bdc12c5e92a5782` |
| 页数 / 质检 | **10 页** / `Errors 0 · Overfull 0 · Underfull 0`（hbox 与 vbox 均无 Overfull/Underfull 行）、`undefined` 5（**全部为字体替身警告**，非引用）、`??` = 0 |
| 引用覆盖 | 表 14 + 图 3 = **17/17 均被正文 `\ref`**（`scratch/check_env_refs.py`） |
| 浮动体顺序 | 表 1..14、图 1..3 严格递增（`scratch/float_order_probe2.py` → ALL OK） |
| manifest | `versions/v9/MANIFEST.sha256` | **117 条**，`sha256sum -c` 全 OK；**相对 v8 恰 3 条变化**（`.tex` + 双副本 `.pdf`），114 条未变；**LF 行尾** |

## 相对 v8 的改动（`.tex` diffstat 23 insertions / 23 deletions；零数字/零实验/零代码）

### 1. 标题（中英同步）
- 中文：`…的结构化候选搜索与失效归因` → `…的候选探索与失效刻画`
- 英文：`Structured Candidate Search and Failure Attribution` → `Candidate Exploration and Failure Characterization`

### 2. 摘要（中英）与关键词
- 中文摘要：`提出结构化候选搜索与失效归因框架` → `提出候选探索与失效刻画框架`；`将候选失效分为六类` → `将候选失效刻画为六类`（**不增字**）。
- 英文摘要：`a framework for structured candidate search and failure attribution` → `a framework for candidate exploration and failure characterization`；`groups candidate failures into six types` → `characterizes candidate failures into six types`；并补 `and a critical-path cover cut`（与中文摘要的"关键路径覆盖割"对齐）。
- 关键词：`类型化失效归因` → `类型化失效刻画`（中/英 `typed failure attribution` → `typed failure characterization`）。

### 3. 贡献重写（§1.3）
| # | v8 | v9 |
|---|---|---|
| 1 | 多特征候选构造与排序：**提出**融合…的多特征加权割… | **候选探索框架**：提出面向预布局门级时序 ECO 的候选探索框架，通过多特征加权割与关键路径覆盖割扩展局部修改空间，并利用候选排序降低验证开销。 |
| 2 | 候选失效分类与搜索控制：将候选失效分为… | **候选失效刻画机制**：建立候选失效刻画机制，将验证失败划分为…（F1--F6），用于分析候选搜索瓶颈并提供参数调整依据。 |
| 3 | 迭代 ECO 与分层验证流程 | **不变** |

**保留的自我限制表述**：贡献 2 仍保留「该机制的定位是**搜索诊断与候选控制**——为下一轮候选构造提供输入，而非独立的收敛增益来源；固定权重与自适应反馈的对照实验支持这一定位。」（防审稿人问"那你的失效机制为什么不涨点"）。贡献 1 仍保留 `1.07 ns / 0.16 ns` 证据句。

### 4. 术语统一
- `结构化归因` → `类型化刻画`（§1.1 三个待量化问题之三）
- `失效归因` → `失效刻画`（§3.2 方法总览 (b)、§3.3 小节标题、结论首句）
- `结构化排序` → `候选排序`（**7 处**：§2.1、§4.4 正文、表 10 表头、表 10 表注、表 11 行、结论、以及表 6 所在段落）
- **终检：全文 `结构化` = 0、`failure attribution`/`失效归因` = 0。**

### 5. 语言风险（3 条）
- §3.4 删防御性断言：「各项特征**并非纯粹的经验权重**，而分别对应…」→「各项特征分别对应…」
- §3.3：「FAECO 的**核心原理**」→「FAECO 的**主要机制**」
- §4.2：「**从机制上看**，JOINT…**能够**同时调整…」→「**在本组接受候选上**，JOINT…**同时调整了**…」（去外推式表述）

### 6. 定位调整与结论收尾
- §2.2 末补：`…使用公开工具链…并以候选级 STA 次数作为可复现的代价度量**；比较重心落在候选空间、候选排序与验证开销三项可在公开工具链上复现的维度**。`
- 结论末句（M4）：删去以"当前 EMA 失效反馈与 S 候选均未取得独立收益"收尾，改为「综上，候选空间与评估顺序是取得时序改善的主要因素（见表~14）。**实验分析进一步揭示了候选排序、验证预算与结构扩展之间的关系，为后续预布局 ECO 搜索策略的设计提供依据。**」（负面结论仍保留在同段前一句，未删证据）

### 7. 文件重命名
主稿 stem 随标题改名：
`FAECO_面向预布局门级时序ECO的候选探索与失效刻画.{tex,pdf}`（`manuscript/` 与 `paper/zh/` 双副本）。
同步更新的**指针**（11 处）：`tools/sync_to_summary.py`(`PDF_STEM`)、`paper/zh/figures/{insert_spef,convert_tables}.py`、`paper/zh/manuscript/{_extract_pages,_render_exp}.py`、`README.md`、`paper/zh/README.md`、`docs/GLOSSARY.md`、`.codex-handoff.json`、`project_docs/agent_handoff/{START_HERE,NEXT_AGENT_PROMPT}.md`。
**未改**（历史记录，保留旧名是正确的）：`versions/v1..v8/`、`paper/zh/CHANGE_LOG.md` 旧行、`project_docs/LOGS.md` 旧行、`agent_handoff/` 旧快照、`paper/zh/submission/`、`paper/zh/review_rounds/`。
**00_Summary**：已同步为新名作者版，并删除旧名文件（同论文只留一份最新）。

## ⚠ 未做（用户明确暂缓 / 后续轮）
- **cost / feature 消融（OI-026）**：用户 2026-10-12 裁定 **暂缓**，不作为当前投稿前置条件；若审稿人要求再加。方案已备于 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：暂缓。
- **OI-028 Integration 英文全文 + `elsarticle` 转排 + 投稿材料**：未做（本轮只改中文稿）。
- **OI-021 AIGC 披露**：须按 **Elsevier** 政策复核。
- **OI-024 Word 转排件**：仍为 v6 版，且现缺**六张**新表 + 新标题/新摘要，须随管线重建（`postprocess.py` 摘要与标题为硬编码）。
- **OI-027 版式**：10 页，用户裁定"等内容定稿再统一排"。

## 验证命令
```bash
cd paper/zh/manuscript
lualatex -interaction=nonstopmode "FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex"   # ×2
cd ../../
python paper/zh/scripts/checks/latex_quality_gate.py      # Errors/Overfull/Underfull 全 0，PAGES=10
python scratch/check_env_refs.py                            # 表/图 \ref 覆盖 17/17
python scratch/float_order_probe2.py "paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.pdf" "paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex"
sha256sum -c versions/v9/MANIFEST.sha256                    # 117 OK
python tools/sync_to_summary.py                             # 00_Summary 同步
```

## 教训
1. **Python 文本模式写文件会引入 CRLF**：`Path.write_text()` 在 Windows 把 `\n` 翻成 `\r\n`，导致 `sha256sum -c` 把 `\r` 当文件名一部分而**全条失败**。凡产出供 `sha256sum -c` 校验的清单，**必须 `open(..., newline="\n")`**。
2. **改标题必须连文件名一起改**，否则 `00_Summary` 的作者版文件名会顶着旧题目；指针文件（脚本常量、README、handoff）须同步，历史记录（`versions/`、`CHANGE_LOG`）**保持旧名才是正确的**。
3. **`sync_to_summary.py` 的构建过期检查按 mtime 判**：编辑 `paper/zh/figures/` 下的**非构建依赖**脚本也会触发 STALE。正确做法是**重新编译**让 PDF 成为最新产物，而不是 `--skip-staleness`。
