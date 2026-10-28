# D28 duplicate-ledger diagnosis

The failure is in the independent v2 checker, not an EDA run. Its line 159 assumes every `skipped_duplicate` record has `cached_from_seq` pointing to a STA launch. The frozen implementation has a second, different branch at `real_wns.py:1693–1702`: an already tested absolute candidate identity is skipped under the current base, with no replayed STA result, no launch sequence, and no `base_netlist_hash` field. The legacy `sta_ledger.py:18–20` counts both forms in `n_cache_replays`.

`DIAGNOSIS.json` independently reads the 28 immutable objects named by ROOT_COMPLETION_AUDIT_28. It binds 581 original files and rechecks their exact bytes. It neither imports the production ledger summarizer nor changes the original ledgers. It does not review the extra three completions existing at the diagnosis finish.

| Class | Frozen ROOT28 records | Meaning |
|---|---:|---|
| New candidate STA launch | 5,243 | Explicit unique launch event, linked measured trial |
| STA result reuse from a launch | 5,821 | Explicit positive cached-from sequence with identical base, candidate, config and cache identity |
| Tested-hash dedup without replay | 29 | No new launch or result replay; previously measured identical candidate under an earlier base |
| Cached pre-STA rejection | 0 | Supported implementation path, not observed in ROOT28 |
| Uncached pre-STA rejection | 76 | `sta_budget_exhausted`, hard rejection reserved before the tool; 73 in random_s1/s641 and 3 in random_s3/s641 |

The old reported count is 5,850 = 5,821 + 29. This equality holds per job against completion accounting, outer-loop result and ROOT28. It must not be described as 5,850 actual STA-result reuses. The new measured-launch count remains 5,243. These are accounting distinctions, not evidence of a general feedback efficacy result.

`DUPLICATE_DETAILS.json` lists all 29 exact zero-based trial locations. `FIRST_FAILURE_s641_FOUR.json` isolates the first failed job's four records. Every identity-dedup record is unaccepted, uncommitted, `sta_executed=false`, `sta_launch_seq=null`, runtime zero, and has no `cached_from_seq` or base field. Its candidate-text hash matches the original candidate hash. The base is explicitly labelled inferred: initial mapped text plus the ordered explicitly committed trial chain, independently constrained by `cache_key = SHA256(base + candidate + config)`. All 29 have prior same-candidate/same-config measured trials under a different base; their retained mapped file and actual STA log were opened and matched to the launch event. The missing raw fields are never filled or rewritten.

The first s641 example is trial index 8, iteration 4, candidate `8d97180cf45ee7dffd575e0b103c5bdec369f982d53744a5f7579c8401e9fc72`. Its earlier actual source is trial index 3 / launch 4 with WNS −1.34. The current duplicate record carries −1.22, the then-current baseline placeholder, so treating it as an actual reused STA measurement would also assign the wrong value. Full hashes and locations are in the JSON details rather than reconstructed prose.

`DIAGNOSIS_RUN.log`, the exact executed script, invocation, source snapshots, original failed v2 log and the original v2 checker are retained. The old failed run, original result files and production source remain unchanged. The diagnosis itself does not complete the full raw-STA/SEC independent review; that remains the prepared v3 checker's task after root reads its source.
