# Sentinel b17 (P2.5)

**Status:** failed (diagnosed; not a current-HEAD validation).

## Run record

| Field | Value |
|---|---|
| run_id | `b17-balanced-20260828T052410861999Z-c7e4b55f` |
| input_hash | `81ae846589e70848f119d5e9b77d8b1d76a9182033047a1db21549e3abec348b` |
| run_spec_hash | `814b29de076a51e40045d0157165fe16d28b306ca5618d2e236f8d3345890f6e` |
| policy / configuration | `balanced`, period `0.5 ns`, 4 iterations, 1 candidate per iteration, joint depth 3, strategies `R,G,B`, 1 worker |
| success / final patch | `false` / `null` |
| WNS history | `[-16.53, -16.53, -16.53, -16.53]` |
| candidate STA runs / stop | `160` / `round_complete ×4` |
| soft-cost events / hard timeouts | `111` / `0` |
| SEC | not run for an accepted final patch (no final patch exists) |

Manifest: [sentinel_manifest.json](../../experiments/20260828_phase2_sentinel/b17/sentinel_manifest.json). Raw trials: [eval_trials.json](../../experiments/20260828_phase2_sentinel/b17/eval_trials.json). Outer-loop result: [outerloop_result.json](../../experiments/20260828_phase2_sentinel/b17/outerloop_result.json).

## Rejection distribution

The 160 trial records all have `accepted=false`. Failure-event counts are event counts; categories overlap when one trial records more than one gate:

| Evidence | Count | Interpretation |
|---|---:|---|
| `F5_verification_too_expensive` unique trials | 111 | Every trial with runtime above the 60 s soft cap was treated as a hard rejection by the pre-fix run. |
| `acceptance_budget_unavailable` unique trials | 75 | Setup WNS/TNS were unavailable; 49 of these were at runtime ≤60 s and 26 at runtime >60 s. |
| `acceptance_budget_violation` unique trials | 27 | `setup_tns` regressed versus the baseline. |
| WNS strictly better than baseline | 56 | All 56 were also in the F5 set; none was accepted. |
| runtime >60 s / ≤60 s | 111 / 49 | Median runtime was 89.48 s; max 133.94 s. |

Round summaries: iteration 1 had 42 trials, iteration 2 had 34, iteration 3 had 41, and iteration 4 had 43; every round stopped as `round_complete`, with best WNS unchanged at `-16.53`.

## Root-cause conclusion

This artifact does **not** establish a defect in `27e6020`. The run id is dated 2026-08-28, while `27e6020` was committed on 2026-08-29 16:35 (+08:00); the manifest also records `git_head_sha=null`. Therefore b17 ran before the slow-but-complete acceptance fix and cannot validate it. The observed all-rejected outcome is explained by the old F5 hard-rejection behavior plus unavailable setup metrics, not by a reproducible current-HEAD failure.

The required follow-up is a fresh b17 run in a new output directory using the current HEAD, with manifest fields for implementation SHA and tool versions populated. Preserve this directory as historical failure evidence; do not overwrite it.

## Current-head rerun (T03) — incomplete

The current-HEAD rerun has **not completed** and has no acceptance evidence. Attempts so far:

| Output directory (drive) | State | Evidence |
|---|---|---|
| `experiments/20260831_phase2_sentinel/b17/` (C) | preflight only | mapping + baseline STA only; no eval, no manifest |
| `experiments/20260831_phase2_sentinel_clean/b17/` (C) | crashed, incomplete | `OSError: [Errno 28] No space left on device` at iteration 1; no manifest |
| `experiments/20260901_phase2_sentinel/b17/` (D) | interrupted, incomplete | baseline done; eval rounds `iter001` 37/42, `iter002` 37/42, `iter003` 12/12; **no `sentinel_manifest.json`**, no SEC |
| `experiments/20260902_phase2_sentinel/b17/` (D) | running, partial | python3.11 PID 46452 restarted 2026-09-02 11:35:45; output to `D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17` (D drive); eval `iter001_cand001/000__184320__G`–`004__184362__G` already written; **no `sentinel_manifest.json` yet** |

The two D-drive attempts (`20260901` interrupted, `20260902` running) are the most complete runs but neither has produced a `sentinel_manifest.json`; the running `20260902` attempt is expected to finish within ~1–2 hours of 2026-09-02 11:35, otherwise fall back to `experiments/20260903_phase2_sentinel/b17/` (D) per the original handoff plan. The required action remains a fresh, uninterrupted rerun on D (do not run on C; it fills the system drive), with `git_head_sha`, tool versions, WNS history, and SEC populated in the manifest.
