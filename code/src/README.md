# src — 主源码

按技术模块建立子目录。示例：

```text
code/src/
|- module_a/          # 模块 A
|- module_b/          # 模块 B
|- include/           # 公共头文件 / 定义
|- constraints/       # 约束（硬件） / 配置（软件）
`- DESIGN.md          # 源码层设计文档
```

规则：

- `DESIGN.md` 记录架构、模块划分与关键决策，随代码演进更新。
- 生成产物（编译输出、工程文件）放 git-ignored 的 `project/` 或 `scratch/`，**绝不放在源码旁**。
- 根目录临时脚本晋级到这里：`scratch/` → `code/src/`（或 `code/scripts/` / `code/tests/`）。
