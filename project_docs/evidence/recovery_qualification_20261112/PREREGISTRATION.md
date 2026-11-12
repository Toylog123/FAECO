# Recovery qualification: instrumentation and physical re-entry pilot

Date: 2026-11-12. Status: preregistered engineering feasibility pilot, not scientific promotion.

User authorizes continued evaluation for ICCAD; no manuscript edits. Parent source HEAD: 51cebf5aa6a8946e81b7e2d6018ba8879660c749. Current CLI corrections must be pinned by file SHA separately; old summaries remain historical.

## Phase 0: same-state reconstruction

- Circuit s382, original Resizer artifacts: `experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/`.
- Recovery recipe: `experiments/20261112_resizer_recovery/arms/RECOVERED_V2/s382/summary.json` and `recovered.v`.
- Library/platform: sky130hd TT 025C 1v80, existing platform + project ORFS RCX snapshot. Tool `/home/toylog/faeco_eda/or26Q3/bin/openroad`; standalone `/usr/local/bin/sta`.
- First reconstruct routed DEF with the exact LEFs/Liberty. Export netlist; check named functional cells and connections against archived Verilog. Independent original-SPEF STA must reproduce original ideal-clock setup and hold slack within 1e-6 ns. Any failure blocks interpretation of downstream recovery differences.
- Save propagated-clock metrics separately; do not compare them with historical ideal-clock metrics.
- Per subprocess timeout 300 s for STA/re-entry; 900 s for routing. Sequential routing only. Emit logs/progress. No cache reuse without matching all input hashes.

## Phase 1: conditional physical feasibility (only after phase 0)

- Arms CONTROL (zero edits), RECOVERY_V2 (exact archived recipe), NATIVE (installed `repair_timing -recover_power 100`, binding help and tool version first).
- All start from same reconstructed state. Physical pipeline and final measurement constraints identical. Native incremental parasitic model must be recorded; cannot silently compare different endpoint configurations.
- Apply swaps in OpenDB, legalize, route and extract new parasitics; do not feed flattened routed.v to the old pipeline or synthesize a second clock tree.
- Check actual placement, DRC, setup/TNS/hold and slew/capacitance. Missing checks => unknown. Control itself may violate timing: report non-worsening relative to control separately from absolute timing closure.
- Primary effect: (control standard-cell area - arm standard-cell area)/control area; also report absolute area and historical added-area-recovery ratio separately. No claim of die-area reduction.
- Strict non-worsening gate: slack degradation no more than 1e-6 ns; any area/timing tradeoff reported separately, never folded into a safety pass. Functional equivalence must be checked before scientific promotion.
- One circuit is feasibility evidence only. Physical failure requires attribution and repair first. Strong-native-baseline parity would invalidate an advantage claim under this setup, not all possible research directions.

## Completion records

Record input/tool/driver SHA256, argv, elapsed time, return codes, outputs and actual pass/fail/unknown states. Do not change gate after observing results. Amendments must precede dependent runs.
