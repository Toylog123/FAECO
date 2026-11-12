# Stage C: isolated forward moves from CONTROL

2026-11-13, registered after Stage B exhausted its 12-run budget without a strict candidate, before any Stage C physical evaluation.

Question: does one of the original 13 recovery actions alone reduce area while preserving propagated setup WNS, setup TNS and hold WNS relative to CONTROL? This tests the alternative that simple conservative selection suffices. Success is a baseline for a future mechanism, not evidence of novel selection or superiority.

Evaluate all 13 isolated actions in sorted instance-name order. For each arm, restore the other 12 actions to CONTROL's cells. Do not accumulate accepted actions, stop on a favorable result, or change the candidate set. The three zero-area actions `_074_`, `_077_`, and `_081_` remain as diagnostics and cannot qualify as positive area improvement. Reuse the frozen physical driver with only the plan filename changed and the frozen full-structure auditor without changes. One physical flow at a time; route 900 s, each STA 300 s, subprocess 1530 s. Maximum 13 additional physical evaluations, separately accounted from Stages A/B. Tool failure or invalid evidence stops for attribution; no automatic retries.

Use the same copied ODB, 13-action recipe, legalization, clearing regular SIGNAL/CLOCK wires, full reroute (15 iterations), RC extraction, final netlist/SPEF pair, Liberty and clock constraints. All inputs and scripts are hash-bound. Cost is observed under a shared host, not an exclusive runtime benchmark.

Primary gates remain positive full functional-cell area reduction, each propagated WNS/TNS/hold delta >= -1e-6 ns, absolute hold >= 0, supported-rule DRC zero and no violations in configured slew/cap reports. This numerical tolerance is not a timing loss budget. Original negative setup slack remains; this is relative non-degradation, not timing closure or complete signoff. Unknown and invalid evidence never count as a pass. Area includes escaped FFs; exclude only enumerated unconnected physical taps.

After all 13 cases, select the greatest-area-saving eligible endpoint (tie: lexical arm name) for complete two-state sequential equivalence against CONTROL. Preserve and report every result, including timing failures and zero-saving diagnostics. Selection only becomes an accepted pilot endpoint after full proof and independent evidence review. Multiple circuits, complete constraints/corners and equal-budget strong baselines are still required for an ICCAD claim.
