> PREPARATION ONLY / SUPERSEDED DRAFT: no 25-candidate EDA was executed. The user subsequently adopted configurable WNS budgets (default10ps), TNS auxiliary, and retained Resizer frontend. This old three-hard-metric draft must be revised and frozen with a new PLAN before execution. Current measured-policy evidence: ../timing_budget_20261113/REPORT.md.

# Complete unmeasured combinational library-target sweep

2026-11-13. Authorized continuation, prepared before any of these physical measurements. This independent evidence package preserves the sealed prior studies and current paper. It tests candidate-space coverage under the existing physical configuration; it does not establish a new optimizer or an independent search mechanism.

## Hypothesis and first refutation

Test whether previously omitted, logically compatible, lower-area library targets can improve the accepted FORWARD__096_ endpoint's area while retaining the fixed CONTROL strict relative timing gate. Report (a) any strict numerical candidate and (b) candidates with more saving than the accepted seed separately. If all 25 fail the strict gate, or the best strict saving is at most 6.256 area units, the specific claim that this expansion improves accepted area is refuted for this fixed neighborhood. Preserve every negative result. A numerical improvement requires complete two-state SEC before acceptance.

## Frozen candidate space

Start from the copied complete CONTROL/Liberty SPACE_AUDIT.json. Select category `combinational_other`, reject `original_recipe_exact_pair`, and exclude the already measured pair `_054_ -> sky130_fd_sc_hd__or3b_2`. This yields exactly 25 instance/target pairs across 11 instances, not 25 independent instances or circuits. The 25 consist of two targets each at `_051_`, `_059_`, and `_063_`, and 19 targets across eight rebuffer instances. Equal-area targets, including o21ai_0 versus o21ai_1, remain distinct; drive suffix is not assumed to order timing quality. No target is removed after seeing this sweep's results.

Each candidate changes exactly one instance from its CONTROL cell to the stated target. No seed action is accumulated. A per-arm recipe contains exactly one entry: `new_cell` is the CONTROL source, `old_cell` is the selected library target, and `restored=[]`. These fields adapt the existing physical/audit interface; `old_cell` does not mean historical rollback. Check complete functional pin/state/PG metadata compatibility against the pinned Liberty, known areas, and the unchanged complete CONTROL structure. Exclude sequential and clkbuf/clkinv families; additionally reject any target instance in the current CONTROL combinational fan-in of a sequential clock pin. Preserve every pin binding and all other instances. Freeze the exact 25 IDs/targets, complete areas, static saved-area scores, measurement order, input/source SHA hashes, and exclusion evidence in PLAN.json before routing.

## Measurement and acceptance

Execute all 25 in lexical `(instance, target_cell)` order, independently from the same copied CONTROL reentry ODB and original SPEF. Reuse the previously validated pipeline: legalization, clear regular signal/clock wires, global plus 15-iteration detailed routing, fresh extracted SPEF, and independent ideal and propagated STA. The only physical-driver adaptation is selecting its RECIPE path from the current arm's frozen PLAN entry inside main. No change to routing, clocks, libraries, parasitics, timing reports, or audit_arm.

Maximum 25 new routes and 50 new STA calls, with one physical job at a time. Route timeout900s, each STA300s, child1530s, batch3000s; the root also invokes the timeout wrapper. Invalid evidence, error, or timeout consumes its verification slot and stops for attribution. No automatic retries, replacements, favorable early stop, or repeated realization of a measured endpoint. Refuse existing output/receipt paths. Freeze this protocol/code by root review and commit before --execute. Default invocation performs read-only preflight, never EDA.

Acceptance uses fresh actual output only. Require complete intended structure and known mapped-cell area, positive area saving against CONTROL, supported-rule DRC0, configured max-slew/cap reports without violations, propagated setup WNS/TNS/hold each >= fixed CONTROL minus1e-6 ns, and absolute hold>=0. Missing/nonfinite fields fail closed. Existing negative setup slack is permitted by this relative comparison; it is not absolute timing closure. Do not substitute predicted timing or ideal-clock timing for actual propagated acceptance. All25 complete before selecting the greatest strict actual saving, lexical candidate ID on ties, with the exact previously accepted seed endpoint as fallback. Only a selected endpoint with more saving than seed gets new full two-state SEC; otherwise reuse the copied seed proof. Retain exact measured netlist/ODB/DEF/SPEF/manifest hashes, never reroute a selected logical target.

## Evidence boundary and costs

The constraint set remains the previous clock-only configuration. This study does not establish complete SDC or PI/PO constraint coverage, full signoff DRC, four-state proof, cross-design generality, or end-to-end equal-budget superiority. Clock-family classification alone is not clock-net analysis; the additional current-netlist clock-fan-in check is a structural scope guard, not constraint signoff. Root's separate constraint_audit diagnostics do not enter the 25-route/50-STA budget and do not change these thresholds.

Prior evidence is reused locally with hashes: the 13 isolated observations/26 STA and accepted seed proof belong to an earlier 41-route discovery study; the subsequent nine pairs and two variants bring those earlier physical studies to 52 routes (41+9+2; the 13 are already within41). These historical costs are separate from this sweep, not additional 13+52 routes. The current sweep is a complete bounded catalog measurement, not an adaptive scheduling comparison. Area scores are static metadata; they do not reorder the lexical physical sequence.

## Implementation and review plan

- Copy required CONTROL/RECOVERY baselines, 13 historical singletons, accepted seed proof, variant exclusion evidence, readers/auditor/selection, and static catalog into this package. All runtime historical lookup uses LOCAL_INPUT_MAP plus COPY_MANIFEST, never reads another experiment directory. Historical Tcl paths remain provenance only.
- Write candidate-configuration tests first: complete25 coverage, exclusion of measured/original/clock/sequential targets, unknown cells, function/pin mismatch, pin-preserving single-target adaptation, duplicate/incomplete catalogs, and immutable CONTROL. Reuse the existing actual-only selection tests.
- Implement candidate configuration and one-time PLAN/recipe freezing; copy the physical driver with only per-arm RECIPE selection. Reuse audit_arm unchanged with each one-entry recipe.
- Implement serial bounded run_library.py, read-only default preflight, no-overwrite receipts, complete actual audit, exact seed fallback, and explicit pending SEC status for a better selected endpoint.
- Run pure tests and local-only preflight. Root independently reviews the source, frozen catalog and protocol, commits, then starts EDA. No production mechanism or manuscript changes are part of preparation.
