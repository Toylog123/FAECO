# Independent endpoint, denominator and policy-core review

2026-11-13. Accepted within the registered 10 ps policy and the archived s382 constraint scope. This review ran no EDA, STA, routing or new SEC. It inspected the completed proof and regenerated its cell models using pure Python.

## Selected physical endpoint and proof

`RESTORE__074_` retains CONTROL's `_074_` and applies the other 12 registered substitutions. The complete structural audit preserves all ports, assignments and named pin connections, including escaped FF identifiers. The area audit independently aligns the full DEF and Verilog instance/master maps; this is not a common-instance subset comparison.

`ACCEPTANCE.json`, produced by `independent_accept.py`, checks the pinned PLAN and every local source binding, original and projected input hashes, all nine proof artifact hashes, the physical output hashes, proof result, and raw successful assertion. Exactly the same 3,026 zero-pin physical tap instances are excluded from both proof inputs. Every other instance survives unchanged in each projection: 102 functional cells, including 21 FFs, per side. The normalized inputs, proof raw inputs, and actual gold/gate modules have identical complete canonical structures.

All 41 used cell masters are covered exactly by `cells.v`. Rebuilding the models from the hash-bound Liberty using the existing emitter produces the identical model-file SHA. This includes all three escaped-FF master types missed by the old regex scanner. The original netlists and proof files remain unchanged. The raw Yosys result is **101 proven, 0 unproven**, with `equiv_status -assert`, return code 0 and no ERROR/FATAL marker. This is two-state sequential equivalence; it is not a timing or physical proof.

| Quantity | CONTROL | RESTORE__074_ | Change |
|---|---:|---:|---:|
| Full mapped-cell area | 1052.2592 | 1005.9648 | −46.2944 |
| Setup WNS (ns) | −0.8484588032153795 | −0.851556880565596 | −0.0030980773502165 |
| Setup TNS (ns) | −13.422542572 | −13.654524803 | −0.231982231 |
| Hold WNS (ns) | 0.4636368511334865 | 0.46721415625228246 | +0.00357730511879595 |

The 3.098077350 ps WNS loss fits 5 ps and 10 ps budgets, and hold improves. It fails the old 0 ps WNS and strict TNS gates. TNS remains explicitly reported under the new auxiliary objective. The full original 13-action RECOVERY endpoint remains ineligible because its hold regression exceeds the numerical tolerance, even though its WNS loss fits 10 ps.

## Stage-specific area denominator

`area_baseline_audit/RECEIPT.json` and its immutable source copies bind the pre-repair CTS DEF, Resizer final exports, CONTROL and the exact recovered endpoint. `A0 = 892.1056`, `AR = 1052.2592`, and `AF = 1005.9648`. Thus Resizer-stage net added area is **160.1536**, recovered area is **46.2944**, and the recovered fraction is **28.90625%**. Total Resizer area falls **4.399524375743%**. These are distinct denominators.

The preceding synthesis-to-CTS/clock-processing increase of 82.5792 is excluded. Endpoint changes after A0 comprise eight added buffers, eight resized FFs and sixteen other resized logic instances. The immediately-after-repair snapshot is absent: this is the controlled flow's net pre-repair to final-export master difference, not a sum of transient resize events. The same 3,026 unconnected physical taps are excluded from the functional mapped-cell metric, without assigning them zero physical area. The result is specific to this s382 lineage; it does not rehabilitate the old 14-design denominator or old 67% claim.

## New policy/search core

Read-only review covered the entire `code/src/rseco/budgeted_recovery.py`, its complete dedicated test file, the current ROADMAP specification, `evaluate_budget.py`, and `CORE_INTEGRATION.json`. No blocking implementation defect was identified in the reviewed version. Full production regression is owned by the root; this report does not predeclare that result.

- The reference is immutable and fixed throughout assessment, beam ranking and delivery. Improvements do not reset the reference, and the WNS budget cannot be spent anew per step. Units are ns, with explicit ps conversion and finite/nonnegative budget validation.
- Area is primary; TNS is an area-tie criterion, not a veto. Hold has both nonnegative and fixed-reference nonregression gates. Missing/invalid metrics, scope or certificates cannot seed further expansions.
- Same-instance alternative actions conflict; canonical complete action sets are deduplicated. Every attempted callback consumes one evaluation, including exceptions, with no retry. Joint acceptance uses returned endpoint measurements, never the sum of singleton deltas. Numerically infeasible but certified measurements may seed later compensation.
- Default selection requires SEC and returns the exact reference when no eligible proven gain exists. Pending-proof points cannot evict proven points from the Pareto archive. Explicit `require_sec=False` yields a proposal, not a deliverable.
- `valid`, `scope_id` and `evidence_id` are caller assertions. A real evaluator must verify complete target structure, physical artifacts and source hashes, applicable electrical checks and exact measured netlist/SPEF identity before certifying them; the core does not supply that machinery. `sec_pass` likewise needs exact-input proof binding.
- The evaluation bound limits callback attempts, not wall time; the caller needs bounded subprocesses. The Pareto archive contains only points feasible for the current budget. Re-selection after loosening a budget must use all retained valid evaluations, not only that archive. The heuristic supplies neither exhaustive coverage nor global optimality.

The historical adapter revalidates the source audit and 52 physical endpoints, then applies the core without online search. It distinguishes the best physical proposal from the best SEC-qualified point: at 0 ps these are pending `COMBO_054_074_098` and proven `FORWARD__096_`, respectively; at 5/10/20 ps both choices are the now-proven `RESTORE__074_`. Eligible counts are 6/15/19/21. Matching this fixed historical pool validates the interface and policy implementation, not beam-search performance or a new scientific optimization advantage.

## Remaining scientific boundaries

The budget was chosen after the prior measurements; the historical strict failures remain unchanged. This work adds one selected-endpoint SEC, zero routing and zero STA runs to the budget-analysis package. The new core has not yet driven prospective physical evaluations. Existing IO-delay/load/transition coverage is incomplete, only the archived TT constrained-path checks apply, and absolute setup violations remain. Strong equal-budget baselines, ablations, broader candidate coverage and cross-design validation are still needed for the proposed independent mechanism and ICCAD claims.
