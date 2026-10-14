# 实验登记表

> 记录**所有做过 / 正在做的实验**，避免重复做。**做新实验前先查本表**。

> **r22当前 paused（用户明确要求，2026-10-14）**：所有EDA已结束，首pilot仅两W0执行后SEC失败停止，**无v2开跑/有效C′结果**。下列规划/修复重跑仅为恢复后的待办；须用户明确恢复，禁止自动运行。最后push28c3c2b，工作区修复尚未新pin，不能将其称原manifest同一对象或全部门通过。

## 登记表

| 实验 ID | 名称 | 版本 | 类型 | 实验定义路径 | 证据包路径 | 状态 | 关键结果 | 运行日期 |
|---------|------|------|------|-------------|-----------|------|----------|----------|
| EXP-001 | example_case | v1 | rtl | `experiments/v1/rtl/example_case/` | `evidence/v1/rtl/example_case/20260811_r01/` | 完成 | … | 2026-08-11 |

## 规则

1. **做新实验前**：先查本表 + `evidence/`，确认未做过（同版本 / 同配置 / 同输入）。
2. **每次实验完成后**：登记一行（或更新现有行），含实验定义路径与证据包路径。
3. 登记表与证据包**一一对应**，防重复、防混淆（版本 / 配置 / 结果）。
4. 查询：按实验名 / 版本 / 类型 / 日期搜索本表，或沿 `evidence/<版本>/<类型>/<实验>/` 定位。

## 与其它文档的关系

- 实验定义：`experiments/<版本>/<类型>/<实验>/`
- 结果证据：`evidence/<版本>/<类型>/<实验>/<YYYYMMDD>_r<N>/`（自包含包）
- 论文数字对照：`CROSSWALK_TEMPLATE.md`
- 分类规范：`../FILE_ORGANIZATION.md`

## 2026-10-14 既有记录重算（非新EDA）

| 登记ID | 类型 | 输入 | 输出 | 结果 |
|---|---|---|---|---|
| DERIVED-R21-STA | 原始台账审计与重绘 | B/D/F既有实验族，r21_source_manifest绑定输入 | r21_20261014/sta_ledger_audit.json、sta_count_followup.md及图件CSV | D 40/40通过，固定/EMA新STA1947/2003，随机均值2480.7；B旧schema不补猜测 |

## 2026-10-14 r22 实验规划与执行登记

| 规划ID | 目的 | 起始版本 | 配置/输入 | 定义/证据路径 | 状态 | 结果 |
|---|---|---|---|---|---|---|
| PLAN-R22-CUT-COST | 新族C′，同运行器双割/cost/顺序可辨识对照 | 起始46ede94；首源码阶段28c3c2b已push，修复工作区尚未新pin | W0/W1/U0/U1/C/UR1/2/3/L九臂×八电路；首manifest锁72commands/8原始input SHA/LIB与工具；0.5ns/20轮/候选STA500/k8/joint_k2/workers1，不拼旧C | `project_docs/planning/R22_EVIDENCE_CLOSURE_PLAN_20261014.md`、`experiments/20261014_r22_cut_ablation/manifest.json` | **paused；首pilot SEC失败，未v2，须用户明确恢复后核修复/新增门再锁新pin** | 无有效C′结果；原失败目录保留 |

本规划获得用户r22“继续推进”新授权，覆盖旧消融暂缓安排。正式运行前必须更新真实revision、输入、参数、超时和预锁判据；运行后按实际证据登记，不补写推测结果。

### r22 已执行静态探针（非EDA）

| 登记ID | 版本/输入 | 定义与证据 | 状态/结果 | 边界 |
|---|---|---|---|---|
| PROBE-R22-LEGACY-GATING | 46ede94；六门DAG g1→g4、g2→g4/g5、g3→g5、g4/g5→g6；critical=[g1,g4,g6]、R={g1,g4}、其余λ=0，比较λc=0/1 | `project_docs/planning/R22_ABLATION_DESIGN_REVIEW_20261014.md` §2，领域评审python -B只读/无文件写出 | **已执行**；旧nonconstrained两λ均cover优先且混备用源，constrained cover在λ=0时第5、λ=1时第1 | 只检来源/门控混杂，无Yosys/OpenSTA，无时序或性能结论；其余12项建议探针未执行 |

### r22 历史派生审计（非EDA）

| 登记ID | 输入/版本 | 输出/执行 | 结果与边界 |
|---|---|---|---|
| DERIVED-R22-HISTORICAL | 既有C六配置臂与b17 180s报告档案；26240文件/git blob指纹，不改变原始数据 | `evidence/r22_historical_audit_20261014/`、`code/scripts/python/audit_historical_evidence_r22.py`；300s timeout，51s/exit0 | b17报告级恢复104，ITC-99独有报告结果2994；C flags/argv/revision分级，完整身份仍缺，s382 v3不自动借用；不运行EDA |
| DERIVED-R22-CORRECTNESS | A/B/D/k1与C12代表已归档accepted/final、SEC脚本/log/gold/gate；410来源/依赖SHA，r21匹配42与既往r22匹配22 | `evidence/r22_historical_correctness_20261014/REPORT.md`、correctness_audit.json/input_hashes.json/audit.py；只读派生审计，无EDA、未改原数据/稿/production | **报告已主线实读确认；后续处置paused**：B完整绑定28/unknown2；A exact可复用2/缺证6；D结构invalid38/40、k1 14/16；C代表结构invalid9/12/unknown3不外推。invalid不推断已证明不等价，unknown非失败；非新SEC/时序实验 |

### r22 预检（未启动电路EDA）

| 登记ID | 输入/输出 | 执行结果 | 边界 |
|---|---|---|---|
| PREFLIGHT-R22-72 | `scratch/r22_preflight_config`，正式计划九臂×八电路配置；执行源码尚未最终冻结 | nativeYosys0.67+146 git468ba27d9dirty/OpenSTA3.1.0/SECYosys0.33版本校验成功，72配置注册 | dryrun只配置与工具版本，不mapping/STA；不当正式运行、不填性能结果，最终源码回归待完成 |
| DRYRUN-R22-LOCKED | `experiments/20261014_r22_cut_ablation/manifest.json`；actualgit28c3c2b、production SHA、8原始输入SHA/LIB、72完整命令 | 三工具版本锁；配置清单已注册 | 仅正式路径的locked dryrun，无mapping/STA；尚未正式执行72运行 |

### C′正式登记（首pilot已执行，SEC失败停止）

| 实验ID | 族/版本 | 输入与配置 | 定义/证据目录 | 状态/结果 |
|---|---|---|---|---|
| EXP-R22-CPRIME-72 | C-prime-r22；首执行git28c3c2b，逐文件SHA锁 | 八ISCAS89原始input SHA/LIB SHA；W0/W1/U0/U1/C/UR1/2/3/L，72完整commands；500候选STA/20轮/k8/joint_k2/workers1等由首manifest决定，3900s包装/3930s硬超时；三工具版本/Python3.11.9 | `experiments/20261014_r22_cut_ablation/manifest.json`及W0/s27、W0/s382、batch_failures.json；预锁计划见R22_EVIDENCE_CLOSURE_PLAN | **stopped / r22 paused**；两pilot SEC失败batch58s/exit1，其它臂未启动；无v2开跑/有效结果。原目录保留，须用户明确恢复再新pin/完整受影响矩阵 |

每个pilot/正式run以该manifest中的真实命令为定义；开跑与完成需逐项补真实时间、退出码、停止原因及证据，不由dryrun注册数推算执行数。若production/config改变，先新钉版本/清单，不沿用此条假称同一对象。

首轮pilot实际命令：`.venv/Scripts/python.exe -u -X utf8 code/scripts/run_r22_cut_ablation.py --output-dir experiments/20261014_r22_cut_ablation --circuits s27,s382`，session66717，batch wrapper43200s。共享mapping2例后仅W0两run启动：s27 runner47s/exit0、s38248s/exit0，最终独立SEC发现helper definitions变化，batch58s/exit1并停止。两run中间WNS不计有效成果。实读STA launch12/11、评估14/13、缓存0/0，差额各2为F1前置拒绝。归因与修复见OI-035/036、LOG-20261014-23；尚无v2正式开跑。


## 2026-10-14 r22用户暂停（不新增实验）

正式v1仅W0/s27、W0/s382，SEC输入helper改变门失败；原目录完整保留。已归档109原文件ZIP与逐文件SHA：r22_preflight_20261014/failed_v1_pilot_snapshot.zip、pause_snapshot_manifest.json。最后全回归667/4skip/156subtests；K1–K6待修，v2未注册/未运行。历史A/D/C审计REPORT已主线确认，不以计数恢复证明合法终点。等待用户明确恢复。
