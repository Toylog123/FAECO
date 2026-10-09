# 参考文献核对报告（T20 投稿检查单 #3）

> 日期：2026-10-09
> 对象：`paper/zh/manuscript/FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex` 的 `thebibliography`（19 条）+ 已冻结 PDF（字节 SHA `28647dc0…`，内容指纹 `70bbd610…`）
> 规范依据：JCAD《写作指南｜参考文献规范》 https://www.jcad.cn/news/6 （2023-01-21）+ GB/T 7714
> 性质：**只读核对，未改动任何论文文件**（论文内容处于冻结 v3 状态）。本报告仅列问题与建议，等待授权后再落地。

---

## 0. 结论（TL;DR）

| 级别 | 数量 | 摘要 |
|---|---|---|
| **P0** | 1 | **参考文献编号未按正文首次引用顺序排列**——正文首处引用渲染为 `[1, 7, 9]`，19 条中 18 条编号错位（仅 `ho2010eco` 恰好为 1 正确）。JCAD 规范一.1 硬性要求按出现顺序编号。 |
| **P1** | 5 | `[C]//` 缺空格（11 条）；4 条纯网址类文献处理方式待定 + `[EB/OL]` 缺引用日期；期刊名未写全称（1 条）；题名不完整（1 条）；`[Z]` 类型不在 JCAD 类型表（1 条） |
| **P2** | 4 | 页码 `1-6` 应为 `71:1-71:6`；会议名/出版者细节（3 条）；全条无 DOI；题名标点 |
| **不适用** | 1 | 中文文献双语著录——本稿 19 条**全为英文文献**，无中文文献，该规则不触发 |

**事实性核验**：19 条的作者 / 题名 / 年 / 卷(期) / 页码经 IEEE Xplore、ACM DL、dblp、Semantic Scholar、出版社页面逐条比对，**除 P1-4（题名截断）、P2-1（页码）、P2-2（会议名细节）外全部准确**，无虚构文献。

---

## 1. P0：编号顺序不符合 JCAD 规范一.1

**规范原文**：「各条参考文献应按其在正文中出现的先后用阿拉伯数字连续排序。**注意一定要按在文中出现的顺序编号。**」

**实测**：正文第 123 行首次引用为 `\cite{ho2010eco,liu2021rlsizer,chen2024aito}`，PDF 渲染为 **`[1, 7, 9]`**（第 45 行）；后续依次出现 `[14, 15, 16]`、`[1, 2]`……均非递增。**19 条中 18 条编号错位**（仅 `ho2010eco` 恰为 1）。

**当前 bibitem 顺序 vs 应然顺序（按正文首次引用）**

| # | 键 | 本稿编号 | **应然编号** | 条目 |
|---|---|---|---|---|
| 1 | `ho2010eco` | 1 | **1** ✓ | Ho et al., TCAD 2010 |
| 2 | `kravets2019symbolic` | 2 | **7** ✗ | Kravets et al., DAC 2019 |
| 3 | `jiang2010fraig` | 3 | **8** ✗ | Wu et al., ICCAD 2010 |
| 4 | `jiang2016resource` | 4 | **9** ✗ | Cheng et al., DATE 2016 |
| 5 | `zhuo2018patch` | 5 | **11** ✗ | Dao et al., DAC 2018 |
| 6 | `zhong2024stp` | 6 | **10** ✗ | Pan et al., DATE 2024 |
| 7 | `liu2021rlsizer` | 7 | **2** ✗ | Lu et al., DAC 2021 |
| 8 | `huang2025phys` | 8 | **12** ✗ | Ye et al., TCAD 2025 |
| 9 | `chen2024aito` | 9 | **3** ✗ | Wu et al., Integration 2024 |
| 10 | `zhang2025buffalo` | 10 | **13** ✗ | Hsiao et al., ICCAD 2025 |
| 11 | `yosys` | 11 | **14** ✗ | Wolf（网页） |
| 12 | `liberty` | 12 | **18** ✗ | Synopsys（手册） |
| 13 | `abc` | 13 | **19** ✗ | Brayton & Mishchenko, CAV 2010 |
| 14 | `iscas89` | 14 | **4** ✗ | Brglez et al., ISCAS 1989 |
| 15 | `itc99` | 15 | **5** ✗ | Davidson, ITC 1999 |
| 16 | `picorv32` | 16 | **6** ✗ | Wolf（网页） |
| 17 | `openroad` | 17 | **16** ✗ | Ajayi et al., DAC 2019 |
| 18 | `sky130` | 18 | **17** ✗ | SkyWater（网页） |
| 19 | `opensta` | 19 | **15** ✗ | Parallax（网页） |

**修复方式**（仅重排 `thebibliography` 中 `\bibitem` 行顺序，`\cite` 键不变、正文一字不动）：按上表"应然编号"列的键序重排 19 行 → 重编译 ×2 → 重跑质量门 → 重冻结（v4）→ **Word 转排稿随管线重建**（转排稿的 `[1]–[19]` 由字面化预处理生成，须同批更新）。

**为何此前未发现**：既有机械终检只验"19 bibitem ↔ 19 cite 一一对应"，**未验顺序**。此项属新发现。

---

## 2. P1：格式类问题

### P1-1 会议文献 `[C]//` 缺空格（11 条）
JCAD 模板：`作者. 题名[C]（后面无句号） //会议论文集名称。出版地：出版者，出版年：页码`——即 `[C]` 与 `//` **之间有空格**。本稿 11 条会议文献全部写作 `[C]//`，应改为 `[C] //`。
受影响：`kravets2019symbolic`、`jiang2010fraig`、`jiang2016resource`、`zhuo2018patch`、`zhong2024stp`、`liu2021rlsizer`、`zhang2025buffalo`、`abc`、`iscas89`、`itc99`、`openroad`。

### P1-2 纯网址类文献（4 条）处理方式待定
- 条目：`yosys`、`picorv32`、`sky130`、`opensta`（均为 GitHub / 官网）。
- JCAD 规范一.12：「参考文献若只是表示一些网站的信息，**不能作为参考文献**，应将该网址在正文所在页作为页脚书写（页脚处只写网址，不要其他信息）」。
- 但规范二.11 又允许"电子文档"作参考文献，模板为：`作者. 题名[OL]. [用投稿日期代替]. 获取和访问途径`。
- 本稿现格式为 `[EB/OL]. 出版者, 2024. https://…`，**缺 `[引用日期]`**，与规范二.11 不符。
- **建议**：① 若保留为参考文献 → 按二.11 改写并补投稿日期；② 若从严按一.12 → 移至正文页脚。**建议按 ①处理并保留**（Yosys/OpenSTA/SKY130 是被评估对象，属合理文献），但需知晓编辑部可能援引一.12 要求移页脚。

### P1-3 `[Z]` 类型不在 JCAD 类型表（1 条）
`liberty` 条目：`Synopsys Inc. Liberty User Guide, Version 2016.12[Z]. Mountain View: Synopsys, 2016.`
- JCAD 类型表仅列 M/C/N/J/D/R/S/P + DB/CP/EB + OL/MT/CD/DK，**无 `[Z]`**。用户手册应按规范二.4 标 `[M]`。
- 另：`Liberty User Guide, Version 2016.12` 与出版地 `Mountain View` 无公开可核来源（Synopsys 该文档非公开出版物）。**建议改用可核来源**（如 Liberty 参考手册的官方条目，或与 `sky130` 的 PDK 库文件合并表述），或改为页脚。

### P1-4 期刊名未写全称（1 条）
`chen2024aito`：`Integration, 2024, 98: 102211` → JCAD 规范一.3 要求期刊名**全称**：`Integration, the VLSI Journal`（官方刊名，ISSN 0167-9260）。

### P1-5 题名不完整（1 条）
`zhang2025buffalo`：本稿题名 `BUFFALO: PPA-configurable LLM-based buffer tree generation`；**官方完整题名** `BUFFALO: PPA-Configurable, LLM-based Buffer Tree Generation **via Group Relative Policy Optimization**`（ICCAD 2025，DOI 10.1109/ICCAD66269.2025.11240744）。题名截断属著录错误，须补全。

---

## 3. P2：细节类

| 编号 | 条目 | 本稿 | 应为 |
|---|---|---|---|
| P2-1 | `kravets2019symbolic` | `2019: 1-6` | `2019: 71:1-71:6`（DAC 2019 论文号 71） |
| P2-2 | `zhong2024stp` / `jiang2016resource` | `…Design, Automation & Test in Europe Conference` | `…Design, Automation & Test in Europe Conference & Exhibition (DATE)` |
| P2-3 | `liu2021rlsizer` | `…58th Annual Design Automation Conference. New York: ACM, 2021` | 会议名 `58th ACM/IEEE Design Automation Conference (DAC)`；出版者 **IEEE**（注：本稿写 ACM） |
| P2-4 | `itc99` | `ITC'99 benchmark circuits: preliminary results` | 官方题名 `ITC'99 Benchmark Circuits - Preliminary Results` |
| P2-5 | 全部 19 条 | 无 DOI | JCAD 仅对 `[J/OL]` 强制 DOI/URL；`[J]`、`[C]` 未强制。检查单要求"核对 DOI" → 建议对 8 条期刊/会议条目**可选补 DOI**（已备齐，见附表） |

**可选补 DOI 清单**：
- `ho2010eco` 10.1109/TCAD.2010.2043573
- `kravets2019symbolic` 10.1145/3316781.3317790
- `jiang2010fraig` 10.5555/2133429.2133584
- `jiang2016resource` 10.5555/2971808.2972050
- `zhuo2018patch` 10.1145/3195970.3196039
- `zhong2024stp` 10.23919/DATE58400.2024.10546678
- `liu2021rlsizer` 10.1109/DAC18074.2021.9586138
- `huang2025phys` 10.1109/TCAD.2024.3488577
- `chen2024aito` 10.1016/j.vlsi.2024.102211
- `zhang2025buffalo` 10.1109/ICCAD66269.2025.11240744
- `abc` 10.1007/978-3-642-14295-6_5
- `iscas89` 10.1109/ISCAS.1989.100747
- `itc99` 10.1109/TEST.1999.805857
- `openroad` 10.1145/3316781.3326334

---

## 4. 事实核验明细（逐条，均已比对权威源）

| 键 | 核验结果 | 核验源 |
|---|---|---|
| `ho2010eco` | ✓ 作者 4 人（Ho K H, Chen Y P, Fang J W, Chang Y W），TCAD 29(5): 697-710, 2010 全对 | IEEE Xplore 5452097 / ACM DL |
| `kravets2019symbolic` | 作者/年/会议 ✓；**页码应为 71:1-71:6** | Nian-Ze Lee 主页 / dblp |
| `jiang2010fraig` | ✓ Wu B H, Yang C J, Huang C Y, Jiang J H R；ICCAD 2010: 729-734（标签名 `jiang*` 与作者不符，但键名不可见，不影响著录） | ACM DL 2133429.2133584 |
| `jiang2016resource` | ✓ Cheng A C, Jiang I H R, Jou J Y；DATE 2016: 1036-1041（ACM DL 口径） | ACM DL 2971808.2972050 |
| `zhuo2018patch` | ✓ Dao A Q, Lee N Z, Chen L C, et al.；DAC 2018 Article 51: 1-6 | ACM DL 3195970.3196039 |
| `zhong2024stp` | ✓ Pan H, Zhang R, Xia Y, et al.；DATE 2024: 1-6 | IEEE Xplore 10546678 |
| `liu2021rlsizer` | ✓ Lu Y C, Nath S, Khandelwal V, Lim S K；DAC 2021: 733-738 | ACM DL / NSTL |
| `huang2025phys` | ✓ Ye Y, Xu P, Ren L, et al.；TCAD 44(5): 1901-1914, 2025 | dblp journals/tcad/YeXRCYYS25 |
| `chen2024aito` | ✓ Wu H, Huang Z, Li X, Zhu W；Integration 98: 102211, 2024（期刊名须全称） | ScienceDirect / PlumX |
| `zhang2025buffalo` | 作者/会议/页码 ✓；**题名截断** | IEEE Xplore 11240744 / dblp |
| `yosys` | 作者 Wolf C ✓（Clifford Wolf）；网页类 | — |
| `liberty` | **[Z] 类型 + 来源不可核** | — |
| `abc` | ✓ Brayton R, Mishchenko A；CAV 2010 LNCS 6174: 24-40 | dblp conf/cav/BraytonM10 |
| `iscas89` | ✓ Brglez F, Bryan D, Kozminski K；ISCAS 1989: 1929-1934 | Google Scholar / CVUT 转载 |
| `itc99` | ✓ Davidson S；ITC 1999: 1125-1125 | IEEE Xplore 805857 / dblp |
| `picorv32` | 作者 Wolf C ✓；网页类 | — |
| `openroad` | ✓ Ajayi T, Chhabria V A, Fogaça M, et al.；DAC 2019: 1-4 | ACM DL 3316781.3326334 |
| `sky130` | 机构 SkyWater ✓；网页类 | — |
| `opensta` | 网页类 | — |

---

## 5. 建议处置（需用户授权）

**方案 A（推荐）——统一修 `.tex` 源头，再重冻结**：
1. 重排 `thebibliography` 19 行为应然顺序（P0）；
2. 一并修 P1-1 ~ P1-5、P2-1 ~ P2-4（纯著录格式，不触碰正文与数字）；
3. 重编译 ×2 → 质量门 → 双副本 → 重冻结 **v4**；
4. **Word 转排稿随管线重建**（引用字面化编号同步更新）。

**方案 B——仅在 Word 转排稿侧修正**：不动 `.tex`，在转排管线中重排与原位替换。缺点：LaTeX 冻结版与投稿版不一致，溯源割裂。

**说明**：以上改动**全部属参考文献著录层**，不涉及正文、公式、数字、结论；但因触及冻结文件，按冻结令须先取得用户授权。**建议采用方案 A**。

---

## 6. 未决 / 待确认

1. `[EB/OL]` 4 条是否保留为参考文献（P1-2），还是按 JCAD 一.12 移页脚——取决于编辑部尺度。
2. `liberty` 条目来源（P1-3）——是否可换成可核来源或并入 `sky130`。
3. 是否补 DOI（P2-5，可选）。
4. 另注：本稿 19 条**未引用《计算机辅助设计与图形学学报》本刊文献**（非硬性要求，供参考）。
