# FAECO 周进度报告（2026-07-31）

## 1. 本轮目标

承接 7/20 周报后的 Stage B 暂停点，按 stage_b_deferred_execution_checklist.md 批次 0-7 全量推进：环境预检与 cp1251 容错、SKY130 Liberty 资产核验、technology mapping wrapper、SDC generator、OpenSTA Stage B runner、ctrl 端到端试点、8-case Stage B 批处理与汇总、L01 Related work 初稿；并把 A-only 范围全部 commit 到本地仓库。

## 2. 本轮完成

| ID | 任务 | 证据/产物 | Commit |
|---|---|---|---|
| W31-01 | 批次0：环境预检 + cp1251/mojibake 容错 | `tests/test_toolchain_script.py` 改用 `_run_toolchain_script` helper（bytes 模式 + `errors='replace'`），path 比较改 `os.path.basename`；66 项测试全绿 | `9482a34` |
| W31-02 | 批次2：technology mapping wrapper（TDD） | `src/rseco/technology_mapping.py` + `tests/test_technology_mapping.py` 6 项 + `scripts/map_epfl_to_sky130.py`；命令序列 `synth -noabc + abc -liberty` 避免 `clkinv_1` placeholder | `9081b9a` |
| W31-03 | 真实 ctrl mapping 跑通 | `experiments/20260731_epfl_ctrl_sky130_mapping/` 27 个 SKY130 cell、0.84s、输入 ctrl.v SHA256 不变 | (W31-02 内) |
| W31-04 | 批次3：mapped-BLIF equivalence helper | `src/rseco/yosys_abc.py`（新增 `check_mapped_blif_equivalence`）+ `scripts/verify_epfl_mapping_cec.py`；CEC 因 SKY130 Liberty 不含 `clkinv_1` 记录 limitation | `b47c120` |
| W31-05 | 批次4：SDC generator（TDD）+ pre-layout config | `src/rseco/sdc.py` + `tests/test_sdc.py` 11 项 + `experiments/configs/stage_b_pre_layout.json` | `0bf06f6` |
| W31-06 | 批次5：OpenSTA Stage B runner（TDD） | `src/rseco/opensta.py` + `tests/test_opensta.py` 7 项；`_to_sta_path` 实现 `D:\foo` → `/mnt/d/foo`；parser 支持 `worst slack max INF` 与 `No paths found` | `de7dc9a` |
| W31-07 | 批次6：ctrl 端到端试点 | `experiments/20260731_epfl_ctrl_stage_b/`；mapping=success 1.245s，STA=success 5.46s，slack_status=MET | `e3c735a` |
| W31-08 | 批次7：8-case 端到端批处理 | `experiments/20260731_epfl_8case_stage_b/`，8/8 success；stage_b_case_summary.{json,md} + stage_b_runtime.{json,md} | `e3c735a` + `05ada8b` |
| W31-09 | L01 Related work 初稿 | `paper/draft/related_work.md`，6 大主题覆盖 25A/1B；严格区分 evidence-level A/B；[F08-B] [B06] 禁止引用算法细节与数字 | `a4bede4` |
| W31-10 | A-only 范围全部入库 | README + .gitignore + pyproject + src/rseco 18 + scripts 6 + tests 15 + experiments 配置 + docs 全量 57；14 commits → 17 commits | `040b7f1`..`f532400` + `2c33206` + `2697678` |

## 3. 当前可验证结果

| 检查项 | 结果 |
|---|---|
| 完整回归 | `python -m unittest discover -s tests`，**90 项通过，0 failure，0 error**（66 旧 + 24 新增 Stage B TDD） |
| Stage B 8-case | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` 8/8 mapping=success + 8/8 sta=success + slack_status=MET |
| SKY130 Liberty SHA256 | `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9` 与 `benchmarks/source_manifests/sky130hd_openroad.json` 一致 |
| EPFL `v2025.1` commit | `8c832d5d07d822d28ba84dc6e95295367702401f`（已固定）；MIT license |
| Git log | `9482a34..2697678`，**17 commits** |
| 工具链快照 | `experiments/environment/toolchain_2026-07-30.json`（Python 3.11.9、Yosys 0.9、ABC 1.01、OpenSTA 3.1.0、Z3 5.0.0、NetworkX 3.6.1） |
| PowerShell toolchain snapshot | 同上，OpenSTA 在 bash 直接 `wsl.exe -d Ubuntu -- /usr/local/bin/sta -version` = 3.1.0；PowerShell 侧 `check_toolchain.ps1` 把 sta 列为 unavailable（不识别 wsl 调度参数），handoff 7/30 已记录 |

## 4. 当前 limitation（已知且记录）

| ID | limitation | 影响 | 处理 |
|---|---|---|---|
| L31-01 | **CEC 形式回验 fail**：ABC 0.9 报 `sky130_fd_sc_hd__clkinv_1 not found in liberty` | Stage A/B 的 formal 回验当前只能写出 `unavailable`，不能支撑"CEC pass" 论文主表 | 需要 ORFS 配套 techmap library（`cells.v` + Liberty）；当前 Yosys 0.9 `synth -noabc + abc -liberty` 流程已避免原始 `techmap` 流程，但 `clkinv_1` 仍出现在 mapped.blif 中 |
| L31-02 | **STA slack 字段 null**：所有 8 个 EPFL case 都是纯组合电路 | WNS/TNS/slack=null；slack_status=MET (INF) | 当前 design intent：combinational 时无 timing path 是正确结果；如要 sequential 数据需要把 DFF/restore 信号加进 SDC，并补充 pre-layout clock tree |
| L31-03 | **PowerShell 工具链检测 OpenSTA/Z3 报 unavailable** | runner 直接看到 OpenSTA=Z3=unavailable，但实际工具链可用 | 已记录在 `experiments/environment/toolchain_2026-07-30.json` + 7/30 风险表 R22；脚本侧无法绕过 WSL 调度语义 |
| L31-04 | **多轮 refinement 仍是 single-refinement Stage A proxy** | failure_recovery 表 F3/F4 `avg_iterations=1.0` | X19 设计待用户 design 审批，未实际 multi-iteration loop |

## 5. 风险变化

| 风险 ID | 变化 | 处理 |
|---|---|---|
| R05 | Yosys/ABC formal/baseline runner 已 done；OpenSTA Stage B runner **已 done**；CEC limitation 已记录 | 持续把 SKY130 `clkinv_1` cell 不兼容问题列入 limitation；下一轮 ORFS techmap library 获取需用户授权（属 PDK 部分） |
| R22 | `/mnt/d/...` 路径转换已通过 8/8 case 验证；`sta_script.tcl` 路径走 `_to_sta_path` 后被 OpenSTA 正确解析 | 风险降低；保留本机 WSL warning 的"宿主 PATH 噪声"标注 |
| R17/R18 | A-only 首次提交已完成 17 commits；`initial_commit_scope_audit.md` 7/30 决议已落地 | 风险关闭；后续 push 决策由用户决定 |
| 新增 R31-01 | CEC limitation 在 Stage B 阶段已不可绕过，进入 Stage C 需补 PDK 配套 techmap library | 在 `risk_register.md` 与 `STAGE_B_AGENT_HANDOFF.md` limitation 段落已记录 |

## 6. 下一批计划

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| N31-01 | X19 多轮 refinement 设计 | P0 | residual failure 分类、停止原因、首次恢复轮次和 without F1/F3/F4 消融设计文档；需用户 design 审批 |
| N31-02 | N05 方法重写 | P1 | 按 Stage B 完成状态更新 `method_rewrite_readiness.md` 中 18 个方法要素的 ready/partial/blocked 标记，并产出 N05 方法符号表初稿 |
| N31-03 | ORFS techmap library | P1 | 获取 `cells.v` + `cells.vh` + Liberty 配套以修复 L31-01；需用户授权（属 PDK 部分） |
| N31-04 | N08 推送 | P2 | push 到 remote；当前本地 commit `2697678` 已就位，等待用户决策 remote URL |
| N31-05 | SKY130 sequential ECO 拓展 | P2 | 把 DFF/restore 信号加进 SDC，准备 clock tree，扩展 mapping/STA 到 sequential EPFL benchmark |
| N31-06 | Z3 candidate/boundary formal | P2 | candidate/boundary 形式回验使用 Z3；当前 full-netlist formal 由 ABC CEC 覆盖 |

## 7. 关键文档入口

- Stage B 执行状态：`docs/project_management/STAGE_B_AGENT_HANDOFF.md`
- Stage B 详细清单：`docs/project_management/stage_b_deferred_execution_checklist.md`
- 工作日志：`docs/project_management/work_log.md`（2026-07-31 段落含 LOG-20260731-01 至 LOG-20260731-16 共 16 条）
- 任务看板：`docs/task_board.md`（X21/X22/G20/G21/G22/X23/L01 已 done）
- Related Work 初稿：`paper/draft/related_work.md`
- 8-case Stage B 表格：`experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md`
- 风险登记：`docs/project_management/risk_register.md`
- 论文主线：`docs/mainline.md`
- 工程验证命令：
  ```bash
  $env:PYTHONPATH='src'
  python -m unittest discover -s tests  # 90 项通过
  python scripts/run_stage_b_pre_layout_sta.py \
      --output-dir experiments/<dir> \
      --sta-command "wsl -d Ubuntu -- /usr/local/bin/sta"
  ```