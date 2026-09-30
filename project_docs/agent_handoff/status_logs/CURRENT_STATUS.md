# Current Status

## 2026-09-30 补充材料成文轮（本轮）

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
