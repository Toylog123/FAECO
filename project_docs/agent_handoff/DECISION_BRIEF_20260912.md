# 决策简报（2026-09-12，交用户拍板的三件事）

> 每项给出：现状事实 → 选项与成本 → 建议。选定后由下一轮会话执行。

---

## D-01 versions/v1 基线冻结方案（OI-003）

**现状事实**

- 模板 `project_docs/versioning.md` 定义"版本 = 论文 + 源码 + 测试 + 证据"四元绑定，且明确两条承载方式：**git commit/tag 承载历史**（每个 commit 即不可变版本）+ `versions/` 完整体复制（零交叉引用，最高要求）。
- git 已跟踪 1303 个文件（论文 tex/PDF、code 全部、实验**汇总层**：RESULTS.md/results.json/INVENTORY/聚合 summary）；实验原始输出 **116 GB 未跟踪**（其中 itc99_main 19G、phys_closure 2.6G、sprint1_itc99 2.5G、sprint2_lambda_b18 2.3G、sprint2_ablation 1.5G）。
- 磁盘现状：同步盘单份 116 GB 已较重。

**选项**

| 选项 | 内容 | 成本 | 说明 |
|---|---|---|---|
| **A 轻量冻结（推荐）** | `git tag v2026-09-12-submission-ready` + SHA-256 manifest（论文 tex/PDF + code/src + code/tests + RESULTS + results.json + 聚合 summary + SEC csv）落 `versions/v1/`（KB 级） | 分钟级 | 符合模板"历史由 git 承载"条款；manifest 锁定四元绑定；不复制原始输出 |
| B 中量冻结 | A + 把 paper-evidence 汇总层小文件（估 <100 MB）复制进 `versions/v1/evidence/` | 小时级 | "证据自包含"口径更强；与 experiments/ 内容重复 |
| C 完整体复制 | code+docs+paper+关键实验目录全复制（≥25 GB；全量 116 GB） | 天级+磁盘双份 | 模板字面最高要求，但同步盘不现实，不推荐 |

**建议**：A。投稿里程碑用 tag+manifest 固定即可；若将来期刊要求证据打包，再按 B 补。

---

## D-02 机制图（OI-006，现状已变化，原问题基本消失）

**现状事实**

- 原"1 总览 + 3 局部小图"拆分方案针对 **2026-08-13 的 12 页 JCAD 版**（4 张机制图、图 2 缩得过小）。
- 当前 9 页改名稿**只保留 3 张图**：方法流程（`fig_method_flow_redraw_20260814.png`）、割生成机制（`fig_cut_generation_mechanism_imagegen.png`）、ISCAS89 数据图（`fig_iscas89.pdf`）——"4 图拆分"问题在当前版本已不存在。
- 旧拆分提示词生成于 2026-08-13 会话（thread 019fefa2…），**未存档到仓库**；旧版机制图素材仍在 `paper/zh/figures/`（fig_feedback_loop_new.png 等）。

**选项**

| 选项 | 内容 | 成本 |
|---|---|---|
| **A 维持现状（推荐）** | 3 图布局已通过 18 轮审稿 + 一致性审计；不再动图 | 零 |
| B 增补机制图 | 若目标期刊模板/审稿要求更多示意（失效反馈闭环、SPEF 门控），从旧素材增补 1–2 张 | 半天（重排 + 重编译调 0 Overfull；9 页双栏已较满，有页数风险） |

**建议**：A，投稿后视审稿意见再定。

---

## D-03 DOI / DRC（OI-001 / OI-002，实际比登记的更轻）

**DOI — 事实更新**：主稿正文**没有 DOI 占位符**（"DOI"仅出现在一行注释和模板示例 template.tex/example_paper.tex；中图法分类号 TP391.41 已填）。因此 OI-001 从"替换占位符"降级为：**投稿时按目标期刊模板补稿件编号/DOI 字段**——纯投稿流程动作，无正文风险。

**DRC — 现状与选项**

- 事实：P&R 产物（`experiments/20260807_real_pr_iscas8`）有 pr_run.log / pre_layout_audit 等，但无 DRC 报告；论文已按 nature 口径**如实声明不写 DRC signoff**。
- 关键约束：OpenROAD 2.0 本身不含完整 signoff DRC；SKY130 的 DRC signoff 需引入 **Magic/KLayout** 工具链 + 对 16 个 final.odb 重跑 + 违例修复迭代（天级工作量，且可能引出新的物理问题）。

| 选项 | 内容 | 成本 |
|---|---|---|
| **A 维持如实声明投稿（推荐）** | 边界声明已写清楚；审稿通常不因如实声明的边界拒稿 | 零 |
| B 被要求时补跑 | 若审稿意见提出，再引入 Magic（sky130.tech）对 ODB 跑 DRC 出报告，作为 rebuttal 证据 | 天级，仅按需 |

**建议**：两项都取 A；DRC 留作 rebuttal 备选。

---

## 选定后的执行清单（下一次会话）

1. D-01=A → `git tag v2026-09-12-submission-ready && git push --tags` + `make manifest` 生成清单入 `versions/v1/`。
2. D-02=A → 无动作（OI-006 关闭为 "current-layout accepted"）。
3. D-03=A → OI-001/OI-002 关闭/降级为投稿流程项。
