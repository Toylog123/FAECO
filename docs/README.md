# docs/ — 技术文档

技术文档（环境、术语、经验、文献）。与项目过程文档 `../project_docs/` 的分工：

- `docs/`：**技术性**文档，面向实现与复现（环境、术语口径、经验、文献、材料）。
- `project_docs/`：**过程性**文档，面向管理与交接（进度、日志、看板、评审、基线、证据）。

避免两处内容重复：同一主题只在一处维护，另一处用链接。

| 文件/目录 | 内容 |
|---|---|
| `environment.md` | 工具链版本、依赖、复现环境（Python/WSL2/OSS-CAD/OpenSTA/OpenROAD/SKY130） |
| `GLOSSARY.md` | 术语中英速查与关键口径（正式定义以论文 §3 为准） |
| `EXPERIENCE.md` | 经验库：现象 / 原因 / 解决 / 验证 |
| `literature/` | 文献矩阵与笔记（Related Work 证据链，25A/1B） |
| `materials/` | 原始材料归档 |

论文在 `../paper/zh/`；实验在 `../experiments/`（`INVENTORY.md` 总索引）。
