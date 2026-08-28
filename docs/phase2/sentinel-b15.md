# Sentinel b15 (P2.5)

**Goal:** on a large ITC'99 netlist, prove the two search-policy semantics are distinct and correct: `fast` stops each round at the first acceptable candidate, while `balanced` evaluates the full round (`round_complete`) and therefore lands on a better final result — with SEC intact.

## Run records (fast vs balanced)

| Field | fast | balanced |
|---|---|---|
| run_id | `b15-fast-20260828T032815969207Z-7a9e4e3c` | `b15-balanced-20260828T034330466096Z-a4a8e7fe` |
| input_hash | `6f9c403d…` | `6f9c403d…` (identical) |
| run_spec_hash | `5facc5e7…` | `ca98ea24…` |
| success / iterations | true / 4 | true / 4 |
| n_candidate_sta_runs | 20 | 159 |
| round_stop_reasons | `first_acceptable` ×4 | `round_complete` ×4 |
| wns_history | `[-12.53, -11.85, -11.73, -11.68]` | `[-11.7, -11.57, -11.49, -11.48]` |
| accepted patch | `patch_U2956_critical_path_cover` | `patch_U2956_critical_path_cover` |

Manifests: [b15-fast.json](manifests/b15-fast.json), [b15-balanced.json](manifests/b15-balanced.json).

Configuration (both): period 0.5 ns, 4 iterations, beam 1, candidates-per-iteration 1, joint-enumerate-depth 3, strategies R/G/B, priority table `src/rseco/strategy_priority_table.json`, 1 worker, OSS-CAD Yosys 0.67+146 + WSL OpenSTA 3.1.0, implementation head `c860b6a`.

## Policy semantic evidence (G5 b15)

Baseline: `wns=-12.55 min_slack=0.39 endpoint=_49360_ D=U2956`.

- `fast` covered 43/43/29/7 candidates per round but **partially validated** (`coverage.partial=true`), stopping each round at the first acceptable candidate; 20 STA total.
- `balanced` **fully validated every round**: coverage `43/43`, `44/44`, `41/41`, `31/31` (`partial=false`), 159 STA total, all `round_stop_reason=round_complete`.
- Because balanced does not stop early, it accepts a better patch than fast on the same input: final WNS **-11.48** (balanced) vs **-11.68** (fast), an extra 0.2 ns improvement from full-round evaluation of JOINT-depth-3 candidates.
- Round-by-round best: balanced `[-11.7, -11.57, -11.49, -11.48]` vs fast `[-12.53, -11.85, -11.73, -11.68]`.

## Accept/reject evidence

- 159 balanced candidate STA trials, every trial carries `acceptance_evidence` with OpenSTA provenance and structured `failure_events` on rejection.
- accepted kinds include `G` and joint `JOINT` candidates (joint-enumerate-depth 3); no `F1_equivalence_failure` / `F2_boundary_invalid`.
- soft-cost events: none; hard timeout events: none.

## SEC evidence

Full-netlist SEC of the accepted final netlist vs baseline: **pass** (`yosys_blif_abc_cec`, 15.2 s), evidence at `experiments/20260828_phase2_sentinel/b15/sec_verification.json` (baseline sha256 `3c567390…`, final sha256 `40ad64bf…`).

## Gate

G5 b15 row: **pass** (policy semantics distinct and verified; full-round balanced evaluation; SEC intact).
