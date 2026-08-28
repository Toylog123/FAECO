# Sentinel s382 (P2.4)

**Goal:** regular sequential case with accept/reject evidence complete, and balanced-mode replayability proven by two identical fresh runs.

## Run records (replay pair)

| Field | Run 1 | Run 2 |
|---|---|---|
| run_id | `s382-balanced-20260828T032529851154Z-5a64f9cb` | `s382-balanced-20260828T032626728345Z-31d429be` |
| input_hash | `2503d4cbc4a70850…` | `2503d4cbc4a70850…` |
| run_spec_hash | `bb462ab7a0a6da23…` | `bb462ab7a0a6da23…` |
| success / iterations | true / 4 | true / 4 |
| wns_history | `[-0.85, -0.83, -0.83]` | `[-0.85, -0.83, -0.83]` |
| accepted patch | `patch_C3_Q3VD_critical_path_cover` | `patch_C3_Q3VD_critical_path_cover` |

Manifests: [s382-balanced.json](manifests/s382-balanced.json) (run 2), [s382-balanced-replay-run1.json](manifests/s382-balanced-replay-run1.json) (run 1).

Configuration: period 0.5 ns, balanced, 4 iterations, beam 1, joint depth 0, strategies R/G/B, priority table, 1 worker, OSS-CAD Yosys 0.67+146 + WSL OpenSTA 3.1.0, implementation head `2aaa7db`.

## Replayability (G5 s382)

- `input_hash` equal across runs: **true**
- `run_spec_hash` equal across runs: **true** (config hash excludes run-id identity; see `tests/test_runspec.py::test_config_hash_is_stable_across_run_ids`)
- outcome equal across runs: **true**
- baseline: `wns=-0.98 min_slack=0.42 endpoint=DFF_9`; critical path identical (66 instances)

## Accept/reject evidence

- 47 candidate STA trials across 3 evaluated rounds (`round_stop_reason=round_complete` each; coverage `17/17`, `16/16`, `14/14` in call_log)
- every trial carries `acceptance_evidence` with OpenSTA provenance and structured `failure_events` on rejection
- accepted kinds: `G` ×2; zero `F1_equivalence_failure` / `F2_boundary_invalid` across trials
- soft-cost events: none; hard timeout events: none

## SEC evidence

Full-netlist SEC of the accepted final netlist vs baseline: **pass** (`yosys_blif_abc_cec`, 2.7 s), evidence at `experiments/20260828_phase2_sentinel/s382/sec_verification.json`.

## Gate

G5 s382 row: **pass** (balanced replayable; accept/reject evidence complete).
