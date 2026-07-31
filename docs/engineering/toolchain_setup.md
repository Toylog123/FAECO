# Toolchain Setup

更新时间：2026-07-20

本文档记录 FAECO 工程原型所需工具链、当前检测结果和后续接入策略。

## 1. 当前检测结果

基线检测时间：2026-07-15

可复现快照：`experiments/environment/toolchain_2026-07-15.json`，由 `scripts/check_toolchain.ps1` 生成。

当前 runner 还会为每次实验自动写入 `experiments/<run>/environment/toolchain_snapshot.json`，并把快照路径和工具可用性 map 写入实验 `config.json`；batch runner 还会在 `tables/case_summary.json` 的每个 run 行中透传同一份 snapshot。snapshot 中每个工具条目包含 `version` 字段，可用工具记录版本，不可用工具记录 `null`。最近的 batch snapshot 位于 `experiments/20260718_minimal_combinational_batch_demo/environment/toolchain_snapshot.json`。

| 工具 | 当前状态 | 说明 |
|---|---|---|
| Python | 可用 | 当前实验 snapshot 中可用，版本为 3.11.9 |
| Yosys | 可用 | Scoop `yosys 0.9`，当前 batch snapshot 已记录版本和 shim 路径 |
| ABC | 已安装并进入默认实验链路 | UC Berkeley ABC 1.01 由 Scoop Yosys 包提供，命令为 `yosys-abc.exe`；runner 和快照默认候选为 `yosys-abc` 后回退 `abc` |
| OpenSTA | WSL2 已安装并接入 Stage B runner (2026-07-31) | 2026-07-20 在 WSL2 Ubuntu 24.04.4 中按 `parallaxsw/OpenSTA` commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56` 构建，`/usr/local/bin/sta -version` 返回 `3.1.0`；Stage B runner `src/rseco/opensta.py` + 7 项 TDD 测试已实现，`_to_sta_path` 把 Windows 路径转换为 `/mnt/d/...` WSL2 路径；8-case Stage B 端到端 mapping 8/8 success + STA 8/8 success，`experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}` 已落盘 |
| z3 Python package | 未检出 | 后续可用于小 cone SAT/SMT 等价验证 |
| networkx Python package | 可用 | 当前实验 snapshot 中可用，版本为 3.4.2；weighted cut 当前使用项目内 Edmonds-Karp 实现，后续可替换或交叉验证 |

## 2. 当前可运行策略

当前阶段不依赖外部 EDA 工具，先用项目内最小实现跑通：

| 模块 | 当前实现 | 后续替换/扩展 |
|---|---|---|
| netlist parser | `src/rseco/netlist.py` 解析简单 gate-level Verilog | 后续用 Yosys 规范化输入 |
| cone extraction | `src/rseco/graph.py` 支持 fanin cone | 后续扩展 fanout 和 sequential path cone |
| equivalence | `src/rseco/equivalence.py` 支持 structural signature；`src/rseco/yosys_abc.py` 支持正式 Yosys-BLIF-ABC full-netlist `cec` | 当前 5-case local smoke formal 为 5/5 pass；scope 为 Yosys 规范化后的门级 full-netlist 全部主输出对比 |
| ABC baseline | `src/rseco/yosys_abc.py` 提供 rewrite/refactor/resyn baseline | 使用 `yosys-abc -s` 和显式 Berkeley ABC resyn2 展开序列，保留 optimized BLIF，并从 ABC `print_stats` 提取 AIG node/level；当前 5-case local smoke 为 5/5 success |
| fixed cut | `src/rseco/cut.py` 使用 cone boundary 作为 baseline | 后续实现真正 network-flow/min-cut |
| patch | `src/rseco/patch.py` 记录候选 patch | 后续接 patch replacement |

## 3. 推荐接入顺序

| 阶段 | 工具 | 目标 |
|---|---|---|
| Step 1 | 无外部工具 | 跑通 c17 demo、cut、patch、metrics |
| Step 2 | Yosys | 将公开 Verilog/BLIF 统一转为简单 gate-level netlist |
| Step 3 | ABC | 生成 resynthesized netlist 和开源 baseline |
| Step 4 | ABC SAT 或 Z3 | 对 candidate patch 做形式化等价验证 |
| Step 5 | OpenSTA | 接入 WNS/TNS 和 violating paths |

## 4. Windows 环境建议

当前优先不在工程中硬编码安装路径。后续可采用：

1. MSYS2/conda 安装 Yosys 和 ABC。
2. 通过环境变量记录工具路径。
3. 在 `scripts/check_toolchain.ps1` 中集中检测。
4. 实验配置中记录工具版本和命令行。
5. 每次实验保留 `environment/toolchain_snapshot.json`，用于解释 ABC baseline、formal equivalence 和外部 runtime 的可用性。

当前本机探测结果：`yosys.exe` 和 `yosys-abc.exe` 已由 Scoop `yosys 0.9` 安装到 shims；OpenSTA 已在 WSL2 内安装，可通过 `FAECO_OPENSTA="wsl.exe -d Ubuntu -- /usr/local/bin/sta"` 暴露给 Windows 检测脚本和 Python runner。检测脚本和 Python runner 已支持 `FAECO_ABC`、`FAECO_YOSYS`、`FAECO_OPENSTA` 显式路径或带参数命令，并优先于 PATH 检测。未设置 `FAECO_ABC` 时，当前 runner 会自动识别 `yosys-abc`，再回退到 `abc`。

工具兼容性 smoke 已确认：ABC 1.01 直接读取 c17 的 ANSI 端口声明会断言，读取 c432 的多行 module 声明会失败；c432 文件还带 UTF-8 BOM，Yosys 0.9 会静默跳过该 module。去除 BOM 后，以 Yosys `proc; flatten; opt; simplemap; clean; write_blif` 规范化，再执行 ABC `cec`，c17 和 c432 均报告 equivalent。正式接入必须复用这条规范化链路，不能把“可执行文件已安装”直接写成“5-case formal 已通过”。

2026-07-19 的 X18 隔离设计探针进一步覆盖了当前 5 个本地 smoke case。探针位于 Git 忽略的 `tmp/x18_full_netlist_probe_20260719_03/`，`probe_summary.json` 的 SHA256 为 `0EE7281BC7B0D04EC03EAB27C6D0538A9EB74B7F7105F83FBA8066672CA6A685`。5 个 original/resynthesized pair 经去 BOM、Yosys-BLIF 规范化后，全网表全部主输出 `cec` 均为 pass；5 个 ABC baseline 均生成 optimized BLIF，且 original/optimized 回验均为 pass。2026-07-20 已批准 X18 的 formal scope 为 Yosys 规范化后的门级 full-netlist 全部主输出对比；candidate/boundary-level formal 留作后续增强。该结果仍只是设计探针，不是正式 runner 产物；c432/c499/c880 仍受未声明 license 限制。

探针还定位了两个正式接入前必须处理的兼容性问题：

1. 当前 Scoop/Yosys 包没有可加载的 `abc.rc`，因此 wrapper 中的 `resyn2` alias 会报 `unknown command`。Berkeley ABC 官方仓库 commit `bcfdf592289a408cd67ec19260f8a60a37b085b6` 的 `abc.rc` 将 `resyn2` 定义为 `b; rw; rf; b; rw; rwz; b; rfz; rwz; b`。隔离探针使用 `-s` 禁止隐式 rc，并显式展开为对应内建命令，5 个 baseline 均成功。
2. ABC optimized BLIF 经 Yosys 0.9 `write_verilog` 导出后使用 assign/LUT 表达式；当前轻量 parser 对 5 个导出文件均得到 `gate_count=0`。因此 baseline 的 AIG node/level 指标应从 ABC `print_stats` 结构化提取，不能把该 Verilog 交给当前 parser 后声称得到门数。探针中的 c432/c499/c880 AIG and-node 分别减少 70/10/14，level 分别减少 7/4/2；c17 两个 run 均无变化。上述数值仍只用于集成设计判断，不进入论文主表。

### 4.1 OpenSTA 只读安装就绪审计与 WSL2 构建

2026-07-19 的只读审计固定了 [OpenSTA 官方仓库](https://github.com/The-OpenROAD-Project/OpenSTA) `master` commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56`、GPL-3.0 license SHA256 和官方 Ubuntu 24.04 Dockerfile。审计产物位于 Git 忽略的 `tmp/opensta_readiness_audit_20260719_01/readiness_summary.json`，SHA256 为 `2198CBD5D6E7D4A268047E8D32D9C2C05B543A93F19D38664FD913EE1670CEB0`；该文件不是正式实验产物，也没有改变 runner 或 batch 工具状态。

当前三条路径的结论如下：

| 路径 | 当前状态 | 判断 |
|---|---|---|
| WSL2 Ubuntu 24.04 源码构建 | 已完成本体构建 | 与官方 Ubuntu 24.04 recipe 对齐；已安装 CMake、Tcl、SWIG、Bison、Flex、Eigen、fmt、automake/autotools，已构建 CUDD 3.0.0 和 OpenSTA `3.1.0`；仍需 Stage B runner 路径桥和正式 WNS/TNS artifact |
| Docker Ubuntu 24.04 | 未就绪 | Docker 29.2.1 client 可用，但 daemon 未运行；runner 还缺 volume/path wrapper |
| Windows 原生源码构建 | 首轮不推荐 | 当前缺少 CMake/Tcl/CUDD 等依赖，Scoop 无 OpenSTA package，且官方当前 recipe 主要面向 Ubuntu |

官方 Dockerfile 从 `davidkebo/cudd` 的 `main` 分支 URL 下载 `cudd-3.0.0.tar.gz`，未在文件中固定 archive checksum。正式构建应固定 OpenSTA commit，并在安装前独立核验并记录 CUDD archive SHA256，不能只把浮动 URL 当作可复现版本。

现有工具解析逻辑可以通过 `FAECO_OPENSTA="wsl.exe -d Ubuntu -- /usr/local/bin/sta"` 记录带参数命令并执行 `-version` 探测。2026-07-20 已修复 PowerShell 检测脚本对 `-d`/`--` 参数的保留，以及 WSL PATH translation warning 对版本行的干扰；Python runner 的版本探测 timeout 也已从 5 秒提高到 20 秒，避免 WSL 冷启动时把 OpenSTA 版本误记为 `null`。但真正 Stage B 调用还必须设计 Windows 到 WSL 的 Liberty、Verilog、SDC 和 report 路径转换；在该设计和测试完成前，不能把“OpenSTA 本体已安装”写成“OpenSTA 已接入实验 runner”。正式 5-case batch 尚未产生可报告的 WNS/TNS 或真实 STA critical path。

2026-07-20 安装前复测确认：WSL2 `Ubuntu` 发行版可启动，系统为 Ubuntu 24.04.4 LTS、`x86_64`；但 `which sta`、`which opensta`、`/usr/local/bin`、`/usr/bin`、`/opt/opensta/bin`、`/opt/OpenSTA/build` 以及 root filesystem 内的 `sta` 搜索均未发现 OpenSTA 可执行文件。随后已用 root apt 安装缺失依赖，CUDD 3.0.0 archive SHA256 固定为 `b8e966b4562c96a03e7fbea239729587d7b395d53cadcc39a7203b49cf7eeb69`，并构建 `/opt/faeco/OpenSTA-parallaxsw-dc5ccd2/build/sta`。`/usr/local/bin/sta` 已链接到该二进制，`sta -version` 返回 `3.1.0`。WSL 输出的 `Failed to translate E:\APP\...` 是宿主 PATH 翻译噪声，安装和 smoke 均已在该噪声存在时完成。

最小 STA smoke 产物位于 Git 忽略的 `tmp/faeco_opensta_smoke_20260720_01/`，输入包含 `smoke.lib`、`smoke.v`、`smoke.sdc` 和 `smoke.tcl`。命令 `wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/BaiduSyncdisk/03_FAECO/tmp/faeco_opensta_smoke_20260720_01 && sta -no_init smoke.tcl | tee smoke.out'` 已通过，输出完整 max timing path，slack 为 `0.70 slack (MET)`，并报告 `wns max 0.00`、`tns max 0.00`。这证明 OpenSTA 本体和 Windows 工作区到 WSL `/mnt/d/...` 读路径可用，但尚未证明 runner 能自动生成 Liberty/Verilog/SDC/report 路径并解析正式 WNS/TNS。

## 5. 显式工具路径变量

| 环境变量 | 对应工具 | 示例 | 使用位置 |
|---|---|---|---|
| `FAECO_ABC` | ABC | `C:\tools\abc\abc.exe` 或 `python C:\tools\fake_abc.py` | `scripts/check_toolchain.ps1`、实验 runner snapshot、ABC formal wrapper、ABC baseline wrapper |
| `FAECO_YOSYS` | Yosys | `C:\tools\yosys\yosys.exe` | `scripts/check_toolchain.ps1`、实验 runner snapshot |
| `FAECO_OPENSTA` | OpenSTA | `C:\tools\OpenSTA\sta.exe` 或 `wsl.exe -d Ubuntu -- /usr/local/bin/sta` | `scripts/check_toolchain.ps1`、实验 runner snapshot；真正 Stage B 还需路径桥接 |

使用方式示例：

```powershell
$env:FAECO_ABC = (Get-Command yosys-abc).Source
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_toolchain.ps1
python scripts\run_minimal_combinational_demo.py --config experiments\configs\minimal_combinational.json --output-dir experiments\20260718_minimal_combinational_batch_demo
```

如果环境变量指向不可执行文件或无法解析的命令，检测逻辑会回退到 PATH；如果 PATH 也没有对应工具，则 snapshot 仍记录 `available=false`、`version=null`。

## 6. 最小验收标准

进入批量 benchmark 前，工具链至少应满足：

1. `python -m unittest discover -s tests` 通过。
2. `yosys` 能读取一个 ISCAS/EPFL Verilog 并输出规范化网表。
3. `abc` 能对同一网表执行 `strash; rewrite; refactor; balance`。
4. 等价验证接口能对一个小 cone 返回 pass/fail/timeout。
5. 所有工具版本写入实验目录。

## 7. 检测命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_toolchain.ps1 `
  -OutputPath experiments/environment/toolchain_YYYY-MM-DD.json
```

脚本输出 JSON，字段包含检测时间、工具标识、可用状态、实际命令、路径和版本。Python 包检测使用当前 `python` 解释器，因此结果与运行 FAECO 原型的环境一致。

实验 runner 内部使用同一类检测逻辑生成 per-experiment snapshot。单独复测工具链时仍使用上面的脚本；生成实验结果时，以实验目录内的 snapshot 为论文表格追溯依据。
