# r10（复审四）— 零算力增强 + 期刊目标改判

| 项 | 值 |
|---|---|
| 轮次 | r10 |
| 日期 | 2026-10-12 |
| 触发 | 用户粘贴的第三方审稿意见（对 **v7 / 作者版 9 页**的复审） |
| 用户裁定范围 | **只做零算力项**（`AskUserQuestion`） |
| 运行时间表口径 | **族 D 三臂** |
| 目标期刊 | **改投 Integration, the VLSI Journal**（取代 JCAD） |
| 前置稿 | `manuscript_before.tex` — SHA256 `4539efa45d31a147f47f72443afdd54e05f4e06e1d614dd5615df0c0f9eee3a5`（= v7） |
| 产出稿 | `manuscript_after.tex` — SHA256 `3bb991290c646b5dc27c7d74e03c10fc6fba45d78b52c355e32e2dca2fd50da6` |
| diffstat | **69 insertions / 5 deletions** |

## 本轮落地（5 项，全部零算力）

| # | 内容 | 位置 |
|---|---|---|
| 1 | **新增 §3.4 特征设计动机**（`sec:feature_motivation`）+ **表 4** `tab:feature_motivation`（加权割特征 ↔ ECO 风险对照） | §3 |
| 2 | §2.2 补「为什么无法直接定量比较」整段 + **表 2** `tab:baseline_cmp` | §2 |
| 3 | §4.4 第二组补引导句 + **表 11** `tab:runtime`（族 D 三臂：固定权重 4146/2010.8 s、EMA 自适应 4883/2065.3 s、随机排序均值 5624/2460.3 s） | §4.4 |
| 4 | §5 结论补失效统计句（F4 占候选级评估 60.2%） | §5 |
| 5 | 3 处硬编码 `§3.5` → `\S\ref{sec:validation}`（因插入 §3.4 导致 §3.5 顺延，必须改为交叉引用） | §1.2 / §4.1 |

**零数字改动**：8/8、18/19、2/3、1.07、0.16、0.54、0.40、37→126、76/126、0/126、90/126、5/1/2、3363、4044、664、12812、7.57 万/15.10 万 —— **全部照旧**。
**零实验改动 / 零代码改动**。

## 版面

- 页数 **9 → 10**（新增 3 表 + 1 小节所致）。JCAD 无 8 页硬限；改投 Integration 亦无此限。末页为「结论 + 参考文献」，`\balance` 生效、两栏均衡。
- 质检：`Errors 0 / Overfull hbox 0 / Underfull hbox 0 / Overfull vbox 0 / undefined refs 0`，`??` = 0。
- 表/图引用覆盖 **14/14 + 3/3**；编号阅读顺序 **1..14 / 1..3 全递增**（加固版探针 `scratch/float_order_probe2.py`）。
- 逐页行数：`[52, 68, 65, 74, 35, 60, 67, 68, 72, 52]`。

## 三件套指纹

| 件 | 值 |
|---|---|
| `.tex` SHA256 | `3bb991290c646b5dc27c7d74e03c10fc6fba45d78b52c355e32e2dca2fd50da6` |
| 双副本 PDF 字节 SHA256 | `6f27a08bbf18bc0786ffc76937b8a9ba1e98bfc78eb7868890a3dd479e4cfb49`（2,766,966 B，两处一致） |
| 内容指纹（poppler 25.07，`pdftotext -layout` 原始输出 SHA256） | `96a2070fce0fb319863af678b6dd9a5d35f6871c544f942c791cbe43b563f747` |

## 关键判据文件

- `comments.md` — 复审四要点摘录
- `response.md` — 逐项处置 + 运行时间表不可行性证明 + STA 口径对账 + 版面调平记录
- `table_data.json` — 表 11 全部数字（脚本 `scratch/build_r10_tables.py` 现算）
- `manuscript_before.tex` / `manuscript_after.tex`

## 遗留（转后续轮次）

1. **feature/cost 消融（OI-026）** —— 审稿人「必须补」第 3 项；需改 `code/src/rseco/flow.py:359/385` 加候选源开关 + 单元测试 + 约 40–60 min ISCAS89 算力。用户已表示**可投入新算力**。
2. **大规模验证**（§七）—— OpenCores / RISC-V 完整模块 / 工业规模 netlist；需新基准接入 + 新算力。
3. **Integration 投稿转化** —— 英文稿 + Elsevier 格式与材料。
4. **Word 转排件仍为 v6**（OI-024）；**图源 PNG 不在 manifest**（OI-025）；**加权割消融未做**（OI-026）。
