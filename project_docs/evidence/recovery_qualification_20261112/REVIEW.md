# Independent pilot review — 2026-11-13

Scope: review of `physical_probe.py`, preregistration, phase0, and all three completed phase1_v2 arms. The first review snapshot covered CONTROL / RECOVERY_V2 while NATIVE was running. Subsequent explicit authorization added two serial bounded SEC checks below. No physical pipeline or unit test was launched by this reviewer; original physical outputs remain unchanged.

## Findings and disposition

1. **The v2 reroute correction is justified as an engineering repair.** The preregistration amendment preserves failed v1, explicitly clears regular signal/clock wires, and applies the same full reroute preparation to all arms. Power/ground wiring is retained. This evaluates full-reroute feasibility, not incremental ECO routing efficiency.
2. **The measured endpoint is the new physical endpoint.** Flow Tcl writes each arm's routed Verilog/DEF/ODB after detailed routing, extracts parasitics, and writes that arm's SPEF. Both final STA scripts reference that same arm's new Verilog and SPEF. The original SPEF is read only at flow entry. CONTROL and RECOVERY endpoint hashes are recorded below. The CONTROL's exactly reproduced historical setup/hold readings do not mean old SPEF was used: its newly written SPEF has a distinct byte hash.
3. **The exact archived recovery recipe was applied.** Complete structural parsing of the two final Verilog exports finds precisely 13 cell-type substitutions equal to the archived `applied` list, with unchanged complete instance keys, pin bindings, ports, declarations and assignments. No extra logical edits were observed. This is structural evidence, not sequential equivalence proof.
4. **RECOVERY_V2 fails the preregistered strict timing non-worsening gate.** Relative to CONTROL, ideal setup slack changes from -0.8413860164147025 to -0.847116377045154 ns (delta -0.0057303606304515 ns). Propagated setup changes from -0.8484588032153795 to -0.858430437844504 ns (delta -0.0099716346291245 ns); propagated hold changes from 0.4636368511334865 to 0.46361825489782404 ns (delta -0.00001859623566246 ns). All three degradations exceed 1e-6 ns. Ideal TNS is -13.255755 versus -13.560900 ns; propagated TNS is -13.422543 versus -13.735190 ns. DRC reports are empty and both manifests report zero violations. Physical execution success and area recovery cannot be called a safety pass. Do not change the gate after observing this result.
5. **Readout validation remains partly manual.** The driver parses STA numbers without requiring successful return code, absence of error diagnostics and `ROUTED_STA_OK`; the marker also precedes the appended DRV reports. Both inspected arms have return code zero, completed marker and numeric reports, so this is an automation weakness rather than an observed invalidation. The raw max-slew/max-capacitance command emits no violating rows in the inspected reports; `drv_status` remains pending until explicitly adjudicated. Actual constrained-port/endpoint coverage and unconstrained-path checks are not established by these outputs.
6. **Final evidence sealing is incomplete in the driver.** It records input and flow Tcl hashes, but not output Verilog/SPEF/ODB, final STA Tcl/log hashes, executable binary or actual WSL Liberty/LEF hashes. The raw artifacts are available and can be sealed without rerunning EDA. Native baseline help/version and toolchain receipts, if stored separately, should be bound into the final receipt. Phase0 structure receipt is not an automatic gate in the driver, although it has separately passed.
7. **Native comparison is deliberately limited.** Native recovery runs with propagated clocks and original extracted parasitics; the historical recovery recipe was selected using ideal clocks and fixed parasitics. Final endpoint measurements are common and separately reported, which permits this feasibility comparison, but it is not evidence of equal optimization constraints or fair compute budgets. Do not infer mechanism superiority from one untuned native invocation, particularly while baseline setup slack remains negative.

## Minimal SEC reuse path

Use `code/scripts/run_r22_cut_ablation.py:108`, API `final_sec(initial_text, final_text, "s382", output_path)`. It generates symmetric Liberty-derived cell models, performs cell-input and two-state-domain checks, and runs pinned WSL `/usr/bin/yosys` with `equiv_simple`, `equiv_induct -seq 10` and `equiv_status -assert`, timeout 180 seconds. A successful result must include both zero return code and the explicit proof-success log message. Do not use the b17-specific wrapper.

Read-only preflight on both current final netlists found the only cell missing from the selected TT Liberty to be `sky130_fd_sc_hd__tapvpwrvgnd_1`; each has 3026 such instances, all with zero named pin connections. The existing API correctly rejects these unknown cells at input validation. All other instantiated cells are in the library; the existing two-state-domain checker returns no unsupported reason. Sequential cells have clock definitions.

Minimal transparent adaptation: save original hashes; parse and enumerate all instances; remove **only** instances whose type is exactly this physical-only tap type and whose connection list is proven empty; assert the same removed instance set on both sides; save normalized netlists, hashes and complete removal list; invoke `final_sec` on the normalized pair. Never generally drop unknown cells, connected taps, clock buffers or unsupported tristate logic. Bind generated cell models and Liberty hash. A pass then proves the normalized logical projection, whose link to the actual physical exports is established by this explicit no-pin removal receipt.

Pair original Resizer final export against each final arm (and/or CONTROL against RECOVERY) to cover actual outputs rather than the archived prephysical recipe. The authorized CONTROL-relative proof execution is recorded below.

## Final endpoint and SEC review

All three arms now have flow and both STA return codes zero. Independent inspection of all nine logs found the required `PHYSICAL_PROBE_OK` / `ROUTED_STA_OK` markers, no `Error:`, `[ERROR`, `invalid command name`, `wrong # args` or `failed to` diagnostics, and no `VIOLATED` rows. All six endpoint scripts explicitly read their own final `routed.v` and `routed.spef`; all request max-slew/max-capacitance reports. The final min-slack and six-digit TNS reports are present after the marker. This completes the observed raw-report review, but does not prove constraint coverage beyond the configured checks. NATIVE's ideal/propagated setup, hold and TNS match CONTROL.

Preserved tool limitations: tap-cell blackbox warnings remain; routing logs warn that LEF58_ENCLOSURE without CUTCLASS is unsupported and skipped for several cut layers. Therefore zero reported DRC means zero violations of the checks this installed flow performs, not comprehensive foundry signoff.

The first SEC driver stopped before any prover because the old used-cell regex excludes escaped instance names, including all 21 `DFF_N/_0_` instances. `run_pilot_sec_v1.py` and the empty failed output directory are retained. The pre-run `SEC_ADAPTER_PREREG.md` authorizes the evidence-local model-generator adapter. It uses the complete Reader cell set while keeping the production `final_sec` source and all instance names unchanged. The omitted legacy types were exactly `dfxtp_1`, `dfxtp_2`, `dfxtp_4` (with the full Sky130 prefix).

Both sides of both proofs contain 102 functional cells including 21 sequential cells after removal of the identical 3026 empty-pin tap instances. The proof receipts contain all removed IDs, original and normalized hashes, exact model types, Liberty hash, generated model hash and all proof artifact hashes.

| Pair | Receipt | Result | Prover runtime | Proof cells |
|---|---|---|---|---|
| CONTROL vs RECOVERY_V2 | `sec/CONTROL_vs_RECOVERY_V2_models_v2/receipt.json` | PASS; original inputs unchanged | 0.313 s | 101 proven, 0 unproven |
| CONTROL vs NATIVE | `sec/CONTROL_vs_NATIVE_models_v2/receipt.json` | PASS; original inputs unchanged | 0.281 s | 101 proven, 0 unproven |

Each prover used `/usr/bin/yosys`, 180-second timeout; each driver ran under `run_with_timeout.sh 450`, sequentially, wrapper return codes zero (11 s / 10 s). Both raw logs contain `Equivalence successfully proven!`. This accepts two-state logical equivalence of the explicitly documented projection of the actual physical endpoints. It does not turn RECOVERY_V2's measured timing degradation into a safety pass. Preregistered strict timing non-worsening still fails.

## Endpoint identities inspected

| Arm | Artifact | SHA256 |
|---|---|---|
| CONTROL | routed.v | 3a2666be3cc4cf11c041c8be8793c16e30e617bb2e846468e2454ed5247aab8e |
| CONTROL | routed.spef | d56c2bc238d25e3659f4d6a65eeda7362acfeebd7c2159f24a18820adcd5afd8 |
| CONTROL | flow.tcl | 52499f3eb32c1006372c7652b1793826f64c969db93cf62b2d6bad3adcbbfe60 |
| CONTROL | ideal.tcl | d071ba0665d5303be5f725281119420632b86affa8142cf1d2e4a4a5c0a25782 |
| CONTROL | propagated.tcl | 8bb9b56fb51eb86de1d40dda20f3bd1157f20fb08bd97f998fcae8e272aead4a |
| RECOVERY_V2 | routed.v | a203adbd62283eaa7293940964f997f995c74055257d18619f56c2054ee91ab4 |
| RECOVERY_V2 | routed.spef | 1bb1988953e705afa710ce28e9e3b207c7e1bea45a5ee7bcd08a59151ea7ef22 |
| RECOVERY_V2 | flow.tcl | 4ae16caf0ec9794adcd30a00956191b9c36d487404bd9c17f50d909c5904a168 |
| RECOVERY_V2 | ideal.tcl | 02056b69b15ed24f4072141354285246bc7083fa5d46ab071b6e0068f28a0fde |
| RECOVERY_V2 | propagated.tcl | f7022f889dbeb54c16337a253770f81f037970688a1fdd8ad34d26dd0d10cc7d |

Physical-only tap blackbox warnings remain in independent STA logs; they are not silently converted into a general signoff guarantee. Constrained-path coverage and complete artifact sealing remain open; root will freeze endpoint output hashes. The completed formal and raw-report checks above supersede their initially pending status.
