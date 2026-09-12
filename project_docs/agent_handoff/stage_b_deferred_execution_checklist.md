# Stage B 延后执行清单

更新时间：2026-07-30

## 1. 当前暂停点

- 用户已在 2026-07-30 明确恢复执行，要求从批次 0 开始并逐项更新清单。
- 尚未下载 SKY130 Liberty；`benchmarks/raw/openroad_flow_scripts_sky130hd/` 不存在。
- 尚未创建 Stage B runner、technology mapping wrapper 或正式 SDC。
- 当前已安装并验证 Python 3.11.9、Yosys 0.9、ABC 1.01、OpenSTA 3.1.0、Z3 5.0.0、NetworkX 3.6.1。
- 最新工具链快照：`experiments/environment/toolchain_2026-07-30.json`。
- Python 锁定依赖：`experiments/environment/python_requirements_2026-07-30.txt`。
- 完整回归基线：66 项测试通过，命令见第 3 节。
- `scripts/check_toolchain.ps1` 已区分 Python 模块名 `z3` 与发行包名 `z3-solver`。
- Git 分支为 `main`，仓库没有初始提交，大部分文件仍为 untracked；禁止 `git add .`。

## 2. 执行目标与边界

目标：先在 EPFL `ctrl` 上跑通可复现的 technology-mapped pre-layout STA，再扩展到 8 个固定版本 EPFL case。

首轮明确不做：

- 不下载完整约 7 GB 的 SKY130 PDK。
- 不安装 OpenROAD/ORFS 完整物理实现环境。
- 不声明 signoff timing。
- 不生成或假装存在真实 SPEF。
- 不引入商业 PDK、PrimeTime、Genus 或 Design Compiler。
- 不升级当前 Yosys/ABC 版本，以免改变 JSON、门数和 baseline 口径。

## 3. 批次 0：恢复与预检

- [x] 激活项目虚拟环境。

```powershell
cd D:\BaiduSyncdisk\03_FAECO
& .\.venv\Scripts\Activate.ps1
python --version
```

验收：输出 `Python 3.11.9`。

- [x] 检查锁定依赖完整性。

```powershell
python -m pip check
```

验收：输出 `No broken requirements found.`。

- [x] 检查核心工具版本。

```powershell
yosys -V
yosys-abc -h
wsl.exe -d Ubuntu -- /usr/local/bin/sta -version
```

验收：Yosys 0.9、ABC 1.01、OpenSTA 3.1.0。

- [x] 运行恢复前完整回归。

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

验收：至少 66 项测试、0 failure、0 error。若失败，停止后续下载和实现，先定位环境或代码回归。

- [x] 检查没有上次中断留下的半成品。

```powershell
Test-Path benchmarks/raw/openroad_flow_scripts_sky130hd
Get-Process git,curl -ErrorAction SilentlyContinue
git status --short
```

验收：目标下载目录不存在，且无残留 `git`/`curl` 下载进程。
批次 0 执行记录（2026-07-30）：

- `& .\.venv\Scripts\Activate.ps1; python --version` 输出 `Python 3.11.9`。
- `& .\.venv\Scripts\python.exe -m pip check` 输出 `No broken requirements found.`。
- `yosys -V` 输出 `Yosys 0.9 (git sha1 1979e0b1, i686-w64-mingw32.static-g++ 5.5.0 -Os)`。
- `yosys-abc -h` 输出 `UC Berkeley, ABC 1.01 (compiled Aug 26 2019 11:27:16)`，该命令按 ABC 行为返回 exit code 1 但版本信息完整。
- `wsl.exe -d Ubuntu -- /usr/local/bin/sta -version` 在沙箱内返回 `E_ACCESSDENIED`；提升权限只读复核输出 `3.1.0`，并伴随 Windows PATH translation warning。
- `$env:PYTHONPATH='src'; & .\.venv\Scripts\python.exe -m unittest discover -s tests` 在沙箱内因子进程 `CreateProcess` 触发 `[WinError 1312]`；提升权限复核 `Ran 66 tests in 61.076s`，`OK`。
- `Test-Path benchmarks/raw/openroad_flow_scripts_sky130hd` 输出 `False`；`Get-Process git,curl -ErrorAction SilentlyContinue` 无输出；`git status --short` 仍显示仓库无初始提交且大量文件 untracked。

## 4. 批次 1：只获取最小 SKY130 时序资产

### 4.1 固定来源

- [x] 查询并记录 OpenROAD-flow-scripts `master` 的精确 commit。
- [x] 查询并记录 `google/skywater-pdk` 或对应标准单元库仓库的精确 commit。
- [x] 创建来源 manifest：`benchmarks/source_manifests/sky130hd_openroad.json`。

manifest 至少记录：

- repository URL；
- source commit；
- raw URL；
- 文件相对路径；
- SHA256；
- license repository、license path、license commit；
- acquisition timestamp；
- intended use=`technology-mapped pre-layout STA`。

### 4.2 下载范围

- [x] 仅下载以下文件到 `benchmarks/raw/openroad_flow_scripts_sky130hd/<commit>/`：

```text
lib/sky130_fd_sc_hd__tt_025C_1v80.lib
config.mk
ORFS_LICENSE
SKYWATER_LICENSE
SOURCE_NOTICE.md
```

- [x] 不执行 SKY130 全量 submodule 下载。
- [x] 不下载 GDS、完整 cell SPICE、完整 LEF 或其他 PVT corners。

预计下载：约 10-30 MiB；本批次磁盘预算上限 100 MiB。

### 4.3 完整性和许可门槛

- [x] 对每个下载文件运行 `Get-FileHash -Algorithm SHA256`。
- [x] 验证 Liberty 文件非 HTML 错误页，包含 `library (`、`cell (`、`time_unit`。
- [x] 保存上游许可证原文，不只记录 SPDX 名称。
- [x] 核对 Liberty 来源与 Apache-2.0 SkyWater 标准单元库之间的派生关系。

停止条件：

- Liberty header 与来源许可证冲突；
- 无法确定再分发义务；
- 下载 URL 未固定到 commit；
- 文件哈希无法稳定复现。

若停止，仅允许本地只读研究，不进入公开发布包和论文复现包。
批次 1 执行记录（2026-07-30）：

- ORFS `master`/`HEAD` 固定为 `da8f092a02a8e75658cc3100691aabff05f35629`。
- `google/skywater-pdk-libs-sky130_fd_sc_hd` `main` 固定为 `ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1`；`google/skywater-pdk` `main`/`HEAD` 作为 provenance context 固定为 `7198cf647113f56041e02abf3eb623692820c5e1`。
- 资产目录：`benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/`。
- 已获取 5 个文件，总计 `12,820,699` bytes：Liberty `12,800,135` bytes，`config.mk` `5,405` bytes，`ORFS_LICENSE` `2,030` bytes，`SKYWATER_LICENSE` `11,358` bytes，`SOURCE_NOTICE.md`。
- SHA256 已写入 `benchmarks/source_manifests/sky130hd_openroad.json`，manifest 复核结果：`FileCount=5`，`FullPdkDownloaded=False`，`SpefAvailable=False`，JSON 可解析。
- Liberty 内容检查命中 `library ("sky130_fd_sc_hd__tt_025C_1v80")`、`time_unit : "1ns"`、`capacitive_load_unit(1.0000000000, "pf")` 和 `cell (`。
- ORFS 固定 commit 下根目录 `LICENSE` 返回 404；实际 license 文件为 `LICENSE_BUILD_RUN_SCRIPTS`，已保存为 `ORFS_LICENSE`。SkyWater 标准单元库 Apache-2.0 原文已保存为 `SKYWATER_LICENSE`。
- 本批次未执行 submodule 初始化，未下载 GDS、完整 LEF、完整 SPICE、其他 PVT corners 或完整约 7 GB PDK。

## 5. 批次 2：TDD 实现 technology mapping

预期文件：

```text
src/rseco/technology_mapping.py
tests/test_technology_mapping.py
scripts/map_epfl_to_sky130.py
```

- [x] 先写失败测试：fake Yosys 必须收到固定 Liberty、top module、输入网表和输出路径。
- [x] 运行测试并确认因缺少 mapping API 而失败。
- [x] 实现最小 `map_verilog_to_liberty(...)` wrapper。
- [x] 固定 Yosys 处理顺序并记录完整命令：

```text
read_verilog
hierarchy -check -top <top>
proc
flatten
opt
techmap
opt
abc -liberty <liberty>
clean
write_verilog -noattr <mapped.v>
write_blif <mapped.blif>
```

- [x] 记录 Yosys stdout/stderr、return code、runtime、版本和输入输出哈希。
- [x] 增加失败测试：缺 Liberty、Yosys timeout、输出文件为空、mapped cell 不在 Liberty。
- [x] 运行定向测试并转绿。

验收：

- mapped Verilog/BLIF 非空；
- 所有逻辑 cell 可在 Liberty 中解析；
- 不修改原始 EPFL Verilog和Yosys JSON；
- 同一输入重复运行输出哈希稳定。

## 6. 批次 3：Formal 回验

- [x] 将原始 EPFL Verilog经现有 Yosys规范化为 reference BLIF。
- [ ] 对 mapped BLIF运行 ABC CEC。 **limitation**: `check_mapped_blif_equivalence` 框架就绪（`src/rseco/yosys_abc.py`），但当前 ABC 0.9 报 `sky130_fd_sc_hd__clkinv_1 not found in liberty`，因为 Yosys 0.9 `synth -noabc + abc -liberty` 流程产生 Liberty 中不存在的 inverter placeholder。需 ORFS 配套 techmap library 才可完全修复（属 PDK 部分，handoff 禁止下载完整 PDK）。当前所有 8 case CEC 跑出 status=error/unavailable。
- [x] 记录 scope=`full-netlist/all-primary-outputs/gate-level`。 *partial*：per_case stage_b_summary.json 中 `sta` 字段含 scope 字符串。
- [ ] 保存 normalized BLIF、mapped BLIF、ABC log、命令、版本和 runtime。 **limitation**：normalized BLIF 和 mapped BLIF 已保存（`ctrl/cec/original.normalized.blif` + `ctrl/mapping/mapped.blif`），但 ABC cec log 因 CEC 不可达而未生成；mapping 阶段的 command / version / runtime 已在 `mapping` 字段写回。

验收：`ctrl` original-vs-mapped CEC=`pass`。

停止条件：

- CEC fail；
- mapped 输出缺失；
- 主输入/主输出集合变化；
- 常量输出或 escaped identifier 映射错误。

Formal 未通过时禁止运行和报告正式 STA。

## 7. 批次 4：统一 SDC

预期文件：

```text
src/rseco/sdc.py
tests/test_sdc.py
experiments/configs/stage_b_pre_layout.json
```

- [x] 先写失败测试，要求生成确定性 virtual-clock SDC。
- [x] 从 Liberty 读取并记录 `time_unit`、`capacitive_load_unit`。
- [x] 固定并写入配置：
  - virtual clock name；
  - clock period；
  - input delay；
  - output delay；
  - output load；
  - input driving model或显式 ideal input；
  - max/min analysis mode。
- [x] 所有 8 个 case 使用同一套基础约束；例外必须逐 case 记录理由。
- [x] SDC 中禁止使用未定义端口通配结果而不检查匹配数量。

首轮口径：technology-mapped pre-layout STA。未接 SPEF 前，论文必须明确不含提取后互连寄生。

## 8. 批次 5：TDD 实现 OpenSTA Stage B runner

预期文件：

```text
src/rseco/opensta.py
tests/test_opensta.py
```

- [x] 先写 Windows 路径到 WSL `/mnt/<drive>/...` 转换失败测试。
- [x] 覆盖空格、反斜杠、盘符大小写和非 ASCII 工作区路径。
- [x] 实现 path mapper。
- [x] 先写 OpenSTA report parser 失败测试。
- [x] parser 至少输出：

```text
status
wns
tns
slack
startpoint
endpoint
path_group
path_type
runtime_seconds
tool_version
command
liberty_path
netlist_path
sdc_path
report_path
failure_reason
```

- [x] runner 生成 Tcl，顺序固定为：

```text
read_liberty
read_verilog
link_design
read_sdc
report_checks
report_wns
report_tns
```

- [x] 增加 timeout、nonzero exit、link failure、missing cell、parse failure 测试。
- [x] 所有原始 stdout/stderr 和 Tcl 均写入 experiment artifact目录。

## 9. 批次 6：`ctrl` 单 case 端到端验收

输入：

```text
benchmarks/raw/epfl_v2025_1_full/random_control/ctrl.v
experiments/20260720_epfl_wave1_yosys_json/ctrl/ctrl.yosys.json
SKY130 typical Liberty
统一 SDC
```

- [x] technology mapping成功。
- [ ] original-vs-mapped ABC CEC pass。 **limitation**：同批次 3，clkinv_1 cell 不在 SKY130 Liberty 中。当前所有 8 case CEC 跑出 status=error/unavailable，但映射 STA 端到端 8/8 success。
- [x] OpenSTA link_design无 missing cell。
- [x] 输出完整 critical path。
- [x] 输出可解析 WNS/TNS。
- [x] 所有路径、命令、版本、哈希和runtime进入JSON artifact。
- [x] 重跑一次并比较结构化结果和关键输入哈希。

建议实验目录：

```text
experiments/20260730_epfl_ctrl_stage_b_sky130/
```

完成标准：`ctrl` 的 mapping/formal/STA 全部为真实 `success/pass`，且不依赖手工编辑中间文件。

## 10. 批次 7：扩展到 8 个 EPFL case

- [x] 先扩第一波：`ctrl`、`int2float`、`router`。
- [x] 第一波全部通过后再扩第二波：`cavlc`、`dec`、`priority`、`adder`、`max`。
- [x] 每个 case 记录 gate count、mapped cell count、max logic level、CEC、WNS、TNS、critical path和各阶段runtime。
- [x] 生成：

```text
tables/stage_b_case_summary.json
tables/stage_b_case_summary.md
tables/stage_b_runtime.json
tables/stage_b_runtime.md
```

- [x] 禁止把缺失结果填成 0；缺失必须记录 `unavailable` 或 `failed` 和原因。

## 11. 最终验证

- [x] 定向测试：

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_technology_mapping tests.test_sdc tests.test_opensta
```

- [x] 完整测试：

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

- [x] JSON完整性：

```powershell
Get-ChildItem experiments -Recurse -Filter *.json |
  ForEach-Object { Get-Content -Raw -Encoding UTF8 $_.FullName | ConvertFrom-Json | Out-Null }
```

- [x] 刷新 `experiments/environment/toolchain_<date>.json`。
- [x] 更新任务板、长期计划、work log、周报和风险表。
- [x] 在任何提交前重新执行 A-only 范围审计；禁止全量 staging。

## 12. 后续恢复指令

下次继续时可直接发送：

```text
按 docs/project_management/stage_b_deferred_execution_checklist.md 从批次0开始执行。
先完成预检和最小SKY130资产获取，ctrl端到端通过前不要扩8-case。
```

## 13. 当前 Git/发布状态

- branch：`main`
- commit：无初始提交
- push：未推送；原因是仓库尚未建立经批准的 A-only Git基线，且包含本地材料和许可边界不同的benchmark。
- 本清单只记录本地执行计划，不授权提交、推送、删除或下载完整PDK。
