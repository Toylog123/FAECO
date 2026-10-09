# Work Progress

本文件按**倒序**记录每一轮工作（最新在上）。完整正序日志见 `LOGS.md`。

## 2026-10-09 文档同步轮：v3 交接文档对齐 + Word 件哈希登记

- **做了什么**：① 提交 09-30 遗留的 v3 同步批（`5bc0e7d`：LOGS-07 + CURRENT_RUN_HANDOFF v3 节 + T20 锚点 + Word 转排稿随管线重导出）；② 实测复核冻结完好——`versions/v3/MANIFEST.sha256` 117/117 OK、PDF 双副本字节 SHA `28647dc0…`、内容指纹 `70bbd610…`（poppler 25.07）、v3 双 tag 经 `^{commit}` 解析均 = `26f4f3b`；③ 刷新 `START_HERE.md`（HEAD/指纹/tag 由 09-29 旧值 → v3）、`CURRENT_STATUS.md`（补本轮 + 09-30 终审轮）、`TASK_BOARD.md`（T20 行 → v3）、`NEXT_AGENT_PROMPT.md`（v2 → v3）、`.codex-handoff.json`（全字段刷新）、T20 包 §0/§3；④ 登记 Word 转排件字节 SHA256 到 T20 包 §3。
- **关键结果**：main = `5bc0e7d`（论文 v3 tag 仍 = `26f4f3b`）；**未动论文内容、未动代码**；文档与仓库实态对齐。
- **下一步**：投稿手工/流程项 —— 用户 Word 手工收尾（MathType/占位/图 2 通栏/终稿 PDF）、检查单 #3 参考文献核对、⚠ OI-021 AIGC 披露、承诺书/保密审查/英文长摘要。

## 2026-09-30 终审修正轮：5 处正文修正 + 重冻结 v3（内容修改终止）

- **做了什么**：用户终审确认前 4 项已改对，提出最后 5 处正文一致性修正（零数字、零实验）：§3.4 F6 交叉引用纠错（§4.4→§4.5）/ §4.1 接受准则闭合 b06 TNS 辅助接受例外 / 摘要（中英）PicoRV32 分母解释（`picorv32_regs` 无 setup path 不参与判定；中文 298 字、英文 150 词）/ 表 8 补 $\Delta L$、$\Delta_{\mathrm{WNS}}$ 符号定义 / §4.5 F6 措辞对齐"启用式反馈"。Word 转排稿随管线同步重建，Word 引擎重导出 8 页。
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）、内容指纹 `70bbd610…`；**重冻结 v3**（tag `v2026-09-30-submission-ready-r2` = `26f4f3b` + 论文 tag `faeco-paper-final-20260930-r2`，manifest `versions/v3`，117 条；v2/v1 superseded）。**用户明示"改完即停止内容修改、不加任何实验"。**

## 2026-09-30 投稿执行轮：五项拍板落地 + 摘要适配重冻结 v2 + Word 转排完成

- **做了什么**：① 用户拍板 OI-018~022（1-C 留修稿轮 / 直接转排 / 摘要授权且同步冻结版 / AIGC 暂缓 / 维持 manifest 默认）；② OI-020 执行——中英摘要按 JCAD 规则改写（295 字 / 149 词，去第一人称），其余正文零改动；**重冻结 v2**（tag `v2026-09-30-submission-ready` = `4dc16c6`）；③ OI-019 执行——Word 转排三件套（`paper/zh/submission/word/`：docx + Word 引擎导出 PDF + 转排说明），管线 = 引用字面化预处理 → pandoc（OMML）→ python-docx JCAD 版式；**本机 Microsoft Word 实测 8 页全对**；④ 方正免费字体四款经 AUR SHA256 校验装为用户级字体。
- **关键结果**：论文未动（v1/v2 冻结版与既有 manifest 未变）；Word 转排件为可溯源新制品（哈希见 T20 包 §3）。

## 2026-09-30 补充材料成文轮：S1–S5 全部初稿完成

- **做了什么**：`paper/zh/submission/supplementary/` 成文 S1（失效事件名映射，**闭合 OI-008 投稿前必办项**）/ S2（实验族与可复现性，脱敏）/ S3（SEC 逐实例，29 PASS + 1 N/A = 30）/ S4（环境工具链）/ S5（基准来源许可）；更正两处过时表述（OI-008 两层命名分工、manifest SEC 行 22→29+1）；补建 PicoRV32 source manifest。
- **关键结果**：论文未动（内容指纹仍 `7adf0279…`）；代码未改；S1–S5 初稿待用户确认。

## 2026-09-29 决策轮：D-01~D-03 落地 + RESULTS.md 对齐 + T20 启动

- **做了什么**：① 用户拍板 D-01=A / D-02=A / D-03=A，T20 目标期刊=JCAD；② D-01 落地——`versions/v1` 轻量冻结（manifest 117 条全 OK 自校验 + tag `v2026-09-29-submission-ready` = `d84061a`，已 push），并实测发现 3 个论文数字源证据文件（`20260826_aggregation/summary.json` 等）此前未被 git 跟踪，现由 manifest 锁定；③ D-02/D-03 台账结案（OPEN_ISSUES「已决」表 + 决策简报注记）；④ `experiments/RESULTS.md` 对齐论文终稿口径——实查修正 ISCAS89/ITC-99/PicoRV32 中位数（+0.10/+0.18/+0.60）与 ITC-99 success 口径（18/19 严格改善），b06 补 TNS 辅助接受事实；⑤ T20 投稿包骨架落 `paper/zh/submission/`（检查单 + cover letter 草稿 + 补充材料清单），JCAD 官方要求调研进行中；⑥ 1-C 评估完毕：代码侧已实现并过 gate，剩余动作是论文插入小节，与内容冻结冲突，待用户拍板。
- **关键结果**：main = `d84061a` + 4 个 tag 上 origin；论文未动（仍 9 页冻结版，内容指纹 `7adf0279…`）；RESULTS.md 三处数字错误已修正并与 `summary.json` 对账一致。
- **下一步**：JCAD 调研回填检查单 → S1–S5 补充材料成文 → 用户决定 1-C（插入论文 / 留到修稿轮）。

## 2026-09-29 论文终稿收敛 + 仓库收敛 + 版面收尾（详见 `agent_handoff/handoff_20260929.md`）

- **做了什么**：终稿审稿三批修改（评审 15 项优先 7 项 `681841a`、第二轮 10 项 `0ea80b6`、必改 4 项 `a8142b6`）；版面两次修复回 9 页（根因均为双栏下 `\FloatBarrier` 退化 `\clearpage`）；删除 81 个历史 `.tex` 与 82 个历史 PDF（删前均先入库固化）；发布冻结 tag `faeco-paper-final-20260929`，机械终检全过（0 `??`、29 label 唯一、19 bibitem ↔ 19 cite）。**用户明确要求停止论文内容修改。**
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull；PDF 字节 SHA256 `9af41d77…`（双副本一致）、内容指纹 `7adf0279…`。

## 2026-09-14 交接整理收尾

- **做了什么**：核查交接文档体系，发现并补齐三处缺口：上轮交接文档变更未提交（本轮 commit+push）、`NEXT_AGENT_PROMPT.md` 为空模板（已补全：目标=D-01~D-03 落地 + T20、约束、证据门）、`.codex-handoff.json` 时间戳过期（已刷新，read_order 补入决策简报）；核查 versions/v1/ 为模板占位（与待 D-01 决策一致）。
- **关键结果**：pytest 264 passed + 4 skipped（环境验证通过）；全套交接文档提交推送，仓库随时可无口头交接。
- **下一步**：不变——用户拍板 D-01~D-03 → 执行决策 → T20 投稿件打包。

## 2026-09-12（下午）决策简报 + 交接收尾

- **做了什么**：为 OPEN_ISSUES 中三项待决策事项（versions/v1 冻结、机制图、DOI/DRC）核实最新事实并编写决策简报 `agent_handoff/DECISION_BRIEF_20260912.md`；刷新 OPEN_ISSUES（OI-001 降级：主稿无 DOI 占位符；OI-006 重定义：当前 9 页稿仅 3 图，原拆分问题已消失；新增 OI-007 hold limitation 记录）与 TASK_BOARD（U26-06/U26-08 关闭、U26-07 部分完成、新增 D-01~D-03 决策项与 T20 投稿打包任务）；重建全套交接文档。
- **关键结果**：三项决策均有明确建议（轻量冻结 / 维持 3 图 / 维持如实声明+按需 rebuttal），用户拍板后下一轮即可执行。
- **下一步**：用户读简报做 D-01~D-03 决策 → 执行（tag+manifest / 无动作 / 关闭对应 OI）→ T20 投稿件打包。

## 2026-09-12 框架架构迁移 + 环境重建 + 旧副本清理

- **做了什么**：robocopy 全量复制仓库（316,765 文件 / 117.7 GB / 0 失败）至 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，git 历史与远程保留；按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）；路径修复（pyproject、12+ 硬编码脚本、19+12 测试锚点）；交接文档重建。随后 `.venv` 用 Python 3.11.9 重建并装依赖；C 盘 3 个 git worktree 删除（分支先推送固化、未提交文档抢救归档）；旧目录全删。
- **关键结果**：pytest 264 passed + 4 skipped 全绿；check_project.sh PASS；live 文件旧路径残扫 0；main 与 origin 同步（35fd558 → f5b6380）。
- **映射全记录**：`migration/MIGRATION_20260912.md`。

## 2026-09-11 第 18 轮审稿修订 + 全文一致性审计

- **第 18 轮**（3d984c6）：接手中断会话的未提交修订（SEC 口径细分、b17 预算披露、benchmark 纳入规则、tab:configs、SPEF 公式、F6 降强），修正幽灵引用/重复段落/配置表事实错误；排版债清零（0 Overfull，9 页）。
- **一致性审计**（d329f19）：修复 8 处正文与实验产物的矛盾（策略分布、b21 +2.75、3363 次 STA、b06 声明、b18/b19 归属、SEC 计数 5 处口径、随机种子、pcpi_mul +0.07）；审计记录 `review_history/paper_audit/consistency_audit_20260911.md`。

## 2026-09-08 ~ 09-09 实验补齐与结果汇总（摘要）

b17 phase-2 重跑（+0.38 ns / 104 STA / SEC 12812+1 unproven）；joint-depth 消融；hold-mode ITC-99（诚实 limitation）；multi-iter ablation 与 --no-early-stop 修复；`experiments/RESULTS.md` + `results.json` 顶层汇总。详见 `LOGS.md`。

（2026-08-11 ~ 08-13 的 17 轮命名版审稿史、2026-08-26 unified-loop 主实验、更早 N31 系列见 `LOGS.md` 与 `review_history/paper_audit/`。）
