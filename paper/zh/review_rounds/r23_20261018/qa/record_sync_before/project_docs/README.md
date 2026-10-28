# 项目过程文档

当前执行（2026-10-18/LOG139）：用户新指令“审稿中文稿”，r23全稿只读审稿，输入2d76968c…/领域角色fcd0e2e2…与contract QA1a3651b0…已实际注册，五same-family新forknone席先盲标准再看稿，NOT_CALIBRATED/目标期刊未确认；最终报告未齐。HEAD/codef761不变，不改稿图/源或新EDA。D仅producer56/56完成（remaining106a6234…/monitor30098530…，active-failed空），正式accepted28/raw3，56+全部8包post两门未齐前仍锁不commit。本轮不启动D终验归档/修源。新交接handoff_20261018_r23.md，旧r22交接保原件。

A8限定修订已接受（LOG120）：proof/双语句表、EN包含布局/38页视觉、当前PDF与四metadata同步获独立+根472b441b接受；OI050此门closed，ZH173ae809…/ENc2783046…为当前工作稿，未完成其它科学/作者投稿门。D诊断caption v2已根接受，仍仅预览。

D计时环境（LOG110）：科学STA并发≤2电路；期间另有mock QA、7z压缩恢复、串行A8 SEC与TeX/Poppler，整机非独占benchmark。输入/结果/actualSTA计数不变，observed walltime不直接用于独占或跨方法速度因果。

本目录存放项目过程与治理文档，而非源码。

当前r21论文审稿与配图入口为 `../paper/zh/review_rounds/r21_20261014/editorial_decision.md`；计数与图件交叉表见 `evidence/R21_FIGURE_EVIDENCE.md`。当前稿为12页、7图14表的工作修订，历史v18基线保留。

**历史阶段7231→source修复（后已由f761替代；以下为当轮记录，不作当前指令）：** 用户于2026-10-18明确“继续推进 做好记录”，当轮授权为继续执行。唯一工作区 `D:/BaiduSyncdisk/01_Papers/03_FAECO`，当前main阶段提交为 `7231e0296da357df435414f75b0a41fe78265837`（941files），origin/main已实际push到7231e02（session60883 exit0）；C′原始source pin仍3ea0f75不回写。归档/图件审查已齐，当前进入S/SPEF修复计划先红后绿，生产可按明确文件归属改动，整体回归/独立review/源码新commit后才注册正式EDA；不恢复已结束的session9345。

**C′v3全72已独立验收。** `project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json`（SHA `a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738`）实核8电路×9臂、all_matrix_verified/source_stable/completion_set_frozen_at_start均true，72个当前completion SHA匹配。8458候选评估记录、6858 candidate_ideal STA+72初始baseline=6930实际STA过程，other0，192保留提交；每终点独立SEC均非零proven/0unproven。physical/electrical/S均false，不能称物理STA。最终审计exit0/runtime46.546s；剩54原运行wrapper3728s/exit0。stage72五件script/log/invocation/receipt/原运行log保真归档；旧51/54/v1失败/v2仅注册原件不覆盖。

当前接受协议是严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不关闭setup_tns预算。零收益与不利结果保留，不调参制造正结果。完整16个weighted/uniform配对已按所有重复同base轮独立核查，5454次交叉比较cut/pool/dispatch全同、16终点全文同（FIGURE_CPRIME_REVIEW269205b9…）；本矩阵未观察到独立权重收益，重复轮不是独立统计样本。新C′不替代旧B3/C/D。

完整v8历史收据为969pass/4skip/156subtests、170源码SHA稳定，OI040/041实现门closed；A6/B2/B17实际对象新证明已各自绑定原pin，B3主线51QA及C作者84/独立注册38QA、原OI042反例拒绝仅关闭工具实现门，尚未新clean pin正式登记同族EDA。四态支持仍open，实际三态/显式Z/switch须unsupported非pass。中英稿时钟元数据OI043已两遍编译/38p视觉/副本验收，仅设置说明门closed；科学回填和投稿声明仍待。


当前接受协议为严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不意味着关闭setup_tns预算。W0/s27首候选WNS -.27→-.26但TNS -.49→-.50，被setup_tns硬门拒。零提交/零WNS收益如实保留，不为正结果调参。最终审计分开理想候选、baseline/refresh/physical STA与提交。

| 子目录 / 文件 | 角色 |
|---------------|------|
| `WORK_PROGRESS.md` | 工作进度（倒序，最新在上） |
| `LOGS.md` | 总工作日志（按时间正序追加，便于回溯查询） |
| `OPEN_ISSUES.md` | 未决问题追踪（未解决持续保留，必须告知用户） |
| `RECORDS.md` | 记录体系总览（所有记录点 + 默认强制更新要求） |
| `agent_handoff/` | 交接入口与状态（README → START_HERE → CURRENT_STATUS → TASK_BOARD → CURRENT_RUN_HANDOFF） |
| `reports/weekly/` | 周期性总结（周报） |
| `baselines/` | 具名基线：绑定论文、源码、测试与证据 |
| `versioning.md` | 版本管理策略（代码 / 测试多版本、基线绑定） |
| `ARCHIVE_POLICY.md` | 归档与版本迭代规范（各对象何时/如何归档） |
| `FILE_ORGANIZATION.md` | 文件分类与命名规范（按实验/版本/类型分，防混块） |
| `evidence/` | 不可变实验证据与结论交叉表（含 CROSSWALK_TEMPLATE 论文-证据交叉表模板） |
| `design_specs/` | 项目立项评估（创新性评估）与专项设计规范 |
| `review_history/` | 评审历史：论文审稿轮次（REVIEW_ROUND_TEMPLATE）+ 工程审查报告（代码/设计/实验，ENGINEERING_REVIEW_TEMPLATE） |
| `archive/` | 退役版本与迁移历史 |
| `migration/` | 迁移记录 |
| `worktrees/` | 临时工作树注册表 |

分工：技术文档（面向实现）见根 `docs/`；这里只放过程与治理内容。
