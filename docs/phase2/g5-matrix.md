# G5 Gate Matrix — Phase 2 Sentinel

Status legend: ✅ pass · 🔄 in progress · ⏳ pending · ❌ failed · ⛔ blocked (with diagnosis).

| Case | run_id (policy) | input_hash | run_spec_hash | WNS baseline → final | n STA / stop | SEC | evidence | status |
|---|---|---|---|---|---|---|---|---|
| s27 | `s27-balanced-20260828T032210532289Z-38f4c3da` | `05d18654…` | `0878d54f…` | -0.27 → -0.18 | 99 / round_complete ×3 | pass | [sentinel-s27.md](sentinel-s27.md), [manifest](manifests/s27-balanced.json) | ✅ |
| s382 | `s382-balanced-20260828T032626728345Z-31d429be` (replay `…-5a64f9cb`) | `2503d4cb…` | `bb462ab7…` | -0.98 → -0.83 | 47 / round_complete | pass | [sentinel-s382.md](sentinel-s382.md), [manifest](manifests/s382-balanced.json), [replay](manifests/s382-balanced-replay-run1.json) | ✅ |
| b15 | fast `b15-fast-20260828T032815969207Z-7a9e4e3c`; balanced `b15-balanced-20260828T034330466096Z-a4a8e7fe` | `6f9c403d…` (identical) | `5facc5e7…` / `ca98ea24…` | -12.55 → -11.68 (fast) / -11.48 (balanced) | 20 / first_acceptable ×4; 159 / round_complete ×4 | pass (15.2 s) | [sentinel-b15.md](sentinel-b15.md), [fast](manifests/b15-fast.json), [balanced](manifests/b15-balanced.json) | ✅ |
| b17 | `b17-balanced-20260828T052410861999Z-c7e4b55f` | `81ae8465…` | `814b29de…` | -16.53 → -16.53 | 160 / round_complete ×4 | not run | [sentinel-b17.md](sentinel-b17.md), [manifest](../../experiments/20260828_phase2_sentinel/b17/sentinel_manifest.json) | ❌ |
| b18 | ⏳ pending | — | — | — | — | pending | pending | ⏳ |
| picorv32 | ⏳ pending | — | — | — | — | pending | pending | ⏳ |

## Phase 2 exit record

- All G5 rows: 3/6 ✅, 1/6 ❌, 2/6 ⏳ (b17 completed without an accepted patch; see diagnosis).
- Full verification gates + smoke re-run: pending (P2.9).
- Rollback audit: no policy degradation observed on completed cases (s27, s382, b15 both policies improve WNS, SEC intact).

The historical b17 row above is fixed as **failed**. A separate current-HEAD rerun is in progress under `experiments/20260831_phase2_sentinel_clean/b17/`; it must not overwrite or replace the historical failure row until its manifest, SEC, and WNS evidence are complete.
