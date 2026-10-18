# OI048 mapped BLIF scope repair — independent implementation record

Status: owned production and tests frozen; parent integration/full regression pending. No Git operation, scientific EDA campaign, or paper/figure edit was performed.

## Confirmed defect and narrow repair

The independent native counterexample in `r22_cec_top_scope_audit_20261018/fix_independent_review_v2/` showed a mapped BLIF with an unrelated `dummy` identity model followed by the intended `ztop` inverter could falsely pass: ABC chose the first of two roots. Source Verilog had already been normalized correctly. A single-model inverter failed, proving the multi-root result was a wrong-object proof.

`verilog_modules.select_blif_top_module` now selects the unique root by `.subckt`/`.gate` references, or validates an explicitly named model. Default selection rejects independent roots in either order and disconnected models; reachable helper models remain supported. Explicit selection is caller-supplied proof scope, not inferred equivalence to another model.

Both `check_mapped_blif_equivalence` and the ABC baseline backcheck now use the existing shared normalizer on the mapped/generated BLIF before CEC. Shared Yosys normalization runs `hierarchy -check -top` and flattening. Original raw BLIF is retained, and a distinct normalized BLIF plus numbered input/output/log SHA receipt records the actual proof object. The baseline still returns its raw generated netlist as its output.

The common CEC status gate gives nonzero exit codes, multiple-root diagnostics, explicit `Error:` lines, and `Cannot open input file` diagnostics precedence over success text. The actual native ABC returns rc0 for a missing-input error. Benign `Cannot open file "abc.rc"` lookup warnings alone remain accepted when CEC reports equivalent. Contradictory non-equivalence/equivalence text returns fail.

## Additional confirmed source-selection window

Parent proposed a concrete timing gap: top selection/extraction occurred before the normalizer bound its actual input snapshots. A selector hook changes the original file after selecting `oldtop`, adding a new `ztop` root that instantiates and inverts `oldtop`. Before repair, the helper returned rc0 with no source drift detected. Ordinary and BOM-prefixed original sources both reproduced this (controlled process boundary, not a native proof claim), with two actual red tests in `RED_SOURCE_WINDOW.log`.

The normalizer now snapshots `original_source` before preparation/top inference, checks all bound inputs immediately before launch, and retains the after-check. This binds the original caller object even when BOM sanitization creates a separate file. Drift returns nonzero and preserves its receipt; the two new regressions are green. No additional normalization implementation or ABC invocation path was introduced.

## Verification and retained history

- Initial behavioral red: `RED.log`, 14 failed / 2 passed. Missing selector API tests are distinguished from existing false-pass behavior; the earlier native counterexample is the independent proof of the real defect.
- Explicit diagnostic red: `RED_STATUS_V2_RETRY.log`, 2 failed / 6 passed / 11 deselected. `RED_STATUS_V2.log` is an environment failure (WSL bash could not find python, rc127), preserved and excluded from red code evidence.
- Source-selection-window red: 2 failed / 19 deselected, 0.42s.
- Final bounded adjacent suite: `GREEN_V3.log`, **47 passed / 1 skipped in 4.64s**, 300s wrapper, exit0. Earlier `GREEN_V1` and `GREEN_V2` remain separate history.
- Native small controls: `native_post/RESULT.json` and `NATIVE_POST.log`, 120s wrapper, exit0. Identity pass; inverter fail; two independent-root orderings error; explicit ztop inverter fail; missing explicit top error; helper-first unique hierarchy pass; actual baseline success. The real zero-return-code missing-input diagnostic is retained verbatim in logs; appending success text remains rejected by the status parser.
- Frozen source SHA before/after native controls is identical. The original `test_yosys_abc_flow.py` hash is unchanged by this agent. `FINAL_RECEIPT.json` contains frozen source hashes and 176 artifact hashes; `native_probe.py` archives the exact scratch probe.

This closes the reproduced implementation defects subject to parent independent replay and full regression. It does not validate historical proofs generally or upgrade two-state/static checks to four-state/physical capability. Scientific S/SPEF experiments still require the newly pinned source and registered actual-tool execution.
