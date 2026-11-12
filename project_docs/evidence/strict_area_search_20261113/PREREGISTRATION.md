# Fixed-seed strict area search: design and implementation plan

2026-11-13. Continuation authorized by the user. This is a bounded test of candidate interactions and verification ordering, not a claim of a novel optimizer. Preserve the sealed recovery_repair_20261113 package and frozen paper. Reuse the current checkout and existing physical pipeline; no new dependencies or production state machine.

## Hypotheses and refutation

The accepted FORWARD__096_ endpoint saves 6.256 area units with propagated WNS/TNS improved and hold unchanged versus CONTROL. Test whether adding one more positive-area action gives a larger strictly feasible saving. If all nine pairs fail, the one-step expansion hypothesis fails for this neighborhood; retain the accepted seed. Separately test whether singleton-informed risk ordering finds useful feasible points with fewer new physical evaluations than area ordering. The primary comparison is k=3; k=1,6,9 and the complete prefix trace are secondary. A tie or worse result at k=3 does not support a scheduling advantage. At k=9 both strategies MUST give the same best endpoint.

## Frozen search space and measurements

Use original13 recipe actions from the sealed study. Include the nine positive-area actions other than _096_: _052_, _054_, _055_, _079_, _093_, _098_, _102_, _111_, _113_. Each candidate applies exactly _096_ plus one listed action to the same copied CONTROL reentry ODB. The restored set contains the other11 original actions. Three zero-area actions _074_/_077_/_081_ remain at CONTROL. Never build from the already routed seed ODB, accumulate accepted actions, or change the seed during this study.

Measure all nine in lexical action order, independent of strategy ordering. Same legalization, regular signal/clock wire clearing, full reroute15 iterations, fresh extracted SPEF, ideal and propagated independent STA. At most9 new routes/18 STA. One routing process at a time, route900s/STA300s/child1530s; explicit batch timeout. Preserve failure; invalid/timeout consumes budget and stops for attribution, no automatic replacement. No early favorable stopping. Historical labels and seed proof are reused, not rerun and not counted as new evaluations.

## Frozen ordering and acceptance

Both strategies receive exactly the same prior CONTROL, seed and13 singleton observations. For extra action j, predicted pair metrics are M_seed + M_j - M_CONTROL, all in ns. Norms for setup/TNS/hold are respectively0.010/0.312647/0.001ns, inherited from the previous registered study rather than tuned to pair results. Deficit=max(0,CONTROL_metric-prediction-1e-6)/norm.

- area_first: descending exact total saved area, then lexical candidate ID.
- timing_risk: ascending(max deficit,sum deficits), descending exact total saved area, then lexical candidate ID.

Freeze the candidate lists, exact area, predictions, scores and both full orderings in PLAN.json before measuring any pair. Prediction is proposal metadata only. Acceptance uses fresh actual audited physical output, positive saving relative to CONTROL, propagated setup/TNS/hold each >= CONTROL minus1e-6ns, hold>=0, complete intended structure, supported-rule DRC0 and configured slew/cap reports without violations. Missing/nonfinite values or incomplete evidence cannot pass. The reference stays CONTROL, allowing already acquired slack margin to be spent; do not silently switch it to the seed. These are relative gates under the current constraints, not absolute closure/signoff.

Replay both orders over the shared measured pool. Each prefix includes the accepted seed as fallback; retain the greatest actual saving among strictly feasible measured points, with lexical ID tie-break. Return the exact measured endpoint files/hashes, never reroute an accepted logical target. Each distinct prefix candidate costs one charged verification regardless of shared offline data reuse; actual physical calls total9, not18. Assert every prefix's best saving is nondecreasing, k=9 endpoint identical, and all-failure fallback exactly equals seed. Select the overall best improved point for full two-state SEC after all9 finish; report other numerical candidates as pending SEC. No positive improvement means no new proof required, reuse the sealed seed acceptance.

Fairness is only conditional on shared history: prior isolated observations cost13 routes/26 STA and seed discovery/proof was part of a broader41-route study. Report these costs separately; prefix comparison is not an end-to-end equal-cost claim, not adaptive greedy comparison, and not a statistical test from nine independent circuits.

## Implementation tasks and ownership

Use the writing-plans/executing-plans and TDD workflow for the new evidence-level selection functions. Existing physical driver/reader/auditor are copied and adapted minimally; no third SearchState or production acceptance changes.

- [ ] Copy required inputs and prior labels/acceptance into this evidence package, hash-bind provenance and local files. Historical baseline STA logs may be reused with explicit local-copy mapping; runtime verification must not depend on another experiment directory. Original historical Tcl paths remain provenance, never executed as new measurements.
- [ ] Implement pure selection helpers in `selection.py`; test missing/NaN actual metrics, area-only/WNS-only false positives, predicted-vs-measured separation, immutable seed fallback, exact tie handling, k9 equality and no decreasing prefix optimum. Tests live in this package and run under pytest; record red then green. No EDA in tests.
- [ ] Copy `physical_probe.py` with only local plan/recipe paths adapted as needed; copy complete `structure_reader.py` and `analyze_repair.py`, document any copied-baseline lookup adaptation. No relaxation of `audit_arm`.
- [ ] Implement `run_search.py` with read-only default preflight and explicit --execute, source/input SHA checks, no overwrite, serial bounded nine-arm measurement, complete raw receipts and frozen-policy replay.
- [ ] Independent review plus root preflight, then commit protocol/code BEFORE route execution. Record all9 results and actual costs; run selected-point SEC only after numeric acceptance.
- [ ] Independent raw audit, report/replay check, preservation of prior seal, docs update, new manifest, commit+push. No promotion to production mechanism or paper without further evidence.

Review focus: changing reference/seed accidentally; counting shared measurements twice; using predicted feasibility as actual acceptance; old netlist/SPEF mismatch; ignoring TNS or hold; modifying frozen prior results; selecting a new route instead of the exact accepted physical endpoint.
