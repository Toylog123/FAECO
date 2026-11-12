# Independent Stage B review — 2026-11-13

**Disposition: accept execution and bounded-search evidence; no strict feasible candidate was found.** All twelve combination evaluations completed with valid physical/measurement evidence. None satisfies the user's simultaneous zero-added-loss WNS, TNS and hold conditions within 1e-6 ns. No candidate is approved for promotion or requires an acceptance SEC. The absence of success is not a proof that all possible recovery configurations fail.

## Independent checks

The reviewer did not call the author's `rank` or `audit_arm` functions for this review. Using the frozen singleton summary, full structural Reader and Liberty areas, the reviewer independently reconstructed the initial beam, all one-action extension sets, additive proposal estimates, exact candidate areas, deficit ranking and measured next-layer beams. No EDA or unit tests were launched.

- Initial beam is `_098_`, `_074_`, `_111_` in that order.
- Four cardinalities 2/3/4/5 each selected exactly three unique new subsets; all choices matched the preregistered deterministic rule. No unregistered action, duplicate evaluation, timeout replacement or extra physical job was observed.
- The rank uses fixed setup/TNS/hold scales 0.010 / 0.312647 / 0.001 ns, tolerance 1e-6 ns, then maximum deficit, summed deficit, retained area and sorted instance names. These constants are a search heuristic, not calibrated uncertainty bounds.
- Original singleton `SUMMARY.json`, analyzer, plan and batch hashes remain unchanged. Combination runner/driver/plan hashes match the receipt; the plan's preregistration hash matches the frozen rule.
- For each of all twelve outputs, full instance names/types, all pin connections, port declarations, wires and assignments exactly match CONTROL with the intended archived recipe minus the restored subset. Every functional instance has a known Liberty area; only the 3026 explicitly unconnected tap instances are excluded. Escaped FF names are included.
- Every flow and both endpoint STA processes returned zero and emitted completion markers without error/Tcl-failure diagnostics. Empty DRC reports and configured max-slew/cap report segments have no violations. Negative setup-path `VIOLATED` labels were correctly kept separate from DRV checks.
- Each endpoint Tcl references its own new routed Verilog and SPEF. Independently parsed raw setup/hold/9-digit TNS values match the recorded metrics. All recorded output hashes and driver input hashes match actual files.
- The final combination summary equals the concatenated actual layer results, records twelve attempts, and reports no feasible point at any of the four diagnostic WNS budgets. The strict primary condition was not relaxed.

`TOOLCHAIN_RECHECK.json` records that the installed OpenROAD, standalone STA, TT Liberty and both LEFs match the prior five pinned hashes; local setRC/RCX identities are additionally recorded. This review does not add a new EDA tool invocation.

## Results and costs

All twelve combinations have worse TNS than CONTROL, so even the diagnostic 2/5/10 ps WNS budgets yield no feasible solution under the retained TNS/hold gates. Some combinations improve WNS, confirming that WNS alone would have produced a misleading acceptance.

| Restored instances | Mapped area saved | Delta WNS (ns) | Delta TNS (ns) | Delta hold (ns) | Primary result |
|---|---:|---:|---:|---:|---|
| 054, 074, 098 | 3.686087990% | +0.001660727111 | -0.125137329 | +0.001717348486 | TNS fails |
| 054, 074, 098, 111 | 2.972651605% | +0.002110256414 | -0.088749886 | -0.000147604151 | TNS and hold fail |
| 054, 074, 093, 098, 111 | 2.497027348% | +0.001715960707 | -0.077928543 | -0.000147548640 | TNS and hold fail |

The last row has the smallest TNS deficit among the twelve tested combinations; it is not a safe endpoint. All deltas are propagated-clock candidate minus CONTROL using the same final measurement convention.

Stage B used 12 routing jobs and 24 endpoint STA jobs. Sum of per-job elapsed times is 344.641 s, including 331.717 s recorded physical flow time and 10.004 s recorded endpoint STA time. These are observed shared-host costs, not an exclusive performance benchmark or total end-to-end study time. Together with Stage A, the bounded search evaluated 25 new physical candidates and 50 endpoint STA runs; baseline diagnostics and prior qualification runs are separate.

## What this supports

The bounded compensation search can reduce or reverse the original WNS loss while retaining some mapped-cell area saving, but under this single s382 implementation every tested compensation still fails the complete no-degradation requirement. That is the strongest supported outcome. Do not label the task solved, native recovery surpassed, or an ICCAD-level independent mechanism demonstrated. No equal-budget strongest-sequential or other competitive search ablation has established the contribution of this particular ranking rule; one circuit and one physical realization cannot establish generality. Do not treat the twelve sampled combinations as exhaustive coverage of the 13-action subset space.

Further work requires a separately scoped, predeclared decision; no automatic extension beyond the twelve-job budget is authorized by this receipt. Supported-flow DRC and configured DRV coverage remain narrower than foundry signoff or complete constraint coverage.

## Frozen reviewed identities

- `COMBINATION_RECEIPT.json`: `7937cb561e12c9b6a49d75da745359dc3c1beb811925885edaa09eb377457495`
- `COMBINATION_SUMMARY.json`: `b9371a560633f8efc4db7631f42869716793facc991ac9f9b3f278c3451d5204`
- Stage A `SUMMARY.json`: `5ae335bc5e981842a41a912bbf1b4ccf213738106dba02d94b1a52495079c8a9`

Later evidence or SEC receipts must be separately identified; this review does not silently apply to modified outputs.
