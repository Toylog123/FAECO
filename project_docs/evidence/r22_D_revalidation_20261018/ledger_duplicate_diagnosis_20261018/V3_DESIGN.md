# Bounded v2 → v3 checker adaptation

The original v2 checker SHA is `59e51ed56d72fafc3b2dd611bf62028e4491991d6d07ca8bebc4b31ddd9e4250`. The new self-contained `checker_v3.py` SHA is `f6b053dfa6552aca43817f0dc1c1bdefca295c32bdf7ddc4b01cf1b12ab71daf`. `checker_v2_to_v3.diff` shows the exact adaptation; `V3_PREPARATION_RECEIPT.json` binds all preparation files. Only AST syntax parsing has run. The actual checker audit has not run.

The original raw baseline/candidate Tcl, mapped netlist, STA log, launch sequence, measured/accepted gain curves, final state, actual SEC scripts/logs/models/inputs, 45 source files, HEAD, Liberty, registration, completion and before/after read-identity checks remain in place. No production import supplies the new classification totals; they are independently reconstructed inside the checker from each selected raw ledger.

The trial branch becomes a strict four-way split of nonlaunch records:

1. Positive `cached_from_seq`: require an earlier measured trial and actual event with identical candidate/base/config/cache identity, same reported WNS/TNS and provenance. This counts as actual STA-result reuse.
2. `skipped_duplicate` with a present null `cached_from_seq`: require a prior same-key original pre-STA rejection, identical failure evidence and identities, and no STA launch/provenance. This counts as cached rejection, not STA reuse.
3. `skipped_duplicate` with no cached-from key: require the exact tested-hash signature, prior measured identical candidate/config under a different base, no reported launch/provenance/failure evidence, rejection placeholder equal to that call's baseline, and unaccepted/uncommitted state. Infer the missing base only through the explicit commit chain and exact cache-key digest. Record the inference separately; never mutate raw data.
4. Other nonlaunch records: require explicit hard pre-STA rejection evidence, false launch/accept/commit flags and no STA provenance. The observed 76 budget rejects must identify reservation before the tool.

The legacy `n_cache_replays` value is retained as the compatibility sum of classes 1–3 and still compared to the existing completion/result/ROOT28 fields. New explicit counters distinguish them. Missing or conflicting evidence raises an assertion; no default zero or guessed origin is used. All 5,243 measured launches still pass through the unchanged actual artifact checker, which also binds the earlier launch objects referenced by the 29 dedup records.

The selection contract changes explicitly from v2's “root set must equal every completed directory at start” to an immutable registered subset. The supplied root audit must have unique keys matching its own row set, be a nonempty subset of the 56 unique registered manifest keys, and all selected completion hashes must still equal that frozen receipt. Extra completions at start and end are separately listed as unreviewed. `full_56_registered_keys_reviewed` is true only when the selected key set equals the manifest's full 56-key set. ROOT28 is never edited, and new producer completions do not enter the review implicitly.

Expected execution after root source review:

```text
checker_v3.py --audit project_docs/evidence/r22_D_revalidation_20261018/ROOT_COMPLETION_AUDIT_28.json --output <new exclusive output directory>
```

Use the established bounded wrapper and monitor progress. This is a read-only artifact audit, not a new scientific EDA run. The preparation is not a claim that all 28 raw proofs/STA artifacts have independently passed v3; that claim requires the actual run and its source-stability receipt. Later jobs can wait for the full 56-key review rather than repeating review on every producer increment.
