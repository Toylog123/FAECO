# 主目录磁盘使用审计与瘦身结果

日期：2026-08-24
审计范围：`D:\BaiduSyncdisk\03_FAECO` 及隔离 worktree
本轮删除量：**0 bytes**

## `experiments/` NTFS 原位压缩最终结果

本轮仅对精确目录 `D:\BaiduSyncdisk\03_FAECO\experiments` 执行 NTFS 原位压缩；未移动、重命名、归档或删除任何文件。`compact` exit code 为 `0`。统计为 310,251 files、79,075 directories；逻辑大小 17,739,639,394 bytes，物理占用 5,752,165,068 bytes，压缩比约 3.1:1。D 盘可用空间由 42.931 GiB 增至 54.387 GiB，增加 11.456 GiB。

抽检 `sta.log`：逻辑长度 333,472,702 bytes，仍可读；物理占用 125,054,976 bytes，压缩比约 2.7:1。`tmp/`、`paper/`、`.venv/` 未处理。

## 分层证据

主目录约 **19.7 GiB**，分层统计如下（四舍五入）：

| 层级 | 占用 | 文件数/说明 |
|---|---:|---|
| `experiments/` | 16.832 GiB | 231,178 files |
| `tmp/` | 1.222 GiB | 临时产物 |
| `paper/` | 0.676 GiB | 论文与渲染产物 |
| `benchmarks/` | 0.445 GiB | benchmark 资产 |
| `.venv/` | 0.429 GiB | Python 环境 |
| `.git/` | 0.025 GiB | Git 数据 |
| 隔离 worktree | 约 25 MiB | 独立工作区 |

`experiments/` 内部最大项为：`mapped.v` 75,829 个、9.217 GiB；`sta.log` 75,934 个、6.307 GiB；`pr_run.log` 0.591 GiB。主要实验目录约为：`pureB` 2.628 GiB、`phys_closure` 2.586 GiB、`sprint1` 2.398 GiB、`lambda_b18` 2.258 GiB、`sprint2_ablation` 1.441 GiB。

## 根因

- `real_wns.py` / `hold_repair.py` 对每个 candidate 写全量 `mapped.v`，导致候选数直接放大网表副本占用。
- `opensta.py` 将 OpenSTA stdout+stderr 全量写入 `sta.log`，导致大量重复日志。
- 这些产物已加入 `.gitignore`，避免进入版本库，但 gitignore 不会释放固定的本地磁盘空间。

## 分级建议（只建议，不删除）

- **A：保留** manifest/JSON、最终 accepted 结果和关键原始日志，作为可复现与审计证据。
- **B：可考虑归档**候选级 `mapped.v` 与候选级 STA 日志；应先按实验目录、manifest 和接受候选清单确认可恢复性。
- **C：需逐路径确认后才可处理** `tmp/`、`.venv/`、论文渲染中间物；尤其不能把共享环境或未核实实验产物作为整体删除。

本轮删除量为 0 bytes；除上述对精确 `experiments/` 目录的 NTFS 原位压缩外，没有移动、重命名或归档文件。后续删除或路径级清理仍必须由用户逐项批准。
