# 归档索引（ARCHIVE_INDEX）

> **用途**：回答「这份文档为什么不见了 / 现在该看哪一份」。
> **规则**：本索引只登记**去向**，不重复内容。现行口径一律见 [CANON.md](CANON.md)。
> **建立**：2026-10-28。

---

## 1 本轮归档（2026-10-28）

### 1.1 `archive/2026-10-28_superseded/plans/` —— 互相冲突的方案（2 份）

| 文件 | 归档原因 | 现由谁取代 |
|---|---|---|
| `FAECO_R94_DATA_TO_LOOP_PLAN_20261028.md` | 五条方向中**三条与既有裁定冲突**、三个关键数字与证据不符（H1 「CI 跨 0」实为 CI `[0.052976, 0.177924]` 不含 0；H2 对象错位；「s713 比随机慢」无此读数） | CANON §8「已否决，不得重启」 |
| `FAECO_R94_SALVAGE_PLAN_20261028.md` | 路线 I/II 的判据逻辑已被同日 r94 读数取代（门槛与兑现率的关系、类型构成） | CANON §7、§8 |

### 1.2 `archive/2026-10-28_superseded/reports/` —— 已被取代的报告（4 份）

| 文件 | 归档原因 | 现由谁取代 |
|---|---|---|
| `FAECO_STATUS_20261028.md` | 项目状态报告，早于同日 r94 决定性读数 | CANON §0–§2 |
| `STORAGE_AND_VERSION_AUDIT_20261028.md` | 体积与版本盘点 | **PROJECT_MAP §2 §4** |
| `STORAGE_DISPOSAL_20261028.csv` | 358 行逐目录处置清单 | PROJECT_MAP §6（只留待办项） |
| `STORAGE_AUDIT_20261021.md` | 上一轮存储审计（其 NTFS 压缩方案**已实测失效**，压缩率 1.0） | PROJECT_MAP §2 §6 |

> `STORAGE_DISPOSAL_20261028.csv` 如需按原清单逐条核对体积，仍可查；但**判定结论以 PROJECT_MAP 为准**。

### 1.3 `archive/2026-10-28_superseded/planning_done/` —— 已执行完的轮次方案（15 份）

**FAECO 轮次方案（13 份，全部已执行完毕，论文已交付至 r28）**

`FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md`、`FAECO_R14_DEFENSIVE_PURGE_PLAN_20261013.md`、
`FAECO_R15_DEFENSIVE_PURGE2_PLAN_20261013.md`、`FAECO_R16_TERMINOLOGY_CALIBRATION_PLAN_20261013.md`、
`FAECO_R17_LOGIC_CALIBRATION_PLAN_20261013.md`、`FAECO_R18_FIG2_REPLACE_PLAN_20261013.md`、
`FAECO_R19_POSITIONING_RESTRUCTURE_PLAN_20261013.md`、`FAECO_R20_NARRATIVE_CONVERGENCE_PLAN_20261013.md`、
`R22_ABLATION_DESIGN_REVIEW_20261014.md`、`R22_CODE_REVIEW_20261014.md`、
`R22_EVIDENCE_CLOSURE_PLAN_20261014.md`、`R22_CORRECTNESS_RESUME_PLAN_20261016.md`、
`R22_S_SPEF_REPAIR_PLAN_20261018.md`

**7 月旧方案（2 份，早于 FAECO 框架）**

`RSECO学长论文接手发表方案.md`、`项目重启与论文推进方案.md`

> **`planning/` 现存仅 4 份**：`README.md` + `FAECO_V2_DESIGN_PLAN_20260923.md` + `FAECO_V2_IMPL_CONTRACT_20260923.md` + `FAECO_V2_TECH_DESIGN_20260923.md`（V2 实现契约仍可能约束代码，故保留）。

---

## 2 已加失效横幅、**未移动**的顶层文档（10 份）

移动会造成断链（这些文件被 5–13 处引用），故采用**头部横幅**：打开即见「已停用 → 看 CANON」。

| 文件 | 最后实质更新 | 其内容现由谁承担 |
|---|---|---|
| `mainline.md` | 2026-08-03 | CANON §0 §2 |
| `roadmap.md` | 2026-08-03 | CANON §8 |
| `milestones.md` | 2026-07-31 | CANON §1 |
| `long_term_task_plan.md` | 2026-08-03 | CANON §8 |
| `risk_register.md` | 2026-08-03 | CANON §10 + PROJECT_MAP §5 |
| `RECORDS.md` | 2026-08-11 | `LOGS.md` |
| `decision_log.md` | 2026-09-08 | CANON §5「已裁定不可翻」 |
| `future_task_backlog.md` | 2026-09-08 | CANON §8 |
| `ARCHIVE_POLICY.md` | 2026-08-11 | 本文件 §4 |
| `FILE_ORGANIZATION.md` | 2026-08-11 | PROJECT_MAP §2 |

---

## 3 未动、仍可查的历史（原位保留）

| 位置 | 数量 | 为什么不动 |
|---|---:|---|
| `agent_handoff/`（含 `status_logs/`） | 41 + | 时序交接记录，有 `README.md` 索引。**只读最近一份**（`handoff_20261028_r93.md`）与其 README |
| `reports/` | 其余 9 份 | 多为实验报告（L2/L3/S/ELECTRICAL 等），被 CANON §5 引用为「已裁定」的依据 |
| `review_history/` | 22 | 审稿历史，溯源用 |
| `design_specs/` | 8 | 设计规格，可能约束 `code/` |
| `evidence/` | 426 MB | **论文每个数字的唯一来源**，逐条绑定 `PAPER_EVIDENCE_MANIFEST.md`，**禁动** |
| `archive/`（旧） | 11 份 + 子目录 | 早于本轮的归档，保留 |

---

## 4 归档规则（以后照这个判）

**该归档**：
1. 「最新进展 / 主线 / 路线图 / 里程碑 / 状态报告」类文档 **超过 2 周未更新**。
2. **已执行完毕**的轮次方案（该轮产物已进 `review_rounds/` 或论文）。
3. 被新读数**取代**的分析报告。
4. 同一问题存在**两份及以上互斥说法**时——保留一份进 CANON，其余归档。

**不该归档**：
1. `LOGS.md`（只追加）、`OPEN_ISSUES.md`（容器）。
2. `evidence/` 下任何东西。
3. `versions/` 的 MANIFEST。
4. 冻结论文的任何副本。

**铁律**：归档 = **移动 + 登记本索引**，**不删除**。删除只在 `PROJECT_MAP §6`「清理待办」里、经确认后执行。
