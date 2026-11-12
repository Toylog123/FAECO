# Stage D: three independent joint-compensation probes

Prepared 2026-11-13 before any Stage D EDA execution. Stage C is still pending at registration; no Stage C outcome or contribution is presumed. Execution requires all13 Stage C cases finished with valid evidence, including unfavorable and zero-area outcomes. Root review and commit precede explicit execution.

## Fixed candidates and adapter semantics

The fixed logical base is the actual Stage B endpoint COMBO_054_074_093_098_111 (restored original instances _054_, _074_, _093_, _098_, _111_). It was the closest actual TNS endpoint among the completed12 combinations; its saved area is26.2752, but TNS and hold failed strict non-degradation. Its result is a diagnostic base, not an accepted endpoint.

Evaluate exactly three independent arms, each starting from that same target logical base:

1. JOINT_057: _057_ sky130_fd_sc_hd__o31a_1 -> sky130_fd_sc_hd__o31a_2.
2. JOINT_083: _083_ sky130_fd_sc_hd__o21a_1 -> sky130_fd_sc_hd__o21a_2.
3. JOINT_REBUFFER1: rebuffer1 sky130_fd_sc_hd__buf_6 -> sky130_fd_sc_hd__buf_8.

No accumulated upsizes, favorable-case stopping, extra candidates or adaptive changes. These are the three previously reviewed path/load candidates, outside the original13 recovery actions. Cell function and input-port identity are checked against pinned Liberty; no timing benefit is assumed. Area increments are1.2512,1.2512,3.7536 respectively; net saved areas before any unexpected structural change are25.0240,25.0240,22.5216.

JOINT_RECIPE contains the unchanged13 original actions plus3 explicit target edits. For the added edits only, new_cell means the CONTROL source cell and old_cell means the intended upsize target, solely to adapt the existing physical driver. They are not historical reversions. Every arm's restored set is the fixed5 original restorations plus the other2 unused extras. The executed endpoint therefore contains8 original downsize/recovery actions plus1 new upsize. The runner validates the entire schema, functions, original13 identity, restored sets and final whole-netlist connectivity/cell targets. The physical driver differs from the frozen original only in the plan filename and recipe path.

## Physical protocol and gates

Each arm begins from the same copied accepted reentry ODB and original SPEF as Stages A-C, applies its complete target edit set, legalizes, clears regular SIGNAL/CLOCK wires, reroutes15 iterations and extracts new SPEF. It does not reuse a routed base ODB or old parasitics for final measurement. Fixed tools, libraries, RCX, constraints, propagated-clock primary measurements, 900s route / 300s each STA / 1530s driver timeout; one physical process at a time. Maximum3 new physical evaluations, recorded separately. A failed/timeout or invalid run consumes a slot and halts for attribution; no automatic retry. Valid unfavorable runs do not stop the remaining arms.

Strict primary gates: positive full mapped-cell area saving relative to CONTROL; propagated WNS, TNS and hold slack each >= CONTROL minus1e-6ns; absolute hold>=0; supported-rule DRC0; no violations in configured slew/cap reports; exact complete functional structure and pin bindings. All cells including escaped FFs count in area; only enumerated zero-pin taps may be projected. No broadened timing budget, complete-constraint/signoff claim, or conversion of unknown measurements to pass.

After all3 valid cases, select greatest-area-saving strict feasible candidate, tie by lexical arm name, for full two-state sequential equivalence against CONTROL with complete used-cell models. A numeric pass remains pending SEC and independent evidence review. Report every case and compare the best evaluated saved area with Stage C's strongest strict feasible isolated-forward baseline at its recorded cost. Stage D uses three extra runs after prior evidence; this is not equal-budget superiority evidence. Positive results would establish only a local compensation endpoint; independent mechanism, transferability and ICCAD contribution remain unproven.

## Preservation

New JOINT_* documents/scripts/receipts only; no changes to prior plans, drivers, results or summaries. Bind all required source/input hashes before execution and refuse existing output directories/logs/receipts. Default runner action is read-only preflight, reporting pending Stage C without running EDA; --execute requires all prerequisites and is the only launch path.
