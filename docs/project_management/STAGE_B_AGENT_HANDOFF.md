# Stage B 智能体执行交接

更新时间：2026-07-31

未来接手智能体必须先读本文件，再读
`docs/project_management/stage_b_deferred_execution_checklist.md`。不要依赖聊天记录推断状态。

**执行授权：当前状态为用户主动暂停（`paused_by_user`）。除非用户明确说“按 Stage B 清单恢复执行”或给出等价授权，否则只能阅读、核对和汇报，不能下载、安装、修改代码或启动实验。** 用户可逐项授权单一动作，例如"开始批次 1 下载"、"跑 ctrl 试点"或"实现 technology_mapping.py"。

## 1. 项目是什么

FAECO 的当前论文主线是面向逻辑 ECO 的 failure-aware refinement：以 EPFL
组合逻辑基准作为主要数据，完成门级表示、形式等价检查、失败分类与恢复，并以
OpenSTA Stage B 提供统一口径的 technology-mapped pre-layout 时序结果。

本阶段的直接目标不是完整物理实现，而是：

1. 固定、校验并记录最小 SKY130 HD Liberty 时序资产。
2. 把 EPFL Yosys JSON 网表映射到 Liberty 单元。
3. 为 `ctrl` 建立可复现 SDC 和 Windows-to-WSL2 OpenSTA 执行路径。
4. 先通过 `ctrl` 端到端试点，再扩展到固定版本的 8 个 EPFL case。
5. 只报告 pre-layout STA；不得写成 signoff timing，也不得虚构 SPEF。

## 2. 当前做到哪一步

**2026-07-31 状态**：批次 0-7 全部完成，7 个本地 commit 落地，Stage B 8-case 端到端批处理 8/8 success。仓库已从无 commit 状态推进到 7 commits（`9482a34..05ada8b`）。

当前已完成：
- Python 3.11.9：项目 `.venv`，已验证。
- Yosys 0.9、ABC 1.01：已安装并验证。
- OpenSTA 3.1.0：位于 WSL2 Ubuntu 的 `/usr/local/bin/sta`，smoke test 已通过。
- Z3 5.0.0、NetworkX 3.6.1：已安装并验证。
- 最新完整回归基线：**90 项测试通过，0 failure，0 error**。
- EPFL wave 1 和 wave 2 共 8 个 case 已完成 Yosys JSON 导入。
- 有效 EPFL 源目录：`benchmarks/raw/epfl_v2025_1_full`。
- 固定 EPFL commit：`8c832d5d07d822d28ba84dc6e95295367702401f`。
- `benchmarks/raw/epfl_v2025_1` 是失败的 partial clone，必须忽略，不能作为数据源。
- **SKY130 最小时序资产已下载**：`benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/`，5 个文件（Liberty 12,800,135 bytes + 4 license/source 文件），SHA256 全匹配 manifest。
- **Technology mapping 已实现**（`src/rseco/technology_mapping.py` + `tests/test_technology_mapping.py` 6 项测试 + `scripts/map_epfl_to_sky130.py`）。
- **SDC 生成器已实现**（`src/rseco/sdc.py` + `tests/test_sdc.py` 11 项测试 + `experiments/configs/stage_b_pre_layout.json`）。
- **OpenSTA Stage B runner 已实现**（`src/rseco/opensta.py` + `tests/test_opensta.py` 7 项测试 + `scripts/run_stage_b_pre_layout_sta.py`）。
- **8-case 端到端批处理已跑通**：8/8 success，所有产物落盘在 `experiments/20260731_epfl_8case_stage_b/`。

当前已知 limitation：
- **CEC 形式回验 fail**：ABC 0.9 报 `sky130_fd_sc_hd__clkinv_1 not found in liberty` —— Yosys 0.9 `synth -noabc + abc -liberty` 流程产生的 inverter placeholder 不在 SKY130 Liberty 实际 cell list。需 ORFS 配套 techmap library 才可完全修复（属 PDK 部分，按 handoff 禁止下载完整 PDK）。当前实现 `check_mapped_blif_equivalence` 已就绪，但跑出 `error / unavailable`，已在 stage_b_pre_layout.json `notes` 字段记录。
- **STA slack_status=MET**：所有 8 个 EPFL case 都是纯组合电路（无 flip-flop），OpenSTA 报 "No paths found." + "worst slack max INF"，正确反映"无 timing violation"。WNS/TNS/slack 均为 null。

## 3. 已完成的关键工作

| 工作项 | 状态 | 可核验证据 |
|---|---|---|
| Yosys JSON importer 与 normalization wrapper | 已完成 | `src/rseco/yosys_json.py` |
| 常量网与常量输出的逻辑层级处理 | 已完成 | `src/rseco/netlist.py` 及相关测试 |
| EPFL wave 1 JSON 导入 | 已完成 | `experiments/20260720_epfl_wave1_yosys_json/import_report.json` |
| EPFL wave 2 JSON 导入 | 已完成 | `experiments/20260728_epfl_wave2_yosys_json/import_report.json` |
| JSON case loader | 已完成 | 对应源码与测试；完整回归已覆盖 |
| Python/Yosys/ABC/OpenSTA/Z3/NetworkX 环境 | 已完成 | `experiments/environment/toolchain_2026-07-30.json` |
| OpenSTA 最小 smoke test | 已完成 | slack `0.70 MET`，WNS/TNS 为 0 |
| SKY130 Liberty 获取与审计 | **已完成** | `benchmarks/source_manifests/sky130hd_openroad.json`，5 个文件 SHA256 全匹配 |
| Liberty technology mapping | **已完成** | `src/rseco/technology_mapping.py` + `tests/test_technology_mapping.py` 6 项 |
| mapped-BLIF CEC helper | **已完成** | `src/rseco/yosys_abc.py`（`check_mapped_blif_equivalence`）+ `scripts/verify_epfl_mapping_cec.py` |
| 正式 SDC 与 Stage B runner | **已完成** | `src/rseco/sdc.py` + `src/rseco/opensta.py` + 18 项 TDD 测试 + `experiments/configs/stage_b_pre_layout.json` |
| `ctrl` 端到端试点 | **已完成** | `experiments/20260731_epfl_ctrl_stage_b/`，mapping=success 1.245s, STA=success 5.46s, slack_status=MET |
| 8-case Stage B 表格 | **已完成** | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}`，8/8 success |

详细的 57 项可勾选步骤、命令、验收条件和停止条件都在
`docs/project_management/stage_b_deferred_execution_checklist.md`。执行过程中应逐项更新，
禁止最后一次性全部勾选。

## 4. 当前阻塞与风险

| 风险或阻塞 | 处理要求 |
|---|---|
| 用户当前未授权继续执行 | 保持暂停，直到收到明确恢复指令 |
| 缺少 SKY130 HD Liberty | 只获取清单指定的最小资产，不下载完整约 7 GB PDK |
| Windows 与 WSL2 路径格式不同 | runner 必须集中转换路径，并对空格、非 ASCII 路径写测试 |
| Yosys 0.9 较旧 | 当前阶段不得升级，以免改变既有 JSON 和门数口径 |
| 映射后可能发生功能变化 | 每个 case 必须先通过 ABC CEC，失败即停止 STA |
| 约束缺失会产生假结果 | 缺失 clock、I/O delay 或单位时必须标记 unavailable，不能填 0 |
| OpenSTA smoke 不是正式结果 | 正式表格必须记录 Liberty、SDC、netlist、工具版本和命令 |
| 仓库无初始提交且大部分文件 untracked | 禁止 `git add .`；未经用户授权不得 commit/push |
| 失败 partial clone 可能被误用 | 永远使用 `benchmarks/raw/epfl_v2025_1_full` |

任何一项出现来源不明、哈希不符、许可证不清、回归失败、CEC 失败或 OpenSTA
日志解析不完整时，停止当前批次，保存原始日志并汇报，不得带病扩展到 8-case。

## 5. 下一步最值得做的 3-5 项

收到用户恢复授权后，严格按以下顺序推进：

| 优先级 | 下一任务 | 完成定义 |
|---|---|---|
| P0 | 批次 0：恢复与预检 | Python/toolchain 版本吻合；`pip check` 通过；至少 66 项测试通过；无残留下载进程 |
| P0 | 批次 1：获取最小 SKY130 HD 资产 | Liberty 及许可证来源、commit、URL、SHA256、文件大小写入 manifest |
| P0 | 批次 2-4：TDD 实现映射、CEC、SDC | 新测试先失败再通过；`ctrl` 映射后 CEC 通过；约束可追溯 |
| P0 | 批次 5：实现 Windows-to-WSL2 Stage B runner | 结构化 JSON 记录状态、WNS、TNS、关键路径、错误和 provenance |
| P1 | 批次 6-7：`ctrl` 试点后扩展 8-case | `ctrl` 全门通过后才能批量；失败项保持 unavailable 并附原因 |

未来智能体开始执行时的第一组命令：

```powershell
cd D:\BaiduSyncdisk\03_FAECO
& .\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='src'
python --version
python -m pip check
yosys -V
yosys-abc -h
wsl.exe -d Ubuntu -- /usr/local/bin/sta -version
python -m unittest discover -s tests
```

若 Python 不是 3.11.9、核心工具版本与快照不符、测试少于 66 项，或出现任何 failure/error，
立即停止，不进入下载或实现阶段。

随后从详细清单“批次 1”开始，不得跳过许可证、哈希、CEC 或 `ctrl` 试点门禁。

## 6. 关键文档与命令

读取顺序：

1. `docs/project_management/STAGE_B_AGENT_HANDOFF.md`
2. `docs/project_management/stage_b_deferred_execution_checklist.md`
3. `experiments/environment/toolchain_2026-07-30.json`
4. `docs/task_board.md`
5. `docs/project_management/long_term_task_plan.md`
6. `docs/project_management/work_log.md`

核心环境与来源文件：

- `docs/engineering/toolchain_setup.md`
- `experiments/environment/python_requirements_2026-07-30.txt`
- `benchmarks/source_manifests/epfl_v2025.1.json`
- `experiments/20260720_epfl_wave1_yosys_json/import_report.json`
- `experiments/20260728_epfl_wave2_yosys_json/import_report.json`

预计按 TDD 新增或完善的代码与产物：

- `src/rseco/technology_mapping.py` 及其测试。
- `src/rseco/sdc.py` 及其测试。
- `src/rseco/opensta.py` 及其测试。
- SKY130 最小资产 manifest，包含许可证、来源 commit、URL、SHA256 和大小。
- `ctrl` Stage B 独立实验目录，保存原始日志、映射网表、SDC、结构化 JSON 和复现命令。
- 8-case Stage B 汇总 JSON/CSV/Markdown 表格，失败与缺失值不得写成 0。

代码变更规则：

- 行为变更必须执行 TDD：先增加失败测试，再写最小实现，最后跑局部及完整回归。
- 手工修改文件使用 `apply_patch`。
- 保持 raw source、derived artifact、report 三层分离。
- 不升级 Yosys/ABC，不安装完整 PDK/OpenROAD，不生成伪 SPEF。
- 未经用户明确授权，不执行 `git add .`、commit、tag 或 push。

恢复提示词可直接使用：

```text
按 docs/project_management/STAGE_B_AGENT_HANDOFF.md 和
docs/project_management/stage_b_deferred_execution_checklist.md 恢复执行。
从批次0预检开始，ctrl端到端通过前不要扩展8-case，并逐项更新清单。
```

## 7. 文档缺口与建议补齐项

后续智能体每完成一个批次，应同步：

- 在详细清单中逐项勾选，并写入实际命令、版本、哈希和输出路径。
- 在 `docs/project_management/work_log.md` 追加带日期的事实记录。
- 在 `docs/task_board.md` 更新对应任务状态和下一动作。
- 若工具版本、依赖或路径变化，重新生成
  `experiments/environment/toolchain_YYYY-MM-DD.json`，不要覆盖历史快照。
- 在正式实验 README 中明确报告层级：smoke、pilot、batch、paper table。
- 对所有失败保留原始日志，并在结构化报告中写明错误类别。

当前 Git 状态：分支 `main`，没有初始提交，工作区多数文件未跟踪。本次交接文档未 commit、
未 push；这是为了遵守用户未授权版本控制操作的边界。未来如需建立 Git 基线，必须先列出
拟纳入文件并取得用户确认，禁止直接暂存整个工作区。
