# 环境与依赖清单

> 目标：任何接手者按本文件即可**完整复现**开发 / 实验环境。
> 环境变更时同步更新本文件。

## 1. Python（Windows 侧，宿主）

- Python 3.11；依赖以根目录 `pyproject.toml` 为准：`pip install -e .`
- 测试：`python -m pytest code/tests -q`（264 项，2026-09-12 迁移前全绿基线）
- 论文图脚本：`paper/zh/figures/gen_figures.py`（matplotlib，直读 `experiments/` 聚合 JSON）
- 论文编译：XeLaTeX（latexmk -xelatex），字体为系统字体（方正书宋/黑体/SimHei）

> 注意：仓库 2026-09-12 自 `D:\BaiduSyncdisk\03_FAECO` 迁入本路径，旧 `.venv` 内可编辑安装的绝对路径已失效——在本目录重新 `pip install -e .` 即可。

## 2. EDA 工具链（WSL2 Ubuntu 侧）

| 工具 | 版本 | 用途 |
|---|---|---|
| OSS-CAD Suite（Yosys + yosys-abc） | 0.67+146 | 综合映射（SKY130 HD）、ABC cec、基准转换 |
| Yosys（系统包） | 0.33 | 顺序 SEC（equiv_make + equiv_simple + equiv_induct）；b18/b19 大电路 64 位映射 |
| OpenSTA | 3.1.0（parallaxsw dc5ccd2 + CUDD 3.0.0） | 理想线网 / SPEF 时序测量（`sta` 在 WSL PATH） |
| OpenROAD | 2.0 | 布局 + 全局布线寄生估计验证（P&R 实验） |

## 3. 工艺库与数据

- SKY130 HD（sky130_fd_sc_hd）；Liberty `tt_025C_1v80` 位于 `data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/<sha>/lib/`
- SEC 用行为单元模型：`data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v`（由 Liberty boolean function 提取，生成脚本 `code/scripts/make_liberty_cells_v.py`）
- 基准：ISCAS89（8 电路主数据）、ITC-99（b01–b15/b17/b20–b22 批量 + b18/b19 补充实例）、PicoRV32 三子模块；EPFL v2025.1 固定版本
- 时钟约束：统一 0.5 ns（stress-test 口径，见论文 §4.1）

## 4. 工具链检测

`code/scripts/check_toolchain.ps1`（Windows）/ `bash code/scripts/check_project.sh`（框架体检）输出机器可读快照。
