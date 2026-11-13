# Configurable timing-budget recovery: implementation and qualified endpoint

2026-11-13. This stage implements a fixed-reference policy and bounded combination-search kernel, validates the policy on52 archived physical endpoints, and proves the selected exact endpoint. The measured area result comes from historical reclassification, not a new run of the search algorithm.

## Measured s382 result under the user-selected10ps budget

| Metric | Resizer CONTROL | Selected RESTORE074 | Change |
|---|---:|---:|---:|
| Complete mapped-cell area |1052.2592|1005.9648|−46.2944 (−4.399524375743%)|
| Propagated setup slack (ns)|−0.8484588032153795|−0.851556880565596|−0.0030980773502165|
| Propagated hold slack (ns)|0.4636368511334865|0.46721415625228246|+0.003577305118796|
| TNS (ns)|−13.422542572|−13.654524803|−0.231982231|

The fixed pre-repair CTS area is892.1056, so Resizer net added area is160.1536 and the selected endpoint recovers **28.90625%** of that increment. The denominator excludes synthesis-to-CTS area82.5792. It counts final master differences between the controlled snapshots, not the cumulative area of all transient resizing events. The other13 designs' denominators remain unaudited.

Full two-state sequential equivalence passed:101 proven,0 unproven;102 functional instances including21 FFs;41 used library masters/model definitions. Only the same3026 unconnected tap instances were projected out, with complete structure checks. Proof registration commit is `c5a4d05`; proof/source hashes are in `sec/CONTROL_vs_RESTORE__074__models_v2/receipt.json`. `ACCEPTANCE.json`, `INDEPENDENT_REVIEW.md`, `ROOT_READBACK.json` and `area_baseline_audit/` bind the same endpoint and denominator.

## Fixed-pool budget comparison

| Allowed WNS loss | Physically eligible endpoints | Best physical proposal | Best SEC-qualified endpoint |
|---|---:|---|---|
|0ps|6|COMBO054074098, area−3.68609%, SEC pending|FORWARD096, area−0.59453%|
|5ps|15|RESTORE074, area−4.39952%|RESTORE074|
|10ps|19|RESTORE074, area−4.39952%|RESTORE074|
|20ps|21|RESTORE074, area−4.39952%|RESTORE074|

These are52 measured endpoints on ONE design, not52 independent circuits. Larger budgets do not improve the selected area in this fixed pool beyond5ps. This does not prove5ps sufficient for other candidates/designs. TNS is reported and used as an auxiliary tie-break, not a hidden hard constraint. Hold keeps the original nonregression/nonnegative gate. Old strict failures and the intermediate WNS-primary package are preserved.

## Implemented mechanism and executable interface

`code/src/rseco/budgeted_recovery.py` provides immutable Endpoint/Action/BudgetPolicy, fixed-reference assessment, default SEC-qualified selection with exact reference fallback, and bounded measured combination search. The evaluator receives the full sorted action set from the fixed reference. Conflicting targets on one instance are excluded; duplicate sets are not reevaluated; failed callbacks consume budget. Estimates only order proposals; actual combined measurements decide feasibility. The beam uses measured timing deficits and area to retain parents, including temporarily numerically infeasible parents that may be compensated. A feasible nondominated archive preserves proven points when a better pending-proof point exists. This is a bounded heuristic, not a global optimum guarantee.

The physical/structural `valid` flag and evidence/scope identities are caller certificates, not proof produced by the pure kernel. The caller must impose callback timeouts and validate endpoint provenance. The archive is policy-specific; widening a budget requires the full evaluations/pool, not just the earlier archive.

A real-data adapter checks archived source/output hashes, raw metrics and proof receipts, then invokes the new policy:

```powershell
.venv/Scripts/python.exe project_docs/evidence/timing_budget_20261113/evaluate_budget.py --budget-ps 0 5 10 20 --output scratch/recovery_budget_results.json
```

`CORE_INTEGRATION.json` records agreement with the independent52-endpoint classification and preserves the distinction between pending-proof proposals and deliverable endpoints. This command performs no routing, STA or SEC. It accepts other finite nonnegative budgets in ps; the kernel uses ns. The old `recover_area.py` CLI remains unchanged (default15ps, legacy fixed-SPEF path); do not call it the new online mechanism.

## Validation and remaining research

The implementation's red/green unit tests, full regression, CLI validation and integration receipts are collected with this report. Final verification counts are recorded in `VERIFICATION.json` after the run completes. New physical work this stage:0routes/0STA/1SEC. The earlier constraint audit cost2 diagnostic STA and is recorded separately in `library_area_search_20261113/constraint_audit/`.

The selected endpoint still has negative setup slack. Three inputs lack input delays and six outputs lack output delays/are unconstrained in the existing configuration; supported-rule route DRC and configured DRV checks are not complete signoff. This stage does not establish complete IO safety, multi-corner generality, or online-search superiority. Next implementation gate is a prospective physical evaluator for the expanded candidate space; subsequent scientific gates are equal-budget strong baselines, joint-selection ablation, complete intended constraints and cross-design evidence. Manuscripts are not rewritten as if those gates passed.
