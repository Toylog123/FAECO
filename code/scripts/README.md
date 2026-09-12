# 可复用脚本

按语言 / 用途划分子目录（`python/`、`shell/` 等），随项目需要扩展。

## 内置工具脚本

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check_record.sh` | 检查今日是否已更新交接记录 | `bash code/scripts/check_record.sh` |
| `check_project.sh` | 项目健康检查（记录 / 目录卫生 / git 状态 / 占位残留），输出交接就绪度 | `bash code/scripts/check_project.sh` |
| `make_manifest.sh` | 冻结基线前生成源码 + 测试 + 证据的 SHA-256 清单 | `bash code/scripts/make_manifest.sh [-o 输出] [路径...]` |

统一入口：`make check` / `make record` / `make manifest`（见根 `Makefile`）。

## 规则

1. 脚本应**自包含、可重复运行**，注释标明输入、输出、运行环境。
2. 晋级路径：`scratch/`（临时）→ `code/scripts/`（复用）→ 证据包 `source/`（随实验固化）。
3. 一次性探针脚本留在 `scratch/`，不要堆积在这里。

| `run_with_timeout.sh` | 长任务超时运行包装（测试/实验/构建防卡死） | `bash code/scripts/run_with_timeout.sh <秒> <命令...>` |
