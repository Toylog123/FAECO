# 版本 v20 —— 中文 v3 后布局可调预算面积回收基线（2026-11-22）

| 项 | 值 |
|---|---|
| 基线 ID | `v2026-11-22-postroute-v3-zh` |
| 前置基线 | `v19`（`v2026-10-28-acceptance-band-caliber-r28`，预布局 v2 定稿基线） |
| 当前论文（中文 v3） | `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（14 页，LuaLaTeX 0 Error / 0 Overfull / 0 Undefined） |
| 英文稿状态 | **暂冻**（先专注于中文论文定稿与工程/目录梳理，英文稿停在上一同步点，不纳入本中文 v20 发布范围） |
| 历史归档 | 预布局 v1/v2 中文主稿与补充材料继续保留在 `paper/zh/manuscript/`（只读归档） |

## 涵盖范围

1. **后布局可调预算核心与通用独立重布线引擎**：`code/src/rseco/` 与 `code/tests/` 全量 Python 源码及测试文档。
2. **中文 v3 主稿与双副本 PDF**：
   - 源码：`paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（已完成学术化表达精修，去除脚本文件名、内部接口名与工具命令行细节）
   - PDF 副本：`paper/zh/FAECO_v3_后布局可调预算面积回收.pdf`、`paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.pdf`（另同步副本至 `paper/zh/build/`）
3. **5 套 Nature 风格中文高清矢量图表**：
   - `fig_framework_arch_zh.pdf`、`budget_curves.pdf`、`fig_tipping_gate_mech_zh.pdf`、`fig_multicorner_spef_zh.pdf`、`fig_tool_agnostic_results_zh.pdf`（全部通过字体 $\ge 5\text{ pt}$ 与 `0 fail / 0 warn` 碰撞质检）
4. **核心后布局实验证据**：`project_docs/evidence/postroute_recovery_20261120/{REPORT.md, SUMMARY.json}`

## 验证命令

```bash
# 在仓库根目录校验全部锁定文件 SHA-256
sha256sum -c versions/v20/MANIFEST.sha256

# 若需重算 manifest
.venv/Scripts/python.exe versions/v20/make_manifest.py
```
