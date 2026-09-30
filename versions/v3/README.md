# 版本 v3 — `v2026-09-30-submission-ready-r2`（终审 5 处修正冻结）

- 基线 ID：`v2026-09-30-submission-ready-r2`
- 冻结日期：2026-09-30
- git tag：`v2026-09-30-submission-ready-r2`（annotated tag，指向包含本 README 与 `MANIFEST.sha256` 的提交）
- 方案：**D-01=A 轻量冻结**（同 v1/v2）
- **派生来源**：自 v2（`v2026-09-30-submission-ready`）派生。改动 = 用户终审指出的 **5 处正文一致性修正**（零数字、零实验）：
  1. §3.4 F6 交叉引用纠错（§4.4 → §4.5，F6 定位为"验证识别与过滤作用、未证明独立提高物理 WNS"）；
  2. §4.1 接受准则复述闭合 b06 TNS 辅助接受例外；
  3. 摘要（中/英）PicoRV32 分母解释（`picorv32_regs` 无 setup path 不参与判定，消除"其余 1 个电路"歧义）；
  4. 表 8 补 $\Delta L=L_{\mathrm{before}}-L_{\mathrm{after}}$ / $\Delta_{\mathrm{WNS}}$ 符号定义；
  5. §4.5 F6 措辞与方法层"启用式反馈"口径对齐。
  详见 `paper/zh/CHANGE_LOG.md` 2026-09-30 终审行与 `PAPER_EVIDENCE_MANIFEST.md` §6。

## 与 v2 的差异

| 项 | v2（superseded） | v3（active） |
|---|---|---|
| 论文 tag | `faeco-paper-final-20260930` | `faeco-paper-final-20260930-r2` |
| PDF 字节 SHA256 | `df82292f…` | `28647dc0…` |
| 内容指纹（poppler 25.07） | `43becd39…` | `70bbd610…` |
| 正文 | 5 处一致性修正前 | 5 处一致性修正后（终稿） |

## manifest 覆盖范围（与 v1/v2 相同口径）

论文 `.tex` + 双副本 `.pdf`；`code/src`、`code/tests` 源文件（不含构建产物）；`experiments/RESULTS.md`、`results.json`、`20260826_aggregation/summary.json`（论文主数字源）、`ablation_summary.json`、`20260826_sec/summary.csv`。

**验证方法**（仓库根目录）：`sha256sum -c versions/v3/MANIFEST.sha256` —— 117 条全部 OK 即冻结未动。
