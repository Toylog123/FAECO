# FAECO 风险登记表

更新时间：2026-07-20

| ID | 风险 | 概率 | 影响 | 等级 | 应对策略 | 状态 |
|---|---|---|---|---|---|---|
| R01 | 旧代码和旧数据不可用 | 高 | 高 | P0 | 不依赖旧代码，重建可复现公开 flow；已建立 benchmark selection 和 case schema 初版 | active |
| R02 | 只做组合逻辑不够真实 | 中 | 高 | P0 | 第一阶段做 combinational cone，第二阶段扩展 sequential reg-to-reg cone | active |
| R03 | 中文论文创新性不足 | 中 | 高 | P0 | 主打 failure-aware cut refinement；已写 FAECO 算法伪代码初版 | active |
| R04 | benchmark case 构造不被认可 | 中 | 高 | P0 | 明确 case generation、来源许可、公开脚本和 baseline；已固定 EPFL `v2025.1` 主来源并建立来源清单 | active |
| R05 | OpenSTA/Yosys/ABC 工具链卡住 | 低 | 中 | P1 | Yosys/ABC 已完成正式 runner 接入，5-case local smoke formal 5/5 pass、ABC baseline 5/5 success；OpenSTA 已在 WSL2 Ubuntu 24.04.4 构建并通过最小 Liberty/Verilog/SDC smoke，但 Stage B 路径桥和 report parser 仍待接入 | watch |
| R06 | failure-aware 反馈效果不明显 | 中 | 高 | P0 | 做失败类型消融，必要时调整主贡献为 benchmark flow + ranking | watch |
| R07 | ranking 贡献不够强 | 中 | 中 | P1 | 第一版作为补强贡献，不作为唯一创新点 | active |
| R08 | 文献综述不完整 | 低 | 中 | P1 | 已完成 25 篇 A 级全文和 1 条 B 级官方证据；写作结构获批后形成 Related Work 初稿，DAC 2018 保持 B 级边界并定期复核 | active |
| R09 | 项目无版本管理导致混乱 | 中 | 高 | P0 | 已初始化 Git并完成首次提交范围审计；待确认 A-only 范围、Git 身份和发布属性后创建基线 | mitigated |
| R10 | 投稿目标不明确 | 中 | 中 | P1 | Phase 6 前确定中文期刊/会议目标 | pending |
| R11 | 当前 c432/c499/c880 的第三方来源未声明 license | 高 | 高 | P0 | 仅保留为本地 smoke；论文主集迁移到 EPFL `v2025.1` MIT 数据，发布包排除未获许可文件 | active |
| R12 | 本地 SAT Sweeping 2006 PDF 的文件名与正文错配 | 高 | 高 | P0 | 原错配文件保留追溯并禁止引用；已从 Cadence Labs 原始链接的 Common Crawl 归档恢复正确全文并升级为 A，source manifest 固定归档定位、正确/错配 SHA 和再分发边界；正确副本只留在忽略提交的核验缓存 | mitigated |
| R13 | 本地 buffer insertion PDF 的年份/venue 标签误标 | 高 | 中 | P1 | 正文、DOI 和 DBLP 已确认文件实际为 2012 IEEE TCAD 扩展版；核心笔记固定 journal 书目并保留 ASP-DAC 2006 preliminary 关系，不按文件名引用 | mitigated |
| R14 | DAC 2018 cost-aware multi-target 论文无合法公开全文 | 中 | 中 | P1 | OpenAlex/Semantic Scholar/Crossref、NTU 机构记录、作者站点和归档资产已复核，仍只有 closed/出版者入口/受限文件；source manifest 只允许使用正式书目、摘要和 ICCAD 2017 问题规范 | active |
| R15 | BUFFALO 文件名、artifact 和结果叙事不一致 | 中 | 中 | P1 | source manifest 固定实际 ICCAD 2025 版本；只按 Table IV 写最大 71.10% TNS，83x 限定为代表性单网，未公开代码/数据时只进入 discussion | mitigated |
| R16 | ML timing 论文的速度、泛化和可复现性被过度外推 | 中 | 高 | P1 | source manifests 固定 4154x 的 opt+route+STA 对比口径、130-nm 到 7-nm 且含一个 7-nm 训练设计、未公开处理后数据/模型/Cadence flow；只作为表示与泛化边界证据 | mitigated |
| R17 | 原始论文、课题材料或许可不完整 benchmark 被误写入 Git 历史 | 高 | 高 | P0 | `initial_commit_scope_audit.md` 将当前 241 个候选分为 A 核心 135、B 本机 smoke/不可移植产物 51、C 私有/版权材料 55；禁止全量 `git add .`，staging 后强制复核路径与大小 | active |
| R18 | 首次提交因隐式行尾/编码归一化产生大面积不可审计改动 | 中 | 中 | P1 | A 类非法 UTF-8/冲突/尾随空格已清零；当前仍有 8 个 mixed、11 个 CRLF-only、16 个 BOM 文件，首次 staging 前显式决定 `.gitattributes`，不在无批准时批量改写 | active |
| R19 | 目标算法文档领先于当前工程实现 | 高 | 高 | P0 | `faeco_algorithm.md`、`failure_taxonomy.md` 已标记为目标规范；`method_rewrite_readiness.md` 逐项固定 ready/partial/blocked，论文以代码和实验产物为第一事实源 | active |
| R20 | ABC baseline 依赖缺失 alias，optimized Verilog 又不受当前 parser 支持 | 低 | 中 | P1 | 已在正式 runner 中使用 `yosys-abc -s` 和 Berkeley ABC 官方 `resyn2` 展开序列，保留 optimized BLIF，并从 ABC `print_stats` 提取 AIG node/level；后续迁移 EPFL 主集时继续按同一规则回归 | watch |
| R21 | EPFL 来源可规范化但 Yosys JSON importer 尚未实现 | 高 | 高 | P0 | 8 个 Verilog 对官方 BLIF CEC 已通过，Yosys JSON 已获批为权威内部格式；下一步实现 JSON gate/level 统计、escaped identifier 映射、case metadata 和 formal 回验产物 | active |
| R22 | Windows runner 与 WSL OpenSTA 的路径语义不一致 | 高 | 高 | P0 | OpenSTA 本体和 `/mnt/d/...` smoke 已通过；在接入 STA runner 前仍需设计并测试 Windows 到 WSL 的 Liberty/Verilog/SDC/report 路径转换，命令、工作目录和产物路径写入实验日志；未通过前不报告正式 WNS/TNS | active |
