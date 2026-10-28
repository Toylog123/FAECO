# 环境与依赖清单

> 目标：任何接手者按本文件即可**完整复现**开发 / 实验环境。
> 环境变更时同步更新本文件。

## 1. Python（Windows 侧，宿主）

- Python 3.11；依赖以根目录 `pyproject.toml` 为准：`pip install -e .`
- 测试：`python -m pytest code/tests -q`（542 项）
- 论文图脚本：`paper/zh/figures/data/scripts/review_r21_figures.py`（matplotlib，原始 JSON/逐候选台账与来源SHA256；旧 gen_figures.py 留作历史）
- 论文编译：**LuaLaTeX**（ctexart 双栏，r21末页采用已安装flushend的noshrink/nospread平衡；须 `cd paper/zh/manuscript` 后 `lualatex` 连跑两遍），字体走 **OSFONTDIR 项目内字体**（跨电脑免装；官方免费方正书宋/仿宋/黑体简体）

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

> 检测脚本按 **系统 Python** 探测 `z3` / `networkx`，而本项目实际跑在 `.venv`（editable 安装）里，
> 因此在只装了 venv 的机器上 `z3` 会**误报为不可用**。以 `.venv\Scripts\python.exe -c "import z3"` 为准。

## 5. 新设备恢复记录（2026-10-23，设备迁移后实测）

迁移到新设备时**下列三项会缺失**，且其中两项会直接让 D 复算 / 映射流程失败：

| 项 | 旧设备 | 新设备初始状态 | 恢复动作 |
|---|---|---|---|
| OpenSTA（WSL） | `/usr/local/bin/sta` = 3.1.0（parallaxsw dc5ccd2 + CUDD 3.0.0） | **完全缺失**（无 `sta`、无 `tclsh`/`swig`/`libeigen3-dev`） | 按 §5.1 源码重建，产出 `/usr/local/bin/sta` = **3.1.0** |
| WSL 发行版名 | `Ubuntu` | 实际叫 `Ubuntu-24.04` | 项目**硬编码** `wsl.exe -d Ubuntu`（见 `code/src/rseco/opensta.py:348`、`code/scripts/run_r22_cut_ablation.py:75,141`），故导出并以 `Ubuntu` 之名重新注册（`D:\WSL\Ubuntu`）。WSL 3.0.1 **不支持** `wsl --set-name` |
| OSS-CAD Suite（Windows 原生） | `C:\oss-cad-suite-build\oss-cad-suite`（Yosys 0.67+146 / `468ba27d9`） | **缺失** | 装 **2026-08-04** nightly 到 `C:\oss-cad-suite-build\oss-cad-suite` → `Yosys 0.67+146 (git sha1 468ba27d9-dirty)`，与证据钉的版本串**逐字一致** |

### 5.1 OpenSTA 3.1.0 重建配方（WSL2 Ubuntu 24.04）

```bash
apt-get install -y --no-install-recommends build-essential cmake swig tcl-dev tcllib \
    zlib1g-dev libeigen3-dev libfl-dev tcl-tclreadline libfmt-dev flex bison \
    autoconf automake libtool make git ca-certificates
# CUDD 3.0.0 -> /usr/local（libcudd.so + cudd.h）
# OpenSTA: parallaxsw/OpenSTA @ dc5ccd2（= 3.1.0）-> cmake -DCMAKE_BUILD_TYPE=Release .. && make && make install
/usr/local/bin/sta -version   # => 3.1.0
```

- 源码获取：GitHub 网页 / codeload 在部分网络不通，**`api.github.com` 的 tarball 通道可用**：
  `https://api.github.com/repos/parallaxsw/OpenSTA/tarball/dc5ccd2`（返回 13.9 MB tar.gz）。
- 缺 `libfl-dev` 时 CMake 会在 `FLEX_INCLUDE_DIR` 上失败（`FlexLexer.h` 缺失）。
- 上游自带 `Dockerfile.ubuntu24.04`，其依赖清单可作权威参考。

### 5.2 Windows 侧 PATH 要求

- **OSS-CAD**：`bin` 与 `lib` **同时**加入 PATH（`lib` 内为 yosys.exe 依赖的 DLL），否则 `yosys -V` 无输出。
- **Git Bash 必须在 System32 之前**：机器级 PATH 优先于用户级 PATH，`C:\Windows\System32\bash.exe`（WSL 启动器）
  不支持 `pwd -W`，会让 `code/tests/test_run_equivalence_sweep_sh.py` 的 7 项动态检查被 skip。
  完整跑测请用：
  ```powershell
  $env:PATH = "C:\Program Files\Git\bin;C:\oss-cad-suite-build\oss-cad-suite\bin;C:\oss-cad-suite-build\oss-cad-suite\lib;" + $env:PATH
  .venv\Scripts\python.exe -m pytest code/tests -q
  ```

### 5.3 新设备实测基线（2026-10-23 / 10-24）

| 验证项 | 结果 |
|---|---|
| `pytest code/tests -q` | **1056 passed / 0 skipped / 156 subtests**（203.78 s） |
| 论文双稿 LuaLaTeX 双遍 | 主稿（源 SHA `f0f4d5e0…`）与补充（`79dfad67…`）均 rc=0 |
| OpenSTA 端到端 | s27 历史基线复测：WNS `-0.27`、TNS `-0.49`、min slack `0.44` 与旧设备 `sta.log` **逐项一致** |
| SEC 端到端 | `final_sec` → `wsl.exe -d Ubuntu -- /usr/bin/yosys` → "Equivalence successfully proven!"（11 proven / 0 unproven） |
| OpenROAD P&R 端到端 | s382 baseline `tns -15.77` / `worst slack -1.16` / `0.45`；fixed `tns -14.58` / `-1.02` / `0.44` —— 与 LOG-20260807-01 记录**四个数字全部一致**（baseline 16 s，fixed 79 s） |
| **映射字节复现** | 用 0.67+146 重跑 ISCAS89 s27 映射，产出 `mapped.v` SHA-256 = `b80c931d0ca423c…`（1547 B），与旧设备 `experiments/20260826_iscas89_main/s27/s27/mapped.v` **逐字节相同** |

### 5.4 OpenROAD 2.0（WSL 用户空间，2026-10-24 装好）

沿用 LOG-20260807-01 的配方：**无官方二进制**，取 Precision-Innovations 的 Ubuntu 22.04 deb 解包到用户目录。

```bash
# 1) 取 deb（GitHub API 资产端点，网页端不通）
#    https://api.github.com/repos/Precision-Innovations/OpenROAD/releases/tags/2024-12-14
#    -> openroad_2.0-17598-ga008522d8_amd64_ubuntu-22.04.deb
dpkg-deb -x <deb>.deb ~/or_extract          # -> ~/or_extract/usr/bin/{openroad,sta}
# 2) Qt5 运行时走 apt
apt-get install -y --no-install-recommends libqt5charts5 libqt5core5a libqt5gui5 \
    libqt5widgets5 libqt5svg5 libqt5network5 libqt5xml5 libqt5sql5 tcl-tclreadline
# 3) 两个符号链接（deb 不含 python3.10 / ortools 共享库名）
ln -s ~/or_extract/opt/or-tools/lib/libortools.so.9.11.4210 ~/or_libs/libortools.so.9
ln -s /usr/lib/x86_64-linux-gnu/libpython3.12.so.1.0      ~/or_libs/libpython3.10.so.1.0
# 4) ORFS 平台资产（与仓库 Liberty 同为 ORFS 提交 da8f092a…）
#    flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef、lef/sky130_fd_sc_hd_merged.lef、pdn.tcl
#    -> ~/OpenROAD-flow-scripts/flow/platforms/sky130hd/
```

- `~/or_env.sh` 是入口（`source ~/or_env.sh`）。**PATH 顺序必须 `/usr/local/bin` 在前**：
  deb 自带 `sta` 是 **2.6.0**，而项目工具链身份是 `/usr/local/bin/sta` = **OpenSTA 3.1.0**；
  顺序颠倒会让裸 `sta` 静默降级到 2.6.0。
- python3.10 → 3.12 的软链会打印 `Symbol 'PyType_Type' has different size` 警告，**与旧设备历史日志同款，属已知且无害**。
- LEF 冒烟基线：tlef = 13 layers / 25 vias，merged lef = **441 library cells**（与旧设备 `pr_run.log` 逐字相同）。
- 复跑入口：`experiments/20260807_real_pr_s382/run_pr_all.sh`（需 `~/pr_s382/{baseline,fixed}` 布局）。

### 5.5 归档工具

- **7-Zip 26.05** 已装（`C:\Program Files\7-Zip\7z.exe`，winget `7zip.7zip`），用于 `scratch/_archive_cleanup_20261021.7z` 等历史归档解包。
- Python `tarfile` / `zipfile` 可替代 `.tar.gz` / `.zip`，但**不能**替代 `.7z`。

### 5.6 仍缺 / 待办

| 项 | 影响面 | 说明 |
|---|---|---|
| Git Bash 的 PATH 优先级 | 7 项测试需会话级 PATH | 本机无管理员权限，机器级 PATH 改不了（`C:\Windows\system32\bash.exe` 恒先于用户 PATH）。根治需管理员执行一次：`[Environment]::SetEnvironmentVariable('Path','C:\Program Files\Git\bin;'+[Environment]::GetEnvironmentVariable('Path','Machine'),'Machine')` |

### 5.7 大文件下载配方（本网络 GitHub CDN 特性）

GitHub release 的**非 Range 请求会被限流/卡死在约 2 MB**，而**显式 byte-range 请求很快**。
另外 `api.github.com` 的未认证配额只有 **60 次/小时**，而**每个 Range 请求都计一次**——用 API 资产端点分块下载会
在几百 MB 处触发 `403 rate limit exceeded`。

可行组合（本次实测走通）：

1. 取签名后的 CDN 地址用 **一次** API 调用（`api.github.com/repos/<repo>/releases/assets/<id>`，
   `Accept: application/octet-stream`，不跟随重定向即可拿到 `Location`）；
2. 剩余字节**直接向 CDN** 发 Range 请求，**不再经过 API**，配额只花掉 1 次；
3. 或者更省：**用 release 下载直链** `https://github.com/<repo>/releases/download/<tag>/<asset>`
   带 `Range` 头，它 302 到同一 CDN，**完全不计 API 配额**（本次 591 MB 即用此路径完成，46 s）。

实测速度：Range 块 4–16 MB，约 2–13 MB/s。脚本见 `scratch/direct_range_download.py`、
`scratch/chunked_download.py`（后者带每块重试与增量落盘）。

另注：GitHub 网页 / `codeload` 在本网络不通，但 `api.github.com` 的
tarball / releases / **git blobs** 通道可用（ORFS 平台文件就是这样按 blob 取的）。


