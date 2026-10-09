# Current Status

## 2026-10-09 摘要可读性改写轮（本轮最新）

- **用户反馈"摘要太多技术要点、难让大同行看懂"并授权改写**（零数字、零实验、零主张改动，**仅中/英摘要两段**）：① 删 R/G/B/JOINT、F1--F6、多特征加权割、违例扇入锥、SPEF 复测/SEC、纯 G、WNS/TNS 等**未展开机制名与缩写**，改概念化表述；② 首句补"为什么重要"；③ 结果层保留 8/8、18/19、2/3、1.07 vs 0.16 与"无实例退化/尚未达到完全时序收敛"边界；④ 英文摘要同步改写（维持无第一人称）。
- **字数**：中文 **264 字**（原 298，JCAD ≤300）、英文 **148 词**（原 150，≤150）。
- **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；字节 SHA `5c37725a…`（双副本一致）、内容指纹 `0a2b0723…`（poppler 25.07）。
- **重冻结 v5**：tag `v2026-10-09-abstract-plain`（提交 `1c67f50`）+ 论文 tag `faeco-paper-final-20261009b`；`versions/v5/MANIFEST.sha256` 117 条全 OK（相对 v4 变动 3 条）；v4 及更早 superseded。
- **Word 转排稿再重建**：`word/FAECO_投稿Word转排_20261009b.{docx,_Word导出.pdf}`（8 页）；旧 20260930/20261009 两批归档 `word/superseded/`。**正文刻意保留机制名**（摘要给大同行、正文给同行）。

## 2026-10-09 参考文献修复轮

- **用户授权"方案 A"完成一次性参考文献著录层修复**（零数字、零实验、零正文主张改动）：① **P0**——`thebibliography` 按正文首次引用顺序由 19 条重排为 **14 条**（原首处引用渲染 `[1, 7, 9]`，18/19 条错位，违反 JCAD 规范一.1）；② 5 条纯 URL 工具/文档引用（picorv32 / yosys / OpenSTA / skywater-pdk×2）改正文**页脚脚注**（`\footnote{\url{…}}`，JCAD 一.12）；③ P1/P2——`[C] //` 空格（11 条）、`Integration` 全称、BUFFALO 题名补全、kravets 页码 `71:1-71:6`、`[Z]` 类型移出、DOI `_` 转义。
- **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；正文无 `[15]`–`[19]`；字节 SHA `dea21bb3…`（双副本一致）、内容指纹 `6ca972d5…`（poppler 25.07）。
- **重冻结 v4**：tag `v2026-10-09-reference-fix`（提交 `1d01881`）+ 论文 tag `faeco-paper-final-20261009`；`versions/v4/MANIFEST.sha256` 117 条全 OK；`BASELINE_INDEX.csv` v3→superseded / v4→active。
- **Word 转排稿随管线重建**：`word/FAECO_投稿Word转排_20261009.docx` + `…_Word导出.pdf`（8 页），5 条 URL 脚注为 Word 原生脚注（落引用页页脚）；旧 20260930 稿（编号错位）归档 `word/superseded_20260930/`。**未改任何数字/实验/主张**。

## 2026-10-09 文档同步轮

- **论文内容冻结 v3，修改已终止**：tag `v2026-09-30-submission-ready-r2` / `faeco-paper-final-20260930-r2` 均 = `26f4f3b`；9 页 / 0 Error / 0 Overfull / 0 Underfull；内容指纹 `70bbd610…`（poppler 25.07）；`versions/v3/MANIFEST.sha256` 117 条全 OK（实测复核）。**（本状态已被上节 v4 取代。）**
- **本轮仅文档收尾（未动论文、未动代码）**：① 提交 09-30 遗留的 v3 同步批（`5bc0e7d`：LOGS-07 + CURRENT_RUN_HANDOFF v3 节 + T20 锚点 + Word 转排稿重导出）；② 刷新 `START_HERE.md` / `CURRENT_STATUS.md` / `TASK_BOARD.md` / `NEXT_AGENT_PROMPT.md` / `.codex-handoff.json` / T20 包 §0§3 至 v3；③ 登记 Word 转排件字节 SHA256。
- **投稿剩余动作（非论文内容）**：用户 Word 手工项（MathType / 黄色占位 / 图 2 通栏 / 终稿 PDF）+ 检查单 #3 参考文献核对 + ⚠ OI-021 AIGC 披露 + 承诺书/保密审查/英文长摘要。

## 2026-09-30 终审修正轮（v3 冻结；内容修改终止）

- 用户终审 5 处正文一致性修正落地（零数字、零实验）：§3.4 F6 交叉引用纠错（§4.4→§4.5）/ §4.1 接受准则闭合 b06 TNS 辅助接受 / 摘要（中英）PicoRV32 分母解释（**中文 298 字、英文 150 词**）/ 表 8 补 $\Delta L$、$\Delta_{\mathrm{WNS}}$ 符号定义 / §4.5 F6 措辞对齐"启用式反馈"。
- **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）。
- **重冻结 v3**：tag `v2026-09-30-submission-ready-r2`（= `26f4f3b`）+ 论文 tag `faeco-paper-final-20260930-r2`；manifest `versions/v3/MANIFEST.sha256`（117 条）；v2/v1 依次 superseded。**用户明示"改完即停止内容修改、不加任何实验"。**
- **Word 转排稿同步**：摘要串 + 正文 5 处随管线重建，Word 引擎重导出 8 页；`word/转排说明.md` 与 T20 检查单锚点刷新至 v3。

## 2026-09-30 投稿执行轮

- **五项拍板全部落地**：OI-018 1-C 留修稿轮；OI-019 直接转排（询问邮件作废）；OI-020 授权且同步冻结版（**已执行**）；OI-021 AIGC 暂缓（⚠ 投稿时必须解决）；OI-022 维持默认。
- **摘要 JCAD 适配 + 重冻结 v2**：中文摘要 295 字（去"本文"）、英文 149 词；9 页 / 0/0/0；新指纹 `43becd39…`（poppler 25.07）；tag `v2026-09-30-submission-ready` + `faeco-paper-final-20260930`（提交 `4dc16c6`），v1 superseded。
- **Word 转排完成**（`paper/zh/submission/word/`）：docx + Word 引擎导出 PDF + 转排说明。管线 = 引用字面化预处理 → pandoc（OMML 公式）→ python-docx JCAD 版式（题录块/双栏/三线表/上标引文/首页脚注）。**本机 Microsoft Word 实测导出核验通过（8 页，表格/公式/双栏全对）**；LibreOffice 预览的多栏表格伪影是其渲染局限，非文件缺陷。
- **方正字体**：官方免费四款（书宋/仿宋/黑体简体）已经 AUR SHA256 校验后装入本机（用户级）；GBK 版为商业字库，编辑部终排用自有正版，不影响投稿。
- **待用户手工收尾**（见 `word/转排说明.md`）：MathType 批量转换、黄色占位替换（通信作者/基金/日期/简介）、图 2 通栏、终稿导出 PDF。

## 2026-09-30 补充材料成文轮

- **S1–S5 补充材料初稿全部完成**（`paper/zh/submission/supplementary/`）：S1 事件名映射（**OI-008 投稿前必办项闭合**）、S2 族与可复现性（脱敏）、S3 SEC 逐实例（29 PASS + 1 N/A = 30，口径闭合）、S4 环境工具链、S5 基准来源许可。
- **两处过时表述更正**：OI-008"当前代码已无旧事件名"（0a 合并后 `real_wns.py:1864` 仍以旧名写台账，属两层命名分工）；`PAPER_EVIDENCE_MANIFEST` SEC 行"22 行 PASS"（实读 29 行 PASS + 1 N/A）。
- **缺口闭合**：PicoRV32 补建 `data/raw/benchmarks/source_manifests/picorv32.json`（clone HEAD `a473fc8f…`，ISC；三个 modules/*.v 为上游单文件三份相同副本，非导入错误）。
- 论文未动（指纹 `7adf0279…` 不变）；代码未改；`scratch/failure_dist_full.txt` 为本轮探针留痕。

## 2026-09-29 决策轮（上轮）

- **决策落地**：D-01=A / D-02=A / D-03=A 已执行（tag `v2026-09-29-submission-ready` = `d84061a` + manifest 117 条全 OK；OI-003/006/001/002 结案）；T20 目标期刊 = **JCAD**。
- **T20**：`paper/zh/submission/` 投稿包就绪（检查单 + JCAD 要求核实报告 + 官方 2026 Word 模板 + cover letter 草稿 + 补充材料清单 + 询问邮件草稿）。**核心事实：JCAD 无 LaTeX 通道，投稿须 Word+PDF**。
- **RESULTS.md 对齐**：rev. 2026-09-29 修正 3 处 headline（中位数 ISCAS89 +0.10 / ITC-99 +0.18 / PicoRV32 +0.60；ITC-99 严格改善 18/19）+ b06 TNS 辅助接受事实，全部实查自 `summary.json` 与 b06 产物。
- **git**：main = `d84061a`（已 push）；5 个 tag 全部上 origin。论文未动（内容指纹仍 `7adf0279…`）。

## 待用户拍板（OPEN_ISSUES OI-018~OI-022）

1. **OI-018** 1-C（§3 增量小节）插入时机——默认留修稿轮。
2. **OI-019** Word 转排路径——默认先发询问邮件（草稿已备，待确认发送）。
3. **OI-020** 摘要改写授权（JCAD ≤300 字、禁第一人称）。
4. **OI-021** AIGC 披露口径（JCAD 2026 硬要求）。
5. **OI-022** 3 个证据汇总文件是否 `git add`。

## 不要做

- 论文内容修改仍冻结（含摘要）；`experiments/` 证据严禁删除；改 `.tex` 前必读 `PAPER_EVIDENCE_MANIFEST.md`。
- 未跑测试不修改 `code/src/rseco/`；压页先查 `\FloatBarrier`。

## 历史状态（2026-09-14 及以前）

- 见 `agent_handoff/handoff_20260929.md` 与 `WORK_PROGRESS.md`；pytest 基线 264→486+ passed 随 0a/L2/L3 扩展（详见各报告），2026-09-29 轮未跑新测试（未改代码）。
