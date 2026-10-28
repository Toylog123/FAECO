# 行为准则

## 1. 质疑优先（Challenge-first）

任何请求、方案、结论、数字在验证之前都是**待检验假设**，不因来源而自动采信。

| 怎么做 | 不要做 |
|--------|--------|
| 执行前先独立评估目标、约束、证据、风险与顺序 | 因用户/上级/主流/既有代码/历史结论而跳过评估 |
| 发现薄弱、证据不足或更优路径时，附具体依据说明 | 空泛否定或默默执行 |
| 证据与既有结论冲突时，以证据为准 | 为维持一致性而忽略新证据 |
| 对自身产出同样保持审查：找错误、缺口、过度声称 | — |

## 2. 质量不打折

| 怎么做 | 不要做 |
|--------|--------|
| 硬件/关键设计实施前先评审，确认目标与约束再动手 | 跳过评审直接编码 |
| 默认追求更稳、更快、更清晰的实现 | 满足于"能跑" |
| 需要时大改/重构/重写，力度服从质量需要 | 因害怕修改而只做小修小补 |
| 论文困难时以完善设计、补足实验来提升 | 用弱化声明、缩小范围来应付 |
| 降级是最后手段，须说明原因、影响与恢复路径 | 因时间/便利而轻易降低目标 |

## 3. 自我批判（自杀式测试）

实验 / 设计立项前，先做反驳性检验——先想清楚"什么结果会推翻我的主张"，先跑那个测试。

| 做法 | 不要做 |
|------|--------|
| 立项前先问"什么结果会推翻我的主张"，并优先设计并运行该测试 | 只跑支持自己结论的实验 |
| 主动与最强竞争基线对比 | 只与弱的 / 自设的基线对比 |
| 主动测失效场景（边界、G 失效、异常输入、退化） | 只测理想 / 顺利路径 |
| 主动测最不利初始条件（热启动、长尾、冷缓存） | 默认用最有利初始状态 |
| 预判审稿人可能点名的测试，提前自己做 | 等到评审再补 |
| 措辞 / 结论修订后做最终一致性检查 | 改完措辞不回溯结论 |

## 4. 结果归因（实验结果与预期不符时）

结果不符预期时，**先分析归因，不急于否定**——很多时候只是实现问题，而非最初的想法不行。

| 做法 | 不要做 |
|------|--------|
| 先区分问题层次：实现 bug / 设定缺陷 / 环境问题 / 数据问题 | 直接把"结果不符"归咎于想法不行 |
| 逐层排查：复现 → 校验输入 → 检查实现 → 对照设定假设 | 跳过排查直接下结论 |
| 实现问题：修复后复跑；想法仍成立则保留原方案 | 因实现 bug 而放弃原方案 |
| 设定缺陷：用证据确认"想法本身不成立"后才调整 / 放弃 | 凭直觉否定初始设定 |
| 归因结论写入实验记录与经验库（`docs/EXPERIENCE.md`） | 结果异常不记录、不分析 |
| 区分"实现可修"与"设定需改"，分别处理 | 把两者混为一谈 |

## 5. 记录与文档同步（实时记录）

**工作过程中边做边记、同步记录，不做事后补记**——完成一个动作随即记录，不留到收尾。**所有相关文档都要随工作同步更新，不只下列几个。**

**专职记录（多智能体时）**：分配一个智能体专门负责实时记录与文档同步，其他智能体专注执行。

**文档更新清单**（按触发时机更新对应文档，完整见 `project_docs/RECORDS.md`）：

| 触发时机 | 要更新的文档 |
|----------|--------------|
| 每个关键动作 | `project_docs/LOGS.md`（总日志） |
| 每轮结束 | `project_docs/WORK_PROGRESS.md`、`agent_handoff/status_logs/CURRENT_STATUS.md`、`agent_handoff/TASK_BOARD.md`、`agent_handoff/CURRENT_RUN_HANDOFF.md`、`agent_handoff/NEXT_AGENT_PROMPT.md` |
| 发现问题 | `project_docs/OPEN_ISSUES.md` |
| 解决问题 | `docs/EXPERIENCE.md`（经验库） |
| 每次实验 | `project_docs/evidence/EXPERIMENT_REGISTRY.md`（登记，防重复做） |
| 每次改论文 | `paper/zh/CHANGE_LOG.md` |
| 每次改图 | `paper/zh/figures/CHANGE_LOG.md` |
| 审稿轮次 | `paper/zh/review_rounds/r<N>/` |
| 结构 / 路径变更 | `README.md`、`AGENTS.md`、`.codex-handoff.json`、`project_docs/README.md` |
| 版本相关变更 | `project_docs/versioning.md`、`baselines/` |
| 术语 / 译名变更 | `docs/GLOSSARY.md`、`paper/GLOSSARY.md` |
| 数据 / 结论变更 | `project_docs/evidence/`（交叉表、索引） |
| 每周日 | `reports/weekly/2026-W##.md`（周报） |
| 自检 | `bash code/scripts/check_record.sh` |
| 未解决的问题登记并持续保留，必须告知用户 | `project_docs/OPEN_ISSUES.md` |

## 6. 先查既往（复用优先）

遇到问题时，**先查之前怎么解决的，能复用就适配，不重造**——避免浪费已推进的工作。

| 做法 | 不要做 |
|------|--------|
| 动手前先查：`docs/EXPERIENCE.md`（经验库）、`versions/`（历史版本）、`project_docs/evidence/`（既有证据）、git 历史 | 从头重新解决 |
| 之前版本已推进的实验 / 代码 / 脚本，**适配后复用**，不重新实现 | 无视历史重新搭建 |
| 复用前校验：来源版本、输入、口径、是否适用当前需求 | 直接照搬不校验 |
| 适配修改记录到 `LOGS.md` / 经验库 | 适配了但不留痕 |
| 查不到再新做，并登记经验供后续复用 | 每次都重来一遍 |

## 7. 改动后整体验证（部分改动 → 整体回归）

设计 / 代码改动部分模块后，**放回整体做集成 / 回归测试**，确保测的是当前版本，而非旧版或别的设定。

| 做法 | 不要做 |
|------|--------|
| 改动部分后，放回整体做集成 / 回归测试 | 只测改动部分，忽视整体 |
| 测试前确认被测对象 = 当前版本（当前设想 / 基线） | 测的其实是旧版本 / 别的设定 |
| 每个测试记录：被测版本、输入、设定 | 不同版本 / 设定的结果混在一起 |
| 测试输入与结果一一对应（交叉表 / manifest） | 结果与输入不对应 |
| 回归不过：先确认测的是对的东西，再归因 | 用错版本的结果下结论 |

## 8. 运行监测（长任务防卡死）

运行测试 / 实验 / 构建等长任务时，设置超时并监测进度，避免卡死空等。

| 做法 | 不要做 |
|------|--------|
| 长任务设置合理超时（按任务复杂度） | 无限期等待 |
| 定期检查进度 / 日志，确认在推进 | 挂着不管直到超时 |
| 用超时包装工具运行长任务（`code/scripts/run_with_timeout.sh`） | 直接裸跑不设超时 |
| 卡死 / 超时后：先查日志定位卡在哪，再处理 | 盲目重跑 |
| 监测结果记录到日志 / 经验库 | 卡死经历不记录 |

## 9. 实验记录与实查（防混淆）

每次实验必须记录配置与结果，引用时**实际查看**，不凭印象。

| 做法 | 不要做 |
|------|--------|
| 每次实验：运行前记录配置（参数 / 版本 / 输入），运行后记录结果 | 实验不记录配置或结果 |
| 配置与结果一一对应（实验记录 / evidence 包 / 交叉表） | 结果不知道对应哪个配置 |
| 引用任何数字前，**实际打开证据文件确认** | 凭印象 / 记忆引用结果 |
| 配置变更时明确标注，不与旧配置混用 | 改配置不记录，误当旧结果 |
| 结果归入 evidence 包并登记索引 | 结果散落无登记 |

## 10. 并行协作（多智能体并发）

能并行的就并行——可分解的独立子任务默认多智能体并发，不串行。

| 做法 | 不要做 |
|------|--------|
| 任务可分解为独立子任务时，默认并行派发多智能体 | 逐个子任务串行等待 |
| 识别依赖关系：相互独立的并行，有依赖的才串行 | 把无依赖的任务硬排成顺序 |
| 每个并行子任务有明确产出与归属 | 并行但职责不清、结果无人负责 |
| 并行结果汇合后统一审查（同样过证据 / 质量门） | 并行结果直接采信不复核 |
| 关键路径 / 高风险步骤留在主线亲自推进 | 关键路径也盲目外包 |
| 并行规模匹配任务复杂度，不为并行而并行 | 过小任务也强行拆并发 |
| 派发子智能体后**监控是否有实际进展**（消息 / 工具调用 / 产出），无产出视为卡住 | 派发后盲等，子智能体空转 |
| 子智能体卡住（超时 / 无产出）：先查其日志 / 输出定位，再重启或降级串行 | 无限期等待卡住的子智能体 |

# 工程纪律

## Git

| 时机 | 动作 |
|------|------|
| 阶段性工作完成（功能门/实验包/论文一轮） | `git commit` + `git push` |
| 里程碑成果（对应基线） | `git tag <基线ID>` |
| 重大改动/重构/实验切换前 | 先 commit 或 tag 固化当前状态，保证可回退 |

## 破坏性操作防护（可回撤）

删除 / 覆盖 / 大规模重构等操作前，确保可回退：

| 做法 | 不要做 |
|------|--------|
| 删除 / 覆盖前，先确认该路径已在 git 提交（可回滚） | 未提交就删除 / 覆盖 |
| 不可 git 回滚的（未跟踪 / 大文件 / 仓库外目录）先手动备份 | 直接删除无备份 |
| 破坏性操作前先 `git status` 确认工作区状态 | 不看状态就删 |
| 删除文件用 `git rm` 或先移动，不裸 `rm` | 裸 `rm` 误删无法恢复 |
| 大规模重构前先 commit / tag 固化当前状态 | 改一半才发现回不去 |

## 版本隔离

| 规则 | 说明 |
|------|------|
| 版本完整体 | 每版本自包含 `code/`+`project/`+`experiments/`+`docs/` |
| 零交叉引用 | 禁止新版本引用旧版本文件（含脚本）；需要就复制 |
| 冻结流程 | 阶段完成→打基线+tag→完整复制进 `versions/<基线ID>/` |
| 主目录=最新 | 根 `code/` 等始终是当前最好版本 |
| 详见 | `project_docs/versioning.md` |

## 目录卫生

| 放哪里 | 什么内容 |
|--------|----------|
| 根目录 | 仅 `AGENTS.md` / `README.md` / `.gitignore` / `.codex-handoff.json` + 受跟踪目录 |
| `scratch/` | 临时脚本/补丁/探针（git-ignored） |
| `code/scripts/` | 证明有用的脚本晋级到此 |
| `code/tests/` | 测试 |
| `code/src/` | 源码（按模块） |
| `project_docs/` | 文档合并同类项，不叠加重复 |

## 文档同步

结构/路径变更后**同一次提交**内更新对应文档：`README.md`（目录角色+快速开始）、`AGENTS.md`、`.codex-handoff.json`、`project_docs/versioning.md`（涉版本时）。

# 接手者入口

从 `project_docs/agent_handoff/README.md` 开始，按阅读顺序加载全部上下文——仓库须随时可无口头交接。

## r22专项入口（2026-10-18当前执行；历史失败保留）

- 当前状态（2026-10-19/LOG258）：r27完整中文主文/补充黑白灰工作稿已交付；main1d3b94f4/9d0394e8为10页7图6表8554CJK/14refs，补9886b68a/27ac11ab为9页5图12表9632CJK。内置模型两示意图+7量化图、双遍编译/DeviceGray19页严格灰度/根全页视觉/各3PDF同步均完成，FINAL_DELIVERY10701c76。科学正文仅图路径和两色词变化；AI原生RGB细差/字体提示/序列化微差明记。无新EDA/production/HEAD改动，四partial/D正式28/56raw3/8/OI051与HEADf761两门锁保持，不提交。
- 用户10-18明确“继续推进 做好记录”，继续授权有效。当前main/origin均`f761ee1996a83fc4f0f3de0999b74d85a8237858`：source/evidence阶段1278files已实际commit+push；当前完整v5为1056pass/156subtests、174code.py前后/当前/ZIP一致，无skip/warnings，最终独立67da65a4…限定接受。code树clean，实时记录可dirty；旧v1/v3/v4失败及v2受限环境原件保留，不作当前待修/待commit指令。
- A8限定修订已接受（LOG120）：原A8同批SEC、双语句表、EN局部布局/38页视觉/副本metadata获独立+根472b441b接受，OI050此门closed；不外推其它科学/投稿。该A8当轮ZH173ae809…/ENc2783046…（ZH当前另以r24为准），D诊断captionv2获根文本接受，原图不重绘。
- D正式矩阵fd336745…/f761固定，45执行源/121provenance/actualLib。当前producer56/56全部完成（remaining106a6234…/monitor30098530…），根冻结28与不同owner v3/根f14c3306…正式接受28，仅该subset/extra不计/full56false。余42同清单已finished/rc0/5898.406s；60秒监测99002已观察batchreceipt自动收束（68c282be…），不再记运行中/不重启；完整56独立+根验收及8/8case归档根post都齐前HEAD/code锁不commit。D完整raw根接受3/8=s27/s382/s420（s420 postecc44332…）；其余逐case接受后准入，不能因新producer完成擅称根接受。v3 f6b053df…严格分实际STA-cache/hash去重/preSTA拒绝，旧宽cache不叫纯STA复用；原v2失败保历史。
- D计时环境（LOG110）：科学STA并发≤2电路；期间另有mock QA、7z压缩恢复、串行A8 SEC与TeX/Poppler，整机非独占benchmark。输入/结果/actualSTA计数不变，observed walltime不直接用于独占或跨方法速度因果。
- 后续全56独立原件审查入口固定为`project_docs/evidence/r22_D_revalidation_20261018/ledger_duplicate_diagnosis_20261018/checker_v3.py`（f6b053df…）；原checker_v2/TOOLS_PREPARATION保历史。当前28的900/930不是未来全56已登记timeout，全56按实测量/runtime另登记并持续监测。
- D14原件在`project_docs/evidence/r22_D_revalidation_20261018/`；s27/s382两raw包已producer+根逐SHA后验接受（D2/8case），其它6需完成/验收后准入。当前2case fixed/adaptive机制诊断限该四对象：EMA真实更新传入cut，更新后dispatch无新身份、evaluator前去重，不据此声称普遍无效或改去重造收益。
- 历史C′v3科学runtime pin仍3ea0f75，独立全72验收a34da9c3…、8458评估/6858candidate ideal STA+72baseline=6930实际STA/192提交，终点SEC均非空通过；八C′raw包根接受已齐。7231e02是已push的C′归档/图审查历史阶段，不是当前HEAD。旧51/54/v1失败/v2仅注册均保留；结束session9345不恢复/重跑。C′独立16配对5454 same-base trace交叉比较和终点一致，只说明本矩阵未见独立权重收益，不是5454独立样本或普遍无效结论。
- 当前已复现S证据/共享normalizer输入绑定、OI047模型子集、OI048 source/mapped top/status/source-window实现门已随f761限定闭合；tiny真实OpenSTA ordinary/escaped注入获根与不同owner56bdc6b1…接受。四态能力、b18 inout域OI046、显式bytes注入已复现的timeout呈现OI049（待D后修）、历史OI048/P08 proof对象影响及S/SPEF科学效果仍open，不将实现验收外推历史结果。s382旧RC配方仍unknown；旧258 filtered模型defect实为审计器!解析问题，V2为0mismatch/unknown，不反用旧错误审计否定模型。
- 当前pin外部B3/C adapter mocked QA分别51pass/84pass及3901临时件完整ZIP获根7b62e0e9…接受；5810稳定来源为174code.py+B3树5628+C树8，不叫5810生产文件，不force-add旧sandbox整树。它不是B3/C正式同族EDA或历史runtime身份恢复；B3/C科学对象与配置仍须独立登记，不拼C′/D结果。
- 英文工作稿`paper/en/manuscript/FAECO.tex`/预览`paper/en/build/FAECO.pdf`，中文12页/英文26页均7图14表；科学回填/投稿材料未齐。OI043仅周期元数据门已双语编译/38p视觉/副本同步关闭。真实三态/显式Z/开关原语须unsupported非pass，不能删除Z或用二态cut冒充四态。
- 图件：C′全72预览`r22_matrix_gain_cost_v3`已数据/几何/6.8pt/根与独立视觉通过；D两例机制预览`r22_D_feedback_mechanism_v1/iteration02`已作者与根独立rawCSV/实际PNG-PDF视觉3067eb58…接受，7pt/碰撞对齐通过。两者均未因此插入主稿/替换旧科学图，预览不等投稿格式验收，旧失败/iteration保留。
- 接手先读`project_docs/agent_handoff/handoff_20261018_r22.md`与CURRENT_STATUS；正式命令/计数以各manifest/原始台账/收据为准，候选评估、实际STA、缓存、提交分别计数。新数据/库/源码变化必须停止并归因；历史恢复见`project_docs/evidence/r22_historical_audit_20261014/HISTORICAL_RECOVERY_REPORT.md`，新族不跨族替代旧科学结果。

## 当前论文图件入口（2026-10-14，r21）

当前图件生成器为 `paper/zh/figures/data/scripts/review_r21_figures.py`；图1/2矢量源在 `manual/figures/`，图4–7数据图及CSV在 `data/final/`。旧全量 `gen_figures.py` 含历史硬编码，保留作历史，不用于重建当前图件。审稿与计数验收见 `paper/zh/review_rounds/r21_20261014/`；原始实验族必须继续隔离，STA测量计数须排除缓存复用和前置拒绝，旧schema缺字段时不得猜测实际次数。

## r23中文只读审稿历史完成（2026-10-18，LOG149；当前转r24）

历史完成状态（2026-10-18/LOG149）：r23中文只读全审完成，Major Revision，20意见/22路线图（8 must_fix、14 should_fix）；报告`paper/zh/review_rounds/r23_20261018/REVIEW_REPORT.md`及root crosscheck/最终SHA回执齐。五席十阶段及机械合成PASS≠科学全部通过，模型家族/provider身份未知，不称独立专家验证。Integration既有目标保留，本轮仅无正式criteria绑定。正文/图件/代码/HEADf761不变，无新EDA。D producer56已完成但accepted28/raw3，56+8post两门齐前不提交。下一轮按路线图与现有证据修订，不能重复证明A8/b17或跨族补旧科学结论。


## r24中文稿与配图历史交付（2026-10-18，LOG205；当前转r25）

当前r24作者修订交付已完成，最终源a2349e07/PDF142ddba6与build05/根视觉/三副本/9批最终包已实际绑定，交接见project_docs/agent_handoff/handoff_20261018_r24.md。四partial与D28/56raw3/8/旧族/四态/原raw SPEF OI051等继续pending，不把本轮成稿当科学全关或投稿终稿，不提交/不改生产HEAD。


## r25历史交付（2026-10-18，LOG225；当前转r26）

当前状态（2026-10-18/LOG225）：r25主线压缩工作稿已交付，主文0c8b/abfa为5页3图2表3638中文字符；独立补充eb9/626b为10页6图12表。区域构造→覆盖优先调度→同endpoint收益/实际STA成本为主线，负面与限制保留。main_build03/Sup_build02编译/全15页根视觉/两组各3PDF同步均完成，字体替代提示保留；9图字节未改，无新EDA/production改动。r24四partial及D正式28/56、raw3/8不变，HEADf761两门锁不提交，非投稿终稿。

主文`paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`；独立补充`paper/zh/manuscript/FAECO_补充材料.tex`。进入manuscript目录，显式选相应TeX分别LuaLaTeX双遍，不能自动猜主文件。当前身份与科学未决见handoff_20261018_r25及CURRENT_STATUS；r25 FINAL_DELIVERY及两ROOT_VISUAL_QA为该轮历史回执，旧包保历史。

## r26历史交付（2026-10-18，LOG243）

当前状态（2026-10-18/LOG243）：r26完整中文论文已交付，主文e841/d0c7为10页7图6表8554CJK，补充44ba/5bae为9页5图12表；恢复论证而删重复，区域→调度→收益/成本主线清楚。内置图片模型重做图1/2，量化图原字节保留；双稿编译/全19页根视觉/各3PDF同步完成，字体提示及AI图观察保留，投稿资格未核验。无新EDA/codeHEAD改动，四partial/D正式28/56raw3/8和HEADf761两门锁保持，不提交。

主文/补充TeX路径同当前README，须显式选目标分别LuaLaTeX双遍；r26 FINAL_DELIVERY为历史包，当前以r27 FINAL_DELIVERY为准，图像模型未知身份/工作稿投稿资格边界保留。历史r25的5页稿保before，当前不再压成短稿；科学门以OPEN_ISSUES/当前handoff为准。

## r27当前交付（2026-10-19，LOG258）

当前状态（2026-10-19/LOG258）：r27完整中文主文/补充黑白灰工作稿已交付；main1d3b94f4/9d0394e8为10页7图6表8554CJK/14refs，补9886b68a/27ac11ab为9页5图12表9632CJK。内置模型两示意图+7量化图、双遍编译/DeviceGray19页严格灰度/根全页视觉/各3PDF同步均完成，FINAL_DELIVERY10701c76。科学正文仅图路径和两色词变化；AI原生RGB细差/字体提示/序列化微差明记。无新EDA/production/HEAD改动，四partial/D正式28/56raw3/8/OI051与HEADf761两门锁保持，不提交。
