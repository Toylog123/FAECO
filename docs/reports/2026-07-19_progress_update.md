# 2026-07-19 进度更新

当前阶段：Phase 4 批量 combinational 实验继续推进；Phase 1 旧稿页级审计已收口，随新工程和文献证据增量更新。

## 1. 今日完成

| ID | 任务 | 产物 |
|---|---|---|
| D01 | 扩展 deterministic random cut baseline | `src/rseco/cut.py`、`patch_ranking`、`baseline_comparison.json` |
| D02 | 接入 ABC `cec` formal equivalence wrapper | `src/rseco/equivalence.py`、per-case `formal_equivalence` 和 `formal_equivalence_result` |
| D03 | 接入 ABC rewrite/refactor/resyn baseline wrapper | `src/rseco/abc_baseline.py`、per-case `abc_baseline_status` 和 comparison 表字段 |
| D04 | 将 batch comparison 扩展为多 baseline 对比 | `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.json`、`.md` |
| D05 | 归档 per-experiment 工具链快照 | `experiments/*/environment/toolchain_snapshot.json`、实验 `config.json`、batch `case_summary.json` |
| D06 | 刷新 5-case batch artifacts | `c17 N22/N23`、`c432`、`c499`、`c880` 均有 raw metrics、summary 和 comparison 输出 |
| D07 | 为工具链快照补版本字段 | `scripts/run_minimal_combinational_demo.py`、`scripts/check_toolchain.ps1`、`tests/test_demo_runner.py`、`tests/test_toolchain_script.py` |
| D08 | 建立结构化 runtime stage schema | `src/rseco/flow.py`、`scripts/run_minimal_combinational_demo.py`、`tests/test_case_loader_netlist_flow.py`、`tests/test_demo_runner.py` |
| D09 | 生成 batch runtime breakdown 表 | `experiments/20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.json`、`.md` |
| D10 | 生成 failure recovery Stage A proxy 表 | `experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.json`、`.md` |
| D11 | 隔离 experiment runner 与输入 case 产物 | `src/rseco/flow.py`、`scripts/run_minimal_combinational_demo.py`、`tests/test_demo_runner.py` |
| D12 | 安装并核验 Yosys 0.9 / UC Berkeley ABC 1.01 | Scoop `yosys`、`yosys.exe`、`yosys-abc.exe`、c17/c432 smoke |
| D13 | 验证 Yosys-BLIF-ABC 规范化路径 | 去 BOM + Yosys `simplemap` + ABC `cec`，c17/c432 均报告 equivalent |
| D14 | 完成旧稿 16 页 PDF/DOCX 页级核验 | `docs/paper_audit/legacy_source_locator.md`、PDF 逐页渲染、DOCX 195 段落/6 表结构核对 |
| D15 | 修订 claim-evidence 与公式图表审计 | C01-C12 页码、式(1)-(20)、图1-9、表1-5、CutFinder 3/8→8/8 的历史证据边界 |
| D16 | 确认旧稿三类一致性硬伤 | Word 字段更新证明后五式应重编号为(15)-(19)；图6误引；表2四套统计不一致 |
| D17 | 完成表2独立复算 | `docs/paper_audit/legacy_table2_recalculation.md`，逐 case 百分比和四套汇总口径均已记录 |
| D18 | 完成公开 benchmark 来源与许可审计 | `docs/experiment_design/benchmark_source_and_license_audit.md`、两个 source manifest |
| D19 | 固定 EPFL 论文主来源 | EPFL `v2025.1`、commit `8c832d5...`、MIT license 和 8 个候选文件 blob SHA；当前 ISCAS85 降级为本地 smoke |
| D20 | 完成第一轮 P0 核心文献全文核验 | 7 篇本地 PDF 的首页、方法、结论、DOI、页数和 SHA256；`docs/literature/core_paper_notes.md` |
| D21 | 升级 Related Work 矩阵为证据化记录 | `docs/literature/literature_matrix.md`，区分 timing ECO、functional ECO、formal 和工具链适用边界 |
| D22 | 发现并隔离 SAT Sweeping 2006 错配证据 | 本地同名 PDF 实际为 keeper architecture 论文；正确 DOI 为 `10.1145/1146909.1146970`，错配文件不再进入引用证据链 |
| D23 | 将文献证据同步到论文 claim 和项目日志 | `claim_evidence_matrix.md`、`revision_roadmap.md`、任务板、长期计划、周报、风险表和材料索引 |
| D24 | 完成第二批 3 篇核心文献精读 | 2012 Bezier fixability、2012 metal-configurable spare cells、2018 ECO patch functions；首页、方法、结论、DOI、页数和 SHA256 均已核验 |
| D25 | 收紧 FAECO 方法与指标边界 | 明确真实 fixability 依赖物理/资源特征，target/boundary selection 与 Boolean patch synthesis 必须分开报告 |
| D26 | 核验正确 SAT Sweeping 2006 作者全文 | 核对 AIG/simulation/SAT、local ODC、observability vectors、trie candidate search、IWLS/OpenCores 实验与结论 |
| D27 | 建立 SAT Sweeping source manifest | 机器可读固定 DOI、作者全文页面、本地错配 SHA、B 级证据和“未获再分发许可/不复制 PDF”边界 |
| D28 | 完成第三批 3 篇核心文献全文核验 | 2012 negotiation-based restructuring、2016 resource-aware patch、2016 unified functional/timing ECO；首页/结论页、DOI、页数和 SHA256 均已核对 |
| D29 | 补齐资源竞争与物理代价证据边界 | 明确 congestion/history penalty、size-vs-wiring-cost tradeoff、timing-to-functional transformation 和 STA refinement 的适用范围 |
| D30 | 同步第三批证据到论文和项目日志 | 核心全文计数更新为 13；claim audit、文献矩阵、任务板、长期计划、风险表、周报和工作日志统一更新 |
| D31 | 完成第四批 2 篇核心文献全文核验 | 2012 Multi-Patch 与 2013 Intuitive ECO；首页/末页、DOI、页数和 SHA256 均已核对 |
| D32 | 补齐 multi-error patch 与 functional correspondence 证据边界 | 区分 diagnosis、Boolean patch synthesis、formal checking、失败回退、逻辑 delta 和 industrial physical synthesis |
| D33 | 同步第四批证据到论文和项目日志 | 新增 LIT-F06/F07，核心全文计数更新为 15；claim audit、文献矩阵、任务板、长期计划、风险表、周报和工作日志统一更新 |
| D34 | 完成第五批 3 篇核心文献全文核验 | 2012 optimal buffer insertion、2021 RL-Sizer、2024 STP SAT-sweeping；首页/末页、DOI、页数和 SHA256 均已核对 |
| D35 | 发现并修正 buffer 论文书目错标 | 本地文件名写 2006 ASP-DAC，正文实际是增加作者/证明/cost extension 的 2012 IEEE TCAD 版本；后续固定 journal 书目 |
| D36 | 同步第五批证据到论文和项目日志 | 新增 LIT-B01/B02/V03，核心全文计数更新为 18；claim audit、文献矩阵、任务板、长期计划、风险表、周报和工作日志统一更新 |
| D37 | 完成第六批 3 篇核心文献全文核验 | 2025 physically-aware gate sizing、2024 AiTO、2025 MLBuf；首页/末页、正式版本、页数和 SHA256 均已核对 |
| D38 | 收口 modern sizing/buffering 的方法与复现边界 | 区分 post-route physical-aware sizing、post-placement simultaneous B&G 和 global-placement virtual buffering；确认 AiTO 数据/实现不公开，MLBuf 正式发表于 MLCAD 2025且 BSD-3-Clause 开源 |
| D39 | 同步第六批证据到论文和项目日志 | 新增 LIT-B03/B04/B05，核心本地全文计数更新为 21；claim audit、文献矩阵、任务板、长期计划、风险表、周报和工作日志统一更新 |
| D40 | 定位第七批 cost-aware multi-target 核心文献 | 确认 DAC 2018 双 DOI、Article 96:1-96:6、NTU/DBLP 书目和 ICCAD 2017 contest 问题来源；本地无对应 PDF |
| D41 | 完成公开全文与证据等级审计 | OpenAlex/ResearchGate 未发现公开全文，NTU 博士论文仅有目录且无 bitstream；按 B 级固定 abstract/contest-spec 可用范围和算法/复杂度/结果禁用边界 |
| D42 | 建立 DAC 2018 source manifest 并同步项目文档 | 新增 LIT-F08 和机器可读来源清单；related-work 口径更新为 21 篇本地 A 级全文加 2 条 B 级网页/官方证据 |
| D43 | 完成第七批文献与工程回归验证 | 50 个 JSON 全部可解析，文献条目精确为 21A/2B，source manifest 和活跃文档状态一致；47 项测试、single demo 和 5-case batch 均通过 |
| D44 | 定位并校正 BUFFALO 正式版本 | 本地文件名标为 2024/arXiv，正文和 NVIDIA/Georgia Tech/DBLP 证明实际为 ICCAD 2025、DOI `10.1109/ICCAD66269.2025.11240744` |
| D45 | 完成 BUFFALO PDF 与来源核验 | 本地 IEEE 全文 9 页、SHA256 `1C039551...B33E8C4`，首页/末页渲染完整；Georgia Tech 作者 PDF 9 页、SHA256 `53CC13EE...B1AE7` |
| D46 | 完成 BUFFALO 方法、实验与 artifact 边界审计 | 固定 T5 full-tree generation、20M pairs、INSTA-guided net/chip GRPO、9-design ASAP7 flow；确认实现/数据未公开、83x 仅为代表性单网、71%/77.7% TNS 表述不一致 |
| D47 | 建立 BUFFALO source manifest 并同步项目文档 | 新增 LIT-B06，related-work 口径更新为 22 篇本地 A 级全文加 2 条 B 级网页/官方证据；BUFFALO 只进入 discussion，不进入当前可运行 baseline |
| D48 | 完成第八批文献与工程回归验证 | 51 个 JSON 全部可解析，文献条目精确为 22A/2B；BUFFALO 双 PDF 页数/哈希复核通过，47 项测试、single demo 和 5-case batch 均通过 |
| D49 | 完成两篇 ML timing 正式书目与 PDF 核验 | DAC 2023 restructure-tolerant 与 DAC 2024 cross-node timing 本地/作者 PDF 均为 6 页且逐字节一致；SHA256 分别为 `130DD9DA...BECD`、`1FA79D2E...AC83` |
| D50 | 收口结构变化容忍 timing prediction 证据边界 | 固定 endpoint GNN+layout CNN、5 train/5 test、7-nm Cadence flow、平均 R2 `0.8724`；4154x 明确是 inference 对 commercial opt+route+STA 总流，不是 STA-vs-STA 或 timing closure |
| D51 | 收口跨 technology timing transfer 证据边界 | 固定 4 个 130-nm 加 1 个 7-nm 训练设计、5 个 7-nm 测试设计、平均 R2 `0.810` 和约 4% inference overhead；不写成零目标数据、任意节点泛化或端到端 EDA runtime |
| D52 | 建立两份 ML timing source manifest 并同步总日志 | 新增 LIT-M01/M02，related-work 口径更新为 24 篇本地 A 级全文加 2 条 B 级网页/官方证据；ML timing/generalization 核心缺口关闭，未公开模型/处理后数据/Cadence flow 的边界已固定 |
| D53 | 完成第九批文献与工程回归验证 | 53 个 JSON 全部可解析，文献条目精确为 24A/2B，两篇本地 PDF 哈希与 manifest/作者 PDF 一致；47 项测试、single demo 和 5-case batch 均通过 |
| D54 | 恢复并核验正确 SAT Sweeping 2006 全文 | 由 Cadence Labs 原始 PDF 链接的 Common Crawl `CC-MAIN-2009-2010` 归档恢复 6 页全文；SHA256 为 `DA48ABD...DFB42`，首页、末页、标题、作者和 DOI 均一致 |
| D55 | 复核 DAC 2018 cost-aware multi-target 开放获取状态 | OpenAlex、Unpaywall、NTU Scholars、作者页面和 ResearchGate 均未提供合法公开全文；NTU 学位论文的 2.76 MB 文件明确为受限访问且未授权公开 |
| D56 | 完成第十批来源清单与项目文档同步 | SAT Sweeping 证据由 B 升为 A，正确副本只留在 Git 忽略的核验缓存且禁止再分发；DAC 2018 保持 B，总口径更新为 25A/1B |
| D57 | 完成第十批文献与工程回归验证 | 53 个 JSON 全部可解析，26 条文献精确为 25A/1B，SAT 正确 PDF 页数与 SHA256 同 manifest 一致；47 项测试、single demo 和 5-case batch 均通过 |
| D58 | 完成总任务看板过期动作审计 | 修正 20 余个 `done` 条目的旧后续动作，不再重复安排已完成的 cut、batch、c432 导入或工具探测；当前依赖统一到 X18/X19/X21 |
| D59 | 对齐任务看板、长期计划与 backlog 状态 | PM22 由过期的 `pending/P1` 修正为 `in_progress/P0`；补入 N08 Git 首次基线任务，并更新 F15/F19/F20 的当前实现边界 |
| D60 | 完成 Git 首次提交工作区盘点 | 当前未忽略候选为 241 个文件、约 95.32 MiB；无 remote、无仓库 LICENSE、无 `.gitattributes`，Git LFS 3.7.1 可用但不解决再分发许可 |
| D61 | 建立首次提交范围与门槛审计 | 当前分层为 A 工程核心 135、B 本机 smoke/不可移植产物 51、C 私有/版权材料 55；固定 COMMIT-01 至 COMMIT-11 门槛，明确禁止直接 `git add .` |
| D62 | 刷新仓库入口和 Git 风险记录 | 顶层 README 下一步改为 X18/X19/X21/N05/L01/N08，工程根目录名修正为 `03_FAECO/`，新增 R17 防止原始材料误入历史 |
| D63 | 完成 A-only 隔离副本验证 | 135 个源路径全部复制，路径清单 SHA256 `6C15C13F...11479F`；隔离副本 47 项测试和 single demo 通过，无 PDF/DOCX 或工作区绝对路径 |
| D64 | 验证 A-only batch 依赖闭包 | 原 5-case config 因排除 c432/c499/c880 按预期失败；临时 2-case c17 config 成功运行，证明 runner 可用但便携主 batch 配置仍待 X21 |
| D65 | 完成 A-only secrets/PII 与路径卫生审计 | 私钥/token/password 命中 0；唯一邮箱为已知占位身份，三个 Windows 路径为 `C:\tools\...` 示例；路径碰撞、超长路径、symlink、Office/PDF 二进制均为 0 |
| D66 | 完成 A-only 编码与工作树标记审计 | 非法 UTF-8、NUL、冲突标记、开发占位注释和尾随空格均为 0；8 mixed/11 CRLF-only/16 BOM 固定为 COMMIT-11 行尾策略决策，不擅自批量改写 |
| D67 | 完成 FAECO 方法重写就绪审计 | `method_rewrite_readiness.md` 将 18 个方法要素映射到代码、实验字段和依赖，当前为 1 ready/8 partial/9 blocked；固定旧稿四项硬伤处置、公式继承策略和方法禁写 claim |
| D68 | 收紧算法设计文档与实现边界 | `faeco_algorithm.md` 和 `failure_taxonomy.md` 已标为目标规范；新增 R19，明确代码和实验产物优先于目标伪代码，完整 Method 仍为 pending |
| D69 | 刷新 135 文件 A-only 基线验证 | 新增方法审计后候选变为 241=A135/B51/C55；新隔离副本 47 项测试、single demo、2-case c17 batch 和静态卫生通过，路径清单 SHA256 `6C15C13F...11479F` |
| D70 | 定位 ABC `resyn2` baseline 兼容性根因 | 当前 Scoop/Yosys 包缺少可加载 `abc.rc`，`resyn2` 因此不是可用命令；Berkeley ABC 官方 `abc.rc` commit `bcfdf592...` 已固定 alias 展开序列 |
| D71 | 完成 X18 隔离 5-case 全网表探针 | 去 BOM + Yosys-BLIF + `yosys-abc -s` 显式序列使 5 个 pair CEC、5 个 baseline 和 5 个 baseline 回验全部成功；ABC stats 完整，summary SHA256 `0EE7281B...6A685`，但仍不是正式实验 |
| D72 | 完成 X18 探针与项目日志一致性复核 | 58 行任务板、33 行长期计划、18 项方法矩阵、20 行风险表和 53 个 JSON 结构正确；47 项测试通过，正式 5-case formal/ABC 状态未被探针覆盖 |
| D73 | 复核 EPFL 固定源与许可闭包 | 本地 HEAD/tag/manifest commit、MIT license blob、8 个 Verilog blob 和 8 个官方 BLIF blob 全部一致，mismatch=0，来源工作树干净 |
| D74 | 完成 X21 隔离 8-candidate 规范化 CEC | 8/8 Yosys-BLIF 成功、8/8 对同 tag 官方 BLIF 的 ABC CEC pass，I/O/AIG and-node/level 逐项一致；summary SHA256 `F268C5BF...E2A49` |
| D75 | 定位 EPFL 正式导入的权威格式缺口 | 8 个原始 Verilog及第一波 3 个 `write_verilog -noexpr` 输出在当前 parser 中均为 0 gates；X21 状态改为 in_progress，正式 case 创建前需批准 BLIF/Yosys JSON/simple-gate Verilog 方案 |
| D76 | 完成 X21 就绪探针最终一致性复核 | 修正验证脚本的 PowerShell 筛选写法后，8 个候选的 Yosys/CEC/stats 仍为 8/8；53 个正式 JSON 均可解析，正式 5-case formal/ABC 状态和 EPFL 未导入边界均未改变 |
| D77 | 刷新 X21 文档后的 135 文件 A-only 基线 | 新 `_04` 隔离副本 missing/hash mismatch 均为 0；47 项测试、single demo 和 2-case c17 batch 通过，静态卫生命中 0，路径摘要仍为 `6C15C13F...11479F` |
| D78 | 复核 DAC 2018 cost-aware multi-target 开放获取状态 | OpenAlex 为 closed，Semantic Scholar 为 `isOpenAccess=false/CLOSED`，Crossref 仅有 ACM 出版者入口；NTU、作者站点和归档资产仍无公开全文，证据等级保持 B |
| D79 | 收敛 Related Work 的全文前置条件 | DAC 2018 合法全文改为定期复核项，不再阻塞 25A/1B 初稿；算法细节、复杂度和实验数字仍禁止由 B 级摘要/规范证据推断 |
| D80 | 固定 OpenSTA 官方构建证据 | 官方仓库 `master` commit `dc5ccd2...`、GPL-3.0 license、Ubuntu 24.04 Dockerfile 和 `sta -version` CLI 已核对；官方仓库当前无 tag，后续按 commit 固定 |
| D81 | 完成 OpenSTA Windows/WSL2/Docker 只读就绪比较 | WSL2 Ubuntu 24.04 与官方 recipe 对齐且缺失依赖均有 apt candidate；Docker 仅 client 可用、daemon 未运行；Windows 原生缺少 CMake/Tcl/CUDD，不作为首轮推荐路径 |
| D82 | 归档 OpenSTA 就绪审计并同步总日志 | `tmp/opensta_readiness_audit_20260719_01/readiness_summary.json` SHA256 `2198CBD5...70CEB0`、toolchain/task/PM/risk/backlog/report 文档；新增 X22/R22，明确未安装、无 WNS/TNS、runner 和正式 batch 状态均未改变 |
| D83 | 完成 OpenSTA 审计批次回归与 A-only 复核 | 主工作区和 A-only 副本各 47 项测试通过，single/5-case/c17-only runner 均成功；53 个正式 JSON 解析错误 0，A135 source missing/hash mismatch 均为 0，正式 formal/ABC 仍各 5 个 unavailable |

## 2. 当前 batch 状态

| 项 | 当前值 |
|---|---|
| batch 目录 | `experiments/20260718_minimal_combinational_batch_demo/` |
| case count | 5 |
| cases | `iscas85_c17_case01`、`iscas85_c17_case02`、`iscas85_c432_case01`、`iscas85_c499_case01`、`iscas85_c880_case01` |
| methods | `fixed_min_cut`、`random_cut`、`size_only_cut`、`critical_path_only_cut`、`abc_rewrite_refactor_resyn`、`faeco_selected` |
| selected FAECO patch | 5 个 case 均为 `patch_<target>_size_refined_cut` |
| structural equivalence | 5 个 case 均为 `pass`，method 为 structural signature |
| formal equivalence | 5 个 case 均为 `unavailable`，原因是 `ABC command not found: abc` |
| ABC baseline | 5 个 case 均为 `unavailable`，原因是 `ABC command not found: abc` |
| toolchain snapshot | `experiments/20260718_minimal_combinational_batch_demo/environment/toolchain_snapshot.json` |
| runtime schema | `metrics.runtime.schema_version=1`，stage 覆盖 parse、cone extraction、structural equivalence、formal equivalence、ABC baseline、cut search、ranking、replacement |
| runtime table | `experiments/20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.json/md`，覆盖 5 个 case 的 stage duration/status/category/tool |
| failure recovery table | `experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.json/md`，F3/F4 的 Stage A proxy recovery rate 当前为 1.000，`avg_iterations=1.0`，来源是 single-refinement proxy iteration count |

## 3. 工具链快照

| 工具 | 当前状态 | 说明 |
|---|---|---|
| Python | 可用 | 版本 3.11.9，当前 Python-only flow 可运行 |
| NetworkX | 可用 | 版本 3.4.2；当前 weighted cut 使用项目内 Edmonds-Karp 实现 |
| Yosys | 可用 | Scoop `yosys 0.9`，正式 batch snapshot 已记录版本与 shim 路径 |
| ABC | 二进制与隔离 5-case 探针可用，正式 runner 尚未接入 | UC Berkeley ABC 1.01 命令为 `yosys-abc.exe`；需使用 `-s` 和显式 `resyn2` 展开，当前正式 batch 继续记录 unavailable |
| OpenSTA | 不可用 | 正式 batch 仍未检出，版本为 `null`；只读审计推荐 WSL2 Ubuntu 24.04 固定源码构建，但尚未安装、未接入路径桥或产生 WNS/TNS |
| Z3 | 不可用 | 未在当前 Python 环境检出，版本为 `null` |

## 4. 当前限制

| 限制 | 影响 | 下一步 |
|---|---|---|
| `yosys-abc` 尚未进入默认候选 | 正式 batch 仍无法刷新真实 ABC/SAT pass/fail 和 optimized netlist | 自动识别 `yosys-abc`，并记录 ABC `version` 命令 |
| ABC 1.01 不能直接可靠读取当前 Verilog | c17 ANSI 端口声明触发断言，c432 多行 module/BOM 读取失败 | 接入去 BOM + Yosys `simplemap` BLIF 规范化后再运行 ABC |
| 当前 ABC 包缺少 `abc.rc` | wrapper 的 `resyn2` alias 报 `unknown command` | 使用 `yosys-abc -s`，按固定官方 commit 显式展开内建命令并记录完整序列 |
| optimized Verilog 是 assign/LUT 表达式 | 当前轻量 parser 对 5 个导出文件均得到 0 gates，不能据此比较 baseline 门数 | 保留 optimized BLIF，并从 ABC `print_stats` 提取 AIG and-node/level；Verilog 只作派生产物 |
| OpenSTA 未安装且 Windows-WSL 路径桥未设计 | 暂不能报告真实 WNS/TNS，WSL 可构建也不等于 runner 已接入 | 按 X22 固定 commit/CUDD 哈希，安装依赖并通过最小 STA smoke 后，再按 TDD 接入路径转换和 runtime |
| critical-path-only 仍是 Stage A proxy | 不能当作真实 STA critical path baseline | 接 OpenSTA 后替换为真实路径特征 |
| c432/c499/c880 来源为第三方整理仓库且 license 未声明 | 当前 5-case batch 不能作为许可完备的论文主实验集，也不进入可再分发包 | 已固定 EPFL `v2025.1` MIT 替代源；下一步导入并迁移主表 |
| EPFL 原始 Verilog及 Yosys noexpr 输出不受当前轻量 parser 支持 | 8 个原始候选和第一波 3 个 noexpr 导出均为 0 gates，不能建立可信 case metrics | 先批准 BLIF、Yosys JSON 或确定性 simple-gate Verilog，再生成 FAECO case |
| 文献库 SAT Sweeping 2006 PDF 内容错配 | 若按文件名引用，会把 keeper architecture 论文误作 formal 证据 | 归档的正确 6 页全文已达 A 级并建立 manifest；原错配文件继续禁引，正确核验缓存不提交、不再分发 |
| Git 仓库尚无初始提交 | 缺少可回退基线 | 确认提交范围后创建首次提交 |
| 目标算法文档领先于当前实现 | 容易把等价点映射、boundary closure、Boolean patch synthesis、多轮循环和停止条件误写为已实现 | 以 `method_rewrite_readiness.md` 为写作门槛；先完成 X18/X19/X21 和 OpenSTA，再编写完整 Method |

## 5. 下一批任务

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| N01 | 接入 `yosys-abc` 与 Yosys-BLIF 规范化 | P0 | 自动检测 UC Berkeley ABC，使用 `-s` 和显式序列，5-case wrapper 记录 formal scope、BLIF、ABC stats、日志和真实状态 |
| N02 | 刷新 5-case batch 的真实验证和 ABC baseline | P0 | `formal_equivalence_result` 和 `abc_baseline_status` 记录真实工具结果 |
| N03 | 接入外部 EDA runtime breakdown | P0 | runtime 表区分 Python flow、formal verification、ABC baseline 和后续 Yosys/OpenSTA 阶段 |
| N04 | 实现多轮 refinement 与消融配置 | P0 | recovery 统计不再依赖 single-refinement proxy，并生成 without F1/F3/F4 表 |
| N05 | 修订旧稿硬伤并重写 FAECO 方法定义 | P0 | 就绪审计已完成；待 X18/X19/X21/X22 关闭阻塞后，式(15)/图6/表2处理、符号、公式和伪代码均与工程实现一致 |
| N06 | 导入 EPFL 第一波公开 benchmark | P0 | 8 个 Verilog/官方 BLIF blob 与隔离 CEC 已通过；批准权威格式后，ctrl/int2float/router 保留 MIT notice并生成 formal 可追溯 cases |
| N07 | 形成 Related Work 第一版证据化段落 | P1 | 写作结构获批后，以 25A/1B 证据按 timing ECO、functional ECO、formal、B&G、ML timing 问题设置分组；DAC 2018 保持 B 级边界并定期复核，不阻塞初稿 |
| N08 | 建立 Git 首次可回退基线 | P0 | A-only 135 文件 dry-run 与静态卫生已通过；确认真实 Git 身份、发布属性和行尾策略后精确 staging，不误提交 51 个本机 artifact、55 个私有/版权材料或核验缓存 |
| N09 | 安装并接入 OpenSTA Stage B | P0 | 批准 WSL2 路径后固定 OpenSTA commit 与 CUDD SHA256，`sta -version` 和最小 Liberty/Verilog/SDC smoke 通过，runner 可追溯输出 WNS/TNS、critical path、runtime 和跨系统路径 |

## 6. 验证记录

| 命令/检查 | 结果 |
|---|---|
| `$env:PYTHONPATH='src'; python -m unittest discover -s tests` | 47 项测试通过 |
| `python scripts\run_minimal_combinational_demo.py` | 成功刷新 `experiments/20260717_minimal_combinational_demo/` |
| `python scripts\run_minimal_combinational_demo.py --config experiments\configs\minimal_combinational.json --output-dir experiments\20260718_minimal_combinational_batch_demo` | 成功刷新 5-case batch |
| `experiments/20260718_minimal_combinational_batch_demo/environment/toolchain_snapshot.json` | Python 3.11.9、NetworkX 3.4.2、Yosys 0.9 可用；ABC/OpenSTA/Z3 在正式 batch 中仍不可用 |
| OpenSTA 只读就绪审计 | `tmp/opensta_readiness_audit_20260719_01/readiness_summary.json` SHA256 `2198CBD5...70CEB0`，固定官方 commit/license/Dockerfile 哈希、Ubuntu 依赖候选和三条路径比较；`opensta_installed=false`、`runner_modified=false`、`wns_tns_available=false` |
| fake ABC runner 回归 | runner 的 ABC netlist 写入实验 `raw_results/<run>/abc_baseline/`，输入 case 文件保持不变，旧 fake artifact 已删除 |
| Yosys-BLIF-ABC smoke | c17 和 c432 经去 BOM、Yosys `simplemap`、ABC `cec` 均报告 equivalent；尚未据此宣称 5-case formal 完成 |
| X18 失败探针 | 直接沿用 wrapper 的 `resyn2` 在首个 c17 baseline 报 `unknown command`；启动日志确认 Scoop/Yosys 包没有可加载 `abc.rc`，该轮按错误停止且不作成功证据 |
| X18 隔离 5-case 探针 | `tmp/x18_full_netlist_probe_20260719_03/probe_summary.json` 精确为 5 个 pair CEC pass、5 个 baseline success、5 个 baseline CEC pass、5 个 optimized Verilog export success；缺失产物和 `abc.rc` 警告均为 0，summary SHA256 `0EE7281B...6A685` |
| X18 baseline stats | c432/c499/c880 的 AIG and-node 分别 208→138、396→386、327→313，level 分别 30→23、21→17、24→22；c17 两个 run 均无变化。数值只用于设计探针，未进入正式主表 |
| X18 optimized Verilog 兼容性 | 5 个导出文件由当前 parser 读取均为 `gate_count=0`，证明正式 baseline 指标必须来自 ABC stats 或另行定义可解析导出，不得复用该 0-gate 结果 |
| `experiments/20260718_minimal_combinational_batch_demo/raw_results/c17_n22_baseline/metrics.json` | `metrics.runtime.stages` 已记录 Python flow 阶段和 `external_tool_wrapper/unavailable` 的 ABC 相关阶段 |
| `experiments/20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.json` | `case_count=5`，stage 顺序为 parse、cone extraction、equivalence、formal equivalence、ABC baseline、cut search、ranking、replacement |
| `experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.json` | `case_count=5`，F3/F4 均为 initial fail count 5、proxy recovered count 5、recovery rate 1.000、`avg_iterations=1.0` |
| 旧稿 PDF/DOCX 核验 | PDF 16 页逐页可读；Word 16.0 识别 DOCX 16 页；`python-docx` 读取 195 段落和 6 个表格对象 |
| `docs/paper_audit/legacy_source_locator.md` | C01-C12、公式、图表、表格均有页级定位，并记录三项已确认一致性问题 |
| EPFL source pin | HEAD/tag/manifest 均为 commit `8c832d5d07d822d28ba84dc6e95295367702401f`；MIT license blob `ab602974...9f08`，8 个 Verilog和8 个官方 BLIF blob mismatch 均为 0 |
| EPFL 8-candidate readiness probe | `tmp/x21_epfl_readiness_probe_20260719_01/probe_summary.json` 记录 8/8 Yosys success、8/8 对官方 BLIF CEC pass、8/8 stats match；SHA256 `F268C5BF...E2A49`，仍为 ignored tmp probe |
| EPFL 第一波规模与耗时 | ctrl/int2float/router AIG and-node/level 为 174/10、260/16、257/54；Yosys 约 0.361/0.497/0.444 秒，CEC 约 0.132/0.139/0.137 秒，仅用于导入排序 |
| EPFL canonical format gap | 8 个原始 Verilog gate count 均为 0；ctrl/int2float/router 的 noexpr cell Verilog 仍为 0 gates且 logic-level 失败，证明正式导入尚未完成 |
| 第一轮 P0 文献核验 | 7 篇全文已记录页数、DOI、SHA256、方法和证据边界；ABC/Yosys/OpenSTA 官方来源已归档 |
| SAT Sweeping 本地文件核对 | 同名 PDF SHA256 为 `DC27E109...52B3`，正文 DOI 为 `10.1145/1146909.1147156`，与正确 SAT Sweeping DOI `10.1145/1146909.1146970` 不一致 |
| 第二批 P0 文献核验 | 3 篇首页视觉一致；页数分别为 10/6/6，SHA256 为 `FF19C10A...AA31`、`7F83DB36...8272`、`98A08DDA...D062`；DOI 与论文首页和高校/作者页面一致 |
| SAT Sweeping source manifest | JSON 可解析；正确 DOI `10.1145/1146909.1146970`、归档全文状态 `local_full_text_verified`、6 页 PDF SHA256 `DA48ABD...DFB42`、错配文件状态 `content_mismatch_do_not_cite`、证据等级 A |
| 第三批核心文献核验 | 3 篇首页/结论页视觉一致；页数为 6/6/8，SHA256 为 `03C22C49...BFBB`、`2E476451...74B9`、`5850EABA...7B8D`；DOI/页码与 DBLP、DATE、Wiley/IET 记录一致 |
| 第四批核心文献核验 | 2 篇首页/末页视觉一致；页数均为 6，SHA256 为 `DFAEF833...77AD5`、`DA7BA4C1...9D9C38`；DOI/页码与 NTU/DBLP/DATE、IBM Research 记录一致 |
| 第五批核心文献核验 | 3 篇首页/末页视觉一致；页数为 5/6/6，SHA256 为 `4DB532F8...7F04`、`2EE0663A...B288`、`B02BFA84...ECC6`；DOI/页码与 DBLP/IEEE/作者页、DATE 记录一致 |
| 第六批核心文献核验 | 3 篇首页/末页视觉一致；本地页数为 14/12/10，SHA256 为 `286744C8...5439`、`506B8958...6000F`、`EA377DA5...C645`；physically-aware/AiTO 的 journal 书目与作者页/ScienceDirect 一致，MLBuf 本地为 arXiv v2 全文且正式 MLCAD 2025 书目、代码和 BSD-3-Clause license 已核对 |
| 第七批核心文献核验 | DAC 2018 cost-aware multi-target 双 DOI、NTU/DBLP 书目、ICCAD 2017 resource/patch-size/runtime 评价口径和 NTU 论文目录已核对；无本地 PDF，NTU 2.76 MB 文件为受限访问且未授权公开，证据等级固定为 B |
| 第七批文献与工程回归 | 50 个 JSON 解析失败数为 0；`core_paper_notes.md` 条目计数为 21A/2B；47 项测试通过，single/batch runner 成功刷新；5-case formal/ABC 仍为 `unavailable`，F3/F4 仍为 single-refinement Stage A proxy，行级 `avg_iterations=1.0` |
| 第八批 BUFFALO 核验 | 本地/作者 PDF 均为 9 页，SHA256 分别为 `1C039551...B33E8C4`、`53CC13EE...B1AE7`；正式 ICCAD 2025 书目与 DOI 一致，官方代码仓库检索为 0，source manifest 固定数值和复现边界 |
| 第八批文献与工程回归 | 51 个 JSON 解析失败数为 0；`core_paper_notes.md` 条目计数为 22A/2B；47 项测试通过，single/batch runner 成功刷新；5-case formal/ABC 仍为 `unavailable`，F3/F4 仍为 single-refinement Stage A proxy，行级 `avg_iterations=1.0` |
| 第九批 ML timing 核验 | 两篇本地/作者 PDF 均为 6 页且逐字节一致，SHA256 为 `130DD9DA...BECD`、`1FA79D2E...AC83`；正式 DOI、训练/测试切分、R2/runtime 和未公开 artifact 边界均写入 source manifests |
| 第九批文献与工程回归 | 53 个 JSON 解析失败数为 0；`core_paper_notes.md` 条目计数为 24A/2B；47 项测试通过，single/batch runner 成功刷新；5-case formal/ABC 仍为 `unavailable`，F3/F4 仍为 single-refinement Stage A proxy，行级 `avg_iterations=1.0` |
| 第十批 SAT/DAC 2018 B→A 审计 | 53 个 JSON 解析失败数为 0；26 条文献分级为 25A/1B；SAT 正确 PDF 为 6 页、108879 bytes，SHA256 `DA48ABD...DFB42`，缓存受 `.gitignore` 排除；当前状态文档无陈旧 24A/2B 或“SAT 仍为 B”表述 |
| 第十批文献与工程回归 | 47 项测试通过，single/batch runner 成功刷新；5-case formal/ABC 仍为 `unavailable`，runtime 表的 ABC 阶段仍是 wrapper 探测，F3/F4 仍为 single-refinement Stage A proxy，行级 `avg_iterations=1.0` |
| 总任务日志结构复核 | `task_board.md` 共 59 个任务行、列错误 0，当前状态为 54 done/5 in_progress/0 pending；`long_term_task_plan.md` 共 33 个 PM 行、列错误 0，状态为 18 done/5 in_progress/10 pending；风险表 22 行、列错误 0 |
| 方法重写就绪审计 | 18 个方法要素精确为 1 ready/8 partial/9 blocked；旧稿 SRC-01/02/03 的处置策略 ready，SRC-04 因无多轮/formal/STA/规模证据保持 blocked；算法和 taxonomy 文档已标为目标规范 |
| 135 文件 A-only 刷新 | 当前候选精确为 241=A135/B51/C55；135 个源路径 missing=0、与隔离副本逐文件 SHA256 mismatch=0，路径清单 SHA256 `6C15C13F...11479F` |
| 135 文件 A-only 回归 | 隔离副本 47 项测试、single demo 和 2-case c17 batch 通过；formal/ABC 均为 unavailable，recovery 仍为 `stage_a_proxy`，未升级论文结论 |
| 135 文件 A-only 静态卫生 | credential、非法 UTF-8、NUL、冲突标记、尾随空格、大小写碰撞、超长路径、symlink、Office/PDF 和工作区绝对路径均为 0 |

## 7. 今日结论

当前工程已从单 case smoke 推进到 5-case、多 baseline、可追溯环境快照、结构化 runtime schema、batch runtime breakdown 表和 failure recovery proxy 表的实验原型；旧稿页级审计和方法重写就绪审计也已收口。X18 隔离探针已覆盖 5-case Yosys-BLIF-ABC，X21 完成 EPFL 8 个固定 Verilog 对同 tag 官方 BLIF 的独立 CEC，X22 又固定了 OpenSTA 的 WSL2 Ubuntu 24.04 推荐安装路径。三条链路仍停在设计/就绪层：X18 formal scope 未确认，X21 权威内部格式未批准，OpenSTA 未安装且 Windows-WSL 路径桥未设计。当前 ISCAS85 batch 仍只作本地 smoke，related-work 为 25A/1B。下一步取得三项设计/安装批准后再按 TDD 接入正式工具链、EPFL cases 和 WNS/TNS；在此之前不能写成正式 ABC、STA、公开 benchmark 主实验或多轮 recovery 已完成。
