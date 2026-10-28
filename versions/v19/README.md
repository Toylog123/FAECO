# 版本 v19 —— 当前定稿基线（r28 底稿 + r94 判定带口径修订 + r95 §4.1 判定带分解限定，三份稿同口径）

| 项 | 值 |
|---|---|
| 提交 | **`v19 tag 所指提交`**（`git rev-parse v2026-10-28-acceptance-band-caliber-r28^{commit}` 可验；本基线不另记裸 SHA，与 v18 同体例） |
| tag | `v2026-10-28-acceptance-band-caliber-r28`（版本 tag）、`faeco-paper-final-20261028`（论文 tag） |
| 远端 | **尚未推送 origin**（v11–v19 均未上远端，沿用既有做法；等待用户「推送」指令） |
| 前置 | v18 = r20，提交 `73dc0e7`，tag `v2026-10-13-narrative-convergence-r20` / `faeco-paper-final-20261013i` |
| 基线编号 | **v19 对应 r28，不遵循 vN↔r(N+2) 旧约定**——r21–r27 从未单独建基线（`git tag \| grep r2[1-9]` = 0），故本次一次性收口到 r28。此偏差显式登记，后续若回溯 r21–r27 需另立编号，不得占用 v20–v25 |
| 论文中文题 | FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画（未变） |
| 论文英文题 | FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO（未变） |
| 冻结口径 | **三份稿**（v18 只冻结中文主稿）：中文主稿 + 中文补充材料 + 英文稿 |

## 一、三份稿（源）

| 稿别 | 字节 | 行尾 | SHA-256（前 16） |
|---|---|---|---|
| 中文主稿 `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex` | 47,479 | **纯 LF / 485 行 / CRLF=0 / `\r\r\n`=0** | `627b853d27ed3578` |
| 中文补充 `paper/zh/manuscript/FAECO_补充材料.tex` | 52,097 | **纯 LF / 598 行 / CRLF=0** | `9cbc0616d15e5d5b` |
| 英文稿 `paper/en/manuscript/FAECO.tex` | 53,577 | **纯 LF / 457 行 / CRLF=0** | `327987d274f35851` |

> 行尾口径说明：v18 时代 `.tex` 为 CRLF（681 行）；自 r22 起工作区实为**纯 LF**，`.gitattributes` 已对 `paper/zh/manuscript/*.tex` 与 `paper/en/manuscript/FAECO.tex` 锁定 `-text`，检出不会再被 autocrlf 改写。**旧说法「`.tex` 必须纯 CRLF」作废。**

## 二、PDF（双副本 + 单份，均实测）

| 产物 | 字节 | 字节 SHA-256（前 16） | 内容指纹（前 16） | 页数 |
|---|---|---|---|---|
| 中文主稿 PDF（`manuscript/` + `paper/zh/` 双副本，逐字节一致） | 3,003,871 | `a8b62e6691735d37` | `f9a2177074d8b9b4` | **10** |
| 中文补充 PDF（同双副本，逐字节一致） | 601,408 | `1d81111753b8be0b` | `a26800123d8dc4dc` | **9** |
| 英文稿 PDF（`paper/en/build/`，入库副本） | 514,974 | `a14498a78e81808f` | `2c72651da39185e9` | **26** |

- 字节 SHA 含 lualatex 写入的时间戳，**重编必变**；判同一内容请用**内容指纹**（`pdftotext -layout` 的文本层 SHA）。
- 双副本一致性已实测：主稿 OK、补充 OK（`versions/v19/make_manifest.py` 输出）。

## 三、文档结构（实测 grep 计数）

| 稿别 | figure | table | bibitem | section |
|---|---|---|---|---|
| 中文主稿 | 7 | 6 | 14 | 6 |
| 中文补充 | 5 | 12 | 0（沿用主稿 refs） | 6 |
| 英文稿 | 7 | 14 | 0（BibTeX 侧） | 11 |

## 四、manifest

`versions/v19/MANIFEST.sha256` —— **148 条**（v18 为 117），**纯 LF**（148 LF / 0 CRLF）。

相对 v18 同路径比对：

| 类别 | 条数 |
|---|---|
| 同路径hash未变 | 92 |
| hash 变化 | 24 |
| 新增（v18 未覆盖） | 32 |
| v18 有而此处无 | 1（`code/src/rseco/strategy_priority_table.json`，r22 期间移除） |

**口径扩展（相对 v18，其余保持同口径以便逐条对比）**：

1. `code/` 覆盖 `code/src` + `code/tests` 下全部 `.py`/`.md`（排除 `__pycache__`）；v18 为 109 条，本次 135 条。
2. `paper/` 由「中文主稿 tex + 双 PDF」扩到三份稿共 8 个文件（含补充材料 tex/双 PDF、英文 tex/build PDF）。
3. `experiments/` 保持 v18 的 5 条不变。

验证方式：`sha256sum -c versions/v19/MANIFEST.sha256`（须在仓库根执行；manifest 已由 `.gitattributes` 锁 `eol=lf`，防止 `\r` 被当作文件名一部分报错，参见 OI-026）。

本目录另含 `make_manifest.py`（自包含复算脚本，向上两级定位仓库根），重跑会重新生成**逐字节相同**的 MANIFEST（已实测）。该脚本自身不在 148 条之内——它不属于 `code/`、`paper/`、`experiments/` 三类冻结对象。

## 五、本轮冻结的是什么（以及不是什么）

**是**：当前工作区三份稿的**逐字节状态** + 支撑它的代码状态 + 三个 PDF 的编译产物。r94 的判定带口径修订（F-1~F-6 限定句）与 r95 的 §4.1 判定带分解限定均已落在稿内，**未改任何既有数字、未加图、未加表、未加实验**；页数与 r28 底稿相同（10 / 9 / 26）。

**r95 加的是什么**：§4.1 原句「W1 在 8 个电路上均改善，平均为 0.16125 ns」改为先陈述 $\Delta$WNS 均为正，再按**各电路自身**候选级判定带（该电路 2σ，0.024558–0.08474 ns）分解：5/8 电路超带、贡献 89.1%、扣带净额 0.12120 ns，余 3 个低于本电路噪声分辨率不计为可确认改善。读数来自 `project_docs/evidence/r95_band_decomposition_20261028/`，脚本含硬断言（八电路均值必须等于 0.16125 ns 才写结果）。**该带取自 ISCAS89 基族逐电路 `cand_threshold`，不是 ITC-99 扩面族的 0.049752 ns，两族不可互换。**

**不是**：不是新实验的结果登记。r30 物理标签族、判定带 0.049752 ns、五/八个负结论等科学读数**不因本基线而变化**，其口径仍以 `project_docs/CANON.md` 为准。

## 六、已知未决（随本基线一并携带）

1. **r21–r27 无基线**——只有 `paper/zh/review_rounds/r21..r27` 的轮次目录，没有对应 `versions/vN`。若审稿要求追溯某轮中间稿，只能从 review_rounds 取。
2. **`BASELINE_INDEX.csv` 长期停在 v18/r20**——本次更新 active 行到 v19/r28；v19 之前的 9 轮仍为空窗。
3. **末页参考文献孤儿页**（OI-027）——主稿 10 页的最后一页仍只有文献，未处理。
4. **补充材料 `bibitem`=0**——它沿用主稿的参考文献编号，单独送审时须自带文献表。
5. **英文稿缺覆盖优先受控实验**——`paper/en/manuscript/FAECO.tex` 里 `cover`/`W1`/`fig:gain_cost` 均零命中，即「割区 0/8 → 覆盖区 8/8」这条主结果与 0.16125 ns 的读数**未进英文稿**。中文主稿有、英文稿无，三份稿的贡献叙述并不等价；r95 的限定句因此只作用于中文两份。此项待决，不得按「三份同口径」对外表述。

## 七、复现命令

```bash
# 重算全部指纹（只读，不改稿；与本目录 MANIFEST.sha256 逐字节一致，已实测）
python versions/v19/make_manifest.py

# 校验 manifest
sha256sum -c versions/v19/MANIFEST.sha256
```

编译（中文稿）必须 `cwd = paper/zh/manuscript`，因为 `Path=./fonts/` 是相对路径：

```bash
cd paper/zh/manuscript
lualatex -interaction=nonstopmode FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex
lualatex -interaction=nonstopmode FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex
```

**不要**用 `compile.ps1 -Name <中文名>`（PS 5.1 会按 GBK 破坏参数）；**不要**用 `&&` 串联两遍（第一遍 `grep -c` 返回 1 会断链，第二遍静默不跑）。
