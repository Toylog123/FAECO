# project/scripts — 构建 / 运行脚本

> 放项目工程的构建、启动、状态检查脚本（受 git 跟踪）。生成的工程目录在 `project/` 下但被 git-ignored。

形式：

- 脚本自包含、可重复运行，注释标明输入 / 输出 / 环境。
- 命名：`run_<动作>.sh` / `build_<目标>.sh` / `check_<状态>.sh`。
- 生成物输出到 git-ignored 路径（如 `project/<工程>/`、`scratch/`）。
