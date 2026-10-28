# 项目体积盘点与版本对应关系（2026-10-28）

- 审计对象：`D:\BaiduSyncdisk\01_Papers\03_FAECO`
- 方法：只读普查（`scratch/_size_survey.py`、`scratch/_inventory.py`、`scratch/_classify.py`），按扩展名分类聚合 + git 跟踪状态 + 证据清单交叉比对
- 状态：**本轮未删除、未移动、未改动任何文件**
- 前序审计：`project_docs/reports/STORAGE_AUDIT_20261021.md` + `STORAGE_CLEANUP_20261021/README.md`（10-21 已执行一轮清理）

---

## 0. 一分钟结论

| 问题 | 答案 |
|---|---|
| 总体积 | **约 176 GB**（D 盘已用 341.2 GB / 剩余 290.0 GB） |
| 真正的冗余在哪 | **`experiments/` 的 111.6 GB 是 STA 全量路径日志**，真正的结论文件只有 **4.2 GB** |
| 哪些是"当前版本" | 论文 = **r28**（`.tex` `f0f4d5e0…` / PDF `e71feb3d…` / 10 页，2026-10-19 12:55）；版本库最新只到 **v18 = r20（10-13）**，**落后 8 轮** |
| 能删多少 | 零风险档可删 **约 68 GB**；再加"日志提取后删原件"可到 **约 145 GB**，删后约剩 31 GB |
| 最大隐患 | **10-21 做的 NTFS 压缩已失效**（实测压缩率 1.0），且**日志根因未修**（`opensta.py:336`），继续跑实验会再涨 |

---

## 1. 体积真实构成

### 1.1 顶层分布

| 目录 | 逻辑体积 | 文件数 | git 跟踪 | 性质 |
|---|---:|---:|---|---|
| `experiments/` | **150.7 GB** | 533k+ | **不跟踪**（128 个 `2026*` 全被 `.gitignore` 排除） | 实验产出 |
| `scratch/` | **25.4 GB** | 52k+ | **不跟踪**（除 `.gitkeep`） | 临时区 |
| `paper/` | 652 MB | — | 部分跟踪 | 论文源 + 各轮 QA |
| `data/` | 458 MB | — | 部分跟踪 | benchmark 原件 |
| `project_docs/` | 431 MB | — | 跟踪 | 证据包 |
| `.git/` | 287 MB | — | — | 历史对象 |
| `skills/` | 40 MB | — | 跟踪 | |
| `code/` | 7 MB | — | 跟踪 | |
| `versions/` | 1 MB | — | 跟踪 | 18 个冻结版本的 README + MANIFEST |
| `z/` | 0（空目录） | — | 不跟踪 | 残留 |

**结论：96% 的体积在 `experiments/` + `scratch/`，且 100% 不在 git 里 —— 删了无法从 git 恢复。**

### 1.2 按文件类型拆解（决定"能删什么"的关键表）

| 类别 | `experiments/` | `scratch/` | 说明 |
|---|---:|---:|---|
| **日志**（`.log` 等） | **111.6 GB** / 164,318 个 | **10.8 GB** / 16,742 个 | STA 全量违例路径转储，数字可从结果文件重建 |
| **物理中间件**（`.odb/.def/.spef/.v` 等） | 38.3 GB / 226,953 个 | 12.5 GB / 27,064 个 | 可从网表重跑生成 |
| **结果文件**（`.json/.csv/.md/.tsv`） | **4.2 GB** / 15,165 个 | 0.67 GB / 16,873 个 | **结论载体，必须保留** |
| 脚本（`.py/.tcl`） | 82 MB / 154,876 个 | 16 MB | 可保留 |
| 归档（`.7z` 等） | — | 56 MB | |

> **一句话：150.7 GB 里只有 4.2 GB 是结论，111.6 GB 是日志。清理的靶心非常明确。**

### 1.3 单点最大的 10 个目录

| 体积 | 目录 | 构成 | 判定 |
|---:|---|---|---|
| **44.5 GB** | `experiments/20260902_phase2_sentinel` | log 44.2 GB（139 个 ≥100 MB 的 `sta.log`，单个 **320 MB**）/ artifact 282 MB / **result 0** | 10-21 明确"未删（历史 G5 门禁证据）"；但**无任何结果文件** |
| **25.9 GB** | `experiments/20261024_physical_labels_itc99` | artifact 17.9 GB / log 8.1 GB / result 仅 20 MB | 扩面族前身，10-27 还在写 |
| **18.4 GB** | `experiments/20260826_itc99_main` | log 14.2 GB / result **1.86 GB** | 族 B 证据（r22 B3 审计引用）→ result 必留 |
| **16.2 GB** | `scratch/sandbox_r34_rebuild` | artifact 11.3 GB / log 4.9 GB / result 18 MB | **`project_docs/` 0 引用** |
| 7.9 GB | `experiments/20261018_r22_D_revalidate_v1` | log 7.1 GB / result 459 MB | 当前证据 |
| 7.8 GB | `experiments/20260924_threearm` | log 6.8 GB / result 531 MB | 族 D |
| 6.0 GB | `scratch/r22_D_restorecheck_*`（5 个） | 各为整仓副本 | 10-25 凌晨临时件，0 引用 |
| 5.1 GB | `experiments/20261016_r22_cut_ablation_v3` | log 4.8 GB / result 203 MB | 族 C′ |
| 4.8 GB | `experiments/20260926_electrical_3a` | log 4.0 GB / result 394 MB | 族 G（内部诊断，不进论文） |
| 2.7 GB | `experiments/20260806_tcad_pureB_ablation` | log 1.96 GB | 族 C |

---

## 2. 哪些"无关"、能删、能删多少

### 2.1 A 档：零风险（明确临时 / 重复 / 0 引用 / 已被 gitignore）

| # | 对象 | 回收 | 依据 | 风险 |
|---|---|---:|---|---|
| A1 | `paper/zh/manuscript/_review_*`、`_figure_audit_*`、`_mechanism_pages_*` 等共 50+ 个临时目录（405 个 PNG） | **241.6 MB** | 2026-08-11~08-13 论文排版期的**逐页截图审查**残留；`.gitignore` 已写 `paper/zh/manuscript/_*`；git 跟踪 0 个 | 无（历史 PDF 仍在 `review_rounds/`） |
| A2 | `data/raw/benchmarks/raw/epfl_v2025_1_full/.git/`（嵌套第三方 git 仓库） | **130.8 MB** | 第三方 benchmark 的完整 clone 带来的 pack；工作文件本身保留 | 无（丢失该外部仓库 git 历史，可重新 clone） |
| A3 | `scratch/sandbox_r34_rebuild/` | **16.2 GB** | r34 重建沙盒；`project_docs/` **0 命中**；内容为 `20261024_*` 的子集（20,952 文件 vs 32,105） | 无（正式产物在 `experiments/`） |
| A4 | `scratch/r22_D_restorecheck_s641/s713/s820/s832/s953_*`（5 个） | **6.0 GB** | 2026-10-25 凌晨的整仓副本恢复检查；0 引用；10-21 已对同类 11 个做过「归档后删除」 | 低（同类先例已批准） |
| A5 | 全仓 `__pycache__/`、`.pytest_cache/` | <50 MB | 可再生缓存 | 无 |
| A6 | `z/`（空目录） | 0 | 空 | 无 |
| | **A 档合计** | **≈ 22.6 GB** | | |

### 2.2 B 档：日志提取后删原件（收益最大，需一次确认）

| # | 对象 | 回收 | 做法 |
|---|---|---:|---|
| B1 | `experiments/` 全部 `.log`（111.6 GB / 164k 个） | **≈ 111.6 GB** | **不能直接删**。先按族跑一遍提取器：把每个 `sta.log` 的 WNS/TNS/TNS 段、`report_checks` 表头行抽成 `<dir>/log_digest.json`，再删原件；抽样校验"摘要可重建论文数字"后执行 |
| B2 | `scratch/` 全部 `.log`（10.8 GB，含 sandbox 4.9 GB） | **≈ 10.8 GB** | 同上；A3/A4 一并处理则此项自动消掉 |
| B3 | `experiments/20260902_phase2_sentinel` 的 139 个 320 MB `sta.log` | **43.2 GB** | 该目录 **result = 0**，全部科学内容都在日志里 → **必须先提取**（提取后删除，保留 282 MB artifact + 摘要） |
| | **B 档合计** | **≈ 122 GB** | |

### 2.3 C 档：可重跑生成（不建议现在删）

| 对象 | 体积 | 说明 |
|---|---:|---|
| `experiments/` 的 `.odb/.def/.spef` 等物理中间件 | 38.3 GB | 理论上可从网表重跑，但**重跑成本是小时级 EDA**；且部分是一次性快照 |
| `scratch/toolchain/` | 1.24 GB | 工具链二进制（11 个文件），可能是 OSS-CAD/sta，删了要重下 |
| `paper/zh/review_rounds/`（r7–r29，23 轮） | 214 MB | 历史审稿归档，**建议 7z 压缩归档**（可省 ~90%），不建议删 |
| `project_docs/evidence/` | 426 MB | 含 7z 分卷证据包（`r22_D_revalidation` 141 MB 等），**必留** |

### 2.4 必留清单（不要动）

| 对象 | 体积 | 理由 |
|---|---:|---|
| `experiments/*/` 下的 **result 类文件**（json/csv/md/tsv） | **4.2 GB** | 论文每个数字的唯一来源（`PAPER_EVIDENCE_MANIFEST.md` §2 逐数字绑定） |
| `experiments/20260826_aggregation/summary.json` 等聚合件 | 含上 | 摘要三元组 8/8、18/19、2/2 的出处 |
| `project_docs/evidence/` | 426 MB | 证据包 + 论文证据清单 |
| `paper/zh/{*.tex,*.pdf,figures/,fonts/,review_rounds/}` | ~380 MB | 论文本体与图源 |
| `versions/v1–v18/` | 1 MB | 冻结版本（轻量：README + MANIFEST，**成本极低，无删除必要**） |
| `data/raw/benchmarks/`（除嵌套 `.git`） | ~330 MB | benchmark 原件 |
| `.git/` | 287 MB | 历史，不可删 |

---

## 3. 版本对应关系（第二问）

### 3.1 三层"版本"是三个不同的东西，容易混

| 层 | 载体 | 粒度 | 当前指向 |
|---|---|---|---|
| **论文修改轮** | `paper/zh/review_rounds/rN_YYYYMMDD/` | 每轮审稿/改稿 | **r29** 存在（10-19 价值评估）；**交付轮 = r28**；r30/r93/r94 属工程轮，不在 `review_rounds` |
| **冻结版本** | `versions/vN/`（README + MANIFEST.sha256） | 每次打基线 | **v18**；`BASELINE_INDEX.csv` 标 `active` |
| **实验族** | `experiments/<YYYYMMDD>_<name>/` | 每批 EDA 运行 | 128 个，对应论文不同小节 |

### 3.2 `versions/` ↔ 论文轮：**v7 起是 `vN ↔ r(N+2)`**

| 版本 | 基线 ID | 日期 | 对应论文轮 | 状态 |
|---|---|---|---|---|
| v1 | 2026-09-29-submission-ready | 09-29 | — | superseded |
| v2 | 2026-09-30-submission-ready | 09-30 | — | superseded |
| v3 | 2026-09-30-submission-ready-r2 | 09-30 | — | superseded |
| v4 | 2026-10-09-reference-fix | 10-09 | — | superseded |
| v5 | 2026-10-09-abstract-plain | 10-09 | — | superseded |
| v6 | 2026-10-09-text-review | 10-09 | — | superseded |
| **v7** | 2026-10-12-review-r9 | 10-12 | **r9** | superseded |
| v8 | 2026-10-12-review-r10 | 10-12 | r10 | superseded |
| v9 | 2026-10-12-submission-polish-r11 | 10-12 | r11 | superseded |
| v10 | 2026-10-12-pre-submission-consistency-r12 | 10-13 | r12 | superseded |
| v11 | 2026-10-13-abstract-broaden-r13 | 10-13 | r13 | superseded |
| v12 | 2026-10-13-defensive-purge-r14 | 10-13 | r14 | superseded |
| v13 | 2026-10-13-defensive-purge2-r15 | 10-13 | r15 | superseded |
| v14 | 2026-10-13-terminology-calibration-r16 | 10-13 | r16 | superseded |
| v15 | 2026-10-13-logic-calibration-r17 | 10-13 | r17 | superseded |
| v16 | 2026-10-13-fig2-update-r18 | 10-13 | r18 | superseded |
| v17 | 2026-10-13-positioning-r19 | 10-13 | r19 | superseded |
| **v18** | 2026-10-13-narrative-convergence-r20 | 10-13 | **r20** | **active（但已落后 8 轮）** |
| — | **（缺失）** | — | **r21–r28** | **未打基线** |

### 3.3 ⚠️ 发现的版本缺口

**论文实际交付状态**（本轮实测指纹反查）：

| 项 | 值 | 交叉验证 |
|---|---|---|
| `.tex` SHA256 | `f0f4d5e003076e5bb8123f39655ec99e6afa4520823609000e0ade652cf9d57b` | 出现在 `evidence/r28_records_final_20261019/RECEIPT.json`、`handoff_20261019_r28.md` 等 10 处 |
| 主稿 PDF SHA256 | `e71feb3d732c67dc5a2192b4cf7e9cfc110939a840fe79ec74c1ccb90e25cb11` | 双副本一致 |
| 页数 | **10 页** | `pdfinfo` |
| 时间 | 2026-10-19 12:55 | 文件 mtime |

→ 确认当前论文 = **r28 交付版**，但 `versions/` 与 `BASELINE_INDEX.csv` 停在 **r20**。

**后果**：
1. `BASELINE_INDEX.csv` 的 `active` 指向一个已被取代 8 轮的状态；
2. v18 的 `MANIFEST.sha256` 记录 `.tex` 为 `f65929ca…`，**与当前 `f0f4d5e0…` 不一致** → 现在用 `sha256sum -c versions/v18/MANIFEST.sha256` 会大量 FAIL；
3. r21–r28 的改动（含标题/摘要/图表最终态）**没有冻结快照**，只能靠 `review_rounds/r21–r28` + git 历史追溯。

### 3.4 实验族 ↔ 论文小节（哪些实验"有用"）

依据 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md` §0 + §2：

| 族 | 产物目录 | 支撑论文位置 | 判定 |
|---|---|---|---|
| **A** | `20260805_tcad_sprint1_iscas89`、`_itc99` | §4.2 / §4.5 表 7 预布局列 | 必留（result 20 MB） |
| **A\*** | `20260928_sprint1` | §4.2 可复现性限制 | 必留（255 MB） |
| **A′** | `20260807_real_pr_iscas8` | §4.5 表 7 全局布线列（5/1/2） | 必留（43 MB） |
| **A″** | `20260805_parasitic_s382/b18_scan`、`20260805_phys_closure` | §4.6 SPEF 门控 | 必留（2.7 GB，log 占大头） |
| **B** | `20260826_iscas89_main`、`itc99_main`、`picorv32_hetero`、`sec`、`20260908_phase2_b17_resume`、聚合 `20260826_aggregation` | 摘要/§4.3 三元组 8/8、18/19、2/2；SEC 28/29 | **必留**（18 GB 里 result 1.86 GB） |
| **C** | `20260807_multiround_8c_067`、`20260826_ablation_pureG/_pureB/_random_seed*` | §4.4 表 6（1.074 / 0.161 / 0.536 / 0.398） | 必留 |
| **C′** | `20261016_r22_cut_ablation_v3`、`20261018_r22_D_revalidate_v1` | r22 重验证 | 必留 |
| **D** | `20260924_threearm`、`20260924_l2_k1` | §4.4 EMA 无独立贡献 | 必留 |
| **E** | `20260924_l3s_ablation`、`_k4` | **历史族，已被 F 取代** | 可只留 result |
| **F** | `20260928_s_l1_ablation` | §4.6 表 8（S 三层裁决） | 必留 |
| **G** | `20260926_electrical_3a` | **内部诊断，不进论文主张** | 可只留 result |
| **扩面族** | `20261025_physical_labels_itc99_ext`（主池 1393） | **论文 0 命中**（三份 `.tex` 全部 0） | 服务于 r93/r94 分析，非论文证据 |
| 前身 | `20261024_physical_labels`、`20261024_physical_labels_itc99`、`20261024_physical_transfer_noise` | 扩面族构造期 | 结果留、中间件可清 |

**未被任何族/论文引用的**：`20260901_*`（10-21 已删，因其与 0902 逐字节 100% 相同）、`_stale_*`（已删）、`sandbox_r34_rebuild`（A3）。

---

## 4. 根因：为什么清了还会再涨

| 根因 | 现状 | 证据 |
|---|---|---|
| **STA 打印全量违例路径** | **未修** | `code/src/rseco/opensta.py:336`：`report_checks -path_delay max -slack_max 0 -endpoint_count 100000`；单文件实测 **6,641,300 行 / 320 MB / 100,001 个路径段** |
| 调用放大 | — | outer-loop 4 轮 × 每轮数十候选 × 每候选数十门评估 × 每评估 1 次 STA |
| **NTFS 压缩已失效** | **实测压缩率 1.0**（全部未压缩） | 10-21 曾压缩 experiments 省 80.6 GB 磁盘；本轮 `compact /q` 抽查显示 0 个已压缩 → 可能被同步客户端或后续写入撤销 |
| 放在同步盘 | 仍在 `BaiduSyncdisk` 下 | 176 GB 会被同步客户端反复扫描/上传 |

**建议顺序：先修根因 → 再清理 → 最后重新压缩。** 否则清理后跑一轮实验又会长回来。

---

## 5. 建议执行顺序（三档，逐档确认）

| 步骤 | 内容 | 回收 | 风险 | 回退 |
|---|---|---:|---|---|
| **S1** | A 档（A1–A6） | **22.6 GB** | 无 | 无需回退（全是临时/重复） |
| **S2** | B 档：写 `log_digest` 提取器 → 抽样验证 → 删 `experiments/` + `scratch/` 的 `.log` | **≈ 122 GB** | 需先证明摘要可重建数字 | 抽取器产出 `log_digest.json` 入库；原件删前生成 SHA256 清单 |
| **S3** | 修 `opensta.py` 根因（默认 `-endpoint_count` 降到 ~50 或加 `--full-paths` 开关，默认关） | 防止复发 | 改动 STA 报告内容 → 需回归测试 | git 回退；不影响已归档数字 |
| **S4** | 对 `experiments/` 重新开 NTFS 压缩 | 磁盘再省 ~50%（≈ 15–20 GB） | 无（字节不变） | `compact /u` 还原 |
| **S5** | 补 r28 基线：`versions/v19`（MANIFEST 指向当前 `f0f4d5e0…`）+ 更新 `BASELINE_INDEX.csv` 的 `active` 行 | 0 GB | 低（只写文档） | 删除 v19 目录 |

**S1 做完 = 176 → 153 GB；S1+S2 做完 = 约 31 GB；S3 是"不再反弹"的前提。**

---

## 6. 本轮未做的事

- 未删除任何文件（本轮为只读盘点）
- 未修改 `.tex` / `code/` / `.gitignore`
- 未启动 EDA、未做 git 提交
- `wsl.exe` 仍被本机安全策略拉黑（真实 EDA 侧操作受限）
