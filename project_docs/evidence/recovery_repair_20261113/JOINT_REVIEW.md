# Independent Stage D review — 2026-11-13

**All three runs are valid engineering measurements, but none passes the strict primary gate.** No Stage D endpoint is eligible for acceptance SEC. This does not invalidate the separately accepted conservative FORWARD__096_ baseline.

Pre-run review verified the exact original13-plus-extra3 recipe, all source hashes and the driver's only two changes (plan filename and recipe path). For extras only, `new_cell` is the CONTROL source and `old_cell` is the upsize target; this adapter was checked against actual CONTROL cell identities and does not reverse the intended move. Relative to the actual fixed Stage B logical base, each target has exactly one additional change: `_057_` o31a_1 to o31a_2; `_083_` o21a_1 to o21a_2; or `rebuffer1` buf_6 to buf_8. Pinned Liberty input pins/output functions agree, and the pairs are combinational and non-tristate. No timing advantage was assumed.

Post-run review independently reconstructed each complete target from CONTROL and compared all final cell instances, pin bindings, port/wire declarations and assignments. It independently recomputed full mapped-cell area with escaped FF coverage, checked every recorded input/output SHA, and parsed all flow/STA raw reports without using the author's `audit_arm` function. All three actual targets match the plan, with 3128 total instances / 102 functional instances / 335 pin connections. Only the verified empty-pin physical taps are excluded from area.

The final STA scripts read each arm's own new routed Verilog and SPEF. All nine processes have zero return codes and completed sentinels, with no error/Tcl-failure diagnostics. DRC reports are empty; configured slew/cap report segments contain no violations. Known negative setup-path labels are not mistaken for DRV failures. Original supported-flow DRC and incomplete-constraint-coverage limitations remain.

| Arm | Mapped area | Saving vs CONTROL | Delta setup WNS (ns) | Delta TNS (ns) | Delta hold WNS (ns) | Strict gate |
|---|---:|---:|---:|---:|---:|---|
| JOINT_057 | 1027.2352 | 2.378121284% | -0.003183397990 | -0.120345116 | -0.000147548640 | FAIL |
| JOINT_083 | 1027.2352 | 2.378121284% | +0.000984212711 | -0.042348862 | -0.000193844940 | FAIL |
| JOINT_REBUFFER1 | 1029.7376 | 2.140309156% | -0.010551726159 | -0.227338791 | -0.000147548640 | FAIL |

All deltas use propagated-clock final measurements relative to CONTROL. JOINT_083 reduces the fixed base's TNS deficit, but its remaining TNS and hold degradations exceed the unchanged 1e-6 ns comparison tolerance. Reporting its larger area saving as superiority over the accepted forward baseline would therefore be incorrect. The final `selected_pending_SEC = null` and empty candidate list are correct.

All three registered cases ran once, in order, without favorable-case stopping or replacement. Stage D used 3 routing jobs and 6 endpoint STA jobs. Observed per-job time sums to 87.063 s (physical flow 83.860 s; endpoint STA 2.501 s); outer wrapper completed in 92 s with return code zero. These are shared-host measurements. Across Stages A/B/C/D there are 41 new physical candidate runs and 82 endpoint STA measurements, excluding baseline diagnostics, prior qualification and formal proofs.

## Interpretation and accepted baseline

The joint probes provide evidence of local timing/area interactions and of an unsuccessful strict repair within this three-candidate set. They do not establish that joint compensation cannot work elsewhere, nor that the current search is a novel or competitive ICCAD mechanism. No equal-budget strongest-method comparison or multi-design generalization has been shown.

FORWARD__096_ separately passed independent full-netlist projection/model/SEC review: 101 equivalence cells proven, zero unproven; the original physical sources still match their hashes. Its strict physical/metric review and proof are bound in `FORWARD_ACCEPTANCE.json` (SHA256 `e7d217e8976f79c06724111b5850d64daa0d88b0b913454b76dadfc50ca9b9dd`). This accepts a local conservative baseline with 0.594530321046% mapped-cell area reduction; it does not convert any Stage D failure into a success or confer novelty.

Reviewed `JOINT_RECEIPT.json` and `JOINT_SUMMARY.json` are byte-identical, SHA256 `0ff6393a929c2d51dcf8f6315a10cfd6686c9ff9170978719170071eaad2ac50`. Old forward SEC validation used its unchanged `run_repair_sec.py` SHA256 `056e9394c2926450ea2cd2bd7676e401ba911e9a413b60de3d0735f7d05aae07`; it was not checked against the later separate joint SEC helper.
