# Sentinel s27 (P2.3)

**Goal:** minimal end-to-end smoke: mapping, STA, candidates, equivalence/SEC, and manifest all present and passing on the smallest sequential case.

## Run record

| Field | Value |
|---|---|
| run_id | `s27-balanced-20260828T031515235079Z-0236dfc3` |
| circuit / policy | `s27` / `balanced` |
| period | 0.5 ns |
| input_hash | `05d18654d9cbb7e4…` |
| run_spec_hash | `e25717c91c9ef200…` |
| implementation head | `836c6f6` |
| Yosys | 0.67+146 (OSS-CAD native) |
| OpenSTA | 3.1.0 (WSL Ubuntu) |
| manifest | [docs/phase2/manifests/s27-balanced.json](manifests/s27-balanced.json) |
| experiment dir | `experiments/20260828_phase2_sentinel/s27/` (gitignored) |

## Outcome

- success: **true**, 3 iterations, wns history `[-0.19, -0.18, -0.18]` from baseline `-0.27`
- accepted patch: `patch_G10_critical_path_cover`
- candidate STA runs: 99; every round `round_stop_reason=round_complete` (balanced full round, coverage `34/34`, `1/1`, `1/1` in call_log)
- soft-cost events: none (all STA runs under 60 s cap); hard timeout events: none

## G5 chain evidence (s27 row)

| Stage | Evidence | Status |
|---|---|---|
| mapping | `mapped.v`, `map.ys`, `map.log` | pass |
| STA | `sta.log`, `sta.tcl`; baseline `wns=-0.27` | pass |
| candidates | `eval_trials.json` (99 trials), `eval/iter*_cand*` dirs | pass |
| equivalence/SEC | all 99 trials have `acceptance_evidence` (OpenSTA provenance); zero `F1_equivalence_failure` / `F2_boundary_invalid` events across trials | pass |
| manifest | `sentinel_manifest.json` with input_hash, run_spec_hash, resolved snapshot, argv, toolchain, outcome | pass |

**SEC note (honest boundary):** the full-netlist Yosys-ABC SEC stage (`topology-sec`) is invoked only for TOPOLOGY candidates. The s27 cut region has no supported multi-gate topology pattern, so no TOPOLOGY candidate was generated and that stage produced no artifacts; it is recorded here as *no TOPOLOGY candidate available*, not as a silent pass. Per-candidate Liberty-function equivalence (R/G/B) and boundary-closure checks ran for every trial. The full-netlist SEC stage is exercised on the s382 sentinel (P2.4), whose logic cones are expected to contain topology patterns.

## Gate

G5 s27 row: **pass** (full chain present; full-netlist SEC stage explicitly recorded as no-candidate on this tiny case and deferred to s382).
