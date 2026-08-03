# FAECO 风险登记表

更新时间：2026-07-20

| ID | 风险 | 概率 | 影响 | 等级 | 应对策略 | 状态 |
|---|---|---|---|---|---|---|
| R01 | 旧代码和旧数据不可用 | 高 | 高 | P0 | 不依赖旧代码，重建可复现公开 flow；已建立 benchmark selection 和 case schema 初版 | active |
| R02 | 只做组合逻辑不够真实 | 中 | 高 | P0 | 第一阶段做 combinational cone，第二阶段扩展 sequential reg-to-reg cone | active |
| R03 | 中文论文创新性不足 | 中 | 高 | P0 | 主打 failure-aware cut refinement；已写 FAECO 算法伪代码初版 | active |
| R04 | benchmark case 构造不被认可 | 中 | 高 | P0 | 明确 case generation、来源许可、公开脚本和 baseline；已固定 EPFL `v2025.1` 主来源并建立来源清单 | active |
| R05 | OpenSTA/Yosys/ABC 工具链卡住 | 低 | 中 | P1 | Yosys/ABC 已完成正式 runner 接入，5-case local smoke formal 5/5 pass、ABC baseline 5/5 success；OpenSTA 已在 WSL2 Ubuntu 24.04.4 构建并通过最小 Liberty/Verilog/SDC smoke；Stage B 路径桥和 report parser 已 TDD 实现 (`src/rseco/opensta.py` + 7 项测试)，WSL2 → Windows 路径转换 `_to_sta_path` 已覆盖；8-case Stage B 端到端跑通 mapping=success 8/8 + sta=success 8/8 | mitigated |
| R06 | failure-aware 反馈效果不明显 | 中 | 高 | P0 | 做失败类型消融，必要时调整主贡献为 benchmark flow + ranking | watch |
| R07 | ranking 贡献不够强 | 中 | 中 | P1 | 第一版作为补强贡献，不作为唯一创新点 | active |
| R08 | 文献综述不完整 | 低 | 中 | P1 | 已完成 25 篇 A 级全文和 1 条 B 级官方证据；L01 Related Work 初稿已落地 (`paper/draft/related_work.md`)，6 大主题分组覆盖 25A/1B；DAC 2018 保持 B 级边界并定期复核 | mitigated |
| R09 | 项目无版本管理导致混乱 | 中 | 高 | P0 | 已初始化 Git 并完成首次提交范围审计；A-only 范围已分批 commit 17 个版本到本地（`9482a34..16b61a6`），涵盖 README/.gitignore/pyproject.toml/src/rseco 18 模块/scripts 6/tests 15/experiments 配置/docs 全量 57/paper/draft/related_work.md；待用户决策 remote URL 后 push | mitigated |
| R10 | 投稿目标不明确 | 中 | 中 | P1 | Phase 6 前确定中文期刊/会议目标 | pending |
| R11 | 当前 c432/c499/c880 的第三方来源未声明 license | 高 | 高 | P0 | 仅保留为本地 smoke；论文主集迁移到 EPFL `v2025.1` MIT 数据，发布包排除未获许可文件 | active |
| R12 | 本地 SAT Sweeping 2006 PDF 的文件名与正文错配 | 高 | 高 | P0 | 原错配文件保留追溯并禁止引用；已从 Cadence Labs 原始链接的 Common Crawl 归档恢复正确全文并升级为 A，source manifest 固定归档定位、正确/错配 SHA 和再分发边界；正确副本只留在忽略提交的核验缓存 | mitigated |
| R13 | 本地 buffer insertion PDF 的年份/venue 标签误标 | 高 | 中 | P1 | 正文、DOI 和 DBLP 已确认文件实际为 2012 IEEE TCAD 扩展版；核心笔记固定 journal 书目并保留 ASP-DAC 2006 preliminary 关系，不按文件名引用 | mitigated |
| R14 | DAC 2018 cost-aware multi-target 论文无合法公开全文 | 中 | 中 | P1 | OpenAlex/Semantic Scholar/Crossref、NTU 机构记录、作者站点和归档资产已复核，仍只有 closed/出版者入口/受限文件；source manifest 只允许使用正式书目、摘要和 ICCAD 2017 问题规范 | active |
| R15 | BUFFALO 文件名、artifact 和结果叙事不一致 | 中 | 中 | P1 | source manifest 固定实际 ICCAD 2025 版本；只按 Table IV 写最大 71.10% TNS，83x 限定为代表性单网，未公开代码/数据时只进入 discussion | mitigated |
| R16 | ML timing 论文的速度、泛化和可复现性被过度外推 | 中 | 高 | P1 | source manifests 固定 4154x 的 opt+route+STA 对比口径、130-nm 到 7-nm 且含一个 7-nm 训练设计、未公开处理后数据/模型/Cadence flow；只作为表示与泛化边界证据 | mitigated |
| R17 | 原始论文、课题材料或许可不完整 benchmark 被误写入 Git 历史 | 高 | 高 | P0 | `initial_commit_scope_audit.md` 将当前 241 个候选分为 A 核心 135、B 本机 smoke/不可移植产物 51、C 私有/版权材料 55；A-only 全部入库完成后，B（实验产物、ISCS85 raw Verilog、tmp probe 目录）和 C（`benchmarks/raw/`, `data/`, `paper/`, `.codex-handoff.json`）仍 untracked；禁止全量 `git add .` | mitigated |
| R18 | 首次提交因隐式行尾/编码归一化产生大面积不可审计改动 | 中 | 中 | P1 | A 类非法 UTF-8/冲突/尾随空格已清零；A-only 全部 17 commits 全部走 Git 默认 autocrlf 替换 (LF → CRLF warning 不影响 commit)；8 个 mixed / 11 个 CRLF-only / 16 个 BOM 文件仍 untracked；首次 push 前显式决定 `.gitattributes` | mitigated |
| R19 | 目标算法文档领先于当前工程实现 | 高 | 高 | P0 | `faeco_algorithm.md`、`failure_taxonomy.md` 已标记为目标规范；`method_rewrite_readiness.md` 逐项固定 ready/partial/blocked，论文以代码和实验产物为第一事实源 | active |
| R20 | ABC baseline 依赖缺失 alias，optimized Verilog 又不受当前 parser 支持 | 低 | 中 | P1 | 已在正式 runner 中使用 `yosys-abc -s` 和 Berkeley ABC 官方 `resyn2` 展开序列，保留 optimized BLIF，并从 ABC `print_stats` 提取 AIG node/level；后续迁移 EPFL 主集时继续按同一规则回归 | watch |
| R21 | EPFL 来源可规范化但 Yosys JSON importer 尚未实现 | 高 | 高 | P0 | 8 个 Verilog 对官方 BLIF CEC 已通过，Yosys JSON 已获批为权威内部格式；Yosys JSON importer + wrapper 已实现（`src/rseco/yosys_json.py` + `tests/test_yosys_json_importer.py`），wave 1+2 共 8 个 EPFL case 已规范化导入；case metadata、gate/level 统计和 formal 回验产物已写回 `experiments/20260720_epfl_wave1_yosys_json/import_report.json` 和 `experiments/20260728_epfl_wave2_yosys_json/import_report.json` | mitigated |
| R22 | Windows runner 与 WSL OpenSTA 的路径语义不一致 | 高 | 高 | P0 | OpenSTA 本体和 `/mnt/d/...` smoke 已通过；Stage B runner 的 Liberty/Verilog/SDC 路径转换通过 `_to_sta_path` 已实现；`sta_script.tcl` 路径也走 `_to_sta_path`；8-case Stage B 验证通过；WSL PATH translation warning 仅为宿主 PATH 噪声 | mitigated |
| R31-01 | Stage B CEC limitation 在 SKY130 Liberty 中不可绕过 | 中 | 中 | P1 | ABC 0.9 报 `sky130_fd_sc_hd__clkinv_1 not found in liberty`，因为 Yosys 0.9 `synth -noabc + abc -liberty` 流程产生 Liberty 中不存在的 inverter placeholder；当前所有 8 case mapped-vs-original CEC 跑出 `unavailable`；mapped BLIF 文本仍可作 Stage B 输入喂给 OpenSTA 但不能支撑论文主表 formal 结论 | active |
| R0803-01 | N31-06 Z3 wrapper 8-case 端到端受 mapped.v 门级实例化限制 | 中 | 中 | P2 | wrapper multi-output/escaped/xor/constant 已支持（12 项 TDD 测试全绿），但 mapped.v 是 SKY130 门级实例化（0 assign，含 `clkinv_1`），assign-only parser 无法构建 replaced 侧表达式 → 8-case 端到端 error；Yosys `aigmap` 对 mapped.v 报 SKY130 模块 undefined，AIG→SMT 依赖 N31-03 cells.v | active |
