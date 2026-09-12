# Current Status

## 2026-09-12 框架架构迁移完成

- **完成**：仓库迁移至 `D:\BaiduSyncdisk\01_Papers\03_FAECO`（99_项目模板框架），git 历史与远程保留；目录重组织 + 路径修复 + 交接文档重建。
- **当前位点**：论文（9 页，第 18 轮 + 一致性审计闭环）已推送；工程结构对齐模板；等待用户决策 OPEN_ISSUES 中 OI-003 / OI-006。
- **阻塞 / 风险**：
  - 旧 `.venv` 可编辑安装路径失效（迁移副作用）——本目录重新 `pip install -e .` 即可；
  - 旧目录 `D:\BaiduSyncdisk\03_FAECO` 仍存在（迁移源归档，处置见 OI-005）；
  - `experiments/` 历史产物内记录的旧绝对路径为证据记录，不改写。

## 下一步（建议优先级）

1. 迁移后首跑验证：`python -m pytest code/tests -q` + `bash code/scripts/check_project.sh`。
2. 用户确认 OI-003（versions/v1 冻结方案）后执行首个基线冻结。
3. 论文第 19 轮（如有新审稿意见）：以 `review_history/paper_audit/consistency_audit_20260911.md` 为基线，仅处理新意见。
4. 投稿前：DOI 替换（OI-001）、DRC signoff 决策（OI-002）。

## 不要做

- 不要删除 `D:\BaiduSyncdisk\03_FAECO`（用户处置）。
- 不要改写 `experiments/` 历史产物；论文改动前先跑测试 + 数字对账（GLOSSARY 关键口径）。
