# code — 当前版本代码资产

> 当前推进版本的代码统一收纳于此。包含：

| 子目录 | 内容 |
|--------|------|
| `src/` | 源码（按模块），`DESIGN.md` 记录源码层设计 |
| `scripts/` | 脚本（工具：`check_record` / `check_project` / `make_manifest` 等） |
| `tests/` | 测试 |

规则：

1. 开发 / 脚本 / 测试都在 `code/` 内自包含推进。
2. 阶段完成 → 打基线 + git tag → 完整复制为 `versions/<基线ID>/`（见 `versions/README.md`）。
3. 临时脚本放 `scratch/`，晋级后归 `code/scripts/` 或 `code/tests/`。
