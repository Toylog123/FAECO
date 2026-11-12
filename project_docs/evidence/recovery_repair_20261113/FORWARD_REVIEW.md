# Independent Stage C review — 2026-11-13

All thirteen isolated forward cases completed and were independently checked. Exactly one positive-area endpoint meets the strict numeric and configured physical gates: **FORWARD__096_**. It is the unique candidate and therefore also the preregistered maximum-area eligible selection. Full SEC is still required before endpoint acceptance; this review launched no EDA or unit tests.

The review did not call the author's `audit_arm` function. It independently parsed every final Verilog, required the full structure to equal CONTROL plus exactly the intended single archived cell reversion, recomputed full mapped-cell area including escaped FFs, checked all recorded output/input hashes, read the flow and both STA raw logs, verified arm-specific new Verilog/SPEF paths, and recomputed primary qualification from the propagated-clock readings. Empty DRC reports and configured slew/cap reports were checked separately from known negative setup-path labels.

## Selected numeric candidate

| Metric | CONTROL-relative result |
|---|---:|
| Action | `_096_`: `sky130_fd_sc_hd__nor4_2` to `sky130_fd_sc_hd__nor4_1` |
| Full mapped-cell area | 1046.0032 |
| Area saved | 6.256, or 0.594530321046% of CONTROL 1052.2592 |
| Propagated setup WNS delta | +0.001714739461534 ns |
| Propagated setup TNS delta | +0.004840851 ns |
| Propagated hold WNS delta | 0 ns |
| Primary numeric gate | PASS, with 1e-6 ns comparison tolerance |
| SEC | Pending at review time |

Twelve other actions do not qualify. `_074_`, `_077_`, `_081_` are all zero-area diagnostics, not positive-area recovery results. No favorable-result early stopping or accumulation occurred; all thirteen were run in sorted action order. The frozen final selection rule (largest eligible area saving, lexical tie break) selects `_096_` correctly.

Stage C used thirteen routing jobs and twenty-six endpoint STA jobs, with summed per-job elapsed time 373.592 s on the shared host. This is separately accounted from Stages A/B and baseline diagnostics. The source driver differs from the frozen original only in its plan filename; the plan is exactly the twelve-action complement for each of the thirteen isolated moves. All source hashes and independent full-coverage checks pass.

## Interpretation

This is a feasible **conservative single-action baseline candidate**, not evidence of a new joint-selection mechanism or ICCAD-level novelty. After SEC, it can refute a claim that every positive-area recovery action must degrade the tracked timing metrics under this implementation. It does not establish optimality, broad physical robustness, timing closure, complete constraint coverage, or superiority over strong equal-budget methods. The original negative setup slack remains negative. Supported-flow DRC excludes the previously documented unsupported LEF58 rules, and configured DRV reports do not constitute complete signoff.

Frozen reviewed `FORWARD_RECEIPT.json` SHA256: `b39a2424ef82b75923bc70570ff7ececf63ade6567c870f1a6bd7dbf1aaf5295`. The final `FORWARD_SUMMARY.json` is parsed-equal to that receipt. Later SEC or changed source artifacts require their own explicit identity.

Subsequent independent proof review accepted this local baseline. See `FORWARD_ACCEPTANCE.json`, SHA256 `e7d217e8976f79c06724111b5850d64daa0d88b0b913454b76dadfc50ca9b9dd`: complete model coverage, exact declared tap projection, unchanged original sources and 101 proven / 0 unproven equivalence cells. This explicitly supersedes the pending-SEC status above without changing the numeric endpoint or its scope.
