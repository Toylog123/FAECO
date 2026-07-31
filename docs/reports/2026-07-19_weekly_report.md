# FAECO 周进度报告（2026-07-14 至 2026-07-19）

## 1. 本周目标

围绕 FAECO 主线完成可执行的组合逻辑实验原型：建立最小 case、cut/refinement/ranking/replacement 闭环，扩展到多电路 batch，并形成可追溯的 baseline、runtime、failure recovery 和工具链记录。

## 2. 本周完成

| 方向 | 完成内容 | 主要产物 |
|---|---|---|
| 工程骨架 | 初始化 Python 工程、测试、case schema、parser、cone extraction 和 metrics flow | `src/rseco/`、`tests/`、`data/cases/minimal/` |
| FAECO 原型 | 实现 failure-aware refinement、weighted s-t cut、deterministic ranking 和 cone-level replacement | `refinement.py`、`cut.py`、`ranking.py`、`replacement.py` |
| 多 case 实验 | batch 覆盖 c17 N22/N23、c432、c499、c880 共 5 个 case | `experiments/20260718_minimal_combinational_batch_demo/` |
| Baseline | 接入 fixed、seeded random、size-only、critical-path-only proxy、ABC wrapper 和 FAECO selected 对比 | `tables/baseline_comparison.json/md` |
| 验证与环境 | 区分 structural signature 与 ABC formal wrapper，归档工具路径、版本和可用性 | `formal_equivalence`、`environment/toolchain_snapshot.json` |
| Runtime 与恢复 | 建立结构化 runtime stages、batch runtime 表和 failure recovery Stage A proxy 表 | `tables/runtime_breakdown.*`、`tables/failure_recovery.*` |
| 工具链推进 | 安装 Yosys 0.9 / UC Berkeley ABC 1.01，验证去 BOM + Yosys `simplemap` BLIF + ABC `cec` 路径 | c17/c432 smoke 均报告 equivalent |
| OpenSTA 安装就绪审计 | 固定官方 commit/license/Ubuntu 24.04 recipe，比较 Windows/WSL2/Docker 路径；推荐 WSL2 固定源码构建，但未安装或接入 runner | `readiness_summary.json` SHA256 `2198CBD5...70CEB0`、`toolchain_setup.md`、X22、R22 |
| X18 隔离设计探针 | 5-case 全网表 pair CEC、ABC baseline 和 baseline 回验均成功；定位缺失 `abc.rc`/`resyn2` alias 与 optimized Verilog 0-gate parser 问题 | `tmp/x18_full_netlist_probe_20260719_03/`、`toolchain_setup.md`、R20 |
| 实验隔离 | 修复 runner 把 fake ABC 输出写回输入 case 的副作用 | runner 只向实验 `raw_results` 写运行产物 |
| 论文证据审计 | 完成旧稿 16 页 PDF/DOCX 页级核验，定位 C01-C12、式(1)-(20)、图1-9和表1-5 | `legacy_source_locator.md`、更新后的 claim/formula audit |
| 方法重写就绪审计 | 将目标算法逐项反校到代码和实验字段，标记 1 个 ready、8 个 partial、9 个 blocked 方法要素，并固定旧稿公式处置和禁写 claim | `method_rewrite_readiness.md`、更新后的算法/taxonomy 状态说明、R19 |
| Benchmark 来源治理 | 固定 EPFL `v2025.1` MIT 主来源、8 个 Verilog/官方 BLIF blob，并限制当前 ISCAS85 为本地 smoke | `benchmark_source_and_license_audit.md`、`benchmarks/source_manifests/` |
| EPFL 导入就绪探针 | 8/8 Yosys 规范化成功、8/8 对同 tag 官方 BLIF CEC pass、stats 全部一致；同时定位权威内部格式缺口 | `tmp/x21_epfl_readiness_probe_20260719_01/`、X21、R21 |
| Related Work 证据 | 核验 25 篇 A 级全文和 1 条 B 级官方证据；DAC 2006 SAT Sweeping 已升级为 A，DAC 2018 经 OA API、NTU、作者站点和归档资产复核后仍无合法公开全文，保持 B | `core_paper_notes.md`、`literature_matrix.md`、`source_manifests/` |
| 总任务日志审计 | 清理任务看板中已由后续工作完成的旧“下一步动作”，统一当前依赖到 X18/X19/X21；PM22 修正为 `in_progress/P0` | `task_board.md`、`long_term_task_plan.md`、`future_task_backlog.md` |
| Git 首次基线审计 | 当前 241 个未忽略候选分为 A 核心 135、B 本机 smoke/不可移植产物 51、C 私有/版权材料 55；确认无 remote、无 LICENSE、Git 身份仍为占位值 | `initial_commit_scope_audit.md`、R17、N08 |

## 3. 当前可验证结果

| 检查项 | 结果 |
|---|---|
| 单元测试 | 47 项通过 |
| single-case demo | 成功刷新 |
| batch case count | 5 |
| FAECO selected patch | 5 个 case 均选择 `size_refined_cut` |
| structural equivalence | 5 个 case 均为 `pass`，仅表示结构签名一致 |
| formal equivalence | 正式 batch 仍为 `unavailable`，尚未接入 `yosys-abc` 规范化链路 |
| ABC baseline | 正式 batch 仍为 `unavailable`，尚无可引用的 optimized netlist 指标 |
| X18 隔离探针 | 5/5 pair CEC pass、5/5 baseline success、5/5 baseline CEC pass；scope 为全网表全部主输出，且不是正式 runner/candidate formal |
| failure recovery | F3/F4 proxy recovery rate 为 1.000，`avg_iterations=1.0` 来自单次 refinement proxy |
| 工具链快照 | Python 3.11.9、NetworkX 3.4.2、Yosys 0.9 可用；ABC/OpenSTA/Z3 尚未进入正式 batch |
| OpenSTA readiness | WSL2 Ubuntu 24.04 缺失依赖均有 apt candidate；Docker daemon 未运行，Windows 原生依赖不全；`opensta_installed=false` 且无 WNS/TNS |
| 旧稿一致性 | Word 字段更新证明原式(16)-(20)应改为(15)-(19)；确认图6误引，且表2正文/Avg/逐行均值/slack 反算四套统计不一致 |
| 核心文献证据 | 25 篇全文为 A 级；DAC 2006 SAT Sweeping 已通过归档的 Cadence Labs 正确全文升级为 A，DAC 2018 cost-aware multi-target 仍为 B 级官方证据 |
| 文献与 JSON 一致性 | 53 个 JSON 全部可解析；`core_paper_notes.md` 条目计数为 25A/1B，SAT 正确核验 PDF 的 6 页与 SHA256 同 source manifest 一致 |
| 任务日志一致性 | 任务看板 59 行均为 6 字段，状态为 54 done/5 in_progress/0 pending；长期计划 33 行均为 7 字段，状态为 18 done/5 in_progress/10 pending；风险表 22 行无重复 ID |
| 方法实现边界 | 方法矩阵共 18 项；完整 Method 仍为 pending，真实 boundary closure、patch synthesis、多轮循环、candidate-level formal/STA 和公开主实验仍受阻 |
| Git 提交状态 | staged 文件 0、remote 0、仓库 LICENSE 0；`tmp/` 和 Python cache 已忽略，未执行提交 |
| A-only dry-run | 135 个源路径全部复制，SHA256 `6C15C13F...11479F`；隔离副本 47 项测试、single demo 和 2-case c17 batch 通过 |
| A-only 静态卫生 | 凭据/私钥、非法 UTF-8、冲突标记、尾随空格、大小写碰撞、超长路径和 Office/PDF 二进制均为 0；COMMIT-10 通过 |

## 4. 本周判断

当前证据可以支持“FAECO 的组合逻辑原型、5-case 批处理、实验记录结构和多 baseline 接口已经形成”。当前证据不能支持“已完成 5-case ABC/SAT 形式化验证”“ABC baseline 已产生真实优化收益”“critical-path-only 使用真实 STA 路径”或“已获得多轮 failure recovery 统计”。

## 5. 风险与处理

| 风险 | 当前影响 | 处理方向 |
|---|---|---|
| ABC 1.01 直读现有 Verilog 不稳定 | c17 ANSI 声明断言，c432 多行 module/BOM 读取失败 | 固化去 BOM + Yosys BLIF 规范化，再调用 ABC |
| OpenSTA 未安装且跨系统路径未设计 | 无真实 WNS/TNS 和 critical path；WSL 可构建不等于 runner 已接入 | 按 X22 固定 commit/CUDD 哈希，通过最小 STA smoke，再测试 Windows-WSL 的 Liberty/Verilog/SDC/report 路径转换 |
| c432/c499/c880 license 未声明 | 当前 5-case batch 不能作为论文主集或可再分发包 | 已固定 EPFL `v2025.1` MIT 替代源；待完成导入和主表迁移 |
| EPFL 尚无获批权威内部格式 | 8 个原始 Verilog及第一波 noexpr 导出在当前 parser 中仍为 0 gates | 在 BLIF、Yosys JSON、确定性 simple-gate Verilog 中完成设计审批，再创建正式 case |
| failure recovery 仍为 proxy | 不能形成多轮恢复结论 | 实现真正 refinement loop 与 ablation |
| Git 尚无初始提交 | 缺少版本回退基线 | 明确原始材料纳入策略后创建首个提交 |
| 全量 staging 会纳入私有/版权材料 | 约 94.08 MiB 的旧稿、课题和文献材料会永久进入历史，另有 51 个许可不完整或不可移植的本机 artifact | 禁止 `git add .`；采用已通过 dry-run 的 A-only 工程核心范围并审计 staged diff |
| 行尾策略尚未固定 | 当前 A 类有 116 个 LF-only、8 个 mixed、11 个 CRLF-only 和 16 个 BOM 文件；`core.autocrlf=true` 可能在首次 staging 时隐式归一化 | 首次提交前确认 `.gitattributes`，当前不做无授权批量改写 |
| 旧稿数据和编号不一致 | 不能直接引用 B&G/RSECO 均值或沿用原编号 | 已完成复算；FAECO 新稿删除旧均值，并将后五式统一重编号为(15)-(19) |
| SAT Sweeping 文献库 PDF 错配 | 按文件名引用会产生事实性错误 | manifest 已固定归档正确全文与两个 SHA；错配文件继续禁引，正确核验缓存不提交、不再分发 |
| DAC 2018 cost-aware multi-target 无公开全文 | 不能核验算法细节、复杂度和实验数字 | OpenAlex/Semantic Scholar/Crossref、NTU、作者站点和归档资产均已复核；继续只使用正式书目、摘要与 ICCAD 2017 问题规范 |
| BUFFALO 未公开本体 artifact 且数值叙事不一致 | 不能复现模型/数据/商业闭环，也不能照抄 77.7%/83x 为 full-chip 总结 | 只按 Table IV 写最大 71.10% TNS，83x 限定为代表性单网；该工作只进入 discussion |
| ML timing 结果口径容易被过度外推 | 4154x 不是 STA-vs-STA，130-nm 到 7-nm transfer 也不是零目标数据或任意节点泛化 | source manifest 固定比较阶段、训练切分和未公开 artifact；只用于表示/泛化讨论，不替代 FAECO formal/STA/runtime |
| 目标算法文档领先于实现 | 容易把 `equivalence_map`、boundary closure、patched netlist、多轮 recovery 和停止条件误写成当前能力 | 算法/taxonomy 已标为目标规范；方法章节以代码、实验产物和 readiness matrix 为准 |
| `resyn2` alias 与 baseline 指标不可移植 | 当前 ABC 包缺少 `abc.rc`；optimized Verilog 的 assign/LUT 又使轻量 parser 返回 0 gates | 使用 `-s` 和固定官方 alias 展开；baseline node/level 从 ABC `print_stats` 提取，BLIF 作为权威产物 |

## 6. 下周优先任务

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| WN01 | 接入 `yosys-abc` 自动检测与版本采集 | P0 | snapshot 正确记录 UC Berkeley ABC 命令、路径、版本和 `-s` 启动策略 |
| WN02 | 接入 Yosys-BLIF 规范化 formal/baseline | P0 | formal scope 获批后，5-case 产生真实 ABC 状态、BLIF、stats、日志和 runtime |
| WN03 | 实现多轮 refinement 与消融配置 | P0 | failure recovery 从 single-refinement proxy 升级为真实迭代统计 |
| WN04 | 落实旧稿硬伤修订和 FAECO 方法定义重写 | P0 | 就绪审计已完成；待 X18/X19/X21/X22 关闭阻塞后，修正式(15)/图6/表2问题，并形成与实现一致的符号和公式 |
| WN05 | 导入 EPFL 第一波 benchmark | P0 | 来源/官方 BLIF CEC 已就绪；批准权威格式后，使 ctrl/int2float/router 的 MIT notice、case、formal 和日志完整 |
| WN06 | 形成 Related Work 第一版证据化段落 | P1 | 写作结构获批后，以 25A/1B 证据按问题设置分组写作；DAC 2018 保持 B 级边界并定期复核，不阻塞初稿 |
| WN07 | 建立 Git 首次可回退基线 | P0 | A-only dry-run/静态卫生已通过；确认真实 Git 身份、发布属性和行尾策略后精确 staging，B/C 类不进入可推送历史 |
| WN08 | 安装并接入 OpenSTA Stage B | P0 | 批准 WSL2 路径后固定 OpenSTA/CUDD，`sta -version` 与最小 Liberty/Verilog/SDC smoke 通过，runner 记录 WNS/TNS、critical path、runtime 和路径映射 |

## 7. 组会一句话结论

本周完成了 FAECO 从单 case 到 5-case、多 baseline、可追溯 runtime/环境/恢复表的组合逻辑原型，收口旧稿页级审计和方法重写就绪审计，并把 Yosys-BLIF-ABC 探针扩展到 5 个本地 smoke case。EPFL `v2025.1` 的 8 个 Verilog/官方 BLIF 已完成 blob 固定和隔离 CEC；OpenSTA 也完成只读安装就绪审计，推荐 WSL2 Ubuntu 24.04 固定源码构建，但尚未安装或接入。related-work 为 25A/1B。下一步确认 X18 formal scope、X21 权威格式和 X22 安装/路径桥方案，再进入正式实现。
