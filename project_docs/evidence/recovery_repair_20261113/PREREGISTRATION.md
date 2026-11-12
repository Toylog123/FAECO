# s382 minimal compensation: bounded physical study

2026-11-13. User approved reducing timing degradation while preserving area savings. This is a local repair study, not an ICCAD novelty claim. Preserve all previous artifacts; no production parser changes or silent expansion of the 13-action set.

## Inputs and objective

Copy the accepted s382 reentry OpenDB/manifest, original SPEF, archived 13-action recipe, full structural checker, and prior CONTROL/RECOVERY endpoints into `inputs/`. Source qualification package: `recovery_qualification_20261112`; copy required assets, do not mutate it. Tool/Liberty/LEF/RCX hashes fixed to the prior flow. Same period0.5ns, propagated-clock final gate, full reroute15iterations with all regular wires cleared in a copied database, identical legalization/extraction. One routing process at a time; route timeout900s, STA300s. Cost recorded, not an exclusive-host benchmark.

Maximize retained absolute mapped-cell area reduction relative to CONTROL, subject to setup WNS loss budgets **0, 0.002, 0.005, 0.010ns** (+1e-6ns numerical tolerance), **TNS non-worsening** (1e-6ns tolerance), **hold slack >=0**, supported-rule route DRC0 and no reported slew/cap violations. The hold gate is new absolute feasibility, not the prior strict hold-nonworsening test; also report the old hold delta separately. All designs still have setup violations; this is no added degradation, not timing closure. Complete SDC/DRV coverage remains outside established evidence and must remain explicit.

Re-measure CONTROL and original RECOVERY standalone STA with 9-digit TNS, setup/hold detailed path reports before dependent decisions; same final netlist/SPEF, no new routing. Diagnostic path membership is explanatory, not a candidate filter. Final candidate area uses full named-instance parser and independent Liberty areas, including escaped FF; only explicitly unconnected physical taps excluded.

## Stage A: all13 single compensation cases

**User steering before physical runs**: user explicitly requires no timing degradation and an independent mechanism judged against ICCAD standards. Primary acceptance is now WNS/TNS/**hold non-worsening relative to CONTROL** (1e-6ns numerical tolerance), not merely hold>=0. Absolute hold feasibility also required. The 2/5/10ps budgets are diagnostic only, never scientific promotion; zero-budget primary takes precedence over earlier absolute-hold text. No timing relaxation may be used to hide failure. Independent mechanism means a documented selection/compensation algorithm with same-budget strong baselines, not renaming OpenROAD or claiming a single-case search as novelty.

For every archived reverted instance, retain the other12 reversions and restore exactly that instance to Resizer's cell. Evaluate all13, no early stopping or removal of unfavorable cases. Verify exported netlist has exactly the intended swaps and unchanged pinbindings/assigns. Save per-case input/driver/config/output SHA, Tcl, complete logs, metrics and runtime. Unknown/missing/failed measurement is failure to qualify, not zero loss.

## Stage B: optional bounded combinations

Only if no singleton satisfies the zero-budget gates with positive area saving, expand combinations using an explicitly recorded rule fixed before observing combination outcomes. Max12 new physical runs; rank search toward zero WNS budget only, then report all4 budgets from the same evaluated set. Predicted metrics cannot authorize acceptance. The all-restored CONTROL is an available zero-saving fallback, never counted as a useful recovery solution.

## Acceptance and review

For each budget report maximum-area feasible evaluated solution, all failures, WNS/TNS/hold deltas, actual candidate/route/STA counts, and the fraction of original saving retained. Before claiming a new valid endpoint: full intended-edit/connection check and existing full-netlist sequential proof with complete Liberty-used-cell enumeration (101proven/0unproven expected for current s382), raw log/error review, and hash sealing. Models exclude only fully enumerated zero-pin taps. Findings remain s382-local and single implementation. A successful point does not establish uniqueness, transferability or superiority over equal-budget strong greedy/native methods.
